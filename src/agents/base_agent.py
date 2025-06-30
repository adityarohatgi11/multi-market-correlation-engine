"""
Base Agent Framework for Multi-Market Correlation Engine

This module provides the foundation for all specialized agents in the system.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json
import threading
from queue import Queue
import uuid


class AgentStatus(Enum):
    """Agent status enumeration"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    STOPPED = "stopped"


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    """Task data structure"""
    id: str
    name: str
    priority: TaskPriority
    created_at: datetime
    scheduled_at: Optional[datetime]
    data: Dict[str, Any]
    callback: Optional[Callable] = None
    
    def __post_init__(self):
        if self.scheduled_at is None:
            self.scheduled_at = self.created_at


@dataclass
class AgentMetrics:
    """Agent performance metrics"""
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_runtime: float = 0.0
    average_task_time: float = 0.0
    last_activity: Optional[datetime] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class BaseAgent(ABC):
    """
    Base class for all agents in the multi-market correlation engine.
    
    Provides common functionality for task management, logging, error handling,
    and communication between agents.
    """
    
    def __init__(self, agent_id: str, name: str, config: Optional[Dict] = None):
        """
        Initialize the base agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name for the agent
            config: Configuration dictionary
        """
        self.agent_id = agent_id
        self.name = name
        self.config = config or {}
        self.status = AgentStatus.IDLE
        self.metrics = AgentMetrics()
        
        # Task management
        self.task_queue = Queue()
        self.running_tasks = {}
        self.completed_tasks = []
        
        # Communication
        self.message_queue = Queue()
        self.subscribers = []
        
        # Control
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._worker_thread = None
        
        # Logging
        self.logger = self._setup_logger()
        
        self.logger.info(f"Agent {self.name} ({self.agent_id}) initialized")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup agent-specific logger"""
        logger = logging.getLogger(f"agent.{self.agent_id}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'%(asctime)s - {self.name} - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def start(self):
        """Start the agent"""
        if self.status != AgentStatus.IDLE:
            self.logger.warning(f"Agent already running with status: {self.status}")
            return
        
        self.status = AgentStatus.RUNNING
        self._stop_event.clear()
        self._pause_event.clear()
        
        self._worker_thread = threading.Thread(target=self._run_worker, daemon=True)
        self._worker_thread.start()
        
        self.logger.info("Agent started")
    
    def stop(self):
        """Stop the agent"""
        self.status = AgentStatus.STOPPED
        self._stop_event.set()
        
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=5.0)
        
        self.logger.info("Agent stopped")
    
    def pause(self):
        """Pause the agent"""
        self.status = AgentStatus.PAUSED
        self._pause_event.set()
        self.logger.info("Agent paused")
    
    def resume(self):
        """Resume the agent"""
        if self.status == AgentStatus.PAUSED:
            self.status = AgentStatus.RUNNING
            self._pause_event.clear()
            self.logger.info("Agent resumed")
    
    def add_task(self, task: Task):
        """Add a task to the agent's queue"""
        self.task_queue.put(task)
        self.logger.debug(f"Task added: {task.name} (Priority: {task.priority.name})")
    
    def create_task(self, name: str, data: Dict[str, Any], 
                   priority: TaskPriority = TaskPriority.MEDIUM,
                   scheduled_at: Optional[datetime] = None) -> Task:
        """Create and add a new task"""
        task = Task(
            id=str(uuid.uuid4()),
            name=name,
            priority=priority,
            created_at=datetime.now(),
            scheduled_at=scheduled_at,
            data=data
        )
        self.add_task(task)
        return task
    
    def send_message(self, recipient_id: str, message_type: str, data: Dict[str, Any]):
        """Send a message to another agent"""
        message = {
            'id': str(uuid.uuid4()),
            'sender_id': self.agent_id,
            'recipient_id': recipient_id,
            'message_type': message_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        # Notify subscribers
        for subscriber in self.subscribers:
            try:
                subscriber(message)
            except Exception as e:
                self.logger.error(f"Error notifying subscriber: {e}")
    
    def subscribe_to_messages(self, callback: Callable):
        """Subscribe to messages from this agent"""
        self.subscribers.append(callback)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics"""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'status': self.status.value,
            'metrics': {
                'tasks_completed': self.metrics.tasks_completed,
                'tasks_failed': self.metrics.tasks_failed,
                'total_runtime': self.metrics.total_runtime,
                'average_task_time': self.metrics.average_task_time,
                'last_activity': self.metrics.last_activity.isoformat() if self.metrics.last_activity else None,
                'error_count': len(self.metrics.errors)
            },
            'queue_size': self.task_queue.qsize(),
            'running_tasks': len(self.running_tasks)
        }
    
    def _run_worker(self):
        """Main worker loop"""
        self.logger.info("Worker thread started")
        
        while not self._stop_event.is_set():
            try:
                # Handle pause
                if self._pause_event.is_set():
                    time.sleep(0.1)
                    continue
                
                # Get next task
                if not self.task_queue.empty():
                    task = self.task_queue.get_nowait()
                    
                    # Check if task is scheduled for future
                    if task.scheduled_at > datetime.now():
                        # Put back in queue and wait
                        self.task_queue.put(task)
                        time.sleep(1)
                        continue
                    
                    # Execute task
                    self._execute_task(task)
                else:
                    # No tasks, perform idle work
                    self._idle_work()
                    time.sleep(0.1)
                    
            except Exception as e:
                self.logger.error(f"Error in worker loop: {e}")
                self.status = AgentStatus.ERROR
                self.metrics.errors.append(str(e))
                time.sleep(1)
        
        self.logger.info("Worker thread stopped")
    
    def _execute_task(self, task: Task):
        """Execute a single task"""
        start_time = time.time()
        self.running_tasks[task.id] = task
        
        try:
            self.logger.info(f"Executing task: {task.name}")
            
            # Execute the task-specific logic
            result = self.execute_task(task)
            
            # Update metrics
            execution_time = time.time() - start_time
            self.metrics.tasks_completed += 1
            self.metrics.total_runtime += execution_time
            self.metrics.average_task_time = self.metrics.total_runtime / self.metrics.tasks_completed
            self.metrics.last_activity = datetime.now()
            
            # Move to completed tasks
            self.completed_tasks.append({
                'task': task,
                'result': result,
                'execution_time': execution_time,
                'completed_at': datetime.now()
            })
            
            # Call callback if provided
            if task.callback:
                try:
                    task.callback(task, result)
                except Exception as e:
                    self.logger.error(f"Error in task callback: {e}")
            
            self.logger.info(f"Task completed: {task.name} ({execution_time:.2f}s)")
            
        except Exception as e:
            self.logger.error(f"Task failed: {task.name} - {e}")
            self.metrics.tasks_failed += 1
            self.metrics.errors.append(f"Task {task.name}: {str(e)}")
            
        finally:
            # Remove from running tasks
            self.running_tasks.pop(task.id, None)
    
    @abstractmethod
    def execute_task(self, task: Task) -> Any:
        """
        Execute a specific task. Must be implemented by subclasses.
        
        Args:
            task: The task to execute
            
        Returns:
            Task execution result
        """
        pass
    
    def _idle_work(self):
        """
        Perform work when no tasks are queued.
        Can be overridden by subclasses for background activities.
        """
        pass
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check and return status"""
        return {
            'healthy': self.status in [AgentStatus.IDLE, AgentStatus.RUNNING],
            'status': self.status.value,
            'last_activity': self.metrics.last_activity.isoformat() if self.metrics.last_activity else None,
            'error_count': len(self.metrics.errors),
            'recent_errors': self.metrics.errors[-5:] if self.metrics.errors else []
        }


class AgentRegistry:
    """Registry for managing multiple agents"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger("agent_registry")
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent"""
        self.agents[agent.agent_id] = agent
        self.logger.info(f"Agent registered: {agent.name} ({agent.agent_id})")
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        if agent_id in self.agents:
            agent = self.agents.pop(agent_id)
            agent.stop()
            self.logger.info(f"Agent unregistered: {agent.name} ({agent_id})")
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by ID"""
        return self.agents.get(agent_id)
    
    def start_all(self):
        """Start all registered agents"""
        for agent in self.agents.values():
            agent.start()
        self.logger.info(f"Started {len(self.agents)} agents")
    
    def stop_all(self):
        """Stop all registered agents"""
        for agent in self.agents.values():
            agent.stop()
        self.logger.info("All agents stopped")
    
    def get_status_all(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            agent_id: agent.get_status()
            for agent_id, agent in self.agents.items()
        }
    
    def health_check_all(self) -> Dict[str, Any]:
        """Perform health check on all agents"""
        return {
            agent_id: agent.health_check()
            for agent_id, agent in self.agents.items()
        }


# Global agent registry instance
agent_registry = AgentRegistry()


if __name__ == "__main__":
    # Example usage
    class TestAgent(BaseAgent):
        def execute_task(self, task: Task) -> Any:
            # Simulate work
            time.sleep(1)
            return f"Completed {task.name}"
    
    # Create and test agent
    agent = TestAgent("test-001", "Test Agent")
    agent.start()
    
    # Add some tasks
    agent.create_task("Test Task 1", {"data": "test1"})
    agent.create_task("Test Task 2", {"data": "test2"}, priority=TaskPriority.HIGH)
    
    # Let it run for a bit
    time.sleep(5)
    
    # Check status
    print(json.dumps(agent.get_status(), indent=2))
    
    # Stop agent
    agent.stop()
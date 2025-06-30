"""
Agent Coordinator for Multi-Market Correlation Engine

This module coordinates multiple agents and manages the overall system workflow.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import schedule
import logging

from .base_agent import BaseAgent, Task, TaskPriority, AgentStatus, agent_registry
from .data_collection_agent import DataCollectionAgent
from .analysis_agent import AnalysisAgent


class AgentCoordinator:
    """
    Coordinates multiple agents and manages system-wide workflows.
    
    Features:
    - Agent lifecycle management
    - Inter-agent communication
    - Workflow orchestration
    - System monitoring and health checks
    - Automated scheduling
    - Error handling and recovery
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the agent coordinator.
        
        Args:
            config: Configuration dictionary
        """
        default_config = {
            'enable_data_collection': True,
            'enable_analysis': True,
            'enable_reporting': True,
            'enable_alerts': True,
            'collection_interval': 300,  # 5 minutes
            'analysis_interval': 3600,  # 1 hour
            'health_check_interval': 600,  # 10 minutes
            'symbols': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
            'auto_start_agents': True,
            'enable_scheduling': True
        }
        
        if config:
            default_config.update(config)
        
        self.config = default_config
        self.agents = {}
        self.workflows = {}
        self.system_status = 'stopped'
        self.message_queue = []
        
        # Scheduling
        self.scheduler_active = False
        self.scheduler_thread = None
        
        # Logging
        self.logger = self._setup_logger()
        
        # Initialize agents
        self._initialize_agents()
        
        self.logger.info("Agent Coordinator initialized")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup coordinator logger"""
        logger = logging.getLogger("agent_coordinator")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - AgentCoordinator - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _initialize_agents(self):
        """Initialize all agents"""
        try:
            # Initialize data collection agent
            if self.config['enable_data_collection']:
                data_agent_config = {
                    'collection_interval': self.config['collection_interval'],
                    'symbols': self.config['symbols'],
                    'enable_scheduling': self.config['enable_scheduling']
                }
                self.agents['data_collector'] = DataCollectionAgent(config=data_agent_config)
                agent_registry.register_agent(self.agents['data_collector'])
                self.logger.info("Data collection agent initialized")
            
            # Initialize analysis agent
            if self.config['enable_analysis']:
                analysis_agent_config = {
                    'analysis_interval': self.config['analysis_interval'],
                    'symbols': self.config['symbols']
                }
                self.agents['analyzer'] = AnalysisAgent(config=analysis_agent_config)
                agent_registry.register_agent(self.agents['analyzer'])
                self.logger.info("Analysis agent initialized")
            
            # Setup inter-agent communication
            self._setup_agent_communication()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {e}")
            raise
    
    def _setup_agent_communication(self):
        """Setup communication between agents"""
        # Data collector sends messages to analyzer when data is available
        if 'data_collector' in self.agents:
            self.agents['data_collector'].subscribe_to_messages(self._handle_agent_message)
        
        if 'analyzer' in self.agents:
            self.agents['analyzer'].subscribe_to_messages(self._handle_agent_message)
    
    def _handle_agent_message(self, message: Dict[str, Any]):
        """Handle messages between agents"""
        try:
            sender_id = message.get('sender_id')
            recipient_id = message.get('recipient_id')
            message_type = message.get('message_type')
            data = message.get('data', {})
            
            self.logger.debug(f"Message from {sender_id} to {recipient_id}: {message_type}")
            
            # Store message for monitoring
            self.message_queue.append(message)
            
            # Handle specific message types
            if message_type == 'data_available' and recipient_id == 'analysis-agent-001':
                # Trigger analysis when new data is available
                if 'analyzer' in self.agents:
                    symbols = data.get('symbols', self.config['symbols'])
                    self.agents['analyzer'].create_task(
                        "Data-Triggered Analysis",
                        {
                            'type': 'correlation_analysis',
                            'symbols': symbols
                        },
                        priority=TaskPriority.MEDIUM
                    )
            
            elif message_type == 'analysis_complete':
                # Handle analysis completion
                self.logger.info("Analysis completed, results available")
                # Could trigger reporting here
            
            # Clean old messages
            self._cleanup_old_messages()
            
        except Exception as e:
            self.logger.error(f"Error handling agent message: {e}")
    
    def _cleanup_old_messages(self):
        """Clean up old messages from the queue"""
        cutoff_time = datetime.now() - timedelta(hours=1)
        self.message_queue = [
            msg for msg in self.message_queue
            if datetime.fromisoformat(msg['timestamp']) > cutoff_time
        ]
    
    def start_system(self):
        """Start the entire multi-agent system"""
        try:
            self.logger.info("Starting multi-agent system...")
            
            # Start all agents
            if self.config['auto_start_agents']:
                for agent_name, agent in self.agents.items():
                    agent.start()
                    self.logger.info(f"Started {agent_name}")
            
            # Start scheduling if enabled
            if self.config['enable_scheduling']:
                self.start_scheduling()
            
            # Start data collection scheduling
            if 'data_collector' in self.agents:
                self.agents['data_collector'].start_scheduled_collection()
            
            self.system_status = 'running'
            self.logger.info("Multi-agent system started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start system: {e}")
            self.system_status = 'error'
            raise
    
    def stop_system(self):
        """Stop the entire multi-agent system"""
        try:
            self.logger.info("Stopping multi-agent system...")
            
            # Stop scheduling
            self.stop_scheduling()
            
            # Stop data collection scheduling
            if 'data_collector' in self.agents:
                self.agents['data_collector'].stop_scheduled_collection()
            
            # Stop all agents
            for agent_name, agent in self.agents.items():
                agent.stop()
                self.logger.info(f"Stopped {agent_name}")
            
            self.system_status = 'stopped'
            self.logger.info("Multi-agent system stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping system: {e}")
    
    def start_scheduling(self):
        """Start system-wide scheduling"""
        if self.scheduler_active:
            self.logger.warning("Scheduler already active")
            return
        
        # Schedule system health checks
        schedule.every(self.config['health_check_interval'] // 60).minutes.do(
            self._schedule_health_check
        )
        
        # Schedule comprehensive analysis
        schedule.every().day.at("08:00").do(self._schedule_comprehensive_analysis)
        
        # Schedule system cleanup
        schedule.every().day.at("02:00").do(self._schedule_system_cleanup)
        
        # Start scheduler thread
        self.scheduler_active = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("System scheduling started")
    
    def stop_scheduling(self):
        """Stop system-wide scheduling"""
        self.scheduler_active = False
        schedule.clear()
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5.0)
        
        self.logger.info("System scheduling stopped")
    
    def _run_scheduler(self):
        """Run the system scheduler"""
        while self.scheduler_active:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                time.sleep(60)
    
    def _schedule_health_check(self):
        """Schedule a system health check"""
        try:
            health_status = self.get_system_health()
            
            # Check for unhealthy agents
            unhealthy_agents = [
                agent_id for agent_id, health in health_status['agents'].items()
                if not health.get('healthy', False)
            ]
            
            if unhealthy_agents:
                self.logger.warning(f"Unhealthy agents detected: {unhealthy_agents}")
                # Could implement recovery logic here
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
    
    def _schedule_comprehensive_analysis(self):
        """Schedule a comprehensive analysis"""
        if 'analyzer' in self.agents:
            self.agents['analyzer'].create_task(
                "Scheduled Comprehensive Analysis",
                {
                    'type': 'comprehensive_analysis',
                    'symbols': self.config['symbols']
                },
                priority=TaskPriority.MEDIUM
            )
    
    def _schedule_system_cleanup(self):
        """Schedule system cleanup tasks"""
        # Clean up old messages
        self._cleanup_old_messages()
        
        # Trigger agent cleanup
        for agent in self.agents.values():
            agent.create_task(
                "System Cleanup",
                {'type': 'cleanup'},
                priority=TaskPriority.LOW
            )
    
    def execute_workflow(self, workflow_name: str, parameters: Dict[str, Any] = None) -> str:
        """Execute a predefined workflow"""
        parameters = parameters or {}
        
        if workflow_name == 'full_market_analysis':
            return self._execute_full_market_analysis(parameters)
        elif workflow_name == 'data_collection_and_analysis':
            return self._execute_data_collection_and_analysis(parameters)
        elif workflow_name == 'emergency_analysis':
            return self._execute_emergency_analysis(parameters)
        else:
            raise ValueError(f"Unknown workflow: {workflow_name}")
    
    def _execute_full_market_analysis(self, parameters: Dict[str, Any]) -> str:
        """Execute full market analysis workflow"""
        symbols = parameters.get('symbols', self.config['symbols'])
        workflow_id = f"full_analysis_{int(time.time())}"
        
        self.logger.info(f"Starting full market analysis workflow: {workflow_id}")
        
        workflow_tasks = []
        
        # Step 1: Collect fresh data
        if 'data_collector' in self.agents:
            task_id = self.agents['data_collector'].force_collection(symbols)
            workflow_tasks.append(('data_collection', task_id))
        
        # Step 2: Comprehensive analysis (will be triggered by data availability)
        if 'analyzer' in self.agents:
            task_id = self.agents['analyzer'].force_analysis('comprehensive_analysis', symbols)
            workflow_tasks.append(('analysis', task_id))
        
        # Store workflow
        self.workflows[workflow_id] = {
            'name': 'full_market_analysis',
            'parameters': parameters,
            'tasks': workflow_tasks,
            'status': 'running',
            'started_at': datetime.now().isoformat()
        }
        
        return workflow_id
    
    def _execute_data_collection_and_analysis(self, parameters: Dict[str, Any]) -> str:
        """Execute data collection and basic analysis workflow"""
        symbols = parameters.get('symbols', self.config['symbols'])
        workflow_id = f"collect_analyze_{int(time.time())}"
        
        self.logger.info(f"Starting data collection and analysis workflow: {workflow_id}")
        
        workflow_tasks = []
        
        # Collect data
        if 'data_collector' in self.agents:
            task_id = self.agents['data_collector'].force_collection(symbols)
            workflow_tasks.append(('data_collection', task_id))
        
        # Basic correlation analysis
        if 'analyzer' in self.agents:
            task_id = self.agents['analyzer'].force_analysis('correlation_analysis', symbols)
            workflow_tasks.append(('correlation_analysis', task_id))
        
        self.workflows[workflow_id] = {
            'name': 'data_collection_and_analysis',
            'parameters': parameters,
            'tasks': workflow_tasks,
            'status': 'running',
            'started_at': datetime.now().isoformat()
        }
        
        return workflow_id
    
    def _execute_emergency_analysis(self, parameters: Dict[str, Any]) -> str:
        """Execute emergency analysis workflow with high priority"""
        symbols = parameters.get('symbols', self.config['symbols'])
        workflow_id = f"emergency_{int(time.time())}"
        
        self.logger.warning(f"Starting emergency analysis workflow: {workflow_id}")
        
        workflow_tasks = []
        
        # High priority analysis
        if 'analyzer' in self.agents:
            # Create multiple high-priority tasks
            for analysis_type in ['correlation_analysis', 'volatility_analysis', 'network_analysis']:
                task = self.agents['analyzer'].create_task(
                    f"Emergency {analysis_type}",
                    {
                        'type': analysis_type,
                        'symbols': symbols
                    },
                    priority=TaskPriority.CRITICAL
                )
                workflow_tasks.append((analysis_type, task.id))
        
        self.workflows[workflow_id] = {
            'name': 'emergency_analysis',
            'parameters': parameters,
            'tasks': workflow_tasks,
            'status': 'running',
            'started_at': datetime.now().isoformat()
        }
        
        return workflow_id
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of a specific workflow"""
        if workflow_id not in self.workflows:
            return {'error': 'Workflow not found'}
        
        workflow = self.workflows[workflow_id]
        
        # Check task statuses
        task_statuses = {}
        for task_type, task_id in workflow['tasks']:
            # This would need to be implemented to check actual task status
            task_statuses[task_type] = 'unknown'  # Placeholder
        
        return {
            'workflow_id': workflow_id,
            'name': workflow['name'],
            'status': workflow['status'],
            'started_at': workflow['started_at'],
            'task_statuses': task_statuses,
            'parameters': workflow['parameters']
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        agent_statuses = {}
        for agent_name, agent in self.agents.items():
            agent_statuses[agent_name] = agent.get_status()
        
        return {
            'system_status': self.system_status,
            'scheduler_active': self.scheduler_active,
            'total_agents': len(self.agents),
            'active_workflows': len([w for w in self.workflows.values() if w['status'] == 'running']),
            'total_workflows': len(self.workflows),
            'agents': agent_statuses,
            'message_queue_size': len(self.message_queue),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health status"""
        agent_health = {}
        overall_healthy = True
        
        for agent_name, agent in self.agents.items():
            health = agent.health_check()
            agent_health[agent_name] = health
            if not health.get('healthy', False):
                overall_healthy = False
        
        return {
            'overall_healthy': overall_healthy,
            'system_status': self.system_status,
            'agents': agent_health,
            'scheduler_active': self.scheduler_active,
            'timestamp': datetime.now().isoformat()
        }
    
    def restart_agent(self, agent_name: str):
        """Restart a specific agent"""
        if agent_name not in self.agents:
            raise ValueError(f"Agent {agent_name} not found")
        
        agent = self.agents[agent_name]
        
        self.logger.info(f"Restarting agent: {agent_name}")
        
        # Stop the agent
        agent.stop()
        
        # Wait a moment
        time.sleep(2)
        
        # Start the agent
        agent.start()
        
        self.logger.info(f"Agent {agent_name} restarted")
    
    def get_agent_logs(self, agent_name: str, lines: int = 100) -> List[str]:
        """Get recent logs from a specific agent"""
        # This would need to be implemented to access agent logs
        # For now, return a placeholder
        return [f"Log entry for {agent_name} - not implemented yet"]


def main():
    """Main function for running the agent coordinator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Multi-Market Correlation Engine Agent Coordinator')
    parser.add_argument('--config', type=str, help='Configuration file path')
    parser.add_argument('--workflow', type=str, help='Workflow to execute')
    parser.add_argument('--symbols', nargs='+', help='Symbols to analyze')
    parser.add_argument('--test-mode', action='store_true', help='Run in test mode')
    
    args = parser.parse_args()
    
    # Load configuration
    config = {}
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    # Override symbols if provided
    if args.symbols:
        config['symbols'] = args.symbols
    
    # Initialize coordinator
    coordinator = AgentCoordinator(config)
    
    try:
        # Start the system
        coordinator.start_system()
        
        # Execute workflow if specified
        if args.workflow:
            workflow_params = {}
            if args.symbols:
                workflow_params['symbols'] = args.symbols
            
            workflow_id = coordinator.execute_workflow(args.workflow, workflow_params)
            print(f"Started workflow {args.workflow}: {workflow_id}")
        
        if args.test_mode:
            # Run for a short time in test mode
            print("Running in test mode for 60 seconds...")
            time.sleep(60)
        else:
            # Run indefinitely
            print("Agent system running. Press Ctrl+C to stop.")
            while True:
                time.sleep(10)
                
                # Print periodic status
                status = coordinator.get_system_status()
                print(f"System Status: {status['system_status']}, "
                      f"Active Agents: {status['total_agents']}, "
                      f"Active Workflows: {status['active_workflows']}")
    
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        coordinator.stop_system()


if __name__ == "__main__":
    main() 
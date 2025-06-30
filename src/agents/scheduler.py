"""
Scheduler Agent for Multi-Market Correlation Engine

This agent handles automated scheduling of tasks across the system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import schedule
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
import json

from .base_agent import BaseAgent, Task, TaskPriority, AgentStatus


class SchedulerAgent(BaseAgent):
    """
    Agent responsible for scheduling and executing recurring tasks.
    
    Features:
    - Cron-like scheduling
    - Task dependency management
    - Retry logic for failed tasks
    - Dynamic schedule updates
    - Performance monitoring
    """
    
    def __init__(self, agent_id: str = "scheduler-001", 
                 name: str = "Scheduler Agent", 
                 config: Optional[Dict] = None):
        """
        Initialize the scheduler agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name for the agent
            config: Configuration dictionary
        """
        default_config = {
            'max_concurrent_jobs': 5,
            'retry_attempts': 3,
            'retry_delay': 300,  # 5 minutes
            'job_timeout': 3600,  # 1 hour
            'enable_job_persistence': True,
            'schedule_file': 'data/schedules.json'
        }
        
        if config:
            default_config.update(config)
        
        super().__init__(agent_id, name, default_config)
        
        # Scheduling state
        self.scheduled_jobs = {}
        self.running_jobs = {}
        self.job_history = []
        self.job_counter = 0
        
        # Load persistent schedules
        self._load_schedules()
        
        self.logger.info("Scheduler Agent initialized")
    
    def execute_task(self, task: Task) -> Any:
        """Execute a scheduler task"""
        task_type = task.data.get('type', 'unknown')
        
        try:
            if task_type == 'schedule_job':
                return self._schedule_job(task.data)
            elif task_type == 'cancel_job':
                return self._cancel_job(task.data)
            elif task_type == 'list_jobs':
                return self._list_jobs(task.data)
            elif task_type == 'execute_job':
                return self._execute_scheduled_job(task.data)
            elif task_type == 'cleanup_history':
                return self._cleanup_job_history(task.data)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
                
        except Exception as e:
            self.logger.error(f"Scheduler task execution failed: {e}")
            raise
    
    def _schedule_job(self, task_data: Dict) -> Dict[str, Any]:
        """Schedule a new job"""
        job_name = task_data.get('job_name')
        schedule_type = task_data.get('schedule_type')  # 'interval', 'daily', 'weekly', etc.
        schedule_params = task_data.get('schedule_params', {})
        job_config = task_data.get('job_config', {})
        
        if not job_name:
            raise ValueError("Job name is required")
        
        self.job_counter += 1
        job_id = f"job_{self.job_counter}_{int(time.time())}"
        
        # Create job definition
        job_def = {
            'job_id': job_id,
            'job_name': job_name,
            'schedule_type': schedule_type,
            'schedule_params': schedule_params,
            'job_config': job_config,
            'created_at': datetime.now().isoformat(),
            'last_run': None,
            'next_run': None,
            'run_count': 0,
            'failure_count': 0,
            'enabled': True
        }
        
        # Schedule the job
        try:
            self._create_schedule(job_def)
            self.scheduled_jobs[job_id] = job_def
            
            # Save to persistence
            if self.config['enable_job_persistence']:
                self._save_schedules()
            
            self.logger.info(f"Job scheduled: {job_name} ({job_id})")
            
            return {
                'job_id': job_id,
                'status': 'scheduled',
                'message': f"Job {job_name} scheduled successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to schedule job {job_name}: {e}")
            raise
    
    def _create_schedule(self, job_def: Dict):
        """Create a schedule based on job definition"""
        schedule_type = job_def['schedule_type']
        params = job_def['schedule_params']
        job_id = job_def['job_id']
        
        if schedule_type == 'interval':
            # Every X minutes/hours
            interval = params.get('interval', 60)  # minutes
            unit = params.get('unit', 'minutes')
            
            if unit == 'minutes':
                schedule.every(interval).minutes.do(
                    self._trigger_job_execution, job_id
                ).tag(job_id)
            elif unit == 'hours':
                schedule.every(interval).hours.do(
                    self._trigger_job_execution, job_id
                ).tag(job_id)
            elif unit == 'seconds':
                schedule.every(interval).seconds.do(
                    self._trigger_job_execution, job_id
                ).tag(job_id)
        
        elif schedule_type == 'daily':
            # Daily at specific time
            time_str = params.get('time', '09:00')
            schedule.every().day.at(time_str).do(
                self._trigger_job_execution, job_id
            ).tag(job_id)
        
        elif schedule_type == 'weekly':
            # Weekly on specific day and time
            day = params.get('day', 'monday')
            time_str = params.get('time', '09:00')
            
            if day.lower() == 'monday':
                schedule.every().monday.at(time_str).do(
                    self._trigger_job_execution, job_id
                ).tag(job_id)
            elif day.lower() == 'tuesday':
                schedule.every().tuesday.at(time_str).do(
                    self._trigger_job_execution, job_id
                ).tag(job_id)
            # Add other days as needed
        
        elif schedule_type == 'cron':
            # Simplified cron-like scheduling
            # This would need more sophisticated implementation
            self.logger.warning("Cron scheduling not fully implemented")
        
        else:
            raise ValueError(f"Unknown schedule type: {schedule_type}")
        
        # Update next run time
        job_def['next_run'] = self._get_next_run_time(job_id)
    
    def _get_next_run_time(self, job_id: str) -> Optional[str]:
        """Get the next scheduled run time for a job"""
        try:
            jobs = schedule.get_jobs(tag=job_id)
            if jobs:
                next_run = jobs[0].next_run
                return next_run.isoformat() if next_run else None
        except:
            pass
        return None
    
    def _trigger_job_execution(self, job_id: str):
        """Trigger execution of a scheduled job"""
        if job_id not in self.scheduled_jobs:
            self.logger.warning(f"Job {job_id} not found in scheduled jobs")
            return
        
        job_def = self.scheduled_jobs[job_id]
        
        if not job_def.get('enabled', True):
            self.logger.debug(f"Job {job_id} is disabled, skipping")
            return
        
        # Check if we're at max concurrent jobs
        if len(self.running_jobs) >= self.config['max_concurrent_jobs']:
            self.logger.warning(f"Max concurrent jobs reached, delaying {job_id}")
            # Could implement queuing here
            return
        
        # Create execution task
        self.create_task(
            f"Execute Job: {job_def['job_name']}",
            {
                'type': 'execute_job',
                'job_id': job_id
            },
            priority=TaskPriority.MEDIUM
        )
    
    def _execute_scheduled_job(self, task_data: Dict) -> Dict[str, Any]:
        """Execute a scheduled job"""
        job_id = task_data.get('job_id')
        
        if job_id not in self.scheduled_jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job_def = self.scheduled_jobs[job_id]
        job_config = job_def['job_config']
        
        # Mark job as running
        execution_id = f"exec_{job_id}_{int(time.time())}"
        execution_info = {
            'execution_id': execution_id,
            'job_id': job_id,
            'job_name': job_def['job_name'],
            'started_at': datetime.now().isoformat(),
            'status': 'running'
        }
        
        self.running_jobs[execution_id] = execution_info
        
        try:
            self.logger.info(f"Executing job: {job_def['job_name']} ({job_id})")
            
            # Execute the actual job based on job type
            result = self._execute_job_by_type(job_config)
            
            # Update execution info
            execution_info.update({
                'status': 'completed',
                'completed_at': datetime.now().isoformat(),
                'result': result
            })
            
            # Update job statistics
            job_def['last_run'] = execution_info['completed_at']
            job_def['run_count'] += 1
            job_def['next_run'] = self._get_next_run_time(job_id)
            
            self.logger.info(f"Job completed: {job_def['job_name']}")
            
        except Exception as e:
            self.logger.error(f"Job execution failed: {job_def['job_name']} - {e}")
            
            # Update execution info
            execution_info.update({
                'status': 'failed',
                'failed_at': datetime.now().isoformat(),
                'error': str(e)
            })
            
            # Update job statistics
            job_def['failure_count'] += 1
            
            # Implement retry logic
            if job_def['failure_count'] <= self.config['retry_attempts']:
                self.logger.info(f"Scheduling retry for job: {job_def['job_name']}")
                # Schedule retry
                retry_time = datetime.now() + timedelta(seconds=self.config['retry_delay'])
                self.create_task(
                    f"Retry Job: {job_def['job_name']}",
                    {
                        'type': 'execute_job',
                        'job_id': job_id
                    },
                    priority=TaskPriority.HIGH,
                    scheduled_at=retry_time
                )
        
        finally:
            # Move to history and remove from running
            self.job_history.append(execution_info)
            self.running_jobs.pop(execution_id, None)
            
            # Save updated schedules
            if self.config['enable_job_persistence']:
                self._save_schedules()
        
        return execution_info
    
    def _execute_job_by_type(self, job_config: Dict) -> Any:
        """Execute job based on its type"""
        job_type = job_config.get('type', 'unknown')
        
        if job_type == 'agent_task':
            # Execute a task on another agent
            return self._execute_agent_task(job_config)
        
        elif job_type == 'workflow':
            # Execute a workflow
            return self._execute_workflow(job_config)
        
        elif job_type == 'system_command':
            # Execute a system command
            return self._execute_system_command(job_config)
        
        elif job_type == 'health_check':
            # Perform system health check
            return self._execute_health_check(job_config)
        
        else:
            raise ValueError(f"Unknown job type: {job_type}")
    
    def _execute_agent_task(self, job_config: Dict) -> Dict[str, Any]:
        """Execute a task on another agent"""
        from .base_agent import agent_registry
        
        agent_id = job_config.get('agent_id')
        task_config = job_config.get('task_config', {})
        
        agent = agent_registry.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        # Create and execute task
        task = agent.create_task(
            task_config.get('name', 'Scheduled Task'),
            task_config.get('data', {}),
            priority=TaskPriority(task_config.get('priority', 2))
        )
        
        return {'task_id': task.id, 'agent_id': agent_id}
    
    def _execute_workflow(self, job_config: Dict) -> Dict[str, Any]:
        """Execute a workflow"""
        # This would integrate with the workflow system
        workflow_name = job_config.get('workflow_name')
        workflow_params = job_config.get('workflow_params', {})
        
        # Placeholder - would need actual workflow execution
        return {
            'workflow_name': workflow_name,
            'status': 'executed',
            'message': 'Workflow execution not implemented'
        }
    
    def _execute_system_command(self, job_config: Dict) -> Dict[str, Any]:
        """Execute a system command"""
        import subprocess
        
        command = job_config.get('command')
        if not command:
            raise ValueError("Command is required")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=job_config.get('timeout', 300)
            )
            
            return {
                'command': command,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except subprocess.TimeoutExpired:
            raise Exception(f"Command timed out: {command}")
    
    def _execute_health_check(self, job_config: Dict) -> Dict[str, Any]:
        """Execute a health check"""
        from .base_agent import agent_registry
        
        # Check all registered agents
        health_results = agent_registry.health_check_all()
        
        # Count healthy vs unhealthy
        healthy_count = sum(1 for h in health_results.values() if h.get('healthy', False))
        total_count = len(health_results)
        
        return {
            'healthy_agents': healthy_count,
            'total_agents': total_count,
            'overall_healthy': healthy_count == total_count,
            'details': health_results
        }
    
    def _cancel_job(self, task_data: Dict) -> Dict[str, Any]:
        """Cancel a scheduled job"""
        job_id = task_data.get('job_id')
        
        if job_id not in self.scheduled_jobs:
            return {'error': f'Job {job_id} not found'}
        
        # Remove from schedule
        schedule.clear(tag=job_id)
        
        # Mark as disabled
        self.scheduled_jobs[job_id]['enabled'] = False
        
        # Save changes
        if self.config['enable_job_persistence']:
            self._save_schedules()
        
        self.logger.info(f"Job cancelled: {job_id}")
        
        return {
            'job_id': job_id,
            'status': 'cancelled',
            'message': f'Job {job_id} cancelled successfully'
        }
    
    def _list_jobs(self, task_data: Dict) -> Dict[str, Any]:
        """List all scheduled jobs"""
        include_disabled = task_data.get('include_disabled', False)
        
        jobs = []
        for job_id, job_def in self.scheduled_jobs.items():
            if not include_disabled and not job_def.get('enabled', True):
                continue
            
            jobs.append({
                'job_id': job_id,
                'job_name': job_def['job_name'],
                'schedule_type': job_def['schedule_type'],
                'enabled': job_def.get('enabled', True),
                'last_run': job_def.get('last_run'),
                'next_run': job_def.get('next_run'),
                'run_count': job_def.get('run_count', 0),
                'failure_count': job_def.get('failure_count', 0)
            })
        
        return {
            'total_jobs': len(jobs),
            'running_jobs': len(self.running_jobs),
            'jobs': jobs
        }
    
    def _cleanup_job_history(self, task_data: Dict) -> Dict[str, Any]:
        """Clean up old job history"""
        retention_days = task_data.get('retention_days', 30)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        initial_count = len(self.job_history)
        
        self.job_history = [
            entry for entry in self.job_history
            if datetime.fromisoformat(entry['started_at']) > cutoff_date
        ]
        
        cleaned_count = initial_count - len(self.job_history)
        
        self.logger.info(f"Cleaned up {cleaned_count} old job history entries")
        
        return {
            'cleaned_entries': cleaned_count,
            'remaining_entries': len(self.job_history),
            'cutoff_date': cutoff_date.isoformat()
        }
    
    def _load_schedules(self):
        """Load schedules from persistence"""
        if not self.config['enable_job_persistence']:
            return
        
        try:
            schedule_file = self.config['schedule_file']
            if os.path.exists(schedule_file):
                with open(schedule_file, 'r') as f:
                    data = json.load(f)
                    self.scheduled_jobs = data.get('scheduled_jobs', {})
                    self.job_counter = data.get('job_counter', 0)
                
                # Recreate schedules
                for job_def in self.scheduled_jobs.values():
                    if job_def.get('enabled', True):
                        try:
                            self._create_schedule(job_def)
                        except Exception as e:
                            self.logger.error(f"Failed to recreate schedule for {job_def['job_name']}: {e}")
                
                self.logger.info(f"Loaded {len(self.scheduled_jobs)} scheduled jobs")
        
        except Exception as e:
            self.logger.error(f"Failed to load schedules: {e}")
    
    def _save_schedules(self):
        """Save schedules to persistence"""
        if not self.config['enable_job_persistence']:
            return
        
        try:
            schedule_file = self.config['schedule_file']
            os.makedirs(os.path.dirname(schedule_file), exist_ok=True)
            
            data = {
                'scheduled_jobs': self.scheduled_jobs,
                'job_counter': self.job_counter,
                'saved_at': datetime.now().isoformat()
            }
            
            with open(schedule_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception as e:
            self.logger.error(f"Failed to save schedules: {e}")
    
    def _idle_work(self):
        """Perform idle work - run scheduled jobs"""
        try:
            schedule.run_pending()
        except Exception as e:
            self.logger.error(f"Error running scheduled jobs: {e}")
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get detailed scheduler status"""
        return {
            'total_scheduled_jobs': len(self.scheduled_jobs),
            'enabled_jobs': len([j for j in self.scheduled_jobs.values() if j.get('enabled', True)]),
            'running_jobs': len(self.running_jobs),
            'job_history_size': len(self.job_history),
            'next_jobs': self._get_next_jobs(5),
            'recent_executions': self.job_history[-10:] if self.job_history else []
        }
    
    def _get_next_jobs(self, limit: int = 5) -> List[Dict]:
        """Get next scheduled jobs"""
        next_jobs = []
        
        for job_id, job_def in self.scheduled_jobs.items():
            if job_def.get('enabled', True) and job_def.get('next_run'):
                next_jobs.append({
                    'job_id': job_id,
                    'job_name': job_def['job_name'],
                    'next_run': job_def['next_run']
                })
        
        # Sort by next run time
        next_jobs.sort(key=lambda x: x['next_run'])
        
        return next_jobs[:limit]


if __name__ == "__main__":
    # Test the scheduler agent
    agent = SchedulerAgent()
    
    # Start the agent
    agent.start()
    
    # Schedule a test job
    agent.create_task(
        "Schedule Test Job",
        {
            'type': 'schedule_job',
            'job_name': 'Test Health Check',
            'schedule_type': 'interval',
            'schedule_params': {'interval': 1, 'unit': 'minutes'},
            'job_config': {'type': 'health_check'}
        },
        priority=TaskPriority.HIGH
    )
    
    # Run for a bit
    time.sleep(120)  # 2 minutes
    
    # Check status
    status = agent.get_scheduler_status()
    print("Scheduler Status:")
    print(f"Scheduled jobs: {status['total_scheduled_jobs']}")
    print(f"Running jobs: {status['running_jobs']}")
    
    # Stop the agent
    agent.stop()
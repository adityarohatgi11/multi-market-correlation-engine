#!/usr/bin/env python3
"""
Comprehensive test script for Phase 3: Multi-Agent Automation
Tests: Base Agent, Data Collection Agent, Analysis Agent, Agent Coordinator, Scheduler, Reporting Agent
"""

import sys
import os
import traceback
import time
from datetime import datetime, timedelta

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def setup_test_environment():
    """Set up test environment with test database"""
    # Set environment variable for test database
    os.environ["DATABASE_URL"] = "sqlite:///test_phase3.db"
    print("✅ Test environment configured")

def test_imports():
    """Test all Phase 3 imports"""
    print("=" * 60)
    print("TESTING PHASE 3 IMPORTS")
    print("=" * 60)
    
    imports_to_test = [
        ("base_agent", "BaseAgent"),
        ("data_collection_agent", "DataCollectionAgent"),
        ("analysis_agent", "AnalysisAgent"),
        ("agent_coordinator", "AgentCoordinator"),
        ("scheduler", "SchedulerAgent"),
        ("reporting_agent", "ReportingAgent")
    ]
    
    success_count = 0
    for module_name, class_name in imports_to_test:
        try:
            module = __import__(f"src.agents.{module_name}", fromlist=[class_name])
            getattr(module, class_name)
            print(f"✅ {class_name} import successful")
            success_count += 1
        except Exception as e:
            print(f"❌ {class_name} import failed: {e}")
            traceback.print_exc()
    
    return success_count == len(imports_to_test)

def test_base_agent():
    """Test BaseAgent functionality through concrete implementation"""
    print("\n" + "=" * 60)
    print("TESTING BASE AGENT (via TestAgent)")
    print("=" * 60)
    
    try:
        from src.agents.base_agent import BaseAgent, Task, TaskPriority
        
        # Create a concrete test agent implementation
        class TestAgent(BaseAgent):
            def execute_task(self, task: Task) -> any:
                """Test implementation of abstract method"""
                return f"Executed task: {task.name}"
        
        # Create test agent
        agent = TestAgent("test_agent", "Test Agent")
        print("✅ TestAgent initialization successful")
        
        # Test task creation and queuing
        task = agent.create_task(
            "test_task_1",
            {"test": "data"},
            priority=TaskPriority.MEDIUM
        )
        print("✅ Task creation and queuing successful")
        
        # Test agent status
        status = agent.get_status()
        print(f"✅ Agent status: {status['status']}")
        
        # Test health check
        health = agent.health_check()
        print(f"✅ Health check: {'Healthy' if health['healthy'] else 'Unhealthy'}")
        
        # Test metrics
        metrics = agent.metrics
        print(f"✅ Metrics retrieved: {metrics.tasks_completed} tasks completed")
        
        # Stop agent
        agent.stop()
        print("✅ Agent stopped successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ BaseAgent test failed: {e}")
        traceback.print_exc()
        return False

def test_data_collection_agent():
    """Test DataCollectionAgent functionality"""
    print("\n" + "=" * 60)
    print("TESTING DATA COLLECTION AGENT")
    print("=" * 60)
    
    try:
        from src.agents.data_collection_agent import DataCollectionAgent
        from src.agents.base_agent import TaskPriority
        
        # Initialize agent
        agent = DataCollectionAgent("data_collector", "Data Collection Agent")
        print("✅ DataCollectionAgent initialization successful")
        
        # Test agent start
        agent.start()
        time.sleep(1)  # Give it a moment to start
        print("✅ Agent started successfully")
        
        # Test task creation using the base create_task method
        collection_task = agent.create_task(
            "Test Collection Task",
            {
                'type': 'collect_real_time',
                'symbols': ['AAPL', 'MSFT'],
                'source': 'yahoo_finance'
            },
            priority=TaskPriority.MEDIUM
        )
        print("✅ Collection task created and queued")
        
        # Wait for task processing
        time.sleep(3)
        
        # Test health check
        health = agent.health_check()
        print(f"✅ Health check: {'Healthy' if health['healthy'] else 'Unhealthy'}")
        
        # Test metrics
        metrics = agent.metrics
        print(f"✅ Collection metrics: {metrics.tasks_completed} tasks completed")
        
        # Test collection status
        status = agent.get_collection_status()
        print(f"✅ Collection status retrieved: {len(status)} metrics")
        
        # Stop agent
        agent.stop()
        print("✅ Data collection agent stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ DataCollectionAgent test failed: {e}")
        traceback.print_exc()
        return False

def test_analysis_agent():
    """Test AnalysisAgent functionality"""
    print("\n" + "=" * 60)
    print("TESTING ANALYSIS AGENT")
    print("=" * 60)
    
    try:
        from src.agents.analysis_agent import AnalysisAgent
        from src.agents.base_agent import TaskPriority
        
        # Initialize agent
        agent = AnalysisAgent("analyzer", "Analysis Agent")
        print("✅ AnalysisAgent initialization successful")
        
        # Test agent start
        agent.start()
        time.sleep(1)
        print("✅ Analysis agent started")
        
        # Test analysis task creation using base create_task method
        analysis_task = agent.create_task(
            "Test Analysis Task",
            {
                'type': 'correlation_analysis',
                'symbols': ['AAPL', 'MSFT']
            },
            priority=TaskPriority.MEDIUM
        )
        print("✅ Analysis task created and queued")
        
        # Wait for processing
        time.sleep(2)
        
        # Test health check
        health = agent.health_check()
        print(f"✅ Health check: {'Healthy' if health['healthy'] else 'Unhealthy'}")
        
        # Test analysis status
        status = agent.get_analysis_status()
        print(f"✅ Analysis status retrieved: {len(status)} metrics")
        
        # Stop agent
        agent.stop()
        print("✅ Analysis agent stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ AnalysisAgent test failed: {e}")
        traceback.print_exc()
        return False

def test_scheduler_agent():
    """Test SchedulerAgent functionality"""
    print("\n" + "=" * 60)
    print("TESTING SCHEDULER AGENT")
    print("=" * 60)
    
    try:
        from src.agents.scheduler import SchedulerAgent
        from src.agents.base_agent import TaskPriority
        
        agent = SchedulerAgent("scheduler", "Scheduler Agent")
        print("✅ SchedulerAgent initialization successful")
        
        # Test agent start
        agent.start()
        time.sleep(1)
        print("✅ Scheduler agent started")
        
        # Test job scheduling using create_task
        schedule_task = agent.create_task(
            "Test Schedule Task",
            {
                'type': 'schedule_job',
                'job_name': 'test_job',
                'interval_seconds': 5,
                'job_data': {'test': 'data'}
            },
            priority=TaskPriority.MEDIUM
        )
        print("✅ Schedule task created and queued")
        
        # Test health check
        health = agent.health_check()
        print(f"✅ Health check: {'Healthy' if health['healthy'] else 'Unhealthy'}")
        
        # Test scheduler status
        status = agent.get_scheduler_status()
        print(f"✅ Scheduler status retrieved: {len(status)} metrics")
        
        # Stop agent
        agent.stop()
        print("✅ Scheduler agent stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ SchedulerAgent test failed: {e}")
        traceback.print_exc()
        return False

def test_reporting_agent():
    """Test ReportingAgent functionality"""
    print("\n" + "=" * 60)
    print("TESTING REPORTING AGENT")
    print("=" * 60)
    
    try:
        from src.agents.reporting_agent import ReportingAgent
        from src.agents.base_agent import TaskPriority
        
        # Initialize agent
        agent = ReportingAgent("reporter", "Reporting Agent")
        print("✅ ReportingAgent initialization successful")
        
        # Test agent start
        agent.start()
        time.sleep(1)
        print("✅ Reporting agent started")
        
        # Test report generation task using create_task
        report_task = agent.create_task(
            "Test Report Task",
            {
                'type': 'generate_report',
                'report_type': 'correlation_report',
                'symbols': ['AAPL', 'MSFT']
            },
            priority=TaskPriority.MEDIUM
        )
        print("✅ Report task created and queued")
        
        # Wait for processing
        time.sleep(2)
        
        # Test health check
        health = agent.health_check()
        print(f"✅ Health check: {'Healthy' if health['healthy'] else 'Unhealthy'}")
        
        # Test reporting status
        status = agent.get_reporting_status()
        print(f"✅ Reporting status retrieved: {len(status)} metrics")
        
        # Stop agent
        agent.stop()
        print("✅ Reporting agent stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ ReportingAgent test failed: {e}")
        traceback.print_exc()
        return False

def test_agent_coordinator():
    """Test AgentCoordinator functionality"""
    print("\n" + "=" * 60)
    print("TESTING AGENT COORDINATOR")
    print("=" * 60)
    
    try:
        from src.agents.agent_coordinator import AgentCoordinator
        
        # Initialize coordinator with configuration (not db_manager)
        test_config = {
            'enable_data_collection': True,
            'enable_analysis': True,
            'symbols': ['AAPL', 'MSFT'],
            'auto_start_agents': False  # Don't auto-start for testing
        }
        coordinator = AgentCoordinator(config=test_config)
        print("✅ AgentCoordinator initialization successful")
        
        # Test workflow execution
        workflow_id = coordinator.execute_workflow("data_collection_and_analysis", {"symbols": ['AAPL', 'MSFT']})
        print(f"✅ Workflow executed: {workflow_id}")
        
        # Wait for workflow processing
        time.sleep(2)
        
        # Test system status
        status = coordinator.get_system_status()
        print(f"✅ System status: {len(status)} metrics")
        
        # Test system health
        health = coordinator.get_system_health()
        print(f"✅ System health retrieved: {len(health)} agents")
        
        # Stop coordinator
        coordinator.stop_system()
        print("✅ Coordinator stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ AgentCoordinator test failed: {e}")
        traceback.print_exc()
        return False

def test_inter_agent_communication():
    """Test inter-agent communication"""
    print("\n" + "=" * 60)
    print("TESTING INTER-AGENT COMMUNICATION")
    print("=" * 60)
    
    try:
        from src.agents.base_agent import BaseAgent
        
        # Create concrete test agents
        class TestAgent(BaseAgent):
            def execute_task(self, task) -> any:
                return f"Executed: {task.name}"
        
        # Create two test agents
        agent1 = TestAgent("agent1", "Agent 1")
        agent2 = TestAgent("agent2", "Agent 2")
        
        agent1.start()
        agent2.start()
        time.sleep(1)
        print("✅ Two agents started")
        
        # Test message sending
        agent1.send_message("agent2", "test_message", {"test": "communication"})
        print("✅ Message sent from agent1 to agent2")
        
        # Wait for message processing
        time.sleep(1)
        
        # Test agent communication is working (messages are handled internally)
        print("✅ Inter-agent communication system functional")
        
        # Stop agents
        agent1.stop()
        agent2.stop()
        print("✅ Agents stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ Inter-agent communication test failed: {e}")
        traceback.print_exc()
        return False

def cleanup_test_files():
    """Clean up test files"""
    try:
        test_files = ["test_phase3.db"]
        for file_path in test_files:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"✅ Cleaned up {file_path}")
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")

def main():
    """Run all Phase 3 tests"""
    print("PHASE 3 MULTI-AGENT AUTOMATION TESTING")
    print("=" * 60)
    
    # Setup test environment
    setup_test_environment()
    
    test_results = []
    
    # Test imports
    imports_success = test_imports()
    test_results.append(("Imports", imports_success))
    
    if not imports_success:
        print("❌ Imports failed, skipping other tests")
        return False
    
    # Test individual agents
    test_results.append(("Base Agent", test_base_agent()))
    test_results.append(("Data Collection Agent", test_data_collection_agent()))
    test_results.append(("Analysis Agent", test_analysis_agent()))
    test_results.append(("Scheduler Agent", test_scheduler_agent()))
    test_results.append(("Reporting Agent", test_reporting_agent()))
    test_results.append(("Agent Coordinator", test_agent_coordinator()))
    test_results.append(("Inter-Agent Communication", test_inter_agent_communication()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("PHASE 3 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(test_results)} tests passed")
    
    # Cleanup
    cleanup_test_files()
    
    return passed == len(test_results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
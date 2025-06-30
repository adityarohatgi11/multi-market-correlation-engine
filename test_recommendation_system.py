#!/usr/bin/env python3
"""
Comprehensive Test for Asset Recommendation System
================================================

Tests the complete recommendation engine integration.

Author: Multi-Market Correlation Engine Team
Version: 1.0.0
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RecommendationSystemTester:
    """Comprehensive tester for the recommendation system."""
    
    def __init__(self):
        """Initialize the tester."""
        self.test_results = []
        self.test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
        self.sample_portfolio = {
            'AAPL': 0.3,
            'MSFT': 0.25,
            'GOOGL': 0.2,
            'AMZN': 0.15,
            'TSLA': 0.1
        }
    
    def log_test(self, test_name: str, success: bool, message: str = "", duration: float = 0):
        """Log test results."""
        status = "✅ PASSED" if success else "❌ FAILED"
        duration_str = f" ({duration:.2f}s)" if duration > 0 else ""
        
        result = {
            'test_name': test_name,
            'status': status,
            'success': success,
            'message': message,
            'duration': duration
        }
        
        self.test_results.append(result)
        
        print(f"{status}: {test_name}{duration_str}")
        if message:
            print(f"   📝 {message}")
        print()
    
    def test_recommendation_engine_import(self):
        """Test recommendation engine import."""
        start_time = time.time()
        try:
            from src.models.recommendation_engine import AssetRecommendationEngine, PortfolioOptimizer
            engine = AssetRecommendationEngine()
            optimizer = PortfolioOptimizer()
            
            self.log_test(
                "Recommendation Engine Import",
                True,
                "Successfully imported and initialized recommendation engine",
                time.time() - start_time
            )
            return engine, optimizer
            
        except Exception as e:
            self.log_test(
                "Recommendation Engine Import",
                False,
                f"Import failed: {e}",
                time.time() - start_time
            )
            return None, None
    
    def test_recommendation_agent_import(self):
        """Test recommendation agent import."""
        start_time = time.time()
        try:
            from src.agents.recommendation_agent import RecommendationAgent
            agent = RecommendationAgent()
            
            self.log_test(
                "Recommendation Agent Import",
                True,
                "Successfully imported and initialized recommendation agent",
                time.time() - start_time
            )
            return agent
            
        except Exception as e:
            self.log_test(
                "Recommendation Agent Import",
                False,
                f"Import failed: {e}",
                time.time() - start_time
            )
            return None
    
    def test_basic_recommendation_generation(self, engine):
        """Test basic recommendation generation."""
        if not engine:
            self.log_test("Basic Recommendation Generation", False, "Engine not available")
            return None
        
        start_time = time.time()
        try:
            recommendations = engine.generate_recommendations(
                portfolio=self.sample_portfolio,
                universe=self.test_symbols,
                horizon="1M",
                strategy="balanced"
            )
            
            if 'error' in recommendations:
                self.log_test(
                    "Basic Recommendation Generation",
                    False,
                    f"Error in recommendations: {recommendations['error']}",
                    time.time() - start_time
                )
                return None
            
            # Check required fields
            required_fields = ['buy_signals', 'sell_signals', 'optimal_weights', 'risk_assessment']
            missing_fields = [field for field in required_fields if field not in recommendations]
            
            if missing_fields:
                self.log_test(
                    "Basic Recommendation Generation",
                    False,
                    f"Missing fields: {missing_fields}",
                    time.time() - start_time
                )
                return None
            
            buy_count = len(recommendations.get('buy_signals', []))
            sell_count = len(recommendations.get('sell_signals', []))
            
            self.log_test(
                "Basic Recommendation Generation",
                True,
                f"Generated {buy_count} buy signals, {sell_count} sell signals",
                time.time() - start_time
            )
            return recommendations
            
        except Exception as e:
            self.log_test(
                "Basic Recommendation Generation",
                False,
                f"Generation failed: {e}",
                time.time() - start_time
            )
            return None
    
    def test_portfolio_optimization(self, optimizer):
        """Test portfolio optimization."""
        if not optimizer:
            self.log_test("Portfolio Optimization", False, "Optimizer not available")
            return
        
        start_time = time.time()
        try:
            # Create sample returns data
            dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
            returns_data = {}
            
            for symbol in self.test_symbols:
                returns_data[symbol] = np.random.normal(0.001, 0.02, len(dates))
            
            returns_df = pd.DataFrame(returns_data, index=dates)
            
            # Test mean-variance optimization
            optimal_weights = optimizer.mean_variance_optimization(returns_df)
            
            if optimal_weights and len(optimal_weights) > 0:
                total_weight = sum(optimal_weights.values())
                self.log_test(
                    "Portfolio Optimization",
                    True,
                    f"Optimized portfolio with {len(optimal_weights)} assets, total weight: {total_weight:.3f}",
                    time.time() - start_time
                )
            else:
                self.log_test(
                    "Portfolio Optimization",
                    False,
                    "Optimization returned empty results",
                    time.time() - start_time
                )
                
        except Exception as e:
            self.log_test(
                "Portfolio Optimization",
                False,
                f"Optimization failed: {e}",
                time.time() - start_time
            )
    
    def test_agent_task_handling(self, agent):
        """Test agent task handling."""
        if not agent:
            self.log_test("Agent Task Handling", False, "Agent not available")
            return
        
        start_time = time.time()
        try:
            from src.agents.base_agent import Task, TaskPriority
            
            # Test recommendation generation task
            task_data = {
                'type': 'generate_recommendations',
                'portfolio': self.sample_portfolio,
                'universe': self.test_symbols,
                'strategy': 'balanced',
                'horizon': '1M'
            }
            
            task = Task(
                id="test_recommendation",
                name="generate_recommendations",
                priority=TaskPriority.HIGH,
                created_at=datetime.now(),
                scheduled_at=None,
                data=task_data
            )
            
            result = agent._handle_task(task)
            
            if 'error' in result:
                self.log_test(
                    "Agent Task Handling",
                    False,
                    f"Task handling error: {result['error']}",
                    time.time() - start_time
                )
            else:
                self.log_test(
                    "Agent Task Handling",
                    True,
                    "Successfully handled recommendation task",
                    time.time() - start_time
                )
                
        except Exception as e:
            self.log_test(
                "Agent Task Handling",
                False,
                f"Task handling failed: {e}",
                time.time() - start_time
            )
    
    def test_api_endpoints(self):
        """Test API endpoints."""
        start_time = time.time()
        try:
            import requests
            
            # Test if API is running
            response = requests.get("http://127.0.0.1:8000/health", timeout=5)
            if response.status_code != 200:
                self.log_test(
                    "API Endpoints",
                    False,
                    "API server not running",
                    time.time() - start_time
                )
                return
            
            # Test recommendations endpoint
            test_payload = {
                "portfolio": self.sample_portfolio,
                "universe": self.test_symbols,
                "strategy": "balanced",
                "horizon": "1M"
            }
            
            response = requests.post(
                "http://127.0.0.1:8000/recommendations/generate",
                json=test_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    self.log_test(
                        "API Endpoints",
                        True,
                        "Recommendations API endpoint working",
                        time.time() - start_time
                    )
                else:
                    self.log_test(
                        "API Endpoints",
                        False,
                        f"API returned error: {data.get('message', 'Unknown error')}",
                        time.time() - start_time
                    )
            else:
                self.log_test(
                    "API Endpoints",
                    False,
                    f"API request failed with status {response.status_code}",
                    time.time() - start_time
                )
                
        except requests.exceptions.ConnectionError:
            self.log_test(
                "API Endpoints",
                False,
                "Cannot connect to API server (not running)",
                time.time() - start_time
            )
        except Exception as e:
            self.log_test(
                "API Endpoints",
                False,
                f"API test failed: {e}",
                time.time() - start_time
            )
    
    def test_dashboard_components(self):
        """Test dashboard components."""
        start_time = time.time()
        try:
            from src.dashboard.components.recommendation_panel import RecommendationPanel
            
            panel = RecommendationPanel()
            
            self.log_test(
                "Dashboard Components",
                True,
                "Successfully imported recommendation panel",
                time.time() - start_time
            )
            
        except Exception as e:
            self.log_test(
                "Dashboard Components",
                False,
                f"Dashboard component test failed: {e}",
                time.time() - start_time
            )
    
    def test_integration_workflow(self, engine, agent):
        """Test complete integration workflow."""
        if not engine or not agent:
            self.log_test("Integration Workflow", False, "Components not available")
            return
        
        start_time = time.time()
        try:
            # Step 1: Generate recommendations
            recommendations = engine.generate_recommendations(
                portfolio=self.sample_portfolio,
                universe=self.test_symbols,
                horizon="1M",
                strategy="balanced"
            )
            
            if 'error' in recommendations:
                self.log_test(
                    "Integration Workflow",
                    False,
                    f"Workflow failed at recommendation generation: {recommendations['error']}",
                    time.time() - start_time
                )
                return
            
            # Step 2: Get optimal weights
            optimal_weights = recommendations.get('optimal_weights', {})
            
            # Step 3: Analyze portfolio using agent
            from src.agents.base_agent import Task, TaskPriority
            
            task_data = {
                'type': 'analyze_portfolio',
                'portfolio': optimal_weights,
                'benchmark': 'SPY'
            }
            
            task = Task(
                id="test_analysis",
                name="analyze_portfolio",
                priority=TaskPriority.MEDIUM,
                created_at=datetime.now(),
                scheduled_at=None,
                data=task_data
            )
            
            analysis_result = agent._handle_task(task)
            
            if 'error' in analysis_result:
                self.log_test(
                    "Integration Workflow",
                    False,
                    f"Workflow failed at portfolio analysis: {analysis_result['error']}",
                    time.time() - start_time
                )
                return
            
            self.log_test(
                "Integration Workflow",
                True,
                "Complete workflow executed successfully",
                time.time() - start_time
            )
            
        except Exception as e:
            self.log_test(
                "Integration Workflow",
                False,
                f"Integration workflow failed: {e}",
                time.time() - start_time
            )
    
    def run_all_tests(self):
        """Run all recommendation system tests."""
        print("🚀 ASSET RECOMMENDATION SYSTEM - COMPREHENSIVE TEST")
        print("=" * 60)
        
        # Test 1: Import recommendation engine
        engine, optimizer = self.test_recommendation_engine_import()
        
        # Test 2: Import recommendation agent
        agent = self.test_recommendation_agent_import()
        
        # Test 3: Basic recommendation generation
        recommendations = self.test_basic_recommendation_generation(engine)
        
        # Test 4: Portfolio optimization
        self.test_portfolio_optimization(optimizer)
        
        # Test 5: Agent task handling
        self.test_agent_task_handling(agent)
        
        # Test 6: API endpoints
        self.test_api_endpoints()
        
        # Test 7: Dashboard components
        self.test_dashboard_components()
        
        # Test 8: Integration workflow
        self.test_integration_workflow(engine, agent)
        
        # Generate summary
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print comprehensive test summary."""
        print("\n" + "=" * 60)
        print("📊 RECOMMENDATION SYSTEM TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test_name']}: {result['message']}")
        
        print(f"\n🎯 RECOMMENDATION SYSTEM STATUS:")
        if success_rate >= 90:
            print("🟢 EXCELLENT - Recommendation system fully operational!")
        elif success_rate >= 75:
            print("🟡 GOOD - Recommendation system mostly working with minor issues")
        elif success_rate >= 50:
            print("🟠 FAIR - Recommendation system partially working")
        else:
            print("🔴 POOR - Recommendation system needs significant fixes")
        
        print("\n" + "=" * 60)


def main():
    """Main test execution."""
    try:
        tester = RecommendationSystemTester()
        tester.run_all_tests()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test execution failed: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
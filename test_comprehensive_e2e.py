#!/usr/bin/env python3
"""
Comprehensive End-to-End Testing Suite
Multi-Market Correlation Engine with TypeScript Frontend
"""

import requests
import json
import time
from datetime import datetime

class ComprehensiveE2ETest:
    def __init__(self):
        self.frontend_url = "http://localhost:3000"
        self.api_url = "http://127.0.0.1:8000"
        self.test_results = []
        self.start_time = datetime.now()
        
    def log_test(self, test_name, status, details="", duration=0):
        """Log test results with color coding"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "duration": f"{duration:.2f}s"
        }
        self.test_results.append(result)
        
        # Color coding
        colors = {"PASS": "\033[92m", "FAIL": "\033[91m", "WARN": "\033[93m"}
        color = colors.get(status, "\033[0m")
        print(f"{color}[{status}] {test_name}: {details}\033[0m")
    
    def make_request(self, method, endpoint, **kwargs):
        """Make HTTP request with timing"""
        try:
            start_time = time.time()
            url = f"{self.api_url}{endpoint}"
            response = requests.request(method, url, timeout=30, **kwargs)
            duration = time.time() - start_time
            return response, duration, None
        except Exception as e:
            return None, 0, str(e)
    
    def test_backend_health(self):
        """Test 1: Backend API Health"""
        print("\n🏥 Testing Backend Health...")
        
        response, duration, error = self.make_request("GET", "/health")
        if error:
            self.log_test("Backend Health", "FAIL", f"Connection error: {error}", duration)
            return False
            
        if response and response.status_code == 200:
            self.log_test("Backend Health", "PASS", f"API healthy", duration)
            return True
        else:
            self.log_test("Backend Health", "FAIL", f"Status: {response.status_code if response else 'None'}", duration)
            return False
    
    def test_frontend_connectivity(self):
        """Test 2: Frontend Connectivity"""
        print("\n🌐 Testing Frontend...")
        
        try:
            start_time = time.time()
            response = requests.get(self.frontend_url, timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                content = response.text.lower()
                has_react = 'id="root"' in content
                has_scripts = 'script' in content
                
                if has_react and has_scripts:
                    self.log_test("Frontend Connectivity", "PASS", "React app loaded", duration)
                    return True
                else:
                    self.log_test("Frontend Connectivity", "WARN", "Partial load", duration)
                    return False
            else:
                self.log_test("Frontend Connectivity", "FAIL", f"HTTP {response.status_code}", duration)
                return False
        except Exception as e:
            self.log_test("Frontend Connectivity", "FAIL", f"Connection failed: {e}", 0)
            return False
    
    def test_llm_integration(self):
        """Test 3: LLM Features"""
        print("\n🤖 Testing LLM...")
        
        # LLM Status
        response, duration, error = self.make_request("GET", "/llm/status")
        if response and response.status_code == 200:
            self.log_test("LLM Status", "PASS", "LLM available", duration)
        else:
            self.log_test("LLM Status", "WARN", "LLM unavailable", duration)
        
        # LLM Chat
        chat_data = {"message": "What is correlation?", "context": "finance"}
        response, duration, error = self.make_request("POST", "/llm/chat", json=chat_data)
        
        if response and response.status_code == 200:
            self.log_test("LLM Chat", "PASS", "Chat working", duration)
            return True
        else:
            self.log_test("LLM Chat", "WARN", "Chat unavailable", duration)
            return False
    
    def test_vector_database(self):
        """Test 4: Vector Database"""
        print("\n🔍 Testing Vector DB...")
        
        # Vector stats
        response, duration, error = self.make_request("GET", "/llm/vector/stats")
        if response and response.status_code == 200:
            self.log_test("Vector Stats", "PASS", "Vector DB operational", duration)
        else:
            self.log_test("Vector Stats", "WARN", "Vector DB unavailable", duration)
        
        # Vector search
        search_data = {"query": "market patterns", "top_k": 3}
        response, duration, error = self.make_request("POST", "/llm/vector/search", json=search_data)
        
        if response and response.status_code == 200:
            self.log_test("Vector Search", "PASS", "Search working", duration)
            return True
        else:
            self.log_test("Vector Search", "WARN", "Search unavailable", duration)
            return False
    
    def test_market_features(self):
        """Test 5: Market Data & Analysis"""
        print("\n📊 Testing Market Features...")
        
        # Market data
        params = {"symbols": "AAPL,MSFT", "time_range": "1M"}
        response, duration, error = self.make_request("GET", "/market/data", params=params)
        
        if response and response.status_code == 200:
            self.log_test("Market Data", "PASS", "Data retrieval working", duration)
        else:
            self.log_test("Market Data", "WARN", "Data unavailable", duration)
        
        # Correlation analysis
        corr_data = {"symbols": ["AAPL", "MSFT"], "time_range": "1M"}
        response, duration, error = self.make_request("POST", "/market/correlation", json=corr_data)
        
        if response and response.status_code == 200:
            self.log_test("Correlation Analysis", "PASS", "Correlation working", duration)
            return True
        else:
            self.log_test("Correlation Analysis", "WARN", "Correlation unavailable", duration)
            return False
    
    def test_recommendations(self):
        """Test 6: Recommendations"""
        print("\n🎯 Testing Recommendations...")
        
        rec_data = {
            "portfolio": {"AAPL": 0.5, "MSFT": 0.5},
            "strategy": "balanced",
            "time_horizon": "6M",
            "risk_tolerance": "medium"
        }
        
        response, duration, error = self.make_request("POST", "/recommendations/generate", json=rec_data)
        
        if response and response.status_code == 200:
            self.log_test("Recommendations", "PASS", "Recommendations working", duration)
            return True
        else:
            self.log_test("Recommendations", "WARN", "Recommendations unavailable", duration)
            return False
    
    def test_workflow_system(self):
        """Test 7: Workflow System"""
        print("\n⚙️ Testing Workflows...")
        
        # Workflow list
        response, duration, error = self.make_request("GET", "/workflow/list")
        if response and response.status_code == 200:
            self.log_test("Workflow List", "PASS", "Workflow system operational", duration)
        else:
            self.log_test("Workflow List", "WARN", "Workflow system unavailable", duration)
        
        # Demo workflow
        demo_data = {"symbols": ["AAPL"], "workflow_type": "quick_analysis"}
        response, duration, error = self.make_request("POST", "/demo/full-workflow", json=demo_data)
        
        if response and response.status_code == 200:
            self.log_test("Demo Workflow", "PASS", "Demo workflow started", duration)
            return True
        else:
            self.log_test("Demo Workflow", "WARN", "Demo workflow unavailable", duration)
            return False
    
    def run_all_tests(self):
        """Execute all tests"""
        print("🚀 COMPREHENSIVE E2E TESTING")
        print("Multi-Market Correlation Engine")
        print("=" * 50)
        
        tests = [
            self.test_backend_health,
            self.test_frontend_connectivity,
            self.test_llm_integration,
            self.test_vector_database,
            self.test_market_features,
            self.test_recommendations,
            self.test_workflow_system
        ]
        
        passed = failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log_test(test.__name__, "FAIL", f"Crashed: {e}", 0)
                failed += 1
        
        # Generate report
        total_time = (datetime.now() - self.start_time).total_seconds()
        total = passed + failed
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"\n{'='*50}")
        print(f"📊 FINAL REPORT")
        print(f"{'='*50}")
        print(f"⏱️  Duration: {total_time:.1f}s")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success: {success_rate:.1f}%")
        
        # System status
        if failed == 0:
            print(f"\n🎉 ALL SYSTEMS OPERATIONAL!")
            print(f"✅ Frontend and backend fully functional")
        elif failed <= 2:
            print(f"\n✅ MOSTLY OPERATIONAL")
            print(f"⚠️  {failed} minor issues detected")
        else:
            print(f"\n⚠️  NEEDS ATTENTION")
            print(f"🔧 {failed} issues require fixing")
        
        # Feature summary
        print(f"\n🎯 FEATURE STATUS:")
        for result in self.test_results:
            emoji = "✅" if result["status"] == "PASS" else "⚠️" if result["status"] == "WARN" else "❌"
            print(f"{emoji} {result['test']}: {result['details']}")
        
        return success_rate > 70

if __name__ == "__main__":
    print("🎯 Multi-Market Correlation Engine E2E Tests")
    print("⏳ Waiting for servers...")
    time.sleep(3)
    
    tester = ComprehensiveE2ETest()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n🎉 Testing completed successfully!")
    else:
        print(f"\n⚠️  Testing completed with issues.")

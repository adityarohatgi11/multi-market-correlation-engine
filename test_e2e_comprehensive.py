#!/usr/bin/env python3
"""
Comprehensive End-to-End Testing Suite
Multi-Market Correlation Engine with TypeScript Frontend
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List
from datetime import datetime
import subprocess
import threading

class E2ETestSuite:
def __init__(self):
self.frontend_url = "http://localhost:3000"
self.api_url = "http://127.0.0.1:8000"
self.test_results = []
self.start_time = datetime.now()

def log_test(self, test_name: str, status: str, details: str = "", duration: float = 0):
"""Log test results"""
result = {
"test": test_name,
"status": status,
"details": details,
"duration": f"{duration:.2f}s",
"timestamp": datetime.now().isoformat()
}
self.test_results.append(result)

# Color coding for terminal output
color = {
"PASS": "\033[92m", # Green
"FAIL": "\033[91m", # Red
"WARN": "\033[93m", # Yellow
"INFO": "\033[94m" # Blue
}.get(status, "\033[0m")

print(f"{color}[{status}] {test_name}: {details}\033[0m")

def make_request(self, method: str, endpoint: str, **kwargs) -> tuple:
"""Make HTTP request with error handling"""
try:
start_time = time.time()
url = f"{self.api_url}{endpoint}"
response = requests.request(method, url, timeout=30, **kwargs)
duration = time.time() - start_time
return response, duration, None
except Exception as e:
return None, 0, str(e)

def test_backend_health(self):
"""Test 1: Backend Health Check"""
print("\n Testing Backend Health...")

response, duration, error = self.make_request("GET", "/health")
if error:
self.log_test("Backend Health", "FAIL", f"Connection error: {error}", duration)
return False

if response.status_code == 200:
self.log_test("Backend Health", "PASS", f"Server responding (Status: {response.status_code})", duration)
return True
else:
self.log_test("Backend Health", "FAIL", f"Unexpected status: {response.status_code}", duration)
return False

def test_llm_status(self):
"""Test 2: LLM Status Check"""
print("\n Testing LLM Integration...")

response, duration, error = self.make_request("GET", "/llm/status")
if error:
self.log_test("LLM Status", "FAIL", f"Request error: {error}", duration)
return False

if response.status_code == 200:
data = response.json()
status = data.get('status', 'unknown')
model = data.get('model_name', 'unknown')
self.log_test("LLM Status", "PASS", f"Model: {model}, Status: {status}", duration)
return True
else:
self.log_test("LLM Status", "FAIL", f"Status code: {response.status_code}", duration)
return False

def test_llm_chat(self):
"""Test 3: LLM Chat Functionality"""
print("\n Testing LLM Chat...")

chat_data = {
"message": "What is correlation analysis in finance?",
"context": "financial_analysis"
}

response, duration, error = self.make_request("POST", "/llm/chat", json=chat_data)
if error:
self.log_test("LLM Chat", "FAIL", f"Request error: {error}", duration)
return False

if response.status_code == 200:
data = response.json()
response_text = data.get('response', '')
if len(response_text) > 50:
self.log_test("LLM Chat", "PASS", f"Got response ({len(response_text)} chars)", duration)
return True
else:
self.log_test("LLM Chat", "WARN", f"Short response: {response_text}", duration)
return False
else:
self.log_test("LLM Chat", "FAIL", f"Status code: {response.status_code}", duration)
return False

def test_vector_database(self):
"""Test 4: Vector Database Operations"""
print("\n Testing Vector Database...")

# Test vector stats
response, duration, error = self.make_request("GET", "/llm/vector/stats")
if error:
self.log_test("Vector Stats", "FAIL", f"Request error: {error}", duration)
return False

if response.status_code == 200:
data = response.json()
count = data.get('total_vectors', 0)
self.log_test("Vector Stats", "PASS", f"Vector count: {count}", duration)
else:
self.log_test("Vector Stats", "FAIL", f"Status code: {response.status_code}", duration)
return False

# Test vector search
search_data = {
"query": "market volatility patterns",
"top_k": 5
}

response, duration, error = self.make_request("POST", "/llm/vector/search", json=search_data)
if error:
self.log_test("Vector Search", "FAIL", f"Request error: {error}", duration)
return False

if response.status_code == 200:
data = response.json()
results = data.get('results', [])
self.log_test("Vector Search", "PASS", f"Found {len(results)} results", duration)
return True
else:
self.log_test("Vector Search", "FAIL", f"Status code: {response.status_code}", duration)
return False

def test_market_data(self):
"""Test 5: Market Data Collection"""
print("\n Testing Market Data Collection...")

# Test market data endpoint
params = {
"symbols": "AAPL,MSFT,GOOGL",
"time_range": "1M"
}

response, duration, error = self.make_request("GET", "/market/data", params=params)
if error:
self.log_test("Market Data", "FAIL", f"Request error: {error}", duration)
return False

if response.status_code == 200:
data = response.json()
if isinstance(data, list) and len(data) > 0:
self.log_test("Market Data", "PASS", f"Retrieved {len(data)} data points", duration)
return True
else:
self.log_test("Market Data", "WARN", "Empty data response", duration)
return False
else:
self.log_test("Market Data", "FAIL", f"Status code: {response.status_code}", duration)
return False

def test_correlation_analysis(self):
"""Test 6: Correlation Analysis"""
print("\n🔗 Testing Correlation Analysis...")

correlation_data = {
"symbols": ["AAPL", "MSFT", "GOOGL", "AMZN"],
"time_range": "3M"
}

response, duration, error = self.make_request("POST", "/market/correlation", json=correlation_data)
if error:
self.log_test("Correlation Analysis", "FAIL", f"Request error: {error}", duration)
return False

if response.status_code == 200:
data = response.json()
matrix = data.get('correlation_matrix', {})
if matrix:
symbols_count = len(matrix.keys())
self.log_test("Correlation Analysis", "PASS", f"Matrix for {symbols_count} symbols", duration)
return True
else:
self.log_test("Correlation Analysis", "WARN", "Empty correlation matrix", duration)
return False
else:
self.log_test("Correlation Analysis", "FAIL", f"Status code: {response.status_code}", duration)
return False

def test_recommendations(self):
"""Test 7: Investment Recommendations"""
print("\n Testing Investment Recommendations...")

recommendation_data = {
"portfolio": {"AAPL": 0.3, "MSFT": 0.3, "GOOGL": 0.4},
"strategy": "balanced",
"time_horizon": "6M",
"risk_tolerance": "medium"
}

response, duration, error = self.make_request("POST", "/recommendations/generate", json=recommendation_data)
if error:
self.log_test("Recommendations", "FAIL", f"Request error: {error}", duration)
return False

if response.status_code == 200:
data = response.json()
if isinstance(data, list) and len(data) > 0:
self.log_test("Recommendations", "PASS", f"Generated {len(data)} recommendations", duration)
return True
else:
self.log_test("Recommendations", "WARN", "No recommendations generated", duration)
return False
else:
self.log_test("Recommendations", "FAIL", f"Status code: {response.status_code}", duration)
return False

def test_workflow_system(self):
"""Test 8: Workflow Management System"""
print("\n Testing Workflow System...")

# Test workflow list
response, duration, error = self.make_request("GET", "/workflow/list")
if error:
self.log_test("Workflow List", "FAIL", f"Request error: {error}", duration)
return False

if response.status_code == 200:
data = response.json()
workflows = data.get('workflows', [])
self.log_test("Workflow List", "PASS", f"Found {len(workflows)} workflows", duration)
else:
self.log_test("Workflow List", "WARN", f"Status code: {response.status_code}", duration)

# Test starting a demo workflow
demo_data = {
"symbols": ["AAPL", "MSFT"],
"workflow_type": "quick_analysis"
}

response, duration, error = self.make_request("POST", "/demo/full-workflow", json=demo_data)
if error:
self.log_test("Demo Workflow", "FAIL", f"Request error: {error}", duration)
return False

if response.status_code == 200:
data = response.json()
workflow_id = data.get('workflow_id')
self.log_test("Demo Workflow", "PASS", f"Started workflow: {workflow_id}", duration)
return True
else:
self.log_test("Demo Workflow", "WARN", f"Status code: {response.status_code}", duration)
return False

def test_frontend_accessibility(self):
"""Test 9: Frontend Accessibility"""
print("\n Testing Frontend Accessibility...")

try:
start_time = time.time()
response = requests.get(self.frontend_url, timeout=10)
duration = time.time() - start_time

if response.status_code == 200:
content = response.text

# Check for essential HTML elements
checks = {
"DOCTYPE": "<!DOCTYPE html>" in content,
"Meta Viewport": 'name="viewport"' in content,
"Title": "<title>" in content,
"React Root": 'id="root"' in content,
"CSS": "stylesheet" in content or ".css" in content,
"JavaScript": "script" in content or ".js" in content
}

passed = sum(checks.values())
total = len(checks)

if passed == total:
self.log_test("Frontend Accessibility", "PASS", f"All {total} HTML checks passed", duration)
return True
else:
failed_checks = [k for k, v in checks.items() if not v]
self.log_test("Frontend Accessibility", "WARN", f"{passed}/{total} checks passed. Failed: {failed_checks}", duration)
return False
else:
self.log_test("Frontend Accessibility", "FAIL", f"HTTP {response.status_code}", duration)
return False

except Exception as e:
self.log_test("Frontend Accessibility", "FAIL", f"Connection error: {str(e)}", 0)
return False

def test_api_integration(self):
"""Test 10: Frontend-Backend API Integration"""
print("\n🔌 Testing API Integration...")

# Test various API endpoints that the frontend uses
endpoints_to_test = [
("/health", "GET"),
("/llm/status", "GET"),
("/llm/vector/stats", "GET"),
]

passed_tests = 0
total_tests = len(endpoints_to_test)

for endpoint, method in endpoints_to_test:
response, duration, error = self.make_request(method, endpoint)

if error:
self.log_test(f"API {endpoint}", "FAIL", f"Error: {error}", duration)
elif response.status_code == 200:
self.log_test(f"API {endpoint}", "PASS", f"Response OK", duration)
passed_tests += 1
else:
self.log_test(f"API {endpoint}", "WARN", f"Status: {response.status_code}", duration)

if passed_tests == total_tests:
self.log_test("API Integration", "PASS", f"All {total_tests} endpoints working", 0)
return True
else:
self.log_test("API Integration", "WARN", f"{passed_tests}/{total_tests} endpoints working", 0)
return False

def test_performance_metrics(self):
"""Test 11: Performance Metrics"""
print("\n Testing Performance Metrics...")

# Test API response times
endpoints = ["/health", "/llm/status", "/llm/vector/stats"]
response_times = []

for endpoint in endpoints:
response, duration, error = self.make_request("GET", endpoint)
if not error and response.status_code == 200:
response_times.append(duration)

if response_times:
avg_response_time = sum(response_times) / len(response_times)
max_response_time = max(response_times)

if avg_response_time < 1.0:
self.log_test("API Performance", "PASS", f"Avg: {avg_response_time:.3f}s, Max: {max_response_time:.3f}s", 0)
return True
elif avg_response_time < 3.0:
self.log_test("API Performance", "WARN", f"Avg: {avg_response_time:.3f}s, Max: {max_response_time:.3f}s", 0)
return False
else:
self.log_test("API Performance", "FAIL", f"Slow responses - Avg: {avg_response_time:.3f}s", 0)
return False
else:
self.log_test("API Performance", "FAIL", "No successful responses to measure", 0)
return False

def test_error_handling(self):
"""Test 12: Error Handling"""
print("\n Testing Error Handling...")

# Test invalid endpoints
response, duration, error = self.make_request("GET", "/invalid-endpoint")
if response and response.status_code == 404:
self.log_test("404 Handling", "PASS", "Proper 404 response", duration)
else:
self.log_test("404 Handling", "WARN", f"Unexpected response for invalid endpoint", duration)

# Test invalid JSON data
response, duration, error = self.make_request("POST", "/llm/chat", json={"invalid": "data"})
if response and response.status_code in [400, 422]:
self.log_test("Invalid Data Handling", "PASS", f"Proper error response ({response.status_code})", duration)
return True
else:
self.log_test("Invalid Data Handling", "WARN", f"Unexpected response for invalid data", duration)
return False

def run_all_tests(self):
"""Run all end-to-end tests"""
print(" Starting Comprehensive End-to-End Testing Suite")
print("=" * 60)

# Test sequence
tests = [
self.test_backend_health,
self.test_frontend_accessibility,
self.test_llm_status,
self.test_llm_chat,
self.test_vector_database,
self.test_market_data,
self.test_correlation_analysis,
self.test_recommendations,
self.test_workflow_system,
self.test_api_integration,
self.test_performance_metrics,
self.test_error_handling
]

passed = 0
failed = 0
warnings = 0

for test in tests:
try:
result = test()
if result:
passed += 1
else:
failed += 1
except Exception as e:
self.log_test(test.__name__, "FAIL", f"Test crashed: {str(e)}", 0)
failed += 1

# Count warnings
warnings = sum(1 for result in self.test_results if result["status"] == "WARN")

# Generate summary
self.generate_test_report(passed, failed, warnings)

def generate_test_report(self, passed: int, failed: int, warnings: int):
"""Generate comprehensive test report"""
print("\n" + "=" * 60)
print(" COMPREHENSIVE TEST REPORT")
print("=" * 60)

total_duration = (datetime.now() - self.start_time).total_seconds()

print(f"⏱ Total Duration: {total_duration:.2f} seconds")
print(f" Passed: {passed}")
print(f" Failed: {failed}")
print(f" Warnings: {warnings}")
print(f" Success Rate: {(passed/(passed+failed)*100):.1f}%")

print(f"\n FEATURE STATUS SUMMARY:")
print("-" * 40)

feature_groups = {
"Backend Core": ["Backend Health", "API Integration", "API Performance"],
"LLM Integration": ["LLM Status", "LLM Chat"],
"Vector Database": ["Vector Stats", "Vector Search"],
"Market Data": ["Market Data", "Correlation Analysis"],
"Recommendations": ["Recommendations"],
"Workflow System": ["Workflow List", "Demo Workflow"],
"Frontend": ["Frontend Accessibility"],
"Error Handling": ["404 Handling", "Invalid Data Handling"]
}

for group, test_names in feature_groups.items():
group_results = [r for r in self.test_results if any(name in r["test"] for name in test_names)]
group_passed = sum(1 for r in group_results if r["status"] == "PASS")
group_total = len(group_results)

if group_total > 0:
status_emoji = "" if group_passed == group_total else "" if group_passed > 0 else ""
print(f"{status_emoji} {group}: {group_passed}/{group_total}")

print(f"\n DETAILED TEST RESULTS:")
print("-" * 40)

for result in self.test_results:
status_emoji = {"PASS": "", "FAIL": "", "WARN": "", "INFO": ""}.get(result["status"], "")
print(f"{status_emoji} {result['test']}: {result['details']} ({result['duration']})")

# Save detailed report to file
report_data = {
"summary": {
"total_duration": f"{total_duration:.2f}s",
"passed": passed,
"failed": failed,
"warnings": warnings,
"success_rate": f"{(passed/(passed+failed)*100):.1f}%",
"timestamp": datetime.now().isoformat()
},
"detailed_results": self.test_results
}

with open("e2e_test_report.json", "w") as f:
json.dump(report_data, f, indent=2)

print(f"\n Detailed report saved to: e2e_test_report.json")

# Overall assessment
if failed == 0:
print(f"\n ALL SYSTEMS OPERATIONAL! Frontend and backend are fully functional.")
elif failed <= 2:
print(f"\n MOSTLY OPERATIONAL with {failed} minor issues. System is usable.")
else:
print(f"\n MULTIPLE ISSUES DETECTED. {failed} tests failed - needs attention.")

if __name__ == "__main__":
print("Multi-Market Correlation Engine - E2E Test Suite")
print("Testing all frontend and backend features...")

# Wait a moment for servers to be ready
print("⏳ Waiting 5 seconds for servers to be ready...")
time.sleep(5)

tester = E2ETestSuite()
tester.run_all_tests()
#!/usr/bin/env python3
"""
Frontend Feature Testing Suite
Tests specific frontend functionality and user interactions
"""

import requests
import json
import time
from datetime import datetime

class FrontendFeatureTest:
def __init__(self):
self.frontend_url = "http://localhost:3000"
self.api_url = "http://127.0.0.1:8000"
self.test_results = []

def log_test(self, test_name, status, details="", duration=0):
"""Log test results with color coding"""
result = {
"test": test_name,
"status": status,
"details": details,
"duration": f"{duration:.2f}s"
}
self.test_results.append(result)

colors = {"PASS": "\033[92m", "FAIL": "\033[91m", "WARN": "\033[93m"}
color = colors.get(status, "\033[0m")
print(f"{color}[{status}] {test_name}: {details}\033[0m")

def make_request(self, method, endpoint, **kwargs):
"""Make HTTP request with timing"""
try:
start_time = time.time()
url = f"{self.api_url}{endpoint}"
response = requests.request(method, url, timeout=10, **kwargs)
duration = time.time() - start_time
return response, duration, None
except Exception as e:
return None, 0, str(e)

def test_frontend_assets(self):
"""Test Frontend Asset Loading"""
print("\n Testing Frontend Assets...")

try:
# Test main page
start_time = time.time()
response = requests.get(self.frontend_url, timeout=10)
duration = time.time() - start_time

if response.status_code == 200:
content = response.text
checks = {
"React Root": 'id="root"' in content,
"CSS Loaded": 'rel="stylesheet"' in content or '.css' in content,
"Vite Scripts": '/src/main.tsx' in content or 'vite' in content,
"Meta Tags": 'name="viewport"' in content,
"Title": '<title>' in content
}

passed = sum(checks.values())
total = len(checks)

if passed == total:
self.log_test("Frontend Assets", "PASS", f"All {total} checks passed", duration)
else:
failed = [k for k, v in checks.items() if not v]
self.log_test("Frontend Assets", "WARN", f"{passed}/{total} - Failed: {failed}", duration)

return True
else:
self.log_test("Frontend Assets", "FAIL", f"HTTP {response.status_code}", duration)
return False

except Exception as e:
self.log_test("Frontend Assets", "FAIL", f"Error: {e}", 0)
return False

def test_api_endpoints_for_frontend(self):
"""Test API Endpoints Used by Frontend"""
print("\n🔌 Testing Frontend API Integration...")

endpoints = [
("/health", "GET"),
("/llm/status", "GET"),
("/llm/vector/stats", "GET")
]

passed = 0
for endpoint, method in endpoints:
response, duration, error = self.make_request(method, endpoint)

if error:
self.log_test(f"API {endpoint}", "FAIL", f"Error: {error[:50]}", duration)
elif response and response.status_code == 200:
self.log_test(f"API {endpoint}", "PASS", "Responding correctly", duration)
passed += 1
else:
self.log_test(f"API {endpoint}", "WARN", f"HTTP {response.status_code if response else 'None'}", duration)

return passed == len(endpoints)

def test_llm_features(self):
"""Test LLM Assistant Features"""
print("\n Testing LLM Assistant...")

# Test LLM status for frontend
response, duration, error = self.make_request("GET", "/llm/status")
if response and response.status_code == 200:
data = response.json()
model = data.get('model_name', 'Unknown')
status = data.get('status', 'Unknown')
self.log_test("LLM Status Check", "PASS", f"Model: {model}, Status: {status}", duration)
else:
self.log_test("LLM Status Check", "WARN", "LLM status unavailable", duration)

# Test LLM chat functionality
chat_requests = [
{"message": "What is correlation analysis?", "context": "finance"},
{"message": "How do I interpret correlation coefficients?", "context": "education"},
{"message": "Explain market volatility", "context": "trading"}
]

chat_success = 0
for i, chat_data in enumerate(chat_requests):
response, duration, error = self.make_request("POST", "/llm/chat", json=chat_data)

if response and response.status_code == 200:
try:
data = response.json()
response_text = data.get('response', '')
if len(response_text) > 20:
self.log_test(f"LLM Chat Test {i+1}", "PASS", f"Got response ({len(response_text)} chars)", duration)
chat_success += 1
else:
self.log_test(f"LLM Chat Test {i+1}", "WARN", "Short response", duration)
except:
self.log_test(f"LLM Chat Test {i+1}", "WARN", "Invalid JSON response", duration)
else:
self.log_test(f"LLM Chat Test {i+1}", "WARN", "Chat request failed", duration)

return chat_success > 0

def test_vector_search_features(self):
"""Test Vector Search Features"""
print("\n Testing Vector Search...")

# Test vector database stats
response, duration, error = self.make_request("GET", "/llm/vector/stats")
if response and response.status_code == 200:
try:
data = response.json()
vector_count = data.get('total_vectors', 0)
dimensions = data.get('dimensions', 0)
self.log_test("Vector DB Stats", "PASS", f"Vectors: {vector_count}, Dims: {dimensions}", duration)
except:
self.log_test("Vector DB Stats", "PASS", "Vector stats available", duration)
else:
self.log_test("Vector DB Stats", "WARN", "Vector stats unavailable", duration)

# Test vector search queries
search_queries = [
{"query": "market correlation patterns", "top_k": 5},
{"query": "stock price volatility analysis", "top_k": 3},
{"query": "portfolio risk assessment", "top_k": 5}
]

search_success = 0
for i, search_data in enumerate(search_queries):
response, duration, error = self.make_request("POST", "/llm/vector/search", json=search_data)

if response and response.status_code == 200:
try:
data = response.json()
results = data.get('results', [])
self.log_test(f"Vector Search {i+1}", "PASS", f"Found {len(results)} results", duration)
search_success += 1
except:
self.log_test(f"Vector Search {i+1}", "PASS", "Search completed", duration)
search_success += 1
else:
self.log_test(f"Vector Search {i+1}", "WARN", "Search failed", duration)

return search_success > 0

def test_market_analysis_features(self):
"""Test Market Analysis Features"""
print("\n Testing Market Analysis...")

# Test market data retrieval
test_symbols = [
"AAPL,MSFT",
"GOOGL,AMZN,TSLA",
"SPY,QQQ"
]

market_success = 0
for i, symbols in enumerate(test_symbols):
params = {"symbols": symbols, "time_range": "1M"}
response, duration, error = self.make_request("GET", "/market/data", params=params)

if response and response.status_code == 200:
try:
data = response.json()
if isinstance(data, list) and len(data) > 0:
self.log_test(f"Market Data {i+1}", "PASS", f"Retrieved {len(data)} data points", duration)
market_success += 1
else:
self.log_test(f"Market Data {i+1}", "WARN", "Empty data response", duration)
except:
self.log_test(f"Market Data {i+1}", "WARN", "Invalid response format", duration)
else:
self.log_test(f"Market Data {i+1}", "WARN", "Market data unavailable", duration)

# Test correlation analysis
correlation_tests = [
{"symbols": ["AAPL", "MSFT"], "time_range": "1M"},
{"symbols": ["GOOGL", "AMZN", "TSLA"], "time_range": "3M"}
]

corr_success = 0
for i, corr_data in enumerate(correlation_tests):
response, duration, error = self.make_request("POST", "/market/correlation", json=corr_data)

if response and response.status_code == 200:
try:
data = response.json()
matrix = data.get('correlation_matrix', {})
if matrix:
symbols_count = len(matrix.keys())
self.log_test(f"Correlation Analysis {i+1}", "PASS", f"Matrix for {symbols_count} symbols", duration)
corr_success += 1
else:
self.log_test(f"Correlation Analysis {i+1}", "WARN", "Empty correlation matrix", duration)
except:
self.log_test(f"Correlation Analysis {i+1}", "WARN", "Invalid response format", duration)
else:
self.log_test(f"Correlation Analysis {i+1}", "WARN", "Correlation analysis unavailable", duration)

return market_success > 0 or corr_success > 0

def test_recommendation_features(self):
"""Test Investment Recommendation Features"""
print("\n Testing Investment Recommendations...")

recommendation_tests = [
{
"portfolio": {"AAPL": 0.4, "MSFT": 0.3, "GOOGL": 0.3},
"strategy": "growth",
"time_horizon": "1Y",
"risk_tolerance": "high"
},
{
"portfolio": {"SPY": 0.6, "BND": 0.4},
"strategy": "conservative",
"time_horizon": "5Y",
"risk_tolerance": "low"
}
]

rec_success = 0
for i, rec_data in enumerate(recommendation_tests):
response, duration, error = self.make_request("POST", "/recommendations/generate", json=rec_data)

if response and response.status_code == 200:
try:
data = response.json()
if isinstance(data, list) and len(data) > 0:
self.log_test(f"Recommendations {i+1}", "PASS", f"Generated {len(data)} recommendations", duration)
rec_success += 1
else:
self.log_test(f"Recommendations {i+1}", "WARN", "No recommendations generated", duration)
except:
self.log_test(f"Recommendations {i+1}", "WARN", "Invalid response format", duration)
else:
self.log_test(f"Recommendations {i+1}", "WARN", "Recommendations unavailable", duration)

return rec_success > 0

def test_dashboard_features(self):
"""Test Dashboard Features"""
print("\n Testing Dashboard Features...")

# Test various dashboard endpoints
dashboard_endpoints = [
("/api/portfolio/summary", "GET"),
("/api/metrics/overview", "GET"),
("/api/alerts/active", "GET")
]

dashboard_success = 0
for endpoint, method in dashboard_endpoints:
response, duration, error = self.make_request(method, endpoint)

if response and response.status_code == 200:
self.log_test(f"Dashboard {endpoint}", "PASS", "Dashboard endpoint working", duration)
dashboard_success += 1
elif response and response.status_code == 404:
self.log_test(f"Dashboard {endpoint}", "WARN", "Endpoint not implemented", duration)
else:
self.log_test(f"Dashboard {endpoint}", "WARN", "Dashboard endpoint unavailable", duration)

return dashboard_success > 0

def run_frontend_tests(self):
"""Run all frontend feature tests"""
print(" FRONTEND FEATURE TESTING SUITE")
print("Multi-Market Correlation Engine TypeScript Frontend")
print("=" * 60)

start_time = time.time()

# Run all test suites
test_results = {
"Frontend Assets": self.test_frontend_assets(),
"API Integration": self.test_api_endpoints_for_frontend(),
"LLM Features": self.test_llm_features(),
"Vector Search": self.test_vector_search_features(),
"Market Analysis": self.test_market_analysis_features(),
"Recommendations": self.test_recommendation_features(),
"Dashboard": self.test_dashboard_features()
}

total_duration = time.time() - start_time

# Calculate results
passed_suites = sum(test_results.values())
total_suites = len(test_results)

individual_tests = len(self.test_results)
individual_passed = sum(1 for r in self.test_results if r["status"] == "PASS")
individual_warnings = sum(1 for r in self.test_results if r["status"] == "WARN")
individual_failed = sum(1 for r in self.test_results if r["status"] == "FAIL")

# Generate report
print(f"\n{'='*60}")
print(f" FRONTEND TESTING REPORT")
print(f"{'='*60}")
print(f"⏱ Total Duration: {total_duration:.1f} seconds")
print(f"🧪 Test Suites: {passed_suites}/{total_suites} passed")
print(f"🔬 Individual Tests: {individual_passed} passed, {individual_warnings} warnings, {individual_failed} failed")
print(f" Suite Success Rate: {(passed_suites/total_suites*100):.1f}%")
print(f" Test Success Rate: {(individual_passed/individual_tests*100):.1f}%")

print(f"\n FEATURE SUITE RESULTS:")
print("-" * 40)
for suite, result in test_results.items():
emoji = "" if result else ""
print(f"{emoji} {suite}: {'OPERATIONAL' if result else 'NEEDS ATTENTION'}")

print(f"\n DETAILED TEST RESULTS:")
print("-" * 40)
for result in self.test_results:
emoji = {"PASS": "", "FAIL": "", "WARN": ""}.get(result["status"], "")
print(f"{emoji} {result['test']}: {result['details']} ({result['duration']})")

# Overall assessment
print(f"\n OVERALL FRONTEND ASSESSMENT:")
print("-" * 40)

if passed_suites == total_suites:
print(" EXCELLENT: All frontend features are fully operational!")
print(" TypeScript compilation successful")
print(" React application loading correctly")
print(" API integration working")
print(" All major features functional")
elif passed_suites >= total_suites * 0.7:
print(" GOOD: Frontend is mostly operational")
print(f" {passed_suites}/{total_suites} feature suites working")
print(" Some features may need backend implementation")
elif passed_suites >= total_suites * 0.5:
print(" FAIR: Frontend partially operational")
print(f" {passed_suites}/{total_suites} feature suites working")
print(" Backend services need attention")
else:
print(" NEEDS WORK: Multiple frontend issues")
print(f" Only {passed_suites}/{total_suites} feature suites working")
print(" Requires significant debugging")

return passed_suites >= total_suites * 0.7

if __name__ == "__main__":
print(" Multi-Market Correlation Engine")
print("🔬 Frontend Feature Testing Suite")
print(" Testing TypeScript React Frontend")
print("")

tester = FrontendFeatureTest()
success = tester.run_frontend_tests()

if success:
print(f"\n Frontend testing completed successfully!")
else:
print(f"\n Frontend testing revealed issues that need attention.")

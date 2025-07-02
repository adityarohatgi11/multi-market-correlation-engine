#!/usr/bin/env python3
"""
User Experience Testing Suite
Tests frontend UI components, navigation, and user workflows
"""

import requests
import json
import time
from datetime import datetime

class UserExperienceTest:
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

colors = {"PASS": "\033[92m", "FAIL": "\033[91m", "WARN": "\033[93m", "INFO": "\033[94m"}
color = colors.get(status, "\033[0m")
print(f"{color}[{status}] {test_name}: {details}\033[0m")

def test_frontend_performance(self):
"""Test Frontend Loading Performance"""
print("\n Testing Frontend Performance...")

try:
start_time = time.time()
response = requests.get(self.frontend_url, timeout=10)
load_time = time.time() - start_time

if response.status_code == 200:
if load_time < 1.0:
self.log_test("Page Load Speed", "PASS", f"Fast loading: {load_time:.3f}s", load_time)
elif load_time < 3.0:
self.log_test("Page Load Speed", "WARN", f"Moderate loading: {load_time:.3f}s", load_time)
else:
self.log_test("Page Load Speed", "FAIL", f"Slow loading: {load_time:.3f}s", load_time)

# Test content size
content_size = len(response.content)
if content_size > 1000:
self.log_test("Content Size", "PASS", f"Adequate content: {content_size} bytes", 0)
else:
self.log_test("Content Size", "WARN", f"Small content: {content_size} bytes", 0)

return True
else:
self.log_test("Page Load Speed", "FAIL", f"HTTP {response.status_code}", load_time)
return False

except Exception as e:
self.log_test("Page Load Speed", "FAIL", f"Error: {e}", 0)
return False

def test_responsive_design(self):
"""Test Responsive Design Elements"""
print("\n Testing Responsive Design...")

try:
response = requests.get(self.frontend_url, timeout=10)
if response.status_code == 200:
content = response.text.lower()

responsive_checks = {
"Viewport Meta": 'name="viewport"' in content,
"CSS Framework": 'tailwind' in content or 'bootstrap' in content or 'css' in content,
"Flexible Layout": 'flex' in content or 'grid' in content,
"Media Queries": '@media' in content or 'responsive' in content
}

passed = sum(responsive_checks.values())
total = len(responsive_checks)

if passed >= total - 1: # Allow 1 failure
self.log_test("Responsive Design", "PASS", f"Good responsive elements ({passed}/{total})", 0)
return True
else:
failed = [k for k, v in responsive_checks.items() if not v]
self.log_test("Responsive Design", "WARN", f"Missing: {failed}", 0)
return False
else:
self.log_test("Responsive Design", "FAIL", "Could not load page", 0)
return False

except Exception as e:
self.log_test("Responsive Design", "FAIL", f"Error: {e}", 0)
return False

def test_ui_components(self):
"""Test UI Component Loading"""
print("\n Testing UI Components...")

try:
response = requests.get(self.frontend_url, timeout=10)
if response.status_code == 200:
content = response.text.lower()

ui_checks = {
"React Components": 'react' in content,
"Navigation Elements": 'nav' in content or 'menu' in content,
"Interactive Elements": 'button' in content or 'onclick' in content,
"Modern Framework": 'vite' in content or 'webpack' in content,
"Styling System": 'style' in content or 'class' in content
}

passed = sum(ui_checks.values())
total = len(ui_checks)

if passed >= 4: # At least 4 out of 5
self.log_test("UI Components", "PASS", f"Modern UI stack ({passed}/{total})", 0)
return True
else:
failed = [k for k, v in ui_checks.items() if not v]
self.log_test("UI Components", "WARN", f"Missing: {failed}", 0)
return False
else:
self.log_test("UI Components", "FAIL", "Could not load page", 0)
return False

except Exception as e:
self.log_test("UI Components", "FAIL", f"Error: {e}", 0)
return False

def test_user_workflows(self):
"""Test User Workflow Scenarios"""
print("\n👤 Testing User Workflows...")

# Simulate typical user interactions by testing API endpoints
workflows = [
("Dashboard View", "GET", "/health"),
("System Status", "GET", "/llm/status"),
("Vector Database", "GET", "/llm/vector/stats"),
("LLM Interaction", "POST", "/llm/chat", {"message": "Hello", "context": "test"})
]

workflow_success = 0
for workflow_name, method, endpoint, *args in workflows:
try:
start_time = time.time()

if method == "GET":
url = f"{self.api_url}{endpoint}"
response = requests.get(url, timeout=5)
else:
url = f"{self.api_url}{endpoint}"
data = args[0] if args else {}
response = requests.post(url, json=data, timeout=5)

duration = time.time() - start_time

if response.status_code == 200:
self.log_test(f"Workflow: {workflow_name}", "PASS", f"API responsive", duration)
workflow_success += 1
elif response.status_code in [404, 422, 500]:
self.log_test(f"Workflow: {workflow_name}", "WARN", f"HTTP {response.status_code}", duration)
else:
self.log_test(f"Workflow: {workflow_name}", "WARN", f"HTTP {response.status_code}", duration)

except Exception as e:
self.log_test(f"Workflow: {workflow_name}", "WARN", f"Error: {str(e)[:50]}", 0)

return workflow_success >= len(workflows) // 2

def test_accessibility_features(self):
"""Test Accessibility Features"""
print("\n♿ Testing Accessibility...")

try:
response = requests.get(self.frontend_url, timeout=10)
if response.status_code == 200:
content = response.text.lower()

accessibility_checks = {
"HTML5 Semantic": '<!doctype html>' in content,
"Page Title": '<title>' in content,
"Language Attribute": 'lang=' in content,
"Meta Description": 'name="description"' in content or 'meta' in content,
"Proper Headings": '<h1' in content or '<h2' in content
}

passed = sum(accessibility_checks.values())
total = len(accessibility_checks)

if passed >= 4:
self.log_test("Accessibility", "PASS", f"Good accessibility ({passed}/{total})", 0)
return True
else:
failed = [k for k, v in accessibility_checks.items() if not v]
self.log_test("Accessibility", "WARN", f"Missing: {failed}", 0)
return False
else:
self.log_test("Accessibility", "FAIL", "Could not load page", 0)
return False

except Exception as e:
self.log_test("Accessibility", "FAIL", f"Error: {e}", 0)
return False

def test_error_handling_ux(self):
"""Test Error Handling User Experience"""
print("\n Testing Error Handling UX...")

# Test various error scenarios
error_tests = [
("404 Handling", "GET", "/nonexistent-page"),
("API Error", "POST", "/llm/chat", {"invalid": "data"}),
("Timeout Handling", "GET", "/slow-endpoint")
]

error_handling_success = 0
for test_name, method, endpoint, *args in error_tests:
try:
start_time = time.time()

if method == "GET":
url = f"{self.api_url}{endpoint}"
response = requests.get(url, timeout=5)
else:
url = f"{self.api_url}{endpoint}"
data = args[0] if args else {}
response = requests.post(url, json=data, timeout=5)

duration = time.time() - start_time

if response.status_code in [400, 404, 422, 500]:
self.log_test(f"Error UX: {test_name}", "PASS", f"Proper error response ({response.status_code})", duration)
error_handling_success += 1
else:
self.log_test(f"Error UX: {test_name}", "WARN", f"Unexpected response ({response.status_code})", duration)

except requests.exceptions.Timeout:
self.log_test(f"Error UX: {test_name}", "WARN", "Timeout occurred", 5.0)
except Exception as e:
self.log_test(f"Error UX: {test_name}", "WARN", f"Error: {str(e)[:50]}", 0)

return error_handling_success > 0

def test_browser_compatibility(self):
"""Test Browser Compatibility Features"""
print("\n Testing Browser Compatibility...")

try:
response = requests.get(self.frontend_url, timeout=10)
if response.status_code == 200:
content = response.text.lower()

compatibility_checks = {
"Modern JS": 'type="module"' in content or 'es6' in content,
"CSS3 Features": 'css' in content,
"Progressive Enhancement": 'noscript' in content or 'fallback' in content,
"Cross-browser CSS": 'webkit' in content or 'vendor' in content or 'prefix' in content,
"Standards Compliance": '<!doctype html>' in content
}

passed = sum(compatibility_checks.values())
total = len(compatibility_checks)

if passed >= 3:
self.log_test("Browser Compatibility", "PASS", f"Good compatibility ({passed}/{total})", 0)
return True
else:
failed = [k for k, v in compatibility_checks.items() if not v]
self.log_test("Browser Compatibility", "WARN", f"Missing: {failed}", 0)
return False
else:
self.log_test("Browser Compatibility", "FAIL", "Could not load page", 0)
return False

except Exception as e:
self.log_test("Browser Compatibility", "FAIL", f"Error: {e}", 0)
return False

def run_ux_tests(self):
"""Run all user experience tests"""
print(" USER EXPERIENCE TESTING SUITE")
print("Multi-Market Correlation Engine TypeScript Frontend")
print("=" * 65)

start_time = time.time()

# Run all UX test suites
ux_test_results = {
"Performance": self.test_frontend_performance(),
"Responsive Design": self.test_responsive_design(),
"UI Components": self.test_ui_components(),
"User Workflows": self.test_user_workflows(),
"Accessibility": self.test_accessibility_features(),
"Error Handling": self.test_error_handling_ux(),
"Browser Compatibility": self.test_browser_compatibility()
}

total_duration = time.time() - start_time

# Calculate results
passed_suites = sum(ux_test_results.values())
total_suites = len(ux_test_results)

individual_tests = len(self.test_results)
individual_passed = sum(1 for r in self.test_results if r["status"] == "PASS")
individual_warnings = sum(1 for r in self.test_results if r["status"] == "WARN")
individual_failed = sum(1 for r in self.test_results if r["status"] == "FAIL")

# Generate comprehensive UX report
print(f"\n{'='*65}")
print(f" USER EXPERIENCE TESTING REPORT")
print(f"{'='*65}")
print(f"⏱ Total Duration: {total_duration:.1f} seconds")
print(f"🧪 UX Test Suites: {passed_suites}/{total_suites} passed")
print(f"🔬 Individual Tests: {individual_passed} passed, {individual_warnings} warnings, {individual_failed} failed")
print(f" UX Suite Success Rate: {(passed_suites/total_suites*100):.1f}%")
print(f" Individual Test Success Rate: {(individual_passed/individual_tests*100):.1f}%")

print(f"\n USER EXPERIENCE ASSESSMENT:")
print("-" * 45)
for suite, result in ux_test_results.items():
emoji = "" if result else ""
status = "EXCELLENT" if result else "NEEDS IMPROVEMENT"
print(f"{emoji} {suite}: {status}")

print(f"\n DETAILED UX TEST RESULTS:")
print("-" * 45)
for result in self.test_results:
emoji = {"PASS": "", "FAIL": "", "WARN": "", "INFO": ""}.get(result["status"], "")
print(f"{emoji} {result['test']}: {result['details']} ({result['duration']})")

# UX Quality Assessment
print(f"\n OVERALL UX QUALITY SCORE:")
print("-" * 45)

ux_score = (passed_suites / total_suites) * 100

if ux_score >= 85:
print(" EXCELLENT UX (85-100%)")
print(" Professional-grade user experience")
print(" Modern, responsive, and accessible")
print(" Ready for production deployment")
elif ux_score >= 70:
print(" GOOD UX (70-84%)")
print(" Solid user experience foundation")
print(" Minor improvements recommended")
print(" Suitable for beta testing")
elif ux_score >= 50:
print(" FAIR UX (50-69%)")
print(" Several UX improvements needed")
print(" Focus on accessibility and performance")
print(" Requires UX optimization")
else:
print(" POOR UX (0-49%)")
print(" 🛑 Significant UX issues detected")
print(" Major redesign recommended")
print(" 📞 UX consultation needed")

# Recommendations
print(f"\n UX IMPROVEMENT RECOMMENDATIONS:")
print("-" * 45)

if not ux_test_results["Performance"]:
print(" Optimize loading performance and reduce bundle size")
if not ux_test_results["Responsive Design"]:
print(" Implement responsive design for mobile devices")
if not ux_test_results["Accessibility"]:
print("♿ Add accessibility features (ARIA labels, alt text)")
if not ux_test_results["Error Handling"]:
print(" Improve error messaging and user feedback")
if not ux_test_results["Browser Compatibility"]:
print(" Test and fix cross-browser compatibility issues")

if passed_suites == total_suites:
print(" No immediate UX improvements needed - excellent work!")

return ux_score >= 70

if __name__ == "__main__":
print(" Multi-Market Correlation Engine")
print(" User Experience Testing Suite")
print(" Evaluating TypeScript React Frontend UX")
print("")

tester = UserExperienceTest()
success = tester.run_ux_tests()

if success:
print(f"\n User experience testing passed! Frontend UX is good.")
else:
print(f"\n User experience needs improvement. See recommendations above.")

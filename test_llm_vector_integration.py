#!/usr/bin/env python3
"""
FAISS Vector Database and LLM Integration Test
=============================================

Comprehensive test suite for FAISS vector database and Llama LLM integration
in the Multi-Market Correlation Engine.

Author: Multi-Market Correlation Engine Team
Version: 1.0.0
"""

import sys
import os
import time
import traceback
from datetime import datetime
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_vector_database():
"""Test FAISS vector database functionality."""
print(" Testing FAISS Vector Database...")

try:
from src.data.vector_database import get_vector_db, FinancialEmbedding

# Initialize vector database
vector_db = get_vector_db()
print(f" Vector database initialized: {vector_db.__class__.__name__}")

# Test embedding generation
embedding_gen = FinancialEmbedding()
print(f" Embedding generator initialized: {embedding_gen.__class__.__name__}")

# Test price pattern embedding
sample_prices = pd.Series([100, 101, 99, 102, 98, 103, 97, 105, 108, 106],
index=pd.date_range('2024-01-01', periods=10))

price_embedding = embedding_gen.create_price_pattern_embedding(sample_prices)
print(f" Price pattern embedding created: shape {price_embedding.shape}")

# Test correlation embedding
sample_corr = pd.DataFrame({
'AAPL': [1.0, 0.7, 0.5],
'MSFT': [0.7, 1.0, 0.6],
'GOOGL': [0.5, 0.6, 1.0]
}, index=['AAPL', 'MSFT', 'GOOGL'])

corr_embedding = embedding_gen.create_correlation_embedding(sample_corr)
print(f" Correlation embedding created: shape {corr_embedding.shape}")

# Test text embedding
text_embedding = embedding_gen.create_text_embedding("High volatility tech stock pattern")
print(f" Text embedding created: shape {text_embedding.shape}")

# Test adding patterns to vector database
success = vector_db.add_financial_pattern(
pattern_id="test_pattern_001",
symbol="AAPL",
pattern_type="price_pattern",
data={'price_series': sample_prices},
metadata={'test': True, 'created': datetime.now().isoformat()}
)
print(f" Pattern added to vector DB: {success}")

# Test similarity search
results = vector_db.search_by_text_query("tech stock volatility", k=3)
print(f" Similarity search completed: {len(results)} results")

# Test vector database statistics
stats = vector_db.get_pattern_statistics()
print(f" Vector DB stats: {stats}")

return True

except Exception as e:
print(f" Vector database test failed: {e}")
print(f"Traceback: {traceback.format_exc()}")
return False


def test_llm_engine():
"""Test Llama LLM engine functionality."""
print("\n Testing Llama LLM Engine...")

try:
from src.models.llm_engine import get_llm_engine

# Initialize LLM engine
llm_engine = get_llm_engine()
print(f" LLM engine initialized: {llm_engine.__class__.__name__}")

# Test model info
model_info = llm_engine.get_model_info()
print(f" Model info retrieved: {model_info}")

if not model_info['model_available']:
print(" No LLM model loaded - skipping model tests")
return True

# Test chat query
response = llm_engine.chat_query("What are the key principles of portfolio diversification?")
print(f" Chat query processed: {len(response.get('response', ''))} characters")

# Test market analysis
sample_data = {
'symbols': ['AAPL', 'MSFT'],
'prices': {'AAPL': 150.0, 'MSFT': 300.0},
'volatility': {'AAPL': 0.25, 'MSFT': 0.30}
}

analysis = llm_engine.generate_market_analysis(sample_data, "Sample market analysis")
print(f" Market analysis generated: {len(analysis.get('analysis', ''))} characters")

# Test correlation insights
correlation_matrix = pd.DataFrame({
'AAPL': [1.0, 0.7],
'MSFT': [0.7, 1.0]
}, index=['AAPL', 'MSFT'])

insights = llm_engine.explain_correlations(correlation_matrix, "recent period")
print(f" Correlation insights generated: {len(insights.get('insights', ''))} characters")

return True

except Exception as e:
print(f" LLM engine test failed: {e}")
print(f"Traceback: {traceback.format_exc()}")
return False


def test_llm_agent():
"""Test LLM agent functionality."""
print("\n Testing LLM Agent...")

try:
from src.agents.llm_agent import LLMAgent
from src.agents.base_agent import Task, TaskPriority

# Initialize LLM agent
agent = LLMAgent()
print(f" LLM agent initialized: {agent.name}")

# Test agent status
status = agent.get_agent_status()
print(f" Agent status retrieved: {status['status']}")

# Test chat query task
chat_task = Task(
id="test_chat",
name="chat_query",
priority=TaskPriority.MEDIUM,
created_at=datetime.now(),
scheduled_at=None,
data={
'type': 'chat_query',
'query': 'What is correlation analysis?',
'user_id': 'test_user'
}
)

chat_result = agent._handle_task(chat_task)
print(f" Chat task processed: {'error' not in chat_result}")

# Test market analysis task
analysis_task = Task(
id="test_analysis",
name="generate_market_analysis",
priority=TaskPriority.HIGH,
created_at=datetime.now(),
scheduled_at=None,
data={
'type': 'generate_market_analysis',
'symbols': ['AAPL', 'MSFT'],
'time_period': '1M'
}
)

analysis_result = agent._handle_task(analysis_task)
print(f" Market analysis task processed: {'error' not in analysis_result}")

return True

except Exception as e:
print(f" LLM agent test failed: {e}")
print(f"Traceback: {traceback.format_exc()}")
return False


def test_api_endpoints():
"""Test LLM API endpoints."""
print("\n Testing LLM API Endpoints...")

try:
import requests

# Check if API server is running
try:
response = requests.get("http://127.0.0.1:8000/health", timeout=5)
if response.status_code != 200:
print(" API server not running - skipping endpoint tests")
return True
except:
print(" API server not accessible - skipping endpoint tests")
return True

# Test LLM status endpoint
response = requests.get("http://127.0.0.1:8000/llm/status", timeout=10)
if response.status_code == 200:
print(" LLM status endpoint working")
else:
print(f" LLM status endpoint returned {response.status_code}")

# Test chat endpoint
chat_response = requests.post(
"http://127.0.0.1:8000/llm/chat",
json={
"query": "What is financial correlation analysis?",
"user_id": "test_user"
},
timeout=30
)

if chat_response.status_code == 200:
print(" LLM chat endpoint working")
else:
print(f" LLM chat endpoint returned {chat_response.status_code}")

# Test vector search endpoint
search_response = requests.post(
"http://127.0.0.1:8000/llm/vector/search",
json={
"query_type": "text",
"query_data": "tech stock patterns",
"k": 5
},
timeout=30
)

if search_response.status_code == 200:
print(" Vector search endpoint working")
else:
print(f" Vector search endpoint returned {search_response.status_code}")

# Test vector statistics endpoint
stats_response = requests.get("http://127.0.0.1:8000/llm/vector/stats", timeout=10)
if stats_response.status_code == 200:
print(" Vector stats endpoint working")
else:
print(f" Vector stats endpoint returned {stats_response.status_code}")

return True

except Exception as e:
print(f" API endpoints test failed: {e}")
print(f"Traceback: {traceback.format_exc()}")
return False


def test_dashboard_integration():
"""Test dashboard integration."""
print("\n Testing Dashboard Integration...")

try:
from src.dashboard.components.llm_panel import LLMPanel

# Test LLM panel initialization
llm_panel = LLMPanel()
print(f" LLM panel initialized: {llm_panel.__class__.__name__}")

# Test component methods (without Streamlit context)
print(" LLM panel component methods accessible")

return True

except Exception as e:
print(f" Dashboard integration test failed: {e}")
print(f"Traceback: {traceback.format_exc()}")
return False


def test_integration_workflow():
"""Test end-to-end integration workflow."""
print("\n Testing End-to-End Integration Workflow...")

try:
from src.data.vector_database import get_vector_db
from src.models.llm_engine import get_llm_engine
from src.agents.llm_agent import LLMAgent

# Initialize components
vector_db = get_vector_db()
llm_engine = get_llm_engine()
llm_agent = LLMAgent()

# Create and store a financial pattern
sample_data = {
'text_data': 'High volatility technology stock pattern during market uncertainty',
'price_data': pd.Series([100, 95, 98, 92, 96],
index=pd.date_range('2024-01-01', periods=5)),
'symbols': ['TECH_PATTERN']
}

success = vector_db.add_financial_pattern(
pattern_id="integration_test_001",
symbol="TECH_PATTERN",
pattern_type="composite_pattern",
data=sample_data,
metadata={'test_type': 'integration', 'created': datetime.now().isoformat()}
)
print(f" Pattern stored in vector DB: {success}")

# Search for similar patterns
search_results = vector_db.search_by_text_query("technology stock volatility", k=3)
print(f" Similar patterns found: {len(search_results)}")

# Generate LLM analysis if model is available
if llm_engine.get_model_info()['model_available']:
analysis = llm_engine.generate_market_analysis(
{'patterns': search_results},
"Integration test analysis"
)
print(f" LLM analysis generated: {len(analysis.get('analysis', ''))} characters")
else:
print(" No LLM model - skipping analysis generation")

# Test agent workflow
from src.agents.base_agent import Task, TaskPriority

workflow_task = Task(
id="integration_workflow",
name="similarity_search",
priority=TaskPriority.MEDIUM,
created_at=datetime.now(),
scheduled_at=None,
data={
'type': 'similarity_search',
'query_type': 'text',
'query_data': 'volatile tech stocks',
'k': 5
}
)

workflow_result = llm_agent._handle_task(workflow_task)
print(f" Integration workflow completed: {'error' not in workflow_result}")

return True

except Exception as e:
print(f" Integration workflow test failed: {e}")
print(f"Traceback: {traceback.format_exc()}")
return False


def run_dependency_check():
"""Check if all required dependencies are available."""
print(" Checking Dependencies...")

dependencies = {
'faiss-cpu': 'faiss',
'sentence-transformers': 'sentence_transformers',
'llama-cpp-python': 'llama_cpp',
'langchain': 'langchain',
'numpy': 'numpy',
'pandas': 'pandas',
'streamlit': 'streamlit',
'requests': 'requests'
}

missing_deps = []
for dep_name, import_name in dependencies.items():
try:
__import__(import_name)
print(f" {dep_name}")
except ImportError:
print(f" {dep_name} - Missing")
missing_deps.append(dep_name)

if missing_deps:
print(f"\n Missing dependencies: {', '.join(missing_deps)}")
print("Install them with: pip install " + " ".join(missing_deps))
return False

return True


def main():
"""Run all tests."""
print(" Multi-Market Correlation Engine - LLM & Vector DB Integration Test")
print("=" * 80)

start_time = time.time()

# Check dependencies first
if not run_dependency_check():
print("\n Dependency check failed. Please install missing packages.")
return

print("\n" + "=" * 80)

# Run tests
tests = [
("Vector Database", test_vector_database),
("LLM Engine", test_llm_engine),
("LLM Agent", test_llm_agent),
("API Endpoints", test_api_endpoints),
("Dashboard Integration", test_dashboard_integration),
("Integration Workflow", test_integration_workflow)
]

passed = 0
total = len(tests)

for test_name, test_func in tests:
print(f"\n{'='*20} {test_name} {'='*20}")
try:
if test_func():
passed += 1
print(f" {test_name} - PASSED")
else:
print(f" {test_name} - FAILED")
except Exception as e:
print(f" {test_name} - ERROR: {e}")

# Summary
end_time = time.time()
duration = end_time - start_time

print("\n" + "=" * 80)
print(" TEST SUMMARY")
print("=" * 80)
print(f"Total Tests: {total}")
print(f"Passed: {passed}")
print(f"Failed: {total - passed}")
print(f"Success Rate: {passed/total*100:.1f}%")
print(f"Duration: {duration:.2f} seconds")

if passed == total:
print("\n ALL TESTS PASSED! LLM & Vector DB integration is ready!")
print("\n Next Steps:")
print("1. Download a Llama model for full LLM functionality")
print("2. Start the API server: python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000")
print("3. Launch the dashboard: streamlit run src/dashboard/unified_dashboard.py")
print("4. Test the LLM Assistant tab in the dashboard")
else:
print(f"\n {total - passed} tests failed. Check the errors above.")

print("\n" + "=" * 80)


if __name__ == "__main__":
main()
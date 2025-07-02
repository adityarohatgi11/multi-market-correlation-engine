"""
LLM Panel for Streamlit Dashboard
=================================

Interactive dashboard component for AI-powered financial analysis,
vector similarity search, and natural language interface.

Author: Multi-Market Correlation Engine Team
Version: 1.0.0
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)


class LLMPanel:
"""
Streamlit component for LLM and vector database functionality.
"""

def __init__(self, api_base_url: str = "http://127.0.0.1:8000"):
"""
Initialize the LLM panel.

Args:
api_base_url: Base URL for API endpoints
"""
self.api_base_url = api_base_url
self.llm_api_url = f"{api_base_url}/llm"

def render(self):
"""Render the complete LLM panel."""
st.title(" AI-Powered Financial Analysis")
st.markdown("---")

# Check system status
self._render_system_status()

# Create tabs for different LLM functionalities
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
" Chat Assistant",
" Market Analysis",
" Vector Search",
" Correlation Insights",
" Auto Insights",
" System Management"
])

with tab1:
self._render_chat_interface()

with tab2:
self._render_market_analysis()

with tab3:
self._render_vector_search()

with tab4:
self._render_correlation_insights()

with tab5:
self._render_auto_insights()

with tab6:
self._render_system_management()

def _render_system_status(self):
"""Render system status information."""
try:
response = requests.get(f"{self.llm_api_url}/status", timeout=10)
if response.status_code == 200:
status_data = response.json()['data']

col1, col2, col3 = st.columns(3)

with col1:
llm_available = status_data['llm_engine']['model_available']
st.metric(
" LLM Engine",
"Available" if llm_available else "Unavailable",
delta="Ready" if llm_available else "Model not loaded"
)

with col2:
vector_patterns = status_data['vector_database']['total_patterns']
st.metric(
" Vector Database",
f"{vector_patterns} patterns",
delta=f"{status_data['vector_database']['unique_symbols']} symbols"
)

with col3:
agent_status = status_data['llm_agent']['status']
st.metric(
" LLM Agent",
agent_status.capitalize(),
delta=f"{status_data['llm_agent']['tasks_completed']} tasks"
)

if not llm_available:
st.warning(" LLM model not available. Some features will be limited.")

else:
st.error(" Cannot connect to LLM service")

except Exception as e:
st.error(f" System status check failed: {e}")

def _render_chat_interface(self):
"""Render the chat interface."""
st.subheader(" AI Financial Assistant")
st.markdown("Ask questions about market analysis, correlations, or investment strategies.")

# Initialize chat history
if 'chat_history' not in st.session_state:
st.session_state.chat_history = []

# Chat input
col1, col2 = st.columns([4, 1])

with col1:
user_query = st.text_input(
"Your question:",
placeholder="e.g., What are the key factors affecting portfolio diversification?",
key="chat_input"
)

with col2:
send_query = st.button("Send", type="primary")

# User settings
with st.expander(" Chat Settings"):
user_id = st.text_input("User ID", value="default", help="Maintains conversation context")
include_context = st.checkbox("Include conversation context", value=True)

# Process query
if send_query and user_query:
with st.spinner(" AI is thinking..."):
try:
response = requests.post(
f"{self.llm_api_url}/chat",
json={
"query": user_query,
"user_id": user_id,
"include_context": include_context
},
timeout=30
)

if response.status_code == 200:
ai_response = response.json()['data']['response']

# Add to chat history
st.session_state.chat_history.append({
'user': user_query,
'ai': ai_response,
'timestamp': datetime.now().strftime("%H:%M:%S")
})

# Clear input
st.session_state.chat_input = ""
st.rerun()
else:
st.error(f" Chat failed: {response.text}")

except Exception as e:
st.error(f" Chat error: {e}")

# Display chat history
if st.session_state.chat_history:
st.markdown("### 📜 Conversation History")

for i, chat in enumerate(reversed(st.session_state.chat_history[-10:])):
with st.container():
st.markdown(f"**👤 You ({chat['timestamp']}):**")
st.markdown(f"> {chat['user']}")

st.markdown("** AI Assistant:**")
st.markdown(chat['ai'])

if i < len(st.session_state.chat_history) - 1:
st.markdown("---")

# Clear history button
if st.session_state.chat_history:
if st.button(" Clear Chat History"):
st.session_state.chat_history = []
st.rerun()

def _render_market_analysis(self):
"""Render market analysis interface."""
st.subheader(" AI Market Analysis")
st.markdown("Generate comprehensive market insights using AI.")

# Input parameters
col1, col2 = st.columns(2)

with col1:
symbols_input = st.text_area(
"Symbols (one per line):",
value="AAPL\nMSFT\nGOOGL\nAMZN\nTSLA",
height=100
)

with col2:
time_period = st.selectbox(
"Time Period:",
["1D", "1W", "1M", "3M", "6M", "1Y"],
index=2
)

analysis_depth = st.selectbox(
"Analysis Depth:",
["quick", "comprehensive", "detailed"],
index=1
)

if st.button(" Generate Analysis", type="primary"):
symbols = [s.strip().upper() for s in symbols_input.split('\n') if s.strip()]

if not symbols:
st.error(" Please enter at least one symbol")
return

with st.spinner(" Generating market analysis..."):
try:
response = requests.post(
f"{self.llm_api_url}/analyze/market",
json={
"symbols": symbols,
"time_period": time_period,
"analysis_depth": analysis_depth
},
timeout=60
)

if response.status_code == 200:
analysis_data = response.json()['data']

# Display analysis
st.markdown("### Market Analysis Results")

if 'analysis' in analysis_data:
st.markdown("#### AI Insights")
st.markdown(analysis_data['analysis'])

# Show data summary
if 'data_summary' in analysis_data:
with st.expander(" Data Summary"):
st.text(analysis_data['data_summary'])

# Store analysis button
if st.button(" Store Analysis in Vector DB"):
self._store_analysis_in_vector_db(analysis_data, symbols, "market_analysis")

else:
st.error(f" Analysis failed: {response.text}")

except Exception as e:
st.error(f" Analysis error: {e}")

def _render_vector_search(self):
"""Render vector similarity search interface."""
st.subheader(" Vector Similarity Search")
st.markdown("Search for similar financial patterns using AI embeddings.")

# Search type selection
search_type = st.radio(
"Search Type:",
["Text Query", "Symbol Pattern", "Custom Data"],
horizontal=True
)

if search_type == "Text Query":
query_text = st.text_area(
"Describe what you're looking for:",
placeholder="e.g., high volatility tech stocks during market downturns",
height=100
)

if st.button(" Search Patterns"):
if query_text:
self._perform_text_search(query_text)

elif search_type == "Symbol Pattern":
col1, col2 = st.columns(2)

with col1:
symbol = st.text_input("Symbol:", value="AAPL")

with col2:
k_results = st.number_input("Number of results:", min_value=1, max_value=20, value=5)

if st.button(" Find Similar Patterns"):
if symbol:
self._perform_symbol_search(symbol, k_results)

elif search_type == "Custom Data":
st.markdown("Upload custom financial data for similarity search")

uploaded_file = st.file_uploader(
"Upload CSV file:",
type=['csv'],
help="CSV should contain price data with columns: date, close"
)

if uploaded_file and st.button(" Search Similar"):
self._perform_custom_search(uploaded_file)

# Search filters
with st.expander(" Search Filters"):
col1, col2 = st.columns(2)

with col1:
min_similarity = st.slider(
"Minimum Similarity:",
min_value=0.0,
max_value=1.0,
value=0.5,
step=0.1
)

with col2:
pattern_type_filter = st.selectbox(
"Pattern Type:",
["All", "price_pattern", "correlation_pattern", "regime_pattern", "composite_pattern"]
)

# Vector database statistics
st.markdown("### Vector Database Statistics")
self._show_vector_stats()

def _render_correlation_insights(self):
"""Render correlation insights interface."""
st.subheader(" Correlation Pattern Insights")
st.markdown("Analyze correlation patterns with AI explanations.")

# Manual correlation input
st.markdown("#### Manual Correlation Matrix")

symbols_for_corr = st.text_input(
"Symbols (comma-separated):",
value="AAPL,MSFT,GOOGL,AMZN"
)

if symbols_for_corr:
symbols_list = [s.strip().upper() for s in symbols_for_corr.split(',')]

# Create manual correlation matrix input
if len(symbols_list) <= 6: # Reasonable limit for manual input
corr_data = {}

st.markdown("Enter correlation values (0 to 1):")

for i, symbol1 in enumerate(symbols_list):
corr_data[symbol1] = {}
cols = st.columns(len(symbols_list))

for j, symbol2 in enumerate(symbols_list):
if i == j:
corr_data[symbol1][symbol2] = 1.0
cols[j].text_input(f"{symbol1}-{symbol2}", value="1.0", disabled=True, key=f"corr_{i}_{j}")
elif i < j:
corr_value = cols[j].number_input(
f"{symbol1}-{symbol2}",
min_value=-1.0,
max_value=1.0,
value=0.5,
step=0.1,
key=f"corr_{i}_{j}"
)
corr_data[symbol1][symbol2] = corr_value
corr_data[symbol2] = corr_data.get(symbol2, {})
corr_data[symbol2][symbol1] = corr_value
else:
# Use symmetry
if symbol2 in corr_data and symbol1 in corr_data[symbol2]:
corr_value = corr_data[symbol2][symbol1]
corr_data[symbol1][symbol2] = corr_value
cols[j].text_input(f"{symbol1}-{symbol2}", value=str(corr_value), disabled=True, key=f"corr_{i}_{j}")

# Time period
time_period = st.selectbox(
"Time Period Description:",
["Last Month", "Last Quarter", "Last Year", "Bear Market", "Bull Market", "Recent Volatility"],
key="corr_time_period"
)

if st.button(" Analyze Correlations"):
self._analyze_correlations(corr_data, time_period)

else:
st.warning(" Please enter 6 or fewer symbols for manual correlation input")

# Sample correlation analysis
st.markdown("#### Quick Analysis")
if st.button(" Analyze Sample Tech Portfolio"):
sample_corr = {
"AAPL": {"AAPL": 1.0, "MSFT": 0.72, "GOOGL": 0.68, "AMZN": 0.65},
"MSFT": {"AAPL": 0.72, "MSFT": 1.0, "GOOGL": 0.75, "AMZN": 0.69},
"GOOGL": {"AAPL": 0.68, "MSFT": 0.75, "GOOGL": 1.0, "AMZN": 0.71},
"AMZN": {"AAPL": 0.65, "MSFT": 0.69, "GOOGL": 0.71, "AMZN": 1.0}
}
self._analyze_correlations(sample_corr, "Recent Tech Rally")

def _render_auto_insights(self):
"""Render auto insights generation interface."""
st.subheader(" Automated Insights")
st.markdown("Generate AI insights based on market triggers and events.")

# Trigger type selection
trigger_type = st.selectbox(
"Insight Trigger Type:",
["general", "correlation_change", "regime_change", "anomaly_detection", "portfolio_alert"]
)

# Trigger-specific inputs
if trigger_type == "correlation_change":
st.markdown("#### Correlation Change Analysis")

old_corr = st.number_input("Previous correlation:", value=0.5, min_value=-1.0, max_value=1.0, step=0.1)
new_corr = st.number_input("New correlation:", value=0.8, min_value=-1.0, max_value=1.0, step=0.1)

trigger_data = {
"symbols": ["AAPL", "MSFT"],
"old_correlation": old_corr,
"new_correlation": new_corr,
"change_magnitude": abs(new_corr - old_corr)
}

elif trigger_type == "regime_change":
st.markdown("#### Regime Change Analysis")

old_regime = st.selectbox("Previous regime:", ["bull", "bear", "neutral", "crisis", "recovery"])
new_regime = st.selectbox("New regime:", ["bull", "bear", "neutral", "crisis", "recovery"])

trigger_data = {
"old_regime": old_regime,
"new_regime": new_regime,
"transition_probability": st.slider("Transition probability:", 0.0, 1.0, 0.7, 0.1)
}

elif trigger_type == "anomaly_detection":
st.markdown("#### Anomaly Detection Analysis")

anomaly_type = st.selectbox("Anomaly type:", ["price_spike", "volume_surge", "correlation_break", "volatility_burst"])
severity = st.selectbox("Severity:", ["low", "medium", "high", "extreme"])

trigger_data = {
"anomaly_type": anomaly_type,
"severity": severity,
"affected_symbols": ["AAPL", "MSFT", "GOOGL"],
"confidence": st.slider("Detection confidence:", 0.0, 1.0, 0.8, 0.1)
}

elif trigger_type == "portfolio_alert":
st.markdown("#### Portfolio Alert Analysis")

alert_type = st.selectbox("Alert type:", ["rebalancing", "risk_limit", "drawdown", "concentration"])

trigger_data = {
"alert_type": alert_type,
"portfolio_drift": st.slider("Portfolio drift (%):", 0.0, 50.0, 15.0, 1.0),
"risk_level": st.selectbox("Current risk level:", ["low", "medium", "high", "extreme"])
}

else:
trigger_data = {}

if st.button(" Generate Insights", type="primary"):
self._generate_insights(trigger_type, trigger_data)

def _render_system_management(self):
"""Render system management interface."""
st.subheader(" System Management")
st.markdown("Manage AI models and vector database.")

# Model information
st.markdown("#### Available Models")
self._show_available_models()

# Vector database management
st.markdown("#### Vector Database Management")

col1, col2, col3, col4 = st.columns(4)

with col1:
if st.button(" Save Vector Index"):
self._save_vector_index()

with col2:
if st.button(" Load Vector Index"):
self._load_vector_index()

with col3:
if st.button(" Show Statistics"):
self._show_detailed_vector_stats()

with col4:
if st.button(" Clear Database", type="secondary"):
if st.session_state.get('confirm_clear', False):
self._clear_vector_database()
st.session_state.confirm_clear = False
else:
st.session_state.confirm_clear = True
st.warning(" Click again to confirm clearing the database")

def _perform_text_search(self, query_text: str):
"""Perform text-based similarity search."""
try:
response = requests.post(
f"{self.llm_api_url}/vector/search",
json={
"query_type": "text",
"query_data": query_text,
"k": 10
},
timeout=30
)

if response.status_code == 200:
results = response.json()['data']['results']
self._display_search_results(results, f"Text search: '{query_text}'")
else:
st.error(f" Search failed: {response.text}")

except Exception as e:
st.error(f" Search error: {e}")

def _perform_symbol_search(self, symbol: str, k: int):
"""Perform symbol pattern similarity search."""
try:
# Note: This would need actual price data in a real implementation
st.info(" Symbol pattern search requires historical price data integration")

# For demo, show how it would work
st.markdown(f"**Would search for patterns similar to {symbol}:**")
st.markdown("- Price movement patterns")
st.markdown("- Volatility characteristics")
st.markdown("- Technical indicator similarities")

except Exception as e:
st.error(f" Search error: {e}")

def _perform_custom_search(self, uploaded_file):
"""Perform custom data similarity search."""
try:
# Read uploaded CSV
df = pd.read_csv(uploaded_file)

if 'close' not in df.columns:
st.error(" CSV must contain 'close' column")
return

st.success(f" Uploaded {len(df)} data points")
st.dataframe(df.head())

# In a real implementation, this would create embeddings and search
st.info(" Custom data search functionality ready for implementation")

except Exception as e:
st.error(f" File processing error: {e}")

def _analyze_correlations(self, correlation_matrix: Dict, time_period: str):
"""Analyze correlation patterns."""
try:
response = requests.post(
f"{self.llm_api_url}/analyze/correlations",
json={
"correlation_matrix": correlation_matrix,
"time_period": time_period
},
timeout=30
)

if response.status_code == 200:
insights = response.json()['data']

st.markdown("### Correlation Analysis Results")

if 'insights' in insights:
st.markdown("#### AI Insights")
st.markdown(insights['insights'])

# Visualize correlation matrix
if 'correlation_summary' in insights:
st.markdown("#### Correlation Visualization")
self._plot_correlation_heatmap(correlation_matrix)

else:
st.error(f" Analysis failed: {response.text}")

except Exception as e:
st.error(f" Analysis error: {e}")

def _generate_insights(self, trigger_type: str, trigger_data: Dict):
"""Generate automated insights."""
try:
response = requests.post(
f"{self.llm_api_url}/insights/generate",
params={"trigger_type": trigger_type},
json=trigger_data,
timeout=30
)

if response.status_code == 200:
insights_data = response.json()['data']

st.markdown("### Generated Insights")

insights = insights_data.get('insights', [])

if insights:
for i, insight in enumerate(insights):
with st.container():
st.markdown(f"**Insight {i+1}:**")
st.markdown(f"- **Type:** {insight.get('type', 'General')}")
st.markdown(f"- **Content:** {insight.get('content', 'No content')}")
st.markdown(f"- **Timestamp:** {insight.get('timestamp', 'Unknown')}")

if i < len(insights) - 1:
st.markdown("---")
else:
st.info("No specific insights generated for this trigger.")

else:
st.error(f" Insight generation failed: {response.text}")

except Exception as e:
st.error(f" Insight generation error: {e}")

def _show_vector_stats(self):
"""Show vector database statistics."""
try:
response = requests.get(f"{self.llm_api_url}/vector/stats", timeout=10)

if response.status_code == 200:
stats = response.json()['data']

col1, col2, col3 = st.columns(3)

with col1:
st.metric("Total Patterns", stats.get('total_patterns', 0))

with col2:
st.metric("Unique Symbols", stats.get('unique_symbols', 0))

with col3:
st.metric("Index Type", stats.get('index_type', 'Unknown'))

# Pattern types breakdown
pattern_types = stats.get('pattern_types', {})
if pattern_types:
st.markdown("**Pattern Types:**")
for ptype, count in pattern_types.items():
st.markdown(f"- {ptype}: {count}")

else:
st.error(" Cannot retrieve vector database statistics")

except Exception as e:
st.error(f" Stats error: {e}")

def _show_available_models(self):
"""Show available AI models information."""
try:
response = requests.get(f"{self.llm_api_url}/models/available", timeout=10)

if response.status_code == 200:
models_info = response.json()['data']

# LLM Models
st.markdown("** Language Models:**")
llm_models = models_info.get('llm_models', {})
for model_name, model_info in llm_models.items():
available = "" if model_info.get('available', False) else ""
st.markdown(f"- {model_name}: {available}")
if model_info.get('model_path'):
st.markdown(f" - Path: {model_info['model_path']}")

# Embedding Models
st.markdown("**🔤 Embedding Models:**")
embedding_models = models_info.get('embedding_models', {})
for model_name, model_info in embedding_models.items():
st.markdown(f"- {model_name}: ")
st.markdown(f" - Model: {model_info.get('model', 'Unknown')}")
st.markdown(f" - Dimension: {model_info.get('dimension', 'Unknown')}")

else:
st.error(" Cannot retrieve models information")

except Exception as e:
st.error(f" Models info error: {e}")

def _plot_correlation_heatmap(self, correlation_matrix: Dict):
"""Plot correlation heatmap."""
try:
# Convert to DataFrame
df = pd.DataFrame(correlation_matrix)

# Create heatmap
fig = px.imshow(
df,
color_continuous_scale='RdBu_r',
aspect='auto',
title='Correlation Matrix Heatmap'
)

fig.update_layout(
width=600,
height=500,
title_x=0.5
)

st.plotly_chart(fig, use_container_width=True)

except Exception as e:
st.error(f" Plotting error: {e}")

def _display_search_results(self, results: List[Dict], search_description: str):
"""Display similarity search results."""
st.markdown(f"### Search Results: {search_description}")

if not results:
st.info("No similar patterns found.")
return

for i, result in enumerate(results):
with st.container():
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
st.markdown(f"**Pattern {i+1}:** {result.get('pattern_id', 'Unknown')}")
st.markdown(f"Symbol: {result.get('symbol', 'Unknown')}")
st.markdown(f"Type: {result.get('pattern_type', 'Unknown')}")

with col2:
similarity = result.get('similarity_score', 0)
st.metric("Similarity", f"{similarity:.3f}")

with col3:
timestamp = result.get('timestamp', 'Unknown')
if timestamp != 'Unknown':
try:
dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
st.markdown(f"**Date:**<br>{dt.strftime('%Y-%m-%d')}", unsafe_allow_html=True)
except:
st.markdown(f"**Date:**<br>{timestamp}", unsafe_allow_html=True)

if i < len(results) - 1:
st.markdown("---")

def _store_analysis_in_vector_db(self, analysis_data: Dict, symbols: List[str], analysis_type: str):
"""Store analysis in vector database."""
try:
pattern_id = f"{analysis_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

response = requests.post(
f"{self.llm_api_url}/vector/store",
json={
"pattern_id": pattern_id,
"symbol": ",".join(symbols),
"pattern_type": "composite_pattern",
"data": {
"text_data": analysis_data.get('analysis', ''),
"analysis_type": analysis_type
},
"metadata": {
"symbols": symbols,
"analysis_type": analysis_type,
"timestamp": datetime.now().isoformat()
}
},
timeout=30
)

if response.status_code == 200:
st.success(f" Analysis stored with ID: {pattern_id}")
else:
st.error(f" Storage failed: {response.text}")

except Exception as e:
st.error(f" Storage error: {e}")

def _save_vector_index(self):
"""Save vector database index."""
try:
response = requests.post(f"{self.llm_api_url}/vector/save", timeout=30)

if response.status_code == 200:
st.success(" Vector index saved successfully")
else:
st.error(f" Save failed: {response.text}")

except Exception as e:
st.error(f" Save error: {e}")

def _load_vector_index(self):
"""Load vector database index."""
try:
response = requests.post(f"{self.llm_api_url}/vector/load", timeout=30)

if response.status_code == 200:
st.success(" Vector index loaded successfully")
else:
st.error(f" Load failed: {response.text}")

except Exception as e:
st.error(f" Load error: {e}")

def _clear_vector_database(self):
"""Clear vector database."""
try:
response = requests.delete(f"{self.llm_api_url}/vector/clear", timeout=30)

if response.status_code == 200:
st.success(" Vector database cleared successfully")
st.session_state.confirm_clear = False
else:
st.error(f" Clear failed: {response.text}")

except Exception as e:
st.error(f" Clear error: {e}")

def _show_detailed_vector_stats(self):
"""Show detailed vector database statistics."""
try:
response = requests.get(f"{self.llm_api_url}/vector/stats", timeout=10)

if response.status_code == 200:
stats = response.json()['data']

st.json(stats)
else:
st.error(" Cannot retrieve detailed statistics")

except Exception as e:
st.error(f" Detailed stats error: {e}")


def render_llm_panel():
"""
Render the LLM panel (main entry point).
"""
try:
panel = LLMPanel()
panel.render()
except Exception as e:
st.error(f" LLM panel failed to load: {e}")
st.markdown("Please ensure the API server is running and accessible.")


if __name__ == "__main__":
# Test the panel
render_llm_panel()
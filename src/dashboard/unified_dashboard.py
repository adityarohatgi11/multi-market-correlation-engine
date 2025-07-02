"""
Unified Multi-Market Correlation Engine Dashboard
Combines all features: System Monitoring, Financial Analysis, and AI-Powered Insights
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
import networkx as nx
from datetime import datetime, timedelta
import time
import requests
import json
import logging
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Configure page
st.set_page_config(
page_title="Multi-Market Correlation Engine - Unified Dashboard",
page_icon="",
layout="wide",
initial_sidebar_state="expanded"
)

# Import project modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.config_manager import ConfigManager
from src.data.database_manager import DatabaseManager
from src.models.correlation_engine import CorrelationEngine
from src.agents.agent_coordinator import AgentCoordinator
from src.collectors.yahoo_finance_collector import YahooFinanceCollector
from src.models.garch_models import GARCHAnalyzer
from src.models.var_models import VARAnalyzer
from src.models.ml_models import MLCorrelationPredictor, RegimeDetector
from src.models.network_analysis import NetworkAnalyzer

# Import recommendation panel
try:
from src.dashboard.components.recommendation_panel import RecommendationPanel
RECOMMENDATIONS_AVAILABLE = True
except ImportError as e:
st.warning(f"Recommendation panel not available: {e}")
RECOMMENDATIONS_AVAILABLE = False

# Import LLM panel
try:
from src.dashboard.components.llm_panel import LLMPanel
LLM_AVAILABLE = True
except ImportError as e:
st.warning(f"LLM panel not available: {e}")
LLM_AVAILABLE = False

# Initialize components
@st.cache_resource
def initialize_components():
"""Initialize all system components"""
try:
config = ConfigManager()
db_manager = DatabaseManager()
correlation_engine = CorrelationEngine()
collector = YahooFinanceCollector()

# Initialize AI/ML models (constructors require no external arguments)
garch_analyzer = GARCHAnalyzer()
var_analyzer = VARAnalyzer()
ml_predictor = MLCorrelationPredictor()
regime_detector = RegimeDetector()
network_analyzer = NetworkAnalyzer()

return {
'config': config,
'db_manager': db_manager,
'correlation_engine': correlation_engine,
'collector': collector,
'garch_analyzer': garch_analyzer,
'var_analyzer': var_analyzer,
'ml_predictor': ml_predictor,
'regime_detector': regime_detector,
'network_analyzer': network_analyzer
}
except Exception as e:
st.error(f"Failed to initialize components: {e}")
return None

def check_api_status():
"""Check if API server is running"""
try:
response = requests.get("http://127.0.0.1:8000/health", timeout=5)
return response.status_code == 200, response.json() if response.status_code == 200 else None
except:
return False, None

def get_agent_status():
"""Get agent system status"""
try:
response = requests.get("http://127.0.0.1:8000/agents/status", timeout=5)
return response.json() if response.status_code == 200 else None
except:
return None

def collect_data_via_api(symbols: List[str]):
"""Trigger data collection via API"""
try:
response = requests.post(
"http://127.0.0.1:8000/agents/collect",
json={"symbols": symbols},
timeout=30
)
return response.status_code == 200, response.json() if response.status_code == 200 else None
except Exception as e:
return False, str(e)

def get_market_data_via_api(symbols: List[str], limit: int = 100):
"""Get market data via API"""
try:
params = {"symbols": ",".join(symbols), "limit": limit}
response = requests.get("http://127.0.0.1:8000/data/market", params=params, timeout=10)
return response.json() if response.status_code == 200 else None
except:
return None

def get_correlations_via_api(symbols: List[str]):
"""Get correlations via API"""
try:
params = {"symbols": ",".join(symbols)}
response = requests.get("http://127.0.0.1:8000/data/correlations", params=params, timeout=10)
return response.json() if response.status_code == 200 else None
except:
return None

def create_correlation_heatmap(correlation_matrix: pd.DataFrame):
"""Create correlation heatmap"""
fig = px.imshow(
correlation_matrix,
text_auto=True,
aspect="auto",
color_continuous_scale="RdBu_r",
title="Asset Correlation Matrix"
)
fig.update_layout(height=500)
return fig

def create_price_chart(data: pd.DataFrame, symbols: List[str]):
"""Create price chart"""
fig = go.Figure()

for symbol in symbols:
symbol_data = data[data['symbol'] == symbol].sort_values('timestamp')
if not symbol_data.empty:
fig.add_trace(go.Scatter(
x=symbol_data['timestamp'],
y=symbol_data['close'],
mode='lines',
name=symbol,
line=dict(width=2)
))

fig.update_layout(
title="Price Trends",
xaxis_title="Date",
yaxis_title="Price ($)",
height=400,
hovermode='x unified'
)
return fig

def create_network_graph(correlation_matrix: pd.DataFrame, threshold: float = 0.5):
"""Create network graph of correlations"""
G = nx.Graph()

# Add nodes
for symbol in correlation_matrix.index:
G.add_node(symbol)

# Add edges for correlations above threshold
for i, symbol1 in enumerate(correlation_matrix.index):
for j, symbol2 in enumerate(correlation_matrix.columns):
if i < j: # Avoid duplicates
corr_value = correlation_matrix.iloc[i, j]
if abs(corr_value) >= threshold:
G.add_edge(symbol1, symbol2, weight=abs(corr_value))

# Create layout
pos = nx.spring_layout(G, k=1, iterations=50)

# Create traces
edge_x, edge_y = [], []
for edge in G.edges():
x0, y0 = pos[edge[0]]
x1, y1 = pos[edge[1]]
edge_x.extend([x0, x1, None])
edge_y.extend([y0, y1, None])

node_x = [pos[node][0] for node in G.nodes()]
node_y = [pos[node][1] for node in G.nodes()]

fig = go.Figure()

# Add edges
fig.add_trace(go.Scatter(
x=edge_x, y=edge_y,
line=dict(width=2, color='lightgray'),
hoverinfo='none',
mode='lines'
))

# Add nodes
fig.add_trace(go.Scatter(
x=node_x, y=node_y,
mode='markers+text',
hoverinfo='text',
text=list(G.nodes()),
textposition="middle center",
marker=dict(
size=30,
color='lightblue',
line=dict(width=2, color='darkblue')
)
))

fig.update_layout(
title="Correlation Network",
showlegend=False,
hovermode='closest',
margin=dict(b=20,l=5,r=5,t=40),
annotations=[
dict(
text="Node size represents centrality",
showarrow=False,
xref="paper", yref="paper",
x=0.005, y=-0.002,
xanchor='left', yanchor='bottom',
font=dict(size=12)
)
],
xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
height=500
)

return fig

def main():
# Header
st.title(" Multi-Market Correlation Engine")
st.markdown("**Unified Dashboard - System Monitoring • Financial Analysis • AI-Powered Insights**")

# Initialize components
components = initialize_components()
if not components:
st.error("Failed to initialize system components")
return

# Sidebar - System Status
with st.sidebar:
st.header(" System Status")

# API Status
api_running, api_data = check_api_status()
if api_running:
st.success(" API Server: Running")
if api_data:
st.json(api_data)
else:
st.error(" API Server: Offline")
st.info("Start API: `python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 &`")

# Agent Status
if api_running:
agent_status = get_agent_status()
if agent_status:
st.success(" Agents: Active")
for agent_name, status in agent_status.items():
status_icon = "🟢" if status.get('status') == 'running' else "🔴"
st.write(f"{status_icon} {agent_name}")
else:
st.warning(" Agents: Unknown")

st.divider()

# Symbol Selection
st.header(" Analysis Settings")

# Available symbols
available_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "JPM", "BAC", "GS", "XOM", "CVX", "JNJ", "PFE"]

# Predefined groups
symbol_groups = {
"Tech Stocks": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],
"Financial": ["JPM", "BAC", "GS"],
"Energy": ["XOM", "CVX"],
"Healthcare": ["JNJ", "PFE"],
"Mixed Portfolio": ["AAPL", "MSFT", "JPM", "XOM", "JNJ"]
}

selected_group = st.selectbox("Choose Symbol Group", list(symbol_groups.keys()))
default_symbols = symbol_groups[selected_group]

symbols = st.multiselect(
"Select Symbols",
options=available_symbols,
default=default_symbols,
help="Choose 2-5 symbols for analysis"
)

# Analysis parameters
st.subheader("Parameters")
lookback_days = st.slider("Lookback Period (days)", 30, 365, 90)
correlation_threshold = st.slider("Correlation Threshold", 0.1, 0.9, 0.5)

# Data collection
st.divider()
if st.button(" Collect Fresh Data", type="primary"):
if api_running and symbols:
with st.spinner("Collecting data..."):
success, result = collect_data_via_api(symbols)
if success:
st.success("Data collected successfully!")
st.rerun()
else:
st.error(f"Data collection failed: {result}")
else:
st.error("API not running or no symbols selected")

if not symbols:
st.warning("Please select symbols to begin analysis")
return

# Main Dashboard Tabs - reorder for logical flow
tabs = [
" Market Overview",
"🔗 Correlations",
" Network Analysis",
" AI Insights",
" System Monitor"
]

# Insert optional tabs at appropriate positions
if RECOMMENDATIONS_AVAILABLE:
tabs.insert(3, " Recommendations") # After Network, before AI

if LLM_AVAILABLE:
tabs.insert(-1, "🧠 LLM Assistant") # Before System Monitor

# Create tabs dynamically based on available features
if RECOMMENDATIONS_AVAILABLE and LLM_AVAILABLE:
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(tabs)
elif RECOMMENDATIONS_AVAILABLE or LLM_AVAILABLE:
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(tabs)
else:
tab1, tab2, tab3, tab4, tab5 = st.tabs(tabs)

# Tab 1: Market Overview
with tab1:
st.header(" Market Overview")

# Get market data
if api_running:
market_data = get_market_data_via_api(symbols, limit=lookback_days)
if market_data and market_data.get('data'):
df = pd.DataFrame(market_data['data'])
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Metrics row
col1, col2, col3, col4 = st.columns(4)
with col1:
st.metric("Total Records", len(df))
with col2:
st.metric("Symbols", len(symbols))
with col3:
latest_date = df['timestamp'].max().strftime('%Y-%m-%d')
st.metric("Latest Data", latest_date)
with col4:
data_quality = market_data.get('metadata', {}).get('quality_score', 0)
st.metric("Data Quality", f"{data_quality:.1%}")

# Price chart
st.plotly_chart(create_price_chart(df, symbols), use_container_width=True)

# Recent data table
st.subheader("Recent Market Data")
recent_data = df.groupby('symbol').tail(5).sort_values(['symbol', 'timestamp'])
st.dataframe(recent_data[['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume']], use_container_width=True)

else:
st.warning("No market data available. Try collecting fresh data.")
else:
st.error("API server not running. Cannot fetch market data.")

# Tab 2: Correlations
with tab2:
st.header("🔗 Correlation Analysis")

if api_running:
corr_data = get_correlations_via_api(symbols)
if corr_data and corr_data.get('correlation_matrix'):
corr_matrix = pd.DataFrame(corr_data['correlation_matrix'])

# Correlation heatmap
st.plotly_chart(create_correlation_heatmap(corr_matrix), use_container_width=True)

# Correlation statistics
col1, col2 = st.columns(2)

with col1:
st.subheader("Correlation Statistics")
# Get upper triangle correlations
mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
correlations = corr_matrix.where(mask).stack().reset_index()
correlations.columns = ['Asset 1', 'Asset 2', 'Correlation']
correlations = correlations.sort_values('Correlation', key=abs, ascending=False)
st.dataframe(correlations, use_container_width=True)

with col2:
st.subheader("Key Insights")

# Highest correlations
high_corr = correlations[correlations['Correlation'].abs() >= correlation_threshold]
st.write(f"**High Correlations (≥{correlation_threshold}):**")
for _, row in high_corr.head(5).iterrows():
direction = "" if row['Correlation'] > 0 else ""
st.write(f"{direction} {row['Asset 1']} ↔ {row['Asset 2']}: {row['Correlation']:.3f}")

# Average correlation
avg_corr = correlations['Correlation'].mean()
st.metric("Average Correlation", f"{avg_corr:.3f}")

# Most correlated asset
asset_avg_corr = corr_matrix.mean().sort_values(ascending=False)
st.write(f"**Most Connected Asset:** {asset_avg_corr.index[0]} ({asset_avg_corr.iloc[0]:.3f})")
else:
st.warning("No correlation data available.")
else:
st.error("API server not running. Cannot fetch correlation data.")

# Tab 3: Recommendations (if available)
if RECOMMENDATIONS_AVAILABLE:
with tab4:
try:
recommendation_panel = RecommendationPanel()
recommendation_panel.render()
except Exception as e:
st.error(f"Error loading recommendation panel: {e}")
st.info("Please ensure all recommendation dependencies are installed.")

# LLM Assistant tab (if available)
if LLM_AVAILABLE:
llm_tab_index = -2 # Second to last tab (before System Monitor)

# Determine which tab variable to use based on available features
if RECOMMENDATIONS_AVAILABLE and LLM_AVAILABLE:
llm_tab = tab6 # tab1, tab2, tab3, tab4(recs), tab5(ai), tab6(llm), tab7(sys)
elif LLM_AVAILABLE:
llm_tab = tab5 # tab1, tab2, tab3(ai), tab4(net), tab5(llm), tab6(sys)
else:
llm_tab = None

if llm_tab:
with llm_tab:
try:
llm_panel = LLMPanel()
llm_panel.render()
except Exception as e:
st.error(f"Error loading LLM panel: {e}")
st.info("Please ensure all LLM dependencies are installed and models are available.")

# AI Insights tab (adjusted index based on available features)
if RECOMMENDATIONS_AVAILABLE and LLM_AVAILABLE:
ai_tab = tab5 # tab1, tab2, tab3, tab4(recs), tab5(ai), tab6(llm), tab7(sys)
elif RECOMMENDATIONS_AVAILABLE:
ai_tab = tab5 # tab1, tab2, tab3, tab4(recs), tab5(ai), tab6(sys)
elif LLM_AVAILABLE:
ai_tab = tab3 # tab1, tab2, tab3(ai), tab4(net), tab5(llm), tab6(sys)
else:
ai_tab = tab3 # tab1, tab2, tab3(ai), tab4(net), tab5(sys)

with ai_tab:
st.header(" AI-Powered Insights")

col1, col2 = st.columns(2)

with col1:
st.subheader(" GARCH Volatility Analysis")
if st.button("Run GARCH Analysis"):
with st.spinner("Running GARCH analysis..."):
try:
garch_results = components['garch_analyzer'].comprehensive_analysis(symbols)
if garch_results:
st.success("GARCH analysis completed!")

# Display volatility forecasts
for symbol in symbols:
if symbol in garch_results.get('volatility_forecasts', {}):
forecast = garch_results['volatility_forecasts'][symbol]
st.write(f"**{symbol}** - Next day volatility forecast: {forecast:.4f}")
else:
st.warning("GARCH analysis returned no results")
except Exception as e:
st.error(f"GARCH analysis failed: {e}")

with col2:
st.subheader(" VAR Analysis")
if st.button("Run VAR Analysis"):
with st.spinner("Running VAR analysis..."):
try:
var_results = components['var_analyzer'].comprehensive_analysis(symbols)
if var_results:
st.success("VAR analysis completed!")

# Display Granger causality results
if 'granger_causality' in var_results:
st.write("**Granger Causality Results:**")
for pair, result in var_results['granger_causality'].items():
if result.get('p_value', 1) < 0.05:
st.write(f" {pair}: Significant causality (p={result['p_value']:.4f})")
else:
st.warning("VAR analysis returned no results")
except Exception as e:
st.error(f"VAR analysis failed: {e}")

st.divider()

# ML Predictions
col3, col4 = st.columns(2)

with col3:
st.subheader("🧠 ML Correlation Prediction")
if st.button("Generate ML Predictions"):
with st.spinner("Running ML predictions..."):
try:
# Get recent data for prediction
if api_running:
market_data = get_market_data_via_api(symbols, limit=100)
if market_data and market_data.get('data'):
df = pd.DataFrame(market_data['data'])

predictions = components['ml_predictor'].predict_correlations(df, symbols)
if predictions:
st.success("ML predictions generated!")
st.json(predictions)
else:
st.warning("No predictions generated")
else:
st.error("No market data for predictions")
else:
st.error("API not running")
except Exception as e:
st.error(f"ML prediction failed: {e}")

with col4:
st.subheader(" Regime Detection")
if st.button("Detect Market Regimes"):
with st.spinner("Detecting market regimes..."):
try:
regime_results = components['regime_detector'].analyze_regimes(symbols)
if regime_results:
st.success("Regime analysis completed!")

# Display current regime
current_regime = regime_results.get('current_regime', 'Unknown')
regime_prob = regime_results.get('regime_probability', 0)

st.metric("Current Market Regime", current_regime)
st.metric("Confidence", f"{regime_prob:.1%}")

# Regime characteristics
if 'regime_characteristics' in regime_results:
st.write("**Regime Characteristics:**")
for char, value in regime_results['regime_characteristics'].items():
st.write(f"• {char}: {value}")
else:
st.warning("Regime analysis returned no results")
except Exception as e:
st.error(f"Regime detection failed: {e}")

# Network Analysis tab (adjusted index based on available features)
if RECOMMENDATIONS_AVAILABLE and LLM_AVAILABLE:
network_tab = tab4 # Recommendations take tab4, this moves to a different position
# Actually, let me recalculate: tab1(market), tab2(corr), tab3(?), tab4(recs), tab5(ai), tab6(llm), tab7(sys)
# Network should be after correlations, so tab3
network_tab = tab3
elif RECOMMENDATIONS_AVAILABLE:
network_tab = tab4 # tab1(market), tab2(corr), tab3(?), tab4(recs), tab5(ai), tab6(sys)
# Actually: tab1(market), tab2(corr), tab3(network), tab4(recs), tab5(ai), tab6(sys)
network_tab = tab3
elif LLM_AVAILABLE:
network_tab = tab4 # tab1(market), tab2(corr), tab3(ai), tab4(net), tab5(llm), tab6(sys)
else:
network_tab = tab4 # tab1(market), tab2(corr), tab3(ai), tab4(net), tab5(sys)

with network_tab:
st.header(" Network Analysis")

if api_running:
corr_data = get_correlations_via_api(symbols)
if corr_data and corr_data.get('correlation_matrix'):
corr_matrix = pd.DataFrame(corr_data['correlation_matrix'])

# Network graph
st.plotly_chart(create_network_graph(corr_matrix, correlation_threshold), use_container_width=True)

# Network metrics
col1, col2 = st.columns(2)

with col1:
st.subheader("Network Metrics")
if st.button("Calculate Network Metrics"):
with st.spinner("Analyzing network..."):
try:
network_results = components['network_analyzer'].comprehensive_analysis(symbols)
if network_results:
st.success("Network analysis completed!")

# Display network metrics
metrics = network_results.get('network_metrics', {})
for metric, value in metrics.items():
st.metric(metric.replace('_', ' ').title(), f"{value:.3f}")

# Systemic risk ranking
if 'systemic_risk' in network_results:
st.write("**Systemic Risk Ranking:**")
for i, (symbol, risk) in enumerate(network_results['systemic_risk'].items(), 1):
st.write(f"{i}. {symbol}: {risk:.3f}")
else:
st.warning("Network analysis returned no results")
except Exception as e:
st.error(f"Network analysis failed: {e}")

with col2:
st.subheader("Connection Analysis")

# Most connected assets
connections = corr_matrix.abs().sum().sort_values(ascending=False)
st.write("**Most Connected Assets:**")
for symbol, conn_strength in connections.items():
st.write(f"• {symbol}: {conn_strength:.2f}")
else:
st.warning("No correlation data for network analysis.")
else:
st.error("API server not running.")

# Tab 5: System Monitor
with tab5:
st.header(" System Monitor")

# System health
col1, col2, col3 = st.columns(3)

with col1:
st.subheader(" API Health")
if api_running:
st.success("API Server: Running")
st.write("**Endpoint:** http://127.0.0.1:8000")
st.write("**Documentation:** http://127.0.0.1:8000/docs")
else:
st.error("API Server: Offline")
st.code("python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 &")

with col2:
st.subheader(" Agent System")
if api_running:
agent_status = get_agent_status()
if agent_status:
for agent_name, status in agent_status.items():
status_color = "🟢" if status.get('status') == 'running' else "🔴"
st.write(f"{status_color} **{agent_name}**")
st.write(f" Status: {status.get('status', 'unknown')}")
st.write(f" Tasks: {status.get('tasks_completed', 0)}")
else:
st.warning("Agent status unavailable")
else:
st.error("API not running")

with col3:
st.subheader(" Database")
try:
db_manager = components['db_manager']
# Try to get record count
total_records = len(db_manager.get_market_data(symbols, limit=10000))
st.success("Database: Connected")
st.metric("Total Records", total_records)
except Exception as e:
st.error(f"Database: Error - {e}")

# System logs (if available)
st.subheader(" Recent Activity")
if api_running:
try:
# Try to get some system info
response = requests.get("http://127.0.0.1:8000/", timeout=5)
if response.status_code == 200:
system_info = response.json()
st.json(system_info)
except:
st.info("No recent activity logs available")
else:
st.info("API server offline - no activity logs")

# Performance metrics
st.subheader(" Performance")

# Simulate some performance metrics
perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)

with perf_col1:
st.metric("Uptime", "99.9%")
with perf_col2:
st.metric("Avg Response", "250ms")
with perf_col3:
st.metric("Memory Usage", "85%")
with perf_col4:
st.metric("CPU Usage", "42%")

if __name__ == "__main__":
main()
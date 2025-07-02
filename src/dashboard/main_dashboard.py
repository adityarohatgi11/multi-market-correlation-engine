"""
Multi-Market Correlation Engine - Main Dashboard
==============================================

Real-time web dashboard for monitoring and controlling the multi-agent
correlation analysis system.

Author: Multi-Market Correlation Engine Team
Version: 4.0.0
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.agents.agent_coordinator import AgentCoordinator
from src.data.database_manager import get_db_manager
from src.models.correlation_engine import CorrelationEngine
from src.dashboard.components.metrics_display import MetricsDisplay
from src.dashboard.components.correlation_heatmap import CorrelationHeatmap
from src.dashboard.components.agent_status import AgentStatusDisplay

# Configure Streamlit page
st.set_page_config(
page_title="Multi-Market Correlation Engine",
page_icon="",
layout="wide",
initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
.main-header {
font-size: 2.5rem;
font-weight: bold;
color: #1f77b4;
text-align: center;
margin-bottom: 2rem;
}
.metric-card {
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
padding: 1rem;
border-radius: 10px;
color: white;
margin: 0.5rem 0;
}
.status-healthy {
color: #28a745;
font-weight: bold;
}
.status-warning {
color: #ffc107;
font-weight: bold;
}
.status-error {
color: #dc3545;
font-weight: bold;
}
.sidebar-section {
background: #f8f9fa;
padding: 1rem;
border-radius: 5px;
margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

class DashboardApp:
"""Main dashboard application class."""

def __init__(self):
"""Initialize dashboard components."""
self.db_manager = None
self.correlation_engine = None
self.agent_coordinator = None
self.metrics_display = MetricsDisplay()
self.correlation_heatmap = CorrelationHeatmap()
self.agent_status = AgentStatusDisplay()

# Initialize session state
if 'initialized' not in st.session_state:
st.session_state.initialized = False
st.session_state.auto_refresh = True
st.session_state.refresh_interval = 30
st.session_state.selected_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

def initialize_components(self):
"""Initialize backend components."""
try:
self.db_manager = get_db_manager()
self.correlation_engine = CorrelationEngine()

# Initialize agent coordinator if not already done
if not st.session_state.initialized:
with st.spinner("Initializing multi-agent system..."):
config = {
'symbols': st.session_state.selected_symbols,
'enable_scheduling': False,
'auto_start_agents': True
}
self.agent_coordinator = AgentCoordinator(config)
self.agent_coordinator.start_system()
st.session_state.initialized = True
st.session_state.agent_coordinator = self.agent_coordinator
else:
self.agent_coordinator = st.session_state.get('agent_coordinator')

return True
except Exception as e:
st.error(f"Failed to initialize components: {e}")
return False

def render_header(self):
"""Render the main header."""
st.markdown('<h1 class="main-header"> Multi-Market Correlation Engine</h1>',
unsafe_allow_html=True)

# Status indicator
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
if st.session_state.initialized:
st.success("🟢 System Online - Real-time monitoring active")
else:
st.warning("🟡 System Initializing...")

def render_sidebar(self):
"""Render the sidebar controls."""
st.sidebar.title(" Control Panel")

# System Controls
st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
st.sidebar.subheader("System Controls")

# Auto-refresh toggle
st.session_state.auto_refresh = st.sidebar.checkbox(
"Auto Refresh",
value=st.session_state.auto_refresh
)

if st.session_state.auto_refresh:
st.session_state.refresh_interval = st.sidebar.slider(
"Refresh Interval (seconds)",
10, 300, st.session_state.refresh_interval
)

# Manual refresh button
if st.sidebar.button(" Refresh Now"):
st.rerun()

st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Symbol Selection
st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
st.sidebar.subheader("Symbol Selection")

available_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']
st.session_state.selected_symbols = st.sidebar.multiselect(
"Select Symbols",
available_symbols,
default=st.session_state.selected_symbols
)

st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Agent Controls
if st.session_state.initialized and self.agent_coordinator:
st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
st.sidebar.subheader("Agent Controls")

if st.sidebar.button(" Force Data Collection"):
with st.spinner("Triggering data collection..."):
try:
workflow_id = self.agent_coordinator.execute_workflow(
'data_collection_and_analysis',
{'symbols': st.session_state.selected_symbols}
)
st.sidebar.success(f"Workflow started: {workflow_id[:8]}...")
except Exception as e:
st.sidebar.error(f"Failed to start workflow: {e}")

if st.sidebar.button(" Force Analysis"):
with st.spinner("Triggering analysis..."):
try:
if 'analyzer' in self.agent_coordinator.agents:
task = self.agent_coordinator.agents['analyzer'].create_task(
"Manual Analysis",
{
'type': 'correlation_analysis',
'symbols': st.session_state.selected_symbols
}
)
st.sidebar.success(f"Analysis task created: {task.id[:8]}...")
except Exception as e:
st.sidebar.error(f"Failed to create analysis task: {e}")

st.sidebar.markdown('</div>', unsafe_allow_html=True)

def render_main_content(self):
"""Render the main dashboard content."""
if not st.session_state.initialized:
st.info("Please wait while the system initializes...")
return

# Key Metrics Row
st.subheader(" System Overview")
self.render_metrics_overview()

# Agent Status Row
st.subheader(" Agent Status")
self.render_agent_status()

# Correlation Analysis Row
st.subheader("🔗 Correlation Analysis")
self.render_correlation_analysis()

# Data Quality Row
st.subheader(" Data Quality")
self.render_data_quality()

def render_metrics_overview(self):
"""Render system metrics overview."""
col1, col2, col3, col4 = st.columns(4)

try:
# Get system status
if self.agent_coordinator:
status = self.agent_coordinator.get_system_status()

with col1:
st.metric(
label="Active Agents",
value=status.get('total_agents', 0),
delta=None
)

with col2:
completed_tasks = sum(
agent['metrics']['tasks_completed']
for agent in status.get('agents', {}).values()
)
st.metric(
label="Tasks Completed",
value=completed_tasks,
delta=None
)

with col3:
# Get latest data count
if self.db_manager:
data_count = len(self.db_manager.get_market_data(
symbols=st.session_state.selected_symbols,
limit=1000
))
st.metric(
label="Data Records",
value=data_count,
delta=None
)
else:
st.metric("Data Records", "N/A")

with col4:
st.metric(
label="System Status",
value=status.get('system_status', 'Unknown').title(),
delta=None
)
except Exception as e:
st.error(f"Error loading metrics: {e}")

def render_agent_status(self):
"""Render agent status information."""
if not self.agent_coordinator:
st.warning("Agent coordinator not available")
return

try:
status = self.agent_coordinator.get_system_status()
agents = status.get('agents', {})

col1, col2 = st.columns(2)

with col1:
st.subheader("Data Collection Agent")
if 'data_collector' in agents:
agent = agents['data_collector']
status_color = "status-healthy" if agent['status'] == 'running' else "status-error"
st.markdown(f'<p class="{status_color}">Status: {agent["status"].title()}</p>',
unsafe_allow_html=True)
st.write(f"Tasks Completed: {agent['metrics']['tasks_completed']}")
st.write(f"Queue Size: {agent.get('queue_size', 0)}")
else:
st.error("Data collection agent not found")

with col2:
st.subheader("Analysis Agent")
if 'analyzer' in agents:
agent = agents['analyzer']
status_color = "status-healthy" if agent['status'] == 'running' else "status-error"
st.markdown(f'<p class="{status_color}">Status: {agent["status"].title()}</p>',
unsafe_allow_html=True)
st.write(f"Tasks Completed: {agent['metrics']['tasks_completed']}")
st.write(f"Queue Size: {agent.get('queue_size', 0)}")
else:
st.error("Analysis agent not found")

except Exception as e:
st.error(f"Error loading agent status: {e}")

def render_correlation_analysis(self):
"""Render correlation analysis visualizations."""
try:
if not self.db_manager:
st.warning("Database manager not available")
return

# Get recent market data
data = self.db_manager.get_market_data(
symbols=st.session_state.selected_symbols,
limit=500
)

if data.empty:
st.warning("No data available for correlation analysis")
return

# Create correlation heatmap
col1, col2 = st.columns([2, 1])

with col1:
st.subheader("Correlation Heatmap")

# Pivot data for correlation calculation
pivot_data = data.pivot(index='date', columns='symbol', values='close')

if len(pivot_data.columns) > 1:
# Calculate correlation matrix
corr_matrix = pivot_data.corr()

# Create heatmap
fig = px.imshow(
corr_matrix,
labels=dict(x="Symbol", y="Symbol", color="Correlation"),
x=corr_matrix.columns,
y=corr_matrix.columns,
color_continuous_scale="RdBu_r",
aspect="auto"
)
fig.update_layout(
title="Asset Correlation Matrix",
width=600,
height=500
)
st.plotly_chart(fig, use_container_width=True)
else:
st.info("Need at least 2 symbols for correlation analysis")

with col2:
st.subheader("Correlation Stats")
if len(pivot_data.columns) > 1:
corr_matrix = pivot_data.corr()

# Get upper triangle (excluding diagonal)
mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
correlations = corr_matrix.where(mask).stack()

st.metric("Average Correlation", f"{correlations.mean():.3f}")
st.metric("Max Correlation", f"{correlations.max():.3f}")
st.metric("Min Correlation", f"{correlations.min():.3f}")
st.metric("Std Deviation", f"{correlations.std():.3f}")

# Show strongest correlations
st.subheader("Strongest Correlations")
top_corr = correlations.abs().nlargest(3)
for pair, corr in top_corr.items():
st.write(f"{pair[0]} - {pair[1]}: {corr:.3f}")

except Exception as e:
st.error(f"Error in correlation analysis: {e}")

def render_data_quality(self):
"""Render data quality metrics."""
try:
if not self.db_manager:
st.warning("Database manager not available")
return

# Get recent data for quality analysis
data = self.db_manager.get_market_data(
symbols=st.session_state.selected_symbols,
limit=1000
)

if data.empty:
st.warning("No data available for quality analysis")
return

col1, col2, col3 = st.columns(3)

with col1:
st.subheader("Data Completeness")

# Calculate completeness by symbol
completeness = data.groupby('symbol').apply(
lambda x: 1 - x.isnull().sum().sum() / (len(x) * len(x.columns))
)

fig = px.bar(
x=completeness.index,
y=completeness.values,
title="Data Completeness by Symbol",
labels={'x': 'Symbol', 'y': 'Completeness %'}
)
fig.update_layout(height=300)
st.plotly_chart(fig, use_container_width=True)

with col2:
st.subheader("Data Freshness")

# Calculate data freshness
latest_dates = data.groupby('symbol')['date'].max()
now = datetime.now()

freshness_hours = []
for symbol, latest_date in latest_dates.items():
if pd.notna(latest_date):
latest_dt = pd.to_datetime(latest_date)
hours_old = (now - latest_dt).total_seconds() / 3600
freshness_hours.append(hours_old)
else:
freshness_hours.append(999) # Very old

avg_freshness = np.mean(freshness_hours)
st.metric("Avg Data Age (hours)", f"{avg_freshness:.1f}")

# Show freshness by symbol
for symbol, hours in zip(latest_dates.index, freshness_hours):
if hours < 24:
status = "🟢"
elif hours < 72:
status = "🟡"
else:
status = "🔴"
st.write(f"{status} {symbol}: {hours:.1f}h")

with col3:
st.subheader("Data Volume")

# Show data volume by symbol
volume_counts = data.groupby('symbol').size()

fig = px.pie(
values=volume_counts.values,
names=volume_counts.index,
title="Data Distribution by Symbol"
)
fig.update_layout(height=300)
st.plotly_chart(fig, use_container_width=True)

except Exception as e:
st.error(f"Error in data quality analysis: {e}")

def run(self):
"""Run the main dashboard application."""
# Render sidebar
self.render_sidebar()

# Initialize components
if self.initialize_components():
# Render main content
self.render_header()
self.render_main_content()

# Auto-refresh logic
if st.session_state.auto_refresh:
time.sleep(st.session_state.refresh_interval)
st.rerun()
else:
st.error("Failed to initialize dashboard components")

# Run the dashboard
if __name__ == "__main__":
app = DashboardApp()
app.run()
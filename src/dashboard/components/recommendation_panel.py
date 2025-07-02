"""
Asset Recommendation Panel Component
===================================

Streamlit component for asset recommendations and portfolio management.

Author: Multi-Market Correlation Engine Team
Version: 1.0.0
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Any, Optional
import requests
import json
from datetime import datetime, timedelta

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models.recommendation_engine import AssetRecommendationEngine
from src.agents.recommendation_agent import RecommendationAgent


class RecommendationPanel:
"""Interactive recommendation panel for Streamlit dashboard."""

def __init__(self):
"""Initialize the recommendation panel."""
self.recommendation_engine = AssetRecommendationEngine()
self.recommendation_agent = RecommendationAgent()

# Initialize session state
if 'current_portfolio' not in st.session_state:
st.session_state.current_portfolio = {}
if 'recommendation_history' not in st.session_state:
st.session_state.recommendation_history = []
if 'selected_strategy' not in st.session_state:
st.session_state.selected_strategy = 'balanced'

def render(self):
"""Render the complete recommendation panel."""
st.header(" Asset Recommendation Engine")

# Create tabs for different functionalities
tab1, tab2, tab3, tab4, tab5 = st.tabs([
" Recommendations",
" Portfolio Analysis",
"⚖ Optimization",
" Risk Assessment",
" Performance"
])

with tab1:
self._render_recommendations_tab()

with tab2:
self._render_portfolio_analysis_tab()

with tab3:
self._render_optimization_tab()

with tab4:
self._render_risk_assessment_tab()

with tab5:
self._render_performance_tab()

def _render_recommendations_tab(self):
"""Render the recommendations tab."""
st.subheader(" Generate Asset Recommendations")

# Portfolio input section
col1, col2 = st.columns([2, 1])

with col1:
st.markdown("### Current Portfolio")

# Portfolio input methods
input_method = st.radio(
"Portfolio Input Method:",
["Manual Entry", "Upload CSV", "Use Sample Portfolio"],
horizontal=True
)

if input_method == "Manual Entry":
portfolio = self._manual_portfolio_input()
elif input_method == "Upload CSV":
portfolio = self._csv_portfolio_input()
else:
portfolio = self._sample_portfolio_input()

st.session_state.current_portfolio = portfolio

with col2:
st.markdown("### Strategy Settings")

# Strategy selection
strategies = {
'conservative': ' Conservative',
'balanced': '⚖ Balanced',
'aggressive': ' Aggressive',
'diversified': ' Diversified'
}

strategy = st.selectbox(
"Investment Strategy:",
options=list(strategies.keys()),
format_func=lambda x: strategies[x],
index=1
)
st.session_state.selected_strategy = strategy

# Time horizon
horizon = st.selectbox(
"Investment Horizon:",
['1D', '1W', '1M', '3M', '6M', '1Y'],
index=2
)

# Asset universe
universe_options = st.multiselect(
"Asset Universe (leave empty for default):",
['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA',
'JPM', 'JNJ', 'V', 'WMT', 'PG', 'HD', 'MA', 'UNH'],
default=[]
)

universe = universe_options if universe_options else None

# Generate recommendations button
if st.button(" Generate Recommendations", type="primary"):
with st.spinner("Generating recommendations..."):
recommendations = self._generate_recommendations(
portfolio, universe, strategy, horizon
)

if recommendations and 'error' not in recommendations:
st.session_state.last_recommendations = recommendations
st.success(" Recommendations generated successfully!")
else:
st.error(f" Error: {recommendations.get('error', 'Unknown error')}")

# Display recommendations
if hasattr(st.session_state, 'last_recommendations'):
self._display_recommendations(st.session_state.last_recommendations)

def _render_portfolio_analysis_tab(self):
"""Render the portfolio analysis tab."""
st.subheader(" Portfolio Analysis")

if not st.session_state.current_portfolio:
st.info("Please enter a portfolio in the Recommendations tab first.")
return

col1, col2 = st.columns(2)

with col1:
st.markdown("### Portfolio Composition")

# Portfolio pie chart
portfolio_df = pd.DataFrame(
list(st.session_state.current_portfolio.items()),
columns=['Symbol', 'Weight']
)

fig = px.pie(
portfolio_df,
values='Weight',
names='Symbol',
title="Current Portfolio Allocation"
)
st.plotly_chart(fig, use_container_width=True)

with col2:
st.markdown("### Portfolio Metrics")

if st.button(" Analyze Portfolio"):
with st.spinner("Analyzing portfolio..."):
analysis = self._analyze_portfolio(st.session_state.current_portfolio)

if analysis and 'error' not in analysis:
self._display_portfolio_metrics(analysis)
else:
st.error(f"Analysis failed: {analysis.get('error', 'Unknown error')}")

def _render_optimization_tab(self):
"""Render the optimization tab."""
st.subheader("⚖ Portfolio Optimization")

if not st.session_state.current_portfolio:
st.info("Please enter a portfolio in the Recommendations tab first.")
return

col1, col2 = st.columns([1, 2])

with col1:
st.markdown("### Optimization Settings")

optimization_method = st.selectbox(
"Optimization Method:",
['mean_variance', 'risk_parity'],
format_func=lambda x: 'Mean-Variance' if x == 'mean_variance' else 'Risk Parity'
)

if optimization_method == 'mean_variance':
target_return = st.slider(
"Target Annual Return:",
min_value=0.0,
max_value=0.30,
value=0.10,
step=0.01,
format="%.2f"
)
else:
target_return = None

if st.button(" Optimize Portfolio"):
with st.spinner("Optimizing portfolio..."):
optimization_result = self._optimize_portfolio(
st.session_state.current_portfolio,
optimization_method,
target_return
)

if optimization_result and 'error' not in optimization_result:
st.session_state.optimization_result = optimization_result
st.success(" Portfolio optimized successfully!")
else:
st.error(f"Optimization failed: {optimization_result.get('error', 'Unknown error')}")

with col2:
st.markdown("### Optimization Results")

if hasattr(st.session_state, 'optimization_result'):
self._display_optimization_results(st.session_state.optimization_result)

def _render_risk_assessment_tab(self):
"""Render the risk assessment tab."""
st.subheader(" Risk Assessment")

if not st.session_state.current_portfolio:
st.info("Please enter a portfolio in the Recommendations tab first.")
return

# Risk measures selection
risk_measures = st.multiselect(
"Select Risk Measures:",
['var', 'cvar', 'max_drawdown', 'volatility'],
default=['var', 'cvar', 'max_drawdown']
)

if st.button(" Assess Risk"):
with st.spinner("Assessing portfolio risk..."):
risk_assessment = self._assess_portfolio_risk(
st.session_state.current_portfolio,
risk_measures
)

if risk_assessment and 'error' not in risk_assessment:
self._display_risk_assessment(risk_assessment)
else:
st.error(f"Risk assessment failed: {risk_assessment.get('error', 'Unknown error')}")

def _render_performance_tab(self):
"""Render the performance tracking tab."""
st.subheader(" Performance Tracking")

col1, col2 = st.columns(2)

with col1:
st.markdown("### Recommendation History")

if st.session_state.recommendation_history:
history_df = pd.DataFrame(st.session_state.recommendation_history)
st.dataframe(history_df, use_container_width=True)
else:
st.info("No recommendation history available.")

with col2:
st.markdown("### Performance Metrics")

if st.button(" Generate Performance Report"):
# Placeholder for performance analysis
st.info("Performance tracking feature coming soon!")

def _manual_portfolio_input(self) -> Dict[str, float]:
"""Handle manual portfolio input."""
portfolio = {}

# Number of assets
num_assets = st.number_input("Number of assets:", min_value=1, max_value=20, value=3)

# Asset input
for i in range(num_assets):
col1, col2 = st.columns(2)
with col1:
symbol = st.text_input(f"Asset {i+1} Symbol:", key=f"symbol_{i}", value=f"AAPL" if i == 0 else "")
with col2:
weight = st.number_input(f"Weight:", min_value=0.0, max_value=1.0, value=0.0, key=f"weight_{i}")

if symbol and weight > 0:
portfolio[symbol.upper()] = weight

# Normalize weights
if portfolio:
total_weight = sum(portfolio.values())
if total_weight > 0:
portfolio = {k: v/total_weight for k, v in portfolio.items()}

# Display normalized weights
st.info(f"Portfolio normalized. Total weight: {sum(portfolio.values()):.3f}")

return portfolio

def _csv_portfolio_input(self) -> Dict[str, float]:
"""Handle CSV portfolio input."""
uploaded_file = st.file_uploader("Upload portfolio CSV", type=['csv'])

if uploaded_file is not None:
try:
df = pd.read_csv(uploaded_file)

# Expect columns: Symbol, Weight
if 'Symbol' in df.columns and 'Weight' in df.columns:
portfolio = dict(zip(df['Symbol'], df['Weight']))

# Normalize weights
total_weight = sum(portfolio.values())
if total_weight > 0:
portfolio = {k: v/total_weight for k, v in portfolio.items()}

st.success(f"Loaded portfolio with {len(portfolio)} assets")
return portfolio
else:
st.error("CSV must have 'Symbol' and 'Weight' columns")
except Exception as e:
st.error(f"Error reading CSV: {e}")

return {}

def _sample_portfolio_input(self) -> Dict[str, float]:
"""Provide sample portfolio options."""
sample_portfolios = {
"Tech Heavy": {"AAPL": 0.3, "MSFT": 0.25, "GOOGL": 0.2, "AMZN": 0.15, "TSLA": 0.1},
"Diversified": {"AAPL": 0.2, "JPM": 0.2, "JNJ": 0.2, "WMT": 0.2, "HD": 0.2},
"Growth": {"TSLA": 0.25, "NVDA": 0.25, "META": 0.25, "GOOGL": 0.25},
"Defensive": {"JNJ": 0.3, "PG": 0.25, "WMT": 0.25, "V": 0.2}
}

selected_sample = st.selectbox(
"Choose sample portfolio:",
list(sample_portfolios.keys())
)

return sample_portfolios[selected_sample]

def _generate_recommendations(self, portfolio: Dict[str, float], universe: Optional[List[str]],
strategy: str, horizon: str) -> Dict[str, Any]:
"""Generate asset recommendations."""
try:
recommendations = self.recommendation_engine.generate_recommendations(
portfolio=portfolio,
universe=universe or ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'JNJ', 'V'],
horizon=horizon,
strategy=strategy
)

# Store in history
if 'error' not in recommendations:
history_entry = {
'timestamp': datetime.now().isoformat(),
'strategy': strategy,
'horizon': horizon,
'buy_signals': len(recommendations.get('buy_signals', [])),
'sell_signals': len(recommendations.get('sell_signals', [])),
'risk_level': recommendations.get('risk_assessment', {}).get('overall_risk_level', 'unknown')
}
st.session_state.recommendation_history.append(history_entry)

return recommendations

except Exception as e:
return {'error': str(e)}

def _analyze_portfolio(self, portfolio: Dict[str, float]) -> Dict[str, Any]:
"""Analyze portfolio performance."""
try:
from src.agents.base_agent import Task, TaskPriority

task_data = {
'type': 'analyze_portfolio',
'portfolio': portfolio,
'benchmark': 'SPY'
}

task = Task(
task_id=f"analyze_{len(portfolio)}",
task_type="analyze_portfolio",
priority=TaskPriority.MEDIUM,
data=task_data
)

return self.recommendation_agent._handle_task(task)

except Exception as e:
return {'error': str(e)}

def _optimize_portfolio(self, portfolio: Dict[str, float], method: str,
target_return: Optional[float]) -> Dict[str, Any]:
"""Optimize portfolio allocation."""
try:
from src.agents.base_agent import Task, TaskPriority

task_data = {
'type': 'optimize_portfolio',
'portfolio': portfolio,
'method': method,
'target_return': target_return
}

task = Task(
task_id=f"optimize_{method}",
task_type="optimize_portfolio",
priority=TaskPriority.HIGH,
data=task_data
)

return self.recommendation_agent._handle_task(task)

except Exception as e:
return {'error': str(e)}

def _assess_portfolio_risk(self, portfolio: Dict[str, float],
risk_measures: List[str]) -> Dict[str, Any]:
"""Assess portfolio risk."""
try:
from src.agents.base_agent import Task, TaskPriority

task_data = {
'type': 'risk_assessment',
'portfolio': portfolio,
'risk_measures': risk_measures
}

task = Task(
task_id=f"risk_{len(portfolio)}",
task_type="risk_assessment",
priority=TaskPriority.HIGH,
data=task_data
)

return self.recommendation_agent._handle_task(task)

except Exception as e:
return {'error': str(e)}

def _display_recommendations(self, recommendations: Dict[str, Any]):
"""Display recommendation results."""
st.markdown("### Recommendation Results")

# Summary metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
buy_count = len(recommendations.get('buy_signals', []))
st.metric("Buy Signals", buy_count)

with col2:
sell_count = len(recommendations.get('sell_signals', []))
st.metric("Sell Signals", sell_count)

with col3:
hold_count = len(recommendations.get('hold_signals', []))
st.metric("Hold Signals", hold_count)

with col4:
risk_level = recommendations.get('risk_assessment', {}).get('overall_risk_level', 'unknown')
st.metric("Risk Level", risk_level.upper())

# Detailed signals
if buy_count > 0:
st.markdown("#### Buy Signals")
buy_df = pd.DataFrame(recommendations['buy_signals'])
st.dataframe(buy_df, use_container_width=True)

if sell_count > 0:
st.markdown("#### Sell Signals")
sell_df = pd.DataFrame(recommendations['sell_signals'])
st.dataframe(sell_df, use_container_width=True)

# Optimal weights visualization
optimal_weights = recommendations.get('optimal_weights', {})
if optimal_weights:
st.markdown("#### Optimal Portfolio Allocation")

weights_df = pd.DataFrame(
list(optimal_weights.items()),
columns=['Symbol', 'Weight']
)

fig = px.bar(
weights_df,
x='Symbol',
y='Weight',
title="Recommended Portfolio Weights"
)
st.plotly_chart(fig, use_container_width=True)

# Summary text
if 'summary' in recommendations:
st.markdown("#### Summary")
st.info(recommendations['summary'])

def _display_portfolio_metrics(self, analysis: Dict[str, Any]):
"""Display portfolio analysis metrics."""
if 'portfolio_metrics' in analysis:
metrics = analysis['portfolio_metrics']

col1, col2, col3 = st.columns(3)

with col1:
st.metric("Annual Return", f"{metrics.get('annual_return', 0):.2%}")
st.metric("Sharpe Ratio", f"{metrics.get('sharpe_ratio', 0):.3f}")

with col2:
st.metric("Annual Volatility", f"{metrics.get('annual_volatility', 0):.2%}")
st.metric("Max Drawdown", f"{metrics.get('max_drawdown', 0):.2%}")

with col3:
st.metric("VaR (95%)", f"{metrics.get('var_95', 0):.2%}")
st.metric("CVaR (95%)", f"{metrics.get('cvar_95', 0):.2%}")

def _display_optimization_results(self, result: Dict[str, Any]):
"""Display portfolio optimization results."""
optimal_weights = result.get('optimal_weights', {})

if optimal_weights:
# Comparison chart
current_portfolio = st.session_state.current_portfolio

comparison_data = []
for symbol in set(list(current_portfolio.keys()) + list(optimal_weights.keys())):
comparison_data.append({
'Symbol': symbol,
'Current': current_portfolio.get(symbol, 0),
'Optimal': optimal_weights.get(symbol, 0)
})

comparison_df = pd.DataFrame(comparison_data)

fig = px.bar(
comparison_df,
x='Symbol',
y=['Current', 'Optimal'],
title="Current vs Optimal Portfolio Allocation",
barmode='group'
)
st.plotly_chart(fig, use_container_width=True)

# Portfolio metrics
if 'portfolio_metrics' in result:
self._display_portfolio_metrics(result)

def _display_risk_assessment(self, assessment: Dict[str, Any]):
"""Display risk assessment results."""
risk_level = assessment.get('risk_level', 'unknown')
risk_score = assessment.get('composite_risk_score', 0)

col1, col2 = st.columns(2)

with col1:
st.metric("Risk Level", risk_level.upper())
st.metric("Risk Score", f"{risk_score:.3f}")

with col2:
# Risk gauge
fig = go.Figure(go.Indicator(
mode = "gauge+number",
value = risk_score,
domain = {'x': [0, 1], 'y': [0, 1]},
title = {'text': "Risk Score"},
gauge = {
'axis': {'range': [None, 1]},
'bar': {'color': "darkblue"},
'steps': [
{'range': [0, 0.4], 'color': "lightgreen"},
{'range': [0.4, 0.7], 'color': "yellow"},
{'range': [0.7, 1], 'color': "red"}
],
'threshold': {
'line': {'color': "red", 'width': 4},
'thickness': 0.75,
'value': 0.8
}
}
))
st.plotly_chart(fig, use_container_width=True)

# Risk recommendations
recommendations = assessment.get('recommendations', [])
if recommendations:
st.markdown("#### Risk Management Recommendations")
for rec in recommendations:
st.info(rec)
"""
Visualization Utilities
=======================

Plotting utilities for market data and correlation analysis.

Author: Multi-Market Correlation Engine Team
Version: 0.1.0
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns

class CorrelationPlotter:
"""Correlation visualization utilities."""

@staticmethod
def plot_correlation_heatmap(corr_matrix, title="Correlation Matrix"):
"""Create correlation heatmap using plotly."""
fig = px.imshow(
corr_matrix,
text_auto='.3f',
aspect="auto",
color_continuous_scale='RdBu_r',
color_continuous_midpoint=0,
title=title
)

fig.update_layout(
title_x=0.5,
width=600,
height=500
)

return fig

@staticmethod
def plot_rolling_correlations(rolling_corr_dict, title="Rolling Correlations"):
"""Plot rolling correlations over time."""
fig = go.Figure()

for pair_name, corr_series in rolling_corr_dict.items():
fig.add_trace(go.Scatter(
x=corr_series.index,
y=corr_series.values,
mode='lines',
name=pair_name.replace('_', ' vs '),
line=dict(width=2)
))

fig.update_layout(
title=title,
xaxis_title="Date",
yaxis_title="Correlation",
hovermode='x unified'
)

return fig

class PricePlotter:
"""Price and return visualization utilities."""

@staticmethod
def plot_price_series(price_data, title="Price Series"):
"""Plot normalized price series."""
# Normalize to 100
normalized_prices = price_data.div(price_data.iloc[0]) * 100

fig = go.Figure()

for symbol in normalized_prices.columns:
fig.add_trace(go.Scatter(
x=normalized_prices.index,
y=normalized_prices[symbol],
mode='lines',
name=symbol,
line=dict(width=2)
))

fig.update_layout(
title=title,
xaxis_title="Date",
yaxis_title="Normalized Price (Base=100)",
hovermode='x unified'
)

return fig

if __name__ == "__main__":
print(" Visualization utilities created successfully!")

"""
Correlation Heatmap Component
============================

Advanced correlation visualization component with interactive features.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Any


class CorrelationHeatmap:
    """Component for advanced correlation visualizations."""
    
    def __init__(self):
        """Initialize correlation heatmap component."""
        pass
    
    def render_interactive_heatmap(self, correlation_matrix: pd.DataFrame):
        """Render interactive correlation heatmap."""
        if correlation_matrix.empty:
            st.warning("No correlation data available")
            return
        
        # Create interactive heatmap
        fig = px.imshow(
            correlation_matrix,
            labels=dict(x="Asset", y="Asset", color="Correlation"),
            x=correlation_matrix.columns,
            y=correlation_matrix.columns,
            color_continuous_scale="RdBu_r",
            aspect="auto",
            zmin=-1,
            zmax=1
        )
        
        # Add text annotations
        fig.update_traces(
            text=correlation_matrix.round(3),
            texttemplate="%{text}",
            textfont={"size": 10}
        )
        
        fig.update_layout(
            title="Asset Correlation Matrix",
            width=600,
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_correlation_network(self, correlation_matrix: pd.DataFrame, threshold: float = 0.5):
        """Render correlation network graph."""
        if correlation_matrix.empty:
            st.warning("No correlation data available")
            return
        
        # Create network data
        assets = correlation_matrix.columns.tolist()
        edges = []
        edge_weights = []
        
        for i, asset1 in enumerate(assets):
            for j, asset2 in enumerate(assets):
                if i < j:  # Avoid duplicates
                    corr = correlation_matrix.loc[asset1, asset2]
                    if abs(corr) >= threshold:
                        edges.append((asset1, asset2))
                        edge_weights.append(abs(corr))
        
        if not edges:
            st.info(f"No correlations above threshold {threshold}")
            return
        
        # Create network visualization
        # This is a simplified version - in production, you'd use networkx or similar
        st.subheader(f"Correlation Network (threshold: {threshold})")
        
        # Display as a table for now
        network_data = pd.DataFrame({
            'Asset 1': [edge[0] for edge in edges],
            'Asset 2': [edge[1] for edge in edges],
            'Correlation': [correlation_matrix.loc[edge[0], edge[1]] for edge in edges]
        })
        
        st.dataframe(network_data.sort_values('Correlation', key=abs, ascending=False))
    
    def render_rolling_correlations(self, data: pd.DataFrame, window: int = 30):
        """Render rolling correlation chart."""
        if data.empty or len(data.columns) < 2:
            st.warning("Need at least 2 assets for rolling correlation")
            return
        
        # Calculate rolling correlations for first two assets
        assets = data.columns[:2]
        rolling_corr = data[assets[0]].rolling(window=window).corr(data[assets[1]])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=rolling_corr,
            mode='lines',
            name=f'{assets[0]} - {assets[1]} ({window}d rolling)',
            line=dict(color='blue')
        ))
        
        fig.update_layout(
            title=f"Rolling Correlation: {assets[0]} vs {assets[1]}",
            xaxis_title="Date",
            yaxis_title="Correlation",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_correlation_distribution(self, correlation_matrix: pd.DataFrame):
        """Render correlation distribution histogram."""
        if correlation_matrix.empty:
            st.warning("No correlation data available")
            return
        
        # Get upper triangle correlations (excluding diagonal)
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool), k=1)
        correlations = correlation_matrix.where(mask).stack()
        
        fig = px.histogram(
            x=correlations,
            nbins=20,
            title="Distribution of Asset Correlations",
            labels={'x': 'Correlation', 'y': 'Frequency'}
        )
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Show statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Mean Correlation", f"{correlations.mean():.3f}")
        with col2:
            st.metric("Median Correlation", f"{correlations.median():.3f}")
        with col3:
            st.metric("Std Deviation", f"{correlations.std():.3f}") 
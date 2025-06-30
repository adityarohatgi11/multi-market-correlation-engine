"""
Metrics Display Component
========================

Component for displaying system metrics and KPIs in the dashboard.
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Any


class MetricsDisplay:
    """Component for displaying system metrics."""
    
    def __init__(self):
        """Initialize metrics display component."""
        pass
    
    def render_kpi_cards(self, metrics: Dict[str, Any]):
        """Render KPI cards with metrics."""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="System Uptime",
                value=metrics.get('uptime', 'N/A'),
                delta=None
            )
        
        with col2:
            st.metric(
                label="Data Quality Score",
                value=f"{metrics.get('data_quality', 0):.2f}",
                delta=metrics.get('quality_delta', 0)
            )
        
        with col3:
            st.metric(
                label="API Response Time",
                value=f"{metrics.get('response_time', 0):.0f}ms",
                delta=metrics.get('response_delta', 0)
            )
        
        with col4:
            st.metric(
                label="Active Connections",
                value=metrics.get('connections', 0),
                delta=metrics.get('connection_delta', 0)
            )
    
    def render_performance_chart(self, performance_data: List[Dict]):
        """Render performance metrics chart."""
        if not performance_data:
            st.info("No performance data available")
            return
        
        fig = go.Figure()
        
        # Add response time trace
        timestamps = [item['timestamp'] for item in performance_data]
        response_times = [item['response_time'] for item in performance_data]
        
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=response_times,
            mode='lines+markers',
            name='Response Time (ms)',
            line=dict(color='blue')
        ))
        
        fig.update_layout(
            title="System Performance Over Time",
            xaxis_title="Time",
            yaxis_title="Response Time (ms)",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_system_health(self, health_data: Dict[str, Any]):
        """Render system health indicators."""
        st.subheader("System Health")
        
        # Overall health status
        overall_health = health_data.get('overall_healthy', False)
        if overall_health:
            st.success("🟢 All systems operational")
        else:
            st.error("🔴 System issues detected")
        
        # Component health
        components = health_data.get('components', {})
        for component, status in components.items():
            if status.get('healthy', False):
                st.success(f"✅ {component}: Healthy")
            else:
                st.error(f"❌ {component}: {status.get('error', 'Unknown error')}") 
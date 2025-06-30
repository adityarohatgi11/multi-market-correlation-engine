"""
Agent Status Display Component
=============================

Component for displaying multi-agent system status and controls.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from typing import Dict, List, Any


class AgentStatusDisplay:
    """Component for displaying agent system status."""
    
    def __init__(self):
        """Initialize agent status display component."""
        pass
    
    def render_agent_overview(self, agents_status: Dict[str, Any]):
        """Render overview of all agents."""
        if not agents_status:
            st.warning("No agent status data available")
            return
        
        # Create agent status cards
        cols = st.columns(len(agents_status))
        
        for idx, (agent_name, status) in enumerate(agents_status.items()):
            with cols[idx]:
                self._render_agent_card(agent_name, status)
    
    def _render_agent_card(self, agent_name: str, status: Dict[str, Any]):
        """Render individual agent status card."""
        # Determine status color
        agent_status = status.get('status', 'unknown')
        if agent_status == 'running':
            status_color = "#28a745"  # Green
            status_icon = "🟢"
        elif agent_status == 'stopped':
            status_color = "#dc3545"  # Red
            status_icon = "🔴"
        else:
            status_color = "#ffc107"  # Yellow
            status_icon = "🟡"
        
        # Agent card
        st.markdown(f"""
        <div style="
            border: 2px solid {status_color};
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem 0;
            background: linear-gradient(135deg, {status_color}22 0%, {status_color}11 100%);
        ">
            <h4>{status_icon} {agent_name.replace('_', ' ').title()}</h4>
            <p><strong>Status:</strong> {agent_status.title()}</p>
            <p><strong>Tasks:</strong> {status.get('metrics', {}).get('tasks_completed', 0)}</p>
            <p><strong>Queue:</strong> {status.get('queue_size', 0)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_task_metrics(self, agents_status: Dict[str, Any]):
        """Render task execution metrics."""
        if not agents_status:
            return
        
        # Collect task metrics
        agent_names = []
        tasks_completed = []
        tasks_failed = []
        
        for agent_name, status in agents_status.items():
            metrics = status.get('metrics', {})
            agent_names.append(agent_name.replace('_', ' ').title())
            tasks_completed.append(metrics.get('tasks_completed', 0))
            tasks_failed.append(metrics.get('tasks_failed', 0))
        
        # Create task metrics chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Completed',
            x=agent_names,
            y=tasks_completed,
            marker_color='green'
        ))
        
        fig.add_trace(go.Bar(
            name='Failed',
            x=agent_names,
            y=tasks_failed,
            marker_color='red'
        ))
        
        fig.update_layout(
            title="Task Execution by Agent",
            xaxis_title="Agent",
            yaxis_title="Number of Tasks",
            barmode='group',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_agent_timeline(self, agent_activities: List[Dict[str, Any]]):
        """Render agent activity timeline."""
        if not agent_activities:
            st.info("No agent activity data available")
            return
        
        # Create timeline chart
        fig = go.Figure()
        
        for activity in agent_activities:
            fig.add_trace(go.Scatter(
                x=[activity['timestamp']],
                y=[activity['agent']],
                mode='markers',
                marker=dict(
                    size=10,
                    color=self._get_activity_color(activity['type'])
                ),
                text=activity['description'],
                name=activity['type']
            ))
        
        fig.update_layout(
            title="Agent Activity Timeline",
            xaxis_title="Time",
            yaxis_title="Agent",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _get_activity_color(self, activity_type: str) -> str:
        """Get color for activity type."""
        color_map = {
            'task_started': 'blue',
            'task_completed': 'green',
            'task_failed': 'red',
            'agent_started': 'purple',
            'agent_stopped': 'orange',
            'data_collected': 'cyan',
            'analysis_completed': 'magenta'
        }
        return color_map.get(activity_type, 'gray')
    
    def render_performance_metrics(self, agents_status: Dict[str, Any]):
        """Render agent performance metrics."""
        if not agents_status:
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Response Times")
            
            # Collect response time data
            agent_names = []
            avg_times = []
            
            for agent_name, status in agents_status.items():
                metrics = status.get('metrics', {})
                agent_names.append(agent_name.replace('_', ' ').title())
                avg_times.append(metrics.get('average_task_time', 0))
            
            if any(avg_times):
                fig = px.bar(
                    x=agent_names,
                    y=avg_times,
                    title="Average Task Execution Time",
                    labels={'x': 'Agent', 'y': 'Time (seconds)'}
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No timing data available")
        
        with col2:
            st.subheader("Error Rates")
            
            # Collect error rate data
            error_rates = []
            
            for agent_name, status in agents_status.items():
                metrics = status.get('metrics', {})
                completed = metrics.get('tasks_completed', 0)
                failed = metrics.get('tasks_failed', 0)
                total = completed + failed
                
                if total > 0:
                    error_rate = (failed / total) * 100
                else:
                    error_rate = 0
                
                error_rates.append(error_rate)
            
            if any(error_rates):
                fig = px.bar(
                    x=agent_names,
                    y=error_rates,
                    title="Task Error Rate",
                    labels={'x': 'Agent', 'y': 'Error Rate (%)'}
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No error data available")
    
    def render_agent_controls(self, agent_coordinator):
        """Render agent control buttons."""
        if not agent_coordinator:
            st.warning("Agent coordinator not available")
            return
        
        st.subheader("Agent Controls")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Start All Agents"):
                try:
                    agent_coordinator.start_system()
                    st.success("All agents started")
                except Exception as e:
                    st.error(f"Failed to start agents: {e}")
        
        with col2:
            if st.button("⏸️ Stop All Agents"):
                try:
                    agent_coordinator.stop_system()
                    st.success("All agents stopped")
                except Exception as e:
                    st.error(f"Failed to stop agents: {e}")
        
        with col3:
            if st.button("🔄 Restart System"):
                try:
                    agent_coordinator.stop_system()
                    agent_coordinator.start_system()
                    st.success("System restarted")
                except Exception as e:
                    st.error(f"Failed to restart system: {e}") 
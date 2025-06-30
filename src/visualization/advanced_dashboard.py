"""
Advanced Dashboard Implementation
================================

Advanced Streamlit dashboard with GARCH, VAR, ML, and Network Analysis.

Author: Multi-Market Correlation Engine Team
Version: 0.1.0
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import date, datetime, timedelta
import warnings
import sys
import os

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.config.config_manager import get_config
from src.data.database_manager import get_db_manager
from src.collectors.yahoo_finance_collector import YahooFinanceCollector
from src.models.correlation_engine import CorrelationEngine
from src.models.garch_models import GARCHAnalyzer
from src.models.var_models import VARAnalyzer
from src.models.ml_models import MLCorrelationPredictor, RegimeDetector
from src.models.network_analysis import NetworkAnalyzer

warnings.filterwarnings("ignore")

# Page configuration
st.set_page_config(
    page_title="Multi-Market Correlation Engine - Advanced Analytics",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
        background: linear-gradient(90deg, #1E3A8A, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .section-header {
        font-size: 1.8rem;
        color: #1F2937;
        margin: 1.5rem 0 1rem 0;
        border-left: 4px solid #3B82F6;
        padding-left: 1rem;
    }
    .metric-container {
        background: linear-gradient(135deg, #F8FAFC, #E2E8F0);
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #CBD5E1;
        margin: 0.5rem 0;
    }
    .stButton > button {
        background: linear-gradient(90deg, #3B82F6, #1E40AF);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
    .status-success {
        background-color: #D1FAE5;
        color: #065F46;
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 4px solid #10B981;
    }
    .status-warning {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 4px solid #F59E0B;
    }
    .status-error {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 4px solid #EF4444;
    }
</style>
""", unsafe_allow_html=True)

def initialize_components():
    """Initialize all analysis components."""
    try:
        components = {
            'config': get_config(),
            'db_manager': get_db_manager(),
            'collector': YahooFinanceCollector(),
            'correlation_analyzer': CorrelationEngine(),
            'garch_analyzer': GARCHAnalyzer(),
            'var_analyzer': VARAnalyzer(),
            'ml_predictor': MLCorrelationPredictor(),
            'regime_detector': RegimeDetector(),
            'network_analyzer': NetworkAnalyzer()
        }
        return components
    except Exception as e:
        st.error(f"Failed to initialize components: {e}")
        return None

def main():
    """Main dashboard application."""
    
    # Header
    st.markdown('<h1 class="main-header">🚀 Multi-Market Correlation Engine</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align: center; color: #6B7280;">Advanced Analytics Dashboard - Phase 2</h3>', unsafe_allow_html=True)
    
    # Initialize components
    components = initialize_components()
    if not components:
        st.error("Failed to initialize system components")
        return
    
    # Sidebar configuration
    st.sidebar.header("🎛️ Analysis Configuration")
    
    # Analysis type selection
    analysis_type = st.sidebar.selectbox(
        "Select Analysis Type",
        ["📊 Overview", "📈 GARCH Models", "🔄 VAR Analysis", "🤖 Machine Learning", "🌐 Network Analysis", "🎯 Regime Detection"]
    )
    
    # Symbol selection
    st.sidebar.subheader("📈 Asset Selection")
    
    # Available symbols
    available_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "JPM", "BAC", "GS", "XOM", "CVX", "JNJ", "PFE"]
    
    # Predefined symbol groups (only using available symbols)
    symbol_groups = {
        "Tech Stocks": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],
        "Financial": ["JPM", "BAC", "GS"],
        "Energy": ["XOM", "CVX"],
        "Healthcare": ["JNJ", "PFE"],
        "Mixed Portfolio": ["AAPL", "MSFT", "JPM", "XOM", "JNJ"]
    }
    
    # Ensure all symbols in groups are available
    for group_name, group_symbols in symbol_groups.items():
        symbol_groups[group_name] = [s for s in group_symbols if s in available_symbols]
    
    selected_group = st.sidebar.selectbox("Choose Symbol Group", list(symbol_groups.keys()))
    default_symbols = symbol_groups[selected_group]
    
    symbols = st.sidebar.multiselect(
        "Select Symbols",
        options=available_symbols,
        default=default_symbols,
        help="Choose 2-5 symbols for analysis"
    )
    
    # Date range selection
    st.sidebar.subheader("📅 Date Range")
    end_date = st.sidebar.date_input("End Date", date.today())
    start_date = st.sidebar.date_input("Start Date", end_date - timedelta(days=365))
    
    if start_date >= end_date:
        st.sidebar.error("Start date must be before end date")
        return
    
    if len(symbols) < 2:
        st.warning("Please select at least 2 symbols for analysis")
        return
    
    # Data collection section
    st.sidebar.subheader("📊 Data Management")
    if st.sidebar.button("🔄 Collect Fresh Data", help="Collect latest market data"):
        with st.spinner("Collecting market data..."):
            try:
                collector = components['collector']
                end_date_collect = date.today()
                start_date_collect = end_date_collect - timedelta(days=730)  # 2 years
                results = collector.collect_batch(symbols, start_date_collect, end_date_collect)
                
                if results:
                    success_count = sum(1 for r in results if r.success)
                    st.sidebar.success(f"✅ Collected data for {success_count}/{len(symbols)} symbols")
                else:
                    st.sidebar.error("❌ Failed to collect data")
            except Exception as e:
                st.sidebar.error(f"❌ Data collection error: {e}")
    
    # Main content based on analysis type
    if analysis_type == "📊 Overview":
        show_overview(components, symbols, start_date, end_date)
    elif analysis_type == "📈 GARCH Models":
        show_garch_analysis(components, symbols, start_date, end_date)
    elif analysis_type == "🔄 VAR Analysis":
        show_var_analysis(components, symbols, start_date, end_date)
    elif analysis_type == "�� Machine Learning":
        show_ml_analysis(components, symbols, start_date, end_date)
    elif analysis_type == "🌐 Network Analysis":
        show_network_analysis(components, symbols, start_date, end_date)
    elif analysis_type == "🎯 Regime Detection":
        show_regime_analysis(components, symbols, start_date, end_date)

def show_overview(components, symbols, start_date, end_date):
    """Show system overview and basic correlation analysis."""
    st.markdown('<h2 class="section-header">📊 System Overview</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Selected Symbols", len(symbols))
    with col2:
        st.metric("📅 Analysis Period", f"{(end_date - start_date).days} days")
    with col3:
        st.metric("🚀 Phase", "2 (Advanced Analytics)")
    with col4:
        st.metric("⚡ Status", "Active")
    
    # Quick correlation analysis
    st.markdown('<h3 class="section-header">🔗 Quick Correlation Analysis</h3>', unsafe_allow_html=True)
    
    if st.button("🚀 Run Quick Analysis"):
        with st.spinner("Running correlation analysis..."):
            try:
                analyzer = components['correlation_analyzer']
                results = analyzer.run_comprehensive_analysis(symbols, start_date, end_date)
                
                if results:
                    # Show correlation heatmap
                    corr_matrix = results['static_correlations']['correlation_matrix']
                    
                    fig = px.imshow(
                        corr_matrix,
                        title="Correlation Heatmap",
                        color_continuous_scale='RdBu_r',
                        zmin=-1, zmax=1
                    )
                    fig.update_layout(height=500)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Summary metrics
                    st.subheader("📈 Summary Metrics")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        avg_corr = corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].mean()
                        st.metric("Average Correlation", f"{avg_corr:.3f}")
                    
                    with col2:
                        max_corr = corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].max()
                        st.metric("Maximum Correlation", f"{max_corr:.3f}")
                    
                    with col3:
                        min_corr = corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].min()
                        st.metric("Minimum Correlation", f"{min_corr:.3f}")
                
            except Exception as e:
                st.error(f"Analysis failed: {e}")

def show_garch_analysis(components, symbols, start_date, end_date):
    """Show GARCH volatility analysis."""
    st.markdown('<h2 class="section-header">📈 GARCH Volatility Models</h2>', unsafe_allow_html=True)
    
    st.info("🔬 GARCH models analyze volatility clustering and forecast future volatility")
    
    if st.button("🚀 Run GARCH Analysis"):
        with st.spinner("Running GARCH analysis... This may take a few minutes."):
            try:
                garch_analyzer = components['garch_analyzer']
                results = garch_analyzer.run_comprehensive_garch_analysis(symbols, start_date, end_date)
                
                if results:
                    st.success("✅ GARCH analysis completed!")
                    
                    # Display results for each symbol
                    for symbol in results['individual_results']:
                        model_result = results['individual_results'][symbol]
                        
                        st.subheader(f"📊 {symbol} - GARCH Results")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Model Type", model_result['model_type'])
                        with col2:
                            st.metric("AIC", f"{model_result['aic']:.2f}")
                        with col3:
                            st.metric("Log-Likelihood", f"{model_result['loglikelihood']:.2f}")
                        with col4:
                            if 'forecast' in model_result and model_result['forecast']:
                                next_vol = model_result['forecast']['volatility_forecast'][0]
                                st.metric("Next Day Vol (%)", f"{next_vol:.3f}")
                        
                        # Volatility plot
                        if 'conditional_volatility' in model_result:
                            vol_data = model_result['conditional_volatility']
                            
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=vol_data.index,
                                y=vol_data.values,
                                mode='lines',
                                name='Conditional Volatility',
                                line=dict(color='red', width=1)
                            ))
                            
                            fig.update_layout(
                                title=f"{symbol} - Conditional Volatility",
                                xaxis_title="Date",
                                yaxis_title="Volatility (%)",
                                height=400
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"GARCH analysis failed: {e}")

def show_var_analysis(components, symbols, start_date, end_date):
    """Show VAR analysis."""
    st.markdown('<h2 class="section-header">🔄 Vector Autoregression (VAR) Analysis</h2>', unsafe_allow_html=True)
    
    st.info("🔍 VAR models analyze relationships between multiple time series and Granger causality")
    
    if len(symbols) < 2:
        st.warning("VAR analysis requires at least 2 symbols")
        return
    
    if st.button("🚀 Run VAR Analysis"):
        with st.spinner("Running VAR analysis... This may take a few minutes."):
            try:
                var_analyzer = components['var_analyzer']
                results = var_analyzer.run_comprehensive_var_analysis(symbols, start_date, end_date)
                
                if results:
                    st.success("✅ VAR analysis completed!")
                    
                    # Model information
                    if 'fitted_model' in results:
                        model_info = results['fitted_model']
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("VAR Order", model_info['lags'])
                        with col2:
                            st.metric("AIC", f"{model_info['aic']:.2f}")
                        with col3:
                            st.metric("BIC", f"{model_info['bic']:.2f}")
                    
                    # Granger causality results
                    if 'granger_causality' in results:
                        st.subheader("🔗 Granger Causality Test Results")
                        
                        causality_data = []
                        for pair, test_result in results['granger_causality'].items():
                            causality_data.append({
                                'Relationship': pair,
                                'Test Statistic': f"{test_result['test_statistic']:.3f}",
                                'P-Value': f"{test_result['p_value']:.4f}",
                                'Significant': "✅ Yes" if test_result['is_significant'] else "❌ No"
                            })
                        
                        causality_df = pd.DataFrame(causality_data)
                        st.dataframe(causality_df, use_container_width=True)
                        
                        # Count significant relationships
                        significant_count = sum(1 for test in results['granger_causality'].values() 
                                              if test['is_significant'])
                        st.metric("Significant Causal Relationships", f"{significant_count}/{len(results['granger_causality'])}")
                
            except Exception as e:
                st.error(f"VAR analysis failed: {e}")

def show_ml_analysis(components, symbols, start_date, end_date):
    """Show machine learning analysis."""
    st.markdown('<h2 class="section-header">🤖 Machine Learning Analysis</h2>', unsafe_allow_html=True)
    
    st.info("🧠 ML models predict future correlations using Random Forest and LSTM neural networks")
    
    if st.button("🚀 Run ML Analysis"):
        with st.spinner("Training ML models... This may take several minutes."):
            try:
                ml_predictor = components['ml_predictor']
                results = ml_predictor.run_comprehensive_ml_analysis(symbols, start_date, end_date)
                
                if results:
                    st.success("✅ ML analysis completed!")
                    
                    # Model performance
                    st.subheader("📊 Model Performance")
                    
                    performance_data = []
                    for model_name, model_results in results['models'].items():
                        performance_data.append({
                            'Model': model_name.replace('_', ' ').title(),
                            'Test R²': f"{model_results['test_r2']:.3f}",
                            'Test MSE': f"{model_results['test_mse']:.6f}",
                            'Train R²': f"{model_results['train_r2']:.3f}"
                        })
                    
                    performance_df = pd.DataFrame(performance_data)
                    st.dataframe(performance_df, use_container_width=True)
                    
                    # Feature importance (Random Forest)
                    if 'random_forest' in results['models']:
                        rf_results = results['models']['random_forest']
                        if 'feature_importance' in rf_results:
                            st.subheader("🎯 Feature Importance (Random Forest)")
                            
                            importance_df = pd.DataFrame(
                                list(rf_results['feature_importance'].items()),
                                columns=['Feature', 'Importance']
                            ).sort_values('Importance', ascending=False).head(10)
                            
                            fig = px.bar(
                                importance_df,
                                x='Importance',
                                y='Feature',
                                orientation='h',
                                title="Top 10 Most Important Features"
                            )
                            fig.update_layout(height=400)
                            st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"ML analysis failed: {e}")

def show_network_analysis(components, symbols, start_date, end_date):
    """Show network analysis."""
    st.markdown('<h2 class="section-header">🌐 Network Analysis</h2>', unsafe_allow_html=True)
    
    st.info("🕸️ Network analysis reveals market structure and systemic risk relationships")
    
    if len(symbols) < 3:
        st.warning("Network analysis works best with at least 3 symbols")
        return
    
    # Correlation threshold selection
    threshold = st.slider("Correlation Threshold", 0.1, 0.9, 0.3, 0.1, 
                         help="Minimum correlation to create network connection")
    
    if st.button("🚀 Run Network Analysis"):
        with st.spinner("Building correlation networks..."):
            try:
                network_analyzer = components['network_analyzer']
                results = network_analyzer.run_comprehensive_network_analysis(symbols, start_date, end_date)
                
                if results:
                    st.success("✅ Network analysis completed!")
                    
                    # Network metrics for selected threshold
                    threshold_key = f'network_threshold_{int(threshold*100)}'
                    if threshold_key in results:
                        network_data = results[threshold_key]
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Nodes", network_data['n_nodes'])
                        with col2:
                            st.metric("Edges", network_data['n_edges'])
                        with col3:
                            st.metric("Density", f"{network_data['density']:.3f}")
                        with col4:
                            avg_clustering = network_data['metrics'].get('average_clustering', 0)
                            st.metric("Avg Clustering", f"{avg_clustering:.3f}")
                        
                        # Network visualization
                        st.subheader("🕸️ Network Visualization")
                        
                        # Create simple network visualization
                        fig = network_analyzer.create_network_visualization(network_data)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Systemic risk analysis
                        systemic_key = f'systemic_risk_threshold_{int(threshold*100)}'
                        if systemic_key in results:
                            systemic_data = results[systemic_key]
                            
                            st.subheader("⚠️ Systemic Risk Analysis")
                            
                            risk_data = []
                            for node, score in systemic_data['systemic_risk_scores'].items():
                                risk_data.append({
                                    'Symbol': node,
                                    'Systemic Risk Score': f"{score:.3f}",
                                    'Risk Level': "🔴 High" if score > 0.7 else "🟡 Medium" if score > 0.4 else "🟢 Low"
                                })
                            
                            risk_df = pd.DataFrame(risk_data).head(10)
                            st.dataframe(risk_df, use_container_width=True)
                
            except Exception as e:
                st.error(f"Network analysis failed: {e}")

def show_regime_analysis(components, symbols, start_date, end_date):
    """Show regime detection analysis."""
    st.markdown('<h2 class="section-header">🎯 Market Regime Detection</h2>', unsafe_allow_html=True)
    
    st.info("🎭 Regime detection identifies different market states using clustering algorithms")
    
    # Number of regimes selection
    n_regimes = st.selectbox("Number of Regimes", [2, 3, 4], index=1, 
                            help="Number of market regimes to detect")
    
    if st.button("🚀 Run Regime Analysis"):
        with st.spinner("Detecting market regimes..."):
            try:
                regime_detector = components['regime_detector']
                results = regime_detector.run_regime_analysis(symbols, start_date, end_date)
                
                if results:
                    st.success("✅ Regime analysis completed!")
                    
                    # Show results for selected number of regimes
                    regime_key = f'regimes_{n_regimes}'
                    if regime_key in results:
                        regime_data = results[regime_key]
                        
                        # Regime statistics
                        st.subheader(f"📊 {n_regimes} Market Regimes")
                        
                        regime_stats_data = []
                        for regime_id, stats in regime_data['regime_stats'].items():
                            regime_stats_data.append({
                                'Regime': f"Regime {regime_id}",
                                'Duration (%)': f"{stats['percentage']:.1f}%",
                                'Observations': stats['count']
                            })
                        
                        regime_stats_df = pd.DataFrame(regime_stats_data)
                        st.dataframe(regime_stats_df, use_container_width=True)
                        
                        # Regime timeline
                        st.subheader("📈 Regime Timeline")
                        
                        regime_series = regime_data['regimes']
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=regime_series.index,
                            y=regime_series.values,
                            mode='markers',
                            marker=dict(
                                size=4,
                                color=regime_series.values,
                                colorscale='viridis',
                                showscale=True,
                                colorbar=dict(title="Regime")
                            ),
                            name='Market Regime'
                        ))
                        
                        fig.update_layout(
                            title="Market Regime Evolution Over Time",
                            xaxis_title="Date",
                            yaxis_title="Regime",
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Model quality metrics
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Explained Variance", f"{regime_data['explained_variance']:.3f}")
                        with col2:
                            st.metric("Number of Regimes", regime_data['n_regimes'])
                
            except Exception as e:
                st.error(f"Regime analysis failed: {e}")

if __name__ == "__main__":
    main()

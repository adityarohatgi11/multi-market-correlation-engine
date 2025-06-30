"""
Basic Streamlit Dashboard
========================

Interactive dashboard for the Multi-Market Correlation Engine.
Displays correlations, data quality, and basic analytics.

Author: Multi-Market Correlation Engine Team
Version: 0.1.0
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date, timedelta
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.config.config_manager import get_config
from src.data.database_manager import get_db_manager
from src.models.correlation_engine import CorrelationEngine
from src.collectors.yahoo_finance_collector import YahooFinanceCollector

# Page configuration
st.set_page_config(
    page_title="Multi-Market Correlation Engine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def initialize_components():
    """Initialize application components."""
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = get_db_manager()
        st.session_state.correlation_engine = CorrelationEngine()
        st.session_state.collector = YahooFinanceCollector()

def load_data_summary():
    """Load data summary from database."""
    try:
        summary = st.session_state.db_manager.get_data_quality_summary()
        return summary
    except Exception as e:
        st.error(f"Error loading data summary: {e}")
        return {}

def display_header():
    """Display application header."""
    st.markdown('<h1 class="main-header">📊 Multi-Market Correlation Engine</h1>', unsafe_allow_html=True)
    st.markdown("---")

def display_sidebar():
    """Display sidebar with controls."""
    st.sidebar.header("🔧 Analysis Controls")
    
    # Symbol selection
    st.sidebar.subheader("📈 Asset Selection")
    
    # Predefined symbol groups
    symbol_groups = {
        "Tech Stocks": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],
        "Market Indices": ["SPY", "QQQ", "IWM", "VTI"],
        "Commodities": ["GLD", "SLV", "USO", "DBA"],
        "Crypto": ["BTC-USD", "ETH-USD", "ADA-USD"],
        "Custom": []
    }
    
    selected_group = st.sidebar.selectbox("Choose Asset Group:", list(symbol_groups.keys()))
    
    if selected_group == "Custom":
        symbols_input = st.sidebar.text_input(
            "Enter symbols (comma-separated):",
            value="AAPL,MSFT,GOOGL",
            help="Enter stock symbols separated by commas"
        )
        symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]
    else:
        symbols = symbol_groups[selected_group]
        st.sidebar.write(f"Selected: {', '.join(symbols)}")
    
    # Date range selection
    st.sidebar.subheader("📅 Date Range")
    end_date = st.sidebar.date_input("End Date", value=date.today())
    
    date_options = {
        "1 Month": 30,
        "3 Months": 90,
        "6 Months": 180,
        "1 Year": 365,
        "2 Years": 730
    }
    
    selected_period = st.sidebar.selectbox("Time Period:", list(date_options.keys()), index=2)
    start_date = end_date - timedelta(days=date_options[selected_period])
    
    # Analysis options
    st.sidebar.subheader("⚙️ Analysis Options")
    correlation_method = st.sidebar.selectbox(
        "Correlation Method:",
        ["pearson", "spearman", "kendall"],
        help="Choose correlation calculation method"
    )
    
    rolling_window = st.sidebar.slider(
        "Rolling Window (days):",
        min_value=10,
        max_value=100,
        value=30,
        help="Window size for rolling correlations"
    )
    
    return {
        'symbols': symbols,
        'start_date': start_date,
        'end_date': end_date,
        'correlation_method': correlation_method,
        'rolling_window': rolling_window
    }

def display_data_overview():
    """Display data overview section."""
    st.header("📊 Data Overview")
    
    summary = load_data_summary()
    
    if summary:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Market Data Records",
                f"{summary.get('market_data_records', 0):,}",
                help="Total market data points in database"
            )
        
        with col2:
            st.metric(
                "Correlation Records",
                f"{summary.get('correlation_records', 0):,}",
                help="Total correlation calculations stored"
            )
        
        with col3:
            st.metric(
                "Data Sources",
                "3",
                help="Yahoo Finance, FRED, CoinGecko"
            )
        
        with col4:
            st.metric(
                "Asset Classes",
                "5",
                help="Equities, Bonds, Commodities, Crypto, Currencies"
            )
    
    else:
        st.warning("No data summary available. Please collect some data first.")

def collect_data_section(params):
    """Data collection section."""
    st.header("🔄 Data Collection")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write(f"**Symbols to collect:** {', '.join(params['symbols'])}")
        st.write(f"**Date range:** {params['start_date']} to {params['end_date']}")
    
    with col2:
        if st.button("🚀 Collect Data", type="primary"):
            with st.spinner("Collecting market data..."):
                progress_bar = st.progress(0)
                results = []
                
                for i, symbol in enumerate(params['symbols']):
                    try:
                        result = st.session_state.collector.collect_symbol_data(
                            symbol=symbol,
                            start_date=params['start_date'],
                            end_date=params['end_date'],
                            asset_class='equity'
                        )
                        results.append(result)
                        progress_bar.progress((i + 1) / len(params['symbols']))
                    except Exception as e:
                        st.error(f"Error collecting {symbol}: {e}")
                
                # Display results
                successful = sum(1 for r in results if r.success)
                total_records = sum(r.records_collected for r in results)
                
                if successful > 0:
                    st.success(f"✅ Collected {total_records} records for {successful}/{len(params['symbols'])} symbols")
                else:
                    st.error("❌ No data collected successfully")

def run_correlation_analysis(params):
    """Run and display correlation analysis."""
    st.header("📈 Correlation Analysis")
    
    try:
        with st.spinner("Running correlation analysis..."):
            results = st.session_state.correlation_engine.run_comprehensive_analysis(
                symbols=params['symbols'],
                start_date=params['start_date'],
                end_date=params['end_date'],
                rolling_window=params['rolling_window']
            )
        
        if not results:
            st.warning("No analysis results. Please collect data first.")
            return
        
        # Display summary metrics
        stats = results['summary_statistics']
        data_period = results['data_period']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Avg Correlation",
                f"{stats['avg_return_correlation']:.3f}",
                help="Average pairwise correlation"
            )
        
        with col2:
            st.metric(
                "Max Correlation",
                f"{stats['max_correlation']:.3f}",
                help="Highest pairwise correlation"
            )
        
        with col3:
            st.metric(
                "Observations",
                f"{data_period['observations']:,}",
                help="Number of data points analyzed"
            )
        
        with col4:
            st.metric(
                "Date Range",
                f"{(data_period['end'] - data_period['start']).days} days",
                help="Analysis period length"
            )
        
        # Correlation matrix visualization
        st.subheader("🔗 Correlation Matrix")
        
        corr_matrix = results['static_correlations']['return_correlation']
        
        if not corr_matrix.empty:
            # Create heatmap
            fig = px.imshow(
                corr_matrix,
                text_auto='.3f',
                aspect="auto",
                color_continuous_scale='RdBu_r',
                color_continuous_midpoint=0,
                title="Return Correlations Heatmap"
            )
            
            fig.update_layout(
                title_x=0.5,
                width=600,
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display correlation table
            st.subheader("📋 Correlation Matrix Table")
            st.dataframe(
                corr_matrix.round(3),
                use_container_width=True
            )
        
        else:
            st.warning("Insufficient data for correlation analysis.")
        
        # Rolling correlations (if available)
        rolling_corr = results.get('rolling_correlations', {})
        
        if rolling_corr:
            st.subheader("📊 Rolling Correlations")
            
            # Create rolling correlation plot
            fig = go.Figure()
            
            for pair_name, corr_series in rolling_corr.items():
                fig.add_trace(go.Scatter(
                    x=corr_series.index,
                    y=corr_series.values,
                    mode='lines',
                    name=pair_name.replace('_', ' vs '),
                    line=dict(width=2)
                ))
            
            fig.update_layout(
                title="Rolling Correlations Over Time",
                xaxis_title="Date",
                yaxis_title="Correlation",
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Analysis summary text
        st.subheader("📝 Analysis Summary")
        summary_text = st.session_state.correlation_engine.generate_correlation_summary(results)
        st.text(summary_text)
        
    except Exception as e:
        st.error(f"Error in correlation analysis: {e}")

def main():
    """Main dashboard function."""
    # Initialize components
    initialize_components()
    
    # Display header
    display_header()
    
    # Get sidebar parameters
    params = display_sidebar()
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "🔄 Data Collection", "📈 Analysis"])
    
    with tab1:
        display_data_overview()
    
    with tab2:
        collect_data_section(params)
    
    with tab3:
        run_correlation_analysis(params)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**Multi-Market Correlation Engine v0.1.0** | "
        "Built with Streamlit | "
        "Data sources: Yahoo Finance, FRED, CoinGecko"
    )

if __name__ == "__main__":
    main()

# Unified Multi-Market Correlation Engine Dashboard

## Overview

**ONE DASHBOARD TO RULE THEM ALL!**

This unified dashboard combines all the functionality from the previous 3 separate dashboards into a single, comprehensive interface. No more confusion about which dashboard does what - everything you need is now in one place.

## What This Solves

### Before (3 Confusing Dashboards):
- **Main Dashboard (8501)** - System monitoring only
- **Visualization Dashboard (8502)** - Basic charts only
- **Advanced Dashboard (8503)** - AI features only

### Now (1 Unified Dashboard):
- **Unified Dashboard (8500)** - **EVERYTHING IN ONE PLACE**

## Quick Start

### Option 1: Simple Launch (Recommended)
```bash
python launch_unified_dashboard.py
```

### Option 2: Manual Launch
```bash
# Terminal 1: Start API
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 &

# Terminal 2: Start Dashboard
python -m streamlit run src/dashboard/unified_dashboard.py --server.port 8500 --server.address 127.0.0.1 --browser.gatherUsageStats false --server.headless true &
```

## Access URLs

| Service | URL | Purpose |
|---------|-----|---------|
| ** Unified Dashboard** | `http://127.0.0.1:8500` | **Main interface - USE THIS** |
| API Server | `http://127.0.0.1:8000` | Backend API |
| API Documentation | `http://127.0.0.1:8000/docs` | Interactive API docs |

## Dashboard Features

### Sidebar - System Control
- ** System Status** - Real-time API and agent monitoring
- ** Analysis Settings** - Symbol selection and parameters
- ** Data Collection** - One-click fresh data collection

### Tab 1: Market Overview
- **Real-time price charts** for selected symbols
- **Market data metrics** (records, quality, latest data)
- **Recent market data table** with OHLCV data
- **Data quality indicators**

### 🔗 Tab 2: Correlations
- **Interactive correlation heatmap** with color coding
- **Correlation statistics table** sorted by strength
- **Key insights** with high correlations highlighted
- **Most connected asset** identification

### Tab 3: AI Insights
- ** GARCH Volatility Analysis** - Volatility forecasting
- ** VAR Analysis** - Granger causality testing
- **🧠 ML Correlation Prediction** - Machine learning predictions
- ** Regime Detection** - Market regime analysis

### Tab 4: Network Analysis
- **Interactive network graph** of asset correlations
- **Network metrics** (centrality, clustering, etc.)
- **Systemic risk ranking** of assets
- **Connection analysis** showing most connected assets

### Tab 5: System Monitor
- ** API Health** - Server status and endpoints
- ** Agent System** - Multi-agent status and tasks
- ** Database** - Connection status and record counts
- ** Recent Activity** - System logs and activity
- ** Performance** - System metrics and uptime

## How to Use

### 1. **Select Your Symbols**
- Use the sidebar to choose from predefined groups (Tech, Financial, Energy, etc.)
- Or manually select symbols from the available options
- Supports 2-5 symbols for optimal analysis

### 2. **Adjust Parameters**
- **Lookback Period**: How many days of historical data to analyze
- **Correlation Threshold**: Minimum correlation strength to highlight

### 3. **Collect Fresh Data**
- Click " Collect Fresh Data" to get the latest market data
- The system will automatically update all analyses

### 4. **Explore the Tabs**
- **Start with Market Overview** to see your data
- **Check Correlations** for relationship analysis
- **Use AI Insights** for advanced predictions
- **Explore Network Analysis** for systemic risk
- **Monitor System** for health checks

## AI-Powered Features

### GARCH Volatility Analysis
- Predicts next-day volatility for each asset
- Uses advanced GARCH(1,1), GARCH(1,2), and GARCH(2,1) models
- Provides volatility forecasts for risk management

### VAR Analysis
- Tests for Granger causality between assets
- Identifies which assets influence others
- Provides statistical significance testing

### ML Correlation Prediction
- Uses machine learning to predict future correlations
- Employs multiple algorithms for robust predictions
- Provides confidence intervals

### Regime Detection
- Identifies current market regime (bull/bear/sideways)
- Provides regime probability and characteristics
- Helps adjust strategies based on market conditions

## System Requirements

- Python 3.8+
- All dependencies from `requirements.txt`
- Minimum 4GB RAM
- Internet connection for data collection

## Troubleshooting

### Dashboard Won't Load
```bash
# Check if services are running
ps aux | grep -E "(streamlit|uvicorn)"

# Restart if needed
python launch_unified_dashboard.py
```

### API Connection Issues
```bash
# Test API health
curl http://127.0.0.1:8000/health

# Check API root
curl http://127.0.0.1:8000/
```

### No Data Available
1. Ensure API is running
2. Click " Collect Fresh Data" in sidebar
3. Wait for data collection to complete
4. Refresh the dashboard

### Analysis Errors
- Check that you have selected 2-5 symbols
- Ensure sufficient historical data exists
- Try collecting fresh data

## Performance Tips

1. **Start with fewer symbols** (2-3) for faster analysis
2. **Use shorter lookback periods** for quicker results
3. **Collect data during market hours** for best quality
4. **Monitor system resources** in the System Monitor tab

## Key Benefits

### Unified Experience
- **One URL to remember**: `http://127.0.0.1:8500`
- **All features in one place** - no more dashboard confusion
- **Consistent interface** across all functionality

### Real-Time Monitoring
- **Live system status** in sidebar
- **Real-time data updates** with one-click refresh
- **Agent activity monitoring** shows AI system status

### Advanced Analytics
- **Professional-grade analysis** with GARCH, VAR, ML
- **Interactive visualizations** with Plotly
- **Network analysis** for systemic risk assessment

### Easy to Use
- **Intuitive tab-based navigation**
- **Clear status indicators** (🟢🔴)
- **One-click data collection**
- **Built-in help and guidance**

## Success!

You now have a **single, powerful dashboard** that provides:

- **Market data visualization**
- 🔗 **Correlation analysis**
- **AI-powered insights**
- **Network analysis**
- **System monitoring**

**All in one unified interface at `http://127.0.0.1:8500`**

---

## 🆘 Need Help?

If you encounter any issues:

1. Check the **System Monitor** tab for status
2. Look at the **sidebar** for system health indicators
3. Try the ** Collect Fresh Data** button
4. Restart using `python launch_unified_dashboard.py`

**Happy analyzing! **
# Development Environment Setup

## Step 1.1: Python Environment
```bash
# Check Python version (need 3.9+)
python --version

# Create virtual environment
python -m venv correlation_env

# Activate environment
# On macOS/Linux:
source correlation_env/bin/activate
# On Windows:
# correlation_env\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

## Step 1.2: Install Core Dependencies
```bash
# Install requirements
pip install -r requirements.txt

# Verify installation
python -c "import pandas, numpy, yfinance, streamlit; print('All packages installed successfully!')"
```

## Step 1.3: Get Free API Keys
```bash
# 1. FRED API (Federal Reserve Economic Data)
# Visit: https://fred.stlouisfed.org/docs/api/api_key.html
# Register for free API key
# Create .env file and add: FRED_API_KEY=your_key_here

# 2. Alpha Vantage (Backup data source)
# Visit: https://www.alphavantage.co/support/#api-key
# Get free API key (5 calls/minute)
# Add to .env: ALPHA_VANTAGE_KEY=your_key_here

# 3. News API (Optional - for sentiment)
# Visit: https://newsapi.org/register
# Free tier: 1000 requests/day
# Add to .env: NEWS_API_KEY=your_key_here
```

## Step 1.4: Project Structure Verification
```
multi_market_correlation_engine/
├── README.md                    ✓ Created
├── requirements.txt             ✓ Created
├── .env                         → Create this
├── .gitignore                   → Create this
├── config/
│   └── data_sources.yaml       ✓ Created
├── src/
│   ├── __init__.py             → Create this
│   ├── collectors/
│   ├── models/
│   ├── agents/
│   └── visualization/
├── data/
│   ├── raw/
│   ├── processed/
│   └── models/
├── tests/
├── notebooks/
└── logs/
``` 
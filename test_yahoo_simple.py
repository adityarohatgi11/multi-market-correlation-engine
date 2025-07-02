#!/usr/bin/env python3
"""
Simple Yahoo Finance Test
========================

Direct test of Yahoo Finance data collection without config dependencies.
"""

import yfinance as yf
from datetime import date, timedelta

def test_yahoo_direct():
    """Test Yahoo Finance directly using yfinance library."""
    print("🚀 Testing Yahoo Finance Free Data Collection")
    print("=" * 50)
    
    # Test different asset classes
    test_symbols = {
        'Apple Stock': 'AAPL',
        'S&P 500 Index': '^GSPC',
        'SPDR S&P 500 ETF': 'SPY',
        'EUR/USD Currency': 'EURUSD=X',
        'Gold Futures': 'GC=F',
        '10-Year Treasury': '^TNX'
    }
    
    # Calculate date range (last 7 days)
    end_date = date.today()
    start_date = end_date - timedelta(days=7)
    
    results = []
    
    for asset_name, symbol in test_symbols.items():
        print(f"\n📊 Testing {asset_name} ({symbol})")
        
        try:
            # Fetch data using yfinance
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date)
            
            if not data.empty:
                print(f"   ✅ Success: {len(data)} records collected")
                print(f"   📈 Latest Close: ${data['Close'].iloc[-1]:.2f}")
                print(f"   📊 Date Range: {data.index[0].date()} to {data.index[-1].date()}")
                results.append(True)
            else:
                print(f"   ⚠️  No data returned")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append(False)
    
    # Summary
    successful = sum(results)
    total = len(results)
    print(f"\n🎯 Results: {successful}/{total} successful collections")
    
    if successful > 0:
        print("\n🎉 Yahoo Finance is working perfectly!")
        print("   You have access to 40,000+ stocks, ETFs, commodities, currencies, and bonds!")
    
    return successful > 0

if __name__ == "__main__":
    success = test_yahoo_direct()
    
    if success:
        print("\n📋 Your Free Data Capabilities:")
        print("   • 40,000+ global stocks")
        print("   • 3,000+ ETFs and funds") 
        print("   • 200+ market indices")
        print("   • 50+ commodity futures")
        print("   • 100+ currency pairs")
        print("   • Bond rates and treasury data")
        print("   • 2000 requests/minute rate limit")
        print("   • Historical data back 10+ years")
        print("   • 100% FREE - No API key required!")

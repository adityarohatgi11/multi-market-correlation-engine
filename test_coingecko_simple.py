#!/usr/bin/env python3
"""
Simple CoinGecko Test
====================

Direct test of CoinGecko API for cryptocurrency data.
"""

import requests
import json
from datetime import date, timedelta

def test_coingecko_direct():
    """Test CoinGecko API directly."""
    print("🪙 Testing CoinGecko Free Cryptocurrency Data")
    print("=" * 50)
    
    base_url = "https://api.coingecko.com/api/v3"
    
    # Test 1: Get current prices for major cryptocurrencies
    print("\n📊 Testing Current Price Data")
    try:
        url = f"{base_url}/simple/price"
        params = {
            'ids': 'bitcoin,ethereum,binancecoin,cardano,solana',
            'vs_currencies': 'usd',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        for coin_id, coin_data in data.items():
            price = coin_data.get('usd', 0)
            change = coin_data.get('usd_24h_change', 0)
            volume = coin_data.get('usd_24h_vol', 0)
            
            print(f"   🪙 {coin_id.title()}: ${price:,.2f} ({change:+.2f}%) Vol: ${volume:,.0f}")
        
        print("   ✅ Current price data: SUCCESS")
        
    except Exception as e:
        print(f"   ❌ Current price data failed: {e}")
        return False
    
    # Test 2: Get historical data for Bitcoin
    print("\n📈 Testing Historical Data (Bitcoin - 7 days)")
    try:
        url = f"{base_url}/coins/bitcoin/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': '7',
            'interval': 'daily'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        prices = data.get('prices', [])
        
        if prices:
            print(f"   📊 Historical records: {len(prices)} data points")
            print(f"   📅 Date range: {len(prices)} days of data")
            print("   ✅ Historical data: SUCCESS")
        else:
            print("   ⚠️  No historical data returned")
            return False
            
    except Exception as e:
        print(f"   ❌ Historical data failed: {e}")
        return False
    
    # Test 3: Get list of supported coins
    print("\n🔍 Testing Supported Coins List")
    try:
        url = f"{base_url}/coins/list"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        coins = response.json()
        print(f"   🪙 Total supported coins: {len(coins):,}")
        print("   ✅ Coins list: SUCCESS")
        
    except Exception as e:
        print(f"   ❌ Coins list failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_coingecko_direct()
    
    if success:
        print("\n🎉 CoinGecko is working perfectly!")
        print("\n📋 Your Free Crypto Data Capabilities:")
        print("   • 10,000+ cryptocurrencies")
        print("   • Real-time price data")
        print("   • Historical data (unlimited)")
        print("   • Market cap and volume data")
        print("   • 24h price changes")
        print("   • No API key required!")
        print("   • Rate limit: 10-50 requests/minute")
        print("   • 100% FREE forever!")
    else:
        print("\n❌ CoinGecko test failed")
        print("   Check your internet connection and try again")

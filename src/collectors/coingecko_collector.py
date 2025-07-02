"""
CoinGecko API Collector
======================

Collects cryptocurrency data from CoinGecko API.
Completely free with rate limiting.

Features:
- 10,000+ cryptocurrencies
- Historical price data (unlimited)
- Market cap, volume, price data
- No API key required for basic tier
- Free tier: 10-50 requests/minute
"""

import time
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import requests
import pandas as pd
from dataclasses import dataclass

from src.config.config_manager import get_config
from src.data.database_manager import get_db_manager

logger = logging.getLogger(__name__)


@dataclass
class CoinGeckoCollectionResult:
    """Result of CoinGecko data collection operation."""
    success: bool
    coin_id: str
    records_collected: int
    error_message: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class CoinGeckoCollector:
    """
    CoinGecko API data collector for cryptocurrency data.
    
    Free API with 10-50 requests per minute limit.
    No API key required for basic tier.
    """
    
    def __init__(self):
        """Initialize CoinGecko collector."""
        self.config = get_config()
        self.db_manager = get_db_manager()
        self.base_url = "https://api.coingecko.com/api/v3"
        
        # Rate limiting (10-50 requests per minute for free tier)
        self.last_request_time = 0
        self.min_request_interval = 6.0  # 6 seconds between requests (10 req/min)
        
        logger.info("CoinGecko collector initialized")
    
    def collect_coin_data(
        self,
        coin_id: str,
        start_date: date,
        end_date: date,
        vs_currency: str = "usd"
    ) -> CoinGeckoCollectionResult:
        """
        Collect historical data for a single cryptocurrency.
        
        Args:
            coin_id: CoinGecko coin ID (e.g., 'bitcoin', 'ethereum')
            start_date: Start date for collection
            end_date: End date for collection
            vs_currency: Currency to price against (default: 'usd')
            
        Returns:
            CoinGeckoCollectionResult with operation details
        """
        try:
            # Rate limiting
            self._wait_for_rate_limit()
            
            logger.debug(f"Collecting CoinGecko data for {coin_id} from {start_date} to {end_date}")
            
            # Fetch historical data
            data = self._fetch_coin_history(coin_id, start_date, end_date, vs_currency)
            
            if data is None or data.empty:
                return CoinGeckoCollectionResult(
                    success=False,
                    coin_id=coin_id,
                    records_collected=0,
                    error_message="No data returned from CoinGecko API"
                )
            
            # Save to database
            records_saved = self._save_crypto_data(data, coin_id)
            
            logger.info(f"Collected {records_saved} records for {coin_id}")
            
            return CoinGeckoCollectionResult(
                success=True,
                coin_id=coin_id,
                records_collected=records_saved,
                start_date=start_date,
                end_date=end_date
            )
            
        except Exception as e:
            logger.error(f"Failed to collect CoinGecko data for {coin_id}: {e}")
            return CoinGeckoCollectionResult(
                success=False,
                coin_id=coin_id,
                records_collected=0,
                error_message=str(e)
            )
    
    def _fetch_coin_history(
        self,
        coin_id: str,
        start_date: date,
        end_date: date,
        vs_currency: str
    ) -> Optional[pd.DataFrame]:
        """Fetch historical data from CoinGecko API."""
        try:
            # Calculate days for CoinGecko API
            days_diff = (end_date - start_date).days
            
            # CoinGecko API endpoint for historical data
            url = f"{self.base_url}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': vs_currency,
                'days': max(1, days_diff),
                'interval': 'daily' if days_diff > 1 else 'hourly'
            }
            
            # Make API request
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if not data or 'prices' not in data:
                logger.warning(f"No price data found for {coin_id}")
                return None
            
            # Convert to DataFrame
            df_records = []
            
            # Process prices (timestamp, price)
            prices = data.get('prices', [])
            market_caps = data.get('market_caps', [])
            volumes = data.get('total_volumes', [])
            
            # Create lookup dictionaries for market cap and volume
            market_cap_dict = {ts: value for ts, value in market_caps}
            volume_dict = {ts: value for ts, value in volumes}
            
            for timestamp, price in prices:
                dt = datetime.fromtimestamp(timestamp / 1000).date()
                
                # Filter by date range
                if start_date <= dt <= end_date:
                    record = {
                        'date': dt,
                        'close_price': price,
                        'market_cap': market_cap_dict.get(timestamp, None),
                        'volume': volume_dict.get(timestamp, None),
                        'coin_id': coin_id,
                        'vs_currency': vs_currency
                    }
                    df_records.append(record)
            
            if not df_records:
                return None
            
            df = pd.DataFrame(df_records)
            
            # Add metadata
            df['source'] = 'coingecko'
            df['collected_at'] = datetime.now()
            
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"CoinGecko API request failed for {coin_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing CoinGecko data for {coin_id}: {e}")
            return None
    
    def _save_crypto_data(self, df: pd.DataFrame, coin_id: str) -> int:
        """Save cryptocurrency data to database."""
        try:
            # Convert to market data format for compatibility
            market_data_records = []
            
            for _, row in df.iterrows():
                record = {
                    'symbol': coin_id.upper(),
                    'asset_class': 'cryptocurrency',
                    'date': row['date'],
                    'close_price': row['close_price'],
                    'volume': row.get('volume'),
                    'source': 'coingecko',
                    'data_quality_score': 0.95  # CoinGecko data is high quality
                }
                market_data_records.append(record)
            
            if market_data_records:
                market_df = pd.DataFrame(market_data_records)
                return self.db_manager.save_market_data(market_df, source="coingecko")
            
            return 0
            
        except Exception as e:
            logger.error(f"Failed to save CoinGecko data for {coin_id}: {e}")
            return 0
    
    def _wait_for_rate_limit(self):
        """Implement rate limiting for CoinGecko API."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            logger.debug(f"Rate limiting: waiting {sleep_time:.1f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def collect_crypto_portfolio(self, days_back: int = 365) -> List[CoinGeckoCollectionResult]:
        """
        Collect data for predefined cryptocurrency portfolio.
        
        Args:
            days_back: Number of days of historical data to collect
            
        Returns:
            List of collection results
        """
        # Get crypto configuration
        crypto_config = self.config.get_data_source_config("crypto")
        coingecko_config = crypto_config.get('coingecko', {})
        coin_list = coingecko_config.get('coins', [])
        vs_currency = coingecko_config.get('vs_currency', 'usd')
        
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back)
        
        results = []
        logger.info(f"Collecting {len(coin_list)} cryptocurrencies from CoinGecko")
        
        for coin_id in coin_list:
            result = self.collect_coin_data(coin_id, start_date, end_date, vs_currency)
            results.append(result)
            
            # Respect rate limits
            time.sleep(1)
        
        successful_collections = sum(1 for r in results if r.success)
        logger.info(f"Successfully collected {successful_collections}/{len(coin_list)} cryptocurrencies")
        
        return results


# Example usage
if __name__ == "__main__":
    try:
        collector = CoinGeckoCollector()
        print("✅ CoinGecko collector initialized!")
        
        # Test collection
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        result = collector.collect_coin_data(
            coin_id="bitcoin",
            start_date=start_date,
            end_date=end_date
        )
        
        print(f"Collection result: {result.success}")
        print(f"Records collected: {result.records_collected}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

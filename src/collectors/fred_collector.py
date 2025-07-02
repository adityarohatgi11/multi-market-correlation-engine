"""
FRED (Federal Reserve Economic Data) Collector
=============================================

Collects economic indicators from the Federal Reserve Economic Data API.
Completely free with API key registration.

Features:
- Economic indicators (GDP, inflation, unemployment, etc.)
- Interest rates and bond yields
- Currency exchange rates
- Market volatility indices
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
class FREDCollectionResult:
    """Result of FRED data collection operation."""
    success: bool
    series_id: str
    records_collected: int
    error_message: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class FREDCollector:
    """
    FRED API data collector for economic indicators.
    
    Free API with 120 requests per minute limit.
    Requires free API key from https://fred.stlouisfed.org/docs/api/api_key.html
    """
    
    def __init__(self):
        """Initialize FRED collector."""
        self.config = get_config()
        self.db_manager = get_db_manager()
        self.base_url = "https://api.stlouisfed.org/fred"
        
        # Get API key from environment variable
        import os
        self.api_key = os.getenv('FRED_API_KEY')
        if not self.api_key:
            logger.warning("FRED_API_KEY not found in environment variables. "
                         "Get free key from https://fred.stlouisfed.org/docs/api/api_key.html")
        
        # Rate limiting (120 requests per minute for free tier)
        self.last_request_time = 0
        self.min_request_interval = 0.5  # 500ms between requests
        
        logger.info("FRED collector initialized")
    
    def collect_series_data(
        self,
        series_id: str,
        start_date: date,
        end_date: date,
        frequency: str = "d"  # d=daily, w=weekly, m=monthly, q=quarterly, a=annual
    ) -> FREDCollectionResult:
        """
        Collect data for a single FRED series.
        
        Args:
            series_id: FRED series ID (e.g., 'GDP', 'UNRATE', 'DGS10')
            start_date: Start date for collection
            end_date: End date for collection
            frequency: Data frequency
            
        Returns:
            FREDCollectionResult with operation details
        """
        if not self.api_key:
            return FREDCollectionResult(
                success=False,
                series_id=series_id,
                records_collected=0,
                error_message="FRED API key not configured"
            )
        
        try:
            # Rate limiting
            self._wait_for_rate_limit()
            
            logger.debug(f"Collecting FRED data for {series_id} from {start_date} to {end_date}")
            
            # Fetch series data
            data = self._fetch_series_data(series_id, start_date, end_date, frequency)
            
            if data is None or data.empty:
                return FREDCollectionResult(
                    success=False,
                    series_id=series_id,
                    records_collected=0,
                    error_message="No data returned from FRED API"
                )
            
            # Save to database
            records_saved = self._save_economic_data(data, series_id)
            
            logger.info(f"Collected {records_saved} records for FRED series {series_id}")
            
            return FREDCollectionResult(
                success=True,
                series_id=series_id,
                records_collected=records_saved,
                start_date=start_date,
                end_date=end_date
            )
            
        except Exception as e:
            logger.error(f"Failed to collect FRED data for {series_id}: {e}")
            return FREDCollectionResult(
                success=False,
                series_id=series_id,
                records_collected=0,
                error_message=str(e)
            )
    
    def _fetch_series_data(
        self,
        series_id: str,
        start_date: date,
        end_date: date,
        frequency: str
    ) -> Optional[pd.DataFrame]:
        """Fetch data from FRED API."""
        try:
            # Build API URL
            url = f"{self.base_url}/series/observations"
            params = {
                'series_id': series_id,
                'api_key': self.api_key,
                'file_type': 'json',
                'observation_start': start_date.strftime('%Y-%m-%d'),
                'observation_end': end_date.strftime('%Y-%m-%d'),
                'frequency': frequency,
                'sort_order': 'asc'
            }
            
            # Make API request
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'observations' not in data:
                logger.warning(f"No observations found for series {series_id}")
                return None
            
            # Convert to DataFrame
            observations = data['observations']
            df = pd.DataFrame(observations)
            
            if df.empty:
                return None
            
            # Clean and process data
            df['date'] = pd.to_datetime(df['date']).dt.date
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            
            # Remove rows with missing values (FRED uses '.' for missing)
            df = df.dropna(subset=['value'])
            
            # Add metadata
            df['series_id'] = series_id
            df['source'] = 'fred'
            df['collected_at'] = datetime.now()
            
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"FRED API request failed for {series_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing FRED data for {series_id}: {e}")
            return None
    
    def _save_economic_data(self, df: pd.DataFrame, series_id: str) -> int:
        """Save economic data to database."""
        try:
            # Convert to market data format for compatibility
            market_data_records = []
            
            for _, row in df.iterrows():
                record = {
                    'symbol': series_id,
                    'asset_class': 'economic_indicator',
                    'date': row['date'],
                    'close_price': row['value'],  # Store economic value as close price
                    'source': 'fred',
                    'data_quality_score': 1.0  # FRED data is high quality
                }
                market_data_records.append(record)
            
            if market_data_records:
                market_df = pd.DataFrame(market_data_records)
                return self.db_manager.save_market_data(market_df, source="fred")
            
            return 0
            
        except Exception as e:
            logger.error(f"Failed to save FRED data for {series_id}: {e}")
            return 0
    
    def _wait_for_rate_limit(self):
        """Implement rate limiting for FRED API."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def collect_economic_indicators(self, days_back: int = 365) -> List[FREDCollectionResult]:
        """
        Collect predefined economic indicators.
        
        Args:
            days_back: Number of days of historical data to collect
            
        Returns:
            List of collection results
        """
        # Get FRED configuration
        fred_config = self.config.get_data_source_config("fred")
        series_list = []
        
        # Collect all series from configuration
        series_config = fred_config.get('series', {})
        for category, series in series_config.items():
            series_list.extend(series)
        
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back)
        
        results = []
        logger.info(f"Collecting {len(series_list)} FRED economic indicators")
        
        for series_id in series_list:
            result = self.collect_series_data(series_id, start_date, end_date)
            results.append(result)
            
            # Small delay between series to be respectful
            time.sleep(0.1)
        
        successful_collections = sum(1 for r in results if r.success)
        logger.info(f"Successfully collected {successful_collections}/{len(series_list)} FRED series")
        
        return results
    
    def get_available_series(self, search_text: str = None) -> List[Dict[str, Any]]:
        """
        Search for available FRED series.
        
        Args:
            search_text: Text to search for in series titles/descriptions
            
        Returns:
            List of series information
        """
        if not self.api_key:
            logger.warning("FRED API key required for series search")
            return []
        
        try:
            self._wait_for_rate_limit()
            
            url = f"{self.base_url}/series/search"
            params = {
                'search_text': search_text or 'economic indicators',
                'api_key': self.api_key,
                'file_type': 'json',
                'limit': 100
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data.get('seriess', [])
            
        except Exception as e:
            logger.error(f"Failed to search FRED series: {e}")
            return []


# Example usage
if __name__ == "__main__":
    import os
    
    # Set API key for testing (get from https://fred.stlouisfed.org/docs/api/api_key.html)
    # os.environ['FRED_API_KEY'] = 'your_api_key_here'
    
    try:
        collector = FREDCollector()
        print("✅ FRED collector initialized!")
        
        if collector.api_key:
            # Test collection
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            
            result = collector.collect_series_data(
                series_id="DGS10",  # 10-Year Treasury Rate
                start_date=start_date,
                end_date=end_date
            )
            
            print(f"Collection result: {result.success}")
            print(f"Records collected: {result.records_collected}")
        else:
            print("⚠️  Set FRED_API_KEY environment variable to test data collection")
            
    except Exception as e:
        print(f"❌ Error: {e}") 
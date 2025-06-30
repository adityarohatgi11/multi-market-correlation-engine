"""
Yahoo Finance Data Collector
============================

Comprehensive data collection from Yahoo Finance API with rate limiting,
error handling, and data validation for multi-asset market data.

Author: Multi-Market Correlation Engine Team
Version: 0.1.0
"""

import time
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings

import pandas as pd
import numpy as np
import yfinance as yf
from requests.exceptions import RequestException, Timeout
from tqdm import tqdm

from src.config.config_manager import get_config
from src.data.database_manager import get_db_manager

# Suppress yfinance warnings
warnings.filterwarnings("ignore", module="yfinance")

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class CollectionResult:
    """Result of a data collection operation."""
    success: bool
    symbol: str
    records_collected: int
    error_message: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    data_quality_score: Optional[float] = None


class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, max_calls_per_minute: int = 200):
        """
        Initialize rate limiter.
        
        Args:
            max_calls_per_minute: Maximum API calls per minute
        """
        self.max_calls = max_calls_per_minute
        self.calls = []
    
    def wait_if_needed(self) -> None:
        """Wait if rate limit would be exceeded."""
        now = datetime.utcnow()
        
        # Remove calls older than 1 minute
        self.calls = [call_time for call_time in self.calls 
                     if (now - call_time).total_seconds() < 60]
        
        # Check if we need to wait
        if len(self.calls) >= self.max_calls:
            # Wait until oldest call is 1 minute old
            oldest_call = min(self.calls)
            wait_time = 60 - (now - oldest_call).total_seconds()
            if wait_time > 0:
                logger.info(f"Rate limit reached, waiting {wait_time:.1f} seconds")
                time.sleep(wait_time)
        
        # Record this call
        self.calls.append(now)


class YahooFinanceCollector:
    """
    Yahoo Finance data collector with advanced features.
    
    Features:
    - Multi-asset support (stocks, ETFs, commodities, currencies, bonds)
    - Rate limiting and retry logic
    - Data validation and quality scoring
    - Concurrent collection with thread pooling
    - Error handling and logging
    """
    
    def __init__(self):
        """Initialize Yahoo Finance collector."""
        self.config = get_config()
        self.db_manager = get_db_manager()
        self.rate_limiter = RateLimiter(max_calls_per_minute=180)  # Conservative limit
        
        # Get collection configuration
        self.collection_config = self.config.get_data_source_config("collection")
        self.yahoo_config = self.config.get_data_source_config("yahoo_finance")
        self.rate_limit_config = self.config.get_data_source_config("rate_limits")
        
        logger.info("Yahoo Finance collector initialized")
    
    def collect_symbol_data(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        asset_class: str = "equity"
    ) -> CollectionResult:
        """
        Collect data for a single symbol.
        
        Args:
            symbol: Symbol to collect
            start_date: Start date for collection
            end_date: End date for collection
            asset_class: Asset class (equity, commodity, currency, etc.)
            
        Returns:
            CollectionResult with operation details
        """
        self.rate_limiter.wait_if_needed()
        
        try:
            logger.debug(f"Collecting data for {symbol} from {start_date} to {end_date}")
            
            # Create ticker object
            ticker = yf.Ticker(symbol)
            
            # Fetch historical data with retry logic
            data = self._fetch_with_retry(ticker, start_date, end_date)
            
            if data is None or data.empty:
                return CollectionResult(
                    success=False,
                    symbol=symbol,
                    records_collected=0,
                    error_message="No data returned from Yahoo Finance"
                )
            
            # Clean and validate data
            cleaned_data = self._clean_and_validate_data(data, symbol, asset_class)
            
            if cleaned_data.empty:
                return CollectionResult(
                    success=False,
                    symbol=symbol,
                    records_collected=0,
                    error_message="Data failed validation"
                )
            
            # Calculate data quality score
            quality_score = self._calculate_data_quality(cleaned_data)
            
            # Save to database
            records_saved = self.db_manager.save_market_data(
                cleaned_data, 
                source="yahoo_finance"
            )
            
            logger.info(f"Collected {records_saved} records for {symbol} "
                       f"(quality: {quality_score:.2f})")
            
            return CollectionResult(
                success=True,
                symbol=symbol,
                records_collected=records_saved,
                start_date=start_date,
                end_date=end_date,
                data_quality_score=quality_score
            )
            
        except Exception as e:
            logger.error(f"Failed to collect data for {symbol}: {e}")
            return CollectionResult(
                success=False,
                symbol=symbol,
                records_collected=0,
                error_message=str(e)
            )
    
    def _fetch_with_retry(
        self, 
        ticker: yf.Ticker, 
        start_date: date, 
        end_date: date,
        max_retries: int = 3
    ) -> Optional[pd.DataFrame]:
        """
        Fetch data with retry logic.
        
        Args:
            ticker: Yahoo Finance ticker object
            start_date: Start date
            end_date: End date
            max_retries: Maximum retry attempts
            
        Returns:
            DataFrame with market data or None if failed
        """
        for attempt in range(max_retries):
            try:
                data = ticker.history(
                    start=start_date,
                    end=end_date,
                    interval="1d",
                    auto_adjust=False,
                    prepost=True
                )
                
                if not data.empty:
                    return data
                    
                logger.warning(f"Empty data on attempt {attempt + 1} for {ticker.ticker}")
                
            except (RequestException, Timeout) as e:
                logger.warning(f"Network error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
            except Exception as e:
                logger.error(f"Unexpected error fetching data: {e}")
                break
        
        return None
    
    def _clean_and_validate_data(
        self, 
        data: pd.DataFrame, 
        symbol: str, 
        asset_class: str
    ) -> pd.DataFrame:
        """
        Clean and validate market data.
        
        Args:
            data: Raw market data DataFrame
            symbol: Symbol being processed
            asset_class: Asset class
            
        Returns:
            Cleaned and validated DataFrame
        """
        if data.empty:
            return data
        
        try:
            # Reset index to get date as column
            df = data.reset_index()
            
            # Standardize column names
            column_mapping = {
                'Date': 'date',
                'Open': 'open',
                'High': 'high', 
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume',
                'Adj Close': 'adjusted_close'
            }
            
            df = df.rename(columns=column_mapping)
            
            # Add metadata columns
            df['symbol'] = symbol
            df['asset_class'] = asset_class
            
            # Ensure date is datetime
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date']).dt.date
            
            # Validate required columns
            required_columns = ['date', 'close', 'symbol']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                logger.error(f"Missing required columns for {symbol}: {missing_columns}")
                return pd.DataFrame()
            
            # Remove rows with missing close prices
            initial_rows = len(df)
            df = df.dropna(subset=['close'])
            
            if len(df) < initial_rows:
                logger.warning(f"Removed {initial_rows - len(df)} rows with missing close prices for {symbol}")
            
            # Basic price validation
            df = self._validate_prices(df, symbol)
            
            # Remove outliers
            df = self._remove_outliers(df, symbol)
            
            # Sort by date
            df = df.sort_values('date').reset_index(drop=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to clean data for {symbol}: {e}")
            return pd.DataFrame()
    
    def _validate_prices(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Validate price data for basic sanity checks.
        
        Args:
            df: DataFrame with market data
            symbol: Symbol being validated
            
        Returns:
            DataFrame with invalid prices removed
        """
        initial_rows = len(df)
        
        # Remove negative prices
        price_columns = ['open', 'high', 'low', 'close', 'adjusted_close']
        for col in price_columns:
            if col in df.columns:
                df = df[df[col] > 0]
        
        # Check OHLC relationships (High >= Low, etc.)
        if all(col in df.columns for col in ['open', 'high', 'low', 'close']):
            valid_ohlc = (
                (df['high'] >= df['low']) &
                (df['high'] >= df['open']) &
                (df['high'] >= df['close']) &
                (df['low'] <= df['open']) &
                (df['low'] <= df['close'])
            )
            df = df[valid_ohlc]
        
        # Remove extreme price jumps (>50% daily change)
        if 'close' in df.columns and len(df) > 1:
            df['price_change'] = df['close'].pct_change()
            extreme_changes = df['price_change'].abs() > 0.5
            df = df[~extreme_changes]
            df = df.drop('price_change', axis=1)
        
        removed_rows = initial_rows - len(df)
        if removed_rows > 0:
            logger.warning(f"Removed {removed_rows} rows with invalid prices for {symbol}")
        
        return df
    
    def _remove_outliers(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Remove statistical outliers from the data.
        
        Args:
            df: DataFrame with market data
            symbol: Symbol being processed
            
        Returns:
            DataFrame with outliers removed
        """
        if len(df) < 10:  # Need minimum data for outlier detection
            return df
        
        initial_rows = len(df)
        
        # Use IQR method for outlier detection on closing prices
        if 'close' in df.columns:
            Q1 = df['close'].quantile(0.25)
            Q3 = df['close'].quantile(0.75)
            IQR = Q3 - Q1
            
            # Define outlier bounds (1.5 * IQR is standard)
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Keep only data within bounds
            df = df[(df['close'] >= lower_bound) & (df['close'] <= upper_bound)]
        
        removed_rows = initial_rows - len(df)
        if removed_rows > 0:
            logger.info(f"Removed {removed_rows} outliers for {symbol}")
        
        return df
    
    def _calculate_data_quality(self, df: pd.DataFrame) -> float:
        """
        Calculate data quality score (0-1).
        
        Args:
            df: DataFrame with market data
            
        Returns:
            Quality score between 0 and 1
        """
        if df.empty:
            return 0.0
        
        scores = []
        
        # Completeness score (non-null values)
        total_cells = len(df) * len(df.columns)
        non_null_cells = df.count().sum()
        completeness = non_null_cells / total_cells if total_cells > 0 else 0
        scores.append(completeness * 0.3)  # 30% weight
        
        # Consistency score (valid OHLC relationships)
        if all(col in df.columns for col in ['open', 'high', 'low', 'close']):
            valid_ohlc = (
                (df['high'] >= df['low']) &
                (df['high'] >= df['open']) &
                (df['high'] >= df['close']) &
                (df['low'] <= df['open']) &
                (df['low'] <= df['close'])
            ).mean()
            scores.append(valid_ohlc * 0.3)  # 30% weight
        
        # Continuity score (no large gaps in dates)
        if 'date' in df.columns and len(df) > 1:
            df_sorted = df.sort_values('date')
            date_diffs = pd.to_datetime(df_sorted['date']).diff().dt.days
            # Expect mostly 1-day differences (weekdays) or 3-day (weekends)
            reasonable_gaps = (date_diffs <= 4).mean()
            scores.append(reasonable_gaps * 0.25)  # 25% weight
        
        # Volume consistency (if available)
        if 'volume' in df.columns:
            # Check for reasonable volume values (not all zeros)
            volume_quality = (df['volume'] > 0).mean()
            scores.append(volume_quality * 0.15)  # 15% weight
        
        # Return weighted average
        return np.mean(scores) if scores else 0.5
    
    def collect_batch(
        self,
        symbols: List[str],
        start_date: date,
        end_date: date,
        asset_classes: Optional[Dict[str, str]] = None,
        max_workers: int = 5
    ) -> List[CollectionResult]:
        """
        Collect data for multiple symbols in parallel.
        
        Args:
            symbols: List of symbols to collect
            start_date: Start date for collection
            end_date: End date for collection
            asset_classes: Dict mapping symbols to asset classes
            max_workers: Maximum number of concurrent workers
            
        Returns:
            List of CollectionResult objects
        """
        logger.info(f"Starting batch collection for {len(symbols)} symbols")
        
        results = []
        asset_classes = asset_classes or {}
        
        # Use ThreadPoolExecutor for concurrent collection
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_symbol = {}
            for symbol in symbols:
                asset_class = asset_classes.get(symbol, "equity")
                future = executor.submit(
                    self.collect_symbol_data,
                    symbol,
                    start_date,
                    end_date,
                    asset_class
                )
                future_to_symbol[future] = symbol
            
            # Collect results with progress bar
            with tqdm(total=len(symbols), desc="Collecting data") as pbar:
                for future in as_completed(future_to_symbol):
                    symbol = future_to_symbol[future]
                    try:
                        result = future.result()
                        results.append(result)
                        
                        # Update progress bar
                        status = "✓" if result.success else "✗"
                        pbar.set_postfix_str(f"{symbol}: {status}")
                        pbar.update(1)
                        
                    except Exception as e:
                        logger.error(f"Failed to collect {symbol}: {e}")
                        results.append(CollectionResult(
                            success=False,
                            symbol=symbol,
                            records_collected=0,
                            error_message=str(e)
                        ))
                        pbar.update(1)
        
        # Log summary
        successful = sum(1 for r in results if r.success)
        total_records = sum(r.records_collected for r in results)
        
        logger.info(f"Batch collection complete: {successful}/{len(symbols)} symbols successful, "
                   f"{total_records} total records collected")
        
        return results
    
    def collect_predefined_universe(
        self,
        universe_name: str,
        days_back: int = 252  # 1 year of trading days
    ) -> List[CollectionResult]:
        """
        Collect data for a predefined universe of symbols.
        
        Args:
            universe_name: Name of predefined universe (global_indices, major_currencies, etc.)
            days_back: Number of days back to collect
            
        Returns:
            List of CollectionResult objects
        """
        logger.info(f"Collecting predefined universe: {universe_name}")
        
        # Get symbol lists from configuration
        symbol_config = {}
        
        if universe_name == "global_indices":
            symbol_config = self.yahoo_config.get("equities", {}).get("global_indices", {})
        elif universe_name == "major_currencies":
            symbol_config = self.yahoo_config.get("currencies", {}).get("major_pairs", {})
        elif universe_name == "commodities":
            symbol_config = self.yahoo_config.get("commodities", {}).get("major_commodities", {})
        elif universe_name == "crypto":
            symbol_config = self.yahoo_config.get("crypto", {}).get("major_crypto", {})
        
        if not symbol_config:
            logger.error(f"Unknown universe: {universe_name}")
            return []
        
        # Extract symbols and asset classes
        symbols = list(symbol_config.keys())
        asset_classes = {symbol: data.get("asset_class", "equity") 
                        for symbol, data in symbol_config.items()}
        
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back)
        
        # Collect data
        return self.collect_batch(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            asset_classes=asset_classes
        )


# Example usage and testing
if __name__ == "__main__":
    # Test Yahoo Finance collector
    try:
        collector = YahooFinanceCollector()
        print("✅ Yahoo Finance collector initialized!")
        
        # Test single symbol collection
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        result = collector.collect_symbol_data(
            symbol="AAPL",
            start_date=start_date,
            end_date=end_date,
            asset_class="equity"
        )
        
        print(f"Collection result: {result.success}")
        print(f"Records collected: {result.records_collected}")
        print(f"Data quality: {result.data_quality_score:.2f}")
        
    except Exception as e:
        print(f"❌ Error: {e}") 
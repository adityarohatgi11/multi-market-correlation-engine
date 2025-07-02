"""
ETL Pipeline for Multi-Market Correlation Engine
=============================================

Comprehensive data collection, transformation, and loading pipeline
for financial market data from multiple sources.

Author: Multi-Market Correlation Engine Team
Version: 1.0.0
"""

import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import yfinance as yf
import requests
from dataclasses import dataclass
import sqlite3
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ETLConfig:
    """Configuration for ETL pipeline."""
    data_sources: List[str]
    symbols: List[str]
    update_frequency: str  # 'real-time', 'hourly', 'daily'
    batch_size: int
    max_workers: int
    retry_attempts: int
    output_path: str
    database_path: str

@dataclass
class DataQualityMetrics:
    """Data quality assessment metrics."""
    completeness_score: float
    accuracy_score: float
    timeliness_score: float
    consistency_score: float
    total_records: int
    missing_records: int
    outliers_detected: int
    validation_errors: List[str]

class DataCollector:
    """Collects data from various financial data sources."""
    
    def __init__(self, config: ETLConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Multi-Market-Correlation-Engine/1.0'
        })
    
    async def collect_yahoo_finance_data(self, symbols: List[str], period: str = "1mo") -> pd.DataFrame:
        """Collect data from Yahoo Finance."""
        logger.info(f"Collecting Yahoo Finance data for {len(symbols)} symbols")
        
        try:
            # Use yfinance to download data
            data_frames = []
            
            with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                future_to_symbol = {
                    executor.submit(self._fetch_yahoo_symbol, symbol, period): symbol 
                    for symbol in symbols
                }
                
                for future in as_completed(future_to_symbol):
                    symbol = future_to_symbol[future]
                    try:
                        symbol_data = future.result()
                        if symbol_data is not None and not symbol_data.empty:
                            symbol_data['symbol'] = symbol
                            data_frames.append(symbol_data)
                        else:
                            logger.warning(f"No data retrieved for {symbol}")
                    except Exception as e:
                        logger.error(f"Error fetching data for {symbol}: {e}")
            
            if data_frames:
                combined_data = pd.concat(data_frames, ignore_index=True)
                logger.info(f"Successfully collected data for {len(data_frames)} symbols")
                return combined_data
            else:
                logger.warning("No data collected from Yahoo Finance")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Yahoo Finance collection failed: {e}")
            return pd.DataFrame()
    
    def _fetch_yahoo_symbol(self, symbol: str, period: str) -> Optional[pd.DataFrame]:
        """Fetch data for a single symbol from Yahoo Finance."""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return None
            
            # Reset index to make Date a column
            hist = hist.reset_index()
            hist.columns = hist.columns.str.lower()
            
            # Add metadata
            hist['source'] = 'yahoo_finance'
            hist['collected_at'] = datetime.now()
            
            return hist
            
        except Exception as e:
            logger.error(f"Failed to fetch {symbol}: {e}")
            return None
    
    async def collect_fred_data(self) -> pd.DataFrame:
        """Collect economic indicators from FRED."""
        logger.info("Collecting FRED economic data")
        
        # Mock FRED data for demonstration
        # In production, you would use the FRED API
        fred_indicators = {
            'GDPC1': 'Real GDP',
            'FEDFUNDS': 'Federal Funds Rate', 
            'UNRATE': 'Unemployment Rate',
            'CPIAUCSL': 'Consumer Price Index',
            'DGS10': '10-Year Treasury Rate'
        }
        
        data_records = []
        for indicator_id, name in fred_indicators.items():
            # Generate mock data
            dates = pd.date_range(
                start=datetime.now() - timedelta(days=30),
                end=datetime.now(),
                freq='D'
            )
            
            for date in dates:
                value = np.random.normal(100, 10) if indicator_id == 'GDPC1' else np.random.normal(2.5, 0.5)
                data_records.append({
                    'date': date,
                    'indicator_id': indicator_id,
                    'indicator_name': name,
                    'value': round(value, 4),
                    'source': 'fred',
                    'collected_at': datetime.now()
                })
        
        return pd.DataFrame(data_records)
    
    async def collect_crypto_data(self, crypto_symbols: List[str]) -> pd.DataFrame:
        """Collect cryptocurrency data."""
        logger.info(f"Collecting crypto data for {len(crypto_symbols)} symbols")
        
        # For demo purposes, generate mock crypto data
        # In production, you would use CoinGecko or similar API
        data_records = []
        
        for symbol in crypto_symbols:
            dates = pd.date_range(
                start=datetime.now() - timedelta(days=30),
                end=datetime.now(),
                freq='H'  # Hourly data for crypto
            )
            
            base_price = np.random.uniform(100, 50000)  # Random base price
            
            for i, date in enumerate(dates):
                # Generate realistic price movement
                change = np.random.normal(0, 0.02)  # 2% standard deviation
                price = base_price * (1 + change)
                volume = np.random.uniform(1000000, 10000000)
                
                data_records.append({
                    'date': date,
                    'symbol': symbol,
                    'price': round(price, 2),
                    'volume': int(volume),
                    'market_cap': price * 21000000,  # Rough estimate
                    'source': 'coingecko',
                    'collected_at': datetime.now()
                })
                
                base_price = price  # Use current price as base for next
        
        return pd.DataFrame(data_records)

class DataTransformer:
    """Transforms and cleans collected data."""
    
    def __init__(self, config: ETLConfig):
        self.config = config
    
    def clean_market_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize market data."""
        logger.info(f"Cleaning market data with {len(df)} records")
        
        if df.empty:
            return df
        
        # Create a copy to avoid modifying original
        cleaned_df = df.copy()
        
        # Standardize column names
        column_mapping = {
            'Date': 'date',
            'Open': 'open',
            'High': 'high', 
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume',
            'Adj Close': 'adj_close'
        }
        
        cleaned_df.rename(columns=column_mapping, inplace=True)
        
        # Convert date column to datetime
        if 'date' in cleaned_df.columns:
            cleaned_df['date'] = pd.to_datetime(cleaned_df['date'])
        
        # Remove rows with missing critical data
        critical_columns = ['date', 'close']
        available_critical = [col for col in critical_columns if col in cleaned_df.columns]
        cleaned_df = cleaned_df.dropna(subset=available_critical)
        
        # Handle outliers in price data
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        available_numeric = [col for col in numeric_columns if col in cleaned_df.columns]
        
        for col in available_numeric:
            if col in cleaned_df.columns:
                # Remove extreme outliers (beyond 3 standard deviations)
                mean_val = cleaned_df[col].mean()
                std_val = cleaned_df[col].std()
                lower_bound = mean_val - 3 * std_val
                upper_bound = mean_val + 3 * std_val
                
                outlier_mask = (cleaned_df[col] < lower_bound) | (cleaned_df[col] > upper_bound)
                outlier_count = outlier_mask.sum()
                
                if outlier_count > 0:
                    logger.warning(f"Removing {outlier_count} outliers from {col}")
                    cleaned_df = cleaned_df[~outlier_mask]
        
        # Add derived features
        if 'high' in cleaned_df.columns and 'low' in cleaned_df.columns:
            cleaned_df['daily_range'] = cleaned_df['high'] - cleaned_df['low']
        
        if 'close' in cleaned_df.columns:
            cleaned_df['price_change'] = cleaned_df.groupby('symbol')['close'].pct_change()
        
        # Add data quality flags
        cleaned_df['data_quality_score'] = 1.0  # Default high quality
        cleaned_df['transformation_timestamp'] = datetime.now()
        
        logger.info(f"Cleaned data: {len(cleaned_df)} records remaining")
        return cleaned_df
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for market data."""
        logger.info("Calculating technical indicators")
        
        if df.empty or 'close' not in df.columns:
            return df
        
        enhanced_df = df.copy()
        
        # Group by symbol for indicator calculations
        for symbol in enhanced_df['symbol'].unique():
            symbol_mask = enhanced_df['symbol'] == symbol
            symbol_data = enhanced_df[symbol_mask].copy().sort_values('date')
            
            if len(symbol_data) < 20:  # Need enough data for indicators
                continue
            
            close_prices = symbol_data['close']
            
            # Simple Moving Averages
            symbol_data['sma_20'] = close_prices.rolling(window=20, min_periods=1).mean()
            symbol_data['sma_50'] = close_prices.rolling(window=50, min_periods=1).mean()
            
            # Exponential Moving Average
            symbol_data['ema_12'] = close_prices.ewm(span=12).mean()
            symbol_data['ema_26'] = close_prices.ewm(span=26).mean()
            
            # MACD
            symbol_data['macd'] = symbol_data['ema_12'] - symbol_data['ema_26']
            symbol_data['macd_signal'] = symbol_data['macd'].ewm(span=9).mean()
            
            # RSI (simplified)
            delta = close_prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            symbol_data['rsi'] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands
            rolling_mean = close_prices.rolling(window=20).mean()
            rolling_std = close_prices.rolling(window=20).std()
            symbol_data['bb_upper'] = rolling_mean + (rolling_std * 2)
            symbol_data['bb_lower'] = rolling_mean - (rolling_std * 2)
            
            # Volatility
            symbol_data['volatility'] = close_prices.pct_change().rolling(window=20).std() * np.sqrt(252)
            
            # Update the main dataframe
            enhanced_df.loc[symbol_mask] = symbol_data
        
        logger.info("Technical indicators calculated")
        return enhanced_df

class DataQualityChecker:
    """Assesses and monitors data quality."""
    
    def __init__(self, config: ETLConfig):
        self.config = config
    
    def assess_data_quality(self, df: pd.DataFrame) -> DataQualityMetrics:
        """Comprehensive data quality assessment."""
        logger.info("Assessing data quality")
        
        if df.empty:
            return DataQualityMetrics(
                completeness_score=0.0,
                accuracy_score=0.0,
                timeliness_score=0.0,
                consistency_score=0.0,
                total_records=0,
                missing_records=0,
                outliers_detected=0,
                validation_errors=["No data available"]
            )
        
        total_records = len(df)
        validation_errors = []
        
        # Completeness check
        missing_data = df.isnull().sum().sum()
        total_cells = total_records * len(df.columns)
        completeness_score = 1.0 - (missing_data / total_cells) if total_cells > 0 else 0.0
        
        # Accuracy check (detect outliers)
        outliers_detected = 0
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if col in ['close', 'open', 'high', 'low']:  # Price columns
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outlier_mask = (df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))
                outliers_detected += outlier_mask.sum()
        
        accuracy_score = 1.0 - (outliers_detected / total_records) if total_records > 0 else 0.0
        
        # Timeliness check
        timeliness_score = 1.0  # Default, would check against expected update times
        if 'collected_at' in df.columns:
            latest_collection = pd.to_datetime(df['collected_at']).max()
            time_diff = datetime.now() - latest_collection
            if time_diff > timedelta(hours=1):
                timeliness_score = max(0.0, 1.0 - (time_diff.total_seconds() / 86400))  # Decay over 24h
        
        # Consistency check
        consistency_score = 1.0  # Default, would check cross-validation rules
        
        # Symbol validation
        if 'symbol' in df.columns:
            invalid_symbols = df['symbol'].isna().sum()
            if invalid_symbols > 0:
                validation_errors.append(f"{invalid_symbols} records with missing symbols")
        
        # Price validation
        if 'close' in df.columns:
            negative_prices = (df['close'] <= 0).sum()
            if negative_prices > 0:
                validation_errors.append(f"{negative_prices} records with invalid prices")
        
        return DataQualityMetrics(
            completeness_score=completeness_score,
            accuracy_score=accuracy_score,
            timeliness_score=timeliness_score,
            consistency_score=consistency_score,
            total_records=total_records,
            missing_records=missing_data,
            outliers_detected=outliers_detected,
            validation_errors=validation_errors
        )

class DataLoader:
    """Loads processed data into storage systems."""
    
    def __init__(self, config: ETLConfig):
        self.config = config
        self.db_path = config.database_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Market data table
                conn.execute('''
                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    adj_close REAL,
                    source TEXT,
                    collected_at TEXT,
                    data_quality_score REAL,
                    UNIQUE(date, symbol, source)
                )
                ''')
                
                # Technical indicators table
                conn.execute('''
                CREATE TABLE IF NOT EXISTS technical_indicators (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    sma_20 REAL,
                    sma_50 REAL,
                    ema_12 REAL,
                    ema_26 REAL,
                    macd REAL,
                    macd_signal REAL,
                    rsi REAL,
                    bb_upper REAL,
                    bb_lower REAL,
                    volatility REAL,
                    UNIQUE(date, symbol)
                )
                ''')
                
                # ETL runs table
                conn.execute('''
                CREATE TABLE IF NOT EXISTS etl_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT UNIQUE,
                    start_time TEXT,
                    end_time TEXT,
                    status TEXT,
                    records_processed INTEGER,
                    errors_count INTEGER,
                    data_quality_score REAL,
                    config TEXT
                )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def load_market_data(self, df: pd.DataFrame) -> bool:
        """Load market data into database."""
        if df.empty:
            logger.warning("No market data to load")
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Prepare data for insertion
                df_to_load = df.copy()
                
                # Ensure required columns exist
                required_columns = ['date', 'symbol']
                missing_columns = [col for col in required_columns if col not in df_to_load.columns]
                if missing_columns:
                    logger.error(f"Missing required columns: {missing_columns}")
                    return False
                
                # Convert datetime to string for SQLite
                if 'date' in df_to_load.columns:
                    df_to_load['date'] = df_to_load['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
                if 'collected_at' in df_to_load.columns:
                    df_to_load['collected_at'] = pd.to_datetime(df_to_load['collected_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
                
                # Load data using replace strategy for duplicates
                df_to_load.to_sql('market_data', conn, if_exists='append', index=False)
                
                logger.info(f"Successfully loaded {len(df_to_load)} market data records")
                return True
                
        except Exception as e:
            logger.error(f"Failed to load market data: {e}")
            return False
    
    def log_etl_run(self, run_id: str, start_time: datetime, end_time: datetime, 
                   status: str, records_processed: int, errors_count: int, 
                   data_quality_score: float, config: Dict) -> bool:
        """Log ETL run information."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                INSERT OR REPLACE INTO etl_runs 
                (run_id, start_time, end_time, status, records_processed, errors_count, data_quality_score, config)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    run_id,
                    start_time.isoformat(),
                    end_time.isoformat(),
                    status,
                    records_processed,
                    errors_count,
                    data_quality_score,
                    json.dumps(config.__dict__ if hasattr(config, '__dict__') else config)
                ))
                
                conn.commit()
                logger.info(f"ETL run {run_id} logged successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to log ETL run: {e}")
            return False

class ETLPipeline:
    """Main ETL pipeline orchestrator."""
    
    def __init__(self, config: ETLConfig):
        self.config = config
        self.collector = DataCollector(config)
        self.transformer = DataTransformer(config)
        self.quality_checker = DataQualityChecker(config)
        self.loader = DataLoader(config)
        
    async def run_pipeline(self, run_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute the complete ETL pipeline."""
        if run_id is None:
            run_id = f"etl_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        start_time = datetime.now()
        logger.info(f"Starting ETL pipeline run: {run_id}")
        
        try:
            results = {
                'run_id': run_id,
                'start_time': start_time,
                'status': 'running',
                'stages': {},
                'data_quality': None,
                'errors': []
            }
            
            # Stage 1: Data Collection
            logger.info("Stage 1: Data Collection")
            collection_start = datetime.now()
            
            # Split symbols by data source
            stock_symbols = [s for s in self.config.symbols if not s.endswith('-USD')]
            crypto_symbols = [s for s in self.config.symbols if s.endswith('-USD')]
            
            # Collect data from different sources
            market_data_frames = []
            
            if 'yahoo_finance' in self.config.data_sources and stock_symbols:
                yahoo_data = await self.collector.collect_yahoo_finance_data(stock_symbols)
                if not yahoo_data.empty:
                    market_data_frames.append(yahoo_data)
            
            if 'fred' in self.config.data_sources:
                fred_data = await self.collector.collect_fred_data()
                # Note: FRED data structure is different, handle separately
            
            if 'coingecko' in self.config.data_sources and crypto_symbols:
                crypto_data = await self.collector.collect_crypto_data(crypto_symbols)
                if not crypto_data.empty:
                    market_data_frames.append(crypto_data)
            
            # Combine market data
            if market_data_frames:
                raw_market_data = pd.concat(market_data_frames, ignore_index=True)
            else:
                raw_market_data = pd.DataFrame()
            
            collection_duration = (datetime.now() - collection_start).total_seconds()
            results['stages']['data_collection'] = {
                'duration_seconds': collection_duration,
                'records_collected': len(raw_market_data),
                'status': 'completed'
            }
            
            # Stage 2: Data Transformation
            logger.info("Stage 2: Data Transformation")
            transform_start = datetime.now()
            
            cleaned_data = self.transformer.clean_market_data(raw_market_data)
            enhanced_data = self.transformer.calculate_technical_indicators(cleaned_data)
            
            transform_duration = (datetime.now() - transform_start).total_seconds()
            results['stages']['data_transformation'] = {
                'duration_seconds': transform_duration,
                'records_transformed': len(enhanced_data),
                'status': 'completed'
            }
            
            # Stage 3: Data Quality Assessment
            logger.info("Stage 3: Data Quality Assessment")
            quality_start = datetime.now()
            
            quality_metrics = self.quality_checker.assess_data_quality(enhanced_data)
            
            quality_duration = (datetime.now() - quality_start).total_seconds()
            results['stages']['data_quality'] = {
                'duration_seconds': quality_duration,
                'quality_score': (quality_metrics.completeness_score + 
                                quality_metrics.accuracy_score + 
                                quality_metrics.timeliness_score + 
                                quality_metrics.consistency_score) / 4,
                'status': 'completed'
            }
            results['data_quality'] = quality_metrics.__dict__
            
            # Stage 4: Data Loading
            logger.info("Stage 4: Data Loading")
            load_start = datetime.now()
            
            load_success = self.loader.load_market_data(enhanced_data)
            
            load_duration = (datetime.now() - load_start).total_seconds()
            results['stages']['data_loading'] = {
                'duration_seconds': load_duration,
                'records_loaded': len(enhanced_data) if load_success else 0,
                'status': 'completed' if load_success else 'failed'
            }
            
            # Complete pipeline
            end_time = datetime.now()
            total_duration = (end_time - start_time).total_seconds()
            
            results.update({
                'end_time': end_time,
                'total_duration_seconds': total_duration,
                'status': 'completed',
                'records_processed': len(enhanced_data),
                'errors_count': len(quality_metrics.validation_errors)
            })
            
            # Log the run
            overall_quality_score = (quality_metrics.completeness_score + 
                                   quality_metrics.accuracy_score + 
                                   quality_metrics.timeliness_score + 
                                   quality_metrics.consistency_score) / 4
            
            self.loader.log_etl_run(
                run_id=run_id,
                start_time=start_time,
                end_time=end_time,
                status='completed',
                records_processed=len(enhanced_data),
                errors_count=len(quality_metrics.validation_errors),
                data_quality_score=overall_quality_score,
                config=self.config
            )
            
            logger.info(f"ETL pipeline {run_id} completed successfully in {total_duration:.2f} seconds")
            return results
            
        except Exception as e:
            end_time = datetime.now()
            error_msg = f"ETL pipeline failed: {e}"
            logger.error(error_msg)
            
            results.update({
                'end_time': end_time,
                'status': 'failed',
                'error': str(e)
            })
            
            # Log the failed run
            self.loader.log_etl_run(
                run_id=run_id,
                start_time=start_time,
                end_time=end_time,
                status='failed',
                records_processed=0,
                errors_count=1,
                data_quality_score=0.0,
                config=self.config
            )
            
            return results

# Factory function for creating ETL pipeline
def create_etl_pipeline() -> ETLPipeline:
    """Create and configure ETL pipeline with default settings."""
    
    # Default symbol lists
    default_symbols = [
        # Tech stocks
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA',
        # Financial
        'JPM', 'BAC', 'GS', 'WFC',
        # Energy  
        'XOM', 'CVX',
        # Healthcare
        'JNJ', 'UNH', 'PFE',
        # Market ETFs
        'SPY', 'QQQ', 'IWM',
        # Crypto
        'BTC-USD', 'ETH-USD'
    ]
    
    config = ETLConfig(
        data_sources=['yahoo_finance', 'fred', 'coingecko'],
        symbols=default_symbols,
        update_frequency='daily',
        batch_size=100,
        max_workers=5,
        retry_attempts=3,
        output_path='data/processed',
        database_path='data/market_data.db'
    )
    
    # Ensure directories exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    
    return ETLPipeline(config)

# CLI interface for running ETL pipeline
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run ETL Pipeline')
    parser.add_argument('--symbols', nargs='+', help='List of symbols to process')
    parser.add_argument('--sources', nargs='+', default=['yahoo_finance'], 
                       help='Data sources to use')
    parser.add_argument('--workers', type=int, default=5, help='Number of worker threads')
    
    args = parser.parse_args()
    
    # Create pipeline
    pipeline = create_etl_pipeline()
    
    # Override config if arguments provided
    if args.symbols:
        pipeline.config.symbols = args.symbols
    if args.sources:
        pipeline.config.data_sources = args.sources
    if args.workers:
        pipeline.config.max_workers = args.workers
    
    # Run pipeline
    async def main():
        results = await pipeline.run_pipeline()
        print(f"ETL Pipeline completed: {results['status']}")
        print(f"Records processed: {results['records_processed']}")
        print(f"Duration: {results['total_duration_seconds']:.2f} seconds")
        
        if results.get('data_quality'):
            quality = results['data_quality']
            print(f"Data Quality Score: {quality.get('completeness_score', 0):.2f}")
    
    asyncio.run(main()) 
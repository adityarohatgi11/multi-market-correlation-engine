"""
Data Collection Agent for Multi-Market Correlation Engine

This agent handles automated data collection from various market data sources
with scheduling, quality monitoring, and error handling.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import pandas as pd
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional
import schedule
import threading

from .base_agent import BaseAgent, Task, TaskPriority, AgentStatus
from ..collectors.yahoo_finance_collector import YahooFinanceCollector
from ..data.database_manager import DatabaseManager


class DataCollectionAgent(BaseAgent):
    """
    Agent responsible for automated market data collection.
    
    Features:
    - Scheduled data collection
    - Multiple data source support
    - Data quality monitoring
    - Error handling and retry logic
    - Real-time and historical data collection
    """
    
    def __init__(self, agent_id: str = "data-collector-001", 
                 name: str = "Data Collection Agent", 
                 config: Optional[Dict] = None):
        """
        Initialize the data collection agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name for the agent
            config: Configuration dictionary
        """
        default_config = {
            'collection_interval': 300,  # 5 minutes
            'symbols': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],  # Default symbols, will be updated later
            'data_sources': ['yahoo_finance'],
            'quality_threshold': 0.8,
            'retry_attempts': 3,
            'retry_delay': 60,
            'batch_size': 10,
            'enable_scheduling': True
        }
        
        if config:
            default_config.update(config)
        
        super().__init__(agent_id, name, default_config)
        
        # Update symbols with comprehensive list
        try:
            comprehensive_symbols = self._get_comprehensive_symbol_list()
            self.config['symbols'] = comprehensive_symbols
        except Exception as e:
            self.logger.warning(f'Failed to load comprehensive symbol list, using defaults: {e}')
        
        # Initialize components
        self.db_manager = DatabaseManager()
        self.collectors = self._initialize_collectors()
        
        # Data collection state
        self.last_collection_time = None
        self.collection_errors = []
        self.data_quality_scores = {}
        
        # Scheduling
        self.scheduler_thread = None
        self.schedule_active = False
        
        self.logger.info("Data Collection Agent initialized")
    
    def _initialize_collectors(self) -> Dict[str, Any]:
        """Initialize data collectors for different sources"""
        collectors = {}
        
        if 'yahoo_finance' in self.config['data_sources']:
            collectors['yahoo_finance'] = YahooFinanceCollector()
            self.logger.info("Yahoo Finance collector initialized")
        
        return collectors
    
    def execute_task(self, task: Task) -> Any:
        """Execute a data collection task"""
        task_type = task.data.get('type', 'unknown')
        
        try:
            if task_type == 'collect_real_time':
                return self._collect_real_time_data(task.data)
            elif task_type == 'collect_historical':
                return self._collect_historical_data(task.data)
            elif task_type == 'quality_check':
                return self._perform_quality_check(task.data)
            elif task_type == 'cleanup':
                return self._cleanup_old_data(task.data)
            elif task_type == 'health_check':
                return self._data_source_health_check(task.data)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
                
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            raise
    
    def _collect_real_time_data(self, task_data: Dict) -> Dict[str, Any]:
        """Collect real-time market data"""
        symbols = task_data.get('symbols', self.config['symbols'])
        source = task_data.get('source', 'yahoo_finance')
        
        if source not in self.collectors:
            raise ValueError(f"Unknown data source: {source}")
        
        collector = self.collectors[source]
        results = {}
        
        self.logger.info(f"Collecting real-time data for {len(symbols)} symbols")
        
        try:
            # Calculate date range for recent data (last 30 days)
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            
            # Collect data in batches
            batch_size = self.config['batch_size']
            for i in range(0, len(symbols), batch_size):
                batch_symbols = symbols[i:i + batch_size]
                
                # Collect data for this batch using collect_batch
                batch_results = collector.collect_batch(batch_symbols, start_date, end_date)
                
                # Process results
                successful_results = [r for r in batch_results if r.success]
                total_records = sum(r.records_collected for r in successful_results)
                
                if successful_results:
                    # Calculate average quality score for this batch
                    avg_quality = sum(r.data_quality_score or 0 for r in successful_results) / len(successful_results)
                    
                    results[f'batch_{i//batch_size + 1}'] = {
                        'symbols': batch_symbols,
                        'successful_symbols': [r.symbol for r in successful_results],
                        'records_stored': total_records,
                        'quality_score': avg_quality,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Update quality tracking
                    for result in successful_results:
                        self.data_quality_scores[result.symbol] = result.data_quality_score or 0
                
                # Log any errors
                failed_results = [r for r in batch_results if not r.success]
                for failed_result in failed_results:
                    self.collection_errors.append({
                        'error': failed_result.error_message,
                        'timestamp': datetime.now().isoformat(),
                        'symbol': failed_result.symbol,
                        'source': source
                    })
                
                # Small delay between batches
                time.sleep(1)
            
            self.last_collection_time = datetime.now()
            
            # Send success message
            self.send_message(
                'analysis-agent-001',
                'data_available',
                {'symbols': symbols, 'timestamp': self.last_collection_time.isoformat()}
            )
            
            return results
            
        except Exception as e:
            self.collection_errors.append({
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'symbols': symbols,
                'source': source
            })
            raise
    
    def _collect_historical_data(self, task_data: Dict) -> Dict[str, Any]:
        """Collect historical market data"""
        symbols = task_data.get('symbols', self.config['symbols'])
        period = task_data.get('period', '1y')
        source = task_data.get('source', 'yahoo_finance')
        
        if source not in self.collectors:
            raise ValueError(f"Unknown data source: {source}")
        
        collector = self.collectors[source]
        results = {}
        
        self.logger.info(f"Collecting historical data for {len(symbols)} symbols ({period})")
        
        try:
            # Convert period to date range
            end_date = date.today()
            if period == '1d':
                start_date = end_date - timedelta(days=1)
            elif period == '1w':
                start_date = end_date - timedelta(weeks=1)
            elif period == '1mo':
                start_date = end_date - timedelta(days=30)
            elif period == '3mo':
                start_date = end_date - timedelta(days=90)
            elif period == '6mo':
                start_date = end_date - timedelta(days=180)
            elif period == '1y':
                start_date = end_date - timedelta(days=365)
            elif period == '2y':
                start_date = end_date - timedelta(days=730)
            else:
                start_date = end_date - timedelta(days=365)  # Default to 1 year
            
            # Collect data using collect_batch
            batch_results = collector.collect_batch(symbols, start_date, end_date)
            
            # Process results
            successful_results = [r for r in batch_results if r.success]
            total_records = sum(r.records_collected for r in successful_results)
            
            if successful_results:
                # Calculate average quality score
                avg_quality = sum(r.data_quality_score or 0 for r in successful_results) / len(successful_results)
                
                results = {
                    'symbols': symbols,
                    'successful_symbols': [r.symbol for r in successful_results],
                    'period': period,
                    'records_stored': total_records,
                    'quality_score': avg_quality,
                    'data_range': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    },
                    'timestamp': datetime.now().isoformat()
                }
                
                # Update quality tracking
                for result in successful_results:
                    self.data_quality_scores[result.symbol] = result.data_quality_score or 0
            
            # Log any errors
            failed_results = [r for r in batch_results if not r.success]
            for failed_result in failed_results:
                self.collection_errors.append({
                    'error': failed_result.error_message,
                    'timestamp': datetime.now().isoformat(),
                    'symbol': failed_result.symbol,
                    'source': source,
                    'period': period
                })
            
            return results
            
        except Exception as e:
            self.collection_errors.append({
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'symbols': symbols,
                'source': source,
                'period': period
            })
            raise
    
    def _calculate_quality_score(self, data: pd.DataFrame) -> float:
        """Calculate data quality score"""
        if data is None or data.empty:
            return 0.0
        
        # Check for missing values
        missing_ratio = data.isnull().sum().sum() / (data.shape[0] * data.shape[1])
        
        # Check for duplicate entries
        duplicate_ratio = data.duplicated().sum() / len(data)
        
        # Check for outliers (using IQR method)
        outlier_ratio = 0.0
        numeric_columns = data.select_dtypes(include=['float64', 'int64']).columns
        
        if len(numeric_columns) > 0:
            total_outliers = 0
            total_values = 0
            
            for col in numeric_columns:
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = ((data[col] < lower_bound) | (data[col] > upper_bound)).sum()
                total_outliers += outliers
                total_values += len(data[col].dropna())
            
            if total_values > 0:
                outlier_ratio = total_outliers / total_values
        
        # Calculate overall quality score
        quality_score = 1.0 - (missing_ratio * 0.4 + duplicate_ratio * 0.3 + outlier_ratio * 0.3)
        return max(0.0, min(1.0, quality_score))
    
    def _perform_quality_check(self, task_data: Dict) -> Dict[str, Any]:
        """Perform data quality check"""
        lookback_hours = task_data.get('lookback_hours', 24)
        
        # Get recent data from database
        cutoff_time = datetime.now() - timedelta(hours=lookback_hours)
        
        try:
            # This would need to be implemented in DatabaseManager
            # recent_data = self.db_manager.get_data_since(cutoff_time)
            
            # For now, return a mock quality report
            quality_report = {
                'overall_quality': sum(self.data_quality_scores.values()) / len(self.data_quality_scores) if self.data_quality_scores else 0.0,
                'symbol_quality': self.data_quality_scores,
                'recent_errors': len([e for e in self.collection_errors if datetime.fromisoformat(e['timestamp']) > cutoff_time]),
                'last_collection': self.last_collection_time.isoformat() if self.last_collection_time else None,
                'timestamp': datetime.now().isoformat()
            }
            
            return quality_report
            
        except Exception as e:
            self.logger.error(f"Quality check failed: {e}")
            raise
    
    def _cleanup_old_data(self, task_data: Dict) -> Dict[str, Any]:
        """Clean up old data from database"""
        retention_days = task_data.get('retention_days', 365)
        
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        try:
            # This would need to be implemented in DatabaseManager
            # deleted_records = self.db_manager.delete_data_before(cutoff_date)
            
            # For now, return a mock cleanup report
            cleanup_report = {
                'cutoff_date': cutoff_date.isoformat(),
                'deleted_records': 0,  # Would be actual count
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Data cleanup completed: {cleanup_report}")
            return cleanup_report
            
        except Exception as e:
            self.logger.error(f"Data cleanup failed: {e}")
            raise
    
    def _data_source_health_check(self, task_data: Dict) -> Dict[str, Any]:
        """Check health of data sources"""
        health_status = {}
        
        for source_name, collector in self.collectors.items():
            try:
                # Test with a simple data request using collect_batch
                end_date = date.today()
                start_date = end_date - timedelta(days=1)
                test_results = collector.collect_batch(['AAPL'], start_date, end_date)
                
                # Check if we got a successful result
                test_success = any(r.success for r in test_results) if test_results else False
                
                health_status[source_name] = {
                    'healthy': test_success,
                    'last_test': datetime.now().isoformat(),
                    'error': None
                }
                
            except Exception as e:
                health_status[source_name] = {
                    'healthy': False,
                    'last_test': datetime.now().isoformat(),
                    'error': str(e)
                }
        
        return health_status
    
    def start_scheduled_collection(self):
        """Start scheduled data collection"""
        if not self.config['enable_scheduling']:
            self.logger.info("Scheduled collection disabled in config")
            return
        
        if self.schedule_active:
            self.logger.warning("Scheduled collection already active")
            return
        
        # Schedule regular data collection
        interval_minutes = self.config['collection_interval'] // 60
        schedule.every(interval_minutes).minutes.do(self._schedule_real_time_collection)
        
        # Schedule daily quality checks
        schedule.every().day.at("09:00").do(self._schedule_quality_check)
        
        # Schedule weekly cleanup
        schedule.every().sunday.at("02:00").do(self._schedule_cleanup)
        
        # Start scheduler thread
        self.schedule_active = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("Scheduled data collection started")
    
    def stop_scheduled_collection(self):
        """Stop scheduled data collection"""
        self.schedule_active = False
        schedule.clear()
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5.0)
        
        self.logger.info("Scheduled data collection stopped")
    
    def _run_scheduler(self):
        """Run the scheduler in a separate thread"""
        while self.schedule_active:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def _schedule_real_time_collection(self):
        """Schedule a real-time data collection task"""
        self.create_task(
            "Scheduled Real-Time Collection",
            {
                'type': 'collect_real_time',
                'symbols': self.config['symbols'],
                'source': 'yahoo_finance'
            },
            priority=TaskPriority.MEDIUM
        )
    
    def _schedule_quality_check(self):
        """Schedule a quality check task"""
        self.create_task(
            "Scheduled Quality Check",
            {
                'type': 'quality_check',
                'lookback_hours': 24
            },
            priority=TaskPriority.LOW
        )
    
    def _schedule_cleanup(self):
        """Schedule a data cleanup task"""
        self.create_task(
            "Scheduled Data Cleanup",
            {
                'type': 'cleanup',
                'retention_days': 365
            },
            priority=TaskPriority.LOW
        )
    
    def get_collection_status(self) -> Dict[str, Any]:
        """Get detailed collection status"""
        return {
            'last_collection': self.last_collection_time.isoformat() if self.last_collection_time else None,
            'quality_scores': self.data_quality_scores,
            'recent_errors': self.collection_errors[-10:],  # Last 10 errors
            'scheduled_collection_active': self.schedule_active,
            'data_sources': list(self.collectors.keys()),
            'configured_symbols': self.config['symbols']
        }
    
    def force_collection(self, symbols: Optional[List[str]] = None) -> str:
        """Force immediate data collection"""
        symbols = symbols or self.config['symbols']
        
        task = self.create_task(
            "Manual Data Collection",
            {
                'type': 'collect_real_time',
                'symbols': symbols,
                'source': 'yahoo_finance'
            },
            priority=TaskPriority.HIGH
        )
        
        return task.id
    
    def _get_comprehensive_symbol_list(self) -> List[str]:
        """Get comprehensive symbol list from data_sources.yaml configuration."""
        try:
            from src.config.config_manager import get_config
            config = get_config()
            yahoo_config = config.get_data_source_config("yahoo_finance")
            
            # Collect all symbols from different categories
            all_symbols = []
            
            # Global indices
            equities = yahoo_config.get('equities', {})
            all_symbols.extend(equities.get('global_indices', []))
            all_symbols.extend(equities.get('sector_etfs', []))
            
            # Other asset classes
            all_symbols.extend(yahoo_config.get('commodities', []))
            all_symbols.extend(yahoo_config.get('bonds', []))
            all_symbols.extend(yahoo_config.get('currencies', []))
            
            # Remove duplicates while preserving order
            unique_symbols = []
            seen = set()
            for symbol in all_symbols:
                if symbol not in seen:
                    unique_symbols.append(symbol)
                    seen.add(symbol)
            
            self.logger.info(f"Loaded {len(unique_symbols)} symbols from configuration")
            return unique_symbols
            
        except Exception as e:
            self.logger.warning(f"Failed to load comprehensive symbol list: {e}")
            # Fallback to expanded default set
            return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'BAC', 'XOM', 
                   'SPY', 'QQQ', 'IWM', 'VTI', 'GLD', 'TLT', '^GSPC', '^IXIC']


if __name__ == "__main__":
    # Test the data collection agent
    agent = DataCollectionAgent()
    
    # Start the agent
    agent.start()
    
    # Force a data collection
    task_id = agent.force_collection(['AAPL', 'MSFT'])
    print(f"Started collection task: {task_id}")
    
    # Wait for task completion
    time.sleep(10)
    
    # Check status
    status = agent.get_collection_status()
    print("Collection Status:")
    print(f"Last collection: {status['last_collection']}")
    print(f"Quality scores: {status['quality_scores']}")
    
    # Stop the agent
    agent.stop()
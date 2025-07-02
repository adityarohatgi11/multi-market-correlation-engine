#!/usr/bin/env python3
"""
Enhanced Data Collection Pipeline
================================

Comprehensive data collection using the full symbol universe from data_sources.yaml
instead of the limited default symbol set.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
import logging

from src.collectors.yahoo_finance_collector import YahooFinanceCollector
from src.data.database_manager import get_db_manager
from src.config.config_manager import get_config

# Configure logging
logging.basicConfig(
level=logging.INFO,
format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EnhancedDataCollector:
"""Enhanced data collector that uses the full symbol universe."""

def __init__(self):
"""Initialize the enhanced data collector."""
self.config = get_config()
self.db_manager = get_db_manager()
self.yahoo_collector = YahooFinanceCollector()

# Load the full symbol universe from configuration
self.symbol_universe = self._load_symbol_universe()

logger.info(f"Enhanced Data Collector initialized")

def _load_symbol_universe(self) -> Dict[str, List[str]]:
"""Load the complete symbol universe from data_sources.yaml"""
try:
# Load Yahoo Finance symbols
yahoo_config = self.config.get_data_source_config("yahoo_finance")

symbols = {
'global_indices': yahoo_config.get('equities', {}).get('global_indices', []),
'sector_etfs': yahoo_config.get('equities', {}).get('sector_etfs', []),
'commodities': yahoo_config.get('commodities', []),
'bonds': yahoo_config.get('bonds', []),
'currencies': yahoo_config.get('currencies', [])
}

# Count total symbols
total_symbols = sum(len(symbol_list) for symbol_list in symbols.values())
logger.info(f"Loaded {total_symbols} symbols from configuration:")
for category, symbol_list in symbols.items():
logger.info(f" {category}: {len(symbol_list)} symbols")

return symbols

except Exception as e:
logger.error(f"Failed to load symbol universe: {e}")
# Fallback to default symbols
return {
'fallback': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'BAC', 'XOM']
}

def collect_all_symbols(self, days_back: int = 365) -> Dict[str, Any]:
"""Collect data for all symbols in the universe."""
end_date = date.today()
start_date = end_date - timedelta(days=days_back)

logger.info(f"Starting comprehensive data collection from {start_date} to {end_date}")

# Flatten all symbols
all_symbols = []
asset_class_map = {}

for category, symbols in self.symbol_universe.items():
for symbol in symbols:
all_symbols.append(symbol)
if category == 'global_indices':
asset_class_map[symbol] = 'index'
elif category == 'sector_etfs':
asset_class_map[symbol] = 'etf'
elif category == 'commodities':
asset_class_map[symbol] = 'commodity'
elif category == 'bonds':
asset_class_map[symbol] = 'bond'
elif category == 'currencies':
asset_class_map[symbol] = 'currency'
else:
asset_class_map[symbol] = 'equity'

logger.info(f"Collecting data for {len(all_symbols)} symbols")

# Collect in batches
batch_size = 8
all_results = []
successful = 0
failed = 0

for i in range(0, len(all_symbols), batch_size):
batch_symbols = all_symbols[i:i + batch_size]
batch_num = i // batch_size + 1
total_batches = (len(all_symbols) + batch_size - 1) // batch_size

logger.info(f"Processing batch {batch_num}/{total_batches}: {batch_symbols}")

try:
batch_results = self.yahoo_collector.collect_batch(
symbols=batch_symbols,
start_date=start_date,
end_date=end_date,
asset_classes=asset_class_map
)

all_results.extend(batch_results)

batch_successful = sum(1 for r in batch_results if r.success)
batch_failed = len(batch_results) - batch_successful

successful += batch_successful
failed += batch_failed

logger.info(f"Batch {batch_num}: {batch_successful} successful, {batch_failed} failed")
time.sleep(1)

except Exception as e:
logger.error(f"Batch {batch_num} failed: {e}")
failed += len(batch_symbols)

return {
'total_symbols': len(all_symbols),
'successful': successful,
'failed': failed,
'success_rate': successful / len(all_symbols) * 100 if all_symbols else 0,
'total_records': sum(r.records_collected for r in all_results if r.success),
'successful_symbols': [r.symbol for r in all_results if r.success],
'failed_symbols': [r.symbol for r in all_results if not r.success]
}

def run_collection(self, days_back: int = 730):
"""Run the enhanced collection pipeline."""
print(" Enhanced Data Collection Pipeline")
print("=" * 50)

# Show current database status
try:
import pandas as pd
with self.db_manager.get_session() as session:
query = 'SELECT COUNT(DISTINCT symbol) as unique_symbols, COUNT(*) as total_records FROM market_data'
result = pd.read_sql(query, session.bind)
initial_symbols = result.iloc[0]['unique_symbols']
initial_records = result.iloc[0]['total_records']

print(f" Initial database: {initial_symbols} symbols, {initial_records} records")
except:
initial_symbols = 0
initial_records = 0
print(" Initial database: Empty or inaccessible")

# Run collection
results = self.collect_all_symbols(days_back=days_back)

# Show final status
try:
with self.db_manager.get_session() as session:
query = 'SELECT COUNT(DISTINCT symbol) as unique_symbols, COUNT(*) as total_records FROM market_data'
result = pd.read_sql(query, session.bind)
final_symbols = result.iloc[0]['unique_symbols']
final_records = result.iloc[0]['total_records']

print(f" Final database: {final_symbols} symbols, {final_records} records")
print(f" Added: {final_symbols - initial_symbols} symbols, {final_records - initial_records} records")
except:
print(" Final database: Unable to query")

print(f"\n Collection Results:")
print(f" Total symbols attempted: {results['total_symbols']}")
print(f" Successful: {results['successful']}")
print(f" Failed: {results['failed']}")
print(f" Success rate: {results['success_rate']:.1f}%")
print(f" Total records collected: {results['total_records']}")

if results['failed_symbols']:
print(f"\n Failed symbols: {results['failed_symbols']}")

print("\n Enhanced data collection completed!")


def main():
try:
collector = EnhancedDataCollector()
collector.run_collection(days_back=730) # 2 years of data
return 0
except Exception as e:
print(f" Collection failed: {e}")
return 1


if __name__ == "__main__":
exit(main())

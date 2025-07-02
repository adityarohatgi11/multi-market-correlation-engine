#!/usr/bin/env python3
"""
Comprehensive test script for Phase 1: Foundation Components
Tests: Database Manager, Yahoo Finance Collector, Basic Data Operations
"""

import sys
import os
import traceback
from datetime import datetime, timedelta
import sqlite3

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
"""Test all Phase 1 imports"""
print("=" * 60)
print("TESTING PHASE 1 IMPORTS")
print("=" * 60)

try:
from src.data.database_manager import DatabaseManager
print(" DatabaseManager import successful")
except Exception as e:
print(f" DatabaseManager import failed: {e}")
traceback.print_exc()
return False

try:
from src.collectors.yahoo_finance_collector import YahooFinanceCollector
print(" YahooFinanceCollector import successful")
except Exception as e:
print(f" YahooFinanceCollector import failed: {e}")
traceback.print_exc()
return False

return True

def setup_test_environment():
"""Set up test environment with test database"""
# Set environment variable for test database
os.environ["DATABASE_URL"] = "sqlite:///test_phase1.db"
print(" Test environment configured")

def test_database_manager():
"""Test DatabaseManager functionality"""
print("\n" + "=" * 60)
print("TESTING DATABASE MANAGER")
print("=" * 60)

try:
from src.data.database_manager import DatabaseManager
from sqlalchemy import text

# Initialize database manager (uses config)
db_manager = DatabaseManager()
print(" DatabaseManager initialization successful")

# Test connection by checking if we can get a session
try:
with db_manager.get_session() as session:
# Simple query to test connection (using text() for raw SQL)
result = session.execute(text("SELECT 1")).fetchone()
print(" Database connection test successful")
except Exception as e:
print(f" Database connection test failed: {e}")
return False

# Test that tables were created
from src.data.database_manager import Base
table_names = list(Base.metadata.tables.keys())
print(f" Tables created: {len(table_names)} tables")
for table in table_names:
print(f" - {table}")

return True

except Exception as e:
print(f" DatabaseManager test failed: {e}")
traceback.print_exc()
return False

def test_yahoo_finance_collector():
"""Test YahooFinanceCollector functionality"""
print("\n" + "=" * 60)
print("TESTING YAHOO FINANCE COLLECTOR")
print("=" * 60)

try:
from src.collectors.yahoo_finance_collector import YahooFinanceCollector

# Initialize collector (it gets db_manager internally)
collector = YahooFinanceCollector()
print(" YahooFinanceCollector initialization successful")

# Test single symbol collection
end_date = datetime.now().date()
start_date = end_date - timedelta(days=30)

print("Testing single symbol collection (AAPL)...")
result = collector.collect_symbol_data("AAPL", start_date, end_date)
if result.success:
print(f" Single symbol collection successful: {result.records_collected} records")
else:
print(f" Single symbol collection failed: {result.error_message}")
return False

# Test batch collection
print("Testing batch collection...")
symbols = ["MSFT", "GOOGL"]
batch_results = collector.collect_batch(symbols, start_date, end_date)
successful_collections = sum(1 for result in batch_results if result.success)
print(f" Batch collection: {successful_collections}/{len(symbols)} successful")

return True

except Exception as e:
print(f" YahooFinanceCollector test failed: {e}")
traceback.print_exc()
return False

def test_data_persistence():
"""Test data persistence and retrieval"""
print("\n" + "=" * 60)
print("TESTING DATA PERSISTENCE")
print("=" * 60)

try:
from src.data.database_manager import DatabaseManager

db_manager = DatabaseManager()

# Check if data was persisted using the DatabaseManager
test_symbols = ["AAPL", "MSFT", "GOOGL"]
end_date = datetime.now().date()
start_date = (datetime.now() - timedelta(days=30)).date()

market_data = db_manager.get_market_data(
symbols=test_symbols,
start_date=start_date,
end_date=end_date
)

if not market_data.empty:
print(f" Market data retrieved: {len(market_data)} records")
print(f" Symbols: {market_data.index.get_level_values('symbol').unique().tolist()}")
print(f" Date range: {market_data.index.get_level_values('date').min()} to {market_data.index.get_level_values('date').max()}")

# Show sample data
sample_data = market_data.head()
print(" Sample data:")
for (symbol, date), row in sample_data.iterrows():
print(f" {symbol} on {date.date()}: Close=${row['close']:.2f}")
else:
print(" No market data found in database")
return False

return True

except Exception as e:
print(f" Data persistence test failed: {e}")
traceback.print_exc()
return False

def cleanup_test_files():
"""Clean up test files"""
try:
if os.path.exists("test_phase1.db"):
os.remove("test_phase1.db")
print(" Test database cleaned up")
except Exception as e:
print(f" Cleanup warning: {e}")

def main():
"""Run all Phase 1 tests"""
print("PHASE 1 FOUNDATION TESTING")
print("=" * 60)

# Setup test environment
setup_test_environment()

test_results = []

# Test imports
test_results.append(("Imports", test_imports()))

# Test database manager
test_results.append(("Database Manager", test_database_manager()))

# Test yahoo finance collector
test_results.append(("Yahoo Finance Collector", test_yahoo_finance_collector()))

# Test data persistence
test_results.append(("Data Persistence", test_data_persistence()))

# Print summary
print("\n" + "=" * 60)
print("PHASE 1 TEST SUMMARY")
print("=" * 60)

passed = 0
for test_name, result in test_results:
status = " PASSED" if result else " FAILED"
print(f"{test_name}: {status}")
if result:
passed += 1

print(f"\nOverall: {passed}/{len(test_results)} tests passed")

# Cleanup
cleanup_test_files()

return passed == len(test_results)

if __name__ == "__main__":
success = main()
sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Full Data Update Script
======================

Convenient script to update all symbols in the database with the latest data.
Run this daily/weekly to keep your database current.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_data_collector import EnhancedDataCollector

def main():
print(" Full Data Update - Multi-Market Correlation Engine")
print("=" * 55)

try:
collector = EnhancedDataCollector()

# Update with last 30 days of data (for regular updates)
results = collector.collect_all_symbols(days_back=30)

print(f" Update completed!")
print(f" Symbols: {results['successful']}/{results['total_symbols']} successful")
print(f" Records: {results['total_records']} new records added")

if results['failed_symbols']:
print(f" Failed: {results['failed_symbols']}")

return 0

except Exception as e:
print(f" Update failed: {e}")
return 1

if __name__ == "__main__":
exit(main())

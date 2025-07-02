"""
Database Management System
=========================

Centralized database management for the Multi-Market Correlation Engine.
Handles database connections, schema creation, and data access patterns.

Author: Multi-Market Correlation Engine Team
Version: 0.1.0
"""

import logging
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Union
from contextlib import contextmanager
from dataclasses import dataclass

import pandas as pd
import numpy as np
from sqlalchemy import (
create_engine, Column, Integer, String, Float, DateTime, Date,
Boolean, Text, Index, ForeignKey, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.dialects.sqlite import BLOB
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from src.config.config_manager import get_config

# Configure logging
logger = logging.getLogger(__name__)

# SQLAlchemy base
Base = declarative_base()


class MarketData(Base):
"""
Market data table for storing price/volume information.

Optimized for time series data with proper indexing.
"""
__tablename__ = 'market_data'

id = Column(Integer, primary_key=True, autoincrement=True)
symbol = Column(String(20), nullable=False, index=True)
asset_class = Column(String(20), nullable=False, index=True) # equity, bond, commodity, crypto, currency
date = Column(Date, nullable=False, index=True)
timestamp = Column(DateTime, nullable=True) # For intraday data

# OHLCV data
open_price = Column(Float, nullable=True)
high_price = Column(Float, nullable=True)
low_price = Column(Float, nullable=True)
close_price = Column(Float, nullable=False)
volume = Column(Float, nullable=True)
adjusted_close = Column(Float, nullable=True)

# Metadata
source = Column(String(50), nullable=False) # yahoo_finance, fred, coingecko
data_quality_score = Column(Float, nullable=True) # 0-1 quality score
created_at = Column(DateTime, default=datetime.utcnow)
updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Constraints and indexes
__table_args__ = (
UniqueConstraint('symbol', 'date', 'source', name='uix_symbol_date_source'),
Index('ix_market_data_symbol_date', 'symbol', 'date'),
Index('ix_market_data_asset_class_date', 'asset_class', 'date'),
)

def __repr__(self):
return f"<MarketData(symbol='{self.symbol}', date='{self.date}', close={self.close_price})>"


class CorrelationData(Base):
"""
Correlation data table for storing calculated correlations.
"""
__tablename__ = 'correlation_data'

id = Column(Integer, primary_key=True, autoincrement=True)
symbol1 = Column(String(20), nullable=False, index=True)
symbol2 = Column(String(20), nullable=False, index=True)
correlation_type = Column(String(50), nullable=False) # pearson, spearman, kendall, dcc
correlation_value = Column(Float, nullable=False)

# Time period information
start_date = Column(Date, nullable=False)
end_date = Column(Date, nullable=False)
window_size = Column(Integer, nullable=True) # Rolling window size if applicable
calculation_date = Column(Date, nullable=False, index=True)

# Statistical metadata
p_value = Column(Float, nullable=True)
confidence_interval_lower = Column(Float, nullable=True)
confidence_interval_upper = Column(Float, nullable=True)
sample_size = Column(Integer, nullable=True)

# Model metadata
model_version = Column(String(20), nullable=True)
model_parameters = Column(Text, nullable=True) # JSON string of parameters
created_at = Column(DateTime, default=datetime.utcnow)

# Constraints and indexes
__table_args__ = (
UniqueConstraint(
'symbol1', 'symbol2', 'correlation_type', 'calculation_date', 'window_size',
name='uix_correlation_unique'
),
Index('ix_correlation_symbols', 'symbol1', 'symbol2'),
Index('ix_correlation_date', 'calculation_date'),
)

def __repr__(self):
return f"<CorrelationData({self.symbol1}-{self.symbol2}: {self.correlation_value:.3f})>"


class ModelResults(Base):
"""
Model results table for storing ML model outputs and predictions.
"""
__tablename__ = 'model_results'

id = Column(Integer, primary_key=True, autoincrement=True)
model_name = Column(String(100), nullable=False, index=True)
model_type = Column(String(50), nullable=False) # garch, var, lstm, ensemble
model_version = Column(String(20), nullable=False)

# Input data specification
input_symbols = Column(Text, nullable=False) # JSON array of symbols
target_variable = Column(String(100), nullable=False)

# Time information
training_start_date = Column(Date, nullable=False)
training_end_date = Column(Date, nullable=False)
prediction_date = Column(Date, nullable=False, index=True)
forecast_horizon = Column(Integer, nullable=False) # Days ahead

# Results
predicted_value = Column(Float, nullable=False)
confidence_interval_lower = Column(Float, nullable=True)
confidence_interval_upper = Column(Float, nullable=True)
actual_value = Column(Float, nullable=True) # Filled after realization

# Model performance metrics
mse = Column(Float, nullable=True)
mae = Column(Float, nullable=True)
rmse = Column(Float, nullable=True)
r_squared = Column(Float, nullable=True)

# Model metadata
hyperparameters = Column(Text, nullable=True) # JSON string
feature_importance = Column(Text, nullable=True) # JSON string
model_artifact_path = Column(String(500), nullable=True) # Path to saved model

created_at = Column(DateTime, default=datetime.utcnow)

# Indexes
__table_args__ = (
Index('ix_model_results_name_date', 'model_name', 'prediction_date'),
Index('ix_model_results_type_date', 'model_type', 'prediction_date'),
)

def __repr__(self):
return f"<ModelResults({self.model_name}: {self.predicted_value:.3f})>"


class RegimeData(Base):
"""
Market regime data table for storing regime classifications.
"""
__tablename__ = 'regime_data'

id = Column(Integer, primary_key=True, autoincrement=True)
date = Column(Date, nullable=False, index=True)
regime_name = Column(String(50), nullable=False) # bull, bear, crisis, recovery, neutral
regime_probability = Column(Float, nullable=False) # 0-1 probability

# Market characteristics
volatility_level = Column(String(20), nullable=True) # low, medium, high
correlation_level = Column(String(20), nullable=True) # low, medium, high
market_stress_index = Column(Float, nullable=True) # 0-1 stress level

# Detection method
detection_method = Column(String(50), nullable=False) # hmm, volatility_clustering, manual
model_confidence = Column(Float, nullable=True) # Model confidence in classification

# Economic indicators
vix_level = Column(Float, nullable=True)
yield_curve_slope = Column(Float, nullable=True)
credit_spreads = Column(Float, nullable=True)

created_at = Column(DateTime, default=datetime.utcnow)

# Indexes
__table_args__ = (
Index('ix_regime_date_regime', 'date', 'regime_name'),
)

def __repr__(self):
return f"<RegimeData({self.date}: {self.regime_name} - {self.regime_probability:.2f})>"


class DataQuality(Base):
"""
Data quality metrics and monitoring.
"""
__tablename__ = 'data_quality'

id = Column(Integer, primary_key=True, autoincrement=True)
table_name = Column(String(100), nullable=False, index=True)
symbol = Column(String(20), nullable=True, index=True)
check_date = Column(Date, nullable=False, index=True)

# Quality metrics
completeness_score = Column(Float, nullable=False) # % of non-null values
accuracy_score = Column(Float, nullable=True) # Based on validation rules
consistency_score = Column(Float, nullable=True) # Internal consistency
timeliness_score = Column(Float, nullable=True) # Data freshness
overall_quality_score = Column(Float, nullable=False) # Weighted average

# Issue details
missing_data_points = Column(Integer, nullable=False, default=0)
outlier_count = Column(Integer, nullable=False, default=0)
validation_errors = Column(Text, nullable=True) # JSON array of errors

# Recommendations
quality_status = Column(String(20), nullable=False) # excellent, good, fair, poor
recommended_actions = Column(Text, nullable=True) # JSON array of recommendations

created_at = Column(DateTime, default=datetime.utcnow)

def __repr__(self):
return f"<DataQuality({self.table_name}:{self.symbol} - {self.overall_quality_score:.2f})>"


class DatabaseManager:
"""
Central database manager for the application.

Provides connection management, session handling, and data access methods.
"""

def __init__(self):
"""Initialize database manager."""
self.config = get_config()
self.engine = None
self.SessionLocal = None
self._initialize_database()

def _initialize_database(self) -> None:
"""Initialize database connection and create tables."""
try:
# Create engine
database_url = self.config.get_database_url()
self.engine = create_engine(
database_url,
echo=self.config.is_debug_mode(),
pool_pre_ping=True
)

# Create session factory
self.SessionLocal = sessionmaker(
autocommit=False,
autoflush=False,
bind=self.engine
)

# Create all tables
Base.metadata.create_all(bind=self.engine)

logger.info("Database initialized successfully")

except Exception as e:
logger.error(f"Failed to initialize database: {e}")
raise

@contextmanager
def get_session(self):
"""
Get database session with automatic cleanup.

Yields:
Database session
"""
session = self.SessionLocal()
try:
yield session
session.commit()
except Exception as e:
session.rollback()
logger.error(f"Database session error: {e}")
raise
finally:
session.close()

def save_market_data(self, data: pd.DataFrame, source: str) -> int:
"""
Save market data to database.

Args:
data: DataFrame with market data
source: Data source identifier

Returns:
Number of records saved
"""
if data.empty:
logger.warning("Empty DataFrame provided to save_market_data")
return 0

records_saved = 0

try:
with self.get_session() as session:
for _, row in data.iterrows():
market_data = MarketData(
symbol=row.get('symbol'),
asset_class=row.get('asset_class', 'unknown'),
date=row.get('date'),
open_price=row.get('open'),
high_price=row.get('high'),
low_price=row.get('low'),
close_price=row.get('close'),
volume=row.get('volume'),
adjusted_close=row.get('adjusted_close'),
source=source
)

# Handle duplicates with merge (upsert)
existing = session.query(MarketData).filter_by(
symbol=market_data.symbol,
date=market_data.date,
source=source
).first()

if existing:
# Update existing record
for attr in ['open_price', 'high_price', 'low_price',
'close_price', 'volume', 'adjusted_close']:
if hasattr(market_data, attr):
setattr(existing, attr, getattr(market_data, attr))
existing.updated_at = datetime.utcnow()
else:
# Add new record
session.add(market_data)
records_saved += 1

session.commit()
logger.info(f"Saved {records_saved} market data records from {source}")

except Exception as e:
logger.error(f"Failed to save market data: {e}")
raise

return records_saved

def get_market_data(
self,
symbols: List[str],
start_date: Optional[date] = None,
end_date: Optional[date] = None,
source: Optional[str] = None
) -> pd.DataFrame:
"""
Retrieve market data from database.

Args:
symbols: List of symbols to retrieve
start_date: Start date for data
end_date: End date for data
source: Data source filter

Returns:
DataFrame with market data
"""
try:
with self.get_session() as session:
query = session.query(MarketData).filter(
MarketData.symbol.in_(symbols)
)

if start_date:
query = query.filter(MarketData.date >= start_date)
if end_date:
query = query.filter(MarketData.date <= end_date)
if source:
query = query.filter(MarketData.source == source)

query = query.order_by(MarketData.symbol, MarketData.date)

# Convert to DataFrame
data = []
for record in query.all():
data.append({
'symbol': record.symbol,
'date': record.date,
'open': record.open_price,
'high': record.high_price,
'low': record.low_price,
'close': record.close_price,
'volume': record.volume,
'adjusted_close': record.adjusted_close,
'asset_class': record.asset_class,
'source': record.source
})

df = pd.DataFrame(data)
if not df.empty:
df['date'] = pd.to_datetime(df['date'])

logger.info(f"Retrieved {len(df)} market data records")
return df

except Exception as e:
logger.error(f"Failed to retrieve market data: {e}")
raise

def save_correlation_data(self, correlations: List[Dict[str, Any]]) -> int:
"""
Save correlation data to database.

Args:
correlations: List of correlation dictionaries

Returns:
Number of records saved
"""
if not correlations:
return 0

records_saved = 0

try:
with self.get_session() as session:
for corr_data in correlations:
correlation = CorrelationData(**corr_data)

# Check for existing record
existing = session.query(CorrelationData).filter_by(
symbol1=correlation.symbol1,
symbol2=correlation.symbol2,
correlation_type=correlation.correlation_type,
calculation_date=correlation.calculation_date,
window_size=correlation.window_size
).first()

if not existing:
session.add(correlation)
records_saved += 1

session.commit()
logger.info(f"Saved {records_saved} correlation records")

except Exception as e:
logger.error(f"Failed to save correlation data: {e}")
raise

return records_saved

def get_data_quality_summary(self) -> Dict[str, Any]:
"""
Get data quality summary across all tables.

Returns:
Dictionary with quality metrics
"""
try:
with self.get_session() as session:
# Market data quality
market_data_count = session.query(MarketData).count()

# Correlation data quality
correlation_count = session.query(CorrelationData).count()

# Latest quality checks
latest_quality = session.query(DataQuality).order_by(
DataQuality.check_date.desc()
).limit(10).all()

summary = {
'market_data_records': market_data_count,
'correlation_records': correlation_count,
'latest_quality_checks': [
{
'table': q.table_name,
'symbol': q.symbol,
'date': q.check_date,
'quality_score': q.overall_quality_score,
'status': q.quality_status
}
for q in latest_quality
]
}

return summary

except Exception as e:
logger.error(f"Failed to get data quality summary: {e}")
raise


# Global database manager instance
_db_manager = None


def get_db_manager() -> DatabaseManager:
"""
Get the global database manager instance.

Returns:
DatabaseManager instance
"""
global _db_manager
if _db_manager is None:
_db_manager = DatabaseManager()
return _db_manager


# Example usage and testing
if __name__ == "__main__":
# Test database functionality
try:
db = get_db_manager()
print(" Database initialized successfully!")

# Test data quality summary
summary = db.get_data_quality_summary()
print(f"Market data records: {summary['market_data_records']}")
print(f"Correlation records: {summary['correlation_records']}")

except Exception as e:
print(f" Database error: {e}")
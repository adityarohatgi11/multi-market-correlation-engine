"""
Multi-Market Correlation Engine
==============================

An advanced AI-powered system for analyzing, visualizing, and forecasting
correlation structures across global financial markets.

Features:
- Multi-asset data collection (equities, bonds, commodities, crypto)
- Advanced correlation analysis with DCC-GARCH models
- Machine learning forecasting and regime detection
- Real-time dashboard and alerts
- Autonomous AI agents for market monitoring

Author: Multi-Market Correlation Engine Team
Version: 0.1.0
License: MIT
"""

__version__ = "0.1.0"
__author__ = "Multi-Market Correlation Engine Team"

# Import main components
from .config import get_config
from .data import get_db_manager
from .collectors import YahooFinanceCollector

__all__ = [
    "get_config",
    "get_db_manager", 
    "YahooFinanceCollector",
] 
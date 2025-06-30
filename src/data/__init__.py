"""
Data management package for Multi-Market Correlation Engine.
"""

from .database_manager import get_db_manager, DatabaseManager

__all__ = [
    'get_db_manager',
    'DatabaseManager'
] 
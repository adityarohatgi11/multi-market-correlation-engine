"""
Configuration manager for the Multi-Market Correlation Engine.

Handles loading configuration from various sources including YAML files,
environment variables, and default values.
"""

import os
import yaml
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class DataSourceConfig:
    """Configuration for data sources."""
    yahoo_finance: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "symbols": ["AAPL", "GOOGL", "MSFT", "TSLA"],
        "period": "1y"
    })
    crypto: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "coins": ["bitcoin", "ethereum", "cardano"],
        "currency": "usd"
    })
    fred: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "series": ["GDP", "UNRATE", "FEDFUNDS"]
    })
    collection: Dict[str, Any] = field(default_factory=lambda: {
        "batch_size": 100,
        "retry_attempts": 3,
        "timeout": 30
    })
    rate_limits: Dict[str, Any] = field(default_factory=lambda: {
        "yahoo_finance": {"requests_per_minute": 100},
        "coingecko": {"requests_per_minute": 50},
        "fred": {"requests_per_minute": 120}
    })
    storage: Dict[str, Any] = field(default_factory=lambda: {
        "raw_data_retention_days": 90,
        "processed_data_retention_days": 365
    })
    error_handling: Dict[str, Any] = field(default_factory=lambda: {
        "max_retries": 3,
        "backoff_factor": 2
    })


@dataclass
class DatabaseConfig:
    """Configuration for database connections."""
    url: str = "sqlite:///data/market_data.db"
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10


@dataclass
class LoggingConfig:
    """Configuration for logging."""
    level: str = "INFO"
    file: str = "logs/correlation_engine.log"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5


@dataclass
class AppConfig:
    """Main application configuration."""
    debug: bool = False
    streamlit_port: int = 8501
    api_timeout: int = 30
    max_retries: int = 3
    data_sources: DataSourceConfig = field(default_factory=DataSourceConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


class ConfigManager:
    """Central configuration manager for the application."""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config = AppConfig()
        try:
            self._load_configuration()
        except Exception as e:
            logger.warning(f"Failed to load configuration: {e}, using defaults")

    def _load_configuration(self) -> None:
        """Load configuration from all sources."""
        self._load_yaml_config()
        self._load_env_config()
        self._validate_config()
        logger.info("Configuration loaded successfully")

    def _load_yaml_config(self) -> None:
        """Load configuration from YAML files."""
        data_sources_file = self.config_dir / "data_sources.yaml"
        if data_sources_file.exists():
            try:
                with open(data_sources_file, 'r') as f:
                    data_sources_config = yaml.safe_load(f)
                self.config.data_sources = DataSourceConfig(**data_sources_config)
                logger.info(f"Loaded data sources config from {data_sources_file}")
            except Exception as e:
                logger.warning(f"Failed to load {data_sources_file}: {e}")

    def _load_env_config(self) -> None:
        """Load configuration from environment variables."""
        self.config.database.url = os.getenv("DATABASE_URL", self.config.database.url)
        self.config.logging.level = os.getenv("LOG_LEVEL", self.config.logging.level)
        self.config.debug = os.getenv("DEBUG_MODE", "False").lower() == "true"
        
        # API Keys
        self.fred_api_key = os.getenv("FRED_API_KEY")
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_KEY")
        self.news_api_key = os.getenv("NEWS_API_KEY")

    def _validate_config(self) -> None:
        """Validate configuration values."""
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        log_file_path = Path(self.config.logging.file)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        data_dirs = ["data/raw", "data/processed", "data/models"]
        for dir_path in data_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)

    def get_api_key(self, service: str) -> Optional[str]:
        """Get API key for a service."""
        key_map = {
            "fred": getattr(self, 'fred_api_key', None),
            "alpha_vantage": getattr(self, 'alpha_vantage_key', None),
            "news": getattr(self, 'news_api_key', None),
        }
        return key_map.get(service)

    def get_database_url(self) -> str:
        """Get database connection URL."""
        return self.config.database.url

    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        return self.config.debug


class ConfigurationError(Exception):
    """Raised when configuration loading or validation fails."""
    pass


# Global configuration instance
_config_manager = None


def get_config() -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def reload_config() -> ConfigManager:
    """Reload configuration from all sources."""
    global _config_manager
    _config_manager = ConfigManager()
    return _config_manager

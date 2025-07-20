import os
from dotenv import load_dotenv
from typing import Dict, List
from pathlib import Path

# Load .env file from project root
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    """Configuration class for TradingView data feed application."""
    
    # TradingView credentials
    TV_USERNAME = os.getenv('TV_USERNAME')
    TV_PASSWORD = os.getenv('TV_PASSWORD')
    
    # Authentication settings
    ALLOW_NOLOGIN = os.getenv('ALLOW_NOLOGIN', 'false').lower() in ('true', '1', 'yes', 'on')
    
    # Data settings - Configurable bar limit (adjust based on your account capabilities)
    MAX_BARS_PER_REQUEST = int(os.getenv('MAX_BARS_PER_REQUEST', '5000'))
    DEFAULT_INTERVAL = '1h'
    
    # Supported symbols and their exchanges
    SYMBOLS = {
        'XAUUSD': 'OANDA',
        'BTCUSD': 'BINANCE',
        'EURUSD': 'OANDA',
        'GBPUSD': 'OANDA',
        'USDJPY': 'OANDA'
    }
    
    # Available timeframes
    TIMEFRAMES = {
        '1m': '1 minute',
        '3m': '3 minutes',
        '5m': '5 minutes',
        '15m': '15 minutes',
        '30m': '30 minutes',
        '45m': '45 minutes',
        '1h': '1 hour',
        '2h': '2 hours',
        '3h': '3 hours',
        '4h': '4 hours',
        '1d': 'daily',
        '1w': 'weekly',
        '1M': 'monthly'
    }
    
    # Data directories
    RAW_DATA_DIR = 'data/raw'
    PROCESSED_DATA_DIR = 'data/processed'
    
    # Rate limiting
    REQUEST_DELAY = 1.0  # seconds between requests
    MAX_RETRIES = 3
    
    @classmethod
    def validate_credentials(cls) -> bool:
        """Validate that TradingView credentials are provided."""
        return bool(cls.TV_USERNAME and cls.TV_PASSWORD)
    
    @classmethod
    def get_symbol_exchange(cls, symbol: str) -> str:
        """Get exchange for a given symbol."""
        return cls.SYMBOLS.get(symbol.upper(), 'BINANCE')
    
    @classmethod
    def get_supported_symbols(cls) -> List[str]:
        """Get list of supported symbols."""
        return list(cls.SYMBOLS.keys())
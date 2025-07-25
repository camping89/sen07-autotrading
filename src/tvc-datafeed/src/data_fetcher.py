import pandas as pd
import numpy as np
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
from .tradingview_client import TradingViewClient, Interval
from .config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingViewDataFetcher:
    """Class for fetching historical data from TradingView using direct WebSocket client."""
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """Initialize the data fetcher with optional credentials."""
        self.username = username or Config.TV_USERNAME
        self.password = password or Config.TV_PASSWORD
        self.client = None
        self._connect()
    
    def _connect(self):
        """Establish connection to TradingView."""
        try:
            if self.username and self.password:
                logger.info("Attempting to connect to TradingView with credentials...")
                self.client = TradingViewClient(username=self.username, password=self.password)
                
                # Check if authentication was successful
                if self.client.token == "unauthorized_user_token":
                    if Config.ALLOW_NOLOGIN:
                        logger.warning("⚠️  TradingView authentication failed - using nologin method (limited data access)")
                        logger.warning("💡 Data access will be limited - consider fixing credentials for full access")
                        logger.info(f"Connected with nologin mode ({Config.MAX_BARS_PER_REQUEST:,} bars per request)")
                    else:
                        logger.error("🚫 AUTHENTICATION FAILED: Invalid credentials")
                        logger.error("❌ Your credentials are invalid or authentication failed")
                        logger.error("⚠️  Data access will be severely limited - STOPPING APPLICATION")
                        logger.error("💡 Set ALLOW_NOLOGIN=true in .env to continue with limited access")
                        raise ValueError("Authentication failed - check your credentials in .env file.")
                else:
                    logger.info(f"Successfully connected to TradingView with credentials ({Config.MAX_BARS_PER_REQUEST:,} bars per request)")
            else:
                if Config.ALLOW_NOLOGIN:
                    logger.warning("⚠️  No TradingView credentials provided - using nologin mode")
                    logger.warning("💡 Data access will be limited - add credentials for full access")
                    self.client = TradingViewClient()
                    logger.info("Connected without credentials (limited access)")
                else:
                    logger.error("No TradingView credentials provided")
                    logger.error("💡 Set ALLOW_NOLOGIN=true in .env to continue without credentials")
                    raise ValueError("TradingView credentials are required for full data access")
        except Exception as e:
            logger.error(f"Failed to connect to TradingView: {e}")
            raise
    
    
    def _get_interval_object(self, timeframe: str) -> Interval:
        """Convert timeframe string to Interval object."""
        interval_mapping = {
            '1m': Interval.in_1_minute,
            '3m': Interval.in_3_minute,
            '5m': Interval.in_5_minute,
            '15m': Interval.in_15_minute,
            '30m': Interval.in_30_minute,
            '45m': Interval.in_45_minute,
            '1h': Interval.in_1_hour,
            '2h': Interval.in_2_hour,
            '3h': Interval.in_3_hour,
            '4h': Interval.in_4_hour,
            '1d': Interval.in_daily,
            '1w': Interval.in_weekly,
            '1M': Interval.in_monthly
        }
        
        if timeframe not in interval_mapping:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
        
        return interval_mapping[timeframe]
    
    def search_symbol(self, symbol: str, exchange: Optional[str] = None) -> List[Dict]:
        """Search for symbol on TradingView."""
        try:
            exchange_param = exchange if exchange else ''
            results = self.client.search_symbol(symbol, exchange_param)
            return results
        except Exception as e:
            logger.error(f"Error searching for symbol {symbol}: {e}")
            return []
    
    def get_historical_data(
        self, 
        symbol: str, 
        exchange: str, 
        timeframe: str = '1h',
        n_bars: int = 5000
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical data for a symbol.
        
        Args:
            symbol: Trading symbol (e.g., 'XAUUSD', 'BTCUSD')
            exchange: Exchange name (e.g., 'OANDA', 'BINANCE')
            timeframe: Timeframe for data (e.g., '1h', '1d')
            n_bars: Number of bars to fetch (max 5000)
            
        Returns:
            DataFrame with OHLCV data or None if error
        """
        try:
            interval = self._get_interval_object(timeframe)
            n_bars = min(n_bars, Config.MAX_BARS_PER_REQUEST)
            
            logger.info(f"Fetching {n_bars} bars of {symbol} from {exchange} with {timeframe} timeframe")
            
            data = self.client.get_hist(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                n_bars=n_bars
            )
            
            if data is not None and not data.empty:
                logger.info(f"Successfully fetched {len(data)} bars for {symbol}")
                return data
            else:
                logger.warning(f"No data returned for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    def get_extended_historical_data(
        self,
        symbol: str,
        exchange: str,
        timeframe: str = '1h',
        years_back: int = 10
    ) -> Optional[pd.DataFrame]:
        """
        Fetch maximum available historical data.
        
        Note: TradingView WebSocket limitation - can only fetch most recent data,
        not historical data beyond what's immediately available.
        
        Args:
            symbol: Trading symbol
            exchange: Exchange name
            timeframe: Timeframe for data
            years_back: Number of years requested (informational only)
            
        Returns:
            DataFrame with maximum available historical data
        """
        logger.info(f"Fetching maximum available historical data for {symbol}")
        logger.info(f"Note: TradingView can only fetch recent data, not {years_back} years back")
        
        # Fetch maximum bars available for this account
        data = self.get_historical_data(
            symbol=symbol,
            exchange=exchange,
            timeframe=timeframe,
            n_bars=Config.MAX_BARS_PER_REQUEST
        )
        
        if data is not None and not data.empty:
            date_range = data.index.max() - data.index.min()
            logger.info(f"Retrieved {len(data)} bars spanning {date_range.days} days")
            return data
        else:
            logger.error("No data retrieved")
            return None
    
    
    def get_multiple_symbols_data(
        self,
        symbols: List[str],
        timeframe: str = '1h',
        years_back: int = 1
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple symbols.
        
        Args:
            symbols: List of symbols to fetch
            timeframe: Timeframe for data
            years_back: Number of years back
            
        Returns:
            Dictionary mapping symbol to DataFrame
        """
        results = {}
        
        for symbol in symbols:
            exchange = Config.get_symbol_exchange(symbol)
            logger.info(f"Processing {symbol} on {exchange}")
            
            data = self.get_extended_historical_data(
                symbol=symbol,
                exchange=exchange,
                timeframe=timeframe,
                years_back=years_back
            )
            
            if data is not None:
                results[symbol] = data
            
            # Rate limiting between symbols
            time.sleep(Config.REQUEST_DELAY)
        
        return results
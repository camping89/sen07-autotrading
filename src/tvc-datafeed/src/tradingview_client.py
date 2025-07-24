"""
TradingView WebSocket Client - Clean Core Implementation
Extracted and refactored from tvdatafeed for lean, direct TradingView access.
"""

import datetime
import enum
import json
import logging
import random
import re
import string
import pandas as pd
from websocket import create_connection
import requests
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


class Interval(enum.Enum):
    """TradingView timeframe intervals."""
    in_1_minute = "1"
    in_3_minute = "3"
    in_5_minute = "5"
    in_15_minute = "15"
    in_30_minute = "30"
    in_45_minute = "45"
    in_1_hour = "1H"
    in_2_hour = "2H"
    in_3_hour = "3H"
    in_4_hour = "4H"
    in_daily = "1D"
    in_weekly = "1W"
    in_monthly = "1M"


class TradingViewClient:
    """
    Lean TradingView WebSocket client for historical data fetching.
    Direct replacement for tvdatafeed with core functionality only.
    """
    
    # TradingView endpoints
    _SIGNIN_URL = 'https://www.tradingview.com/accounts/signin/'
    _SEARCH_URL = 'https://symbol-search.tradingview.com/symbol_search/?text={}&hl=1&exchange={}&lang=en&type=&domain=production'
    _WS_URL = "wss://data.tradingview.com/socket.io/websocket"
    
    # Request headers
    _WS_HEADERS = json.dumps({"Origin": "https://data.tradingview.com"})
    _SIGNIN_HEADERS = {'Referer': 'https://www.tradingview.com'}
    _WS_TIMEOUT = 5
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize TradingView client.
        
        Args:
            username: TradingView username (optional)
            password: TradingView password (optional)
        """
        self.ws = None
        self.token = self._authenticate(username, password)
        self.session = self._generate_session()
        self.chart_session = self._generate_chart_session()
        
        if self.token is None:
            self.token = "unauthorized_user_token"
            logger.warning("Using nologin method - data access may be limited")
    
    def _authenticate(self, username: Optional[str], password: Optional[str]) -> Optional[str]:
        """Authenticate with TradingView."""
        if not username or not password:
            return None
        
        data = {
            "username": username,
            "password": password,
            "remember": "on"
        }
        
        try:
            response = requests.post(
                url=self._SIGNIN_URL,
                data=data,
                headers=self._SIGNIN_HEADERS
            )
            return response.json()['user']['auth_token']
        except Exception as e:
            logger.error(f'Authentication failed: {e}')
            return None
    
    @staticmethod
    def _generate_session() -> str:
        """Generate random session ID."""
        return "qs_" + "".join(random.choice(string.ascii_lowercase) for _ in range(12))
    
    @staticmethod
    def _generate_chart_session() -> str:
        """Generate random chart session ID."""
        return "cs_" + "".join(random.choice(string.ascii_lowercase) for _ in range(12))
    
    def _create_connection(self):
        """Create WebSocket connection to TradingView."""
        logger.debug("Creating WebSocket connection")
        self.ws = create_connection(
            self._WS_URL,
            header=["Origin: https://data.tradingview.com"],
            timeout=self._WS_TIMEOUT
        )
    
    @staticmethod
    def _prepend_header(message: str) -> str:
        """Prepend Socket.IO header to message."""
        return f"~m~{len(message)}~m~{message}"
    
    @staticmethod
    def _construct_message(func: str, params: List) -> str:
        """Construct Socket.IO message."""
        return json.dumps({"m": func, "p": params}, separators=(",", ":"))
    
    def _create_message(self, func: str, params: List) -> str:
        """Create complete Socket.IO message."""
        return self._prepend_header(self._construct_message(func, params))
    
    def _send_message(self, func: str, params: List):
        """Send message via WebSocket."""
        message = self._create_message(func, params)
        self.ws.send(message)
    
    @staticmethod
    def _format_symbol(symbol: str, exchange: str, contract: Optional[int] = None) -> str:
        """Format symbol for TradingView."""
        if ":" in symbol:
            return symbol
        elif contract is None:
            return f"{exchange}:{symbol}"
        elif isinstance(contract, int):
            return f"{exchange}:{symbol}{contract}!"
        else:
            raise ValueError("Invalid contract specification")
    
    def _parse_data(self, raw_data: str, symbol: str) -> Optional[pd.DataFrame]:
        """Parse raw WebSocket data into DataFrame."""
        try:
            # Extract series data using regex
            match = re.search('"s":\\[(.+?)\\}\\]', raw_data)
            if not match:
                logger.error("No series data found in response")
                return None
            
            data_str = match.group(1)
            entries = data_str.split(',{"')
            data_rows = []
            
            for entry in entries:
                # Split entry data
                parts = re.split("\\[|:|,|\\]", entry)
                if len(parts) < 10:
                    continue
                
                try:
                    # Extract timestamp and OHLCV data
                    timestamp = datetime.datetime.fromtimestamp(float(parts[4]))
                    ohlcv = [float(parts[i]) for i in range(5, 10)]
                    data_rows.append([timestamp] + ohlcv)
                except (ValueError, IndexError) as e:
                    logger.debug(f"Skipping invalid data entry: {e}")
                    continue
            
            if not data_rows:
                logger.error("No valid data rows parsed")
                return None
            
            # Create DataFrame
            df = pd.DataFrame(
                data_rows,
                columns=["datetime", "open", "high", "low", "close", "volume"]
            ).set_index("datetime")
            
            df.insert(0, "symbol", symbol)
            return df
            
        except Exception as e:
            logger.error(f"Data parsing failed: {e}")
            return None
    
    def get_hist(
        self,
        symbol: str,
        exchange: str,
        interval: Interval = Interval.in_daily,
        n_bars: int = 10,
        fut_contract: Optional[int] = None,
        extended_session: bool = False,
    ) -> Optional[pd.DataFrame]:
        """
        Get historical data from TradingView.
        
        Args:
            symbol: Trading symbol
            exchange: Exchange name
            interval: Data interval
            n_bars: Number of bars to fetch
            fut_contract: Futures contract (None for spot)
            extended_session: Include extended trading hours
            
        Returns:
            DataFrame with OHLCV data or None if failed
        """
        try:
            # Format symbol
            formatted_symbol = self._format_symbol(symbol, exchange, fut_contract)
            interval_str = interval.value
            
            # Create WebSocket connection
            self._create_connection()
            
            # Send initialization messages
            self._send_message("set_auth_token", [self.token])
            self._send_message("chart_create_session", [self.chart_session, ""])
            self._send_message("quote_create_session", [self.session])
            
            # Configure quote fields
            quote_fields = [
                self.session, "ch", "chp", "current_session", "description",
                "local_description", "language", "exchange", "fractional",
                "is_tradable", "lp", "lp_time", "minmov", "minmove2",
                "original_name", "pricescale", "pro_name", "short_name",
                "type", "update_mode", "volume", "currency_code", "rchp", "rtc"
            ]
            self._send_message("quote_set_fields", quote_fields)
            
            # Subscribe to symbol
            self._send_message("quote_add_symbols", [
                self.session, formatted_symbol, {"flags": ["force_permission"]}
            ])
            self._send_message("quote_fast_symbols", [self.session, formatted_symbol])
            
            # Resolve symbol and create series
            session_type = "extended" if extended_session else "regular"
            symbol_config = f'={{"symbol":"{formatted_symbol}","adjustment":"splits","session":"{session_type}"}}'
            
            self._send_message("resolve_symbol", [
                self.chart_session, "symbol_1", symbol_config
            ])
            self._send_message("create_series", [
                self.chart_session, "s1", "s1", "symbol_1", interval_str, n_bars
            ])
            self._send_message("switch_timezone", [self.chart_session, "exchange"])
            
            # Receive data
            raw_data = ""
            logger.debug(f"Fetching data for {formatted_symbol}...")
            
            while True:
                try:
                    result = self.ws.recv()
                    raw_data += result + "\n"
                    
                    if "series_completed" in result:
                        break
                        
                except Exception as e:
                    logger.error(f"WebSocket receive error: {e}")
                    break
            
            # Close connection
            if self.ws:
                self.ws.close()
                self.ws = None
            
            # Parse and return data
            return self._parse_data(raw_data, formatted_symbol)
            
        except Exception as e:
            logger.error(f"Failed to fetch historical data: {e}")
            if self.ws:
                self.ws.close()
                self.ws = None
            return None
    
    def search_symbol(self, text: str, exchange: str = '') -> List[Dict]:
        """
        Search for symbols on TradingView.
        
        Args:
            text: Symbol text to search
            exchange: Optional exchange filter
            
        Returns:
            List of matching symbols
        """
        try:
            url = self._SEARCH_URL.format(text, exchange)
            response = requests.get(url)
            
            # Clean HTML tags from response
            clean_text = response.text.replace('</em>', '').replace('<em>', '')
            return json.loads(clean_text)
            
        except Exception as e:
            logger.error(f"Symbol search failed: {e}")
            return []
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
from typing import Optional, Dict, List, Union
import logging
from pathlib import Path
from .config import Config

logger = logging.getLogger(__name__)

class DataProcessor:
    """Class for processing, validating and storing trading data."""
    
    def __init__(self):
        """Initialize the data processor."""
        self.raw_data_dir = Path(Config.RAW_DATA_DIR)
        self.processed_data_dir = Path(Config.PROCESSED_DATA_DIR)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create data directories if they don't exist."""
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_data(self, data: pd.DataFrame, symbol: str) -> bool:
        """
        Validate trading data for completeness and correctness.
        
        Args:
            data: DataFrame with OHLCV data
            symbol: Trading symbol
            
        Returns:
            True if data is valid, False otherwise
        """
        if data is None or data.empty:
            logger.error(f"No data provided for {symbol}")
            return False
        
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            logger.error(f"Missing columns for {symbol}: {missing_columns}")
            return False
        
        # Check for negative values in OHLC
        if (data[['open', 'high', 'low', 'close']] < 0).any().any():
            logger.error(f"Negative price values found for {symbol}")
            return False
        
        # Check high >= max(open, close) and low <= min(open, close)
        invalid_high = data['high'] < data[['open', 'close']].max(axis=1)
        invalid_low = data['low'] > data[['open', 'close']].min(axis=1)
        
        if invalid_high.any():
            logger.warning(f"Invalid high values found for {symbol}: {invalid_high.sum()} rows")
        
        if invalid_low.any():
            logger.warning(f"Invalid low values found for {symbol}: {invalid_low.sum()} rows")
        
        # Check for duplicate timestamps
        if data.index.duplicated().any():
            logger.warning(f"Duplicate timestamps found for {symbol}")
        
        logger.info(f"Data validation completed for {symbol}: {len(data)} rows")
        return True
    
    def clean_data(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Clean and preprocess trading data.
        
        Args:
            data: Raw DataFrame with OHLCV data
            symbol: Trading symbol
            
        Returns:
            Cleaned DataFrame
        """
        logger.info(f"Cleaning data for {symbol}")
        
        # Remove duplicates
        original_length = len(data)
        data = data.drop_duplicates()
        if len(data) < original_length:
            logger.info(f"Removed {original_length - len(data)} duplicate rows for {symbol}")
        
        # Sort by timestamp
        data = data.sort_index()
        
        # Remove rows with all NaN values
        data = data.dropna(how='all')
        
        # Forward fill missing values (optional)
        data = data.ffill()
        
        # Ensure proper data types
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_columns:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')
        
        logger.info(f"Data cleaning completed for {symbol}: {len(data)} rows remaining")
        return data
    
    def add_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Add basic technical indicators to the data.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with additional technical indicators
        """
        df = data.copy()
        
        # Simple Moving Averages
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['sma_200'] = df['close'].rolling(window=200).mean()
        
        # Exponential Moving Averages
        df['ema_12'] = df['close'].ewm(span=12).mean()
        df['ema_26'] = df['close'].ewm(span=26).mean()
        
        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        bb_period = 20
        bb_std = 2
        df['bb_middle'] = df['close'].rolling(window=bb_period).mean()
        bb_std_dev = df['close'].rolling(window=bb_period).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std_dev * bb_std)
        df['bb_lower'] = df['bb_middle'] - (bb_std_dev * bb_std)
        
        # Price change and returns
        df['price_change'] = df['close'].diff()
        df['price_change_pct'] = df['close'].pct_change() * 100
        
        return df
    
    def save_raw_data(
        self, 
        data: pd.DataFrame, 
        symbol: str, 
        timeframe: str,
        format: str = 'csv'
    ) -> str:
        """
        Save raw data to file.
        
        Args:
            data: DataFrame to save
            symbol: Trading symbol
            timeframe: Data timeframe
            format: File format ('csv', 'json', 'parquet')
            
        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{symbol}_{timeframe}_{timestamp}.{format}"
        filepath = self.raw_data_dir / filename
        
        if format == 'csv':
            data.to_csv(filepath)
        elif format == 'json':
            data.to_json(filepath, orient='index', date_format='iso')
        elif format == 'parquet':
            data.to_parquet(filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Saved raw data to {filepath}")
        return str(filepath)
    
    def save_processed_data(
        self, 
        data: pd.DataFrame, 
        symbol: str, 
        timeframe: str,
        format: str = 'csv'
    ) -> str:
        """
        Save processed data to file.
        
        Args:
            data: DataFrame to save
            symbol: Trading symbol
            timeframe: Data timeframe
            format: File format ('csv', 'json', 'parquet')
            
        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{symbol}_{timeframe}_processed_{timestamp}.{format}"
        filepath = self.processed_data_dir / filename
        
        if format == 'csv':
            data.to_csv(filepath)
        elif format == 'json':
            data.to_json(filepath, orient='index', date_format='iso')
        elif format == 'parquet':
            data.to_parquet(filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Saved processed data to {filepath}")
        return str(filepath)
    
    def load_data(self, filepath: str) -> pd.DataFrame:
        """
        Load data from file.
        
        Args:
            filepath: Path to data file
            
        Returns:
            Loaded DataFrame
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        if filepath.suffix == '.csv':
            return pd.read_csv(filepath, index_col=0, parse_dates=True)
        elif filepath.suffix == '.json':
            return pd.read_json(filepath, orient='index')
        elif filepath.suffix == '.parquet':
            return pd.read_parquet(filepath)
        else:
            raise ValueError(f"Unsupported file format: {filepath.suffix}")
    
    def get_data_summary(self, data: pd.DataFrame, symbol: str) -> Dict:
        """
        Generate summary statistics for the data.
        
        Args:
            data: DataFrame with trading data
            symbol: Trading symbol
            
        Returns:
            Dictionary with summary statistics
        """
        if data.empty:
            return {}
        
        summary = {
            'symbol': symbol,
            'total_rows': len(data),
            'date_range': {
                'start': data.index.min().isoformat() if not data.index.empty else None,
                'end': data.index.max().isoformat() if not data.index.empty else None
            },
            'price_statistics': {
                'min_price': float(data['low'].min()),
                'max_price': float(data['high'].max()),
                'first_close': float(data['close'].iloc[0]),
                'last_close': float(data['close'].iloc[-1]),
                'total_return_pct': float(((data['close'].iloc[-1] / data['close'].iloc[0]) - 1) * 100)
            },
            'volume_statistics': {
                'total_volume': float(data['volume'].sum()),
                'avg_volume': float(data['volume'].mean()),
                'max_volume': float(data['volume'].max())
            }
        }
        
        return summary
    
    def export_multiple_formats(
        self, 
        data: pd.DataFrame, 
        symbol: str, 
        timeframe: str,
        formats: List[str] = ['csv', 'json']
    ) -> Dict[str, str]:
        """
        Export data in multiple formats.
        
        Args:
            data: DataFrame to export
            symbol: Trading symbol
            timeframe: Data timeframe
            formats: List of formats to export
            
        Returns:
            Dictionary mapping format to filepath
        """
        exported_files = {}
        
        for fmt in formats:
            try:
                filepath = self.save_processed_data(data, symbol, timeframe, fmt)
                exported_files[fmt] = filepath
            except Exception as e:
                logger.error(f"Failed to export {symbol} data in {fmt} format: {e}")
        
        return exported_files
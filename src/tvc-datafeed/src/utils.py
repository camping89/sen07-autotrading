import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import pandas as pd
from pathlib import Path

def setup_logging(log_level: str = 'INFO', log_file: Optional[str] = None):
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    
    logging_config = {
        'level': numeric_level,
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'datefmt': '%Y-%m-%d %H:%M:%S'
    }
    
    if log_file:
        logging_config['filename'] = log_file
        logging_config['filemode'] = 'a'
    
    logging.basicConfig(**logging_config)

def create_env_file_template(filepath: str = '.env'):
    """
    Create a template .env file with required environment variables.
    
    Args:
        filepath: Path where to create the .env file
    """
    env_template = """# TradingView Credentials
TV_USERNAME=your_tradingview_username
TV_PASSWORD=your_tradingview_password

# Data Collection Settings
# MAX_BARS_PER_REQUEST: Adjust based on your account capabilities
# - Free accounts: typically 5000 (default)
# - Basic accounts: typically 10000  
# - Premium accounts: typically 20000
# - Pro/Pro+ accounts: may support higher limits
MAX_BARS_PER_REQUEST=5000

# Optional Settings
LOG_LEVEL=INFO
MAX_RETRIES=3
REQUEST_DELAY=1.0
"""
    
    if not os.path.exists(filepath):
        with open(filepath, 'w') as f:
            f.write(env_template)
        print(f"Created template .env file at {filepath}")
        print("Please edit it with your TradingView credentials")
    else:
        print(f".env file already exists at {filepath}")

def validate_timeframe(timeframe: str) -> bool:
    """
    Validate if timeframe is supported.
    
    Args:
        timeframe: Timeframe string to validate
        
    Returns:
        True if valid, False otherwise
    """
    valid_timeframes = [
        '1m', '3m', '5m', '15m', '30m', '45m',
        '1h', '2h', '3h', '4h', '1d', '1w', '1M'
    ]
    return timeframe in valid_timeframes

def calculate_bars_for_period(timeframe: str, days: int) -> int:
    """
    Calculate approximate number of bars for a given period.
    
    Args:
        timeframe: Trading timeframe
        days: Number of days
        
    Returns:
        Estimated number of bars
    """
    # Bars per day for different timeframes (considering market hours)
    bars_per_day = {
        '1m': 1440,   # 24 * 60 (crypto markets)
        '3m': 480,    # 24 * 20
        '5m': 288,    # 24 * 12
        '15m': 96,    # 24 * 4
        '30m': 48,    # 24 * 2
        '45m': 32,    # 24 * 1.33
        '1h': 24,     # 24
        '2h': 12,     # 12
        '3h': 8,      # 8
        '4h': 6,      # 6
        '1d': 1,      # 1
        '1w': 1/7,    # 1/7
        '1M': 1/30    # 1/30
    }
    
    return int(bars_per_day.get(timeframe, 24) * days)

def format_number(number: Union[int, float], precision: int = 2) -> str:
    """
    Format number with thousand separators.
    
    Args:
        number: Number to format
        precision: Decimal precision
        
    Returns:
        Formatted number string
    """
    if isinstance(number, float):
        return f"{number:,.{precision}f}"
    else:
        return f"{number:,}"

def get_file_size(filepath: str) -> str:
    """
    Get human-readable file size.
    
    Args:
        filepath: Path to file
        
    Returns:
        Formatted file size string
    """
    if not os.path.exists(filepath):
        return "File not found"
    
    size_bytes = os.path.getsize(filepath)
    
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def save_metadata(
    metadata: Dict, 
    symbol: str, 
    timeframe: str, 
    data_dir: str = "data"
) -> str:
    """
    Save metadata about the data collection process.
    
    Args:
        metadata: Dictionary containing metadata
        symbol: Trading symbol
        timeframe: Data timeframe
        data_dir: Directory to save metadata
        
    Returns:
        Path to saved metadata file
    """
    os.makedirs(data_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{symbol}_{timeframe}_metadata_{timestamp}.json"
    filepath = os.path.join(data_dir, filename)
    
    # Add timestamp to metadata
    metadata['created_at'] = datetime.now().isoformat()
    metadata['symbol'] = symbol
    metadata['timeframe'] = timeframe
    
    with open(filepath, 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    
    return filepath

def load_metadata(filepath: str) -> Dict:
    """
    Load metadata from JSON file.
    
    Args:
        filepath: Path to metadata file
        
    Returns:
        Metadata dictionary
    """
    with open(filepath, 'r') as f:
        return json.load(f)

def list_data_files(data_dir: str, pattern: str = "*") -> List[str]:
    """
    List all data files in a directory matching a pattern.
    
    Args:
        data_dir: Directory to search
        pattern: File pattern to match
        
    Returns:
        List of file paths
    """
    data_path = Path(data_dir)
    if not data_path.exists():
        return []
    
    return [str(f) for f in data_path.glob(pattern) if f.is_file()]

def get_latest_data_file(data_dir: str, symbol: str, timeframe: str) -> Optional[str]:
    """
    Get the most recent data file for a symbol and timeframe.
    
    Args:
        data_dir: Directory to search
        symbol: Trading symbol
        timeframe: Data timeframe
        
    Returns:
        Path to latest file or None
    """
    pattern = f"{symbol}_{timeframe}_*.csv"
    files = list_data_files(data_dir, pattern)
    
    if not files:
        return None
    
    # Sort by modification time, newest first
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return files[0]

def merge_dataframes(dataframes: List[pd.DataFrame]) -> pd.DataFrame:
    """
    Merge multiple dataframes with proper handling of overlaps.
    
    Args:
        dataframes: List of DataFrames to merge
        
    Returns:
        Merged DataFrame
    """
    if not dataframes:
        return pd.DataFrame()
    
    if len(dataframes) == 1:
        return dataframes[0]
    
    # Concatenate all dataframes
    merged = pd.concat(dataframes, ignore_index=False)
    
    # Remove duplicates and sort
    merged = merged.drop_duplicates().sort_index()
    
    return merged

def datetime_to_timestamp(dt: datetime) -> int:
    """
    Convert datetime to Unix timestamp.
    
    Args:
        dt: Datetime object
        
    Returns:
        Unix timestamp
    """
    return int(dt.timestamp())

def timestamp_to_datetime(timestamp: int) -> datetime:
    """
    Convert Unix timestamp to datetime.
    
    Args:
        timestamp: Unix timestamp
        
    Returns:
        Datetime object
    """
    return datetime.fromtimestamp(timestamp)

def progress_bar(current: int, total: int, width: int = 50) -> str:
    """
    Create a simple progress bar string.
    
    Args:
        current: Current progress
        total: Total items
        width: Width of progress bar
        
    Returns:
        Progress bar string
    """
    if total == 0:
        return "[" + "=" * width + "] 100%"
    
    progress = current / total
    filled = int(width * progress)
    bar = "=" * filled + "-" * (width - filled)
    percentage = int(progress * 100)
    
    return f"[{bar}] {percentage}%"

def retry_on_failure(func, max_retries: int = 3, delay: float = 1.0):
    """
    Retry decorator for functions that might fail.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        delay: Delay between retries in seconds
        
    Returns:
        Function result or raises last exception
    """
    import time
    
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries:
                raise e
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2  # Exponential backoff
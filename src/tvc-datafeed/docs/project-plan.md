# TradingView Data Feed Application - Project Documentation

## Overview

This project provides a comprehensive Python application for fetching historical trading data from TradingView using direct WebSocket connections. The application is designed to work with TradingView premium accounts to access extended historical data for various trading instruments including XAUUSD (Gold), BTCUSD (Bitcoin), and other major forex and cryptocurrency pairs.

## Project Structure

```
src/tvc-datafeed/
├── docs/
│   └── project-plan.md         # This documentation file
├── src/
│   ├── main.py                 # Main application entry point
│   ├── data_fetcher.py         # Core data fetching logic using WebSocket client
│   ├── tradingview_client.py   # Direct TradingView WebSocket client
│   ├── config.py               # Configuration and credentials management
│   ├── data_processor.py       # Data processing and formatting utilities
│   └── utils.py                # Helper functions and utilities
├── data/
│   ├── raw/                    # Raw downloaded data storage
│   └── processed/              # Cleaned and processed data storage
├── requirements.txt            # Python dependencies
└── README.md                   # Usage instructions and quick start guide
```

## Key Features

### 1. Multi-Symbol Data Fetching
- Support for major trading symbols: XAUUSD, BTCUSD, EURUSD, GBPUSD, USDJPY
- Automatic exchange detection for each symbol
- Batch processing for multiple symbols

### 2. Flexible Timeframes
- Support for multiple timeframes: 1m, 3m, 5m, 15m, 30m, 45m, 1h, 2h, 3h, 4h, 1d, 1w, 1M
- Configurable data collection periods (1-10+ years)

### 3. Extended Historical Data Collection
- Intelligent pagination to overcome 5000-bar limitation per request
- Automatic calculation of required requests for extended periods
- Progress tracking and error handling

### 4. Data Processing & Validation
- Comprehensive data validation (OHLCV integrity checks)
- Data cleaning and deduplication
- Technical indicator calculation (SMA, EMA, MACD, RSI, Bollinger Bands)
- Data quality assurance

### 5. Multiple Export Formats
- CSV export for spreadsheet analysis
- JSON export for web applications
- Parquet export for big data processing
- Metadata generation with collection statistics

### 6. Premium Account Integration
- Secure credential management using environment variables
- Full symbol access with premium TradingView accounts
- Rate limiting to respect TradingView's usage policies

## Technical Implementation

### Core Components

#### 1. TradingViewDataFetcher (`data_fetcher.py`)
- **Purpose**: Interface with TradingView's data feed using direct WebSocket client
- **Key Methods**:
  - `get_historical_data()`: Fetch up to 5000 bars for a symbol
  - `get_extended_historical_data()`: Fetch multiple years of data through pagination
  - `get_multiple_symbols_data()`: Batch processing for multiple symbols
- **Features**:
  - Automatic retry logic with exponential backoff
  - Rate limiting between requests
  - Error handling and logging

#### 2. DataProcessor (`data_processor.py`)
- **Purpose**: Clean, validate, and enhance trading data
- **Key Methods**:
  - `validate_data()`: Check data integrity and completeness
  - `clean_data()`: Remove duplicates and handle missing values
  - `add_technical_indicators()`: Calculate common technical indicators
  - `save_processed_data()`: Export data in multiple formats
- **Features**:
  - OHLCV validation (High >= max(Open,Close), Low <= min(Open,Close))
  - Duplicate detection and removal
  - Technical analysis indicators
  - Data summary statistics

#### 3. Configuration Management (`config.py`)
- **Purpose**: Centralized configuration and credential management
- **Key Features**:
  - Environment variable integration for credentials
  - Symbol-to-exchange mapping
  - Timeframe definitions
  - Rate limiting settings
  - Data directory configuration

#### 4. Utility Functions (`utils.py`)
- **Purpose**: Helper functions for common operations
- **Key Functions**:
  - Logging setup and configuration
  - File size and format utilities
  - Progress tracking
  - Metadata management
  - Data validation helpers

#### 5. Main Application (`main.py`)
- **Purpose**: Command-line interface and application orchestration
- **Key Features**:
  - Comprehensive CLI with argument parsing
  - Single and batch processing modes
  - Configuration file support
  - Progress reporting and error handling

### Data Flow

1. **Initialization**: Load credentials and initialize TradingView connection
2. **Symbol Processing**: For each symbol:
   - Determine appropriate exchange
   - Calculate required number of requests for desired time period
   - Fetch data in chunks of 5000 bars maximum
   - Combine and deduplicate data
3. **Data Processing**: 
   - Validate data integrity
   - Clean and preprocess data
   - Add technical indicators
   - Generate summary statistics
4. **Export**: Save data in requested formats with metadata

### Rate Limiting and Error Handling

- **Rate Limiting**: 1-second delay between requests (configurable)
- **Retry Logic**: Up to 3 retries with exponential backoff
- **Error Recovery**: Graceful handling of network issues and API errors
- **Logging**: Comprehensive logging at multiple levels (DEBUG, INFO, WARNING, ERROR)

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
TV_USERNAME=your_tradingview_username
TV_PASSWORD=your_tradingview_password
LOG_LEVEL=INFO
MAX_RETRIES=3
REQUEST_DELAY=1.0
```

### Symbol Configuration

The application includes predefined symbol-to-exchange mappings:

```python
SYMBOLS = {
    'XAUUSD': 'OANDA',      # Gold
    'BTCUSD': 'BINANCE',    # Bitcoin
    'EURUSD': 'OANDA',      # Euro/USD
    'GBPUSD': 'OANDA',      # Pound/USD
    'USDJPY': 'OANDA'       # USD/Yen
}
```

## Usage Examples

### Single Symbol Fetching
```bash
# Fetch 2 years of hourly XAUUSD data
python src/main.py --symbol XAUUSD --timeframe 1h --years 2

# Fetch daily BTCUSD data with multiple export formats
python src/main.py --symbol BTCUSD --timeframe 1d --years 1 --export csv,json,parquet
```

### Batch Processing
```bash
# Fetch multiple symbols
python src/main.py --symbols XAUUSD,BTCUSD,EURUSD --timeframe 1h --years 1

# Use configuration file for complex batch jobs
python src/main.py --config batch_config.json --batch
```

### Utility Commands
```bash
# Create .env template
python src/main.py --create-env

# List supported symbols
python src/main.py --list-symbols
```

## Data Limitations and Considerations

### TradingView API Limitations
- Maximum 5000 bars per request
- Rate limiting required to avoid being blocked
- Premium account required for full symbol access
- Data availability varies by symbol and exchange

### Historical Data Coverage
- **Forex**: Typically 10+ years available
- **Cryptocurrencies**: Varies by coin and exchange
- **Commodities**: Extensive historical coverage
- **Stocks**: Varies by market and symbol

### Data Quality
- Some symbols may have gaps in historical data
- Weekend and holiday gaps are normal for forex markets
- Cryptocurrency data typically has no gaps (24/7 markets)

## Technical Requirements

### Python Dependencies
```txt
websocket-client>=1.0.0
requests>=2.25.0
pandas>=1.5.0
numpy>=1.21.0
python-dotenv>=0.19.0
pytz>=2022.1
```

### System Requirements
- Python 3.8 or higher
- Stable internet connection
- Sufficient disk space for data storage
- TradingView premium account (recommended)

## Performance Considerations

### Data Collection Speed
- Approximately 5000 bars per request
- 1-second delay between requests (rate limiting)
- Typical download speeds:
  - 1 year of hourly data: ~2-3 minutes
  - 10 years of daily data: ~1-2 minutes
  - Multiple symbols: Linear scaling with symbol count

### Storage Requirements
- CSV format: ~100KB per 1000 bars
- JSON format: ~150KB per 1000 bars
- Parquet format: ~50KB per 1000 bars (most efficient)

### Memory Usage
- Minimal memory footprint
- Data processed in chunks
- Suitable for large datasets

## Security Considerations

### Credential Management
- Credentials stored in environment variables only
- No hardcoded credentials in source code
- .env file excluded from version control

### API Usage
- Respectful rate limiting
- Error handling to avoid abuse
- Logging for audit trails

## Future Enhancements

### Potential Improvements
1. **Real-time Data Streaming**: Add live data feed capability
2. **Database Integration**: Direct database storage options
3. **Advanced Technical Indicators**: More sophisticated analysis tools
4. **Data Visualization**: Built-in charting capabilities
5. **API Server**: REST API for data access
6. **Scheduling**: Automated periodic data updates
7. **Cloud Integration**: Cloud storage and processing options

### Scalability Considerations
- Multi-threading for parallel symbol processing
- Database backends for large-scale storage
- Cloud deployment for enterprise use
- API caching for improved performance

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify TradingView credentials
   - Check premium account status
   - Ensure .env file is properly configured

2. **Network Issues**
   - Check internet connectivity
   - Verify firewall settings
   - Consider proxy configuration if needed

3. **Data Quality Issues**
   - Review symbol names and exchanges
   - Check TradingView data availability
   - Validate timeframe selection

4. **Performance Issues**
   - Adjust rate limiting settings
   - Consider smaller data ranges
   - Monitor system resources

### Logging and Debugging

The application provides comprehensive logging:
- Use `--log-level DEBUG` for detailed troubleshooting
- Check log files for error details
- Monitor progress with built-in progress bars

## Conclusion

This TradingView Data Feed Application provides a robust, scalable solution for fetching and processing historical trading data. With support for multiple symbols, timeframes, and export formats, it serves as a comprehensive tool for traders, analysts, and researchers requiring high-quality financial market data.

The modular design allows for easy extension and customization, while the built-in error handling and rate limiting ensure reliable operation with TradingView's services. The application is particularly well-suited for users with TradingView premium accounts who need programmatic access to extensive historical data.

For questions, issues, or feature requests, please refer to the project's issue tracking system or contact the development team.
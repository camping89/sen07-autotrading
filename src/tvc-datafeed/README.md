# TradingView Data Feed Application

A comprehensive Python application for fetching historical trading data from TradingView using premium account credentials. Perfect for traders, analysts, and researchers who need programmatic access to high-quality financial market data.

## 🚀 Features

- **Multi-Symbol Support**: XAUUSD, BTCUSD, EURUSD, GBPUSD, USDJPY and more
- **Flexible Timeframes**: From 1-minute to monthly data
- **Maximum Available Data**: Limited by TradingView WebSocket to recent data only
- **Multiple Export Formats**: CSV, JSON, and Parquet
- **Technical Indicators**: Built-in SMA, EMA, MACD, RSI, Bollinger Bands
- **Batch Processing**: Process multiple symbols efficiently
- **Data Validation**: Comprehensive data quality checks
- **Premium Account Integration**: Full access with TradingView premium accounts

## 📋 Requirements

- Python 3.8 or higher
- TradingView account (premium recommended for full access)
- Stable internet connection

## 🛠️ Installation

1. **Clone or download the project**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up credentials**:
   ```bash
   python src/main.py --create-env
   ```
   Then edit the created `.env` file with your TradingView credentials:
   ```env
   TV_USERNAME=your_tradingview_username
   TV_PASSWORD=your_tradingview_password
   MAX_BARS_PER_REQUEST=5000
   ```

## ⚙️ Bar Limit Configuration

The application uses `MAX_BARS_PER_REQUEST` to optimize data collection based on your TradingView account capabilities:

### Finding Your Account's Bar Limit
```bash
# Test with different limits to find your account's maximum
MAX_BARS_PER_REQUEST=5000   # Start with free account limit
MAX_BARS_PER_REQUEST=10000  # Try basic account limit  
MAX_BARS_PER_REQUEST=20000  # Try premium account limit
MAX_BARS_PER_REQUEST=50000  # Try pro+ account limit
```

### Quick Configuration Examples
```env
# Free Account
MAX_BARS_PER_REQUEST=5000

# Premium Account (upgrade from default)
MAX_BARS_PER_REQUEST=20000

# Pro+ Account (if you upgrade)
MAX_BARS_PER_REQUEST=50000
```

## 🚀 Quick Start

### Fetch Single Symbol Data
```bash
# Get maximum available hourly XAUUSD (Gold) data
python src/main.py --symbol XAUUSD --timeframe 1h --years 2

# Get maximum available daily BTCUSD data in multiple formats
python src/main.py --symbol BTCUSD --timeframe 1d --years 1 --export csv,json,parquet
```

### Fetch Multiple Symbols
```bash
# Get data for multiple symbols
python src/main.py --symbols XAUUSD,BTCUSD,EURUSD --timeframe 1h --years 1
```

### List Available Options
```bash
# See supported symbols
python src/main.py --list-symbols

# See all options
python src/main.py --help
```

## 📊 Supported Symbols & Exchanges

| Symbol | Exchange | Description |
|--------|----------|-------------|
| XAUUSD | OANDA    | Gold Spot   |
| BTCUSD | BINANCE  | Bitcoin     |
| EURUSD | OANDA    | Euro/USD    |
| GBPUSD | OANDA    | Pound/USD   |
| USDJPY | OANDA    | USD/Yen     |

## ⏱️ Supported Timeframes

- **Minutes**: 1m, 3m, 5m, 15m, 30m, 45m
- **Hours**: 1h, 2h, 3h, 4h
- **Days**: 1d
- **Weeks**: 1w
- **Months**: 1M

## 📁 Project Structure

```
src/tvc-datafeed/
├── src/
│   ├── main.py              # Main application
│   ├── data_fetcher.py      # TradingView data fetching
│   ├── data_processor.py    # Data processing & validation
│   ├── config.py            # Configuration management
│   └── utils.py             # Utility functions
├── data/
│   ├── raw/                 # Raw downloaded data
│   └── processed/           # Processed data with indicators
├── docs/
│   └── project-plan.md      # Detailed documentation
└── requirements.txt         # Python dependencies
```

## 💡 Usage Examples

### Basic Usage
```bash
# Fetch 1 year of hourly XAUUSD data
python src/main.py --symbol XAUUSD --timeframe 1h --years 1
```

### Advanced Usage
```bash
# Batch processing with custom timeframe
python src/main.py --symbols XAUUSD,BTCUSD --timeframe 4h --years 2 --export csv,json

# With custom logging level
python src/main.py --symbol BTCUSD --timeframe 1d --years 1 --log-level DEBUG
```

### Configuration File (batch_config.json)
```json
{
  "symbols": ["XAUUSD", "BTCUSD", "EURUSD"],
  "timeframe": "1h",
  "years": 2,
  "export_formats": ["csv", "json"]
}
```

```bash
# Run batch processing from config file
python src/main.py --config batch_config.json --batch
```

## 📈 Output Data

The application exports data with the following columns:

### Basic OHLCV Data
- `datetime` (index)
- `open`, `high`, `low`, `close`, `volume`

### Technical Indicators (automatically added)
- **Moving Averages**: `sma_20`, `sma_50`, `sma_200`, `ema_12`, `ema_26`
- **MACD**: `macd`, `macd_signal`, `macd_histogram`
- **RSI**: `rsi`
- **Bollinger Bands**: `bb_upper`, `bb_middle`, `bb_lower`
- **Price Analysis**: `price_change`, `price_change_pct`

## ⚙️ Configuration Options

### Environment Variables (.env)
```env
TV_USERNAME=your_username
TV_PASSWORD=your_password
MAX_BARS_PER_REQUEST=5000
LOG_LEVEL=INFO
MAX_RETRIES=3
REQUEST_DELAY=1.0
```

### Command Line Arguments
```bash
python src/main.py [OPTIONS]

Options:
  --symbol TEXT          Single symbol to fetch (e.g., XAUUSD)
  --symbols TEXT         Comma-separated symbols
  --timeframe TEXT       Data timeframe (default: 1h)
  --years INTEGER        Years of historical data (default: 1)
  --export TEXT          Export formats: csv,json,parquet (default: csv)
  --config TEXT          JSON configuration file
  --batch                Run in batch mode
  --username TEXT        TradingView username
  --password TEXT        TradingView password
  --log-level TEXT       Logging level (default: INFO)
  --create-env           Create .env template
  --list-symbols         List supported symbols
  --help                 Show help message
```

## 🔄 Data Collection Process

1. **Authentication**: Connects to TradingView with your credentials
2. **Symbol Processing**: Determines appropriate exchange for each symbol
3. **Data Fetching**: Downloads data in 5000-bar chunks (API limitation)
4. **Data Validation**: Checks data integrity and quality
5. **Processing**: Cleans data and adds technical indicators
6. **Export**: Saves data in requested formats with metadata

## ⚠️ Important Limitation

**TradingView WebSocket Constraint**: This application can only fetch the most recent data available from TradingView. Despite requesting years of historical data, you'll only receive recent data (typically several months to 2+ years depending on the symbol and timeframe).

**Why?**: The TradingView WebSocket API returns data from the current time backwards, not from specific historical dates. There's no way to access older historical data programmatically through this method.

**Workaround**: Use longer timeframes (daily, weekly) to get more historical coverage with the same number of bars.

## 📊 Performance & Limitations

### Performance
- **Configurable bar limit**: Set `MAX_BARS_PER_REQUEST` based on your account
- **Typical Performance by Account Type**:
  - Free (5,000 bars): 1 year hourly = 2-3 minutes
  - Premium (20,000 bars): 1 year hourly = 30-60 seconds  
  - Pro+ (higher limits): Even faster collection possible
- **Rate limiting**: 1-second delay between requests (configurable)

### TradingView Account Capabilities
- **Free accounts**: Typically 5,000 bars per request
- **Basic accounts**: Typically 10,000 bars per request
- **Premium accounts**: Typically 20,000 bars per request
- **Pro/Pro+ accounts**: May support even higher limits
- Simply adjust `MAX_BARS_PER_REQUEST` in your `.env` file to match your account
- Rate limiting required (1 second between requests)
- Some symbols may have limited historical data regardless of account type

### Storage Requirements
- **CSV**: ~100KB per 1000 bars
- **JSON**: ~150KB per 1000 bars  
- **Parquet**: ~50KB per 1000 bars (most efficient)

## 🔧 Troubleshooting

### Common Issues

**Authentication Problems**:
```bash
# Verify credentials are set
python src/main.py --symbol XAUUSD --timeframe 1h --years 1 --log-level DEBUG
```

**No Data Returned**:
- Check symbol name spelling
- Verify symbol is available on specified exchange
- Try different timeframe or shorter time period

**Network Issues**:
- Check internet connection
- Consider using VPN if geo-restricted
- Increase retry settings in config

### Debug Mode
```bash
# Run with detailed logging
python src/main.py --symbol XAUUSD --timeframe 1h --years 1 --log-level DEBUG
```

## 📝 Output Files

### Data Files
- **Raw Data**: `data/raw/XAUUSD_1h_20240120_143022.csv`
- **Processed Data**: `data/processed/XAUUSD_1h_processed_20240120_143022.csv`

### Metadata Files
- **Collection Info**: `data/XAUUSD_1h_metadata_20240120_143022.json`

Example metadata:
```json
{
  "symbol": "XAUUSD",
  "exchange": "OANDA",
  "timeframe": "1h",
  "years_requested": 2,
  "total_bars": 8760,
  "fetch_time_seconds": 12.34,
  "data_summary": {
    "date_range": {
      "start": "2022-01-20T14:00:00",
      "end": "2024-01-20T14:00:00"
    },
    "price_statistics": {
      "min_price": 1810.50,
      "max_price": 2085.30,
      "total_return_pct": 15.2
    }
  }
}
```

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.

## ⚠️ Disclaimer

This application is for educational and research purposes. Please ensure you comply with TradingView's Terms of Service when using this tool. The authors are not responsible for any misuse or violations of TradingView's policies.

## 📄 License

This project is provided as-is for educational purposes. Please respect TradingView's Terms of Service and rate limits when using this application.

---

**Happy Trading! 📈**
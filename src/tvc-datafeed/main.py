#!/usr/bin/env python3
"""
TradingView Data Feed Application

A comprehensive application for fetching historical trading data from TradingView
using premium account credentials. Supports multiple symbols, timeframes, and
data export formats.

Usage:
    python main.py --symbol XAUUSD --timeframe 1h --years 2
    python main.py --symbols XAUUSD,BTCUSD --timeframe 1d --years 1 --export csv,json
    python main.py --config symbols.json --batch
"""

import argparse
import json
import sys
import time
from datetime import datetime
from typing import List, Dict, Optional
import logging

# Import our modules from src package
from src.config import Config
from src.data_fetcher import TradingViewDataFetcher
from src.data_processor import DataProcessor
from src.utils import (
    setup_logging, create_env_file_template, validate_timeframe,
    format_number, progress_bar, save_metadata
)

logger = logging.getLogger(__name__)

class TradingViewApp:
    """Main application class for TradingView data fetching."""
    
    def __init__(self):
        """Initialize the application."""
        self.fetcher = None
        self.processor = DataProcessor()
        self.start_time = None
    
    def initialize_fetcher(self, username: Optional[str] = None, password: Optional[str] = None):
        """Initialize the data fetcher with credentials."""
        try:
            self.fetcher = TradingViewDataFetcher(username, password)
            logger.info("TradingView data fetcher initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize fetcher: {e}")
            sys.exit(1)
    
    def fetch_single_symbol(
        self, 
        symbol: str, 
        timeframe: str = '1h', 
        years: int = 1,
        export_formats: List[str] = ['csv']
    ) -> Dict:
        """
        Fetch data for a single symbol.
        
        Args:
            symbol: Trading symbol (e.g., 'XAUUSD')
            timeframe: Data timeframe (e.g., '1h', '1d')
            years: Number of years of historical data
            export_formats: List of export formats
            
        Returns:
            Dictionary with operation results
        """
        logger.info(f"Starting data fetch for {symbol}")
        
        # Get exchange for symbol
        exchange = Config.get_symbol_exchange(symbol)
        logger.info(f"Using exchange {exchange} for {symbol}")
        
        # Fetch data
        start_time = time.time()
        data = self.fetcher.get_extended_historical_data(
            symbol=symbol,
            exchange=exchange,
            timeframe=timeframe,
            years_back=years
        )
        fetch_time = time.time() - start_time
        
        if data is None or data.empty:
            logger.error(f"No data retrieved for {symbol}")
            return {'success': False, 'error': 'No data retrieved'}
        
        # Validate and clean data
        if not self.processor.validate_data(data, symbol):
            logger.error(f"Data validation failed for {symbol}")
            return {'success': False, 'error': 'Data validation failed'}
        
        # Clean data
        cleaned_data = self.processor.clean_data(data, symbol)
        
        # Add technical indicators
        processed_data = self.processor.add_technical_indicators(cleaned_data)
        
        # Generate summary
        summary = self.processor.get_data_summary(processed_data, symbol)
        
        # Export data in requested formats
        exported_files = self.processor.export_multiple_formats(
            processed_data, symbol, timeframe, export_formats
        )
        
        # Save metadata
        metadata = {
            'symbol': symbol,
            'exchange': exchange,
            'timeframe': timeframe,
            'years_requested': years,
            'note': 'TradingView WebSocket limitation: can only fetch most recent data available',
            'fetch_time_seconds': fetch_time,
            'total_bars': len(processed_data),
            'data_summary': summary,
            'exported_files': exported_files
        }
        
        metadata_file = save_metadata(metadata, symbol, timeframe, 'data')
        
        result = {
            'success': True,
            'symbol': symbol,
            'bars_count': len(processed_data),
            'fetch_time': fetch_time,
            'exported_files': exported_files,
            'metadata_file': metadata_file,
            'summary': summary
        }
        
        logger.info(f"Successfully processed {symbol}: {len(processed_data)} bars in {fetch_time:.2f}s")
        return result
    
    def fetch_multiple_symbols(
        self,
        symbols: List[str],
        timeframe: str = '1h',
        years: int = 1,
        export_formats: List[str] = ['csv']
    ) -> Dict:
        """
        Fetch data for multiple symbols.
        
        Args:
            symbols: List of trading symbols
            timeframe: Data timeframe
            years: Number of years of historical data
            export_formats: List of export formats
            
        Returns:
            Dictionary with results for all symbols
        """
        logger.info(f"Starting batch fetch for {len(symbols)} symbols")
        
        results = {}
        total_symbols = len(symbols)
        
        for i, symbol in enumerate(symbols, 1):
            print(f"\n{progress_bar(i-1, total_symbols)} Processing {symbol} ({i}/{total_symbols})")
            
            try:
                result = self.fetch_single_symbol(symbol, timeframe, years, export_formats)
                results[symbol] = result
                
                if result['success']:
                    print(f"✓ {symbol}: {format_number(result['bars_count'])} bars fetched")
                else:
                    print(f"✗ {symbol}: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                results[symbol] = {'success': False, 'error': str(e)}
                print(f"✗ {symbol}: Error - {e}")
            
            # Rate limiting between symbols
            if i < total_symbols:
                time.sleep(Config.REQUEST_DELAY)
        
        print(f"\n{progress_bar(total_symbols, total_symbols)} Batch processing complete")
        
        # Generate batch summary
        successful = sum(1 for r in results.values() if r.get('success', False))
        failed = total_symbols - successful
        
        batch_summary = {
            'total_symbols': total_symbols,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total_symbols) * 100,
            'results': results
        }
        
        logger.info(f"Batch processing complete: {successful}/{total_symbols} successful")
        return batch_summary
    
    def run_from_config(self, config_file: str) -> Dict:
        """
        Run batch processing from configuration file.
        
        Args:
            config_file: Path to JSON configuration file
            
        Returns:
            Batch processing results
        """
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config file {config_file}: {e}")
            sys.exit(1)
        
        symbols = config.get('symbols', [])
        timeframe = config.get('timeframe', '1h')
        years = config.get('years', 1)
        export_formats = config.get('export_formats', ['csv'])
        
        if not symbols:
            logger.error("No symbols specified in config file")
            sys.exit(1)
        
        return self.fetch_multiple_symbols(symbols, timeframe, years, export_formats)

def main():
    """Main entry point of the application."""
    parser = argparse.ArgumentParser(
        description='TradingView Data Feed Application',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch 2 years of hourly XAUUSD data
  python main.py --symbol XAUUSD --timeframe 1h --years 2
  
  # Fetch multiple symbols with daily data
  python main.py --symbols XAUUSD,BTCUSD,EURUSD --timeframe 1d --years 1
  
  # Export in multiple formats
  python main.py --symbol BTCUSD --export csv,json,parquet
  
  # Run from configuration file
  python main.py --config batch_config.json --batch
  
  # Create .env template
  python main.py --create-env
        """
    )
    
    # Main arguments
    parser.add_argument('--symbol', type=str, help='Single trading symbol to fetch (e.g., XAUUSD, BTCUSD)')
    parser.add_argument('--symbols', type=str, help='Comma-separated list of symbols to fetch')
    parser.add_argument('--timeframe', type=str, default='1h', 
                       help='Data timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M). Default: 1h')
    parser.add_argument('--years', type=int, default=1, 
                       help='Number of years of historical data to fetch. Default: 1')
    parser.add_argument('--export', type=str, default='csv',
                       help='Export formats (csv, json, parquet). Comma-separated for multiple. Default: csv')
    
    # Batch processing
    parser.add_argument('--config', type=str, help='JSON configuration file for batch processing')
    parser.add_argument('--batch', action='store_true', help='Run in batch mode using config file')
    
    # Credentials
    parser.add_argument('--username', type=str, help='TradingView username (overrides env var)')
    parser.add_argument('--password', type=str, help='TradingView password (overrides env var)')
    
    # Utility
    parser.add_argument('--create-env', action='store_true', help='Create .env template file')
    parser.add_argument('--list-symbols', action='store_true', help='List supported symbols')
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                       help='Logging level. Default: INFO')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Handle utility commands
    if args.create_env:
        create_env_file_template()
        return
    
    if args.list_symbols:
        print("Supported symbols:")
        for symbol, exchange in Config.SYMBOLS.items():
            print(f"  {symbol} ({exchange})")
        return
    
    # Validate timeframe
    if not validate_timeframe(args.timeframe):
        print(f"Error: Invalid timeframe '{args.timeframe}'")
        print(f"Supported timeframes: {', '.join(Config.TIMEFRAMES.keys())}")
        sys.exit(1)
    
    # Parse export formats
    export_formats = [fmt.strip() for fmt in args.export.split(',')]
    
    # Initialize application
    app = TradingViewApp()
    app.start_time = datetime.now()
    
    # Initialize fetcher with credentials
    app.initialize_fetcher(args.username, args.password)
    
    try:
        if args.batch and args.config:
            # Batch processing from config file
            results = app.run_from_config(args.config)
            
        elif args.symbols:
            # Multiple symbols
            symbols = [s.strip().upper() for s in args.symbols.split(',')]
            results = app.fetch_multiple_symbols(symbols, args.timeframe, args.years, export_formats)
            
        elif args.symbol:
            # Single symbol
            symbol = args.symbol.upper()
            results = app.fetch_single_symbol(symbol, args.timeframe, args.years, export_formats)
            
        else:
            print("Error: Must specify --symbol, --symbols, or --config with --batch")
            parser.print_help()
            sys.exit(1)
        
        # Print comprehensive summary
        total_time = (datetime.now() - app.start_time).total_seconds()
        print(f"\n{'='*80}")
        print(f"TRADINGVIEW DATA COLLECTION SUMMARY")
        print(f"{'='*80}")
        
        if isinstance(results, dict) and 'total_symbols' in results:
            # Batch results
            print(f"BATCH OPERATION:")
            print(f"   Symbols processed: {results['total_symbols']}")
            print(f"   Success rate: {results['success_rate']:.1f}%")
            print(f"   Total time: {total_time:.2f} seconds")
        elif isinstance(results, dict) and results.get('success'):
            # Single symbol results with detailed info
            summary = results.get('summary', {})
            date_range = summary.get('date_range', {})
            price_stats = summary.get('price_statistics', {})
            
            print(f"SINGLE SYMBOL OPERATION:")
            print(f"   Symbol: {results['symbol']} ({args.timeframe} timeframe)")
            print(f"   Requested: {args.years} years of historical data")
            print(f"   Retrieved: {format_number(results['bars_count'])} bars")
            print(f"   Date range: {date_range.get('start', 'N/A')[:10]} to {date_range.get('end', 'N/A')[:10]}")
            if price_stats:
                print(f"   Price range: ${price_stats.get('min_price', 0):.2f} - ${price_stats.get('max_price', 0):.2f}")
                print(f"   Total return: {price_stats.get('total_return_pct', 0):.2f}%")
            print(f"   Export formats: {', '.join(results['exported_files'].keys())}")
            print(f"   Processing time: {total_time:.2f} seconds")
            
            # Calculate actual time coverage
            if results['bars_count'] > 0:
                if args.timeframe == '1h':
                    days_coverage = results['bars_count'] / 24
                    print(f"   Time coverage: ~{days_coverage:.0f} days ({days_coverage/365:.1f} years)")
                elif args.timeframe == '1d':
                    years_coverage = results['bars_count'] / 365
                    print(f"   Time coverage: ~{results['bars_count']} days ({years_coverage:.1f} years)")
        
        print(f"{'='*80}")
        print(f"Note: Due to TradingView WebSocket limitations, only recent data is available")
        print(f"{'='*80}")
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 
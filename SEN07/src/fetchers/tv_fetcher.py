import pandas as pd

class TVFetcher:
    def __init__(self, tv_connector):
        self.tv_connector = tv_connector

    def fetch(self, symbol, timeframe, bars=1000):
        # Giả lập fetch từ TradingView, thực tế sẽ dùng API hoặc websocket
        data = self.tv_connector.get_ohlcv(symbol, timeframe, bars)
        if data is None or len(data) == 0:
            print(f"[ERROR] Không lấy được dữ liệu từ TV cho {symbol} {timeframe}")
            return None
        df = pd.DataFrame(data)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df 
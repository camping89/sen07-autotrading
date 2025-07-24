import MetaTrader5 as mt5
import datetime
from src.connectors.mt5_connector import MT5Connector

class MT5Fetcher:
    def __init__(self, mt5_connector):
        self.mt5_connector = mt5_connector

    def timeframe_str_to_mt5(self, tf: str):
        mapping = {
            "m1": mt5.TIMEFRAME_M1,
            "m3": None,  # Nếu MT5 không hỗ trợ thì để None hoặc custom
            "m5": mt5.TIMEFRAME_M5,
            "m15": mt5.TIMEFRAME_M15,
            "h1": mt5.TIMEFRAME_H1,
            "h4": mt5.TIMEFRAME_H4,
            "h8": None,  # Nếu MT5 không hỗ trợ thì để None hoặc custom
            "D": mt5.TIMEFRAME_D1,
            "W": mt5.TIMEFRAME_W1,
            "M": mt5.TIMEFRAME_MN1,
            "d": mt5.TIMEFRAME_D1,
            "w": mt5.TIMEFRAME_W1,
            "m": mt5.TIMEFRAME_MN1,
        }
        tf_enum = mapping.get(tf)
        if tf_enum is None:
            raise ValueError(f"[ERROR] Timeframe '{tf}' không được hỗ trợ bởi MT5 hoặc mapping không hợp lệ.")
        return tf_enum

    def fetch(self, symbol, timeframe, bars=1000):
        tf_enum = self.timeframe_str_to_mt5(timeframe)
        try:
            rates = mt5.copy_rates_from_pos(symbol, tf_enum, 0, bars)
            if rates is None or len(rates) == 0:
                print(f"[ERROR] Không lấy được dữ liệu từ MT5 cho {symbol} {timeframe}")
                return None
            import pandas as pd
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            return df
        except Exception as e:
            print(f"[ERROR] Lỗi khi fetch dữ liệu từ MT5: {e}")
            return None

def get_mt5_server_offset(symbol="EURUSD"):
    mt5.initialize()
    tick_time = mt5.symbol_info_tick(symbol).time  # timestamp (giây)
    server_time = datetime.datetime.fromtimestamp(tick_time)
    utc_time = datetime.datetime.utcfromtimestamp(tick_time)
    offset = (server_time - utc_time).total_seconds() / 3600
    return offset 
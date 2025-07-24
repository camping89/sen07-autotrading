import MetaTrader5 as mt5
from datetime import datetime

def get_mt5_server_offset(symbol="EURUSD"):
    mt5.initialize()
    tick_time = mt5.symbol_info_tick(symbol).time  # timestamp (giây)
    server_time = datetime.fromtimestamp(tick_time)
    utc_time = datetime.utcfromtimestamp(tick_time)
    offset = (server_time - utc_time).total_seconds() / 3600
    return offset

def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
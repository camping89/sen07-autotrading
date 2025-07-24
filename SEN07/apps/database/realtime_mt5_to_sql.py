import pandas as pd
import sqlalchemy
import time
from datetime import datetime

from src.config.config_manager import ConfigManager
from src.connectors.mt5_connector import MT5Connector
from src.connectors.sql_connector import SQLConnector
from src.fetchers.mt5_fetcher import MT5Fetcher

config = ConfigManager("config/config.json")
mt5_cfg = config.get_mt5_config()
sql_cfg = config.get_sql_config()

# Đọc thêm cấu hình fetch schedule
fetch_schedule = config.config.get("timeframe_fetch_schedule", {})

def get_last_bar_time(engine, table_name, symbol_id, provider_id):
    with engine.connect() as conn:
        row = conn.execute(
            sqlalchemy.text(f"SELECT TOP 1 TimeStamp FROM [data_{table_name}] WHERE SymbolId = :symbol_id AND DataProviderId = :provider_id ORDER BY TimeStamp DESC"),
            {"symbol_id": symbol_id, "provider_id": provider_id}
        ).fetchone()
        return pd.to_datetime(row[0]) if row else None

def get_timeframe_id(engine, timeframe):
    with engine.connect() as conn:
        return conn.execute(
            sqlalchemy.text("SELECT Id FROM table_timeframes WHERE Name = :name"), {"name": timeframe}
        ).scalar()

def fetch_and_save(symbol, timeframe, provider):
    log_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with engine.connect() as conn:
        symbol_id = conn.execute(
            sqlalchemy.text("SELECT Id FROM table_symbols WHERE Symbol = :symbol OR RefName = :symbol"), {"symbol": symbol}
        ).scalar()
        provider_id = conn.execute(
            sqlalchemy.text("SELECT Id FROM table_dataproviders WHERE Name = :provider"), {"provider": provider}
        ).scalar()
        timeframe_id = conn.execute(
            sqlalchemy.text("SELECT Id FROM table_timeframes WHERE Name = :name"), {"name": timeframe}
        ).scalar()
    df = fetcher.fetch(symbol, timeframe, bars=2)
    if df is not None and not df.empty:
        # Loại bỏ nến cuối cùng (nến đang hình thành)
        if len(df) > 1:
            df = df.iloc[:-1]
        # Lọc chỉ giữ nến mới chưa có trong SQL
        last_bar_time = get_last_bar_time(engine, timeframe, symbol_id, provider_id)
        if last_bar_time is not None:
            df = df[df['time'] > last_bar_time]
        if df.empty:
            print(f"[{log_time}] [INFO] Không có nến mới cho {symbol} {timeframe} {provider}")
            return
        df = df.rename(columns={
            'time': 'TimeStamp',
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'tick_volume': 'Volume' if 'tick_volume' in df.columns else 'Volume'
        })
        df['SymbolId'] = symbol_id
        df['DataProviderId'] = provider_id
        df['TimeframeId'] = timeframe_id
        df['TimeStamp'] = pd.to_datetime(df['TimeStamp'])
        df['Exchange'] = provider
        columns = [
            'SymbolId', 'DataProviderId', 'TimeframeId', 'TimeStamp',
            'Open', 'High', 'Low', 'Close', 'Volume', 'Exchange'
        ]
        df = df[columns]
        # Ép kiểu các cột uint64 về int64 để tránh lỗi SQL Server
        for col in df.columns:
            if str(df[col].dtype).startswith('uint'):
                df[col] = df[col].astype('int64')
        df.to_sql(f"data_{timeframe}", engine, if_exists='append', index=False)
        print(f"[{log_time}] [REALTIME] Đã lưu {len(df)} nến mới cho {symbol} {timeframe} {provider}")

def should_fetch(timeframe, now, fetch_config):
    cfg = fetch_config.get(timeframe, {})
    if not cfg:
        return False
    if "second" in cfg and now.second != cfg["second"]:
        return False
    if "minute_mod" in cfg and now.minute % cfg["minute_mod"] != 0:
        return False
    if "minute" in cfg and now.minute != cfg["minute"]:
        return False
    if "hour_mod" in cfg and now.hour % cfg["hour_mod"] != 0:
        return False
    if "hour" in cfg and now.hour != cfg["hour"]:
        return False
    if "day" in cfg and now.day != cfg["day"]:
        return False
    if "weekday" in cfg and now.weekday() != cfg["weekday"]:
        return False
    return True

def main_loop():
    last_fetch_minute = None
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [LOADING...] [REALTIME]...")
    while True:
        now = datetime.now()
        # Chỉ fetch đúng 1 lần mỗi tick (giây thứ 3 của phút mới)
        if now.second == 3 and (last_fetch_minute is None or now.minute != last_fetch_minute):
            with engine.connect() as conn:
                symbols = [row[0] for row in conn.execute(sqlalchemy.text("SELECT Symbol FROM table_symbols WHERE Active = 1")).fetchall()]
                timeframes = [row[0] for row in conn.execute(sqlalchemy.text("SELECT Name FROM table_timeframes WHERE Active = 1")).fetchall()]
                providers = [row[0] for row in conn.execute(sqlalchemy.text("SELECT Name FROM table_dataproviders WHERE Active = 1")).fetchall()]
            for symbol in symbols:
                for timeframe in timeframes:
                    if should_fetch(timeframe, now, fetch_schedule):
                        for provider in providers:
                            try:
                                fetch_and_save(symbol, timeframe, provider)
                            except Exception as e:
                                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [ERROR] Lỗi khi fetch {symbol} {timeframe} {provider}: {e}")
            last_fetch_minute = now.minute
            # Sleep đến tick tiếp theo (giây thứ 3 của phút sau)
            now = datetime.now()
            seconds_to_next_3 = 60 - now.second + 3 if now.second > 3 else 3 - now.second
            time.sleep(seconds_to_next_3)
        else:
            # Sleep ngắn để kiểm tra lại
            time.sleep(0.5)

if __name__ == '__main__':
    mt5_conn = MT5Connector(
        login=mt5_cfg['login'],
        password=mt5_cfg['password'],
        server=mt5_cfg['server'],
        path=mt5_cfg.get('path')
    )
    sql_conn = SQLConnector(sql_cfg)
    engine = sql_conn.get_engine()
    if not mt5_conn.connect():
        raise RuntimeError('Không thể kết nối MT5')
    fetcher = MT5Fetcher(mt5_conn)
    main_loop()
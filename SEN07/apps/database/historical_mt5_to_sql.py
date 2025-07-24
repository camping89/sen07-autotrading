import json
import pandas as pd
import time
import sqlalchemy
from datetime import datetime

from src.connectors.mt5_connector import MT5Connector
from src.connectors.sql_connector import SQLConnector
from src.fetchers.mt5_fetcher import MT5Fetcher
from src.config.config_manager import ConfigManager

def log_sync(engine, symbol_id, timeframe_name, provider_id, records_count, status, error_message=None, sync_duration=0):
    with engine.begin() as conn:
        conn.execute(
            sqlalchemy.text("""
                INSERT INTO table_sync_log
                (SymbolId, TimeframeId, DataProviderId, LastSyncTime, RecordsCount, Status, ErrorMessage, SyncDuration, CreatedAt)
                VALUES
                (:symbol_id, :timeframe_id, :provider_id, GETDATE(), :records_count, :status, :error_message, :sync_duration, GETDATE())
            """),
            {
                "symbol_id": symbol_id,
                "timeframe_id": timeframe_name,
                "provider_id": provider_id,
                "records_count": records_count,
                "status": status,
                "error_message": error_message,
                "sync_duration": sync_duration
            }
        )

# Đọc config
config = ConfigManager("config/config.json")
sql_cfg = config.get_sql_config()
mt5_cfg = config.get_mt5_config()

# Khởi tạo connector
mt5_conn = MT5Connector(
    login=mt5_cfg['login'],
    password=mt5_cfg['password'],
    server=mt5_cfg['server'],
    path=mt5_cfg.get('path')
)
sql_conn = SQLConnector(sql_cfg)
engine = sql_conn.get_engine()

# Kết nối MT5
if not mt5_conn.connect():
    raise RuntimeError('Không thể kết nối MT5')

fetcher = MT5Fetcher(mt5_conn)

# Lấy symbol, timeframe từ SQL
with engine.connect() as conn:
    symbols = [row[0] for row in conn.execute(sqlalchemy.text("SELECT Symbol FROM table_symbols WHERE Active = 1")).fetchall()]
    timeframes = [row[0] for row in conn.execute(sqlalchemy.text("SELECT Name FROM table_timeframes WHERE Active = 1")).fetchall()]

# Lọc chỉ lấy timeframe mà fetcher hỗ trợ
supported_timeframes = []
for tf in timeframes:
    try:
        if fetcher.timeframe_str_to_mt5(tf):
            supported_timeframes.append(tf)
        else:
            print(f"[SKIP] Timeframe {tf} không hỗ trợ trên MT5, bỏ qua!")
    except Exception:
        print(f"[SKIP] Timeframe {tf} không hợp lệ với MT5, bỏ qua!")

provider = 'FTMO'
with engine.connect() as conn:
    provider_id = conn.execute(
        sqlalchemy.text("SELECT Id FROM table_dataproviders WHERE Name = :provider"), {"provider": provider}
    ).scalar()

def get_last_bar_time(engine, table_name, symbol_id, provider_id):
    with engine.connect() as conn:
        row = conn.execute(
            sqlalchemy.text(f"SELECT TOP 1 TimeStamp FROM [data_{table_name}] WHERE SymbolId = :symbol_id AND DataProviderId = :provider_id ORDER BY TimeStamp DESC"),
            {"symbol_id": symbol_id, "provider_id": provider_id}
        ).fetchone()
        return pd.to_datetime(row[0]) if row else None

def get_existing_timestamps(engine, table_name, symbol_id, provider_id):
    with engine.connect() as conn:
        return set(
            row[0] for row in conn.execute(
                sqlalchemy.text(f"SELECT TimeStamp FROM [data_{table_name}] WHERE SymbolId = :symbol_id AND DataProviderId = :provider_id"),
                {"symbol_id": symbol_id, "provider_id": provider_id}
            )
        )

def save_historical(engine, df, table_name, symbol_id, provider_id, provider, timeframe_id):
    if df.empty:
        print(f"[DEBUG] Không có nến nào fetch được từ MT5 cho {table_name}")
        return 0
    # Loại bỏ nến cuối cùng (nến đang hình thành)
    if len(df) > 1:
        df = df.iloc[:-1]
    # Lọc chỉ giữ nến chưa có trong DB (so sánh toàn bộ timestamp)
    existing_times = get_existing_timestamps(engine, table_name, symbol_id, provider_id)
    before = len(df)
    df = df[~df['time'].isin(existing_times)]
    if df.empty:
        print(f"[DEBUG] Không có nến mới cho {table_name}")
        return 0
    rename_dict = {
        'time': 'TimeStamp',
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close'
    }
    if 'volume' in df.columns:
        rename_dict['volume'] = 'Volume'
    elif 'tick_volume' in df.columns:
        rename_dict['tick_volume'] = 'Volume'
    else:
        print(f"[ERROR] Không tìm thấy cột volume hoặc tick_volume trong dữ liệu {table_name}")
        return 0
    df = df.rename(columns=rename_dict)
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
    for col in ['SymbolId', 'DataProviderId', 'TimeframeId', 'Volume']:
        if col in df.columns:
            df[col] = df[col].astype('int64')
    df.to_sql(f"data_{table_name}", engine, if_exists='append', index=False)
    print(f"[INFO] Đã lưu {len(df)} nến mới cho {table_name} (trước lọc: {before})")
    return len(df)

for symbol in symbols:
    for timeframe in supported_timeframes:
        print(f"[INFO] Đang lấy dữ liệu cho {symbol} {timeframe} {provider}")
        try:
            with engine.connect() as conn:
                symbol_id = conn.execute(
                    sqlalchemy.text("SELECT Id FROM table_symbols WHERE Symbol = :symbol OR RefName = :symbol"), {"symbol": symbol}
                ).scalar()
                timeframe_id = conn.execute(
                    sqlalchemy.text("SELECT Id FROM table_timeframes WHERE Name = :name"), {"name": timeframe}
                ).scalar()
            table_name = timeframe
            # Fetch toàn bộ dữ liệu lịch sử (lấy 20000 nến)
            df = fetcher.fetch(symbol, timeframe, bars=20000)
            if df is not None and not df.empty:
                save_historical(engine, df, table_name, symbol_id, provider_id, provider, timeframe_id)
        except Exception as e:
            print(f"[ERROR] Lỗi khi lấy dữ liệu cho {symbol} {timeframe}: {e}")
            log_sync(engine, symbol_id if 'symbol_id' in locals() else 0, timeframe_id if 'timeframe_id' in locals() else 0, provider_id if 'provider_id' in locals() else 0, 0, 'FAILED', str(e), 0)

mt5_conn.disconnect() 
import json
import sqlalchemy
from sqlalchemy import text
import re

from src.config.config_manager import ConfigManager

# Đọc config
config = ConfigManager("config/config.json")
sql_cfg = config.get_sql_config()
symbols = config.get_symbols()
timeframes = config.get_timeframes()

# Tạo database nếu chưa có
server_conn_str = None
if sql_cfg.get('trusted_connection', 'no').lower() == 'yes':
    server_conn_str = (
        f"mssql+pyodbc://{sql_cfg['server']}/master?"
        f"driver={sql_cfg['driver']}&trusted_connection=yes"
    )
else:
    server_conn_str = (
        f"mssql+pyodbc://{sql_cfg['username']}:{sql_cfg['password']}@{sql_cfg['server']}/master?"
        f"driver={sql_cfg['driver']}"
    )

server_engine = sqlalchemy.create_engine(server_conn_str)
with server_engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
    dbname = sql_cfg['database']
    result = conn.execute(sqlalchemy.text("SELECT name FROM sys.databases WHERE name = :dbname"), {"dbname": dbname})
    if not result.fetchone():
        conn.execute(sqlalchemy.text(f"CREATE DATABASE [{dbname}]"))
        print(f"[INFO] Đã tạo database {dbname}")
    else:
        print(f"[INFO] Database {dbname} đã tồn tại.")

# Build connection string
if sql_cfg.get('trusted_connection', 'no').lower() == 'yes':
    conn_str = (
        f"mssql+pyodbc://{sql_cfg['server']}/{sql_cfg['database']}?"
        f"driver={sql_cfg['driver']}&trusted_connection=yes"
    )
else:
    conn_str = (
        f"mssql+pyodbc://{sql_cfg['username']}:{sql_cfg['password']}@{sql_cfg['server']}/{sql_cfg['database']}?"
        f"driver={sql_cfg['driver']}"
    )

engine = sqlalchemy.create_engine(conn_str)

def table_exists(conn, table_name):
    result = conn.execute(
        text("SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = :t"), {"t": table_name}
    )
    return result.fetchone() is not None

# 1. Tạo bảng DataProviders, Timeframes, Symbols ,DataSyncLog nếu chưa có
CREATE_TABLES = [
    '''CREATE TABLE table_symbols (
        Id INT PRIMARY KEY,
        Symbol NVARCHAR(20) NOT NULL,
        RefName NVARCHAR(100),
        Type NVARCHAR(50),
        Active BIT DEFAULT 1
    )''',
    '''CREATE TABLE table_timeframes (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        Name NVARCHAR(20) NOT NULL UNIQUE,
        Minutes INT NOT NULL,
        Description NVARCHAR(100),
        Active BIT DEFAULT 1
    )''',
    '''CREATE TABLE table_dataproviders (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        Name NVARCHAR(50) NOT NULL UNIQUE,
        Description NVARCHAR(200),
        Active BIT DEFAULT 1
    )''',
    '''CREATE TABLE table_sync_log (
        Id BIGINT IDENTITY(1,1) PRIMARY KEY,
        SymbolId INT NOT NULL,
        TimeframeId INT NOT NULL,
        DataProviderId INT NOT NULL,
        LastSyncTime DATETIME2,
        RecordsCount INT DEFAULT 0,
        Status NVARCHAR(20) DEFAULT 'SUCCESS',
        ErrorMessage NVARCHAR(500),
        SyncDuration INT,
        CreatedAt DATETIME2 DEFAULT GETDATE()
    )'''
]

with engine.begin() as conn:
    for stmt in CREATE_TABLES:
        m = None
        match = re.search(r'CREATE TABLE \[?(\w+)\]? ', stmt, re.IGNORECASE)
        if match:
            m = match.group(1)
        if m and not table_exists(conn, m):
            try:
                conn.execute(text(stmt))
                print(f"[INFO] Đã tạo bảng: {m}")
            except Exception as e:
                print(f"[WARN] Không thể tạo bảng {m}: {e}")
        elif m:
            print(f"[INFO] Bảng {m} đã tồn tại.")

# 2. Insert dữ liệu mẫu vào DataProviders, Timeframes, Symbols
with engine.begin() as conn:
    # DataProviders mẫu
    dataproviders = config.get_dataproviders()
    for dp in dataproviders:
        try:
            conn.execute(text("INSERT INTO table_dataproviders (Name, Description, Active) SELECT :Name, :Description, :Active WHERE NOT EXISTS (SELECT 1 FROM table_dataproviders WHERE Name = :Name)"), {
                "Name": dp["name"], "Description": dp["description"], "Active": dp["active"]
            })
        except Exception as e:
            print(f"[WARN] Không thể insert DataProvider {dp['name']}: {e}")
    # Timeframes
    for tf in timeframes:
        try:
            conn.execute(text("INSERT INTO table_timeframes (Name, Minutes, Description, Active) SELECT :Name, :Minutes, :Description, :Active WHERE NOT EXISTS (SELECT 1 FROM table_timeframes WHERE Name = :Name)"), {
                "Name": tf["name"], "Minutes": tf["minutes"], "Description": tf["description"], "Active": tf["active"]
            })
        except Exception as e:
            print(f"[WARN] Không thể insert Timeframe {tf['name']}: {e}")
    # Symbols
    for sym in symbols:
        try:
            conn.execute(text("INSERT INTO table_symbols (Id, Symbol, RefName, Type, Active) SELECT :Id, :Symbol, :RefName, :Type, :Active WHERE NOT EXISTS (SELECT 1 FROM table_symbols WHERE Id = :Id)"), {
                "Id": sym["id"], "Symbol": sym["symbol"], "RefName": sym["ref_name"], "Type": sym["type"], "Active": sym["active"]
            })
        except Exception as e:
            print(f"[WARN] Không thể insert Symbol {sym['symbol']}: {e}")

# 3. Tạo bảng OHLCV cho từng timeframe
OHLCV_TEMPLATE = '''CREATE TABLE {table_name} (
    SymbolId INT NOT NULL,
    DataProviderId INT NOT NULL,
    TimeframeId INT NOT NULL,
    TimeStamp DATETIME2 NOT NULL,
    [Open] FLOAT NOT NULL,
    [High] FLOAT NOT NULL,
    [Low] FLOAT NOT NULL,
    [Close] FLOAT NOT NULL,
    Volume BIGINT,
    Exchange NVARCHAR(50),
    PRIMARY KEY (SymbolId, DataProviderId, TimeframeId, TimeStamp)
)'''

with engine.begin() as conn:
    for tf in timeframes:
        tf_name = tf["name"]
        table_name = f"data_{tf_name}"
        if not table_exists(conn, table_name):
            table_sql = OHLCV_TEMPLATE.replace('{table_name}', table_name)
            try:
                conn.execute(text(table_sql))
                print(f"[INFO] Đã tạo bảng dữ liệu OHLCV: {table_name}")
            except Exception as e:
                print(f"[WARN] Không thể tạo bảng OHLCV {table_name}: {e}")
        else:
            print(f"[INFO] Bảng OHLCV {table_name} đã tồn tại.") 
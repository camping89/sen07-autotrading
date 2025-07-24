from src.config.config_manager import ConfigManager
import sqlalchemy

config = ConfigManager("config/config.json")
sql_cfg = config.get_sql_config()
engine = sqlalchemy.create_engine(
    f"mssql+pyodbc://{sql_cfg['username']}:{sql_cfg['password']}@{sql_cfg['server']}/{sql_cfg['database']}?driver={sql_cfg['driver']}"
)

timeframes = [tf['name'] for tf in config.get_timeframes()]

for tf in timeframes:
    with engine.connect() as conn:
        try:
            conn.execute(sqlalchemy.text(f"DELETE FROM [data_{tf}]"))
            print(f"[INFO] Đã xóa toàn bộ dữ liệu bảng data_{tf}")
        except Exception as e:
            print(f"[WARN] Không thể xóa bảng data_{tf}: {e}") 
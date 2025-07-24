import pandas as pd
from sqlalchemy import create_engine, text

class SQLFetcher:
    def __init__(self, conn_str):
        self.engine = create_engine(conn_str)

    def get_id_by_name(self, table, name):
        with self.engine.connect() as conn:
            result = conn.execute(text(f"SELECT Id FROM {table} WHERE Name = :name"), {"name": name})
            row = result.fetchone()
            return row[0] if row else None

    def fetch_ohlcv(self, timeframe, symbol_id, timeframe_id, provider_id, start=None, end=None, limit=1000):
        with self.engine.connect() as conn:
            params = {
                "Timeframe": timeframe,
                "SymbolId": symbol_id,
                "TimeframeId": timeframe_id,
                "ProviderId": provider_id,
                "StartDate": start,
                "EndDate": end,
                "Limit": limit
            }
            query = text("""
                EXEC sp_GetMarketData_ByTimeframe
                    @Timeframe=:Timeframe,
                    @SymbolId=:SymbolId,
                    @TimeframeId=:TimeframeId,
                    @ProviderId=:ProviderId,
                    @StartDate=:StartDate,
                    @EndDate=:EndDate,
                    @Limit=:Limit
            """)
            df = pd.read_sql(query, conn, params=params)
            return df

    # Có thể bổ sung thêm các hàm fetch khác nếu cần

# Ví dụ sử dụng:
# fetcher = SQLFetcher(conn_str)
# provider_id = fetcher.get_id_by_name('DataProviders', 'FTMO')
# timeframe_id = fetcher.get_id_by_name('Timeframes', 'm5')
# df = fetcher.fetch_ohlcv('m5', symbol_id, timeframe_id, provider_id, start, end, limit) 
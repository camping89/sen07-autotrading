import json
import pandas as pd
import sqlalchemy
from datetime import datetime
from src.strategies.combo import ComboStrategy
from src.connectors.sql_connector import SQLConnector
from src.indicators.sma import SMA
from src.indicators.macd import MACD
import plotly.graph_objs as go

# --- CONFIG ---
SYMBOL = 'EURUSD'
TIMEFRAME = 'm15'
PROVIDER = 'FTMO'
START = '2025-01-01 00:00:00'
END = '2025-07-01 00:00:00'
CSV_PATH = f'backtest_{SYMBOL}_{TIMEFRAME}.csv'
JSON_PATH = f'chart_{SYMBOL}_{TIMEFRAME}.json'

# --- SQL CONFIG ---
with open("config/config.json", 'r') as f:
    config = json.load(f)
sql_cfg = config['sql']
sql_conn = SQLConnector(sql_cfg)
engine = sql_conn.get_engine()

def fetch_ohlcv(symbol, timeframe, provider, start, end):
    with engine.connect() as conn:
        symbol_id = conn.execute(
            sqlalchemy.text("SELECT Id FROM Symbols WHERE Symbol = :symbol OR RefName = :symbol"), {"symbol": symbol}
        ).scalar()
        provider_id = conn.execute(
            sqlalchemy.text("SELECT Id FROM DataProviders WHERE Name = :provider"), {"provider": provider}
        ).scalar()
        if symbol_id is None:
            print(f"[ERROR] Không tìm thấy SymbolId cho {symbol}")
        if provider_id is None:
            print(f"[ERROR] Không tìm thấy ProviderId cho {provider}")
        query = sqlalchemy.text(f"""
            SELECT TimeStamp, [Open], [High], [Low], [Close], Volume
            FROM [{timeframe}]
            WHERE SymbolId = :symbol_id AND DataProviderId = :provider_id
              AND TimeStamp >= :start AND TimeStamp <= :end
            ORDER BY TimeStamp
        """)
        df = pd.read_sql(query, conn, params={
            "symbol_id": symbol_id,
            "provider_id": provider_id,
            "start": start,
            "end": end
        })
    df = df.rename(columns={
        'TimeStamp': 'time',
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    })
    df['time'] = pd.to_datetime(df['time'])
    return df

def run_combo_strategy(df):
    strategy = ComboStrategy()
    df = strategy.generate_signals(df)
    # Tính thêm MA20, MACD hist để xuất ra file/chart
    df['ma20'] = SMA(period=20).calculate(df)
    macd_df = MACD(fast=5, slow=25, signal=5).calculate(df)
    df['macd'] = macd_df['macd']
    df['macd_signal'] = macd_df['signal']
    df['macd_hist'] = macd_df['hist']
    return df

def export_csv(df, path):
    df.to_csv(path, index=False)
    print(f"[RESULT] Đã lưu file CSV: {path}")

def export_json(df, path):
    # Chỉ xuất các trường cần thiết cho showchart
    out = df[['time','open','high','low','close','volume','signal','ma20','macd','macd_signal','macd_hist']].copy()
    out['time'] = out['time'].astype(str)
    out_dict = out.to_dict(orient='records')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(out_dict, f, ensure_ascii=False, indent=2)
    print(f"[RESULT] Đã lưu file JSON: {path}")

def show_plotly_chart(df):
    fig = go.Figure()
    # Candlestick
    fig.add_trace(go.Candlestick(x=df['time'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], name='OHLC'))
    # MA20
    fig.add_trace(go.Scatter(x=df['time'], y=df['ma20'], mode='lines', name='MA20', line=dict(color='blue')))
    # MACD hist (bar)
    fig.add_trace(go.Bar(x=df['time'], y=df['macd_hist'], name='MACD Hist', marker_color='orange', opacity=0.3, yaxis='y2'))
    # Buy/Sell signals (lọc đúng điểm entry đảo chiều)
    signal = df['signal']
    prev_signal = signal.shift(1).fillna(0)
    entry_mask = (signal != 0) & (signal != prev_signal)
    entry_signals = df[entry_mask]
    buys = entry_signals[entry_signals['signal'] == 1]
    sells = entry_signals[entry_signals['signal'] == -1]
    fig.add_trace(go.Scatter(x=buys['time'], y=buys['close'], mode='markers', marker=dict(symbol='triangle-up', color='green', size=10), name='Buy'))
    fig.add_trace(go.Scatter(x=sells['time'], y=sells['close'], mode='markers', marker=dict(symbol='triangle-down', color='red', size=10), name='Sell'))
    # Layout
    fig.update_layout(
        title=f'Combo Strategy Chart: {SYMBOL} {TIMEFRAME}',
        xaxis_title='Time',
        yaxis_title='Price',
        yaxis2=dict(title='MACD Hist', overlaying='y', side='right', showgrid=False),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    fig.show()

if __name__ == '__main__':
    df = fetch_ohlcv(SYMBOL, TIMEFRAME, PROVIDER, START, END)
    print(f"[INFO] Lấy {len(df)} nến từ SQL cho {SYMBOL} {TIMEFRAME}")
    if df.empty:
        print("[ERROR] Không có dữ liệu OHLCV trả về. Kiểm tra lại symbol, provider, timeframe hoặc thời gian truy vấn.")
        sys.exit(1)
    df = run_combo_strategy(df)
    export_csv(df, CSV_PATH)
    export_json(df, JSON_PATH)
    show_plotly_chart(df) 
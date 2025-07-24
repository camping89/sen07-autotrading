import sys

# Đảm bảo chạy từ thư mục gốc project
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.strategies.combo import ComboStrategy
    from src.backtest.engine import BacktestEngine
    from src.backtest.metrics import calc_pnl, calc_winrate, calc_max_drawdown, sharpe_ratio, sortino_ratio, profit_factor, expectancy, avg_win_loss, max_consecutive_wins_losses, annualized_return, calmar_ratio, time_in_market
    from src.backtest.result import save_result_csv, save_result_json, summary_report, plot_equity_signals
    from src.connectors.sql_connector import SQLConnector
except ModuleNotFoundError as e:
    print("[ERROR] Không tìm thấy module src. Hãy chạy lệnh sau từ thư mục gốc project:")
    print("    python apps/backtest/backtest_combo.py")
    sys.exit(1)

import json
import pandas as pd
import sqlalchemy
from datetime import datetime

# --- CONFIG ---
SYMBOL = 'EURUSD'
TIMEFRAME = 'm5'
PROVIDER = 'FTMO'
START = '2024-01-01 00:00:00'
END = '2024-07-01 00:00:00'
CSV_PATH = f'backtest_{SYMBOL}_{TIMEFRAME}.csv'
JSON_PATH = f'chart_{SYMBOL}_{TIMEFRAME}.json'
INITIAL_BALANCE = 100000
FEE_PERC = 0.0002  # 0.02% mỗi lần vào/ra lệnh

# --- SQL CONFIG ---
with open("config/config.json", 'r') as f:
    config = json.load(f)
sql_cfg = config['sql']
sql_conn = SQLConnector(sql_cfg)
engine = sql_conn.get_engine()

# --- LẤY DỮ LIỆU TỪ SQL ---
def fetch_ohlcv(symbol, timeframe, provider, start, end):
    with engine.connect() as conn:
        symbol_id = conn.execute(
            sqlalchemy.text("SELECT Id FROM Symbols WHERE Symbol = :symbol OR RefName = :symbol"), {"symbol": symbol}
        ).scalar()
        provider_id = conn.execute(
            sqlalchemy.text("SELECT Id FROM DataProviders WHERE Name = :provider"), {"provider": provider}
        ).scalar()
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

if __name__ == '__main__':
    df = fetch_ohlcv(SYMBOL, TIMEFRAME, PROVIDER, START, END)
    print(f"[INFO] Lấy {len(df)} nến từ SQL cho {SYMBOL} {TIMEFRAME}")
    # Sử dụng BacktestEngine mới
    engine_bt = BacktestEngine(strategy=ComboStrategy(), df=df, initial_balance=INITIAL_BALANCE, fee_perc=FEE_PERC)
    df_bt = engine_bt.run()
    df_bt.columns = df_bt.columns.str.lower()
    # Tính metrics
    total_return, equity = calc_pnl(df_bt)
    winrate, num_trades = calc_winrate(df_bt)
    max_dd = calc_max_drawdown(equity)
    sharpe = sharpe_ratio(df_bt)
    sortino = sortino_ratio(df_bt)
    pf = profit_factor(df_bt)
    expect = expectancy(df_bt)
    avg_win, avg_loss = avg_win_loss(df_bt)
    max_win, max_loss = max_consecutive_wins_losses(df_bt)
    ann_return = annualized_return(df_bt)
    calmar = calmar_ratio(ann_return, max_dd)
    time_market = time_in_market(df_bt)
    metrics = {
        'total_return': total_return,
        'winrate': winrate,
        'num_trades': num_trades,
        'max_drawdown': max_dd,
        'sharpe_ratio': sharpe,
        'sortino_ratio': sortino,
        'profit_factor': pf,
        'expectancy': expect,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'max_consecutive_win': max_win,
        'max_consecutive_loss': max_loss,
        'annualized_return': ann_return,
        'calmar_ratio': calmar,
        'time_in_market': time_market
    }
    # Lưu kết quả (bao gồm equity, position, trade_price...)
    save_result_csv(df_bt, CSV_PATH)
    save_result_json(metrics, JSON_PATH)
    summary_report(df_bt, metrics)
    plot_equity_signals(df_bt) 
import json
import pandas as pd
import matplotlib.pyplot as plt

def save_result_csv(df, path):
    df.to_csv(path, index=False)
    print(f"[RESULT] Đã lưu kết quả backtest ra file CSV: {path}")

def save_result_json(result_dict, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=2)
    print(f"[RESULT] Đã lưu kết quả backtest ra file JSON: {path}")

def summary_report(df, metrics):
    report = {
        'total_return': metrics.get('total_return'),
        'winrate': metrics.get('winrate'),
        'num_trades': metrics.get('num_trades'),
        'max_drawdown': metrics.get('max_drawdown'),
    }
    print("\n===== BACKTEST SUMMARY =====")
    for k, v in report.items():
        print(f"{k}: {v}")
    return report

def plot_equity_signals(df):
    fig, ax1 = plt.subplots(figsize=(14,6))
    ax1.plot(df['time'], df['close'], label='Close', color='gray')
    ax1.set_ylabel('Price')
    ax2 = ax1.twinx()
    if 'equity' in df.columns:
        ax2.plot(df['time'], df['equity'], label='Equity', color='blue')
        ax2.set_ylabel('Equity')
    # Plot buy/sell signals
    if 'signal' in df.columns:
        buys = df[df['signal'] == 1]
        sells = df[df['signal'] == -1]
        ax1.scatter(buys['time'], buys['close'], marker='^', color='green', label='Buy', zorder=5)
        ax1.scatter(sells['time'], sells['close'], marker='v', color='red', label='Sell', zorder=5)
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
    plt.title('Equity Curve & Buy/Sell Signals')
    plt.show() 
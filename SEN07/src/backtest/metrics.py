import numpy as np
import pandas as pd

def calc_pnl(df, price_col='close', signal_col='signal'):
    df = df.copy()
    df['position'] = df[signal_col].replace(0, method='ffill').shift(1).fillna(0)
    df['ret'] = df[price_col].pct_change() * df['position']
    df['equity'] = (1 + df['ret']).cumprod()
    total_return = df['equity'].iloc[-1] - 1
    return total_return, df['equity']

def calc_winrate(df, signal_col='signal', price_col='close'):
    trades = []
    entry = None
    entry_price = None
    for i, row in df.iterrows():
        if row[signal_col] != 0 and entry is None:
            entry = row[signal_col]
            entry_price = row[price_col]
        elif row[signal_col] != 0 and entry is not None and row[signal_col] != entry:
            exit_price = row[price_col]
            trades.append((entry, entry_price, row[signal_col], exit_price))
            entry = row[signal_col]
            entry_price = row[price_col]
    wins = 0
    total = 0
    for t in trades:
        if t[0] == 1 and t[3] > t[1]:
            wins += 1
        elif t[0] == -1 and t[3] < t[1]:
            wins += 1
        total += 1
    winrate = wins / total if total > 0 else 0
    return winrate, total

def calc_max_drawdown(equity):
    roll_max = equity.cummax()
    drawdown = (equity - roll_max) / roll_max
    max_dd = drawdown.min()
    return max_dd

def sharpe_ratio(df, price_col='close', signal_col='signal', risk_free=0):
    df = df.copy()
    df['position'] = df[signal_col].replace(0, method='ffill').shift(1).fillna(0)
    df['ret'] = df[price_col].pct_change() * df['position']
    excess_ret = df['ret'] - risk_free/252  # Giả sử daily
    if excess_ret.std() == 0:
        return 0
    return np.sqrt(252) * excess_ret.mean() / excess_ret.std()

def sortino_ratio(df, price_col='close', signal_col='signal', risk_free=0):
    df = df.copy()
    df['position'] = df[signal_col].replace(0, method='ffill').shift(1).fillna(0)
    df['ret'] = df[price_col].pct_change() * df['position']
    excess_ret = df['ret'] - risk_free/252
    downside = excess_ret[excess_ret < 0]
    if downside.std() == 0:
        return 0
    return np.sqrt(252) * excess_ret.mean() / downside.std()

def profit_factor(df, signal_col='signal', price_col='close'):
    df = df.copy()
    df['position'] = df[signal_col].replace(0, method='ffill').shift(1).fillna(0)
    df['ret'] = df[price_col].pct_change() * df['position']
    gross_profit = df['ret'][df['ret'] > 0].sum()
    gross_loss = -df['ret'][df['ret'] < 0].sum()
    if gross_loss == 0:
        return np.inf
    return gross_profit / gross_loss

def expectancy(df, signal_col='signal', price_col='close'):
    trades = []
    entry = None
    entry_price = None
    for i, row in df.iterrows():
        if row[signal_col] != 0 and entry is None:
            entry = row[signal_col]
            entry_price = row[price_col]
        elif row[signal_col] != 0 and entry is not None and row[signal_col] != entry:
            exit_price = row[price_col]
            trades.append((entry, entry_price, row[signal_col], exit_price))
            entry = row[signal_col]
            entry_price = row[price_col]
    rets = [(t[3] - t[1])/t[1] if t[0]==1 else (t[1] - t[3])/t[1] for t in trades]
    return np.mean(rets) if rets else 0

def avg_win_loss(df, signal_col='signal', price_col='close'):
    trades = []
    entry = None
    entry_price = None
    for i, row in df.iterrows():
        if row[signal_col] != 0 and entry is None:
            entry = row[signal_col]
            entry_price = row[price_col]
        elif row[signal_col] != 0 and entry is not None and row[signal_col] != entry:
            exit_price = row[price_col]
            trades.append((entry, entry_price, row[signal_col], exit_price))
            entry = row[signal_col]
            entry_price = row[price_col]
    win_rets = [(t[3] - t[1])/t[1] if t[0]==1 and t[3]>t[1] else (t[1] - t[3])/t[1] for t in trades if (t[0]==1 and t[3]>t[1]) or (t[0]==-1 and t[3]<t[1])]
    loss_rets = [(t[3] - t[1])/t[1] if t[0]==1 and t[3]<t[1] else (t[1] - t[3])/t[1] for t in trades if (t[0]==1 and t[3]<t[1]) or (t[0]==-1 and t[3]>t[1])]
    avg_win = np.mean(win_rets) if win_rets else 0
    avg_loss = np.mean(loss_rets) if loss_rets else 0
    return avg_win, avg_loss

def max_consecutive_wins_losses(df, signal_col='signal', price_col='close'):
    trades = []
    entry = None
    entry_price = None
    for i, row in df.iterrows():
        if row[signal_col] != 0 and entry is None:
            entry = row[signal_col]
            entry_price = row[price_col]
        elif row[signal_col] != 0 and entry is not None and row[signal_col] != entry:
            exit_price = row[price_col]
            trades.append((entry, entry_price, row[signal_col], exit_price))
            entry = row[signal_col]
            entry_price = row[price_col]
    streak = 0
    max_win = 0
    max_loss = 0
    last_result = None
    for t in trades:
        win = (t[0] == 1 and t[3] > t[1]) or (t[0] == -1 and t[3] < t[1])
        if win:
            if last_result == 'win':
                streak += 1
            else:
                streak = 1
            max_win = max(max_win, streak)
            last_result = 'win'
        else:
            if last_result == 'loss':
                streak += 1
            else:
                streak = 1
            max_loss = max(max_loss, streak)
            last_result = 'loss'
    return max_win, max_loss

def annualized_return(df, price_col='close', signal_col='signal'):
    df = df.copy()
    df['position'] = df[signal_col].replace(0, method='ffill').shift(1).fillna(0)
    df['ret'] = df[price_col].pct_change() * df['position']
    n_years = (df['ret'].count()) / 252  # Giả sử daily
    total_return = (1 + df['ret']).prod() - 1
    if n_years == 0:
        return 0
    return (1 + total_return) ** (1/n_years) - 1

def calmar_ratio(annual_return, max_drawdown):
    if max_drawdown == 0:
        return np.inf
    return annual_return / abs(max_drawdown)

def time_in_market(df, signal_col='signal'):
    df = df.copy()
    df['position'] = df[signal_col].replace(0, method='ffill').shift(1).fillna(0)
    return (df['position'] != 0).mean() 
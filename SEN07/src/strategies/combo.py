import pandas as pd
from src.indicators.sma import SMA
from src.indicators.macd import MACD

class ComboStrategy:
    def __init__(self):
        pass

    def generate_signals(self, df):
        # Tính MA20
        ma20 = SMA(period=20).calculate(df)
        # Tính MACD hist (5,25,5)
        macd_df = MACD(fast=5, slow=25, signal=5).calculate(df)
        hist = macd_df['hist']
        # Điều kiện mua
        buy = (df['close'] > df['open']) & (df['close'] > ma20) & (hist > 0)
        # Điều kiện bán
        sell = (df['close'] < df['open']) & (df['close'] < ma20) & (hist < 0)
        # Sinh tín hiệu: 1 = buy, -1 = sell, 0 = hold
        signal = pd.Series(0, index=df.index)
        signal[buy] = 1
        signal[sell] = -1
        # Lọc chỉ giữ điểm đảo chiều (không để chuỗi tín hiệu liên tiếp)
        prev_signal = signal.shift(1).fillna(0)
        filtered_signal = signal.copy()
        filtered_signal[(signal == 0) | (signal == prev_signal)] = 0
        df['signal'] = filtered_signal
        return df 
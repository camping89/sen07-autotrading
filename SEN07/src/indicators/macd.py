from .base import Indicator
import pandas as pd

class MACD(Indicator):
    def __init__(self, fast=12, slow=26, signal=9):
        super().__init__(fast=fast, slow=slow, signal=signal)
        self.fast = fast
        self.slow = slow
        self.signal = signal

    def calculate(self, df, price_col='close'):
        fast_ema = df[price_col].ewm(span=self.fast, adjust=False).mean()
        slow_ema = df[price_col].ewm(span=self.slow, adjust=False).mean()
        macd = fast_ema - slow_ema
        signal = macd.ewm(span=self.signal, adjust=False).mean()
        hist = macd - signal
        return pd.DataFrame({'macd': macd, 'signal': signal, 'hist': hist}, index=df.index) 
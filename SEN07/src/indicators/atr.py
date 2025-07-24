from .base import Indicator
import pandas as pd

class ATR(Indicator):
    def __init__(self, period=14):
        super().__init__(period=period)
        self.period = period

    def calculate(self, df):
        high_low = df['High'] - df['Low']
        high_close = (df['High'] - df['Close'].shift()).abs()
        low_close = (df['Low'] - df['Close'].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=self.period).mean()
        return atr 
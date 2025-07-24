from .base import Indicator
import pandas as pd

class RSI(Indicator):
    def __init__(self, period=14):
        super().__init__(period=period)
        self.period = period

    def calculate(self, df, price_col='close'):
        delta = df[price_col].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi 
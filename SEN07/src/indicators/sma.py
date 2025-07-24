from .base import Indicator
import pandas as pd

class SMA(Indicator):
    def __init__(self, period=14):
        super().__init__(period=period)
        self.period = period

    def calculate(self, df, price_col='close'):
        return df[price_col].rolling(window=self.period).mean() 
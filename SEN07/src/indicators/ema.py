from .base import Indicator
import pandas as pd

class EMA(Indicator):
    def __init__(self, period=14):
        super().__init__(period=period)
        self.period = period

    def calculate(self, df, price_col='close'):
        return df[price_col].ewm(span=self.period, adjust=False).mean() 
from .base import Indicator
import pandas as pd

class CCI(Indicator):
    def __init__(self, period=20):
        super().__init__(period=period)
        self.period = period

    def calculate(self, df):
        tp = (df['High'] + df['Low'] + df['Close']) / 3
        ma = tp.rolling(window=self.period).mean()
        md = (tp - ma).abs().rolling(window=self.period).mean()
        cci = (tp - ma) / (0.015 * md)
        return cci 
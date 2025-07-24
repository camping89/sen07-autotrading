from .base import Indicator
import pandas as pd

class Stochastic(Indicator):
    def __init__(self, k_period=14, d_period=3):
        super().__init__(k_period=k_period, d_period=d_period)
        self.k_period = k_period
        self.d_period = d_period

    def calculate(self, df):
        low_min = df['Low'].rolling(window=self.k_period).min()
        high_max = df['High'].rolling(window=self.k_period).max()
        k = 100 * (df['Close'] - low_min) / (high_max - low_min)
        d = k.rolling(window=self.d_period).mean()
        return pd.DataFrame({'%K': k, '%D': d}) 
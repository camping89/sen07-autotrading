from .base import Indicator
import pandas as pd

class BollingerBands(Indicator):
    def __init__(self, period=20, num_std=2):
        super().__init__(period=period, num_std=num_std)
        self.period = period
        self.num_std = num_std

    def calculate(self, df, price_col='Close'):
        ma = df[price_col].rolling(window=self.period).mean()
        std = df[price_col].rolling(window=self.period).std()
        upper = ma + self.num_std * std
        lower = ma - self.num_std * std
        return pd.DataFrame({'upper': upper, 'middle': ma, 'lower': lower}) 
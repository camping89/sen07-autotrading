
from .base import Strategy
from src.indicators.sma import SMA

class MACrossStrategy(Strategy):
    def generate_signals(self, df):
        fast_ma = SMA(period=self.params.get('fast', 10)).calculate(df)
        slow_ma = SMA(period=self.params.get('slow', 20)).calculate(df)
        signal = (fast_ma > slow_ma).astype(int).diff().fillna(0)
        df['signal'] = signal
        return df 
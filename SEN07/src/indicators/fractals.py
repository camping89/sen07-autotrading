from .base import Indicator
import pandas as pd

class Fractals(Indicator):
    def __init__(self):
        super().__init__()

    def calculate(self, df):
        high = df['High']
        low = df['Low']
        up = (high.shift(2) < high.shift(0)) & (high.shift(1) < high.shift(0)) & (high.shift(-1) < high.shift(0)) & (high.shift(-2) < high.shift(0))
        down = (low.shift(2) > low.shift(0)) & (low.shift(1) > low.shift(0)) & (low.shift(-1) > low.shift(0)) & (low.shift(-2) > low.shift(0))
        return pd.DataFrame({'up_fractal': up, 'down_fractal': down}) 
class Indicator:
    def __init__(self, **params):
        self.params = params

    def calculate(self, df, *args, **kwargs):
        raise NotImplementedError 
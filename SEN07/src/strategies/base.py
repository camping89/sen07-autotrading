class Strategy:
    def __init__(self, **params):
        self.params = params

    def generate_signals(self, df):
        raise NotImplementedError 
class BacktestEngine:
    def __init__(self, strategy, df, initial_balance=100000, fee_perc=0):
        self.strategy = strategy
        self.df = df.copy()
        self.initial_balance = initial_balance
        self.fee_perc = fee_perc  # phí giao dịch theo % mỗi lần vào/ra lệnh

    def run(self):
        df = self.strategy.generate_signals(self.df)
        df = df.copy()
        df['position'] = 0
        df['trade_price'] = None
        df['equity'] = self.initial_balance
        position = 0  # 1: long, -1: short, 0: flat
        entry_price = None
        equity = self.initial_balance
        for i, row in df.iterrows():
            signal = row['signal']
            price = row['close']
            # Vào lệnh mới khi có tín hiệu đảo chiều
            if signal == 1 and position <= 0:
                # Nếu đang short, đóng short trước
                if position == -1 and entry_price is not None:
                    pnl = (entry_price - price) / entry_price * equity
                    fee = abs(entry_price - price) * self.fee_perc * equity / entry_price
                    equity += pnl - fee
                position = 1
                entry_price = price
                df.at[i, 'trade_price'] = price
            elif signal == -1 and position >= 0:
                # Nếu đang long, đóng long trước
                if position == 1 and entry_price is not None:
                    pnl = (price - entry_price) / entry_price * equity
                    fee = abs(price - entry_price) * self.fee_perc * equity / entry_price
                    equity += pnl - fee
                position = -1
                entry_price = price
                df.at[i, 'trade_price'] = price
            # Nếu không có tín hiệu đảo chiều, giữ nguyên vị thế
            df.at[i, 'position'] = position
            df.at[i, 'equity'] = equity
        return df 
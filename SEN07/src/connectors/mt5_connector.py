import MetaTrader5 as mt5

class MT5Connector:
    def __init__(self, login, password, server, path=None):
        self.login = int(login)  # Đảm bảo login là int
        self.password = password
        self.server = server
        self.path = path

    def connect(self):
        # Khởi tạo MT5 terminal
        if self.path:
            initialized = mt5.initialize(self.path)
        else:
            initialized = mt5.initialize()
        if not initialized:
            print(f"[ERROR] MT5 initialize failed: {mt5.last_error()}")
            return False
        # Đăng nhập với tên tham số rõ ràng
        authorized = mt5.login(self.login, password=self.password, server=self.server)
        if not authorized:
            print(f"[ERROR] MT5 login failed: {mt5.last_error()}")
            mt5.shutdown()
            return False
        return True

    def disconnect(self):
        mt5.shutdown() 
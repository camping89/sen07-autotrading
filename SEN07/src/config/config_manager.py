import json

class ConfigManager:
    def __init__(self, config_file: str):
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

    def get_sql_config(self):
        return self.config.get("sql", {})

    def get_mt5_config(self):
        return self.config.get("mt5", {})

    def get_symbols(self):
        return self.config.get("symbols", [])

    def get_timeframes(self):
        return self.config.get("timeframes", [])

    def get_tv_config(self):
        return self.config.get("tv", {})

    def get_dataproviders(self):
        return self.config.get("dataproviders", [])

import sqlalchemy

class SQLConnector:
    def __init__(self, sql_cfg):
        self.sql_cfg = sql_cfg
        self.engine = self._create_engine()

    def _create_engine(self):
        if self.sql_cfg.get('trusted_connection', 'no').lower() == 'yes':
            conn_str = (
                f"mssql+pyodbc://{self.sql_cfg['server']}/{self.sql_cfg['database']}?"
                f"driver={self.sql_cfg['driver']}&trusted_connection=yes"
            )
        else:
            conn_str = (
                f"mssql+pyodbc://{self.sql_cfg['username']}:{self.sql_cfg['password']}@{self.sql_cfg['server']}/{self.sql_cfg['database']}?"
                f"driver={self.sql_cfg['driver']}"
            )
        return sqlalchemy.create_engine(conn_str)

    def get_engine(self):
        return self.engine 
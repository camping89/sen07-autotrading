import requests

class TVConnector:
    def __init__(self, api_url, api_key=None):
        self.api_url = api_url
        self.api_key = api_key

    def fetch(self, symbol, timeframe, start, end):
        params = {
            'symbol': symbol,
            'timeframe': timeframe,
            'start': start,
            'end': end
        }
        headers = {'Authorization': f'Bearer {self.api_key}'} if self.api_key else {}
        response = requests.get(self.api_url, params=params, headers=headers)
        response.raise_for_status()
        return response.json() 
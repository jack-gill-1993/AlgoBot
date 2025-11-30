import requests
from dataclasses import dataclass
from typing import List

# Create a simple Candle dataclass (matches your bot structure)
@dataclass
class Candle:
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float

class PolygonClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://api.polygon.io/v2/aggs/ticker"

    def get_candles(self, symbol: str, timespan: str = "minute", limit: int = 50) -> List[Candle]:
        """
        Fetches recent candles for a symbol.
        Example symbols:
          - NQ futures: X:NQ=F
          - ES futures: X:ES=F
          - SPX index: I:SPX
          - BTC: X:BTCUSD
        """

        endpoint = f"{self.url}/{symbol}/range/1/{timespan}/now?limit={limit}&apiKey={self.api_key}"

        response = requests.get(endpoint)
        data = response.json()

        if "results" not in data:
            print("[Polygon] No candle data found:", data)
            return []

        candles = []
        for c in data["results"]:
            candles.append(Candle(
                timestamp = c.get("t"),
                open      = c.get("o", 0),
                high      = c.get("h", 0),
                low       = c.get("l", 0),
                close     = c.get("c", 0),
                volume    = c.get("v", 0)
            ))

        return candles
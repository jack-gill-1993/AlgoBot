"""
Simple Polygon.io client for AlgoBot.

Right now this only fetches basic OHLCV candles.
Later we can extend it to pull tick data and build our own "delta" values.
"""

import requests
from typing import List, Dict, Any


class PolygonClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.polygon.io"

    def get_candles(
        self,
        ticker: str,
        timespan: str = "minute",
        limit: int = 5,
        multiplier: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        Fetch recent aggregate candles using Polygon's v2 aggs endpoint.

        This is intentionally simple: it just returns a list of dicts with
        timestamp, open, high, low, close, volume.
        """
        url = (
            f"{self.base_url}/v2/aggs/ticker/{ticker}/range/"
            f"{multiplier}/{timespan}/"
            "1970-01-01/2100-01-01"
        )

        params = {
            "adjusted": "true",
            "sort": "desc",    # newest first
            "limit": limit,
            "apiKey": self.api_key,
        }

        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results", []) or []

        candles: List[Dict[str, Any]] = []
        for r in results:
            candles.append(
                {
                    "t": r.get("t"),   # timestamp ms
                    "o": r.get("o"),
                    "h": r.get("h"),
                    "l": r.get("l"),
                    "c": r.get("c"),
                    "v": r.get("v"),
                }
            )

        # Return in chronological order (oldest first)
        candles.reverse()
        return candles
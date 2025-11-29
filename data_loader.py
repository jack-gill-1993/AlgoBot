# data_loader.py
# This file will be responsible for getting price candles + footprint data.
# For now, these are placeholders (fake data) so the bot can run without errors.

def get_recent_candles(symbol="NQ", timeframe="15m", limit=5):
    """
    Placeholder function.
    Later: connect to TradingView, Polygon.io, Alpaca, or CME futures feed.
    Returns a list of candle dictionaries.
    """
    return [
        {"open": 100, "high": 105, "low": 99, "close": 104},
        {"open": 104, "high": 106, "low": 102, "close": 103},
        {"open": 103, "high": 108, "low": 103, "close": 107},
    ]


def get_recent_footprint(symbol="NQ", timeframe="15m", limit=5):
    """
    Placeholder footprint.
    Later: real delta + buy/sell imbalance.
    """
    return [
        {"delta": +200000, "buy_imbalance": True, "sell_imbalance": False},
        {"delta": -150000, "buy_imbalance": False, "sell_imbalance": True},
        {"delta": +50000, "buy_imbalance": True, "sell_imbalance": False},
    ]
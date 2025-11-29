"""
AlgoBot - Simple Test Harness

This file does three main things:

1. Defines simple data structures for candles and signals
2. Loads two strategies:
   - breakout_rejection (short)
   - breakout_acceptance (long / trend-following breakout)
3. Uses fake (mock) candle data to TEST the logic and print signals

Later we will:
- Replace `mock_fetch_candles()` with real market data (NQ, ES, etc.)
- Replace the print statements with real order placement
"""

from dataclasses import dataclass
from typing import List, Dict


# -------------------------
# 1. Basic data structures
# -------------------------

@dataclass
class Candle:
    """Represents one bar of data (e.g. 4H or 1D)."""
    time: str           # simple string for now, e.g. "2025-11-26 16:00"
    open: float
    high: float
    low: float
    close: float
    volume: float
    delta: float        # footprint delta (buyers - sellers)


@dataclass
class StrategySignal:
    """Represents a trading signal the bot has found."""
    time: str
    market: str
    strategy: str       # "breakout_rejection" or "breakout_acceptance"
    direction: str      # "long" or "short"
    reason: str


# -------------------------
# 2. Strategy "loader"
# -------------------------

def load_strategies() -> Dict[str, Dict]:
    """
    For now this is a simple hard-coded config.
    Later, we can move this into a separate file (e.g. JSON or YAML).

    Two strategies:

    1) breakout_rejection (short)
       - used when price breaks above a level and then fails
       - we expect negative delta on the rejection candle

    2) breakout_acceptance (long)
       - used when price breaks above a level and holds above it
       - we expect positive delta and a strong close above the level
    """
    strategies = {
        "breakout_rejection": {
            "enabled": True,
            "direction": "short",
            # how far above/below the level we allow
            "tolerance": 0.05,
        },
        "breakout_acceptance": {
            "enabled": True,
            "direction": "long",
            "tolerance": 0.05,
        },
    }
    return strategies


# -------------------------
# 3. Mock data loader
# -------------------------

def mock_fetch_candles(market: str) -> List[Candle]:
    """
    This is just fake data so we can TEST the logic.

    We'll create a simple sequence where:
    - Price is below a level
    - Then it breaks above
    - Then it either rejects or accepts

    You can adjust these numbers to see different behaviours.
    """
    level = 100.0  # pretend "key resistance" level

    candles = [
        # Below the level, normal trading
        Candle("T1",  95,  99,  94,  98,  1000,   50),
        # Tests the level from below
        Candle("T2",  98, 101,  97, 100.5, 1200,  200),
        # Breakout candle (over level) - strong positive delta
        Candle("T3", 100.5, 103, 100, 102.5, 1500, 500),

        # Now we create either a rejection or an acceptance pattern.
        # You can play with these values.

        # Example REJECTION candle (closes back inside range, negative delta)
        Candle("T4", 102.5, 103.5,  99.5,  99.8, 1800, -400),

        # Small bounce after rejection
        Candle("T5",  99.8, 101,   98.5, 100.2, 1100,  50),

        # Fresh selling again
        Candle("T6", 100.2, 100.5,  95,   96.0, 2000, -600),
    ]

    # In a real bot, you’d fetch market data here instead.
    print(f"[TEST] Loaded {len(candles)} mock candles for {market}.")
    print(f"[TEST] Using level = {level}\n")
    return candles


# -------------------------
# 4. Strategy logic
# -------------------------

def is_breakout_rejection(prev: Candle, curr: Candle, level: float, tolerance: float) -> bool:
    """
    Simple breakout rejection logic:

    - Previous candle closed above the level (breakout attempt)
    - Current candle trades above the level BUT closes back below it
    - Current candle has NEGATIVE delta (selling stepped in)
    """
    # Was previous candle clearly above the level?
    prev_above = prev.close > level * (1 + tolerance)

    # Did the current candle poke above the level?
    curr_touched_above = curr.high > level

    # Did the current candle close back below or near the level?
    curr_closed_back_in = curr.close < level * (1 + tolerance)

    # Was there selling pressure?
    selling_pressure = curr.delta < 0

    return prev_above and curr_touched_above and curr_closed_back_in and selling_pressure


def is_breakout_acceptance(prev: Candle, curr: Candle, level: float, tolerance: float) -> bool:
    """
    Simple breakout acceptance logic:

    - Previous candle was near or just below the level
    - Current candle breaks above the level
    - Current candle closes clearly above the level
    - Current candle has POSITIVE delta (buyers in control)
    """
    prev_near_level = abs(prev.close - level) <= level * (2 * tolerance)

    curr_broke_above = curr.high > level and curr.close > level * (1 + tolerance)

    buying_pressure = curr.delta > 0 and curr.close > curr.open

    return prev_near_level and curr_broke_above and buying_pressure


# -------------------------
# 5. Signal generator
# -------------------------

def generate_signals_for_market(
    market: str,
    candles: List[Candle],
    strategies: Dict[str, Dict],
    level: float
) -> List[StrategySignal]:
    """
    Look through the candles and see if any of our strategy conditions are met.
    For now, we use a fixed 'level' for testing.
    """
    signals: List[StrategySignal] = []

    tolerance_reject = strategies["breakout_rejection"]["tolerance"]
    tolerance_accept = strategies["breakout_acceptance"]["tolerance"]

    for i in range(1, len(candles)):
        prev = candles[i - 1]
        curr = candles[i]

        # Breakout rejection (short)
        if strategies["breakout_rejection"]["enabled"]:
            if is_breakout_rejection(prev, curr, level, tolerance_reject):
                signals.append(
                    StrategySignal(
                        time=curr.time,
                        market=market,
                        strategy="breakout_rejection",
                        direction="short",
                        reason=(
                            f"Breakout above {level} failed on {curr.time}: "
                            f"delta={curr.delta}, close={curr.close} back below/near level."
                        ),
                    )
                )

        # Breakout acceptance (long)
        if strategies["breakout_acceptance"]["enabled"]:
            if is_breakout_acceptance(prev, curr, level, tolerance_accept):
                signals.append(
                    StrategySignal(
                        time=curr.time,
                        market=market,
                        strategy="breakout_acceptance",
                        direction="long",
                        reason=(
                            f"Breakout above {level} accepted on {curr.time}: "
                            f"strong close above level with positive delta={curr.delta}."
                        ),
                    )
                )

    return signals


# -------------------------
# 6. Main test runner
# -------------------------

def main():
    print("=== AlgoBot test run (no real trading yet) ===\n")

    # 1) Load our simple strategies
    strategies = load_strategies()

    # 2) Define test markets (later this could be ["NQ", "ES"])
    test_markets = ["TEST_NQ"]

    # 3) A simple test resistance level
    level = 100.0

    # 4) Loop through each market, load mock data, and search for signals
    for market in test_markets:
        candles = mock_fetch_candles(market)
        signals = generate_signals_for_market(market, candles, strategies, level)

        if not signals:
            print(f"[RESULT] No signals found for {market}.\n")
        else:
            print(f"[RESULT] Signals for {market}:")
            for sig in signals:
                print(
                    f"  - {sig.time}: {sig.strategy.upper()} | {sig.direction.upper()} | {sig.reason}"
                )
            print()

    print("=== Test run complete. If this printed without errors, your setup works. ===")


if __name__ == "__main__":
    main()
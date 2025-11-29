# main.py
# AlgoBot – simple skeleton wired up with:
# 1) Strategy loader (breakout rejection + breakout acceptance)
# 2) Data loader hook (where market data will come from later)
# 3) A run() function that ties it all together

from dataclasses import dataclass
from typing import List, Dict, Optional


# ========== Basic data structures ==========

@dataclass
class Candle:
    """Simple candle structure (we will fill this from real data later)."""
    time: str
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class FootprintBar:
    """Simple footprint structure (again, will be real later)."""
    time: str
    delta: float          # net buying vs selling
    total_volume: float   # total traded volume


@dataclass
class Signal:
    """What the bot should output when it finds a setup."""
    market: str           # e.g. "NQ", "ES"
    direction: str        # "LONG" or "SHORT"
    entry_price: float
    stop_price: float
    target_price: float
    reason: str           # short text: "breakout_rejection" etc.


# ========== Strategy loader ==========

def load_strategies() -> Dict[str, Dict]:
    """
    For now this just returns a dictionary with parameters
    for our two core strategies.

    Later we can move this to a separate file or load from JSON,
    but this is enough to get started.
    """

    breakout_rejection = {
        "name": "breakout_rejection_short",
        "direction": "SHORT",
        "min_positive_delta": 0.0,      # placeholder – we will tune later
        "min_negative_delta": 0.0,      # placeholder
        "lookback_candles": 2,          # breakout candle + next candle
    }

    breakout_acceptance = {
        "name": "breakout_acceptance_long",
        "direction": "LONG",
        "min_positive_delta": 0.0,      # placeholder
        "min_negative_delta": 0.0,
        "lookback_candles": 2,
    }

    strategies = {
        "breakout_rejection": breakout_rejection,
        "breakout_acceptance": breakout_acceptance,
    }

    return strategies


# ========== Data loader hook ==========

def load_market_data(market: str) -> Dict[str, List]:
    """
    This is a *stub* (placeholder) for market data.

    Later this function will:
      - connect to your data source / broker
      - download candles + footprint data
      - return them as Python lists of Candle / FootprintBar objects.

    For now, we just return empty lists so that the rest of the code runs.
    """

    candles: List[Candle] = []
    footprints: List[FootprintBar] = []

    # TODO (later):
    #   - pull real data from NQ/ES
    #   - or load from a CSV file for backtesting

    return {
        "candles": candles,
        "footprints": footprints,
    }


# ========== Strategy logic hooks (empty for now) ==========

def find_breakout_rejection_signals(
    market: str,
    candles: List[Candle],
    footprints: List[FootprintBar],
    params: Dict,
) -> List[Signal]:
    """
    Here is where we will later implement the actual rules:

      1. Candle breaks ABOVE a key level
      2. Breakout candle has strong positive delta
      3. Next candle closes back BELOW the level with negative delta
      4. Create a SHORT Signal

    Right now this just returns an empty list so the program runs.
    """

    signals: List[Signal] = []

    # TODO: implement real detection logic using candles + footprints

    return signals


def find_breakout_acceptance_signals(
    market: str,
    candles: List[Candle],
    footprints: List[FootprintBar],
    params: Dict,
) -> List[Signal]:
    """
    Here is where we will later implement the "trend-following breakout" rules:

      1. Strong uptrend
      2. Break above resistance
      3. Positive delta + strong buy imbalances
      4. No heavy absorption
      5. Create a LONG Signal

    Right now this just returns an empty list.
    """

    signals: List[Signal] = []

    # TODO: implement real detection logic

    return signals


# ========== Main runner ==========

def run():
    print("=== AlgoBot starting ===")

    # 1) Load strategy parameters
    strategies = load_strategies()
    print("Loaded strategies:", list(strategies.keys()))

    # 2) Decide which markets we care about (for now: NQ and ES)
    markets = ["NQ", "ES"]

    all_signals: List[Signal] = []

    for market in markets:
        print(f"\n--- Checking market: {market} ---")

        # 3) Load candles + footprint data for this market
        market_data = load_market_data(market)
        candles = market_data["candles"]
        footprints = market_data["footprints"]

        print(f"  Candles loaded: {len(candles)}")
        print(f"  Footprint bars loaded: {len(footprints)}")

        # 4) Run breakout rejection strategy
        rej_params = strategies["breakout_rejection"]
        rejection_signals = find_breakout_rejection_signals(
            market, candles, footprints, rej_params
        )
        print(f"  Breakout rejection signals found: {len(rejection_signals)}")
        all_signals.extend(rejection_signals)

        # 5) Run breakout acceptance strategy
        acc_params = strategies["breakout_acceptance"]
        acceptance_signals = find_breakout_acceptance_signals(
            market, candles, footprints, acc_params
        )
        print(f"  Breakout acceptance signals found: {len(acceptance_signals)}")
        all_signals.extend(acceptance_signals)

    # 6) Show all signals (later this is where we will send orders)
    print("\n=== Summary of signals ===")
    if not all_signals:
        print("No signals yet – logic still to be implemented.")
    else:
        for s in all_signals:
            print(
                f"{s.market} | {s.direction} | entry={s.entry_price} "
                f"stop={s.stop_price} target={s.target_price} | {s.reason}"
            )

    print("\nAlgoBot is ready for the next development step.")


if __name__ == "__main__":
    run()
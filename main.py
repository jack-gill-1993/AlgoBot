# AlgoBot – first strategy skeleton

# ---------------------------------------------------------
# 1. Strategy configurations (your “rules in code form”)
# ---------------------------------------------------------

STRATEGIES = {
    "breakout_rejection_short": {
        "name": "Breakout Rejection (Short)",
        "markets": ["NQ", "ES"],               # Nasdaq, S&P futures
        "timeframes": ["5m", "15m"],
        "direction": "SHORT",

        # Conditions for the breakout candle
        "breakout_candle": {
            "price_condition": "close_above_key_level",
            "delta_condition": "strong_positive_delta"
        },

        # Conditions for the confirmation candle
        "confirmation_candle": {
            "price_condition": "close_back_below_key_level",
            "delta_condition": "delta_turns_negative"
        },

        # Risk & exits
        "stop_rule": "a_little_above_breakout_high",
        "target_rule": "last_swing_low_or_liquidity_pocket",
        "max_risk_per_trade": 0.01  # 1% of account
    },

    "breakout_acceptance_long": {
        "name": "Breakout Acceptance (Trend-Following Long)",
        "markets": ["NQ", "ES"],
        "timeframes": ["5m", "15m"],
        "direction": "LONG",

        # Market context
        "trend_filter": "strong_uptrend",  # e.g. price above moving average, higher highs/lows

        # Breakout candle conditions
        "breakout_candle": {
            "price_condition": "close_above_resistance_level",
            "delta_condition": "positive_delta",
            "footprint_condition": "strong_buy_imbalances_no_heavy_absorption"
        },

        # Entry logic
        "entry": {
            "entry_type": "pullback_after_breakout",
            "pullback_condition": "price_retests_breakout_zone_and_holds"
        },

        # Risk & exits
        "stop_rule": "below_breakout_zone_or_recent_swing_low",
        "target_rule": "trend_follow_trailing_stop",
        "trailing_stop_method": "ATR_or_structure",
        "max_risk_per_trade": 0.01  # 1% of account
    }
}

# ---------------------------------------------------------
# 2. Simple helper to show what’s configured
# ---------------------------------------------------------

def show_strategies() -> None:
    """Print a human-readable summary of all strategies."""
    print("Configured strategies:\n")
    for key, strat in STRATEGIES.items():
        print(f"- ID: {key}")
        print(f"  Name:      {strat['name']}")
        print(f"  Direction: {strat['direction']}")
        print(f"  Markets:   {', '.join(strat['markets'])}")
        print(f"  Timeframes:{', '.join(strat['timeframes'])}")
        print(f"  Stop rule: {strat['stop_rule']}")
        print(f"  Target:    {strat['target_rule']}")
        print(f"  Max risk:  {strat['max_risk_per_trade'] * 100:.1f}%\n")


# ---------------------------------------------------------
# 3. Main entry point (for now just prints your strategies)
# ---------------------------------------------------------

def run():
    """
    First very simple version of AlgoBot:
    - Just prints out the strategies we have defined.
    - Later this will:
        1. Pull live price / footprint data
        2. Detect setups using STRATEGIES config
        3. Send orders to broker (paper first!)
    """
    print("AlgoBot is starting...\n")
    show_strategies()
    print("AlgoBot is ready to grow...")

if __name__ == "__main__":
    run()
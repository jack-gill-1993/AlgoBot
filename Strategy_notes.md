# AlgoBot – Strategy Notes

Goal:
- Fully automated breakout + breakout-rejection bot on indices (NQ, ES, etc.)

Phase 1 – Data:
- Pull OHLCV candles from broker / data provider
- (Later) Pull footprint-style data (bid/ask volume, delta if available)

Phase 2 – Setups:
- Breakout trend-following
- Breakout rejection (fakeout) around key levels

To Do:
- Define exact breakout rules
- Define stop-loss and take-profit logic
- Define when NOT to trade (news, super low volume, etc.)
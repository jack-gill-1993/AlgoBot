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

# AlgoBot – Strategy Notes

## Core setups

1. Breakout rejection (short bias)
   - Watch Nasdaq / S&P futures (NQ, ES)
   - Price breaks above a key level
   - Footprint shows:
     - Big positive delta on breakout candle
     - Next candle: negative delta + price back inside range
   - Action:
     - Enter short
     - Stop: above breakout high
     - Target: last liquidity pocket / prior low

2. Trend-following breakout (long bias)
   - Strong trend up
   - Break above resistance
   - Footprint shows:
     - Positive delta
     - Strong buy imbalances
     - No heavy absorption at top
   - Action:
     - Enter long on pullback
     - Stop: below breakout zone
     - Trail stop with ATR / structure

## Markets

- Start with:
  - NQ futures (Nasdaq)
  - ES futures (S&P 500)
- Later: maybe add crypto (BTC, ETH)

## Risk rules

- Max risk per trade: 1% of account
- No trading during major outages (like CME issues)
- Avoid very low-volume days / holidays
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
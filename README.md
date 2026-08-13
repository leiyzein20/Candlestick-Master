# Candlestick-Master

A TradingView Pine Script v6 indicator that recognizes candlestick patterns (educational tool — no trade signals, no strategy). Works on the TradingView free plan.

**Script:** [`candlestick_master.pine`](candlestick_master.pine)

## What it does

- **OHLC-based detection** — pattern validity comes from the open/high/low/close relationship, never candle color alone. Candle sizes are scaled by ATR(14), so "long body" and "small body" adapt to any pair and any timeframe.
- **Trend context** — reversal patterns only appear after the required prior trend (bullish reversals need a downtrend, bearish reversals need an uptrend), detected via EMA(20)/EMA(50) plus slope.
- **Timeframe gating** — each pattern has its ideal timeframes (e.g. H1 · H4 · D1) and only appears when the chart is on one of them. A pattern with 3 ideal timeframes shows on all 3.
- **Confirmation engine** — confirmation candle (next close beyond the pattern high/low), RSI level + divergence, volume spike (tick volume on forex), and 20 EMA reclaim/loss. Passed checks are scored into `Validation: WEAK / MODERATE / STRONG`.
- **Clean chart** — only the abbreviation is drawn (HAM, BEC, DFD…). Hover the label on desktop, or press-and-hold on mobile, to see the full dynamic checklist:

```
BEC
Bullish Engulfing
Status: CONFIRMED ✓
─────────────
Pattern: Valid ✓
Trend: Downtrend ✓
Location: Support zone ✓
RSI: Bullish divergence ✓
EMA: Reclaiming 20 EMA ✓
Volume: Above average ✓ (tick vol)
─────────────
Validation: STRONG
─────────────
After a downtrend, a small bearish candle's body is fully engulfed by a large bullish candle...
SL: below the engulfing candle low  |  TP: nearest resistance then swing high
Reliability: ★ High (78%) · Ideal TF: H1 · H4 · D1
```

- **Lifecycle tracking** — labels update from `DETECTED — AWAITING CONFIRMATION` to `CONFIRMED ✓`, `FAILED ✗` (invalidation level hit, label dims), or `EXPIRED` (no confirmation within the window).

## How to install

1. Open any chart on [tradingview.com](https://www.tradingview.com).
2. Open the **Pine Editor** panel (bottom of the chart).
3. Delete the default code, paste the full contents of `candlestick_master.pine`.
4. Click **Add to chart**.
5. Open the indicator **Settings** (gear icon) to filter what you see.

## Filtering (Settings panel)

- **Category** — show only Bullish reversal / Bearish reversal / Continuation / Indecision patterns. To see bullish patterns only: untick everything except "Bullish reversal patterns".
- **Priority tier** — Must / Important / Rare (Rare is off by default).
- **Structure** — Single / Double / Triple & multi candle.
- **Individual patterns** — every pattern has its own checkbox.
- **Timeframe gating** — "Ignore timeframe filter" shows patterns on every chart timeframe (testing only).
- **Confirmation** — "Show only confirmed patterns" hides a pattern until the confirmation candle closes.

## Pattern coverage

Batch 1 (implemented with the master's spec data): 01 Hammer (HAM), 02 Hanging Man (HGM), 03 Inverted Hammer (IH), 04 Shooting Star (SST), 05 Bullish Marubozu (BUM), 06 Bearish Marubozu (BEM), 07 Spinning Top (SPT), 08 Standard Doji (DOJ), 09 Long-Legged Doji (LLD), 10 Dragonfly Doji (DFD). Previews awaiting spec data: Gravestone Doji (GSD), Bullish Engulfing (BEC).

Remaining batches (11–45) plug into the same engines: each new pattern is one shape condition plus one `fire()` call. Ideal timeframes per pattern are the `"60,240,D"`-style strings in each `fire()` call.

## Disclaimer

Strictly an educational tool. Not financial advice. Trading involves substantial risk — always do your own research.

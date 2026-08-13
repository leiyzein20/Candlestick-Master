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

**Single candle (01–12):** 01 Hammer (HAM), 02 Hanging Man (HGM), 03 Inverted Hammer (IH), 04 Shooting Star (SST), 05 Bullish Marubozu (BUM), 06 Bearish Marubozu (BEM), 07 Spinning Top (SPT), 08 Standard Doji (DOJ), 09 Long-Legged Doji (LLD), 10 Dragonfly Doji (DFD), 11 Gravestone Doji (GSD), 12 Four Price Doji (FPD).

**Double candle (13–25):** 13 Bullish Engulfing (BEC), 14 Bearish Engulfing (BRE), 15 Bullish Harami (BUH), 16 Bearish Harami (BEH), 17 Harami Cross (HC), 18 Piercing Line (PL), 19 Dark Cloud Cover (DCC), 20 Tweezer Bottom (TWB), 21 Tweezer Top (TWT), 22 Matching Low (ML), 23 Matching High (MH), 24 Stick Sandwich (SSW), 25 Kicking Pattern (KCK).

**Triple & multi candle (26–40):** 26 Morning Star (MS), 27 Evening Star (ES), 28 Morning Doji Star (MDS), 29 Evening Doji Star (EDS), 30 Three White Soldiers (TWS), 31 Three Black Crows (TBC), 32 Three Inside Up (TIU), 33 Three Inside Down (TID), 34 Three Outside Up (TOU), 35 Three Outside Down (TOD), 36 Rising Three Methods (RTM), 37 Falling Three Methods (FTM), 38 Breakaway Bullish (BWY), 39 Ladder Bottom (LDB), 40 Concealing Baby Swallow (CBS).

Remaining: patterns 41–45, pending spec data. New patterns plug into the same engines: each one is a shape condition plus one `fire()` call. Ideal timeframes per pattern are the `"60,240,D"`-style strings in each `fire()` call.

## Disclaimer

Strictly an educational tool. Not financial advice. Trading involves substantial risk — always do your own research.

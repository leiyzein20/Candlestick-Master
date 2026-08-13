# Candlestick Pattern Master — TradingView Pine Script Suite

A single Pine Script v6 indicator (`candlestick-pattern-master.pine`) that detects **45
classic candlestick patterns** (12 single-candle, 13 double-candle, 20 triple/multi-candle),
gates each one to the chart time frame(s) it's actually reliable on, scores every hit with a
live **RSI / EMA / Volume / Trend / Location confirmation checklist**, and draws only a clean
abbreviation on the chart — full detail lives in the hover tooltip.

This document also answers the actual question you asked: **"how should the prompt be"** —
i.e. how to describe this kind of indicator to an AI (me or anyone else) so it gets built,
and extended, correctly. Skip to [The Master Prompt](#the-master-prompt) if that's all you need.

---

## 1. What the script actually does

| Requirement you listed | How it's implemented |
|---|---|
| Coordinate with RSI / Volume for confirmation | Every pattern runs through a shared confirmation engine: prior Trend (EMA50 vs EMA200), Location (near swing support/resistance), RSI (oversold/overbought or momentum), EMA20 reclaim/break, and Volume vs its average. Result is a 0–5 score → **WEAK / MODERATE / STRONG**. |
| Wick-accurate body length | Every single/double/triple pattern formula compares real `body`, `upperWick`, `lowerWick`, `range` ratios (e.g. Hammer requires `lowerWick ≥ 2×body` **and** `≥ 40% of range`), not just open/close color. |
| After downtrend / after uptrend / continuation / exhaustion / reversal | Each pattern is tagged `Bullish Reversal`, `Bearish Reversal`, `Bullish Continuation`, `Bearish Continuation`, or `Neutral/Indecision`, and reversal patterns require the correct prior trend context to even qualify as a "hit". |
| Closing above/below 50% of previous candle | Used explicitly in Piercing Line / Dark Cloud Cover / In-Neck Line (`prevMid = (open[1]+close[1])/2`). |
| Gaps | Used in Kicker, Breakaway, Concealing Baby Swallow, Upside Gap Two Crows. |
| Separate by time frame, only show on the *ideal* time frame(s) | See §2 below — this is the core mechanic you asked for. |
| Abbreviation on chart, full description on hover | `label.new(..., text = "BEC", tooltip = fullDescription)` — TradingView shows the tooltip only when you hover/hold over the label, keeping the chart clean. |
| Filter to only bullish, only bearish, only continuation, etc. | Toggle inputs: *Show Bullish Reversal*, *Show Bearish Reversal*, *Show Bullish Continuation*, *Show Bearish Continuation*, *Show Neutral*, plus *Show Single/Double/Triple-Candle* and *Minimum catalog priority*. |

---

## 2. How the time-frame gating works (the part you emphasized)

TradingView's `timeframe.period` returns the *exact* resolution code of the chart you're
currently viewing (`"1"`, `"5"`, `"15"`, `"60"`, `"240"`, `"D"`, `"W"`, `"M"`, etc — this
covers every free-plan resolution: 1m/2m/3m/5m/10m/15m/30m/45m and 1H/2H/3H/4H, plus D/W/M).

Each pattern stores its ideal time frames as a simple comma list, e.g.:

```
Hammer            -> "60,240,D"      (H1 · H4 · D1 — exactly as in your reference doc)
Bullish Marubozu  -> "15,60,240,D"   (M15 · H1 · H4 · D1)
Tri-Star Bullish  -> "D,W"           (D1 · W1)
```

A tiny helper checks whether the *current* chart resolution is anywhere in that list:

```pinescript
f_tfAllow(idealCsv) => str.contains("," + idealCsv + ",", "," + timeframe.period + ",")
```

So if a pattern has **3** ideal time frames, it will show on **any of the 3** — switch from
H1 to H4 to D1 and it keeps appearing, exactly as you asked ("if a candle pattern has 3 ideal
time frames then that candle must show in 3 different time frames not just one"). Turn the
*"Only show a pattern on ITS ideal time frame(s)"* input OFF if you want to see every pattern
on every time frame regardless (useful while learning/back-testing the shapes themselves).

---

## 3. The hover/hold tooltip — your BEC example, corrected & extended

Your proposed format was **on the right track**. Two small fixes make it actually work as a
*live* checklist instead of a static caption:

1. `label.new()` is the only drawing object with a real hover `tooltip` — `plotshape()`/`plotchar()` cannot show per-occurrence dynamic text, only `label.new()` can (confirmed against the current Pine v6 reference). That's what this script uses everywhere.
2. Your checklist items ("Trend: Downtrend ✓", "RSI: Bullish divergence ✓"...) need to be *computed*, not hard-coded — otherwise every BEC on the chart would show the same canned text. The script recomputes each line from live indicator values at the exact bar the pattern formed.

What you'll actually see when you hover a **BEC** label:

```
BEC
Bullish Engulfing
Status: CONFIRMED

After a downtrend, a small bearish candle appears whose body is fully engulfed
by a large bullish candle. One of the most reliable and best-known upside
reversal patterns.

Ideal Time Frame: 60,240,D

Professional Validation
Pattern: Valid ✓
Trend: Downtrend ✓
Location: Support ✓
RSI: Oversold ✓
EMA: Reclaiming 20 EMA ✓
Volume: Above average ✓

Validation: STRONG
Reliability: ★ High (~75%)   |   Risk:Reward 1:2 – 1:3
```

Status logic: `CONFIRMED` (score 5/5), `FORMING` (3–4/5), `WATCH` (0–2/5) — and the label color
itself (teal/red/gray, customizable) gives you an instant visual read even before hovering.
Every other pattern (HAM, MOR, TWS, 3IU, etc.) uses this exact same template with its own name,
description, bias-appropriate wording ("Uptrend"/"Resistance"/"Breaking EMA" for bearish
patterns), reliability tier and R:R.

---

## 4. Installing & using it

1. Open TradingView → **Pine Editor** (bottom panel) → **New blank indicator**.
2. Delete the placeholder code, paste in the full contents of [`candlestick-pattern-master.pine`](./candlestick-pattern-master.pine).
3. Click **Add to Chart**. Open the ⚙️ **Settings** to toggle categories, min-validation grade, RSI/EMA/Volume parameters, colors, etc.
4. Switch your chart resolution (bottom toolbar) between M1…M45, H1…H4, D1, W1 — patterns will appear/disappear automatically based on their own ideal-timeframe tags.
5. Hover any abbreviation label to read the full name + live confirmation checklist.
6. Use the ⋯ menu → **Add Alert** on this indicator to pick from the 5 grouped `alertcondition`s (Bullish Reversal / Bearish Reversal / Bullish Continuation / Bearish Continuation / Neutral confirmed).

**Example filter combinations** (all just checkbox toggles in Settings → no code edits needed):

- *"I only want bullish patterns"* → turn OFF "Show Bearish Reversal" and "Show Bearish Continuation", leave the two bullish ones ON.
- *"I only want reversal patterns, not continuation"* → turn OFF both Continuation toggles.
- *"I only want the highest-probability setups"* → set **Minimum catalog priority = Must Only** and **Minimum validation grade = STRONG**.
- *"I want to see raw shapes while I'm learning, ignore confirmation"* → set **Minimum validation grade = ANY**.
- *"I only trade H4/D1"* → just switch the chart to H4 or D1; with TF-restriction ON, only the patterns tagged for that timeframe will ever appear — no toggle needed.

---

## 5. Full pattern catalog implemented in the script

| # | Abbr | Pattern | Bias/Role | Structure | Ideal TF | Priority |
|---|------|---------|-----------|-----------|----------|----------|
| 1 | HAM | Hammer | Bullish Reversal | Single | H1·H4·D1 | Must |
| 2 | HGM | Hanging Man | Bearish Reversal | Single | H1·H4·D1 | Must |
| 3 | IVH | Inverted Hammer | Bullish Reversal | Single | H1·H4·D1 | Important |
| 4 | SST | Shooting Star | Bearish Reversal | Single | H1·H4·D1 | Must |
| 5 | BMZ | Bullish Marubozu | Bullish Continuation | Single | M15·H1·H4·D1 | Important |
| 6 | RMZ | Bearish Marubozu | Bearish Continuation | Single | M15·H1·H4·D1 | Important |
| 7 | DOJ | Doji | Neutral | Single | M15·H1·H4·D1 | Important |
| 8 | LLD | Long-Legged Doji | Neutral | Single | H1·H4·D1 | Rare |
| 9 | DFD | Dragonfly Doji | Bullish Reversal | Single | H1·H4·D1 | Important |
| 10 | GSD | Gravestone Doji | Bearish Reversal | Single | H1·H4·D1 | Important |
| 11 | SPT | Spinning Top | Neutral | Single | H1·H4·D1 | Rare |
| 12 | HWC | High Wave Candle | Neutral | Single | H4·D1 | Rare |
| 13 | BEC | Bullish Engulfing | Bullish Reversal | Double | H1·H4·D1 | Must |
| 14 | BEA | Bearish Engulfing | Bearish Reversal | Double | H1·H4·D1 | Must |
| 15 | BHR | Bullish Harami | Bullish Reversal | Double | H1·H4·D1 | Important |
| 16 | BHB | Bearish Harami | Bearish Reversal | Double | H1·H4·D1 | Important |
| 17 | HXB | Bullish Harami Cross | Bullish Reversal | Double | H1·H4·D1 | Rare |
| 18 | HXR | Bearish Harami Cross | Bearish Reversal | Double | H1·H4·D1 | Rare |
| 19 | PIL | Piercing Line | Bullish Reversal | Double | H4·D1 | Important |
| 20 | DCC | Dark Cloud Cover | Bearish Reversal | Double | H4·D1 | Important |
| 21 | TWB | Tweezer Bottom | Bullish Reversal | Double | H1·H4·D1 | Rare |
| 22 | TWT | Tweezer Top | Bearish Reversal | Double | H1·H4·D1 | Rare |
| 23 | BKK | Bullish Kicker | Bullish Reversal | Double | H4·D1 | Rare |
| 24 | RKK | Bearish Kicker | Bearish Reversal | Double | H4·D1 | Rare |
| 25 | INL | In-Neck Line | Bearish Continuation | Double | H4·D1 | Rare |
| 26 | MOR | Morning Star | Bullish Reversal | Triple | H4·D1 | Must |
| 27 | EVE | Evening Star | Bearish Reversal | Triple | H4·D1 | Must |
| 28 | MDS | Morning Doji Star | Bullish Reversal | Triple | H4·D1 | Important |
| 29 | EDS | Evening Doji Star | Bearish Reversal | Triple | H4·D1 | Important |
| 30 | TWS | Three White Soldiers | Bullish Reversal | Triple | H4·D1 | Must |
| 31 | TBC | Three Black Crows | Bearish Reversal | Triple | H4·D1 | Must |
| 32 | 3IU | Three Inside Up | Bullish Reversal | Triple | H4·D1 | Important |
| 33 | 3ID | Three Inside Down | Bearish Reversal | Triple | H4·D1 | Important |
| 34 | 3OU | Three Outside Up | Bullish Reversal | Triple | H4·D1 | Important |
| 35 | 3OD | Three Outside Down | Bearish Reversal | Triple | H4·D1 | Important |
| 36 | R3M | Rising Three Methods | Bullish Continuation | Multi (5) | H4·D1 | Important |
| 37 | F3M | Falling Three Methods | Bearish Continuation | Multi (5) | H4·D1 | Important |
| 38 | BRK | Breakaway (Bullish) | Bullish Reversal | Multi (5) | D1 (gap) | Rare |
| 39 | LDB | Ladder Bottom | Bullish Reversal | Multi (4) | D1 | Rare |
| 40 | CBS | Concealing Baby Swallow | Bullish Reversal | Multi (4) | D1 | Rare |
| 41 | U3R | Unique Three River | Bullish Reversal | Triple | D1 | Rare |
| 42 | TRS | Tri-Star (Bullish) | Bullish Reversal | Triple | D1·W1 | Rare |
| 43 | ADB | Advance Block | Bearish Reversal | Triple | H4·D1 | Important |
| 44 | DLB | Deliberation Pattern | Bearish Reversal | Triple | H4·D1 | Important |
| 45 | UTC | Upside Gap Two Crows | Bearish Reversal | Triple | D1 (gap) | Rare |

> Patterns #38–41 and #45 are inherently rare, complex, multi-candle shapes. The script
> implements pragmatic heuristics that closely follow the textbook description you provided;
> always eyeball-confirm these specific ones before trusting the label.

---

## The Master Prompt

This is the reusable specification — hand this to any AI (or re-read it yourself as a spec)
whenever you want to **regenerate, extend, or fork** this indicator. It's written the way you
should always brief this kind of request: scope, structure, per-pattern metadata, confirmation
logic, UI behavior, and output format, all explicit.

```
Build a single Pine Script v6 TradingView indicator called "<name>" that detects the
following candlestick patterns ONLY (no trend-following/oscillator signals of its own —
candlestick pattern recognition is the entire scope):

1. PATTERN LIST
   For each pattern, provide: Name, Abbreviation (2–4 chars, unique), Structure
   (Single/Double/Triple+ candle), Bias/Role (Bullish Reversal / Bearish Reversal /
   Bullish Continuation / Bearish Continuation / Neutral-Indecision), Priority
   (Must / Important / Rare), Ideal Time Frame(s) (using TradingView's own resolution
   codes: 1,2,3,5,10,15,30,45 for minutes; 60,120,180,240 for H1–H4; D, W, M for
   Daily/Weekly/Monthly), a 1–2 sentence description, approximate reliability % and
   risk:reward.

2. DETECTION ACCURACY
   - Base every pattern on real OHLC geometry: body = |close-open|, range = high-low,
     upperWick = high-max(open,close), lowerWick = min(open,close)-low. Use wick:body
     ratios (e.g. "lower wick ≥ 2× body"), NOT candle color, to validate shape.
   - Reversal patterns must additionally check for the required PRIOR trend (down for
     bullish reversals, up for bearish reversals) measured on price action *before* the
     pattern's own candles — never let the pattern's own candles create the trend
     signal (no self-fulfilling detection).
   - Use closing-above/below-50%-of-previous-candle logic where the classic definition
     calls for it (Piercing Line, Dark Cloud Cover, In-Neck Line).
   - Detect true gaps (open beyond prior high/low) for gap-dependent patterns (Kicker,
     Breakaway, Upside Gap Two Crows, Concealing Baby Swallow).

3. TIME-FRAME GATING
   - Every pattern only renders while the chart's `timeframe.period` matches ONE OF its
     own ideal-time-frame tags (encode as a comma list, match with a "contains" check
     wrapped in delimiters so "5" doesn't accidentally match inside "45"/"15").
   - If a pattern lists 3 ideal time frames, it must appear on all 3 when the chart is
     switched to any of them — never restrict to a single hardcoded time frame.
   - Provide a master ON/OFF toggle to disable time-frame restriction entirely (useful
     for study/backtesting).

4. CONFIRMATION ENGINE (applies uniformly to every pattern via one shared function)
   - Trend: EMA(fast) vs EMA(slow), evaluated BEFORE the pattern's candles.
   - Location: is price near a recent swing low (bullish) / swing high (bearish),
     tolerance in ATR.
   - RSI: oversold/rising for bullish, overbought/falling for bearish.
   - EMA: price reclaiming/breaking a shorter confirmation EMA (flag whether it JUST
     crossed vs already was beyond it, for wording).
   - Volume: current volume vs its moving average × multiplier (note for forex: this is
     tick volume, treat as relative-only).
   - Produce a 0–5 confirmation score → WEAK (0–2) / MODERATE (3–4) / STRONG (5), and a
     status word WATCH / FORMING / CONFIRMED.

5. DISPLAY / UX
   - Draw ONLY a short abbreviation on the chart via label.new() (never the full name —
     keep the chart uncluttered). Color-code bullish/bearish/neutral.
   - On hover, the label's tooltip must show: Abbreviation, Full name, live Status,
     the pattern description, its ideal time frame tag, then a "Professional
     Validation" checklist with a line per confirmation factor (Trend/Location/RSI/
     EMA/Volume) each ending in ✓ or ✗ computed live, then the overall Validation
     grade and the reliability/R:R stats.
   - Provide checkbox filters for: Show Single/Double/Triple-candle, Show Bullish
     Reversal / Bearish Reversal / Bullish Continuation / Bearish Continuation /
     Neutral, Minimum catalog priority, Minimum validation grade to display, and a
     max-labels-per-bar cap to prevent clutter when several patterns fire on one candle.
   - Stack multiple same-bar labels vertically (offset by ATR) instead of overlapping.
   - Group alertcondition()s by bias/role category (not 45 separate alerts) so users
     can build 3–5 simple TradingView alerts instead of dozens.

6. CONSTRAINTS
   - Pine Script v6 syntax only. No repainting: never use future bars; base all
     "prior trend" lookups on bars strictly before the pattern.
   - Educational-tool disclaimer only — never present this as financial advice.

Now generate the complete, ready-to-paste .pine file, followed by a short usage guide.
```

**How to reuse/adapt this prompt for a narrower ask** — just add a one-line constraint on
top, e.g.:

- `"...only include the 13 double-candle patterns, skip everything else."`
- `"...I only trade H4 and D1, drop every pattern whose ideal timeframe list doesn't include one of those two."`
- `"...swap the confirmation engine's RSI for a MACD histogram cross instead."`
- `"...I want individual on/off toggles per pattern, not just per category (accept a longer settings panel)."`

The structure of the prompt (scope → per-pattern metadata → detection accuracy rules →
time-frame gating → confirmation engine → display/UX → constraints) is what matters — keep
those seven sections whenever you brief this to any AI and you'll get a consistent, working
result every time.

---

## 6. Limitations & honesty notes

- This is pattern-shape + rule-based detection, not machine learning — like any candlestick
  scanner (including paid ones) it will occasionally mis-flag borderline shapes. Treat every
  label as a *candidate*, and use the confirmation checklist + your own visual read before
  acting.
- Forex spot data on TradingView is tick volume, not true traded volume — the Volume
  confirmation line is directional/relative only.
- Patterns #38 (Breakaway), #39 (Ladder Bottom), #40 (Concealing Baby Swallow), #41 (Unique
  Three River) and #45 (Upside Gap Two Crows) are rare, highly specific multi-candle shapes;
  the detection logic is a faithful-but-simplified approximation of the classic definition.
- Nothing in this script or document is financial advice. Trading forex carries substantial
  risk — always do your own research (DYOR) and backtest before risking real capital.

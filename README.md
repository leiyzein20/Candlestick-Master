# Candlestick Master 45

A TradingView (Pine Script v6) indicator that reads candlestick patterns the way a
price-action trader does: pure OHLC geometry, every pattern gated to its own ideal time
frame, an abbreviation-only chart, and a hold-to-read card that cross-checks the pattern
against trend, location, RSI, EMA and volume before it calls anything confirmed.

| | |
| :-- | :-- |
| **Indicator** | [`pine/candlestick_master_45.pine`](pine/candlestick_master_45.pine) |
| **The prompt you asked for** | [`prompts/MASTER_PROMPT.md`](prompts/MASTER_PROMPT.md) |
| **How to feed it pattern data** | [`prompts/PATTERN_CARD_TEMPLATE.md`](prompts/PATTERN_CARD_TEMPLATE.md) |
| **All 45 patterns + the TF gate table** | [`docs/PATTERNS.md`](docs/PATTERNS.md) |

---

## 1. Getting started

1. Open TradingView, then `Pine Editor` at the bottom of the chart.
2. `Open` → `New indicator`, delete the template, paste the whole contents of
   [`pine/candlestick_master_45.pine`](pine/candlestick_master_45.pine).
3. `Save`, give it a name, then `Add to chart`.
4. Put the chart on **H4** first. That is where the largest part of the catalogue is armed
   (39 of the 45 patterns), so it is the fastest way to confirm the script is working.
5. Open the settings gear and walk down the six groups: Display, Filters, Time Frame
   Engine, Confirmation Engine, Pattern Geometry, Alerts.

If the chart is empty on your first look, that is usually correct behaviour rather than a
bug — see the next section.

---

## 2. The time frame gate

This was your main requirement, so it is the part of the engine that is least willing to
compromise.

Every pattern carries its own list of ideal time frames. With the default **Strict**
setting a pattern draws only when your chart is on one of them. A pattern with three ideal
time frames prints on all three:

- `BEC` (Bullish Engulfing) is `H1 · H4 · D1` → it appears on H1, on H4 and on D1.
- `CBS` (Concealing Baby Swallow) is `D1` → it appears on D1 and nowhere else.
- `TS3` (Tri-Star) is `D1 · W1` → two time frames, both of them armed.

Switch your chart to M5 and the chart goes clean, because nothing in the catalogue is a
five-minute signal. That is the intended result: the gate is what stops a D1 Morning Star
from being counted as a scalping signal.

The full map of which patterns are armed on which time frame is in
[`docs/PATTERNS.md`](docs/PATTERNS.md). The short version:

| Chart | Patterns armed |
| :-- | --: |
| M1 – M10, M30, M45, H2, H3, MN1 | 0 |
| M15 | 4 |
| H1 | 17 |
| H4 | 39 |
| D1 | 39 |
| W1 | 3 |

Three gating modes are available:

- **Strict — ideal time frames only** (default). What a candlestick master would do.
- **Ideal ± 1 step.** Widens each pattern by one rung of the ladder
  `M1 M2 M3 M5 M10 M15 M30 M45 H1 H2 H3 H4 H6 H8 H12 D1 W1 MN1`, so an `H4 · D1` pattern
  also prints on H3 and W1. Useful on H2 and H3, which are otherwise empty.
- **Off.** Every pattern on every time frame. Use this for studying, not for trading.

The matching is delimiter-safe, so `M1` never accidentally matches `M15`.

---

## 3. Abbreviation on the chart, full card on hold

The chart only ever shows the abbreviation — `BEC`, `HAM`, `MST` — so it stays readable.
Bullish labels sit under the candle, bearish above it, spaced by ATR so they scale with
volatility. If several patterns fire on the same candle they stack, capped by
`Max labels per candle` (default 3).

Hover the label on desktop, or hold it on mobile, and you get the card. Yes — the format
you wrote out is exactly what it produces:

```text
BEC
Bullish Engulfing
Status: CONFIRMED

Pattern: Valid ✓
Trend: Downtrend ✓
Location: Support ✓
RSI: Bullish divergence (28.4) ✓
EMA: Above 20 EMA (just reclaimed) ✓
Volume: Above average ✓

Validation: STRONG (5/5)
──────────────────────────────
#13 · Double Candle · Reversal
Structure: 2-candle · Bullish · Must
Ideal time frame: H1 · H4 · D1   (chart: H4)
Reliability: 78%
Pattern high: 1.09412   Pattern low: 1.09180
──────────────────────────────
WHAT IT IS
After a downtrend, a small bearish candle appears whose body is fully engulfed by a large
bullish candle. One of the most reliable and best-known upside reversal patterns.

HOW TO RECOGNIZE
Prior downtrend. Candle 1 bearish, candle 2 bullish with its BODY covering the entire body
of candle 1 (shadows may exceed). The larger the engulfing ratio the stronger.

STOP LOSS
Below the low of the engulfing pattern.

TAKE PROFIT
Nearest resistance then the swing high. This pattern often starts long moves — consider
trailing.

PRO TIP
Engulfing at major support with heavy volume is an A+ setup. Do not require the shadows to
be engulfed — the body alone is the definition.
```

Two things about that block are worth being precise about, because they are where most
pattern scanners quietly lie:

**Every ✓ is a live measurement, not decoration.** When a check fails you get the real
state and a ✗, for example `Trend: Downtrend ✗` or `Volume: No volume data ✗`. A pattern
with a valid shape but no supporting context still prints — with `Validation: WEAK (1/5)`.
Hiding it would be lying by omission; scoring it tells you what you are actually looking
at.

**`Status: CONFIRMED` genuinely means confirmed.** It cannot be known until the candle
after the pattern closes, so the script evaluates one bar late and draws the label back
onto the pattern candle. The label appears one candle after the pattern completes, and it
never repaints or disappears afterwards. If you would rather see patterns the moment they
close, turn off `Wait for the confirmation candle` — the status then reads `FORMING`, which
is honest about what it is.

---

## 4. How it coordinates with RSI, EMA and volume

You asked for confirmation from other indicators. Rather than making you stack three more
indicators on the chart and eyeball them, the five cross-checks are computed inside this
one script and scored:

| Check | Bullish pattern passes when | Bearish pattern passes when |
| :-- | :-- | :-- |
| **Trend** | a downtrend existed *before* the pattern's first candle | an uptrend existed before it |
| **Location** | the pattern low sits on a recent swing-pivot support | the pattern high sits on a recent swing-pivot resistance |
| **RSI** | RSI is oversold, or a pivot-based bullish divergence is live | overbought, or a bearish divergence is live |
| **EMA** | price is above the fast EMA (flagged when just reclaimed) | price is below it (flagged when just lost) |
| **Volume** | volume is above its own average by the multiplier | same |

Score 5 or 4 is `STRONG`, 3 is `MODERATE`, 1–2 is `WEAK`, 0 is `NONE`. Set
`Minimum validation score` to 4 and the chart shows only A+ setups.

The trend check is measured **before** the pattern starts — a 3-candle pattern reads the
trend state 3 bars back. That matters: a Morning Star's own three candles would otherwise
help create the "downtrend" the pattern is supposed to be reversing.

Trend is the one check allowed to be definitional, and only where it genuinely is the
definition. A Hammer and a Hanging Man are the identical shape; the prior trend is the only
thing that separates them. Set the trend mode to `Off` and you will see both fire on the
same candle, which is the mathematically correct consequence.

---

## 5. Filtering — "I only want bullish patterns"

Everything is in the `② Filters` group, no code editing:

- **Direction** — All / Bullish only / Bearish only / Neutral only.
- **Pattern role** — All / Reversal / Continuation / Exhaustion / Indecision.
- **Category switches** — single-candle (12), double-candle (13), triple & multi (20).
- **Priority** — All / Must only / Must + Important.
- **Minimum reliability %.**
- **Whitelist** — `BEC,HAM,MST` shows only those three, everything else is silent.
- **Blacklist** — `SPT,DOJ,LLD` kills the noisy indecision patterns while keeping the rest.

The direction filter is applied to the direction that actually *fired*, not to the
catalogue entry, so a bearish Belt Hold stays hidden while `Bullish only` is selected even
though Belt Hold is catalogued as a dual-direction pattern.

Useful starting combinations:

| You want | Settings |
| :-- | :-- |
| Only bullish reversals worth trading | Direction `Bullish only`, Role `Reversal only`, Priority `Must only`, min score 3 |
| A clean swing chart | Chart H4, Priority `Must + Important`, min reliability 70, status `Confirmed only` |
| Study one pattern in depth | Whitelist `BEC`, TF gating `Off`, status `Everything (incl. failed)` |
| Trend-following entries only | Role `Continuation only` |

---

## 6. Forex and gaps

Spot forex trades 24/5 and almost never gaps. Under the textbook stock-market definitions,
Morning Star, Tri-Star, Breakaway, Concealing Baby Swallow, Kicker and Upside Gap Two Crows
require a true price gap, which means on EURUSD they would essentially never fire.

The `Gap rule` setting handles this:

- **Strict (wick gap)** — the classic definition. Correct for indices, stocks and crypto
  weekends.
- **Body gap (forex-friendly)** — *default*. The bodies must not overlap, which preserves
  the psychology of the separation without demanding a true gap.
- **Off** — ignore the gap clause entirely. Loosest, and it will produce false positives.

The Kicker is deliberately exempt from the loosening: even in body mode its open must clear
the entire previous candle. Without that exception every ordinary higher open would be
labelled a kicker.

---

## 7. Free plan notes

- The indicator is one script, and the free plan allows up to three indicators per chart,
  so it fits with room to spare. All five confirmations are computed internally, so you do
  not need to spend your remaining slots on RSI, EMA and a volume average.
- All the intervals the free plan gives you are on the ladder. The ones the catalogue
  actually uses are M15, H1, H4, D1 and W1.
- Alerts: create the alert with the condition **"Any alert() function call"**. The message
  carries abbreviation, name, status, score, symbol and time frame. The free plan's alert
  limit applies as usual.
- Only the most recent 500 labels can exist at once — a Pine limit, not a script limit.
  On a long history the oldest labels drop off. Narrowing the filters is the fix.

---

## 8. Honest limitations

- **Reliability percentages are catalogue values, not backtested results.** They come from
  the pattern cards and are used for filtering and display only. Nothing in this repo
  measured them, and you should not treat them as an edge until you have tested them on
  your own pairs and sessions.
- **This is an educational and analysis tool, not a signal service.** It tells you a
  pattern's shape is valid and how much context supports it. It does not know about news,
  sessions, spread or your risk model.
- **Some rules had to be interpreted** to be expressible in OHLC terms. Where a classic
  definition is vague, the script uses an explicit input rather than a hidden constant, so
  you can see and change every threshold. The main interpretations: Three Inside Up/Down
  confirms on a close beyond the inside candle's extreme, Piercing Line accepts an open
  below the previous *close* rather than the previous *low*, and Three White Soldiers /
  Three Black Crows require the prior opposite trend.
- **Pattern quality still depends on location.** A hammer mid-range is noise no matter how
  perfect its geometry. That is exactly what the Location check and the score are for.

---

## 9. Repo layout

```text
pine/candlestick_master_45.pine   the indicator
prompts/MASTER_PROMPT.md          the build prompt + variation prompts
prompts/PATTERN_CARD_TEMPLATE.md  the schema for pasting pattern data
docs/PATTERNS.md                  generated catalogue + time frame gate map
tools/check_pine.py               structural checks on the Pine source
tools/gen_pattern_table.py        regenerates docs/PATTERNS.md from the registry
```

After editing the registry in the `.pine` file:

```bash
python3 tools/check_pine.py
python3 tools/gen_pattern_table.py
```

---

## Disclaimer

Educational tool. Not financial advice and not a trading recommendation. Trading carries
substantial risk of loss. Do your own research.

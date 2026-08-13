# DEFINITION CONVERSIONS

Every place where something vague, unstated, or unmeasurable had to become an explicit rule.

**This file exists so that no engine default is invisible.** If a number appears anywhere in
this project and was not supplied by the owner, it has an ID here, a stated rationale, and an
input that overrides it.

Rules:

* A supplied pattern specification **always overrides** the conversion for its own pattern.
* A conversion is never applied silently — the pattern file that relies on one cites its ID in
  the `conversions:` front-matter field.
* `tools/spec_lint.py` fails if a pattern file cites an ID that does not exist here.
* Changing a default is a documented change to this table, not an edit buried in code.

Total conversions: **65**.

---

## Body and shape — `CV-BODY-*`

| ID | Converts | Explicit rule | Default | Why this value |
| --- | --- | --- | --- | --- |
| `CV-BODY-001` | "doji", "open ≈ close" | `bodyPct <= dojiMaxBody` | `0.10` | An exact `open == close` almost never occurs, so a tolerance is unavoidable; 10% of range is the commonly published figure and is small enough that a doji still looks like one. |
| `CV-BODY-002` | "small body" | `bodyPct <= smallBodyMax` | `0.30` | Leaves a clear band between doji (≤10%) and large (≥60%) so the three classes are visually distinguishable. |
| `CV-BODY-003` | "large body", "strong body" | `bodyPct >= largeBodyMin` | `0.60` | The body dominates the candle without demanding a near-marubozu. |
| `CV-BODY-004` | "marubozu", "no wicks" | `bodyPct >= marubozuMin` | `0.90` | Allows one or two ticks of wick, which real data almost always has. |

## Wicks — `CV-WICK-*`

| ID | Converts | Explicit rule | Default | Why this value |
| --- | --- | --- | --- | --- |
| `CV-WICK-001` | "long wick" as a fraction of the candle | `wickPct >= longWickMin` | `0.60` | Matches the "two-thirds of the candle" idiom while leaving room for a small body plus an opposite wick. |
| `CV-WICK-002` | "long wick" as a multiple of the body | `wick >= longWickBodyMult * body` | `2.0` | The "at least twice the body" idiom, verbatim. Evaluated as a multiplication, never a division (`WICK_BODY_ENGINE.md` §3). |
| `CV-WICK-003` | "short wick", "little or no wick" | `wickPct <= shortWickMax` | `0.10` | Mirror of the doji tolerance, so "no upper wick" and "no body" are equally forgiving. |

## Relative size — `CV-SIZE-*`

| ID | Converts | Explicit rule | Default | Why this value |
| --- | --- | --- | --- | --- |
| `CV-SIZE-001` | "average candle size" | `avgRange20 = ta.sma(range, 20)` | `20` bars | One month of daily bars / one session of hourly bars; long enough to be stable, short enough to track a volatility change. |
| `CV-SIZE-002` | "average body size" | `avgBody20 = ta.sma(body, 20)` | `20` bars | Same period as `CV-SIZE-001` so the two are comparable. |
| `CV-SIZE-003` | "unusually large candle" | `relRange >= 1.5` | `1.5` | Half again the recent average is visible to the eye without being rare. |
| `CV-SIZE-004` | "small candle relative to recent action" | `relRange <= 0.6` | `0.6` | Symmetric-in-spirit counterpart to `1.5`. |
| `CV-SIZE-005` | "a meaningful candle" (one-tick-range guard) | `range >= minRangeTicks * tick` | `2` ticks, **off by default** | Available to patterns whose text implies substance; off by default because enabling it globally would silently change every pattern's hit rate. |
| `CV-SIZE-006` | `relBody` on a near-flat instrument | display clamp `[0, 10]`; logic uses the raw value | — | Prevents a meaningless `4000×` in a tooltip without altering any comparison. |

## Comparison mathematics — `CV-MATH-*`

| ID | Converts | Explicit rule | Default | Why this value |
| --- | --- | --- | --- | --- |
| `CV-MATH-001` | float equality on prices and computed levels | tolerance `eps` ticks; ratio thresholds inclusive | `eps = 0` | Exact by default so behaviour is predictable and reproducible; the input exists for instruments whose computed midpoints fall between valid tick prices. |

## Candle relationships — `CV-REL-*`

| ID | Converts | Explicit rule | Default | Why this value |
| --- | --- | --- | --- | --- |
| `CV-REL-001` | "engulfs" | `bodyTop(a) >= bodyTop(b) and bodyBottom(a) <= bodyBottom(b)` | inclusive, **body** | Opening exactly at the previous close is extremely common on 24-hour instruments; the strict form would reject most real engulfings. Both forms are published (`SI-02`, `SI-03`). |
| `CV-REL-002` | "50%", "the midpoint of the previous candle" | `C > (O1 + C1) / 2` | previous **body** midpoint | The body reading is the one used by the classical piercing/dark-cloud descriptions. Range midpoint is published separately and is a defensible alternative (`SI-01`). |
| `CV-REL-003` | penetration display range | clamp `[-1.0, 2.0]` for display only | — | Keeps a tooltip readable when a close lands far beyond the previous body; logic uses the raw value. |
| `CV-REL-004` | "gap" inside a star-family pattern | `bodyGapUp` / `bodyGapDown` | body gap | Classical star descriptions mean a body gap; wicks routinely overlap in real data. |
| `CV-REL-005` | "gap" elsewhere | `trueGapUp` / `trueGapDown` | true range gap | Outside the star family, "gap" ordinarily means the ranges do not overlap. |
| `CV-REL-006` | "significant gap" | `gapSizeAtr >= gapMinAtr` | `0` | Zero so that no size requirement is invented; the input exists for a spec that supplies one. |

## Trend — `CV-TREND-*`

| ID | Converts | Explicit rule | Default | Why this value |
| --- | --- | --- | --- | --- |
| `CV-TREND-001` | "rising"/"falling" EMA | `slopeN(x) = (x - x[slopeLen]) / atr14` | `slopeLen = 5` | ATR normalisation makes one threshold portable across instruments; 5 bars is short enough to be current, long enough to ignore a single bar. |
| `CV-TREND-002` | "uptrend" | alignment + `slopeN(ema20) >= +0.10` + `close > ema50` | as stated | Three independent conditions, so one alone cannot declare a trend. |
| `CV-TREND-003` | "downtrend" | mirror of `CV-TREND-002` | as stated | Exact mirror, so the two directions are equally hard to satisfy. |
| `CV-TREND-004` | "sideways", "ranging" | `abs(spreadN) < 0.50 and abs(slopeN(ema20)) < 0.10` | as stated | Both compression *and* flatness required; either alone is common mid-trend. |
| `CV-TREND-005` | "trend strength" | `0..3`: alignment + momentum + price position | as stated | A count of named conditions rather than a manufactured percentage. |
| `CV-TREND-006` | **"clear trend"** | `state == direction and trendStrength >= 2` | `>= 2` of 3 | The phrase appears in many specifications and must mean one thing. Two of three conditions is "clear" without demanding perfection. |
| `CV-TREND-007` | "clear trend" reinforced by structure | `and structureState == HH_HL / LH_LL` | **off** | Available, off by default because the pivot confirmation delay would drag every pattern's trend context backwards. |

## Timeframe — `CV-TF-*`

| ID | Converts | Explicit rule | Default | Why this value |
| --- | --- | --- | --- | --- |
| `CV-TF-001` | "ideal timeframe" on a chart timeframe nobody listed | nine classes (`SUB_MINUTE` … `MONTHLY`); `CLASS` mode allows same-class matches | `CLASS` | `EXACT` produces an empty chart on any timeframe the owner did not enumerate, which looks like a broken indicator. All three modes are available (`SI-10`). |

## RSI — `CV-RSI-*`

| ID | Converts | Explicit rule | Default | Why this value |
| --- | --- | --- | --- | --- |
| `CV-RSI-001` | "overbought" / "oversold" / "midline" | `>= 70` / `<= 30` / `50` | as stated | The standard Wilder levels; no case for inventing others. |
| `CV-RSI-002` | which RSI statement to show when several are true | divergence → OB/OS → momentum → neutral | as stated | The most specific true statement wins; showing "bullish" when a divergence exists would discard information. |
| `CV-RSI-003` | "swing high/low" for divergence | `ta.pivothigh/low(5, 5)` | `5 / 5` | Symmetric and short enough that the 5-bar confirmation delay stays tolerable. |
| `CV-RSI-004` | minimum separation of the two pivots | `>= 5` bars | `5` | Closer pivots are noise rather than a swing pair. |
| `CV-RSI-005` | maximum separation of the two pivots | `<= 60` bars | `60` | Beyond this the two lows are not the same swing structure. |
| `CV-RSI-006` | "the divergence is still valid" | active `10` bars after the second pivot's confirmation | `10` | A divergence is a condition, not a permanent state; a bound is required or it never expires. |
| `CV-RSI-007` | how RSI is paired with price for divergence | RSI sampled **at the price pivot** | as stated | The question is "price made a lower low while momentum did not", which is anchored to the price swing. Pivoting both series independently would require an invented pairing rule. |

## EMA — `CV-EMA-*`

| ID | Converts | Explicit rule | Default | Why this value |
| --- | --- | --- | --- | --- |
| `CV-EMA-001` | **"reclaim"** | `close > ema and barssince(crossover) <= reclaimWindow` | `3` bars | A reclaim is an event, not a position. The window makes "reclaiming" a short state rather than a single tick; `0` reduces it to the crossing bar. |
| `CV-EMA-002` | "rejection" | wick through with a close back, **or** a crossunder within the window | as stated | Supplied text uses both idioms. |
| `CV-EMA-003` | which EMA statement to show | event → configuration → position → neutral | as stated | Prevents the weakest statement ("above the 20 EMA") from being dressed up as the strongest. |

## Volume — `CV-VOL-*`

| ID | Converts | Explicit rule | Default | Why this value |
| --- | --- | --- | --- | --- |
| `CV-VOL-001` | "average volume" | `ta.sma(volume, 20)` | `20` bars | Matches the candle-size average period. |
| `CV-VOL-002` | "above average volume" | `volRatio >= 1.20` | `1.20` | A soft statement needs a soft threshold; a bare `> 1.0` fires on half of all bars. |
| `CV-VOL-003` | "volume expansion", "climactic volume" | `volRatio >= 1.50` | `1.50` | A distinctly stronger statement than `CV-VOL-002`, which is why both exist. |
| `CV-VOL-004` | "below average volume", "weak participation" | `volRatio <= 0.80` | `0.80` | Symmetric-in-spirit with `1.20`. |
| `CV-VOL-005` | `volRatio` on a bad print | display clamp `[0, 20]`; logic uses the raw value | — | Keeps the tooltip readable while leaving the anomaly visible. |

## Location — `CV-LOC-*`

| ID | Converts | Explicit rule | Default | Why this value |
| --- | --- | --- | --- | --- |
| `CV-LOC-001` | "at support/resistance" | `abs(low - level) <= atr14 * locTolAtr` | `0.50` ATR | ATR scaling works on any instrument and widens where levels are genuinely fuzzier. |
| `CV-LOC-002` | "demand"/"supply" zone | support/resistance **and** `touches >= 2` | `2` | An area defended more than once. This is a touch count and nothing more — no order-flow claim (`LOCATION_ENGINE.md` §5). |
| `CV-LOC-003` | "the range" | `rangePos` over `highest/lowest(100)` | `100` bars | Enough history to contain a real swing range at any timeframe. |
| `CV-LOC-004` | "near the low/high of the range" | `rangePos <= 0.20` / `>= 0.80` | `0.20 / 0.80` | Bottom and top fifth. |
| `CV-LOC-005` | "mid-range" | `0.40 <= rangePos <= 0.60` | `0.40–0.60` | The middle fifth; the two gaps on either side are deliberately `UNCLEAR` rather than forced. |
| `CV-LOC-006` | **"major support/resistance"** | `touches >= 2` **and** one contributing pivot of length `>= 10` | `2` / `10` | "Major" needs a structural pivot, not a wiggle. One explicit operationalisation of a subjective word. |
| `CV-LOC-007` | how many levels to remember | 20 per side, FIFO | `20` | Spans a long visible history while keeping the per-bar loop at ~40 iterations. |
| `CV-LOC-008` | which location statement to show | demand/supply → support/resistance → swing extreme → mid-range → unclear | as stated | Most specific first; nearest level wins on a collision. |

## Confirmation — `CV-CONF-*`

| ID | Converts | Explicit rule | Default | Why this value |
| --- | --- | --- | --- | --- |
| `CV-CONF-001` | "confirmed by the next candle" | bullish: a closed candle closes above the **pattern** high; bearish: mirror | as stated | Uses the extreme of the whole pattern, captured at detection so the level cannot drift. Close-based, because an intrabar touch is only knowable on a forming bar. |
| `CV-CONF-002` | "the following candles" | window of `3` closed candles | `3` | Long enough for a real follow-through, short enough that a signal does not stay open indefinitely (`SI-09`). |
| `CV-CONF-003` | trigger and invalidation on the same candle | **`FAILED` wins** | as stated | Conservative, and it removes a dependency on evaluation order. |
| `CV-CONF-004` | pending queue capacity | 60 records, oldest dropped and **counted** | `60` | Bounds the per-bar loop; overflow is surfaced in the panel rather than hidden. |

## Validation — `CV-VAL-*`

| ID | Converts | Explicit rule | Default | Why this value |
| --- | --- | --- | --- | --- |
| `CV-VAL-001` | "do not make a pattern strong just because more boxes were checked" | contradiction caps (1 opposing → `MODERATE`, ≥2 → `WEAK`), no double counting, unconfirmed ceiling, exclusion is neutral | as stated | Counting only agreement would rate a bullish pattern in a strong downtrend the same as one in a neutral market. |
| `CV-VAL-002` | scoring a pattern with no direction | directional factors excluded until the breakout resolves direction; `maxScore = 2` before, `6` after | as stated | Directional factors cannot be for or against a pattern that has no side. |

## Display — `CV-DISP-*`

| ID | Converts | Explicit rule | Default | Why this value |
| --- | --- | --- | --- | --- |
| `CV-DISP-001` | where the label goes | bullish below, bearish above, neutral above | as stated | Keeps the label out of the direction the pattern implies. |
| `CV-DISP-002` | label appearance | colour by direction, size/opacity by validation band | as stated | Strength readable at a glance without adding chart text. |
| `CV-DISP-003` | showing status on the chart | optional one-character mark (`✓ ✗ ·`), **off** | off | `BEC CONFIRMED` on every signal recreates the clutter the abbreviation rule exists to prevent. |
| `CV-DISP-004` | structural detail in the tooltip | a `── Structure ──` block after the six factors | on | Makes a detection auditable: the numbers that satisfied the rules are visible. |
| `CV-DISP-005` | the info panel | one table, last bar only, with timeframe/warm-up/filter/event diagnostics | on | Answers "why is nothing showing?" without guesswork. |
| `CV-DISP-006` | several patterns on one bar | ATR-fraction vertical offsets, max 4 per side, then `+n` | `4` | Prevents a pattern-dense bar from consuming the 500-label budget. |

## Filters and alerts — `CV-FILT-*`, `CV-ALERT-*`

| ID | Converts | Explicit rule | Default | Why this value |
| --- | --- | --- | --- | --- |
| `CV-FILT-001` | which category a filter matches | **primary** category; an input widens it to secondary categories | primary, widening off | Predictable: `REVERSAL ONLY` shows patterns whose primary category is reversal, so the same pattern set appears every time. |
| `CV-ALERT-001` | how alerts are exposed | `alert()` per pattern-state + 9 aggregate `alertcondition` series | as stated | ~150 individual `alertcondition`s (3 states × 50+ patterns) would bloat the compiled script and make the alert dialog unusable. |

---

## Index by owner phrase

The phrases most likely to appear in a supplied specification, and where each one lands:

| Phrase in a specification | Conversion |
| --- | --- |
| "long lower wick" / "long shadow" | `CV-WICK-001` or `CV-WICK-002` — **the spec must say which** (`SI-05`) |
| "small real body" | `CV-BODY-002` |
| "no upper wick" | `CV-WICK-003` |
| "doji" | `CV-BODY-001` |
| "engulfs the previous candle" | `CV-REL-001` |
| "closes above the midpoint" / "more than 50%" | `CV-REL-002` |
| "gaps above" | `CV-REL-004` / `CV-REL-005` |
| "clear downtrend" / "established uptrend" | `CV-TREND-006` |
| "sideways" / "choppy" | `CV-TREND-004` |
| "ideal on H1, H4, D1" | `CV-TF-001` |
| "oversold" | `CV-RSI-001` |
| "bullish divergence" | `CV-RSI-003` … `CV-RSI-007` |
| "reclaims the 20 EMA" | `CV-EMA-001` |
| "rejected at the EMA" | `CV-EMA-002` |
| "above average volume" | `CV-VOL-002` |
| "volume expansion" / "climactic volume" | `CV-VOL-003` |
| "at support" | `CV-LOC-001` |
| "major support" | `CV-LOC-006` |
| "in a demand zone" | `CV-LOC-002` |
| "confirmed by the next candle" | `CV-CONF-001` |
| "within a few candles" | `CV-CONF-002` |
| "high reliability" | **no conversion** — stored as a supplied label, excluded from all maths (`MASTER_SPECIFICATION.md` §14) |
| "±72% accuracy" | **no conversion** — stored verbatim as `User-provided reference` |
| "institutional buying" / "smart money" | **no conversion** — not observable; preserved verbatim with an `AUDIT FLAG` |

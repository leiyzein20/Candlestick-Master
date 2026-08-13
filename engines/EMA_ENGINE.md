# EMA ENGINE (L3)

EMA context. The engine's central discipline: **being above an EMA is not a reclaim.**

---

## 1. Purpose

Publish the EMA set and the relations pattern validation needs — alignment, side, reclaim,
rejection, slope — with a reclaim that requires an actual transition.

## 2. Contract

**Inputs:** `close`, `high`, `low`, `atr14`, `bar_index`, `reclaimWindow`.

**Outputs:**

| Output | Type | Meaning |
| --- | --- | --- |
| `ema20`, `ema50`, `ema200` | float | the EMA set `[OWNER]` |
| `aboveEma20/50/200` | bool | `close > ema` |
| `belowEma20/50/200` | bool | `close < ema` |
| `alignBull`, `alignBear` | bool | `ema20 > ema50 > ema200` / mirror |
| `reclaim20/50/200` | bool | §4 |
| `reject20/50/200` | bool | §5 |
| `emaSlopeN20/50/200` | float | ATR-normalised slope |
| `emaState` | int enum | §6 |
| `emaText` | string | the exact tooltip string |
| `ema200Ready` | bool | `bar_index >= 200` |

## 3. Side — the weakest statement

```
aboveEma20 = close > ema20
```

This is reported as `EMA: Above 20 EMA` / `EMA: Below 20 EMA`. It is a position, not an
event, and it is the *lowest*-ranked EMA statement (§6). In a long uptrend, "above the 20
EMA" is true on most bars and therefore carries little information — which is exactly why it
must not be dressed up as something stronger.

## 4. Reclaim — requires a crossing

```
reclaim(e) = close > e and ta.barssince(ta.crossover(close, e)) <= reclaimWindow
```

`reclaimWindow` default `3` closed bars `[ENGINE-DEFAULT]` `CV-EMA-001`.

Two conditions, both required: the close is **now** above the EMA, **and** the crossing
happened on this bar or within the last `reclaimWindow` closed bars.

| Situation | `aboveEma20` | `reclaim20` |
| --- | --- | --- |
| 40 bars into an uptrend, price well above the 20 EMA | `true` | **`false`** |
| price closed below the 20 EMA yesterday, closes above it today | `true` | **`true`** |
| price crossed up 3 bars ago and is still above | `true` | `true` (at the window edge) |
| price crossed up 8 bars ago and is still above | `true` | `false` (window expired) |
| price crossed up today then closed back below | `false` | `false` |

The mirror, `reclaimDown(e)`, uses `ta.crossunder` for bearish patterns, so
"reclaiming the 20 EMA" has a bearish counterpart ("losing the 20 EMA") with identical
strictness.

Rationale for the window rather than "crossed on this bar": a supplied specification saying
"price reclaims the 20 EMA" describes a short state, not a single tick. Three bars is a
documented default, and it is an input. A window of `0` would reduce it to the exact crossing
bar, which is available by setting the input.

## 5. Rejection

```
reject(e) = (high > e and close < e)
         or (close < e and ta.barssince(ta.crossunder(close, e)) <= reclaimWindow)
```

Two forms, because supplied text uses both: an intrabar test that failed to hold (the wick
pierced the EMA, the close did not), and a recent loss of the level.

`[ENGINE-DEFAULT]` `CV-EMA-002`. The mirror for bullish rejection of resistance uses `low < e
and close > e`.

## 6. State precedence

One state per bar `[ENGINE-DEFAULT]` `CV-EMA-003`, strongest statement first:

| # | State | Condition | Tooltip string |
| --- | --- | --- | --- |
| 1 | `RECLAIM_20` | `reclaim20` | `EMA: Reclaiming 20 EMA ✓` |
| 1 | `LOSE_20` | `reclaimDown20` | `EMA: Losing 20 EMA` |
| 2 | `REJECT_20` | `reject20` | `EMA: Rejected at 20 EMA` |
| 3 | `ALIGN_BULL` | `alignBull` | `EMA: Bullish alignment ✓` |
| 3 | `ALIGN_BEAR` | `alignBear` | `EMA: Bearish alignment ✓` |
| 4 | `ABOVE_20` | `aboveEma20` | `EMA: Above 20 EMA` |
| 4 | `BELOW_20` | `belowEma20` | `EMA: Below 20 EMA` |
| 5 | `EMA_NEUTRAL` | anything else | `EMA: Neutral` |

An event (reclaim / rejection) outranks a configuration (alignment), which outranks a
position (side). The 20 EMA is the reference for events because it is the EMA the owner's
examples name; events on the 50 and 200 are computed and available to any pattern that asks
for them by name.

## 7. Slope

```
emaSlopeN(e) = (e - e[5]) / atr14
```

Same normalisation as [`TREND_ENGINE.md`](TREND_ENGINE.md) §3, so a slope threshold means
the same thing in both engines. Published for pattern rules that reference EMA direction;
not part of `emaState`.

## 8. Warm-up

| EMA | Bars needed | Behaviour before |
| --- | --- | --- |
| `ema20` | 20 | `na`; EMA factor excluded from scoring |
| `ema50` | 50 | `na`; alignment unavailable |
| `ema200` | 200 | `na`; `ema200Ready = false`, trend engine goes relaxed |

Pine returns an EMA value earlier than its length, seeded from the first bars. That value is
not the EMA it claims to be, so the engine gates on `bar_index` explicitly rather than
trusting a non-`na` return. While a required EMA is unavailable the factor is **excluded**
from the confluence maximum, never scored as a failure
([`VALIDATION_ENGINE.md`](VALIDATION_ENGINE.md)).

## 9. What the engine will not claim

* No "EMA support/resistance" statement — an EMA is not a level in the sense
  [`LOCATION_ENGINE.md`](LOCATION_ENGINE.md) uses, and merging the two would double-count one
  piece of evidence in the score (`MASTER_SPECIFICATION.md` §9.1 rule 2).
* No golden/death-cross narrative. `alignBull` / `alignBear` describe the configuration and
  stop there.
* No claim that a reclaim predicts anything.

## 10. Cost

| Item | Count |
| --- | --- |
| `ta.*` calls | 3 EMAs + up to 6 cross/barssince pairs, all shared |
| Per-bar work | ~20 comparisons |
| Arrays / drawings | 0 |

`ta.crossover` / `ta.crossunder` / `ta.barssince` are computed at fixed call sites for the
three EMAs. Patterns never call them.

## 11. Tests

[`../tests/EMA_TESTS.md`](../tests/EMA_TESTS.md), vectors `tests/vectors/ema.json`:

* the §4 table asserted row by row — especially "40 bars above the EMA" must yield
  `reclaim20 == false`;
* window boundary: crossing exactly `reclaimWindow` bars ago is a reclaim; one bar older is
  not;
* a cross up followed by a close back below → not a reclaim;
* rejection: wick through the EMA with a close below → `REJECT_20`; wick and close both above
  → not a rejection;
* precedence: a bar that is simultaneously reclaiming and bullish-aligned reports the
  reclaim;
* warm-up: `ema200` unavailable before bar 200 → factor excluded, trend relaxed;
* slope sign and magnitude against a hand-computed series.

## 12. Open questions for supplied specifications

| # | Question | Until answered |
| --- | --- | --- |
| 1 | Is a 3-bar reclaim window right, or should "reclaim" mean the crossing bar only? | 3 bars (`CV-EMA-001`), input |
| 2 | Which EMA is the reference for per-pattern reclaim rules — always 20? | 20 for the state string; 50/200 available per pattern |
| 3 | Should EMA alignment require the 200, or is 20>50 enough? | 200 required in full mode; 20>50 in relaxed mode only |
| 4 | Any pattern where EMA is **mandatory** rather than confluence? | none assumed |

# EMA TESTS

Covers [`engines/EMA_ENGINE.md`](../engines/EMA_ENGINE.md).

```bash
python3 tools/run_tests.py ema_reclaim -v
```

The property this suite exists to defend: **being above an EMA is not a reclaim.**

---

## 1. A long trend produces no reclaims

Fixture: 80 bars rising steadily, price above its 20 EMA for the entire second half.

| Check | Expected |
| --- | --- |
| price above the 20 EMA on bars 40–79 | `true` (fixture sanity — the test must not pass by accident) |
| reclaims reported on bars 40–79 | **zero** |

Both rows are needed. Without the first, a fixture that drifted below the EMA would report no
reclaims for the wrong reason and the test would pass vacuously.

## 2. A genuine reclaim, and its window

Fixture: 40 flat bars, a 15-bar decline that closes below the 20 EMA, then a sharp recovery
that closes back above it.

| Bar | Expected |
| --- | --- |
| the crossing bar `x` | reclaim **true** |
| `x + 1` | true (inside the 3-bar window) |
| `x + 2` | true |
| `x + 3` | true (window edge, inclusive) |
| `x + 4` | **false** — the window expired, even though price is still above the EMA |

`x + 4` is the assertion that separates a reclaim from a position. Price is above the EMA on
that bar, and the answer is still `false`.

## 3. Cases that must NOT be a reclaim

| Case | Expected |
| --- | --- |
| above the EMA for 40 consecutive bars | not a reclaim |
| crossed up intrabar but closed back below | not a reclaim (close-based) |
| crossed up 8 bars ago, still above | not a reclaim (window expired) |
| above the EMA from the first bar, never having been below | not a reclaim (no crossing) |

The last row is the warm-up trap: on a chart whose first bars open above the EMA, there is no
crossover, so `barssince(crossover)` has no event to measure. The implementation must treat
"no crossing has ever happened" as *not a reclaim*, not as "crossed infinitely long ago" and
certainly not as `na` leaking into a boolean.

## 4. EMA implementation

`ema()` in the reference model reproduces `ta.ema()`: an SMA seed at bar `length - 1`, then
`alpha = 2 / (length + 1)` recursion. `None` before the seed.

| Check | Expected |
| --- | --- |
| bars 0 … `length - 2` | `None` |
| bar `length - 1` | equals the SMA of the first `length` values |
| a constant series | the EMA equals the constant |

## 5. Warm-up and availability

| EMA | Bars needed | Behaviour before |
| --- | --- | --- |
| 20 | 20 | EMA factor **excluded** from `maxScore`, never scored as a failure |
| 50 | 50 | alignment unavailable |
| 200 | 200 | `ema200Ready == false`; the trend engine switches to relaxed mode and the tooltip says `(relaxed)` |

Pine will return a 200-EMA value from 30 bars of history. It is not a 200-period EMA, so the
implementation must gate on `bar_index >= 200` rather than on the value being non-`na`. This is
a manual check (M5) because it depends on Pine's seeding behaviour, not on arithmetic.

## 6. To add when specifications arrive

* Per-pattern reclaim rules that name the 50 or 200 EMA instead of the 20.
* Rejection cases: wick through the EMA with a close back below (`REJECT_20`), versus wick and
  close both above (not a rejection).
* State precedence: a bar that is simultaneously reclaiming and bullish-aligned must report the
  reclaim, since an event outranks a configuration.
* Slope sign and magnitude against a hand-computed series, once a pattern references EMA
  direction.

## 7. Manual checks (TradingView only)

| # | Check | Expected |
| --- | --- | --- |
| M1 | compare all three EMAs against TradingView's built-in EMA | identical |
| M2 | a strong trend far above the 20 EMA | tooltip says `EMA: Above 20 EMA`, never `Reclaiming` |
| M3 | the bar that crosses back above the 20 EMA | tooltip says `EMA: Reclaiming 20 EMA ✓` |
| M4 | four bars after that crossing | back to `Above 20 EMA` |
| M5 | a symbol with fewer than 200 bars of history | `(relaxed)` in the trend string, EMA factor excluded, no runtime error |
| M6 | a wick piercing the 20 EMA with a close below | `EMA: Rejected at 20 EMA` |

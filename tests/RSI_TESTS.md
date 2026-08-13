# RSI TESTS

Covers [`engines/RSI_ENGINE.md`](../engines/RSI_ENGINE.md).

```bash
python3 tools/run_tests.py rsi_trend rsi_divergence rsi_gaps -v
```

The two properties this suite exists to defend:

1. **`rsi > 50` is momentum, never divergence.**
2. **A divergence is not usable before its second pivot is confirmed.**

---

## 1. Momentum is not divergence

Fixture: a monotonically rising close series, 120 bars.

| Check | Expected |
| --- | --- |
| bullish divergences found | **zero** |
| RSI state at bar 100 | `BULL_MOM` or `OVERBOUGHT` — never `BULL_DIV` |

A rising market with rising RSI is the single most common situation in which a sloppy
implementation reports "bullish divergence ✓" and inflates every confluence score. The suite
fails if any divergence is detected in a series that contains no lower low at all.

## 2. State precedence

From [`RSI_ENGINE.md` §4](../engines/RSI_ENGINE.md):

| Input | Expected state | String |
| --- | --- | --- |
| `rsi = 25`, bull divergence active | `BULL_DIV` | `RSI: Bullish divergence ✓` |
| `rsi = 25`, no divergence | `OVERSOLD` | `RSI: Oversold ✓` |
| `rsi = 60` rising, no divergence | `BULL_MOM` | `RSI: Bullish` |
| `rsi = 48` flat | `NEUTRAL` | `RSI: Neutral` |
| `rsi = None` (warm-up) | `UNAVAILABLE` | `RSI: n/a (warming up)` |

Divergence outranking oversold is asserted directly: the same RSI value of 25 must report
divergence when one is active and oversold when none is.

## 3. Divergence and its confirmation delay

Fixture (`ANCHORS_BULL_DIV` in `tools/run_tests.py`), 160 bars: a steep decline into a pivot
low at **bar 40**, a bounce, then a slower decline into a marginally lower pivot low at
**bar 90**. The slower second decline leaves RSI higher at the second low — a textbook bullish
divergence, built by construction rather than found by search.

Structural assertions:

| Check | Expected |
| --- | --- |
| divergence detected | yes, `kind == BULL` |
| price made a lower low | `price(90) < price(40)` |
| RSI made a higher low | `rsi(90) > rsi(40)` |
| second pivot's confirmation bar | `90 + 5 = 95` |
| `active_from` | `95` — equal to the confirmation bar |

Timing assertions, one per bar — this is the no-repaint rule:

| Bar | Divergence active? |
| --- | --- |
| 90 (the pivot itself) | **no** |
| 91 | **no** |
| 92 | **no** |
| 93 | **no** |
| 94 | **no** |
| 95 (confirmation) | **yes** |
| 105 (`active_from + 10`) | yes — the last active bar |
| 106 | **no** — the window expired |

The five "no" rows are the whole point. On bar 90 the low exists on the chart and a human eye
can see it, but five later bars have not yet printed, so it is not yet a pivot. Any
implementation that reported divergence on bar 90 would be reading the future on history and
would behave differently live.

## 4. Pivot separation limits

Same fixture, whose pivots are 50 bars apart:

| Configuration | Expected |
| --- | --- |
| defaults (`min 5`, `max 60`) | divergence accepted |
| `min_gap = 51` | divergence **rejected** |
| `max_gap = 49` | divergence **rejected** |

Bracketing the fixture's actual separation from both sides proves the limits are enforced,
rather than merely present in the configuration.

## 5. RSI implementation

`rsi_wilder()` in the reference model reproduces `ta.rsi()`: a simple average seed over the
first `length` differences, then Wilder smoothing. `None` before the seed completes.

| Check | Expected |
| --- | --- |
| bars 0–13 | `None` |
| bar 14 | first value |
| all-gains series | `100.0` |
| all-losses series | `0.0` |

## 6. To add when specifications arrive

* Any pattern that names its own RSI levels, tested at those levels.
* A bearish-divergence fixture mirroring §3, if a supplied pattern requires one.
* Interaction: a divergence active *at the same bar* a pattern fires, verifying the RSI factor
  scores `+1` and the tooltip string is exactly `RSI: Bullish divergence ✓`.

## 7. Manual checks (TradingView only)

| # | Check | Expected |
| --- | --- | --- |
| M1 | compare the plotted RSI with a standard RSI(14) indicator | identical values |
| M2 | scroll history: does a divergence label ever appear earlier than 5 bars after its pivot? | never |
| M3 | watch a forming bar that would become a pivot | no divergence claimed until the bar closes and 5 more print |
| M4 | reload the chart after a live divergence appears | the same bar still shows it — no back-dating, no disappearance |
| M5 | first 14 bars of a fresh symbol | `RSI: n/a (warming up)` and RSI excluded from `maxScore` |

M4 is the definitive repaint test: a signal that survives a reload at the same bar was real at
that bar.

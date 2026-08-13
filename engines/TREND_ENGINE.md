# TREND ENGINE (L3)

One trend definition for the whole system. Objective, ATR-normalised, and explicit about
what "clear trend" means.

---

## 1. Purpose

Answer one question per bar — `UPTREND`, `DOWNTREND`, `SIDEWAYS`, or `UNCLEAR` — plus a
strength number, so that pattern specifications saying "in a downtrend" or "in a clear
downtrend" resolve to a single measurable rule instead of a per-pattern opinion.

## 2. Contract

**Inputs:** `ema20`, `ema50`, `ema200`, `atr14`, `close`, confirmed pivots from
[`LOCATION_ENGINE.md`](LOCATION_ENGINE.md), `bar_index`.

**Outputs:**

| Output | Type | Values |
| --- | --- | --- |
| `trendState` | int enum | `UPTREND` / `DOWNTREND` / `SIDEWAYS` / `UNCLEAR` |
| `trendStrength` | int | `0..3` |
| `trendRelaxed` | bool | true while `ema200` is unavailable |
| `structureState` | int enum | `HH_HL` / `LH_LL` / `MIXED` / `UNKNOWN` |
| `isClearUptrend` / `isClearDowntrend` | bool | §5 |
| `trendText` | string | e.g. `Downtrend ✓`, `Sideways`, `Uptrend (relaxed)` |

## 3. Normalisation — why ATR

A raw EMA slope is in price units, so a threshold like "slope > 0.5" means something
different on EURUSD (0.5 ≈ 5000 pips) than on BTC (0.5 ≈ nothing). Every measure is
therefore divided by `atr14`, making thresholds dimensionless and portable across
instruments and timeframes.

```
slopeN(x) = (x - x[slopeLen]) / atr14        slopeLen = 5   [ENGINE-DEFAULT] CV-TREND-001
spreadN   = (ema20 - ema50) / atr14
extN      = (close - ema20) / atr14                          -- extension from the mean
```

`slopeN` reads as "how many ATRs the EMA moved over the last `slopeLen` bars".

## 4. States

Full mode (at least 200 bars of history):

| State | Rule | ID |
| --- | --- | --- |
| `UPTREND` | `ema20 > ema50 and ema50 > ema200 and slopeN(ema20) >= +0.10 and close > ema50` | `CV-TREND-002` |
| `DOWNTREND` | `ema20 < ema50 and ema50 < ema200 and slopeN(ema20) <= -0.10 and close < ema50` | `CV-TREND-003` |
| `SIDEWAYS` | `abs(spreadN) < 0.50 and abs(slopeN(ema20)) < 0.10` | `CV-TREND-004` |
| `UNCLEAR` | anything else | `[DERIVED]` |

Evaluation order is `UPTREND` → `DOWNTREND` → `SIDEWAYS` → `UNCLEAR`; the trend rules are
mutually exclusive by construction (alignment cannot be both ways), and `SIDEWAYS` is tested
only after both directional rules fail, so no bar can match two states.

`UNCLEAR` is a real answer, not a failure. It covers the genuinely common case of EMAs
crossing, a strong move against an old alignment, or a transition — and it is the honest
label for it. The alternative, forcing every bar into a direction, would make the trend
factor meaningless.

**Strength** `[ENGINE-DEFAULT]` `CV-TREND-005`, `0..3`:

| +1 for | Condition |
| --- | --- |
| alignment | `ema20 > ema50 > ema200` (or the mirror) |
| momentum | `abs(slopeN(ema20))` beyond the `0.10` threshold |
| price position | close on the trend side of **both** `ema20` and `ema50` |

## 5. "Clear trend" — the conversion

Pattern specifications routinely say "clear downtrend". That phrase is converted once, here,
and every pattern that uses it cites the ID `[ENGINE-DEFAULT]` `CV-TREND-006`:

```
isClearDowntrend = trendState == DOWNTREND and trendStrength >= 2
isClearUptrend   = trendState == UPTREND   and trendStrength >= 2
```

Optional reinforcement, off by default `CV-TREND-007`:
`and structureState == LH_LL` (respectively `HH_HL`).

Recorded honestly: this is an operational definition of a subjective phrase. It is not
claimed to be *the* definition, it is claimed to be *explicit, measurable, and consistently
applied* — which is what the phrase needs in order to be implementable at all. Any supplied
specification that defines "clear" numerically overrides it for its own pattern.

## 6. Swing structure

From confirmed pivots only (`pivotLen = 5`, so a pivot is knowable `5` bars after it forms):

```
structureState = HH_HL   when lastPH > prevPH and lastPL > prevPL
               = LH_LL   when lastPH < prevPH and lastPL < prevPL
               = MIXED   when two pivots of each type exist but disagree
               = UNKNOWN before two of each exist
```

Structure is deliberately **secondary**: it is available to patterns and to the optional
reinforcement in §5, but it does not define `trendState` on its own, because it lags by the
pivot confirmation delay and would drag every pattern's trend context backwards with it
([`../ARCHITECTURE.md`](../ARCHITECTURE.md) §5).

## 7. Insufficient history — relaxed mode

`ema200` requires 200 bars. Before that, the alignment term is undefined.

```
trendFullReady = bar_index >= 200
```

While false, **relaxed mode** applies `[DERIVED]`:

| Term | Relaxed substitute |
| --- | --- |
| alignment | `ema20 > ema50` only |
| slope | `slopeN(ema50) >= 0.05` (a slower EMA needs a lower bar) |
| price position | unchanged (`close` vs `ema50`) |

`trendRelaxed` is set, `trendText` gains the suffix `(relaxed)`, and the info panel shows
`trend: relaxed (bar n/200)`. The EMA confluence factor is **excluded** from scoring while
relaxed rather than scored as a pass or a fail
([`VALIDATION_ENGINE.md`](VALIDATION_ENGINE.md)).

Alternative rejected: computing `ema200` from whatever history exists. Pine will happily
return a value from 30 bars, but a 200-period EMA seeded on 30 bars is not a 200-period EMA,
and using it would produce confident-looking trend labels on nonsense.

## 8. What the engine will not claim

* No trend *forecast*. The state describes bars that have closed.
* No "trend strength percentage" — strength is a `0..3` count of three named conditions, and
  the tooltip shows the count, not a manufactured percent.
* No hidden regime model, no ADX substitute, no volatility filter beyond the ATR
  normalisation itself.
* No claim that EMA alignment causes anything. It is a description of the moving-average
  configuration, chosen because it is reproducible.

## 9. Cost

| Item | Count |
| --- | --- |
| `ta.*` calls | 4, shared (`ema20/50/200`, `atr14`) + pivots shared with location |
| Per-bar arithmetic | ~15 |
| Arrays / drawings | 0 |

## 10. Tests

[`../tests/OHLC_TESTS.md`](../tests/OHLC_TESTS.md) covers arithmetic;
trend-specific cases live in `tests/vectors/trend.json` and
[`../tests/PATTERN_TESTS.md`](../tests/PATTERN_TESTS.md):

* synthetic rising / falling / flat series → expected state and strength;
* a series that alternates so no state holds → `UNCLEAR`, asserting `UNCLEAR` is reachable;
* boundary slopes at exactly `±0.10` (inclusive, so `0.10` counts as trending);
* `spreadN` at exactly `0.50`;
* bars 1–199 → `trendRelaxed == true`, and the relaxed rules produce the documented state;
* bar 200 → the state may legitimately change on that bar; the change is expected and is
  not a repaint (no historical bar is rewritten);
* pivot-based `structureState` never uses a pivot before its confirmation bar.

## 11. Open questions for supplied specifications

| # | Question | Until answered |
| --- | --- | --- |
| 1 | Is the EMA set (20/50/200) the intended trend basis for every pattern? | yes, per the owner's engine list |
| 2 | Does "clear trend" mean strength ≥ 2, or should swing structure be mandatory? | strength ≥ 2, structure optional (`CV-TREND-006/007`) |
| 3 | Should `SIDEWAYS` block reversal patterns, or only score 0? | score 0, never block, unless a spec makes the trend mandatory |
| 4 | Is a `slopeLen` of 5 bars appropriate on daily and weekly charts? | 5 bars on all timeframes; single input if it needs to differ |

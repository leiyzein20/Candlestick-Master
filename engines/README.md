# ENGINES

One specification per engine. Each file has the same shape:

1. **Purpose** — the one job the engine owns.
2. **Contract** — inputs, outputs, and the exact type of every value it publishes.
3. **Rules** — the arithmetic, with provenance markers and conversion IDs.
4. **Edge cases** — degenerate data, insufficient history, `na` policy.
5. **Cost** — what it adds to the per-bar budget.
6. **Tests** — which vectors and which manual checks cover it.
7. **Open questions** — what a supplied specification still has to settle.

Precedence: a supplied pattern specification overrides
[`../MASTER_SPECIFICATION.md`](../MASTER_SPECIFICATION.md), which overrides these files.
An engine never introduces a rule that the master specification does not have.

| Engine | Layer | Owns |
| --- | --- | --- |
| [`OHLC_ENGINE.md`](OHLC_ENGINE.md) | L1 | primitives: range, body, wicks, ratios, close position, colour, degeneracy |
| [`WICK_BODY_ENGINE.md`](WICK_BODY_ENGINE.md) | L1 | shape classification built on those primitives |
| [`RELATIONSHIP_ENGINE.md`](RELATIONSHIP_ENGINE.md) | L2 | candle-to-candle maths for offsets 1–5: engulfment, containment, 50% rules, penetration, gaps |
| [`TREND_ENGINE.md`](TREND_ENGINE.md) | L3 | trend state, strength, swing structure, "clear trend" |
| [`TIMEFRAME_ENGINE.md`](TIMEFRAME_ENGINE.md) | L5 | canonical timeframes, classes, enforcement modes, test mode |
| [`RSI_ENGINE.md`](RSI_ENGINE.md) | L3 | RSI state and pivot-based divergence with honest delay |
| [`EMA_ENGINE.md`](EMA_ENGINE.md) | L3 | EMA set, alignment, reclaim vs rejection vs merely-above |
| [`VOLUME_ENGINE.md`](VOLUME_ENGINE.md) | L3 | volume ratio, thresholds, and data-source honesty |
| [`LOCATION_ENGINE.md`](LOCATION_ENGINE.md) | L3 | support/resistance/demand/supply/range position from confirmed pivots |
| [`CONFIRMATION_ENGINE.md`](CONFIRMATION_ENGINE.md) | L7 | DETECTED → CONFIRMED / FAILED / EXPIRED on closed candles |
| [`VALIDATION_ENGINE.md`](VALIDATION_ENGINE.md) | L6 | confluence scoring, bands, anti-inflation rules |
| [`DISPLAY_ENGINE.md`](DISPLAY_ENGINE.md) | L8 | labels, tooltips, info panel, alert payloads |

`RELATIONSHIP_ENGINE.md` is the twelfth file in a list of eleven requested engines. It exists
because the previous-candle relationship calculations are a separate requirement in their own
right, and folding them into `OHLC_ENGINE.md` would put single-candle and multi-candle
mathematics in one file — the two things patterns most often need to cite separately.

## Shared values computed once per bar

Declared here so no engine and no pattern recomputes them
([`../ARCHITECTURE.md`](../ARCHITECTURE.md) A2). This list is the complete set of `ta.*`
call sites in the future script.

| Value | Source | Consumers |
| --- | --- | --- |
| `atr14` | `ta.atr(14)` | trend, location, relationship (gap size), display |
| `ema20`, `ema50`, `ema200` | `ta.ema` ×3 | trend, EMA |
| `rsi14` | `ta.rsi(close, 14)` | RSI |
| `volAvg20` | `ta.sma(volume, 20)` | volume |
| `avgRange20`, `avgBody20` | `ta.sma` ×2 | wick/body classes, display |
| `pivotHigh`, `pivotLow` | `ta.pivothigh/low(5, 5)` | RSI divergence, location, trend structure |
| `hh100`, `ll100` | `ta.highest/lowest(100)` | location range position |
| `crossUp20/50/200`, `crossDn20/50/200` | `ta.crossover/crossunder` + `ta.barssince` | EMA reclaim/rejection |

Total: ~18 `ta.*` call sites, fixed, independent of pattern count.

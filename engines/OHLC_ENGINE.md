# OHLC ENGINE (L1)

The one place candle primitives are computed. Every other engine and every pattern reads
from here. Duplicating any formula below inside a pattern is a review failure
([`../ARCHITECTURE.md`](../ARCHITECTURE.md) A3).

---

## 1. Purpose

Turn four numbers — open, high, low, close — into the complete set of derived measurements
the rest of the system needs, for any candle offset, with defined behaviour on degenerate
data.

## 2. Contract

**Inputs:** `open`, `high`, `low`, `close` at offset `n` (`n = 0..5`), `syminfo.mintick`.
**Reads no indicator, no context, no user input** other than the comparison tolerance.

**Outputs** (all available per offset):

| Name | Type | Range | Definition |
| --- | --- | --- | --- |
| `range(n)` | float | ≥ 0 | `H - L` |
| `body(n)` | float | ≥ 0 | `abs(C - O)` |
| `upperWick(n)` | float | ≥ 0 | `H - max(O, C)` |
| `lowerWick(n)` | float | ≥ 0 | `min(O, C) - L` |
| `bodyTop(n)` | float | — | `max(O, C)` |
| `bodyBottom(n)` | float | — | `min(O, C)` |
| `bodyPct(n)` | float | 0..1 | `body / range` |
| `upperWickPct(n)` | float | 0..1 | `upperWick / range` |
| `lowerWickPct(n)` | float | 0..1 | `lowerWick / range` |
| `closePos(n)` | float | 0..1 | `(C - L) / range` |
| `openPos(n)` | float | 0..1 | `(O - L) / range` |
| `candleMid(n)` | float | — | `(H + L) / 2` |
| `bodyMid(n)` | float | — | `(O + C) / 2` |
| `isBull(n)` | bool | — | `C > O` |
| `isBear(n)` | bool | — | `C < O` |
| `isFlat(n)` | bool | — | `C == O` |
| `isMeasurable(n)` | bool | — | `range > 0` |

All primitive formulas are `[OWNER]`-supplied. Derived positions are `[DERIVED]`.

## 3. Identities that must hold

Used as assertions in the reference model and as invariants in review:

```
range        == body + upperWick + lowerWick
bodyPct      == 1 - upperWickPct - lowerWickPct
bodyTop      - bodyBottom == body
closePos     == 1 - (H - C) / range
isBull XOR isBear XOR isFlat            (exactly one is true)
0 <= bodyPct, upperWickPct, lowerWickPct, closePos, openPos <= 1
candleMid    == bodyMid  only when  O + C == H + L   (not generally true)
```

The last line is the guard against the single most common candlestick coding error:
treating the candle midpoint and the body midpoint as the same value. They are separate
outputs with separate names and are never substituted for one another
([`../docs/GLOSSARY.md`](../docs/GLOSSARY.md)).

## 4. Colour policy

```
isBull = C > O ,  isBear = C < O ,  isFlat = C == O
```

`isFlat` is **not** bullish and **not** bearish. A pattern requiring "a bullish candle"
fails on a flat candle. Only an explicit supplied rule ("open and close may be equal")
changes that, per pattern, and it is recorded in the pattern file.

Rationale: a flat close is a real market state (no net change over the bar), and silently
folding it into one side would make one pattern in a mirrored pair strictly easier to
trigger than the other.

## 5. Degenerate candles — `range == 0`

Happens on illiquid instruments, halted sessions, and synthetic/backfilled data: all four
prices identical.

Every ratio would divide by zero. Policy `[DERIVED]`:

| Value | When `range == 0` |
| --- | --- |
| `isMeasurable` | `false` |
| `bodyPct`, `upperWickPct`, `lowerWickPct` | `0` |
| `closePos`, `openPos` | `0.5` |
| `candleMid`, `bodyMid` | the single price |
| every pattern using this candle | **returns false** |

Two reasons for defining constants instead of `na`:

1. Pine v6 keeps `na` inside `bool`, and an `na` boolean propagating into a pattern
   condition produces neither `true` nor `false` in a predictable way. Fixed numbers plus an
   explicit `isMeasurable` flag keep every boolean well-defined
   ([`../MASTER_SPECIFICATION.md`](../MASTER_SPECIFICATION.md) §13).
2. `0.5` for `closePos` is the honest answer: on a zero-range candle the close is
   simultaneously at the high and the low. It is never *used*, because `isMeasurable`
   gates the pattern first, but it must not be a number that accidentally satisfies a rule
   like "closes in the upper third".

**Rule: every pattern's structure test includes `isMeasurable` for every candle it reads.**
This is a checklist item in `tests/OHLC_TESTS.md`, not a convention.

## 6. Near-zero range

A range that is tiny but non-zero (one tick) is measurable but produces jumpy ratios: a
one-tick body in a one-tick range is `bodyPct == 1.0`, technically a marubozu.

Optional guard `[ENGINE-DEFAULT]` `CV-SIZE-005`: `isSignificantRange = range >= minRangeTicks * tick`,
default `minRangeTicks = 2`. It is **not** applied automatically — it is available to
patterns whose supplied text implies a meaningful candle, and its use is recorded per
pattern. Left off by default because silently ignoring one-tick candles would be an
undocumented change to every pattern's hit rate.

## 7. Float comparison

Per `MASTER_SPECIFICATION.md` §3.6: raw price order comparisons as-is; comparisons against
computed levels use `eps` ticks (default `0`); ratio thresholds are inclusive.

The tolerance exists for instruments where a computed midpoint falls between two valid
tick prices, so an "equal to the midpoint" close can never be represented exactly. Default
`0` keeps behaviour exact unless the owner opts in.

## 8. History depth

Offsets `0..5` are published `[OWNER]`. Nothing in the engine reads deeper, which keeps
`max_bars_back` at its default and avoids the "requested too many bars back" error class.

If a supplied pattern needs candle 6 or beyond, the depth constant is raised once, in one
place, and the change is noted here.

## 9. Cost

| Item | Count |
| --- | --- |
| `ta.*` calls | 0 |
| Arithmetic ops per bar | ~40 (offset 0) + on-demand history reads |
| Arrays / labels / lines | 0 |

Offsets 1–5 use Pine's built-in history operator rather than stored copies, so extra
offsets cost nothing structurally.

## 10. Tests

Covered by [`../tests/OHLC_TESTS.md`](../tests/OHLC_TESTS.md) and the vectors in
`tests/vectors/ohlc_engine.json`, executed with `python3 tools/run_tests.py`:

* every identity in §3, on random and hand-built candles;
* all four colour cases including flat;
* zero range, one-tick range, body-only (no wicks), wick-only (doji), extreme asymmetry;
* boundary ratios at exactly `0.10`, `0.30`, `0.60`, `0.90`;
* `closePos` at `0`, `0.5`, `1`.

## 11. Open questions for supplied specifications

| # | Question | Until answered |
| --- | --- | --- |
| 1 | Is a flat candle (`C == O`) ever acceptable where a coloured candle is required? | treated as failing (`SI-12`) |
| 2 | Should one-tick-range candles be excluded globally? | not excluded (`CV-SIZE-005` available, off) |
| 3 | Any instrument-specific tick tolerance wanted? | `eps = 0`, exact comparisons |

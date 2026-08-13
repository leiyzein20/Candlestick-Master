# WICK / BODY ENGINE (L1)

Shape classification. Consumes only [`OHLC_ENGINE.md`](OHLC_ENGINE.md) outputs; produces
the vocabulary that pattern specifications use ("small body", "long lower wick",
"marubozu").

---

## 1. Purpose

Give every vague size word exactly one measurable meaning, in one place, so that fifty
pattern files cannot drift into fifty slightly different definitions of "long wick".

## 2. Contract

**Inputs:** `bodyPct(n)`, `upperWickPct(n)`, `lowerWickPct(n)`, `body(n)`, `range(n)`,
`avgRange20`, `avgBody20`, `isMeasurable(n)`, plus the thresholds in §3.

**Outputs:** booleans per offset, and the two relative-size floats.

| Output | Rule | Default | ID |
| --- | --- | --- | --- |
| `isDojiBody(n)` | `bodyPct <= dojiMaxBody` | `0.10` | `CV-BODY-001` |
| `isSmallBody(n)` | `bodyPct <= smallBodyMax` | `0.30` | `CV-BODY-002` |
| `isLargeBody(n)` | `bodyPct >= largeBodyMin` | `0.60` | `CV-BODY-003` |
| `isMarubozu(n)` | `bodyPct >= marubozuMin` | `0.90` | `CV-BODY-004` |
| `isLongUpperWickR(n)` | `upperWickPct >= longWickMin` | `0.60` | `CV-WICK-001` |
| `isLongLowerWickR(n)` | `lowerWickPct >= longWickMin` | `0.60` | `CV-WICK-001` |
| `isLongUpperWickB(n)` | `upperWick >= longWickBodyMult * body` | `2.0` | `CV-WICK-002` |
| `isLongLowerWickB(n)` | `lowerWick >= longWickBodyMult * body` | `2.0` | `CV-WICK-002` |
| `isShortUpperWick(n)` | `upperWickPct <= shortWickMax` | `0.10` | `CV-WICK-003` |
| `isShortLowerWick(n)` | `lowerWickPct <= shortWickMax` | `0.10` | `CV-WICK-003` |
| `relRange(n)` | `range / avgRange20` | — | `CV-SIZE-001` |
| `relBody(n)` | `body / avgBody20` | — | `CV-SIZE-002` |
| `isLargeCandle(n)` | `relRange >= 1.5` | `1.5` | `CV-SIZE-003` |
| `isSmallCandle(n)` | `relRange <= 0.6` | `0.6` | `CV-SIZE-004` |

Every threshold is an input. Every default is `[ENGINE-DEFAULT]` and listed in
[`../docs/DEFINITION_CONVERSIONS.md`](../docs/DEFINITION_CONVERSIONS.md).

## 3. Why two definitions of "long wick"

Supplied specifications use two incompatible idioms:

| Idiom | Measure | Suffix |
| --- | --- | --- |
| "the wick is at least twice the body" | multiple of **body** | `...WickB` |
| "the wick is two-thirds of the candle" | fraction of **range** | `...WickR` |

They disagree in practice. A candle with `body = 0.30`, `lowerWick = 0.65`,
`upperWick = 0.05` of range satisfies both. A candle with `body = 0.05`,
`lowerWick = 0.45`, `upperWick = 0.50` satisfies the *body-multiple* test (0.45 ≥ 2×0.05)
but fails the *range-fraction* test (0.45 < 0.60) — and visually it is a spinning top, not
a hammer.

So the engine publishes both, and a pattern must state which it means. If the supplied text
does not say, the ambiguity is logged (`SI-05`) rather than resolved by preference.

**The body-multiple form has a divide-by-zero-shaped trap.** With `body == 0` (a perfect
doji) any non-zero wick is "infinitely" larger than the body, so `wick >= 2 * body` is
trivially true. The engine therefore evaluates it as a multiplication, never a division,
and patterns that use it and mean a *directional* candle must also require a non-doji body.
This is a checklist item at intake, not a hidden guard: silently adding "and body > 0" to a
supplied rule would be modifying the rule.

## 4. Ratio boundaries are inclusive

A specification saying "body no more than 10% of the range" becomes `bodyPct <= 0.10`, so a
candle at exactly 10.0% qualifies. "Body greater than 60%" becomes `bodyPct >= 0.60`.

The direction of the inclusivity is recorded per pattern, because the boundary case is
exactly what a test vector will probe, and two reviewers reading "10%" can otherwise
disagree about a candle sitting on the line.

## 5. Class overlaps are intentional

`isDojiBody` ⊂ `isSmallBody` at the defaults (`0.10 < 0.30`), and `isMarubozu` ⊂
`isLargeBody`. The classes are **not** partitioned, and no code assumes exclusivity. A
pattern needing "small but not a doji" writes both conditions explicitly.

## 6. Relative size and the 20-bar warm-up

`avgRange20` / `avgBody20` need 20 bars. Before that they are `na` and every
`relRange` / `relBody` comparison would be undefined.

Policy `[DERIVED]`: `sizeContextReady = bar_index >= 20`. While it is false, patterns that
depend on relative size **do not fire**, and the info panel shows `warming up (n/20)`. They
are not silently allowed through on absolute ratios, because that would make the first 20
bars of every chart behave differently from the rest.

`avgBody20` can legitimately be near zero on a flat instrument, which makes `relBody`
explode. `relBody` is therefore clamped to `[0, 10]` for **display**, and comparisons use
the raw value `[ENGINE-DEFAULT]` `CV-SIZE-006`.

## 7. What this engine deliberately does not do

* No "hammer-ness" score, no composite shape metric. Patterns compose booleans; a fuzzy
  score would make a structure test partially true, which
  [`../MASTER_SPECIFICATION.md`](../MASTER_SPECIFICATION.md) §1.1 forbids.
* No comparison against other candles — that is
  [`RELATIONSHIP_ENGINE.md`](RELATIONSHIP_ENGINE.md).
* No trend or volatility judgement beyond `relRange` / `relBody`.

## 8. Cost

| Item | Count |
| --- | --- |
| `ta.*` calls | 2 (`avgRange20`, `avgBody20`), shared |
| Booleans per offset | 10 |
| Arrays / drawings | 0 |

## 9. Tests

[`../tests/OHLC_TESTS.md`](../tests/OHLC_TESTS.md), vectors `tests/vectors/wick_body.json`:

* each class exactly at, one tick above, and one tick below its threshold;
* the two long-wick definitions on candles where they disagree (the §3 example is a vector);
* `body == 0` against the body-multiple test, asserting the trap is visible;
* overlap assertions: every doji is a small body, every marubozu is a large body;
* warm-up: bars 1–19 must not satisfy any relative-size class.

## 10. Open questions for supplied specifications

| # | Question | Until answered |
| --- | --- | --- |
| 1 | Per-pattern: is "long wick" measured against range or body? | logged as `AM-`, `SI-05` |
| 2 | Are the default class cut-offs (`0.10 / 0.30 / 0.60 / 0.90`) acceptable, or does each pattern carry its own? | defaults used, cited by `CV-` ID |
| 3 | Should "long" be relative to recent candles (`relRange`) rather than to its own range? | own range; `relRange` available |

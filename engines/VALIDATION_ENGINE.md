# VALIDATION / CONFLUENCE ENGINE (L6)

Turns context into one band: `WEAK`, `MODERATE`, `STRONG`, `VERY STRONG`. Its hardest job is
**not** rewarding a pattern for having many boxes ticked.

---

## 1. Purpose

Score agreement between a valid pattern structure and its context, transparently enough that
a tooltip can show exactly why a band was reached.

## 2. Structure is not a factor

An invalid structure is not reported at all, so "Pattern: Valid ✓" is a **precondition**, not
a point. It appears in the tooltip because the owner's format includes it, but it contributes
nothing to the score — otherwise every signal would start with a free point and the bands
would compress.

## 3. Factors

Six, each `+1`, `0`, or **excluded** `[OWNER]` list:

| Factor | `+1` when | `0` when | Excluded when |
| --- | --- | --- | --- |
| Trend | `trendState` matches the pattern's `reqTrend` | it does not | the pattern requires no particular trend |
| Location | bullish: `AT_SUPPORT`/`AT_DEMAND`/`SWING_LOW`; bearish: `AT_RESISTANCE`/`AT_SUPPLY`/`SWING_HIGH` | any other defined state | `locState == UNCLEAR`, or fewer than two confirmed pivots |
| RSI | divergence in the pattern's direction, or `OVERSOLD` for bullish / `OVERBOUGHT` for bearish | any other state | RSI warming up |
| EMA | reclaim or alignment in the pattern's direction | side-only, neutral, or opposing | required EMA not yet available |
| Volume | `ABOVE` or `HIGH` | `NORMAL` or `BELOW` | no volume series, or warming up |
| Confirmation | status is `CONFIRMED` | `DETECTED`, `EXPIRED`, or `FAILED` | never excluded |

Each factor consumes an engine's published state — it does not re-derive anything.

## 4. Score, maximum, and bands

```
score    = sum of factor points          0 .. maxScore
maxScore = 6 - (number of excluded factors)
ratio    = score / maxScore
```

Bands on the **ratio**:

| Band | Ratio | At `maxScore = 6` | At `maxScore = 5` | At `maxScore = 4` |
| --- | --- | --- | --- | --- |
| `WEAK` | `<= 0.3333` | 0–2 | 0–1 | 0–1 |
| `MODERATE` | `<= 0.5000` | 3 | 2 | 2 |
| `STRONG` | `<= 0.8333` | 4–5 | 3–4 | 3 |
| `VERY STRONG` | `> 0.8333` | 6 | 5 | 4 |

The `maxScore = 6` column **is** the owner's specification (0–2 WEAK, 3 MODERATE, 4–5 STRONG,
6+ VERY STRONG) `[OWNER]`. Everything else is the same table with a smaller denominator.

Why ratios rather than absolute counts: on an index with no volume data, `maxScore` is 5. With
absolute bands, such a chart could never reach `VERY STRONG` and would systematically read
weaker than a stock chart for identical price action. The ratio keeps the bands meaning the
same thing when a factor is genuinely unmeasurable.

Band edges are inputs, expressed as ratios.

## 5. Anti-inflation rules `[ENGINE-DEFAULT]` `CV-VAL-001`

The owner's constraint — *do not make a pattern "strong" simply because more boxes were
checked* — implemented as four concrete rules:

### 5.1 Contradiction cap

Counting only agreement makes a bullish pattern in a strong downtrend look identical to one in
a neutral market: both score `0` for trend. But those are not the same situation.

```
opposingFactors = count of factors that actively contradict the pattern's direction
```

A factor *contradicts* when it takes a defined state pointing the other way: a bullish pattern
with `trendState == DOWNTREND and trendStrength >= 2`, or `locState == AT_RESISTANCE`, or a
bearish RSI divergence, or a bearish EMA state.

| `opposingFactors` | Cap |
| --- | --- |
| 1 | band capped at `MODERATE` |
| ≥ 2 | band capped at `WEAK` |

The cap is displayed: `Validation: MODERATE (capped: trend opposes)`. A cap is applied *after*
the band is computed, and it can only lower it.

### 5.2 No double counting

One piece of evidence, one point:

* RSI divergence **and** RSI oversold → one RSI point;
* EMA reclaim **and** EMA bullish alignment → one EMA point;
* `AT_SUPPORT` **and** `SWING_LOW` → one location point;
* EMA proximity is **not** also a location point — the EMA engine deliberately publishes no
  support/resistance statement ([`EMA_ENGINE.md`](EMA_ENGINE.md) §9).

### 5.3 Unconfirmed ceiling

A pattern still at `DETECTED` cannot be `VERY STRONG`. `VERY STRONG` requires the confirmation
factor, so the top band always means "and it actually followed through".

Worth recording honestly: with the current factor set this ceiling is **already implied by the
arithmetic**. Confirmation is never excluded, so `ratio > 0.8333` forces `score == maxScore`,
which forces every measurable factor — including confirmation — to have passed. The explicit
rule is kept as a guard against a future change to the band edges or to factor weights that
would break that coincidence, and the test suite asserts it directly rather than relying on the
arithmetic holding.

### 5.4 Exclusion is neutral

An excluded factor lowers `maxScore` and is printed as `n/a` with its reason. It is never a
pass and never a fail. Absent data must not create a signal quality it cannot support, in
either direction.

## 6. Mandatory factors

If a supplied specification explicitly says a contextual factor is required, it becomes a
**precondition** for that pattern (`MASTER_SPECIFICATION.md` §1.1): failing it suppresses the
pattern entirely rather than lowering its score. Passing it still scores `+1`, because a
genuine confluence is still a confluence.

Set only from explicit words ("only valid in a downtrend", "must occur at support",
"requires volume expansion"). Softer wording ("works best with", "ideally", "preferably") is
confluence, not a gate, and the distinction is recorded per pattern.

## 7. Neutral patterns

A neutral pattern has no direction, so the four directional factors (trend, location, RSI, EMA)
cannot be evaluated for or against it. Before resolution they are **excluded**, leaving
`maxScore = 2` (volume + confirmation) `[ENGINE-DEFAULT]` `CV-VAL-002`.

Once the confirmation engine resolves a direction by breakout
([`CONFIRMATION_ENGINE.md`](CONFIRMATION_ENGINE.md) §4), the directional factors are evaluated
against the *resolved* direction and `maxScore` returns to 6. The tooltip states which case
applies.

## 8. What the score is not

* Not a probability. Not a win rate. Not an expectancy. Nothing in this engine has been
  validated against outcomes, and no supplied statistic enters it
  (`MASTER_SPECIFICATION.md` §14).
* Not a ranking across patterns. Two `STRONG` signals from different patterns are not
  comparable in strength.
* Not risk sizing.

It is a count of how many named, independently defined conditions agreed — nothing more, and
the tooltip shows every one of them so the count can be checked by eye.

## 9. Worked examples

Using the owner's example, `maxScore = 6`:

| Factors | Score | Ratio | Band |
| --- | --- | --- | --- |
| trend ✓, location ✓, RSI div ✓, EMA reclaim ✓, volume ✓, confirmed ✓ | 6 | 1.00 | `VERY STRONG` |
| trend ✓, location ✓, RSI div ✓, EMA reclaim ✓, volume ✓, not yet confirmed | 5 | 0.83 | `STRONG` |
| trend ✓, location ✓, RSI **neutral**, EMA reclaim ✓, volume ✓, not confirmed | 4 | 0.67 | `STRONG` |
| trend ✓, location ✓, RSI neutral, EMA side-only, volume normal, not confirmed | 2 | 0.33 | `WEAK` |
| as above but on an index with no volume (`maxScore = 5`) | 2 | 0.40 | `MODERATE` |
| bullish pattern, trend `DOWNTREND` strength 3, location `AT_RESISTANCE`, others ✓ | 4 | 0.67 | `STRONG` → **capped `WEAK`** (2 opposing) |

Row 3 reproduces the owner's second example — RSI neutral, everything else present — landing
`STRONG` at 4/6. Row 4 reproduces the shape of a low-confluence signal. Row 6 is why §5.1
exists.

## 10. Cost

| Item | Count |
| --- | --- |
| `ta.*` calls | 0 |
| Per-bar work | ~12 comparisons per emitted pattern (only for patterns that fired) |
| Arrays / drawings | 0 |

Scoring runs only for a pattern that detected or resolved on this bar, not for all 50+ every
bar.

## 11. Tests

Vectors `tests/vectors/validation.json`, plus
[`../tests/PATTERN_TESTS.md`](../tests/PATTERN_TESTS.md):

* every row of §9 asserted exactly;
* band boundaries at ratio `0.3333`, `0.5000`, `0.8333` (inclusive upper edges);
* `maxScore` 6, 5, 4 with the same factor pattern → documented band shifts;
* double-counting cases produce one point, not two;
* an unconfirmed pattern with everything else ✓ cannot reach `VERY STRONG`;
* one opposing factor caps at `MODERATE`, two cap at `WEAK`, and the cap text appears;
* a neutral pattern before resolution has `maxScore == 2`, and 6 after resolution;
* a mandatory failing factor suppresses the pattern entirely rather than scoring it.

## 12. Open questions for supplied specifications

| # | Question | Until answered |
| --- | --- | --- |
| 1 | Are the six factors the intended set? | yes, per the owner's list |
| 2 | Should confirmation be a scoring factor or a separate axis? | scoring factor, with the §5.3 ceiling |
| 3 | Are contradiction caps wanted, or should opposing context only score 0? | caps applied (`CV-VAL-001`), switchable |
| 4 | Should factors be weighted (e.g. trend worth 2)? | equal weights; weighting was not specified |

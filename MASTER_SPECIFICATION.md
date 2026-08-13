# MASTER SPECIFICATION

**Normative document.** Where this file and any other file disagree, this file wins —
except for supplied pattern specifications, which always win over this file for their own
pattern (see §1.3).

Every threshold below is a **default with an input**, and every default is tagged with a
provenance marker:

| Marker | Meaning |
| --- | --- |
| `[OWNER]` | Supplied by the project owner. Never changed without instruction. |
| `[DERIVED]` | Forced by arithmetic or by an `[OWNER]` rule. Not a judgement call. |
| `[ENGINE-DEFAULT]` | Chosen by the engine because a measurable value was required and none was supplied. Every one of these is listed in [`docs/DEFINITION_CONVERSIONS.md`](docs/DEFINITION_CONVERSIONS.md) with an ID, and is overridable by a later `[OWNER]` value. |

Nothing in this file is a claim about market behaviour. See §14.

---

## 1. Governing principles

### 1.1 Structure is separate from context

Two independent questions, answered in order and never merged:

1. **Structure** — does the OHLC geometry satisfy the pattern definition? Inputs: open,
   high, low, close of the pattern's candles, and nothing else. Output: `true` / `false`.
2. **Context** — trend, location, RSI, EMA, volume. Inputs: the context engines. Output: a
   confluence score and a validation band.

A structurally valid pattern in poor context is **valid and WEAK**, never invalid.

The single exception: if a supplied specification states that a contextual factor is
**mandatory** ("only valid in a downtrend", "must occur at support", "requires volume
expansion"), that factor is promoted into a structural precondition for that pattern only,
recorded in its spec file as `MANDATORY CONTEXT`, and listed in the registry. This never
happens by inference — only from explicit words in the supplied specification.

### 1.2 Preservation of supplied specifications

* Supplied text is stored **verbatim** in the pattern file's *As Supplied* block.
* Machine rules are written **beside** it, never over it.
* Anything vague is converted to an explicit measurable rule, and the conversion is
  recorded with an ID in [`docs/DEFINITION_CONVERSIONS.md`](docs/DEFINITION_CONVERSIONS.md).
* Anything contradictory or missing is raised in [`CONFLICT_LOG.md`](CONFLICT_LOG.md) and
  the pattern is held at status `BLOCKED`. It is not guessed.
* Anything that appears technically incorrect keeps its original wording and receives an
  adjacent `AUDIT FLAG:` note. No silent correction.
* Two similarly named patterns are treated as two independent patterns with independent
  rules. Nothing is shared by name similarity.

### 1.3 Precedence order

```
supplied pattern specification
        ↓  overrides
MASTER_SPECIFICATION.md  (this file)
        ↓  overrides
engines/*.md
        ↓  overrides
implementation
```

An implementation detail may never introduce a rule absent from the layer above it.

---

## 2. Notation

For the candle at offset `n` (0 = current):

| Symbol | Meaning |
| --- | --- |
| `O`, `H`, `L`, `C` | open, high, low, close of the current candle |
| `O1`, `H1`, `L1`, `C1` | the previous candle (offset 1); likewise `O2..O5` etc. |
| `tick` | `syminfo.mintick` — the instrument's minimum price increment |
| `eps` | comparison tolerance in ticks, `[ENGINE-DEFAULT] 0` (see §3.6) |
| `ATR` | `ta.atr(14)` `[ENGINE-DEFAULT]` — the single volatility unit used repo-wide |

Ratios are unitless fractions in `0..1`. Percentages in tooltips are those fractions
×100, rounded to 1 decimal `[DERIVED]`.

---

## 3. Candle measurement (L1)

Full detail: [`engines/OHLC_ENGINE.md`](engines/OHLC_ENGINE.md),
[`engines/WICK_BODY_ENGINE.md`](engines/WICK_BODY_ENGINE.md).

### 3.1 Primitives `[OWNER]`

```
range        = H - L
body         = abs(C - O)
upperWick    = H - max(O, C)
lowerWick    = min(O, C) - L
bodyPct      = body      / range
upperWickPct = upperWick / range
lowerWickPct = lowerWick / range
closePos     = (C - L)   / range
```

### 3.2 Derived positions `[DERIVED]`

```
bodyTop      = max(O, C)
bodyBottom   = min(O, C)
openPos      = (O - L) / range
candleMid    = (H + L) / 2          -- midpoint of the RANGE
bodyMid      = (O + C) / 2          -- midpoint of the BODY
wickTotalPct = upperWickPct + lowerWickPct        = 1 - bodyPct
```

`candleMid` and `bodyMid` are **different values** and are never used
interchangeably. See §4.3 and [`docs/GLOSSARY.md`](docs/GLOSSARY.md).

### 3.3 Colour `[OWNER]`

```
isBull  = C > O
isBear  = C < O
isFlat  = C == O            -- a four-price / flat-close candle
```

`isFlat` is neither bullish nor bearish. A pattern requiring a coloured candle fails on a
flat candle unless its specification says otherwise.

### 3.4 Size and shape classes `[ENGINE-DEFAULT]`

Placeholders until each pattern's supplied specification states its own numbers. Any
pattern that supplies its own threshold uses **its own**, not these.

| Class | Rule | Default | Conversion ID |
| --- | --- | --- | --- |
| Doji body | `bodyPct <= dojiMaxBody` | `0.10` | `CV-BODY-001` |
| Small body | `bodyPct <= smallBodyMax` | `0.30` | `CV-BODY-002` |
| Large body | `bodyPct >= largeBodyMin` | `0.60` | `CV-BODY-003` |
| Long wick (of range) | `wickPct >= longWickMin` | `0.60` | `CV-WICK-001` |
| Long wick (of body) | `wick >= longWickBodyMult * body` | `2.0` | `CV-WICK-002` |
| Short wick (of range) | `wickPct <= shortWickMax` | `0.10` | `CV-WICK-003` |
| Marubozu | `bodyPct >= marubozuMin` | `0.90` | `CV-BODY-004` |

Relative-to-recent size, for "long"/"unusually large" wording:

```
avgRange = ta.sma(range, 20)      [ENGINE-DEFAULT]  CV-SIZE-001
avgBody  = ta.sma(body,  20)      [ENGINE-DEFAULT]  CV-SIZE-002
relRange = range / avgRange
relBody  = body  / avgBody
isLargeCandle = relRange >= 1.5   [ENGINE-DEFAULT]  CV-SIZE-003
isSmallCandle = relRange <= 0.6   [ENGINE-DEFAULT]  CV-SIZE-004
```

Both wick classes are provided because supplied specs use both idioms ("wick at least
twice the body" vs "wick is two-thirds of the candle"). A pattern must state which one it
means; if it does not, the ambiguity is logged, not guessed.

### 3.5 Degenerate candles `[DERIVED]`

`range == 0` (all four prices equal) makes every ratio a division by zero.

```
isMeasurable = range > 0
```

When `isMeasurable` is false: all `*Pct` values are defined as `0`, `closePos` as `0.5`,
and **every pattern returns false**. No `na` is allowed to propagate into a boolean, and no
pattern may be satisfied by a zero-range bar. Rationale in
[`engines/OHLC_ENGINE.md` §5](engines/OHLC_ENGINE.md).

### 3.6 Float comparison policy `[ENGINE-DEFAULT]` `CV-MATH-001`

Prices are floats; `==` on computed prices is unreliable.

* Order comparisons (`>`, `<`, `>=`, `<=`) on **raw prices** are used as-is.
* Comparisons against a **computed level** (a midpoint, a penetration threshold) use a
  tolerance of `eps` ticks, default `0` — i.e. exact by default, with an input to loosen it
  for instruments with coarse ticks.
* Equality between two prices means `abs(a - b) <= eps * tick`.
* Ratio comparisons are inclusive at the boundary (`>=` / `<=`) so that a stated threshold
  value counts as satisfying it. A spec saying "body less than 10% of range" is encoded as
  `bodyPct <= 0.10`, and the inclusivity is noted in the pattern file.

---

## 4. Candle-to-candle relationships (L2)

Full detail: [`engines/RELATIONSHIP_ENGINE.md`](engines/RELATIONSHIP_ENGINE.md).
Available for offsets 1..5 `[OWNER]`.

### 4.1 Engulfment `[OWNER]`

```
bodyEngulfsPrev   = bodyTop >= bodyTop1  and bodyBottom <= bodyBottom1
bodyEngulfsStrict = bodyTop >  bodyTop1  and bodyBottom <  bodyBottom1
rangeEngulfsPrev  = H >= H1 and L <= L1          -- "wick engulfment"
rangeEngulfsStrict= H >  H1 and L <  L1
```

`bodyEngulfsPrev` vs `bodyEngulfsStrict` matters when the two candles share an
open/close. Each pattern must state which it requires; the default when a spec says only
"engulfs" is the **inclusive body** form, logged as `CV-REL-001`.

### 4.2 Containment `[DERIVED]`

```
bodyInsidePrevBody = bodyTop <= bodyTop1 and bodyBottom >= bodyBottom1   -- harami
rangeInsidePrev    = H <= H1 and L >= L1                                 -- inside bar
```

### 4.3 The 50% rules `[OWNER]`

Three genuinely different statements exist in candlestick literature. All three are
implemented and never conflated:

```
closeAbovePrevBodyMid  = C > (O1 + C1) / 2      -- 50% of previous BODY
closeAbovePrevRangeMid = C > (H1 + L1) / 2      -- 50% of previous RANGE
closeAbovePrevBodyPct(p) = C > bodyBottom1 + p * (bodyTop1 - bodyBottom1)
```

plus the mirrored `...Below...` forms.

**Default when a spec says "closes above the 50% level" without qualifying it:**
previous **body** midpoint `[ENGINE-DEFAULT]` `CV-REL-002`. The pattern file records which
form was used and flags the ambiguity.

### 4.4 Penetration percentage `[OWNER]`

How deep the current body closes into the previous body, as a fraction of the previous
body:

```
-- bullish penetration of a previous bearish candle (O1 > C1)
penetrationUp   = (C - C1) / (O1 - C1)

-- bearish penetration of a previous bullish candle (C1 > O1)
penetrationDown = (O1 - C) / (O1 - C1)   ... expressed as (C1 - C) / (C1 - O1)
```

Undefined when the previous body is zero (`O1 == C1`); then penetration is `na` and any
pattern requiring it returns false `[DERIVED]`. Reported values are clamped to
`[-1.0, 2.0]` for display only, never for logic `[ENGINE-DEFAULT]` `CV-REL-003`.

### 4.5 Gaps `[OWNER]`

```
trueGapUp    = L > H1          -- ranges do not overlap at all
trueGapDown  = H < L1
bodyGapUp    = bodyBottom > bodyTop1     -- bodies do not overlap; wicks may
bodyGapDown  = bodyTop < bodyBottom1
gapUpSize    = L - H1
gapUpSizeAtr = (L - H1) / ATR
```

24-hour instruments (crypto, spot FX) rarely produce `trueGap*` on intraday timeframes;
star-family patterns in the literature usually mean `bodyGap*`. Which one a pattern
requires must come from its specification. The engine default for the unqualified word
"gap" in a *star* context is `bodyGap*` `[ENGINE-DEFAULT]` `CV-REL-004`; elsewhere it is
`trueGap*` `CV-REL-005`. Every use is recorded per pattern.

A minimum gap size may be required per pattern: `gapMinAtr`, default `0`
`[ENGINE-DEFAULT]` `CV-REL-006`.

### 4.6 Open/close relations `[OWNER]`

```
openAbovePrevClose, openBelowPrevClose
openAbovePrevOpen,  openBelowPrevOpen
closeAbovePrevHigh, closeBelowPrevLow
closeAbovePrevClose,closeBelowPrevClose
higherHigh = H > H1 ,  lowerLow = L < L1
```

---

## 5. Trend context (L3)

Full detail + all thresholds: [`engines/TREND_ENGINE.md`](engines/TREND_ENGINE.md).

States: `UPTREND`, `DOWNTREND`, `SIDEWAYS`, `UNCLEAR` `[OWNER]`.

ATR-normalised measures, so thresholds are instrument-independent:

```
slopeN(x)  = (x - x[slopeLen]) / ATR        slopeLen = 5   [ENGINE-DEFAULT] CV-TREND-001
spreadN    = (ema20 - ema50) / ATR
alignBull  = ema20 > ema50 and ema50 > ema200
alignBear  = ema20 < ema50 and ema50 < ema200
```

| State | Rule (full mode, ≥200 bars) | ID |
| --- | --- | --- |
| `UPTREND` | `alignBull and slopeN(ema20) >= +0.10 and C > ema50` | `CV-TREND-002` |
| `DOWNTREND` | `alignBear and slopeN(ema20) <= -0.10 and C < ema50` | `CV-TREND-003` |
| `SIDEWAYS` | `abs(spreadN) < 0.50 and abs(slopeN(ema20)) < 0.10` | `CV-TREND-004` |
| `UNCLEAR` | anything else | `[DERIVED]` |

`trendStrength` ∈ `0..3` `[ENGINE-DEFAULT]` `CV-TREND-005`: +1 EMA alignment, +1 slope
beyond threshold, +1 price on the correct side of both `ema20` and `ema50`.

**"Clear downtrend" → measurable** `[ENGINE-DEFAULT]` `CV-TREND-006`:
`state == DOWNTREND and trendStrength >= 2`. Optionally reinforced by swing structure
(`lowerHighs and lowerLows` from confirmed pivots). The same, mirrored, for "clear
uptrend". Every supplied spec that uses this phrase points at this ID.

Before 200 bars exist, `ema200` is unusable, so a documented **relaxed mode** applies
(`ema20`/`ema50` only) and the tooltip appends `(relaxed)` `[DERIVED]`.

---

## 6. Timeframe policy (L5)

Full detail: [`engines/TIMEFRAME_ENGINE.md`](engines/TIMEFRAME_ENGINE.md).

Every pattern carries **all** of its ideal timeframes — never a chosen subset. A pattern
listing H1/H4/D1 must work on all three `[OWNER]`.

Chart timeframe is reduced to minutes via `timeframe.in_seconds() / 60` and matched
against the pattern's list. Canonical tokens and their minute values:

| Token | Min | Token | Min | Token | Min |
| --- | --- | --- | --- | --- | --- |
| `1m` | 1 | `45m` | 45 | `8H` | 480 |
| `2m` | 2 | `1H` | 60 | `12H` | 720 |
| `3m` | 3 | `2H` | 120 | `1D` | 1440 |
| `5m` | 5 | `3H` | 180 | `1W` | 10080 |
| `10m` | 10 | `4H` | 240 | `1M` | 43200 |
| `15m` | 15 | `6H` | 360 | | |
| `30m` | 30 | | | | |

Sub-minute (seconds/ticks) and non-listed values (e.g. `7m`, `2D`) are handled by class
matching, never by rejection-through-omission.

Three enforcement modes `[OWNER]` + `[ENGINE-DEFAULT]` classes:

| Mode | Behaviour |
| --- | --- |
| `OFF` | timeframe never hides a pattern |
| `CLASS` *(default)* | allowed if the chart timeframe falls in the same **class** as any listed timeframe — so a 3H chart accepts an H1/H4-listed pattern, a 45m chart accepts a 15m/30m-listed one |
| `EXACT` | allowed only on the exact listed minute values |

Classes `[ENGINE-DEFAULT]` `CV-TF-001`: `SUB_MINUTE (<1)`, `MIN_FAST (1–3)`,
`MIN_MID (5–10)`, `MIN_SLOW (15–45)`, `HOUR_LOW (60–180)`, `HOUR_HIGH (240–720)`,
`DAILY (1440)`, `WEEKLY (10080)`, `MONTHLY (≥43200)`.

`TEST MODE` `[OWNER]` overrides all of the above and additionally relaxes context gating,
so a pattern can be verified in isolation. It is visibly announced in the info panel and
in every tooltip produced while it is on.

---

## 7. Context engines (L3) — summary of outputs

Each engine returns a small enum plus a display string. Full rules in the engine files.

### 7.1 RSI — [`engines/RSI_ENGINE.md`](engines/RSI_ENGINE.md)

`ta.rsi(close, 14)` `[OWNER]`; overbought `70`, oversold `30` `[ENGINE-DEFAULT]`
`CV-RSI-001`.

States, in strict precedence order `[ENGINE-DEFAULT]` `CV-RSI-002`:

```
1  BULLISH_DIVERGENCE / BEARISH_DIVERGENCE   (pivot-based, §7.1.1)
2  OVERSOLD (rsi <= 30) / OVERBOUGHT (rsi >= 70)
3  BULLISH_MOMENTUM (rsi > 50 and rsi > rsi[1]) / BEARISH_MOMENTUM (rsi < 50 and rsi < rsi[1])
4  NEUTRAL
```

Tooltip strings, exactly: `RSI: Bullish divergence ✓`, `RSI: Oversold ✓`, `RSI: Bullish`,
`RSI: Neutral`, `RSI: Bearish divergence`, `RSI: Overbought`.

**`RSI > 50` is momentum, never divergence.** The two are separate states with separate
strings, and no code path may label one as the other.

#### 7.1.1 Divergence `[OWNER]` structure, `[ENGINE-DEFAULT]` parameters

Requires two **confirmed** pivots:

```
bullish divergence: pivotLow[k].price < pivotLow[k-1].price
                and rsiAt(pivotLow[k])  > rsiAt(pivotLow[k-1])
bearish divergence: pivotHigh[k].price > pivotHigh[k-1].price
                and rsiAt(pivotHigh[k]) < rsiAt(pivotHigh[k-1])
```

| Parameter | Default | ID |
| --- | --- | --- |
| pivot left/right length | `5 / 5` | `CV-RSI-003` |
| min bars between the two pivots | `5` | `CV-RSI-004` |
| max bars between the two pivots | `60` | `CV-RSI-005` |
| bars the divergence stays "active" after confirmation | `10` | `CV-RSI-006` |

A pivot is usable only from bar `pivotBar + right`. A divergence is therefore never
reported on the pivot bar itself. This delay is real and documented, not engineered away.

### 7.2 EMA — [`engines/EMA_ENGINE.md`](engines/EMA_ENGINE.md)

`ema20`, `ema50`, `ema200` `[OWNER]`.

```
reclaim(e)  = C > e and ta.barssince(ta.crossover(C, e))  <= reclaimWindow
rejection(e)= (H > e and C < e) or (C < e and ta.barssince(ta.crossunder(C, e)) <= reclaimWindow)
```

`reclaimWindow` default `3` closed bars `[ENGINE-DEFAULT]` `CV-EMA-001`.

**Being above an EMA is not a reclaim.** A reclaim requires an actual crossing inside the
window, with price still on the new side. Strings: `EMA: Reclaiming 20 EMA ✓`,
`EMA: Bullish alignment ✓`, `EMA: Above 20 EMA`, `EMA: Below 20 EMA`,
`EMA: Rejected at 20 EMA`.

### 7.3 Volume — [`engines/VOLUME_ENGINE.md`](engines/VOLUME_ENGINE.md)

```
volAvg   = ta.sma(volume, 20)          [ENGINE-DEFAULT] CV-VOL-001
volRatio = volume / volAvg
ABOVE  : volRatio >= 1.20              [ENGINE-DEFAULT] CV-VOL-002
HIGH   : volRatio >= 1.50              [ENGINE-DEFAULT] CV-VOL-003
BELOW  : volRatio <= 0.80              [ENGINE-DEFAULT] CV-VOL-004
NORMAL : otherwise
```

**Data honesty rule** `[OWNER]`: the wording follows the data source.

| Instrument class | Wording |
| --- | --- |
| centralised (stock, futures, most crypto pairs on one venue) | `Volume: Above average ✓` |
| forex / CFD / broker-fed | `Volume: Above average tick volume ✓` |
| no volume series | `Volume: n/a (no volume data)` and the factor is **excluded** from scoring |

Forex tick volume is never described as centralised market volume, and no claim is made
that it represents traded size.

### 7.4 Location — [`engines/LOCATION_ENGINE.md`](engines/LOCATION_ENGINE.md)

States: `AT_SUPPORT`, `AT_RESISTANCE`, `AT_DEMAND`, `AT_SUPPLY`, `SWING_HIGH`,
`SWING_LOW`, `MID_RANGE`, `UNCLEAR` `[OWNER]`.

Built only from **confirmed** pivots, with an ATR tolerance:

```
tol        = ATR * locTolAtr           locTolAtr = 0.50   [ENGINE-DEFAULT] CV-LOC-001
AT_SUPPORT = any stored pivot-low level P with abs(L - P) <= tol
touches(P) = number of confirmed pivots within tol of P
AT_DEMAND  = AT_SUPPORT and touches(P) >= 2                 [ENGINE-DEFAULT] CV-LOC-002
rangePos   = (C - lowest(100)) / (highest(100) - lowest(100))            CV-LOC-003
SWING_LOW  = rangePos <= 0.20 ,  SWING_HIGH = rangePos >= 0.80           CV-LOC-004
MID_RANGE  = 0.40 <= rangePos <= 0.60                                    CV-LOC-005
```

**"Major support" → measurable** `[ENGINE-DEFAULT]` `CV-LOC-006`: a level with
`touches >= 2` where at least one touch comes from a pivot of length ≥ `10`.

Demand/supply here means *a price area that has been defended more than once in the visible
history*. It is not order-flow, not institutional positioning, and the docs never imply the
script can see either.

---

## 8. Confirmation lifecycle (L7)

Full detail: [`engines/CONFIRMATION_ENGINE.md`](engines/CONFIRMATION_ENGINE.md).

```
                 ┌─────────────┐
   structure ok  │  DETECTED   │  label created at the pattern's last candle
   ───────────►  └──┬───┬───┬──┘
                    │   │   │
      trigger hit   │   │   │  window elapsed
      ┌─────────────┘   │   └─────────────┐
      ▼                 ▼                 ▼
┌───────────┐    ┌────────────┐    ┌───────────┐
│ CONFIRMED │    │   FAILED   │    │  EXPIRED  │
└───────────┘    └────────────┘    └───────────┘
                 invalidation hit
```

All three transitions require a **fully closed** candle after the pattern's last candle.

Generic rule when a supplied spec gives no explicit one `[ENGINE-DEFAULT]` `CV-CONF-001`:

| Direction | Trigger (→ CONFIRMED) | Invalidation (→ FAILED) |
| --- | --- | --- |
| bullish | a closed candle closes **above the pattern high** | a closed candle closes **below the pattern low** |
| bearish | a closed candle closes **below the pattern low** | a closed candle closes **above the pattern high** |
| neutral | either side breaks; the break direction becomes the resolved direction | — |

* Window: `confirmBars` closed candles, default `3` `[ENGINE-DEFAULT]` `CV-CONF-002`.
* Both conditions on the same candle → **FAILED** wins (conservative) `CV-CONF-003`.
* `EXPIRED` is distinct from `FAILED`: nothing happened, versus the pattern was negated.
  They are never merged, and `EXPIRED` does not fire the "failed" alert.
* States are terminal. A `FAILED` pattern is never revived by later price action.
* Any pattern whose supplied spec defines its own confirmation or failure rule uses that
  rule; the generic rule is only a fallback and the pattern file says which applied.

---

## 9. Validation / confluence (L6)

Full detail: [`engines/VALIDATION_ENGINE.md`](engines/VALIDATION_ENGINE.md).

Structure is a **precondition, not a factor** — it is never scored, because an invalid
structure is not reported at all.

Six factors, each `+1`, `0`, or *excluded* `[OWNER]` factor list:

| Factor | `+1` when | Excluded when |
| --- | --- | --- |
| Trend | trend state matches the pattern's required trend | pattern requires no trend |
| Location | bullish at support/demand/swing low; bearish at resistance/supply/swing high | location `UNCLEAR` |
| RSI | divergence in the pattern's direction, or OS (bullish) / OB (bearish) | — |
| EMA | reclaim/alignment in the pattern's direction | fewer bars than the longest EMA in relaxed mode |
| Volume | `ABOVE` or `HIGH` | no volume series |
| Confirmation | status is `CONFIRMED` | status still `DETECTED` → `0`, not excluded |

```
score = Σ factors                     0 .. maxScore
maxScore = 6 - (excluded factors)
ratio = score / maxScore
```

Bands on the **ratio**, so that excluded factors cannot silently inflate or deflate a
result `[DERIVED from OWNER bands]`:

| Band | Ratio | Equivalent at `maxScore = 6` |
| --- | --- | --- |
| `WEAK` | `ratio <= 0.3333` | 0–2 |
| `MODERATE` | `<= 0.5000` | 3 |
| `STRONG` | `<= 0.8333` | 4–5 |
| `VERY STRONG` | `> 0.8333` | 6 |

The owner-supplied bands (0–2 WEAK / 3 MODERATE / 4–5 STRONG / 6+ VERY STRONG) are the
`maxScore = 6` case of the same table `[OWNER]`. Band edges are inputs.

### 9.1 Anti-inflation rules `[ENGINE-DEFAULT]` `CV-VAL-001`

A high score must mean *agreement*, not *box count*:

1. **Contradiction cap.** If a context factor directly opposes the pattern (bullish
   pattern in a `trendStrength >= 2` `DOWNTREND`… i.e. the wrong side), the band is capped
   at `MODERATE`, and at `WEAK` if two or more factors oppose. Caps are shown in the
   tooltip as `(capped: trend opposes)`.
2. **No double counting.** RSI divergence and RSI oversold are one factor, not two. EMA
   reclaim and EMA alignment are one factor.
3. **Unconfirmed ceiling.** A `DETECTED`-but-unconfirmed pattern cannot reach
   `VERY STRONG`. `VERY STRONG` requires the confirmation factor.
4. **Exclusion is neutral.** An excluded factor lowers `maxScore`; it is never counted as
   a pass and never as a fail.
5. **Mandatory factors are not scoring factors.** If a spec makes a factor mandatory, its
   failure suppresses the pattern (§1.1); when it passes it still scores `+1`, because it
   is genuine confluence.

---

## 10. Display (L8)

Full detail: [`engines/DISPLAY_ENGINE.md`](engines/DISPLAY_ENGINE.md).

### 10.1 Chart label `[OWNER]`

* Label text is the **abbreviation only** — `HAM`, `BEC`, `PL`, `MS`, `MDS`, `ES`, `EDS`,
  `TWS`, `TBC`, `THRU`, …
* The full name appears on the chart **only** when `Debug mode` is enabled.
* Bullish labels below the bar, bearish above, neutral above `[ENGINE-DEFAULT]`
  `CV-DISP-001`.
* Colour by direction; size/opacity by validation band `[ENGINE-DEFAULT]` `CV-DISP-002`.
* Status is *not* in the label text (it would pollute the chart); it is the first line of
  the tooltip. A resolved status may optionally be marked with a single-character suffix
  when `Show status marks` is on: `✓` confirmed, `✗` failed, `·` expired `CV-DISP-003`.

### 10.2 Tooltip — exact format `[OWNER]`

```
BEC
Bullish Engulfing
Status: CONFIRMED

Pattern: Valid ✓
Trend: Downtrend ✓
Location: Support ✓
RSI: Bullish divergence ✓
EMA: Reclaiming 20 EMA ✓
Volume: Above average ✓

Validation: STRONG
```

Then, after a blank line, a structural block `[ENGINE-DEFAULT]` `CV-DISP-004`:

```
── Structure ──
Body: 68.2% of range
Upper wick: 6.1% · Lower wick: 25.7%
Penetration: 71.4% of previous body
Gap: none
Rel. body: 1.8× avg(20)
Confirm: close > 1.10842 within 3 bars
Timeframe: 1H (class HOUR_LOW, allowed)
```

Rules: a `✓` marks a factor that **passed**; a factor that did not pass is printed without
a tick and without a cross, exactly as in the owner's `RSI: Neutral` example. Absent data
prints `n/a` plus the reason. Nothing is omitted, so the tooltip always has the same shape.

### 10.3 Info panel `[ENGINE-DEFAULT]` `CV-DISP-005`

One optional table, written on the last bar only: chart timeframe + class + enforcement
mode, trend state and strength, RSI value and state, EMA alignment, volume state and
source wording, location state, counts of detected/confirmed/failed, `TEST MODE` banner
when active.

---

## 11. Filters, toggles, alerts

### 11.1 Display filter `[OWNER]`

`ALL`, `BULLISH ONLY`, `BEARISH ONLY`, `BULLISH REVERSAL ONLY`,
`BEARISH REVERSAL ONLY`, `REVERSAL ONLY`, `CONTINUATION ONLY`, `EXHAUSTION ONLY`,
`NEUTRAL ONLY`.

The filter is a **display-layer** mask. Detection, confirmation tracking, and scoring keep
running for filtered-out patterns, so a hidden pattern's lifecycle is intact when it is
unhidden `[OWNER]`. Filters match a pattern's **primary** category
(`patterns/CLASSIFICATION.md`); an input `Filter includes secondary categories`
(default off) widens them `[ENGINE-DEFAULT]` `CV-FILT-001`.

### 11.2 Per-pattern toggles `[OWNER]`

Every pattern gets its own `Show <name>` boolean, grouped by category in the settings
dialog. Default on. A disabled pattern is skipped at the display layer, exactly like a
filtered one.

### 11.3 Alerts `[OWNER]` mechanism `[ENGINE-DEFAULT]` `CV-ALERT-001`

* Per-pattern, per-state events use `alert()` with
  `alert.freq_once_per_bar_close` and a structured message:
  `CM | <ABBR> | <STATE> | <symbol> <timeframe> | Validation: <BAND> | <price>`.
* A small fixed set of `alertcondition` series is exposed for TradingView's alert dialog:
  `Any Detected`, `Any Confirmed`, `Any Failed`, `Bullish Detected`, `Bullish Confirmed`,
  `Bearish Detected`, `Bearish Confirmed`, `Strong or better Detected`,
  `Very Strong Confirmed`.
* Rationale for not creating ~150 individual `alertcondition`s (3 states × 50+ patterns):
  compiled-script cost and an unusable alert dialog. Per-pattern granularity is achieved
  with the `alert()` message plus an optional "focus one pattern" input.
* **No alert ever places, modifies, or closes an order.** This indicator has no strategy
  functions and no broker integration.

---

## 12. No-repainting policy `[OWNER]`

1. Detection, confirmation, labels, and alerts occur only on **closed** candles.
2. No pattern's evaluation reads a bar that did not exist at that pattern's own bar.
3. Pivot-derived features become available only after the pivot's confirmation delay.
4. A signal is never back-dated to before the bar on which it was knowable.
5. Documented delays are listed in [`ARCHITECTURE.md` §5](ARCHITECTURE.md).
6. `request.security` (if a supplied spec ever forces higher-timeframe data) will use
   `lookahead_off` with a `[1]` offset, and the resulting extra delay will be documented
   per pattern.
7. A label's status advancing `DETECTED → CONFIRMED` on a later closed bar is a state
   machine, not repainting: the transition bar is fixed and no earlier decision changes.

---

## 13. Pine Script constraints `[OWNER]`

Binding on all future implementation work:

* Pine Script **v6** only. No invented syntax; anything not in the official reference is
  not used.
* `//@version=6`, `indicator(...)` with `max_labels_count` declared, `overlay = true`.
* v6 `na`-in-`bool` semantics: booleans are kept non-`na` by construction; comparisons that
  can produce `na` are wrapped (`nz`, explicit availability flags). No reliance on the v5
  behaviour where `na` collapsed to `false`.
* `input.*`, `plot*`, and `alertcondition` only at global scope.
* No `ta.*` inside a pattern function (§A2).
* No `request.*` in the core path.
* Functions stay small; nesting depth ≤ 2; no fragile multiline expressions.
* Every engine gets a comment banner matching the section list in `ARCHITECTURE.md` §7.
* Resource budget in `ARCHITECTURE.md` §6 is a hard constraint, not an aspiration.

---

## 14. Financial-accuracy rules `[OWNER]`

1. This is an **educational pattern-recognition tool**. Nothing here is advice.
2. No probability, win rate, reliability percentage, or expectancy is invented anywhere in
   the repo or the script.
3. A supplied statistic (e.g. `±72%`) is stored verbatim in the pattern file's *As
   Supplied* block, displayed only if requested, and always attributed as
   `User-provided reference`. It never enters the scoring engine, the validation band, or
   any calculation.
4. `Reliability` and `Risk` classifications are stored as **supplied labels**, not as
   computed or validated quantities.
5. Volume claims stay within what the data supports (§7.3).
6. Market psychology text is stored as *pattern psychology (as supplied)* — narrative
   context, never presented as measured fact.
7. Pattern rarity is preserved. A rule is never loosened to produce more signals; if a
   specification makes a pattern rare, it stays rare.

---

## 15. Definition of done

The project is not "finished" until all of:

* every supplied pattern exists as a file, a registry row, a toggle, and a test set;
* `CONFLICT_LOG.md` has no unresolved `BLOCKING` entry;
* every `[ENGINE-DEFAULT]` in use is listed in `docs/DEFINITION_CONVERSIONS.md`;
* the Pine file compiles in TradingView v6 with no errors and no warnings;
* the resource review in `ARCHITECTURE.md` §6 has been re-run against the final script;
* `tests/PINE_COMPILE_CHECKLIST.md` and `tests/PATTERN_TESTS.md` are executed and recorded;
* no-repaint checks (§12) are re-verified on a live forming bar and on history;
* a structural review of the whole file has been done — not just a fix of whatever line
  TradingView last complained about.

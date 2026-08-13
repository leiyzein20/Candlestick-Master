# LOCATION ENGINE (L3)

Where in the structure the pattern happened. Built from confirmed pivots and stated
approximations — never from claims about order flow.

---

## 1. Purpose

Answer "is this at support / resistance / mid-range?" with a reproducible calculation, and
give the phrase "major support" one explicit measurable meaning.

## 2. Contract

**Inputs:** `high`, `low`, `close`, `atr14`, `ta.pivothigh/low(5, 5)`,
`ta.highest/lowest(100)`, `bar_index`.

**Outputs:**

| Output | Type | Meaning |
| --- | --- | --- |
| `locState` | int enum | `AT_SUPPORT` / `AT_RESISTANCE` / `AT_DEMAND` / `AT_SUPPLY` / `SWING_HIGH` / `SWING_LOW` / `MID_RANGE` / `UNCLEAR` |
| `locLevel` | float | the level matched, or `na` |
| `locTouches` | int | confirmed touches of that level |
| `rangePos` | float | `0..1` position within the 100-bar range |
| `locText` | string | the exact tooltip string |
| `locReady` | bool | at least two confirmed pivots exist |

## 3. Level store

Confirmed pivot highs and lows are kept in two capped arrays (20 entries each, FIFO)
`[ENGINE-DEFAULT]` `CV-LOC-007`. Each entry holds the level, the bar it formed, and the bar
it was **confirmed** (`pivotBar + right`).

Only confirmed pivots enter the store, and no entry is usable before its confirmation bar
([`../ARCHITECTURE.md`](../ARCHITECTURE.md) A6). This is the same discipline as
[`RSI_ENGINE.md`](RSI_ENGINE.md) §5.1 and for the same reason: a level that "was support" can
only be known to be a pivot five bars later.

Cap of 20 is a budget decision: 20 levels on each side spans a long visible history at any
timeframe, and the per-bar loop stays at ~40 iterations.

## 4. Proximity

```
tol = atr14 * locTolAtr          locTolAtr = 0.50   [ENGINE-DEFAULT] CV-LOC-001
```

```
AT_SUPPORT    = any stored pivot-low  level P with abs(low  - P) <= tol
AT_RESISTANCE = any stored pivot-high level P with abs(high - P) <= tol
```

ATR-scaled rather than percentage-scaled, so one tolerance works on EURUSD, BTC, and an
index, and so the tolerance widens in volatile conditions where levels are genuinely fuzzier.

The candle's **low** is tested against support and its **high** against resistance: a pattern
"at support" is one that reached down to the level, not one whose close happened to be near
it.

## 5. Demand and supply — an approximation, labelled as one

```
locTouches(P) = number of confirmed pivots within tol of P
AT_DEMAND = AT_SUPPORT    and locTouches >= 2     [ENGINE-DEFAULT] CV-LOC-002
AT_SUPPLY = AT_RESISTANCE and locTouches >= 2
```

What this means: **a price area that has been turned away from more than once in the visible
history.** That is all it means.

What it does **not** mean, and what the tooltip, the docs, and the code comments never imply:

* an institutional order block,
* unfilled limit orders resting at the level,
* accumulation or distribution,
* "smart money" positioning,
* anything about volume profile or order-book depth.

None of that is observable from OHLC in Pine, and the words "demand" and "supply" are used
here only because the owner's engine list names them. The distinction between `AT_SUPPORT`
and `AT_DEMAND` in this engine is *touch count*, nothing more, and that is stated in the
tooltip: `Location: Demand (2 touches) ✓`.

## 6. Range position

```
rangePos = (close - lowest(100)) / (highest(100) - lowest(100))     CV-LOC-003
```

| State | Rule | ID |
| --- | --- | --- |
| `SWING_LOW` | `rangePos <= 0.20` | `CV-LOC-004` |
| `SWING_HIGH` | `rangePos >= 0.80` | `CV-LOC-004` |
| `MID_RANGE` | `0.40 <= rangePos <= 0.60` | `CV-LOC-005` |
| `UNCLEAR` | `0.20 < rangePos < 0.40` or `0.60 < rangePos < 0.80` | `[DERIVED]` |

The two unnamed bands are deliberate. Calling `rangePos = 0.35` either "swing low" or
"mid-range" would be a coin flip, and `UNCLEAR` excludes the location factor from the score
instead of guessing ([`VALIDATION_ENGINE.md`](VALIDATION_ENGINE.md)).

Lookback `100` bars `[ENGINE-DEFAULT]` `CV-LOC-003`. Degenerate case
`highest(100) == lowest(100)` (a completely flat 100 bars) → `rangePos = 0.5`, `UNCLEAR`.

## 7. State precedence

`[ENGINE-DEFAULT]` `CV-LOC-008`, most specific first:

```
1  AT_DEMAND / AT_SUPPLY        (a level with >= 2 touches)
2  AT_SUPPORT / AT_RESISTANCE   (a level with 1 touch)
3  SWING_LOW / SWING_HIGH       (range position extreme, no level nearby)
4  MID_RANGE
5  UNCLEAR
```

If the candle is simultaneously near a pivot low and a pivot high — possible on a wide bar in
a tight range — the **nearer** level wins; on an exact tie, support wins for a bullish
pattern and resistance for a bearish one, which is the only place in this engine where the
pattern's direction affects the location reading. That tie-break is recorded because it is a
choice, not arithmetic.

## 8. "Major support" — the conversion

`[ENGINE-DEFAULT]` `CV-LOC-006`:

```
isMajorLevel(P) = locTouches(P) >= 2
              and at least one contributing pivot has left/right length >= 10
```

The second clause requires one of the touches to be a *structurally significant* pivot — a
low with ten bars of higher lows on each side, not a minor wiggle. Implemented with a second
pivot series at length 10, which is one additional shared `ta.*` pair.

Stated plainly: "major" is subjective, this is one explicit operationalisation of it, and any
supplied specification that defines it differently overrides this for its own pattern.

## 9. What the engine will not do

* Draw zones. No boxes, no lines — the box budget stays at zero
  (`ARCHITECTURE.md` §6) and location is reported as text.
* Merge nearby levels into a "zone" with a computed width. That is an extra model with extra
  parameters and it was not specified.
* Use volume profile, VWAP, or session levels. Not specified, not invented.
* Claim a level will hold.

## 10. Cost

| Item | Count |
| --- | --- |
| `ta.*` calls | 4 pivots (len 5 and len 10, high and low) + 2 extremes, all shared |
| Arrays | 2, capped at 20 entries |
| Loop iterations | ≤ 40 per bar |
| Drawings | 0 |

## 11. Tests

Vectors `tests/vectors/location.json`:

* a level touched once → `AT_SUPPORT`; touched twice → `AT_DEMAND` with `locTouches == 2`;
* a candle exactly `tol` away → matched (inclusive); one tick further → not matched;
* a pivot used before its confirmation bar → must never happen (asserted on the pivot store);
* `rangePos` at `0.20`, `0.40`, `0.60`, `0.80` boundaries;
* the `0.20 < rangePos < 0.40` gap → `UNCLEAR` and the factor excluded from `maxScore`;
* flat 100-bar window → no division error, `UNCLEAR`;
* the near-support-and-resistance tie-break;
* `locReady == false` before two confirmed pivots exist, with the factor excluded.

## 12. Open questions for supplied specifications

| # | Question | Until answered |
| --- | --- | --- |
| 1 | Is `0.5 × ATR` the right proximity tolerance? | `0.50` (`CV-LOC-001`), input |
| 2 | Does "at support" mean the wick reached it, or the close is near it? | the wick (low/high), §4 |
| 3 | Is a 100-bar lookback right for range position? | `100` (`CV-LOC-003`) |
| 4 | Does "major support" mean something more specific? | ≥2 touches, one long pivot (`CV-LOC-006`) |
| 5 | Should any pattern **require** a location match? | none assumed; only an explicit spec makes it mandatory |

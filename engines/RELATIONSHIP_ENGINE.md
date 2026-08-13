# RELATIONSHIP ENGINE (L2)

Candle-to-candle mathematics for offsets 1–5. Exact arithmetic only — no approximation
where OHLC can answer the question directly.

---

## 1. Purpose

Own every comparison between two candles: engulfment, containment, gaps, the 50% family,
penetration depth, and the open/close relations. One implementation each, reused by every
pattern.

## 2. Contract

**Inputs:** [`OHLC_ENGINE.md`](OHLC_ENGINE.md) outputs at the two offsets involved, `atr14`
(gap sizing only), `tick`, `eps`.

**Convention:** `relates(a, b)` compares the candle at offset `a` (the newer) to the candle
at offset `b` (the older), with `b > a`. The common case is `a = 0, b = 1`. All published
helpers take both offsets so three- and five-candle patterns reuse them without a second
implementation.

## 3. Previous-candle accessors `[OWNER]`

Offsets 1–5 for: open, high, low, close, body, bodyTop, bodyBottom, range, candleMid,
bodyMid, colour. All are pass-throughs to the OHLC engine at the requested offset — they
exist as named accessors so pattern files can read like their specifications
("previous candle midpoint") while resolving to one shared definition.

## 4. Engulfment `[OWNER]`

```
bodyEngulfs(a, b)        = bodyTop(a) >= bodyTop(b) and bodyBottom(a) <= bodyBottom(b)
bodyEngulfsStrict(a, b)  = bodyTop(a) >  bodyTop(b) and bodyBottom(a) <  bodyBottom(b)
rangeEngulfs(a, b)       = H(a) >= H(b) and L(a) <= L(b)
rangeEngulfsStrict(a, b) = H(a) >  H(b) and L(a) <  L(b)
```

Four variants because two independent choices exist: **body vs range** (does the wick
count?) and **inclusive vs strict** (may the two candles share a boundary?).

They differ in real cases:

| Case | `bodyEngulfs` | `bodyEngulfsStrict` |
| --- | --- | --- |
| `O = C1` exactly (very common — the new candle opens at the old close) | `true` | `false` |
| new body one tick larger on both sides | `true` | `true` |

Because opening exactly at the previous close is extremely common on 24-hour instruments,
the inclusive/strict choice materially changes how often engulfing patterns fire. Default
for an unqualified "engulfs" is **inclusive body** (`CV-REL-001`), and every pattern file
records which of the four it uses.

## 5. Containment `[DERIVED]`

```
bodyInside(a, b)  = bodyTop(a) <= bodyTop(b) and bodyBottom(a) >= bodyBottom(b)   -- harami
rangeInside(a, b) = H(a) <= H(b) and L(a) >= L(b)                                 -- inside bar
```

`bodyInside` is the exact logical inverse of `bodyEngulfs` with the arguments swapped, and
that identity is asserted in the tests to keep the two from drifting apart.

## 6. The 50% family `[OWNER]`

Three distinct statements, all published, never conflated:

```
closeAbovePrevBodyMid(a, b)  = C(a) > bodyMid(b)      -- (O(b) + C(b)) / 2
closeAbovePrevRangeMid(a, b) = C(a) > candleMid(b)    -- (H(b) + L(b)) / 2
closeAbovePrevBodyPct(a, b, p)
    = C(a) > bodyBottom(b) + p * (bodyTop(b) - bodyBottom(b))
```

plus `closeBelow...` mirrors, and `openAbove...` / `openBelow...` variants where a supplied
rule concerns the open.

`closeAbovePrevBodyPct(a, b, 0.5)` equals `closeAbovePrevBodyMid(a, b)` — an identity that
the tests assert, so the general form can be trusted for the 30% / 70% / two-thirds cases
that supplied specifications sometimes use.

**Default for an unqualified "50% level": previous body midpoint** (`CV-REL-002`,
`SI-01`). The body reading is the one used by the classical descriptions of the
piercing/dark-cloud family, but "the middle of the previous candle" is a defensible reading
of the range midpoint, so the choice is recorded per pattern rather than assumed globally.

The strictness question repeats here: "closes above the midpoint" is encoded as `>`, and
"closes at or above" as `>=`. A close landing exactly on a computed midpoint is possible
whenever the midpoint happens to be a valid tick price, so the choice is explicit and is a
test vector.

## 7. Penetration percentage `[OWNER]`

How far the newer candle's close reaches into the older candle's body, as a fraction of that
body:

```
prevBodySize      = abs(O(b) - C(b))

-- newer bullish candle penetrating an older bearish body (O(b) > C(b))
penetrationUp(a, b)   = (C(a) - C(b)) / (O(b) - C(b))

-- newer bearish candle penetrating an older bullish body (C(b) > O(b))
penetrationDown(a, b) = (C(b) - C(a)) / (C(b) - O(b))
```

Reading the scale: `0.0` = closed at the older body's far end (no penetration), `0.5` =
exactly halfway, `1.0` = closed at the older body's near end, `> 1.0` = closed beyond the
older body (engulfment territory), `< 0` = closed on the wrong side entirely.

Edge cases:

| Condition | Behaviour |
| --- | --- |
| `prevBodySize == 0` (older candle is a perfect doji) | penetration is **undefined**; the accessor returns `na` and any pattern requiring it returns `false` `[DERIVED]` |
| older candle's colour is not the one the formula assumes | the pattern's own colour rules must already exclude it; the accessor does not silently flip sign |
| display | clamped to `[-1.0, 2.0]` for the tooltip only, never for logic (`CV-REL-003`) |

The `na`-on-doji rule matters: a "closes more than 50% into the previous body" condition
cannot be evaluated when there is no previous body, and returning `false` from the accessor
instead of `na` would hide the distinction between "not deep enough" and "not
measurable".

## 8. Gaps `[OWNER]`

```
trueGapUp(a, b)   = L(a) > H(b)                    -- ranges do not overlap at all
trueGapDown(a, b) = H(a) < L(b)
bodyGapUp(a, b)   = bodyBottom(a) > bodyTop(b)     -- bodies do not overlap; wicks may
bodyGapDown(a, b) = bodyTop(a) < bodyBottom(b)
gapUpSize(a, b)   = L(a) - H(b)
gapUpSizeAtr(a,b) = (L(a) - H(b)) / atr14
```

Which one a pattern means comes from its specification. Engine defaults for the
unqualified word "gap": **body gap** inside the star family (`CV-REL-004`), **true gap**
everywhere else (`CV-REL-005`). Optional minimum size `gapMinAtr`, default `0`
(`CV-REL-006`).

Instrument reality, documented rather than engineered around:

| Instrument class | True intraday gaps | Notes |
| --- | --- | --- |
| equities, index futures with a session break | common | at session boundaries |
| spot FX | rare | weekend gap only; 24×5 |
| crypto | very rare | 24×7 |
| any instrument | possible | thin liquidity, halts, feed outages |

A gap-dependent pattern is therefore near-impossible on some instruments. That is stated in
the pattern file. No rule is weakened to manufacture gaps
([`../MASTER_SPECIFICATION.md`](../MASTER_SPECIFICATION.md) §14.7).

Pine cannot distinguish a genuine liquidity gap from a missing bar. Recorded as a
limitation; not detectable.

## 9. Open / close relations `[OWNER]`

```
openAbovePrevClose, openBelowPrevClose, openAbovePrevOpen,  openBelowPrevOpen
closeAbovePrevClose, closeBelowPrevClose
closeAbovePrevHigh,  closeBelowPrevLow
higherHigh (H(a) > H(b)),  lowerLow (L(a) < L(b))
higherClose, lowerClose, higherOpen, lowerOpen
```

`closeAbovePrevHigh` doubles as the default bullish confirmation trigger
([`CONFIRMATION_ENGINE.md`](CONFIRMATION_ENGINE.md)), computed once and reused.

## 10. Multi-candle helpers `[DERIVED]`

For three-to-five candle patterns, bounded and non-looping:

```
allBull(from, to)      -- every candle in the inclusive offset span is bullish
allBear(from, to)
risingCloses(from, to) -- each close above the previous (newer > older)
fallingCloses(from, to)
higherHighs(from, to), lowerLows(from, to)
maxHigh(from, to), minLow(from, to)
```

Spans are limited to offsets 0–5. These are the only place a supplied phrase like "three
consecutive bullish candles" is translated, so all such patterns share one implementation.

## 11. Cost

| Item | Count |
| --- | --- |
| `ta.*` calls | 0 (`atr14` is shared, computed elsewhere) |
| History reads | up to 4 prices × 6 offsets, via Pine's `[]` |
| Arrays / drawings | 0 |

No stored candle history: Pine's history operator already provides it up to
`max_bars_back`.

## 12. Tests

[`../tests/OHLC_TESTS.md`](../tests/OHLC_TESTS.md), vectors
`tests/vectors/relationship.json`:

* all four engulfment variants on the shared-boundary case (`O == C1`);
* `bodyInside(a,b)` ≡ `bodyEngulfs(b,a)` identity;
* `closeAbovePrevBodyPct(a,b,0.5)` ≡ `closeAbovePrevBodyMid(a,b)` identity;
* body-midpoint vs range-midpoint on a candle where they differ substantially (long single
  wick) — asserting the two are not interchangeable;
* penetration at `0.0`, `0.4999`, `0.5`, `0.5001`, `1.0`, `> 1.0`, `< 0`, and doji-previous
  (`na`);
* `trueGap` vs `bodyGap` on a case where bodies gap but wicks overlap;
* gap size in ATR units, including `atr14` warm-up;
* five-candle spans at the depth limit.

## 13. Open questions for supplied specifications

| # | Question | Until answered |
| --- | --- | --- |
| 1 | Per-pattern: engulfment inclusive or strict, body or range? | inclusive body (`CV-REL-001`, `SI-02/03`) |
| 2 | Per-pattern: is "50%" the body midpoint or the range midpoint? | body midpoint (`CV-REL-002`, `SI-01`) |
| 3 | Per-pattern: "gap" = true gap or body gap? Minimum size? | star family body, else true; size `0` (`SI-04`) |
| 4 | Is penetration measured to the close only, or may a wick satisfy it? | close only — the classical reading; flagged per pattern if a spec implies otherwise |

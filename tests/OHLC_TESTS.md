# OHLC / WICK-BODY / RELATIONSHIP TESTS

Covers [`engines/OHLC_ENGINE.md`](../engines/OHLC_ENGINE.md),
[`engines/WICK_BODY_ENGINE.md`](../engines/WICK_BODY_ENGINE.md),
[`engines/RELATIONSHIP_ENGINE.md`](../engines/RELATIONSHIP_ENGINE.md).

```bash
python3 tools/run_tests.py ohlc identities wick_body relationship degenerate
```

Vectors: `vectors/ohlc_engine.json`, `vectors/wick_body.json`, `vectors/relationship.json`.

---

## 1. Primitives — `vectors/ohlc_engine.json`

| ID | Case | Why it is in the suite |
| --- | --- | --- |
| `OHLC-001` | standard bullish candle | baseline for every ratio |
| `OHLC-002` | mirrored bearish candle | identical geometry must give identical body/wick values and a mirrored `close_pos` |
| `OHLC-003` | perfect doji | `body == 0`, equal wicks, `is_flat` — not bullish, not bearish |
| `OHLC-004` | degenerate candle, all four prices equal | the division-by-zero case; must be `is_measurable == false` with defined constants |
| `OHLC-005` | bullish marubozu | `bodyPct == 1`, both wicks zero, `close_pos == 1` |
| `OHLC-006` | tiny body high in the range, long lower wick | geometry only — asserts nothing about any pattern |
| `OHLC-007` | one-tick range | measurable, but every ratio is extreme |
| `OHLC-008` | close exactly at the low | `close_pos == 0` boundary |
| `OHLC-009` | candle midpoint 92.5 vs body midpoint 102.0 | the two are different numbers |

## 2. Identities — run on every case plus 2000 random candles

From [`OHLC_ENGINE.md` §3](../engines/OHLC_ENGINE.md):

```
range == body + upperWick + lowerWick
bodyPct + upperWickPct + lowerWickPct == 1        (when measurable)
bodyTop - bodyBottom == body
closePos == 1 - (H - C) / range
exactly one of isBull / isBear / isFlat
all ratios within 0..1
```

Random candles are generated with a fixed seed (`20260813`) so a failure is reproducible, and
include a deliberate share of zero-range and one-tick candles.

## 3. Shape classes — `vectors/wick_body.json`

Boundary-first, because a threshold is only interesting at its edge.

| ID | Case | Expected |
| --- | --- | --- |
| `WB-001` | body exactly 10% | doji (inclusive) |
| `WB-002` | body 10.1% | not a doji, still a small body |
| `WB-003` | body exactly 30% | small body (inclusive) |
| `WB-004` | body exactly 60% | large body (inclusive), not a marubozu |
| `WB-005` | body exactly 90% | marubozu, both wicks short |
| `WB-006` | body 30%, lower wick 65% | **both** long-wick idioms agree |
| `WB-007` | body 5%, lower wick 45%, upper wick 50% | the idioms **disagree**: body-multiple says long, range-fraction says no |
| `WB-008` | `body == 0` with 50% wicks | the body-multiple trap is visible: `wick >= 2 * body` is trivially true |
| `WB-009` | wick exactly 60% of range | long by the range-fraction idiom |
| `WB-010` | wick exactly 10% of range | still a short wick |

Plus asserted implications: every doji body is a small body, and every marubozu is a large
body. The classes overlap by design and no code may assume they partition.

`WB-007` and `WB-008` are the reason the engine publishes two long-wick definitions instead
of choosing one. They are the cases a supplied specification has to disambiguate (`SI-05`).

## 4. Relationships — `vectors/relationship.json`

| ID | Case | Expected highlight |
| --- | --- | --- |
| `REL-001` | new open == old close, new close == old open | inclusive engulfment `true`, strict `false` |
| `REL-002` | previous candle has a long lower wick | the same close is **below** the body midpoint and **above** the range midpoint |
| `REL-003` | penetration exactly `0.5` | close sits *on* the body midpoint, so strict `>` is `false` |
| `REL-004` | previous candle is a doji | penetration is `null`, not `0.0` |
| `REL-005` | bodies gap, ranges overlap | `body_gap_up` true, `true_gap_up` false |
| `REL-006` | true gap of 2.0 with ATR 4.0 | `gap_up_size_atr == 0.5` |
| `REL-007` | harami / inside bar | body inside and range inside, engulfment false |
| `REL-008` | true gap down | close below previous low, penetration 3.25 |

Two identities are asserted on **every** relationship case, not just chosen ones:

```
bodyInside(a, b)                     == bodyEngulfs(b, a)
closeAbovePrevBodyPct(a, b, 0.5)     == closeAbovePrevBodyMid(a, b)
```

The second matters because the general `p`-percent form is what a supplied "closes above two
thirds of the previous body" rule will use; if it disagreed with the 50% helper at `p = 0.5`,
one of the two would be wrong.

## 5. Degenerate-data gating

| Check | Expected |
| --- | --- |
| zero-range candle | `is_measurable == false` |
| zero-range `close_pos` | `0.5` — never a value that could satisfy "closed in the upper third" |
| zero-range marubozu test | `false`, despite `bodyPct` being defined as `0` |
| zero-range long-wick tests | `false` |
| zero-range doji test | `true` (documented consequence of `bodyPct == 0`) |

The last row is a deliberate, documented outcome rather than an accident: a zero-range candle
*is* body-less. The protection against it satisfying a pattern is the mandatory
`is_measurable` gate in every pattern's structure test, not a special case inside the class
functions.

## 6. To add when specifications arrive

* Five-candle span helpers (`allBull`, `risingCloses`, `maxHigh`) at the offset-5 depth limit.
* `eps` tolerance behaviour once an instrument with coarse ticks is nominated.
* Any pattern-specific threshold that overrides an `[ENGINE-DEFAULT]`, tested at its own
  boundary.

## 7. Manual checks (TradingView only)

| # | Check | Why it cannot be automated |
| --- | --- | --- |
| M1 | ratios on a real chart match the tooltip to 1 decimal | needs the live tooltip renderer |
| M2 | a real zero-range bar (illiquid session) produces no detection | needs real data |
| M3 | history offsets 1–5 read the intended bars at the very start of the chart | needs Pine's `max_bars_back` behaviour |
| M4 | no `na`-related runtime error on the first bars of a fresh symbol | needs the Pine runtime |

# RSI ENGINE (L3)

RSI state and divergence. The engine's central discipline: **momentum is not divergence**,
and divergence is not knowable before its pivots are.

---

## 1. Purpose

Publish one RSI reading and one honest RSI state per bar, so pattern validation can cite
"RSI: Oversold ✓" or "RSI: Bullish divergence ✓" without either being invented.

## 2. Contract

**Inputs:** `close`, `rsiLen` (default `14` `[OWNER]`), overbought/oversold levels,
confirmed price pivots, `bar_index`.

**Outputs:**

| Output | Type | Meaning |
| --- | --- | --- |
| `rsi` | float | `ta.rsi(close, 14)` |
| `rsiState` | int enum | §4 |
| `rsiText` | string | the exact tooltip string |
| `bullDivActive` / `bearDivActive` | bool | §5 |
| `rsiReady` | bool | `bar_index >= rsiLen + 1` |

## 3. Parameters

| Parameter | Default | Provenance |
| --- | --- | --- |
| length | `14` | `[OWNER]` |
| overbought | `70` | `[ENGINE-DEFAULT]` `CV-RSI-001` |
| oversold | `30` | `[ENGINE-DEFAULT]` `CV-RSI-001` |
| midline | `50` | `[ENGINE-DEFAULT]` `CV-RSI-001` |
| pivot left / right | `5 / 5` | `[ENGINE-DEFAULT]` `CV-RSI-003` |
| min bars between pivots | `5` | `[ENGINE-DEFAULT]` `CV-RSI-004` |
| max bars between pivots | `60` | `[ENGINE-DEFAULT]` `CV-RSI-005` |
| divergence active window | `10` bars | `[ENGINE-DEFAULT]` `CV-RSI-006` |

## 4. States and precedence

Exactly one state per bar, resolved in this order `[ENGINE-DEFAULT]` `CV-RSI-002`:

| # | State | Condition | Tooltip string |
| --- | --- | --- | --- |
| 1 | `BULL_DIV` | `bullDivActive` | `RSI: Bullish divergence ✓` |
| 1 | `BEAR_DIV` | `bearDivActive` | `RSI: Bearish divergence` |
| 2 | `OVERSOLD` | `rsi <= 30` | `RSI: Oversold ✓` |
| 2 | `OVERBOUGHT` | `rsi >= 70` | `RSI: Overbought` |
| 3 | `BULL_MOM` | `rsi > 50 and rsi > rsi[1]` | `RSI: Bullish` |
| 3 | `BEAR_MOM` | `rsi < 50 and rsi < rsi[1]` | `RSI: Bearish` |
| 4 | `NEUTRAL` | anything else | `RSI: Neutral` |

Divergence outranks oversold/overbought because it is the more specific statement, and
because a bullish divergence very often *coincides* with oversold — showing the weaker of
the two would discard information.

The `✓` marks appear only where the state supports the pattern's direction; the display
engine, not this engine, decides which string gets the tick
([`DISPLAY_ENGINE.md`](DISPLAY_ENGINE.md)). A bearish divergence on a bullish pattern is
printed without a tick, exactly like the owner's `RSI: Neutral` example.

### 4.1 The prohibition

`rsi > 50` is **bullish momentum**. It is never labelled divergence, in any code path, log
line, tooltip, or document. The two states have different names, different conditions, and
different strings, and the tests assert that a rising-RSI series with no pivot pair produces
`RSI: Bullish` and never `RSI: Bullish divergence ✓`.

Reason it is stated this bluntly: conflating them is the single most common inaccuracy in
published pattern indicators, and it inflates the confluence score of every signal in a
trending market.

## 5. Divergence

Structure `[OWNER]`, parameters `[ENGINE-DEFAULT]`.

Requires **two confirmed pivots of the same kind**, with the RSI value sampled at each pivot
bar:

```
bullish divergence:
    pivotLow[k].price < pivotLow[k-1].price          -- price made a lower low
and rsiAtPivot[k]     > rsiAtPivot[k-1]              -- RSI made a higher low

bearish divergence:
    pivotHigh[k].price > pivotHigh[k-1].price        -- price made a higher high
and rsiAtPivot[k]      < rsiAtPivot[k-1]             -- RSI made a lower high
```

Additional conditions:

* pivot separation within `[5, 60]` bars — closer pivots are noise, further apart is not the
  same swing pair;
* the divergence becomes **active** on the bar the second pivot is *confirmed*, and stays
  active for `10` bars;
* only the most recent qualifying pair is considered; no multi-leg or hidden-divergence
  variants, because none was specified and inventing them would add unrequested rules.

### 5.1 Confirmation delay — stated, not hidden

`ta.pivotlow(5, 5)` reports a pivot **5 bars after it happened**. It has to: a low is only a
pivot once five later bars have failed to undercut it.

Therefore:

```
pivot forms at bar P  →  knowable at bar P + 5  →  divergence usable from bar P + 5
```

The engine records `confirmedAtBar = pivotBar + right` for every pivot and **refuses to use
a pivot before that bar**. On a bar where a pattern fires and the second pivot has not yet
been confirmed, the RSI state is whatever §4 rungs 2–4 produce — not divergence.

This is the no-repaint requirement applied concretely. The alternative — reading the pivot on
the bar it formed — would make historical signals look prescient and live signals look
broken, which is exactly the failure mode the owner's §14 forbids.

The cost is real and is accepted: a divergence-confirmed pattern label can be up to 5 bars
later than a chart reader's eye would place it. Documented in
[`../ARCHITECTURE.md`](../ARCHITECTURE.md) §5 and in every affected pattern file.

### 5.2 Why the RSI value is sampled at the price pivot

Two designs exist: pivot the price series and read RSI there, or pivot the RSI series
independently and pair the two sets.

This engine samples RSI **at the price pivot** because the pattern question is "did price
make a lower low while momentum did not?" — which is anchored to the price swing. Pivoting
both series independently produces pairs that can be several bars apart, and the pairing rule
would then be an invented parameter. Recorded as a design decision, not a claim that the
other approach is wrong `[ENGINE-DEFAULT]` `CV-RSI-007`.

## 6. Warm-up

`ta.rsi(close, 14)` is `na` for the first 14 bars.

```
rsiReady = bar_index >= rsiLen + 1
```

While false: `rsiState = NEUTRAL`, `rsiText = "RSI: n/a (warming up)"`, and the RSI factor is
**excluded** from the confluence score rather than counted as a miss
([`VALIDATION_ENGINE.md`](VALIDATION_ENGINE.md)). Divergence additionally needs enough bars
for two pivots — at minimum `2 × 5 + 5 + 5` bars — before it can ever be true.

## 7. Cost

| Item | Count |
| --- | --- |
| `ta.*` calls | 3 (`rsi`, `pivothigh`, `pivotlow`), pivots shared with location and trend |
| Arrays | 2 small ring buffers (last 2–4 pivots of each kind), capped |
| Per-bar work | a handful of comparisons |

Pivot arrays are capped at 4 entries per side: the divergence rule needs two, and two spare
allow the "most recent qualifying pair" search without unbounded growth.

## 8. Tests

[`../tests/RSI_TESTS.md`](../tests/RSI_TESTS.md), vectors `tests/vectors/rsi.json`:

* a monotonically rising close series → `RSI: Bullish`, and **never** a divergence string;
* a hand-built lower-low-in-price / higher-low-in-RSI series → `BULL_DIV`, active exactly
  from `secondPivotBar + 5`, and **not** on `secondPivotBar + 4`;
* the mirror for `BEAR_DIV`;
* a divergence whose pivots are 3 bars apart → rejected (below the minimum);
* a divergence whose pivots are 80 bars apart → rejected (above the maximum);
* divergence expiry after exactly 10 bars;
* precedence: a bar that is both oversold and bull-divergent reports divergence;
* bars 1–14 → `RSI: n/a (warming up)` and RSI excluded from `maxScore`;
* a live/forming bar never flips an already-emitted historical divergence state.

## 9. Open questions for supplied specifications

| # | Question | Until answered |
| --- | --- | --- |
| 1 | Are 70/30 the intended levels, or per-pattern? | 70/30 (`CV-RSI-001`) |
| 2 | Pivot length 5/5 — acceptable on daily and on 1m? | 5/5 everywhere, single input |
| 3 | How long should a divergence stay valid? | 10 bars (`CV-RSI-006`) |
| 4 | Do any patterns require RSI as **mandatory** rather than confluence? | none; confluence only, per `MASTER_SPECIFICATION.md` §1.1 |
| 5 | Should hidden/continuation divergence be supported? | no — not specified, not invented |

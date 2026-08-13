# DISPLAY ENGINE (L8)

Chart output. Abbreviations only on the chart; everything else in the tooltip.

---

## 1. Purpose

Put the minimum on the chart and the maximum in the hover, so a chart with fifty active
pattern definitions stays readable.

## 2. Contract

**Inputs:** the emitted event (pattern id, status, factors, score, band, structural
measurements, levels), display inputs (debug mode, status marks, label size, panel on/off).

**Outputs:** one label per detection with a rewritten tooltip on resolution; one optional info
panel; alert payload strings.

## 3. Label

| Property | Rule |
| --- | --- |
| Text | the **abbreviation only** — `HAM`, `BEC`, `PL`, `MS`, `MDS`, `ES`, `EDS`, `TWS`, `TBC`, `THRU`, … `[OWNER]` |
| Full name on chart | **only** when `Debug mode` is on `[OWNER]` |
| Position | bullish below the bar, bearish above, neutral above `[ENGINE-DEFAULT]` `CV-DISP-001` |
| Anchor bar | the pattern's **last candle**, never the resolution bar |
| Colour | by direction: bullish / bearish / neutral `[ENGINE-DEFAULT]` `CV-DISP-002` |
| Size / opacity | by validation band — stronger bands drawn larger / more opaque `CV-DISP-002` |
| Status in text | **no** — status lives in the tooltip |
| Optional status mark | when `Show status marks` is on: `✓` confirmed, `✗` failed, `·` expired, appended to the abbreviation `CV-DISP-003` |

Status is kept out of the label text by default because `BEC CONFIRMED` on every signal
recreates exactly the clutter the abbreviation rule exists to prevent. The one-character mark
is the compromise, off by default.

Multiple patterns on one bar: labels are offset vertically by ATR fractions so they do not
overlap `[ENGINE-DEFAULT]` `CV-DISP-006`. A cap of 4 labels per bar per side applies; beyond
that the count is shown (`+2`) and the full list appears in the panel. Bounded so a
pattern-dense bar cannot consume the label budget.

## 4. Tooltip — exact format `[OWNER]`

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

Then, after a blank line, the structural block `[ENGINE-DEFAULT]` `CV-DISP-004`:

```
── Structure ──
Body: 68.2% of range
Upper wick: 6.1% · Lower wick: 25.7%
Penetration: 71.4% of previous body
Gap: none
Rel. body: 1.8× avg(20)
Confirm: close > 1.10842 within 3 bars
Resolved: +2 bars
Timeframe: 1H (class HOUR_LOW, allowed)
```

### 4.1 Tick rules

* `✓` marks a factor that **passed** for this pattern's direction.
* A factor that did not pass is printed **without** a tick and without a cross — exactly like
  the owner's `RSI: Neutral` line. It is never omitted, so the block always has the same six
  lines and the same shape.
* An excluded factor prints `n/a` plus its reason: `Volume: n/a (no volume data)`,
  `RSI: n/a (warming up)`, `Location: n/a (unclear)`.
* A contradicting factor is printed plainly (`Trend: Uptrend`) and, if it triggered a cap, the
  validation line says so: `Validation: MODERATE (capped: trend opposes)`.

Contrast with the owner's two examples: identical structure, RSI line changing from
`Bullish divergence ✓` to `Neutral`, and the validation line moving `STRONG` → `MODERATE`
without any other line changing. That property — one factor changing exactly one line — is what
the fixed shape buys.

### 4.2 Line-by-line source

| Line | Source |
| --- | --- |
| abbreviation, full name | registry |
| `Status:` | [`CONFIRMATION_ENGINE.md`](CONFIRMATION_ENGINE.md) |
| `Pattern: Valid ✓` | precondition, always ✓ when a label exists |
| `Trend:` | [`TREND_ENGINE.md`](TREND_ENGINE.md) `trendText` |
| `Location:` | [`LOCATION_ENGINE.md`](LOCATION_ENGINE.md) `locText` |
| `RSI:` | [`RSI_ENGINE.md`](RSI_ENGINE.md) `rsiText` |
| `EMA:` | [`EMA_ENGINE.md`](EMA_ENGINE.md) `emaText` |
| `Volume:` | [`VOLUME_ENGINE.md`](VOLUME_ENGINE.md) `volText` |
| `Validation:` | [`VALIDATION_ENGINE.md`](VALIDATION_ENGINE.md) band + cap |
| structure block | [`OHLC_ENGINE.md`](OHLC_ENGINE.md) / [`RELATIONSHIP_ENGINE.md`](RELATIONSHIP_ENGINE.md), captured at detection |
| `Timeframe:` | [`TIMEFRAME_ENGINE.md`](TIMEFRAME_ENGINE.md) `tfText` |

Factor strings are produced by the engines, not re-worded here, so the tooltip cannot disagree
with the score.

### 4.3 Values are frozen at detection

The structural numbers are captured when the pattern is detected and never recomputed. A
tooltip read 200 bars later shows what was true at that bar.

The only field that changes after creation is `Status:` (and `Resolved: +n bars`), which is the
state machine advancing — see [`CONFIRMATION_ENGINE.md`](CONFIRMATION_ENGINE.md) §10.

### 4.4 Test mode

While `TEST MODE` is on, every tooltip gains a first line:

```
TEST MODE: timeframe/context gating bypassed
```

So a screenshot cannot be mistaken for normal operation.

### 4.5 Supplied narrative

If `Show supplied description` is on, the pattern's supplied tooltip description is appended
last, under a `── Supplied ──` heading, and any supplied statistic is printed with its
attribution: `Reliability: ±72% (User-provided reference)`
(`MASTER_SPECIFICATION.md` §14).

## 5. Info panel `[ENGINE-DEFAULT]` `CV-DISP-005`

One table, top-right by default, written **only** on the last bar. Contents:

```
CANDLESTICK MASTER            [TEST MODE]
Timeframe   1H · HOUR_LOW · enforcement CLASS
Trend       Downtrend (strength 2)
RSI         28.4 · Oversold
EMA         20>50, below 200 (bullish alignment: no)
Volume      1.4× avg(20) · tick volume
Location    Support · 1.10420 · 2 touches
Patterns    enabled 0/0 · allowed here 0
Events      detected 0 · confirmed 0 · failed 0 · expired 0
Warm-up     ema200 12/200 · pivots 4
```

Diagnostic, not decorative: every "why is nothing showing?" question is answered by one of
these rows — wrong timeframe, warming up, everything filtered out, or nothing detected.

Written on `barstate.islast` only, so it costs nothing on history.

## 6. Alert payloads

| Kind | Mechanism | Payload |
| --- | --- | --- |
| Per pattern per state | `alert()`, `alert.freq_once_per_bar_close` | `CM \| BEC \| CONFIRMED \| EURUSD 60 \| Validation: STRONG \| 1.10842` |
| Aggregate | `alertcondition` series | fixed titles, see `MASTER_SPECIFICATION.md` §11.3 |

No alert places, modifies, or closes an order. The script contains no strategy calls
`[OWNER]`.

## 7. Resource discipline

| Item | Budget |
| --- | --- |
| Labels | `max_labels_count = 500`; one per detection, ≤ 4 per bar per side |
| Boxes / lines | 0 |
| Tables | 1, last bar only |
| Plots | none required; a plot is used only if a debug series is enabled |
| String building | only for a pattern that actually fired — never for all patterns every bar |

Tooltip strings are the main hidden cost in a script like this: building a 20-line string for
50 patterns on every bar would be catastrophic. Strings are built **only** at detection and at
resolution ([`../ARCHITECTURE.md`](../ARCHITECTURE.md) §6).

## 8. Tests

Manual checks recorded in [`../tests/PATTERN_TESTS.md`](../tests/PATTERN_TESTS.md), since
labels and tooltips cannot be asserted outside TradingView:

* label text is the abbreviation only, in every mode except debug;
* the tooltip block is always six factor lines, in the owner's order, with the exact strings;
* the two owner examples reproduced verbatim from real chart events;
* one factor changing alters exactly one line plus the validation line;
* excluded factors print `n/a` with a reason;
* status rewrite on resolution leaves the label at its original bar;
* 5+ patterns on one bar → offsets applied, cap and `+n` shown;
* panel shows the correct warm-up and filter counts when nothing is displayed;
* test-mode banner present in panel and in every tooltip.

## 9. Open questions for supplied specifications

| # | Question | Until answered |
| --- | --- | --- |
| 1 | Should the status mark suffix be on by default? | off (§3) |
| 2 | Is the structural block wanted in the tooltip, or the six factors only? | included (`CV-DISP-004`) |
| 3 | Preferred label colours / sizes? | direction colours, size by band (`CV-DISP-002`) |
| 4 | Should supplied descriptions and statistics show by default? | off; attribution mandatory when on |

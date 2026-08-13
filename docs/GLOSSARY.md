# GLOSSARY

Exact meanings, so that two documents cannot use one word for two things.

Where a term has a common ambiguity, the ambiguity is named explicitly rather than resolved by
context.

---

## Candle geometry

| Term | Exact meaning | Not to be confused with |
| --- | --- | --- |
| **Range** | `high - low`. The full extent of the candle. | Body. "Candle size" in a spec usually means range, but is flagged when unclear. |
| **Body** | `abs(close - open)`. | Range. |
| **Real body** | Same as body. Both spellings appear in supplied text. | — |
| **Upper wick** | `high - max(open, close)`. Also *upper shadow*, *upper tail*. | Distance from the high to the close, which differs on a bearish candle. |
| **Lower wick** | `min(open, close) - low`. | Distance from the low to the close. |
| **Body top / bottom** | `max(open, close)` / `min(open, close)`. | High / low. |
| **Candle midpoint** | `(high + low) / 2` — the middle of the **range**. | Body midpoint. **These are different numbers.** |
| **Body midpoint** | `(open + close) / 2` — the middle of the **body**. | Candle midpoint. |
| **50% level** | Ambiguous on its own. In this project it defaults to the **body** midpoint (`CV-REL-002`) and every use states which. | — |
| **Close position** | `(close - low) / range` — where in the range the candle closed, `0..1`. | Body percentage. |
| **Body percentage** | `body / range`, `0..1`. | Body size in price units. |
| **Degenerate candle** | `range == 0`: all four prices equal. Every pattern rejects it. | Doji, which has a range but a tiny body. |
| **Flat candle** | `close == open` exactly. Neither bullish nor bearish. | Doji, which is a *threshold* class (`bodyPct <= 0.10`). |

## Relationships

| Term | Exact meaning | Note |
| --- | --- | --- |
| **Engulf (body)** | The newer body covers the older body: `bodyTop(a) >= bodyTop(b) and bodyBottom(a) <= bodyBottom(b)`. | Four variants exist — body/range × inclusive/strict (`CV-REL-001`). |
| **Engulf (range)** | The newer range covers the older: `H(a) >= H(b) and L(a) <= L(b)`. Also *wick engulfment*. | Strictly stronger than body engulfment. |
| **Harami / inside** | The newer body is inside the older body. Exact inverse of body engulfment with arguments swapped. | *Inside bar* usually means **range** containment. |
| **Penetration** | How far the newer close reaches into the older **body**, as a fraction of that body. `0.5` = halfway, `1.0` = at the far end, `> 1.0` = beyond. | Undefined (`na`) when the older candle has no body. |
| **True gap** | Ranges do not overlap: `L(a) > H(b)` or `H(a) < L(b)`. | Body gap. |
| **Body gap** | Bodies do not overlap; wicks may: `bodyBottom(a) > bodyTop(b)`. | True gap. Star-family patterns usually mean this one. |

## Context

| Term | Exact meaning | Note |
| --- | --- | --- |
| **Uptrend / Downtrend** | The states defined in `CV-TREND-002/003` — EMA alignment **and** slope **and** price position. | Not "price went up recently". |
| **Sideways** | `CV-TREND-004`: EMA compression **and** flat slope. | Not the absence of a trend label. |
| **Unclear (trend)** | None of the three states holds. A real answer, not an error. | Sideways. |
| **Clear trend** | `CV-TREND-006`: the state plus `trendStrength >= 2`. | The unqualified word "trend". |
| **Trend strength** | An integer `0..3` counting three named conditions. | A percentage. There is none. |
| **RSI momentum** | `rsi > 50 and rising` (or the mirror). Tooltip: `RSI: Bullish`. | **Divergence.** Never labelled as such. |
| **RSI divergence** | Two confirmed pivots where price and RSI disagree (`CV-RSI-003`…`007`). Tooltip: `RSI: Bullish divergence ✓`. | Momentum. |
| **EMA reclaim** | Close is above the EMA **and** the crossing happened within `reclaimWindow` closed bars (`CV-EMA-001`). | **Being above the EMA**, which is `EMA: Above 20 EMA`. |
| **EMA rejection** | Wick through the EMA with a close back on the original side, or a recent crossunder (`CV-EMA-002`). | A single close on the other side. |
| **EMA alignment** | `ema20 > ema50 > ema200` or the mirror. A configuration. | A crossing event. |
| **Volume** | What the chart's volume series reports. | Traded size across all venues. |
| **Tick volume** | The number of price updates a **broker's own feed** produced. Standard on forex/CFD. | Market volume. The wording always says "tick volume" when this is the source. |
| **Support / Resistance** | A confirmed pivot level within `0.5 × ATR` of the candle's low / high (`CV-LOC-001`). | A drawn zone. Nothing is drawn. |
| **Demand / Supply** | The same, with `>= 2` touches (`CV-LOC-002`). **A touch count, nothing more.** | Order blocks, institutional orders, order-book depth. None of which is observable here. |
| **Major support** | `CV-LOC-006`: `>= 2` touches with one structurally significant pivot. | Any support level. |
| **Range position** | `(close - lowest(100)) / (highest(100) - lowest(100))`. | The candle's own range. |

## Lifecycle

| Term | Exact meaning |
| --- | --- |
| **Detected** | The structure was satisfied on a **closed** candle. Nothing more is claimed. |
| **Confirmed** | A later **closed** candle reached the trigger level. |
| **Failed** | A later **closed** candle reached the invalidation level. The pattern was negated. |
| **Expired** | The window elapsed with neither. **Nothing happened** — not a failure, and no failure alert. |
| **Trigger level** | The price that confirms, captured at detection and never recomputed. |
| **Invalidation level** | The price that fails it, likewise fixed at detection. |
| **Confirmation window** | The number of closed candles allowed to resolve it (`CV-CONF-002`). |
| **Terminal state** | `CONFIRMED` / `FAILED` / `EXPIRED` never change afterwards. |

## Validation

| Term | Exact meaning |
| --- | --- |
| **Factor** | One of six named context checks, each worth `+1`, `0`, or excluded. |
| **Excluded factor** | Unmeasurable here (no volume series, RSI warming up, location unclear). Lowers `maxScore`; never a pass, never a fail. |
| **Opposing factor** | A factor in a defined state pointing against the pattern. Triggers a cap, not a negative score. |
| **Score / maxScore / ratio** | Points earned / points available / their quotient. Bands are on the ratio. |
| **Band** | `WEAK` / `MODERATE` / `STRONG` / `VERY STRONG`. A count of agreement — **not** a probability, win rate, or expectancy. |
| **Cap** | An upper limit applied after the band is computed, when context contradicts the pattern. Shown in the tooltip. |
| **Mandatory context** | A contextual factor that a supplied specification explicitly **requires**. Failing it suppresses the pattern instead of lowering the score. |

## Project process

| Term | Exact meaning |
| --- | --- |
| **As Supplied** | §1 of a pattern file. The owner's text, verbatim and immutable. |
| **Machine rule** | The same rule expressed in engine notation, written beside the original. |
| **Conversion (`CV-`)** | A vague phrase turned into an explicit measurable rule, with an ID in `DEFINITION_CONVERSIONS.md`. |
| **Conflict (`CF-`)** | Two supplied rules that cannot both hold. Blocking. Never resolved by preference. |
| **Ambiguity (`AM-`)** | Understandable but not yet uniquely measurable. |
| **Missing (`MS-`)** | A required field was not supplied. |
| **Audit flag (`AF-`)** | The supplied rule is preserved and implemented as-is, with a note explaining why it looks technically wrong. |
| **User-provided reference** | The attribution attached to any supplied statistic. It never enters a calculation. |
| **Primary category** | The single category that determines the file location and the display filter. |
| **Secondary category** | An additional conceptual category. Recorded, but does not move the file. |
| **Repainting** | Presenting a historical signal that could not have been known at that bar. Forbidden. |
| **Status advance** | A label's `Status:` changing on a later closed bar. Permitted, and not repainting — the detection bar and the detection itself never change. |
| **Ideal timeframes** | **All** timeframes a specification lists. Never narrowed to one. |
| **Enforcement mode** | `OFF` / `CLASS` / `EXACT` — how strictly the ideal list gates display. |
| **Test mode** | Bypasses timeframe and context gating for verification. Always announced in the panel and in every tooltip. |

## Pine Script terms used in this repo

| Term | Meaning here |
| --- | --- |
| **Closed candle** | A bar for which `barstate.isconfirmed` is true. |
| **Forming bar** | The live, incomplete bar. Never produces a detection, a resolution, or an alert. |
| **Offset `[n]`** | Pine's history operator: `n` bars back. Offset `0` is the current candle. |
| **Confirmed pivot** | A pivot whose `right` bars have printed, so it is knowable. Usable only from `pivotBar + right`. |
| **Warm-up** | Bars before an indicator has enough history to be what it claims (20 for a 20-EMA, 200 for a 200-EMA). |
| **Registry** | The data table of patterns that drives display, filtering, gating, scoring, and alerts generically. |

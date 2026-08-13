# ARCHITECTURE

Candlestick Master — structural design of the engine stack, the data flow, and the
constraints Pine Script imposes on both.

Normative formulas live in [`MASTER_SPECIFICATION.md`](MASTER_SPECIFICATION.md).
This document describes *shape*: what depends on what, what is computed once, what runs
per pattern, and why.

---

## 1. Design rules

| # | Rule | Consequence in code |
| --- | --- | --- |
| A1 | **Structure before context.** A pattern's OHLC geometry is decided without ever reading RSI/EMA/volume/trend. | Detection functions take only candle measurements. Context is applied afterwards, by the validation engine. |
| A2 | **Compute once, reuse everywhere.** | All indicators (RSI, EMA×3, ATR, volume SMA, pivots, range extremes) are computed exactly once per bar in the engine layer. No pattern may call `ta.*`. |
| A3 | **One definition, one place.** | Body %, wick %, penetration %, gap tests, midpoints exist in exactly one function each. Duplicating a formula inside a pattern is a review failure. |
| A4 | **Data-driven registry.** | Patterns are rows in a registry (abbreviation, name, direction, category, timeframe list, confirmation parameters, toggle). Display, filtering, timeframe gating, scoring, and alerting are generic loops over that registry — they do not grow when patterns are added. |
| A5 | **Closed candles only.** | Every detection, confirmation, label, and alert is gated on `barstate.isconfirmed`. The forming bar never produces a state change. |
| A6 | **No future information.** | Pivot-derived features (divergence, location) are usable only from the bar on which the pivot becomes *confirmed*, never from the pivot bar itself. |
| A7 | **Fail closed.** | Missing/degenerate data (zero range, `na` volume, insufficient bars for EMA200) yields "unavailable", never a silent `true`. Unavailable factors are excluded from scoring, not scored as failures. |
| A8 | **Bounded work per bar.** | Loop counts are bounded by registry size and a capped pending-confirmation array. No unbounded growth, no `request.security` in the core path. |

---

## 2. Layer stack

Strictly one-directional. A layer may only read from layers above it.

```
                         ┌──────────────────────────────────────────┐
 L0  INPUT LAYER         │ inputs, toggles, filter mode, TF policy  │
                         └────────────────────┬─────────────────────┘
                                              │
                         ┌────────────────────▼─────────────────────┐
 L1  MEASUREMENT         │ OHLC_ENGINE        WICK_BODY_ENGINE      │
     (bar-local)         │ range, body, wicks, %s, close position,  │
                         │ classes: bull/bear/doji/small/large      │
                         └────────────────────┬─────────────────────┘
                                              │
                         ┌────────────────────▼─────────────────────┐
 L2  RELATIONSHIP        │ RELATIONSHIP_ENGINE  (n = 1..5 back)     │
     (bar-to-bar)        │ midpoints, engulfment, gaps, 50% rules,  │
                         │ penetration %, harami, open/close vs prev│
                         └────────────────────┬─────────────────────┘
                                              │
        ┌─────────────────────────────────────┼─────────────────────────────────────┐
        │                                     │                                     │
 ┌──────▼───────┐   ┌──────────────┐   ┌──────▼───────┐   ┌──────────────┐   ┌──────▼───────┐
 │ L3 CONTEXT   │   │ L3 CONTEXT   │   │ L3 CONTEXT   │   │ L3 CONTEXT   │   │ L3 CONTEXT   │
 │ TREND_ENGINE │   │ RSI_ENGINE   │   │ EMA_ENGINE   │   │VOLUME_ENGINE │   │LOCATION_ENG. │
 └──────┬───────┘   └──────┬───────┘   └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
        └─────────────────────────────────────┼─────────────────────────────────────┘
                                              │      (shared: ATR, pivots, EMA set)
 ┌────────────────────────────────────────────▼────────────────────────────────────────────┐
 │ L4  PATTERN LAYER   pure functions of L1 + L2 only.  bool structure_ok (+ levels)       │
 └────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │
 ┌────────────────────────────────────────────▼────────────────────────────────────────────┐
 │ L5  GATING          TIMEFRAME_ENGINE · pattern toggle · category/direction filter       │
 └────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │
 ┌────────────────────────────────────────────▼────────────────────────────────────────────┐
 │ L6  VALIDATION      CONFLUENCE scoring (L3 factors) → WEAK / MODERATE / STRONG / V.STRONG│
 └────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │
 ┌────────────────────────────────────────────▼────────────────────────────────────────────┐
 │ L7  LIFECYCLE       CONFIRMATION_ENGINE: pending queue, trigger / invalidation levels   │
 │                     DETECTED → CONFIRMED | FAILED | EXPIRED   (closed bars only)        │
 └────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │
 ┌────────────────────────────────────────────▼────────────────────────────────────────────┐
 │ L8  OUTPUT          DISPLAY_ENGINE (abbreviation label + tooltip, panel) · ALERTS       │
 └─────────────────────────────────────────────────────────────────────────────────────────┘
```

**Why L4 sits below L3 but does not read it:** context engines are computed before the
pattern layer in *source order* (Pine needs the series defined), but pattern functions are
forbidden by A1 from taking them as arguments. The dependency is enforced by signature:
detection functions receive only measurement/relationship values.

---

## 3. Per-bar execution order

Exactly one pass, top to bottom, for every bar:

```
 1. read inputs                                     (once, global scope)
 2. build registry                                  (once, on barstate.isfirst)
 3. resolve timeframe permissions per pattern        (once, TF is constant per chart)
 4. measurements            L1
 5. relationships           L2
 6. shared indicators       ATR, EMA20/50/200, RSI, volume SMA, pivots
 7. context states          L3   → trend, rsi, ema, volume, location descriptors
 8. pattern structure       L4   → one bool (+ optional levels) per pattern
 9. resolve pending queue   L7   → confirm / fail / expire, update existing labels
10. emit new detections     L5→L6→L7→L8 (gated on barstate.isconfirmed)
11. aggregate alert flags   L8   (global scope, for alertcondition)
12. info panel              L8   (last bar only)
```

Steps 9 **before** 10 on purpose: the bar that confirms an older pattern may itself be a
new pattern. Resolving first keeps the two events independent and correctly ordered.

---

## 4. The pattern registry (A4)

One row per pattern, built once. Fields:

| Field | Type | Used by |
| --- | --- | --- |
| `id` | int (index) | everything |
| `abbr` | string | label text, alerts |
| `name` | string | tooltip, debug label |
| `dir` | int `+1/0/-1` | direction filter, colour, confirmation polarity |
| `cat` | string | category filter |
| `tfs` | string, CSV of canonical minutes | timeframe engine |
| `tfOk` | bool | resolved once |
| `enabled` | bool | per-pattern toggle |
| `reqTrend` | int `+1/0/-1` | validation (trend factor), mandatory-trend rule |
| `confirmBars` | int | confirmation window |
| `needsVol` / `needsRsi` … | bool | mandatory-factor rule (only when a spec says *mandatory*) |

Adding a pattern = one registry row + one detection function + one `emit()` call. No
change to display, filtering, scoring, lifecycle, or alerting code. This is the property
that makes 50+ patterns tractable inside Pine.

---

## 5. No-repaint design

| Mechanism | Implementation |
| --- | --- |
| Detection | evaluated only when `barstate.isconfirmed` — i.e. on a fully closed candle. |
| Confirmation | requires a *later* fully closed candle. Never the forming bar. |
| Pivots | `ta.pivothigh/low(len, len)` is knowable only `len` bars after the pivot. The engine records `confirmedAtBar = pivotBar + len` and refuses to use the pivot before that bar. |
| RSI divergence | built from two pivots; the divergence is reported from `confirmedAtBar` of the *second* pivot onward, and only stays "active" for a bounded window. |
| Location | uses only pivots already confirmed by the current bar. |
| Historical labels | drawn at the bar where the information existed (`bar_index - offset`), not at the bar where it was noticed. |
| Alerts | `alert.freq_once_per_bar_close`; aggregate `alertcondition` series are only true on the bar of the state change. |

**Documented, unavoidable delays** (see `MASTER_SPECIFICATION.md` §12):

| Feature | Delay | Reason |
| --- | --- | --- |
| Pattern detection | end of the pattern's last candle | closed-candle rule |
| Confirmation | +1 to `confirmBars` closed candles | the confirming candle must close |
| Pivot availability | `pivotLen` bars | a pivot is not a pivot until the right side exists |
| RSI divergence | `pivotLen` bars after the second pivot | same |
| EMA200-dependent trend | first 200 bars use relaxed mode | insufficient history |

A label's *status text* legitimately changes after creation (`DETECTED` → `CONFIRMED`).
That is a state machine advancing on new closed bars, not repainting: the transition bar
is fixed, no historical bar's decision is revised, and nothing is back-dated.

---

## 6. Pine resource budget

Hard-ish limits Pine imposes, and the room reserved for each:

| Resource | Pine limit | Budget | Design response |
| --- | --- | --- | --- |
| Labels | 500 (`max_labels_count`) | 500 declared | One label per event, none per bar. Pending queue capped. Old labels are auto-culled by Pine (FIFO). |
| Boxes / lines | 500 each | **0 used** | Not used at all — no zone drawing. |
| Tables | 1 per script practical | 1 | Single optional info panel, written on `barstate.islast` only. |
| Local scopes / compiled size | ~1000 scopes, script length limits | keep detection functions flat | No nested `if` deeper than 2; booleans composed with `and`/`or`, not branches. |
| `request.*` calls | 40 | **0 in core** | Higher-timeframe context is *not* used unless a supplied spec mandates it; if it is, it is a single request reused by all patterns. |
| `ta.*` calls | counted per call site | ~15 total | Centralised in the engine layer (A2). 50 patterns add **zero** `ta.*` calls. |
| Loop iterations | 500k/bar practical | ≤ ~200/bar | Registry loop (≤ ~70) + pending loop (≤ 60) + pivot arrays (≤ 20). |
| `max_bars_back` | 5000 | default | No dynamic history access on `var`-held series; avoids the "requested too many bars back" class of error. |
| Arrays | fine | ≤ 10 arrays | Registry (parallel arrays / UDT array), pending queue, pivot level stores — all capped. |

Rejected designs and the reason:

* **One `alertcondition` per pattern per state** (~150+). Rejected: bloats the alert
  dialog and the compiled script. Replaced by `alert()` with structured messages plus a
  small set of aggregate `alertcondition` series (`MASTER_SPECIFICATION.md` §11).
* **A drawn zone per detected S/R level.** Rejected: box budget and visual noise.
  Location is reported in text.
* **Per-pattern indicator variants** (e.g. "Hammer RSI"). Rejected by A2.
* **Recomputing measurements inside each pattern.** Rejected by A3.
* **Storing full candle history in arrays.** Rejected: Pine's built-in history operator
  `[]` already does this for free up to `max_bars_back`.

---

## 7. Planned source layout of the Pine file

> **Not yet written.** Pine implementation is gated on the explicit instruction
> `ALL PATTERN DATA PROVIDED. BEGIN IMPLEMENTATION.` (see
> [`IMPLEMENTATION_GATE.md`](IMPLEMENTATION_GATE.md)). This section fixes the layout in
> advance so that batch work has a stable target.

Section banners are stable so that diffs and reviews stay legible:

```
 0  header, indicator(), version notes
 1  INPUTS
 2  TIMEFRAME ENGINE
 3  OHLC / WICK-BODY ENGINE
 4  RELATIONSHIP ENGINE
 5  SHARED INDICATORS
 6  TREND ENGINE
 7  RSI ENGINE (+ pivot divergence)
 8  EMA ENGINE
 9  VOLUME ENGINE
10  LOCATION ENGINE
11  VALIDATION / CONFLUENCE ENGINE
12  CONFIRMATION ENGINE (types, queue, resolution)
13  DISPLAY ENGINE (labels, tooltips, panel)
14  PATTERN REGISTRY
15  PATTERN LAYER  ← the only section that grows per batch
16  EMIT / GATING
17  ALERTS
18  INFO PANEL
```

Sections 0–14 and 16–18 are *fixed cost*. Batch work touches 14 (one row) and 15 (one
function) only.

---

## 8. Repo-side verification

Pine cannot be compiled outside TradingView, so the repo carries independent checks that
catch the errors a compiler would, before a paste.

**Available now (specification phase):**

1. `tools/spec_lint.py` — every pattern file contains all mandatory template fields; every
   registry row has a file and every file has a registry row; abbreviations are unique;
   timeframe lists use canonical tokens; `AUDIT FLAG` / ambiguity entries are
   cross-referenced in `CONFLICT_LOG.md`.
2. `tools/reference_model.py` + `tools/run_tests.py` — Python mirror of the L1/L2
   mathematics, executed against the numeric vectors in `tests/vectors/`. Every threshold
   later written into Pine must agree with these vectors.

**Lands with the first Pine batch:**

3. `tools/pine_lint.py` — heuristics: `//@version=6` present, banned pre-v6 constructs
   (`iff(`, `study(`, bare `security(`, bare `rsi(`, bare `crossover(`, `transp=`, legacy
   `input(`), bracket/quote balance, `input.*` and `alertcondition(` and `plot(` at global
   scope, `max_labels_count` declared when `label.new` is used, tab characters, trailing
   whitespace, line length.

None of these replaces the manual gate in `tests/PINE_COMPILE_CHECKLIST.md`.

# PATTERN TESTS

The test set **every** supplied pattern must have before it is implemented, plus the
display, alert, and resource checks that apply to the script as a whole.

> **No pattern tests exist yet** — no pattern specifications have been supplied. This document
> is the template and the standard, not a record of results.

---

## 1. The rule

Test vectors are written **from the supplied specification, before implementation**. Not after,
and never by running the implementation and recording what it did. A test written from the code
proves only that the code is self-consistent.

Each pattern gets `tests/vectors/<slug>.json` and a completed §2 table in its own pattern file
(template §19).

## 2. The seven mandatory cases

| # | Case | Constructed how | Expected |
| --- | --- | --- | --- |
| 1 | **VALID** | every supplied rule satisfied, comfortably inside each threshold | detected |
| 2 | **INVALID** | exactly **one** rule broken, everything else identical | not detected |
| 3 | **WRONG TREND** | valid structure, opposing trend context | detected; trend factor `0` or `oppose`; band capped. **Suppressed** only if the spec makes trend mandatory |
| 4 | **WRONG TIMEFRAME** | valid structure on a timeframe outside the ideal list | hidden in `EXACT` and `CLASS`; shown in `OFF` and `TEST MODE` |
| 5 | **FAILED CONFIRMATION** | valid, then a close beyond the invalidation level | `FAILED` |
| 6 | **SUCCESSFUL CONFIRMATION** | valid, then a close beyond the trigger level | `CONFIRMED` |
| 7 | **EDGE CASE** | see §3 | per case |

Case 2 is written **once per rule**: a five-rule pattern gets five INVALID vectors, each
breaking one rule. This is what catches a rule that was translated but never actually wired
into the condition — the most common silent implementation error, and one a single INVALID case
cannot detect.

## 3. Mandatory edge cases

Every pattern, whether or not its specification mentions them:

| # | Edge case | Expected |
| --- | --- | --- |
| E1 | each body ratio threshold, exactly at the boundary | passes (thresholds are inclusive) |
| E2 | each body ratio, one tick outside | fails |
| E3 | each wick ratio, at and outside the boundary | as specified |
| E4 | 50% penetration exactly at the level | per the pattern's own strictness — `>` fails, `>=` passes |
| E5 | gap exactly zero | not a gap |
| E6 | gap at the minimum required size | passes |
| E7 | zero-range candle anywhere in the pattern | **not detected** |
| E8 | flat candle (`close == open`) where a coloured candle is required | not detected, unless the spec allows it |
| E9 | previous candle is a doji where penetration is required | not detected (penetration undefined) |
| E10 | candles share a boundary (`open == previous close`) | per the pattern's engulfment strictness |
| E11 | the pattern's own candle count at the history limit (first bars of the chart) | not detected, no error |
| E12 | `EXPIRED` path: neither level reached in the window | `EXPIRED`, no failure alert |

E7 and E9 exist because both produce a *defined but meaningless* measurement, and a rule
written only against ratios can be satisfied by nonsense data.

## 4. Mathematical cases

For any pattern whose rules involve arithmetic, tested independently of the pattern:

| Quantity | Cases |
| --- | --- |
| body ratio | at, just below, just above each threshold |
| wick ratio | both idioms (range fraction and body multiple) where the spec is explicit; ambiguity logged where it is not |
| 50% penetration | `0.0`, `0.4999`, `0.5`, `0.5001`, `1.0`, `>1.0`, `<0`, undefined |
| gap | true gap, body gap, zero gap, gap in ATR units |
| OHLC relationships | engulfment ×4 variants, containment, opens/closes vs previous |

These are already covered generically in [`OHLC_TESTS.md`](OHLC_TESTS.md); a pattern adds only
the specific values **its** thresholds sit on.

## 5. Cross-pattern checks

Run after every batch, over all implemented patterns:

| # | Check | Why |
| --- | --- | --- |
| X1 | every previously implemented pattern still fires on its VALID vector | regression |
| X2 | patterns in a superset/subset relationship both fire, as documented in each file's §20 | a double signal must be expected, not a surprise |
| X3 | no two patterns share an abbreviation | label ambiguity |
| X4 | two similarly named patterns produce different results on a vector that distinguishes them | proves they were not silently merged |
| X5 | a pattern's rarity has not changed after a refactor | counts on a fixed 5000-bar history are recorded per pattern and compared |

X5 is the guard against the drift the owner warned about: quietly loosening a rule because too
few signals appeared. A changed count must be explained by a changed specification, not by
tuning.

## 6. Display checks (manual, TradingView)

| # | Check | Expected |
| --- | --- | --- |
| D1 | label text | abbreviation only |
| D2 | debug mode | full name appears; only then |
| D3 | label position | bullish below, bearish above, neutral above |
| D4 | tooltip shape | the exact block from `MASTER_SPECIFICATION.md` §10.2, always six factor lines |
| D5 | the owner's example 1 | reproduced verbatim from a real chart event |
| D6 | the owner's example 2 (RSI neutral) | identical except the RSI line and the validation line |
| D7 | excluded factor | prints `n/a` with a reason |
| D8 | capped validation | `Validation: MODERATE (capped: trend opposes)` |
| D9 | 5+ patterns on one bar | vertical offsets, max 4 per side, `+n` shown |
| D10 | structural block numbers | match the tooltip's own claims to 1 decimal |
| D11 | supplied statistic display | shown only when enabled, always as `User-provided reference` |
| D12 | info panel | correct warm-up, filter counts, and event counts; explains an empty chart |

## 7. Filter and toggle checks (manual)

| # | Check | Expected |
| --- | --- | --- |
| F1 | each of the nine filter modes | only the intended patterns are displayed |
| F2 | a filtered-out pattern's lifecycle | still tracked — un-hiding it mid-history shows correct statuses |
| F3 | per-pattern toggle off | that pattern alone disappears |
| F4 | all patterns off | clean chart, panel still reports state, no error |
| F5 | `Filter includes secondary categories` on | patterns with a matching secondary category also appear |

F2 matters because it distinguishes a display mask from a disabled engine, which is what
`MASTER_SPECIFICATION.md` §11.1 requires.

## 8. Alert checks (manual)

| # | Check | Expected |
| --- | --- | --- |
| A1 | `alert()` payload | `CM \| ABBR \| STATE \| symbol timeframe \| Validation: BAND \| price` |
| A2 | firing frequency | once per bar close, never intrabar |
| A3 | aggregate `alertcondition` list | the nine titles from `MASTER_SPECIFICATION.md` §11.3, all selectable |
| A4 | an `EXPIRED` pattern | no failure alert received |
| A5 | a filtered-out pattern | alert behaviour matches the documented decision (display mask vs alert mask) |
| A6 | no order is ever placed | the script contains no `strategy.*` call — verified by grep and by the absence of strategy inputs |

## 9. Resource checks (manual, after every batch)

| # | Check | Limit |
| --- | --- | --- |
| R1 | compiles with no error and no warning | — |
| R2 | label count on a 10k-bar history | ≤ 500 live, oldest culled without error |
| R3 | no `max_bars_back` error on any tested symbol | — |
| R4 | script load time on 1m and 1D charts | subjectively immediate; no timeout |
| R5 | `ta.*` call sites | matches the fixed list in `engines/README.md`; unchanged by the batch |
| R6 | loop iterations per bar | registry + pending queue only, both bounded |
| R7 | boxes / lines used | zero |
| R8 | `request.*` calls | zero |

R5 is the batch-over-batch discipline that keeps 50+ patterns affordable: adding a pattern must
not add an indicator call.

## 10. Recording results

Each batch appends a block to this file:

```
BATCH <n> - <date>
Patterns:            CM-0xx .. CM-0yy
Vectors:             <count> cases, <pass>/<fail>
Compile:             PASS (Pine v6, no warnings)
Regression (X1):     PASS - <count> previously implemented patterns re-verified
Repaint (M-series):  PASS - replay + reload identical
Resources:           labels <n>/500, ta.* <n>, loops <n>/bar
Rarity (X5):         <pattern>: <n> signals / 5000 bars  (previous: <n>)
Open issues:         <CONFLICT_LOG ids>
```

A batch with no recorded block has not been tested, whatever the code looks like.

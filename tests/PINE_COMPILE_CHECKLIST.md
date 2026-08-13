# PINE COMPILE CHECKLIST

The manual gate. Run in full after **every** implementation batch, and before any claim that
the script works.

Nothing outside TradingView can compile Pine. `tools/pine_lint.py` (which lands with the first
Pine batch) catches a useful subset of mistakes, and this checklist catches the rest.

---

## 0. Before pasting

| # | Check |
| --- | --- |
| 0.1 | `python3 tools/run_tests.py` passes |
| 0.2 | `python3 tools/spec_lint.py` passes |
| 0.3 | `python3 tools/pine_lint.py` passes |
| 0.4 | `CONFLICT_LOG.md` has no `BLOCKING` entry for any pattern in this batch |
| 0.5 | every threshold in the new code appears in a vector or in `docs/DEFINITION_CONVERSIONS.md` |

## 1. Language and declaration

| # | Check | Note |
| --- | --- | --- |
| 1.1 | `//@version=6` is the first line | |
| 1.2 | `indicator(...)` with `overlay = true` and `max_labels_count = 500` | |
| 1.3 | no pre-v6 constructs: `study(`, `iff(`, bare `security(`, bare `rsi(`/`sma(`/`crossover(`, `transp=`, legacy `input(` | all namespaced (`ta.`, `math.`, `str.`, `request.`) |
| 1.4 | no invented functions or parameters | every call checked against the official v6 reference |
| 1.5 | no `strategy.*` call anywhere | this indicator never trades |

## 2. Types and `na`

| # | Check | Why it matters in v6 |
| --- | --- | --- |
| 2.1 | no boolean can be `na` at a decision point | v6 does not collapse `na` to `false`; a comparison against an `na` float yields `na` |
| 2.2 | every division has a guarded denominator | zero range, zero previous body, zero volume average |
| 2.3 | explicit availability flags (`isMeasurable`, `rsiReady`, `ema200Ready`, `volReady`, `locReady`) rather than `na` checks on values | a seeded EMA is non-`na` and still wrong |
| 2.4 | `nz()` used only where a documented default exists | not as a blanket silencer |
| 2.5 | int/float and series/simple types match every parameter's requirement | `length` arguments need `simple int` |
| 2.6 | string concatenation only on non-`na` strings | |

## 3. History and indexing

| # | Check |
| --- | --- |
| 3.1 | history depth used is within the declared limit (offsets 0–5 unless raised deliberately) |
| 3.2 | candle *k* of an *n*-candle pattern maps to offset `n - k`, verified per pattern |
| 3.3 | no history access on a `var`-held variable that could exceed `max_bars_back` |
| 3.4 | first-bars behaviour verified on a fresh symbol: no error, no false detection |
| 3.5 | no `[]` offset inside a loop whose bound is a series value |

## 4. Repainting

| # | Check |
| --- | --- |
| 4.1 | every detection is gated on `barstate.isconfirmed` |
| 4.2 | every resolution is gated the same way |
| 4.3 | no pivot is read before `pivotBar + right` |
| 4.4 | no `request.*` with `lookahead_on` |
| 4.5 | replay mode, bar by bar: state changes happen on the bars the tooltips claim |
| 4.6 | reload the chart: identical labels at identical bars |
| 4.7 | a live forming bar produces no label, no status change, and no alert |

## 5. Timeframe

| # | Check |
| --- | --- |
| 5.1 | 1m, 5m, 15m, 45m, 1H, 2H, 4H, 1D, 1W, 1M — all load without error |
| 5.2 | visibility matches `tests/TIMEFRAME_TESTS.md` §2 on each |
| 5.3 | a seconds chart and a tick chart load without error |
| 5.4 | `TEST MODE` overrides enforcement and shows its banner |
| 5.5 | the info panel timeframe row is correct on each |

## 6. Labels and tooltips

| # | Check |
| --- | --- |
| 6.1 | abbreviation only on the chart |
| 6.2 | tooltip matches `MASTER_SPECIFICATION.md` §10.2 exactly, including the `✓` placement |
| 6.3 | excluded factors print `n/a` with a reason |
| 6.4 | several patterns on one bar: offsets applied, cap respected |
| 6.5 | 10k-bar history: labels culled by Pine without error |
| 6.6 | no label is created on a filtered-out or disabled pattern |

## 7. Alerts

| # | Check |
| --- | --- |
| 7.1 | every `alertcondition` is at global scope |
| 7.2 | the nine aggregate conditions appear in the alert dialog with the documented titles |
| 7.3 | `alert()` fires once per bar close with the documented payload |
| 7.4 | an `EXPIRED` pattern fires no failure alert |

## 8. Resources

| # | Check | Target |
| --- | --- | --- |
| 8.1 | compile time and load time | no timeout on 1m or 1D |
| 8.2 | `ta.*` call sites | matches `engines/README.md`; unchanged by the batch |
| 8.3 | loop iterations per bar | registry + pending queue only |
| 8.4 | labels | ≤ 500 declared and respected |
| 8.5 | boxes, lines, plots | 0, 0, and only debug plots |
| 8.6 | `request.*` | 0 |
| 8.7 | tables | 1, written on `barstate.islast` only |

## 9. Regression

| # | Check |
| --- | --- |
| 9.1 | every previously implemented pattern still fires on its VALID vector |
| 9.2 | previously recorded signal counts on a fixed 5000-bar history are unchanged, or the change is explained by a specification change |
| 9.3 | no previously passing manual check has regressed |

## 10. If TradingView reports an error

The procedure, per `MASTER_SPECIFICATION.md` §13 and the owner's §23:

1. **Do not patch the reported line.** The reported line is where the parser gave up, which is
   frequently not where the mistake is.
2. Read the **preceding** statements: an unclosed bracket, a bad indent, a missing
   continuation, or a type mismatch introduced earlier.
3. Identify the **root cause** and state it before editing.
4. Fix the cause, then **re-check the whole module**, not just the line.
5. Re-run this checklist from §1 for the affected module, then look for secondary errors the
   first one was masking.
6. Only then re-paste.

## 11. Sign-off

A batch is complete when every box above is checked **and** the result block is recorded in
[`PATTERN_TESTS.md`](PATTERN_TESTS.md) §10. Until then the batch is in progress, regardless of
how the chart looks.

The script is never described as "complete" or "working" on the strength of a successful
compile alone. A compile proves the syntax; §§4–9 prove the behaviour.

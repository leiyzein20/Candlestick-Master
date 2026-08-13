# PATTERN REGISTRY

The single authoritative index of every pattern in Candlestick Master.

If a pattern is not in the table in §5, it does not exist as far as the engine, the
settings dialog, the filters, the alerts, and the tests are concerned.

`tools/spec_lint.py` enforces the invariants in §4.

---

## 1. Row schema

Every registry row carries exactly these columns.

| Column | Type | Rules |
| --- | --- | --- |
| `ID` | `CM-###` | Assigned in arrival order, never reused, never renumbered. |
| `ABBR` | 2–4 uppercase chars | Unique across the whole registry. Chart label text. |
| `Name` | string | Full name, exactly as supplied. |
| `Dir` | `Bullish` / `Bearish` / `Neutral` | From the supplied specification. |
| `Primary` | `Reversal` / `Continuation` / `Exhaustion` / `Neutral` / `Gap` | One value only. Routing key. |
| `Secondary` | list or `—` | Additional conceptual categories. Never affects the file location. |
| `Candles` | int | Number of candles the structure spans. |
| `Timeframes` | CSV of canonical tokens | **All** ideal timeframes. Never a subset. |
| `File` | path | `patterns/<dir>/<slug>.md` |
| `Status` | see §2 | Lifecycle of the specification, not of a trade. |
| `Flags` | list or `—` | `CF-`/`AM-`/`MS-`/`AF-` IDs from `CONFLICT_LOG.md`. |

Machine-only fields, held in the pattern file's front-matter rather than this table (they
would make it unreadable): `reqTrend`, `mandatoryContext`, `confirmBars`, `triggerLevel`,
`invalidationLevel`, `rsiRule`, `emaRule`, `volRule`, `locationRule`, `riskClass`,
`reliabilityClass`.

## 2. Status values

| Status | Meaning |
| --- | --- |
| `RECEIVED` | Supplied text captured verbatim; not yet translated into machine rules. |
| `SPECIFIED` | Machine rules written; all fields present; no blocking flags. |
| `BLOCKED` | Held by a `BLOCKING` entry in `CONFLICT_LOG.md`. Not implementable. |
| `TESTS-READY` | Test vectors written (`tests/vectors/`), expected results agreed. |
| `IMPLEMENTED` | Present in the Pine file and compiling. |
| `VERIFIED` | Batch gate passed: compile, indexing, repaint, timeframe, label, alert, resource, regression. |

A pattern may only reach `IMPLEMENTED` from `TESTS-READY`, and `TESTS-READY` from
`SPECIFIED`. `BLOCKED` short-circuits everything.

## 3. Abbreviation policy

1. Abbreviations are **unique**. `tools/spec_lint.py` fails the build on a duplicate.
2. If a supplied specification names an abbreviation, that abbreviation is used as given.
3. If two supplied patterns claim the same abbreviation, **neither is renamed**. A `CF-`
   entry is raised in `CONFLICT_LOG.md` and both patterns are held at `BLOCKED` until the
   owner decides (§1.14 of `CONFLICT_LOG.md`, `SI-14`).
4. If no abbreviation is supplied, one is derived — initials of the significant words,
   2–4 characters, uppercase — and marked `derived` in the pattern file so it is obvious
   the owner did not choose it.
5. Abbreviations are the only text allowed on a chart label
   (`MASTER_SPECIFICATION.md` §10.1).

### 3.1 Reserved abbreviations

These strings appeared in the owner's chart-label examples. They are **reserved** so that
no derived abbreviation can collide with them.

| Reserved | Expansion |
| --- | --- |
| `HAM` | Owner example: "Hammer" (the only one stated in prose). |
| `BEC` | Owner example: "Bullish Engulfing" (stated in the tooltip example). |
| `PL` | Owner example: "Piercing Line" (named in the Phase 1 list). |
| `MS` | **Unconfirmed.** Reserved, expansion pending the supplied specification. |
| `MDS` | **Unconfirmed.** Reserved, expansion pending. |
| `ES` | **Unconfirmed.** Reserved, expansion pending. |
| `EDS` | **Unconfirmed.** Reserved, expansion pending. |
| `TWS` | **Unconfirmed.** Reserved, expansion pending. |
| `TBC` | **Unconfirmed.** Reserved, expansion pending. |
| `THRU` | **Unconfirmed.** Reserved, expansion pending. |

No expansion is assumed for the seven unconfirmed entries. Guessing them (however
conventional the guess) would be inventing a pattern definition, which
`MASTER_SPECIFICATION.md` §1.2 forbids. Each becomes a normal registry row when its
specification arrives.

## 4. Invariants

Checked by `tools/spec_lint.py`:

* `ID` unique, contiguous, `CM-` prefixed.
* `ABBR` unique, 2–4 chars, `A-Z` only, not colliding with §3.1 unless it *is* that pattern.
* `File` exists, and its front-matter `id` / `abbr` / `dir` / `primary` match this table.
* `File` sits in the directory demanded by `patterns/CLASSIFICATION.md` for
  (`Dir`, `Primary`).
* `Timeframes` contains only canonical tokens (`MASTER_SPECIFICATION.md` §6) and is
  non-empty.
* `Candles` ≥ 1 and equals the number of candles described in the pattern file's structure
  block.
* Every `Flags` ID exists in `CONFLICT_LOG.md`, and every `CONFLICT_LOG.md` entry naming a
  pattern appears in that pattern's `Flags`.
* No pattern is `IMPLEMENTED` while any of its flags is `BLOCKING`.
* Every pattern file contains all mandatory template sections
  (`patterns/SPEC_TEMPLATE.md`).

## 5. Registry

> **Empty by design.** Awaiting the supplied pattern specifications. Rows are added on
> intake, in arrival order.

| ID | ABBR | Name | Dir | Primary | Secondary | Candles | Timeframes | File | Status | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| *(none yet)* | | | | | | | | | | |

### 5.1 Counters

| Metric | Count |
| --- | --- |
| Total patterns | 0 |
| Bullish / Bearish / Neutral | 0 / 0 / 0 |
| Reversal / Continuation / Exhaustion / Neutral / Gap | 0 / 0 / 0 / 0 / 0 |
| `RECEIVED` | 0 |
| `SPECIFIED` | 0 |
| `BLOCKED` | 0 |
| `TESTS-READY` | 0 |
| `IMPLEMENTED` | 0 |
| `VERIFIED` | 0 |

### 5.2 Timeframe coverage

Filled in as patterns arrive. Its purpose is to answer, at a glance, "what does this
indicator actually show on a 15m chart?" — and to catch a batch that accidentally
concentrated on one timeframe.

| Timeframe | Patterns allowed (`EXACT` mode) | Patterns allowed (`CLASS` mode) |
| --- | --- | --- |
| 1m … 1M | 0 | 0 |

## 6. Change discipline

* Adding a pattern: append a row, create the file, add the toggle, add test vectors,
  update §5.1. Nothing else in the engine changes (`ARCHITECTURE.md` §4).
* Editing a supplied rule: not permitted without an owner instruction. The *As Supplied*
  block is immutable; corrections live in the machine-rules block with an `AF-` flag.
* Removing a pattern: status → `WITHDRAWN`, row kept, ID never reused.

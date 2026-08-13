# INTAKE PROCEDURE

What happens to every supplied pattern specification, in order. Mechanical by design: the
same input always produces the same filing, so no round-trip questions are needed except
the genuine contradictions listed in [`CLASSIFICATION.md`](CLASSIFICATION.md) §5.1.

---

## 0. Capture before anything else

The supplied text is pasted **verbatim** into §1 of the new pattern file before any
analysis. Typos, formatting, ordering, and any statistics are preserved. Nothing is
paraphrased at this step, because a paraphrase made during intake is indistinguishable from
a paraphrase made by mistake later.

If one message contains several patterns, each gets its own file. Splitting a message is
allowed; editing its content is not.

## 1. The twelve steps

| # | Step | Output | Reference |
| --- | --- | --- | --- |
| 1 | Determine the correct directory | routing decision | `CLASSIFICATION.md` §2 |
| 2 | Create the pattern specification file | `patterns/<dir>/<slug>.md` from `SPEC_TEMPLATE.md` | — |
| 3 | Add it to the registry | row in `PATTERN_REGISTRY.md` §5 | `PATTERN_REGISTRY.md` §1 |
| 4 | Assign the abbreviation | `abbr`, `abbr_derived` | `PATTERN_REGISTRY.md` §3 |
| 5 | Record the candle count | `candle_count` + §4 candle table | template §4 |
| 6 | Record **all** ideal timeframes | `timeframes` + §5 table | `MASTER_SPECIFICATION.md` §6 |
| 7 | Record structural OHLC rules | template §§7–12 | `MASTER_SPECIFICATION.md` §§3–4 |
| 8 | Record contextual requirements | template §§6, 13 | `MASTER_SPECIFICATION.md` §§5, 7 |
| 9 | Record confirmation rules | template §14 | `MASTER_SPECIFICATION.md` §8 |
| 10 | Record failure conditions | template §15 | `MASTER_SPECIFICATION.md` §8 |
| 11 | Record RSI / EMA / volume validation | template §13 | `engines/{RSI,EMA,VOLUME}_ENGINE.md` |
| 12 | Record ambiguities **separately** | template §17 + `CONFLICT_LOG.md` | `CONFLICT_LOG.md` |

Steps 1–12 are completed for a pattern before the next pattern is started, so a partially
filed pattern never exists in a commit.

## 2. Translating a rule into a machine rule

For each rule in the supplied text:

1. **Quote it** in the relevant template section.
2. **Express it** in the notation of `MASTER_SPECIFICATION.md` §2, using only the
   centralised engine values — never a new formula (`ARCHITECTURE.md` A3).
3. **Classify the gap**, if the translation was not one-to-one:

| Situation | Action |
| --- | --- |
| The rule is already exact (`close > previous high`) | translate directly, no entry |
| The rule is vague but has a documented default (`"long lower wick"`) | apply the default, cite its `CV-` ID, add an `AM-` row in template §17 stating which reading was used |
| The rule is vague with **no** documented default | add an `AM-` entry, status `AWAITING OWNER`; pattern → `BLOCKED` |
| The rule contradicts another supplied rule | add a `CF-` entry; pattern → `BLOCKED`; **do not choose a side** |
| A required field is absent | add an `MS-` entry; structural fields → `BLOCKED` |
| The rule is clear but looks technically wrong | keep it exactly, add `AUDIT FLAG:` in template §18 + `AF-` entry; pattern stays implementable |

4. **Never** invent a threshold. If a number is needed and none exists, either a documented
   `[ENGINE-DEFAULT]` covers it (cite the ID) or it becomes an `AM-`.

## 3. The AUDIT FLAG rule

Applied when a supplied rule appears technically incorrect — unsatisfiable, self-negating,
arithmetically impossible, or describing something the data cannot express.

* The rule is **kept exactly as supplied** in §1 and translated as supplied in §§7–12.
* An `AUDIT FLAG:` block is added in §18 explaining the mechanical reason for the concern
  and its runtime consequence.
* The pattern remains implementable and is implemented as supplied.
* No wording is softened, no threshold nudged, no condition dropped.

Example of the mechanical style an audit flag uses (not a real pattern):

```
AUDIT FLAG:
Rule 3 requires bodyPct >= 0.70 while rule 5 requires lowerWickPct >= 0.40.
Since bodyPct + upperWickPct + lowerWickPct == 1 by construction, the two cannot both
hold (0.70 + 0.40 > 1). As supplied, this pattern can never fire. Preserved unchanged.
```

## 4. Cross-checks run after every batch

`python3 tools/spec_lint.py` must pass. It checks:

* every mandatory template section is present and non-empty;
* front-matter is valid and agrees with the registry row;
* the file is in the directory the routing table demands;
* abbreviations are unique and do not collide with the reserved list;
* timeframe tokens are canonical and the list is non-empty (or explicitly `NOT SUPPLIED`);
* `candle_count` matches the number of rows in the §4 candle table;
* every flag ID in a pattern file exists in `CONFLICT_LOG.md`, and every log entry naming a
  pattern is listed in that pattern's `flags`;
* no pattern is marked `IMPLEMENTED` while carrying a `BLOCKING` flag;
* every `CV-` ID cited exists in `docs/DEFINITION_CONVERSIONS.md`.

Then, manually:

* registry counters in `PATTERN_REGISTRY.md` §5.1 updated;
* duplicate-definition scan: does an arriving pattern have the same rules as an existing one
  under a different name? Similar names are **not** assumed to be the same pattern, and
  identical rules under two names are raised as a `CF-` rather than merged
  (`MASTER_SPECIFICATION.md` §1.2);
* superset/subset scan: if pattern B's rules are strictly implied by pattern A's, note it in
  both files' §20 so the double-signal is expected rather than surprising.

## 5. What intake never does

* Never asks where a file goes when the routing table answers it.
* Never rewrites, condenses, or "corrects" supplied trading rules.
* Never merges two similarly named patterns.
* Never drops a timeframe, a candle, a wick condition, or a statistic.
* Never resolves a contradiction by picking the more common convention.
* Never writes Pine Script (see [`../IMPLEMENTATION_GATE.md`](../IMPLEMENTATION_GATE.md)).

## 6. Batch report

After each delivered batch, the following is reported back:

```
BATCH <n> INTAKE REPORT
Patterns received:      <count>
Filed:                  <per directory>
Registry IDs:           CM-0xx .. CM-0yy
Abbreviations assigned: <list>  (derived: <list>)
Timeframes seen:        <union of tokens>
New CV- conversions:    <ids>
New flags:              CF-<n> BLOCKING, AM-<n>, MS-<n>, AF-<n>
Blocked patterns:       <ids + one-line reason>
Needs owner decision:   <ids + the question, phrased as options>
spec_lint:              PASS / FAIL (<detail>)
```

The "needs owner decision" list is the only thing that requires a reply; everything else is
already filed.

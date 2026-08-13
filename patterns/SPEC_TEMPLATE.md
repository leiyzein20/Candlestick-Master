# PATTERN SPECIFICATION TEMPLATE

Copy this file to `patterns/<dir>/<slug>.md` per
[`CLASSIFICATION.md`](CLASSIFICATION.md) and fill it in.

**Every section below is mandatory** and is checked by `tools/spec_lint.py`. A section with
no supplied content is written as `NOT SUPPLIED` — never deleted, never guessed, and it
generates an `MS-` entry in [`../CONFLICT_LOG.md`](../CONFLICT_LOG.md) if it is a structural
field.

Three rules govern editing a filled-in pattern file:

1. **§1 *As Supplied* is immutable.** It holds the owner's text verbatim, including
   typos, formatting, and any statistic. Nothing is reworded, reordered, condensed, or
   "cleaned up".
2. **Machine rules live in §4–§12, beside the original, never over it.** If a machine rule
   needed a decision the supplied text did not make, the decision is recorded in §14 and
   in `docs/DEFINITION_CONVERSIONS.md` — not applied silently.
3. **A rule that looks technically wrong stays as supplied**, with an `AUDIT FLAG:` note
   directly beneath it in §15. It is implemented as supplied unless the owner says
   otherwise.

---

```yaml
# ── front-matter: machine fields (kept out of PATTERN_REGISTRY.md for readability) ──
id: CM-000                    # assigned on intake, never reused
abbr: XXX                     # 2-4 uppercase; 'derived: true' if not owner-supplied
abbr_derived: false
name: ""                      # full name, exactly as supplied
direction: ""                 # Bullish | Bearish | Neutral
primary_category: ""          # Reversal | Continuation | Exhaustion | Neutral | Gap
secondary_categories: []      # e.g. [Gap, Reversal]
classification_rung: 0        # which rung of CLASSIFICATION.md §4 fired
candle_count: 0
timeframes: []                # ALL ideal timeframes, canonical tokens: [1H, 4H, 1D]
required_trend: ""            # Uptrend | Downtrend | Sideways | Any | NOT SUPPLIED
mandatory_context: []         # only factors the spec explicitly calls mandatory
confirm_bars: null            # int, or null to use the engine default (CV-CONF-002)
trigger_level: ""             # e.g. "pattern high" | supplied rule | engine default
invalidation_level: ""
rsi_rule: ""                  # verbatim intent, or NOT SUPPLIED
ema_rule: ""
volume_rule: ""
location_rule: ""
risk_class: ""                # as supplied label only
reliability_class: ""         # as supplied label only
supplied_statistics: []       # verbatim, e.g. ["±72%"] - labelled User-provided reference
status: RECEIVED              # RECEIVED | SPECIFIED | BLOCKED | TESTS-READY | IMPLEMENTED | VERIFIED
flags: []                     # CONFLICT_LOG ids: [AM-0007, AF-0002]
conversions: []               # DEFINITION_CONVERSIONS ids relied upon: [CV-REL-002]
test_vectors: ""              # tests/vectors/<slug>.json
```

---

## 1. As Supplied (verbatim — immutable)

```text
<paste the owner's specification here exactly as received>
```

**Received:** `<date>` · **Batch:** `<n>`

## 2. Identity

| Field | Value |
| --- | --- |
| Full name | |
| Abbreviation | |
| Abbreviation source | supplied / derived |
| Direction | |
| Primary category | |
| Secondary categories | |
| Candle count | |
| Registry ID | |

## 3. Classification record

* Rung fired (`CLASSIFICATION.md` §4): `<0-5>`
* Sentence the direction was taken from: "<quote>"
* Rungs that also matched (→ secondary): `<list or none>`
* Filed at: `patterns/<dir>/<file>.md`
* Filing notes / oddities: `<none | AM-id>`

## 4. Structure

Plain-language description of the shape, candle by candle, using the supplied wording where
possible.

| # | Candle | Role | Required colour |
| --- | --- | --- | --- |
| 1 | oldest | | |
| 2 | | | |
| n | most recent (the signal candle) | | |

**Indexing note.** Candle 1 is the *oldest*. In implementation the most recent candle is
offset `0`, so candle *k* of an *n*-candle pattern is offset `n - k`. This mapping is
written out explicitly per pattern to prevent off-by-one errors.

## 5. Ideal timeframes

| Token | Included | Source |
| --- | --- | --- |
| | | supplied / NOT SUPPLIED |

* All supplied timeframes are listed. **None is dropped**, and no single "best" one is
  selected (`MASTER_SPECIFICATION.md` §6).
* If none was supplied: `NOT SUPPLIED` → `MS-` entry; the pattern is not timeframe-gated
  until the owner supplies the list.

## 6. Required trend

| Field | Value |
| --- | --- |
| Supplied wording | "<quote>" |
| Machine rule | e.g. `trend == DOWNTREND and trendStrength >= 2` |
| Conversion ID | e.g. `CV-TREND-006` |
| Mandatory? | yes (spec says so) / no (scored as confluence) |

## 7. OHLC rules (structural)

Exact arithmetic, in the notation of `MASTER_SPECIFICATION.md` §2. Structure only — no
RSI/EMA/volume/trend may appear here (§1.1).

```
1. <rule>
2. <rule>
```

## 8. Body rules

| Candle | Rule | Threshold | Source |
| --- | --- | --- | --- |
| | e.g. `bodyPct >= 0.60` | | supplied / `CV-BODY-003` |

## 9. Wick rules

| Candle | Wick | Rule | Threshold | Source |
| --- | --- | --- | --- | --- |
| | upper / lower | | | supplied / `CV-WICK-00n` |

State explicitly whether a "long wick" is measured **against the range** or **as a multiple
of the body** (`SI-05`). If the supplied text does not say, record it in §14 rather than
choosing quietly.

## 10. Candle-to-candle relationships

| Relationship | Rule | Notes |
| --- | --- | --- |
| engulfment | inclusive / strict, body / range | `SI-02`, `SI-03` |
| containment | | |
| open vs prev close | | |
| close vs prev close | | |

## 11. 50% and penetration rules

| Field | Value |
| --- | --- |
| Supplied wording | "<quote>" |
| Reference used | previous **body** midpoint / previous **range** midpoint |
| Machine rule | e.g. `C > (O1 + C1) / 2` |
| Penetration requirement | e.g. `penetrationUp >= 0.50` |
| Conversion ID | `CV-REL-002` |

## 12. Gap requirements

| Field | Value |
| --- | --- |
| Gap required? | yes / no / optional |
| Type | true range gap / body gap |
| Direction | up / down |
| Minimum size | e.g. `gapUpSizeAtr >= 0.25`, or none |
| Conversion ID | `CV-REL-004` / `CV-REL-005` / `CV-REL-006` |

## 13. Context requirements (validation, not structure)

| Factor | Supplied wording | Machine rule | Mandatory? | Conversion |
| --- | --- | --- | --- | --- |
| Location | | | | `CV-LOC-00n` |
| RSI | | | | `CV-RSI-00n` |
| EMA | | | | `CV-EMA-00n` |
| Volume | | | | `CV-VOL-00n` |

Mandatory is set **only** when the supplied text explicitly says the factor is required
(`MASTER_SPECIFICATION.md` §1.1). Anything softer ("works best with", "ideally") is
confluence, not a gate.

## 14. Confirmation

| Field | Value |
| --- | --- |
| Supplied rule | "<quote>" or NOT SUPPLIED |
| Trigger (→ CONFIRMED) | |
| Window | `<n>` closed candles |
| Rule source | supplied / engine default `CV-CONF-001` |
| Closed-candle only | yes (always) |

## 15. Failure condition

| Field | Value |
| --- | --- |
| Supplied rule | "<quote>" or NOT SUPPLIED |
| Invalidation (→ FAILED) | |
| Expiry (→ EXPIRED) | window elapsed with neither trigger nor invalidation |
| Rule source | supplied / engine default `CV-CONF-001` |

## 16. Supplied classifications and narrative (stored, never computed)

| Field | Value |
| --- | --- |
| Risk classification | `<as supplied>` |
| Reliability classification | `<as supplied>` |
| Supplied statistics | `<verbatim>` — **User-provided reference** |

**Tooltip description (as supplied):**

> <text>

**Pattern psychology (as supplied):**

> <text>

**Common mistakes (as supplied):**

> <text>

**Pro tips (as supplied):**

> <text>

Nothing in §16 enters the scoring engine, the validation band, or any calculation
(`MASTER_SPECIFICATION.md` §14).

## 17. Ambiguity register (recorded separately, per instruction)

Every point where the supplied text did not determine a unique machine rule. One row per
issue, each with a `CONFLICT_LOG.md` ID.

| ID | Field | Supplied wording | Why it is ambiguous | Readings possible | Default applied (if any) | Status |
| --- | --- | --- | --- | --- | --- | --- |
| | | | | | | OPEN |

## 18. Audit flags

Preserved-as-supplied items that appear technically incorrect. **The rule above is not
changed.**

```
AUDIT FLAG:
<what appears wrong, the arithmetic or logic that shows it, and what the consequence is at
runtime — e.g. "these two conditions cannot both be true, so the pattern can never fire">
```

Each flag gets an `AF-` ID in `CONFLICT_LOG.md`.

## 19. Test plan

| Case | Vector ID | Expected |
| --- | --- | --- |
| VALID | | detected |
| INVALID (structure fails by one rule) | | not detected |
| WRONG TREND | | detected, trend factor 0 (or suppressed if mandatory) |
| WRONG TIMEFRAME | | hidden in `EXACT`/`CLASS`, shown in `OFF`/TEST MODE |
| FAILED CONFIRMATION | | `FAILED` |
| SUCCESSFUL CONFIRMATION | | `CONFIRMED` |
| EXPIRED | | `EXPIRED`, no failure alert |
| EDGE: boundary body ratio | | at threshold → passes (inclusive, §3.6) |
| EDGE: boundary wick ratio | | |
| EDGE: exact 50% level | | |
| EDGE: zero range candle | | not detected (§3.5) |
| EDGE: flat candle (`C == O`) | | per §3.3 |
| EDGE: gap exactly zero | | |

Vectors live in `tests/vectors/<slug>.json` and run via `python3 tools/run_tests.py`.

## 20. Implementation notes

* Registry row: `<paste the row>`
* Detection function name: `f_<slug>()`
* Reuses: `<engine helpers only — no new ta.* calls>`
* Estimated added cost: `<labels / loop iterations / none>`
* Interaction with other patterns: `<e.g. superset of CM-0xx; both may fire>`

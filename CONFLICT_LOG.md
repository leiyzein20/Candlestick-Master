# CONFLICT LOG

Every contradiction, ambiguity, missing rule, and suspected technical error found in a
supplied pattern specification. **Nothing here is resolved silently.**

Entries are never deleted. A resolved entry keeps its history and gains a resolution line.

---

## How entries are classified

| Type | Prefix | Meaning | Blocks implementation? |
| --- | --- | --- | --- |
| Conflict | `CF-` | Two supplied rules cannot both be satisfied, or a rule contradicts another pattern's rule where they are meant to agree. | **Yes** |
| Ambiguity | `AM-` | The rule is understandable but not yet measurable in one unique way. | **Yes**, unless a documented default is explicitly accepted |
| Missing | `MS-` | A required field or rule was not supplied. | **Yes** for structural fields; no for optional narrative fields |
| Audit flag | `AF-` | The supplied rule is preserved as-is, but appears technically incorrect, self-defeating, or impossible. | No — preserved and implemented as supplied |
| Conversion | `CV-` | A vague phrase turned into an explicit measurable rule. Lives in [`docs/DEFINITION_CONVERSIONS.md`](docs/DEFINITION_CONVERSIONS.md); cross-referenced here only when a specific pattern depends on it. | No |

Severity: `BLOCKING` (pattern cannot be implemented), `MAJOR` (pattern implementable but
behaviour is uncertain), `MINOR` (cosmetic / documentation).

Status: `OPEN` → `AWAITING OWNER` → `RESOLVED` / `ACCEPTED AS SUPPLIED` / `WITHDRAWN`.

---

## Entry format

Every entry uses exactly this shape so the log stays diffable and machine-checkable:

```markdown
### CF-0001 — <short title>

* **Pattern(s):** <ID / abbreviation / name>
* **Type:** Conflict
* **Severity:** BLOCKING
* **Status:** OPEN
* **Raised:** <date>
* **Supplied text A:** "<verbatim quote>"
* **Supplied text B:** "<verbatim quote>"
* **Why they collide:** <mechanical explanation, with the arithmetic if relevant>
* **Cannot be auto-resolved because:** <both readings are defensible / data does not exist / etc.>
* **Options (not chosen):**
  1. <option> — consequence
  2. <option> — consequence
* **Owner decision:** <blank until supplied>
```

`AF-` entries additionally carry the exact `AUDIT FLAG:` text that was inserted into the
pattern file, so the file and the log cannot drift apart.

---

## Open entries

*None. No pattern specifications have been supplied yet.*

## Resolved entries

*None.*

---

## Standing items

Recorded now because they will affect many patterns as soon as specifications arrive.
These are **not** conflicts in supplied data; they are known decision points where a
supplied spec will need to say which reading it means, and where the engine default is
already documented so nothing is invented silently.

| ID | Decision point | Engine default until told otherwise | Reference |
| --- | --- | --- | --- |
| `SI-01` | "50%" — previous **body** midpoint vs previous **range** midpoint | body midpoint | `CV-REL-002` |
| `SI-02` | "Engulfs" — inclusive (`>=`) vs strict (`>`) body comparison | inclusive body | `CV-REL-001` |
| `SI-03` | "Engulfs" — body-only vs full range including wicks | body-only | `CV-REL-001` |
| `SI-04` | "Gap" — true range gap vs body gap | body gap in star-family, true gap elsewhere | `CV-REL-004/005` |
| `SI-05` | "Long wick" — fraction of range vs multiple of body | both available; spec must state which | `CV-WICK-001/002` |
| `SI-06` | "Small body" / "large body" numeric cut-offs | `≤0.30` / `≥0.60` of range | `CV-BODY-002/003` |
| `SI-07` | "Clear trend" | trend state + `trendStrength >= 2` | `CV-TREND-006` |
| `SI-08` | "Major support/resistance" | ≥2 touches, one from a pivot of length ≥10 | `CV-LOC-006` |
| `SI-09` | Confirmation window when unspecified | 3 closed candles | `CV-CONF-002` |
| `SI-10` | Ideal-timeframe matching on non-listed chart timeframes (e.g. 3H when spec lists H1/H4) | `CLASS` mode allows it; `EXACT` mode hides it | `CV-TF-001` |
| `SI-11` | Doji tolerance (`open == close`) | `bodyPct <= 0.10` | `CV-BODY-001` |
| `SI-12` | Flat candle (`close == open`) where a coloured candle is required | fails, unless the spec allows it | `MASTER_SPECIFICATION.md` §3.3 |
| `SI-13` | Supplied probabilities / reliability percentages | stored verbatim, labelled `User-provided reference`, excluded from all maths | `MASTER_SPECIFICATION.md` §14 |
| `SI-14` | Abbreviation collision between two supplied patterns | **not** auto-renamed — raised as `CF-` and both patterns held | `PATTERN_REGISTRY.md` §3 |

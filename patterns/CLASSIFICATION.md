# CLASSIFICATION AND ROUTING

How a supplied pattern is filed. This is a **deterministic procedure**, not a judgement
call, so filing never needs to be discussed. The only case that goes back to the owner is
a *genuine* contradiction (§5).

---

## 1. The two axes

Every pattern gets exactly one value on each axis.

**Direction** — the side the pattern implies:

| Value | Meaning |
| --- | --- |
| `Bullish` | implies upward resolution |
| `Bearish` | implies downward resolution |
| `Neutral` | implies indecision / no directional bias of its own |

**Primary category** — what the pattern *does*, one value only:

| Value | Meaning |
| --- | --- |
| `Reversal` | a prior move is expected to turn |
| `Continuation` | a prior move is expected to resume |
| `Exhaustion` | a move is running out of participation — climax, blow-off, capitulation, overextension |
| `Neutral` | balance / indecision, no directional expectation |
| `Gap` | the pattern's identity **is** the gap (§3) |

Additional conceptual categories are recorded as **secondary** categories. Secondary
categories never affect the file location, and by default never affect the display filter
(`MASTER_SPECIFICATION.md` §11.1).

---

## 2. Routing table

Complete over all 15 combinations. No gaps, no defaults, no interpretation.

| Direction | Primary | Directory | Filename |
| --- | --- | --- | --- |
| Bullish | Reversal | `patterns/bullish_reversal/` | `<slug>.md` |
| Bullish | Continuation | `patterns/continuation/` | `bull_<slug>.md` |
| Bullish | Exhaustion | `patterns/exhaustion/` | `bull_<slug>.md` |
| Bullish | Gap | `patterns/gap_patterns/` | `bull_<slug>.md` |
| Bullish | Neutral | `patterns/neutral/` | `bull_<slug>.md` + `AM-` note (§5.2) |
| Bearish | Reversal | `patterns/bearish_reversal/` | `<slug>.md` |
| Bearish | Continuation | `patterns/continuation/` | `bear_<slug>.md` |
| Bearish | Exhaustion | `patterns/exhaustion/` | `bear_<slug>.md` |
| Bearish | Gap | `patterns/gap_patterns/` | `bear_<slug>.md` |
| Bearish | Neutral | `patterns/neutral/` | `bear_<slug>.md` + `AM-` note (§5.2) |
| Neutral | Reversal | `patterns/neutral/` | `neut_<slug>.md` |
| Neutral | Continuation | `patterns/continuation/` | `neut_<slug>.md` |
| Neutral | Exhaustion | `patterns/exhaustion/` | `neut_<slug>.md` |
| Neutral | Gap | `patterns/gap_patterns/` | `neut_<slug>.md` |
| Neutral | Neutral | `patterns/neutral/` | `neut_<slug>.md` |

Notes on the table:

* Direction-specific reversal directories exist because reversals are the bulk of the
  database and splitting them keeps both directories navigable.
* The shared directories (`continuation`, `exhaustion`, `neutral`, `gap_patterns`) hold
  both sides, so filenames there carry a `bull_` / `bear_` / `neut_` prefix. That keeps a
  directory listing readable without opening files.
* A `Neutral`-direction pattern that a spec calls a reversal (e.g. an indecision candle
  presented as a turning signal) files under `patterns/neutral/` while keeping
  `Primary: Reversal` in the registry. Directory and category are allowed to differ here
  precisely because the routing table says so — it is not an inconsistency.

**Slug** = the full supplied name, lowercased, non-alphanumerics → `_`, no leading or
trailing `_`. Example: `Three White Soldiers` → `three_white_soldiers`.

---

## 3. When is `Gap` the primary category?

`Gap` is reserved for patterns whose **identity is the gap itself** — the specification
describes a price discontinuity as the pattern, and there is no named candle formation
underneath it.

A pattern is **not** primary-`Gap` merely because its rules contain a gap requirement. Many
multi-candle formations require a gap as one of several structural conditions; those keep
their behavioural category (`Reversal` / `Exhaustion` / `Continuation`) and record `Gap` as
a **secondary** category, with the gap rule captured in the *Gap requirements* field.

Test, applied in order:

1. Remove the gap requirement from the specification. Is a recognisable, separately named
   candle formation still described? → **not** primary-`Gap`; `Gap` becomes secondary.
2. Otherwise → primary-`Gap`.

This test is mechanical and gives the same answer every time. It is applied per supplied
specification, never by pattern name.

---

## 4. Choosing the primary category

**Rung 0.** If the supplied specification states a category, use it verbatim. Stop.

Otherwise, walk the ladder and take the **first** rung that matches. The ladder is ordered,
so it always produces exactly one answer:

| Rung | Question | Primary |
| --- | --- | --- |
| 1 | Is the gap the pattern's identity (§3)? | `Gap` |
| 2 | Does the specification describe climax, blow-off, capitulation, panic, overextension, or a trend ending through *loss of participation* rather than through opposing structure? | `Exhaustion` |
| 3 | Does it require a **prior opposite** move and imply a turn? | `Reversal` |
| 4 | Does it require a **prior same-direction** move and imply resumption? | `Continuation` |
| 5 | Does it describe balance / indecision with no directional expectation? | `Neutral` |
| 6 | None of the above matched. | → §5.1 |

The rung that fired, and any rung that *also* matched, are both recorded in the pattern
file's *Classification* block. Rungs that also matched become secondary categories. That is
how a pattern legitimately belongs to more than one conceptual category without its file
location becoming ambiguous.

Choosing direction is simpler and is taken from the specification's own words. If the
specification implies a direction only through its rules (e.g. every rule concerns a
downtrend turning up), the direction is recorded together with the sentence it was taken
from.

---

## 5. The only cases that come back to the owner

### 5.1 Genuine contradiction — `BLOCKING`

Raised as a `CF-` entry in `CONFLICT_LOG.md`, pattern held at `BLOCKED`:

* the specification explicitly names **two** primary categories (e.g. calls the pattern
  both a continuation and a reversal) — the ladder is not allowed to overrule an explicit
  statement, so it cannot pick;
* the specification names a direction that its own rules contradict (e.g. `Bullish` while
  every rule describes a bearish resolution);
* the ladder reaches rung 6 — nothing in the specification indicates what the pattern is
  for.

### 5.2 Non-blocking oddity — `MINOR`

Recorded as an `AM-` entry, filed anyway per the routing table, work continues:

* a directional pattern (`Bullish` / `Bearish`) with `Primary: Neutral`;
* `Neutral` direction with a strongly directional confirmation rule;
* a category that fires on a rung far from the specification's own emphasis (the note
  records the alternative reading).

---

## 6. Worked examples of the procedure

Deliberately abstract — no real pattern rules are invented here, since none have been
supplied. They show the mechanism only.

| Supplied says | Direction | Rung fired | Primary | Secondary | Filed as |
| --- | --- | --- | --- | --- | --- |
| "bullish reversal, 2 candles, needs a downtrend" | Bullish | 0 (explicit) | Reversal | — | `patterns/bullish_reversal/<slug>.md` |
| "three-candle bearish formation appearing after an extended rally, buyers exhausted" | Bearish | 2 | Exhaustion | Reversal | `patterns/exhaustion/bear_<slug>.md` |
| "price gaps above the prior range and never trades back" | Bullish | 1 | Gap | Continuation | `patterns/gap_patterns/bull_<slug>.md` |
| "star formation: gap, small body, then close back into the first body" | Bullish | 3 | Reversal | Gap | `patterns/bullish_reversal/<slug>.md` |
| "open and close nearly equal, market undecided" | Neutral | 5 | Neutral | — | `patterns/neutral/neut_<slug>.md` |
| "continuation pattern that some traders also treat as a reversal" | either | 5.1 | — | — | `BLOCKED`, `CF-` raised |

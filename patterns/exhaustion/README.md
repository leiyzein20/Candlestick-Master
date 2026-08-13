# EXHAUSTION PATTERNS

`Primary category: Exhaustion`, any direction.

Filename: `bull_<slug>.md` / `bear_<slug>.md` / `neut_<slug>.md`.

## What lands here

The supplied text describes a move **running out of participation**: climax, blow-off,
capitulation, panic, overextension, or a trend ending through loss of force rather than
through opposing structure (`CLASSIFICATION.md` §4, rung 2).

Exhaustion outranks `Reversal` on the ladder, so a pattern described in exhaustion language
files here even though it also implies a turn. `Reversal` is then recorded as a **secondary**
category, and the registry keeps both — that is how the `REVERSAL ONLY` filter can still
optionally include it (`CV-FILT-001`).

## Category-specific checks at intake

* **Direction semantics need care.** A *selling* climax is a bearish event with a bullish
  implication. The recorded `Dir` is the direction the pattern **implies**, per the supplied
  text, and the sentence it was taken from is quoted in §3 of the pattern file.
* **Extension is often part of the definition.** "After an extended move" needs a measurable
  rule; the engine offers ATR-normalised extension and trend strength
  (`engines/TREND_ENGINE.md`), and whichever is used is cited by `CV-` ID. It is never
  assumed.
* **Volume language is frequent and must stay honest.** Climax claims often lean on volume;
  on forex/CFD feeds the wording becomes "tick volume", and where no volume series exists
  the factor is excluded rather than faked (`MASTER_SPECIFICATION.md` §7.3).
* **No probability claims.** Exhaustion specs tend to arrive with reliability statements;
  they are stored as supplied labels and excluded from every calculation
  (`MASTER_SPECIFICATION.md` §14).
* **Rarity is preserved.** Exhaustion patterns are typically rare by construction. Rules are
  never loosened to make them appear more often
  (`MASTER_SPECIFICATION.md` §14.7).

## Index

| ID | ABBR | Name | Dir | Candles | Timeframes | Status |
| --- | --- | --- | --- | --- | --- | --- |
| *(none yet)* | | | | | | |

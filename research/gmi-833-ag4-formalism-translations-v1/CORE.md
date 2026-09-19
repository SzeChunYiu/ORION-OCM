# AG4 — the fifteen family pairs, adjudicated (START HERE)

The AG4 row asks for exact translations among the applicable finite specializations of the six
families the section lists. Two of the fifteen pairs already had one on `main`; thirteen did
not. This tranche adjudicates all thirty directed translations over one registered finite
universe and publishes the exact residual wherever a translation is not total.

## Headline numbers (exact integer and `Fraction` arithmetic; no float enters any claim)

| quantity | value |
|---|---|
| registered objects across the ten specializations | `8,032` |
| directed translations | `30`: `16` TOTAL · `14` PARTIAL · `0` EMPTY |
| pairs | `15`: `4` mutually total · `8` total one way · `3` partial both ways |
| mutually total | `A-D`, `B-C`, `B-E`, `C-E` |
| partial in both directions | `B-F`, `C-F`, `E-F` |
| exact domains | `B -> {A,D,F}` `274/1,024` · `C -> {A,D,F}` `542/1,412` · `E -> {A,D,F}` `478/1,348` · `F -> *` `3,728/4,160` |
| obstructions, by incidence | blocking `9` · nondeterminism `9` · non-point-mass kernel `6` · arity `5` · monoidal structure `1` |
| translations out of the category family | total but **not canonical**; fibre sizes `1`, `4`, `6`, `13` |
| kernel-to-support fibre | `324` kernels over `102` supports, largest fibre `90` |
| flattening control | `8,032 -> 516` objects makes all `30` total and all `15` mutually total |
| route A / route B disagreements | `0` |

## The three things worth knowing

**Not one of the fifteen pairs is a free interchange.** Four are mutually total and eight are
total in one direction only, but the other direction of each of those eight is bounded by an
exact domain and a named obstruction. Three pairs are partial in both directions. The families
differ, and the differences have names and sizes.

**The obstruction vocabulary was closed before any run, and three of its eight tokens never
fire.** That is reported rather than dropped, and two of the three are the interesting ones:
`WEIGHTS_NOT_RECOVERABLE` and `NO_CHOSEN_GENERATING_FAMILY` never block a translation because
neither is a barrier. A kernel's weights are a **fibre** over its support — `324` kernels present
only `102` supports — and a monoid's missing label indexing is a failure of **canonicity**, not of
existence. Both are measured directly instead of being miscounted as obstructions.

**The result depends entirely on not flattening the universe.** Cut every family down to the one
deterministic, total, arity-one core they all contain and all thirty translations become total.
That control is run on every pass and published beside the true table; it is what a universe
designed to make every translation succeed would look like.

## Evidence

- **2 materially independent routes.** Route B imports neither route A nor any parent module. It
  decodes objects from integer indices, computes behaviour by a dynamic program over composed
  word-transition tables, decides translatability by binary search in a sorted list, recomputes
  the submonoids from scratch, and re-derives every obstruction from the object's structure.
  **0 disagreements** on verdict, exact domain, translatable count, common class, obstruction
  set, object counts, both histograms and the mutually-total list.
- **6 hostiles, all detected, each with a control proving it moves its quantity**: behaviour
  compared in the source's own class (`16 -> 12` totals); the universe flattened (`8,032 -> 516`
  objects, `15/15` mutually total); a source range trimmed to one specialization
  (`40,160 -> 11,320`); a witness that in fact translates (`14` planted, `8` caught); an
  obstruction outside the vocabulary; the observation window cut to one letter (`16 -> 21`).
- **Null.** `0 / 200` randomized totality patterns across the thirty directed translations
  reproduce the published one.
- **No-alarm case asserted**: every witness re-verifies as untranslatable, every obstruction is
  in the vocabulary, every common class matches the rule, every source range recomputes from the
  generators, and `W - 1` gives the same thirty verdicts as `W`.

## What this does not say

A `TOTAL` verdict is a statement about the source family's whole registered range at this finite
scope. It is not a claim that the two formalisms are interchangeable in general, and it carries
nothing about cost, description length or search geometry — `TRANSLATION_PRESERVES_COST` and
`TRANSLATION_PRESERVES_SEARCH_GEOMETRY` are registered forbidden promotions, following the
merged parent `gmi-833-aj5-g0-lowering-v1`'s own transfer boundary.

## Reproduce

```
python3 -I -B  research/gmi-833-ag4-formalism-translations-v1/ag4_formalism_translations_v1.py
python3 -I -B  research/gmi-833-ag4-formalism-translations-v1/independent_oracle_v1.py
python3 -I -O -B research/gmi-833-ag4-formalism-translations-v1/test_ag4_v1.py
```

Route A takes about 3 s, route B about 2 s. Stdlib only.

## Files

`FREEZE_V1.md` (committed before any code, commit `e03cc198`) ·
`AG4_TRANSLATION_THEOREMS_V1.md` (`AG4T-1` … `AG4T-4`) · `PARENT_LEDGER.md` ·
`KNOWN_CONFLICT_V1.json` · `RESULT_V1.json` · `ORACLE_RESULT_V1.json` · `TEST_RESULT_V1.json` ·
`MANIFEST_V1.json`.

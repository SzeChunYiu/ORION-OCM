# FREEZE — `gmi-833-ag4-formalism-translations-v1`

Committed **before** any executor, oracle, test, receipt or workflow file of this package.
Nothing below may be edited after the first implementation commit; a later correction must
arrive as a new file that cites this one.

## Custody

| field | value |
|---|---|
| `source_main` | `50f833cc4bc3cadcefd44eca14fa58f73f815587` |
| issue | `SzeChunYiu/ORION-OCM#833` |
| section | AG4 (one row) |
| comment | `5693520829` |
| claim ceiling | `AG4_ALL_FIFTEEN_FAMILY_PAIRS_ADJUDICATED_TOTAL_OR_PARTIAL_WITH_A_NAMED_OBSTRUCTION_AT_REGISTERED_FINITE_SCOPE` |

## The exact row this tranche may reconcile

Byte-exact from comment `5693520829`. No other row of any section is in scope.

Anchor `### AG4 — Process/transition semantics below named operators`:

```
- [ ] Construct exact translations among the applicable finite specializations.
```

**No neighboring row is earned here.** In particular this tranche does not touch AG4's five
already-checked rows, AG2 row 13, AG3 row 14, AG5 rows 30-32, AG6 rows 34-36 and 38, AG7 rows
41 and 44, AG8 row 48, or any AH row.

## 1. The six families, taken verbatim from the AG4 section

The AG4 comment lists six candidate families to compare without choosing one in advance. The
block is reproduced byte-exactly because it is what fixes the scope of the row's phrase "the
applicable finite specializations"; the AB terminology ratchet fires on one word inside it, and
that is recorded in `KNOWN_CONFLICT_V1.json` rather than repaired by paraphrase:

```text
A. carrier + finitary operations          (universal algebra)
B. states + labelled transition relation (LTS / operational semantics)
C. coalgebraic state-transition systems  (state-based behavior)
D. objects + morphisms + composition     (category/process theory)
E. relations/kernels rather than only deterministic functions
F. typed process interfaces + serial/parallel composition
```

Fifteen unordered pairs, thirty directed translations. Two of the fifteen already have an exact
translation on `main`: `A`-`E` by `gmi-833-aj5-g0-lowering-v1`'s `P-FUN`/`P-REL` pair, and one
formalization-style pair by `gmi-833-aj12-foundation-substrate-relativity-v1`. Those two are
cited, not re-claimed. The remaining thirteen are the residual this tranche exists for.

## 2. The finite specializations, fixed before any run

State space `S = {0, 1}`. Label alphabet `Lab = {x, y}`. Observation alphabet `Obs = {0, 1}`.
Rational weights are drawn from the frozen grid `{0, 1/2, 1}` and are carried as exact
`fractions.Fraction`; no float is constructed anywhere.

Each family's registered range is its **own** full range. The families are deliberately NOT
cut down to a common deterministic core: the differences between their ranges are where the
obstructions live, and a universe flattened to make every translation total would measure
nothing.

| family | a registered object is | range size |
|---|---|---|
| `A` | `S`, one total function `S -> S` per label, one `out : S -> Obs` | deterministic, total |
| `B` | `S`, one relation `R_l` on `S` per label, one `out` | nondeterministic, possibly blocking |
| `Cd` | a coalgebra `S -> (Obs x S)^Lab` | deterministic |
| `Cn` | a coalgebra `S -> (Obs x P(S))^Lab` | nondeterministic |
| `Cp` | a coalgebra `S -> (Obs x D(S))^Lab` over the frozen weight grid | probabilistic |
| `D` | a submonoid of `S -> S` under composition, together with `out` | deterministic, no chosen generating family |
| `Er` | one relation per label, one `out` | relational |
| `Ek` | one `S -> D(S)` kernel per label over the frozen grid, one `out` | probabilistic |
| `F1` | a typed process of arity `1` with serial and parallel composition | deterministic, arity 1 |
| `F2` | a typed process of arity `2` with serial and parallel composition | deterministic, arity 2 |

`C` is the union of `Cd`, `Cn`, `Cp`; `E` is the union of `Er`, `Ek`; `F` is the union of `F1`,
`F2`. A pair's adjudication ranges over the whole union on each side.

## 3. What an exact translation is

The comparison object is the **observable behaviour** of a specialization, in the coarsest class
the pair spans:

```text
deterministic   beh : Lab* -> Obs
nondeterministic beh : Lab* -> subset of Obs        (the set of observations reachable)
probabilistic   beh : Lab* -> D(Obs)                (exact rational weights)
```

A deterministic behaviour lifts to a nondeterministic one by singletons and to a probabilistic
one by point masses; a probabilistic behaviour projects to a nondeterministic one by support.
Behaviour is decided on the finite window `|w| <= W` with `W = 4`; the executor must prove the
window is sufficient by recomputing at `W` and at `W - 1` and finding the induced partitions
equal.

A directed translation `tau : X -> Y` is **exact on `x`** iff `tau(x)` is a registered `Y`-object
and `beh_Y(tau(x)) = beh_X(x)` in the coarsest common class.

`tau` is **TOTAL** iff it is exact on every registered `X`-object.
`tau` is **PARTIAL** iff it is exact on a proper non-empty subset; the executor must then publish
(i) the exact size of that subset, (ii) a structural description of it, (iii) a named obstruction,
and (iv) an explicit `X`-object outside it together with a proof that no registered `Y`-object has
its behaviour — proved by exhaustive search over the whole registered `Y` range, never asserted.
`tau` is **EMPTY** iff no registered `X`-object translates.

A pair is **canonical** iff the translation is a function of the object alone; it is
**NON_CANONICAL** iff a choice has to be made, and the executor must then publish the exact fibre
sizes the choice ranges over.

## 4. The obstruction vocabulary, fixed before any run

No obstruction outside this list may be published; a translation that fails for a reason not on
this list is a `RED` result, not a new name.

- `NONDETERMINISM_NOT_FUNCTIONAL` — a relation with two successors has no total-function image.
- `BLOCKING_NOT_TOTAL` — a relation with no successor has no total-function image.
- `WEIGHTS_NOT_RECOVERABLE` — the support of a kernel forgets the weights, so the inverse is
  a fibre rather than a map.
- `NON_DIRAC_KERNEL` — a kernel that is not a point mass has no deterministic image.
- `NO_CHOSEN_GENERATING_FAMILY` — a monoid carries no label indexing, so recovering a labelled
  action is a choice.
- `MONOIDAL_STRUCTURE_NOT_DERIVABLE_FROM_COMPOSITION` — serial composition does not determine a
  tensor.
- `ARITY_NOT_REPRESENTABLE` — an arity-`2` interface has no arity-`1` image on `S`.
- `FUNCTOR_NOT_IN_RANGE` — the coalgebra's functor is outside the target family's declared range.

## 5. The gates, fixed before any run

`status: GREEN` requires **all** of:

1. all `15` pairs and all `30` directed translations carry a verdict from section 3;
2. every `TOTAL` verdict is verified exhaustively over the source family's whole registered
   range, with zero behaviour mismatches;
3. every `PARTIAL` verdict carries its exact domain size, its named obstruction from section 4,
   and a witness outside the domain whose untranslatability is proved by exhaustive search over
   the target range;
4. **not all 15 pairs are total.** If they are, the universe was flattened and the result is
   `RED`: a family set whose members are mutually and totally interchangeable is not the six
   families the AG4 section lists;
5. every published behaviour equality is computed in the coarsest common class, and the
   observation window is proved sufficient;
6. route A and route B agree on every published quantity, route B importing nothing from route A;
7. every declared hostile is detected, each paired with a control proving the perturbation moves
   the quantity it claims to move; a perturbation that cannot is recorded as inapplicable and is
   NOT counted as a hostile;
8. the null reproduces the totality pattern in `0` of its live draws;
9. the no-alarm case is asserted.

Any failure publishes `status: RED` with the failing gate named. A red result is a result.

## 6. Falsifiers, fixed before any run

- If every directed translation is total, the specializations were flattened and every number
  here is void.
- If a `TOTAL` verdict has one behaviour mismatch on the registered range, that verdict is void.
- If a `PARTIAL` verdict's witness does translate after all, the exhaustive search was not
  exhaustive and every number is void.
- If the behaviour window `W - 1` and `W` disagree on any verdict, the window is insufficient.
- If a randomized assignment of totality across the `30` directed translations reproduces the
  published pattern, the adjudication is not identifying.
- If any obstruction outside section 4's list is needed, the vocabulary was wrong and the
  affected verdicts are withdrawn rather than renamed.

## 7. Forbidden promotions

`UNIQUE_LOWEST_PROCESS_FORMALISM`, `ABSOLUTE_PROCESS_ONTOLOGY_PROVEN`,
`ALL_PROCESS_FORMALISMS_EQUIVALENT`, `THE_SIX_FAMILIES_ARE_EXHAUSTIVE`,
`TRANSLATION_PRESERVES_COST`, `TRANSLATION_PRESERVES_SEARCH_GEOMETRY`,
`FORMALISM_CHOICE_IS_FREE`, `COMPLETE_GMI`.

The merged parent `gmi-833-aj1-operational-process-base-v1` registers
`ABSOLUTE_PROCESS_ONTOLOGY_PROVEN` as forbidden and states minimality only relative to named
requirements. Nothing here weakens that: an adjudication that produces obstructions in both
directions is evidence **for** `MULTIPLE_FOUNDATIONALLY_EQUIVALENT_PROCESS_BASES`, the terminal
AG4's last row already permits, and against any unique-bottom reading.

## 8. What is not claimed novel

Universal algebra and finitary operations, labelled transition systems and structural
operational semantics, the coalgebraic treatment of state-based systems and its functor
parameterization, categories with a chosen generating family, the powerset and distribution
monads and their Kleisli categories, symmetric monoidal categories and the distinction between
serial and parallel composition, Markov kernels, and the classical isomorphism between labelled
transition systems and coalgebras for the powerset functor, are all parent mathematics. They are
pinned in `PARENT_LEDGER.md`. The residual contribution of this tranche is the exhaustive
adjudication itself: thirty directed translations over one registered finite universe, each
either verified total or bounded by an exact domain, a named obstruction and a proved witness.

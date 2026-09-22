# GMI #833 Section-H real-scale freeze v1 — Probabilistic graphical models.

`source_main`: `6e116ce5`.

This file is committed **in its own commit, before any executor, test, data
extraction, fit, or result artifact of this package exists**. `git log
--diff-filter=A` order is the custody record and CI asserts it.

## 1. The exact issue row this package may reconcile

Section of the issue: the Section-H families header line of issue #833,
recorded verbatim (with its own wording and its row prefix) as the `anchor`
field of this package's `ISSUE_833_RECONCILIATION` document: the anchor string
is the header line exactly as the live body carries it, and the only row this
package may reconcile is the one quoted immediately below.

Row, verbatim and complete:

```
- [ ] Probabilistic graphical models.
```

**No neighboring row is earned here.** No row of any other section, no
aggregate Section-H row, and none of the other 40 named-family rows. In
particular `Bayesian inference/belief-state systems.`, `Particle/population
inference.`, `Decision trees/rule systems.` and `Associative memory.` are
handled by other packages (`gmi-833-h-real-scale-decision-trees-v1` at
`SIGMA_H08R`, `gmi-833-h-real-scale-associative-memory-v1` at `SIGMA_H06R`);
none are re-earned, re-claimed, or depended upon here.

## 2. The scope decision that governs this package

Section H requires eleven coordinates per row: property prediction from
specification/ecology (`R01`); `P3`/`P4` grammar (`R02`); no family macros
(`R03`); family-blind recovery (`R04`); a matched negative control (`R05`);
lower bound where possible (`R06`); resource crossover (`R07`); held-out frozen
prediction (`R08`); independent regeneration (`R09`); independent search
(`R10`); real-scale test (`R11`).

The finite scope of this row (R01–R10) is certified by the parent
`gmi-833-h-family-tranche-a-v1` at its registered finite scope, with R11 open
(`REAL_SCALE_OPEN_PENDING`). It is **invalid** to add the missing certificate
at a different scope and declare the conjunction: that is
`CROSS_SCOPE_GATE_COMPOSITION`, forbidden by
`gmi-833-h-family-requirement-ledger-v1` `HRL-1` and proved invalid by PR #997
`FGS-2`. A scope is the tuple (family row, grammar, ecology, budget, freeze,
protected interface); every one of those coordinates moves here.

**Therefore this package imports no gate certificate from any parent. It earns
all eleven coordinates at its own scope, self-contained.** The parents supply
form — the eleven-coordinate real-scale ledger shape
(`gmi-833-h-real-scale-classical-v1`, `gmi-833-h-real-scale-revival-v1`), the
finite-scope row shape and the registered contract steer
(`gmi-833-h-family-tranche-a-v1`), the post-hoc structural classifier idea,
the charged-cost model idea, the symmetric half-split regeneration form, the
matched-presentation control form and the null constructions of the siblings
(`gmi-833-h-real-scale-nearest-neighbor-v1` at `SIGMA_H05R`,
`gmi-833-h-real-scale-associative-memory-v1` at `SIGMA_H06R`,
`gmi-833-h-real-scale-decision-trees-v1` at `SIGMA_H08R`) — and are cited as
the strongest parents in `PARENT_LEDGER.md`. They supply no evidence that is
counted here. The finite-scope steer of this row at `SIGMA_CENSUS` is a steer
only; no tranche-a number, no tranche-a gate certificate, and no tranche-a
scope is imported as evidence.

### The registered contract of this row, recorded as a steer

`research/gmi-833-h-obstruction-census-v1/FROZEN_FAMILY_REGISTRY_V1.json`
(blob `e0a8e7a9d0988dc5b702737db693df375710b986` on `source_main`) records for
this row, verbatim:

```
{"id": "H18", "row": "Probabilistic graphical models.", "contract": "TRIPLE_PARITY",
 "hallmark": "registered three-variable dependency response"}
```

and the file's own `scope` field states what that field is: `finite operational
hallmark contracts; not full historical-family definitions`. **That contract is
a steer, exactly as the sibling `gmi-833-h-real-scale-decision-trees-v1`
recorded its own `THRESHOLD_CONJUNCTION` steer as a steer only** (its
`FREEZE_V1.md` section 2 records the tranche-a class as "a steer only — no
tranche-a number, no tranche-a gate certificate, and no tranche-a scope is
imported as evidence"); its own winner is the two-test conjunction
`LEN<=9&CNT>=1`. A steer constrains the STRUCTURE of the recovered readout, not
a literal arity, and it supplies no evidence.

**How the steer is honoured here, in one line.** The recovered readout is a
DEPENDENCY response over the stored factorisation: a conjunction of
factor-local conditions, every factor must agree, which is the dependency
structure the steer names — not a threshold over one stored dimension, which is
the sibling's class. The steer is recorded and honoured; it is not imported as
evidence, and this package claims no three-variable arity.

A test asserts that no gate certificate emitted here carries a `sigma` that is
not this package's own, and that no parent result file is read by the checker.

## 3. The scope, written out

| id | family row | ecology `F` | protected interface |
|---|---|---|---|
| `SIGMA_H18R` | Probabilistic graphical models. | `F16` stored factor graph on `D` | held-out exact prototype-agreement; held-out exact sign-decision error count |

Every gate certificate emitted by this package carries its `sigma` id. The
checker fails the run if the row's eleven certificates do not all carry one and
the same `sigma` id, or if any `sigma` is foreign.

## 4. Real data source, bound by digest

Externally originated; none generated by this package or by any agent. Every
number in every claim traces to these bytes.

- `D` = `/usr/share/dict/american-english` on billy-old (billy-laptop-old),
  104,334 whitespace-separated tokens
  (`len(open(path).read().split())`, the exact arithmetic definition of `N`),
  in file order; sha256 digest of the file bytes
  `9e66281f7e51445eab6857488ff6e3d768afffadb7fb1adbef5e4617bee4a53b`.

Host of record: `billy-old`, Linux, CPython 3.14.4. Any digest mismatch fails
the run closed. A negative control asserts that a perturbed path or a
perturbed digest fails rather than passing vacuously.

### The ecology, registered before it is built

`F16` (`SIGMA_H18R`). Tokenise `D` into its 104,334 whitespace-separated
tokens. The descriptor closure is: for every token `w` and every length `L`
with `2 <= L <= len(w)`, the prefix `w[:L]`. The exact total is

```
T = sum(len(w) - 1 for w in words) = 776,142 descriptors
```

**The stored object is a factor graph with two independent factors over
disjoint token populations.** The token list is split by a content-external,
deterministic rule into

```
R1 = the tokens of EVEN length   (387,582 descriptor occurrences)
R2 = the tokens of ODD  length   (388,560 descriptor occurrences)
```

Every descriptor occurrence belongs to exactly one factor, so the two stored
relations are disjoint and independent: no descriptor occurrence is counted in
both. For a query descriptor `q` the **factor-local evidence** is, per factor
`i`,

```
ci(q) = the number of stored descriptor occurrences of q contributed by factor i
fi(q) = |Ai(q)|, where Ai(q) is the set of distinct letters that appear
        immediately after q across factor i's tokens
        (the factor's continuation fan-out; the trie child count of q inside
         factor i's token trie)
```

and there is **no marginalised table**: the language of section 5 contains
factor-local readouts and PRODUCTS of factor-local readouts, never a
pre-computed joint or marginal distribution.

A task is a query descriptor. The family is **probabilistic graphical
models**: the stored object is a factorisation of a joint distribution into
factors over a small variable set — independence structure, i.e. which
variables are coupled and which are separately determined — and the question a
graphical model answers is whether the factors AGREE about a query. Here the
factors are `R1` and `R2`, the factor-local evidence of a query is
`(ci(q), fi(q))`, and the factor-product readout is the message-passing /
marginalisation structure of the stored model.

The protected interface is held-out exact prototype-agreement and held-out
exact sign-decision error count, over the exact decisions

```
y(q) = 1 iff f1(q) >= 1 AND f2(q) >= 1
```

**The label is JOINT CONSISTENCY across the two independent stored factors:**
a query is positive exactly when EVERY factor agrees that it has a stored
continuation — the conjunction over factor-local evidence, which is what a
factorisation asserts and what a factor-product readout computes. It is not a
threshold over one stored dimension: `f1(q) >= 1` alone (the R1 factor only)
and `f2(q) >= 1` alone (the R2 factor only) each fail it on a large share of
the descriptors, and corrupting exactly one factor destroys it.

Slices, fixed here before any fit: the descriptor list is partitioned by a
deterministic 7:1 rule registered in `FREEZE_V1_SLICE_ADDENDUM.md`, giving

```
n_fit = (T * 7) // 8 = 679,124  >= 100k
n_held = T - n_fit = 97,018    >= 20k
```

which clears the R11 real-scale bar (n_fit >= 100k / n_held >= 20k on a
sha256-bound external REAL source, exact arithmetic, independent oracle).

## 5. Grammar

`G_PGM`: a family-blind grammar derived ONLY from the sha-bound bytes of `D`.
Descriptor closure over the token vocabulary (prefixes of length >= 2), the
two-factor split of the token list, the factor-local evidence table (per-factor
occurrence count and per-factor continuation fan-out), and a charged-cost model
over factor lookups and scan cost. No family-level macro, no hand-encoded
graphical-model routine, no reference to any external implementation. Section
R03 asserts the grammar contains no graphical-model macro, and R04 recovers
the family from the grammar alone.

## 6. Arithmetic

Exact integer arithmetic for every reported quantity: every claimed number is
an exact integer decision count (prototype agreement, sign-decision errors,
null errors, ladder errors, charged-cost units, crossover index). No float
enters any comparison, count, loss, or claim. There is no real-valued fitting
routine whose output requires a rationalisation operator, so this package
carries no arithmetic addendum: the exact-integer form is complete in this
freeze and the slice addenda.

## 7. Budget

Registered node and index budgets for the family-blind search, stated before
any fit, identical for every arm: the descriptor-closure vocabulary index, the
two factor tables, and the scan window are all bounded and fixed in the
executor. Resource crossover (`R07`) varies these budgets and asserts the
held-out error is monotone in them.

## 8. Predictions, frozen before any outcome

Held-out frozen predictions are written to the frozen-prediction record
(`R08`) before the oracle is run, exactly as in
`gmi-833-h-real-scale-classical-v1`: the fit is completed on `n_fit`, the
prediction for each held-out query is emitted to the frozen record, and only
then is the independent oracle (Section R09) run and compared.

## 9. Falsifiers

A held-out exact prototype-agreement below the registered baseline, an
exact sign-decision error count above the registered bound, a null that
performs comparably to the family on the same slice rule, or any cross-scope
gate composition — any one falsifies the claim ceiling. The registered
numerical forms are in `FREEZE_V1_SLICE_ADDENDUM.md` section 7 so they cannot
be read after the fact.

## 10. Controls

Matched negative control (`R05`): a shuffled-label null with equal sample size
on the identical slice rule must perform at chance; a one-factor design null,
which destroys exactly ONE of the two stored factors at matched size while the
other stays intact, must fail to recover the family; and the other factor's
arm must stay intact under that corruption. The screen asserts `CLEAN` only
when the no-alarm case also fires.

## 11. Claim ceiling

`REAL_SCALE_ELEVEN_GATE_DERIVATION_OF_NAMED_CLASSICAL_FAMILY_AT_REGISTERED_SCOPE`
— all eleven coordinates R01–R11 at the single registered scope
`SIGMA_H18R`, self-contained, real-scale. Forbidden promotions (mirrored from
the parent real-scale packages): `CROSS_SCOPE_GATE_COMPOSITION`,
`REGISTERED_CONTROL_SUBSTITUTION`, `POST_HOC_FALSIFIER_REPLACEMENT`,
`ECOLOGY_ITERATION_UNTIL_POSITIVE`, `INDEPENDENT_TEAM_REPLICATION`, `M5`,
`EV4`, `EV5`, `REAL_SCALE_VALIDATION_COMPLETE`, `SECTION_H_COMPLETE`,
`ALL_KNOWN_FORM_RECOVERY`, `UNIVERSAL_GRAMMAR_NEUTRALITY`,
`FRONTIER_SCALE_VALIDATION`, `NAMED_FAMILY_ROW_CLOSED_OUTSIDE_THIS_PACKAGE`,
`FINITE_EVIDENCE_IMPLIES_REAL_SCALE`, `COMPLETE_GMI`.

# Grand GMI Learning-Law Selection Theorem V1

Status: **CONDITIONAL SELECTION OVER REGISTERED CONTRACTS; NO PREMISE-FREE DERIVATION CLAIMED**
Date: 2026-09-13

Ledger item 7. `OPTIMIZATION.md` derives each learning law *from* a premise:
O1 forces the gradient step from Euclidean movement, O2 forces mirror descent
and exponentiation from Bregman movement, O3 makes Bayesian updating the unique
minimiser under a likelihood premise, O4 derives reverse-mode credit assignment.
O0 states the hinge and stops there:

> "different premises select different mechanisms"

No registered unit supplies the converse map. This unit does, conditionally.

## 1. LLS-1 — the premise register

A **contract** is a pair `(K, pi)`: a capability set `K` drawn from seven
registered capabilities, and an exact price `pi(op)` for each of six charged
operations. Five laws are registered, each with the premises its source clause
requires and the operations it charges.

| law | premises | charges | clause |
|---|---|---|---|
| `GRADIENT_STEP` | differentiable objective, Euclidean geometry | gradient eval, projection | O1 |
| `MIRROR_DESCENT` | differentiable objective, simplex geometry | gradient eval, normalisation | O2 |
| `BAYES_UPDATE` | likelihood model, finite hypotheses, simplex geometry | likelihood eval, normalisation | O3 |
| `EXACT_SEARCH` | discrete program space | enumeration | core |
| `ORDINAL_HILL_CLIMB` | discrete program space, ordinal comparison | comparison | core |

A law is **admissible** at `K` iff its premises are a subset of `K`. Removing
any single premise removes the law; this is checked for every law and premise.

## 2. LLS-2 — the selection map is total

Let `A(K)` be the admissible set and `c(l, pi)` the sum of charged prices.
Define

- `INFEASIBLE_AT_CONTRACT` when `A(K)` is empty;
- `SELECTED(l)` when `l` uniquely minimises `c(., pi)` over `A(K)`;
- `UNDETERMINED_TIE` when the minimum is attained more than once.

Over the complete lattice of `2^7 = 128` capability sets the infeasible count
is 36. It is not asserted: it is recomputed from the closed-form predicate

`¬DISC ∧ ¬(DIFF∧EUC) ∧ ¬(DIFF∧SIMPLEX) ∧ ¬(LIK∧FINH∧SIMPLEX)`

and the two counts are required to agree.

The remaining 92 contracts split according to the price vector, and **LLS-6
shows the split is generic**: under any generic prices all 92 are `SELECTED`
and none are undetermined.

## 3. LLS-3 — resources select the law at fixed capabilities

This is the positive result. At a fixed capability set the selected law changes
with the price vector alone:

- `{differentiable, simplex, likelihood, finite hypotheses}` admits exactly
  `BAYES_UPDATE` and `MIRROR_DESCENT`. Cheap gradient evaluation selects mirror
  descent; cheap likelihood evaluation selects the Bayes update.
- `{discrete programs, ordinal comparison}` selects exact search when
  enumeration is cheap and hill climbing when comparison is cheap.
- `{differentiable, Euclidean, simplex}` selects the gradient step when
  projection is cheap and mirror descent when normalisation is cheap.

So "gradient learning rather than Bayesian updating" is decided by the
registered resource contract, not by the capability list and not by the author.

## 4. LLS-4 — hiding a premise leaves the law unidentified

Project contracts by deleting the geometry capabilities from the record. Two
contracts with the same projection receive different selected laws, so an
observer who does not record geometry cannot identify the law from the rest of
the contract. Recording the full contract does identify it. This is the
developmental-underdetermination argument moved from `D` to the law itself, and
it is a statement about the *record*, not about what is knowable in principle.

## 5. LLS-5 — what is refused

- **Premise-free selection is refused.** The empty contract returns
  `INFEASIBLE_AT_CONTRACT`. Per O0 the local decision rule is "an added,
  testable local decision premise, not an algebraic consequence of the word
  intelligence".
- **Unpriced operations refuse rather than default.** A missing price raises;
  it is never treated as zero.
- **Inexact prices are refused.** Float prices raise; all arithmetic is exact
  rational.
- `eta` and the geometry remain "part of the declared resource/accuracy
  contract, not a universal numeric constant predicted by GMI" (O0).

## 6. LLS-6 — the ties were an artifact of a degenerate probe

An earlier draft of this unit reported the census **at uniform prices** as
"36 infeasible, 50 selected, 42 undetermined" and treated the 42 as a property
of the selection law. That was a measurement artifact, and the root cause is
visible in the charge table: `GRADIENT_STEP`, `MIRROR_DESCENT` and
`BAYES_UPDATE` each charge exactly two operations, and `EXACT_SEARCH` and
`ORDINAL_HILL_CLIMB` each charge one. Equal arity plus equal unit prices forces
equal totals, so uniform prices are the one vector guaranteed to tie.

Call a price vector **generic** when no two registered laws' charged totals
coincide. Then:

- under uniform prices the tie locus is nonempty and ties appear;
- under generic prices the tie locus is empty, and the census is **36
  infeasible, 92 selected, 0 undetermined** — checked on two independent
  generic vectors that agree exactly;
- genericity is load-bearing, not incidental: setting `projection` equal to
  `normalization` in an otherwise generic vector reintroduces the
  `GRADIENT_STEP`/`MIRROR_DESCENT` tie on cue.

So the registered contract **determines** the learning law on every feasible
contract, except on the price-equality locus where two admissible laws cost
exactly the same. A tie is a coincidence of prices, not an incompleteness of
the selection law.

## 7. Scope and falsifiers

Not claimed: that the five registered laws exhaust machine learning; that the
charge model matches any physical cost; that a selected law converges or
generalises — L1–L4 own those under their own premises, and L5's two-world
countermodel already forbids universal improvement; that any architecture
follows, since AEM needs `(F, O, R, D)` and this unit supplies only `D`.

Falsified if a registered law is admissible without one of its premises, if the
census disagrees with the closed-form predicate, if any price flip fails to move
the selected law, or if a law is selected at the empty contract.

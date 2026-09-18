# GMI #833 Section AE10 — resource-bounded usable information: prospective freeze v1

Source `main`: `91c6d2876ba80c517a186e28fce3bdbe4e3fc218`.

Committed **before** any executor, oracle, test, receipt or reconciliation file
of this package exists in the tree.

## Rows this tranche may reconcile (verbatim, from issue comment 5692689542)

Anchor heading (verbatim, three hashes):

> `### AE10 — Resource-bounded usable information`

1. `- [ ] Define \`usable information\` relative to allowed computation, memory, communication, precision, time and energy budgets.`
2. `- [ ] Show exact examples where Shannon mutual information is identical but achievable task performance differs because decoding/search cost differs.`
3. `- [ ] Derive monotonicity/bounds as resource budgets relax.`
4. `- [ ] Relate to computationally constrained information measures / bounded rationality literature rather than inventing duplicate terminology.`
6. `- [ ] Add adversarial cryptographic/pseudorandom-style fixtures only at a mathematically defensible scope to separate information existence from feasible extraction.`

## Row explicitly NOT closed here

`- [ ] Determine whether GMI morphology selection is better predicted by raw information, usable information, or a vector of resource-conditioned sufficient statistics.`

That row requires pinned GMI morphology-selection receipts and is deferred to a
later tranche. It is recorded in `not_closed` of this package's reconciliation.

**No neighboring row is earned here.** No AE1, AE2 or other row, and no row of
the #833 issue body, is earned by this tranche.

## Frozen definitions

The **budget lattice** `B` is the finite product lattice, frozen here, of

- `k`: junta arity, the number of observed coordinates a rule may read;
- `d`: decision-tree depth, the branching budget of a rule;
- `m`: labelled-sample budget available for identification;
- `p`: observation precision, the number of retained leading bits;
- `c`: communication budget, the number of bits a rule may pass to its decision
  stage.

Budgets are ordered componentwise. `H_R` is the set of rules admissible under
`R`. `H` is monotone: `R <= R'` implies `H_R subset-or-equal H_{R'}`; this must
be proved for the frozen lattice, not assumed.

**Usable information** under budget `R` for a registered world `W` and a task
specification `T` (loss or utility) is frozen as the *achievability gap*

`U(W, T, R) = best achievable expected score over H_R  -  best achievable
expected score with no observation`,

an exact rational. `U` is defined relative to the rule class and the task, never
relative to an architecture. Time and energy budgets are registered as
*declared but not instantiated* dimensions of `B` in v1: the package must say so
explicitly rather than pretend they are measured.

## Required evidence and falsifiers

- `USE-1`: monotonicity. `U(W, T, R) <= U(W, T, R')` whenever `R <= R'`, proved
  from `H_R subset-or-equal H_{R'}`, and verified exhaustively over the entire
  frozen budget lattice for every registered world.
- `USE-2`: ceiling. `U(W, T, R) <= gain(W, T)` for all `R`, with `gain` the
  full-information optimum, and equality attained at the lattice top for at
  least one registered world. Verified exhaustively.
- `USE-3`: equal-Shannon separation. Two registered worlds with *exactly equal*
  mutual information whose usable information under the same budget differs
  exactly, the difference attributable to decoding cost; plus a second pair
  where the difference is attributable to identification/search cost at equal
  decoding cost. Both differences exact rationals.
- `USE-4`: unconditional pseudorandom-style fixture. A registered world in which
  the joint restricted to any proper subset of observed coordinates together
  with the target is exactly uniform, so that information exists globally while
  no budget-restricted rule below the registered arity beats base rate. The
  separation must be **unconditional**: no cryptographic hardness assumption may
  be invoked, and the package must state that it is not one.
- `USE-5`: terminology ledger. A machine-readable crosswalk mapping `U` onto the
  established parent notions it instantiates, with citations, stating which
  parts are parent-owned and what the residual is. Inventing a duplicate name
  without the crosswalk entry is a package defect.
- Two materially independent routes for every computational claim: an analytic
  route and a separately written brute-force oracle sharing no imports with it.
- Hostiles must be shown to move their target quantity before the checker is
  shown to flag them.
- A null the true result beats, with the no-alarm case asserted.
- Byte-identical `RESULT_V1.json` under `python3 -I -B` and `python3 -I -O -B`.

## Claim ceiling

`GMI_833_AE10_RESOURCE_BOUNDED_USABLE_INFORMATION_DEFINED_BOUNDED_AND_EXACTLY_SEPARATED_FROM_SHANNON_INFORMATION_AT_REGISTERED_FINITE_SCOPE`

## Forbidden promotions

`MUTUAL_INFORMATION_SUFFICIENT_FOR_INTELLIGENCE`,
`CRYPTOGRAPHIC_HARDNESS_ASSUMED`, `COMPLEXITY_CLASS_SEPARATION`,
`ENERGY_BUDGET_MEASURED`, `TIME_BUDGET_MEASURED`,
`GMI_MORPHOLOGY_PREDICTION`, `ARCHITECTURE_SELECTION_LAW`,
`INTELLIGENCE_EQUALS_COMPRESSION`, `COMPLETE_GMI`,
`NOVEL_INFORMATION_MEASURE`.

Parent-owned and not claimed novel: predictive V-information (Xu, Zhao, Song,
Ermon, Finn 2020), HILL pseudoentropy and computational entropy, bounded
rationality (Simon 1955; Russell and Subramanian 1995), resource-rational
analysis (Lieder and Griffiths 2020), rate-distortion theory, and the
unconditional parity lower bounds for decision trees and juntas. The residual
is the exact float-free finite instantiation on a frozen budget lattice with
machine-checked monotonicity and the equal-Shannon separation pair.

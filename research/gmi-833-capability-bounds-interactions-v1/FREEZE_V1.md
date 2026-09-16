# GMI #906 capability bounds/interactions freeze v1

Parent: #833 Section K. Source main: `9f90fc4ef961b7e9adccf7438488d1a64b9e68be`.

## Frozen closure target

This tranche targets exactly three proof-only rows:

- derive capability lower bounds as well as ceilings;
- derive capability interactions/synergies;
- derive capability interference under shared budgets.

It does not re-audit every capability definition, re-prove the historical eleven
ceilings, build a capability predictor, or close any empirical validation row.

## Frozen parent subtraction

The implementation must pin and import the merged #837 foundation, #848
morphology/capability contract, and #854 compact axiom core.  The historical
finite joint-threshold and shared-budget witnesses in
`gmi-capability-interactions-v3` may be repaired and lifted into the upgraded
contract.  The later unified theorem's rule that resource-channel overlap alone
determines interaction type is explicitly rejected: overlap neither guarantees
reuse nor rules out contention.

Frozen parent blobs:

- foundation result: `c0c574c4ec6e237d5fdafa694eac131399625a70`;
- morphology/capability result: `bdc5c3cd42e312d8c7af52f7ba84220631a25f8a`;
- axiom-core result: `3366a3bc7236d286f8d123bf53e4e3b2d22ad7b9`;
- historical interaction-tranche data: `40b24f58069777bcc3a3ccb3c68497d1e1e04d18`;
- historical unified theorem text: `294898059082ee55377bb0b73c1e55bd6a749847`.

## Frozen formal scope

- finite nonempty feasible realization classes and exact rational scores;
- external task/verifier/resource capability contracts, never architecture
  labels;
- constructive ceiling lower certificates kept distinct from uniform
  class-wide capability floors;
- a registered `2 x 2` intervention design with one unchanged external score
  functional and exact mixed finite difference;
- a finite product-capacity threshold microscope for strict complementarity;
- a mandatory maintenance charge drawn from the same hard resource budget for
  interference, paired with an old-feasible-set-preserving free-option control.

## Frozen theorem obligations

1. In a finite feasible class, the class-wide floor is the minimum score and the
   ceiling is the maximum score.  Any witnessed score lower-bounds the ceiling;
   it does not thereby lower-bound every class member.  Under class inclusion,
   the floor is nonincreasing and the ceiling nondecreasing.  Empty feasible
   classes return a typed nonnumeric result.
2. For the registered four-cell design, interaction is the mixed difference
   `s11-s10-s01+s00`; its sign classifies that design only.  In the product
   threshold witness, strict joint-only synergy holds iff baseline and both
   single upgrades miss the threshold while the joint upgrade reaches it.
3. With hard budget `R`, requirement `Q>0`, and unavoidable shared-budget charge
   `M>=0`, a previously capable system is harmed iff `R>=Q` and `R-M<Q`.
   Conversely, retaining every old feasible configuration as a free option
   cannot lower the optimum under the unchanged objective.

## Frozen falsifiers

The result is red if it confuses a witnessed ceiling lower certificate with a
uniform floor, reverses either inclusion monotonicity, assigns a numeric bound to
an empty feasible class, changes anything except one registered factor between
adjacent four-cell conditions, infers synergy from overlap alone, reports
interference without a load-bearing coupling, uses binary floating point, accepts
parent drift, or promotes the result beyond finite registered scope.

Allowed terminal only after analytic proof and exact replay:

`GMI_833_FINITE_CAPABILITY_BOUNDS_SYNERGY_AND_INTERFERENCE_AT_REGISTERED_SCOPE`

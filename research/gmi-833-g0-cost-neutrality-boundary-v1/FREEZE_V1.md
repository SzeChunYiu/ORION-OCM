# GMI #833 E7 — G0 cost-neutrality boundary freeze v1

**Parent:** #833 Section E  
**Child:** #891  
**Source main:** `97af465d8339d8c32cfcb2a6fd622c8be0a19d25`  
**Pinned E2 result blob:** `e903033615946a71f2f0859cda42e5b902e0d693`  
**Status:** pre-implementation theorem/evidence freeze

## Scientific question

Adjudicate, rather than assume, the row:

`Prove the grammar does not privilege a known family under the registered cost model.`

E2 already proves finite grammar-relative description/reachability bias. E7 therefore distinguishes family-**label** blindness from stronger representation/search neutrality.

## Registered raw coordinates and cost

For a finite grammar presentation `p`:

- `L(p)` = registered description/instruction length;
- `d(p)` = registered mutation distance from the frozen start.

Raw pair `(L,d)` remains primary.

For diagnostic scalarization only:

`C_w(p) = w_L L(p) + w_d d(p)`

with exact strictly-positive rational weights in frozen set:

- `w11=(1,1)`;
- `w21=(2,1)`;
- `w12=(1,2)`.

No family label, target identity, architecture name, or post-outcome score enters `C_w`.

## LABEL-1 — post-hoc family-label blindness

Freeze four post-hoc labels:

`FINITE_STATE`, `SYMBOLIC`, `PROBABILISTIC`, `NEURAL`.

Assign them bijectively to the four presentation nodes of the E2 remint fixture only as annotations. Exhaust all `4! = 24` label assignments. Because labels are not inputs to cost, every node cost, semantic-class minimum cost, Pareto relation and registered semantic selection must remain byte-identical for all three weight vectors.

This proves only label-name blindness.

## ISO-1 — isometric grammar-remint invariance

Consume E2's four-node finite grammar and all 24 node-name remints that preserve semantics, length, adjacency and start set. For each of three weight vectors, verify raw `(L,d)`, scalar costs, Pareto order and semantic selection are preserved. Target: `24*3 = 72` zero-failure remint/weight checks.

## STRUCT-NEG — stronger neutrality counterexample

Consume E2's same-semantics non-isometric `GA/GB` pair:

- `GA`: A has `(L,d)=(1,1)`, B `(2,2)`;
- `GB`: A has `(2,2)`, B `(1,1)`.

For every frozen positive weight vector, selection over `{A,B}` must reverse `A` in GA -> `B` in GB.

Therefore:

`same semantic coverage + family-label-blind cost != grammar neutrality`.

The stronger no-privilege statement is false at this registered scope.

## Cost-hostile audit

A cost declaration fails closed if it contains:

- nonzero family-label adjustment/bonus/penalty;
- target-identity adjustment;
- zero or negative primitive/resource price where strictly positive pricing is claimed;
- non-rational/float registered weight;
- missing raw `(L,d)` coordinates.

Frozen explicit hostiles:

- `family_adjustment={NEURAL:-1}` -> `FAMILY_LABEL_COST_PRIVILEGE`;
- `target_adjustment={targetA:-1}` -> `TARGET_SPECIFIC_COST_PRIVILEGE`;
- zero primitive price -> `ZERO_COST_PRIVILEGED_PRIMITIVE`.

## Pareto boundary

For every G0 registered presentation pair, strictly positive scalarization must preserve strict raw `(L,d)` Pareto dominance. Independent enumeration required.

Parent-owned incomparability control:

- x=(1,4), y=(4,1);
- w21=(2,1) selects x;
- w12=(1,2) selects y.

Thus positive weights preserve dominance but may reverse incomparable points.

## Terminals

Narrow positive:

`LABEL_BLIND_AND_ISOMETRICALLY_INVARIANT_AT_REGISTERED_SCOPE`

Row-level scientific disposition:

`NO_UNIVERSAL_GRAMMAR_NEUTRALITY__STRUCTURAL_BIAS_COUNTEREXAMPLE`

The row may be reconciled only with this negative/conditional wording, never as `G0_UNBIASED` or universal no-privilege.

## Claim ceiling

`GMI_G0_COST_LABEL_BLINDNESS_AND_STRUCTURAL_PRIVILEGE_BOUNDARY_AT_REGISTERED_SCOPE`

Forbidden:

- `G0_UNBIASED`
- `NO_KNOWN_FAMILY_PRIVILEGED_UNIVERSALLY`
- `REPRESENTATION_INVARIANT_COST_UNIVERSALLY`
- `SEARCH_NEUTRALITY_PROVED`
- `ARCHITECTURE_PRIOR_FREE_GRAMMAR`
- `ALL_SCALARIZATIONS_AGREE`
- `COMPLETE_GMI`

## Reconciliation boundary

Only after exact-head PR CI is green may #833's single no-privilege row be marked scientifically disposed, with the negative/conditional terminal above.

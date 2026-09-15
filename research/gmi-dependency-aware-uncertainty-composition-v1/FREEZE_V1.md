# #759 freeze — dependency-aware finite-DAG uncertainty composition V1

Date: 2026-09-15. Parent ledger: #602 section M. Child issue: #759.

This commit is the pre-implementation authority for this tranche. Before this commit on this branch there is no executor, hostile suite, scored receipt, formalization, or dedicated workflow for `gmi-dependency-aware-uncertainty-composition-v1`.

## Claim boundary

Target only:

```text
DEPENDENCY_AWARE_UNCERTAINTY_COMPOSITION_AT_REGISTERED_FINITE_DAG_SCOPE
```

This tranche may prove exact global feasible-assignment propagation for a finite typed DAG, dependence-safe coverage from a joint root confidence set and registered local relation-failure budgets, a marginal-root union-bound variant, soundness (but possible strict looseness) of node-local Cartesian propagation, and fail-closed missing-relation semantics.

It may not claim universal uncertainty propagation, calibrated real-world probabilities, independent root/stage failures, capability-prediction calibration, infinite-graph closure, continuous interval optimality, G6/G7, or complete GMI.

## Strongest parents / subtraction

No mathematical novelty is claimed over:

- finite constraint satisfaction and projection of a feasible relation;
- relational/set-valued image propagation;
- reachability/set propagation;
- Boole's inequality / Bonferroni union-bound accounting;
- classical dependency loss from replacing a joint feasible set by Cartesian products of marginals.

#657/RR-4 owns the registered affine shared-event special case. #748/#749 owns the sequential developmental specialization. #757 targets finite chain composition. #759 is the finite DAG/joint-dependence hardening.

The repository residual is the typed graph contract, exact global-vs-local comparison, explicit root-dependence accounting, fail-closed missing relations, bounded exhaustive certificate, hostile controls, deterministic receipt, and claim-boundary discipline.

## Frozen typed DAG object

A registered graph consists of:

```text
V             finite tuple of unique node names
R subseteq V  nonempty tuple of root nodes
Pa(v)         ordered tuple of parents for every non-root v
domain(v)     finite nonempty tuple of exact hashable values
Q_v           optional finite relation from parent tuples to domain(v)
beta_v        exact Fraction in [0,1] for every registered Q_v
outputs       nonempty tuple of requested output nodes
```

A relation row for non-root `v` is

```text
((x_p1,...,x_pm), y)
```

where every parent value lies in its registered parent domain and `y in domain(v)`.

Rules:

1. the directed parent graph must be acyclic;
2. every parent name must already belong to `V` and no node may parent itself;
3. parent order is semantically part of the relation signature;
4. roots have no local relation;
5. a registered relation may be partial and set-valued;
6. a missing relation is distinct from an empty registered relation;
7. missing relation means the complete local relation from the Cartesian parent domain to the full output domain;
8. a missing relation cannot claim a nonzero relation-failure budget;
9. all registration freezes before source activation/scoring;
10. post-activation mutation is rejected.

## Frozen root uncertainty contracts

### Joint-root contract

Let roots be ordered `R=(r_1,...,r_m)`. A joint confidence set is

```text
C_R subseteq product_j domain(r_j)
```

with registered exact source failure budget `alpha in [0,1]` and semantic assumption

```text
P(theta_R in C_R) >= 1-alpha.
```

The set may encode arbitrary dependence among roots. No factorization is implied.

### Marginal-root contract

If only marginal confidence sets `C_r subseteq domain(r)` are available with

```text
P(theta_r notin C_r) <= alpha_r,
```

the only registered joint set in V1 is

```text
C_R = product_r C_r
```

with source failure budget

```text
alpha_joint = min(1, sum_r alpha_r).
```

No product-of-coverages field is permitted without a separately registered dependence model.

## Frozen theorem DA-1 — global feasible-assignment coverage

Let `G=(V,E)` be any frozen finite DAG. Let true values `theta_v in domain(v)` exist on a common probability space. Let the joint root set obey

```text
P(theta_R in C_R) >= 1-alpha.
```

For each non-root node having registered relation `Q_v`, define the good event

```text
H_v = { ((theta_p)_(p in Pa(v)), theta_v) in Q_v }
```

and assume only

```text
P(H_v^c) <= beta_v.
```

No independence among root coverage or local relation events is assumed.

For a missing relation, use the complete relation and no `beta_v`; conditional on all true node values belonging to the registered domains, its local constraint is automatically satisfied.

Define the global feasible-assignment set

```text
A = {
  x_V in product_(v in V) domain(v) :
  x_R in C_R and
  ((x_p)_(p in Pa(v)), x_v) in Q_v^* for every non-root v
}
```

where `Q_v^*` is the registered relation when present and the complete local relation when missing.

For any nonempty output tuple `O`, define

```text
C_O = projection_O(A).
```

Then

```text
P(theta_O in C_O)
>= max(0, 1-alpha-sum_(registered non-root v) beta_v).
```

Stronger pathwise statement: on the intersection of root coverage and every registered `H_v`, the entire true assignment `theta_V` belongs to `A`, hence every output projection contains the true output simultaneously.

## Frozen theorem DA-2 — marginal-root union-bound contract

For marginal root sets with failure budgets `alpha_r`, define

```text
C_R = product_r C_r.
```

Then

```text
P(theta_R in C_R)
>= max(0, 1-sum_r alpha_r)
```

with no independence assumption, because failure of the Cartesian joint set is the union of marginal failures.

Combining with DA-1 gives

```text
P(theta_O in C_O)
>= max(0, 1-sum_r alpha_r-sum_v beta_v).
```

A multiplication such as `product_r (1-alpha_r)` is forbidden unless an appropriate independence premise is separately registered and proved.

## Frozen theorem DA-3 — local Cartesian propagation is sound

Define local node sets in a topological order.

For roots, use the coordinate projection of `C_R`:

```text
S_r = projection_r(C_R).
```

For non-root `v`, define

```text
S_v = Q_v^*[ product_(p in Pa(v)) S_p ].
```

Then for every node `v`,

```text
projection_v(A) subseteq S_v.
```

Therefore local forward propagation is a sound over-approximation of the exact global projection.

Proof target: topological induction. Any globally feasible assignment provides parent values lying in each parent local set by the induction hypothesis, so its child value must be included by the local relation image.

Equality is not promised.

## Frozen hostile DA-H1 — shared-ancestor dependency loss

Use exact domains

```text
X_x = {-1,+1}
X_a = {-1,+1}
X_b = {-1,+1}
X_y = {-2,0,+2}
```

with root set

```text
C_x = {-1,+1}
```

and exact zero-beta deterministic relations

```text
a = x
b = x
y = a - b.
```

The globally feasible assignments are exactly

```text
(-1,-1,-1,0)
(+1,+1,+1,0),
```

so

```text
projection_y(A) = {0}.
```

Node-local propagation gives

```text
S_a = S_b = {-1,+1}
```

and then forgets that `a=b`, forming the Cartesian parent product. Therefore

```text
S_y = {-2,0,+2}.
```

Required result:

```text
{0} proper-subset {-2,0,+2}.
```

The local result is sound but strictly looser. Any algorithm reporting `{0}` from only the two marginal parent sets must have preserved or reconstructed the shared-ancestor dependence by some additional joint representation.

Nearest false generalization: interval/set arithmetic on repeated or dependent quantities can be exact only when dependency information is retained; marginals alone do not encode that dependence.

## Frozen hostile DA-H2 — marginal-root product is unsound without independence

On equiprobable atoms

```text
Omega={a,b,c,d},
```

let root-1 confidence fail only at `a` and root-2 confidence fail only at `b`.

Then each marginal coverage is `3/4`, but joint root coverage is exactly

```text
1/2,
```

while an independence product gives

```text
9/16 > 1/2.
```

The union-bound lower bound `1-1/4-1/4=1/2` is attained.

Also include the complete-overlap control where both roots fail only at `a`: true joint coverage is `3/4`, while the same union lower bound is `1/2`, showing conservatism rather than equality.

## Frozen missing-relation semantics DA-4

For a non-root node `v` with no registered `Q_v`, define

```text
Q_v^* = product_(p in Pa(v)) domain(p) x domain(v).
```

For every nonempty parent feasible set, the local image is exactly `domain(v)`.

Globally, the missing relation imposes no coupling constraint beyond node-domain membership. Therefore it cannot narrow the global feasible assignments and cannot contribute a claimed relation-failure budget.

Downstream registered relations must propagate from this widened uncertainty. Copying one parent, choosing a nominal operator, or injecting a zero-width output is forbidden.

## Frozen nonlinear/set-valued control DA-C1

Use one root

```text
x in {-2,-1,0,1,2},
C_x={-1,0,1},
alpha=1/20.
```

Register exact relations

```text
s = x^2,
q in {s-1,s,s+1}.
```

with domains

```text
S={0,1,4},
Q={-1,0,1,2,3,4,5}.
```

Expected exact global and local projections are

```text
s={0,1}
q={-1,0,1,2}.
```

This control prevents an implementation that only handles affine or functional relations.

## Frozen joint-root dependence control DA-C2

Use roots

```text
r1,r2 in {0,1}
```

with joint source set

```text
C_R={(0,0),(1,1)}.
```

and exact child relation

```text
y = r1 XOR r2.
```

Global propagation gives

```text
y={0}.
```

Marginalizing roots first gives `S_r1=S_r2={0,1}` and local Cartesian propagation gives `S_y={0,1}`. This second strict-dependence control shows that loss can originate directly in a joint root confidence set, not only at a shared internal ancestor.

## Frozen exact budget control DA-C3

Use

```text
alpha = 1/20,
beta_a = 1/100,
beta_b = 1/200,
beta_y = 1/400.
```

Expected dependence-safe lower coverage:

```text
1 - 1/20 - 1/100 - 1/200 - 1/400
= 373/400.
```

For a two-root marginal contract with

```text
alpha_1=1/40,
alpha_2=1/40,
```

and the same stage budgets, expected lower coverage is also

```text
373/400.
```

No product shortcut may appear in the canonical receipt.

## Frozen exhaustive finite certificate DA-C4

Use binary domains for the graph

```text
x -> a
x -> b
(a,b) -> y.
```

Enumerate completely:

- all `4` root sets `C_x subseteq {0,1}`;
- all `4` deterministic Boolean functions `a=f(x)`;
- all `4` deterministic Boolean functions `b=g(x)`;
- all `16` deterministic Boolean functions `y=h(a,b)`.

Total:

```text
4 * 4 * 4 * 16 = 1024
```

registered deterministic DAGs/root-set cases.

For every case compute the exact global feasible output and the local Cartesian output, and require

```text
global_y subseteq local_y.
```

The receipt must expose the exact case count, failure count, and number of strict-overapproximation cases. At least one strict case is required; otherwise the certificate has failed to exercise dependency loss.

## Frozen graph/registration hostiles

The executor/tests must reject:

- directed cycles;
- unknown parent names;
- duplicate node names;
- duplicate parent names for one node;
- relation rows with wrong parent arity;
- relation endpoints outside registered domains;
- duplicate relation rows;
- non-Fraction or out-of-range budgets;
- a nonzero beta attached to a missing relation;
- output nodes not in the graph;
- root tuples with wrong arity or values outside root domains;
- post-activation graph/root/relation mutation.

A registered empty relation is legal and yields an empty feasible image; this must remain distinct from a missing relation, which is complete/fail-closed ignorance.

## Frozen result schema

Canonical `RESULT_V1.json` must include at least:

```text
schema
issue=759
parent_issue=602
freeze_commit
claim_ceiling
DA-1/2/3/4 proof classes
exhaustive certificate: cases/failures/strict cases
shared-ancestor hostile: global/local outputs
joint-root hostile: global/local outputs
marginal-root dependence hostile: true joint/product/union lower
nonlinear set-valued control
exact budget controls
missing-relation control
cycle/mutation hostile summary
forbidden claims
```

All finite probability quantities use exact `Fraction` arithmetic and canonical string serialization.

## Frozen falsifiers

This tranche is falsified if any of the following occurs:

- on a root-good/all-registered-relations-good path, the true output is absent from the global projection;
- any of the 1,024 exhaustive cases has `global_y` not a subset of `local_y`;
- the 1,024-case census contains no strict local over-approximation;
- the shared-ancestor hostile does not give global `{0}` and local `{-2,0,2}`;
- the joint-root XOR hostile does not give global `{0}` and local `{0,1}`;
- marginal-root accounting reports `9/16` as a guaranteed lower bound in the disjoint-quarter hostile;
- a missing relation narrows a nonempty node below its full registered domain;
- a registered empty relation is treated as missing/full-domain;
- a cycle or post-activation mutation is accepted;
- normal and `python -O` receipts differ byte-for-byte.

## Frozen proof/evidence classes

- DA-1 global feasible-assignment coverage: P1 theorem; exact controls P2.
- DA-2 marginal-root union-bound contract: P1 theorem; exact dependence hostile P2.
- DA-3 local Cartesian soundness/strict looseness: P1 theorem; bounded exhaustive certificate and hostiles P2.
- DA-4 missing relation/full-domain semantics: P1 theorem; P2 controls.

No P3/P4 real-scale or calibrated empirical probability claim is introduced.

## Required completion evidence

Completion requires, after this freeze commit:

- `FORMALIZATION_V1.md` with explicit quantifiers, domains, proofs, parent subtraction, assumptions, nearest counterexamples and claim ceiling;
- exact finite DAG executor and adversarial tests;
- deterministic `RESULT_V1.json` produced by the executor;
- normal and `python -O` test/replay with byte-identical receipt;
- dedicated CI with freeze-custody verification proving this freeze predates implementation/result artifacts;
- merge before reconciling #759. Because #757 also targets the #602 composition row, #759 must not double-toggle or broaden #602 beyond evidence actually merged.

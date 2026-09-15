# Dependency-aware uncertainty composition — formalization V1

Issue #759; parent ledger #602 Section M, row `Propagate uncertainty through composition`.

Pre-implementation authority: `FREEZE_V1.md`, commit `c90e7643c069ec6134d3750e1dbc4fc188c777ba`, committed before the executor, tests, result receipt or this formalization existed.

## Claim boundary and evidence classes

This capsule establishes only

```text
DEPENDENCY_AWARE_UNCERTAINTY_COMPOSITION_AT_REGISTERED_FINITE_DAG_SCOPE
```

for finite acyclic composition graphs with exact finite node domains and preregistered deterministic/set-valued relations.

Evidence classes:

- **UC-1, UC-2, UC-3, UC-4:** P1 set-theoretic/probability statements;
- **UC-5:** P1 interval special-case regression inherited from interval analysis;
- finite graph controls and hostiles: P2 exhaustive/exact executable evidence;
- no P4 empirical capability-calibration claim is made.

This is not a theorem that uncertainty stays small. Sound composition is allowed to widen uncertainty, including to a full domain.

## 1. Registered objects

Let `G=(V,E)` be a finite directed acyclic graph. For every node `v`, let `X_v` be a nonempty finite domain. Let

```text
Pa(v) = ordered tuple of parents of v
R = {v : Pa(v) is empty}
```

be the root set. The true graph state is a random vector

```text
theta = (theta_v)_{v in V},   theta_v in X_v.
```

A root confidence object is a set

```text
C_R subseteq product_{r in R} X_r
```

with one registered source failure budget `alpha` satisfying

```text
P(theta_R in C_R) >= 1-alpha.
```

For every non-root node `v`, a registered operator relation is

```text
Q_v subseteq (product_{p in Pa(v)} X_p) x X_v.
```

The V1 executable requires the relation to be total over the registered parent domain: each parent tuple has at least one admissible output. A deterministic operator has exactly one output for each parent tuple; a set-valued operator may have several.

For an `UNKNOWN_RELATION` node, V1 substitutes the universal relation

```text
Q_v^? = (product_{p in Pa(v)} X_p) x X_v.
```

This asserts no semantic relation beyond domain membership.

For an explicit relation, define the relation-good event

```text
H_v = { ((theta_p)_{p in Pa(v)}, theta_v) in Q_v }
```

and suppose the registered scientific premise is

```text
P(H_v^c) <= beta_v.
```

The executor records `beta_v`; it does not estimate or authenticate that premise.

## 2. UC-1 — global feasible-assignment propagation [P1/P3 consequence]

Define the globally feasible assignment set

```text
A(C_R,Q)
  = { x in product_{v in V} X_v :
        x_R in C_R
        and
        ((x_p)_{p in Pa(v)},x_v) in Q_v
        for every non-root v }.
```

For output nodes `O subseteq V`, define

```text
C_O = proj_O A(C_R,Q).
```

### Theorem UC-1

For every finite registered DAG,

```text
P(theta_O in C_O)
  >= 1 - alpha - sum_{v notin R} beta_v.
```

No independence among root coverage and relation-good events is required.

### Proof

Let

```text
G0 = {theta_R in C_R}
G* = G0 intersect (intersection_{v notin R} H_v).
```

On `G*`, the true full assignment `theta` satisfies every defining condition of `A(C_R,Q)`: its root tuple is in `C_R`, and every local parent/output tuple is in its relation. Therefore `theta in A`, hence `theta_O in proj_O A = C_O`.

Thus a composition-coverage failure can occur only outside `G*`. Boole's inequality gives

```text
P((G*)^c)
 <= P(G0^c) + sum_v P(H_v^c)
 <= alpha + sum_v beta_v.
```

Rearranging proves the claim. QED.

### Exact-relation corollary

If all `beta_v=0`, then the source confidence event is preserved:

```text
P(theta_O in C_O) >= 1-alpha.
```

This includes arbitrary deterministic nonlinear functions and arbitrary finite set-valued relations.

### Nearest false generalization

If a relation omits the true local parent/output tuple and no failure budget covers that possibility, output coverage can fail even when root coverage is perfect. Relation validity is load-bearing.

## 3. UC-2 — marginal root sets do not manufacture a joint event [P1]

Suppose one has only rootwise sets `C_r` with

```text
P(theta_r notin C_r) <= alpha_r.
```

Define

```text
C_R^prod = product_r C_r.
```

### Theorem UC-2

Without any independence premise,

```text
P(theta_R in C_R^prod)
 >= 1 - sum_r alpha_r.
```

### Proof

The complement of joint root coverage is the union of marginal failure events:

```text
{theta_R notin C_R^prod}
 = union_r {theta_r notin C_r}.
```

Apply Boole's union bound. QED.

The bound plugs into UC-1, yielding total failure at most

```text
sum_r alpha_r + sum_v beta_v.
```

### Why multiplication is invalid

The frozen 20-atom hostile uses two coverage events, each with probability `19/20`, whose failures occur on distinct atoms. Their joint coverage is

```text
18/20 = 9/10,
```

which exactly attains the union-bound lower bound. Multiplying marginals as if independent would instead report

```text
(19/20)^2 = 361/400.
```

Since `9/10 != 361/400`, marginal confidence labels do not establish independence.

## 4. UC-3 — local Cartesian propagation is sound but can be strictly looser [P1]

The global feasible set can be expensive because it preserves joint assignments. A cheaper local algorithm keeps only one set per node.

For roots define

```text
S_r = proj_r(C_R).
```

For non-roots define

```text
S_v
 = { y in X_v :
       exists (x_p) in product_{p in Pa(v)} S_p
       with (((x_p),y) in Q_v) }.
```

For an unknown relation, this definition gives `S_v=X_v`.

Let

```text
A_v = proj_v A(C_R,Q)
```

be the exact global projection at node `v`.

### Theorem UC-3

For every node,

```text
A_v subseteq S_v.
```

Hence local Cartesian propagation is a sound over-approximation of the global feasible projection.

### Proof

Proceed in a topological order.

For a root `r`, every globally feasible root assignment belongs to `C_R`, so its coordinate lies in `proj_r(C_R)=S_r`.

Assume the inclusion holds for all parents of a non-root `v`. Take any `y in A_v`. By definition of projection there exists one global feasible assignment `x` with `x_v=y`. For each parent `p`, `x_p in A_p subseteq S_p`. The same feasible assignment satisfies `((x_p),y) in Q_v`, so the parent tuple lies in the local Cartesian product and the local image includes `y`. QED.

### Strictness: shared-ancestor dependency

Freeze

```text
x in {-1,+1}
a=x
b=x
y=a-b.
```

Global feasible assignments preserve `a=b`, so

```text
A_y = {0}.
```

Local propagation retains only

```text
S_a=S_b={-1,+1}
```

and forms all Cartesian pairs, including impossible `(-1,+1)` and `(+1,-1)`. Therefore

```text
S_y={-2,0,+2}
```

and `A_y subsetneq S_y`.

This is the standard dependency problem in interval/set propagation: forgetting joint structure loses precision but remains safe when the extension is inclusion-preserving. Reporting `{0}` requires carrying the shared-ancestor equality or an equivalent joint representation.

## 5. UC-4 — unknown operator semantics must widen, not guess [P1/P5 boundary]

For an unknown node `v`, register the universal relation

```text
Q_v^? = (product parent domains) x X_v.
```

Then for every nonempty feasible parent set the node itself admits its full registered domain `X_v`; downstream relations may later collapse that uncertainty.

### Proof

For every parent tuple and every `y in X_v`, the universal relation contains the pair. Therefore every domain value is admissible at the unknown node. QED.

Frozen control:

```text
x=0
q in {0,1,2}, UNKNOWN_RELATION
y=q+1
```

gives

```text
q={0,1,2}
y={1,2,3}
CANNOT_IDENTIFY_UNKNOWN_RELATION.
```

A different downstream relation may collapse an unknown node to a constant output; in that case the output itself is identified despite upstream ignorance. The terminal therefore follows the actual propagated output set.

## 6. UC-5 — affine interval parent regression [P1/P2]

For

```text
y = a*x+b+e,
x in [L,U],
e in [Elo,Ehi],
```

the exact range over the rectangle is attained at corners because the map is affine in both inputs.

For the frozen parent control

```text
x in [1/4,3/4],
a=-2,
b=3,
e in [-1/10,1/10],
```

the corner values are `7/5, 8/5, 12/5, 13/5`, so the exact hull is

```text
[7/5,13/5].
```

This reproduces the #657 RR-4 affine special case and is only a regression/parent-subtraction control.

## 7. Frozen finite controls

### Nonlinear two-root graph

With full Cartesian root joint support

```text
x in {-2,-1,1,2}
z in {-1,+1}
sq=x^2
out=sq+z,
```

both global and local propagation give exactly

```text
{0,2,3,5}.
```

This is a positive control showing local propagation need not be loose when its Cartesian combinations correspond to feasible root combinations.

### Set-valued operator

For

```text
u in {0,1}
s in {u,u+1}
y=2s,
```

the exact output is

```text
{0,2,4}.
```

No stochastic distribution is inferred from multiple admissible outputs; this is set-valued epistemic uncertainty.

### Failure-budget dependence control

On 200 equiprobable atoms, source failure occupies 10 atoms, relation-1 failure two different atoms and relation-2 failure one further atom. The failure events are disjoint, hence

```text
1/20 + 1/100 + 1/200 = 13/200
```

and the actual joint-good probability is exactly `187/200`.

The product under an unjustified independence assumption would be

```text
(19/20)(99/100)(199/200)
= 374319/400000,
```

which differs from `187/200 = 374000/400000`. The union bound is exact in this hostile while independence is false.

## 8. Governance / software invariants

The V1 executor enforces:

1. graph finite and nonempty;
2. node names unique;
3. domains nonempty, exact `Fraction`, duplicate-free and canonically sorted;
4. parent names exist;
5. self-cycles/general cycles rejected;
6. explicit relation endpoints stay inside registered domains;
7. explicit relations are total over the full registered parent-domain product;
8. unknown and explicit relation semantics are mutually exclusive;
9. roots cannot have relation semantics or nonzero operator-failure budget;
10. unknown/universal relations carry zero misspecification budget because they make no restriction;
11. source root joint set is nonempty and domain-valid;
12. source/graph/output contracts lock at activation;
13. all failure budgets are exact `Fraction`s in `[0,1]`;
14. output nodes are registered and distinct.

The suite also verifies deterministic receipt reproduction under normal Python and `python -O`.

## 9. Complexity boundary

Exact global feasible propagation may require enumeration exponential in graph size/domain width. This capsule proves semantic correctness, not scalable inference.

The local algorithm can be cheaper but may over-enclose. Dependency-preserving symbolic constraints, factor graphs, affine arithmetic, zonotopes, BDDs, SAT/SMT and related methods are parent mechanisms for trading precision against computation; no GMI novelty is claimed for them.

## 10. Parent subtraction and literature

The core mathematics is parent-owned:

- interval/set range enclosure and inclusion isotony: Moore; Moore, Kearfott & Cloud;
- set-valued maps and reachable-set propagation: standard set-valued/reachability analysis;
- unknown dependence and Fréchet-style bounds: imprecise-probability literature;
- probability composition: Boole's union bound;
- repository special cases: #657/RR-4 (affine shared-event composition) and #748 (sequential developmental relation transport).

The repository contribution is the fail-closed typed DAG contract, exact dependency hostile, and integration with #602's explicit uncertainty ledger.

## 11. Falsifiers

This capsule is falsified at its registered scope by any of:

- a globally feasible node value missing from the reported local set;
- a true assignment satisfying registered root/relation premises but absent from the global feasible set;
- shared-ancestor global output containing `-2` or `+2`;
- shared-ancestor local output omitting `-2` or `+2`;
- multiplication of marginal confidence coverages without a registered independence premise;
- an unknown relation producing less than its full registered node domain before downstream constraints;
- an accepted cycle, out-of-domain relation endpoint or post-activation graph mutation;
- normal/optimized receipt drift.

## 12. #602 consequence

If the frozen controls, proof review and dedicated CI merge green, this capsule supports checking exactly one master row:

```text
M — Propagate uncertainty through composition.
```

It does not close the still-separate Section-M capability statistical calibration row.

# Dependency-aware finite-DAG uncertainty composition — formalization V1

Issue #759; parent ledger #602 Section M. Pre-implementation authority: `FREEZE_V1.md`, commit `9cc71b4876cc1f578d93df79cdbb6b042a995fec`, committed before the executor, hostile suite, result receipt, formalization, or dedicated workflow existed on the branch.

## 1. Claim boundary and review lenses

Claim ceiling:

```text
DEPENDENCY_AWARE_UNCERTAINTY_COMPOSITION_AT_REGISTERED_FINITE_DAG_SCOPE
```

The capsule is reviewed through three independent lenses.

1. **Formal-methods / constraint lens.** The exact uncertainty object is a joint feasible-assignment relation over a finite typed DAG. Output uncertainty is a projection of that relation, not a bag of independently propagated marginal intervals.
2. **Probability / confidence lens.** Deterministic feasible-set propagation is separated from probabilistic statements that the true assignment satisfies the root and local relation contracts. Failure budgets are combined only by inequalities valid under arbitrary dependence.
3. **Hostile-verification lens.** Every load-bearing assumption has a nearest finite counterexample. Shared-ancestor dependence and dependent roots are tested explicitly, and local-over-global inclusion is checked exhaustively on a complete bounded family.

No mathematical novelty is claimed for relational joins/projections, constraint satisfaction, set-valued propagation, Boole's inequality, Fréchet-type arbitrary-dependence bounds, or the classical dependency/wrapping problem of interval/set arithmetic. The repository residual is the exact typed contract, proof/claim boundary, hostile suite, exhaustive certificate, deterministic receipt, and fail-closed semantics.

Parent anchors include Moore/Kearfott/Cloud-style interval analysis and its dependence problem; set propagation/reachability analysis; classical Boole/Fréchet bounds; and relational join/projection semantics. Aho–Beeri–Ullman and Goodman–Shmueli are relevant database-theory parents for join/projection views of global relational constraints. #657/RR-4 owns a shared-event affine specialization, #748/#749 owns the developmental chain specialization, and #757 owns the simpler finite-chain composition result.

Evidence classes:

- DA-1 global feasible-assignment coverage: P1 theorem + P2 exact controls.
- DA-2 marginal-root dependence-safe contract: P1 theorem + P2 exact hostile.
- DA-3 local Cartesian soundness and strict looseness: P1 theorem + P2 exhaustive/hostile evidence.
- DA-4 missing-relation semantics: P1 theorem + P2 controls.

No P3 asymptotic or P4 empirical calibration claim is introduced.

---

## 2. Typed finite-DAG semantics

Let `G=(V,E)` be a finite directed acyclic graph. Every node `v in V` has a finite nonempty registered domain `X_v`. Let the root tuple be

```text
R=(r_1,...,r_m),   m>=1.
```

For every non-root node `v`, let

```text
Pa(v)=(p_1,...,p_d)
```

be its ordered tuple of parents. Parent order is part of the type of a local relation. A registered relation, when present, is

```text
Q_v subseteq (X_p1 x ... x X_pd) x X_v.
```

`Q_v` may be partial, nonfunctional, and set-valued. It need not be injective, surjective, total, or deterministic.

A missing relation is represented semantically by the complete relation

```text
Q_v^* = (X_p1 x ... x X_pd) x X_v.
```

A registered empty relation is instead `Q_v=emptyset` and means no parent/output tuple is feasible. The two cases are deliberately not conflated.

All domains, nodes, parent signatures, local relations, failure budgets, root contracts, and requested outputs are frozen before activation. Post-activation mutation is rejected.

---

## 3. Joint root confidence objects

Let the true root tuple be

```text
theta_R=(theta_r1,...,theta_rm)
```

on some probability space. A joint root confidence object is a finite set

```text
C_R subseteq X_r1 x ... x X_rm
```

with a registered source-failure budget `alpha in [0,1]` and premise

```text
P(theta_R in C_R) >= 1-alpha.          (R-JOINT)
```

The set `C_R` may encode arbitrary dependence among roots. No factorization is inferred from its coordinate projections.

For root `r_j`, define its marginal projection `pi_j(C_R)`. Always

```text
C_R subseteq product_j pi_j(C_R),
```

and inclusion can be strict. Replacing `C_R` by this Cartesian product therefore forgets dependence.

---

## 4. DA-2 — marginal-root contract under arbitrary dependence [P1]

Suppose only marginal confidence sets are registered:

```text
C_r subseteq X_r,
P(theta_r notin C_r) <= alpha_r.
```

Define `C_R^cart=product_r C_r`. Then

```text
theta_R notin C_R^cart
iff exists r: theta_r notin C_r.
```

Hence

```text
P(theta_R notin C_R^cart)
= P(union_r {theta_r notin C_r})
<= sum_r P(theta_r notin C_r)
<= sum_r alpha_r
```

by Boole's inequality. Therefore

```text
P(theta_R in C_R^cart)
>= max(0,1-sum_r alpha_r).              (DA-2)
```

No independence appears.

### Product hostile

Let `Omega={a,b,c,d}` with equiprobable atoms. Root-confidence failure 1 occurs only at `a`, failure 2 only at `b`. Each marginal coverage is `3/4`, but simultaneous coverage is exactly `1/2`, while

```text
(3/4)(3/4)=9/16 > 1/2.
```

Thus the independence product is not a guaranteed lower bound. The union lower bound `1-1/4-1/4=1/2` is attained. If both failures occur only at `a`, true simultaneous coverage is `3/4` while the union lower bound remains `1/2`, showing the valid bound may be conservative.

---

## 5. Global feasible-assignment object

For each non-root node with registered relation `Q_v`, define

```text
H_v = { ((theta_p)_(p in Pa(v)), theta_v) in Q_v }
```

and assume only

```text
P(H_v^c) <= beta_v.                    (REL-v)
```

No `beta_v` is attached to a missing relation: its complete relation contains every domain-valid tuple.

Let `Q_v^*` mean registered `Q_v` when present and the complete relation when missing. Define

```text
A = {
  x_V in product_(v in V) X_v :
  x_R in C_R and
  ((x_p)_(p in Pa(v)),x_v) in Q_v^*
  for every non-root v
}.
```

For requested output tuple `O=(o_1,...,o_k)`, define

```text
C_O^global = pi_O(A).
```

The implementation enumerates this finite relation exactly; enumeration is an evidence mechanism, not the theorem definition.

---

## 6. DA-1 — global feasible-assignment coverage [P1]

### Theorem

Assume the registered finite domains contain the true values, `(R-JOINT)` holds with failure `alpha`, and every registered local relation satisfies `(REL-v)` with failure `beta_v`. No independence assumption is made. Then

```text
P(theta_O in C_O^global)
>= max(0,1-alpha-sum_(registered non-root v) beta_v).
```

Stronger pathwise statement: on

```text
H = {theta_R in C_R}
    intersect
    intersection_(registered non-root v) H_v,
```

the entire true assignment `theta_V` belongs to `A`.

### Proof

Fix any outcome in `H`. Its root tuple belongs to `C_R`. Every registered local tuple belongs to its `Q_v` by the corresponding good event. Every missing-relation local tuple belongs to the complete `Q_v^*` automatically because all true values lie in their declared domains. Thus the true vector satisfies every constraint defining `A`, so `theta_V in A`. Projection yields `theta_O in pi_O(A)`.

Therefore

```text
H subseteq {theta_O in C_O^global}.
```

Moreover,

```text
H^c
= {theta_R notin C_R}
  union union_v H_v^c.
```

By Boole's inequality,

```text
P(H^c)
<= alpha + sum_v beta_v.
```

Hence `P(H)>=1-alpha-sum_v beta_v`; flooring at zero and using the event inclusion proves the theorem. QED.

Because the whole true assignment belongs to `A` on `H`, a multi-node requested output is covered jointly without an extra union bound merely for projecting several outputs.

---

## 7. Combining DA-1 and DA-2

With only marginal root sets, substitute the valid joint source failure

```text
alpha_joint <= sum_r alpha_r
```

into DA-1. This gives

```text
P(theta_O in C_O^global)
>= max(0,1-sum_r alpha_r-sum_v beta_v).
```

The two union bounds flatten algebraically; neither step assumes independence.

Frozen arithmetic control:

```text
alpha=1/20,
beta_a=1/100,
beta_b=1/200,
beta_y=1/400.
```

The total failure budget is `27/400`, so the exact lower bound is `373/400`. Two marginal root budgets `1/40,1/40` also union-bound to `1/20` and therefore yield the same `373/400` with the same local budgets.

---

## 8. Local Cartesian propagation

Define node sets in topological order. For a root `r`, set

```text
S_r = pi_r(C_R).
```

For a non-root `v`, form the local Cartesian parent set

```text
P_v^local = product_(p in Pa(v)) S_p
```

and propagate

```text
S_v = {y in X_v : exists z in P_v^local, (z,y) in Q_v^*}.
```

This representation keeps one marginal set per node. It discards joint constraints among parents unless those constraints are retained separately.

---

## 9. DA-3 — local propagation is sound but may be loose [P1]

### Theorem

For every node `v`,

```text
pi_v(A) subseteq S_v.
```

For several output nodes,

```text
pi_O(A) subseteq product_(o in O) S_o.
```

### Proof by topological induction

A finite DAG has a topological order.

For a root `r`, any `x_r in pi_r(A)` comes from a feasible assignment whose root tuple belongs to `C_R`; therefore `x_r in pi_r(C_R)=S_r`.

For a non-root `v`, assume the result holds for every parent. Take `y in pi_v(A)`. Some feasible assignment has child value `y`; each of its parent values belongs to the corresponding exact global parent projection and therefore, by induction, to the local parent set. Hence the ordered parent tuple lies in the local Cartesian parent product. Global feasibility also gives membership in `Q_v^*`, so `y` is included in the local relational image `S_v`. QED.

The theorem establishes inclusion only. Equality is not promised because the Cartesian product may recombine parent values that are separately possible but never jointly possible.

---

## 10. DA-H1 — shared-ancestor dependency loss [P2]

Freeze

```text
x in {-1,+1},
a=x,
b=x,
y=a-b.
```

The only globally feasible assignments are

```text
(-1,-1,-1,0)
(+1,+1,+1,0),
```

so the exact global output is

```text
pi_y(A)={0}.
```

Local propagation gives

```text
S_a=S_b={-1,+1}.
```

Their Cartesian product contains the infeasible cross pairs `(-1,+1)` and `(+1,-1)`, so local evaluation of `a-b` gives

```text
S_y={-2,0,+2}.
```

Thus

```text
{0} proper-subset {-2,0,+2}.
```

This is the finite relational analogue of the classical interval dependency example `x-x`: decorrelating repeated occurrences of one uncertain quantity widens the enclosure.

---

## 11. Joint-root dependence witness [P2]

Let `r1,r2 in {0,1}` with joint root set

```text
C_R={(0,0),(1,1)}
```

and exact `y=r1 XOR r2`. Global propagation preserves root equality and gives `y={0}`. Marginal root projections are both `{0,1}`; their Cartesian product introduces `(0,1)` and `(1,0)` and local propagation gives `y={0,1}`.

So dependence loss can originate directly in a non-Cartesian root confidence set, not only at a shared internal ancestor.

---

## 12. Complete bounded DA-3 certificate [P2]

The exact certificate fixes the binary graph

```text
x -> a
x -> b
(a,b) -> y
```

and enumerates:

- 4 root subsets `C_x subseteq {0,1}`;
- 4 unary Boolean functions `a=f(x)`;
- 4 unary Boolean functions `b=g(x)`;
- 16 binary Boolean functions `y=h(a,b)`.

Total:

```text
4*4*4*16 = 1024
```

cases. For every case it computes exact global and local output sets independently and checks `global_y subseteq local_y`.

Committed result:

```text
cases = 1024
failures = 0
strict_overapproximation_cases = 24.
```

The 24 strict cases demonstrate that the complete bounded universe actually exercises dependency loss. The census certifies the executor at P2; DA-3 itself is the P1 induction above.

---

## 13. DA-4 — missing relation means complete local ignorance [P1]

For a missing local relation at node `v`, let

```text
Q_v^* = (product_(p in Pa(v)) X_p) x X_v.
```

For every nonempty feasible parent set `T`, its relational image under `Q_v^*` is exactly `X_v`: one inclusion follows from typing, and for the reverse inclusion choose any `y in X_v` and any `z in T`; `(z,y)` belongs to the complete relation. QED.

Globally, the complete relation imposes no coupling constraint beyond node-domain membership. Therefore a missing operator cannot narrow the feasible set and cannot justify a nonzero relation-failure budget.

If the upstream feasible parent set is empty, its image is empty even under the complete relation. This prevents an upstream contradiction from becoming spurious possibility.

A registered empty relation is different: its image is empty for every parent set. Treating registered empty as missing would turn explicit impossibility into unconstrained possibility; dedicated tests forbid that conflation.

---

## 14. Nonlinear and set-valued control [P2]

Let

```text
x in {-2,-1,0,1,2},
C_x={-1,0,1},
alpha=1/20,
s=x^2,
q in {s-1,s,s+1}.
```

Then exact propagation gives

```text
s={0,1}
q={-1,0,1,2}.
```

Global and local propagation agree on this chain. Because all registered local relation failures are zero, DA-1 preserves the source lower coverage `19/20`. This control ensures the implementation is not restricted to affine, functional, or Boolean relations.

---

## 15. Assumption ledger and nearest counterexamples

**Domain adequacy.** The theorem assumes true values lie in the declared domains. If truth is outside a registered finite domain, even a complete missing relation cannot recover it; this is domain misspecification, not a projection failure.

**Valid root and relation budgets.** `alpha` and `beta_v` are semantic premises, not empirically established by this capsule. A falsely optimistic budget can invalidate the advertised coverage.

**Finite acyclic graph.** Topological propagation requires a DAG. A cycle needs additional fixed-point semantics; V1 rejects cycles rather than inventing one.

**Parent order.** Ordered parent signatures are load-bearing. For subtraction, swapping parents changes `a-b` to `b-a`.

**Joint dependence.** Marginals do not determine dependence. The shared-ancestor and diagonal-root controls are nearest counterexamples.

**Missing versus empty relation.** Missing means ignorance/full local relation; registered empty means impossibility. Conflating them reverses semantics.

**No independence from separate budgets.** Disjoint quarter failures give true simultaneous good probability `1/2`, below the product `9/16`.

**Local soundness is not local sharpness.** DA-3 is inclusion only; 24 of 1024 bounded cases are strict.

---

## 16. Exact software contract

The executor enforces without relying on Python `assert` semantics:

- unique node names and finite nonempty unique/hashable domains;
- known, unique, non-self parents;
- DAG acyclicity;
- exact relation arity and typed endpoints;
- no duplicate relation rows;
- exact `Fraction` budgets in `[0,1]`;
- roots cannot register local relations/budgets;
- missing relations cannot carry nonzero `beta`;
- registered outputs must exist;
- root contract order, tuple arity, endpoint membership, and uniqueness;
- no mutation after activation;
- registered empty relation distinct from missing relation;
- deterministic canonical receipt.

The suite contains 44 exact/adversarial tests and is run under normal Python and `python -O`. Both modes byte-reproduce the committed receipt.

---

## 17. Strongest-parent subtraction

The global feasible set is a finite join/conjunction of a root relation and local constraint relations followed by projection; this is ordinary relational/constraint mathematics. Node-local propagation is ordinary set-valued forward propagation. The shared-ancestor widening is the classical dependency/wrapping phenomenon from interval/set arithmetic. Confidence composition is an application of Boole's inequality and, in the two-event view, Fréchet bounds.

What is repository-specific is the auditable contract:

```text
joint root confidence relation
+ typed finite DAG relations
-> exact global feasible relation
-> output projection
+ registered relation-failure budgets
-> dependence-safe lower coverage
```

and the separately characterized local approximation:

```text
node marginals
-> Cartesian parent products
-> sound but potentially strict over-approximation.
```

---

## 18. Falsification registry row

```text
claim:
  A finite registered DAG's global feasible-assignment projection contains
  the true output on the root-good/operator-good event; local Cartesian
  propagation contains global node projections but can be strictly looser.

scope:
  Finite typed DAGs; exact finite domains/relations; registered joint or
  union-bounded marginal root confidence contracts.

assumptions:
  Domain adequacy; valid root/local failure budgets; frozen semantics;
  no unregistered independence.

strongest parent:
  Constraint/join-projection semantics + set-valued propagation +
  interval dependency analysis + Boole/Fréchet bounds.

prediction:
  Global output coverage >= max(0,1-alpha-sum beta_v); with marginal roots,
  alpha is at most sum alpha_r; exact global output is contained in local.

negative twin:
  Shared-ancestor and diagonal-root dependence produce strict local widening;
  missing relation produces full local output domain on nonempty parents.

falsifier:
  A good-event true assignment absent from A; any exhaustive case with
  global output outside local; dependence hostile not strict; product
  coverage guaranteed without independence; missing relation narrows;
  cycle/mutation accepted; normal and optimized receipts differ.

nearest counterexample:
  a=x,b=x,y=a-b gives global {0}, local {-2,0,2}; disjoint quarter-failures
  give joint good 1/2 versus independence product 9/16.

status:
  P1 theorems + P2 exact finite exhaustive/hostile certificate.
```

---

## 19. Claim disposition

The evidence supports only

```text
DEPENDENCY_AWARE_UNCERTAINTY_COMPOSITION_AT_REGISTERED_FINITE_DAG_SCOPE.
```

It does not support `UNIVERSAL_UNCERTAINTY_PROPAGATION`, `PROBABILISTIC_CAPABILITY_CALIBRATION`, `INDEPENDENCE_PROVED`, `REAL_SCALE_CALIBRATION`, `G6`, `G7`, or `COMPLETE_GMI`.

This hardens #602 Section M's composition-uncertainty lane by proving the joint-dependence case that a simple chain or marginal-only representation cannot express. It does not close the separate capability-calibration row or any complete-theory terminal.

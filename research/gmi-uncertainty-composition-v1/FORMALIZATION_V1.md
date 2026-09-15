# Exact finite uncertainty composition — formalization V1

Issue #757; parent ledger #602 Section M. Pre-implementation authority: `FREEZE_V1.md`, commit `417db4581fb66903eeba5c6bfb6e60a02719716d`, committed before this executor, test suite, result receipt, or dedicated workflow existed on the branch.

## 1. Claim boundary, expert lenses, and parent subtraction

Claim ceiling:

```text
SOUND_FINITE_UNCERTAINTY_COMPOSITION_FOR_REGISTERED_RELATIONS
```

Three independent lenses are used throughout this capsule.

1. **Formal methods / set-valued semantics.** Treat every stage as a preregistered relation and every uncertainty object as a set of admissible states. This prevents a functional or single-representative assumption from entering silently.
2. **Probability / confidence accounting.** Separate deterministic set propagation from probabilistic statements about whether the true path lies inside the registered sets/relations. Combine failure budgets only with inequalities valid under arbitrary dependence.
3. **Hostile verification.** Pair each load-bearing rule with the nearest small counterexample, and check the core set identity exhaustively over a complete bounded universe.

The mathematics is parent-owned. UC-1 is ordinary relational image/composition. UC-2 is a pathwise induction followed by Boole's inequality (union bound). UC-3 is finite possible-world/query semantics. UC-4 is the image of a nonempty set under the complete relation. Set propagation as a general reachability technique is standard; for example Althoff, Frehse & Girard (2021), *Set Propagation Techniques for Reachability Analysis*, review iterative propagation of sets under system dynamics for rigorous reachability over-approximations.

The repository residual is narrower: a generic finite registered contract, exact-rational dependence-safe budget algebra, a missing-relation fail-closed rule, explicit empty-set semantics, a complete 1,024-case certificate, deterministic replay, and hostile evidence that prevents an unjustified independence product from being substituted for the valid lower bound.

Evidence classes:

- UC-1: P1 theorem + P2 exhaustive finite certificate.
- UC-2: P1 theorem + P2 exact arithmetic/hostile controls.
- UC-3: P1 semantic equivalence + P2 query controls.
- UC-4: P1 theorem + P2 missing-relation control.
- UC-H1: P2 exact finite counterexample.
- No P3 asymptotic, P4 empirical, or universal-calibration claim is made.

Forbidden implications include `INDEPENDENT_STAGE_ERRORS`, `UNIVERSAL_UNCERTAINTY_CALIBRATION`, `REAL_WORLD_COVERAGE_PROVED`, `G6`, `G7`, and `COMPLETE_GMI`.

---

## 2. Registered finite semantics

Let

```text
X_0, X_1, ..., X_k
```

be finite nonempty sets, with `k >= 1`. For each stage `i=0,...,k-1`, register a relation

```text
R_i subseteq X_i x X_(i+1).
```

For a set `S subseteq X_i`, define the relational image

```text
R_i[S]
= { y in X_(i+1) : exists x in S such that (x,y) in R_i }.
```

For compatible relations

```text
R subseteq X x Y,
Q subseteq Y x Z,
```

define composition in execution order by

```text
Q o R
= { (x,z) in X x Z :
    exists y in Y such that (x,y) in R and (y,z) in Q }.
```

No totality, functionality, injectivity, surjectivity, invertibility, or independence assumption is implicit in these definitions.

The finite-set executor validates every endpoint against its declared domain. The semantic object is a set: repeated ways of reaching the same target are deduplicated. This matters operationally: the first implementation attempt accidentally retained multiplicities in an image, and the exhaustive certificate rejected it. The corrected implementation canonicalizes mathematical sets rather than paths.

---

## 3. UC-1 — exact image composition [P1]

### Theorem

For every finite sets `X,Y,Z`, every subset `S subseteq X`, and every relations

```text
R subseteq X x Y,
Q subseteq Y x Z,
```

we have

```text
Q[R[S]] = (Q o R)[S].
```

### Proof

Fix arbitrary `z in Z`. Then

```text
z in Q[R[S]]
```

iff, by definition of relational image,

```text
exists y in R[S] such that (y,z) in Q.
```

Expanding `y in R[S]` gives

```text
exists y in Y, exists x in S:
    (x,y) in R and (y,z) in Q.
```

By definition of relational composition, this is equivalent to

```text
exists x in S such that (x,z) in (Q o R),
```

which is exactly

```text
z in (Q o R)[S].
```

Since membership is equivalent for every `z in Z`, extensionality gives the set equality. QED.

### Functional specialization

If `R` and `Q` are graphs of functions `f:X->Y` and `g:Y->Z`, the relation theorem specializes to

```text
g[f[S]] = (g o f)[S].
```

No separate theorem is needed; functions are a strict special case of relations.

### Exhaustive bounded certificate

The P2 certificate takes

```text
X=Y=Z={0,1}.
```

There are exactly

```text
2^2 = 4
```

possible source subsets, and

```text
2^(2*2) = 16
```

relations for each of `R` and `Q`. Therefore the complete bounded universe contains

```text
4 * 16 * 16 = 1024
```

triples `(S,R,Q)`.

The executable enumerates all 1,024 and independently computes both sides. The committed result records

```text
cases    = 1024
failures = 0.
```

This does not prove UC-1 by sampling; UC-1 is already P1. The enumeration certifies that the finite implementation agrees with the theorem on the complete registered bounded universe.

---

## 4. UC-2 — finite-chain coverage under arbitrary dependence [P1]

### Registered probabilistic objects

Let random variables

```text
X_i^true in X_i
```

represent the true states. Let `S_0 subseteq X_0` be the registered source uncertainty set (possibly itself random) and suppose only

```text
P(X_0^true in S_0) >= 1-alpha,
```

with `alpha in [0,1]`.

For stage `i`, define the registered-good event

```text
G_i
= { (X_i^true, X_(i+1)^true) in R_i }.
```

Assume only the marginal failure bound

```text
P(G_i^c) <= beta_i,
```

where `beta_i in [0,1]`.

No independence is assumed between:

- source coverage and any stage event;
- two different stage events;
- any hidden common cause driving several failures.

Define the propagated sets recursively by

```text
S_(i+1) = R_i[S_i].
```

### Pathwise lemma

On the event

```text
H
= {X_0^true in S_0}
  intersect G_0
  intersect ...
  intersect G_(k-1),
```

we have

```text
X_i^true in S_i
```

for every `i=0,...,k`.

### Proof

The base case `i=0` holds by the first conjunct defining `H`.

For the induction step, assume `X_i^true in S_i`. Because `H subseteq G_i`, we also have

```text
(X_i^true, X_(i+1)^true) in R_i.
```

By the definition of relational image, a target related by `R_i` to any member of `S_i` belongs to `R_i[S_i]`. Therefore

```text
X_(i+1)^true in R_i[S_i] = S_(i+1).
```

Induction proves the claim. QED.

### Coverage theorem

Because `H` implies `X_k^true in S_k`,

```text
P(X_k^true in S_k) >= P(H).
```

The complement of `H` is

```text
H^c
= {X_0^true notin S_0}
  union G_0^c
  union ...
  union G_(k-1)^c.
```

By Boole's inequality,

```text
P(H^c)
<= P(X_0^true notin S_0) + sum_i P(G_i^c)
<= alpha + sum_i beta_i.
```

Hence

```text
P(H)
= 1 - P(H^c)
>= 1 - alpha - sum_i beta_i.
```

Since probabilities cannot be negative,

```text
P(X_k^true in S_k)
>= max(0, 1-alpha-sum_i beta_i).
```

QED.

### Why no independence appears

The derivation uses only a union upper bound on failure events. Product rules such as

```text
P(intersect_i G_i) = product_i P(G_i)
```

are equalities only under appropriate independence assumptions. They are not conservative lower bounds in arbitrary dependence.

This distinction is load-bearing. A confidence budget is not a license to assume how failures overlap.

### Frozen exact arithmetic control

For

```text
alpha  = 1/20,
beta_0 = 1/100,
beta_1 = 1/200,
```

the theorem gives

```text
1 - 1/20 - 1/100 - 1/200
= 1 - (10+2+1)/200
= 187/200.
```

The executor represents every budget as `fractions.Fraction`; no floating rounding or hidden product is used.

---

## 5. UC-H1 — disjoint failures refute the independence-product shortcut [P2]

Take the equiprobable sample space

```text
Omega = {a,b,c,d},
P({omega}) = 1/4.
```

Let two stage failure events be

```text
F_1={a},
F_2={b},
```

and `G_i=F_i^c`.

Then

```text
P(G_1)=P(G_2)=3/4.
```

Because the failures are disjoint,

```text
G_1 intersect G_2 = {c,d},
P(G_1 intersect G_2)=1/2.
```

An unjustified independence product would report

```text
(3/4)(3/4)=9/16.
```

But

```text
9/16 > 1/2,
```

so `9/16` is not even a valid lower bound here.

The dependence-safe union-bound lower bound is

```text
1 - P(F_1)-P(F_2)
= 1 - 1/4 - 1/4
= 1/2,
```

and is attained exactly.

This is also the two-event Fréchet lower bound for the intersection when only the marginals are known:

```text
P(G_1 intersect G_2)
>= max(0, P(G_1)+P(G_2)-1).
```

### Overlap control: the valid lower bound may be conservative

Now take

```text
F_1=F_2={a}.
```

Then the union-bound lower bound remains `1/2`, but the true joint-good probability is

```text
P(G_1 intersect G_2)=3/4.
```

Thus the theorem is sound under arbitrary dependence, not necessarily sharp. The capsule makes no claim that the bound equals true coverage.

---

## 6. UC-3 — Boolean query identifiability [P1]

Let `S subseteq X` be a nonempty propagated uncertainty set and

```text
q : X -> {False,True}
```

a registered Boolean query.

### Definition

The query is identifiable from `S` iff every state still admitted by `S` gives the same answer.

Equivalently,

```text
q is identifiable on S
iff |q[S]| = 1.
```

### Theorem

For nonempty `S`:

- if `q(x)=True` for every `x in S`, the only sound answer is `IDENTIFIED_TRUE`;
- if `q(x)=False` for every `x in S`, the only sound answer is `IDENTIFIED_FALSE`;
- if there exist `x,y in S` with `q(x) != q(y)`, the answer is `CANNOT_IDENTIFY`.

### Proof

If `q` is constant, every state compatible with the uncertainty object entails the same Boolean proposition, so that proposition is determined.

Conversely, if both Boolean values occur on admissible states, then the uncertainty object itself does not distinguish which answer is true. Returning either Boolean would exclude an admitted possible state without evidence. Therefore no Boolean value is identified. QED.

### Empty-set guard

Classical logic makes universal statements over the empty set vacuously true. Using that convention directly in an identification API would be dangerous: both “all states satisfy q” and “all states fail q” can become vacuous.

Accordingly, this contract gives the empty propagated set a separate terminal:

```text
INCONSISTENT_EMPTY_IMAGE.
```

It never maps an empty image to `IDENTIFIED_TRUE` or `IDENTIFIED_FALSE`.

This is not a new theorem; it is a safety-critical semantic choice preventing inconsistency from masquerading as certainty.

---

## 7. UC-4 — missing relation means full target ignorance [P1]

Suppose a stage declares only finite domains

```text
X != empty,
Y != empty
```

and no coupling information between them.

The least informative registered relation is the complete relation

```text
C = X x Y.
```

### Theorem

For every nonempty `S subseteq X`,

```text
C[S] = Y.
```

### Proof

First, by definition of relational image, `C[S] subseteq Y`.

For the reverse inclusion, choose arbitrary `y in Y`. Since `S` is nonempty, choose `x in S`. Because `C=X x Y`, `(x,y) in C`. Therefore `y in C[S]`. Since `y` was arbitrary, `Y subseteq C[S]`. QED.

### Consequence

A missing coupling relation must propagate to the full registered target domain:

```text
S_next = Y,
marker = MISSING_RELATION_FULL_DOMAIN.
```

It is unsound to copy the source set forward unless an identity or other coupling relation has actually been registered.

### Nearest counterexample to “just copy the old set”

Take

```text
X={0}, Y={1},
S={0}.
```

Source coverage can be one: the source truth is certainly `0`. If the true update sends `0` to `1`, copying `{0}` into the target state space has zero target coverage and is not even a subset of `Y`. The full-domain target `{1}` is the only sound ignorance set without more coupling information.

### No invented relation-failure budget

A missing relation has no registered good-event semantics, so the implementation does not charge or claim a `beta` for it. It widens the set to the full target domain. Any downstream query remains identifiable only if it is constant over that full domain.

This is intentionally different from a registered but uncertain relation, for which `beta_i` has a declared event meaning.

---

## 8. Heterogeneous-carrier control [P2]

The frozen exact chain deliberately uses different carrier types/cardinalities:

```text
X0 = {0,1,2}
X1 = {"a","b"}
X2 = {10,20,30,40}
S0 = {0,2}
```

with

```text
R0 = {
  (0,"a"),
  (1,"a"),
  (2,"b")
}

R1 = {
  ("a",10),
  ("a",20),
  ("b",30),
  ("b",40)
}.
```

Sequential propagation gives

```text
S1 = R0[S0] = {"a","b"},
S2 = R1[S1] = {10,20,30,40}.
```

Direct composition gives

```text
(R1 o R0)[S0] = {10,20,30,40},
```

exactly matching UC-1.

This control is intentionally not a single homogeneous integer carrier. It catches implementations that accidentally treat relation composition as matrix/index composition over one shared state universe rather than typed source/target relations.

The frozen target queries are:

```text
q_even(x)  = (x mod 2 == 0)
q_gt_25(x) = (x > 25)
q_le_40(x) = (x <= 40).
```

On `S2=X2` the exact outcomes are

```text
q_even  -> IDENTIFIED_TRUE
q_gt_25 -> CANNOT_IDENTIFY
q_le_40 -> IDENTIFIED_TRUE.
```

The same query outcomes occur in the missing-relation control only because the missing relation widens to exactly this full `X2`. The distinct marker `MISSING_RELATION_FULL_DOMAIN` remains present so “known relation happened to cover the whole target” is not confused with “no coupling relation was known.”

---

## 9. Assumption ledger and nearest counterexamples

### A1. Registered domains are the intended semantic universes

If the true state lies outside the declared domain, none of the finite set theorems can rescue the registration. The executor checks internal endpoint consistency, not ontological completeness of the domain.

**Nearest counterexample:** declare target domain `{0}` while the physical target can be `1`. Full-domain fail-closed propagation returns `{0}` and still misses the true target. The error is domain misspecification, not relation composition.

### A2. Stage failure bounds are valid

UC-2 assumes

```text
P(G_i^c) <= beta_i.
```

The capsule does not estimate, calibrate, or authenticate this inequality.

**Nearest counterexample:** actual `P(G_i^c)=1/2` but declare `beta_i=0`. The reported bound can fail. This is why `REAL_WORLD_COVERAGE_PROVED` is forbidden.

### A3. Finite chain

The theorem is stated for every finite registered `k`. It does not silently infer an infinite-horizon simultaneous-coverage statement.

An infinite-horizon result requires a summable allocation or another explicit argument. #748 contains a developmental specialization with a summable countable budget; that is not imported here.

### A4. Boolean query is evaluated on the whole admitted set

Selecting one representative state is insufficient.

**Nearest counterexample:** `S={0,1}`, `q(x)=(x=1)`. Evaluating only at representative `0` returns false even though `1` remains admitted. The only set-sound terminal is `CANNOT_IDENTIFY`.

### A5. Independence is not registered

Without an independence proof, product coverage is not licensed.

**Nearest counterexample:** UC-H1 gives exact `1/2` joint good probability while the product is `9/16`.

### A6. Nonempty source for the complete-relation image theorem

`(X x Y)[empty]=empty`, not `Y`.

The implementation therefore distinguishes empty inconsistency from ordinary nonempty ignorance. UC-4's full-target conclusion explicitly quantifies only over nonempty source sets.

---

## 10. Exact software contract and adversarial discipline

The executable enforces, without relying on Python `assert` statements:

- finite nonempty registered domains;
- no duplicate domain elements;
- relation endpoints belong to the registered typed source/target domains;
- no duplicate relation pairs;
- source sets are registered subsets;
- compatible stage chaining;
- exact `Fraction` probability budgets in `[0,1]`;
- coverage lower bound floored at zero;
- missing relations widen to the full target domain;
- mutation after campaign activation is rejected;
- empty images have their own terminal;
- deterministic canonical result serialization.

The test suite includes:

- the full 1,024-case UC-1 universe;
- heterogeneous carriers;
- functional specialization;
- invalid endpoints and duplicate objects;
- exact `187/200` budget arithmetic;
- zero-floor behavior;
- constant/mixed/empty query cases;
- complete-relation/missing-relation behavior;
- post-activation mutation rejection;
- disjoint-failure hostile;
- overlapping-failure conservatism control;
- canonical receipt determinism.

The same suite is run under normal Python and `python -O`, and the committed receipt must be byte-identical under both modes. Thus no proof obligation depends on optimization-sensitive `assert` behavior.

---

## 11. Parent comparison and what remains genuinely open

### Relation/set propagation parents

Relational image and composition are elementary set theory/relation algebra. Reachable-set propagation is standard in formal verification and control. This capsule does not claim a new relation algebra or reachability theorem.

### Probability parents

UC-2 is an application of Boole's inequality. For two events, the exact dependence-robust lower envelope using only marginal probabilities is the classical Fréchet bound

```text
max(0, P(A)+P(B)-1).
```

The hostile demonstrates why this parent result, not an independence product, owns the inference.

### GMI-specific residual

What is repository-specific is the *contract and evidence discipline*:

```text
registered finite relation
-> exact set image
-> separately registered failure budget
-> dependence-safe confidence lower bound
-> query constancy or abstention
-> fail-closed full target on missing coupling
-> exhaustive/hostile receipt.
```

That discipline closes one ledger row. It does not establish that GMI's capability uncertainty is calibrated, that developmental transition laws are correct, or that any real-world distribution obeys a declared budget.

---

## 12. Falsification registry row

```text
claim:
  Finite registered relational composition transports source-set
  uncertainty soundly, and registered source/stage failure budgets
  compose by a dependence-safe union bound.

scope:
  Finite nonempty registered state spaces; finite chain; exact finite
  relations; Boolean downstream query semantics.

assumptions:
  Source coverage bound valid; each registered stage failure bound valid;
  relation/domain registrations semantically correct; no unregistered
  independence used.

strongest parent:
  Relational image/composition + set propagation/reachability +
  Boole/Fréchet probability bounds.

prediction:
  UC-1 identity holds exactly; final coverage is at least
  max(0,1-alpha-sum beta_i); query is identified iff constant on target set.

negative twin:
  Missing relation widens to full target domain; mixed query abstains.

falsifier:
  Any of the 1024 exact UC-1 cases fails; hostile needs stronger than
  1/2 without independence; missing relation narrows a nonempty source
  below full target; mixed/empty query is falsely identified.

nearest counterexample:
  Disjoint quarter-failure events refute product coverage; arbitrary update
  refutes source-set copying.

status:
  P1 theorem + P2 exact finite executable certificate at registered scope.
```

---

## 13. Final claim disposition

The exact theorems, hostile controls, and executable certificate support only:

```text
SOUND_FINITE_UNCERTAINTY_COMPOSITION_FOR_REGISTERED_RELATIONS
```

They do **not** support:

```text
INDEPENDENT_STAGE_ERRORS
UNIVERSAL_UNCERTAINTY_CALIBRATION
REAL_WORLD_COVERAGE_PROVED
G6
G7
COMPLETE_GMI
```

Accordingly, this artifact is sufficient to reconcile only #602 Section M:

```text
Propagate uncertainty through composition.
```

No neighboring M, O, P, V, or final-complete-theory box is implied by this result alone.

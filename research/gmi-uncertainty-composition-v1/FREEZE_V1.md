# #757 freeze — finite uncertainty composition V1

Date: 2026-09-15. Parent ledger: #602 section M. Child issue: #757.

This commit is the pre-implementation authority for this tranche. Before this commit on this branch there is no executor, test oracle, scored result, receipt, or dedicated workflow for `gmi-uncertainty-composition-v1`.

## Claim boundary

Target only:

```text
SOUND_FINITE_UNCERTAINTY_COMPOSITION_FOR_REGISTERED_RELATIONS
```

This tranche may prove exact set-image composition for finite registered relations, dependence-safe transport of a source coverage guarantee through finitely many registered stage relations, and fail-closed Boolean-query semantics when a relation is missing.

It may not claim independent stage errors, universal uncertainty calibration, Bayesian/posterior calibration, real-world coverage, G6 capability prediction, G7 developmental prediction, or complete GMI closure.

The developmental specialization remains owned by #748/#749. This issue is intentionally generic composition.

## Strongest parents / subtraction

The mathematical backbone is parent-owned:

- ordinary relation composition and relational image;
- image of a set under a function as the functional special case;
- Boole's inequality / the union bound;
- ordinary confidence-set propagation through known maps or set-valued maps.

The repository residual is only the exact finite registered contract, explicit no-independence budget algebra, missing-relation fail-closed semantics, exhaustive finite certificate, hostile dependence witness, deterministic receipt, and claim-boundary discipline.

## Frozen finite objects

For a registered chain length `k >= 1`, freeze finite nonempty sets

```text
X_0, X_1, ..., X_k
```

and relations

```text
R_i subseteq X_i x X_(i+1),   i = 0,...,k-1.
```

For a set `S subseteq X_i`, define the exact relational image

```text
R_i[S] = { y in X_(i+1) : exists x in S, (x,y) in R_i }.
```

For compatible relations `R subseteq X x Y` and `Q subseteq Y x Z`, define composition in execution order

```text
Q o R = { (x,z) : exists y in Y, (x,y) in R and (y,z) in Q }.
```

No totality, functionality, injectivity, surjectivity, or independence premise is implied unless explicitly registered by a particular control.

## Frozen theorem UC-1 — exact relational-image composition

For every finite `X,Y,Z`, every `S subseteq X`, every `R subseteq X x Y`, and every `Q subseteq Y x Z`,

```text
Q[R[S]] = (Q o R)[S].
```

The implementation must check this identity exhaustively over a bounded complete universe, not only on hand-picked examples.

Functional specialization: if `R` and `Q` are graphs of functions `f` and `g`, then the theorem reduces to

```text
g[f[S]] = (g o f)[S].
```

No novelty is claimed for either identity.

## Frozen theorem UC-2 — finite-chain coverage without independence

Let random variables `X_i^true` take values in the registered finite spaces `X_i`. Let `S_0 subseteq X_0` be a random or deterministic source uncertainty set satisfying

```text
P(X_0^true in S_0) >= 1 - alpha,
```

where `alpha in [0,1]`.

For each stage `i`, define the registered-good event

```text
G_i = { (X_i^true, X_(i+1)^true) in R_i }
```

and assume only

```text
P(G_i^c) <= beta_i,
```

with each `beta_i in [0,1]`. No independence among the source event or any stage-good events is assumed.

Define recursively

```text
S_(i+1) = R_i[S_i].
```

Then for every finite `k`,

```text
P(X_k^true in S_k)
>= P({X_0^true in S_0} intersect G_0 intersect ... intersect G_(k-1))
>= max(0, 1 - alpha - sum_i beta_i).
```

The first inequality is pathwise implication by induction. The second is Boole's inequality applied to failure events.

The executor may only propagate registered `alpha` and `beta_i`; it does not estimate or authenticate those budgets from data.

## Frozen theorem UC-3 — Boolean query identifiability

For a propagated target set `S_k subseteq X_k` and a registered Boolean query

```text
q : X_k -> {False, True},
```

`q` is identifiable from the propagated set iff it is constant on `S_k`.

Exact terminal semantics:

- all `q(x)=True` on nonempty `S_k` -> `IDENTIFIED_TRUE`;
- all `q(x)=False` on nonempty `S_k` -> `IDENTIFIED_FALSE`;
- both values occur -> `CANNOT_IDENTIFY`;
- empty propagated set -> `INCONSISTENT_EMPTY_IMAGE`, never a positive identification.

A Boolean result is therefore a statement about constancy on the registered uncertainty set, not about a selected representative.

## Frozen theorem UC-4 — missing relation fails closed

If a stage from `X_i` to registered target domain `X_(i+1)` has no registered coupling relation, the sound default relation is the complete relation

```text
X_i x X_(i+1).
```

For every nonempty `S_i`, its image is exactly the full target domain `X_(i+1)`.

Therefore missing relation semantics are:

```text
S_(i+1) = X_(i+1)
```

with terminal marker `MISSING_RELATION_FULL_DOMAIN`.

No inherited stage confidence narrower than the source-plus-registered-budgets claim may be manufactured. A downstream Boolean query can still be identified only when it is constant on the full target domain.

Nearest false generalization: copying `S_i` forward across an arbitrary stage can give zero target coverage even if source coverage is one.

## Frozen hostile UC-H1 — multiplication is unsound without independence

Use a four-point probability space with equiprobable atoms

```text
Omega = {a,b,c,d},  P(omega)=1/4.
```

Define two stage failure events

```text
F_1 = {a}
F_2 = {b}.
```

Then

```text
P(F_1)=P(F_2)=1/4,
P(G_1)=P(G_2)=3/4,
P(G_1 intersect G_2)=1/2.
```

The independence product would be

```text
(3/4)(3/4) = 9/16,
```

which is strictly larger than the true joint-good probability `1/2` and therefore is not a sound lower bound without independence.

The union-bound lower bound is

```text
1 - 1/4 - 1/4 = 1/2,
```

which is attained exactly by this hostile.

The test must also include a perfectly overlapping-failure control to demonstrate that the union bound can be conservative rather than exact.

## Frozen exhaustive certificate universe

The bounded complete UC-1 certificate uses

```text
X = Y = Z = {0,1}.
```

There are:

- `2^2 = 4` subsets `S subseteq X`;
- `2^(2*2) = 16` binary relations `R subseteq X x Y`;
- `16` binary relations `Q subseteq Y x Z`;
- `4 * 16 * 16 = 1024` exact identity cases.

All 1024 cases must be enumerated and checked. The receipt must expose the exact case count.

A second deterministic chain control uses three finite spaces with different cardinalities so an implementation that accidentally assumes one shared carrier cannot pass.

## Frozen concrete chain control

Use

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

Expected exact images:

```text
S1 = {"a","b"}
S2 = {10,20,30,40}
```

and direct composed image must equal `S2` exactly.

Use source/stage budgets

```text
alpha  = 1/20
beta_0 = 1/100
beta_1 = 1/200
```

so the exact registered lower coverage is

```text
1 - 1/20 - 1/100 - 1/200 = 187/200.
```

No product-of-coverages field is permitted in the canonical result schema.

## Frozen query controls

On target domain

```text
X2 = {10,20,30,40}
```

freeze queries

```text
q_even(x) = (x mod 2 == 0)             # constant True on X2
q_gt_25(x) = (x > 25)                  # mixed on X2
q_le_40(x) = (x <= 40)                 # constant True on X2
```

Expected on the concrete chain target `S2=X2`:

```text
q_even  -> IDENTIFIED_TRUE
q_gt_25 -> CANNOT_IDENTIFY
q_le_40 -> IDENTIFIED_TRUE
```

The missing-relation control also propagates to `X2` and must produce the same query identifiability outcomes while carrying the distinct `MISSING_RELATION_FULL_DOMAIN` marker.

## Frozen implementation contract

The V1 executor must:

1. represent relations and finite sets canonically without relying on Python object hash iteration order;
2. validate every relation endpoint against its registered source/target domain;
3. reject incompatible relation composition;
4. compute relational images and compositions exactly;
5. use exact `Fraction` arithmetic for `alpha`, `beta_i`, and coverage lower bounds;
6. cap the reported lower coverage at `0` rather than emitting a negative probability;
7. distinguish empty-image inconsistency from query identifiability;
8. fail closed to the full registered target domain when a relation is absent;
9. reject mutation of a frozen campaign after activation;
10. emit deterministic canonical JSON with no product-independence shortcut.

## Frozen falsifiers

This tranche is falsified if any of the following occurs:

- any of the 1024 exhaustive UC-1 cases violates image composition;
- a compatible direct composed image differs from sequential propagation;
- the implementation requires independence for UC-2 or reports a stronger product lower bound without a registered independence proof;
- the disjoint-failure hostile reports joint-good lower bound above `1/2`;
- a missing relation yields a proper subset of the full registered target domain from a nonempty source set;
- a mixed Boolean query is reported as identified;
- an empty image is reported as `IDENTIFIED_TRUE` or `IDENTIFIED_FALSE`;
- normal and `python -O` canonical receipts differ.

## Frozen proof/evidence classes

- UC-1: `P1` formal theorem plus `P2` exhaustive finite certificate.
- UC-2: `P1` formal theorem; arithmetic controls are `P2`.
- UC-3: `P1` finite semantic equivalence plus `P2` controls.
- UC-4: `P1` complete-relation image theorem plus `P2` hostile/control.
- UC-H1: `P2` exact finite probability witness.

No P3/P4 empirical or real-scale claim is introduced by this tranche.

## Required completion evidence

Completion requires, after this freeze commit:

- `FORMALIZATION_V1.md` with explicit quantifiers, domains, proofs, strongest-parent subtraction, nearest counterexamples, and claim ceiling;
- exact executor and hostile/exhaustive tests;
- deterministic `RESULT_V1.json` and a receipt reproducer;
- normal and `python -O` replay with byte-identical receipt;
- dedicated CI including a freeze-custody check that this freeze commit is an ancestor and predates implementation/result artifacts;
- merge before reconciling only #757 and the single #602 row `Propagate uncertainty through composition`.

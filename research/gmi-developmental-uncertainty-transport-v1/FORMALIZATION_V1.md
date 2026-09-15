# Developmental uncertainty transport — formalization V1

Issue #748; parent ledger #602 Section M. Pre-implementation authority: `FREEZE_V1.md`, commit `041bb8950ebeed94b8b258e7ad23258df19eec1c`, committed before this executor, receipt, tests, or scored result existed on the branch.

## Claim boundary and evidence classes

This capsule establishes only

```text
SOUND_DEVELOPMENTAL_UNCERTAINTY_TRANSPORT_AT_REGISTERED_FINITE_SCOPE
```

under preregistered finite state domains and preregistered developmental transition relations. It does not learn a transition relation, establish G7 developmental prediction, authenticate physical sampling, certify a misspecified relation, transport raw observations to a changed developmental version, or show that uncertainty remains small.

Evidence classes:

- **DT-1, DT-3, DT-4, DT-5, DT-6:** P1 deterministic/set-theoretic statements;
- **DT-2:** P3 probability bound obtained from a P1 implication plus Boole's union bound; its statistical premises are stated explicitly;
- exact finite/rational controls and hostile tests: P2 executable evidence;
- no P4 empirical developmental-calibration claim is made.

Strongest parents own nearly all mathematics. The construction is an operational bridge between standard confidence-set logic, set-valued/reachability propagation, and the repository's versioned developmental semantics. Relevant external parents include R. E. Moore's interval/set-mapping treatment, Aubin & Frankowska's set-valued analysis, and Althoff, Frehse & Girard (2021), *Set Propagation Techniques for Reachability Analysis*. In-repository statistical source coverage is owned by ARC-6/#655 and the replay-resistant F1 adapter/#657. The five developmental change labels are owned by #628 `gmi-developmental-taxonomy-v1`.

---

## 1. Registered objects and quantifiers

Let `T` be a finite nonnegative integer. For every `t=0,...,T`, let `X_t` be a nonempty registered state/parameter domain and let the true developmental quantity be a random variable

```text
theta_t : Omega -> X_t.
```

At `t=0`, let `C_0(Omega) subseteq X_0` be a random confidence set determined by source-version evidence. The load-bearing source premise is

```text
P(theta_0 in C_0) >= 1 - alpha,
```

for registered `alpha in [0,1]`.

For each transition `t=1,...,T`, preregister a relation

```text
R_t subseteq X_(t-1) x X_t.
```

Define its image on a set `A subseteq X_(t-1)` by

```text
R_t(A) := { y in X_t : exists x in A such that (x,y) in R_t }.
```

The propagated uncertainty sets are recursively

```text
C_t := R_t(C_(t-1)).
```

The relation is frozen before source activation in the executable protocol. That preregistration rule is a research-governance condition preventing an outcome-selected transition map from being portrayed as prospective transport. The set-theoretic implication below would remain algebraically true for whatever relation was selected, but a post-outcome-selected relation would not inherit the confirmatory interpretation or any preregistered relation-validity budget.

No independence among source evidence, developmental transitions, relation-validity events, or later events is assumed anywhere in this capsule.

---

## 2. DT-1 — exact relational image preserves source coverage [P1]

Assume that, almost surely, every true developmental transition belongs to its registered relation:

```text
(theta_(t-1), theta_t) in R_t    for every t=1,...,T.
```

### Theorem DT-1

On every outcome `omega` for which

```text
theta_0(omega) in C_0(omega),
```

we have

```text
theta_t(omega) in C_t(omega)    for every t=0,...,T.
```

Consequently,

```text
P(theta_t in C_t for every t<=T) >= 1-alpha.
```

### Proof

Fix an outcome `omega` in the source-coverage event. The claim is true at `t=0` by definition. Suppose inductively that `theta_(t-1)(omega) in C_(t-1)(omega)`. By the exact-transition premise,

```text
(theta_(t-1)(omega), theta_t(omega)) in R_t.
```

Because the source endpoint belongs to `C_(t-1)(omega)`, the definition of relational image gives

```text
theta_t(omega) in R_t(C_(t-1)(omega)) = C_t(omega).
```

Finite induction proves simultaneous membership through `T`. Thus the source-coverage event is a subset of the all-times propagated-coverage event, so the latter has probability at least `1-alpha`. QED.

### What DT-1 does not say

It does not say `C_t` is small, minimal, convex, interval-shaped, statistically efficient, or empirically calibrated for a real developmental mechanism. A sound image can expand drastically. Coverage and informativeness are different properties.

---

## 3. DT-2 — uncertain transition relations compose by a global failure budget [P1/P3]

For each `t>=1`, define the relation-validity event

```text
H_t := { (theta_(t-1), theta_t) in R_t }.
```

Assume only the marginal bounds

```text
P(H_t^c) <= beta_t,
```

where `beta_t in [0,1]` is registered before source activation. The events may be arbitrarily dependent on one another and on the source confidence event.

Let

```text
G_0 := { theta_0 in C_0 }.
```

### Theorem DT-2A — finite chain

For every finite `T`,

```text
P(theta_t in C_t for every t<=T)
>= 1 - alpha - sum_(t=1)^T beta_t,
```

with the lower bound clipped at zero when the displayed right-hand side is negative.

### Proof

On the event

```text
G_0 intersect H_1 intersect ... intersect H_T,
```

DT-1's deterministic induction applies verbatim, because every realized transition lies in its registered relation. Hence

```text
G_0 intersect H_1 intersect ... intersect H_T
subseteq
{theta_t in C_t for every t<=T}.
```

Taking complements and applying Boole's inequality,

```text
P((G_0 intersect H_1 intersect ... intersect H_T)^c)
= P(G_0^c union H_1^c union ... union H_T^c)
<= P(G_0^c) + sum_t P(H_t^c)
<= alpha + sum_t beta_t.
```

Rearranging proves the stated lower bound. No product probability, conditional independence, pairwise independence, or iid assumption appears. QED.

### Theorem DT-2B — countably many registered developmental steps, all finite attained times

Let a total transition-failure budget `beta in [0,1]` be allocated as

```text
beta_t = beta / [t(t+1)],  t=1,2,... .
```

Then

```text
sum_(t=1)^N beta_t
= beta * N/(N+1)
< beta,
```

and

```text
sum_(t=1)^infinity beta_t = beta.
```

Therefore

```text
P(G_0 intersect (intersection over all t>=1 H_t)) >= 1-alpha-beta,
```

and on that event every finite attained propagated set covers its true developmental quantity.

### Proof

Use the telescoping identity

```text
1/[t(t+1)] = 1/t - 1/(t+1).
```

For every finite `N`, DT-2A gives failure probability at most

```text
alpha + beta*N/(N+1).
```

Equivalently, directly apply countable subadditivity to

```text
G_0^c union (union over t>=1 H_t^c)
```

and the convergent series. The complement therefore has probability at least `1-alpha-beta`. DT-1's induction applies to every finite prefix on that one event. QED.

### Frozen arithmetic witness

With `alpha=1/20`, `beta_1=1/100`, and `beta_2=1/200`, the registered failure budget is exactly

```text
1/20 + 1/100 + 1/200 = 13/200,
```

so the coverage lower bound is `187/200`.

With the countable allocation `beta=1/20`, the all-finite-times lower bound is

```text
1 - 1/20 - 1/20 = 9/10.
```

The executable receipt verifies exact partial sums at `N=1,2,5,1000`.

### Nearest false generalization

Marginal transition guarantees do not combine by multiplying their success probabilities unless additional independence structure has actually been proved. This capsule deliberately uses only the union bound. Any implementation reporting a smaller failure budget than the registered source budget plus relation budgets would require a separately registered shared-event theorem.

---

## 4. DT-3 — complete ignorance maps to the full target domain [P1]

Suppose no relation constraining source to target is registered. The maximally permissive relation consistent with only the domains is

```text
R_unknown = X_(t-1) x X_t.
```

### Theorem DT-3A

For every nonempty `A subseteq X_(t-1)`,

```text
R_unknown(A) = X_t.
```

### Proof

Take any `y in X_t`. Since `A` is nonempty, choose any `x in A`. Then `(x,y)` lies in the Cartesian product, so `y in R_unknown(A)`. Thus `X_t subseteq R_unknown(A)`. The reverse inclusion holds by the codomain of the relation. QED.

Therefore the fail-closed implementation for a missing developmental relation returns the entire registered target domain and terminal

```text
CANNOT_IDENTIFY_NO_RELATION.
```

It must not silently copy the source set into the target version.

### Theorem DT-3B — source-set copying has no general coverage guarantee

There exists a developmental update with source coverage one for which copying the source set to the target has target coverage zero.

### Exact counterexample

Let

```text
X_0 = {0},
C_0 = {0},
theta_0 = 0 surely,
X_1 = {0,1},
theta_1 = 1 surely.
```

The source set covers with probability one. If one copies `C_1 := C_0 = {0}`, then `theta_1 notin C_1` surely, so target coverage is zero. The full target domain `{0,1}` covers surely. QED.

This is the sharp reason #657's “new developmental version starts with zero evidence” rule cannot be replaced by silent interval/visit inheritance.

---

## 5. DT-4 — transported claims are not transported observations [P1]

A source empirical object can contain raw observation counts or other evidence metadata. A developmental relation licenses only the logical implication

```text
source true value in C_(t-1)
and true transition in R_t
=> target true value in R_t(C_(t-1)).
```

It does not imply that a source-version sample was drawn from the target-version data-generating process.

### Theorem DT-4

Under the executable state machine, every target `ConfidenceObject` created by a developmental transport has `raw_evidence_count = 0`, regardless of the source object's raw evidence count.

### Proof

`TransportCampaign._apply` constructs each target object with a new target version/domain, the relational image, and the accumulated failure budget, while setting the raw evidence field literally to zero. `propagate_unknown` does the same. There is no API operation that copies source evidence counters, sums, tokens, or origins into a target object. Induction along any registered chain preserves zero target inherited evidence. QED.

The frozen control starts with source raw evidence count 2048 and checks zero on all five target versions.

This theorem is intentionally stronger as governance than the mathematics strictly requires: it prevents a semantic set transform from being confused with a statistical sample transform.

---

## 6. DT-5 — exact finite relational images and nonlinear maps [P1/P2]

For finite domains, the implementation computes

```text
R(A) = {y : (x,y) in R for some x in A}
```

by direct comprehension. Hence it is exact relative to the enumerated relation: there is no numerical approximation error.

The hostile suite compares the implementation against an independently written comprehension on a rational relation family.

### Frozen nonlinear control

For

```text
A = {-1,0,1},
y in {x^2-1, x^2, x^2+1},
```

the exact image is

```text
{-1,0,1,2}.
```

Indeed:

- `x=-1` contributes `{0,1,2}`;
- `x=0` contributes `{-1,0,1}`;
- `x=1` contributes `{0,1,2}`;

and their union is exactly the frozen set. This control prevents the claimed mechanism from collapsing to affine-only propagation.

---

## 7. DT-6 — exact affine interval hull with bounded set error [P1/P2]

Let

```text
x in [l,u],
y = a*x + b + e,
e in [-eps,+eps], eps>=0.
```

### Theorem DT-6

The smallest closed interval containing all admissible `y` values is

```text
[
  min(a*l+b-eps, a*l+b+eps, a*u+b-eps, a*u+b+eps),
  max(a*l+b-eps, a*l+b+eps, a*u+b-eps, a*u+b+eps)
].
```

### Proof

The map `(x,e) -> a*x+b+e` is affine on the rectangle `[l,u] x [-eps,eps]`. A linear/affine functional attains its extrema on a compact rectangle at corners. Equivalently, for fixed `e` the function is monotone in `x` according to the sign of `a`, and for fixed `x` it is monotone in `e`; therefore the extrema occur at endpoint/error-corner pairs. Every intermediate value lies between those extrema, so the interval hull is exact. QED.

For the frozen control

```text
l=1/4, u=3/4, a=-2, b=3, eps=1/10,
```

the four corner values have minimum `7/5` and maximum `13/5`; the implementation and independent exhaustive corner enumeration agree exactly.

The bounded error interval here is a **set-valued admissibility statement**. It is not itself a probability distribution and should not be called aleatoric probability without an additional registered stochastic model.

---

## 8. The five registered A3 change kinds

The exact executable chain uses the developmental vocabulary already registered by #628 rather than inventing a competing taxonomy:

| change kind | registered relation | source set image |
|---|---|---|
| `INFO` | `y=x+1` | `{-1,0,1} -> {0,1,2}` |
| `RECODE` | `y=x` | `{0,1,2} -> {0,1,2}` |
| `SKILL` | `y in {x,x+1}` | `{0,1,2} -> {0,1,2,3}` |
| `LAW` | `y in {x-1,x,x+1}` | `{0,1,2,3} -> {-1,0,1,2,3,4}` |
| `MORPH` | `y=x^2` | `{-1,0,1,2,3,4} -> {0,1,4,9,16}` |

All five relations have registered `beta_t=0`, so the source failure budget remains exactly `1/20` throughout. The names do not contribute mathematical force: the force comes from each preregistered relation. The five controls show that the same transport semantics covers identity/recode, deterministic affine, one-to-many set-valued, and nonlinear mappings.

These are exact microscope controls, not empirical claims that real INFO/SKILL/LAW/MORPH changes obey these toy relations.

---

## 9. Query identifiability under propagated uncertainty

Let `q : X_t -> {False,True}` be a registered deterministic Boolean query and let `C_t` be the current uncertainty set.

### Proposition

The answer to `q(theta_t)` is logically identifiable from set membership alone exactly when `q` is constant on `C_t`.

### Proof

If `q` is constant on `C_t`, every admissible value has the same answer, so the answer is identified. Conversely, if `q` is nonconstant on `C_t`, there are `x,y in C_t` with opposite answers, and membership information alone cannot distinguish which is true. QED.

Thus a full-domain uncertainty set can still identify an invariant query. The frozen no-relation control on target `{0,1,2}` gives:

- `q(x)=(x>0)`: nonconstant, hence `CANNOT_IDENTIFY`;
- `q(x)=True`: constant, hence `IDENTIFIED_TRUE`.

This is more precise than declaring every no-relation target unknowable, while remaining fail-closed for non-invariant claims.

---

## 10. Epistemic versus aleatoric uncertainty at this scope

This capsule keeps three concepts separate:

1. **Epistemic source uncertainty:** uncertainty about the current fixed true quantity after finite evidence, represented by a confidence/set object `C_0` and source failure budget `alpha`.
2. **Model/transition-set uncertainty:** a relation `R_t` may admit multiple successors. This is set-valued uncertainty about what transitions are licensed by the registered model. Without a probability measure over successors, it is not a probabilistic aleatoric distribution.
3. **Relation misspecification uncertainty:** `beta_t` bounds the event that the true transition falls outside the registered relation. It is a probability-of-model-failure budget, not a distribution over points inside the relation.

If future work registers a stochastic transition kernel, process noise law, or conditional outcome distribution, that can support an explicit aleatoric component. This capsule does not infer such a distribution from set width.

Accordingly, #748 closes a developmental **transport** obligation only. It does not by itself justify checking the broader #602 row “Distinguish epistemic uncertainty from aleatoric uncertainty” across all morphology/capability/developmental claims.

---

## 11. Why post-outcome maps and misspecified relations are outside the guarantee

DT-1/DT-2 are conditional theorems. They do not make an arbitrary relation valid.

- If a registered relation excludes the realized true transition, that step lies in `H_t^c` and is charged to its registered `beta_t` premise.
- If an analyst chooses a relation after seeing protected target outcomes, the mathematical image statement may still hold for that relation, but the preregistered probabilistic interpretation and confirmatory evidence class are lost.
- If `beta_t` was asserted without an independent theorem/experiment establishing it, DT-2 only says what would follow **if** that bound is true; it does not prove the bound itself.

The executable layer therefore locks all transition contracts after source activation and rejects post-activation registration.

---

## 12. Verification matrix and falsifiers

The exact/adversarial suite covers 35 controls, including:

- frozen contract immutability and exact-Fraction budgets;
- rejected version skips/back-edges and unknown change kinds;
- total-relation requirement and endpoint domain checks;
- post-source-activation relation registration rejection;
- exact relational-image comparison against an independent comprehension;
- exact and uncertain budget accumulation;
- telescoping countable allocation at `N=1,2,5,1000`;
- all five A3 change kinds and frozen images;
- raw-evidence noninheritance;
- no-relation full-domain propagation;
- the zero-target-coverage source-copy counterexample;
- query abstention and invariant-query identification;
- affine interval/corner equality;
- nonlinear finite relation image;
- deterministic receipt reproduction.

The dedicated workflow runs the suite under normal Python and `python -O`, verifies freeze custody, and requires byte-identical reproduction of `RESULT_V1.json`.

The registered claim is falsified at its scope by any of the following:

- an admissible registered successor omitted from an exact relational image;
- a reported failure budget below the source-plus-registered-transition union budget without a stronger separately proved shared-event argument;
- any use of an independence assumption not stated in the theorem;
- a no-relation step returning copied source uncertainty instead of the full target domain;
- inherited raw evidence on a target developmental version;
- accepted post-activation transport registration;
- disagreement with any frozen five-kind exact image;
- an affine corner outside the reported interval hull;
- optimized-mode receipt drift;
- wording that upgrades this bridge to G7, empirical developmental calibration, or complete-GMI closure.

---

## 13. Parent subtraction and residual contribution

The mathematical theorem is deliberately parent-owned:

- standard set-valued analysis owns relational images and set propagation;
- interval analysis owns rigorous enclosures for interval/set mappings;
- reachability analysis owns propagation of sets under uncertain dynamics;
- elementary probability owns the union bound;
- ARC-6/#655 and #657 own the source simultaneous confidence machinery;
- #628 owns the developmental change taxonomy.

The residual contribution of this capsule is narrower: it binds those parents into the repository's versioned developmental evidence discipline, provides an exact executable fail-closed transport contract, proves that raw evidence and semantic confidence-set transport are distinct operations, and supplies hostile controls that make the nearest unsafe shortcut—silent source-set/evidence inheritance—fail visibly.

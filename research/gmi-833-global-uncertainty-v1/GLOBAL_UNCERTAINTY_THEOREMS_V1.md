# Global uncertainty, confidence composition and abstention — v1

**Issue:** #851, child of #833 Section C  
**Freeze:** `research/gmi-833-global-uncertainty-v1/FREEZE_V1.md` at `b62fd81b5e3b37a4f94f70aaaa54d4b76e36008a`  
**Source main:** `5db372ef7003253d5846b324ed80a2454613983c`  
**Claim ceiling:** `GMI_GLOBAL_UNCERTAINTY_AND_ABSTENTION_CONTRACT_AT_REGISTERED_FINITE_SCOPE`

This tranche does not invent new confidence-set, relational-composition, partial-identification, selective-prediction, or law-of-total-variance mathematics. It supplies one architecture-independent typed contract that composes the strongest already-merged repository parents without silently changing their semantics.

## 1. Registered scope and review lenses

Fix finite nonempty registered domains, explicit integer versions, exact rational failure budgets, and provenance identifiers. Domain elements are opaque finite values. Architecture names do not enter any definition.

Three independent lenses govern this capsule.

1. **Set/constraint lens.** Feasibility and relational propagation are ordinary set images, joins and projections. Empty feasible sets and missing relations have different meanings.
2. **Probability/confidence lens.** A probability guarantee exists only on a `ConfidenceSet` or a separately registered calibration object. Dependence-free composition uses only valid arbitrary-dependence bounds.
3. **Identification/decision lens.** A unique factual answer is licensed only when the registered query is constant on the surviving set. Failure to identify is not failure to execute a check.

A fourth hostile lens checks latent-model uncertainty: predictive marginals do not determine a unique epistemic/aleatoric allocation.

## 2. U-1 — typed uncertainty objects [contract + P1 disjointness]

The global object is a tagged sum with five constructors.

### U-1a `FeasibleSet(X,C,v,p)`

`X` is a finite nonempty domain and `C subseteq X`. No probability premise is attached.

State-level knowledge is:

- `C=emptyset` -> `INCONSISTENT_REGISTERED_ASSUMPTIONS`;
- `C=X` -> `UNKNOWN` (maximal registered possibility);
- otherwise -> `FEASIBLE`.

`UNKNOWN` therefore means “all registered states remain possible,” not “the checker failed.”

### U-1b `ConfidenceSet(X,C,alpha,target,v,p)`

This is a feasible set plus the explicit premise

`P(theta in C) >= 1-alpha`, with `alpha in [0,1]`.

The set can still equal the whole domain and be non-informative. A coverage statement and identifying information are different coordinates.

### U-1c `PredictiveLaw(Y,P,v,p)`

`P` is an exact probability law on the outcome domain `Y`. It is not a confidence set over a latent/model parameter and does not expose a latent decomposition.

### U-1d `LatentPredictiveModel(Theta,pi,Y,K,v,p)`

`pi` is a probability law on registered latent states and `K(y|theta)` is a registered conditional outcome kernel. Only this constructor has enough semantics for the finite conditional-variance decomposition used below.

### U-1e `SelectivePrediction(S,e,c,v,p)`

`S` is a set of emitted values, `e` is a registered risk/error certificate and `c` a registered coverage quantity. These fields are not inferred from a bare feasible set.

### Theorem U-1 — constructor disjointness

The five uncertainty kinds are semantically disjoint constructors. Any conversion between constructors is a separate checked operation with its own premises; there is no implicit coercion that can manufacture a probability level, latent decomposition, or calibration certificate.

**Proof.** This is a definitional property of the tagged sum. Each constructor has a distinct tag and constructor-specific required fields. Equality/coercion across tags is not defined. The executable model represents the tags by a five-valued enum and constructor-specific dataclasses; illegal fields/normalizations fail closed. `□`

This is type safety, not an ontological claim that all real uncertainty falls into exactly five philosophical kinds.

## 3. U-2A — exact relational image composition [P1 + P2]

For finite spaces `X,Y,Z`, set `S subseteq X`, and relations

`R subseteq X x Y`, `Q subseteq Y x Z`,

define

`R[S] = {y in Y : exists x in S, (x,y) in R}`

and relational composition

`Q o R = {(x,z) : exists y, (x,y) in R and (y,z) in Q}`.

### Theorem U-2A

`Q[R[S]] = (Q o R)[S]`.

**Proof.** For arbitrary `z`,

`z in Q[R[S]]`

iff there exists `y in R[S]` with `(y,z) in Q`; this is equivalent to existence of `x in S` and `y` with `(x,y) in R` and `(y,z) in Q`; by definition this is equivalent to `z in (Q o R)[S]`. Extensionality gives equality. `□`

**Machine certificate.** The executor checks every `4 x 16 x 16 = 1,024` choice of source subset and two binary relations on `{0,1}`. Failures: `0`.

Parent ownership: #757/#761.

## 4. U-2B — dependence-safe confidence composition [P1 + P2]

Let finite spaces `X_0,...,X_k`, source set `C_0 subseteq X_0`, and registered relations

`R_i subseteq X_i x X_(i+1)`

be fixed. Define `C_(i+1)=R_i[C_i]`.

Let

`G_0 = {theta_0 in C_0}`

and

`G_i = {(theta_i,theta_(i+1)) in R_i}`.

Assume only

`P(G_0^c) <= alpha`,

`P(G_i^c) <= beta_i`.

No independence premise is made.

### Theorem U-2B

`P(theta_k in C_k) >= max(0,1-alpha-sum_i beta_i)`.

**Proof.** On `G_0`, `theta_0 in C_0`. If `theta_i in C_i` and `G_i` holds, then `(theta_i,theta_(i+1)) in R_i`; hence by the definition of relational image `theta_(i+1) in C_(i+1)`. Induction therefore gives

`intersection_(i=0..k-1) G_i subseteq {theta_k in C_k}`

where the first term denotes the source-good event and the remaining terms the relation-good events. By Boole's inequality,

`P(any good event fails) <= alpha + sum_i beta_i`.

Taking complements and clipping the lower bound at zero proves the claim. `□`

The exact receipt includes the control

`alpha=1/20`, `beta_1=1/100`, `beta_2=1/200`

so the lower bound is

`1 - 1/20 - 1/100 - 1/200 = 187/200`.

### No product shortcut

On four equiprobable atoms let failure event `A` occur only on atom 0 and failure event `B` only on atom 1. Each good marginal has probability `3/4`, but simultaneous goodness is `1/2`. The independence product `9/16` is strictly too high to be a valid arbitrary-dependence lower bound, while the union-bound lower bound `1/2` is exact.

The implementation refuses a product of good-event probabilities unless an independence model is explicitly registered. It also exhaustively checks Boole's lower bound over every ordered triple of subsets of a four-atom probability space: `16^3 = 4,096` cases, zero violations.

Parent ownership: #757/#761 and classical Boole/Fréchet arbitrary-dependence probability bounds.

## 5. U-2C — exact finite-DAG object and local-over-global boundary [P1 + P2]

Let `G=(V,E)` be a finite DAG. Every node `v` has finite domain `X_v`. Let the roots have a registered joint feasible/confidence relation `C_R`, and every non-root `v` have a registered local relation

`Q_v subseteq (product_(p in Pa(v)) X_p) x X_v`.

Define the global feasible-assignment relation

`A = {x_V : x_R in C_R and ((x_p)_(p in Pa(v)),x_v) in Q_v for every non-root v}`.

For output tuple `O`, the exact propagated set is `pi_O(A)`.

### Theorem U-2C.1 — global pathwise soundness

On the event that the true root tuple is in `C_R` and every true local tuple is in its registered relation, the complete true assignment belongs to `A`; therefore its output tuple belongs to `pi_O(A)`.

**Proof.** Each defining conjunct of `A` is exactly one of the assumed good-event statements. Therefore the true assignment satisfies all conjuncts. Projection preserves membership of its requested coordinates. `□`

Combining this pathwise statement with Boole's inequality gives the inherited #759/#765 joint-output coverage theorem without an independence premise.

### Theorem U-2C.2 — local Cartesian propagation is sound but may be loose

Let root marginal sets contain the projections of every global feasible root assignment. Propagate node-local sets in topological order via

`S_v = Q_v[product_(p in Pa(v)) S_p]`.

Then for every node `v`,

`pi_v(A) subseteq S_v`.

**Proof.** By topological induction. The root case is the premise. For a non-root node, take any value `x_v` appearing in a global feasible assignment. Every parent value in that same assignment lies in its local set by induction. The parent tuple therefore belongs to the Cartesian product of parent local sets; because the global assignment also satisfies `Q_v`, `x_v` is included in the local relational image. `□`

The inclusion can be strict because Cartesian products forget dependence.

### Shared-ancestor hostile

`x in {-1,+1}`, `a=x`, `b=x`, `y=a-b`.

Global feasibility preserves `a=b` and gives `y={0}`. Local marginals give `a=b={-1,+1}`; their Cartesian product additionally permits unequal pairs and yields `y={-2,0,2}`.

### Dependent-root hostile

Root joint set `{(0,0),(1,1)}` and `y=r1 XOR r2` gives exact `y={0}`. Replacing the root joint set by the product of its marginals gives all four bit pairs and `y={0,1}`.

Parent ownership: #759/#765. This child revalidates the boundary; it does not reclaim the theorem.

## 6. U-3 — missing relation, empty relation, and developmental transport [P1 + P2]

### Theorem U-3A — missing relation semantics

For nonempty source set `C subseteq X`, if the relation from `X` to a registered target domain `Y` is missing, the fail-closed relation is the complete relation `X x Y`. Its image is exactly `Y`.

**Proof.** Every `y in Y` pairs with every `x in C`, and `C` is nonempty, so every `y` is in the image. No value outside `Y` can be in the image. `□`

Thus missing relation means maximal registered target possibility, `UNKNOWN`; it is not a license to copy a source value or choose a nominal transform.

### Theorem U-3B — upstream inconsistency is not laundered

If `C=emptyset`, then for every relation `R`, including the complete relation,

`R[C]=emptyset`.

**Proof.** Membership in a relational image requires existence of `x in C`; there is no such `x`. `□`

Therefore a missing relation does not convert a known upstream inconsistency into `UNKNOWN`. This hostile was added after independent review of the first implementation draft.

### Registered empty relation

If `R=emptyset`, then `R[C]=emptyset` for every `C`; this is infeasibility/inconsistency under the registered relation, not ignorance.

### Missing target domain

If the target domain itself is not registered, the system cannot even construct the complete fail-closed relation. The only licensed terminal is `CANNOT_CHECK(TARGET_DOMAIN_NOT_REGISTERED)`.

### Developmental/version rule

For a developmental transport from version `v` to version `v+1`, a registered relation and explicit failure budget may transport the set/confidence object, but the target object's `raw_evidence_count` is reset to zero. Source observations remain evidence about the source version; they do not become raw target-version observations by transport.

The executable wrapper rejects non-adjacent developmental versions and resets the evidence count on registered transport.

Parent ownership: #748/#749.

## 7. U-4 — query-relative identification and abstention [P1 + P2]

Let `q:X->Y` be a registered finite query and `C subseteq X`. Define the identified set

`I_q(C)=q[C]={q(x):x in C}`.

### Theorem U-4A — exact query identification

For nonempty `C`, `I_q(C)` is a singleton `{y}` iff `q(x)=y` for every `x in C`.

**Proof.** If the image is `{y}`, every image value of every `x in C` equals `y`. Conversely, if every `x in C` maps to `y` and `C` is nonempty, the image contains `y` and contains no other value. `□`

Therefore:

- singleton image -> `IDENTIFIED(y)`;
- image with more than one value -> `CANNOT_IDENTIFY(candidate_set)` and a unique factual answer must abstain;
- `C=emptyset` -> `INCONSISTENT_REGISTERED_ASSUMPTIONS`;
- missing/mismatched query semantics -> `CANNOT_CHECK(reason)`.

### Theorem U-4B — confidence image preservation

If `C` is a confidence set with

`P(theta in C) >= 1-alpha`,

then

`P(q(theta) in q[C]) >= 1-alpha`.

If additionally `q[C]={y}`, then

`P(q(theta)=y) >= 1-alpha`.

**Proof.** The event `{theta in C}` is a subset of `{q(theta) in q[C]}` by the definition of image. Event monotonicity gives the first inequality. A singleton image turns the latter event into `{q(theta)=y}`. `□`

The implementation therefore carries the confidence failure budget into both identified and set-valued query results rather than silently converting confidence to certainty.

### `UNKNOWN` is query-relative

Take `X={0,1}` and `C=X`; state knowledge is `UNKNOWN`.

- Identity query `q(x)=x` gives `{0,1}` -> `CANNOT_IDENTIFY`.
- Constant query `q(x)=7` gives `{7}` -> `IDENTIFIED(7)`.

Hence maximal state uncertainty can coexist with exact identification of a coarser query. This is the ordinary identified-set idea: non-point-identification of state does not imply non-identification of every functional.

**Machine certificate.** On domain `{0,1,2}`, every one of the 8 state subsets is combined with every one of the 8 binary-valued queries: 64 cases. The executor independently classifies each by the cardinality of the exact image. Failures: 0.

External parent anchors: partial-identification/identified-set theory (Manski and related literature) and selective classification/reject-option theory (Chow; El-Yaniv & Wiener). This tranche does not equate statistical reject risk with set-theoretic non-identification; it only uses abstention as the decision terminal when a unique registered query value is not identified.

## 8. U-5 — predictive marginal cannot identify a unique latent variance split [P1 + P2]

Let the outcome be `Y in {0,1}` and latent state `Theta in {a,b}` with prior `(1/2,1/2)`.

### Model E — pure conditional-mean epistemic component

`P(Y=0|a)=1`, `P(Y=1|b)=1`.

Conditional means are `0` and `1`; conditional variances are both `0`. Therefore

`A = E[Var(Y|Theta)] = 0`,

`E_mean = Var(E[Y|Theta]) = 1/4`,

`T = Var(Y) = 1/4`.

### Model A — pure aleatoric component

Both latent states use `Bernoulli(1/2)`.

Conditional means are both `1/2`; conditional variances are both `1/4`. Therefore

`A=1/4`, `E_mean=0`, `T=1/4`.

Both models have exactly the same predictive marginal

`P(Y=0)=P(Y=1)=1/2`.

### Theorem U-5A — finite law of total variance

For any registered finite latent model with numeric finite outcome domain,

`Var(Y) = E[Var(Y|Theta)] + Var(E[Y|Theta])`.

**Proof.** Write `m(Theta)=E[Y|Theta]`. Expanding squares,

`E[(Y-EY)^2] = E[(Y-m+m-EY)^2]`.

The cross term has conditional expectation zero because `E[Y-m|Theta]=0`. The remaining terms are `E[Var(Y|Theta)]` and `Var(m)`. Finite sums make every expectation exact. `□`

### Theorem U-5B — marginal-only non-identifiability

No function of the predictive marginal alone can return the unique pair `(A,E_mean)` correctly for every registered model in a class containing Models E and A.

**Proof by collision.** The input marginal to such a function is identical for the two models, so the function must return the same value on both. But the registered decompositions are `(0,1/4)` and `(1/4,0)`. It cannot be correct for both. `□`

Thus `PredictiveLaw.epistemic_aleatoric_decomposition()` fails closed with `CANNOT_DECOMPOSE_WITHOUT_LATENT_SEMANTICS`; the decomposition method exists only on `LatentPredictiveModel`.

Parent ownership: #750/#751 and the ordinary law of total variance. Hüllermeier & Waegeman (2021) and Kendall & Gal (2017) are taxonomy/application anchors, not novelty claims.

## 9. Strongest-parent subtraction

| Residual in #851 | Strongest owner | What this tranche may claim | What it may not reclaim |
|---|---|---|---|
| chain relational images + arbitrary-dependence confidence budget | #757/#761 | typed integration + revalidation | new union-bound/composition theorem |
| joint finite-DAG projection + local Cartesian over-approximation | #759/#765 | common interface + inherited hostile replay | new dependency-analysis theorem |
| developmental uncertainty transport | #748/#749 | adjacent-version guard + typed boundary | new developmental transport mathematics |
| epistemic/aleatoric split | #750/#751 | marginal-vs-latent type boundary | universal uncertainty decomposition |
| selective capability calibration | #766/#767 | separate selective-prediction constructor | transfer of calibration outside its registered frame |
| identified sets / partial identification | external parent literature | query-relative abstention semantics | novelty in identification theory |
| reject option / selective prediction | Chow; El-Yaniv & Wiener | distinguish abstention terminal from state uncertainty | universal risk/coverage optimality |

The repository residual is therefore a **global typed composition discipline**, not a new probability theory.

## 10. Theorem / assumption / falsifier ledger

| ID | Class | Load-bearing assumptions | Nearest falsifier / hostile | Machine evidence |
|---|---|---|---|---|
| U-1 | contract/P1 | constructor tags; registered fields | implicit coercion across kinds | constructor validation tests |
| U-2A | P1/P2 | finite typed relations | domain mismatch / composition bug | 1,024-case exhaustive census |
| U-2B | P1/P2 | registered failure budgets; no hidden extra failures | disjoint `1/4` failures refute product shortcut | 4,096-case Boole census + exact hostile |
| U-2C | P1/P2 | finite DAG; joint relation retained for exact result | shared ancestor; dependent roots | exact global vs local hostiles |
| U-3 | P1/P2 | registered target domain; explicit version semantics | missing vs empty; upstream empty laundering; non-adjacent version | exact terminal/version tests |
| U-4 | P1/P2 | registered finite query; set semantics | full-domain identity query; full-domain constant query; empty set; missing query | 64-case exhaustive census |
| U-5 | P1/P2 | registered latent semantics for decomposition | same marginal/opposite decompositions | exact rational collision |

No P3 asymptotic or P4 empirical claim is introduced by this capsule.

## 11. Exact receipt summary

The canonical executor/test suite verifies:

- five machine-distinct uncertainty constructors;
- four machine-distinct state/query failure terminals where applicable;
- 1,024 exhaustive two-relation composition cases, zero failures;
- 4,096 exhaustive three-failure-event Boole cases, zero failures;
- 64 exhaustive query-identification cases, zero failures;
- shared-ancestor exact `{0}` versus local `{-2,0,2}`;
- dependent-root exact `{0}` versus local `{0,1}`;
- anti-product hostile: true joint good `1/2`, product `9/16`, dependence-safe lower bound `1/2`;
- exact composed coverage lower bound `187/200`;
- missing relation -> full-domain `UNKNOWN` only when the upstream set is nonempty;
- empty relation and upstream-empty cases -> inconsistency;
- missing target domain -> `CANNOT_CHECK`;
- developmental target raw-evidence count reset to `0` and non-adjacent version rejected;
- equal Bernoulli(`1/2`) predictive marginals with opposite `0`/`1/4` variance components;
- marginal-only decomposition rejected;
- deterministic result bytes under normal Python and `python -O`.

Local suite: 44 exact/adversarial tests in each mode. Canonical `RESULT_V1.json` SHA-256 is recorded in the pull request after the final receipt is generated.

## 12. Claim boundary

Allowed after dedicated CI verifies the frozen capsule:

`GMI_GLOBAL_UNCERTAINTY_AND_ABSTENTION_CONTRACT_AT_REGISTERED_FINITE_SCOPE`

Forbidden from this tranche alone:

- `UNIVERSAL_UNCERTAINTY_CALIBRATION`
- `INDEPENDENCE_PROVED`
- `ALL_REAL_WORLD_CONFIDENCE_VALID`
- `UNIVERSAL_POSTERIOR_CORRECTNESS`
- `REAL_SCALE_UNCERTAINTY_VALIDATION`
- `COMPLETE_GMI`

This capsule does not close the #833 corpus audit, terminology migration, leakage detector, universal neutral grammar, family re-derivation, real-scale replication, or complete-theory gate.

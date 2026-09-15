# GMI #833 global uncertainty / abstention freeze v1

**Parent:** #833 Section C  
**Child:** #851  
**Source main:** `5db372ef7003253d5846b324ed80a2454613983c`  
**Status:** pre-implementation theorem/evidence freeze

This file freezes the typed objects, theorem statements, finite witnesses, hostile counterexamples, parent ownership and claim ceiling before implementation, tests, results, reconciliation, or pull-request outcome exist on this branch.

## 1. Registered finite scope

Fix finite registered domains and version/provenance identifiers. Domain elements are opaque finite values; probability/failure budgets are exact rationals. No architecture-family name is part of the uncertainty semantics.

The contract must keep five object kinds machine-distinct:

1. `FeasibleSet(X,C,version,provenance)` with `C subseteq X`; this carries no probability guarantee.
2. `ConfidenceSet(X,C,alpha,target,version,provenance)` with an explicit registered premise `P(theta in C) >= 1-alpha`.
3. `PredictiveLaw(Y,P,version,provenance)` for predictive/aleatoric randomness over outcomes.
4. `LatentPredictiveModel(Theta,pi,K,version,provenance)` only when latent-state semantics, prior and conditional kernel are registered.
5. `SelectivePrediction(value_set,error_or_risk_certificate,coverage,version,provenance)` only when the corresponding selection/calibration semantics are actually registered.

A full set `C=X` means maximal registered possibility / `UNKNOWN` at state level. It has complete structural coverage of the registered domain but can contain no identifying information. Structural coverage and informativeness are separate.

An empty registered feasible set `C=emptyset` means inconsistency/infeasibility under the registered assumptions. It is not `UNKNOWN`.

## 2. U-1 — type-safety and non-coercion

Target theorem/contract: uncertainty kinds are tagged and non-interchangeable. In particular:

- a feasible set cannot silently acquire a confidence level;
- a predictive marginal cannot silently become a confidence set over latent models;
- a marginal-only predictive law cannot expose an epistemic/aleatoric decomposition;
- selective-prediction coverage/error fields cannot be inferred from a bare feasible set;
- `UNKNOWN`, `CANNOT_IDENTIFY`, `CANNOT_CHECK`, and `INCONSISTENT_REGISTERED_ASSUMPTIONS` are distinct machine states.

Frozen falsifier: any generic helper that accepts one uncertainty kind where another is required without an explicit, checked conversion invalidates U-1.

## 3. U-2 — registered relational propagation

For finite domains `X_0,...,X_k`, source confidence set `C_0 subseteq X_0`, and registered relations

`R_i subseteq X_i x X_(i+1)`,

define exact relational images

`C_(i+1) = R_i[C_i] = { y : exists x in C_i, (x,y) in R_i }`.

Let the source-good event satisfy `P(theta_0 in C_0) >= 1-alpha`. Let the registered relation-good event at stage `i` satisfy

`P((theta_i,theta_(i+1)) notin R_i) <= beta_i`.

Target coverage theorem:

`P(theta_k in C_k) >= max(0, 1-alpha-sum_i beta_i)`.

No independence premise is allowed. Exact relations are the `beta_i=0` specialization.

The analytic proof target is pathwise inclusion on the intersection of all good events followed by Boole's inequality. This mathematics is parent-owned by #757/#761; this child integrates it into one global typed contract rather than claiming a new union-bound theorem.

### Frozen dependence hostile

Take two failure events of probability `1/4` that are disjoint. Then simultaneous success is exactly `1/2`; multiplying marginal success probabilities would produce `9/16` and is therefore not a valid dependence-free lower bound. The implementation must refuse an independence-product shortcut unless an independence model is explicitly registered.

## 4. U-2DAG — dependency-preserving composition boundary

For a finite registered DAG with root confidence relation/set and local node relations, the exact object is the global feasible-assignment relation satisfying every root/local constraint, followed by projection to the requested output nodes.

Target inherited theorem: on the root-good and all relation-good events, the true assignment belongs to the global feasible-assignment relation; therefore output coverage obeys the same union-bound budget with no independence premise.

Node-local Cartesian propagation is a sound over-approximation of global projection but may lose shared dependence.

### Frozen shared-ancestor hostile

`x in {-1,+1}`, `a=x`, `b=x`, `y=a-b`.

Exact global propagation gives `y={0}`. Local propagation that keeps only marginal parent sets gives `a=b={-1,+1}` and hence `y={-2,0,2}`. Reporting the local superset as exact is forbidden.

### Frozen dependent-root hostile

Use roots `(r1,r2)` constrained to equal bits `{(0,0),(1,1)}` and output `y=r1 XOR r2`. Exact joint propagation gives `{0}`; replacing the joint root relation by the Cartesian product of marginals gives `{0,1}`. A joint confidence object may not be factorized without a registered dependence premise.

This mathematics is parent-owned by #759/#765; this child revalidates the boundary and exposes it through the common contract.

## 5. U-3 — missing relation, empty relation and developmental/version rule

A missing relation and a registered empty relation are semantically different:

- **missing relation + registered target domain:** return maximal local ignorance over the full target domain; no narrower inherited information is permitted;
- **registered empty relation:** return an empty feasible set / `INCONSISTENT_REGISTERED_ASSUMPTIONS`;
- **missing target domain/required semantics:** return `CANNOT_CHECK`, not a fabricated domain or confidence object.

Across a registered developmental update, a set/confidence claim may be transported only through an explicitly registered relation and failure budget. The target object receives zero migrated raw-observation/sample count; old evidence does not become target-version raw evidence merely because an uncertainty set was transported.

This rule absorbs the developmental transport mathematics owned by #748/#749 rather than rewriting its receipt.

## 6. U-4 — query-relative identification and abstention

For a registered finite query `q : X -> Y` and set `C subseteq X`, define the identified set

`I_q(C) = q[C] = {q(x) : x in C}`.

Target theorem for registered nonempty `C`:

- `|I_q(C)|=1` iff every state in `C` agrees on the query value; emit `IDENTIFIED(value)`;
- `|I_q(C)|>1` iff the unique factual answer is not identified; emit `CANNOT_IDENTIFY(candidate_set)` and abstain from a unique claim.

Boundary terminals:

- `C=emptyset` -> `INCONSISTENT_REGISTERED_ASSUMPTIONS`;
- missing required domain/query/verifier/semantics -> `CANNOT_CHECK(reason)`;
- `C=X` is state-level `UNKNOWN`, but a query may still be `IDENTIFIED` if it is constant on `X`.

### Frozen controls

1. `UNKNOWN` nonidentifying hostile: `X={0,1}`, `C=X`, `q(x)=x` -> `CANNOT_IDENTIFY({0,1})`.
2. Query-identified despite state ambiguity: `X={0,1}`, `C=X`, constant `q(x)=7` -> `IDENTIFIED(7)`.
3. Empty set -> inconsistency, not `UNKNOWN` and not `CANNOT_IDENTIFY`.
4. Missing query -> `CANNOT_CHECK`, not `CANNOT_IDENTIFY`.

The identified-set/partial-identification and reject-option mathematics is parent-owned; the #833 residual is the common fail-closed semantics and machine distinction.

## 7. U-5 — predictive marginal does not identify epistemic/aleatoric decomposition

Frozen exact binary witness, outcome `Y in {0,1}`:

**Model A:** latent `Theta in {a,b}` with prior `(1/2,1/2)`; `Y=0` deterministically under `a` and `Y=1` deterministically under `b`.

- predictive marginal: Bernoulli(`1/2`);
- expected conditional variance: `0`;
- variance of conditional means: `1/4`.

**Model B:** same latent prior, but both conditional kernels are Bernoulli(`1/2`).

- predictive marginal: Bernoulli(`1/2`);
- expected conditional variance: `1/4`;
- variance of conditional means: `0`.

Thus the same predictive marginal admits opposite epistemic/aleatoric allocations under different registered latent semantics. A `PredictiveLaw` alone must fail closed on decomposition; a `LatentPredictiveModel` is required.

This exact non-identifiability result is parent-owned by #750/#751; this child incorporates its type boundary.

## 8. Exact/P2 certificate plan

The post-freeze executor/tests must use exact arithmetic and verify at least:

- all object-kind validations and illegal coercions;
- finite relational-image composition controls;
- exact union-bound arithmetic and the disjoint-failure anti-product hostile;
- shared-ancestor and dependent-root strict-overapproximation hostiles;
- missing-relation versus empty-relation behavior;
- unknown-versus-inconsistent-versus-cannot-check-versus-cannot-identify distinction;
- identified query under ambiguous state and nonidentified query under full-domain `UNKNOWN`;
- version transport resets raw evidence count;
- the two latent models have exactly equal predictive marginals and opposite `0` versus `1/4` variance components;
- deterministic receipt reproduction under normal Python and `python -O`.

No stochastic Monte Carlo result may substitute for these exact controls.

## 9. Parent ownership / non-novel mathematics

Strongest repository parents receive first refusal:

- #757/#761 — finite relational-image composition and dependence-safe chain coverage;
- #759/#765 — dependency-aware finite-DAG composition and local-vs-global boundary;
- #748/#749 — developmental uncertainty transport and no evidence-count migration;
- #750/#751 — epistemic/aleatoric separation and marginal-only non-identifiability;
- #766/#767 — finite-population calibration for selective capability prediction.

External parent mathematics includes confidence sets, set-valued/reachability analysis, relational join/projection, Boole/Fréchet arbitrary-dependence bounds, partial identification/identified sets, and selective classification/reject-option theory.

The only intended #833 residual is an architecture-independent typed interface that composes these already-owned mathematical ideas without conflating their meanings.

## 10. Frozen falsifiers

This tranche fails if any of the following occurs:

- object kinds can be silently interchanged;
- an independence-product confidence bound is reported without a registered independence model;
- local Cartesian propagation is reported as the exact joint result in either dependence hostile;
- a missing relation is treated as an empty relation or vice versa;
- a missing target domain fabricates a full-domain object instead of `CANNOT_CHECK`;
- transported target-version objects inherit source raw-evidence counts;
- `UNKNOWN`, `CANNOT_IDENTIFY`, `CANNOT_CHECK`, and inconsistency collapse to one terminal;
- an ambiguous state cannot yield an identified constant query;
- a marginal-only predictive law returns a unique epistemic/aleatoric decomposition;
- Model A and Model B fail to share the same predictive marginal or fail to exchange the two variance components;
- any parent-owned theorem is promoted as new uncertainty mathematics;
- a finite exact contract is promoted to universal or real-world calibration.

## 11. Claim ceiling

Allowed only if all frozen obligations pass:

`GMI_GLOBAL_UNCERTAINTY_AND_ABSTENTION_CONTRACT_AT_REGISTERED_FINITE_SCOPE`

Forbidden promotions from this tranche alone:

- `UNIVERSAL_UNCERTAINTY_CALIBRATION`
- `INDEPENDENCE_PROVED`
- `ALL_REAL_WORLD_CONFIDENCE_VALID`
- `UNIVERSAL_POSTERIOR_CORRECTNESS`
- `REAL_SCALE_UNCERTAINTY_VALIDATION`
- `COMPLETE_GMI`

No corpus migration, neutral-grammar closure, downstream family derivation, real-scale validation, or complete-GMI claim is part of this freeze.
# GMI #833 uncertainty / abstention contract freeze v1

**Parent:** #833 Section C  
**Child:** #851  
**Source main:** `5db372ef7003253d5846b324ed80a2454613983c`  
**Status:** pre-implementation theorem/evidence freeze

This file freezes the typed uncertainty ontology, composition/abstention theorem targets, parent evidence pins, hostile controls, and claim ceiling before executor/tests/results/reconciliation exist on this branch.

## Strongest merged parent evidence — pinned, not re-claimed

1. Dependency-aware finite-DAG uncertainty composition:
   - `research/gmi-dependency-aware-uncertainty-composition-v1/RESULT_V1.json`
   - Git blob `d5253d8b77f45a3dfc9f96ddf66eef427acb1bf9`
   - claim ceiling `DEPENDENCY_AWARE_UNCERTAINTY_COMPOSITION_AT_REGISTERED_FINITE_DAG_SCOPE`
   - owns shared-ancestor/global-vs-local relation semantics, arbitrary-dependence union bounds, missing-vs-empty relation distinction.
2. Developmental uncertainty transport:
   - `research/gmi-developmental-uncertainty-transport-v1/RESULT_V1.json`
   - Git blob `49df3257c9181c64bae63b53c503e302ca887fe8`
   - claim ceiling `SOUND_DEVELOPMENTAL_UNCERTAINTY_TRANSPORT_AT_REGISTERED_FINITE_SCOPE`
   - owns registered set transport, versioning, raw-evidence non-inheritance, missing-relation abstention.
3. Epistemic / aleatoric separation:
   - `research/gmi-epistemic-aleatoric-separation-v1/RESULT_V1.json`
   - Git blob `e422a880c7e1f49cd80260cc679c31e056a4046d`
   - claim ceiling `EXACT_EPISTEMIC_ALEATORIC_SEPARATION_FOR_REGISTERED_FINITE_LATENT_MODELS`
   - owns the same-marginal/different-decomposition impossibility and latent-semantics requirement.
4. Selective capability calibration:
   - `research/gmi-capability-calibration-v2/RESULT_V2.json`
   - Git blob `278845962ef2a573d3664fc3a400591e440ed313`
   - claim ceiling `EXACT_FINITE_POPULATION_CAPABILITY_ERROR_CALIBRATION_AT_REGISTERED_DETERMINATE_FRAME`
   - owns exact finite-population selective-risk calibration and abstention accounting.

The present child may compose and type these results; it may not rename their parent mathematics as new GMI theorems.

## U-1 — typed uncertainty objects

Freeze a tagged, architecture-independent interface. No one scalar called `uncertainty` is permitted to carry all semantics.

### U-1a FeasibleSet

`FeasibleSet(X,C,version,provenance)` where `C subseteq X`.

Semantics: current registered possibilities/admissible values only. No probability/coverage claim follows.

### U-1b ConfidenceSet

`ConfidenceSet(X,C,alpha,target,version,provenance,raw_evidence_count)` where `0 <= alpha <= 1` and the declared coverage premise is

`P(theta in C) >= 1-alpha`.

Coverage and informativeness are distinct. A full-domain object `C=X` can have structural coverage one while identifying nothing about a nonconstant query.

### U-1c PredictiveLaw

`PredictiveLaw(Y,P,version,provenance)` for an outcome probability law. It is aleatoric/predictive probability, not by itself a confidence set over models/parameters.

### U-1d LatentPredictiveModel

`LatentPredictiveModel(Theta,pi,K,version,provenance)` only when latent/model semantics are explicitly registered. Epistemic/aleatoric decomposition is defined relative to this object.

### U-1e SelectivePrediction

`SelectivePrediction(value_set,error_or_risk_certificate,coverage,scope,provenance)` only when selective calibration/reject semantics are actually established. Abstentions never count as successful predictions.

## U-2 — dependence-safe composition

For finite spaces `X_0,...,X_k`, source confidence set `C_0` with failure budget `alpha`, and preregistered relations `R_i subseteq X_i x X_(i+1)` whose true transition relation fails with probability at most `beta_i`, define

`C_(i+1) = R_i[C_i]`.

Target theorem:

`P(theta_k in C_k) >= max(0, 1-alpha-sum_i beta_i)`

with **no independence premise**.

DAG target: preserve a joint root set/global feasible-assignment relation. Local Cartesian propagation is sound but may be strictly wider under shared ancestors. Freeze the inherited hostile `a=x, b=x, y=a-b`: global `{0}` versus local `{-2,0,2}`.

Dependence hostile: two disjoint quarter-failure events have true joint-good probability `1/2`; multiplying `3/4 * 3/4 = 9/16` is unsound while the union lower bound `1/2` is attained.

## U-3 — missing, empty, and version semantics

- Missing relation + known registered target domain means **complete relation / maximal target ignorance**, not copying a source set and not inventing a nominal mapping.
- Registered empty relation means **infeasible/inconsistent**, not ignorance.
- Missing target domain or missing semantics required to construct/check an object means `CANNOT_CHECK`, not a fabricated full-domain object.
- Across developmental versions, a set/confidence claim may transport only through a registered relation and explicit failure budget. Target-version `raw_evidence_count` is zero unless fresh target-version evidence is separately registered.

## U-4 — global query / abstention semantics

For a registered `FeasibleSet` or `ConfidenceSet` with candidate set `C` and registered query `q`, define the identified set

`I_q(C) = {q(x): x in C}`.

Freeze exact terminals:

1. `C=emptyset` -> `INCONSISTENT_REGISTERED_ASSUMPTIONS`.
2. `|I_q(C)|=1` -> `IDENTIFIED(value)` even when `|C|>1`.
3. `|I_q(C)|>1` -> `CANNOT_IDENTIFY(candidate_values)`; unique factual prediction must abstain.
4. required domain/query/verifier/semantics absent -> `CANNOT_CHECK(reason)`.
5. `UNKNOWN` is the state `C=X` (maximal registered possibility), not a synonym for `CANNOT_CHECK` and not automatically a terminal. A constant query over `X` remains identifiable.

This is query-relative partial identification. State non-identifiability does not imply action/query non-identifiability if all surviving states agree on the protected query.

## U-5 — uncertainty-kind non-conflation

A marginal `PredictiveLaw` cannot license an epistemic/aleatoric decomposition. Freeze #750's same-full-marginal hostile: pure aleatoric and pure epistemic-mean latent models can both induce the same `P(Y=-1)=P(Y=+1)=1/2` marginal. Decomposition without registered latent semantics must terminate `CANNOT_DECOMPOSE_WITHOUT_LATENT_SEMANTICS`.

## Executable finite controls

The post-freeze executor must provide exact rational controls for:

- deterministic relational-image composition;
- failure-budget addition and clipping at one;
- disjoint-quarter dependence hostile (`true=1/2`, `independence-product=9/16`, union lower `1/2`);
- shared-ancestor global/local hostile (`{0}` versus `{-2,0,2}`);
- missing relation -> full target domain; empty relation -> inconsistency;
- `UNKNOWN` full domain with identity query -> `CANNOT_IDENTIFY`;
- same `UNKNOWN` full domain with constant query -> `IDENTIFIED`;
- empty candidate set -> inconsistency;
- missing query/domain -> `CANNOT_CHECK`;
- developmental transport with target raw evidence count zero;
- predictive-law decomposition without latent semantics -> fail closed;
- exact parent receipt blob/claim-ceiling validation.

## Parent terminology / literature anchors

Use established terms where they match:

- confidence set / confidence region;
- identified set / partial identification;
- set-valued image / reachability / relational projection;
- Boole union bound / Frechet-style arbitrary-dependence bounds;
- selective prediction / reject option (Chow-style error-reject tradeoff and later selective classification);
- epistemic versus aleatoric uncertainty only relative to explicit latent/model semantics.

## Frozen falsifiers

This tranche fails if any of these occurs:

- confidence and feasible-set semantics become interchangeable;
- a product-of-coverages shortcut is used without a dependence model;
- missing and empty relations share a terminal;
- UNKNOWN and CANNOT_CHECK are conflated;
- an empty candidate set is reported as UNKNOWN;
- state ambiguity forces abstention when the registered query is constant;
- a nonconstant query over a multi-value set is emitted as uniquely identified;
- developmental target versions inherit raw source sample counts;
- marginal predictive law is decomposed into epistemic/aleatoric parts without latent semantics;
- any parent receipt pin or claim ceiling drifts;
- finite registered results are promoted to universal/real-world calibration.

## Claim ceiling

`GMI_GLOBAL_UNCERTAINTY_AND_ABSTENTION_CONTRACT_AT_REGISTERED_FINITE_SCOPE`

Forbidden promotions:

- `UNIVERSAL_UNCERTAINTY_CALIBRATION`
- `INDEPENDENCE_PROVED`
- `ALL_REAL_WORLD_CONFIDENCE_VALID`
- `UNIVERSAL_POSTERIOR_CORRECTNESS`
- `REAL_SCALE_UNCERTAINTY_VALIDATION`
- `COMPLETE_GMI`

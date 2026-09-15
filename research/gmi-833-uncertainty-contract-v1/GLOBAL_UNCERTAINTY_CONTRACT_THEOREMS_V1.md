# Global uncertainty, composition, and abstention contract — v1

**Issue:** #851, child of #833 Section C  
**Freeze:** `research/gmi-833-uncertainty-contract-v1/FREEZE_V1.md`  
**Claim ceiling:** `GMI_GLOBAL_UNCERTAINTY_AND_ABSTENTION_CONTRACT_AT_REGISTERED_FINITE_SCOPE`

This tranche unifies already-established finite uncertainty results behind one typed, architecture-independent interface. It does not claim new probability mathematics, universal calibration, or validity outside the declared finite registered scope.

## 1. Why one scalar called “uncertainty” is mathematically unsafe

The following objects answer different questions and are not interchangeable:

1. `FeasibleSet(X,C,...)`: which registered states/parameters remain possible or admissible?
2. `ConfidenceSet(X,C,alpha,...)`: which set carries a stated coverage premise `P(theta in C) >= 1-alpha`?
3. `PredictiveLaw(Y,P,...)`: what probability law is assigned to future outcomes?
4. `LatentPredictiveModel(Theta,pi,K,...)`: what latent/model semantics support an epistemic/aleatoric decomposition?
5. `SelectivePrediction(...)`: on what selected subset is a prediction issued, with what risk/error certificate and determinate coverage?

A set may be maximally uninformative and still cover the truth. A predictive distribution may be precisely specified while leaving model/parameter uncertainty unidentified. A selective predictor may have a small certified error rate on determinate cases while abstaining elsewhere. Collapsing these into one number destroys the quantifiers needed for valid composition and abstention.

The executable adapter therefore uses a tagged sum of exact finite objects rather than an overloaded `uncertainty` field.

---

## 2. U-1 — feasible sets and confidence sets

Let `X` be a nonempty finite registered domain and `C subseteq X`.

### Definition U-1a — feasible set

`F = (X,C,v,p)`

is a feasible-set object at developmental/version identity `v` and provenance `p`. It asserts only that the current registered possibility/admissibility set is `C`. It has no probability claim.

### Definition U-1b — confidence set

`K = (X,C,alpha,theta,v,p,n_raw)`

is a confidence-set object only when an external statistical argument licenses

`P(theta in C) >= 1-alpha`, `0 <= alpha <= 1`.

`n_raw` records raw evidence owned by that version. Transporting the set does not automatically transport the underlying observations.

### Proposition U-1c — coverage is not informativeness

There is no implication

`high coverage => identification`.

**Witness.** Let `C=X={0,1}` and `alpha=0`. Coverage is one, yet for the identity query `q(x)=x`, the identified set is `{0,1}` and the value is not uniquely identified. For the constant query `q(x)=7`, the identified set is `{7}` and the protected query is identified despite complete state ambiguity. `□`

This distinction is the global reason the interface keeps `coverage_lower_bound` separate from `identified_set`.

---

## 3. U-2 — dependence-safe uncertainty composition

Fix finite registered spaces `X_0,...,X_k`. Let source truth `theta_0` and a source confidence set `C_0 subseteq X_0` satisfy

`P(theta_0 in C_0) >= 1-alpha`.

For each stage `i=0,...,k-1`, let

`R_i subseteq X_i x X_(i+1)`

be a preregistered relation, and let `G_i` be the event that the true transition obeys

`(theta_i,theta_(i+1)) in R_i`.

Assume only

`P(G_i^c) <= beta_i`.

No independence assumption is made. Define the exact relational images

`C_(i+1) = R_i[C_i] = { y : exists x in C_i, (x,y) in R_i }`.

### Theorem U-2A — finite-chain composition

For every finite `k`,

`P(theta_k in C_k) >= max(0, 1-alpha-sum_i beta_i)`.

### Proof

Let `G_0^src = {theta_0 in C_0}`. On

`G_0^src ∩ G_0 ∩ ... ∩ G_(k-1)`,

pathwise induction proves `theta_i in C_i` for every stage: the base is the source event; if `theta_i in C_i` and the true transition lies in `R_i`, then by definition of relational image `theta_(i+1) in R_i[C_i]=C_(i+1)`.

Therefore

`P(theta_k notin C_k)`

is at most the probability that at least one source/relation-good event fails. Boole's union bound gives

`P(theta_k notin C_k) <= alpha + sum_i beta_i`,

and probabilities are lower-bounded by zero. `□`

This is the general composition rule claimed by this tranche: finite registered relations with arbitrary dependence and explicit failure budgets.

### Dependence hostile

If two stage-good events each have marginal probability `3/4`, it is not sound to infer joint probability `9/16`. Let their failure sets be disjoint quarters of one probability space. Then joint-good probability is exactly `1/2`, while the independence product is `9/16`. The union-bound lower bound is also `1/2` and is attained. Thus multiplication requires an additional dependence model.

---

## 4. U-2B — DAG composition and shared dependence

For a finite DAG with registered root uncertainty and local relations, the exact object is the **global feasible-assignment relation**:

`A = {x_V : x_R in C_R and every registered parent/output tuple satisfies its relation}`.

For output nodes `O`, the exact propagated set is the projection `proj_O(A)`.

A local forward algorithm that replaces joint parent sets by Cartesian products is sound as an over-approximation, but shared ancestors can make it strictly wider.

### Shared-ancestor hostile

Let `x in {-1,+1}`, `a=x`, `b=x`, and `y=a-b`.

The global relation preserves the equality `a=b`, so

`C_y^global = {0}`.

If local propagation forgets that dependence, it retains

`C_a=C_b={-1,+1}`

and computes

`C_y^local={-2,0,+2}`.

Hence

`C_y^global subsetneq C_y^local`.

The narrower `{0}` is licensed only by a representation that preserves the joint/shared-ancestor relation. This theorem and the 1,024-case finite certificate are owned by the merged dependency-aware parent package; #851 imports their scope and semantics rather than rebranding them.

---

## 5. U-3 — missing relation, empty relation, and developmental versions

### Missing relation

If a source and target domain are registered but the transition relation is unknown, the fail-closed relation is the complete relation

`R_missing = X_source x X_target`.

For every nonempty source candidate set `C`,

`R_missing[C] = X_target`.

Thus missing mechanism knowledge becomes maximal registered target ignorance. Copying `C` forward would assert an unregistered identity relation and can be false.

### Empty registered relation

If a relation is explicitly registered as empty, then for every source set

`R_empty[C] = emptyset`.

This is not ignorance. It says no registered assignment satisfies the relation. A positive coverage premise on the resulting empty set would be contradictory. The adapter therefore emits

`INCONSISTENT_REGISTERED_ASSUMPTIONS`

and downgrades guaranteed coverage to zero rather than serializing a misleading positive confidence lower bound.

### Missing target semantics

If the target domain or other semantics needed to construct/check the object are not registered, no full-domain object can be fabricated. The terminal is

`CANNOT_CHECK(reason)`.

### Developmental evidence ownership

Set-level claims may transport from version `v` to `v+1` only through a registered relation and failure budget. The transported object receives `raw_evidence_count=0` unless new evidence is explicitly registered at the target version. This is an evidence-identity rule: relation transport moves a claim, not the physical observations that originally supported it.

The exact witness begins with `2048` raw source observations, applies two registered relations with budgets `1/100` and `1/200` to a source budget `1/20`, and ends at version 2 with

`alpha = 1/20 + 1/100 + 1/200 = 13/200`,

coverage lower bound `187/200`, and raw target evidence count zero.

---

## 6. U-4 — global identified-set and abstention semantics

Let `C subseteq X` be the candidate set of a registered feasible/confidence object and let `q:X->Y` be a registered protected query. Define the **identified set**

`I_q(C) = { q(x) : x in C }`.

This is standard partial-identification logic applied to the registered computational object.

### Theorem U-4 — query terminal partition

Exactly one of the following applies when the necessary domain/object/query semantics are registered:

1. `C=emptyset`: `INCONSISTENT_REGISTERED_ASSUMPTIONS`.
2. `|I_q(C)|=1`: `IDENTIFIED(y)` for the unique `y`.
3. `|I_q(C)|>1`: `CANNOT_IDENTIFY(I_q(C))`; a unique factual answer must abstain.

If the domain, query, verifier, or required semantics are absent, the distinct terminal is

`CANNOT_CHECK(reason)`.

### Proof

For nonempty finite `C`, the image `I_q(C)` is nonempty. Its cardinality is therefore either one or greater than one, giving cases 2 and 3. The empty-set case is disjoint. Missing semantics are meta-level failure to construct/evaluate the identified set and therefore must not be merged with any of the three mathematical cases. `□`

### UNKNOWN is a state, not a checking failure

Define

`UNKNOWN_X := C=X`.

It is maximal registered possibility. It is not synonymous with `CANNOT_CHECK`: the domain is known and queries can be evaluated over it. Under `UNKNOWN_X`, a nonconstant query can be nonidentified, while a constant query is still identified.

This makes abstention **query-relative**. State/parameter ambiguity does not imply action-level ambiguity when all surviving states agree on the protected decision.

---

## 7. U-5 — predictive randomness is not automatically epistemic uncertainty

A `PredictiveLaw` specifies `P(Y)` over registered outcomes. It does not by itself specify a latent/model space `Theta`, weights `pi(theta)`, or conditional kernels `K(Y|theta)`.

If such latent semantics are registered, the finite law of total variance gives

`Var(Y) = E_pi[Var(Y|theta)] + Var_pi(E[Y|theta])`.

The first term may be called the registered aleatoric variance component and the second the epistemic variance of the conditional predictive mean **relative to that latent semantics**.

### Non-identifiability theorem U-5

No function of the predictive marginal alone can uniquely recover that decomposition over the registered latent-model class.

### Proof by counterexample

Two finite latent models induce exactly

`P(Y=-1)=P(Y=+1)=1/2`.

- Pure aleatoric model: one latent state with the fair conditional kernel. Decomposition `(A,E_mean,T)=(1,0,1)`.
- Pure epistemic-mean model: two equal-weight latent states, one deterministically emits `-1`, the other `+1`. Decomposition `(0,1,1)`.

The marginals are identical while the decompositions differ. Therefore a marginal-only object cannot identify the decomposition. `□`

The global adapter returns

`CANNOT_DECOMPOSE_WITHOUT_LATENT_SEMANTICS`

for a marginal `PredictiveLaw` rather than inventing a split.

---

## 8. Selective prediction / reject-option boundary

A calibrated selective predictor needs at least two distinct coordinates:

- risk/error information on the **determinate** predictions;
- the fraction/coverage of cases on which a determinate prediction is issued.

Abstentions are not successes and cannot enter the accuracy numerator. The merged finite-population parent package provides one exact certificate at its registered determinate frame: upper error `3/64`, candidate-grid determinate coverage `1/16`, with abstentions explicitly excluded from success accounting.

This follows the established reject-option/selective-prediction distinction: one trades coverage against error/risk instead of treating rejection as a correct label. Chow's classical reject-option analysis and modern selective-classification work own that framing; #851 only makes it a typed GMI interface requirement.

---

## 9. Parent ownership and literature crosswalk

The mathematical parents are explicit:

- **confidence sets/regions:** coverage is a statistical guarantee tied to assumptions and sampling/evidence, not a synonym for possibility sets;
- **set-valued / reachability / relational analysis:** exact images, joins, projections, and global feasible assignments own the propagation mathematics;
- **Boole/Fréchet arbitrary-dependence bounds:** own the dependence-safe probability algebra;
- **partial identification:** identified sets formalize what a model/data/assumption set does and does not uniquely determine; see Manski's partial-identification programme;
- **random sets:** provide a broad mathematical home for set-valued uncertainty objects;
- **reject option / selective classification:** Chow's error-reject tradeoff and later selective prediction own the risk-versus-coverage framing;
- **epistemic/aleatoric decomposition:** law-of-total-variance decompositions require declared latent/model semantics; the merged #750 package owns the exact finite counterexample.

Representative anchors include C. K. Chow, *On Optimum Recognition Error and Reject Tradeoff* (1970); C. F. Manski, *Partial Identification of Probability Distributions* (2003) and later identification/decision work; I. Molchanov, *Theory of Random Sets* (2005); and Y. Geifman & R. El-Yaniv, *SelectiveNet* (ICML 2019). These are parent theories, not novelty claims.

Repository parents pinned by #851 are:

- `gmi-dependency-aware-uncertainty-composition-v1`;
- `gmi-developmental-uncertainty-transport-v1`;
- `gmi-epistemic-aleatoric-separation-v1`;
- `gmi-capability-calibration-v2`.

The executor verifies their exact Git blobs, claim ceilings, and one load-bearing semantic field before issuing a GREEN receipt.

---

## 10. Claim boundary

Allowed terminal:

`GMI_GLOBAL_UNCERTAINTY_AND_ABSTENTION_CONTRACT_AT_REGISTERED_FINITE_SCOPE`

This means the registered finite GMI foundation now has one typed uncertainty interface, a dependence-safe composition rule at the claimed finite relational scope, and globally consistent query/abstention terminals.

It does **not** imply:

- `UNIVERSAL_UNCERTAINTY_CALIBRATION`;
- `INDEPENDENCE_PROVED`;
- `ALL_REAL_WORLD_CONFIDENCE_VALID`;
- `UNIVERSAL_POSTERIOR_CORRECTNESS`;
- `REAL_SCALE_UNCERTAINTY_VALIDATION`;
- `COMPLETE_GMI`.

Real-world calibration, infinite/general stochastic-process conditions, posterior correctness, and domain-specific statistical assumptions remain separate evidence obligations.

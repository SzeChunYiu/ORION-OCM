# GMI Developmental Realization Principle v1

Status: **FORMAL SYNTHESIS EXTENSION — NORMATIVE REALIZATION ≠ MORPHOGENETIC DISCOVERY**

Refs: #233, #377, #373, #369, GMI-v1.

## 1. Purpose

GMI-v1 already separates:

- task-relative semantic developmental state;
- morphology as a resource-bounded realization/factorization of that state;
- verified capability/resource profiles;
- within-morphology development `U`;
- structural/morphogenetic change `Gamma`.

This document answers the next question:

> Given a cognitive obligation and a set of semantically adequate realizations, what does it mean for one machine-intelligence morphology to be better suited than another, and how is that different from the process that actually discovers the morphology?

The answer must not collapse into “the architecture with the highest benchmark score wins,” and it must not assume that a bounded developmental process can find the normative optimum.

---

# 2. Cognitive obligation

Let a registered cognitive obligation be

\[
\Omega=(\mathcal E, D, J, V, C, H, \mathcal R),
\]

where:

- `E` is the ecology/task family;
- `D` is the legal development protocol;
- `J` is the registered intervention/probe class used to define semantic sufficiency;
- `V` is the external verification/admissibility contract;
- `C` is the external constitution/authority boundary;
- `H` is the horizon or stopping rule;
- `R` is the declared raw resource-coordinate semantics.

Let

\[
S_\Omega
\]

be the task-relative semantic developmental sufficient state induced by GMI-v1: developmental situations are equivalent when every admissible future intervention/programme induces the same registered future semantic-trace law.

`S_Omega` is semantic. Raw implementation cost is not part of this quotient unless the obligation explicitly promotes resource consequences into the semantic contract.

---

# 3. Realization

A morphology

\[
M=(F,\Theta,K,U,\Gamma,\kappa,\rho_M)
\]

**realizes** `S_Omega` on scope `X` when its compiler/semantic map `kappa` preserves the registered semantic distinctions required by `Omega` on `X`.

Exact realization:

\[
M \models_X S_\Omega
\]

means semantic equivalence is preserved exactly under every registered intervention/programme in scope.

Approximate realization is permitted only when the obligation itself declares an admissible distortion/approximation contract. A generic distance threshold is not automatically an equivalence relation and therefore does not create a quotient by itself.

The feasible realization set is

\[
\mathcal M_\Omega(X)
=
\{M: M\models_X S_\Omega\}.
\]

If no candidate satisfies the obligation:

```text
NO_ADMISSIBLE_REALIZATION_AT_SCOPE
```

is a valid terminal.

---

# 4. Raw lifetime burden

For morphology `M`, ecology `e`, initial developmental situation `d`, protocol `D`, and horizon/stopping rule `H`, define the complete raw burden vector

\[
B_M(e\mid d,D,H)
\]

over the registered coordinates `R`.

Typical coordinates include:

```text
initial construction / pretraining / compilation
new information supplied
development / acquisition work
proposal / search / reasoning work
verification / checker work
tool / environment interaction
persistent storage
active memory
index construction / maintenance
communication
revision / invalidation / relearning
human intervention
CPU / GPU / wall / I/O / energy where measured
```

No coordinate is free merely because it occurs before deployment or between tasks.

A scalar lifetime cost exists only after a prospectively declared valuation/price functional

\[
\lambda: \mathbb R_+^{|R|}\to\mathbb R.
\]

Without `lambda`, compare Pareto frontiers.

---

# 5. Developmental realization frontier

For obligation `Omega`, ecology family/distribution `mu`, horizon `H`, and admissible capability floor `Q*`, define

\[
\mathcal F^{real}_\Omega(\mu,H,Q^*)
=
\operatorname{Pareto}\left\{
\big(Q_M,\,B_M\big):
M\in\mathcal M_\Omega,
Q_M\succeq Q^*
\right\}.
\]

A morphology is **realization-dominated** at the registered scope if another admissible morphology is no worse on every registered capability/resource coordinate and strictly better on at least one.

This is a normative comparison over admissible realizations.

It does not say the dominated morphology cannot be discovered, cannot be historically common, or cannot be useful under a different ecology/resource regime.

---

# 6. Scalarized optimum when prices are declared

Given a prospectively frozen scalar valuation `lambda`, define

\[
M^*_{\Omega,\mu,H,\lambda}
\in
\arg\min_{M\in\mathcal M_\Omega,\;Q_M\succeq Q^*}
\mathbb E_{e\sim\mu}
\left[\lambda\big(B_M(e\mid d,D,H)\big)\right].
\]

This is the **normative developmental realization optimum**.

It is task-, ecology-, horizon-, protocol-, verifier-, constitution- and price-relative.

Therefore GMI-v1 does **not** predict one universally best morphology.

A change in any of

```text
ecology
reuse horizon
verification strength
revision/drift rate
hardware / communication prices
memory/storage prices
latency requirement
training/acquisition budget
risk/authority constraints
```

may move the optimum to another morphology.

That movement is a morphology **phase boundary** only when the change is registered prospectively and the candidate/frontier set is fixed or independently defined.

---

# 7. Normative optimum is not morphogenesis

The central split is:

\[
\boxed{
\text{realization optimum}
\neq
\text{morphology actually found by development/search}
}
\]

Let

\[
\Gamma_g(M\mid \Sigma_0,\Omega,B_{search})
\]

be the distribution over morphologies produced by developmental/morphogenetic process `g` from starting search state `Sigma_0` under search budget `B_search`.

Then the realized search outcome is sampled from `Gamma_g`, not from the normative argmin oracle.

Define the **morphogenetic regret** under scalar valuation `lambda` as

\[
Regret_{morph}(g)
=
\mathbb E_{M\sim\Gamma_g}
\left[
C_\lambda(M)-C_\lambda(M^*)
\right],
\]

where `C_lambda` is the registered scalarized lifetime burden at matched capability.

For vector/Pareto analysis, replace scalar regret with distance/dominance deficiency relative to the registered realization frontier, under a prospectively declared metric if needed.

A strong developmental system should therefore be studied on two axes:

1. **realization quality** — how good is the found morphology once built?
2. **morphogenetic efficiency** — how much search/development was required to find it?

A morphology with excellent deployment economics may still be a poor developmental choice if discovering/training it is prohibitively expensive at the actual horizon.

---

# 8. Full lifetime criterion including morphology discovery

Let

\[
B^{discover}_g(M)
\]

be the burden spent by morphogenetic process `g` to discover, validate, construct and admit `M`.

Then complete lifetime burden is

\[
B^{life}_{g,M}
=
B^{discover}_g(M)
+
B^{serve/update}_{M}.
\]

This blocks the common error:

> “architecture A is cheap after training, therefore A is the best intelligence form.”

Whether A is preferred depends on whether its build/discovery cost is repaid within the registered effective horizon before drift/invalidation/reset.

---

# 9. Parent theory ownership

This principle intentionally adopts rather than renames mature mathematics.

## 9.1 Rate-distortion / Information Bottleneck

Owns important cases where one trades representation complexity/information against distortion or predictive/task relevance.

GMI use:

```text
semantic obligation / allowed distortion
+ representation resource pressure
-> admissible representation frontier
```

GMI does not claim rate-distortion itself as novelty.

## 9.2 Bounded rationality / rate-distortion control

Owns optimization of policies/decisions under information-processing constraints and can produce specialization/hierarchical organization under bounded information.

GMI use:

```text
resource-constrained cognition/control realization
```

Again parent-owned.

## 9.3 Resource-rational / rational metareasoning

Owns the normative idea that computations themselves have value/cost and that cognition should be selected by expected downstream value.

GMI use:

```text
which reasoning/search/verification organization is worth paying for
```

## 9.4 Algorithm selection / portfolio methods

Owns mapping instance/ecology features to the best member of a fixed algorithm portfolio.

GMI use:

```text
fixed known morphology portfolio selection
```

Track B novelty cannot be “select an architecture using features.”

## 9.5 Neural architecture search / AutoML / evolution

Owns large parts of searching architecture/hyperparameter/update-rule spaces.

GMI use:

```text
morphogenetic process Gamma_g
```

The search algorithm may be parent-owned while GMI supplies common semantic/resource/evidence accounting.

## 9.6 Program synthesis / universal search

Owns broad executable-form search and description-length/search-bias relationships.

GMI use:

```text
programmatic morphology realization / search
```

## 9.7 Factored models / graphical models / modularity theory

Owns many compact-factorization and dependency-induced modularity results.

GMI use:

```text
why one realization can be exponentially more compact/local than another
```

---

# 10. What GMI adds at the synthesis level

The synthesis contribution is not a new optimization theorem at this stage.

It is one explicit separation of:

```text
semantic developmental obligation
-> admissible realization set
-> capability/resource realization frontier
-> morphology-specific development/update dynamics
-> morphogenetic search distribution
-> discovery burden
-> complete lifetime burden
-> generality profile across ecologies
```

using the same objects for neural, symbolic, probabilistic, programmatic, evolutionary and governed-explicit systems.

This makes several otherwise-confused questions distinct:

### Q-A: Can a morphology represent the required cognition?

Semantic sufficiency / admissibility.

### Q-B: If it can, how expensive is it to realize and maintain?

Realization frontier.

### Q-C: Can a bounded developmental process actually discover/build it?

Morphogenesis/search.

### Q-D: Does experience improve the process of finding later useful realizations?

K2/K3 / meta-morphogenesis.

### Q-E: Does the answer transfer across materially different ecologies?

Generality profile / E2–E4.

---

# 11. Candidate explanation of neural dominance — conditional, not privileged

Neural/differentiable morphologies can dominate a registered regime when, relative to available alternatives:

```text
large reusable data/task horizon
+ dense differentiable credit signal
+ high-value distributed statistical approximation
+ accelerator-friendly operations
+ cheap amortized serving
```

more than repay:

```text
training/acquisition cost
parameter/storage cost
revision/retraining cost
verification limitations
plasticity/interference cost
```

This is not a theorem that neural systems dominate generally.

Likewise explicit symbolic/programmatic morphologies may dominate regimes with strong pressure for:

```text
exactness
local revision
small data
sparse compositional rules
strong formal verification
rapid regime change
high cost of retraining
```

and hybrid morphologies may occupy regimes where different obligations demand different realization properties.

These are hypotheses to be tested by prospective phase prediction, not architecture labels inserted after outcomes.

---

# 12. Minimal propositions

## RP-1 — Pareto admissibility [definition consequence]

If `M1` and `M2` realize the same registered semantic obligation at matched capability and

\[
B_{M1}\preceq B_{M2}
\]

coordinate-wise with at least one strict inequality, `M2` is realization-dominated at that scope.

No scalar price vector is required.

## RP-2 — price-conditioned reversal [elementary theorem]

If neither resource vector dominates the other, there exist nonnegative price vectors under which either morphology may be preferred whenever each has at least one coordinate advantage that receives positive price and no other priced disadvantage overwhelms it.

Therefore post-hoc scalar weighting can manufacture a winner and is forbidden for primary inference.

## RP-3 — horizon crossover [elementary theorem]

For two fixed-capability morphologies with affine lifetime scalar costs

\[
C_i(H)=A_i+Hc_i,
\]

where `A_i` is build/acquisition cost and `c_i` is expected per-use burden, if `c_1<c_2` and `A_1>A_2`, the unique crossover is

\[
H^*=\frac{A_1-A_2}{c_2-c_1}.
\]

This is amortization arithmetic, not GMI novelty.

## RP-4 — discovery-cost reversal [elementary theorem]

If morphology `M1` has lower serving burden than `M2` but the extra morphogenetic discovery/build cost exceeds all expected serving savings over the registered horizon, `M1` is worse in complete lifetime burden.

## RP-5 — normative/search separation [formal distinction]

An oracle optimum over `M_Omega` does not imply a bounded morphogenetic process can identify or reach it. In Turing-complete/unbounded spaces, exact global realization optimization is generally not computably available without strong restrictions.

Therefore GMI phase-law experiments must state whether they test:

```text
NORMATIVE_FRONTIER
SEARCH_RECOVERY
or BOTH
```

---

# 13. Empirical obligations

A serious morphology-dominance result must freeze before protected outcomes:

```text
semantic obligation
candidate morphology set / generative space
ecology and task distribution
horizon / stopping rule
raw resource semantics
capability floor
verifier strength
price vector if scalarization is primary
morphogenetic search budget if search is evaluated
parent methods
phase variable(s)
predicted transition region
negative/control region
```

Then distinguish:

```text
1. predicted normative frontier transition
2. whether blind/neutral search recovers frontier occupants
3. search/discovery cost
4. disjoint-ecology replication
```

A post-hoc architecture label is not a phase law.

---

# 14. Relationship to the original Track-B questions

## B1 — fundamental basis

This principle does not restore a unique cognitive atom. A useful basis/factorization is judged partly by whether it yields an efficient realization of semantic developmental distinctions.

## B2 — morphogenesis

`Gamma_g` is a bounded search/development distribution over realizations, not an oracle mapping directly to the normative optimum.

## B3 — developmental limits/dominance

This document supplies the canonical target:

\[
\text{semantic adequacy}
+
\text{lifetime capability/resource frontier}
+
\text{discovery cost}.
\]

The earlier `d(development)/d(cost)` intuition becomes one local derivative/summary of this richer frontier, not the definition of intelligence.

## B4 — unknown morphology

A credible missing morphology requires a prospectively identified **frontier hole**: known parents cannot occupy a theoretically/headroom-feasible region under the frozen obligation/resources.

## B5 — meta-morphogenesis

K3/meta-morphogenesis asks whether experience reduces the burden/regret of `Gamma_g` itself on fresh ecology families.

---

# 15. Hard boundaries

GMI-v1 must retain:

```text
NO_UNIVERSAL_BEST_MORPHOLOGY
NO_UNIVERSAL_EXACT_MORPHOLOGY_PREDICTOR_FOR_ARBITRARY_TURING_COMPLETE_SYSTEMS
NO_FREE_DISCOVERY_COST
NO_POST_HOC_SCALAR_WINNER
NO_NEW_MORPHOLOGY_FROM_SOURCE_CODE_NOVELTY
NO_MORPHOGENESIS_CLAIM_FROM_NORMATIVE_OPTIMUM_ALONE
```

Allowed negative terminals:

```text
PARENT_REALIZATION_THEORY_SUFFICIENT
NO_NONTRIVIAL_FRONTIER_RESIDUAL
SEARCH_COST_DOMINATES
MORPHOLOGY_NOT_SEMANTICALLY_ADMISSIBLE
NO_PROSPECTIVE_PHASE_PREDICTION
CANNOT_CHECK_<reason>
```

---

# 16. Current claim ceiling

The strongest statement earned by this document alone is:

```text
GMI_DEVELOPMENTAL_REALIZATION_PRINCIPLE_SPECIFIED_V1
```

Meaning:

> GMI-v1 has a coherent normative object for comparing semantically adequate machine-intelligence realizations under complete lifetime resources, and a separate morphogenetic object for the bounded process that searches for those realizations.

It does **not** mean a new universal morphology theorem has been discovered.

The next theory work is to machine-check/calibrate RP-1…RP-4 on exact finite cases, register counterexamples to common overgeneralizations, and ask whether any nontrivial cross-paradigm predictive residual remains after rate-distortion, resource-rational, algorithm-selection and family-native parents.

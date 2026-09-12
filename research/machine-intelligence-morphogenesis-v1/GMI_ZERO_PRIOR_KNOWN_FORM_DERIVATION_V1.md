# GMI Zero-Prior Known-Form Derivation v1

Status: **CORE FALSIFICATION PROGRAMME / THEORY COMPLETENESS TEST**

Status date: 2026-09-12.

Purpose:

> Test whether GMI could have derived known machine-intelligence forms in a world where none had yet been invented. Explanation after historical observation is insufficient.

---

# 1. Zero-prior constitution

For each derivation trial, hide:

```text
architecture/family names
historical implementation patterns
papers and benchmark outcomes for the held-out form
named search macros that instantiate the form
```

Provide only:

\[
\mathcal Z=(O,\Xi_{obl},D,J,V,C,P,H,\mathcal G_0),
\]

where:

```text
O        semantic obligation
Xi_obl   measured obligation/demand coordinates
D        legal development information
J        interventions/teaching actions
V,C      verifier and constitution
P        resource/substrate context
H        developmental horizon/history conditions
G0       architecture-neutral primitive carrier/operator grammar
```

GMI must output before neutral search:

```text
predicted carrier type(s)
predicted operator/mechanism set
predicted state factorization
predicted update/development law class
predicted resource/scaling response
negative twins
parent-equivalent alternatives
claim confidence / unresolved gap
```

---

# 2. Derivation operator

Let `R` range over legal low-level realizations expressible by `G0`. Define

\[
R^*(\mathcal Z)
\in
\arg\min_{R\in Adm(O)}
\left[
L_O(R)+\pi(P)^\top\rho(R)
\right]
\]

subject to semantic quotient preservation and legal-development constraints.

GMI does not need to reconstruct historical source code. It succeeds if it predicts the implementation-invariant property/mechanism vector of the held-out family and neutral search recovers a realization in that equivalence neighborhood.

---

# 3. Acceptance ladder

```text
Z0 POST-HOC HOME
   GMI can describe the known family after being told it exists.

Z1 DIRECTIONAL DERIVATION
   ecology coordinates predict why the family should gain/lose advantage.

Z2 PROPERTY-FIRST PREDICTION
   mechanism/property vector frozen before search.

Z3 NEUTRAL REDISCOVERY
   low-level grammar recovers matching form without named macro.

Z4 HELD-FAMILY PREDICTION
   response law fitted on other forms/ecologies predicts held-out family niche.

Z5 COUNTERFACTUAL DISCOVERY
   GMI predicts an unknown form before implementation and neutral search recovers it.
```

A general theory should eventually reach at least Z3 on major known families before claiming Z5 discovery power.

---

# 4. Domain-level derivations from obligation geometry

## D1 coefficient/function-field state

Predicted when:

```text
many queries reuse the same regular mapping
semantic regularities admit compression into shared parameters/basis coefficients
updates can be amortized
approximation is legal
parameterized evaluation is cheaper than per-query search or explicit exemplar storage
```

Negative twin:

```text
highly volatile independent facts with little reusable regularity
```

Gap: quantitative pre-outcome estimator of compressibility/generalization remains open.

## D2 exemplar/memory-indexed state

Predicted when:

```text
individual distinctions are numerous and volatile
local insertion/deletion is cheap
exact/provenance-bearing records matter
compression into shared parameters causes interference or update cost
```

Negative twin: smooth low-dimensional regularity with high query reuse.

## D3 probabilistic-belief state

Predicted when:

```text
multiple latent hypotheses remain live
protected decisions depend on uncertainty/calibration
new evidence must update relative belief
partial observability is material
```

Negative twin: fully observed deterministic exact state.

## D4 symbolic/program state

Predicted when:

```text
obligation has reusable discrete compositional laws
exactness/verification matters
small rules/programs replace large extensional tables
```

Negative twin: noisy high-dimensional perception with no compact stable symbolic law.

## D5 search/frontier state

Predicted when:

```text
answer-specific computation is large
precompiling every answer is uneconomic
branching alternatives exist
partial candidates can be cheaply evaluated/pruned
```

Negative twin: repeated identical queries where compilation/cache amortizes.

## D6 dynamical sufficient state

Predicted when:

```text
future behavior depends on history
history admits a compact recursively updateable sufficient statistic
replaying full history is expensive
```

Negative twin: memoryless IID mapping.

## D7 collective/distributed state

Predicted when:

```text
relevant information/resources are partitioned across locations/agents
centralization is impossible or expensive
communication can reconstruct target semantics at lower burden
```

Negative twin: all information local and communication expensive.

## D8 morphogenetic/self-rewriting state

Predicted when:

```text
regime changes persist
fixed-family regret is high
local/global architecture change can amortize over future use
switch/search cost is lower than remaining fixed
```

Negative twin: stationary short-horizon ecology.

These are domain-direction derivations, not yet complete quantitative response laws.

---

# 5. Known-form derivation table

The table below freezes what GMI should derive from zero prior. `Status` refers to current theory strength, not historical empirical acceptance.

| Held-out known form | Zero-prior ecology signature | Predicted structural property | Current derivation status | Main gap |
|---|---|---|---|---|
| linear regression | low-dimensional approximately linear conditional mean, stationary mapping, squared-error style loss | compact coefficient vector + linear evaluation | PARENT-THEOREM / Z1 | pre-outcome test for linear sufficiency |
| logistic regression / GLM | exponential-family outcome with low-dimensional sufficient predictors | coefficient field + link function | PARENT-THEOREM / Z1 | automatic family/link selection |
| kernel / basis machine | smooth similarity geometry, limited data, reusable fixed feature relation | weighted basis/similarity expansion | PARENT-THEOREM / Z1 | kernel/geometry prediction |
| kNN / case memory | local metric continuity, cheap writes, volatile exemplars, weak compression value | explicit exemplar memory + local retrieval | CONDITIONAL / Z1 | metric identifiability and dimension scaling |
| decision tree | piecewise/discontinuous conditional structure with sparse partition rules | hierarchical conditional partition | CONDITIONAL / Z1 | predict split geometry and tree depth |
| boosted additive trees | residual errors successively correctable by weak partition learners | staged additive residual correction | PROGRAMME / Z1 | quantitative weak-learner edge law |
| Bayesian network / graphical belief | uncertain latent variables with sparse conditional independence | factorized probability state + conditioning | PARENT-THEOREM / Z1 | structure discovery under intervention |
| HMM / Kalman-like estimator | sequential hidden state with compact Markov sufficient statistic and uncertainty | recurrent probabilistic state update | PARENT-THEOREM / Z1 | nonlinear/non-Gaussian boundary |
| rule/expert system | sparse reusable exact if/then laws, low perceptual noise | symbolic rule state + exact rewrite | CONDITIONAL / Z1 | rule acquisition burden |
| SAT/SMT/constraint solver | exact compositional constraints, discrete admissibility | symbolic constraints + propagation/search | PARENT / Z1 | solver-family response law |
| A*/best-first search | query-specific combinatorial path problem with useful lower-bound heuristic | explicit frontier + priority expansion | PARENT / Z1 | heuristic-value prediction |
| MCTS | branching sequential decisions, stochastic rollouts/evaluation, limited exact model | tree/frontier search with adaptive sampling | CONDITIONAL / Z1 | rollout/value bias law |
| finite-state / recurrent machine | sequence dependence with bounded sufficient state | compact dynamical state | FORMAL principle / Z1 | state-dimension estimator |
| linear/state-space sequence model | long sequence generated by stable low-dimensional dynamics and scan-efficient substrate | recurrent linear/structured state update | CONDITIONAL / Z1 | nonlinear boundary and state order |
| MLP | reusable high-dimensional nonlinear map, smooth/compositional structure, dense differentiable feedback | layered nonlinear coefficient machine | PARENT + PROGRAMME / Z1 | reachability/generalization quantitative law |
| CNN | translation/local symmetry + local dependency | shared local filters / equivariant factorization | PARENT + PROGRAMME / Z2 target | quantitative symmetry-to-burden law |
| GNN/message passing | permutation-respecting relational graph + local edge interactions | shared neighborhood aggregation | PARENT + PROGRAMME / Z2 target | depth/oversquashing/locality phase law |
| RNN/LSTM | online sequential processing + history dependence + low-dimensional evolving state | gated recurrent state | PROGRAMME / Z2 target | gating mechanism prediction |
| Transformer | per-example dependency graph varies; long-range content interaction; high parallel-training value | content-dependent routing + shared token transforms + positional distinction | FORMAL mechanisms + PROGRAMME / Z2 target | quantitative attention-vs-fixed-routing frontier |
| sparse/local attention | semantic dependency density sparse relative to context size | conditional sparse routing | PROGRAMME / Z2 target | dependency-density estimator |
| MoE | heterogeneous modes + sparse per-example demand + communication not dominant | conditional heterogeneous expert routing | PROGRAMME / Z2 target | heterogeneity/communication phase boundary |
| external memory / RAG | broad stable predictive core + volatile/provenance-heavy residual distinctions | parametric core + explicit retrievable authority state | PRQ + PROGRAMME / Z2 target | empirical residual estimator |
| LoRA/adapters | target change small/structured relative to reusable core | localized/low-rank residual update | PROGRAMME / Z2 target | residual rank prediction |
| ensemble | partially independent errors and acceptable serve burden | multiple predictors + aggregation | PARENT / Z1 | diversity/correlation measurement |
| verifier-gated search | cheap proposal, expensive false adoption, reliable checker | propose -> verify -> admit | EXACT phase calibration + PROGRAMME | real transfer and verifier scaling |
| model-based planning | action consequences predictable enough for reusable latent dynamics; online decisions depend on counterfactual futures | world model + search/control | CONDITIONAL / Z1 | model-error vs planning-value law |
| model-free policy/value learning | repeated control where direct policy/value amortization beats online planning | learned value/policy field | CONDITIONAL / Z1 | crossover against model-based/search |
| diffusion/score generative model | high-dimensional continuous multimodal distribution where iterative local denoising field is tractable | learned score/denoising dynamics | PARENT/EMPIRICAL / Z0-Z1 | GMI-specific derivation still weak |
| autoregressive generative model | sequence joint law naturally factorizes by causal prefix and sequential serving is acceptable | conditional next-step predictor | FORMAL factorization + EMPIRICAL | why this factorization dominates alternatives by ecology |
| evolutionary/QD search | differentiability/credit weak, search landscape deceptive or diversity itself valuable | population variation + selection/diversity archive | PARENT / Z1 | predict descriptors/search operator from ecology |

---

# 6. Theorem ZP-1 — recovery failure identifies a gap

Suppose a known family `F` has a registered ecology cell where:

1. `F` is on the protected burden/capability frontier under matched tuning;
2. `F` is expressible in neutral grammar `G0`;
3. search budget is sufficient to recover calibrated known forms of comparable description complexity;
4. GMI's frozen property prediction excludes the defining property vector of `F`.

Then the failure is a **theory prediction failure**, not merely an implementation failure.

If the property prediction includes `F` but neutral search repeatedly fails while calibrated comparable forms are recovered, the failure is instead a **search/grammar failure**.

This separates theory incompleteness from optimizer weakness.

---

# 7. Theorem ZP-2 — explanation requires counterfactual niche prediction

A theory that only maps a known form `F` to a post-hoc descriptor is not predictive. For explanatory standing it must identify at least one ecology intervention `I` such that before observing the protected outcome it predicts

\[
\Delta \operatorname{FrontierProb}(F\mid I)
\]

with the correct direction, and preferably magnitude/phase boundary.

Therefore every zero-prior derivation requires a matched negative twin.

---

# 8. Highest-priority gaps exposed by the zero-prior table

```text
GZ1 quantitative compressibility -> coefficient-vs-memory prediction
GZ2 optimization reachability/generalization -> neural-family prediction
GZ3 dependency variability/density estimator -> Transformer/sparse attention prediction
GZ4 heterogeneity/communication estimator -> MoE prediction
GZ5 predictive-target residual estimator -> RAG/adapters prediction
GZ6 state-dimension estimator -> recurrent/SSM prediction
GZ7 exactness/compositionality estimator -> symbolic/program prediction
GZ8 heuristic/information-value estimator -> search/planning prediction
GZ9 generative factorization selector -> autoregressive vs diffusion vs flow/latent models
GZ10 control amortization selector -> model-free vs model-based/planning
```

These are blocking gaps for a claim that GMI could have derived all major known machine-intelligence forms from zero prior.

---

# 9. Required experiment

Run leave-one-family-out derivation tournaments:

```text
freeze ecology generator and metrics
remove one architecture/family from theory calibration
fit only generic GMI response laws on remaining families
predict held-out family's niche/property vector
run neutral search with low-level primitives
compare recovered form to held-out family under remints
```

Do this first for high-information families:

```text
linear regression
kNN memory
Bayesian belief
symbolic constraints
search
CNN
recurrent state
Transformer
MoE
RAG
```

A failure becomes a named theory gap and blocks stronger completeness claims.

---

# 10. Claim ceiling

Current GMI has plausible/formal directional derivations for many known families, but it **cannot yet claim zero-prior derivation completeness**. The table explicitly identifies the missing quantitative laws that must be filled.
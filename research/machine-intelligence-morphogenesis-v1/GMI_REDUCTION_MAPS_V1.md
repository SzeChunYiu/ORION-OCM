# GMI Reduction Maps v1

Status: **consistency obligations / proof sketches**. A general theory should reduce to simpler established theories when its extra structure is disabled.

---

# R1 — fixed-agent reduction

Set

```text
U = identity
Gamma = identity
```

and fix the morphology realization.

Then GMI reduces to a fixed agent interacting with an environment under an external performance/verification measure and resource semantics.

If resource costs are ignored and the ecology is a reward-generating sequential environment, the remaining object is compatible with ordinary sequential decision / UAI-style agent analysis.

**Consistency requirement:** GMI must not force developmental capital into a system that does not learn.

---

# R2 — pure prediction reduction

Let the obligation contain no machine interventions/actions beyond passive observation and prediction, and let verification depend only on predictive distributions.

Then future developmental equivalence reduces to equality of future predictive distributions:

\[
h\sim h'
\iff
P(Y_{future}\mid h)=P(Y_{future}\mid h').
\]

This is the causal-state / predictive-state idea.

**Consistency requirement:** a predictive sufficient state should be sufficient under this restricted obligation; GMI must not require provenance/OCM-specific fields when they cannot affect future protected quantities.

---

# R3 — finite deterministic automaton reduction

Let the morphology be a finite deterministic machine with no stochasticity and a finite registered event alphabet.

GMI future-equivalence becomes ordinary future-trace equivalence. Quotienting by that relation gives the classical minimal deterministic transducer / Myhill-Nerode-style state representation.

Track B already has exact executable fixtures for this reduction.

---

# R4 — MDP/bisimulation reduction

Let:

```text
state be Markov
U = Gamma = identity
resources ignored or included only as immediate costs
verification/value depend only on reward/transition behavior
```

Then approximate future-equivalence becomes an MDP state-abstraction/bisimulation problem.

Ferns-Panangaden-Precup-style bisimulation metrics become parent tools for approximate quotienting.

**GMI extra structure only matters when machine update/development histories themselves are protected future quantities.**

---

# R5 — factored-MDP reduction

Let the minimal/control state be represented by variables

\[
Z=(Z_1,\ldots,Z_n)
\]

with sparse conditional dependency structure and fixed `U/Gamma`.

Then GMI morphology factorization reduces to ordinary factored MDP / DBN structure. The benefit of compact local conditional tables versus a flat global transition table is parent-owned.

**GMI extension:** learning/revision/morphogenesis may change the factorization and must charge acquisition/maintenance/update cost.

---

# R6 — information-bottleneck reduction

Let the problem be a representation map

\[
X\to Z
\]

where utility depends only on retained relevance to `Y`, and the resource coordinate is mutual information / representation rate.

Then minimizing resource for relevant predictive information recovers the Information Bottleneck/rate-distortion orientation.

**GMI extension:** `Z` may participate in sequential action, learning, verification and future morphology updates; resource vectors may include more than information rate.

---

# R7 — bounded-rational decision reduction

Let the machine choose an action distribution `p(a|w)` relative to prior/default `p0(a)`, with utility and KL information-processing cost.

Then a GMI scalarized frontier recovers information-theoretic bounded rationality/free-energy optimization under the corresponding assumptions.

**GMI extension:** build/update/maintenance/plasticity and verifier costs can be additional resource coordinates rather than collapsed into one information cost.

---

# R8 — Bayesian learner reduction

Let morphology structure `F` be fixed and `Theta_t` be a posterior.

Set

\[
U(\Theta_t,e_t)\propto P(e_t\mid \theta)\Theta_t(\theta).
\]

Then within-form development is ordinary Bayesian conditioning. If action selection is expected utility under the posterior, the system reduces to a Bayesian agent.

**GMI extension:** model-structure change is `Gamma`; future-task meta-priors and learned learning rules live at higher developmental levels.

---

# R9 — gradient learner reduction

Fix neural architecture `F`, set `Theta` to network/optimizer parameters, and set

\[
U(\Theta,e)=\Theta-\eta\widehat\nabla \mathcal L.
\]

Then GMI within-form development reduces to ordinary gradient learning.

`Gamma=identity` gives fixed-architecture training; `Gamma!=identity` admits architecture search/growth/pruning.

---

# R10 — program search / OOPS reduction

Let `F` be a programming language/library, `Theta` a search bias/prior/library state, and `K` a bias-proportional search procedure.

Updating `Theta` by storing/reusing successful code specializes GMI K1 development to incremental program-search bias transformation.

OOPS is therefore a direct parent specialization.

---

# R11 — lifelong/meta-learning reduction

Let tasks `T_i` be sampled from a declared meta-environment and let `Theta` include a representation/prior/learning algorithm shared across tasks.

Then `U` acting across tasks is a lifelong/meta-learner.

Under the relevant assumptions, PAC-Bayes/regret/sample-complexity results apply to future tasks.

**Consistency requirement:** GMI K2 claims must not exceed what these parent bounds justify without additional evidence.

---

# R12 — architecture search / evolution reduction

Let the candidate morphology family itself be the search space and let `Gamma` be mutation/recombination/NAS/program-synthesis updates with a selection/evaluation rule.

Then GMI morphogenesis reduces to ordinary architecture/evolutionary search.

Modularity/facilitated-variation results become special cases where ecology/resource structure changes the architectures found and their evolvability.

---

# R13 — OCM/HST reduction

Use #233 HST state

\[
\Sigma=(L,Q,H,E,R,V,C).
\]

Set GMI morphology fields as one concrete realization of `L/Q/H/R`, while retaining `V,C` as external authority. GMI Verified Developmental Burden reuses HST Verified Search Burden as a principal resource object.

Current OCM program-search experiments are therefore not a separate theory; they are one empirical specialization.

---

# Consistency criterion

If any parent special case requires changing the meaning of:

```text
developmental state
morphology
external verification
resource burden
K0/K1/K2/K3
generality profile
```

rather than merely fixing parameters/turning off unused components, GMI-v1 has failed its generality objective.

Current status:

```text
REDUCTION_MAPS_SPECIFIED__FORMAL_PROOF_DETAIL_INCOMPLETE
```

# GMI Known-Form Derivation Ladder v1

Status: **CONDITIONAL DERIVATION / PARENT-ABSORBING SYNTHESIS**

Refs: `GMI_SEMANTIC_QUOTIENT_REALIZATION_THEOREM_V1.md`, `GMI_CROSS_PARADIGM_REALIZATION_NORMAL_FORM_V1.md`, #233, #377.

## 1. Core point

The general theory does not and should not assert:

```text
semantic quotient -> neural network, uniquely.
```

The semantic quotient specifies the protected developmental distinctions required by a registered cognitive obligation.

A concrete machine-intelligence morphology is obtained only after adding a **realization language** and an **update/morphogenesis law**.

The general pattern is:

\[
\Omega
\to
S_\Omega
\xrightarrow[\text{realization assumptions}]{\mathcal L_M}
\mathfrak M
\xrightarrow[\text{experience}]{U,\Gamma}
\mathfrak M'.
\]

Different extra assumptions yield different known forms.

This is the scientifically defensible interpretation of “a general cognitive substrate can evolve into neural, symbolic, probabilistic or other machine intelligence.”

---

# 2. Base GMI requirements before morphology choice

The common base supplies only:

```text
registered obligation Omega
semantic developmental quotient S_Omega or an approximation contract
realization state Z
semantic interpretation kappa : Z -> S_Omega
proposal/execution kernel Q
within-form update U
structural change Gamma
resource semantics rho
external verifier/constitution V,C
```

No coordinate above says `neuron`, `production`, `posterior`, `program` or `skill`.

Therefore any such form needs additional realization assumptions.

---

# 3. Neural/differentiable derivation

Add the following structure.

## N1 — continuous parametric carrier

Choose a parameter/state space such as

\[
\Theta\subseteq\mathbb R^p
\]

or tensor-valued generalization.

This is a realization choice, not demanded by GMI semantics.

## N2 — compositional differentiable transformations

Choose parameterized maps such as

\[
h_{l+1}=\sigma_l(W_lh_l+b_l).
\]

Composition produces a network/function

\[
f_\theta.
\]

A graph of such parameterized transformations is a neural/differentiable morphology.

## N3 — trainable objective / feedback bridge

Define a loss or differentiable surrogate

\[
\mathcal L(\theta;e)
\]

whose relation to the external obligation/verifier is explicit.

Training loss does not become truth or external verification merely because it is differentiable.

## N4 — gradient-style update

Choose

\[
U(\theta,e)
=
\theta-\eta\widehat\nabla_\theta \mathcal L(\theta;e)
\]

or Adam/learned-optimizer/other declared update.

Backpropagation computes compositional derivatives for the chosen network structure.

At this point the GMI normal form has specialized to an ordinary trainable neural system.

### Parent ownership

Backpropagation, gradient descent, neural architectures and their categorical/compositional formulations are parent mathematics/engineering.

`Backprop as Functor` explicitly constructs a compositional category of learners and shows gradient descent/backpropagation fits it.

### Morphogenetic discovery

If `Gamma` searches over primitive mathematical operations, state/registers and update programs, neural/backprop-like algorithms can be **discovered**, not merely hand-instantiated.

AutoML-Zero is a direct parent example: evolutionary search over basic mathematical operations rediscovered two-layer neural networks trained by backpropagation and other recognizable ML techniques.

NEAT is a parent for evolving neural topology/complexification from minimal networks.

Therefore GMI cannot claim novelty for “simple primitives can evolve a neural network.”

The open GMI question is whether the theory predicts *when that form should occupy the developmental/lifetime frontier*.

---

# 4. Symbolic / production derivation

Instead add:

## S1 — discrete typed carrier

Use symbolic objects/relations/working state.

## S2 — guarded transformations

Represent transformations as productions/rewrite rules

\[
condition(z)\Rightarrow action(z).
\]

## S3 — agenda / matching / search kernel

`Q` performs exact matching, candidate generation, conflict resolution or symbolic search.

## S4 — symbolic learning/update

`U` may add/revise productions, chunks, dependencies, utilities or explicit schemas.

`Gamma` may expand vocabulary/operator/state representation or reorganize modules.

Now the same GMI normal form instantiates a production/symbolic cognitive architecture.

Parents include Soar, ACT-R, production systems, term rewriting, TMS/ATMS, rule induction and program transformation.

---

# 5. Bayesian / probabilistic derivation

Instead add:

## B1 — probabilistic carrier

Use a probability distribution/belief state

\[
P_t(z,\theta).
\]

## B2 — generative/likelihood model

Specify

\[
P(e\mid z,\theta).
\]

## B3 — probabilistic execution/decision

`Q` uses posterior prediction, sampling, expected utility, message passing or inference.

## B4 — conditioning/update

For exact Bayes,

\[
P_{t+1}(z,\theta)
\propto
P(e_t\mid z,\theta)P_t(z,\theta).
\]

Approximate inference is another realization with its own distortion/resources.

`Gamma` may change graphical/model/program structure.

This produces a probabilistic machine-intelligence morphology.

Parents include Bayesian filtering/decision theory, probabilistic graphical models, probabilistic programming, predictive-state representations and active inference where the mapping is faithful.

---

# 6. Programmatic / synthesis derivation

Instead add:

## P1 — executable grammar/language

Choose a typed program grammar

\[
\mathcal G.
\]

## P2 — interpreter/executor

Programs induce transformations/actions under `Q`.

## P3 — synthesis/search distribution

`Q` may enumerate, sample or heuristically propose programs.

## P4 — library/grammar update

`U` changes program priors, libraries or reusable abstractions.

`Gamma` changes the grammar/operator language itself.

This yields programmatic/library-learning morphology.

Parents include universal/program search, OOPS/PowerPlay, CEGIS, DreamCoder, Stitch and other synthesis/library-learning systems.

DreamCoder itself is already hybrid: symbolic program/library induction plus a neural recognition/search policy.

---

# 7. Associative memory / skill morphology

Add a persistent addressable store and retrieval/serving rule:

```text
Z      = episodes / embeddings / prototypes / skill records / indexes
Q      = retrieve / rank / serve / compose
U      = insert / summarize / consolidate / update applicability
Gamma  = reorganize index/schema/memory hierarchy
```

This generates retrieval/case/skill-centered intelligence.

Parents include associative memory, case-based reasoning, RAG, skill libraries and continual skill agents.

---

# 8. Hybrid derivation

A hybrid morphology composes realizations through declared interfaces.

Examples:

```text
neural proposal + symbolic verifier
neural retrieval + program synthesis
Bayesian world model + planner
LLM proposal + Lean kernel
OCM explicit field/control + external neural/CAS/prover donors
```

A hybrid is not scientifically new merely because multiple known modules are connected.

Its developmental/resource coupling must yield a residual beyond the parent product.

---

# 9. General generation relation

Let

\[
\mathcal L_{morph}
\]

be a registered morphology construction language containing some set of state carriers, transformations, compositions and update rules.

Let

\[
\Gamma
\]

be a bounded proposal/search/development process over this language.

Then a form `M` is **generable at scope** if

\[
P_\Gamma(M\text{ or an equivalent realization within budget }B)>0.
\]

This is not the same as saying it is likely, economical or selected.

Three levels remain distinct:

```text
EXPRESSIBLE       M exists in the morphology language
DISCOVERABLE      Gamma can reach M under the registered budget
FRONTIER-USEFUL   M is semantically admissible and competitive on the lifetime frontier
```

A universal-computation proof establishes, at best, a weak version of `EXPRESSIBLE`.

---

# 10. GMI-KD1 — morphology-language dependence

The general semantic quotient alone cannot determine a neural, symbolic, Bayesian or programmatic realization.

Specific morphology derivation requires additional structure in `L_morph` and/or `Gamma`.

Therefore:

```text
SEMANTIC_SUFFICIENCY
!=
REALIZATION UNIQUENESS.
```

This is a foundational limit on the original “one atom inevitably grows into the neural network” picture.

---

# 11. GMI-KD2 — discovery is not inevitability

Even if a morphology is expressible and useful, a bounded `Gamma` may fail to discover it.

Thus:

```text
frontier morphology exists
!=
development/evolution will find it.
```

AutoML-Zero/NEAT demonstrate positive cases under particular search languages and ecologies, not a universal morphogenesis theorem.

---

# 12. GMI-KD3 — different ecologies may select different forms

A morphology phase claim requires a registered candidate class and complete resource accounting.

The target is conditional:

\[
\mathcal F(\Omega,\mathcal M_{avail},\rho,\pi)
\]

rather than a universal architecture ranking.

Candidate pressures include:

```text
semantic/predictive complexity
dependency locality
credit-information structure
noise/uncertainty
drift/invalidation
verification structure
reuse horizon
retention/plasticity
physical resource prices
```

These are encoded provisionally by `Xi(Omega)` and realization response functions.

---

# 13. What “derive a neural network from GMI” may legitimately mean

There are four claim levels.

## D0 — embedding

Show an existing neural learner fits the GMI normal form.

Already established at formal-mapping scope.

## D1 — constructive derivation

Starting from declared parametric/differentiable primitives, construct a neural network and gradient update as a valid realization.

This is parent mathematics.

## D2 — blind rediscovery

A morphology search whose objective does not say “build a neural network” independently finds a neural/backprop-like solution.

AutoML-Zero/NEAT-type parents already establish important examples.

## D3 — prospective phase prediction

Before search, GMI predicts an obligation/resource regime where neural-like realization properties should occupy the frontier; blind search recovers them there and a different form in another predicted regime.

**D3 is the strongest Track-B target.**

---

# 14. Unknown forms

Once the theory can prospectively predict known morphology regimes, a frontier hole can motivate search for a form outside the known families.

A candidate is scientifically new only after reduction against:

```text
neural/differentiable
symbolic/production
probabilistic
dynamical/reservoir
vector-symbolic
programmatic/library-learning
memory/retrieval
evolutionary/population
known hybrid products
```

at matched semantic obligation and developmental/lifetime resources.

---

# 15. Current answer

The current GMI synthesis supports the following statement:

> Known forms of machine intelligence can be generated as different specializations of a common semantic-realization-development framework once family-specific carrier, transformation and update assumptions are supplied. Existing AutoML/neuroevolution results show that at least some such forms, including neural/backpropagation algorithms, can be rediscovered from lower-level search languages. What remains open is a prospective general law predicting which realization properties should emerge under which cognitive obligations, resources and developmental ecologies.

Terminal:

```text
KNOWN_FORM_CONDITIONAL_DERIVATION_SPECIFIED_V1
NEURAL_FORM_NOT_UNIQUELY_IMPLIED_BY_GMI
PROSPECTIVE_MORPHOLOGY_PHASE_LAW_REMAINS_OPEN
```

# GMI Structural Domains and Kingdoms v1

Status: **FOUNDATIONAL TAXONOMY / PROSPECTIVE CLASSIFICATION — NOT A NOVELTY CLAIM**

Status date: 2026-09-12.

Purpose:

> Classify machine intelligence at a much deeper structural level than architecture variants or ecological phenotypes. The analogy is biological domains/kingdoms: neural networks, regression, symbolic systems, search systems, memory systems, probabilistic systems and collectives should be placed by the primitive substrate in which sufficient cognitive state is represented and transformed.

The F1–F18 atlas describes prospective ecological/developmental forms. This file instead asks: **what fundamentally different kinds of computational organism can intelligence be made from?**

---

# 1. Taxonomic levels

Use five levels:

```text
DOMAIN   where sufficient cognitive state fundamentally lives and how it is transformed
KINGDOM  major structural realization family within a domain
PHYLUM   topology/computation pattern within a kingdom
CLASS    concrete architecture/algorithm family
SPECIES  exact or scope-relative developmental/behavioral equivalence class
```

Examples:

```text
DOMAIN: coefficient/field machines
KINGDOM: distributed nonlinear parametric maps
PHYLUM: layered directed differentiable graphs
CLASS: Transformer / CNN / MLP / RNN
SPECIES: a registered developmental-equivalence class within an ecology
```

Thus `Transformer` is not a domain. `Neural network` is approximately kingdom-level. `Attention` is lower still: a mechanism/phylum-level feature.

Likewise `regression` is not maximally separate from neural networks: ordinary regression and neural networks both live in the broad coefficient/parametric domain, although they are structurally distinct kingdoms.

---

# 2. Domain criterion

Let a realization be

\[
M=(Z,K,U,\Gamma,\kappa,\rho).
\]

Two families belong to different structural domains when their ordinary sufficient-state representation and execution law are fundamentally different in the following sense:

1. their cognitive state is stored in different primitive mathematical objects;
2. their basic execution step uses a different primitive transformation law;
3. translating one family into the other generically requires a nontrivial compiler/expansion rather than a mere parameter remint;
4. there exist registered obligation families where that translation induces qualitatively different asymptotic or lifecycle burden.

This is stronger than saying the source code looks different.

---

# 3. Proposed structural domains

## D1 — Coefficient / Function-Field Machines

Cognition lives primarily in a finite set of fitted coefficients/parameters defining a map or dynamical operator.

Generic form:

\[
y=f_\theta(x),
\qquad
\theta' = U(\theta,D).
\]

Kingdoms:

### K1.1 Linear / generalized regression machines

Examples:

```text
linear regression
logistic regression
GLMs
linear discriminants
linear dynamical models
```

Structural idea: intelligence is encoded in a small explicit coefficient tensor acting through a fixed low-order functional form.

### K1.2 Basis-expansion / spline / kernelized finite-map machines

Examples:

```text
polynomial regression
splines
RBF systems
explicit feature maps
finite kernel expansions
```

Structural idea: cognition lives in weighted basis functions.

### K1.3 Neural / distributed nonlinear parametric machines

Examples:

```text
MLP
CNN
RNN/LSTM
Transformer
state-space neural models
MoE neural systems
```

Structural idea: cognition is distributed across many interacting learned coefficients in a compositional nonlinear graph.

Neural networks are therefore one **kingdom**, not the entire domain of machine intelligence.

### K1.4 Tree / partition parametric machines

Examples:

```text
decision trees
random forests
gradient-boosted trees
oblique trees
```

State is a learned hierarchical partition rather than a dense field of coefficients.

This kingdom sits near the boundary between coefficient machines and symbolic branching machines; taxonomy should be decided by whether learned threshold partitions or explicit symbolic rules dominate the registered semantics.

---

# 4. D2 — Exemplar / Memory-Indexed Machines

Cognition lives primarily in stored cases, records, exemplars or associative traces rather than compressed coefficients.

Generic execution:

\[
y = A(x,\mathcal M),
\]

where `M` is an explicit memory population.

Kingdoms:

### K2.1 Nearest-neighbor / case-based intelligence

Examples:

```text
kNN
case-based reasoning
prototype systems
vector retrieval
```

### K2.2 Associative-memory intelligence

Examples:

```text
content-addressable memory
Hopfield-like memories
sparse distributed memory
```

### K2.3 Retrieval/database intelligence

Examples:

```text
structured databases
knowledge stores
RAG-like retrieval substrate
versioned factual memory
```

Deep distinction from D1:

> adding a new fact can consist of adding a new state element rather than altering a global fitted parameter field.

---

# 5. D3 — Probabilistic Belief Machines

Cognition lives primarily in an explicit probability law, posterior, stochastic latent state or uncertainty-bearing graphical structure.

Generic state:

\[
Z=P(H,\Theta\mid E).
\]

Execution means inference, marginalization, conditioning, sampling or decision under belief.

Kingdoms:

### K3.1 Graphical-model machines

Examples:

```text
Bayesian networks
Markov random fields
HMMs
Kalman/state-space probabilistic models
```

### K3.2 Process/posterior machines

Examples:

```text
Gaussian processes
Bayesian nonparametrics
particle populations
```

### K3.3 Probabilistic-program machines

State includes both program structure and distributions over latent execution histories.

The structural primitive is not simply a point estimate but a normalized or otherwise explicit uncertainty state.

---

# 6. D4 — Symbolic Rule / Program Machines

Cognition lives in discrete rules, expressions, programs, equations, logical facts or rewrite systems whose semantics are defined compositionally.

Generic execution:

\[
(program,state,input) \to (program,state',output).
\]

Kingdoms:

### K4.1 Rule-system intelligence

```text
production systems
expert systems
rewrite systems
logic rules
```

### K4.2 Program intelligence

```text
learned/generated programs
inductive programming
program synthesis artifacts
algorithmic controllers
```

### K4.3 Proof/theorem intelligence

```text
proof search
proof-term construction
formal theorem provers
proof-carrying transformations
```

### K4.4 Constraint intelligence

```text
SAT
SMT
constraint programming
integer programming models
```

The defining feature is that semantic state is represented in discrete manipulable symbols with externally interpretable execution rules, rather than only distributed numeric parameters.

---

# 7. D5 — Search / Deliberative Frontier Machines

Here the main cognitive state is not just a learned model. It is an evolving **frontier of candidate futures/solutions**.

Generic state:

\[
Z_t=(\mathcal F_t,\mathcal C_t,\mathcal V_t),
\]

where `F` is a frontier/open set, `C` candidate histories and `V` scores/verifier state.

Kingdoms:

### K5.1 Graph/tree search intelligence

```text
A*
beam search
branch-and-bound
MCTS
minimax
```

### K5.2 Planning intelligence

```text
classical planners
POMDP planners
trajectory optimization
model-predictive control search
```

### K5.3 Evolutionary/population search intelligence

```text
genetic algorithms
evolution strategies
quality-diversity search
open-ended evolutionary systems
```

### K5.4 Program/proof search intelligence

The generated artifacts may belong to D4, while the *search process itself* belongs to D5.

This distinction is important: a theorem prover can contain a symbolic kingdom and a search kingdom simultaneously.

---

# 8. D6 — Dynamical-State / Controller Machines

Cognition lives in a continuously or discretely evolving internal state whose evolution is itself the computation.

Generic form:

\[
z_{t+1}=F(z_t,x_t),\qquad y_t=G(z_t).
\]

Kingdoms:

### K6.1 Finite-state machines

### K6.2 Control/state-space machines

```text
linear controllers
state observers
hybrid dynamical controllers
```

### K6.3 Recurrent computational machines

RNNs can be represented in D1 structurally by parameters, but operationally they instantiate D6 execution semantics. This is a legitimate cross-domain organism.

### K6.4 Reservoir / attractor machines

Cognition emerges from state trajectories or attractor geometry.

D6 deserves domain status because the sufficient state is fundamentally temporal: deleting the current dynamic state destroys cognition even if all fixed parameters remain.

---

# 9. D7 — Collective / Distributed Population Machines

The sufficient cognitive state does not exist in any single component.

Generic form:

\[
S_O=g(Z_1,\ldots,Z_n,M_{1:n}),
\]

with communication/interaction `M` essential.

Kingdoms:

### K7.1 Multi-agent deliberative systems

### K7.2 Swarm/collective systems

### K7.3 Market/auction/contract systems

### K7.4 Federated/distributed inference systems

A collective can contain agents from any other domain. What makes D7 fundamental is that the **population relation itself is necessary cognitive state**.

---

# 10. D8 — Morphogenetic / Self-Rewriting Machines

This is the most important candidate domain beyond ordinary ML.

Here the architecture/representation family is itself mutable cognitive state.

Generic form:

\[
M_{t+1}=\Gamma(M_t,E_t),
\]

where `Gamma` may modify topology, module type, representation basis, algorithm, precision, memory placement or substrate.

Kingdoms:

### K8.1 Growth/pruning machines

Topology expands/contracts while computational basis stays similar.

### K8.2 Architecture-switching machines

A factor can switch between neural, symbolic, probabilistic, retrieval or program realizations.

### K8.3 Self-compiling machines

A rich developmental state generates task/substrate-specific serving organisms.

### K8.4 Self-modeling morphogenetic machines

The machine learns a response law for changing itself and uses that model to choose future structural mutations.

This is potentially analogous to a genuinely different biological domain because `Gamma`, not merely `U`, is constitutive of intelligence.

---

# 11. D9 — Hybrid / Symbiotic Machines

A hybrid is not merely a bag of components. It becomes a structural domain candidate when no constituent domain alone contains the sufficient cognitive state and typed cross-domain interfaces are essential.

Examples:

```text
neural + theorem prover + versioned database
probabilistic world model + intervention engine
retrieval + symbolic verifier + neural compiler
neural perception + search planner + exact controller
```

Kingdoms should be classified by their coupling law:

```text
pipeline symbiosis
shared-state symbiosis
verifier-gated symbiosis
residual symbiosis
competitive portfolio symbiosis
morphogenetic symbiosis
```

Whether D9 deserves independent domain status or is analogous to biological symbiosis across domains is an open taxonomic question. Do not force exclusivity prematurely.

---

# 12. A compact biological-style tree

```text
MACHINE INTELLIGENCE
|
|-- D1 Coefficient / Function-Field
|   |-- Regression/GLM
|   |-- Basis/kernel expansion
|   |-- Neural networks
|   `-- Trees/partition learners
|
|-- D2 Exemplar / Memory-Indexed
|   |-- kNN/case-based
|   |-- associative memory
|   `-- retrieval/database cognition
|
|-- D3 Probabilistic Belief
|   |-- graphical models
|   |-- stochastic processes/posteriors
|   `-- probabilistic programs
|
|-- D4 Symbolic Rule / Program
|   |-- rules/logic
|   |-- programs
|   |-- theorem/proof systems
|   `-- constraint systems
|
|-- D5 Search / Deliberative Frontier
|   |-- tree/graph search
|   |-- planning
|   |-- evolutionary/population search
|   `-- synthesis/proof search
|
|-- D6 Dynamical-State / Controller
|   |-- finite-state
|   |-- control/state-space
|   |-- recurrent dynamics
|   `-- attractor/reservoir
|
|-- D7 Collective / Distributed Population
|   |-- multi-agent
|   |-- swarm
|   |-- market/contract
|   `-- federated/distributed
|
|-- D8 Morphogenetic / Self-Rewriting
|   |-- growth/pruning
|   |-- architecture switching
|   |-- self-compiling
|   `-- self-modeling morphogenesis
|
`-- D9 Hybrid / Symbiotic
    |-- pipeline
    |-- shared-state
    |-- verifier-gated
    |-- residual
    |-- portfolio
    `-- morphogenetic symbiosis
```

---

# 13. Important correction: regression vs neural network

If the desired comparison is:

```text
neural network = one kingdom
regression = another kingdom
what else?
```

then the most natural peer list is:

```text
linear/regression machines
neural-network machines
tree/partition machines
kernel/basis-function machines
instance/exemplar machines
probabilistic-belief machines
symbolic/rule/program machines
search/planning machines
dynamical/controller machines
collective/population machines
morphogenetic/self-rewriting machines
```

These are much closer to “kingdoms” than the F1–F18 list.

The deeper “domains” are the nine state/execution substrates D1–D9 above.

---

# 14. Domain-novelty criterion

A genuinely new domain of machine intelligence should satisfy all of:

```text
1. novel primitive carrier of sufficient cognitive state;
2. novel primitive execution/update law;
3. no bounded semantics-preserving reduction to existing domains over the registered family,
   where the registered family declares (3a) its STRUCTURE-DEPTH BOUND, (3b) the COMPOSITION
   OPERATOR whose image fixes how a parent's store grows with that depth, and (3c) the
   REUSE-HORIZON BOUND over which the frontier is read; and where the parent is PARENT-MAXIMAL;
4. at least one ecology where the new carrier/law changes the achievable resource-capability frontier;
5. neutral biosphere recovery from low-level primitives;
6. recurrence under remint and independent search encodings.
```

This is a substantially stronger claim than a new architecture.

## 14.1 Amendment to criterion 3 (closes gap DG-3; record `RV-377-065`)

Criterion 3 as originally written — "no bounded semantics-preserving reduction to existing domains over the registered
family" — is neither true nor false until the family names three quantities. `GMI_DEPTH_GATED_KINGDOM_V1.md` executed
the decision that forces each of them; the receipt is
`microscopes/results/STAGE_DK_V1_DEPTH_GATED.json`.

**(3a) The structure-depth bound.** GMI-DA3 (`GMI_DOMAIN_ALGEBRA_EXECUTED_V1.md` §4) shows the reduction's reuse
crossover `H*(d) ~ R^d/d` is unbounded in structure depth `d`, so a bounded reduction at every fixed depth need not be
bounded over a family of unbounded depth. Executed at depths 1–6 for the permutation-protected binding code: the
parent-maximal crossover at `R = 4`, `F = 8`, `D = 64` is `54.5, 22.75, 80.875, 303.25, 1167.4375, 4556.35`, with
consecutive ratios rising strictly towards `R = 4`. A family without a declared depth bound therefore has no determinate
answer to criterion 3.

**(3b) The composition operator.** Naming the depth bound is not enough, because how much the parent must store at depth
`d` is a property of the operator's **image**, not of the depth. Executed: the XOR bind that `RV-377-044` used is
commutative and involutive, so its path code has at most `2^R` values and its measured image is `4, 7, 8, 8, 8, 8` at
depths 1–6 — it saturates, the parent-maximal store is bounded by `2^R·F` vectors **uniformly in depth** (≤ 4618 bits at
`D = 64` against the carrier's 864, a constant factor of 5.3449), and criterion 3 fails for the whole unbounded-depth
family at once. Under `PERM` (the same carrier with the PERMUTE primitive of DC1's declared native basis) the image is
exactly `R^d` = `4, 16, 64, 256, 1024, 4096` and the depth escape is real. A criterion-3 claim that does not name the
operator is a claim about an unnamed image.

**(3c) The reuse-horizon bound.** Even with (3a) and (3b) named, "changes the frontier" is read on a grid, and gap DG-2
requires that grid to extend past every crossover reported. An unbounded `H*(d)` means the carrier holds the frontier
over an ever-larger initial segment of reuse horizons — it does **not** mean the parent is excluded. Executed: in 62 of
the 62 frontier decisions with a non-empty admissible set the parent-maximal opponent occupies at least one horizon, and
in 0 of 96 does the carrier occupy while no parent does.

**Parent-maximality.** Protocol rule 19 (gap DG-5) applies to criterion 3 as stated: the reduction must be attempted
against the strongest member of the parent domain, adversarially constructed. `RV-377-065` constructs three opponents
beyond `RV-377-044`'s, and the strongest of them is a factor of about 4 cheaper.

**Re-adjudication of DC1 under the amended text.** With the depth bound declared, the operator named and the reuse
horizon bounded, DC1 remains `REDUCED_TO_PARENT(D2)`: exact developmental equality with all three materializing
opponents in 48 of 48 executed cells, and no cell in which it excludes the parent-maximal opponent from the frontier. At
structure depth 1 the path-materializing opponent is bit-identical to the carrier in description, in serve cost and in
answers, so depth 1 cannot distinguish the two at all.

---

# 15. Research prediction

The strongest possibility raised by GMI is not merely “there are many neural architectures.” It is:

> Present ML occupies only a subset of structural kingdoms, especially coefficient/neural, probabilistic, search, memory and hybrid systems. The largest unexplored region may be machines whose developmental sufficient state is distributed across multiple representation domains and whose morphology itself changes as part of cognition.

The biosphere programme should therefore search not only for new architectures within D1, but for new **state carriers**, **execution laws** and **morphogenetic laws** that could justify entirely new domains.
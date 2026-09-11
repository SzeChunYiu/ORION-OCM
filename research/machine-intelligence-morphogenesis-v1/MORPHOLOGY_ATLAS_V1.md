# Known Machine-Intelligence Morphology Atlas v1

Status: **parent atlas / anti-rediscovery instrument**, not a claim that these labels are fundamental equivalence classes.

Track B originally used four coarse examples—neural, symbolic, probabilistic, programmatic. That list is insufficient for a theory whose eventual goal is to identify genuinely new forms. A candidate can only be called new after reducing it against a broader parent atlas.

The classes below are **historical/functional families**, not ontological atoms. Several may collapse or overlap under developmental equivalence.

---

## M0 — finite-state / automata / dynamical systems

Canonical structure:

```text
state + input -> state' + output
```

Parents:

- finite automata / Moore / Mealy machines;
- universal coalgebra;
- graph/coupled dynamical systems;
- polynomial-functor / dependent-lens open dynamical systems.

Why it matters:

This is the strongest threat to any proposed “basic cognitive unit” defined merely as a stateful transducer.

Track-B disposition: **foundational parent, not a new intelligence form**.

---

## M1 — dense parametric / differentiable neural morphology

Canonical structure:

```text
distributed numeric state/parameters
+ weighted composition
+ nonlinear maps
+ gradient/evolution/local plasticity
```

Includes feedforward, recurrent, Transformer-like, GNN and modular variants at a coarse level.

Parents include universal approximation/computation, backpropagation, meta-learning, meta-RL, learned optimizers and neural scaling laws.

Track-B question: where is this family on the developmental/resource frontier, not whether it is “really intelligent.”

---

## M2 — spiking / neuromorphic morphology

Canonical structure:

```text
event/spike coding
+ stateful neuron/synapse dynamics
+ local/global plasticity
+ event-driven hardware realization
```

Neuromorphic computing explicitly couples algorithmic morphology to physical energy/latency constraints. Spiking systems therefore reinforce the rule that hardware/resource regime `R` can be part of morphology selection.

Do not automatically collapse M2 into standard dense neural morphology when the registered resource behavior is materially different; equally, do not call it a distinct intelligence form merely because the hardware differs.

---

## M3 — reservoir / dynamical-computation morphology

Canonical structure:

```text
fixed or slowly adapted nonlinear dynamical reservoir
+ input perturbation
+ trained/simple readout
```

Parents:

- echo-state networks;
- liquid-state machines;
- physical reservoir computing.

Important distinction: much of the internal dynamics need not be trained task-by-task. Computational value comes from the intrinsic state-space dynamics and a cheap readout.

Track-B implication: “all intelligence must be stored in heavily trained parameters or explicit rules” is an unsafe assumption.

---

## M4 — cellular / locally developmental morphology

Canonical structure:

```text
many local cells/units
+ shared/local transition rule
+ spatial/graph neighborhood
+ repeated developmental dynamics
```

Parents:

- cellular automata;
- neural cellular automata;
- developmental encodings / self-organizing systems.

Growing Neural Cellular Automata are a direct example where learned local rules generate, persist and regenerate global structure.

This is a strong parent for any future claim that “local cognitive units can self-organize into a global machine.”

---

## M5 — vector-symbolic / hyperdimensional morphology

Canonical structure:

```text
high-dimensional distributed vectors
+ algebraic binding/bundling/permutation
+ similarity / superposition computation
```

Parents: HDC / Vector Symbolic Architectures (VSA), including HRR-like and related families.

VSA research explicitly aims to combine properties of structured symbolic manipulation with distributed representations and has close hardware/cognitive-computing connections.

Track-B implication: a discovered distributed-but-algebraically-compositional representation is not automatically a novel neural/symbolic hybrid.

---

## M6 — production / cognitive-architecture morphology

Canonical structure:

```text
explicit working state
+ condition/action productions/operators
+ conflict/selection control
+ explicit memory systems / chunk learning
```

Parents:

- Soar;
- ACT-R;
- blackboard architectures;
- NARS at a broader reasoning-system level.

Soar in particular already hypothesizes deliberate behavior as selecting/applying operators to states and includes working memory, production memory and learning mechanisms.

Track-B implication: state/operator/workspace cycles are parent-owned.

---

## M7 — logic / symbolic / truth-maintenance morphology

Canonical structure:

```text
explicit propositions/terms/relations
+ inference/rewrite
+ dependency/support semantics
+ revision/truth maintenance
```

Parents:

- logic programming / Datalog;
- term rewriting;
- theorem proving;
- TMS/ATMS;
- CEGAR/CEGIS where search/refinement is involved.

Track-B implication: explicit warrant/revision can be a morphology-level advantage without being a fundamental atom.

---

## M8 — probabilistic / generative-program morphology

Canonical structure:

```text
stochastic generative model/program
+ conditioning/inference
+ belief/posterior state
+ probabilistic decision coupling
```

Parents:

- Bayesian networks / graphical models;
- probabilistic programming (Church-class and successors);
- Bayesian Program Learning;
- Markov categories as a general semantics.

Probabilistic structure may be fundamental to a selected representation or a compiled layer; Track B must test bounded equivalence rather than decide by terminology.

---

## M9 — explicit program / synthesis / library morphology

Canonical structure:

```text
executable programs
+ explicit control flow
+ synthesis/search
+ reusable function/macro library
```

Parents:

- inductive programming;
- genetic programming / CGP;
- OOPS / PowerPlay;
- DreamCoder / Stitch;
- CEGIS;
- FunSearch / AlphaEvolve-like evaluator-guided program evolution.

Self-modifying CGP also shows that program morphologies can change their own phenotype/developmental structure.

---

## M10 — evolutionary / population / archive morphology

Canonical structure:

```text
population/archive of variants
+ inherited variation
+ selection/evaluation
+ optional lifetime learning
```

Parents:

- evolutionary computation;
- NEAT/HyperNEAT;
- quality diversity / MAP-Elites;
- novelty search;
- POET-like coupled ecology/solution evolution.

Important ambiguity: this may be a **meta-level search process** generating individual machines rather than the individual machine's cognition. Track B must state the level before calling it a morphology.

---

## M11 — memory-centric / associative morphology

Canonical structure:

```text
large persistent memory
+ content-addressed retrieval / associative update
+ weak or moderate learned transformation
```

Parents include:

- nearest-neighbor/case-based reasoning;
- associative memories / Hopfield-style systems;
- retrieval/RAG systems;
- episodic/semantic memory architectures.

This family matters because apparent “reasoning” gains may be retrieval-dominated; Track B needs mechanism attribution rather than architecture labels.

---

## M12 — multi-paradigm cognitive integration morphology

Canonical structure:

```text
shared/federated state
+ multiple heterogeneous reasoning/learning algorithms
+ metacontrol / coordination
```

Parents:

- OpenCog / Hyperon;
- blackboard systems;
- neuro-symbolic systems;
- LLM + tools/memory/solvers parent products.

Hyperon explicitly aims to combine diverse cognitive algorithms in a shared metagraph/programming framework. Therefore “one system unifies many kinds of cognition” is not Track-B novelty by itself.

---

## M13 — hybrid parent products

A morphology may combine any of the above:

```text
neural + retrieval
neural + probabilistic latent inference
neural + program execution
neural + theorem prover
explicit symbolic + approximate vector retrieval
program + evolutionary search
probabilistic program + neural amortized inference
OCM-like explicit governance + neural/program/tool donors
```

A candidate new morphology must be attacked against the **strongest plausible hybrid**, not only pure textbook parents.

---

# What counts as distinct in Track B?

This atlas is a search/parent inventory, not a partition theorem.

Two entries may be the same Track-B morphology class if they mutually compile under the registered developmental/resource equivalence relation.

Conversely, two implementations traditionally called “neural networks” may belong to different resource/developmental regions if their update laws and physical execution differ enough.

Therefore Track B uses labels only to ensure parent coverage. The eventual scientific object is an equivalence class under:

```text
current behavior
+ developmental/update behavior
+ retention/plasticity
+ resource frontier
+ revision/transfer response
```

not historical naming.

---

# New-form hostile

Before `NEW_MORPHOLOGY_CANDIDATE_AT_SCOPE`, a candidate must be reduced against at least the applicable families M0–M13 and their strongest obvious product combinations.

This makes the eventual unknown-morphology test substantially harder—and therefore more meaningful.

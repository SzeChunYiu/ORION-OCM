# Primitive Threat Analysis v1

Status: **no candidate fundamental basis survives yet**.

The purpose of this file is to attack the four registered basis candidates with the strongest existing formalism that already looks similar. A candidate only survives if a nontrivial developmental/resource residual remains.

---

## B0 — Local adaptive transducers

Candidate idea:

```text
typed local state
+ typed ports
+ transition kernel
+ composition graph
+ adaptation of state/parameters/topology
```

### Strong parent threats

**Universal coalgebra** already provides a broad theory of state-transition and dynamical systems, including behavioral equivalence via bisimulation.

**Polynomial-functor / dependent-lens dynamical systems** provide typed interfaces and composition/wiring of Moore-style state machines.

**Cellular automata / graph dynamical systems / neural cellular automata** already show complex/global computation from local rules.

### Surviving question

The only interesting residual is not local-state compositionality itself. It is whether adding a restricted developmental/update algebra plus resource semantics yields nontrivial predictions about which higher-level learning morphology emerges.

### Kill rule

If `B0` can only say “all candidate machines are state machines/coalgebras,” with no bounded-development or phase prediction beyond the parent formalism:

```text
PARENT_FORMALISM_SUFFICIENT_B0
```

---

## B1 — Compositional learner

Candidate idea:

```text
parameterized maps
+ update/request maps
+ serial/parallel composition
+ resource semantics
```

### Strong parent threats

**Backprop as Functor** already gives a category of learners and compositional gradient-learning structure.

**Categorical Deep Learning** explicitly pursues an algebraic theory spanning many neural architectures.

Related lens/open-system formalisms threaten any claim that feedback interfaces and learning composition are new.

### Surviving question

Can a similarly compositional object naturally represent *non-differentiable* symbolic, probabilistic and programmatic update laws without hiding them in arbitrary black-box morphisms?

### Kill rule

If symbolic/programmatic/probabilistic morphologies enter only as opaque functions with arbitrary updates, B1 has not explained cross-paradigm morphogenesis:

```text
NEURAL_BIASED_PARENT_ALGEBRA_B1
```

---

## B2 — Rewritable typed program graph

Candidate idea:

```text
typed values
+ small instruction/rewrite set
+ mutable store
+ control/composition
+ program/topology rewrite
```

### Strong parent threats

Universal machines, lambda calculus, combinatory logic, genetic programming and program synthesis already make arbitrary computation programmable.

OOPS/PowerPlay already combine programmatic search with incremental reuse/self-improvement.

### Surviving question

Only bounded developmental compilation and morphology-selection predictions can rescue B2 from vacuity.

### Kill rule

If every architecture is “derived” by encoding its interpreter/program directly, return:

```text
UNIVERSAL_COMPUTATION_ONLY_B2
```

---

## B3 — Stochastic generative kernel

Candidate idea:

```text
typed random choice
+ deterministic transforms
+ composition
+ conditioning/scoring
+ inference/update
```

### Strong parent threats

Church/probabilistic programming already gives universal stochastic generative programming.

Markov categories provide a very general compositional semantics for probability/statistics.

AIXI-style mixtures already combine algorithmic environment uncertainty with sequential decision in an idealized universal agent.

### Surviving question

Can stochastic structure be shown to be resource- or learning-irreducible for some morphology regime, rather than simply a convenient semantic layer over deterministic computation plus random bits?

### Kill rule

If the cross-paradigm explanation is only “deterministic systems are degenerate distributions,” return:

```text
PROBABILISTIC_REENCODING_ONLY_B3
```

---

# Boolean minimality warning: Post/clone theory

The Stage-A Boolean calibration recovered NAND/NOR and other complete sets by enumeration. Boolean functional-completeness/minimal-basis classification is mature mathematics (Post/clone theory and Sheffer-function results).

Therefore the Boolean census is only a **calibration** of our compensation-aware machinery.

Before making a novel minimal-basis theorem on finite operation sets, Track B must check whether the problem is already an instance of:

```text
clone theory / universal algebra
transformation semigroup rank/generators
functional completeness classification
```

Do not rediscover Post's lattice under “cognitive primitives.”

---

# What a surviving basis must add

A candidate basis becomes scientifically interesting only if it supports at least one result not supplied by the parent formalism alone:

1. **bounded developmental compilation** across multiple paradigms;
2. **nontrivial resource lower/upper bounds** separating bases/morphologies;
3. **developmental equivalence** stronger than current behavior/bisimulation where update laws matter;
4. **prospective ecology -> morphology frontier prediction**;
5. **blind recovery** of predicted known forms from a neutral grammar;
6. later, **prediction of a missing morphology**.

Until then the basis candidates remain scaffolds, not discoveries.

Current disposition:

```text
B0 OPEN_UNDER_STRONG_COALGEBRA_DYNAMICAL_PARENT
B1 OPEN_BUT_NEURAL_BIAS_THREAT
B2 OPEN_BUT_UNIVERSAL_COMPUTATION_THREAT
B3 OPEN_BUT_PROBABILISTIC_REENCODING_THREAT
NO_FUNDAMENTAL_BASIS_ESTABLISHED
```

# Task-relative minimality v1

Status: **formal correction to the universal cognitive-atom question.**

## Why this matters

Track B's no-go results attack a representation-independent, universally unique cognitive atom. They do **not** imply that meaningful minimal machines never exist.

Classical parent theory shows the opposite under a fixed equivalence criterion:

- Myhill-Nerode yields a unique minimal DFA up to isomorphism for a fixed regular language/behavioral obligation.
- Computational mechanics defines causal states by predictive equivalence; the resulting epsilon-machine is an optimal predictor, minimal among optimal predictors and unique up to equivalence for the process under its assumptions.
- Predictive-state representations similarly build state from sufficient predictions of future observables/actions under a fixed dynamical task.

The lesson is that **minimality becomes well-posed only after the equivalence relation / obligation is fixed**.

## General quotient pattern

Let histories/internal states `h1,h2` be equivalent when no admissible future intervention/observation can distinguish them with respect to a registered cognitive obligation `O`:

\[
h_1 \sim_O h_2
\quad\Longleftrightarrow\quad
\forall a_{future}\in A_O:\;
\mathcal P_O(\cdot\mid h_1,a_{future})
=
\mathcal P_O(\cdot\mid h_2,a_{future}).
\]

Then the quotient

\[
\mathcal H/\!\sim_O
\]

is the natural candidate state representation for that obligation.

Different obligations induce different quotients.

Examples:

```text
language acceptance          -> Nerode classes
optimal next-symbol prediction -> causal/predictive states
control                       -> action-conditional predictive equivalence
proof search                  -> equivalence under future proof obligations
verified developmental cognition -> equivalence under future capability + update + resource trajectories
```

## Track-B consequence

The phrase

```text
fundamental cognitive unit
```

is currently too underspecified.

A scientifically meaningful replacement is:

> **minimal sufficient developmental state/unit relative to a registered family of future cognitive obligations, interventions, verifier semantics and resource tolerances.**

This is not necessarily a physical atom and need not be unique across different obligations.

## Developmental equivalence relation

For Track B, ordinary behavioral equivalence is insufficient. A candidate developmental relation should quantify over future experience/intervention sequences `e_{1:k}` and compare at least:

```text
verified future outputs/capability
future update response
retention/forgetting
resource vector
revision/revocation behavior
proposal/search distribution where relevant
```

Provisional relation:

\[
h_1 \sim_{dev,O,\epsilon,R} h_2
\]

iff every registered future developmental sequence produces trajectories indistinguishable within declared capability/resource tolerances.

The quotient states are then **developmentally sufficient states at the registered scope**.

## Why this moves upward

This reframes Question 1 from:

> What is the one unique atom from which every intelligence is made?

into:

> What is the coarsest state distinction that must be preserved to predict all registered future cognitive/developmental consequences?

That question has clear mathematical parents and clear generalization paths.

## Strong parent warning

Track B receives no novelty credit merely for quotienting by predictive/behavioral equivalence. The parents above already own that strategy.

A surviving residual would require something like:

1. a developmental equivalence relation spanning learning/update/resource trajectories;
2. a finite/exact minimization theorem on restricted adaptive machines;
3. a useful approximate/statistical construction on larger machines;
4. evidence that the quotient predicts cross-paradigm developmental burden or yields new morphology-phase results.

## Candidate theorem programme

### TDM-1 finite developmental Myhill-Nerode analogue

For a finite adaptive transducer class, define two internal configurations equivalent iff every registered finite future input/feedback history yields the same output/update/resource trace.

Then:

- prove the relation is an equivalence relation;
- construct the quotient machine;
- prove trajectory preservation;
- prove minimality among deterministic machines satisfying the same registered trace semantics;
- characterize uniqueness up to isomorphism.

This would be mostly a finite automata-style theorem, not yet a new intelligence result.

### TDM-2 resource-tolerant quotient

Replace exact trace equality by a declared resource/capability tolerance and study whether a canonical minimal quotient still exists; non-uniqueness is allowed.

### TDM-3 developmental-state scaling

Measure how quotient-state count/complexity grows with history horizon, task diversity and update-law richness for known morphology families.

A nontrivial cross-paradigm scaling law here could be more informative than primitive-count minimality.

## Current decision

```text
UNIVERSAL_UNIQUE_COGNITIVE_ATOM_NOT_SUPPORTED
TASK_RELATIVE_MINIMAL_SUFFICIENT_STATE_IS_WELL_POSED
PARENT_MINIMIZATION_THEORY_STRONG
DEVELOPMENTAL_QUOTIENT_RESIDUAL_OPEN
```

# Finite adaptive-network flattening theorem v1

Status: **formal elementary result / parent-owned mathematics, used as a Track-B subtraction theorem**.

Refs #377, #233, #373. This result does not claim novelty.

## Statement

Let a machine consist of a finite graph of `n` deterministic local units. Unit `i` has a finite local state set `S_i`. Let `T` be a finite set of legal topology/configuration states. Let `X` be a finite external observation alphabet, `F` a finite feedback/teaching alphabet, and `Y` a finite output alphabet.

Assume one global step is deterministic and is completely specified by:

```text
current local states (s_1,...,s_n)
current topology/configuration t
external input x
optional feedback f
```

and produces:

```text
next local states (s'_1,...,s'_n)
next topology/configuration t'
output y.
```

Then the complete machine is exactly representable as a deterministic finite-state transducer with global state

\[
S = \left(\prod_{i=1}^n S_i\right) \times T,
\]

augmented input alphabet `X × F` (or just `X` when no feedback is supplied), transition

\[
\delta:S\times X\times F\to S,
\]

and output map

\[
\lambda:S\times X\to Y.
\]

Therefore a finite local adaptive network does not define a new algebraic/computational class merely because adaptation is distributed across units or topology.

## Proof

Every legal global configuration is the tuple

\[
q=(s_1,\ldots,s_n,t).
\]

Because each component set is finite and the graph has finitely many units, the product state set `S` is finite.

The registered local transition/update/topology rules are deterministic. Consequently, for every `(q,x,f)` there is exactly one next tuple `q'`. Define that result to be `δ(q,x,f)`.

Likewise the machine's registered externally visible output on `(q,x)` is unique; define it as `λ(q,x)`.

The resulting finite-state transducer reproduces the original machine step by step for every finite input/feedback history by induction on history length. QED.

## Corollary 1 — learning can be ordinary state transition

At finite scope, a distinction such as

```text
inference transition
vs
learning/update transition
```

can be scientifically useful but is not required for expressivity. Feedback may simply be part of the transducer input and the post-learning parameter/topology configuration part of global state.

Thus `has a learning rule` alone cannot establish a fundamentally new computational primitive.

## Corollary 2 — topology change is state change at finite scope

If the set of legal topologies is finite, dynamic topology can be encoded in `T` and therefore in global state. A topology-changing unit is not algebraically irreducible relative to a sufficiently general finite-state parent.

Any residual must concern, for example:

- description/factorization cost;
- locality and communication cost;
- learnability/search bias;
- update cost;
- modularity/revision cost;
- scaling as the number of units/topologies grows.

## Corollary 3 — current Track-B candidate B0 is parent-dominated at finite exact scope

`B0_LOCAL_ADAPTIVE_TRANSDUCERS` is a useful *representation/factorization hypothesis*, but on any frozen finite deterministic instance it is contained by ordinary finite-state / coalgebraic state-transition mathematics.

Required disposition at finite exact scope:

```text
PARENT_FORMALISM_SUFFICIENT_FOR_EXPRESSIVITY
```

Track B may retain B0 only for stronger resource/developmental questions.

## What this theorem does NOT say

It does not say that all representations are equally efficient.

A flattened transition table can be exponentially larger than a factorized local description. For `n` binary local states plus `m` binary topology/configuration bits, a naive flat state space can have `2^(n+m)` states while a local rule description may remain compact.

Therefore factorization can matter enormously for:

```text
storage
sample complexity
search
credit assignment
parallelism
local revision
communication
hardware mapping
```

Those are precisely the scientifically interesting residuals.

It also does not settle:

- unbounded/growing state or topology;
- continuous-state systems;
- stochastic systems;
- resource-bounded compilation;
- morphology phase laws;
- open-ended developmental growth.

These require separate parents and theorems.

## Scientific consequence

This result moves Track B upward:

```text
WRONG target:
  find a local stateful unit and call it the atom of intelligence

STRONGER target:
  identify the smallest adaptive generating basis / factorization whose
  composition and update laws induce distinctive resource-bounded
  developmental behavior, and predict when that factorization is favored.
```

A general machine-intelligence theory therefore cannot earn its claim merely from finite local adaptive dynamics.
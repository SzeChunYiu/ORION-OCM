# Finite flattening limit v1

Status: elementary formal boundary; use to prevent false morphology/fundamental-unit claims.

## Deterministic finite case

Let a registered adaptive machine have finite:

```text
internal state S
observation/input X
feedback/development signal L
action/output Y
```

and deterministic maps:

\[
T:S\times X\times L\to S
\]

\[
O:S\times X\to Y.
\]

Then the complete behavior/update semantics can be encoded exactly by finite lookup tables for `T` and `O`.

Therefore every finite deterministic architecture—neural-like, symbolic, programmatic, OCM-like, or otherwise—is behaviorally/developmentally simulable by a finite transducer table at finite scope.

This is not a statement about efficient representation.

---

## Finite stochastic case

For a finite stochastic machine replace deterministic `T/O` with conditional distributions / Markov kernels, e.g.

\[
K(s',y\mid s,x,l).
\]

A finite table of probabilities specifies the full registered stochastic transition/output law.

Again, this establishes finite semantic representability, not efficient learnability/inference/update.

---

# Consequence 1 — D0 representability is intrinsically weak

If Track B only asks:

> Can basis/architecture A reproduce the input/output/update behavior of architecture B on a finite universe?

then a direct table parent always exists in principle.

So:

```text
FINITE_REPRESENTABILITY != FUNDAMENTAL_MORPHOLOGY
```

---

# Consequence 2 — even D1 exact compilation needs resource structure

A meaningful D1 result must bind:

```text
description size
execution cost
update cost
memory
communication
verification cost
compilation cost
```

Otherwise the lookup-table construction trivializes the claim.

---

# Consequence 3 — morphology identity must live above extensional semantics

Scientifically meaningful morphology differences may remain in:

```text
factorization / modularity
topology
representation geometry
credit assignment
locality
compositional reuse
learnability/sample complexity
searchability
developmental update cost
revision/retention/plasticity
hardware realization
```

Two systems may implement exactly the same finite transition kernel but occupy very different developmental/resource frontiers.

---

# Consequence 4 — the “fundamental unit” is unlikely to be identified by finite truth tables

Finite exact microscopes are still valuable for:

```text
counterexamples
minimality under a frozen grammar
resource lower bounds
composition laws
hostile calibration
```

but they cannot alone establish a metaphysically privileged cognitive atom.

A serious fundamental-basis claim must therefore include at least one nontrivial statement about:

```text
bounded compilation
scaling
learning/search complexity
composition
resource asymptotics
or predictive morphology phase behavior
```

---

## Track-B terminal / constraint

```text
FINITE_SEMANTIC_FLATTENING_LIMIT_ADOPTED
```

This boundary pushes the programme upward rather than narrowing it: the key scientific object is no longer raw representational universality, but the **developmental/resource organization of adaptive computation**.

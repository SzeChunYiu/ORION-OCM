# Stage C-v1 structured adaptive census — interpretation

Status: **exact finite subproblem of the frozen Stage C-v1 protocol; not full protocol closure.**

## Registered subproblem

Two one-bit state cells, one external input bit, one feedback label bit, history depth <= 2, expression depth 1.

Two topology arms:

```text
LOCAL_ONLY   each cell reads self/input/label
CROSS_CELL   each cell may additionally read the other cell state
```

Transform catalogue:

```text
NOT
AND
XOR
```

Constants `0/1` and source reads are available as leaves. Morphology identity is quotient by exact expression semantics before the developmental census.

## Exact findings

### 1. Current behavior is again much coarser than developmental behavior

Every full arm has only four possible current behaviors at the registered all-zero initial state, while full structured developmental reach is much larger.

### 2. Communication topology expands bounded developmental reach

With the full operator catalogue:

```text
LOCAL_ONLY developmental classes = 95
CROSS_CELL developmental classes = 294
```

Thus, under the frozen shallow grammar/history scope:

```text
294 - 95 = 199
```

additional developmental signatures become reachable when cells can consume one another's state.

This is an **exact bounded reach result**, not evidence that multi-unit topology is universally necessary for intelligence. A stronger sequential/program parent may emulate the same behavior with different resource costs.

### 3. Reach irreducibility != resource irreducibility

In the CROSS_CELL arm:

```text
{AND, XOR}        developmental reach = 294
{NOT, AND, XOR}   developmental reach = 294
```

So `NOT` is **not reach-necessary** because the registered constants and XOR can compensate.

But minimum expression costs differ:

```text
mean minimum morphology cost with AND+XOR       = 7.4081632653
mean minimum morphology cost with NOT+AND+XOR   = 6.7721088435
```

Adding a reach-redundant primitive lowers the average minimum compilation cost by about:

```text
0.6360544218 expression nodes
```

This exactly demonstrates why Track B/#145 must distinguish:

```text
ALGEBRAIC / REACH IRREDUCIBILITY
RESOURCE IRREDUCIBILITY / VALUE
```

A smallest-cardinality basis need not be the economically best basis.

### 4. The result is still parent-dominated at the formal level

The system is a finite structured adaptive state machine. Standard state-machine/coalgebra/program formalisms can represent it.

Therefore the allowed scientific conclusion is:

```text
STRUCTURED_ADAPTIVE_CENSUS_EXACT__TOPOLOGY_EXPANDS_BOUNDED_REACH__NOT_RESOURCE_USEFUL_NOT_REACH_NECESSARY
```

not:

```text
FUNDAMENTAL_COGNITIVE_UNIT_FOUND
```

## What part of the frozen Stage C-v1 protocol remains open?

This subproblem does **not** yet execute:

- E0–E6 task/ecology contracts as separate capability obligations;
- A3 topology-changing-after-feedback arm;
- explicit P0/P1/P2/P3 parent resource implementations;
- full description-bit accounting;
- exact revision-locality ecology;
- stochastic arm;
- complete topology-mutation hostiles.

So Stage C-v1 is **PARTIAL**, not closed.

## Upward lesson

The exact result supports a more useful theory question than “which primitive is fundamental?”

At a fixed reachable function/development class, primitive and topology choices trade off:

```text
expressive reach
compilation depth
mutable state
communication
update cost
```

The candidate future phase law should therefore operate over **resource-bounded bases/morphologies**, not over a single minimum-cardinality primitive set.

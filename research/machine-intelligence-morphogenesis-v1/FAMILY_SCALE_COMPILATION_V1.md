# Family-scale bounded compilation v1

Status: **Stage-D theory / parent subtraction.** No foundational novelty is claimed by compilation alone.

Refs #377, #233, #373.

## 1. Why family-scale analysis replaces one-off toy derivations

A finite target can always be flattened into a sufficiently large state machine or table. A universal program can also represent every computable target. Therefore Stage D asks whether a **single frozen low-level basis and uniform compiler** preserve the natural scaling of whole morphology families, including their update law, without architecture-labelled macros.

The resource vector is kept raw:

```text
description / prior information
execution / inference
learning / update
communication
memory
verification
maintenance / revision
compiler construction
acquisition / search
```

## 2. Factorization calibration: exact result

For the family

\[
s_i' = s_i \oplus x_i,\qquad i=1,\ldots,n,
\]

a direct global transition table over `n` state bits and `n` input bits contains

\[
2^n\times 2^n = 4^n
\]

entries.

A factored implementation executes `n` XORs. An ordinary loop/program also executes `n` XORs.

`factorization_scaling_calibration.py` verifies exact transition equality through `n=8` and records the formula through `n=16`.

Terminal:

```text
FACTORIZATION_EXPONENTIAL_VS_FLAT__GENERAL_PROGRAM_PARENT_COMPACT
```

Interpretation:

- factorization can be exponentially more succinct than a flat table;
- this does **not** identify a unique cognitive basis;
- a generic compact program captures the factorization too.

This is standard state-space/factorization mathematics used as a subtraction result.

## 3. Neural / differentiable family

Consider a finite-precision feed-forward computation graph with `T` elementary arithmetic/nonlinear operations and scalar loss.

### Execution

A generic typed arithmetic program/DAG executes the same graph with `O(T)` elementary operations, modulo representation constants.

### Gradient update

Reverse-mode automatic differentiation traverses the computation graph with work proportional to the forward computation up to a small implementation-dependent factor, with the usual memory/checkpoint trade-offs. This is established AD parent machinery, not Track-B novelty.

Therefore a general program/computation-graph basis can preserve the asymptotic execution/update structure of ordinary finite neural training without containing a `NEURON` or `BACKPROP` primitive, provided arithmetic/differentiation support is in the compiler/runtime.

This gives at most:

```text
GENERAL_PROGRAM_PARENT_SUFFICIENT_FOR_NEURAL_EXECUTION_AND_AD_UPDATE_AT_REGISTERED_MODEL
```

not a fundamental-basis result.

Important residuals remain outside this compilation observation:

- optimization/implicit bias;
- sample complexity;
- architecture search;
- representation learning;
- parallel hardware mapping;
- long-horizon plasticity;
- emergence from architecture-neutral search.

## 4. Symbolic / production family

A production system with `n` explicit rules can be represented by an ordinary program/interpreter. A naive matcher may scan rules; mature RETE-style pattern matching compiles repeated pattern structure into a network that shares partial matches.

Hence the relevant parent is not a flat `for rule in rules` interpreter but mature production-system indexing/matching.

A generic program basis can encode both the rules and the matcher, including rule addition/deletion/chunking updates.

Current disposition:

```text
GENERAL_PROGRAM_PARENT_SUFFICIENT_FOR_SYMBOLIC_EXECUTION_REPRESENTATION
PRODUCTION_MATCHING_RESOURCE_STRUCTURE_PARENT_OWNED
```

The scientifically interesting questions concern how a morphology *acquires* useful rules/index structure and when that factorization dominates alternatives.

## 5. Probabilistic / factorized family

A factor graph represents a global function/distribution as products of local factors. Sum-product and variable-elimination/junction-tree families exploit this factorization; exact inference complexity can be exponential in a structural width such as treewidth rather than necessarily in the total variable count.

A generic program can encode factors, messages and elimination algorithms with polynomial representation overhead relative to the factored model. Flattening to a full joint table may be exponential.

Therefore:

```text
GENERAL_PROGRAM_PARENT_SUFFICIENT_FOR_PROBABILISTIC_EXECUTION_REPRESENTATION
FACTOR_GRAPH_PARENT_OWNS_STRUCTURAL_INFERENCE_ADVANTAGE
```

The Track-B residual is not “probability can be represented”. It is whether ecology/feedback/resource variables predict when probabilistic factorization is a better developmental morphology than deterministic/programmatic alternatives.

## 6. Programmatic / library family

This family is already native to a general program representation. Function calls, modules, grammars and libraries preserve repeated structure and avoid inlining blow-up.

Parents include ordinary programming languages/compilers, program synthesis, DreamCoder/Stitch, GP and OOPS/PowerPlay.

Disposition:

```text
GENERAL_PROGRAM_PARENT_IDENTITY_FOR_PROGRAMMATIC_MORPHOLOGY
```

## 7. Cross-paradigm conclusion

A sufficiently capable typed program/computation-graph language can compactly realize representatives of all four headline morphology families.

This is useful because it kills the weak foundational claim:

> a common execution language is the fundamental theory of intelligence.

The common execution basis is largely parent-owned and too permissive.

### Stage-D terminal at the current level

```text
GENERAL_PROGRAM_PARENT_SUFFICIENT_FOR_CROSS_PARADIGM_EXECUTION_COMPILATION
```

with an important caveat: *family-specific algorithms/compilers are part of the prior and must be charged*.

## 8. The residual moves upward again

The unresolved object is not execution-language universality. It is:

```text
architecture-neutral developmental acquisition
+ induced proposal/update geometry
+ sample/search complexity
+ morphology-specific lifecycle resources
+ prospective ecology -> frontier prediction
```

In particular, the theory must explain why one factorization/update law is *reachable and useful* under an ecology rather than merely show that a programmer can encode it.

This motivates `COMPILER_INFORMATION_NO_GO_V1.md` and `STRUCTURE_TO_GEOMETRY_PROGRAMME_V1.md`.

## 9. Parent anchors

Load-bearing parent results used here include:

- reverse-mode automatic differentiation / cheap-gradient literature (Linnainmaa; Griewank/Walther);
- Forgy's RETE pattern matcher for production systems;
- Kschischang, Frey & Loeliger factor graphs / sum-product;
- Darwiche variable-elimination/jointree/recursive-conditioning complexity and time-space tradeoffs;
- ordinary compiler/program representations and modularity.

These are parents to reconstruct more deeply before manuscript-level claims.

## 10. What would be stronger than this result?

A meaningful positive would require a *uniform* low-information compiler/development law from a shared basis whose family-scale overhead is bounded across several paradigms **and** whose search/acquisition process does not receive the architecture-specific decomposition by hand.

Even then, the decisive Track-B result remains D3: prospective morphology-frontier prediction and blind recovery.
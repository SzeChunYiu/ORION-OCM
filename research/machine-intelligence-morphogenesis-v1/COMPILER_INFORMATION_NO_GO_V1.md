# Target-specific compiler information no-go v1

Status: **methodological theorem/constraint; parent-owned computability idea, Track-B-specific consequence.**

Refs #377, #233, #373.

## Claim attacked

A weak Stage-D argument would be:

> One common basis `B` can compile a neural system, a symbolic system, a probabilistic system and a programmatic system, therefore `B` is a fundamental cognitive substrate.

This is not sufficient.

## Vacuity construction

Let `B` be any universal-enough execution language. For each computable target morphology `M`, permit a separately hand-authored compiler

\[
\kappa_M : M \to B.
\]

If the description/construction cost of `kappa_M` is uncharged, the compiler can contain essentially all architecture-specific knowledge required to realize `M`.

Then

```text
forall computable M, exists target-specific kappa_M
```

is mostly a consequence of universality plus human engineering. It does not show that `B` naturally generates `M`, that `M` is cheap to acquire from experience, or that the ecology favors `M`.

## Required correction

Every Track-B derivation must charge at least:

```text
L(kappa)          compiler description / prior information
C_build(kappa)    compiler construction or synthesis cost
C_compile         compilation cost
R_runtime         execution resources after compilation
R_update          learning/update resources after compilation
R_maint           maintenance / revision cost
```

A target-specific compiler that scales with the target morphology description is not evidence for a compact generative law.

## Uniform-compiler target

The stronger D1 target is a **uniform compiler**

\[
\kappa : \operatorname{Desc}(M) \to B
\]

whose own description is frozen before the target family and whose overhead is bounded across the whole registered family.

Even this only establishes bounded compilation. It does not establish developmental acquisition or morphogenesis.

## Architecture-neutral acquisition target

D2/D3 require more:

```text
shared low-level basis
+ target-independent search/update machinery
+ ecology / feedback
-> architecture-specific organization acquired without architecture labels
```

The search prior, grammar and mutation/update operators are themselves prior information and must be charged.

## Generative burden

For a target morphology `M`, define provisionally

\[
G_B(M)=L(\kappa)+C_{build}(\kappa)+C_{compile}+C_{acquire/search}.
\]

This is not a universal intelligence scalar. It is a guard against laundering target architecture knowledge through a compiler.

A common basis is scientifically stronger when a **single small compiler/search law** covers a broad family of morphologies with bounded developmental/resource overhead.

## Consequence for Track B

The following is forbidden as a foundational result:

```text
COMMON_BASIS_SUPPORTED
because four separately hand-written compilers produced four known architectures
```

Allowed dispositions include:

```text
GENERAL_PROGRAM_PARENT_SUFFICIENT_FOR_REPRESENTATION
TARGET_SPECIFIC_COMPILER_DOMINATES
UNIFORM_BOUNDED_COMPILATION_SUPPORTED_AT_SCOPE
DEVELOPMENTAL_ACQUISITION_NOT_ESTABLISHED
```

## Ultimate implication

The difficult question is not whether known intelligence forms are computable in the same language. They are.

The difficult question is whether a compact, architecture-neutral developmental law induces their useful factorizations and predicts their resource/ecology regimes without receiving those factorizations through the compiler.
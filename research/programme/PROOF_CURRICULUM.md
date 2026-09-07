# A broad proof curriculum for mechanical OCM learning

[Programme](CORE.md) · [Transfer into language](MATH_TO_LANGUAGE.md) · [Current fixed entry](../proof-corpus-coverage-v1/README.md)

Direction updated, 7 September 2026: FLT is one demanding example in a diverse mathematical
curriculum. Full FLT success is not a prerequisite for useful learning or language transfer.
The existing four-row FLT assignment remains fixed; this broadens subsequent experiments.
This document selects candidate sources and experiments. It records no new corpus ingestion.

## Where to obtain useful experience

Many public formalizations are human-written proofs checked by a computer. They are excellent
examples to learn from, but their existence does not demonstrate autonomous theorem discovery.
Retain proof terms, scripts and actual search traces separately: they expose different information.

| Source | Useful material | Engineering order and boundary |
|---|---|---|
| [Lean/mathlib](https://github.com/leanprover-community/mathlib4) | Broad formal mathematics; source tactics and elaborated proof expressions | First: reuse the existing Lean route. Pin library, toolchain, dependencies and exporter together. Repository licence: Apache-2.0. |
| [Metamath](https://github.com/metamath/set.mm) | Explicit substitution proofs; compressed proofs can be expanded into inference steps | Next independent representation. Keep classical `set.mm` and intuitionistic `iset.mm` foundations distinct; preserve distinct-variable restrictions. Database CC0; verifier licences are separate. |
| [Mathematical Components](https://math-comp.github.io/) | Rocq/SSReflect proofs, algebraic hierarchies and small-scale reflection | Later portability test. Pin Rocq, library and plugins; core licence CeCILL-B. Interfaces and admitted obligations are not completed proofs. |
| [Isabelle Archive of Formal Proofs](https://isa-afp.org/about/) | Structured developments, locales, induction, sessions and imports | Later breadth test. Entry licences differ. Full proof export requires an explicitly qualified recording/export route, including parent sessions. |
| [HOL Light/Flyspeck](https://github.com/flyspeck/flyspeck) | A major formal mathematical development beyond FLT, with executable proof scripts | Later scale/foundation test. Flyspeck is MIT; HOL Light has BSD-style licensing with file exceptions. [OpenTheory](https://www.gilith.com/opentheory/) is a possible transport mechanism, not evidence that every Flyspeck proof is already exported. |

This is a source catalogue, not a claim that the current OCM adapter supports every ecosystem.
Detailed primary-source and checker notes are in the [independent review](proof-curriculum-source-review.txt).
Start with diverse Lean subject families; add other formats after the learning loop works.
Five simultaneous prover integrations would spend effort before answering the main hypothesis.

## What OCM should learn from a proof

1. **Facts and relations:** the checked statement, definitions, assumptions and dependencies.
2. **Executable methods:** reusable subproof compositions, specializations and proof-producing rules.
3. **Representations:** which transformations make a task cheaper, with checked correspondence.
4. **Selection knowledge:** which methods apply, their observed costs and when they fail.
5. **Obstructions and repairs:** the actual failed search state and the intervention that helped.

A final proof rarely records its author's unsuccessful searches. Original discovery cost is
unknown unless recorded; OCM's own replay, search, acquisition and rejection costs are measurable.
Do not reconstruct imaginary experience from a polished proof or count imported theorems as
OCM discoveries. Preserve upstream authorship/provenance and separate supplied scaffolding,
exposed reference material and structures actually acquired by the non-neural machine.
The existing AI-authored FLT material remains disclosed reference input, not evidence that
OCM discovered those proofs. A stronger claim about non-neural teaching provenance needs a
separately qualified teaching partition; unknown authorship remains unknown.

Mechanically generalize repeated, typed proof fragments, check the resulting rule, normalize
against the existing library, and retain it only when it improves future workload performance.
A method can be useful in one context and harmful in another. Learn explicit applicability
and selection rules; there is no reason to expect one universally best method.

## Admission and withholding

Each admitted item keeps a native foundation/checker/version identity, typed statement,
dependencies, proof reference, licence/provenance metadata and cost records. Kernel acceptance
is interpreted under its actual axioms and checking contract. A common catalogue must not
erase the distinction between classical, constructive and other native foundations.
Names, diagram shape and translated syntax alone never establish cross-system equivalence.

Use three explicit partitions: teaching references, development tasks and untouched evaluation.
Group known aliases, ports and closely related proof/dependency families before splitting.
Prevent leakage through theorem names, downstream lemmas, simplification tables, instances,
compiled artifacts and cached proof expansions. Record the checked search scope; do not claim
that a practical duplicate detector decides all mathematical equivalence.

For held-out reconstruction, register the target and allowed context independently and exclude
the original solution plus forbidden dependencies. Exposed replay is a useful adapter test,
but cannot substitute for reconstruction. Capture failures, exclusions and unreached tasks.
Keep every fixed evaluation assignment unchanged once outcomes are observed.

## Curriculum and stopping decisions

| Stage | Smallest useful result | Proceed when |
|---|---|---|
| Read and check | Replay selected existing proofs under registered target/context | Actual semantic association and checker custody pass |
| Reconstruct | Solve small missing regions using a strong mechanical prover | Allowed-information boundaries are qualified and results include failures |
| Acquire and reuse | Produce explicit methods, persist/restart, use them in fresh search | Disabling acquired methods changes measured solving; added facts alone do not explain it |
| Transfer | Reuse methods on new mathematical families and bounded language tasks | Untouched compositions improve against equally adaptive parents without lost correctness |
| Scale and revise | Grow knowledge and method catalogues; withdraw/change premises | Complete task and maintenance costs are measured, including genuinely global cases |
| Large developments | Progress to difficult projects including FLT | Earlier mechanisms show enough capability and economics to justify the computation |

The first studies should span order/set reasoning, algebraic rewriting and finite structures
within one qualified ecosystem. Choose exact populations and train/development/test splits
before semantic outcomes. Use a separate pilot to choose evaluation sizes and resource
allocations. Include easy, difficult, unsupported and globally dependent cases.

Keep the strong existing solver, indexing, caching and library-learning mechanisms in the
comparison. An equally adaptive parent receives the same teaching episodes and new facts.
Adding storage or a grammar is useful engineering; report `PARENT_SUFFICIENT` when the
conventional system reproduces the improvement. Preserve that result and investigate the
remaining bottleneck, instead of selecting a weaker comparator.

Charge the complete experience-to-use cycle: acquisition, checking, extraction, rejected
candidates, compilation, storage, indexing, search, revision and verification. Separate cold
construction from warm calls. Increasing imported theorem count is not the success metric.
The research target is better or cheaper fresh cognition after sufficient useful experience.

## Next concrete work

Finish the registered Lean semantic-entry boundary, then demonstrate one acquisition/restart/
fresh-use loop on varied mathematical families. Build the [bounded language experiment](MATH_TO_LANGUAGE.md)
around those same persisted method objects. The shared mechanism is the research object;
FLT, other formal developments and language tasks supply progressively stronger tests.
Use laptop billy for qualification and CPU-oriented proof work. GPU allocation should follow
an observed parallel computation need; a proof library by itself does not create one.

One substantive paper about measured, revision-safe learned reuse is the first publication
candidate. Cross-foundation or language transfer becomes a further paper only with its own
substantial result. Neither a broad catalogue nor an impressive named theorem establishes
novelty, frontier capability, lifetime savings or top-tier publication readiness.

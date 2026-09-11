# GMI-D2 Exact Microscope v1

Purpose: calibrate Track-B minimality/equivalence machinery on finite worlds **before** any architecture search or LUNARC campaign.

## Stage A — known-answer Boolean calibration (executed)

Universe:

- all `16` binary Boolean functions on inputs `(x,y)`;
- projections `x,y` are free variables, not counted as primitives;
- primitive catalogue: `NOT, AND, OR, XOR, NAND, NOR`;
- legal construction: functional composition only;
- cost coordinate: minimum expression depth.

Executed result:

```text
54 / 63 subsets are complete at this tiny scope.

Inclusion-minimal complete bases:
  {NAND}       max minimum depth 3
  {NOR}        max minimum depth 3
  {NOT, AND}   max minimum depth 4
  {NOT, OR}    max minimum depth 4
```

This is not new mathematics. Post/clone theory and classical functional-completeness results own the underlying Boolean structure.

Terminal:

`EXACT_BASIS_CENSUS_CALIBRATED_ON_KNOWN_BOOLEAN_SCOPE`

---

## Stage B — developmental-equivalence counterexample (executed)

Two machines are exactly identical on every input in the complete registered universe before experience, but after the same supervised event one updates and one does not.

Terminal:

`CURRENT_BEHAVIOR_EQUIVALENCE_DOES_NOT_IMPLY_DEVELOPMENTAL_EQUIVALENCE_EXACT`

Consequence: Track-B morphology equivalence must preserve registered experience -> update -> later behavior, not merely present I/O.

Artifacts:

```text
developmental_equivalence_witness.py
test_developmental_equivalence_witness.py
EXACT_DEVELOPMENTAL_EQUIVALENCE_V1.json
```

---

## Stage C-v0 — one-bit adaptive Boolean basis census (executed)

A morphology is one-bit state `s`, one-bit input `x`, supervised label `l`, output `f(s,x)` and update `g(s,x,l)`, with `f/g` composed from the six-gate catalogue.

Executed exact result:

```text
basis subsets enumerated                  63
complete basis subsets                    54
full (f,g) morphology universe          4096
current-behavior classes at s=0            4
developmental classes (history <=2)     2884
```

This establishes that developmental identity can be dramatically finer than present behavior, but the basis structure is still ordinary Boolean clone/Post mathematics.

Terminal:

`ADAPTIVE_BOOLEAN_BASIS_CENSUS_EXACT__PARENT_MATHEMATICS_DOMINATES`

Artifacts:

```text
adaptive_boolean_basis_census.py
test_adaptive_boolean_basis_census.py
EXACT_ADAPTIVE_BOOLEAN_CENSUS_V1.json
```

---

## Stage C-v1 — structured local state + topology adaptation (executed)

The next grammar stops using arbitrary Boolean truth tables as the morphology itself. It uses two explicit binary local units, one explicit binary edge, restricted local compute operations, restricted state-update operations, and restricted edge-update modes.

Registered components:

```text
compute ops:
  INPUT
  STATE
  NEIGHBOR
  NOT_INPUT
  XOR_INPUT_STATE
  XOR_INPUT_NEIGHBOR
  AND_INPUT_STATE
  AND_INPUT_NEIGHBOR

state update ops:
  HOLD
  WRITE_LABEL
  WRITE_ERROR
  XOR_ERROR
  COPY_OUTPUT
  COPY_NEIGHBOR

edge modes:
  FIXED_OFF
  FIXED_ON
  TOGGLE_ON_ERROR
  SET_ON_ERROR
```

Registered developmental evaluation:

- two initial local-state seeds: `(0,0)` and `(0,1)`;
- every supervised history of length `0..2` over binary `(input,label)` events (`21` histories);
- after each history, probe both binary inputs;
- developmental phenotype = complete concatenated output vector.

Exact enumeration:

```text
family               morphologies   developmental classes
STATIC                    128                 6
STATE_ADAPTIVE           4608                96
TOPOLOGY_ADAPTIVE         256                12
FULL_ADAPTIVE            9216               184
```

Exact reach differences:

```text
state-adaptive unique beyond static                         90
topology-adaptive unique beyond static                       6
topology-adaptive unique beyond state-adaptive               6
state-adaptive unique beyond topology-adaptive              90
full-adaptive unique beyond union(single-channel families)  82
```

So, **under the frozen tiny architecture/grammar budget**, state adaptation and topology adaptation are not interchangeable, and their interaction produces additional developmental phenotypes.

However, the stronger formal result is subtraction rather than novelty:

### Finite flattening theorem

Any finite deterministic graph of finite local states plus finite topology/configuration state can be flattened exactly into one deterministic finite-state transducer by defining global state

\[
S=(\prod_i S_i)\times T.
\]

Feedback/teaching symbols simply augment the transducer input alphabet. Therefore topology change is algebraically just state change at finite scope.

Terminal:

`STRUCTURED_ADAPTATION_INTERACTION_EXACT__FINITE_STATE_PARENT_SUFFICIENT_FOR_EXPRESSIVITY`

Interpretation:

```text
structured factorization matters at a fixed architecture/resource bound
!=
new fundamental computational class
```

The residual is now explicitly about description length, locality, communication, learnability, update/revision cost and scaling—not finite expressivity.

Artifacts:

```text
FINITE_FLATTENING_THEOREM_V1.md
BASIS_CANDIDATE_DISPOSITION_V2.json
structured_adaptive_grammar_census.py
test_structured_adaptive_grammar_census.py
EXACT_STRUCTURED_ADAPTIVE_CENSUS_V1.json
```

---

## Stage C-v2 — next exact question: resource-bounded factorization

Stage C-v1 kills the weak claim that local adaptive units define a new computational class. The next exact question is stronger:

> Can a structured adaptive factorization represent/develop some registered phenotype with provably or exactly smaller **description / local update / communication / search** burden than every matched flat-state/program parent under the same finite scope?

Required comparison:

```text
structured local grammar
vs
flat finite-state table
vs
compressed/symbolic finite-state parent
vs
small explicit program parent
```

Do not compare only against a deliberately uncompressed transition table.

Required resource coordinates:

```text
description bits / AST size
states actually touched per update
communication edges/messages
update steps
compiler/search work to acquire the morphology
maintenance/revision work
```

Possible terminals:

```text
STRUCTURED_FACTORIZATION_RESOURCE_RESIDUAL_AT_SCOPE
PROGRAM_PARENT_SUFFICIENT
STATE_MACHINE_PARENT_SUFFICIENT
NO_RESOURCE_RESIDUAL
REPRESENTATION_PRICE_REGIME_ONLY
CANNOT_CHECK_<reason>
```

---

## Stage D — known-form micro-derivations

Only after Stage C-v2 has a nontrivial resource question, attempt tiny targets from multiple paradigms using the same frozen basis/grammar family:

1. tiny threshold/neural computation plus one update step;
2. finite production/rewrite learner;
3. tiny stochastic/Bayesian update fixture;
4. tiny explicit program/library learner;
5. one simple hybrid statistical + exact-check fixture.

The same basis must reproduce **behavior + registered update law** without architecture-labelled macros. Record separately:

```text
D0 representability
D1 bounded developmental compilation
D2 developmental acquisition
```

If a morphology requires adding a named architecture-specific primitive, report the obstruction rather than quietly expanding the basis.

---

## Stage E — exact developmental-frontier calibration

After known-form micro-derivations exist, vary at least two ecology coordinates and compute complete finite frontiers.

Candidate axes:

```text
reuse horizon
revision frequency
noise / stochasticity
exact-verification requirement
```

Freeze phase-crossing predictions on development worlds, then test on disjoint tiny worlds.

---

## Adoption/kill rules

- Universal interpreter success alone -> `UNIVERSAL_COMPUTATION_ONLY`.
- Generic finite local adaptive system with no resource residual -> `PARENT_FORMALISM_SUFFICIENT`.
- Boolean functional-completeness/minimal-basis results -> parent mathematics/calibration.
- Structured factorization that only beats an intentionally uncompressed flat table -> non-evidence.
- Different bases equivalent but resource-ranked differently -> preserve Pareto/price-regime result; do not force a metaphysical winner.
- Stochastic fixture needs irreducible stochastic primitive at the registered bound -> report obstruction.
- Basis chosen after target results -> exploratory only; re-freeze.
- Phase regions explained after outcome -> no phase-law credit.

## No-HPC rule

GMI-D2 remains finite/exact and runs on ordinary hardware. #221/#220 search machinery is not authorized until the structured grammar, resource comparison and cross-paradigm micro-derivations survive these microscopes.

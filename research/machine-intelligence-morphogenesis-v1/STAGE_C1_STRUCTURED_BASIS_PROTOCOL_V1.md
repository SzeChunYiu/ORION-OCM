# GMI-D2 Stage C-v1 — Structured Adaptive Basis Protocol v1

Status: **DESIGN FREEZE CANDIDATE — execute only after selftest/independent review.**

Purpose: move beyond Stage C-v0, where adaptation was represented by an arbitrary Boolean update function and therefore remained too close to clone/functional-completeness mathematics.

The new question is not “which gates are functionally complete?” It is:

> When the structure of state, communication and adaptation is explicit and local, do different primitive bases / adaptation placements produce genuinely different developmental/resource classes beyond an ordinary exact state-machine or lookup-table parent?

A parent-sufficient result is valid and expected to be informative.

---

# 1. Registered finite universe

## 1.1 Unit state

Each unit has exactly one local Boolean state bit:

```text
s_i ∈ {0,1}
```

The machine has at most `N=2` internal units in v1.

## 1.2 External channels

At each step:

```text
x ∈ {0,1}       # observation/input
l ∈ {0,1,⊥}     # optional teaching/feedback label
```

`⊥` means no label at inference.

One designated unit exposes one output bit `y`.

## 1.3 Topology

Legal topology in v1:

- zero/one directed edge between the two units;
- optional self-state access is local and does not count as an edge;
- external input may be read by each unit;
- label may be read only by primitives in the **development/update phase**, never during ordinary protected inference.

This prevents direct answer leakage from label to output.

---

# 2. Primitive families — low-level, typed, no architecture labels

Candidate catalogue is intentionally overcomplete. Exact reduction decides what is redundant.

## State / interface

```text
READ_INPUT
READ_LOCAL_STATE
READ_NEIGHBOR_STATE
EMIT_LOCAL_STATE
WRITE_LOCAL_STATE
```

## Deterministic Boolean transform

```text
COPY
NOT
AND
XOR
```

NAND/NOR are **not** separately supplied in v1; if useful they must be composed.

## Control

```text
SELECT_IF_CONTROL_BIT
```

A typed multiplexer over two already-computed bits; it does not execute arbitrary code.

## Development-only feedback

```text
READ_LABEL
COMPARE_OUTPUT_LABEL
```

## Restricted update actions

```text
KEEP_STATE
SET_STATE_TO_COMPUTED_BIT
TOGGLE_STATE_IF_ERROR
```

## Topology-development arm only

```text
KEEP_EDGE
TOGGLE_SINGLE_REGISTERED_EDGE_IF_ERROR
```

No arbitrary graph rewrite, program interpreter, gradient primitive, production-rule primitive or Bayesian-update primitive is legal.

---

# 3. Morphology grammar

A morphology is a typed acyclic expression graph for one inference step plus a typed update graph for one development step.

Hard bounds:

```text
<= 2 internal units
<= 1 inter-unit edge
<= 6 primitive transform nodes per unit inference expression
<= 6 primitive transform/update nodes per development expression
one output unit
one optional topology-update action
```

Canonicalize commutative argument order and remove dead nodes before identity hashing.

No universal interpreter, loops or arbitrary lookup tables are candidate primitives.

---

# 4. Four registered adaptation placements

Treat these as **arms**, not primitive labels hidden inside one search space.

## A0 STATIC

No state/topology update from experience.

## A1 LOCAL_STATE

Only unit-local state may change; topology fixed.

## A2 COUPLED_STATE

Both units may change local state based on local/neighbor information; topology fixed.

## A3 TOPOLOGY_PLUS_STATE

Local state plus the single registered edge bit may change after feedback.

A4 arbitrary whole-machine table rewriting is **not** a morphology arm; it is a strong exact parent below.

---

# 5. Strong parents / reduction targets

Every candidate is compared against:

## P0 Exact current-behavior table

Minimal direct table for current `input -> output` behavior; no learning.

## P1 Exact finite-state transducer

Canonical Moore/Mealy-style table over the machine's complete observable/internal state.

## P2 Exact adaptive lookup table

A direct explicit table implementing the complete registered

```text
(current_state,input,label) -> (next_state,output)
```

transition, with all table description/read/update costs charged.

## P3 Small explicit program

Shortest program found in the same low-level expression language **without** modular/local-unit constraints.

If structured morphologies have no developmental/resource residual after these parents:

```text
PARENT_FORMALISM_SUFFICIENT
```

---

# 6. Exact developmental ecologies

All are finite and fully enumerable.

## E0 STATIC_MAPPING

Target mapping is fixed (`identity`, `NOT`, constant mappings). Calibration; A0 should be sufficient.

## E1 ONE_SHOT_BINDING

The target mapping for one input value is revealed by one labelled event and must be retained for later unlabelled probes.

Tests whether adaptive state matters.

## E2 TWO_BINDING_MEMORY

Two labelled input/output bindings arrive sequentially; later both are probed without labels.

Tests memory capacity/encoding.

## E3 REGIME_REVISION

After learning a mapping, exactly one target binding is changed and labelled once. Later probes require the new mapping while the unaffected binding should remain correct.

Tests revision locality and retention.

## E4 DELAYED_CONTEXT

The required output depends on the previous input bit, with no label at inference.

Tests dynamic state independently of supervised binding.

## E5 COUPLED_TWO_UNIT

A target requires combining current external input with one retained state from another unit. Designed so one-unit candidates cannot satisfy all histories under the frozen bounds.

Tests whether a second unit/communication edge earns bounded reach.

## E6 TOPOLOGY_HOSTILE

Construct paired tasks where topology adaptation is either useful or unnecessary; topology-changing arm must not win merely because it can mutate more state.

---

# 7. Exact developmental signature

For each ecology enumerate every legal training/development sequence up to the registered horizon and every subsequent probe sequence.

Signature contains:

```text
outputs at every probe
internal-state trajectory
edge trajectory (A3 only)
retention after revision
failure/abstention if any
```

Two morphologies are exact-developmentally equivalent at this scope only if the full signatures match.

---

# 8. Resource vector

Do not use one scalar as the scientific result.

For each morphology/parent record:

```text
D_desc        canonical description bits/tokens
C_infer       primitive evaluations per inference
C_update      primitive evaluations per labelled update
W_update      state/topology bits actually written
M_persist     persistent mutable bits
C_revision    work + writes after E3 revision
C_compile     cost to compile to/from parent representation where measured
```

Secondary frozen scalar price vectors may be used to expose phase reversals, but raw coordinates remain authoritative.

---

# 9. Exact questions

## C1-Q1 — Does developmental equivalence refine behavioral equivalence?

Expected yes from Stage B/C-v0; re-establish under a structured grammar.

## C1-Q2 — Is any primitive compensation-aware irreducible?

Remove primitive, permit all legal recomposition, rerun complete census.

## C1-Q3 — Does local structure buy a resource frontier?

Compare local adaptive morphologies to P2/P3 direct-table/program parents.

## C1-Q4 — Does topology adaptation expand bounded reach?

Require a witness only if A3 reaches a registered developmental contract that A0–A2 cannot reach under the same bounds, not merely because it uses different syntax.

## C1-Q5 — Does minimum primitive count disagree with minimum lifetime resource cost?

Exact Pareto result preferred over a single winner.

## C1-Q6 — Is the entire structured grammar merely an expensive encoding of P1/P2?

If yes, return parent sufficiency; do not enlarge the benchmark to rescue the basis.

---

# 10. Hostiles

- [ ] label reaches protected inference output directly;
- [ ] canonicalization changes semantics;
- [ ] dead code counted as intelligence/resource;
- [ ] topology mutation only increases hidden state capacity;
- [ ] direct lookup parent denied equivalent memory;
- [ ] structured arm wins because parent description cost is double-counted;
- [ ] one-unit impossibility claimed without exhaustive proof;
- [ ] fixed architecture selected after target outcomes;
- [ ] scalar price chosen post-outcome to manufacture a winner;
- [ ] same morphology represented in multiple syntactic forms inflates diversity;
- [ ] local state reset accidentally between training/probe;
- [ ] E5 encodes the desired two-unit topology into task IDs/features.

---

# 11. Allowed terminals

```text
STRUCTURED_ADAPTIVE_BASIS_RESIDUAL_AT_SCOPE
MULTIPLE_EQUIVALENT_STRUCTURED_BASES
LOCAL_STRUCTURE_RESOURCE_FRONTIER_SUPPORTED
TOPOLOGY_CHANGE_EXPANDS_BOUNDED_REACH_AT_SCOPE
BEHAVIORAL_EQUIVALENCE_STRICTLY_COARSER_THAN_DEVELOPMENTAL_EQUIVALENCE
PARENT_STATE_MACHINE_SUFFICIENT
PARENT_ADAPTIVE_TABLE_SUFFICIENT
PARENT_PROGRAM_SUFFICIENT
NO_PRIMITIVE_IRREDUCIBILITY_AT_SCOPE
RESOURCE_PRICE_REGIME_ONLY
UNIVERSAL_COMPUTATION_ONLY
ASSAY_DEFECT
CANNOT_CHECK_<reason>
```

No Stage-C-v1 terminal establishes a general cognitive atom or cross-paradigm basis.

---

# 12. Freeze / execution order

```text
C1-0 independent protocol hostile review
C1-1 implement canonical grammar/compiler
C1-2 planted selftests / no-alarm controls
C1-3 exact census on E0-E6
C1-4 compensation-aware primitive removals
C1-5 parent compilation/resource comparison
C1-6 exact report + theorem/negative update
```

Only after a nontrivial residual survives C1 may Stage D derive known morphology micro-instances.

# GMI primitive freeze v1

This capsule addresses the 602 Section A1 unchecked boxes: freezing the GMI primitive
signature and proving no architecture label is hidden in the composition grammar.

Status: `FROZEN_FOR_HOSTILE_REVIEW` -- additive to DEFINITIONS_V2_EXACT, supersedes nothing.
Strongest parent: `DEFINITIONS_V2_EXACT` (same primitives; we add the no-hidden-label proof
and Turing insufficiency witness).

Ceiling: G1 (registration of the freeze; no new derivation claimed).

## What is frozen

1. **Typed primitive signature**: `p = (S_p, I_p, O_p, δ_p, F_p, α_p, c_p)` from
   `DEFINITIONS_V2_EXACT.md` Def 1.1. Each primitive's semantics, I/O type, state effect,
   update law, and resource coordinates are fixed below.

2. **Composition grammar C**: exactly five combinators (seq, par, case, loop_n, fbk) from
   `DEFINITIONS_V2_EXACT.md` Def 1.2. No unbounded fixpoint.

3. **No architecture label hidden in primitives (Theorem A1-1)**: every forbidden name
   (BACKPROP, BAYES_UPDATE, ATTENTION, NEURON, PROGRAM_SYNTHESIS, SEARCH, MEMORY) is
   either (a) expressible as a composition of the five combinators under P, or (b) provably
   requires an operation outside P ∪ C and therefore is not closed under Def 1.3.

4. **Plain Turing universality is insufficient (Theorem A1-2)**: two machines that compute
   the same function may differ in their PVR-3 burden (persists / generalises / retains).
   A concrete witness is given.

## File manifest

- `PRIMITIVE_FREEZE_THEOREM_V1.md` -- this file (formal freeze record)
- `primitive_witness.py` -- exact computation proving both theorems
- `test_freeze.py` -- 10+ unittest controls
- `CORE.md` -- read-first entry point
- `MANIFEST.json` -- machine-readable capsule metadata

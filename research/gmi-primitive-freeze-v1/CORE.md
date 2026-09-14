# GMI primitive freeze v1 — read-first entry point

**Ceiling:** G1 (registration of the freeze, no new derivation claimed).

This capsule addresses the 602 Section A1 unchecked boxes about freezing the GMI
primitive signature and proving no architecture label is hidden in the composition
grammar.

## Frozen artifact

`PRIMITIVE_FREEZE_THEOREM_V1.md` contains:

1. **Typed primitive signature** `(S_p, I_p, O_p, δ_p, F_p, α_p, c_p)` from
   `DEFINITIONS_V2_EXACT.md` Def 1.1. Each primitive's semantics, I/O type, state
   effect, update law, and resource coordinates are fixed.

2. **Composition grammar C**: exactly five combinators (`seq`, `par`, `case`,
   `loop_n`, `fbk`) from `DEFINITIONS_V2_EXACT.md` Def 1.2. No unbounded fixpoint.

3. **Theorem A1-1 (no hidden architecture label)**: every forbidden name
   (`BACKPROP`, `BAYES_UPDATE`, `ATTENTION`, `NEURON`, `PROGRAM_SYNTHESIS`,
   `SEARCH`, `MEMORY`) is either (a) expressible as a composition of the five
   combinators under P, or (b) provably requires an operation outside P U C and
   therefore is not closed under Def 1.3.

4. **Theorem A1-2 (Turing universality insufficient)**: two machines that compute
   the same function may differ in their PVR-3 burden. A concrete witness is given.

## Verification

```bash
python -m pytest research/gmi-primitive-freeze-v1/test_freeze.py -v
```

## Files

| File | Role |
|------|------|
| `PRIMITIVE_FREEZE_THEOREM_V1.md` | Formal freeze record |
| `primitive_witness.py` | Exact computation proving both theorems |
| `test_freeze.py` | 10+ unittest controls |
| `MANIFEST.json` | Machine-readable capsule metadata |

## Strongest parent

`DEFINITIONS_V2_EXACT.md` (same primitives; we add the no-hidden-label proof
and Turing insufficiency witness). This capsule is additive; it supersedes nothing.

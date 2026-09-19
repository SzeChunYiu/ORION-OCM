# AG5 — the `G0` extension lowering ledger (START HERE)

AJ5 lowered the five core `G0` opcodes and gave them a primitive-status ledger. The four
registered extension families each *introduce* a named operator and none of them had a status.
This tranche lowers all sixteen of those operators into the same AJ5 role basis and adjudicates
them, so the ledger AG2 asks for covers every registered instruction rather than five of them.

## Headline numbers (exact integer arithmetic throughout; no float enters any claim)

| quantity | value |
|---|---|
| registered checks | `54,366` |
| lowering mismatches against the merged parents | `0` |
| resource-vector mismatches against the parents' own declared vectors | `0` |
| ledger rows | `21` (5 core + 16 extension) |
| operators that are generators relative to the AJ5 role basis | `0` |
| status split | `DERIVED_OPERATION` 7 · `MACRO` 12 · `SEMANTIC_CONVENIENCE` 1 · `RESOURCE_PRICED_IMPLEMENTATION_PRIMITIVE` 1 |
| operators carrying `EXTERNALLY_REGISTERED` | `4` — `CALL`, `VERIFY`, `ADOPT`, `APPLY_EXTERNAL` |
| adoption witness pairs, internal triple fixed | `27 / 27` terminals differ, `9 / 27` active states differ |
| provenance tag: state effect / admission gate | `0 / 486` differences · `24 / 24` forged refused with the gate, `24 / 24` admitted without |
| structure dependence, same state under two graphs | `NEIGHBOR_UPDATE 680 / 756`; `POINTWISE 0 / 756`; `GLOBAL_BROADCAST 0 / 756` |
| lowering cost of `NEIGHBOR_UPDATE` by edge count | `0 -> 24`, `1 -> 28`, `2 -> 33`, `3 -> 39` |
| cost-formula validation, literal expansion vs closed form | `1,972` checks, `0` failures, operand box `16` |

## The boundary you must not drop

Of the five guards in the adoption chain, the registered scope identifies four. The **replay
guard is not identified and cannot be**: adoption strictly increments the active version, so a
consumed proposal always also fails the version test, and no registered case makes the replay
guard the single failure. Exhaustively over all 31 proper subsets of the chain, exactly 1
reproduces the parent on every one of 145 attempts — the subset that drops the replay guard —
and that matches the isolation analysis exactly. The 27-case base universe was far weaker: it
identified only the accept guard and admitted 15 reproducing subsets.

Charged role counts are relative to a chosen lowering and are deliberately **not** in the
two-route agreement set, exactly as AJ5's transfer boundary says instruction-count
descriptions do not transfer.

## Evidence

- **2 materially independent routes.** Route A rebuilds each operator from AJ5 roles over a
  register store and compares against the merged parent modules. Route B imports neither route
  A nor any parent module: it rebuilds the universes from their published definitions and
  recomputes everything by a different mechanism — one global denominator and integer matrix
  arithmetic; an incidence-list traversal with no adjacency register vector; an event-log
  replay; the admission relation as an abstract external oracle. **56 published quantities
  agree, 0 disagreements.**
- **13 hostiles, all detected, each with a control that is clean**: wrong index in the update
  sum, transposed composition, non-exact weights, an unnormalized row, a site in its own
  neighbourhood, a constant charge for a structure-priced operator, implicit delivery on send,
  the provenance gate deleted, the admission guard deleted, replay allowed, an architecture
  family name planted in the lowering, an off-by-one cost formula, and a case table trimmed of
  its isolating cases.
- **Nulls.** `0 / 200` randomized weight-cell permutations, `0 / 200` randomized adjacency
  substitutions and `0 / 200` randomized channel permutations reproduce the parent semantics.
  The guard null is exhaustive rather than sampled: all 31 proper subsets.
- **No-alarm case asserted.** On the true configuration every detector is silent: tag
  differences 0, control operators structure-dependent 0, family-name hits 0, cost-formula
  failures 0, guard prediction matches.

## Reproduce

```
python3 -I -B  research/gmi-833-ag5-extension-lowering-v1/ag5_extension_lowering_v1.py
python3 -I -B  research/gmi-833-ag5-extension-lowering-v1/independent_oracle_v1.py
python3 -I -O -B research/gmi-833-ag5-extension-lowering-v1/test_ag5_extension_lowering_v1.py
```

Route A takes about 14 s; the other two under 3 s. Stdlib only.

## Files

`FREEZE_V1.md` (committed before any code, commit `1bdac829`) ·
`AG5_EXTENSION_THEOREMS_V1.md` (`AG5X-1` … `AG5X-6`) · `PARENT_LEDGER.md` ·
`RESULT_V1.json` · `ORACLE_RESULT_V1.json` · `TEST_RESULT_V1.json` · `MANIFEST_V1.json`.

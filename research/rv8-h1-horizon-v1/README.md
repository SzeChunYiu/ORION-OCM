# RV-8 — the H1 library-acquisition horizon

FNA-4 established that a learned library beats the incumbent **per task** at 16 tasks,
and **projected** break-even at ~6,123 tasks. That is a 380× extrapolation, so
`LIBRARY_ACQUISITION_EXCEEDS_LATER_SAVINGS` was PROJECTED, NOT OBSERVED. This study runs
the horizon on a `(horizon × same-family-mix)` grid to convert it into an observation or
refute it.

The lever question is closed — the admission rule is the failing stage, the lever was
applied, and a classical stdlib-only parent (Stitch + misfire nogoods + CEGIS) holds
`PARENT_SUFFICIENT_FOR_EXPERIENCE_CONSOLIDATION_AT_REGISTERED_SCOPE`. This is a scale
question.

## Files

| file | what it is |
|---|---|
| `RV8_PROTOCOL.md` | the frozen protocol — axes, arms, gates, endpoints, predictions, limitations |
| `RV8_FREEZE.json` | digests and salts recorded before any scored cell |
| `rv8_horizon.py` | the runner: `preflight`, `replicate`, `cell` |
| `rv8_analyse.py` | the analysis, declared in the freeze commit before any result exists |
| `probe_cost.py` | post-preflight sizing probe (SLURM `--time` and launch order only) |

The world, solver, learners, arms and cost model are **imported** from
`research/functional-neural-absorption-v1/fna4_library_synthesis/`, never copied. Every
cost term FNA-4 charges is still charged.

## Running it

```
python3 rv8_horizon.py replicate  <out>     # frozen-receipt determinism gate
python3 rv8_horizon.py preflight  <out>     # harness + acquisition gates, library pickle
python3 rv8_horizon.py cell <i>   <out>     # one (arm, mix, composition, seed) stream
python3 rv8_analyse.py <out>
```

984 cells. Off-Mac only; LUNARC `lu48` under account `lu2026-2-51`, no network from the
cluster. Cells dump progressively every 4,096 tasks, so a timed-out cell still yields an
honestly-labelled prefix.

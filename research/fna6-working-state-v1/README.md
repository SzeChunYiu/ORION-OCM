# FNA-6 — working-state (residual-stream analogue)

Lane FNA-6 of issue #214 (SzeChunYiu/ORION-OCM). Question: does the CURRENT
active-KSO working state on main (structural adjacency index + lazy per-query
liveness + ATMS-style revocation propagation) hold a working-state function that
classic explicit architectures already exhibit — blackboards (Hays-Roth 1985 /
BB1), Soar working memory, ACT-R module buffers — and at what whole-lifecycle
cost?

## What is here

| file | role |
|---|---|
| `PROTOCOL.md` | contract W1-W6, arms, metrics, frozen decision rules |
| `FREEZE_FNA6_V1.json` | frozen before the first scored run: salts, sizing, thresholds, levers |
| `world.py` | population (production `random_space`), two-obligation stream, oracle (`gated_closure`) |
| `contract.py` | charged counters, external exact checker, arm surface |
| `arms.py` | P0 incumbent (instrumented mirror of production), P4 full rescan |
| `blackboard.py` | P1A append-only panels, P1B BB1 version tags (lever L1) |
| `soar_wm.py` | P2 goal-scoped production WM + labelled no-goal-binding mutant |
| `actr.py` | P3 strict-capacity buffers, P3R retrieval-time revalidation (lever L2) |
| `run_fna6.py` | scored runner: validations, replay, locality + null, terminals |
| `test_fna6.py` | strict-JSON, fixture lifecycles, detector teeth, harness agreement |
| `RESULTS_FNA6_V1.{json,md}` | written by the scored run |

## Running

From the repo root:

```
python3 -m unittest discover -s research/fna6-working-state-v1 -p 'test_*.py'
python3 research/fna6-working-state-v1/run_fna6.py
```

All execution on laptop billy (dedicated clone), never the Mac mini.

## Honesty rails

The oracle and impact cones are judge-side and never charged to arms. The
mutant arm is a labelled probe and never a result. Negative OCM-mechanism
outcomes are engineered through the pre-registered levers (L1, L2) under
`results.engineering_chain`, re-running the SAME frozen stream. Terminals use
the issue #214 section 7 vocabulary. Nothing here claims the blackboard is
novel or that any neural component is replaced.

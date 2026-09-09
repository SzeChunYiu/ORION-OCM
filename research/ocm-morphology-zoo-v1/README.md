# OCM Morphology Zoo v1 (issue #221)

Research capsule: quality-diversity generation over OCM organism morphologies,
evaluated against an EXHAUSTIVE census of the bounded genome space. Research
only — nothing here touches production `src/`.

## Read order

1. `PROTOCOL_V1.md` / `PROTOCOL_V1.json` — stage plan + invariants + component digests
2. `FREEZE_V1.json` — prospectively frozen denominators, budgets, constants (read before any result)
3. `MORPHOLOGY_GENOME_V1.json`, `COGNITIVE_UNIT_CONTRACT_V1.json`, `DESCRIPTOR_REGISTRY_V1.json`, `OBJECTIVE_REGISTRY_V1.json`, `TASK_ECOLOGY_V1.json` — registries, GENERATED from code by `hpc/gen_registries.py` (never hand-edit)
4. `REPO_STATE.json`, `LITERATURE_LEDGER.md`, `OPEN_LANE_COLLISION_MAP.json` — MZ-D0 freeze

## Layout

- `morphology/` — genome schema, compiler (invariants fail-closed), canonicalizer, mutations, direct genome + census enumeration; `cgp_genome.py` is the E1 CGP re-encoding (MZ-D5 encoding fit demonstrated); `graph_grammar.py`/`typed_program_genome.py` remain MZ-D5 stubs
- `evaluation/` — deterministic evaluator, descriptors, objectives (frozen dev_score), lifetime tranche, hard-gate invariants, sha256 receipt chain
- `search/` — P01..P15 algorithm arms (live: random, NSGA-II, MAP-Elites, NSLC, CVT-ME, MOME, lexicase, novelty; stubs marked MZ-D5+)
- `hpc/` — census, recovery test, registry generator, smoke tests, Slurm scripts, `submit_campaign.py`
- `results/`, `archives/`, `manifests/` — outputs per run, keyed by run id

## Ground truth (P00 census, laptop billy, deterministic receipt head 79e8773d…)

56,160 genomes in CENSUS_BOUND_V1; 14,904 feasible (26.5%); exact Pareto set 387
phenotypes; best dev_score within bound 0.649325; S grid occupies 4/100 cells,
B grid 2/100 (near-degenerate coverage — a finding, see FREEZE_V1.json).
Evaluation cost 0.086 ms/genome.

## Amend-1 (FREEZE_V1_AMEND_1.json): finer/higher-D axes — saturation proven intrinsic

P00B exhaustive extension (same receipt head): S3d@10 occupies 8/1000 cells,
S2d@20 still 4 (unit_type_entropy is CONSTANT over all 14,904 feasible
genomes), B2d@20 4/400, exhaustive deterministic CVT-64 collapses to 18
occupied niches.  Amend-1 campaign (LUNARC array 3586932, 24/24 ok, audit
3586981 OK): grid archives now SATURATE the amended ceilings exactly
(P03: 8.0 elites = 8/8 S3d cells; P05: 4.0 = 4/4 B2d; P06: 16/18 census
niches) — the retention obstruction is PROVEN to be descriptor-function
degeneracy under CENSUS_BOUND_V1, not grid resolution and not search
failure.  Random still leads Pareto recovery at equal evals (P01 0.3824 vs
P04 0.1111) and dominates the same-CPU-hour view (95.7 vs 6.8 per cpu-hour).

## Status

- MZ-D0/D1/D2/D3/D6 done (census, calibration, production campaign, LUNARC harness; amend-1 re-ranking complete)
- MZ-D4 gate CLOSED by measurement (`results/MZD4_COST_FIT.json`): evals not binding (whole space = 17.15 s; 0.085 ms/eval), no continuous relaxation, no task generator → P08/P10 stay deferred
- MZ-D5 encoding fit DEMONSTRATED for E1 CGP (`results/MZD5_ENCODING_FIT.json`): surjective over all 56,160, mutations legal, codec 4.5% of eval, neutral network measured; scored direct-vs-CGP comparison needs its own numbered amendment
- Later: MZ-D7 lifetime, MZ-D8 islands, MZ-D9 hostile tests

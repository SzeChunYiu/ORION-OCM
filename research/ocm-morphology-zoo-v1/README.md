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

- `morphology/` — genome schema, compiler (invariants fail-closed), canonicalizer, mutations, direct genome + census enumeration; `cgp_genome.py`/`graph_grammar.py`/`typed_program_genome.py` are MZ-D5 tranche stubs
- `evaluation/` — deterministic evaluator, descriptors, objectives (frozen dev_score), lifetime tranche, hard-gate invariants, sha256 receipt chain
- `search/` — P01..P15 algorithm arms (live: random, NSGA-II, MAP-Elites, NSLC, CVT-ME, MOME, lexicase, novelty; stubs marked MZ-D5+)
- `hpc/` — census, recovery test, registry generator, smoke tests, Slurm scripts, `submit_campaign.py`
- `results/`, `archives/`, `manifests/` — outputs per run, keyed by run id

## Ground truth (P00 census, laptop billy, deterministic receipt head 79e8773d…)

56,160 genomes in CENSUS_BOUND_V1; 14,904 feasible (26.5%); exact Pareto set 387
phenotypes; best dev_score within bound 0.649325; S grid occupies 4/100 cells,
B grid 2/100 (near-degenerate coverage — a finding, see FREEZE_V1.json).
Evaluation cost 0.086 ms/genome.

## Status

- MZ-D0/D1 done; MZ-D2 done (census + 8-arm recovery calibration, 3 seeds)
- MZ-D6 LUNARC harness + MZ-D3 production campaign (frozen 40,000 evals/arm/seed) in flight
- Later: MZ-D5 encodings, MZ-D7 lifetime, MZ-D8 islands, MZ-D9 hostile tests

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

## Amend-2 (FREEZE_V1_AMEND_2.json): E0-direct vs E1-CGP scored encoding comparison

MZ-D5 encoding fit demonstrated, then scored under its own numbered amendment at
equal eval budget (40,000/seed, 3 seeds, codec seconds charged inside the E1 arm
wall time; E0 determinism cross-checked 96/96 against the amend-1 runs).
Terminal: `MIXED_INTERMEDIATE_NO_TERMINAL` — E1-CGP wins one pair (R01 random arm:
pareto recovery 0.5116 vs 0.3824) and ties three (MAP-Elites arms flip per
archive); no encoding dominates at this scope. Scored artifacts:
`results/AGGREGATE_AMEND2.json`.

## Amend-3 / MZ-D7 (FREEZE_V1_AMEND_3.json): tier-T2 lifetime — terminal reached

P00C exhaustive census at tier T2 (LifetimeEcologyV2): 56,160 genomes, 28,584
feasible, exact Pareto set 792, receipt head 67ed9271…. Amend-3 campaign
(LUNARC array 3587080, 15/15 ok, aggregate 3587081; every arm evaluated at T2
including both sides of each comparison; Archive-D metrics recomputed uniformly
from genomes with per-elite reset controls):

**Terminal: `DIVERSE_HIGH_PERFORMING_MORPHOLOGIES_FOUND_AT_SCOPE`** (frozen
rule-2 match: some D-archive arm with own-axis recovery >= 0.25 AND best_dev
>= P01 - 0.01). P05/D2d 1.0, P09/D3d 0.988, P06/CVTD 0.615 own-axis; QD
best_dev_T2 0.6037 > P01 0.5711; P01 still leads raw pareto recovery
(0.4604 vs ~0 for cell-elite archives) — all 4 pairs TIE, 0 wins each way.
Developmental-advantage rule NOT met (0 pair wins; no arm retention-frontier-
positive — frontier elites skew to zero-retention architectures; every arm
fails the frozen >= 0.5-every-seed retention bar, best is P03 at 0.313).
"Random still leads" is not overturned on dominance; the diversity claim is
what terminalizes. Scored artifacts: `results/AGGREGATE_AMEND3.json`,
`manifests/CAMPAIGN_AMEND3_MANIFEST.json` (sha-chain V1 -> A1 -> A2 -> A3,
checksum-gated submission).

Timing erratum: `FREEZE_V1_AMEND_3_TIMING_ERRATUM.json` — the amendment's
hand-written `created_utc` label (21:20Z) postdates the scored array
(submitted 21:15:59Z); the sha-chain checksum gate proves the exact frozen
bytes existed at submission, so freeze-before-score holds; label corrected by
erratum, frozen file untouched.

## Status

- MZ-D0/D1/D2/D3/D6 done (census, calibration, production campaign, LUNARC harness; amend-1 re-ranking complete)
- MZ-D7 done at tier T2 via amend-3 (DIVERSE_HIGH_PERFORMING_MORPHOLOGIES_FOUND_AT_SCOPE); amend-2 encoding comparison MIXED_INTERMEDIATE_NO_TERMINAL
- MZ-D4 gate CLOSED by measurement (`results/MZD4_COST_FIT.json`): evals not binding (whole space = 17.15 s; 0.085 ms/eval), no continuous relaxation, no task generator → P08/P10 stay deferred
- MZ-D5 encoding fit DEMONSTRATED for E1 CGP (`results/MZD5_ENCODING_FIT.json`): surjective over all 56,160, mutations legal, codec 4.5% of eval, neutral network measured; scored direct-vs-CGP comparison needs its own numbered amendment
- Later: MZ-D8 islands, MZ-D9 hostile tests; MZ-D5 scored-encoding question remains MIXED_INTERMEDIATE (amend-2)

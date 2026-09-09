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

## Amend-4 / MZ-D8 + MZ-D9 (FREEZE_V1_AMEND_4.json): P13 islands + hostile subset

`FREEZE_V1_AMEND_4.json` is written by a TOOL (`hpc/freeze_amend4.py`), not by
hand: created_utc is stamped by the tool at freeze time (the amend-3 timing
erratum, corrected), the ancestor chain V1->A1->A2->A3 sha-verified before
writing, and the freeze refuses to run unless `archives/HZD9_TRUTH.json`
exists with every P00C xcheck true and no scored amend-4 status exists
(unscored truth -> freeze -> scored runs). One pre-scoring refreeze is
recorded in the file itself (`supersedes_sha256`): the first A4 embed lacked
the two amend-3 denominator keys (PARETO_T2, S3d@10_occupied_T0ref); the
smoke gate caught it before any scored run and the tool refroze with the
defect recorded, never silently.

**MZ-D8 (P13 islands)** — 7 prior-locked islands over the frozen census
grammar (symbolic/rule-heavy, programmatic, factor/graph-heavy,
blackboard/production, memory-heavy, minimal, heterogeneous; the 8th P13
prior "open-ended operator language" is DROPPED and declared — O_basis is
derived, not a free genome field). Per-island MAP-Elites GridArchive over
D_dev_2d@10, region-locked variation, per-island RNG streams
(`seed*1000003+i`), simultaneous unidirectional ring migration every 500
rounds (best elite by dev_score, zero eval charge). Arms: I01_islands_ring_mig
vs I02_islands_nomig, 3 seeds, budget 40,000 (per-island 5,714). Hostiles
from #221 sec 12 carried as metrics: island-class entropy mid/final ("island
diversity disappears after migration") and frontier birth-island concentration
("one mature parent architecture reproduces the entire frontier").

**MZ-D9 (hostile subset)** — fresh unscored HZD9 census over the census
(28,584 feasible; collapse ratio, D2d cell F_arch purity, eta^2 per D-axis,
quality bar = census-median dev_score_T2 0.224507, frozen into A4) + uniform
recompute of the 15 frozen QDA3 archives (junk-free recovery at the quality
bar, own-axis determinism xchecks against the frozen QDA3 values). The three
most load-bearing sec-12 hostiles against the amend-3 terminal
DIVERSE_HIGH_PERFORMING_MORPHOLOGIES_FOUND_AT_SCOPE: genotype->phenotype
collapse, high coverage from low-quality junk, descriptor-choice-as-
architecture-label. Possible amend-3 terminal statuses: RETAINED,
RETAINED_DESCRIPTOR_CONFOUNDED, UNDERMINED_DIVERSITY, UNDERMINED_QUALITY.

Verdicts: `results/AGGREGATE_AMEND4.json` (aggregate refuses to run unless
all 21 statuses are ok and receipts verify; first-match frozen rules, never
narrated). Scored artifacts: `manifests/CAMPAIGN_AMEND4_MANIFEST.json`.

**MZ-D8 scored (array 3587139, 21/21 ok, aggregate 3587148):
`MIXED_INTERMEDIATE_NO_TERMINAL`** — BOTH sec-12 island hostiles REFUTED at
this scope: ring migration did NOT collapse island diversity (final entropy
ratio mig/nomig 1.038; I01 entropy 0.852 vs mid 0.839) and NO single parent
architecture reproduced the frontier (frontier birth-island concentration
0.3125 << 0.9). Matched pair I01 vs I02 TIE (D2d pooled 0.987 vs 0.980;
pareto 0.0143 vs 0.0147; best_dev equal 0.571144) — migration neither helps
nor hurts at this budget, so rule 3 (transfer-supported) also fails on the
pair-win precondition.

**MZ-D9 scored: rule 3 fired — amend-3 terminal status
`UNDERMINED_QUALITY`** (verdict marker MIXED_INTERMEDIATE_NO_TERMINAL).
Hostile 1 (genotype->phenotype collapse) REFUTED decisively: the census
encoding is INJECTIVE over feasible space (28,584 genotypes -> 28,584
distinct phenotypes, collapse 0.0; archive collapse 0.0 on every arm).
Hostile 2 (descriptor = architecture label) NOT fired: D2d purity fraction
0.48 < 0.5, max eta^2(F_arch) 0.387 < 0.8 (closest axis:
persistent_growth_per_capability). Hostile 3 (high coverage from junk) HIT:
at the census-median quality bar 0.224507, P05/D2d keeps only 32.7% and
P09/D3d 28.9% of its own-axis coverage (P06/CVTD 82.2%, P01 random 97.3%,
P03/S3d 100%) — the amend-3 terminal's coverage claim rests substantially on
below-median-quality elites; a revival iteration (quality-gated D-archive
admission) is owed. Descriptive: 28,584 phenotypes map to only 5,232
distinct objective vectors (0.817 objective-space collapse) — morphological
diversity exceeds behavioral diversity, a lead for the next tranche.

## Amend-5 (FREEZE_V1_AMEND_5.json): quality-gated D-archive admission — the owed revival

Amend-4's own frozen mzd9 rule 3 (UNDERMINED_QUALITY) owes a revival iteration:
attribute the failure to ONE stage (the QUALITY stage of archive admission) and
apply the matching lever — `map_elites.run(admission_bar=b)` admits a feasible
record to the D-archive only if `dev_score >= b`; rejected evals stay charged to
the budget.  Junk-free coverage becomes the archive's own objective, so the
amend-3 DIVERSE terminal either stands cleanly at scope with the gate ON or is
honestly revised to quality-conditional.  The gate is the ONE varied dimension:
G00 no-gate twins (same algorithm/budget 40,000/seeds 0-2/axis/res) run in the
same array for attribution and double as in-array determinism xchecks —
`admission_bar=None` consumes no RNG, so each G00 arm must reproduce its frozen
QDA3 twin archive record-for-record (asserted in the worker, plus HZD9R
junk-free cross-check since the bar equals the census median).

Bar chosen PROSPECTIVELY from a new unscored census (`hpc/gate_ceiling.py`,
`archives/GATE_CEILING_TRUTH.json`, receipt 6ce5ceff38a0de5c, xchecked against
P00C/HZD9): per-cell in-census MAX dev gives the structural ceiling of
own-axis recovery at each bar; the frozen rule takes the STRICTEST ladder
quantile keeping ceil >= 0.25 on both gated axes — q0.5 (census median
0.224507 == HZD9 quality_bar_T2) qualified (ceil D2d 16/50 = 0.32, D3d 21/83 =
0.253012), so the coordinator's default was frozen and no relaxation was
needed; the full ladder is embedded in the freeze for audit (dev scores go
negative below q0.25: q0.2 bar is -0.0509).

Arms (12 tasks = 4 arms x 3 seeds): G01_gate_D2d / G01_gate_D3d (bar ON) vs
G00_nogate_D2d / G00_nogate_D3d (control).  First-match terminal rules in #221
sec-15 vocabulary, frozen pre-score: (1) some gated arm seed-mean own-axis
recovery >= 0.25 AND best_dev_T2 >= 0.561144 (P01 0.571144 - 0.01, the amend-3
DIVERSE clause verbatim) -> DIVERSE_HIGH_PERFORMING_MORPHOLOGIES_FOUND_AT_SCOPE
+ RESTORED_QUALITY_GATED_AT_SCOPE; (2) every gated arm < 0.25 ->
NO_MEANINGFUL_BEHAVIORAL_DIVERSITY + REVISED_QUALITY_CONDITIONAL; (3) else
MIXED_INTERMEDIATE_NO_TERMINAL + PARTIAL_RESTORATION.  Aggregate reports
gate-minus-control deltas per axis (attribution, never rule-firing).  Scored
artifacts: `manifests/CAMPAIGN_AMEND5_MANIFEST.json`,
`results/AGGREGATE_AMEND5.json`.

**Amend-5 scored (smoke 3587175, array 3587176 12/12 ok, aggregate 3587226):
rule 1 fired on BOTH gated arms — `DIVERSE_HIGH_PERFORMING_MORPHOLOGIES_
FOUND_AT_SCOPE` / `RESTORED_QUALITY_GATED_AT_SCOPE`.**  G01_gate_D2d: own-axis
0.32 per seed (16/50, junk-free ratio 1.0 by construction), best_dev 0.603719;
G01_gate_D3d: own-axis 0.289157 (24/83), best_dev 0.598576.  Controls confirm
attribution: G00 raw coverage 1.0 / 0.987952 but junk-free only 0.326667 /
0.288597 (reproducing HZD9R exactly) — the gate trades raw coverage for
clean coverage (delta -0.68 / -0.698795) while best_dev is unchanged, i.e.
the junk elites were never load-bearing for quality, only for cell counts.
All G00 byte-identity xchecks true (admission_bar=None reproduced the frozen
QDA3 twins record-for-record; HZD9R junk-free equality).

**Post-score finding (unscored diagnostic, `results/GRAMMAR_ESCAPE_DIAGNOSTIC.
json`): the enumerated census is a strict SUBSET of the searched grammar.**
G01_gate_D3d exceeded its GATE-CEILING "ceiling" (24/83 > 21/83) — impossible
for census-member genomes under deterministic evaluation.  Cause:
`morphology/mutations.py` draws families from the FULL vocabularies (not
CENSUS_BOUND_V1), can add units outside the census pool, and perturbs thetas
(a continuous dimension `enumerate_census` never varies — every census genome
carries DEFAULT_THETA).  98.15% of amend-5 archive elites escape the enumerated
grammar; archive best devs (0.6037) live entirely outside it, while P01
(random_genome only, in-grammar) tops out at the census best 0.571144.  So the
GATE-CEILING ceil_* values are census-subset maxima, not bounds on the searched
space (verdict unaffected: the frozen rules reference recovery and best_dev
bars, never ceilings), and P01-vs-QD best_dev comparisons carry a grammar
confound — a lead for a future amendment (grammar-fair comparison or a
theta-extended census).

## Status

- MZ-D0/D1/D2/D3/D6 done (census, calibration, production campaign, LUNARC harness; amend-1 re-ranking complete)
- MZ-D7 done at tier T2 via amend-3 (DIVERSE_HIGH_PERFORMING_MORPHOLOGIES_FOUND_AT_SCOPE); amend-2 encoding comparison MIXED_INTERMEDIATE_NO_TERMINAL
- MZ-D4 gate CLOSED by measurement (`results/MZD4_COST_FIT.json`): evals not binding (whole space = 17.15 s; 0.085 ms/eval), no continuous relaxation, no task generator → P08/P10 stay deferred
- MZ-D5 encoding fit DEMONSTRATED for E1 CGP (`results/MZD5_ENCODING_FIT.json`): surjective over all 56,160, mutations legal, codec 4.5% of eval, neutral network measured; scored direct-vs-CGP comparison needs its own numbered amendment
- MZ-D8 done via amend-4: MIXED_INTERMEDIATE_NO_TERMINAL, both island hostiles refuted (migration entropy-neutral, no frontier monoculture)
- MZ-D9 done via amend-4: amend-3 terminal UNDERMINED_QUALITY (junk-filtered D2d/D3d coverage 0.33/0.29 at the census-median bar); collapse and descriptor-confound hostiles refuted; quality-gated revival owed
- Amend-5 done (array 3587176, 12/12 ok): DIVERSE_HIGH_PERFORMING_MORPHOLOGIES_FOUND_AT_SCOPE / RESTORED_QUALITY_GATED_AT_SCOPE on both gated axes at the census-median bar 0.224507; junk-free ratio 1.0 by construction; controls reproduce HZD9R
- Post-amend-5 unscored finding: mutation escapes the enumerated census grammar (98% of elites; full-vocab family draws + theta perturbation); census per-cell maxima are subset maxima, P01-vs-QD best_dev carries a grammar confound — lead for a future amendment
- MZ-D5 scored-encoding question remains MIXED_INTERMEDIATE (amend-2)

# B6 adjudication correction V1

Date: 2026-09-13. Status: finite scientific scoring correction; no new experiment.
Reviewed source: main 9f35356ed8e07d4b64c01431925c8278a198f288, incorporating
the bc4dc228 lineage scorer. The original D-table authority is commit
5378c2b7f91f8fbc567764a2ee0c5ff6e256e814; the imported
GMI_B6_DEVELOPMENTAL_MORPHOGENESIS_RV_377_180_FREEZE.md also contains later
Z1--Z5 registrations and disclosures. The freeze and all raw records are unchanged.

## Logical contract and strongest parent

The parent operation is direct evaluation of the frozen predicates under
partial information: HELD requires every admitted completion to satisfy the
predicate, FAILED requires every completion to refute it, and otherwise the
status remains unresolved. This is elementary quantified logic, not a new
GMI mechanism. Completed-run nonrecovery explicitly admitted by a frozen
condition is distinct from a missing receipt or unknown field.

This correction repairs the adjudicator's inference from records. It does not
retune search, thresholds, interventions, candidates or the measured outcomes.

## R1 — load-bearing terminal and the separate kill condition

The D terminal requires D1a AND D1b. A SAME witness with CONTINUED=(2,2,2),
RESET=(1,1,4), TWIN=(3,3,3) has D1a false and D1b true; the previous scorer
reported developmental morphogenesis observed. V2 reports NOT_OBSERVED.
A D1a failure on two seeds blocks observation; the distinct all-three-seed
kill condition is exposed separately and does not trigger from two failures.
Unknown load-bearing results remain unresolved even when every file exists.

D1a held with D1b failed produces the terminal register's parent-sufficient
result. D2 class-sign evidence remains reported separately; it cannot bypass
the explicit D1a/D1b conjunction. Tests cover all 16 pairs of majority hit counts.

## R2 — D2a is a conjunction of separate majorities

Earlier seeds {0,1} and memory-carrier seeds {1,2} satisfy both required
majorities, although their intersection has only one seed. The previous
majority-of-conjunctions incorrectly returned FAILED.
V2 reports the earlier and memory predicates as separate components, with
their own per-seed values and counts, then conjoins their aggregate verdicts.
All 64 pairs of binary three-seed patterns are checked independently.

## R3 — the full defining baseline is required for a spread

RESET burdens 100,101 with the third unknown do not establish a spread of 1.
Completing the baseline with 200 gives spread 100, reversing the previous
D3a failure on two CONTINUED/TWIN differences of 10. V2 leaves the comparison
pending until all three baseline values are known. Completing with 200 yields
HELD; completing with 102 yields FAILED on the same candidate differences.
The same whole-baseline rule applies to the DENSE spread.

## R4 — identity evidence and documented aliases

Missing target or seed fingerprints cannot identify two experiments.
Distinct files with burdens 1 and 2 and absent identity metadata previously
collapsed to one because both hashed the empty list.
V2 hashes only a supplied nonempty string fingerprint list and requires a
known target before inferring identity from campaign metadata. The digest is
full SHA-256. Identity is conditional on the fixed frozen campaign; it is not
a general assertion that matching metadata prove independent measurements.

A shared file path still identifies the documented CROSS/RESET--DISJ/RESET
alias. Deductions count distinct files, avoiding double subtraction of aliases.
Unknown provenance remains unmerged and is listed explicitly. The field
n_experiments_after_proven_deduplication reports that provisional grouping;
n_distinct_experiments is null when identity is unresolved.
Known equal and known distinct seeded-population controls are both tested.

## R8 — founder coverage and the all-recovery quantifier

Z5 excludes cold RESET arms. Every reported warm-arm DENSE recovery must enter
the evidence register before its founder is examined. One known non-DENSE
founder plus 17 unknown warm-arm founders cannot produce HELD.
Missing recovery flags remain unknown, and invalid seed indices cannot select
a carrier accidentally through negative indexing or Boolean-to-integer coercion.
A known DENSE founder can falsify early; contradictory known founder records
for a proven identical experiment block an adjudication.

The frozen Z5 claim quantifies over every recovered machine. The available
first_dense_admissible fields identify only the first recovery per arm.
Even complete non-DENSE founders for those first recoveries establish only
recorded_first_recovery_verdict=HELD. The original broader verdict remains
UNDETERMINED__FIRST_RECOVERY_ONLY. A complete recovery census with equivalent
verification would be required to certify the universal positive. This is a
separate evidence obligation, not a narrowed rewrite of the frozen prediction.

## Adjacent frozen-condition repairs

D2d literally accepts being within spread OR registered UNDETERMINED on two
of three seeds. Two completed no-recovery cases plus one determined failure
therefore satisfy its registered disjunction, although they provide no numeric
support for the class-conditioned sign. V2 separately reports numeric true/
determined counts, the disjunctive condition counts and accepted censored
seeds. HELD_WITH_REGISTERED_UNDETERMINED_CASES and the existing all-vacuous
label preserve that difference. Missing files/metadata remain pending.

The Z registration requires all campaign arms before a final adjudication.
A logically settled early Z1--Z3 predicate remains visible, but the campaign
terminal stays incomplete while other registered arms are missing.
The frozen seed identities are exactly {0,1,2}; duplicates, Boolean identities
and substitutions cannot manufacture three distinct registered seeds.

## Verification and output migration

The isolated laptop CPython 3.12/pytest run passes 40 focused tests, including
all 14 existing guards, JSON counterexamples, the 16 D1 hit-count pairs,
64 D2a Boolean-pattern pairs, and known-complete positive controls.
These are finite scorer tests, not campaign reruns or empirical replication.

The corrected schema is StageB6AdjudicationV2. Default generated outputs are
STAGE_B6_DEV_ADJUDICATION_V2_<host>.json and
STAGE_B6_DEV_ADJ_VALIDATION_V2_<host>.json.
Historical V1 outputs are not overwritten; an explicit preservation test
checks this. Consumers must opt into V2, its D2a component layout, null
unresolved identity count and separately scoped Z5 evidence.
A scoped search of tracked Python/shell/YAML/Markdown consumers found the old
adjudication filename referenced only by the scorer's own regression test.
No claim is made about external scripts or untracked consumers.

Source: gmi_microscope/b6_adjudicate.py.
Tests: test_gmi_b6_adjudicator_guard.py.

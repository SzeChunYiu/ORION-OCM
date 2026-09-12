# GMI closure gap ledger v9 — real-transfer crossover cells re-tested off-band; cost-charged parent

Status: **REAL-TRANSFER CLASS: LAWS ARE A FREE PRE-OUTCOME PREDICTOR OFF THE FINITE-SAMPLE BAND (63/64 REPLICATES, CV
53/64 AT 12–15 EXTRA FITS); CROSSOVERS UNDECIDED BY LAW OR CV; EXTERNAL GATES REMAIN**

Date: 2026-09-12. Successor to `GMI_CLOSURE_GAP_LEDGER_V8.md`, which is not edited. V8's terminals remain authoritative
where this file does not name a successor.

## What ran between V8 and V9

| id | what | where | receipts | terminal |
|---|---|---|---|---|
| RV-377-194 | B: mass-weighted variance term `σ̂² p m / n`, registered band (z = 2 on paired per-query test errors), off-band grid τ ∈ {0.5, 0.65, 0.8, 1.0} at n_test = 8000 from a frozen power calculation, τ ∈ {0, 0.1, 0.3} declared inside-band by construction; F: 20 % within-train probe giving `ê` (≈ 810 unseen training rows) and the retention fraction `ρ̂_s` (disputed probe rows), admissibility band, 0.95 shown inside-band by construction on digits (≈ 7 600 queries needed, 1 797 rows exist); cost-charged parents: 3-fold CV (12 F / 15 B extra fits) and free holdout selection (F) | billy-laptop, freeze `03a2fea8` | `microscopes/results/real_transfer_rv194/` 96/96 | frozen logic `REAL_TRANSFER_PHASE_LAWS_PARENT_SUFFICIENT_CV` (K5 on F; see below) |

Document: `GMI_REAL_TRANSFER_RV_377_194_FREEZE.md` (+§8). Ledger row 85 of `REVIVAL_LEDGER.jsonl`.

## Per-cell record

| lane | cell | class | predicted | observed | agree | band-in | verdict | law / CV right |
|---|---|---|---|---|---|---|---|---|
| B | τ 0.0 | BAND | SHARED 7 | SHARED 8 | 7/8 | 0 | INSIDE_BAND_BY_CONSTRUCTION | 7 / 8 |
| B | τ 0.1 | BAND | SHARED 5, SPEC 3 | SHARED 8 | 5/8 | 1 | INSIDE_BAND_BY_CONSTRUCTION | 5 / 6 |
| B | τ 0.3 | BAND | SHARED 4, SPEC 4 | SPEC 6 | 4/8 | 2 | INSIDE_BAND_BY_CONSTRUCTION | 4 / 4 |
| B | τ 0.5 | OFF | SPEC 8 | SPEC 8 | 8/8 | 0 | GREEN (+0.049) | 8 / 7 |
| B | τ 0.65 | OFF | SPEC 8 | SPEC 8 | 8/8 | 0 | GREEN (+0.222) | 8 / 8 |
| B | τ 0.8 | OFF | SPEC 8 | SPEC 8 | 8/8 | 0 | GREEN (+0.559) | 8 / 7 |
| B | τ 1.0 | OFF | SPEC 8 | SPEC 8 | 8/8 | 0 | GREEN (+0.795) | 8 / 8 |
| F | a 0.6 | OFF | EXPANSION 8 | EXPANSION 7, NONE 1 | 7/8 | 1 | GREEN | 7 / 5 |
| F | a 0.8 | OFF | EXPANSION 8 | EXPANSION 8 | 8/8 | 0 | GREEN | 8 / 5 |
| F | a 0.9 | OFF | EXPANSION 8 | EXPANSION 8 | 8/8 | 0 | GREEN | 8 / 5 |
| F | a 0.95 | BAND | REPLAY 5, EXPANSION 3 | REPLAY 6, EXPANSION 2 | 5/8 | 3 | INSIDE_BAND_BY_CONSTRUCTION | 5 / 2 (holdout 6) |
| F | a 1.0 | OFF | REWRITE 8 | REWRITE 8 | 8/8 | 0 | GREEN | 8 / 8 |

Cost-charged: off-band the law is right 63/64 (B 32/32, F 31/32) at 0 extra fits; 3-fold CV 53/64 (B 30/32, F 23/32)
at 15 / 12 extra fits per replicate (F: 4.1–4.6 s vs 0.01–0.02 s). At the crossovers: law 21/32, CV 20/32, free
holdout 6/8 (F). The F law names the free holdout parent's winner on 37/40.

**On the frozen terminal.** Kill K5 ("law ≠ CV on > 10 % of off-band replicates → PARENT_SUFFICIENT_CV") fired on F
(24/32 same winner). All eight differing replicates are CV errors: CV named NONE (EXPANSION old accuracy under the 0.95
bar on 2/3-size folds) where the law named EXPANSION and EXPANSION won. The kill measured agreement with CV, not
correctness against it; it is a specification defect recorded in the freeze §8.2 and not repaired by re-scoring. The
frozen label is carried as computed; the substantive reading from the same receipts is stated beside it everywhere.

## Residual classification, V9

| class | V8 status | V9 status |
|---|---|---|
| 1. INDEPENDENT-EVIDENCE | unchanged (IG-4, IG-5 pending) | **unchanged** |
| 2a. LEARNING-SCALE EMPIRICAL, REGISTERED SCOPE | executed; result gap where RED | **unchanged** |
| 2b. LEARNING-SCALE EMPIRICAL, MODERN SCALE | untouched | **unchanged** |
| 3. REAL-TRANSFER | tested as phase laws on real learners, same-author; laws equal CV where decidable, lose at crossovers | **CROSSOVER CELLS RE-TESTED OFF-BAND WITH THE LEARNER-CLASS TERMS.** B (heterogeneity): with the mass-weighted variance term the law is GREEN on all four off-band cells (32/32, 0 opposing) and predicts the objective gap to within 0.05 on 25/32; the three low-heterogeneity cells are inside-band by construction and their misses are now descriptor-side (τ̂² from 7–17-row modes), the measured test band being 2× narrower than planned. F (overlap): with a within-train retention probe (`ρ̂_REPLAY` 0.38–0.51, `ρ̂_REWRITE` 0.95–0.97; 0.75 at a = 0.95) the law is GREEN on all four off-crossover cells and names REPLAY 5/8 at the crossover (the K5 midpoint rule: 0/8), right 5/8 vs CV 2/8 there; the 0.95 cell cannot be made off-band on digits (≈ 7 600 queries needed). Cost-charged: the laws are a free pre-outcome predictor right on 63/64 off-band replicates where 3-fold CV is right on 53/64 at 12–15 extra fits; the F law equals free holdout selection on the same probe (37/40). What remains: same-author only; crossovers undecided by any predictor at these descriptor sample sizes; fresh episodes/systems rather than datasets; modern scale; independent authorship. |
| 4. PHYSICAL-MEASUREMENT | evaluated from external published measurements at one registered obligation | **unchanged** |

## Terminals carried forward

Unchanged from V8:

`NO_KNOWN_UNTYPED_FORMAL_BLOCKING_GAP_IN_CURRENT_LEDGER = TRUE`
`NO_KNOWN_UNREDUCED_ORDINARY_CLASSICAL_DOMAIN_CANDIDATE_AT_REGISTERED_MATCHED_PRIMITIVE_SCOPE = TRUE`
`INTERNAL_FORMAL_AND_EXACT_MICROSCOPE_ASSAULT_EXHAUSTED_AT_CURRENT_REGISTERED_SCOPE = TRUE`
`KNOWN_FORM_ZERO_PRIOR_DERIVATION_GREEN_AT_REGISTERED_SCOPE = FALSE`
`NO_KNOWN_UNTYPED_OR_UNTESTED_BLOCKING_GAP_AT_REGISTERED_SCOPE = FALSE`
`LEARNING_SCALE_EMPIRICAL_CLASS_EXECUTED_AT_PROTECTED_TIER_REGISTERED_SCOPE = TRUE`
`K4_PROPERTY_PREDICTION_GREEN_AT_PROTECTED_TIER = FALSE`
`K5_HELD_FAMILY_RESPONSE_LAWS_GREEN_ON_6_OF_8_LANES_AT_PROTECTED_TIER`
`GRAMMAR_AXIS_NOT_VERDICT_INERT`
`REAL_TRANSFER_PHASE_LAWS_GREEN_ON_1_OF_3_LANES` (C, under the RV-377-190 all-cells rule; unchanged as a label)
`PHYSICAL_FRONTIER_SIGN_FROM_PUBLISHED_CONSTANTS__NOT_MEASURED_IN_PROGRAMME = PARENT`
`PHYSICAL_FRONTIER_FLIP_VARIABLES_NAMED_NOT_MEASURED = {d ≳ 10⁴ MACs/query, S ≳ 10¹⁰ pJ/query}`

Superseded in V9:

`REAL_TRANSFER_PHASE_LAWS_ADD_NOTHING_OVER_CV_WHERE_DECIDABLE` — **FALSE** as stated. B: same winner as CV on 30/32
off-band at zero extra fits (CV 15), the two differences in the law's favour. F: the law is more accurate than 3-fold
CV off the crossover (31/32 vs 23/32) and at it (5/8 vs 2/8), and equals free holdout selection (37/40).

New in V9:

`REAL_TRANSFER_PHASE_LAWS_FREE_PREDICTOR_RIGHT_ON_63_OF_64_OFF_BAND_REPLICATES__CV_53_OF_64_AT_12_TO_15_EXTRA_FITS`
`REAL_TRANSFER_CROSSOVER_CELLS_INSIDE_BAND_BY_CONSTRUCTION__UNDECIDED_BY_LAW_21_OF_32_OR_CV_20_OF_32`
`REAL_TRANSFER_RV_377_194_FROZEN_TERMINAL = REAL_TRANSFER_PHASE_LAWS_PARENT_SUFFICIENT_CV` (via a kill that scored
agreement with CV rather than correctness against it; defect recorded, label not re-scored)
`F_CONTINUAL_REAL_LAW_EQUALS_FREE_HOLDOUT_SELECTION = TRUE` (37/40; `PARENT_SUFFICIENT_HOLDOUT`)

The remaining gap is unchanged in kind: **independent authorship, modern scale, fresh real episodes/systems (not
datasets), and hardware constants measured on the study's own obligations.** Within same-author real data the
transferred laws now carry their learner-class terms and are decidable exactly where their descriptors resolve the
crossover; the binding limit at the crossover has moved from the protected test to the descriptors' own sample sizes.

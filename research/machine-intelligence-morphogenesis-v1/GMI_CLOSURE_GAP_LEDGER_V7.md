# GMI closure gap ledger v7 — protected learning-scale runs executed

Status: **LEARNING-SCALE EMPIRICAL CLASS RECLASSIFIED FROM UNTESTED TO TESTED-AT-PROTECTED-TIER; EXTERNAL GATES REMAIN**

Date: 2026-09-12. Successor to `GMI_CLOSURE_GAP_LEDGER_V6.md`, which is not edited. V6's terminals and the V1
real-transfer RED remain authoritative where this file does not name a successor.

## What ran between V6 and V7

Both protected same-author learning-scale experiments that V6 listed as the LEARNING-SCALE EMPIRICAL residual
were executed on LUNARC under execution freezes, unique no-reroll drand beacons and per-task receipts (PR #455):

| run | job | beacon round | tasks | terminal |
|---|---|---|---|---|
| K4 V7 (zero-prior recovery, 22 families x 4 cells x 3 grammars, budget 10^6) | 3605505 | 32138309 | 264/264 | `K4_V7_CONTAINS_THEORY_RED` |
| K5 V7 (held-family response laws, 8 lanes x 4 values x 8 replicates) | 3605249 | 32138625 | 256/256 | `K5_BH_V7_CONTAINS_RED` |

K4 V7: THEORY_RED 150, THEORY_RED_NULL_DOMINATES 76, INCONCLUSIVE_GRAMMAR 38, K4_RECOVERY_GREEN **0**.
Prediction A1 (0 of 264 recover) reproduced at protected tier. Prediction A2 (grammar axis verdict-inert 88/88)
**not** reproduced: 78/88 (family, cell) pairs agree across the three grammars; families K4-A09, A11, A18, A19,
A20 split.

K5 V7: B_ROUTING, B_SPECIALIZATION, B_RESIDUAL, B_COMPILE_SEARCH, D_GENERATIVE, F_CONTINUAL GREEN on all four
values; C_FEATURE_LEARNING THEORY_RED (nonlinear_signal 0.6: 0/8, mean margin -1.07); E_CONTROL INCONCLUSIVE
(goal_reuse 1/2/8 carry predicted-inadmissible replicates; 26/26 admissible replicates agree).

Revival of the two non-green K5 lanes: `GMI_K5_V7_REVIVAL_RV_377_170_FREEZE.md` (RV-377-170, RV-377-171). Both
attribute to the prediction stage (reachability clause dropped; admissibility term omitted). The V8 successor on
fresh grids is GREEN on both lanes at development tier (billy-old, 80/80) and at protected tier (LUNARC job
3605817, beacon round 32144246, 80/80, `K5_BH_V8_PROTECTED_GREEN`). Neither tier reopens the V7 verdicts.

## Residual classification, V7

| class | V6 status | V7 status |
|---|---|---|
| 1. INDEPENDENT-EVIDENCE | open, cannot be closed same-author | **unchanged** (IG-4, IG-5 pending) |
| 2. LEARNING-SCALE EMPIRICAL | untested: "large neutral search/training on untouched known families" | **TESTED AT PROTECTED TIER, SAME-AUTHOR.** The zero-prior recovery half is a protected structural negative (K4: 0/264 at 10^6, F1). The held-family response-law half is protected-positive on 6 of 8 lanes and revived on the remaining two under a corrected prediction. What remains in this class is no longer "run it" but (a) the four things the boundary theorem §6 names and (b) modern large-model scale, which no same-author synthetic run reaches. |
| 3. REAL-TRANSFER | V2 split finite-portfolio bound GREEN (calibration only) | **unchanged** |
| 4. PHYSICAL-MEASUREMENT | cannot be closed by symbolic work | **unchanged** |

Class 2 is therefore split into two sub-classes from V7 on:

- **2a. LEARNING-SCALE EMPIRICAL, REGISTERED SCOPE** — executed; both halves carry protected receipts. Closed as an
  *execution* gap; open as a *result* gap only where the receipts are RED (K4 entirely; K5 C at 0.6, E at 1/2/8).
- **2b. LEARNING-SCALE EMPIRICAL, MODERN SCALE** — untouched; requires compute and models outside the study's
  own synthetic worlds. Same standing as class 1: not closable by same-author symbolic work.

## Terminals carried forward

Unchanged from V6:

`NO_KNOWN_UNTYPED_FORMAL_BLOCKING_GAP_IN_CURRENT_LEDGER = TRUE`
`NO_KNOWN_UNREDUCED_ORDINARY_CLASSICAL_DOMAIN_CANDIDATE_AT_REGISTERED_MATCHED_PRIMITIVE_SCOPE = TRUE`
`INTERNAL_FORMAL_AND_EXACT_MICROSCOPE_ASSAULT_EXHAUSTED_AT_CURRENT_REGISTERED_SCOPE = TRUE`
`KNOWN_FORM_ZERO_PRIOR_DERIVATION_GREEN_AT_REGISTERED_SCOPE = FALSE`
`NO_KNOWN_UNTYPED_OR_UNTESTED_BLOCKING_GAP_AT_REGISTERED_SCOPE = FALSE`

New in V7:

`LEARNING_SCALE_EMPIRICAL_CLASS_EXECUTED_AT_PROTECTED_TIER_REGISTERED_SCOPE = TRUE`
`K4_PROPERTY_PREDICTION_GREEN_AT_PROTECTED_TIER = FALSE` (0/264, beacon 32138309)
`K5_HELD_FAMILY_RESPONSE_LAWS_GREEN_ON_6_OF_8_LANES_AT_PROTECTED_TIER` (non-green: C_FEATURE_LEARNING RV-377-170, E_CONTROL RV-377-171)
`GRAMMAR_AXIS_NOT_VERDICT_INERT` (78/88; the DG-11 exhibit now exists: K4-A09, A11, A18, A19, A20)

The remaining gap is unchanged in kind: **independent, modern-scale, real and hardware evidence** under the
frozen constitutions. Same-author synthetic learning-scale evidence has now been spent; its one positive
(6/8 K5 lanes plus the revived two on fresh grids) and its one structural negative (K4) are both on the record.

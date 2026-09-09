# FNA-6 working-state results (v1)

Freeze: FREEZE_FNA6_V1.json (sha256 281c4af24ad5e7f6)

## Terminal

- **PARENT_SUFFICIENT_FOR_working_state** — P1B_BLACKBOARD_VERSIONED, P2_SOAR_WM, P3R_ACTR_REVALIDATE

## Harness validation

- static no-alarm pass: True
- incumbent closure == production gated_closure: True
- mutant detected on stream: True

## Arms (48 decisions each; ops whole-lifecycle; loc = in-cone fraction, null in parentheses)

| arm | exact | wrong | stale-rev | merge-fail | interfer | ops | xP0 | peak-WS | bytes | loc (null) | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P0_INCUMBENT_ACTIVE_KSO | 48 | 0 | 0 | 0 | 0 | 156191 | 1.00 | 372 | 18995 | 1.0 (0.9159) | - |
| P1A_BLACKBOARD_APPEND | 45 | 3 | 1 | 1 | 3 | 9590 | 0.06 | 375 | 94085 | 1.0 (0.8949) | - |
| P1B_BLACKBOARD_VERSIONED | 48 | 0 | 0 | 0 | 0 | 66847 | 0.43 | 372 | 94405 | 1.0 (0.9029) | - |
| P2_SOAR_WM | 48 | 0 | 0 | 0 | 0 | 35689 | 0.23 | 372 | 3026 | 1.0 (0.8966) | - |
| P2_MUTANT_NO_GOAL_BINDING | 35 | 13 | 3 | 3 | 13 | 35636 | 0.23 | 372 | 3016 | 1.0 (0.8927) | - |
| P3_ACTR_STRICT_BUFFERS | 45 | 3 | 1 | 1 | 0 | 8598 | 0.06 | 372 | 141009 | 1.0 (0.9061) | - |
| P3R_ACTR_REVALIDATE | 48 | 0 | 0 | 0 | 0 | 261105 | 1.67 | 372 | 149333 | 1.0 (0.9039) | - |
| P4_FULL_RESCAN | 48 | 0 | 0 | 0 | 0 | 10707370 | 68.55 | 0 | 2 | 1.0 (0.9158) | STATE_SEARCH_COST_DOMINATES |

## Engineering chain (pre-registered levers)

- L1_blackboard_versioning: P1A_BLACKBOARD_APPEND (sufficient=False) -> P1B_BLACKBOARD_VERSIONED (sufficient=True)
- L2_actr_retrieval_revalidation: P3_ACTR_STRICT_BUFFERS (sufficient=False) -> P3R_ACTR_REVALIDATE (sufficient=True)

## Superseded defect runs

- run 1 (2026-09-09) SUPERSEDED_DEFECT_RUN — static no-alarm control failed: P2_SOAR_WM 45/48 on the scored stream; P3R_ACTR_REVALIDATE 46/48 and P3_ACTR_STRICT_BUFFERS 40/48 on the static control. Root causes and remedy recorded in RESULTS_FNA6_V1.json; freeze, salts, stream and thresholds untouched.
- run 2 (2026-09-09) SUPERSEDED_DEFECT_RUN — all decisions, costs, bytes, locality and terminals valid, but the working-set-occupancy instrument was dead: no arm ever called the resident hooks, so working_set_peak read 0 for every arm in the printed table. Root causes and remedy recorded in RESULTS_FNA6_V1.json; freeze, salts, stream and thresholds untouched.

## Stream

- 48 serves (12 supported / 36 not), 13 updates (6 admissions / 6 revocations / 1 drift), 28 admitted edges


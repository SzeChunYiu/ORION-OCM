# 07 — Absorption ledger: ORION v1 and v2 inside the machine

Directive (#284, comment 5543833893): every artifact gets a disposition and the machine carries the
receipt. Dispositions: `ABSORBED_AS_CODE` (parity test) · `ABSORBED_AS_CONSTRAINT` (planted violation
+ no-alarm) · `ABSORBED_AS_BENCHMARK` (oracle wired) · `ABSORBED_AS_PARENT` (matched arm) ·
`NOT_TRANSFERABLE` (reason). `receipt` = where the proof lives or `[SPEC → Mn]`. Acceptance: zero
`UNMAPPED` at or below the current milestone (M1 today; M2 in flight).

## ORION v1

| artifact | component | disposition | milestone | receipt |
|---|---|---|---|---|
| `epistemic_atlas.py` — `ContextMapKind` vocabulary | edge types (01 §S3) | `ABSORBED_AS_CONSTRAINT` | M0 | `kso_m0_freeze_checks_v1` binds `T` to the enum; unregistered type rejected |
| `epistemic_atlas.py` — gluing / `HorizonStatus` / `UnknownKind` | obstruction-witness *type*; gluing = consistency constraint on overlapping charts | `ABSORBED_AS_CONSTRAINT` (gluing) + `ABSORBED_AS_CODE` (witness type) | M2 | `[SPEC → M2]`: witness object carries `UnknownKind`; planted inconsistent overlap rejected |
| the atlas' *static* locality maths as the reaction dynamic | — | `NOT_TRANSFERABLE` — the drift #194 names; replaced by τ1 | — | 03 §τ1 |
| `jump.py` — `JumpLevel`, `TriggerKind`, `JumpTrigger.is_admissible` | Jump operator, τ5 | `ABSORBED_AS_CODE` | M2 (binding) / M4 (operator) | four-valued outcome binds the witness to `is_admissible` (#295); operator `[SPEC → M4]` |
| Jump ladder J0–J8 (`JUMP_RESEARCH_PROGRAMME_V0.md`) | minimum sufficient level | `ABSORBED_AS_CONSTRAINT` (monotone level) | M4 | `[SPEC → M4]` |
| #558 `ExecutableRegimeWitness.v1`, 84 opaque worlds | first Jump benchmark | `ABSORBED_AS_BENCHMARK` | M4 | `[SPEC → M4]`: 48 positive / 36 control, oracle wired |
| knowledge metabolism (`knowledge_metabolism.py`) | τ2 consolidation + apoptosis | `ABSORBED_AS_CODE` where it maps to A9 / immune removal; else `NOT_TRANSFERABLE` (LLM-driven parts) | M3 | `[SPEC → M3]` parity on its own tests |
| `structural.py` checks | admission predicates | `ABSORBED_AS_CONSTRAINT` | M2b | `[SPEC → M2b]` |
| `ATOMIC_CLAIM_INVENTORY.json` schema | atom schema (01 §S5) | `ABSORBED_AS_CODE` (generalised: claims / constraints / procedures / representations) | M0 | contract §2; M1 atom kinds |
| P-A structural donor discovery; P-B context-relative transport | Jump sources; cross-region navigation | `ABSORBED_AS_PARENT` (evidence) | M4 | closed papers; `[SPEC → M4]` |

## ORION v2

| artifact | component | disposition | milestone | receipt |
|---|---|---|---|---|
| RCL / S1–S7, Theorem S4, RCL profile = ATMS label (#203) | genome `Σ`; label type | `ABSORBED_AS_CONSTRAINT` | M0/M1 | seven predicates on `𝒦`, planted violations, digest unchanged by population (#295) |
| `ocm_reference_semantics.py` (record-store semantics) | executable substrate | `ABSORBED_AS_CODE` | M1 | `[SPEC → M2]` parity: same S1–S7 verdicts on the record store and the hypergraph for the n=4 exhaustive set |
| `rcl_checks_v1.py` (three VACUOUS_CONTRAST repairs) | immune system | `ABSORBED_AS_CONSTRAINT` | M0 | exists; classes carried into `OCM_FAILURE_LEDGER.md` |
| ME-X1 generator / oracle / parents | domain, oracle, comparator | `ABSORBED_AS_BENCHMARK` + `ABSORBED_AS_PARENT` | M1/M2 | M1 receipt (50 worlds); comparator `[SPEC → M2]` |
| ME-X4 generator / oracle | second exact domain | `ABSORBED_AS_BENCHMARK` | M2 | `[SPEC → M2]` |
| FM10/20/30 exact suites (F0 = oracle identity) | positive-control arm | `ABSORBED_AS_BENCHMARK` (F0 as the oracle arm of A14) | M2 | `[SPEC → M2]` |
| FM40/50/60 protected suites | invariance / functoriality / obstruction domains | `ABSORBED_AS_BENCHMARK` (FM60 = obstruction-discovery domain for KS-T19) | M2/M4 | `[SPEC]`; three `PARENT_SUFFICIENT` terminals already on main (#283) |
| ME-X2 locus + minimum escalation (0 false escalations) | Jump level gate | `ABSORBED_AS_CONSTRAINT` | M4 | `[SPEC → M4]` |
| ME-X6 V3 "typing is a coverage prior" | KS-T18 | `ABSORBED_AS_CONSTRAINT` | M0 | #295 checker |
| H-EXT-1 / H-EXT-1R escalation rule | KS-T19 obstruction witness | `ABSORBED_AS_CODE` | M0 | #295 four-valued outcome (ceiling-walker rule) |
| E40 ranker (recovers 0.41; RS1 p=0.0585) | `r_Q` ranking parent / candidate `η_Q` prior | `ABSORBED_AS_PARENT` | M2 | `[SPEC → M2]` arm in A14 |
| E30-R14 boundary contract + `anchored_edit_interface.py` | codec boundary | `ABSORBED_AS_CODE` | M5 | `[SPEC → M5]` |
| FG80 R3 / ME-F1 R3 (deferred on channel) | whether the frontier negative was an interface artifact → codec design input | `ABSORBED_AS_PARENT` (evidence) | M5 | armed on billy-old; result feeds 06 codec contract |
| ME-X3 Lean cross-check (20/20) | EXACT_CHECKER channel | `ABSORBED_AS_CODE` | M6 | `[OPEN_M6]` adapter |
| SD70-V3 meta-policy | navigation-policy candidate (`η_Q`, `α` schedule) | `ABSORBED_AS_PARENT` | M2 | campaign running |
| PRA V2 revision-adequacy | τ3 test bed | `ABSORBED_AS_BENCHMARK` | M3 | arm 1 running |
| `FAILURE_LEDGER.md` (27) + `OCM_FAILURE_LEDGER.md` | immune system catalogue | `ABSORBED_AS_CONSTRAINT` per class | all | table below |
| parent-strength audit (14 faithful parents) | 08 | `ABSORBED_AS_PARENT` | M0 | `KSO_PARENT_SUBTRACTION_V1.md` |
| freeze / seed-commitment / protected-run discipline | run protocol | `ABSORBED_AS_CONSTRAINT` | all | `KSO_M0_FREEZE_V1.json`; self-digest assertion |
| B5 information- and budget-matched federation | comparator harness | `ABSORBED_AS_CONSTRAINT` (KS-T17) | M2 | #295 budget clause |
| LLM-centred controller code (v1/v2 harness controllers) | — | `NOT_TRANSFERABLE` — the LLM is a codec or a comparator arm, never store/solver | — | #284 unbundling |

## Failure classes → checkers on the machine

| class (ledger) | checker on the machine | tag |
|---|---|---|
| counter never ran (`0 violations`) | every checker ships with its planted failure; replay adds independent plants | `[MACHINE]` |
| contrast that could not exist (`1.000 vs 1.000`) / VACUOUS_CONTRAST | power assertion: a claim family with zero negatives reports `NO_POWER` (the #295 constraint-edge fix) | `[MACHINE — being fixed]` |
| sentence nobody executed / REPAIR_DOCUMENTED_NOT_LANDED | receipt self-digest must match the file; CI asserts it | `[MACHINE — #295 fix]` |
| rendered status trusted in place of the thing | receipts carry values, not labels; the gate reads values | `[MACHINE]` |
| STRUCTURALLY_DETERMINED_REGISTERED_CLAUSE | every gate must have a reachable failing outcome; planted-failure requirement | `[MACHINE]` |
| HANDICAPPED_COMPARATOR | parents run on the same `(𝒦, s_Q, B)`; renormalised PPR kept *as the parent* so the delta is visible | `[SPEC → M2]` |
| INTERFACE_ASKS_FOR_WHAT_IT_WITHHELD | codec contract: request atoms must be bound or typed-rejected before navigation | `[SPEC → M5]` |
| FREE_TEXT_CATEGORICAL_ENDPOINT | answers are structured objects scored by oracle/checker; text is render-only | `[MACHINE (M2 design)]` |
| frame error (instrument validated, frame wrong) | replay's FRAME check: independence of the reachability used by the retraction checker | `[MACHINE]` |
| stale pin / cited quantity absent at pin | pin-vs-citation audit (portfolio) | `[SPEC — lane-guards]` |

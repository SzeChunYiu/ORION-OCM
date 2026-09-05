# M11 — Self-model, diagnosis and governed self-reorganisation

Milestone issue: #13. Evidence: `research/ocm-m11/M11_SELF_EVAL_V1.json` (bound by
`docs/provenance/M11_RECEIPT_V1.json`). Obligations: `docs/theorems/OCM_SELF_OBLIGATION_REGISTRY_V1.json`
(KS-T96…T103). Self-application rows: ledger S29–S30.

## 1. What was built

| Object | Module | Content |
|---|---|---|
| Self-model fibre | `src/ocm/selfmodel/model.py` | components with fingerprints and lineage; every self-statement is an OBSERVATION in scope `self` with authority `self_model=1` only; `self_authority_never_raises_object` is the meet with the object authority (never rises); FailureRecord with ablation evidence |
| Diagnosis | `src/ocm/selfmodel/diagnose.py` | a distribution over layers D0–D8 from counterfactual evidence (UNKNOWN when none), the minimum-sufficient layer, an architecture alarm only under a valid ObstructionCertificate (all registered lower alternatives tried with LIVE warrants and failed, plus a ceiling witness); escalation rule |
| Proposals | `src/ocm/selfmodel/proposal.py` | SelfChangeProposal.v1 with change classes C0–C6 (C6 constitutional = recommendation packet only), pre-outcome Prediction digest, origin (existing / transfer / recombination / learned / ORION-V2 import / human), proposal-only authority; protected targets (adoption, assurance, meter, authority, constitution) |
| Governance | `src/ocm/selfmodel/govern.py` | shadow evaluation with object-level non-interference, fresh assurance checks (protocol hash, invariants, no leakage, preservation, reopened marked, budget, rollback artifact, prediction realised), ExternalAdopter as the only adoption path (self-approval has no token and is refused), metered adoption ledger with a per-window budget, migration plan, exact rollback with stamped-evidence revocation, monitoring triggers |
| Benchmark | `src/ocm/selfmodel/benchmark.py` | S0 control + S1–S7 planted causes on the M9 enterprise environment; parents: parameter search over router/revocation, reflection-retry over skills |
| Replay | `src/ocm/selfmodel/replay.py` | ledger rows S11–S28 as recorded FailureRecords with the attributed layer and the shipped class |
| Intake | `src/ocm/selfmodel/intake.py` | ORION-V2 → OCM intake records (theorem → obligations → defect → fix ref) and OCM → ORION-V2 exports (runtime gaps the theory does not cover) |

## 2. Controlled benchmark (S0–S7)

Target suite = 6 urgent cases; preservation suite = 6 non-urgent cases (built from protected
state the machine never reads). The self-model receives an ablation channel (one-layer
counterfactual runs); the parents receive the same environment and no diagnosis object.

| Scenario | True layer | Diagnosed | Class | Escalation | Target | Preservation | Broad rewrite | Rollback |
|---|---|---|---|---|---|---|---|---|
| S0 no-fault control | none | none (no FailureRecord, no proposal) | — | — | 6/6 | 6/6 | — | — |
| S1 router fault | D1 | D1 | C1 | refused (local) | 0/6 → 6/6 | 0/6 → 6/6 | — | exact |
| S2 operator fault | D2 | D2 | C2 | refused (local) | 0/6 → 6/6 | 0/6 → 6/6 | — | exact |
| S3 representation ceiling | D3 | D3 | C3 | allowed under certificate; alarm | 0/6 → 6/6 | 6/6 → 6/6 | — | exact |
| S4 learning policy | D6 | D6 | C4 | refused (local) | 0/6 → 6/6 | 6/6 → 6/6 | — | exact |
| S5 false structural alarm | D2 | D2 (D7 also restores) | C2 | refused (local) | 0/6 → 6/6 | 0/6 → 6/6 | passes assurance, refused as not minimum | exact |
| S6 harmful Jump | D2 | D2 (D7 also restores) | C2 | refused (local) | 0/6 → 6/6 | 6/6 → 6/6 | refused: preservation 0/6, prediction not realised | exact |
| S7 environment drift | D2 | D2 | C2 | refused (local) | 0/6 → 6/6 | 6/6 → 6/6 | — | exact |

Summary over the seven fault scenarios: diagnosis 7/7, minimum class 7/7, false Jumps 0,
missed Jumps 0, assurance 7/7, adopted 7/7, target restored 7/7, preservation kept 7/7, rollback
exact 7/7, prediction realised 7/7, broad rewrites refused 2/2, control raised no proposal.
Parents (fault scenarios only): parameter search solves 2/7 (S1, S5), reflection-retry 1/7 (S1);
neither reaches an operator, representation, policy or drift fault.

## 3. Historical replay (S11–S28)

Recorded replay: outcomes re-read, code not re-executed, the layer is the ledger's attribution.
18 rows; shipped class never exceeded the minimum class for the attributed layer (18/18); 10 rows
at local layers; 8 rows escalated to D3/D4, each with a recorded ceiling witness (8/8, 0
CANNOT_CHECK). The replay audits governance (narrowness, witnesses); it says nothing about the
OCM's diagnostic accuracy on history, for which no ablation channel exists.

## 4. Claim-by-claim terminals

| Claim (issue #13) | Terminal | Basis |
|---|---|---|
| Self-statements never carry object authority | SUPPORTED (exact) | KS-T96 checker: meet with `self_model=1` never raises `world_truth`/`commit`; hostile `mutant_self_description_as_authority` caught |
| Diagnosis is a distribution with a minimum-sufficient level | SUPPORTED at n = 7 planted causes | 7/7 minimum layer; UNKNOWN reported for layers without evidence |
| No escalation without a valid certificate; dead-warrant failures are not obstructions | SUPPORTED (exact) | KS-T98: untried alternative, succeeded alternative, DEAD warrant and missing witness each invalidate; hostile `mutant_dead_warrant_obstruction` accepts the DEAD case |
| False structural alarms are avoided | SUPPORTED at n = 1 scenario (S5) | reinstatement at D2 is minimum; the D7 rewrite is refused as not minimum; recorded replay 0 false escalations at the governance level |
| Harmful high-level Jumps are refused | SUPPORTED at n = 1 scenario (S6) | refused on preservation and prediction, class rule second (ledger S29 records the first, vacuous, pass) |
| Adoption is external only; self-approval impossible | SUPPORTED (exact) | `mutant_self_approve` refused (no token); proposals touching protected targets refused at the meter |
| Rollback is exact and reopens dependents | SUPPORTED at n = 7 | component table restored, stamped evidence DEAD, object-level KS digest unchanged |
| Self-prediction calibration | SUPPORTED at n = 7 (pre-registered digest before outcome access) | `prediction_realised` 7/7; a tampered digest fails `no_leakage` |
| OCM vs parents on self-reorganisation | DESCRIPTIVE (n = 7, no pre-registered rate test) | OCM 7/7 vs parameter search 2/7 and retry 1/7; an inferential terminal needs the M7 discipline at n ≥ 40 planted causes |
| Diagnostic accuracy on real historical failures | CANNOT_CHECK | recorded replay only; no counterfactual channel for history |
| Constitutional (C6) self-change | NOT ATTEMPTED by design | recommendation packets only |

## 5. Limitations and revival backlog

* The benchmark is one environment (enterprise) with seven planted causes and one control; the
  ablation channel is oracle-provided. Revival: planted causes across all three M9 environments
  with n ≥ 40 and the ablation channel produced by the machine's own counterfactual runs.
* The parents are the two the issue names; a stronger parent (a learned failure classifier over
  traces) would need the same channel to be a fair comparison.
* The replay is recorded, not re-executed; the layer assignment is human attribution read
  through D0–D8. Reviving it means freezing the historical code at each row's commit and running
  the ablation channel there.
* The intake protocol is data plus an audit; the theorem → obligation mapping for batch 5 is
  IMPORTED, not DISCHARGED, until the batch lands.

## 6. M11.1 addendum — theory batch 5 intake

ORION-V2 theory batch 5 (E1–E8, PR #344) read this build and reported six side-condition defects
(ledger S34). All six are fixed with their hostiles in `tests/m11/test_batch5_defects.py`: the
proposer's dev tasks must be disjoint from the held-out suite (REFUSED_TASKS_SEEN_BY_PROPOSER);
the pre-outcome prediction is a K_self receipt admitted before the shadow, not a string; shadow
non-interference compares the ledger head as well as the object state hash (a runner that admits
evidence is caught); the adoption ledger owns the cache and asserts rollback exactness itself; the
meter is an object outside every proposal's write set with a nested-token refusal, a read-only
non-decreasing charge and the ⌊B/δ⌋ livelock bound; the architecture alarm has no frequency term
and an obstruction certificate is judged against the component registry's closure; failure records
are derived from their traces, so revoking a trace reopens the diagnosis. The S0–S7 benchmark
results are unchanged (the defects were invisible to it, which is the point of the intake).

## 7. M11.2 addendum — theory batch 6 intake

Batch 6 (ORION-V2 #347) added five obligations (KS-T110…T114, ledger S35): the F4 false-structural-alarm
lemma (a DEAD warrant on the path caps the layer at D2 and emits reinstate/reroute candidates), an
evidence-derived Jump assessment, ledger-chain identity, persisted adoption artifacts, and a
revocation reply that reports the live remainder of a word. All carry hostiles in
`tests/m11/test_batch6_obligations.py`. Benchmark results are unchanged.


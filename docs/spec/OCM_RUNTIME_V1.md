# OCM_RUNTIME_V1 — the unified executable KSO runtime (M2)

Status: **M2 consolidation of the inherited reference scripts into one stateful runtime over the M1 core. NO NOVELTY OR SUPERIORITY CLAIM.** Inherited terminals are replayed, never upgraded (M2 solve = `PARENT_SUFFICIENT`, novelty `NOT_ESTABLISHED`, protected splits `NOT_RUN`).
Issue: #4. Receipt: `docs/provenance/M2_RECEIPT_V1.json`. Obligations: `docs/theorems/OCM_RUNTIME_OBLIGATION_REGISTRY_V1.json` (KS-T25…T33; extends the frozen M1 registry). Vendored parents: `docs/provenance/VENDORED_SOURCE_MANIFEST_V1.json` (`tools/m2_vendor_check.py`). Gap ids MEG-nn: ORION-V2 `research/machine-epistemics-theory/ME_THEORY_GAP_ATLAS_V1.md`.

## 1. Runtime boundary (§1)

`ocm.runtime.ocm_runtime.OCMRuntime(root, *, commit_authority, config)` is the one long-lived object. It owns a `RuntimeState` (canonical `KnowledgeSpace`, certificates, revoked set, nogoods, `EvidenceRegistry`, `OperatorRegistry`, quarantine, learned objects, Jump proposals, meter) and a vendored crash-atomic `LedgerStore`. Public operations: `admit_evidence`, `admit_object`, `compose`, `register_operator`, `solve`, `navigate`, `learn`, `revoke`, `reinstate`, `reopen`, `propose_jump`, `commit_external_action`, `persist`, `replay`, `trace`. The commit authority is host-injected and held privately: no operator, learner or solver can reach it (capability non-distribution, MEG-04). Answers leave only through `solve`'s commitment gate; effects only through `commit_external_action`'s fixed sequence.

## 2. Canonical event model (§2)

`ocm.store.event.OCMEvent`: schema/runtime version · monotonic sequence · `prev_hash` · `event_type` (23 families: EVIDENCE_{ADMITTED,REVOKED,REINSTATED}, OBJECT_{ADMITTED,QUARANTINED,REOPENED}, RELATION_ADMITTED, QUERY_OPENED, NAVIGATION, EXTRACTION, CANDIDATE_COMPOSED, CHECKER_RESULT, LEARNER_UPDATE, SKILL_{PROMOTED,QUARANTINED}, REPRESENTATION_PROPOSAL, OPERATOR_REGISTERED, JUMP_{PROPOSED,ADOPTED,REJECTED}, ACTION_{INTENT,RECEIPT}, SNAPSHOT_WRITTEN) · status PASS | FAIL | CANNOT_CHECK | PROPOSAL · input/output object ids · evidence ids · operator fingerprint · seed · `observed_at` (logical time = sequence; no wall clock) · `resource_delta` (structurally non-optional; summed on replay, S7 over the log) · `expectation` (CAS tuple: log head, KSO state digest, registry revision, evidence epoch — four distinct errors) · payload. `event_id` is content-derived and never its own hash input. **KS-T29** (`store.event.verify_chain`; mutants `mutant_reorder`, `mutant_drop_resource_delta`).

Durability: the vendored `LedgerStore` (ORION `kernel/store.py` mechanics) — exclusive `flock`, stale-temp cleanup, temp-file + fsync + `os.replace` + directory fsync, compare-and-swap `expected_head` (`StaleLedgerHead`), `TransactionIdConflict`, `verify()`. Canonicalisation is versioned and Unicode-pinned (`store.canonical`).

## 3. Object / evidence store (§3)

`ocm.store.evidence.EvidenceRegistry`: eight channels (`Channel` → `CertificateKind` one-to-one; FEEDBACK never warrants), content-bound ids (`ids.evidence_id`), scope, authority, status, revocation state. **Dependence structure (MEG-01, KS-T33):** `E = A ⊔ D`; derived evidence carries its own interval so a citation's warrant is `⊗` of the cited intervals; revocation is assumption-only; `independent_support_count` never counts a shared assumption twice. §3.3 behaviours are distinct outcomes: `DUPLICATE_BYTES`, `DUPLICATE_CONTENT`, `CONTRADICTION` (registers a **nogood**, KS-T25), `OVERLAP`, `SUPERSEDED` (old epoch closed, history kept), `REVOKED_SOURCE_REAPPEARED`. No majority vote (`mutant_majority_truth`).

**Nogoods (MEG-16, KS-T25, `kso.nogoods`).** `filter_𝒩` commutes with ⊕, is a sub-homomorphism for ⊗ (apply after composition; the before-compose mutant lets a composite survive on a nogood), never revives DEAD; a violated CONSTRAINT's nogood kills every composite over both claims. Exhaustive at n=3 (22 families; 8,800 join commutations; 294 strict ⊗ cases; 70,400 Kleene checks).

## 4. Unified state, restart invariant (§4)

`RuntimeState.snapshot()` is deterministic; `kso_state_hash`, `registry_revision`, `evidence_epoch` are canonical digests. The reducer `_apply` is the single writer: every mutation is emitted first (expectation = state before) and then applied, so replay recomputes the identical digests and refuses a stale commit (`Stale*` errors). `persist()` writes a `SNAPSHOT_WRITTEN` event plus a snapshot row; `OCMRuntime(root)` replays and asserts the recorded digest. Tests: run → persist → load → same state; learn → use → revoke → persist → restart (still revoked) → reinstate → restart (recovered) (`tests/m2/test_ocm_runtime.py`).

## 5. Canonical solve loop (§5)

`ocm.runtime.solve.solve`: TASK → GROUNDING (typed parts bound to atoms; `UNBOUND_SEED`, `NON_ATOMIC_INPUT`) → REPRESENTATION → NAVIGATION (warranted + exploratory fixed points, four-valued targets, obstruction witness, non-identifiability) → EXTRACTION (reacting subgraph under the configured surprise model; bounded exact PCST with ties reported, greedy arm flagged) → EXECUTION (three-valued enabling) → COMPOSITION (applicable operators simulated via registered backends; candidate warrant = ⊗) → CHECK (a missing checker is CANNOT_CHECK, never success) → DECISION ∈ ANSWER | ACT | LEARN | CLARIFY | UNKNOWN | JUMP_PROPOSAL | CANNOT_CHECK → COMMITMENT (LIVE warrant ∧ task authority ≤ operator ∧ external commit authority ∧ scope coverage; any CANNOT_CHECK in the trace refuses). Every stage is a `StageResult` with a resource delta; the runtime binds stages to events.

**M2.1 revival (MEG-07, KS-T28).** The frozen surprise model lost 12/50 decisive atoms on the dev split; the receipt's own lever (seed-count-conditioned background) is proved inert by linearity of the fixed point; the registered `SurpriseModel.PROPAGATED` (propagated mass vs propagated background) recovers 47/50 with all four pre-registered guards held (`research/ocm-m2/M2_1_SURPRISE_REVIVAL_OUTCOME_V1.md`). The default stays UNIFORM until the M2 receipt is re-run with the model as a declared parameter.

## 6. Learning loop (§6)

`ocm.learning.learner`: `Experience` (INSTRUCTION, DEMONSTRATION, INTERACTION, EXPERIMENTATION, FEEDBACK) → `UpdateProposal` (OBJECT | BEHAVIOUR | QUARANTINE; status PASS | FAIL | CANNOT_CHECK | GAP_AMBIGUOUS | GAP_INSUFFICIENT | CONTRADICTION) → `OCMRuntime.learn` (admission through `kso.admission` only). Reference learner: version space over a finite registered class with the **agreement-on-the-registered-query-family** rule (MEG-13 finite half). Feedback yields BEHAVIOUR proposals only, unless a `FeedbackContract` routes it as an OBSERVATION of a registered outcome function (MEG-15). Hostiles: ambiguous stays unresolved; contradiction preserved (+ nogood); insufficient never promotes; promoted skill generalises on held-out composition; revoking an essential lesson reopens it while unrelated skills stay live; relearning keeps lineage (**KS-T31**).

## 7. Operator / skill registry (§7)

`ocm.operators.registry`: `OperatorSpec` (id/version/fingerprint, backend kind PROGRAMMATIC | SEARCH | STATISTICAL | PROOF | EXTERNAL_TOOL, inputs, preconditions, effects, warrant, authority, scope, checker, known failures, lineage, resource model). **MEG-02 (KS-T27):** STATISTICAL/neural outputs enter as `⟦0,U⟧` (UNKNOWN) with the score outside the lattice; a candidate becomes LIVE only through an exact-checker certificate or a **scoped `CoverageCertificate`** (EXPERIMENTATION-channel claim about the operator, its evidence id the bridge warrant, scope recorded); outside the scope it stays UNKNOWN; all-UNKNOWN components never compose LIVE; EXTERNAL_TOOL requires an `ActionIntent`. Mutant: `mutant_score_promoted_to_warrant`. **Procedure algebra (MEG-10, KS-T26, `kso.procedures`):** `;`, `⊗_w`, `if`, bounded loop with TRACE vs STATIC warrant readings (static ≤ trace; LIVE(static) ⇒ LIVE(trace); iteration idempotent; guard composes with the taken branch in the trace reading); a `LearnedProcedure` records its reading.

## 8. Governed Jump interface (§8)

`OCMRuntime.propose_jump(JumpProposal)` runs `assess_jump` (byte-identical parent copy) and records `JUMP_PROPOSED`; adoption is never performed by the runtime (C8 external). The solve loop's `OBSTRUCTION_WITNESSED` and `STRUCTURAL_NONIDENTIFIABILITY` witnesses bind to `JumpTrigger` and are recorded as proposals only. Hostiles (Jump without obstruction; lower-level repair available) are caught by `JumpTrigger.is_admissible` / `assess_jump` and the vendored `orion_v2.epistemic_architecture.route_frontier_action`.

## 9. External action / constitutional boundary (§9)

`ocm.constitution.action`: `ActionIntent`, `ActionReceipt` (EXECUTED | REFUSED | FAILED | UNKNOWN | CANNOT_CHECK), `CommitAuthority` protocol, `StaticCommitAuthority`. `ocm.constitution.boundary.commit_external_action` runs one fixed sequence: intent logged (PROPOSAL) before any effect → warrant liveness of the supporting objects → vendored `evaluate_hard_gates` against a contract frozen at an earlier round (`permits_closure` is the only boolean; no evidence ⇒ CANNOT_CHECK; conflicting observations ⇒ FAIL) → external authority decides → execute only if LIVE ∧ PASS ∧ granted → receipt logged. **KS-T30**; mutants `mutant_skip_gate`, `mutant_self_granting_authority`; `internal_authority_has_no_commit` (undeclared coordinate = bottom, MEG-04).

## 10. Unified trace (§10)

Events reference real object/evidence ids (`OCMEvent.input_object_ids`, `output_object_ids`, `evidence_ids`); `OCMRuntime.trace()` returns them. The vendored `runtime.trace.TraceEvent`/`SolveTrace` (ORION `engine/trace.py`, operator vocabulary swapped) cross-validate receipt ↔ transition and enforce a state-hash chain — the catcher for "trace claims an operator ran when it did not". Layers TASK … COMMITMENT are the `solve.Stage` enum.

## 11. Multi-domain non-interference (§11)

Replayed through the runtime: learn a procedure; admit a Lean-certified proof atom (EXACT_CHECKER, scope `math`); revoke the procedure's evidence → proof stays LIVE; reinstate; revoke the proof certificate → procedure stays LIVE; persist/restart between steps. Shared-support interference is MEG-22 (theory batch).

## 12. Historical replay (§12)

`ocm.evaluation.historical.replay_all`: eight adapters (M0 math, M1 population fixture, M2 solve/parent tie, M3 exact procedure learning, M4 governed finite Jump, M5 controlled codec chat, M6a Lean admission, multi-domain) reproduce the inherited terminals exactly (8 PASS); a source that cannot be replayed reports a named CANNOT_CHECK (Lean rerun).

## 13. Performance / resource baseline (§13)

`ocm.evaluation.scaling` on synthetic typed hypergraphs (engineering baseline, not a benchmark): `research/ocm-m2/M2_SCALING_BASELINE_V1.json`. Sparse float navigation (`kso.navigation_sparse`, **KS-T32**, agrees with the exact solver to 1e-14 on small spaces) runs 10⁴ atoms / 3·10⁴ hyperedges in 0.66 s (51 iterations) with 61 MB peak; reopening 0.11 s; admission above 200 atoms uses the sparse reachability path. Exact rational solving remains the authority for receipts.

## 14. Hostiles (§14) — where each is caught

| hostile | caught by |
|---|---|
| stale in-memory state differs after restart | replay digest check + `Stale*` expectations (`test_ocm_runtime`) |
| revoked object returned through an index | KS-S3 + un-renormalised gated seed + prune equivalence (M1) |
| duplicate evidence collision | `EvidenceRegistry` outcomes; `ids.IdentityCollision`; `evidence_identity` dual fingerprints |
| event log order corruption | `verify_chain` + `LedgerIntegrityError` (`mutant_reorder`; on-disk swap test) |
| checker CANNOT_CHECK promoted to success | `solve.check_stage` + `hard_gates.evaluate_hard_gates` |
| feedback-only skill promoted | `WARRANTING_KINDS`, KS-S1, learner BEHAVIOUR-only, `RuntimeRefusal("ZERO_WARRANT_OBJECT_PROPOSAL")` |
| unauthorized external commit | boundary fixed sequence; `NO_COMMIT_AUTHORITY_INSTALLED`; `mutant_skip_gate` |
| Jump without obstruction | `JumpTrigger.is_admissible`; `assess_jump`; runtime never adopts |
| cross-domain revocation leakage | impact cone + non-interference replay |
| trace claims an operator ran when it did not | events carry object ids; vendored `TraceEvent` cross-validation |
| result cache ignores evidence epoch | `EventExpectation.evidence_epoch` CAS |
| resource meter omitted from a committed event | `resource_delta` structurally required; `mutant_drop_resource_delta` breaks the hash |

## 15. Exit (§16)

All M2 exit criteria are held by the tests in `tests/m2/` (108 including the vendored suites), the exhaustive checkers, the historical adapters and the receipt; CI: `.github/workflows/m2-unified-runtime.yml`. Terminal on green: `M2_UNIFIED_RUNTIME_GREEN`. Not claimed: any cognition benchmark, any protected split, any novelty.

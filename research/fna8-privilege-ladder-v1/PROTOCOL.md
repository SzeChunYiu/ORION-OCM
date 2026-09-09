# FNA-8 / D9 protocol — PrivilegeLadderProtocolV1 (frozen before execution)

**Issue #214 work package FNA-8, deliverable FNA-D9. Base commit
`ab5310942b01be11776c0eddc4403dc0e0dcb51c`. Research-only: production `src/` untouched,
no agent deployed, no #165 box touched, no issue/PR writes from the capsule.**

## What this protocol is and is not

#214 §4 FNA-8 registers a staged model-privilege ladder to be run **only after causal
functional replacements exist**. This capsule therefore delivers the measurement
instrument first: `PrivilegeLadderProtocolV1` — the exact authority boundary, held-constant
harness, OCM-side mechanism list, rung-transition gate, 7-axis whole-lifetime cost ledger,
capability-preservation margin and honest-terminal tree for each of the six rungs — and
then executes the instrument **to the extent current-main artifacts permit**:

- **Rung 6** (bounded domain, no frontier model as central cognition) is fully executable
  today: pure OCM arms over the frozen world WL1 (built additively on the #72-owned
  incumbent surfaces `OperatorSpec` / `SolveOperatorIndex.select()`).
- **Rung 1** (LLM controls + OCM records) is executable as an instrumented **shadow
  micro-execution** on a frozen task set: real frontier-model calls (gpt-5.5 via the pinned
  local codex CLI, 0.129.0-alpha.15, config frozen below) on laptop billy. Model outputs
  are recorded, never fabricated; parse failures are charged control failures.
- **Rung 2** (LLM proposes, OCM selects/commits) is executable the same way: the model
  proposes, the incumbent exact machinery selects and commits.
- **Rungs 3–5** are NOT executed: their activation gate (below) is unmet on current main.
  They are recorded `RUNG_PENDING_ACTIVATION_GATE`, claiming nothing.

Evidence class: one authored task world, one population, one author — E1/L1, like FNA-1
and FNA-5. Nothing here licenses deployment or any #165 unlock. No terminal from #214 §7
is emitted from MOCK-mode receipts, and no forbidden collection token
(`TRANSFORMER_REPLACED`, `LLM_EQUIVALENT`, `AGI`, `GENERAL_SUPERIORITY`) appears anywhere.

## The ladder (verbatim from #214 §4) and each rung's contract

```text
R1  LLM controls + OCM records
R2  LLM proposes, OCM selects/commits
R3  OCM plans, LLM supplies candidate code/text
R4  OCM plans + learned operators, model is occasional donor
R5  model limited to interface/language proposal
R6  bounded domain with no frontier neural model as central cognition
```

### Held-constant harness H* (all rungs)

World WL1 (`fna8_world.py`): seeded obligation stream over weighted atoms; task types
AGG (report exact weighted mass) and THRESH (mass vs threshold, seeded boundary band);
operator catalogue with exact families (scan always-applicable; probe anchor-conditional
through the real `SolveOperatorIndex.select()`) and approximate families (window/sample
with declared success laws; realized constants are seeded draws around declared centres);
exact O(slice)-certificate checker (failures always caught, never delivered);
portfolio-recovery fallback to scan, charged. Frozen windows: EVAL (protected),
DRIFT_EVAL (catalogue mutation: window:40 removed, sample:24 added, scan ×1.6; index
rebuild billed to everyone), REV (frozen evidence revocation of one atom; affected
queries re-answered — and, on model rungs, **re-asked**, measured not derived). Splits by
salted hash, disjoint by construction. Model arms see at most 24 EVAL + 8 REV queries
(frozen caps). Determinism: all seeds md5-derived from the frozen salt, sorted iteration
only, no `hash()` dependence.

### Per-rung authority boundary

| rung | the model MAY | the model MAY NOT | OCM side |
|---|---|---|---|
| R1 | choose the operator; compute and deliver the answer itself; fail (charged) | see realized constants, split membership, labels, checker internals, fallback re-selection | records every call/decision/check/commit (append-only `Recorder`); executes the chosen operator's counted work; never selects; exact checker grades the model's answer; scan fallback on failure |
| R2 | propose a ranked candidate list (≤3 ids) | compute or supply the committed answer; commit | incumbent machinery: structural applicability via the real index, attempts in proposed order, first checker-correct result commits; scan fallback; all attempts charged |
| R3 | supply candidate code/text for operator bodies | choose instances, plan, commit | incumbent planning (obligation trajectory over the #72 stages); candidates only enter through the checked admission path |
| R4 | occasional donation when the donor gate concedes | be the standing supplier | plans + learned operators (FNA-4/D6 parents); every donation charged and counted |
| R5 | propose interface/language (names, signatures, grammar) | supply semantics, answers, selection | all semantics OCM-side; proposals enter through checked grammar/interface admission |
| R6 | — no frontier model anywhere in the loop — | — | bounded domain solved by exact/analytic machinery only |

### OCM-side mechanisms required per rung (first-refusal parents bind)

- R6 arms: **A1_INCUMBENT** first-PASS in catalogue order (the incumbent
  `compose→check→decide` policy — clean baseline, never degraded); **A2_GUARDED** the
  analytic guarded parent (cheapest exact by declared cost within tolerance 2.0× of the
  cheapest approximate estimate; re-derived from the declared spec at zero label cost —
  binding #219's guard-first conclusion and its acquisition-price economics);
  **A0_ORACLE** executes all applicable and commits the cheapest correct — labelled
  upper bound, never a result.
- R2's select/commit is the incumbent `SolveOperatorIndex` + exact-certificate +
  first-PASS-commitment semantics; binding #222 (FNA-6, PR open at freeze) for the
  working-state parent that holds the proposal stream between call and commit.
- R3–R5 bind (by contract, not execution): #215 typed indexes (FNA-1) for retrieval,
  #218 minimum-sufficient classical parents, #219 guard-first routing, #222
  blackboard/working-state parents, FNA-3/D5 and FNA-4/D6 suites once they land.

### Rung-transition gates (what authorizes stepping DOWN a rung)

Every transition requires, on the frozen task set: (a) delivered-correct ≥ 1 − ε at the
lower-privilege rung (capability preservation, ε = 0.05); (b) the decisive step at the
lower rung actually consumed by the registered non-model mechanism (capability-source
ledger shows it); (c) the 7-axis ledger complete, with acquisition and maintenance
charged — never hidden; (d) no uncharged model axis. Then:

- **G1→2**: R1 ledger complete and every R1 commit checker-graded before entering state.
- **G2→3 (activation gate)**: FNA-7/#208 transplants T1 `repository_semantic_retrieval`
  and T2 `failure_classification` each at `PARENT_SUFFICIENT_FOR_<capability>` or
  `NON_NEURAL_NONINFERIOR_AT_REGISTERED_SCOPE`, plus a candidate-supply surface the
  incumbent planner consumes. **Unmet on current main** (FNA-7 protocol exists as
  `research/fna7-capability-transplant-v1/`; no transplant results are merged).
- **G3→4**: FNA-4/D6 library/synthesis parents sufficient for learned-operator supply;
  FNA-7 T4/T5 non-inferior; donor-gate conceding policy frozen. Unmet (D6 open).
- **G4→5**: FNA-7 T3 `API/interface_induction` and T6 `verification_interpretation`
  non-inferior; FNA-3/D5 bounds the language-proposal surface. Unmet (D5 open).
- **G5→6**: nothing further — R6 runs as the standing bounded-domain arm whenever its
  own capability gate holds.

### 7-axis whole-lifetime cost ledger (per rung, per arm — #214 §4 verbatim enumeration)

1. `capability_source` — which mechanism supplied the decisive committed step (model /
   exact_scan / exact_probe / approx_window / approx_sample / oracle).
2. `model_usage` — calls, calls_ok, parse_failures, tokens (as reported by the model
   interface), wall seconds. Interface opacity (tokens not splittable into
   prompt/completion by the CLI) is itself recorded, never guessed.
3. `state_growth` — persistent explicit state added (recorder rows/bytes, index entries,
   learned bytes).
4. `acquisition_work` — one-time build: index build work, guard derivation, authored-prior
   bytes of the frozen controller/proposer spec (#214 §6 prior-information accounting).
5. `reasoning_work` — per-query execution + structural-selection work (logical counters).
6. `verifier_work` — exact-certificate + commitment-gate work.
7. `maintenance_and_revision` — drift index rebuild + recompute; revocation recompute;
   model re-asks where a rung needs them (measured, not derived).

Axes are never summed across incommensurable units: `lifetime_logical_work` totals
commensurable logical counters only; tokens and wall seconds stay separate lines.

### Capability-preservation margin

ε = 0.05 on delivered-correct rate per frozen window, defined before outcomes. Exact OCM
arms are correct-by-construction (checker certificate); the margin governs rung
comparisons and transition gates, not post-hoc tuning.

### Honest terminals per rung (registered set, #214 §7)

- R6: `PARENT_SUFFICIENT_FOR_obligation_control` (guarded analytic parent sufficient at
  ε and lifetime cost ≤ (1+ε)·incumbent) / `NON_NEURAL_NONINFERIOR_AT_REGISTERED_SCOPE`
  (incumbent exact machinery) / `CANNOT_CHECK_HARNESS_FAILED_BASELINE`.
- R1: `NO_FUNCTIONAL_PARITY_control_at_scope` (model controller below 1 − ε — stepping to
  R6 is capability-preserving at scope) / `NEURAL_DONOR_DOMINATES_AT_SCOPE` (model
  strictly exceeds every OCM arm) / `NON_NEURAL_NONINFERIOR_AT_REGISTERED_SCOPE`.
- R2: `R2_CAPABILITY_PRESERVED_AT_SCOPE` (committed-correct ≥ 1 − ε with proposals
  consumed at the decisive step — evidence toward G1→2, not deployment authority) /
  `NO_FUNCTIONAL_PARITY_proposal_at_scope`.
- R3–R5: no terminal claimed; status `RUNG_PENDING_ACTIVATION_GATE` with the gate text.
- Machinery failure on a rung that was supposed to execute: `CANNOT_CHECK_<reason>`
  (e.g. `CANNOT_CHECK_NO_MODEL_ACCESS` had the laptop's codex auth been dead).

### Frozen model configuration (R1/R2 shadow arms)

`codex exec --skip-git-repo-check -C <empty workdir> -c model=gpt-5.5 -c
model_reasoning_effort=low -c sandbox_mode=read-only`, one call per query, timeout 300 s,
zero retries, codex-cli 0.129.0-alpha.15, version recorded per receipt. The CLI's fixed
agent scaffold inflates tokens per call (~19k on the 2026-09-09 probe); that is a real
cost of the R1 interface and is charged as measured.

## Controls

- **Mock-never-scores**: the deterministic mock controller/proposer drives only tests and
  smoke runs; receipts are stamped `model_mode: MOCK` and the terminal evaluator refuses
  to score them.
- **No-fabrication rule**: model-call failures, parse failures and illegal operator ids
  are recorded as charged control failures; nothing is repaired, retried into existence,
  or paraphrased.
- **No-oracle information surface** (structurally tested): prompts carry the slice, the
  declared catalogue and declared centres only — never realized constants, split
  membership or checker internals.
- **Determinism**: identical receipts under the frozen salt (tested).
- **Forbidden-token scan** on every receipt (tested).

## Declared limitations, before seeing outcomes

One authored world (E1/L1); the exact checker makes failures always-caught; the boundary
band makes some THRESH queries genuinely hard for in-context arithmetic, which is a fair
measurement of the R1 controller, not a rig; the codex scaffold's fixed token overhead
dominates small-query R1/R2 token counts — reported as measured, and a scope limitation
for per-query token claims; wall seconds are single-host descriptive; rungs 3–5 are
protocol-only until their gates are met. The negative-results directive applies: any
failing arm gets one-stage failure attribution and a revival iteration in a new numbered
file with its own freeze addendum, never a silent edit of frozen files.

# FNA-8 / D9 results — PrivilegeLadderProtocolV1 (consolidated 2026-09-09)

Receipts: `FNA8_R6_FULL.json` (scored), `FNA8_R1_CODEX_INTERFACE_REFUSED.json`,
`FNA8_R2_CODEX_INTERFACE_REFUSED.json` (kept verbatim; see FREEZE amendment 1).
Consolidated artifact: `FNA8_RESULTS_V1.json`. Evidence class E1/L1.

## Headline

- **R6 (bounded domain, no frontier model): terminal
  `PARENT_SUFFICIENT_FOR_obligation_control`.** Over the frozen world WL1
  (240 queries: DEV 66 / EVAL 127 / DRIFT 47; revocation atom a0000 affecting 20
  EVAL queries) the analytic guarded parent delivers **1.0** correct at
  **22,600** lifetime logical work vs the incumbent policy's 1.0 at **28,236**
  (0.80x, inside the frozen (1+eps) bound) — the guard is re-derived from the
  declared spec at zero label cost. Incumbent sources: probe 40 / scan 119 /
  window 10 / sample 5. Guarded sources: scan 167 / probe 3 / window 4.
  Oracle arm labelled, never scored. Drift rebuild + revocation recompute
  charged to every arm.
- **R1 (LLM controls + OCM records): terminal `CANNOT_CHECK_NO_MODEL_ACCESS`.**
  24 EVAL + 5 REV re-ask calls placed to gpt-5.5 (codex exec, pinned CLI); the
  surface refused every call server-side during the scored window (rc=1, null
  agent messages, 0 usable turns). 0 model commits; all 24 queries rescued by
  the charged scan fallback — the 1.0 delivered rate is the OCM safety net,
  never read as model capability. The instrument itself is verified live the
  same day (19:24Z probe: 21,562 tokens, correct reply), so adapter, parsing
  and harness are sound; the refusal is interface-stage. Re-execution path is
  recorded in FREEZE amendment 1.
- **R2 (LLM proposes, OCM selects/commits): terminal `CANNOT_CHECK_NO_MODEL_ACCESS`**
  — same refusal signature (29 calls, 0 usable, 875 s wall; every query
  scan-committed by the incumbent machinery).
- **R3–R5: `RUNG_PENDING_ACTIVATION_GATE`** — activation gates (FNA-7/#208
  transplants T1/T2, D5/D6 parents) unmet on current main; nothing claimed.

## 7-axis ledger (whole-lifetime, per arm; incommensurable axes never summed)

- Model axes charged as measured: R1 29 calls / 29 parse-failures / 968.2 s
  wall / 0 tokens reported by the refused interface; R2 29 / 29 / 875.2 s / 0.
- R1 state growth (the OCM-records obligation): 53 append-only recorder rows,
  8,543 bytes. Revision window: 5 measured re-asks, 1 revoked atom.
- R6 lifetime logical work: acquisition (index build, guard derivation),
  reasoning, verification, drift rebuild and revision recompute all charged.

## Reading

The ladder's current-main status: the bounded-domain rung is **executable and
parent-sufficient today** (exact OCM machinery, cheaper than the incumbent
policy at the registered scope); the two model-privilege rungs that
current-main can instrument are **harness-complete but interface-blocked** at
this run window — their measurement instruments are frozen, tested (23/23) and
one command away from re-execution when the surface answers; rungs 3–5 wait on
their registered activation gates, by design.

No terminal here licenses deployment or any #165 unlock. No forbidden
collection token appears in any receipt (scanned, tested).

# Flagship entry-gate closure plan — FE-DEV-AMORT-1 (Refs #151, refs #165, refs #277)

Opened 2026-09-10, non-final, append-only. Companion to `FLAGSHIP_EXPERIMENT_V1.json`
(`closure_plan_ref`). Every row names the ALREADY-FROZEN, ALREADY-IMPLEMENTED study that
would close a blocking gate sub-item — no row invents new machinery, relaxes a frozen rule,
or authorizes a flagship run. A gate flips only on receipts + an updated #165 evidence sync.

Three of the four open rows are *executions of frozen protocols*: the protocols, the runners
and the tests already exist in the estate, merged and green. The distance to a closed gate is
compute + receipts, not design.

| Gate sub-item (flagship evidence) | Closure study (as frozen) | Registered scope | Owner lane | Status |
|---|---|---|---|---|
| **G2.4 complete** — "SUPPORTED AT REGISTERED POLYNOMIAL SCOPE (#192/#193); explicitly *Not G2.4 complete*" | (a) Execute `research/g2-length-scaling-v1/` unchanged: does the existing fragment learner become causally useful when future tasks require strictly longer primitive programs, with a broader pre-deployment utility gate. (b) Then ONE unification receipt: re-run the #192 G2.4 checklist protocol with the separate-OS-process restart (the `research/g2-process-restart-v1/` harness) bound into the SAME protocol — every checklist item green in one machine identity, one ledger, at the registered length ladder. | registered polynomial estate, sealed worlds, ladder {8,32,128,512}; claim ceiling "bounded causal method reuse in this registered polynomial ecology only" | `g2-length-scaling-v1` (execution) + `g2-macro-operator-v1` (unification receipt) | frozen + machinery merged, NOT executed |
| **G3.2 scoped failure memory** (#165 ordered work C) | Execute `research/g3-scoped-failure-memory-v1/PROTOCOL.md` unchanged: checked failure-point records from counterexamples actually encountered, scoped withdrawal, real process restart, exactly-equipped conventional parent. | authored polynomial distribution (length-4 train / length-5 test, frozen salts); "ordinary checked memoization / counterexample reuse" claim ceiling; tie = `PARENT_SUFFICIENT` | `g3-scoped-failure-memory-v1` | frozen + machinery merged, NOT executed |
| **G3.3 representation change** (#165 ordered work D, first half) | Execute `research/g3-scoped-failure-memory-v1/REPRESENTATION_PROTOCOL.md` unchanged: P0/P1/P2 candidate languages + misleading Q0 registered before outcomes, selection on validation only, dual withdrawal (representation vs memory), fresh-OS-process consumers. | continuation of the #205 eight-task lineage (append-only, inherited state); interpreter-work-coordinate objective; terminal `PREFIX_REPRESENTATION_CAUSALLY_USEFUL_AT_INTERPRETER_STEP_SCOPE` at exact result parity | `g3-scoped-failure-memory-v1` (representation continuation) | frozen + machinery merged, NOT executed |
| **G3.4 insufficiency diagnosis** (#165 ordered work D, second half) | Already executed at scope: `research/g3-representation-diagnosis-v1/` `REPRESENTATION_INSUFFICIENCY_DIAGNOSIS_SUPPORTED_AT_SCOPE` (vocabulary SEARCH_MORE/MISSING_EVIDENCE/LOCAL_REPAIR/MISSING_OPERATOR/REPRESENTATION_INSUFFICIENT/OBSERVATION_CHANNEL_INSUFFICIENT/RESOURCE_BOUND/CANNOT_CHECK with timeout-alone-never-licenses-JUMP). The remaining half of D is the LOOP: a G3.3 positive supplies the representation-change witness that a REPRESENTATION_INSUFFICIENT diagnosis demands; a G3.3 parent-tie proves the diagnosis vocabulary sufficient WITHOUT a causal change (honest PARTIAL, feeds the revival chain). | registered polynomial diagnosis scope; G3.3's registered scope | `g3-representation-diagnosis-v1` (done) + `g3-scoped-failure-memory-v1` (loop) | diagnosis DONE at scope; loop pending G3.3 |
| **Two-domain same core** — "heterogeneous lifetime study not executed (LIF-02 synthetic calibration only)" | HET-LIF-1, frozen separately: `research/het-lifetime-two-domain-v1/HET_LIF_1_FREEZE_V1.json` (PR #364): 4 lifetimes, D1 polynomial + D2 P1-E3 implication-systems, registered core imported unchanged, `SAME_CORE_TWO_DOMAINS_REGISTERED` / `CORE_DIVERGENCE_REQUIRED__<where>` terminals. | E2 scope, descriptive only, no DC-10 claim | `het-lifetime-two-domain-v1` | design frozen; runner + adapters + hostile selftest to build; run after merge |

## Sequencing and hosts

All executions on **laptop billy** (`ssh billy-laptop`; E3 host per E3_PROTOCOL_FREEZE_V1 P8/P9);
billy-old for any E4 rerun; LUNARC batch only if a length-ladder arm needs it. Never the Mac
mini. The three frozen-protocol executions (G2-LEN, G3.2, G3.3) are independent — run them in
parallel; the G2.4 unification receipt and the G3.4 loop closure depend on their outcomes.
HET-LIF-1 builds its runner + hostile selftest while those run.

## Honest terminals discipline (per row)

- `PARENT_SUFFICIENT` is a SUCCESS terminal for the parent question but does NOT flip its
  flagship gate sub-item; it lands here as a revival-chain row (diagnose → attribute to one
  stage → lever → re-test vs strongest parent), never as a quiet drop.
- No threshold moves, no re-draws, no admission loosening, no protocol edits after results;
  any needed change is a recorded supersession BEFORE the next run.
- Cost side is always charged (HDI-14 families + P3 physical meters); count-only claims invalid.
- An executed study's receipts + an #165 evidence-sync comment are the ONLY path to a gate
  flip; nothing in this plan authorizes FE-DEV-AMORT-1 while any entry gate is open.

## Fallbacks (pre-registered, not assumptions)

- If G2-LEN lands negative at longer lengths, the polynomial domain does not complete G2.4
  alone; the registered fallback is re-instantiating the G2.4 checklist over the D2
  implication-systems substrate through the HET-LIF-1 adapter path — a NEW prospective freeze
  (complete-in-one-domain may be earned in D2), never a relabeling of the polynomial result.
- If HET-LIF-1 lands `CORE_DIVERGENCE_REQUIRED__<where>` or `ADAPTER_DOMINATES`, the
  two-domain gate stays PARTIAL and the divergence location becomes the next revival row.

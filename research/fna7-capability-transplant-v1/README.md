# FNA-7 / D8 — CapabilityTransplantProtocolV1 + K2 pilot

Lane FNA-7 / deliverable D8 of the #214 donor-reduction programme, implementing the #208
capability-transplant route: replace ONE model-supplied capability at a time with an explicit
non-neural mechanism, under a held-constant harness, with everything charged.

## Files

- `PROTOCOL.md` — CapabilityTransplantProtocolV1 (generic mechanics + 7 transplant specs).
- `CAPABILITY_TRANSPLANT_PROTOCOL_V1.json` — machine protocol; K2 piloted in this capsule.
- `CONCURRENCY_CHECK.json` — #208 active-work collision check (done FIRST; no collision).
- `FREEZE_FNA7_V1.json` — design frozen before outcome access; 2 numbered amendments.
- `fna7_pilot.py` — pilot harness: arms, repair table, refresh, gate runner (3.8-stdlib-only).
- `test_fna7.py` — 13 tests incl. held-constant-harness digest and banned-token scan.
- `FNA7_PILOT_RESULTS_V1.json` / `.md` — scored run + human summary.
- `SOURCE_LEDGER.json`, `REPO_STATE.json` — provenance and custody.

## One-line result

Pilot capability: failure classification (K2) on the #219 exact world. Terminal:
`PARENT_SUFFICIENT_FOR_FAILURE_CLASSIFICATION__GUARDED_DECLARED_RULE_AT_PILOT_SCOPE_FNA7_V1`
— the zero-acquisition guarded-declared parent is within the frozen ε of the incumbent-class
arm (0.849 vs 0.860 accuracy) at ~16x lower whole-chain cost per failed query; the A2 residual
failure stream is 85% NOISE, and even exact (oracle) classification raises continuation cost on
this stream — parent sufficiency is real and stream-bounded.

## Execution

Tests and the scored run execute on laptop billy (`~/fna7-run`, conda a1_bench, Python
3.10.19), tar+scp+md5 verified; the Mac mini runs nothing. See `REPO_STATE.json` receipts.

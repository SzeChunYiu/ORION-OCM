# FNA-8 / D9 — privilege-reduction / whole-lifetime cost protocol

Issue #214 §4 FNA-8, deliverable FNA-D9. Base commit `ab5310942b01be11776c0eddc4403dc0e0dcb51c`.
Research-only capsule: production `src/` untouched, nothing deployed, no issue/PR writes.

## What is here

- `PROTOCOL.md` — **PrivilegeLadderProtocolV1**: the six rungs with exact authority
  boundaries, the held-constant harness, OCM-side mechanisms with first-refusal parent
  bindings (#215/#218/#219/#222), rung-transition gates incl. the activation gate stated
  against FNA-7's deliverables, the 7-axis whole-lifetime cost ledger, the frozen
  capability-preservation margin (ε = 0.05) and the honest-terminal tree per rung.
- `FREEZE_FNA8_V1.json` — frozen declarations + sha256 digests, consolidated after
  tests green and BEFORE any full-config scored run. Amendments are numbered.
- `fna8_world.py` — frozen task world WL1 (additive on the #72-owned incumbent surfaces
  `OperatorSpec` / `SolveOperatorIndex.select()`; exact checker; drift + revocation
  events). `fna8_ledger.py` — the 7-axis ledger + OCM-side append-only recorder.
  `fna8_model.py` — the single model-reach point (codex exec adapter + declared mock).
  `fna8.py` — driver CLI (`--rung {6,1,2,all}`).
- `test_fna8.py` — 19-test battery (self-managed sys.path): determinism, splits
  partition, checker exactness, no-oracle information surface, parser strictness,
  ledger completeness, authority boundaries, mock-never-scores, pending rungs,
  forbidden-token scan, freeze-hash binding.
- `FNA8_RESULTS_V1.json` / `FNA8_RESULTS_V1.md` — scored artifacts (R6 full; R1/R2
  shadow micro-execution with real gpt-5.5 calls on laptop billy).
- `SOURCE_LEDGER.json` — every claim parent.
- `REPO_STATE.json` — manifest, execution receipts, authority constraints.

## Execution status of the ladder

- **R6** fully executed and scored: `PARENT_SUFFICIENT_FOR_obligation_control`
  (guarded analytic parent, 1.0 correct at 0.80x the incumbent's lifetime logical work).
- **R1** and **R2** attempted as instrumented shadow micro-executions (24 EVAL + ≤8 REV
  real model calls each); the model surface refused every call server-side during the
  scored window, so both are terminalled `CANNOT_CHECK_NO_MODEL_ACCESS` per the
  pre-declared protocol branch (FREEZE amendment 1); the refused receipts are kept
  verbatim as interface-stage evidence and the one-command re-execution path is
  recorded. No model output is fabricated; every refusal is a charged control failure.
- **R3–R5** `RUNG_PENDING_ACTIVATION_GATE` — the FNA-7/#208 transplant results their
  gates require are not merged on current main; nothing is claimed for them.

## Reproduce

```bash
python fna8.py --rung 6 --out r6.json                 # pure OCM, no model needed
python fna8.py --rung 1 --model codex --workdir /tmp/wd --out r1.json   # needs local codex auth
python fna8.py --rung 2 --model codex --workdir /tmp/wd --out r2.json
python -m unittest test_fna8                           # mock mode, no model needed
```

Scored runs executed on laptop billy (conda a1_bench Python 3.10.19), never the Mac mini.

# Heritable Search Geometry v1 — top-level foundation capsule

Issue #233. HSG sits ABOVE #145/#149/#151/#217/#221: those issues' experiments test rows
of `HSG_ATOM_TABLE_V1.json`, not isolated mechanisms. HST v1
(`../heritable-search-transformation-v1/`) is HSG's first finite instantiation (R0–R3
reading); it stays frozen and canonical.

## Read order

1. `HSG_FREEZE_V1.json` — AGP protocol, rung ladder, forbidden terminals (frozen)
2. `HSG_DEFINITIONS_V1.md` — rung types, central lifts, geometry discipline, verdict semantics (frozen)
3. `HSG_ATOM_TABLE_V1.json` — 17 concept atoms + 18 theorem atoms; lanes fill verdicts only
4. `LITERATURE_LEDGER_HSG.md` — per-rung parents; ⚠ = verify before citing
5. lane artifacts: `ladder/` (lift writeups), `hostiles/` (counterexamples), `exact/` (checkers)
6. `HSG_ISSUE_HOOKS_V1.json` — centre, after lanes: row → dependent-issue measurement map

## Execution map (D0'–D6')

D0' this commit (freeze) → D1' lane E: concept atoms G01–G17, rungs R1–R3 + assumption
removals (i)(ii)(iii) → D2' lane F: rungs R4/R5 for all rows (Dobrushin/OT/info-geometry/
semigroup parents; theorem survival T01/T03/T05/T06/T07/T12) → D3' lane G: rungs R6/R7
(C time-variation, kernel-valued processes, open systems; T04/T08/T09/T13/T14/T15/T16/T17/T18)
→ D4' centre survival synthesis (`HSG_SURVIVAL_V1.json`) → D5' issue-hook wave (dependent
issues re-anchored to HSG rows) → D6' hostile review (fresh-context agent).

## Hard rules for lanes (superset of HST's)

- Frozen files are read-only; verdicts go ONLY in `REGISTRY_PATCH_{E,F,G}.json`.
- One rung per lift, one assumption removed per pass, every LIFT_FAILS ships a minimal
  counterexample, every PARENT_SUFFICIENT names the parent and exact owned statement.
- Exact checkers run on **billy-laptop** (`ssh billy-laptop`), never the Mac; a checker
  certifies the finite specialization only, never a rung verdict.
- Output discipline: never echo large files; write artifacts file-by-file; cap command
  stdout; reports ≤60 lines.
- No empirical positive promotion; P4 stays P4 at every rung; forbidden terminals in the
  freeze are enforced verbatim.

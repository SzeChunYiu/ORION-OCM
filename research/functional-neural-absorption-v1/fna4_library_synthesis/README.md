# FNA-4 capsule — library/synthesis learner parent suite (#214 / FNA-D6 -> #62)

Read order: `FNA4_REPORT.md` (results + terminal) -> `FNA4_RESULTS.json`
(distilled numbers) -> `FNA4_PROTOCOL.md` + `FNA4_FREEZE.json` +
`FNA4_FREEZE_ADDENDUM_V1/V2/V3.json` (what was pinned before each run) ->
`receipts/` + `defect_runs/` (verbatim evidence) -> code.

- Question: does OCM's operator/composition learning (#62) need anything beyond
  the strongest classical library/synthesis parents (Reynolds anti-unification,
  Stitch, egg, Soar chunking, Korf macros, CEGIS)? All arms non-neural,
  stdlib-only, executed on main's own substrate (`SolveOperatorIndex`,
  `WarrantProfile` meet, misfire nogoods), every unit charged at 1:1.
- Terminal: `PARENT_SUFFICIENT_FOR_EXPERIENCE_CONSOLIDATION_AT_REGISTERED_SCOPE`
  — 270,829 vs 366,072 units (−26.0%) on an identical fresh 16-task stream by
  STITCH + per-batch nogoods + CEGIS, with measured qualifiers (critical F2
  share, ~6.1k-task break-even at zero repeat, recurrence-gated admission
  harmful). Scope limits and the full comparison table are in the report.
- Negative->positive chains, all in-suite and measured: recurrence-gated
  admission -> utility-gated (the STITCH arm); nogood per_op -> per_batch;
  harness defects 1-3 (preserved in `defect_runs/`, fixed under pre-run
  addenda V1/V2); P6 unmeasurable -> composition-level revival sweep
  (addendum V3, `run_fna4_sweep_r2.py`) with a one-stage attribution probe
  (`probes/`).
- Reproduce (off-Mac host, this directory): `python3 test_fna4.py` (16 tests) ·
  `python3 run_fna4.py <out>` (scored suite, ~30 min) ·
  `python3 run_fna4_sweep_r2.py <out>` (P6 revival) ·
  `python3 distill_results.py` (rebuild RESULTS from receipts).
- Lane state: `FNA4_REPO_STATE.json`. Base 86ddd9b, additive files only, no
  PR opened, no issue edits.

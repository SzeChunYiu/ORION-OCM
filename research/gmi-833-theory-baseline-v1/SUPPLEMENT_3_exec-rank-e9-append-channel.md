# Supplement 3 — owning-lane record: E9 appends channel correction (#981 defect, #988 repair)

Date: 2026-09-17. Lane: #833 W5 G0-ops (the E9 exec-rank owning lane; branch
`fix/833-post-988-register-coherence`). This is the owning-lane narrative
record that Supplement 2 §"Third-party freeze violation restored + succeeded"
explicitly leaves to this lane. No V1- or V2-bound file's content changes
here; this supplement is unbound (register-movement record, like Supplement 1)
and the binding state is Supplement 2's `BASELINE_MANIFEST_V2.json`.

## Defect (this lane's #981, commit `67133f0f`)

Our E9 merge wrote two post-freeze changes into frozen objects:

1. Edited the V1-bound
   `research/gmi-833-g0-grammar-growth-v1/ISSUE_833_RECONCILIATION_GRAMMAR_GROWTH_V1.json`
   in place (whole-file re-indent, `\uXXXX` escaping, additive `e9_note`):
   2881 -> 3265 bytes — the `SILENT_EDIT_OF_BOUND_ARTIFACT` forbidden class.
   `test_theory_baseline_v1.py` went RED on main; flagged by #989.
2. Committed three unregistered files into the frozen closed-set package
   `research/gmi-833-claim-discipline-v1/` (`authored_e9_append.py`,
   `assemble_e9_append.py`, `REGISTRATIONS_E9_APPEND.json`).

Root cause on our side: the E9 PR's paths never triggered the path-filtered
baseline validator, so the defect rode an unvalidated merge (same blindness
Supplement 2 records for the binding side).

## Repair state (verified independently by this lane on main `103e4274`)

Merged #988 repaired both per the post_freeze_edit_rule: the V1 file restored
byte-exact to sha256 `95848277e3649ccafe9c54be3e88b40a3e0b12307cd326dbdf2a57ee3537656d`
(2881 bytes); the reconciled content preserved byte-for-byte in the NEW
successor `ISSUE_833_RECONCILIATION_GRAMMAR_GROWTH_V2.json` (sha256
`dbb15e9f…`, exactly the #981-era bytes; `e9_note` field byte-exact); the
append trio bound unchanged in `BASELINE_MANIFEST_V2.json`; the E9 workflow's
foreign-PR custody fetch repaired (`refs/pull/981/head`). This lane's
independent verification: validator 6/6 GREEN in `-I -B` and `-I -O -B`;
own-implementation hash pass over all 143 bindings across both manifests —
0 violations; 0 unregistered tracked files in every frozen package.

## This PR (register coherence residuals)

- `SUPPLEMENT_1_revival-l47-novel-intelligence-w4.md` renumbered to
  `SUPPLEMENT_2_…` (#989's supplement merged first and holds sequence #1);
  `build_manifest_v2.py` + `BASELINE_MANIFEST_V2.json` rebuilt
  deterministically + the package workflow's V2 anchor updated in the same
  commit (loud-change rule).
- The E9 package's dangling pointer fixed: `MANIFEST_E1.json`
  `reconciliation_note` now resolves to the successor file's `e9_note`
  (the restored V1 file has no such field); `FREEZE_E1.md` §6 carries a
  dated channel-correction amendment; `RECEIPTS_RUN_LOG.md` records the
  correction row; `CORE.md` reading order includes the successor.

## e9_note (verbatim, as preserved in the successor file)

> E9 metric-conditionality note (#897 follow-up, gmi-833-g0-exec-rank-revival-v1):
> the NULL-1 rank-1 statement reconciled by this spec is count-metric; under
> EXEC-B at rho=1, 19/200 equal-cardinality nulls beat the recursive library.
> Rank-1 is restored under BOTH accountings by the nesting-ladder witness
> (flat pair {ab, abab}, break-even 314 vs 164); see REGISTRATIONS_E9_APPEND.json.

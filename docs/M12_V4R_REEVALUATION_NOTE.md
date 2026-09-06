# M12 V4-R — re-evaluation under the corrected adoption gate (engineering re-evaluation, not a new protected study)

Why: the runtime lifecycle revalidation merged in #39 (`docs/RUNTIME_LIFECYCLE_REVALIDATION_V2.md`) corrected the
self-change adoption gate (decision fingerprint, protected targets and the exact target predecessor are all checked)
and reopened the historical M11 V1 and M12 V2 phase-G cells, whose component table was keyed by `machine`. The V4
paired-lifetimes study (`research/ocm-m12/M12_PAIRED_LIFETIMES_EVAL_V4.json`, receipt `M12_PAIRED_RECEIPT_V4`)
ran before that correction; it stays the frozen record of its own pre-registration and code.

What V4-R is: the same eight frozen V4 streams (manifest `72d7d782…`) and the same V4 rule, re-run on the current
runtime (branch `m11.4/predecessor-binding` on main after #39/#40) in a git clone on billy-old. Under the merged
regime the current evaluation code labels every current-runtime run `CANNOT_CHECK_CURRENT_SCIENTIFIC_PROMOTION`
and keeps the pre-registered rule's outcome as `historical_rule_diagnostic`; the cross-domain transfer family is
`CANNOT_CHECK_MATCHED_CASES` because the V2–V4 cell sets differ between arms (6 vs 4; the prospectively matched
cells are implemented for V5 as `phase_E(matched_cells=True)`).

Result (`research/ocm-m12/M12_PAIRED_LIFETIMES_EVAL_V4R.json`):
* decision (merged regime): `CANNOT_CHECK_CURRENT_SCIENTIFIC_PROMOTION`; historical-rule diagnostic: `OCM_LIFETIME_RESIDUAL_SUPPORTED`
* primary family A conversations: OCM 0.9954 vs parent 0.6065, 8/8 lifetimes, one-sided p = 0.00391 (V4: 0.9815 vs 0.607, 8/8, 0.0039)
* phase G under the corrected gate, per lifetime (fault, diagnosed, repaired, rollback exact): [('operator_fault', 'D2', True, True), ('learning_policy', 'D6', True, True), ('environment_drift', 'D2', True, True), ('operator_fault', 'D2', True, True), ('learning_policy', 'D6', True, True), ('environment_drift', 'D2', True, True), ('operator_fault', 'D2', True, True), ('learning_policy', 'D6', True, True)]
* kill gates: 0 hits
* behavioural differences from V4 come from the lane's runtime repairs (e.g. the actual-speech gate): negative-transfer probes 0.857 vs 1.0, conversations 0.9954 vs 0.9815 — reported, not reconciled here.

Status: descriptive engineering re-evaluation. A renewed scientific terminal requires a new pre-registration (V5)
under the merged regime: matched transfer cells, the corrected gate from the start, and the #38 acceptance gates.

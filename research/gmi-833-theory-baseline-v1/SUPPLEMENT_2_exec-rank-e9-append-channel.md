# Supplement 2 — E9 exec-rank appends: post-freeze channel correction

Date: 2026-09-17. Lane: #833 W5 G0-ops repair (branch
`fix/833-baseline-drift-e9-note`). This supplement follows the post-freeze
edit rule (BASELINE_MANIFEST_V1.json `post_freeze_edit_rule`): no bound
artifact is modified; this file is the correct channel for the information
that PR #981 attempted to attach to a bound artifact. The binding is
unchanged, so no BASELINE_MANIFEST_V2 is required.

## Defect (introduced by #981, discovered by #989)

PR #981 (commit `67133f0f`, "exec-cost rank revival") wrote two post-freeze
changes into frozen objects of this baseline:

1. **In-place edit of a bound artifact.**
   `research/gmi-833-g0-grammar-growth-v1/ISSUE_833_RECONCILIATION_GRAMMAR_GROWTH_V1.json`
   was rewritten (whole-file re-indentation, `\uXXXX` escaping of the
   replacement rows, and an additive `e9_note` field): 2881 -> 3265 bytes.
   `test_theory_baseline_v1.py` went RED on main
   (`bound artifact size drifted … 3265 != 2881`), flagged in the #989 PR
   body and on #833. This is exactly the `SILENT_EDIT_OF_BOUND_ARTIFACT`
   forbidden-promotion class.
2. **Unregistered files in a frozen closed-set package.**
   `authored_e9_append.py`, `assemble_e9_append.py`, and
   `REGISTRATIONS_E9_APPEND.json` were committed into
   `research/gmi-833-claim-discipline-v1/` (frozen component package) —
   unregistered tracked files per the closed-set rule.

## Correction (this PR)

- The bound reconciliation artifact is restored byte-exact to its frozen
  pin: sha256 `95848277e3649ccafe9c54be3e88b40a3e0b12307cd326dbdf2a57ee3537656d`,
  2881 bytes (verified against BASELINE_MANIFEST_V1.json with
  `/usr/bin/shasum -a 256`; source blob `67133f0f^`).
- The E9 append trio is relocated into its OWNING lane package at
  `research/gmi-833-g0-exec-rank-revival-v1/claim_discipline_append/`,
  reading the frozen registers read-only. The relocated assembler
  regenerates `REGISTRATIONS_E9_APPEND.json` byte-identical to the
  pre-relocation file (sha256
  `aa8c43832e3b1d46363fa64ee1a7fdaefd8e20f8cbf19e8ae564d23bad0b30e7`);
  the frozen registers' own sha256s (`b6bd7503…` v1, `90a278e1…` v2) are
  unchanged — no information lost, only the channel corrected.
- The `reconciliation_note` pointer in the E9 package's `MANIFEST_E1.json`
  now resolves to this supplement (`…SUPPLEMENT_2_exec-rank-e9-append-channel.md:e9_note`).

## e9_note (verbatim from #981 — the information this supplement preserves)

> E9 metric-conditionality note (#897 follow-up, gmi-833-g0-exec-rank-revival-v1):
> the NULL-1 rank-1 statement reconciled by this spec is count-metric; under
> EXEC-B at rho=1, 19/200 equal-cardinality nulls beat the recursive library.
> Rank-1 is restored under BOTH accountings by the nesting-ladder witness
> (flat pair {ab, abab}, break-even 314 vs 164); see REGISTRATIONS_E9_APPEND.json.

The registered carrier of this note is the claim-discipline append itself
(`REGISTRATIONS_E9_APPEND.json`: status `APPEND_E9_EXEC_RANK_REVIVAL`, the
`METRIC_RELATIVE_RANK1…` forbidden-extrapolation entry), which now lives in
the owning lane per this supplement.

## What stands unchanged

- The tranche-2 ledger append (`SCIENTIFIC_LEDGER_V2.json:revival_records`
  REV-E9-1, closing GAP-T2-2): `gmi-833-g0-grammar-growth-v2` is not a
  baseline-bound package; only its `discipline_append` pointer string was
  corrected to the relocated path, and its package `MANIFEST_V2.json` ledger
  sha256 was refreshed (it had been left stale by #981's ledger rewrite).
- The E9 science (receipts, theorems, witnesses) is untouched: the E9
  package's 44 tests, engine, and oracle are byte-identical and green.

## Validator status

`test_theory_baseline_v1.py` (normal and `-O -B` modes): 6/6 GREEN after
this correction (was RED on `test_every_bound_artifact_hash_matches_live_tree`
before it). No bound artifact differs from its pin; no unregistered tracked
file remains in any frozen component package.

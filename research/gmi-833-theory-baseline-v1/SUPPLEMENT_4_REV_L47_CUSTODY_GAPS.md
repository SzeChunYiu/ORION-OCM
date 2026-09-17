# SUPPLEMENT 4 — REV-L47-CUSTODY-GAPS closed green

Per the post-freeze edit rule of BASELINE_MANIFEST_V1.json governance: this
supplement records a revival-ticket closure. BASELINE_MANIFEST_V1.json, V2
and every file they bind stay byte-identical. This tranche adds ONE new
tracked file inside a frozen component (the corpus-passes closure record),
so the binding changes and BASELINE_MANIFEST_V3.json is cut per the rule
(deterministic builder build_manifest_v3.py, anchors V1+V2, workflow
loud-change literal updated in the same commit); the revival package below
is a new-lane arrival typed per the arrival absorption rule.

## Ticket

`REV-L47-CUSTODY-GAPS` — 18 CUSTODY_NON_DEMONSTRABLE corpus packages from
the corpus identification passes v2 L47 screen (config-freeze separations
too close / outcome-ordering non-demonstrable; class first surfaced in the
AJ9 audit findings).

## Status after this tranche: CLOSED_GREEN (18/18 in principled terminals)

Owning lane: `research/gmi-833-rev-l47-custody-gaps-v1/` (this revival
tranche; PR references #833).

- **Triage** (TRIAGE_V1.json, evidence: triage_timeline_v1.json +
  triage_crosspkg_v1.json): 6 MECHANICAL / 12 SUBSTANTIVE, each decision
  cited to per-package and cross-package git first-add evidence on the
  registered >120 s demonstrability bar of PASS_L47_V1.md.
- **Mechanical repair** (CUSTODY_REPAIR_RECEIPTS_V1.json; checker
  custody_repair_v1.py, negative-control-verified): 6/6
  MECHANICAL_CUSTODY_DEMONSTRATED — aj9a registry (precedes every repo-wide
  holdout implementation by >=1468 s, blob-pinned, single-commit),
  transform-geometry / remint-equivariance / pareto-topology (outcomes
  +126/+135/+136 s, ancestor-ordered, window-immobile; screen flags were
  checker .py artifacts), capability-held-freeze (predictor->freeze->score
  chain all >280 s, digest-bound), capability-transfer-freeze (no outcome
  exists repo-wide; rows immutable; one typed pre-outcome digest
  canonicalization).
- **Prospective re-establishment** (W4 pattern; freeze REV_FREEZE_V1.md first-add 6061e111d BEFORE
  any re-run - every receipt verifies the freeze-commit ancestry of its
  run commit in-repo; remote-host receipts reruns/billy-old +
  reruns/billy-laptop): 12/12 CLEARED_GREEN at original strength,
  including the section-d two-stage replica with fresh single-draw
  acquisition, stage-2 freeze 92197fc42 before any n=17/31 execution, and
  an in-repo-verified custody chain. (A first fully-green chain at
pre-rebase SHAs was orphaned by a re-base after #989 landed
mid-PR-creation; archived under reruns/archive-pre-rebase/ and the
chain re-executed in full - see REV_FREEZE_V1.md re-execution note.) Original landing commit-order gaps
  remain recorded permanent defects (content re-earned, not cleansed).
- **Verdicts + new finding routed**: VERDICTS_V1.json; AJ9A-AUDIT-WALKER-
  LIST-EVASION (pre-existing, root-caused, aj-lane owned, lever recorded).

## Arrivals enumerated (U-NEW objects under the arrival absorption rule)

- `research/gmi-833-rev-l47-custody-gaps-v1/` (new revival-tranche package:
  TRIAGE_V1.json, collectors, mechanical specs + checker + receipts,
  REV_FREEZE_V1.md, run_batch_v1.py, REPLICA_SAMPLE_V1.json,
  REPLICA_TRAIN_V1.json, REPLICA_FIT_FREEZE_V1.json, VERDICTS_V1.json,
  reruns/{billy-old,billy-laptop}/ receipts).
- `research/gmi-833-corpus-passes-v2-v1/VERDICT_REGISTER_L47_REV_ADDENDUM_V1.json`
  (append-only addendum to the frozen verdict register).
- `research/gmi-833-theory-baseline-v1/SUPPLEMENT_4_REV_L47_CUSTODY_GAPS.md`
  (this file).

## Register effect

`revival_ticket_register.open` in the frozen V1 manifest still lists
REV-L47-CUSTODY-GAPS; this supplement is the living record of its closure
(the V1 JSON is byte-frozen and is not edited). The corpus-passes verdict
register records the same closure via its L47 addendum.

## Pre-existing validator red — RESOLVED upstream before this PR merged

At tranche start `test_theory_baseline_v1.py` was red on main (67133f0fa,
PR #981): PR #981 had modified the baseline-bound artifact
`research/gmi-833-g0-grammar-growth-v1/ISSUE_833_RECONCILIATION_GRAMMAR_
GROWTH_V1.json` (2881 -> 3265 bytes) after the manifest pin, with no
re-cut (sole drift among all 136 bound artifacts; diagnosed and routed by
this tranche before the fix landed). The w4 lane's V2 supplement (#988)
subsequently restored the V1 bytes exactly and bound the reconciled
content byte-for-byte in the successor file ISSUE_833_RECONCILIATION_
GRAMMAR_GROWTH_V2.json, fixing the red before this PR merged. With this
tranche the validator is green: 6/6, all manifests V1-V3 anchored and
byte-stable.

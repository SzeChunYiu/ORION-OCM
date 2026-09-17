#!/usr/bin/env python3
"""Build BASELINE_MANIFEST_V5.json — the fourth post-freeze supplement
manifest for GMI_THEORY_BASELINE_V1 (REV-L46-TWO-ROUTE-PROGRAMME tranche 1).

Per the baseline post_freeze_edit_rule: no bound artifact is edited in
place; this tranche appends ONE revival-progress record to the frozen
corpus-passes package (VERDICT_REGISTER_APPEND_REV_L46_V1.json;
VERDICT_REGISTER_V1.json and REVIVAL_TICKETS_V1.json stay byte-identical)
plus new in-package route-2 artifacts and the programme package outside the
frozen components. V5 binds the progress record, the programme artifacts,
the eight ORACLE receipts, and moves the revival-ticket register
current-state (REV-L46: open -> open with tranche 1 complete, 8 of 75).

Deterministic, stdlib-only. Run from anywhere:
  python3 -I -B research/gmi-833-theory-baseline-v1/build_manifest_v5.py
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PKG = "research/gmi-833-theory-baseline-v1"

V1_MANIFEST_ANCHOR = "31de4041c0b6cb94152debbc4901041fb46626b9866122010a11df5319a62e97"
V2_MANIFEST_ANCHOR = "5d7bfcdd313622cf8bc0c53effa33783bac9d4a9d84ef9d7174615a3549ee264"
V3_MANIFEST_ANCHOR = "dbf0a12e0e9927ce6239188fff280131530c66d56ac27b919967cff8c3795900"
V4_MANIFEST_ANCHOR = "05d35d9fe9fc92a61657d13050601f58b854795d2b318fa1b5998f8732bca736"

PROGRESS_COMPONENT = {
    "id": "revival-l46-two-route-tranche-1",
    "package": "research/gmi-833-corpus-passes-v2-v1",
    "pr": None,
    "child_issue": 833,
    "role_in_baseline": (
        "post-freeze supplement per the baseline post_freeze_edit_rule: "
        "REV-L46-TWO-ROUTE-PROGRAMME tranche-1 progress record appended to "
        "the frozen corpus-passes package (VERDICT_REGISTER_V1.json and "
        "REVIVAL_TICKETS_V1.json stay byte-identical; this append carries "
        "the current L46 disposition: 8 of 75 SINGLE_ROUTE packages "
        "converted with exact two-route agreement except one registered "
        "finding, 67 remain for tranche 2)"
    ),
    "artifacts": [
        {
            "path": "research/gmi-833-corpus-passes-v2-v1/VERDICT_REGISTER_APPEND_REV_L46_V1.json",
            "role": "REVIVAL_TICKET_PROGRESS_RECORD",
        },
        {
            "path": "research/gmi-833-rev-l46-two-route-programme-v1/PROGRAMME_V1.md",
            "role": "FROZEN_PROGRAMME",
        },
        {
            "path": "research/gmi-833-rev-l46-two-route-programme-v1/RANKING_V1.json",
            "role": "FROZEN_MECHANICAL_RANKING",
        },
        {
            "path": "research/gmi-833-rev-l46-two-route-programme-v1/FREEZE_L46_TWO_ROUTE_V1.md",
            "role": "PER_PACKAGE_DECLARATIONS",
        },
        {
            "path": "research/gmi-833-rev-l46-two-route-programme-v1/rank_population_v1.py",
            "role": "RANKING_GENERATOR",
        },
        {
            "path": "research/gmi-formal-proof-audit-v1/ORACLE_RESULT_L46_V1.json",
            "role": "TWO_ROUTE_RECEIPT_CONVERTED_16_ROWS",
        },
        {
            "path": "research/gmi-developmental-uncertainty-transport-v1/ORACLE_RESULT_L46_V1.json",
            "role": "TWO_ROUTE_RECEIPT_CONVERTED_57_ROWS",
        },
        {
            "path": "research/gmi-capability-ceilings-v1/ORACLE_RESULT_L46_V1.json",
            "role": "TWO_ROUTE_RECEIPT_CONVERTED_81_ROWS",
        },
        {
            "path": "research/gmi-analog-semantics-closure-v1/ORACLE_RESULT_L46_V1.json",
            "role": "TWO_ROUTE_RECEIPT_CONVERTED_9_ROWS",
        },
        {
            "path": "research/gmi-uncertainty-composition-v1/ORACLE_RESULT_L46_V1.json",
            "role": "TWO_ROUTE_RECEIPT_CONVERTED_39_ROWS",
        },
        {
            "path": "research/gmi-dependency-aware-uncertainty-composition-v1/ORACLE_RESULT_L46_V1.json",
            "role": "TWO_ROUTE_RECEIPT_CONVERTED_41_ROWS",
        },
        {
            "path": "research/gmi-833-rev-l46-two-route-programme-v1/units/gmi-structural-threshold-repair-v1/ORACLE_RESULT_L46_V1.json",
            "role": "TWO_ROUTE_RECEIPT_WITH_FINDING_L46F1_50_ROWS",
        },
        {
            "path": "research/gmi-learning-law-selection-v1/ORACLE_RESULT_L46_V1.json",
            "role": "TWO_ROUTE_RECEIPT_CONVERTED_23_ROWS",
        },
    ],
}

SELF_BINDING_FILES = [
    ("research/gmi-833-theory-baseline-v1/SUPPLEMENT_5_REV_L46_TWO_ROUTE.md",
     "FREEZE_PACKAGE_SUPPLEMENT"),
    ("research/gmi-833-theory-baseline-v1/build_manifest_v5.py",
     "FREEZE_PACKAGE_SELF"),
]


def sha256_and_bytes(rel):
    # type: (str) -> tuple
    data = (REPO / rel).read_bytes()
    return hashlib.sha256(data).hexdigest(), len(data)


def main():
    # type: () -> int
    anchors = {
        "V1": (PKG + "/BASELINE_MANIFEST_V1.json", V1_MANIFEST_ANCHOR),
        "V2": (PKG + "/BASELINE_MANIFEST_V2.json", V2_MANIFEST_ANCHOR),
        "V3": (PKG + "/BASELINE_MANIFEST_V3.json", V3_MANIFEST_ANCHOR),
        "V4": (PKG + "/BASELINE_MANIFEST_V4.json", V4_MANIFEST_ANCHOR),
    }
    shas = {}
    for name, (rel, anchor) in anchors.items():
        sha, _ = sha256_and_bytes(rel)
        if sha != anchor:
            print("REFUSED: BASELINE_MANIFEST_%s.json drifted from its anchor %s"
                  % (name, sha))
            return 2
        shas[name.lower() + "_manifest_sha256_anchored"] = sha

    component = json.loads(json.dumps(PROGRESS_COMPONENT))
    for art in component["artifacts"]:
        sha, size = sha256_and_bytes(art["path"])
        art["sha256"] = sha
        art["bytes"] = size

    self_binding = []
    for rel, role in SELF_BINDING_FILES:
        sha, size = sha256_and_bytes(rel)
        self_binding.append({"path": rel, "sha256": sha, "bytes": size,
                             "role": role})

    manifest = {
        "schema": "GMI_833_THEORY_BASELINE_MANIFEST_V5_SUPPLEMENT",
        "basis": ("GMI_THEORY_BASELINE_V1 post-freeze supplement #5 "
                  "(post_freeze_edit_rule; next number after merged V4 #993)"),
        "v1_manifest_sha256_anchored": shas["v1_manifest_sha256_anchored"],
        "v2_manifest_sha256_anchored": shas["v2_manifest_sha256_anchored"],
        "v3_manifest_sha256_anchored": shas["v3_manifest_sha256_anchored"],
        "v4_manifest_sha256_anchored": shas["v4_manifest_sha256_anchored"],
        "supplement_of": (
            "BASELINE_MANIFEST_V1.json (132 artifacts, byte-identical, still "
            "authoritative for everything it binds), its V2 supplement (5 "
            "artifacts), V3 supplement (REV-L47 closure) and V4 supplement "
            "(REV-L45-073 closure), all byte-identical"
        ),
        "bound_artifact_count": len(component["artifacts"]),
        "components": [component],
        "self_binding": self_binding,
        "revival_ticket_register_update": {
            "statement": (
                "Current-state movement of the baseline revival register; the "
                "pinned V1 register rows are frozen history and stay untouched"
            ),
            "in_progress": [
                {
                    "id": "REV-L46-TWO-ROUTE-PROGRAMME",
                    "status": "OPEN__TRANCHE_1_COMPLETE_8_OF_75_CONVERTED",
                    "evidence": (
                        "research/gmi-833-rev-l46-two-route-programme-v1 "
                        "(frozen ranking + template + gate at programme freeze; "
                        "8 conversions: 7 TWO_ROUTE_CONVERTED + 1 "
                        "TWO_ROUTE_WITH_FINDINGS (L46-F1 BASE6 interpreter "
                        "sensitivity), 316 exact agreement rows total across "
                        "committed receipts, every route-2 stdlib-only by AST "
                        "audit, executed on billy-laptop with sha256-verified "
                        "custody; see VERDICT_REGISTER_APPEND_REV_L46_V1.json)"
                    ),
                    "remaining": (
                        "67 SINGLE_ROUTE packages for tranche 2, enumerated in "
                        "VERDICT_REGISTER_APPEND_REV_L46_V1.json "
                        "(remaining_for_tranche_2); gmi-novel-intelligence-w4-v1 "
                        "and gmi-morphology-phase-rv-v1 re-enter once their "
                        "lanes close"
                    ),
                }
            ],
            "counts_after": {"total": 9, "closed": 6, "open": 3},
        },
        "u_new_arrivals_enumerated": [
            {
                "package": "research/gmi-833-rev-l46-two-route-programme-v1",
                "kind": "new research/gmi-* package (revival programme lane)",
                "claim_ceiling": [
                    "TRANCHE_1_TWO_ROUTE_CONVERSIONS_AT_REGISTERED_SCOPE"
                ],
                "status": (
                    "holds no baseline assertion until typed by the frozen "
                    "mechanical re-run (census extraction, maturity scoring, "
                    "claim-discipline registration, RAG strata, identification "
                    "screens) per the arrival_absorption_rule"
                ),
            }
        ],
        "governance": {
            "edit_rule": (
                "BASELINE_MANIFEST_V1/V2/V3/V4 and every file they bind stay "
                "byte-identical; changes to V5-bound files require rebuilding "
                "V5 and updating the workflow anchor in the same commit "
                "(loud-change rule)"
            ),
            "validator": (
                "research/gmi-833-theory-baseline-v1/test_theory_baseline_v1.py "
                "re-derives every sha256 across ALL BASELINE_MANIFEST_V*.json "
                "from the live tree"
            ),
        },
    }

    out = REPO / PKG / "BASELINE_MANIFEST_V5.json"
    out.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
    print("wrote %s (%d bound artifacts + %d self-bound)" % (
        out, manifest["bound_artifact_count"], len(self_binding)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build BASELINE_MANIFEST_V3.json — the second post-freeze supplement
manifest for GMI_THEORY_BASELINE_V1 (REV-L47-CUSTODY-GAPS closure).

Per the baseline post_freeze_edit_rule: no bound artifact is edited in
place; this tranche appends ONE closure record to the frozen corpus-passes
package (VERDICT_REGISTER_L47_REV_ADDENDUM_V1.json; VERDICT_REGISTER_V1.json
and REVIVAL_TICKETS_V1.json stay byte-identical) plus a new revival-evidence
package outside the frozen components. V3 binds the closure record and
moves the revival-ticket register current-state.

Deterministic, stdlib-only. Run from anywhere:
  python3 -I -B research/gmi-833-theory-baseline-v1/build_manifest_v3.py
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PKG = "research/gmi-833-theory-baseline-v1"

V1_MANIFEST_ANCHOR = "31de4041c0b6cb94152debbc4901041fb46626b9866122010a11df5319a62e97"
V2_MANIFEST_ANCHOR = "b1941d8fd3b8b92e3521721854d5587e080af8f1dfd7aa39911ce28a92fd890a"

CLOSURE_COMPONENT = {
    "id": "revival-l47-custody-gaps-closure",
    "package": "research/gmi-833-corpus-passes-v2-v1",
    "pr": None,
    "child_issue": None,
    "role_in_baseline": (
        "post-freeze supplement per the baseline post_freeze_edit_rule: "
        "REV-L47-CUSTODY-GAPS closure record appended to the frozen "
        "corpus-passes package (VERDICT_REGISTER_V1.json and "
        "REVIVAL_TICKETS_V1.json stay byte-identical; this file supersedes "
        "their L47 CUSTODY_NON_DEMONSTRABLE population disposition as the "
        "current state)"
    ),
    "artifacts": [
        {
            "path": "research/gmi-833-corpus-passes-v2-v1/VERDICT_REGISTER_L47_REV_ADDENDUM_V1.json",
            "role": "REVIVAL_TICKET_CLOSURE_RECORD",
        }
    ],
}

SELF_BINDING_FILES = [
    ("research/gmi-833-theory-baseline-v1/SUPPLEMENT_2_REV_L47_CUSTODY_GAPS.md",
     "FREEZE_PACKAGE_SUPPLEMENT"),
    ("research/gmi-833-theory-baseline-v1/build_manifest_v3.py",
     "FREEZE_PACKAGE_SELF"),
]


def sha256_and_bytes(rel):
    # type: (str) -> tuple
    data = (REPO / rel).read_bytes()
    return hashlib.sha256(data).hexdigest(), len(data)


def main():
    # type: () -> int
    v1_sha, _ = sha256_and_bytes(PKG + "/BASELINE_MANIFEST_V1.json")
    if v1_sha != V1_MANIFEST_ANCHOR:
        print("REFUSED: BASELINE_MANIFEST_V1.json drifted from its anchor %s" % v1_sha)
        return 2
    v2_sha, _ = sha256_and_bytes(PKG + "/BASELINE_MANIFEST_V2.json")
    if v2_sha != V2_MANIFEST_ANCHOR:
        print("REFUSED: BASELINE_MANIFEST_V2.json drifted from its anchor %s" % v2_sha)
        return 2

    component = json.loads(json.dumps(CLOSURE_COMPONENT))
    for art in component["artifacts"]:
        sha, size = sha256_and_bytes(art["path"])
        art["sha256"] = sha
        art["bytes"] = size

    self_binding = []
    for rel, role in SELF_BINDING_FILES:
        sha, size = sha256_and_bytes(rel)
        self_binding.append({"path": rel, "sha256": sha, "bytes": size, "role": role})

    manifest = {
        "schema": "GMI_833_THEORY_BASELINE_MANIFEST_V3_SUPPLEMENT",
        "basis": "GMI_THEORY_BASELINE_V1 post-freeze supplement #2 (post_freeze_edit_rule)",
        "v1_manifest_sha256_anchored": v1_sha,
        "v2_manifest_sha256_anchored": v2_sha,
        "supplement_of": (
            "BASELINE_MANIFEST_V1.json (132 artifacts, byte-identical, still "
            "authoritative for everything it binds) and its V2 supplement "
            "(5 artifacts, byte-identical)"
        ),
        "bound_artifact_count": len(component["artifacts"]),
        "components": [component],
        "self_binding": self_binding,
        "revival_ticket_register_update": {
            "statement": (
                "Current-state movement of the baseline revival register; the "
                "pinned V1 register rows are frozen history and stay untouched"
            ),
            "closed": [
                {
                    "id": "REV-L47-CUSTODY-GAPS",
                    "status": "CLOSED_GREEN__18_OF_18_PRINCIPLED_TERMINALS",
                    "evidence": (
                        "research/gmi-833-rev-l47-custody-gaps-v1 (triage 6 "
                        "MECHANICAL / 12 SUBSTANTIVE, every decision cited; "
                        "6/6 mechanical custody legs demonstrated "
                        "(CUSTODY_REPAIR_RECEIPTS_V1.json); 12/12 "
                        "CLEARED_GREEN by prospective re-establishment under "
                        "freeze first-add 6061e111d, every receipt verifying "
                        "freeze-commit ancestry of its run commit, incl. the "
                        "section-d two-stage replica with stage-2 freeze "
                        "92197fc42 before any n=17/31 execution and an "
                        "in-repo-verified custody chain; see SUPPLEMENT_2 and "
                        "VERDICT_REGISTER_L47_REV_ADDENDUM_V1.json)"
                    ),
                    "permanent_record": (
                        "the 12 substantive packages' original landing "
                        "commit-order gaps remain recorded permanent custody "
                        "defects; content re-earned at original strength, "
                        "nothing retroactively cleansed. New pre-existing "
                        "defect routed: AJ9A-AUDIT-WALKER-LIST-EVASION (aj "
                        "lane; VERDICTS_V1.json new_findings)"
                    ),
                }
            ],
            "counts_after": {"total": 9, "closed": 5, "open": 4},
        },
        "u_new_arrivals_enumerated": [
            {
                "package": "research/gmi-833-rev-l47-custody-gaps-v1",
                "kind": "new research/gmi-* package (revival evidence lane)",
                "claim_ceiling": [
                    "REV_L47_CUSTODY_REPAIR_AND_PROSPECTIVE_REESTABLISHMENT_AT_REGISTERED_CORPUS_SCOPE"
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
                "BASELINE_MANIFEST_V1/V2 and every file they bind stay "
                "byte-identical; changes to V3-bound files require rebuilding "
                "V3 and updating the workflow anchor in the same commit "
                "(loud-change rule)"
            ),
            "validator": (
                "research/gmi-833-theory-baseline-v1/test_theory_baseline_v1.py "
                "re-derives every sha256 across ALL BASELINE_MANIFEST_V*.json "
                "from the live tree"
            ),
        },
    }

    out = REPO / PKG / "BASELINE_MANIFEST_V3.json"
    out.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
    print("wrote %s (%d bound artifacts + %d self-bound)" % (
        out, manifest["bound_artifact_count"], len(self_binding)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

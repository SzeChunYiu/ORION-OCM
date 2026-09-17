#!/usr/bin/env python3
"""Build BASELINE_MANIFEST_V2.json — the post-freeze supplement manifest for
GMI_THEORY_BASELINE_V1 (REV-L47-NOVEL-INTELLIGENCE-W4 closure).

Per the baseline post_freeze_edit_rule (BASELINE_MANIFEST_V1.json
governance): no bound artifact is edited in place; every change lands as a
supplement — a NEW file in the freeze package (SUPPLEMENT_1_*.md) plus new
owning-lane artifacts — and, when the binding changes, BASELINE_MANIFEST_V2.
V1 and every file it binds stay byte-identical; this builder refuses to run
if V1's manifest drifts from its recorded anchor.

Deterministic, stdlib-only. Run from anywhere:
  python3 -I -B research/gmi-833-theory-baseline-v1/build_manifest_v2.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PKG = "research/gmi-833-theory-baseline-v1"

# The V1 manifest is immutable; its committed sha256 (also anchored in the
# package workflow). A drift here means someone edited the freeze in place.
V1_MANIFEST_ANCHOR = "31de4041c0b6cb94152debbc4901041fb46626b9866122010a11df5319a62e97"

# The single new owning-lane artifact inside a frozen component package.
APPEND_COMPONENT = {
    "id": "revival-l47-w4-closure",
    "package": "research/gmi-833-corpus-passes-v2-v1",
    "pr": None,
    "child_issue": None,
    "role_in_baseline": (
        "post-freeze supplement per the baseline post_freeze_edit_rule: "
        "REV-L47-NOVEL-INTELLIGENCE-W4 closure record appended to the frozen "
        "corpus-passes package (VERDICT_REGISTER_V1.json and "
        "REVIVAL_TICKETS_V1.json stay byte-identical; this file supersedes "
        "their REV-L47 rows as the current state)"
    ),
    "artifacts": [
        {
            "path": "research/gmi-833-corpus-passes-v2-v1/VERDICT_REGISTER_APPEND_REV_L47_W4_V1.json",
            "role": "REVIVAL_TICKET_CLOSURE_RECORD",
        }
    ],
}

# Third-party post-freeze edit, restored + succeeded (post_freeze_edit_rule):
# the grammar-growth lane's #897/#978 reconciliation edited the V1-bound
# ISSUE_833_RECONCILIATION_GRAMMAR_GROWTH_V1.json in place on main (2881 ->
# 3265 bytes) without a manifest supplement; their PR never triggered the
# path-filtered baseline validator, so every later PR touching this package
# inherited a red merge tree. The validator's design gives in-place edits of
# V1-bound files NO supersession path ("every file it binds stays
# byte-identical"), so this lane restored the V1 bytes exactly and preserved
# the reconciled content byte-for-byte in the NEW successor file bound here.
# No reconciliation content is authored or altered by this lane.
RESTORED_SUCCESSOR_COMPONENT = {
    "id": "grammar-growth-reconciliation-restored-successor",
    "package": "research/gmi-833-g0-grammar-growth-v1",
    "pr": None,
    "child_issue": 897,
    "role_in_baseline": (
        "post-freeze edit of a V1-bound file restored to its bound bytes; "
        "the reconciled content preserved in this NEW successor file "
        "(byte-identical copy of main's post-#978 version), bound here per "
        "the post_freeze_edit_rule; authored by the grammar-growth lane "
        "(#897/#978), not by this lane"
    ),
    "artifacts": [
        {
            "path": "research/gmi-833-g0-grammar-growth-v1/ISSUE_833_RECONCILIATION_GRAMMAR_GROWTH_V2.json",
            "role": "RECONCILIATION_TABLE_SUCCESSOR_RESTORED_FROM_MAIN",
        }
    ],
}

# Third-party new artifacts in a frozen component, bound here (same rule):
# the claim-discipline lane landed an E9 registrations append (new files,
# the sanctioned append shape) without a manifest binding; their PRs never
# triggered the path-filtered baseline validator. Binding only — no content
# authored or altered by this lane.
UNBOUND_ARRIVALS_COMPONENT = {
    "id": "claim-discipline-e9-append-bound",
    "package": "research/gmi-833-claim-discipline-v1",
    "pr": None,
    "child_issue": None,
    "role_in_baseline": (
        "post-freeze new artifacts in a frozen component, bound here per "
        "the post_freeze_edit_rule ('plus any new artifacts in the owning "
        "lane ... and, when the binding changes, BASELINE_MANIFEST_V2'); "
        "authored by the claim-discipline lane, not by this lane"
    ),
    "artifacts": [
        {"path": "research/gmi-833-claim-discipline-v1/REGISTRATIONS_E9_APPEND.json",
         "role": "CLAIM_DISCIPLINE_APPEND"},
        {"path": "research/gmi-833-claim-discipline-v1/assemble_e9_append.py",
         "role": "CLAIM_DISCIPLINE_APPEND_TOOL"},
        {"path": "research/gmi-833-claim-discipline-v1/authored_e9_append.py",
         "role": "CLAIM_DISCIPLINE_APPEND_TOOL"},
    ],
}

SELF_BINDING_FILES = [
    ("research/gmi-833-theory-baseline-v1/SUPPLEMENT_1_revival-l47-novel-intelligence-w4.md",
     "FREEZE_PACKAGE_SUPPLEMENT"),
    ("research/gmi-833-theory-baseline-v1/build_manifest_v2.py",
     "FREEZE_PACKAGE_SELF"),
]


def sha256_and_bytes(rel):
    # type: (str) -> tuple
    data = (REPO / rel).read_bytes()
    return hashlib.sha256(data).hexdigest(), len(data)


def main():
    # type: () -> int
    v1_rel = PKG + "/BASELINE_MANIFEST_V1.json"
    v1_sha, _ = sha256_and_bytes(v1_rel)
    if v1_sha != V1_MANIFEST_ANCHOR:
        print("REFUSED: BASELINE_MANIFEST_V1.json drifted from its anchor %s" % v1_sha)
        return 2

    # NOTE: no context-dependent fields (branch names differ between the
    # working branch and CI's detached HEAD); the branch is recorded in
    # SUPPLEMENT_1 so the rebuild stays byte-identical everywhere.
    component = json.loads(json.dumps(APPEND_COMPONENT))
    for art in component["artifacts"]:
        sha, size = sha256_and_bytes(art["path"])
        art["sha256"] = sha
        art["bytes"] = size

    absorbed = json.loads(json.dumps(RESTORED_SUCCESSOR_COMPONENT))
    for art in absorbed["artifacts"]:
        sha, size = sha256_and_bytes(art["path"])
        art["sha256"] = sha
        art["bytes"] = size

    arrivals = json.loads(json.dumps(UNBOUND_ARRIVALS_COMPONENT))
    for art in arrivals["artifacts"]:
        sha, size = sha256_and_bytes(art["path"])
        art["sha256"] = sha
        art["bytes"] = size

    self_binding = []
    for rel, role in SELF_BINDING_FILES:
        sha, size = sha256_and_bytes(rel)
        self_binding.append({"path": rel, "sha256": sha, "bytes": size, "role": role})

    manifest = {
        "schema": "GMI_833_THEORY_BASELINE_MANIFEST_V2_SUPPLEMENT",
        "basis": "GMI_THEORY_BASELINE_V1 post-freeze supplement #1 (post_freeze_edit_rule)",
        "v1_manifest_sha256_anchored": v1_sha,
        "supplement_of": "BASELINE_MANIFEST_V1.json (132 artifacts, byte-identical, still authoritative for everything it binds)",
        "bound_artifact_count": (
            len(component["artifacts"]) + len(absorbed["artifacts"])
            + len(arrivals["artifacts"])
        ),
        "components": [component, absorbed, arrivals],
        "self_binding": self_binding,
        "revival_ticket_register_update": {
            "statement": (
                "Current-state movement of the baseline revival register; the "
                "pinned V1 register rows are frozen history and stay untouched"
            ),
            "closed": [
                {
                    "id": "REV-L47-NOVEL-INTELLIGENCE-W4",
                    "status": "CLOSED_GREEN__CONTENT_PROSPECTIVELY_RE_EARNED",
                    "evidence": "research/gmi-novel-intelligence-w4-prospective-v1 (freeze 56195abe precedes executor c1056b31/7438e4b3 precedes results; RESULT_V1.json verdict PROSPECTIVE_CONTENT_CONFIRMED__SUSPICION_CLEARED, D1-D5 all true; two-host bit-identical receipts; see SUPPLEMENT_1 and VERDICT_REGISTER_APPEND_REV_L47_W4_V1.json)",
                    "permanent_record": "the parent package's 89-minute freeze-after-result custody defect remains on its record; only prospective-ness of the CONTENT was re-earned",
                }
            ],
            "counts_after": {"total": 9, "closed": 4, "open": 5},
        },
        "u_new_arrivals_enumerated": [
            {
                "package": "research/gmi-novel-intelligence-w4-prospective-v1",
                "kind": "new research/gmi-* package (revival evidence lane)",
                "claim_ceiling": [
                    "W4_RESIDUAL_QUOTIENT_STRUCTURAL_DOMAIN_AT_REGISTERED_FINITE_FAMILY_SCOPE",
                    "NOVEL_INTEL_LADDER_W2_W3_W4_GREEN_AT_EXACT_RQM_FAMILY_SCOPE",
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
            "edit_rule": "BASELINE_MANIFEST_V1.json and every file it binds stay byte-identical; changes to V2-bound files require rebuilding V2 and updating the workflow anchor in the same commit (loud-change rule)",
            "validator": "research/gmi-833-theory-baseline-v1/test_theory_baseline_v1.py re-derives every sha256 across ALL BASELINE_MANIFEST_V*.json from the live tree",
        },
    }

    out = REPO / PKG / "BASELINE_MANIFEST_V2.json"
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("wrote %s (%d bound artifact(s) in %d components, %d self-binding file(s))" % (
        out, manifest["bound_artifact_count"],
        len(manifest["components"]), len(self_binding)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

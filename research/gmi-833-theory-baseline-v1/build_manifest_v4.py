#!/usr/bin/env python3
"""Build BASELINE_MANIFEST_V4.json — the third post-freeze supplement
manifest for GMI_THEORY_BASELINE_V1 (REV-L45-073-PROOF-STRENGTHENING
closure).

Per the baseline post_freeze_edit_rule: no bound artifact is edited in
place; this tranche appends ONE closure record to the frozen corpus-passes
package (VERDICT_REGISTER_APPEND_REV_L45_073_V1.json; VERDICT_REGISTER_V1.json
and REVIVAL_TICKETS_V1.json stay byte-identical) plus the new proof package
outside the frozen components. V4 binds the closure record, the proof
package artifacts, and moves the revival-ticket register current-state.

Deterministic, stdlib-only. Run from anywhere:
  python3 -I -B research/gmi-833-theory-baseline-v1/build_manifest_v4.py
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

CLOSURE_COMPONENT = {
    "id": "revival-l45-073-proof-strengthening-closure",
    "package": "research/gmi-833-corpus-passes-v2-v1",
    "pr": None,
    "child_issue": None,
    "role_in_baseline": (
        "post-freeze supplement per the baseline post_freeze_edit_rule: "
        "REV-L45-073-PROOF-STRENGTHENING closure record appended to the "
        "frozen corpus-passes package (VERDICT_REGISTER_V1.json and "
        "REVIVAL_TICKETS_V1.json stay byte-identical; this append carries "
        "the current L45 disposition, superseding the borderline_caveat "
        "recorded for re-review at the census-refresh round)"
    ),
    "artifacts": [
        {
            "path": "research/gmi-833-corpus-passes-v2-v1/VERDICT_REGISTER_APPEND_REV_L45_073_V1.json",
            "role": "REVIVAL_TICKET_CLOSURE_RECORD",
        },
        {
            "path": "research/gmi-morphology-phase-rv-proof-v2-v1/MORPHOLOGY_PHASE_RV_BOUNDARY_THEOREM_V2.md",
            "role": "STRENGTHENED_PROOF_THEOREM_DOC",
        },
        {
            "path": "research/gmi-morphology-phase-rv-proof-v2-v1/phase_rv_boundary_route2.py",
            "role": "STRENGTHENED_PROOF_ROUTE2_CHECKER",
        },
        {
            "path": "research/gmi-morphology-phase-rv-proof-v2-v1/RECEIPT_TWO_ROUTE_V1.json",
            "role": "STRENGTHENED_PROOF_TWO_ROUTE_RECEIPT",
        },
        {
            "path": "research/gmi-morphology-phase-rv-proof-v2-v1/test_phase_rv_proof_v2.py",
            "role": "STRENGTHENED_PROOF_TESTS",
        },
        {
            "path": "research/gmi-morphology-phase-rv-proof-v2-v1/MANIFEST.json",
            "role": "STRENGTHENED_PROOF_PACKAGE_MANIFEST",
        },
        {
            "path": "research/gmi-morphology-phase-rv-proof-v2-v1/CORE.md",
            "role": "STRENGTHENED_PROOF_PACKAGE_CORE",
        },
    ],
}

SELF_BINDING_FILES = [
    ("research/gmi-833-theory-baseline-v1/SUPPLEMENT_5_revival-l45-073-proof-strengthening.md",
     "FREEZE_PACKAGE_SUPPLEMENT"),
    ("research/gmi-833-theory-baseline-v1/build_manifest_v4.py",
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
    v3_sha, _ = sha256_and_bytes(PKG + "/BASELINE_MANIFEST_V3.json")
    if v3_sha != V3_MANIFEST_ANCHOR:
        print("REFUSED: BASELINE_MANIFEST_V3.json drifted from its anchor %s" % v3_sha)
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
        "schema": "GMI_833_THEORY_BASELINE_MANIFEST_V4_SUPPLEMENT",
        "basis": "GMI_THEORY_BASELINE_V1 post-freeze supplement #5 (post_freeze_edit_rule; numbering per #992 renumber; #991 took SUPPLEMENT_4 + V3)",
        "v1_manifest_sha256_anchored": v1_sha,
        "v2_manifest_sha256_anchored": v2_sha,
        "v3_manifest_sha256_anchored": v3_sha,
        "supplement_of": (
            "BASELINE_MANIFEST_V1.json (132 artifacts, byte-identical, still "
            "authoritative for everything it binds), its V2 supplement "
            "(5 artifacts) and V3 supplement (1 closure record), all "
            "byte-identical"
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
                    "id": "REV-L45-073-PROOF-STRENGTHENING",
                    "status": "CLOSED_GREEN__PROOF_STRENGTHENED_TO_FULL_SUPPORT_AT_STATED_SCOPE",
                    "evidence": (
                        "research/gmi-morphology-phase-rv-proof-v2-v1: the "
                        "morphology-phase RV claim's weakest-support caveat "
                        "resolved by strengthening the proof to full support "
                        "at the claim's stated scope — kernel-general "
                        "boundary theorems with a route-2 independent checker "
                        "(19 controls; two-host bit-identical receipts: "
                        "199,664 agreement cells, 0 disagreements; sandwich "
                        "proven for all R in both instantiations; exact "
                        "targets all match). See SUPPLEMENT_5 and "
                        "VERDICT_REGISTER_APPEND_REV_L45_073_V1.json"
                    ),
                    "permanent_record": (
                        "the original weakest-support disposition remains "
                        "recorded frozen history; the claim is strengthened, "
                        "not re-scoped — no boundary movement, no downgrade"
                    ),
                }
            ],
            "counts_after": {"total": 9, "closed": 6, "open": 3},
        },
        "u_new_arrivals_enumerated": [
            {
                "package": "research/gmi-morphology-phase-rv-proof-v2-v1",
                "kind": "new research/gmi-* package (revival evidence lane)",
                "claim_ceiling": [
                    "MORPHOLOGY_PHASE_RV_PROOF_V2_FULL_SUPPORT_AT_STATED_SCOPE_TWO_ROUTE_VERIFIED"
                ],
                "status": (
                    "revival-evidence package bound by V4 directly; holds no "
                    "baseline assertion until typed by the frozen mechanical "
                    "re-run (census extraction, maturity scoring, "
                    "claim-discipline registration, RAG strata, identification "
                    "screens) per the arrival_absorption_rule"
                ),
            }
        ],
        "governance": {
            "edit_rule": (
                "BASELINE_MANIFEST_V1/V2/V3 and every file they bind stay "
                "byte-identical; changes to V4-bound files require rebuilding "
                "V4 and updating the workflow anchor in the same commit "
                "(loud-change rule)"
            ),
            "validator": (
                "research/gmi-833-theory-baseline-v1/test_theory_baseline_v1.py "
                "re-derives every sha256 across ALL BASELINE_MANIFEST_V*.json "
                "from the live tree"
            ),
        },
    }

    out = REPO / PKG / "BASELINE_MANIFEST_V4.json"
    out.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
    print("wrote %s (%d bound artifacts + %d self-bound)" % (
        out, manifest["bound_artifact_count"], len(self_binding)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Verify the active runtime successor; preserve historical M7_RECEIPT_V1.json.
    python tools/m7_receipt.py --write-current  # create declared successor; never overwrite history
    python tools/m7_receipt.py --verify         # verify active successor; no historical fallback
Binds the pre-registration (its hash is the study identity), the protected suites, the V1
(DEV_CALIBRATION) and V2 (PROTECTED) comparison receipts, the BLiMP/UD receipt, the matched parent
and the harness.  Applies the pre-registered decision rules to the V2 claims: a family with fewer
pairs than the pre-registered minimum (40) is CANNOT_CHECK whatever its test verdict; a residual
over the matched parent is OCM_LANGUAGE_RESIDUAL_SUPPORTED; EQUIVALENT or RESIDUAL_B is
PARENT_SUFFICIENT; INCONCLUSIVE at n ≥ 40 is CANNOT_CHECK.  No claim beyond the table.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "docs" / "provenance" / "M7_RECEIPT_V1.json"
MIN_N = 40
BOUND = (
    "research/ocm-m7/M7_PREREGISTRATION_V1.md", "research/ocm-m7/M7_PROTECTED_CONVERSATIONS_V1.json", "research/ocm-m7/M7_PROTECTED_CONVERSATIONS_V2.json",
    "research/ocm-m7/M7_COMPARISON_V1.json", "research/ocm-m7/M7_COMPARISON_V2.json", "research/ocm-m7/M7_BLIMP_UD_V1.json",
    "src/ocm/comparators/matched_parent.py", "src/ocm/evaluation/m7_comparison.py", "src/ocm/evaluation/m7_blimp_ud.py", "src/ocm/evaluation/stats.py",
    "docs/provenance/M6_RECEIPT_V1.json", "docs/theorems/OCM_COMPARISON_OBLIGATION_REGISTRY_V1.json", "docs/M7_PROTECTED_COMPARISON_REPORT.md",
)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def decide(claim: dict) -> str:
    if claim["n"] < MIN_N:
        return "CANNOT_CHECK (n below pre-registered minimum)"
    v = claim["verdict"]
    if v == "RESIDUAL_A":
        return "OCM_LANGUAGE_RESIDUAL_SUPPORTED"
    if v in ("EQUIVALENT", "RESIDUAL_B"):
        return "PARENT_SUFFICIENT"
    return "CANNOT_CHECK (inconclusive at the margin)"


def fresh() -> dict:
    v2 = json.loads((ROOT / "research/ocm-m7/M7_COMPARISON_V2.json").read_text(encoding="utf-8"))
    v1 = json.loads((ROOT / "research/ocm-m7/M7_COMPARISON_V1.json").read_text(encoding="utf-8"))
    bu = json.loads((ROOT / "research/ocm-m7/M7_BLIMP_UD_V1.json").read_text(encoding="utf-8"))
    prereg = sha(ROOT / "research/ocm-m7/M7_PREREGISTRATION_V1.md")
    assert v2["preregistration_sha256"] == prereg, "V2 receipt was produced under a different pre-registration"
    table = {}
    for rq, arms in v2["claims"].items():
        table[rq] = {arm: {"n": c["n"], "ocm": c["ocm"], "other": c["other"], "difference": c.get("difference"), "ci_90": c.get("ci_90"), "test_verdict": c["verdict"], "terminal": decide(c)} for arm, c in arms.items()}
    external = {
        "BLiMP": {"terminal": "CANNOT_CHECK (coverage 0 under the frozen admissibility protocol)", "pairs": sum(v["pairs"] for v in bu["blimp"].values()), "covered": sum(v["covered"] for v in bu["blimp"].values())},
        "UD_EWT": {"terminal": "CANNOT_CHECK (coverage 0 under the frozen protocol)", "sentences": sum(v["sentences"] for v in bu["ud_ewt"].get("genres", {}).values()), "interpreted": sum(v["interpreted"] for v in bu["ud_ewt"].get("genres", {}).values())},
        "BabyLM": {"terminal": "CANNOT_CHECK_BABYLM_DATA"}, "CHILDES": {"terminal": "CANNOT_CHECK_CHILDES_DATA"},
        "human_rating": {"terminal": "CANNOT_CHECK (protocol frozen, not run)"}, "frontier_reference": {"terminal": "CANNOT_CHECK (external IO disabled; non-matched by design)"},
    }
    result = {"study": {"preregistration_sha256": prereg, "v1_status": v1.get("study_status", "DEV_CALIBRATION (system fixes S22–S24 made after V1 outcome access)"), "v2_status": v2["study_status"], "v2_conversations_sha256": v2["conversations_sha256"]},
              "terminal_table": table, "external_families": external, "laundering_audit": v2["laundering_audit"], "summary": v2["summary"], "information_budget": v2["information_budget"], "min_n": MIN_N}
    try:
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        head = "UNKNOWN"
    return {"receipt": "M7_RECEIPT_V1", "terminal": "MIXED (claim-by-claim; see terminal_table)", "git_head_at_generation": head, "bound_files": {rel: sha(ROOT / rel) for rel in BOUND}, "deterministic_results": result,
            "authority": "pre-registered protected comparison on the bounded world against the strongest faithful matched parent built here; external families CANNOT_CHECK by coverage/data terms; no human rating; no novelty claim"}


def main(argv: list[str]) -> int:
    from runtime_revision_receipts_v4 import revision_main

    return revision_main(ROOT, argv, 7)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

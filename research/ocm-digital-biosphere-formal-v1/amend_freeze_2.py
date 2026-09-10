#!/usr/bin/env python3
"""Record freeze amendment 2 against the #316 contract freeze."""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib  # noqa: E402

NAMED = ("HOSTILE_REGISTRY_V1.json", "THEOREM_REGISTRY_V1.json")
REASON = (
    "Harvest 1 cancelled maintenance 1, so BIO-T1 clean HOLD was vacuous (no births). "
    "BIO-T12 HOLD was hardcoded B-numbers. Optional social copy of useful_method made "
    "RESET identical to CONTINUED, confounding vertical inheritance with I_h (HDI-7). "
    "Six hostiles lacked clean controls in the live registry file the gate actually loads. "
    "CONTINUED>RESET on inherited methods is solution capital, not developmental "
    "intelligence (#323 HDI-2). This amendment records the live registry/theorem hashes "
    "and an executable code_digest so run_ebf0.py can refuse drift. No scored DEV-CAL-1 run. "
    "Long Earths remain refused."
)


def main():
    fz_path = os.path.join(HERE, lib.FREEZE_NAME)
    fz = lib.load_json(fz_path)
    if any(a.get("id") == 2 for a in fz.get("amendments", [])):
        raise SystemExit("REFUSED: amendment 2 already recorded")
    defs_live = lib.sha256_file(os.path.join(HERE, "DEFINITIONS.md"))
    defs_a1 = fz["amendments"][0]["manifest_sha256"]["DEFINITIONS.md"]
    if defs_live != defs_a1:
        raise SystemExit("REFUSED: DEFINITIONS.md drifted vs amendment 1")
    manifest = dict((n, lib.sha256_file(os.path.join(HERE, n))) for n in NAMED)
    code_files = lib.code_files_sha256(HERE)
    code_digest = lib.code_digest(HERE)
    fz.setdefault("amendments", []).append({
        "id": 2,
        "title": "Run-level BIO-T12 identification, registry hostiles, HDI-2 claim ceiling",
        "reason": REASON,
        "utc": lib.now(),
        "owner_issues": [296, 323],
        "manifest_sha256": manifest,
        "code_digest": code_digest,
        "code_files_sha256": code_files,
        "contains_results": False,
        "architecture_change_authorised": False,
    })
    fz["code_digest"] = code_digest
    fz["code_files_sha256"] = code_files
    cc = fz.setdefault("closure_conditions_section_17", {})
    cc["2_noninterference_machine_checkable"] = (
        "SATISFIED_FOR_DECLARED_GRAPH_AND_RUN_LEVEL_GRAPH_AGREEMENT")
    cc["4_resource_matching_and_knockout_frozen"] = (
        "SATISFIED_FOR_OBJECT_KNOCKOUT__SEARCH_GEOMETRY_RECEIPT_OPEN")
    cc["6_theorem_registry_parents_assumptions_falsifiers"] = (
        "SATISFIED_WEAKENINGS_IN_LIVE_REGISTRY")
    cc["7_hostiles_demonstrate_instruments_can_fail"] = (
        "SATISFIED_ALL_REGISTRY_IDS_PAIRED_AND_FIRING")
    fz["GATE_HOLDS"] = False
    fz["gate_holds_reason"] = (
        "Contract freeze does not assert GATE_HOLDS. Executable checkers may report "
        "GATE_HOLDS at micro-Earth scope only. That is not developmental intelligence "
        "(#323). DEV-CAL-1 is not run. #292 EB-2..EB-8 remain refused.")
    fz["long_earths_refused_until"] = (
        "EB-F0 executable GATE_HOLDS AND DEV-CAL-1 terminal AND #323 success certificate")
    sha = lib.write_json(fz_path, fz)
    print("amendment 2 recorded", sha[:16], "digest", code_digest[:16])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

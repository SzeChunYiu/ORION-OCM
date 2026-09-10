#!/usr/bin/env python3
"""Write FREEZE_V1.json BEFORE theorem/Earth certificates.

Refuses if results/ already contains certificates, or if freeze exists.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib  # noqa: E402


REQUIRED = (
    "DEFINITIONS.md",
    "PARENT_LEDGER.md",
    "WORLD_STATE_AND_DYNAMICS_V1.json",
    "COGNITIVE_UNIT_CONTRACT_V1.json",
    "INHERITANCE_SOCIAL_CHANNELS_V1.json",
    "COARSE_GRAINING_INDIVIDUALITY_V1.json",
    "ASSAY_TRANSFER_CONTRACT_V1.json",
    "THEOREM_REGISTRY_V1.json",
    "HOSTILE_REGISTRY_V1.json",
    "EXACT_WORLD_REGISTRY_V1.json",
)


def main() -> int:
    root = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else HERE
    freeze_path = os.path.join(root, lib.FREEZE_NAME)
    hits = lib.scored_certificates_exist(root)
    if hits:
        raise SystemExit("REFUSED: certificates exist: %s" % hits)
    if os.path.exists(freeze_path):
        raise SystemExit("REFUSED: freeze exists — supersession required")
    missing = [r for r in REQUIRED if not os.path.exists(os.path.join(root, r))]
    if missing:
        raise SystemExit("REFUSED: missing artifacts: %s" % missing)
    cg = lib.load_json(os.path.join(root, "COARSE_GRAINING_INDIVIDUALITY_V1.json"))
    if cg.get("frozen_winner_L_star") is not False:
        raise SystemExit("REFUSED: freeze would encode an L* winner")
    assay = lib.load_json(os.path.join(root, "ASSAY_TRANSFER_CONTRACT_V1.json"))
    if assay.get("future_domain_bridge", {}).get("biosphere_proves_language_math_science"):
        raise SystemExit("REFUSED: circular language/math/science claim")
    if assay.get("assay_feeds_reproduction_primary") is not False:
        raise SystemExit("REFUSED: primary assay-fitness leak in contract")

    digest = lib.code_digest(root)
    freeze = {
        "schema": "BIOSPHERE_EBF0_FREEZE_V1",
        "frozen_utc": lib.now(),
        "owner_issue": 296,
        "gates_issue": 292,
        "branch": "biosphere/eb-f0-formal",
        "evidence_class": "CONFIRMATORY_FIXED",
        "role": "FORMAL_PRECONDITION_NOT_A_COGNITIVE_CORE",
        "code_digest": digest,
        "code_files_sha256": lib.code_files_sha256(root),
        "outcome_neutral": True,
        "frozen_winner_L_star": False,
        "primary_fitness": "endogenous_resource_survival_reproduction",
        "assay_feeds_reproduction_primary": False,
        "biosphere_proves_language_math_science": False,
        "open_ended_forbidden_terminal": True,
        "long_earths_refused_until": "EB-F0 GATE_HOLDS",
        "agp": "research/heritable-search-geometry-v1/HSG_FREEZE_V1.json",
        "rgc": "append-only; defending this layer is a defect",
        "claim_ceilings": [
            "finite recurrence / horizon-scoped novelty",
            "Price is an identity not individuality",
            "no universal best inheritance or social mode",
            "language/math/science only via frozen continued-vs-reset + knockout",
        ],
    }
    sha = lib.write_json(freeze_path, freeze)
    lib.event("ebf0_freeze", sha256=sha, code_digest=digest)
    print("FREEZE", sha, "digest", digest[:16])
    return 0


if __name__ == "__main__":
    sys.exit(main())

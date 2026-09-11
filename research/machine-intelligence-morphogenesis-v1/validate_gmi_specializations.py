"""Validate that GMI specialization mappings use one canonical schema.

This is a theory-consistency check, not a capability test.
"""

from __future__ import annotations

import json
from pathlib import Path


CANONICAL = {"F", "Theta", "K", "U", "Gamma", "kappa", "rho_M"}
EXTERNAL = {"V_external", "C_external", "development_protocol_D"}


def validate(data: dict) -> dict:
    declared = set(data["canonical_morphology_fields"])
    external = set(data["external_fields"])
    if declared != CANONICAL:
        raise AssertionError(f"canonical schema drift: {declared ^ CANONICAL}")
    if external != EXTERNAL:
        raise AssertionError(f"external schema drift: {external ^ EXTERNAL}")

    seen = set()
    for family in data["families"]:
        family_id = family["id"]
        if family_id in seen:
            raise AssertionError(f"duplicate family id {family_id}")
        seen.add(family_id)

        missing = (CANONICAL | EXTERNAL | {"parent_anchors", "status", "id"}) - set(family)
        if missing:
            raise AssertionError(f"{family_id} missing {sorted(missing)}")
        for field in CANONICAL | EXTERNAL:
            value = family[field]
            if value in (None, "", []):
                raise AssertionError(f"{family_id}.{field} is empty")
        if not family["parent_anchors"]:
            raise AssertionError(f"{family_id} has no parent anchors")

    required_material_families = {
        "NEURAL_DIFFERENTIABLE",
        "SYMBOLIC_PRODUCTION",
        "PROBABILISTIC_GENERATIVE",
        "PROGRAMMATIC_LIBRARY_LEARNING",
    }
    if not required_material_families <= seen:
        raise AssertionError(
            f"missing required material families: {sorted(required_material_families - seen)}"
        )

    return {
        "families": len(seen),
        "canonical_fields": sorted(CANONICAL),
        "external_fields": sorted(EXTERNAL),
        "required_material_families_present": True,
        "terminal": "GMI_SPECIALIZATION_SCHEMA_STATIC_CHECK_GREEN",
    }


def main() -> None:
    here = Path(__file__).resolve().parent
    path = here / "GMI_SPECIALIZATION_CONTRACTS_V1.json"
    data = json.loads(path.read_text())
    print(json.dumps(validate(data), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

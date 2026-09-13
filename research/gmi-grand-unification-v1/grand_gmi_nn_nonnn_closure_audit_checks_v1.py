#!/usr/bin/env python3
"""Structural checks for GRAND_GMI_NN_NONNN_CLOSURE_MANIFEST_V1.

This checker verifies that the declared derivation DAG is fully typed and that
external premises/boundaries are not silently omitted. It does NOT prove the
mathematical truth of the referenced theorems or supply empirical premises.
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "GRAND_GMI_NN_NONNN_CLOSURE_MANIFEST_V1.json"

EXPECTED_EDGES = {f"E{i:02d}" for i in range(1, 18)}
EXPECTED_EXTERNAL = {f"X{i:02d}" for i in range(1, 7)}
EXPECTED_BOUNDARIES = {f"B{i:02d}" for i in range(1, 6)}
ALLOWED = {
    "INTERNAL_THEOREM",
    "INTERNAL_PLUS_PARENT",
    "INTERNAL_PLUS_EXTERNAL",
    "PARENT_THEOREM",
    "EXTERNAL_PREMISE",
    "IMPOSSIBILITY_BOUNDARY",
}


def main():
    data = json.loads(MANIFEST.read_text())
    edges = data["required_derivation_edges"]
    external = data["external_premises"]
    boundaries = data["impossibility_or_scope_boundaries"]

    assert set(edges) == EXPECTED_EDGES
    assert set(external) == EXPECTED_EXTERNAL
    assert set(boundaries) == EXPECTED_BOUNDARIES
    assert data["unclassified_required_edges"] == []
    assert data["universal_empirical_architecture_prediction_claimed"] is False
    assert set(data["allowed_edge_classes"]) == ALLOWED

    typed = 0
    for edge_id, edge in edges.items():
        assert edge["name"]
        assert edge["class"] in ALLOWED
        assert edge["class"] != "EXTERNAL_PREMISE"
        assert edge["class"] != "IMPOSSIBILITY_BOUNDARY"
        typed += 1

    # The explanatory DAG is formally closed only in the narrow manifest sense:
    # every required arrow is typed. Real-world verdicts can still be undecided.
    formal_closed = (
        typed == len(EXPECTED_EDGES)
        and not data["unclassified_required_edges"]
        and set(external) == EXPECTED_EXTERNAL
        and set(boundaries) == EXPECTED_BOUNDARIES
    )
    assert formal_closed
    assert data["terminal"] == "FORMALLY_CLOSED_AT_REGISTERED_SCOPE"

    receipt = {
        "terminal": "GRAND_GMI_NN_NONNN_FORMAL_CLOSURE_AUDIT_ALL_GREEN",
        "manifest_terminal": data["terminal"],
        "required_derivation_edges_typed": typed,
        "external_premises_explicit": len(external),
        "impossibility_or_scope_boundaries_explicit": len(boundaries),
        "unclassified_required_edges": 0,
        "universal_empirical_architecture_prediction_claimed": False,
        "checker_scope": "structural completeness of the registered derivation manifest; not a re-proof of theorem contents or empirical adequacy",
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

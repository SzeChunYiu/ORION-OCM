#!/usr/bin/env python3
"""L5 lesion closure: compose derived-lesion matrix + syndrome correspondence."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PARENT = REPO / "research/gmi-derived-lesion-v1"
CLAIM_CEILING = "L5_DERIVED_LESION_AND_SYNDROME_CORRESPONDENCE_AT_REGISTERED_SCOPE"
LESIONS = ("L_mem", "L_att", "L_plan", "L_causal", "L_social", "L_consol")
PRIMARY = {
    "L_mem": "T_mem",
    "L_att": "T_att",
    "L_plan": "T_plan",
    "L_causal": "T_causal",
    "L_social": "T_social",
    "L_consol": "T_consol",
}


def _load_parent_matrix():
    sys.path.insert(0, str(PARENT))
    import derived_lesion_v1 as dl  # noqa: WPS433

    return dl.build_deficit_matrix(), dl


def validate_closure() -> dict:
    matrix, dl = _load_parent_matrix()
    corr = json.loads((HERE / "SYNDROME_CORRESPONDENCE_V1.json").read_text(encoding="utf-8"))
    ledger = json.loads((HERE / "L5_BOX_LEDGER_V1.json").read_text(encoding="utf-8"))
    if corr["anatomical_identity"] != "FORBIDDEN":
        raise ValueError("top-level anatomical identity must be FORBIDDEN")
    if len(corr["rows"]) != 6:
        raise ValueError("expected six syndrome rows")
    if len(ledger["boxes"]) != 7 or any(b["status"] != "GREEN" for b in ledger["boxes"]):
        raise ValueError("L5 ledger drifted")

    for row in corr["rows"]:
        lesion = row["lesion"]
        if lesion not in LESIONS:
            raise ValueError("unknown lesion %s" % lesion)
        if row["anatomical_identity"] != "FORBIDDEN":
            raise ValueError("anatomical identity claimed for %s" % lesion)
        expected = row["predicted_profile"]
        actual = matrix[lesion]
        for task, bit in expected.items():
            if actual[task] != bit:
                raise ValueError("%s/%s profile mismatch: %s vs %s" % (lesion, task, actual[task], bit))
        primary = PRIMARY[lesion]
        if actual[primary] != 0:
            raise ValueError("%s primary %s not lesioned" % (lesion, primary))
        if not row["syndrome_label"] or not row["literature_anchor"]:
            raise ValueError("thin syndrome row for %s" % lesion)

    # Parent double-dissociation still holds.
    pairs = dl.find_all_dissociation_pairs(matrix)
    if len(pairs) < 3:
        raise ValueError("parent dissociation pairs missing")

    return {
        "lesions": 6,
        "syndrome_rows": 6,
        "anatomical_identity": "FORBIDDEN",
        "dissociation_pairs": len(pairs),
        "ledger_boxes": 7,
        "claim_ceiling": CLAIM_CEILING,
        "status": "PASS",
    }


def main() -> None:
    print(json.dumps(validate_closure(), indent=2, sort_keys=True))


class TestL5LesionClosure(unittest.TestCase):
    def test_validate(self):
        out = validate_closure()
        self.assertEqual(out["status"], "PASS")
        self.assertEqual(out["anatomical_identity"], "FORBIDDEN")
        self.assertEqual(out["lesions"], 6)

    def test_parent_tests_still_green(self):
        # Import-time sanity: parent module exports required APIs.
        sys.path.insert(0, str(PARENT))
        import derived_lesion_v1 as dl

        matrix = dl.build_deficit_matrix()
        self.assertEqual(matrix["none"]["T_mem"], 1)
        self.assertEqual(matrix["L_mem"]["T_mem"], 0)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-v":
        unittest.main(verbosity=2, argv=[sys.argv[0]] + sys.argv[2:])
    elif any(a.startswith("test") or a == "-v" for a in sys.argv[1:]):
        unittest.main(verbosity=2)
    else:
        main()

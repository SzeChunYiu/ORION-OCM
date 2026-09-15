"""#602 P1 predictive closure."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEDGER = HERE / "P1_LEDGER_V1.json"
RECEIPT = HERE / "RECEIPT_V1.json"
TERMINAL = "P1_PREDICTIVE_DOMAIN_CLOSURE_AT_REGISTERED_SCOPE"
BOXES = [
    "Harden D1-D8 domain basis.",
    "Test P0 new-domain candidates.",
    "Test RQM/VRQM/VGSC/IQL/LMHM/SCDI property-first predictions.",
]


def run():
    data = json.loads(LEDGER.read_text())
    forms_ok = all(
        v.get("property_vector_derived_before_impl")
        and v.get("neutral_recovery_registered")
        and v.get("parent_reduction_run")
        for v in data["property_first"].values()
    )
    ticks = {
        BOXES[0]: bool(data["harden_d1_d8"]["hardened"]),
        BOXES[1]: bool(data["p0_new_domain_candidates"]["tested"]),
        BOXES[2]: forms_ok and len(data["property_first"]) == 6,
    }
    out = {
        "schema": "GMIP1PredictiveReceiptV1",
        "terminal": TERMINAL,
        "boxes": ticks,
        "all_p1_boxes_green": all(ticks.values()),
        "forms": sorted(data["property_first"]),
    }
    RECEIPT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    return out


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))

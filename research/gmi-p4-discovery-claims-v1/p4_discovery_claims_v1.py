"""#602 P4 discovery claims."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEDGER = HERE / "P4_LEDGER_V1.json"
RECEIPT = HERE / "RECEIPT_V1.json"
TERMINAL = "P4_DISCOVERY_CLAIMS_SUPPORTED_AT_REGISTERED_SCOPE"
BOXES = [
    "Surviving unseen morphology.",
    "Surviving unseen domain.",
    "Replicated novel capability/resource frontier.",
    "Fresh predictions from the residual.",
]


def run():
    data = json.loads(LEDGER.read_text())
    ticks = {
        BOXES[0]: bool(data["surviving_unseen_morphology"]["green"]),
        BOXES[1]: bool(data["surviving_unseen_domain"]["green"]),
        BOXES[2]: bool(data["replicated_novel_frontier"]["green"]),
        BOXES[3]: bool(data["fresh_residual_predictions"]["green"]),
    }
    out = {
        "schema": "GMIP4DiscoveryReceiptV1",
        "terminal": TERMINAL,
        "boxes": ticks,
        "all_p4_boxes_green": all(ticks.values()),
        "forbidden_claims": ["NEW_FORM_OF_INTELLIGENCE_PROVEN", "ONTOLOGICAL_NOVELTY"],
    }
    RECEIPT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    return out


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))

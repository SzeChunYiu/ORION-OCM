"""#602 P3 transfer and energy scaling."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEDGER = HERE / "P3_LEDGER_V1.json"
RECEIPT = HERE / "RECEIPT_V1.json"
TERMINAL = "P3_TRANSFER_AND_ENERGY_SCALING_AT_REGISTERED_SCOPE"
BOXES = [
    "Code/math/science/control transfer.",
    "Physical resource/energy scaling.",
]


def run():
    data = json.loads(LEDGER.read_text())
    ticks = {
        BOXES[0]: bool(data["code_math_science_control_transfer"]["all_green"]),
        BOXES[1]: bool(data["physical_resource_energy_scaling"]["green"]),
    }
    out = {
        "schema": "GMIP3TransferEnergyReceiptV1",
        "terminal": TERMINAL,
        "boxes": ticks,
        "all_p3_boxes_green": all(ticks.values()),
        "n_transfer_arms": len(data["code_math_science_control_transfer"]["arms"]),
        "meters": data["physical_resource_energy_scaling"]["meters"],
    }
    RECEIPT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    return out


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))

"""#602 P0 zero-prior row closure."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROWS = HERE / "P0_ZERO_PRIOR_ROWS_V1.json"
RECEIPT = HERE / "RECEIPT_V1.json"
TERMINAL = "P0_KNOWN_FAMILY_ZERO_PRIOR_ROWS_CLOSED_AT_EXACT_LAYER"
BOX = "Close known-family zero-prior derivation rows from #431/#433."


def run():
    data = json.loads(ROWS.read_text())
    closed = [r for r in data["rows"] if r["disposition"] == "CLOSED_EXACT_LAYER"]
    open_blocking = [
        r
        for r in data["rows"]
        if r["disposition"] not in ("CLOSED_EXACT_LAYER", "TYPED_OPEN_NONBLOCKING")
    ]
    out = {
        "schema": "GMIP0ZeroPriorReceiptV1",
        "terminal": TERMINAL,
        "box": BOX,
        "tick": len(open_blocking) == 0 and len(closed) >= 5,
        "n_rows": len(data["rows"]),
        "n_closed_exact": len(closed),
        "n_open_blocking": len(open_blocking),
        "row_ids": [r["row_id"] for r in data["rows"]],
    }
    RECEIPT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    return out


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))

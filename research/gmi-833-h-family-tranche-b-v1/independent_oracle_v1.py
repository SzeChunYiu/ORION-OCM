from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> None:
    result = json.loads((HERE / "RESULT_V1.json").read_text())
    # Source-separated receipt projection: only public witness vectors are read.
    assert result["grammar"]["family_labels_in_generator"] is False
    assert all(row["finite_witness_match"] for row in result["rows"])
    print(json.dumps({"schema": "GMI833_HB_ORACLE_V1", "agrees": True,
                      "rows": len(result["rows"]), "closed_rows": []}, sort_keys=True))


if __name__ == "__main__":
    main()

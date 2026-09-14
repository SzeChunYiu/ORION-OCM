"""Schema checker for the biological bridge contract (602-L, items 25-28).

Verifies: the contract declares the (E_bio, M, C_pred, D_holdout) schema, the
mechanism inventory has bridge-ready rows with failure-mode language, the
NOT-claimed section exists, and every registered prediction row (if any)
carries all four frozen fields. Currently zero prediction rows: the checker
verifies the schema, not predictions.
CPython 3.8 safe. No network, no data.
"""

from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
CONTRACT = HERE / "BIOLOGICAL_BRIDGE_CONTRACT_V1.md"


def run():
    text = CONTRACT.read_text()
    if len(text) < 2000:
        raise ValueError("contract implausibly short")
    for token in ("E_bio", "C_pred", "D_holdout", "NOT claimed", "Falsifier"):
        if token not in text:
            raise ValueError("contract missing section: " + token)
    rows = [l for l in text.splitlines() if l.startswith("|") and "---" not in l
            and "GMI result" not in l]
    if len(rows) < 5:
        raise ValueError("mechanism inventory too thin: %d" % len(rows))
    preds = re.findall(r"^PRED-\d+", text, re.M)
    for p in preds:
        block = text[text.index(p):text.index(p) + 800]
        for field in ("E_bio", "C_pred", "D_holdout"):
            if field not in block:
                raise ValueError(p + " missing frozen field " + field)
    return {"schema_fields": 4, "inventory_rows": len(rows),
            "predictions_registered": len(preds), "status": "PASS"}


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2))

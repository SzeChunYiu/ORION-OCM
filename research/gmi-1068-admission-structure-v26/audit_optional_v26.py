"""Bind every original optional-component row to complete scoped evidence."""
import hashlib
import json
from pathlib import Path

PACKAGE = "research/gmi-1068-admission-structure-v26"
ORIGINAL = "research/gmi-1068-r1-minimal-process-core-v1/IRREDUCIBILITY_V1.json"
FIELDS = {"component", "status", "claim", "assumptions", "witness", "retained_observer",
          "information_not_recovered", "proof_level", "falsifier", "strongest_parent",
          "dependencies", "details"}


def need(value, message):
    if not value:
        raise ValueError(message)


def verify(root, ledger=None):
    root = Path(root)
    original_path = root / ORIGINAL
    original = json.loads(original_path.read_text())["removed_from_universal_minimum"]
    if ledger is None:
        ledger = json.loads((root / PACKAGE / "OPTIONAL_LEDGER_V26.json").read_text())
    need(type(ledger) is dict and set(ledger) == {
        "schema", "source", "observer", "boundary", "rows"}, "optional ledger fields")
    need(ledger["schema"] == "GMI_V26_OPTIONAL_STRUCTURE_V1", "optional ledger schema")
    expected_source = {"path": ORIGINAL,
                       "sha256": hashlib.sha256(original_path.read_bytes()).hexdigest(),
                       "pointer": "removed_from_universal_minimum"}
    need(type(ledger["source"]) is dict and ledger["source"] == expected_source,
         "original optional source binding")
    for field in ("observer", "boundary"):
        need(type(ledger[field]) is str and bool(ledger[field].strip()), "empty optional " + field)
    rows = ledger["rows"]
    need(type(rows) is list and len(rows) == len(original) == 6, "six original optional rows")
    for old, row in zip(original, rows):
        need(type(row) is dict and set(row) == FIELDS, "optional row fields")
        need(all(type(value) is str and bool(value.strip()) for value in row.values()),
             "optional row must contain explicit text")
        need(row["component"] == old["component"] and row["status"] == old["status"],
             "original optional component or status changed")
    return {"original_removed_components": [row["component"] for row in original],
            "reconciled_rows": len(rows)}

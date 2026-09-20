"""Bind every original survivor obligation to a complete source-keyed ledger row."""
import json
from pathlib import Path

PACKAGE = "research/gmi-1068-guarded-foundations-v25"
ORIGINAL = "research/gmi-1068-r1-minimal-process-core-v1/IRREDUCIBILITY_V1.json"
FIELDS = {"component", "original_loss", "corrected_survivor", "removed", "preserved",
          "model", "query", "response", "strongest_parent", "paper"}


def need(value, message):
    if not value:
        raise ValueError(message)


def verify(root, ledger=None):
    root = Path(root)
    original = json.loads((root / ORIGINAL).read_text())["retained"]
    if ledger is None:
        ledger = json.loads((root / PACKAGE / "SURVIVOR_LEDGER_V25.json").read_text())
    need(type(ledger) is dict and set(ledger) == {
        "schema", "original_source", "claim", "rows", "additional_controls"}, "ledger fields")
    need(ledger["schema"] == "GMI_V25_SIX_SURVIVOR_REPAIR_V1", "ledger schema")
    need(ledger["original_source"] == "../gmi-1068-r1-minimal-process-core-v1/IRREDUCIBILITY_V1.json",
         "original survivor source")
    need(type(ledger["claim"]) is str and bool(ledger["claim"].strip()), "ledger claim")
    rows = ledger["rows"]
    need(type(rows) is list and len(rows) == len(original) == 6, "six original survivors")
    for old, row in zip(original, rows):
        need(type(row) is dict and set(row) == FIELDS, "survivor row fields")
        need(all(type(value) is str and bool(value.strip()) for value in row.values()),
             "survivor row must contain explicit text")
        need(row["component"] == old["component"] and row["original_loss"] == old["loss"],
             "original survivor identity or loss changed")
    controls = ledger["additional_controls"]
    need(type(controls) is dict and set(controls) == {
        "coherence", "named_encoder", "equivalent_encodings"}, "control inventory")
    need(all(type(value) is str and bool(value.strip()) for value in controls.values()),
         "empty control mapping")
    return {"original_survivors": [row["component"] for row in original],
            "reconciled_rows": len(rows)}

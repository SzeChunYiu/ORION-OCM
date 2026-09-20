"""Reconcile the exact seven historical parent rows without certifying prose."""
import hashlib
import json
from pathlib import Path

PACKAGE = "research/gmi-1068-parent-translations-v27"
ORIGINAL = "research/gmi-833-aj1-operational-process-base-v1/PARENT_COMPARISON.json"
ORIGINAL_SHA = "1ff3d6049b22ef6def79c3259816753c2623c1fb266023dcbb6f99d951b81ce2"
OLD_FIELDS = {"name", "parents", "native", "additional_or_external", "status"}
NEW_FIELDS = {"map", "operations", "observer", "lost_data", "inverse_scope",
              "premises", "proof_level", "falsifier", "strongest_parent", "details"}


def need(value, message):
    if not value:
        raise ValueError(message)


def exact(actual, expected):
    if type(actual) is not type(expected):
        return False
    if type(expected) is list:
        return len(actual) == len(expected) and all(exact(x, y) for x, y in zip(actual, expected))
    if type(expected) is dict:
        return set(actual) == set(expected) and all(exact(actual[k], v) for k, v in expected.items())
    return actual == expected


def verify(root, ledger=None):
    root = Path(root)
    source = root / ORIGINAL
    need(hashlib.sha256(source.read_bytes()).hexdigest() == ORIGINAL_SHA, "original parent source drift")
    original = json.loads(source.read_text())["formalisms"]
    if ledger is None:
        ledger = json.loads((root / PACKAGE / "PARENT_TRANSLATIONS_V27.json").read_text())
    need(type(ledger) is dict and set(ledger) == {"schema", "source", "scope", "rows"}, "ledger fields")
    need(ledger["schema"] == "GMI_1068_PARENT_TRANSLATIONS_V27", "ledger schema")
    need(exact(ledger["source"], {"path": ORIGINAL, "sha256": ORIGINAL_SHA, "pointer": "formalisms"}),
         "original parent binding")
    need(type(ledger["scope"]) is str and bool(ledger["scope"].strip()), "empty scope")
    rows = ledger["rows"]
    need(type(rows) is list and len(rows) == len(original) == 7, "seven original parent rows required")
    for old, row in zip(original, rows):
        need(type(row) is dict and set(row) == OLD_FIELDS | NEW_FIELDS, "parent row fields")
        for field in OLD_FIELDS:
            need(exact(row[field], old[field]), "original parent identity or role drift")
        for field in NEW_FIELDS:
            need(type(row[field]) is str and bool(row[field].strip()), "missing parent translation text")
    return {"original_parent_ids": [row["name"] for row in original], "reconciled_rows": len(rows)}

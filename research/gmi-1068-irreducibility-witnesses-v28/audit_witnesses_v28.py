"""Exact original witness identities; this shape guard does not certify the added prose."""
import hashlib
import json
from pathlib import Path
import re

PACKAGE = "research/gmi-1068-irreducibility-witnesses-v28"
SOURCE = {
    "lean": {"path": "research/gmi-1068-r2-context-irreducibility-v1/ContextIrreducibility.lean",
             "sha256": "3b877eb125696b0e389529dc89295d9739ddcc4f26659e5c14dc9a1afcca88b7"},
    "paper": {"path": "research/gmi-1068-r2-context-irreducibility-v1/THEORY_V1.md",
              "sha256": "09773eab96a80843585154e6211e494b9ca721393542a8cbdd114fe7bae3ab5e"},
}
NAMES = ("ctx0_prefers_a0", "ctx1_prefers_a1", "same_process_different_context",
         "process_models_differ_under_same_context", "scalarization_can_reverse_incomparables")
FIRST = "## Theorem R2-1 — process law does not determine value/context"
SECTIONS = (FIRST, FIRST, FIRST, "## Theorem R2-2 — context does not determine process possibility",
            "## Scalarization boundary")
DETAILS = ("observer", "constructor_bridge", "omitted_data", "positive_converse", "premises",
           "proof_level", "strongest_parent", "falsifier", "details")
ORIGINAL = ("original_id", "original_statement", "original_source", "original_paper_section")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def verify(root):
    root = Path(root)
    texts = {}
    for key, record in SOURCE.items():
        raw = (root / record["path"]).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == record["sha256"], "immutable original source drift")
        texts[key] = raw.decode()
    ledger = json.loads((root / PACKAGE / "WITNESS_TRANSLATIONS_V28.json").read_text())
    need(type(ledger) is dict and set(ledger) == {"schema", "source", "rows"}, "witness ledger keys")
    need(ledger["schema"] == "GMI_1068_IRREDUCIBILITY_WITNESSES_V28", "witness ledger schema")
    need(ledger["source"] == SOURCE, "original source identity")
    rows = ledger["rows"]
    need(type(rows) is list and len(rows) == len(NAMES), "original witness inventory")
    for name, section, row in zip(NAMES, SECTIONS, rows):
        matches = re.findall(r"(theorem " + re.escape(name) + r"\b[\s\S]*?)(?=:=)", texts["lean"])
        need(len(matches) == 1 and section in texts["paper"].splitlines(), "original locator unavailable")
        need(type(row) is dict and set(row) == set(ORIGINAL + DETAILS), "witness row fields")
        expected = dict(zip(ORIGINAL, (name, matches[0], SOURCE["lean"]["path"], section)))
        need(all(type(row[k]) is str and row[k] == v for k, v in expected.items()), "original witness changed")
        need(all(type(row[k]) is str and row[k].strip() for k in DETAILS), "empty witness translation")
    return {"original_theorems": list(NAMES), "reconciled_rows": len(rows)}

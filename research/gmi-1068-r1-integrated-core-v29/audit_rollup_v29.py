"""Literal original crosswalk and source locators; this is not a prose-truth oracle."""
import ast
import hashlib
import json
from pathlib import Path
import re

PACKAGE = "research/gmi-1068-r1-integrated-core-v29"
CROSSWALK_SHA = "50aac7a4ed2e226d86373199a19c81a312795d6e4f01df177a11b3bab7cd0297"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    if type(value) is dict:
        need(all(type(k) is str for k in value), "JSON keys must be strings")
        for item in value.values():
            canonical(item)
    elif type(value) is list:
        for item in value:
            canonical(item)
    else:
        need(type(value) in (str, int, bool, type(None)), "noncanonical JSON value")
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def pointer(value, locator):
    need(type(locator) is str and locator.startswith("/"), "JSON pointer required")
    for part in locator[1:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        value = value[int(part)] if type(value) is list else value[part]
    return value


def verify(root, ledger=None):
    root = Path(root).resolve()
    raw = (root / PACKAGE / "ORIGINAL_CROSSWALK_V29.json").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == CROSSWALK_SHA, "frozen crosswalk drift")
    expected = json.loads(raw)
    ledger = expected if ledger is None else ledger
    need(canonical(ledger) == canonical(expected), "registered original crosswalk drift")
    texts = {}
    for key, source in ledger["sources"].items():
        relative = Path(source["path"])
        need(not relative.is_absolute() and ".." not in relative.parts, "source path escape")
        path = (root / relative).resolve()
        need(path.is_relative_to(root), "source symlink escape")
        data = path.read_bytes()
        need(hashlib.sha256(data).hexdigest() == source["sha256"], "original source drift")
        texts[key] = data.decode()
    located = []

    def locate(record):
        text = texts[record["source"]]
        kind, where = record["kind"], record["locator"]
        if kind == "json_pointer":
            value = pointer(json.loads(text), where)
        elif kind == "python_symbol":
            value = [n for n in ast.walk(ast.parse(text))
                     if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == where]
            need(bool(value), "Python locator missing")
        elif kind == "lean_declaration":
            value = re.search(r"\b(?:theorem|lemma|def|abbrev|structure|class|inductive)\s+"
                              + re.escape(where) + r"\b", text)
            need(value is not None, "Lean locator missing")
        elif kind == "markdown_heading":
            value = [line for line in text.splitlines() if line.startswith("#")
                     and line.lstrip("#").strip() == where]
            need(bool(value), "heading locator missing")
        else:
            raise ValueError("unsupported frozen locator kind")
        located.append((record["source"], kind, where))
        return value

    def walk(value):
        if type(value) is dict:
            if {"source", "kind", "locator"} <= set(value):
                locate(value)
            for item in value.values():
                walk(item)
        elif type(value) is list:
            for item in value:
                walk(item)
    walk(ledger)
    results = ledger["required_results"]
    need(len(results) == 8, "eight original results required")
    for row in results:
        lines = texts[row["source"]].splitlines()
        need(lines[row["line"] - 1] == row["original_line"], "original result text drift")
        need(row["heading"] in lines and row["original_line"].split(". ", 1)[1] == row["text"],
             "original result heading/body drift")
    atoms = ledger["atoms"]
    need(len(atoms) == 10, "ten original R1 records required")
    for row in atoms:
        ref = row["complete_prior_record"]
        old = pointer(json.loads(texts[ref["source"]]), ref["locator"])
        for current, prior in (("id", "id"), ("title", "title"),
                               ("current_status", "status"), ("current_disposition", "disposition")):
            need(canonical(row[current]) == canonical(old[prior]), "original atom record drift")
    scope = ledger["original_scope"]
    ref = scope["predecessor_scope_source"]
    old = pointer(json.loads(texts[ref["source"]]), ref["locator"])
    need(scope["predecessor_round_scope"] == old, "historical scope drift")
    counts = [len(row["ordered_rows"]) for row in ledger["inherited_ledgers"]]
    need(counts == [6, 6, 7], "inherited ledger coverage drift")
    return {"original_results": [row["id"] for row in results],
            "original_atoms": [row["id"] for row in atoms],
            "survivor_rows": 6, "optional_rows": 6, "parent_rows": 7,
            "source_records": len(texts), "located_records": len(located)}

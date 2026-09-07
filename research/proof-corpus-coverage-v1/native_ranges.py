"""Derive selectors from SHA-bound lexical wrapper segments; never choose a theorem.

The current registered header grammar is deliberately the inventory's grammar.
Compiler source ranges remain evidence under the pinned source/build profile,
not a cryptographic attestation produced by this helper.
"""
import hashlib
import re

HEADER = re.compile(r"[ \t]*(?:(?:private|protected|noncomputable)\s+)*"
                    r"(?:theorem|lemma)\s+(?P<name>[A-Za-z_][A-Za-z0-9_'.]*)(?![A-Za-z0-9_'.])")
LEGACY_HEADER = re.compile(HEADER.pattern.replace("(?![A-Za-z0-9_'.])", r"\b"))
PARTS = ("context", "declaration", "bridge", "trailing")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def position(text, offset):
    prefix = text[:offset]
    return {"line": prefix.count("\n") + 1, "column": len(prefix.rsplit("\n", 1)[-1])}


def prepare_selector(raw, record, source_path):
    if type(raw) is not bytes or type(record) is not dict or type(source_path) is not str:
        raise ValueError("SELECTOR_INPUT_TYPES")
    if type(record.get("wrapper_bytes")) is not int or record["wrapper_bytes"] != len(raw):
        raise ValueError("WRAPPER_SOURCE_BINDING")
    if record.get("wrapper_sha256") != digest(raw):
        raise ValueError("WRAPPER_SOURCE_BINDING")
    text = raw.decode("utf-8", errors="strict")
    parts = []
    for name in PARTS:
        value = record.get(name + "_source")
        if type(value) is not str or record.get(name + "_sha256") != digest(value.encode()):
            raise ValueError("SEGMENT_BINDING:" + name)
        parts.append(value)
    if "".join(parts) != text:
        raise ValueError("SEGMENT_RECONSTRUCTION")
    context, declaration, bridge, _ = parts
    header = HEADER.match(declaration)
    if header is None or not bridge or bridge != bridge.rstrip():
        raise ValueError("REGISTERED_HEADER_LAYOUT")
    legacy_status = "MATCHED"
    if header["name"] != record.get("theorem_name"):
        legacy = LEGACY_HEADER.match(declaration)
        suffix = header["name"][len(legacy["name"]):] if legacy else ""
        if (legacy is None or legacy["name"] != record.get("theorem_name")
                or not suffix or set(suffix) != {"'"}):
            raise ValueError("REGISTERED_HEADER_NAME")
        legacy_status = "CORRECTED_LEGACY_NAME_BOUNDARY"
    module = record.get("theorem_id")
    if type(module) is not str or not re.fullmatch(r"Theorems\.Thm_[A-Za-z0-9_']+", module):
        raise ValueError("REGISTERED_MODULE_ID")
    if record.get("lexical_only") is not True or record.get("semantic_correspondence") != "NOT_ELABORATED":
        raise ValueError("LEXICAL_RECORD_CONTRACT")
    base = len(context)
    start = base + len(declaration) - len(declaration.lstrip(" \t"))
    stop = base + len(declaration) + len(bridge)
    selection_start, selection_end = (base + n for n in header.span("name"))
    span = lambda a, b: {"start": position(text, a), "end": position(text, b)}
    return {
        "request": {
            "schema": "ocm.coverage.capture.v1", "operation": "capture",
            "module": module.split("."), "source_path": source_path,
            "range": span(start, stop),
            "selection_range": span(selection_start, selection_end),
        },
        "provenance": {
            "schema": "ocm.coverage.source-selector.v1", "wrapper_sha256": digest(raw),
            "wrapper_bytes": len(raw), "theorem_id": module,
            "source_header_name": header["name"], "legacy_theorem_name": record["theorem_name"],
            "legacy_name_status": legacy_status,
            "segments": {name: record[name + "_sha256"] for name in PARTS},
            "coordinate_system": "line1-column0-Unicode-codepoints",
            "range_kind": "registered-core-declaration",
            "semantic_association": "REQUIRES_COMPILED_ORIGIN_AND_RANGE_CHECK",
        },
    }

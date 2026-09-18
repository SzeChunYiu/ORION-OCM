"""Exact parser and invariant checker for the #833 checklist of record.

Pure stdlib. No network. Every operation here is total and deterministic: the
same body text always yields the same rows, keys and ledger.

Vocabulary
----------
row text      the stated obligation, e.g. "Identify circular dependencies."
evidence      the annotation appended to a closed row after the separator
row key       sha256 of (section header + "\\x00" + row text); stable under
              compaction because neither component is ever rewritten
"""

import hashlib
import io
import json

SEP = u" — ✅ "          # " — ✅ "
OPEN_PREFIX = u"- [ ] "
DONE_PREFIX = u"- [x] "
BODY_LIMIT = 65536               # GitHub issue body character ceiling


class ChecklistError(Exception):
    pass


def _key(section, text):
    h = hashlib.sha256()
    h.update(section.encode("utf-8"))
    h.update(b"\x00")
    h.update(text.encode("utf-8"))
    return h.hexdigest()


def parse(body):
    """Return (rows, trailing_defect).

    rows is a list of dicts with keys: line_no, section, checked, text,
    evidence, key, raw. trailing_defect is None, or the verbatim malformed
    tail found at the end of the body (the D1 truncation).
    """
    rows = []
    section = u""
    defect = None
    lines = body.split(u"\n")
    for i, raw in enumerate(lines):
        if raw.startswith(u"# "):
            section = raw
            continue
        if raw.startswith(DONE_PREFIX) or raw.startswith(OPEN_PREFIX):
            checked = raw.startswith(DONE_PREFIX)
            rest = raw[len(DONE_PREFIX):]
            if SEP in rest:
                if rest.count(SEP) != 1:
                    raise ChecklistError("ambiguous separator on line %d" % (i + 1))
                text, evidence = rest.split(SEP)
            else:
                text, evidence = rest, u""
            if checked and not evidence:
                raise ChecklistError("checked row without evidence on line %d" % (i + 1))
            if (not checked) and evidence:
                raise ChecklistError("unchecked row with evidence on line %d" % (i + 1))
            rows.append({
                "line_no": i + 1,
                "section": section,
                "checked": checked,
                "text": text,
                "evidence": evidence,
                "key": _key(section, text),
                "raw": raw,
            })
            continue
        # a checkbox token that does not form a complete row is the D1 defect
        stripped = raw.strip()
        if stripped and stripped.startswith(u"- [") and not stripped.startswith(
                (DONE_PREFIX.strip(), OPEN_PREFIX.rstrip())):
            defect = raw
    return rows, defect


def duplicate_keys(rows):
    seen, dupes = {}, []
    for r in rows:
        if r["key"] in seen:
            dupes.append((seen[r["key"]], r["line_no"]))
        else:
            seen[r["key"]] = r["line_no"]
    return dupes


def signature(rows):
    """The invariant a rewrite must preserve: ordered (key, checked) pairs."""
    return [(r["key"], r["checked"]) for r in rows]


def build_ledger(rows, source_sha=None):
    entries = []
    for r in rows:
        entries.append({
            "key": r["key"],
            "section": r["section"],
            "text": r["text"],
            "checked": r["checked"],
            "evidence": r["evidence"],
        })
    return {
        "schema": "GMI_833_CHECKLIST_EVIDENCE_LEDGER_V1",
        "issue": 833,
        "source_body_sha256": source_sha,
        "row_count": len(rows),
        "checked": sum(1 for r in rows if r["checked"]),
        "unchecked": sum(1 for r in rows if not r["checked"]),
        "separator_codepoints": [ord(c) for c in SEP],
        "entries": entries,
    }


def body_sha256(body):
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def read_text(path):
    with io.open(path, encoding="utf-8") as fh:
        return fh.read()


def write_text(path, text):
    with io.open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def write_json(path, obj):
    with io.open(path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=False))
        fh.write(u"\n")

"""Pointer-form compaction for the #833 checklists that live in issue COMMENTS.

The body hit the 65,536-character ceiling once; the AE comment is now at it
(21 earned rows could not be applied: 76,267 chars). Same remedy as the body:
move each closed row's evidence into a ledger keyed by
sha256(section NUL row_text) and leave `refs pkg L:<12 hex>` in the comment.

Invariants, each with a hostile in the tests:
  I1  no row's stated text changes
  I2  no row's checked/unchecked disposition changes
  I3  the ledger holds REAL evidence for every closed row, never the row's own
      pointer (the defect that once destroyed 168 body annotations)

    python3 -I -B compact_comment_v1.py COMMENT.md OUT.md LEDGER.json
"""
import hashlib
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import checklist_core_v1 as core

SEP = core.SEP
REF = re.compile(r"#\d+")
TICK = re.compile(r"`([^`]+)`")
LIMIT = 65536
LEDGER_PATH_LOCAL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "COMMENT_EVIDENCE_LEDGER_V1.json")


def _key(section, text):
    h = hashlib.sha256(); h.update(section.encode("utf-8")); h.update(b"\x00")
    h.update(text.encode("utf-8")); return h.hexdigest()


def _is_pointer(evidence, key):
    return evidence.rstrip().endswith("L:" + key[:12])


def parse(body):
    """Rows of a comment checklist. Headings are `##`/`###`; rows may be indented."""
    rows = []; section = u""
    in_fence = False
    for i, raw in enumerate(body.split(u"\n")):
        if raw.strip().startswith(u"```"):
            in_fence = not in_fence; continue
        if in_fence:
            continue
        if re.match(r"^#{1,6}\s", raw):
            section = raw.strip(); continue
        m = re.match(r"^(\s*)- \[([ x])\] (.*)$", raw)
        if not m:
            continue
        indent, mark, rest = m.group(1), m.group(2), m.group(3)
        checked = mark == "x"
        if SEP in rest:
            if rest.count(SEP) != 1:
                raise core.ChecklistError("ambiguous separator on line %d" % (i + 1))
            text, evidence = rest.split(SEP)
        else:
            text, evidence = rest, u""
        rows.append({"line_no": i + 1, "section": section, "indent": indent,
                     "checked": checked, "text": text, "evidence": evidence,
                     "key": _key(section, text), "raw": raw})
    return rows


def pointer(evidence, key):
    refs = REF.findall(evidence)[:3]
    ticks = TICK.findall(evidence)
    pkg = next((t for t in ticks if t.startswith(u"gmi-") or t.endswith((u".json", u".py"))), ticks[0] if ticks else u"")
    parts = []
    if refs: parts.append(u" ".join(refs))
    if pkg: parts.append(u"`%s`" % pkg)
    ids = re.findall(r"\b[A-Z]{2,6}-?\d+[A-Za-z]?\b", evidence)[:4]
    if ids: parts.append(u"/".join(dict.fromkeys(ids)))
    if not parts: parts.append(evidence.split(u":")[0][:48].strip())
    parts.append(u"L:%s" % key[:12])
    return u" ".join(parts)


def signature(rows):
    return [(r["key"], r["checked"]) for r in rows]


def compact(body, comment_id, prior_ledger=None):
    rows = parse(body)
    keys = [r["key"] for r in rows]
    if len(set(keys)) != len(keys):
        raise SystemExit("REFUSED: duplicate row keys in comment %s" % comment_id)
    before = signature(rows); texts = [r["text"] for r in rows]
    lines = body.split(u"\n")
    moved = 0
    entries = []
    prior = {}
    src = prior_ledger if prior_ledger is not None else (
        json.load(io.open(LEDGER_PATH_LOCAL, encoding="utf-8")) if os.path.exists(LEDGER_PATH_LOCAL) else {"entries": []})
    for e in src.get("entries", []):
        prior[e["key"]] = e.get("evidence", u"")
    for r in rows:
        ev = r["evidence"]
        if r["checked"] and _is_pointer(ev, r["key"]):
            was = prior.get(r["key"], u"")
            if was and not _is_pointer(was, r["key"]):
                ev = was  # never let a pointer overwrite real evidence
        entries.append({"comment_id": comment_id, "key": r["key"], "section": r["section"],
                        "text": r["text"], "checked": r["checked"], "evidence": ev})
        if r["checked"] and not _is_pointer(r["evidence"], r["key"]):
            lines[r["line_no"] - 1] = r["indent"] + u"- [x] " + r["text"] + SEP + pointer(r["evidence"], r["key"])
            moved += 1
    new = u"\n".join(lines)
    after = parse(new)
    if signature(after) != before or [r["text"] for r in after] != texts:
        raise SystemExit("REFUSED: I1/I2 violated")
    by_key = {e["key"]: e["evidence"] for e in entries}
    for r in rows:
        if r["checked"] and (r["key"] not in by_key or _is_pointer(by_key[r["key"]], r["key"])):
            raise SystemExit("REFUSED: I3 - ledger would hold only a pointer for %r" % r["text"][:60])
    ledger = {"schema": "GMI_833_COMMENT_EVIDENCE_LEDGER_V1", "comment_id": comment_id,
              "source_body_sha256": core.body_sha256(body), "row_count": len(rows),
              "checked": sum(1 for r in rows if r["checked"]),
              "unchecked": sum(1 for r in rows if not r["checked"]), "entries": entries,
              "compaction": {"rows_compacted": moved, "chars_before": len(body), "chars_after": len(new),
                             "headroom_after": LIMIT - len(new)}}
    return new, ledger


def merge_ledger(path, ledger):
    """Union a per-comment ledger into the shared comment ledger, never downgrading."""
    allv = json.load(io.open(path, encoding="utf-8")) if os.path.exists(path) else {
        "schema": "GMI_833_COMMENT_EVIDENCE_LEDGER_V1", "entries": []}
    idx = {(e["comment_id"], e["key"]): e for e in allv["entries"]}
    for e in ledger["entries"]:
        k = (e["comment_id"], e["key"]); old = idx.get(k)
        if old and old.get("checked") and not _is_pointer(old.get("evidence", u""), e["key"]) and _is_pointer(e["evidence"], e["key"]):
            continue
        idx[k] = e
    allv["entries"] = sorted(idx.values(), key=lambda e: (e["comment_id"], e["section"], e["text"]))
    allv["comment_count"] = len({e["comment_id"] for e in allv["entries"]})
    core.write_json(path, allv)
    return allv


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(__doc__); sys.exit(2)
    src, cid, out, led = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
    body = core.read_text(src)
    new, ledger = compact(body, cid)
    core.write_text(out, new); core.write_json(led, ledger)
    c = ledger["compaction"]
    print("comment %d: %d rows compacted; %d -> %d chars; headroom %d -> %d" % (
        cid, c["rows_compacted"], c["chars_before"], c["chars_after"], LIMIT - c["chars_before"], c["headroom_after"]))

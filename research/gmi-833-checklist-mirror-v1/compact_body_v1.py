"""Length-recovering rewrite of the #833 body under loss-forbidding invariants.

The programme's closed rows carry long inline evidence annotations. With 92
rows still open and 1,505 characters of headroom at freeze time, the checklist
of record cannot reach closure in that form. This tool moves each closed row's
full evidence into EVIDENCE_LEDGER_V1.json and leaves a short resolvable
pointer in the body.

Invariants enforced (I1-I3 of FREEZE_V1.md), each with a hostile in the tests:
  I1  no row's stated text changes
  I2  no row's checked/unchecked disposition changes
  I3  every removed evidence annotation is in the ledger, byte-exact

Usage
-----
    python3 -I -B compact_body_v1.py BODY.md OUT.md LEDGER.json
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import checklist_core_v1 as core

LEDGER_PATH = u"research/gmi-833-checklist-mirror-v1/EVIDENCE_LEDGER_V1.json"
REF = re.compile(r"#\d+")
TICK = re.compile(r"`([^`]+)`")

NOTE = (
    u"> **Evidence pointers.** A closed row ends with its source refs, package name and "
    u"a ledger key `L:<12 hex>`. The full evidence text for every row is held byte-exact "
    u"in [%s](%s) under that key, together with the row's stated text and section. "
    u"Row texts are never rewritten here; see "
    u"`research/gmi-833-checklist-mirror-v1/FREEZE_V1.md` for the invariants and the "
    u"measured defect this replaces."
) % (LEDGER_PATH, LEDGER_PATH)


def pointer(evidence, key):
    refs = REF.findall(evidence)[:3]
    ticks = TICK.findall(evidence)
    pkg = u""
    for t in ticks:
        if t.startswith(u"gmi-") or t.endswith(u".json") or t.endswith(u".py"):
            pkg = t
            break
    if not pkg and ticks:
        pkg = ticks[0]
    parts = []
    if refs:
        parts.append(u" ".join(refs))
    if pkg:
        parts.append(u"`%s`" % pkg)
    if not parts:
        parts.append(evidence.split(u":")[0][:48].strip())
    parts.append(u"L:%s" % key[:12])
    return u" ".join(parts)


def compact(body):
    rows, defect = core.parse(body)
    dupes = core.duplicate_keys(rows)
    if dupes:
        raise SystemExit("REFUSED: duplicate row keys %r" % dupes[:3])
    before = core.signature(rows)
    texts_before = [r["text"] for r in rows]

    lines = body.split(u"\n")
    moved = 0
    for r in rows:
        if not r["checked"]:
            continue
        lines[r["line_no"] - 1] = (
            core.DONE_PREFIX + r["text"] + core.SEP + pointer(r["evidence"], r["key"]))
        moved += 1

    # insert the explanatory note directly after the title line
    for i, ln in enumerate(lines):
        if ln.startswith(u"# "):
            lines.insert(i + 1, u"")
            lines.insert(i + 2, NOTE)
            break

    new = u"\n".join(lines)

    rows_after, defect_after = core.parse(new)
    if core.signature(rows_after) != before:
        raise SystemExit("REFUSED: I1/I2 violated - row signature changed")
    if [r["text"] for r in rows_after] != texts_before:
        raise SystemExit("REFUSED: I1 violated - row text changed")
    if defect_after != defect:
        raise SystemExit("REFUSED: trailing defect state changed")

    ledger = core.build_ledger(rows, core.body_sha256(body))
    ledger["compaction"] = {
        "rows_compacted": moved,
        "body_chars_before": len(body),
        "body_chars_after": len(new),
        "chars_reclaimed": len(body) - len(new),
        "headroom_after": core.BODY_LIMIT - len(new),
        "trailing_defect": defect,
    }
    # I3: every removed annotation must be recoverable, byte-exact
    by_key = dict((e["key"], e["evidence"]) for e in ledger["entries"])
    for r in rows:
        if r["checked"] and by_key.get(r["key"]) != r["evidence"]:
            raise SystemExit("REFUSED: I3 violated for row %r" % r["text"][:60])
    return new, ledger


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    src, out, led = argv
    body = core.read_text(src)
    new, ledger = compact(body)
    core.write_text(out, new)
    core.write_json(led, ledger)
    c = ledger["compaction"]
    print("rows compacted : %d" % c["rows_compacted"])
    print("body chars     : %d -> %d (reclaimed %d)"
          % (c["body_chars_before"], c["body_chars_after"], c["chars_reclaimed"]))
    print("headroom       : %d -> %d"
          % (core.BODY_LIMIT - c["body_chars_before"], c["headroom_after"]))
    print("ledger entries : %d (%d checked / %d unchecked)"
          % (ledger["row_count"], ledger["checked"], ledger["unchecked"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

"""Mandatory write path for the #833 issue body.

A GitHub issue body has no server-side history: a write replaces the previous
body irrecoverably. A pre/post count assertion does not protect a shared body,
because the count is derived from the caller's own stale snapshot and passes
while a concurrent lane's edit is erased. This tool therefore re-fetches the
live body immediately before writing, applies the declared replacements to
*that* fetch, and refuses unless every changed line is one the caller declared.

Usage
-----
    python3 -I -B issue_body_safe_write_v1.py PLAN.json            # dry run
    python3 -I -B issue_body_safe_write_v1.py PLAN.json --apply

PLAN.json is either a GMI_ISSUE_RECONCILIATION_V2 document or a list of them.
"""

import io
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import checklist_core_v1 as core

REPO = "SzeChunYiu/ORION-OCM"


class RefusedWrite(Exception):
    pass


def fetch_body(issue):
    out = subprocess.check_output(
        ["gh", "api", "repos/%s/issues/%d" % (REPO, issue), "--jq", ".body"])
    body = out.decode("utf-8")
    if body.endswith("\n"):
        body = body[:-1]
    return body


def load_plan(paths):
    reps = []
    for p in paths:
        with io.open(p, encoding="utf-8") as fh:
            doc = json.load(fh)
        docs = doc if isinstance(doc, list) else [doc]
        for d in docs:
            if d.get("schema") != "GMI_ISSUE_RECONCILIATION_V2":
                raise RefusedWrite("%s: unexpected schema %r" % (p, d.get("schema")))
            if d.get("issue") != 833:
                raise RefusedWrite("%s: issue is %r, expected 833" % (p, d.get("issue")))
            for r in d.get("replacements", []):
                r = dict(r)
                r["_source"] = p
                reps.append(r)
    if not reps:
        raise RefusedWrite("plan contains no replacements")
    return reps


def apply_replacements(body, reps):
    """Return (new_body, intended_changes). Refuses on any ambiguity."""
    lines = body.split(u"\n")
    # map each section header line index
    intended = []
    for rep in reps:
        anchor, old, new = rep["anchor"], rep["old"], rep["new"]
        try:
            a = lines.index(anchor)
        except ValueError:
            raise RefusedWrite("anchor not found: %r (from %s)" % (anchor, rep["_source"]))
        # section extent: up to the next top-level header
        end = len(lines)
        for j in range(a + 1, len(lines)):
            if lines[j].startswith(u"# "):
                end = j
                break
        hits = [j for j in range(a + 1, end) if lines[j] == old]
        if len(hits) == 0:
            raise RefusedWrite(
                "old line not found in section %r (from %s): %r"
                % (anchor, rep["_source"], old[:120]))
        if len(hits) > 1:
            raise RefusedWrite(
                "old line is ambiguous (%d matches) in section %r: %r"
                % (len(hits), anchor, old[:120]))
        j = hits[0]
        lines[j] = new
        intended.append((j, old, new))
    return u"\n".join(lines), intended


def verify(old_body, new_body, intended):
    """Every changed line must be a declared change; nothing else may move."""
    a, b = old_body.split(u"\n"), new_body.split(u"\n")
    if len(a) != len(b):
        raise RefusedWrite("line count changed: %d -> %d" % (len(a), len(b)))
    declared = dict((i, (o, n)) for i, o, n in intended)
    changed = [i for i in range(len(a)) if a[i] != b[i]]
    if sorted(changed) != sorted(declared.keys()):
        undeclared = [i for i in changed if i not in declared]
        missing = [i for i in declared if i not in changed]
        raise RefusedWrite(
            "changed lines do not match declaration; undeclared=%r missing=%r"
            % (undeclared[:5], missing[:5]))
    for i in changed:
        o, n = declared[i]
        if a[i] != o or b[i] != n:
            raise RefusedWrite("line %d content does not match declaration" % (i + 1))

    rows_a, _ = core.parse(old_body)
    rows_b, _ = core.parse(new_body)
    if len(rows_a) != len(rows_b):
        raise RefusedWrite("row count changed: %d -> %d" % (len(rows_a), len(rows_b)))
    for ra, rb in zip(rows_a, rows_b):
        if ra["text"] != rb["text"]:
            raise RefusedWrite("row text changed: %r -> %r" % (ra["text"][:80], rb["text"][:80]))
        if ra["checked"] and not rb["checked"]:
            raise RefusedWrite("row un-checked by this write: %r" % ra["text"][:80])
    if len(new_body) > core.BODY_LIMIT:
        raise RefusedWrite(
            "resulting body is %d characters, over the %d limit; compact first"
            % (len(new_body), core.BODY_LIMIT))
    return rows_a, rows_b


def main(argv):
    apply_it = "--apply" in argv
    paths = [a for a in argv if not a.startswith("--")]
    if not paths:
        print(__doc__)
        return 2
    reps = load_plan(paths)
    live = fetch_body(833)
    new, intended = apply_replacements(live, reps)
    rows_a, rows_b = verify(live, new, intended)

    ca = sum(1 for r in rows_a if r["checked"])
    cb = sum(1 for r in rows_b if r["checked"])
    print("live body      : %d chars, sha %s" % (len(live), core.body_sha256(live)[:16]))
    print("intended body  : %d chars, sha %s" % (len(new), core.body_sha256(new)[:16]))
    print("checked rows   : %d -> %d" % (ca, cb))
    print("headroom left  : %d chars" % (core.BODY_LIMIT - len(new)))
    for i, o, n in intended:
        print("  line %-4d  %s" % (i + 1, n[:110]))
    if not apply_it:
        print("DRY RUN - pass --apply to write")
        return 0

    fd, tmp = tempfile.mkstemp(suffix=".md")
    os.close(fd)
    core.write_text(tmp, new)
    subprocess.check_call(["gh", "issue", "edit", "833", "--repo", REPO, "--body-file", tmp])
    os.unlink(tmp)

    back = fetch_body(833)
    if back != new:
        raise RefusedWrite(
            "POST-WRITE MISMATCH: read back %d chars (sha %s), intended %d (sha %s)"
            % (len(back), core.body_sha256(back)[:16], len(new), core.body_sha256(new)[:16]))
    print("WRITE VERIFIED: %d chars, sha %s" % (len(back), core.body_sha256(back)[:16]))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except RefusedWrite as exc:
        sys.stderr.write("REFUSED: %s\n" % exc)
        sys.exit(1)

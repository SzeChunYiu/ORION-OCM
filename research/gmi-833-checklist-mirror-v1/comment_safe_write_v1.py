"""Safe-write path for the #833 checklists that live in issue COMMENTS.

Sections A-M are in the issue body; sections Z and AA-AJ are spread across ten
issue comments holding 707 further rows. Comments are a second write surface
with the same hazard as the body: an edit replaces the previous text, and the
lane that wrote it last wins.

Same contract as issue_body_safe_write_v1.py: re-fetch the live comment
immediately before writing, apply the declared replacements to THAT fetch, and
refuse unless every changed line is one the caller declared.

    python3 -I -B comment_safe_write_v1.py PLAN.json            # dry run
    python3 -I -B comment_safe_write_v1.py PLAN.json --apply
"""

import io
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import checklist_core_v1 as core
from issue_body_safe_write_v1 import RefusedWrite, REPO

COMMENT_LIMIT = 65536


def fetch_comment(cid):
    out = subprocess.check_output(
        ["gh", "api", "repos/%s/issues/comments/%d" % (REPO, cid), "--jq", ".body"])
    body = out.decode("utf-8")
    return body[:-1] if body.endswith("\n") else body


def load_plan(paths):
    by_comment = {}
    for p in paths:
        with io.open(p, encoding="utf-8") as fh:
            doc = json.load(fh)
        for d in (doc if isinstance(doc, list) else [doc]):
            if d.get("schema") != "GMI_ISSUE_COMMENT_RECONCILIATION_V1":
                raise RefusedWrite("%s: unexpected schema %r" % (p, d.get("schema")))
            if d.get("issue") != 833:
                raise RefusedWrite("%s: issue is %r, expected 833" % (p, d.get("issue")))
            for r in d.get("replacements", []):
                cid = r.get("comment_id")
                if not isinstance(cid, int):
                    raise RefusedWrite("%s: replacement without integer comment_id" % p)
                r = dict(r)
                r["_source"] = p
                by_comment.setdefault(cid, []).append(r)
    if not by_comment:
        raise RefusedWrite("plan contains no replacements")
    return by_comment


def apply_to_comment(body, reps):
    """Anchored, unambiguous replacement inside one comment."""
    lines = body.split(u"\n")
    intended = []
    for rep in reps:
        anchor, old, new = rep.get("anchor"), rep["old"], rep["new"]
        lo, hi = 0, len(lines)
        if anchor:
            hits = [i for i, l in enumerate(lines) if l.strip() == anchor.strip()]
            if len(hits) != 1:
                raise RefusedWrite(
                    "anchor %r matches %d lines in comment (from %s)"
                    % (anchor[:70], len(hits), rep["_source"]))
            lo = hits[0] + 1
            for j in range(lo, len(lines)):
                if lines[j].startswith(u"#"):
                    hi = j
                    break
        cand = [j for j in range(lo, hi) if lines[j] == old]
        if len(cand) != 1:
            raise RefusedWrite(
                "old line matches %d times under anchor %r (from %s): %r"
                % (len(cand), (anchor or "<none>")[:50], rep["_source"], old[:110]))
        lines[cand[0]] = new
        intended.append((cand[0], old, new))
    return u"\n".join(lines), intended


def verify(old_body, new_body, intended):
    a, b = old_body.split(u"\n"), new_body.split(u"\n")
    if len(a) != len(b):
        raise RefusedWrite("line count changed: %d -> %d" % (len(a), len(b)))
    declared = dict((i, (o, n)) for i, o, n in intended)
    changed = [i for i in range(len(a)) if a[i] != b[i]]
    if sorted(changed) != sorted(declared.keys()):
        undeclared = [i for i in changed if i not in declared]
        raise RefusedWrite("undeclared line changes at %r" % (undeclared[:5],))
    for i in changed:
        o, n = declared[i]
        if a[i] != o or b[i] != n:
            raise RefusedWrite("line %d does not match declaration" % (i + 1))
    # a checked row must never become unchecked
    for i in changed:
        if a[i].lstrip().startswith(u"- [x]") and b[i].lstrip().startswith(u"- [ ]"):
            raise RefusedWrite("row un-checked by this write: %r" % a[i][:80])
    if len(new_body) > COMMENT_LIMIT:
        raise RefusedWrite("resulting comment is %d chars, over the %d limit"
                           % (len(new_body), COMMENT_LIMIT))


def counts(text):
    done = sum(1 for l in text.split(u"\n") if l.lstrip().startswith(u"- [x]"))
    todo = sum(1 for l in text.split(u"\n") if l.lstrip().startswith(u"- [ ]"))
    return done, todo


def main(argv):
    apply_it = "--apply" in argv
    paths = [a for a in argv if not a.startswith("--")]
    if not paths:
        print(__doc__)
        return 2
    plan = load_plan(paths)
    total_marked = 0
    for cid, reps in sorted(plan.items()):
        live = fetch_comment(cid)
        new, intended = apply_to_comment(live, reps)
        verify(live, new, intended)
        d0, t0 = counts(live)
        d1, t1 = counts(new)
        print("comment %d: %d chars sha %s -> %d chars sha %s | done %d->%d open %d->%d"
              % (cid, len(live), core.body_sha256(live)[:12],
                 len(new), core.body_sha256(new)[:12], d0, d1, t0, t1))
        for _, _, n in intended:
            print("    %s" % n[:110])
        total_marked += len(intended)
        if not apply_it:
            continue
        fd, tmp = tempfile.mkstemp(suffix=".md")
        os.close(fd)
        core.write_text(tmp, new)
        subprocess.check_call(
            ["gh", "api", "-X", "PATCH",
             "repos/%s/issues/comments/%d" % (REPO, cid),
             "-F", "body=@%s" % tmp])
        os.unlink(tmp)
        back = fetch_comment(cid)
        if back != new:
            raise RefusedWrite(
                "POST-WRITE MISMATCH on comment %d: read back %d chars sha %s, intended %d sha %s"
                % (cid, len(back), core.body_sha256(back)[:12],
                   len(new), core.body_sha256(new)[:12]))
        print("    WRITE VERIFIED")
    print("\n%d row(s) across %d comment(s)%s"
          % (total_marked, len(plan), "" if apply_it else "  [DRY RUN - pass --apply]"))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except RefusedWrite as exc:
        sys.stderr.write("REFUSED: %s\n" % exc)
        sys.exit(1)

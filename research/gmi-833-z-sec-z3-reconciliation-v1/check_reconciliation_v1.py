"""Offline checker for this lane's issue-comment reconciliation.

Verifies, against the byte-exact snapshot committed beside it:
  * the snapshot's sha256 matches the one recorded in the reconciliation;
  * every `old` string occurs EXACTLY ONCE in the whole body and EXACTLY ONCE
    under its own `###` anchor;
  * every `old` is an unchecked row and every `new` is its checked form with an
    appended evidence clause;
  * replacements + not_closed + already-checked rows account for all 131 rows,
    with no row appearing twice;
  * every replacement and every not_closed entry carries `comment_id`.

Run:  python3 -I -B check_reconciliation_v1.py
"""
import collections
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REC = os.path.join(HERE, "ISSUE_833_COMMENT_RECONCILIATION_V1.json")
SNAP = os.path.join(HERE, "COMMENT_5684819296_SNAPSHOT_V1.md")


def main():
    with open(REC) as fh:
        d = json.load(fh)
    body = open(SNAP, "rb").read().decode("utf-8")
    problems = []

    sha = hashlib.sha256(body.encode("utf-8")).hexdigest()
    if sha != d["comment_sha256"]:
        problems.append("snapshot sha256 %s != recorded %s"
                        % (sha, d["comment_sha256"]))
    if len(body.encode("utf-8")) != d["comment_bytes"]:
        problems.append("snapshot byte length mismatch")

    lines = body.split("\n")
    cur = None
    sec = collections.OrderedDict()
    for l in lines:
        if l.startswith("### "):
            cur = l
            sec[cur] = []
        elif l.startswith(("- [ ] ", "- [x] ")) and cur:
            sec[cur].append(l)
    all_rows = [r for v in sec.values() for r in v]
    if len(all_rows) != d["rows_total"]:
        problems.append("row census %d != %d" % (len(all_rows), d["rows_total"]))

    seen = collections.Counter()
    for kind in ("replacements", "not_closed"):
        for e in d[kind]:
            if e.get("comment_id") != d["comment_id"]:
                problems.append("%s entry missing comment_id" % kind)
            a = e["anchor"]
            if a not in sec:
                problems.append("anchor not in body: %r" % a)
                continue
            old = e["old"]
            if body.count(old) != 1:
                problems.append("`old` occurs %d times in the body: %r"
                                % (body.count(old), old[:60]))
            if sec[a].count(old) != 1:
                problems.append("`old` occurs %d times under its anchor: %r"
                                % (sec[a].count(old), old[:60]))
            if not old.startswith("- [ ] "):
                problems.append("`old` is not an unchecked row: %r" % old[:60])
            seen[old] += 1
            if kind == "replacements":
                new = e["new"]
                if not new.startswith("- [x] " + old[6:]):
                    problems.append("`new` is not `old` checked: %r" % new[:80])
                if u"— ✅ " not in new:
                    problems.append("`new` carries no evidence clause: %r"
                                    % new[:80])
                if not new.rstrip().endswith("."):
                    problems.append("`new` does not end in a period")

    dupes = [k for k, v in seen.items() if v > 1]
    if dupes:
        problems.append("%d rows appear in more than one entry" % len(dupes))

    checked = [r for r in all_rows if r.startswith("- [x] ")]
    if len(checked) != d["rows_already_checked_in_live_body"]:
        problems.append("already-checked count %d != %d"
                        % (len(checked), d["rows_already_checked_in_live_body"]))
    tot = (len(d["replacements"]) + len(d["not_closed"]) + len(checked))
    if tot != d["rows_total"]:
        problems.append("accounting does not close: %d != %d"
                        % (tot, d["rows_total"]))
    if len(d["replacements"]) != d["rows_closed_by_this_lane"]:
        problems.append("rows_closed_by_this_lane mismatch")
    if len(d["not_closed"]) != d["rows_not_closed"]:
        problems.append("rows_not_closed mismatch")

    if problems:
        for p in problems:
            sys.stderr.write("FAIL: %s\n" % p)
        return 1
    print("reconciliation OK: %d closed, %d not closed, %d already checked, "
          "%d total; every `old` unique in body and under its anchor"
          % (len(d["replacements"]), len(d["not_closed"]), len(checked),
             d["rows_total"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

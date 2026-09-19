"""Validate the Section Z row census against the committed comment snapshot.

Stdlib only; runnable as `python3 -I -B check_z_map_v1.py` and under -O.
Assertions are never used for the checks, so -O cannot make this vacuously green.
"""
import collections
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SNAP = os.path.join(HERE, "COMMENT_5684819296_SNAPSHOT_V1.md")
CENSUS = os.path.join(HERE, "Z_ROWS_V1.json")
BUCKETS = ("HARNESS", "EXACT-FORMAL", "NEW-SCIENCE", "EXTERNAL-GATE")


def parse(body):
    cur = None
    secs = collections.OrderedDict()
    for line in body.split("\n"):
        if line.startswith("### Z"):
            cur = line
            secs[cur] = []
        elif line.startswith("- [ ] ") and cur is not None:
            secs[cur].append(line)
    return secs


def failures():
    bad = []
    raw = open(SNAP, "rb").read()
    census = json.load(open(CENSUS))
    if hashlib.sha256(raw).hexdigest() != census["snapshot_sha256"]:
        bad.append("snapshot sha256 drift")
    if len(raw) != census["snapshot_bytes"]:
        bad.append("snapshot byte-length drift")
    body = raw.decode("utf-8")
    secs = parse(body)
    if len(secs) != 18:
        bad.append("expected 18 Z subsections, found %d" % len(secs))
    total = sum(len(v) for v in secs.values())
    if total != 131:
        bad.append("expected 131 open rows, found %d" % total)
    if census["total_rows"] != total:
        bad.append("census total_rows %d != parsed %d" % (census["total_rows"], total))
    checked = sum(1 for l in body.split("\n") if l.startswith("- [x] "))
    if checked != census["checked_rows"]:
        bad.append("checked-row drift")
    all_rows = [r for v in secs.values() for r in v]
    counts = collections.Counter(all_rows)
    dups = [r for r, n in counts.items() if n > 1]
    if dups:
        bad.append("%d duplicate row strings" % len(dups))
    subs = [(a, b) for a in all_rows for b in all_rows if a != b and a in b]
    if subs:
        bad.append("%d proper-substring row pairs" % len(subs))
    by_id = dict((s["id"], s) for s in census["subsections"])
    for head, rows in secs.items():
        sid = head.split("—")[0].replace("###", "").strip()
        if sid not in by_id:
            bad.append("census missing subsection %s" % sid)
            continue
        rec = by_id[sid]
        if rec["row_count"] != len(rows) or rec["rows"] != rows:
            bad.append("census rows differ for %s" % sid)
        if rec["bucket"] not in BUCKETS:
            bad.append("bad bucket for %s" % sid)
    # the trailing prose block must carry no rows
    tail = body.split("## Groundbreaking flagship closure rule")[-1]
    if "- [ ]" in tail or "- [x]" in tail:
        bad.append("closure-rule block unexpectedly contains checkbox rows")
    return bad


def self_test():
    """The checker must fire on planted corruption, and stay silent on the real file."""
    bad = failures()
    if bad:
        return ["no-alarm case failed on real data: %s" % bad]
    # planted positive 1: drop a row
    raw = open(SNAP, "rb").read().decode("utf-8")
    planted = raw.replace("- [ ] Score calibration.\n", "", 1)
    if len(parse(planted).get("### Z12 — Prediction sharpness, uncertainty and scientific risk", [])) != 8:
        return ["planted row-drop did not change the parse"]
    # planted positive 2: duplicate a row -> duplicate detector must see it
    dup_rows = ["- [ ] Score coverage.", "- [ ] Score coverage."]
    if len([r for r, n in collections.Counter(dup_rows).items() if n > 1]) != 1:
        return ["duplicate detector cannot fire"]
    return []


def main():
    st = self_test()
    if st:
        sys.stdout.write("SELF_TEST_FAIL\n" + "\n".join(st) + "\n")
        return 2
    bad = failures()
    if bad:
        sys.stdout.write("Z_MAP_FAIL\n" + "\n".join(bad) + "\n")
        return 1
    census = json.load(open(CENSUS))
    sys.stdout.write(
        "Z_MAP_OK subsections=18 rows=131 checked=%d snapshot_sha256=%s\n"
        % (census["checked_rows"], census["snapshot_sha256"])
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

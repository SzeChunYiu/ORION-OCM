"""Validate-the-checker gate: does my invocation of m2p2_gsurf.py reproduce the
verdicts already recorded in the repo for the band-2-3 control worlds?

Nothing measured on band 3-4 may be believed unless this passes. Compares every
decision-bearing field, not just the verdict string. Worlds with no recorded
G-SURF file (hc04, hc07) are reported as NOT-COMPARABLE, never as passes."""
import glob, json, os, sys

REPRO = os.path.expanduser("~/m2band/gsurf_repro")
REC = "research/m2-traversal-capital-v1/m2p2/stage2"
FIELDS = ("verdict", "free_capture_fraction", "chance_ladder",
          "free_best_ladder", "oracle_ladder", "free_best_name")

recorded = {}
for f in sorted(glob.glob(os.path.join(REC, "M2P2_GSURF_*.json"))):
    d = json.load(open(f))
    recorded[d["world_id"]] = d

mine = {}
for f in sorted(glob.glob(os.path.join(REPRO, "G_*.json"))):
    d = json.load(open(f))
    mine[d["world_id"]] = d

print("recorded: %d worlds   reproduced: %d worlds\n" % (len(recorded), len(mine)))

ok = bad = missing = notcomp = 0
for wid in sorted(set(recorded) | set(mine)):
    if wid not in recorded:
        print("  %-22s NOT-COMPARABLE (no recorded G-SURF for this world)" % wid); notcomp += 1; continue
    if wid not in mine:
        print("  %-22s MISSING (recorded, but my re-run produced nothing)" % wid); missing += 1; continue
    r, m = recorded[wid]["gsurf"], mine[wid]["gsurf"]
    diffs = [(k, r.get(k), m.get(k)) for k in FIELDS if r.get(k) != m.get(k)]
    rb, mb = recorded[wid].get("blocking"), mine[wid].get("blocking")
    if rb != mb:
        diffs.append(("blocking", rb, mb))
    if diffs:
        bad += 1
        print("  %-22s MISMATCH" % wid)
        for k, a, b in diffs:
            print("      %-22s recorded=%-14s mine=%s" % (k, a, b))
    else:
        ok += 1
        print("  %-22s MATCH   verdict=%-6s capture=%s" % (wid, m.get("verdict"), m.get("free_capture_fraction")))

print("\nmatch %d   mismatch %d   missing %d   not-comparable %d" % (ok, bad, missing, notcomp))
verdict = "HARNESS VALIDATED" if (bad == 0 and missing == 0 and ok >= 8) else "HARNESS NOT VALIDATED"
print("\n%s" % verdict)
sys.exit(0 if verdict == "HARNESS VALIDATED" else 1)

#!/usr/bin/env python3
"""Repo-wide RATCHETING terminology gate (issue #833, row AB37).

The parent workflow runs the terminology gate over one package directory and
swallows its exit code, so a new package can land with any banned term. This
gate is repo-wide and blocking:

  * scope  = every markdown file under research/ plus repo-root markdown
             (the flagship document set), minus the declared authority docs;
  * signal = per (file, term) hit COUNT from the frozen parent gate
             research/gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CI_GATE_V1.py;
  * rule   = FAIL if any (file, term) count rises above the frozen baseline or
             a new (file, term) pair appears; PASS otherwise. Counts that fall
             are reported as ratchet progress and never fail the build.

Usage:
  python3 -I -B terminology_ratchet_v1.py                       # repo-wide check
  python3 -I -B terminology_ratchet_v1.py --owned-files LIST    # PR-scoped check
  python3 -I -B terminology_ratchet_v1.py --write               # rewrite baseline

On a pull request the gate is run with --owned-files, so a lane is failed only
for banned terms in files it added or grew. That is what keeps the gate from
crying wolf on another lane's PR - a gate that fires on work you did not do is
a gate that gets switched off.
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))
GATE = os.path.join(REPO, "research", "gmi-833-tranche-ab-ac-lit",
                    "GMI_TERMINOLOGY_CI_GATE_V1.py")
BASELINE = os.path.join(HERE, "TERMINOLOGY_BASELINE_V1.json")

# Packages whose SUBJECT is the #833 terminology audit itself. They must quote
# the legacy terms verbatim - a crosswalk row named `machine species`, an AB row
# whose own governing phrase is `parent subtraction`, a freeze that quotes the
# issue row it may not reconcile - so scanning them measures the audit's own
# vocabulary rather than any paper-facing debt. The last three were added by
# gmi-833-ac-lanes-harness-v1 / gmi-833-ab-residual-definitions-v1 /
# gmi-833-aa-finite-universal-harness-v1 on the same criterion; their remaining
# 22 hits are quotations of row-named legacy terms (15) and text inside
# committed pre-implementation freezes that may not be edited after the fact (7).
# gmi-833-aa-ledger-gate-v1 is deliberately NOT excluded: it has zero hits.
EXCLUDED_PACKAGES = ("gmi-833-tranche-ab-ac-lit", "gmi-833-ab-terminology-harness-v1",
                     "gmi-833-terminology-migration-v1", "gmi-833-checklist-mirror-v1",
                     "gmi-833-ac-lanes-harness-v1", "gmi-833-ab-residual-definitions-v1",
                     "gmi-833-aa-finite-universal-harness-v1")


def load_gate():
    spec = importlib.util.spec_from_file_location("gmi_term_gate_v1", GATE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def flagship_files():
    out = []
    root = os.path.join(REPO, "research")
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        rel = os.path.relpath(dirpath, root)
        top = rel.split(os.sep)[0]
        if top in EXCLUDED_PACKAGES:
            continue
        for fn in sorted(filenames):
            if fn.endswith(".md"):
                out.append(os.path.join(dirpath, fn))
    for fn in sorted(os.listdir(REPO)):
        if fn.endswith(".md"):
            out.append(os.path.join(REPO, fn))
    return sorted(out)


def measure(files=None, root=None):
    gate = load_gate()
    root = root or REPO
    files = files if files is not None else flagship_files()
    hits = gate.scan_paths(files, context="paper-facing")
    counts = {}
    for h in hits:
        rel = os.path.relpath(h["file"], root)
        counts.setdefault(rel, {})
        counts[rel][h["term"]] = counts[rel].get(h["term"], 0) + 1
    total = sum(sum(v.values()) for v in counts.values())
    return {"files_scanned": len(files), "files_with_hits": len(counts),
            "total_hits": total, "counts": counts}


def check(baseline, live, owned_new_files=None):
    """`owned_new_files` scopes the new-file rule. On a pull request it is the
    set of markdown paths in the PR's own diff: a lane is failed for banned
    terms in files IT added, never for files another lane added. A new file
    with hits outside that set is reported informationally
    (`unowned_new_files_with_hits`) and does not fail the build. Passing None
    keeps the strict repo-wide rule (used on push to main)."""
    return _check(baseline, live, owned_new_files)


def _check(baseline, live, owned_new_files=None):
    regressions = []
    new_files = []
    improved = 0
    removed = 0
    b = baseline["counts"]
    l = live["counts"]
    for path, terms in sorted(l.items()):
        if path not in b:
            new_files.append(path)
            continue
        for term, n in sorted(terms.items()):
            prev = b[path].get(term, 0)
            if n > prev:
                regressions.append("%s [%s] %d -> %d" % (path, term, prev, n))
            elif n < prev:
                improved += 1
                removed += prev - n
    for path, terms in sorted(b.items()):
        if path not in l:
            improved += 1
            removed += sum(terms.values())
    unowned = []
    if owned_new_files is not None:
        owned = set(owned_new_files)
        unowned = [p for p in new_files if p not in owned]
        new_files = [p for p in new_files if p in owned]
    return {"regressions": regressions, "new_files_with_hits": new_files,
            "unowned_new_files_with_hits": unowned,
            "improved_entries": improved, "sites_removed_vs_baseline": removed}


def main(argv):
    live = measure()
    if "--write" in argv:
        doc = {"schema": "GMI_TERMINOLOGY_RATCHET_BASELINE_V1",
               "issue": 833, "row": "AB37",
               "source_main": "91c6d2876ba80c517a186e28fce3bdbe4e3fc218",
               "gate": "research/gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CI_GATE_V1.py",
               "excluded_packages": list(EXCLUDED_PACKAGES),
               "excluded_reason": "terminology-authority and migration-log packages quote the "
                                  "banned terms definitionally; the parent gate self-skips its "
                                  "own authority docs for the same reason",
               "files_scanned": live["files_scanned"],
               "files_with_hits": live["files_with_hits"],
               "total_hits": live["total_hits"],
               "counts": live["counts"]}
        json.dump(doc, open(BASELINE, "w"), indent=1, sort_keys=True)
        print("baseline written: %d hits in %d of %d files"
              % (live["total_hits"], live["files_with_hits"], live["files_scanned"]))
        return 0
    baseline = json.load(open(BASELINE))
    owned = None
    if "--owned-files" in argv:
        listing = argv[argv.index("--owned-files") + 1]
        owned = [ln.strip() for ln in open(listing) if ln.strip()]
    rep = check(baseline, live, owned)
    print(json.dumps({"files_scanned": live["files_scanned"],
                      "total_hits_live": live["total_hits"],
                      "total_hits_baseline": baseline["total_hits"],
                      "regressions": len(rep["regressions"]),
                      "new_files_with_hits": len(rep["new_files_with_hits"]),
                      "sites_removed_vs_baseline": rep["sites_removed_vs_baseline"],
                      "unowned_new_files_with_hits": len(rep["unowned_new_files_with_hits"]),
                      "new_file_scope": ("PR diff" if owned is not None else "repo-wide")},
                     indent=2, sort_keys=True))
    for r in rep["regressions"][:50]:
        print("  REGRESSION " + r)
    for f in rep["new_files_with_hits"][:50]:
        print("  NEW FILE WITH BANNED TERMS " + f)
    for f in rep["unowned_new_files_with_hits"][:50]:
        print("  (informational, not this PR's file) " + f)
    if rep["regressions"] or rep["new_files_with_hits"]:
        print("[ratchet] FAIL - terminology debt increased")
        return 1
    print("[ratchet] PASS - no new banned-term site")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""REV-L47-CUSTODY-GAPS triage collector.

For each of the 18 TIGHT_GAP_EXECUTOR packages, reconstruct the surviving
first-add timeline on main for: FREEZE* authority files, outcome-bearing
artifacts (RESULT*/RECEIPT*/BLIND_*OUTCOME*), executor/checker .py files, and
config files. Also records later modifications (M) of the freeze path, and
whether the package landed as one squash commit or granular commits.

Output: triage_timeline_v1.json (evidence base; triage decisions cite it).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

PACKAGES = [
    "gmi-833-aj9a-known-family-benchmark-v1",
    "gmi-833-aj9b-k01-blind-recovery-v1",
    "gmi-833-aj9c-k02-blind-recovery-v1",
    "gmi-833-aj9d-k03-blind-recovery-v1",
    "gmi-833-aj9e-k04-blind-recovery-v1",
    "gmi-833-aj9f-k05-blind-recovery-v1",
    "gmi-833-aj9h-k07-k11-blind-recovery-v1",
    "gmi-833-developmental-naturality-v1",
    "gmi-833-heldout-20-transitions-v1",
    "gmi-833-pareto-topology-v1",
    "gmi-833-real-transition-protocol-v1",
    "gmi-833-remint-equivariance-v1",
    "gmi-833-transform-geometry-v1",
    "gmi-capability-held-freeze-v1",
    "gmi-capability-transfer-freeze-v1",
    "gmi-heldout-long-sequence-v1",
    "gmi-history-morphology-discovery-v1",
    "gmi-section-d-uncertainty-extrapolation-v5",
]

FREEZE_RE = re.compile(r"^FREEZE", re.I)
OUTCOME_RE = re.compile(r"(RESULT|RECEIPT|OUTCOME)", re.I)
CONFIG_RE = re.compile(r"CONFIG", re.I)


def classify(name: str) -> str:
    if FREEZE_RE.match(name):
        return "freeze"
    if name.endswith(".py"):
        return "py"
    if OUTCOME_RE.search(name):
        return "outcome"
    if CONFIG_RE.search(name):
        return "config"
    return "other"


def git(*args: str) -> str:
    proc = subprocess.run(["/usr/bin/git", "-C", str(REPO), *args],
                          capture_output=True, text=True, check=True)
    return proc.stdout


def timeline(pkg: str) -> dict:
    base = f"research/{pkg}"
    files = sorted(p.name for p in (REPO / base).iterdir() if p.is_file()) \
        if (REPO / base).is_dir() else []
    # first adds (A) over the package path; also collect M events for freeze files
    adds: dict[str, dict] = {}
    mods: dict[str, list] = {}
    out = git("log", "--diff-filter=A", "--format=__CT__%ct %H %s", "--name-only", "--", base)
    cur = None
    for line in out.splitlines():
        if line.startswith("__CT__"):
            _, rest = line.split("__CT__", 1)
            ct_s, sha, subject = rest.split(" ", 2)
            cur = {"ct": int(ct_s), "sha": sha, "subject": subject}
        elif line.strip() and cur is not None:
            f = line.strip()
            if f.startswith(base + "/"):
                adds.setdefault(f, cur)  # newest-first: first seen = oldest add
    out = git("log", "--diff-filter=M", "--format=__CT__%ct %H %s", "--name-only", "--", base)
    cur = None
    for line in out.splitlines():
        if line.startswith("__CT__"):
            _, rest = line.split("__CT__", 1)
            ct_s, sha, subject = rest.split(" ", 2)
            cur = {"ct": int(ct_s), "sha": sha, "subject": subject}
        elif line.strip() and cur is not None:
            f = line.strip()
            if f.startswith(base + "/") and FREEZE_RE.match(Path(f).name):
                mods.setdefault(f, []).append(cur)
    events = []
    for f, meta in adds.items():
        events.append({
            "file": Path(f).name, "kind": classify(Path(f).name),
            "ct": meta["ct"], "sha": meta["sha"], "subject": meta["subject"][:90],
        })
    events.sort(key=lambda e: e["ct"])
    frz = [e for e in events if e["kind"] == "freeze"]
    fz_t = min((e["ct"] for e in frz), default=None)
    if fz_t is not None:
        for e in events:
            e["dt_from_freeze_s"] = e["ct"] - fz_t
    n_commits = len({e["sha"] for e in events})
    return {
        "package": pkg,
        "n_files_now": len(files),
        "n_add_commits": n_commits,
        "landing": "single_commit" if n_commits == 1 else "granular",
        "events": events,
        "freeze_modifications_after_add": {
            Path(k).name: v for k, v in mods.items()},
        "span_s": (events[-1]["ct"] - events[0]["ct"]) if events else None,
    }


def main() -> None:
    result = {"schema": "REV_L47_CUSTODY_TRIAGE_TIMELINE_V1", "packages": {}}
    for pkg in PACKAGES:
        result["packages"][pkg] = timeline(pkg)
        t = result["packages"][pkg]
        fz = [e for e in t["events"] if e["kind"] == "freeze"]
        oc = [e for e in t["events"] if e["kind"] == "outcome"]
        pys_in_window = [e for e in t["events"]
                         if e["kind"] == "py" and 0 < e.get("dt_from_freeze_s", 1 << 30) <= 120]
        print(f"{pkg}: landing={t['landing']} span={t['span_s']}s "
              f"freeze@{fz[0]['ct'] if fz else '-'} "
              f"outcome_dt={[e['dt_from_freeze_s'] for e in oc]} "
              f"py_in_window={[e['dt_from_freeze_s'] for e in pys_in_window]}")
    out = Path(__file__).parent / "triage_timeline_v1.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    sys.exit(main())

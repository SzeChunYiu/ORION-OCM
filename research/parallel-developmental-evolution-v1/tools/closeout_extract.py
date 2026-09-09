"""Close-out extraction: one compact JSON bundle from the frozen run root.
Runs on LUNARC; the Mac turns it into the section-20 capsule artifacts.
Usage: closeout_extract.py RUN_ROOT > bundle.json
"""
import json
import subprocess
import sys
import time
from pathlib import Path

run = Path(sys.argv[1])
out = {"schema": "pdev217.closeout_bundle.v1", "written_unix": time.time()}


def j(path):
    return json.loads(Path(path).read_text())


# state + manifests ------------------------------------------------------
out["state"] = j(run / "generations" / "state.json")
out["batch_manifest"] = j(run / "manifests" / "BATCH.json")
sub = [json.loads(l) for l in (run / "manifests" / "submissions.jsonl")
       .read_text().splitlines() if l.strip()]
out["submissions"] = sub
amd = run / "manifests" / "AMENDMENTS.json"
if amd.exists():
    out["amendments"] = j(amd)

# ledgers (counts + full generation ledger; candidate ledger summarized) --
out["generation_ledger"] = [json.loads(l) for l in
                            (run / "GENERATION_LEDGER.jsonl").read_text()
                            .splitlines() if l.strip()]
cl = run / "CANDIDATE_LEDGER.jsonl"
ledger_lines = [l for l in cl.read_text().splitlines() if l.strip()]
parseable = corrupt = 0
for l in ledger_lines:
    try:
        json.loads(l)
        parseable += 1
    except Exception:
        corrupt += 1
# Authoritative rebuild: per-candidate eval files (one writer per file, no
# contention).  The append-only ledger suffered concurrent-append
# interleaving (156-wide arrays); it stays on disk untouched as evidence.
rebuilt = []
for gdir in sorted((run / "generations").glob("g[0-9]*")):
    for wdir in sorted(gdir.glob("waves/w[0-9]*")):
        for p in sorted(wdir.joinpath("eval").glob("*.json")):
            if p.name.endswith(".full.json"):
                continue
            rebuilt.append((gdir.name, wdir.name, json.loads(p.read_text())))
with open(run / "CANDIDATE_LEDGER_REBUILT.jsonl", "w") as h:
    for g, w, r in rebuilt:
        h.write(json.dumps(r, sort_keys=True) + "\n")
_by = {}
for g, w, r in rebuilt:
    k = (g, w, r["arm"])
    _by[k] = _by.get(k, 0) + 1
out["candidate_ledger_summary"] = {
    "ledger_lines": len(ledger_lines),
    "ledger_parseable": parseable,
    "ledger_corrupt_interleaved": corrupt,
    "rebuilt_from_authoritative_eval_files": len(rebuilt),
    "measured": sum(1 for _, _, r in rebuilt
                    if r.get("status") == "MEASURED"),
    "crashed": sum(1 for _, _, r in rebuilt
                   if r.get("status") != "MEASURED"),
    "by_generation_wave_arm": {"%s %s %s" % k: v for k, v in _by.items()},
    "incident": "CANDIDATE_LEDGER.jsonl append-only log had interleaved "
                "corrupt lines from concurrent 156-wide array appends; "
                "rebuilt canonically from eval/*.json (single-writer "
                "files); original kept untouched"}
hist = run / "search_history.jsonl"
if hist.exists():
    out["shared_history_rows"] = sum(1 for _ in hist.open())

# per generation ---------------------------------------------------------
gens = {}
for gdir in sorted((run / "generations").glob("g[0-9]*")):
    g = int(gdir.name[1:])
    if g == 0 or gdir.name == "state.json":
        continue
    info = {"waves": {}}
    inc = gdir / "incumbent.json"
    if inc.exists():
        d = j(inc)
        info["incumbent"] = {"digest": d.get("digest"),
                             "suites_dev": d["suites"]["dev"]}
    for extra in ("ADOPTION_PACKET.json", "decision.json",
                  "cycle_receipt.json", "EXHAUSTION_TERMINAL.json"):
        p = gdir / extra
        if p.exists():
            info[extra.replace(".json", "")] = j(p)
    for wdir in sorted(gdir.joinpath("waves").glob("w[0-9]*")):
        w = int(wdir.name[1:])
        win = {}
        for f in ("batch.json", "aggregate.json", "verify_batch.json"):
            p = wdir / f
            if p.exists():
                d = j(p)
                if f == "batch.json":
                    win["denominator"] = d["denominator"]
                    win["quota"] = d.get("quota")
                elif f == "verify_batch.json":
                    win["verify_denominator"] = d["denominator"]
                else:
                    win["aggregate"] = d
        ev = wdir / "eval"
        if ev.exists():
            win["eval_rows"] = sum(1 for p in ev.glob("*.json")
                                   if not p.name.endswith(".full.json"))
        info["waves"][w] = win
    gens[g] = info
out["generations"] = gens

# parents (PDEV-3/11) ----------------------------------------------------
out["parents"] = {}
for arm in ("CONTINUED", "RESET"):
    pdir = run / "parents" / arm
    if pdir.exists():
        out["parents"][arm] = {
            "serial_state": j(pdir / "serial_state.json")}
for pb in sorted(run.glob("generations/g*/parent_batch_g*.json")):
    out["parents"].setdefault("batches", {})[pb.name] = j(pb)
# parent rows per generation (status counts + best MEASURED per arm)
rows_by = {}
for pr in sorted(run.glob("generations/g*/parents/*.json")):
    g = pr.parent.parent.name
    d = j(pr)
    arm = d.get("arm") or pr.name.split(".")[0]
    e = rows_by.setdefault(g, {}).setdefault(arm, {"rows": 0, "measured": 0})
    e["rows"] += 1
    e["measured"] += 1 if d.get("status") == "MEASURED" else 0
    v = d.get("vector") or {}
    if d.get("status") == "MEASURED":
        key = (v.get("failures", 0), v.get("work", 1 << 60))
        if "best" not in e or key < e["best"][0]:
            e["best"] = (key, {"entry_id": d.get("entry_id"),
                               "vector": v})
for g, arms in rows_by.items():
    for arm, e in arms.items():
        if "best" in e:
            e["best"] = e["best"][1]
out["parents"]["rows_by_generation"] = rows_by

# archive ----------------------------------------------------------------
arch = run / "DIVERSITY_ARCHIVE_V1.json"
if arch.exists():
    d = j(arch)
    out["diversity_archive"] = {
        "schema": d.get("schema"), "space_size": d.get("space_size"),
        "cells_occupied": len(d.get("cells", {})),
        "failed_niches": len(d.get("failed_niches", []) or [])}

# lineage freeze ---------------------------------------------------------
fz = run / "lineage" / "CONTINUED" / "freeze.json"
if fz.exists():
    out["freeze"] = j(fz)
snaps = sorted((run / "lineage" / "CONTINUED").glob("snapshot_*.json"))
if snaps:
    out["last_snapshot"] = j(snaps[-1])

# adverse / cannot-check -------------------------------------------------
adverse = []
for gdir in sorted((run / "generations").glob("g[0-9]*")):
    for vrow in sorted(gdir.glob("waves/w*/verify/*.json")):
        d = j(vrow)
        for h in d.get("hostiles", []):
            if h.get("status") in ("ADVERSE_RECORDED",):
                adverse.append({"kind": "ADVERSE_RECORDED",
                                "generation": d.get("generation"),
                                "wave": d.get("wave"),
                                "candidate_id": d.get("candidate_id"),
                                "hostile_id": h.get("hostile_id"),
                                "detail": h.get("detail")})
    for erow in sorted(gdir.glob("waves/w*/eval/*.json")):
        if erow.name.endswith(".full.json"):
            continue
        d = j(erow)
        if d.get("status") != "MEASURED":
            adverse.append({"kind": "CANNOT_CHECK",
                            "generation": d.get("generation"),
                            "wave": d.get("wave"),
                            "candidate_id": d.get("candidate_id"),
                            "detail": d.get("error")})
out["adverse_and_cannot_check"] = adverse

# replicates -------------------------------------------------------------
rep = run / "replicates"
if rep.exists():
    out["replicates"] = {h.name: sorted(p.name for p in h.glob("*.json"))
                         for h in sorted(rep.iterdir()) if h.is_dir()}
res = run / "results" / "CROSS_HOST_REPLICATES.json"
if res.exists():
    out["cross_host_replicates_summary"] = {
        k: j(res)[k] for k in ("verdict", "total_vector_exactly_reproduced",
                               "total_compared")}

# sacct ------------------------------------------------------------------
sacct = subprocess.run(
    ["sacct", "-S", "2026-09-09T12:00", "-X", "-n", "-P",
     "--format=JobID,JobName%20,State,Elapsed,AllocCPUS,TotalCPU,CPUTRaw"],
    capture_output=True, text=True).stdout
rows = [l.split("|") for l in sacct.splitlines() if "pdev" in l]
out["sacct"] = [dict(zip(("jobid", "name", "state", "elapsed", "cpus",
                          "totalcpu", "cputraw"), r)) for r in rows]
print(json.dumps(out, indent=1, sort_keys=True))

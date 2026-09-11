#!/usr/bin/env python3
"""Annotate packet cases with the inputs of two internally computable probes.
  depth_bound : 2 * sum_{i<=k} T^i  vs  b_min(min target length)   (library size, tilings, lengths)
  admitted    : the registered gate's own verdict (dev_state.admission)
Neither reads hidden motifs or protected outcomes."""
import argparse, json, sys
from pathlib import Path
ap = argparse.ArgumentParser(); ap.add_argument("--cases", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--runs", default=""); ap.add_argument("--spec", default="")
a = ap.parse_args()
cum = {}; s = 0
for L in range(9): s += 4 ** L; cum[L] = s
spec = {x["name"]: x for x in json.loads(Path(a.spec).read_text())} if a.spec else {}
pk = json.loads(Path(a.cases).read_text())
for c in pk["cases"]:
    eco = dev = None
    if c["name"] in spec:
        e, d = Path(spec[c["name"]]["ecology"]), Path(spec[c["name"]]["dev"])
        if e.exists() and d.exists(): eco, dev = json.loads(e.read_text()), json.loads(d.read_text())
    elif a.runs:
        e, d = Path(a.runs) / c["name"] / "ECOLOGY.json", Path(a.runs) / c["name"] / "dev_state.json"
        if e.exists() and d.exists(): eco, dev = json.loads(e.read_text()), json.loads(d.read_text())
    if eco is None:
        c["probe_pays_frac"] = None; c["admitted"] = None; continue
    T = len(dev["fragments"]) + 4
    lib = [tuple(f) for f in dev["fragments"]]
    val = eco["streams"]["validation"]
    def tile(prog):
        n = len(prog); best = [None] * (n + 1); best[0] = 0
        for i in range(n):
            if best[i] is None: continue
            for f in lib:
                j = i + len(f)
                if j <= n and tuple(prog[i:j]) == f and (best[j] is None or best[i] + 1 < best[j]): best[j] = best[i] + 1
        return best[n]
    # probe_pays_frac: for each SOLVED validation target, would a guided probe (at its
    # tiling depth) be expected to reach it before the baseline index it actually paid?
    # This is the cost rule's own inner estimate -- observable, and it separates "library
    # complete but too deep to pay" (C2) from "library incomplete" (C1) and "pays" (C0).
    pays = tot = 0
    for r in val:
        d = tile(tuple(r["canonical_program"])); b = int(r.get("baseline_first_index") or 0)
        if b <= 0: continue
        tot += 1
        if d is not None and d <= 4 and (sum(T ** j for j in range(1, d)) + T ** d / 2) < b: pays += 1
    c["T"] = T; c["probe_pays_frac"] = round(pays / tot, 3) if tot else None
    # lib_overlap: agreement between the frequency and MDL selections. Displacement (C1)
    # means compression picks DIFFERENT fragments; complete recovery means both find the
    # same structure. Both libraries are already computed in dev -- cost 0.
    fq = {tuple(f) for f in dev["fragments"]}
    if dev.get("mdl_fragments") is None:
        sys.path.insert(0, str(Path(__file__).parent))
        from m2_mdl_selection import mdl_select
        progs = [tuple(r["canonical_program"]) for r in eco["streams"]["train"]]
        md = {f for f in mdl_select(progs, cap=16) if 2 <= len(f) <= 8}
    else:
        md = {tuple(f) for f in dev["mdl_fragments"]}
    c["lib_overlap"] = round(len(fq & md) / len(fq | md), 3) if (fq | md) else None
    c["tileable_frac"] = round(sum(1 for r in val if tile(tuple(r["canonical_program"])) is not None) / len(val), 3) if val else None
    c["admitted"] = bool(dev.get("admission"))
    print("%-18s T=%-3d pays=%-6s tile=%-6s overlap=%-6s adm=%-5s [%s]" % (c["name"], T, c["probe_pays_frac"], c["tileable_frac"], c["lib_overlap"], c["admitted"], c["true_cause"].split("_")[0]))
Path(a.out).write_text(json.dumps(pk, indent=1))

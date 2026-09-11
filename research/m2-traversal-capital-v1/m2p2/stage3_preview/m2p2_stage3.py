#!/usr/bin/env python3
"""M2-P2 stage-3 aggregator: applies the FROZEN terminal precedence, the admission-law
check and the frozen statistics (paired shuffle-equal-n null per world, Holm across
worlds) to the scored records of the viable authored worlds. Never re-scores.

  usage: m2p2_stage3.py --runs <dir with m2p2_<WID>/ subdirs> --worlds <dir with M2P2_WORLD_*.json> --out STAGE3.json
"""
import argparse, json, random, statistics
from pathlib import Path

ARMS = ("RESET", "LIBRARY_ONLY", "CONTINUED", "SHUFFLED_HISTORY", "ORACLE_FAMILY", "ORDINARY_ADAPTIVE_PARENT")


def paired_shuffle_p(a, b, n_perm=20000, seed=0):
    """one-sided: is mean(b - a) > 0 (a cheaper) beyond label exchange within pairs?"""
    d = [y - x for x, y in zip(a, b)]
    obs = statistics.fmean(d)
    if obs <= 0:
        return 1.0
    rng = random.Random(seed); cnt = 0
    for _ in range(n_perm):
        s = sum(x if rng.random() < 0.5 else -x for x in d) / len(d)
        if s >= obs:
            cnt += 1
    return (cnt + 1) / (n_perm + 1)


def holm(pvals):
    idx = sorted(range(len(pvals)), key=lambda i: pvals[i]); m = len(pvals); adj = [0.0] * m; run = 0.0
    for r, i in enumerate(idx):
        run = max(run, (m - r) * pvals[i]); adj[i] = min(1.0, run)
    return adj


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--runs", required=True); ap.add_argument("--worlds", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(); runs, worlds = Path(a.runs), Path(a.worlds)
    per = []
    for wf in sorted(worlds.glob("M2P2_WORLD_*.json")):
        wid = wf.stem.replace("M2P2_WORLD_", ""); rd = runs / f"m2p2_{wf.stem}"
        if not (rd / "SUMMARY.json").exists():
            per.append({"world": wid, "status": "NOT_SCORED"}); continue
        eco = json.load(open(wf)); summ = json.load(open(rd / "SUMMARY.json")); dev = json.load(open(rd / "dev_state.json"))
        arms = {k: json.load(open(rd / f"arm_{k}.json")) for k in ARMS if (rd / f"arm_{k}.json").exists()}
        rows = {k: {r["target"]: r["B_slots"] for r in v["rows"] if r["verified"]} for k, v in arms.items()}
        common = set.intersection(*(set(v) for v in rows.values()))
        pair = lambda x, y: ([rows[x][t] for t in sorted(common)], [rows[y][t] for t in sorted(common)])
        true = {tuple(m) for m in eco["hidden_motifs"]}; lib = {tuple(f) for f in dev["fragments"]}
        rec = len(true & lib); admitted = bool(dev["admission"])
        law = "HOLDS" if ((rec == len(true)) == admitted) else "VIOLATED"
        means = {k: v.get("mean_B_slots") for k, v in arms.items()}
        p_cont = paired_shuffle_p(*pair("CONTINUED", "RESET")) if admitted else None
        p_parent = paired_shuffle_p(*pair("ORDINARY_ADAPTIVE_PARENT", "RESET"))
        per.append({"world": wid, "status": "SCORED", "terminal": summ.get("terminal"), "admitted": admitted,
                    "chunks_recovered": rec, "chunks": len(true), "admission_law": law,
                    "held_out_strictly_better": dev.get("held_out_strictly_better"), "validated_on": dev.get("validated_on"),
                    "held_out_mean_baseline": dev.get("held_out_mean_baseline"), "held_out_mean_candidate": dev.get("held_out_mean_candidate"),
                    "mean_B": means, "targets_common": len(common),
                    "library_only_equals_reset": means.get("LIBRARY_ONLY") == means.get("RESET"),
                    "shuffled_worse_than_reset": (means.get("SHUFFLED_HISTORY") or 0) > (means.get("RESET") or 0),
                    "p_continued_vs_reset": p_cont, "p_parent_vs_reset_DESCRIPTIVE": p_parent,
                    "parent_vs_reset": round(1 - means["ORDINARY_ADAPTIVE_PARENT"] / means["RESET"], 4) if means.get("ORDINARY_ADAPTIVE_PARENT") else None})
    scored = [p for p in per if p["status"] == "SCORED"]
    admitting = [p for p in scored if p["admitted"]]
    if admitting:
        adj = holm([p["p_continued_vs_reset"] for p in admitting])
        for p, q in zip(admitting, adj): p["holm_p_continued_vs_reset"] = q
    law_v = "VIOLATED" if any(p["admission_law"] == "VIOLATED" for p in scored) else "HOLDS"
    if not scored: terminal = "CANNOT_CHECK_NOTHING_SCORED"
    elif not admitting: terminal = "CANNOT_CHECK_NO_ADMITTING_WORLD"
    else:
        ok = all(p["holm_p_continued_vs_reset"] < 0.05 and p["mean_B"]["CONTINUED"] < p["mean_B"]["RESET"]
                 and p["mean_B"]["CONTINUED"] < p["mean_B"]["SHUFFLED_HISTORY"] for p in admitting) and law_v == "HOLDS"
        terminal = "HISTORY_INDUCED_SEARCH_PRIOR_REPLICATED" if ok else "NOT_REPLICATED"
    adjp = holm([p["p_parent_vs_reset_DESCRIPTIVE"] for p in scored]) if scored else []
    for p, q in zip(scored, adjp): p["holm_p_parent_vs_reset_DESCRIPTIVE"] = q
    out = {"schema": "OCM_M2P2_STAGE3_V1", "terminal": terminal, "admission_law": law_v,
           "worlds_scored": len(scored), "worlds_admitting": len(admitting),
           "descriptive": {"library_only_equals_reset_all": all(p["library_only_equals_reset"] for p in scored),
                           "shuffled_worse_than_reset_all": all(p["shuffled_worse_than_reset"] for p in scored),
                           "parent_vs_reset_min": min((p["parent_vs_reset"] for p in scored if p["parent_vs_reset"] is not None), default=None),
                           "parent_vs_reset_max": max((p["parent_vs_reset"] for p in scored if p["parent_vs_reset"] is not None), default=None),
                           "note": "the no-gate parent is the counterfactual named by the freeze, never deployment; its contrast is descriptive"},
           "per_world": per}
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps({k: v for k, v in out.items() if k != "per_world"}, indent=1))
    for p in per: print(p["world"], p.get("terminal"), "admitted", p.get("admitted"), "law", p.get("admission_law"), "rec", p.get("chunks_recovered"), "/", p.get("chunks"), "parent", p.get("parent_vs_reset"), "holm_desc", p.get("holm_p_parent_vs_reset_DESCRIPTIVE"))


if __name__ == "__main__":
    main()

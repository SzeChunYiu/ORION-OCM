"""Reachability and cost-per-form tables generated from the executed receipts (the 'cost per intelligence' and
'reachability of existing forms' accounts asked for in the note). Reads every Stage D'/E'/E1/credit receipt and every
blind-recovery receipt under microscopes/results and writes GMI_COST_AND_REACHABILITY_TABLE_V1.{json,md}.

Cost per form (per ecology, per basis column B0 unless stated): the frozen lifecycle coordinates of the row at its top ladder
size — description length, exec per query, update+verification per event, revision cost — and the row's capability, so that
'development per cost' can be read directly: capability / lifecycle cost at the headline cell (H = 16, r = 1).

Reachability: for each blind-recovery receipt, which class was reached (winners or best elite), by which search family, at what
budget, with the existence certificate where recorded.
"""
from __future__ import annotations

import glob
import json
import os

from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
ROOT = os.path.dirname(HERE)
B0 = "B0_LOCAL_ADAPTIVE_TRANSDUCERS"
FORM = {"S4": "gradient net (dense numeric)", "S2": "exact program search", "S2a": "approximate program search", "S3": "particles (stochastic search)", "S5": "exemplar memory",
        "S5k": "kNN memory (defective, RV-021)", "S5h": "generalizing kNN memory", "S6": "algebraic (XOR-linear) identification", "S7": "Bayesian model averaging (posterior mean)",
        "R1": "RL as inference (consistency search)", "R2": "tabular Monte-Carlo Q", "R3": "REINFORCE policy net", "R4": "kNN credited action",
        "MONO_C": "monolithic compiled table", "MOD_U": "modular unversioned tables", "VLC": "versioned local compilation", "DENSE": "monolithic gradient net", "MEM": "triple memory", "KNN": "triple kNN"}


def per_event(R, n):
    return {"desc": R["desc"], "exec_q": R["exec"] / (16 * (n + 1)), "upd_e": R["upd"] / n, "ver_e": R["ver"] / n, "rev_e": R["rev"]}


def headline_cost(pe, H=16, r=1):
    return pe["desc"] + H * pe["exec_q"] + r * pe["upd_e"] + r * pe["ver_e"] + (r / 4) * pe["rev_e"]


def main():
    forms = []
    for path in sorted(glob.glob(os.path.join(RES, "STAGE_DE_SMOOTH_*.json")) + sorted(glob.glob(os.path.join(RES, "STAGE_DE_CREDIT_*.json")))):
        d = json.load(open(path))
        if "capability_by_cell" not in d: continue
        eco = d["ecology"]; n = eco.get("H") or eco.get("episodes") or 16; theta = eco["theta"]
        rows = {}
        for k, v in d["capability_by_cell"].items():
            row, col, size = k.split("|")
            if col != B0: continue
            rows.setdefault(row, {})[int(size)] = v
        for row, sizes in rows.items():
            top = max(sizes); R = d["R_by_cell"][f"{row}|{B0}|{top}"]; pe = per_event(R, n); cost = headline_cost(pe)
            forms.append({"receipt": os.path.basename(path), "ecology": d.get("run_tag"), "criterion": eco.get("capability_criterion"), "events": n, "row": row, "form": FORM.get(row, row), "size": top,
                          "capability": sizes[top], "admissible": sizes[top] >= theta, "desc": R["desc"], "exec_per_query": round(pe["exec_q"], 1), "update_per_event": round(pe["upd_e"], 1),
                          "verify_per_event": round(pe["ver_e"], 1), "revision": R["rev"], "lifecycle_cost_H16_r1": round(cost, 1), "capability_per_kilo_cost": round(1000 * sizes[top] / cost, 4) if cost else None})
    reach = []
    for path in sorted(glob.glob(os.path.join(RES, "STAGE_F_BLIND_RECOVERY_*.json"))):
        d = json.load(open(path))
        best = d.get("top_elites_canonicalized") or d.get("top_elites") or []
        reach.append({"receipt": os.path.basename(path), "revival_record": d.get("revival_record"), "ecology": (d.get("ecology") or {}).get("kind"), "search_family": (d.get("search_family") or d.get("search") or "random + hill-climb (V1 family)")[:90],
                      "n_evaluations": d.get("n_evaluations") or d.get("n_random") or d.get("budget"), "existence_certificate": d.get("existence_certificate") or d.get("planted_learner_score_in_this_ecology"),
                      "n_winners": d.get("n_winners_at_theta") if "n_winners_at_theta" in d else len(d.get("winners", [])), "winner_classes": sorted(set(d.get("winner_classes") or [w.get("class", "")[:14] for w in d.get("winners", [])])),
                      "best_score": d.get("best_score"), "best_elite_class": (best[0].get("class", "")[:24] if best else None)})
    out = {"schema": "GMICostAndReachabilityTableV1", "issue": 377, "cost_per_form_B0": forms, "reachability": reach}
    out["receipt_sha256"] = sha256_of({k: v for k, v in out.items() if k != "receipt_sha256"})
    json.dump(out, open(os.path.join(ROOT, "GMI_COST_AND_REACHABILITY_TABLE_V1.json"), "w"), indent=1, sort_keys=True, default=str)
    L = ["# Cost per form and reachability of forms — generated from the executed receipts (B0 column; headline cell H = 16, r = 1)\n",
         "Lifecycle cost = desc + 16·exec/query + update/event + verify/event + revision/4. 'Capability per kilo-cost' is the note's d(development)/d(cost) read at the headline cell: it is a ratio at one point of the (H, r) diagram, not a derivative law.\n",
         "| receipt | row | form | capability | admissible | desc | exec/query | update/event | verify/event | revision | lifecycle cost | capability per kilo-cost |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for f in forms:
        L.append(f"| {f['receipt'].replace('STAGE_DE_SMOOTH_', '').replace('.json', '')} | {f['row']} | {f['form']} | {f['capability']} | {'yes' if f['admissible'] else ''} | {f['desc']} | {f['exec_per_query']} | {f['update_per_event']} | {f['verify_per_event']} | {f['revision']} | {f['lifecycle_cost_H16_r1']} | {f['capability_per_kilo_cost']} |")
    L += ["\n## Reachability (label-free search)\n", "| receipt | record | ecology | search family | evaluations | existence certificate | winners | winner classes | best score | best elite class |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in reach:
        L.append(f"| {r['receipt'].replace('STAGE_F_BLIND_RECOVERY_', '').replace('.json', '')} | {r['revival_record']} | {r['ecology']} | {r['search_family']} | {r['n_evaluations']} | {str(r['existence_certificate'])[:40]} | {r['n_winners']} | {', '.join(c[:14] for c in r['winner_classes'])} | {r['best_score']} | {r['best_elite_class']} |")
    open(os.path.join(ROOT, "GMI_COST_AND_REACHABILITY_TABLE_V1.md"), "w").write("\n".join(L) + "\n")
    return out


if __name__ == "__main__":
    o = main()
    print(len(o["cost_per_form_B0"]), "form rows;", len(o["reachability"]), "reachability rows")
    for f in o["cost_per_form_B0"]:
        if f["admissible"]: print(f"  {f['receipt'][16:44]:30s} {f['row']:6s} cap {f['capability']:.4f} cost {f['lifecycle_cost_H16_r1']:>10.0f} cap/kcost {f['capability_per_kilo_cost']}")

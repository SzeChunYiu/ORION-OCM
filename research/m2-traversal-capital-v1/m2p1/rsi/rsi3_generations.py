#!/usr/bin/env python3
"""RSI-3/4: an improving slope across matched diagnoser generations.

L6 requires "improvement of the improvement process itself" -- a prospectively registered
improving slope in cost_to_verified_improvement across matched generations, not one
successful self-change. RSI-1 -> RSI-2 is one step. This runs the mechanic for three
generations and measures whether each generation's FAILURES improve the next.

The generation loop, applied to the diagnoser itself:
    G_n diagnoses the sealed packet (all 8 cases, hidden truth)
    -> its misses are examined ONLY through internally computable signals
    -> the miss localises a missing probe (this is the RSI step: a failure of the
       improvement process producing a change to the improvement process)
    -> G_(n+1) = G_n + that probe, nothing else
    -> measure cost_to_verified_improvement and accuracy

Probes are added in the order their necessity was discovered, each justified by a
counterexample from the previous generation's misses -- never by peeking at truth:
    G0  RSI-1's six probes, mechanism likelihoods
    G1  + compression_gain     (RSI-1 miss: C3 vs C1 unseparated; needs structure-existence)
    G2  + oracle_also_fails    (RSI-2 miss: C2 outvoted; D1/D2 true-motif library ALSO
                                fails -- deterministic depth signature)
    G3  + drift_signal         (GAP_AUDIT: no cause class for ecology shift; adds C5)

cost_to_verified_improvement(G) = probe cost spent per correctly repaired case.
An improving slope means this falls, or accuracy rises at matched cost, generation over
generation. Likelihoods are NEVER refit; each generation differs from the last by exactly
one mechanism-derived probe. That is what makes the generations MATCHED.
"""
from __future__ import annotations
import argparse, json, statistics
from pathlib import Path

CAUSES = ["C0_NO_FAILURE", "C1_INCOMPLETE_RECOVERY", "C2_ARRANGEMENT_DEPTH",
          "C3_UNSTRUCTURED_ECOLOGY", "C4_ESTIMATOR_VARIANCE", "C5_ECOLOGY_SHIFT"]
REPAIR = {"C0_NO_FAILURE": "none", "C1_INCOMPLETE_RECOVERY": "MDL_SELECTION",
          "C2_ARRANGEMENT_DEPTH": "REDUCE_K_OR_RAISE_P", "C3_UNSTRUCTURED_ECOLOGY": "APPLICABILITY_GATE",
          "C4_ESTIMATOR_VARIANCE": "EXPECTED_UTILITY_ADMISSION", "C5_ECOLOGY_SHIFT": "DEPLOYMENT_LIVENESS"}
VALIDATED = {"E7_longhorizon": "MDL_SELECTION", "E3_16motifs": "MDL_SELECTION",
             "D1_m12k4": "REDUCE_K_OR_RAISE_P", "D2_m12k4": "REDUCE_K_OR_RAISE_P",
             "FOREIGN_M1": "APPLICABILITY_GATE", "E5_healthy": "none", "E8_healthy": "none",
             "E6_healthy": "none", "PLAST_shift": "DEPLOYMENT_LIVENESS"}
COST = {"composability": 4, "guided_depth": 4, "winrate": 1, "ci_shape": 1,
        "compression_gain": 3, "oracle_also_fails": 6, "drift_signal": 2,
        "mdl_response": 8,   # re-mine + re-validate: the dearest probe
        "probe_pays": 2, "admitted": 0}   # arithmetic on the library; the gate's own verdict


def obs(c):
    r = c["better"] / c["heldout"]
    return {
        "composability": "high" if c["composable_frac"] >= .9 else "partial" if c["composable_frac"] >= .3 else "none",
        "guided_depth": "deep" if c["tokens_needed"] >= 4 else "shallow",
        "winrate": "majority" if r >= .6 else "minority" if r >= .25 else "rare",
        "ci_shape": "straddles" if (c["mean_delta"] > 0 and c["ci95_low"] <= 0) else "positive" if c["ci95_low"] > 0 else "negative",
        "compression_gain": "high" if c.get("mdl_gain", 0) >= .35 else "low" if c.get("mdl_gain", 0) >= .12 else "none",
        "oracle_also_fails": "yes" if c.get("oracle_fails") else "no",
        "drift_signal": "yes" if c.get("drift") else "no",
        "probe_pays": ("unknown" if c.get("probe_pays_frac") is None else
                       "high" if c["probe_pays_frac"] >= 0.6 else "low" if c["probe_pays_frac"] >= 0.2 else "none"),
        "admitted": ("unknown" if c.get("admitted") is None else "yes" if c["admitted"] else "no"),
        "mdl_response": ("unknown" if c.get("mdl_response") is None else
                         "improves" if c["mdl_response"] > 0 else
                         "flat" if c["mdl_response"] == 0 else "worsens"),
    }


LIK = {
 "composability": {"none": {"C3": .55, "C1": .30, "C2": .10, "C4": .03, "C0": .02, "C5": .10},
                   "partial": {"C1": .50, "C2": .25, "C3": .15, "C4": .07, "C0": .03, "C5": .15},
                   "high": {"C0": .40, "C2": .30, "C4": .20, "C1": .08, "C3": .02, "C5": .10}},
 "guided_depth": {"deep": {"C2": .65, "C1": .15, "C4": .10, "C3": .05, "C0": .05, "C5": .05},
                  "shallow": {"C1": .30, "C0": .25, "C3": .20, "C4": .15, "C2": .10, "C5": .15}},
 "winrate": {"rare": {"C3": .40, "C1": .35, "C2": .18, "C4": .05, "C0": .02, "C5": .20},
             "minority": {"C1": .40, "C2": .28, "C3": .18, "C4": .10, "C0": .04, "C5": .20},
             "majority": {"C0": .55, "C4": .20, "C2": .13, "C1": .10, "C3": .02, "C5": .05}},
 "ci_shape": {"straddles": {"C4": .60, "C1": .18, "C3": .12, "C2": .06, "C0": .04, "C5": .10},
              "negative": {"C1": .38, "C2": .32, "C3": .22, "C4": .05, "C0": .03, "C5": .25},
              "positive": {"C0": .45, "C4": .25, "C2": .18, "C1": .10, "C3": .02, "C5": .05}},
 "compression_gain": {"none": {"C3": .70, "C1": .15, "C2": .10, "C4": .03, "C0": .02, "C5": .30},
                      "low": {"C1": .45, "C2": .25, "C3": .15, "C4": .10, "C0": .05, "C5": .25},
                      "high": {"C0": .40, "C4": .25, "C2": .20, "C1": .13, "C3": .02, "C5": .15}},
 # oracle-also-fails: if even the TRUE motif set does not help, the library is not the
 # problem -- the target is unreachable at this depth. Deterministic, so sharp.
 "oracle_also_fails": {"yes": {"C2": .85, "C5": .08, "C3": .04, "C1": .02, "C4": .01, "C0": .01},
                       "no": {"C1": .28, "C0": .22, "C3": .20, "C4": .15, "C5": .10, "C2": .05}},
 # drift: a library that WAS admitted and helped, and now hurts on a rolling window
 # depth bound: if even the cheapest target sits below 2g, no library can be reached
 # before baseline on it -- depth is the binding constraint regardless of recovery
 # probe_pays: the cost rule's own estimate of how many solved validation targets a
 # guided probe would reach before their baseline index. "none" with a complete-looking
 # library is depth (C2); "high" is a library that pays (C0-like); C1 sits in between
 # because an incomplete library tiles fewer targets at all.
 "probe_pays": {"none": {"C2": .55, "C3": .20, "C1": .15, "C5": .06, "C4": .03, "C0": .01},
                "low": {"C1": .35, "C2": .30, "C3": .15, "C4": .10, "C5": .07, "C0": .03},
                "high": {"C0": .45, "C1": .25, "C4": .15, "C5": .10, "C2": .03, "C3": .02},
                "unknown": {c: 1/6 for c in ("C0","C1","C2","C3","C4","C5")}},
 # the gate's own verdict: an admitted library is, by definition, not a failure
 "admitted": {"yes": {"C0": .85, "C5": .08, "C4": .04, "C1": .01, "C2": .01, "C3": .01},
              "no": {"C1": .30, "C2": .25, "C3": .18, "C4": .15, "C5": .10, "C0": .02},
              "unknown": {c: 1/6 for c in ("C0","C1","C2","C3","C4","C5")}},
 # MDL reselection helps iff displaced structure EXISTS (C1). No structure (C3) -> flat;
 # depth (C2) -> flat, the library is not the bottleneck; healthy (C0) -> flat/worse.
 "mdl_response": {"improves": {"C1": .70, "C5": .10, "C4": .08, "C2": .05, "C3": .04, "C0": .03},
                  "flat": {"C3": .30, "C2": .25, "C0": .20, "C4": .12, "C5": .08, "C1": .05},
                  "worsens": {"C0": .40, "C3": .25, "C4": .15, "C2": .10, "C5": .07, "C1": .03},
                  "unknown": {c: 1/6 for c in ("C0","C1","C2","C3","C4","C5")}},
 "drift_signal": {"yes": {"C5": .80, "C3": .10, "C1": .05, "C2": .02, "C4": .02, "C0": .01},
                  "no": {"C0": .25, "C1": .22, "C2": .18, "C3": .18, "C4": .15, "C5": .02}},
}

GENERATIONS = [
    ("G0", ["composability", "guided_depth", "winrate", "ci_shape"]),
    ("G1", ["composability", "guided_depth", "winrate", "ci_shape", "compression_gain"]),
    ("G2", ["composability", "guided_depth", "winrate", "ci_shape", "compression_gain", "oracle_also_fails"]),
    ("G3", ["composability", "guided_depth", "winrate", "ci_shape", "compression_gain", "oracle_also_fails", "drift_signal"]),
    ("G4", ["composability", "guided_depth", "winrate", "ci_shape", "compression_gain", "oracle_also_fails", "drift_signal", "mdl_response"]),
    ("G5", ["composability", "guided_depth", "winrate", "ci_shape", "compression_gain", "oracle_also_fails", "drift_signal", "mdl_response", "probe_pays"]),
    ("G6", ["composability", "guided_depth", "winrate", "ci_shape", "compression_gain", "oracle_also_fails", "drift_signal", "mdl_response", "probe_pays", "admitted"]),
]


import math

def _entropy(p):
    return -sum(v * math.log(v + 1e-12) for v in p.values())

def _update(post, p, o):
    tab = LIK[p].get(o, {})
    post = {c: post[c] * tab.get(c.split("_")[0], .02) for c in post}
    s = sum(post.values()) or 1
    return {k: v / s for k, v in post.items()}

def diagnose_active(case, available, stop=0.6):
    """VOI policy pre-registered in RSI-1: max expected info gain per cost, stop at 0.6."""
    post = {c: 1.0 / len(CAUSES) for c in CAUSES}
    o = obs(case)
    remaining, spent, used = list(available), 0, []
    while remaining:
        best, score = None, -1e9
        for p in remaining:
            exp_h = 0.0
            for oo, tab in LIK[p].items():
                p_oo = sum(post[c] * tab.get(c.split("_")[0], .02) for c in post)
                if p_oo > 0:
                    exp_h += p_oo * _entropy(_update(post, p, oo))
            g = (_entropy(post) - exp_h) / COST[p]
            if g > score:
                best, score = p, g
        remaining.remove(best)
        spent += COST[best]
        used.append(best)
        post = _update(post, best, o[best])
        top = max(post, key=post.get)
        if post[top] >= stop:
            break
    top = max(post, key=post.get)
    return top, round(post[top], 3), spent, used

def diagnose(case, probes_used):
    post = {c: 1.0 / len(CAUSES) for c in CAUSES}
    o = obs(case)
    for p in probes_used:
        tab = LIK[p].get(o[p], {})
        post = {c: post[c] * tab.get(c.split("_")[0], .02) for c in post}
        s = sum(post.values()) or 1
        post = {k: v / s for k, v in post.items()}
    top = max(post, key=post.get)
    return top, round(post[top], 3)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mode", choices=("exhaustive", "active"), default="exhaustive")
    a = ap.parse_args()
    cases = json.loads(Path(a.cases).read_text())["cases"]

    gens = []
    for name, probes in GENERATIONS:
        cost = 0
        correct_cause = correct_repair = 0
        calls = {}
        for c in cases:
            if a.mode == "active":
                top, conf, spent, used = diagnose_active(c, probes)
                cost += spent
            else:
                top, conf = diagnose(c, probes)
                cost += sum(COST[p] for p in probes)
            calls[c["name"]] = top
            correct_cause += int(top == c["true_cause"])
            # scoring fix: mechanically-labelled cases carry no hand-validated repair;
            # their validated repair is the one mapped to the true cause, exactly as for
            # the originals (each of whose validated repairs IS REPAIR[true_cause]).
            correct_repair += int(REPAIR[top] == VALIDATED.get(c["name"], REPAIR[c["true_cause"]]))
        acc = correct_cause / len(cases)
        rep = correct_repair / len(cases)
        ctvi = cost / correct_repair if correct_repair else float("inf")
        gens.append({"generation": name, "probes": probes, "probe_cost_total": cost,
                     "cause_accuracy": round(acc, 3), "repair_accuracy": round(rep, 3),
                     "cost_to_verified_improvement": round(ctvi, 2), "calls": calls})
        print("%s probes=%d cost=%-4d cause_acc=%.3f repair_acc=%.3f  cost_to_verified_improvement=%.2f" % (
            name, len(probes), cost, acc, rep, ctvi))

    # confusion for the last generation, to localise the next missing probe
    last = gens[-1]; conf = {}
    for c in cases:
        conf.setdefault(c["true_cause"], {}); conf[c["true_cause"]][last["calls"][c["name"]]] = conf[c["true_cause"]].get(last["calls"][c["name"]], 0) + 1
    print("\nconfusion (%s):" % last["generation"])
    for tc, row in sorted(conf.items()):
        print("  %-24s -> %s" % (tc, ", ".join("%s:%d" % (k.split("_")[0], v) for k, v in sorted(row.items(), key=lambda kv: -kv[1]))))
    ctv = [g["cost_to_verified_improvement"] for g in gens]
    acc = [g["repair_accuracy"] for g in gens]
    slope_ok = all(ctv[i + 1] <= ctv[i] for i in range(len(ctv) - 1)) and acc[-1] > acc[0]
    out = {"schema": "OCM_RSI3_GENERATIONS_V1", "lane": "LANE_M2_TRAVERSAL_CAPITAL_OPUS",
           "stage": "RSI-3/RSI-4", "mode": a.mode, "cases": len(cases), "causes": CAUSES,
           "generations": gens,
           "cost_to_verified_improvement_by_generation": ctv,
           "repair_accuracy_by_generation": acc,
           "improving_slope": slope_ok, "confusion_last": conf,
           "terminal": ("RECURSIVE_ACCELERATION_CANDIDATE" if slope_ok
                        else "NO_IMPROVING_SLOPE"),
           "matching": ("generations differ by exactly one mechanism-derived probe each, "
                        "added in the order its necessity was discovered from the previous "
                        "generation's misses; likelihoods are never refit"),
           "claim_ceiling": ("eight natural cases plus one shift case from one lane; the "
                             "probes were selected by human/AI analysis of the misses, so "
                             "this is the improvement process being IMPROVED by failure, "
                             "not yet the organism doing the improving autonomously")}
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print("\ncost_to_verified_improvement:", ctv, "| repair accuracy:", acc)
    print("TERMINAL:", out["terminal"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

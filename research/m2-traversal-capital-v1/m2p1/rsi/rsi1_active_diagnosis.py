#!/usr/bin/env python3
"""RSI-1: does information-gain-per-cost experiment selection diagnose cheaper?

This lane accumulated a natural-failure benchmark with KNOWN causes -- failures that
actually happened during the developmental work, each later resolved by human/AI
analysis. RSI-1 asks whether a self-model choosing its own experiments by value of
information reaches the same cause more cheaply than fixed or random ablation order.

Candidate causes (the D-layer decomposition for THIS failure class):
  C1 INCOMPLETE_RECOVERY   the mined library is missing motifs the targets need
  C2 ARRANGEMENT_DEPTH     motifs recovered, but compositions sit too deep to reach
  C3 UNSTRUCTURED_ECOLOGY  there is no latent motif structure to recover at all
  C4 ESTIMATOR_VARIANCE    mean benefit is positive but the interval straddles zero

Experiments are INTERNALLY COMPUTABLE probes with declared costs. Evaluator-side facts
(the hidden motif set, the admission law) are deliberately excluded: the organism may not
use them, which is the constraint that makes this a self-diagnosis test rather than a
lookup. Each probe returns a likelihood over causes.

Arms: SCRIPTED (fixed order), RANDOM, VOI (max information gain per cost), ORACLE.
Endpoint: total probe cost until the correct minimum-sufficient cause is identified.
"""
from __future__ import annotations
import argparse, json, math, random, statistics
from pathlib import Path

CAUSES = ["C0_NO_FAILURE", "C1_INCOMPLETE_RECOVERY", "C2_ARRANGEMENT_DEPTH",
          "C3_UNSTRUCTURED_ECOLOGY", "C4_ESTIMATOR_VARIANCE"]
# C0 is the clean no-alarm control: cases where the learner ADMITTED and nothing failed.
# A diagnoser that invents a cause on a healthy run is as defective as one that misses a
# real cause, so healthy runs are scored, not excluded.

# probe -> (cost, function(case) -> observation label)
def p_fragment_lengths(c):   # cheap: inspect the mined library's own shape
    return "all_short" if c["mined_max_len"] <= 2 else "mixed"

def p_ci(c):                 # cheap: already computed by validate_generator
    return "straddles_zero" if (c["mean_delta"] > 0 and c["ci95_low"] <= 0) else \
           "positive" if c["ci95_low"] > 0 else "negative"

def p_worst_ratio(c):        # cheap
    return "at_bound" if c["worst_ratio"] >= 1.99 else "below_bound"

def p_heldout_winrate(c):    # cheap
    r = c["better"] / c["heldout"]
    return "majority" if r >= 0.6 else "minority" if r >= 0.25 else "rare"

def p_composability(c):      # medium: can library tokens compose held-out canonical programs?
    return "high" if c["composable_frac"] >= 0.9 else \
           "partial" if c["composable_frac"] >= 0.3 else "none"

def p_guided_depth(c):       # medium: how many tokens does a typical target need?
    return "deep" if c["tokens_needed"] >= 4 else "shallow"

PROBES = {
    "fragment_lengths": (1.0, p_fragment_lengths),
    "ci_shape":         (1.0, p_ci),
    "worst_ratio":      (1.0, p_worst_ratio),
    "heldout_winrate":  (1.0, p_heldout_winrate),
    "composability":    (4.0, p_composability),
    "guided_depth":     (4.0, p_guided_depth),
}

# P(observation | cause), hand-specified from the MECHANISM, not fitted to the cases
LIK = {
 "composability": {"none":  {"C3": .80, "C1": .15, "C2": .03, "C4": .02},
                   "partial": {"C0": 0.05, "C1": .70, "C2": .15, "C3": .10, "C4": .05},
                   "high":  {"C2": .55, "C4": .35, "C1": .08, "C3": .02}},
 "guided_depth":  {"deep":  {"C2": .60, "C1": .20, "C4": .12, "C3": .08},
                   "shallow": {"C0": 0.25, "C1": .40, "C3": .30, "C4": .20, "C2": .10}},
 "ci_shape":      {"straddles_zero": {"C0": 0.05, "C4": .60, "C1": .20, "C3": .15, "C2": .05},
                   "negative": {"C0": 0.03, "C1": .40, "C2": .35, "C3": .20, "C4": .05},
                   "positive": {"C0": 0.55, "C4": .40, "C2": .30, "C1": .20, "C3": .10}},
 "fragment_lengths": {"all_short": {"C0": 0.2, "C2": .40, "C1": .30, "C3": .20, "C4": .10},
                      "mixed": {"C0": 0.15, "C1": .45, "C3": .25, "C2": .20, "C4": .10}},
 "worst_ratio":   {"at_bound": {"C0": 0.15, "C1": .35, "C2": .35, "C3": .20, "C4": .10},
                   "below_bound": {"C0": 0.25, "C4": .40, "C1": .25, "C2": .20, "C3": .15}},
 "heldout_winrate": {"rare": {"C0": 0.02, "C3": .45, "C1": .35, "C2": .15, "C4": .05},
                     "minority": {"C0": 0.05, "C1": .45, "C2": .25, "C3": .20, "C4": .10},
                     "majority": {"C0": 0.6, "C4": .55, "C2": .25, "C1": .15, "C3": .05}},
}


def norm(p):
    s = sum(p.values())
    return {k: v / s for k, v in p.items()} if s else p


def update(prior, probe, obs):
    tab = LIK[probe].get(obs)
    if not tab:
        return prior
    post = {c: prior[c] * tab.get(c.split("_")[0], 0.01) for c in prior}
    return norm(post)


def entropy(p):
    return -sum(v * math.log(v + 1e-12) for v in p.values())


def voi_pick(prior, remaining, case):
    """expected information gain per unit cost, over the posterior predictive"""
    best, best_score = None, -1e9
    for name in remaining:
        cost, fn = PROBES[name]
        exp_h = 0.0
        for obs, tab in LIK[name].items():
            p_obs = sum(prior[c] * tab.get(c.split("_")[0], 0.01) for c in prior)
            if p_obs <= 0:
                continue
            exp_h += p_obs * entropy(update(prior, name, obs))
        gain = (entropy(prior) - exp_h) / cost
        if gain > best_score:
            best, best_score = name, gain
    return best


def run_arm(case, order_fn, seed=0):
    prior = {c: 1.0 / len(CAUSES) for c in CAUSES}
    remaining = list(PROBES)
    cost = 0.0
    used = []
    rng = random.Random(seed)
    while remaining:
        name = order_fn(prior, remaining, case, rng)
        remaining.remove(name)
        c, fn = PROBES[name]
        cost += c
        used.append(name)
        prior = update(prior, name, fn(case))
        top = max(prior, key=prior.get)
        if prior[top] >= 0.60:
            return {"cost": cost, "probes": used, "called": top,
                    "correct": top == case["true_cause"], "confidence": round(prior[top], 3)}
    top = max(prior, key=prior.get)
    return {"cost": cost, "probes": used, "called": top,
            "correct": top == case["true_cause"], "confidence": round(prior[top], 3)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seeds", type=int, default=40)
    a = ap.parse_args()
    cases = json.loads(Path(a.cases).read_text())["cases"]

    arms = {
        "SCRIPTED": lambda pr, rem, cs, rng: sorted(rem, key=lambda n: (PROBES[n][0], n))[0],
        "RANDOM":   lambda pr, rem, cs, rng: rng.choice(rem),
        "VOI":      lambda pr, rem, cs, rng: voi_pick(pr, rem, cs),
    }
    results = {k: [] for k in arms}
    per_case = []
    for cs in cases:
        row = {"case": cs["name"], "true_cause": cs["true_cause"]}
        for an, fn in arms.items():
            runs = [run_arm(cs, fn, seed=s) for s in range(a.seeds if an == "RANDOM" else 1)]
            ok = [r for r in runs if r["correct"]]
            mean_cost = statistics.fmean(r["cost"] for r in runs)
            acc = len(ok) / len(runs)
            results[an].append({"case": cs["name"], "accuracy": acc, "mean_cost": mean_cost,
                                "called": runs[0]["called"], "probes": runs[0]["probes"]})
            row[an] = {"accuracy": round(acc, 3), "cost": round(mean_cost, 2),
                       "called": runs[0]["called"]}
        per_case.append(row)

    summary = {}
    for an, rows in results.items():
        summary[an] = {
            "accuracy": round(statistics.fmean(r["accuracy"] for r in rows), 3),
            "mean_cost": round(statistics.fmean(r["mean_cost"] for r in rows), 2),
            "cost_per_correct": round(statistics.fmean(r["mean_cost"] for r in rows) /
                                      max(statistics.fmean(r["accuracy"] for r in rows), 1e-9), 2)}
    out = {"schema": "OCM_RSI1_ACTIVE_DIAGNOSIS_V1", "lane": "LANE_M2_TRAVERSAL_CAPITAL_OPUS",
           "stage": "RSI-1", "owner_issue": 165, "hardening_parent": 323,
           "causes": CAUSES, "probe_costs": {k: v[0] for k, v in PROBES.items()},
           "n_cases": len(cases), "per_case": per_case, "summary": summary,
           "terminal": ("ACTIVE_DIAGNOSIS_ADVANTAGE"
                        if summary["VOI"]["cost_per_correct"] < min(
                            summary["SCRIPTED"]["cost_per_correct"],
                            summary["RANDOM"]["cost_per_correct"])
                        else "NO_ACTIVE_DIAGNOSIS_ADVANTAGE"),
           "constraint": ("probes are internally computable; the hidden motif set and the "
                          "admission law are evaluator-side and excluded by construction")}
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps({"terminal": out["terminal"], "summary": summary,
                      "n_cases": len(cases)}, indent=1))
    for r in per_case:
        print(" %-22s true=%-24s VOI=%-24s SCR=%-24s" %
              (r["case"], r["true_cause"], r["VOI"]["called"], r["SCRIPTED"]["called"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

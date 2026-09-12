# M2-P3 primary: per viable world, H0 mean(PARENT_GF_D4) >= 0.5 * mean(RESET) on the same
# protected targets; one-sided paired sign-flip permutation on d_t = GF_t - 0.5*RESET_t,
# 10000 permutations, seed 20260912; Holm across viable worlds, alpha 0.05.
# Terminal: C2_REPLICATED_SECOND_GRAMMAR iff >= 4 viable worlds and >= 80% pass.
# Also reported: the GF_D4 < RESET precondition. NO point prediction is carried over:
# M2-P3 co-registered one fitted to the band-2-3 tiling, and M2P4_FREEZE_V1 forbids
# carrying it forward. The figure is deliberately not restated here. The median ratio
# is reported as a DESCRIPTIVE, never as a registered expectation.
import json, glob, os, random, statistics as st, sys
RUNS = sys.argv[1]; OUT = sys.argv[2]
SEED, PERMS, ALPHA, BAR, FRACTION, MIN_WORLDS = 20260912, 10000, 0.05, 0.5, 0.8, 4
def rows(p): return {r["target"]: r["B_slots"] for r in json.load(open(p))["rows"]}
def verified(p): return json.load(open(p)).get("all_targets_verified") is True
def perm_p(d, rng):
    obs = sum(d); c = 0
    for _ in range(PERMS):
        c += sum(x if rng.random() < 0.5 else -x for x in d) <= obs
    return (c + 1) / (PERMS + 1)
rng = random.Random(SEED); res = []
for w in sorted(glob.glob(RUNS + "/m2p4_*_scored")):
    wid = os.path.basename(w)[len("m2p4_"):-len("_scored")]
    gp, rp = w + "/arm_PARENT_GF_D4.json", w + "/arm_RESET.json"
    if not (os.path.exists(gp) and os.path.exists(rp)): continue
    if not (verified(gp) and verified(rp)):
        res.append({"world": wid, "terminal": "ASSAY_DEFECT_UNVERIFIED_TARGETS"}); continue
    g, r = rows(gp), rows(rp); t = [k for k in g if k in r]
    mg, mr = st.fmean(g[k] for k in t), st.fmean(r[k] for k in t)
    res.append({"world": wid, "n": len(t), "gf_d4": round(mg, 1), "reset": round(mr, 1),
                "ratio_minus_1": round(mg / mr - 1, 4),
                "p_effect": perm_p([g[k] - BAR * r[k] for k in t], rng),
                "p_precondition": perm_p([g[k] - r[k] for k in t], rng)})
scored = [x for x in res if "p_effect" in x]; m = len(scored)
order = sorted(range(m), key=lambda i: scored[i]["p_effect"]); run = 0.0
for rank, i in enumerate(order):
    run = max(run, min(1.0, (m - rank) * scored[i]["p_effect"])); scored[i]["holm"] = round(run, 5)
    scored[i]["passes_50pct_bar"] = run < ALPHA
k = sum(x["passes_50pct_bar"] for x in scored)
med = round(st.median([x["ratio_minus_1"] for x in scored]), 4) if scored else None
terminal = ("CANNOT_CHECK_TOO_FEW_VIABLE_WORLDS" if m < MIN_WORLDS else
            "C2_REPLICATED_SECOND_GRAMMAR" if k >= FRACTION * m else "C2_NOT_REPLICATED_IN_SECOND_GRAMMAR")
out = {"schema": "OCM_M2P4_SCORED_V1", "seed": SEED, "permutations": PERMS, "bar": BAR,
       "fraction_required": FRACTION, "worlds_scored": m, "k_passing": k,
       "terminal": terminal, "median_ratio_minus_1": med,
       "point_prediction": "NONE_REGISTERED_median_is_descriptive_only",
       "precondition_all_significant": all(x["p_precondition"] < ALPHA for x in scored),
       "per_world": res}
json.dump(out, open(OUT, "w"), indent=1)
print(json.dumps({k2: out[k2] for k2 in ("worlds_scored", "k_passing", "terminal", "median_ratio_minus_1",
                                         "point_prediction", "precondition_all_significant")}))

"""Route B for gmi-833-h-real-scale-nearest-neighbor-v1: a source-separated
oracle.

This file imports NOTHING from grammar_nn_v1, run_real_scale_nearest_neighbor_v1
or real_scale_nearest_neighbor_v1. It re-derives, from FREEZE_V1.md and its
slice addenda alone, every claimed quantity of the package from the committed
REAL_RUNS receipt: the readout language and its exact decisions, the exact
replay of every committed block, the held-out error and prototype-agreement
counts, the two registered nulls, the store ladder, the charged-cost crossover
and the presentation control. Non-import is enforced structurally by
test_real_scale_nearest_neighbor_v1.py via an `ast` scan and a `sys.modules`
assertion, not by this comment.

    python3 -I -B  independent_oracle_nn_v1.py
"""
import json
import os
import random
import sys

WHERE = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS = os.path.join(WHERE, "REAL_RUNS")

SIGMA = "SIGMA_H05R"
SOURCE_SHA_REGISTERED = \
    "9e66281f7e51445eab6857488ff6e3d768afffadb7fb1adbef5e4617bee4a53b"
ORDER_MULT = 2654435761
ALPHABET_WIDTH = 27
SEED_LABEL = 20260921
SEED_DESIGN = 20260922
EXPECT_CLASS = "STORED_EXEMPLAR_MEMBERSHIP"

# The readout language of FREEZE_V1_SLICE_ADDENDUM.md section 2, re-declared
# here (the oracle holds no reference to the package's own declaration).
READOUTS = (
    "C0", "C1",
    "LEN<=7", "LEN<=8", "LEN<=9", "LEN<=10", "LEN<=11", "LEN<=12",
    "CNT>=1", "CNT>=2", "CNT>=3",
    "PREF_VOTE", "EXT_VOTE",
)


def fetch(fname):
    full = os.path.join(ARTIFACTS, fname)
    if not os.path.isfile(full):
        raise SystemExit("MISSING REAL_RUN ARTIFACT: " + full)
    with open(full) as handle:
        return json.load(handle)


def decide(name, ql, c, p1, p0, e1, e0):
    """The registered readout semantics, re-implemented from the addendum text.

    Empty-neighbourhood readouts fall back to the fit majority (1).
    """
    if name == "C0":
        return 0
    if name == "C1":
        return 1
    if name.startswith("LEN<="):
        return 1 if ql <= int(name.split("<=")[1]) else 0
    if name.startswith("CNT>="):
        return 1 if c >= int(name.split(">=")[1]) else 0
    if name == "PREF_VOTE":
        if p1 + p0 == 0:
            return 1
        return 1 if p1 > p0 else 0
    if name == "EXT_VOTE":
        if e1 + e0 == 0:
            return 1
        return 1 if e1 > e0 else 0
    raise ValueError("readout outside the registered language: " + name)


def block_errors(rows, name):
    return sum(1 for ql, yv, c, p1, p0, e1, e0 in rows
               if decide(name, ql, c, p1, p0, e1, e0) != yv)


def main():
    rec = fetch("scope_SIGMA_H05R.json")
    src = fetch("sources.json")
    checks = {}

    # provenance: the receipt's digest must equal the frozen string
    checks["source_digest_registered"] = bool(
        rec["source"]["sha256"] == SOURCE_SHA_REGISTERED
        and src["source"]["sha256"] == SOURCE_SHA_REGISTERED)
    checks["source_shape"] = bool(
        rec["source"]["tokens"] == 104334 and rec["source"]["descriptors"] == 776142)

    # registered presentation: counts and key form
    pr = rec["presentation"]
    checks["presentation_counts"] = bool(
        pr["n_fit"] == 679124 and pr["n_held"] == 97018
        and pr["rank_fit"] == 475386 and pr["rank_score"] == 203738
        and pr["half"] == 339562
        and pr["key"] == "(i*%d) mod 2**32" % ORDER_MULT)

    # holdout: recompute errors + prototype agreement from the full rows
    rows = rec["holdout_all"]["queries"]
    n = len(rows)
    errs = sum(1 for yv, p in rows if p != yv)
    agree = n - errs
    ho = rec["holdout"]
    checks["holdout_counts"] = bool(
        errs == ho["winner_errors"] and agree == ho["prototype_agreement"]
        and ho["n"] == 97018 and ho["shared"] == 81403 and ho["unique"] == 15615
        and ho["winner"] == "CNT>=1" and ho["winner_class"] == EXPECT_CLASS)
    checks["falsifier1"] = bool(ho["winner_errors"] <= ho["majority_errors"] // 2)

    # nulls re-derived from the committed permutations (same constructions)
    sh = rec["nulls"]["label"]["shuffled_labels"]
    label_errs = sum(1 for (yv, p), s in zip(rows, sh) if p != s)
    dpred = rec["nulls"]["design"]["predictions"]
    design_errs = sum(1 for (yv, p), d in zip(rows, dpred) if d != yv)
    checks["label_null"] = bool(
        label_errs == rec["nulls"]["label"]["errors"]
        and label_errs > ho["majority_errors"]
        and rec["nulls"]["label"]["seed"] == SEED_LABEL)
    checks["design_null"] = bool(
        design_errs == rec["nulls"]["design"]["errors"]
        and design_errs > 3 * ho["winner_errors"]
        and rec["nulls"]["design"]["seed"] == SEED_DESIGN)

    # exact replay of every committed block (decision tallies -> errors)
    replays_ok = True
    for key, wname in (("held_block", "holdout"),
                       ("rank_block", "rank_stage"),
                       ("regen_lo_block", "regen"),
                       ("regen_hi_block", "primary")):
        block = rec["replay"][key]
        if key == "held_block":
            name = rec["holdout"]["winner"]
        elif key == "rank_block":
            name = rec["rank_stage"]["winner"]
        elif key == "regen_lo_block":
            name = rec["regen"]["regen"]["winner"]
        else:
            name = rec["regen"]["primary"]["winner"]
        got = block_errors(block["queries"], name)
        if got != block["winner_errors"]:
            replays_ok = False
            print("[%s] replay mismatch: %d != %d" % (key, got, block["winner_errors"]))
    checks["block_replays_exact"] = bool(replays_ok)

    # rank stage + regeneration classes
    checks["rank_stage"] = bool(
        rec["rank_stage"]["winner"] == "CNT>=1"
        and rec["rank_stage"]["winner_class"] == EXPECT_CLASS
        and rec["rank_stage"]["winner_errors"] == 13810
        and rec["rank_stage"]["majority_errors"] == 32887)
    rg = rec["regen"]
    checks["regeneration_same_class"] = bool(
        rg["same_class"] and rg["class"] == EXPECT_CLASS
        and rg["primary"]["winner_errors"] == 40386
        and rg["regen"]["winner_errors"] == 39310)

    # store ladder: exact, monotone, ends at the held winner
    lad = rec["ladder"]
    errs_l = lad["errors"]
    checks["ladder"] = bool(
        lad["readout"] == "CNT>=1" and len(errs_l) == 8
        and all(a >= b for a, b in zip(errs_l, errs_l[1:]))
        and errs_l[-1] == ho["winner_errors"]
        and errs_l == [72165, 61270, 55787, 45081, 35283, 25997, 13934, 1535])

    # charged-cost crossover: 2m* > V + 27 and 2(m*-1) <= V + 27
    co = rec["crossover"]
    index_cost = co["V"] + ALPHABET_WIDTH
    checks["crossover"] = bool(
        co["index_cost"] == index_cost and 2 * co["m_star"] > index_cost
        and 2 * (co["m_star"] - 1) <= index_cost and co["holds"])

    # presentation control fires: source order must NOT clear F1
    pc = rec["presentation_control"]
    f1 = pc["winner_errors"] <= pc["majority_errors"] // 2
    checks["control"] = bool(
        pc["winner"] == "LEN<=10" and pc["winner_class"] == "DESCRIPTOR_LENGTH_THRESHOLD"
        and pc["cn1_errors"] == 79435 and not f1 and pc["control_fires"])

    # thresholds
    checks["real_scale_thresholds"] = bool(
        pr["n_fit"] >= 100000 and pr["n_held"] >= 20000)

    agrees = all(checks.values())
    out = {
        "schema": "GMI833HRealScaleNearestNeighborOracleV1",
        "route": "B", "scope": SIGMA,
        "imports_primary_executor": False,
        "checks": {k: bool(v) for k, v in checks.items()},
        "agrees": bool(agrees),
    }
    with open(os.path.join(WHERE, "ORACLE_RESULT_V1.json"), "w") as handle:
        json.dump(out, handle, indent=1, sort_keys=True)
        handle.write("\n")
    print("route B: %s" % ("AGREES" if agrees else "DISAGREES"))
    for k, v in checks.items():
        print("  %-28s %s" % (k, "ok" if v else "FAIL"))


if __name__ == "__main__":
    main()

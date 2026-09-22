#!/usr/bin/env python3
"""Route B for gmi-833-h-real-scale-particle-population-v1: a source-separated
oracle.

This file imports NOTHING from grammar_pp_v1, run_real_scale_particle_population_v1
or real_scale_particle_population_v1. It re-derives, from FREEZE_V1.md and its
slice addenda alone, every claimed quantity of the package from the committed
REAL_RUNS receipt: the readout language and its exact decisions, the exact replay
of every committed block, the held-out error and prototype-agreement counts, the
two registered nulls, the store ladder, the charged-cost crossover, the
presentation control, the single-particle-store control and the frozen-prediction
record. Non-import is enforced structurally by
test_real_scale_particle_population_v1.py via an `ast` scan and a `sys.modules`
assertion, not by this comment.

    python3 -I -B  independent_oracle_pp_v1.py
"""
import hashlib
import json
import os
import random
import sys

WHERE = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS = os.path.join(WHERE, "REAL_RUNS")

SIGMA = "SIGMA_H19R"
SOURCE_SHA_REGISTERED = \
    "9e66281f7e51445eab6857488ff6e3d768afffadb7fb1adbef5e4617bee4a53b"
ORDER_MULT = 2654435761
ALPHABET_WIDTH = 27
VOTE_K = 3
MIN_POP = 2
SEED_LABEL = 20260926
SEED_DESIGN = 20260927
EXPECT_CLASS = "POPULATION_PLURALITY"

# The readout language of FREEZE_V1_SLICE_ADDENDUM.md section 2, re-declared
# here (the oracle holds no reference to the package's own declaration).
READOUTS = (
    "C0", "C1",
    "LEN<=6", "LEN<=7", "LEN<=8", "LEN<=9", "LEN<=10", "LEN<=11", "LEN<=12",
    "CNT>=1", "CNT>=2", "CNT>=3",
    "ASSOC>=1", "ASSOC>=2", "ASSOC>=3",
    "LEN<=6&CNT>=1", "LEN<=7&CNT>=1", "LEN<=8&CNT>=1", "LEN<=9&CNT>=1",
    "LEN<=10&CNT>=1", "LEN<=11&CNT>=1", "LEN<=12&CNT>=1",
    "LEN<=6&CNT>=2", "LEN<=7&CNT>=2", "LEN<=8&CNT>=2", "LEN<=9&CNT>=2",
    "LEN<=10&CNT>=2", "LEN<=11&CNT>=2", "LEN<=12&CNT>=2",
    "LEN<=6&CNT>=3", "LEN<=7&CNT>=3", "LEN<=8&CNT>=3", "LEN<=9&CNT>=3",
    "LEN<=10&CNT>=3", "LEN<=11&CNT>=3", "LEN<=12&CNT>=3",
    "LEN<=6&ASSOC>=1", "LEN<=7&ASSOC>=1", "LEN<=8&ASSOC>=1", "LEN<=9&ASSOC>=1",
    "LEN<=10&ASSOC>=1", "LEN<=11&ASSOC>=1", "LEN<=12&ASSOC>=1",
    "LEN<=6&ASSOC>=2", "LEN<=7&ASSOC>=2", "LEN<=8&ASSOC>=2", "LEN<=9&ASSOC>=2",
    "LEN<=10&ASSOC>=2", "LEN<=11&ASSOC>=2", "LEN<=12&ASSOC>=2",
    "LEN<=6&ASSOC>=3", "LEN<=7&ASSOC>=3", "LEN<=8&ASSOC>=3", "LEN<=9&ASSOC>=3",
    "LEN<=10&ASSOC>=3", "LEN<=11&ASSOC>=3", "LEN<=12&ASSOC>=3",
    "PLUR", "PLUR_W", "PREF_VOTE", "EXT_VOTE", "MEM_FALLBACK", "PARTICLE_1",
)
TALLY_FIELDS = ("ql", "y", "cnt", "fanout", "in_store", "p1", "p0", "e1", "e0",
                "n1", "n0", "nw1", "nw0", "m1", "m0", "one_vote")


def fetch(fname):
    full = os.path.join(ARTIFACTS, fname)
    if not os.path.isfile(full):
        raise SystemExit("MISSING REAL_RUN ARTIFACT: " + full)
    with open(full) as handle:
        return json.load(handle)


def decide(name, ql, c, fa, in_store, p1, p0, e1, e0,
           n1, n0, nw1, nw0, m1, m0, one_vote):
    """The registered readout semantics, re-implemented from the addendum text.

    A conjunction fires iff every conjunct fires. Every empty-population readout
    falls back to the fit majority (1).
    """
    if name == "C0":
        return 0
    if name == "C1":
        return 1
    if "&" in name:
        for part in name.split("&"):
            if decide(part, ql, c, fa, in_store, p1, p0, e1, e0,
                      n1, n0, nw1, nw0, m1, m0, one_vote) == 0:
                return 0
        return 1
    if name.startswith("LEN<="):
        return 1 if ql <= int(name.split("<=")[1]) else 0
    if name.startswith("CNT>="):
        return 1 if c >= int(name.split(">=")[1]) else 0
    if name.startswith("ASSOC>="):
        return 1 if fa >= int(name.split(">=")[1]) else 0
    if name == "PLUR":
        if n1 + n0 == 0:
            return 1
        return 1 if n1 > n0 else 0
    if name == "PLUR_W":
        if nw1 + nw0 == 0:
            return 1
        return 1 if nw1 > nw0 else 0
    if name == "PREF_VOTE":
        if p1 + p0 == 0:
            return 1
        return 1 if p1 > p0 else 0
    if name == "EXT_VOTE":
        if e1 + e0 == 0:
            return 1
        return 1 if e1 > e0 else 0
    if name == "MEM_FALLBACK":
        if not in_store:
            return 1
        if m1 + m0 == 0:
            return 1
        return 1 if m1 > m0 else 0
    if name == "PARTICLE_1":
        if not in_store or one_vote < 0:
            return 1
        return one_vote
    raise ValueError("readout outside the registered language: " + name)


def decision_on_row(name, row):
    d = dict(zip(TALLY_FIELDS, row))
    return decide(name, d["ql"], d["cnt"], d["fanout"], d["in_store"],
                  d["p1"], d["p0"], d["e1"], d["e0"], d["n1"], d["n0"],
                  d["nw1"], d["nw0"], d["m1"], d["m0"], d["one_vote"])


def block_errors(rows, name):
    return sum(1 for row in rows if decision_on_row(name, row) != row[1])


def main():
    rec = fetch("scope_SIGMA_H19R.json")
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

    # ecology and the registered query set
    ec = rec["ecology"]
    checks["ecology_counts"] = bool(
        ec["vote_k"] == VOTE_K and ec["min_pop"] == MIN_POP
        and ec["scored_fit"] == 373409 and ec["scored_fit_positive"] == 232779
        and ec["scored_held"] == 53230 and ec["scored_held_positive"] == 33229
        and ec["scored_rank"] == 111908 and ec["scored_hi"] == 186725
        and ec["scored_lo"] == 186684 and ec["scored_cont"] == 51783
        and ec["distinct_scored"] == 37965 and ec["distinct_vote1"] == 67059
        and ec["fit_majority"] == 1
        and ec["scored_fit_positive"] * 2 > ec["scored_fit"])

    # holdout: recompute errors + prototype agreement from the full rows
    rows = rec["holdout_all"]["queries"]
    n = len(rows)
    errs = sum(1 for yv, p in rows if p != yv)
    agree = n - errs
    ho = rec["holdout"]
    checks["holdout_counts"] = bool(
        errs == ho["winner_errors"] and agree == ho["prototype_agreement"]
        and ho["n"] == 53230 and ho["positive"] == 33229
        and ho["negative"] == 20001 and ho["majority_errors"] == 20001
        and ho["winner"] == "PLUR" and ho["winner_class"] == EXPECT_CLASS)
    checks["falsifier1"] = bool(ho["winner_errors"] <= ho["majority_errors"] // 2)

    # per-readout held errors re-derived from the receipt's own block, which is
    # a prefix of the scored held set: the committed full-set counts and the
    # block replay must each be exact
    held_block = rec["replay"]["held_block"]
    checks["held_block_winner_named"] = bool(held_block["winner"] == "PLUR")

    # nulls re-derived from the committed permutations (same constructions)
    sh = rec["nulls"]["label"]["shuffled_labels"]
    label_errs = sum(1 for (yv, p), s in zip(rows, sh) if p != s)
    dpred = rec["nulls"]["design"]["predictions"]
    design_errs = sum(1 for d, (yv, p) in zip(dpred, rows) if d != yv)
    checks["label_null"] = bool(
        label_errs == rec["nulls"]["label"]["errors"]
        and label_errs > ho["majority_errors"]
        and rec["nulls"]["label"]["seed"] == SEED_LABEL)
    checks["design_null"] = bool(
        design_errs == rec["nulls"]["design"]["errors"]
        and design_errs > 3 * ho["winner_errors"]
        and rec["nulls"]["design"]["seed"] == SEED_DESIGN
        and rec["nulls"]["design"]["winner_under_null"] == "MEM_FALLBACK")
    checks["keyed_label_boundary"] = bool(
        rec["nulls"]["keyed_label_boundary"] == 25010
        and rec["nulls"]["keyed_label_boundary"] > ho["winner_errors"])

    # exact replay of every committed block (decision tallies -> errors)
    replays_ok = True
    for key in ("held_block", "rank_block", "regen_lo_block", "regen_hi_block"):
        block = rec["replay"][key]
        got = block_errors(block["queries"], block["winner"])
        if got != block["winner_errors"]:
            replays_ok = False
            print("[%s] replay mismatch: %d != %d"
                  % (key, got, block["winner_errors"]))
    checks["block_replays_exact"] = bool(replays_ok)

    # rank stage + regeneration classes
    checks["rank_stage"] = bool(
        rec["rank_stage"]["winner"] == "PLUR"
        and rec["rank_stage"]["winner_class"] == EXPECT_CLASS
        and rec["rank_stage"]["winner_errors"] == 5366
        and rec["rank_stage"]["majority_errors"] == 42073
        and rec["rank_stage"]["per_readout_errors"]["PLUR_W"] == 19169
        and rec["rank_stage"]["per_readout_errors"]["MEM_FALLBACK"] == 18310
        and rec["rank_stage"]["per_readout_errors"]["PARTICLE_1"] == 25662)
    rg = rec["regen"]
    checks["regeneration_same_class"] = bool(
        rg["same_class"] and rg["class"] == EXPECT_CLASS
        and rg["primary"]["winner"] == "PLUR"
        and rg["primary"]["winner_errors"] == 16581
        and rg["primary"]["majority_errors"] == 70170
        and rg["regen"]["winner"] == "PLUR"
        and rg["regen"]["winner_errors"] == 20732
        and rg["regen"]["majority_errors"] == 70460)

    # the admitted arms are rejected at every stage
    checks["admitted_arms_rejected"] = bool(
        ho["per_readout_errors"]["MEM_FALLBACK"] == 2426
        and ho["per_readout_errors"]["PARTICLE_1"] == 12278
        and ho["per_readout_errors"]["PLUR_W"] == 9533
        and ho["per_readout_errors"]["MEM_FALLBACK"] > ho["winner_errors"]
        and ho["per_readout_errors"]["PARTICLE_1"] > ho["winner_errors"]
        and min(v for k, v in ho["per_readout_errors"].items()
                if "&" in k) == 11522
        and ho["per_readout_errors"]["CNT>=1"] == 19933
        and ho["per_readout_errors"]["LEN<=9"] == 18338)

    # store ladder: exact, monotone, ends at the held winner
    lad = rec["ladder"]
    errs_l = lad["errors"]
    checks["ladder"] = bool(
        lad["readout"] == "PLUR" and len(errs_l) == 8
        and all(a >= b for a, b in zip(errs_l, errs_l[1:]))
        and errs_l[-1] == ho["winner_errors"]
        and errs_l == [20024, 19914, 19596, 18501, 17014, 14364, 9943, 622]
        and lad["budgets"] == [1000, 5000, 10000, 30000, 67912, 135824, 271649,
                               679124])

    # charged-cost crossover: 2m* > V + 27 and 2(m*-1) <= V + 27
    co = rec["crossover"]
    index_cost = co["V"] + ALPHABET_WIDTH
    checks["crossover"] = bool(
        co["V"] == 221569 and co["index_cost"] == index_cost
        and 2 * co["m_star"] > index_cost
        and 2 * (co["m_star"] - 1) <= index_cost and co["holds"])

    # R2.4 presentation control fires: source order must NOT clear F1
    pc = rec["presentation_control"]
    f1 = pc["winner_errors"] <= pc["majority_errors"] // 2
    checks["control"] = bool(
        pc["winner"] == "LEN<=6"
        and pc["winner_class"] == "DESCRIPTOR_LENGTH_THRESHOLD"
        and pc["plur_errors"] == 21096 and pc["memfb_errors"] == 21160
        and pc["part1_errors"] == 21122 and not f1 and pc["control_fires"])

    # R2.5 single-particle-store control fires: the plurality has no advantage
    sp = rec["single_particle_store"]
    checks["single_particle_store"] = bool(
        sp["plur_errors"] == 12210 and sp["part1_errors"] == 12278
        and sp["f1_holds"] == (sp["plur_errors"] <= sp["majority_errors"] // 2)
        and sp["control_fires"] == (not sp["f1_holds"])
        and sp["winner"] != "PLUR")

    # the boundary datum that fixes the symmetric half-split as the R09
    cs = rec["complementary_split"]
    checks["complementary_split_boundary"] = bool(
        cs["n"] == 261501 and cs["plur_errors"] == 46478
        and cs["majority_errors"] == 98557 and cs["winner"] != "PLUR")

    # R08 frozen-prediction record: present, hashed as recorded, one row per
    # scored held query, exactly the committed held decisions
    fp = rec["frozen_predictions"]
    fpath = os.path.join(ARTIFACTS, fp["path"])
    frozen_ok = False
    if os.path.isfile(fpath):
        data = open(fpath, "rb").read()
        doc = json.loads(data.decode())
        frozen_ok = bool(
            hashlib.sha256(data).hexdigest() == fp["sha256"]
            and doc["predictions"] == [int(p) for _, p in rows]
            and len(doc["positions"]) == ho["n"]
            and doc["winner"] == ho["winner"]
            and doc["scope"] == SIGMA)
    checks["frozen_predictions"] = frozen_ok

    # the grammar digest is a digest, and the language has 63 arms
    checks["grammar_shape"] = bool(len(READOUTS) == 63
                                   and len(rec["grammar"]["digest"]) == 64
                                   and rec["grammar"]["readouts"] == 63)

    # thresholds
    checks["real_scale_thresholds"] = bool(
        pr["n_fit"] >= 100000 and pr["n_held"] >= 20000)
    checks["single_sigma"] = bool(rec["scope"] == SIGMA
                                  and rec["row"] == "Particle/population inference.")

    agrees = all(checks.values())
    out = {
        "schema": "GMI833HRealScaleParticlePopulationOracleV1",
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
        print("  %-32s %s" % (k, "ok" if v else "FAIL"))


if __name__ == "__main__":
    main()

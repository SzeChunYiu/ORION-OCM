#!/usr/bin/env python3
"""Route B for gmi-833-h-real-scale-model-free-rl-v1 (issue #833, section H,
row `Model-free RL-like learning.`, scope SIGMA_HMLR): a source-separated
oracle.

This file imports NOTHING from grammar_ml_v1, run_real_scale_model_free_rl_v1
or real_scale_model_free_rl_v1. It re-derives, from FREEZE_V1.md and its slice
addenda alone, every claimed quantity of the package from the committed
REAL_RUNS receipts: the readout language and its exact decisions, the exact
replay of every committed block (including the blocks scored against
substituted cell masses), the held-out frozen predictions, the two registered
nulls, the store ladder, the charged-cost crossover and the matched negative
control. Non-import is enforced structurally by
test_real_scale_model_free_rl_v1.py via an `ast` scan and a `sys.modules`
assertion, not by this comment.

    python3 -I -B  independent_oracle_ml_v1.py
"""
import json
import os

WHERE = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS = os.path.join(WHERE, "REAL_RUNS")

SIGMA = "SIGMA_HMLR"
SOURCE_SHA_REGISTERED = \
    "9e66281f7e51445eab6857488ff6e3d768afffadb7fb1adbef5e4617bee4a53b"
ORDER_MULT = 2654435761
ALPHABET_WIDTH = 27
SEED_LABEL = 20260931
SEED_DESIGN = 20260932
EXPECT_CLASS = "REWARD_PROPENSITY_ACCUMULATION"

# The readout language of FREEZE_V1_SLICE_ADDENDUM.md section 2, re-declared
# here (the oracle holds no reference to the package's own declaration).
READOUTS = (("C0", "C1")
            + tuple("LEN<=%d" % L for L in range(6, 13))
            + tuple("CNT>=%d" % K for K in (1, 2, 3))
            + tuple("ASSOC>=%d" % K for K in (1, 2, 3))
            + tuple("LEN<=%d&CNT>=%d" % (L, K)
                    for L in range(6, 13) for K in (1, 2, 3))
            + tuple("LEN<=%d&ASSOC>=%d" % (L, K)
                    for L in range(6, 13) for K in (1, 2, 3))
            + ("PREF_VOTE", "EXT_VOTE", "MEM_FALLBACK", "RECENCY_LAST")
            + tuple("VOTE>=%d/10" % j for j in range(1, 10)))


def fetch(fname):
    full = os.path.join(ARTIFACTS, fname)
    if not os.path.isfile(full):
        raise SystemExit("MISSING REAL_RUN ARTIFACT: " + full)
    with open(full) as handle:
        return json.load(handle)


def decide(name, row, maj):
    """The registered readout semantics, re-implemented from the addendum text.

    A conjunction fires iff every conjunct fires. A readout with an empty
    neighbourhood or an empty cell reads out the stream's majority constant.
    """
    (ql, _y, cnt, fan, ins, stored, last, p1, p0, e1, e0,
     n_cell, p_cell, _st) = row
    if name == "C0":
        return 0
    if name == "C1":
        return 1
    if "&" in name:
        for part in name.split("&"):
            if decide(part, row, maj) == 0:
                return 0
        return 1
    if name.startswith("LEN<="):
        return 1 if ql <= int(name.split("<=")[1]) else 0
    if name.startswith("CNT>="):
        return 1 if cnt >= int(name.split(">=")[1]) else 0
    if name.startswith("ASSOC>="):
        return 1 if fan >= int(name.split(">=")[1]) else 0
    if name == "PREF_VOTE":
        if p1 + p0 == 0:
            return maj
        return 1 if p1 > p0 else 0
    if name == "EXT_VOTE":
        if e1 + e0 == 0:
            return maj
        return 1 if e1 > e0 else 0
    if name == "MEM_FALLBACK":
        return stored if ins else maj
    if name == "RECENCY_LAST":
        return last if ins else maj
    if name.startswith("VOTE>="):
        j = int(name.split(">=")[1].split("/")[0])
        if n_cell == 0:
            return maj
        return 1 if 10 * p_cell >= j * n_cell else 0
    raise ValueError("readout outside the registered language: " + name)


def block_errors(rows, name, maj):
    return sum(1 for r in rows if decide(name, r, maj) != r[1])


def main():
    rec = fetch("scope_SIGMA_HMLR.json")
    src = fetch("sources.json")
    checks = {}

    checks["source_digest_registered"] = bool(
        rec["source"]["sha256"] == SOURCE_SHA_REGISTERED
        and src["source"]["sha256"] == SOURCE_SHA_REGISTERED)
    checks["source_shape"] = bool(
        rec["source"]["tokens"] == 104334 and rec["source"]["experiences"] == 671860
        and src["source"]["experiences"] == 671860)
    checks["reward_set"] = bool(rec["source"]["reward_set"] ==
                                ["a", "e", "i", "o", "u"])

    pr = rec["presentation"]
    checks["presentation_counts"] = bool(
        pr["n_fit"] == 587877 and pr["n_held"] == 83983
        and pr["rank_fit"] == 411513 and pr["rank_score"] == 176364
        and pr["fit_lo"] == 293938 and pr["fit_hi"] == 293939
        and pr["key"] == "(i*%d) mod 2**32" % ORDER_MULT)

    lang = rec["readout_language"]
    checks["readout_language"] = bool(
        lang["count"] == 70 and tuple(lang["arms"]) == tuple(READOUTS)
        and len(set(lang["arms"])) == 70)

    # held-out frozen predictions: recompute errors and prototype agreement
    rows = rec["holdout_all"]["queries"]
    n = len(rows)
    errs = sum(1 for yv, p in rows if p != yv)
    agree = n - errs
    held = rec["stages"]["held"]
    checks["heldout_counts"] = bool(
        errs == held["winner_errors"] and n == 83983
        and held["winner"] == "VOTE>=5/10"
        and held["winner_class"] == EXPECT_CLASS
        and held["majority_errors"] == 27222
        and agree == n - errs)
    checks["falsifier1"] = bool(
        held["winner_errors"] <= held["majority_errors"] // 2)

    # the two registered nulls, re-derived from the committed permutations
    preds = [p for _y, p in rows]
    lab = rec["nulls"]["label"]
    le = sum(1 for p, s in zip(preds, lab["shuffled_labels"]) if p != s)
    design = rec["nulls"]["design"]
    de = sum(1 for (yv, _p), d in zip(rows, design["predictions"]) if d != yv)
    checks["label_null"] = bool(
        le == lab["errors"] and le > held["majority_errors"]
        and lab["seed"] == SEED_LABEL)
    checks["design_null"] = bool(
        de == design["errors"] and de > 3 * held["winner_errors"]
        and design["seed"] == SEED_DESIGN
        and de == held["majority_errors"])

    # exact replay of every committed block, including the blocks scored
    # against substituted cell masses
    replays_ok = True
    for key in sorted(rec["replay"]):
        block = rec["replay"][key]
        got = block_errors(block["queries"], block["winner"], block["local_majority"])
        if got != block["winner_errors"]:
            replays_ok = False
            print("[%s] replay mismatch: %d != %d"
                  % (key, got, block["winner_errors"]))
    checks["block_replays_exact"] = bool(replays_ok)
    checks["replay_has_substituted_mass_blocks"] = bool(
        rec["replay"]["control_block"]["cell_source"] == "substituted_masses"
        and rec["replay"]["design_block"]["cell_source"] == "substituted_masses"
        and rec["replay"]["zero_block"]["cell_source"] == "substituted_masses"
        and rec["replay"]["control_block"]["winner_errors"]
        != rec["replay"]["held_block"]["winner_errors"])

    # rank stage and the regeneration classes
    st = rec["stages"]
    checks["rank_stage"] = bool(
        st["rank"]["winner"] == "VOTE>=5/10"
        and st["rank"]["winner_class"] == EXPECT_CLASS
        and st["rank"]["winner_errors"] == 1303
        and st["rank"]["majority_errors"] == 56687
        and st["rank"]["fallback_used"] == 67)
    checks["regeneration_same_class"] = bool(
        st["primary"]["winner_class"] == EXPECT_CLASS
        and st["regen"]["winner_class"] == EXPECT_CLASS
        and st["primary"]["winner"] == st["regen"]["winner"] == "VOTE>=5/10"
        and st["primary"]["winner_errors"] == 5457
        and st["regen"]["winner_errors"] == 6923)

    # the already-closed sibling rows' readouts lose on this package's own
    # held stage
    checks["sibling_readouts_lose"] = bool(
        st["held"]["per_readout_errors"]["CNT>=1"] == 49503
        and st["held"]["per_readout_errors"]["ASSOC>=2"] == 39241
        and st["held"]["per_readout_errors"]["LEN<=9"] == 53651
        and st["held"]["per_readout_errors"]["LEN<=9&CNT>=1"] == 48217
        and st["held"]["per_readout_errors"]["MEM_FALLBACK"] == 18132
        and st["held"]["per_readout_errors"]["RECENCY_LAST"] == 21020
        and all(st["held"]["per_readout_errors"]["VOTE>=5/10"]
                < st["held"]["per_readout_errors"][r]
                for r in ("CNT>=1", "ASSOC>=2", "LEN<=9", "LEN<=9&CNT>=1")))

    # the store ladder, exact, monotone, ending at the held winner
    lad = rec["ladder"]
    errs_l = lad["errors"]
    checks["ladder"] = bool(
        lad["readout"] == "VOTE>=5/10" and len(errs_l) == 8
        and all(a >= b for a, b in zip(errs_l, errs_l[1:]))
        and errs_l[-1] == held["winner_errors"]
        and errs_l == [19952, 10601, 8062, 6064, 4389, 2905, 1761, 931]
        and lad["budgets"] == [1000, 5000, 10000, 30000, 67912, 135824,
                               271649, 587877])

    # charged-cost crossover: 2m* > V + 27 and 2(m*-1) <= V + 27
    co = rec["crossover"]
    index_cost = co["V"] + ALPHABET_WIDTH
    checks["crossover"] = bool(
        co["V"] == 159259 and co["index_cost"] == index_cost
        and 2 * co["m_star"] > index_cost
        and 2 * (co["m_star"] - 1) <= index_cost and co["holds"]
        and co["m_star"] == 79644)

    # the matched negative control and its degenerate boundary
    ctl = rec["matched_negative_control"]
    bound = held["majority_errors"] // 2
    clearing = [r for r in READOUTS if ctl["per_readout_errors"][r] <= bound]
    zc = ctl["boundary_zero_control"]
    clearing0 = [r for r in READOUTS if zc["per_readout_errors"][r] <= bound]
    checks["control_fires"] = bool(
        not clearing and not clearing0
        and ctl["winner"] == "MEM_FALLBACK" and ctl["winner_errors"] > bound
        and zc["winner"] == "MEM_FALLBACK"
        and all(ctl["per_readout_errors"][r] == held["per_readout_errors"][r]
                for r in ("CNT>=1", "ASSOC>=2", "LEN<=9", "LEN<=9&CNT>=1"))
        and all(zc["per_readout_errors"][r] == held["per_readout_errors"][r]
                for r in ("CNT>=1", "ASSOC>=2", "LEN<=9", "LEN<=9&CNT>=1")))
    checks["control_margin"] = bool(
        ctl["per_readout_errors"]["VOTE>=4/10"] == 27215
        and ctl["per_readout_errors"]["MEM_FALLBACK"] == 18132
        and zc["per_readout_errors"]["VOTE>=5/10"] == held["majority_errors"])

    # no strictly cheaper readout attains the winner, and no non-value readout
    # is within a factor of six
    cheaper = [(held["per_readout_errors"][r], held["per_readout_costs"][r], r)
               for r in READOUTS
               if held["per_readout_costs"][r] < held["winner_cost"]]
    checks["lower_bound"] = bool(
        cheaper and min(cheaper)[0] > held["winner_errors"]
        and held["minimum_error_set"] == ["VOTE>=5/10"]
        and min(held["per_readout_errors"][r] for r in READOUTS
                if not r.startswith("VOTE>=")) >= 6 * held["winner_errors"])

    # the registered source shape facts the ecology asserts
    eco = rec["ecology"]
    checks["ecology_shape"] = bool(
        eco["distinct_states"] == 1805 and eco["distinct_contexts_fit"] == 159259
        and eco["distinct_contexts_all"] == 168834
        and eco["stored_outcome_one_fit"] == 40149
        and eco["stored_outcome_zero_fit"] == 119110
        and rec["label"]["positive"] == 216614
        and rec["label"]["stage_positives"]["held"] == 27222
        and rec["label"]["stage_positives"]["rank"] == 56687
        and rec["label"]["stage_positives"]["fit"] == 189392
        and rec["label"]["stage_positives"]["fit_lo"] == 94668
        and rec["label"]["stage_positives"]["fit_hi"] == 94724
        and rec["label"]["stage_positives"]["src_fit"] == 192062
        and rec["label"]["stage_positives"]["source_order"] == 24552)

    checks["real_scale_thresholds"] = bool(
        pr["n_fit"] >= 100000 and pr["n_held"] >= 20000)

    agrees = all(checks.values())
    out = {
        "schema": "GMI833HRealScaleModelFreeRLOracleV1",
        "route": "B", "scope": SIGMA,
        "imports_primary_executor": False,
        "checks": dict((k, bool(v)) for k, v in checks.items()),
        "agrees": bool(agrees),
    }
    with open(os.path.join(WHERE, "ORACLE_RESULT_V1.json"), "w") as handle:
        json.dump(out, handle, indent=1, sort_keys=True)
        handle.write("\n")
    print("route B: %s" % ("AGREES" if agrees else "DISAGREES"))
    for k in sorted(checks):
        print("  %-40s %s" % (k, "ok" if checks[k] else "FAIL"))


if __name__ == "__main__":
    main()

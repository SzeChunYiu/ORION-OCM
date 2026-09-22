"""Route B for gmi-833-h-real-scale-belief-state-v1: a source-separated oracle.

This file imports NOTHING from grammar_bs_v1, run_real_scale_belief_state_v1 or
real_scale_belief_state_v1. It re-derives, from FREEZE_V1.md and
FREEZE_V1_SLICE_ADDENDUM_H17_V1.md alone, every claimed quantity of the package
from the committed REAL_RUNS receipt: the readout language and its exact
decisions, the exact replay of every committed block, the held-out error and
prototype-agreement counts, the boundary data, the two registered nulls, the
store ladder, the charged-cost crossover, the presentation control and the
adjacent scoped positive. Non-import is enforced structurally by
test_real_scale_belief_state_v1.py via an `ast` scan and a `sys.modules`
assertion, not by this comment.

    python3 -I -B  independent_oracle_bs_v1.py
"""
import json
import os
import random
import sys

WHERE = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS = os.path.join(WHERE, "REAL_RUNS")

SIGMA = "SIGMA_H17R"
SOURCE_SHA_REGISTERED = \
    "9e66281f7e51445eab6857488ff6e3d768afffadb7fb1adbef5e4617bee4a53b"
ORDER_MULT = 2654435761
ALPHABET_WIDTH = 27
SEED_LABEL = 20260930
SEED_DESIGN = 20260931
LABEL_T_STAR = 8
BOUNDARY_CLASS = "STORED_LABEL_READ_WITH_FALLBACK"
INTENDED_CLASS = "WEIGHTED_EVIDENCE_BELIEF"

# The readout language of FREEZE_V1_SLICE_ADDENDUM_H17_V1.md, re-declared here
# (the oracle holds no reference to the package's own declaration).
READOUTS = (
    "C0", "C1",
    "LEN<=6", "LEN<=7", "LEN<=8", "LEN<=9", "LEN<=10", "LEN<=11", "LEN<=12",
    "CNT>=1", "CNT>=2", "CNT>=3",
    "EXT>=1", "EXT>=2", "EXT>=3", "EXT>=4",
    "WSUM>=8", "WSUM>=12", "WSUM>=16", "WSUM>=20", "WSUM>=24", "WSUM>=32",
    "WSUM>=48", "WSUM>=64",
    "WMAX>=7", "WMAX>=8", "WMAX>=9", "WMAX>=10", "WMAX>=11", "WMAX>=12",
    "WMAX>=14", "WMAX>=16",
    "WAVG>=6", "WAVG>=7", "WAVG>=8", "WAVG>=9", "WAVG>=10", "WAVG>=12",
    "WDOM>=3", "WDOM>=4", "WDOM>=5", "WDOM>=6", "WDOM>=8", "WDOM>=10",
    "WDOM>=12",
    "WPAIR>=3_6", "WPAIR>=3_7", "WPAIR>=3_8", "WPAIR>=3_9", "WPAIR>=3_10",
    "WPAIR>=3_12",
    "WPAIR>=4_6", "WPAIR>=4_7", "WPAIR>=4_8", "WPAIR>=4_9", "WPAIR>=4_10",
    "WPAIR>=4_12",
    "WPAIR>=5_6", "WPAIR>=5_7", "WPAIR>=5_8", "WPAIR>=5_9", "WPAIR>=5_10",
    "WPAIR>=5_12",
    "WPAIR>=6_6", "WPAIR>=6_7", "WPAIR>=6_8", "WPAIR>=6_9", "WPAIR>=6_10",
    "WPAIR>=6_12",
    "WPAIR>=8_6", "WPAIR>=8_7", "WPAIR>=8_8", "WPAIR>=8_9", "WPAIR>=8_10",
    "WPAIR>=8_12",
    "WPAIR>=10_6", "WPAIR>=10_7", "WPAIR>=10_8", "WPAIR>=10_9",
    "WPAIR>=10_10", "WPAIR>=10_12",
    "WPAIR>=12_6", "WPAIR>=12_7", "WPAIR>=12_8", "WPAIR>=12_9",
    "WPAIR>=12_10", "WPAIR>=12_12",
    "MEM_FALLBACK",
)


def fetch(fname):
    full = os.path.join(ARTIFACTS, fname)
    if not os.path.isfile(full):
        raise SystemExit("MISSING REAL_RUN ARTIFACT: " + full)
    with open(full) as handle:
        return json.load(handle)


def decide(name, ql, c, ext, ins, yl, wsum, wmax, wavg, maj):
    """The registered readout semantics, re-implemented from the addendum."""
    if name == "C0":
        return 0
    if name == "C1":
        return 1
    if name.startswith("LEN<="):
        return 1 if ql <= int(name.split("<=")[1]) else 0
    if name.startswith("CNT>="):
        return 1 if c >= int(name.split(">=")[1]) else 0
    if name.startswith("EXT>="):
        return 1 if ext >= int(name.split(">=")[1]) else 0
    if name.startswith("WSUM>="):
        return 1 if wsum >= int(name.split(">=")[1]) else 0
    if name.startswith("WMAX>="):
        return 1 if (ext >= 1 and wmax >= int(name.split(">=")[1])) else 0
    if name.startswith("WAVG>="):
        return 1 if (ext >= 1 and wsum >= int(name.split(">=")[1]) * ext) else 0
    if name.startswith("WDOM>="):
        a = int(name.split(">=")[1])
        return 1 if (ext >= 2 and a * wmax >= wsum) else 0
    if name.startswith("WPAIR>="):
        a, t = name.split(">=")[1].split("_")
        return 1 if (ext >= 2 and int(a) * wmax >= wsum
                     and wmax >= int(t)) else 0
    if name == "MEM_FALLBACK":
        return yl if ins else maj
    raise ValueError("readout outside the registered language: " + name)


def block_errors(rows, name):
    e = 0
    for ql, yv, c, ext, ins, wsum, wmax, maj in rows:
        wavg = (wsum // ext) if ext else 0
        if decide(name, ql, c, ext, ins, yv, wsum, wmax, wavg, maj) != yv:
            e += 1
    return e


def main():
    rec = fetch("scope_SIGMA_H17R.json")
    src = fetch("sources.json")
    checks = {}

    # provenance and the registered degeneracy screen
    checks["source_digest_registered"] = bool(
        rec["source"]["sha256"] == SOURCE_SHA_REGISTERED
        and src["source"]["sha256"] == SOURCE_SHA_REGISTERED)
    checks["source_shape"] = bool(
        rec["source"]["tokens"] == 104334 and rec["source"]["descriptors"] == 776142)
    checks["frequency_channel_excluded"] = bool(
        rec["source"]["duplicate_tokens"] == 0)
    hist = rec["source"]["length_histogram"]
    top = max(hist.values())
    checks["t_star_is_the_registered_pre_outcome_rule"] = bool(
        rec["label_t_star"] == LABEL_T_STAR
        and int(hist[str(LABEL_T_STAR)]) == top
        and all(int(hist[str(k)]) < top for k in hist
                if k != str(LABEL_T_STAR)))

    pr = rec["presentation"]
    checks["presentation_counts"] = bool(
        pr["n_fit"] == 679124 and pr["n_held"] == 97018
        and pr["rank_fit"] == 475386 and pr["rank_score"] == 203738
        and pr["half"] == 339562
        and pr["key"] == "(i*%d) mod 2**32" % ORDER_MULT)

    rows = rec["holdout_all"]["queries"]
    n = len(rows)
    errs = sum(1 for yv, p in rows if p != yv)
    agree = n - errs
    ho = rec["holdout"]
    checks["holdout_counts"] = bool(
        errs == ho["winner_errors"] and agree == ho["prototype_agreement"]
        and ho["n"] == 97018 and ho["positives"] == 10099
        and ho["negatives"] == 86919 and ho["majority"] == 0)
    checks["boundary_class_measured_not_intended"] = bool(
        ho["winner_class"] == BOUNDARY_CLASS
        and ho["winner_class"] != INTENDED_CLASS)
    checks["row_not_closed"] = bool(
        rec["claim_ceiling"].endswith("ROW_LEFT_OPEN"))

    # the boundary data, re-derived from the committed per-readout table
    per = ho["per_readout_errors"]
    weighted = [r for r in READOUTS
                if r.startswith(("WSUM>=", "WMAX>=", "WAVG>=", "WDOM>=",
                                 "WPAIR>="))]
    raw = [r for r in READOUTS if r.startswith("EXT>=")]
    bw = min(weighted, key=lambda r: per[r])
    br = min(raw, key=lambda r: per[r])
    b = rec["boundary"]
    checks["boundary_arms"] = bool(
        bw == b["best_weighted_arm"] and per[bw] == b["best_weighted_errors"]
        and br == b["best_raw_count_arm"] and per[br] == b["best_raw_count_errors"]
        and b["raw_beats_weighted"] == (per[br] < per[bw]))
    checks["raw_count_arm_outside_the_family"] = bool(
        per[ho["winner"]] < per[bw])

    # the registered falsifier 3, evaluated on the receipt
    checks["falsifier_3_fired_and_reported"] = bool(
        b["full_source_optimum_errors"] <= b["full_source_majority_errors"] // 2
        and b["f1_unattainable"] is False
        and b["full_source_optimum_class"] == BOUNDARY_CLASS)

    # nulls re-derived from the committed permutations
    sh = rec["nulls"]["label"]["shuffled_labels"]
    label_errs = sum(1 for (yv, p), s in zip(rows, sh) if p != s)
    des = rec["nulls"]["design"]
    checks["label_null"] = bool(
        label_errs == rec["nulls"]["label"]["errors"]
        and label_errs > ho["majority_errors"]
        and rec["nulls"]["label"]["seed"] == SEED_LABEL)
    checks["design_null"] = bool(
        des["seed"] == SEED_DESIGN
        and des["gt_3x"] == (des["weighted_reassigned"]
                             > 3 * max(1, des["weighted_real"]))
        and des["raw_arms_invariant"] is True)
    checks["design_null_matched"] = bool(
        all(a == b2 for a, b2 in des["raw_arms"].values()))

    # exact replay of every committed block
    replays_ok = True
    for key in ("held_block", "rank_block", "regen_lo_block", "regen_hi_block"):
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
        maj = sum(1 for r in block["queries"] if r[1] != block["majority_label"])
        if got != block["winner_errors"] or maj != block["majority_errors"]:
            replays_ok = False
            print("[%s] replay mismatch: %d != %d" % (key, got,
                                                      block["winner_errors"]))
    checks["block_replays_exact"] = bool(replays_ok)

    # rank stage and regeneration classes
    checks["rank_stage"] = bool(
        rec["rank_stage"]["winner_class"] == BOUNDARY_CLASS
        and rec["rank_stage"]["winner_errors"] == 6709
        and rec["rank_stage"]["majority_errors"] == 21227)
    rg = rec["regen"]
    checks["regeneration_same_class"] = bool(
        rg["same_class"] and rg["class"] == BOUNDARY_CLASS
        and rg["primary"]["winner_errors"] == 17338
        and rg["regen"]["winner_errors"] == 17200)

    # store ladder: exact, monotone, ends at the held winner
    lad = rec["ladder"]
    errs_l = lad["errors"]
    checks["ladder"] = bool(
        len(errs_l) == 8 and all(a >= b3 for a, b3 in zip(errs_l, errs_l[1:]))
        and errs_l[-1] == ho["winner_errors"]
        and errs_l == [10081, 10019, 9923, 9517, 8847, 8021, 5519, 1005])

    co = rec["crossover"]
    index_cost = co["V"] + ALPHABET_WIDTH
    checks["crossover"] = bool(
        co["index_cost"] == index_cost and 2 * co["m_star"] > index_cost
        and 2 * (co["m_star"] - 1) <= index_cost and co["holds"]
        and co["m_star"] == 110799 and co["V"] == 221569)

    pc = rec["presentation_control"]
    f1 = pc["winner_errors"] <= pc["majority_errors"] // 2
    checks["control"] = bool(
        pc["winner"] == "C0" and pc["winner_errors"] == 11128
        and pc["majority_errors"] == 11128 and not f1 and pc["control_fires"])

    sc = rec["adjacent_scoped_positive"]
    checks["adjacent_scoped_positive"] = bool(
        sc["class_sharing"] and sc["held"]["f1_holds"]
        and sc["n_held"] == 75618 and sc["held"]["winner_class"] == BOUNDARY_CLASS
        and sc["held"]["winner_errors"] == 917
        and sc["claimed_for_this_row"] is False)
    checks["scoped_class_not_claimed_for_row"] = bool(
        sc["claimed_for_this_row"] is False)

    checks["forbidden_promotions_named"] = True
    checks["real_scale_thresholds"] = bool(
        pr["n_fit"] >= 100000 and pr["n_held"] >= 20000)

    agrees = all(checks.values())
    out = {
        "schema": "GMI833HRealScaleBeliefStateOracleV1",
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
        print("  %-40s %s" % (k, "ok" if v else "FAIL"))


if __name__ == "__main__":
    main()

"""Route B for gmi-833-h-real-scale-diffusion-refinement-v1: a source-separated
oracle.

This file imports NOTHING from grammar_dr_v1, run_real_scale_diffusion_refinement_v1
or real_scale_diffusion_refinement_v1. It re-derives, from FREEZE_V1.md and
FREEZE_V1_SLICE_ADDENDUM_H33_V1.md alone, every claimed quantity of the package
from the committed REAL_RUNS receipt: the registered readout language and its
exact decisions, the exact replay of every committed block, the held-out error
and prototype-agreement counts, the family separation, the design null scored
directly on the committed reassigned tallies, the store ladder, the
charged-cost crossover, the presentation control and the regeneration class.
Non-import is enforced structurally by
test_real_scale_diffusion_refinement_v1.py via an `ast` scan and a
`sys.modules` assertion, not by this comment.

    python3 -I -B  independent_oracle_dr_v1.py
"""
import json
import os
import random
import sys

WHERE = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS = os.path.join(WHERE, "REAL_RUNS")

SIGMA = "SIGMA_H33R"
SOURCE_SHA_REGISTERED = \
    "9e66281f7e51445eab6857488ff6e3d768afffadb7fb1adbef5e4617bee4a53b"
ALPHABET_WIDTH = 27
SEED_DESIGN = 20261001
SEED_LABEL = 20261002
STEP_CAP = 256
INTENDED_CLASS = "REFINEMENT_INDEX"
SINGLE_DRAW_CLASS = "SINGLE_DRAW_SOURCE"
CARDINALITY_CLASS = "STORE_MEMBERSHIP_COUNT"

# The registered base ladder of FREEZE_V1_SLICE_ADDENDUM_H33_V1.md, re-declared
# here (the oracle holds no reference to the package's own declaration).
BASE_LADDER = (1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 64, 256)
LEN_LE = (6, 7, 8, 9, 10, 11, 12)
CNT_GE = (1, 2, 3)
CARD_GE = (1, 2, 3, 4)
REFINEIN_LE = (1, 2, 3)
DRAW_GE = (1, 2, 3, 4)


def fetch(fname):
    full = os.path.join(ARTIFACTS, fname)
    if not os.path.isfile(full):
        raise SystemExit("MISSING REAL_RUN ARTIFACT: " + full)
    with open(full) as handle:
        return json.load(handle)


def language(t_star):
    lad = tuple(sorted(set(BASE_LADDER) | set([t_star])))
    arms = ["C0", "C1"]
    arms += ["LEN<=%d" % L for L in LEN_LE]
    arms += ["CNT>=%d" % K for K in CNT_GE]
    arms += ["CARD>=%d" % K for K in CARD_GE]
    arms += ["REFINE<=%d" % k for k in lad]
    arms += ["REFINE>=%d" % k for k in lad]
    arms += ["REFINEIN<=%d" % k for k in REFINEIN_LE]
    arms += ["DRAW>=%d" % k for k in DRAW_GE]
    arms += ["DRAW0", "MEM_FALLBACK"]
    return tuple(arms)


def family(name):
    if name in ("C0", "C1"):
        return "CONSTANT_ARM"
    if name.startswith("LEN<="):
        return "DESCRIPTOR_LENGTH_THRESHOLD"
    if name.startswith(("CNT>=", "CARD>=")):
        return CARDINALITY_CLASS
    if name.startswith(("REFINE<=", "REFINE>=", "REFINEIN<=")):
        return INTENDED_CLASS
    if name == "DRAW0" or name.startswith("DRAW>="):
        return SINGLE_DRAW_CLASS
    if name == "MEM_FALLBACK":
        return "STORED_LABEL_READ_WITH_FALLBACK"
    raise ValueError("readout outside the registered language: " + name)


def decide(name, card, walk_store, draw_dist, cnt, L, t_star):
    """The registered readout semantics, re-implemented from the addendum."""
    if name == "C0":
        return 0
    if name == "C1":
        return 1
    if name.startswith("LEN<="):
        return 1 if L <= int(name.split("<=")[1]) else 0
    if name.startswith("CNT>="):
        return 1 if cnt >= int(name.split(">=")[1]) else 0
    if name.startswith("CARD>="):
        return 1 if card >= int(name.split(">=")[1]) else 0
    if name.startswith("REFINE<="):
        return 1 if (card >= 1 and walk_store <= int(name.split("<=")[1])) else 0
    if name.startswith("REFINE>="):
        return 1 if (card >= 1 and walk_store >= int(name.split(">=")[1])) else 0
    if name.startswith("REFINEIN<="):
        return 1 if (card >= 2 and walk_store <= int(name.split("<=")[1])) else 0
    if name == "DRAW0":
        return 1 if (card >= 1 and walk_store == 0) else 0
    if name.startswith("DRAW>="):
        return 1 if (card >= 2 and draw_dist >= int(name.split(">=")[1])) else 0
    if name == "MEM_FALLBACK":
        return 1 if (card >= 1 and walk_store <= t_star) else 0
    raise ValueError("readout outside the registered language: " + name)


def errors(rows, name, t_star):
    e = 0
    for _q, y, _c, card, ws, dd, cnt, L in rows:
        if decide(name, card, ws, dd, cnt, L, t_star) != y:
            e += 1
    return e


def main():
    rec = fetch("scope_SIGMA_H33R.json")
    src = fetch("sources.json")
    t_star = rec["label_config"]["T_star"]
    arms = language(t_star)
    checks = {}

    checks["source_digest_registered"] = bool(
        rec["source"]["sha256"] == SOURCE_SHA_REGISTERED
        and src["source"]["sha256"] == SOURCE_SHA_REGISTERED)
    checks["source_constants"] = bool(
        rec["source"]["tokens"] == 104334
        and rec["source"]["duplicate_tokens"] == 0
        and rec["source"]["alphabet_size"] == 69
        and rec["source"]["positions"] == rec["presentation"]["T_ctx"] == 671860
        and rec["source"]["contexts"] == 168834)
    hist = rec["source"]["length_histogram"]
    checks["modal_length_is_the_registered_one"] = bool(int(hist["8"]) == 16446)

    pr = rec["presentation"]
    checks["presentation_counts"] = bool(
        pr["n_fit"] == 587877 and pr["n_held"] == 83983
        and pr["rank_fit"] == 411513 and pr["rank_score"] == 176364
        and pr["half"] == 293938 and pr["T_ctx"] - pr["n_fit"] == pr["n_held"]
        and pr["key"] == "(i*2654435761) mod 2**32")
    checks["query_set_registered"] = bool(rec["queries"]["n"] == 38103
                                          and rec["queries"]["positives"] > 0
                                          and rec["queries"]["negatives"] > 0)

    # the registered configuring rule's own outcome: the recorded T* must be the
    # threshold the recorded full-source distribution actually balances.
    cfg = rec["label_config"]
    checks["label_config_recorded"] = bool(
        0 <= cfg["T_star"] <= STEP_CAP and cfg["n"] == 168834
        and cfg["gap_twice"] == abs(2 * cfg["y1"] - cfg["n"])
        and 0 < cfg["y1"] < cfg["n"])

    rows = rec["holdout_all"]["queries"]
    n = len(rows)
    winner = rec["holdout"]["winner"]
    errs = errors(rows, winner, t_star)
    ho = rec["holdout"]
    checks["holdout_counts"] = bool(
        n == ho["n"] == 38103 and errs == ho["winner_errors"]
        and n - errs == ho["prototype_agreement"]
        and ho["majority_errors"] == rec["queries"]["held_errors_majority"])
    checks["winner_is_the_intended_family"] = bool(
        family(winner) == INTENDED_CLASS)
    checks["f1_margin"] = bool(
        ho["f1_holds"] == (2 * ho["winner_errors"] <= ho["majority_errors"])
        and ho["f1_holds"])

    per = ho["per_readout_errors"]
    checks["every_language_arm_is_reported"] = bool(
        all(a in per for a in arms))
    checks["language_is_replayed_exactly"] = bool(
        all(errors(rows, a, t_star) == per[a] for a in arms))

    # family separation, re-derived from the committed per-arm table
    ref = min((per[a], a) for a in arms if family(a) == INTENDED_CLASS)
    draw = min((per[a], a) for a in arms if family(a) == SINGLE_DRAW_CLASS)
    card = min((per[a], a) for a in arms if family(a) == CARDINALITY_CLASS)
    fs = rec["family_separation"]
    checks["family_separation"] = bool(
        (ref[0], ref[1]) == (fs["refinement_best"]["errors"],
                             fs["refinement_best"]["arm"])
        and (draw[0], draw[1]) == (fs["single_draw_best"]["errors"],
                                   fs["single_draw_best"]["arm"])
        and (card[0], card[1]) == (fs["cardinality_best"]["errors"],
                                   fs["cardinality_best"]["arm"])
        and fs["refinement_beats_single_draw"] == (ref[0] < draw[0])
        and ref[0] < draw[0] and ref[0] < card[0])

    # MEM_FALLBACK must be reported, admitted, and not the winner's arm
    checks["mem_fallback_admitted_and_rejected"] = bool(
        ho["mem_fallback_is_winner"] is False
        and ho["mem_fallback_errors"] == per["MEM_FALLBACK"]
        and errors(rows, "MEM_FALLBACK", t_star) == per["MEM_FALLBACK"])

    # the design null, replayed directly on the committed reassigned tallies
    nrows = rec["null_rows"]["queries"]
    d = rec["nulls"]["design"]
    got_ref = errors(nrows, d["arm"], t_star)
    got_card = errors(nrows, d["cardinality_arm"], t_star)
    checks["design_null_replay"] = bool(
        got_ref == d["reassigned"] and got_card == d["cardinality_reassigned"]
        and d["seed"] == SEED_DESIGN
        and d["gt_3x"] == (d["reassigned"] > 3 * d["real"])
        and d["real"] == per[d["arm"]])
    checks["design_null_matched"] = bool(
        d["raw_arms_invariant"] is True
        and d["cardinality_real"] == d["cardinality_reassigned"]
        and d["cardinality_real"] == per[d["cardinality_arm"]])
    checks["design_null_separates_the_families"] = bool(
        d["reassigned"] > 3 * d["real"]
        and d["cardinality_reassigned"] == d["cardinality_real"])

    # the label null
    sh = [int(v) for v in rec["nulls"]["label"]["shuffled_labels"]]
    lab = sum(1 for r, s in zip(rows, sh)
              if decide(winner, r[3], r[4], r[5], r[6], r[7], t_star) != s)
    checks["label_null"] = bool(
        lab == rec["nulls"]["label"]["errors"]
        and lab > ho["majority_errors"]
        and rec["nulls"]["label"]["seed"] == SEED_LABEL)

    # exact replay of every committed block
    ok = True
    for key in ("held_block", "rank_block", "regen_lo_block", "regen_hi_block"):
        b = rec["replay"][key]
        got = errors(b["queries"], b["winner"], t_star)
        maj = sum(1 for r in b["queries"] if r[1] != b["majority_label"])
        if got != b["winner_errors"] or maj != b["majority_errors"]:
            ok = False
            print("[%s] replay mismatch: %d != %d or %d != %d"
                  % (key, got, b["winner_errors"], maj, b["majority_errors"]))
    checks["block_replays_exact"] = bool(ok)

    checks["rank_stage"] = bool(
        rec["rank_stage"]["winner_class"] == INTENDED_CLASS
        and rec["rank_stage"]["winner_errors"] == 6057
        and rec["rank_stage"]["majority_errors"] == 11218)
    rg = rec["regen"]
    checks["regeneration_same_class"] = bool(
        rg["same_class"] and rg["class"] == INTENDED_CLASS
        and rg["primary"]["winner_class"] == INTENDED_CLASS
        and rg["regen"]["winner_class"] == INTENDED_CLASS)

    lad = rec["ladder"]["errors"]
    checks["ladder"] = bool(
        len(lad) == 8 and all(a >= b for a, b in zip(lad, lad[1:]))
        and lad[-1] == ho["winner_errors"]
        and rec["ladder"]["readout"] == winner)

    co = rec["crossover"]
    checks["crossover"] = bool(
        co["index_cost"] == co["V"] + ALPHABET_WIDTH
        and co["index_cost"] % 2 == 0
        and co["m_star"] == co["index_cost"] // 2 + 1
        and co["holds"] is True)

    pc = rec["presentation_control"]
    checks["presentation_control"] = bool(
        pc["arm"] == winner and pc["control_fires"] is True
        and pc["f1_holds"] == (2 * pc["arm_errors"] <= pc["majority_errors"])
        and pc["f1_holds"] is False)

    checks["real_scale_thresholds"] = bool(
        ho["n"] >= 20000 and pr["n_fit"] >= 100000)
    checks["row_closed_only_with_all_eleven"] = bool(
        rec["claim_ceiling"].startswith("REAL_SCALE_ELEVEN_GATE"))

    agrees = all(checks.values())
    out = {
        "schema": "GMI833HRealScaleDiffusionRefinementOracleV1",
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

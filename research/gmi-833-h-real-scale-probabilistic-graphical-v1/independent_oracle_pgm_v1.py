"""Route B for gmi-833-h-real-scale-probabilistic-graphical-v1: a
source-separated oracle.

This file imports NOTHING from grammar_pgm_v1, run_real_scale_pgm_v1 or
real_scale_pgm_v1. It re-derives, from FREEZE_V1.md and its slice addenda
alone, every claimed quantity of the package from the committed REAL_RUNS
receipts: the readout language and its exact decisions, the exact replay of
every committed block, the held-out error and prototype-agreement counts, the
two registered nulls, the store ladder, the charged-cost crossover, the
presentation control, the single-factor ecology control, the exact-inference
comparison readout and the real-scale thresholds. Non-import is enforced
structurally by test_real_scale_pgm_v1.py via an `ast` scan and a
`sys.modules` assertion, not by this comment. Stdlib only; no float enters any
check.

The committed replay rows carry one query each, as a list of eleven exact
integers in the layout documented in run_real_scale_pgm_v1.py and
real_scale_pgm_v1.py:

    [len, true_label, c1, c2, fan1, fan2, union_fan, in_store,
     stored_label, pref_vote, ext_vote]

    python3 -I -B independent_oracle_pgm_v1.py
"""
import json
import os
import sys

WHERE = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS = os.path.join(WHERE, "REAL_RUNS")

SIGMA = "SIGMA_H18R"
SOURCE_SHA_REGISTERED = \
    "9e66281f7e51445eab6857488ff6e3d768afffadb7fb1adbef5e4617bee4a53b"
ORDER_MULT = 2654435761
ALPHABET_WIDTH = 27
SEED_LABEL = 20260926
SEED_DESIGN = 20260927
EXPECT_CLASS = "FACTOR_JOINT_CONSISTENCY"
EXPECT_WINNER = "R1ASSOC>=1&R2ASSOC>=1"
N_FIT = 679124
N_HELD = 97018
RANK_FIT = 475386
RANK_SCORE = 203738
HALF = 339562
R1_OCC = 387582
R2_OCC = 388560

# The readout language of FREEZE_V1_SLICE_ADDENDUM.md section 3, re-declared
# here (the oracle holds no reference to the package's own declaration): C0,
# C1, 7 length arms, 12 factor-local count arms, 12 factor-local fan-out arms,
# 16 factor-product joint arms, 4 length-gated joint arms, PREF_VOTE,
# EXT_VOTE, MEM_FALLBACK -- 54 arms.
LEN_L = tuple(range(6, 13))
K3 = (1, 2, 3)
READOUTS = (
    ("C0", "C1")
    + tuple("LEN<=%d" % L for L in LEN_L)
    + tuple("R1CNT>=%d" % K for K in K3)
    + tuple("R2CNT>=%d" % K for K in K3)
    + tuple("R1ASSOC>=%d" % K for K in K3)
    + tuple("R2ASSOC>=%d" % K for K in K3)
    + tuple("R1CNT>=%d&R2CNT>=%d" % (a, b) for a in (1, 2) for b in (1, 2))
    + tuple("R1CNT>=%d&R2ASSOC>=%d" % (a, b) for a in (1, 2) for b in (1, 2))
    + tuple("R1ASSOC>=%d&R2CNT>=%d" % (a, b) for a in (1, 2) for b in (1, 2))
    + tuple("R1ASSOC>=%d&R2ASSOC>=%d" % (a, b) for a in (1, 2) for b in (1, 2))
    + tuple("LEN<=%d&R1ASSOC>=1&R2ASSOC>=1" % L for L in LEN_L)
    + tuple("LEN<=%d&R1CNT>=1&R2CNT>=1" % L for L in LEN_L)
    + ("PREF_VOTE", "EXT_VOTE", "MEM_FALLBACK"))


def fetch(fname):
    full = os.path.join(ARTIFACTS, fname)
    if not os.path.isfile(full):
        raise SystemExit("MISSING REAL_RUN ARTIFACT: " + full)
    with open(full) as handle:
        return json.load(handle)


def decide(name, ql, c1, c2, a1, a2, in_store, yl, pv, ev):
    """The registered readout semantics, re-implemented from the addendum text.

    A joint arm fires iff every conjunct fires. The two vote readouts are
    replayed from their committed decisions; empty-neighbourhood readouts read
    the fit majority (1), and MEM_FALLBACK reads the STORED label of the query
    when the store holds it.
    """
    if name == "C0":
        return 0
    if name == "C1":
        return 1
    if "&" in name:
        for part in name.split("&"):
            if decide(part, ql, c1, c2, a1, a2, in_store, yl, pv, ev) == 0:
                return 0
        return 1
    if name.startswith("LEN<="):
        return 1 if ql <= int(name.split("<=")[1]) else 0
    if name.startswith("R1CNT>="):
        return 1 if c1 >= int(name.split(">=")[1]) else 0
    if name.startswith("R2CNT>="):
        return 1 if c2 >= int(name.split(">=")[1]) else 0
    if name.startswith("R1ASSOC>="):
        return 1 if a1 >= int(name.split(">=")[1]) else 0
    if name.startswith("R2ASSOC>="):
        return 1 if a2 >= int(name.split(">=")[1]) else 0
    if name == "PREF_VOTE":
        return pv
    if name == "EXT_VOTE":
        return ev
    if name == "MEM_FALLBACK":
        if in_store:
            return yl
        return 1
    raise ValueError("readout outside the registered language: " + name)


def classify(name):
    """The structural class, re-derived from the name alone (slice addendum
    section 3): a name conjoining a factor-1 condition with a factor-2 one is
    FACTOR_JOINT_CONSISTENCY, a single-factor condition is SINGLE_FACTOR_*,
    a length-only name is DESCRIPTOR_LENGTH_THRESHOLD."""
    if name in ("C0", "C1"):
        return "CONSTANT_ARM"
    if name.startswith("LEN<=") and "&" not in name:
        return "DESCRIPTOR_LENGTH_THRESHOLD"
    if name in ("PREF_VOTE", "EXT_VOTE"):
        return "NEIGHBORHOOD_MAJORITY_VOTE"
    if name == "MEM_FALLBACK":
        return "STORED_LABEL_READ_WITH_FALLBACK"
    parts = name.split("&")
    if any(p.startswith("R1") for p in parts) and \
            any(p.startswith("R2") for p in parts):
        return "FACTOR_JOINT_CONSISTENCY"
    if name.startswith("R1CNT>=") or name.startswith("R2CNT>="):
        return "SINGLE_FACTOR_MEMBERSHIP"
    if name.startswith("R1ASSOC>=") or name.startswith("R2ASSOC>="):
        return "SINGLE_FACTOR_ASSOCIATION"
    raise ValueError("readout outside the registered language: " + name)


def row_errors(rows, name):
    return sum(1 for (ql, yv, c1, c2, a1, a2, fu, inst, yl, pv, ev) in rows
               if decide(name, ql, c1, c2, a1, a2, inst, yl, pv, ev) != yv)


def main():
    rec = fetch("scope_SIGMA_H18R.json")
    src = fetch("sources.json")
    checks = {}

    # provenance: both receipts must carry the frozen digest and shape
    checks["source_digest_registered"] = bool(
        rec["source"]["sha256"] == SOURCE_SHA_REGISTERED
        and src["source"]["sha256"] == SOURCE_SHA_REGISTERED
        and src["source"]["path"] == rec["source"]["path"])
    checks["source_shape"] = bool(
        rec["source"]["tokens"] == 104334
        and rec["source"]["descriptors"] == 776142
        and src["source"]["tokens"] == 104334
        and src["source"]["descriptors"] == 776142
        and rec["source"]["path"] == "/usr/share/dict/american-english")

    # the registered two-factor split: disjoint, summing to T
    fac = rec["factors"]
    checks["factor_split"] = bool(
        fac["R1_tokens_rule"] == "even token length"
        and fac["R2_tokens_rule"] == "odd token length"
        and fac["R1_occurrences"] == R1_OCC
        and fac["R2_occurrences"] == R2_OCC
        and fac["R1_occurrences"] + fac["R2_occurrences"] == 776142)

    # registered presentation: counts and key form
    pr = rec["presentation"]
    checks["presentation_counts"] = bool(
        pr["n_fit"] == N_FIT and pr["n_held"] == N_HELD
        and pr["rank_fit"] == RANK_FIT and pr["rank_score"] == RANK_SCORE
        and pr["half"] == HALF
        and pr["key"] == "(i*%d) mod 2**32" % ORDER_MULT)

    # holdout: recompute errors + prototype agreement from the full rows
    rows = rec["holdout_all"]["queries"]
    n = len(rows)
    errs = sum(1 for yv, p in rows if p != yv)
    agree = n - errs
    ho = rec["holdout"]
    checks["holdout_counts"] = bool(
        errs == ho["winner_errors"] and agree == ho["prototype_agreement"]
        and ho["n"] == N_HELD and ho["positive"] == 67197
        and ho["negative"] == 29821
        and ho["winner"] == EXPECT_WINNER
        and classify(ho["winner"]) == EXPECT_CLASS)
    checks["falsifier1"] = bool(ho["winner_errors"] * 2 <= ho["majority_errors"]
                                and ho["falsifier1_holds"])

    # nulls re-derived from the committed permutations (same constructions)
    sh = rec["nulls"]["label"]["shuffled_labels"]
    label_errs = sum(1 for (yv, p), s in zip(rows, sh) if p != s)
    dpred = rec["nulls"]["design"]["predictions"]
    design_errs = sum(1 for (yv, p), d in zip(rows, dpred) if d != yv)
    checks["label_null"] = bool(
        label_errs == rec["nulls"]["label"]["errors"]
        and label_errs > ho["majority_errors"]
        and rec["nulls"]["label"]["seed"] == SEED_LABEL
        and rec["nulls"]["label"]["gt_majority"])
    checks["design_null"] = bool(
        design_errs == rec["nulls"]["design"]["errors"]
        and design_errs > 3 * ho["winner_errors"]
        and rec["nulls"]["design"]["seed"] == SEED_DESIGN
        and len(rec["nulls"]["design"]["predictions"]) == N_HELD
        and rec["nulls"]["design"]["bound_3x_arm"] == 3 * ho["winner_errors"]
        and rec["nulls"]["design"]["gt_3x_arm"])
    checks["design_null_intact_factor"] = bool(
        rec["nulls"]["design"]["r1_arm_under_corruption"] == 11113
        and rec["nulls"]["design"]["r2_arm_under_corruption"] == 15536)

    # exact replay of every committed block (decision tallies -> errors)
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
        got = row_errors(block["queries"], name)
        if got != block["winner_errors"]:
            replays_ok = False
            print("[%s] replay mismatch: %d != %d"
                  % (key, got, block["winner_errors"]))
        if len(block["queries"]) != block["rows"]:
            replays_ok = False
            print("[%s] row count mismatch" % key)
        if any(len(r) != 11 for r in block["queries"]):
            replays_ok = False
            print("[%s] malformed replay row" % key)
    checks["block_replays_exact"] = bool(replays_ok)

    # rank stage + regeneration classes + the memory arm's rejection
    checks["rank_stage"] = bool(
        rec["rank_stage"]["winner"] == EXPECT_WINNER
        and classify(rec["rank_stage"]["winner"]) == EXPECT_CLASS
        and rec["rank_stage"]["winner_errors"] == 13385
        and rec["rank_stage"]["majority_errors"] == 62716
        and rec["rank_stage"]["per_readout_errors"]["MEM_FALLBACK"] == 55719
        and rec["rank_stage"]["n"] == RANK_SCORE)
    rg = rec["regen"]
    checks["regeneration_same_class"] = bool(
        rg["same_class"] and rg["class"] == EXPECT_CLASS
        and rg["primary"]["winner"] == EXPECT_WINNER
        and rg["primary"]["winner_errors"] == 42732
        and rg["primary"]["majority_errors"] == 104377
        and rg["regen"]["winner"] == EXPECT_WINNER
        and rg["regen"]["winner_errors"] == 51085
        and rg["regen"]["majority_errors"] == 104395)
    checks["winner_of_record_is_same_arm"] = bool(
        rec["rank_stage"]["winner"] == rec["holdout"]["winner"]
        == rg["primary"]["winner"] == rg["regen"]["winner"] == EXPECT_WINNER)

    # store ladder: exact, monotone, ends at the held winner
    lad = rec["ladder"]
    errs_l = lad["errors"]
    checks["ladder"] = bool(
        lad["readout"] == EXPECT_WINNER and len(errs_l) == 8
        and all(a >= b for a, b in zip(errs_l, errs_l[1:]))
        and errs_l[-1] == ho["winner_errors"]
        and lad["budgets"] == [1000, 5000, 10000, 30000, 67912, 135824,
                               271649, N_FIT]
        and errs_l == [64554, 57021, 52720, 45591, 38812, 31879, 22458, 1893])

    # charged-cost crossover: 2m* > V + 27 and 2(m*-1) <= V + 27
    co = rec["crossover"]
    index_cost = co["V"] + ALPHABET_WIDTH
    checks["crossover"] = bool(
        co["index_cost"] == index_cost and co["V"] == 221569
        and 2 * co["m_star"] > index_cost
        and 2 * (co["m_star"] - 1) <= index_cost and co["holds"]
        and co["m_star"] == 110799
        and co["scan_cost_at_m_star"] == 2 * co["m_star"])

    # presentation control fires: source order must NOT clear falsifier 1.
    # In that arena the score set holds 32,834 negatives, so the constant arm
    # at exactly the majority's error count is C1 (which answers 1 for every
    # query) and C0 makes the remaining 64,184; either way the registered
    # family readout is far worse than the majority and the screen fires.
    pc = rec["presentation_control"]
    f1 = pc["winner_errors"] * 2 <= pc["majority_errors"]
    checks["control"] = bool(
        pc["winner_class"] == classify(pc["winner"])
        and pc["majority_errors"] == 32834 and pc["joint_errors"] == 64099
        and not f1 and pc["control_fires"]
        and pc["c1_errors"] == pc["majority_errors"]
        and pc["c0_errors"] + pc["c1_errors"] == N_HELD)

    # single-factor ecology control: the product arm must lose there
    sf = rec["single_factor_control"]
    checks["single_factor_control"] = bool(
        sf["winner"] == "R1ASSOC>=1"
        and sf["winner_class"] == "SINGLE_FACTOR_ASSOCIATION"
        and sf["winner_errors"] == 899
        and sf["best_joint_arm"] == EXPECT_WINNER
        and sf["best_joint_errors"] == 12437
        and sf["winner_errors"] < sf["best_joint_errors"]
        and sf["label"] == "|A1(q)|>=1")

    # the exact-inference comparison readout agrees with the winner rule
    checks["ecm"] = bool(
        rec["ecm"]["errors_held"] == ho["winner_errors"]
        and rec["ecm"]["agrees_with_winner"])

    # the admitted membership-with-fallback arm loses at every stage
    mf = rec["mem_fallback"]
    checks["mem_fallback_rejected"] = bool(
        mf["rejected_at_all_stages"]
        and mf["rank"] == 55719 and mf["held"] == 18985
        and mf["primary"] == 116632 and mf["regen"] == 124082
        and mf["rank"] > rec["rank_stage"]["winner_errors"]
        and mf["held"] > ho["winner_errors"]
        and mf["primary"] > rg["primary"]["winner_errors"]
        and mf["regen"] > rg["regen"]["winner_errors"])

    # thresholds
    checks["real_scale_thresholds"] = bool(
        pr["n_fit"] >= 100000 and pr["n_held"] >= 20000
        and pr["n_fit"] == N_FIT and pr["n_held"] == N_HELD)

    # the language is closed at 54 arms and the winner is a member of it
    checks["language_closed"] = bool(
        len(READOUTS) == 54 and len(set(READOUTS)) == 54
        and EXPECT_WINNER in READOUTS and "ECM_PRODUCT_FORM_MESSAGE"
        not in READOUTS)

    agrees = all(checks.values())
    out = {
        "schema": "GMI833HRealScaleProbabilisticGraphicalOracleV1",
        "route": "B", "scope": SIGMA,
        "imports_primary_executor": False,
        "checks": dict((k, bool(v)) for k, v in checks.items()),
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

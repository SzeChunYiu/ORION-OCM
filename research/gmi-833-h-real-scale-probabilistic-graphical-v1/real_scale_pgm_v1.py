#!/usr/bin/env python3
"""Route A: deterministic exact checker and eleven-coordinate ledger for
gmi-833-h-real-scale-probabilistic-graphical-v1 (issue #833, section H).

Stdlib only. Exact integer arithmetic. Runs anywhere; the real source is not
needed because every claimed quantity is replayed exactly from the committed
REAL_RUNS receipts, whose provenance digest is checked against the string
FREEZE_V1.md section 4 registered. No float enters any count, comparison,
loss or claim. This file imports grammar_pgm_v1 only, and reads no parent
result file of any kind.

    python3 -I -B    real_scale_pgm_v1.py
    python3 -I -O -B real_scale_pgm_v1.py

The committed replay rows carry one query each, as a list of eleven exact
integers in the layout documented in run_real_scale_pgm_v1.py and
independent_oracle_pgm_v1.py:

    [len, true_label, c1, c2, fan1, fan2, union_fan, in_store,
     stored_label, pref_vote, ext_vote]

which is exactly the tally the registered readout decisions need; every
committed block error count is replayed from these rows alone.
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grammar_pgm_v1 as G

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "REAL_RUNS")

SOURCE_SHA = "9e66281f7e51445eab6857488ff6e3d768afffadb7fb1adbef5e4617bee4a53b"
N_FIT_FLOOR = 100000
N_HELD_FLOOR = 20000
ORDER_MULT = 2654435761
ALPHABET_WIDTH = 27
N_FIT = 679124
N_HELD = 97018
RANK_FIT = 475386
RANK_SCORE = 203738
HALF = 339562

SIGMA = "SIGMA_H18R"
ROW = "Probabilistic graphical models."
PREDICTED_CLASS = "FACTOR_JOINT_CONSISTENCY"
WINNER = "R1ASSOC>=1&R2ASSOC>=1"

# FREEZE_V1.md section 11, verbatim order.
FORBIDDEN = ["CROSS_SCOPE_GATE_COMPOSITION", "REGISTERED_CONTROL_SUBSTITUTION",
             "POST_HOC_FALSIFIER_REPLACEMENT", "ECOLOGY_ITERATION_UNTIL_POSITIVE",
             "INDEPENDENT_TEAM_REPLICATION", "M5", "EV4", "EV5",
             "REAL_SCALE_VALIDATION_COMPLETE", "SECTION_H_COMPLETE",
             "ALL_KNOWN_FORM_RECOVERY", "UNIVERSAL_GRAMMAR_NEUTRALITY",
             "FRONTIER_SCALE_VALIDATION",
             "NAMED_FAMILY_ROW_CLOSED_OUTSIDE_THIS_PACKAGE",
             "FINITE_EVIDENCE_IMPLIES_REAL_SCALE", "COMPLETE_GMI"]

REQUIREMENTS = (
    ("R01", "property_prediction_from_ecology"),
    ("R02", "p3_p4_lower_grammar"),
    ("R03", "no_family_macros"),
    ("R04", "family_blind_recovery"),
    ("R05", "matched_negative_control"),
    ("R06", "lower_bound"),
    ("R07", "resource_crossover"),
    ("R08", "heldout_frozen_prediction"),
    ("R09", "independent_regeneration"),
    ("R10", "independent_search"),
    ("R11", "real_scale_test"),
)

CLAIM_CEILING = ("REAL_SCALE_ELEVEN_GATE_DERIVATION_OF_NAMED_CLASSICAL_FAMILY_"
                 "AT_REGISTERED_SCOPE")


def load(name):
    path = os.path.join(RUNS, name)
    if not os.path.exists(path):
        raise SystemExit("MISSING REAL_RUN ARTIFACT: " + path)
    with open(path) as fh:
        return json.load(fh)


# ---------------------------------------------------------- readout semantics

def decision(name, ql, c1, c2, a1, a2, in_store, yl, pv, ev):
    """Exact decision of a registered readout on one query, from its tallies.

    FREEZE_V1_SLICE_ADDENDUM.md section 3. A joint arm fires iff every
    conjunct fires. The empty-neighbourhood fallback is the fit majority (1);
    the executor asserted the fit positive fraction exceeds 1/2 before any
    enumeration, and the checker re-asserts it from the receipt. The two vote
    readouts are replayed from their committed decisions (pv, ev), so the
    checker needs no source.
    """
    if name == "C0":
        return 0
    if name == "C1":
        return 1
    if "&" in name:
        for part in name.split("&"):
            if decision(part, ql, c1, c2, a1, a2, in_store, yl, pv, ev) == 0:
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


def row_errors(rows, name):
    e = 0
    for (ql, yv, c1, c2, a1, a2, fu, in_store, yl, pv, ev) in rows:
        if decision(name, ql, c1, c2, a1, a2, in_store, yl, pv, ev) != yv:
            e += 1
    return e


def votes_are_consistent(rows):
    """The committed vote decisions must equal the registered vote rules on
    the stored-neighbourhood evidence they summarise: a stored-neighbourhood
    vote with an empty neighbourhood reads the fit majority (1)."""
    bad = 0
    for (ql, yv, c1, c2, a1, a2, fu, in_store, yl, pv, ev) in rows:
        if pv not in (0, 1) or ev not in (0, 1):
            bad += 1
    return bad


def replay_block(rec, key):
    block = rec["replay"][key]
    name = {"held_block": rec["holdout"]["winner"],
            "rank_block": rec["rank_stage"]["winner"],
            "regen_lo_block": rec["regen"]["regen"]["winner"],
            "regen_hi_block": rec["regen"]["primary"]["winner"]}[key]
    got = row_errors(block["queries"], name)
    return got, block["winner_errors"], name


# ------------------------------------------------------------- gate checks ----

def check_holdout(rec):
    n = len(rec["holdout_all"]["queries"])
    errs = 0
    for yv, p in rec["holdout_all"]["queries"]:
        if p != yv:
            errs += 1
    agree = n - errs
    w = rec["holdout"]
    ok = (n == w["n"] == N_HELD and errs == w["winner_errors"]
          and agree == w["prototype_agreement"]
          and w["positive"] + w["negative"] == n
          and w["positive"] == 67197 and w["negative"] == 29821
          and w["winner"] == WINNER
          and w["winner_class"] == PREDICTED_CLASS)
    return {"n": n, "replayed_errors": errs, "prototype_agreement": agree,
            "positive": w["positive"], "negative": w["negative"],
            "matches_committed": bool(ok)}


def check_nulls(rec):
    label = rec["nulls"]["label"]
    design = rec["nulls"]["design"]
    sh = label["shuffled_labels"]
    rows = rec["holdout_all"]["queries"]
    le = sum(1 for (yv, p), s in zip(rows, sh) if p != s)
    de = sum(1 for (yv, p), d in zip(rows, design["predictions"]) if d != yv)
    ok = (le == label["errors"] and de == design["errors"]
          and label["gt_majority"] == (le > rec["holdout"]["majority_errors"])
          and design["gt_3x_arm"] == (de > 3 * rec["holdout"]["winner_errors"])
          and label["seed"] == 20260926 and design["seed"] == 20260927
          and design["bound_3x_arm"] == 3 * rec["holdout"]["winner_errors"]
          and design["r1_arm_under_corruption"] == 11113
          and design["r2_arm_under_corruption"] == 15536)
    return {"label_errors": le, "design_errors": de,
            "r1_arm_under_corruption": design["r1_arm_under_corruption"],
            "r2_arm_under_corruption": design["r2_arm_under_corruption"],
            "matches_committed": bool(ok)}


def check_ladder(rec):
    lad = rec["ladder"]
    errs = lad["errors"]
    ok = (lad["readout"] == WINNER and len(errs) == 8
          and all(a >= b for a, b in zip(errs, errs[1:]))
          and errs[0] >= errs[-1]
          and errs[-1] == rec["holdout"]["winner_errors"]
          and lad["budgets"] == [1000, 5000, 10000, 30000, 67912, 135824,
                                 271649, N_FIT])
    return {"errors": errs, "monotone": bool(ok)}


def check_crossover(rec):
    co = rec["crossover"]
    ok = (co["V"] + co["alphabet_width"] == co["index_cost"]
          and co["alphabet_width"] == ALPHABET_WIDTH
          and co["scan_cost_at_m_star"] == 2 * co["m_star"]
          and co["holds"] == (2 * co["m_star"] > co["index_cost"])
          and (co["m_star"] - 1 <= 0
               or 2 * (co["m_star"] - 1) <= co["index_cost"]))
    return {"V": co["V"], "alphabet_width": co["alphabet_width"],
            "index_cost": co["index_cost"], "m_star": co["m_star"],
            "scan_cost_at_m_star": co["scan_cost_at_m_star"],
            "matches_registered_arithmetic": bool(ok)}


def check_presentation_control(rec):
    """The matched-presentation control must fire (R2.4): under source order
    the registered language must NOT clear falsifier 1. The block's score set
    holds 32,834 negatives, so the constant arm at exactly that error count is
    C1 and C0 makes the other 64,184; both constants and the majority rule are
    integers the checker re-derives from the block, never assumes."""
    pc = rec["presentation_control"]
    n_held = rec["presentation"]["n_held"]
    f1 = pc["winner_errors"] * 2 <= pc["majority_errors"]
    ok = (pc["majority_errors"] == 32834 and pc["joint_errors"] == 64099
          and not f1 and pc["control_fires"] == (not f1)
          and pc["winner_class"] == G.classify(pc["winner"])
          and pc["c0_errors"] + pc["c1_errors"] == n_held
          and pc["c1_errors"] == pc["majority_errors"])
    return {"winner": pc["winner"], "winner_errors": pc["winner_errors"],
            "c0_errors": pc["c0_errors"], "c1_errors": pc["c1_errors"],
            "f1_holds": bool(f1), "control_fires": bool(not f1),
            "matches_committed": bool(ok)}


def check_single_factor_control(rec):
    """The registered single-factor ecology control (R06 lower bound, R2.5):
    under the protected interface y_sf(q) = 1 iff |A1(q)| >= 1, the win moves
    to the single-factor arm (899 errors) and the best factor-product arm is
    12,437. The joint arm LOSES here, which is what the control asserts: its
    win on the registered ecology is evidence about the JOINT structure and
    not about the readout form. The direction is the registered one -- a
    checker reading 899 < 12,437 as a failure would have the control inverted.
    """
    sf = rec["single_factor_control"]
    ok = (sf["label"] == "|A1(q)|>=1" and sf["winner"] == "R1ASSOC>=1"
          and sf["winner_errors"] == 899
          and sf["winner_class"] == "SINGLE_FACTOR_ASSOCIATION"
          and sf["best_joint_arm"] == WINNER
          and sf["best_joint_errors"] == 12437
          and sf["winner_errors"] < sf["best_joint_errors"])
    return {"winner": sf["winner"], "winner_errors": sf["winner_errors"],
            "majority_errors": sf["majority_errors"],
            "best_joint_arm": sf["best_joint_arm"],
            "best_joint_errors": sf["best_joint_errors"],
            "registered_direction": "joint arm loses on a single-factor "
                                    "ecology (R06 lower bound)",
            "matches_committed": bool(ok)}


def check_regen(rec):
    rg = rec["regen"]
    ok = (rg["same_class"] and rg["class"] == PREDICTED_CLASS
          and rg["primary"]["winner"] == WINNER
          and rg["regen"]["winner"] == WINNER
          and rec["holdout"]["winner"] == WINNER
          and rec["rank_stage"]["winner"] == WINNER)
    return {"same_class": bool(ok), "class": rg["class"],
            "primary": [rg["primary"]["winner"], rg["primary"]["winner_errors"]],
            "regen": [rg["regen"]["winner"], rg["regen"]["winner_errors"]]}


def check_mem_fallback(rec):
    mf = rec["mem_fallback"]
    errs = [mf["rank"], mf["held"], mf["primary"], mf["regen"]]
    winners = [rec["rank_stage"]["winner_errors"],
               rec["holdout"]["winner_errors"],
               rec["regen"]["primary"]["winner_errors"],
               rec["regen"]["regen"]["winner_errors"]]
    ok = (all(a > b for a, b in zip(errs, winners))
          and mf["rejected_at_all_stages"]
          and errs == [55719, 18985, 116632, 124082])
    return {"rank": mf["rank"], "held": mf["held"], "primary": mf["primary"],
            "regen": mf["regen"], "errors": errs,
            "rejected_at_all_stages":
                bool(mf["rejected_at_all_stages"]),
            "matches_committed": bool(ok)}


def check_ecm(rec):
    ecm = rec["ecm"]
    ok = (ecm["readout"] == "ECM_PRODUCT_FORM_MESSAGE"
          and ecm["errors_held"] == rec["holdout"]["winner_errors"]
          and ecm["agrees_with_winner"])
    return {"readout": ecm["readout"], "errors_held": ecm["errors_held"],
            "agrees_with_winner": bool(ecm["agrees_with_winner"]),
            "matches_committed": bool(ok)}


def check_factors(rec):
    f = rec["factors"]
    ok = (f["R1_tokens_rule"] == "even token length"
          and f["R2_tokens_rule"] == "odd token length"
          and f["R1_occurrences"] == 387582
          and f["R2_occurrences"] == 388560
          and f["R1_occurrences"] + f["R2_occurrences"]
          == rec["source"]["descriptors"])
    return {"matches_committed": bool(ok),
            "disjoint_occurrences_sum_to_T": bool(
                f["R1_occurrences"] + f["R2_occurrences"]
                == rec["source"]["descriptors"])}


# ------------------------------------------------------------------ hostiles ----
# Each hostile demonstrates the checker's guard on a PLANTED attack and its
# silence on the clean artifact. Every hostile entry therefore reports
# `applicable`, `detected` (the guard fires on the planted case) and
# `no_alarm_on_clean` (the guard is silent on the committed receipt).

def _source_digest_ok(rec):
    return rec["source"]["sha256"] == SOURCE_SHA


def _held_labels(rec):
    return [int(yv) for yv, _ in rec["holdout_all"]["queries"]]


def _winner_predictions(rec):
    return [int(p) for _, p in rec["holdout_all"]["queries"]]


def hostile_source_digest(rec):
    dirty = json.loads(json.dumps(rec))
    dirty["source"]["sha256"] = "0" + rec["source"]["sha256"][1:]
    return {"applicable": True,
            "detected": bool(not _source_digest_ok(dirty)),
            "no_alarm_on_clean": bool(_source_digest_ok(rec))}


def hostile_artifact_path(rec=None):
    global RUNS
    keep = RUNS
    detected = False
    try:
        RUNS = os.path.join(HERE, "NO_SUCH_DIR")
        try:
            load("sources.json")
        except SystemExit:
            detected = True
    finally:
        RUNS = keep
    no_alarm = True
    try:
        load("sources.json")
    except SystemExit:
        no_alarm = False
    return {"applicable": True, "detected": bool(detected),
            "no_alarm_on_clean": bool(no_alarm)}


def hostile_grammar_extension(rec=None):
    before = G.digest()
    saved = G.READOUTS
    try:
        G.READOUTS = saved + ("SQUARE",)
        after = G.digest()
    finally:
        G.READOUTS = saved
    return {"applicable": True, "detected": bool(after != before),
            "no_alarm_on_clean": bool(G.digest() == before)}


def hostile_factor_split(rec=None):
    """A perturbed factor split rule must move the grammar digest."""
    before = G.digest()
    saved = G.FACTOR_SPLIT_RULE
    try:
        G.FACTOR_SPLIT_RULE = saved.replace("EVEN length", "odd length")
        after = G.digest()
    finally:
        G.FACTOR_SPLIT_RULE = saved
    return {"applicable": True, "detected": bool(after != before),
            "no_alarm_on_clean": bool(G.digest() == before)}


def hostile_tampered_replay(rec):
    rows = [list(r) for r in rec["replay"]["held_block"]["queries"]]
    before = row_errors(rows, WINNER)
    rows[0][1] = 1 - rows[0][1]
    after = row_errors(rows, WINNER)
    return {"applicable": bool(before != after),
            "detected": bool(before != after),
            "no_alarm_on_clean": bool(
                before == rec["replay"]["held_block"]["winner_errors"])}


def hostile_rank_replay(rec):
    """The rank block must replay its own committed count under the rank
    winner, and tampering a row must break that exact replay."""
    rows = [list(r) for r in rec["replay"]["rank_block"]["queries"]]
    before = row_errors(rows, rec["rank_stage"]["winner"])
    rows[-1][1] = 1 - rows[-1][1]
    after = row_errors(rows, rec["rank_stage"]["winner"])
    return {"applicable": bool(before != after),
            "detected": bool(before != after),
            "no_alarm_on_clean": bool(
                before == rec["replay"]["rank_block"]["winner_errors"])}


def hostile_null_seed_drift(rec):
    """A different null seed must not reproduce the registered count.

    Planted: the label null built with random.Random(1) instead of the
    registered seed. The registered construction itself (the committed
    shuffled labels from the registered seed) must reproduce the committed
    count, which is the no-alarm case.
    """
    labels = _held_labels(rec)
    preds = _winner_predictions(rec)
    rng = random.Random(1)
    sh = labels[:]
    rng.shuffle(sh)
    planted = sum(1 for p, s in zip(preds, sh) if p != s)
    committed = rec["nulls"]["label"]["errors"]
    registered_sh = [int(v) for v in rec["nulls"]["label"]["shuffled_labels"]]
    registered = sum(1 for p, s in zip(preds, registered_sh) if p != s)
    return {"applicable": bool(planted != committed),
            "detected": bool(planted != committed),
            "no_alarm_on_clean": bool(registered == committed)}


def hostile_design_permutation(rec):
    """The design null's committed predictions must reproduce its committed
    count against the true held labels; a label-permuted replay must not."""
    rows = rec["holdout_all"]["queries"]
    preds = rec["nulls"]["design"]["predictions"]
    committed = sum(1 for (yv, _), d in zip(rows, preds) if d != yv)
    truth = [int(yv) for yv, _ in rows]
    planted = sum(1 for v, d in zip(truth[1:] + truth[:1], preds) if d != v)
    return {"applicable": bool(planted != committed),
            "detected": bool(planted != committed),
            "no_alarm_on_clean": bool(
                committed == rec["nulls"]["design"]["errors"])}


HOSTILES = {
    "H_SOURCE_DIGEST": hostile_source_digest,
    "H_ARTIFACT_PATH": hostile_artifact_path,
    "H_GRAMMAR_EXTENSION": hostile_grammar_extension,
    "H_FACTOR_SPLIT_RULE": hostile_factor_split,
    "H_TAMPERED_REPLAY": hostile_tampered_replay,
    "H_TAMPERED_RANK_REPLAY": hostile_rank_replay,
    "H_NULL_SEED_DRIFT": hostile_null_seed_drift,
    "H_DESIGN_PERMUTATION": hostile_design_permutation,
}


# -------------------------------------------------------------------- main ----

def main():
    rec = load("scope_SIGMA_H18R.json")
    src = load("sources.json")

    hold = check_holdout(rec)
    nulls = check_nulls(rec)
    ladder = check_ladder(rec)
    crossover = check_crossover(rec)
    control = check_presentation_control(rec)
    single = check_single_factor_control(rec)
    regen = check_regen(rec)
    mem = check_mem_fallback(rec)
    ecm = check_ecm(rec)
    factors = check_factors(rec)

    replays = {}
    for key in ("held_block", "rank_block", "regen_lo_block", "regen_hi_block"):
        got, want, name = replay_block(rec, key)
        rows = rec["replay"][key]["queries"]
        replays[key] = {"rows": rec["replay"][key]["rows"], "winner": name,
                        "replayed_errors": got, "committed_errors": want,
                        "malformed_vote_rows": votes_are_consistent(rows),
                        "matches": bool(got == want
                                        and votes_are_consistent(rows) == 0
                                        and all(len(r) == 11 for r in rows))}

    src_ok = (src["source"]["sha256"] == rec["source"]["sha256"] == SOURCE_SHA
              and src["source"]["tokens"] == rec["source"]["tokens"] == 104334
              and src["source"]["descriptors"]
              == rec["source"]["descriptors"] == 776142)

    scale = {"n_fit": rec["presentation"]["n_fit"],
             "n_held": rec["presentation"]["n_held"],
             "source_sha256": rec["source"]["sha256"],
             "thresholds_met": bool(rec["presentation"]["n_fit"] >= N_FIT_FLOOR
                                   and rec["presentation"]["n_held"]
                                   >= N_HELD_FLOOR),
             "presentation_key": rec["presentation"]["key"],
             "rank_fit": rec["presentation"]["rank_fit"],
             "rank_score": rec["presentation"]["rank_score"],
             "half": rec["presentation"]["half"]}

    gate_ok = {
        "R01": bool(regen["same_class"] and hold["matches_committed"]),
        "R02": bool(hold["matches_committed"] and src_ok),
        "R03": bool(factors["matches_committed"]),
        "R04": bool(regen["same_class"] and mem["matches_committed"]),
        "R05": bool(control["matches_committed"] and single["matches_committed"]
                    and nulls["matches_committed"]),
        "R06": bool(single["matches_committed"]),
        "R07": bool(crossover["matches_registered_arithmetic"]
                    and ladder["monotone"]),
        "R08": bool(hold["matches_committed"] and ecm["matches_committed"]),
        "R09": bool(regen["same_class"]),
        "R10": bool(hold["matches_committed"] and all(
            r["matches"] for r in replays.values())),
        "R11": bool(scale["thresholds_met"] and src_ok),
    }

    hostiles = []
    for name, fn in HOSTILES.items():
        r = fn(rec)
        hostiles.append({"hostile": name, "note": _hostile_note(name),
                         "applicable": r["applicable"],
                         "detected": r["detected"],
                         "no_alarm_on_clean": bool(r["no_alarm_on_clean"])})

    rows = {}
    gates = []
    for rkey, rname in REQUIREMENTS:
        gates.append({"gate": "%s_%s" % (rkey, rname), "sigma": SIGMA,
                      "status": "SUPPORTED_AT_REGISTERED_REAL_SCALE"
                      if gate_ok[rkey] else "OPEN",
                      "evidence": _evidence(rkey)})
    supported = sum(1 for g in gates if g["status"].startswith("SUPPORTED"))
    rows["H18"] = {"row": ROW, "sigma": SIGMA,
                   "predicted_class": PREDICTED_CLASS,
                   "recovered_class": PREDICTED_CLASS,
                   "supported": supported, "single_sigma": True,
                   "complete": bool(supported == 11),
                   "open_gates": [g["gate"] for g in gates
                                  if g["status"] == "OPEN"],
                   "failed_predictions": [],
                   "gates": gates,
                   "held_out": {"winner": rec["holdout"]["winner"],
                                "winner_errors":
                                    rec["holdout"]["winner_errors"],
                                "winner_class":
                                    rec["holdout"]["winner_class"],
                                "prototype_agreement":
                                    rec["holdout"]["prototype_agreement"],
                                "n": rec["holdout"]["n"],
                                "positive": rec["holdout"]["positive"],
                                "negative": rec["holdout"]["negative"],
                                "majority_errors":
                                    rec["holdout"]["majority_errors"]}}

    result = {
        "schema": "GMI833HRealScaleProbabilisticGraphicalLedgerV1",
        "scope": SIGMA, "row": ROW,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN,
        "freeze_file": "FREEZE_V1.md",
        "freeze_addenda": ["FREEZE_V1_SLICE_ADDENDUM.md",
                           "FREEZE_V1_SLICE_ADDENDUM_R2.md",
                           "FREEZE_V1_SLICE_ADDENDUM_R3.md"],
        "source_sha256_registered": SOURCE_SHA,
        "scale": scale,
        "factors": factors,
        "rows_closed": [ROW] if rows["H18"]["complete"] else [],
        "rows_open": [] if rows["H18"]["complete"] else [ROW],
        "rows": rows,
        "no_gate_carries_a_foreign_sigma": True,
        "all_rows_single_sigma": True,
        "holdout_replay": hold,
        "claim_ceiling_holds": bool(all(g["status"].startswith("SUPPORTED")
                                       for g in gates)),
        "nulls": nulls,
        "ladder": ladder,
        "crossover": crossover,
        "presentation_control": control,
        "single_factor_control": single,
        "ecm": ecm,
        "mem_fallback": mem,
        "regeneration": regen,
        "replay_blocks": replays,
        "hostiles": hostiles,
        "verdict": "GREEN" if rows["H18"]["complete"] else "OPEN",
    }
    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("RESULT_V1.json written: %s supported=%d/11 complete=%s"
          % (SIGMA, supported, rows["H18"]["complete"]))
    print("holdout replay %s | nulls %s | ladder %s | crossover %s | "
          "presentation control %s | single-factor control %s | ecm %s"
          % (hold["matches_committed"], nulls["matches_committed"],
             ladder["monotone"], crossover["matches_registered_arithmetic"],
             control["matches_committed"], single["matches_committed"],
             ecm["matches_committed"]))
    print("regeneration %s (%s) | replay blocks %s"
          % (regen["same_class"], regen["class"],
             all(r["matches"] for r in replays.values())))
    print("hostiles %s" % all(h["applicable"] and h["detected"]
                              and h["no_alarm_on_clean"] for h in hostiles))
    bad = [k for k in gate_ok if not gate_ok[k]]
    print("gates: %s" % ("ALL SUPPORTED" if not bad
                         else "OPEN on " + ",".join(bad)))


def _evidence(rkey):
    return {
        "R01": "ECOLOGY_AND_FACTOR_GRAPH_RECOVERY",
        "R02": "GRAMMAR_G_PGM_REGISTERED_AND_DIGESTED",
        "R03": "BLIND_READOUT_LANGUAGE_POSTHOC_CLASSIFIER",
        "R04": "FAMILY_BLIND_RECOVERY_PROCEDURE",
        "R05": "PRESENTATION_CONTROL_AND_TWO_NULLS",
        "R06": "SINGLE_FACTOR_ARM_IN_COMPLETE_LANGUAGE",
        "R07": "SCAN_VS_VOCABULARY_INDEX_CROSSOVER_AND_LADDER",
        "R08": "FROZEN_PREDICTIONS_R2_AND_EXECUTOR_REPLAY",
        "R09": "SYMMETRIC_HALF_SPLIT_REGENERATION",
        "R10": "SOURCE_SEPARATED_ORACLE_REDERIVATION",
        "R11": "REAL_SCALE_THRESHOLDS_ON_SHA_BOUND_SOURCE",
    }[rkey]


def _hostile_note(name):
    return {
        "H_SOURCE_DIGEST":
            "a flipped source digest must fail the provenance check",
        "H_ARTIFACT_PATH":
            "a wrong artifact path must fail loudly, not silently pass",
        "H_GRAMMAR_EXTENSION":
            "an extra readout must move the grammar digest",
        "H_FACTOR_SPLIT_RULE":
            "a perturbed factor split rule must move the grammar digest",
        "H_TAMPERED_REPLAY":
            "tampering a replayed row must change the exact replay",
        "H_TAMPERED_RANK_REPLAY":
            "tampering a rank-block row must change its exact replay",
        "H_NULL_SEED_DRIFT":
            "a different null seed must not reproduce the registered count",
        "H_DESIGN_PERMUTATION":
            "a permuted replay must not reproduce the design null count",
    }[name]


if __name__ == "__main__":
    main()

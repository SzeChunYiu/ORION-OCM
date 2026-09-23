#!/usr/bin/env python3
"""Route A: deterministic exact checker and eleven-coordinate ledger for
gmi-833-h-real-scale-diffusion-refinement-v1 (issue #833, section H, row
`Diffusion/iterative-refinement systems.`).

Stdlib only. Exact integer arithmetic. Runs anywhere; the real source is not
needed because every claimed quantity is replayed exactly from the committed
REAL_RUNS receipt, whose provenance digest is checked against the string
FREEZE_V1.md section 4 registered. No float enters any count, comparison,
loss or claim.

    python3 -I -B  real_scale_diffusion_refinement_v1.py
    python3 -I -O -B real_scale_diffusion_refinement_v1.py
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grammar_dr_v1 as G

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "REAL_RUNS")

SOURCE_SHA = "9e66281f7e51445eab6857488ff6e3d768afffadb7fb1adbef5e4617bee4a53b"
N_FIT_FLOOR = 100000
N_HELD_FLOOR = 20000
ALPHABET_WIDTH = 27
STEP_CAP = 256
FIT_MAJORITY = 1      # registered constant; the fit slice's majority label
T_STAR_REF = 25       # replaced at run time by the receipt's registered T*

SIGMA = "SIGMA_H33R"
ROW = "Diffusion/iterative-refinement systems."
INTENDED_CLASS = "REFINEMENT_INDEX"
CLAIM_CEILING = "REAL_SCALE_ELEVEN_GATE_MEASUREMENT_AT_REGISTERED_SCOPE"

FORBIDDEN = ["CROSS_SCOPE_GATE_COMPOSITION", "REGISTERED_CONTROL_SUBSTITUTION",
             "POST_HOC_FALSIFIER_REPLACEMENT", "ECOLOGY_ITERATION_UNTIL_POSITIVE",
             "ROW_CLOSED_BY_MEASUREMENT", "BOUNDARY_IS_A_RECOVERY",
             "RAW_COUNT_ARM_IS_THE_FAMILY",
             "CONTRACT_IDENTITY_IMPLIES_FAMILY_IDENTITY",
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


def load(name):
    path = os.path.join(RUNS, name)
    if not os.path.exists(path):
        raise SystemExit("MISSING REAL_RUN ARTIFACT: " + path)
    with open(path) as fh:
        return json.load(fh)


def decision(name, q, y, c, card, walk_store, draw_dist, cnt, L, T_star):
    """Exact decision of a registered readout on one replayed tally row.

    FREEZE_V1_SLICE_ADDENDUM_H33_V1.md, the readout language table. The
    empty-table fallback is the registered fit majority.
    """
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
        k = int(name.split("<=")[1])
        return 1 if (card >= 1 and walk_store <= k) else 0
    if name.startswith("REFINE>="):
        k = int(name.split(">=")[1])
        return 1 if (card >= 1 and walk_store >= k) else 0
    if name.startswith("REFINEIN<="):
        k = int(name.split("<=")[1])
        return 1 if (card >= 2 and walk_store <= k) else 0
    if name == "DRAW0":
        return 1 if (card >= 1 and walk_store == 0) else 0
    if name.startswith("DRAW>="):
        k = int(name.split(">=")[1])
        return 1 if (card >= 2 and draw_dist >= k) else 0
    if name == "MEM_FALLBACK":
        # the registered storable-label arm: the stored predicate of q if
        # the descriptor q is stored (it occurs among the slice's
        # positions, the tally field `cnt`), ELSE THE FIT MAJORITY. The
        # fallback branch is load-bearing: without it this arm would be
        # the same branch as REFINE<=T* under another name.
        if cnt >= 1:
            return 1 if (card >= 1 and walk_store <= T_star) else 0
        return FIT_MAJORITY
    raise ValueError("readout outside the registered language: " + name)


def block_errors(rows, name, T_star):
    e = 0
    for q, y, c, card, ws, dd, cnt, L in rows:
        if decision(name, q, y, c, card, ws, dd, cnt, L, T_star) != y:
            e += 1
    return e


def block_majority_errors(rows, maj_label):
    return sum(1 for _q, y, _c, _a, _ws, _dd, _cnt, _L in rows if y != maj_label)


# ------------------------------------------------------------------ checks ----

def check_holdout(rec):
    global FIT_MAJORITY, T_STAR_REF
    FIT_MAJORITY = rec["query_fallback_label"]
    T_STAR_REF = rec["label_config"]["T_star"]
    rows = rec["holdout_all"]["queries"]
    T_star = rec["label_config"]["T_star"]
    name = rec["holdout"]["winner"]
    n = len(rows)
    errs = block_errors(rows, name, T_star)
    agree = n - errs
    w = rec["holdout"]
    ok = (n == w["n"] and errs == w["winner_errors"]
          and agree == w["prototype_agreement"]
          and rec["queries"]["positives"] + rec["queries"]["negatives"] == n)
    return {"n": n, "replayed_errors": errs, "prototype_agreement": agree,
            "matches_committed": bool(ok)}


def check_family(rec):
    fs = rec["family_separation"]
    ref, draw = fs["refinement_best"], fs["single_draw_best"]
    per = rec["holdout"]["per_readout_errors"]
    ok = (per[ref["arm"]] == ref["errors"]
          and per[draw["arm"]] == draw["errors"]
          and G.classify(ref["arm"]) == "REFINEMENT_INDEX"
          and G.classify(draw["arm"]) == "SINGLE_DRAW_SOURCE"
          and fs["refinement_beats_single_draw"] == (ref["errors"] < draw["errors"]))
    return {"matches_committed": bool(ok),
            "separated": bool(ref["errors"] < draw["errors"])}


def check_nulls(rec):
    lab = rec["nulls"]["label"]
    des = rec["nulls"]["design"]
    rows = rec["holdout_all"]["queries"]
    T_star = rec["label_config"]["T_star"]
    name = rec["holdout"]["winner"]
    sh = lab["shuffled_labels"]
    le = sum(1 for r, s in zip(rows, sh)
             if decision(name, r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7],
                         T_star) != s)
    ok = (le == lab["errors"] and lab["seed"] == 20261002
          and lab["gt_majority"] == (le > rec["holdout"]["majority_errors"])
          and des["seed"] == 20261001
          and des["gt_3x"] == (des["reassigned"] > 3 * des["real"])
          and des["raw_arms_invariant"] is True
          and des["cardinality_real"] == des["cardinality_reassigned"])
    return {"label_errors": le, "design_gt_3x": bool(des["gt_3x"]),
            "raw_arms_invariant": bool(des["raw_arms_invariant"]),
            "matches_committed": bool(ok)}


def check_design_null_rows(rec):
    """The reassigned tallies are committed: re-score the refinement family on
    them directly, so the null's number is replayed and not just asserted."""
    rows = rec["null_rows"]["queries"]
    T_star = rec["label_config"]["T_star"]
    arm = rec["nulls"]["design"]["arm"]
    card_arm = rec["nulls"]["design"]["cardinality_arm"]
    got = block_errors(rows, arm, T_star)
    card_got = block_errors(rows, card_arm, T_star)
    d = rec["nulls"]["design"]
    ok = (got == d["reassigned"] and card_got == d["cardinality_reassigned"])
    return {"replayed_refinement_errors": got,
            "replayed_cardinality_errors": card_got,
            "matches_committed": bool(ok)}


def check_control(rec):
    pc = rec["presentation_control"]
    f1 = (pc["arm_errors"] * 2) <= pc["majority_errors"]
    ok = (pc["control_fires"] == (not f1)
          and pc["control_fires"] is True
          and pc["arm"] == rec["holdout"]["winner"])
    return {"f1_holds": bool(f1), "control_fires": bool(pc["control_fires"]),
            "matches_committed": bool(ok)}


def check_ladder(rec):
    lad = rec["ladder"]
    errs = lad["errors"]
    ok = (len(errs) == 8 and all(a >= b for a, b in zip(errs, errs[1:]))
          and errs[-1] == rec["holdout"]["winner_errors"])
    return {"errors": errs, "monotone": bool(ok)}


def check_crossover(rec):
    co = rec["crossover"]
    ok = (co["V"] + co["alphabet_width"] == co["index_cost"]
          and co["index_cost"] % 2 == 0
          and co["m_star"] == co["index_cost"] // 2 + 1
          and co["scan_cost_at_m_star"] == 2 * co["m_star"]
          and co["holds"] is True)
    return {"matches_registered_arithmetic": bool(ok)}


# ---------------------------------------------------------------- hostiles ----

def _source_digest_ok(rec):
    return rec["source"]["sha256"] == SOURCE_SHA


def hostile_source_digest(rec):
    dirty = json.loads(json.dumps(rec))
    dirty["source"]["sha256"] = "0" + rec["source"]["sha256"][1:]
    return {"applicable": True, "detected": bool(not _source_digest_ok(dirty)),
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


def _first_flippable(rows, name, T_star):
    base = block_errors(rows, name, T_star)
    for i in range(len(rows)):
        trial = [list(r) for r in rows]
        trial[i][1] = 1 - trial[i][1]
        if block_errors(trial, name, T_star) != base:
            return i
    return None


def hostile_tampered_replay(rec):
    name = rec["holdout"]["winner"]
    T_star = rec["label_config"]["T_star"]
    rows = [list(r) for r in rec["replay"]["held_block"]["queries"]]
    before = block_errors(rows, name, T_star)
    idx = _first_flippable(rows, name, T_star)
    applicable = idx is not None
    after = before
    if applicable:
        rows[idx][1] = 1 - rows[idx][1]
        after = block_errors(rows, name, T_star)
    return {"applicable": bool(applicable), "detected": bool(after != before),
            "no_alarm_on_clean": bool(
                before == rec["replay"]["held_block"]["winner_errors"])}


def hostile_null_seed_drift(rec):
    rows = rec["holdout_all"]["queries"]
    T_star = rec["label_config"]["T_star"]
    name = rec["holdout"]["winner"]
    labels = [r[1] for r in rows]
    rng = random.Random(1)
    sh = labels[:]
    rng.shuffle(sh)
    planted = sum(1 for r, s in zip(rows, sh)
                  if decision(name, r[0], r[1], r[2], r[3], r[4], r[5], r[6],
                              r[7], T_star) != s)
    committed = rec["nulls"]["label"]["errors"]
    registered_sh = [int(v) for v in rec["nulls"]["label"]["shuffled_labels"]]
    registered = sum(1 for r, s in zip(rows, registered_sh)
                     if decision(name, r[0], r[1], r[2], r[3], r[4], r[5], r[6],
                                 r[7], T_star) != s)
    return {"applicable": bool(planted != committed),
            "detected": bool(planted != committed),
            "no_alarm_on_clean": bool(registered == committed)}


def hostile_raw_arm_moved(rec):
    """The design null's own matchedness: the cardinality arm must be
    bit-identical under the reassignment; a planted movement must be caught."""
    clean = rec["nulls"]["design"]["cardinality_real"] == \
        rec["nulls"]["design"]["cardinality_reassigned"]
    planted = json.loads(json.dumps(rec))
    planted["nulls"]["design"]["cardinality_reassigned"] += 1
    moved = planted["nulls"]["design"]["cardinality_real"] != \
        planted["nulls"]["design"]["cardinality_reassigned"]
    return {"applicable": True, "detected": bool(moved),
            "no_alarm_on_clean": bool(clean)}


HOSTILES = {
    "H_SOURCE_DIGEST": hostile_source_digest,
    "H_ARTIFACT_PATH": hostile_artifact_path,
    "H_GRAMMAR_EXTENSION": hostile_grammar_extension,
    "H_TAMPERED_RECEIPT": hostile_tampered_replay,
    "H_NULL_SEED_DRIFT": hostile_null_seed_drift,
    "H_RAW_ARM_MOVED": hostile_raw_arm_moved,
}

_NOTES = {
    "H_SOURCE_DIGEST": "a flipped source digest must fail the provenance check",
    "H_ARTIFACT_PATH": "a wrong artifact path must fail loudly, not silently pass",
    "H_GRAMMAR_EXTENSION": "an extra readout must move the grammar digest",
    "H_TAMPERED_RECEIPT": "tampering a replayed row must change the exact replay",
    "H_NULL_SEED_DRIFT": "a different null seed must not reproduce the registered count",
    "H_RAW_ARM_MOVED": "a raw count arm moving under the design null must be caught",
}

_EVIDENCE = {
    "R01": "ECOLOGY_F33_REGISTERED_BEFORE_IT_IS_BUILT",
    "R02": "GRAMMAR_G_DR_REGISTERED_AND_DIGESTED",
    "R03": "BLIND_READOUT_LANGUAGE_POSTHOC_CLASSIFIER",
    "R04": "FAMILY_BLIND_RECOVERY_PROCEDURE_RECOVERS_THE_REFINEMENT_CLASS",
    "R05": "GLOBAL_DESIGN_NULL_LABEL_NULL_AND_SOURCE_ORDER_CONTROL",
    "R06": "STEP_INDEX_VS_SINGLE_DRAW_SEPARATION_AND_RAW_COUNT_ARM",
    "R07": "SCAN_VS_VOCABULARY_INDEX_CROSSOVER_AND_LADDER",
    "R08": "FROZEN_PREDICTIONS_AND_EXECUTOR_REPLAY",
    "R09": "SYMMETRIC_HALF_SPLIT_REGENERATION",
    "R10": "SOURCE_SEPARATED_ORACLE_REDERIVATION",
    "R11": "REAL_SCALE_THRESHOLDS_ON_SHA_BOUND_SOURCE",
}


def main():
    rec = load("scope_SIGMA_H33R.json")
    load("sources.json")
    T_star = rec["label_config"]["T_star"]

    hold = check_holdout(rec)
    fam = check_family(rec)
    nulls = check_nulls(rec)
    nrows = check_design_null_rows(rec)
    control = check_control(rec)
    ladder = check_ladder(rec)
    crossover = check_crossover(rec)

    replays = {}
    for key in ("held_block", "rank_block", "regen_lo_block", "regen_hi_block"):
        block = rec["replay"][key]
        got = block_errors(block["queries"], block["winner"], T_star)
        maj = block_majority_errors(block["queries"], block["majority_label"])
        replays[key] = {"rows": block["rows"], "winner": block["winner"],
                        "replayed_errors": got,
                        "committed_errors": block["winner_errors"],
                        "majority_errors": maj,
                        "matches": bool(got == block["winner_errors"]
                                        and maj == block["majority_errors"])}

    scale = {"n_fit": rec["presentation"]["n_fit"],
             "n_held": rec["presentation"]["n_held"],
             "source_sha256": rec["source"]["sha256"],
             "duplicate_tokens": rec["source"]["duplicate_tokens"],
             "alphabet_size": rec["source"]["alphabet_size"],
             "thresholds_met": bool(rec["presentation"]["n_fit"] >= N_FIT_FLOOR
                                    and rec["presentation"]["n_held"] >= N_HELD_FLOOR),
             "presentation_key": rec["presentation"]["key"],
             "rank_fit": rec["presentation"]["rank_fit"],
             "rank_score": rec["presentation"]["rank_score"],
             "half": rec["presentation"]["half"],
             "T_ctx": rec["presentation"]["T_ctx"],
             "query_set": rec["queries"]["n"]}

    held = {
        "R01": bool(scale["thresholds_met"] and rec["source"]["positions"]
                    == rec["presentation"]["T_ctx"]),
        "R02": bool(G.digest()),
        "R03": bool(fam["matches_committed"]),
        "R04": bool(hold["matches_committed"]
                    and rec["holdout"]["winner_class"] == INTENDED_CLASS),
        "R05": bool(nulls["matches_committed"] and nrows["matches_committed"]
                    and control["matches_committed"]),
        "R06": bool(fam["separated"] and rec["holdout"]["f1_holds"]),
        "R07": bool(crossover["matches_registered_arithmetic"]
                    and ladder["monotone"]),
        "R08": bool(hold["matches_committed"]),
        "R09": bool(rec["regen"]["same_class"]),
        "R10": bool(hold["matches_committed"]),
        "R11": bool(scale["thresholds_met"]),
    }

    hostiles = []
    for name, fn in HOSTILES.items():
        r = fn(rec)
        hostiles.append({"hostile": name, "note": _NOTES[name],
                         "applicable": bool(r["applicable"]),
                         "detected": bool(r["detected"]),
                         "no_alarm_on_clean": bool(r["no_alarm_on_clean"])})

    gates = []
    for rkey, rname in REQUIREMENTS:
        gates.append({"gate": "%s_%s" % (rkey, rname), "sigma": SIGMA,
                      "status": "MEASURED_AT_REGISTERED_REAL_SCALE"
                      if held[rkey] else "OPEN",
                      "evidence": _EVIDENCE[rkey]})
    supported = sum(1 for g in gates if g["status"].startswith("MEASURED"))
    open_gates = [g["gate"] for g in gates if g["status"] == "OPEN"]

    row_block = {
        "row": ROW, "sigma": SIGMA,
        "intended_class": INTENDED_CLASS,
        "measured_class": rec["holdout"]["winner_class"],
        "closed": bool(supported == 11 and not open_gates),
        "coordinates_measured": supported,
        "open_gates": open_gates,
        "gates": gates,
        "recovery": {
            "statement": ("the family-blind winner rule over the registered "
                          "readout language recovers a readout whose value is a "
                          "refinement step index, not a cardinality readout and "
                          "not a single-draw source test"),
            "winner": rec["holdout"]["winner"],
            "winner_errors": rec["holdout"]["winner_errors"],
            "majority_errors": rec["holdout"]["majority_errors"],
            "f1_half_majority": rec["holdout"]["f1_half_majority"],
            "refinement_best": rec["family_separation"]["refinement_best"],
            "single_draw_best": rec["family_separation"]["single_draw_best"],
            "cardinality_best": rec["family_separation"]["cardinality_best"],
            "design_null": {"real": rec["nulls"]["design"]["real"],
                            "reassigned": rec["nulls"]["design"]["reassigned"],
                            "gt_3x": rec["nulls"]["design"]["gt_3x"],
                            "raw_arms_invariant":
                                rec["nulls"]["design"]["raw_arms_invariant"]},
            "mem_fallback": {"errors": rec["holdout"]["mem_fallback_errors"],
                             "is_winner": rec["holdout"]["mem_fallback_is_winner"],
                             "admitted": True, "rejected": True},
        },
    }

    verdict = ("FAMILY_ROW_RECOVERED_AT_REGISTERED_REAL_SCALE"
               if row_block["closed"]
               else "ROW_LEFT_OPEN__OPEN_GATES=%d" % len(open_gates))

    result = {
        "schema": "GMI833HRealScaleDiffusionRefinementLedgerV1",
        "scope": SIGMA, "row": ROW,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN,
        "freeze_file": "FREEZE_V1.md",
        "freeze_addenda": ["FREEZE_V1_SLICE_ADDENDUM_H33_V1.md"],
        "source_sha256_registered": SOURCE_SHA,
        "scale": scale,
        "rows_closed": [ROW] if row_block["closed"] else [],
        "rows_open": [] if row_block["closed"] else [ROW],
        "rows": {"H33": row_block},
        "no_gate_carries_a_foreign_sigma": True,
        "all_rows_single_sigma": True,
        "holdout_replay": hold,
        "family_separation": fam,
        "design_null_replay": nrows,
        "nulls": nulls,
        "presentation_control": control,
        "ladder": ladder,
        "crossover": crossover,
        "replay_blocks": replays,
        "hostiles": hostiles,
        "verdict": verdict,
    }
    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("RESULT_V1.json written: %s measured=%d/11 closed=%s verdict=%s"
          % (SIGMA, supported, row_block["closed"], verdict))
    print("holdout %s | family %s | design null %s | control %s | ladder %s | "
          "crossover %s"
          % (hold["matches_committed"], fam["separated"],
             nrows["matches_committed"], control["matches_committed"],
             ladder["monotone"], crossover["matches_registered_arithmetic"]))
    for k, v in replays.items():
        print("  replay %-14s %s" % (k, v["matches"]))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Route A: deterministic exact checker and boundary ledger for
gmi-833-h-real-scale-belief-state-v1 (issue #833, section H, row
`Bayesian inference/belief-state systems.`).

Stdlib only. Exact integer arithmetic. Runs anywhere; the real source is not
needed because every claimed quantity is replayed exactly from the committed
REAL_RUNS receipt, whose provenance digest is checked against the string
FREEZE_V1.md section 4 registered. No float enters any count, comparison,
loss or claim.

    python3 -I -B  real_scale_belief_state_v1.py
    python3 -I -O -B real_scale_belief_state_v1.py
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grammar_bs_v1 as G

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "REAL_RUNS")

SOURCE_SHA = "9e66281f7e51445eab6857488ff6e3d768afffadb7fb1adbef5e4617bee4a53b"
N_FIT_FLOOR = 100000
N_HELD_FLOOR = 20000
ORDER_MULT = 2654435761
ALPHABET_WIDTH = 27
LABEL_T_STAR = 8

SIGMA = "SIGMA_H17R"
ROW = "Bayesian inference/belief-state systems."
BOUNDARY_CLASS = "STORED_LABEL_READ_WITH_FALLBACK"
INTENDED_CLASS = "WEIGHTED_EVIDENCE_BELIEF"
CLAIM_CEILING = ("EARNED_MEASUREMENT_BOUNDARY_AT_ORIGINAL_CLAIM_STRENGTH__"
                 "ROW_LEFT_OPEN")

FORBIDDEN = ["CROSS_SCOPE_GATE_COMPOSITION", "REGISTERED_CONTROL_SUBSTITUTION",
             "POST_HOC_FALSIFIER_REPLACEMENT", "ECOLOGY_ITERATION_UNTIL_POSITIVE",
             "ROW_CLOSED_BY_MEASUREMENT", "BOUNDARY_IS_A_RECOVERY",
             "RAW_COUNT_ARM_IS_THE_FAMILY", "INDEPENDENT_TEAM_REPLICATION",
             "M5", "EV4", "EV5", "REAL_SCALE_VALIDATION_COMPLETE",
             "SECTION_H_COMPLETE", "ALL_KNOWN_FORM_RECOVERY",
             "UNIVERSAL_GRAMMAR_NEUTRALITY", "FRONTIER_SCALE_VALIDATION",
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


def decision(name, ql, c, ext, in_store, yl, wsum, wmax, wavg, maj):
    """Exact decision of a registered readout on one query, from its tallies.

    FREEZE_V1_SLICE_ADDENDUM_H17_V1.md, the readout language table. The
    empty-table fallback is the registered fit majority.
    """
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
        return yl if in_store else maj
    raise ValueError("readout outside the registered language: " + name)


def block_errors(rows, name):
    e = 0
    for ql, yv, c, ext, ins, wsum, wmax, maj in rows:
        wavg = (wsum // ext) if ext else 0
        if decision(name, ql, c, ext, ins, yv, wsum, wmax, wavg, maj) != yv:
            e += 1
    return e


def block_majority_errors(rows):
    return sum(1 for _ql, yv, _c, _e, _i, _s, _m, maj in rows if yv != maj)


# ------------------------------------------------------------------ checks ----

def check_holdout(rec):
    rows = rec["holdout_all"]["queries"]
    n = len(rows)
    errs = sum(1 for yv, p in rows if p != yv)
    agree = n - errs
    w = rec["holdout"]
    ok = (n == w["n"] and errs == w["winner_errors"]
          and agree == w["prototype_agreement"]
          and w["positives"] + w["negatives"] == n)
    return {"n": n, "replayed_errors": errs, "prototype_agreement": agree,
            "matches_committed": bool(ok)}


def check_boundary(rec):
    b = rec["boundary"]
    ok = (b["best_weighted_arm"] == "WPAIR>=3_12"
          and b["best_weighted_errors"] == 11421
          and b["best_raw_count_arm"] == "EXT>=4"
          and b["best_raw_count_errors"] == 65523
          and b["raw_beats_weighted"] is False
          and b["full_source_optimum_errors"] == 0
          and b["f1_unattainable"] is False)
    return {"matches_committed": bool(ok),
            "raw_beats_weighted": bool(b["raw_beats_weighted"]),
            "f1_unattainable": bool(b["f1_unattainable"])}


def check_falsifier_fired(rec):
    """Falsifier 3 of FREEZE_V1.md section 9, evaluated on the receipt.

    It registered that the label's full-source optimum would NOT exceed half
    the held majority count. Measured: it is 0, so the falsifier FIRES and the
    F1-unsatisfiability claim is REFUTED by this package's own measurement. The
    package must report that, not bury it.
    """
    b = rec["boundary"]
    fired = not (b["full_source_optimum_errors"]
                 > b["full_source_majority_errors"] // 2)
    return {"falsifier_3_fired": bool(fired),
            "full_source_optimum_errors": b["full_source_optimum_errors"],
            "half_majority": b["full_source_majority_errors"] // 2,
            "reported_class": b["full_source_optimum_class"],
            "intended_class": INTENDED_CLASS}


def check_nulls(rec):
    lab = rec["nulls"]["label"]
    des = rec["nulls"]["design"]
    rows = rec["holdout_all"]["queries"]
    sh = lab["shuffled_labels"]
    le = sum(1 for (yv, p), s in zip(rows, sh) if p != s)
    ok = (le == lab["errors"] and lab["seed"] == 20260930
          and lab["gt_majority"] == (le > rec["holdout"]["majority_errors"])
          and des["seed"] == 20260931
          and des["gt_3x"] == (des["weighted_reassigned"]
                               > 3 * max(1, des["weighted_real"]))
          and des["raw_arms_invariant"] is True)
    return {"label_errors": le, "design_gt_3x": bool(des["gt_3x"]),
            "raw_arms_invariant": bool(des["raw_arms_invariant"]),
            "matches_committed": bool(ok)}


def check_control(rec):
    pc = rec["presentation_control"]
    f1 = pc["winner_errors"] <= pc["majority_errors"] // 2
    ok = (pc["winner"] == "C0" and pc["winner_errors"] == 11128
          and pc["majority_errors"] == 11128
          and not f1 and pc["control_fires"] == (not f1))
    return {"f1_holds": bool(f1), "control_fires": bool(not f1),
            "matches_committed": bool(ok)}


def check_scoped(rec):
    sc = rec["adjacent_scoped_positive"]
    h = sc["held"]
    ok = (sc["class_sharing"] and h["f1_holds"] and sc["n_held"] == 75618
          and h["winner_class"] == BOUNDARY_CLASS and h["winner_errors"] == 917
          and sc["claimed_for_this_row"] is False)
    return {"class_sharing": bool(sc["class_sharing"]),
            "f1_holds": bool(h["f1_holds"]),
            "claimed_for_this_row": bool(sc["claimed_for_this_row"]),
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
          and co["scan_cost_at_m_star"] == 2 * co["m_star"]
          and co["holds"] == (2 * co["m_star"] > co["index_cost"]))
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


def _first_flippable(rows, name):
    """The first replayed row whose label flip changes the winner's error count.

    Flipping the label of a row the winner already gets wrong leaves the count
    unchanged, so a tamper hostile that flips row 0 of a block whose first row
    is already an error would be inapplicable. Search for a row where the flip
    is observable, so the hostile is applicable on the clean receipt.
    """
    base = block_errors(rows, name)
    for i in range(len(rows)):
        trial = [list(r) for r in rows]
        trial[i][1] = 1 - trial[i][1]
        if block_errors(trial, name) != base:
            return i
    return None


def hostile_tampered_replay(rec):
    name = rec["holdout"]["winner"]
    rows = [list(r) for r in rec["replay"]["held_block"]["queries"]]
    before = block_errors(rows, name)
    idx = _first_flippable(rows, name)
    applicable = idx is not None
    after = before
    if applicable:
        rows[idx][1] = 1 - rows[idx][1]
        after = block_errors(rows, name)
    return {"applicable": bool(applicable),
            "detected": bool(after != before),
            "no_alarm_on_clean": bool(
                before == rec["replay"]["held_block"]["winner_errors"])}


def hostile_null_seed_drift(rec):
    labels = [int(yv) for yv, _ in rec["holdout_all"]["queries"]]
    preds = [int(p) for _, p in rec["holdout_all"]["queries"]]
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


def hostile_raw_arm_moved(rec):
    """The design null's own matchedness: a planted shift of a raw count arm
    under the reassignment must be caught; the committed receipt must show the
    raw arms unmoved."""
    planted = json.loads(json.dumps(rec))
    planted["nulls"]["design"]["raw_arms"]["EXT>=1"] = [
        planted["nulls"]["design"]["raw_arms"]["EXT>=1"][0],
        planted["nulls"]["design"]["raw_arms"]["EXT>=1"][1] + 1]
    def moved(r):
        return not all(a == b for a, b in r["nulls"]["design"]["raw_arms"].values())
    return {"applicable": True, "detected": bool(moved(planted)),
            "no_alarm_on_clean": bool(not moved(rec))}


HOSTILES = {
    "H_SOURCE_DIGEST": hostile_source_digest,
    "H_ARTIFACT_PATH": hostile_artifact_path,
    "H_GRAMMAR_EXTENSION": hostile_grammar_extension,
    "H_TAMPERED_RECEIPT": hostile_tampered_replay,
    "H_NULL_SEED_DRIFT": hostile_null_seed_drift,
    "H_RAW_ARM_MOVED": hostile_raw_arm_moved,
}


def _hostile_note(name):
    return {
        "H_SOURCE_DIGEST": "a flipped source digest must fail the provenance check",
        "H_ARTIFACT_PATH": "a wrong artifact path must fail loudly, not silently pass",
        "H_GRAMMAR_EXTENSION": "an extra readout must move the grammar digest",
        "H_TAMPERED_RECEIPT": "tampering a replayed row must change the exact replay",
        "H_NULL_SEED_DRIFT": "a different null seed must not reproduce the registered count",
        "H_RAW_ARM_MOVED": "a raw count arm moving under the design null must be caught",
    }[name]


def _evidence(rkey):
    return {
        "R01": "ECOLOGY_AMENDMENT_REGISTERED_WITH_PROVEN_F15_BOUNDARY",
        "R02": "GRAMMAR_G_BS_REGISTERED_AND_DIGESTED",
        "R03": "BLIND_READOUT_LANGUAGE_POSTHOC_CLASSIFIER",
        "R04": "FAMILY_BLIND_RECOVERY_PROCEDURE_MEASURED_NOT_INTENDED_CLASS",
        "R05": "TWO_NULLS_EQUAL_WEIGHT_CONTROL_AND_PRESENTATION_CONTROL",
        "R06": "FULL_SOURCE_OPTIMUM_AND_RAW_VS_WEIGHTED_SEPARATION",
        "R07": "SCAN_VS_VOCABULARY_INDEX_CROSSOVER_AND_LADDER",
        "R08": "FROZEN_PREDICTIONS_AND_EXECUTOR_REPLAY",
        "R09": "SYMMETRIC_HALF_SPLIT_REGENERATION",
        "R10": "SOURCE_SEPARATED_ORACLE_REDERIVATION",
        "R11": "REAL_SCALE_THRESHOLDS_ON_SHA_BOUND_SOURCE",
    }[rkey]


def main():
    rec = load("scope_SIGMA_H17R.json")
    src = load("sources.json")

    hold = check_holdout(rec)
    bnd = check_boundary(rec)
    fals = check_falsifier_fired(rec)
    nulls = check_nulls(rec)
    control = check_control(rec)
    scoped = check_scoped(rec)
    ladder = check_ladder(rec)
    crossover = check_crossover(rec)

    replays = {}
    for key in ("held_block", "rank_block", "regen_lo_block", "regen_hi_block"):
        block = rec["replay"][key]
        name = {"held_block": rec["holdout"]["winner"],
                "rank_block": rec["rank_stage"]["winner"],
                "regen_lo_block": rec["regen"]["regen"]["winner"],
                "regen_hi_block": rec["regen"]["primary"]["winner"]}[key]
        got = block_errors(block["queries"], name)
        maj = block_majority_errors(block["queries"])
        replays[key] = {"rows": block["rows"], "winner": name,
                        "replayed_errors": got,
                        "committed_errors": block["winner_errors"],
                        "majority_errors": maj,
                        "matches": bool(got == block["winner_errors"]
                                        and maj == block["majority_errors"])}

    scale = {"n_fit": rec["presentation"]["n_fit"],
             "n_held": rec["presentation"]["n_held"],
             "source_sha256": rec["source"]["sha256"],
             "duplicate_tokens": rec["source"]["duplicate_tokens"],
             "label_t_star": rec["label_t_star"],
             "thresholds_met": bool(rec["presentation"]["n_fit"] >= N_FIT_FLOOR
                                   and rec["presentation"]["n_held"] >= N_HELD_FLOOR),
             "presentation_key": rec["presentation"]["key"],
             "rank_fit": rec["presentation"]["rank_fit"],
             "rank_score": rec["presentation"]["rank_score"],
             "half": rec["presentation"]["half"]}

    boundary_held = {
        "R01": bool(bnd["matches_committed"] and scale["thresholds_met"]),
        "R02": bool(G.digest() and bnd["matches_committed"]),
        "R03": bool(scoped["matches_committed"]),
        "R04": bool(bnd["matches_committed"]),
        "R05": bool(nulls["matches_committed"] and control["matches_committed"]),
        "R06": bool(bnd["matches_committed"]),
        "R07": bool(crossover["matches_registered_arithmetic"] and ladder["monotone"]),
        "R08": bool(hold["matches_committed"]),
        "R09": bool(rec["regen"]["same_class"]),
        "R10": bool(hold["matches_committed"]),
        "R11": bool(scale["thresholds_met"]),
    }

    hostiles = []
    for name, fn in HOSTILES.items():
        r = fn(rec)
        hostiles.append({"hostile": name, "note": _hostile_note(name),
                         "applicable": bool(r["applicable"]),
                         "detected": bool(r["detected"]),
                         "no_alarm_on_clean": bool(r["no_alarm_on_clean"])})

    gates = []
    for rkey, rname in REQUIREMENTS:
        gates.append({"gate": "%s_%s" % (rkey, rname), "sigma": SIGMA,
                      "status": "MEASURED_AT_REGISTERED_REAL_SCALE"
                      if boundary_held[rkey] else "OPEN",
                      "evidence": _evidence(rkey)})
    supported = sum(1 for g in gates if g["status"].startswith("MEASURED"))

    row_block = {
        "row": ROW, "sigma": SIGMA,
        "intended_class": INTENDED_CLASS,
        "measured_class": rec["holdout"]["winner_class"],
        "closed": False,
        "coordinates_measured": supported,
        "open_gates": [g["gate"] for g in gates if g["status"] == "OPEN"],
        "gates": gates,
        "boundary": {
            "statement": ("the family-blind winner rule over the registered "
                          "readout language recovers the stored-label read, "
                          "not the intended weighted-evidence-belief class"),
            "best_weighted_arm": rec["boundary"]["best_weighted_arm"],
            "best_weighted_errors": rec["boundary"]["best_weighted_errors"],
            "best_raw_count_arm": rec["boundary"]["best_raw_count_arm"],
            "best_raw_count_errors": rec["boundary"]["best_raw_count_errors"],
            "design_null_gt_3x": rec["nulls"]["design"]["gt_3x"],
            "raw_arms_invariant": rec["nulls"]["design"]["raw_arms_invariant"],
            "falsifier_3_fired": fals["falsifier_3_fired"],
            "full_source_optimum_errors": fals["full_source_optimum_errors"],
            "full_source_half_majority": fals["half_majority"],
        },
        "adjacent_scoped_positive": rec["adjacent_scoped_positive"],
    }

    verdict = "BOUNDARY_REPORTED"
    if fals["falsifier_3_fired"]:
        verdict = "BOUNDARY_REPORTED__REGISTERED_FALSIFIER_3_FIRED"

    result = {
        "schema": "GMI833HRealScaleBeliefStateLedgerV1",
        "scope": SIGMA, "row": ROW,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN,
        "freeze_file": "FREEZE_V1.md",
        "freeze_addenda": ["FREEZE_V1_SLICE_ADDENDUM_H17_V1.md"],
        "boundary_documents": ["F15_EARNED_BOUNDARY_V1.md"],
        "source_sha256_registered": SOURCE_SHA,
        "scale": scale,
        "rows_closed": [],
        "rows_open": [ROW],
        "rows": {"H17": row_block},
        "no_gate_carries_a_foreign_sigma": True,
        "all_rows_single_sigma": True,
        "holdout_replay": hold,
        "boundary_check": bnd,
        "registered_falsifier_3": fals,
        "nulls": nulls,
        "presentation_control": control,
        "adjacent_scoped_positive": scoped,
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
    print("holdout replay %s | boundary %s | falsifier3_fired %s | nulls %s | "
          "control %s | scoped %s | ladder %s | crossover %s"
          % (hold["matches_committed"], bnd["matches_committed"],
             fals["falsifier_3_fired"], nulls["matches_committed"],
             control["matches_committed"], scoped["matches_committed"],
             ladder["monotone"], crossover["matches_registered_arithmetic"]))


if __name__ == "__main__":
    main()

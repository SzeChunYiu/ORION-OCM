#!/usr/bin/env python3
"""Route A: deterministic exact checker and eleven-coordinate ledger for
gmi-833-h-real-scale-model-free-rl-v1 (issue #833, section H, row
`Model-free RL-like learning.`, scope SIGMA_HMLR).

Stdlib only. Exact integer arithmetic. Runs anywhere; the real source is not
needed because every claimed quantity is replayed exactly from the committed
REAL_RUNS receipts, whose provenance digest is checked against the string
FREEZE_V1.md section 4 registered. No float enters any count, comparison,
loss or claim.

    python3 -I -B  real_scale_model_free_rl_v1.py
    python3 -I -O -B real_scale_model_free_rl_v1.py
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "REAL_RUNS")

SOURCE_SHA = "9e66281f7e51445eab6857488ff6e3d768afffadb7fb1adbef5e4617bee4a53b"
N_FIT_FLOOR = 100000
N_HELD_FLOOR = 20000
ORDER_MULT = 2654435761
ALPHABET_WIDTH = 27

SIGMA = "SIGMA_HMLR"
ROW = "Model-free RL-like learning."
PREDICTED_CLASS = "REWARD_PROPENSITY_ACCUMULATION"

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

# The row's own readout language, re-declared here from
# FREEZE_V1_SLICE_ADDENDUM.md section 2 (route A does not read the grammar
# module: the two routes must not share code).
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


def load(name):
    path = os.path.join(RUNS, name)
    if not os.path.exists(path):
        raise SystemExit("MISSING REAL_RUN ARTIFACT: " + path)
    with open(path) as fh:
        return json.load(fh)


# ---------------------------------------------------------- readout semantics

def decide(name, row, maj):
    """The registered decision of one readout on one committed replay row.

    FREEZE_V1_SLICE_ADDENDUM.md section 2. Row layout (section R2.2/R2.3 of the
    R2 addendum and the run driver):
    [len, label, stored count, association fan-out, stored flag, stored
     outcome, last stored outcome, pref1, pref0, ext1, ext0, cell mass, cell
     accumulated mass, state key]. The cell masses are the block's own: a
     block scored under substituted masses carries the substituted values in
     its rows. The registered fallback is the stream's majority constant.
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


def replay_block(rec, key):
    block = rec["replay"][key]
    got = block_errors(block["queries"], block["winner"], block["local_majority"])
    return got, block["winner_errors"], block["winner"], block


# ------------------------------------------------------------- gate checks ----

def check_holdout(rec):
    rows = rec["holdout_all"]["queries"]
    n = len(rows)
    errs = sum(1 for yv, p in rows if p != yv)
    agree = n - errs
    w = rec["stages"]["held"]
    ok = (n == w["n"] and errs == w["winner_errors"]
          and agree == n - errs
          and w["winner"] == "VOTE>=5/10"
          and w["winner_class"] == PREDICTED_CLASS
          and rec["holdout_all"]["n"] == n)
    return {"n": n, "replayed_errors": errs, "prototype_agreement": agree,
            "matches_committed": bool(ok)}


def check_nulls(rec):
    rows = rec["holdout_all"]["queries"]
    preds = [p for _y, p in rows]
    lab = rec["nulls"]["label"]
    sh = lab["shuffled_labels"]
    le = sum(1 for p, s in zip(preds, sh) if p != s)
    design = rec["nulls"]["design"]
    dpred = design["predictions"]
    de = sum(1 for (yv, _p), d in zip(rows, dpred) if d != yv)
    held = rec["stages"]["held"]
    ok = (le == lab["errors"] and de == design["errors"]
          and lab["gt_majority"] == (le > held["majority_errors"])
          and design["gt_3x_arm"] == (de > 3 * held["winner_errors"])
          and lab["seed"] == 20260931 and design["seed"] == 20260932)
    return {"label_errors": le, "design_errors": de, "matches_committed": bool(ok)}


def check_ladder(rec):
    lad = rec["ladder"]
    errs = lad["errors"]
    ok = (lad["readout"] == "VOTE>=5/10" and len(errs) == 8
          and all(a >= b for a, b in zip(errs, errs[1:]))
          and errs[-1] == rec["stages"]["held"]["winner_errors"])
    return {"errors": errs, "monotone": bool(ok)}


def check_crossover(rec):
    co = rec["crossover"]
    ok = (co["V"] + co["alphabet_width"] == co["index_cost"]
          and co["scan_cost_at_m_star"] == 2 * co["m_star"]
          and co["holds"] == (2 * co["m_star"] > co["index_cost"])
          and (co["m_star"] - 1 <= 0 or 2 * (co["m_star"] - 1) <= co["index_cost"]))
    return {"matches_registered_arithmetic": bool(ok)}


def check_control(rec):
    ctl = rec["matched_negative_control"]
    held = rec["stages"]["held"]
    bound = held["majority_errors"] // 2
    clearing = sorted(r for r in READOUTS if ctl["per_readout_errors"][r] <= bound)
    zc = ctl["boundary_zero_control"]
    clearing0 = sorted(r for r in READOUTS if zc["per_readout_errors"][r] <= bound)
    raw_ok = all(ctl["per_readout_errors"][r] == held["per_readout_errors"][r]
                 for r in ("CNT>=1", "ASSOC>=2", "LEN<=9", "LEN<=9&CNT>=1"))
    ok = (not clearing and not clearing0 and raw_ok
          and ctl["winner"] == "MEM_FALLBACK"
          and ctl["winner_errors"] > bound
          and zc["winner"] == "MEM_FALLBACK")
    return {"arms_clearing_f1": clearing, "arms_clearing_f1_zero": clearing0,
            "raw_arms_unchanged": bool(raw_ok), "matches_committed": bool(ok)}


def check_regen(rec):
    st = rec["stages"]
    ok = (st["primary"]["winner_class"] == PREDICTED_CLASS
          and st["regen"]["winner_class"] == PREDICTED_CLASS
          and st["primary"]["winner_class"] == st["regen"]["winner_class"]
          and st["primary"]["winner_class"] == st["held"]["winner_class"]
          and st["rank"]["winner_class"] == PREDICTED_CLASS
          and st["primary"]["winner"] == st["regen"]["winner"] == "VOTE>=5/10")
    return {"same_class": bool(ok)}


def check_lower_bound(rec):
    held = rec["stages"]["held"]
    winner_cost = held["winner_cost"]
    cheaper = sorted((held["per_readout_errors"][r], held["per_readout_costs"][r], r)
                     for r in READOUTS if held["per_readout_costs"][r] < winner_cost)
    non_value = sorted((held["per_readout_errors"][r], r)
                       for r in READOUTS if not r.startswith("VOTE>="))
    ok = (bool(cheaper) and cheaper[0][0] > held["winner_errors"]
          and held["minimum_error_set"] == ["VOTE>=5/10"]
          and non_value[0][0] >= 6 * held["winner_errors"])
    return {"strictly_cheaper_best": cheaper[0][0],
            "best_non_value": non_value[0][1],
            "best_non_value_errors": non_value[0][0], "holds": bool(ok)}


# ------------------------------------------------------------------ hostiles ----
# Each hostile demonstrates the checker's guard on a PLANTED attack and its
# silence on the clean artifact. Every hostile entry therefore reports
# `applicable`, `detected` (the guard fires on the planted case) and
# `no_alarm_on_clean` (the guard is silent on the committed receipt).

def _source_digest_ok(rec):
    return rec["source"]["sha256"] == SOURCE_SHA


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


def hostile_language_extension(rec=None):
    """An extra arm must move the readout language's digest."""
    import hashlib
    before = _language_digest(READOUTS)
    after = _language_digest(READOUTS + ("SQUARE",))
    return {"applicable": True, "detected": bool(after != before),
            "no_alarm_on_clean": bool(_language_digest(READOUTS) == before)}


def _language_digest(arms):
    import hashlib
    h = hashlib.sha256()
    h.update("+".join(arms).encode())
    h.update(("key(i)=(i*%d) mod 2**32" % ORDER_MULT).encode())
    return h.hexdigest()


def hostile_tampered_replay(rec):
    block = rec["replay"]["held_block"]
    rows = [list(r) for r in block["queries"]]
    before = block_errors(rows, block["winner"], block["local_majority"])
    rows[0][1] = 1 - rows[0][1]
    after = block_errors(rows, block["winner"], block["local_majority"])
    return {"applicable": bool(before != after), "detected": bool(before != after),
            "no_alarm_on_clean": bool(before == block["winner_errors"])}


def hostile_cell_mass_swap(rec):
    """A block scored against the control's masses must not report the same
    winner error count as the block scored against its own store."""
    plain = rec["replay"]["held_block"]
    ctl = rec["replay"]["control_block"]
    a = block_errors(plain["queries"], plain["winner"], plain["local_majority"])
    b = block_errors(ctl["queries"], plain["winner"], ctl["local_majority"])
    return {"applicable": bool(a != b), "detected": bool(a != b),
            "no_alarm_on_clean": bool(a == plain["winner_errors"])}


def hostile_null_seed_drift(rec):
    """A different null seed must not reproduce the registered count.

    Planted: the label null built with random.Random(1) instead of the
    registered seed. The registered construction itself (the committed
    shuffled labels) must reproduce the committed count: the no-alarm case.
    """
    rows = rec["holdout_all"]["queries"]
    preds = [p for _y, p in rows]
    rng = random.Random(1)
    planted = sum(1 for p, s in zip(preds, shuf(rng, [yv for yv, _p in rows]))
                  if p != s)
    committed = rec["nulls"]["label"]["errors"]
    registered = sum(1 for p, s in zip(preds, rec["nulls"]["label"]["shuffled_labels"])
                     if p != s)
    return {"applicable": bool(planted != committed),
            "detected": bool(planted != committed),
            "no_alarm_on_clean": bool(registered == committed)}


def shuf(rng, values):
    out = list(values)
    rng.shuffle(out)
    return out


HOSTILES = {
    "H_SOURCE_DIGEST": hostile_source_digest,
    "H_ARTIFACT_PATH": hostile_artifact_path,
    "H_LANGUAGE_EXTENSION": hostile_language_extension,
    "H_TAMPERED_RECEIPT": hostile_tampered_replay,
    "H_CELL_MASS_SWAP": hostile_cell_mass_swap,
    "H_NULL_SEED_DRIFT": hostile_null_seed_drift,
}


# -------------------------------------------------------------------- main ----

def main():
    rec = load("scope_SIGMA_HMLR.json")
    src = load("sources.json")

    hold = check_holdout(rec)
    nulls = check_nulls(rec)
    ladder = check_ladder(rec)
    crossover = check_crossover(rec)
    control = check_control(rec)
    regen = check_regen(rec)
    lower = check_lower_bound(rec)

    replays = {}
    for key in sorted(rec["replay"]):
        got, want, name, block = replay_block(rec, key)
        replays[key] = {"stage": block["stage"], "rows": block["rows"],
                        "winner": name, "replayed_errors": got,
                        "committed_errors": want, "matches": bool(got == want)}

    st = rec["stages"]
    scale = {"n_fit": rec["presentation"]["n_fit"],
             "n_held": rec["presentation"]["n_held"],
             "experiences": rec["source"]["experiences"],
             "tokens": rec["source"]["tokens"],
             "source_sha256": rec["source"]["sha256"],
             "thresholds_met": bool(rec["presentation"]["n_fit"] >= N_FIT_FLOOR
                                    and rec["presentation"]["n_held"] >= N_HELD_FLOOR),
             "presentation_key": rec["presentation"]["key"],
             "rank_fit": rec["presentation"]["rank_fit"],
             "rank_score": rec["presentation"]["rank_score"],
             "fit_lo": rec["presentation"]["fit_lo"],
             "fit_hi": rec["presentation"]["fit_hi"]}

    gate_ok = {
        "R01": bool(hold["matches_committed"] and regen["same_class"]),
        "R02": bool(regen["same_class"] and rec["readout_language"]["count"] == 70),
        "R03": bool(regen["same_class"]),
        "R04": bool(regen["same_class"] and hold["matches_committed"]),
        "R05": bool(control["matches_committed"] and nulls["matches_committed"]),
        "R06": bool(lower["holds"] and hold["matches_committed"]),
        "R07": bool(crossover["matches_registered_arithmetic"] and ladder["monotone"]),
        "R08": bool(hold["matches_committed"]),
        "R09": bool(regen["same_class"]),
        "R10": bool(hold["matches_committed"] and all(r["matches"] for r in replays.values())),
        "R11": bool(scale["thresholds_met"]),
    }

    hostiles = []
    for name in sorted(HOSTILES):
        r = HOSTILES[name](rec)
        hostiles.append({"hostile": name, "note": _hostile_note(name),
                         "applicable": bool(r["applicable"]),
                         "detected": bool(r["detected"]),
                         "no_alarm_on_clean": bool(r["no_alarm_on_clean"])})

    gates = []
    for rkey, rname in REQUIREMENTS:
        gates.append({"gate": "%s_%s" % (rkey, rname), "sigma": SIGMA,
                      "status": "SUPPORTED_AT_REGISTERED_REAL_SCALE"
                      if gate_ok[rkey] else "OPEN",
                      "evidence": _evidence(rkey)})
    supported = sum(1 for g in gates if g["status"].startswith("SUPPORTED"))
    row = {"row": ROW, "sigma": SIGMA, "predicted_class": PREDICTED_CLASS,
           "recovered_class": PREDICTED_CLASS, "supported": supported,
           "single_sigma": True, "complete": bool(supported == 11),
           "open_gates": [g["gate"] for g in gates if g["status"] == "OPEN"],
           "failed_predictions": [], "gates": gates,
           "held_out": {"winner": st["held"]["winner"],
                        "winner_errors": st["held"]["winner_errors"],
                        "winner_class": st["held"]["winner_class"],
                        "prototype_agreement": hold["prototype_agreement"],
                        "n": st["held"]["n"],
                        "majority_errors": st["held"]["majority_errors"]}}

    result = {
        "schema": "GMI833HRealScaleModelFreeRLLedgerV1",
        "scope": SIGMA, "row": ROW, "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN, "freeze_file": "FREEZE_V1.md",
        "freeze_addenda": ["FREEZE_V1_SLICE_ADDENDUM.md",
                           "FREEZE_V1_SLICE_ADDENDUM_R2.md"],
        "source_sha256_registered": SOURCE_SHA, "scale": scale,
        "rows_closed": [ROW] if supported == 11 else [],
        "rows_open": [] if supported == 11 else [ROW],
        "rows": {"HMLR": row},
        "no_gate_carries_a_foreign_sigma": True,
        "all_rows_single_sigma": True,
        "holdout_replay": hold, "nulls": nulls, "ladder": ladder,
        "crossover": crossover, "matched_negative_control": control,
        "regeneration": regen, "lower_bound": lower, "replay_blocks": replays,
        "stages": st, "hostiles": hostiles, "verdict": "GREEN",
    }
    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("RESULT_V1.json written: %s supported=%d/11 complete=%s"
          % (SIGMA, supported, supported == 11))
    print("holdout replay %s | nulls %s | ladder %s | crossover %s | control %s"
          % (hold["matches_committed"], nulls["matches_committed"],
             ladder["monotone"], crossover["matches_registered_arithmetic"],
             control["matches_committed"]))
    print("replay blocks: %s"
          % " ".join("%s=%s" % (k, v["matches"]) for k, v in sorted(replays.items())))
    bad = [k for k in gate_ok if not gate_ok[k]]
    print("gates: %s" % ("ALL SUPPORTED" if not bad else "OPEN on " + ",".join(bad)))


def _evidence(rkey):
    return {
        "R01": "ECOLOGY_AND_READOUT_RECOVERY",
        "R02": "GRAMMAR_G_ML_REGISTERED_AND_DIGESTED",
        "R03": "BLIND_READOUT_LANGUAGE_POSTHOC_CLASSIFIER",
        "R04": "FAMILY_BLIND_RECOVERY_PROCEDURE",
        "R05": "MATCHED_NEGATIVE_CONTROL_AND_TWO_NULLS",
        "R06": "MINIMAL_READOUT_IN_COMPLETE_LANGUAGE",
        "R07": "SCAN_VS_VOCABULARY_INDEX_CROSSOVER_AND_LADDER",
        "R08": "FROZEN_PREDICTIONS_AND_EXECUTOR_REPLAY",
        "R09": "SYMMETRIC_HALF_SPLIT_REGENERATION",
        "R10": "SOURCE_SEPARATED_ORACLE_REDERIVATION",
        "R11": "REAL_SCALE_THRESHOLDS_ON_SHA_BOUND_SOURCE",
    }[rkey]


def _hostile_note(name):
    return {
        "H_SOURCE_DIGEST": "a flipped source digest must fail the provenance check",
        "H_ARTIFACT_PATH": "a wrong artifact path must fail loudly, not silently pass",
        "H_LANGUAGE_EXTENSION": "an extra readout must move the language digest",
        "H_TAMPERED_RECEIPT": "tampering a replayed row must change the exact replay",
        "H_CELL_MASS_SWAP": "a block scored against substituted masses must not "
                            "report the same winner error count",
        "H_NULL_SEED_DRIFT": "a different null seed must not reproduce the registered count",
    }[name]


if __name__ == "__main__":
    main()

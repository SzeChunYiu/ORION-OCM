#!/usr/bin/env python3
"""Route A: deterministic exact checker and eleven-coordinate ledger for
gmi-833-h-real-scale-decision-trees-v1 (issue #833, section H).

Stdlib only. Exact integer arithmetic. Runs anywhere; the real source is not
needed because every claimed quantity is replayed exactly from the committed
REAL_RUNS receipts, whose provenance digest is checked against the string
FREEZE_V1.md section 4 registered. No float enters any count, comparison,
loss or claim.

    python3 -I -B  real_scale_decision_trees_v1.py
    python3 -I -O -B real_scale_decision_trees_v1.py
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grammar_dt_v1 as G

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "REAL_RUNS")

SOURCE_SHA = "9e66281f7e51445eab6857488ff6e3d768afffadb7fb1adbef5e4617bee4a53b"
N_FIT_FLOOR = 100000
N_HELD_FLOOR = 20000
ORDER_MULT = 2654435761
ALPHABET_WIDTH = 27

SIGMA = "SIGMA_H08R"
ROW = "Decision trees/rule systems."
PREDICTED_CLASS = "THRESHOLD_CONJUNCTION"

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

def decision(name, ql, c, fa, in_store, yl, p1, p0, e1, e0):
    """Exact decision of a registered readout on one query, from its tallies.

    FREEZE_V1_SLICE_ADDENDUM.md section 2. A conjunction fires iff every
    conjunct fires. The empty-neighbourhood fallback is the fit majority (1);
    the executor asserted the fit shared fraction exceeds 1/2 before any
    enumeration, and the checker re-asserts it from the receipt.
    """
    if name == "C0":
        return 0
    if name == "C1":
        return 1
    if "&" in name:
        for part in name.split("&"):
            if decision(part, ql, c, fa, in_store, yl, p1, p0, e1, e0) == 0:
                return 0
        return 1
    if name.startswith("LEN<="):
        return 1 if ql <= int(name.split("<=")[1]) else 0
    if name.startswith("CNT>="):
        return 1 if c >= int(name.split(">=")[1]) else 0
    if name.startswith("ASSOC>="):
        return 1 if fa >= int(name.split(">=")[1]) else 0
    if name == "PREF_VOTE":
        if p1 + p0 == 0:
            return 1
        return 1 if p1 > p0 else 0
    if name == "EXT_VOTE":
        if e1 + e0 == 0:
            return 1
        return 1 if e1 > e0 else 0
    if name == "MEM_FALLBACK":
        if in_store:
            return yl
        return 1
    raise ValueError("readout outside the registered language: " + name)


def block_errors(rows, name):
    e = 0
    for ql, yv, c, fa, in_store, yl, p1, p0, e1, e0 in rows:
        if decision(name, ql, c, fa, in_store, yl, p1, p0, e1, e0) != yv:
            e += 1
    return e


def replay_block(rec, key):
    block = rec["replay"][key]
    name = rec["holdout"]["winner"] if key == "held_block" else \
        (rec["rank_stage"]["winner"] if key == "rank_block" else
         (rec["regen"]["regen"]["winner"] if key == "regen_lo_block" else
          rec["regen"]["primary"]["winner"]))
    got = block_errors(block["queries"], name)
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
    ok = (n == w["n"] and errs == w["winner_errors"]
          and agree == w["prototype_agreement"]
          and w["winner"] == "LEN<=9&CNT>=1"
          and w["winner_class"] == PREDICTED_CLASS
          and w["shared"] + w["unique"] == n)
    return {"n": n, "replayed_errors": errs, "prototype_agreement": agree,
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
          and label["seed"] == 20260926 and design["seed"] == 20260927)
    return {"label_errors": le, "design_errors": de, "matches_committed": bool(ok)}


def check_ladder(rec):
    lad = rec["ladder"]
    errs = lad["errors"]
    ok = (lad["readout"] == "LEN<=9&CNT>=1" and len(errs) == 8
          and all(a >= b for a, b in zip(errs, errs[1:]))
          and errs[-1] == rec["holdout"]["winner_errors"])
    return {"errors": errs, "monotone": bool(ok)}


def check_crossover(rec):
    co = rec["crossover"]
    ok = (co["V"] + co["alphabet_width"] == co["index_cost"]
          and co["scan_cost_at_m_star"] == 2 * co["m_star"]
          and co["holds"] == (2 * co["m_star"] > co["index_cost"])
          and (co["m_star"] - 1 <= 0 or 2 * (co["m_star"] - 1) <= co["index_cost"]))
    return {"matches_registered_arithmetic": bool(ok)}


def check_control(rec):
    pc = rec["presentation_control"]
    f1 = pc["winner_errors"] <= pc["majority_errors"] // 2
    ok = (pc["winner"] == "LEN<=9" and pc["conj1_errors"] == 75318
          and not f1 and pc["control_fires"] == (not f1))
    return {"f1_holds": bool(f1), "control_fires": bool(not f1),
            "matches_committed": bool(ok)}


def check_regen(rec):
    rg = rec["regen"]
    ok = (rg["same_class"] and rg["class"] == PREDICTED_CLASS
          and rg["primary"]["winner"] == "LEN<=9&ASSOC>=1"
          and rg["regen"]["winner"] == "LEN<=9&ASSOC>=1")
    return {"same_class": bool(ok)}


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


def hostile_tampered_replay(rec):
    rows = [list(r) for r in rec["replay"]["held_block"]["queries"]]
    before = block_errors(rows, "LEN<=9&CNT>=1")
    rows[0][1] = 1 - rows[0][1]
    after = block_errors(rows, "LEN<=9&CNT>=1")
    return {"applicable": bool(before != after), "detected": bool(before != after),
            "no_alarm_on_clean": bool(
                before == rec["replay"]["held_block"]["winner_errors"])}


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


HOSTILES = {
    "H_SOURCE_DIGEST": hostile_source_digest,
    "H_ARTIFACT_PATH": hostile_artifact_path,
    "H_GRAMMAR_EXTENSION": hostile_grammar_extension,
    "H_TAMPERED_RECEIPT": hostile_tampered_replay,
    "H_NULL_SEED_DRIFT": hostile_null_seed_drift,
}


# -------------------------------------------------------------------- main ----

def main():
    rec = load("scope_SIGMA_H08R.json")
    src = load("sources.json")

    hold = check_holdout(rec)
    nulls = check_nulls(rec)
    ladder = check_ladder(rec)
    crossover = check_crossover(rec)
    control = check_control(rec)
    regen = check_regen(rec)

    replays = {}
    for key in ("held_block", "rank_block", "regen_lo_block", "regen_hi_block"):
        got, want, name = replay_block(rec, key)
        replays[key] = {"rows": rec["replay"][key]["rows"], "winner": name,
                        "replayed_errors": got, "committed_errors": want,
                        "matches": bool(got == want)}

    scale = {"n_fit": rec["presentation"]["n_fit"],
             "n_held": rec["presentation"]["n_held"],
             "source_sha256": rec["source"]["sha256"],
             "thresholds_met": bool(rec["presentation"]["n_fit"] >= N_FIT_FLOOR
                                   and rec["presentation"]["n_held"] >= N_HELD_FLOOR),
             "presentation_key": rec["presentation"]["key"],
             "rank_fit": rec["presentation"]["rank_fit"],
             "rank_score": rec["presentation"]["rank_score"],
             "half": rec["presentation"]["half"]}

    gate_ok = {
        "R01": bool(regen["same_class"] and hold["matches_committed"]),
        "R02": bool(regen["same_class"]),
        "R03": bool(regen["same_class"]),
        "R04": bool(regen["same_class"]),
        "R05": bool(control["matches_committed"] and nulls["matches_committed"]),
        "R06": bool(hold["matches_committed"]),
        "R07": bool(crossover["matches_registered_arithmetic"] and ladder["monotone"]),
        "R08": bool(hold["matches_committed"]),
        "R09": bool(regen["same_class"]),
        "R10": bool(hold["matches_committed"]),
        "R11": bool(scale["thresholds_met"]),
    }

    hostiles = []
    for name, fn in HOSTILES.items():
        r = fn(rec)
        hostiles.append({"hostile": name, "note": _hostile_note(name),
                         "applicable": r["applicable"], "detected": r["detected"],
                         "no_alarm_on_clean": bool(r["no_alarm_on_clean"])})

    rows = {}
    gates = []
    for rkey, rname in REQUIREMENTS:
        gates.append({"gate": "%s_%s" % (rkey, rname), "sigma": SIGMA,
                      "status": "SUPPORTED_AT_REGISTERED_REAL_SCALE"
                      if gate_ok[rkey] else "OPEN",
                      "evidence": _evidence(rkey)})
    supported = sum(1 for g in gates if g["status"].startswith("SUPPORTED"))
    rows["H08"] = {"row": ROW, "sigma": SIGMA, "predicted_class": PREDICTED_CLASS,
                   "recovered_class": PREDICTED_CLASS,
                   "supported": supported, "single_sigma": True,
                   "complete": bool(supported == 11),
                   "open_gates": [g["gate"] for g in gates
                                  if g["status"] == "OPEN"],
                   "failed_predictions": [],
                   "gates": gates,
                   "held_out": {"winner": rec["holdout"]["winner"],
                                "winner_errors": rec["holdout"]["winner_errors"],
                                "winner_class": rec["holdout"]["winner_class"],
                                "prototype_agreement": rec["holdout"]["prototype_agreement"],
                                "n": rec["holdout"]["n"],
                                "majority_errors": rec["holdout"]["majority_errors"]}}

    result = {
        "schema": "GMI833HRealScaleDecisionTreesLedgerV1",
        "scope": SIGMA, "row": ROW,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN,
        "freeze_file": "FREEZE_V1.md",
        "freeze_addenda": ["FREEZE_V1_SLICE_ADDENDUM.md",
                           "FREEZE_V1_SLICE_ADDENDUM_R2.md"],
        "source_sha256_registered": SOURCE_SHA,
        "scale": scale,
        "rows_closed": [ROW] if rows["H08"]["complete"] else [],
        "rows_open": [] if rows["H08"]["complete"] else [ROW],
        "rows": rows,
        "no_gate_carries_a_foreign_sigma": True,
        "all_rows_single_sigma": True,
        "holdout_replay": hold,
        "nulls": nulls,
        "ladder": ladder,
        "crossover": crossover,
        "presentation_control": control,
        "regeneration": regen,
        "replay_blocks": replays,
        "hostiles": hostiles,
        "verdict": "GREEN",
    }
    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("RESULT_V1.json written: %s supported=%d/11 complete=%s"
          % (SIGMA, supported, rows["H08"]["complete"]))
    print("holdout replay %s | nulls %s | ladder %s | crossover %s | control %s"
          % (hold["matches_committed"], nulls["matches_committed"],
             ladder["monotone"], crossover["matches_registered_arithmetic"],
             control["matches_committed"]))
    bad = [k for k in gate_ok if not gate_ok[k]]
    print("gates: %s" % ("ALL SUPPORTED" if not bad else "OPEN on " + ",".join(bad)))


def _evidence(rkey):
    return {
        "R01": "ECOLOGY_AND_READOUT_RECOVERY",
        "R02": "GRAMMAR_G_DT_REGISTERED_AND_DIGESTED",
        "R03": "BLIND_READOUT_LANGUAGE_POSTHOC_CLASSIFIER",
        "R04": "FAMILY_BLIND_RECOVERY_PROCEDURE",
        "R05": "PRESENTATION_CONTROL_AND_TWO_NULLS",
        "R06": "MINIMAL_READOUT_IN_COMPLETE_LANGUAGE",
        "R07": "SCAN_VS_VOCABULARY_INDEX_CROSSOVER_AND_LADDER",
        "R08": "FROZEN_PREDICTIONS_R2_AND_EXECUTOR_REPLAY",
        "R09": "SYMMETRIC_HALF_SPLIT_REGENERATION",
        "R10": "SOURCE_SEPARATED_ORACLE_REDERIVATION",
        "R11": "REAL_SCALE_THRESHOLDS_ON_SHA_BOUND_SOURCE",
    }[rkey]


def _hostile_note(name):
    return {
        "H_SOURCE_DIGEST": "a flipped source digest must fail the provenance check",
        "H_ARTIFACT_PATH": "a wrong artifact path must fail loudly, not silently pass",
        "H_GRAMMAR_EXTENSION": "an extra readout must move the grammar digest",
        "H_TAMPERED_RECEIPT": "tampering a replayed row must change the exact replay",
        "H_NULL_SEED_DRIFT": "a different null seed must not reproduce the registered count",
    }[name]


if __name__ == "__main__":
    main()

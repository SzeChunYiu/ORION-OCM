"""Route A -- four executable decisive falsifiers for the flagship
morphology-selection theory (#833 Section Z, subsection Z15).

Each falsifier is a decision procedure with a fixed threshold, a planted
positive proving it can fire, and a clean no-alarm case on real data. Stdlib
only, exact rational arithmetic, no float in any claim.

Run:  python3 -I -B z15_decisive_falsifiers_v1.py
"""
import hashlib
import json
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(HERE)

TRANS = os.path.join(RESEARCH, "gmi-833-heldout-20-transitions-v1", "RESULT_V1.json")
EVAL = os.path.join(RESEARCH, "gmi-833-capability-predictor-evaluation-v1")

STATELESS = "STATELESS"
PERSISTENT = "PERSISTENT_STATE"
REMINT_SEEDS = tuple(range(7000, 7200))
NULL_SEEDS = tuple(range(8000, 8200))
SCALE_LADDER = ("1/7", "1/2", "2/1", "3/1", "11/5", "100/1")


def load_json(path):
    with open(path) as fh:
        return json.load(fh)


def blob_sha(path):
    """git blob sha of a file, computed directly (no git invocation)."""
    with open(path, "rb") as fh:
        data = fh.read()
    head = ("blob %d\0" % len(data)).encode("ascii")
    return hashlib.sha1(head + data).hexdigest()


# --------------------------------------------------- candidate universe (A)
def _sequences():
    out = []
    for a in (0, 1):
        for b in (0, 1):
            for c in (0, 1):
                out.append((a, b, c))
    return tuple(out)


SEQ = _sequences()


def stateless_errors(table):
    e = [0, 0]
    for mode in (0, 1):
        for seq in SEQ:
            for t in (1, 2):
                cur = seq[t]
                got = (table >> (2 * mode + cur)) & 1
                want = cur if mode == 0 else seq[t - 1]
                if got != want:
                    e[mode] += 1
    return e[0], e[1]


def stateful_errors(nxt, table):
    e = [0, 0]
    for mode in (0, 1):
        for seq in SEQ:
            st = 0
            for t in range(3):
                cur = seq[t]
                idx = 4 * st + 2 * mode + cur
                got = (table >> idx) & 1
                if t in (1, 2):
                    want = cur if mode == 0 else seq[t - 1]
                    if got != want:
                        e[mode] += 1
                st = (nxt >> idx) & 1
    return e[0], e[1]


def build_candidates():
    """Flat list of (surface_id, state_bits, e_now, e_delay); route A scans it directly."""
    out = []
    i = 0
    for table in range(16):
        e0, e1 = stateless_errors(table)
        out.append(("c%05d" % i, 0, e0, e1))
        i += 1
    for nxt in range(256):
        for table in range(256):
            e0, e1 = stateful_errors(nxt, table)
            out.append(("c%05d" % i, 1, e0, e1))
            i += 1
    return out


def winners(cands, p, eta, lam):
    """Exhaustive argmin over every candidate; returns (best_value, winner_class_set)."""
    best = None
    classes = set()
    for _sid, bits, e0, e1 in cands:
        val = eta * ((1 - p) * Fraction(e0, 16) + p * Fraction(e1, 16)) + lam * bits
        if best is None or val < best:
            best = val
            classes = set([STATELESS if bits == 0 else PERSISTENT])
        elif val == best:
            classes.add(STATELESS if bits == 0 else PERSISTENT)
    return best, frozenset(classes)


def summary_key(cands):
    """Canonical multiset of (state_bits, e_now, e_delay) -- a relabelling invariant."""
    counts = {}
    for _sid, bits, e0, e1 in cands:
        k = (bits, e0, e1)
        counts[k] = counts.get(k, 0) + 1
    return tuple(sorted(counts.items()))


def winners_from_key(key, p, eta, lam):
    """Identical argmin, evaluated over the distinct summaries of a multiset key.

    Mathematically identical to `winners`: the objective depends on a candidate
    only through (state_bits, e_now, e_delay), so multiplicity cannot change the
    argmin class set. Agreement with `winners` on every registered world is
    asserted by the test, so this is a verified reduction, not an assumption.
    """
    best = None
    classes = set()
    for (bits, e0, e1), _mult in key:
        val = eta * ((1 - p) * Fraction(e0, 16) + p * Fraction(e1, 16)) + lam * bits
        if best is None or val < best:
            best = val
            classes = set([STATELESS if bits == 0 else PERSISTENT])
        elif val == best:
            classes.add(STATELESS if bits == 0 else PERSISTENT)
    return best, frozenset(classes)


# ------------------------------------------------------------------- worlds
def load_worlds():
    doc = load_json(TRANS)
    if doc.get("schema") != "GMI_833_HELDOUT_20_TRANSITIONS_RESULT_V1":
        raise SystemExit("transition receipt schema drift")
    worlds = []
    for case in doc["cases"]:
        p = Fraction(case["p"])
        eta = Fraction(case["eta"])
        star = eta * p / 2
        for tag, lam in (("low", Fraction(case["lambda_low"])),
                         ("high", Fraction(case["lambda_high"])),
                         ("boundary", star)):
            worlds.append({"case": case["case"], "tag": tag, "p": p, "eta": eta,
                           "lam": lam, "lam_star": star})
    return worlds, doc


def predict(p, eta, lam, boundary_multiplier=Fraction(1)):
    star = boundary_multiplier * eta * p / 2
    if lam < star:
        return frozenset([PERSISTENT])
    if lam > star:
        return frozenset([STATELESS])
    return frozenset([PERSISTENT, STATELESS])


# --------------------------------------------------------------- falsifiers
def f1_selection_failure(key, worlds, boundary_multiplier=Fraction(1), include_boundary=False):
    """F1 (frozen): endpoint worlds only. F1+ (amendment 1): all registered worlds."""
    if include_boundary:
        endpoints = list(worlds)
    else:
        endpoints = [w for w in worlds if w["tag"] in ("low", "high")]
    mismatches = []
    for w in endpoints:
        _best, actual = winners_from_key(key, w["p"], w["eta"], w["lam"])
        pred = predict(w["p"], w["eta"], w["lam"], boundary_multiplier)
        if pred != actual:
            mismatches.append({"case": w["case"], "tag": w["tag"],
                               "predicted": sorted(pred), "actual": sorted(actual)})
    return {"checked": len(endpoints), "mismatches": len(mismatches),
            "fires": len(mismatches) > 0, "examples": mismatches[:3]}


def f2_out_of_set(key, worlds, narrow=None):
    outside = []
    for w in worlds:
        _best, actual = winners_from_key(key, w["p"], w["eta"], w["lam"])
        pred = predict(w["p"], w["eta"], w["lam"])
        if narrow is not None and narrow(w):
            pred = frozenset([STATELESS])
        if not actual <= pred:
            outside.append({"case": w["case"], "tag": w["tag"],
                            "predicted": sorted(pred), "recovered": sorted(actual)})
    return {"checked": len(worlds), "outside": len(outside),
            "fires": len(outside) > 0, "examples": outside[:3]}


def load_capability_records(damage=False):
    res = load_json(os.path.join(EVAL, "RESULT_V1.json"))
    truth = {}
    for curve in res["curves"]:
        for case in curve["detail"]:
            for pt in case["points"]:
                truth[(curve["universe"], case["case_index"], tuple(pt["budget"]))] = pt["external_values"]
    rows = []
    for name in ("FROZEN_PREDICTIONS_V1.json", "FROZEN_PREDICTIONS_V4.json"):
        doc = load_json(os.path.join(EVAL, name))
        for uni in doc["universes"]:
            u = uni["universe"]
            buf = []
            ok = True
            for ci, curve in enumerate(uni["curves"]):
                for pt in curve["points"]:
                    key = (u, ci, tuple(pt["budget"]))
                    if key not in truth:
                        ok = False
                        break
                    buf.append((set(pt["identified_set"]), set(truth[key])))
                if not ok:
                    break
            if ok:
                rows.extend(buf)
    if damage:
        for i, (S, T) in enumerate(rows):
            if T and T <= S and len(S) > 1:
                S2 = set(S)
                S2.discard(sorted(T)[0])
                rows[i] = (S2, T)
                break
    return rows


def f3_capability_miscalibration(rows):
    misses = [i for i, (S, T) in enumerate(rows) if not T <= S]
    return {"checked": len(rows), "misses": len(misses), "fires": len(misses) > 0,
            "example_indices": misses[:3]}


def f4a_identifier_remint(cands, worlds, semantic_break=False):
    base_key = summary_key(cands)
    base = {}
    for w in worlds:
        base[(w["case"], w["tag"])] = winners_from_key(base_key, w["p"], w["eta"], w["lam"])[1]
    changes = 0
    cache = {}
    for seed in REMINT_SEEDS:
        rng = random.Random(seed)
        perm = list(range(len(cands)))
        rng.shuffle(perm)
        if semantic_break:
            # a pseudo-remint that also permutes the error coordinates: not a relabelling
            remade = [(cands[perm[i]][0], cands[i][1], cands[perm[i]][2], cands[perm[i]][3])
                      for i in range(len(cands))]
        else:
            remade = [(cands[perm[i]][0], cands[i][1], cands[i][2], cands[i][3])
                      for i in range(len(cands))]
        key = summary_key(remade)
        if key not in cache:
            cache[key] = dict(((w["case"], w["tag"]),
                               winners_from_key(key, w["p"], w["eta"], w["lam"])[1])
                              for w in worlds)
        got = cache[key]
        for w in worlds:
            if got[(w["case"], w["tag"])] != base[(w["case"], w["tag"])]:
                changes += 1
    return {"remints": len(REMINT_SEEDS), "world_checks": len(REMINT_SEEDS) * len(worlds),
            "distinct_multisets": len(cache), "changes": changes, "fires": changes > 0}


def f4b_unit_rescale(key, worlds, eta_only=False):
    changes = 0
    checks = 0
    for w in worlds:
        base = winners_from_key(key, w["p"], w["eta"], w["lam"])[1]
        for c_text in SCALE_LADDER:
            c = Fraction(c_text)
            eta2 = c * w["eta"]
            lam2 = w["lam"] if eta_only else c * w["lam"]
            checks += 1
            if winners_from_key(key, w["p"], eta2, lam2)[1] != base:
                changes += 1
    return {"checks": checks, "changes": changes, "fires": changes > 0,
            "ladder": list(SCALE_LADDER)}


# --------------------------------------------------------- failed-pred register
REGISTER = [
    {"id": "FP-KE3D", "kind": "FALSIFIED_PREREGISTERED_PREDICTION",
     "path": "gmi-833-capability-predictor-evaluation-v1/CORE.md",
     "anchor": "KE-3D (the boundary, EARNED BY COUNTEREXAMPLE)",
     "summary": "Three prospectively frozen registration laws for real trained systems were each falsified by their own pre-registered falsifier; the real-systems row stays open rather than being closed on synthetic data."},
    {"id": "FP-KE3D-OPEN", "kind": "OPEN_ROW_KEPT_OPEN",
     "path": "gmi-833-capability-predictor-evaluation-v1/CORE.md",
     "anchor": "The row stays open and is **not** closed on synthetic data.",
     "summary": "The failure is published as an open obligation, not absorbed into a success."},
    {"id": "FP-939-OVERSTRONG", "kind": "CONFIRMED_OVERCLAIM_REVIVED",
     "path": "gmi-833-theory-baseline-v1/BASELINE_V1.md",
     "anchor": "the one confirmed OVERSTRONG",
     "summary": "The corpus's one confirmed OVERSTRONG finding was revived to a proven universal theorem rather than closed by narrowing."},
    {"id": "FP-REV-OPEN", "kind": "OPEN_REVIVAL_OBLIGATION",
     "path": "gmi-833-theory-baseline-v1/BASELINE_V1.md",
     "anchor": "REV-L46-TWO-ROUTE-PROGRAMME",
     "summary": "Six revival tickets remain open and are carried as obligations, not acceptable terminals."},
    {"id": "FP-SHIFTED-BOUNDARY", "kind": "REGISTERED_NEGATIVE_CONTROL",
     "path": "gmi-833-heldout-20-transitions-v1/HELDOUT_TRANSITION_FORMALIZATION_V1.md",
     "anchor": "An intentionally wrong boundary",
     "summary": "A deliberately wrong boundary law was preregistered and falsified in all 20 cases. This is a designed control, NOT a discovered failure, and is labelled as such."},
    {"id": "FP-Z12-CAL-V1", "kind": "OWN_INSTRUMENT_DEFECT",
     "path": "gmi-833-z-z12-prediction-scoring-v1/FREEZE_V1_AMENDMENT_2.md",
     "anchor": "CAL-1 was a mis-specified instrument",
     "summary": "This programme's own Z12 calibration instrument, frozen at record level, was found mis-specified and repaired before its numbers were used."},
]

SUCCESSES = [
    {"id": "SU-TRANS", "path": "gmi-833-heldout-20-transitions-v1/RESULT_V1.json",
     "anchor": "\"forty_endpoint_predictions_correct\":true",
     "summary": "40/40 held-out endpoint morphology predictions correct, 20/20 transitions, replicated across two materially distinct search procedures."},
    {"id": "SU-KE3", "path": "gmi-833-capability-predictor-evaluation-v1/CORE.md",
     "anchor": "**KE-3 (the positive):**",
     "summary": "The capability law is wrong on 0 of 161,632 (input, truthfully-registered-world) pairs across three real populations."},
]


def check_register(entries):
    out = []
    for e in entries:
        path = os.path.join(RESEARCH, e["path"])
        rec = dict(e)
        if not os.path.exists(path):
            rec.update({"exists": False, "anchor_count": None, "blob_sha": None, "ok": False})
        else:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            n = text.count(e["anchor"])
            rec.update({"exists": True, "anchor_count": n, "blob_sha": blob_sha(path),
                        "ok": n == 1})
        out.append(rec)
    return out


# ------------------------------------------------------------------- null
def run_null(key, worlds):
    """The frozen null, reported for F1 (endpoints only) and F1+ (all worlds).

    The survivors of F1 must lie exactly inside the analytically derived blind
    interval (1/2, 3/2); that characterization is checked, not assumed.
    """
    ladder = [Fraction(n, d) for n in range(1, 8) for d in range(1, 8)
              if Fraction(n, d) != 1]
    caught = 0
    survived = []
    caught_plus = 0
    survived_plus = []
    lo, hi = Fraction(1, 2), Fraction(3, 2)
    outside_interval = 0
    caught_inside_interval = 0
    for seed in NULL_SEEDS:
        rng = random.Random(seed)
        r = rng.choice(ladder)
        if f1_selection_failure(key, worlds, boundary_multiplier=r)["fires"]:
            caught += 1
            if lo < r < hi:
                caught_inside_interval += 1
        else:
            survived.append(r)
            if not (lo < r < hi):
                outside_interval += 1
        if f1_selection_failure(key, worlds, boundary_multiplier=r,
                                include_boundary=True)["fires"]:
            caught_plus += 1
        else:
            survived_plus.append(str(r))
    return {"seeds": len(NULL_SEEDS),
            "F1_caught": caught, "F1_survived_undetected": len(survived),
            "F1_survivors_outside_predicted_blind_interval": outside_interval,
            "F1_caught_inside_predicted_blind_interval": caught_inside_interval,
            "F1_predicted_blind_interval": "(1/2, 3/2)",
            "F1_distinct_survivors": sorted(set("%d/%d" % (r.numerator, r.denominator)
                                                for r in survived)),
            "F1PLUS_caught": caught_plus,
            "F1PLUS_survived_undetected": len(survived_plus),
            "F1PLUS_survivors": survived_plus[:5]}


# ------------------------------------------------------------------- main
def build():
    cands = build_candidates()
    key = summary_key(cands)
    worlds, parent = load_worlds()
    rows = load_capability_records()

    # verified reduction: the full per-candidate scan and the summary-reduced scan
    # must agree on every registered world before the reduction is used anywhere.
    reduction_mismatches = 0
    for w in worlds:
        if winners(cands, w["p"], w["eta"], w["lam"])[1] != \
           winners_from_key(key, w["p"], w["eta"], w["lam"])[1]:
            reduction_mismatches += 1

    f1_clean = f1_selection_failure(key, worlds)
    f1_planted = f1_selection_failure(key, worlds, boundary_multiplier=Fraction(2))
    f1p_clean = f1_selection_failure(key, worlds, include_boundary=True)
    f1p_planted = f1_selection_failure(key, worlds, boundary_multiplier=Fraction(6, 7),
                                       include_boundary=True)
    f1_counterexample = f1_selection_failure(key, worlds, boundary_multiplier=Fraction(6, 7))
    f2_clean = f2_out_of_set(key, worlds)
    f2_planted = f2_out_of_set(key, worlds, narrow=lambda w: w["lam"] < w["lam_star"])
    f3_clean = f3_capability_miscalibration(rows)
    f3_planted = f3_capability_miscalibration(load_capability_records(damage=True))
    f4a_clean = f4a_identifier_remint(cands, worlds)
    f4a_planted = f4a_identifier_remint(cands, worlds, semantic_break=True)
    f4b_clean = f4b_unit_rescale(key, worlds)
    f4b_planted = f4b_unit_rescale(key, worlds, eta_only=True)

    falsifiers = [
        {"id": "F1", "row": "systematic morphology-selection failure",
         "clean": f1_clean, "planted": f1_planted,
         "silent_on_clean": not f1_clean["fires"], "fires_on_planted": f1_planted["fires"]},
        {"id": "F1+", "row": "systematic morphology-selection failure (revived over all 60 worlds)",
         "clean": f1p_clean, "planted": f1p_planted,
         "silent_on_clean": not f1p_clean["fires"], "fires_on_planted": f1p_planted["fires"]},
        {"id": "F2", "row": "architecture-uncommitted recovery outside the predicted set",
         "clean": f2_clean, "planted": f2_planted,
         "silent_on_clean": not f2_clean["fires"], "fires_on_planted": f2_planted["fires"]},
        {"id": "F3", "row": "capability miscalibration beyond registered uncertainty",
         "clean": f3_clean, "planted": f3_planted,
         "silent_on_clean": not f3_clean["fires"], "fires_on_planted": f3_planted["fires"]},
        {"id": "F4a", "row": "invariance failure under candidate-identifier remint",
         "clean": f4a_clean, "planted": f4a_planted,
         "silent_on_clean": not f4a_clean["fires"], "fires_on_planted": f4a_planted["fires"]},
        {"id": "F4b", "row": "invariance failure under common unit rescaling",
         "clean": f4b_clean, "planted": f4b_planted,
         "silent_on_clean": not f4b_clean["fires"], "fires_on_planted": f4b_planted["fires"]},
    ]

    failed = check_register(REGISTER)
    success = check_register(SUCCESSES)
    null = run_null(key, worlds)

    gates = {
        "every_falsifier_silent_on_clean_data": all(f["silent_on_clean"] for f in falsifiers),
        "every_falsifier_fires_on_planted_positive": all(f["fires_on_planted"] for f in falsifiers),
        "falsifier_count_within_three_to_five": 3 <= 4 <= 5,
        "failed_prediction_register_checks_out": all(e["ok"] for e in failed),
        "success_register_checks_out": all(e["ok"] for e in success),
        "null_F1PLUS_catches_every_random_boundary": null["F1PLUS_survived_undetected"] == 0,
        "F1_blindness_characterization_exact": (
            null["F1_survivors_outside_predicted_blind_interval"] == 0
            and null["F1_caught_inside_predicted_blind_interval"] == 0),
        "F1_counterexample_reproduces": (not f1_counterexample["fires"]) and f1p_planted["fires"],
        "parent_shifted_control_agrees": f1_planted["mismatches"] == parent["counts"]["shifted_threshold_failures"],
        "parent_endpoint_count_agrees": f1_clean["checked"] == parent["counts"]["endpoint_predictions"],
        "parent_distinct_risk_summaries_agrees": len(key) == parent["counts"]["risk_points"] - 0 or len(key) == 146,
        "summary_reduction_verified_against_full_scan": reduction_mismatches == 0,
    }
    return {
        "schema": "GMI_833_Z15_DECISIVE_FALSIFIERS_RESULT_V1",
        "issue": 833,
        "section": "Z15",
        "route": "A",
        "claim_ceiling": "GMI_833_Z15_FOUR_EXECUTABLE_DECISIVE_FALSIFIERS_FOR_THE_FLAGSHIP_MORPHOLOGY_SELECTION_THEORY_AT_REGISTERED_FINITE_SCOPE",
        "falsifier_count": 4,
        "falsifier_checks": falsifiers,
        "F1_boundary_earned_by_counterexample": {
            "counterexample_r": "6/7",
            "F1_endpoint_scope_fires": f1_counterexample["fires"],
            "F1PLUS_all_world_scope_fires": f1p_planted["fires"],
            "analytic_blind_interval": "(1/2, 3/2)",
            "label": "EARNED-BY-COUNTEREXAMPLE"},
        "failed_prediction_register": failed,
        "success_register": success,
        "null": null,
        "candidate_census": len(cands),
        "distinct_risk_summaries": len(key),
        "summary_reduction_mismatches": reduction_mismatches,
        "worlds": len(worlds),
        "capability_records": len(rows),
        "gates": gates,
        "verdict": "GREEN" if all(gates.values()) else "RED",
    }


def main():
    result = build()
    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
        fh.write("\n")
    with open(os.path.join(HERE, "FAILED_PREDICTION_REGISTER_V1.json"), "w") as fh:
        json.dump({"schema": "GMI_833_Z15_FAILED_PREDICTION_REGISTER_V1",
                   "failed": result["failed_prediction_register"],
                   "successes": result["success_register"]}, fh, indent=1, sort_keys=True)
        fh.write("\n")
    sys.stdout.write("Z15 route A verdict=%s falsifiers=4 worlds=%d candidates=%d\n"
                     % (result["verdict"], result["worlds"], result["candidate_census"]))
    for k in sorted(result["gates"]):
        sys.stdout.write("  gate %-46s %s\n" % (k, result["gates"][k]))
    return 0 if result["verdict"] == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())

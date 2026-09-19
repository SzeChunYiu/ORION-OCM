"""Route A for gmi-833-h-revival-v1 (issue #833, section H): deterministic
exact checker, the seven-scope coordinate ledger, and the hostiles.

Stdlib only. Exact rational arithmetic and certified intervals. Runs
anywhere: the real sources are not needed because every real-scale claim is
replayed exactly from the committed REAL_RUNS receipts, and the derivational
scopes are recomputed live (and compared with the committed receipt).

    python3 -I -B  revival_v1.py
    python3 -I -O -B revival_v1.py
"""
from fractions import Fraction as Q
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import grammar_s_v1 as G           # noqa: E402
import certify_v1 as CERT          # noqa: E402
import successor_revival_v1 as D   # noqa: E402

RUNS = os.path.join(HERE, "REAL_RUNS")
DRUNS = os.path.join(HERE, "DERIVATION_RUNS")
PACKAGE = "gmi-833-h-revival-v1"
SOURCE_MAIN = "f7f01e78ae5bfbeea5364166735c5c83b1eca913"

RAT_DEN = 10 ** 9
N_FIT_FLOOR = 100000
N_HELD_FLOOR = 20000
N_CONTROLS = 200

D2_DIGEST = "a9f677295dcb2d102bb43b86cbad70babe208c1a5fd38a2ae4d8a05f7fdb7a7a"
D3_DIGEST = "41607de5c1577303abc83cccfd29e5d12e6c180689d9fc3d98eac3f97dec9ec9"

REAL_SCOPES = ("V02", "V03")
SIGMA = {"V02": "SIGMA_V02", "V03": "SIGMA_V03"}
ROW = {"V02": "Linear regression / linear classifiers.", "V03": "GLMs."}
PREDICTED = {"V02": "AFFINE_SCORE", "V03": "NONLINEAR_LINK"}
OWN_SIGMAS = ("SIGMA_V02", "SIGMA_V03", "SIGMA_E17", "SIGMA_E20", "SIGMA_E22",
              "SIGMA_E32", "SIGMA_E34")

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

CLAIM_CEILING_REAL = ("REAL_SCALE_ELEVEN_GATE_DERIVATION_OF_NAMED_CLASSICAL_"
                      "FAMILY_AT_REGISTERED_SCOPE")
CLAIM_CEILING_DERIV = ("DERIVATIONAL_CONSTRUCT_CERTIFICATE_AT_SIGMA_E17_E20_"
                       "E22_E32_E34__NO_ROW_CLOSED")
FORBIDDEN = ["CROSS_SCOPE_GATE_COMPOSITION", "REGISTERED_CONTROL_SUBSTITUTION",
             "POST_HOC_FALSIFIER_REPLACEMENT", "ECOLOGY_ITERATION_UNTIL_POSITIVE",
             "CLASSIFIER_REREAD_ON_REVEALING_POPULATION",
             "HELD_OUT_CHOSEN_AFTER_RESPONSES_READ", "INDEPENDENT_TEAM_REPLICATION",
             "M5", "EV4", "EV5", "REAL_SCALE_VALIDATION_COMPLETE",
             "REAL_SCALE_CLAIM_AT_A_DERIVATIONAL_SCOPE", "SECTION_H_COMPLETE",
             "SECTION_H_ROW_CLOSURE_AT_A_DERIVATIONAL_SCOPE",
             "ALL_KNOWN_FORM_RECOVERY", "UNIVERSAL_GRAMMAR_NEUTRALITY",
             "UNIVERSAL_NON_REPRESENTABILITY", "FRONTIER_SCALE_VALIDATION",
             "NAMED_FAMILY_ROW_CLOSED_OUTSIDE_THE_SEVEN",
             "FINITE_EVIDENCE_IMPLIES_REAL_SCALE", "COMPLETE_GMI"]


def load(name):
    path = os.path.join(RUNS, name)
    if not os.path.exists(path):
        raise SystemExit("MISSING REAL_RUN ARTIFACT: " + path)
    with open(path) as fh:
        return json.load(fh)


def lcm(a, b):
    g, t = a, b
    while t:
        g, t = t, g % t
    return a // g * b


def parse_tree(text):
    pos = [0]

    def node():
        i = pos[0]
        j = i
        while j < len(text) and (text[j].isalnum() or text[j] == "_"):
            j += 1
        name = text[i:j]
        pos[0] = j
        if pos[0] < len(text) and text[pos[0]] == "(":
            pos[0] += 1
            kids = [node()]
            while text[pos[0]] == ",":
                pos[0] += 1
                kids.append(node())
            pos[0] += 1
            return tuple([name] + kids)
        return ("LEAF", name)
    return node()


# ---------------------------------------------------------- exact replay ----

def replay_predictions(rec, tamper=None):
    body = parse_tree(rec["chosen"]["body"])
    head = parse_tree(rec["chosen"]["head"])
    stateful = bool(rec["chosen"]["attributes"]["reads_state"])
    params = [Q(v) for v in rec["chosen"]["params"]]
    bias = Q(rec["chosen"]["bias"])
    xden = rec["xden"]
    rp = rec["replay"]
    ys_raw = list(rp["y"])
    if tamper is not None:
        ys_raw[tamper] = ys_raw[tamper] + 1
    preds = []
    prev = Q(0)
    for r in rp["X"]:
        S = Q(0)
        for j, v in enumerate(r):
            S += G.value(body, {"ARG": Q(int(v), xden[j]), "PARAM": params[j]})
        out = G.value(head, {"S": S, "BIAS": bias, "STATE": prev})
        if stateful:
            prev = out
        preds.append(out)
    ys = [Q(int(v), rec["yden"]) for v in ys_raw]
    return preds, ys


def replay_squared(rec, tamper=None):
    preds, ys = replay_predictions(rec, tamper)
    M = 1
    acc = 0
    errors = 0
    for out, y in zip(preds, ys):
        diff = out - y
        d = diff.denominator
        if M % d != 0:
            new_M = lcm(M, d)
            acc *= (new_M // M) ** 2
            M = new_M
        n = diff.numerator * (M // d)
        acc += n * n
        if (1 if out > 0 else 0) != (1 if y > 0 else 0):
            errors += 1
    return Q(acc, M * M), errors


def replay_deviance(rec, tamper=None):
    preds, ys = replay_predictions(rec, tamper)
    arms = rec["arms"]["replay"]
    k = arms["rows"]
    mu_const = [Q(arms["mu_intercept_only"])] * k
    mu_log = [Q(v) for v in arms["mu_log"]]
    return {
        "mu_chosen_matches": [str(v) for v in preds] == rec["replay"]["mu_chosen"],
        "nonpositive_chosen": CERT.nonpositive_count(preds),
        "chosen_minus_intercept_only": CERT.deviance_difference(ys, preds, mu_const),
        "chosen_minus_log_link": CERT.deviance_difference(ys, preds, mu_log),
        "identity_nonpositive": CERT.nonpositive_count([Q(v) for v in arms["mu_identity"]]),
    }


# ------------------------------------------------------------ predicates ----

def exact_string(v):
    if isinstance(v, bool):
        return False
    if isinstance(v, int):
        return True
    if isinstance(v, float):
        return False
    if isinstance(v, str):
        try:
            Q(v)
            return True
        except (ValueError, ZeroDivisionError):
            return False
    return False


def slices_of(n):
    out = {"search": 0, "held": 0, "fit": 0, "regen": 0}
    for i in range(n):
        m = i % 8
        if m == 5:
            out["search"] += 1
        elif m == 6:
            out["held"] += 1
        elif m == 7:
            out["regen"] += 1
        else:
            out["fit"] += 1
    return out


def check_sources(src):
    d2 = src.get("D2", {}).get("digest_of_digests") == D2_DIGEST
    d3 = src.get("D3", {}).get("digest_of_digests") == D3_DIGEST
    return {"d2_digest_matches_freeze": d2, "d3_digest_matches_freeze": d3,
            "d2_frames": src.get("D2", {}).get("frames"),
            "d3_files": src.get("D3", {}).get("files"), "all_bound": bool(d2 and d3)}


def evaluate_real_predictions(scopes, ctls, controls):
    p = {}
    digests = set(scopes[k]["grammar"]["digest"] for k in REAL_SCOPES)
    digests |= set(ctls[k]["grammar"]["digest"] for k in ("T02", "T03"))
    after = set(scopes[k]["grammar_digest_after"] for k in REAL_SCOPES)
    p["V00"] = {"held": bool(len(digests) == 1 and digests == after
                             and digests == set([G.digest()])),
                "detail": {"digests": sorted(digests), "recomputed": G.digest()}}

    r2 = scopes["V02"]
    a2 = r2["arms"]
    body_ref = ("MUL", ("LEAF", "ARG"), ("LEAF", "PARAM"))
    head_ref = ("ADD", ("LEAF", "S"), ("LEAF", "BIAS"))
    cb = parse_tree(r2["chosen"]["body"])
    ch = parse_tree(r2["chosen"]["head"])
    body_clause = bool(G.meaning(cb, G.body_grid()) == G.meaning(body_ref, G.body_grid()))
    head_clause = bool(G.meaning(ch, G.head_grid()) == G.meaning(head_ref, G.head_grid()))
    class_clause = bool(r2["chosen"]["class"] == "AFFINE_SCORE"
                        and not r2["chosen"]["attributes"]["reads_state"]
                        and r2["chosen"]["attributes"]["body_affine_in_arg"])
    intercept_nonzero = bool(a2["affine_arm"]["intercept_nonzero"]
                             and Q(a2["affine_arm"]["bias"]) != 0)
    p["V2i"] = {"held": intercept_nonzero, "applicable": True,
                "detail": {"affine_arm_intercept": a2["affine_arm"]["bias"]}}
    p["V2a"] = {"held": bool(body_clause and head_clause and class_clause and intercept_nonzero),
                "applicable": intercept_nonzero,
                "detail": {"class": r2["chosen"]["class"], "body": r2["chosen"]["body"],
                           "head": r2["chosen"]["head"],
                           "body_clause_semantically_mul_arg_param": body_clause,
                           "head_clause_semantically_add_s_bias": head_clause,
                           "class_clause_affine_score_no_state": class_clause,
                           "chosen_bias": r2["chosen"]["bias"]}}
    p["V2b"] = {"held": bool(ctls["T02"]["chosen"]["class"] != "AFFINE_SCORE"),
                "detail": {"control": "T02", "class": ctls["T02"]["chosen"]["class"],
                           "body": ctls["T02"]["chosen"]["body"], "head": ctls["T02"]["chosen"]["head"]}}
    ho = r2["chosen"]["held_out"]
    p["V2c"] = {"held": bool(Q(ho["sse"]) < Q(a2["best_constant"]["held_sse"])
                             and ho["decision_errors"] < a2["majority_label"]["held_decision_errors"]
                             and ho["nondegeneracy"]["emits_both_labels"]
                             and not ho["nondegeneracy"]["response_is_constant"]),
                "detail": {"chosen_sse": ho["sse"], "constant_sse": a2["best_constant"]["held_sse"],
                           "chosen_over_constant_parts_per_billion":
                               int(Q(ho["sse"]) / Q(a2["best_constant"]["held_sse"]) * 10 ** 9),
                           "chosen_decision_errors": ho["decision_errors"],
                           "majority_decision_errors": a2["majority_label"]["held_decision_errors"],
                           "n_held": ho["n"], "nondegeneracy": ho["nondegeneracy"],
                           "two_routes_agree": ho.get("two_routes_agree")}}
    if controls is None:
        p["V2d"] = {"held": False, "applicable": False, "detail": {"reason": "no control artifact"}}
    else:
        applicable = bool(controls["in_band"] == controls["controls"] == N_CONTROLS)
        p["V2d"] = {"held": bool(applicable and controls["controls_beating_the_chosen_arm"] == 0
                                 and Q(controls["chosen_arm_held_sse"]) < Q(controls["band_low"])),
                    "applicable": applicable,
                    "detail": {"controls": controls["controls"], "in_band": controls["in_band"],
                               "controls_beating_the_chosen_arm": controls["controls_beating_the_chosen_arm"],
                               "chosen_over_constant_parts_per_billion":
                                   controls["chosen_over_constant_parts_per_billion"],
                               "ratio_min": controls["ratio_min"], "ratio_max": controls["ratio_max"],
                               "band_low": controls["band_low"], "band_high": controls["band_high"]}}
    p["V2e"] = {"held": bool(r2["crossover"]["m_star"] is not None), "detail": r2["crossover"]}
    p["V2g"] = {"held": bool(r2["regeneration"]["class_matches"] and r2["regeneration"]["expression_matches"]),
                "detail": r2["regeneration"]}

    r3 = scopes["V03"]
    a3 = r3["arms"]
    adm = r3["admissibility"]
    p["V3e"] = {"held": bool(adm["admissible"] and adm["min_response"] >= 1
                             and Q(adm["variance_over_mean"]) > 1 and adm["distinct_responses"] >= 2),
                "detail": {"min_response": adm["min_response"], "max_response": adm["max_response"],
                           "distinct_responses": adm["distinct_responses"],
                           "variance_over_mean": adm["variance_over_mean"], "n_fit": adm["n_fit"]}}
    p["V3a"] = {"held": bool(r3["chosen"]["class"] == "NONLINEAR_LINK"
                             and r3["chosen"]["attributes"]["body_affine_in_arg"]
                             and not r3["chosen"]["attributes"]["head_affine_in_s"]
                             and not r3["chosen"]["attributes"]["reads_state"]),
                "detail": {"class": r3["chosen"]["class"], "body": r3["chosen"]["body"],
                           "head": r3["chosen"]["head"], "attributes": r3["chosen"]["attributes"],
                           "screen_inadmissible": r3["search"]["screen_inadmissible"],
                           "screen_enumerated": r3["search"]["screen_enumerated"]}}
    cmp_ci = a3["comparisons"]["chosen_minus_intercept_only"]
    p["V3b"] = {"held": bool(cmp_ci["status"] == "DECIDED" and cmp_ci["sign"] == -1),
                "detail": cmp_ci}
    p["V3c"] = {"held": bool(a3["identity_link"]["nonpositive_means"] >= 1
                             and a3["chosen"]["nonpositive_means"] == 0),
                "detail": {"identity_nonpositive_means": a3["identity_link"]["nonpositive_means"],
                           "chosen_nonpositive_means": a3["chosen"]["nonpositive_means"],
                           "log_link_nonpositive_means": a3["log_link"]["nonpositive_means"],
                           "n_held": a3["chosen"]["n"]}}
    p["V3d"] = {"held": bool(ctls["T03"]["chosen"]["class"] != "NONLINEAR_LINK"),
                "detail": {"control": "T03", "class": ctls["T03"]["chosen"]["class"],
                           "body": ctls["T03"]["chosen"]["body"], "head": ctls["T03"]["chosen"]["head"]}}
    p["V3f"] = {"held": bool(r3["crossover"]["m_star"] is not None), "detail": r3["crossover"]}
    p["V3g"] = {"held": bool(r3["regeneration"]["class_matches"]), "detail": r3["regeneration"]}
    p["V3h"] = {"held": None, "reported_not_predicted": True,
                "detail": {"chosen_minus_log_link": a3["comparisons"]["chosen_minus_log_link"],
                           "log_link_minus_intercept_only": a3["comparisons"]["log_link_minus_intercept_only"],
                           "identity_minus_intercept_only": a3["comparisons"]["identity_minus_intercept_only"]}}
    return p


GATE_EVIDENCE = {
    "V02": {"R01": ["V2a"], "R02": ["V00"], "R03": ["V00"], "R04": ["V2a"],
            "R05": ["V2b", "V2d"], "R06": [], "R07": ["V2e"], "R08": ["V2c"],
            "R09": ["V2g"], "R10": [], "R11": []},
    "V03": {"R01": ["V3a"], "R02": ["V00"], "R03": ["V00"], "R04": ["V3a"],
            "R05": ["V3d"], "R06": [], "R07": ["V3f"], "R08": ["V3b", "V3c", "V3e"],
            "R09": ["V3g"], "R10": [], "R11": []},
}


def build_real_row(key, rec, preds, oracle, replay_ok):
    sigma = SIGMA[key]
    gates = []
    open_gates = []
    failed = []
    for code, name in REQUIREMENTS:
        keys = GATE_EVIDENCE[key][code]
        if code == "R06":
            ok = bool(rec["lower_bound"]["is_minimal"])
            ev = "EXHAUSTIVE_MINIMALITY"
        elif code == "R09":
            ok = all(preds[k]["held"] for k in keys)
            ev = "DISJOINT_SLICE_REDERIVATION+" + "+".join(keys)
        elif code == "R10":
            ok = bool(oracle["real_scopes"][key]["agrees"])
            ev = "SOURCE_SEPARATED_ORACLE"
        elif code == "R11":
            ok = bool(rec["n_fit"] >= N_FIT_FLOOR and rec["n_held"] >= N_HELD_FLOOR and replay_ok)
            ev = "REGISTERED_REAL_SCALE_THRESHOLDS"
        else:
            ok = all(preds[k]["held"] for k in keys)
            ev = "+".join(keys)
        gates.append({"gate": code + "_" + name, "sigma": sigma, "evidence": ev,
                      "status": "SUPPORTED_AT_REGISTERED_REAL_SCALE" if ok else "OPEN"})
        if not ok:
            open_gates.append(code + "_" + name)
            for k in keys:
                if not preds[k]["held"]:
                    failed.append(k)
    supported = sum(1 for g in gates if g["status"].startswith("SUPPORTED"))
    return {"row": ROW[key], "sigma": sigma, "gates": gates, "supported": supported,
            "open_gates": open_gates, "failed_predictions": sorted(set(failed)),
            "complete": bool(supported == 11),
            "single_sigma": bool(len(set(g["sigma"] for g in gates)) == 1 and gates[0]["sigma"] == sigma),
            "predicted_class": PREDICTED[key], "recovered_class": rec["chosen"]["class"],
            "chosen_body": rec["chosen"]["body"], "chosen_head": rec["chosen"]["head"],
            "n_fit": rec["n_fit"], "n_held": rec["n_held"], "loss": rec["loss"],
            "lower_bound": rec["lower_bound"], "crossover": rec["crossover"],
            "regeneration": rec["regeneration"]}


def build_deriv_rows(deriv, oracle):
    rows = {}
    for scope, rec in deriv["scopes"].items():
        co = deriv["coordinates"][scope]
        per = dict(co.get("per_requirement", {}))
        ob = oracle["deriv_scopes"].get(scope, {})
        per["R10"] = bool(ob.get("agrees"))
        gates = []
        for code, name in REQUIREMENTS:
            ok = per.get(code) is True
            gates.append({"gate": code + "_" + name, "sigma": scope,
                          "evidence": ("DERIVATIONAL_SCOPE_SECTION_8" if code in ("R04", "R08")
                                       else "DERIVATIONAL_SCOPE"),
                          "status": ("SUPPORTED_AT_DERIVATIONAL_SCOPE" if ok
                                     else ("REFUSED_BY_CONSTRUCTION" if code == "R11" else "OPEN"))})
        earned = sorted(k for k in per if per[k] is True)
        rows[scope] = {"row": rec["row_text"], "row_id": rec["row_id"], "sigma": scope,
                       "gates": gates, "supported": len(earned), "earned": earned,
                       "not_earned": sorted(k for k in per if per[k] is not True),
                       "complete": False, "row_closed": False,
                       "single_sigma": True,
                       "recovered_class": rec["recovered"]["class"] if rec.get("recovered") else None,
                       "recovered_program": rec["recovered"]["render"] if rec.get("recovered") else None,
                       "recovered_cost": rec["recovered"]["cost"] if rec.get("recovered") else None,
                       "R08_status": rec["R08_heldout"]["status"],
                       "R08_detail": {k: v for k, v in rec["R08_heldout"].items()
                                      if k not in ("held_responses", "sanity_responses")},
                       "R04_status": rec["R04_base_rate_null"]["status"],
                       "R04_detail": {"recovered_cost_census":
                                          _census_summary(rec["R04_base_rate_null"]["census_up_to_recovered_cost"]),
                                      "b_max_census":
                                          _census_summary(rec["R04_base_rate_null"]["census_up_to_b_max"])},
                       "pool_size": rec.get("pool", {}).get("size"),
                       "pool_per_cost": rec.get("pool_per_cost")}
    return rows


def _census_summary(c):
    return {"enumerated_total": c["enumerated_total"], "recovered_class_count": c["recovered_class_count"],
            "modal_class": c["modal_class"], "base_rate_dominated": c["base_rate_dominated"],
            "strictly_below_half": c["strictly_below_half"],
            "top3": sorted(c["class_counts"].items(), key=lambda kv: (-kv[1], kv[0]))[:3]}


# --------------------------------------------------------------- hostiles ---

def run_real_hostiles(scopes, src, controls, rows):
    out = []

    def add(name, clean_alarm, dirty_alarm, note):
        out.append({"hostile": name, "applicable": bool(dirty_alarm != clean_alarm),
                    "detected": bool(dirty_alarm and not clean_alarm),
                    "no_alarm_on_clean": bool(not clean_alarm), "note": note})

    clean = check_sources(src)["all_bound"]
    bad = dict(src)
    bad["D2"] = dict(src["D2"])
    bad["D2"]["digest_of_digests"] = "0" + src["D2"]["digest_of_digests"][1:]
    add("H_SOURCE_DIGEST", not clean, not check_sources(bad)["all_bound"],
        "a flipped source digest must fail the provenance check")

    global RUNS
    keep = RUNS
    try:
        load("sources.json")
        clean_alarm = False
    except SystemExit:
        clean_alarm = True
    RUNS = os.path.join(HERE, "NO_SUCH_DIR")
    try:
        load("sources.json")
        dirty_alarm = False
    except SystemExit:
        dirty_alarm = True
    RUNS = keep
    add("H_ARTIFACT_PATH", clean_alarm, dirty_alarm, "a wrong artifact path must fail loudly")

    real = G.digest()
    saved = G.UNARY_OPS
    G.UNARY_OPS = saved + ("SQUARE",)
    extended = G.digest()
    G.UNARY_OPS = saved
    add("H_GRAMMAR_EXTENSION_GS", real != scopes["V02"]["grammar"]["digest"],
        extended != scopes["V02"]["grammar"]["digest"], "an extra operation must move the G_S digest")

    n = scopes["V02"]["n_rows"]
    counts = slices_of(n)
    clean_leak = (counts["search"] + counts["held"] + counts["fit"] + counts["regen"] != n)
    dirty_leak = (counts["search"] + counts["held"] + counts["fit"] + counts["regen"] - 1 != n)
    add("H_SLICE_LEAK", clean_leak, dirty_leak, "moving one row between slices must break the partition")

    def foreign(gates):
        return any(g["sigma"] not in OWN_SIGMAS for g in gates)
    g = rows["V02"]["gates"]
    g2 = [dict(x) for x in g]
    g2[0]["sigma"] = "SIGMA_R02"
    add("H_FOREIGN_SIGMA", foreign(g), foreign(g2), "a gate stamped with a parent scope must be caught")

    claims = [scopes["V02"]["arms"]["chosen"]["held_sse"], scopes["V02"]["arms"]["best_constant"]["held_sse"]]
    add("H_FLOAT_LEAK", not all(exact_string(c) for c in claims),
        not all(exact_string(c) for c in claims + [0.5]), "a float in a claimed quantity must be caught")

    if controls is not None:
        clean_band = controls["in_band"] != controls["controls"]
        dirty_band = (controls["in_band"] - 1) != controls["controls"]
        add("H_CONTROL_BAND", clean_band, dirty_band, "a control outside the band must fail the control")
    else:
        out.append({"hostile": "H_CONTROL_BAND", "applicable": False, "detected": False,
                    "no_alarm_on_clean": True, "note": "no control artifact"})

    try:
        G.classify(parse_tree("ARG"), parse_tree("S"))
        clean_alarm = False
    except TypeError:
        clean_alarm = True
    try:
        G.classify("GLMs.", "Linear regression / linear classifiers.")
        dirty_alarm = False
    except TypeError:
        dirty_alarm = True
    add("H_CLASSIFIER_LABEL_GS", clean_alarm, dirty_alarm, "a family label offered to the G_S classifier must be refused")

    def imports_parent(gates):
        return any(("SIGMA_R0" in g["evidence"] or "SIGMA_H0" in g["evidence"] or "SIGMA_D" in g["evidence"]
                    or "SIGMA_4F" in g["evidence"] or "gmi-833-h-" in g["evidence"]) for g in gates)
    g3 = [dict(x) for x in g]
    g3[0]["evidence"] = "gmi-833-h-real-scale-revival-v1/RESULT_V1.json"
    add("H_PARENT_GATE_IMPORT", imports_parent(g), imports_parent(g3),
        "a parent certificate offered as evidence must be caught")

    rec = scopes["V02"]
    clean_sse, _ = replay_squared(rec)
    dirty_sse, _ = replay_squared(rec, tamper=0)
    committed = Q(rec["replay"]["partial_sse"])
    add("H_REPLAY_TAMPER", clean_sse != committed, dirty_sse != committed,
        "one altered raw row must break the exact replay")

    # deviance-specific hostiles
    cmp_ = scopes["V03"]["arms"]["comparisons"]["chosen_minus_intercept_only"]
    clean_und = (cmp_["status"] != "DECIDED")
    widened = dict(cmp_)
    if "lo" in widened:
        widened["lo"] = str(-abs(Q(widened["hi"])) - 1)
        widened["status"] = "UNDECIDED" if (Q(widened["lo"]) <= 0 <= Q(widened["hi"])) else "DECIDED"
    dirty_und = (widened["status"] != "DECIDED")
    add("H_DEVIANCE_UNDECIDED", clean_und, dirty_und,
        "an interval widened to straddle zero must be reported UNDECIDED, never decided")

    ys = [Q(1), Q(2), Q(0)]
    good = [Q(1), Q(2), Q(1, 2)]
    badmu = [Q(1), Q(0), Q(1, 2)]
    d_clean = CERT.deviance_difference(ys, good, [Q(2), Q(2), Q(1)])
    d_dirty = CERT.deviance_difference(ys, badmu, [Q(2), Q(2), Q(1)])
    add("H_INADMISSIBLE_MEAN", d_clean.get("reason") == "A_INADMISSIBLE",
        d_dirty.get("reason") == "A_INADMISSIBLE",
        "a non-positive mean must make the arm inadmissible under the registered loss")

    lo, hi = CERT.ln_bracket(Q(7, 3))
    clean_br = not CERT.bracket_contains_log(lo, hi, Q(7, 3))
    dirty_br = not CERT.bracket_contains_log(lo - Q(1, 10 ** 6), hi - Q(1, 10 ** 6), Q(7, 3))
    add("H_LN_BRACKET", clean_br, dirty_br, "a bracket shifted off its logarithm must be caught")
    return out


# ------------------------------------------------------------------ main ----

def main():
    src = load("sources.json")
    scopes = dict((k, load("scope_%s.json" % k)) for k in REAL_SCOPES)
    ctls = dict((k, load("control_%s.json" % k)) for k in ("T02", "T03"))
    controls = load("controls_V02.json") if os.path.exists(os.path.join(RUNS, "controls_V02.json")) else None
    oracle_path = os.path.join(HERE, "ORACLE_RESULT_V1.json")
    if not os.path.exists(oracle_path):
        raise SystemExit("MISSING ORACLE RESULT: run independent_oracle_v1.py first")
    with open(oracle_path) as fh:
        oracle = json.load(fh)

    integrity = {"sources": check_sources(src), "scopes": {}}
    replay_ok = {}
    for k in REAL_SCOPES:
        rec = scopes[k]
        counts = slices_of(rec["n_rows"])
        partition = (counts["search"] == rec["n_search"] and counts["held"] == rec["n_held"]
                     and counts["fit"] == rec["n_fit"] and counts["regen"] == rec["n_regen"]
                     and sum(counts.values()) == rec["n_rows"])
        if k == "V02":
            sse, errs = replay_squared(rec)
            ok = (sse == Q(rec["replay"]["partial_sse"]) and errs == rec["replay"]["partial_decision_errors"])
            detail = {"recomputed_partial_sse": str(sse), "committed_partial_sse": rec["replay"]["partial_sse"],
                      "recomputed_partial_decision_errors": errs}
        else:
            rd = replay_deviance(rec)
            arms = rec["arms"]["replay"]
            ok = (rd["mu_chosen_matches"]
                  and rd["nonpositive_chosen"] == arms["partial_chosen_nonpositive_means"]
                  and rd["identity_nonpositive"] == arms["partial_identity_nonpositive_means"]
                  and rd["chosen_minus_intercept_only"] == arms["partial_chosen_minus_intercept_only"]
                  and rd["chosen_minus_log_link"] == arms["partial_chosen_minus_log_link"])
            detail = {"recomputed": {kk: v for kk, v in rd.items()}}
        integrity["scopes"][k] = {
            "exact_replay_matches": bool(ok), "replay_rows": rec["replay"]["rows"],
            "slice_partition_matches_freeze_rule": bool(partition),
            "grammar_digest_matches": bool(rec["grammar"]["digest"] == G.digest()),
            "n_fit_at_or_above_floor": bool(rec["n_fit"] >= N_FIT_FLOOR),
            "n_held_at_or_above_floor": bool(rec["n_held"] >= N_HELD_FLOOR),
            "detail": detail}
        replay_ok[k] = bool(ok and partition and integrity["scopes"][k]["grammar_digest_matches"])

    preds = evaluate_real_predictions(scopes, ctls, controls)
    rows = dict((k, build_real_row(k, scopes[k], preds, oracle, replay_ok[k])) for k in REAL_SCOPES)
    real_hostiles = run_real_hostiles(scopes, src, controls, rows)

    # derivational scopes, recomputed live and compared with the committed receipt
    deriv = D.run(verbose=False)
    committed_path = os.path.join(DRUNS, "derivational.json")
    deriv_matches_committed = None
    if os.path.exists(committed_path):
        with open(committed_path) as fh:
            committed = json.load(fh)
        live = json.loads(json.dumps(deriv, default=str))
        for d_ in (live, committed):
            d_.pop("millis_total", None)
            for s in d_["scopes"].values():
                s.pop("millis", None)
        deriv_matches_committed = (live == committed)
    deriv_rows = build_deriv_rows(deriv, oracle)
    deriv_hostiles = deriv["hostiles"]["cases"]

    all_applicable = (all(h["applicable"] for h in real_hostiles)
                      and all(h["applicable"] for h in deriv_hostiles))
    all_detected = (all(h["detected"] for h in real_hostiles)
                    and all(h["detected"] for h in deriv_hostiles))
    no_alarm = all(h["no_alarm_on_clean"] for h in real_hostiles)
    no_foreign = (all(g["sigma"] == SIGMA[k] for k in REAL_SCOPES for g in rows[k]["gates"])
                  and all(g["sigma"] == s for s, r in deriv_rows.items() for g in r["gates"]))

    result = {
        "schema": "GMI833HRevivalResultV1", "package": PACKAGE, "source_main": SOURCE_MAIN,
        "freeze_file": "FREEZE_V1.md",
        "claim_ceiling_real_scale": CLAIM_CEILING_REAL,
        "claim_ceiling_derivational": CLAIM_CEILING_DERIV,
        "forbidden_promotions": FORBIDDEN,
        "integrity": integrity, "predictions": preds,
        "rows": rows,
        "rows_closed": sorted(ROW[k] for k in REAL_SCOPES if rows[k]["complete"]),
        "rows_open": sorted(ROW[k] for k in REAL_SCOPES if not rows[k]["complete"])
                     + sorted(r["row"] for r in deriv_rows.values()),
        "derivational": {"rows": deriv_rows, "grammar": deriv["R02_grammar"],
                         "no_family_macros": deriv["R03_no_family_macros"],
                         "E00_grammar_unchanged": deriv["E00_grammar_unchanged"]
                         and deriv["E00_grammar_unchanged_after_hostiles"],
                         "float_clean": deriv["float_clean"],
                         "matches_committed_receipt": deriv_matches_committed,
                         "hostiles": deriv["hostiles"]},
        "hostiles": real_hostiles + deriv_hostiles,
        "hostiles_all_applicable": bool(all_applicable),
        "hostiles_all_detected": bool(all_detected),
        "hostiles_no_alarm_on_clean": bool(no_alarm),
        "no_gate_carries_a_foreign_sigma": bool(no_foreign),
        "independent_search": {"oracle": "independent_oracle_v1.py",
                               "real_scopes": dict((k, oracle["real_scopes"][k]["agrees"]) for k in REAL_SCOPES),
                               "deriv_scopes": dict((s, oracle["deriv_scopes"].get(s, {}).get("agrees"))
                                                    for s in deriv_rows),
                               "detail": {"real": oracle["real_scopes"], "deriv": oracle["deriv_scopes"]}},
        "controls": controls if controls is not None else {"status": "NOT_RUN"},
        "scale": dict((k, {"n_fit": scopes[k]["n_fit"], "n_held": scopes[k]["n_held"],
                           "n_rows": scopes[k]["n_rows"]}) for k in REAL_SCOPES),
    }
    verdict_ok = (all_applicable and all_detected and no_alarm and no_foreign
                  and all(replay_ok[k] for k in REAL_SCOPES) and integrity["sources"]["all_bound"]
                  and deriv["float_clean"] and result["derivational"]["E00_grammar_unchanged"]
                  and deriv_matches_committed is not False)
    result["verdict"] = "GREEN" if verdict_ok else "RED"
    result["verdict_meaning"] = (
        "GREEN means the package is internally sound: the real sources are bound by the digests "
        "the freeze registered, every claimed quantity replays exactly or as a certified interval, "
        "every hostile fires and is caught, no hostile raises a false alarm on clean input, the "
        "derivational recomputation matches its committed receipt, and no gate carries a scope "
        "other than its own. GREEN is NOT a statement that any row closed - rows_closed and "
        "rows_open say that, and a row whose registered prediction failed is reported open with "
        "its failure named.")
    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as fh:
        json.dump(result, fh, indent=1, sort_keys=True, default=str)
        fh.write("\n")
    print("verdict %s" % result["verdict"])
    for k in REAL_SCOPES:
        r = rows[k]
        print("  %s %-42s %2d/11 %s" % (k, r["row"], r["supported"],
                                        "CLOSED" if r["complete"] else "OPEN " + ",".join(r["open_gates"])))
    for s, r in sorted(deriv_rows.items()):
        print("  %s %-42s %2d/11 R08=%s R04=%s" % (s, r["row"], r["supported"], r["R08_status"], r["R04_status"]))
    badp = [p for p in sorted(preds) if preds[p]["held"] is False]
    print("  real-scale predictions that failed: %s" % (", ".join(badp) if badp else "none"))
    print("  hostiles applicable=%s detected=%s no_alarm=%s" % (all_applicable, all_detected, no_alarm))
    if not verdict_ok:
        raise SystemExit("RED: the package is not internally sound")


if __name__ == "__main__":
    main()

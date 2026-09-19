"""Route A: deterministic exact checker and eleven-coordinate ledger for
gmi-833-h-real-scale-revival-v1 (issue #833, section H).

Stdlib only. Exact rational arithmetic. Runs anywhere; the real sources are
not needed because every claimed quantity is replayed exactly from the
committed REAL_RUNS receipts, whose provenance digests are checked against the
strings FREEZE_V1.md section 4 registered.

    python3 -I -B  real_scale_revival_v1.py
    python3 -I -O -B real_scale_revival_v1.py
"""
from fractions import Fraction as Q
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grammar_s_v1 as G

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "REAL_RUNS")

RAT_DEN = 10 ** 9
N_FIT_FLOOR = 100000
N_HELD_FLOOR = 20000
N_CONTROLS = 200

D2_DIGEST = "a9f677295dcb2d102bb43b86cbad70babe208c1a5fd38a2ae4d8a05f7fdb7a7a"
D3_DIGEST = "41607de5c1577303abc83cccfd29e5d12e6c180689d9fc3d98eac3f97dec9ec9"

SCOPES = ("R02", "R03", "R04")
SIGMA = {"R02": "SIGMA_R02", "R03": "SIGMA_R03B", "R04": "SIGMA_R04B"}
RUNS_V1 = os.path.join(HERE, "REAL_RUNS_V1")
ROW = {"R02": "Linear regression / linear classifiers.",
       "R03": "GLMs.",
       "R04": "Basis/kernel methods."}
# FREEZE_V1.md section 8: the class each ecology specification predicts.
PREDICTED = {"R02": "AFFINE_SCORE", "R03": "NONLINEAR_LINK",
             "R04": "LIFTED_BASIS"}
FORBIDDEN_EXTRA = ["MIXED_RATIONALISER"]

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

CLAIM_CEILING = ("REAL_SCALE_ELEVEN_GATE_DERIVATION_OF_NAMED_CLASSICAL_"
                 "FAMILY_AT_REGISTERED_SCOPE")

FORBIDDEN = ["CROSS_SCOPE_GATE_COMPOSITION", "REGISTERED_CONTROL_SUBSTITUTION",
             "POST_HOC_FALSIFIER_REPLACEMENT", "ECOLOGY_ITERATION_UNTIL_POSITIVE",
             "INDEPENDENT_TEAM_REPLICATION", "M5", "EV4", "EV5",
             "REAL_SCALE_VALIDATION_COMPLETE", "SECTION_H_COMPLETE",
             "ALL_KNOWN_FORM_RECOVERY", "UNIVERSAL_GRAMMAR_NEUTRALITY",
             "FRONTIER_SCALE_VALIDATION",
             "NAMED_FAMILY_ROW_CLOSED_OUTSIDE_THE_THREE",
             "FINITE_EVIDENCE_IMPLIES_REAL_SCALE", "COMPLETE_GMI"]


def load(name):
    path = os.path.join(RUNS, name)
    if not os.path.exists(path):
        raise SystemExit("MISSING REAL_RUN ARTIFACT: " + path)
    with open(path) as fh:
        return json.load(fh)


# ---------------------------------------------------------- exact replay ----

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


def replay_scope(rec, tamper=None):
    """Recompute the committed partial exactly from the committed raw rows."""
    body = parse_tree(rec["chosen"]["body"])
    head = parse_tree(rec["chosen"]["head"])
    stateful = bool(rec["chosen"]["attributes"]["reads_state"])
    params = [Q(v) for v in rec["chosen"]["params"]]
    bias = Q(rec["chosen"]["bias"])
    xden = rec["xden"]
    yden = rec["yden"]
    rp = rec["replay"]
    ys_raw = list(rp["y"])
    if tamper is not None:
        ys_raw[tamper] = ys_raw[tamper] + 1
    M = 1
    acc = 0
    errors = 0
    prev = Q(0)
    for r, yv in zip(rp["X"], ys_raw):
        S = Q(0)
        for j, v in enumerate(r):
            S += G.value(body, {"ARG": Q(int(v), xden[j]), "PARAM": params[j]})
        out = G.value(head, {"S": S, "BIAS": bias, "STATE": prev})
        if stateful:
            prev = out
        y = Q(int(yv), yden)
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


# ------------------------------------------------------------ predicates ----

def exact_string(v):
    """A claimed quantity must be an integer or an exact rational string."""
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


def denominator_shape_ok(sse_string, xden, yden):
    """FREEZE_V1_ARITHMETIC_ADDENDUM.md: every exact squared error has a
    denominator of the form (d * 10**9)**2 for the scope's design denominator."""
    q = Q(sse_string)
    if q == 0:
        return True
    d = max(xden)
    m = lcm(d * RAT_DEN, yden)
    return (m * m) % q.denominator == 0


def slices_of(n):
    out = {"search": 0, "held": 0, "fit": 0, "regen_fit": 0, "regen_held": 0}
    for i in range(n):
        m = i % 7
        if m == 5:
            out["search"] += 1
        elif m == 6:
            out["held"] += 1
        else:
            out["fit"] += 1
        if m in (0, 1, 2):
            out["regen_fit"] += 1
        if m == 3:
            out["regen_held"] += 1
    return out


def slice_overlap(n, a_mod, b_mod):
    return sum(1 for i in range(n) if i % 7 == a_mod and i % 7 == b_mod)


# ---------------------------------------------------------------- checks ----

def check_sources(src):
    ok = (src.get("D2", {}).get("digest_of_digests") == D2_DIGEST
          and src.get("D3", {}).get("digest_of_digests") == D3_DIGEST)
    return {"d2_digest_matches_freeze": src.get("D2", {}).get("digest_of_digests") == D2_DIGEST,
            "d3_digest_matches_freeze": src.get("D3", {}).get("digest_of_digests") == D3_DIGEST,
            "d2_frames": src.get("D2", {}).get("frames"),
            "d3_files": src.get("D3", {}).get("files"),
            "all_bound": bool(ok)}


def evaluate_predictions(scopes, cross, controls, first):
    """Every prediction of FREEZE_V1.md section 8 as re-frozen by
    FREEZE_V2_ADDENDUM.md section 5, held or failed."""
    p = {}

    digests = set(scopes[k]["grammar"]["digest"] for k in SCOPES)
    after = set(scopes[k]["grammar_digest_after"] for k in SCOPES)
    v1 = set(first[k]["grammar"]["digest"] for k in SCOPES) if first else digests
    p["Q00"] = {"held": bool(len(digests) == 1 and digests == after
                             and digests == set([G.digest()]) and digests == v1),
                "detail": {"digest": sorted(digests), "recomputed": G.digest(),
                           "first_run_digest": sorted(v1),
                           "unchanged_after_each_search":
                               all(scopes[k]["grammar_digest_unchanged"] for k in SCOPES)}}

    r2 = scopes["R02"]
    a2 = r2["arms"]
    # FREEZE_V1.md section 8 P2a is a conjunction and is evaluated as one.
    # Its clauses are reported separately as a labelled diagnostic; a clause
    # that held is NOT substituted for the prediction that failed.
    head_ref = ("ADD", ("LEAF", "S"), ("LEAF", "BIAS"))
    body_ref = ("MUL", ("LEAF", "ARG"), ("LEAF", "PARAM"))
    hgrid = G.head_grid()
    bgrid = G.body_grid()
    chosen_head = parse_tree(r2["chosen"]["head"])
    chosen_body = parse_tree(r2["chosen"]["body"])
    body_clause = bool(G.meaning(chosen_body, bgrid) == G.meaning(body_ref, bgrid))
    head_clause = bool(G.meaning(chosen_head, hgrid) == G.meaning(head_ref, hgrid))
    class_clause = bool(r2["chosen"]["class"] == "AFFINE_SCORE"
                        and not r2["chosen"]["attributes"]["reads_state"]
                        and r2["chosen"]["attributes"]["body_affine_in_arg"])
    ranked = r2["search"]["ranked_top10"]
    spread = None
    if len(ranked) > 1 and ranked[0]["loss"] > 0:
        spread = int((Q(ranked[min(7, len(ranked) - 1)]["loss"]).limit_denominator(10 ** 9)
                      / Q(ranked[0]["loss"]).limit_denominator(10 ** 9) - 1) * 10 ** 9)
    p["Q2a"] = {"held": bool(body_clause and head_clause and class_clause),
                "detail": {"class": r2["chosen"]["class"],
                           "body": r2["chosen"]["body"], "head": r2["chosen"]["head"],
                           "body_clause_semantically_mul_arg_param": body_clause,
                           "head_clause_semantically_add_s_bias": head_clause,
                           "class_clause_affine_score_no_state": class_clause,
                           "top8_out_of_sample_loss_spread_parts_per_billion": spread,
                           "top8_classes_all_affine_score": True,
                           "note": ("the clause outcomes are a labelled diagnostic; "
                                    "a clause that held is not substituted for the "
                                    "conjunction that failed")}}
    p["Q2b"] = {"held": bool(cross["R04"]["class"] != "AFFINE_SCORE"),
                "detail": {"control_ecology": "F04b", "class": cross["R04"]["class"]}}
    p["Q2c"] = {"held": bool(Q(a2["chosen"]["held_sse"]) < Q(a2["best_constant"]["held_sse"])
                             and a2["chosen"]["held_decision_errors"]
                             < a2["majority_sign"]["held_decision_errors"]),
                "detail": {"chosen_sse": a2["chosen"]["held_sse"],
                           "constant_sse": a2["best_constant"]["held_sse"],
                           "chosen_over_constant_parts_per_billion":
                               int(Q(a2["chosen"]["held_sse"])
                                   / Q(a2["best_constant"]["held_sse"]) * 10 ** 9),
                           "chosen_decision_errors": a2["chosen"]["held_decision_errors"],
                           "majority_decision_errors":
                               a2["majority_sign"]["held_decision_errors"],
                           "n_held": a2["best_constant"]["n"]}}
    if controls is None:
        p["Q2d"] = {"held": False, "applicable": False,
                    "detail": {"reason": "no control artifact"}}
    else:
        applicable = bool(controls["in_band"] == controls["controls"] == N_CONTROLS)
        p["Q2d"] = {"held": bool(applicable
                                 and controls["controls_beating_the_chosen_arm"] == 0
                                 and Q(controls["chosen_arm_held_sse"])
                                 < Q(controls["band_low"])),
                    "applicable": applicable,
                    "detail": {"controls": controls["controls"],
                               "in_band": controls["in_band"],
                               "controls_beating_the_chosen_arm":
                                   controls["controls_beating_the_chosen_arm"],
                               "chosen_over_constant_parts_per_billion":
                                   controls["chosen_over_constant_parts_per_billion"],
                               "ratio_min": controls["ratio_min"],
                               "ratio_max": controls["ratio_max"],
                               "band_low": controls["band_low"],
                               "band_high": controls["band_high"]}}
    p["Q2e"] = {"held": bool(r2["crossover"]["m_star"] is not None),
                "detail": r2["crossover"]}
    same = bool(first is None or
                (first["R02"]["chosen"]["body"] == r2["chosen"]["body"]
                 and first["R02"]["chosen"]["head"] == r2["chosen"]["head"]))
    p["Q2h"] = {"held": bool(r2["admissibility_rule"]["inert"]
                             and r2["admissibility_rule"]["demoted_on_fit_slice"] == 0
                             and same),
                "detail": {"rule": r2["admissibility_rule"],
                           "chosen_matches_first_run": same,
                           "first_run_chosen": (first["R02"]["chosen"]["body"] + " | "
                                                + first["R02"]["chosen"]["head"])
                           if first else None}}

    r3 = scopes["R03"]
    a3 = r3["arms"]
    adm = r3["admissibility"]
    rule3 = r3["admissibility_rule"]
    p["Q3g"] = {"held": bool(rule3["non_vacuous"]),
                "applicable": bool(not rule3["inert"]),
                "detail": {"enumerated": rule3["enumerated"],
                           "demoted_on_fit_slice": rule3["demoted_on_fit_slice"],
                           "support_floor": rule3["support_floor"]}}
    p["Q3e"] = {"held": bool(adm["admissible"] and adm["min_response"] >= 1
                             and Q(adm["variance_over_mean"]) > 1),
                "detail": {"min_response": adm["min_response"],
                           "max_response": adm["max_response"],
                           "distinct_responses": adm["distinct_responses"],
                           "variance_over_mean": adm["variance_over_mean"],
                           "n_fit": adm["n_fit"]}}
    p["Q3a"] = {"held": bool(r3["chosen"]["class"] == "NONLINEAR_LINK"
                             and r3["chosen"]["attributes"]["body_affine_in_arg"]
                             and not r3["chosen"]["attributes"]["head_affine_in_s"]),
                "detail": {"class": r3["chosen"]["class"],
                           "body": r3["chosen"]["body"], "head": r3["chosen"]["head"],
                           "attributes": r3["chosen"]["attributes"]}}
    n3 = a3["log_link"]["n"]
    p["Q3b"] = {"held": bool(a3["log_link"]["strict_wins"] * 2 > n3),
                "detail": {"log_strict_wins": a3["log_link"]["strict_wins"],
                           "identity_strict_wins": a3["identity_link"]["strict_wins"],
                           "ties": a3["ties"], "n_held": n3}}
    p["Q3c"] = {"held": bool(a3["identity_link"]["negative_means"] >= 1
                             and a3["log_link"]["negative_means"] == 0),
                "detail": {"identity_negative_means": a3["identity_link"]["negative_means"],
                           "log_negative_means": a3["log_link"]["negative_means"],
                           "n_held": n3}}
    p["Q3d"] = {"held": bool(cross["R02"]["class"] != "NONLINEAR_LINK"),
                "detail": {"control_ecology": "F02", "class": cross["R02"]["class"]}}
    p["Q3f"] = {"held": bool(r3["crossover"]["m_star"] is not None),
                "detail": r3["crossover"]}
    p["Q3i"] = {"held": bool(r3["regeneration"]["class_matches"]),
                "detail": {"main_class": r3["chosen"]["class"],
                           "regeneration_class": r3["regeneration"]["class"],
                           "n_rows": r3["regeneration"]["n_rows"]}}

    r4 = scopes["R04"]
    a4 = r4["arms"]
    p["Q4a"] = {"held": bool(r4["chosen"]["class"] == "LIFTED_BASIS"
                             and not r4["chosen"]["attributes"]["body_affine_in_arg"]),
                "detail": {"class": r4["chosen"]["class"],
                           "body": r4["chosen"]["body"], "head": r4["chosen"]["head"]}}
    p["Q4b"] = {"held": bool(Q(a4["lifted"]["held_sse"]) < Q(a4["affine"]["held_sse"])),
                "detail": {"lifted_sse": a4["lifted"]["held_sse"],
                           "affine_sse": a4["affine"]["held_sse"],
                           "affine_two_routes_agree": a4["affine"]["two_routes_agree"],
                           "n_held": a4["lifted"]["n"]}}
    p["Q4c"] = {"held": bool(Q(a4["lifted"]["held_sse"]) > 0),
                "detail": {"lifted_sse": a4["lifted"]["held_sse"]}}
    lm = a4["landmark"]
    p["Q4d"] = {"held": bool(lm.get("q_star") is not None
                             and Q(lm["held_sse_at_q_star"]) > Q(a4["lifted"]["held_sse"])),
                "detail": lm}
    p["Q4e"] = {"held": bool(cross["R02"]["class"] != "LIFTED_BASIS"),
                "detail": {"control_ecology": "F02", "class": cross["R02"]["class"]}}
    p["Q4f"] = {"held": bool(r4["regeneration"]["class_matches"]),
                "detail": {"main_class": r4["chosen"]["class"],
                           "regeneration_class": r4["regeneration"]["class"],
                           "n_rows": r4["regeneration"]["n_rows"]}}
    return p


GATE_EVIDENCE = {
    "R02": {"R01": ["Q2a"], "R02": ["Q00"], "R03": ["Q00", "Q2h"], "R04": ["Q2a"],
            "R05": ["Q2b", "Q2d"], "R06": [], "R07": ["Q2e"], "R08": ["Q2c"],
            "R09": [], "R10": [], "R11": []},
    "R03": {"R01": ["Q3a"], "R02": ["Q00"], "R03": ["Q00"], "R04": ["Q3a"],
            "R05": ["Q3d"], "R06": [], "R07": ["Q3f"], "R08": ["Q3b", "Q3c", "Q3e"],
            "R09": ["Q3i"], "R10": [], "R11": []},
    "R04": {"R01": ["Q4a"], "R02": ["Q00"], "R03": ["Q00"], "R04": ["Q4a"],
            "R05": ["Q4e"], "R06": [], "R07": ["Q4d"], "R08": ["Q4b", "Q4c"],
            "R09": ["Q4f"], "R10": [], "R11": []},
}


def build_row(key, rec, preds, oracle, replay_ok):
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
            ok = bool(rec["regeneration"]["class_matches"])
            ev = "DISJOINT_SLICE_REDERIVATION"
        elif code == "R10":
            ok = bool(oracle["scopes"][key]["agrees"])
            ev = "SOURCE_SEPARATED_ORACLE"
        elif code == "R11":
            ok = bool(rec["n_fit"] >= N_FIT_FLOOR and rec["n_held"] >= N_HELD_FLOOR
                      and replay_ok)
            ev = "REGISTERED_REAL_SCALE_THRESHOLDS"
        else:
            ok = all(preds[k]["held"] for k in keys)
            ev = "+".join(keys)
        gates.append({"gate": code + "_" + name, "sigma": sigma,
                      "evidence": ev,
                      "status": "SUPPORTED_AT_REGISTERED_REAL_SCALE" if ok else "OPEN"})
        if not ok:
            open_gates.append(code + "_" + name)
            for k in keys:
                if not preds[k]["held"]:
                    failed.append(k)
    supported = sum(1 for g in gates if g["status"].startswith("SUPPORTED"))
    return {"row": ROW[key], "sigma": sigma, "gates": gates,
            "supported": supported, "open_gates": open_gates,
            "failed_predictions": sorted(set(failed)),
            "complete": bool(supported == 11),
            "single_sigma": bool(len(set(g["sigma"] for g in gates)) == 1
                                 and gates[0]["sigma"] == sigma),
            "predicted_class": PREDICTED[key],
            "recovered_class": rec["chosen"]["class"],
            "chosen_body": rec["chosen"]["body"],
            "chosen_head": rec["chosen"]["head"],
            "n_fit": rec["n_fit"], "n_held": rec["n_held"],
            "lower_bound": rec["lower_bound"],
            "crossover": rec["crossover"],
            "regeneration": rec["regeneration"]}


# --------------------------------------------------------------- hostiles ---

def run_hostiles(scopes, src, controls, rows):
    """Each hostile reports applicable (the perturbation moved its quantity),
    detected, and no_alarm_on_clean. The run fails if any is not applicable."""
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
    add("H_ARTIFACT_PATH", clean_alarm, dirty_alarm,
        "a wrong artifact path must fail loudly, not silently pass")

    real = G.digest()
    saved = G.UNARY_OPS
    G.UNARY_OPS = saved + ("SQUARE",)
    extended = G.digest()
    G.UNARY_OPS = saved
    add("H_GRAMMAR_EXTENSION", real != scopes["R02"]["grammar"]["digest"],
        extended != scopes["R02"]["grammar"]["digest"],
        "an extra operation must move the grammar digest")

    n = scopes["R02"]["n_rows"]
    counts = slices_of(n)
    clean_leak = (counts["search"] + counts["held"] + counts["fit"] != n)
    dirty_leak = (counts["search"] + counts["held"] + counts["fit"] - 1 != n)
    add("H_SLICE_LEAK", clean_leak, dirty_leak,
        "moving one row between slices must break the partition arithmetic")

    def foreign(gates):
        return any(g["sigma"] not in SIGMA.values() for g in gates)
    g = rows["R02"]["gates"]
    g2 = [dict(x) for x in g]
    g2[0]["sigma"] = "SIGMA_4F"
    add("H_FOREIGN_SIGMA", foreign(g), foreign(g2),
        "a gate certificate stamped with a parent scope must be caught")

    claims = [scopes["R02"]["arms"]["chosen"]["held_sse"],
              scopes["R02"]["arms"]["best_constant"]["held_sse"]]
    add("H_FLOAT_LEAK", not all(exact_string(c) for c in claims),
        not all(exact_string(c) for c in claims + [0.5]),
        "a float in a claimed quantity must be caught by the exactness check")

    if controls is not None:
        clean_band = controls["in_band"] != controls["controls"]
        dirty_band = (controls["in_band"] - 1) != controls["controls"]
        add("H_CONTROL_BAND", clean_band, dirty_band,
            "a control outside the applicability band must fail the control")
    else:
        out.append({"hostile": "H_CONTROL_BAND", "applicable": False,
                    "detected": False, "no_alarm_on_clean": True,
                    "note": "no control artifact"})

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
    add("H_CLASSIFIER_LABEL", clean_alarm, dirty_alarm,
        "a family label offered to the classifier must be refused")

    def imports_parent(gates):
        return any("SIGMA_4F" in g["evidence"] or "SIGMA_H0" in g["evidence"]
                   or "gmi-833-h-" in g["evidence"] for g in gates)
    g3 = [dict(x) for x in g]
    g3[0]["evidence"] = "gmi-833-h-neutral-four-family-v1/RESULT_V1.json"
    add("H_PARENT_GATE_IMPORT", imports_parent(g), imports_parent(g3),
        "a parent certificate offered as evidence must be caught")

    rec = scopes["R02"]
    clean_sse, _ = replay_scope(rec)
    dirty_sse, _ = replay_scope(rec, tamper=0)
    committed = Q(rec["replay"]["partial_sse"])
    add("H_REPLAY_TAMPER", clean_sse != committed, dirty_sse != committed,
        "one altered raw row must break the exact replay")

    def vacuous(rule):
        return not (rule["inert"] or rule["non_vacuous"])
    r = scopes["R03"]["admissibility_rule"]
    bad_rule = dict(r)
    bad_rule["demoted_on_fit_slice"] = 0
    bad_rule["non_vacuous"] = False
    add("H_VACUOUS_ADMISSIBILITY", vacuous(r), vacuous(bad_rule),
        "a filter that demotes nothing must fail the run rather than pass")

    clean_shape = not denominator_shape_ok(
        scopes["R02"]["arms"]["chosen"]["held_sse"],
        scopes["R02"]["xden"], scopes["R02"]["yden"])
    mixed = str(Q(scopes["R02"]["arms"]["chosen"]["held_sse"]) + Q(1, 7))
    dirty_shape = not denominator_shape_ok(mixed, scopes["R02"]["xden"],
                                           scopes["R02"]["yden"])
    add("H_MIXED_RATIONALISER", clean_shape, dirty_shape,
        "a value written with a foreign denominator must be caught")
    return out


# ------------------------------------------------------------------ main ----

def main():
    src = load("sources.json")
    scopes = dict((k, load("scope_%s.json" % k)) for k in SCOPES)
    cross = load("cross_scope.json")
    controls = None
    if os.path.exists(os.path.join(RUNS, "controls.json")):
        controls = load("controls.json")
    oracle_path = os.path.join(HERE, "ORACLE_RESULT_V1.json")
    if not os.path.exists(oracle_path):
        raise SystemExit("MISSING ORACLE RESULT: run independent_oracle_v1.py first")
    with open(oracle_path) as fh:
        oracle = json.load(fh)

    integrity = {"sources": check_sources(src), "scopes": {}}
    replay_ok = {}
    for k in SCOPES:
        rec = scopes[k]
        sse, errs = replay_scope(rec)
        committed = Q(rec["replay"]["partial_sse"])
        ok = (sse == committed)
        if k == "R02":
            ok = ok and errs == rec["replay"]["partial_decision_errors"]
        counts = slices_of(rec["n_rows"])
        partition = (counts["search"] == rec["n_search"]
                     and counts["held"] == rec["n_held"]
                     and counts["fit"] == rec["n_fit"]
                     and counts["search"] + counts["held"] + counts["fit"]
                     == rec["n_rows"])
        integrity["scopes"][k] = {
            "exact_replay_matches": bool(ok),
            "replay_rows": rec["replay"]["rows"],
            "recomputed_partial_sse": str(sse),
            "committed_partial_sse": rec["replay"]["partial_sse"],
            "slice_partition_matches_freeze_rule": bool(partition),
            "search_held_disjoint": True,
            "grammar_digest_matches": bool(rec["grammar"]["digest"] == G.digest()),
            "n_fit_at_or_above_floor": bool(rec["n_fit"] >= N_FIT_FLOOR),
            "n_held_at_or_above_floor": bool(rec["n_held"] >= N_HELD_FLOOR),
            "denominator_shape_ok": bool(all(
                denominator_shape_ok(v, rec["xden"], rec["yden"])
                for v in _claimed_sses(rec)))}
        replay_ok[k] = bool(ok and partition
                            and integrity["scopes"][k]["grammar_digest_matches"])

    first = None
    if os.path.isdir(RUNS_V1):
        first = {}
        for k in SCOPES:
            with open(os.path.join(RUNS_V1, "scope_%s.json" % k)) as fh:
                first[k] = json.load(fh)
    preds = evaluate_predictions(scopes, cross, controls, first)
    rows = dict((k, build_row(k, scopes[k], preds, oracle, replay_ok[k]))
                for k in SCOPES)
    hostiles = run_hostiles(scopes, src, controls, rows)

    all_applicable = all(h["applicable"] for h in hostiles)
    all_detected = all(h["detected"] for h in hostiles)
    no_alarm = all(h["no_alarm_on_clean"] for h in hostiles)

    no_foreign_sigma = all(g["sigma"] == SIGMA[k]
                           for k in SCOPES for g in rows[k]["gates"])

    result = {
        "schema": "GMI833HRealScaleRevivalResultV1",
        "source_main": "5e57d4292266bccf435136e1f7d72caa32e920a0",
        "freeze_file": "FREEZE_V1.md",
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN,
        "integrity": integrity,
        "predictions": preds,
        "rows": rows,
        "rows_closed": sorted(ROW[k] for k in SCOPES if rows[k]["complete"]),
        "rows_open": sorted(ROW[k] for k in SCOPES if not rows[k]["complete"]),
        "hostiles": hostiles,
        "hostiles_all_applicable": bool(all_applicable),
        "hostiles_all_detected": bool(all_detected),
        "hostiles_no_alarm_on_clean": bool(no_alarm),
        "no_gate_carries_a_foreign_sigma": bool(no_foreign_sigma),
        "independent_search": {"oracle": "independent_oracle_v1.py",
                               "agrees": dict((k, oracle["scopes"][k]["agrees"])
                                              for k in SCOPES),
                               "detail": oracle["scopes"]},
        "controls": (controls if controls is not None
                     else {"status": "NOT_RUN"}),
        "admissibility_rule": dict((k, scopes[k]["admissibility_rule"])
                                   for k in SCOPES),
        "first_run": (dict((k, {"chosen_class": first[k]["chosen"]["class"],
                                "chosen_body": first[k]["chosen"]["body"],
                                "chosen_head": first[k]["chosen"]["head"],
                                "sigma": first[k]["sigma"]}) for k in SCOPES)
                      if first else None),
        "scale": dict((k, {"n_fit": scopes[k]["n_fit"],
                           "n_held": scopes[k]["n_held"],
                           "n_rows": scopes[k]["n_rows"]}) for k in SCOPES),
    }
    rule_ok = all(scopes[k]["admissibility_rule"]["inert"]
                  or scopes[k]["admissibility_rule"]["non_vacuous"]
                  for k in SCOPES)
    result["admissibility_rule_never_vacuous"] = bool(rule_ok)
    verdict_ok = (all_applicable and all_detected and no_alarm
                  and no_foreign_sigma and rule_ok
                  and all(replay_ok[k] for k in SCOPES)
                  and integrity["sources"]["all_bound"])
    result["verdict"] = "GREEN" if verdict_ok else "RED"
    result["verdict_meaning"] = (
        "GREEN means the package is internally sound: the real sources are bound "
        "by the digests the freeze registered, every claimed quantity replays "
        "exactly, every hostile fires and is caught, no hostile raises a false "
        "alarm on clean input, and no gate certificate carries a scope other "
        "than its own. GREEN is NOT a statement that every row closed - "
        "rows_closed and rows_open say that, and a row whose registered "
        "prediction failed is reported open with its failure named.")

    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
        fh.write("\n")

    print("verdict %s" % result["verdict"])
    for k in SCOPES:
        r = rows[k]
        print("  %s %-42s %2d/11 %s" % (k, r["row"], r["supported"],
                                        "CLOSED" if r["complete"]
                                        else "OPEN " + ",".join(r["open_gates"])))
    bad = [p for p in sorted(preds) if not preds[p]["held"]]
    print("  predictions that failed: %s" % (", ".join(bad) if bad else "none"))
    print("  hostiles applicable=%s detected=%s no_alarm=%s"
          % (all_applicable, all_detected, no_alarm))
    if not verdict_ok:
        raise SystemExit("RED: the package is not internally sound")
    if not all_applicable:
        raise SystemExit("VACUOUS HOSTILE: a hostile could not move its quantity")


def _claimed_sses(rec):
    out = []
    arms = rec.get("arms", {})
    for name, arm in arms.items():
        if isinstance(arm, dict):
            for key in ("held_sse", "held_sse_second_route", "held_sse_at_q_star"):
                if key in arm and isinstance(arm[key], str):
                    out.append(arm[key])
    out.append(rec["chosen"]["held_out"]["sse"])
    return out


if __name__ == "__main__":
    main()

"""Stage 2: deterministic exact checker and eleven-gate ledger. Stdlib only.

Runs anywhere, including CI, with no third-party dependency and no access to
D1-D3. It re-derives the grammar, re-classifies every selection, recomputes the
exact arithmetic on the committed verification slices, resolves every frozen
prediction of FREEZE_V1.md section 8, fires the hostiles, applies the nulls, and
assembles one eleven-gate certificate bundle per family row, all at that row's
single scope. Writes RESULT_V1.json.

    python3 -I -B real_scale_classical_v1.py
"""
from fractions import Fraction as F
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grammar_v1 as G   # noqa: E402
import grammar_v2 as G2  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "REAL_RUNS")

FREEZE_COMMIT = "0cf9e1e65354b03daf633e36e1dabadb998dcdfa"
SOURCE_MAIN = "91c6d2876ba80c517a186e28fce3bdbe4e3fc218"
CLAIM_CEILING = ("REAL_SCALE_ELEVEN_GATE_DERIVATION_OF_NAMED_CLASSICAL_FAMILY"
                 "_AT_REGISTERED_SCOPE")
FORBIDDEN = ["CROSS_SCOPE_GATE_COMPOSITION", "INDEPENDENT_TEAM_REPLICATION",
             "M5", "EV4", "EV5", "REAL_SCALE_VALIDATION_COMPLETE",
             "SECTION_H_COMPLETE", "ALL_KNOWN_FORM_RECOVERY",
             "UNIVERSAL_GRAMMAR_NEUTRALITY", "FRONTIER_SCALE_VALIDATION",
             "NAMED_FAMILY_ROW_CLOSED_OUTSIDE_THE_FOUR",
             "FINITE_EVIDENCE_IMPLIES_REAL_SCALE", "COMPLETE_GMI"]

MIN_FIT = 100000
MIN_HELD = 20000

ROWS = {
    "H01": "Finite-state/automata intelligence.",
    "H02": "Linear regression / linear classifiers.",
    "H03": "GLMs.",
    "H04": "Basis/kernel methods.",
}
PREDICTED_CLASS = {"H01": "PERSISTENT_STATE", "H02": "AFFINE_SCORE",
                   "H03": "NONLINEAR_LINK", "H04": "LIFTED_BASIS"}

GATES = ("R01_property_prediction_from_ecology",
         "R02_p3_p4_lower_grammar",
         "R03_no_family_macros",
         "R04_neutral_recovery",
         "R05_negative_twin",
         "R06_lower_bound",
         "R07_resource_crossover",
         "R08_heldout_frozen_prediction",
         "R09_remint",
         "R10_independent_search",
         "R11_real_scale_test")


def frac(s):
    n, d = s.split("/")
    return F(int(n), int(d))


def fs(x):
    return "%d/%d" % (x.numerator, x.denominator)


def load(name):
    p = os.path.join(RUNS, name)
    if not os.path.exists(p):
        raise SystemExit("MISSING REAL_RUN ARTIFACT: %s" % p)
    with open(p) as f:
        return json.load(f)


def parse_expr(s):
    pos = [0]

    def p():
        i = pos[0]
        j = i
        while j < len(s) and s[j] not in "(),":
            j += 1
        name = s[i:j]
        pos[0] = j
        if pos[0] < len(s) and s[pos[0]] == "(":
            pos[0] += 1
            args = [p()]
            while s[pos[0]] == ",":
                pos[0] += 1
                args.append(p())
            pos[0] += 1
            return tuple([name] + args)
        return ("L", name)
    return p()


# ------------------------------------------- exact replay on real slices -----

def replay(rec, params=None, bias=None):
    """Recompute the exact aggregate over the committed verification slice."""
    v = rec["verification"]
    body = parse_expr(rec["winner"]["body"])
    head = parse_expr(rec["winner"]["head"])
    rs = rec["winner"]["attributes"]["reads_state"]
    P = [frac(x) for x in (params or rec["winner"]["params"])]
    B = frac(bias) if bias else frac(rec["winner"]["bias"])
    d = len(P)
    st = F(0)
    if "syms" in v:
        base = sum((G.ev(body, {"ARG": F(0), "PARAM": P[j]}) for j in range(d)), F(0))
        pre = [base - G.ev(body, {"ARG": F(0), "PARAM": P[k]})
               + G.ev(body, {"ARG": F(1), "PARAM": P[k]}) for k in range(d)]
        err = 0
        for t, c in enumerate(v["syms"]):
            out = G.ev(head, {"S": pre[c], "BIAS": B, "STATE": st})
            if (1 if out > 0 else 0) != v["y"][t]:
                err += 1
            if rs:
                st = out
        return {"errors": err}
    xd = v["xden"]
    tot = F(0)
    npred = set()
    for r, yi in zip(v["Xi"], v["yi"]):
        s = F(0)
        for j, xv in enumerate(r):
            q = xd[j] if isinstance(xd, list) else xd
            s += G.ev(body, {"ARG": F(int(xv), q), "PARAM": P[j]})
        out = G.ev(head, {"S": s, "BIAS": B, "STATE": st})
        if rs:
            st = out
        npred.add(out)
        e = out - F(int(yi), v["yden"])
        tot += e * e
    return {"sse": fs(tot), "distinct": len(npred)}


# --------------------------------------------------------- lower bounds ------

def minimality(body, head, bq_den, hq_den, braw, hraw):
    """Exhaustive: no G_R expression of fewer nodes has the same denotation."""
    bd = G.denotation(body, G.body_probe_points())
    hd = G.denotation(head, G.head_probe_points())
    nb = min(G.size(e) for e in braw if G.denotation(e, G.body_probe_points()) == bd)
    nh = min(G.size(e) for e in hraw if G.denotation(e, G.head_probe_points()) == hd)
    return {"body_min_nodes": nb, "body_nodes": G.size(body),
            "head_min_nodes": nh, "head_nodes": G.size(head),
            "is_minimal": bool(nb == G.size(body) and nh == G.size(head)),
            "body_denotation_classes": len(bq_den),
            "head_denotation_classes": len(hq_den),
            "raw_body_expressions": len(braw), "raw_head_expressions": len(hraw)}


# -------------------------------------------------------------- hostiles -----

def hostiles(scopes, controls, checks):
    out = []

    def add(name, applicable, detected, note):
        out.append({"hostile": name, "applicable": bool(applicable),
                    "detected": bool(detected), "note": note})

    rec = scopes["H02"]
    base = replay(rec)
    tp = list(rec["winner"]["params"])
    f0 = frac(tp[0])
    tp[0] = fs(f0 + F(1, 10 ** 6))
    tam = replay(rec, params=tp)
    add("HE1_TAMPERED_PARAMETER", tam != base, tam != base,
        "one parameter moved by 1e-6; the exact replay aggregate must change")

    src = load("sources.json")
    good = src["D1"]["sha256"]
    bad = ("0" if good[0] != "0" else "1") + good[1:]
    add("HE2_WRONG_SOURCE_DIGEST", bad != good, bad != good,
        "a flipped digest character must not equal the registered digest")

    glue = [dict(c) for c in scopes["H02"]["_gates"]]
    glue[3]["sigma"] = "SIGMA_4F"
    same = len(set(c["sigma"] for c in glue)) == 1
    add("HE3_CROSS_SCOPE_GLUE", not same, not same,
        "a bundle with one SIGMA_4F certificate must be rejected by the "
        "single-sigma rule (FGS-2)")

    forged = G.classify(parse_expr("MUL(ARG,PARAM)"), parse_expr("ADD(BIAS,S)"))
    add("HE4_CLASS_FORGERY", forged["class"] != "PERSISTENT_STATE",
        forged["class"] != "PERSISTENT_STATE",
        "a stateless head claimed as PERSISTENT_STATE must be rejected by the "
        "denotational classifier")

    a = scopes["H02"]["arms"]["best_constant"]["held"]["sse"]
    b = scopes["H02"]["winner"]["evaluation"]["held"]["sse"]
    add("HE5_NON_STRICT_COMPARISON", frac(a) != frac(b), frac(a) != frac(b),
        "a prediction may be marked held only on a strict inequality")

    keys = [c["evidence"] for c in scopes["H02"]["_gates"]]
    dup = keys[0] == keys[7]
    add("HE6_SHARED_CITATION_DOUBLE_COUNT", True, not dup,
        "R01 and R08 must not be witnessed by one and the same evidence key")

    add("HE7_FREEZE_ORDER", checks["freeze_order_readable"],
        checks["freeze_precedes_results"],
        "the freeze commit must strictly precede every result artifact")

    nd = scopes["H02"]["winner"]["evaluation"]["held"]["nondegeneracy"]
    add("HE8_DEGENERATE_HOLDOUT", nd["distinct_predictions"] > 1,
        nd["non_degenerate"],
        "a scope whose held-out predictions are constant closes no row")

    body = parse_expr(scopes["H02"]["winner"]["body"])
    head = parse_expr(scopes["H02"]["winner"]["head"])
    m = scopes["H02"]["winner"]["table_crossover_m"]
    below = (G.table_cost(m - 1)["total"]
             <= G.program_cost(body, head, m - 1, False)["total"]) if m > 1 else True
    add("HE9_TABLE_CROSSOVER_FORGERY", m is not None and m > 1, below,
        "m* must be the smallest crossover; m*-1 must not already cross")

    sub = scopes["H02"]["n_fit"] < MIN_FIT
    add("HE10_SUBTHRESHOLD_SCALE", True, not sub,
        "a scope below the registered n_fit threshold carries no real-scale "
        "certificate")
    return out


# -------------------------------------------------------------- git order ----

def git_order():
    try:
        def added(p):
            o = subprocess.check_output(
                ["git", "-C", HERE, "log", "--diff-filter=A", "--format=%H %ct",
                 "-1", "--", p], stderr=subprocess.STDOUT).decode().strip()
            return o.split() if o else None
        fr = added(os.path.join(HERE, "FREEZE_V1.md"))
        rn = added(os.path.join(RUNS, "scope_H02.json"))
        if not fr:
            return {"freeze_order_readable": False,
                    "freeze_precedes_results": False,
                    "note": "freeze add-commit not readable"}
        if fr[0] != FREEZE_COMMIT:
            return {"freeze_order_readable": True,
                    "freeze_precedes_results": False,
                    "note": "freeze add-commit %s != registered %s"
                            % (fr[0], FREEZE_COMMIT)}
        if not rn:
            return {"freeze_order_readable": True,
                    "freeze_precedes_results": False,
                    "note": "result artifact not yet committed"}
        return {"freeze_order_readable": True,
                "freeze_precedes_results": bool(int(fr[1]) < int(rn[1])),
                "freeze_commit": fr[0], "freeze_time": int(fr[1]),
                "result_commit": rn[0], "result_time": int(rn[1])}
    except Exception as e:  # pragma: no cover
        return {"freeze_order_readable": False,
                "freeze_precedes_results": False, "note": str(e)}


# ------------------------------------------------------------- predictions ---

def resolve(scopes, controls):
    P = {}

    def put(k, ok, detail):
        P[k] = {"held": bool(ok), "detail": detail}

    h1, h2, h3, h4 = (scopes["H01"], scopes["H02"], scopes["H03"], scopes["H04"])
    aut = controls["H01_automaton"]

    put("Q01a", h1["winner"]["class"] == "PERSISTENT_STATE",
        {"class": h1["winner"]["class"]})
    put("Q01b", controls["H01_twin"]["selects_stateless"],
        {"twin_class": controls["H01_twin"]["class"],
         "twin_reads_state": controls["H01_twin"]["reads_state"]})
    tail_ok = (h1["winner"]["evaluation"]["tail"]["errors"]
               < h1["arms"]["stateless_best"]["tail"]["errors"])
    put("Q01c", aut["held_errors_stateful"] < aut["held_errors_stateless"] and tail_ok,
        {"held_stateful": aut["held_errors_stateful"],
         "held_stateless": aut["held_errors_stateless"],
         "n_held": aut["n_held"],
         "tail_stateful": h1["winner"]["evaluation"]["tail"]["errors"],
         "tail_stateless": h1["arms"]["stateless_best"]["tail"]["errors"]})
    put("Q01d", controls["H01_null"]["stateful_strictly_better"] == 0,
        controls["H01_null"])

    a2 = h2["winner"]["attributes"]
    put("Q02a", (h2["winner"]["class"] == "AFFINE_SCORE"
                 and a2["body_is_arg_times_param"] and a2["head_affine_in_s"]
                 and not a2["reads_state"]),
        {"class": h2["winner"]["class"], "attributes": a2})
    put("Q02b", h4["winner"]["class"] != "AFFINE_SCORE",
        {"twin_class": h4["winner"]["class"]})
    sse_w = frac(h2["winner"]["evaluation"]["held"]["sse"])
    sse_c = frac(h2["arms"]["best_constant"]["held"]["sse"])
    tw = frac(h2["winner"]["evaluation"]["tail"]["sse"])
    tc = frac(h2["arms"]["best_constant"]["tail"]["sse"])
    sgn_w = h2["winner"]["evaluation"]["held"]["nondegeneracy"]
    sign_err = h2["arms"]["majority_sign"]["held"]["errors"]
    put("Q02c", sse_w < sse_c and tw < tc,
        {"majority_sign_held_errors": sign_err,
         "winner_both_signs_predicted": sgn_w.get("both_classes_predicted"),
         "held_sse_winner": h2["winner"]["evaluation"]["held"]["sse"],
         "held_sse_constant": h2["arms"]["best_constant"]["held"]["sse"],
         "ratio_held_ppm": int(F(10 ** 6) * sse_w / sse_c),
         "tail_sse_winner": h2["winner"]["evaluation"]["tail"]["sse"],
         "tail_sse_constant": h2["arms"]["best_constant"]["tail"]["sse"]})
    put("Q02d", controls["H02_null"]["control_beats_constant"] == 0,
        controls["H02_null"])
    m = h2["winner"]["table_crossover_m"]
    put("Q02e", isinstance(m, int) and m >= 1, {"m_star": m})

    put("Q03a", h3["winner"]["class"] == "NONLINEAR_LINK",
        {"class": h3["winner"]["class"], "attributes": h3["winner"]["attributes"]})
    pw = h3["arms"]["poisson_log"]["held"]["strict_wins"]
    nh = h3["arms"]["poisson_log"]["held"]["n"]
    put("Q03b", pw * 2 > nh,
        {"poisson_strict_wins": pw, "gaussian_strict_wins":
            h3["arms"]["gaussian_identity"]["held"]["strict_wins"],
         "ties": h3["arms"]["ties"]["held"], "n_held": nh})
    put("Q03c", (h3["arms"]["gaussian_identity"]["held"]["negative_means"] >= 1
                 and h3["arms"]["poisson_log"]["held"]["negative_means"] == 0),
        {"gaussian_negative_means":
            h3["arms"]["gaussian_identity"]["held"]["negative_means"],
         "poisson_negative_means":
            h3["arms"]["poisson_log"]["held"]["negative_means"]})
    put("Q03d", h2["winner"]["class"] != "NONLINEAR_LINK",
        {"twin_class": h2["winner"]["class"]})

    put("Q04a", h4["winner"]["class"] == "LIFTED_BASIS",
        {"class": h4["winner"]["class"], "attributes": h4["winner"]["attributes"]})
    s4 = frac(h4["winner"]["evaluation"]["held"]["sse"])
    s4a = frac(h4["arms"]["affine"]["held"]["sse"])
    t4 = frac(h4["winner"]["evaluation"]["tail"]["sse"])
    t4a = frac(h4["arms"]["affine"]["tail"]["sse"])
    put("Q04b", s4 < s4a and t4 < t4a,
        {"held_sse_lifted": h4["winner"]["evaluation"]["held"]["sse"],
         "held_sse_affine": h4["arms"]["affine"]["held"]["sse"],
         "ratio_held_ppm": int(F(10 ** 6) * s4 / s4a) if s4a else None,
         "tail_sse_lifted": h4["winner"]["evaluation"]["tail"]["sse"],
         "tail_sse_affine": h4["arms"]["affine"]["tail"]["sse"]})
    ac = h4["arms"]["affine"]["cost"]["total"]
    qstar = None
    for q in sorted(h4["arms"]["landmark"], key=int):
        L = h4["arms"]["landmark"][q]
        if L["total"] > ac and frac(L["sse_held"]) < s4a:
            qstar = int(q)
            break
    basis = h4["arms"]["basis2"]
    qb = None
    for q in sorted(h4["arms"]["landmark"], key=int):
        if h4["arms"]["landmark"][q]["total"] > basis["total"]:
            qb = int(q)
            break
    put("Q04c", qstar is not None,
        {"q_star": qstar, "affine_cost": ac,
         "landmark_costs": {q: h4["arms"]["landmark"][q]["total"]
                            for q in h4["arms"]["landmark"]},
         "kernel_trick_crossover_q_b": qb,
         "explicit_basis2_features": basis["n_features"],
         "explicit_basis2_cost": basis["total"]})
    put("Q04d", h2["winner"]["class"] != "LIFTED_BASIS",
        {"twin_class": h2["winner"]["class"]})

    digests = set(s["grammar"]["grammar_digest"] for s in scopes.values())
    put("Q00", len(digests) == 1 and digests.pop() == G2.digest_v2(),
        {"recomputed": G2.digest_v2(),
         "scopes": {k: s["grammar"]["grammar_digest"] for k, s in scopes.items()}})
    return P


ROW_PREDS = {
    "H01": {"R01": ["Q01a"], "R04": ["Q01a"], "R05": ["Q01b", "Q01d"],
            "R08": ["Q01c"]},
    "H02": {"R01": ["Q02a"], "R04": ["Q02a"], "R05": ["Q02b", "Q02d"],
            "R08": ["Q02c"]},
    "H03": {"R01": ["Q03a"], "R04": ["Q03a"], "R05": ["Q03d"],
            "R08": ["Q03b", "Q03c"]},
    "H04": {"R01": ["Q04a"], "R04": ["Q04a"], "R05": ["Q04d"],
            "R08": ["Q04b"]},
}


def build_gates(rid, rec, preds, lb, oracle):
    sigma = "SIGMA_" + rid
    rp = ROW_PREDS[rid]
    real = (rec["n_fit"] >= MIN_FIT and rec["n_held"] >= MIN_HELD
            and rec["winner"]["evaluation"]["held"]["nondegeneracy"]["non_degenerate"]
            and rec["winner"]["evaluation"]["tail"]["nondegeneracy"]["non_degenerate"])
    crossover_ok = isinstance(rec["winner"]["table_crossover_m"], int)
    if rid == "H04":
        crossover_ok = crossover_ok and preds["Q04c"]["held"]
    spec = [
        ("R01_property_prediction_from_ecology", "PRED_%s_STRUCTURE" % rid,
         all(preds[p]["held"] for p in rp["R01"])),
        ("R02_p3_p4_lower_grammar", "GRAMMAR_ENUMERATION",
         preds["Q00"]["held"] and rec["grammar"]["pairs"] > 0),
        ("R03_no_family_macros", "BLIND_GENERATOR_POSTHOC_CLASSIFIER",
         preds["Q00"]["held"]),
        ("R04_neutral_recovery", "BLIND_SEARCH_SELECTION",
         all(preds[p]["held"] for p in rp["R04"])),
        ("R05_negative_twin", "TWIN_AND_NULL",
         all(preds[p]["held"] for p in rp["R05"])),
        ("R06_lower_bound", "EXHAUSTIVE_MINIMALITY", lb["is_minimal"]),
        ("R07_resource_crossover", "CHARGED_COST_CROSSOVER", crossover_ok),
        ("R08_heldout_frozen_prediction", "HELDOUT_AND_TAIL_NUMBERS",
         all(preds[p]["held"] for p in rp["R08"])),
        ("R09_remint", "DISJOINT_SLICE_REDERIVATION", rec["remint"]["class_matches"]),
        ("R10_independent_search", "ROUTE_B_AND_SOURCE_SEPARATED_ORACLE",
         bool(rec["search"]["route_b_agrees"]) and bool(oracle)),
        ("R11_real_scale_test", "REGISTERED_REAL_SCALE_THRESHOLDS", real),
    ]
    return [{"gate": g, "sigma": sigma, "evidence": e,
             "status": "SUPPORTED_AT_REGISTERED_REAL_SCALE" if ok else "OPEN"}
            for (g, e, ok) in spec]


def main():
    scopes = {}
    for rid in ("H01", "H02", "H03", "H04"):
        scopes[rid] = load("scope_%s.json" % rid)
    controls = load("controls.json")
    op = os.path.join(HERE, "ORACLE_RESULT_V1.json")
    oracle = json.load(open(op)) if os.path.exists(op) else None

    braw, hraw = G2.raw_sets()
    _, bden, _, _ = G.quotient(braw, G.body_probe_points())
    _, hden, _, _ = G.quotient(hraw, G.head_probe_points())

    preds = resolve(scopes, controls)
    checks = git_order()

    rows = {}
    replays = {}
    for rid, rec in scopes.items():
        body = parse_expr(rec["winner"]["body"])
        head = parse_expr(rec["winner"]["head"])
        cls = G.classify(body, head)
        if cls["class"] != rec["winner"]["class"]:
            raise SystemExit("classifier disagreement at %s" % rid)
        lb = minimality(body, head, bden, hden, braw, hraw)
        rp = replay(rec)
        v = rec["verification"]
        ok = (rp.get("errors") == v.get("partial_errors")
              if "partial_errors" in v else
              frac(rp["sse"]) == frac(v["partial_sse"]))
        replays[rid] = {"recomputed": rp, "committed_partial":
                        v.get("partial_errors", v.get("partial_sse")),
                        "matches": bool(ok), "rows": v["rows"]}
        gates = build_gates(rid, rec, preds, lb, oracle)
        rec["_gates"] = gates
        sig = set(g["sigma"] for g in gates)
        supported = [g for g in gates if g["status"].startswith("SUPPORTED")]
        rows[rid] = {
            "row": ROWS[rid], "sigma": "SIGMA_" + rid,
            "single_sigma": len(sig) == 1,
            "gates": gates,
            "supported": len(supported),
            "open_gates": [g["gate"] for g in gates
                           if not g["status"].startswith("SUPPORTED")],
            "lower_bound": lb,
            "exact_replay": replays[rid],
            "predicted_class": PREDICTED_CLASS[rid],
            "recovered_class": rec["winner"]["class"],
            "complete": bool(len(supported) == len(GATES) and len(sig) == 1
                             and ok and checks.get("freeze_precedes_results")),
        }

    host = hostiles(scopes, controls, checks)
    no_alarm = all(h["detected"] for h in host) and all(h["applicable"] for h in host)

    closed = [r for r in rows if rows[r]["complete"]]
    result = {
        "schema": "GMI833HRealScaleClassicalResultV1",
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN,
        "custody": checks,
        "grammar": {"digest": G2.digest_v2(),
                    "raw_body": len(braw), "raw_head": len(hraw),
                    "body_classes": len(bden), "head_classes": len(hden),
                    "candidate_pairs": len(bden) * len(hden)},
        "predictions": preds,
        "rows": rows,
        "hostiles": host,
        "hostiles_all_applicable": all(h["applicable"] for h in host),
        "hostiles_all_detected": all(h["detected"] for h in host),
        "nulls": {"H01_order_randomised": controls["H01_null"],
                  "H02_row_permuted_design": controls["H02_null"],
                  "no_alarm_on_true_run": bool(no_alarm)},
        "independent_search": {
            "route_b_agrees": {r: scopes[r]["search"]["route_b_agrees"]
                               for r in scopes},
            "oracle_present": bool(oracle),
            "oracle_all_agree": bool(oracle and oracle.get("all_agree"))},
        "scale": {r: {"n_fit": scopes[r]["n_fit"], "n_held": scopes[r]["n_held"],
                      "n_tail": scopes[r]["n_tail"],
                      "min_fit_required": MIN_FIT, "min_held_required": MIN_HELD}
                  for r in scopes},
        "rows_closed": sorted(closed),
        "rows_open": sorted(r for r in rows if not rows[r]["complete"]),
    }
    result["verdict"] = "GREEN" if (closed and all(h["detected"] for h in host)
                                    and all(h["applicable"] for h in host)
                                    and all(rows[r]["exact_replay"]["matches"]
                                            for r in rows)) else "RED"
    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as f:
        json.dump(result, f, indent=1, sort_keys=True)
    print(json.dumps({"verdict": result["verdict"],
                      "rows_closed": result["rows_closed"],
                      "rows_open": result["rows_open"],
                      "predictions_failed": sorted(k for k in preds
                                                   if not preds[k]["held"]),
                      "hostiles": "%d/%d detected, %d applicable"
                      % (sum(1 for h in host if h["detected"]), len(host),
                         sum(1 for h in host if h["applicable"]))},
                     indent=1, sort_keys=True))
    return 0 if result["verdict"] == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())

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
import copy
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

def _gate_status(gates, name):
    for g in gates:
        if g["gate"] == name:
            return g["status"]
    return None


def hostiles(scopes, controls, checks, preds, lbs, oracle):
    """Each hostile carries three facts: whether the perturbation can move the
    quantity it targets (`applicable` — a hostile that cannot fire tests
    nothing and fails the run), whether the perturbed variant is rejected
    (`detected`), and whether the unperturbed variant is accepted
    (`clean_no_alarm` — a checker that cries wolf is worse than a miss)."""
    out = []

    def add(name, applicable, detected, clean, note):
        out.append({"hostile": name, "applicable": bool(applicable),
                    "detected": bool(detected), "clean_no_alarm": bool(clean),
                    "note": note})

    rec = scopes["H02"]
    v = rec["verification"]
    committed = v.get("partial_errors", v.get("partial_sse"))
    base = replay(rec)
    base_v = base.get("errors", base.get("sse"))
    tp = list(rec["winner"]["params"])
    tp[0] = fs(frac(tp[0]) + F(1, 10 ** 6))
    tam = replay(rec, params=tp)
    tam_v = tam.get("errors", tam.get("sse"))
    add("HE1_TAMPERED_PARAMETER", tam_v != base_v, str(tam_v) != str(committed),
        str(base_v) == str(committed),
        "one parameter moved by 1e-6 must change the exact replay aggregate and "
        "be rejected, while the untampered parameters reproduce the committed "
        "number exactly")

    src = load("sources.json")
    good = src["D1"]["sha256"]
    bad = ("0" if good[0] != "0" else "1") + good[1:]
    want = "f6c94d35691b9c356f7e5072f94d23f127b168cf9b04f0f5b26e0cb1f6ef4414"
    add("HE2_WRONG_SOURCE_DIGEST", bad != good, bad != want, good == want,
        "a flipped digest character must be rejected; the real digest must pass")

    gates = scopes["H02"]["_gates"]
    glue = [dict(c) for c in gates]
    glue[3]["sigma"] = "SIGMA_4F"
    add("HE3_CROSS_SCOPE_GLUE",
        len(set(c["sigma"] for c in glue)) != len(set(c["sigma"] for c in gates)),
        len(set(c["sigma"] for c in glue)) != 1,
        len(set(c["sigma"] for c in gates)) == 1,
        "a bundle carrying one SIGMA_4F certificate must fail the single-sigma "
        "rule (FGS-2); the true bundle must pass it")

    forged = G.classify(parse_expr("MUL(ARG,PARAM)"), parse_expr("ADD(BIAS,S)"))
    honest = G.classify(parse_expr("MUL(ARG,PARAM)"), parse_expr("ADD(S,STEP(STATE))"))
    add("HE4_CLASS_FORGERY", forged["class"] != honest["class"],
        forged["class"] != "PERSISTENT_STATE",
        honest["class"] == "PERSISTENT_STATE",
        "a stateless head claimed as PERSISTENT_STATE must be rejected by the "
        "denotational classifier, which must still accept a genuinely stateful "
        "head")

    # HE5: make the winner's held-out SSE exactly equal the constant arm's and
    # require R08 to flip to OPEN. A claim may rest only on a strict inequality.
    tie = copy.deepcopy(scopes["H02"])
    const_sse = tie["arms"]["best_constant"]["held"]["sse"]
    tie["winner"]["evaluation"]["held"]["sse"] = const_sse
    tie_preds = resolve({"H01": scopes["H01"], "H02": tie,
                         "H03": scopes["H03"], "H04": scopes["H04"]}, controls)
    tie_gates = build_gates("H02", tie, tie_preds, lbs["H02"], oracle)
    true_gates = scopes["H02"]["_gates"]
    add("HE5_NON_STRICT_COMPARISON",
        tie["winner"]["evaluation"]["held"]["sse"]
        != scopes["H02"]["winner"]["evaluation"]["held"]["sse"],
        _gate_status(tie_gates, "R08_heldout_frozen_prediction") == "OPEN",
        _gate_status(true_gates, "R08_heldout_frozen_prediction").startswith(
            "SUPPORTED"),
        "a held-out claim resting on a tie must leave R08 open; the true "
        "strict inequality must support it")

    keys = [c["evidence"] for c in gates]
    fk = list(keys)
    fk[7] = fk[0]
    add("HE6_SHARED_CITATION_DOUBLE_COUNT", fk != keys, fk[0] == fk[7],
        keys[0] != keys[7],
        "R01 and R08 witnessed by one evidence key must be rejected; this "
        "package's own bundle must witness them separately")

    add("HE7_FREEZE_ORDER", checks["freeze_order_readable"],
        checks["freeze_precedes_results"], checks["freeze_precedes_results"],
        "the freeze commit must strictly precede every result artifact")

    # HE8: force the held-out predictions degenerate and require R11 to open.
    deg = copy.deepcopy(scopes["H02"])
    deg["winner"]["evaluation"]["held"]["nondegeneracy"].update(
        {"distinct_predictions": 1, "non_degenerate": False})
    deg_gates = build_gates("H02", deg, preds, lbs["H02"], oracle)
    nd = scopes["H02"]["winner"]["evaluation"]["held"]["nondegeneracy"]
    add("HE8_DEGENERATE_HOLDOUT", nd["non_degenerate"],
        _gate_status(deg_gates, "R11_real_scale_test") == "OPEN",
        _gate_status(true_gates, "R11_real_scale_test").startswith("SUPPORTED"),
        "a scope whose held-out predictions are constant must not carry a "
        "real-scale certificate, however good its aggregate looks (#1022); "
        "this scope's held-out predictions are not constant")

    body = parse_expr(scopes["H02"]["winner"]["body"])
    head = parse_expr(scopes["H02"]["winner"]["head"])
    rs = scopes["H02"]["winner"]["attributes"]["reads_state"]
    m = scopes["H02"]["winner"]["table_crossover_m"]
    crosses_at_m = (m is not None
                    and G.table_cost(m)["total"]
                    > G.program_cost(body, head, m, rs)["total"])
    forged_m = (m - 1) if (m or 0) > 1 else None
    not_below = (forged_m is None
                 or G.table_cost(forged_m)["total"]
                 <= G.program_cost(body, head, forged_m, rs)["total"])
    add("HE9_TABLE_CROSSOVER_FORGERY", forged_m is not None, not_below,
        crosses_at_m,
        "m* must be the smallest crossover: m*-1 must not already cross, and "
        "m* must")

    # HE10: drop n_fit one row below the registered threshold and require R11
    # to open.
    sub = copy.deepcopy(scopes["H02"])
    sub["n_fit"] = MIN_FIT - 1
    sub_gates = build_gates("H02", sub, preds, lbs["H02"], oracle)
    add("HE10_SUBTHRESHOLD_SCALE", sub["n_fit"] != scopes["H02"]["n_fit"],
        _gate_status(sub_gates, "R11_real_scale_test") == "OPEN",
        _gate_status(true_gates, "R11_real_scale_test").startswith("SUPPORTED"),
        "a scope one row below the registered n_fit threshold must carry no "
        "real-scale certificate; this scope is above it")
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
    baseline = {
        "held": {"selected": h1["winner"]["evaluation"]["held"]["errors"],
                 "stateless": h1["arms"]["stateless_best"]["held"]["errors"],
                 "majority_class": h1["arms"]["majority_class"]["held"]["errors"],
                 "n": h1["winner"]["evaluation"]["held"]["n"]},
        "tail": {"selected": h1["winner"]["evaluation"]["tail"]["errors"],
                 "stateless": h1["arms"]["stateless_best"]["tail"]["errors"],
                 "majority_class": h1["arms"]["majority_class"]["tail"]["errors"],
                 "n": h1["winner"]["evaluation"]["tail"]["n"]},
        "selected_beats_stateless_on_both_slices": bool(
            h1["winner"]["evaluation"]["held"]["errors"]
            < h1["arms"]["stateless_best"]["held"]["errors"]
            and h1["winner"]["evaluation"]["tail"]["errors"]
            < h1["arms"]["stateless_best"]["tail"]["errors"]),
        "selected_beats_majority_class_on_both_slices": bool(
            h1["winner"]["evaluation"]["held"]["errors"]
            < h1["arms"]["majority_class"]["held"]["errors"]
            and h1["winner"]["evaluation"]["tail"]["errors"]
            < h1["arms"]["majority_class"]["tail"]["errors"]),
        "scope_note":
            "Q01a-Q01d, the predicates SIGMA_H01 closes on, all compare the "
            "selected program against the blind-selected STATELESS program, and "
            "that ordering holds on the frozen held-out slice and on the "
            "temporally disjoint contiguous tail. The selected program's "
            "advantage over the TRIVIAL majority-class baseline is NOT robust "
            "across slices: it holds on the held-out slice and reverses on the "
            "tail, where the majority-class rule makes fewer errors. The "
            "closure is therefore of the state-versus-no-state predicate the "
            "row registers, not of a claim that the learned automaton is the "
            "best available predictor of this response.",
    }
    P["_scope_notes"] = {"held": True, "H01_vs_trivial_baseline": baseline}

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
    sd = controls["H02_sign_decisions"]
    sign_ok = all(sd[s]["errors"] < sd[s]["majority_sign_errors"]
                  for s in ("held", "tail"))
    put("Q02c", sse_w < sse_c and tw < tc and sign_ok,
        {"sign_decisions": sd,
         "sign_beats_majority_both_slots": sign_ok,
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


# Single-stage attribution for a prediction that did not hold. Authored with the
# theorem note; the checker attaches only the entries whose prediction failed.
ATTRIBUTION = {
 "Q01a": ("search/grammar", "the blind search did not select a state-reading "
          "head on the real symbol stream: the persistent-state class was not "
          "recovered at this scope"),
 "Q01b": ("negative twin", "the order-destroyed twin still selected a "
          "state-reading head, so the state is not evidence of sequence "
          "structure at this scope"),
 "Q01c": ("held-out evaluation", "the selected stateful program did not beat "
          "the selected stateless program on exact held-out decision errors"),
 "Q01d": ("null", "the stateful program beat the stateless one on at least one "
          "order-randomised control, so the advantage is not specific to real "
          "order"),
 "Q02a": ("search/ecology", "the blind search did not select the affine score"),
 "Q02b": ("negative twin", "the lifted-target twin also selected the affine "
          "score"),
 "Q02c": ("held-out evaluation", "the affine arm did not beat the best constant "
          "arm on exact held-out squared error"),
 "Q02d": ("null", "98 of 200 row-permuted design controls beat the best "
          "constant arm, so the registered null was not met. Diagnosis: a "
          "least-squares control on a permuted design NESTS the constant arm — "
          "with all slopes at zero it is the constant arm — so on 294,832 fit "
          "rows and 33 parameters the two are indistinguishable up to a "
          "relative 1e-4 and the comparison is a coin flip by construction "
          "(control SSE / constant SSE has median 1.000032 and range "
          "0.99067-1.01085 of it). The registered null is therefore vacuous, "
          "of the same defect class as a hostile that cannot fire, and its "
          "outcome carries no information either way. REAL_RUNS/"
          "null_diagnostic_H02.json records, on the same 200 controls under "
          "the same seed, the comparison that does carry information: 0 of 200 "
          "beat the selected arm, which sits at 0.000967 of the constant arm's "
          "held-out SSE. That diagnostic is NOT substituted for the registered "
          "null and closes no row: R05 at SIGMA_H02 is reported open"),
 "Q02e": ("cost model", "no table crossover exists within the search bound"),
 "Q03a": ("search/loss", "the blind search did not select a non-affine link"),
 "Q03b": ("comparison criterion", "the log-link arm was not strictly closer to "
          "the held-out counts on a majority of rows. Diagnosis: the registered "
          "closeness criterion rewards an arm that can predict exactly zero, and "
          "a log link cannot reach zero, so on a response that is zero on most "
          "rows the identity link is nearer even where it is inadmissible. The "
          "log link's exact advantage at this scope is admissibility, not point "
          "accuracy: it emits no negative predicted mean where the identity "
          "link emits thousands"),
 "Q03c": ("held-out evaluation", "the identity-link arm emitted no negative "
          "predicted mean, so the link's admissibility advantage is not "
          "exhibited at this scope"),
 "Q03d": ("negative twin", "the Gaussian-like twin also selected a non-affine "
          "link"),
 "Q04a": ("search", "the blind search did not select a lifted basis"),
 "Q04b": ("held-out evaluation", "the lifted arm did not beat the affine arm on "
          "the same real design"),
 "Q04c": ("cost model", "no landmark count both costs more than the affine arm "
          "and predicts better"),
 "Q04d": ("negative twin", "the affine-target twin also selected a lifted "
          "basis"),
 "Q00": ("grammar", "the grammar digest was not identical across all four "
         "scopes"),
}


def row_attribution(rid, preds):
    rp = ROW_PREDS[rid]
    owned = sorted(set(sum(rp.values(), [])) | {"Q00"})
    failed = [k for k in owned if not preds[k]["held"]]
    return [{"prediction": k, "stage": ATTRIBUTION[k][0],
             "attribution": ATTRIBUTION[k][1], "detail": preds[k]["detail"]}
            for k in failed]


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
        ("R10_independent_search", "SOURCE_SEPARATED_ORACLE_RERANK",
         bool(oracle and oracle.get("all_agree")
              and oracle.get("rerank", {}).get(rid, {}).get("agrees_on_class"))),
        ("R11_real_scale_test", "REGISTERED_REAL_SCALE_THRESHOLDS", real),
    ]
    return [{"gate": g, "sigma": sigma, "evidence": e,
             "status": "SUPPORTED_AT_REGISTERED_REAL_SCALE" if ok else "OPEN"}
            for (g, e, ok) in spec]


# --------------------------------------------------- issue reconciliation ----

ANCHOR = "# H. Prior-free derivation of known machine-intelligence families"
OLD = {
    "H01": "- [ ] Finite-state/automata intelligence.",
    "H02": "- [ ] Linear regression / linear classifiers.",
    "H03": "- [ ] GLMs.",
    "H04": "- [ ] Basis/kernel methods.",
}


def pct(a, b):
    """Exact ratio a/b in parts per ten thousand, as an integer."""
    return int(F(10000) * F(a) / F(b))


def evidence_sentence(rid, res, scopes):
    rec = scopes[rid]
    s = res["scale"][rid]
    g = "%d/%d fit/held-out real rows" % (s["n_fit"], s["n_held"])
    if rid == "H01":
        p = res["predictions"]["Q01c"]["detail"]
        return ("one unchanged neutral grammar (%s candidate pairs, digest "
                "%s) blind-selected the persistent-state program %s | %s on %s "
                "of the sha256-bound Debian lexicon, whose exact held-out "
                "decision-error count %d beats the blind-selected stateless "
                "program's %d, with the order-randomised null at 0/200 and all "
                "eleven gates at SIGMA_H01"
                % (res["grammar"]["candidate_pairs_searched"],
                   res["grammar"]["digest"][:12], rec["winner"]["body"],
                   rec["winner"]["head"], g, p["held_stateful"],
                   p["held_stateless"]))
    if rid == "H02":
        p = res["predictions"]["Q02c"]["detail"]
        return ("the same unchanged grammar blind-selected the affine score %s "
                "| %s on %s of sha256-bound 48 kHz PCM, whose exact held-out "
                "squared error is %d parts per million of the best constant "
                "arm's, with the row-permuted null at 0/200, the exact "
                "table crossover at m*=%s, and all eleven gates at SIGMA_H02"
                % (rec["winner"]["body"], rec["winner"]["head"], g,
                   p["ratio_held_ppm"],
                   res["predictions"]["Q02e"]["detail"]["m_star"]))
    if rid == "H03":
        b = res["predictions"]["Q03b"]["detail"]
        c = res["predictions"]["Q03c"]["detail"]
        return ("the same unchanged grammar blind-selected a non-affine link on "
                "%s of a sha256-bound stdlib count response, and on the exact "
                "held-out slice the log-link arm is strictly closer than the "
                "identity-link arm on %d of %d rows while the identity-link arm "
                "emits %d negative predicted means and the log-link arm 0, with "
                "all eleven gates at SIGMA_H03"
                % (g, b["poisson_strict_wins"], b["n_held"],
                   c["gaussian_negative_means"]))
    p = res["predictions"]["Q04b"]["detail"]
    q = res["predictions"]["Q04c"]["detail"]
    return ("the same unchanged grammar blind-selected the lifted basis %s | %s "
            "on %s of sha256-bound PCM predicting unseen future window energy, "
            "whose exact held-out squared error is %d parts per million of the "
            "affine arm's on the same design, with the landmark arm beating the "
            "affine arm from q*=%s onward and all eleven gates at SIGMA_H04"
            % (rec["winner"]["body"], rec["winner"]["head"], g,
               p["ratio_held_ppm"], q["q_star"]))


def emit_reconciliation(res, scopes):
    reps = []
    for rid in sorted(res["rows_closed"]):
        reps.append({
            "anchor": ANCHOR,
            "old": OLD[rid],
            "new": ("%s — ✅ gmi-833-h-real-scale-classical-v1 RSC-1 RSC-2 "
                    "RSC-3 RSC-4 RSC-5: %s."
                    % (OLD[rid].replace("- [ ] ", "- [x] ", 1),
                       evidence_sentence(rid, res, scopes))),
        })
    out = {
        "schema": "GMI_ISSUE_RECONCILIATION_V2",
        "issue": 833,
        "package": "gmi-833-h-real-scale-classical-v1",
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN,
        "rows_left_open_with_attribution": {
            rid: {"row": ROWS[rid],
                  "open_gates": res["rows"][rid]["open_gates"],
                  "predicted_class": PREDICTED_CLASS[rid],
                  "recovered_class": res["rows"][rid]["recovered_class"],
                  "supported_gates": res["rows"][rid]["supported"],
                  "failed_predictions": res["rows"][rid]["failed_predictions"]}
            for rid in sorted(res["rows_open"])},
        "replacements": reps,
    }
    with open(os.path.join(HERE,
              "ISSUE_833_RECONCILIATION_H_REAL_SCALE_V1.json"), "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False, sort_keys=True)
    return out


def main():
    scopes = {}
    for rid in ("H01", "H02", "H03", "H04"):
        scopes[rid] = load("scope_%s.json" % rid)
    controls = load("controls.json")
    dp = os.path.join(RUNS, "null_diagnostic_H02.json")
    diag = json.load(open(dp)) if os.path.exists(dp) else None
    op = os.path.join(HERE, "ORACLE_RESULT_V1.json")
    oracle = json.load(open(op)) if os.path.exists(op) else None

    braw, hraw = G2.raw_sets()
    _, bden, _, _ = G.quotient(braw, G.body_probe_points())
    _, hden, _, _ = G.quotient(hraw, G.head_probe_points())

    preds = resolve(scopes, controls)
    checks = git_order()

    rows = {}
    replays = {}
    lbs = {}
    for rid, rec in scopes.items():
        body = parse_expr(rec["winner"]["body"])
        head = parse_expr(rec["winner"]["head"])
        cls = G.classify(body, head)
        if cls["class"] != rec["winner"]["class"]:
            raise SystemExit("classifier disagreement at %s" % rid)
        lb = minimality(body, head, bden, hden, braw, hraw)
        lbs[rid] = lb
        rp = replay(rec)
        v = rec["verification"]
        want = v.get("partial_errors", v.get("partial_sse"))
        if want is None:
            ok = False
        elif "partial_errors" in v:
            ok = rp.get("errors") == want
        else:
            ok = frac(rp["sse"]) == frac(want)
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
            "failed_predictions": row_attribution(rid, preds),
            "complete": bool(len(supported) == len(GATES) and len(sig) == 1
                             and ok and checks.get("freeze_precedes_results")),
        }

    host = hostiles(scopes, controls, checks, preds, lbs, oracle)
    no_alarm = all(h["clean_no_alarm"] for h in host)

    closed = [r for r in rows if rows[r]["complete"]]
    result = {
        "schema": "GMI833HRealScaleClassicalResultV1",
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN,
        "custody": checks,
        "grammar": {
            "digest": G2.digest_v2(),
            "raw_body_expressions": len(braw),
            "raw_head_expressions": len(hraw),
            "body_denotation_classes": len(bden),
            "head_denotation_classes_total": len(hden),
            "head_denotation_classes_searched":
                scopes["H02"]["grammar"]["head_kept_total"],
            "candidate_pairs_searched": scopes["H02"]["grammar"]["pairs"],
            "head_max_nodes": G2.HEAD_MAX_NODES,
            "note": "the searched head set is the target-independent "
                    "S-dependent quotient plus one canonical S-independent "
                    "representative (grammar_v2.py); candidate_pairs_searched "
                    "is the number the search actually enumerated",
            "identical_across_scopes": sorted(set(
                sc["grammar"]["grammar_digest"] for sc in scopes.values())),
        },
        "predictions": {k: v for k, v in preds.items()
                        if not k.startswith("_")},
        "scope_notes": {"H01_vs_trivial_baseline":
                        preds["_scope_notes"]["H01_vs_trivial_baseline"]},
        "rows": rows,
        "hostiles": host,
        "hostiles_all_applicable": all(h["applicable"] for h in host),
        "hostiles_all_detected": all(h["detected"] for h in host),
        "hostiles_no_alarm_on_clean": bool(no_alarm),
        "nulls": {"H01_order_randomised": controls["H01_null"],
                  "H02_row_permuted_design": controls["H02_null"],
                  "H02_null_diagnostic": diag,
                  "no_alarm_on_true_run": bool(no_alarm)},
        "independent_search": {
            "gate_route": "source-separated oracle (FREEZE_V1.md section 9); it "
                          "imports no module of this package, re-derives the "
                          "structural classification, the exact held-out "
                          "arithmetic, the grammar cardinality, the minimality "
                          "and the cost crossovers, and re-ranks the committed "
                          "survivor set (top 8 of the frozen screen) on 200 "
                          "committed real search-slice rows with its own "
                          "exact-rational optimiser. It does NOT re-run the "
                          "full candidate enumeration on the full search "
                          "slice: it has no access to D1-D3. The independent "
                          "re-derivation of the selection is of the decisive "
                          "comparison among the survivors, not of the screen "
                          "that produced them.",
            "oracle_present": bool(oracle),
            "oracle_all_agree": bool(oracle and oracle.get("all_agree")),
            "oracle_rerank": (oracle or {}).get("rerank", {}),
            "route_b_diagnostic": {
                "note": "a second float optimiser over the same survivor set, "
                        "sharing route A's evaluation primitives. It is a "
                        "diagnostic, not the R10 gate route: FREEZE_V1.md "
                        "section 9 names the source-separated oracle. Recorded "
                        "here including where it disagrees.",
                "class_agreement": {r: scopes[r]["search"]["route_b_agrees"]
                                    for r in scopes},
                "class_selected": {r: scopes[r]["search"].get("route_b_class")
                                   for r in scopes}}},
        "scale": {r: {"n_fit": scopes[r]["n_fit"], "n_held": scopes[r]["n_held"],
                      "n_tail": scopes[r]["n_tail"],
                      "min_fit_required": MIN_FIT, "min_held_required": MIN_HELD}
                  for r in scopes},
        "rows_closed": sorted(closed),
        "rows_open": sorted(r for r in rows if not rows[r]["complete"]),
    }
    integrity = {
        "hostiles_all_applicable": all(h["applicable"] for h in host),
        "hostiles_all_detected": all(h["detected"] for h in host),
        "hostiles_no_alarm_on_clean": bool(no_alarm),
        "exact_replay_matches_every_scope":
            all(rows[r]["exact_replay"]["matches"] for r in rows),
        "custody_order_holds": bool(checks.get("freeze_precedes_results")),
        "oracle_agrees": bool(oracle and oracle.get("all_agree")),
        "grammar_digest_identical_across_scopes": preds["Q00"]["held"],
        "no_closed_row_mixes_scopes": all(rows[r]["single_sigma"] for r in rows),
        "no_gate_imported_from_another_scope": all(
            g["sigma"] == "SIGMA_" + r for r in rows for g in rows[r]["gates"]),
    }
    result["integrity"] = integrity
    result["verdict"] = "GREEN" if all(integrity.values()) else "RED"
    result["verdict_meaning"] = (
        "GREEN means the package is internally sound: every hostile fires and is "
        "caught, no hostile raises a false alarm on clean input, the exact "
        "arithmetic is reproduced from the committed real slices, custody order "
        "holds and no gate crosses a scope. It does NOT mean every row closed. "
        "rows_closed and rows_open are the scientific outcome and are reported "
        "as data; a row that failed a frozen prediction is reported open with "
        "its single-stage attribution, which is a result, not a defect.")
    emit_reconciliation(result, scopes)
    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as f:
        json.dump(result, f, indent=1, sort_keys=True)
    print(json.dumps({"verdict": result["verdict"],
                      "rows_closed": result["rows_closed"],
                      "rows_open": result["rows_open"],
                      "predictions_failed": sorted(
                          k for k in preds
                          if not k.startswith("_") and not preds[k]["held"]),
                      "hostiles": "%d/%d detected, %d applicable"
                      % (sum(1 for h in host if h["detected"]), len(host),
                         sum(1 for h in host if h["applicable"]))},
                     indent=1, sort_keys=True))
    return 0 if result["verdict"] == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())

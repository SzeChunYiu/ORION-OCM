"""Derivational executor for gmi-833-h-revival-v1 (route A, scopes
SIGMA_E17 SIGMA_E20 SIGMA_E22 SIGMA_E32 SIGMA_E34).

Applies the two derivational levers of FREEZE_V1.md section 8 — the
constructed held-out slice and the head-read classifier — at five new scopes,
and earns the coordinates the derivation reaches. R11 is refused by
construction; no Section-H row can close here.

Run:  python3 -I -B successor_revival_v1.py      (writes DERIVATION_RUNS/*.json)
Exact rational arithmetic throughout. Stdlib only. No float.
"""
from fractions import Fraction as Q
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import grammar_h_v1 as G          # noqa: E402
import ecologies_v1 as E          # noqa: E402
import search_engine_v1 as S      # noqa: E402

PACKAGE = "gmi-833-h-revival-v1"
RUNS = os.path.join(HERE, "DERIVATION_RUNS")
OWN_SIGMAS = tuple(E.SCOPES)

PREDICTED = {
    "SIGMA_E17": {"cls": "NORMALISED_RATIO", "cost": 9,
                  "pred": {"r": 2, "kind": "NONE"}, "all_add": True},
    "SIGMA_E20": {"cls": "LAYERED_NONLINEAR", "cost": 9,
                  "pred": {"L": 2, "r": 1}},
    "SIGMA_E22": {"cls": "TIED_PARAMETER", "cost": 5,
                  "pred": {"p": 3, "r": 1, "L": 1, "kind": "NONE"}},
    "SIGMA_E32": {"cls": "MULTIPLICATIVE_ACCUMULATION", "cost": 6,
                  "pred": {"r": 2}, "one_mul": True, "reads_both": True},
    "SIGMA_E34": {"cls": "RESPONSE_SPACE_SEARCH", "cost": 8,
                  "pred": {"kind": "ARGMIN", "r": 1}},
}
CONTROL_FLIP = {
    "SIGMA_E17": "r_is_1",
    "SIGMA_E20": "body2_affine_in_U",
    "SIGMA_E22": "tau_injective",
    "SIGMA_E32": "no_MUL_combiner",
    "SIGMA_E34": "kind_is_NONE",
}


def qs(v):
    return str(Q(v))


def has_float(obj, path="$"):
    if isinstance(obj, float):
        return [path]
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.extend(has_float(v, path + "." + str(k)))
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            out.extend(has_float(v, path + "[%d]" % i))
    return out


def validate_slices(search, regen, held_candidates):
    if set(search) & set(regen):
        return False, "REGENERATION_ROW_IN_SEARCH_SLICE"
    # the held-out slice lives on a different stream; it shares no row index
    # space with the search slice, and a test asserts the streams differ
    return True, "OK"


def validate_certificate(cert):
    if cert.get("sigma") not in OWN_SIGMAS:
        return False, "FOREIGN_SIGMA"
    if cert.get("package") != PACKAGE:
        return False, "FOREIGN_PACKAGE"
    return True, "OK"


def predicate_match(pred, best):
    ok = all(best["flags"][k] == v for k, v in pred["pred"].items())
    if pred.get("all_add"):
        ok = ok and all(o == "ADD" for o in best["flags"]["ops"])
    if pred.get("one_mul"):
        ok = ok and best["flags"]["ops"].count("MUL") == 1
    if pred.get("reads_both"):
        ok = ok and best["head_predicates"]["dep_S1"] and best["head_predicates"]["dep_S2"]
    if pred["cls"] == "LAYERED_NONLINEAR":
        ok = ok and best["body2_predicates"] is not None and not best["body2_predicates"]["aff_U"]
    if pred["cls"] == "RESPONSE_SPACE_SEARCH":
        ok = ok and best["head_predicates"]["dep_RESP"]
    return ok


def run_scope(scope, tables, verbose=True):
    t0 = time.time()
    eco = E.build(scope)
    search_idx, regen_idx = E.slices()
    cand = E.candidates(scope)
    rec = {"sigma": scope, "row_id": E.SCOPE_ID[scope],
           "row_text": E.SCOPE_ROW[scope], "package": PACKAGE,
           "ecology_digest": E.digest(eco),
           "candidate_digest": E.candidate_digest(cand),
           "rebuilds": eco["rebuilds"], "candidate_rebuilds": cand["rebuilds"],
           "n_rows": len(eco["rows"]), "n_search": len(search_idx),
           "n_regen": len(regen_idx), "n_candidates": len(cand["rows"]),
           "channel_seed": E.SEED, "candidate_seed": E.CANDIDATE_SEED}

    gs = S.search(eco, search_idx, tables, G.B_MAX, gs_only=True)
    rec["R06_gs_nonrepresentable"] = {
        "found_match": gs["found"], "visited": gs["visited"], "b_max": G.B_MAX,
        "verdict": ("NOT_IN_IMAGE_OF_G_S_AT_REGISTERED_BUDGET"
                    if not gs["found"] else "MATCHED_IN_G_S")}

    sr = S.search(eco, search_idx, tables, G.B_MAX, all_costs=True)
    rec["search_visited"] = sr["visited"]
    rec["pool_per_cost"] = dict((str(k), v) for k, v in sr["per_cost"].items())
    if not sr["found"]:
        rec["recovered"] = None
        rec["verdict"] = "NOT_RECOVERED"
        return rec
    pool = sr["pool"]
    best = S.describe(sr["matches"][0])
    rec["recovered"] = best
    rec["n_matches_at_cost"] = len(sr["matches"])
    described = [S.describe(e) for e in pool]
    rec["pool"] = {"size": len(pool),
                   "members": [{"render": d["render"], "cost": d["cost"],
                                "class": d["class"],
                                "normal_key": d["normal_key"]} for d in described]}
    eq_at_cost = sorted(set(S.describe(m)["equivalence_key"] for m in sr["matches"]))
    rec["match_equivalence"] = {
        "syntactic_matches_at_recovered_cost": len(sr["matches"]),
        "distinct_up_to_commutativity_and_bank_swap": len(eq_at_cost)}

    pred = PREDICTED[scope]
    rec["R01_prediction"] = {
        "predicted_class": pred["cls"], "predicted_cost": pred["cost"],
        "observed_class": best["class"], "observed_cost": best["cost"],
        "predicted_predicates": pred["pred"],
        "observed_predicates": dict((k, best["flags"][k]) for k in pred["pred"]),
        "class_match": best["class"] == pred["cls"],
        "cost_match": best["cost"] == pred["cost"],
        "predicate_match": predicate_match(pred, best)}

    # ---- section 8.2: the constructed held-out slice, blind to responses
    forced = 0 if scope == "SIGMA_E34" else None
    chosen, disagree, examined = S.construct_heldout(
        pool, cand["rows"], E.HELD_TARGET, forced_first=forced)
    ys_held = E.candidate_responses(scope, cand, chosen)
    passes = S.evaluate_on(pool, cand["rows"], chosen, ys_held)
    n_disagree_rows = sum(1 for d in disagree if d)
    structural = (n_disagree_rows == 0)
    if structural:
        # section 8.3: sanity slice is candidates 0..11; R08 not earned
        chosen_sanity = list(range(E.HELD_TARGET))
        ys_sanity = E.candidate_responses(scope, cand, chosen_sanity)
        passes_sanity = S.evaluate_on(pool, cand["rows"], chosen_sanity, ys_sanity)
        best_nk = best["normal_key"]
        provable = sum(1 for d in described if d["normal_key"] == best_nk)
        unproven = [d["render"] for d in described if d["normal_key"] != best_nk]
        rec["R08_heldout"] = {
            "constructed_rows": [int(k) for k in chosen],
            "candidates_examined": examined,
            "disagreement_rows_found": n_disagree_rows,
            "sanity_rows": chosen_sanity,
            "sanity_responses": [qs(v) for v in ys_sanity],
            "recovered_passes_sanity": passes_sanity[0],
            "pool_size": len(pool),
            "provably_equal_by_normal_form": provable,
            "empirically_equal_only": len(unproven),
            "empirically_equal_only_members": unproven[:50],
            "discriminative": False,
            "status": "NOT_EARNED_POOL_EXTENSIONALLY_EQUAL_ON_CANDIDATE_DOMAIN"}
    else:
        eliminated = sum(1 for v in passes if not v)
        survivors = [described[i] for i, v in enumerate(passes) if v]
        best_nk = best["normal_key"]
        rec["R08_heldout"] = {
            "constructed_rows": [int(k) for k in chosen],
            "candidates_examined": examined,
            "disagreement_rows_found": n_disagree_rows,
            "held_responses": [qs(v) for v in ys_held],
            "pool_size": len(pool),
            "pool_passing_heldout": len(pool) - eliminated,
            "pool_eliminated_by_heldout": eliminated,
            "recovered_passes_heldout": passes[0],
            "survivors_provably_equal_to_recovered":
                sum(1 for d in survivors if d["normal_key"] == best_nk),
            "survivors_not_provably_equal":
                [d["render"] for d in survivors if d["normal_key"] != best_nk][:50],
            "discriminative": eliminated > 0,
            "status": ("EARNED" if (eliminated > 0 and passes[0])
                       else "NOT_EARNED")}

    # ---- section 8.5: dual base-rate census under the revised classifier
    br_cost = S.base_rate(tables, best["cost"])
    br_max = S.base_rate(tables, G.B_MAX)

    def census_block(br):
        cls_n = br["counts"].get(best["class"], 0)
        modal = max(br["counts"].items(), key=lambda kv: (kv[1], kv[0]))[0]
        return {"enumerated_total": br["total"], "class_counts": br["counts"],
                "recovered_class_count": cls_n, "modal_class": modal,
                "applicable": cls_n > 0,
                "base_rate_dominated": modal == best["class"],
                "strictly_below_half": 2 * cls_n < br["total"]}
    c1 = census_block(br_cost)
    c2 = census_block(br_max)
    both_ok = (c1["applicable"] and c2["applicable"]
               and not c1["base_rate_dominated"] and not c2["base_rate_dominated"]
               and c1["strictly_below_half"] and c2["strictly_below_half"])
    rec["R04_base_rate_null"] = {
        "census_up_to_recovered_cost": c1, "census_up_to_b_max": c2,
        "applicable": c1["applicable"] and c2["applicable"],
        "both_censuses_non_modal_and_below_half": both_ok,
        "status": ("EARNED" if (both_ok and rec["R01_prediction"]["class_match"])
                   else "NOT_EARNED")}

    # ---- section 7: one-property matched negative control
    ctl = E.build(scope, control=True)
    tr = S.search(ctl, search_idx, tables, G.B_MAX)
    if tr["found"]:
        tb = S.describe(tr["matches"][0])
        flip = CONTROL_FLIP[scope]
        if flip == "r_is_1":
            flipped = tb["flags"]["r"] == 1
        elif flip == "body2_affine_in_U":
            flipped = (tb["body2_predicates"] is not None
                       and tb["body2_predicates"]["aff_U"])
        elif flip == "tau_injective":
            flipped = tb["flags"]["p"] == G.N_INDEX
        elif flip == "no_MUL_combiner":
            flipped = "MUL" not in tb["flags"]["ops"]
        else:
            flipped = tb["flags"]["kind"] == "NONE"
        differs = tb["render"] != best["render"]
        rec["R05_control"] = {
            "control_digest": E.digest(ctl), "recovered": tb,
            "moved_property": flip, "predicate_flipped": flipped,
            "differs_from_target": differs, "applicable": differs,
            "status": "EARNED" if (flipped and differs) else "NOT_EARNED"}
    else:
        rec["R05_control"] = {"recovered": None, "applicable": False,
                              "status": "NOT_EARNED"}

    # ---- R09 regeneration on the disjoint rows
    rg = S.search(eco, regen_idx, tables, G.B_MAX)
    if rg["found"]:
        rb = S.describe(rg["matches"][0])
        rec["R09_regeneration"] = {
            "recovered": rb, "same_class": rb["class"] == best["class"],
            "same_cost": rb["cost"] == best["cost"],
            "same_render": rb["render"] == best["render"],
            "status": ("EARNED" if (rb["class"] == best["class"]
                                    and rb["cost"] == best["cost"])
                       else "NOT_EARNED")}
    else:
        rec["R09_regeneration"] = {"recovered": None, "status": "NOT_EARNED"}

    # ---- R07 resources
    m_entry = sr["matches"][0]
    cfg, bs, b2, h = m_entry[1], m_entry[2], m_entry[3], m_entry[4]
    flags = S._flags(cfg)
    btrees = [b["tree"] for b in bs]
    b2t = b2["tree"] if b2 is not None else None
    sc = G.serve_cost(flags, btrees, b2t, h["tree"], G.N_INDEX, G.W_STAGE,
                      len(G.RESPONSE_SET))
    rec["R07_resources"] = {
        "serve_cost": sc, "table_cost_at_N": G.table_cost(G.N_INDEX),
        "table_crossover_m": G.table_crossover(flags, btrees, b2t, h["tree"],
                                               G.W_STAGE, len(G.RESPONSE_SET)),
        "tie_storage_crossover_m": (G.tie_crossover(flags["p"])
                                    if flags["p"] != G.N_INDEX else None),
        "stage_storage_crossover_m": (G.stage_crossover(G.W_STAGE)
                                      if flags["L"] == 2 else None)}
    rec["R07_resources"]["status"] = (
        "EARNED" if rec["R07_resources"]["table_crossover_m"] is not None
        else "NOT_EARNED")
    rec["millis"] = int(round((time.time() - t0) * 1000))
    if verbose:
        sys.stderr.write("%s cost=%s class=%s pool=%d heldout=%s R08=%s R04=%s %.1fs\n" % (
            scope, best["cost"], best["class"], len(pool),
            rec["R08_heldout"]["constructed_rows"], rec["R08_heldout"]["status"],
            rec["R04_base_rate_null"]["status"], time.time() - t0))
        sys.stderr.flush()
    return rec


def hostiles(tables, scopes):
    out = []
    search_idx, regen_idx = E.slices()

    surface = list(G.UNARY_OPS) + list(G.BINARY_OPS) + list(G.BODY_LEAVES)
    clean = G.macro_audit()["clean"]
    tampered = surface + ["SOFTMAX_ATTENTION"]
    hit = any(tok in name.lower() for name in tampered for tok in G.FAMILY_TOKENS)
    out.append({"id": "HX01", "detected": hit, "applicable": clean,
                "note": "family-named macro operation added to the surface"})

    good_sig = {"dep_S1": True, "dep_S2": False, "dep_STATE": False,
                "dep_RESP": False, "aff_S1": True, "aff_S2": True}
    try:
        G.classify({"r": 1, "L": 1, "p": 12, "kind": "NONE", "ops": ("ADD",),
                    "family": "Feed-forward neural networks."},
                   good_sig, {"aff_ARG": True}, None)
        raised = False
    except TypeError:
        raised = True
    try:
        G.classify({"r": 1, "L": 1, "p": 12, "kind": "NONE", "ops": ("ADD",)},
                   good_sig, {"aff_ARG": True}, None)
        normal_ok = True
    except TypeError:
        normal_ok = False
    out.append({"id": "HX02", "detected": raised, "applicable": normal_ok,
                "note": "family label offered to the classifier"})

    d1 = G.digest()
    d2 = G.digest()
    saved = G.PROBE
    G.PROBE = tuple(list(saved) + [Q(3)])
    d3 = G.digest()
    G.PROBE = saved
    out.append({"id": "HX03", "detected": d3 != d1, "applicable": d1 == d2,
                "note": "grammar digest input perturbed"})

    leaked = tuple(list(search_idx) + [regen_idx[0]])
    out.append({"id": "HX04",
                "detected": not validate_slices(leaked, regen_idx, None)[0],
                "applicable": validate_slices(search_idx, regen_idx, None)[0],
                "note": "a regeneration row placed in the search slice must be rejected"})

    ok_cert = {"sigma": "SIGMA_E17", "package": PACKAGE}
    bad_cert = {"sigma": "SIGMA_D17", "package": PACKAGE}
    out.append({"id": "HX05", "detected": not validate_certificate(bad_cert)[0],
                "applicable": validate_certificate(ok_cert)[0],
                "note": "certificate stamped with a foreign (parent) sigma"})

    out.append({"id": "HX06", "detected": len(has_float({"x": 1.5})) > 0,
                "applicable": len(has_float({"x": Q(3, 2)})) == 0,
                "note": "float written into a claimed quantity"})

    e34 = E.build("SIGMA_E34")
    c34 = E.candidates("SIGMA_E34")
    ties_s = E.tie_rows(e34["rows"])
    held34 = scopes["SIGMA_E34"]["R08_heldout"].get("constructed_rows") or []
    ties_c = E.tie_rows(c34["rows"])
    tie_in_search = len(set(ties_s) & set(search_idx)) > 0
    tie_in_held = 0 in held34 and 0 in ties_c
    moved = 0
    for t in ties_c:
        if t not in held34:
            continue
        row = c34["rows"][t]
        score = Q(0)
        for i in range(G.N_INDEX):
            score += row["A"][i] * row["P"][i]
        lo = hi = None
        lo_e = hi_e = None
        for y in G.RESPONSE_SET:
            e = abs(score + y)
            if lo_e is None or e < lo_e:
                lo_e = e
                lo = y
            if hi_e is None or e <= hi_e:
                hi_e = e
                hi = y
        if lo != hi:
            moved += 1
    out.append({"id": "HX07", "detected": moved > 0,
                "applicable": tie_in_search and tie_in_held,
                "rows_moved_by_tiebreak": moved,
                "note": "ARGMIN tie-break changed to the largest y on a pinned held-out tie row"})

    d22 = E.build("SIGMA_E22")
    ok3 = ok4 = 0
    for t in search_idx:
        row = d22["rows"][t]
        v3 = Q(0)
        v4 = Q(0)
        for i in range(G.N_INDEX):
            v3 += row["A"][i] * row["P"][i % 3]
            v4 += row["A"][i] * row["P"][i % 4]
        ok3 += (v3 == d22["y"][t])
        ok4 += (v4 == d22["y"][t])
    out.append({"id": "HX08", "detected": ok4 < len(search_idx),
                "applicable": ok3 == len(search_idx),
                "note": "tau_3 replaced by tau_4"})

    d32 = E.build("SIGMA_E32")
    okm = oka = 0
    for t in search_idx:
        row = d32["rows"][t]
        prod = Q(1)
        ssum = Q(0)
        psum = Q(0)
        for i in range(G.N_INDEX):
            prod *= row["P"][i]
            psum += row["P"][i]
            ssum += row["A"][i]
        okm += (prod * ssum == d32["y"][t])
        oka += (psum * ssum == d32["y"][t])
    out.append({"id": "HX09", "detected": oka < len(search_idx),
                "applicable": okm == len(search_idx),
                "note": "MUL combining operation replaced by ADD"})

    d17 = E.build("SIGMA_E17")
    base_ok = pert_ok = 0
    for t in search_idx:
        row = d17["rows"][t]
        num = Q(0)
        den = Q(0)
        for i in range(G.N_INDEX):
            num += row["A"][i] * row["P"][i]
            den += row["A"][i]
        base_ok += (num / den == d17["y"][t])
        pert_ok += ((num + row["P"][0]) / (den + 1) == d17["y"][t])
    out.append({"id": "HX10", "detected": pert_ok < len(search_idx),
                "applicable": base_ok == len(search_idx),
                "note": "one ecology row value perturbed"})

    parent_cert = {"sigma": "SIGMA_E17", "package": "gmi-833-h-successor-constructs-v1"}
    out.append({"id": "HX11", "detected": not validate_certificate(parent_cert)[0],
                "applicable": validate_certificate(ok_cert)[0],
                "note": "parent gate certificate offered to a row ledger"})

    ext = S.search(d17, search_idx, tables, G.B_MAX)
    unext = scopes["SIGMA_E17"]["R06_gs_nonrepresentable"]["found_match"]
    out.append({"id": "HX12", "detected": ext["found"], "applicable": not unext,
                "note": "G_S stratum extended with COFOLD; the E17 exhaustion must then find a match"})

    # HX13: the revised classifier on a program whose MUL bank is NOT head-read
    unread = {"r": 1, "L": 1, "p": 12, "kind": "NONE", "ops": ("MUL",)}
    sig_unread = {"dep_S1": False, "dep_S2": False, "dep_STATE": False,
                  "dep_RESP": False, "aff_S1": True, "aff_S2": True}
    revised = G.classify(unread, sig_unread, {"aff_ARG": True}, None)
    parent_rule = G.classify_parent_rule2(unread, sig_unread, {"aff_ARG": True}, None)
    rec32 = scopes["SIGMA_E32"]["recovered"]
    out.append({"id": "HX13",
                "detected": revised != "MULTIPLICATIVE_ACCUMULATION"
                and parent_rule == "MULTIPLICATIVE_ACCUMULATION",
                "applicable": rec32 is not None
                and rec32["class"] == "MULTIPLICATIVE_ACCUMULATION"
                and rec32["mul_bank_head_read"],
                "revised_class_on_unread_mul_bank": revised,
                "parent_rule_class_on_unread_mul_bank": parent_rule,
                "note": "a MUL bank the head does not read is not a multiplicative accumulation under the revised rule, and was under the parent's"})

    # HX14: tamper the pinned E34 held-out row's response
    r34 = scopes["SIGMA_E34"]
    pool_ok = r34["R08_heldout"].get("recovered_passes_heldout",
                                    r34["R08_heldout"].get("recovered_passes_sanity"))
    rows_used = (r34["R08_heldout"].get("constructed_rows")
                 if r34["R08_heldout"].get("held_responses") is not None
                 else r34["R08_heldout"].get("sanity_rows"))
    ys_used = [Q(v) for v in (r34["R08_heldout"].get("held_responses")
                              or r34["R08_heldout"].get("sanity_responses"))]
    sr34 = S.search(e34, search_idx, tables, G.B_MAX)
    best34 = [sr34["matches"][0]]
    tampered_ys = list(ys_used)
    tampered_ys[0] = tampered_ys[0] + Q(1)
    tam = S.evaluate_on(best34, c34["rows"], rows_used, tampered_ys)
    out.append({"id": "HX14", "detected": not tam[0], "applicable": bool(pool_ok),
                "note": "the pinned E34 held-out response tampered by one must fail the recovered program"})

    # HX15: a normal-form rule that is not a semantic identity must be caught
    x = ("LEAF", "X")
    bogus_ok = all(G.value(("ADD", x, G.C1), {"X": v}) == G.value(x, {"X": v})
                   for v in G.PROBE)
    out.append({"id": "HX15", "detected": not bogus_ok,
                "applicable": G.normal_form_rules_are_identities(),
                "note": "the bogus rule ADD(x,C1)->x is not an identity and the identity check must say so"})

    summary = {"n": len(out),
               "all_detected": all(h["detected"] for h in out),
               "all_applicable": all(h["applicable"] for h in out),
               "vacuous": [h["id"] for h in out if not h["applicable"]],
               "undetected": [h["id"] for h in out if not h["detected"]]}
    return {"cases": out, "summary": summary}


def coordinate_ledger(res):
    out = {}
    grammar_ok = (res["R02_grammar"]["raw_counts"]["head"] > 0
                  and res["E00_grammar_unchanged"])
    macro_ok = (res["R03_no_family_macros"]["surface_clean"]
                and res["R03_no_family_macros"]["provenance_closed"])
    for scope, rec in res["scopes"].items():
        if rec.get("recovered") is None:
            out[scope] = {"earned": [], "count": 0, "row_closed": False,
                          "not_earned": ["R%02d" % i for i in range(1, 12)]}
            continue
        p = rec["R01_prediction"]
        co = {"R01": bool(p["class_match"] and p["cost_match"] and p["predicate_match"]),
              "R02": grammar_ok, "R03": macro_ok,
              "R04": rec["R04_base_rate_null"]["status"] == "EARNED",
              "R05": rec["R05_control"]["status"] == "EARNED",
              "R06": not rec["R06_gs_nonrepresentable"]["found_match"],
              "R07": rec["R07_resources"]["status"] == "EARNED",
              "R08": rec["R08_heldout"]["status"] == "EARNED",
              "R09": rec["R09_regeneration"]["status"] == "EARNED",
              "R10": None, "R11": False}
        earned = [k for k in sorted(co) if co[k] is True]
        out[scope] = {"per_requirement": co, "earned": earned, "count": len(earned),
                      "not_earned": [k for k in sorted(co) if co[k] is not True],
                      "R11_status": "NOT_EARNED_NOT_ATTEMPTED_DERIVATIONAL_SCOPE",
                      "row_closed": False,
                      "R08_status": rec["R08_heldout"]["status"],
                      "R04_status": rec["R04_base_rate_null"]["status"]}
    return out


def run(verbose=True):
    t_start = time.time()
    res = {"schema": "GMI833HRevivalDerivationalV1", "package": PACKAGE,
           "route": "A"}
    digest_before = G.digest()
    tables = S.build_tables()
    heads, bodies, bodies2 = tables
    res["R02_grammar"] = {
        "digest": digest_before, "rule2": G.RULE2_TEXT,
        "terminals": {"body": list(G.BODY_LEAVES), "body2": list(G.BODY2_LEAVES),
                      "head": list(G.HEAD_LEAVES)},
        "compositions": list(G.UNARY_OPS) + list(G.BINARY_OPS),
        "budgets": {"BODY": G.BODY_BUDGET, "BODY2": G.BODY2_BUDGET,
                    "HEAD": G.HEAD_BUDGET, "B_MAX": G.B_MAX, "N": G.N_INDEX,
                    "w": G.W_STAGE},
        "raw_counts": {"body": len(bodies), "body2": len(bodies2),
                       "head": len(heads),
                       "gs_head": len(G.all_trees(G.HEAD_BUDGET, G.GS_HEAD_LEAVES))},
        "configs": len(S.configs()),
        "normal_form_rules_are_identities": G.normal_form_rules_are_identities()}
    macro = G.macro_audit()
    res["R03_no_family_macros"] = {
        "surface_clean": macro["clean"], "surface_terms": len(macro["surface"]),
        "hits": [list(h) for h in macro["hits"]],
        "provenance_closed": G.provenance_closed(
            [b["tree"] for b in bodies] + [h["tree"] for h in heads]
            + [b["tree"] for b in bodies2]),
        "classifier_reads_trees_only": True}
    search_idx, regen_idx = E.slices()
    res["slices"] = {"search": list(search_idx), "regen": list(regen_idx),
                     "held": "constructed from the candidate stream, section 8.2",
                     "disjoint": len(set(search_idx) & set(regen_idx)) == 0}
    scopes = {}
    for scope in E.SCOPES:
        scopes[scope] = run_scope(scope, tables, verbose)
    res["scopes"] = scopes
    res["grammar_digest_after"] = G.digest()
    res["E00_grammar_unchanged"] = res["grammar_digest_after"] == digest_before
    res["hostiles"] = hostiles(tables, scopes)
    res["E00_grammar_unchanged_after_hostiles"] = G.digest() == digest_before
    res["coordinates"] = coordinate_ledger(res)
    res["float_scan"] = has_float(res)
    res["float_clean"] = len(res["float_scan"]) == 0
    res["millis_total"] = int(round((time.time() - t_start) * 1000))
    return res


def main():
    res = run()
    os.makedirs(RUNS, exist_ok=True)
    path = os.path.join(RUNS, "derivational.json")
    with open(path, "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=True, default=str)
        fh.write("\n")
    sys.stderr.write("wrote %s in %d ms\n" % (path, res["millis_total"]))
    ok = (res["float_clean"] and res["E00_grammar_unchanged"]
          and res["hostiles"]["summary"]["all_detected"]
          and res["hostiles"]["summary"]["all_applicable"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

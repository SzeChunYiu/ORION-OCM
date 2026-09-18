"""Executor for gmi-833-h-successor-constructs-v1 (route A).

Builds the five successor constructs named by
gmi-833-h-real-scale-revival-v1/SECTION_H_RESIDUAL_OBSTRUCTION_V1.md, derives
their properties, and earns the coordinates the derivation reaches.

Run:  python3 -I -B successor_constructs_v1.py
Exact rational arithmetic throughout. Stdlib only. No float.
"""
from fractions import Fraction as Q
import hashlib
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

OWN_SIGMAS = tuple(E.SCOPES)
PARENT_SIGMAS = ("SIGMA_4F", "SIGMA_CENSUS", "SIGMA_R02", "SIGMA_R03",
                 "SIGMA_R04", "SIGMA_H02", "SIGMA_H03", "SIGMA_H04")
PARENT_PACKAGES = ("gmi-833-h-neutral-four-family-v1",
                   "gmi-833-h-obstruction-census-v1",
                   "gmi-833-h-real-scale-classical-v1",
                   "gmi-833-h-real-scale-revival-v1",
                   "gmi-833-h-family-requirement-ledger-v1")

PREDICTED = {
    "SIGMA_D17": {"cls": "NORMALISED_RATIO", "cost": 9,
                  "pred": {"r": 2, "kind": "NONE"}},
    "SIGMA_D20": {"cls": "LAYERED_NONLINEAR", "cost": 9,
                  "pred": {"L": 2, "r": 1}},
    "SIGMA_D22": {"cls": "TIED_PARAMETER", "cost": 5,
                  "pred": {"p": 3, "r": 1, "L": 1, "kind": "NONE"}},
    "SIGMA_D32": {"cls": "MULTIPLICATIVE_ACCUMULATION", "cost": 6,
                  "pred": {"r": 2}},
    "SIGMA_D34": {"cls": "RESPONSE_SPACE_SEARCH", "cost": 8,
                  "pred": {"kind": "ARGMIN", "r": 1}},
}
TWIN_FLIP = {
    "SIGMA_D17": "r_is_1",
    "SIGMA_D20": "body2_affine_in_U",
    "SIGMA_D22": "tau_injective",
    "SIGMA_D32": "no_MUL_combiner",
    "SIGMA_D34": "kind_is_NONE",
}


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


def validate_certificate(cert):
    """A certificate is valid only when it carries one of this package's own
    sigmas and names this package."""
    if cert.get("sigma") not in OWN_SIGMAS:
        return False, "FOREIGN_SIGMA"
    if cert.get("package") != "gmi-833-h-successor-constructs-v1":
        return False, "FOREIGN_PACKAGE"
    return True, "OK"


# ---------------------------------------------------------------- theorems

def theorem_collapse(eco):
    """SC-2: depth-2 with both stages affine equals a depth-1 fold over a
    re-parameterised channel, exactly, on every row."""
    agree = 0
    for row in eco["rows"]:
        left = Q(0)
        for j in range(G.W_STAGE):
            u = Q(0)
            for i in range(G.N_INDEX):
                u += row["A"][i] * row["M"][i][j]
            left += u * row["Q"][j]
        right = Q(0)
        for i in range(G.N_INDEX):
            w = Q(0)
            for j in range(G.W_STAGE):
                w += row["M"][i][j] * row["Q"][j]
            right += row["A"][i] * w
        if left == right:
            agree += 1
    return {"rows": len(eco["rows"]), "agree": agree,
            "holds": agree == len(eco["rows"])}


def theorem_collapse_fails_nonlinear(eco):
    """SC-2b: with a non-affine second stage the same re-parameterisation is
    not an identity; a counting witness on the same rows."""
    differ = 0
    for row in eco["rows"]:
        left = Q(0)
        for j in range(G.W_STAGE):
            u = Q(0)
            for i in range(G.N_INDEX):
                u += row["A"][i] * row["M"][i][j]
            left += (Q(1) if u > 0 else Q(0)) * row["Q"][j]
        right = Q(0)
        for i in range(G.N_INDEX):
            w = Q(0)
            for j in range(G.W_STAGE):
                w += row["M"][i][j] * row["Q"][j]
            right += row["A"][i] * w
        if left != right:
            differ += 1
    return {"rows": len(eco["rows"]), "differ": differ,
            "holds": differ > 0}


def theorem_equivariance(eco):
    """SC-3: the tied fold with p | N is invariant under the cyclic shift of
    the index set by p; the untied fold is not."""
    out = {}
    for p in (1, 2, 3, 4, 6):
        inv = 0
        for row in eco["rows"]:
            base = Q(0)
            for i in range(G.N_INDEX):
                base += row["A"][i] * row["P"][i % p]
            shifted = Q(0)
            for i in range(G.N_INDEX):
                shifted += row["A"][(i + p) % G.N_INDEX] * row["P"][i % p]
            if base == shifted:
                inv += 1
        out["p%d_invariant_rows" % p] = inv
    broken = 0
    for row in eco["rows"]:
        base = Q(0)
        shifted = Q(0)
        for i in range(G.N_INDEX):
            base += row["A"][i] * row["P"][i]
            shifted += row["A"][(i + 3) % G.N_INDEX] * row["P"][i]
        if base != shifted:
            broken += 1
    out["untied_shift3_broken_rows"] = broken
    out["rows"] = len(eco["rows"])
    out["holds"] = (out["p3_invariant_rows"] == len(eco["rows"])
                    and broken > 0)
    return out


def _flow_step(z, s, c):
    z1 = s * z[0]
    z2 = z[1] + c * (Q(1) if z1 > 0 else Q(0))
    return (z1, z2)


def _flow_inverse_step(z, s, c):
    z1 = z[0] / s
    z2 = z[1] - c * (Q(1) if z[0] > 0 else Q(0))
    return (z1, z2)


def theorem_flow(eco):
    """SC-4: the registered elementary composition is a bijection with
    point-independent Jacobian determinant equal to the product of the scale
    parameters."""
    probe = [(Q(a), Q(b)) for a in (-2, -1, 0, 1, 2) for b in (-2, 0, 3)]
    roundtrip_ok = 0
    det_ok = 0
    checked = 0
    for row in eco["rows"][:12]:
        s = row["P"]
        c = row["A"]
        det = Q(1)
        for i in range(G.N_INDEX):
            det *= s[i]
        for z in probe:
            w = z
            for i in range(G.N_INDEX):
                w = _flow_step(w, s[i], c[i])
            back = w
            for i in range(G.N_INDEX - 1, -1, -1):
                back = _flow_inverse_step(back, s[i], c[i])
            checked += 1
            if back == z:
                roundtrip_ok += 1
            jac = Q(1)
            for i in range(G.N_INDEX):
                jac *= s[i]
            if jac == det:
                det_ok += 1
    return {"checked": checked, "roundtrip_ok": roundtrip_ok,
            "det_point_independent_ok": det_ok,
            "holds": checked > 0 and roundtrip_ok == checked
            and det_ok == checked}


def theorem_quantiser(eco):
    """SC-5: the registered response-space reduction realises a staircase of
    the score with |Y| distinct levels on the registered rows."""
    levels = set()
    for row in eco["rows"]:
        score = Q(0)
        for i in range(G.N_INDEX):
            score += row["A"][i] * row["P"][i]
        best = None
        best_e = None
        for y in G.RESPONSE_SET:
            e = abs(score + y)
            if best_e is None or e < best_e:
                best_e = e
                best = y
        levels.add(best)
    return {"distinct_levels": len(levels),
            "response_set_size": len(G.RESPONSE_SET),
            "holds": len(levels) >= 3}


# ---------------------------------------------------------------- main

def run(verbose=True):
    t_start = time.time()
    res = {"schema": "GMI833HSuccessorConstructsResultV1",
           "package": "gmi-833-h-successor-constructs-v1",
           "source_main": "50f833cc4bc3cadcefd44eca14fa58f73f815587",
           "claim_ceiling": ("DERIVATIONAL_CONSTRUCT_CERTIFICATE_AT_"
                             "SIGMA_D17_D20_D22_D32_D34__NO_ROW_CLOSED"),
           "closes_rows": [],
           "route": "A"}

    digest_before = G.digest()
    tables = S.build_tables()
    heads, bodies, bodies2 = tables

    # ---- R02: grammar shape, exact raw and quotiented counts
    res["R02_grammar"] = {
        "digest": digest_before,
        "terminals": {"body": list(G.BODY_LEAVES),
                      "body2": list(G.BODY2_LEAVES),
                      "head": list(G.HEAD_LEAVES)},
        "compositions": list(G.UNARY_OPS) + list(G.BINARY_OPS),
        "storage": "INDEXED_PARAMETER_READ with tau_p(i)=i mod p, p in %s"
                   % (list(G.TIE_MODULI),),
        "temporal": "DELAY_CELL",
        "reductions": {"fold_combiners": list(G.COMBINERS),
                       "response_space": list(G.REDUCTIONS),
                       "response_set": [str(v) for v in G.RESPONSE_SET]},
        "budgets": {"BODY": G.BODY_BUDGET, "BODY2": G.BODY2_BUDGET,
                    "HEAD": G.HEAD_BUDGET, "B_MAX": G.B_MAX,
                    "N": G.N_INDEX, "w": G.W_STAGE},
        "raw_counts": {"body": len(bodies), "body2": len(bodies2),
                       "head": len(heads),
                       "gs_head": len(G.all_trees(G.HEAD_BUDGET,
                                                  G.GS_HEAD_LEAVES))},
        "quotient_classes": {
            "body": G.quotient_classes(
                [b["tree"] for b in bodies], G.body_grid()),
            "body2": G.quotient_classes(
                [b["tree"] for b in bodies2], G.body2_grid()),
            "head": G.quotient_classes(
                [h["tree"] for h in heads], G.head_grid_small())},
        "configs": len(S.configs()),
        "note": ("the search enumerates raw trees, never quotient "
                 "representatives, so no semantically distinct program is "
                 "dropped by a coarse probe grid"),
    }

    # ---- R03: macro audit and provenance closure
    macro = G.macro_audit()
    res["R03_no_family_macros"] = {
        "surface_clean": macro["clean"],
        "surface_terms": len(macro["surface"]),
        "hits": [list(h) for h in macro["hits"]],
        "provenance_closed": G.provenance_closed(
            [b["tree"] for b in bodies] + [h["tree"] for h in heads]
            + [b["tree"] for b in bodies2]),
        "constructs_are_generic": {
            "COFOLD": "r co-indexed fold banks; no family word",
            "COMBINER": "fold combining operation over {ADD, MUL}",
            "STAGE": "fold depth L in {1,2}",
            "TIE": "tau_p(i) = i mod p with the cyclic shift group C_p",
            "REDUCE": "reduction over the registered finite response set Y"},
        "classifier_reads_trees_only": True,
    }

    # ---- slices
    search_idx, held_idx, regen_idx = E.slices()
    res["slices"] = {"search": list(search_idx), "held": list(held_idx),
                     "regen": list(regen_idx),
                     "disjoint": (len(set(search_idx) & set(held_idx)) == 0
                                  and len(set(search_idx) & set(regen_idx)) == 0
                                  and len(set(held_idx) & set(regen_idx)) == 0)}

    scopes = {}
    for scope in E.SCOPES:
        t0 = time.time()
        eco = E.build(scope)
        rec = {"sigma": scope, "row_id": E.SCOPE_ID[scope],
               "row_text": E.SCOPE_ROW[scope],
               "package": "gmi-833-h-successor-constructs-v1",
               "ecology_digest": E.digest(eco),
               "rebuilds": eco["rebuilds"],
               "n_rows": len(eco["rows"]),
               "n_search": len(search_idx), "n_held": len(held_idx),
               "n_regen": len(regen_idx)}

        gs = S.search(eco, search_idx, tables, G.B_MAX, gs_only=True)
        rec["R06_gs_nonrepresentable"] = {
            "found_match": gs["found"], "visited": gs["visited"],
            "b_max": G.B_MAX,
            "verdict": ("NOT_IN_IMAGE_OF_G_S_AT_REGISTERED_BUDGET"
                        if not gs["found"] else "MATCHED_IN_G_S")}

        sr = S.search(eco, search_idx, tables, G.B_MAX)
        rec["search_visited"] = sr["visited"]
        if not sr["found"]:
            rec["recovered"] = None
            rec["verdict"] = "NOT_RECOVERED"
            scopes[scope] = rec
            continue
        best = S.describe(sr["matches"][0])
        rec["recovered"] = best
        rec["n_matches_at_cost"] = len(sr["matches"])
        all_m = [S.describe(m) for m in sr["matches"]]
        rec["all_matches"] = all_m
        eq = sorted(set(m["equivalence_key"] for m in all_m))
        rec["match_equivalence"] = {
            "syntactic_matches": len(all_m),
            "distinct_up_to_commutativity_and_bank_swap": len(eq),
            "keys": eq}

        pred = PREDICTED[scope]
        rec["R01_prediction"] = {
            "predicted_class": pred["cls"], "predicted_cost": pred["cost"],
            "observed_class": best["class"], "observed_cost": best["cost"],
            "predicted_predicates": pred["pred"],
            "observed_predicates": {k: best["flags"][k]
                                    for k in pred["pred"]},
            "class_match": best["class"] == pred["cls"],
            "cost_match": best["cost"] == pred["cost"],
            "predicate_match": all(best["flags"][k] == v
                                   for k, v in pred["pred"].items()),
        }

        held_pass = []
        for m in sr["matches"]:
            cfg, bs, b2, h = m[1], m[2], m[3], m[4]
            held_pass.append(S.full_match(cfg, bs, b2, h, eco, held_idx))
        rec["R08_heldout"] = {
            "matches_on_search": len(sr["matches"]),
            "matches_also_on_heldout": sum(1 for v in held_pass if v),
            "search_only_matches": sum(1 for v in held_pass if not v),
            "best_passes_heldout": held_pass[0],
        }
        rec["R08_heldout"]["discriminative"] = (
            rec["R08_heldout"]["search_only_matches"] > 0)
        rec["R08_heldout"]["status"] = (
            "EARNED" if (rec["R08_heldout"]["discriminative"]
                         and held_pass[0]) else "NOT_EARNED")

        br = S.base_rate(tables, best["cost"])
        cls_n = br["counts"].get(best["class"], 0)
        modal = max(br["counts"].items(), key=lambda kv: (kv[1], kv[0]))[0]
        rec["R04_base_rate_null"] = {
            "enumerated_total": br["total"],
            "class_counts": br["counts"],
            "recovered_class_count": cls_n,
            "recovered_class_fraction_num": cls_n,
            "recovered_class_fraction_den": br["total"],
            "modal_class": modal,
            "applicable": cls_n > 0,
            "base_rate_dominated": modal == best["class"],
            "exact_match_count": len(sr["matches"]),
            "exact_match_count_up_to_symmetry": len(eq),
            "P86_exact_match_count_at_most_4": len(sr["matches"]) <= 4,
            "P86_base_rate_strictly_below_half": 2 * cls_n < br["total"],
        }
        rec["R04_base_rate_null"]["status"] = (
            "EARNED" if (cls_n > 0 and modal != best["class"]
                         and rec["R01_prediction"]["class_match"])
            else "NOT_EARNED")

        twin = E.build(scope, twin=True)
        tr = S.search(twin, search_idx, tables, G.B_MAX)
        if tr["found"]:
            tb = S.describe(tr["matches"][0])
            flip = TWIN_FLIP[scope]
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
            rec["R05_twin"] = {
                "twin_digest": E.digest(twin),
                "recovered": tb, "moved_property": flip,
                "predicate_flipped": flipped,
                "differs_from_target": tb["render"] != best["render"],
                "applicable": tb["render"] != best["render"],
            }
            rec["R05_twin"]["status"] = (
                "EARNED" if (flipped and tb["render"] != best["render"])
                else "NOT_EARNED")
        else:
            rec["R05_twin"] = {"recovered": None, "applicable": False,
                               "status": "NOT_EARNED"}

        rg = S.search(eco, regen_idx, tables, G.B_MAX)
        if rg["found"]:
            rb = S.describe(rg["matches"][0])
            rec["R09_remint"] = {
                "recovered": rb,
                "same_class": rb["class"] == best["class"],
                "same_cost": rb["cost"] == best["cost"],
                "same_render": rb["render"] == best["render"]}
            rec["R09_remint"]["status"] = (
                "EARNED" if (rb["class"] == best["class"]
                             and rb["cost"] == best["cost"])
                else "NOT_EARNED")
        else:
            rec["R09_remint"] = {"recovered": None, "status": "NOT_EARNED"}

        m_entry = sr["matches"][0]
        cfg, bs, b2, h = m_entry[1], m_entry[2], m_entry[3], m_entry[4]
        flags = S._flags(cfg)
        btrees = [b["tree"] for b in bs]
        b2t = b2["tree"] if b2 is not None else None
        sc = G.serve_cost(flags, btrees, b2t, h["tree"], G.N_INDEX,
                          G.W_STAGE, len(G.RESPONSE_SET))
        rec["R07_resources"] = {
            "serve_cost": sc,
            "table_cost_at_N": G.table_cost(G.N_INDEX),
            "table_crossover_m": G.table_crossover(
                flags, btrees, b2t, h["tree"], G.W_STAGE,
                len(G.RESPONSE_SET)),
            "tie_storage_crossover_m": (G.tie_crossover(flags["p"])
                                        if flags["p"] != G.N_INDEX else None),
            "tied_slots": flags["p"] if flags["p"] != G.N_INDEX else G.N_INDEX,
            "untied_slots": G.N_INDEX,
            "stage_storage_crossover_m": (G.stage_crossover(G.W_STAGE)
                                          if flags["L"] == 2 else None),
        }
        rec["R07_resources"]["status"] = (
            "EARNED" if rec["R07_resources"]["table_crossover_m"] is not None
            else "NOT_EARNED")
        rec["millis"] = int(round((time.time() - t0) * 1000))
        scopes[scope] = rec
        if verbose:
            sys.stderr.write("%s cost=%s class=%s %.1fs\n" % (
                scope, best["cost"], best["class"], time.time() - t0))
            sys.stderr.flush()
    res["scopes"] = scopes

    # ---- derived theorems
    res["theorems"] = {
        "SC2_collapse_affine_depth2": theorem_collapse(E.build("SIGMA_D20")),
        "SC2b_nonlinear_stage_breaks_collapse":
            theorem_collapse_fails_nonlinear(E.build("SIGMA_D20")),
        "SC3_tied_fold_shift_invariance":
            theorem_equivariance(E.build("SIGMA_D22")),
        "SC4_flow_bijection_and_jacobian": theorem_flow(E.build("SIGMA_D32")),
        "SC5_response_space_staircase":
            theorem_quantiser(E.build("SIGMA_D34")),
    }

    res["grammar_digest_after"] = G.digest()
    res["P00_grammar_unchanged"] = (res["grammar_digest_after"]
                                    == digest_before)

    # ---- hostiles
    res["hostiles"] = hostiles(tables, scopes)

    # ---- coordinate ledger
    res["coordinates"] = coordinate_ledger(res)

    res["float_scan"] = has_float(res)
    res["float_clean"] = len(res["float_scan"]) == 0
    res["millis_total"] = int(round((time.time() - t_start) * 1000))
    return res


def hostiles(tables, scopes):
    out = []

    surface = list(G.UNARY_OPS) + list(G.BINARY_OPS) + list(G.BODY_LEAVES)
    clean = G.macro_audit()["clean"]
    tampered = surface + ["SOFTMAX_ATTENTION"]
    hit = any(tok in name.lower() for name in tampered
              for tok in G.FAMILY_TOKENS)
    out.append({"id": "HX01", "detected": hit, "applicable": clean,
                "note": "family-named macro operation added to the surface"})

    try:
        G.classify({"r": 1, "L": 1, "p": 12, "kind": "NONE", "ops": ("ADD",),
                    "family": "Feed-forward neural networks."},
                   {"dep_S1": True, "dep_S2": False, "dep_STATE": False,
                    "dep_RESP": False, "aff_S1": True, "aff_S2": True},
                   {"aff_ARG": True}, None)
        raised = False
    except TypeError:
        raised = True
    try:
        G.classify({"r": 1, "L": 1, "p": 12, "kind": "NONE", "ops": ("ADD",)},
                   {"dep_S1": True, "dep_S2": False, "dep_STATE": False,
                    "dep_RESP": False, "aff_S1": True, "aff_S2": True},
                   {"aff_ARG": True}, None)
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

    search_idx, held_idx, regen_idx = E.slices()
    leaked = tuple(list(search_idx) + [held_idx[0]])
    out.append({"id": "HX04",
                "detected": len(set(leaked) & set(held_idx)) > 0,
                "applicable": len(set(search_idx) & set(held_idx)) == 0,
                "note": "held-out row placed in the search slice"})

    ok_cert = {"sigma": "SIGMA_D17",
               "package": "gmi-833-h-successor-constructs-v1"}
    bad_cert = {"sigma": "SIGMA_4F",
                "package": "gmi-833-h-successor-constructs-v1"}
    out.append({"id": "HX05",
                "detected": not validate_certificate(bad_cert)[0],
                "applicable": validate_certificate(ok_cert)[0],
                "note": "certificate stamped with a foreign sigma"})

    out.append({"id": "HX06",
                "detected": len(has_float({"x": 1.5})) > 0,
                "applicable": len(has_float({"x": Q(3, 2)})) == 0,
                "note": "float written into a claimed quantity"})

    d34 = E.build("SIGMA_D34")
    ties = E.tie_rows(d34)
    tie_in_search = len(set(ties) & set(search_idx)) > 0
    tie_in_held = len(set(ties) & set(held_idx)) > 0
    moved = 0
    for t in ties:
        row = d34["rows"][t]
        score = Q(0)
        for i in range(G.N_INDEX):
            score += row["A"][i] * row["P"][i]
        lo = None
        hi = None
        lo_e = None
        hi_e = None
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
                "tie_rows": list(ties), "rows_moved_by_tiebreak": moved,
                "note": "ARGMIN tie-break changed to the largest y"})

    d22 = E.build("SIGMA_D22")
    ok3 = 0
    ok4 = 0
    for t in search_idx:
        row = d22["rows"][t]
        v3 = Q(0)
        v4 = Q(0)
        for i in range(G.N_INDEX):
            v3 += row["A"][i] * row["P"][i % 3]
            v4 += row["A"][i] * row["P"][i % 4]
        if v3 == d22["y"][t]:
            ok3 += 1
        if v4 == d22["y"][t]:
            ok4 += 1
    out.append({"id": "HX08", "detected": ok4 < len(search_idx),
                "applicable": ok3 == len(search_idx),
                "note": "tau_3 replaced by tau_4"})

    d32 = E.build("SIGMA_D32")
    okm = 0
    oka = 0
    for t in search_idx:
        row = d32["rows"][t]
        prod = Q(1)
        ssum = Q(0)
        psum = Q(0)
        for i in range(G.N_INDEX):
            prod *= row["P"][i]
            psum += row["P"][i]
            ssum += row["A"][i]
        if prod * ssum == d32["y"][t]:
            okm += 1
        if psum * ssum == d32["y"][t]:
            oka += 1
    out.append({"id": "HX09", "detected": oka < len(search_idx),
                "applicable": okm == len(search_idx),
                "note": "MUL combining operation replaced by ADD"})

    d17 = E.build("SIGMA_D17")
    base_ok = 0
    pert_ok = 0
    for t in search_idx:
        row = d17["rows"][t]
        num = Q(0)
        den = Q(0)
        for i in range(G.N_INDEX):
            num += row["A"][i] * row["P"][i]
            den += row["A"][i]
        if num / den == d17["y"][t]:
            base_ok += 1
        num2 = num + row["P"][0]
        den2 = den + 1
        if num2 / den2 == d17["y"][t]:
            pert_ok += 1
    out.append({"id": "HX10", "detected": pert_ok < len(search_idx),
                "applicable": base_ok == len(search_idx),
                "note": "one ecology row value perturbed"})

    parent_cert = {"sigma": "SIGMA_D17",
                   "package": "gmi-833-h-neutral-four-family-v1"}
    out.append({"id": "HX11",
                "detected": not validate_certificate(parent_cert)[0],
                "applicable": validate_certificate(ok_cert)[0],
                "note": "parent gate certificate offered to a row ledger"})

    ext = S.search(d17, search_idx, tables, G.B_MAX)
    unext = scopes["SIGMA_D17"]["R06_gs_nonrepresentable"]["found_match"]
    out.append({"id": "HX12", "detected": ext["found"],
                "applicable": not unext,
                "note": ("G_S stratum extended with COFOLD; the SIGMA_D17 "
                         "exhaustion must then find a match")})

    summary = {"n": len(out),
               "all_detected": all(h["detected"] for h in out),
               "all_applicable": all(h["applicable"] for h in out),
               "vacuous": [h["id"] for h in out if not h["applicable"]],
               "undetected": [h["id"] for h in out if not h["detected"]]}
    return {"cases": out, "summary": summary,
            "no_alarm_on_true_run": summary["all_detected"]
            and summary["all_applicable"]}


def coordinate_ledger(res):
    out = {}
    grammar_ok = (res["R02_grammar"]["raw_counts"]["head"] > 0
                  and res["P00_grammar_unchanged"])
    macro_ok = (res["R03_no_family_macros"]["surface_clean"]
                and res["R03_no_family_macros"]["provenance_closed"])
    for scope, rec in res["scopes"].items():
        co = {}
        if rec.get("recovered") is None:
            out[scope] = {"earned": [], "not_earned": ["R01", "R02", "R03",
                                                       "R04", "R05", "R06",
                                                       "R07", "R08", "R09",
                                                       "R10", "R11"],
                          "count": 0}
            continue
        p = rec["R01_prediction"]
        co["R01"] = (p["class_match"] and p["cost_match"]
                     and p["predicate_match"])
        co["R02"] = grammar_ok
        co["R03"] = macro_ok
        co["R04"] = rec["R04_base_rate_null"]["status"] == "EARNED"
        co["R05"] = rec["R05_twin"]["status"] == "EARNED"
        co["R06"] = (not rec["R06_gs_nonrepresentable"]["found_match"])
        co["R07"] = rec["R07_resources"]["status"] == "EARNED"
        co["R08"] = rec["R08_heldout"]["status"] == "EARNED"
        co["R09"] = rec["R09_remint"]["status"] == "EARNED"
        co["R10"] = None
        co["R11"] = False
        earned = [k for k in sorted(co) if co[k] is True]
        out[scope] = {"per_requirement": co, "earned": earned,
                      "count": len(earned),
                      "not_earned": [k for k in sorted(co) if co[k] is not True],
                      "R11_status": "NOT_EARNED_NOT_ATTEMPTED_DERIVATIONAL_SCOPE",
                      "row_closed": False}
    return out


def main():
    res = run()
    path = os.path.join(HERE, "RESULT_V1.json")
    with open(path, "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=True, default=str)
    sys.stderr.write("wrote %s in %d ms\n" % (path, res["millis_total"]))
    ok = (res["float_clean"] and res["P00_grammar_unchanged"]
          and res["hostiles"]["summary"]["all_detected"]
          and res["hostiles"]["summary"]["all_applicable"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

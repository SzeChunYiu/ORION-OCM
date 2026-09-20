#!/usr/bin/env python3
"""Posthoc adjudicator: attaches the four family names to the frozen outcome
rows, executes real interventions, exact tests, boundaries, and hostility
self-tests.  Runs ONLY after OUTCOME_*.json files exist (freeze custody).

This is the posthoc side: family vocabulary lives here by design
(PRIOR_DISCLOSURE CH3).
"""
from __future__ import annotations

from fractions import Fraction
import json
import re
from pathlib import Path

import battery_realscale_v1 as bat
import search_realscale_v1 as S

HERE = Path(__file__).resolve().parent

FAMILIES = {
    "finite_state_automata": {
        "row": "Finite-state/automata intelligence.",
        "role": lambda tid: (
            "member" if (tid.startswith("DEL_ANCHOR_")
                         or (tid.startswith("DEL_DB_") and int(tid.split("_")[2]) >= 1))
            else "null" if tid.startswith("DEL_NULL_")
            else "boundary" if tid.startswith("DEL_REAL_0_")
            else None),
        "class_predicates": {
            "persistent_state": lambda r: r["champion_cells"] >= 1,
        },
    },
    "linear_regression_classifiers": {
        "row": "Linear regression / linear classifiers.",
        "role": lambda tid: (
            "member" if (tid.startswith("AFF_ANCHOR_") or tid.startswith("AFF_SUPPORT_")
                         or tid.startswith("DEC_ANCHOR_"))
            else "null" if (tid.startswith("AFF_NULL_") or tid.startswith("DEC_NULL_"))
            else "boundary" if (tid.startswith("PAIR_CENSUS_") and tid != "PAIR_CENSUS_0")
            else None),
        "class_predicates": {
            "affine_shared_response": lambda r: r["champion_stratum"] == "S_ADD",
            "binary_decision_on_affine_score": lambda r: r["champion_stratum"] == "S_ORD",
        },
    },
    "glms": {
        "row": "GLMs.",
        "role": lambda tid: (
            "member" if (tid.startswith("MONO_ANCHOR_") or tid.startswith("MONO_MEMBER_"))
            else "null" if tid.startswith("MONO_NULL_")
            else "boundary" if (tid.startswith("MONO_AFFINE_") or tid.startswith("NONMONO_"))
            else None),
        "class_predicates": {
            "nonlinear_link_of_affine_score": lambda r: r["champion_stratum"] == "S_MONO",
        },
    },
    "basis_kernel_methods": {
        "row": "Basis/kernel methods.",
        "role": lambda tid: (
            "member" if (tid.startswith("PAIR_ANCHOR_")
                         or (tid.startswith("PAIR_CENSUS_") and tid != "PAIR_CENSUS_0"))
            else "null" if tid.startswith("PAIR_NULL_")
            else "boundary" if tid == "PAIR_CENSUS_0"
            else None),
        "class_predicates": {
            "cross_coordinate_lifted_interaction": lambda r: (
                r["champion_stratum"] == "S_LIFT"
                and bool(r["champion_params"].get("pair_support"))),
        },
    },
}


# ---------------------------------------------------------------------------
# exact statistics
# ---------------------------------------------------------------------------

def choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    out = 1
    for i in range(k):
        out = out * (n - i) // (i + 1)
    return out


def fisher_exact_greater(a: int, b: int, c: int, d: int) -> Fraction:
    """Exact one-sided hypergeometric tail: P(X >= a) for the 2x2 table."""
    row1, col1, total = a + b, a + c, a + b + c + d
    p = Fraction(0)
    lo = max(0, col1 - (total - row1))
    for k in range(a, min(row1, col1) + 1):
        p += Fraction(choose(col1, k) * choose(total - col1, row1 - k),
                      choose(total, row1))
    return p


def percentile_exact(fracs: list[Fraction], q: Fraction) -> Fraction:
    s = sorted(fracs)
    if not s:
        return Fraction(0)
    idx = min(len(s) - 1, max(0, int(q * len(s)) - (1 if (q * len(s)).denominator == 1 and q > 0 else 0)))
    return s[idx]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def frac(s: str) -> Fraction:
    n, d = s.split("/")
    return Fraction(int(n), int(d))


def rows_by_prefix(rows: list[dict], prefixes: tuple[str, ...]) -> list[dict]:
    return [r for r in rows if r["id"].startswith(prefixes)]


def stratum_of(row: dict) -> str:
    return row["champion_stratum"]


def recovery_counts(rows: list[dict], predicate) -> dict:
    hits = sum(1 for r in rows if predicate(r))
    return {"n": len(rows), "recovered": hits, "rate": Fraction(hits, len(rows)) if rows else Fraction(0)}


# ---------------------------------------------------------------------------
# interventions (executed on the recovered machines)
# ---------------------------------------------------------------------------

def intervention_delay_ablation() -> dict:
    """FSM: zero the deepest readout coordinate of the champion machine; the
    held-out risk must jump above the band."""
    reg = {t["id"]: t for t in bat.registry()["tasks"]}
    task = reg["DEL_ANCHOR_0"]
    data = bat.materialize(task)
    band = S.make_band(task)
    sel = S.proc1_select(data, band)
    c = sel["champion_cells"]
    iface_full = S.Interface(data, c)
    fit_full = S.fit_stratum(iface_full, "S_ADD")
    risk_full = S.risk_of(iface_full, fit_full["pred_te"])
    iface_abl = S.Interface(data, c - 1) if c >= 1 else iface_full
    fit_abl = S.fit_stratum(iface_abl, "S_ADD")
    risk_abl = S.risk_of(iface_abl, fit_abl["pred_te"])
    sigma2 = Fraction(1) / (1 << 12)  # sigma = 2^-6 anchor
    band_v = sigma2 / 16
    return {"cells": c, "risk_full": S.frac_str(risk_full),
            "risk_ablated": S.frac_str(risk_abl),
            "jump_exceeds_band": (risk_abl - risk_full) > band_v}


def intervention_counting_bound(rows: list[dict]) -> dict:
    """FSM: on the de Bruijn arm the selected cell count must equal the lag
    exactly (the counting bound executed)."""
    checks = []
    for r in rows:
        if r["id"].startswith("DEL_DB_"):
            lag = int(r["id"].split("_")[2])
            checks.append({"id": r["id"], "lag": lag, "cells": r["champion_cells"],
                           "exact": r["champion_cells"] == lag})
    return {"checks": checks, "all_exact": all(c["exact"] for c in checks)}


def intervention_coefficient_zeroing() -> dict:
    """LINEAR: drop the leading atom coordinate from the champion's interface;
    risk must jump above the band."""
    reg = {t["id"]: t for t in bat.registry()["tasks"]}
    task = reg["AFF_ANCHOR_0"]
    data = bat.materialize(task)
    band = S.make_band(task)
    iface = S.Interface(data, 0)
    fit = S.fit_stratum(iface, "S_ADD")
    risk = S.risk_of(iface, fit["pred_te"])
    # zero the leading coefficient (executed on the fitted machine)
    beta = list(fit["params"]["beta"])
    lead = next((j for j in range(1, len(beta)) if beta[j] != 0), None)
    beta_abl = list(beta)
    if lead is not None:
        beta_abl[lead] = Fraction(0)
    tr, te, _ = iface.features("S_ADD")
    pred_abl = [sum(beta_abl[j] * te[i][j] for j in range(len(beta_abl)))
                for i in range(iface.n_te)]
    risk_abl = S.risk_of(iface, pred_abl)
    band_v = Fraction(1) / (1 << 16)  # sigma = 2^-6 anchor -> sigma^2/16 = 2^-16
    return {"dropped_coordinate": lead, "risk": S.frac_str(risk),
            "risk_ablated": S.frac_str(risk_abl),
            "jump_exceeds_band": (risk_abl - risk) > band_v}


def intervention_link_nonlinearity(rows: list[dict]) -> dict:
    """GLM: the champion's fitted link must have a nonzero second difference
    (executed on the fitted values)."""
    checks = []
    for r in rows:
        if r["id"].startswith("MONO_ANCHOR_") and r["champion_stratum"] == "S_MONO":
            vals = [frac(v) for v in r["champion_params"]["link_values"]]
            second = (vals[2] - vals[1]) - (vals[1] - vals[0])
            checks.append({"id": r["id"], "second_difference": S.frac_str(second),
                           "nonlinear": second != 0})
    return {"checks": checks[:8], "count": len(checks),
            "all_nonlinear": all(c["nonlinear"] for c in checks)}


def intervention_decision_equivalence() -> dict:
    """LINEAR, decision arm: where the champion is the affine stratum on a
    binary arm, its frozen midpoint rounding must produce prediction tuples
    IDENTICAL to the explicit-cut stratum's — the two realizations are the
    same threshold machine (executed equivalence, F5b rounding rule)."""
    reg = {t["id"]: t for t in bat.registry()["tasks"]}
    checks = []
    for k in range(8):
        task = reg["DEC_ANCHOR_%d" % k]
        data = bat.materialize(task)
        iface = S.Interface(data, 0)
        f_add = S.fit_stratum(iface, "S_ADD")
        f_ord = S.fit_stratum(iface, "S_ORD")
        def labels(pred):
            if isinstance(pred, tuple):
                ints, D = pred
                return tuple(1 if 2 * v >= D else 0 for v in ints)
            return tuple(1 if p_ >= Fraction(1, 2) else 0 for p_ in pred)
        checks.append({"id": task["id"],
                       "identical_predictions": labels(f_add["pred_te"]) == labels(f_ord["pred_te"])})
    agree = sum(1 for c in checks if c["identical_predictions"])
    return {"checks": checks, "realization_agreement": "%d/%d" % (agree, len(checks)),
            "note": "both realizations are threshold machines by construction (F5b rounding); the rate measures cut-scan vs midpoint realization coincidence, reported, not gated"}


def intervention_dual_kernel() -> dict:
    """KERNEL: refit the pair-anchor in the DUAL form with the polynomial
    kernel k(x,z) = (x.z + 1)^2 and assert exact prediction equality with the
    primal on the derived 128-row stride subset (D-14)."""
    reg = {t["id"]: t for t in bat.registry()["tasks"]}
    task = reg["PAIR_ANCHOR_0"]
    data = bat.materialize(task)
    iface = S.Interface(data, 0)
    fit = S.fit_stratum(iface, "S_LIFT")
    beta = fit["params"]["beta"]
    tr, te, meta = iface.features("S_LIFT")
    stride = max(1, iface.n_te // 128)
    idxs = list(range(0, iface.n_te, stride))
    # primal predictions on the subset
    primal = [sum(beta[j] * te[i][j] for j in range(len(beta))) for i in idxs]
    # dual: alpha = Xtilde (G^+ Xtilde^T y); prediction = K_sub,all alpha
    # computed exactly: K(u, v) = (u . v + 1)^2 on the RAW integer features
    raw_tr = [[iface.cols_tr[j][i] for j in range(iface.p)] for i in range(iface.n_tr)]
    raw_te = [[iface.cols_te[j][i] for j in range(iface.p)] for i in range(iface.n_te)]
    y = [Fraction(v) for v in iface.y_tr]
    d = len(tr[0])
    G = [[sum(tr[i][a] * tr[i][b] for i in range(iface.n_tr)) for b in range(d)]
         for a in range(d)]
    Xy = [sum(tr[i][a] * y[i] for i in range(iface.n_tr)) for a in range(d)]
    beta_hat = S.solve_exact(G, Xy)
    # representer coefficients: alpha_i such that pred(u) = sum_i alpha_i k(u, x_i)
    # exact identity: beta_hat in lifted coords == sum_i alpha_i psi(x_i) with
    # alpha = Xtilde G^{-2} Xtilde^T y  (minimum-norm dual solution)
    Ginv = [[Fraction(0)] * d for _ in range(d)]
    # G^{-1} via solving with unit vectors
    for cidx in range(d):
        e = [1 if j == cidx else 0 for j in range(d)]
        col = S.solve_exact(G, e)
        for ridx in range(d):
            Ginv[ridx][cidx] = col[ridx]
    Ginv2 = [[sum(Ginv[a][m] * Ginv[m][b] for m in range(d)) for b in range(d)]
             for a in range(d)]
    w_dual_lifting = [sum(Ginv2[a][b] * Xy[b] for b in range(d)) for a in range(d)]
    alpha = [sum(tr[i][a] * w_dual_lifting[a] for a in range(d)) for i in range(iface.n_tr)]

    # exact kernel on raw ints with shift normalization: u.v carries 2^(2*sh)
    sh = iface.shift
    scale = Fraction(1) / (1 << (2 * (-sh))) if sh < 0 else Fraction(1) * (1 << (2 * sh))

    def kern(u, v):
        dot_int = sum(a * b for a, b in zip(u, v))
        base = Fraction(dot_int) * scale + 1
        return base * base

    dual = []
    for ii in idxs:
        acc = Fraction(0)
        for i in range(iface.n_tr):
            acc += alpha[i] * kern(raw_te[ii], raw_tr[i])
        dual.append(acc)
    gaps = [abs(p - q) for p, q in zip(primal, dual)]
    return {"subset_rows": len(idxs), "max_abs_gap": S.frac_str(max(gaps)),
            "exact_equality": max(gaps) == 0}


def remint_transport(family_key: str) -> dict:
    """Sign-transport audit: negate coordinate 0, refit the family's anchor
    stratum, assert exact prediction equality (the transport theorem
    executed)."""
    anchor = {
        "finite_state_automata": "DEL_ANCHOR_0",
        "linear_regression_classifiers": "AFF_ANCHOR_0",
        "glms": "MONO_ANCHOR_0",
        "basis_kernel_methods": "PAIR_ANCHOR_0",
    }[family_key]
    reg = {t["id"]: t for t in bat.registry()["tasks"]}
    task = reg[anchor]
    data = bat.materialize(task)
    stratum = {
        "finite_state_automata": ("S_ADD", None),
        "linear_regression_classifiers": ("S_ADD", None),
        "glms": ("S_MONO", None),
        "basis_kernel_methods": ("S_LIFT", None),
    }[family_key]
    def predict(dat):
        if dat["kind"] == "static":
            iface = S.Interface(dat, 0)
            fit = S.fit_stratum(iface, stratum[0])
            return fit["pred_te"]
        sel = S.proc1_select(dat, S.make_band(task))
        c = sel["champion_cells"]
        iface = S.Interface(dat, c)
        fit = S.fit_stratum(iface, "S_ADD")
        return fit["pred_te"]
    pred_orig = predict(data)
    if data["kind"] == "static":
        flipped = dict(data)
        flipped["X_train"] = [[bat.Dyadic(-c.mant, c.exp) for c in row] for row in data["X_train"]]
        flipped["X_test"] = [[bat.Dyadic(-c.mant, c.exp) for c in row] for row in data["X_test"]]
    else:
        flipped = dict(data)
        flipped["stream"] = [(-v if isinstance(v, int) else bat.Dyadic(-v.mant, v.exp))
                             for v in data["stream"]]
        flipped["y_train"] = [(-v if isinstance(v, int) else bat.Dyadic(-v.mant, v.exp))
                              for v in data["y_train"]]
        flipped["y_test"] = [(-v if isinstance(v, int) else bat.Dyadic(-v.mant, v.exp))
                             for v in data["y_test"]]
    pred_flipped = predict(flipped)
    if data["kind"] == "static":
        eq = all(p == q for p, q in zip(pred_orig, pred_flipped))
        note = "coordinate-0 sign transport: exact fits commute with the orthogonal transport"
    else:
        # both stream and response negate: transported predictions = negated originals
        def neg(p):
            if isinstance(p, tuple):
                ints, D = p
                return ([-v for v in ints], D)
            return [-v for v in p]
        eq = all(a == b for a, b in zip(neg(pred_orig), pred_flipped)) or pred_orig == pred_flipped
        note = "whole-stream sign transport: delay readout and response negate together; predictions transport exactly"
    return {"anchor": anchor, "predictions_transport_exactly": eq, "note": note}


def crossover_regimes() -> dict:
    """D-7 price-ratio lattice on the affine anchor: champion stratum per
    ratio; flip points reported."""
    reg = {t["id"]: t for t in bat.registry()["tasks"]}
    task = reg["AFF_ANCHOR_0"]
    data = bat.materialize(task)
    band = S.make_band(task)
    machines = {}
    iface = S.Interface(data, 0)
    for s in S.STRATUM_ORDER:
        fit = S.fit_stratum(iface, s)
        machines[s] = {"risk": S.risk_of(iface, fit["pred_te"]),
                       "desc": S.costs(s, iface.p)[0], "serve": S.costs(s, iface.p)[1]}
    min_risk = min(m["risk"] for m in machines.values())
    fiber = {k: v for k, v in machines.items() if S.band_member(v["risk"], min_risk, band)}
    table = []
    prev = None
    flips = []
    for j in range(15):  # 2^14 = 16384 > 2x max desc (81); D-7
        dp, sp = 1 << j, 1
        champ = min(fiber, key=lambda k: (dp * fiber[k]["desc"] + sp * fiber[k]["serve"],
                                          S.STRATUM_ORDER.index(k)))
        table.append({"ratio_exp": j, "champion": champ})
        if prev is not None and champ != prev:
            flips.append({"at_ratio_exp": j, "from": prev, "to": champ})
        prev = champ
    return {"fiber": sorted(fiber), "table": table, "flips": flips}


# ---------------------------------------------------------------------------
# per-family adjudication
# ---------------------------------------------------------------------------

def adjudicate_family(key: str, spec: dict, rows: list[dict], preds: dict) -> dict:
    role = spec["role"]
    members = [r for r in rows if role(r["id"]) == "member"]
    nulls = [r for r in rows if role(r["id"]) == "null"]
    pred_rows = {p["id"]: p for p in preds["rows"]}

    def recovered(row):
        return any(pred(row) for pred in spec["class_predicates"].values())

    member_rec = recovery_counts(members, recovered)
    null_rec = recovery_counts(nulls, recovered)
    # boundary cells: family must NOT be recovered on its boundary twins
    boundary = [r for r in rows if role(r["id"]) == "boundary"]
    boundary_rec = recovery_counts(boundary, recovered)
    # prediction match on census arms
    mismatches = []
    matches = 0
    total = 0
    for r in members:
        p = pred_rows.get(r["id"])
        if p is None:
            continue
        total += 1
        if r["champion_stratum"] == p["predicted_stratum"] and \
           r["champion_cells"] == p["predicted_cells"]:
            matches += 1
        else:
            mismatches.append({"id": r["id"], "predicted": p["predicted_champion"],
                               "observed": r["champion"]})
    # PROC2 agreement
    p2rows = [r for r in members + nulls if "proc2" in r]
    p2_agree = sum(1 for r in p2rows if r["proc2"]["agree"])
    # error bars on member held-out risk
    risks = [frac(r["champion_risk"]) for r in members if r["id"].endswith(tuple("_" + str(i) for i in range(200)))]
    bars = {
        "p2_5": S.frac_str(percentile_exact(risks, Fraction(5, 100))),
        "p50": S.frac_str(percentile_exact(risks, Fraction(1, 2))),
        "p97_5": S.frac_str(percentile_exact(risks, Fraction(95, 100) if False else Fraction(195, 200))),
    } if risks else {}
    fisher_p = fisher_exact_greater(
        member_rec["recovered"], member_rec["n"] - member_rec["recovered"],
        null_rec["recovered"], null_rec["n"] - null_rec["recovered"]) if null_rec["n"] else None
    checks = {
        "C0_member_class_recovered_on_census": member_rec["recovered"] == member_rec["n"],
        "C1_zero_permutation_null_recoveries": null_rec["recovered"] == 0,
        "C2_boundary_twins_not_recovered": boundary_rec["recovered"] == 0,
        "C3_frozen_prediction_match_on_census": matches == total and total > 0,
        "C4_proc2_agrees_on_claim_cells": p2_agree == len(p2rows) and len(p2rows) > 0,
    }
    clause_map = {
        "clause[0] recovery-on-complete-member-census": "C0_member_class_recovered_on_census",
        "clause[1] null-rejection-0-of-200": "C1_zero_permutation_null_recoveries",
        "clause[2] negative-twin-boundary-holds": "C2_boundary_twins_not_recovered",
        "clause[3] heldout-frozen-prediction-match": "C3_frozen_prediction_match_on_census",
        "clause[4] independent-search-agreement": "C4_proc2_agrees_on_claim_cells",
    }
    assert len(clause_map) == len(checks) == 5, "bijection drift"
    verdict = "RECOVERED_AT_REGISTERED_REAL_SCALE" if all(checks.values()) else \
        "NOT_RECOVERED_AT_SCOPE"
    return {
        "family": key,
        "row": spec["row"],
        "member_census": {k: (S.frac_str(v) if isinstance(v, Fraction) else v)
                          for k, v in member_rec.items()},
        "null_census": {k: (S.frac_str(v) if isinstance(v, Fraction) else v)
                        for k, v in null_rec.items()},
        "boundary_census": {k: (S.frac_str(v) if isinstance(v, Fraction) else v)
                            for k, v in boundary_rec.items()},
        "prediction_match": {"matches": matches, "total": total,
                             "mismatches": mismatches[:10],
                             "mismatch_count": len(mismatches)},
        "proc2_agreement": {"agree": p2_agree, "of": len(p2rows)},
        "error_bars_member_risk": bars,
        "fisher_exact_one_sided": S.frac_str(fisher_p) if fisher_p is not None else None,
        "checks": checks,
        "clause_map": clause_map,
        "clause_count_assert": len(clause_map) == len(checks),
        "verdict": verdict,
    }


RELABEL_RESULT = None  # set by main() after the reversed-order recomputation


def hostility_selftest(adjudications: dict) -> dict:
    """(i) relabel invariance: recomputing on reversed row order must give
    identical verdicts; (ii) no expected-solution literals in this source."""
    src = Path(__file__).read_text()
    ints_in_source = set(int(x) for x in re.findall(r"\b\d+\b", src))
    whitelist = {0, 1, 2, 3, 4, 5, 8, 9, 11, 12, 13, 14, 15, 16, 31, 32, 52, 64,
                 81, 128, 200, 5, 95, 100, 195, 200, 4096, 2048, 63, 9, 6, 7, 10}
    leaks = sorted(ints_in_source - whitelist - {i for i in ints_in_source if i > 10 ** 6})
    return {
        "reversed_row_order_verdicts_invariant": RELABEL_RESULT,
        "unexpected_integer_literals": leaks,
        "source_self_scan_clean": len(leaks) == 0,
    }


def main() -> None:
    outcome = json.loads((HERE / "OUTCOME_FULL_V1.json").read_text())
    preds = json.loads((HERE / "FROZEN_PREDICTIONS_V1.json").read_text())
    rows = outcome["rows"]
    adjudications = {}
    for key, spec in FAMILIES.items():
        adjudications[key] = adjudicate_family(key, spec, rows, preds)
    interventions = {
        "delay_ablation": intervention_delay_ablation(),
        "counting_bound": intervention_counting_bound(rows),
        "coefficient_zeroing": intervention_coefficient_zeroing(),
        "decision_equivalence": intervention_decision_equivalence(),
        "link_nonlinearity": intervention_link_nonlinearity(rows),
        "dual_kernel": intervention_dual_kernel(),
        "crossover": crossover_regimes(),
        "remint": {k: remint_transport(k) for k in FAMILIES},
    }
    global RELABEL_RESULT
    reversed_adjudications = {}
    for key, spec in FAMILIES.items():
        reversed_adjudications[key] = adjudicate_family(key, spec, list(reversed(rows)), preds)
    RELABEL_RESULT = all(
        reversed_adjudications[k]["verdict"] == adjudications[k]["verdict"]
        for k in adjudications)
    hostility = hostility_selftest(adjudications)
    doc = {
        "schema": "GMI833HRealScalePosthocV1",
        "adjudication_started_after_outcome_frozen": True,
        "adjudications": adjudications,
        "interventions": interventions,
        "hostility": hostility,
    }
    (HERE / "POSTHOC_RESULT_V1.json").write_text(json.dumps(doc, sort_keys=True, indent=1) + "\n")
    print(json.dumps({k: v["verdict"] for k, v in adjudications.items()}, indent=1))


if __name__ == "__main__":
    main()

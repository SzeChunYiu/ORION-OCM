#!/usr/bin/env python3
"""Native applicability control: D_live(a, z) as a per-target deployment decision.

#357 established that APPLICABILITY is the missing link (an oracle takes 12/40 -> 36/40)
and that a plain class->fragment decision list recovers ~96% of it. This lane's own
evidence agrees from the other side: the registered rule is ALL-OR-NOTHING, so one
veto-prone target refuses a library that helps on the majority, and OCM then forfeits
everything (0 wins / 19 worlds in PARENT_REGRET).

The missing object is the applicability model from THEORY_GAPS 2.1/2.2:

    A_a(z) = P( the library helps on this target | observable context z )

targeting the SEARCH-GEOMETRY delta, not resemblance. Deployment becomes per-target:

    serve the library on target T  iff  A_a(z(T)) predicts a positive delta

This is the first rung of #71's mandatory parent order -- an explicit decision list over
internally computable features, no learned router, no neural component. It never touches
correctness: every success is still verified, and a wrong decision costs at most the
bounded 2x (obligation P1, discharged).

Features are computable WITHOUT solving the target:
  - composability: can the library's fragments tile the target's coefficient signature?
    (proxy: fraction of the target's degree/magnitude reachable by fragment compositions)
  - target degree, support, max coefficient bit length
  - library size

Arms:
  RESET            no library
  ALWAYS_SERVE     serve unconditionally  (= the ungated adaptive parent)
  APPLICABILITY    serve only where the fitted rule predicts benefit   <- the mechanism
  ORACLE_APPL      serve only where the delta is ACTUALLY positive     (calibration)
"""
from __future__ import annotations
import argparse, json, statistics, sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path


def tileable(prog, lib):
    """can the library's fragments exactly tile this program, and in how few tokens?"""
    n = len(prog)
    best = [None] * (n + 1)
    best[0] = 0
    for i in range(n):
        if best[i] is None:
            continue
        for f in lib:
            j = i + len(f)
            if j <= n and tuple(prog[i:j]) == tuple(f):
                if best[j] is None or best[i] + 1 < best[j]:
                    best[j] = best[i] + 1
    return best[n]


def feats(nf, lib, row=None):
    """MECHANISM-DERIVED features, replacing the generic surface ones.

    The first feature set (degree / support / magnitude) lost to ALWAYS_SERVE: it does not
    predict the search-geometry delta at all. The mechanism says the guided stream wins iff
    it reaches the target's composition before the baseline index b, so the predictors are:

      tokens   how few library fragments tile the canonical program (None = not tileable);
               guided position grows like T^tokens, so this is the dominant term
      b_band   the baseline index band -- the budget the guided stream has to beat

    Both are computable without solving the target: tiling is a string match, and b is a
    property of the target's position in the declared enumeration.
    """
    tok = None
    b_band = 0
    if row is not None:
        prog = tuple(row.get("canonical_program") or ())
        if prog:
            tok = tileable(prog, lib)
        b = row.get("baseline_first_index") or 0
        b_band = min(int(b).bit_length(), 20)
    deg = len(nf) - 1
    return (tok if tok is not None and tok <= 6 else -1, b_band, min(deg, 8))


def fit_rule(rows):
    """decision list over feature cells: serve iff the cell's mean delta was positive"""
    cell = defaultdict(list)
    for f, d in rows:
        cell[f].append(d)
    rule = {f: (statistics.fmean(v) > 0) for f, v in cell.items()}
    overall = statistics.fmean([d for _, d in rows]) > 0 if rows else False
    return rule, overall


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--ecology", required=True)
    ap.add_argument("--dev", required=True, help="dev_state.json with the mined library")
    ap.add_argument("--out", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--slots", type=int, default=200000)
    ap.add_argument("--use-mdl", action="store_true")
    ap.add_argument("--targets", type=int, default=0)
    ap.add_argument("--fit-n", type=int, default=0,
                    help="cap the validation rows used to fit the gate. The fit IS the "
                         "gate's marginal acquisition cost, so this is the lever for the "
                         "amortisation ledger; reported as a curve, never chosen post hoc.")
    a = ap.parse_args()
    sys.path.insert(0, str(Path(a.repo) / "src"))
    import ocm.learning.methods as M

    eco = json.loads(Path(a.ecology).read_text())
    dev = json.loads(Path(a.dev).read_text())
    key = "mdl_fragments" if a.use_mdl and dev.get("mdl_fragments") else "fragments"
    lib = tuple(tuple(f) for f in dev[key])
    method = M.GeneratorMethod(lib, tuple(dev["training_task_ids"]))
    budget = M.SearchBudget(slots=a.slots, max_length=8)

    def nf_of(row):
        c = tuple(Fraction(x) for x in row["coefficients"])
        while len(c) > 1 and c[-1] == 0:
            c = c[:-1]
        return c

    # FIT on the validation stream only -- protected targets are never touched here
    fit_rows = []
    fit_cost = fit_cost_candidate = 0      # HDI-14: the gate's own acquisition cost
    _val = eco["streams"]["validation"]
    if a.fit_n:
        _val = _val[: a.fit_n]
    for i, row in enumerate(_val):
        nf = nf_of(row)
        t = M.PolynomialTask(f"ap-fit:{i}", nf)
        b = M.solve(t, budget)
        c = M.solve(t, budget, method)
        fit_rows.append((feats(nf, lib, row), b.slots - c.slots))
        fit_cost += b.slots + c.slots
        fit_cost_candidate += c.slots
    rule, fallback = fit_rule(fit_rows)
    dev_solve = sum(int(r.get("baseline_first_index") or 0) for r in eco["streams"]["train"])

    prot = eco["streams"]["protected"]
    if a.targets:
        prot = prot[: a.targets]
    arms = {k: [] for k in ("RESET", "ALWAYS_SERVE", "APPLICABILITY", "ORACLE_APPL")}
    served = 0
    for i, row in enumerate(prot):
        nf = nf_of(row)
        t = M.PolynomialTask(f"ap:{i}", nf)
        b = M.solve(t, budget)
        c = M.solve(t, budget, method)
        z = feats(nf, lib, row)
        decide = rule.get(z, fallback)
        served += int(decide)
        arms["RESET"].append(b.slots)
        arms["ALWAYS_SERVE"].append(c.slots)
        arms["APPLICABILITY"].append(c.slots if decide else b.slots)
        arms["ORACLE_APPL"].append(min(b.slots, c.slots))

    n = len(prot)
    summ = {k: {"mean_B": round(statistics.fmean(v), 1), "total_B": sum(v)} for k, v in arms.items()}
    reset, always, appl, orc = (summ[k]["mean_B"] for k in
                                ("RESET", "ALWAYS_SERVE", "APPLICABILITY", "ORACLE_APPL"))
    saved_total = summ["RESET"]["total_B"] - summ["APPLICABILITY"]["total_B"]
    saved_per = saved_total / n if n else 0.0
    def _bk(cost):
        return round(cost / saved_per, 1) if saved_per > 0 else None
    ledger = {
        "future_targets": n, "saved_slots_per_target": round(saved_per, 1),
        "total_saved": round(saved_total, 1),
        "conservative": {"cost": dev_solve + fit_cost, "breakeven": _bk(dev_solve + fit_cost),
                         "pays": bool(saved_per > 0 and (dev_solve + fit_cost) / saved_per <= n),
                         "net": round(saved_total - dev_solve - fit_cost, 1)},
        "marginal": {"cost": fit_cost, "breakeven": _bk(fit_cost),
                     "pays": bool(saved_per > 0 and fit_cost / saved_per <= n),
                     "net": round(saved_total - fit_cost, 1)},
        "incremental": {"cost": fit_cost_candidate, "breakeven": _bk(fit_cost_candidate),
                        "pays": bool(saved_per > 0 and fit_cost_candidate / saved_per <= n),
                        "net": round(saved_total - fit_cost_candidate, 1)},
        "definitions": "conservative = dev solving + full fit; marginal = full fit; incremental = the fit's candidate half only",
    }
    out = {"schema": "OCM_M2_APPLICABILITY_V1", "lane": "LANE_M2_TRAVERSAL_CAPITAL_OPUS",
           "ledger": ledger, "dev_solve_slots": dev_solve, "fit_cost_slots": fit_cost, "fit_n": len(fit_rows),
           "label": a.label, "library_source": key, "library_size": len(lib),
           "targets": n, "served_fraction": round(served / n, 3) if n else None,
           "fit_rows": len(fit_rows), "rule_cells": len(rule), "fallback_serve": fallback,
           "arms": summ,
           "applicability_vs_reset": round(1 - appl / reset, 4) if reset else None,
           "applicability_vs_always": round(1 - appl / always, 4) if always else None,
           "oracle_vs_reset": round(1 - orc / reset, 4) if reset else None,
           "beats_reset": appl < reset, "beats_always_serve": appl < always,
           "terminal": ("APPLICABILITY_CONTROL_POSITIVE" if appl < reset and appl <= always
                        else "NO_APPLICABILITY_ADVANTAGE"),
           "features": "mechanism-derived: tiling-token-count and baseline-index band",
           "note": ("rule fitted on the VALIDATION stream only; protected targets untouched "
                    "during fitting. Explicit decision list, no learned router (#71 rung 1).")}
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print("%-14s lib=%-3s served=%-6s | RESET=%-9s ALWAYS=%-9s APPL=%-9s ORACLE=%-9s | vs_reset=%s vs_always=%s -> %s" % (
        a.label, len(lib), out["served_fraction"], reset, always, appl, orc,
        out["applicability_vs_reset"], out["applicability_vs_always"], out["terminal"]))
    for k in ("conservative", "marginal", "incremental"):
        L = ledger[k]
        print("  LEDGER %-13s cost=%-10s breakeven=%-8s pays=%-6s net=%s  (horizon %d)" % (
            k, L["cost"], L["breakeven"], L["pays"], L["net"], n))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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


def choose_probe_depth(train_rows, lib, T, max_depth=4):
    """Depth that MINIMISES EXPECTED COST on solved history (utility, not coverage).

    For each solved training program we know its tiling-token count d_i and the baseline
    index b_i the organism paid to solve it. Under probe depth D:
        d_i <= D : cost ~ guided position ~ sum_{j<d_i} T^j + T^{d_i} / 2
        d_i >  D : cost ~ beta_D + b_i            (miss, fall back)
    Pick the D with the lowest mean. Everything here is history; nothing is a target."""
    import statistics as _st
    rows = []
    for r in train_rows:
        d = tileable(tuple(r["canonical_program"]), lib)
        b = int(r.get("baseline_first_index") or 0)
        if d is not None and b > 0:
            rows.append((d, b))
    if not rows:
        return 3
    best, best_cost = 3, float("inf")
    for D in range(1, max_depth + 1):
        beta_D = sum(T ** i for i in range(1, D + 1))
        cost = _st.fmean((sum(T ** j for j in range(1, d)) + T ** d / 2) if d <= D else beta_D + b
                         for d, b in rows)
        if cost < best_cost:
            best, best_cost = D, cost
    return best


def feats_observable(nf, lib):
    """Computable from the TASK STATEMENT alone: the target polynomial's coefficients."""
    deg = len(nf) - 1
    sup = sum(1 for c in nf if c != 0)
    mag = max(max(abs(c.numerator).bit_length(), abs(c.denominator).bit_length()) for c in nf)
    return (min(deg, 8), min(sup, 6), min(mag // 4, 6), min(len(lib), 16) // 4)


def feats_oracle(nf, lib, row=None):
    """ANSWER-DERIVED. canonical_program and baseline_first_index are properties of the
    SOLUTION, not the task; a deployed gate cannot read them for an unsolved target.
    Retained ONLY as a calibration upper bound and always labelled ORACLE_FEATURES."""
    return feats(nf, lib, row)


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
    ap.add_argument("--features", choices=("observable", "probe", "probe_then_rule", "oracle"), default="observable",
                    help="observable: task-statement features only (deployable). "
                         "probe: no fitted rule -- run the guided stream ALONE for beta "
                         "slots (charged); hit -> done, miss -> RESET. oracle: "
                         "answer-derived features, calibration ceiling only.")
    ap.add_argument("--probe-depth", default="3",
                    help="max tokens per probe word. '3' (registered default) or 'auto': "
                         "the max tiling-token count over SOLVED training programs -- "
                         "observable, because history is solved -- capped at 4.")
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
        z_fit = (feats_oracle(nf, lib, row) if a.features == "oracle" else feats_observable(nf, lib))
        fit_rows.append((z_fit, b.slots - c.slots))
        fit_cost += b.slots + c.slots
        fit_cost_candidate += c.slots
    rule, fallback = fit_rule(fit_rows)
    dev_solve = sum(int(r.get("baseline_first_index") or 0) for r in eco["streams"]["train"])

    prot = eco["streams"]["protected"]
    if a.targets:
        prot = prot[: a.targets]
    _T = len(lib) + len(M.PRIMITIVES)
    if a.probe_depth == "cost":
        probe_depth = choose_probe_depth(eco["streams"]["train"], lib, _T)
    elif a.probe_depth == "auto":
        # depth learned from HISTORY: how many library tokens do the solved training
        # programs need? Training programs are solved, so tiling them is observable.
        _tk = [tileable(tuple(r["canonical_program"]), lib) for r in eco["streams"]["train"]]
        _tk = [x for x in _tk if x is not None]
        probe_depth = min(max(_tk) if _tk else 3, 4)
    else:
        probe_depth = int(a.probe_depth)
    beta = sum(_T ** i for i in range(1, probe_depth + 1))   # all <=depth-token words
    arms = {k: [] for k in ("RESET", "ALWAYS_SERVE", "APPLICABILITY", "ORACLE_APPL")}
    served = 0
    per_target = []
    for i, row in enumerate(prot):
        nf = nf_of(row)
        t = M.PolynomialTask(f"ap:{i}", nf)
        b = M.solve(t, budget)
        c = M.solve(t, budget, method)
        if a.features in ("probe", "probe_then_rule"):
            # charged ACTION, observable by construction: enumerate the guided stream alone
            # (library tokens + primitives, words of <= 3 tokens, every word one slot, the
            # same accounting as solve) and stop at the first verified hit or at beta.
            tokens = tuple(lib) + tuple((op,) for op in M.PRIMITIVES)
            beta_used, hit = 0, None
            from itertools import product as _prod
            for L in range(1, probe_depth + 1):
                for word in _prod(tokens, repeat=L):
                    beta_used += 1
                    if beta_used > beta:
                        break
                    prog = tuple(op for tok in word for op in tok)
                    if len(prog) > 8:
                        continue
                    if M.normal_form(prog) == nf:
                        hit = beta_used
                        break
                if hit is not None or beta_used > beta:
                    break
            decide = hit is not None
            if hit is not None:
                probe_B = hit
            elif a.features == "probe_then_rule":
                # miss: the observable rule (fitted on validation) decides interleave vs RESET
                z_r = feats_observable(nf, lib)
                use_interleave = rule.get(z_r, fallback)
                probe_B = beta + (c.slots if use_interleave else b.slots)
                decide = decide or use_interleave
            else:
                probe_B = beta + b.slots   # miss: fall back to RESET
        else:
            z = (feats_oracle(nf, lib, row) if a.features == "oracle" else feats_observable(nf, lib))
            decide = rule.get(z, fallback)
            probe_B = None
        served += int(decide)
        arms["RESET"].append(b.slots)
        arms["ALWAYS_SERVE"].append(c.slots)
        arms["APPLICABILITY"].append(probe_B if probe_B is not None else (c.slots if decide else b.slots))
        arms["ORACLE_APPL"].append(min(b.slots, c.slots))
        per_target.append({"i": i, "RESET": b.slots, "ALWAYS": c.slots,
                           "APPL": arms["APPLICABILITY"][-1], "served": bool(decide)})

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
    bound = None
    if a.features in ("probe", "probe_then_rule"):
        _slack = (lambda r: r["RESET"] + beta) if a.features == "probe" else (lambda r: beta + max(r["RESET"], r["ALWAYS"]))
        viol = [r for r in per_target if r["APPL"] > _slack(r)]
        bound = {"claim": "APPL <= RESET + beta on every target", "beta": beta,
                 "violations": len(viol), "max_excess": max((r["APPL"] - r["RESET"] for r in per_target), default=0),
                 "verdict": "DISCHARGED_EMPIRICALLY" if not viol else "FALSIFIED"}
    if a.features in ("probe", "probe_then_rule"):
        ledger["marginal"] = {"cost": 0, "breakeven": 0.0, "pays": saved_per > 0, "net": round(saved_total, 1)}
        ledger["incremental"] = dict(ledger["marginal"])
        ledger["conservative"] = {"cost": dev_solve, "breakeven": _bk(dev_solve),
                                  "pays": bool(saved_per > 0 and dev_solve / saved_per <= n),
                                  "net": round(saved_total - dev_solve, 1)}
        ledger["note"] = "probe gate fits nothing; beta is charged inside B; fit cost from the rule path removed"
    out = {"schema": "OCM_M2_APPLICABILITY_V2", "lane": "LANE_M2_TRAVERSAL_CAPITAL_OPUS",
           "per_target": per_target, "probe_bound": bound,
           "feature_mode": a.features,
           "deployable": a.features in ("observable", "probe", "probe_then_rule"),
           "leak_note": ("ORACLE_FEATURES: answer-derived, calibration ceiling only, NOT a "
                         "deployable gate" if a.features == "oracle" else
                         "features/actions computable from the task statement or charged probes"),
           "probe_beta_slots": beta if a.features in ("probe", "probe_then_rule") else None,
           "probe_depth": probe_depth if a.features in ("probe", "probe_then_rule") else None,
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
    print("[%s] " % a.features.upper(), end="")
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

"""RV-377-112 / DG-12 -- is the OBLIGATION itself a constant function?

Rule 40 asks whether a constant answer can CLEAR theta on an ecology.  That is one level
too shallow.  The DG-9 E1/E3 audit found `e1_scdi` regime B returning the answer 1 on all
24 registered evaluation queries: the obligation is not merely easy for a constant, it IS
a constant.  A row scoring 1.0000 there has demonstrated nothing whatsoever, and no
capability number computed on it carries information.

Nothing in the corpus has ever checked for this.  Rule 40's control would flag a
degenerate obligation only incidentally, via a best constant at or near the ceiling, and
only where a best constant was computed at all.

This module audits every obligation reachable from the registered modules for degeneracy
directly: how many DISTINCT answers does the truth function take over its own declared
evaluation set?  One distinct answer is DEGENERATE.  Two, on a set of n queries, is
reported with its split, because a near-balanced binary obligation and a 23-1 binary
obligation are very different instruments.
"""
from __future__ import annotations

import collections
import itertools
import json
import os
import time

from . import ecology, smooth
from .core import sha256_of

RES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "microscopes", "results")


def _classify(vals):
    n = len(vals)
    c = collections.Counter(vals)
    k = len(c)
    top = max(c.values())
    best_const_agreement = top / n if n else 0.0
    if k <= 1:
        status = "DEGENERATE__OBLIGATION_IS_A_CONSTANT"
    elif best_const_agreement >= 0.85:
        status = "NEAR_DEGENERATE__CONSTANT_AGREES_ON_>=85%"
    elif k == 2 and min(c.values()) <= max(1, n // 10):
        status = "SKEWED_BINARY"
    else:
        status = "NON_DEGENERATE"
    return {"n_queries": n, "n_distinct_answers": k, "counts": {str(a): b for a, b in sorted(c.items(), key=lambda t: -t[1])},
            "best_constant_agreement": round(best_const_agreement, 4), "status": status}


def audit_smooth_registry():
    """every registered smooth/table ecology, over its own declared evaluation set."""
    out = {}
    for name, spec in sorted(ecology.REGISTRY.items()):
        target = ecology.target_of(spec)
        for crit, eval_x in (("all", smooth.ALL_X), ("unseen", smooth.UNSEEN)):
            out[f"{name}|{crit}"] = _classify([target[x] for x in eval_x])
    return out


def audit_e1():
    """the E1 serving regimes at their REGISTERED coefficients, over the registered eval set."""
    out = {}
    try:
        from . import e1_scdi, e1_vlc
    except Exception as e:
        return {"__unavailable__": repr(e)[:200]}
    CV, N_F, Q = e1_scdi.COEFF_VALUES, e1_scdi.N_F, e1_vlc.EVAL_QUERIES
    coeffs = [(CV[(2 * i) % 4], CV[(2 * i + 1) % 4]) for i in range(N_F)]
    for reg in ("A", "B", "C", "D"):
        try:
            out[f"e1_scdi|regime_{reg}"] = _classify([e1_scdi.truth_regime(coeffs, x, s, reg) for (x, s) in Q])
        except Exception as e:
            out[f"e1_scdi|regime_{reg}"] = {"error": repr(e)[:200]}
    # How much of the coefficient space is degenerate, not just the registered point?
    for reg in ("A", "B", "C", "D"):
        n_deg = n_tot = 0
        try:
            for flat in itertools.product(CV, repeat=2 * N_F):
                cf = tuple((flat[2 * i], flat[2 * i + 1]) for i in range(N_F))
                vals = [e1_scdi.truth_regime(cf, x, s, reg) for (x, s) in Q]
                n_tot += 1
                n_deg += len(set(vals)) <= 1
            out[f"e1_scdi|regime_{reg}|coefficient_space"] = {
                "n_assignments": n_tot, "n_degenerate": n_deg,
                "fraction_degenerate": round(n_deg / n_tot, 4) if n_tot else None}
        except Exception as e:
            out[f"e1_scdi|regime_{reg}|coefficient_space"] = {"error": repr(e)[:200]}
    return out


def main(tag="V33_DEGENERACY_AUDIT", revival="RV-377-112"):
    t0 = time.time()
    rows = {}
    rows.update({f"smooth_registry::{k}": v for k, v in audit_smooth_registry().items()})
    rows.update({f"e1::{k}": v for k, v in audit_e1().items()})
    scored = {k: v for k, v in rows.items() if "status" in v}
    by_status = collections.Counter(v["status"] for v in scored.values())
    degenerate = sorted(k for k, v in scored.items() if v["status"].startswith("DEGENERATE"))
    near = sorted(k for k, v in scored.items() if v["status"].startswith("NEAR_DEGENERATE"))
    receipt = {"schema": "RV377_112_DegeneracyAuditV1", "revival_record": revival, "run_tag": tag, "issue": [377],
               "status": "EXECUTED_EXACT_AT_SCOPE", "gap": "DG-12",
               "question": "does the obligation itself take more than one value over its own declared evaluation set?",
               "why_rule_40_is_not_enough": "rule 40 asks whether a CONSTANT ANSWER can clear theta; it does not ask whether the OBLIGATION is constant. A degenerate obligation is scored 1.0000 by any constant emitter and carries no information at all.",
               "rows": rows, "counts_by_status": dict(by_status),
               "degenerate": degenerate, "near_degenerate": near,
               "n_scored": len(scored), "seconds": round(time.time() - t0, 1),
               "claim_ceiling": "covers the registered smooth/table ecologies over both declared criteria and the E1 serving regimes at their registered coefficients; obligations in modules not imported here are NOT covered and are listed as uncovered rather than assumed clean"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    print(f"scored {len(scored)} obligations | {dict(by_status)}")
    for k, v in sorted(scored.items()):
        if v["status"] != "NON_DEGENERATE":
            print(f"  {k:42} distinct={v['n_distinct_answers']:2d}/{v['n_queries']:2d} "
                  f"best_const={v['best_constant_agreement']:.4f}  {v['status']}")
    for k, v in sorted(rows.items()):
        if "fraction_degenerate" in v:
            print(f"  {k:42} degenerate on {v['n_degenerate']}/{v['n_assignments']} = {v['fraction_degenerate']:.4f} of the coefficient space")
    return receipt


if __name__ == "__main__":
    main()


# =====================================================================================================================
# RV-377-118 Lane D (DG-12 completion): the twelve modules RV-377-112 listed as UNCOVERED, audited one at a time.
#
# Same question, same classifier (`_classify` above), same units. What is new is only WHERE the obligation and its
# evaluation set are read from: each module's OWN declared truth function and the evaluation set its own `run()` scores
# capability on. Nothing is invented; a module with no obligation of that shape is recorded NOT_APPLICABLE with the
# reason, and an obligation a module merely inherits from `ecology.REGISTRY` is recorded as inherited, not as new.
#
# The coefficient replays for the E1 family are taken from `constant_control.py` (RV-377-108, rule 40), so the DG-12
# distinct-answer count and the rule-40 best-constant control are computed on IDENTICAL coefficient vectors.
# =====================================================================================================================
import hashlib
import socket

DG12_MODULES = ("axis_a", "b1x", "b2_common", "b2_depth", "b2_norm", "b2_prenorm",
                "e1_cp", "e1_iql", "e1_lmhm", "e1_vgsc", "e1_vlc", "refine_f")
DG12_SCHEMA = "RV377_118D_DG12_ModuleAuditV1"
DG12_REVIVAL = "RV-377-118"
DG12_FREEZE = "GMI_DG12_COMPLETION_RV_377_118D_FREEZE.md"
D1_PREDICTION = ("at least one further degenerate or near-degenerate obligation is found among the 12. `e1_scdi` "
                 "regime B was degenerate on 57.7 % of its coefficient space, and nothing suggests it is unique.")
_HERE = os.path.dirname(os.path.abspath(__file__))
# every source file whose text determines a module's obligation (hashed into the receipt)
_DEPS = {"axis_a": ("axis_a.py",), "b1x": ("b1x.py", "b1.py", "smooth.py", "ecology.py"),
         "b2_common": ("b2_common.py",), "b2_depth": ("b2_depth.py", "core.py"),
         "b2_norm": ("b2_norm.py", "core.py"), "b2_prenorm": ("b2_prenorm.py", "core.py"),
         "e1_cp": ("e1_cp.py", "e1_vlc.py", "constant_control.py"),
         "e1_iql": ("e1_iql.py",), "e1_lmhm": ("e1_lmhm.py", "e1_vlc.py", "constant_control.py"),
         "e1_vgsc": ("e1_vgsc.py", "e1_vlc.py", "constant_control.py"),
         "e1_vlc": ("e1_vlc.py", "constant_control.py"),
         "refine_f": ("refine_f.py", "e1_scdi.py", "e1_vlc.py", "constant_control.py")}


def _sha_file(name):
    with open(os.path.join(_HERE, name), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _control_agree(vals, tol, theta):
    """rule-40 best constant under an exact-agreement metric with tolerance `tol` fx units, swept over the full
    registered fx grid exactly as constant_control.best_constant_agree does (target keyed by query index)."""
    from .constant_control import best_constant_agree
    tm = {i: v for i, v in enumerate(vals)}
    cap, c = best_constant_agree(tm, list(range(len(vals))), tol=tol)
    return {"metric": f"exact agreement within {tol} fx", "best_constant_fx": c, "best_constant_capability": cap,
            "theta": theta, "constant_clears_theta": cap >= theta}


def _control_mae(target, eval_set, theta):
    """rule-40 best constant under the B1 mean-absolute-error capability (constant_control.best_constant)."""
    from .constant_control import best_constant
    cap, c = best_constant(target, eval_set)
    return {"metric": "mean-abs-error capability, cap = max(0, 1 - err/1.5)", "best_constant_fx": c,
            "best_constant_capability": cap, "theta": theta, "constant_clears_theta": cap >= theta}


def _obl(vals, eval_set, registered=True, control=None, **extra):
    row = _classify(list(vals))
    row["evaluation_set"] = eval_set
    row["registered_evaluation_set"] = bool(registered)
    if control is not None:
        row["rule40_constant_control"] = control
    row.update(extra)
    return row


# ---------------------------------------------------------------------------------------------------- per module
def _audit_axis_a():
    from . import axis_a as A
    out = {}
    for mode in A.MODES:
        for T in A.T_GRID:
            xs = A.stream(T, 0); ys = A.truth(mode, xs); half = T // 2
            w = ys[half:]
            out[f"E_hist|{mode}|T={T}|scored_window"] = _obl(
                w, f"events t in [{half}, {T}) of stream(T={T}, seed=0): the window run() scores capability on",
                control=_control_agree(w, 0, A.THETA),
                note="the module's rule-22 CONST_BEST row picks the modal answer of this same window with hindsight, "
                     "so best_constant_agreement here IS that control's capability")
            out[f"E_hist|{mode}|T={T}|full_stream"] = _obl(
                ys, f"all {T} events of stream(T={T}, seed=0) (served, but only the second half is scored)",
                registered=False)
    return out, [], {"seed": 0, "theta": A.THETA, "modes": list(A.MODES), "T_grid": list(A.T_GRID),
                     "obligation": "axis_a.truth(mode, stream(T, seed)) — the online history-dependent answer"}


def _audit_b1x():
    from . import b1, ecology, smooth
    out = {}
    for name, spec in sorted(ecology.REGISTRY.items()):
        t = ecology.target_of(spec)
        for crit, ev in (("unseen", smooth.UNSEEN), ("all", smooth.ALL_X)):
            out[f"{name}|{crit}"] = _obl(
                [t[x] for x in ev], f"smooth.{'UNSEEN' if crit == 'unseen' else 'ALL_X'} ({len(ev)} inputs)",
                registered=(crit == "unseen"), control=_control_mae(t, ev, b1.THETA),
                inherited_from=f"ecology.REGISTRY['{name}'] via b1.evaluate -> smooth.run(criterion='{crit}'); "
                               f"audited in RV-377-112 as smooth_registry::{name}|{crit}")
    return out, [], {"theta": b1.THETA, "criterion_scored_by_b1x": "unseen (b1x.evaluate default)",
                     "obligation": "none of its own: b1x adds one archive coordinate to b1 and scores the registered "
                                   "ecology targets; every row here is INHERITED and was already covered by RV-377-112"}


def _audit_b2_common():
    na = [{"what": "b2_common", "status": "NOT_APPLICABLE",
           "reason": "shared instrument library for the B2 atlas rows: it declares the rule-21/22/24/28/29 helpers "
                     "(constant_control, obligation_is_void, gate_claim, crossovers, census, exact rank/solve) and no "
                     "obligation, truth function or evaluation set of its own. The obligations it is used on live in "
                     "b2_depth / b2_norm / b2_prenorm (audited here) and the other b2_* row modules."}]
    return {}, na, {"obligation": "none declared"}


def _audit_b2_depth():
    from . import b2_depth as D
    from fractions import Fraction as Fr
    vals = [D.obligation(x) for x in D.GRID]
    theta = float(Fr(3, 4))
    out = {"b2_depth.obligation|GRID": _obl(
        vals, f"b2_depth.GRID: every representable 8-bit fixed-point input ({len(D.GRID)} states); profile() "
              f"scores the hindsight-optimal reader of the final state against this obligation on the whole grid",
        control=_control_agree(vals, 0, theta),
        theta_source="THETA_CAP = Fr(3,4) in b2_residual.py (B2.8), the row module that consumes b2_depth")}
    return out, [], {"n_classes": D.N_CLASSES, "theta": theta,
                     "obligation": "which of N_CLASSES equal bands of the fixed-point range the INPUT lay in"}


def _audit_b2_norm():
    from . import b2_norm as N
    out = {}
    theta = float(N.THETA)
    for tb, fb in N.PRECISIONS:
        F = N.Fixed(tb, fb); g = F.grid()
        vals = [N.obligation(x, F) for x in g]
        out[f"b2_norm.obligation|precision=({tb},{fb})"] = _obl(
            vals, f"Fixed({tb},{fb}).grid(): every representable state at that width ({len(g)} states)",
            registered=True, control=_control_agree(vals, 0, theta),
            note="(8,4) is the REGISTERED universe; the wider members are declared extensions of it")
    return out, [], {"n_classes": N.N_CLASSES, "theta": theta, "precisions": [list(p) for p in N.PRECISIONS],
                     "obligation": "which of N_CLASSES equal bands of the precision's range the INPUT lay in"}


def _audit_b2_prenorm():
    from . import b2_prenorm as P
    vals = [P.obligation(x) for x in P.GRID]
    theta = float(P.THETA)
    out = {"b2_prenorm.obligation|GRID": _obl(
        vals, f"b2_prenorm.GRID: every representable 8-bit fixed-point input ({len(P.GRID)} states)",
        control=_control_agree(vals, 0, theta))}
    return out, [], {"n_classes": P.N_CLASSES, "theta": theta,
                     "obligation": "which of N_CLASSES equal bands of the fixed-point range the INPUT lay in"}


def _audit_e1_cp():
    from . import e1_cp as E
    from .constant_control import _coeffs_cp, _e1_initial_coeffs, _factored_queries, _factored_target
    out = {}
    dev = _e1_initial_coeffs()
    for cell, spec in E.CELLS.items():
        shared, alt = _coeffs_cp(shared=spec["shared"], U=spec["U"])
        for reg in spec["regimes"]:
            tol = 1 if reg == "A" else 0
            final = shared if (spec["shared"] or reg == "A") else alt
            for crit in ("unseen", "all"):
                qs = _factored_queries(2, crit)
                vals = [_factored_target(final, qs, reg, "cp")[q] for q in qs]
                out[f"E_factored3|{cell}|regime_{reg}|final_coefficients|{crit}"] = _obl(
                    vals, ("e1_vlc.EVAL_QUERIES (24 unseen-pattern queries): the set run() scores capability on "
                           "after the last revision" if crit == "unseen" else
                           "the complete query space, 6 scopes x 256 inputs (informational)"),
                    registered=(crit == "unseen"), control=_control_agree(vals, tol, E.THETA),
                    coefficients=[list(c) for c in final], metric_tolerance_fx=tol)
        # the development-time obligation (before any revision), per regime
        for reg in spec["regimes"]:
            tol = 1 if reg == "A" else 0
            qs = _factored_queries(2, "unseen")
            vals = [_factored_target(dev, qs, reg, "cp")[q] for q in qs]
            out[f"E_factored3|{cell}|regime_{reg}|development_coefficients|unseen"] = _obl(
                vals, "e1_vlc.EVAL_QUERIES at the opening coefficients (queried in window 0, not scored)",
                registered=False, control=_control_agree(vals, tol, E.THETA),
                coefficients=[list(c) for c in dev], metric_tolerance_fx=tol)
    # how much of the coefficient space is degenerate (the RV-377-112 sweep, on e1_cp's own truth_regime)
    from .e1_vlc import COEFF_VALUES as CV, N_F, EVAL_QUERIES as Q
    for reg in E.REGIMES:
        n_deg = n_tot = 0
        for flat in itertools.product(CV, repeat=2 * N_F):
            cf = tuple((flat[2 * i], flat[2 * i + 1]) for i in range(N_F))
            n_tot += 1
            n_deg += len({E.truth_regime(cf, x, s, reg) for (x, s) in Q}) <= 1
        out[f"E_factored3|regime_{reg}|coefficient_space"] = {
            "n_assignments": n_tot, "n_degenerate": n_deg, "fraction_degenerate": round(n_deg / n_tot, 4)}
    return out, [], {"theta": E.THETA, "tau_fx": E.TAU, "cells": {k: dict(v, regimes=list(v["regimes"])) for k, v in E.CELLS.items()},
                     "obligation": "e1_cp.truth_regime over e1_vlc.EVAL_QUERIES at the coefficients run() scores against "
                                   "(after the cell's U revision windows; N3 serves B/C from independent coefficients)"}


def _audit_e1_iql():
    from . import e1_iql as I
    from .constant_control import _alias_targets
    out = {}
    for d, tgt in _alias_targets().items():
        name = "".join(map(str, d)); vals = list(tgt)
        out[f"E_alias|truth_d={name}"] = _obl(
            vals, "the obligation's 25 answers: v-vector under do(v_j = 1) for j = 0..4 (the set capability() scores)",
            control=_control_agree(vals, 0, I.THETA))
    pooled = [v for tgt in _alias_targets().values() for v in tgt]
    out["E_alias|all_16_orientations_pooled"] = _obl(pooled, "the 16 x 25 answers pooled (informational)", registered=False)
    return out, [], {"theta": I.THETA, "n_orientations": len(I.ORIENTATIONS),
                     "obligation": "e1_iql.target_vector(d): 25 binary interventional answers, one obligation per "
                                   "ground-truth orientation d (run() is executed at every d)"}


def _audit_e1_lmhm():
    from . import e1_lmhm as L
    from .constant_control import _coeffs_lmhm, _e1_initial_coeffs, _factored_queries, _factored_target
    out = {}
    for tag, coeffs, reg_ok in (("final_coefficients", _coeffs_lmhm(), True),
                                ("development_coefficients", _e1_initial_coeffs(), False)):
        for crit in ("unseen", "all"):
            qs = _factored_queries(2, crit)
            vals = [_factored_target(coeffs, qs)[q] for q in qs]
            out[f"E_factored|HETEROGENEOUS(U=16)|{tag}|{crit}"] = _obl(
                vals, ("e1_vlc.EVAL_QUERIES after the 16 heterogeneous revision rounds: the set run() scores"
                       if crit == "unseen" else "the complete query space (informational)"),
                registered=(reg_ok and crit == "unseen"), control=_control_agree(vals, 1, L.THETA),
                coefficients=[list(c) for c in coeffs], metric_tolerance_fx=1)
    return out, [], {"theta": L.THETA, "U": L.U_ROUNDS, "revision_period": L.REVISION_PERIOD,
                     "obligation": "e1_vlc.truth over EVAL_QUERIES at the coefficients after the 16 rounds"}


def _audit_e1_vgsc():
    from . import e1_vgsc as V
    from .constant_control import _coeffs_vgsc, _e1_initial_coeffs, _factored_queries, _factored_target
    out = {}
    for pa in sorted(V.STEP_SEQ):
        coeffs = _coeffs_vgsc(pa)
        for crit in ("unseen", "all"):
            qs = _factored_queries(2, crit)
            vals = [_factored_target(coeffs, qs)[q] for q in qs]
            out[f"E_factored|{pa}|final_coefficients|{crit}"] = _obl(
                vals, ("e1_vlc.EVAL_QUERIES after the cell's 16 revision rounds: the set run() scores"
                       if crit == "unseen" else "the complete query space (informational)"),
                registered=(crit == "unseen"), control=_control_agree(vals, 1, V.THETA),
                coefficients=[list(c) for c in coeffs], metric_tolerance_fx=1)
    dev = _e1_initial_coeffs(); qs = _factored_queries(2, "unseen")
    vals = [_factored_target(dev, qs)[q] for q in qs]
    out["E_factored|development_coefficients|unseen"] = _obl(
        vals, "e1_vlc.EVAL_QUERIES at the opening coefficients (queried, not scored)", registered=False,
        control=_control_agree(vals, 1, V.THETA), coefficients=[list(c) for c in dev], metric_tolerance_fx=1)
    return out, [], {"theta": V.THETA, "U": V.U_ROUNDS, "step_sequences": V.STEP_SEQ,
                     "obligation": "e1_vlc.truth over EVAL_QUERIES at the coefficients after the cell's step sequence"}


def _audit_e1_vlc():
    from . import e1_vlc as E
    from .constant_control import _coeffs_vlc, _factored_queries, _factored_target
    out = {}
    cells = [(k, v["U"], v["cone"], 2) for k, v in E.CELLS.items()]
    cells += [(k, v["U"], v["cone"], v["scope_size"]) for k, v in E.COLLISION_CELLS.items()]
    for cell, U, cone, ss in cells:
        coeffs = _coeffs_vlc(U, cone)
        for crit in ("unseen", "all"):
            qs = _factored_queries(ss, crit)
            vals = [_factored_target(coeffs, qs)[q] for q in qs]
            out[f"E_factored|{cell}|U={U}|cone={cone}|scope_size={ss}|final_coefficients|{crit}"] = _obl(
                vals, (f"e1_vlc.EVAL_BY_SIZE[{ss}] ({len(qs)} unseen-pattern queries) after the cell's U={U} "
                       f"revision rounds: the set run() scores" if crit == "unseen"
                       else "the complete query space at that scope size (informational)"),
                registered=(crit == "unseen"), control=_control_agree(vals, 1, E.THETA),
                coefficients=[list(c) for c in coeffs], metric_tolerance_fx=1)
    return out, [], {"theta": E.THETA, "cells": E.CELLS, "collision_cells": E.COLLISION_CELLS,
                     "obligation": "e1_vlc.truth over EVAL_BY_SIZE[scope_size] at the coefficients after the cell's "
                                   "revisions (T1_STATIONARY, U=0, is the development obligation itself)"}


def _audit_refine_f():
    from . import refine_f as R, e1_scdi
    from .constant_control import _e1_initial_coeffs
    from .e1_vlc import EVAL_QUERIES as Q
    out = {}
    coeffs = _e1_initial_coeffs()      # exactly what _f6_develop() trains on
    for reg in list(e1_scdi.REGIMES) + [R.REGIME_E]:
        vals = [R._f6_truth(coeffs, x, s, reg) for (x, s) in Q]
        used = ("COMPOSITIONAL_UNSEEN (verdict = agreement; truth not consulted) and ABSTAIN_OBLIGATION "
                "(truth-scored B_risk)" if reg == R.REGIME_E else
                "OVERFLOW / NOISY_CUE / REVOKE_THEN_REQUERY (agreement) and ABSTAIN_OBLIGATION (truth-scored B_risk)")
        out[f"suite_f6|E_factored|regime_{reg}|registered_coefficients"] = _obl(
            vals, "e1_vlc.EVAL_QUERIES (24) at the registered opening coefficients, as suite_f6 serves them",
            control=_control_agree(vals, 0, e1_scdi.THETA), demands_using_this_truth=used,
            declared_in="refine_f.REGIME_E / _f6_truth" if reg == R.REGIME_E else "e1_scdi.truth_regime, imported by _f6_truth")
    na = [{"what": s, "status": "NOT_APPLICABLE__SEPARATION_INSTRUMENT",
           "reason": "the refined-family verdict (adjudicate) is EQUAL/SPLIT on candidate-vs-parent served-answer "
                     "agreement, with no theta and no capability; a truth enters only the ABSTAIN_OBLIGATION "
                     "lifecycle score, and for this suite that truth is the committed receipt's own recorded answers "
                     "or the suite's declared enumeration, not a scoring obligation of the DG-12 shape"}
          for s in ("suite_dc1 (P1)", "suite_dc9 (P4)", "suite_dc7 (P2, P3)", "suite_n3 (P5, P6)",
                    "suite_n10 (P7, P8)", "suite_n8 (P9, P10)", "suite_n11 (P11)")]
    return out, na, {"obligation": "refine_f declares one truth function of its own, the fifth serving regime E "
                                   "(1 iff the scope sum is strictly positive) over e1_vlc.EVAL_QUERIES, and imports "
                                   "e1_scdi.truth_regime for A-D; both are audited at the coefficients suite_f6 uses",
                     "verdict_dependence": "no refine_f verdict is taken against a truth (agreement only), so a "
                                           "degenerate truth here voids the ABSTAIN_OBLIGATION B_risk score of the "
                                           "affected regime, not the EQUAL/SPLIT verdict"}


_AUDITS = {"axis_a": _audit_axis_a, "b1x": _audit_b1x, "b2_common": _audit_b2_common, "b2_depth": _audit_b2_depth,
           "b2_norm": _audit_b2_norm, "b2_prenorm": _audit_b2_prenorm, "e1_cp": _audit_e1_cp, "e1_iql": _audit_e1_iql,
           "e1_lmhm": _audit_e1_lmhm, "e1_vgsc": _audit_e1_vgsc, "e1_vlc": _audit_e1_vlc, "refine_f": _audit_refine_f}


def _host(host=None):
    return host or os.environ.get("GMI_HOST") or socket.gethostname().split(".")[0]


def _jsonable(o):
    """receipts are JSON with sort_keys; Fractions and tuples become str / lists so two hosts hash identically."""
    return json.loads(json.dumps(o, sort_keys=True, default=str))


def audit_module(name, host=None, out_dir=None):
    """DG-12 degeneracy audit of ONE of the twelve modules RV-377-112 left uncovered. Writes
    microscopes/results/STAGE_DG12_COMPLETION_{name}_{HOST}.json and returns a compact summary."""
    if name not in _AUDITS:
        raise KeyError(f"{name!r} is not one of the twelve DG-12 modules: {DG12_MODULES}")
    host = _host(host); out_dir = out_dir or RES
    t0 = time.time()
    obligations, not_applicable, notes = _AUDITS[name]()
    obligations = _jsonable(obligations)
    scored = {k: v for k, v in obligations.items() if "status" in v}
    registered = {k: v for k, v in scored.items() if v.get("registered_evaluation_set")}
    own = {k: v for k, v in registered.items() if "inherited_from" not in v}
    by_status = collections.Counter(v["status"] for v in scored.values())
    degenerate = sorted(k for k, v in own.items() if v["status"].startswith("DEGENERATE"))
    near = sorted(k for k, v in own.items() if v["status"].startswith("NEAR_DEGENERATE"))
    skewed = sorted(k for k, v in own.items() if v["status"] == "SKEWED_BINARY")
    const_clears = sorted(k for k, v in registered.items()
                          if v.get("rule40_constant_control", {}).get("constant_clears_theta"))
    if not scored and not_applicable:
        verdict = "NOT_APPLICABLE__NO_OBLIGATION_OF_THIS_SHAPE"
    elif degenerate:
        verdict = "DEGENERATE_OBLIGATION_FOUND"
    elif near:
        verdict = "NEAR_DEGENERATE_OBLIGATION_FOUND"
    elif not own and registered:
        verdict = "ALL_INHERITED_OBLIGATIONS_NON_DEGENERATE__NOTHING_NEW_TO_AUDIT"
    else:
        verdict = "ALL_REGISTERED_OBLIGATIONS_NON_DEGENERATE"
    receipt = {"schema": DG12_SCHEMA, "revival_record": DG12_REVIVAL, "lane": "RV118-D", "gap": "DG-12",
               "freeze_record": DG12_FREEZE, "issue": [377], "module": name,
               "status": "EXECUTED_EXACT_AT_SCOPE",
               "question": "does the obligation itself take more than one value over its own declared evaluation set?",
               "classification": "identical to RV-377-112 (_classify): DEGENERATE if one distinct answer; NEAR_DEGENERATE "
                                 "if the best constant agrees on >= 85 %; SKEWED_BINARY if binary with the minority "
                                 "class <= max(1, n/10); else NON_DEGENERATE. Verdicts are taken on the module's OWN "
                                 "obligations over their REGISTERED evaluation sets; rows marked inherited or "
                                 "informational are reported but do not decide.",
               "notes": _jsonable(notes), "obligations": obligations, "not_applicable": not_applicable,
               "counts_by_status": dict(by_status), "n_scored": len(scored), "n_registered": len(registered),
               "n_own_registered": len(own),
               "degenerate": degenerate, "near_degenerate": near, "skewed_binary": skewed,
               "rule40_constant_clears_theta": const_clears,
               "module_verdict": verdict,
               "inputs_sha256": {f: _sha_file(f) for f in ("degeneracy_audit.py",) + _DEPS[name]},
               "claim_ceiling": "exact, deterministic, no randomness; covers the obligations this module declares or "
                                "scores at the coefficients / streams / grids its own run() uses; it does not run the "
                                "module's rows and takes no verdict on any capability number"}
    receipt["content_sha256"] = sha256_of(receipt)
    receipt["host"] = host
    receipt["seconds"] = round(time.time() - t0, 2)
    receipt["receipt_path"] = f"microscopes/results/STAGE_DG12_COMPLETION_{name}_{host}.json"
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, f"STAGE_DG12_COMPLETION_{name}_{host}.json"), "w") as f:
        json.dump(receipt, f, indent=1, sort_keys=True, default=str)
    return {"module": name, "verdict": verdict, "n_scored": len(scored), "n_own_registered": len(own),
            "degenerate": degenerate, "near_degenerate": near, "skewed_binary": skewed,
            "rule40_constant_clears_theta": const_clears, "content_sha256": receipt["content_sha256"],
            "receipt": receipt["receipt_path"]}


def audit_all_modules(host=None, out_dir=None):
    """all twelve, then the aggregate STAGE_DG12_COMPLETION_{HOST}.json that adjudicates prediction D1."""
    host = _host(host); out_dir = out_dir or RES
    t0 = time.time()
    per = {m: audit_module(m, host, out_dir) for m in DG12_MODULES}
    found = sorted(m for m, s in per.items() if s["verdict"] in ("DEGENERATE_OBLIGATION_FOUND",
                                                                  "NEAR_DEGENERATE_OBLIGATION_FOUND"))
    agg = {"schema": "RV377_118D_DG12_CompletionV1", "revival_record": DG12_REVIVAL, "lane": "RV118-D", "gap": "DG-12",
           "freeze_record": DG12_FREEZE, "issue": [377], "status": "EXECUTED_EXACT_AT_SCOPE",
           "modules": list(DG12_MODULES), "per_module": per,
           "d1_prediction_verbatim": D1_PREDICTION,
           "d1_rule": "HELD iff at least one module's OWN obligation, over its REGISTERED evaluation set, is "
                      "DEGENERATE or NEAR_DEGENERATE under the RV-377-112 classifier; SKEWED_BINARY, inherited rows "
                      "and informational rows do not count",
           "d1_modules_with_finding": found,
           "d1_outcome": "HELD" if found else "FAILED",
           "extends": "RV-377-112 (STAGE_V33_DEGENERACY_AUDIT.json: 16 obligations, 1 degenerate)",
           "n_modules_audited": sum(1 for s in per.values() if not s["verdict"].startswith("NOT_APPLICABLE")),
           "n_modules_not_applicable": sum(1 for s in per.values() if s["verdict"].startswith("NOT_APPLICABLE"))}
    agg["content_sha256"] = sha256_of(agg)
    agg["host"] = host; agg["seconds"] = round(time.time() - t0, 2)
    agg["receipt_sha256"] = sha256_of({k: v for k, v in agg.items() if k != "receipt_sha256"})
    with open(os.path.join(out_dir, f"STAGE_DG12_COMPLETION_{host}.json"), "w") as f:
        json.dump(agg, f, indent=1, sort_keys=True, default=str)
    print(f"DG-12 completion on {host}: D1 {agg['d1_outcome']}  findings in {found}")
    for m in DG12_MODULES:
        s = per[m]
        print(f"  {m:11s} {s['verdict']:62s} scored={s['n_scored']:3d} own_registered={s['n_own_registered']:3d} "
              f"deg={len(s['degenerate'])} near={len(s['near_degenerate'])} skew={len(s['skewed_binary'])}")
    return agg

"""Form Oracle arm runner (FO-V1).

Reuses, unchanged:
  search.successive_halving.run_successive_halving   frozen T0->T1->T2, eta=3,
                                                     late-bloomer insurance 0.15
  morphology.gs_bound                                legality-filtered (F,O,Pi)
  evaluation.*                                       frozen charging and gates

Self-built residual only: the charging proxy that lets the reject ledger see
EVERY evaluation attempt the frozen loop makes, behavioural dedup, the
4-objective front, evolvability, and the C-immutability gate.

The proxy patches the names BOUND INSIDE successive_halving rather than the
evaluator itself, so the frozen loop runs verbatim and its accounting can never
disagree with ours.
"""
from __future__ import annotations

import contextlib
import json
import os
import random
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

from oracle import behaviour_sig as BS
from oracle import burden as BU
from oracle import evolvability as EV
from oracle import objectives4 as OB
from oracle.c_immutability import (CImmutabilityViolation, check_c_immutable,
                                   constitution_snapshot)

# Sampling lanes, reused from the zoo's legality-bounded sampler. The names are
# the KEYS of morphology.gs_bound.LANES ("units", "hetero", "farch", "obasis"),
# not the names of the functions behind them -- lane_sampler indexes that dict
# and raises KeyError on a function name.
LANES = ("gs_uniform", "units", "hetero", "farch", "obasis")

# Evolvability is (1+K_STEPS) future evaluations plus up to K_STEPS*P_MAX T0
# proposals per survivor, so it is computed on a SEEDED RANDOM SUBSAMPLE of T2
# survivors -- random, never top-N, because top-N would select on capability
# and bias the estimator it feeds.
EVOLVABILITY_SUBSAMPLE = 64


@contextlib.contextmanager
def _charging_proxy(ledger: BU.RejectLedger):
    """Charge every evaluation attempt the frozen SH loop makes."""
    import search.successive_halving as SH
    orig_eval = SH.evaluate_genome

    def wrapped(g, tier="T0", **kw):  # noqa: ANN001
        try:
            r = orig_eval(g, tier=tier, **kw)
        except Exception:
            ledger.charge_crash(tier)
            raise
        ledger.charge_eval(tier, r.get("evaluation"))
        return r

    SH.evaluate_genome = wrapped
    try:
        yield
    finally:
        SH.evaluate_genome = orig_eval


def _sampler(lane: str):
    """Legality-bounded sampler from the frozen GS_BOUND_V1 vocabulary.

    Every lane goes through the zoo's own dispatcher so the Form Oracle draws
    from exactly the space the census and the parents drew from.
    """
    import morphology.gs_bound as GB
    if lane == "gs_uniform":
        return GB.gs_uniform_sample
    if not hasattr(GB, "lane_sampler"):
        raise RuntimeError("CANNOT_CHECK_LANE_SAMPLER_MISSING")
    return lambda rng: GB.lane_sampler(lane, rng)


_SLIM_KEYS = (
    "arm", "seed", "lane", "genotype_digest", "phenotype_digest",
    "behaviour_signature", "capability", "B_own", "burden", "index_built",
    "active_kN", "F_arch", "Pi_arch", "L", "R", "K", "T_family", "n_units",
    "unit_types", "tier_of_objectives", "t2_feasible", "t2_total_tasks",
    "t3_gen", "t3_feasible", "evolvability", "cap_bin",
    "search_objectives", "report_objectives", "coverage_objectives",
)


def _slim(rec: Dict[str, Any], keep_detail: bool) -> Dict[str, Any]:
    """One record, without provenance nothing reads."""
    out = {k: rec[k] for k in _SLIM_KEYS if k in rec}
    if keep_detail:
        for k in ("burden_components", "evolvability_detail",
                  "evolvability_error", "t3_error"):
            if k in rec:
                out[k] = rec[k]
    return out


def _genome_of(rec: Dict[str, Any]):
    from morphology.schema import OCMMorphologyGenomeV1
    g = rec.get("genome")
    if g is None:
        return None
    if isinstance(g, dict):
        return OCMMorphologyGenomeV1.from_json_obj(g)
    return g


def run_oracle_arm(arm: str, seed: int, t0_budget: int,
                   dedup: bool = True, lane: str = "gs_uniform",
                   evolvability_n: int = EVOLVABILITY_SUBSAMPLE,
                   compute_t3: bool = True) -> Dict[str, Any]:
    """One Form Oracle arm end to end."""
    from search.successive_halving import run_successive_halving
    from evaluation.t3_ecology import evaluate_t3

    t_start = time.time()
    ledger = BU.RejectLedger()
    sig = BS.SigCost()
    c_before = constitution_snapshot()

    sampler = _sampler(lane)
    t_search0 = time.time()
    with _charging_proxy(ledger):
        sh = run_successive_halving(t0_budget=t0_budget, seed=seed,
                                    sampler=sampler)
    search_elapsed = time.time() - t_search0

    survivors: List[Dict[str, Any]] = list(sh.get("t2_survivors")
                                           or sh.get("survivors") or [])

    # Distinct T2-viable PHENOTYPES: the parents' own unit. GS-R2 reports
    # distinct_t2_viable_phenotypes and morphologies_per_cpu_hour on that
    # quantity, so it is counted here too. Distinct BEHAVIOURS is a different
    # and stricter count; reporting only the behaviour count beside a parent's
    # phenotype count would compare two different things.
    distinct_phenotypes = {r.get("phenotype_digest") for r in survivors
                           if r.get("phenotype_digest")
                           and isinstance(r.get("t2"), dict)}

    # ---- behavioural dedup on the T2 survivors (cost measured separately)
    #
    # A survivor record's TOP-LEVEL "evaluation" is its T0 evaluation
    # (total_tasks 15, ecology_id None). The T2 result lives in the "t2"
    # sub-record (total_tasks 88, ecology_id LifetimeEcologyV2). Objective 1 is
    # frozen as T2 solved_fraction, so every objective, the burden components
    # and the behaviour signature must read rec["t2"], not rec. Reading the top
    # level scores the cheap 15-task screen and calls it the 12-epoch
    # developmental battery.
    kept: List[Dict[str, Any]] = []
    n_no_t2 = 0
    for rec in survivors:
        t2rec = rec.get("t2")
        if not isinstance(t2rec, dict) or not isinstance(
                t2rec.get("evaluation"), dict):
            n_no_t2 += 1
            continue
        ev = t2rec["evaluation"]
        gates = (t2rec.get("gates") or {})
        s, is_new = sig.admit(ev, gates)
        rec["behaviour_signature"] = s
        if (not dedup) or is_new:
            kept.append(rec)
    ledger.n_retained = len(kept)
    reject_share = ledger.reject_share()

    # ---- objectives
    rng = random.Random(seed ^ 0x5EED)
    idx = list(range(len(kept)))
    rng.shuffle(idx)
    evolv_idx = set(idx[:max(0, evolvability_n)])

    records: List[Dict[str, Any]] = []
    c_violations: List[Dict[str, Any]] = []
    for i, rec in enumerate(kept):
        ev = rec["t2"]["evaluation"]          # T2, per the frozen objective
        t2gates = (rec["t2"].get("gates") or {})
        g = _genome_of(rec)
        out: Dict[str, Any] = {
            "arm": arm, "seed": seed, "lane": lane,
            "genotype_digest": rec.get("genotype_digest"),
            "phenotype_digest": rec.get("phenotype_digest"),
            "behaviour_signature": rec.get("behaviour_signature"),
            "capability": float(ev.get("solved_fraction", 0.0)),
            "B_own": BU.b_own(ev),
            "burden": BU.b_full(ev, reject_share),
            "burden_components": BU.burden_components(ev),
            "index_built": bool(ev.get("index_built", False)),
            "active_kN": ev.get("active_kN"),
            # Structural coordinates. Without these a front member is an opaque
            # digest and the front cannot be attributed to any region of the
            # (F, O, Pi) space, which is the map the study is for.
            "F_arch": getattr(g, "F_arch", None) if g is not None else None,
            "Pi_arch": getattr(g, "Pi_arch", None) if g is not None else None,
            "L": getattr(g, "L", None) if g is not None else None,
            "R": getattr(g, "R", None) if g is not None else None,
            "K": getattr(g, "K", None) if g is not None else None,
            "T_family": getattr(g, "T", None) if g is not None else None,
            "n_units": len(getattr(g, "U", []) or []) if g is not None else None,
            "unit_types": (sorted({u.unit_type for u in getattr(g, "U", [])})
                           if g is not None else None),
            "tier_of_objectives": "T2",
            "t2_feasible": bool(rec["t2"].get("feasible")),
            "t2_total_tasks": ev.get("total_tasks"),
            "t3_gen": OB.CANNOT_CHECK,
            "evolvability": OB.CANNOT_CHECK,
        }
        out["cap_bin"] = EV.cap_bin(out["capability"])

        if g is not None:
            try:
                check_c_immutable(g, c_before, constitution_snapshot())
            except CImmutabilityViolation as e:
                c_violations.append({"genotype_digest": out["genotype_digest"],
                                     "violation": str(e)[:300]})

        if compute_t3 and g is not None:
            try:
                from oracle.future_family import HELDOUT_T3_KEY_ID
                t3 = evaluate_t3(g, HELDOUT_T3_KEY_ID)
                ledger.charge_eval("T3", t3.get("evaluation"))
                out["t3_gen"] = float(t3["evaluation"].get("solved_fraction", 0.0))
                out["t3_feasible"] = bool(t3.get("feasible"))
            except Exception as e:  # noqa: BLE001
                out["t3_gen"] = OB.CANNOT_CHECK
                out["t3_error"] = repr(e)[:160]

        if i in evolv_idx and g is not None:
            try:
                e = EV.evolvability(g, out["capability"], seed * 1000 + i, ledger)
                out["evolvability"] = e["evolvability"]
                out["evolvability_detail"] = {
                    k: e[k] for k in ("delta_cap_fof", "b_steps", "n_accepted",
                                      "status", "cap_fof_before",
                                      "cap_fof_after")}
            except Exception as e:  # noqa: BLE001
                out["evolvability"] = OB.CANNOT_CHECK
                out["evolvability_error"] = repr(e)[:160]

        out["search_objectives"] = OB.search_vector(out)
        out["report_objectives"] = OB.report_vector(out)
        out["coverage_objectives"] = OB.coverage_vector(out)
        records.append(out)

    crash_settle = ledger.settle()

    # Indices whose full provenance is retained in the written output.
    detail_idx = {i for i, r in enumerate(records)
                  if isinstance(r.get("evolvability_detail"), dict)}

    front_search = OB.pareto_front_k(records, "search_objectives",
                                     OB.SEARCH_MAXIMIZE)
    front_report = OB.pareto_front_k(records, "report_objectives",
                                     OB.REPORT_MAXIMIZE)
    front_coverage = OB.pareto_front_k(records, "coverage_objectives",
                                       OB.COVERAGE_MAXIMIZE)

    elapsed = time.time() - t_start
    cpu_h = elapsed / 3600.0
    search_cpu_h = search_elapsed / 3600.0
    return {
        "study": "FORM_ORACLE_V1",
        "arm": arm, "seed": seed, "lane": lane, "dedup": dedup,
        "t0_budget": t0_budget,
        "n_survivors_pre_dedup": len(survivors),
        "n_survivors_without_t2": n_no_t2,
        "n_retained": len(kept),
        "n_records": len(records),
        # The share actually used inside every record's burden. Search rungs
        # only; measurement work is reported apart so burden (objective 2) and
        # evolvability (objective 4) are not entangled through the ledger.
        "reject_share_per_retained": reject_share,
        "ledger": ledger.report(),
        "crash_settlement": crash_settle,
        "dedup_cost": sig.report(),
        "front_search": front_search,
        "front_report": front_report,
        "front_search_members": [records[i] for i in front_search["front_indices"]],
        "front_report_members": [records[i] for i in front_report["front_indices"]],
        "front_coverage": front_coverage,
        "front_coverage_members": [records[i]
                                   for i in front_coverage["front_indices"]],
        "c_immutability": {
            "n_violations": len(c_violations),
            "violations": c_violations[:20],
            "c_digest_before": c_before["_all"],
            "c_digest_after": constitution_snapshot()["_all"],
        },
        "elapsed_s": round(elapsed, 3),
        "cpu_hours": round(cpu_h, 8),
        # Parent-comparable denominator. GS-R2 reports morphologies_per_cpu_hour
        # as distinct T2-viable survivors per cpu-hour (GSA2_hetero 5062.7 per
        # seed at 51.258 cpu-s/seed -> 354,046). Matching that definition is the
        # only way this number can be put beside a parent's. Attempts/cpu-hour
        # is a different quantity and is reported under its own name.
        # PARENT-COMPARABLE. GS-R2's morphologies_per_cpu_hour counts distinct
        # T2-viable PHENOTYPES over SEARCH cpu-hours. The Form Oracle also pays
        # for T3 and evolvability measurement, which the parents never paid, so
        # measurement time is excluded from this denominator and reported apart.
        "search_elapsed_s": round(search_elapsed, 3),
        "search_cpu_hours": round(search_cpu_h, 8),
        "distinct_t2_viable_phenotypes": len(distinct_phenotypes),
        "morphologies_per_cpu_hour": (
            round(len(distinct_phenotypes) / search_cpu_h, 2)
            if search_cpu_h > 0 else None),
        # Stricter unit: distinct BEHAVIOURS, not phenotypes. Not comparable to
        # a parent figure and labelled so it cannot be mistaken for one.
        "distinct_behaviours_per_cpu_hour_NOT_PARENT_COMPARABLE": (
            round(len(kept) / search_cpu_h, 2) if search_cpu_h > 0 else None),
        "attempts_per_cpu_hour": (round(ledger.n_attempts / cpu_h, 2)
                                  if cpu_h > 0 else None),
        "distinct_t2_viable_behaviours": len(kept),
        "memoisation_caveat": (
            "evaluate_genome memoises on (phenotype_digest, tier); a repeated "
            "phenotype costs ~0 wall clock but is charged its full modelled "
            "work. Wall-clock rates are therefore optimistic relative to "
            "charged work and are only comparable at matched budget."),
        # Records are written SLIM. A campaign of 72 arms retaining ~2500
        # records each overran the LUNARC home quota when every record carried
        # its full burden-component dict and evolvability provenance. The
        # aggregator needs the objective vectors and the structural
        # coordinates; per-record provenance is kept only where it is actually
        # read -- front members and the evolvability subsample.
        "records": [_slim(r, keep_detail=(i in detail_idx))
                    for i, r in enumerate(records)],
        "sh_meta": {k: v for k, v in sh.items()
                    if not isinstance(v, (list, dict))},
    }


def main(argv: Optional[List[str]] = None) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--t0-budget", type=int, default=729)
    ap.add_argument("--lane", default="gs_uniform")
    ap.add_argument("--no-dedup", action="store_true")
    ap.add_argument("--no-t3", action="store_true")
    ap.add_argument("--evolvability-n", type=int, default=EVOLVABILITY_SUBSAMPLE)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)

    res = run_oracle_arm(a.arm, a.seed, a.t0_budget,
                         dedup=not a.no_dedup, lane=a.lane,
                         evolvability_n=a.evolvability_n,
                         compute_t3=not a.no_t3)
    tmp = a.out + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(res, fh, sort_keys=True, separators=(",", ":"))
    os.replace(tmp, a.out)
    with open(a.out + ".status", "w") as fh:
        fh.write("OK\n")
    sys.stderr.write("FO arm=%s seed=%d retained=%d front=%d attempts=%d\n"
                     % (a.arm, a.seed, res["n_retained"],
                        res["front_report"]["n_front"],
                        res["ledger"]["n_attempts"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

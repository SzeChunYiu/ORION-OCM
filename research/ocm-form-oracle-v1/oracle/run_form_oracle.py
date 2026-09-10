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

# Frozen sampling lanes, reused from the zoo's legality-bounded sampler.
LANES = ("gs_uniform", "lane_units", "lane_hetero", "lane_fields", "lane_ops")

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
    with _charging_proxy(ledger):
        sh = run_successive_halving(t0_budget=t0_budget, seed=seed,
                                    sampler=sampler)

    survivors: List[Dict[str, Any]] = list(sh.get("t2_survivors")
                                           or sh.get("survivors") or [])

    # ---- behavioural dedup on the T2 survivors (cost measured separately)
    kept: List[Dict[str, Any]] = []
    for rec in survivors:
        ev = (rec.get("evaluation") or {})
        gates = (rec.get("gates") or {})
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
        ev = (rec.get("evaluation") or {})
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
        records.append(out)

    crash_settle = ledger.settle()
    front_search = OB.pareto_front_k(records, "search_objectives",
                                     OB.SEARCH_MAXIMIZE)
    front_report = OB.pareto_front_k(records, "report_objectives",
                                     OB.REPORT_MAXIMIZE)

    elapsed = time.time() - t_start
    cpu_h = elapsed / 3600.0
    return {
        "study": "FORM_ORACLE_V1",
        "arm": arm, "seed": seed, "lane": lane, "dedup": dedup,
        "t0_budget": t0_budget,
        "n_survivors_pre_dedup": len(survivors),
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
        "morphologies_per_cpu_hour": (round(len(kept) / cpu_h, 2)
                                      if cpu_h > 0 else None),
        "attempts_per_cpu_hour": (round(ledger.n_attempts / cpu_h, 2)
                                  if cpu_h > 0 else None),
        "distinct_t2_viable": len(kept),
        "memoisation_caveat": (
            "evaluate_genome memoises on (phenotype_digest, tier); a repeated "
            "phenotype costs ~0 wall clock but is charged its full modelled "
            "work. Wall-clock rates are therefore optimistic relative to "
            "charged work and are only comparable at matched budget."),
        "records": records,
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

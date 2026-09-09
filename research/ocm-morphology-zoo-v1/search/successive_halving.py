"""GS successive halving over evaluation tiers (#221 sec 18 GS-R0, P15
parent): T0 -> T1 -> T2 with eta=3 halving and a FROZEN late-bloomer
insurance fraction promoted regardless of rank.

Contract
--------
* Promotion among VIABLE candidates only (hard admissibility first); the
  ranking applied to viable candidates is supplied by the arm — novelty
  for GSA1-GSA4, surrogate for GSA5, dev_score only where an arm's frozen
  protocol demands it (GSR control uses random rank).  Promotion is on
  feasibility + diversity, never mean score alone (P15).
* Late-bloomer insurance: ceil(insurance_fraction * promote_n) extra
  candidates promoted by rank among viable-but-unranked — frozen at 0.15.
* Every sampled genome is charged its T0 evaluation; every promotion is
  charged its higher-tier evaluation; failures ledgered (failure_memory).
* Tier definitions: T0 = evaluate_genome (V1 exact micro-worlds);
  T1 = evaluation.gs_t1.evaluate_t1 (GS definition, frozen);
  T2 = evaluate_genome tier "T2" (developmental lifetime + reset control).
"""
from __future__ import annotations

import math
import random
import time
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from evaluation.evaluate import evaluate_genome
from search.failure_memory import append_failure, stage_attribution

# Frozen defaults (embedded in GRAND_SEARCH_R1_FREEZE.json by freeze_gs.py)
GS_ETA = 3
GS_RUNGS: Tuple[str, ...] = ("T0", "T1", "T2")
GS_LATE_BLOOMER_FRACTION = 0.15
GS_MIN_PROMOTE = 3


def halving_counts(n0: int, eta: int = GS_ETA,
                   rungs: Sequence[str] = GS_RUNGS) -> List[int]:
    """Candidates evaluated at each rung for one round: n0, n0/eta, ..."""
    out = []
    n = n0
    for _ in rungs:
        out.append(max(1, n))
        n = n // eta
    return out


def promote(viable: List[Dict[str, Any]], promote_n: int,
            rank_fn: Callable[[Dict[str, Any]], float],
            insurance_fraction: float = GS_LATE_BLOOMER_FRACTION,
            rng: Optional[random.Random] = None) -> Dict[str, Any]:
    """Rank-based promotion + frozen late-bloomer insurance.

    Returns {"ranked": [...], "insurance": [...]} — both promoted.  `ranked`
    is the top promote_n by rank_fn (higher = better).  `insurance` is
    ceil(insurance_fraction*promote_n) further candidates taken by rank
    among the REMAINDER (novelty-biased when rank_fn is novelty; random
    tie-shuffle otherwise)."""
    rng = rng or random.Random(0)
    rest = list(viable)
    rng.shuffle(rest)  # deterministic tie order
    ordered = sorted(rest, key=lambda r: -float(rank_fn(r)))
    n_rank = max(1, min(promote_n, len(ordered)))
    ranked = ordered[:n_rank]
    remainder = ordered[n_rank:]
    n_ins = min(len(remainder),
                math.ceil(insurance_fraction * max(1, promote_n)))
    insurance = remainder[:n_ins]  # highest-ranked remainder = rank-biased
    return {"ranked": ranked, "insurance": insurance}


def _eval_tier(g, tier: str) -> Dict[str, Any]:
    """Tier dispatch with automatic failure-ledger append on failure."""
    from morphology.gs_bound import grammar_signature
    try:
        if tier == "T0":
            r = evaluate_genome(g, tier="T0")
        elif tier == "T1":
            from evaluation.gs_t1 import evaluate_t1
            r = evaluate_t1(g)
        elif tier == "T2":
            r = evaluate_genome(g, tier="T2")
        else:
            raise ValueError("unknown tier %r" % tier)
    except Exception as e:
        append_failure({
            "candidate_id": g.digest(), "tier": tier, "stage": "tier_eval",
            "counterexample": "exception:%s" % repr(e)[:180],
            "grammar_signature": grammar_signature(g)})
        raise
    if not r["feasible"]:
        att = stage_attribution(r)
        append_failure({
            "candidate_id": r["genotype_digest"], "tier": tier,
            "stage": att["stage"], "counterexample": att["counterexample"],
            "grammar_signature": grammar_signature(g),
            "gates": {k: v for k, v in r["gates"].items()
                      if isinstance(v, bool) and v is False}})
    return r


def run_successive_halving(
        t0_budget: int = 729, seed: int = 0,
        sampler: Optional[Callable[[random.Random], Any]] = None,
        parent_pool: Optional[List[Dict[str, Any]]] = None,
        rank_fn: Optional[Callable[[Dict[str, Any]], float]] = None,
        eta: int = GS_ETA,
        insurance_fraction: float = GS_LATE_BLOOMER_FRACTION,
        n0: Optional[int] = None,
        pop_size: int = 48,
        wall_deadline: Optional[float] = None,
        rank_prepare: Optional[Callable[[List[Dict[str, Any]]], None]] = None,
        on_round_end: Optional[Callable[..., None]] = None,
        on_progress: Optional[Callable[[Dict[str, Any]], None]] = None
        ) -> Dict[str, Any]:
    """Rounds of T0 sampling -> eta-halving promotions to T1 -> T2.

    sampler(rng) yields genomes (lane or uniform).  parent_pool, when
    non-empty and rng.random() < 0.8, supplies mutated/crossover children
    instead (drives the novelty arms).  rank_fn ranks VIABLE records for
    promotion (novelty / surrogate / dev_score / random per arm protocol).
    wall_deadline (unix seconds) stops between rounds — honest partials.
    rank_prepare(viable_records) is called before each promotion selection
    so the arm can compute order-independent rank keys for the whole cohort
    (novelty vs archive+cohort pool; surrogate allocation scores).
    on_round_end(round_id, t0_records, t1_records, t2_records) is called at
    the end of each round (surrogate retraining on completed evals only).
    """
    from morphology.direct_genome import random_genome
    from morphology.mutations import crossover, mutate

    rng = random.Random(seed)
    if rank_fn is None:
        rank_fn = lambda r: rng.random()  # noqa: E731  (random-rank control)
    draw = sampler or (lambda r: random_genome(r))

    def _genome_of(rec):
        from morphology.schema import OCMMorphologyGenomeV1
        return OCMMorphologyGenomeV1.from_json_obj(rec["genome"])

    counts = {t: 0 for t in GS_RUNGS}
    viable_counts = {t: 0 for t in GS_RUNGS}
    survivors: List[Dict[str, Any]] = []
    failures_t1_t2 = 0
    t_start = time.time()
    rounds = 0

    while counts["T0"] < t0_budget:
        if wall_deadline is not None and time.time() > wall_deadline:
            break
        this_n0 = n0 or 729
        this_n0 = min(this_n0, t0_budget - counts["T0"])
        round_id = rounds
        rounds += 1
        # ---- T0 cohort
        cohort: List[Any] = []
        for _ in range(this_n0):
            if parent_pool and rng.random() < 0.8:
                parent = _genome_of(rng.choice(parent_pool))
                if rng.random() < 0.3 and len(parent_pool) > 1:
                    other = _genome_of(rng.choice(parent_pool))
                    cohort.append(crossover(parent, other, rng))
                else:
                    cohort.append(mutate(parent, rng))
            else:
                cohort.append(draw(rng))
        t0_records: List[Dict[str, Any]] = []
        for g in cohort:
            try:
                r = _eval_tier(g, "T0")
            except Exception:
                counts["T0"] += 1
                continue  # crash retained in ledger; charged as attempted
            counts["T0"] += 1
            rec = {"genotype_digest": r["genotype_digest"],
                   "phenotype_digest": r["phenotype_digest"],
                   "genome": g.to_json_obj(), "n_units": len(g.U),
                   "gates": r["gates"], "feasible": bool(r["feasible"]),
                   "evaluation": r["evaluation"], "round": round_id}
            t0_records.append(rec)
            if rec["feasible"]:
                viable_counts["T0"] += 1
        viable = [r for r in t0_records if r["feasible"]]
        # ---- promote n0/eta to T1
        if rank_prepare is not None and viable:
            rank_prepare(viable)
        n_t1 = max(GS_MIN_PROMOTE, this_n0 // eta)
        sel = promote(viable, n_t1, rank_fn, insurance_fraction, rng)
        t1_pool = sel["ranked"] + sel["insurance"]
        t1_viable: List[Dict[str, Any]] = []
        t1_records: List[Dict[str, Any]] = []
        for rec in t1_pool:
            try:
                r1 = _eval_tier(_genome_of(rec), "T1")
            except Exception:
                counts["T1"] += 1
                failures_t1_t2 += 1
                continue
            counts["T1"] += 1
            rec2 = dict(rec)
            rec2["t1"] = {"feasible": bool(r1["feasible"]),
                          "gates": r1["gates"],
                          "evaluation": r1["evaluation"]}
            if r1["feasible"]:
                viable_counts["T1"] += 1
                t1_viable.append(rec2)
            t1_records.append(rec2)
        # ---- promote n_t1/eta to T2
        if rank_prepare is not None and t1_viable:
            rank_prepare(t1_viable)
        n_t2 = max(GS_MIN_PROMOTE, n_t1 // eta)
        sel2 = promote(t1_viable, n_t2, rank_fn, insurance_fraction, rng)
        t2_pool = sel2["ranked"] + sel2["insurance"]
        for rec in t2_pool:
            try:
                r2 = _eval_tier(_genome_of(rec), "T2")
            except Exception:
                counts["T2"] += 1
                failures_t1_t2 += 1
                continue
            counts["T2"] += 1
            rec3 = dict(rec)
            rec3["t2"] = {"feasible": bool(r2["feasible"]),
                          "gates": r2["gates"],
                          "evaluation": r2["evaluation"]}
            if r2["feasible"]:
                viable_counts["T2"] += 1
                survivors.append(rec3)
        # ---- parent pool refresh (novelty arms keep the archive's best)
        if viable:
            keep = max(2, pop_size // 3)
            parent_pool = sorted(
                viable, key=lambda r: -float(rank_fn(r)))[:keep] or parent_pool
        if on_round_end is not None:
            t2_recs = [r for r in survivors if r.get("round") == round_id]
            on_round_end(round_id, t0_records, t1_records, t2_recs)
        if on_progress is not None:  # GS-R1h hourly honest partials
            on_progress({
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "round": round_id, "counts": dict(counts),
                "viable_counts": dict(viable_counts),
                "n_survivors": len(survivors),
                "elapsed_s": round(time.time() - t_start, 3),
                "cpu_s": round(time.process_time(), 3)})

    return {
        "algorithm": "GS_successive_halving", "eta": eta,
        "insurance_fraction": insurance_fraction,
        "rounds": rounds, "counts": counts, "viable_counts": viable_counts,
        "t1_t2_eval_failures": failures_t1_t2,
        "survivors": survivors,
        "elapsed_s": round(time.time() - t_start, 3),
    }

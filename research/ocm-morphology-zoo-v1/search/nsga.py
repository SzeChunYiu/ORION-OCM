"""P02 NSGA-II (Deb et al. 2002; via L19 context) — explicit multi-objective
evolution parent.  Tests whether explicit QD adds value beyond ordinary
multi-objective diversity (#221 sec 7 P02).  Stdlib implementation.
"""
from __future__ import annotations

import random
import time
from typing import Any, Dict, List

from evaluation.objectives import OBJECTIVE_NAMES, dominates
from morphology.direct_genome import random_genome
from morphology.mutations import mutate, crossover
from morphology.schema import OCMMorphologyGenomeV1
from search.map_elites import evaluate_record


def fast_non_dominated_sort(recs: List[Dict[str, Any]]) -> List[List[int]]:
    n = len(recs)
    S = [[] for _ in range(n)]
    rank = [0] * n
    fronts: List[List[int]] = [[]]
    for p in range(n):
        for q in range(n):
            if p == q:
                continue
            if dominates(recs[p]["objectives"], recs[q]["objectives"]):
                S[p].append(q)
            elif dominates(recs[q]["objectives"], recs[p]["objectives"]):
                rank[p] += 1  # count of dominators (cheap domination count)
    first = [p for p in range(n) if rank[p] == 0]
    fronts.append(first)
    remaining = set(range(n)) - set(first)
    while remaining:
        # Peel: among remaining, those not dominated by any other remaining
        nxt = [p for p in remaining
               if not any(q in remaining and q != p and
                          dominates(recs[q]["objectives"], recs[p]["objectives"])
                          for q in list(remaining))]
        if not nxt:  # safety: cycles cannot happen with strict dominance
            nxt = list(remaining)
        fronts.append(nxt)
        remaining -= set(nxt)
    return [f for f in fronts if f]


def crowding_distance(recs: List[Dict[str, Any]], idxs: List[int]) -> Dict[int, float]:
    dist = {i: 0.0 for i in idxs}
    for oi, name in enumerate(OBJECTIVE_NAMES):
        order = sorted(idxs, key=lambda i: recs[i]["objectives"][oi])
        if len(order) < 3:
            for i in order:
                dist[i] = float("inf")
            continue
        dist[order[0]] = dist[order[-1]] = float("inf")
        span = (recs[order[-1]]["objectives"][oi] - recs[order[0]]["objectives"][oi]) or 1.0
        for a in range(1, len(order) - 1):
            dist[order[a]] += (recs[order[a + 1]]["objectives"][oi]
                               - recs[order[a - 1]]["objectives"][oi]) / span
    return dist


def run(budget: int = 4000, seed: int = 0, pop_size: int = 100,
        start_from=None) -> Dict[str, Any]:
    rng = random.Random(seed)
    t0 = time.time()
    n_evals = 0
    n_feasible = 0
    population: List[Dict[str, Any]] = []
    kept: Dict[str, Dict[str, Any]] = {}
    # init
    while len(population) < pop_size and n_evals < budget:
        g = start_from.clone() if (start_from is not None and not population) else random_genome(rng)
        r = evaluate_record(g, "S_structural_2d")
        n_evals += 1
        if r["feasible"]:
            n_feasible += 1
            population.append(r)
            kept[r["phenotype_digest"]] = r
        else:
            population.append(r)  # infeasible compete with worst objectives
    while n_evals < budget:
        # binary tournament on (rank via dominance in current pop, crowding)
        def better(a, b):
            # feasible dominates infeasible; then objective dominance; then random
            if a["feasible"] != b["feasible"]:
                return a if a["feasible"] else b
            if dominates(a["objectives"], b["objectives"]):
                return a
            if dominates(b["objectives"], a["objectives"]):
                return b
            return a if rng.random() < 0.5 else b

        children = []
        while len(children) < pop_size and n_evals < budget:
            a = better(rng.choice(population), rng.choice(population))
            b = better(rng.choice(population), rng.choice(population))
            ga = OCMMorphologyGenomeV1.from_json_obj(a["genome"])
            gb = OCMMorphologyGenomeV1.from_json_obj(b["genome"])
            child = mutate(crossover(ga, gb, rng), rng, p_struct=0.5, p_theta=0.5)
            r = evaluate_record(child, "S_structural_2d")
            n_evals += 1
            if r["feasible"]:
                n_feasible += 1
                kept[r["phenotype_digest"]] = r
            children.append(r)
        union = population + children
        fronts = fast_non_dominated_sort([
            dict(u, objectives=([u["objectives"][0]] + [1e9] * 9)
                 if not u["feasible"] else u["objectives"]) for u in union])
        newpop: List[Dict[str, Any]] = []
        for f in fronts:
            if len(newpop) + len(f) > pop_size:
                cd = crowding_distance(union, f)
                f = sorted(f, key=lambda i: -cd[i])[: pop_size - len(newpop)]
            newpop.extend(union[i] for i in f)
            if len(newpop) >= pop_size:
                break
        population = newpop[:pop_size]
    feasible_pop = [p for p in population if p["feasible"]]
    return {
        "algorithm": "P02_nsga2", "seed": seed, "evals": n_evals,
        "elapsed_s": round(time.time() - t0, 3), "feasible_found": n_feasible,
        "final_feasible_pop": len(feasible_pop),
        "unique_feasible_phenotypes": len(kept),
        "best_dev_score": max((r["dev_score"] for r in kept.values()), default=None),
        "archive": [{kk: r[kk] for kk in
                     ("genotype_digest", "phenotype_digest", "genome", "objectives",
                      "dev_score", "descriptors")} for r in kept.values()],
    }

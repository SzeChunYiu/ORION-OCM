"""P01 uniform random search — mandatory baseline (Mouret&Clune parent L01 context).

Same evaluation budget as every arm; returns the feasible non-dominated set
plus full evaluation records for downstream metrics.
"""
from __future__ import annotations

import random
import time
from typing import Any, Dict, List

from evaluation.evaluate import evaluate_genome
from evaluation.objectives import dev_score, dominates, pareto_front
from morphology.direct_genome import random_genome
from morphology.mutations import mutate


def run(budget: int = 4000, seed: int = 0, start_from=None,
        archive_dims: str = "S_structural_2d", sampler=None) -> Dict[str, Any]:
    rng = random.Random(seed)
    t0 = time.time()
    population: List[Dict[str, Any]] = []
    n_feasible = 0
    for i in range(budget):
        g = mutate(start_from, rng) if (start_from is not None and rng.random() < 0.5) \
            else (sampler(rng) if sampler else random_genome(rng))
        r = evaluate_genome(g)
        if not r["feasible"]:
            continue
        n_feasible += 1
        population.append({
            "genotype_digest": r["genotype_digest"],
            "phenotype_digest": r["phenotype_digest"],
            "genome": g.to_json_obj(),
            "objectives": r["evaluation"].get("objectives") or _obj(r),
            "dev_score": dev_score(r["evaluation"]),
            "evaluation": r["evaluation"],
        })
    front_idx = pareto_front(population)
    archive = [population[i] for i in front_idx]
    # collapse exact phenotype duplicates, keep best dev_score
    best: Dict[str, Dict[str, Any]] = {}
    for it in population:
        k = it["phenotype_digest"]
        if k not in best or it["dev_score"] > best[k]["dev_score"]:
            best[k] = it
    return {
        "algorithm": "P01_random", "seed": seed, "evals": budget,
        "elapsed_s": round(time.time() - t0, 3), "feasible_found": n_feasible,
        "archive": archive,
        "unique_phenotypes": len(best),
        "best_dev_score": max((it["dev_score"] for it in population), default=None),
        "all_feasible": list(best.values()),
    }


def _obj(r: Dict[str, Any]) -> List[float]:
    from evaluation.objectives import objective_vector
    return objective_vector(r["evaluation"])

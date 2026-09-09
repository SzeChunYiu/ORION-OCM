"""P03 Novelty Search (Lehman & Stanley 2011, L04) — behavior-only novelty.

No quality pressure except hard feasibility (gates).  Archive = novel feasible
behaviors; selection by novelty score (mean distance to k nearest in
population + archive).  Tests deceptive stepping-stone value (#221 sec 7 P03).
"""
from __future__ import annotations

import random
import time
from typing import Any, Dict, List, Tuple

from evaluation.descriptors import descriptors_for
from evaluation.evaluate import evaluate_genome
from evaluation.objectives import dev_score, objective_vector
from morphology.compile import compile_genome
from morphology.direct_genome import random_genome
from morphology.mutations import mutate, crossover
from morphology.schema import OCMMorphologyGenomeV1
from search.map_elites import evaluate_record


def _dist(a, b) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def novelty_score(desc, pool: List[Tuple[float, ...]], k: int = 15) -> float:
    if not pool:
        return 0.0
    ds = sorted(_dist(desc, p) for p in pool)
    take = ds[: min(k, len(ds))]
    return sum(take) / len(take)


def run(budget: int = 4000, seed: int = 0, k: int = 15, pop_size: int = 60,
        archive_add_prob: float = 0.15, archive_cap: int = 500,
        behavior_archive: str = "B_behavior_2d", start_from=None) -> Dict[str, Any]:
    rng = random.Random(seed)
    t0 = time.time()
    population: List[Dict[str, Any]] = []
    archive: List[Tuple[float, ...]] = []
    n_evals = 0
    n_feasible = 0
    kept: Dict[str, Dict[str, Any]] = {}
    while n_evals < budget:
        # produce children
        children = []
        for _ in range(min(pop_size, budget - n_evals)):
            if population and rng.random() < 0.8:
                parent = rng.choice(population)
                g1 = OCMMorphologyGenomeV1.from_json_obj(parent["genome"])
                if rng.random() < 0.3 and len(population) > 1:
                    other = rng.choice(population)
                    g2 = OCMMorphologyGenomeV1.from_json_obj(other["genome"])
                    children.append(crossover(g1, g2, rng))
                else:
                    children.append(mutate(g1, rng))
            else:
                children.append(random_genome(rng))
        recs = [evaluate_record(g, behavior_archive) for g in children]
        n_evals += len(recs)
        feas = [r for r in recs if r["feasible"]]
        n_feasible += len(feas)
        for r in feas:
            kept[r["phenotype_digest"]] = r
        # novelty of each child vs (archive + others)
        pool_desc = archive + [tuple(r["descriptors"]) for r in recs]
        scored = [(novelty_score(tuple(r["descriptors"]), pool_desc, k), r)
                  for r in recs]
        scored.sort(key=lambda sr: -sr[0])
        survivors = [r for _, r in scored[: max(2, pop_size // 3)] if r["feasible"]]
        population = (population + survivors)[-pop_size:]
        for sc, r in scored:
            if r["feasible"] and rng.random() < archive_add_prob:
                archive.append(tuple(r["descriptors"]))
        if len(archive) > archive_cap:
            archive = archive[-archive_cap:]
    return {
        "algorithm": "P03_novelty", "seed": seed, "evals": n_evals,
        "elapsed_s": round(time.time() - t0, 3), "feasible_found": n_feasible,
        "n_archive": len(archive),
        "unique_feasible_phenotypes": len(kept),
        "best_dev_score": max((r["dev_score"] for r in kept.values()), default=None),
        "archive": [{kk: r[kk] for kk in
                     ("genotype_digest", "phenotype_digest", "genome", "objectives",
                      "dev_score", "descriptors")} for r in kept.values()],
    }

"""P04 Novelty Search with Local Competition (Pugh/Soros/Stanley, L05).

Fitness = novelty + local competition: rank of dev_score among the k nearest
behavioral neighbors.  Nearest-neighbor archive retained.
"""
from __future__ import annotations

import random
import time
from typing import Any, Dict, List, Tuple

from evaluation.objectives import objective_vector
from morphology.direct_genome import random_genome
from morphology.mutations import mutate, crossover
from morphology.schema import OCMMorphologyGenomeV1
from search.map_elites import evaluate_record
from search.novelty import _dist


def _neighbors(desc, pool, k):
    order = sorted(range(len(pool)), key=lambda i: _dist(desc, pool[i][0]))
    return [pool[i] for i in order[:k]]


def run(budget: int = 4000, seed: int = 0, k: int = 15, pop_size: int = 60,
        archive_cap: int = 500, behavior_archive: str = "B_behavior_2d",
        start_from=None) -> Dict[str, Any]:
    rng = random.Random(seed)
    t0 = time.time()
    population: List[Dict[str, Any]] = []
    # archive entries: (desc, dev_score, record)
    archive: List[Tuple[Tuple[float, ...], float, Dict[str, Any]]] = []
    n_evals = 0
    n_feasible = 0
    kept: Dict[str, Dict[str, Any]] = {}
    while n_evals < budget:
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
        pool = [(tuple(r["descriptors"]), r["dev_score"], r) for r in feas] + archive
        # local competition: rank among k nearest by dev_score
        scored = []
        for r in recs:
            if not r["feasible"]:
                scored.append((-1e9, r))
                continue
            nbrs = _neighbors(tuple(r["descriptors"]), pool, k)
            rank = sum(1 for _, s, _ in nbrs if s > r["dev_score"])
            novelty = sum(_dist(tuple(r["descriptors"]), d) for d, _, _ in nbrs) / max(1, len(nbrs))
            scored.append((novelty - rank, r))
        scored.sort(key=lambda sr: -sr[0])
        survivors = [r for s, r in scored[: max(2, pop_size // 3)] if r["feasible"]]
        population = (population + survivors)[-pop_size:]
        for s, r in scored:
            if r["feasible"] and rng.random() < 0.2:
                archive.append((tuple(r["descriptors"]), r["dev_score"], r))
        if len(archive) > archive_cap:
            archive = archive[-archive_cap:]
    return {
        "algorithm": "P04_nslc", "seed": seed, "evals": n_evals,
        "elapsed_s": round(time.time() - t0, 3), "feasible_found": n_feasible,
        "n_archive": len(archive),
        "unique_feasible_phenotypes": len(kept),
        "best_dev_score": max((r["dev_score"] for r in kept.values()), default=None),
        "archive": [{kk: r[kk] for kk in
                     ("genotype_digest", "phenotype_digest", "genome", "objectives",
                      "dev_score", "descriptors")} for r in kept.values()],
    }

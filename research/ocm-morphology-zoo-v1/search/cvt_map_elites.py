"""P06 CVT-MAP-Elites (Vassiliades & Mouret, L06) — 5-10D descriptors, fixed size.

Deterministic k-means over seeded samples from the descriptor space; niche =
nearest centroid; archive size fixed at k regardless of dimension.
"""
from __future__ import annotations

import math
import random
import time
from typing import Any, Dict, List, Tuple

from evaluation.descriptors import DESCRIPTOR_REGISTRY, descriptors_for
from evaluation.evaluate import evaluate_genome
from evaluation.objectives import dev_score, objective_vector
from morphology.compile import compile_genome
from morphology.direct_genome import random_genome
from morphology.mutations import mutate, crossover
from morphology.schema import OCMMorphologyGenomeV1
from search.map_elites import evaluate_record


def _kmeans(data: List[Tuple[float, ...]], k: int, iters: int = 20,
            rng: random.Random = None) -> List[Tuple[float, ...]]:
    rng = rng or random.Random(0)
    cents = [data[i] for i in rng.sample(range(len(data)), k)]
    for _ in range(iters):
        assign = []
        for p in data:
            j = min(range(k), key=lambda c: _dist(p, cents[c]))
            assign.append(j)
        new = []
        for c in range(k):
            members = [p for p, a in zip(data, assign) if a == c]
            if members:
                new.append(tuple(sum(m[d] for m in members) / len(members)
                                 for d in range(len(members[0]))))
            else:
                new.append(cents[c])
        if new == cents:
            break
        cents = new
    return cents


def _dist(a: Tuple[float, ...], b: Tuple[float, ...]) -> float:
    s = 0.0
    for x, y in zip(a, b):
        s += (x - y) ** 2
    return s


class CVTArchive:
    def __init__(self, centroids: List[Tuple[float, ...]]) -> None:
        self.centroids = centroids
        self.cells: Dict[int, Dict[str, Any]] = {}

    def niche(self, desc: Tuple[float, ...]) -> int:
        return min(range(len(self.centroids)),
                   key=lambda c: _dist(desc, self.centroids[c]))

    def try_insert(self, rec: Dict[str, Any]) -> bool:
        if not rec["feasible"]:
            return False
        idx = self.niche(tuple(rec["descriptors"]))
        cur = self.cells.get(idx)
        if cur is None or rec["dev_score"] > cur["dev_score"]:
            self.cells[idx] = rec
            return True
        return False

    def coverage(self) -> float:
        return len(self.cells) / len(self.centroids)

    def elites(self) -> List[Dict[str, Any]]:
        return list(self.cells.values())

    def qd_score(self) -> float:
        return sum(e["dev_score"] for e in self.cells.values())


def run(budget: int = 4000, seed: int = 0, archive: str = "S_cvtd", k: int = 64,
        init_fraction: float = 0.2, start_from=None) -> Dict[str, Any]:
    rng = random.Random(seed)
    t0 = time.time()
    # sample descriptor space to build centroids (deterministic, charged to budget)
    samples = []
    n_sample = min(budget - 1, 500)
    sample_recs = []
    for _ in range(n_sample):
        g = start_from.clone() if start_from is not None else random_genome(rng)
        rec = evaluate_record(g, archive)
        sample_recs.append(rec)
        samples.append(tuple(rec["descriptors"]))
    cents = _kmeans(samples, k, rng=rng)
    arch = CVTArchive(cents)
    # initial random phase: sampled evaluations are real work and fill cells
    for rec in sample_recs:
        arch.try_insert(rec)
    n_evals = len(samples)
    n_feasible = sum(1 for r in sample_recs if r["feasible"])
    batch = []
    while n_evals < budget:
        if not batch:
            if not arch.cells:
                batch = [random_genome(rng)]
            else:
                elites = arch.elites()
                for _ in range(10):
                    if rng.random() < 0.5 or len(elites) == 1:
                        g1 = OCMMorphologyGenomeV1.from_json_obj(rng.choice(elites)["genome"])
                        batch.append(mutate(g1, rng))
                    else:
                        a = OCMMorphologyGenomeV1.from_json_obj(rng.choice(elites)["genome"])
                        b = OCMMorphologyGenomeV1.from_json_obj(rng.choice(elites)["genome"])
                        batch.append(crossover(a, b, rng))
                    if len(batch) >= 10:
                        break
        g = batch.pop()
        rec = evaluate_record(g, archive)
        n_evals += 1
        if rec["feasible"]:
            n_feasible += 1
        arch.try_insert(rec)
    return {
        "algorithm": "P06_cvt_map_elites", "seed": seed, "evals": n_evals,
        "archive_name": archive, "k": k,
        "elapsed_s": round(time.time() - t0, 3), "feasible_found": n_feasible,
        "coverage": round(arch.coverage(), 6), "qd_score": round(arch.qd_score(), 6),
        "n_elites": len(arch.elites()),
        "best_dev_score": max((e["dev_score"] for e in arch.elites()), default=None),
        "archive": [{kk: e[kk] for kk in
                     ("genotype_digest", "phenotype_digest", "genome", "objectives",
                      "dev_score", "descriptors")} for e in arch.elites()],
    }

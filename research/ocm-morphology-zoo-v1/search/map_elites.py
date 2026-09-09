"""P05 vanilla MAP-Elites (Mouret & Clune 2015, L01) + shared grid machinery.

Grid archive over registered descriptor axes; one elite per cell by frozen
scalar dev_score; feasibility (hard gates) required for admission.
"""
from __future__ import annotations

import random
import time
from typing import Any, Dict, List, Tuple

from evaluation.descriptors import DESCRIPTOR_REGISTRY, descriptors_for
from evaluation.evaluate import evaluate_genome
from evaluation.objectives import dev_score, objective_vector
from morphology.compile import compile_genome
from morphology.direct_genome import random_genome
from morphology.mutations import mutate, crossover


def grid_indices(desc: Tuple[float, ...], bounds, res: int = 10) -> Tuple[int, ...]:
    out = []
    for d, b in zip(desc, bounds):
        lo, hi = b
        out.append(min(res - 1, max(0, int((d - lo) / (hi - lo + 1e-12) * res))))
    return tuple(out)


def evaluate_record(g, archive: str) -> Dict[str, Any]:
    r = evaluate_genome(g)
    org = compile_genome(g)
    return {
        "genotype_digest": r["genotype_digest"],
        "phenotype_digest": r["phenotype_digest"],
        "genome": g.to_json_obj(),
        "objectives": objective_vector(r["evaluation"]),
        "dev_score": dev_score(r["evaluation"]),
        "descriptors": descriptors_for(org, r["evaluation"], archive),
        "evaluation": r["evaluation"],
        "feasible": r["feasible"],
    }


class GridArchive:
    def __init__(self, registry_name: str, res: int = 10) -> None:
        self.reg = DESCRIPTOR_REGISTRY[registry_name]
        self.res = res
        self.cells: Dict[Tuple[int, ...], Dict[str, Any]] = {}

    def try_insert(self, rec: Dict[str, Any]) -> bool:
        if not rec["feasible"]:
            return False
        idx = grid_indices(tuple(rec["descriptors"]), self.reg["bounds"], self.res)
        cur = self.cells.get(idx)
        if cur is None or rec["dev_score"] > cur["dev_score"]:
            self.cells[idx] = rec
            return True
        return False

    def coverage(self) -> float:
        return len(self.cells) / (self.res ** len(self.reg["dims"]))

    def elites(self) -> List[Dict[str, Any]]:
        return list(self.cells.values())

    def qd_score(self) -> float:
        return sum(e["dev_score"] for e in self.cells.values())


def run(budget: int = 4000, seed: int = 0, init_fraction: float = 0.2,
        archive: str = "S_structural_2d", res: int = 10, start_from=None,
        sampler=None, mutator=None, crossover_fn=None) -> Dict[str, Any]:
    """Standard MAP-Elites loop: random init, then mutation/crossover elites.

    Optional encoding hooks (FREEZE_V1_AMEND_2, E1-CGP arms): sampler(rng)
    replaces random_genome, mutator(g, rng) replaces mutate, crossover_fn(a,
    b, rng) replaces crossover.  With all None the loop is byte-identical to
    the pre-amendment behaviour (RNG consumption order unchanged)."""
    rng = random.Random(seed)
    t0 = time.time()
    arch = GridArchive(archive, res)
    n_init = max(1, int(budget * init_fraction))
    n_evals = 0
    n_feasible = 0
    batch = []
    for _ in range(n_init):
        g = start_from.clone() if start_from is not None else (
            sampler(rng) if sampler else random_genome(rng))
        batch.append(g)
    while n_evals < budget:
        if not batch:
            if not arch.cells:
                batch = [sampler(rng) if sampler else random_genome(rng)]
            else:
                elites = arch.elites()
                for _ in range(10):
                    # branch condition MUST stay identical to the pre-amend-2
                    # loop: adding "or crossover_fn is None" here suppressed
                    # crossover for hook-less (E0) arms and broke E0==amend-1
                    # reproducibility (caught by the QDA2-vs-QDA1 xcheck)
                    if rng.random() < 0.5 or len(elites) == 1:
                        g1 = _genome_of(rng.choice(elites), rng)
                        batch.append(mutator(g1, rng) if mutator else mutate(g1, rng))
                    else:
                        a = _genome_of(rng.choice(elites), rng)
                        b = _genome_of(rng.choice(elites), rng)
                        batch.append(crossover_fn(a, b, rng) if crossover_fn
                                     else crossover(a, b, rng))
                    if len(batch) >= 10:
                        break
        g = batch.pop()
        rec = evaluate_record(g, archive)
        n_evals += 1
        if rec["feasible"]:
            n_feasible += 1
        arch.try_insert(rec)
    return {
        "algorithm": "P05_map_elites", "seed": seed, "evals": n_evals,
        "archive_name": archive, "resolution": res,
        "elapsed_s": round(time.time() - t0, 3), "feasible_found": n_feasible,
        "coverage": round(arch.coverage(), 6), "qd_score": round(arch.qd_score(), 6),
        "n_elites": len(arch.elites()),
        "best_dev_score": max((e["dev_score"] for e in arch.elites()), default=None),
        "archive": [{k: e[k] for k in
                     ("genotype_digest", "phenotype_digest", "genome", "objectives",
                      "dev_score", "descriptors")} for e in arch.elites()],
    }


def _genome_of(rec: Dict[str, Any], rng: random.Random):
    from morphology.schema import OCMMorphologyGenomeV1
    return OCMMorphologyGenomeV1.from_json_obj(rec["genome"])

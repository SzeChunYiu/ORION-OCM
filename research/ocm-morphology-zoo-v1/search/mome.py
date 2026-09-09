"""P07 MOME (Multi-Objective MAP-Elites, L09) — Pareto front per niche.

Preferred main scientific archive when objectives conflict (#221 sec 6).
Niche = grid cell over registered descriptor axes; each cell holds its local
non-dominated set (capped), reported with per-niche hypervolume-style extent.
"""
from __future__ import annotations

import random
import time
from typing import Any, Dict, List, Tuple

from evaluation.descriptors import DESCRIPTOR_REGISTRY, descriptors_for
from evaluation.objectives import OBJECTIVE_NAMES, dominates, objective_vector
from evaluation.evaluate import evaluate_genome
from morphology.compile import compile_genome
from morphology.direct_genome import random_genome
from morphology.mutations import mutate, crossover
from morphology.schema import OCMMorphologyGenomeV1
from search.map_elites import evaluate_record, grid_indices


class MOMEArchive:
    def __init__(self, registry_name: str, res: int = 8,
                 cell_cap: int = 8) -> None:
        self.reg = DESCRIPTOR_REGISTRY[registry_name]
        self.res = res
        self.cell_cap = cell_cap
        self.cells: Dict[Tuple[int, ...], List[Dict[str, Any]]] = {}

    def try_insert(self, rec: Dict[str, Any]) -> bool:
        if not rec["feasible"]:
            return False
        idx = grid_indices(tuple(rec["descriptors"]), self.reg["bounds"], self.res)
        cell = self.cells.setdefault(idx, [])
        for other in cell:
            if dominates(other["objectives"], rec["objectives"]):
                return False
        cell[:] = [o for o in cell
                   if not dominates(rec["objectives"], o["objectives"])]
        cell.append(rec)
        if len(cell) > self.cell_cap:
            cell.sort(key=lambda r: -r["objectives"][OBJECTIVE_NAMES.index("capability")])
            cell[:] = cell[: self.cell_cap]
        return True

    def all_elites(self) -> List[Dict[str, Any]]:
        return [e for cell in self.cells.values() for e in cell]

    def occupied_cells(self) -> int:
        return len(self.cells)

    def per_cell_extent(self) -> List[float]:
        """Proxy for per-niche Pareto extent: spread of capability x (-cost)."""
        out = []
        for cell in self.cells.values():
            caps = [e["objectives"][0] for e in cell]
            costs = [e["objectives"][1] + e["objectives"][4] for e in cell]
            out.append(round((max(caps) - min(caps)) + (max(costs) - min(costs)) / 2, 6))
        return out


def run(budget: int = 4000, seed: int = 0, archive: str = "S_structural_2d",
        res: int = 8, cell_cap: int = 8, init_fraction: float = 0.2,
        start_from=None) -> Dict[str, Any]:
    rng = random.Random(seed)
    t0 = time.time()
    arch = MOMEArchive(archive, res, cell_cap)
    n_init = max(1, int(budget * init_fraction))
    n_evals = 0
    n_feasible = 0
    batch = [start_from.clone() if start_from is not None else random_genome(rng)
             for _ in range(n_init)]
    while n_evals < budget:
        if not batch:
            if not arch.cells:
                batch = [random_genome(rng)]
            else:
                pool = arch.all_elites()
                for _ in range(10):
                    if rng.random() < 0.5 or len(pool) == 1:
                        g1 = OCMMorphologyGenomeV1.from_json_obj(rng.choice(pool)["genome"])
                        batch.append(mutate(g1, rng))
                    else:
                        a = OCMMorphologyGenomeV1.from_json_obj(rng.choice(pool)["genome"])
                        b = OCMMorphologyGenomeV1.from_json_obj(rng.choice(pool)["genome"])
                        batch.append(crossover(a, b, rng))
                    if len(batch) >= 10:
                        break
        g = batch.pop()
        rec = evaluate_record(g, archive)
        n_evals += 1
        if rec["feasible"]:
            n_feasible += 1
        arch.try_insert(rec)
    elites = arch.all_elites()
    return {
        "algorithm": "P07_mome", "seed": seed, "evals": n_evals,
        "archive_name": archive, "resolution": res, "cell_cap": cell_cap,
        "elapsed_s": round(time.time() - t0, 3), "feasible_found": n_feasible,
        "occupied_cells": arch.occupied_cells(),
        "n_elites": len(elites),
        "per_cell_extent": arch.per_cell_extent(),
        "best_dev_score": max((e["dev_score"] for e in elites), default=None),
        "archive": [{k: e[k] for k in
                     ("genotype_digest", "phenotype_digest", "genome", "objectives",
                      "dev_score", "descriptors")} for e in elites],
    }

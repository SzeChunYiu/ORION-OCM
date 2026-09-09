"""P11 lexicase / epsilon-lexicase selection (Helmuth et al., L15).

Task cases are selection axes: each world-family task (and each objective)
is a case; parents are selected by filtering on randomly ordered cases.
Preserves specialists that aggregate fitness erases (#221 sec 7 P11).
"""
from __future__ import annotations

import random
import time
from typing import Any, Dict, List

from evaluation.objectives import objective_vector
from morphology.direct_genome import random_genome
from morphology.mutations import mutate, crossover
from morphology.schema import OCMMorphologyGenomeV1
from search.map_elites import evaluate_record

CASE_KEYS = ("method_acq", "composition", "scoped_failure", "repr_twin",
             "revocation", "probe", "similarity_recall", "family_variant")


def case_vector(rec: Dict[str, Any]) -> List[float]:
    """Per-case performance: solved fraction per world family + neg cost cases."""
    pf = rec["evaluation"].get("per_family", {})
    cases = [pf.get(c, {}).get("solved", 0) / max(1, pf.get(c, {}).get("total", 1))
             for c in CASE_KEYS]
    cases.append(-rec["evaluation"].get("work_total", 0.0) / 500.0)
    cases.append(-rec["evaluation"].get("persistent_bytes", 0.0) / 150.0)
    return cases


def lexicase_select(population: List[Dict[str, Any]], rng: random.Random,
                    epsilon: float = 0.0) -> Dict[str, Any]:
    if not population:
        raise ValueError("empty population")
    candidates = list(population)
    cases = list(range(len(CASE_KEYS) + 2))
    rng.shuffle(cases)
    for ci in cases:
        if len(candidates) == 1:
            break
        vals = [case_vector(c)[ci] for c in candidates]
        best = max(vals)
        threshold = best - epsilon
        candidates = [c for c, v in zip(candidates, vals) if v >= threshold] or candidates
    return rng.choice(candidates)


def run(budget: int = 4000, seed: int = 0, pop_size: int = 100,
        epsilon: float = 0.0, start_from=None) -> Dict[str, Any]:
    rng = random.Random(seed)
    t0 = time.time()
    n_evals = 0
    n_feasible = 0
    population: List[Dict[str, Any]] = []
    kept: Dict[str, Dict[str, Any]] = {}
    while n_evals < budget:
        need = pop_size if not population else pop_size
        children = []
        for _ in range(need):
            if n_evals >= budget:
                break
            if population and rng.random() < 0.9:
                a = lexicase_select(population, rng, epsilon)
                b = lexicase_select(population, rng, epsilon)
                ga = OCMMorphologyGenomeV1.from_json_obj(a["genome"])
                gb = OCMMorphologyGenomeV1.from_json_obj(b["genome"])
                child = mutate(crossover(ga, gb, rng), rng, p_struct=0.5, p_theta=0.5)
            else:
                child = random_genome(rng)
            r = evaluate_record(child, "B_behavior_2d")
            n_evals += 1
            if r["feasible"]:
                n_feasible += 1
                kept[r["phenotype_digest"]] = r
                children.append(r)
        if children:
            population = (population + children)[-pop_size:]
    return {
        "algorithm": "P11_lexicase", "seed": seed, "evals": n_evals,
        "elapsed_s": round(time.time() - t0, 3), "feasible_found": n_feasible,
        "unique_feasible_phenotypes": len(kept),
        "best_dev_score": max((r["dev_score"] for r in kept.values()), default=None),
        "archive": [{kk: r[kk] for kk in
                     ("genotype_digest", "phenotype_digest", "genome", "objectives",
                      "dev_score", "descriptors")} for r in kept.values()],
    }

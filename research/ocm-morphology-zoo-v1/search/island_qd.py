"""P13 island-model QD (MZ-D8, FREEZE_V1_AMEND_4) — IMPLEMENTED.

Replaces the MZ-D8 authorization stub: the gate condition ("after fixed-ecology
QD is calibrated, MZ-D3") is met by amend-1/2/3 (QDA1/QDA2/QDA3 frozen and
aggregated).  Other gated modules keep their stubs.

Islands are PRIOR-RESTRICTED subregions of the frozen census grammar
(CENSUS_BOUND_V1).  #221 sec 7 P13 island priors, mapped faithfully onto the
E0_direct genome (declared mapping; the one P13 prior NOT supported faithfully
— "open-ended operator language" — is dropped: O_basis is DERIVED from
units/L/K/R by operators_for(), it is not a free genome field, so an
open-operator island cannot be expressed without misrepresenting the genome):

  P13 prior                  island region (within CENSUS_BOUND_V1)
  ------------------------------------------------------------------
  symbolic/rule-heavy        F_arch in {flat_typed_relational, event_sourced_tms};
                             production_rule required; extras from
                             {production_rule, constraint_solver, exact_index}
  programmatic               rewrite_program required; extras from
                             {rewrite_program, search_planner, exact_index}
  factor/graph-heavy         F_arch = hypergraph_metagraph (extras free)
  blackboard/production      F_arch = blackboard_production,
                             Pi_arch = blackboard_bidding_agenda,
                             production_rule required
  memory-heavy               K = episodic_store, episodic_memory required
  minimal/tiny               zero extra units (single fact_relation store)
  heterogeneous units        exactly 3 extra units (all fields free)

Each island runs its own MAP-Elites archive (GridArchive, D_dev_2d@10);
sampling, mutation and crossover are REGION-LOCKED (offspring that would leave
the island region are re-drawn), so the only cross-island mixing channel is
migration.  Migration (frozen): unidirectional ring, every M rounds, each
island's current best elite (by dev_score) is copied to its successor and
competes there via try_insert; migration is not charged evaluation budget.
The no-migration control consumes an IDENTICAL per-island RNG stream: migration
itself draws no rng, so I01 (mig) and I02 (nomig) differ only through planted
migrants and their descendants.

Island identity/provenance: every genome carries provenance["birth_island"];
migrants carry provenance["migrations"] (copy count) — surviving cross-island
elites are identifiable after the run.
"""
from __future__ import annotations

import math
import random
from typing import Any, Dict, List, Optional, Tuple

from morphology.direct_genome import CENSUS_BOUND_V1, _make
from morphology.mutations import crossover, mutate
from search.map_elites import GridArchive, evaluate_record

# ------------------------------------------------------------------ priors
# FROZEN in FREEZE_V1_AMEND_4.json by hpc/freeze_amend4.py (which imports this
# table — single source of truth).  None = inherit CENSUS_BOUND_V1 tuple.
ISLAND_PRIORS_V1: Tuple[Dict[str, Any], ...] = (
    {"island_id": "I1_symbolic_rule_heavy", "p13_prior": "symbolic/rule-heavy",
     "F_arch": ("flat_typed_relational", "event_sourced_tms"),
     "extras_pool": ("production_rule", "constraint_solver", "exact_index"),
     "extras_required": ("production_rule",), "n_extras": (1, 3),
     "T_family": None, "Pi_arch": None, "L": None, "R": None, "K": None},
    {"island_id": "I2_programmatic", "p13_prior": "programmatic",
     "F_arch": None,
     "extras_pool": ("rewrite_program", "search_planner", "exact_index"),
     "extras_required": ("rewrite_program",), "n_extras": (1, 3),
     "T_family": None, "Pi_arch": None, "L": None, "R": None, "K": None},
    {"island_id": "I3_factor_graph_heavy", "p13_prior": "factor/graph-heavy",
     "F_arch": ("hypergraph_metagraph",),
     "extras_pool": tuple(CENSUS_BOUND_V1["extra_units"]),
     "extras_required": (), "n_extras": (0, 3),
     "T_family": None, "Pi_arch": None, "L": None, "R": None, "K": None},
    {"island_id": "I4_blackboard_production", "p13_prior": "blackboard/production",
     "F_arch": ("blackboard_production",),
     "extras_pool": tuple(CENSUS_BOUND_V1["extra_units"]),
     "extras_required": ("production_rule",), "n_extras": (1, 3),
     "T_family": None, "Pi_arch": ("blackboard_bidding_agenda",),
     "L": None, "R": None, "K": None},
    {"island_id": "I5_memory_heavy", "p13_prior": "memory-heavy",
     "F_arch": None,
     "extras_pool": tuple(CENSUS_BOUND_V1["extra_units"]),
     "extras_required": ("episodic_memory",), "n_extras": (1, 3),
     "T_family": None, "Pi_arch": None, "L": None, "R": None,
     "K": ("episodic_store",)},
    {"island_id": "I6_minimal_tiny", "p13_prior": "minimal/tiny",
     "F_arch": None,
     "extras_pool": (), "extras_required": (), "n_extras": (0, 0),
     "T_family": None, "Pi_arch": None, "L": None, "R": None, "K": None},
    {"island_id": "I7_heterogeneous_units", "p13_prior": "heterogeneous units",
     "F_arch": None,
     "extras_pool": tuple(CENSUS_BOUND_V1["extra_units"]),
     "extras_required": (), "n_extras": (3, 3),
     "T_family": None, "Pi_arch": None, "L": None, "R": None, "K": None},
)

N_ISLANDS = len(ISLAND_PRIORS_V1)


def _bound_field(field: str, prior: Dict[str, Any]) -> Tuple[str, ...]:
    v = prior[field]
    return tuple(CENSUS_BOUND_V1[field]) if v is None else tuple(v)


def in_region(g, prior: Dict[str, Any]) -> bool:
    """Region predicate: is genome g inside this island's prior subregion?"""
    extras = tuple(sorted(u.unit_type for u in g.U if u.unit_type != "fact_relation"))
    if g.F_arch not in _bound_field("F_arch", prior):
        return False
    pool = set(prior["extras_pool"])
    required = set(prior["extras_required"])
    if not set(extras) <= pool or not required <= set(extras):
        return False
    lo, hi = prior["n_extras"]
    if not (lo <= len(extras) <= hi):
        return False
    for f in ("T_family", "Pi_arch", "L", "R", "K"):
        if getattr(g, f) not in _bound_field(f, prior):
            return False
    return True


def region_sampler(prior: Dict[str, Any], rng: random.Random):
    """Uniform-ish draw from the island's restricted grammar."""
    pool = [t for t in prior["extras_pool"]
            if t not in prior["extras_required"]]
    lo, hi = prior["n_extras"]
    hi = min(hi, len(prior["extras_required"]) + len(pool))
    n = rng.randint(min(lo, hi), hi)
    extras = set(prior["extras_required"])
    if n > len(extras):
        extras |= set(rng.sample(pool, n - len(extras)))
    F = rng.choice(list(_bound_field("F_arch", prior)))
    return _make(F, sorted(extras), rng.choice(list(_bound_field("T_family", prior))),
                 rng.choice(list(_bound_field("Pi_arch", prior))),
                 rng.choice(list(_bound_field("L", prior))),
                 rng.choice(list(_bound_field("R", prior))),
                 rng.choice(list(_bound_field("K", prior))))


def region_child(parent_rec: Dict[str, Any], prior: Dict[str, Any],
                 rng: random.Random, second_rec: Optional[Dict[str, Any]] = None):
    """Region-locked reproduction: mutate (or crossover) up to 8 tries; an
    offspring that leaves the island region is discarded and re-drawn (the
    re-draw consumes rng identically in mig and nomig arms); after 8 misses
    fall back to the regional sampler (fresh island genome)."""
    from morphology.schema import OCMMorphologyGenomeV1
    p1 = OCMMorphologyGenomeV1.from_json_obj(parent_rec["genome"])
    for _ in range(8):
        if second_rec is None or rng.random() < 0.5:
            child = mutate(p1, rng)
        else:
            p2 = OCMMorphologyGenomeV1.from_json_obj(second_rec["genome"])
            child = crossover(p1, p2, rng)
        if in_region(child, prior):
            child.provenance = dict(child.provenance)
            child.provenance["birth_island"] = parent_rec["genome"].get(
                "provenance", {}).get("birth_island", -1)
            return child
    return region_sampler(prior, rng)


def normalized_entropy(counts: List[int], n_classes: int) -> float:
    n = sum(counts)
    if n == 0 or n_classes <= 1:
        return 0.0
    h = -sum((c / n) * math.log(c / n + 1e-12, 2) for c in counts if c > 0)
    return round(h / math.log(n_classes, 2), 6)


def run_islands(budget: int = 40000, seed: int = 0, archive: str = "D_dev_2d",
                res: int = 10, migration: bool = True, interval: int = 500,
                init_fraction: float = 0.2) -> Dict[str, Any]:
    """P13 island run: N_ISLANDS region-locked MAP-Elites islands, round-robin
    interleaved (one evaluation per island per round), optional ring migration
    every `interval` rounds (simultaneous: all outbound migrants are chosen
    from the pre-migration state, then inserted).  Per-island budget is
    budget // N_ISLANDS; charged evals are therefore N_ISLANDS * that."""
    per = budget // N_ISLANDS
    rngs = [random.Random(seed * 1000003 + i) for i in range(N_ISLANDS)]
    archs = [GridArchive(archive, res) for _ in range(N_ISLANDS)]
    batches: List[List[Any]] = [[] for _ in range(N_ISLANDS)]
    n_evals = [0] * N_ISLANDS
    n_feasible = [0] * N_ISLANDS
    n_migrants_planted = 0
    n_migration_events = 0
    n_init = max(1, int(per * init_fraction))
    for i, prior in enumerate(ISLAND_PRIORS_V1):
        for _ in range(n_init):
            g = region_sampler(prior, rngs[i])
            g.provenance = {"origin": "island_init", "birth_island": i}
            batches[i].append(g)
    mid_counts: Optional[List[int]] = None
    mid_round = per // 2

    def class_counts() -> List[int]:
        """Pooled (deduped by genotype digest) count of elites per birth
        island; elites with a missing/invalid birth_island count nowhere."""
        counts = [0] * N_ISLANDS
        seen = set()
        for i in range(N_ISLANDS):
            for e in archs[i].elites():
                gd = e["genotype_digest"]
                if gd in seen:
                    continue
                seen.add(gd)
                b = e["genome"].get("provenance", {}).get("birth_island", -1)
                if 0 <= b < N_ISLANDS:
                    counts[b] += 1
        return counts

    for rnd in range(per):
        for i, prior in enumerate(ISLAND_PRIORS_V1):
            if not batches[i]:
                if not archs[i].cells:
                    g = region_sampler(prior, rngs[i])
                    g.provenance = {"origin": "island_init", "birth_island": i}
                    batches[i].append(g)
                else:
                    elites = archs[i].elites()
                    if len(elites) == 1 or rngs[i].random() < 0.5:
                        batches[i].append(region_child(
                            rngs[i].choice(elites), prior, rngs[i]))
                    else:
                        batches[i].append(region_child(
                            rngs[i].choice(elites), prior, rngs[i],
                            second_rec=rngs[i].choice(elites)))
            g = batches[i].pop()
            if "birth_island" not in g.provenance:
                g.provenance = dict(g.provenance)
                g.provenance["birth_island"] = i
            rec = evaluate_record(g, archive)
            rec["residence_island"] = i
            n_evals[i] += 1
            if rec["feasible"]:
                n_feasible[i] += 1
            archs[i].try_insert(rec)
        if migration and (rnd + 1) % interval == 0:
            n_migration_events += 1
            outbound = []
            for i in range(N_ISLANDS):
                elites = archs[i].elites()
                if elites:
                    outbound.append(max(elites, key=lambda e: e["dev_score"]))
                else:
                    outbound.append(None)
            for i, migrant in enumerate(outbound):
                if migrant is None:
                    continue
                j = (i + 1) % N_ISLANDS
                prov = dict(migrant["genome"].get("provenance", {}))
                prov["migrations"] = prov.get("migrations", 0) + 1
                from morphology.schema import OCMMorphologyGenomeV1
                g = OCMMorphologyGenomeV1.from_json_obj(migrant["genome"])
                g.provenance = prov
                copy = dict(migrant)
                copy["genome"] = g.to_json_obj()
                copy["genotype_digest"] = g.digest()
                copy["residence_island"] = j
                copy["migrant"] = True
                if archs[j].try_insert(copy):
                    n_migrants_planted += 1
        if rnd + 1 == mid_round:
            mid_counts = class_counts()

    final_counts = class_counts()
    pooled, seen = [], set()
    for i in range(N_ISLANDS):
        for e in archs[i].elites():
            if e["genotype_digest"] not in seen:
                seen.add(e["genotype_digest"])
                pooled.append(e)
    return {
        "algorithm": "P13_island_qd", "seed": seed,
        "migration": migration, "interval": interval,
        "topology": "unidirectional_ring",
        "archive_name": archive, "resolution": res,
        "n_islands": N_ISLANDS,
        "per_island_budget": per,
        "evals": sum(n_evals), "n_evals_per_island": n_evals,
        "n_feasible_per_island": n_feasible,
        "n_migration_events": n_migration_events,
        "n_migrants_planted": n_migrants_planted,
        "island_class_counts_mid": mid_counts,
        "island_class_counts_final": final_counts,
        "island_entropy_mid": normalized_entropy(mid_counts or [], N_ISLANDS),
        "island_entropy_final": normalized_entropy(final_counts, N_ISLANDS),
        "n_elites_pooled": len(pooled),
        "islands": {"%d_%s" % (i, p["island_id"]): {
            "n_elites": len(archs[i].elites()),
            "best_dev": max((e["dev_score"] for e in archs[i].elites()),
                            default=None),
            "n_feasible_evals": n_feasible[i]}
            for i, p in enumerate(ISLAND_PRIORS_V1)},
        "archive": pooled,
    }

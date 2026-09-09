"""E0 direct explicit genome: KSO reference morphology + samplers + census bound.

The reference arm mirrors the *organization* of the production core
(src/ocm/kso + src/ocm/runtime at ab53109) at the abstraction level of the zoo
schema.  Faithfulness map (organizational, not code-level):

  production component                       zoo genome element
  ------------------------------------------------------------------
  kso/space.py typed store                   F_arch=kso_reference, fact_relation
  runtime/operator_index + extraction_index  exact_index unit, retrieval mult
  kso/warrant.py + admission.py              admit_warranted operator
  kso/extraction*.py gated closure           extract_closure operator
  kso/procedures.py + firing.py              production_rule unit, compose_methods
  kso/nogoods.py + obligations.py            L=scoped_nogood, check_consistency
  kso/revocation.py cones                    R=dependency_cone_reopen, revoke_reopen
  kso/jump.py + surprise.py probes           diagnostic_probe unit, probe_missing
  kso/abstraction.py                         abstraction_schema unit, consolidate
  runtime cost-aware exact ordering          Pi_arch=cost_aware_metapolicy
  persistent store + index                   K=persistent_facts_index
"""
from __future__ import annotations

import random
from itertools import combinations
from typing import Dict, Iterator, List, Sequence, Tuple

from morphology.schema import (EXECUTIVE_FAMILIES, FIELD_FAMILIES, LEARNING_FAMILIES,
                     MEMORY_FAMILIES, OCMMorphologyGenomeV1, REVISION_FAMILIES,
                     TOPOLOGY_FAMILIES, UNIT_TYPES, UnitSpec, OPERATORS)
from morphology.compile import OPERATOR_SUPPORT, LEARNING_SUBSTITUTES, MEMORY_SUBSTITUTES

DEFAULT_THETA: Dict[str, float] = {
    "queue_budget": 32.0, "probe_budget": 4.0, "expansion_cap": 64.0,
    "consolidation_threshold": 0.5, "index_build": 1.0, "bidding_temperature": 1.0,
}

# Census bound P00 (frozen in manifests before any optimizer comparison).
CENSUS_BOUND_V1: Dict[str, Tuple[str, ...]] = {
    "F_arch": ("flat_typed_relational", "hypergraph_metagraph",
               "blackboard_production", "event_sourced_tms",
               "approx_projection_vsa", "kso_reference"),
    "extra_units": ("production_rule", "rewrite_program", "search_planner",
                    "exact_index", "assoc_similarity", "constraint_solver",
                    "diagnostic_probe", "abstraction_schema", "episodic_memory"),
    "max_extra_units": 3,
    "T_family": ("central_blackboard_star", "layered_dag", "sparse_modular"),
    "Pi_arch": ("exact_global_queue", "blackboard_bidding_agenda"),
    "L": ("none", "exemplar_persistence", "scoped_nogood"),
    "R": ("dependency_cone_reopen", "full_rescan"),
    "K": ("persistent_facts", "episodic_store"),
}


def reference_kso_genome() -> OCMMorphologyGenomeV1:
    units = [
        UnitSpec("kso_store", "fact_relation"),
        UnitSpec("kso_index", "exact_index"),
        UnitSpec("kso_procedures", "production_rule"),
        UnitSpec("kso_probe", "diagnostic_probe"),
        UnitSpec("kso_abstraction", "abstraction_schema"),
    ]
    return OCMMorphologyGenomeV1(
        encoding="E0_direct", F_arch="kso_reference", U=units,
        T_family="layered_dag",
        O_basis=("observe", "admit_warranted", "extract_closure",
                 "compose_methods", "probe_missing", "check_consistency",
                 "revoke_reopen", "consolidate"),
        Pi_arch="cost_aware_metapolicy", L="scoped_nogood",
        R="dependency_cone_reopen", K="persistent_facts_index",
        theta=dict(DEFAULT_THETA),
        provenance={"origin": "reference_kso_mirror", "issue": 221},
    )


def operators_for(units: Sequence[str], L: str, K: str, R: str) -> Tuple[str, ...]:
    """Canonical operator language: every operator executable given units/L/K/R."""
    support_types = set(units)
    out = []
    for op in OPERATORS:
        support = set(OPERATOR_SUPPORT[op]) | set(LEARNING_SUBSTITUTES.get(op, ()))
        if op in MEMORY_SUBSTITUTES:
            support |= set(MEMORY_SUBSTITUTES[op])
        if support & support_types or L in support or K in support:
            if op == "revoke_reopen":
                if R != "none":
                    out.append(op)
            else:
                out.append(op)
    return tuple(sorted(out))


def _make(F: str, extras: Sequence[str], T: str, Pi: str, L: str, R: str,
          K: str) -> OCMMorphologyGenomeV1:
    unit_types = ["fact_relation"] + list(extras)
    units = [UnitSpec("u%02d_%s" % (i, t), t) for i, t in enumerate(unit_types)]
    return OCMMorphologyGenomeV1(
        encoding="E0_direct", F_arch=F, U=units, T_family=T,
        O_basis=operators_for(unit_types, L, K, R), Pi_arch=Pi, L=L, R=R, K=K,
        theta=dict(DEFAULT_THETA))


def enumerate_census(bound: Dict[str, Tuple[str, ...]] = CENSUS_BOUND_V1) -> Iterator[OCMMorphologyGenomeV1]:
    """Exhaustive enumeration of every legal genome within the census bound."""
    from .compile import compile_genome, InvariantViolation
    for F in bound["F_arch"]:
        extras_pool = list(bound["extra_units"])
        for n in range(0, bound["max_extra_units"] + 1):
            for extras in combinations(extras_pool, n):
                for T in bound["T_family"]:
                    for Pi in bound["Pi_arch"]:
                        for L in bound["L"]:
                            for R in bound["R"]:
                                for K in bound["K"]:
                                    g = _make(F, extras, T, Pi, L, R, K)
                                    try:
                                        compile_genome(g)
                                    except InvariantViolation:
                                        continue  # illegal combination, not a census member
                                    yield g


def census_size(bound: Dict[str, Tuple[str, ...]] = CENSUS_BOUND_V1) -> int:
    n = 0
    for _ in enumerate_census(bound):
        n += 1
    return n


def random_genome(rng: random.Random, bound: Dict[str, Tuple[str, ...]] = CENSUS_BOUND_V1
                  ) -> OCMMorphologyGenomeV1:
    """Uniform-ish sampler over the census grammar (used by P01 and mutations)."""
    extras_pool = list(bound["extra_units"])
    n = rng.randint(0, bound["max_extra_units"])
    extras = sorted(rng.sample(extras_pool, n))
    return _make(rng.choice(bound["F_arch"]), extras, rng.choice(bound["T_family"]),
                 rng.choice(bound["Pi_arch"]), rng.choice(bound["L"]),
                 rng.choice(bound["R"]), rng.choice(bound["K"]))

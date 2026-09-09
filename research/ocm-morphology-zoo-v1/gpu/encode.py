"""Genome -> compiled feature rows for the batched T0 tape (GS GPU lane).

The encoder NEVER reimplements compile semantics: it calls the zoo's own
morphology.compile.compile_genome per genome (exact structural synthesis +
invariant validation on CPU) and extracts the scalar features the frozen T0
tape (evaluation/lifetime.py) and the descriptor registries consume.  The
vectorized tape then reproduces run_lifetime arithmetic bit-for-bit.

Feature contract (names are frozen; the tape reads exactly these):
  flags/lookups
    f_idx, t_idx, pi_idx, l_idx, r_idx, k_idx   vocabulary indices
    fm_admit/fm_retrieve/fm_reopen/fm_bytes/fm_compose   FIELD_MULT row
    tm_cross, tm_maintenance                     TOPOLOGY_MULT row
    em_dispatch, em_expansion, em_probe          EXEC_MULT row
    queue_budget (int), index_build_theta
  capability sets (over ACTIVE unit types — same as Sim.types)
    has_<unit_type> for the 13 unit types (1.0/0.0)
    can_check, can_probe, can_schema, persists   (derived exactly as in
    run_lifetime, including the L/K/Pi substitutions)
    r_none, r_full_rescan, l_consolidation, l_not_none, f_hierarchical_fibred
  structure
    n_units, n_active_units, n_modules (max(1,..) as in Sim), unit_prior
    (charged prior over ALL units, dead included — #221 sec 3.2), n_edges,
    max_degree, n_dead
  bookkeeping (strings/lists kept per row, not columns)
    genotype_digest, phenotype_digest, active_unit_types, active_operators,
    dead_units, unit_type_counts_in_U_order (for the entropy sum order)
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from morphology.compile import CompiledOrganism, compile_genome
from morphology.schema import (EXECUTIVE_FAMILIES, FIELD_FAMILIES,
                               LEARNING_FAMILIES, MEMORY_FAMILIES,
                               REVISION_FAMILIES, TOPOLOGY_FAMILIES,
                               UNIT_TYPES)
from evaluation.lifetime import COST_MODEL_V1, EXEC_MULT, FIELD_MULT, TOPOLOGY_MULT

F_VOCAB: Tuple[str, ...] = tuple(sorted(FIELD_FAMILIES))
T_VOCAB: Tuple[str, ...] = tuple(TOPOLOGY_FAMILIES)
PI_VOCAB: Tuple[str, ...] = tuple(sorted(EXECUTIVE_FAMILIES))
L_VOCAB: Tuple[str, ...] = tuple(LEARNING_FAMILIES)
R_VOCAB: Tuple[str, ...] = tuple(REVISION_FAMILIES)
K_VOCAB: Tuple[str, ...] = tuple(MEMORY_FAMILIES)
UNIT_TYPE_VOCAB: Tuple[str, ...] = tuple(sorted(UNIT_TYPES))

CHARGED_PRIOR: Dict[str, int] = {
    "fact_relation": 16, "production_rule": 24, "rewrite_program": 32,
    "fsm_controller": 20, "search_planner": 28, "exact_index": 40,
    "assoc_similarity": 24, "constraint_solver": 36, "diagnostic_probe": 22,
    "abstraction_schema": 30, "episodic_memory": 18,
    "procedural_memory": 18, "local_executive": 26,
}

# column names produced per batch (floats unless noted)
COLUMN_NAMES: Tuple[str, ...] = (
    "f_idx", "t_idx", "pi_idx", "l_idx", "r_idx", "k_idx",
    "fm_admit", "fm_retrieve", "fm_reopen", "fm_bytes", "fm_compose",
    "tm_cross", "tm_maintenance",
    "em_dispatch", "em_expansion", "em_probe",
    "queue_budget", "index_build_theta",
    "can_check", "can_probe", "can_schema", "persists",
    "r_none", "r_full_rescan", "l_consolidation", "l_not_none",
    "f_hierarchical_fibred",
    "n_units", "n_active_units", "n_modules", "unit_prior",
    "n_edges", "max_degree", "n_dead",
) + tuple("has_" + t for t in UNIT_TYPE_VOCAB)


def encode_organism(org: CompiledOrganism) -> Dict[str, Any]:
    """Extract the frozen feature row from a compiled organism (exact)."""
    g = org.genome
    types = set(org.active_unit_types)  # Sim.types — ACTIVE types only
    fm = FIELD_MULT[g.F_arch]
    tm = TOPOLOGY_MULT[g.T_family]
    em = EXEC_MULT[g.Pi_arch]
    deg: Dict[str, int] = {}
    for a, b in org.edges:
        deg[a] = deg.get(a, 0) + 1
        deg[b] = deg.get(b, 0) + 1
    row: Dict[str, Any] = {
        "f_idx": float(F_VOCAB.index(g.F_arch)),
        "t_idx": float(T_VOCAB.index(g.T_family)),
        "pi_idx": float(PI_VOCAB.index(g.Pi_arch)),
        "l_idx": float(L_VOCAB.index(g.L)),
        "r_idx": float(R_VOCAB.index(g.R)),
        "k_idx": float(K_VOCAB.index(g.K)),
        "fm_admit": float(fm["admit"]), "fm_retrieve": float(fm["retrieve"]),
        "fm_reopen": float(fm["reopen"]), "fm_bytes": float(fm["bytes"]),
        "fm_compose": float(fm["compose"]),
        "tm_cross": float(tm["cross"]), "tm_maintenance": float(tm["maintenance"]),
        "em_dispatch": float(em["dispatch"]), "em_expansion": float(em["expansion"]),
        "em_probe": float(em["probe"]),
        "queue_budget": float(int(g.theta.get("queue_budget", 32.0))),
        "index_build_theta": float(g.theta.get("index_build", 1.0)),
        "can_check": 1.0 if (("constraint_solver" in types)
                             or (g.L == "scoped_nogood")) else 0.0,
        "can_probe": 1.0 if (("diagnostic_probe" in types)
                             or (g.Pi_arch == "adaptive_probe_policy")) else 0.0,
        "can_schema": 1.0 if (("abstraction_schema" in types) or (
            g.L in ("anti_unification_schema", "consolidation_schema_residual"))
        ) else 0.0,
        "persists": 1.0 if ((g.L != "none") or ("episodic_memory" in types)
                            or (g.K in ("episodic_store", "procedural_store"))
                            ) else 0.0,
        "r_none": 1.0 if g.R == "none" else 0.0,
        "r_full_rescan": 1.0 if g.R == "full_rescan" else 0.0,
        "l_consolidation": 1.0 if g.L == "consolidation_schema_residual" else 0.0,
        "l_not_none": 1.0 if g.L != "none" else 0.0,
        "f_hierarchical_fibred": 1.0 if g.F_arch == "hierarchical_fibred" else 0.0,
        "n_units": float(len(g.U)),
        "n_active_units": float(len(org.active_units)),
        "n_modules": float(max(1, len(org.modules))),
        "unit_prior": float(sum(CHARGED_PRIOR[u.unit_type] for u in g.U)),
        "n_edges": float(len(org.edges)),
        "max_degree": float(max(deg.values()) if deg else 0),
        "n_dead": float(len(org.dead_units)),
    }
    for t in UNIT_TYPE_VOCAB:
        row["has_" + t] = 1.0 if t in types else 0.0
    # per-row bookkeeping (not tape columns)
    row["_genotype_digest"] = org.genotype_digest
    row["_phenotype_digest"] = org.phenotype_digest
    row["_active_unit_types"] = list(org.active_unit_types)
    row["_active_operators"] = list(org.active_operators)
    row["_dead_units"] = list(org.dead_units)
    # unit-type counts in genome.U order — fixes the descriptor entropy
    # summation order to structural_descriptors' dict insertion order
    counts: Dict[str, int] = {}
    for u in g.U:
        counts[u.unit_type] = counts.get(u.unit_type, 0) + 1
    row["_unit_type_counts_in_U_order"] = [
        (t, c) for t, c in counts.items()]
    row["_t_family"] = g.T_family
    row["_r_family"] = g.R
    row["_n_modules_raw"] = len(org.modules)
    # structural descriptors computed ONCE by the real zoo function (exact,
    # never reimplemented); behavioral/developmental are derived later from
    # the batched tape outputs by gpu.batch_descriptors via the same zoo
    # functions
    from evaluation.descriptors import structural_descriptors
    row["_structural"] = structural_descriptors(org)
    return row


def encode_genome(genome: Any) -> Dict[str, Any]:
    """compile + encode one genome (exact zoo compile path)."""
    return encode_organism(compile_genome(genome))


def encode_batch(genomes: List[Any]) -> Dict[str, Any]:
    """Encode many genomes -> {'columns': {name: [floats]}, 'rows': [...]}."""
    rows = [encode_genome(g) for g in genomes]
    columns: Dict[str, List[float]] = {name: [r[name] for r in rows]
                                       for name in COLUMN_NAMES}
    meta = [{k: v for k, v in r.items() if k.startswith("_")} for r in rows]
    return {"n": len(rows), "columns": columns, "meta": meta,
            "column_names": list(COLUMN_NAMES)}

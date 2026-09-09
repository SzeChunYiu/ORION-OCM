"""Diversity descriptors for Archives S / B / D (#221 sec 5).

All descriptor computations are deterministic functions of the compiled
organism and its evaluation.  Descriptor registries (bounds, dimension,
archive kind) are declared here and consumed by search/map_elites etc.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Sequence, Tuple

from morphology.compile import CompiledOrganism
from morphology.schema import APPROXIMATE_UNIT_TYPES

# ---------------------------------------------------------------- Archive S
S_DIMS = ("centralization", "hierarchy_depth", "module_count",
          "unit_type_entropy", "edge_density", "controller_centralization",
          "explicit_fraction")


def structural_descriptors(org: CompiledOrganism) -> Dict[str, float]:
    units = org.genome.U
    n = max(1, len(units))
    types = [u.unit_type for u in units]
    counts: Dict[str, int] = {}
    for t in types:
        counts[t] = counts.get(t, 0) + 1
    entropy = -sum((c / n) * math.log(c / n + 1e-12, 2) for c in counts.values())
    max_entropy = math.log(len(counts) + 1e-12, 2) if len(counts) > 1 else 1.0
    norm_entropy = entropy / max(1.0, max_entropy)
    edges = org.edges
    possible = n * (n - 1) / 2.0
    density = len(edges) / max(1.0, possible)
    # centralization: share of edges touching the most connected unit
    deg: Dict[str, int] = {}
    for a, b in edges:
        deg[a] = deg.get(a, 0) + 1
        deg[b] = deg.get(b, 0) + 1
    if org.genome.T_family == "central_blackboard_star" or not deg:
        centralization = 1.0
    else:
        centralization = max(deg.values()) / max(1, 2 * len(edges))
    hier = {"layered_dag": 3.0, "hierarchy_tree": 3.0, "central_blackboard_star": 2.0,
            "sparse_modular": 2.0, "small_world_sparse": 2.0,
            "recurrent_event_graph": 2.0, "distributed_local_controllers": 2.0,
            "growing_pruning": 2.0}.get(org.genome.T_family, 2.0)
    n_exec = sum(1 for u in units if u.unit_type in ("local_executive",))
    ctrl_centralization = 1.0 if n_exec == 0 else 1.0 / (1.0 + n_exec)
    approx = sum(1 for u in units if u.unit_type in APPROXIMATE_UNIT_TYPES)
    explicit_fraction = 1.0 - approx / n
    return {
        "centralization": round(centralization, 6),
        "hierarchy_depth": hier,
        "module_count": float(max(1, len(org.modules))),
        "unit_type_entropy": round(norm_entropy, 6),
        "edge_density": round(density, 6),
        "controller_centralization": round(ctrl_centralization, 6),
        "explicit_fraction": round(explicit_fraction, 6),
    }


# ---------------------------------------------------------------- Archive B
B_DIMS = ("active_kN", "expansions_per_solved", "probe_count",
          "method_reuse_fraction", "composition_depth",
          "revision_work_ratio", "refusal_rate")


def behavioral_descriptors(org: CompiledOrganism, ev: Dict[str, Any]) -> Dict[str, float]:
    solved = max(1, ev.get("solved", 0))
    return {
        "active_kN": float(ev.get("active_kN", 0.0)),
        "expansions_per_solved": round(ev.get("expansions", 0) / solved, 6),
        "probe_count": float(ev.get("probes", 0)),
        "method_reuse_fraction": float(ev.get("method_reuse_fraction", 0.0)),
        "composition_depth": float(ev.get("composition_used", 0)),
        "revision_work_ratio": round(
            ev.get("revision_work", 0.0) / max(1.0, ev.get("work_total", 1.0)), 6),
        "refusal_rate": round(
            ev.get("correct_refusals", 0) / max(1, ev.get("correct_refusals", 0)
                                                + ev.get("harmful_transfers", 0)), 6),
    }


def transfer_profile(ev: Dict[str, Any]) -> List[float]:
    """Solved-fraction per world family — the transfer-profile vector."""
    fams = ("method_acq", "composition", "scoped_failure", "repr_twin",
            "revocation", "probe", "similarity_recall", "family_variant")
    pf = ev.get("per_family", {})
    return [round(pf.get(f, {}).get("solved", 0) / max(1, pf.get(f, {}).get("total", 1)), 6)
            for f in fams]


# ---------------------------------------------------------------- Archive D
D_DIMS = ("primitive_pressure_slope", "marginal_acquisition_slope",
          "persistent_growth_per_capability", "learned_vs_imported",
          "consolidation_ratio")
# interpretable grid-view axes over Archive D (MZ-D7, FREEZE_V1_AMEND_3)
D2_VIEW_DIMS = ("marginal_acquisition_slope", "persistent_growth_per_capability")


def _slope(ys: Sequence[float]) -> float:
    if len(ys) < 2:
        return 0.0
    n = len(ys)
    xs = list(range(n))
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs) or 1.0
    return num / den


def developmental_descriptors(org: CompiledOrganism, ev: Dict[str, Any]) -> Dict[str, float]:
    caps = [float(c) for c in ev.get("epoch_capabilities", [])]
    work = [float(w) for w in ev.get("epoch_work", [])]
    bytes_ = [float(b) for b in ev.get("epoch_persistent_bytes", [])]
    new_caps = [max(0.0, caps[i] - (caps[i - 1] if i else 0.0))
                for i in range(len(caps))]
    # work per NEW capability per epoch (primitive-pressure slope proxy)
    wpc = [work[i] / (new_caps[i] if new_caps[i] > 0 else 1.0)
           for i in range(len(work))]
    learned = ev.get("methods", 0) + ev.get("episodes", 0) + ev.get("schemas", 0)
    imported = len(org.genome.U)
    return {
        "primitive_pressure_slope": round(_slope(wpc), 6),
        "marginal_acquisition_slope": round(_slope(work), 6),
        "persistent_growth_per_capability": round(
            (bytes_[-1] - bytes_[0]) / max(1.0, sum(new_caps)) if bytes_ else 0.0, 6),
        "learned_vs_imported": round(learned / max(1, learned + imported), 6),
        "consolidation_ratio": round(
            ev.get("maintenance_work", 0.0) / max(1.0, ev.get("work_total", 1.0)), 6),
    }


DESCRIPTOR_REGISTRY: Dict[str, Dict[str, Any]] = {
    "S_structural_2d": {"dims": ("centralization", "unit_type_entropy"),
                        "bounds": ((0.0, 1.0), (0.0, 1.0)), "kind": "grid"},
    "S_structural_3d": {"dims": ("centralization", "unit_type_entropy", "module_count"),
                        "bounds": ((0.0, 1.0), (0.0, 1.0), (1.0, 4.0)), "kind": "grid"},
    "S_cvtd": {"dims": S_DIMS, "kind": "cvt"},
    "B_behavior_2d": {"dims": ("expansions_per_solved", "method_reuse_fraction"),
                      "bounds": ((0.0, 32.0), (0.0, 1.0)), "kind": "grid"},
    "B_cvtd": {"dims": B_DIMS, "kind": "cvt"},
    "D_developmental": {"dims": D_DIMS, "kind": "cvt"},
    # MZ-D7 (FREEZE_V1_AMEND_3): grid views over Archive D.  Bounds are the
    # empirical feasible-census ranges quantized outward to 0.05, taken from
    # CENSUS_P00C truth and frozen BEFORE any scored T2 run (asserted by
    # tests against archives/CENSUS_P00C_TRUTH.json).  The 3d view's third
    # axis is primitive_pressure_slope: consolidation_ratio is IDENTICALLY 0
    # over the frozen V1 census space (its only charging paths are
    # T_family in {recurrent_event_graph, distributed_local_controllers,
    # growing_pruning} and L == consolidation_schema_residual — none present
    # in the 56160-genome space), so it is a dead axis there (P00C finding).
    "D_dev_2d": {"dims": D2_VIEW_DIMS,
                 "bounds": ((1.35, 37.75), (3.0, 10.4)), "kind": "grid"},
    "D_dev_3d": {"dims": D2_VIEW_DIMS + ("primitive_pressure_slope",),
                 "bounds": ((1.35, 37.75), (3.0, 10.4), (1.85, 38.85)),
                 "kind": "grid"},
}


def descriptors_for(org: CompiledOrganism, ev: Dict[str, Any],
                    archive: str = "S_structural_2d") -> Tuple[float, ...]:
    reg = DESCRIPTOR_REGISTRY[archive]
    if archive.startswith("S"):
        d = structural_descriptors(org)
    elif archive.startswith("B"):
        d = behavioral_descriptors(org, ev)
    else:
        d = developmental_descriptors(org, ev)
    return tuple(float(d[k]) for k in reg["dims"])

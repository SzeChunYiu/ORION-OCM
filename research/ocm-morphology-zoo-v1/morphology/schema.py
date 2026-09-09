"""OCMMorphologyGenomeV1 — typed genome for zoo organisms (issue #221 sec 3).

G = (F_arch, U, T, O_basis, Pi_arch, L, R, K, theta).  C is NOT part of G.

Research-only: nothing here touches production src/.  Python >=3.9, stdlib only.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

GENOME_SCHEMA_ID = "OCMMorphologyGenomeV1"
UNIT_CONTRACT_ID = "CognitiveUnitContractV1"

# ---------------------------------------------------------------- vocabularies

# Field / knowledge-space families (#221 sec 3.1).  Each entry:
#   native_warrant  — can facts admitted via this field alone carry identity/warrant
#   approximate     — any approximate/proposal-only representation built in
#   native_reopen   — dependency reopening is native (cheap revocation cone)
FIELD_FAMILIES: Dict[str, Dict[str, Any]] = {
    "flat_typed_relational": {"native_warrant": True, "approximate": False, "native_reopen": False,
                              "note": "production-KSO-shaped flat typed store"},
    "typed_property_graph": {"native_warrant": True, "approximate": False, "native_reopen": False},
    "hypergraph_metagraph": {"native_warrant": True, "approximate": False, "native_reopen": False,
                             "nary": True},
    "factorized_field": {"native_warrant": True, "approximate": False, "native_reopen": False},
    "hierarchical_fibred": {"native_warrant": True, "approximate": False, "native_reopen": False,
                            "scoped": True},
    "blackboard_production": {"native_warrant": True, "approximate": False, "native_reopen": False},
    "event_sourced_tms": {"native_warrant": True, "approximate": False, "native_reopen": True},
    "library_procedural": {"native_warrant": True, "approximate": False, "native_reopen": False},
    "approx_projection_vsa": {"native_warrant": False, "approximate": True, "native_reopen": False,
                              "note": "HDC/VSA projection, proposal-only; exact store required for warrant"},
    "kso_reference": {"native_warrant": True, "approximate": False, "native_reopen": True,
                      "note": "reference arm mirroring src/ocm/kso organization on main ab53109"},
}

# Cognitive unit types (#221 sec 3.2).  charged_prior = prior information charged
# at compile time (bytes); approximate units can never mint identity/warrant.
UNIT_TYPES: Dict[str, Dict[str, Any]] = {
    "fact_relation": {"charged_prior": 16, "approximate": False,
                      "competence": "hold/derive typed facts"},
    "production_rule": {"charged_prior": 24, "approximate": False,
                        "competence": "fire rule: premises->conclusion facts"},
    "rewrite_program": {"charged_prior": 32, "approximate": False,
                        "competence": "convert raw obs to typed features (representation repair)"},
    "fsm_controller": {"charged_prior": 20, "approximate": False,
                       "competence": "ordered multi-step method execution (A then B)"},
    "search_planner": {"charged_prior": 28, "approximate": False,
                       "competence": "bounded forward search to goal, charged per expansion"},
    "exact_index": {"charged_prior": 40, "approximate": False,
                    "competence": "exact retrieval index; build cost charged, query cost reduced"},
    "assoc_similarity": {"charged_prior": 24, "approximate": True,
                         "competence": "similarity proposals WITHOUT warrant"},
    "constraint_solver": {"charged_prior": 36, "approximate": False,
                          "competence": "consistency check; detects scoped failure (nogood)"},
    "diagnostic_probe": {"charged_prior": 22, "approximate": False,
                         "competence": "adaptive information gathering (decision-sufficient state)"},
    "abstraction_schema": {"charged_prior": 30, "approximate": False,
                           "competence": "compress patterns; generalize to family variants"},
    "episodic_memory": {"charged_prior": 18, "approximate": False,
                        "competence": "store solved-case trajectories for reuse"},
    "procedural_memory": {"charged_prior": 18, "approximate": False,
                          "competence": "store compiled procedures; cheap re-execution"},
    "local_executive": {"charged_prior": 26, "approximate": False,
                        "competence": "local scheduling; reduces global dispatch overhead"},
}

APPROXIMATE_UNIT_TYPES = frozenset(t for t, m in UNIT_TYPES.items() if m["approximate"])

# Topology families (#221 sec 3.3).
TOPOLOGY_FAMILIES = (
    "central_blackboard_star", "layered_dag", "hierarchy_tree", "sparse_modular",
    "small_world_sparse", "recurrent_event_graph", "distributed_local_controllers",
    "growing_pruning",
)

# Executive families (#221 sec 3.4).  learned=False for every legal family (#71).
EXECUTIVE_FAMILIES: Dict[str, Dict[str, Any]] = {
    "exact_global_queue": {"learned": False},
    "event_driven_local": {"learned": False},
    "hierarchical_executive": {"learned": False},
    "blackboard_bidding_agenda": {"learned": False},
    "cost_aware_metapolicy": {"learned": False},
    "adaptive_probe_policy": {"learned": False, "note": "#216 parent"},
    "distributed_propose_central_commit": {"learned": False},
}

# Learning / development families (#221 sec 3.5).
LEARNING_FAMILIES = (
    "none", "exemplar_persistence", "anti_unification_schema", "library_learning",
    "rewrite_egraph_abstraction", "verifier_guided_cegis", "scoped_nogood",
    "representation_split", "consolidation_schema_residual",
)

# Revision / consolidation rule families.
REVISION_FAMILIES = (
    "none", "dependency_cone_reopen", "full_rescan",
)

# Memory organization families.
MEMORY_FAMILIES = (
    "volatile_only", "persistent_facts", "persistent_facts_index", "episodic_store",
    "procedural_store", "consolidated_schema_residual",
)

# Primitive + compositional operator language (O_basis).  Operators may be
# enabled/disabled per genome; every enabled operator's execution work is charged.
OPERATORS = (
    "observe", "admit_warranted", "extract_closure", "compose_methods",
    "propose_similar", "check_consistency", "probe_missing", "abstract_schema",
    "store_episode", "compile_procedure", "revoke_reopen", "consolidate",
)


@dataclass
class UnitSpec:
    """One cognitive unit instance (CognitiveUnitContractV1 carrier)."""
    unit_id: str
    unit_type: str
    params: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.unit_type not in UNIT_TYPES:
            raise ValueError("unknown unit type: %s" % self.unit_type)
        if not self.unit_id:
            raise ValueError("unit_id must be non-empty")


@dataclass
class OCMMorphologyGenomeV1:
    """G = (F_arch, U, T, O_basis, Pi_arch, L, R, K, theta)."""
    schema_id: str = GENOME_SCHEMA_ID
    encoding: str = "E0_direct"          # E0_direct | E1_cgp | E2_graph_grammar | E3_typed_program
    F_arch: str = "flat_typed_relational"
    U: List[UnitSpec] = field(default_factory=list)
    T_family: str = "central_blackboard_star"
    T_edges: List[Tuple[str, str]] = field(default_factory=list)   # (from_unit_id, to_unit_id)
    O_basis: Tuple[str, ...] = ()
    Pi_arch: str = "exact_global_queue"
    L: str = "none"
    R: str = "dependency_cone_reopen"
    K: str = "persistent_facts"
    theta: Dict[str, float] = field(default_factory=dict)
    provenance: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.schema_id != GENOME_SCHEMA_ID:
            raise ValueError("schema mismatch")
        if self.F_arch not in FIELD_FAMILIES:
            raise ValueError("unknown field family: %s" % self.F_arch)
        if self.T_family not in TOPOLOGY_FAMILIES:
            raise ValueError("unknown topology family: %s" % self.T_family)
        if self.Pi_arch not in EXECUTIVE_FAMILIES:
            raise ValueError("unknown executive: %s" % self.Pi_arch)
        if self.L not in LEARNING_FAMILIES:
            raise ValueError("unknown learning family: %s" % self.L)
        if self.R not in REVISION_FAMILIES:
            raise ValueError("unknown revision family: %s" % self.R)
        if self.K not in MEMORY_FAMILIES:
            raise ValueError("unknown memory family: %s" % self.K)
        for op in self.O_basis:
            if op not in OPERATORS:
                raise ValueError("unknown operator: %s" % op)
        ids = [u.unit_id for u in self.U]
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate unit ids")

    # ---- serialization -------------------------------------------------
    def to_json_obj(self) -> Dict[str, Any]:
        return {
            "schema_id": self.schema_id,
            "encoding": self.encoding,
            "F_arch": self.F_arch,
            "U": [{"unit_id": u.unit_id, "unit_type": u.unit_type,
                   "params": dict(sorted(u.params.items()))} for u in self.U],
            "T_family": self.T_family,
            "T_edges": sorted(tuple(e) for e in self.T_edges),
            "O_basis": sorted(self.O_basis),
            "Pi_arch": self.Pi_arch,
            "L": self.L,
            "R": self.R,
            "K": self.K,
            "theta": dict(sorted(self.theta.items())),
            "provenance": _canon_jsonable(self.provenance),
        }

    @classmethod
    def from_json_obj(cls, obj: Dict[str, Any]) -> "OCMMorphologyGenomeV1":
        return cls(
            schema_id=obj["schema_id"], encoding=obj["encoding"], F_arch=obj["F_arch"],
            U=[UnitSpec(u["unit_id"], u["unit_type"], dict(u.get("params", {})))
               for u in obj["U"]],
            T_family=obj["T_family"],
            T_edges=[tuple(e) for e in obj["T_edges"]],
            O_basis=tuple(obj["O_basis"]),
            Pi_arch=obj["Pi_arch"], L=obj["L"], R=obj["R"], K=obj["K"],
            theta=dict(obj.get("theta", {})),
            provenance=dict(obj.get("provenance", {})),
        )

    def digest(self) -> str:
        return hashlib.sha256(
            json.dumps(self.to_json_obj(), sort_keys=True,
                       separators=(",", ":")).encode("utf-8")).hexdigest()

    def clone(self) -> "OCMMorphologyGenomeV1":
        import copy
        return copy.deepcopy(self)


def _canon_jsonable(x: Any) -> Any:
    if isinstance(x, dict):
        return {str(k): _canon_jsonable(v) for k, v in sorted(x.items(), key=lambda kv: str(kv[0]))}
    if isinstance(x, (list, tuple)):
        return [_canon_jsonable(v) for v in x]
    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    return str(x)

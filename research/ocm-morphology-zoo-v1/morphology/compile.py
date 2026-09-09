"""Genome -> ExecutableOrganism compiler + invariant validator (#221 MZ-D1).

Produces the structural object the lifetime simulator evaluates.  Family cost
multipliers live in evaluation/lifetime.py (single frozen cost model); this
module owns structure, reachability (active vs dead units), operator
support, and constitutional invariant validation at compile time.
"""
from __future__ import annotations

from typing import Dict, FrozenSet, List, Tuple

from morphology.canonicalize import phenotype_digest
from morphology.schema import (APPROXIMATE_UNIT_TYPES, EXECUTIVE_FAMILIES,
                     FIELD_FAMILIES, LEARNING_FAMILIES, MEMORY_FAMILIES,
                     OCMMorphologyGenomeV1, REVISION_FAMILIES, TOPOLOGY_FAMILIES,
                     UNIT_TYPES, UnitSpec)

# operator -> unit types that can execute it (executive/learning families can
# substitute for a missing unit; substitutions are recorded, never free).
OPERATOR_SUPPORT: Dict[str, Tuple[str, ...]] = {
    "observe": ("fact_relation",),
    "admit_warranted": ("fact_relation",),
    "extract_closure": ("fact_relation", "search_planner"),
    "compose_methods": ("fsm_controller", "search_planner"),
    "propose_similar": ("assoc_similarity",),
    "check_consistency": ("constraint_solver",),
    "probe_missing": ("diagnostic_probe",),
    "abstract_schema": ("abstraction_schema",),
    "store_episode": ("episodic_memory",),
    "compile_procedure": ("procedural_memory",),
    "revoke_reopen": ("fact_relation",),
    "consolidate": ("abstraction_schema",),
}

LEARNING_SUBSTITUTES = {
    "probe_missing": ("adaptive_probe_policy",),
    "abstract_schema": ("anti_unification_schema",),
    "compile_procedure": ("library_learning",),
    "store_episode": ("exemplar_persistence",),
    "consolidate": ("consolidation_schema_residual",),
    "check_consistency": ("scoped_nogood",),
}
MEMORY_SUBSTITUTES = {
    "store_episode": ("episodic_store",),
    "compile_procedure": ("procedural_store",),
}
EXECUTIVE_SUBSTITUTES = {
    "probe_missing": ("adaptive_probe_policy",),
}


class InvariantViolation(Exception):
    def __init__(self, code: str, detail: str):
        super().__init__("%s: %s" % (code, detail))
        self.code = code
        self.detail = detail


# deterministic grouping used by module-oriented topologies
_TYPE_GROUP_ORDER = (
    ("fact_relation", "exact_index", "assoc_similarity"),
    ("production_rule", "rewrite_program", "fsm_controller", "search_planner",
     "constraint_solver", "diagnostic_probe", "abstraction_schema"),
    ("episodic_memory", "procedural_memory", "local_executive"),
)


def _type_group(unit_type: str) -> int:
    for gi, group in enumerate(_TYPE_GROUP_ORDER):
        if unit_type in group:
            return gi
    return 1


class CompiledOrganism:
    """Structural phenotype: what the organism *is*, before any task runs."""

    def __init__(self, genome: OCMMorphologyGenomeV1) -> None:
        self.genome = genome
        self.units: Dict[str, UnitSpec] = {u.unit_id: u for u in genome.U}
        self._validate_invariants()
        self.edges = self._resolve_edges()
        self.active_units = self._reachability()
        self.active_unit_types = tuple(sorted(
            self.units[uid].unit_type for uid in self.active_units))
        self.active_operators = tuple(sorted(self._active_operators()))
        self.phenotype_digest = phenotype_digest(
            genome, self.active_unit_types, self.active_operators)
        self.genotype_digest = genome.digest()
        self.dead_units = tuple(sorted(set(self.units) - set(self.active_units)))
        self.modules = self._modules()

    # ------------------------------------------------------------------
    def _validate_invariants(self) -> None:
        g = self.genome
        # vocabulary membership: fail closed as InvariantViolation (never KeyError),
        # even when the genome was mutated after construction
        if g.F_arch not in FIELD_FAMILIES:
            raise InvariantViolation("UNKNOWN_FIELD_FAMILY", g.F_arch)
        for attr, vocab, tag in (("T_family", TOPOLOGY_FAMILIES, "T"),
                                 ("Pi_arch", EXECUTIVE_FAMILIES, "PI"),
                                 ("L", LEARNING_FAMILIES, "L"),
                                 ("R", REVISION_FAMILIES, "R"),
                                 ("K", MEMORY_FAMILIES, "K")):
            if getattr(g, attr) not in vocab:
                raise InvariantViolation("UNKNOWN_%s_FAMILY" % tag, getattr(g, attr))
        for u in g.U:
            if u.unit_type not in UNIT_TYPES:
                raise InvariantViolation("UNKNOWN_UNIT_TYPE", u.unit_type)
        # edges reference existing units
        for a, b in g.T_edges:
            if a not in self.units or b not in self.units:
                raise InvariantViolation(
                    "EDGE_TO_UNKNOWN_UNIT", "%s->%s" % (a, b))
        # INV-APPX-1: approximate representations never mint identity/warrant.
        if FIELD_FAMILIES[g.F_arch].get("approximate") and "admit_warranted" in g.O_basis:
            exact_units = [u for u in g.U if u.unit_type == "fact_relation"]
            if not exact_units:
                raise InvariantViolation(
                    "APPROXIMATE_FIELD_MINTS_WARRANT",
                    "approx_projection_vsa has no exact fact unit to carry warrant")
        for u in g.U:
            if u.unit_type in APPROXIMATE_UNIT_TYPES and "admit_warranted" in u.params:
                raise InvariantViolation(
                    "APPROXIMATE_UNIT_MINTS_WARRANT", u.unit_id)
        # learned router ban (#71): the executive vocabulary cannot express it,
        # and theta may not smuggle learned selectors.
        for key in g.theta:
            if "learned" in key or "router" in key:
                raise InvariantViolation("LEARNED_ROUTER_BAN", key)
        # revocation semantics cannot be weakened below cone reopen while
        # claiming revoke_reopen
        if "revoke_reopen" in g.O_basis and g.R == "none":
            raise InvariantViolation("REVOCATION_WEAKENED",
                                     "revoke_reopen operator with R=none")

    def _resolve_edges(self) -> List[Tuple[str, str]]:
        g = self.genome
        if g.T_edges:
            return sorted(set(tuple(e) for e in g.T_edges))
        ids = sorted(self.units)
        if not ids:
            return []
        fam = g.T_family
        out: List[Tuple[str, str]] = []
        if fam in ("central_blackboard_star", "recurrent_event_graph"):
            pass  # all units attach to the implicit working state
        elif fam == "layered_dag":
            layers: List[List[str]] = [[], [], []]
            for uid in ids:
                layers[_type_group(self.units[uid].unit_type)].append(uid)
            for i in range(2):
                for a in layers[i]:
                    for b in layers[i + 1]:
                        out.append((a, b))
            if fam == "recurrent_event_graph":
                for b in layers[2]:
                    for a in layers[1]:
                        out.append((b, a))
        elif fam in ("hierarchy_tree", "sparse_modular", "small_world_sparse",
                     "distributed_local_controllers", "growing_pruning"):
            groups: List[List[str]] = [[], [], []]
            for uid in ids:
                groups[_type_group(self.units[uid].unit_type)].append(uid)
            for gi in range(3):
                reps = groups[gi][:1]
                for rep in reps:
                    for m in groups[gi]:
                        if m != rep:
                            out.append((rep, m))
                if gi < 2 and groups[gi] and groups[gi + 1]:
                    out.append((groups[gi][0], groups[gi + 1][0]))
            if fam == "small_world_sparse" and len(ids) >= 4:
                out.append((ids[0], ids[-1]))
                out.append((ids[len(ids) // 2], ids[0]))
        return sorted(set(out))

    def _reachability(self) -> FrozenSet[str]:
        """A unit is active iff it can exchange with the working state.

        central star / recurrent event: everything is attached to the shared
        working state -> all active.  Module topologies: modules whose group
        contains no scheduler (local_executive) and has no bridge edge are
        unreachable under distributed dispatch.
        """
        g = self.genome
        ids = set(self.units)
        fam = g.T_family
        if fam in ("central_blackboard_star", "recurrent_event_graph",
                   "layered_dag", "hierarchy_tree", "small_world_sparse"):
            return frozenset(ids)
        if fam in ("sparse_modular", "growing_pruning"):
            # every module reachable through its representative chain
            groups: List[List[str]] = [[], [], []]
            for uid in sorted(ids):
                groups[_type_group(self.units[uid].unit_type)].append(uid)
            active = set()
            for gi, grp in enumerate(groups):
                if grp and any(u in ids for u in grp):
                    active.update(grp)
            return frozenset(active)
        # distributed_local_controllers: a group is live only with a local_executive
        groups = [[], [], []]
        for uid in sorted(ids):
            groups[_type_group(self.units[uid].unit_type)].append(uid)
        active = set()
        for grp in groups:
            if any(self.units[u].unit_type == "local_executive" for u in grp):
                active.update(grp)
        return frozenset(active)

    def _active_operators(self) -> List[str]:
        g = self.genome
        active_types = set(self.active_unit_types)
        result = []
        for op in g.O_basis:
            support = set(OPERATOR_SUPPORT[op]) | set(LEARNING_SUBSTITUTES.get(op, ()))
            if op in MEMORY_SUBSTITUTES:
                support |= set(MEMORY_SUBSTITUTES[op])
            if op in EXECUTIVE_SUBSTITUTES:
                support |= set(EXECUTIVE_SUBSTITUTES[op])
            # executive family can substitute for probe support
            if g.Pi_arch in support or g.L in support or g.K in support:
                result.append(op)
            elif support & active_types:
                result.append(op)
        return result

    def _modules(self) -> List[List[str]]:
        groups: List[List[str]] = [[], [], []]
        for uid in sorted(self.active_units):
            groups[_type_group(self.units[uid].unit_type)].append(uid)
        return [grp for grp in groups if grp]


def compile_genome(genome: OCMMorphologyGenomeV1) -> CompiledOrganism:
    return CompiledOrganism(genome)

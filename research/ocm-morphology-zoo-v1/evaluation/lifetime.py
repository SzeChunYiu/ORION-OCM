"""Frozen cost model + exact micro-world battery + lifetime simulator (MZ-D1/D2).

Scientific contract
-------------------
* Deterministic: evaluate(organism) is a pure function of the compiled
  phenotype — no RNG.  Optimizer seeds live in search/, never here.
* Complete charging: every unit (active AND dead), every operation, every
  stored byte, every maintenance pass is charged before any capability is
  credited (#221 sec 12: 'giant memory/search system wins by uncharged
  state/work' must be impossible).
* Exact checkers: each world has a ground-truth condition; approximate units
  can only propose, never mint correct answers.

The constants below are the zoo's physics.  They are frozen in
FREEZE_V1.json BEFORE any scored run; sensitivity spot-checks are recorded in
results/ (census sensitivity note).  Changing any constant after scored runs
is a numbered freeze amendment.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from morphology.compile import CompiledOrganism

COST_MODEL_V1: Dict[str, float] = {
    # base work units (deterministic, world constants)
    "observe_work": 1.0,          # admit one observation
    "closure_work": 2.0,          # one gated-closure level
    "expansion_work": 3.0,        # one planner expansion
    "rule_fire_work": 1.0,        # one production firing
    "rewrite_work": 4.0,          # one representation rewrite
    "probe_work": 2.0,            # one adaptive probe
    "index_build_work": 8.0,      # one-time exact index build
    "index_query_work": 1.0,      # indexed retrieval
    "scan_item_work": 1.0,        # linear scan of one stored item
    "consistency_work": 4.0,      # one consistency/nogood check
    "abstraction_work": 6.0,      # one schema abstraction
    "store_work": 2.0,            # persist one item
    "reuse_work": 1.0,            # apply persisted method once
    "schema_apply_work": 1.0,     # apply a schema to a variant
    "rescan_work": 10.0,          # full rescan per fact after revocation
    "cone_reopen_work": 3.0,      # reopen per item in dependency cone
    "dispatch_work": 1.0,         # one executive dispatch
    "hop_work": 0.5,              # one inter-unit message hop
    "consolidate_work": 3.0,      # one maintenance/consolidation pass
    "bidding_work": 0.2,          # agenda bidding per task
    # world shapes (exact instance parameters, not tunable)
    "w1_expansions": 8.0, "w2_expansions": 14.0, "w4_expansions": 6.0,
    "w6_info_need": 4.0, "w6_probe_yield": 2.0, "w6_n_obs": 12.0,
    "w7_items": 10.0, "w7_k": 3.0, "w8_variants": 3.0,
    "revocation_facts": 6.0, "w3_premises": 3.0,
}

# field-family multipliers (documented mechanism, frozen)
FIELD_MULT: Dict[str, Dict[str, float]] = {
    "flat_typed_relational": {"admit": 1.0, "retrieve": 1.0, "reopen": 1.0, "bytes": 1.0, "compose": 1.0},
    "typed_property_graph": {"admit": 1.2, "retrieve": 0.7, "reopen": 1.0, "bytes": 1.3, "compose": 1.0},
    "hypergraph_metagraph": {"admit": 1.5, "retrieve": 0.6, "reopen": 1.0, "bytes": 1.5, "compose": 0.6},
    "factorized_field": {"admit": 1.4, "retrieve": 0.8, "reopen": 1.0, "bytes": 1.2, "compose": 1.0},
    "hierarchical_fibred": {"admit": 1.1, "retrieve": 0.9, "reopen": 0.8, "bytes": 1.1, "compose": 1.0},
    "blackboard_production": {"admit": 0.9, "retrieve": 1.0, "reopen": 1.0, "bytes": 1.0, "compose": 0.9},
    "event_sourced_tms": {"admit": 1.2, "retrieve": 1.1, "reopen": 0.4, "bytes": 1.6, "compose": 1.0},
    "library_procedural": {"admit": 1.0, "retrieve": 0.9, "reopen": 1.0, "bytes": 1.0, "compose": 1.0},
    "approx_projection_vsa": {"admit": 1.3, "retrieve": 0.3, "reopen": 1.0, "bytes": 1.2, "compose": 1.0},
    "kso_reference": {"admit": 1.0, "retrieve": 0.8, "reopen": 0.5, "bytes": 1.1, "compose": 1.0},
}

TOPOLOGY_MULT: Dict[str, Dict[str, float]] = {
    "central_blackboard_star": {"cross": 1.0, "maintenance": 0.0},
    "layered_dag": {"cross": 1.1, "maintenance": 0.0},
    "hierarchy_tree": {"cross": 1.3, "maintenance": 0.0},
    "sparse_modular": {"cross": 1.4, "maintenance": 0.0},
    "small_world_sparse": {"cross": 0.8, "maintenance": 0.0},
    "recurrent_event_graph": {"cross": 1.1, "maintenance": 1.0},
    "distributed_local_controllers": {"cross": 1.5, "maintenance": 1.0},
    "growing_pruning": {"cross": 1.0, "maintenance": 2.0},
}

EXEC_MULT: Dict[str, Dict[str, float]] = {
    "exact_global_queue": {"dispatch": 1.0, "expansion": 1.0, "probe": 1.0},
    "event_driven_local": {"dispatch": 0.7, "expansion": 1.0, "probe": 1.0},
    "hierarchical_executive": {"dispatch": 0.8, "expansion": 1.0, "probe": 1.0},
    "blackboard_bidding_agenda": {"dispatch": 0.75, "expansion": 1.0, "probe": 1.0},
    "cost_aware_metapolicy": {"dispatch": 1.1, "expansion": 0.8, "probe": 1.0},
    "adaptive_probe_policy": {"dispatch": 1.0, "expansion": 1.0, "probe": 0.8},
    "distributed_propose_central_commit": {"dispatch": 0.7, "expansion": 1.0, "probe": 1.0},
}


class Sim:
    """Deterministic cost-accounting accumulator for one organism lifetime."""

    def __init__(self, org: CompiledOrganism) -> None:
        self.org = org
        g = org.genome
        self.cm = dict(COST_MODEL_V1)
        self.fm = FIELD_MULT[g.F_arch]
        self.tm = TOPOLOGY_MULT[g.T_family]
        self.em = EXEC_MULT[g.Pi_arch]
        self.types = set(org.active_unit_types)
        self.ops = set(org.active_operators)
        self.budget = int(g.theta.get("queue_budget", 32.0))
        self.n_modules = max(1, len(org.modules))
        # cost counters
        self.work = 0.0
        self.acquisition_work = 0.0
        self.reasoning_work = 0.0
        self.verification_work = 0.0
        self.maintenance_work = 0.0
        self.revision_work = 0.0
        self.probes = 0
        self.expansions = 0
        self.hops = 0
        # lifetime memory
        self.methods = 0
        self.episodes = 0
        self.schemas = 0
        self.index_built = False
        self.facts = 0
        # outcomes
        self.solved = 0
        self.total = 0
        self.correct_refusals = 0
        self.harmful_transfers = 0
        self.stale_answers = 0
        self.reused = 0
        self.compose_used = 0
        self.epoch_work: List[float] = []
        self.epoch_capabilities: List[int] = []
        self.epoch_persistent_bytes: List[float] = []
        self._epoch_work_acc = 0.0
        self._epoch_cap_acc = 0

    # ---------------------------------------------------------------- helpers
    def _charge(self, w: float, bucket: str = "reasoning") -> None:
        self.work += w
        self._epoch_work_acc += w
        if bucket == "acquisition":
            self.acquisition_work += w
        elif bucket == "verification":
            self.verification_work += w
        elif bucket == "maintenance":
            self.maintenance_work += w
        elif bucket == "revision":
            self.revision_work += w
        else:
            self.reasoning_work += w

    def dispatch(self) -> None:
        self._charge(self.cm["dispatch_work"] * self.em["dispatch"], "reasoning")

    def cross_module(self, w: float, bucket: str = "reasoning") -> None:
        self._charge(w * self.tm["cross"] * (1.0 + 0.1 * (self.n_modules - 1) / 2), bucket)

    def persistent_bytes(self) -> float:
        fm = self.fm
        unit_prior = sum(
            # every unit costs its charged prior — dead units too (#221 sec 3.2)
            {"fact_relation": 16, "production_rule": 24, "rewrite_program": 32,
             "fsm_controller": 20, "search_planner": 28, "exact_index": 40,
             "assoc_similarity": 24, "constraint_solver": 36, "diagnostic_probe": 22,
             "abstraction_schema": 30, "episodic_memory": 18,
             "procedural_memory": 18, "local_executive": 26}[u.unit_type]
            for u in self.org.genome.U)
        stored = (self.methods * 8 + self.episodes * 12 + self.schemas * 6
                  + self.facts * 1)
        return (unit_prior + stored * fm["bytes"]) + (
            self.cm["index_build_work"] * 0 if not self.index_built else 24)

    def end_epoch(self) -> None:
        self.epoch_work.append(round(self._epoch_work_acc, 6))
        self.epoch_capabilities.append(self._epoch_cap_acc)
        self.epoch_persistent_bytes.append(round(self.persistent_bytes(), 6))
        self._epoch_work_acc = 0.0
        self._epoch_cap_acc = 0
        if self.org.genome.L == "consolidation_schema_residual":
            self._charge(self.cm["consolidate_work"], "maintenance")
        self._charge(self.tm["maintenance"], "maintenance")


WORLD_FAMILIES = ("method_acq", "composition", "scoped_failure", "repr_twin",
                  "revocation", "probe", "similarity_recall", "family_variant")


def run_lifetime(org: CompiledOrganism) -> Dict[str, Any]:
    """Run the full fixed battery as one deterministic lifetime."""
    s = Sim(org)
    g = org.genome
    per_family: Dict[str, Dict[str, Any]] = {}
    can_rule = "production_rule" in s.types
    can_plan = "search_planner" in s.types
    can_fsm = "fsm_controller" in s.types
    can_rewrite = "rewrite_program" in s.types
    can_index = "exact_index" in s.types
    can_assoc = "assoc_similarity" in s.types
    can_check = ("constraint_solver" in s.types) or (g.L == "scoped_nogood")
    can_probe = ("diagnostic_probe" in s.types) or (g.Pi_arch == "adaptive_probe_policy")
    can_schema = ("abstraction_schema" in s.types) or (
        g.L in ("anti_unification_schema", "consolidation_schema_residual"))
    persists = (g.L != "none") or ("episodic_memory" in s.types) or (
        g.K in ("episodic_store", "procedural_store"))

    def solve_task(family: str, expansions_needed: float, rule_path: bool,
                   composition: bool = False) -> bool:
        s.total += 1
        s.dispatch()
        solved = False
        if rule_path and can_rule:
            s._charge(s.cm["rule_fire_work"] * (2.0 if composition else 1.0)
                      * s.fm.get("compose", 1.0) if composition else s.cm["rule_fire_work"])
            solved = True
        elif can_plan:
            need = expansions_needed * s.em["expansion"]
            if composition:
                need *= s.fm.get("compose", 1.0)
                s.cross_module(need * s.cm["expansion_work"] * 0.1)
            if need <= s.budget:
                s._charge(need * s.cm["expansion_work"])
                s.expansions += int(need)
                solved = True
                if composition:
                    s.compose_used += 1
            else:
                s._charge(s.budget * s.cm["expansion_work"])
                s.expansions += s.budget
        elif can_fsm and composition:
            s._charge(2 * s.cm["rule_fire_work"] * s.fm.get("compose", 1.0))
            solved = True
            s.compose_used += 1
        if solved:
            s.solved += 1
            s._epoch_cap_acc += 1
        per_family.setdefault(family, {"solved": 0, "total": 0})
        per_family[family]["total"] += 1
        if solved:
            per_family[family]["solved"] += 1
        return solved

    # ---- epoch 1: acquisition + retrieval
    s._charge(4 * s.cm["observe_work"] * s.fm["admit"], "acquisition")
    s.facts += 4
    solve_task("method_acq", s.cm["w1_expansions"], can_rule)
    if persists:
        s._charge(s.cm["store_work"], "acquisition")
        s.methods += 1
    # similarity recall world
    s.total += 1
    s.dispatch()
    if can_index:
        if not s.index_built and g.theta.get("index_build", 1.0) >= 1.0:
            s._charge(s.cm["index_build_work"], "acquisition")
            s.index_built = True
        s._charge(s.cm["index_query_work"] * s.fm["retrieve"] * s.cm["w7_k"])
        s.solved += 1
        s._epoch_cap_acc += 1
    elif can_assoc:
        s._charge(s.cm["probe_work"] * s.cm["w7_k"] * s.fm["retrieve"])
        s._charge(s.cm["consistency_work"], "verification")  # exact check mandatory
        s.solved += 1
        s._epoch_cap_acc += 1
    else:
        s._charge(s.cm["scan_item_work"] * s.cm["w7_items"])
        s.solved += 1
        s._epoch_cap_acc += 1
    per_family.setdefault("similarity_recall", {"solved": 1, "total": 1})
    s.end_epoch()

    # ---- epoch 2: reuse, composition, probing
    s.total += 1
    s.dispatch()
    ma_solved = False
    if s.methods > 0 or ("episodic_memory" in s.types):
        s._charge(s.cm["reuse_work"])
        s.reused += 1
        ma_solved = True
    else:
        need = s.cm["w1_expansions"] * s.em["expansion"]
        if can_plan and need <= s.budget:
            s._charge(need * s.cm["expansion_work"])
            ma_solved = True
        elif can_rule:
            s._charge(s.cm["rule_fire_work"])
            ma_solved = True
    if ma_solved:
        s.solved += 1
        s._epoch_cap_acc += 1
    per_family.setdefault("method_acq", {"solved": 0, "total": 0})
    per_family["method_acq"]["total"] += 1
    if ma_solved:
        per_family["method_acq"]["solved"] += 1
    solve_task("composition", s.cm["w2_expansions"], can_rule, composition=True)
    # probe world 1
    s.total += 1
    s.dispatch()
    if can_probe:
        n = int(-(-int(s.cm["w6_info_need"]) // int(s.cm["w6_probe_yield"])))
        s._charge(n * s.cm["probe_work"] * s.em["probe"])
        s.probes += n
        s.solved += 1
        s._epoch_cap_acc += 1
    elif s.budget >= s.cm["w6_n_obs"]:
        s._charge(s.cm["w6_n_obs"] * s.cm["observe_work"] * s.fm["admit"], "acquisition")
        s.solved += 1
        s._epoch_cap_acc += 1
    per_family.setdefault("probe", {"solved": 1 if can_probe or s.budget >= s.cm["w6_n_obs"] else 0, "total": 1})
    s.end_epoch()

    # ---- epoch 3: revocation + scoped failure
    s._charge(3 * s.cm["observe_work"] * s.fm["admit"], "acquisition")
    s.facts += 3
    s.total += 1
    s.dispatch()
    s._charge(s.cm["closure_work"] * s.fm["retrieve"], "reasoning")
    s.solved += 1
    s._epoch_cap_acc += 1
    per_family.setdefault("revocation", {"solved": 0, "total": 0})
    per_family["revocation"]["total"] += 1
    per_family["revocation"]["solved"] += 1
    # revocation event
    if g.R == "none":
        s.stale_answers += 1  # returns stale derived answer — invariant breach
    elif g.R == "full_rescan":
        s._charge(s.cm["rescan_work"] * s.cm["revocation_facts"], "revision")
    else:
        s._charge(s.cm["cone_reopen_work"] * s.fm["reopen"] * 2, "revision")
    # re-solve after reopen
    s.total += 1
    s.dispatch()
    if g.R == "none":
        s.stale_answers += 1  # wrong answer recorded
    else:
        need = 4 * s.em["expansion"]
        if can_plan or can_rule:
            s._charge((s.cm["rule_fire_work"] if can_rule else need * s.cm["expansion_work"]))
            s.solved += 1
            s._epoch_cap_acc += 1
    per_family["revocation"]["total"] += 1
    per_family["revocation"]["solved"] += 0 if g.R == "none" else 1
    # scoped failure x2
    for _ in range(2):
        s.total += 1
        s.dispatch()
        if can_check or g.F_arch == "hierarchical_fibred":
            s._charge(s.cm["consistency_work"] * (0.4 if g.F_arch == "hierarchical_fibred" else 1.0),
                      "verification")
            s.correct_refusals += 1
            per_family.setdefault("scoped_failure", {"solved": 0, "total": 0})
            per_family["scoped_failure"]["total"] += 1
        elif s.methods > 0 or ("episodic_memory" in s.types):
            s._charge(s.cm["reuse_work"])
            s.harmful_transfers += 1  # blind reuse across scopes — WRONG answer
            per_family.setdefault("scoped_failure", {"solved": 0, "total": 0})
            per_family["scoped_failure"]["total"] += 1
        else:
            s._charge(s.cm["rule_fire_work"])
            s.harmful_transfers += 1
            per_family.setdefault("scoped_failure", {"solved": 0, "total": 0})
            per_family["scoped_failure"]["total"] += 1
    s.end_epoch()

    # ---- epoch 4: representation twins, variants, probe 2
    for _ in range(2):
        s.total += 1
        s.dispatch()
        if can_rewrite:
            s._charge(s.cm["rewrite_work"])
            need = s.cm["w4_expansions"] * s.em["expansion"]
            if can_rule:
                s._charge(s.cm["rule_fire_work"])
            elif can_plan and need <= s.budget:
                s._charge(need * s.cm["expansion_work"])
                s.expansions += int(need)
            else:
                per_family.setdefault("repr_twin", {"solved": 0, "total": 0})
                per_family["repr_twin"]["total"] += 1
                continue
            s.solved += 1
            s._epoch_cap_acc += 1
            per_family.setdefault("repr_twin", {"solved": 0, "total": 0})
            per_family["repr_twin"]["total"] += 1
            per_family["repr_twin"]["solved"] += 1
        else:
            per_family.setdefault("repr_twin", {"solved": 0, "total": 0})
            per_family["repr_twin"]["total"] += 1
    fv = per_family.setdefault("family_variant", {"solved": 0, "total": 0})
    for i in range(int(s.cm["w8_variants"])):
        s.total += 1
        s.dispatch()
        fv_solved_task = False
        if can_schema:
            if i == 0:
                s._charge(s.cm["abstraction_work"], "acquisition")
                s.schemas += 1
            s._charge(s.cm["schema_apply_work"])
            fv_solved_task = True
        elif can_rule:
            s._charge(s.cm["rule_fire_work"])
            fv_solved_task = True
        elif can_plan and s.cm["w4_expansions"] <= s.budget:
            s._charge(s.cm["w4_expansions"] * s.cm["expansion_work"])
            fv_solved_task = True
        if fv_solved_task:
            s.solved += 1
            s._epoch_cap_acc += 1
            fv["solved"] += 1
        fv["total"] += 1
    # probe world 2 (same mechanics, count only once more)
    s.total += 1
    s.dispatch()
    if can_probe:
        n = int(-(-int(s.cm["w6_info_need"]) // int(s.cm["w6_probe_yield"])))
        s._charge(n * s.cm["probe_work"] * s.em["probe"])
        s.probes += n
        s.solved += 1
        s._epoch_cap_acc += 1
    per_family.setdefault("probe", {"solved": 0, "total": 0})
    per_family["probe"]["total"] += 1
    if can_probe:
        per_family["probe"]["solved"] += 1
    s.end_epoch()

    return _summarize(s, per_family)


def _summarize(s: Sim, per_family: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    solved_frac = s.solved / max(1, s.total)
    ev = {
        "solved": s.solved, "total_tasks": s.total, "solved_fraction": round(solved_frac, 6),
        "work_total": round(s.work, 6),
        "acquisition_work": round(s.acquisition_work, 6),
        "reasoning_work": round(s.reasoning_work, 6),
        "verification_work": round(s.verification_work, 6),
        "maintenance_work": round(s.maintenance_work, 6),
        "revision_work": round(s.revision_work, 6),
        "self_change_work": 0.0,  # static organisms this tranche (P14+ changes this)
        "persistent_bytes": round(s.persistent_bytes(), 6),
        "probes": s.probes, "expansions": s.expansions,
        "correct_refusals": s.correct_refusals,
        "harmful_transfers": s.harmful_transfers,
        "stale_answers": s.stale_answers,
        "method_reuse_fraction": round(s.reused / 2.0, 6),
        "composition_used": s.compose_used,
        "per_family": {k: dict(v) for k, v in sorted(per_family.items())},
        "epoch_work": s.epoch_work,
        "epoch_capabilities": s.epoch_capabilities,
        "epoch_persistent_bytes": s.epoch_persistent_bytes,
        "methods": s.methods, "episodes": s.episodes, "schemas": s.schemas,
        "active_bytes_proxy": round(
            s.facts * 1.0 + 6.0, 6),
        "dead_units": list(s.org.dead_units),
    }
    # active k/N: fraction of unit mass actually used at least once
    active_used = len([u for u in s.org.active_units])
    ev["active_kN"] = round(active_used / max(1, len(s.org.genome.U)), 6)
    return ev

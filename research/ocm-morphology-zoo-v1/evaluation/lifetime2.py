"""T2 developmental lifetime battery (MZ-D7): LIFETIME_ECOLOGY_V2.

One deterministic long lifetime per organism: 12 epochs over the 8 E0
micro-world families with escalating difficulty, two revocation waves, and a
RESET control (memory cleared at epoch boundaries) that measures retention
value per architecture.  Identical task schedule for every genome; only the
organism differs.  Charging discipline identical to lifetime.py (every unit,
operation, stored byte and maintenance pass is charged; nothing is free).

The V1 battery (lifetime.py) remains FROZEN and untouched: T0 scores and all
amend-1/amend-2 denominators stay reproducible.  T2 constants below are
frozen in FREEZE_V1_AMEND_3.json before any scored T2 run.
"""
from __future__ import annotations

from typing import Any, Dict

from evaluation.lifetime import Sim, _summarize
from morphology.compile import CompiledOrganism

ECOLOGY_V2: Dict[str, Any] = {
    "ecology_id": "LifetimeEcologyV2",
    "epochs": 12,
    # family -> (first_epoch inclusive, tasks per epoch from then on)
    "schedule": {
        "method_acq": (0, 2),
        "similarity_recall": (0, 1),
        "composition": (2, 1),
        "scoped_failure": (3, 1),
        "repr_twin": (4, 1),
        "probe": (5, 1),
        "revocation": (6, 1),
        "family_variant": (7, 2),
    },
    "difficulty_growth": 0.15,   # expansions multiplier per epoch index
    "acquisitions_per_epoch": 3,  # observations admitted every epoch
    "revocation_epochs": (6, 10),
}

# world base shapes reused from COST_MODEL_V1 (frozen in lifetime.py)
_BASE = {"method_acq": "w1_expansions", "composition": "w2_expansions",
         "repr_twin": "w4_expansions", "revocation": 4.0}


def _capabilities(sim: Sim) -> Dict[str, Any]:
    g = sim.org.genome
    s = sim
    return {
        "can_rule": "production_rule" in s.types,
        "can_plan": "search_planner" in s.types,
        "can_fsm": "fsm_controller" in s.types,
        "can_rewrite": "rewrite_program" in s.types,
        "can_index": "exact_index" in s.types,
        "can_assoc": "assoc_similarity" in s.types,
        "can_check": ("constraint_solver" in s.types) or (g.L == "scoped_nogood"),
        "can_probe": ("diagnostic_probe" in s.types)
        or (g.Pi_arch == "adaptive_probe_policy"),
        "can_schema": ("abstraction_schema" in s.types) or (
            g.L in ("anti_unification_schema", "consolidation_schema_residual")),
        "persists": (g.L != "none") or ("episodic_memory" in s.types) or (
            g.K in ("episodic_store", "procedural_store")),
    }


def run_lifetime2(org: CompiledOrganism, reset: bool = False) -> Dict[str, Any]:
    """One T2 lifetime.  reset=True clears persisted memory at every epoch
    boundary (methods/schemas/facts/index) — the continued-vs-reset control."""
    s = Sim(org)
    g = org.genome
    sched = ECOLOGY_V2["schedule"]
    grow = ECOLOGY_V2["difficulty_growth"]
    cap = _capabilities(s)
    per_family: Dict[str, Dict[str, Any]] = {}

    def fam(f: str) -> Dict[str, Any]:
        return per_family.setdefault(f, {"solved": 0, "total": 0})

    def solve(family: str, solved: bool) -> None:
        s.total += 1
        if solved:
            s.solved += 1
            s._epoch_cap_acc += 1
        fam(family)["total"] += 1
        if solved:
            fam(family)["solved"] += 1

    def task(family: str, e: int, composition: bool = False) -> None:
        """One world instance at epoch-e difficulty."""
        s.dispatch()
        base = s.cm.get(_BASE.get(family, "w1_expansions"), _BASE[family]) \
            if family in _BASE else 1.0
        need_mult = 1.0 + grow * e
        solved = False
        if family == "method_acq":
            if s.methods > 0 or "episodic_memory" in s.types:
                s._charge(s.cm["reuse_work"])
                s.reused += 1
                solved = True
            elif cap["can_rule"]:
                s._charge(s.cm["rule_fire_work"])
                solved = True
            elif cap["can_plan"] and base * need_mult * s.em["expansion"] <= s.budget:
                need = base * need_mult * s.em["expansion"]
                s._charge(need * s.cm["expansion_work"])
                s.expansions += int(need)
                solved = True
        elif family == "similarity_recall":
            if cap["can_index"]:
                if not s.index_built and g.theta.get("index_build", 1.0) >= 1.0:
                    s._charge(s.cm["index_build_work"], "acquisition")
                    s.index_built = True
                s._charge(s.cm["index_query_work"] * s.fm["retrieve"] * s.cm["w7_k"])
                solved = True
            elif cap["can_assoc"]:
                s._charge(s.cm["probe_work"] * s.cm["w7_k"] * s.fm["retrieve"])
                s._charge(s.cm["consistency_work"], "verification")
                solved = True
            else:
                s._charge(s.cm["scan_item_work"] * s.cm["w7_items"])
                solved = True
        elif family == "composition":
            if cap["can_rule"]:
                s._charge(2 * s.cm["rule_fire_work"] * s.fm.get("compose", 1.0))
                solved = True
                s.compose_used += 1
            elif cap["can_plan"]:
                need = base * need_mult * s.em["expansion"] * s.fm.get("compose", 1.0)
                if need <= s.budget:
                    s._charge(need * s.cm["expansion_work"])
                    s.cross_module(need * s.cm["expansion_work"] * 0.1)
                    s.expansions += int(need)
                    solved = True
                    s.compose_used += 1
                else:
                    s._charge(s.budget * s.cm["expansion_work"])
                    s.expansions += s.budget
            elif cap["can_fsm"]:
                s._charge(2 * s.cm["rule_fire_work"] * s.fm.get("compose", 1.0))
                solved = True
                s.compose_used += 1
        elif family == "scoped_failure":
            if cap["can_check"] or g.F_arch == "hierarchical_fibred":
                s._charge(s.cm["consistency_work"] * (
                    0.4 if g.F_arch == "hierarchical_fibred" else 1.0), "verification")
                s.correct_refusals += 1
                solved = True
            elif s.methods > 0 or "episodic_memory" in s.types:
                s._charge(s.cm["reuse_work"])
                s.harmful_transfers += 1  # blind reuse across scopes — WRONG
            else:
                s._charge(s.cm["rule_fire_work"])
                s.harmful_transfers += 1
        elif family == "repr_twin":
            if cap["can_rewrite"]:
                s._charge(s.cm["rewrite_work"])
                need = base * need_mult * s.em["expansion"]
                if cap["can_rule"]:
                    s._charge(s.cm["rule_fire_work"])
                    solved = True
                elif cap["can_plan"] and need <= s.budget:
                    s._charge(need * s.cm["expansion_work"])
                    s.expansions += int(need)
                    solved = True
            # no rewrite -> unsolved
        elif family == "probe":
            if cap["can_probe"]:
                n = int(-(-int(s.cm["w6_info_need"]) // int(s.cm["w6_probe_yield"])))
                s._charge(n * s.cm["probe_work"] * s.em["probe"])
                s.probes += n
                solved = True
            elif s.budget >= s.cm["w6_n_obs"]:
                s._charge(s.cm["w6_n_obs"] * s.cm["observe_work"] * s.fm["admit"],
                          "acquisition")
                solved = True
        elif family == "revocation":
            s._charge(s.cm["closure_work"] * s.fm["retrieve"])
            solved = True
            if e in ECOLOGY_V2["revocation_epochs"]:
                # revocation event: reopen the cone, then re-derive
                if g.R == "none":
                    s.stale_answers += 1
                elif g.R == "full_rescan":
                    s._charge(s.cm["rescan_work"] * s.cm["revocation_facts"], "revision")
                else:
                    s._charge(s.cm["cone_reopen_work"] * s.fm["reopen"] * 2, "revision")
                s.total += 1
                s.dispatch()
                if g.R == "none":
                    s.stale_answers += 1
                elif cap["can_rule"]:
                    s._charge(s.cm["rule_fire_work"])
                    s.solved += 1
                    s._epoch_cap_acc += 1
                    fam(family)["solved"] += 1
                elif cap["can_plan"]:
                    need = _BASE["revocation"] * s.em["expansion"]
                    if need <= s.budget:
                        s._charge(need * s.cm["expansion_work"])
                        s.solved += 1
                        s._epoch_cap_acc += 1
                        fam(family)["solved"] += 1
                fam(family)["total"] += 1
        elif family == "family_variant":
            if cap["can_schema"]:
                if s.schemas == 0:
                    s._charge(s.cm["abstraction_work"], "acquisition")
                    s.schemas += 1
                s._charge(s.cm["schema_apply_work"])
                solved = True
            elif cap["can_rule"]:
                s._charge(s.cm["rule_fire_work"] * need_mult)
                solved = True
            elif cap["can_plan"] and s.cm["w4_expansions"] * need_mult <= s.budget:
                s._charge(s.cm["w4_expansions"] * need_mult * s.cm["expansion_work"])
                s.expansions += int(s.cm["w4_expansions"] * need_mult)
                solved = True
        solve(family, solved)

    for e in range(ECOLOGY_V2["epochs"]):
        if reset and e > 0:
            # RESET control: persisted development is wiped each epoch
            s.methods = 0
            s.schemas = 0
            s.facts = 0
            s.index_built = False
        # per-epoch acquisitions
        s._charge(ECOLOGY_V2["acquisitions_per_epoch"] * s.cm["observe_work"]
                  * s.fm["admit"], "acquisition")
        s.facts += ECOLOGY_V2["acquisitions_per_epoch"]
        if e == 0 and cap["persists"]:
            s._charge(s.cm["store_work"], "acquisition")
            s.methods += 1
        for family, (start, per_epoch) in sorted(sched.items()):
            if e < start:
                continue
            for _ in range(per_epoch):
                task(family, e)
        s.end_epoch()

    ev = _summarize(s, per_family)
    # V2 battery has up to 24 method_acq instances (V1 had 2): recompute the
    # reuse fraction against the actual opportunity count, capped at 1.
    ma_total = max(1, fam("method_acq")["total"])
    ev["method_reuse_fraction"] = round(min(1.0, s.reused / ma_total), 6)
    ev["ecology_id"] = ECOLOGY_V2["ecology_id"] if not reset \
        else ECOLOGY_V2["ecology_id"] + "_reset"
    ev["tier"] = "T2"
    return ev

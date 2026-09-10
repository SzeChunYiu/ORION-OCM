"""Held-out T3 ecology (GRAND SEARCH #221 sec 18): a DISJOINT cross-domain
proxy task-family draw, key-frozen inside GRAND_SEARCH_R1_FREEZE.json and
evaluated ONLY on R1 survivors (never during search).

Design contract
---------------
* Family names are disjoint from the 8 V1/T2 world families (method_acq,
  composition, scoped_failure, repr_twin, revocation, probe,
  similarity_recall, family_variant).
* Instance parameters (expansion depths, item scales, variant counts,
  epoch mixes) are drawn DETERMINISTICALLY from sha256(T3_KEY || family):
  nobody chooses them — the freeze tool mints the key before any scored
  run and the draw is a pure function of it.
* Physics unchanged: the frozen COST_MODEL_V1 / FIELD_MULT / TOPOLOGY_MULT
  / EXEC_MULT constants charge every unit, operation and byte exactly as
  the V1/T2 batteries do.  No new constants are minted here.
* Deterministic pure function of the compiled organism — no RNG.
* Viability floor on T3 = the frozen CAPABILITY_FLOOR_V1 (0.5), same as
  every other tier.
"""
from __future__ import annotations

import hashlib
import struct
from typing import Any, Dict, Tuple

from evaluation.invariants import CAPABILITY_FLOOR_V1, hard_gate_report
from evaluation.lifetime import Sim
from morphology.compile import CompiledOrganism, compile_genome

T3_FAMILIES: Tuple[str, ...] = (
    "t3_chain_transfer",      # 3-hop method chaining (deep composition)
    "t3_doubt_probe",         # probing under contradictory evidence
    "t3_scale_retrieval",     # retrieval at key-derived scale
    "t3_conflict_refusal",    # contradiction -> correct refusal required
    "t3_novel_variant",       # schema application to novel variant classes
    "t3_interrupted_plan",    # revocation mid-plan, re-derivation
)


def _u32(key: str, salt: str) -> int:
    h = hashlib.sha256(("%s|%s|%s" % (key, salt, "GS_T3_V1")).encode()).digest()
    return struct.unpack(">I", h[:4])[0]


def _draw(key: str, salt: str, lo: float, hi: float) -> float:
    return round(lo + (hi - lo) * (_u32(key, salt) / 4294967295.0), 4)


def t3_draw(key: str) -> Dict[str, Dict[str, float]]:
    """The full frozen instance draw (deterministic in the key).  Recorded
    verbatim in the freeze so the battery is auditable before survivors
    exist."""
    return {
        "t3_chain_transfer": {"hops": _draw(key, "chain_hops", 2.0, 4.0),
                              "depth_mult": _draw(key, "chain_depth", 0.8, 1.6)},
        "t3_doubt_probe": {"contradictions": _draw(key, "doubt_c", 1.0, 3.0),
                           "probe_yield": _draw(key, "doubt_y", 1.0, 2.5)},
        "t3_scale_retrieval": {"items_mult": _draw(key, "scale_i", 3.0, 8.0),
                               "k": _draw(key, "scale_k", 3.0, 7.0)},
        "t3_conflict_refusal": {"pairs": _draw(key, "conflict_p", 1.0, 3.0)},
        "t3_novel_variant": {"variants": _draw(key, "novel_v", 2.0, 5.0),
                             "depth_mult": _draw(key, "novel_d", 1.0, 1.8)},
        "t3_interrupted_plan": {"interrupts": _draw(key, "int_n", 1.0, 3.0),
                                "redepth": _draw(key, "int_d", 3.0, 7.0)},
    }


def run_t3(org: CompiledOrganism, key: str) -> Dict[str, Any]:
    """One held-out T3 lifetime.  Charging discipline identical to the
    frozen batteries (Sim, COST_MODEL_V1, family multipliers)."""
    d = t3_draw(key)
    s = Sim(org)
    g = org.genome
    per_family: Dict[str, Dict[str, Any]] = {}

    def fam(f: str) -> Dict[str, Any]:
        return per_family.setdefault(f, {"solved": 0, "total": 0})

    def result(f: str, solved: bool) -> None:
        s.total += 1
        if solved:
            s.solved += 1
            s._epoch_cap_acc += 1
        fam(f)["total"] += 1
        if solved:
            fam(f)["solved"] += 1

    can_rule = "production_rule" in s.types
    can_plan = "search_planner" in s.types
    can_fsm = "fsm_controller" in s.types
    can_index = "exact_index" in s.types
    can_assoc = "assoc_similarity" in s.types
    can_check = ("constraint_solver" in s.types) or (g.L == "scoped_nogood")
    can_probe = ("diagnostic_probe" in s.types) or (g.Pi_arch == "adaptive_probe_policy")
    can_schema = ("abstraction_schema" in s.types) or (
        g.L in ("anti_unification_schema", "consolidation_schema_residual"))

    # ---- family t3_chain_transfer: hops sequential derivations, each hop
    # charged; solved only if EVERY hop is executable (rules chain, or one
    # deep planner expansion of depth hops*depth_mult).
    hops = int(d["t3_chain_transfer"]["hops"])
    depth = d["t3_chain_transfer"]["depth_mult"]
    s.dispatch()
    if can_rule:
        for _ in range(hops):
            s._charge(s.cm["rule_fire_work"] * s.fm.get("compose", 1.0))
        result("t3_chain_transfer", True)
    elif can_plan:
        need = hops * depth * s.cm["w1_expansions"] * s.em["expansion"]
        if need <= s.budget:
            s._charge(need * s.cm["expansion_work"])
            s.expansions += int(need)
            result("t3_chain_transfer", True)
        else:
            s._charge(s.budget * s.cm["expansion_work"])
            s.expansions += s.budget
            result("t3_chain_transfer", False)
    elif can_fsm and hops <= 2:
        s._charge(hops * s.cm["rule_fire_work"] * s.fm.get("compose", 1.0))
        result("t3_chain_transfer", True)
    else:
        result("t3_chain_transfer", False)
    s.end_epoch()

    # ---- family t3_doubt_probe: contradictory evidence arrives; the
    # organism must PROBE (information gathering) then CHECK consistency —
    # blind reuse or answering without probing is an incorrect answer.
    contradictions = int(d["t3_doubt_probe"]["contradictions"])
    yield_ = max(1.0, d["t3_doubt_probe"]["probe_yield"])
    s._charge(contradictions * s.cm["observe_work"] * s.fm["admit"], "acquisition")
    s.facts += contradictions
    s.dispatch()
    if can_probe and can_check:
        n = int(-(-int(s.cm["w6_info_need"]) // int(max(1, yield_))))
        s._charge(n * s.cm["probe_work"] * s.em["probe"])
        s.probes += n
        s._charge(s.cm["consistency_work"], "verification")
        s.correct_refusals += 1
        result("t3_doubt_probe", True)
    elif can_check:
        s._charge(s.cm["consistency_work"] * contradictions, "verification")
        s.correct_refusals += 1
        result("t3_doubt_probe", True)
    else:
        s._charge(s.cm["reuse_work"] if s.methods else s.cm["rule_fire_work"])
        s.harmful_transfers += 1  # answered under unresolved doubt — WRONG
        result("t3_doubt_probe", False)
    s.end_epoch()

    # ---- family t3_scale_retrieval: same retrieval competence at a
    # key-derived larger scale (exact index or checked proposals win; pure
    # scan is charged the full scaled scan).
    items = s.cm["w7_items"] * d["t3_scale_retrieval"]["items_mult"]
    k = d["t3_scale_retrieval"]["k"]
    s.dispatch()
    if can_index:
        if not s.index_built and g.theta.get("index_build", 1.0) >= 1.0:
            s._charge(s.cm["index_build_work"], "acquisition")
            s.index_built = True
        s._charge(s.cm["index_query_work"] * s.fm["retrieve"] * k)
        result("t3_scale_retrieval", True)
    elif can_assoc:
        s._charge(s.cm["probe_work"] * k * s.fm["retrieve"])
        s._charge(s.cm["consistency_work"], "verification")
        result("t3_scale_retrieval", True)
    else:
        s._charge(s.cm["scan_item_work"] * items)
        result("t3_scale_retrieval", True)
    s.end_epoch()

    # ---- family t3_conflict_refusal: contradictory fact pairs; the only
    # correct behaviour is a scoped refusal.  Persistence without a checker
    # transfers the contradiction (harmful).
    pairs = int(d["t3_conflict_refusal"]["pairs"])
    for _ in range(pairs):
        s.dispatch()
        if can_check or g.F_arch == "hierarchical_fibred":
            s._charge(s.cm["consistency_work"] * (
                0.4 if g.F_arch == "hierarchical_fibred" else 1.0), "verification")
            s.correct_refusals += 1
            result("t3_conflict_refusal", True)
        elif s.methods > 0 or "episodic_memory" in s.types:
            s._charge(s.cm["reuse_work"])
            s.harmful_transfers += 1
            result("t3_conflict_refusal", False)
        else:
            s._charge(s.cm["rule_fire_work"])
            s.harmful_transfers += 1
            result("t3_conflict_refusal", False)
    s.end_epoch()

    # ---- family t3_novel_variant: schema application to novel variant
    # classes at key-derived depth; schemas win cheaply, rules re-derive,
    # planners pay scaled expansions.
    variants = int(d["t3_novel_variant"]["variants"])
    vdepth = d["t3_novel_variant"]["depth_mult"]
    for _ in range(variants):
        s.dispatch()
        if can_schema:
            if s.schemas == 0:
                s._charge(s.cm["abstraction_work"], "acquisition")
                s.schemas += 1
            s._charge(s.cm["schema_apply_work"] * vdepth)
            result("t3_novel_variant", True)
        elif can_rule:
            s._charge(s.cm["rule_fire_work"] * vdepth)
            result("t3_novel_variant", True)
        elif can_plan and s.cm["w4_expansions"] * vdepth <= s.budget:
            s._charge(s.cm["w4_expansions"] * vdepth * s.cm["expansion_work"])
            s.expansions += int(s.cm["w4_expansions"] * vdepth)
            result("t3_novel_variant", True)
        else:
            result("t3_novel_variant", False)
    s.end_epoch()

    # ---- family t3_interrupted_plan: plan in flight, facts revoked
    # mid-plan (frozen revocation charging), re-derive at key-derived
    # depth.  R=none yields stale answers (gate-breaking, as everywhere).
    interrupts = int(d["t3_interrupted_plan"]["interrupts"])
    redepth = d["t3_interrupted_plan"]["redepth"]
    for _ in range(interrupts):
        s.dispatch()
        s._charge(s.cm["closure_work"] * s.fm["retrieve"], "reasoning")
        if g.R == "none":
            s.stale_answers += 1
            result("t3_interrupted_plan", False)
            continue
        if g.R == "full_rescan":
            s._charge(s.cm["rescan_work"] * s.cm["revocation_facts"], "revision")
        else:
            s._charge(s.cm["cone_reopen_work"] * s.fm["reopen"] * 2, "revision")
        need = redepth * s.em["expansion"]
        if can_rule:
            s._charge(s.cm["rule_fire_work"])
            result("t3_interrupted_plan", True)
        elif can_plan and need <= s.budget:
            s._charge(need * s.cm["expansion_work"])
            s.expansions += int(need)
            result("t3_interrupted_plan", True)
        else:
            s._charge(need * s.cm["expansion_work"] * 0.5)
            result("t3_interrupted_plan", False)
    s.end_epoch()

    solved_frac = s.solved / max(1, s.total)
    ev = {
        "ecology_id": "GSHeldoutT3V1",
        "t3_key": key,
        "families": list(T3_FAMILIES),
        "draw": d,
        "solved": s.solved, "total_tasks": s.total,
        "solved_fraction": round(solved_frac, 6),
        "work_total": round(s.work, 6),
        "persistent_bytes": round(s.persistent_bytes(), 6),
        "probes": s.probes, "expansions": s.expansions,
        "correct_refusals": s.correct_refusals,
        "harmful_transfers": s.harmful_transfers,
        "stale_answers": s.stale_answers,
        "per_family": {kk: dict(vv) for kk, vv in sorted(per_family.items())},
        "tier": "T3",
    }
    return ev


def evaluate_t3(genome, key: str) -> Dict[str, Any]:
    """Held-out T3 evaluation with the frozen hard gates applied verbatim
    (same gate code path as T0/T1/T2 — floors unchanged)."""
    org = compile_genome(genome)
    ev = run_t3(org, key)
    gates = hard_gate_report(org, ev)
    return {
        "genotype_digest": org.genotype_digest,
        "phenotype_digest": org.phenotype_digest,
        "gates": gates,
        "feasible": gates["feasible"],
        "evaluation": ev,
        "tier": "T3",
        "capability_floor": CAPABILITY_FLOOR_V1,
    }

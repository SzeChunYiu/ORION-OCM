"""Issue #165 H4 exact-revocation capsule.

Uses production ``ocm.kso`` warrant / prune / compose / procedures / extraction
indexes. Does not edit ``src/``. Planted oracle only. Distinct from H3 atom
liveness at ``research/h3-local-revision-v1/``. Not a programme-wide H4 close.
"""
from __future__ import annotations

import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Hashable, Iterable

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from ocm.kso.admission import (
    CertificateKind,
    GovernedSpace,
    admit,
    compose,
    ks_S2_composition,
    mutant_compose_merge,
)
from ocm.kso.extraction_index import ExtractionIndex, ExtractionRun
from ocm.kso.extraction_indexed import reacting_subgraph_from_support_indexed
from ocm.kso.firing import Enabling, enabling_verdict
from ocm.kso.navigation import fixed_point, seed_vector
from ocm.kso.procedures import Alt, If, LearnedProcedure, Prim, Reading, Test, run
from ocm.kso.procedures import mutant_static_reading_for_trace_claim
from ocm.kso.revocation import prune, reopening_report, strip_all_warrants
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace, TypedRejection
from ocm.kso.warrant import CannotCheck, Liveness, WarrantProfile, live

SCHEMA = "ocm.h4.exact-revocation.v1"
ALPHA = Fraction(1, 3)
THRESHOLD = Fraction(1, 1000)

EV_SRC = "ev:src"
EV_ALT = "ev:alt"
EV_UNREL = "ev:unrel"

GOAL = "goal"
SRC = "src_skill"
ALT = "alt_skill"
UNREL = "unrel_skill"
COMP_SRC = "composed_from_src"
COMP_DEEP = "composed_deep"
COMP_ALT = "composed_from_alt"
COMP_UNREL = "composed_from_unrel"
COMP_BOTH = "composed_src_and_unrel"

MUST_REMOVE = frozenset({SRC, COMP_SRC, COMP_DEEP, COMP_BOTH})
MUST_KEEP = frozenset({GOAL, ALT, UNREL, COMP_ALT, COMP_UNREL})
MUST_DISABLE_COMPOSE = frozenset(
    {f"compose:{COMP_SRC}", f"compose:{COMP_DEEP}", f"compose:{COMP_BOTH}"}
)
MUST_KEEP_COMPOSE = frozenset({f"compose:{COMP_ALT}", f"compose:{COMP_UNREL}"})


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def _src_prim() -> Prim:
    return Prim("m-src", lambda v: ("src", v), (frozenset({EV_SRC}),))


def _alt_prim() -> Prim:
    return Prim("m-alt", lambda v: ("alt", v), (frozenset({EV_ALT}),))


def _unrel_prim() -> Prim:
    return Prim("m-unrel", lambda v: ("unrel", v), (frozenset({EV_UNREL}),))


def plant_methods() -> dict[str, LearnedProcedure]:
    """Methods are procedure objects with recorded readings, not KSO atoms."""
    src, alt, unrel = _src_prim(), _alt_prim(), _unrel_prim()
    even = Test("even", lambda v: v % 2 == 0)
    return {
        "method_src": LearnedProcedure.static("method_src", src),
        "method_alt": LearnedProcedure.static("method_alt", Alt(src, alt, certified=True)),
        "method_unrel": LearnedProcedure.static("method_unrel", unrel),
        "method_trace": LearnedProcedure(
            "method_trace", If(even, src, unrel), Reading.TRACE, WarrantProfile.one().lower
        ),
    }


def plant_base() -> KnowledgeSpace:
    """Skills and goal before composition (cache-identity baseline)."""
    return KnowledgeSpace(
        (
            Atom(GOAL, "goal"),
            Atom(SRC, "procedure", WarrantProfile.of({EV_SRC}), content_ref="method_src"),
            Atom(ALT, "procedure", WarrantProfile.of({EV_SRC}, {EV_ALT}), content_ref="method_alt"),
            Atom(UNREL, "procedure", WarrantProfile.of({EV_UNREL}), content_ref="method_unrel"),
        ),
        (
            Hyperedge("g-src", (GOAL,), (SRC,), "DEPENDENCE"),
            Hyperedge("g-alt", (GOAL,), (ALT,), "DEPENDENCE"),
            Hyperedge("g-unrel", (GOAL,), (UNREL,), "DEPENDENCE"),
        ),
    )


def plant_world() -> KnowledgeSpace:
    ks = plant_base()
    ks, _ = compose(ks, [SRC], COMP_SRC, executable_ref="method_src")
    ks, _ = compose(ks, [COMP_SRC], COMP_DEEP, executable_ref="method_src")
    ks, _ = compose(ks, [ALT], COMP_ALT, executable_ref="method_alt")
    ks, _ = compose(ks, [UNREL], COMP_UNREL, executable_ref="method_unrel")
    ks, _ = compose(ks, [SRC, UNREL], COMP_BOTH, executable_ref="method_src")
    return ks


def enabling_map(
    ks: KnowledgeSpace, act: dict[str, Fraction], revoked: Iterable[Hashable] = ()
) -> dict[str, str]:
    rv = frozenset(revoked)
    return {
        e.edge_id: enabling_verdict(ks, e, act, THRESHOLD, rv).enabling.value
        for e in ks.hyperedges
    }


def mutant_stale_liveness_memo(
    ks: KnowledgeSpace,
    index: ExtractionIndex,
    revoked: Iterable[Hashable],
    stale_live: dict[str, bool],
) -> dict[str, bool]:
    """Planted: reuse a previous query's atom-liveness memo under a new revoked set."""
    run = ExtractionRun(ks, index, revoked)
    run._atom_live.update(stale_live)
    return {atom_id: run.live_atom(atom_id) for atom_id in ks.ids}


def index_mismatch_reason(index: ExtractionIndex, ks: KnowledgeSpace) -> str | None:
    try:
        index.check(ks)
    except CannotCheck as exc:
        return str(exc)
    return None


def relearn_on_pruned(pruned_ks: KnowledgeSpace) -> KnowledgeSpace:
    """Re-admit the source skill onto a store that already dropped it, then compose."""
    src = Atom(SRC, "procedure", WarrantProfile.of({EV_SRC}), content_ref="method_src")
    edge = Hyperedge("g-src", (GOAL,), (SRC,), "DEPENDENCE")
    ks, _ = admit(pruned_ks, src, (edge,), CertificateKind.INSTRUCTION)
    ks, _ = compose(ks, [SRC], COMP_SRC, executable_ref="method_src")
    ks, _ = compose(ks, [COMP_SRC], COMP_DEEP, executable_ref="method_src")
    ks, _ = compose(ks, [SRC, UNREL], COMP_BOTH, executable_ref="method_src")
    return ks


def run_study() -> dict[str, Any]:
    base = plant_base()
    # Materialize structural caches on the pre-composition snapshot.
    _ = base.outgoing_edges(SRC)
    _ = base.ids
    base_index = ExtractionIndex(base)

    ks = plant_world()
    methods = plant_methods()
    seed = seed_vector(ks, {GOAL: Fraction(1)})
    revoked = (EV_SRC,)

    pre_live = {a.atom_id: a.liveness(()).value for a in ks.atoms}
    pre_act = fixed_point(ks, seed, ALPHA)
    pre_en = enabling_map(ks, pre_act)
    pre_warrants = {a.atom_id: a.warrant for a in ks.atoms}

    pruned = prune(ks, revoked)
    post_live = {a.atom_id: a.liveness(revoked).value for a in ks.atoms}
    post_act = fixed_point(ks, seed, ALPHA, revoked=revoked)
    post_en = enabling_map(ks, post_act, revoked)
    report = reopening_report(ks, (), revoked, seed=seed)

    # --- source removal (physical prune, not DEAD-in-place) ---
    removed_atoms = frozenset(pruned.removed_atoms)
    kept_ids = frozenset(pruned.space.ids)
    source_removed = (
        MUST_REMOVE <= removed_atoms
        and MUST_REMOVE.isdisjoint(kept_ids)
        and MUST_KEEP <= kept_ids
        and MUST_REMOVE <= frozenset(ks.ids)  # original space still holds them
        and MUST_DISABLE_COMPOSE <= pruned.removed_edges
        and MUST_KEEP_COMPOSE.isdisjoint(pruned.removed_edges)
    )

    # --- warrant invalidation (evaluation, not rewrite) ---
    src_w = ks.atom(SRC).warrant
    both_w = ks.atom(COMP_BOTH).warrant
    alt_w = ks.atom(ALT).warrant
    warrants_not_rewritten = all(
        ks.atom(atom_id).warrant is pre_warrants[atom_id] for atom_id in ks.ids
    )
    src_eval_dead = src_w.liveness(revoked) is Liveness.DEAD and not live(src_w.lower, revoked)
    src_evidence_retained = EV_SRC in src_w.evidence
    both_is_meet = both_w == src_w.meet(ks.atom(UNREL).warrant)
    both_eval_dead = both_w.liveness(revoked) is Liveness.DEAD
    alt_eval_live = alt_w.liveness(revoked) is Liveness.LIVE
    stripped = strip_all_warrants(ks)
    strip_is_collateral = (
        not stripped.atom(ALT).is_live(())
        and not stripped.atom(UNREL).is_live(())
        and not stripped.atom(GOAL).is_live(())
    )
    warrant_exact = (
        warrants_not_rewritten
        and src_eval_dead
        and src_evidence_retained
        and both_is_meet
        and both_eval_dead
        and alt_eval_live
        and strip_is_collateral
    )

    # --- method invalidation (reading-gated; not atom liveness) ---
    m_src = methods["method_src"]
    m_alt = methods["method_alt"]
    m_unrel = methods["method_unrel"]
    m_trace = methods["method_trace"]
    src_method_dead = m_src.liveness_for_input(0, revoked) is Liveness.DEAD
    alt_method_live = m_alt.liveness_for_input(0, revoked) is Liveness.LIVE
    unrel_method_live = m_unrel.liveness_for_input(0, revoked) is Liveness.LIVE
    trace_even_dead = m_trace.liveness_for_input(2, revoked) is Liveness.DEAD
    trace_odd_live = m_trace.liveness_for_input(3, revoked) is Liveness.LIVE
    static_mutant_kills_odd = (
        mutant_static_reading_for_trace_claim(m_trace, 3, revoked) is Liveness.DEAD
    )
    # run() itself does not refuse; the recorded reading is the gate.
    dead_method_still_runs = run(m_src.proc, 0).output == ("src", 0)
    method_exact = (
        src_method_dead
        and alt_method_live
        and unrel_method_live
        and trace_even_dead
        and trace_odd_live
        and static_mutant_kills_odd
        and dead_method_still_runs
        and m_src.reading is Reading.STATIC
        and m_trace.reading is Reading.TRACE
    )

    # --- cache invalidation ---
    index = ExtractionIndex(ks)
    rho = {atom_id: 1.0 for atom_id in ks.ids}
    sg_pre, work_pre = reacting_subgraph_from_support_indexed(
        ks, rho, (GOAL,), revoked=(), index=index, with_work=True
    )
    sg_post, work_post = reacting_subgraph_from_support_indexed(
        ks, rho, (GOAL,), revoked=revoked, index=index, with_work=True
    )
    prune_mismatch = index_mismatch_reason(index, pruned.space)
    compose_mismatch = index_mismatch_reason(base_index, ks)
    identity_mismatch = index_mismatch_reason(index, plant_world())
    # Same-space index remains valid; liveness is re-evaluated per query.
    same_space_ok = index_mismatch_reason(index, ks) is None
    post_excludes_removed = MUST_REMOVE.isdisjoint(sg_post.atoms)
    pre_includes_src_chain = {SRC, COMP_SRC, COMP_DEEP, COMP_BOTH} <= sg_pre.atoms
    alt_cached_post = {ALT, COMP_ALT} <= sg_post.atoms
    unrel_cached_post = {UNREL, COMP_UNREL} <= sg_post.atoms
    post_rechecks_warrants = work_post.atom_warrant_checks > 0
    fresh_run = ExtractionRun(ks, index, revoked)
    fresh_live = {atom_id: fresh_run.live_atom(atom_id) for atom_id in ks.ids}
    stale_live = mutant_stale_liveness_memo(
        ks, index, revoked, {atom_id: True for atom_id in ks.ids}
    )
    stale_keeps_src = stale_live[SRC] is True and stale_live[COMP_BOTH] is True
    fresh_drops_src = fresh_live[SRC] is False and fresh_live[COMP_BOTH] is False
    # Structural caches do not leak across compose/replace.
    base_src_out = {e.edge_id for e in base.outgoing_edges(SRC)}
    world_src_out = {e.edge_id for e in ks.outgoing_edges(SRC)}
    cache_not_inherited = (
        f"compose:{COMP_SRC}" not in base_src_out and f"compose:{COMP_SRC}" in world_src_out
    )
    cache_exact = (
        prune_mismatch == "EXTRACTION_INDEX_SNAPSHOT_MISMATCH"
        and compose_mismatch == "EXTRACTION_INDEX_SNAPSHOT_MISMATCH"
        and identity_mismatch == "EXTRACTION_INDEX_SNAPSHOT_MISMATCH"
        and same_space_ok
        and post_excludes_removed
        and pre_includes_src_chain
        and alt_cached_post
        and unrel_cached_post
        and post_rechecks_warrants
        and stale_keeps_src
        and fresh_drops_src
        and cache_not_inherited
    )

    # --- composition reopening ---
    compose_disabled = all(post_en.get(eid) == Enabling.DISABLED.value for eid in MUST_DISABLE_COMPOSE)
    compose_kept = all(post_en.get(eid) == Enabling.ENABLED.value for eid in MUST_KEEP_COMPOSE)
    both_reopens = COMP_BOTH in report.reopen
    src_chain_reopens = {SRC, COMP_SRC, COMP_DEEP} <= report.reopen
    s2_holds = ks_S2_composition(GovernedSpace(ks))
    merged = mutant_compose_merge(plant_base(), [SRC, UNREL], "mutant_both")
    mutant_join_survives = merged.atom("mutant_both").is_live(revoked)
    both_meet_dies = not ks.atom(COMP_BOTH).is_live(revoked)
    composition_exact = (
        compose_disabled
        and compose_kept
        and both_reopens
        and src_chain_reopens
        and s2_holds
        and mutant_join_survives
        and both_meet_dies
        and COMP_BOTH in pruned.removed_atoms
        and ALT not in report.reopen
    )

    # --- alternate-support preservation ---
    alt_atom_live = ks.atom(ALT).is_live(revoked) and ks.atom(COMP_ALT).is_live(revoked)
    alt_in_pruned = {ALT, COMP_ALT} <= kept_ids
    alt_method_ok = alt_method_live
    both_supports_kill_alt = (
        not ks.atom(ALT).is_live((EV_SRC, EV_ALT))
        and not ks.atom(COMP_ALT).is_live((EV_SRC, EV_ALT))
        and m_alt.liveness_for_input(0, (EV_SRC, EV_ALT)) is Liveness.DEAD
    )
    dual_revoke_prunes_alt = ALT in prune(ks, (EV_SRC, EV_ALT)).removed_atoms
    alt_exact = (
        alt_atom_live
        and alt_in_pruned
        and alt_method_ok
        and both_supports_kill_alt
        and dual_revoke_prunes_alt
        and trace_odd_live
        and unrel_method_live
        and {ALT, COMP_ALT} <= report.unaffected
    )

    # --- relearning / restoration ---
    restore_live = {a.atom_id: a.liveness(()).value for a in ks.atoms}
    restore_act = fixed_point(ks, seed, ALPHA, revoked=())
    restore_en = enabling_map(ks, restore_act)
    gated_restore = restore_live == pre_live and restore_act == pre_act and restore_en == pre_en
    prune_empty = prune(ks, ())
    empty_prune_keeps = frozenset(prune_empty.space.ids) == frozenset(ks.ids)
    # Pruned store cannot resurrect by emptying revoked: the atoms are gone.
    pruned_restore_act = fixed_point(pruned.space, seed_vector(pruned.space, {GOAL: Fraction(1)}), ALPHA)
    pruned_lacks_src = SRC not in pruned.space.ids
    recompose_rejected = False
    try:
        compose(pruned.space, [SRC], "relearned_head")
    except TypedRejection as exc:
        recompose_rejected = exc.code == "UNKNOWN_ATOM"
    relearned = relearn_on_pruned(pruned.space)
    relearned_warrants = (
        relearned.atom(SRC).warrant == src_w
        and relearned.atom(COMP_SRC).warrant == ks.atom(COMP_SRC).warrant
        and relearned.atom(COMP_DEEP).warrant == ks.atom(COMP_DEEP).warrant
        and relearned.atom(COMP_BOTH).warrant == both_w
        and relearned.atom(ALT).warrant == alt_w
    )
    relearned_live = all(relearned.atom(x).is_live(()) for x in (*MUST_REMOVE, *MUST_KEEP))
    method_restore = (
        m_src.liveness_for_input(0, ()) is Liveness.LIVE
        and run(m_src.proc, 0).output == ("src", 0)
        and m_trace.liveness_for_input(2, ()) is Liveness.LIVE
    )
    original_index_still_valid = index_mismatch_reason(index, ks) is None
    restoration_exact = (
        gated_restore
        and empty_prune_keeps
        and pruned_lacks_src
        and recompose_rejected
        and relearned_warrants
        and relearned_live
        and method_restore
        and original_index_still_valid
        and GOAL in pruned_restore_act
    )

    boxes = {
        "H4/001-source_removal": {
            "text": "source removal",
            "status": "EARNED_AT_SCOPE" if source_removed else "OPEN",
            "removed_atoms": sorted(removed_atoms),
            "kept_ids": sorted(kept_ids),
            "must_remove": sorted(MUST_REMOVE),
            "must_keep": sorted(MUST_KEEP),
            "removed_compose_edges": sorted(MUST_DISABLE_COMPOSE & pruned.removed_edges),
            "original_space_still_holds_source": SRC in ks.ids,
        },
        "H4/002-warrant_invalidation": {
            "text": "warrant invalidation",
            "status": "EARNED_AT_SCOPE" if warrant_exact else "OPEN",
            "warrants_not_rewritten": warrants_not_rewritten,
            "src_eval_dead": src_eval_dead,
            "src_evidence_retained": src_evidence_retained,
            "composed_both_is_meet": both_is_meet,
            "composed_both_eval_dead": both_eval_dead,
            "alt_eval_live": alt_eval_live,
            "strip_all_warrants_is_collateral": strip_is_collateral,
        },
        "H4/003-method_invalidation": {
            "text": "method invalidation",
            "status": "EARNED_AT_SCOPE" if method_exact else "OPEN",
            "src_static_dead": src_method_dead,
            "alt_certified_live": alt_method_live,
            "unrel_static_live": unrel_method_live,
            "trace_even_src_branch_dead": trace_even_dead,
            "trace_odd_unrel_branch_live": trace_odd_live,
            "static_mutant_kills_live_trace_branch": static_mutant_kills_odd,
            "run_does_not_refuse_dead_method": dead_method_still_runs,
        },
        "H4/004-cache_invalidation": {
            "text": "cache invalidation",
            "status": "EARNED_AT_SCOPE" if cache_exact else "OPEN",
            "prune_snapshot_mismatch": prune_mismatch,
            "compose_snapshot_mismatch": compose_mismatch,
            "identity_snapshot_mismatch": identity_mismatch,
            "same_space_index_reusable": same_space_ok,
            "post_query_excludes_removed": post_excludes_removed,
            "post_query_rechecks_warrants": post_rechecks_warrants,
            "stale_memo_keeps_src": stale_keeps_src,
            "fresh_memo_drops_src": fresh_drops_src,
            "structural_cache_not_inherited_across_compose": cache_not_inherited,
            "work_pre_atom_warrant_checks": work_pre.atom_warrant_checks,
            "work_post_atom_warrant_checks": work_post.atom_warrant_checks,
        },
        "H4/005-composition_reopening": {
            "text": "composition reopening",
            "status": "EARNED_AT_SCOPE" if composition_exact else "OPEN",
            "compose_disabled": sorted(eid for eid in MUST_DISABLE_COMPOSE if post_en.get(eid) == Enabling.DISABLED.value),
            "compose_kept": sorted(eid for eid in MUST_KEEP_COMPOSE if post_en.get(eid) == Enabling.ENABLED.value),
            "reopen": sorted(report.reopen),
            "composed_both_reopens_despite_live_unrel_tail": both_reopens,
            "ks_S2_composition": s2_holds,
            "mutant_join_compose_survives_src_revoke": mutant_join_survives,
        },
        "H4/006-alternate_support_preservation": {
            "text": "alternate-support preservation",
            "status": "EARNED_AT_SCOPE" if alt_exact else "OPEN",
            "alt_atom_live": alt_atom_live,
            "alt_kept_in_pruned_store": alt_in_pruned,
            "alt_method_live": alt_method_ok,
            "both_supports_revoked_kills_alt": both_supports_kill_alt,
            "dual_revoke_prunes_alt": dual_revoke_prunes_alt,
            "unaffected": sorted(report.unaffected),
            "alt_outside_src_composition_cone": {ALT, COMP_ALT} <= report.unaffected,
        },
        "H4/007-relearning_restoration": {
            "text": "relearning/restoration",
            "status": "EARNED_AT_SCOPE" if restoration_exact else "OPEN",
            "gated_restore_on_original_space": gated_restore,
            "empty_revoke_prune_keeps_all": empty_prune_keeps,
            "pruned_store_lacks_source": pruned_lacks_src,
            "recompose_on_pruned_store_rejected": recompose_rejected,
            "relearned_warrants_match": relearned_warrants,
            "relearned_atoms_live": relearned_live,
            "methods_live_after_empty_revoke": method_restore,
        },
    }

    earned = sorted(k for k, v in boxes.items() if v["status"] == "EARNED_AT_SCOPE")
    open_boxes = sorted(k for k, v in boxes.items() if v["status"] == "OPEN")
    if len(earned) == len(boxes):
        terminal = "PARENT_SUFFICIENT_AT_PLANTED_EXACT_REVOCATION_SCOPE"
    elif earned:
        terminal = "H4_PARTIAL_AT_PLANTED_EXACT_REVOCATION_SCOPE"
    else:
        terminal = "H4_EXACT_REVOCATION_GATE_FAILED"

    return {
        "schema": SCHEMA,
        "issue": 165,
        "head": git_head(),
        "terminal": terminal,
        "programme_wide_close": False,
        "production_src_edited": False,
        "h3_capsule_untouched": True,
        "parent": (
            "production ocm.kso prune/warrant/compose/procedures/extraction-index "
            "(ATMS labels, JTMS reopening, KAT readings, snapshot-bound indexes)"
        ),
        "parent_sufficient": terminal.startswith("PARENT_SUFFICIENT"),
        "claim_ceiling": (
            "Planted-oracle H4 exact revocation on methods, caches, and compositions. "
            "Distinct from H3 atom-liveness gating: prune removes dead structure, "
            "warrant labels are evaluated not rewritten, LearnedProcedure readings "
            "gate use, ExtractionIndex refuses replaced snapshots, and a pruned "
            "store requires re-admission. Not programme-wide H4 close. Not H3/H5."
        ),
        "boxes": boxes,
        "earned": earned,
        "open": open_boxes,
        "cannot_check": sorted(
            k for k, v in boxes.items() if str(v["status"]).startswith("CANNOT_CHECK")
        ),
        "world": {
            "atoms": list(ks.ids),
            "revoked": [EV_SRC],
            "pre_liveness": pre_live,
            "post_liveness": post_live,
            "pruned_ids": sorted(kept_ids),
            "removed_atoms": sorted(removed_atoms),
            "removed_edges": sorted(pruned.removed_edges),
            "reopening": report.as_dict(),
            "enabled_pre": sorted(
                eid for eid, v in pre_en.items() if v == Enabling.ENABLED.value
            ),
            "enabled_post": sorted(
                eid for eid, v in post_en.items() if v == Enabling.ENABLED.value
            ),
            "methods": {
                name: {"reading": lp.reading.value, "name": lp.name}
                for name, lp in methods.items()
            },
        },
        "not_issued": [
            "PROGRAMME_WIDE_H4_CLOSE",
            "H4_RESIDUAL_OVER_TMS_SKILL_LIBRARY_INDEX",
            "H3_OVERWRITE",
            "PROGRAMME_WIDE_H3_CLOSE",
            "H5_LIFETIME_ECONOMICS",
            "INDUCED_DEPENDENCY_PRECISION_RECALL",
            "M11_M12_SCIENTIFIC_INHERITANCE",
        ],
    }


def _jsonable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, frozenset):
        return sorted(_jsonable(v) for v in value)
    return value


def main(out: Path) -> dict[str, Any]:
    result = _jsonable(run_study())
    out.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    out.write_text(text)
    capsule = Path(__file__).resolve().parent / "RESULT.json"
    if out.resolve() != capsule.resolve():
        capsule.write_text(text)
    print(json.dumps({"terminal": result["terminal"], "earned": result["earned"]}, indent=2))
    return result


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "RESULT.json"
    main(target)

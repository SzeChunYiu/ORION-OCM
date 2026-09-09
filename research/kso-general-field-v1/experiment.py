"""Issue #165 §8 General Epistemic Field capsule.

Uses production ``ocm.kso`` types / warrant / compose / navigation / revocation.
Does not edit ``src/``. Planted oracle only. Does not mint a second truth store.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from ocm.kso.admission import compose
from ocm.kso.navigation import fixed_point, seed_vector
from ocm.kso.revocation import impact_cone, reopening_report
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace
from ocm.kso.types import (
    CORE_ATOM_TYPES,
    DEFAULT_REGISTRY,
    Authority,
    RelationSpec,
    TypeRegistry,
    mutant_authority_max,
)
from ocm.kso.warrant import Liveness, WarrantProfile, all_profiles, powerset

SCHEMA = "ocm.kso.general-field.v1"
ALPHA = Fraction(1, 3)

LANGUAGE_TYPES = ("lexeme", "utterance", "construction")
MATH_TYPES = ("theorem", "lemma", "axiom")
SCIENCE_TYPES = ("protocol", "experiment", "measurement", "hypothesis")
EXTRA_ATOM_TYPES = LANGUAGE_TYPES + MATH_TYPES + SCIENCE_TYPES

EV_SRC = "ev:src"
EV_SAID = "ev:said"
EV_METER = "ev:meter"
EV_KERNEL = "ev:kernel"
EV_METER2 = "ev:meter2"
EV_LEX = "ev:lex"
EV_SIM = "ev:sim"
EV_TWIN = "ev:twin"
EV_CORR = "ev:corr"
EV_UNREL = "ev:unrel"

FACT = "fact"
LANG_OF_FACT = "lang_of_fact"
MATH_OF_FACT = "math_of_fact"
SCI_OF_FACT = "sci_of_fact"
SAID = "said"
WORLD = "world"
SAID_AND_WORLD = "said_and_world"
PROVED = "proved"
MEASURED = "measured"
APPLICABILITY = "applicability"
QUERY = "q"
CAT = "lex_cat"
KAT = "lex_kat"
TWIN = "lex_twin"
IDENT = "ident_cat"
COLOR = "color"
GOAL = "goal"


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def production_src_edited() -> bool:
    try:
        out = subprocess.check_output(
            ["git", "diff", "--", "src"], cwd=REPO, text=True
        )
    except (OSError, subprocess.CalledProcessError):
        return True
    return bool(out.strip())


def snapshot_default_registry() -> dict[str, list[str]]:
    return {
        "atom_types": sorted(DEFAULT_REGISTRY.atom_types),
        "relation_types": sorted(DEFAULT_REGISTRY.relation_types),
    }


def fresh_registry_with_extras() -> TypeRegistry:
    """Local registry. Never mutate ``DEFAULT_REGISTRY``."""
    reg = TypeRegistry()
    for name in EXTRA_ATOM_TYPES:
        reg.register_atom_type(name)
    reg.register_relation_type(RelationSpec("SIMILAR_TO", dependency=False))
    return reg


def warrant_algebra_fingerprint() -> dict[str, Any]:
    """Join / meet / liveness table on n=3 certified profiles. Type-free."""
    profiles = [WarrantProfile.certified(p) for p in all_profiles(3)]
    join_meet: list[list[Any]] = []
    for i, a in enumerate(profiles):
        for j, b in enumerate(profiles):
            joined = a.join(b)
            met = a.meet(b)
            join_meet.append([i, j, joined.as_dict(), met.as_dict()])
    live_rows: list[list[Any]] = []
    for i, a in enumerate(profiles):
        for revoked in powerset(range(3)):
            live_rows.append([i, sorted(revoked), a.liveness(revoked).value])
    payload = {
        "n_profiles": len(profiles),
        "n_join_meet": len(join_meet),
        "n_liveness": len(live_rows),
        "join_meet": join_meet,
        "liveness": live_rows,
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return {
        "n_profiles": len(profiles),
        "n_join_meet": len(join_meet),
        "n_liveness": len(live_rows),
        "sha256": hashlib.sha256(blob.encode()).hexdigest(),
    }


def compose_warrant_for_type(atom_type: str, registry: TypeRegistry) -> dict[str, Any]:
    ks = KnowledgeSpace(
        (
            Atom("a", atom_type, WarrantProfile.of({0})),
            Atom("b", atom_type, WarrantProfile.of({1}, {2})),
        ),
        (),
        registry,
    )
    ks, rec = compose(ks, ["a", "b"], "h", head_type=atom_type)
    return {
        "head_type": atom_type,
        "warrant": rec.warrant.as_dict(),
        "authority": rec.authority.as_dict(),
        "liveness_empty": rec.warrant.liveness(()).value,
        "liveness_revoke_0": rec.warrant.liveness((0,)).value,
        "liveness_revoke_1_2": rec.warrant.liveness((1, 2)).value,
    }


def unregistered_rejected(atom_type: str, registry: TypeRegistry | None = None) -> bool:
    try:
        KnowledgeSpace((Atom("x", atom_type),), (), registry or TypeRegistry())
    except Exception:
        return True
    return False


def plant_world() -> KnowledgeSpace:
    reg = fresh_registry_with_extras()
    ks = KnowledgeSpace(
        (
            Atom(GOAL, "goal"),
            Atom(FACT, "claim", WarrantProfile.of({EV_SRC}), Authority.of(world_truth=1)),
            Atom(SAID, "utterance", WarrantProfile.of({EV_SAID}), Authority.of(speaker=1)),
            Atom(WORLD, "observation", WarrantProfile.of({EV_METER}), Authority.of(world_truth=1)),
            Atom(PROVED, "theorem", WarrantProfile.of({EV_KERNEL}), Authority.of(formal_proof=1)),
            Atom(
                MEASURED,
                "observation",
                WarrantProfile.of({EV_METER2}),
                Authority.of(empirical=1),
            ),
            Atom(QUERY, "query_seed", WarrantProfile.one()),
            Atom(
                CAT,
                "lexeme",
                WarrantProfile.of({EV_LEX}),
                Authority.of(speaker=1),
                content_ref="cat",
            ),
            Atom(
                KAT,
                "lexeme",
                WarrantProfile.of({EV_SIM}),
                Authority.of(speaker=1),
                content_ref="kat",
            ),
            Atom(
                TWIN,
                "lexeme",
                WarrantProfile.of({EV_TWIN}),
                Authority.of(speaker=1),
                content_ref="cat",
            ),
            Atom(COLOR, "claim", WarrantProfile.of({EV_UNREL})),
        ),
        (
            Hyperedge("g-fact", (GOAL,), (FACT,), "DEPENDENCE"),
            Hyperedge("g-color", (GOAL,), (COLOR,), "DEPENDENCE"),
            Hyperedge("g-q", (GOAL,), (QUERY,), "DEPENDENCE"),
            Hyperedge("sim-cat", (QUERY,), (CAT,), "SIMILAR_TO"),
            Hyperedge("sim-kat", (QUERY,), (KAT,), "SIMILAR_TO"),
        ),
        reg,
    )
    ks, _ = compose(ks, [FACT], LANG_OF_FACT, head_type="utterance")
    ks, _ = compose(ks, [FACT], MATH_OF_FACT, head_type="theorem")
    ks, _ = compose(ks, [FACT], SCI_OF_FACT, head_type="protocol")
    ks, _ = compose(ks, [SAID, WORLD], SAID_AND_WORLD, head_type="claim")
    ks, _ = compose(ks, [PROVED, MEASURED], APPLICABILITY, head_type="hypothesis")
    ks, _ = compose(
        ks,
        [CAT, TWIN],
        IDENT,
        head_type="lexeme",
        bridge_warrant=WarrantProfile.of({EV_CORR}),
    )
    return ks


def mutant_identify_by_content_ref(ks: KnowledgeSpace) -> dict[str, dict[str, Any]]:
    """Hostile: join warrants of atoms that share ``content_ref`` (no correspondence)."""
    groups: dict[str, list[Atom]] = {}
    for atom in ks.atoms:
        if atom.content_ref:
            groups.setdefault(atom.content_ref, []).append(atom)
    merged: dict[str, dict[str, Any]] = {}
    for ref, atoms in groups.items():
        w = WarrantProfile.zero()
        for atom in atoms:
            w = w.join(atom.warrant)
        for atom in atoms:
            merged[atom.atom_id] = {"content_ref": ref, "warrant": w.as_dict()}
    return merged


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


def run_study() -> dict[str, Any]:
    default_before = snapshot_default_registry()
    fingerprint_before = warrant_algebra_fingerprint()

    core_reg = TypeRegistry()
    extra_reg = fresh_registry_with_extras()
    claim_compose = compose_warrant_for_type("claim", core_reg)
    language_composes = {
        t: compose_warrant_for_type(t, extra_reg) for t in LANGUAGE_TYPES
    }
    math_composes = {t: compose_warrant_for_type(t, extra_reg) for t in MATH_TYPES}
    science_composes = {
        t: compose_warrant_for_type(t, extra_reg) for t in SCIENCE_TYPES
    }
    fingerprint_after_register = warrant_algebra_fingerprint()

    extra_types_registered = all(t in extra_reg.atom_types for t in EXTRA_ATOM_TYPES)
    similar_not_dependency = "SIMILAR_TO" not in extra_reg.dependency_types
    unregistered_core = unregistered_rejected("vibe", core_reg)
    unregistered_extra = unregistered_rejected("vibe", extra_reg)
    language_warrants_match = all(
        language_composes[t]["warrant"] == claim_compose["warrant"]
        and language_composes[t]["liveness_empty"] == claim_compose["liveness_empty"]
        and language_composes[t]["liveness_revoke_0"] == claim_compose["liveness_revoke_0"]
        and language_composes[t]["liveness_revoke_1_2"] == claim_compose["liveness_revoke_1_2"]
        for t in LANGUAGE_TYPES
    )
    math_warrants_match = all(
        math_composes[t]["warrant"] == claim_compose["warrant"]
        and math_composes[t]["liveness_empty"] == claim_compose["liveness_empty"]
        and math_composes[t]["liveness_revoke_0"] == claim_compose["liveness_revoke_0"]
        and math_composes[t]["liveness_revoke_1_2"] == claim_compose["liveness_revoke_1_2"]
        for t in MATH_TYPES
    )
    science_warrants_match = all(
        science_composes[t]["warrant"] == claim_compose["warrant"]
        and science_composes[t]["liveness_empty"] == claim_compose["liveness_empty"]
        and science_composes[t]["liveness_revoke_0"] == claim_compose["liveness_revoke_0"]
        and science_composes[t]["liveness_revoke_1_2"] == claim_compose["liveness_revoke_1_2"]
        for t in SCIENCE_TYPES
    )
    fingerprint_unchanged = fingerprint_before == fingerprint_after_register

    ks = plant_world()
    fingerprint_after_world = warrant_algebra_fingerprint()
    fingerprint_still_unchanged = fingerprint_before == fingerprint_after_world

    speaker = ks.atom(SAID).authority
    world_auth = ks.atom(WORLD).authority
    mixed = ks.atom(SAID_AND_WORLD).authority
    speaker_world_meet = speaker.meet(world_auth)
    hostile_max = mutant_authority_max([speaker, world_auth])
    speaker_not_world = speaker.rank("world_truth") == 0 and speaker.rank("speaker") == 1
    world_not_speaker = world_auth.rank("speaker") == 0 and world_auth.rank("world_truth") == 1
    meet_collapses = mixed == speaker_world_meet and mixed.rank("speaker") == 0 and mixed.rank("world_truth") == 0
    max_leaks = hostile_max.rank("speaker") == 1 and hostile_max.rank("world_truth") == 1
    said_survives_world_revoke = ks.atom(SAID).liveness((EV_METER,)) is Liveness.LIVE
    world_survives_said_revoke = ks.atom(WORLD).liveness((EV_SAID,)) is Liveness.LIVE
    mixed_dies_either = (
        ks.atom(SAID_AND_WORLD).liveness((EV_SAID,)) is Liveness.DEAD
        and ks.atom(SAID_AND_WORLD).liveness((EV_METER,)) is Liveness.DEAD
    )

    proved_auth = ks.atom(PROVED).authority
    measured_auth = ks.atom(MEASURED).authority
    apply_auth = ks.atom(APPLICABILITY).authority
    proof_not_empirical = (
        proved_auth.rank("empirical") == 0 and proved_auth.rank("formal_proof") == 1
    )
    empirical_not_proof = (
        measured_auth.rank("formal_proof") == 0 and measured_auth.rank("empirical") == 1
    )
    apply_meet_empty = (
        apply_auth.rank("formal_proof") == 0 and apply_auth.rank("empirical") == 0
    )
    proof_survives_meter = ks.atom(PROVED).liveness((EV_METER2,)) is Liveness.LIVE
    measured_survives_kernel = ks.atom(MEASURED).liveness((EV_KERNEL,)) is Liveness.LIVE
    apply_dies_either = (
        ks.atom(APPLICABILITY).liveness((EV_KERNEL,)) is Liveness.DEAD
        and ks.atom(APPLICABILITY).liveness((EV_METER2,)) is Liveness.DEAD
    )
    proof_max_leaks = mutant_authority_max([proved_auth, measured_auth])
    proof_hostile_leaks = (
        proof_max_leaks.rank("formal_proof") == 1 and proof_max_leaks.rank("empirical") == 1
    )

    seed = seed_vector(ks, {QUERY: Fraction(1)})
    act = fixed_point(ks, seed, ALPHA)
    similar_activated = act[CAT] > 0 and act[KAT] > 0
    similar_warrants_distinct = ks.atom(CAT).warrant != ks.atom(KAT).warrant
    similar_ids_distinct = CAT != KAT
    cone_cat = impact_cone(ks, {CAT})
    similar_not_in_cone = KAT not in cone_cat and QUERY not in cone_cat
    kat_survives_lex_revoke = ks.atom(KAT).liveness((EV_LEX,)) is Liveness.LIVE
    cat_survives_sim_revoke = ks.atom(CAT).liveness((EV_SIM,)) is Liveness.LIVE
    similar_is_not_dependency = "SIMILAR_TO" not in ks.registry.dependency_types

    same_content = ks.atom(CAT).content_ref == ks.atom(TWIN).content_ref == "cat"
    production_warrants_not_merged = ks.atom(CAT).warrant != ks.atom(TWIN).warrant
    ident_warrant = ks.atom(IDENT).warrant
    corr_required = EV_CORR in ident_warrant.evidence
    ident_dies_without_corr = ks.atom(IDENT).liveness((EV_CORR,)) is Liveness.DEAD
    ends_live_without_corr = (
        ks.atom(CAT).liveness((EV_CORR,)) is Liveness.LIVE
        and ks.atom(TWIN).liveness((EV_CORR,)) is Liveness.LIVE
    )
    hostile_merge = mutant_identify_by_content_ref(ks)
    hostile_would_join = hostile_merge[CAT]["warrant"] != ks.atom(CAT).warrant.as_dict()

    revoked_src = (EV_SRC,)
    report = reopening_report(ks, (), revoked_src, seed=seed_vector(ks, {GOAL: Fraction(1)}))
    cone_fact = impact_cone(ks, {FACT})
    views = frozenset({LANG_OF_FACT, MATH_OF_FACT, SCI_OF_FACT})
    views_in_cone = views <= cone_fact
    views_reopen = views <= report.reopen
    views_dead = all(ks.atom(v).liveness(revoked_src) is Liveness.DEAD for v in views)
    color_live = ks.atom(COLOR).liveness(revoked_src) is Liveness.LIVE
    color_unaffected = COLOR in report.unaffected
    said_unrelated_to_src = ks.atom(SAID).liveness(revoked_src) is Liveness.LIVE

    compose_mod = compose.__module__
    nav_mod = fixed_point.__module__
    cone_mod = impact_cone.__module__
    same_modules = (
        compose_mod == "ocm.kso.admission"
        and nav_mod == "ocm.kso.navigation"
        and cone_mod == "ocm.kso.revocation"
    )
    lang_seed = seed_vector(ks, {LANG_OF_FACT: Fraction(1)})
    math_seed = seed_vector(ks, {MATH_OF_FACT: Fraction(1)})
    sci_seed = seed_vector(ks, {SCI_OF_FACT: Fraction(1)})
    lang_act = fixed_point(ks, lang_seed, ALPHA)
    math_act = fixed_point(ks, math_seed, ALPHA)
    sci_act = fixed_point(ks, sci_seed, ALPHA)
    domain_navigation_lives = (
        lang_act[LANG_OF_FACT] > 0
        and math_act[MATH_OF_FACT] > 0
        and sci_act[SCI_OF_FACT] > 0
    )
    math_live_on_math_seed = math_act[MATH_OF_FACT] > 0
    sci_live_on_sci_seed = sci_act[SCI_OF_FACT] > 0

    default_after = snapshot_default_registry()
    default_untouched = default_before == default_after
    default_is_core = set(default_after["atom_types"]) == set(CORE_ATOM_TYPES)
    src_edited = production_src_edited()

    boxes = {
        "GEF/001-language_types_register_without_changing_core_warrant_semant": {
            "text": "language types register without changing core warrant semantics",
            "status": (
                "EARNED_AT_SCOPE"
                if extra_types_registered
                and language_warrants_match
                and fingerprint_unchanged
                and fingerprint_still_unchanged
                and unregistered_core
                and unregistered_extra
                and default_untouched
                else "OPEN"
            ),
            "types": list(LANGUAGE_TYPES),
            "warrants_match_claim": language_warrants_match,
            "fingerprint_unchanged": fingerprint_unchanged,
        },
        "GEF/002-mathematics_types_register_without_changing_core_warrant_sem": {
            "text": "mathematics types register without changing core warrant semantics",
            "status": (
                "EARNED_AT_SCOPE"
                if extra_types_registered
                and math_warrants_match
                and fingerprint_unchanged
                and fingerprint_still_unchanged
                and unregistered_core
                else "OPEN"
            ),
            "types": list(MATH_TYPES),
            "warrants_match_claim": math_warrants_match,
            "fingerprint_unchanged": fingerprint_unchanged,
        },
        "GEF/003-procedural_scientific_types_register_without_changing_core_w": {
            "text": "procedural/scientific types register without changing core warrant semantics",
            "status": (
                "EARNED_AT_SCOPE"
                if extra_types_registered
                and science_warrants_match
                and fingerprint_unchanged
                and fingerprint_still_unchanged
                and unregistered_core
                else "OPEN"
            ),
            "types": list(SCIENCE_TYPES),
            "warrants_match_claim": science_warrants_match,
            "fingerprint_unchanged": fingerprint_unchanged,
        },
        "GEF/004-speaker_commitment_remains_distinct_from_world_truth": {
            "text": "speaker commitment remains distinct from world truth",
            "status": (
                "EARNED_AT_SCOPE"
                if speaker_not_world
                and world_not_speaker
                and meet_collapses
                and max_leaks
                and said_survives_world_revoke
                and world_survives_said_revoke
                and mixed_dies_either
                else "OPEN"
            ),
            "speaker_ranks": speaker.as_dict(),
            "world_ranks": world_auth.as_dict(),
            "meet_ranks": mixed.as_dict(),
            "hostile_max_ranks": hostile_max.as_dict(),
            "hostile_max_leaks_both": max_leaks,
        },
        "GEF/005-formal_proof_remains_distinct_from_empirical_applicability": {
            "text": "formal proof remains distinct from empirical applicability",
            "status": (
                "EARNED_AT_SCOPE"
                if proof_not_empirical
                and empirical_not_proof
                and apply_meet_empty
                and proof_survives_meter
                and measured_survives_kernel
                and apply_dies_either
                and proof_hostile_leaks
                else "OPEN"
            ),
            "proof_ranks": proved_auth.as_dict(),
            "empirical_ranks": measured_auth.as_dict(),
            "applicability_meet_ranks": apply_auth.as_dict(),
            "hostile_max_ranks": proof_max_leaks.as_dict(),
        },
        "GEF/006-retrieved_similarity_remains_distinct_from_identity_warrant": {
            "text": "retrieved similarity remains distinct from identity/warrant",
            "status": (
                "EARNED_AT_SCOPE"
                if similar_activated
                and similar_warrants_distinct
                and similar_ids_distinct
                and similar_not_in_cone
                and kat_survives_lex_revoke
                and cat_survives_sim_revoke
                and similar_is_not_dependency
                else "OPEN"
            ),
            "similar_activated": similar_activated,
            "activation": {"cat": str(act[CAT]), "kat": str(act[KAT])},
            "warrants_distinct": similar_warrants_distinct,
            "kat_not_in_cat_cone": similar_not_in_cone,
            "similar_to_dependency": False if similar_is_not_dependency else True,
        },
        "GEF/007-shared_identity_requires_correspondence_witness": {
            "text": "shared identity requires correspondence witness",
            "status": (
                "EARNED_AT_SCOPE"
                if same_content
                and production_warrants_not_merged
                and corr_required
                and ident_dies_without_corr
                and ends_live_without_corr
                and hostile_would_join
                else "OPEN"
            ),
            "same_content_ref": same_content,
            "production_warrants_not_merged": production_warrants_not_merged,
            "identity_requires_ev_corr": corr_required,
            "identity_dead_if_corr_revoked": ident_dies_without_corr,
            "ends_remain_live": ends_live_without_corr,
            "hostile_content_ref_join_differs": hostile_would_join,
        },
        "GEF/008-revision_propagates_across_views_by_dependency": {
            "text": "revision propagates across views by dependency",
            "status": (
                "EARNED_AT_SCOPE"
                if views_in_cone
                and views_reopen
                and views_dead
                and color_live
                and color_unaffected
                and said_unrelated_to_src
                else "OPEN"
            ),
            "cone_from_fact": sorted(cone_fact),
            "reopen": sorted(report.reopen),
            "unaffected": sorted(report.unaffected),
            "views_dead": views_dead,
            "color_live": color_live,
        },
        "GEF/009-same_executive_architecture_works_across_domains": {
            "text": "same executive architecture works across domains",
            "status": (
                "EARNED_AT_SCOPE"
                if same_modules
                and domain_navigation_lives
                and math_live_on_math_seed
                and sci_live_on_sci_seed
                and extra_types_registered
                else "OPEN"
            ),
            "compose_module": compose_mod,
            "fixed_point_module": nav_mod,
            "impact_cone_module": cone_mod,
            "domain_navigation_positive": domain_navigation_lives,
        },
    }

    earned = sorted(k for k, v in boxes.items() if v["status"] == "EARNED_AT_SCOPE")
    open_boxes = sorted(k for k, v in boxes.items() if v["status"] == "OPEN")
    type_boxes_earned = all(
        boxes[k]["status"] == "EARNED_AT_SCOPE"
        for k in (
            "GEF/001-language_types_register_without_changing_core_warrant_semant",
            "GEF/002-mathematics_types_register_without_changing_core_warrant_sem",
            "GEF/003-procedural_scientific_types_register_without_changing_core_w",
        )
    )
    all_nine = len(earned) == 9 and not open_boxes
    if all_nine and fingerprint_unchanged and not src_edited and default_untouched:
        terminal = "CURRENT_KSO_ALREADY_GENERAL_ENOUGH"
    elif type_boxes_earned and fingerprint_unchanged:
        terminal = "CURRENT_KSO_ALREADY_GENERAL_ENOUGH_TYPES_ONLY"
    elif open_boxes:
        terminal = "GEF_PLANTED_KSO_GATE_FAILED"
    else:
        terminal = "CANNOT_CHECK_GEF_TERMINAL"

    return {
        "schema": SCHEMA,
        "issue": 165,
        "section": 8,
        "head": git_head(),
        "terminal": terminal,
        "programme_wide_close": False,
        "production_src_edited": src_edited,
        "default_registry_untouched": default_untouched,
        "default_registry_is_core": default_is_core,
        "parent": (
            "production ocm.kso TypeRegistry / WarrantProfile / Authority / compose / "
            "fixed_point / impact_cone (ATMS labels, Denning lattice, JTMS cone)"
        ),
        "parent_sufficient": terminal == "CURRENT_KSO_ALREADY_GENERAL_ENOUGH",
        "second_truth_store": False,
        "claim_ceiling": (
            "Planted-oracle §8 GEF boxes on production KSO type registry and warrant "
            "algebra. Extra types register locally without changing join/meet/liveness. "
            "Not programme-wide GEF close. Not N/k/index/federation. Not #73 prototype."
        ),
        "warrant_fingerprint": fingerprint_before,
        "warrant_fingerprint_after_register": fingerprint_after_register,
        "warrant_fingerprint_after_world": fingerprint_after_world,
        "fingerprint_unchanged": fingerprint_unchanged and fingerprint_still_unchanged,
        "similar_not_dependency": similar_not_dependency,
        "boxes": boxes,
        "earned": earned,
        "open": open_boxes,
        "cannot_check": [],
        "not_issued": [
            "PROGRAMME_WIDE_GEF_CLOSE",
            "GENERAL_EPISTEMIC_FIELD_SUPPORTED_AT_REGISTERED_SCOPE",
            "GEF/010-grow_unrelated_cross_domain_n",
            "GEF/011-measure_relevant_k",
            "GEF/012-charge_cross_domain_indexes",
            "GEF/013-compare_parent_federation",
            "LANGUAGE_FLUENCY_BOUNDARY_MEASURED",
            "PARENT_PRODUCT_SUFFICIENT",
            "DOMAIN_CORE_FORK_REQUIRED",
        ],
        "world": {
            "atoms": list(ks.ids),
            "extra_atom_types": list(EXTRA_ATOM_TYPES),
            "extra_relation_types": ["SIMILAR_TO"],
            "core_atom_types": list(CORE_ATOM_TYPES),
            "claim_compose": claim_compose,
            "speaker": speaker.as_dict(),
            "world_truth": world_auth.as_dict(),
        },
    }


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

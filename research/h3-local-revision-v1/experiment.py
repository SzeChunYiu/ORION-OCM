"""Issue #165 H3 local-revision capsule.

Uses production ``ocm.kso.warrant`` / ``ocm.kso.revocation`` / ``ocm.kso.admission.compose``.
Does not edit ``src/``. Planted oracle only. Not a programme-wide H3 close.
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

from ocm.kso.admission import compose
from ocm.kso.firing import Enabling, enabled_hyperedges, enabling_verdict
from ocm.kso.navigation import fixed_point, seed_vector
from ocm.kso.revocation import impact_cone, mutant_impact_cone_direct_only, reopening_report
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace
from ocm.kso.warrant import Liveness, WarrantProfile

SCHEMA = "ocm.h3.local-revision.v1"
ALPHA = Fraction(1, 3)
THRESHOLD = Fraction(1, 1000)

EV_SRC = "ev:src"
EV_ALT = "ev:alt"
EV_UNREL = "ev:unrel"

SOURCE = "source"
MID = "mid"
DEEP = "deep"
DUAL = "dual"
ALT = "alt"
ALT_ANSWER = "alt_answer"
UNRELATED = "unrelated"
UNRELATED_ANSWER = "unrelated_answer"
GOAL = "goal"

# Authored oracle labels (independent of impact_cone).
MUST_REOPEN = frozenset({SOURCE, MID, DEEP})
STRUCTURAL_DEPENDENTS_OF_SOURCE = frozenset({SOURCE, MID, DEEP, DUAL})
MUST_REMAIN_UNRELATED = frozenset({UNRELATED, UNRELATED_ANSWER})
MUST_REMAIN_ALT = frozenset({ALT, ALT_ANSWER, DUAL})
MUST_RECHECK = frozenset({DUAL})


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def tms_dead(ks: KnowledgeSpace, revoked: Iterable[Hashable]) -> frozenset[str]:
    """Independent per-atom warrant liveness (ATMS labels). Does not call impact_cone."""
    rv = frozenset(revoked)
    return frozenset(
        a.atom_id
        for a in ks.atoms
        if a.liveness(()) is Liveness.LIVE and a.liveness(rv) is not Liveness.LIVE
    )


def activation_changed(
    pre: dict[str, Fraction], post: dict[str, Fraction]
) -> frozenset[str]:
    return frozenset(x for x in pre if pre[x] != post[x])


def precision_recall(predicted: frozenset[str], truth: frozenset[str]) -> dict[str, Any]:
    """Return P/R, or CANNOT_CHECK when a denominator is empty."""
    inter = predicted & truth
    if not predicted and not truth:
        return {
            "precision": 1.0,
            "recall": 1.0,
            "status": "VACUOUS_EMPTY_BOTH",
            "predicted": [],
            "truth": [],
            "true_positives": [],
        }
    out: dict[str, Any] = {
        "predicted": sorted(predicted),
        "truth": sorted(truth),
        "true_positives": sorted(inter),
        "false_positives": sorted(predicted - truth),
        "false_negatives": sorted(truth - predicted),
    }
    if not predicted:
        out["precision"] = "CANNOT_CHECK_EMPTY_PREDICTION"
        out["recall"] = 0.0 if truth else "CANNOT_CHECK_EMPTY_TRUTH"
        out["status"] = "CANNOT_CHECK_EMPTY_PREDICTION"
        return out
    if not truth:
        out["precision"] = 0.0
        out["recall"] = "CANNOT_CHECK_EMPTY_TRUTH"
        out["status"] = "CANNOT_CHECK_EMPTY_TRUTH"
        return out
    p = len(inter) / len(predicted)
    r = len(inter) / len(truth)
    out["precision"] = p
    out["recall"] = r
    out["status"] = "MEASURED"
    return out


def plant_world() -> KnowledgeSpace:
    """Planted support world: chain, unrelated skill, and alternate warrant."""
    ks = KnowledgeSpace(
        (
            Atom(GOAL, "goal"),
            Atom(SOURCE, "procedure", WarrantProfile.of({EV_SRC})),
            Atom(ALT, "procedure", WarrantProfile.of({EV_SRC}, {EV_ALT})),
            Atom(UNRELATED, "procedure", WarrantProfile.of({EV_UNREL})),
            Atom(DUAL, "procedure", WarrantProfile.of({EV_SRC}, {EV_ALT})),
        ),
        (
            Hyperedge("g-src", (GOAL,), (SOURCE,), "DEPENDENCE"),
            Hyperedge("g-alt", (GOAL,), (ALT,), "DEPENDENCE"),
            Hyperedge("g-unrel", (GOAL,), (UNRELATED,), "DEPENDENCE"),
            Hyperedge("src-dual", (SOURCE,), (DUAL,), "DEPENDENCE"),
        ),
    )
    ks, _ = compose(ks, [SOURCE], MID)
    ks, _ = compose(ks, [MID], DEEP)
    ks, _ = compose(ks, [ALT], ALT_ANSWER)
    ks, _ = compose(ks, [UNRELATED], UNRELATED_ANSWER)
    return ks


def enabling_map(
    ks: KnowledgeSpace, act: dict[str, Fraction], revoked: Iterable[Hashable] = ()
) -> dict[str, str]:
    rv = frozenset(revoked)
    return {
        e.edge_id: enabling_verdict(ks, e, act, THRESHOLD, rv).enabling.value
        for e in ks.hyperedges
    }


def run_study() -> dict[str, Any]:
    ks = plant_world()
    seed = seed_vector(ks, {GOAL: Fraction(1)})
    pre_live = {a.atom_id: a.liveness(()).value for a in ks.atoms}
    pre_act = fixed_point(ks, seed, ALPHA)
    pre_en = enabling_map(ks, pre_act)

    revoked = (EV_SRC,)
    dead = tms_dead(ks, revoked)
    post_live = {a.atom_id: a.liveness(revoked).value for a in ks.atoms}
    post_act = fixed_point(ks, seed, ALPHA, revoked=revoked)
    post_en = enabling_map(ks, post_act, revoked)
    act_delta = activation_changed(pre_act, post_act)
    report = reopening_report(ks, (), revoked, seed=seed)
    cone_from_source = impact_cone(ks, {SOURCE})
    mutant_cone = mutant_impact_cone_direct_only(ks, {SOURCE})

    restore_live = {a.atom_id: a.liveness(()).value for a in ks.atoms}
    restore_act = fixed_point(ks, seed, ALPHA, revoked=())
    restore_en = enabling_map(ks, restore_act)
    restoration_exact = (
        restore_live == pre_live and restore_act == pre_act and restore_en == pre_en
    )

    unrelated_live = all(ks.atom(x).is_live(revoked) for x in MUST_REMAIN_UNRELATED)
    unrelated_act_held = all(pre_act[x] == post_act[x] for x in MUST_REMAIN_UNRELATED)
    unrelated_enabled = all(
        post_en[eid] == Enabling.ENABLED.value
        for eid, e in ks.edge_map().items()
        if UNRELATED in e.tails or UNRELATED_ANSWER in e.heads
    )
    alt_live = all(ks.atom(x).is_live(revoked) for x in MUST_REMAIN_ALT)
    alt_revoked_both_dead = not ks.atom(DUAL).is_live((EV_SRC, EV_ALT)) and not ks.atom(
        ALT
    ).is_live((EV_SRC, EV_ALT))

    true_dependents_reopen = MUST_REOPEN <= report.reopen and MUST_REOPEN <= dead
    stale_survivors = sorted(x for x in MUST_REOPEN if ks.atom(x).is_live(revoked))
    collateral_dead = sorted(
        x
        for x in (MUST_REMAIN_UNRELATED | MUST_REMAIN_ALT | {GOAL})
        if x in dead
    )
    deep_disabled = post_en.get("compose:deep") == Enabling.DISABLED.value
    mid_disabled = post_en.get("compose:mid") == Enabling.DISABLED.value

    reopen_pr = precision_recall(frozenset(report.reopen), MUST_REOPEN)
    dep_pr = precision_recall(cone_from_source, STRUCTURAL_DEPENDENTS_OF_SOURCE)
    mutant_pr = precision_recall(mutant_cone, STRUCTURAL_DEPENDENTS_OF_SOURCE)
    # Observational liveness-loss vs authored must-reopen (independent of cone).
    obs_reopen_pr = precision_recall(dead, MUST_REOPEN)

    mutant_misses_deep = DEEP not in mutant_cone and DEEP in cone_from_source
    dep_measured = dep_pr["status"] == "MEASURED" and obs_reopen_pr["status"] == "MEASURED"
    dep_perfect = (
        dep_measured
        and dep_pr["precision"] == 1.0
        and dep_pr["recall"] == 1.0
        and obs_reopen_pr["precision"] == 1.0
        and obs_reopen_pr["recall"] == 1.0
        and mutant_pr["status"] == "MEASURED"
        and mutant_pr["recall"] < 1.0
        and mutant_misses_deep
    )

    boxes = {
        "H3/001-true_dependents_reopen": {
            "text": "true dependents reopen",
            "status": "EARNED_AT_SCOPE" if true_dependents_reopen and not stale_survivors and mid_disabled and deep_disabled else "OPEN",
            "reopen": sorted(report.reopen),
            "must_reopen": sorted(MUST_REOPEN),
            "stale_survivors": stale_survivors,
            "compose_mid_disabled": mid_disabled,
            "compose_deep_disabled": deep_disabled,
        },
        "H3/002-unrelated_competence_remains": {
            "text": "unrelated competence remains",
            "status": (
                "EARNED_AT_SCOPE"
                if unrelated_live and unrelated_act_held and unrelated_enabled and MUST_REMAIN_UNRELATED <= report.unaffected
                else "OPEN"
            ),
            "unaffected": sorted(report.unaffected),
            "live": unrelated_live,
            "activation_held": unrelated_act_held,
            "enabling_held": unrelated_enabled,
        },
        "H3/003-alternate_support_preserves_valid_competence": {
            "text": "alternate support preserves valid competence",
            "status": (
                "EARNED_AT_SCOPE"
                if alt_live and MUST_RECHECK <= report.recheck and alt_revoked_both_dead
                else "OPEN"
            ),
            "live_after_src_revoke": alt_live,
            "recheck": sorted(report.recheck),
            "both_supports_revoked_kills_alt": alt_revoked_both_dead,
        },
        "H3/004-restoration_returns_exactly_justified_state": {
            "text": "restoration returns exactly justified state",
            "status": "EARNED_AT_SCOPE" if restoration_exact else "OPEN",
            "liveness_restored": restore_live == pre_live,
            "activation_restored": restore_act == pre_act,
            "enabling_restored": restore_en == pre_en,
        },
        "H3/005-dependency_precision_recall_measured": {
            "text": "dependency precision/recall measured",
            "status": "EARNED_AT_SCOPE" if dep_measured else "CANNOT_CHECK_NO_DENOMINATOR",
            "planted_oracle": {
                "cone_vs_authored_structural_dependents": dep_pr,
                "reopen_vs_authored_must_reopen": reopen_pr,
                "tms_dead_vs_authored_must_reopen": obs_reopen_pr,
                "perfect_at_this_oracle": dep_perfect,
            },
            "mutant_shallow_cone": {
                **mutant_pr,
                "misses_deep_dependent": mutant_misses_deep,
                "note": "Direct-only cone of source must miss the deep composition head, else the P/R metric is inert.",
            },
            "induced_or_unknown_support_graphs": "CANNOT_CHECK_NO_INDEPENDENT_INDUCED_ORACLE",
            "lifetime_p6_residual": "CANNOT_CHECK_NOT_RUN",
        },
    }

    integrity = [
        boxes["H3/001-true_dependents_reopen"]["status"] == "EARNED_AT_SCOPE",
        boxes["H3/002-unrelated_competence_remains"]["status"] == "EARNED_AT_SCOPE",
        boxes["H3/003-alternate_support_preserves_valid_competence"]["status"] == "EARNED_AT_SCOPE",
        boxes["H3/004-restoration_returns_exactly_justified_state"]["status"] == "EARNED_AT_SCOPE",
    ]
    pr_status = boxes["H3/005-dependency_precision_recall_measured"]["status"]
    if all(integrity) and pr_status == "EARNED_AT_SCOPE":
        terminal = "PARENT_SUFFICIENT_AT_PLANTED_KSO_SCOPE"
    elif all(integrity) and str(pr_status).startswith("CANNOT_CHECK"):
        terminal = "H3_INTEGRITY_GATES_PASS_PRECISION_RECALL_CANNOT_CHECK"
    elif all(integrity):
        terminal = "H3_INTEGRITY_GATES_PASS_AT_PLANTED_KSO_SCOPE"
    else:
        terminal = "H3_INTEGRITY_GATE_FAILED"

    return {
        "schema": SCHEMA,
        "issue": 165,
        "head": git_head(),
        "terminal": terminal,
        "programme_wide_close": False,
        "production_src_edited": False,
        "parent": "production ocm.kso warrant/revocation (ATMS labels, JTMS impact cone, KS-T22 reopening)",
        "parent_sufficient": terminal.startswith("PARENT_SUFFICIENT"),
        "claim_ceiling": (
            "Planted-oracle H3 integrity on production KSO warrant/revocation. "
            "This is the ATMS/JTMS parent, not an OCM residual over TMS. "
            "Not programme-wide H3 close. Not H4/H5. Induced-graph P/R is CANNOT_CHECK."
        ),
        "boxes": boxes,
        "earned": sorted(k for k, v in boxes.items() if v["status"] == "EARNED_AT_SCOPE"),
        "open": sorted(k for k, v in boxes.items() if v["status"] == "OPEN"),
        "cannot_check": sorted(
            k for k, v in boxes.items() if str(v["status"]).startswith("CANNOT_CHECK")
        ),
        "world": {
            "atoms": list(ks.ids),
            "revoked": [EV_SRC],
            "pre_liveness": pre_live,
            "post_liveness": post_live,
            "tms_dead": sorted(dead),
            "stale_survivors": stale_survivors,
            "collateral_invalidations": collateral_dead,
            "reopening": report.as_dict(),
            "cone_from_source": sorted(cone_from_source),
            "mutant_cone_from_source": sorted(mutant_cone),
            "activation_changed": sorted(act_delta),
            "enabled_pre": sorted(enabled_hyperedges(ks, pre_act, THRESHOLD)),
            "enabled_post": sorted(enabled_hyperedges(ks, post_act, THRESHOLD, revoked)),
        },
        "not_issued": [
            "PROGRAMME_WIDE_H3_CLOSE",
            "H3_RESIDUAL_OVER_TMS",
            "H4_EXACT_REVOCATION_CLOSE",
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
    print(json.dumps({"terminal": result["terminal"], "earned": result["earned"]}, indent=2))
    return result


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "RESULT.json"
    main(target)

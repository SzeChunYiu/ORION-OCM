#!/usr/bin/env python3
"""Fail-closed structural validator for the #602 formal closure capsule."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEP = HERE / "GMI_602_CLOSURE_DEPENDENCIES_V1.json"
SPINE = HERE / "GMI_602_PARENT_ATLAS_AND_FORMAL_CLOSURE_V1.md"
AMENDMENT = HERE / "GMI_602_PARENT_ATLAS_AMENDMENTS_V1.md"
FORMAL_V2 = HERE / "GMI_602_FORMAL_GAP_CLOSURE_V2.md"
FORMAL_V2_CORRIGENDA = HERE / "GMI_602_FORMAL_GAP_CORRIGENDA_V2.md"
KNOWN_V3 = HERE / "GMI_602_KNOWN_FAMILY_FORMAL_CLOSURE_V3.md"
CROSSWALK = HERE / "GMI_602_PARENT_FIRST_CROSSWALK_V1.json"
PARENT = ROOT.parent / "machine-intelligence-morphogenesis-v1" / "PARENT_LEDGER_V2.json"

EXPECTED_SECTIONS = tuple(chr(c) for c in range(ord("A"), ord("V") + 1))
EXPECTED_THEOREMS = {
    *(f"T602-{i:02d}" for i in range(1, 17)),
    "T602-17",
    "T602-17b",
    *(f"T602-{i:02d}" for i in range(18, 37)),
}
EXPECTED_CORRIGENDA_V1 = {"C602-05", "C602-13", "C602-14", "C602-17b", "C602-20"}
EXPECTED_CORRIGENDA_V2 = {"C602-25", "C602-26"}
EXPECTED_CORRIGENDA = EXPECTED_CORRIGENDA_V1 | EXPECTED_CORRIGENDA_V2
EXPECTED_ADDED_PARENT_CLASSES = {
    "predictive_state_causal_state_bisimulation",
    "statistical_sufficiency_information_bottleneck",
    "pac_vc_pac_bayes",
    "minimax_le_cam_fano_assouad",
    "online_learning_regret",
    "bandit_exploration",
    "generic_active_learning",
    "streaming_cell_probe_external_memory",
    "algorithmic_information_universal_agents",
    "observability_controllability_system_identification",
}
EXPECTED_Q_IDS = {f"Q{i:02d}" for i in range(1, 24)}
EXPECTED_SUPPLEMENTAL_PARENT_IDS = {f"S{i:02d}" for i in range(1, 12)}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> None:
    dep = load_json(DEP)
    parent = load_json(PARENT)
    crosswalk = load_json(CROSSWALK)
    spine = SPINE.read_text(encoding="utf-8")
    amendment = AMENDMENT.read_text(encoding="utf-8")
    formal_v2 = FORMAL_V2.read_text(encoding="utf-8")
    formal_v2_corrigenda = FORMAL_V2_CORRIGENDA.read_text(encoding="utf-8")
    known_v3 = KNOWN_V3.read_text(encoding="utf-8")

    assert dep["schema"] == "GMI_602_CLOSURE_DEPENDENCIES_V1"
    assert dep["formal_spine"] == SPINE.name
    assert dep["formal_amendment"] == AMENDMENT.name
    assert dep["formal_gap_supplement"] == FORMAL_V2.name
    assert dep["formal_gap_corrigenda"] == FORMAL_V2_CORRIGENDA.name
    assert dep["known_family_formal_supplement"] == KNOWN_V3.name
    assert dep["parent_crosswalk"] == CROSSWALK.name
    assert isinstance(parent, dict) and parent, "specialist parent ledger must parse as a nonempty JSON object"
    assert PARENT.stat().st_size > 10_000, "specialist parent ledger unexpectedly collapsed"

    assert crosswalk["schema"] == "GMI_602_PARENT_FIRST_CROSSWALK_V1"
    q_rows = crosswalk["issue_Q_required"]
    supplemental_rows = crosswalk["supplemental_parent_classes_required_by_other_602_rows"]
    assert {row["id"] for row in q_rows} == EXPECTED_Q_IDS, "#602 Q parent crosswalk must cover all 23 requested families exactly once"
    assert {row["id"] for row in supplemental_rows} == EXPECTED_SUPPLEMENTAL_PARENT_IDS, "supplemental parent-first inventory drifted"
    for row in q_rows + supplemental_rows:
        assert row.get("parent_owns") or row.get("purpose"), f"{row['id']}: missing parent-owned content"
        assert row.get("gmi_residual") or row.get("residual"), f"{row['id']}: missing explicit GMI residual"

    sections = dep["sections"]
    assert tuple(sections.keys()) == EXPECTED_SECTIONS, "A..V section ledger must be complete and ordered"
    for name, row in sections.items():
        assert row.get("formal_status"), f"{name}: missing formal_status"
        assert row.get("evidence_status"), f"{name}: missing evidence_status"
        assert isinstance(row.get("blockers"), list), f"{name}: blockers must be explicit"

    theorem_ids = set(dep["theorems"])
    assert theorem_ids == EXPECTED_THEOREMS, "formal theorem inventory drifted"
    spine_ids = {*(f"T602-{i:02d}" for i in range(1, 24)), "T602-17b"}
    v2_ids = {f"T602-{i:02d}" for i in range(24, 34)}
    v3_ids = {f"T602-{i:02d}" for i in range(34, 37)}
    for theorem_id in sorted(EXPECTED_THEOREMS):
        if theorem_id in spine_ids:
            corpus = spine
        elif theorem_id in v2_ids:
            corpus = formal_v2
        elif theorem_id in v3_ids:
            corpus = known_v3
        else:
            raise AssertionError(f"{theorem_id}: no owning formal artifact")
        assert theorem_id in corpus, f"{theorem_id}: declared but absent from its formal artifact"

    corrigenda = set(dep["normative_corrigenda"])
    assert corrigenda == EXPECTED_CORRIGENDA, "normative corrigenda inventory drifted"
    for correction_id in sorted(EXPECTED_CORRIGENDA_V1):
        assert correction_id in amendment, f"{correction_id}: declared but absent from V1 amendment"
    for correction_id in sorted(EXPECTED_CORRIGENDA_V2):
        assert correction_id in formal_v2_corrigenda, f"{correction_id}: declared but absent from V2 corrigenda"

    added_parents = set(dep["added_parent_classes"])
    assert added_parents == EXPECTED_ADDED_PARENT_CLASSES, "added parent-first class inventory drifted"
    for token in ("Predictive Representations of State", "Vapnik", "Assouad", "Frequency Moments", "AIXI"):
        assert token in amendment, f"parent amendment lost required anchor token: {token}"

    assert "finite admitted candidate set" in amendment, "C602-14 candidate-finiteness repair missing"
    assert "C_\\pi(t)" in amendment, "C602-17b transcript-cell definition missing"
    assert "distinct real-valued" in amendment, "C602-20 extrapolation scope repair missing"
    assert "infimum" in formal_v2_corrigenda and "epsilon" in formal_v2_corrigenda, "C602-25 attainment repair missing"
    assert "continuous-state Markov kernel" in formal_v2_corrigenda, "C602-26 continuous reachability repair missing"

    for token in (
        "residual external-memory",
        "common learning/update object",
        "developmental reachability",
        "hybrid solver routing",
        "capability interaction calculus",
        "capability-predictor sufficiency",
        "machine-species ecology",
        "Optional inheritance monotonicity",
        "global statistical-validity",
        "scaling, bottlenecks",
    ):
        assert token in formal_v2, f"formal V2 supplement lost required gap-closure token: {token}"

    for token in (
        "fixed/local vs adaptive-sparse",
        "selector/emitter factorization",
        "retained program/library search-burden law",
    ):
        assert token in known_v3, f"known-family V3 supplement lost required formal gap: {token}"

    assert sections["Q"]["evidence_status"] == "GREEN_REGISTERED_SCOPE_PARENT_CROSSWALK"
    assert not sections["Q"]["blockers"], "registered-scope Q coverage should not be made impossible by a permanent blocker"

    empirical = dep["empirical_claim"]
    if empirical["status"] == "EARNED":
        allowed = {
            "GREEN",
            "NOT_REQUIRED",
            "UPSTREAM_SPECIALIST_PARENT_LEDGER_PRESENT",
            "PARENT_CROSSWALK_PRESENT",
            "GREEN_REGISTERED_SCOPE_PARENT_CROSSWALK",
        }
        non_green = {
            name: row["evidence_status"]
            for name, row in sections.items()
            if row["evidence_status"] not in allowed
        }
        blockers = {name: row["blockers"] for name, row in sections.items() if row["blockers"]}
        assert not non_green, f"fail closed: empirical closure has non-green dependencies: {non_green}"
        assert not blockers, f"fail closed: empirical closure has blockers: {blockers}"

    assert empirical["status"] == "NOT_EARNED", "this branch must not silently promote empirical closure"
    assert sections["V"]["evidence_status"] == "NOT_GREEN"

    print("GMI_602_CLOSURE_DEPENDENCY_LEDGER_VALID")
    print(f"parent_ledger_bytes={PARENT.stat().st_size}")
    print(f"issue_Q_parent_rows={len(q_rows)}")
    print(f"supplemental_parent_rows={len(supplemental_rows)}")
    print(f"theorem_ids={len(theorem_ids)}")
    print(f"corrigenda={len(corrigenda)}")
    print(f"added_parent_classes={len(added_parents)}")
    print(f"sections={len(sections)}")
    print("complete_empirical_closure=NOT_EARNED")


if __name__ == "__main__":
    main()

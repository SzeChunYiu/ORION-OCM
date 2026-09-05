"""KnowledgeSpace.v1 M0 freeze checkers (``kso_m0_freeze_checks_v1.py``).

Each test pins one clause of the substrate contract to a finite check with a planted failure or
a must-differ control; ``CANNOT_CHECK`` is exercised as a distinct outcome and never a pass.
"""

from __future__ import annotations

import importlib.util
import sys
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "research" / "orion-machine" / "reference" / "kso_m0_freeze_checks_v1.py"


def _load():
    spec = importlib.util.spec_from_file_location("kso_m0_freeze_checks_v1", MODULE)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load()


@pytest.fixture(scope="module")
def result(mod):
    return mod.run_all()


def test_genome_predicates_hold_and_every_planted_violation_is_caught(result):
    g = result["g1_genome_S1_S7"]
    assert g["predicates"] == 7 and g["all_hold_on_witness"] == 1
    assert all(g["planted_violations_caught"].values())
    assert len(g["genome_digest"]) == 64


def test_edge_vocabulary_is_bound_to_the_atlas_source(result):
    f = result["f1_edge_vocabulary"]
    assert f == {"atlas_kinds_bound": 6, "kso_relation_kinds": 4, "vocabulary_size": 10, "atlas_source_matches": 1, "unregistered_type_rejected": 1}


def test_retraction_propagation_both_directions(result):
    f = result["f2_retraction_propagation"]
    assert f["revoked_atom_activation_zero"] == 1
    assert f["downstream_atoms_dropped_exactly"] == 2
    assert f["unrelated_atom_unchanged"] == 1
    assert f["renormalising_parent_raises_unrelated"] == 1
    assert f["reinstatement_restores_pre_vector"] == 1
    assert f["a_row_mass_after_revocation"] == "1/2"
    assert f["unapplied_retraction_is_cannot_check"] == 1


def test_unapplied_planted_retraction_is_cannot_check_not_a_pass(mod):
    ks = mod.retraction_witness_space()
    seed = mod.seed_vector(ks, {"s": Fraction(1, 1)})
    with pytest.raises(mod.CannotCheck):
        mod.retraction_checker(ks, seed=seed, alpha=Fraction(1, 3), revoke=frozenset({9}), revoked_atom="b", downstream=("c",), unrelated="z")


def test_hub_two_directions(result):
    f = result["f3_hub_two_directions"]
    assert f["direction_i_hub_first_by_popularity"] == 1
    assert f["direction_i_specific_first_by_surprise"] == 1
    assert f["direction_ii_hub_first_by_surprise_when_only_hub_touched"] == 1
    assert f["popularity_control_differs"] == 1
    assert f["i_surprise_specific"] > f["i_surprise_hub"]


def test_acquisition_channels_feedback_unwarranted_exact_checker_warrants(result):
    c = result["f4_acquisition"]["cases"]
    assert c["instruction_connected"] == "ADMITTED"
    assert c["isolated_live"] == "ISOLATED_ATOM_REJECTED"
    assert c["isolated_quarantined"] == "QUARANTINED"
    assert c["feedback_unwarranted_cannot_fire"] == "HELD"
    assert c["exact_checker_warrants_firing"] == "HELD"
    assert c["warranting_channel_without_warrant"] == "WARRANTING_CHANNEL_WITHOUT_WARRANT"
    assert c["unregistered_relation"] == "UNREGISTERED_RELATION_TYPE"


def test_atomisation_exactness(result):
    f = result["f5_atomisation"]
    assert f["parts"] == 2 and f["seeds"] == 2 and f["deterministic_seed_vector"] == 1
    assert f["rejections"] == {"empty": "EMPTY_QUESTION", "non_atomic": "NON_ATOMIC_INPUT", "unbound": "UNBOUND_SEED", "no_refs": "UNBOUND_SEED"}


def test_navigation_outcomes_are_four_valued_and_distinct(result, mod):
    f = result["f6_navigation_outcomes"]
    o = f["outcomes"]
    assert o["chain_target_big_budget"].startswith("FOUND")
    assert o["chain_target_small_budget"].startswith("GAP_NOT_FOUND:BUDGET")
    assert o["absent_target"] == "GAP_NOT_FOUND:TARGET_ABSENT"
    assert o["island_target"].startswith("OBSTRUCTION_WITNESSED")
    assert o["warrant_gated_target"].startswith("GAP_NOT_FOUND:WARRANT")
    assert f["zero_budget_is_cannot_check"] == 1
    assert f["witness_binds_to_jump_trigger_admissible"] == 1
    assert {m.value for m in mod.NavigationOutcome} == {"FOUND", "GAP_NOT_FOUND", "OBSTRUCTION_WITNESSED", "CANNOT_CHECK"}


def test_compose_is_a_conjunctive_label_not_a_merge(result):
    f = result["g2_compose"]
    assert f["composite_label_is_conjunctive_product"] == 1
    assert f["component_revocation_kills_composite"] == 2
    assert f["merge_mutant_detected"] == 1


def test_extraction_unique_and_optimiser_distinct(result):
    f = result["g2_extract"]
    assert f["reacting_subgraph_deterministic"] == 1
    assert f["revoked_atom_and_its_edges_leave_subgraph"] == 1
    assert f["optimiser_tie_witness_optima"] > 1
    assert f["optimiser_unique_witness"] == 1


def test_translator_invariance_reduces_to_seed_equality(result):
    f = result["g2_translator_invariance"]
    assert f["equal_seed_vectors_identical_extraction"] == 1
    assert f["unequal_seed_vectors_differ"] == 1
    assert f["codec_agreement_on_seed_vector"] == "OPEN_M5"


def test_nonidentifiability_is_an_obstruction_witness(result):
    f = result["g2_nonidentifiability"]
    assert f == {"symmetric_twin_is_obstruction": 1, "no_twin_is_found": 1, "reatomisation_separates": 1}


def test_growth_invariant_holds_and_cancers_are_caught(result):
    f = result["g3_growth_invariant"]
    assert f["growth_steps"] == 3 and f["genome_held_every_step"] == 1 and f["genome_digest_unchanged"] == 1 and f["fixed_point_reached"] == 1
    assert set(f["cancers"].values()) == {"CAUGHT"}


def test_no_single_parent_owns_label_gated_exact_share_retraction(result):
    f = result["f7_parent_subtraction"]
    assert f["parents_run"] == 8
    assert f["single_parent_owning_label_gated_exact_share_retraction"] == 0
    assert f["kso_law_equals_two_parent_product"] == 1
    names = [r["parent"] for r in f["rows"]]
    for needle in ("Collins & Loftus", "Quillian", "ACT-R", "Hopfield", "case-based", "RWR", "JTMS", "ATMS"):
        assert any(needle in n for n in names), needle


def test_budget_clause_unmatched_is_cannot_check(result):
    assert result["f8_budget_clause"] == {"matched_pair_accepted": 1, "unmatched_pair_is_cannot_check": 1}


def test_typing_is_a_coverage_prior(result):
    f = result["f9_typing_coverage_prior"]
    assert f["outcome_ties_under_full_coverage"] == 3
    assert f["unexercised_types_where_typed_advantage_is_admissible"]
    assert f["typed_advantage_claimed"] == 0


def test_codec_boundary_closed_under_shown(result):
    f = result["f10_closed_under_shown"]
    assert f["rejections"] == {"unshown_ref": "ASKED_FOR_WHAT_WAS_NOT_SHOWN", "duplicate_hash": "AMBIGUOUS_REFERENCE"}


def test_cli_exit_codes_are_three_and_distinct(mod, monkeypatch, capsys):
    assert mod.main([]) == 0
    monkeypatch.setattr(mod, "check_f1_edge_vocabulary", lambda: (_ for _ in ()).throw(mod.CannotCheck("planted")))
    assert mod.main([]) == 2
    monkeypatch.setattr(mod, "check_f1_edge_vocabulary", lambda: (_ for _ in ()).throw(AssertionError("planted")))
    assert mod.main([]) == 1
    capsys.readouterr()

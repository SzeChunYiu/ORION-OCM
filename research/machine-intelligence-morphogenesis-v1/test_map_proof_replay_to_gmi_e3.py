import copy

import pytest

from map_proof_replay_to_gmi_e3 import INPUT_SCHEMA, map_receipt


def pass_receipt():
    return {
        "schema": INPUT_SCHEMA,
        "terminal": "FIXED_PROOF_REPLAY_PASS",
        "manifest_sha256": "a" * 64,
        "toolchain": "Lean (version 4.19.0, pinned)",
        "archive_sha256": "b" * 64,
        "lean_binary_sha256": "c" * 64,
        "statement_scope": "Nine named fixed theorems and their written hypotheses; core Lean only",
        "claims": {
            "fresh_kernel_replay": "REQUIRED",
            "informal_correspondence": "NOT_OBTAINED",
            "learned_proof_methods": "NOT_EVALUATED",
            "runtime_adoption": "NOT_GRANTED",
            "scientific_novelty": "NOT_ESTABLISHED",
            "unseen_proof_generalization": "NOT_EVALUATED",
        },
        "limitations": ["Known authored reconstruction, not unseen or learned proof evaluation"],
    }


def test_pass_maps_to_formal_calibration_without_developmental_claim():
    episode = map_receipt(pass_receipt())
    assert episode["episode_identity"]["domain"] == "FORMAL_MATHEMATICS_LEAN"
    assert episode["outcome"]["terminal"] == "FORMAL_KERNEL_VERIFIED_FIXED_REPLAY_ONLY"
    assert episode["outcome"]["capability_vector"]["target_kernel_verified"] is True
    assert episode["outcome"]["capability_vector"]["statement_correspondence"] == "UNKNOWN"
    attribution = episode["developmental_attribution"]
    assert attribution["candidate_capital_level"] == "NONE_CALIBRATION"
    assert attribution["pre_solution_mediator_observed"] is False
    assert attribution["causal_attribution_terminal"] == "NO_DEVELOPMENTAL_CLAIM_FIXED_REPLAY"
    assert episode["morphology_realization"]["U_update_law_identity"] == "IDENTITY_NO_LEARNING"
    assert episode["resource_vector"]["development_update_work"] == 0


def test_mapper_preserves_not_obtained_correspondence():
    episode = map_receipt(pass_receipt())
    assert episode["external_verification"]["statement_or_spec_correspondence_rule"] == "NOT_OBTAINED_FOR_INFORMAL_STATEMENT"
    assert "no informal correspondence" in episode["outcome"]["semantic_claim_ceiling"].lower()


def test_cannot_check_does_not_become_success():
    receipt = pass_receipt()
    receipt["terminal"] = "CANNOT_CHECK"
    episode = map_receipt(receipt)
    assert episode["outcome"]["terminal"] == "CANNOT_CHECK"
    assert episode["outcome"]["admissible_result"] is False
    assert episode["outcome"]["capability_vector"]["target_kernel_verified"] is False


def test_wrong_source_schema_rejected():
    receipt = pass_receipt()
    receipt["schema"] = "something.else"
    with pytest.raises(ValueError):
        map_receipt(receipt)


def test_unknown_source_terminal_rejected():
    receipt = pass_receipt()
    receipt["terminal"] = "MAYBE"
    with pytest.raises(ValueError):
        map_receipt(receipt)

from gmi_realization_signature_collision import (
    affine_description_terms,
    candidate_realizations,
    coarse_signature,
    collision_receipt,
    majority3,
    parity3,
    relevant_input_fraction,
    table,
    winner,
)


def test_parity_and_majority_match_frozen_coarse_signature():
    parity = table(3, parity3)
    majority = table(3, majority3)
    assert coarse_signature(parity, 3, horizon=1) == coarse_signature(majority, 3, horizon=1)


def test_all_inputs_are_semantically_relevant_for_both():
    assert relevant_input_fraction(table(3, parity3), 3) == 1.0
    assert relevant_input_fraction(table(3, majority3), 3) == 1.0


def test_constructive_regularity_differs_under_frozen_affine_language():
    parity = table(3, parity3)
    majority = table(3, majority3)
    assert affine_description_terms(parity, 3) == 3
    assert affine_description_terms(majority, 3) is None


def test_realization_frontier_differs_despite_coarse_signature_collision():
    parity = table(3, parity3)
    majority = table(3, majority3)
    assert winner(parity, 3, horizon=1) == ("AFFINE_XOR_PROGRAM",)
    assert winner(majority, 3, horizon=1) == ("LOOKUP_TABLE",)


def test_majority_affine_candidate_is_semantically_inadmissible_not_merely_expensive():
    majority = table(3, majority3)
    candidates = {c.name: c for c in candidate_realizations(majority, 3, horizon=1)}
    assert candidates["AFFINE_XOR_PROGRAM"].semantically_admissible is False
    assert candidates["LOOKUP_TABLE"].semantically_admissible is True


def test_collision_receipt_is_fail_closed_on_coarse_signature():
    receipt = collision_receipt()
    assert receipt["collision"] is True
    assert receipt["obligations"]["PARITY_3"]["winner"] == ("AFFINE_XOR_PROGRAM",)
    assert receipt["obligations"]["MAJORITY_3"]["winner"] == ("LOOKUP_TABLE",)
    assert receipt["terminal"] == "REALIZATION_SIGNATURE_INSUFFICIENT__COARSE_SIGNATURE_COLLISION_EXACT"
    assert "reference-language dependent" in receipt["claim_boundary"]

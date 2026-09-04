"""Lane #203 reference semantics: the substrate constraints S1-S7 must hold exactly,
each must be able to fail for its registered reason, and CANNOT_CHECK must be distinct."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "research" / "orion-machine" / "reference" / "ocm_reference_semantics.py"


def _load():
    spec = importlib.util.spec_from_file_location("ocm_reference_semantics", MODULE)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # dataclasses resolve annotations through sys.modules
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load()


@pytest.fixture(scope="module")
def result(mod):
    return mod.run_reference_semantics()


def test_substrate_uses_the_committed_rcl_model(mod):
    assert mod.rcl.MAX_EXHAUSTIVE_N >= 4
    assert len(mod.rcl.enumerate_antichains(4)) == 168  # Dedekind antichains on 4 atoms
    assert mod.CHANNELS == ("instruction", "demonstration", "interaction", "experimentation", "feedback")


def test_S1_admission_gate_and_laundering_control(result):
    s1 = result["checks"]["S1_admission"]
    assert s1["rejected_by_V"] is True
    assert s1["laundering_planted"] is True and s1["laundering_caught_by_invariant"] is True
    assert s1["V_calls"] == 2  # the laundered path never called V


def test_S2_composition_is_conjunctive_with_scope_intersection(result):
    s2 = result["checks"]["S2_composition"]
    assert s2["exhaustive"] == {"n": 3, "antichains": 20, "pairs": 400, "liveness_checks": 3200, "violations": [], "holds": True}
    assert s2["sampled"]["liveness_checks"] == 64000 and s2["sampled"]["seed"] == 20260904 and s2["sampled"]["holds"]
    assert s2["scope"] == {"composite_scope": ["b"], "union_scope_countermodels": ["a", "c"], "holds": True}


def test_S3_revocation_completeness_and_positive_only_abstention(result):
    s3 = result["checks"]["S3_revocation_completeness"]
    assert (s3["antichains"], s3["revocations"], s3["liveness_checks"], s3["mismatches"]) == (168, 16, 2688, 0)
    assert s3["two_evaluator_agreement"] == {"agree": 2688, "denominator": 2688}
    p = s3["planted_positive_only_store"]
    assert p["false_retractions"] == 0 and p["abstentions_where_truth_is_live"] == 485 and p["caught"]
    assert p["first_witness"] == {"profile": [[0], [1]], "revoked": [0], "emitted_witness": [0]}


def test_S4_coarsest_authority_preserving_representation_is_generated_partition(result):
    s4 = result["checks"]["S4_representation_revision"]
    assert s4["partitions"] == 15 and s4["antichains"] == 168
    by = {r["gamma"]: r for r in s4["families"]}
    assert by["singletons"]["generated_partition"] == [[0], [1], [2], [3]] and by["singletons"]["exact_partitions"] == 1
    assert by["pairs_01_23"]["generated_partition"] == [[0, 1], [2, 3]] and by["pairs_01_23"]["exact_partitions"] == 4
    assert by["one_set_12"]["generated_partition"] == [[0, 3], [1, 2]] and by["one_set_12"]["exact_partitions"] == 4
    assert all(r["generated_is_coarsest_exact"] for r in s4["families"])
    assert all(r["policies_evaluated"] == ["over", "under"] and r["abstain_counted_separately"] for r in s4["families"])
    planted = s4["planted_split_coarsening"]
    assert planted["caught"] and planted["false_retract_witness"] == {"profile": [[2]], "revoked": [1]}
    assert planted["false_retain_witness"] == {"profile": [[1]], "revoked": [1]}


def test_S5_S6_strategy_and_architecture_revision_preserve_authority(result):
    s5 = result["checks"]["S5_strategy_revision"]
    assert s5["signatures_unchanged"] == s5["records"] == 167
    assert s5["planted_readmission_under_weaker_channel"]["caught"]
    s6 = result["checks"]["S6_architecture_revision"]
    assert s6["signature_injective"] and s6["roundtrip_exact"] == 168
    assert s6["planted_encoding_dropping_last_coordinate"] == {"distinct_codes": 167, "collisions": 1, "caught": True}


def test_S7_every_transition_is_charged_and_free_mutation_is_caught(result):
    s7 = result["checks"]["S7_resource_conservation"]
    ops = [d["op"] for d in s7["transitions"]]
    assert ops == ["admit/instruction", "admit/interaction", "compose", "revoke{3}"]
    assert all(d["charged_positive"] and d["B_theta_constant"] for d in s7["transitions"])
    revoke = s7["transitions"][-1]["delta"]
    assert (revoke["W_update"], revoke["recourse"], revoke["abstentions"]) == (3, 2, 2)
    assert s7["planted_free_mutation"] == {"store_changed": True, "any_counter_changed": False, "caught": True}


def test_mutations_asserted_applied_and_detected(result):
    m = result["controls"]["mutations"]
    assert m["planted"] == m["detected"] == 4
    for k, v in m.items():
        if isinstance(v, dict):
            assert v["applied"] is True and v["detected"] is True, k
    assert m["M2_live_ignores_revocation"]["two_evaluator_agreement"]["agree"] < 2688
    # M3 must be caught for its registered reason: exactness disagrees with the independent judge
    assert m["M3_block_union_always_true"]["exact_partition_counts_under_mutation"] != {"singletons": 1, "pairs_01_23": 4, "nested_0_01_012": 1, "one_set_12": 4}


def test_S4_exactness_is_not_measurability_by_construction(mod):
    """The census must be able to disagree with the measurability judge: corrupt the
    store's block-union test alone and the exact-partition counts must change."""
    orig = mod.is_block_union
    mod.is_block_union = lambda r, pi: True
    try:
        res = mod.check_S4_representation_revision(4)
    finally:
        mod.is_block_union = orig
    counts = {r["gamma"]: r["exact_partitions"] for r in res["families"]}
    assert counts == {"singletons": 15, "pairs_01_23": 15, "nested_0_01_012": 15, "one_set_12": 15}
    assert res["holds"] is False
    # and the independent judge is untouched by that mutation
    assert mod.is_block_union_b(frozenset({1}), (frozenset({0}), frozenset({1, 2}), frozenset({3}))) is False
    assert mod.is_block_union_b(frozenset({1, 2}), (frozenset({0}), frozenset({1, 2}), frozenset({3}))) is True


def test_endpoint_only_and_certified_empty_records(mod):
    s = mod.Substrate(n=4)
    s.admit("fb", (1,), {"behaviour": (1,)}, "feedback", frozenset({"c"}))
    assert s.live("fb") is None  # no warrant exhibited: abstain, never retain or retract
    s.admit("empty", (1,), {"behaviour": (1,), "warrants": []}, "experimentation", frozenset({"c"}))
    assert s.live("empty") is False  # certified no warrant: dead


def test_exit_code_contract(mod, monkeypatch, capsys):
    assert mod.main([]) == 0
    capsys.readouterr()

    def cannot(*a, **k):
        raise mod.CannotCheck("planted")

    monkeypatch.setattr(mod, "run_reference_semantics", cannot)
    assert mod.main([]) == 2
    assert json.loads(capsys.readouterr().out)["terminal"] == "CANNOT_CHECK"

    def fail(*a, **k):
        raise AssertionError("planted")

    monkeypatch.setattr(mod, "run_reference_semantics", fail)
    assert mod.main([]) == 1
    assert json.loads(capsys.readouterr().out)["terminal"] == "FAIL"


def test_authority_fields_claim_nothing(result):
    a = result["authority"]
    assert a["semantics_frozen"] is False
    assert a["proof_assistant_encoding"].startswith("CANNOT_CHECK")
    assert a["novelty_established"] is False and a["architecture_superiority_established"] is False

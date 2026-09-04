from __future__ import annotations

import copy
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "research" / "orion-machine" / "reference" / "kso_m6_formal_math_v1.py"


def load():
    name = "kso_m6_formal_math_v1"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, MODULE)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def m6():
    return load()


@pytest.fixture(scope="module")
def result(m6):
    return m6.run_m6a()


def test_real_protected_lean_receipt_is_integrated(result):
    assert result["terminal"] == "M6A_FORMAL_MATH_VERIFIER_CHANNEL_INTEGRATED_PARENT_SUFFICIENT"
    s = result["source"]
    assert s["rows"] == 40
    assert s["kernel_verified"] == 20
    assert s["registered_rejections"] == 20
    assert s["cannot_check"] == 0 and s["disagreements"] == 0
    assert s["lean_version"] == "4.33.1"


def test_only_kernel_verified_proof_certificates_become_warranted_atoms(m6):
    receipt = m6.load_receipt()
    accepted, rejected = m6.validate_receipt(receipt)
    ks, atoms = m6.admit_verified_rows(receipt, accepted)
    assert len(atoms) == 20
    assert all(a.atom_id in ks.ids for a in atoms)
    assert all(m6.kso.profile_live(ks.atom_map()[a.atom_id].profile, ()) for a in atoms)
    rejected_ids = {m6._proof_atom_id(str(r["file"])) for r in rejected}
    assert rejected_ids.isdisjoint(set(ks.ids))


def test_proof_evidence_revocation_removes_its_warranted_path(result):
    life = result["kso"]["lifecycle"]
    assert life["source_file"] == "ok_F1_0007_1cd7ba.lean"
    assert life["pre_live"] is True
    assert life["post_live"] is False
    assert life["pre_navigation_share_positive"] is True
    assert life["post_navigation_share"] == "0"


def test_registered_corrupted_proofs_are_real_negative_controls(m6):
    receipt = m6.load_receipt()
    accepted, rejected = m6.validate_receipt(receipt)
    assert len(accepted) == len(rejected) == 20
    assert all(r["expect"] == "REJECT" for r in rejected)
    assert all(r["verdict"] == "REJECTED_FOR_THE_REGISTERED_REASON" for r in rejected)
    assert all(str(r["file"]).startswith("bad_") for r in rejected)


def test_hostile_receipt_mutations_are_blocked(result):
    assert result["hostiles"] == {
        "cannot_check_blocks_admission": 1,
        "corrupted_proof_cannot_be_promoted": 1,
        "oracle_disagreement_blocks_admission": 1,
        "row_count_drift_detected": 1,
    }


def test_cannot_check_is_distinct_from_pass(m6):
    receipt = m6.load_receipt()
    bad = copy.deepcopy(receipt)
    bad["cannot_check"] = 1
    with pytest.raises(m6.CannotCheck, match="CANNOT_CHECK"):
        m6.validate_receipt(bad)


def test_upstream_scientific_terminal_is_not_promoted(result):
    assert result["upstream_scientific_terminal"] == "PARENT_SUFFICIENT"
    a = result["authority"]
    assert a["formal_math_verifier_channel_integrated"] is True
    assert a["protected_campaign_rerun"] is False
    assert a["open_frontier_problem_solved"] is False
    assert a["frontier_math_discovery"] is False
    assert a["novelty"] is False
    assert a["M6_full"] is False


def test_main_exit_contract(m6, monkeypatch):
    assert m6.main([]) == 0
    original = m6.load_receipt
    monkeypatch.setattr(m6, "load_receipt", lambda path=m6.LEAN_RECEIPT: (_ for _ in ()).throw(m6.CannotCheck("planted")))
    try:
        assert m6.main([]) == 2
    finally:
        monkeypatch.setattr(m6, "load_receipt", original)

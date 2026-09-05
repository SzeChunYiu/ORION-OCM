"""M12: one persistent instance through A–G (principal ordering), identity continuity, kill gates,
the parent through the same lifetime, and the pre-registered tier rules on the recorded receipt."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from ocm.evaluation import m12_lifetime_eval as EV
from ocm.lifetime import machine as MC

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def lifetimes(tmp_path_factory):
    root = tmp_path_factory.mktemp("m12")
    return {arm: {"O1": EV.run_lifetime(arm, "O1", root)} for arm in ("ocm", "whole_system_parent")}


def test_one_persistent_instance_no_reset_and_no_kill_gate_hits(lifetimes):
    r = lifetimes["ocm"]["O1"]
    assert r["no_reset"] and len({row[2] for row in r["identity_trace"]}) == 1 and all(row[3] for row in r["identity_trace"])
    assert len(r["phases"]) == 8 and r["information"]["protected_exposure"] == 0 and r["resources"]["external_io"] == 0
    gates = EV.kill_gates(lifetimes)
    assert gates["hits"] == 0, gates


def test_phase_outcomes_on_the_principal_ordering(lifetimes):
    o, p = lifetimes["ocm"]["O1"]["phases"], lifetimes["whole_system_parent"]["O1"]["phases"]
    assert sum(o["A"]["conversations"]) >= 50 and o["A"]["always_attempts"] == 0
    assert all(o["B"]["success"]) and all(o["C"]["success"]) and o["C"]["route"] == "TRANSFER" and o["C"]["acquisition_cost"] < p["C"]["acquisition_cost"]
    assert all(o["D"]["causal"]) and all(o["D"]["communication"]) and not all(p["D"]["causal"])
    assert o["E"]["transfer_precision"] == 1.0 and o["E"]["harmful_accepted"] == 0 and p["E"]["harmful_accepted"] >= 1
    assert o["F"]["stale_behaviours"] == 0 and o["F"]["dependents_reopened"] == 3 and o["F"]["unrelated_intact"] == 2 and p["F"]["stale_behaviours"] >= 1
    assert o["G"]["diagnosis_correct"] and o["G"]["repaired"] and o["G"]["preserved"] and o["G"]["rollback_exact"] and not p["G"]["repaired"]
    assert o["unknown"]["unregistered_domain_no_action"]


def test_recorded_receipt_tiers_follow_the_preregistered_rules():
    d = json.loads((ROOT / "research/ocm-m12/M12_LIFETIME_EVAL_V2.json").read_text())
    det = d["deterministic"]
    assert det["gates"]["hits"] == 0 and det["tiers"]["tier0_operational"]["holds"]
    assert det["claims"]["A_conversations"]["n"] == 54 and det["claims"]["A_conversations"]["terminal"] in ("OCM_RESIDUAL", "EQUIVALENT", "PARENT_RESIDUAL", "INCONCLUSIVE")
    assert all(v["n"] < 40 or v["terminal"] != "DESCRIPTIVE (n < 40)" for v in det["claims"].values())
    assert d["exit_gate_before_replication"] in ("CANNOT_CHECK", "PARENT_SUFFICIENT", "FULL_OCM_RESIDUAL_SUPPORTED")
    assert "CANNOT_CHECK" in d["cannot_check"]["frontier_reference"]
    # a claim that never touched the parent cannot be a residual: the exit gate needs a matching replication receipt
    assert EV.exit_gate(det["tiers"], det["claims"], None) != "FULL_OCM_RESIDUAL_SUPPORTED" or not det["tiers"]["tier6_broad"]["holds"]

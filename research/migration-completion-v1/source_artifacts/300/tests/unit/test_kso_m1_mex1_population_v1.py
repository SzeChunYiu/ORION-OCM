"""KnowledgeSpace.v1 M1 — population from ME-X1 worlds and the M0 invariants on the machine.

Runs the public development split at one instance per family (10 worlds, seeded, deterministic).
The counts below are the receipt's own denominators; a change in the generator or the population
map changes them and must be re-pinned deliberately.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "research" / "orion-machine" / "reference" / "kso_m1_mex1_population_v1.py"


def _load():
    spec = importlib.util.spec_from_file_location("kso_m1_mex1_population_v1", MODULE)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load()


@pytest.fixture(scope="module")
def receipt(mod):
    return mod.run(per_family=1)


def test_population_totals_pinned(receipt):
    t = receipt["totals"]
    assert t["worlds"] == 10
    assert t["atoms"] == 748 and t["hyperedges"] == 351
    assert t["p2_cells"] == 126 and t["v1_p2_cells"] == 126
    assert t["p3_revocations"] == 80
    assert t["events_replayed"] == 10 and t["events_acquisition_needed"] == 0
    assert t["v1_revoked_base_atoms"] == 3 and t["v1_worlds_with_revocation_or_censoring"] == 2
    assert t["v0_oracle_negative_cells"] == 0 and t["v1_oracle_negative_cells"] == 2
    assert t["constraint_power_worlds_caught"] == 10 and t["p4_direction_i_worlds"] == 3
    assert receipt["power"]["P2_v0"].startswith("NO_POWER")


def test_every_world_is_dense_and_label_equals_oracle(receipt):
    for w in receipt["worlds"]:
        assert w["P1_dense"]["isolated"] == 0 and w["P1_dense"]["quarantined"] == 0
        assert w["P1_dense"]["planted_isolated_rejected"] == 1
        assert w["P2_label_equals_oracle"]["mismatches"] == 0
        assert w["P2_label_equals_oracle"]["planted_merged_family_label_caught"] == "CAUGHT"
        assert w["v1"]["P2_label_equals_oracle"]["mismatches"] == 0


def test_retraction_both_directions_on_real_worlds(receipt):
    raised = 0
    for w in receipt["worlds"]:
        p = w["P3_retraction"]
        assert p["revocations_checked"] == 8
        assert p["dead_atoms_zero"] == p["unreachable_atoms_unchanged"] == p["reachable_atoms_never_gain"] == p["reinstatement_restores"] == 8
        raised += p["renormalising_parent_raised_unreachable_atom"]
        assert w["P3_events"]["status"] == "REPLAYED" and w["P3_events"]["claim_cells_disagree"] == 0
    assert raised >= 1


def test_hub_two_directions_discriminating_form(receipt):
    holds = 0
    for w in receipt["worlds"]:
        d = w["P4_hub"]["direction_i"]
        if d["holds"]:
            holds += 1
            assert d["hub_raw_rank"] == 1 and d["hub_surprise_rank"] != 1 and d["planted_popularity_ranker_differs"]
        assert w["P4_hub"]["direction_ii_hub_only"]["status"].startswith("NOT_DISCRIMINATING")
        assert w["P4_hub"]["direction_iii_background"]["status"].startswith("IDENTITY")
    assert holds >= 1


def test_constraint_edge_is_powered_by_derived_negative_evidence_worlds(receipt):
    for w in receipt["worlds"]:
        c = w["P2_constraint_power"]
        assert c["nocontra_status"] == "INVALID" and c["claim_label_dead"] and c["oracle_support"] is False
        assert c["tail_drop_mutant_caught"] == "CAUGHT"


def test_receipt_self_bindings_match_the_committed_files():
    receipt = json.loads((ROOT / "research" / "orion-machine" / "results" / "KSO_M1_POPULATION_RECEIPT_V1.json").read_text(encoding="utf-8"))
    where = {"mex1_generator.py": ROOT / "research/experiments/me-x1", "mex1_oracle.py": ROOT / "research/experiments/me-x1", "mex1_model.py": ROOT / "research/experiments/me-x1",
             "kso_math_v1.py": ROOT / "research/orion-machine/reference", "kso_m0_freeze_checks_v1.py": ROOT / "research/orion-machine/reference", "kso_m1_mex1_population_v1.py": ROOT / "research/orion-machine/reference"}
    for name, digest in receipt["bindings"].items():
        assert hashlib.sha256((where[name] / name).read_bytes()).hexdigest() == digest, name
    freeze = json.loads((ROOT / "research" / "orion-machine" / "results" / "KSO_M0_FREEZE_V1.json").read_text(encoding="utf-8"))
    for rel, digest in freeze["bindings"].items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == digest, rel
    assert freeze["m1_receipt_body_sha256"] == receipt["provenance"]["body_sha256"]


def test_genome_holds_and_is_unchanged_by_population(receipt, mod):
    for w in receipt["worlds"]:
        g = w["P5_genome"]
        assert g["S1"] and g["S2"] and g["S3_sampled"] and g["S4_identity_measurable"] and g["S4_merged_pair_not_measurable"]
        assert g["S5_policy_swap_invariant"] and g["S6_labels_canonical"] and g["S7_metered"] and g["genome_digest_unchanged"]
    assert receipt["genome_digest"] == mod.m0.genome_digest()


def test_protected_split_is_refused_as_cannot_check(mod):
    with pytest.raises(mod.CannotCheck):
        mod.run(split="protected", per_family=1)
    with pytest.raises(mod.CannotCheck):
        mod.run(per_family=6)


def test_gated_seed_gives_dead_atom_zero_activation(mod):
    ks = mod.KnowledgeSpace(
        (mod.Atom("a", "claim", (frozenset({0}),)), mod.Atom("b", "claim", mod.ONE)),
        (mod.Hyperedge("ab", ("a",), ("b",), "SUPPORT", profile=mod.ONE),),
    )
    a = mod.activation(ks, mod.uniform(ks), Fraction(1, 2), revoked={0})
    assert a["a"] == 0 and a["b"] == Fraction(1, 4)
    a0 = mod.activation(ks, mod.uniform(ks), Fraction(1, 2))
    assert a0["b"] == Fraction(1, 4) + Fraction(1, 2) * Fraction(1, 4)


def test_bindings_cover_generator_oracle_and_checkers(receipt):
    assert set(receipt["bindings"]) == {"mex1_generator.py", "mex1_oracle.py", "mex1_model.py", "kso_math_v1.py", "kso_m0_freeze_checks_v1.py", "kso_m1_mex1_population_v1.py"}
    assert all(len(v) == 64 for v in receipt["bindings"].values())


def test_populate_with_request_adds_one_goal_atom_with_dependence_edges(mod):
    gen, model, oracle = mod._mex1()
    inst, exp = gen.generate_split("dev", "ME-X1-DEV-20260902", {model.FAMILIES[0]: 1})[0]
    w1 = oracle.final_world(inst.world_v0, inst.events)
    base = mod.populate(w1)
    pop = mod.populate(w1, request=inst.request, request_id=inst.instance_id)
    rid = f"req:{inst.instance_id}"
    assert len(pop.space.atoms) == len(base.space.atoms) + 1
    goal_edges = [e for e in pop.space.hyperedges if e.tails == (rid,)]
    assert goal_edges and goal_edges[0].heads == (f"claim:{inst.request.target_claim_id}",) and goal_edges[0].relation_type == "DEPENDENCE"
    assert (len(goal_edges) == 2) == bool(inst.request.result_id and f"res:{inst.request.result_id}" in pop.space.ids)
    assert pop.governed.certificates[rid] == mod.Cert.INSTRUCTION
    assert mod.check_P1_dense(pop)["isolated"] == 0

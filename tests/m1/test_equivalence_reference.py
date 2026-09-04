"""M1 D3 — no architecture laundering: the canonical package reproduces the frozen reference."""
from __future__ import annotations

import random
from fractions import Fraction as F
from itertools import combinations

import pytest

from ocm.historical import load_reference
from ocm.kso import admission as AD
from ocm.kso import checks as C
from ocm.kso import navigation as N
from ocm.kso import space as S
from ocm.kso.warrant import WarrantProfile


@pytest.fixture(scope="module")
def ref():
    return load_reference("kso_math_v1")


@pytest.fixture(scope="module")
def frz():
    return load_reference("kso_m0_freeze_checks_v1")


@pytest.mark.parametrize("witness", ["retraction_witness_space", "hub_witness_space", "navigation_witness_space"])
@pytest.mark.parametrize("revoked", [(), (0,), (0, 1)])
def test_matrix_and_fixed_point_match_reference(ref, frz, witness, revoked):
    ksr = getattr(frz, witness)()
    ks = S.from_reference(ksr)
    assert N.navigation_matrix(ks, revoked=revoked).as_lists() == ref.navigation_matrix(ksr, revoked=revoked)
    seed = frz.seed_vector(ksr, {ksr.ids[0]: F(1)})
    assert N.fixed_point(ks, seed, F(1, 3), revoked=revoked) == frz.fixed_point(ksr, seed, F(1, 3), revoked=revoked)


def test_round_trip_to_reference_is_identity_on_projected_fields(ref, frz):
    ksr = frz.retraction_witness_space()
    back = S.to_reference(S.from_reference(ksr), ref)
    assert [(a.atom_id, a.atom_type, a.profile, a.quarantined) for a in back.atoms] == [(a.atom_id, a.atom_type, a.profile, a.quarantined) for a in ksr.atoms]
    assert [(e.edge_id, e.tails, e.heads, e.relation_type, e.weight, e.profile) for e in back.hyperedges] == [(e.edge_id, e.tails, e.heads, e.relation_type, e.weight, e.profile) for e in ksr.hyperedges]


def test_random_spaces_match_reference_under_every_revocation(ref):
    rng = random.Random(7)
    n = 0
    for _ in range(25):
        ks = C.random_space(rng)
        ksr = S.to_reference(ks, ref)
        for r in range(4):
            for R in combinations(range(3), r):
                assert N.navigation_matrix(ks, revoked=R).as_lists() == ref.navigation_matrix(ksr, revoked=R)
                n += 1
    assert n == 25 * 8


def test_f_checks_reproduced(frz):
    """The inherited freeze checkers' own denominators are reproduced by the canonical checkers."""
    assert C.check_navigation_outcomes()["distinct_outcomes"] == 3
    hub = C.check_hub_two_directions()
    assert hub["background_zero_surprise_atoms"] == len(frz.hub_witness_space().ids)
    adm = C.check_admission_channels()
    for k in ("instruction_connected", "isolated_live", "isolated_quarantined", "feedback_unwarranted_cannot_fire", "exact_checker_warrants_firing", "warranting_channel_without_warrant", "unregistered_relation"):
        assert k in adm["cases"]
    ret = C.check_retraction_propagation()
    assert ret["matches_reference"] == 1


def test_documented_tightening_composition_warrant_mismatch(frz):
    """Reference F4 case 1 admits a COMPOSITION head whose warrant is not bridge ⊗ tails; the
    canonical admit rejects it (KS-S2 at admission).  Recorded as a documented tightening."""
    base = S.KnowledgeSpace((S.Atom("a", "claim"), S.Atom("b", "claim")), (S.Hyperedge("ab", ("a",), ("b",), "DEPENDENCE"),))
    with pytest.raises(S.TypedRejection) as exc:
        AD.admit(base, S.Atom("c", "procedure", WarrantProfile.of({1})), (S.Hyperedge("bc", ("b",), ("c",), "COMPOSITION"),), "INSTRUCTION")
    assert exc.value.code == "COMPOSITION_WARRANT_MISMATCH"
    ks, r = AD.admit(base, S.Atom("c", "procedure", WarrantProfile.of({1})), (S.Hyperedge("bc", ("b",), ("c",), "COMPOSITION", warrant=WarrantProfile.of({1})),), "INSTRUCTION")
    assert r.warranted and AD.ks_S2_composition(AD.GovernedSpace(ks, {"a": "INSTRUCTION", "b": "INSTRUCTION", "c": "INSTRUCTION"}))


def test_inherited_certificate_kinds_are_a_subset():
    inherited = {"INSTRUCTION", "DEMONSTRATION", "INTERACTION", "EXPERIMENTATION", "FEEDBACK", "EXACT_CHECKER"}
    assert inherited <= {k.value for k in AD.CertificateKind}
    assert {k.value for k in AD.CertificateKind} - inherited == {"OBSERVATION", "IMPORTED"}

"""M2 §3.2–3.3 evidence registry with dependence (MEG-01) and nogoods (MEG-16)."""
from __future__ import annotations

import pytest

from ocm.kso import nogoods as NG
from ocm.kso.admission import CertificateKind
from ocm.kso.types import Scope
from ocm.kso.warrant import Liveness, WarrantProfile as WP
from ocm.store.evidence import Admission, Channel, EvidenceRegistry, mutant_majority_truth


def test_eight_channels_map_onto_certificate_kinds_and_feedback_never_warrants():
    assert {c.certificate for c in Channel} == set(CertificateKind)
    r = EvidenceRegistry()
    _, fb = r.register({"reward": 1}, Channel.FEEDBACK, "user")
    _, ob = r.register({"obs": "x"}, Channel.OBSERVATION, "sensor")
    assert r.liveness([ob.evidence_id]) is Liveness.LIVE
    assert r.liveness([fb.evidence_id]) is Liveness.DEAD and r.liveness([ob.evidence_id, fb.evidence_id]) is Liveness.DEAD


def test_duplicate_bytes_vs_duplicate_content_vs_overlap_are_distinct():
    r = EvidenceRegistry()
    o1, a = r.register({"p": 1}, Channel.INSTRUCTION, "teacher-A")
    o2, a2 = r.register({"p": 1}, Channel.INSTRUCTION, "teacher-A")
    o3, b = r.register({"p": 1}, Channel.INSTRUCTION, "teacher-B")
    o4, c = r.register({"p": 2}, Channel.INSTRUCTION, "teacher-B", overlaps=[a.evidence_id])
    assert (o1, o2, o3, o4) == (Admission.ADMITTED, Admission.DUPLICATE_BYTES, Admission.DUPLICATE_CONTENT, Admission.OVERLAP)
    assert a2.evidence_id == a.evidence_id and b.evidence_id != a.evidence_id
    assert ("SAME_CONTENT", a.evidence_id) in b.links and ("OVERLAPS", a.evidence_id) in c.links


def test_contradiction_registers_a_nogood_and_never_majority_votes():
    r = EvidenceRegistry()
    _, x = r.register({"claim": "moon=cheese"}, Channel.INSTRUCTION, "user-1")
    _, y = r.register({"claim": "moon=rock"}, Channel.OBSERVATION, "probe", contradicts=[x.evidence_id])
    assert r.liveness([x.evidence_id]) is Liveness.LIVE and r.liveness([y.evidence_id]) is Liveness.LIVE
    assert r.liveness([x.evidence_id, y.evidence_id]) is Liveness.DEAD   # cannot both warrant one claim
    for i in range(5):
        r.register({"claim": "moon=cheese", "i": i}, Channel.INSTRUCTION, f"user-{i+2}")
    votes = {"cheese": [e for e, rec in r.records.items() if "cheese" in rec.source or rec.content_hash != y.content_hash and e != y.evidence_id], "rock": [y.evidence_id]}
    assert mutant_majority_truth(r, votes) == "cheese"  # the mutant's answer
    assert r.liveness([y.evidence_id]) is Liveness.LIVE    # the registry's: warrant, not count


def test_supersession_closes_the_old_epoch_and_keeps_history():
    r = EvidenceRegistry()
    _, old = r.register({"meeting": "tue"}, Channel.INTERACTION, "user", scope=Scope.of("conv", epoch=(0, float("inf"))))
    _, new = r.register({"meeting": "wed"}, Channel.INTERACTION, "user", scope=Scope.of("conv", epoch=(5, float("inf"))), supersedes=old.evidence_id)
    assert r.records[old.evidence_id].superseded_by == new.evidence_id
    assert r.records[old.evidence_id].scope.epoch == (0, 5) and ("SUPERSEDES", old.evidence_id) in new.links
    assert old.evidence_id in r.records  # history is never deleted


def test_derived_evidence_carries_its_assumptions_and_revocation_is_assumption_only():
    r = EvidenceRegistry()
    _, a = r.register({"raw": 1}, Channel.OBSERVATION, "sensor")
    _, d = r.register({"derived": "summary"}, Channel.IMPORTED, "pipeline", derived_from=r.citation_warrant([a.evidence_id]))
    assert not d.is_assumption and r.citation_warrant([d.evidence_id]).evidence == {a.evidence_id}
    with pytest.raises(ValueError):
        r.revoke([d.evidence_id])
    r.revoke([a.evidence_id])
    assert r.liveness([d.evidence_id]) is Liveness.DEAD
    o, d2 = r.register({"derived": "summary-again"}, Channel.IMPORTED, "pipeline-2", derived_from=r.citation_warrant([a.evidence_id]))
    assert o is Admission.REVOKED_SOURCE_REAPPEARED and r.liveness([d2.evidence_id]) is Liveness.DEAD
    r.reinstate([a.evidence_id])
    assert r.liveness([d.evidence_id]) is Liveness.LIVE


def test_shared_assumption_never_counts_twice():
    r = EvidenceRegistry()
    _, a = r.register({"src": "wire"}, Channel.OBSERVATION, "agency")
    _, p1 = r.register({"paper": 1}, Channel.IMPORTED, "outlet-1", derived_from=r.citation_warrant([a.evidence_id]))
    _, p2 = r.register({"paper": 2}, Channel.IMPORTED, "outlet-2", derived_from=r.citation_warrant([a.evidence_id]))
    _, q = r.register({"src": "own-lab"}, Channel.EXPERIMENT, "lab")
    assert r.independent_support_count([[p1.evidence_id], [p2.evidence_id]]) == 1
    assert r.independent_support_count([[p1.evidence_id], [q.evidence_id]]) == 2


def test_nogood_algebra_exhaustive_and_mutant():
    out = NG.check_nogoods(3)
    assert out["meet_strict_cases"] > 0 and out["join_commutation_checks"] == out["meet_inequality_checks"]
    ng = NG.NogoodSet.of({0, 1})
    p, q = WP.of({0}), WP.of({1})
    assert ng.liveness(p, ()) is Liveness.LIVE and ng.liveness(p.meet(q), ()) is Liveness.DEAD
    assert NG.mutant_filter_before_compose(ng, p.lower, q.lower) == (frozenset({0, 1}),)

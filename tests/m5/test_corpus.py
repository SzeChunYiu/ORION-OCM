"""M5 §6: raw text yields ungrounded form hypotheses only; grounding needs aligned evidence; the
frequency-grounds hostile is what the rule forbids."""
from __future__ import annotations

from ocm.learning.language import corpus as CO

TEXT = ("the robot opened the door. the robot pushed the door. the robot lifted the box. "
        "the portal opened. the portal opened again. the portal was opened by the robot. the door opened. "
        "the robot kicked the ball. the robot kicked the door. the robot lifted the ball. "
        "the robot will push the box. the robot will lift the cup. the robot will kick the ball. ") * 3


def test_mining_yields_ungrounded_hypotheses_that_the_interpreter_cannot_consult():
    hs = CO.mine(TEXT, "ev:corpus1")
    kinds = {h.kind for h in hs}
    assert kinds == {"token", "suffix", "collocation"}
    portal = next(h for h in hs if h.form_id == "token:portal")
    assert portal.status is CO.FormStatus.UNGROUNDED_FORM_ONLY and portal.count >= 9 and not CO.consultable(portal)
    assert portal.authority.rank("world_truth") == 0 and portal.authority.rank("corpus") == 1
    suf = next(h for h in hs if h.form_id == "suffix:ed")
    assert set(suf.content["stems_with_base_form"]) >= {"kick", "lift", "push"}
    assert any(h.form_id == "colloc:the_robot" for h in hs)


def test_binding_only_through_aligned_evidence_and_revocation_returns_to_revoked():
    hs = {h.form_id: h for h in CO.mine(TEXT, "ev:corpus1")}
    portal = hs["token:portal"]
    CO.propose_binding(portal, "door")
    assert portal.status is CO.FormStatus.CANDIDATE_SEMANTIC_BINDING and not CO.consultable(portal)
    try:
        CO.bind(portal, "door", ["ev:corpus1"], channel="corpus")
        assert False, "corpus evidence must not bind"
    except ValueError:
        pass
    CO.bind(portal, "gateway", ["ev:demo7"], channel="demonstration")
    assert portal.status is CO.FormStatus.GROUNDED_CONSTRUCTION and CO.consultable(portal)
    assert portal.warrant().evidence == {"ev:corpus1", "ev:demo7"} and portal.authority.rank("world_truth") == 0
    CO.revoke(portal, {"ev:demo7"})
    assert portal.status is CO.FormStatus.REVOKED
    CO.contradict(hs["colloc:the_robot"], "ev:counter")
    assert hs["colloc:the_robot"].status is CO.FormStatus.CONTRADICTED


def test_frequency_never_grounds_and_the_mutant_does():
    hs = {h.form_id: h for h in CO.mine(TEXT, "ev:corpus1")}
    portal = hs["token:portal"]
    assert not CO.consultable(portal)
    m = CO.mutant_frequency_grounds(portal, "door", threshold=5)
    assert CO.consultable(m) and m.authority.rank("world_truth") == 1     # the laundering the rule forbids

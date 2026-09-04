"""M2 §6 learner lifecycle hostiles on the reference version-space learner."""
from __future__ import annotations

from ocm.kso.admission import CertificateKind
from ocm.kso.warrant import Liveness
from ocm.learning import learner as L

AND = {"AND": lambda x: int(x[0] and x[1]), "OR": lambda x: int(x[0] or x[1]), "XOR": lambda x: int(x[0] != x[1]), "FIRST": lambda x: x[0]}
DOMAIN = ((0, 0), (0, 1), (1, 0), (1, 1))


def _learner(contracts=()):
    return L.VersionSpaceLearner("skill:and", AND, DOMAIN, contracts=tuple(contracts))


def _demo(i, pairs):
    return L.Experience(f"x{i}", L.ExperienceKind.DEMONSTRATION, f"ev:{i}", "skill:and", {"pairs": pairs}, "teacher")


def test_insufficient_examples_never_promote_and_ambiguity_is_preserved():
    lr = _learner()
    lr.observe(_demo(1, [((1, 1), 1)]))
    p = lr.propose_updates()[-1]
    assert p.kind is L.UpdateKind.QUARANTINE and p.status is L.UpdateStatus.GAP_AMBIGUOUS
    assert set(p.payload["candidates"]) == {"AND", "FIRST", "OR"}


def test_complete_demonstrations_promote_with_evidence_warrant_and_revocation_reopens():
    lr = _learner()
    lr.observe(_demo(1, [((1, 1), 1), ((0, 1), 0)]))
    lr.observe(_demo(2, [((1, 0), 0)]))
    p = lr.propose_updates()[-1]
    assert p.kind is L.UpdateKind.OBJECT and p.status is L.UpdateStatus.PASS and p.payload["hypothesis"] == "AND"
    assert p.warrant.evidence == {"ev:1", "ev:2"} and p.certificate is CertificateKind.DEMONSTRATION
    assert p.warrant.liveness(("ev:2",)) is Liveness.DEAD and p.warrant.liveness(("ev:9",)) is Liveness.LIVE


def test_contradiction_is_preserved_not_averaged():
    lr = _learner()
    lr.observe(_demo(1, [((1, 1), 1)]))
    lr.observe(_demo(2, [((1, 1), 0)]))
    p = lr.propose_updates()[-1]
    assert p.status is L.UpdateStatus.CONTRADICTION and p.kind is L.UpdateKind.QUARANTINE
    assert L.mutant_average_contradiction(lr).kind is L.UpdateKind.OBJECT  # the mutant picks a winner


def test_feedback_updates_behaviour_only_unless_a_contract_licenses_it():
    lr = _learner()
    lr.observe(_demo(1, [((1, 1), 1), ((0, 1), 0), ((1, 0), 0)]))
    lr.observe(L.Experience("f1", L.ExperienceKind.FEEDBACK, "ev:fb", "skill:and", {"reward": 1.0, "pairs": [((0, 0), 1)]}, "user"))
    props = lr.propose_updates()
    kinds = {p.kind for p in props}
    assert L.UpdateKind.BEHAVIOUR in kinds
    obj = [p for p in props if p.kind is L.UpdateKind.OBJECT][0]
    assert "ev:fb" not in obj.warrant.evidence            # unlicensed feedback never pins the object
    assert L.mutant_feedback_mints_warrant(lr).warrant.evidence == {"ev:fb"}
    lic = _learner(contracts=[L.FeedbackContract("skill:and", "sandbox:v1")])
    lic.observe(_demo(1, [((1, 1), 1), ((0, 1), 0), ((1, 0), 0)]))
    lic.observe(L.Experience("f1", L.ExperienceKind.FEEDBACK, "ev:obs", "skill:and", {"reward": 1.0, "pairs": [((0, 0), 0)], "outcome_function_id": "sandbox:v1"}, "sandbox"))
    obj2 = [p for p in lic.propose_updates() if p.kind is L.UpdateKind.OBJECT][0]
    assert "ev:obs" in obj2.warrant.evidence               # licensed: an observation of the registered outcome


def test_instruction_names_a_hypothesis_but_is_checked_against_demonstrations():
    lr = _learner()
    lr.observe(L.Experience("i1", L.ExperienceKind.INSTRUCTION, "ev:book", "skill:and", {"hypothesis": "OR"}, "book"))
    lr.observe(_demo(1, [((0, 1), 0)]))   # refutes OR
    p = lr.propose_updates()[-1]
    assert p.payload.get("hypothesis") != "OR" and p.status in (L.UpdateStatus.GAP_AMBIGUOUS, L.UpdateStatus.PASS)
    lr2 = _learner()
    lr2.observe(L.Experience("i1", L.ExperienceKind.INSTRUCTION, "ev:book", "skill:and", {"hypothesis": "AND"}, "book"))
    p2 = lr2.propose_updates()[-1]
    assert p2.status is L.UpdateStatus.PASS and p2.certificate is CertificateKind.INSTRUCTION and p2.warrant.evidence == {"ev:book"}

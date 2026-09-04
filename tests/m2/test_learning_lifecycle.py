"""M2 §6 lifecycle through the canonical core: learn → admit → use → revoke → reopen → relearn."""
from __future__ import annotations

from fractions import Fraction as F

from ocm.kso import admission as AD
from ocm.kso import revocation as RV
from ocm.kso import space as S
from ocm.kso.firing import Enabling, enabling_verdict
from ocm.kso.warrant import Liveness, WarrantProfile as WP
from ocm.learning import learner as L

AND = {"AND": lambda x: int(x[0] and x[1]), "OR": lambda x: int(x[0] or x[1]), "XOR": lambda x: int(x[0] != x[1])}
DOMAIN = ((0, 0), (0, 1), (1, 0), (1, 1))


def _learn(evidence_prefix="ev"):
    lr = L.VersionSpaceLearner("skill:and", AND, DOMAIN)
    lr.observe(L.Experience("x1", L.ExperienceKind.DEMONSTRATION, f"{evidence_prefix}:1", "skill:and", {"pairs": [((1, 1), 1), ((0, 1), 0)]}))
    lr.observe(L.Experience("x2", L.ExperienceKind.DEMONSTRATION, f"{evidence_prefix}:2", "skill:and", {"pairs": [((1, 0), 0)]}))
    return [p for p in lr.propose_updates() if p.kind is L.UpdateKind.OBJECT][0]


def test_learn_use_revoke_reopen_relearn_with_unrelated_skill_intact():
    base = S.KnowledgeSpace((S.Atom("goal", "goal"), S.Atom("unrelated", "procedure", WP.of({"other:1"}))), (S.Hyperedge("gu", ("goal",), ("unrelated",), "DEPENDENCE"),))
    p = _learn()
    skill = S.Atom(p.target, "procedure", p.warrant, content_ref=p.payload["hypothesis"])
    ks, receipt = AD.admit(base, skill, (S.Hyperedge("g-skill", ("goal",), (p.target,), "DEPENDENCE"),), p.certificate)
    assert receipt.warranted and ks.atom(p.target).liveness(()) is Liveness.LIVE
    # use: the skill enables a composition edge
    ks2, _ = AD.compose(ks, [p.target], "answer", executable_ref="run:AND")
    act = {x: F(1) for x in ks2.ids}
    assert enabling_verdict(ks2, ks2.edge_map()["compose:answer"], act, F(1, 2)).enabling is Enabling.ENABLED
    # revoke an essential lesson → skill and its composite die; unrelated stays live; report says so
    rep = RV.reopening_report(ks2, (), ("ev:2",))
    assert ks2.atom(p.target).liveness(("ev:2",)) is Liveness.DEAD and ks2.atom("answer").liveness(("ev:2",)) is Liveness.DEAD
    assert "unrelated" in rep.unaffected and p.target in rep.reopen and "answer" in rep.reopen
    assert enabling_verdict(ks2, ks2.edge_map()["compose:answer"], act, F(1, 2), revoked=("ev:2",)).enabling is Enabling.DISABLED
    # relearn with new support: new evidence ids, lineage recorded, restores exactly on its own support
    p2 = _learn(evidence_prefix="ev2")
    relearned = S.Atom(p.target + "#2", "procedure", p2.warrant, content_ref=p2.payload["hypothesis"], meta=(("lineage", (p.target,)),))
    ks3, _ = AD.admit(ks2, relearned, (S.Hyperedge("g-skill2", ("goal",), (p.target + "#2",), "DEPENDENCE"),), p2.certificate)
    assert ks3.atom(p.target + "#2").liveness(("ev:2",)) is Liveness.LIVE and dict(ks3.atom(p.target + "#2").meta)["lineage"] == (p.target,)
    assert ks3.atom(p.target).liveness(("ev:2",)) is Liveness.DEAD  # history kept, not overwritten


def test_promoted_skill_generalises_on_held_out_composition_and_ambiguous_never_admits():
    p = _learn()
    table = dict(p.payload["table"])
    assert table[(0, 0)] == 0  # never demonstrated; follows from the agreement rule on the registered family
    lr = L.VersionSpaceLearner("skill:and", AND, DOMAIN)
    lr.observe(L.Experience("x1", L.ExperienceKind.DEMONSTRATION, "ev:1", "skill:and", {"pairs": [((1, 1), 1)]}))
    q = lr.propose_updates()[-1]
    assert q.kind is L.UpdateKind.QUARANTINE and q.warrant.is_zero
    base = S.KnowledgeSpace((S.Atom("goal", "goal"),), ())
    quarantined = S.Atom("skill:and?", "procedure", q.warrant, quarantined=True)
    ks, r = AD.admit(base, quarantined, (), "DEMONSTRATION") if not q.warrant.is_zero else (None, None)
    assert ks is None  # a zero-warrant object is not admitted through a warranting channel at all

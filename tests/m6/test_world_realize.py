"""M6 §4–§6: bounded world with provenance (assert / verify kept apart; revoke one source reopens
exactly), and realisation as a checked codec."""
from __future__ import annotations

from pathlib import Path

from ocm.knowledge import world as KW
from ocm.kso.warrant import Liveness
from ocm.language import constructions as C
from ocm.language import interpret as I
from ocm.language import meaning as M
from ocm.language import realize as RZ
from ocm.runtime.ocm_runtime import OCMRuntime
from tests.m3.test_interpretation import _lexicon

MANIFEST = Path(__file__).resolve().parents[2] / "research" / "ocm-m6" / "KNOWLEDGE_MANIFEST_V1.json"


def test_world_loads_manifest_and_keeps_assertion_verification_and_repetition_apart(tmp_path):
    rt = OCMRuntime(tmp_path / "rt")
    w = KW.KnowledgeWorld(rt)
    rep = w.load_manifest(MANIFEST)
    assert rep["facts"] >= 50 and rep["verified"] >= 45 and rep["documents"] == 3
    paris = w.facts["geo:paris:france"]
    assert w.liveness("geo:paris:france") is Liveness.LIVE and w.authority("geo:paris:france").rank("verified") == 1
    alm = w.facts["alm:paris:population"]
    assert w.liveness("alm:paris:population") is Liveness.LIVE and w.authority("alm:paris:population").rank("verified") == 0   # source claim only
    assert w.authority("alm:paris:population").rank("world_truth") == 0
    # lookup by meaning
    f, lv = w.lookup(KW.triple("paris", "LOCATED_IN", "france"))
    assert f is paris and lv is Liveness.LIVE
    assert w.lookup(KW.triple("paris", "LOCATED_IN", "spain")) == (None, Liveness.UNKNOWN)
    # a wrong source asserting the contrary is a live *source claim*, not knowledge; both are on record
    rum, lv2 = w.lookup(KW.triple("paris", "LOCATED_IN", "germany"))
    assert rum is not None and lv2 is Liveness.LIVE and w.authority(rum.fact_id).rank("verified") == 0
    # repetition never raises authority; the mutant does
    for _ in range(5):
        w.assert_fact("rum:paris:germany", rum.meaning, "geography", "rumour:v1")
    assert w.authority("rum:paris:germany").rank("verified") == 0
    assert KW.mutant_repetition_raises_authority(w, "rum:paris:germany", 3).rank("verified") == 1


def test_revoking_one_source_reopens_exactly_its_facts(tmp_path):
    rt = OCMRuntime(tmp_path / "rt")
    w = KW.KnowledgeWorld(rt)
    w.load_manifest(MANIFEST)
    rep = w.revoke_source("rumour:v1")
    assert rep["facts_dead"] == ["rum:paris:germany"]
    assert w.liveness("geo:paris:france") is Liveness.LIVE and w.liveness("alm:paris:population") is Liveness.LIVE
    rep2 = w.revoke_source("almanac:v1")
    assert set(rep2["facts_dead"]) == {"rum:paris:germany", "alm:paris:population", "alm:sweden:cold"}
    assert len(w.about("paris")) == 2 and set(w.relations_of("paris")) == {"LOCATED_IN", "CAPITAL_OF"}


def test_realisation_is_a_checked_codec():
    lx = _lexicon()
    cons = C.seed_constructions()
    ex = M.example_meanings()
    m = ex["the robot opened the red door"]
    reals = RZ.realize(m, lx, cons)
    texts = {r.construction_id: (r.text, r.checked) for r in reals}
    assert texts["en:transitive"] == ("The robot opened the red door.", True)
    assert texts["en:passive"] == ("The red door was opened by the robot.", True)
    neg = RZ.realize(ex["the robot did not open the door"], lx, cons, style=RZ.Style(contractions=True))
    assert neg[0].text == "The robot didn't open the door." and neg[0].checked
    q = RZ.realize(ex["did the robot open the door"], lx, cons)
    assert q[0].text == "Did the robot open the door?" and q[0].checked
    # a mutant paraphrase that drops the negation is caught by reverse reading
    bad = RZ.mutant_paraphrase_changes_negation(neg[0])
    r = I.interpret(bad.text.rstrip("."), lx, cons)
    assert r.verdict is not I.Verdict.INTERPRETED or M.canonical(r.meaning)[1] != bad.digest
    # style: passive preferred; pronoun only where certified safe
    p = RZ.realize(m, lx, cons, style=RZ.Style(prefer_passive=True))
    assert RZ.best(p).construction_id == "en:passive"
    pro = RZ.realize(ex["the robot did not open the door"], lx, cons, style=RZ.Style(pronoun_for={"robot": "it"}))
    assert pro[0].text == "It did not open the door." and pro[0].checked is False    # pronoun surface does not reverse-read to the full meaning: reported, not used
    # revoked lexeme evidence: no realisation
    assert RZ.realize(m, lx, cons, revoked={"ev:robot"}) == []

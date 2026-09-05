"""M5 §11 active learning, §12 negative transfer, §13 multilingual preflight, §14 retention."""
from __future__ import annotations

from ocm.language import acquisition as AQ
from ocm.language import constructions as C
from ocm.language import interpret as I
from ocm.language import lexicon as L
from ocm.language import meaning as M
from ocm.learning.language import active as A
from ocm.learning.language import transfer as T
from tests.m5.test_lexical import tr
from tests.m3.test_acquisition import _lexicon as _sov_lexicon


def test_active_learner_prefers_the_most_informative_admissible_action_and_never_asks_gold():
    vs = {"h1": 1, "h2": 2, "h3": 3, "h4": 4}
    ask_example = A.Action(A.ActionKind.ASK_EXAMPLE, "u", 1.0, lambda h: h % 2)          # splits 2/2
    propose = A.Action(A.ActionKind.PROPOSE_AND_CONFIRM, "h1", 0.5, lambda h: h == 1)    # splits 1/3
    sandbox = A.Action(A.ActionKind.TEST_IN_SANDBOX, "u", 2.0, lambda h: h)              # pins everything
    gold = A.Action(A.ActionKind.ASK_GOLD_LABEL, "u", 0.1, lambda h: h)
    ch = A.choose(vs, [ask_example, propose, sandbox, gold])
    assert ch.action is not None and ch.action.kind is not A.ActionKind.ASK_GOLD_LABEL
    assert A.expected_elimination(vs, sandbox) == 3.0 and A.expected_elimination(vs, ask_example) == 2.0
    assert ch.action.kind in (A.ActionKind.ASK_EXAMPLE, A.ActionKind.PROPOSE_AND_CONFIRM)   # best elimination per cost
    assert A.choose({"h1": 1}, [ask_example]).action is None
    assert A.mutant_ask_gold_label(vs, [gold]).action.kind is A.ActionKind.ASK_GOLD_LABEL   # the prohibited action
    regret = A.oracle_regret(vs, [ask_example, propose, sandbox, gold], ch.action, true_h=3)
    assert regret >= 0.0


def test_transfer_decisions_and_precision():
    ok = T.propose_transfer("meaning:transitive", T.TransferClass.MEANING_STRUCTURE, "en", "sov")
    wo = T.propose_transfer("cons:en:transitive", T.TransferClass.WORD_ORDER, "en", "sov")
    ce = T.propose_transfer("meaning:x", T.TransferClass.MEANING_STRUCTURE, "en", "sov", counter_evidence=["ev:sov-demo"])
    sense = T.propose_transfer("sense:bank:fin", T.TransferClass.SENSE, "finance", "general", same_kind_of_scope="domain")
    style = T.propose_transfer("style:archaic", T.TransferClass.STYLE, "novel", "novel2", same_kind_of_scope="register")
    assert ok.allowed and not wo.allowed and not ce.allowed and not sense.allowed and not style.allowed
    prec = T.transfer_precision([(ok, True), (wo, False), (ce, False), (sense, False), (style, False)])
    assert prec == {"chosen": 1, "beneficial": 1, "precision": 1.0, "harmful_transfers": 0, "proposals": 5, "harmful_rate": 0.0}


def test_multilingual_preflight_sov_is_not_forced_into_english_order():
    lx = _sov_lexicon()
    en = list(C.seed_constructions())
    utt = T.sov_utterance("robot", "door", "opened")               # "robot door opened" (S O V)
    gold = M.MeaningGraph((M.MNode("x1", "entity", "robot"), M.MNode("e", "event", "open"), M.MNode("x2", "entity", "door")), (M.MEdge("ROLE:agent", ("e",), ("x1",)), M.MEdge("ROLE:patient", ("e",), ("x2",)), M.MEdge("TENSE", ("e",), ("e",), "past")), root="e")
    r_en = I.interpret(utt, lx, [c for c in en if c.language == "en"])
    assert r_en.verdict is I.Verdict.UNKNOWN_CONSTRUCTION                # detected, not forced
    # the hostile: relabel the English transitive as SOV — it either fails to parse or swaps roles
    forced = T.mutant_transfer_word_order(next(c for c in en if c.construction_id == "en:transitive"), "sov")
    r_forced = I.interpret(utt, lx, [next(c for c in en if c.construction_id == "en:np"), forced])
    assert r_forced.verdict is not I.Verdict.INTERPRETED or not M.isomorphic(r_forced.meaning, gold)
    # learn the SOV order from demonstrations over the same {S, V, O} class; the meaning structure transfers intact
    def template(b):
        s, v, o = b["S"], b["V"], b["O"]
        return M.MeaningGraph((M.MNode("x1", "entity", s.lemma), M.MNode("e", "event", v.lemma), M.MNode("x2", "entity", o.lemma)), (M.MEdge("ROLE:agent", ("e",), ("x1",)), M.MEdge("ROLE:patient", ("e",), ("x2",)), M.MEdge("TENSE", ("e",), ("e",), "past")), root="e")
    hyps = AQ.order_hypotheses([("S", C.Slot("S", L.Category.NOUN)), ("V", C.Slot("V", L.Category.VERB, requires=("tense",))), ("O", C.Slot("O", L.Category.NOUN))])
    fam = AQ.ConstructionFamily("transitive", hyps, template, query_family=("cat key saw", "box door pushed"), language="sov")
    demos = [AQ.Demonstration("robot door opened", gold, "ev:sov1"), AQ.Demonstration("cat key saw", M.MeaningGraph((M.MNode("x1", "entity", "cat"), M.MNode("e", "event", "see"), M.MNode("x2", "entity", "key")), (M.MEdge("ROLE:agent", ("e",), ("x1",)), M.MEdge("ROLE:patient", ("e",), ("x2",)), M.MEdge("TENSE", ("e",), ("e",), "past")), root="e"), "ev:sov2")]
    p = AQ.acquire(fam, lx, demos)
    assert p.status.value == "PASS" and p.payload["hypothesis"] == "SOV"
    sov = AQ.construction_from_proposal(fam, p)
    assert sov.language == "sov"
    r = I.interpret("box key pushed", lx, [sov])
    assert r.verdict is I.Verdict.INTERPRETED and r.meaning.node("x1").label == "box" and r.meaning.node("x2").label == "key"
    # the English inventory is untouched by the SOV lesson (language scope)
    assert I.interpret("robot door opened", lx, [c for c in en if c.language == "en"]).verdict is I.Verdict.UNKNOWN_CONSTRUCTION


def test_retention_vector_after_a_lexical_update():
    from ocm.learning.language import lexical as LX
    from tests.m3.test_interpretation import _lexicon
    lx = _lexicon()
    cons = C.seed_constructions()
    probes = {"the robot opened the door": tr("robot", "open", "door"), "the robot opened the crate": tr("robot", "open", "crate"), "the door was opened by the robot": tr("robot", "open", "door")}
    before = T.evaluate(lx, cons, probes.items())
    LX.learn_word(lx, "the robot opened the crate", tr("robot", "open", "crate"), "ev:demo1")
    after = T.evaluate(lx, cons, probes.items())
    v = T.retention(before, after, new_set=["the robot opened the crate"], old_set=["the robot opened the door"], unrelated_set=["the door was opened by the robot"], reopened=0, work=1)
    assert (v.new_gain, v.old_loss, v.unrelated_change) == (1, 0, 0) and v.denominators == {"new": 1, "old": 1, "unrelated": 1}

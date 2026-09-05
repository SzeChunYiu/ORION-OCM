"""M3 §8–§13: frozen synthetic corpus, custody receipt, learn on dev, evaluate on protected +
held-out lexemes + paraphrase equivalence — separate numbers, never one aggregate."""
from __future__ import annotations

from ocm.language import acquisition as AQ
from ocm.language import constructions as C
from ocm.language import interpret as I
from ocm.language import lexicon as L
from ocm.language import meaning as M
from ocm.language import microworld as W
from ocm.kso.warrant import WarrantProfile as WP


def _lexicon_for(examples):
    """A lexicon covering every word in the corpus (lexical acquisition is M3 §3; here the
    vocabulary is given so that construction learning is what is measured)."""
    lx = L.Lexicon()
    ev = lambda n: WP.of({f"ev:lex:{n}"})  # noqa: E731
    lx.add(L.Lexeme("the", L.Category.DET, ()))
    lx.add(L.Lexeme("do", L.Category.AUX, ()))
    lx.add(L.Lexeme("be", L.Category.AUX, ()))
    lx.add(L.Lexeme("not", L.Category.NEG, ()))
    lx.add(L.Lexeme("by", L.Category.PREP, ()))
    for n in W.NOUNS:
        lx.add(L.Lexeme(n, L.Category.NOUN, (L.Sense(n, n, "entity", ev(n)),)))
    for a in W.ADJS:
        lx.add(L.Lexeme(a, L.Category.ADJ, (L.Sense(a, a, "property", ev(a)),)))
    for v, past in W.VERBS_PAST.items():
        lx.add(L.Lexeme(v, L.Category.VERB, (L.Sense(v, v, "event", ev(v)),)))
        if past != v + "ed":
            lx.add_rule(L.MorphRule(f"past-{v}", L.RuleKind.EXCEPTION, L.Category.VERB, (("tense", "past"),), lambda l, p=past: p, lambda s, p=past, v=v: v if s == p else None, ev(f"past-{v}"), lemmas=frozenset({v})))
            lx.add_rule(L.MorphRule(f"pp-{v}", L.RuleKind.EXCEPTION, L.Category.VERB, (("participle", "past"),), lambda l, p=past: p, lambda s, p=past, v=v: v if s == p else None, ev(f"pp-{v}"), lemmas=frozenset({v})))
    lx.add_rule(L.MorphRule("past-ed", L.RuleKind.PRODUCTIVE, L.Category.VERB, (("tense", "past"),), lambda l: l + "ed", lambda s: s[:-2] if s.endswith("ed") else None, ev("rule-ed")))
    lx.add_rule(L.MorphRule("pp-ed", L.RuleKind.PRODUCTIVE, L.Category.VERB, (("participle", "past"),), lambda l: l + "ed", lambda s: s[:-2] if s.endswith("ed") else None, ev("rule-pp")))
    lx.add_rule(L.MorphRule("aux-did", L.RuleKind.EXCEPTION, L.Category.AUX, (("tense", "past"),), lambda l: "did", lambda s: "do" if s == "did" else None, ev("did"), lemmas=frozenset({"do"})))
    lx.add_rule(L.MorphRule("aux-was", L.RuleKind.EXCEPTION, L.Category.AUX, (("tense", "past"),), lambda l: "was", lambda s: "be" if s == "was" else None, ev("was"), lemmas=frozenset({"be"})))
    return lx


def test_corpus_is_deterministic_and_protected_split_is_frozen_before_tuning():
    a, b = W.generate(), W.generate()
    assert [e.example_id for e in a] == [e.example_id for e in b]
    rec = W.custody_receipt(a, "OCM-M3-MICROWORLD-20260905")
    assert rec["dev"] + rec["protected"] == rec["n"] == 240 and rec["held_out_lexemes_absent_from_dev"]
    assert 0.25 < rec["protected"] / rec["n"] < 0.6


def test_learned_transitive_construction_generalises_to_protected_and_held_out_lexemes():
    ex = W.generate()
    lx = _lexicon_for(ex)
    dev = [e for e in ex if e.split == "dev" and e.family == "transitive"]
    prot = [e for e in ex if e.split == "protected" and e.family == "transitive"]

    seed = {c.construction_id: c for c in C.seed_constructions()}
    template = seed["en:transitive"].template
    N, V = L.Category.NOUN, L.Category.VERB
    # the six orders of {NP, V, NP}; noun phrases are their own recursive construction (helper)
    hyps = AQ.order_hypotheses([("S", C.Slot("subj", N, phrase="NP")), ("V", C.Slot("verb", V, requires=("tense",))), ("O", C.Slot("obj", N, phrase="NP"))])
    fam = AQ.ConstructionFamily("transitive", hyps, template, query_family=tuple(e.utterance for e in dev[:5]), helpers=(seed["en:np"],))
    demos = [AQ.Demonstration(e.utterance, e.meaning, f"ev:demo:{e.example_id}") for e in dev[:6]]
    p = AQ.acquire(fam, lx, demos)
    assert p.status.value == "PASS", p.detail
    c = AQ.construction_from_proposal(fam, p)
    inv = [seed["en:np"], c]
    exact_prot = sum(1 for e in prot if (r := I.interpret(e.utterance, lx, inv)).verdict is I.Verdict.INTERPRETED and M.isomorphic(r.meaning, e.meaning))
    held = [e for e in prot if e.held_out]
    exact_held = sum(1 for e in held if (r := I.interpret(e.utterance, lx, inv)).verdict is I.Verdict.INTERPRETED and M.isomorphic(r.meaning, e.meaning))
    assert exact_prot == len(prot) and exact_held == len(held) and len(held) > 0
    # lessons required: six demonstrations pinned the hypothesis; warrant is exactly those lessons
    assert len(p.warrant.evidence) <= 6


def test_paraphrase_pairs_share_the_meaning_graph_and_passive_is_interpreted_by_the_seed_inventory():
    ex = W.generate()
    lx = _lexicon_for(ex)
    pairs = W.paraphrase_pairs(ex)
    assert pairs
    cons = C.seed_constructions()
    ok = 0
    for a, p in pairs[:10]:
        ra, rp = I.interpret(a.utterance, lx, cons), I.interpret(p.utterance, lx, cons)
        if ra.verdict is I.Verdict.INTERPRETED and rp.verdict is I.Verdict.INTERPRETED and M.isomorphic(ra.meaning, rp.meaning):
            ok += 1
    assert ok == min(10, len(pairs))

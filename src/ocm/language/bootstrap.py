"""Runtime seed vocabulary, copied from the registered M3 fixtures without semantic changes.

The historical fixture files remain unchanged. This module owns the executable
bootstrap so installed runtimes do not depend on a checkout's test suite. See
``ocm.data/RESOURCE_CUSTODY_V1.json`` for source hashes and scope.
"""
from __future__ import annotations

from ocm.kso.warrant import WarrantProfile as WP
from ocm.language import lexicon as L
from ocm.language import microworld as W


def microworld_lexicon() -> L.Lexicon:
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


def acquisition_lexicon() -> L.Lexicon:
    lx = L.Lexicon()
    ev = lambda n: WP.of({f"ev:{n}"})  # noqa: E731
    for n in ("robot", "door", "cat", "box", "key"):
        lx.add(L.Lexeme(n, L.Category.NOUN, (L.Sense(n, n, "entity", ev(n)),)))
    for v in ("open", "push", "see"):
        lx.add(L.Lexeme(v, L.Category.VERB, (L.Sense(v, v, "event", ev(v)),)))
    lx.add_rule(L.MorphRule("past-ed", L.RuleKind.PRODUCTIVE, L.Category.VERB, (("tense", "past"),), lambda l: l + "ed", lambda s: s[:-2] if s.endswith("ed") else None, ev("rule-ed")))
    lx.add_rule(L.MorphRule("saw", L.RuleKind.EXCEPTION, L.Category.VERB, (("tense", "past"),), lambda l: "saw", lambda s: "see" if s == "saw" else None, ev("saw"), lemmas=frozenset({"see"})))
    return lx

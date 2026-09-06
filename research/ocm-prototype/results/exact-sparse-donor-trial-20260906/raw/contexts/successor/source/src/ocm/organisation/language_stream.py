"""The language lifetime stream as a KnowledgeSpace (M8 §11): the Alpha lexicon, constructions,
morphology rules and bounded-world facts become atoms; edges record real dependencies (a
construction depends on the categories it consumes, a fact on the lexemes that name its labels, a
morphology rule on its category's lexemes).  Declared labels: grammar / lexicon / knowledge /
discourse — a hand hierarchy to compare against communities and fibres.  Tasks: cross-construction
retrieval (from a lexeme reach the constructions that use its category), fact retrieval from a
lexeme, and revocation locality probes.
"""
from __future__ import annotations

import json
from pathlib import Path

from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace
from ocm.kso.types import Scope
from ocm.kso.warrant import WarrantProfile

from ocm.chat.session import DEFAULT_MANIFEST, _load_lexicon_and_constructions


def language_space() -> tuple[KnowledgeSpace, tuple[tuple[str, str], ...], dict[str, str]]:
    lx, cons = _load_lexicon_and_constructions(Path("."))
    atoms: list[Atom] = []
    edges: list[Hyperedge] = []
    labels: dict[str, str] = {}
    k = 0
    # lexemes (scope = language), one atom each; evidence = the union of sense evidence
    lex_by_cat: dict[str, list[str]] = {}
    for key, lexeme in lx.lexemes.items():
        aid = f"lex:{key}"
        ev = {e for s in lexeme.senses for e in s.warrant.evidence} or {f"ev:lex:{lexeme.lemma}"}
        atoms.append(Atom(aid, "claim", WarrantProfile.of(ev), scope=Scope.of("en")))
        labels[aid] = "lexicon"
        lex_by_cat.setdefault(lexeme.category.value, []).append(aid)
    # constructions depend on the categories they consume (one hyperedge per construction from a
    # representative lexeme of each category)
    for c in cons:
        aid = f"cons:{c.construction_id}"
        atoms.append(Atom(aid, "procedure", c.warrant, scope=Scope.of("en")))
        labels[aid] = "grammar"
        cats = sorted({s.category.value for s in c.pattern})
        # retrieval stream: each consumed category's representative lexeme *supports* the construction
        # (one edge per tail, so reach is associative; conjunctive dependence is the warrant's job)
        for cat in cats:
            if cat in lex_by_cat:
                edges.append(Hyperedge(f"e{k}", (lex_by_cat[cat][0],), (aid,), "SUPPORT"))
                k += 1
    # morphology rules depend on their category
    for r in lx.rules:
        aid = f"rule:{r.rule_id}"
        atoms.append(Atom(aid, "procedure", r.warrant, scope=Scope.of("en")))
        labels[aid] = "grammar"
        if r.category.value in lex_by_cat:
            edges.append(Hyperedge(f"e{k}", (lex_by_cat[r.category.value][0],), (aid,), "DEPENDENCE"))
            k += 1
    # facts depend on the lexemes naming their labels
    man = json.loads(DEFAULT_MANIFEST.read_text(encoding="utf-8"))
    lex_ids = {key.split("|")[0]: f"lex:{key}" for key in lx.lexemes}
    for f in man["facts"]:
        aid = f"fact:{f['fact_id']}"
        atoms.append(Atom(aid, "claim", WarrantProfile.of({f"ev:fact:{f['fact_id']}"}), scope=Scope.of(f["topic"])))
        labels[aid] = "knowledge"
        for x in (f["subject"], f["object"]):
            if x in lex_ids:
                edges.append(Hyperedge(f"e{k}", (lex_ids[x],), (aid,), "SUPPORT"))
                k += 1
    ks = KnowledgeSpace(tuple(atoms), tuple(edges))
    # tasks: lexeme → construction using its category; lexeme → fact naming it
    tasks: list[tuple[str, str]] = []
    for c in cons[:6]:
        cats = sorted({s.category.value for s in c.pattern})
        if cats and cats[0] in lex_by_cat:
            tasks.append((lex_by_cat[cats[0]][0], f"cons:{c.construction_id}"))
    for f in man["facts"][:12]:
        if f["subject"] in lex_ids:
            tasks.append((lex_ids[f["subject"]], f"fact:{f['fact_id']}"))
    return ks, tuple(tasks), labels

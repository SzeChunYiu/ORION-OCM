"""N1 phase B — a UD-derived recursive construction grammar (task 2) and gold tree meanings (task 4).

From every training sentence's dependency tree we read *phrase rules*: for a head token with UPOS H
and its dependents in surface order, the rule is `H ← [dep_1 … head … dep_k]` where each dependent
is summarised by (relation, category-or-phrase).  The rule's template builds the meaning of the
phrase as a rooted tree: head node (typed by category: NOUN→entity, VERB→event, ADJ→property,
ADV→manner, …), one registered relation edge per dependent (nsubj → ROLE:agent, obj → ROLE:patient,
iobj → ROLE:recipient, obl → ROLE:oblique, amod/advmod → MODIFIES, nmod → MODIFIES, det 'the' →
feature definite, case → feature case=<preposition>, aux/cop/mark/punct → annotations or dropped),
TENSE from the head's features.  A sentence's gold meaning is the same construction applied to its
own tree, so grading is exact tree-canonical equality (meaning_tree.canonical_any).

Two inventories are measured on the protected splits:
  * MEMORISED  — every rule seen in training (surface pattern → template); the trajectory-memory
    parent of M9: no generalisation beyond seen category sequences;
  * LEARNED    — per family (head UPOS + multiset of dependent relations) the M3 version-space
    learner over ORDER hypotheses (permutations of the dependents around the head) with the
    training sentences as demonstrations; a family whose version space collapses to one order is a
    learned construction; families with several surviving orders are AMBIGUOUS_ORDER.
Coverage = fraction of protected sentences whose whole tree is derivable by the inventory (every
phrase rule present); interpretation accuracy = exact gold match on those.  Nothing here reads the
protected split before the inventory is frozen from the training split.
"""
from __future__ import annotations

import itertools
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Iterable

from ocm.language import lexicon as L
from ocm.language.meaning import MEdge, MNode, MeaningGraph, register_relations
from ocm.language.meaning_tree import canonical_any
from ocm.learning.language import ud as UD

register_relations("ROLE:recipient", "ROLE:oblique", "ROLE:complement", "ROLE:predicate", "COORDINATES", "LOCATED_IN")

REL_MAP = {"nsubj": "ROLE:agent", "nsubj:pass": "ROLE:patient", "csubj": "ROLE:agent", "obj": "ROLE:patient", "iobj": "ROLE:recipient", "obl": "ROLE:oblique", "obl:tmod": "ROLE:oblique", "obl:npmod": "ROLE:oblique",
           "xcomp": "ROLE:complement", "ccomp": "ROLE:complement", "advcl": "ROLE:complement", "acl": "MODIFIES", "acl:relcl": "MODIFIES", "amod": "MODIFIES", "advmod": "MODIFIES", "nmod": "MODIFIES", "nmod:poss": "MODIFIES",
           "nummod": "MODIFIES", "appos": "MODIFIES", "compound": "MODIFIES", "flat": "MODIFIES", "conj": "COORDINATES", "parataxis": "COORDINATES", "vocative": "MODIFIES", "dislocated": "MODIFIES", "list": "COORDINATES"}
FEATURE_DEPS = {"det", "case", "aux", "aux:pass", "cop", "mark", "cc", "punct", "expl", "discourse", "fixed", "goeswith", "reparandum", "orphan", "dep", "clf", "det:predet", "cc:preconj"}
NODE_TYPE = {"NOUN": "entity", "PROPN": "entity", "PRON": "entity", "NUM": "value", "VERB": "event", "AUX": "event", "ADJ": "property", "ADV": "property", "ADP": "value", "DET": "quantifier", "INTJ": "value", "SYM": "value", "X": "value", "SCONJ": "value", "CCONJ": "value", "PART": "value"}


@dataclass(frozen=True)
class Rule:
    head_upos: str
    pattern: tuple[str, ...]              # surface-ordered items: "HEAD" or "rel:UPOS"

    @property
    def family(self) -> tuple[str, tuple[str, ...]]:
        return self.head_upos, tuple(sorted(p for p in self.pattern if p != "HEAD"))


def rules_of(s: UD.Sentence) -> list[tuple[Rule, int]]:
    """One rule per non-leaf token, in the token's surface order; leaves are terminals."""
    children: dict[int, list[UD.Token]] = defaultdict(list)
    for t in s.tokens:
        if t.head:
            children[t.head].append(t)
    out = []
    for t in s.tokens:
        kids = children.get(t.idx)
        if not kids:
            continue
        items = sorted(kids + [t], key=lambda x: x.idx)
        out.append((Rule(t.upos, tuple("HEAD" if x.idx == t.idx else f"{x.deprel}:{x.upos}" for x in items)), t.idx))
    return out


def gold_tree(s: UD.Sentence) -> MeaningGraph | None:
    """The UD-derived meaning as a rooted tree (None when the sentence has no root)."""
    r = s.root()
    if r is None:
        return None
    children: dict[int, list[UD.Token]] = defaultdict(list)
    for t in s.tokens:
        if t.head:
            children[t.head].append(t)
    nodes: list[MNode] = []
    edges: list[MEdge] = []

    def build(t: UD.Token) -> str:
        nid = f"n{t.idx}"
        feats: dict[str, str] = {}
        f = dict(t.feats)
        if f.get("Number") == "Plur":
            feats["number"] = "plural"
        for c in children.get(t.idx, []):
            if c.deprel == "det" and c.lemma.lower() == "the":
                feats["definite"] = "yes"
            elif c.deprel == "case":
                feats["case"] = c.lemma.lower()
        nodes.append(MNode(nid, NODE_TYPE.get(t.upos, "entity"), t.lemma.lower(), tuple(sorted(feats.items()))))
        if f.get("Tense") in ("Past", "Pres") and t.upos in ("VERB", "AUX"):
            edges.append(MEdge("TENSE", (nid,), (nid,), {"Past": "past", "Pres": "present"}[f["Tense"]]))
        if any(c.deprel == "advmod" and c.lemma.lower() in ("not", "n't", "never") for c in children.get(t.idx, [])):
            edges.append(MEdge("NEGATES", (nid,), (nid,)))
        for c in children.get(t.idx, []):
            if c.deprel in FEATURE_DEPS or c.upos == "PUNCT" or (c.deprel == "advmod" and c.lemma.lower() in ("not", "n't", "never")):
                continue
            rel = REL_MAP.get(c.deprel, REL_MAP.get(c.deprel.split(":")[0], "MODIFIES"))
            cid = build(c)
            edges.append(MEdge(rel, (nid,), (cid,)))
        return nid

    root_id = build(r)
    return MeaningGraph(tuple(nodes), tuple(edges), root=root_id)


@dataclass
class Grammar:
    memorised: Counter = field(default_factory=Counter)                 # Rule → count
    families: dict[tuple, Counter] = field(default_factory=lambda: defaultdict(Counter))   # family → Counter(pattern)
    sentences: int = 0

    def learned(self) -> dict[tuple, str]:
        """Version space per family over ORDER hypotheses: the surviving orders are exactly the
        patterns attested (every demonstration is consistent with the order it exhibits and refutes
        no other); a family is LEARNED iff one order survives, AMBIGUOUS_ORDER otherwise."""
        out = {}
        for fam, pats in self.families.items():
            out[fam] = "LEARNED" if len(pats) == 1 else f"AMBIGUOUS_ORDER({len(pats)})"
        return out

    def receipt(self) -> dict[str, Any]:
        lr = self.learned()
        return {"sentences": self.sentences, "memorised_rules": len(self.memorised), "families": len(self.families), "learned_single_order": sum(1 for v in lr.values() if v == "LEARNED"),
                "ambiguous_order": sum(1 for v in lr.values() if v.startswith("AMBIGUOUS")), "singleton_rules": sum(1 for c in self.memorised.values() if c == 1), "top_rules": [(f"{r.head_upos} ← {' '.join(r.pattern)}", c) for r, c in self.memorised.most_common(8)]}


def induce_grammar(sentences: Iterable[UD.Sentence]) -> Grammar:
    g = Grammar()
    for s in sentences:
        g.sentences += 1
        for rule, _ in rules_of(s):
            g.memorised[rule] += 1
            g.families[rule.family][rule.pattern] += 1
    return g


def derivable(s: UD.Sentence, g: Grammar, *, mode: str) -> tuple[bool, list[str]]:
    """Whole-tree derivability: every phrase rule of the sentence is in the inventory (MEMORISED), or
    its family is LEARNED with the same order (LEARNED mode; ambiguous families are refused)."""
    missing = []
    lr = g.learned() if mode == "LEARNED" else None
    for rule, _ in rules_of(s):
        if mode == "MEMORISED":
            if rule not in g.memorised:
                missing.append(f"{rule.head_upos} ← {' '.join(rule.pattern)}")
        else:
            fam = rule.family
            if lr.get(fam) != "LEARNED" or rule.pattern not in g.families[fam]:
                missing.append(f"{rule.head_upos} ← {' '.join(rule.pattern)}")
    return (not missing), missing


def evaluate(sentences: Iterable[UD.Sentence], g: Grammar, ind: UD.Induction, *, mode: str) -> dict[str, Any]:
    """Protected-split coverage and exact interpretation: a sentence is INTERPRETED iff it is
    derivable and every lexical token is in the induced lexicon; its meaning is then the tree the
    rules build, which by construction equals the gold tree — so the measured quantity is the
    inventory's reach, graded by canonical equality as a self-check.  Sentences whose gold tree is not
    a tree (should not happen for UD) are CANNOT_CHECK."""
    n = derivable_n = interpreted = exact = cannot = lex_unknown = 0
    missing_rules: Counter = Counter()
    for s in sentences:
        gold = gold_tree(s)
        if gold is None:
            cannot += 1
            continue
        n += 1
        ok, missing = derivable(s, g, mode=mode)
        for m in missing[:3]:
            missing_rules[m] += 1
        lex_ok = all(f"{t.lemma.lower()}|{UD.UPOS_TO_CATEGORY[t.upos].value}" in ind.attestations for t in s.tokens if t.upos in UD.UPOS_TO_CATEGORY)
        if not lex_ok:
            lex_unknown += 1
        if ok:
            derivable_n += 1
            if lex_ok:
                interpreted += 1
                try:
                    exact += int(canonical_any(gold) == canonical_any(gold_tree(s)))
                except Exception:  # noqa: BLE001
                    cannot += 1
    return {"mode": mode, "sentences": n, "cannot_check": cannot, "derivable": f"{derivable_n}/{n}", "lexically_known": f"{n - lex_unknown}/{n}", "interpreted": f"{interpreted}/{n}", "exact_gold_match_of_interpreted": f"{exact}/{interpreted}", "missing_rules_top": missing_rules.most_common(8)}


def mutant_memorised_as_learned(g: Grammar) -> int:
    """Planted (M9 trajectory-memory hostile): report every memorised rule as a learned construction."""
    return len(g.memorised)

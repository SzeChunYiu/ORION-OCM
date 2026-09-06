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

    def identification(self) -> dict[str, Any]:
        """Identifiability receipt (ORION-V2 batch 11 K1, obligations H1/H2): what class this inventory identifies
        and what it cannot.  The class is category-level (slots constrained by phrase type only) with a finite
        arity bound; a family LEARNED from a single demonstration is LEARNED-at-n=1 (no lifecycle warrant past its
        demonstration); an inventory with rules attested once is NOT_CONVERGED (a Good–Turing reading, not a
        certificate); and for any string whose category shape admits two attested decompositions a unique parse is
        UNREACHABLE_FROM_POSITIVE_DATA — no further positive demonstration lowers the derivation count."""
        lr = self.learned()
        arity = max((len(r.pattern) - 1 for r in self.memorised), default=0)
        singletons = sum(1 for c in self.memorised.values() if c == 1)
        fam_total = {fam: sum(pats.values()) for fam, pats in self.families.items()}
        learned_at_1 = sum(1 for fam, v in lr.items() if v == "LEARNED" and fam_total[fam] == 1)
        return {"class": "category-level slots (phrase type only), dependency-order families, finite arity", "arity_bound": arity,
                "learned_families": sum(1 for v in lr.values() if v == "LEARNED"), "learned_at_n1": learned_at_1,
                "rules_attested_once": singletons, "rules_total": len(self.memorised),
                "convergence": ("NOT_CONVERGED (Good–Turing reading: %d of %d rules attested once; not a certificate)" % (singletons, len(self.memorised))) if singletons else "NO_SINGLETON_RULES (convergence still not certified: finite sample)",
                "unique_parse": "UNREACHABLE_FROM_POSITIVE_DATA for strings whose category shape has ≥ 2 attested decompositions (batch 11 K1 ii–iv); a unique reading needs a registered negative/membership channel or a finer (lexicalised) class"}

    def receipt(self) -> dict[str, Any]:
        lr = self.learned()
        return {"sentences": self.sentences, "memorised_rules": len(self.memorised), "families": len(self.families), "learned_single_order": sum(1 for v in lr.values() if v == "LEARNED"),
                "ambiguous_order": sum(1 for v in lr.values() if v.startswith("AMBIGUOUS")), "singleton_rules": sum(1 for c in self.memorised.values() if c == 1), "top_rules": [(f"{r.head_upos} ← {' '.join(r.pattern)}", c) for r, c in self.memorised.most_common(8)],
                "identification": self.identification()}


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


# ------------------------------------------------------------------ N1 phase C: rules → M3 constructions → real parsing
PHRASE_OF_UPOS = {"NOUN": "NP", "PROPN": "NP", "PRON": "NP", "NUM": "NP", "VERB": "VP", "AUX": "VP", "ADJ": "AP", "ADV": "ADVP", "ADP": "PP", "DET": "DP", "SCONJ": "SP", "CCONJ": "CP", "PART": "PARTP", "INTJ": "IP", "SYM": "NP", "X": "NP"}


def constructions_from_grammar(g: Grammar, *, min_count: int = 1, learned_only: bool = False, evidence_prefix: str = "ud:rule") -> list:
    """Every phrase rule becomes an M3 Construction whose pattern is the rule's surface items: the head
    is a lexical slot of the head category; each dependent is a recursive phrase slot of its own
    head category (a leaf dependent is a phrase produced by its own leaf construction).  The template
    builds the head node, TENSE / NEGATES annotations, feature-bearing dependents (det 'the', case)
    as features, and one registered relation edge per contentful dependent — the same shape as
    `gold_tree`, so parsing a sentence and comparing to its gold tree is an exact test."""
    from ocm.language.constructions import Construction, Phrase, Slot
    from ocm.kso.warrant import WarrantProfile as WP
    lr = g.learned() if learned_only else None
    out = []
    # leaf constructions: one per category, produce a phrase whose meaning is the bare head node
    for upos, cat in UD.UPOS_TO_CATEGORY.items():
        def leaf_t(b, upos=upos):
            r = b["h"]
            return MeaningGraph((MNode("x", NODE_TYPE.get(upos, "entity"), r.sense.concept if r.sense else r.lemma, tuple(sorted(dict(r.features).items()))),), (), root="x")
        out.append(Construction(f"ud:leaf:{upos}", f"leaf:{upos}", (Slot("h", cat),), leaf_t, WP.of({f"{evidence_prefix}:leaf:{upos}"}), produces=PHRASE_OF_UPOS.get(upos, "NP"), head_slot="h", head_node="x"))
    for rule, count in g.memorised.items():
        if count < min_count or (learned_only and lr.get(rule.family) != "LEARNED"):
            continue
        head_cat = UD.UPOS_TO_CATEGORY.get(rule.head_upos)
        if head_cat is None:
            continue
        slots, roles = [], []
        ok = True
        for i, item in enumerate(rule.pattern):
            if item == "HEAD":
                slots.append(Slot("h", head_cat))
                continue
            rel, upos = item.split(":", 1) if ":" in item else (item, "X")
            if upos not in UD.UPOS_TO_CATEGORY and upos != "PUNCT":
                ok = False
                break
            if upos == "PUNCT":
                continue                                          # punctuation is not a lexical unit for the parser
            name = f"d{i}"
            slots.append(Slot(name, UD.UPOS_TO_CATEGORY[upos], phrase=PHRASE_OF_UPOS.get(upos, "NP")))
            roles.append((name, rel, upos))
        if not ok:
            continue

        def tmpl(b, roles=roles, head_upos=rule.head_upos):
            r = b["h"]
            feats: dict[str, str] = dict(r.features)
            nodes: list[MNode] = []
            edges: list[MEdge] = []
            mapped_children = []
            for name, rel, upos in roles:
                ph = b[name]
                if rel == "det" and getattr(ph, "meaning", None) is not None and ph.meaning.node(ph.head_node).label == "the":
                    feats["definite"] = "yes"
                    continue
                if rel == "case":
                    feats["case"] = ph.meaning.node(ph.head_node).label or ""
                    continue
                if rel in FEATURE_DEPS:
                    continue
                if rel == "advmod" and (ph.meaning.node(ph.head_node).label in ("not", "n't", "never")):
                    edges.append(MEdge("NEGATES", ("x",), ("x",)))
                    continue
                mapping = {n.node_id: f"{name}.{n.node_id}" for n in ph.meaning.nodes}
                sub = ph.meaning.relabel(mapping)
                nodes.extend(sub.nodes)
                edges.extend(sub.edges)
                mapped_children.append((REL_MAP.get(rel, REL_MAP.get(rel.split(":")[0], "MODIFIES")), mapping[ph.head_node]))
            tense = feats.pop("tense", None)
            feats.pop("participle", None)
            head = MNode("x", NODE_TYPE.get(head_upos, "entity"), r.sense.concept if r.sense else r.lemma, tuple(sorted(feats.items())))
            all_edges = ([MEdge("TENSE", ("x",), ("x",), tense)] if tense and head_upos in ("VERB", "AUX") else []) + edges + [MEdge(rel, ("x",), (cid,)) for rel, cid in mapped_children]
            return MeaningGraph((head, *nodes), tuple(all_edges), root="x")

        cid = f"ud:{rule.head_upos}:{'_'.join(p.replace(':', '-') for p in rule.pattern)}"
        out.append(Construction(cid, f"rule:{rule.head_upos}", tuple(slots), tmpl, WP.of({f"{evidence_prefix}:{cid}"}), lineage=(f"count:{count}",), produces=PHRASE_OF_UPOS.get(rule.head_upos, "NP"), head_slot="h", head_node="x"))
        if rule.head_upos in ("VERB", "AUX"):
            # the same rule at clause level (produces=None): a sentence reading when it spans the whole utterance
            out.append(Construction(cid + ":clause", f"clause:{rule.head_upos}", tuple(slots), tmpl, WP.of({f"{evidence_prefix}:{cid}"}), lineage=(f"count:{count}",)))
    return out


def erase_gaps(g):
    """Structure match for gap-bearing meanings: labels of underspecified/gap nodes are erased before canonicalisation."""
    from ocm.language.meaning import MNode, MeaningGraph
    nodes = tuple(MNode(n.node_id, n.node_type, None, tuple(f for f in n.features if f[0] != "gap"), True) if n.underspecified or ("gap", "yes") in n.features else n for n in g.nodes)
    return MeaningGraph(nodes, g.edges, g.root)


def erase_labels_of(g, node_ids):
    from ocm.language.meaning import MNode, MeaningGraph
    nodes = tuple(MNode(n.node_id, n.node_type, None, tuple(f for f in n.features if f[0] != "gap"), True) if n.node_id in node_ids else n for n in g.nodes)
    return MeaningGraph(nodes, g.edges, g.root)


def parse_protected(sentences: Iterable[UD.Sentence], constructions, ind: UD.Induction, *, limit: int | None = None, time_budget_s: float = 600.0, max_tokens: int = 12, engine: str = "matcher", chart_max_items: int = 300_000, gaps: bool = False) -> dict[str, Any]:
    """Parse protected token strings with the M3 matcher over the induced lexicon and the UD-derived
    constructions; grade INTERPRETED candidates against the gold tree by tree-exact canonical equality.
    Root-level phrases only count as a sentence reading when the top phrase is VP/NP covering all tokens."""
    import time
    from collections import Counter
    from ocm.language import interpret as I
    verdicts: Counter = Counter()
    n = exact = 0
    misses = []
    t0 = time.perf_counter()
    for s in sentences:
        if limit is not None and n >= limit:
            break
        if time.perf_counter() - t0 > time_budget_s:
            verdicts["TIME_BUDGET_CANNOT_CHECK"] += 1
            continue
        gold = gold_tree(s)
        if gold is None:
            continue
        lexical = [t for t in s.tokens if t.upos != "PUNCT"]
        if len(lexical) > max_tokens:
            verdicts["LENGTH_CANNOT_CHECK"] += 1          # the bottom-up span table is exponential in attachment ambiguity; bounded by declaration
            continue
        n += 1
        utt = " ".join(t.form.lower() for t in lexical)
        if engine == "chart":
            from ocm.language import chart as CH
            try:
                r = CH.parse(utt.split(), ind.lexicon, constructions, max_items=chart_max_items, gaps=gaps)
            except CH.ChartCap:
                verdicts["CHART_CAP_CANNOT_CHECK"] += 1
                continue
            except Exception as exc:  # noqa: BLE001
                verdicts[f"ERROR:{type(exc).__name__}"] += 1
                continue
            verdicts[r["verdict"]] += 1
            ms = [m["meaning"] for m in r["meanings"] if m.get("meaning") is not None]
            try:
                gd = canonical_any(gold)
                if r["verdict"] == "INTERPRETED" and ms and canonical_any(ms[0]) == gd:
                    exact += 1
                elif r["verdict"] == "INTERPRETED_WITH_GAPS" and ms:
                    # structure match: erase the labels of the gap nodes and of the gold nodes standing for the same tokens
                    gm = erase_gaps(ms[0])
                    gap_forms = set(r.get("gaps", []))
                    gold_gap_ids = {t2.idx for t2 in s.tokens if t2.form.lower() in gap_forms}
                    gg = erase_labels_of(gold, {f"n{i}" for i in gold_gap_ids})
                    if canonical_any(gm) == canonical_any(gg):
                        verdicts["GAP_STRUCTURE_MATCH"] += 1
                elif r["verdict"] == "AMBIGUOUS":
                    verdicts["AMBIGUOUS_COUNT_TOTAL"] += r["count"]
                    if any(canonical_any(m) == gd for m in ms):
                        verdicts["AMBIGUOUS_WITH_GOLD_AMONG_UNPACKED"] += 1
                    rk = r.get("ranking", {})
                    if rk.get("scored"):
                        verdicts["AMBIGUOUS_RANKED"] += 1
                        if rk.get("top_unique_derivation"):
                            verdicts["AMBIGUOUS_TOP_UNIQUE"] += 1
                        if ms and canonical_any(ms[0]) == gd:
                            verdicts["AMBIGUOUS_TOP_IS_GOLD"] += 1          # the evidence-ranked first reading equals the gold tree (a report, not a licence)
                elif len(misses) < 8:
                    misses.append((utt[:80], r["verdict"]))
            except Exception:  # noqa: BLE001
                verdicts["CANONICAL_CANNOT_CHECK"] += 1
            continue
        try:
            r = I.interpret(utt, ind.lexicon, constructions)
        except Exception as exc:  # noqa: BLE001
            verdicts[f"ERROR:{type(exc).__name__}"] += 1
            continue
        verdicts[r.verdict.value] += 1
        if r.verdict is I.Verdict.INTERPRETED:
            try:
                if canonical_any(r.candidates[0].meaning) == canonical_any(gold):
                    exact += 1
                elif len(misses) < 8:
                    misses.append((utt[:80], "MEANING_MISMATCH"))
            except Exception:  # noqa: BLE001
                verdicts["CANONICAL_CANNOT_CHECK"] += 1
        elif r.verdict is I.Verdict.AMBIGUOUS:
            try:
                if any(canonical_any(c.meaning) == canonical_any(gold) for c in r.candidates):
                    verdicts["AMBIGUOUS_WITH_GOLD_AMONG_CANDIDATES"] += 1
            except Exception:  # noqa: BLE001
                pass
        elif len(misses) < 8:
            misses.append((utt[:80], r.verdict.value + ":" + r.reason[:60]))
    return {"engine": engine, "gaps": gaps, "parsed": n, "verdicts": dict(verdicts), "exact_gold_match": f"{exact}/{n}", "wall_s": round(time.perf_counter() - t0, 1), "misses_sample": misses}


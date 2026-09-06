"""N1 task 3 (tree canonical form) and phase B (UD-derived grammar): exactness, bound behaviour, gold trees, derivability."""
from __future__ import annotations

import pytest

from ocm.language.meaning import MAX_EXACT_CANONICAL, CannotCheck, MEdge, MNode, MeaningGraph, canonical
from ocm.language import meaning_tree as MT
from ocm.learning.language import ud as UD
from ocm.learning.language import ud_grammar as G

from .test_ud_induction import CONLLU


def _chain(n: int, label: str = "x", rel: str = "MODIFIES") -> MeaningGraph:
    nodes = [MNode(f"n{i}", "entity", f"{label}{i}") for i in range(n)]
    edges = [MEdge(rel, (f"n{i}",), (f"n{i+1}",)) for i in range(n - 1)]
    return MeaningGraph(tuple(nodes), tuple(edges), root="n0")


def test_tree_canonical_is_exact_and_relabel_invariant_and_small_graphs_unchanged():
    small = _chain(4)
    assert MT.canonical_any(small) == canonical(small)[1]                     # digests below the bound are untouched
    big = _chain(MAX_EXACT_CANONICAL + 5)
    with pytest.raises(CannotCheck):
        canonical(big)                                                        # the bounded form still refuses
    d = MT.canonical_any(big)
    assert d.startswith("tree:")
    relabelled = big.relabel({f"n{i}": f"m{(i * 7) % 13}" for i in range(MAX_EXACT_CANONICAL + 5)})
    assert MT.canonical_any(relabelled) == d                                   # isomorphic trees agree
    # reordering children at the root does not change the digest; changing a label does
    root = MNode("r", "event", "give")
    a, b = MNode("a", "entity", "girl"), MNode("b", "entity", "book")
    kids = [MNode(f"k{i}", "property", f"p{i}") for i in range(8)]
    g1 = MeaningGraph((root, a, b, *kids), (MEdge("ROLE:agent", ("r",), ("a",)), MEdge("ROLE:patient", ("r",), ("b",)), *[MEdge("MODIFIES", ("b",), (k.node_id,)) for k in kids]), root="r")
    g2 = MeaningGraph((root, b, a, *reversed(kids)), (MEdge("ROLE:patient", ("r",), ("b",)), *[MEdge("MODIFIES", ("b",), (k.node_id,)) for k in reversed(kids)], MEdge("ROLE:agent", ("r",), ("a",))), root="r")
    assert MT.canonical_any(g1) == MT.canonical_any(g2)
    g3 = MeaningGraph((root, a, MNode("b", "entity", "cup"), *kids), g1.edges, root="r")
    assert MT.canonical_any(g3) != MT.canonical_any(g1)
    # a non-tree above the bound stays CANNOT_CHECK; the hostile hashes it anyway
    cyc_nodes = [MNode(f"c{i}", "entity", "x") for i in range(MAX_EXACT_CANONICAL + 2)]
    cyc = MeaningGraph(tuple(cyc_nodes), tuple(MEdge("COORDINATES", (f"c{i}",), (f"c{(i + 1) % len(cyc_nodes)}",)) for i in range(len(cyc_nodes))))
    assert not MT.is_tree(cyc)
    with pytest.raises(CannotCheck):
        MT.canonical_any(cyc)
    assert isinstance(MT.mutant_wl_for_trees(cyc), str)


def test_ud_grammar_gold_trees_rules_and_derivability(tmp_path):
    p = tmp_path / "t.conllu"
    p.write_text(CONLLU)
    sents = list(UD.read_conllu(p))
    gold = G.gold_tree(sents[0])
    assert gold.root == "n3" and {e.relation for e in gold.edges} == {"ROLE:agent", "ROLE:patient", "TENSE"}
    assert gold.node("n2").features == (("definite", "yes"),) and gold.node("n2").label == "girl" and MT.is_tree(gold)
    g = G.induce_grammar(sents[:2])                                            # train on s1, s2; s3 is protected
    rec = g.receipt()
    assert rec["memorised_rules"] == 2 and rec["families"] == 2 and rec["learned_single_order"] == 2   # VERB ← nsubj:NOUN HEAD obj:NOUN punct:PUNCT ; NOUN ← det:DET HEAD
    ok, missing = G.derivable(sents[2], g, mode="MEMORISED")
    assert not ok and missing == ["VERB ← nsubj:PRON HEAD punct:PUNCT"]        # the intransitive pronoun clause was never seen
    ind = UD.induce(sents[:2])
    ev = G.evaluate(sents[:2], g, ind, mode="MEMORISED")
    assert ev["derivable"] == "2/2" and ev["interpreted"] == "2/2" and ev["exact_gold_match_of_interpreted"] == "2/2"
    ev3 = G.evaluate(sents[2:], g, ind, mode="LEARNED")
    assert ev3["derivable"] == "0/1" and ev3["lexically_known"] == "0/1"
    assert G.mutant_memorised_as_learned(g) == 2                                # the hostile calls every memorised rule learned

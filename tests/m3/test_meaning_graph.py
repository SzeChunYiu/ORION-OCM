"""M3 §2 MeaningGraph.v1: required meanings representable; exact canonical form; WL is not canonical."""
from __future__ import annotations

import pytest

from ocm.kso.warrant import CannotCheck
from ocm.language import meaning as M


def test_required_example_meanings_are_representable_and_distinct():
    ex = M.example_meanings()
    assert len(ex) == 9
    digests = {k: M.canonical(g)[1] for k, g in ex.items()}
    assert len(set(digests.values())) == 9
    active, passive = ex["the robot opened the red door"], ex["the door was opened by the robot"]
    assert not M.isomorphic(active, passive)  # the red modifier differs; roles are identical
    stripped = M.MeaningGraph(tuple(n for n in active.nodes if n.node_id != "red"), tuple(e for e in active.edges if e.relation != "MODIFIES"), root="open")
    assert M.isomorphic(stripped, passive)     # passive alternation preserves the meaning graph


def test_canonical_form_is_isomorphism_invariant_and_seed_is_a_function_of_it():
    g = M.example_meanings()["john thinks mary may leave"]
    renamed = g.relabel({"john": "x1", "mary": "x2", "think": "x3", "leave": "x4"})
    assert M.isomorphic(g, renamed)
    s1 = M.seed_from_meaning(g, {"n0": "atom:john"})
    s2 = M.seed_from_meaning(renamed, {"n0": "atom:john"})
    assert s1 == s2


def test_wl_hash_collides_where_canonical_form_does_not():
    a, b = M.wl_collision_witness()
    assert M.wl1_hash(a) == M.wl1_hash(b)          # the mutant "canonical form" collides
    assert not M.isomorphic(a, b)                  # exact canonical form separates them


def test_exact_canonical_form_is_bounded_and_fails_closed():
    nodes = tuple(M.MNode(f"e{i}", "entity", "x") for i in range(M.MAX_EXACT_CANONICAL + 1))
    with pytest.raises(CannotCheck):
        M.canonical(M.MeaningGraph(nodes, ()))


def test_registry_extension_is_data_not_code():
    reg = M.meaning_registry()
    assert "meaning:event" in reg.atom_types and "ROLE:agent" in reg.relation_types
    with pytest.raises(ValueError):
        M.MNode("z", "vibe")
    with pytest.raises(ValueError):
        M.MEdge("LIKES", ("a",), ("b",))

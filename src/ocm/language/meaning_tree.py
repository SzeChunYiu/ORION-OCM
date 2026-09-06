"""Exact canonical form for tree-shaped meaning graphs (N1 task 3).

`meaning.canonical` is exact but bounded to MAX_EXACT_CANONICAL nodes because it enumerates
orderings.  Meanings derived from dependency trees are rooted trees whose edges point from a head
to a dependent (tails = (head,), heads = (dependent,)); self-loop edges (TENSE, NEGATES) are node
annotations.  For such graphs the Aho–Hopcroft–Ullman canonical string is exact and polynomial, so
the node bound is not needed.  `canonical_any` keeps the small-graph digest unchanged (receipts
depend on it) and uses the tree digest — with a distinct `tree:` prefix — only above the bound;
non-tree graphs above the bound stay CANNOT_CHECK, exactly as before.
"""
from __future__ import annotations

import hashlib
from collections import defaultdict

from ocm.language.meaning import MAX_EXACT_CANONICAL, CannotCheck, MeaningGraph, canonical


def is_tree(g: MeaningGraph) -> bool:
    """Rooted tree: a root with no parent, every other node exactly one parent, single-tail /
    single-head edges only (self-loops allowed as annotations), every node reachable from the root."""
    parents: dict[str, int] = defaultdict(int)
    children: dict[str, list[str]] = defaultdict(list)
    for e in g.edges:
        if len(e.tails) != 1 or len(e.heads) != 1:
            return False
        t, h = e.tails[0], e.heads[0]
        if t == h:
            continue
        parents[h] += 1
        children[t].append(h)
    roots = [n.node_id for n in g.nodes if parents[n.node_id] == 0]
    if len(roots) != 1 or any(parents[n.node_id] > 1 for n in g.nodes):
        return False
    if g.root is not None and g.root != roots[0]:
        return False
    seen = set()
    stack = [roots[0]]
    while stack:
        v = stack.pop()
        if v in seen:
            return False
        seen.add(v)
        stack.extend(children[v])
    return len(seen) == len(g.nodes)


def tree_encoding(g: MeaningGraph) -> str:
    """AHU encoding: each node is (colour, sorted self-annotations, sorted (relation, value, child encoding))."""
    if not is_tree(g):
        raise CannotCheck("not a rooted tree; use the bounded exact canonical form")
    node = {n.node_id: n for n in g.nodes}
    annots: dict[str, list[str]] = defaultdict(list)
    kids: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for e in g.edges:
        t, h = e.tails[0], e.heads[0]
        if t == h:
            annots[t].append(f"{e.relation}={e.value}")
        else:
            kids[t].append((e.relation, e.value or "", h))
    root = next(n.node_id for n in g.nodes if all(not (e.tails[0] != e.heads[0] and e.heads[0] == n.node_id) for e in g.edges))

    def enc(v: str) -> str:
        parts = sorted(f"{rel}|{val}|{enc(c)}" for rel, val, c in kids[v])
        return "(" + node[v].colour() + "{" + ",".join(sorted(annots[v])) + "}" + "[" + ";".join(parts) + "])"
    return enc(root)


def canonical_any(g: MeaningGraph) -> str:
    """Digest usable for exact equality on any tree-shaped meaning and on any meaning within the bound."""
    if len(g.nodes) <= MAX_EXACT_CANONICAL:
        return canonical(g)[1]
    return "tree:" + hashlib.sha256(tree_encoding(g).encode("utf-8")).hexdigest()


def mutant_wl_for_trees(g: MeaningGraph) -> str:
    """Planted (MEG-24 hostile): a non-canonical hash used as if exact."""
    from ocm.language.meaning import wl1_hash
    return wl1_hash(g)

"""Minimal walkable e-graph: hash-consing, union-find, congruence closure.

Project-specific residual for D21. `egglog` is the mature reuse arm and runs as an
independent cross-check, but it exposes only bounded `extract_multiple`, never
exhaustive e-class membership. T86 is stated as an *e-class invariant* and
`WORLDS_V1["OW6"].justify` requires every e-class member to be ground-truth
evaluated, so exhaustive membership enumeration is mandatory and is built here.

Rules are e-matchers over e-nodes (not over enumerated terms), so saturation stays
polynomial in the e-graph even when the term-level AC orbit is astronomically large.

Terms are the frozen OW6 shape: `(op, left, right)` tuples; leaves are the frozen
tokens "2"/"3"/"5"/"x" or a folded non-negative int.
"""
from __future__ import annotations
import time

class EClassCapExceeded(Exception):
    """Exhaustive e-class enumeration hit its cap or found a self-referential class.

    Reported with its own status, never silently treated as 'checked and fine'.
    """

class EGraph:
    def __init__(self) -> None:
        self.parent: list[int] = []
        self.nodes: dict[tuple, int] = {}       # canonical enode -> class id
        self.classes: dict[int, set[tuple]] = {}
        self.stats = {"enodes": 0, "merges": 0, "rebuilds": 0, "rule_applications": 0}

    # ------------------------------------------------------------ union-find
    def find(self, c: int) -> int:
        while self.parent[c] != c:
            self.parent[c] = self.parent[self.parent[c]]
            c = self.parent[c]
        return c

    def _canon(self, node: tuple) -> tuple:
        return node if node[0] == "leaf" else (node[0], self.find(node[1]), self.find(node[2]))

    def add_node(self, node: tuple) -> int:
        node = self._canon(node)
        if node in self.nodes:
            return self.find(self.nodes[node])
        c = len(self.parent)
        self.parent.append(c)
        self.classes[c] = {node}
        self.nodes[node] = c
        self.stats["enodes"] += 1
        return c

    def add_term(self, t) -> int:
        if isinstance(t, tuple):
            return self.add_node((t[0], self.add_term(t[1]), self.add_term(t[2])))
        return self.add_node(("leaf", t))

    def merge(self, a: int, b: int) -> bool:
        a, b = self.find(a), self.find(b)
        if a == b:
            return False
        if len(self.classes[a]) < len(self.classes[b]):
            a, b = b, a
        self.parent[b] = a
        self.classes[a] |= self.classes.pop(b)
        self.stats["merges"] += 1
        return True

    def rebuild(self) -> None:
        """Congruence closure to fixpoint."""
        changed = True
        while changed:
            changed = False
            self.stats["rebuilds"] += 1
            seen: dict[tuple, int] = {}
            for c in list(self.classes):
                if self.find(c) != c:
                    continue
                for n in list(self.classes[c]):
                    cn = self._canon(n)
                    if cn in seen and self.find(seen[cn]) != self.find(c):
                        if self.merge(seen[cn], c):
                            changed = True
                    seen[cn] = self.find(c)
            # re-key every class from its canonical enodes
            new: dict[int, set[tuple]] = {}
            for c, ns in self.classes.items():
                new.setdefault(self.find(c), set()).update(self._canon(n) for n in ns)
            self.classes = new
            self.nodes = {n: c for c, ns in self.classes.items() for n in ns}

    # ------------------------------------------------------------ enumeration
    def eclass_terms(self, cid: int, cap: int = 50000):
        """EXHAUSTIVE enumeration of every term in the e-class.

        Raises EClassCapExceeded on a self-referential class or on cap overflow,
        so 'could not check' is never reported as 'checked and fine'.
        """
        memo: dict[int, list] = {}

        def walk(c: int, path: frozenset):
            c = self.find(c)
            if c in path:
                raise EClassCapExceeded(f"class {c} is self-referential")
            if c in memo:
                return memo[c]
            out: list = []
            for n in sorted(self.classes[c], key=repr):
                if n[0] == "leaf":
                    out.append(n[1])
                    continue
                for l in walk(n[1], path | {c}):
                    for r in walk(n[2], path | {c}):
                        out.append((n[0], l, r))
                        if len(out) > cap:
                            raise EClassCapExceeded(f"class {c} exceeded cap {cap}")
            memo[c] = out
            return out

        return walk(self.find(cid), frozenset())

    def enodes(self):
        """Canonical (class_id, enode) pairs, stable order."""
        for c in sorted(self.classes):
            if self.find(c) != c:
                continue
            for n in sorted(self.classes[c], key=repr):
                yield c, self._canon(n)

    def leaf_value(self, cid: int):
        """The numeric leaf of a class, if it has one (else None)."""
        for n in self.classes[self.find(cid)]:
            if n[0] == "leaf":
                v = n[1]
                if isinstance(v, int):
                    return v
                if isinstance(v, str) and v.isdigit():
                    return int(v)
        return None

    # ------------------------------------------------------------- saturation
    def saturate(self, rules, cap_iters: int = 60, deadline_s: float = 300.0):
        """`rules`: name -> fn(egraph) -> iterable of (class_a, class_b) merge requests.

        Returns (iterations, saturated).
        """
        t_end = time.process_time() + deadline_s
        for it in range(1, cap_iters + 1):
            if time.process_time() > t_end:
                return it, False
            requests: list[tuple[int, int]] = []
            for name in sorted(rules):
                for a, b in rules[name](self):
                    self.stats["rule_applications"] += 1
                    requests.append((a, b))
            changed = False
            for a, b in requests:
                if self.merge(a, b):
                    changed = True
            self.rebuild()
            if not changed:
                return it, True
        return cap_iters, False

    def n_classes(self) -> int:
        return len({self.find(c) for c in self.classes})

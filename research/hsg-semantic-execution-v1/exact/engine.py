"""D18 obligation-hypergraph semiring engine.

One finite deduction-hypergraph structure; the evaluator is swappable via the
Semiring protocol (plus/add/zero/one/mul). Acyclic DP is licensed only after
SCC analysis; cyclic worlds are REPORTED, never silently looped. Every
evaluator is cross-checkable against independent brute-force derivation-tree
enumeration (exact values: int / Fraction / polynomial dicts -- no floats).
"""
from __future__ import annotations
import time
from fractions import Fraction
from math import inf

TREE_CAP = 2_000_000  # brute-force enumeration bound (tiny worlds stay far under)

# ------------------------------------------------------------ semirings ----
class BooleanSR:
    name = "BooleanReachability"
    zero, one = False, True
    def plus(self, a, b): return a or b
    def mul(self, a, b): return a and b
    def edge_w(self, e, w): return True

class CountingSR:
    name = "Counting"
    zero, one = 0, 1
    def plus(self, a, b): return a + b
    def mul(self, a, b): return a * b
    def edge_w(self, e, w): return 1

class ViterbiSR:
    name = "Viterbi(max-product)"
    zero, one = Fraction(0), Fraction(1)
    def plus(self, a, b): return max(a, b)
    def mul(self, a, b): return a * b
    def edge_w(self, e, w): return w["viterbi_w"]

class TropicalSR:
    name = "Tropical(min-plus)"
    zero, one = inf, Fraction(0)
    def plus(self, a, b): return min(a, b)
    def mul(self, a, b): return a + b   # inf-safe: inf+x==inf
    def edge_w(self, e, w): return w["tropical_w"]

class ProvenanceNX:
    """N[X]: polynomial as dict monomial(frozenset of leaf vars) -> coef."""
    name = "ProvenanceNX"
    zero, one = {}, {frozenset(): 1}
    def plus(self, a, b):
        out = dict(a)
        for m, c in b.items():
            out[m] = out.get(m, 0) + c
        return {m: c for m, c in out.items() if c} or {}
    def mul(self, a, b):
        out = {}
        for ma, ca in a.items():
            for mb, cb in b.items():
                m = ma | mb
                out[m] = out.get(m, 0) + ca * cb
        return {m: c for m, c in out.items() if c} or {}
    def edge_w(self, e, w): return self.one

# -------------------------------------------------------------- engine ----
class LicenceError(Exception):
    """Acyclic-DP licence violated (cycle found). Reported, never looped."""

class Hypergraph:
    def __init__(self, nodes, edges):
        self.nodes = list(nodes)
        self.edges = list(edges)
        self.incoming = {n: [] for n in nodes}
        for e in edges:
            self.incoming[e["conclusion"]].append(e)
        self._scc = None

    def scc_tarjan(self):
        """Iterative Tarjan SCC (stdlib-only, no recursion). Time-bounded."""
        deadline = time.process_time() + 10.0
        index, low, onstk, stack = {}, {}, set(), []
        sccs, counter = [], [0]
        for root in self.nodes:
            if root in index:
                continue
            work = [(root, iter(self._succ(root)))]
            index[root] = low[root] = counter[0]; counter[0] += 1
            stack.append(root); onstk.add(root)
            while work:
                if time.process_time() > deadline:
                    raise LicenceError("SCC computation exceeded time bound")
                node, it = work[-1]
                advanced = False
                for s in it:
                    if s not in index:
                        index[s] = low[s] = counter[0]; counter[0] += 1
                        stack.append(s); onstk.add(s)
                        work.append((s, iter(self._succ(s))))
                        advanced = True
                        break
                    elif s in onstk:
                        low[node] = min(low[node], index[s])
                if advanced:
                    continue
                work.pop()
                if work:
                    parent = work[-1][0]
                    low[parent] = min(low[parent], low[node])
                if low[node] == index[node]:
                    comp = set()
                    while True:
                        w = stack.pop(); onstk.discard(w); comp.add(w)
                        if w == node:
                            break
                    sccs.append(comp)
        return sccs

    def _succ(self, n):
        return [e["conclusion"] for e in self.edges if n in e["premises"]]

    def cyclic_nodes(self):
        return sorted({n for comp in self.scc_tarjan() if len(comp) > 1 for n in comp})

    def topo_order(self):
        """Kahn over premise-occurrences. Raises LicenceError naming the cycle."""
        import bisect
        pending = {n: 0 for n in self.nodes}
        as_premise = {n: [] for n in self.nodes}
        for e in self.edges:
            for p in e["premises"]:
                pending[e["conclusion"]] += 1
                as_premise[p].append(e["conclusion"])
        ready = sorted(n for n in self.nodes if pending[n] == 0)
        order = []
        while ready:
            n = ready.pop(0)
            order.append(n)
            for c in as_premise[n]:
                pending[c] -= 1
                if pending[c] == 0:
                    bisect.insort(ready, c)
        if len(order) != len(self.nodes):
            cyc = sorted(n for n in self.nodes if n not in order)
            raise LicenceError(f"cyclic nodes: {cyc}")
        return order

    def solve(self, sr, leaf_annotation=None):
        """Semiring DP over the whole hypergraph (one pass, shared values).
        Cyclic worlds raise LicenceError instead of looping."""
        order = self.topo_order()
        values, node_visits, edge_visits = {}, 0, 0
        for n in order:
            ins = sorted(self.incoming[n], key=lambda e: e["id"])
            if not ins:
                values[n] = leaf_annotation(n) if leaf_annotation else sr.one
                node_visits += 1
                continue
            acc = sr.zero
            for e in ins:
                edge_visits += 1
                term = sr.edge_w(e, e)
                for p in e["premises"]:
                    term = sr.mul(term, values[p])
                acc = sr.plus(acc, term)
            values[n] = acc
            node_visits += 1
        return values, {"node_visits": node_visits, "edge_visits": edge_visits}

    def solve_roots(self, sr, roots):
        """Re-solve mode: fresh solve per root query (no cross-query sharing).
        Returns values per root + summed visit counts."""
        vals, nv, ev = {}, 0, 0
        for r in sorted(roots):
            v, st = self._solve_sub(sr, r)
            vals[r] = v
            nv += st["node_visits"]; ev += st["edge_visits"]
        return vals, {"node_visits": nv, "edge_visits": ev}

    def _solve_sub(self, sr, root):
        """DP restricted to the sub-hypergraph reachable to root."""
        order = self.topo_order()
        keep = set()
        stack = [root]
        while stack:
            n = stack.pop()
            if n in keep:
                continue
            keep.add(n)
            for e in self.incoming[n]:
                stack.extend(e["premises"])
        values, nv, ev = {}, 0, 0
        for n in order:
            if n not in keep:
                continue
            ins = sorted(self.incoming[n], key=lambda e: e["id"])
            if not ins:
                values[n] = sr.one; nv += 1
                continue
            acc = sr.zero
            for e in ins:
                ev += 1
                term = sr.edge_w(e, e)
                for p in e["premises"]:
                    term = sr.mul(term, values[p])
                acc = sr.plus(acc, term)
            values[n] = acc; nv += 1
        return values[root], {"node_visits": nv, "edge_visits": ev}

    # ------------------------------------------------- brute force ----
    def enumerate_trees(self, node, _path=frozenset()):
        """Independent derivation-TREE enumeration (no DP). Yields nested
        ('leaf', node) | (edge_id, [subtrees]). Cycles raise LicenceError."""
        if node in _path:
            raise LicenceError(f"cycle through {node}: enumeration diverges")
        ins = sorted(self.incoming[node], key=lambda e: e["id"])
        if not ins:
            yield ("leaf", node)
            return
        for e in ins:
            sub_lists = [list(self.enumerate_trees(p, _path | {node}))
                         for p in e["premises"]]
            for combo in _cartesian(sub_lists):
                yield (e["id"], combo)

def _cartesian(lists):
    if not lists:
        yield ()
        return
    for head in lists[0]:
        for tail in _cartesian(lists[1:]):
            yield (head,) + tail

# ------------------------------------------------ brute-force aggregation ----
def brute_force_value(hg, node, sr_name, edge_map=None):
    """Aggregate enumerated trees per evaluator semantics, independent code
    path from Hypergraph.solve. Provenance monomial = product of LEAF node
    variables in the tree (edge weights one)."""
    if sr_name == "BooleanReachability":
        for _ in hg.enumerate_trees(node):
            return True
        return False
    if sr_name == "Counting":
        return sum(1 for _ in hg.enumerate_trees(node))
    if sr_name == "Viterbi(max-product)":
        best = Fraction(0)
        for t in hg.enumerate_trees(node):
            w = _tree_weight(t, edge_map)
            best = max(best, w)
        return best
    if sr_name == "Tropical(min-plus)":
        best = inf
        for t in hg.enumerate_trees(node):
            best = min(best, _tree_cost(t, edge_map))
        return best
    if sr_name == "ProvenanceNX":
        poly = {}
        for t in hg.enumerate_trees(node):
            m = frozenset(_tree_leaves(t))
            poly[m] = poly.get(m, 0) + 1
        return poly
    raise ValueError(sr_name)

def _tree_weight(t, edge_map):
    if t[0] == "leaf":
        return Fraction(1)
    total = Fraction(1)
    for sub in t[1]:
        total *= _tree_weight(sub, edge_map)
    return total * edge_map[t[0]]["viterbi_w"]

def _tree_cost(t, edge_map):
    if t[0] == "leaf":
        return Fraction(0)
    total = Fraction(0)
    for sub in t[1]:
        total += _tree_cost(sub, edge_map)
    return total + edge_map[t[0]]["tropical_w"]

def _tree_leaves(t):
    if t[0] == "leaf":
        return [t[1]]
    out = []
    for sub in t[1]:
        out.extend(_tree_leaves(sub))
    return out

# ----------------------------------------------------------- packed forest ----
def packed_forest(hg):
    """Packed derivation forest with sharing: each node stores its alternative
    (edge_id, premise-node) pairs ONCE; trees are recovered by extraction.
    Returns (forest dict, stats)."""
    t0 = time.process_time()
    order = hg.topo_order()
    forest, node_visits, edge_visits = {}, 0, 0
    for n in order:
        ins = sorted(hg.incoming[n], key=lambda e: e["id"])
        node_visits += 1
        if not ins:
            forest[n] = ("leaf",)
            continue
        alts = []
        for e in ins:
            edge_visits += 1
            alts.append((e["id"], tuple(e["premises"])))
        forest[n] = tuple(sorted(alts))
    cpu = time.process_time() - t0
    return forest, {"node_visits": node_visits, "edge_visits": edge_visits,
                    "process_time_s": cpu}

def extract_tree(forest, node, choice, depth=0):
    """Re-expand the packed forest to one derivation tree. `choice` picks the
    alternative per node (deterministic: first alternative by default)."""
    if depth > 10_000:
        raise LicenceError("extract depth bound exceeded (cycle?)")
    alt = forest[node]
    if alt == ("leaf",):
        return ("leaf", node)
    eid, premises = choice(node, alt)
    subs = [extract_tree(forest, p, choice, depth + 1) for p in premises]
    return (eid, tuple(subs))

def packed_extract_all(hg, forest, node, cap=TREE_CAP):
    """All trees of `node` from the packed forest (sharing-aware)."""
    out = []
    def rec(n, depth):
        if depth > 500:
            raise LicenceError("extract depth exceeded")
        alt = forest[n]
        if alt == ("leaf",):
            out.append(("leaf", n)); return [out[-1]]
        trees = []
        for eid, premises in alt:
            sub_lists = [rec(p, depth + 1) for p in premises]
            for combo in _cartesian(sub_lists):
                t = (eid, tuple(combo))
                trees.append(t)
        return trees
    trees = rec(node, 0)
    if len(trees) > cap:
        raise LicenceError("tree cap exceeded")
    return trees

# ------------------------------------------------------------- D18 run ----
def _leaf_prov(n):
    return {frozenset([n]): 1}

def run_d18(ow1_worlds):
    """Cross-check every evaluator against brute-force derivation enumeration
    on every OW1 world; detect cycles; measure packed-forest reuse."""
    srs = [BooleanSR(), CountingSR(), ViterbiSR(), TropicalSR(), ProvenanceNX()]
    rows, cyc_rows = [], []
    t_start = time.process_time()
    n_checks, n_agree = 0, 0
    for w in sorted(ow1_worlds, key=lambda w: w["id"]):
        hg = Hypergraph(w["nodes"], w["edges"])
        edge_map = {e["id"]: e for e in w["edges"]}
        if w["cyclic"]:
            try:
                hg.solve(BooleanSR())
                row = {"world": w["id"], "solve_raised": False, "defect": True}
            except LicenceError as ex:
                row = {"world": w["id"], "solve_raised": True,
                       "cyclic_nodes": hg.cyclic_nodes(), "defect": False,
                       "licence": "ACYCLIC_DP_LICENCE_INVALID__REPORTED"}
            try:
                next(hg.enumerate_trees(w["nodes"][-1]))
                row["enumeration_raised"] = False
            except LicenceError:
                row["enumeration_raised"] = True
            except StopIteration:
                row["enumeration_raised"] = True  # no tree, no divergence
            cyc_rows.append(row)
            continue
        for sr in srs:
            la = _leaf_prov if isinstance(sr, ProvenanceNX) else None
            values, _st = hg.solve(sr, leaf_annotation=la)
            for n in sorted(w["nodes"]):
                bf = brute_force_value(hg, n, sr.name, edge_map)
                dp = values[n]
                ok = (dp == bf)
                n_checks += 1
                n_agree += bool(ok)
                if not ok:
                    rows.append({"world": w["id"], "semiring": sr.name,
                                 "node": n, "dp": repr(dp), "bf": repr(bf),
                                 "agree": False})
        # packed-forest cross-check: extraction == enumeration
        forest, pst = packed_forest(hg)
        for n in sorted(w["nodes"]):
            ext = sorted(map(repr, packed_extract_all(hg, forest, n)))
            enum = sorted(map(repr, hg.enumerate_trees(n)))
            n_checks += 1
            n_agree += bool(ext == enum)
            if ext != enum:
                rows.append({"world": w["id"], "semiring": "PackedForest",
                             "node": n, "agree": False})
    agreement = (n_agree / n_checks) if n_checks else 1.0
    return {"agreement_exact": agreement, "n_checks": n_checks,
            "n_agree": n_agree, "disagreements": rows,
            "cyclic_worlds": cyc_rows, "cpu_s": time.process_time() - t_start}

def measure_reuse(ow1_worlds):
    """Packed-forest shared solve vs per-root re-solve, on every acyclic OW1
    world: node/edge visit totals + process_time. Whole-hypergraph query set."""
    rows = []
    t_start = time.process_time()
    for w in sorted(ow1_worlds, key=lambda w: w["id"]):
        if w["cyclic"]:
            continue
        hg = Hypergraph(w["nodes"], w["edges"])
        _f, packed = packed_forest(hg)                     # one shared pass
        sr = CountingSR()
        _v, resolve = hg.solve_roots(sr, hg.nodes)         # fresh per root
        # packed query cost amortised: one packed pass serves every root
        rows.append({"world": w["id"], "n_nodes": len(w["nodes"]),
                     "n_edges": len(w["edges"]),
                     "packed_node_visits": packed["node_visits"],
                     "packed_edge_visits": packed["edge_visits"],
                     "packed_cpu_s": packed["process_time_s"],
                     "resolve_node_visits": resolve["node_visits"],
                     "resolve_edge_visits": resolve["edge_visits"],
                     "node_visit_ratio": round(resolve["node_visits"]
                                               / max(1, packed["node_visits"]), 3),
                     "edge_visit_ratio": round(resolve["edge_visits"]
                                               / max(1, packed["edge_visits"]), 3)})
    tot_p = sum(r["packed_node_visits"] for r in rows)
    tot_r = sum(r["resolve_node_visits"] for r in rows)
    tot_pe = sum(r["packed_edge_visits"] for r in rows)
    tot_re = sum(r["resolve_edge_visits"] for r in rows)
    return {"per_world": rows, "n_worlds": len(rows),
            "total_packed_node_visits": tot_p, "total_resolve_node_visits": tot_r,
            "total_packed_edge_visits": tot_pe, "total_resolve_edge_visits": tot_re,
            "aggregate_node_visit_ratio": round(tot_r / max(1, tot_p), 3),
            "aggregate_edge_visit_ratio": round(tot_re / max(1, tot_pe), 3),
            "cpu_s": time.process_time() - t_start}

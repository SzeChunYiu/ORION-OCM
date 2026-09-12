"""N10 — event-causal / partial-order carrier: exact microscope and bounded-reduction attack.

Target: novel-domain hypothesis N10 (Event-Causal / Partial-Order Intelligence). The hypothesis document
`GMI_NOVEL_DOMAIN_HYPOTHESES_V1.md` is NOT PRESENT on this branch (see the receipt field
`hypothesis_source_status`); the N10 specification executed here is RECONSTRUCTED from the task directive's
enumeration (carrier, native operators, natural complexity coordinate, predicted niche, capability hypothesis,
weak regime, parent attacks, domain discriminator) and tested against the admission contract that IS present:
the domain criterion of `GMI_STRUCTURAL_DOMAINS_KINGDOMS_V1.md` section 2, the domain-novelty criterion of
section 14, and the executable method of `GMI_DOMAIN_CANDIDATES_DC1_DC9_V1.md` sections 0 and 2.

CARRIER (reconstructed N10): a PARTIAL ORDER OF EVENTS (an event structure / causal poset), held as one vector
clock per event over the w causal chains. The sufficient cognitive state is the happens-before order itself,
NOT the sequence in which the events were observed.

NATIVE OPERATORS: EXTEND (append an event over its immediate predecessors), JOIN (componentwise least upper
bound of the predecessors' clocks — the lattice join on downsets), COMPARE (happens-before test), CONCURRENT?
(incomparability test).

NATURAL COMPLEXITY COORDINATE: the WIDTH w of the partial order (the size of the largest antichain = the number
of concurrent causal chains), against the number of linear extensions of the poset, which is the number of
distinct interleavings a sequence carrier would have to account for.

ECOLOGY E_causal(w, L): w causal chains of L events each (n = w*L events). Event (c, l) depends on (c, l-1) and,
at a declared LCG-chosen rate, on (c', l-1) of one other chain. Development presents the events ONE AT A TIME in
a DECLARED LINEAR EXTENSION of the poset (an interleaving). The OBLIGATION is the one the carrier is for:
decide, for every ordered pair of events, whether the first happens before the second, the second before the
first, or the two are CONCURRENT -- and do so INVARIANTLY under which interleaving was observed. Each cell is
therefore run under TWO different declared linear extensions of the SAME poset, and interleaving invariance is
an executed measurement, not an assumption.

ROWS (all charged exactly through Machine; the same query pairs, the same answers compared bit for bit):
  POSET          the candidate: one vector clock per event, JOIN on append, componentwise COMPARE on query.
  PAIRTABLE      matched parent 1, D2 (table memory, eager): DENIED the join operator, so it stores the observed
                 immediate-dependency edges and materializes the full n x n transitive closure by a charged
                 Floyd-Warshall pass at the end of development, then answers by store lookups. Its answers are
                 provably identical to POSET's (both decide reachability in the same DAG): the reduction attack.
  SEQ_MEM        matched parent 2, D2 (sequence / exemplar memory -- the row the hypothesis names): stores the
                 observed interleaving as positions and answers from position order. It can never return
                 CONCURRENT, and its answers depend on WHICH interleaving it saw: the domain discriminator.
  PROG_SEARCH    matched parent 3, D4/D5 (program search + verifier): stores the immediate-dependency edge list
                 and searches for a causal path at query time. Lazy; answers identical to POSET's.
  POSET_NOJOIN   negative twin: the candidate with its DISTINGUISHING OPERATOR REMOVED. Each event's clock
                 carries only its own chain component, so causality never propagates across a cross-chain edge.

PRECISION INSTRUMENTS (the dc_energy.Arith pattern, used here because arithmetic RANGE is exactly what a causal
counter consumes): `fx8` is the registered 8-bit fixed-point universe (clock components and sequence positions
are numbers in that universe, one causal step = FX_ONE, so a component saturates past 7 steps) and `wide` is the
declared wide-integer instrument evaluating the IDENTICAL charged operation sequence at unbounded precision.
Counter-based rows (POSET, SEQ_MEM, POSET_NOJOIN) consume range; the purely relational rows (PAIRTABLE,
PROG_SEARCH) do not, so the instrument pair separates a precision gate from a representational one.

ACCOUNTING: exec/upd/ver/rev are exact charged Machine ops under the declared column (the REDUCED price).
`native_ops` / `native_compile_ops` price the same computation at one op per JOIN / COMPARE, one op per table
lookup, one op per closure relaxation, one op per search node. `desc_bits` is the information-theoretic
description of the served state; every formula is declared in the receipt.
"""
from __future__ import annotations

import json
import math
import os
import sys

from . import bases
from .core import FX_ONE, Machine, sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
THETA = 0.85
PROG_OPS = 14  # declared program length of the causal-path search program


def _lcg_stream(seed):
    """declared deterministic generator (32-bit LCG, Numerical Recipes constants; bits 16.. per draw)."""
    x = (seed * 1103515245 + 12345) & 0xFFFFFFFF
    while True:
        x = (x * 1103515245 + 12345) & 0xFFFFFFFF
        yield (x >> 16) & 0xFFFF


def _idx_bits(x):
    return max(1, math.ceil(math.log2(x))) if x > 1 else 1


# ------------------------------------------------------------------------------------------------- ecology
def poset(w, L, cross_num=1, cross_den=2, seed=53):
    """w causal chains of L events; event (c, l) depends on (c, l-1) and, at rate cross_num/cross_den, on one
    declared other chain's (c', l-1). Returns (n, preds, chain_of, level_of)."""
    g = _lcg_stream(seed)
    n = w * L
    eid = lambda c, l: c * L + l
    preds = [[] for _ in range(n)]
    chain_of = [0] * n
    level_of = [0] * n
    for l in range(L):
        for c in range(w):
            e = eid(c, l)
            chain_of[e], level_of[e] = c, l
            if l > 0:
                preds[e].append(eid(c, l - 1))
                if w > 1 and next(g) % cross_den < cross_num:
                    cp = (c + 1 + next(g) % (w - 1)) % w
                    if cp != c:
                        preds[e].append(eid(cp, l - 1))
    return n, preds, chain_of, level_of


def closure(n, preds):
    """uncharged declared reference: reach[i][j] = 1 iff event i happens before event j."""
    succ = [[] for _ in range(n)]
    for j, ps in enumerate(preds):
        for p in ps:
            succ[p].append(j)
    reach = [[0] * n for _ in range(n)]
    for i in range(n):
        stack = list(succ[i])
        while stack:
            k = stack.pop()
            if not reach[i][k]:
                reach[i][k] = 1
                stack.extend(succ[k])
    return reach


def interleavings(n, preds, seed=53):
    """two DECLARED linear extensions of the same poset.
    variant 0: level-major (sort by (level, chain)) -- always a topological order for this dependency shape.
    variant 1: Kahn's algorithm with an LCG tie-break over the ready set."""
    level = [0] * n
    for j in range(n):
        level[j] = 0 if not preds[j] else 1 + max(level[p] for p in preds[j])
    v0 = sorted(range(n), key=lambda e: (level[e], e))
    g = _lcg_stream(seed + 7)
    indeg = [len(p) for p in preds]
    succ = [[] for _ in range(n)]
    for j, ps in enumerate(preds):
        for p in ps:
            succ[p].append(j)
    ready = [e for e in range(n) if indeg[e] == 0]
    v1 = []
    while ready:
        k = next(g) % len(ready)
        e = ready.pop(k)
        v1.append(e)
        for s in succ[e]:
            indeg[s] -= 1
            if indeg[s] == 0:
                ready.append(s)
    return [v0, v1]


def _count_linear_extensions(n, preds, cap=10 ** 15):
    """exact count of linear extensions (the interleaving burden a sequence carrier faces), by downset DP.
    Returned only for n <= 20; larger posets report None (the count is astronomically large and not needed)."""
    if n > 20:
        return None
    predmask = [0] * n
    for j, ps in enumerate(preds):
        for p in ps:
            predmask[j] |= 1 << p
    dp = {0: 1}
    for _ in range(n):
        nd = {}
        for S, c in dp.items():
            for e in range(n):
                if not (S >> e) & 1 and (predmask[e] & ~S) == 0:
                    nd[S | (1 << e)] = nd.get(S | (1 << e), 0) + c
        dp = nd
        if not dp:
            break
    return min(dp.get((1 << n) - 1, 0), cap)


def ecology(w, L, cross_num=1, cross_den=2, seed=53):
    n, preds, chain_of, level_of = poset(w, L, cross_num, cross_den, seed)
    reach = closure(n, preds)
    queries = [(i, j) for i in range(n) for j in range(n) if i != j]
    truth = {}
    for (i, j) in queries:
        truth[(i, j)] = 1 if reach[i][j] else (2 if reach[j][i] else 0)
    n_edges = sum(len(p) for p in preds)
    n_ordered = sum(1 for q in queries if truth[q] != 0)
    width = max(sum(1 for j in range(n) if not reach[i][j] and not reach[j][i] and i != j) for i in range(n)) + 1 if n > 1 else 1
    return {"w": w, "L": L, "n": n, "preds": preds, "chain_of": chain_of, "level_of": level_of,
            "queries": queries, "truth": truth, "n_queries": len(queries), "n_edges": n_edges,
            "n_ordered_pairs": n_ordered, "n_concurrent_pairs": len(queries) - n_ordered,
            "seq_mem_capability_upper_bound": round(n_ordered / len(queries), 4),
            "max_incomparable_neighbourhood": width, "linear_extensions": _count_linear_extensions(n, preds),
            "interleavings": interleavings(n, preds, seed), "cross_rate": f"{cross_num}/{cross_den}"}


# ------------------------------------------------------------------------------------------------- arithmetic
class Arith:
    """charged scalar arithmetic in one of two DECLARED precision instruments with IDENTICAL op charges:
      'fx8'  the registered 8-bit fixed-point universe (TOTAL_BITS 8, FRAC_BITS 4; one causal step = FX_ONE, so
             a counter saturates past 7 steps);
      'wide' the declared wide-integer instrument (gap G5): the same charged operation sequence evaluated at
             unbounded integer precision.
    Op counts are identical in the two modes, so any capability difference is attributable to precision alone."""

    def __init__(self, M, mode):
        self.M = M
        self.mode = mode

    def step(self, a):
        """one causal increment."""
        if self.mode == "wide":
            self.M.op("ADD", 0, 0)
            return a + FX_ONE
        return self.M.op("ADD", a, FX_ONE)

    def gt(self, a, b):
        if self.mode == "wide":
            self.M.op("GT", 0, 0)
            return int(a > b)
        return self.M.op("GT", a, b)

    def eq(self, a, b):
        if self.mode == "wide":
            self.M.op("EQ", 0, 0)
            return int(a == b)
        return self.M.op("EQ", a, b)

    def maxi(self, a, b):
        """JOIN component: charged GT then SEL, identically in both instruments."""
        g = self.gt(a, b)
        if self.mode == "wide":
            self.M.op("SEL", 0, 0, 0)
            return a if g else b
        return self.M.op("SEL", g, a, b)


# ------------------------------------------------------------------------------------------------- rows
class Row:
    row = "?"

    def __init__(self, eco, arith=None):
        self.e = eco
        self.A = arith
        self.native_ops = 0
        self.native_compile_ops = 0

    def init(self, M):
        pass

    def observe(self, M, e):
        pass

    def finalize(self, M):
        pass

    def query(self, M, q):
        raise NotImplementedError

    def desc_bits(self):
        return 0


class Poset(Row):
    """the candidate: one vector clock per event; JOIN on EXTEND, componentwise COMPARE on query."""
    row = "POSET"

    def init(self, M):
        self.w = self.e["w"]
        self.clock = [[0] * self.w for _ in range(self.e["n"])]

    def observe(self, M, e):
        w = self.w
        v = [0] * w
        for p in self.e["preds"][e]:
            for k in range(w):
                v[k] = self.A.maxi(v[k], self.clock[p][k])  # JOIN: componentwise least upper bound
        c = self.e["chain_of"][e]
        v[c] = self.A.step(v[c])  # EXTEND: own causal component advances
        self.clock[e] = v
        self.native_ops += 1  # one JOIN+EXTEND at the declared native price

    def _le(self, M, i, j):
        """componentwise <= : the happens-before test on the clock lattice."""
        for k in range(self.w):
            if self.A.gt(self.clock[i][k], self.clock[j][k]):
                return 0
        return 1

    def query(self, M, q):
        i, j = q
        self.native_ops += 1  # one COMPARE at the declared native price
        if self._le(M, i, j):
            return 1
        if self._le(M, j, i):
            return 2
        return 0

    def desc_bits(self):
        return self.e["n"] * self.e["w"] * _idx_bits(self.e["L"] + 1)


class PosetNoJoin(Poset):
    """negative twin: the JOIN removed. A clock carries only its own chain component, so causality never
    propagates across a cross-chain dependency edge."""
    row = "POSET_NOJOIN"

    def observe(self, M, e):
        w = self.w
        v = [0] * w
        for p in self.e["preds"][e]:
            for k in range(w):
                self.A.maxi(0, 0)  # the same charged op sequence, with the join result discarded
        c = self.e["chain_of"][e]
        own = self.clock[self.e["preds"][e][0]][c] if self.e["preds"][e] else 0
        v[c] = self.A.step(own if self.e["chain_of"][self.e["preds"][e][0]] == c else 0) if self.e["preds"][e] else self.A.step(0)
        self.clock[e] = v
        self.native_ops += 1


class PairTable(Row):
    """matched parent 1 (D2 table memory, eager). DENIED the join operator, so it stores the observed
    immediate-dependency edges and materializes the full transitive closure by a charged Floyd-Warshall pass."""
    row = "PAIRTABLE"

    def init(self, M):
        n = self.e["n"]
        self.R = [[0] * n for _ in range(n)]
        M.declare_store("hb")

    def observe(self, M, e):
        for p in self.e["preds"][e]:
            self.R[p][e] = M.op("OR", self.R[p][e], 1)

    def finalize(self, M):
        n = self.e["n"]
        # charged Floyd-Warshall: n^3 relaxations of one AND and one OR each
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    self.R[i][j] = M.op("OR", self.R[i][j], M.op("AND", self.R[i][k], self.R[k][j]))
            self.native_compile_ops += 1  # one closure round at the declared native price
        for i in range(n):
            for j in range(n):
                if i != j and self.R[i][j]:
                    M.op("S_INSERT", "hb", (i, j), 1)
        self.n_entries = sum(1 for i in range(n) for j in range(n) if i != j and self.R[i][j])

    def query(self, M, q):
        i, j = q
        self.native_ops += 2  # two LOOKUPs at the declared native price
        if M.op("S_LOOKUP", "hb", (i, j)):
            return 1
        if M.op("S_LOOKUP", "hb", (j, i)):
            return 2
        return 0

    def desc_bits(self):
        return self.e["n"] * self.e["n"]


class SeqMem(Row):
    """matched parent 2 (D2 sequence / exemplar memory): stores the observed interleaving as positions and
    answers from position order. It can never return CONCURRENT, and its answers depend on the interleaving."""
    row = "SEQ_MEM"

    def init(self, M):
        self.pos = [0] * self.e["n"]
        self.t = 0

    def observe(self, M, e):
        self.t = self.A.step(self.t)
        self.pos[e] = self.t

    def query(self, M, q):
        i, j = q
        self.native_ops += 1
        return 1 if self.A.gt(self.pos[j], self.pos[i]) else 2

    def desc_bits(self):
        return self.e["n"] * _idx_bits(self.e["n"] + 1)


class ProgSearch(Row):
    """matched parent 3 (D4/D5 program search + verifier): the immediate-dependency edge list plus a declared
    causal-path search program run at query time. Lazy; answers identical to the candidate's."""
    row = "PROG_SEARCH"

    def init(self, M):
        n = self.e["n"]
        self.succ = [[] for _ in range(n)]
        M.declare_program(PROG_OPS)

    def observe(self, M, e):
        for p in self.e["preds"][e]:
            self.succ[p].append(e)

    def _path(self, M, i, j):
        seen = {i}
        stack = [i]
        while stack:
            u = stack.pop()
            self.native_ops += 1  # one search node at the declared native price
            for v in self.succ[u]:
                if M.op("EQ", v, j):
                    return 1
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        return 0

    def query(self, M, q):
        i, j = q
        if self._path(M, i, j):
            return 1
        if self._path(M, j, i):
            return 2
        return 0

    def desc_bits(self):
        return self.e["n_edges"] * 2 * _idx_bits(self.e["n"]) + PROG_OPS


ROWS = {"POSET": Poset, "PAIRTABLE": PairTable, "SEQ_MEM": SeqMem, "PROG_SEARCH": ProgSearch,
        "POSET_NOJOIN": PosetNoJoin}
CANDIDATE = "POSET"
PARENTS = ("PAIRTABLE", "SEQ_MEM", "PROG_SEARCH")
TWIN = "POSET_NOJOIN"


def run(row, basis, eco, seed=0, precision="wide", interleaving=0):
    M = Machine(basis, seed=seed)
    ref = ROWS[row](eco, Arith(M, precision))
    M.phase("exec")
    ref.init(M)
    init = dict(M.L.c)
    order = eco["interleavings"][interleaving]
    for e in order:
        M.phase("upd")
        ref.observe(M, e)
        M.end_event()
    M.phase("upd")
    ref.finalize(M)
    M.end_event()
    learn = dict(M.L.c)
    M.phase("exec")
    correct = 0
    answers = []
    for q in eco["queries"]:
        a = ref.query(M, q)
        answers.append([q[0], q[1], a])
        correct += int(a == eco["truth"][q])
    cap = round(correct / len(eco["queries"]), 4)
    R = dict(M.L.c)
    nq = len(eco["queries"])
    return {"row": row, "basis": basis.name, "precision": precision, "interleaving": interleaving,
            "capability": cap, "admissible": cap >= THETA, "R": R,
            "compile_ops": init["exec"], "learn_ops": learn["upd"],
            "exec_per_query": round((R["exec"] - learn["exec"]) / nq, 4),
            "native_ops": ref.native_ops, "native_compile_ops": ref.native_compile_ops,
            "native_per_query": round(ref.native_ops / nq, 4),
            "desc_bits": ref.desc_bits(), "n_queries": nq, "answer_signature": sha256_of(answers)}


CELLS = {
    "w1_L8":  {"w": 1, "L": 8},
    "w2_L4":  {"w": 2, "L": 4},
    "w2_L8":  {"w": 2, "L": 8},
    "w4_L4":  {"w": 4, "L": 4},
    "w4_L8":  {"w": 4, "L": 8},
    "w8_L4":  {"w": 8, "L": 4},
    "w2_L12": {"w": 2, "L": 12},
    "w4_L12": {"w": 4, "L": 12},
}
# DECLARED EXTENSION (RV-377-052): an OUT-OF-SAMPLE grid for the three exact laws that the failed clauses of
# RV-377-051 uncovered -- the SERVE law (the candidate's serve scales with WIDTH, the search parent's with DEPTH, so
# the candidate wins iff L > w), the PRECISION-GATE law (a counter-based row is gated exactly when the range of the
# counter it actually uses exceeds 8: L for the vector clock, n = wL for the sequence position) and the NEGATIVE-TWIN
# ATTRIBUTION law (removing the JOIN costs exactly the cross-chain ordered pairs). The widths 3, 6, 12 and the chain
# length L = 6 appear in no CELLS cell; five cells satisfy L > w and three do not, so the serve law is tested in both
# directions, and exactly one cell has L > 8 while all eight have n > 8, so the precision law's two thresholds are
# separated by the grid rather than confounded.
CELLS_R2 = {
    "w2_L6":  {"w": 2, "L": 6},
    "w3_L6":  {"w": 3, "L": 6},
    "w4_L6":  {"w": 4, "L": 6},
    "w6_L4":  {"w": 6, "L": 4},
    "w6_L6":  {"w": 6, "L": 6},
    "w3_L12": {"w": 3, "L": 12},
    "w6_L8":  {"w": 6, "L": 8},
    "w12_L4": {"w": 12, "L": 4},
}
COLUMNS = ("B0_LOCAL_ADAPTIVE_TRANSDUCERS", "B0i_LOCAL_ADAPTIVE_TRANSDUCERS")
PRECISIONS = ("fx8", "wide")


def _basis(col):
    return bases.INDEXED_VARIANTS[col] if col in bases.INDEXED_VARIANTS else bases.ALL[col]


def lifecycle(r, H, price):
    if price == "native":
        return r["desc_bits"] + r["native_compile_ops"] + H * r["native_per_query"]
    return r["desc_bits"] + r["compile_ops"] + r["learn_ops"] + H * r["exec_per_query"]


def crossover(r1, r2, price):
    """the reuse horizon H at which r1 and r2 have equal lifecycle cost, or None if they never cross for H >= 0."""
    if price == "native":
        d1, s1 = r1["desc_bits"] + r1["native_compile_ops"], r1["native_per_query"]
        d2, s2 = r2["desc_bits"] + r2["native_compile_ops"], r2["native_per_query"]
    else:
        d1, s1 = r1["desc_bits"] + r1["compile_ops"] + r1["learn_ops"], r1["exec_per_query"]
        d2, s2 = r2["desc_bits"] + r2["compile_ops"] + r2["learn_ops"], r2["exec_per_query"]
    if s1 == s2:
        return None
    H = (d2 - d1) / (s1 - s2)
    return round(H, 4) if H >= 0 else None


BASE_GRID = (1, 16, 128, 1024)


def main(tag="V27_N10_PARTIALORDER", seed=0, columns=COLUMNS, cell_grid=None,
         schema="StageDNN10PartialOrderV1", revival="RV-377-051", laws_under_test=False):
    CELLS = cell_grid or globals()["CELLS"]
    cells, ecos = {}, {}
    for cname, spec in CELLS.items():
        eco = ecology(spec["w"], spec["L"])
        ecos[cname] = eco
        for rname in ROWS:
            for col in columns:
                for prec in PRECISIONS:
                    for il in (0, 1):
                        cells[(cname, rname, col, prec, il)] = run(rname, _basis(col), eco, seed, prec, il)

    # --- the domain discriminator: is the row's answer set INVARIANT under the observed interleaving?
    invariance = {}
    for cname in CELLS:
        for col in columns:
            for prec in PRECISIONS:
                for r in ROWS:
                    invariance[f"{cname}|{col}|{prec}|{r}"] = (
                        cells[(cname, r, col, prec, 0)]["answer_signature"]
                        == cells[(cname, r, col, prec, 1)]["answer_signature"])

    # --- the bounded-reduction attack: exact developmental equality of candidate and each matched parent
    equality = {}
    for cname in CELLS:
        for col in columns:
            for prec in PRECISIONS:
                cand = cells[(cname, CANDIDATE, col, prec, 0)]["answer_signature"]
                for p in PARENTS + (TWIN,):
                    equality[f"{cname}|{col}|{prec}|{CANDIDATE}_vs_{p}"] = (
                        cand == cells[(cname, p, col, prec, 0)]["answer_signature"])

    # --- DG-2: the reuse-horizon grid is CONSTRUCTED from the analytic crossovers, not truncated
    crossovers, grid = {}, {}
    for cname in CELLS:
        for col in columns:
            for prec in PRECISIONS:
                for price in ("reduced", "native"):
                    adm = [r for r in ROWS if cells[(cname, r, col, prec, 0)]["admissible"]]
                    pts = set(BASE_GRID)
                    for a, r1 in enumerate(adm):
                        for r2 in adm[a + 1:]:
                            H = crossover(cells[(cname, r1, col, prec, 0)], cells[(cname, r2, col, prec, 0)], price)
                            crossovers[f"{cname}|{col}|{prec}|{price}|{r1}_vs_{r2}"] = H
                            if H is not None:
                                pts.add(max(0, int(math.floor(H / 2))))
                                pts.add(int(math.ceil(H)) + 1)
                                pts.add(int(math.ceil(2 * H)))
                    grid[f"{cname}|{col}|{prec}|{price}"] = sorted(p for p in pts if p >= 0)

    frontier = {}
    for cname in CELLS:
        for col in columns:
            for prec in PRECISIONS:
                for price in ("reduced", "native"):
                    adm = [r for r in ROWS if cells[(cname, r, col, prec, 0)]["admissible"]]
                    for H in grid[f"{cname}|{col}|{prec}|{price}"]:
                        costs = {r: lifecycle(cells[(cname, r, col, prec, 0)], H, price) for r in adm}
                        frontier[f"{cname}|{col}|{prec}|{price}|H={H}"] = (
                            sorted(r for r, c in costs.items() if c <= min(costs.values()) + 1e-9) if costs else [])

    receipt = {
        "schema": schema, "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422],
        "revival_record": revival, "run_tag": tag,
        "domain_candidate": "N10 event-causal / partial-order intelligence",
        "hypothesis_source_status": (
            "GMI_NOVEL_DOMAIN_HYPOTHESES_V1.md is NOT PRESENT on branch claude/gmi-d0-d1-research-dnbp8i "
            "(nor GMI_NEW_DOMAIN_HARDENING_PROGRAMME_V1.md, nor GMI_DOMAIN_DERIVATION_COMPLETENESS_V1.md). "
            "The N10 specification executed here is RECONSTRUCTED from the task directive's enumeration and "
            "tested against the admission contract that is present: kingdoms sections 2 and 14 and the "
            "DC1-DC9 method sections 0 and 2. Every reconstructed element is stated in `candidate_spec`."),
        "candidate_spec": {
            "carrier": "a causal poset of n events held as one w-component vector clock per event; the served state "
                       "is the happens-before order, not the observed sequence",
            "native_operators": "EXTEND (append an event over its immediate predecessors), JOIN (componentwise least "
                                "upper bound of the predecessors' clocks), COMPARE (happens-before), CONCURRENT? "
                                "(incomparability)",
            "natural_complexity_coordinate": "the WIDTH w of the partial order (largest antichain / number of "
                                             "concurrent causal chains), against the number of linear extensions of "
                                             "the poset (reported per cell for n <= 20)",
            "predicted_niche": "obligations whose answer is an invariant of the causal order while the SAME causal "
                               "content is observed in many different interleavings",
            "capability_hypothesis": "exact happens-before and concurrency answers, invariant under the observed "
                                     "interleaving, with a description of n*w*ceil(log2(L+1)) bits, where a sequence "
                                     "carrier cannot represent concurrency at all and a table parent needs n^2 bits",
            "weak_regime": "width 1 (a total order), where the poset carrier degenerates exactly to the sequence "
                           "carrier; and any obligation that actually depends on the observed interleaving",
            "parent_attacks": "D2 table memory (PAIRTABLE, eager closure), D2 sequence/exemplar memory (SEQ_MEM) and "
                              "D4/D5 program search (PROG_SEARCH, lazy path search)",
            "domain_discriminator": "interleaving invariance: each cell is run under two declared linear extensions of "
                                    "the same poset and the answer signatures are compared",
        },
        "cells_spec": CELLS, "columns": list(columns), "precisions": list(PRECISIONS), "theta": THETA,
        "rows": list(ROWS), "row_roles": {"candidate": CANDIDATE, "matched_parents": list(PARENTS),
                                          "negative_twin": TWIN},
        "generator": "LCG(1103515245, 12345), bits 16.. per draw; poset seed 53, cross-chain rate 1/2; interleaving "
                     "variant 0 = level-major order, variant 1 = Kahn with LCG tie-break (seed 60)",
        "precision_instruments": {
            "fx8": "registered universe: TOTAL_BITS 8, FRAC_BITS 4; one causal step = FX_ONE = 16 raw, so a counter "
                   "component saturates past 7 steps",
            "wide": "declared wide-integer instrument (gap G5): identical charged operation sequence at unbounded "
                    "integer precision"},
        "desc_bits_formulas": {
            "POSET": "n*w*ceil(log2(L+1))", "POSET_NOJOIN": "n*w*ceil(log2(L+1))",
            "PAIRTABLE": "n^2", "SEQ_MEM": "n*ceil(log2(n+1))",
            "PROG_SEARCH": "n_edges*2*ceil(log2 n) + PROG_OPS"},
        "native_price_vector": "one op per JOIN+EXTEND and one per COMPARE (poset); two ops per table LOOKUP and one "
                               "per closure round (table parent); one op per position compare (sequence parent); one "
                               "op per search node (program search). Declared, not measured.",
        "ecology_facts": {c: {k: ecos[c][k] for k in ("w", "L", "n", "n_queries", "n_edges", "n_ordered_pairs",
                                                      "n_concurrent_pairs", "seq_mem_capability_upper_bound",
                                                      "max_incomparable_neighbourhood", "linear_extensions",
                                                      "cross_rate")} for c in CELLS},
        "cells": {f"{c}|{r}|{col}|{p}|il{il}": {k: v for k, v in dd.items() if k not in ("row", "basis")}
                  for (c, r, col, p, il), dd in cells.items()},
        "interleaving_invariance": invariance,
        "developmental_equality": equality,
        "crossovers": crossovers,
        "frontier_grid": grid,
        "frontier": frontier,
        "dg2_compliance": "the reuse-horizon grid of every (cell, column, precision, price) is the union of the base "
                          "grid (1, 16, 128, 1024) with floor(H*/2), ceil(H*)+1 and ceil(2H*) of EVERY pairwise "
                          "analytic crossover among the admissible rows, so no frontier statement is made on a "
                          "truncated grid",
        "claim_ceiling": "exact charged replay at scope; one declared poset per cell, two declared interleavings; the "
                         "reduction attack is an exact answer-signature equality test against three matched "
                         "existing-domain parents; native prices are declared, not measured; no new domain is claimed",
    }
    # --- the three EXACT LAWS under test (RV-377-052); each is a per-cell predicate reported cell by cell
    if laws_under_test:
        laws = {}
        for cname, spec in CELLS.items():
            w, L = spec["w"], spec["L"]
            e = ecos[cname]
            for col in columns:
                for p in PRECISIONS:
                    po = cells[(cname, "POSET", col, p, 0)]
                    ps = cells[(cname, "PROG_SEARCH", col, p, 0)]
                    laws[f"serve_law|{cname}|{col}|{p}"] = {
                        "L_gt_w": L > w, "poset_serve": po["exec_per_query"], "search_serve": ps["exec_per_query"],
                        "poset_cheaper": po["exec_per_query"] < ps["exec_per_query"],
                        "law_holds": (po["exec_per_query"] < ps["exec_per_query"]) == (L > w)}
                tw = cells[(cname, "POSET_NOJOIN", col, "wide", 0)]
                want = round((e["n_concurrent_pairs"] + w * L * (L - 1)) / e["n_queries"], 4)
                laws[f"twin_law|{cname}|{col}"] = {
                    "predicted": want, "observed": tw["capability"],
                    "admissible_predicted": want >= THETA, "admissible_observed": tw["admissible"],
                    "law_holds": abs(tw["capability"] - want) <= 0.0001 and (want >= THETA) == tw["admissible"]}
                for r, rng in (("POSET", L), ("POSET_NOJOIN", L), ("SEQ_MEM", w * L)):
                    a = cells[(cname, r, col, "fx8", 0)]["capability"]
                    b = cells[(cname, r, col, "wide", 0)]["capability"]
                    laws[f"precision_law|{cname}|{col}|{r}"] = {
                        "counter_range": rng, "gated_predicted": rng > 8, "fx8": a, "wide": b,
                        "law_holds": (a < b) == (rng > 8)}
                for r in ("PAIRTABLE", "PROG_SEARCH"):
                    a = cells[(cname, r, col, "fx8", 0)]
                    b = cells[(cname, r, col, "wide", 0)]
                    laws[f"precision_law|{cname}|{col}|{r}"] = {
                        "counter_range": 0, "gated_predicted": False,
                        "law_holds": a["capability"] == b["capability"] and a["R"] == b["R"]
                                     and a["answer_signature"] == b["answer_signature"]}
        receipt["exact_laws_under_test"] = laws
        receipt["exact_laws_summary"] = {k: sum(1 for kk, v in laws.items() if kk.startswith(k) and v["law_holds"])
                                         for k in ("serve_law", "twin_law", "precision_law")}
        receipt["exact_laws_total"] = {k: sum(1 for kk in laws if kk.startswith(k))
                                       for k in ("serve_law", "twin_law", "precision_law")}
        receipt["exact_laws_declared"] = {
            "serve_law": "exec_per_query(POSET) < exec_per_query(PROG_SEARCH) iff L > w",
            "precision_law": "a row's fx8 capability is strictly below its wide capability iff the range of the "
                             "counter it uses exceeds 8 (range L for POSET and POSET_NOJOIN, n = wL for SEQ_MEM, "
                             "no counter for PAIRTABLE and PROG_SEARCH)",
            "twin_law": "capability(POSET_NOJOIN, wide) = (n_concurrent_pairs + w*L*(L-1)) / n_queries"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_DN_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    if laws_under_test:
        print("EXACT LAWS", receipt["exact_laws_summary"], "of", receipt["exact_laws_total"])
    c0, p0 = columns[0], "wide"
    for cname in CELLS:
        e = ecos[cname]
        print(cname, "n", e["n"], "conc", e["n_concurrent_pairs"], "/", e["n_queries"], "linext", e["linear_extensions"])
        print("   cap fx8 ", {r: cells[(cname, r, c0, 'fx8', 0)]["capability"] for r in ROWS})
        print("   cap wide", {r: cells[(cname, r, c0, p0, 0)]["capability"] for r in ROWS})
        print("   invariant(wide)", {r: invariance[f'{cname}|{c0}|{p0}|{r}'] for r in ROWS})
        print("   eq(wide)", {p: equality[f'{cname}|{c0}|{p0}|POSET_vs_{p}'] for p in PARENTS + (TWIN,)})
        print("   desc", {r: cells[(cname, r, c0, p0, 0)]["desc_bits"] for r in ROWS},
              "exec/q", {r: cells[(cname, r, c0, p0, 0)]["exec_per_query"] for r in ROWS})
    return receipt


if __name__ == "__main__":
    main(tag=sys.argv[1] if len(sys.argv) > 1 else "V27_N10_PARTIALORDER")

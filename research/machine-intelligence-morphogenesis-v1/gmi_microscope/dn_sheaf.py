"""N3 — relational-constraint / sheaf carrier: exact microscope and bounded-reduction attack.

Target: novel-domain hypothesis N3 (Relational-Constraint / Sheaf Intelligence). The hypothesis document
`GMI_NOVEL_DOMAIN_HYPOTHESES_V1.md` is NOT PRESENT on this branch (see the receipt field
`hypothesis_source_status`); the N3 specification executed here is RECONSTRUCTED from the task directive's
enumeration (carrier, native operators, natural complexity coordinate, predicted niche, capability hypothesis,
weak regime, parent attacks, domain discriminator) and tested against the admission contract that IS present:
the domain criterion of `GMI_STRUCTURAL_DOMAINS_KINGDOMS_V1.md` section 2, the domain-novelty criterion of
section 14, and the executable method of `GMI_DOMAIN_CANDIDATES_DC1_DC9_V1.md` sections 0 and 2 (implement the
candidate carrier natively, implement the strongest existing-domain parent as a matched row on the same
ecology, compare answer signatures for exact developmental equality, compare description / serve / update
costs to find the crossover).

CARRIER (reconstructed N3): a SHEAF OF LOCAL SECTIONS over a declared cover. The sufficient cognitive state is
a family of local relations (local sections) on overlapping patches of a variable set, together with the
restriction maps to the overlaps. There is no global table and no program: global answers are obtained by
GLUING local sections along overlaps.

NATIVE OPERATORS: RESTRICT (restrict a local section to an overlap), GLUE (compose two local sections that
agree on their overlap), CHECK (does a local section extend?), PROJECT (read a variable off a glued section).

NATURAL COMPLEXITY COORDINATE: the number of patches k = n - 1 at fixed overlap width 1 (equivalently the
chain length n), against the size d^n of the global assignment space that the cover factorizes.

ECOLOGY E_glue(n, d, rho): variables x_0..x_{n-1} over a domain of size d; cover P_i = {x_i, x_{i+1}} for
i = 0..n-2 with overlap {x_{i+1}} of width 1; one declared local relation R_i subset d x d per patch, drawn by
the declared LCG at density rho. The OBLIGATION is the one the carrier is for: given boundary values
(x_0 = a, x_{n-1} = b), decide whether a GLOBAL SECTION exists and return the canonical (lexicographically
least) one. Query family = all d^2 boundary pairs. Development shows only the d boundary pairs with b = 0, so
the evaluation set contains d^2 - d queries never seen in development: the obligation is compositional, not
memorizable.

ROWS (all charged exactly through Machine; the same queries, the same answers compared bit for bit):
  SHEAF        the candidate: local relations only; forward gluing pass, backward gluing pass, then PROJECT
               the lex-least global section. Serve is linear in the number of patches.
  TABLE_MAT    matched parent 1, D2 (constraint / table memory, K4.4-as-table): DENIED the gluing operator, so
               it materializes the global answer table by enumerating the whole d^n assignment space at init
               and answers by one store lookup. Its answers are provably identical to SHEAF's (both return the
               lex-least global section), so this row IS the bounded-reduction attack.
  PROG_SEARCH  matched parent 2, D4/D5 (program search with a verifier): the same local relations plus a
               declared depth-first program that searches assignments in lex order and verifies each edge.
               Lex-first DFS returns the lex-least solution, so its answers are also identical to SHEAF's.
  TABLE_SEEN   matched parent 3, D2 (plain exemplar memory): stores the dev queries and their answers, answers
               an unseen boundary pair by nearest seen key. The generalization control.
  SHEAF_NOGLUE negative twin: the candidate with its DISTINGUISHING OPERATOR REMOVED. Local sections are still
               held but never composed across an overlap: patch i contributes only the set of values that are
               allowed at x_{i+1} by SOME predecessor, so the restriction maps are dropped.

ACCOUNTING: exec/upd/ver/rev are exact charged Machine ops under the declared column (the REDUCED price, one op
per scalar/Boolean operation). `native_ops` / `native_compile_ops` count the same computation at the DECLARED
NATIVE price of one op per sheaf operation (GLUE / RESTRICT / PROJECT), one op per table lookup, one op per
enumerated candidate assignment, one op per search node. `desc_bits` is the information-theoretic description
of the served state; every formula is declared in the receipt.
"""
from __future__ import annotations

import itertools
import json
import math
import os
import sys

from . import bases
from .core import Machine, sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
THETA = 0.85
PROG_OPS = 12  # declared program length of the DFS verifier program (desc charged at basis.desc_per_op)


def lcg_bits(seed, n):
    """declared deterministic bit generator (32-bit LCG, Numerical Recipes constants; bit 16 per draw).

    Same generator as gmi_microscope.dc_vsa.lcg_bits, kept local so this microscope is self-contained."""
    x = (seed * 1103515245 + 12345) & 0xFFFFFFFF
    out = 0
    for i in range(n):
        x = (x * 1103515245 + 12345) & 0xFFFFFFFF
        out |= ((x >> 16) & 1) << i
    return out


def _lcg_stream(seed):
    x = (seed * 1103515245 + 12345) & 0xFFFFFFFF
    while True:
        x = (x * 1103515245 + 12345) & 0xFFFFFFFF
        yield (x >> 16) & 0xFFFF


# ------------------------------------------------------------------------------------------------- ecology
def relations(n, d, rho_num, rho_den, seed=41, tail=False):
    """the declared local sections: R[i][u][v] in {0,1} for patch i, drawn at density rho_num/rho_den.

    Every patch is forced to contain at least one allowed pair (a patch with an empty section makes every
    boundary pair infeasible and the cell degenerate).

    `tail` selects the DECLARED LATE-FAILURE REGIME, which is the regime the N3 capability hypothesis names as
    the candidate's niche: the FINAL patch is restricted to a single allowed pair, so a lex-first search with no
    lookahead must exhaust the whole prefix space before it can report that a boundary pair is infeasible, while
    the sheaf's backward restriction pass rules the same boundary out in one pass over the cover. The earlier
    patches keep the declared density."""
    g = _lcg_stream(seed)
    R = []
    for i in range(n - 1):
        M = [[0] * d for _ in range(d)]
        for u in range(d):
            for v in range(d):
                M[u][v] = int(next(g) % rho_den < rho_num)
        if not any(any(r) for r in M):
            M[0][0] = 1
        R.append(M)
    if tail:
        R[n - 2] = [[0] * d for _ in range(d)]
        R[n - 2][0][0] = 1
    return R


def oracle(n, d, R, a, b):
    """uncharged declared reference: the lex-least global section with the given boundary, or None."""
    for asg in itertools.product(range(d), repeat=n):
        if asg[0] != a or asg[n - 1] != b:
            continue
        if all(R[i][asg[i]][asg[i + 1]] for i in range(n - 1)):
            return asg
    return None


def ecology(n, d, rho_num, rho_den, seed=41, tail=False):
    R = relations(n, d, rho_num, rho_den, seed, tail)
    queries = [(a, b) for a in range(d) for b in range(d)]
    truth = {q: oracle(n, d, R, q[0], q[1]) for q in queries}
    dev = [q for q in queries if q[1] == 0]
    n_feasible = sum(1 for q in queries if truth[q] is not None)
    density = sum(sum(sum(r) for r in M) for M in R) / ((n - 1) * d * d)
    return {"n": n, "d": d, "rho": f"{rho_num}/{rho_den}", "tail": bool(tail), "R": R, "queries": queries, "eval": queries,
            "dev": dev, "truth": truth, "n_feasible": n_feasible, "n_queries": len(queries),
            "executed_relation_density": round(density, 4), "global_space": d ** n, "n_patches": n - 1}


# ------------------------------------------------------------------------------------------------- rows
class Row:
    row = "?"

    def __init__(self, eco):
        self.e = eco
        self.native_ops = 0          # declared native price, serve side
        self.native_compile_ops = 0  # declared native price, construction side

    def init(self, M):
        pass

    def observe(self, M, q, ans):
        pass

    def query(self, M, q):
        raise NotImplementedError

    def desc_bits(self):
        return 0


def _idx_bits(x):
    return max(1, math.ceil(math.log2(x))) if x > 1 else 1


class Sheaf(Row):
    """the candidate: RESTRICT / GLUE / CHECK / PROJECT over the local sections. No global object is stored."""
    row = "SHEAF"

    def init(self, M):
        self.R = self.e["R"]

    def _forward(self, M, a):
        """GLUE along the cover from the boundary: F_{i+1}[v] = OR_u (F_i[u] AND R_i[u][v])."""
        n, d = self.e["n"], self.e["d"]
        F = [[0] * d for _ in range(n)]
        F[0][a] = 1
        for i in range(n - 1):
            for v in range(d):
                acc = 0
                for u in range(d):
                    acc = M.op("OR", acc, M.op("AND", F[i][u], self.R[i][u][v]))
                F[i + 1][v] = acc
            self.native_ops += 1  # one GLUE at the declared native price
        return F

    def _backward(self, M, b):
        """the restriction maps run the other way: B_i[u] = OR_v (R_i[u][v] AND B_{i+1}[v])."""
        n, d = self.e["n"], self.e["d"]
        B = [[0] * d for _ in range(n)]
        B[n - 1][b] = 1
        for i in range(n - 2, -1, -1):
            for u in range(d):
                acc = 0
                for v in range(d):
                    acc = M.op("OR", acc, M.op("AND", self.R[i][u][v], B[i + 1][v]))
                B[i][u] = acc
            self.native_ops += 1  # one RESTRICT at the declared native price
        return B

    def query(self, M, q):
        n, d = self.e["n"], self.e["d"]
        a, b = q
        F = self._forward(M, a)
        B = self._backward(M, b)
        # CHECK: a global section exists iff the two glued sections agree somewhere at every position
        ok = 1
        for i in range(n):
            agree = 0
            for u in range(d):
                agree = M.op("OR", agree, M.op("AND", F[i][u], B[i][u]))
            ok = M.op("AND", ok, agree)
        self.native_ops += 1  # one CHECK
        if not ok:
            return None
        # PROJECT: greedy lex-least section; B guarantees completion, so greedy is exact
        out = [a]
        for i in range(n - 1):
            pick = -1
            for v in range(d):
                if M.op("AND", self.R[i][out[i]][v], B[i + 1][v]):
                    pick = v
                    break
            out.append(pick)
            self.native_ops += 1  # one PROJECT per position
        return tuple(out)

    def desc_bits(self):
        n, d = self.e["n"], self.e["d"]
        # (n-1) local sections of d*d bits, plus the cover: two variable indices per patch
        return (n - 1) * d * d + (n - 1) * 2 * _idx_bits(n)


class SheafNoGlue(Sheaf):
    """negative twin: the GLUE operator removed. Local sections are held but never composed across an overlap;
    patch i contributes only the set of values allowed at x_{i+1} by SOME predecessor (restriction maps dropped)."""
    row = "SHEAF_NOGLUE"

    def query(self, M, q):
        n, d = self.e["n"], self.e["d"]
        a, b = q
        allowed = [[0] * d for _ in range(n)]
        allowed[0][a] = 1
        for i in range(n - 1):
            for v in range(d):
                acc = 0
                for u in range(d):
                    acc = M.op("OR", acc, M.op("AND", 1, self.R[i][u][v]))  # ANY predecessor: no restriction
                allowed[i + 1][v] = acc
            self.native_ops += 1
        ok = 1
        for i in range(n):
            agree = 0
            for u in range(d):
                agree = M.op("OR", agree, allowed[i][u])
            ok = M.op("AND", ok, agree)
        self.native_ops += 1
        if not ok:
            return None
        out = [a]
        for i in range(n - 1):
            pick = -1
            for v in range(d):
                if M.op("AND", allowed[i + 1][v], 1):
                    pick = v
                    break
            out.append(pick)
            self.native_ops += 1
        return tuple(out)


class TableMat(Row):
    """matched parent 1 (D2 constraint / table memory). DENIED the gluing operator, so the only way it can own
    this obligation is to materialize the global answer table by enumerating the d^n assignment space."""
    row = "TABLE_MAT"

    def init(self, M):
        n, d = self.e["n"], self.e["d"]
        R = self.e["R"]
        M.declare_store("answers")
        best = {}
        # lex-order enumeration; the FIRST consistent assignment for a boundary pair is the lex-least one.
        # No early exit: the charged compile cost is exactly d^n * (n-1) AND activations, analytically predictable.
        for asg in itertools.product(range(d), repeat=n):
            ok = 1
            for i in range(n - 1):
                ok = M.op("AND", ok, R[i][asg[i]][asg[i + 1]])
            self.native_compile_ops += 1  # one CHECK per candidate assignment at the declared native price
            if ok:
                k = (asg[0], asg[n - 1])
                if k not in best:
                    best[k] = asg
        for a in range(d):
            for b in range(d):
                M.op("S_INSERT", "answers", (a, b), best.get((a, b)))
        self.n_entries = d * d

    def query(self, M, q):
        self.native_ops += 1  # one LOOKUP at the declared native price
        return M.op("S_LOOKUP", "answers", q)

    def desc_bits(self):
        n, d = self.e["n"], self.e["d"]
        # d^2 keys, each holding an existence bit plus an n-symbol assignment
        return d * d * (1 + n * _idx_bits(d))


class ProgSearch(Row):
    """matched parent 2 (D4/D5 program search + verifier): the same local sections plus a declared DFS program.
    Lex-first depth-first search returns the lex-least solution, so its answers equal SHEAF's exactly."""
    row = "PROG_SEARCH"

    def init(self, M):
        self.R = self.e["R"]
        M.declare_program(PROG_OPS)

    def query(self, M, q):
        n, d = self.e["n"], self.e["d"]
        a, b = q
        R = self.R
        stack = [(a,)]
        while stack:
            asg = stack.pop()
            self.native_ops += 1  # one EXTEND (search node) at the declared native price
            i = len(asg) - 1
            if i == n - 1:
                return asg
            dom = [b] if i == n - 2 else list(range(d))
            nxt = []
            for v in dom:
                if M.op("AND", R[i][asg[i]][v], 1):
                    nxt.append(asg + (v,))
            stack.extend(reversed(nxt))  # LIFO: reversed push keeps lex order on pop
        return None

    def desc_bits(self):
        n, d = self.e["n"], self.e["d"]
        return (n - 1) * d * d + (n - 1) * 2 * _idx_bits(n) + PROG_OPS


class TableSeen(Row):
    """matched parent 3 (D2 plain exemplar memory): stores the dev queries, answers an unseen boundary pair by
    nearest seen key. The generalization control."""
    row = "TABLE_SEEN"

    def init(self, M):
        self.mem = []
        M.declare_store("seen")

    def observe(self, M, q, ans):
        M.op("S_INSERT", "seen", q, ans)
        self.mem.append((q, ans))

    def query(self, M, q):
        self.native_ops += 1
        hit = M.op("S_LOOKUP", "seen", q)
        if hit is not None:
            return hit
        if not self.mem:
            return None
        best, bd = None, None
        for (k, v) in self.mem:
            dist = M.op("ADD", abs(k[0] - q[0]), abs(k[1] - q[1]))
            if bd is None or M.op("GT", bd, dist):
                bd, best = dist, v
        return best

    def desc_bits(self):
        n, d = self.e["n"], self.e["d"]
        return len(self.mem) * (2 * _idx_bits(d) + 1 + n * _idx_bits(d))


ROWS = {"SHEAF": Sheaf, "TABLE_MAT": TableMat, "PROG_SEARCH": ProgSearch, "TABLE_SEEN": TableSeen,
        "SHEAF_NOGLUE": SheafNoGlue}
CANDIDATE = "SHEAF"
PARENTS = ("TABLE_MAT", "PROG_SEARCH", "TABLE_SEEN")
TWIN = "SHEAF_NOGLUE"


def run(row, basis, eco, seed=0):
    M = Machine(basis, seed=seed)
    ref = ROWS[row](eco)
    M.phase("exec")
    ref.init(M)
    init = dict(M.L.c)
    for q in eco["dev"]:
        M.phase("upd")
        ref.observe(M, q, eco["truth"][q])
        M.end_event()
    learn = dict(M.L.c)
    M.phase("exec")
    correct = 0
    answers = []
    for q in eco["eval"]:
        a = ref.query(M, q)
        a = tuple(a) if a is not None else None
        answers.append([list(q), list(a) if a is not None else None])
        correct += int(a == eco["truth"][q])
    cap = round(correct / len(eco["eval"]), 4)
    R = dict(M.L.c)
    nq = len(eco["eval"])
    return {"row": row, "basis": basis.name, "capability": cap, "admissible": cap >= THETA, "R": R,
            "compile_ops": init["exec"], "learn_ops": learn["upd"],
            "exec_per_query": round((R["exec"] - learn["exec"]) / nq, 4),
            "native_ops": ref.native_ops, "native_compile_ops": ref.native_compile_ops,
            "native_per_query": round(ref.native_ops / nq, 4),
            "desc_bits": ref.desc_bits(), "n_queries": nq, "answer_signature": sha256_of(answers)}


CELLS = {
    "n4_d3_dense":  {"n": 4, "d": 3, "rho_num": 7, "rho_den": 10},
    "n6_d3_dense":  {"n": 6, "d": 3, "rho_num": 7, "rho_den": 10},
    "n8_d3_dense":  {"n": 8, "d": 3, "rho_num": 7, "rho_den": 10},
    "n10_d3_dense": {"n": 10, "d": 3, "rho_num": 7, "rho_den": 10},
    "n4_d3_sparse": {"n": 4, "d": 3, "rho_num": 4, "rho_den": 10},
    "n6_d3_sparse": {"n": 6, "d": 3, "rho_num": 4, "rho_den": 10},
    "n8_d3_sparse": {"n": 8, "d": 3, "rho_num": 4, "rho_den": 10},
    "n6_d4_dense":  {"n": 6, "d": 4, "rho_num": 7, "rho_den": 10},
    "n6_d3_late":   {"n": 6, "d": 3, "rho_num": 9, "rho_den": 10, "tail": True},
    "n8_d3_late":   {"n": 8, "d": 3, "rho_num": 9, "rho_den": 10, "tail": True},
    "n10_d3_late":  {"n": 10, "d": 3, "rho_num": 9, "rho_den": 10, "tail": True},
}
COLUMNS = ("B0_LOCAL_ADAPTIVE_TRANSDUCERS", "B0i_LOCAL_ADAPTIVE_TRANSDUCERS")


def _basis(col):
    return bases.INDEXED_VARIANTS[col] if col in bases.INDEXED_VARIANTS else bases.ALL[col]


def lifecycle(r, H, price):
    """desc + construction + H * serve, under the reduced (charged ops) or declared native price."""
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


def main(tag="V26_N3_SHEAF", seed=0, columns=COLUMNS):
    cells, ecos = {}, {}
    for cname, spec in CELLS.items():
        eco = ecology(spec["n"], spec["d"], spec["rho_num"], spec["rho_den"], tail=spec.get("tail", False))
        ecos[cname] = eco
        for rname in ROWS:
            for col in columns:
                cells[(cname, rname, col)] = run(rname, _basis(col), eco, seed)

    # --- the bounded-reduction attack: exact developmental equality of candidate and each matched parent
    equality = {}
    for cname in CELLS:
        for col in columns:
            cand = cells[(cname, CANDIDATE, col)]["answer_signature"]
            for p in PARENTS + (TWIN,):
                equality[f"{cname}|{col}|{CANDIDATE}_vs_{p}"] = cand == cells[(cname, p, col)]["answer_signature"]

    # --- DG-2: the reuse-horizon grid is CONSTRUCTED from the analytic crossovers, not truncated
    crossovers, grid = {}, {}
    for cname in CELLS:
        for col in columns:
            for price in ("reduced", "native"):
                adm = [r for r in ROWS if cells[(cname, r, col)]["admissible"]]
                pts = set(BASE_GRID)
                for i, r1 in enumerate(adm):
                    for r2 in adm[i + 1:]:
                        H = crossover(cells[(cname, r1, col)], cells[(cname, r2, col)], price)
                        crossovers[f"{cname}|{col}|{price}|{r1}_vs_{r2}"] = H
                        if H is not None:
                            for m in (0.5, 1.0, 2.0):
                                pts.add(max(0, int(math.floor(H * m)) if m < 1 else int(math.ceil(H * m)) + 1))
                grid[f"{cname}|{col}|{price}"] = sorted(p for p in pts if p >= 0)

    frontier = {}
    for cname in CELLS:
        for col in columns:
            for price in ("reduced", "native"):
                adm = [r for r in ROWS if cells[(cname, r, col)]["admissible"]]
                for H in grid[f"{cname}|{col}|{price}"]:
                    costs = {r: lifecycle(cells[(cname, r, col)], H, price) for r in adm}
                    frontier[f"{cname}|{col}|{price}|H={H}"] = (
                        sorted(r for r, c in costs.items() if c <= min(costs.values()) + 1e-9) if costs else [])

    receipt = {
        "schema": "StageDNN3SheafV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422],
        "revival_record": "RV-377-050", "run_tag": tag,
        "domain_candidate": "N3 relational-constraint / sheaf intelligence",
        "hypothesis_source_status": (
            "GMI_NOVEL_DOMAIN_HYPOTHESES_V1.md is NOT PRESENT on branch claude/gmi-d0-d1-research-dnbp8i "
            "(nor GMI_NEW_DOMAIN_HARDENING_PROGRAMME_V1.md, nor GMI_DOMAIN_DERIVATION_COMPLETENESS_V1.md). "
            "The N3 specification executed here is RECONSTRUCTED from the task directive's enumeration and "
            "tested against the admission contract that is present: kingdoms sections 2 and 14 and the "
            "DC1-DC9 method sections 0 and 2. Every reconstructed element is stated in `candidate_spec`."),
        "candidate_spec": {
            "carrier": "a sheaf of local sections over a declared cover: (n-1) local relations R_i subset d x d on "
                       "patches P_i = {x_i, x_{i+1}} with overlap {x_{i+1}} of width 1, plus the restriction maps",
            "native_operators": "RESTRICT (restrict a local section to an overlap), GLUE (compose sections agreeing "
                                "on their overlap), CHECK (does a local section extend), PROJECT (read a variable off "
                                "a glued section)",
            "natural_complexity_coordinate": "number of patches k = n - 1 at fixed overlap width 1, against the global "
                                             "assignment space d^n that the cover factorizes",
            "predicted_niche": "obligations whose global relation is exponential (d^n) but factorizes through a cover of "
                               "bounded overlap; queries ask for a global section consistent with a boundary",
            "capability_hypothesis": "exact global answers with a description linear in the number of patches "
                                     "((n-1)d^2 bits) and a serve cost linear in the number of patches, where a table "
                                     "parent must enumerate d^n and a search parent may backtrack exponentially",
            "weak_regime": "overlap width approaching n (the cover stops factorizing) and dense relations (where lex-first "
                           "search finds a solution immediately and gluing is pure overhead)",
            "parent_attacks": "D2 constraint/table memory (TABLE_MAT, materializing) and D4/D5 program search "
                              "(PROG_SEARCH, lazy), plus a plain exemplar control (TABLE_SEEN)",
            "domain_discriminator": "does gluing produce answers no bounded parent reproduces? Decided here by exact "
                                    "answer-signature equality against both matched parents",
        },
        "cells_spec": CELLS, "columns": list(columns), "theta": THETA, "rows": list(ROWS),
        "row_roles": {"candidate": CANDIDATE, "matched_parents": list(PARENTS), "negative_twin": TWIN},
        "generator": "LCG(1103515245, 12345), bit 16 per draw for relation seeds; relations seed 41; density rho = "
                     "rho_num/rho_den tested on the low 16 bits mod rho_den",
        "desc_bits_formulas": {
            "SHEAF": "(n-1)*d^2 + (n-1)*2*ceil(log2 n)",
            "SHEAF_NOGLUE": "(n-1)*d^2 + (n-1)*2*ceil(log2 n)",
            "TABLE_MAT": "d^2 * (1 + n*ceil(log2 d))",
            "PROG_SEARCH": "(n-1)*d^2 + (n-1)*2*ceil(log2 n) + PROG_OPS",
            "TABLE_SEEN": "|dev| * (2*ceil(log2 d) + 1 + n*ceil(log2 d))",
        },
        "native_price_vector": "one op per GLUE / RESTRICT / CHECK / PROJECT (sheaf); one op per table LOOKUP; one op "
                               "per enumerated candidate assignment (table construction); one op per search node "
                               "(program search). Declared, not measured.",
        "ecology_facts": {c: {k: ecos[c][k] for k in ("n", "d", "rho", "n_feasible", "n_queries", "tail",
                                                      "executed_relation_density", "global_space", "n_patches")}
                          for c in CELLS},
        "cells": {f"{c}|{r}|{col}": {k: v for k, v in dd.items() if k not in ("row", "basis")}
                  for (c, r, col), dd in cells.items()},
        "developmental_equality": equality,
        "crossovers": crossovers,
        "frontier_grid": grid,
        "frontier": frontier,
        "dg2_compliance": "the reuse-horizon grid of every (cell, column, price) is the union of the base grid "
                          "(1, 16, 128, 1024) with floor(H*/2), ceil(H*)+1 and ceil(2H*) of EVERY pairwise analytic "
                          "crossover among the admissible rows, so no frontier statement is made on a truncated grid",
        "claim_ceiling": "exact charged replay at scope; one declared relation family per cell; the reduction attack is "
                         "an exact answer-signature equality test against two matched existing-domain parents; native "
                         "prices are declared, not measured; no new domain is claimed",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_DN_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    c0 = columns[0]
    print("candidate == parent answers (col %s):" % c0)
    for cname in CELLS:
        print(" ", cname, {p: equality[f"{cname}|{c0}|SHEAF_vs_{p}"] for p in PARENTS + (TWIN,)})
    for cname in CELLS:
        print(cname, "cap", {r: cells[(cname, r, c0)]["capability"] for r in ROWS})
        print("   desc", {r: cells[(cname, r, c0)]["desc_bits"] for r in ROWS},
              "| compile", {r: cells[(cname, r, c0)]["compile_ops"] for r in ("SHEAF", "TABLE_MAT", "PROG_SEARCH")},
              "| exec/q", {r: cells[(cname, r, c0)]["exec_per_query"] for r in ("SHEAF", "TABLE_MAT", "PROG_SEARCH")})
        print("   H* SHEAF vs TABLE_MAT reduced", crossovers.get(f"{cname}|{c0}|reduced|SHEAF_vs_TABLE_MAT"),
              "native", crossovers.get(f"{cname}|{c0}|native|SHEAF_vs_TABLE_MAT"),
              "| grid", grid[f"{cname}|{c0}|reduced"][-3:])
    return receipt


if __name__ == "__main__":
    main(tag=sys.argv[1] if len(sys.argv) > 1 else "V26_N3_SHEAF")

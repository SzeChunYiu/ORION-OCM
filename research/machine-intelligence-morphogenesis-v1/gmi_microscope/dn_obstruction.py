"""N11 — invariant / obstruction carrier: exact microscope and bounded-reduction attack
(novel-domain hypothesis N11 "Invariant / Obstruction Intelligence"; method of
GMI_DOMAIN_CANDIDATES_DC1_DC9_V1.md sections 0 and 2; domain criterion
GMI_STRUCTURAL_DOMAINS_KINGDOMS_V1.md section 2, novelty criterion section 14;
records RV-377-053, companion of RV-377-044 / RV-377-045).

HYPOTHESIS SPEC AS EXECUTED HERE (reconstructed from the Track B brief; the upstream
GMI_NOVEL_DOMAIN_HYPOTHESES_V1.md is not present on this branch — see
GMI_DOMAIN_N8_N11_EXECUTED_V1.md section 0):

  carrier              a finite set of CERTIFIED INVARIANTS (annihilator / obstruction functionals)
                       h_1..h_d, each a linear functional on the instance space that every move of the
                       registered move set preserves, together with the move set's reachable image.
                       Sufficient cognitive state = the invariant basis, NOT the reachable set.
  native operators     DERIVE (compute a basis of the annihilator of the move set), EVALUATE
                       (apply an invariant to an instance), CERTIFY (an invariant mismatch is a PROOF
                       of unreachability — no search is performed or needed).
  complexity coord.    the corank d = m - rank(moves): the number of independent obstructions.
  predicted niche      obligations in which the INTERESTING instances are UNSATISFIABLE: a search
                       carrier must exhaust the whole move space to say "no", an invariant carrier
                       answers in d evaluations.
  capability hypothesis  exact decision of reachability, with serve cost independent of the search
                       space size 2^k.
  weak regime          large corank (d close to m): the invariant basis is then as large as the
                       reachable-set description and the carrier loses its description advantage.
  parent attacks       (D5) a program-search row that tests candidate move combinations one by one;
                       (D1) a dense-coefficient row that carries the row-echelon basis of the move
                       span and decides membership by reduction.
  domain discriminator does a bounded semantics-preserving reduction to D1/D5 exist, and is the
                       lifecycle burden of that reduction qualitatively (not constantly) different?

ECOLOGY E_obstruct(m, k, d): the instance space is GF(2)^m. A declared move set of k generators
spans a subspace of corank d (the generators are drawn inside the kernel of d declared hidden check
vectors, so rank = m - d). An instance is a difference delta = target XOR start; the obligation is the
DECISION "is the target reachable from the start under the moves?". Development streams the k moves
(as move events) and then n_dev LABELLED instances, so every row observes exactly the same events and
uses what its law can use. Evaluation asks n_eval instances NEVER seen in development, of which the
majority are UNSATISFIABLE (the interesting ones).

Rows (all charged exactly; identical instances, answers compared bit for bit):
  OBSTRUCT        the candidate: DERIVE the annihilator basis from the moves at the end of development,
                  then answer by d EVALUATE ops. Serve cost 2*d*m, independent of k.
  DENSE_RREF      the strongest D1 parent: carry the reduced row-echelon basis of the move span
                  (r = m - d dense coefficient rows) and decide by reduction. Its answers are provably
                  identical to OBSTRUCT's (over GF(2) the row space is exactly the annihilator of the
                  null space), so this row is the bounded-reduction attack: if it matches OBSTRUCT
                  everywhere at bounded overhead, N11 is REDUCED_TO_PARENT(D1).
  SEARCH_ENUM     the strongest D5 parent: store the k moves and test move combinations ONE BY ONE in
                  declared Gray-code order until the difference is produced; on an unsatisfiable
                  instance it must exhaust all 2^k combinations. Its exhaustion cost is MEASURED.
                  If a declared node budget is exceeded the row returns -1 ("no decision"), which
                  counts as incorrect - it is never credited with a lucky default.
  TABLE_SEEN      a D2 memory parent: exact-key table over the labelled development instances.
  OBSTRUCT_NOCERT negative twin: the candidate with DERIVE/CERTIFY removed - d functionals of the same
                  size drawn from the declared LCG instead of derived from the move set.

Accounting: exec/upd/ver/rev are exact charged Machine ops on the B0 column (the REDUCED price
vector, one op per bit operation). `native_ops` counts the same computation at the DECLARED NATIVE
price (one op per EVALUATE, one per echelon REDUCE, one per tested move combination, one per LOOKUP).
`desc_bits` is the information-theoretic description of the SERVED state, declared per row below.
"""
from __future__ import annotations

import json
import os
import sys

from . import bases
from .core import Machine, sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
THETA = 0.85
SEARCH_BUDGET = 1 << 16  # declared node budget for SEARCH_ENUM; exceeding it yields -1 (no decision)


def lcg_bits(seed, m):
    """declared deterministic bit generator (32-bit LCG, Numerical Recipes constants), one bit per draw.
    Same generator as dc_vsa.lcg_bits."""
    x = (seed * 1103515245 + 12345) & 0xFFFFFFFF
    out = 0
    for i in range(m):
        x = (x * 1103515245 + 12345) & 0xFFFFFFFF
        out |= ((x >> 16) & 1) << i
    return out


class Lcg:
    def __init__(self, seed): self.x = seed & 0xFFFFFFFF

    def nxt(self):
        self.x = (self.x * 1103515245 + 12345) & 0xFFFFFFFF
        return self.x >> 16


# ------------------------------------------------------------------ charged GF(2) primitives
def _xor_vec(M, a, b, m):
    out = 0
    for i in range(m):
        if M.op("XOR", (a >> i) & 1, (b >> i) & 1): out |= 1 << i
    return out


def _parity_and(M, a, b, m):
    """the charged EVALUATE op: parity of the bitwise AND (a linear functional applied to a vector)."""
    p = 0
    for i in range(m):
        p = M.op("XOR", p, M.op("AND", (a >> i) & 1, (b >> i) & 1))
    return p


def _eq_vec(M, a, b, m):
    r = 1
    for i in range(m):
        r = M.op("AND", r, M.op("EQ", (a >> i) & 1, (b >> i) & 1))
    return r


def _bit(M, v, i):
    return M.op("AND", (v >> i) & 1, 1)


def _reduce(M, v, basis, pivots, m):
    cur = v
    for p, b in zip(pivots, basis):
        if _bit(M, cur, p): cur = _xor_vec(M, cur, b, m)
    return cur


def _first_set(M, v, m):
    for i in range(m):
        if _bit(M, v, i): return i
    return -1


def _echelon(M, rows, m):
    basis, pivots = [], []
    for v in rows:
        cur = _reduce(M, v, basis, pivots, m)
        p = _first_set(M, cur, m)
        if p >= 0: basis.append(cur); pivots.append(p)
    return basis, pivots


def _back_reduce(M, basis, pivots, m):
    """full RREF: each pivot column appears only in its own row (charged)."""
    for i in range(len(basis) - 1, -1, -1):
        for j in range(i):
            if _bit(M, basis[j], pivots[i]): basis[j] = _xor_vec(M, basis[j], basis[i], m)
    return basis


def _nullspace(M, basis, pivots, m):
    """basis of {h : g . h = 0 for every g in the row space} from the full RREF (charged).
    In full RREF row_i[p_j] = delta_ij, so h_f = e_f + sum_i basis_i[f] e_{p_i} annihilates every row."""
    free = [c for c in range(m) if c not in pivots]
    ns = []
    for f in free:
        h = 1 << f
        for i, p in enumerate(pivots):
            if _bit(M, basis[i], f): h |= 1 << p
        ns.append(h)
    return ns


# ------------------------------------------------------------------ ecology
def ecology(m, k, d=2, n_dev=6, n_eval=8, n_unsat_eval=5, seed=17):
    """A declared move set of k moves whose span has EXACTLY corank d, independently of k.

    Construction: d hidden check functionals are declared; m - d independent moves are drawn inside
    their common kernel (rejection on rank), and the remaining k - (m - d) moves are declared XOR
    combinations of those (a REDUNDANT move set). Rank is therefore m - d and corank exactly d for
    every k, so the k-sweep varies the SEARCH SPACE SIZE 2^k alone and the invariant carrier's serve
    cost is held fixed by construction. Evaluation instances are unseen in development and the
    majority are UNSATISFIABLE (the interesting ones).
    """
    assert k >= m - d, (m, d, k)
    checks = [lcg_bits(4000 + i, m) for i in range(d)]
    # pivot bit i belongs to check i alone: check i = e_i + (its bits at index >= d)
    checks = [(1 << i) | (checks[i] & ~((1 << d) - 1)) for i in range(d)]

    def project(v):
        """force v into the common kernel of the checks by setting bit i from the bits at index >= d."""
        v &= ~((1 << d) - 1)
        for i in range(d):
            par = 0
            for b in range(d, m):
                if (checks[i] >> b) & 1 and (v >> b) & 1: par ^= 1
            v |= par << i
        return v

    g = Lcg(seed)

    def rand_vec():
        out = 0
        for i in range(m):
            out |= (g.nxt() & 1) << i
        return out

    # --- exact (uncharged) rank tracker: the ecology's ground truth
    span_basis, span_piv = [], []

    def add(v):
        cur = v
        for p, b in zip(span_piv, span_basis):
            if (cur >> p) & 1: cur ^= b
        if cur:
            span_basis.append(cur); span_piv.append((cur & -cur).bit_length() - 1)
            return True
        return False

    indep = []
    guard = 0
    while len(indep) < m - d and guard < 100000:
        guard += 1
        v = project(rand_vec())
        if v and add(v): indep.append(v)
    assert len(indep) == m - d, (m, d, len(indep))
    moves = list(indep)
    while len(moves) < k:                       # declared redundant moves: XOR of a random subset
        acc = 0
        for v in indep:
            if g.nxt() & 1: acc ^= v
        if acc: moves.append(acc)
    rank = len(span_basis)

    def reachable(delta):
        cur = delta
        for p, b in zip(span_piv, span_basis):
            if (cur >> p) & 1: cur ^= b
        return int(cur == 0)

    def sat_instance():
        acc = 0
        for mv in moves:
            if g.nxt() & 1: acc ^= mv
        return acc

    def unsat_instance():
        while True:
            v = rand_vec()
            if not reachable(v): return v

    seen = set()

    def fresh(fn):
        for _ in range(100000):
            v = fn()
            if v not in seen: seen.add(v); return v
        raise RuntimeError("ecology exhausted")

    dev = []
    for i in range(n_dev):
        v = fresh(sat_instance if i % 2 == 0 else unsat_instance)
        dev.append((v, reachable(v)))
    ev = []
    for i in range(n_eval):
        v = fresh(unsat_instance if i < n_unsat_eval else sat_instance)
        ev.append((v, reachable(v)))
    return {"m": m, "k": k, "d": d, "rank": rank, "corank": m - rank, "moves": moves, "checks": checks,
            "n_independent_moves": len(indep), "n_redundant_moves": k - len(indep),
            "dev": dev, "eval": ev, "n_unsat_eval": sum(1 for _, a in ev if a == 0)}


# ------------------------------------------------------------------ rows
class Row:
    row = "?"

    def __init__(self, eco): self.e = eco; self.native_ops = 0; self.budget_exhausted = 0

    def init(self, M): pass

    def see_move(self, M, mv): pass

    def see_instance(self, M, delta, label): pass

    def compile(self, M): pass

    def query(self, M, delta): raise NotImplementedError

    def desc_bits(self): return 0


class Obstruct(Row):
    """the candidate: DERIVE a certified annihilator basis, then CERTIFY unreachability by EVALUATE."""
    row = "OBSTRUCT"

    def init(self, M): self.moves = []; self.H = []

    def see_move(self, M, mv): self.moves.append(mv)

    def compile(self, M):
        m = self.e["m"]
        basis, piv = _echelon(M, self.moves, m)
        basis = _back_reduce(M, basis, piv, m)
        self.H = _nullspace(M, basis, piv, m)
        self.derived_corank = len(self.H)

    def query(self, M, delta):
        m = self.e["m"]; ok = 1
        for h in self.H:
            ok = M.op("AND", ok, M.op("NOT", _parity_and(M, h, delta, m)))
            self.native_ops += 1  # one EVALUATE at the declared native price
        return ok

    def desc_bits(self): return len(self.H) * self.e["m"]


class ObstructNoCert(Obstruct):
    """negative twin: d functionals of the same size that are NOT derived from the move set."""
    row = "OBSTRUCT_NOCERT"

    def compile(self, M):
        self.H = [lcg_bits(9100 + i, self.e["m"]) for i in range(self.e["corank"])]
        self.derived_corank = len(self.H)


class DenseRref(Row):
    """the strongest D1 parent: the dense row-echelon coefficient basis of the move span."""
    row = "DENSE_RREF"

    def init(self, M): self.moves = []; self.basis = []; self.piv = []

    def see_move(self, M, mv): self.moves.append(mv)

    def compile(self, M):
        m = self.e["m"]
        self.basis, self.piv = _echelon(M, self.moves, m)
        self.basis = _back_reduce(M, self.basis, self.piv, m)

    def query(self, M, delta):
        m = self.e["m"]
        cur = _reduce(M, delta, self.basis, self.piv, m)
        self.native_ops += len(self.basis)  # one REDUCE per coefficient row at the declared native price
        return int(_eq_vec(M, cur, 0, m))

    def desc_bits(self): return len(self.basis) * self.e["m"]


class SearchEnum(Row):
    """the strongest D5 parent: test move combinations ONE BY ONE (Gray-code order) until the
    difference is produced; an unsatisfiable instance forces exhaustion of all 2^k combinations."""
    row = "SEARCH_ENUM"

    def init(self, M): self.moves = []

    def see_move(self, M, mv): self.moves.append(mv)

    def query(self, M, delta):
        m = self.e["m"]; k = len(self.moves); acc = 0
        if _eq_vec(M, acc, delta, m): self.native_ops += 1; return 1
        self.native_ops += 1
        total = 1 << k
        for i in range(1, total):
            if i > SEARCH_BUDGET: self.budget_exhausted = 1; return -1
            j = (i & -i).bit_length() - 1  # Gray-code: flip move j
            acc = _xor_vec(M, acc, self.moves[j], m)
            self.native_ops += 1  # one tested combination at the declared native price
            if _eq_vec(M, acc, delta, m): return 1
        return 0

    def desc_bits(self): return len(self.moves) * self.e["m"]


class TableSeen(Row):
    """D2 memory parent: exact-key table over the labelled development instances."""
    row = "TABLE_SEEN"

    def init(self, M): self.mem = {}

    def see_instance(self, M, delta, label): self.mem[delta] = label

    def query(self, M, delta):
        self.native_ops += 1
        for key, lab in self.mem.items():
            if _eq_vec(M, key, delta, self.e["m"]): return lab
        return -1  # no stored key: no decision (counts as incorrect; never a lucky default)

    def desc_bits(self): return len(self.mem) * (self.e["m"] + 1)


ROWS = {"OBSTRUCT": Obstruct, "DENSE_RREF": DenseRref, "SEARCH_ENUM": SearchEnum,
        "TABLE_SEEN": TableSeen, "OBSTRUCT_NOCERT": ObstructNoCert}


def run(row, basis, eco, seed=0):
    M = Machine(basis, seed=seed); ref = ROWS[row](eco)
    M.phase("exec"); ref.init(M)
    for mv in eco["moves"]:
        M.phase("upd"); ref.see_move(M, mv); M.end_event()
    for delta, lab in eco["dev"]:
        M.phase("upd"); ref.see_instance(M, delta, lab); M.end_event()
    M.phase("upd"); ref.compile(M); M.end_event()
    after_dev = dict(M.L.c)
    M.phase("exec"); correct = 0; answers = []
    unsat_exec = 0; n_unsat = 0
    for idx, (delta, lab) in enumerate(eco["eval"]):
        before = M.L.c["exec"]
        a = ref.query(M, delta)
        answers.append((idx, a)); correct += int(a == lab)
        if lab == 0: unsat_exec += M.L.c["exec"] - before; n_unsat += 1
    n = len(eco["eval"]); cap = round(correct / n, 4)
    R = dict(M.L.c)
    return {"row": row, "basis": basis.name, "capability": cap, "admissible": cap >= THETA, "R": R,
            "compile_ops": after_dev["upd"], "exec_per_query": round((R["exec"] - after_dev["exec"]) / n, 4),
            "exec_per_unsat_query": round(unsat_exec / n_unsat, 4) if n_unsat else 0.0,
            "native_ops": ref.native_ops, "native_per_query": round(ref.native_ops / n, 4),
            "desc_bits": ref.desc_bits(), "n_queries": n, "budget_exhausted": ref.budget_exhausted,
            "answer_signature": sha256_of(answers)}


# k-sweep: the search-space growth law at fixed instance width. m-sweep: the polynomial separation
# against the dense coefficient parent at fixed corank.
CELLS = {
    # k-sweep: search-space growth law at fixed instance width m = 10 and fixed corank d = 2
    "m10_d2_k8":  {"m": 10, "k": 8,  "d": 2, "sweep": "k"},
    "m10_d2_k10": {"m": 10, "k": 10, "d": 2, "sweep": "k"},
    "m10_d2_k12": {"m": 10, "k": 12, "d": 2, "sweep": "k"},
    "m10_d2_k14": {"m": 10, "k": 14, "d": 2, "sweep": "k"},
    "m10_d2_k16": {"m": 10, "k": 16, "d": 2, "sweep": "k"},
    # m-sweep: separation against the dense coefficient parent at fixed corank d = 2
    "m16_d2_k16": {"m": 16, "k": 16, "d": 2, "sweep": "m"},
    "m24_d2_k24": {"m": 24, "k": 24, "d": 2, "sweep": "m"},
    "m32_d2_k32": {"m": 32, "k": 32, "d": 2, "sweep": "m"},
    "m48_d2_k48": {"m": 48, "k": 48, "d": 2, "sweep": "m"},
    # declared weak regime of the hypothesis: corank = m/2, where the invariant basis is as large
    # as the coefficient basis and the carrier's description advantage is predicted to vanish
    "m32_d16_k32": {"m": 32, "k": 32, "d": 16, "sweep": "weak"},
}


def lifecycle(r, H, native=False):
    """desc + H * serve + compile, under the reduced (charged ops) or declared native price."""
    return r["desc_bits"] + H * (r["native_per_query"] if native else r["exec_per_query"]) + (0 if native else r["compile_ops"])


def crossovers(cells_for_cell, native=False):
    """analytic reuse-horizon crossovers H* between every pair of ADMISSIBLE rows (DG-2:
    the frontier grid must extend past every finite positive crossover)."""
    out = {}
    names = [r for r in cells_for_cell if cells_for_cell[r]["admissible"]]
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            ra, rb = cells_for_cell[a], cells_for_cell[b]
            sa = ra["native_per_query"] if native else ra["exec_per_query"]
            sb = rb["native_per_query"] if native else rb["exec_per_query"]
            ca = ra["desc_bits"] + (0 if native else ra["compile_ops"])
            cb = rb["desc_bits"] + (0 if native else rb["compile_ops"])
            if sa == sb:
                out[f"{a}|{b}"] = None  # parallel: no crossover
                continue
            h = (cb - ca) / (sa - sb)
            out[f"{a}|{b}"] = round(h, 4) if h > 0 else None
    return out


def grid_for(cx_list, base=(1, 16, 128, 1024)):
    """declared grid rule (DG-2): the base grid, every finite positive crossover bracketed
    (floor and ceil+1), and twice the largest crossover."""
    import math
    hs = set(base)
    finite = [h for cx in cx_list for h in cx.values() if h is not None and h > 0]
    for h in finite:
        hs.add(max(1, int(math.floor(h)))); hs.add(int(math.ceil(h)) + 1)
    if finite: hs.add(int(math.ceil(2 * max(finite))))
    return sorted(hs)


def main(tag="V29_N11_OBSTRUCTION", seed=0, cells_subset=None):
    col = "B0_LOCAL_ADAPTIVE_TRANSDUCERS"; b = bases.ALL[col]
    specs = {c: s for c, s in CELLS.items() if cells_subset is None or c in cells_subset}
    cells = {}; ecos = {}
    for cname, spec in specs.items():
        eco = ecology(spec["m"], spec["k"], spec["d"]); ecos[cname] = eco
        for rname in ROWS:
            cells[(cname, rname)] = run(rname, b, eco, seed)

    # exact response equality between the candidate and each parent (the bounded-reduction attack)
    equality = {}
    for cname in specs:
        for parent in ("DENSE_RREF", "SEARCH_ENUM", "TABLE_SEEN"):
            equality[f"{cname}|OBSTRUCT=={parent}"] = cells[(cname, "OBSTRUCT")]["answer_signature"] == cells[(cname, parent)]["answer_signature"]

    # measured growth law over the k-sweep: the parent's exhaustion cost is MEASURED, not assumed
    ks = [c for c in specs if specs[c]["sweep"] == "k"]
    growth = {}
    for cname in sorted(ks, key=lambda c: specs[c]["k"]):
        o = cells[(cname, "OBSTRUCT")]; s = cells[(cname, "SEARCH_ENUM")]; dn = cells[(cname, "DENSE_RREF")]
        growth[cname] = {"k": specs[cname]["k"], "search_space_2^k": 1 << specs[cname]["k"],
                         "obstruct_exec_per_unsat_query": o["exec_per_unsat_query"],
                         "search_exec_per_unsat_query": s["exec_per_unsat_query"],
                         "dense_exec_per_unsat_query": dn["exec_per_unsat_query"],
                         "search_over_obstruct": round(s["exec_per_unsat_query"] / o["exec_per_unsat_query"], 4) if o["exec_per_unsat_query"] else None,
                         "search_native_per_query": s["native_per_query"], "obstruct_native_per_query": o["native_per_query"]}
    ms = [c for c in specs if specs[c]["sweep"] == "m"]
    mgrowth = {}
    for cname in sorted(ms, key=lambda c: specs[c]["m"]) :
        o = cells[(cname, "OBSTRUCT")]; dn = cells[(cname, "DENSE_RREF")]
        mgrowth[cname] = {"m": specs[cname]["m"], "rank": ecos[cname]["rank"], "corank": ecos[cname]["corank"],
                          "obstruct_exec_per_query": o["exec_per_query"], "dense_exec_per_query": dn["exec_per_query"],
                          "dense_over_obstruct_exec": round(dn["exec_per_query"] / o["exec_per_query"], 4),
                          "obstruct_desc_bits": o["desc_bits"], "dense_desc_bits": dn["desc_bits"],
                          "dense_over_obstruct_desc": round(dn["desc_bits"] / o["desc_bits"], 4)}

    frontier = {}; cx_all = {}
    for cname in specs:
        per = {r: cells[(cname, r)] for r in ROWS}
        for price in ("reduced", "native"):
            cx = crossovers(per, native=(price == "native")); cx_all[f"{cname}|{price}"] = cx
            grid = grid_for([cx])
            for H in grid:
                adm = [r for r in ROWS if per[r]["admissible"]]
                costs = {r: lifecycle(per[r], H, native=(price == "native")) for r in adm}
                frontier[f"{cname}|{price}|H={H}"] = sorted(r for r, c in costs.items() if c <= min(costs.values()) + 1e-9) if costs else []

    receipt = {
        "schema": "StageDN29N11ObstructionV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422],
        "revival_record": "RV-377-053", "run_tag": tag,
        "domain_candidate": "N11 invariant / obstruction intelligence",
        "hypothesis_source": "reconstructed from the Track B brief; GMI_NOVEL_DOMAIN_HYPOTHESES_V1.md is absent from this branch (see GMI_DOMAIN_N8_N11_EXECUTED_V1.md section 0)",
        "column": col, "theta": THETA, "search_budget": SEARCH_BUDGET,
        "cells_spec": specs, "rows": list(ROWS),
        "ecology_facts": {c: {"m": ecos[c]["m"], "k": ecos[c]["k"], "declared_corank": ecos[c]["d"], "measured_rank": ecos[c]["rank"],
                              "measured_corank": ecos[c]["corank"], "n_independent_moves": ecos[c]["n_independent_moves"],
                              "n_redundant_moves": ecos[c]["n_redundant_moves"], "n_eval": len(ecos[c]["eval"]),
                              "n_unsat_eval": ecos[c]["n_unsat_eval"], "n_dev_instances": len(ecos[c]["dev"])} for c in specs},
        "description_semantics": {
            "OBSTRUCT": "d_measured * m bits: the derived certified annihilator basis",
            "DENSE_RREF": "rank * m bits: the reduced row-echelon coefficient basis of the move span",
            "SEARCH_ENUM": "k * m bits: the raw move list",
            "TABLE_SEEN": "n_dev * (m + 1) bits: key plus label per stored development instance",
            "OBSTRUCT_NOCERT": "d_measured * m bits: the same carrier size, functionals not derived from the moves"},
        "native_price_vector": "one op per EVALUATE (OBSTRUCT), per echelon REDUCE row (DENSE_RREF), per tested move combination (SEARCH_ENUM), per LOOKUP (TABLE_SEEN); declared, not measured",
        "cells": {f"{c}|{r}": {k: v for k, v in d.items() if k not in ("row", "basis")} for (c, r), d in cells.items()},
        "obstruct_equals_parent_answers": equality,
        "growth_law_k_sweep": growth, "growth_law_m_sweep": mgrowth,
        "frontier_crossovers": cx_all, "frontier": frontier,
        "claim_ceiling": "exact charged replay at scope on one declared instance family per cell; the reduction attack is an exact answer-signature test against the dense-coefficient parent; the search parent's exhaustion cost is measured, not assumed; native prices are declared, not measured; no new domain is claimed",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_DN_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    print("OBSTRUCT == DENSE_RREF answers everywhere:", all(v for k, v in equality.items() if "DENSE_RREF" in k))
    for cname in specs:
        print(cname, {r: cells[(cname, r)]["capability"] for r in ROWS},
              "| desc", {r: cells[(cname, r)]["desc_bits"] for r in ("OBSTRUCT", "DENSE_RREF", "SEARCH_ENUM")},
              "| exec/unsat-q", {r: cells[(cname, r)]["exec_per_unsat_query"] for r in ("OBSTRUCT", "DENSE_RREF", "SEARCH_ENUM")})
    return receipt


if __name__ == "__main__":
    main(tag=sys.argv[1] if len(sys.argv) > 1 else "V29_N11_OBSTRUCTION")

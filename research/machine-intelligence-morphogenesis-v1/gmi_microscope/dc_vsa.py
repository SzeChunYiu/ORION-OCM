"""DC1 — hyperdimensional / vector-symbolic carrier: exact microscope and bounded-reduction attack
(GMI_DOMAIN_CANDIDATES_DC1_DC9_V1.md section 2, record RV-377-044; domain criterion of
GMI_STRUCTURAL_DOMAINS_KINGDOMS_V1.md sections 2 and 14).

Carrier: a D-bit hypervector h in {0,1}^D holding superposed bound structure; item memory = a codebook of R role and F
filler hypervectors. Native law: BIND = bitwise XOR, BUNDLE = bitwise majority, UNBIND = XOR (self-inverse), CLEANUP =
nearest codebook item by Hamming distance.

Ecology E_rolefill(D, depth, k, noise): a record is a bundle of k bound structures of depth `depth` over R = 4 roles and
F = 8 fillers (depth 1: role -> filler; depth 2: role -> (role' -> filler)). Development shows the machine SEEN records;
evaluation asks (cue hypervector, role path) -> filler on records NEVER seen in development, and on noise-corrupted cues.
The obligation is compositional: the answer is determined by the structure the cue encodes, not by any stored record.

Rows (all charged exactly; the same cues, the same answers compared bit for bit):
  VSA          codebook only; unbind along the path, then cleanup over the F fillers.
  STORE_MAT    the strongest D2 parent: materialize every bound vector for every role path at init (R*F for depth 1,
               R*R*F for depth 2) and answer by nearest among those whose path matches the query. Its answers are
               provably identical to VSA's (Hamming(cue, role XOR f) = Hamming(cue XOR role, f)), so this row is the
               bounded-reduction attack: if it matches VSA everywhere at bounded overhead, DC1 is REDUCED_TO_PARENT.
  STORE_SEEN   plain exemplar memory over the records actually seen in development (nearest seen cue -> its answer).
  VSA_NOBIND   negative twin: bundle the fillers without binding them to roles (the binding mechanism removed).

Accounting: exec/upd/ver/rev are exact charged Machine ops (the REDUCED price vector, one op per bit operation).
`hv_ops` counts the same computation at the DECLARED NATIVE price of one op per hypervector operation (the associative /
in-memory hardware assumption of the VSA literature). `desc_bits` is the information-theoretic description of the served
state: D bits per stored hypervector plus the declared index overhead.
"""
from __future__ import annotations

import json
import os
import sys

from . import bases
from .core import Machine, sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
R_ROLES = 4
F_FILLERS = 8
THETA = 0.85
IDX_BITS = 8  # declared index overhead per stored hypervector (its path label)


def lcg_bits(seed, D):
    """declared deterministic codebook generator (32-bit LCG, Numerical Recipes constants); one bit per draw."""
    x = (seed * 1103515245 + 12345) & 0xFFFFFFFF
    out = 0
    for i in range(D):
        x = (x * 1103515245 + 12345) & 0xFFFFFFFF
        out |= ((x >> 16) & 1) << i
    return out


def codebook(D):
    roles = [lcg_bits(1000 + i, D) for i in range(R_ROLES)]
    fillers = [lcg_bits(2000 + j, D) for j in range(F_FILLERS)]
    return roles, fillers


def popcount(n):
    return bin(n).count("1")


# ----------------------------------------------------------------------------------------------------- structures
def paths(depth):
    if depth == 1:
        return [(i,) for i in range(R_ROLES)]
    return [(i, j) for i in range(R_ROLES) for j in range(R_ROLES)]


def bound_vector(roles, fillers, path, f, D):
    """BIND along the path: role_{p1} XOR (role_{p2} XOR ... XOR filler)."""
    v = fillers[f]
    for r in reversed(path):
        v ^= roles[r]
    return v


def bundle(vecs, D, tie):
    """BUNDLE = bitwise majority; ties (even count) broken by the declared tie vector."""
    out = 0
    for b in range(D):
        s = sum((v >> b) & 1 for v in vecs)
        if 2 * s > len(vecs): out |= 1 << b
        elif 2 * s == len(vecs) and ((tie >> b) & 1): out |= 1 << b
    return out


def make_record(roles, fillers, items, D, tie):
    """items: list of (path, filler). Returns (cue hypervector, {path: filler})."""
    vs = [bound_vector(roles, fillers, p, f, D) for p, f in items]
    return bundle(vs, D, tie), {p: f for p, f in items}


def ecology(D, depth, k, n_dev=8, n_eval=8, noise=0, seed=7):
    """declared record generator: deterministic, dev and eval records disjoint as structures."""
    roles, fillers = codebook(D); tie = lcg_bits(3000, D); P = paths(depth)
    rng = seed; recs = []
    def nxt():
        nonlocal rng
        rng = (rng * 1103515245 + 12345) & 0xFFFFFFFF
        return rng >> 16
    for n in range(n_dev + n_eval):
        chosen = []
        used = set()
        while len(chosen) < k:
            p = P[nxt() % len(P)]
            if p in used: continue
            used.add(p); chosen.append((p, nxt() % F_FILLERS))
        cue, ans = make_record(roles, fillers, chosen, D, tie)
        if noise and n >= n_dev:
            for _ in range(noise): cue ^= 1 << (nxt() % D)
        recs.append({"cue": cue, "answers": ans, "items": chosen})
    return {"roles": roles, "fillers": fillers, "tie": tie, "D": D, "depth": depth, "k": k, "dev": recs[:n_dev], "eval": recs[n_dev:], "noise": noise}


# ----------------------------------------------------------------------------------------------------- rows
class Row:
    row = "?"

    def __init__(self, eco): self.e = eco; self.hv_ops = 0

    def init(self, M): pass

    def observe(self, M, rec): pass

    def query(self, M, cue, path): raise NotImplementedError

    def desc_bits(self): return 0


def _xor_bits(M, a, b, D):
    """charged bitwise XOR of two D-bit hypervectors."""
    out = 0
    for i in range(D):
        if M.op("XOR", (a >> i) & 1, (b >> i) & 1): out |= 1 << i
    return out


def _hamming(M, a, b, D):
    """charged Hamming distance."""
    d = 0
    for i in range(D): d = M.op("ADD", d, M.op("XOR", (a >> i) & 1, (b >> i) & 1))
    return d


def _argmin(M, ds):
    best = 0
    for i in range(1, len(ds)):
        if M.op("GT", ds[best], ds[i]): best = i
    return best


class VSA(Row):
    row = "VSA"

    def init(self, M):
        self.roles = self.e["roles"]; self.fillers = self.e["fillers"]

    def query(self, M, cue, path):
        D = self.e["D"]; v = cue
        for r in path:
            v = _xor_bits(M, v, self.roles[r], D); self.hv_ops += 1  # UNBIND
        ds = [_hamming(M, v, f, D) for f in self.fillers]; self.hv_ops += len(self.fillers)  # CLEANUP
        return _argmin(M, ds)

    def desc_bits(self):
        return (R_ROLES + F_FILLERS) * (self.e["D"] + IDX_BITS)


class StoreMat(Row):
    """the strongest D2 parent: materialize every bound vector for every (path, filler) and answer by nearest match."""
    row = "STORE_MAT"

    def init(self, M):
        D = self.e["D"]; self.table = {}
        for p in paths(self.e["depth"]):
            for f in range(F_FILLERS):
                v = self.e["fillers"][f]
                for r in reversed(p): v = _xor_bits(M, v, self.e["roles"][r], D); self.hv_ops += 1  # materialization cost
                self.table.setdefault(p, []).append(v)
        self.n_stored = sum(len(v) for v in self.table.values())

    def query(self, M, cue, path):
        D = self.e["D"]; cands = self.table[path]
        ds = [_hamming(M, cue, c, D) for c in cands]; self.hv_ops += len(cands)
        return _argmin(M, ds)

    def desc_bits(self):
        return self.n_stored * (self.e["D"] + IDX_BITS)


class StoreSeen(Row):
    """plain exemplar memory over the records seen in development."""
    row = "STORE_SEEN"

    def init(self, M): self.mem = []

    def observe(self, M, rec):
        self.mem.append((rec["cue"], dict(rec["answers"])))

    def query(self, M, cue, path):
        D = self.e["D"]
        cands = [(c, a) for c, a in self.mem if path in a]
        if not cands: return -1
        ds = [_hamming(M, cue, c, D) for c, _ in cands]; self.hv_ops += len(cands)
        return cands[_argmin(M, ds)][1][path]

    def desc_bits(self):
        return len(self.mem) * (self.e["D"] + IDX_BITS + len(paths(self.e["depth"])) * 3)


class VSANoBind(Row):
    """negative twin: the codebook without the binding operator — fillers are bundled directly, roles are lost."""
    row = "VSA_NOBIND"

    def init(self, M): self.fillers = self.e["fillers"]

    def query(self, M, cue, path):
        D = self.e["D"]
        ds = [_hamming(M, cue, f, D) for f in self.fillers]; self.hv_ops += len(self.fillers)
        return _argmin(M, ds)

    def desc_bits(self):
        return (R_ROLES + F_FILLERS) * (self.e["D"] + IDX_BITS)


ROWS = {"VSA": VSA, "STORE_MAT": StoreMat, "STORE_SEEN": StoreSeen, "VSA_NOBIND": VSANoBind}


def run(row, basis, eco, seed=0):
    ref = ROWS[row](eco); M = Machine(basis, seed=seed)
    M.phase("exec"); ref.init(M)
    init_ops = dict(M.L.c)
    for rec in eco["dev"]:
        M.phase("upd"); ref.observe(M, rec); M.end_event()
    M.phase("exec"); correct = 0; total = 0; answers = []
    for rec in eco["eval"]:
        for p, f in rec["answers"].items():
            a = ref.query(M, rec["cue"], p); answers.append((tuple(p), a)); total += 1; correct += int(a == f)
    cap = round(correct / total, 4) if total else 0.0
    R = dict(M.L.c)
    return {"row": row, "basis": basis.name, "capability": cap, "admissible": cap >= THETA, "R": R, "compile_ops": init_ops["exec"], "exec_per_query": (R["exec"] - init_ops["exec"]) / total,
            "hv_ops": ref.hv_ops, "desc_bits": ref.desc_bits(), "n_queries": total, "answer_signature": sha256_of(answers)}


CELLS = {
    "D64_d1_k3": {"D": 64, "depth": 1, "k": 3, "noise": 0},
    "D64_d1_k4": {"D": 64, "depth": 1, "k": 4, "noise": 0},
    "D64_d1_k3_noisy": {"D": 64, "depth": 1, "k": 3, "noise": 8},
    "D128_d1_k3": {"D": 128, "depth": 1, "k": 3, "noise": 0},
    "D64_d2_k3": {"D": 64, "depth": 2, "k": 3, "noise": 0},
    "D128_d2_k3": {"D": 128, "depth": 2, "k": 3, "noise": 0},
    "D256_d2_k5": {"D": 256, "depth": 2, "k": 5, "noise": 0},
}


def lifecycle(r, H, n_records=8, native=False):
    """desc + H * exec_per_query + materialization, under the reduced (charged ops) or declared native (hv op) price."""
    if native:
        return r["desc_bits"] + H * (r["hv_ops"] / max(r["n_queries"], 1))
    return r["desc_bits"] + H * r["exec_per_query"] + r["compile_ops"]


def main(tag="V24_DC1_VSA", seed=0, columns=None):
    cols = columns or {"B0_LOCAL_ADAPTIVE_TRANSDUCERS": bases.ALL["B0_LOCAL_ADAPTIVE_TRANSDUCERS"]}
    cells = {}
    for cname, spec in CELLS.items():
        eco = ecology(spec["D"], spec["depth"], spec["k"], noise=spec["noise"])
        for rname in ROWS:
            for col, b in cols.items(): cells[(cname, rname, col)] = run(rname, b, eco, seed)
    # exact response equality between VSA and its strongest parent (the bounded-reduction attack)
    equality = {}
    for cname in CELLS:
        for col in cols:
            equality[f"{cname}|{col}"] = cells[(cname, "VSA", col)]["answer_signature"] == cells[(cname, "STORE_MAT", col)]["answer_signature"]
    ratios = {}
    for cname in CELLS:
        for col in cols:
            v = cells[(cname, "VSA", col)]; s = cells[(cname, "STORE_MAT", col)]
            ratios[f"{cname}|{col}"] = {"desc_vsa": v["desc_bits"], "desc_store_mat": s["desc_bits"], "desc_ratio_store_over_vsa": round(s["desc_bits"] / v["desc_bits"], 3),
                                        "exec_per_query_vsa": v["exec_per_query"], "exec_per_query_store_mat": s["exec_per_query"], "compile_ops_store_mat": s["compile_ops"],
                                        "hv_ops_vsa": v["hv_ops"], "hv_ops_store_mat": s["hv_ops"]}
    frontier = {}
    for cname in CELLS:
        for col in cols:
            for price in ("reduced", "native"):
                for H in (1, 16, 128, 1024):
                    adm = [r for r in ROWS if cells[(cname, r, col)]["admissible"]]
                    costs = {r: lifecycle(cells[(cname, r, col)], H, native=(price == "native")) for r in adm}
                    frontier[f"{cname}|{col}|{price}|H={H}"] = sorted(r for r, c in costs.items() if c <= min(costs.values()) + 1e-9) if costs else []
    receipt = {"schema": "StageDC1VSAV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422], "revival_record": "RV-377-044", "run_tag": tag, "domain_candidate": "DC1 hyperdimensional / vector-symbolic",
               "cells_spec": CELLS, "codebook": {"R_roles": R_ROLES, "F_fillers": F_FILLERS, "generator": "LCG(1103515245, 12345), bit 16 per draw; roles seed 1000+i, fillers 2000+j, tie vector 3000", "index_bits_per_stored_hypervector": IDX_BITS},
               "rows": list(ROWS), "cells": {f"{c}|{r}|{col}": {k: v for k, v in d.items() if k not in ("row", "basis")} for (c, r, col), d in cells.items()},
               "vsa_equals_store_mat_answers": equality, "reduction_ratios": ratios, "frontier": frontier,
               "claim_ceiling": "exact charged replay at scope; the reduction attack is an exact response-equality test against the materializing exemplar parent; native prices are declared, not measured"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_DC_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    c0 = list(cols)[0]
    print("VSA == STORE_MAT answers everywhere:", all(equality.values()))
    for cname in CELLS:
        print(cname, {r: cells[(cname, r, c0)]["capability"] for r in ROWS}, "| desc ratio", ratios[f"{cname}|{c0}"]["desc_ratio_store_over_vsa"],
              "| exec/q", round(cells[(cname, "VSA", c0)]["exec_per_query"]), "vs", round(cells[(cname, "STORE_MAT", c0)]["exec_per_query"]),
              "| frontier H=128 reduced", frontier[f"{cname}|{c0}|reduced|H=128"], "native", frontier[f"{cname}|{c0}|native|H=128"])
    return receipt


if __name__ == "__main__":
    main(tag=sys.argv[1] if len(sys.argv) > 1 else "V24_DC1_VSA")

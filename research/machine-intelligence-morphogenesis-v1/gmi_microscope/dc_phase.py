"""DC9 — oscillatory / phase-coding carrier: exact microscope and cross-carrier equality attack
(GMI_DOMAIN_CANDIDATES_DC1_DC9_V1.md section 2, record RV-377-054; follows RV-377-044, which reduced DC1).

Carrier: Dp coupled phase units, each holding a phase in Z_Q (Q declared phase levels). Native law:
  BIND      phase offset, theta <- (theta_role + theta_filler) mod Q  (binding by phase locking to a role)
  UNBIND    (theta_cue - theta_role) mod Q
  BUNDLE    the discrete circular mean: per component, the phase p in Z_Q maximizing sum_j cos(2 pi (theta_j - p)/Q),
            i.e. the Kuramoto order-parameter argmax; declared tie-break: the SMALLEST phase
  COHERENCE sum_i cos(2 pi (theta_i - phi_i)/Q), the order parameter of the phase difference
  CLEANUP   argmax coherence over the F filler phase vectors; declared tie-break: the smallest filler index

Ecology E_bindsync: THE SAME OBLIGATION AS DC1's E_rolefill (gmi_microscope/dc_vsa.py), built from the SAME declared
record structures. dc_vsa.ecology produces, for each record, a list of (role path, filler) items; the phase ecology
encodes exactly those items in the phase code, so the two carriers answer the SAME queries, in the SAME order, about
the SAME structures, and their `answer_signature`s are directly comparable. That comparison is the whole point: the
question is whether phase binding is anything other than DC1's binding in a different code.

Rows:
  PHASE           the candidate (phases as the carrier; binding by phase offset; retrieval by phase comparison).
  VSA             DC1's hyperdimensional row, imported unchanged from dc_vsa as a CROSS-DOMAIN parent.
  PHASE_STORE_MAT the strongest D2 parent IN THE CANDIDATE'S OWN CODE: every bound (role path, filler) phase vector
                  materialized at init, answered by maximum coherence. This is the bounded-reduction attack.
  STORE_MAT       DC1's materializing exemplar parent, imported unchanged from dc_vsa (the D2 parent that RV-377-044
                  showed is developmentally identical to VSA).
  PHASE_NOCOUPLE  the negative twin: the oscillators are never phase-locked to their roles — fillers are bundled
                  directly and retrieval compares against the raw cue, so the role structure is lost.

TWO DECLARED PRECISION INSTRUMENTS with IDENTICAL charged operation sequences (the dc_energy.Arith pattern):
  fx8   the registered 8-bit fixed point (scale 16, clamp at +-127): a coherence sum over Dp >= 32 components
        saturates long before it is complete, so phases do not fit the registered universe;
  wide  a declared wide fixed point at scale 2^24 evaluated at unbounded integer precision.
Cosines are taken from a declared Q-entry integer table built from the same integer-Taylor pi constant as dc_quantum.

Accounting: charged ops are the REDUCED price (one op per scalar operation on one phase unit); `ph_ops` counts the
same computation at the DECLARED NATIVE price of one op per PHASE-VECTOR operation, the analogue of dc_vsa's `hv_ops`.
Description: Dp * ceil(log2 Q) bits per stored phase vector plus dc_vsa's declared index overhead, so a Q-level phase
vector of Dp units and a binary hypervector of D = Dp * log2(Q) bits cost the SAME description.
"""
from __future__ import annotations

import json
import math
import os
import sys

from . import bases
from . import dc_vsa
from .core import FX_ONE, Machine, sha256_of
from .dc_quantum import PI_DEN, _cos_w
from .dc_vsa import F_FILLERS, IDX_BITS, R_ROLES, THETA, lcg_bits, paths

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
WIDE_BITS = 24


class PArith:
    """two declared precision instruments with IDENTICAL charged operation sequences.
      fx8 : the registered 8-bit fixed point (scale FX_ONE = 16, clamp at +-127 raw);
      wide: a declared wide fixed point at scale 2^WIDE_BITS, unbounded integer precision."""

    def __init__(self, M, mode):
        self.M = M; self.mode = mode
        self.S = FX_ONE if mode == "fx8" else (1 << WIDE_BITS)

    def add(self, a, b):
        if self.mode == "wide": self.M.op("ADD", 0, 0); return a + b
        return self.M.op("ADD", a, b)

    def sub(self, a, b):
        if self.mode == "wide": self.M.op("SUB", 0, 0); return a - b
        return self.M.op("SUB", a, b)

    def gt(self, a, b):
        if self.mode == "wide": self.M.op("GT", 0, 0); return int(a > b)
        return self.M.op("GT", a, b)


def cos_table(Q, S):
    """declared integer cosine table: cos(2 pi q / Q) at instrument scale S, from the integer-Taylor pi constant."""
    out = []
    for q in range(Q):
        # cos(2 pi q / Q) = cos( (2q mod 2Q) * pi / Q ) with the argument folded into [0, pi]
        num = (2 * q) % (2 * Q)
        v = _cos_w(num, Q) if num <= Q else _cos_w(2 * Q - num, Q)
        neg = v < 0; m = -v if neg else v
        r = (m * S + PI_DEN // 2) // PI_DEN
        out.append(-r if neg else r)
    return out


def lcg_phases(seed, Dp, Q):
    """declared deterministic phase codebook generator: dc_vsa's LCG bit stream, ceil(log2 Q) bits per unit."""
    w = max(1, (Q - 1).bit_length())
    bits = lcg_bits(seed, Dp * w)
    return [sum(((bits >> (i * w + b)) & 1) << b for b in range(w)) % Q for i in range(Dp)]


def codebook(Dp, Q):
    """THE SAME LCG SEEDS AS dc_vsa.codebook (roles 1000+i, fillers 2000+j), read ceil(log2 Q) bits per phase unit.
    At Q = 2 and Dp = D this reproduces DC1's binary codebook BIT FOR BIT, so an equality test between the carriers at
    Q = 2 is a statement about the LAWS and not about two independent random codes."""
    roles = [lcg_phases(1000 + i, Dp, Q) for i in range(R_ROLES)]
    fillers = [lcg_phases(2000 + j, Dp, Q) for j in range(F_FILLERS)]
    return roles, fillers


def bind_path(roles, fillers, path, f, Q):
    """uncharged ecology-side BIND along the path (role phases added to the filler phase, mod Q)."""
    v = list(fillers[f])
    for r in reversed(path):
        v = [(v[i] + roles[r][i]) % Q for i in range(len(v))]
    return v


def bundle_phases(vecs, Q, COS):
    """uncharged ecology-side BUNDLE: the discrete circular mean, ties to the smallest phase."""
    Dp = len(vecs[0]); out = []
    for i in range(Dp):
        best_p, best_s = 0, None
        for p in range(Q):
            s = sum(COS[(v[i] - p) % Q] for v in vecs)
            if best_s is None or s > best_s: best_p, best_s = p, s
        out.append(best_p)
    return out


def ecology(D, depth, k, Dp, Q, noise=0, n_dev=8, n_eval=8, seed=7, phase_noise=0):  # `seed` is the declared RECORD seed (G2 replication axis)
    """DC1's E_rolefill ecology (dc_vsa.ecology, unchanged) plus the phase encoding of THE SAME record structures."""
    e = dc_vsa.ecology(D, depth, k, n_dev=n_dev, n_eval=n_eval, noise=noise, seed=seed)
    COS = cos_table(Q, 1 << WIDE_BITS)  # ecology-side construction uses the wide table
    roles, fillers = codebook(Dp, Q)
    rng = 991
    def nxt():
        nonlocal rng
        rng = (rng * 1103515245 + 12345) & 0xFFFFFFFF
        return rng >> 16
    for idx, rec in enumerate(e["dev"] + e["eval"]):
        vs = [bind_path(roles, fillers, p, f, Q) for p, f in rec["items"]]
        cue = bundle_phases(vs, Q, COS)
        if phase_noise and idx >= n_dev:
            for _ in range(phase_noise):
                i = nxt() % Dp; cue[i] = (cue[i] + 1) % Q  # declared phase noise: a one-step kick
        rec["phase_cue"] = cue
    e.update({"Dp": Dp, "Q": Q, "phase_roles": roles, "phase_fillers": fillers, "phase_noise": phase_noise,
              "phase_bits_per_vector": Dp * max(1, (Q - 1).bit_length()), "vsa_bits_per_vector": D})
    return e


# -------------------------------------------------------------------------------------------------------- rows
def _mod_sub(A, a, b, Q):
    """charged modular phase difference (a - b) mod Q: SUB + GT + conditional SUB (3 ops)."""
    d = A.sub(a, b)
    if A.gt(0, d): d = A.sub(d, -Q)
    else: A.sub(0, 0)
    return d % Q


def _mod_add(A, a, b, Q):
    """charged modular phase sum (a + b) mod Q: ADD + GT + conditional SUB (3 ops)."""
    d = A.add(a, b)
    if A.gt(d, Q - 1): d = A.sub(d, Q)
    else: A.sub(0, 0)
    return d % Q


def _cos_lookup(M, COS, Q, d):
    """charged Q-entry cosine table lookup as a multiplexer tree (ceil(log2 Q) SEL ops)."""
    for b in range(max(1, (Q - 1).bit_length())): M.op("SEL", (d >> b) & 1, 0, 0)
    return COS[d]


class PhaseRow:
    row = "PHASE"

    def __init__(self, eco, A, COS):
        self.e = eco; self.A = A; self.COS = COS; self.ph_ops = 0

    def init(self, M):
        self.roles = self.e["phase_roles"]; self.fillers = self.e["phase_fillers"]

    def observe(self, M, rec): pass

    def _coherence(self, M, a, b):
        A = self.A; Q = self.e["Q"]; s = 0
        for i in range(self.e["Dp"]):
            s = A.add(s, _cos_lookup(M, self.COS, Q, _mod_sub(A, a[i], b[i], Q)))
        self.ph_ops += 1
        return s

    def query(self, M, rec, path):
        A = self.A; Q = self.e["Q"]; v = list(rec["phase_cue"])
        for r in path:
            v = [_mod_sub(A, v[i], self.roles[r][i], Q) for i in range(self.e["Dp"])]
            self.ph_ops += 1  # UNBIND
        cs = [self._coherence(M, v, f) for f in self.fillers]  # CLEANUP
        best = 0
        for j in range(1, len(cs)):
            if A.gt(cs[j], cs[best]): best = j  # declared tie-break: the smallest filler index
        return best

    def desc_bits(self):
        return (R_ROLES + F_FILLERS) * (self.e["phase_bits_per_vector"] + IDX_BITS)


class PhaseStoreMat(PhaseRow):
    """the strongest D2 parent IN THE CANDIDATE'S OWN CODE: materialize every bound (role path, filler) phase vector
    at init and answer by maximum coherence among the candidates whose path matches the query. Its answers are
    provably identical to PHASE's, because coherence(cue - role, f) = coherence(cue, role + f) componentwise — the
    same lazy-versus-eager identity that RV-377-044 executed for the binary code."""
    row = "PHASE_STORE_MAT"

    def init(self, M):
        super().init(M)
        A = self.A; Q = self.e["Q"]; Dp = self.e["Dp"]; self.table = {}
        for pth in paths(self.e["depth"]):
            for f in range(F_FILLERS):
                v = list(self.fillers[f])
                for r in reversed(pth):
                    v = [_mod_add(A, v[i], self.roles[r][i], Q) for i in range(Dp)]
                    self.ph_ops += 1  # materialization cost at the declared native price
                self.table.setdefault(pth, []).append(v)
        self.n_stored = sum(len(v) for v in self.table.values())

    def query(self, M, rec, path):
        A = self.A; cands = self.table[path]
        cs = [self._coherence(M, rec["phase_cue"], c) for c in cands]
        best = 0
        for j in range(1, len(cs)):
            if A.gt(cs[j], cs[best]): best = j
        return best

    def desc_bits(self):
        return self.n_stored * (self.e["phase_bits_per_vector"] + IDX_BITS)


class PhaseNoCouple(PhaseRow):
    """negative twin: the oscillators are never phase-locked to their roles, so the cue is compared to the raw
    filler phase vectors and the role structure is lost."""
    row = "PHASE_NOCOUPLE"

    def query(self, M, rec, path):
        A = self.A
        cs = [self._coherence(M, rec["phase_cue"], f) for f in self.fillers]
        best = 0
        for j in range(1, len(cs)):
            if A.gt(cs[j], cs[best]): best = j
        return best


PHASE_ROWS = {"PHASE": PhaseRow, "PHASE_STORE_MAT": PhaseStoreMat, "PHASE_NOCOUPLE": PhaseNoCouple}
VSA_ROWS = ("VSA", "STORE_MAT")
ROWS = tuple(PHASE_ROWS) + VSA_ROWS


def run_phase(row, basis, eco, seed=0, precision="wide"):
    M = Machine(basis, seed=seed); A = PArith(M, precision)
    COS = cos_table(eco["Q"], A.S)
    ref = PHASE_ROWS[row](eco, A, COS)
    M.phase("exec"); ref.init(M)
    init_ops = dict(M.L.c)
    for rec in eco["dev"]:
        M.phase("upd"); ref.observe(M, rec); M.end_event()
    M.phase("exec"); correct = 0; total = 0; answers = []
    for rec in eco["eval"]:
        for p, f in rec["answers"].items():
            a = ref.query(M, rec, p); answers.append((tuple(p), a)); total += 1; correct += int(a == f)
    cap = round(correct / total, 4) if total else 0.0
    R = dict(M.L.c)
    return {"row": row, "basis": basis.name, "precision": precision, "capability": cap, "admissible": cap >= THETA,
            "R": R, "compile_ops": init_ops["exec"], "exec_per_query": (R["exec"] - init_ops["exec"]) / total,
            "native_per_query": ref.ph_ops / total, "ph_ops": ref.ph_ops, "desc_bits": ref.desc_bits(),
            "n_queries": total, "answer_signature": sha256_of(answers)}


def run_vsa(row, basis, eco, seed=0, precision="wide"):
    """DC1's rows, imported unchanged; the precision label is carried for shape only — the hyperdimensional rows are
    pure bit operations and do not depend on the arithmetic instrument (their identity across instruments is checked)."""
    d = dc_vsa.run(row, basis, eco, seed)
    d["precision"] = precision
    d["native_per_query"] = d["hv_ops"] / d["n_queries"]
    d["ph_ops"] = d["hv_ops"]
    return d


def run(row, basis, eco, seed=0, precision="wide"):
    return run_phase(row, basis, eco, seed, precision) if row in PHASE_ROWS else run_vsa(row, basis, eco, seed, precision)


# ------------------------------------------------------------------------------------------------------- cells
CELLS = {
    # equal-description cells: Dp * log2(Q) == D, so the phase and binary codes cost the same bits per vector
    "D64_d1_k3_Q2_P64": {"D": 64, "depth": 1, "k": 3, "Dp": 64, "Q": 2, "noise": 0, "phase_noise": 0},
    "D64_d1_k4_Q2_P64": {"D": 64, "depth": 1, "k": 4, "Dp": 64, "Q": 2, "noise": 0, "phase_noise": 0},
    "D64_d1_k3_Q4_P32": {"D": 64, "depth": 1, "k": 3, "Dp": 32, "Q": 4, "noise": 0, "phase_noise": 0},
    "D64_d1_k4_Q4_P32": {"D": 64, "depth": 1, "k": 4, "Dp": 32, "Q": 4, "noise": 0, "phase_noise": 0},
    "D96_d1_k3_Q8_P32": {"D": 96, "depth": 1, "k": 3, "Dp": 32, "Q": 8, "noise": 0, "phase_noise": 0},
    "D96_d1_k3_Q2_P96": {"D": 96, "depth": 1, "k": 3, "Dp": 96, "Q": 2, "noise": 0, "phase_noise": 0},
    # richer-code cell: the phase row is given twice the description of the binary row
    "D64_d1_k3_Q4_P64": {"D": 64, "depth": 1, "k": 3, "Dp": 64, "Q": 4, "noise": 0, "phase_noise": 0},
    # depth-2 (compositional) cells
    "D64_d2_k3_Q2_P64": {"D": 64, "depth": 2, "k": 3, "Dp": 64, "Q": 2, "noise": 0, "phase_noise": 0},
    "D128_d2_k3_Q4_P64": {"D": 128, "depth": 2, "k": 3, "Dp": 64, "Q": 4, "noise": 0, "phase_noise": 0},
    # noisy cell: 8 bit flips for the binary cue, 8 one-step phase kicks for the phase cue (declared analogues)
    "D64_d1_k3_Q2_P64_noisy": {"D": 64, "depth": 1, "k": 3, "Dp": 64, "Q": 2, "noise": 8, "phase_noise": 8},
    "D64_d1_k3_Q4_P32_noisy": {"D": 64, "depth": 1, "k": 3, "Dp": 32, "Q": 4, "noise": 8, "phase_noise": 8},
}


BASE_CELLS = dict(CELLS)
CELLS = {f"{n}_s{s_}": {**v, "rec_seed": s_} for n, v in BASE_CELLS.items() for s_ in (7, 13, 23)}


def lifecycle(r, H, native=False):
    per_q = r["native_per_query"] if native else r["exec_per_query"]
    fixed = r["desc_bits"] + (0 if native else r.get("compile_ops", 0))
    return fixed + H * per_q


def crossovers(adm, price):
    out = {}; names = sorted(adm); nat = price == "native"
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            ra, rb = adm[a], adm[b]
            fa = ra["desc_bits"] + (0 if nat else ra.get("compile_ops", 0))
            fb = rb["desc_bits"] + (0 if nat else rb.get("compile_ops", 0))
            pa = ra["native_per_query"] if nat else ra["exec_per_query"]
            pb = rb["native_per_query"] if nat else rb["exec_per_query"]
            if pa == pb: continue
            h = (fb - fa) / (pa - pb)
            if h > 0: out[f"{a}|{b}"] = round(h, 4)
    return out


def grid_for(cross, base=(1, 16, 128, 1024)):
    g = set(base)
    for h in cross.values():
        g.add(max(1, int(math.floor(h)))); g.add(int(math.ceil(h)) + 1); g.add(2 * int(math.ceil(h)) + 2)
    return sorted(g)


def main(tag="V32_DC9_PHASE", seed=0, cells=None):
    col = "B0_LOCAL_ADAPTIVE_TRANSDUCERS"; b = bases.ALL[col]
    use = cells if cells is not None else CELLS
    out = {}; ecos = {}
    for cname, spec in use.items():
        eco = ecology(spec["D"], spec["depth"], spec["k"], spec["Dp"], spec["Q"], noise=spec["noise"],
                      phase_noise=spec["phase_noise"], seed=spec.get("rec_seed", 7))
        ecos[cname] = eco
        for rname in ROWS:
            for prec in ("fx8", "wide"): out[(cname, rname, prec)] = run(rname, b, eco, seed, prec)
    # --- the cross-carrier equality attack: are the phase carrier's answers DC1's answers?
    equality = {}
    for cname in use:
        for prec in ("fx8", "wide"):
            p = out[(cname, "PHASE", prec)]; v = out[(cname, "VSA", prec)]; s = out[(cname, "STORE_MAT", prec)]
            psm = out[(cname, "PHASE_STORE_MAT", prec)]
            equality[f"{cname}|{prec}"] = {
                "phase_equals_vsa": p["answer_signature"] == v["answer_signature"],
                "phase_equals_phase_store_mat": p["answer_signature"] == psm["answer_signature"],
                "capability_phase_store_mat": psm["capability"],
                "phase_equals_store_mat": p["answer_signature"] == s["answer_signature"],
                "vsa_equals_store_mat": v["answer_signature"] == s["answer_signature"],
                "capability_phase": p["capability"], "capability_vsa": v["capability"],
                "equal_description": ecos[cname]["phase_bits_per_vector"] == ecos[cname]["vsa_bits_per_vector"],
                "Q": ecos[cname]["Q"], "k": use[cname]["k"], "k_parity": "odd" if use[cname]["k"] % 2 else "even"}
    frontier = {}; cross_all = {}; grids = {}; occupants = {}
    for cname in use:
        for prec in ("fx8", "wide"):
            for price in ("reduced", "native"):
                adm = {r: out[(cname, r, prec)] for r in ROWS if out[(cname, r, prec)]["admissible"]}
                cr = crossovers(adm, price); key = f"{cname}|{prec}|{price}"
                cross_all[key] = cr; g = grid_for(cr); grids[key] = g
                for H in g:
                    if not adm: frontier[f"{key}|H={H}"] = []; continue
                    costs = {r: lifecycle(adm[r], H, native=(price == "native")) for r in adm}
                    frontier[f"{key}|H={H}"] = sorted(r for r, c in costs.items() if c <= min(costs.values()) + 1e-9)
                occupants[key] = sorted({r for H in g for r in frontier[f"{key}|H={H}"]})
    receipt = {"schema": "StageDC9PhaseV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422],
               "revival_record": "RV-377-054", "run_tag": tag,
               "domain_candidate": "DC9 oscillatory / phase coding (Kuramoto-style coupled phases, binding by synchrony)",
               "ecology": "E_bindsync: DC1's E_rolefill obligation (gmi_microscope/dc_vsa.ecology, unchanged) with the SAME record structures additionally encoded in the phase code, so the two carriers answer the same queries in the same order and their answer signatures are directly comparable",
               "cells_spec": use, "theta": THETA, "rows": list(ROWS),
               "ecology_note": "dc_vsa.ecology draws k DISTINCT role paths per record, so k <= R_ROLES = 4 at depth 1 and k <= 16 at depth 2; every declared cell respects that bound",
               "replication": "every base cell is run at THREE declared record seeds (7, 13 and 23): a G2-style replication of the capability comparison on independently drawn record structures",
               "codebook": {"R_roles": R_ROLES, "F_fillers": F_FILLERS, "phase_generator": "dc_vsa LCG(1103515245, 12345) bit stream, ceil(log2 Q) bits per phase unit; THE SAME SEEDS as dc_vsa.codebook (roles 1000+i, fillers 2000+j), so at Q = 2 and Dp = D the phase codebook IS DC1's binary codebook bit for bit", "index_bits_per_stored_vector": IDX_BITS,
                            "cosine_table": "declared Q-entry integer table cos(2 pi q / Q) from the integer-Taylor pi constant of dc_quantum"},
               "declared_prices": {"native": "one op per PHASE-VECTOR operation (UNBIND, COHERENCE), the analogue of dc_vsa's hv_ops", "reduced": "per phase unit: 3 ops for a modular phase difference (SUB + GT + conditional SUB) + ceil(log2 Q) SEL for the cosine table + 1 ADD to accumulate"},
               "precision_instruments": {"fx8": "registered universe: TOTAL_BITS 8, FRAC_BITS 4, coherence sums saturate at +-127", "wide": "declared wide fixed point at scale 2^24, unbounded integer precision; IDENTICAL charged operation sequence"},
               "tie_breaks": {"phase_bundle": "the SMALLEST phase (declared)", "vsa_bundle": "dc_vsa's declared tie VECTOR lcg_bits(3000, D)", "cleanup": "the smallest filler index in both carriers"},
               "ecology_facts": {c: {"phase_bits_per_vector": ecos[c]["phase_bits_per_vector"], "vsa_bits_per_vector": ecos[c]["vsa_bits_per_vector"],
                                     "equal_description": ecos[c]["phase_bits_per_vector"] == ecos[c]["vsa_bits_per_vector"],
                                     "noise_bitflips": use[c]["noise"], "phase_noise_kicks": use[c]["phase_noise"]} for c in use},
               "cells": {f"{c}|{r}|{p}": {k: v for k, v in d.items() if k not in ("row", "basis")} for (c, r, p), d in out.items()},
               "cross_carrier_equality": equality, "analytic_crossovers": cross_all, "frontier_grids": grids,
               "frontier": frontier, "frontier_occupants_over_extended_grid": occupants,
               "claim_ceiling": "exact charged replay at scope; DC1's ecology and DC1's two rows are imported unchanged, so the comparison is on one obligation only; the hyperdimensional rows are pure bit operations and carry no arithmetic instrument, so the fx8/wide axis moves only the phase rows; native prices are declared, not measured; one declared codebook per cell"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_DC_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    for cname in use:
        e = equality[f"{cname}|wide"]
        print(cname, "eqdesc", e["equal_description"], "| wide caps",
              {r: out[(cname, r, "wide")]["capability"] for r in ROWS},
              "| fx8 PHASE", out[(cname, "PHASE", "fx8")]["capability"],
              "| P==VSA", e["phase_equals_vsa"], "P==SM", e["phase_equals_store_mat"],
              "| desc", {r: out[(cname, r, "wide")]["desc_bits"] for r in ROWS})
    return receipt


if __name__ == "__main__":
    main(tag=sys.argv[1] if len(sys.argv) > 1 else "V32_DC9_PHASE")

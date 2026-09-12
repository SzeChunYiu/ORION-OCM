"""DK — the DEPTH-GATED KINGDOM question: an exact charged microscope over a depth-indexed family of role-filler
ecologies, run against an adversarially constructed PARENT-MAXIMAL opponent (issue #422, record RV-377-065).

Context. GMI-DA2 (`GMI_DOMAIN_ALGEBRA_EXECUTED_V1.md` section 3) proved the lazy/eager duality for the binding carrier:
the algebraic realization (store a codebook, compose on demand) and the materializing exemplar store (store every
composite) are exactly developmentally equal and differ only in a description/serve trade with a reuse crossover H*.
GMI-DA3 (section 4) then claimed the one escape on the depth axis: with R roles, F fillers and structure depth d,

    H*(d) = [ (R^d*F - (R+F))*bits + R^d*F*D*d ] / (d*D)   ~   R^d / d,

unbounded in d, so no single reuse horizon amortizes the reduction over a family of unbounded depth. That is a
statement about a family, not a carrier, and it is exactly what `GMI_STRUCTURAL_DOMAINS_KINGDOMS_V1.md` section 14
criterion 3 must be read with (gap DG-3). This microscope turns the remark into an executed decision.

The decisive point of this module is protocol rule 19 (gap DG-5): a reduction verdict is valid only against a
PARENT-MAXIMAL opponent. GMI-DA3's formula assumes the parent must materialize R^d * F distinct bound vectors. Whether
it must is a property of the BINDING OPERATOR, and it is measured here rather than assumed:

  * `XOR` -- the law RV-377-044 actually executed (`gmi_microscope/dc_vsa.py`): BIND is bitwise XOR, which is
    commutative and involutive, so the composition along a path depends only on the PARITY of the multiset of roles.
    The number of distinct path vectors is therefore at most 2^R, not R^d, and it SATURATES with depth.
  * `PERM` -- the same carrier with the PERMUTE primitive that DC1's declared native basis already contains
    (`GMI_DOMAIN_CANDIDATES_DC1_DC9_V1.md` section 2: "ops BIND, BUNDLE(k), PERMUTE, HAMMING, CLEANUP"): the role at
    path position i is protected by the cyclic shift rho^i before binding, so distinct paths give distinct path
    vectors and the binding set is genuinely R^d.

Ecology E_rolefill(R, F, d): R = 4 roles, F = 8 fillers, records are bundles of k bound (role path, filler) structures
at structure depth d. Record STRUCTURES are drawn law-independently, so the two laws answer the same queries about the
same structures. Development shows SEEN records; evaluation asks (cue, role path) -> filler on records never seen.

Rows (all charged exactly; identical cues, answers compared bit for bit through `answer_signature`):
  VSA          the algebraic/binding carrier: codebook only, fold the path roles into the cue, clean up over F fillers.
               Its charged op sequence at depth 1 under the XOR law is dc_vsa.VSA's, op for op.
  STORE_MAT    the materializing exemplar store of RV-377-044, generalized to depth d: one stored vector per
               (path, filler), answered by nearest among the F candidates of the queried path.
  STORE_PATH   ADVERSARIAL PARENT 1: materialize the R^d PATH vectors only and serve with one XOR plus the cleanup.
               Strictly stronger than STORE_MAT (it is smaller by a factor approaching F) and still an exemplar store:
               TABLE + LOOKUP + NEAREST plus one Boolean op, i.e. the declared "D2 x Boolean-D1" parent of DC1.
  STORE_DEDUP  ADVERSARIAL PARENT 2, and the parent-maximal one under the XOR law: materialize one bundle per DISTINCT
               path vector and recover the class from the path by a declared key program (for XOR, the R-bit parity of
               the role multiset; for PERM, no two paths collide, so the class IS the path and this row degenerates to
               STORE_MAT). Its description is bounded by 2^R * F vectors UNIFORMLY IN DEPTH under the XOR law.
  STORE_SEEN   plain exemplar memory over the records seen in development.
  VSA_NOBIND   the negative twin: fillers compared to the raw cue, the binding law removed.
  PARENT_BEST  not a machine: the pointwise-minimum lifecycle over the admissible parent rows at each reuse horizon.
               This is the declared parent-maximal opponent against which the kingdom question is decided.

DG-2 is fixed here by construction: for every cell and every declared price vector the analytic crossover of every
admissible pair is computed FIRST, in exact rational arithmetic, and the reuse grid is then built to span at least
twice the largest crossover it reports (`grid_for`, asserted by `check_dg2`). No "no cell exists" clause in this
module's frozen prediction is evaluated on a grid that stops short of a crossover.

Arithmetic. Description, compile and serve costs are exact integers of charged Machine ops; every frontier comparison
is done in `fractions.Fraction`, so no lifecycle ordering depends on a floating-point tolerance. The only rounded
quantity is `capability` (correct/total, rounded to 4 places, the registered convention of the D'/E' microscopes);
admissibility is decided on the exact rational correct/total against theta = 0.85. Universe: TOTAL_BITS 8,
FRAC_BITS 4, basis B0, theta 0.85, cost model C = desc + H*exec_q + r*(upd_e + ver_e) + (r/4)*rev_e (this ecology
registers no feedback, verification or revocation events, so r = 0 and C = desc + H*exec_q, plus compile under the
reduced price).
"""
from __future__ import annotations

import itertools
import json
import os
import sys
from fractions import Fraction

from . import bases
from .core import Machine, sha256_of
from .dc_vsa import F_FILLERS, IDX_BITS, R_ROLES, THETA, _argmin, _hamming, _xor_bits, lcg_bits

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
LAWS = ("XOR", "PERM")
N_DEV = 8
N_EVAL = 8


# ------------------------------------------------------------------------------------------------------- structures
def paths(depth):
    """every role path of length `depth` over R_ROLES roles: R^depth of them, in a declared deterministic order."""
    return [tuple(t) for t in itertools.product(range(R_ROLES), repeat=depth)]


def codebook(D):
    """dc_vsa's declared codebook, unchanged: LCG(1103515245, 12345), roles seed 1000+i, fillers seed 2000+j."""
    return [lcg_bits(1000 + i, D) for i in range(R_ROLES)], [lcg_bits(2000 + j, D) for j in range(F_FILLERS)]


def rot(v, D, s):
    """PERMUTE: cyclic left shift of a D-bit hypervector by s positions (uncharged, ecology side)."""
    s %= D
    return ((v << s) | (v >> (D - s))) & ((1 << D) - 1)


def path_vector(roles, path, D, law):
    """uncharged ecology-side path composition. XOR: the XOR of the path's role vectors (commutative and involutive,
    so only the parity of the role multiset survives). PERM: role at position i protected by rho^i before binding."""
    v = 0
    for i, r in enumerate(path):
        v ^= roles[r] if law == "XOR" else rot(roles[r], D, i)
    return v


def parity_key(path):
    """the declared class key of the XOR law: the R-bit indicator of the roles occurring an odd number of times."""
    e = 0
    for r in path: e ^= 1 << r
    return e


def class_key(path, law):
    return parity_key(path) if law == "XOR" else path


def bundle(vecs, D, tie):
    """BUNDLE = bitwise majority; ties broken by dc_vsa's declared tie vector lcg_bits(3000, D)."""
    out = 0
    for b in range(D):
        s = sum((v >> b) & 1 for v in vecs)
        if 2 * s > len(vecs): out |= 1 << b
        elif 2 * s == len(vecs) and ((tie >> b) & 1): out |= 1 << b
    return out


def structures(depth, k, seed, n_dev=N_DEV, n_eval=N_EVAL):
    """LAW-INDEPENDENT record structures: k distinct role paths per record with their fillers, drawn by dc_vsa's
    declared LCG stream, so the XOR and PERM columns answer the same queries about the same structures."""
    P = paths(depth); rng = seed; out = []
    def nxt():
        nonlocal rng
        rng = (rng * 1103515245 + 12345) & 0xFFFFFFFF
        return rng >> 16
    for _ in range(n_dev + n_eval):
        chosen = []; used = set()
        while len(chosen) < k:
            p = P[nxt() % len(P)]
            if p in used: continue
            used.add(p); chosen.append((p, nxt() % F_FILLERS))
        out.append(chosen)
    return out


def ecology(D, depth, k, law, seed=7, n_dev=N_DEV, n_eval=N_EVAL, role_relabel=None, filler_relabel=None):
    """E_rolefill(R, F, d) in the declared law. `role_relabel`/`filler_relabel` are the REMINT nuisance maps: a
    relabelling of the role and filler indices together with the matching relabelling of the codebook, which leaves
    every bound vector and every cue bit-identical and permutes only the names (H5)."""
    roles, fillers = codebook(D); tie = lcg_bits(3000, D)
    sr = list(range(R_ROLES)) if role_relabel is None else list(role_relabel)
    sf = list(range(F_FILLERS)) if filler_relabel is None else list(filler_relabel)
    # roles_lab[sr[i]] = roles[i]: the new label sr[i] names the old vector, so bound vectors are unchanged
    roles_lab = [0] * R_ROLES; fillers_lab = [0] * F_FILLERS
    for i in range(R_ROLES): roles_lab[sr[i]] = roles[i]
    for j in range(F_FILLERS): fillers_lab[sf[j]] = fillers[j]
    recs = []
    for items in structures(depth, k, seed, n_dev, n_eval):
        lab = [(tuple(sr[r] for r in p), sf[f]) for p, f in items]
        vs = [path_vector(roles_lab, p, D, law) ^ fillers_lab[f] for p, f in lab]
        recs.append({"cue": bundle(vs, D, tie), "answers": {p: f for p, f in lab}, "items": lab})
    pv = {p: path_vector(roles_lab, p, D, law) for p in paths(depth)}
    classes = {}
    for p in paths(depth): classes.setdefault(class_key(p, law), []).append(p)
    ambiguous = sum(1 for r in recs[n_dev:] for p, _ in r["items"]
                    if sum(1 for q, _ in r["items"] if pv[q] == pv[p]) > 1)
    # exactly-tied cleanups: the declared tie-break (smallest filler index) decides these, so they are the only
    # queries whose ANSWER depends on the nuisance labelling of the fillers (measured, not assumed)
    ties = 0
    for r in recs[n_dev:]:
        for p, _ in r["items"]:
            v = r["cue"] ^ pv[p]
            ds = [bin(v ^ f).count("1") for f in fillers_lab]
            ties += int(ds.count(min(ds)) > 1)
    return {"roles": roles_lab, "fillers": fillers_lab, "tie": tie, "D": D, "depth": depth, "k": k, "law": law,
            "dev": recs[:n_dev], "eval": recs[n_dev:], "path_vectors": pv, "classes": classes,
            "n_paths": len(pv), "n_distinct_path_vectors": len(set(pv.values())), "n_classes": len(classes),
            "ambiguous_eval_queries": ambiguous, "tied_cleanup_eval_queries": ties, "seed": seed,
            "role_relabel": sr, "filler_relabel": sf}


# ------------------------------------------------------------------------------------------------- charged helpers
def _permute(M, v, D, s):
    """charged PERMUTE: a cyclic shift is wiring, charged one gate per bit exactly as core.py's SHR macro charges
    its shift. s = 0 is the identity and is not applied, hence not charged."""
    if s % D == 0: return v
    for _ in range(D): M.op("AND", 1, 1)
    return rot(v, D, s)


def _fold_path(M, row, M_v, roles, path, D, law):
    """charged composition of the path roles into `M_v` (the cue for the candidate, 0-seeded for a parent's compile).
    The FIRST role is taken from the codebook for free when M_v is None (nothing to combine it with yet)."""
    v = M_v
    for i, r in enumerate(path):
        u = roles[r] if law == "XOR" else _permute(M, roles[r], D, i)
        if law == "PERM" and i > 0: row.hv_ops += 1
        if v is None: v = u
        else:
            v = _xor_bits(M, v, u, D); row.hv_ops += 1
    return 0 if v is None else v  # the empty path (the XOR law's identity class) composes to the zero vector


# ----------------------------------------------------------------------------------------------------------- rows
class Row:
    row = "?"
    is_parent = False

    def __init__(self, eco): self.e = eco; self.hv_ops = 0; self.hv_compile = 0

    def init(self, M): pass

    def observe(self, M, rec): pass

    def query(self, M, rec, path): raise NotImplementedError

    def desc_bits(self): raise NotImplementedError


class VSA(Row):
    """the algebraic/binding carrier: the codebook is the whole served state; the path is composed on demand."""
    row = "VSA"

    def init(self, M):
        self.roles = self.e["roles"]; self.fillers = self.e["fillers"]

    def query(self, M, rec, path):
        D = self.e["D"]
        v = _fold_path(M, self, rec["cue"], self.roles, path, D, self.e["law"])
        ds = [_hamming(M, v, f, D) for f in self.fillers]; self.hv_ops += len(self.fillers)
        return _argmin(M, ds)

    def desc_bits(self):
        return (R_ROLES + F_FILLERS) * (self.e["D"] + IDX_BITS)


class VSANoBind(VSA):
    """negative twin: the binding law is removed, so the cue is compared to the raw filler vectors."""
    row = "VSA_NOBIND"

    def query(self, M, rec, path):
        D = self.e["D"]
        ds = [_hamming(M, rec["cue"], f, D) for f in self.fillers]; self.hv_ops += len(self.fillers)
        return _argmin(M, ds)


class StorePath(Row):
    """ADVERSARIAL PARENT 1: one stored vector per role path; serve = one XOR plus the cleanup."""
    row = "STORE_PATH"
    is_parent = True

    def init(self, M):
        D = self.e["D"]; self.fillers = self.e["fillers"]; self.table = {}
        for p in paths(self.e["depth"]):
            self.table[p] = _fold_path(M, self, None, self.e["roles"], p, D, self.e["law"])
        self.hv_compile = self.hv_ops; self.hv_ops = 0
        self.n_stored = len(self.table) + F_FILLERS

    def query(self, M, rec, path):
        D = self.e["D"]
        v = _xor_bits(M, rec["cue"], self.table[path], D); self.hv_ops += 1
        ds = [_hamming(M, v, f, D) for f in self.fillers]; self.hv_ops += len(self.fillers)
        return _argmin(M, ds)

    def desc_bits(self):
        return self.n_stored * (self.e["D"] + IDX_BITS)


class StoreMat(Row):
    """the materializing exemplar parent of RV-377-044 at depth d: one stored vector per (path, filler)."""
    row = "STORE_MAT"
    is_parent = True

    def _keys(self):
        return [(p, [p]) for p in paths(self.e["depth"])]

    def init(self, M):
        D = self.e["D"]; self.table = {}
        for key, reps in self._keys():
            P = _fold_path(M, self, None, self.e["roles"], reps[0], D, self.e["law"])
            self.table[key] = [_xor_bits(M, P, f, D) for f in self.e["fillers"]]
            self.hv_ops += F_FILLERS
        self.hv_compile = self.hv_ops; self.hv_ops = 0
        self.n_stored = sum(len(v) for v in self.table.values())

    def _key_of(self, M, path):
        return path

    def query(self, M, rec, path):
        D = self.e["D"]; cands = self.table[self._key_of(M, path)]
        ds = [_hamming(M, rec["cue"], c, D) for c in cands]; self.hv_ops += len(cands)
        return _argmin(M, ds)

    def desc_bits(self):
        return self.n_stored * (self.e["D"] + IDX_BITS)


class StoreDedup(StoreMat):
    """ADVERSARIAL PARENT 2: one stored bundle per DISTINCT path vector, with the class recovered from the path by a
    declared key program. Under the XOR law the class is the R-bit parity of the role multiset, so the store is bounded
    by 2^R * F vectors uniformly in depth; under the PERM law no two paths collide and the row degenerates to
    STORE_MAT with a free key."""
    row = "STORE_DEDUP"
    is_parent = True

    def _keys(self):
        """the CHEAPEST representative of each class, so the opponent's materialization is itself parent-maximal:
        under the XOR law the parity subset (sorted, length |e| <= R) composes to the same vector as any path in the
        class at strictly lower charged cost; under the PERM law the class is the path and the path is its own
        representative."""
        out = []
        for key, ps in sorted(self.e["classes"].items(), key=str):
            rep = tuple(r for r in range(R_ROLES) if (key >> r) & 1) if self.e["law"] == "XOR" else sorted(ps)[0]
            out.append((key, [rep]))
        return out

    def _key_of(self, M, path):
        if self.e["law"] != "XOR": return path
        e = 0
        for r in path:
            for b in range(R_ROLES): M.op("XOR", (e >> b) & 1, 1 if b == r else 0)
            e ^= 1 << r
        return e

    def desc_bits(self):
        key_prog = 0 if self.e["law"] != "XOR" else R_ROLES + self.e["depth"]  # R-bit parity register + d toggle ops
        return self.n_stored * (self.e["D"] + IDX_BITS) + key_prog


class StoreSeen(Row):
    """plain exemplar memory over the records seen in development (nearest seen cue -> its answer on that path)."""
    row = "STORE_SEEN"
    is_parent = True

    def init(self, M): self.mem = []

    def observe(self, M, rec): self.mem.append((rec["cue"], dict(rec["answers"])))

    def query(self, M, rec, path):
        D = self.e["D"]
        cands = [(c, a) for c, a in self.mem if path in a]
        if not cands: return -1
        ds = [_hamming(M, rec["cue"], c, D) for c, _ in cands]; self.hv_ops += len(cands)
        return cands[_argmin(M, ds)][1][path]

    def desc_bits(self):
        # one cue plus its index label, plus k answers of (path label, filler label) bits each
        per_item = 2 * self.e["depth"] + 3
        return len(self.mem) * (self.e["D"] + IDX_BITS + self.e["k"] * per_item)


ROWS = {"VSA": VSA, "STORE_MAT": StoreMat, "STORE_PATH": StorePath, "STORE_DEDUP": StoreDedup,
        "STORE_SEEN": StoreSeen, "VSA_NOBIND": VSANoBind}
PARENT_ROWS = tuple(r for r, c in ROWS.items() if c.is_parent)


def run(row, basis, eco, seed=0):
    ref = ROWS[row](eco); M = Machine(basis, seed=seed)
    M.phase("exec"); ref.init(M)
    init_ops = dict(M.L.c)
    for rec in eco["dev"]:
        M.phase("upd"); ref.observe(M, rec); M.end_event()
    M.phase("exec"); correct = 0; total = 0; answers = []
    for rec in eco["eval"]:
        for p, f in sorted(rec["answers"].items()):
            a = ref.query(M, rec, p); answers.append((tuple(p), a)); total += 1; correct += int(a == f)
    R = dict(M.L.c)
    exec_total = R["exec"] - init_ops["exec"]
    return {"row": row, "basis": basis.name, "capability": round(correct / total, 4) if total else 0.0,
            "correct": correct, "n_queries": total, "admissible": Fraction(correct, total) >= Fraction(85, 100),
            "R": R, "compile_ops": init_ops["exec"], "exec_ops_total": exec_total,
            "exec_per_query": exec_total / total, "hv_ops": ref.hv_ops, "hv_compile_ops": ref.hv_compile,
            "native_per_query": ref.hv_ops / total, "desc_bits": ref.desc_bits(),
            "answer_signature": sha256_of(answers)}


# ------------------------------------------------------------------------------------------- lifecycle and frontier
def fixed_cost(r, price):
    """C = desc + H*exec_q under the registered cost model; the ecology registers no upd/ver/rev events, so r = 0.
    Under `reduced` the parent's materialization is charged; under `native` it is not (the dc_phase convention),
    which is the PARENT-MAXIMAL reading and is used for the kingdom verdict."""
    return Fraction(r["desc_bits"] + (r["compile_ops"] if price == "reduced" else 0))


def per_query(r, price):
    return Fraction(r["exec_ops_total"], r["n_queries"]) if price == "reduced" else Fraction(r["hv_ops"], r["n_queries"])


def lifecycle(r, H, price):
    return fixed_cost(r, price) + Fraction(H) * per_query(r, price)


def crossovers(adm, price):
    """exact rational crossovers of every admissible pair, computed BEFORE any grid is built (gap DG-2)."""
    out = {}; names = sorted(adm)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            pa, pb = per_query(adm[a], price), per_query(adm[b], price)
            if pa == pb: continue
            h = (fixed_cost(adm[b], price) - fixed_cost(adm[a], price)) / (pa - pb)
            if h > 0: out[f"{a}|{b}"] = h
    return out


BASE_GRID = (1, 16, 128, 1024)


def grid_for(cross, base=BASE_GRID):
    """DG-2: the reuse grid spans at least TWICE the largest analytic crossover reported for this cell, and brackets
    every individual crossover from below and above."""
    g = set(base)
    for h in cross.values():
        f = int(h)
        g.update({max(1, f), f + 1, 2 * f + 2})
    if cross:
        hmax = max(cross.values())
        g.update({2 * int(hmax) + 2, 4 * int(hmax) + 4})
    return sorted(g)


def check_dg2(cross, grid):
    """the DG-2 assertion itself: no crossover of this cell lies at or beyond half the grid's extent."""
    if not cross: return True
    return max(grid) >= 2 * max(cross.values())


def frontier_of(adm, price, grid):
    out = {}
    for H in grid:
        if not adm: out[H] = []; continue
        costs = {r: lifecycle(adm[r], H, price) for r in adm}
        m = min(costs.values())
        out[H] = sorted(r for r, c in costs.items() if c == m)
    return out


# ----------------------------------------------------------------------------------------------------------- cells
DEPTHS = (1, 2, 3, 4, 5, 6)
WIDTHS = ((64, (7, 13, 23)), (128, (7,)))
K_ITEMS = 3

CELLS = {f"{law}_d{d}_D{D}_s{s}": {"law": law, "depth": d, "D": D, "k": K_ITEMS, "rec_seed": s}
         for law in LAWS for d in DEPTHS for D, seeds in WIDTHS for s in seeds}


def cell_report(spec, basis, seed=0, role_relabel=None, filler_relabel=None):
    eco = ecology(spec["D"], spec["depth"], spec["k"], spec["law"], seed=spec["rec_seed"],
                  role_relabel=role_relabel, filler_relabel=filler_relabel)
    out = {r: run(r, basis, eco, seed) for r in ROWS}
    return eco, out


def decide(out, price):
    """the kingdom question at one cell and one price vector: does the binding carrier occupy a frontier cell that NO
    parent row occupies at ANY reuse horizon of the extended grid?"""
    adm = {r: out[r] for r in ROWS if out[r]["admissible"]}
    cross = crossovers(adm, price)
    grid = grid_for(cross)
    front = frontier_of(adm, price, grid)
    occ = {r for H in grid for r in front[H]}
    parent_occ = sorted(occ & set(PARENT_ROWS))
    vsa_sole = sorted(H for H in grid if front[H] == ["VSA"])
    return {"admissible_rows": sorted(adm), "crossovers": {k: str(v) for k, v in cross.items()},
            "crossovers_decimal": {k: round(float(v), 4) for k, v in cross.items()},
            "grid": grid, "grid_max": max(grid), "dg2_grid_covers_twice_every_crossover": check_dg2(cross, grid),
            "frontier": {str(H): front[H] for H in grid}, "occupants": sorted(occ),
            "parent_occupants": parent_occ, "parent_occupies_some_cell": bool(parent_occ),
            "vsa_sole_occupant_horizons": vsa_sole,
            "kingdom_at_this_cell": bool(vsa_sole) and not parent_occ}




# ------------------------------------------------------------------------------------------------- closed forms
def closed_forms(law, depth, D):
    """the cost algebra written out, so every measured integer has an independently derived prediction (rule 11)."""
    b = D + IDX_BITS; Rd = R_ROLES ** depth; F = F_FILLERS; d = depth
    perm = 2 if law == "PERM" else 1  # charged D ops per composed role: XOR only, or PERMUTE + XOR
    return {
        "desc_VSA": (R_ROLES + F) * b,
        "desc_STORE_PATH": (Rd + F) * b,
        "desc_STORE_MAT": Rd * F * b,
        "compile_STORE_PATH": Rd * (d - 1) * perm * D,
        "compile_STORE_MAT": Rd * ((d - 1) * perm * D + F * D),
        "exec_VSA": (d + (d - 1) * (perm - 1)) * D + 2 * F * D + (F - 1),
        "exec_STORE_PATH": D + 2 * F * D + (F - 1),
        "exec_STORE_MAT": 2 * F * D + (F - 1),
        "GMI_DA3_H_star_assuming_R_pow_d_distinct_bindings": str(
            Fraction((Rd * F - (R_ROLES + F)) * b + Rd * F * D * d, d * D)),
    }


# ----------------------------------------------------------------------------------------------------- remint
def ir_genotypes(depth):
    """the carrier/law contrast written in the neutral morphology IR (gmi_microscope/morph.py), so that the
    distinction the kingdom question turns on can be checked for remint invariance (H5). The IR has no binding kind
    (the DG-1 family of gaps): GATE, the two-vector local transform, stands for the composite-carrier bind, and the
    eager parents differ from the carrier only in a STATE WIDTH parameter, which is the whole content of GMI-DA2."""
    from . import morph
    Rd = R_ROLES ** depth
    carrier = morph.make({0: ("INPUT", {"width": 64}), 1: ("DENSE", {"width": R_ROLES}), 2: ("GATE", {}),
                          3: ("KVSTORE", {"cap": F_FILLERS}), 4: ("NEAREST", {"k": 1, "metric": 0}), 5: ("OUTPUT", {})},
                         [(1, 2, 0), (0, 2, 1), (3, 4, 0), (2, 4, 1), (4, 5, 0)], meta={"row": "VSA"})
    store_path = morph.make({0: ("INPUT", {"width": 64}), 1: ("DENSE", {"width": Rd}), 2: ("GATE", {}),
                             3: ("KVSTORE", {"cap": F_FILLERS}), 4: ("NEAREST", {"k": 1, "metric": 0}), 5: ("OUTPUT", {})},
                            [(1, 2, 0), (0, 2, 1), (3, 4, 0), (2, 4, 1), (4, 5, 0)], meta={"row": "STORE_PATH"})
    store_mat = morph.make({0: ("INPUT", {"width": 64}), 1: ("KVSTORE", {"cap": Rd * F_FILLERS}),
                            2: ("NEAREST", {"k": 1, "metric": 0}), 3: ("OUTPUT", {})},
                           [(1, 2, 0), (0, 2, 1), (2, 3, 0)], meta={"row": "STORE_MAT"})
    return {"VSA": carrier, "STORE_PATH": store_path, "STORE_MAT": store_mat}


def remint_ir(depth):
    from . import morph
    gs = ir_genotypes(depth)
    out = {"typechecks": {}, "canonical_invariant_under_remint": {}, "fingerprint": {}, "mechanism_vector": {}}
    for name, g in gs.items():
        out["typechecks"][name] = bool(morph.typecheck(g))
        out["canonical_invariant_under_remint"][name] = all(
            morph.canonical(morph.remint(g, s)) == morph.canonical(g) for s in (1, 2, 3))
        out["fingerprint"][name] = morph.fingerprint(g)
        out["mechanism_vector"][name] = morph.mechanism_vector(g)
    out["fingerprints_all_distinct"] = len(set(out["fingerprint"].values())) == len(gs)
    out["carrier_and_path_parent_share_mechanism_vector"] = out["mechanism_vector"]["VSA"] == out["mechanism_vector"]["STORE_PATH"]
    out["carrier_and_materializing_parent_differ_in_mechanism_vector"] = out["mechanism_vector"]["VSA"] != out["mechanism_vector"]["STORE_MAT"]
    return out


REMINT_CELLS = ("XOR_d1_D64_s7", "PERM_d2_D64_s7", "PERM_d4_D64_s7")
ROLE_RELABEL = (2, 0, 3, 1)                       # declared nuisance relabelling of the role names
FILLER_RELABEL = (5, 2, 7, 0, 3, 6, 1, 4)          # declared nuisance relabelling of the filler names


def remint_instance(spec, basis, price="reduced", seed=0):
    """the executed instance-level remint: rename the roles and the fillers (and the codebook with them), which leaves
    every bound vector and every cue bit-identical and changes only the names. Capability, every charged coordinate
    and the whole frontier decision must be unchanged."""
    ea, a = cell_report(spec, basis, seed)
    eb, b = cell_report(spec, basis, seed, role_relabel=ROLE_RELABEL, filler_relabel=FILLER_RELABEL)
    cost_keys = ("n_queries", "R", "compile_ops", "exec_ops_total", "desc_bits", "hv_ops", "hv_compile_ops")
    costs = {r: all(a[r][k] == b[r][k] for k in cost_keys) for r in ROWS}
    caps = {r: a[r]["capability"] == b[r]["capability"] for r in ROWS}
    adms = {r: a[r]["admissible"] == b[r]["admissible"] for r in ROWS}
    sa = a["VSA"]["answer_signature"]; sb = b["VSA"]["answer_signature"]
    eq_a = {r: a[r]["answer_signature"] == sa for r in PARENT_ROWS}
    eq_b = {r: b[r]["answer_signature"] == sb for r in PARENT_ROWS}
    da, db = decide(a, price), decide(b, price)
    return {"per_row_charged_costs_identical": costs, "all_charged_costs_identical": all(costs.values()),
            "per_row_capability_identical": caps, "all_capability_identical": all(caps.values()),
            "all_admissibility_identical": all(adms.values()),
            "capability_delta_by_row": {r: round(b[r]["capability"] - a[r]["capability"], 4) for r in ROWS},
            "carrier_parent_equality_identical": eq_a == eq_b,
            "decision_identical": all(da[k] == db[k] for k in ("crossovers", "grid", "frontier", "occupants",
                                                               "parent_occupants", "vsa_sole_occupant_horizons",
                                                               "kingdom_at_this_cell")),
            "tied_cleanup_eval_queries": ea["tied_cleanup_eval_queries"],
            "note": "the declared cleanup tie-break is the SMALLEST filler index, so an exactly-tied cleanup is decided by the nuisance labelling; where capability moves under remint it moves IDENTICALLY in the carrier and in every materializing parent, which is the quantity the kingdom question turns on"}


# ------------------------------------------------------------------------------------------------------------ main
def main(tag="V1_DEPTH_GATED", seed=0, cells=None, out_path=None):
    basis = bases.ALL["B0_LOCAL_ADAPTIVE_TRANSDUCERS"]
    use = dict(CELLS) if cells is None else dict(cells)
    measured = {}; facts = {}; equality = {}; decisions = {}; forms = {}
    for cname, spec in use.items():
        eco, out = cell_report(spec, basis, seed)
        facts[cname] = {k: eco[k] for k in ("n_paths", "n_distinct_path_vectors", "n_classes",
                                            "ambiguous_eval_queries", "tied_cleanup_eval_queries")}
        facts[cname]["path_code_is_injective"] = eco["n_distinct_path_vectors"] == eco["n_paths"]
        forms[cname] = closed_forms(spec["law"], spec["depth"], spec["D"])
        sig = out["VSA"]["answer_signature"]
        equality[cname] = {f"VSA=={r}": out[r]["answer_signature"] == sig for r in PARENT_ROWS}
        equality[cname]["VSA==VSA_NOBIND"] = out["VSA_NOBIND"]["answer_signature"] == sig
        for r in ROWS: measured[f"{cname}|{r}"] = {k: v for k, v in out[r].items() if k not in ("row", "basis")}
        for price in ("reduced", "native"): decisions[f"{cname}|{price}"] = decide(out, price)

    # the depth law of the parent-maximal opponent, per (law, width, seed, price)
    depth_law = {}
    for law in LAWS:
        for D, seeds in WIDTHS:
            for s in seeds:
                if any(f"{law}_d{d}_D{D}_s{s}|reduced" not in decisions for d in DEPTHS): continue
                for price in ("reduced", "native"):
                    key = f"{law}|D{D}|s{s}|{price}"; series = {}
                    for d in DEPTHS:
                        dec = decisions[f"{law}_d{d}_D{D}_s{s}|{price}"]
                        hs = [Fraction(v) for k, v in dec["crossovers"].items()
                              if "VSA" in k.split("|") and set(k.split("|")) & set(PARENT_ROWS)]
                        series[d] = {"parent_maximal_crossover_H_star": str(min(hs)) if hs else None,
                                     "parent_maximal_crossover_H_star_decimal": round(float(min(hs)), 4) if hs else None,
                                     "admissible": "VSA" in dec["admissible_rows"],
                                     "parent_occupies_some_horizon": dec["parent_occupies_some_cell"]}
                    ratios = {}
                    for d in DEPTHS[1:]:
                        a, b = series[d - 1]["parent_maximal_crossover_H_star"], series[d]["parent_maximal_crossover_H_star"]
                        if a and b: ratios[f"{d - 1}->{d}"] = round(float(Fraction(b) / Fraction(a)), 4)
                    depth_law[key] = {"by_depth": series, "growth_ratio": ratios}

    rem_ir = remint_ir(3)
    rem_inst = {c: remint_instance(CELLS[c], basis, "reduced", seed) for c in REMINT_CELLS}

    kingdom_cells = sorted(c for c in decisions if decisions[c]["kingdom_at_this_cell"])
    d_star = min((use[c.split("|")[0]]["depth"] for c in kingdom_cells), default=None)
    max_depth = max(DEPTHS)
    terminal = (f"DEPTH_GATED_KINGDOM_ESTABLISHED_AT_SCOPE__D_STAR_{d_star}" if d_star is not None else
                f"NO_DEPTH_GATED_KINGDOM_AT_EXECUTED_DEPTHS__PARENT_MAXIMAL_OPPONENT_OCCUPIES_EVERY_CELL_TO_DEPTH_{max_depth}")

    receipt = {
        "schema": "StageDKDepthGatedV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422],
        "revival_record": "RV-377-065", "run_tag": tag,
        "question": "does the algebraic/binding carrier occupy a frontier cell that a PARENT-MAXIMAL exemplar-store opponent cannot occupy at ANY reuse horizon, at any executed structure depth?",
        "family": "E_rolefill(R = 4 roles, F = 8 fillers, structure depth d in 1..6, k = 3 bound items per record, 8 development records, 8 evaluation records on unseen structures)",
        "laws": {"XOR": "BIND = bitwise XOR (the law executed by RV-377-044 in gmi_microscope/dc_vsa.py); commutative and involutive, so a path composes to the PARITY of its role multiset",
                 "PERM": "BIND = bitwise XOR with the role at path position i protected by the cyclic shift rho^i (the PERMUTE primitive of DC1's declared native basis, GMI_DOMAIN_CANDIDATES_DC1_DC9_V1 section 2); distinct paths compose to distinct vectors"},
        "cell_definition": "a CELL is one (law, structure depth, hypervector width, record seed) configuration; a row OCCUPIES a cell when it is a frontier occupant at at least one reuse horizon of that cell's extended reuse grid",
        "frontier_rule": "PROTOCOL RULE 17, declared: a row occupies reuse horizon H of a cell iff (a) it is ADMISSIBLE there, i.e. its exact rational correct/total is >= theta = 85/100, and (b) its exact rational lifecycle C(H) is equal to the minimum C(H) over the admissible rows of that cell; ties occupy jointly. No largest-ladder-size rule is used: every row answers the same query set, so the frontier is the best-admissible-cost rule at a fixed obligation",
        "cost_model": "C = desc + H*exec_q + r*(upd_e + ver_e) + (r/4)*rev_e with r = 0 (this ecology registers no feedback, verification or revocation events), evaluated in exact rational arithmetic; theta = 0.85",
        "declared_prices": {"reduced": "charged Machine ops under basis B0: fixed = desc_bits + compile_ops, per query = exec_ops_total / n_queries",
                            "native": "one op per HYPERVECTOR operation (dc_vsa's hv_ops price): fixed = desc_bits with the parent's materialization UNPRICED, per query = hv_ops / n_queries. Leaving materialization unpriced is the dc_phase convention and is the PARENT-MAXIMAL reading, so the kingdom verdict is taken under the price that most favours the opponent"},
        "universe": {"TOTAL_BITS": 8, "FRAC_BITS": 4, "basis": basis.name, "theta": THETA,
                     "index_bits_per_stored_hypervector": IDX_BITS, "R_roles": R_ROLES, "F_fillers": F_FILLERS,
                     "codebook": "dc_vsa's, unchanged: LCG(1103515245, 12345), roles seed 1000+i, fillers seed 2000+j, tie vector seed 3000"},
        "parent_maximality_procedure": "PROTOCOL RULE 19 (gap DG-5). Four opponents are constructed adversarially rather than conveniently: STORE_MAT (RV-377-044's materializing store, generalized to depth d), STORE_PATH (materialize the path vectors only: smaller than STORE_MAT by a factor approaching F and still an exemplar store), STORE_DEDUP (materialize one bundle per DISTINCT path vector, with the class recovered from the path by a declared key program and the CHEAPEST representative used for materialization) and STORE_SEEN. PARENT_BEST, the opponent the verdict is taken against, is the pointwise minimum lifecycle over the admissible ones at each reuse horizon",
        "dg2_procedure": "GAP DG-2, fixed by construction. For every cell and every price vector the analytic crossover of every admissible pair is computed FIRST in exact rational arithmetic (crossovers()); the reuse grid is then built (grid_for()) to bracket every crossover from below and above AND to extend to at least 4x the largest crossover, hence past 2x it; check_dg2() asserts max(grid) >= 2 * max(crossover) for every cell and is reported per cell as dg2_grid_covers_twice_every_crossover",
        "rows": list(ROWS), "parent_rows": list(PARENT_ROWS), "cells_spec": use,
        "ecology_facts": facts, "closed_forms": forms,
        "cells": measured,
        "exact_developmental_equality": equality,
        "decisions": decisions, "depth_law_of_the_parent_maximal_opponent": depth_law,
        "remint_ir": rem_ir, "remint_instance": rem_inst,
        "kingdom_cells": kingdom_cells, "d_star": d_star, "terminal": terminal,
        "claim_ceiling": "exact charged replay at scope. The scope is one obligation family (role-filler binding), one primitive alphabet, one arithmetic instrument (8-bit fixed point, basis B0), two declared binding laws, six structure depths, two hypervector widths and three record seeds at the narrower width. Native prices are DECLARED, not measured. Capability is the only rounded quantity (correct/total to 4 places); admissibility and every frontier comparison are exact rationals, so no verdict depends on a floating-point tolerance. A negative kingdom verdict is a statement about the opponents constructed here: it can be overturned only by a carrier that beats all four, never by a weaker parent",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    path = out_path or os.path.join(RES, f"STAGE_DK_{tag}.json")
    json.dump(receipt, open(path, "w"), indent=1, sort_keys=True, default=str)
    for law in LAWS:
        if f"{law}|D64|s7|reduced" not in depth_law: continue
        print(law, "H*(d) parent-maximal, reduced, D64 s7:",
              {d: depth_law[f"{law}|D64|s7|reduced"]["by_depth"][d]["parent_maximal_crossover_H_star_decimal"] for d in DEPTHS})
        print("   admissible:", {d: depth_law[f"{law}|D64|s7|reduced"]["by_depth"][d]["admissible"] for d in DEPTHS},
              "| distinct path vectors:", {d: facts[f"{law}_d{d}_D64_s7"]["n_distinct_path_vectors"] for d in DEPTHS})
    print("terminal:", terminal)
    return receipt


if __name__ == "__main__":
    main(tag=sys.argv[1] if len(sys.argv) > 1 else "V1_DEPTH_GATED")

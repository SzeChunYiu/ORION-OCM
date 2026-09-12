"""RV-377-063: exact-layer ability test of the Codex-lane predicted form F4, the Interventional Quotient Learner
(IQL: value an intervention by the TARGET-SEMANTIC ambiguity it removes per charged burden, not by predictive surprise;
GMI_PREDICTED_MACHINE_INTELLIGENCE_FORMS_V1 section 5, kill condition
TARGET_QUOTIENT_INFORMATION_VALUE_ADDS_NO_PREDICTIVE_POWER_OVER_PARENT_ACTIVE_LEARNING_CRITERIA;
GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1 row B3-F4).

Ecology E_alias (declared, deterministic, no randomness anywhere):

  * TARGET LAYER. Five causal nodes v0..v4 on the FIXED undirected skeleton 0-1-2-3-4. A hypothesis's structure is the
    ORIENTATION d = (d0..d3) of the four edges (d_e = 0: node e -> node e+1; d_e = 1: node e+1 -> node e), so 16
    structures. Mechanism (declared): v_j = OR(parents of j) OR u_j, exogenous bits u all 0 in the resting regime.
  * OBSERVATIONAL ALIASING, exactly. The skeleton is connected and every edge is a copy, so in the resting regime
    EVERY one of the 16 orientations emits the identical observational record v = 00000. Observation alone therefore
    leaves the structure 16-fold ambiguous; only an intervention separates the aliases. This is the F4 premise built
    into the world rather than asserted about it.
  * NUISANCE LAYER. Two isolated nodes z0, z1 carry NO causal connection to the v layer at all.
  * READOUT BANK. n_w instrumented readouts sit on the declared attachment map `attach` (attach[k] names the node read
    by readout k). Readout k computes w_k = g_k(node) with an unknown unary map g_k in {ZERO, ID, NOT, ONE}, encoded as
    the bit pair (lo_k, hi_k) = (g_k(0), g_k(1)). The resting observation reveals every lo_k for free and no hi_k, so
    each readout carries exactly one residual bit, resolved only by driving its node to 1.
  * SERVING OBLIGATION (the target quotient S_O): the 25 interventional queries "under do(v_i = 1), what is v_j?".
    Their answers are a function of the ORIENTATION ALONE. The readout layer and the z nodes appear NOWHERE in the
    obligation, so the readouts attached to z are an exact PREDICTION-TARGET RESIDUAL: real, resolvable observational
    uncertainty with provably zero target value. The 16 orientations induce 16 distinct answer vectors (edge e's
    direction is read off from v_{e+1} under do(v_e = 1)), so target ambiguity starts at 16 in an aliased cell.
  * LEGAL INTERVENTIONS: do(v_i = 1) for i in 0..4 and do(z_r = 1) for r in 0..1 -- seven in all, each charged its
    declared price and each performed at most once (the world is deterministic, so a repeat returns no new record).
    Each returns the full record (v vector, readout vector). A DECLARED BUDGET B caps the number of interventions.
  * CAPABILITY: a row answers an obligation query only where ALL its remaining consistent hypotheses agree (else it
    abstains, F4.5); capability = fraction of the 25 queries answered correctly. theta = 0.85, so admissibility means
    the target quotient has been resolved to one answer vector.

VERSION SPACE (shared by every row, and the reason this is laptop-scale). The hypothesis space is the exact product
(orientation) x (residual readout bits), and every record factors the same way, so the machine carries the version
space FACTORED: a charged store of consistent orientations plus one charged known/unknown flag per readout. Under the
declared uniform prior this is exactly equivalent to enumerating the product, and the three value functionals reduce
to closed forms that the machine evaluates with charged ops (derivation in `value` docstrings). The factorization is
available to every row identically, so it cannot favour one.

Rows (identical machine, identical stop rule, identical evidence update, identical factored version space; they differ
ONLY in the functional that ranks the next intervention -- which is the entire F4 discriminator):

  IQL               (A_t - E[A_{t+1} | do j]) / c_j with A = the number of distinct TARGET ANSWER VECTORS still
                    consistent: target-semantic ambiguity reduction per unit charged burden (F4.3)
  PRED_UNCERTAINTY  (number of distinct predicted RECORDS of intervention j) / c_j: maximum predictive uncertainty
                    (uncertainty sampling) -- the standard active-learning parent, the row that must be beaten
  ENTROPY           (|Hs| - E[|Hs_{t+1}| | do j]) / c_j: generic version-space entropy reduction over the WHOLE
                    hypothesis space, structure and readout together
  RANDOM            a declared fixed intervention order; no scoring work at all
  IQL_NOAMBIG       THE NEGATIVE TWIN: the identical IQL machine with the ambiguity measure A replaced by the constant
                    1, so every numerator is 0 and only the declared tie-break (smallest index) survives

Cells -- the design isolates ALIASING from PREDICTION-TARGET RESIDUAL, one knob each:

  ALIAS_RESID     aliased target (16) + readout residual on both z nodes and on v2   -> the registered F4 regime
  ALIAS_NORESID   aliased target (16), readout bank EMPTY                            -> aliasing WITHOUT a residual
  NOALIAS_RESID   readout residual kept, but four declared NATURAL EXPERIMENTS (spontaneous activations at v0..v3,
                  observed at the v layer only and charged nothing) are handed over, so observation already identifies
                  the orientation                                                    -> the NO-ALIASING twin ecology

Every cell is run at ALL 16 ground-truth orientations (an exhaustive sweep, not a sample), at four declared budgets, at
two declared intervention price vectors, and in all seven registered price columns.

Declared instrument note (same convention as RV-377-031): the score comparison uses a WIDE integer accumulator --
numerators reach 2^U * |D|^2 and the registered fixed point saturates at 127 -- charged one INC activation per counted
orientation and MUL + MUL + GT per pairwise comparison, with the VALUE computed at unbounded integer precision. The
charging is real; only the 8-bit clamp is lifted, identically for every row.
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

N_V = 5
N_Z = 2
EDGES = tuple((i, i + 1) for i in range(N_V - 1))
ORIENTATIONS = list(itertools.product((0, 1), repeat=len(EDGES)))  # 16, fixed enumeration order
THETA = 0.85
LO_TRUTH = tuple((k * 3 + 1) % 2 for k in range(16))   # declared g_k(0), revealed free by the resting observation
HI_TRUTH = tuple((k * 5 + 1) % 2 for k in range(16))   # declared g_k(1): the residual bit of readout k
NATURAL_NODES = tuple(range(N_V - 1))                  # declared natural experiments of the no-aliasing twin

# an intervention is ("v", i) or ("z", r); declared enumeration order
INTERVENTIONS = [("v", i) for i in range(N_V)] + [("z", r) for r in range(N_Z)]
RANDOM_ORDER = (("v", 2), ("z", 0), ("v", 0), ("z", 1), ("v", 4), ("v", 1), ("v", 3))  # declared fixed order

# attachment maps: attach[k] is the node read by readout k
RESID_ATTACH = (("v", 2),) + (("z", 0),) * 4 + (("z", 1),) * 4   # 9 readouts: one on the target layer, eight nuisance
CELLS = {
    "ALIAS_RESID": {"attach": RESID_ATTACH, "natural": False},
    "ALIAS_NORESID": {"attach": (), "natural": False},
    "NOALIAS_RESID": {"attach": RESID_ATTACH, "natural": True},
}
BUDGETS = (2, 3, 4, 7)
# declared intervention price vectors; SKEW makes the two chain-end interventions cheap and the interior dear, so the
# "per unit charged burden" division of F4.3 can change the ranking rather than merely rescale it
INT_PRICES = {"UNIT": {("v", i): 1 for i in range(N_V)} | {("z", r): 1 for r in range(N_Z)},
              "SKEW": {("v", 0): 1, ("v", 1): 3, ("v", 2): 3, ("v", 3): 3, ("v", 4): 1} |
                      {("z", r): 1 for r in range(N_Z)}}
LAM_GRID_BASE = (0, 1, 4, 16, 64, 256, 1024)   # intervention retention prices; extended to every crossover (DG-2)


# ---------------------------------------------------------------- charged world model
def vvec(M, d, j):
    """v-vector under do(v_j = 1), exogenous bits 0: charged OR relaxation to the fixpoint (|EDGES| sweeps suffice)."""
    s = [0] * N_V
    s[j] = 1
    for _ in range(len(EDGES)):
        for e, (a, b) in enumerate(EDGES):
            src, dst = (a, b) if d[e] == 0 else (b, a)
            s[dst] = M.op("OR", s[dst], s[src])
    return tuple(s)


def target_vector(M, d):
    """the obligation's 25 answers under orientation d (charged)."""
    return tuple(itertools.chain.from_iterable(vvec(M, d, j) for j in range(N_V)))


def driven(M, iv, d_v):
    """which nodes are driven to 1 by intervention iv under a given v-pattern table: ('v', i) drives {i} u desc(i);
    ('z', r) drives z_r alone (the nuisance nodes are causally isolated, by construction)."""
    kind, idx = iv
    if kind == "v":
        return {("v", m) for m, bit in enumerate(d_v[idx]) if bit}
    return {("z", idx)}


# ---------------------------------------------------------------- rows
class Row:
    """The shared machine. The version space is carried FACTORED: a charged store of consistent orientations plus one
    charged known/unknown flag per readout. Subclasses supply ONLY `value`, the functional that ranks interventions."""

    row = "BASE"
    scores = True

    def __init__(self, attach, prices, budget):
        self.attach = attach
        self.prices = prices
        self.budget = budget

    def init(self, M, natural, truth_d):
        M.declare_store("orient")
        M.declare_program(14)
        for iv in INTERVENTIONS:
            M.declare(f"done_{iv[0]}{iv[1]}", "bool", 0)
        for k in range(len(self.attach)):
            M.declare(f"unk{k}", "bool", 1)      # the resting observation gave lo_k; hi_k is still unknown
        self.dv = {d: {j: vvec(M, d, j) for j in range(N_V)} for d in ORIENTATIONS}
        self.tgt = {d: target_vector(M, d) for d in ORIENTATIONS}
        for d in ORIENTATIONS:
            M.op("S_INSERT", "orient", d, 1)
        self.D = list(ORIENTATIONS)
        self.truth_d = truth_d
        self.n_int = 0
        self.burden_int = 0
        self.n_int_target = 0      # interventions spent on the target layer
        self.n_int_nuisance = 0    # interventions spent on the causally isolated nuisance layer
        if natural:   # declared natural experiments: spontaneous v-layer activations, observed free of charge
            for j in NATURAL_NODES:
                self._filter_orient(M, j)

    # ---- shared evidence update
    def _filter_orient(self, M, j):
        """keep the orientations whose v-record under a driving of node j matches the world's (one charged EQ each)."""
        want = self.dv[self.truth_d][j]
        keep = [d for d in self.D if M.op("EQ", self.dv[d][j], want)]
        if len(keep) != len(self.D):
            M.stores["orient"] = [(k, v) for k, v in M.stores["orient"] if k in set(keep)]
            M.op("S_DELETE", "orient", None)
        self.D = keep

    def _reveal(self, M, iv):
        """every readout attached to a node this intervention drives to 1 has its residual bit revealed."""
        dr = driven(M, iv, self.dv[self.truth_d])
        for k, node in enumerate(self.attach):
            if node in dr and M.read(f"unk{k}"):
                M.write(f"unk{k}", 0)

    def unknown_on(self, M, nodes):
        return [k for k, node in enumerate(self.attach) if node in nodes and M.read(f"unk{k}")]

    # ---- shared serving / stop rule
    def answers(self, M):
        """the common value where every consistent hypothesis agrees, else None (abstain, F4.5)."""
        out = []
        for q in range(N_V * N_V):
            vals = {self.tgt[d][q] for d in self.D}
            out.append(next(iter(vals)) if len(vals) == 1 else None)
        return out

    def capability(self, M):
        served = self.answers(M)
        want = self.tgt[self.truth_d]
        return sum(int(served[q] is not None and served[q] == want[q]) for q in range(N_V * N_V)) / (N_V * N_V)

    # ---- the partition an intervention would induce, in the factored representation
    def _partition(self, M, iv):
        """returns [(|D_p|, u_p)] -- the sizes of the target-layer blocks and the number of residual readout bits each
        block would reveal. For a nuisance intervention there is one target block (it splits no orientation)."""
        kind, idx = iv
        if kind == "z":
            u = len(self.unknown_on(M, {("z", idx)}))
            for _ in self.D:
                M.op("INC", 0)
            return [(len(self.D), u)]
        groups = {}
        for d in self.D:
            M.op("INC", 0)
            groups.setdefault(self.dv[d][idx], []).append(d)
        out = []
        for p, ds in groups.items():
            nodes = {("v", m) for m, bit in enumerate(p) if bit}
            out.append((len(ds), len(self.unknown_on(M, nodes))))
        return out

    def value(self, M, iv, parts, U):
        raise NotImplementedError

    def select(self, M):
        legal = [iv for iv in INTERVENTIONS if not M.read(f"done_{iv[0]}{iv[1]}")]
        if not legal:
            return None
        if not self.scores:
            return next(iv for iv in RANDOM_ORDER if iv in legal)
        U = sum(1 for k in range(len(self.attach)) if M.read(f"unk{k}"))
        num = {iv: self.value(M, iv, self._partition(M, iv), U) for iv in legal}
        best = legal[0]
        for iv in legal[1:]:     # num_iv / c_iv vs num_best / c_best, cross-multiplied on the wide instrument
            M.op("MUL", 0, 0); M.op("MUL", 0, 0); M.op("GT", 0, 0)
            if num[iv] * self.prices[best] > num[best] * self.prices[iv]:
                best = iv
        return best

    def intervene(self, M, iv):
        M.write(f"done_{iv[0]}{iv[1]}", 1)
        self.n_int += 1
        self.burden_int += self.prices[iv]
        if iv[0] == "v":
            self.n_int_target += 1
            self._filter_orient(M, iv[1])
        else:
            self.n_int_nuisance += 1
        self._reveal(M, iv)


class IQL(Row):
    """F4.3 executed. With the version space factored as D x {0,1}^U and a uniform prior, the expected posterior
    target ambiguity after do(j) is  E[A'] = sum_p (|D_p| / |D|) |D_p|, because the readout bits split blocks without
    splitting target classes. Scaling by |D| gives the integer numerator  |D|^2 - sum_p |D_p|^2  -- the target-layer
    Gini split. A nuisance intervention leaves one block, so its numerator is exactly 0."""

    row = "IQL"

    def ambiguity_weight(self, n):
        return n

    def value(self, M, iv, parts, U):
        n = len(self.D)
        acc = 0
        for size, _u in parts:
            M.op("INC", 0)
            acc += size * self.ambiguity_weight(size)
        return n * self.ambiguity_weight(n) - acc


class IQLNoAmbig(IQL):
    """THE NEGATIVE TWIN: the identical machine with the ambiguity measure replaced by the constant 1, so every
    numerator collapses to n*1 - sum_p size*1 = 0 and only the declared tie-break (first legal index) survives."""

    row = "IQL_NOAMBIG"

    def ambiguity_weight(self, n):
        return 1


class PredUncertainty(Row):
    """The parent that must be beaten: rank by the predictive uncertainty of the intervention's OWN record
    (uncertainty sampling / maximum expected information about the observable). In the factored representation the
    number of distinct predicted records is exactly sum_p 2^{u_p}, and the cardinality analogue of the uncertainty is
    that count MINUS ONE, so that an intervention whose record is already certain scores exactly 0 -- the same
    reduction form IQL and ENTROPY use. (Calibration note: scoring the raw count instead would hand the parent a
    positive value for a fully predictable intervention and lose it interventions it should never spend. The parent is
    given its strongest form here on purpose; the F4 discriminator is only worth reporting against that.)"""

    row = "PRED_UNCERTAINTY"

    def value(self, M, iv, parts, U):
        acc = 0
        for size, u in parts:
            M.op("INC", 0)
            acc += 1 << u
        return acc - 1


class EntropyRow(Row):
    """Generic version-space entropy reduction over the WHOLE hypothesis space (structure and readout together):
    |Hs|^2 - sum_blocks |block|^2 with |Hs| = |D| 2^U. A block is (p, an assignment of the u_p revealed bits) and has
    size |D_p| 2^{U-u_p}, so the sum is 2^{2U} sum_p |D_p|^2 2^{-u_p}. Scaled by 2^U to stay integral."""

    row = "ENTROPY"

    def value(self, M, iv, parts, U):
        n = len(self.D)
        acc = 0
        for size, u in parts:
            M.op("INC", 0)
            acc += size * size * (1 << (U - u))
        return n * n * (1 << U) - acc


class RandomRow(Row):
    row = "RANDOM"
    scores = False

    def value(self, M, iv, parts, U):
        return 0


ROWS = {r.row: r for r in (IQL, PredUncertainty, EntropyRow, RandomRow, IQLNoAmbig)}


# ---------------------------------------------------------------- one charged lifecycle
def run(row, basis, cell, price_name, budget, truth_d, seed=0):
    spec = CELLS[cell]
    ref = ROWS[row](spec["attach"], INT_PRICES[price_name], budget)
    M = Machine(basis, seed=seed)
    M.phase("exec")
    ref.init(M, spec["natural"], truth_d)
    caps = [round(ref.capability(M), 4)]
    order = []
    while ref.capability(M) < THETA and ref.n_int < budget:
        M.phase("ver")
        iv = ref.select(M)
        M.end_event()
        if iv is None:
            break
        M.phase("upd")
        ref.intervene(M, iv)
        M.end_event()
        order.append(f"{iv[0]}{iv[1]}")
        caps.append(round(ref.capability(M), 4))
    M.phase("exec")
    served = ref.answers(M)
    cap = ref.capability(M)
    desc_state = (sum(M.basis.desc_bits(M.cell_types[n]) for n in M.cells)
                  + sum(M.basis.desc_store_header + len(st) * M.basis.desc_store_entry for st in M.stores.values()))
    R = dict(M.L.c)
    return {"row": row, "basis": basis.name, "cell": cell, "price": price_name, "budget": budget,
            "truth_d": "".join(map(str, truth_d)),
            "R": R, "desc_state": desc_state, "capability": round(cap, 4), "admissible": cap >= THETA,
            "interventions": ref.n_int, "intervention_order": order,
            "interventions_on_target_layer": ref.n_int_target,
            "interventions_on_nuisance_layer": ref.n_int_nuisance,
            "intervention_burden": ref.burden_int,
            "scoring_ops": R["ver"], "update_ops": R["upd"], "exec_ops": R["exec"],
            "charged_total": R["desc"] + R["exec"] + R["upd"] + R["ver"] + R["rev"],
            "orientations_remaining": len(ref.D),
            "abstentions": sum(int(a is None) for a in served),
            "answer_signature": sha256_of(served),
            "capability_trace": caps}


def lifecycle(r, lam):
    """C = charged ops (declaration, scoring, evidence update, serving) + lam * charged intervention burden."""
    return r["charged_total"] + lam * r["intervention_burden"]


def crossovers(agg):
    """analytic lam* at which a pair's total burden crosses: lam* = (C_a - C_b) / (B_b - B_a)."""
    out = {}
    names = sorted(agg)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            db = agg[b]["intervention_burden"] - agg[a]["intervention_burden"]
            if db == 0:
                continue
            lam = (agg[a]["charged_total"] - agg[b]["charged_total"]) / db
            if lam > 0:
                out[f"{a}|{b}"] = round(lam, 4)
    return out


def grid_for(cross, base=LAM_GRID_BASE):
    """DG-2: the grid a frontier statement is checked on must extend past EVERY crossover that statement reports."""
    g = set(base)
    for lam in cross.values():
        g.add(max(0, int(math.floor(lam))))
        g.add(int(math.ceil(lam)) + 1)
        g.add(2 * int(math.ceil(lam)) + 2)
    return sorted(g)


def main(tag="V35_F4_IQL", seed=0, columns=None, cells=None, prices=None, budgets=None):
    cols = columns or dict(bases.ALL_HW)
    use = cells or dict(CELLS)
    pr = prices or dict(INT_PRICES)
    buds = budgets or BUDGETS
    out = {}
    for cell in use:
        for pname in pr:
            for B in buds:
                for d in ORIENTATIONS:
                    for row in ROWS:
                        for col in cols:
                            out[(cell, pname, B, "".join(map(str, d)), row, col)] = run(row, cols[col], cell, pname, B, d, seed)

    # C2: what the machine LEARNS (interventions, capability, served answers) must be column-invariant; only its price differs
    c2 = {}
    for (cell, pname, B, dk, row, _c) in list(out):
        key = f"{cell}|{pname}|B={B}|{dk}|{row}"
        if key in c2:
            continue
        sigs = {(out[(cell, pname, B, dk, row, c)]["interventions"], out[(cell, pname, B, dk, row, c)]["capability"],
                 out[(cell, pname, B, dk, row, c)]["answer_signature"]) for c in cols}
        c2[key] = len(sigs) == 1

    summary = {}
    for cell in use:
        for pname in pr:
            for B in buds:
                for col in cols:
                    for row in ROWS:
                        rs = [out[(cell, pname, B, "".join(map(str, d)), row, col)] for d in ORIENTATIONS]
                        ints = [r["interventions"] for r in rs]
                        summary[f"{cell}|{pname}|B={B}|{col}|{row}"] = {
                            "admissible_count": sum(int(r["admissible"]) for r in rs), "n_orientations": len(rs),
                            "mean_interventions": round(sum(ints) / len(ints), 4), "max_interventions": max(ints),
                            "mean_interventions_on_target_layer": round(sum(r["interventions_on_target_layer"] for r in rs) / len(rs), 4),
                            "mean_interventions_on_nuisance_layer": round(sum(r["interventions_on_nuisance_layer"] for r in rs) / len(rs), 4),
                            "mean_intervention_burden": round(sum(r["intervention_burden"] for r in rs) / len(rs), 4),
                            "mean_charged_total": round(sum(r["charged_total"] for r in rs) / len(rs), 4),
                            "mean_scoring_ops": round(sum(r["scoring_ops"] for r in rs) / len(rs), 4),
                            "mean_capability": round(sum(r["capability"] for r in rs) / len(rs), 4),
                            "admissible_all_orientations": all(r["admissible"] for r in rs)}

    # frontier over the intervention retention price lam, on a grid extending past every analytic crossover (DG-2).
    # Only rows admissible at EVERY ground-truth orientation may occupy the frontier.
    frontier = {}; cross_all = {}; grids = {}; occupants = {}
    for cell in use:
        for pname in pr:
            for B in buds:
                for col in cols:
                    agg = {}
                    for row in ROWS:
                        rs = [out[(cell, pname, B, "".join(map(str, d)), row, col)] for d in ORIENTATIONS]
                        if not all(r["admissible"] for r in rs):
                            continue
                        agg[row] = {"charged_total": sum(r["charged_total"] for r in rs) / len(rs),
                                    "intervention_burden": sum(r["intervention_burden"] for r in rs) / len(rs)}
                    key = f"{cell}|{pname}|B={B}|{col}"
                    cr = crossovers(agg); cross_all[key] = cr
                    g = grid_for(cr); grids[key] = g
                    for lam in g:
                        if not agg:
                            frontier[f"{key}|lam={lam}"] = []
                            continue
                        costs = {r: lifecycle(agg[r], lam) for r in agg}
                        frontier[f"{key}|lam={lam}"] = sorted(r for r, c in costs.items() if c <= min(costs.values()) + 1e-9)
                    occupants[key] = sorted({r for lam in g for r in frontier[f"{key}|lam={lam}"]})

    # the F4 discriminator read directly off the sweep
    disc = {}
    for cell in use:
        for pname in pr:
            for B in buds:
                for col in cols:
                    k = f"{cell}|{pname}|B={B}|{col}"
                    s = lambda row: summary[f"{k}|{row}"]
                    disc[k] = {
                        "iql_admissible": s("IQL")["admissible_count"], "pred_admissible": s("PRED_UNCERTAINTY")["admissible_count"],
                        "entropy_admissible": s("ENTROPY")["admissible_count"], "random_admissible": s("RANDOM")["admissible_count"],
                        "twin_admissible": s("IQL_NOAMBIG")["admissible_count"],
                        "iql_beats_pred_on_admissibility": s("IQL")["admissible_count"] > s("PRED_UNCERTAINTY")["admissible_count"],
                        "iql_ties_pred_on_admissibility": s("IQL")["admissible_count"] == s("PRED_UNCERTAINTY")["admissible_count"],
                        "iql_mean_interventions": s("IQL")["mean_interventions"], "pred_mean_interventions": s("PRED_UNCERTAINTY")["mean_interventions"],
                        "iql_mean_burden": s("IQL")["mean_intervention_burden"], "pred_mean_burden": s("PRED_UNCERTAINTY")["mean_intervention_burden"],
                        "iql_mean_charged_total": s("IQL")["mean_charged_total"], "pred_mean_charged_total": s("PRED_UNCERTAINTY")["mean_charged_total"],
                        "iql_beats_pred_on_charged_total": s("IQL")["mean_charged_total"] < s("PRED_UNCERTAINTY")["mean_charged_total"],
                        "pred_nuisance_interventions": s("PRED_UNCERTAINTY")["mean_interventions_on_nuisance_layer"],
                        "iql_nuisance_interventions": s("IQL")["mean_interventions_on_nuisance_layer"],
                        "twin_collapse": s("IQL_NOAMBIG")["admissible_count"] < s("IQL")["admissible_count"]}

    receipt = {
        "schema": "StageE1IQLV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422],
        "revival_record": "RV-377-063", "run_tag": tag,
        "codex_form": "F4 IQL (GMI_PREDICTED_MACHINE_INTELLIGENCE_FORMS_V1 section 5; protocol row B3-F4)",
        "ecology": "E_alias: five causal nodes on the fixed path skeleton 0-1-2-3-4 with unknown edge orientation (16 "
                   "structures) and the copy mechanism v_j = OR(parents) OR u_j, so the resting observation is v = 00000 "
                   "under EVERY orientation and observation aliases the target exactly; two causally isolated nuisance "
                   "nodes z0, z1 carry a readout bank whose residual bits are pure prediction-target residual; the "
                   "obligation is the 25 interventional queries do(v_i = 1) -> v_j, a function of the orientation alone",
        "cells_spec": {c: {"attach": [list(a) for a in v["attach"]], "n_readouts": len(v["attach"]),
                           "readouts_on_target_layer": sum(1 for a in v["attach"] if a[0] == "v"),
                           "readouts_on_nuisance_layer": sum(1 for a in v["attach"] if a[0] == "z"),
                           "natural_experiments": (list(NATURAL_NODES) if v["natural"] else []),
                           "hypotheses_at_start": len(ORIENTATIONS) * (1 << len(v["attach"])),
                           "target_classes_at_start": len(ORIENTATIONS)} for c, v in use.items()},
        "budgets": list(buds), "theta": THETA,
        "intervention_prices": {p: {f"{k[0]}{k[1]}": v for k, v in pr[p].items()} for p in pr},
        "interventions": [f"{k}{i}" for k, i in INTERVENTIONS],
        "random_order": [f"{k}{i}" for k, i in RANDOM_ORDER],
        "readout_truth": {"lo": list(LO_TRUTH[:len(RESID_ATTACH)]), "hi": list(HI_TRUTH[:len(RESID_ATTACH)])},
        "orientation_sweep": ["".join(map(str, d)) for d in ORIENTATIONS],
        "rows": list(ROWS), "columns": sorted(cols),
        "C2_column_invariance": c2,
        "cells": {"|".join(map(str, k)): {kk: vv for kk, vv in r.items() if kk not in ("row", "basis", "cell", "price", "budget")}
                  for k, r in out.items()},
        "summary_over_orientation_sweep": summary, "discriminator": disc,
        "analytic_crossovers": cross_all, "frontier_grids": grids, "frontier": frontier,
        "frontier_occupants_over_extended_grid": occupants,
        "version_space_note": "the hypothesis space is the exact product (orientation) x (residual readout bits) and every "
                              "record factors the same way, so the machine carries the version space factored (a charged "
                              "store of consistent orientations plus one charged known/unknown flag per readout). Under "
                              "the declared uniform prior this is exactly equivalent to enumerating the product; the "
                              "factorization is available identically to every row.",
        "wide_instrument_note": "score comparison uses a declared WIDE integer accumulator (numerators reach 2^U |D|^2; the "
                                "registered fixed point saturates at 127). One INC per counted orientation and MUL + MUL + GT "
                                "per pairwise comparison are charged; only the 8-bit clamp is lifted, identically for every "
                                "row (same convention as RV-377-031).",
        "claim_ceiling": "exact charged replay at scope; one declared skeleton, one declared readout truth, EXHAUSTIVE "
                         "16-orientation sweep, four declared budgets, two declared intervention price vectors, seven price "
                         "columns; every row deterministic (no randomness anywhere, so one seed is exhaustive). The "
                         "obligation is the interventional query set only: nothing is claimed about worlds where the "
                         "readout layer enters the serving obligation, where it would cease to be a residual."}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_E1_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)

    print("C2 all:", all(c2.values()))
    c0 = sorted(cols)[0]
    for cell in use:
        for pname in pr:
            for B in buds:
                print(f"== {cell} | {pname} | B={B} | {c0.split('_')[0]}")
                for row in ROWS:
                    s = summary[f"{cell}|{pname}|B={B}|{c0}|{row}"]
                    print(f"   {row:17s} adm {s['admissible_count']:2d}/{s['n_orientations']} n_int {s['mean_interventions']:5.3f} "
                          f"(tgt {s['mean_interventions_on_target_layer']:4.2f} nui {s['mean_interventions_on_nuisance_layer']:4.2f}) "
                          f"burden {s['mean_intervention_burden']:6.3f} charged {s['mean_charged_total']:9.1f} cap {s['mean_capability']:.4f}")
                print("   crossovers:", cross_all[f"{cell}|{pname}|B={B}|{c0}"])
                print("   occupants over extended grid:", occupants[f"{cell}|{pname}|B={B}|{c0}"])
    return receipt


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "calib":
        B0 = "B0_LOCAL_ADAPTIVE_TRANSDUCERS"
        main(tag="CALIB_F4_IQL_B0", columns={B0: bases.ALL_HW[B0]},
             cells={c: CELLS[c] for c in ("ALIAS_RESID", "ALIAS_NORESID")}, budgets=(3,))
    else:
        main()

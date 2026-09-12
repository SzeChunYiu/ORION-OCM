"""DC2 — self-organizing field carrier: exact microscope and bounded-reduction attack
(GMI_DOMAIN_CANDIDATES_DC1_DC9_V1.md section 2, record RV-377-046).

Carrier: a 1-D ring of L binary cells, s in {0,1}^L. Native law: one SYNCHRONOUS lattice update in which every site
applies THE SAME radius-1 local rule f: {0,1}^3 -> {0,1} (one of the 256 elementary cellular automata). The declared
native price is one op per STEP (one whole lattice update); the reduced price is L site updates, each charged at gate
level (5 ADD to form the 3-bit neighbourhood index + a 6-SEL mux into the 8-entry rule table = 11 ops per site).

Ecology E_spatial(L, T, rule, n_dev): development shows n_dev declared trajectories (an initial configuration and the
whole T-step orbit under the hidden rule), so a learner observes single-step transitions. Evaluation gives UNSEEN
initial configurations and demands the configuration after T steps exactly (a configuration is correct only if all L
bits are right). Development and evaluation configurations are disjoint by construction.

Rows (all charged exactly, all evaluated on the same unseen configurations, answers compared bit for bit):
  FIELD           search over the 256 elementary local rules; served state = THE RULE (8 bits). One rule is shared by
                  every site: translation equivariance / weight sharing is IN the carrier.
  FIELD_NONLOCAL  the negative twin: the SAME search over the SAME 256-entry hypothesis class, with the
                  translation-equivariance constraint REMOVED — every site carries its own independently searched
                  8-bit rule table (served state = 8L bits). Nothing else differs, so the FIELD/FIELD_NONLOCAL gap is
                  attributable to weight sharing alone.
  TABLE           the D2 parent: memorize the GLOBAL map (initial configuration -> configuration after T steps) as an
                  exact-key store with a charged linear scan. Must fail on unseen configurations.
  DENSE           the D1 parent: a coefficient row over the FLATTENED configuration — one linear threshold unit per
                  output site over all L inputs (no locality, no sharing), trained by a declared perceptron over the
                  single-step transitions and rolled out T steps. Description L*(L+1) integer coefficients.

Tie-break (declared, frozen): among the rules consistent with every observed transition, take the SMALLEST rule number.
Search realization (declared): the 256 candidates are filtered against the observed transitions with early exit at the
first mismatch; the surviving set is exactly the consistent set of the full search, so the served rule is identical to
the exhaustive search's, and the receipt reports `search_ops_exhaustive_analytic` alongside the executed op counts.

The scientific question: is the field carrier anything more than weight sharing under translation symmetry?
Measured: (a) the SAMPLE EFFICIENCY separation n*(FIELD) vs n*(FIELD_NONLOCAL) (smallest n_dev reaching theta),
(b) the DESCRIPTION separation 8L / 8 = L exactly, (c) exact developmental equality of the two rows' answers once both
are identified (the bounded reduction made executable), each reported as a function of L.
"""
from __future__ import annotations

import json
import math
import os
import sys

from . import bases
from .core import Machine, sha256_of
from .dc_energy import Arith

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
THETA = 0.85
N_RULES = 256
RULE_BITS = 8
PERCEPTRON_PASSES = 5
DENSE_TRAIN_CAP = 16  # declared budget cap: DENSE trains on at most the first 16 dev trajectories (disclosed; its
# capability is flat in n_dev over the executed range, which the receipt shows, and it is admissible nowhere)
PRECISION = "wide"  # DC2 uses the declared wide-integer instrument only: perceptron weights leave the 8-bit range


def lcg_bits(seed, n):
    """declared deterministic configuration generator (32-bit LCG, Numerical Recipes constants); one bit per draw.
    Identical generator to dc_vsa.lcg_bits, returned as a bit list."""
    x = (seed * 1103515245 + 12345) & 0xFFFFFFFF
    out = []
    for _ in range(n):
        x = (x * 1103515245 + 12345) & 0xFFFFFFFF
        out.append((x >> 16) & 1)
    return out


def true_step(rule, s):
    """uncharged reference dynamics used ONLY to build the ecology (the hidden rule's own orbit)."""
    L = len(s)
    return [(rule >> (4 * s[(i - 1) % L] + 2 * s[i] + s[(i + 1) % L])) & 1 for i in range(L)]


def ecology(L, T, rule, n_dev, n_eval=16, seed=17):
    dev, ev = [], []
    for n in range(n_dev):
        s0 = lcg_bits(seed * 1000 + n, L)
        traj = [s0]
        for _ in range(T): traj.append(true_step(rule, traj[-1]))
        dev.append(traj)
    for n in range(n_eval):
        s0 = lcg_bits(seed * 1000 + 500 + n, L)
        s = s0
        for _ in range(T): s = true_step(rule, s)
        ev.append((s0, s))
    seen = {tuple(t[0]) for t in dev}
    return {"L": L, "T": T, "rule": rule, "n_dev": n_dev, "n_eval": n_eval, "dev": dev, "eval": ev,
            "eval_initials_unseen": all(tuple(e[0]) not in seen for e in ev)}


# ------------------------------------------------------------------------------------------------ charged primitives
def _nbhd_index(M, s, i, L):
    """charged construction of the 3-bit neighbourhood index 4*l + 2*c + r (5 ADD)."""
    l, c, r = s[(i - 1) % L], s[i], s[(i + 1) % L]
    a = M.op("ADD", l, l)
    a = M.op("ADD", a, a)
    b = M.op("ADD", c, c)
    return M.op("ADD", M.op("ADD", a, b), r)


def _table_bit(M, rule, idx):
    """charged 8-entry table lookup as a multiplexer tree (6 SEL)."""
    b0 = M.op("SEL", idx & 1, (rule >> 1) & 1, rule & 1)
    b1 = M.op("SEL", idx & 1, (rule >> 3) & 1, (rule >> 2) & 1)
    b2 = M.op("SEL", idx & 1, (rule >> 5) & 1, (rule >> 4) & 1)
    b3 = M.op("SEL", idx & 1, (rule >> 7) & 1, (rule >> 6) & 1)
    # the three SEL levels are charged; the returned value is the exact table entry
    M.op("SEL", (idx >> 1) & 1, b1, b0)
    M.op("SEL", (idx >> 1) & 1, b3, b2)
    return (rule >> idx) & 1


def _step_shared(M, rule, s, L, counter):
    out = []
    for i in range(L):
        out.append(_table_bit(M, rule, _nbhd_index(M, s, i, L)))
    counter[0] += 1  # one STEP at the declared native price
    return out


def _step_per_site(M, rules, s, L, counter):
    out = []
    for i in range(L):
        out.append(_table_bit(M, rules[i], _nbhd_index(M, s, i, L)))
    counter[0] += 1
    return out


# ------------------------------------------------------------------------------------------------------------ rows
class Row:
    row = "?"

    def __init__(self, eco, arith=None): self.e = eco; self.native_ops = [0]; self.A = arith

    def init(self, M): pass

    def learn(self, M): pass

    def query(self, M, s0): raise NotImplementedError

    def desc_bits(self): return 0


class Field(Row):
    """search over the 256 elementary rules, one rule shared by every site (translation equivariance)."""
    row = "FIELD"

    def init(self, M): self.rule = 0; self.n_consistent = N_RULES

    def learn(self, M):
        L = self.e["L"]
        surv = []
        for cand in range(N_RULES):
            ok = True
            for traj in self.e["dev"]:
                for t in range(len(traj) - 1):
                    s, nxt = traj[t], traj[t + 1]
                    for i in range(L):
                        if not M.op("EQ", _table_bit(M, cand, _nbhd_index(M, s, i, L)), nxt[i]):
                            ok = False; break
                    if not ok: break
                if not ok: break
            if ok: surv.append(cand)
        self.n_consistent = len(surv)
        self.rule = surv[0] if surv else 0  # declared tie-break: smallest consistent rule number

    def query(self, M, s0):
        s = list(s0)
        for _ in range(self.e["T"]): s = _step_shared(M, self.rule, s, self.e["L"], self.native_ops)
        return s

    def desc_bits(self): return RULE_BITS


class FieldNonlocal(Row):
    """negative twin: the identical search, with weight sharing removed — one independent rule table per site."""
    row = "FIELD_NONLOCAL"

    def init(self, M): self.rules = [0] * self.e["L"]; self.n_consistent = [N_RULES] * self.e["L"]

    def learn(self, M):
        L = self.e["L"]
        for i in range(L):
            surv = []
            for cand in range(N_RULES):
                ok = True
                for traj in self.e["dev"]:
                    for t in range(len(traj) - 1):
                        if not M.op("EQ", _table_bit(M, cand, _nbhd_index(M, traj[t], i, L)), traj[t + 1][i]):
                            ok = False; break
                    if not ok: break
                if ok: surv.append(cand)
            self.n_consistent[i] = len(surv)
            self.rules[i] = surv[0] if surv else 0

    def query(self, M, s0):
        s = list(s0)
        for _ in range(self.e["T"]): s = _step_per_site(M, self.rules, s, self.e["L"], self.native_ops)
        return s

    def desc_bits(self): return RULE_BITS * self.e["L"]


class Table(Row):
    """the D2 parent: memorize the global T-step map; exact-key store with a charged linear scan."""
    row = "TABLE"

    def init(self, M): self.mem = []

    def learn(self, M):
        for traj in self.e["dev"]:
            self.mem.append((list(traj[0]), list(traj[-1])))

    def query(self, M, s0):
        L = self.e["L"]
        for key, val in self.mem:
            hit = 1
            for i in range(L):
                if not M.op("EQ", key[i], s0[i]): hit = 0; break
            if hit:
                self.native_ops[0] += 1
                return list(val)
        self.native_ops[0] += 1
        return list(s0)  # declared default on a miss: return the input unchanged

    def desc_bits(self): return len(self.mem) * 2 * self.e["L"]


class Dense(Row):
    """the D1 parent: one linear threshold unit per output site over the FLATTENED configuration (no locality, no
    sharing), trained by a declared perceptron over the single-step transitions, then rolled out T steps."""
    row = "DENSE"

    def init(self, M):
        L = self.e["L"]
        self.W = [[0] * L for _ in range(L)]
        self.b = [0] * L

    def _predict_site(self, M, j, xs):
        s = self.b[j]
        for i in range(self.e["L"]): s = self.A.add(s, self.A.mul(self.W[j][i], xs[i]))
        return 1 if self.A.gt(s, 0) else 0

    def learn(self, M):
        L = self.e["L"]
        pairs = [(t[k], t[k + 1]) for t in self.e["dev"][:DENSE_TRAIN_CAP] for k in range(len(t) - 1)]
        for _ in range(PERCEPTRON_PASSES):
            for s, nxt in pairs:
                xs = [2 * v - 1 for v in s]
                for j in range(L):
                    p = self._predict_site(M, j, xs)
                    if p != nxt[j]:
                        g = 1 if nxt[j] else -1
                        for i in range(L): self.W[j][i] = self.A.add(self.W[j][i], g * xs[i])
                        self.b[j] = self.A.add(self.b[j], g)

    def query(self, M, s0):
        L = self.e["L"]; s = list(s0)
        for _ in range(self.e["T"]):
            xs = [2 * v - 1 for v in s]
            s = [self._predict_site(M, j, xs) for j in range(L)]
            self.native_ops[0] += 1
        return s

    def desc_bits(self):
        L = self.e["L"]
        w = max(1, max((abs(v) for r in self.W for v in r), default=0))
        bits = max(2, int(math.ceil(math.log2(2 * w + 1))) + 1)
        return L * (L + 1) * bits


ROWS = {"FIELD": Field, "FIELD_NONLOCAL": FieldNonlocal, "TABLE": Table, "DENSE": Dense}


def search_ops_exhaustive_analytic(eco):
    """the declared exhaustive-search accounting: 256 candidates x every observed transition x L sites x 12 ops."""
    L, T, n = eco["L"], eco["T"], eco["n_dev"]
    return N_RULES * n * T * L * 12  # 11 evaluation ops + 1 EQ comparison per candidate/site


def run(row, basis, eco, seed=0, precision=PRECISION):
    M = Machine(basis, seed=seed); ref = ROWS[row](eco, Arith(M, precision))
    M.phase("exec"); ref.init(M)
    M.phase("upd"); ref.learn(M); M.end_event()
    learn = dict(M.L.c)
    M.phase("exec"); correct = 0; outs = []
    for s0, target in eco["eval"]:
        out = ref.query(M, s0); outs.append(tuple(out)); correct += int(out == target)
    cap = round(correct / len(eco["eval"]), 4)
    R = dict(M.L.c)
    d = {"row": row, "basis": basis.name, "precision": precision, "capability": cap, "admissible": cap >= THETA, "R": R,
         "learn_ops": learn["upd"], "exec_per_query": (R["exec"] - learn["exec"]) / len(eco["eval"]),
         "native_ops": ref.native_ops[0], "desc_bits": ref.desc_bits(), "n_queries": len(eco["eval"]),
         "answer_signature": sha256_of(outs)}
    if row == "FIELD": d["rule_served"] = ref.rule; d["n_consistent"] = ref.n_consistent
    if row == "FIELD_NONLOCAL":
        d["rules_served_distinct"] = len(set(ref.rules)); d["sites_identified"] = sum(1 for c in ref.n_consistent if c == 1)
        d["max_consistent_per_site"] = max(ref.n_consistent)
    return d


# ---------------------------------------------------------------------------------------------------------- cells
L_GRID = (8, 16, 32, 64)
T_STEPS = 3
RULE_GRID = (110, 30, 90, 232)
NDEV_GRID = (1, 2, 4, 8, 16, 32, 64, 128, 256)
CELLS = {f"L{L}_r{r}_n{n}": {"L": L, "T": T_STEPS, "rule": r, "n_dev": n} for L in L_GRID for r in RULE_GRID for n in NDEV_GRID}


def lifecycle(r, H, native=False):
    per_q = (r["native_ops"] / max(r["n_queries"], 1)) if native else r["exec_per_query"]
    return r["desc_bits"] + H * per_q + (0 if native else r["learn_ops"])


def crossovers(cellrows, price):
    """analytic reuse horizons at which each admissible pair of rows swaps order (DG-2: the grid must reach them)."""
    out = {}
    names = sorted(cellrows)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            ra, rb = cellrows[a], cellrows[b]
            nat = price == "native"
            fa = ra["desc_bits"] + (0 if nat else ra["learn_ops"]); fb = rb["desc_bits"] + (0 if nat else rb["learn_ops"])
            pa = (ra["native_ops"] / max(ra["n_queries"], 1)) if nat else ra["exec_per_query"]
            pb = (rb["native_ops"] / max(rb["n_queries"], 1)) if nat else rb["exec_per_query"]
            if pa == pb: continue
            h = (fb - fa) / (pa - pb)
            if h > 0: out[f"{a}|{b}"] = round(h, 4)
    return out


def grid_for(cross, base=(1, 16, 128, 1024)):
    """DG-2: the reuse grid must EXTEND BEYOND the analytic crossover of every price vector reported."""
    g = set(base)
    for h in cross.values():
        g.add(max(1, int(math.floor(h)))); g.add(int(math.ceil(h)) + 1); g.add(2 * int(math.ceil(h)) + 2)
    return sorted(g)


def main(tag="V30_DC2_FIELD", seed=0, cells=None):
    col = "B0_LOCAL_ADAPTIVE_TRANSDUCERS"; b = bases.ALL[col]
    use = cells if cells is not None else CELLS
    out = {}; ecos = {}
    for cname, spec in use.items():
        eco = ecology(spec["L"], spec["T"], spec["rule"], spec["n_dev"]); ecos[cname] = eco
        for rname in ROWS: out[(cname, rname)] = run(rname, b, eco, seed)
    # --- sample efficiency: smallest n_dev reaching theta, per (L, rule), per row
    sample_eff = {}
    for L in sorted({s["L"] for s in use.values()}):
        for r in sorted({s["rule"] for s in use.values()}):
            for rname in ROWS:
                ns = sorted(s["n_dev"] for c, s in use.items() if s["L"] == L and s["rule"] == r)
                star = None
                for n in ns:
                    c = f"L{L}_r{r}_n{n}"
                    if (c, rname) in out and out[(c, rname)]["admissible"]: star = n; break
                sample_eff[f"L{L}_r{r}|{rname}"] = star
    ratios = {}
    for L in sorted({s["L"] for s in use.values()}):
        for r in sorted({s["rule"] for s in use.values()}):
            f = sample_eff.get(f"L{L}_r{r}|FIELD"); nl = sample_eff.get(f"L{L}_r{r}|FIELD_NONLOCAL")
            ratios[f"L{L}_r{r}"] = {"n_star_field": f, "n_star_field_nonlocal": nl,
                                    "sample_efficiency_ratio": (None if (f in (None, 0) or nl is None) else round(nl / f, 4)),
                                    "desc_field": RULE_BITS, "desc_field_nonlocal": RULE_BITS * L,
                                    "description_ratio": L}
    # --- exact developmental equality with the weight-sharing-ablated parent, once both are identified
    equality = {c: out[(c, "FIELD")]["answer_signature"] == out[(c, "FIELD_NONLOCAL")]["answer_signature"] for c in use}
    identified = {c: {"field_n_consistent": out[(c, "FIELD")]["n_consistent"],
                      "nonlocal_sites_identified": out[(c, "FIELD_NONLOCAL")]["sites_identified"],
                      "nonlocal_sites_total": use[c]["L"],
                      "field_rule_served": out[(c, "FIELD")]["rule_served"], "true_rule": use[c]["rule"]} for c in use}
    # --- frontier over a reuse grid extended past every analytic crossover (DG-2)
    frontier = {}; cross_all = {}; grids = {}
    for cname in use:
        for price in ("reduced", "native"):
            adm = {r: out[(cname, r)] for r in ROWS if out[(cname, r)]["admissible"]}
            cr = crossovers(adm, price); cross_all[f"{cname}|{price}"] = cr
            g = grid_for(cr); grids[f"{cname}|{price}"] = g
            for H in g:
                if not adm: frontier[f"{cname}|{price}|H={H}"] = []; continue
                costs = {r: lifecycle(adm[r], H, native=(price == "native")) for r in adm}
                frontier[f"{cname}|{price}|H={H}"] = sorted(r for r, c in costs.items() if c <= min(costs.values()) + 1e-9)
    receipt = {"schema": "StageDC2FieldV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422],
               "revival_record": "RV-377-046", "run_tag": tag,
               "domain_candidate": "DC2 self-organizing field (cellular automata / reaction-diffusion)",
               "ecology": "E_spatial(L, T, rule, n_dev): ring of L cells; development shows n_dev whole T-step orbits under a hidden elementary rule; evaluation demands the exact configuration after T steps on UNSEEN initial configurations",
               "cells_spec": use, "theta": THETA, "precision_instrument": {"wide": "declared wide-integer instrument (gap G5): identical charged operation sequence at unbounded integer precision; DC2 needs it because perceptron weights leave the 8-bit range"},
               "declared_prices": {"native": "one op per STEP (a whole synchronous lattice update)", "reduced": "per site: 5 ADD (3-bit neighbourhood index) + 6 SEL (8-entry rule-table mux) = 11 ops; one STEP therefore costs 11L"},
               "search_realization": "the 256 candidates are filtered against every observed transition with early exit at the first mismatch; the surviving set equals the consistent set of the exhaustive search and the declared tie-break serves the SMALLEST consistent rule number",
               "search_ops_exhaustive_analytic": {c: search_ops_exhaustive_analytic(ecos[c]) for c in use},
               "rows": list(ROWS), "perceptron_passes": PERCEPTRON_PASSES, "dense_train_cap_trajectories": DENSE_TRAIN_CAP,
               "ecology_facts": {c: {"eval_initials_unseen": ecos[c]["eval_initials_unseen"], "n_eval": ecos[c]["n_eval"], "n_transitions_observed": use[c]["n_dev"] * T_STEPS} for c in use},
               "cells": {f"{c}|{r}": {k: v for k, v in d.items() if k not in ("row", "basis")} for (c, r), d in out.items()},
               "identification": identified, "field_equals_field_nonlocal_answers": equality,
               "sample_efficiency_n_star": sample_eff, "separation_by_L": ratios,
               "analytic_crossovers": cross_all, "frontier_grids": grids, "frontier": frontier,
               "claim_ceiling": "exact charged replay at scope; one declared configuration set per cell; two declared elementary rules; native prices are declared, not measured; the sample-efficiency numbers are n_dev thresholds on a declared grid {1,2,4,8,16,32} and are therefore resolved only to the next grid point"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_DC_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    for cname in use:
        print(cname, {r: out[(cname, r)]["capability"] for r in ROWS},
              "| field rule", out[(cname, "FIELD")]["rule_served"], "cons", out[(cname, "FIELD")]["n_consistent"],
              "| nl ident", out[(cname, "FIELD_NONLOCAL")]["sites_identified"], "/", use[cname]["L"],
              "| eq", equality[cname])
    print("sample efficiency n*:", {k: v for k, v in sample_eff.items() if "FIELD" in k})
    print("separation:", ratios)
    return receipt


if __name__ == "__main__":
    main(tag=sys.argv[1] if len(sys.argv) > 1 else "V30_DC2_FIELD")

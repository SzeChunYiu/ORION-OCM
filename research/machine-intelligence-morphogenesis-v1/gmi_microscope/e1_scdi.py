"""RV-377-064: exact-layer ability test of the Codex-lane predicted form F6, the Self-Compiling Developmental
Intelligence (SCDI: ONE authoritative developmental state, MANY disposable serving realizations compiled from it, with
a recompile policy that responds to the hardware price; GMI_PREDICTED_MACHINE_INTELLIGENCE_FORMS_V1 section 7, kill
condition SELF_COMPILATION_ADDS_NO_FRONTIER_VALUE_AFTER_PARENT_COMPILERS_AND_CACHES_RECEIVE_FIRST_REFUSAL;
GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1 row B3-F6).

Ecology: E_factored (gmi_microscope/e1_vlc, unchanged -- four linear factors over bit pairs, scope-2 queries, the
(1,1) pattern of every factor UNSEEN in development so that serving requires the learned linear structure and a raw
memory cannot generalize), served through up to FOUR declared serving regimes over the same latent factors:

    A  exact sum over the scope                     (the regime that carries the development labels)
    B  threshold: 1 iff the scope sum exceeds 0.75
    C  argmax: 1 iff the second factor of the scope exceeds the first
    D  quantized sum: the scope sum shifted right twice (a declared coarse-exactness serving obligation)

Development is labelled in regime A ONLY. The authority state is therefore richer than any one serving obligation
needs -- exactly F6.1 -- and regimes B, C and D are served by TRANSFER from it, never by their own labels.

PRICE VECTOR PER REGIME, and the price switch. Each serving regime is served under its own registered price column, and
the assignment ROTATES at every price switch: at epoch e regime g is served under COLUMN_CYCLE[(g + e) mod 4] with

    COLUMN_CYCLE = (HW_TENSOR_PRICED, B0 scan-store, B2 native-store, U uniform)

HW_TENSOR_PRICED prices dense arithmetic at 1 and a store activation at 8; the B0 scan-store column emulates a store
by linear scan; B2 makes the store native and emulates fixed-point arithmetic at gate level; U prices everything at 1.
The optimal serving realization is therefore NOT the same in every column, which is the whole F6 premise (F6.5,
"multiple serving morphologies may coexist") and the thing no single fixed form can track.

Rows:

  AUTH_INTERP        authority state + interpretation at every query; never compiles (the no-compiler control)
  UNIVERSAL          ONE universal serving model: a single table materialized over (regime, scope, pattern) for every
                     regime at once, with the authority state NOT retained -- the protocol's "one universal serving
                     model" parent. It cannot recompile, because there is nothing left to recompile from.
  AUTH_TABLE         authority state + per-regime compiled serving tables (the compiled serving realization itself)
  SCDI               authority state + a CHARGED POLICY PROBE that compiles the first regime's table, measures a real
                     lookup against a real interpretation in the column it is actually running in, and then either
                     keeps compiling or discards the probe and interprets. The discarded probe compile is charged: the
                     price of being self-compiling is paid, not assumed (F6.4 executed rather than asserted).
  SCDI_NORECOMPILE   THE NEGATIVE TWIN: the identical machine with the recompile policy removed -- the serving family
                     is PINNED to whatever the epoch-0 column chose and is never revisited when the price switches.
  RETRAIN            independently retrained models per regime: G separate learners, each developed from the SAME
                     number of development events but labelled in ITS OWN regime, with no shared authority state.

THE QUANTITY PREDICTED ANALYTICALLY BEFORE THE RUN is K*, the number of price switches at which recompiling beats
every fixed form. It is the same crossover family as RV-377-033 (compile amortization H*) and RV-377-038
(description-vs-replay H*): each row's lifetime cost is exactly affine in the switch count K,

    C_row(K, H) = desc_row + compile_row(K) + H * sum over epochs and active regimes of per_query(row, column)
                = a_row + b_row * K ,

so the crossover against a fixed form X is K*(SCDI, X) = (a_SCDI - a_X) / (b_X - b_SCDI), and the reported frontier
grid extends past every K* it reports (gap DG-2).

Laptop-scale, exactly reproducible, no randomness anywhere.
"""
from __future__ import annotations

import itertools
import json
import math
import os
import sys

from . import bases
from .core import Machine, clamp, fx, sha256_of
from .e1_vlc import COEFF_VALUES, DEV_EVENTS, EVAL_QUERIES, N_F, SCOPES, Learner, fbits, truth

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")

THETA = 0.85
TAU = fx(0.75)
REGIMES = ("A", "B", "C", "D")
G_GRID = (1, 2, 3, 4)
# declared price cycle: regime g is served under COLUMN_CYCLE[(g + epoch) % 4]
COLUMN_CYCLE = ("HW_TENSOR_PRICED", "B0_LOCAL_ADAPTIVE_TRANSDUCERS", "B2_REWRITABLE_TYPED_PROGRAM_GRAPH", "U_UNIFORM_UNIVERSAL")
H_HEAD = 64                       # headline queries per regime per epoch
K_GRID_BASE = (0, 1, 2, 4, 8, 16, 32)   # price switches; extended past every analytic crossover (DG-2)
PATTERNS = list(itertools.product((0, 1), repeat=4))   # the four bits of a scope's two factors, fixed order


def truth_regime(coeffs, x, s, regime):
    """the declared serving obligation of each regime over the same latent factors."""
    if regime == "A":
        return truth(coeffs, x, s)
    if regime == "B":
        return 1 if truth(coeffs, x, s) > TAU else 0
    if regime == "D":
        return truth(coeffs, x, s) >> 2
    a, b = s
    va = clamp(coeffs[a][0] * fbits(x, a)[0] + coeffs[a][1] * fbits(x, a)[1])
    vb = clamp(coeffs[b][0] * fbits(x, b)[0] + coeffs[b][1] * fbits(x, b)[1])
    return 1 if vb > va else 0


def x_of(scope, pat):
    """the input whose two in-scope factors carry the declared 4-bit pattern (out-of-scope bits 0)."""
    a, b = scope
    return (pat[0] << (2 * a)) | (pat[1] << (2 * a + 1)) | (pat[2] << (2 * b)) | (pat[3] << (2 * b + 1))


def pat_of(x, scope):
    a, b = scope
    return fbits(x, a) + fbits(x, b)


# ---------------------------------------------------------------- serving realizations
class Serving:
    """the two declared serving realization families, both compiled from / interpreting the SAME authority state."""

    @staticmethod
    def interp(M, L, x, s, regime):
        """serve by interpreting the authority state at query time (charged arithmetic)."""
        if regime == "C":
            a, b = s
            return 1 if M.op("GT", L.value(b, x), L.value(a, x)) else 0
        tot = clamp(sum(L.value(i, x) for i in s))
        if regime == "A":
            return tot
        if regime == "B":
            return 1 if M.op("GT", tot, TAU) else 0
        return M.op("SHR", M.op("SHR", tot))

    @staticmethod
    def compile_table(M, L, store, regime):
        """materialize a serving realization for one regime: 6 scopes x 16 patterns, each an interpreted value."""
        for si, s in enumerate(SCOPES):
            for pi, pat in enumerate(PATTERNS):
                M.op("S_INSERT", store, (regime, si, pi), Serving.interp(M, L, x_of(s, pat), s, regime))

    @staticmethod
    def lookup(M, store, x, s, regime):
        return M.op("S_LOOKUP", store, (regime, SCOPES.index(s), PATTERNS.index(pat_of(x, s))))


# ---------------------------------------------------------------- rows
class RowBase:
    row = "BASE"
    keeps_authority = True

    def __init__(self, regimes, pinned_family=None):
        self.regimes = regimes
        self.pinned_family = pinned_family
        self.family = {}
        self.compile_ops = 0
        self.probe_ops = 0
        self.discarded_compile_ops = 0

    def develop(self, M, coeffs):
        """the authority state: developed ONCE, from regime-A labels only."""
        self.L = Learner(M)
        M.declare_program(10)
        for x, s in DEV_EVENTS:
            M.phase("upd")
            self.L.observe(x, s, truth(coeffs, x, s))
            M.end_event()

    def build(self, M):
        raise NotImplementedError

    def query(self, M, x, s, regime):
        raise NotImplementedError


class AuthInterp(RowBase):
    row = "AUTH_INTERP"

    def build(self, M):
        for g in self.regimes:
            self.family[g] = "INTERP"

    def query(self, M, x, s, regime):
        return Serving.interp(M, self.L, x, s, regime)


class AuthTable(RowBase):
    row = "AUTH_TABLE"

    def build(self, M):
        M.declare_store("serve")
        before = dict(M.L.c)
        for g in self.regimes:
            Serving.compile_table(M, self.L, "serve", g)
            self.family[g] = "TABLE"
        self.compile_ops = sum(M.L.c[k] - before[k] for k in M.L.c)

    def query(self, M, x, s, regime):
        return Serving.lookup(M, "serve", x, s, regime)


class Universal(RowBase):
    """ONE universal serving model over every regime at once, with the authority state NOT retained: after the
    materialization the learner's cells and evidence store are released, so there is nothing to recompile from."""

    row = "UNIVERSAL"
    keeps_authority = False

    def build(self, M):
        M.declare_store("serve")
        before = dict(M.L.c)
        for g in self.regimes:
            Serving.compile_table(M, self.L, "serve", g)
            self.family[g] = "TABLE"
        self.compile_ops = sum(M.L.c[k] - before[k] for k in M.L.c)
        M.stores["evidence"] = []      # the authority state is discarded: this row cannot recompile
        M.op("S_DELETE", "evidence", None)
        self.released = [n for n in list(M.cells) if n[0] in "ac" and n[1:].isdigit()]

    def query(self, M, x, s, regime):
        return Serving.lookup(M, "serve", x, s, regime)


class SCDI(RowBase):
    """F6.4 executed. The policy COMPILES the first regime's serving table, then measures a real lookup against a real
    interpretation IN THE COLUMN IT IS RUNNING IN and decides. If interpretation wins the probe compile is discarded --
    and charged, because a self-compiling machine really does pay for the realizations it decides not to keep."""

    row = "SCDI"

    def build(self, M):
        M.declare_store("serve")
        probe_regime = self.regimes[0]
        before = dict(M.L.c)
        Serving.compile_table(M, self.L, "serve", probe_regime)
        probe_compile = sum(M.L.c[k] - before[k] for k in M.L.c)
        x0, s0 = EVAL_QUERIES[0]
        b1 = sum(M.L.c.values()); Serving.lookup(M, "serve", x0, s0, probe_regime); c_table = sum(M.L.c.values()) - b1
        b2 = sum(M.L.c.values()); Serving.interp(M, self.L, x0, s0, probe_regime); c_interp = sum(M.L.c.values()) - b2
        measure_ops = sum(M.L.c.values()) - b1
        keep_table = not M.op("GT", c_table, c_interp)       # charged decision
        if keep_table:
            before2 = dict(M.L.c)
            for g in self.regimes[1:]:
                Serving.compile_table(M, self.L, "serve", g)
            self.compile_ops = probe_compile + sum(M.L.c[k] - before2[k] for k in M.L.c)
            for g in self.regimes:
                self.family[g] = "TABLE"
        else:
            M.stores["serve"] = []
            M.op("S_DELETE", "serve", None)
            self.discarded_compile_ops = probe_compile
            self.compile_ops = probe_compile
            for g in self.regimes:
                self.family[g] = "INTERP"
        # the probe charge is the measurement plus, when the probe is discarded, the compile it threw away
        self.probe_ops = measure_ops + self.discarded_compile_ops

    def query(self, M, x, s, regime):
        if self.family[regime] == "TABLE":
            return Serving.lookup(M, "serve", x, s, regime)
        return Serving.interp(M, self.L, x, s, regime)


class SCDINoRecompile(SCDI):
    """THE NEGATIVE TWIN: the identical machine with the recompile policy removed. The serving family is PINNED to the
    declared epoch-0 choice and never revisited, so the price probe is not run and the price switch is not answered."""

    row = "SCDI_NORECOMPILE"

    def build(self, M):
        pin = self.pinned_family
        fams = {g: (pin.get(g, "INTERP") if isinstance(pin, dict) else pin) for g in self.regimes}
        tabled = [g for g in self.regimes if fams[g] == "TABLE"]
        if tabled:
            M.declare_store("serve")
            before = dict(M.L.c)
            for g in tabled:
                Serving.compile_table(M, self.L, "serve", g)
            self.compile_ops = sum(M.L.c[k] - before[k] for k in M.L.c)
        self.family = fams


class Retrain(RowBase):
    """independently retrained models per regime: G separate learners, each given the SAME development events but
    labelled in its OWN regime, with no shared authority state and therefore no transfer."""

    row = "RETRAIN"

    def develop(self, M, coeffs):
        self.Ls = {}
        M.declare_program(10 * len(self.regimes))
        for g in self.regimes:
            self.Ls[g] = Learner(M, prefix=f"{g}_")
            for x, s in DEV_EVENTS:
                M.phase("upd")
                self.Ls[g].observe(x, s, truth_regime(coeffs, x, s, g))
                M.end_event()
        self.L = self.Ls[self.regimes[0]]

    def build(self, M):
        for g in self.regimes:
            self.family[g] = "INTERP"

    def query(self, M, x, s, regime):
        return Serving.interp(M, self.Ls[regime], x, s, regime)


ROWS = {r.row: r for r in (AuthInterp, Universal, AuthTable, SCDI, SCDINoRecompile, Retrain)}


# ---------------------------------------------------------------- one charged lifecycle in one column
def run(row, basis, G, pinned_family=None, seed=0):
    regimes = REGIMES[:G]
    ref = ROWS[row](regimes, pinned_family)
    M = Machine(basis, seed=seed)
    coeffs = [(COEFF_VALUES[(2 * i) % 4], COEFF_VALUES[(2 * i + 1) % 4]) for i in range(N_F)]
    M.phase("exec")
    ref.develop(M, coeffs)
    M.phase("upd")
    ref.build(M)
    M.end_event()
    dev_and_build = dict(M.L.c)
    per_regime = {}
    answers_all = []
    M.phase("exec")
    for g in regimes:
        before = sum(M.L.c.values())
        outs = [ref.query(M, x, s, g) for x, s in EVAL_QUERIES]
        ops = sum(M.L.c.values()) - before
        want = [truth_regime(coeffs, x, s, g) for x, s in EVAL_QUERIES]
        cap = sum(int(o is not None and o == w) for o, w in zip(outs, want)) / len(want)
        per_regime[g] = {"capability": round(cap, 4), "admissible": cap >= THETA,
                         "exec_per_query": ops / len(EVAL_QUERIES),
                         "family": ref.family[g], "answer_signature": sha256_of(outs)}
        answers_all.append(outs)
    desc_state = (sum(M.basis.desc_bits(M.cell_types[n]) for n in M.cells)
                  + sum(M.basis.desc_store_header + len(st) * M.basis.desc_store_entry for st in M.stores.values()))
    R = dict(M.L.c)
    caps = [per_regime[g]["capability"] for g in regimes]
    return {"row": row, "basis": basis.name, "G": G,
            "R": R, "R_development_and_build": dev_and_build, "desc_state": desc_state,
            "compile_ops": ref.compile_ops, "probe_ops": ref.probe_ops,
            "discarded_compile_ops": ref.discarded_compile_ops,
            "families": dict(ref.family),
            "per_regime": per_regime,
            "min_capability": round(min(caps), 4), "mean_capability": round(sum(caps) / len(caps), 4),
            "admissible": all(per_regime[g]["admissible"] for g in regimes),
            "exec_per_query": sum(per_regime[g]["exec_per_query"] for g in regimes) / len(regimes),
            "answer_signature": sha256_of(answers_all)}


# ---------------------------------------------------------------- the price-switch schedule, composed exactly
def family_of(measured, row, G, g, col, epoch0_col):
    """which serving realization `row` uses for regime g when g is currently priced in `col`.

    SCDI answers the price (it picks the family its charged probe preferred IN THAT COLUMN); the negative twin is
    pinned to whatever the regime's EPOCH-0 column chose and never revisits it; the parents are fixed by construction."""
    if row in ("UNIVERSAL", "AUTH_TABLE"):
        return "TABLE"
    if row in ("AUTH_INTERP", "RETRAIN"):
        return "INTERP"
    if row == "SCDI":
        return measured[("SCDI", col, G)]["families"][g]
    return measured[("SCDI", epoch0_col, G)]["families"][g]     # SCDI_NORECOMPILE


def serve_cost(measured, G, g, col, family):
    """the charged per-query cost of serving regime g in column `col` out of the named realization family."""
    src = "AUTH_TABLE" if family == "TABLE" else "AUTH_INTERP"
    return measured[(src, col, G)]["per_regime"][g]["exec_per_query"]


def schedule_cost(measured, row, G, K, H):
    """C_row(K, H) = desc + (build charges actually incurred) + H * sum over epochs e in 0..K and active regimes g of
    the per-query cost of the family this row serves g with, priced in COLUMN_CYCLE[(g + e) mod 4].

    BUILD CHARGES. F6.4 makes the cache part of the form, so a compiled realization that is still valid (the authority
    state has not changed) is NOT rebuilt when the price rotates back to a column already visited: SCDI pays one
    charged probe per DISTINCT column it meets and one compile per (regime, column) pair it actually decides to
    materialize. The negative twin builds once, at epoch 0. The fixed parents build once, at epoch 0. Charging SCDI a
    fresh probe and a fresh compile every epoch instead would be a strawman of the form, not of the parents."""
    regimes = REGIMES[:G]
    cyc = COLUMN_CYCLE
    ep0 = {g: cyc[gi % len(cyc)] for gi, g in enumerate(regimes)}
    total = measured[(row, cyc[0], G)]["desc_state"]
    built = set()
    seen_cols = set()
    for e in range(K + 1):
        for gi, g in enumerate(regimes):
            col = cyc[(gi + e) % len(cyc)]
            fam = family_of(measured, row, G, g, col, ep0[g])
            if row == "SCDI":
                if col not in seen_cols:      # one charged policy probe per distinct price vector met
                    seen_cols.add(col)
                    total += measured[("SCDI", col, G)]["probe_ops"]
                key = (g, col)
                if fam == "TABLE" and key not in built:
                    built.add(key)
                    total += measured[("AUTH_TABLE", col, G)]["compile_ops"] / G
            elif e == 0 and fam == "TABLE" and g not in built:
                built.add(g)
                total += measured[("AUTH_TABLE", ep0[g], G)]["compile_ops"] / G
            total += H * serve_cost(measured, G, g, col, fam)
    return total


AFFINE_FIT_RANGE = (len(COLUMN_CYCLE), 2 * len(COLUMN_CYCLE))


def affine(measured, row, G, H):
    """(a, b) with C_row(K) = a + b K, fitted on AFFINE_FIT_RANGE.

    Every row's cost is exactly affine in K once each row has met every column it will ever build for, i.e. for
    K >= len(COLUMN_CYCLE) - 1; below that the build charges are still accumulating. The fit is therefore taken across
    one full cycle inside the exact regime, and every crossover reported from it names that range (gap DG-3)."""
    k0, k1 = AFFINE_FIT_RANGE
    c0 = schedule_cost(measured, row, G, k0, H)
    c1 = schedule_cost(measured, row, G, k1, H)
    b = (c1 - c0) / (k1 - k0)
    return c0 - b * k0, b


def crossovers(measured, rows, G, H):
    """K*(a, b) = (a_a - a_b) / (b_b - b_a): the switch count at which the pair's lifetime costs cross."""
    ab = {r: affine(measured, r, G, H) for r in rows}
    out = {}
    names = sorted(rows)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            db = ab[b][1] - ab[a][1]
            if abs(db) < 1e-12:
                continue
            k = (ab[a][0] - ab[b][0]) / db
            if k > 0:
                out[f"{a}|{b}"] = round(k, 4)
    return out, {r: {"a": round(ab[r][0], 4), "b_per_switch": round(ab[r][1], 4)} for r in ab}


def grid_for(cross, base=K_GRID_BASE):
    """DG-2: a frontier statement is checked only on a grid whose largest point exceeds every crossover it reports."""
    g = set(base)
    for k in cross.values():
        g.add(max(0, int(math.floor(k))))
        g.add(int(math.ceil(k)) + 1)
        g.add(2 * int(math.ceil(k)) + 2)
    return sorted(g)


def main(tag="V36_F6_SCDI", seed=0, gs=None, H=H_HEAD, pinned_family=None, cols=None):
    use_g = gs or G_GRID
    cycle = cols or COLUMN_CYCLE
    # the twin's pin is the family SCDI's policy chooses in the declared epoch-0 column
    pin = pinned_family or {g: run("SCDI", bases.ALL_HW[cycle[gi % len(cycle)]], use_g[-1])["families"][g]
                            for gi, g in enumerate(REGIMES[:use_g[-1]])}
    measured = {}
    for G in use_g:
        for col in cycle:
            for row in ROWS:
                measured[(row, col, G)] = run(row, bases.ALL_HW[col], G, pin, seed)

    # C2: what a row LEARNS and SERVES must be column-invariant; only its price may differ
    c2 = {}
    for G in use_g:
        for row in ROWS:
            sigs = {measured[(row, c, G)]["answer_signature"] for c in cycle}
            caps = {measured[(row, c, G)]["min_capability"] for c in cycle}
            c2[f"G={G}|{row}"] = len(sigs) == 1 and len(caps) == 1

    # exact developmental equality of every row's served answers against each parent, per regime
    equality = {}
    for G in use_g:
        for col in cycle:
            for row in ROWS:
                for g in REGIMES[:G]:
                    equality[f"G={G}|{col}|{row}|{g}"] = {
                        "answer_signature": measured[(row, col, G)]["per_regime"][g]["answer_signature"],
                        "equals_AUTH_INTERP": (measured[(row, col, G)]["per_regime"][g]["answer_signature"]
                                               == measured[("AUTH_INTERP", col, G)]["per_regime"][g]["answer_signature"]),
                        "equals_UNIVERSAL": (measured[(row, col, G)]["per_regime"][g]["answer_signature"]
                                             == measured[("UNIVERSAL", col, G)]["per_regime"][g]["answer_signature"]),
                        "equals_RETRAIN": (measured[(row, col, G)]["per_regime"][g]["answer_signature"]
                                           == measured[("RETRAIN", col, G)]["per_regime"][g]["answer_signature"]),
                        "capability": measured[(row, col, G)]["per_regime"][g]["capability"]}

    frontier = {}; cross_all = {}; grids = {}; occupants = {}; affines = {}
    for G in use_g:
        adm = [r for r in ROWS if all(measured[(r, c, G)]["admissible"] for c in cycle)]
        cr, ab = crossovers(measured, adm, G, H) if adm else ({}, {})
        key = f"G={G}|H={H}"
        cross_all[key] = cr; affines[key] = ab
        grid = grid_for(cr); grids[key] = grid
        for K in grid:
            if not adm:
                frontier[f"{key}|K={K}"] = []
                continue
            costs = {r: schedule_cost(measured, r, G, K, H) for r in adm}
            frontier[f"{key}|K={K}"] = sorted(r for r, c in costs.items() if c <= min(costs.values()) + 1e-9)
        occupants[key] = sorted({r for K in grid for r in frontier[f"{key}|K={K}"]})

    receipt = {
        "schema": "StageE1SCDIV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422],
        "revival_record": "RV-377-064", "run_tag": tag,
        "codex_form": "F6 SCDI (GMI_PREDICTED_MACHINE_INTELLIGENCE_FORMS_V1 section 7; protocol row B3-F6)",
        "ecology": "E_factored (gmi_microscope/e1_vlc, unchanged) served through up to four declared regimes over the same "
                   "latent factors; development is labelled in regime A only, so B/C/D are served by transfer from the "
                   "authority state and never from their own labels",
        "cells_spec": {"regimes": {"A": "exact scope sum", "B": "1 iff scope sum > 0.75", "C": "1 iff second factor exceeds first",
                                   "D": "scope sum shifted right twice"},
                       "G_grid": list(use_g), "column_cycle": list(cycle),
                       "price_switch": "at epoch e regime g is served under COLUMN_CYCLE[(g + e) mod 4]",
                       "H_per_regime_per_epoch": H, "theta": THETA,
                       "eval_queries": len(EVAL_QUERIES), "table_entries_per_regime": len(SCOPES) * len(PATTERNS),
                       "twin_pinned_family_by_regime": pin,
                       "affine_fit_range_in_K": list(AFFINE_FIT_RANGE)},
        "rows": list(ROWS), "columns": list(cycle),
        "C2_column_invariance": c2,
        "cells": {f"G={G}|{col}|{row}": {k: v for k, v in measured[(row, col, G)].items() if k not in ("row", "basis", "G")}
                  for (row, col, G) in measured},
        "developmental_equality": equality,
        "affine_cost_model": affines, "analytic_crossovers": cross_all, "frontier_grids": grids,
        "frontier": frontier, "frontier_occupants_over_extended_grid": occupants,
        "crossover_family_note": "each row's lifetime cost is exactly affine in the price-switch count K, so "
                                 "K*(a,b) = (a_a - a_b)/(b_b - b_a) is the same crossover family as RV-377-033's compile "
                                 "amortization H* and RV-377-038's description-vs-replay H*; the reported grid extends "
                                 "past every K* it reports (gap DG-2).",
        "claim_ceiling": "exact charged replay at scope; one declared ecology, four declared serving regimes, one declared "
                         "four-column price cycle, one declared development schedule labelled in regime A only; every row "
                         "deterministic (one seed is exhaustive). The schedule composition prices each epoch from the "
                         "measured per-column coordinates of that row: it is exact for the declared cycle and claims "
                         "nothing about schedules that are not a rotation of it."}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_E1_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)

    print("C2 all:", all(c2.values()), "| twin pin by regime:", pin)
    for G in use_g:
        print(f"== G={G}")
        for row in ROWS:
            m = measured[(row, cycle[0], G)]
            fams = {c: measured[(row, c, G)]["families"][REGIMES[0]] for c in cycle}
            print(f"   {row:17s} cap_min {m['min_capability']:.4f} adm_all_cols "
                  f"{all(measured[(row, c, G)]['admissible'] for c in cycle)!s:5s} desc {m['desc_state']:6d} "
                  f"compile {m['compile_ops']:8d} pq " +
                  " ".join(f"{c.split('_')[0]}={measured[(row, c, G)]['exec_per_query']:8.2f}" for c in cycle) +
                  f" fam {[fams[c] for c in cycle]}")
        print("   affine (a, b per switch):", affines[f"G={G}|H={H}"])
        print("   crossovers K*:", cross_all[f"G={G}|H={H}"])
        print("   grid:", grids[f"G={G}|H={H}"])
        print("   occupants over extended grid:", occupants[f"G={G}|H={H}"])
    return receipt


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "calib":
        main(tag="CALIB_F6_SCDI", gs=(2,))
    else:
        main()

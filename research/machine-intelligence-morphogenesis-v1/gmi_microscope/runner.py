"""Protocol runner: executes a reference row under a basis column on the size ladder and returns the
phenotype Phi = (Q table, D table, R vector, S observables) plus per-coordinate overhead kappa
against the parent's own accounting.

Registered protocol (frozen): H = 8 feedback events on the binding target T(x) = BINDING_TARGET;
after each event the row is queried on every x in X_DOMAIN (D table row); a registered
verification (compare all 4 outputs to the target, charged on 'ver') after every event; one
revocation of the t=2 example at t=5 (charged on 'rev'). Feedback content is the row's native
channel: exact_counterexample gets (x, y); likelihood_score gets (x, y) with a fixed likelihood
model; scalar_loss gets (x, y) and computes its own loss; an inert row ignores feedback.
"""
from __future__ import annotations

import math

from .core import COORDS, Machine
from .references import ROWS, X_DOMAIN

H = 8
REVOKE_AT = 5
BINDING_TARGET = {0: 1, 1: 0, 2: 1, 3: 1}  # frozen target mapping; not linearly separable in (bit1, bit0)
SCHEDULE = [0, 1, 2, 3, 0, 1, 2, 3]  # x presented at events t=1..8


def classify_locality(frac: float, n_cells: int) -> str:
    if frac == 0.0:
        return "NONE"
    if frac * n_cells <= 2.0:
        return "LOCAL_O1"
    if frac < 0.5:
        return "SPARSE_SUBLINEAR"
    return "DENSE_LINEAR"


def theta_type(M: Machine) -> str:
    types = set(M.cell_types.values())
    if "fx" in types and (types - {"fx"}):
        return "MIXED"
    if "fx" in types:
        return "BOUNDED_NUMERIC"
    return "DISCRETE_FINITE"


def run(row_name: str, basis, size: int, seed: int = 0) -> dict:
    ref = ROWS[row_name](size)
    M = Machine(basis, seed=seed)
    M.phase("exec")
    ref.init(M)
    if hasattr(ref, "snapshot_initial"):
        ref.snapshot_initial(M)
    desc_after_init = M.L.c["desc"]
    Q = {}
    D = []
    per_phase = []
    changed_by_channel = set()
    max_writes = 0
    for t in range(1, H + 1):
        x = SCHEDULE[t - 1]
        y = BINDING_TARGET[x]
        before = dict(M.L.c)
        # queries (D table)
        M.phase("exec")
        Qt = {xx: ref.query(M, xx) for xx in X_DOMAIN}
        if t == 1:
            Q = dict(Qt)
        D.append(Qt)
        # feedback event
        M.phase("upd")
        cells_before = dict(M.cells)
        ref.feedback(M, x, y)
        wrote = len(M.L.writes_in_event)
        max_writes = max(max_writes, wrote)
        M.end_event()
        if any(cells_before.get(k) != v for k, v in M.cells.items()) or wrote:
            changed_by_channel.add(ref.fb_channel)
        # verification
        M.phase("ver")
        for xx in X_DOMAIN:
            M.op("EQ", ref.query(M, xx), BINDING_TARGET[xx])
        # revocation
        if t == REVOKE_AT:
            M.phase("rev")
            ref.revoke(M, SCHEDULE[1])
            M.end_event()
        after = dict(M.L.c)
        per_phase.append({c: after[c] - before[c] for c in COORDS})
    M.phase("exec")
    final = {xx: ref.query(M, xx) for xx in X_DOMAIN}
    D.append(final)
    R = dict(M.L.c)
    n_cells = len(M.cells) + sum(len(s) for s in M.stores.values())
    loc_frac = max(M.L.event_write_fracs) if M.L.event_write_fracs else 0.0
    S = {
        "theta_type": theta_type(M),
        "update_locality": classify_locality(loc_frac, n_cells),
        "max_event_write_fraction": loc_frac,
        "feedback_dependence": sorted(c for c in changed_by_channel if c),
        "execution_shape": ref.declared["execution_shape"],
        "store_discipline": ref.declared["store_discipline"],
        "n_state_cells": n_cells,
        "max_cells_written_per_event": max_writes,
    }
    capability = sum(int(final[xx] == BINDING_TARGET[xx]) for xx in X_DOMAIN) / len(X_DOMAIN)
    pc = ref.parent_cost()
    # per-event parent totals over the protocol (same event counts as the run)
    parent_total = {
        "desc": pc["desc"],
        "exec": pc["exec"] * 4 * (H + 1),
        "upd": None if pc["upd"] is None else pc["upd"] * H,
        "ver": pc["ver"] * H,
        "rev": None if pc["rev"] is None else pc["rev"] * 1,
    }
    kappa = {}
    for c in COORDS:
        if parent_total[c] in (None, 0):
            kappa[c] = {"absolute": R[c], "parent": parent_total[c]}
        else:
            kappa[c] = round(R[c] / parent_total[c], 4)
    return {
        "row": row_name, "basis": basis.name, "size": size,
        "Q": Q, "D": D, "R": R, "S": S, "capability": capability,
        "parent_cost_model": pc, "parent_total": parent_total, "kappa": kappa,
        "per_event": per_phase, "desc_after_init": desc_after_init,
        "native_ops": M.L.native_ops, "emulated_ops": M.L.emulated_ops,
        "flat_table_entries_log2": round(math.log2(ref.flat_table_entries()), 2),
    }

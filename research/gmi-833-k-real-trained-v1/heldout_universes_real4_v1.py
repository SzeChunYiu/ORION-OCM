"""SIGMA_REAL4 and the set-valued bridge SB-L* (FREEZE_V1.md sections 3.2-3.4).

Created AFTER the freeze commit 233bb38a504f7ba10a1a75578840c0416b2e5c0d and
BEFORE any SIGMA_REAL4 training exists.  The parent modules of
``gmi-833-capability-predictor-evaluation-v1`` are imported, never edited.

The bridge is NOT hand-authored: ``derive_bridge`` applies the frozen
commitment rule CR-1 to the parent's three real receipts and ``FROZEN_SB_TABLE``
is what FREEZE_V1.md section 3.3 says that derivation must return.  A
disagreement between the two is a package failure, not a table edit.

Python 3.8 compatible, stdlib only, exact ``Fraction`` arithmetic.
"""

from fractions import Fraction
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EVAL_PKG = os.path.join(os.path.dirname(HERE), "gmi-833-capability-predictor-evaluation-v1")
if EVAL_PKG not in sys.path:
    sys.path.insert(0, EVAL_PKG)

import heldout_universes_v1 as hu  # noqa: E402

FREEZE_COMMIT = "233bb38a504f7ba10a1a75578840c0416b2e5c0d"

UNSOLVED = 0
SOLVED = 1
BAND = Fraction(99, 100)

REAL4_MECHS = ("MLP", "GRU")
REAL4_SIZES = (6, 48)
REAL4_HEADS = (1, 3, 5, 7)
REAL4_RHO3_BASE = 15
REAL4_K_THRESHOLD = 12          # k = 2 iff GRU and size >= 12 (FREEZE_V1 3.4)
REAL4_BAND = BAND

REAL4_GRID = {
    "budgets": ((6, 1, 2, 15), (48, 2, 3, 16), (48, 2, 4, 16)),
    "charges": ((0, 0, 0, 0), (1, 0, 0, 0)),
    "d_values": (10, 14, 99),
    "b_values": (0, 8, 16, 24, 32),
    "h_values": ("NO_OBSERVATION", (1, 0), (2, 1)),
    "tau_values": (Fraction(3, 17), Fraction(8, 17), Fraction(11, 17), Fraction(1)),
}

RECEIPTS = (
    os.path.join(EVAL_PKG, "REAL_RUNS", "REAL_MEASURED_V1.json"),
    os.path.join(EVAL_PKG, "REAL_RUNS_V2", "REAL_MEASURED_V2.json"),
    os.path.join(EVAL_PKG, "REAL_RUNS_V3", "REAL_MEASURED_V3.json"),
)

# What FREEZE_V1.md section 3.3 says CR-1 must derive from the receipts.
FROZEN_SB_TABLE = {
    "untrained": "UNSOLVED",
    "T0_trained": "SOLVED",
    "MLP_T1_trained": "UNSOLVED",
    "MLP_T2_trained": "UNSOLVED",
    "GRU_T1_threshold": 12,
    "GRU_T2_threshold": None,
}
MIN_HEADS = 4
MIN_WIDTHS = 2


# --------------------------------------------------------------------------
# CR-1: derive the bridge from the parent's receipts
# --------------------------------------------------------------------------


def load_receipt_rows(paths=RECEIPTS):
    """(mech, size, w, task, trained_acc, untrained_acc) for every measured head."""
    rows = []
    for path in paths:
        with open(path) as handle:
            payload = json.load(handle)
        for key, acc in payload["per_head_exact_accuracy"].items():
            mech, size, w, task = key.split("|")
            rows.append((mech, int(size), int(w), int(task),
                         Fraction(acc["trained"]), Fraction(acc["untrained"])))
    rows.sort()
    return rows


def _unanimous(heads, band_value):
    """heads: list of (size, is_solved).  Unanimous at band_value with the
    registered minimum support?"""
    if len(heads) < MIN_HEADS:
        return False
    if len(set(s for s, _ in heads)) < MIN_WIDTHS:
        return False
    return all((sol == (band_value == SOLVED)) for _, sol in heads)


def derive_bridge(rows=None):
    rows = load_receipt_rows() if rows is None else rows
    table = {}
    evidence = {}

    untrained = [(r[1], r[5] >= BAND) for r in rows]
    n_untr_solved = sum(1 for _, s in untrained if s)
    table["untrained"] = "UNSOLVED" if n_untr_solved == 0 else "ABSTAIN"
    evidence["untrained"] = {"heads": len(untrained), "solved": n_untr_solved,
                             "max_untrained_acc": str(max(r[5] for r in rows))}

    t0 = [(r[1], r[4] >= BAND) for r in rows if r[3] == 0]
    table["T0_trained"] = "SOLVED" if _unanimous(t0, SOLVED) else "ABSTAIN"
    evidence["T0_trained"] = {"heads": len(t0), "solved": sum(1 for _, s in t0 if s),
                              "widths": sorted(set(s for s, _ in t0))}

    for j in (1, 2):
        mlp = [(r[1], r[4] >= BAND) for r in rows if r[0] == "MLP" and r[3] == j]
        key = "MLP_T%d_trained" % j
        table[key] = "UNSOLVED" if _unanimous(mlp, UNSOLVED) else "ABSTAIN"
        evidence[key] = {"heads": len(mlp), "solved": sum(1 for _, s in mlp if s),
                         "widths": sorted(set(s for s, _ in mlp)),
                         "max_trained_acc": str(max(r[4] for r in rows
                                                    if r[0] == "MLP" and r[3] == j))}

    for j in (1, 2):
        gru = [(r[1], r[4] >= BAND) for r in rows if r[0] == "GRU" and r[3] == j]
        widths = sorted(set(s for s, _ in gru))
        threshold = None
        for s_star in widths:
            above = [(s, sol) for s, sol in gru if s >= s_star]
            if _unanimous(above, SOLVED):
                threshold = s_star
                break
        key = "GRU_T%d_threshold" % j
        table[key] = threshold
        evidence[key] = {
            "heads": len(gru),
            "per_width": dict((str(s), [sum(1 for ss, sol in gru if ss == s and sol),
                                        sum(1 for ss, _ in gru if ss == s)])
                              for s in widths),
        }
    return table, evidence


def bridge_matches_freeze(table):
    return table == FROZEN_SB_TABLE


# --------------------------------------------------------------------------
# Band intervals and admissible sets under a bridge table
# --------------------------------------------------------------------------


def band_interval(table, machine, j):
    """Interval of admissible bands for head j of machine, as a tuple of band
    values: (UNSOLVED,), (SOLVED,) or (UNSOLVED, SOLVED)."""
    mech, size, w, h = machine
    if not (h >> j) & 1:
        return (UNSOLVED,) if table["untrained"] == "UNSOLVED" else (UNSOLVED, SOLVED)
    if j == 0:
        return (SOLVED,) if table["T0_trained"] == "SOLVED" else (UNSOLVED, SOLVED)
    if mech == "MLP":
        v = table["MLP_T%d_trained" % j]
        if v == "UNSOLVED":
            return (UNSOLVED,)
        if v == "SOLVED":
            return (SOLVED,)
        return (UNSOLVED, SOLVED)
    threshold = table["GRU_T%d_threshold" % j]
    if threshold is not None and size >= threshold:
        return (SOLVED,)
    return (UNSOLVED, SOLVED)


def admissible_bits(table, machine):
    """Sorted tuple of admissible solved-bit vectors (the product of intervals)."""
    out = []
    for bands in itertools.product(*(band_interval(table, machine, j) for j in range(3))):
        bits = 0
        for j, b in enumerate(bands):
            if b == SOLVED:
                bits |= 1 << j
        out.append(bits)
    return tuple(sorted(out))


def proto_admissible_bits(machine):
    """CB-PROTO: every subset of the trained heads (the parent lane's bridge)."""
    h = machine[3]
    return tuple(b for b in range(8) if not (b & ~h))


def cap_of_bits(mu, verified, bits):
    total = Fraction(0)
    for j in range(3):
        if verified[j] and ((bits >> j) & 1):
            total += mu[j]
    return total


def value_set(mu, verified, bits_tuple):
    return frozenset(cap_of_bits(mu, verified, b) for b in bits_tuple)


def committed_cells(table, machines):
    """(machine index, head) pairs whose interval is a singleton."""
    out = []
    for i, m in enumerate(machines):
        for j in range(3):
            if len(band_interval(table, m, j)) == 1:
                out.append((i, j))
    return tuple(out)


# --------------------------------------------------------------------------
# The population
# --------------------------------------------------------------------------


def real4_descriptor(machine):
    mech, size, w, h = machine
    if mech == "MLP":
        k = 0
    elif size < REAL4_K_THRESHOLD:
        k = 1
    else:
        k = 2
    rho = [0] * hu.RHO_DIM_HELDOUT
    rho[0] = size
    rho[1] = 1 + w
    rho[2] = 1 + hu.popcount(h)
    rho[3] = REAL4_RHO3_BASE + (1 if mech == "GRU" else 0)
    dev = size + hu.popcount(h) + w + (2 if mech == "GRU" else 0)
    obs = (1 + w, 1 if mech == "GRU" else 0)
    return k, tuple(rho), dev, obs


def build_sigma_real4():
    raw = []
    machines = []
    for mech in REAL4_MECHS:
        for size in REAL4_SIZES:
            for w in (0, 1):
                for h in REAL4_HEADS:
                    machines.append((mech, size, w, h))
    for machine in machines:
        k, rho, dev, obs = real4_descriptor(machine)
        raw.append((machine[1], machine[2], machine[3], k, rho, dev, obs))
    order = sorted(range(len(raw)),
                   key=lambda i: (raw[i][4][0], raw[i][4][3], raw[i][0],
                                  raw[i][1], raw[i][2]))
    rank = [0] * len(raw)
    for pos, idx in enumerate(order):
        rank[idx] = pos
    return tuple(raw), tuple(rank), tuple(machines)


REAL4_RAW, REAL4_RANK, REAL4_MACHINES = build_sigma_real4()


def min_world_law(table):
    """Placeholder point law = the least admissible bit vector of each machine.
    Used ONLY to satisfy make_spec's CAP slot; no claim reads it.  Route B
    installs explicit worlds; route A never reads CAP."""
    def law(machine):
        return admissible_bits(table, machine)[0]
    return law


def sigma_real4(table=None):
    if table is None:
        table, _ev = derive_bridge()
    return hu.make_spec("SIGMA_REAL4", REAL4_RAW, REAL4_RANK, REAL4_MACHINES,
                        hu.MU_REAL, min_world_law(table), REAL4_GRID,
                        lambda rec: rec[1] == 0)


def spec_with_world(base_spec, machines, world):
    """A fresh registration surface whose CAP is the given world's table."""
    spec = dict(base_spec)
    cap = {}
    for contract in base_spec["CONTRACTS"]:
        verified = hu.VERIFIED[contract]
        cap[contract] = tuple(cap_of_bits(hu.MU_REAL, verified, world[i])
                              for i in range(len(machines)))
    spec["CAP"] = cap
    spec["_CEILING_CACHE"] = {}
    return spec


def clean_spec(spec):
    return dict((k, v) for k, v in spec.items() if not k.startswith("__"))


def machine_key(machine):
    return "|".join(str(x) for x in machine)


if __name__ == "__main__":
    table, evidence = derive_bridge()
    print(json.dumps({"derived": table, "matches_freeze": bridge_matches_freeze(table),
                      "evidence": evidence}, indent=1, sort_keys=True))

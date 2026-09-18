"""SIGMA_REAL3 -- second registered revival of the real-system row.

`heldout_universes_v1.py` and `heldout_universes_v2.py` are left byte-identical.

Diagnosis after V2 (single stage, still the registration law -- now its
MEASUREMENT PREDICATE): `solved := exact accuracy 1 on the protected split` sits
inside the optimization noise band of these systems. `(GRU,16,w=0)` reached
1981/2000 on ones-mod-3 -- 19 items short of exact -- while `(GRU,16,w=1)`
reached exactly 1 on parity, so the V2 "no skip shortcut" clause and the
exact-equality predicate are both refuted by the same population.

Lever (two parts, both pre-registered here):
1. band the measurement away from the threshold: a task counts as solved iff
   exact accuracy >= 99/100, which is the #903 banded-classification discipline;
2. move the structural threshold from width >= 8 to width >= 16, which is where
   the V1+V2 evidence actually places the accumulator that SGD finds.

Re-tested prospectively on a third population at widths 12 and 32, which neither
earlier population contains.
"""

from fractions import Fraction
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import heldout_universes_v1 as hu  # noqa: E402

REAL3_MECHS = ("MLP", "GRU")
REAL3_SIZES = (12, 32)
REAL3_HEADS = (1, 3, 5, 7)
REAL3_WIDTH_THRESHOLD = 16
REAL3_BAND = Fraction(99, 100)


def real3_solved_law(machine):
    mech, size, w, h = machine
    capable = (mech == "GRU" and size >= REAL3_WIDTH_THRESHOLD)
    bits = 0
    if h & 1:
        bits |= 1
    if (h & 2) and capable:
        bits |= 2
    if (h & 4) and capable:
        bits |= 4
    return bits


def real3_descriptor(machine):
    mech, size, w, h = machine
    if mech == "MLP":
        k = 0
    elif size < REAL3_WIDTH_THRESHOLD:
        k = 1
    else:
        k = 2
    rho = [0] * hu.RHO_DIM_HELDOUT
    rho[0] = size
    rho[1] = 1 + w
    rho[2] = 1 + hu.popcount(h)
    rho[3] = 9 + (1 if mech == "GRU" else 0)
    dev = size + hu.popcount(h) + w + (2 if mech == "GRU" else 0)
    obs = (1 + w, 1 if mech == "GRU" else 0)
    return k, tuple(rho), dev, obs


def build_sigma_real3():
    raw = []
    machines = []
    for mech in REAL3_MECHS:
        for size in REAL3_SIZES:
            for w in (0, 1):
                for h in REAL3_HEADS:
                    machines.append((mech, size, w, h))
    for machine in machines:
        k, rho, dev, obs = real3_descriptor(machine)
        raw.append((machine[1], machine[2], machine[3], k, rho, dev, obs))
    order = sorted(range(len(raw)),
                   key=lambda i: (raw[i][4][0], raw[i][4][3], raw[i][0],
                                  raw[i][1], raw[i][2]))
    rank = [0] * len(raw)
    for pos, idx in enumerate(order):
        rank[idx] = pos
    return tuple(raw), tuple(rank), tuple(machines)


REAL3_GRID = {
    "budgets": ((12, 1, 2, 9), (32, 2, 3, 10), (32, 2, 4, 10)),
    "charges": ((0, 0, 0, 0), (1, 0, 0, 0)),
    "d_values": (14, 20, 99),
    "b_values": (0, 8, 16, 24, 32),
    "h_values": ("NO_OBSERVATION", (1, 0), (2, 1)),
    "tau_values": (Fraction(3, 17), Fraction(8, 17), Fraction(11, 17), Fraction(1)),
}

REAL3_RAW, REAL3_RANK, REAL3_MACHINES = build_sigma_real3()


def sigma_real3():
    return hu.make_spec("SIGMA_REAL3", REAL3_RAW, REAL3_RANK, REAL3_MACHINES,
                        hu.MU_REAL, real3_solved_law, REAL3_GRID,
                        lambda rec: rec[1] == 0)

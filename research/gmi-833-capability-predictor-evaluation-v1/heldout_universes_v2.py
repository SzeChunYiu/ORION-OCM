"""SIGMA_REAL2 -- the registered revival set for the real-system row.

`heldout_universes_v1.py` is left byte-identical to its frozen form; this
module only adds a new, disjoint population and an amended registration law.

Diagnosis behind the revival (single stage): the V1 registered law
`real_solved_law` over-predicted.  It asserted that parity is solved by any
recurrent system *or* any width >= 8 system, and that ones-mod-3 is solved by
any width >= 8 system.  Measured V1 outcomes falsify both: at the registered
training budget only `(GRU, 8, w=0)` reaches exact accuracy on parity and on
ones-mod-3, and the very same architecture with the last-symbol skip feature
(`w = 1`) does not.  The failing stage is therefore the registration law, not
the training budget -- the budget was demonstrably sufficient for `(GRU,8,0)` --
and not `F`, which was never consulted about training.

Lever: amend the law to require recurrence AND width AND the absence of the
skip shortcut, then re-test PROSPECTIVELY on a new population of systems that
the V1 outcomes did not contain (widths 4 and 16 instead of 2 and 8).  The
training protocol is unchanged, so the amendment cannot be a budget rescue.
"""

from fractions import Fraction
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import heldout_universes_v1 as hu  # noqa: E402

REAL2_MECHS = ("MLP", "GRU")
REAL2_SIZES = (4, 16)
REAL2_HEADS = (1, 3, 5, 7)
REAL2_WIDTH_THRESHOLD = 8


def real2_solved_law(machine):
    """Amended registration law (V2).

    * ``T0`` (last bit): solved whenever head 0 is trained -- unchanged, and
      confirmed on 8/8 V1 configurations.
    * ``T1`` (parity) and ``T2`` (ones mod 3): solved only by a recurrent system
      of width at least 8 WITHOUT the last-symbol skip feature.
    """
    mech, size, w, h = machine
    capable = (mech == "GRU" and size >= REAL2_WIDTH_THRESHOLD and w == 0)
    bits = 0
    if h & 1:
        bits |= 1
    if (h & 2) and capable:
        bits |= 2
    if (h & 4) and capable:
        bits |= 4
    return bits


def real2_descriptor(machine):
    mech, size, w, h = machine
    if mech == "MLP":
        k = 0
    elif size < REAL2_WIDTH_THRESHOLD:
        k = 1
    else:
        k = 2
    rho = [0] * hu.RHO_DIM_HELDOUT
    rho[0] = size
    rho[1] = 1 + w
    rho[2] = 1 + hu.popcount(h)
    rho[3] = 7 + (1 if mech == "GRU" else 0)
    dev = size + hu.popcount(h) + w + (2 if mech == "GRU" else 0)
    obs = (1 + w, 1 if mech == "GRU" else 0)
    return k, tuple(rho), dev, obs


def build_sigma_real2():
    raw = []
    machines = []
    for mech in REAL2_MECHS:
        for size in REAL2_SIZES:
            for w in (0, 1):
                for h in REAL2_HEADS:
                    machines.append((mech, size, w, h))
    for machine in machines:
        k, rho, dev, obs = real2_descriptor(machine)
        raw.append((machine[1], machine[2], machine[3], k, rho, dev, obs))
    order = sorted(range(len(raw)),
                   key=lambda i: (raw[i][4][0], raw[i][4][3], raw[i][0],
                                  raw[i][1], raw[i][2]))
    rank = [0] * len(raw)
    for pos, idx in enumerate(order):
        rank[idx] = pos
    return tuple(raw), tuple(rank), tuple(machines)


REAL2_GRID = {
    "budgets": ((4, 1, 2, 7), (16, 2, 3, 8), (16, 2, 4, 8)),
    "charges": ((0, 0, 0, 0), (1, 0, 0, 0)),
    "d_values": (8, 14, 99),
    "b_values": (0, 8, 16, 24, 32),
    "h_values": ("NO_OBSERVATION", (1, 0), (2, 1)),
    "tau_values": (Fraction(3, 17), Fraction(8, 17), Fraction(11, 17), Fraction(1)),
}

REAL2_RAW, REAL2_RANK, REAL2_MACHINES = build_sigma_real2()


def sigma_real2():
    spec = hu.make_spec("SIGMA_REAL2", REAL2_RAW, REAL2_RANK, REAL2_MACHINES,
                        hu.MU_REAL, real2_solved_law, REAL2_GRID,
                        lambda rec: rec[1] == 0)
    return spec

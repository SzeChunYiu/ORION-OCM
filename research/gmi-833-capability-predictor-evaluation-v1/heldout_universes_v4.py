"""SIGMA_SYN2 / SIGMA_ARCH2 -- the POWER revival of the held-out rows.

All earlier universe modules are left byte-identical.

Diagnosis (single stage: grid/universe registration, discovered PREDICTION-SIDE,
with no outcome oracle consulted): on SIGMA_SYN and SIGMA_ARCH every point `F`
emits takes one of only two degenerate values -- `UNSATISFIED` or `0`.  The
soundness census over those points is true but weak: a predictor that only ever
identifies a degenerate value is barely being asked a question.  The cause is the
observation coordinate.  `obs = (1+w, m mod 2)` is too coarse to pin a survivor
set down to machines that share a NONZERO capability, so every non-degenerate
image is multi-valued and `F` correctly abstains.

Lever: a finer registered observation `obs = (1+w, m mod 2, h mod 4)`, which can
select survivor sets all of whose members solve the same task.  New machines
carry a new coordinate so their outcomes were never measured before the freeze:
SIGMA_SYN2 adds a `g` gate on head 2, SIGMA_ARCH2 adds the parameters
`REC 6`, `CTR 3` and `FF 3`.

Nothing about `F` changes; this is a change of instrument, not of predictor.
"""

from fractions import Fraction
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import heldout_universes_v1 as hu  # noqa: E402

SYN2_MODULI = (1, 2, 3, 6)


def syn2_machine_answer(machine, task_index, word):
    m, w, h, g = machine
    if not (h >> task_index) & 1:
        return 0
    state = sum(word) % m
    if task_index == 0:
        return (word[-1] if word else 0) if w == 1 else 0
    if task_index == 1:
        return state % 2
    if g != 1:
        return 0
    return 1 if state % 3 == 0 else 0


def syn2_solved_law(machine):
    m, w, h, g = machine
    bits = 0
    if (h & 1) and w == 1:
        bits |= 1
    if (h & 2) and m % 2 == 0:
        bits |= 2
    if (h & 4) and m % 3 == 0 and g == 1:
        bits |= 4
    return bits


def syn2_descriptor(machine):
    m, w, h, g = machine
    if m == 1:
        k = 0
    elif m in (2, 3):
        k = 1
    else:
        k = 2
    rho = [0] * hu.RHO_DIM_HELDOUT
    rho[0] = m
    rho[1] = 1 + w
    rho[2] = 1 + hu.popcount(h)
    rho[3] = 11 + g
    dev = m + hu.popcount(h) + w + g
    obs = (1 + w, m % 2, h & 3)
    return k, tuple(rho), dev, obs


def build_sigma_syn2():
    machines = []
    for m in SYN2_MODULI:
        for w in (0, 1):
            for h in range(8):
                for g in (0, 1):
                    machines.append((m, w, h, g))
    raw = []
    for machine in machines:
        k, rho, dev, obs = syn2_descriptor(machine)
        raw.append((machine[0], machine[1], machine[2], k, rho, dev, obs))
    order = sorted(range(len(raw)),
                   key=lambda i: (raw[i][4][0], raw[i][4][3], raw[i][0],
                                  raw[i][1], raw[i][2]))
    rank = [0] * len(raw)
    for pos, idx in enumerate(order):
        rank[idx] = pos
    return tuple(raw), tuple(rank), tuple(machines)


ARCH2_FAMILIES = ("FF", "REC", "CTR", "STK")
ARCH2_PARAMS = {"FF": (1, 2, 3), "REC": (2, 3, 6), "CTR": (2, 3, 4), "STK": (1, 2)}
ARCH2_K = {"FF": 0, "REC": 1, "CTR": 1, "STK": 2}


def arch2_machine_answer(machine, task_index, word):
    return hu.arch_machine_answer(machine, task_index, word)


def arch2_solved_law(machine):
    mech, param, w, h = machine
    tracks_ones = (mech == "CTR" and param >= hu.WORD_LENGTH)
    bits = 0
    if (h & 1) and w == 1:
        bits |= 1
    if (h & 2) and ((mech == "REC" and param % 2 == 0) or tracks_ones):
        bits |= 2
    if (h & 4) and ((mech == "REC" and param % 3 == 0) or tracks_ones):
        bits |= 4
    return bits


def arch2_descriptor(machine):
    mech, param, w, h = machine
    k = ARCH2_K[mech]
    rho = [0] * hu.RHO_DIM_HELDOUT
    rho[0] = param + (1 if mech in ("CTR", "STK") else 0)
    rho[1] = 1 + w
    rho[2] = 1 + hu.popcount(h)
    rho[3] = 13 + (1 if mech in ("REC", "CTR") else 0)
    dev = param + hu.popcount(h) + w + ARCH2_K[mech]
    obs = (1 + w, param % 2, h & 3)
    return k, tuple(rho), dev, obs


def build_sigma_arch2():
    machines = []
    for mech in ARCH2_FAMILIES:
        for param in ARCH2_PARAMS[mech]:
            for w in (0, 1):
                for h in range(8):
                    machines.append((mech, param, w, h))
    raw = []
    for machine in machines:
        k, rho, dev, obs = arch2_descriptor(machine)
        raw.append((machine[1], machine[2], machine[3], k, rho, dev, obs))
    order = sorted(range(len(raw)),
                   key=lambda i: (raw[i][4][0], raw[i][4][3], raw[i][0],
                                  raw[i][1], raw[i][2]))
    rank = [0] * len(raw)
    for pos, idx in enumerate(order):
        rank[idx] = pos
    return tuple(raw), tuple(rank), tuple(machines)


SYN2_GRID = {
    "budgets": ((2, 2, 2, 12), (3, 2, 3, 12), (6, 2, 4, 12)),
    "charges": ((0, 0, 0, 0), (1, 0, 0, 0)),
    "d_values": (4, 7, 99),
    "b_values": (0, 16, 32, 64, 128),
    "h_values": ((2, 1, 1), (1, 0, 2), (2, 0, 3)),
    "tau_values": (Fraction(2, 11), Fraction(5, 11), Fraction(7, 11), Fraction(9, 11)),
}

ARCH2_GRID = {
    "budgets": ((2, 2, 2, 14), (3, 2, 3, 14), (5, 2, 4, 14)),
    "charges": ((0, 0, 0, 0), (1, 0, 0, 0)),
    "d_values": (4, 7, 99),
    "b_values": (0, 20, 40, 80, 160),
    "h_values": ((2, 1, 1), (1, 0, 2), (2, 0, 3)),
    "tau_values": (Fraction(2, 13), Fraction(6, 13), Fraction(11, 13), Fraction(1)),
}

SYN2_RAW, SYN2_RANK, SYN2_MACHINES = build_sigma_syn2()
ARCH2_RAW, ARCH2_RANK, ARCH2_MACHINES = build_sigma_arch2()


def sigma_syn2():
    return hu.make_spec("SIGMA_SYN2", SYN2_RAW, SYN2_RANK, SYN2_MACHINES, hu.MU_SYN,
                        syn2_solved_law, SYN2_GRID, lambda rec: rec[1] == 0)


def sigma_arch2():
    return hu.make_spec("SIGMA_ARCH2", ARCH2_RAW, ARCH2_RANK, ARCH2_MACHINES,
                        hu.MU_ARCH, arch2_solved_law, ARCH2_GRID,
                        lambda rec: rec[1] == 0)

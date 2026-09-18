"""External capability evaluator -- the outcome oracle.

Introduced strictly after the freeze commit.  It never consults a registered
capability table: it RUNS every machine over the whole protected battery and
compares the answers exactly.  For the real systems it reads the measured
solved-sets off the committed ``REAL_RUNS/`` receipts, which are produced by
actual torch training.

Also builds ``SIGMA_OOD``, the structurally out-of-universe population used by
the OOD probe.

Python 3.8 compatible, stdlib only, exact ``Fraction`` arithmetic.
"""

from fractions import Fraction
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import heldout_universes_v1 as hu  # noqa: E402
import heldout_universes_v2 as hv  # noqa: E402

UNSATISFIED = "UNSATISFIED"


# --------------------------------------------------------------------------
# Measured solved-sets: run the machine, compare exactly
# --------------------------------------------------------------------------


def measure_solved_bits(answer_fn, machine):
    """Brute-force simulation over the entire protected battery."""
    bits = 0
    for task_index in range(3):
        target = hu.TASKS[task_index][1]
        ok = True
        for word in hu.WORDS:
            if answer_fn(machine, task_index, word) != target(word):
                ok = False
                break
        if ok:
            bits |= 1 << task_index
    return bits


def measured_cap(bits, mu, contract):
    verified = hu.VERIFIED[contract]
    total = Fraction(0)
    for j in range(3):
        if verified[j] and ((bits >> j) & 1):
            total += mu[j]
    return total


def admissible(rho, budget, charge):
    for j in range(hu.RHO_DIM_HELDOUT):
        effective = (budget[j] if j < len(budget) else 0) - (charge[j] if j < len(charge) else 0)
        if rho[j] > effective:
            return False
    return True


def extcap(rho, bits, mu, contract, budget, charge):
    """extcap(x,E,R): UNSATISFIED outside the budget, else the measured value."""
    if not admissible(rho, budget, charge):
        return UNSATISFIED
    return measured_cap(bits, mu, contract)


# --------------------------------------------------------------------------
# Per-universe measurement
# --------------------------------------------------------------------------

REAL_RUNS_DIR = os.path.join(HERE, "REAL_RUNS")


REAL_RUNS_V2_DIR = os.path.join(HERE, "REAL_RUNS_V2")


def load_real_measured(version=1):
    """Measured solved-sets of the real trained systems, from the receipts."""
    if version == 2:
        path = os.path.join(REAL_RUNS_V2_DIR, "REAL_MEASURED_V2.json")
    else:
        path = os.path.join(REAL_RUNS_DIR, "REAL_MEASURED_V1.json")
    if not os.path.exists(path):
        return None
    with open(path) as handle:
        payload = json.load(handle)
    return payload


def measure_universe(name):
    """Return (machines, measured_bits, mu, source) for a registered universe."""
    if name == "SIGMA_SYN":
        machines = hu.SYN_MACHINES
        bits = tuple(measure_solved_bits(hu.syn_machine_answer, m) for m in machines)
        return machines, bits, hu.MU_SYN, "SIMULATION"
    if name == "SIGMA_ARCH":
        machines = hu.ARCH_MACHINES
        bits = tuple(measure_solved_bits(hu.arch_machine_answer, m) for m in machines)
        return machines, bits, hu.MU_ARCH, "SIMULATION"
    if name == "SIGMA_REAL2":
        machines = hv.REAL2_MACHINES
        payload = load_real_measured(2)
        if payload is None:
            return machines, None, hu.MU_REAL, "UNAVAILABLE"
        table = payload["measured_solved_bits"]
        bits = tuple(table["|".join(str(x) for x in m)] for m in machines)
        return machines, bits, hu.MU_REAL, "REAL_TRAINING_V2"
    if name == "SIGMA_REAL":
        machines = hu.REAL_MACHINES
        payload = load_real_measured(1)
        if payload is None:
            return machines, None, hu.MU_REAL, "UNAVAILABLE"
        table = payload["measured_solved_bits"]
        bits = tuple(table["|".join(str(x) for x in m)] for m in machines)
        return machines, bits, hu.MU_REAL, "REAL_TRAINING"
    raise ValueError("unregistered universe: %r" % (name,))


def registered_bits(name):
    if name == "SIGMA_SYN":
        return tuple(hu.syn_solved_law(m) for m in hu.SYN_MACHINES)
    if name == "SIGMA_ARCH":
        return tuple(hu.arch_solved_law(m) for m in hu.ARCH_MACHINES)
    if name == "SIGMA_REAL":
        return tuple(hu.real_solved_law(m) for m in hu.REAL_MACHINES)
    if name == "SIGMA_REAL2":
        return tuple(hv.real2_solved_law(m) for m in hv.REAL2_MACHINES)
    raise ValueError("unregistered universe: %r" % (name,))


# --------------------------------------------------------------------------
# SIGMA_OOD: structurally out-of-universe worlds
# --------------------------------------------------------------------------
#
# Each registered generator coordinate of SIGMA_SYN is relaxed one at a time:
#   m   -> the registered moduli {1,2,3,6} plus the unregistered {4,5,12}
#   w   -> {0,1} plus the unregistered 2 (a second register)
#   h   -> 0..7 plus the unregistered 8..15 (a fourth head that answers nothing)
# The registered 64 are removed, leaving only genuinely out-of-universe worlds.

OOD_MODULI = (1, 2, 3, 4, 5, 6, 12)
OOD_W = (0, 1, 2)
OOD_H = tuple(range(16))


def ood_machine_answer(machine, task_index, word):
    m, w, h = machine
    if not (h >> task_index) & 1:
        return 0
    state = sum(word) % m
    if task_index == 0:
        return (word[-1] if word else 0) if w >= 1 else 0
    if task_index == 1:
        return state % 2
    return 1 if state % 3 == 0 else 0


def ood_descriptor(machine):
    m, w, h = machine
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
    rho[3] = 1 + (1 if h else 0)
    dev = m + hu.popcount(h) + w
    obs = (1 + w, m % 2)
    return k, tuple(rho), dev, obs


def build_sigma_ood():
    registered = set(hu.SYN_MACHINES)
    out = []
    for m in OOD_MODULI:
        for w in OOD_W:
            for h in OOD_H:
                machine = (m, w, h)
                if machine in registered:
                    continue
                k, rho, dev, obs = ood_descriptor(machine)
                bits = measure_solved_bits(ood_machine_answer, machine)
                out.append({
                    "machine": machine,
                    "k": k,
                    "rho": rho,
                    "dev": dev,
                    "obs": obs,
                    "bits": bits,
                    "relaxed": ("modulus" if m not in hu.SYN_MODULI else
                                ("register" if w == 2 else "head")),
                })
    return tuple(out)

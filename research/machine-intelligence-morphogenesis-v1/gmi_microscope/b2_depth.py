"""Shared depth-stack instrument for stage-B2 rows B2.8 (residual), B2.9 (normalization) and B2.10 (pre/post norm).

Everything runs in the REGISTERED 8-bit fixed-point universe of gmi_microscope/core.py (TOTAL_BITS = 8,
FRAC_BITS = 4), with its exact ADD, SUB, MUL (declared rounding), THRESH, SHR and SATURATION semantics. Every input of
the declared grid is enumerated; nothing is sampled and nothing is fitted.

A STACK is L blocks over a one-dimensional state. Block l applies a declared sublayer

    f_l(x) = ADD(MUL(g, x), b_l)

with a declared per-layer GAIN g (the activation-scale drift axis of B2.9) and a declared per-layer bias b_l. What
varies between arms is only how the sublayer's output is combined with the incoming state and what, if anything,
normalizes it. Three quantities are measured at every depth:

    distinct_states     the number of distinct final states over the enumerated input grid. This is exactly the
                        signal-propagation quantity: a stack that collapses every input to one state has destroyed
                        every distinction it was given, and one that keeps 256 has destroyed none.
    max_response        the largest change in the final state produced by a declared input perturbation of delta
                        least-significant bits. This is the measured analogue of the Jacobian in a quantized
                        universe; it is an integer number of LSBs, not a derivative.
    capability          the hindsight-optimal function of the final state on a declared obligation -- the
                        PARENT-MAXIMAL reader of that state (protocol rule 19).

Charged costs are METERED on gmi_microscope/core.Machine under basis B0, never counted by hand.
"""
from __future__ import annotations

from fractions import Fraction as Fr

from . import bases
from .core import FRAC_BITS, FX_MAX, FX_MIN, Machine, clamp

GRID = list(range(FX_MIN, FX_MAX + 1))         # every representable 8-bit fixed-point state: 256 of them
DEPTHS = (1, 2, 4, 8, 16)
DELTAS = (1, 2, 4)                             # declared input perturbations, in LSBs
N_CLASSES = 4                                  # the declared obligation partitions the input into 4 classes


def MUL(a, b):
    return clamp((a * b + (1 << (FRAC_BITS - 1))) >> FRAC_BITS)


def ADD(a, b):
    return clamp(a + b)


def bias(l):
    """Declared per-layer bias; deterministic, no RNG."""
    return ((l * 3) % 5) - 2


def obligation(x):
    """The declared protected obligation: which of N_CLASSES equal bands of the fixed-point range the INPUT lay in."""
    return min(N_CLASSES - 1, (x - FX_MIN) * N_CLASSES // (FX_MAX - FX_MIN + 1))


def center_scale(x, s):
    """A declared center+scale normalizer on a one-dimensional state: subtract the declared center and divide by the
    declared scale s, in the registered fixed point. With one coordinate there is no batch statistic to estimate, so
    the centre and the scale are DECLARED, which is what makes the arm a gauge choice rather than a learned map."""
    return MUL(clamp(x - 0), int(round((1 << FRAC_BITS) / s)))


def rms_like(x, s):
    """A declared RMS-like normalizer: no recentering, divide by the declared scale s."""
    return MUL(x, int(round((1 << FRAC_BITS) / s)))


def run_stack(x0, L, g, arm):
    """One forward pass of the declared stack. `arm` names the combination rule; see each row module's docstring."""
    x = x0
    for l in range(L):
        f = ADD(MUL(g, x), bias(l))
        if arm == "PLAIN":
            x = f
        elif arm == "RESIDUAL":
            x = ADD(x, f)
        elif arm == "PLAIN_RESCALED":
            x = rms_like(f, Fr(g, 1 << FRAC_BITS)) if g else f
        elif arm == "RESIDUAL_RESCALED":
            x = rms_like(ADD(x, f), Fr(g, 1 << FRAC_BITS) + 1 if g else 1)
        elif arm == "NONE":
            x = f
        elif arm == "CENTER_SCALE":
            x = center_scale(f, Fr(g, 1 << FRAC_BITS) if g else 1)
        elif arm == "RMS":
            x = rms_like(f, Fr(g, 1 << FRAC_BITS) if g else 1)
        elif arm == "CONST_SCALE":
            x = rms_like(f, Fr(1))                      # the negative twin: identical arithmetic, no data dependence
        elif arm == "PRE_NORM":
            x = ADD(x, ADD(MUL(g, rms_like(x, Fr(g, 1 << FRAC_BITS) if g else 1)), bias(l)))
        elif arm == "POST_NORM":
            x = rms_like(ADD(x, f), Fr(g, 1 << FRAC_BITS) + 1 if g else 1)
        else:
            raise KeyError(arm)
    return x


def profile(L, g, arm, delta):
    """The three measured quantities plus the obligation capability, over the enumerated grid."""
    out = {x: run_stack(x, L, g, arm) for x in GRID}
    distinct = len(set(out.values()))
    resp = 0
    for x in GRID:
        xp = x + delta
        if xp > FX_MAX:
            continue
        resp = max(resp, abs(out[xp] - out[x]))
    groups = {}
    for x in GRID:
        groups.setdefault(out[x], []).append(obligation(x))
    correct = 0
    for v in groups.values():
        cnt = {}
        for t in v:
            cnt[t] = cnt.get(t, 0) + 1
        correct += max(cnt.values())
    sat = sum(1 for x in GRID if out[x] in (FX_MAX, FX_MIN))
    return {"distinct_states": distinct, "max_response_lsb": resp,
            "saturated_fraction": Fr(sat, len(GRID)),
            "collapsed_to_one_state": distinct == 1,
            "capability": Fr(correct, len(GRID))}


def charged_cost(L, arm):
    """Metered on the registered charged machine (basis B0), never counted by hand."""
    M = Machine(bases.B0)
    M.phase("exec")
    before = M.L.c["exec"]
    x = 8
    for l in range(L):
        f = M.op("ADD", M.op("MUL", 16, x), bias(l))
        if arm == "PLAIN" or arm == "NONE":
            x = f
        elif arm == "RESIDUAL":
            x = M.op("ADD", x, f)
        elif arm in ("PLAIN_RESCALED", "RMS", "CONST_SCALE"):
            x = M.op("MUL", f, 16)
        elif arm == "CENTER_SCALE":
            x = M.op("MUL", M.op("SUB", f, 0), 16)
        elif arm == "RESIDUAL_RESCALED" or arm == "POST_NORM":
            x = M.op("MUL", M.op("ADD", x, f), 16)
        elif arm == "PRE_NORM":
            x = M.op("ADD", x, M.op("ADD", M.op("MUL", 16, M.op("MUL", x, 16)), bias(l)))
    return M.L.c["exec"] - before

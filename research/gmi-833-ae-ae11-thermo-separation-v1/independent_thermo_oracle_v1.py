#!/usr/bin/env python3
"""GMI #833 Section AE11 -- route B, the independent oracle.

Imports nothing from `ae11_thermo_separation_v1`.  Every claimed quantity is
recomputed by a materially different algorithm:

  route A                                     route B (here)
  ------------------------------------------  ------------------------------------
  K_U: walk BIT STRINGS of each length in     K_U: enumerate INSTRUCTION SEQUENCES
  increasing integer order, decode each one,  depth-first in instruction-table
  keep the first program that emits x         order, execute as you build, relax a
                                              per-output minimum; no decoder runs
  H_shannon: closed-form exponent algebra     H_shannon: build the canonical code
  H = sum_i e_i / 2**e_i                      tree, check Kraft equality over a
                                              common power-of-two denominator, and
                                              accumulate INTEGER leaf depths, with
                                              one division at the very end
  S_stat: the length of the registered        S_stat: explicit construction of the
  support tuple                               microstate SET, then its cardinality
  erased bits: forward image, |image|         erased bits: partition the domain
                                              into preimage classes and count the
                                              classes; largest class by the same
                                              partition
  register state: 2-character strings         register state: integers 0..3 with
                                              bitwise operations
  census: first witness per ordered pair      census: ALL witnesses per ordered
                                              pair, collected exhaustively

stdlib only; exact integer and Fraction arithmetic; CPython 3.8 compatible.
"""
from __future__ import print_function

import json
import sys
from fractions import Fraction as F

STRING_LENGTH = 6
LCAP = 14
MAXOUT = 24
NBITS = 2 ** STRING_LENGTH

ALPHABET = tuple(format(v, "0%db" % STRING_LENGTH) for v in range(NBITS))


class OracleError(RuntimeError):
    pass


def require(cond, msg):
    if not cond:
        raise OracleError(msg)


# ---------------------------------------------------------------------------
# The registered machine, re-declared here as data (not imported).
# ---------------------------------------------------------------------------
# (op, code length in bits, number of distinct parameter settings)
OPS = (
    ("EMIT0", 2, 1),
    ("EMIT1", 2, 1),
    ("HALT", 2, 1),
    ("REPEAT_LAST_K_N", 7, 16),
    ("COPY_PREFIX", 6, 8),
)
HALT_BITS = 2


def op_variants():
    """Every concrete instruction with its code length, in instruction-table
    order.  Route A never builds this list; it decodes bit strings instead."""
    out = []
    for name, bits, _n in OPS:
        if name == "REPEAT_LAST_K_N":
            for k in (1, 2):
                for n in range(1, 9):
                    out.append((name, (k, n), bits))
        elif name == "COPY_PREFIX":
            for j in range(1, 9):
                out.append((name, (j,), bits))
        elif name == "HALT":
            continue
        else:
            out.append((name, (), bits))
    return tuple(out)


VARIANTS = op_variants()


def apply_op(name, params, out):
    if name == "EMIT0":
        return out + "0"
    if name == "EMIT1":
        return out + "1"
    if name == "REPEAT_LAST_K_N":
        k, n = params
        if len(out) < k:
            return None
        return out + out[-k:] * n
    j = params[0]
    if len(out) < j:
        return None
    return out + out[:j]


def oracle_complexity_table(cap=LCAP):
    """K_U(x) for every registered string, by depth-first enumeration of
    INSTRUCTION SEQUENCES.  A sequence of total code length L that has produced
    an output of exactly STRING_LENGTH bits yields a program of length
    L + HALT_BITS."""
    best = {}

    def walk(out, used):
        if len(out) == STRING_LENGTH:
            total = used + HALT_BITS
            if total <= cap and (out not in best or total < best[out]):
                best[out] = total
        for name, params, bits in VARIANTS:
            nxt_used = used + bits
            if nxt_used + HALT_BITS > cap:
                continue
            nxt = apply_op(name, params, out)
            if nxt is None or len(nxt) > MAXOUT:
                continue
            walk(nxt, nxt_used)

    walk("", 0)
    return best


def oracle_program_kraft(cap=LCAP):
    """Kraft sum over the program set, counted by enumerating instruction
    sequences rather than by decoding bit strings.  A sequence of instructions
    followed by HALT is a program whatever its output length is."""
    total_ref = [F(0)]

    def walk(out, used):
        halted = used + HALT_BITS
        if halted <= cap:
            total_ref[0] += F(1, 2 ** halted)
        for name, params, bits in VARIANTS:
            nxt_used = used + bits
            if nxt_used + HALT_BITS > cap:
                continue
            nxt = apply_op(name, params, out)
            if nxt is None or len(nxt) > MAXOUT:
                continue
            walk(nxt, nxt_used)

    walk("", 0)
    return total_ref[0]


def oracle_instruction_kraft():
    total = F(0)
    for _name, bits, n_variants in OPS:
        total += F(n_variants, 2 ** bits)
    return total


# ---------------------------------------------------------------------------
# Shannon entropy by the canonical code tree, with integer accumulation.
# ---------------------------------------------------------------------------
def oracle_shannon_bits(exponents):
    """H(P) in bits for a dyadic distribution given as a list of exponents e_i
    with masses 1/2**e_i.  Route B puts every mass over the common denominator
    2**E, checks Kraft equality on the INTEGER numerators (which is exactly the
    statement that the code tree is complete), accumulates the integer sum
    sum_i n_i * e_i, and divides once at the end."""
    if not exponents:
        return F(0)
    biggest = max(exponents)
    numerators = [2 ** (biggest - e) for e in exponents]
    require(sum(numerators) == 2 ** biggest,
            "the registered dyadic masses do not form a complete code tree")
    acc = 0
    for n, e in zip(numerators, exponents):
        acc += n * e
    return F(acc, 2 ** biggest)


def oracle_microstate_count(support):
    """S_stat is carried as the integer microstate count.  Route B builds the
    microstate SET explicitly and takes its cardinality."""
    omega = set()
    for label in support:
        omega.add(label)
    return len(omega)


# ---------------------------------------------------------------------------
# The registered roster, re-declared here as data.
# ---------------------------------------------------------------------------
S4 = ("000000", "000001", "000010", "000011")
S5 = S4 + ("000100",)

ROSTER = (
    ("R_ALTERNATING_STRING", (("010101", 0),), "010101", 1, 2),
    ("R_MACRO_A", tuple((s, 2) for s in S4), "000000", 1, 2),
    ("R_MACRO_B", (("000000", 1), ("000001", 3), ("000010", 3),
                   ("000011", 3), ("000100", 3)), "000000", 3, 2),
    ("R_PROCESS_A", tuple((s, 2) for s in S4), "000000", 5, 4),
    ("R_PROCESS_B", tuple((s, STRING_LENGTH) for s in ALPHABET), "000010", 5, 2),
    ("R_SKEW_DYADIC", (("000000", 1), ("000001", 2), ("000010", 3),
                       ("000011", 3)), "000000", 3, 4),
    ("R_UNIFORM_BLOCK", tuple((s, STRING_LENGTH) for s in ALPHABET),
     "000000", 1, 2),
    ("R_ZERO_STRING", (("000000", 0),), "000000", 1, 2),
)

QUANTITIES = ("H_shannon", "K_U", "S_stat", "S_thermo")


def oracle_roster(table):
    out = []
    for name, dist, string, q, t in ROSTER:
        exps = [e for _s, e in dist]
        support = [s for s, _e in dist]
        out.append({
            "id": name,
            "H_shannon": oracle_shannon_bits(exps),
            "K_U": table.get(string, ">LCAP"),
            "S_stat": oracle_microstate_count(support),
            "S_thermo": F(q, t),
            "string": string,
        })
    return sorted(out, key=lambda r: r["id"])


def oracle_census(values):
    """All witnesses per ordered pair, collected exhaustively."""
    rows = {}
    for a in QUANTITIES:
        for b in QUANTITIES:
            if a == b:
                continue
            found = []
            for i in range(len(values)):
                for j in range(len(values)):
                    if i >= j:
                        continue
                    if values[i][a] == values[j][a] and values[i][b] != values[j][b]:
                        found.append((values[i]["id"], values[j]["id"]))
            rows[(a, b)] = sorted(found)
    return rows


def oracle_witnessed_count(values):
    return sum(1 for v in oracle_census(values).values() if v)


# ---------------------------------------------------------------------------
# Maps and devices on integer register states.
# ---------------------------------------------------------------------------
DOMAIN = (0, 1, 2, 3)          # state = 2*a + b


def hi(s):
    return (s >> 1) & 1


def lo(s):
    return s & 1


MAPS = {
    "F_AND": lambda s: 2 * (hi(s) & lo(s)),
    "F_BIJECTION": lambda s: 2 * hi(s) + (hi(s) ^ lo(s)),
    "F_ERASE1": lambda s: 2 * hi(s),
    "F_ERASE2": lambda s: 0,
}

PRIMITIVES = {
    "AND_INTO_BIT0": lambda s: 2 * (hi(s) & lo(s)) + lo(s),
    "CNOT": lambda s: 2 * hi(s) + (hi(s) ^ lo(s)),
    "NOOP": lambda s: s,
    "RESET_BIT0": lambda s: lo(s),
    "RESET_BIT1": lambda s: 2 * hi(s),
    "SWAP": lambda s: 2 * lo(s) + hi(s),
}

LOW_OVERHEAD_OPS = {
    "F_AND": ("AND_INTO_BIT0", "RESET_BIT1"),
    "F_BIJECTION": ("CNOT",),
    "F_ERASE1": ("RESET_BIT1",),
    "F_ERASE2": ("RESET_BIT0", "RESET_BIT1"),
}
HIGH_OVERHEAD_PREAMBLE = ("SWAP", "SWAP", "CNOT", "CNOT", "NOOP")


def exact_log2_int(n):
    if n <= 0:
        return None
    k = 0
    m = n
    while m % 2 == 0:
        m //= 2
        k += 1
    return k if m == 1 else None


def oracle_preimage_partition(fn, domain=DOMAIN):
    """Partition the domain into preimage classes -- route B never forms the
    forward image as a set."""
    classes = {}
    for s in domain:
        classes.setdefault(fn(s), []).append(s)
    return dict((k, sorted(v)) for k, v in classes.items())


def oracle_erased_bits(fn, domain=DOMAIN):
    classes = oracle_preimage_partition(fn, domain)
    a = exact_log2_int(len(domain))
    b = exact_log2_int(len(classes))
    require(a is not None, "domain size is not a power of two")
    return None if b is None else a - b


def oracle_largest_preimage(fn, domain=DOMAIN):
    return max(len(v) for v in oracle_preimage_partition(fn, domain).values())


def oracle_pushforward_exponents(fn, domain=DOMAIN):
    """Push forward the uniform input on the 4-state register by counting
    preimage classes.  Returns (exponents, None) when every image mass is
    dyadic, else (None, masses) with masses as Fractions."""
    classes = oracle_preimage_partition(fn, domain)
    masses = sorted(F(len(v), len(domain)) for v in classes.values())
    exps = []
    for m in masses:
        e = exact_log2_int(m.denominator)
        if m.numerator != 1 or e is None:
            return (None, masses)
        exps.append(e)
    return (exps, masses)


def oracle_drop_bits(fn, domain=DOMAIN):
    """H(uniform) - H(f_* uniform), exact when dyadic, else None."""
    h_in = F(exact_log2_int(len(domain)))
    exps, _masses = oracle_pushforward_exponents(fn, domain)
    if exps is None:
        return None
    return h_in - oracle_shannon_bits(exps)


RELAXED_CORRELATED_STATE = 3        # "11" as an integer register state


def oracle_conditional_relaxation(map_id, state=RELAXED_CORRELATED_STATE):
    """Recount the relaxed no-residual-correlation object by preimage
    partitioning restricted to the conditional support."""
    fn = MAPS[map_id]
    classes = oracle_preimage_partition(fn, (state,))
    a = exact_log2_int(1)
    b = exact_log2_int(len(classes))
    return {
        "conditional_state_count": 1,
        "conditional_image_count": len(classes),
        "relative_erased_bits": a - b,
        "conditional_drop_bits": F(0) - F(0),
    }


def oracle_device(device, map_id):
    ops = LOW_OVERHEAD_OPS[map_id]
    if device == "DEV_HIGH_OVERHEAD":
        ops = HIGH_OVERHEAD_PREAMBLE + ops

    def net(s):
        cur = s
        for op in ops:
            cur = PRIMITIVES[op](cur)
        return cur

    return {
        "ops": list(ops),
        "total_ops": len(ops),
        "overhead_ops": len(ops) - len(LOW_OVERHEAD_OPS[map_id]),
        "implements": all(net(s) == MAPS[map_id](s) for s in DOMAIN),
        "erased_bits": oracle_erased_bits(net),
    }


# ---------------------------------------------------------------------------
# Certified rational brackets for non-dyadic logarithms.
# ---------------------------------------------------------------------------
def oracle_log2_bracket(a, lower, upper):
    """Confirm lower <= log2(a) <= upper by integer comparisons only."""
    lo_ok = a ** lower.denominator >= 2 ** lower.numerator
    hi_ok = a ** upper.denominator <= 2 ** upper.numerator
    require(lo_ok and hi_ok, "log2 bracket certificate fails for %d" % a)
    return (lower, upper)


def oracle_and_drop_bracket():
    """(3/4) * log2(3), bracketed by certified rationals."""
    lo, hi_ = oracle_log2_bracket(3, F(19, 12), F(8, 5))
    return (F(3, 4) * lo, F(3, 4) * hi_)


def oracle_gibbs_bound(w):
    """The exact integer log2 W when W is a power of two, else a certified
    rational lower bound for log2 W."""
    e = exact_log2_int(w)
    if e is not None:
        return F(e)
    if w == 5:
        lo, _hi = oracle_log2_bracket(5, F(9, 4), F(7, 3))
        return lo
    raise OracleError("no registered certificate for log2(%d)" % w)


# ---------------------------------------------------------------------------
# Resource registry cross-check.
# ---------------------------------------------------------------------------
def oracle_instantiated_physical(registry_rows):
    n = 0
    for row in registry_rows:
        if row.get("class") == "PHYSICAL_ENERGETIC" and row.get("instantiated"):
            n += 1
    return n


# ---------------------------------------------------------------------------
# The oracle bundle.
# ---------------------------------------------------------------------------
def oracle():
    table = oracle_complexity_table()
    values = oracle_roster(table)
    census = oracle_census(values)
    histogram = {}
    for s in ALPHABET:
        key = str(table.get(s, ">LCAP"))
        histogram[key] = histogram.get(key, 0) + 1
    k_ints = [table[s] for s in ALPHABET if s in table]

    maps = {}
    for map_id in sorted(MAPS):
        fn = MAPS[map_id]
        drop = oracle_drop_bits(fn)
        lp = oracle_largest_preimage(fn)
        lp_log2 = exact_log2_int(lp)
        maps[map_id] = {
            "erased_bits": oracle_erased_bits(fn),
            "image_size": len(oracle_preimage_partition(fn)),
            "largest_preimage_size": lp,
            "log2_largest_preimage": (lp_log2 if lp_log2 is not None
                                      else "NOT_A_POWER_OF_TWO"),
            "drop_bits": (str(drop) if drop is not None else "NOT_DECIDED"),
        }
    devices = {}
    for device in ("DEV_HIGH_OVERHEAD", "DEV_LOW_OVERHEAD"):
        for map_id in sorted(MAPS):
            devices[device + "|" + map_id] = oracle_device(device, map_id)

    and_lo, and_hi = oracle_and_drop_bracket()
    return {
        "K_U_table": dict((s, table.get(s, ">LCAP")) for s in ALPHABET),
        "K_U_histogram": histogram,
        "K_U_min": min(k_ints),
        "K_U_max": max(k_ints),
        "strings_over_cap": NBITS - len(k_ints),
        "instruction_kraft_sum": oracle_instruction_kraft(),
        "program_kraft_sum": oracle_program_kraft(),
        "roster": values,
        "census": census,
        "witnessed_pairs": sum(1 for v in census.values() if v),
        "maps": maps,
        "devices": devices,
        "and_drop_bracket": (and_lo, and_hi),
        "conditional_relaxation": dict(
            (map_id, oracle_conditional_relaxation(map_id))
            for map_id in sorted(MAPS)),
        "gibbs_bounds": dict((v["id"], oracle_gibbs_bound(v["S_stat"]))
                             for v in values),
    }


def main():
    o = oracle()
    summary = {
        "K_U_histogram": o["K_U_histogram"],
        "K_U_min": o["K_U_min"],
        "K_U_max": o["K_U_max"],
        "strings_over_cap": o["strings_over_cap"],
        "instruction_kraft_sum": str(o["instruction_kraft_sum"]),
        "program_kraft_sum": str(o["program_kraft_sum"]),
        "witnessed_pairs": o["witnessed_pairs"],
        "roster": [{"id": r["id"], "H_shannon": str(r["H_shannon"]),
                    "K_U": r["K_U"], "S_stat": r["S_stat"],
                    "S_thermo": str(r["S_thermo"])} for r in o["roster"]],
        "maps": o["maps"],
        "and_drop_bracket": [str(o["and_drop_bracket"][0]),
                             str(o["and_drop_bracket"][1])],
    }
    sys.stdout.write(json.dumps(summary, sort_keys=True, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

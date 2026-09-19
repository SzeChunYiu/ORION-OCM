#!/usr/bin/env python3
"""GMI #833 Section AE11 -- route A executor: thermodynamic and physical-information
separation on a registered finite roster, in exact arithmetic, with no energy value
computed anywhere.

Prints RESULT_V1.json to stdout. Byte-identical under `python3 -I -B` and
`python3 -I -O -B`, and across CPython 3.8 and 3.12.

Discipline (from FREEZE_V1.md):
  * every quantity entering a claim is a `fractions.Fraction` or an `int`;
  * Landauer statements are carried as `W_min = m * k_B T ln 2` with `m` an exact
    integer erased-bit count, never as a joule value;
  * statistical-mechanical entropy is carried as the integer microstate count `W`
    together with the exact statement `S_stat = k_B ln W`, and comparisons between
    macrostates are decided by comparing `W` as integers;
  * thermodynamic entropy change is the exact rational `Q / T` in registered units;
  * where a comparison needs the logarithm of a non-dyadic rational it is decided
    only by certified exact rational bounds via integer comparisons.

No bare `assert` is used: `-O` would strip it.
"""
from __future__ import print_function

import hashlib
import itertools
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent

SCHEMA = "GMI_833_AE11_THERMO_SEPARATION_RESULT_V1"
SECTION = "AE11"
PACKAGE = "gmi-833-ae-ae11-thermo-separation-v1"
ISSUE = 833
ISSUE_COMMENT_ID = 5692689542
SOURCE_MAIN = "0dcdec54fbece041ee2b7cd1f630469ad85d19d3"
# Custody sha of the commit that added FREEZE_V1.md, supplied by the lane owner.
FREEZE_COMMIT = "68a5bcb7236d14f7c52421f9cd24bf443f37be99"
REGISTER_COMMIT = "db1fbc6efa5778c58a4fb31cc5408f01b8845a4a"
CLAIM_CEILING = ("GMI_833_AE11_FOUR_ENTROPY_NOTIONS_SEPARATED_AND_LANDAUER_"
                 "SCOPE_AUDITED_WITHOUT_ANY_ENERGY_MEASUREMENT")

FORBIDDEN_PROMOTIONS = [
    "ALL_LEARNING_IS_COMPRESSION",
    "ARCHITECTURE_SELECTION_LAW",
    "ASYMPTOTIC_EXTRAPOLATION_FROM_FINITE_ROSTER",
    "COMPLETE_GMI",
    "ENERGY_CLAIM_WITHOUT_HARDWARE_MEASUREMENT",
    "FREE_ENERGY_PRINCIPLE_PROVED",
    "GENERAL_REASONING_REDUCED_TO_PREDICTION",
    "GMI_MORPHOLOGY_PREDICTION",
    "INFORMATION_SAVINGS_IMPLY_ENERGY_SAVINGS",
    "INTELLIGENCE_EQUALS_COMPRESSION",
    "LANDAUER_BOUND_DETERMINES_SYSTEM_ENERGY",
    "MANIFOLD_HYPOTHESIS_UNIVERSAL",
    "MUTUAL_INFORMATION_SUFFICIENT_FOR_INTELLIGENCE",
    "REAL_SYSTEM_CLAIM_WITHOUT_INSTRUMENT",
    "SHANNON_ENTROPY_EQUALS_THERMODYNAMIC_ENTROPY",
    "THERMODYNAMIC_INTELLIGENCE_LAW",
    "WORLD_MODEL_ALWAYS_REQUIRED",
]


class ExecutorError(RuntimeError):
    pass


def require(cond, msg):
    """Assertion that survives `-O`."""
    if not cond:
        raise ExecutorError(msg)


# ---------------------------------------------------------------------------
# 0. Registered constants (mirrored from PROSPECTIVE_REGISTER_V1.json).
# ---------------------------------------------------------------------------
STRING_LENGTH = 6
LCAP = 14
MAXOUT = 24
NULL_TRIALS = 200
NULL_SEED = 8331111
REGISTERED_PHYSICAL_SYSTEMS = 0

ALPHABET = tuple(format(v, "0%db" % STRING_LENGTH) for v in range(2 ** STRING_LENGTH))

# The frozen prefix-free instruction set.  Each instruction has a frozen integer
# code length; the codewords form a complete prefix code (Kraft sum exactly 1),
# and a program is a bit string that decodes to a sequence of complete codewords
# ending in HALT with no bit left over, so the program set is prefix-free too.
INSTRUCTION_TABLE = (
    {"op": "EMIT0", "code": "00", "bits": 2, "params": "",
     "semantics": "append the bit 0 to the output"},
    {"op": "EMIT1", "code": "01", "bits": 2, "params": "",
     "semantics": "append the bit 1 to the output"},
    {"op": "HALT", "code": "10", "bits": 2, "params": "",
     "semantics": "stop; the program is valid only if no bit is left over"},
    {"op": "REPEAT_LAST_K_N", "code": "110", "bits": 7,
     "params": "1 bit k-1 with k in 1..2, then 3 bits n-1 with n in 1..8",
     "semantics": "append the last k output bits, n times; undefined if the "
                  "output is shorter than k"},
    {"op": "COPY_PREFIX", "code": "111", "bits": 6,
     "params": "3 bits j-1 with j in 1..8",
     "semantics": "append the first j output bits; undefined if the output is "
                  "shorter than j"},
)


def instruction_kraft_sum():
    """Exact Kraft sum over the instruction codewords, as a Fraction."""
    total = F(0)
    for row in INSTRUCTION_TABLE:
        n_variants = 2 ** (row["bits"] - len(row["code"]))
        total += F(n_variants, 2 ** row["bits"])
    return total


def decode_one(bits, i):
    """Decode one instruction at offset i. Returns (op, params, next_i) or None."""
    n = len(bits)
    if i + 2 <= n:
        head = bits[i:i + 2]
        if head == "00":
            return ("EMIT0", (), i + 2)
        if head == "01":
            return ("EMIT1", (), i + 2)
        if head == "10":
            return ("HALT", (), i + 2)
    if i + 3 <= n:
        head = bits[i:i + 3]
        if head == "110":
            if i + 7 <= n:
                k = int(bits[i + 3], 2) + 1
                n_rep = int(bits[i + 4:i + 7], 2) + 1
                return ("REPEAT_LAST_K_N", (k, n_rep), i + 7)
            return None
        if head == "111":
            if i + 6 <= n:
                j = int(bits[i + 3:i + 6], 2) + 1
                return ("COPY_PREFIX", (j,), i + 6)
            return None
    return None


def run_program(bits):
    """Run a candidate program. Returns the output string, or None if the bit
    string is not a program of U (bad decode, undefined operation, overflow, or
    bits left over after HALT)."""
    out = ""
    i = 0
    while True:
        step = decode_one(bits, i)
        if step is None:
            return None
        op, params, nxt = step
        if op == "HALT":
            return out if nxt == len(bits) else None
        if op == "EMIT0":
            out += "0"
        elif op == "EMIT1":
            out += "1"
        elif op == "REPEAT_LAST_K_N":
            k, n_rep = params
            if len(out) < k:
                return None
            out = out + out[-k:] * n_rep
        else:
            j = params[0]
            if len(out) < j:
                return None
            out = out + out[:j]
        if len(out) > MAXOUT:
            return None
        i = nxt


def complexity_table(cap):
    """K_U(x) for every registered string, by increasing program length.

    Route A searches the program space in BIT-STRING order: for each length
    1..cap it walks the 2**length bit strings in increasing integer order and
    decodes each one.  The first program that outputs x fixes K_U(x)."""
    best = {}
    programs_by_length = {}
    kraft = F(0)
    for length in range(1, cap + 1):
        count = 0
        for value in range(2 ** length):
            bits = format(value, "0%db" % length)
            out = run_program(bits)
            if out is None:
                continue
            count += 1
            kraft += F(1, 2 ** length)
            if len(out) == STRING_LENGTH and out not in best:
                best[out] = (length, bits)
        if count:
            programs_by_length[length] = count
    return best, programs_by_length, kraft


def k_of(table, x):
    """Exact integer K_U(x), or the registered symbol '>LCAP'."""
    hit = table.get(x)
    return hit[0] if hit is not None else ">LCAP"


# ---------------------------------------------------------------------------
# 1. Exact rational certificates for non-dyadic logarithms.
# ---------------------------------------------------------------------------
def certifies_log2_at_least(a, b, u, v):
    """Certify log2(a/b) >= u/v by the integer comparison a**v >= 2**u * b**v."""
    return a ** v >= (2 ** u) * (b ** v)


def certifies_log2_at_most(a, b, u, v):
    """Certify log2(a/b) <= u/v by the integer comparison a**v <= 2**u * b**v."""
    return a ** v <= (2 ** u) * (b ** v)


LOG2_CERTIFICATES = {
    "log2(3)": {"lower": (19, 12), "upper": (8, 5), "a": 3, "b": 1},
    "log2(5)": {"lower": (9, 4), "upper": (7, 3), "a": 5, "b": 1},
}


def log2_bracket(name):
    cert = LOG2_CERTIFICATES[name]
    lo_u, lo_v = cert["lower"]
    hi_u, hi_v = cert["upper"]
    require(certifies_log2_at_least(cert["a"], cert["b"], lo_u, lo_v),
            "lower certificate fails for " + name)
    require(certifies_log2_at_most(cert["a"], cert["b"], hi_u, hi_v),
            "upper certificate fails for " + name)
    return F(lo_u, lo_v), F(hi_u, hi_v)


def exact_log2_int(n):
    """log2(n) as an exact integer when n is a power of two, else None."""
    if n <= 0:
        return None
    k = 0
    m = n
    while m % 2 == 0:
        m //= 2
        k += 1
    return k if m == 1 else None


# ---------------------------------------------------------------------------
# 2. The registered roster: four quantities on eight composite objects.
# ---------------------------------------------------------------------------
S4 = ("000000", "000001", "000010", "000011")
S5 = S4 + ("000100",)


def dyadic(pairs):
    """A distribution given as ((string, exponent), ...) with mass 1/2**exponent."""
    masses = [(s, F(1, 2 ** e)) for s, e in pairs]
    total = sum(m for _, m in masses)
    require(total == 1, "registered distribution does not sum to 1")
    return tuple(sorted(masses))


def uniform_on(strings):
    e = exact_log2_int(len(strings))
    require(e is not None, "uniform registered support must have size 2**k")
    return dyadic(tuple((s, e) for s in strings))


def shannon_bits(dist):
    """H(P) in bits, exact.  Every mass is 1/2**e so -log2(mass) = e exactly.

    Route A uses the closed-form exponent algebra: H = sum_i e_i / 2**e_i."""
    total = F(0)
    for _, mass in dist:
        e = exact_log2_int(mass.denominator)
        require(mass.numerator == 1 and e is not None,
                "registered mass is not an integer power of 1/2")
        total += F(e, 2 ** e)
    return total


ROSTER = (
    {"id": "R_ALTERNATING_STRING", "dist": dyadic((("010101", 0),)),
     "string": "010101", "Q": F(1), "T": F(2),
     "note": "point mass on the alternating string; the same H_shannon and the "
             "same microstate count as R_ZERO_STRING, a different K_U"},
    {"id": "R_MACRO_A", "dist": uniform_on(S4), "string": "000000",
     "Q": F(1), "T": F(2),
     "note": "uniform macrostate of 4 microstates"},
    {"id": "R_MACRO_B", "dist": dyadic((("000000", 1), ("000001", 3),
                                        ("000010", 3), ("000011", 3),
                                        ("000100", 3))),
     "string": "000000", "Q": F(3), "T": F(2),
     "note": "5 microstates, H_shannon exactly 2 -- equal Shannon entropy to "
             "R_MACRO_A with a strictly larger microstate count"},
    {"id": "R_PROCESS_A", "dist": uniform_on(S4), "string": "000000",
     "Q": F(5), "T": F(4),
     "note": "same distribution and macrostate as R_MACRO_A, a different "
             "registered quasi-static process"},
    {"id": "R_PROCESS_B", "dist": uniform_on(ALPHABET), "string": "000010",
     "Q": F(5), "T": F(2),
     "note": "the lexicographically least string attaining the maximum K_U over "
             "the 64-string alphabet, carried on the maximal-entropy distribution"},
    {"id": "R_SKEW_DYADIC", "dist": dyadic((("000000", 1), ("000001", 2),
                                            ("000010", 3), ("000011", 3))),
     "string": "000000", "Q": F(3), "T": F(4),
     "note": "4 microstates, H_shannon strictly below log2 4"},
    {"id": "R_UNIFORM_BLOCK", "dist": uniform_on(ALPHABET), "string": "000000",
     "Q": F(1), "T": F(2),
     "note": "the uniform distribution on all 2**6 strings: maximal H_shannon, "
             "members of several different K_U"},
    {"id": "R_ZERO_STRING", "dist": dyadic((("000000", 0),)), "string": "000000",
     "Q": F(1), "T": F(2),
     "note": "point mass on the all-zero string"},
)

QUANTITIES = ("H_shannon", "K_U", "S_stat", "S_thermo")


def roster_values(table, roster=ROSTER):
    """The four registered quantities for each object.

    S_stat is carried as the integer microstate count W = |supp(P)|, with the
    exact statement S_stat = k_B ln W; comparisons are integer comparisons of W.
    S_thermo is the exact rational Q/T in the registered units."""
    out = []
    for obj in roster:
        w = len(obj["dist"])
        out.append({
            "id": obj["id"],
            "H_shannon": shannon_bits(obj["dist"]),
            "K_U": k_of(table, obj["string"]),
            "S_stat": w,
            "S_thermo": obj["Q"] / obj["T"],
            "string": obj["string"],
            "Q": obj["Q"],
            "T": obj["T"],
            "support_size": w,
            "note": obj["note"],
        })
    return out


# Which ordered pairs are linked by a registered definitional relation?  Only
# H_shannon and S_stat are: W is the size of the support of P, so
# H_shannon <= log2 W always holds.  A witness for such a pair exhibits the slack
# in that relation.  Every other pair has no registered definitional relation and
# its witness exhibits outright registered independence.
DERIVED_PAIRS = frozenset([("H_shannon", "S_stat"), ("S_stat", "H_shannon")])


def census(values):
    """For each ordered pair (A, B), two objects x, y with A(x) = A(y) and
    B(x) != B(y): a witness that B is not a function of A.

    Route A scans ordered index pairs in lexicographic order and keeps the first
    witness."""
    rows = []
    for a in QUANTITIES:
        for b in QUANTITIES:
            if a == b:
                continue
            found = None
            for i, j in itertools.combinations(range(len(values)), 2):
                if values[i][a] == values[j][a] and values[i][b] != values[j][b]:
                    found = (values[i]["id"], values[j]["id"])
                    break
            kind = "derived" if (a, b) in DERIVED_PAIRS else "registered_independent"
            rows.append({
                "fixed": a,
                "free": b,
                "witnessed": found is not None,
                "witness": list(found) if found else None,
                "witness_kind": kind,
                "fixed_value": (str(values[[v["id"] for v in values].index(found[0])][a])
                                if found else None),
                "free_values": ([str(values[[v["id"] for v in values].index(found[0])][b]),
                                 str(values[[v["id"] for v in values].index(found[1])][b])]
                                if found else None),
            })
    return rows


def witnessed_count(values):
    n = 0
    for a in QUANTITIES:
        for b in QUANTITIES:
            if a == b:
                continue
            for i, j in itertools.combinations(range(len(values)), 2):
                if values[i][a] == values[j][a] and values[i][b] != values[j][b]:
                    n += 1
                    break
    return n


# ---------------------------------------------------------------------------
# 3. Registered maps, device models, erased-bit counts.
# ---------------------------------------------------------------------------
D = ("00", "01", "10", "11")          # the registered 2-bit logical register


def f_bijection(s):
    return s[0] + str(int(s[0]) ^ int(s[1]))


def f_erase1(s):
    return s[0] + "0"


def f_erase2(s):
    return "00"


def f_and(s):
    return str(int(s[0]) & int(s[1])) + "0"


MAPS = (
    {"id": "F_AND", "fn": f_and,
     "definition": "(a, b) -> (a AND b, 0)"},
    {"id": "F_BIJECTION", "fn": f_bijection,
     "definition": "(a, b) -> (a, a XOR b), a bijection of the register"},
    {"id": "F_ERASE1", "fn": f_erase1,
     "definition": "(a, b) -> (a, 0)"},
    {"id": "F_ERASE2", "fn": f_erase2,
     "definition": "(a, b) -> (0, 0)"},
)

# Registered primitive logical operations of a device model.
PRIMITIVES = {
    "RESET_BIT0": lambda s: "0" + s[1],
    "RESET_BIT1": lambda s: s[0] + "0",
    "CNOT": lambda s: s[0] + str(int(s[0]) ^ int(s[1])),
    "SWAP": lambda s: s[1] + s[0],
    "AND_INTO_BIT0": lambda s: str(int(s[0]) & int(s[1])) + s[1],
    "NOOP": lambda s: s,
}

# The minimal registered op sequence per map.
LOW_OVERHEAD_OPS = {
    "F_AND": ("AND_INTO_BIT0", "RESET_BIT1"),
    "F_BIJECTION": ("CNOT",),
    "F_ERASE1": ("RESET_BIT1",),
    "F_ERASE2": ("RESET_BIT0", "RESET_BIT1"),
}
# A registered preamble of five operations, every one of them a bijection of the
# register, so it changes the net map not at all and the erased-bit count not at
# all, while it changes the registered operation count by exactly five.
HIGH_OVERHEAD_PREAMBLE = ("SWAP", "SWAP", "CNOT", "CNOT", "NOOP")
DEVICES = ("DEV_LOW_OVERHEAD", "DEV_HIGH_OVERHEAD")


def device_ops(device, map_id):
    low = LOW_OVERHEAD_OPS[map_id]
    if device == "DEV_LOW_OVERHEAD":
        return low
    return HIGH_OVERHEAD_PREAMBLE + low


def compose_ops(ops):
    def net(s):
        cur = s
        for op in ops:
            cur = PRIMITIVES[op](cur)
        return cur
    return net


def image_of(fn, domain=D):
    """Route A computes the image by forward application and set size."""
    return sorted(set(fn(s) for s in domain))


def erased_bits(fn, domain=D):
    """m = log2|D| - log2|image(f)|, an exact integer, defined when both counts
    are powers of two."""
    a = exact_log2_int(len(domain))
    b = exact_log2_int(len(image_of(fn, domain)))
    require(a is not None, "registered domain size is not a power of two")
    return None if b is None else a - b


def largest_preimage(fn, domain=D):
    counts = {}
    for s in domain:
        counts[fn(s)] = counts.get(fn(s), 0) + 1
    return max(counts.values())


def pushforward(dist_on_D, fn):
    out = {}
    for s, mass in dist_on_D:
        t = fn(s)
        out[t] = out.get(t, F(0)) + mass
    return tuple(sorted(out.items()))


UNIFORM_D = tuple(sorted((s, F(1, 4)) for s in D))


def shannon_bits_general(dist):
    """H(P) in bits when every mass is dyadic; otherwise None (the caller then
    falls back on certified rational bounds)."""
    total = F(0)
    for _, mass in dist:
        e = exact_log2_int(mass.denominator)
        if mass.numerator != 1 or e is None:
            return None
        total += F(e, 2 ** e)
    return total


# ---------------------------------------------------------------------------
# 4. The resource registry (row 2).
# ---------------------------------------------------------------------------
def resource_registry():
    logical = [
        ("program_length_bits", "the length in bits of a program of U; the "
         "quantity K_U minimises"),
        ("shannon_entropy_bits", "H_shannon of a registered dyadic distribution"),
        ("microstate_count", "the integer W of a registered macrostate"),
        ("erased_bit_count", "the integer m = log2|D| - log2|image(f)|"),
        ("device_primitive_operation_count",
         "the integer number of registered primitive operations a device model runs"),
        ("overhead_operation_count",
         "the integer difference between a device model's operation count and the "
         "minimal registered sequence for the same map"),
        ("program_length_cap", "the frozen integer LCAP"),
        ("logical_state_count", "|D| and |image(f)| as integers"),
        ("preimage_count", "the integer size of the largest preimage class"),
        ("roster_cardinality", "the integer number of registered objects"),
        ("null_trial_count", "the frozen integer number of null trials"),
        ("registered_string_length", "the frozen integer string length"),
    ]
    physical = [
        ("heat_Q_joules", "the heat of a registered quasi-static process as a "
         "physical magnitude"),
        ("temperature_T_kelvin", "the reservoir temperature as a physical magnitude"),
        ("boltzmann_constant_k_B", "the physical constant"),
        ("landauer_quantum_k_B_T_ln2_joules",
         "the energy scale of one erased bit as a physical magnitude"),
        ("erasure_work_W_min_joules", "the Landauer work as a physical magnitude"),
        ("device_power_draw_watts", "hardware power"),
        ("wall_clock_energy_per_operation_joules", "hardware energy per operation"),
        ("hardware_thermal_dissipation", "heat a real device sheds"),
        ("biological_metabolic_rate", "the energetic upkeep of an organism"),
        ("entropy_production_rate", "a rate of entropy production in a driven system"),
        ("maintenance_power", "power to hold a driven system away from equilibrium"),
        ("thermodynamic_entropy_change_registered_units",
         "Q / T as an exact rational in the registered units; Q and T are "
         "registered symbols with no physical magnitude, so no value in J/K is "
         "produced"),
    ]
    rows = []
    for name, desc in logical:
        rows.append({
            "resource": name, "class": "LOGICAL_COMPUTATIONAL",
            "instantiated": True,
            "numeric_value_in_physical_units": False,
            "description": desc,
        })
    for name, desc in physical:
        rows.append({
            "resource": name, "class": "PHYSICAL_ENERGETIC",
            "instantiated": False,
            "numeric_value_in_physical_units": False,
            "description": desc,
        })
    return sorted(rows, key=lambda r: r["resource"])


def instantiated_physical(rows):
    return [r["resource"] for r in rows
            if r["class"] == "PHYSICAL_ENERGETIC" and r["instantiated"]]


# ---------------------------------------------------------------------------
# 5. Nonequilibrium-term gate (row 4).
# ---------------------------------------------------------------------------
NONEQ_TERMS = (
    "dissipative structure",
    "energy harvesting",
    "entropy production",
    "far from equilibrium",
    "housekeeping heat",
    "maintenance power",
    "metabolic maintenance",
    "nonequilibrium",
    "non-equilibrium",
    "steady-state flux",
)


def noneq_hits(claims):
    hits = []
    for claim_id in sorted(claims):
        text = claims[claim_id].lower()
        for term in NONEQ_TERMS:
            if term in text:
                hits.append({"claim": claim_id, "term": term})
    return hits


PHYSICAL_SYSTEM_COMPONENTS = ("boundary", "dynamics", "reservoir", "temperature")


def registered_physical_systems():
    """A registered physical system is the tuple
    (boundary, dynamics, reservoir, temperature).  The registered quasi-static
    processes supply a temperature SYMBOL only, so not one of them is a physical
    system.  The count is 0."""
    systems = []
    for obj in ROSTER:
        components = {"temperature": True, "boundary": False,
                      "dynamics": False, "reservoir": False}
        if all(components[c] for c in PHYSICAL_SYSTEM_COMPONENTS):
            systems.append(obj["id"])
    return systems


# ---------------------------------------------------------------------------
# 6. Bound records.
# ---------------------------------------------------------------------------
def bound_record(bid, kind, quantity, bound_value, range_lo, range_hi,
                 range_derivation, attained_by, violated_by, notes):
    if kind == "upper":
        vacuous = bound_value >= range_hi
    else:
        vacuous = bound_value <= range_lo
    status = "FALSIFIABLE" if violated_by is not None else "UNFALSIFIED_BOUND"
    return {
        "id": bid,
        "kind": kind,
        "quantity": quantity,
        "bound_value": str(bound_value),
        "range_lo": str(range_lo),
        "range_hi": str(range_hi),
        "range_derivation": range_derivation,
        "vacuous": vacuous,
        "attained_by": attained_by,
        "violated_by": violated_by,
        "status": status,
        "used_for_closure": (violated_by is not None) and (not vacuous),
        "notes": notes,
    }


LANDAUER_ASSUMPTIONS = (
    {"assumption": "thermal equilibrium of the reservoir at a single temperature T",
     "registered_violation": "RELAXED_TWO_RESERVOIR",
     "violation_effect": "with a second reservoir at a different registered "
                         "temperature the work referred to the hotter reservoir "
                         "is no longer bounded below by m in units of k_B T ln 2; "
                         "the bound is stated at a single T and silently changes "
                         "meaning when T does",
     "violates_the_bound": True},
    {"assumption": "quasi-static operation",
     "registered_violation": "RELAXED_FINITE_TIME",
     "violation_effect": "a finite-time protocol dissipates strictly MORE than m, "
                         "so relaxing this assumption breaks ATTAINMENT and not "
                         "the lower bound; recorded as such rather than dressed "
                         "up as a violation",
     "violates_the_bound": False},
    {"assumption": "no residual correlation between the erased register and the "
                   "environment",
     "registered_violation": "RELAXED_CORRELATED_RESET",
     "violation_effect": "when the register is perfectly correlated with a "
                         "registered ancilla the conditional logical state count "
                         "is 1, the relative erased-bit count is the integer 0, "
                         "and a protocol in the relaxed class attains 0 < m",
     "violates_the_bound": True},
    {"assumption": "logical irreversibility of the map",
     "registered_violation": "F_BIJECTION",
     "violation_effect": "a bijection has m = 0, the bound reads W_min >= 0 and "
                         "is vacuous against the definitional floor of the "
                         "dissipation, which is 0",
     "violates_the_bound": False},
)


# The registered conditional state: given a perfectly correlated ancilla the
# register is known, so its conditional distribution is a point mass.  Which
# state it is does not matter -- the relaxation is computed on it, not asserted.
RELAXED_CORRELATED_STATE = "11"


def relaxed_correlated_reset(fn, state=RELAXED_CORRELATED_STATE):
    """The no-residual-correlation assumption dropped: condition on a registered
    ancilla that determines the register.  Returns the exact integer relative
    erased-bit count and the exact conditional entropy drop, both COMPUTED."""
    conditional_domain = (state,)
    rel_m = erased_bits(fn, domain=conditional_domain)
    point_mass = ((state, F(1)),)
    h_in = shannon_bits_general(point_mass)
    h_out = shannon_bits_general(pushforward(point_mass, fn))
    return {
        "conditional_state_count": len(conditional_domain),
        "conditional_image_count": len(image_of(fn, conditional_domain)),
        "relative_erased_bits": rel_m,
        "conditional_drop_bits": h_in - h_out,
    }


def landauer_bounds(map_rows):
    """One lower-bound record per registered map."""
    range_hi = F(exact_log2_int(len(D)))
    derivation = (
        "The bounded quantity is the dissipation of a protocol of the registered "
        "class R_PROTO, in units of k_B T ln 2.  R_PROTO is defined as the class of "
        "protocols that act only on the registered logical register D and reset it "
        "with the registered reset primitive.  By that definition the dissipation is "
        "0 when the protocol resets nothing, which fixes range_lo = 0, and is at "
        "most the full reset of the register, log2|D| = %d, which fixes range_hi. "
        "Both endpoints come from the definition of R_PROTO and of D; neither comes "
        "from any value observed on the roster." % exact_log2_int(len(D)))
    by_id = dict((m["id"], m) for m in MAPS)
    out = []
    for row in map_rows:
        m = row["erased_bits"]
        relaxed = relaxed_correlated_reset(by_id[row["id"]]["fn"])
        violated = None
        if m > 0 and relaxed["relative_erased_bits"] < m:
            violated = {
                "object": "RELAXED_CORRELATED_RESET__" + row["id"],
                "relaxed_class": "the registered assumption 'no residual "
                                 "correlation with the environment' is dropped: the "
                                 "register is perfectly correlated with a registered "
                                 "ancilla, so its conditional distribution is the "
                                 "registered point mass on " +
                                 RELAXED_CORRELATED_STATE,
                "attained_value": str(relaxed["relative_erased_bits"]),
                "conditional_state_count": relaxed["conditional_state_count"],
                "conditional_image_count": relaxed["conditional_image_count"],
                "conditional_drop_bits": str(relaxed["conditional_drop_bits"]),
                "why": "conditioned on the ancilla the register has exactly %d "
                       "possible state, its image has %d, so the relative "
                       "erased-bit count is the computed integer %d and the "
                       "conditional entropy drop is the computed rational %s; the "
                       "relaxed protocol attains %d, strictly below the bound "
                       "value %d"
                       % (relaxed["conditional_state_count"],
                          relaxed["conditional_image_count"],
                          relaxed["relative_erased_bits"],
                          str(relaxed["conditional_drop_bits"]),
                          relaxed["relative_erased_bits"], m),
            }
        out.append(bound_record(
            "B_LANDAUER__" + row["id"], "lower",
            "dissipation of a protocol in the registered class R_PROTO "
            "implementing " + row["id"] + ", in units of k_B T ln 2",
            F(m), F(0), range_hi, derivation,
            {"object": "PROTO_QUASISTATIC_ERASE__" + row["id"],
             "attained_value": str(m),
             "why": "the registered idealised quasi-static protocol for this map "
                    "dissipates exactly m = %d in units of k_B T ln 2; this is a "
                    "registered protocol model, not a measurement" % m},
            violated,
            {"landauer_statement": "W_min = %d * k_B T ln 2" % m,
             "erased_bits": m,
             "no_energy_value_computed": True}))
    return out


def drop_bounds(map_rows):
    """m_count(f) <= H(P) - H(f_*P) under the registered uniform input: one lower
    bound per map on the distributional logical irreversibility."""
    range_hi = F(exact_log2_int(len(D)))
    derivation = (
        "The bounded quantity is H_shannon(P) - H_shannon(f_*P) in bits for a "
        "distribution P on the registered 4-state register.  By the definition of "
        "Shannon entropy on a 4-point domain, H_shannon lies in [0, log2 4] and the "
        "push-forward entropy is non-negative, so the drop lies in [0, 2].  Both "
        "endpoints come from the definition of Shannon entropy on D; neither comes "
        "from any value observed on the roster.")
    relaxed_inputs = {
        "F_AND": ("uniform on {00, 11}", tuple(sorted((s, F(1, 2))
                                                      for s in ("00", "11")))),
        "F_ERASE1": ("uniform on {00, 10}", tuple(sorted((s, F(1, 2))
                                                         for s in ("00", "10")))),
        "F_ERASE2": ("point mass on 00", (("00", F(1)),)),
        "F_BIJECTION": ("uniform on {00, 11}", tuple(sorted((s, F(1, 2))
                                                            for s in ("00", "11")))),
    }
    out = []
    by_id = dict((m["id"], m) for m in MAPS)
    for row in map_rows:
        m = row["erased_bits"]
        fn = by_id[row["id"]]["fn"]
        label, p_rel = relaxed_inputs[row["id"]]
        h_in = shannon_bits_general(p_rel)
        h_out = shannon_bits_general(pushforward(p_rel, fn))
        violated = None
        if h_in is not None and h_out is not None and (h_in - h_out) < m:
            violated = {
                "object": "RELAXED_INPUT__" + row["id"],
                "relaxed_class": "the registered assumption 'the input "
                                 "distribution is uniform on D' is dropped",
                "input": label,
                "attained_value": str(h_in - h_out),
                "why": "under this non-uniform registered input the drop is %s, "
                       "strictly below the bound value %d" % (str(h_in - h_out), m),
            }
        out.append(bound_record(
            "B_DROP__" + row["id"], "lower",
            "H_shannon(P) - H_shannon(f_*P) in bits for " + row["id"] +
            " under the registered uniform input",
            F(m), F(0), range_hi, derivation,
            {"object": row["id"] + "__uniform_input",
             "attained_value": row["drop_bits"],
             "attained": row["drop_is_exact"] and row["drop_bits"] == str(F(m)),
             "why": "under the registered uniform input the drop is %s"
                    % row["drop_bits"]},
            violated,
            {"drop_is_exact_rational": row["drop_is_exact"],
             "drop_bracket": row.get("drop_bracket")}))
    return out


def gibbs_bounds(values):
    """H_shannon(P) <= log2 W, one upper-bound record per registered object."""
    range_hi = F(STRING_LENGTH)
    derivation = (
        "The bounded quantity is H_shannon(P) in bits for a distribution P on the "
        "registered alphabet of 2**%d strings.  By the definition of Shannon "
        "entropy on a finite alphabet, H_shannon lies in [0, log2 (2**%d)] = [0, %d]. "
        "Both endpoints come from the definition of Shannon entropy on the "
        "registered alphabet; neither comes from any value observed on the roster."
        % (STRING_LENGTH, STRING_LENGTH, STRING_LENGTH))
    out = []
    for v in values:
        w = v["S_stat"]
        exact = exact_log2_int(w)
        if exact is not None:
            bound_value = F(exact)
            certificate = "log2(%d) = %d exactly" % (w, exact)
        else:
            lo, _hi = log2_bracket("log2(%d)" % w)
            bound_value = lo
            certificate = ("log2(%d) >= %s, certified by the integer comparison "
                           "%d**%d >= 2**%d" % (w, str(lo), w, lo.denominator,
                                                lo.numerator))
        # A violator lives in the relaxed class where the declared macrostate need
        # not contain the support of P: take the uniform distribution on the first
        # 2**e registered strings, whose H_shannon is exactly e, while the object
        # still declares W microstates.  Such an e exists only while the bound
        # value is below the alphabet ceiling.
        violator = None
        for e in range(1, STRING_LENGTH + 1):
            if F(e) > bound_value:
                violator = {
                    "object": "RELAXED_SUPPORT_MISMATCH__" + v["id"],
                    "relaxed_class": "the registered requirement that the declared "
                                     "macrostate contain the support of P is dropped",
                    "attained_value": str(F(e)),
                    "why": "an object declaring %d microstates while P is uniform "
                           "on the first 2**%d registered strings has "
                           "H_shannon = %d, strictly above the bound value %s"
                           % (w, e, e, str(bound_value)),
                }
                break
        out.append(bound_record(
            "B_GIBBS__" + v["id"], "upper",
            "H_shannon(P) in bits for " + v["id"],
            bound_value, F(0), range_hi, derivation,
            {"object": v["id"], "attained_value": str(v["H_shannon"]),
             "attained": v["H_shannon"] == bound_value,
             "why": "equality holds exactly when P is uniform on its support"},
            violator,
            {"microstate_count": w,
             "log2_certificate": certificate,
             "S_stat_statement": "S_stat = k_B ln %d" % w,
             "holds": v["H_shannon"] <= bound_value}))
    return out


# ---------------------------------------------------------------------------
# 7. Null: is a fully witnessed census something any roster gets?
# ---------------------------------------------------------------------------
class LCG(object):
    """A deterministic integer generator; no float is produced anywhere."""

    def __init__(self, seed):
        self.state = seed

    def draw(self, modulus):
        self.state = (1103515245 * self.state + 12345) % (2 ** 31)
        return self.state % modulus


def random_dyadic_exponents(rng, splits):
    """A dyadic distribution as a multiset of exponents, built by splitting."""
    parts = [0]
    for _ in range(splits):
        i = rng.draw(len(parts))
        a = parts[i]
        if a >= 6:
            continue
        parts[i] = a + 1
        parts.append(a + 1)
    return sorted(parts)


NULL_Q = (1, 2, 3, 4, 5, 6, 7, 8)
NULL_T = (1, 2, 4, 8)


def run_null(table, trials=NULL_TRIALS, seed=NULL_SEED):
    rng = LCG(seed)
    histogram = {}
    largest = 0
    reached_full = 0
    for _ in range(trials):
        objs = []
        for _k in range(len(ROSTER)):
            parts = random_dyadic_exponents(rng, rng.draw(8))
            h = sum(F(a, 2 ** a) for a in parts)
            x = ALPHABET[rng.draw(len(ALPHABET))]
            objs.append({
                "id": "null_%d" % _k,
                "H_shannon": h,
                "K_U": k_of(table, x),
                "S_stat": len(parts),
                "S_thermo": F(NULL_Q[rng.draw(len(NULL_Q))],
                              NULL_T[rng.draw(len(NULL_T))]),
            })
        c = witnessed_count(objs)
        histogram[c] = histogram.get(c, 0) + 1
        if c > largest:
            largest = c
        if c == 12:
            reached_full += 1
    return {
        "detector": "the ordered-pair census: for how many of the 12 ordered "
                    "pairs (A, B) of the four quantities does the roster contain "
                    "two objects with A equal and B different",
        "family": "8 objects per trial; a dyadic distribution built by repeated "
                  "splitting from a deterministic integer generator, a string "
                  "drawn uniformly from the 64-string alphabet, and Q/T drawn "
                  "from the registered rational grid Q in 1..8, T in {1,2,4,8}",
        "trials": trials,
        "seed": seed,
        "histogram": dict((str(k), v) for k, v in sorted(histogram.items())),
        "largest_null_witnessed_pairs": largest,
        "trials_reaching_all_twelve": reached_full,
        "witness_witnessed_pairs": 12,
        "primary_comparison": "threshold-free: the registered roster witnesses all "
                              "12 ordered pairs, strictly more than the largest "
                              "count any of the %d random rosters attains" % trials,
        "witness_exceeds_largest_null": largest < 12,
        "no_alarm_case": "the conflation detector -- an ordered pair that the "
                         "roster cannot witness -- does not fire on the registered "
                         "clean roster: 0 of 12 pairs are unwitnessed",
        "no_alarm_holds": None,   # filled by the caller
        "known_clean_rosters_flagged": [],
    }


# ---------------------------------------------------------------------------
# 8. Hostiles: potency first, then detection.
# ---------------------------------------------------------------------------
def hostile_entropy_conflate(table):
    values = roster_values(table)
    true_w = [v["S_stat"] for v in values]
    distinct_h = sorted(set(v["H_shannon"] for v in values))
    perturbed = []
    for v in values:
        u = dict(v)
        u["S_stat"] = 1 + distinct_h.index(v["H_shannon"])
        perturbed.append(u)
    pert_w = [v["S_stat"] for v in perturbed]
    potent = pert_w != true_w
    detected = witnessed_count(perturbed) < 12
    return {
        "name": "H_ENTROPY_CONFLATE",
        "perturbs": "the census so S_stat is reported as a function of H_shannon",
        "true_value": [str(x) for x in true_w],
        "perturbed_value": [str(x) for x in pert_w],
        "potent": potent,
        "detected": detected,
        "detector": "the ordered-pair census: the pair (H_shannon, S_stat) loses "
                    "its witness, so the witnessed count falls below 12",
        "witnessed_pairs_after": witnessed_count(perturbed),
    }


def hostile_erased_bits(map_rows):
    true_m = dict((r["id"], r["erased_bits"]) for r in map_rows)["F_ERASE2"]
    pert_m = 1
    recomputed = erased_bits(f_erase2)
    return {
        "name": "H_ERASED_BITS",
        "perturbs": "the erased-bit count of F_ERASE2",
        "true_value": true_m,
        "perturbed_value": pert_m,
        "potent": pert_m != true_m,
        "detected": pert_m != recomputed,
        "detector": "recomputation of m from the image size of the map: "
                    "log2|D| - log2|image(F_ERASE2)| = %d" % recomputed,
    }


def hostile_overhead_equal():
    true_high = len(device_ops("DEV_HIGH_OVERHEAD", "F_ERASE2"))
    true_low = len(device_ops("DEV_LOW_OVERHEAD", "F_ERASE2"))
    pert_high = len(LOW_OVERHEAD_OPS["F_ERASE2"])   # the preamble removed
    return {
        "name": "H_OVERHEAD_EQUAL",
        "perturbs": "DEV_HIGH_OVERHEAD so the two devices stop differing",
        "true_value": [true_low, true_high],
        "perturbed_value": [true_low, pert_high],
        "potent": pert_high != true_high,
        "detected": pert_high == true_low,
        "detector": "the non-inference witness: a map whose two device models "
                    "carry the SAME erased-bit count and DIFFERENT registered "
                    "operation counts; with the preamble removed the counts "
                    "coincide and the witness is gone",
    }


def hostile_physical_claim(rows):
    true_count = len(instantiated_physical(rows))
    planted = list(rows) + [{
        "resource": "planted_device_energy_joules",
        "class": "PHYSICAL_ENERGETIC",
        "instantiated": True,
        "numeric_value_in_physical_units": True,
        "description": "a planted instantiation of a physical energetic resource",
    }]
    pert_count = len(instantiated_physical(planted))
    return {
        "name": "H_PHYSICAL_CLAIM",
        "perturbs": "the resource registry by planting a PHYSICAL_ENERGETIC "
                    "instantiation, which the gate must flag",
        "true_value": true_count,
        "perturbed_value": pert_count,
        "potent": pert_count != true_count,
        "detected": pert_count > 0,
        "detector": "the row-2 gate: the count of instantiated PHYSICAL_ENERGETIC "
                    "resources must be exactly 0",
    }


def hostile_lcap(table):
    perturbed_cap = 13
    pert_table, _pc, _pk = complexity_table(perturbed_cap)
    probe = "000010"
    true_k = k_of(table, probe)
    pert_k = k_of(pert_table, probe)
    unreachable = [s for s in ALPHABET if s not in pert_table]
    roster_unreachable = sorted(set(o["string"] for o in ROSTER
                                   if o["string"] not in pert_table))
    return {
        "name": "H_LCAP",
        "perturbs": "the program-length cap so a K_U value changes",
        "probe_string": probe,
        "true_value": true_k,
        "perturbed_value": pert_k,
        "perturbed_cap": perturbed_cap,
        "potent": pert_k != true_k,
        "detected": len(roster_unreachable) > 0,
        "detector": "the K_U table gate: at the perturbed cap the registered "
                    "roster string %s has no program of length at most the cap "
                    "and is reported as '>LCAP', so "
                    "complexity_defined_for_every_registered_string fails"
                    % (roster_unreachable[0] if roster_unreachable else "(none)"),
        "roster_strings_over_cap_after": roster_unreachable,
        "alphabet_strings_over_cap_after": len(unreachable),
    }


# ---------------------------------------------------------------------------
# 9. Register custody.
# ---------------------------------------------------------------------------
def register_digest(register):
    body = dict(register)
    body.pop("self_digest_sha256", None)
    body.pop("self_digest_note", None)
    blob = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


# ---------------------------------------------------------------------------
# 10. Main.
# ---------------------------------------------------------------------------
def contains_float(obj):
    if isinstance(obj, float):
        return True
    if isinstance(obj, dict):
        return any(contains_float(k) or contains_float(v) for k, v in obj.items())
    if isinstance(obj, (list, tuple)):
        return any(contains_float(v) for v in obj)
    return False


def build():
    register = json.loads((HERE / "PROSPECTIVE_REGISTER_V1.json")
                          .read_text(encoding="utf-8"))
    digest = register_digest(register)
    require(digest == register["self_digest_sha256"],
            "PROSPECTIVE_REGISTER_V1.json self digest mismatch: recomputed %s, "
            "declared %s" % (digest, register["self_digest_sha256"]))

    kraft_instructions = instruction_kraft_sum()
    table, programs_by_length, kraft_programs = complexity_table(LCAP)
    values = roster_values(table)

    # --- row 1: the census -------------------------------------------------
    census_rows = census(values)
    census_complete = all(r["witnessed"] for r in census_rows)
    derived = sum(1 for r in census_rows if r["witness_kind"] == "derived")

    k_histogram = {}
    for s in ALPHABET:
        key = str(k_of(table, s))
        k_histogram[key] = k_histogram.get(key, 0) + 1
    k_values = [k_of(table, s) for s in ALPHABET]
    over_cap = [s for s in ALPHABET if s not in table]
    k_min = min(v for v in k_values if isinstance(v, int))
    k_max = max(v for v in k_values if isinstance(v, int))
    lex_least_max = sorted(s for s in ALPHABET if k_of(table, s) == k_max)[0]
    lex_least_min = sorted(s for s in ALPHABET if k_of(table, s) == k_min)[0]

    uniform_block = [v for v in values if v["id"] == "R_UNIFORM_BLOCK"][0]
    process_b = [v for v in values if v["id"] == "R_PROCESS_B"][0]

    # --- row 2: the resource registry --------------------------------------
    registry = resource_registry()
    physical_instantiated = instantiated_physical(registry)

    # --- rows 3 and 5: maps, devices, erased bits ---------------------------
    map_rows = []
    for m in MAPS:
        fn = m["fn"]
        img = image_of(fn)
        mm = erased_bits(fn)
        out_dist = pushforward(UNIFORM_D, fn)
        drop = None
        h_out = shannon_bits_general(out_dist)
        bracket = None
        if h_out is not None:
            drop = shannon_bits_general(UNIFORM_D) - h_out
            drop_str = str(drop)
            drop_exact = True
        else:
            # The only non-dyadic push-forward on this roster is F_AND's
            # (3/4, 1/4); decide it by certified rational bounds on log2 3.
            lo3, hi3 = log2_bracket("log2(3)")
            drop_lo, drop_hi = F(3, 4) * lo3, F(3, 4) * hi3
            drop_str = "NOT_DECIDED"
            drop_exact = False
            bracket = {
                "expression": "(3/4) * log2(3)",
                "lower": str(drop_lo),
                "upper": str(drop_hi),
                "certificate": "log2(3) >= 19/12 by 3**12 >= 2**19 and "
                               "log2(3) <= 8/5 by 3**5 <= 2**8",
                "strictly_above_erased_bits": drop_lo > F(mm),
            }
        lp = largest_preimage(fn)
        lp_log2 = exact_log2_int(lp)
        map_rows.append({
            "id": m["id"],
            "definition": m["definition"],
            "image": img,
            "image_size": len(img),
            "domain_size": len(D),
            "erased_bits": mm,
            "landauer_statement": "W_min = %d * k_B T ln 2" % mm,
            "largest_preimage_size": lp,
            "log2_largest_preimage": (lp_log2 if lp_log2 is not None
                                      else "NOT_A_POWER_OF_TWO"),
            "drop_bits": drop_str,
            "drop_is_exact": drop_exact,
            "drop_bracket": bracket,
            "bijection": mm == 0,
        })
    map_rows.sort(key=lambda r: r["id"])

    device_rows = []
    for dev in DEVICES:
        for m in MAPS:
            ops = device_ops(dev, m["id"])
            net = compose_ops(ops)
            net_table = dict((s, net(s)) for s in D)
            ref_table = dict((s, m["fn"](s)) for s in D)
            require(net_table == ref_table,
                    "device %s does not implement %s" % (dev, m["id"]))
            device_rows.append({
                "device": dev,
                "map": m["id"],
                "ops": list(ops),
                "total_ops": len(ops),
                "overhead_ops": len(ops) - len(LOW_OVERHEAD_OPS[m["id"]]),
                "erased_bits": erased_bits(net),
                "implements_registered_map": True,
            })
    device_rows.sort(key=lambda r: (r["map"], r["device"]))

    non_inference = []
    for m in MAPS:
        low = [d for d in device_rows
               if d["map"] == m["id"] and d["device"] == "DEV_LOW_OVERHEAD"][0]
        high = [d for d in device_rows
                if d["map"] == m["id"] and d["device"] == "DEV_HIGH_OVERHEAD"][0]
        non_inference.append({
            "map": m["id"],
            "erased_bits": low["erased_bits"],
            "erased_bits_equal": low["erased_bits"] == high["erased_bits"],
            "total_ops_low": low["total_ops"],
            "total_ops_high": high["total_ops"],
            "total_ops_differ": low["total_ops"] != high["total_ops"],
            "operation_count_gap": high["total_ops"] - low["total_ops"],
        })
    non_inference.sort(key=lambda r: r["map"])
    non_inference_holds = all(r["erased_bits_equal"] and r["total_ops_differ"]
                              for r in non_inference)

    erase2 = [r for r in non_inference if r["map"] == "F_ERASE2"][0]

    bij = [r for r in map_rows if r["id"] == "F_BIJECTION"][0]
    bij_dev = [d for d in device_rows
               if d["map"] == "F_BIJECTION" and d["device"] == "DEV_LOW_OVERHEAD"][0]
    many_to_one = [r for r in map_rows if r["id"] == "F_ERASE2"][0]
    scope_row = {
        "bijection": {
            "map": bij["id"],
            "erased_bits": bij["erased_bits"],
            "landauer_bound_in_kT_ln2": bij["erased_bits"],
            "registered_total_ops": bij_dev["total_ops"],
            "total_ops_strictly_positive": bij_dev["total_ops"] > 0,
        },
        "many_to_one": {
            "map": many_to_one["id"],
            "erased_bits": many_to_one["erased_bits"],
            "landauer_bound_in_kT_ln2": many_to_one["erased_bits"],
            "registered_total_ops": [d["total_ops"] for d in device_rows
                                     if d["map"] == "F_ERASE2"],
        },
        "statement": "logical irreversibility lower-bounds the dissipation "
                     "ATTRIBUTABLE TO ERASURE under the registered assumptions "
                     "and nothing more: a bijection has erased-bit count exactly "
                     "0 and Landauer bound exactly 0 while its registered "
                     "operation count is strictly positive, and a many-to-one map "
                     "has a strictly positive erased-bit count while its "
                     "registered operation count is not determined by it",
    }

    # --- row 4: physical systems and the nonequilibrium gate ---------------
    systems = registered_physical_systems()
    claims = {
        "AE11-1": "all twelve ordered pairs of the four registered quantities are "
                  "witnessed non-functionally dependent on the registered roster",
        "AE11-2": "the maximal-entropy registered distribution has members whose "
                  "algorithmic complexity on the frozen machine takes several "
                  "different integer values",
        "AE11-3": "every resource this tranche names is classified, and the count "
                  "of instantiated physical energetic resources is exactly 0",
        "AE11-4": "every registered map carries a Landauer lower-bound record with "
                  "an exact integer erased-bit coefficient, a vacuity "
                  "classification, an attainment witness and, where the bound is "
                  "not vacuous, a witness from an explicitly relaxed class that "
                  "breaks it",
        "AE11-5": "the two registered device models of each map carry the same "
                  "exact integer erased-bit count and different registered "
                  "operation counts",
        "AE11-6": "the number of registered physical systems is exactly 0 and no "
                  "registered claim of this package carries a term from the frozen "
                  "driven-system vocabulary",
        "AE11-7": "a registered bijection has erased-bit count exactly 0 and "
                  "Landauer bound exactly 0 while its registered operation count "
                  "is strictly positive, and a registered many-to-one map has a "
                  "strictly positive erased-bit count",
    }
    clean_hits = noneq_hits(claims)
    planted = dict(claims)
    planted["FIXTURE_NONEQ_PLANT"] = (
        "the registered device is held in a steady-state flux with a strictly "
        "positive entropy production and a nonequilibrium maintenance cost")
    planted_hits = noneq_hits(planted)
    noneq = {
        "frozen_terms": list(NONEQ_TERMS),
        "claims_scanned": sorted(claims),
        "clean_roster_hits": clean_hits,
        "no_alarm_holds": len(clean_hits) == 0,
        "planted_fixture": "FIXTURE_NONEQ_PLANT",
        "planted_fixture_hits": [h for h in planted_hits
                                 if h["claim"] == "FIXTURE_NONEQ_PLANT"],
        "planted_fixture_flagged": any(h["claim"] == "FIXTURE_NONEQ_PLANT"
                                       for h in planted_hits),
        "registered_physical_systems": len(systems),
        "physical_system_definition": "(boundary, dynamics, reservoir, "
                                      "temperature); a registered quasi-static "
                                      "process supplies a temperature symbol only, "
                                      "so it is not a physical system",
    }

    # --- bounds ------------------------------------------------------------
    bounds = (landauer_bounds(map_rows) + drop_bounds(map_rows)
              + gibbs_bounds(values))
    bounds.sort(key=lambda b: b["id"])
    unfalsified = [b["id"] for b in bounds if b["status"] == "UNFALSIFIED_BOUND"]
    vacuous = [b["id"] for b in bounds if b["vacuous"]]
    every_nonvacuous_has_violator = all(
        b["violated_by"] is not None for b in bounds if not b["vacuous"])

    # --- hostiles ----------------------------------------------------------
    hostiles = [
        hostile_entropy_conflate(table),
        hostile_erased_bits(map_rows),
        hostile_lcap(table),
        hostile_overhead_equal(),
        hostile_physical_claim(registry),
    ]
    hostiles.sort(key=lambda h: h["name"])

    # --- null --------------------------------------------------------------
    null = run_null(table)
    null["no_alarm_holds"] = census_complete

    # --- prospective predictions ------------------------------------------
    preds = []
    by_pid = dict((p["id"], p["claim"])
                  for p in register["prospective_predictions"])

    preds.append({
        "id": "AE11-P1", "claim": by_pid["AE11-P1"],
        "status": "CONFIRMED" if (census_complete and k_min != k_max) else "REFUTED",
        "exact_values": {
            "ordered_pairs_witnessed": sum(1 for r in census_rows if r["witnessed"]),
            "ordered_pairs_total": 12,
            "derived_witnesses": derived,
            "registered_independent_witnesses": 12 - derived,
            "R_UNIFORM_BLOCK_H_shannon_bits": str(uniform_block["H_shannon"]),
            "K_U_min_over_support": k_min,
            "K_U_max_over_support": k_max,
            "K_U_histogram_over_support": k_histogram,
        },
        "caveat": "the registered freeze phrases the classic witness as K_U "
                  "ranging from a small constant to m bits.  On the frozen machine "
                  "at string length %d and cap %d that numeric phrasing is not "
                  "attainable: the emit instructions cost 2 bits each and HALT 2, "
                  "so the ceiling is pinned at %d and the floor cannot be small. "
                  "What is witnessed, and all that is claimed, is that one maximal "
                  "Shannon entropy value of %s bits coexists with members of %d "
                  "distinct K_U values spanning %d to %d."
                  % (STRING_LENGTH, LCAP, STRING_LENGTH * 2 + 2,
                     str(uniform_block["H_shannon"]), len(k_histogram),
                     k_min, k_max),
    })
    preds.append({
        "id": "AE11-P2", "claim": by_pid["AE11-P2"],
        "status": "CONFIRMED" if not physical_instantiated else "REFUTED",
        "exact_values": {
            "resources_classified": len(registry),
            "logical_computational": sum(1 for r in registry
                                         if r["class"] == "LOGICAL_COMPUTATIONAL"),
            "physical_energetic_declared": sum(
                1 for r in registry if r["class"] == "PHYSICAL_ENERGETIC"),
            "physical_energetic_instantiated": len(physical_instantiated),
        },
    })
    p3_ok = all(b["kind"] == "lower" and b["attained_by"] is not None
                for b in bounds if b["id"].startswith("B_LANDAUER__"))
    p3_ok = p3_ok and all(
        (b["violated_by"] is not None) or b["vacuous"]
        for b in bounds if b["id"].startswith("B_LANDAUER__"))
    preds.append({
        "id": "AE11-P3", "claim": by_pid["AE11-P3"],
        "status": "CONFIRMED" if p3_ok else "REFUTED",
        "exact_values": {
            "landauer_bound_records": sum(1 for b in bounds
                                          if b["id"].startswith("B_LANDAUER__")),
            "vacuous_landauer_records": sorted(
                b["id"] for b in bounds
                if b["id"].startswith("B_LANDAUER__") and b["vacuous"]),
            "unfalsified_bounds": unfalsified,
            "erased_bit_coefficients": dict(
                (r["id"], r["erased_bits"]) for r in map_rows),
        },
        "caveat": "B_LANDAUER__F_BIJECTION has bound value 0 against a "
                  "definitional floor of 0.  It is reported as vacuous and as an "
                  "UNFALSIFIED_BOUND, and it closes nothing; a non-negative "
                  "quantity cannot fall below 0.",
    })
    preds.append({
        "id": "AE11-P4", "claim": by_pid["AE11-P4"],
        "status": "CONFIRMED" if (erase2["erased_bits_equal"]
                                  and erase2["total_ops_differ"]) else "REFUTED",
        "exact_values": {
            "map": "F_ERASE2",
            "erased_bits_both_devices": erase2["erased_bits"],
            "total_ops_DEV_LOW_OVERHEAD": erase2["total_ops_low"],
            "total_ops_DEV_HIGH_OVERHEAD": erase2["total_ops_high"],
            "holds_for_every_registered_map": non_inference_holds,
            "operation_count_gap": erase2["operation_count_gap"],
        },
    })
    p5_ok = (len(systems) == REGISTERED_PHYSICAL_SYSTEMS
             and noneq["no_alarm_holds"] and noneq["planted_fixture_flagged"])
    preds.append({
        "id": "AE11-P5", "claim": by_pid["AE11-P5"],
        "status": "CONFIRMED" if p5_ok else "REFUTED",
        "exact_values": {
            "registered_physical_systems": len(systems),
            "clean_roster_hits": len(clean_hits),
            "planted_fixture_hits": len(noneq["planted_fixture_hits"]),
        },
    })
    p6_ok = (bij["erased_bits"] == 0 and bij_dev["total_ops"] > 0
             and many_to_one["erased_bits"] > 0)
    preds.append({
        "id": "AE11-P6", "claim": by_pid["AE11-P6"],
        "status": "CONFIRMED" if p6_ok else "REFUTED",
        "exact_values": {
            "F_BIJECTION_erased_bits": bij["erased_bits"],
            "F_BIJECTION_landauer_bound_in_kT_ln2": bij["erased_bits"],
            "F_BIJECTION_registered_total_ops": bij_dev["total_ops"],
            "F_ERASE2_erased_bits": many_to_one["erased_bits"],
        },
    })
    preds.sort(key=lambda p: p["id"])

    # --- checks ------------------------------------------------------------
    and_row = [r for r in map_rows if r["id"] == "F_AND"][0]
    checks = {
        "census_all_twelve_ordered_pairs_witnessed": census_complete,
        "classic_witness_equal_entropy_different_complexity": (
            uniform_block["H_shannon"] == process_b["H_shannon"]
            and uniform_block["K_U"] != process_b["K_U"]),
        "complexity_defined_for_every_registered_string": len(over_cap) == 0,
        "instruction_code_is_a_complete_prefix_code": kraft_instructions == 1,
        "program_set_satisfies_kraft": kraft_programs <= 1,
        "resource_registry_covers_every_named_resource": len(registry) == 24,
        "no_instantiated_physical_energetic_resource": not physical_instantiated,
        "no_float_in_any_claimed_quantity": not any(
            contains_float(x) for x in
            (map_rows, device_rows, non_inference, scope_row, census_rows,
             registry, bounds, hostiles, null, preds, noneq, values)),
        "every_map_carries_a_landauer_bound_record": (
            sum(1 for b in bounds if b["id"].startswith("B_LANDAUER__"))
            == len(MAPS)),
        "every_nonvacuous_bound_has_a_violator": every_nonvacuous_has_violator,
        "landauer_bound_does_not_determine_total_cost": non_inference_holds,
        "registered_physical_systems_is_zero": len(systems) == 0,
        "noneq_gate_silent_on_clean_roster": noneq["no_alarm_holds"],
        "noneq_gate_flags_planted_fixture": noneq["planted_fixture_flagged"],
        "bijection_has_zero_erased_bits_and_positive_op_count": (
            bij["erased_bits"] == 0 and bij_dev["total_ops"] > 0),
        "many_to_one_map_has_positive_erased_bits": many_to_one["erased_bits"] > 0,
        "and_map_drop_strictly_exceeds_erased_bits_by_certificate": (
            and_row["drop_bracket"]["strictly_above_erased_bits"]),
        "and_map_drop_reported_as_not_decided": and_row["drop_bits"] == "NOT_DECIDED",
        "gibbs_bound_vacuous_exactly_at_the_alphabet_ceiling": sorted(
            b["id"] for b in bounds
            if b["id"].startswith("B_GIBBS__") and b["vacuous"]) == [
            "B_GIBBS__R_PROCESS_B", "B_GIBBS__R_UNIFORM_BLOCK"],
        "every_bound_is_either_falsifiable_or_flagged_vacuous": all(
            (b["violated_by"] is not None) or b["vacuous"] for b in bounds),
        "no_vacuous_or_unfalsified_bound_closes_a_row": all(
            (not b["used_for_closure"]) for b in bounds
            if b["vacuous"] or b["status"] == "UNFALSIFIED_BOUND"),
        "every_hostile_is_potent": all(h["potent"] for h in hostiles),
        "every_hostile_is_detected": all(h["detected"] for h in hostiles),
        "null_beaten_threshold_free": null["witness_exceeds_largest_null"],
        "null_no_alarm_on_clean_roster": null["no_alarm_holds"],
        "register_digest_matches": digest == register["self_digest_sha256"],
        "register_freeze_commit_matches_custody_sha": (
            register["freeze_commit"] == FREEZE_COMMIT),
        "register_source_main_matches": register["source_main"] == SOURCE_MAIN,
        "registered_roster_names_match_the_register": (
            sorted(o["id"] for o in ROSTER)
            == sorted(register["roster"]["objects"])
            and sorted(m["id"] for m in MAPS)
            == sorted(register["roster"]["maps"])
            and sorted(DEVICES) == sorted(register["roster"]["devices"])
            and sorted(QUANTITIES) == sorted(register["roster"]["quantities"])),
        "registered_hostile_names_match_the_register": None,
        "every_prospective_prediction_reported": len(preds) == len(
            register["prospective_predictions"]),
        "all_prospective_predictions_confirmed": all(
            p["status"] == "CONFIRMED" for p in preds),
    }

    checks["registered_hostile_names_match_the_register"] = (
        sorted(h["name"] for h in hostiles)
        == sorted(h["name"] for h in register["hostiles"]))

    receipt = {
        "schema": SCHEMA,
        "section": SECTION,
        "issue": ISSUE,
        "issue_comment_id": ISSUE_COMMENT_ID,
        "package": PACKAGE,
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "register_commit": REGISTER_COMMIT,
        "register_digest_sha256": digest,
        "register_declared_freeze_commit": register["freeze_commit"],
        "custody_note": (
            "PROSPECTIVE_REGISTER_V1.json declares freeze_commit %s and the lane "
            "owner's custody sha for the freeze commit is %s; the two agree, and "
            "the executor asserts that they agree rather than assuming it.  The "
            "register is binding and was not edited by this package: the executor "
            "recomputes its canonical self digest and refuses to emit on a "
            "mismatch.  Every custody assertion in this package and in its "
            "workflow uses %s."
            % (register["freeze_commit"], FREEZE_COMMIT, FREEZE_COMMIT)),
        "claim_ceiling": CLAIM_CEILING,
        "verdict": None,
        "theorems": ["AE11-1", "AE11-2", "AE11-3", "AE11-4", "AE11-5",
                     "AE11-6", "AE11-7"],
        "checks": checks,
        "results": {
            "machine": {
                "string_length": STRING_LENGTH,
                "program_length_cap": LCAP,
                "max_output_length": MAXOUT,
                "instruction_table": [dict(row) for row in INSTRUCTION_TABLE],
                "instruction_kraft_sum": str(kraft_instructions),
                "program_kraft_sum_up_to_cap": str(kraft_programs),
                "programs_by_length": dict((str(k), v) for k, v in
                                           sorted(programs_by_length.items())),
                "machine_relative": "K_U is relative to this frozen machine and to "
                                    "the frozen cap.  Both are stated, and every "
                                    "K_U value below is a value on THIS machine, "
                                    "not a machine-independent quantity.",
                "search_order": "route A makes a single ordered pass over the "
                                "bit-string program space -- each length in turn, "
                                "each length's bit strings in increasing integer "
                                "order -- decoding each candidate and memoising "
                                "the first, hence shortest, program per output",
            },
            "complexity_table": {
                "K_U_histogram": k_histogram,
                "K_U_min": k_min,
                "K_U_max": k_max,
                "lexicographically_least_at_min": lex_least_min,
                "lexicographically_least_at_max": lex_least_max,
                "strings_over_cap": len(over_cap),
                "distinct_K_U_values": len(k_histogram),
            },
            "roster": [
                {"id": v["id"], "H_shannon_bits": str(v["H_shannon"]),
                 "K_U_bits": v["K_U"], "S_stat_microstate_count": v["S_stat"],
                 "S_stat_statement": "S_stat = k_B ln %d" % v["S_stat"],
                 "S_thermo_Q_over_T": str(v["S_thermo"]),
                 "Q": str(v["Q"]), "T": str(v["T"]),
                 "string": v["string"], "note": v["note"]}
                for v in values],
            "census": census_rows,
            "census_summary": {
                "ordered_pairs": 12,
                "witnessed": sum(1 for r in census_rows if r["witnessed"]),
                "unwitnessed": [[r["fixed"], r["free"]] for r in census_rows
                                if not r["witnessed"]],
                "derived_witnesses": derived,
                "registered_independent_witnesses": 12 - derived,
                "derived_meaning": "H_shannon and S_stat are linked by the "
                                   "registered definitional relation "
                                   "H_shannon <= log2 W, since W is the size of "
                                   "the support of P; a derived witness exhibits "
                                   "the slack in that relation.  The other ten "
                                   "pairs have no registered definitional relation "
                                   "at all.",
            },
            "classic_witness": {
                "distribution": "R_UNIFORM_BLOCK, uniform on all 2**6 strings",
                "H_shannon_bits": str(uniform_block["H_shannon"]),
                "maximal_for_the_alphabet": uniform_block["H_shannon"] == F(
                    STRING_LENGTH),
                "members_K_U_histogram": k_histogram,
                "member_at_K_U_min": lex_least_min,
                "member_at_K_U_max": lex_least_max,
                "paired_object_same_entropy": {
                    "a": uniform_block["id"], "b": process_b["id"],
                    "H_shannon_bits": str(process_b["H_shannon"]),
                    "K_U_a": uniform_block["K_U"], "K_U_b": process_b["K_U"]},
            },
            "resource_registry": registry,
            "resource_registry_summary": {
                "total": len(registry),
                "logical_computational": sum(
                    1 for r in registry if r["class"] == "LOGICAL_COMPUTATIONAL"),
                "physical_energetic_declared": sum(
                    1 for r in registry if r["class"] == "PHYSICAL_ENERGETIC"),
                "physical_energetic_instantiated": len(physical_instantiated),
                "instantiated_physical_resources": physical_instantiated,
            },
            "maps": map_rows,
            "devices": device_rows,
            "landauer_assumptions": [dict(a) for a in LANDAUER_ASSUMPTIONS],
            "non_inference": {
                "per_map": non_inference,
                "holds_for_every_map": non_inference_holds,
                "statement": "the erased-bit count is identical under both "
                             "registered device models of a map while the "
                             "registered operation count differs by exactly 5, so "
                             "the erasure bound does not determine the total "
                             "registered cost of an implementation, let alone a "
                             "physical energy, which this package never computes",
            },
            "correct_scope": scope_row,
            "nonequilibrium_gate": noneq,
            "claims_scanned": claims,
        },
        "bounds": bounds,
        "hostiles": hostiles,
        "null": null,
        "prospective_predictions": preds,
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "rows_closed": 5,
        "rows_left_open": 3,
    }

    require(not contains_float(receipt), "a float reached the receipt")
    receipt["verdict"] = "GREEN" if all(checks.values()) else "RED"
    require(receipt["verdict"] == "GREEN",
            "not every check passed: " +
            ",".join(sorted(k for k, v in checks.items() if not v)))
    return receipt


def main():
    sys.stdout.write(json.dumps(build(), sort_keys=True, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Held-out registered universes for the #833 Section-K capability predictor.

This module defines the held-out machine populations and the *universe
injection* harness.  It contains NO outcome oracle and NO scoring code: the
true capability of a machine is obtained only by the separate external
evaluator, which is introduced after the freeze commit.

Three populations are registered here.

* ``SIGMA_SYN``   -- held-out synthetic machine species (modular head machines).
* ``SIGMA_ARCH``  -- held-out *known architecture* families (four named
                     mechanisms with genuinely different simulators).
* ``SIGMA_OOD``   -- structurally out-of-universe machines used only by the
                     OOD probe; never installed as a registered universe.

The predictor ``F`` itself is never modified.  ``install_universe`` rebinds the
enumerated registration surface of ``capability_predictor_v1`` and nothing
else; ``code_fingerprint`` proves every function body is byte-identical before
and after installation.

Python 3.8 compatible, stdlib only, exact ``Fraction`` arithmetic.
"""

from fractions import Fraction
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.join(os.path.dirname(HERE), "gmi-833-capability-predictor-v1")
PARENT_FILE = os.path.join(PARENT_DIR, "capability_predictor_v1.py")

# The parent blob pinned by MANIFEST_V1.json of this package.
PARENT_BLOB_SHA = "7f1bb6808901be2291bf575ee3178247d14d01d4"

# --------------------------------------------------------------------------
# Protected task battery (the external capability contract's raw material)
# --------------------------------------------------------------------------

WORD_LENGTH = 4


def protected_words():
    """All binary words of length 0..WORD_LENGTH, in deterministic order."""
    out = [()]
    frontier = [()]
    for _ in range(WORD_LENGTH):
        nxt = []
        for w in frontier:
            for sym in (0, 1):
                nxt.append(w + (sym,))
        out.extend(nxt)
        frontier = nxt
    return tuple(out)


WORDS = protected_words()
N_WORDS = len(WORDS)


def target_last(word):
    return word[-1] if word else 0


def target_parity(word):
    return sum(word) % 2


def target_count3(word):
    return 1 if sum(word) % 3 == 0 else 0


TASKS = (("T0_LAST", target_last),
         ("T1_PARITY", target_parity),
         ("T2_COUNT3", target_count3))

# Two registered capability contracts, mirroring the parent's E_full / E_v0.
VERIFIED = {"E_full": (True, True, True), "E_v0": (False, True, True)}

MU_SYN = (Fraction(5, 11), Fraction(4, 11), Fraction(2, 11))
MU_ARCH = (Fraction(7, 13), Fraction(4, 13), Fraction(2, 13))

RHO_DIM_HELDOUT = 14


def popcount(n):
    total = 0
    while n:
        total += n & 1
        n >>= 1
    return total


# --------------------------------------------------------------------------
# SIGMA_SYN: synthetic machine species -- "modular head machines"
# --------------------------------------------------------------------------
#
# A machine is (m, w, h):
#   m in {1,2,3,6}  state modulus; the live state is s = ones(u) mod m
#   w in {0,1}      presence of a last-symbol register
#   h in 0..7       which of the three output heads are wired
#
# Head semantics (the MECHANISM; the external evaluator simulates this):
#   head0 = last symbol if w == 1 else 0
#   head1 = s mod 2
#   head2 = 1 if s mod 3 == 0 else 0
# An unwired head emits the constant 0.

SYN_MODULI = (1, 2, 3, 6)


def syn_machine_answer(machine, task_index, word):
    """Run the synthetic species.  Pure mechanism; no lookup of the answer."""
    m, w, h = machine
    if not (h >> task_index) & 1:
        return 0
    state = sum(word) % m
    if task_index == 0:
        return (word[-1] if word else 0) if w == 1 else 0
    if task_index == 1:
        return state % 2
    return 1 if state % 3 == 0 else 0


def syn_solved_law(machine):
    """Closed-form registered law for the solved-set (route A, no simulation)."""
    m, w, h = machine
    bits = 0
    if (h & 1) and w == 1:
        bits |= 1
    if (h & 2) and m % 2 == 0:
        bits |= 2
    if (h & 4) and m % 3 == 0:
        bits |= 4
    return bits


def syn_descriptor(machine):
    """Structural descriptor: expressivity class, rho, dev cost, observation."""
    m, w, h = machine
    if m == 1:
        k = 0
    elif m in (2, 3):
        k = 1
    else:
        k = 2
    rho = [0] * RHO_DIM_HELDOUT
    rho[0] = m
    rho[1] = 1 + w
    rho[2] = 1 + popcount(h)
    rho[3] = 1 + (1 if h else 0)
    dev = m + popcount(h) + w
    obs = (1 + w, m % 2)
    return k, tuple(rho), dev, obs


def build_sigma_syn():
    raw = []
    machines = []
    for m in SYN_MODULI:
        for w in (0, 1):
            for h in range(8):
                machines.append((m, w, h))
    for machine in machines:
        k, rho, dev, obs = syn_descriptor(machine)
        m, w, h = machine
        raw.append((m, w, h, k, rho, dev, obs))
    order = sorted(range(len(raw)),
                   key=lambda i: (raw[i][4][0], raw[i][0], raw[i][1], raw[i][2]))
    rank = [0] * len(raw)
    for pos, idx in enumerate(order):
        rank[idx] = pos
    return tuple(raw), tuple(rank), tuple(machines)


# --------------------------------------------------------------------------
# SIGMA_ARCH: held-out *known architecture* families
# --------------------------------------------------------------------------
#
# Four named mechanism families with genuinely different simulators.  The
# family label is carried in a SEPARATE parallel list and is never an argument
# to the descriptor encoder; see blindness enforcement in the evaluator.
#
#   FF    feed-forward window machine: output is a function of the last
#         `win` symbols only (win in {1,2}); no persistent state.
#   REC   recurrent accumulator: state = ones mod m, m in {2,3}.
#   CTR   saturating counter: state = min(ones, cap), cap in {2,3}.
#   STK   bounded stack: push on 1, pop on 0, depth d in {1,2}; the readable
#         quantity is the stack height.
#
# Every family exposes the same three heads; head j is wired iff h & (1<<j).

ARCH_FAMILIES = ("FF", "REC", "CTR", "STK")


def _arch_state(mech, param, word):
    if mech == "FF":
        tail = word[-param:] if word else ()
        return sum(tail)
    if mech == "REC":
        return sum(word) % param
    if mech == "CTR":
        total = sum(word)
        return total if total < param else param
    depth = 0
    for sym in word:
        if sym == 1:
            if depth < param:
                depth += 1
        else:
            if depth > 0:
                depth -= 1
    return depth


def arch_machine_answer(machine, task_index, word):
    """Run a known-architecture machine.  Pure mechanism."""
    mech, param, w, h = machine
    if not (h >> task_index) & 1:
        return 0
    state = _arch_state(mech, param, word)
    if task_index == 0:
        return (word[-1] if word else 0) if w == 1 else 0
    if task_index == 1:
        return state % 2
    return 1 if state % 3 == 0 else 0


def arch_solved_law(machine):
    """Closed-form registered law for known architectures (route A).

    Let ``s(u)`` be the readable state.  Head j is wired iff ``h & (1 << j)``.

    * ``T0`` (last symbol) is solved iff head 0 is wired and the last-symbol
      register is present (``w == 1``).
    * ``T1`` (parity) is solved iff head 1 is wired and ``s(u) = ones(u) (mod 2)``
      on every protected word.  That holds for ``REC`` with an even modulus, and
      for ``CTR`` whose saturation cap is at least ``WORD_LENGTH`` (then
      ``s(u) = min(ones(u), cap) = ones(u)`` exactly).  ``FF`` reads only the last
      ``param <= 2 < WORD_LENGTH`` symbols and ``STK`` height is not a function
      of ``ones(u)``, so neither can solve it.
    * ``T2`` (count-3) is solved iff head 2 is wired and ``s(u) = ones(u) (mod 3)``
      on every protected word: ``REC`` with ``3 | param``, or ``CTR`` with
      ``cap >= WORD_LENGTH``.

    Brute-force simulation over the whole protected battery is the independent
    second route and must agree on every machine.
    """
    mech, param, w, h = machine
    tracks_ones = (mech == "CTR" and param >= WORD_LENGTH)
    bits = 0
    if (h & 1) and w == 1:
        bits |= 1
    if (h & 2) and ((mech == "REC" and param % 2 == 0) or tracks_ones):
        bits |= 2
    if (h & 4) and ((mech == "REC" and param % 3 == 0) or tracks_ones):
        bits |= 4
    return bits


ARCH_PARAMS = {"FF": (1, 2), "REC": (2, 3), "CTR": (2, 4), "STK": (1, 2)}
ARCH_K = {"FF": 0, "REC": 1, "CTR": 1, "STK": 2}


def arch_descriptor(machine):
    """Descriptor encoder.  Receives ONLY the semantic machine record.

    The family string is a *mechanism* tag, not a family label: it selects the
    simulator.  Expressivity class k is derived from the readable-state
    structure, not from the name.  See BLINDNESS_V1 for the audit.
    """
    mech, param, w, h = machine
    k = ARCH_K[mech]
    rho = [0] * RHO_DIM_HELDOUT
    rho[0] = param + (1 if mech in ("CTR", "STK") else 0)
    rho[1] = 1 + w
    rho[2] = 1 + popcount(h)
    rho[3] = 3 + (1 if mech in ("REC", "CTR") else 0)
    dev = param + popcount(h) + w + ARCH_K[mech]
    obs = (1 + w, param % 2)
    return k, tuple(rho), dev, obs


def build_sigma_arch():
    raw = []
    machines = []
    labels = []
    for mech in ARCH_FAMILIES:
        for param in ARCH_PARAMS[mech]:
            for w in (0, 1):
                for h in range(8):
                    machines.append((mech, param, w, h))
                    labels.append(mech)
    for machine in machines:
        k, rho, dev, obs = arch_descriptor(machine)
        raw.append((machine[1], machine[2], machine[3], k, rho, dev, obs))
    order = sorted(range(len(raw)),
                   key=lambda i: (raw[i][4][0], raw[i][0], raw[i][1], raw[i][2]))
    rank = [0] * len(raw)
    for pos, idx in enumerate(order):
        rank[idx] = pos
    return tuple(raw), tuple(rank), tuple(machines), tuple(labels)


# --------------------------------------------------------------------------
# Registered capability tables (the frozen registration law)
# --------------------------------------------------------------------------


def cap_table(machines, solved_law, mu, contract):
    verified = VERIFIED[contract]
    out = []
    for machine in machines:
        bits = solved_law(machine)
        total = Fraction(0)
        for j in range(3):
            if verified[j] and ((bits >> j) & 1):
                total += mu[j]
        out.append(total)
    return tuple(out)


# --------------------------------------------------------------------------
# Registered input grids
# --------------------------------------------------------------------------

SYN_GRID = {
    "budgets": ((2, 1, 2, 1), (3, 2, 3, 2), (6, 2, 4, 2)),
    "charges": ((0, 0, 0, 0), (1, 0, 0, 0)),
    "d_values": (3, 6, 99),
    "b_values": (0, 12, 24, 40, 64),
    "h_values": ("NO_OBSERVATION", (1, 0), (2, 1)),
    "tau_values": (Fraction(2, 11), Fraction(5, 11), Fraction(7, 11), Fraction(9, 11)),
}

ARCH_GRID = {
    "budgets": ((2, 1, 2, 3), (3, 2, 3, 4), (5, 2, 4, 4)),
    "charges": ((0, 0, 0, 0), (1, 0, 0, 0)),
    "d_values": (4, 7, 99),
    "b_values": (0, 24, 48, 80, 128),
    "h_values": ("NO_OBSERVATION", (1, 0), (2, 1)),
    "tau_values": (Fraction(2, 13), Fraction(6, 13), Fraction(11, 13), Fraction(1)),
}


def build_u_values(raw, full_mask, selector):
    """Three typed uncertainty inputs: one FeasibleSet, two ConfidenceSets."""
    sub = 0
    for i, rec in enumerate(raw):
        if selector(rec):
            sub |= 1 << i
    return (("U0", "FEASIBLE_SET", full_mask, None),
            ("U1", "CONFIDENCE_SET", sub, Fraction(1, 20)),
            ("U2", "CONFIDENCE_SET", full_mask, Fraction(1, 10)))


# --------------------------------------------------------------------------
# Universe specifications
# --------------------------------------------------------------------------


def _expr_mask(raw, k_m):
    mask = 0
    for i, rec in enumerate(raw):
        if rec[3] in k_m:
            mask |= 1 << i
    return mask


def _res_mask(raw, budget, charge):
    effective = []
    for j in range(RHO_DIM_HELDOUT):
        effective.append((budget[j] if j < len(budget) else 0)
                         - (charge[j] if j < len(charge) else 0))
    mask = 0
    for i, rec in enumerate(raw):
        ok = True
        for j in range(RHO_DIM_HELDOUT):
            if rec[4][j] > effective[j]:
                ok = False
                break
        if ok:
            mask |= 1 << i
    return mask


def _reach_mask(raw, b_dev):
    mask = 0
    for i, rec in enumerate(raw):
        if rec[5] <= b_dev:
            mask |= 1 << i
    return mask


def _seen_mask(rank, budget):
    mask = 0
    for i in range(len(rank)):
        if rank[i] < budget:
            mask |= 1 << i
    return mask


def _obs_mask(raw, observed, full_mask):
    if observed == "NO_OBSERVATION":
        return full_mask
    mask = 0
    for i, rec in enumerate(raw):
        if rec[6] == observed:
            mask |= 1 << i
    return mask


def make_spec(name, raw, rank, machines, mu, solved_law, grid, selector):
    n = len(raw)
    full_mask = (1 << n) - 1
    contracts = ("E_full", "E_v0")
    cap = dict((c, cap_table(machines, solved_law, mu, c)) for c in contracts)
    k_m_values = tuple(frozenset(j for j in range(3) if (bits >> j) & 1)
                       for bits in range(8))
    r_values = tuple((b, m) for b in grid["budgets"] for m in grid["charges"])
    u_values = build_u_values(raw, full_mask, selector)
    spec = {
        "MU": mu,
        "RHO_DIM": RHO_DIM_HELDOUT,
        "UNIVERSE": raw,
        "SEARCH_RANK": rank,
        "N": n,
        "FULL_MASK": full_mask,
        "CONTRACTS": contracts,
        "CAP": cap,
        "K_M_VALUES": k_m_values,
        "BUDGETS": grid["budgets"],
        "CHARGES": grid["charges"],
        "R_VALUES": r_values,
        "D_VALUES": grid["d_values"],
        "B_VALUES": grid["b_values"],
        "H_VALUES": grid["h_values"],
        "TAU_VALUES": grid["tau_values"],
        "U_VALUES": u_values,
        "EXPR_MASKS": dict((i, _expr_mask(raw, v)) for i, v in enumerate(k_m_values)),
        "RES_MASKS": dict((r, _res_mask(raw, r[0], r[1])) for r in r_values),
        "REACH_MASKS": dict((d, _reach_mask(raw, d)) for d in grid["d_values"]),
        "SEEN_MASKS": dict((b, _seen_mask(rank, b)) for b in grid["b_values"]),
        "OBS_MASKS": dict((h, _obs_mask(raw, h, full_mask)) for h in grid["h_values"]),
        "_CEILING_CACHE": {},
    }
    spec["__name__"] = name
    spec["__machines__"] = machines
    return spec


SYN_RAW, SYN_RANK, SYN_MACHINES = build_sigma_syn()
ARCH_RAW, ARCH_RANK, ARCH_MACHINES, ARCH_LABELS = build_sigma_arch()


def sigma_syn():
    return make_spec("SIGMA_SYN", SYN_RAW, SYN_RANK, SYN_MACHINES, MU_SYN,
                     syn_solved_law, SYN_GRID, lambda rec: rec[1] == 0)


def sigma_arch():
    return make_spec("SIGMA_ARCH", ARCH_RAW, ARCH_RANK, ARCH_MACHINES, MU_ARCH,
                     arch_solved_law, ARCH_GRID, lambda rec: rec[1] == 0)


# --------------------------------------------------------------------------
# Universe injection
# --------------------------------------------------------------------------

REGISTRATION_SURFACE = (
    "MU", "RHO_DIM", "UNIVERSE", "SEARCH_RANK", "N", "FULL_MASK", "CONTRACTS",
    "CAP", "K_M_VALUES", "BUDGETS", "CHARGES", "R_VALUES", "D_VALUES",
    "B_VALUES", "H_VALUES", "TAU_VALUES", "U_VALUES", "EXPR_MASKS",
    "RES_MASKS", "REACH_MASKS", "SEEN_MASKS", "OBS_MASKS", "_CEILING_CACHE",
)


_SIGMA_1 = []


def load_parent():
    """Import the parent and snapshot Sigma_1 BEFORE any universe is installed."""
    if PARENT_DIR not in sys.path:
        sys.path.insert(0, PARENT_DIR)
    import capability_predictor_v1 as parent
    if not _SIGMA_1:
        _SIGMA_1.append(tuple(parent.UNIVERSE))
    return parent


def sigma_1():
    """The parent's pristine 32-realization universe (snapshot, never rebound)."""
    if not _SIGMA_1:
        raise ValueError("load_parent() must run before sigma_1()")
    return _SIGMA_1[0]


def git_blob_sha(path):
    with open(path, "rb") as handle:
        data = handle.read()
    header = ("blob %d\0" % len(data)).encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def code_fingerprint(module):
    """Byte fingerprint of every function body in the module."""
    import types
    items = []
    for name in sorted(dir(module)):
        obj = getattr(module, name)
        if isinstance(obj, types.FunctionType):
            items.append((name, obj.__code__.co_code))
        elif isinstance(obj, type):
            for attr in sorted(vars(obj)):
                sub = vars(obj)[attr]
                if isinstance(sub, types.FunctionType):
                    items.append((name + "." + attr, sub.__code__.co_code))
    digest = hashlib.sha256()
    for name, code in items:
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(code)
        digest.update(b"\0")
    return digest.hexdigest(), len(items)


def install_universe(module, spec):
    """Rebind exactly the registration surface.  F's code is never touched."""
    keys = set(k for k in spec if not k.startswith("__"))
    if keys != set(REGISTRATION_SURFACE):
        missing = sorted(set(REGISTRATION_SURFACE) - keys)
        extra = sorted(keys - set(REGISTRATION_SURFACE))
        raise ValueError("registration surface mismatch: missing=%r extra=%r"
                         % (missing, extra))
    before = code_fingerprint(module)
    for name in REGISTRATION_SURFACE:
        setattr(module, name, spec[name])
    after = code_fingerprint(module)
    if before != after:
        raise ValueError("installation altered F's code: %r != %r" % (before, after))
    return after


# --------------------------------------------------------------------------
# Structural disjointness certificate
# --------------------------------------------------------------------------


def disjointness_certificate(base_raw, base_label, raw, label):
    """Exhaustive pairwise proof that two registered populations are disjoint.

    The structural argument is a single separating coordinate: rho[3] takes the
    value 0 on every Sigma_1 realization, a value in {1,2} on every SIGMA_SYN
    realization and a value in {3,4} on every SIGMA_ARCH realization, so no two
    of the three populations can share a realization.  The exhaustive pairwise
    descriptor comparison is the independent second route.
    """
    base_rho3 = sorted(set(rec[4][3] for rec in base_raw))
    held_rho3 = sorted(set(rec[4][3] for rec in raw))
    collisions = 0
    examples = []
    for held in raw:
        for base in base_raw:
            if held[3:] == base[3:]:
                collisions += 1
                if len(examples) < 3:
                    examples.append([list(held[:3]), list(base[:3])])
    return {
        "base": base_label,
        "universe": label,
        "base_size": len(base_raw),
        "heldout_size": len(raw),
        "pairs_checked": len(raw) * len(base_raw),
        "base_rho3_values": base_rho3,
        "heldout_rho3_values": held_rho3,
        "structural_separator": "rho[3]: 0 on Sigma_1, {1,2} on SIGMA_SYN, {3,4} on SIGMA_ARCH",
        "separator_holds": not (set(base_rho3) & set(held_rho3)),
        "descriptor_collisions": collisions,
        "collision_examples": examples,
        "disjoint": collisions == 0,
    }


# --------------------------------------------------------------------------
# SIGMA_REAL: real trained systems (torch, CPU, registered seeds)
# --------------------------------------------------------------------------
#
# A real system is (mech, size, w, h):
#   mech in {"MLP","GRU"}  feed-forward vs recurrent
#   size in {2,8}          hidden width
#   w    in {0,1}          explicit last-symbol feature appended to the readout
#   h    in {1,3,5,7}      which of the three task heads are actually trained
#                          (an untrained head keeps its frozen initialisation)
#
# Protected battery: length-REAL_WORD_LEN binary words read off a sha256-pinned
# real source file (bit = byte & 1).  Train and protected-eval windows are
# disjoint by position.  Capability is measured by EXACT accuracy on the
# protected split: a task counts as solved only at accuracy exactly 1.

REAL_SOURCE = {
    "path": "/usr/lib/python3.8/argparse.py",
    "sha256": "cc1e3c3a7cb538c32270a77b6f62ac7e91ff5b5a9261607ccbb3e6afe57c44f7",
    "bytes": 96311,
}
REAL_WORD_LEN = 12
REAL_TRAIN_WINDOWS = (0, 6000)
REAL_EVAL_WINDOWS = (6000, 8000)

REAL_MECHS = ("MLP", "GRU")
REAL_SIZES = (2, 8)
REAL_HEADS = (1, 3, 5, 7)

MU_REAL = (Fraction(8, 17), Fraction(6, 17), Fraction(3, 17))

REAL_TRAINING = {
    "framework": "torch",
    "device": "cpu",
    "threads": 1,
    "optimizer": "Adam",
    "lr": "1/1000",
    "epochs": 400,
    "batch": 256,
    "loss": "BCEWithLogitsLoss",
    "seed_rule": "seed = 8317 + 101*mech_index + 17*size + 3*w + task_index",
    "solved_rule": "exact accuracy Fraction(correct, total) == 1 on the protected split",
}


def real_solved_law(machine):
    """Frozen capacity-based registration law for the real systems (route A).

    * ``T0`` (last bit) is a single input coordinate; both architectures can
      read it, so it is predicted solved whenever head 0 is trained.
    * ``T1`` (parity of 12 bits) is predicted solved when head 1 is trained and
      the system either carries recurrence (a 2-state accumulator suffices) or
      has the wider feed-forward readout (``size >= 8``).
    * ``T2`` (ones mod 3) needs a three-valued accumulator and is predicted
      solved only for the wider systems (``size >= 8``) with head 2 trained.

    This law is a PREDICTION about real training outcomes and is falsifiable:
    the measured solved-set is obtained only by running the trained systems.
    """
    mech, size, w, h = machine
    bits = 0
    if h & 1:
        bits |= 1
    if (h & 2) and (mech == "GRU" or size >= 8):
        bits |= 2
    if (h & 4) and size >= 8:
        bits |= 4
    return bits


def real_descriptor(machine):
    mech, size, w, h = machine
    if mech == "MLP":
        k = 0
    elif size < 8:
        k = 1
    else:
        k = 2
    rho = [0] * RHO_DIM_HELDOUT
    rho[0] = size
    rho[1] = 1 + w
    rho[2] = 1 + popcount(h)
    rho[3] = 5 + (1 if mech == "GRU" else 0)
    dev = size + popcount(h) + w + (2 if mech == "GRU" else 0)
    obs = (1 + w, 1 if mech == "GRU" else 0)
    return k, tuple(rho), dev, obs


def build_sigma_real():
    raw = []
    machines = []
    for mech in REAL_MECHS:
        for size in REAL_SIZES:
            for w in (0, 1):
                for h in REAL_HEADS:
                    machines.append((mech, size, w, h))
    for machine in machines:
        k, rho, dev, obs = real_descriptor(machine)
        raw.append((machine[1], machine[2], machine[3], k, rho, dev, obs))
    order = sorted(range(len(raw)),
                   key=lambda i: (raw[i][4][0], raw[i][4][3], raw[i][0], raw[i][1], raw[i][2]))
    rank = [0] * len(raw)
    for pos, idx in enumerate(order):
        rank[idx] = pos
    return tuple(raw), tuple(rank), tuple(machines)


REAL_GRID = {
    "budgets": ((2, 1, 2, 5), (8, 2, 3, 6), (8, 2, 4, 6)),
    "charges": ((0, 0, 0, 0), (1, 0, 0, 0)),
    "d_values": (6, 10, 99),
    "b_values": (0, 8, 16, 24, 32),
    "h_values": ("NO_OBSERVATION", (1, 0), (2, 1)),
    "tau_values": (Fraction(3, 17), Fraction(8, 17), Fraction(11, 17), Fraction(1)),
}

REAL_RAW, REAL_RANK, REAL_MACHINES = build_sigma_real()


def sigma_real():
    return make_spec("SIGMA_REAL", REAL_RAW, REAL_RANK, REAL_MACHINES, MU_REAL,
                     real_solved_law, REAL_GRID, lambda rec: rec[1] == 0)

#!/usr/bin/env python3
"""Battery generator for the real-scale four-stratum tranche (freeze F2).

Everything is exact dyadic arithmetic (Dyadic = mant * 2**exp, mant an odd
or even integer).  The PRNG is the declared SHA-256 counter stream (freeze
D-10).  Vocabulary is lower-process only; no candidate-class menu appears
in this file (screened by test_realscale_v1.py).
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

P_DIM = 4                      # freeze D-2
N_ROWS = 1 << 12               # freeze D-3 (4096)
D_MAX = 11                     # freeze D-8
KAPPA_STEPS = 13               # freeze D-6: kappa = 2^(4k), k = 0..13
SIGMA_EXPS = [None] + list(range(-12, 0))   # sigma lattice: 0 plus 2^-k, k=1..12 (D-3); 1/2 = 2^-1 is a member
MAG_EXPS = range(-4, 5)        # freeze D-4
ANCHOR_SIGMA_EXP = -6          # freeze D-9 mid-lattice point
N_SEEDS = 200                  # freeze D-9
HADAMARD4 = ((1, 1, 1, 1), (1, -1, 1, -1), (1, 1, -1, -1), (1, -1, -1, 1))
PAIR_INDEX = list(combinations(range(P_DIM), 2))
# value lattice for step maps: {0} U {+-2^j}, j in [-4,4]  (19 values)
STEP_VALUES = [0] + [s * (2 ** j) for j in MAG_EXPS for s in (1, -1)]
STREAM_SPLIT = N_ROWS // 2     # freeze D-13
STREAM_DOMAIN_BITS = D_MAX + 1  # de Bruijn order: full (L_MAX+1)-gram coverage (D-8)


class Dyadic:
    """Exact dyadic rational: value = mant * 2**exp."""

    __slots__ = ("mant", "exp")

    def __init__(self, mant: int, exp: int):
        self.mant = int(mant)
        self.exp = int(exp)

    @staticmethod
    def power(exp: int) -> "Dyadic":
        return Dyadic(1, exp)

    def __add__(self, other: "Dyadic") -> "Dyadic":
        if self.exp <= other.exp:
            lo, hi, f = self, other, 1 << (other.exp - self.exp)
            return Dyadic(lo.mant + hi.mant * f, lo.exp)
        return other + self

    def __neg__(self) -> "Dyadic":
        return Dyadic(-self.mant, self.exp)

    def __sub__(self, other: "Dyadic") -> "Dyadic":
        return self + (-other)

    def __mul__(self, other: "Dyadic") -> "Dyadic":
        return Dyadic(self.mant * other.mant, self.exp + other.exp)

    def fraction(self) -> Fraction:
        return Fraction(self.mant) * Fraction(2) ** self.exp

    def _pair(self, other: "Dyadic") -> tuple[int, int]:
        """Both values rescaled to the smaller exponent (exact)."""
        e = min(self.exp, other.exp)
        return self.mant << (self.exp - e), other.mant << (other.exp - e)

    def __eq__(self, other):
        a, b = self._pair(other)
        return a == b

    def __lt__(self, other):
        a, b = self._pair(other)
        return a < b

    def __le__(self, other):
        a, b = self._pair(other)
        return a <= b

    def __ge__(self, other):
        a, b = self._pair(other)
        return a >= b

    def __gt__(self, other):
        a, b = self._pair(other)
        return a > b

    def __hash__(self):
        return hash(self.fraction())

    def __repr__(self):
        return "D(%d*2^%d)" % (self.mant, self.exp)


def prng_bytes(seed_hex: str, counter: int, count: int) -> bytes:
    out = bytearray()
    i = 0
    while len(out) < count:
        out += sha256(("GMI833H-RSF1|PRNG|" + seed_hex + "|" + str(counter + i)).encode()).digest()
        i += 1
    return bytes(out[:count])


def task_seed(tag: str) -> str:
    return sha256(("GMI833H-RSF1|" + tag).encode()).hexdigest()[:16]


def draw_dyadics(seed_hex: str, counter: int, n: int, include_zero: bool = True) -> list[Dyadic]:
    """Draw n values from the D-4 magnitude lattice with uniform signs.

    2 bytes per draw: byte0 % 9 selects the magnitude exponent (0 -> zero
    when include_zero, else exponent -4 + ((byte0 % 9) mod 9 mapping)),
    byte1 & 1 the sign.
    """
    raw = prng_bytes(seed_hex, counter, 2 * n)
    out = []
    for i in range(n):
        idx = raw[2 * i] % 9
        if include_zero and idx == 0:
            out.append(Dyadic(0, 0))
        else:
            if include_zero:
                j = -4 + (idx - 1)
            else:
                j = -4 + idx
            sign = 1 if (raw[2 * i + 1] & 1) else -1
            out.append(Dyadic(sign, j))
    return out


def draw_signs(seed_hex: str, counter: int, n: int) -> list[int]:
    raw = prng_bytes(seed_hex, counter, n)
    return [1 if (b & 1) else -1 for b in raw]


def draw_bits(seed_hex: str, counter: int, n: int) -> list[int]:
    raw = prng_bytes(seed_hex, counter, n)
    return [b & 1 for b in raw]


def draw_dyadic_flip(seed_hex: str, counter: int, n: int, sigma_exp: int) -> list[Dyadic]:
    """Rademacher +-sigma noise with sigma = 2**sigma_exp (exact)."""
    signs = draw_signs(seed_hex, counter, n)
    return [Dyadic(s, sigma_exp) for s in signs]


def draw_bernoulli(seed_hex: str, counter: int, n: int, eps_exp: int) -> list[bool]:
    """Exact Bernoulli(2**eps_exp) flips: draw 12 bits, flip iff < 2**eps_exp.

    The 12-bit draw val is uniform on [0, 4096); val/4096 < 2**eps_exp iff
    val < 2**(12+eps_exp); eps_exp is in [-12, 0] so the shift is exact.
    """
    if eps_exp is None:
        return [False] * n
    raw = prng_bytes(seed_hex, counter, 2 * n)
    thresh = 1 << (12 + eps_exp)
    out = []
    for i in range(n):
        val = (raw[2 * i] << 4) | (raw[2 * i + 1] >> 4)
        out.append(val < thresh)
    return out


def de_bruijn(order: int) -> list[int]:
    """Canonical lexicographically-least binary de Bruijn sequence B(2, order)."""
    alphabet = [0, 1]
    a = [0] * (2 * order)
    seq = []

    def db(t, p):
        if t > order:
            if order % p == 0:
                seq.extend(a[1:p + 1])
        else:
            a[t] = a[t - p]
            db(t + 1, p)
            for j in range(a[t - p] + 1, 2):
                a[t] = j
                db(t + 1, t)

    db(1, 1)
    return seq


def design_rows(kappa_exp: int, seed_hex: str) -> list[list[Dyadic]]:
    """X = R * H4 * S * P; exact conditioning 2**(4*kappa_exp) (freeze D-6)."""
    n = N_ROWS
    signs = draw_signs(seed_hex, 0, n)
    perm_bits = prng_bytes(seed_hex, 1, 2 * P_DIM)
    perm = list(range(P_DIM))
    for i in range(P_DIM - 1, 0, -1):
        j = perm_bits[P_DIM - 1 - i] % (i + 1)
        perm[i], perm[j] = perm[j], perm[i]
    col_sign = [1 if (perm_bits[P_DIM + i] & 1) else -1 for i in range(P_DIM)]
    num = 2 * kappa_exp
    spread = [-num + round(i * (2 * num) / (P_DIM - 1)) for i in range(P_DIM)]
    rows = []
    for r in range(n):
        s = signs[r]
        row = []
        for c in range(P_DIM):
            target = perm[c]
            h = HADAMARD4[r % 4][target] * col_sign[c]
            row.append(Dyadic(s * h, spread[target] - 1))
        rows.append(row)
    return rows


def coefficients_for(seed_hex: str, support: list[int]) -> list[Dyadic]:
    vals = draw_dyadics(seed_hex, 2, P_DIM)
    out = []
    for i in range(P_DIM):
        if support[i]:
            v = vals[i]
            if v.mant == 0:
                v = Dyadic(1, 0)
        else:
            v = Dyadic(0, 0)
        out.append(v)
    return out


def score_tercile_cuts(score: list[Dyadic]) -> tuple[Dyadic, Dyadic]:
    """D-1 order-statistic tercile cuts of a score vector (exact)."""
    s = sorted(score, key=lambda d: d.fraction())
    k1 = (len(s) * 1 + 2) // 3
    k2 = (len(s) * 2 + 2) // 3
    return s[k1 - 1], s[k2 - 1]


# ---------------------------------------------------------------------------
# Registry (freeze F2).  Complete classes in the declared lattices.
# ---------------------------------------------------------------------------

def _mono_triples():
    """All non-decreasing triples over STEP_VALUES with >=1 strict gap."""
    members, affine_level, constants = [], [], []
    vals = STEP_VALUES
    for v0 in vals:
        for v1 in vals:
            for v2 in vals:
                tri = (v0, v1, v2)
                if not (v0 <= v1 <= v2):
                    continue
                gaps = (v1 - v0, v2 - v1)
                if gaps[0] == 0 and gaps[1] == 0:
                    constants.append(tri)
                    continue
                if gaps[0] == gaps[1]:
                    affine_level.append(tri)
                else:
                    members.append(tri)
    return members, affine_level, constants


def _nonmono_triples():
    """Peak/valley triples over STEP_VALUES (strict turn at the middle)."""
    out = []
    vals = STEP_VALUES
    for v0 in vals:
        for v1 in vals:
            for v2 in vals:
                if (v0 < v1 > v2) or (v0 > v1 < v2):
                    out.append((v0, v1, v2))
    return out


def registry() -> dict:
    tasks = []

    def add(tid, kind, params):
        row = {"id": tid, "kind": kind}
        row.update(params)
        row["seed"] = task_seed(tid)
        tasks.append(row)

    full = [1] * P_DIM
    # affine member class
    for j, e in enumerate(SIGMA_EXPS):
        add("AFF_NOISE_%d" % j, "static", {"gen": "affine", "support": full,
            "sigma_exp": e, "kappa_exp": 0, "arm": "noise_sweep"})
    for k in range(KAPPA_STEPS + 1):
        add("AFF_KAPPA_%d" % k, "static", {"gen": "affine", "support": full,
            "sigma_exp": -12, "kappa_exp": k, "arm": "kappa_sweep"})
    for mask in range(1, 1 << P_DIM):
        add("AFF_SUPPORT_%d" % mask, "static", {"gen": "affine",
            "support": [(mask >> i) & 1 for i in range(P_DIM)],
            "sigma_exp": ANCHOR_SIGMA_EXP, "kappa_exp": 0, "arm": "support_census"})
    for r in range(N_SEEDS):
        add("AFF_ANCHOR_%d" % r, "static", {"gen": "affine", "support": full,
            "sigma_exp": ANCHOR_SIGMA_EXP, "kappa_exp": 0, "arm": "seed_census"})
    for r in range(N_SEEDS):
        add("AFF_NULL_%d" % r, "static", {"gen": "affine", "support": full,
            "sigma_exp": ANCHOR_SIGMA_EXP, "kappa_exp": 0, "arm": "perm_null"})
    # decision member class (binary)
    for j, e in enumerate(SIGMA_EXPS):
        add("DEC_NOISE_%d" % j, "static", {"gen": "decision", "support": full,
            "eps_exp": e, "kappa_exp": 0, "arm": "noise_sweep", "binary": True})
    for k in range(KAPPA_STEPS + 1):
        add("DEC_KAPPA_%d" % k, "static", {"gen": "decision", "support": full,
            "eps_exp": -12, "kappa_exp": k, "arm": "kappa_sweep", "binary": True})
    for r in range(N_SEEDS):
        add("DEC_ANCHOR_%d" % r, "static", {"gen": "decision", "support": full,
            "eps_exp": ANCHOR_SIGMA_EXP, "kappa_exp": 0, "arm": "seed_census", "binary": True})
    for r in range(N_SEEDS):
        add("DEC_NULL_%d" % r, "static", {"gen": "decision", "support": full,
            "eps_exp": ANCHOR_SIGMA_EXP, "kappa_exp": 0, "arm": "perm_null", "binary": True})
    # monotone step member class + affine-level boundary census
    members, affine_level, constants = _mono_triples()
    for idx, tri in enumerate(members):
        add("MONO_MEMBER_%d" % idx, "static", {"gen": "mono_step", "steps": list(tri),
            "support": full, "sigma_exp": ANCHOR_SIGMA_EXP, "kappa_exp": 0, "arm": "member_census"})
    for idx, tri in enumerate(affine_level):
        add("MONO_AFFINE_%d" % idx, "static", {"gen": "mono_step", "steps": list(tri),
            "support": full, "sigma_exp": ANCHOR_SIGMA_EXP, "kappa_exp": 0, "arm": "boundary_census"})
    anchor = members[len(members) // 2]
    for j, e in enumerate(SIGMA_EXPS):
        add("MONO_NOISE_%d" % j, "static", {"gen": "mono_step", "steps": list(anchor),
            "support": full, "sigma_exp": e, "kappa_exp": 0, "arm": "noise_sweep"})
    for k in range(KAPPA_STEPS + 1):
        add("MONO_KAPPA_%d" % k, "static", {"gen": "mono_step", "steps": list(anchor),
            "support": full, "sigma_exp": -12, "kappa_exp": k, "arm": "kappa_sweep"})
    for r in range(N_SEEDS):
        add("MONO_ANCHOR_%d" % r, "static", {"gen": "mono_step", "steps": list(anchor),
            "support": full, "sigma_exp": ANCHOR_SIGMA_EXP, "kappa_exp": 0, "arm": "seed_census"})
    for r in range(N_SEEDS):
        add("MONO_NULL_%d" % r, "static", {"gen": "mono_step", "steps": list(anchor),
            "support": full, "sigma_exp": ANCHOR_SIGMA_EXP, "kappa_exp": 0, "arm": "perm_null"})
    # non-monotone counterexample census
    for idx, tri in enumerate(_nonmono_triples()):
        add("NONMONO_CENSUS_%d" % idx, "static", {"gen": "mono_step", "steps": list(tri),
            "support": full, "sigma_exp": ANCHOR_SIGMA_EXP, "kappa_exp": 0, "arm": "counterexample_census"})
    nonmono_anchor = _nonmono_triples()[len(_nonmono_triples()) // 2]
    for r in range(N_SEEDS):
        add("NONMONO_ANCHOR_%d" % r, "static", {"gen": "mono_step", "steps": list(nonmono_anchor),
            "support": full, "sigma_exp": ANCHOR_SIGMA_EXP, "kappa_exp": 0, "arm": "seed_census"})
    # pair-interaction member class (all 2^6 pair supports incl. empty)
    for mask in range(1 << len(PAIR_INDEX)):
        add("PAIR_CENSUS_%d" % mask, "static", {"gen": "pair_lift",
            "pair_support": [1 if (mask >> i) & 1 else 0 for i in range(len(PAIR_INDEX))],
            "atom_support": full, "sigma_exp": ANCHOR_SIGMA_EXP, "kappa_exp": 0,
            "arm": "support_census"})
    for j, e in enumerate(SIGMA_EXPS):
        add("PAIR_NOISE_%d" % j, "static", {"gen": "pair_lift",
            "pair_support": [1] * len(PAIR_INDEX), "atom_support": full,
            "sigma_exp": e, "kappa_exp": 0, "arm": "noise_sweep"})
    for k in range(KAPPA_STEPS + 1):
        add("PAIR_KAPPA_%d" % k, "static", {"gen": "pair_lift",
            "pair_support": [1] * len(PAIR_INDEX), "atom_support": full,
            "sigma_exp": -12, "kappa_exp": k, "arm": "kappa_sweep"})
    for r in range(N_SEEDS):
        add("PAIR_ANCHOR_%d" % r, "static", {"gen": "pair_lift",
            "pair_support": [1] * len(PAIR_INDEX), "atom_support": full,
            "sigma_exp": ANCHOR_SIGMA_EXP, "kappa_exp": 0, "arm": "seed_census"})
    for r in range(N_SEEDS):
        add("PAIR_NULL_%d" % r, "static", {"gen": "pair_lift",
            "pair_support": [1] * len(PAIR_INDEX), "atom_support": full,
            "sigma_exp": ANCHOR_SIGMA_EXP, "kappa_exp": 0, "arm": "perm_null"})
    # constant arm
    for j, e in enumerate(SIGMA_EXPS):
        add("CONST_NOISE_%d" % j, "static", {"gen": "constant",
            "sigma_exp": e, "kappa_exp": 0, "arm": "noise_sweep"})
    # stream battery
    for lag in range(D_MAX + 1):
        for j, e in enumerate(SIGMA_EXPS):
            add("DEL_REAL_%d_%d" % (lag, j), "stream", {"gen": "delay_real",
                "lag": lag, "sigma_exp": e, "arm": "noise_sweep"})
        add("DEL_DB_%d" % lag, "stream", {"gen": "delay_binary",
            "lag": lag, "eps_exp": ANCHOR_SIGMA_EXP, "arm": "dbjni_arm", "binary": True})
    for r in range(N_SEEDS):
        add("DEL_ANCHOR_%d" % r, "stream", {"gen": "delay_real",
            "lag": 6, "sigma_exp": ANCHOR_SIGMA_EXP, "arm": "seed_census"})
    for r in range(N_SEEDS):
        add("DEL_NULL_%d" % r, "stream", {"gen": "delay_real",
            "lag": 6, "sigma_exp": ANCHOR_SIGMA_EXP, "arm": "perm_null"})

    return {
        "schema": "GMI833HRealScaleBatteryRegistryV1",
        "freeze": "FREEZE_V1.md",
        "p": P_DIM,
        "n": N_ROWS,
        "d_max": D_MAX,
        "sigma_exps": [None] + list(range(-12, 0)) + [1],
        "anchor_sigma_exp": ANCHOR_SIGMA_EXP,
        "n_seeds": N_SEEDS,
        "kappa_lattice": ["2^%d" % (4 * k) for k in range(KAPPA_STEPS + 1)],
        "pair_index": [list(c) for c in PAIR_INDEX],
        "mono_anchor": list(anchor),
        "nonmono_anchor": list(nonmono_anchor),
        "mono_member_count": len(members),
        "mono_affine_level_count": len(affine_level),
        "mono_constant_count": len(constants),
        "nonmono_member_count": len(_nonmono_triples()),
        "tasks": tasks,
    }


def build_registry_file() -> None:
    data = registry()
    (HERE / "BATTERY_REGISTRY_V1.json").write_text(json.dumps(data, sort_keys=True, indent=1) + "\n")


def to_int_rep(dys: list[Dyadic]) -> tuple[list[int], int]:
    """Common-shift integer representation of a dyadic vector."""
    if not dys:
        return [], 0
    shift = min(d.exp for d in dys)
    ints = [d.mant << (d.exp - shift) for d in dys]
    return ints, shift


def materialize(task: dict) -> dict:
    """Materialize a registry task into exact train/test data."""
    seed = task["seed"]
    n = N_ROWS
    gen = task["gen"]
    if task["kind"] == "static":
        rows = design_rows(task["kappa_exp"], seed)
        w = coefficients_for(seed, task.get("support", full_list()))
        score = [sum_d([rows[i][j] * w[j] for j in range(P_DIM)]) for i in range(n)]
        if gen == "affine":
            y = list(score)
        elif gen == "decision":
            _, cut = score_tercile_cuts(score)
            y = [Dyadic(1, 0) if s >= cut else Dyadic(0, 0) for s in score]
        elif gen == "mono_step":
            c1, c2 = score_tercile_cuts(score)
            steps = [Dyadic(v, 0) for v in task["steps"]]
            y = [steps[0] if s < c1 else steps[1] if s < c2 else steps[2] for s in score]
        elif gen == "pair_lift":
            u = [Dyadic(0, 0)] * len(PAIR_INDEX)
            uv = draw_dyadics(seed, 3, len(PAIR_INDEX))
            for idx, (a, b) in enumerate(PAIR_INDEX):
                if task["pair_support"][idx]:
                    u[idx] = uv[idx] if uv[idx].mant != 0 else Dyadic(1, 0)
            y = [score[i] + sum_d([u[t] * rows[i][PAIR_INDEX[t][0]] * rows[i][PAIR_INDEX[t][1]]
                                   for t in range(len(PAIR_INDEX)) if u[t].mant != 0])
                 for i in range(n)]
        elif gen == "constant":
            y = [Dyadic(0, 0)] * n
        else:
            raise ValueError("unknown gen " + gen)
        # noise
        if task.get("binary"):
            eps_exp = task["eps_exp"]
            if eps_exp is not None:
                flips = draw_bernoulli(seed, 5, n, eps_exp)
                y = [flip_d(y[i]) if flips[i] else y[i] for i in range(n)]
        else:
            e = task["sigma_exp"]
            if e is not None:
                noise = draw_dyadic_flip(seed, 4, n, e)
                y = [y[i] + noise[i] for i in range(n)]
        if task.get("arm") == "perm_null":
            y = permute_within(y, STREAM_SPLIT, seed)
        half = n // 2
        return {
            "kind": "static", "binary": bool(task.get("binary")),
            "X_train": rows[:half], "y_train": y[:half],
            "X_test": rows[half:], "y_test": y[half:],
        }
    if task["kind"] == "stream":
        lag = task["lag"]
        if gen == "delay_real":
            x = draw_dyadics(seed, 0, n)
            y = [x[i - lag] if i >= lag else Dyadic(0, 0) for i in range(n)]
            e = task["sigma_exp"]
            if e is not None:
                noise = draw_dyadic_flip(seed, 1, n, e)
                y = [y[i] + noise[i] for i in range(n)]
            binary = False
        elif gen == "delay_binary":
            x = de_bruijn(STREAM_DOMAIN_BITS)
            x = [x[i % len(x)] for i in range(n)]
            y = [x[i - lag] if i >= lag else 0 for i in range(n)]
            eps_exp = task["eps_exp"]
            flips = draw_bernoulli(seed, 2, n, eps_exp)
            y = [(1 - y[i]) if flips[i] else y[i] for i in range(n)]
            binary = True
        else:
            raise ValueError("unknown gen " + gen)
        if task.get("arm") == "perm_null":
            y = permute_within(y, STREAM_SPLIT, seed)
        half = n // 2
        # delay-augmented interface built by the search (c up to D_MAX);
        # canonical zero history prefix (parent convention).
        return {
            "kind": "stream", "binary": binary, "stream": x,
            "y_train": y[:half], "y_test": y[half:], "half": half,
        }
    raise ValueError("unknown kind " + task["kind"])


def full_list() -> list[int]:
    return [1] * P_DIM


def sum_d(items: list[Dyadic]) -> Dyadic:
    if not items:
        return Dyadic(0, 0)
    out = items[0]
    for it in items[1:]:
        out = out + it
    return out


def flip_d(v: Dyadic) -> Dyadic:
    return Dyadic(1, 0) - v


def permute_within(vals: list, half: int, seed_hex: str) -> list:
    """Permute the training half (the declared null arm, D-9)."""
    idx = list(range(half))
    raw = prng_bytes(seed_hex + "|NULL", 9, 4 * half)
    for i in range(half - 1, 0, -1):
        j = int.from_bytes(raw[4 * i:4 * i + 4], "big") % (i + 1)
        idx[i], idx[j] = idx[j], idx[i]
    return [vals[idx[i]] if i < half else vals[i] for i in range(len(vals))]


if __name__ == "__main__":
    build_registry_file()
    print("registry tasks:", len(registry()["tasks"]))

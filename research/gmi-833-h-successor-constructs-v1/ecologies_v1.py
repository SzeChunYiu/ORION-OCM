"""The five registered ecologies and their five negative twins.

FREEZE_V1.md section 5 and FREEZE_V1_ADDENDUM.md A7. Exact rational values
only; every value comes from the one registered deterministic stream. No
sampler, simulator or model is used anywhere.
"""
from fractions import Fraction as Q
import hashlib

SEED = 20260918
MOD = 2 ** 31
MULT = 1103515245
INC = 12345

N_INDEX = 12
W_STAGE = 4
N_ROWS = 48
RESPONSE_SET = (Q(-6), Q(-4), Q(0), Q(4), Q(6))

SCOPES = ("SIGMA_D17", "SIGMA_D20", "SIGMA_D22", "SIGMA_D32", "SIGMA_D34")
SCOPE_ROW = {
    "SIGMA_D17": "Bayesian inference/belief-state systems.",
    "SIGMA_D20": "Feed-forward neural networks.",
    "SIGMA_D22": "CNN/equivariant local-weight-sharing systems.",
    "SIGMA_D32": "Flow-like transport systems.",
    "SIGMA_D34": "Energy-based systems.",
}
SCOPE_ID = {"SIGMA_D17": "H17", "SIGMA_D20": "H20", "SIGMA_D22": "H22",
            "SIGMA_D32": "H32", "SIGMA_D34": "H34"}

PIN_SEARCH_A = (1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0)
PIN_SEARCH_P = (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
PIN_HELD_A = (1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
PIN_HELD_P = (-1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)


class Stream(object):
    def __init__(self, seed=SEED):
        self.s = seed
        self.draws = 0

    def next(self):
        self.s = (MULT * self.s + INC) % MOD
        self.draws += 1
        return self.s


def _draw_row(st, scope):
    if scope == "SIGMA_D34":
        A = tuple(Q((st.next() % 3) - 1) for _ in range(N_INDEX))
        P = tuple(Q((st.next() % 3) - 1) for _ in range(N_INDEX))
    else:
        A = tuple(Q(st.next() % 11) for _ in range(N_INDEX))
        P = []
        for _ in range(N_INDEX):
            v = (st.next() % 21) - 10
            P.append(Q(v if v != 0 else 1))
        P = tuple(P)
    M = tuple(tuple(Q((st.next() % 7) - 3) for _ in range(W_STAGE))
              for _ in range(N_INDEX))
    Qc = tuple(Q((st.next() % 7) - 3) for _ in range(W_STAGE))
    return {"A": A, "P": P, "M": M, "Q": Qc}


def build_channels(scope):
    """48 rows of the four channels. Returns (rows, rebuilds)."""
    st = Stream()
    rows = []
    rebuilds = 0
    for idx in range(N_ROWS):
        row = _draw_row(st, scope)
        if scope == "SIGMA_D17":
            while sum(row["A"]) == 0:
                rebuilds += 1
                row = _draw_row(st, scope)
        if scope == "SIGMA_D34" and idx == 0:
            row = dict(row)
            row["A"] = tuple(Q(v) for v in PIN_SEARCH_A)
            row["P"] = tuple(Q(v) for v in PIN_SEARCH_P)
        if scope == "SIGMA_D34" and idx == 2:
            row = dict(row)
            row["A"] = tuple(Q(v) for v in PIN_HELD_A)
            row["P"] = tuple(Q(v) for v in PIN_HELD_P)
        rows.append(row)
    return rows, rebuilds


def _stage1(row, j):
    tot = Q(0)
    for i in range(N_INDEX):
        tot += row["A"][i] * row["M"][i][j]
    return tot


def _step(v):
    return Q(1) if v > 0 else Q(0)


def response_target(scope, row):
    if scope == "SIGMA_D17":
        num = Q(0)
        den = Q(0)
        for i in range(N_INDEX):
            num += row["A"][i] * row["P"][i]
            den += row["A"][i]
        return num / den
    if scope == "SIGMA_D20":
        tot = Q(0)
        for j in range(W_STAGE):
            tot += _step(_stage1(row, j)) * row["Q"][j]
        return tot
    if scope == "SIGMA_D22":
        tot = Q(0)
        for i in range(N_INDEX):
            tot += row["A"][i] * row["P"][i % 3]
        return tot
    if scope == "SIGMA_D32":
        prod = Q(1)
        ssum = Q(0)
        for i in range(N_INDEX):
            prod *= row["P"][i]
            ssum += row["A"][i]
        return prod * ssum
    if scope == "SIGMA_D34":
        score = Q(0)
        for i in range(N_INDEX):
            score += row["A"][i] * row["P"][i]
        best = None
        best_e = None
        for y in RESPONSE_SET:
            e = abs(score + y)
            if best_e is None or e < best_e:
                best_e = e
                best = y
        return best
    raise ValueError("no scope " + str(scope))


def response_twin(scope, row):
    if scope == "SIGMA_D17":
        tot = Q(0)
        for i in range(N_INDEX):
            tot += row["A"][i] * row["P"][i]
        return tot
    if scope == "SIGMA_D20":
        tot = Q(0)
        for j in range(W_STAGE):
            tot += _stage1(row, j) * row["Q"][j]
        return tot
    if scope == "SIGMA_D22":
        tot = Q(0)
        for i in range(N_INDEX):
            tot += row["A"][i] * row["P"][i]
        return tot
    if scope == "SIGMA_D32":
        psum = Q(0)
        ssum = Q(0)
        for i in range(N_INDEX):
            psum += row["P"][i]
            ssum += row["A"][i]
        return psum * ssum
    if scope == "SIGMA_D34":
        score = Q(0)
        for i in range(N_INDEX):
            score += row["A"][i] * row["P"][i]
        return -score
    raise ValueError("no scope " + str(scope))


def slices():
    """FREEZE_V1.md section 5.3."""
    search = tuple(i for i in range(N_ROWS) if i % 4 in (0, 1))
    held = tuple(i for i in range(N_ROWS) if i % 4 == 2)
    regen = tuple(i for i in range(N_ROWS) if i % 4 == 3)
    return search, held, regen


def build(scope, twin=False):
    rows, rebuilds = build_channels(scope)
    fn = response_twin if twin else response_target
    ys = tuple(fn(scope, r) for r in rows)
    search, held, regen = slices()
    return {"scope": scope, "rows": rows, "y": ys, "rebuilds": rebuilds,
            "search": search, "held": held, "regen": regen, "twin": twin}


def digest(eco):
    h = hashlib.sha256()
    h.update(eco["scope"].encode())
    h.update(b"twin" if eco["twin"] else b"target")
    for idx, row in enumerate(eco["rows"]):
        h.update(("#%d" % idx).encode())
        for key in ("A", "P", "Q"):
            h.update((",".join(str(v) for v in row[key])).encode())
        for line in row["M"]:
            h.update((",".join(str(v) for v in line)).encode())
        h.update(str(eco["y"][idx]).encode())
    return h.hexdigest()


def tie_rows(eco):
    """Rows at which the ARGMIN of the registered energy has a tie."""
    out = []
    for idx, row in enumerate(eco["rows"]):
        score = Q(0)
        for i in range(N_INDEX):
            score += row["A"][i] * row["P"][i]
        best_e = None
        hits = 0
        for y in RESPONSE_SET:
            e = abs(score + y)
            if best_e is None or e < best_e:
                best_e = e
                hits = 1
            elif e == best_e:
                hits += 1
        if hits > 1:
            out.append(idx)
    return tuple(out)

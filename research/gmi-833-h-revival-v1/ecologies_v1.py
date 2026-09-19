"""The five derivational ecologies of gmi-833-h-revival-v1, their one-property
matched negative controls, and the candidate stream for the constructed
held-out slice.

FREEZE_V1.md sections 7 and 8.2. Exact rational values only; every value
comes from the two registered deterministic streams. No sampler, simulator or
model is used anywhere. The functionals are the parent's, verbatim; the seed is
new, so no parent row is a row here.
"""
from fractions import Fraction as Q
import hashlib

SEED = 20260919          # channel stream, section 7
CANDIDATE_SEED = 20260921  # held-out candidate stream, section 8.2
MOD = 2 ** 31
MULT = 1103515245
INC = 12345

N_INDEX = 12
W_STAGE = 4
N_ROWS = 48
N_CANDIDATES = 480
HELD_TARGET = 12
RESPONSE_SET = (Q(-6), Q(-4), Q(0), Q(4), Q(6))

SCOPES = ("SIGMA_E17", "SIGMA_E20", "SIGMA_E22", "SIGMA_E32", "SIGMA_E34")
SCOPE_ROW = {
    "SIGMA_E17": "Bayesian inference/belief-state systems.",
    "SIGMA_E20": "Feed-forward neural networks.",
    "SIGMA_E22": "CNN/equivariant local-weight-sharing systems.",
    "SIGMA_E32": "Flow-like transport systems.",
    "SIGMA_E34": "Energy-based systems.",
}
SCOPE_ID = {"SIGMA_E17": "H17", "SIGMA_E20": "H20", "SIGMA_E22": "H22",
            "SIGMA_E32": "H32", "SIGMA_E34": "H34"}

PIN_SEARCH_A = (1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0)
PIN_SEARCH_P = (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
PIN_HELD_A = (1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
PIN_HELD_P = (-1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)


class Stream(object):
    def __init__(self, seed):
        self.s = seed
        self.draws = 0

    def next(self):
        self.s = (MULT * self.s + INC) % MOD
        self.draws += 1
        return self.s


def _draw_row(st, scope):
    if scope == "SIGMA_E34":
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
    """48 rows of the four channels from the channel stream. (rows, rebuilds)"""
    st = Stream(SEED)
    rows = []
    rebuilds = 0
    for idx in range(N_ROWS):
        row = _draw_row(st, scope)
        if scope == "SIGMA_E17":
            while sum(row["A"]) == 0:
                rebuilds += 1
                row = _draw_row(st, scope)
        if scope == "SIGMA_E34" and idx == 0:
            row = dict(row)
            row["A"] = tuple(Q(v) for v in PIN_SEARCH_A)
            row["P"] = tuple(Q(v) for v in PIN_SEARCH_P)
        rows.append(row)
    return rows, rebuilds


def build_candidates(scope):
    """480 candidate rows from the candidate stream. Candidate 0 at SIGMA_E34
    is the pinned held-out tie row. (rows, rebuilds)"""
    st = Stream(CANDIDATE_SEED)
    rows = []
    rebuilds = 0
    for idx in range(N_CANDIDATES):
        row = _draw_row(st, scope)
        if scope == "SIGMA_E17":
            while sum(row["A"]) == 0:
                rebuilds += 1
                row = _draw_row(st, scope)
        if scope == "SIGMA_E34" and idx == 0:
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
    if scope == "SIGMA_E17":
        num = Q(0)
        den = Q(0)
        for i in range(N_INDEX):
            num += row["A"][i] * row["P"][i]
            den += row["A"][i]
        return num / den
    if scope == "SIGMA_E20":
        tot = Q(0)
        for j in range(W_STAGE):
            tot += _step(_stage1(row, j)) * row["Q"][j]
        return tot
    if scope == "SIGMA_E22":
        tot = Q(0)
        for i in range(N_INDEX):
            tot += row["A"][i] * row["P"][i % 3]
        return tot
    if scope == "SIGMA_E32":
        prod = Q(1)
        ssum = Q(0)
        for i in range(N_INDEX):
            prod *= row["P"][i]
            ssum += row["A"][i]
        return prod * ssum
    if scope == "SIGMA_E34":
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


def response_control(scope, row):
    if scope == "SIGMA_E17":
        tot = Q(0)
        for i in range(N_INDEX):
            tot += row["A"][i] * row["P"][i]
        return tot
    if scope == "SIGMA_E20":
        tot = Q(0)
        for j in range(W_STAGE):
            tot += _stage1(row, j) * row["Q"][j]
        return tot
    if scope == "SIGMA_E22":
        tot = Q(0)
        for i in range(N_INDEX):
            tot += row["A"][i] * row["P"][i]
        return tot
    if scope == "SIGMA_E32":
        psum = Q(0)
        ssum = Q(0)
        for i in range(N_INDEX):
            psum += row["P"][i]
            ssum += row["A"][i]
        return psum * ssum
    if scope == "SIGMA_E34":
        score = Q(0)
        for i in range(N_INDEX):
            score += row["A"][i] * row["P"][i]
        return -score
    raise ValueError("no scope " + str(scope))


def slices():
    """FREEZE_V1.md section 7: search and regeneration only; the held-out
    slice is constructed from the candidate stream, never sliced here."""
    search = tuple(i for i in range(N_ROWS) if i % 4 in (0, 1))
    regen = tuple(i for i in range(N_ROWS) if i % 4 == 3)
    return search, regen


def build(scope, control=False):
    rows, rebuilds = build_channels(scope)
    fn = response_control if control else response_target
    ys = tuple(fn(scope, r) for r in rows)
    search, regen = slices()
    return {"scope": scope, "rows": rows, "y": ys, "rebuilds": rebuilds,
            "search": search, "regen": regen, "control": control}


def candidates(scope, control=False):
    """The candidate rows WITHOUT responses. Responses are computed only after
    the held-out slice is chosen (section 8.2), by `candidate_responses`."""
    rows, rebuilds = build_candidates(scope)
    return {"scope": scope, "rows": rows, "rebuilds": rebuilds,
            "control": control}


def candidate_responses(scope, cand, chosen, control=False):
    fn = response_control if control else response_target
    return tuple(fn(scope, cand["rows"][k]) for k in chosen)


def digest(eco):
    h = hashlib.sha256()
    h.update(eco["scope"].encode())
    h.update(b"control" if eco["control"] else b"target")
    for idx, row in enumerate(eco["rows"]):
        h.update(("#%d" % idx).encode())
        for key in ("A", "P", "Q"):
            h.update((",".join(str(v) for v in row[key])).encode())
        for line in row["M"]:
            h.update((",".join(str(v) for v in line)).encode())
        h.update(str(eco["y"][idx]).encode())
    return h.hexdigest()


def candidate_digest(cand):
    h = hashlib.sha256()
    h.update(cand["scope"].encode())
    h.update(b"candidates")
    for idx, row in enumerate(cand["rows"]):
        h.update(("#%d" % idx).encode())
        for key in ("A", "P", "Q"):
            h.update((",".join(str(v) for v in row[key])).encode())
        for line in row["M"]:
            h.update((",".join(str(v) for v in line)).encode())
    return h.hexdigest()


def tie_rows(rows):
    """Row indices at which the ARGMIN of the registered energy has a tie."""
    out = []
    for idx, row in enumerate(rows):
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

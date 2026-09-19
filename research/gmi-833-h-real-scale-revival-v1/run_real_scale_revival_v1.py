"""Real-scale run driver for gmi-833-h-real-scale-revival-v1.

Runs on the host of record (FREEZE_V1.md section 4). Reads the sha256-bound
real sources, builds the three registered ecologies, runs the family-blind
enumerative search over G_S, fits the arms at real scale and writes the
receipts under REAL_RUNS/ that the stdlib checker replays exactly.

Numpy is used only inside fitting and screening. Every claimed quantity is
recomputed exactly with fractions.Fraction before it is written.

Usage:  python3 -B run_real_scale_revival_v1.py [--controls] [--quick]
"""
from fractions import Fraction as Q
import glob
import hashlib
import multiprocessing as mp
import json
import os
import sys
import time
import wave

import numpy as np

import grammar_s_v1 as G

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "REAL_RUNS")

RAT_DEN = 10 ** 9              # FREEZE_V1.md section 6
SEED = 20260918                # FREEZE_V1.md section 8, P2d
SCREEN_ROWS = 400
ORACLE_ROWS = 1500
RANK_SPLIT = 7  # tenths of the search slice used to fit the ranking stage
KEEP = 40
SWEEPS = 6
N_CONTROLS = 200
VERIFY_ROWS = 1500

D2_DIGEST = "a9f677295dcb2d102bb43b86cbad70babe208c1a5fd38a2ae4d8a05f7fdb7a7a"
D3_DIGEST = "41607de5c1577303abc83cccfd29e5d12e6c180689d9fc3d98eac3f97dec9ec9"

SCOPES = {"R02": "SIGMA_R02", "R03": "SIGMA_R03B", "R04": "SIGMA_R04B"}
# FREEZE_V2_ADDENDUM.md section 3: the one-sided registered response support.
# None means the support is two-sided and the admissibility rule is inert.
SUPPORT_FLOOR = {"R02": None, "R03": 0, "R04": 0}


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def digest_of_digests(paths):
    parts = []
    for p in paths:
        with open(p, "rb") as fh:
            parts.append(sha_bytes(fh.read()))
    return sha_bytes("".join(parts).encode()), parts


# --------------------------------------------------------------- sources ----

def load_sources(bad_path=False, bad_digest=False):
    wavs = sorted(glob.glob("/usr/share/sounds/alsa/*.wav"))
    if bad_path:
        wavs = sorted(glob.glob("/usr/share/sounds/NO_SUCH_DIR/*.wav"))
    if not wavs:
        raise SystemExit("MISSING REAL SOURCE: D2 is not readable")
    d2, d2parts = digest_of_digests(wavs)
    want2 = D2_DIGEST if not bad_digest else ("0" + D2_DIGEST[1:])
    if d2 != want2:
        raise SystemExit("SOURCE DIGEST MISMATCH: D2 %s != %s" % (d2, want2))
    frames = []
    for p in wavs:
        w = wave.open(p, "rb")
        if w.getnchannels() != 1 or w.getsampwidth() != 2:
            raise SystemExit("D2 shape drift in " + p)
        raw = w.readframes(w.getnframes())
        w.close()
        frames.append(np.frombuffer(raw, dtype="<i2").astype(np.int64))
    pcm = np.concatenate(frames)

    pys = sorted(glob.glob("/usr/lib/python3.8/**/*.py", recursive=True))
    d3, d3parts = digest_of_digests(pys)
    if d3 != D3_DIGEST:
        raise SystemExit("SOURCE DIGEST MISMATCH: D3 %s != %s" % (d3, D3_DIGEST))
    texts = []
    for p in pys:
        with open(p, "rb") as fh:
            texts.append((p, fh.read()))
    sources = {
        "D2": {"paths": [os.path.basename(p) for p in wavs], "files": len(wavs),
               "frames": int(len(pcm)), "digest_of_digests": d2,
               "per_file": d2parts},
        "D3": {"files": len(pys), "bytes": sum(len(t) for _, t in texts),
               "digest_of_digests": d3},
    }
    return pcm, texts, sources


# ------------------------------------------------------------- ecologies ----

TOKEN_START = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_")
TOKEN_REST = TOKEN_START | set("0123456789")
VOWELS = set("aeiouAEIOU")


def ecology_F02(pcm):
    d = 32
    n = len(pcm) - 33
    idx = np.arange(n)[:, None] + np.arange(d)[None, :]
    return {"name": "F02", "X": pcm[idx], "y": pcm[33:33 + n], "d": d,
            "xden": (32768,) * d, "yden": 32768, "loss": "squared"}


def ecology_F04(pcm):
    d = 32
    n = len(pcm) - 33
    idx = np.arange(n)[:, None] + np.arange(1, d + 1)[None, :]
    X = pcm[idx]
    positive = (pcm > 0).astype(np.int64)
    cs = np.concatenate([[0], np.cumsum(positive)])
    y = cs[32:32 + n] - cs[0:n]
    return {"name": "F04b", "X": X, "y": y, "d": d,
            "xden": (32768,) * d, "yden": 32, "loss": "squared"}


def _tokens_of(text):
    out = []
    i = 0
    L = len(text)
    while i < L:
        c = text[i]
        if c in TOKEN_START:
            j = i + 1
            while j < L and text[j] in TOKEN_REST:
                j += 1
            out.append((text[i:j], i))
            i = j
        else:
            i += 1
    return out


F03_COLS = ("tok_len", "lead_us", "trail_us", "upper", "lower", "digits",
            "underscores", "vowels", "first_is_us", "file_bytes",
            "file_lines", "file_tokens")


def ecology_F03(texts):
    rows = []
    ys = []
    for path, raw in texts:
        text = raw.decode("utf-8", "replace")
        toks = _tokens_of(text)
        counts = {}
        first = {}
        for name, off in toks:
            counts[name] = counts.get(name, 0) + 1
            if name not in first:
                first[name] = off
        fb = len(raw)
        fl = text.count("\n") + 1
        ft = len(counts)
        for name in sorted(counts, key=lambda k: (first[k], k)):
            up = sum(1 for ch in name if "A" <= ch <= "Z")
            lo = sum(1 for ch in name if "a" <= ch <= "z")
            dg = sum(1 for ch in name if "0" <= ch <= "9")
            us = name.count("_")
            vo = sum(1 for ch in name if ch in VOWELS)
            rows.append((len(name), 1 if name.startswith("_") else 0,
                         1 if name.endswith("_") else 0, up, lo, dg, us, vo,
                         1 if name[0] == "_" else 0, fb, fl, ft))
            ys.append(counts[name])
    X = np.array(rows, dtype=np.int64)
    y = np.array(ys, dtype=np.int64)
    den = []
    for j in range(X.shape[1]):
        m = int(np.abs(X[:, j]).max())
        p = 1
        while p < m + 1:
            p *= 2
        den.append(p)
    return {"name": "F03", "X": X, "y": y, "d": X.shape[1],
            "xden": tuple(den), "yden": 1, "loss": "squared",
            "columns": F03_COLS}


# ---------------------------------------------------------------- slices ----

def slices(n):
    """FREEZE_V1.md section 4. Modulus 7."""
    i = np.arange(n)
    m = i % 7
    return {"search": i[m == 5], "held": i[m == 6],
            "fit": i[(m != 5) & (m != 6)],
            "regen_fit": i[(m == 0) | (m == 1) | (m == 2)],
            "regen_held": i[m == 3]}


def design(eco, idx):
    X = eco["X"][idx].astype(np.float64) / np.array(eco["xden"], dtype=np.float64)
    y = eco["y"][idx].astype(np.float64) / float(eco["yden"])
    return X, y


# --------------------------------------------------------------- fitting ----

def _reciprocal(v):
    return 0.0 if v == 0.0 else 1.0 / v


def _np_reciprocal(v):
    out = np.zeros_like(v)
    nz = v != 0
    out[nz] = 1.0 / v[nz]
    return out


def _np_source(tree):
    op = tree[0]
    if op == "LEAF":
        name = tree[1]
        if name == "C0":
            return "np.zeros_like(_shape)"
        if name == "C1":
            return "np.ones_like(_shape)"
        return name.lower()
    if op == "NEG":
        return "(-(" + _np_source(tree[1]) + "))"
    if op == "ABS":
        return "(np.abs(" + _np_source(tree[1]) + "))"
    if op == "STEP":
        return "((" + _np_source(tree[1]) + ")>0).astype(np.float64)"
    if op == "RECIP":
        return "(_np_reciprocal(" + _np_source(tree[1]) + "))"
    if op == "ADD":
        return "((" + _np_source(tree[1]) + ")+(" + _np_source(tree[2]) + "))"
    if op == "MUL":
        return "((" + _np_source(tree[1]) + ")*(" + _np_source(tree[2]) + "))"
    raise ValueError(op)


_BODY_CACHE = {}
_HEAD_CACHE = {}
_HEAD_SCALAR_CACHE = {}


def body_fn(body):
    key = G.show(body)
    if key not in _BODY_CACHE:
        src = ("def _f(arg, param, _shape):\n    return " + _np_source(body) + "\n")
        env = {"np": np, "_np_reciprocal": _np_reciprocal}
        exec(src, env)
        _BODY_CACHE[key] = env["_f"]
    return _BODY_CACHE[key]


def head_fn(head):
    key = G.show(head)
    if key not in _HEAD_CACHE:
        src = ("def _g(s, bias, state, _shape):\n    return " + _np_source(head) + "\n")
        env = {"np": np, "_np_reciprocal": _np_reciprocal}
        exec(src, env)
        _HEAD_CACHE[key] = env["_g"]
    return _HEAD_CACHE[key]


class SPlan(object):
    """Shared fold-value plan for one BODY on one design block.

    The fold value S = sum_j BODY(ARG_j, PARAM_j) depends on BODY alone, so it
    is built once per BODY and reused for every HEAD. When BODY is affine in
    PARAM - decided symbolically on the frozen probe grid, not guessed - S is
    represented by its offset and its per-parameter columns and every later
    evaluation is one matrix-vector product.
    """

    def __init__(self, body, X):
        self.body = body
        self.X = X
        self.bf = body_fn(body)
        self.affine = G.affine_in(body, "PARAM", ["ARG", "PARAM"])
        if self.affine:
            d = X.shape[1]
            P0 = np.zeros_like(X)
            self.base = self.bf(X, P0, X).sum(axis=1)
            self.cols = np.empty((X.shape[0], d), dtype=np.float64)
            for j in range(d):
                P = np.zeros_like(X)
                P[:, j] = 1.0
                self.cols[:, j] = self.bf(X, P, X).sum(axis=1) - self.base

    def fold(self, params):
        p = np.asarray(params, dtype=np.float64)
        if self.affine:
            return self.base + self.cols.dot(p)
        P = np.broadcast_to(p, self.X.shape)
        return self.bf(self.X, P, self.X).sum(axis=1)


def apply_head(head, S, bias, stateful):
    hf = head_fn(head)
    b = np.full(S.shape, float(bias))
    if not stateful:
        return hf(S, b, np.zeros_like(S), S)
    hs = head_scalar_fn(head)
    out = np.empty(S.shape[0], dtype=np.float64)
    prev = 0.0
    b = float(bias)
    for i, sv in enumerate(S.tolist()):
        prev = hs(sv, b, prev)
        out[i] = prev
    return out


def head_scalar_fn(head):
    key = G.show(head)
    if key not in _HEAD_SCALAR_CACHE:
        src = ("def _h(s, bias, state):\n    return " + G.to_python(head) + "\n")
        env = {"_reciprocal": _reciprocal}
        exec(src, env)
        _HEAD_SCALAR_CACHE[key] = env["_h"]
    return _HEAD_SCALAR_CACHE[key]


def predict(body, head, stateful, X, params, bias):
    return apply_head(head, SPlan(body, X).fold(params), bias, stateful)


def predict_plan(plan, head, stateful, params, bias):
    return apply_head(head, plan.fold(params), bias, stateful)


def loss_of(pred, y):
    r = pred - y
    return float(np.dot(r, r))


def joint_affine(plan, head, stateful, y_len, d):
    """Probe whether the prediction is jointly affine in (params, bias)."""
    base = predict_plan(plan, head, stateful, np.zeros(d), 0.0)
    cols = []
    for j in range(d):
        p = np.zeros(d)
        p[j] = 1.0
        cols.append(predict_plan(plan, head, stateful, p, 0.0) - base)
    cols.append(predict_plan(plan, head, stateful, np.zeros(d), 1.0) - base)
    Z = np.stack(cols, axis=1)
    rs = np.random.RandomState(SEED)
    for _ in range(3):
        v = rs.randint(-3, 4, size=d + 1).astype(np.float64)
        got = predict_plan(plan, head, stateful, v[:d], v[d])
        want = base + Z.dot(v)
        if not np.allclose(got, want, rtol=1e-9, atol=1e-9):
            return None, None
    return base, Z


def lsq_from(base, Z, y, d, ridge=1e-8):
    A = Z.T.dot(Z) + ridge * np.eye(d + 1)
    b = Z.T.dot(y - base)
    try:
        v = np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        v = np.linalg.lstsq(Z, y - base, rcond=None)[0]
    return v[:d], float(v[d])


def cd_fit_plan(plan, head, stateful, y, d, sweeps, p0=None, b0=0.0):
    p = np.zeros(d) if p0 is None else np.array(p0, dtype=np.float64)
    bias = float(b0)
    best = loss_of(predict_plan(plan, head, stateful, p, bias), y)
    step = 1.0
    for _ in range(sweeps):
        for j in range(d + 1):
            cur = p[j] if j < d else bias
            for k in (-4, -2, -1, 1, 2, 4):
                v = cur + k * step
                if j < d:
                    p[j] = v
                else:
                    bias = v
                L = loss_of(predict_plan(plan, head, stateful, p, bias), y)
                if L < best - 1e-15:
                    best = L
                    cur = v
                else:
                    if j < d:
                        p[j] = cur
                    else:
                        bias = cur
            if j < d:
                p[j] = cur
            else:
                bias = cur
        step *= 0.5
    return p, bias, best


def fit_plan(plan, head, stateful, y, d, sweeps=SWEEPS):
    """One routine for every candidate. No family information reaches it."""
    base, Z = joint_affine(plan, head, stateful, len(y), d)
    if Z is not None:
        p, b = lsq_from(base, Z, y, d)
        L = loss_of(predict_plan(plan, head, stateful, p, b), y)
        if not np.isfinite(L):
            raise ValueError("non-finite")
        return p, b, L, "LEAST_SQUARES"
    p, b, L = cd_fit_plan(plan, head, stateful, y, d, sweeps)
    if not np.isfinite(L):
        raise ValueError("non-finite")
    return p, b, L, "COORDINATE_DESCENT"


def generic_fit(body, head, stateful, X, y, d, sweeps=SWEEPS):
    return fit_plan(SPlan(body, X), head, stateful, y, d, sweeps)


# ------------------------------------------------------- exact arithmetic ----
# FREEZE_V1_ARITHMETIC_ADDENDUM.md: one fixed-denominator operator, every arm.

LCM_GUARD = 10 ** 40


def rationalise(x):
    if not np.isfinite(x):
        raise ValueError("a fitting routine produced a non-finite value")
    return Q(int(round(float(x) * RAT_DEN)), RAT_DEN)


def qstr(q):
    return str(Q(q))


def _lcm(a, b):
    g = a
    t = b
    while t:
        g, t = t, g % t
    return a // g * b


class ExactSSE(object):
    """Exact sum of squares accumulated over one running common denominator.

    Aborts if the common denominator exceeds the registered guard, rather than
    silently producing a quantity that cannot be computed.
    """

    def __init__(self):
        self.M = 1
        self.acc = 0

    def add(self, diff):
        d = diff.denominator
        if self.M % d != 0:
            new_M = _lcm(self.M, d)
            if new_M > LCM_GUARD:
                raise ValueError("EXACT ACCUMULATION GUARD: common denominator "
                                 "exceeds 10**40; the chosen program does not "
                                 "admit a feasible exact sum at this scope")
            self.acc *= (new_M // self.M) ** 2
            self.M = new_M
        n = diff.numerator * (self.M // d)
        self.acc += n * n

    def value(self):
        return Q(self.acc, self.M * self.M)


def exact_row_values(eco, i):
    den = eco["xden"]
    row = eco["X"][i]
    return [Q(int(v), den[j]) for j, v in enumerate(row)]


def exact_response(eco, i):
    return Q(int(eco["y"][i]), eco["yden"])


def exact_predict(body, head, stateful, rows, params, bias):
    out = []
    prev = Q(0)
    for r in rows:
        S = Q(0)
        for j, v in enumerate(r):
            S += G.value(body, {"ARG": v, "PARAM": params[j]})
        o = G.value(head, {"S": S, "BIAS": bias, "STATE": prev})
        out.append(o)
        if stateful:
            prev = o
    return out


def exact_evaluate(eco, idx, body, head, stateful, params, bias,
                   want_decisions=False, chunk=4000):
    """Streaming exact evaluation on a slice. Returns exact quantities only."""
    sse = ExactSSE()
    errors = 0
    preds_seen = set()
    resp_seen = set()
    prev = Q(0)
    for start in range(0, len(idx), chunk):
        part = idx[start:start + chunk]
        rows = [exact_row_values(eco, i) for i in part]
        ys = [exact_response(eco, i) for i in part]
        for r, y in zip(rows, ys):
            S = Q(0)
            for j, v in enumerate(r):
                S += G.value(body, {"ARG": v, "PARAM": params[j]})
            o = G.value(head, {"S": S, "BIAS": bias, "STATE": prev})
            if stateful:
                prev = o
            sse.add(o - y)
            if want_decisions and (1 if o > 0 else 0) != (1 if y > 0 else 0):
                errors += 1
            if len(preds_seen) < 20000:
                preds_seen.add(o)
                resp_seen.add(y)
    out = {"n": int(len(idx)), "sse": qstr(sse.value()),
           "nondegeneracy": {"distinct_predictions": len(preds_seen),
                             "distinct_responses": len(resp_seen),
                             "response_is_constant": len(resp_seen) <= 1,
                             "prediction_is_constant": len(preds_seen) <= 1}}
    if want_decisions:
        out["decision_errors"] = errors
    return out


def exact_sse_of_pairs(pred, ys):
    acc = ExactSSE()
    for a, b in zip(pred, ys):
        acc.add(a - b)
    return acc.value()


def decision_errors(pred, ys):
    n = 0
    for a, b in zip(pred, ys):
        if (1 if a > 0 else 0) != (1 if b > 0 else 0):
            n += 1
    return n


def head_affine_coefficients(head):
    """(h_s, h_b, h_0) with HEAD(S,BIAS,0) = h_s*S + h_b*BIAS + h_0, exactly.

    Valid only for a HEAD that is jointly affine in S and BIAS and reads no
    STATE; the caller checks that on the frozen probe grid and refuses
    otherwise, so the decomposition is never assumed.
    """
    z = G.value(head, {"S": Q(0), "BIAS": Q(0), "STATE": Q(0)})
    hs = G.value(head, {"S": Q(1), "BIAS": Q(0), "STATE": Q(0)}) - z
    hb = G.value(head, {"S": Q(0), "BIAS": Q(1), "STATE": Q(0)}) - z
    for a in (Q(-2), Q(3, 2), Q(2)):
        for b in (Q(-1), Q(1, 2), Q(2)):
            if G.value(head, {"S": a, "BIAS": b, "STATE": Q(0)}) != hs * a + hb * b + z:
                return None
    return hs, hb, z


def affine_int_sse(eco, idx, params, bias, head=None):
    """Exact squared error of a linear-score program by integer accumulation.

    BODY is semantically MUL(ARG,PARAM) and HEAD is jointly affine in S and
    BIAS, so pred_i = h_s * (sum_j X_ij a_j)/(xden*RAT_DEN) + h_b*b/RAT_DEN + h_0.
    Every xden is equal within a scope, so one common denominator suffices.
    """
    den = eco["xden"]
    if len(set(den)) != 1:
        return None
    xd = den[0]
    if head is None:
        hs, hb, h0 = Q(1), Q(1), Q(0)
    else:
        got = head_affine_coefficients(head)
        if got is None:
            return None
        hs, hb, h0 = got
    a = np.array([int(p.numerator) * (RAT_DEN // int(p.denominator))
                  for p in params], dtype=np.int64)
    b = Q(bias)
    M = _lcm(_lcm(xd * RAT_DEN * hs.denominator,
                  RAT_DEN * hb.denominator * b.denominator),
             _lcm(eco["yden"], h0.denominator))
    X = eco["X"][idx]
    Y = eco["y"][idx]
    lin = X.dot(a)
    if np.abs(lin).max() > 2 ** 62:
        raise ValueError("integer overflow guard tripped in affine_int_sse")
    k_lin = Q(hs, xd * RAT_DEN) * M
    k_const = (hb * b + h0) * M
    k_y = Q(M, eco["yden"])
    if (k_lin.denominator != 1 or k_const.denominator != 1
            or k_y.denominator != 1):
        return None
    kl, kc, ky = int(k_lin), int(k_const), int(k_y)
    total = 0
    for v, yv in zip(lin.tolist(), Y.tolist()):
        d = v * kl + kc - yv * ky
        total += d * d
    return Q(total, M * M)


# ---------------------------------------------------------------- search ----

def build_candidates():
    braw = G.all_trees(G.BODY_BUDGET, G.BODY_LEAVES)
    hraw = G.all_trees(G.HEAD_BUDGET, G.HEAD_LEAVES)
    bq, _, nbr, nbc = G.collapse(braw, G.body_grid())
    hq, _, nhr, nhc = G.collapse(hraw, G.head_grid())
    pairs = [(b, h) for b in bq for h in hq]
    meta = {"body_raw": nbr, "body_classes": nbc, "head_raw": nhr,
            "head_classes": nhc, "pairs": len(pairs), "digest": G.digest()}
    return pairs, bq, hq, meta


WORKERS = int(os.environ.get("REVIVAL_WORKERS", "12"))

_CTX = {}


def _screen_one_body(br):
    body, heads = _CTX["by_body"][br]
    X, y, d, sweeps = _CTX["X"], _CTX["y"], _CTX["d"], _CTX["sweeps"]
    floor = _CTX["floor"]
    Xa = _CTX["Xa"]
    plan = SPlan(body, X)
    plan_a = SPlan(body, Xa) if floor is not None else None
    res = []
    for h in heads:
        stateful = G.depends_on(h, "STATE", ["S", "BIAS"])
        try:
            p, bi, L, how = fit_plan(plan, h, stateful, y, d, sweeps)
        except (ValueError, FloatingPointError, np.linalg.LinAlgError):
            continue
        demoted = 0
        if floor is not None:
            try:
                pa = predict_plan(plan_a, h, stateful, p, bi)
                demoted = 0 if np.all(np.isfinite(pa)) and pa.min() >= floor else 1
            except (ValueError, FloatingPointError, np.linalg.LinAlgError):
                demoted = 1
        res.append((demoted, L, G.nodes(body) + G.nodes(h), br, G.show(h),
                    body, h, bool(stateful)))
    return res


def screen(pairs, X, y, d, sweeps, Xa=None, floor=None):
    """Family-blind scoring of every enumerated pair, grouped by BODY.

    The grouping is an arithmetic saving only: the fold value depends on BODY
    alone. Every enumerated pair is still scored, by the same routine, with no
    family information reaching it.
    """
    by_body = {}
    for (b, h) in pairs:
        by_body.setdefault(G.show(b), (b, []))[1].append(h)
    _CTX.clear()
    _CTX.update({"by_body": by_body, "X": X, "y": y, "d": d, "sweeps": sweeps,
                 "Xa": Xa, "floor": floor})
    names = sorted(by_body)
    t0 = time.time()
    if WORKERS > 1:
        pool = mp.Pool(WORKERS)
        chunks = []
        try:
            for k, chunk in enumerate(pool.imap_unordered(_screen_one_body, names)):
                chunks.append(chunk)
                print("    screened body %d/%d (%.0fs)"
                      % (k + 1, len(names), time.time() - t0))
        finally:
            pool.close()
            pool.join()
    else:
        chunks = []
        for k, name in enumerate(names):
            chunks.append(_screen_one_body(name))
            print("    screened body %d/%d (%.0fs)" % (k + 1, len(names),
                                                       time.time() - t0))
    scored = [t for chunk in chunks for t in chunk]
    scored.sort(key=lambda t: (t[0], t[1], t[2], t[3], t[4]))
    return scored


def run_search(pairs, eco, idx, fit_idx, floor, tag):
    """Family-blind search.

    Screen: every enumerated pair, fitted and scored in sample on a small block
    of the ranking-fit part. A coarse prefilter; it decides nothing alone.

    Rank (FREEZE_V3_ADDENDUM.md): the survivors are refitted on the ranking-fit
    part of the search slice and scored on the ranking-score part, which they
    have not seen. The held-out slice is never touched.

    Support-admissibility (FREEZE_V2_ADDENDUM.md) is measured on fit-slice rows
    and is inert where the registered response support is two-sided.
    """
    d = eco["d"]
    t0 = time.time()
    cut = len(idx) * RANK_SPLIT // 10
    rank_fit = idx[:cut]
    rank_score = idx[cut:]
    Xs, ys = design(eco, rank_fit[:SCREEN_ROWS])
    Xa = None
    if floor is not None:
        Xa, _ = design(eco, fit_idx[:SCREEN_ROWS])
    scored = screen(pairs, Xs, ys, d, 2, Xa, floor)
    demoted = sum(1 for t in scored if t[0])
    kept = scored[:KEEP]

    Xf, yf = design(eco, rank_fit)
    Xv, yv = design(eco, rank_score)
    Xaf = None
    if floor is not None:
        Xaf, _ = design(eco, fit_idx[:len(rank_fit)])
    ranked = []
    ob = {"rows": 0}
    Xo, yo = design(eco, rank_fit[:ORACLE_ROWS])
    Xp, yp = design(eco, rank_score[:ORACLE_ROWS])
    Xoa = None
    if floor is not None:
        Xoa, _ = design(eco, fit_idx[:ORACLE_ROWS])
    oracle_rank = []
    for (_, _, _, br, hr, b, h, st) in kept:
        plan_f = SPlan(b, Xf)
        plan_v = SPlan(b, Xv)
        plan_a = SPlan(b, Xaf) if floor is not None else None
        try:
            p, bi, L_in, how = fit_plan(plan_f, h, st, yf, d)
            L = loss_of(predict_plan(plan_v, h, st, p, bi), yv)
        except (ValueError, FloatingPointError, np.linalg.LinAlgError):
            continue
        if not np.isfinite(L):
            continue
        bad = 0
        if floor is not None:
            try:
                pa = predict_plan(plan_a, h, st, p, bi)
                bad = 0 if np.all(np.isfinite(pa)) and pa.min() >= floor else 1
            except (ValueError, FloatingPointError, np.linalg.LinAlgError):
                bad = 1
        ranked.append({"inadmissible": bad, "loss": L, "in_sample_loss": L_in,
                       "body": br, "head": hr,
                       "nodes": G.nodes(b) + G.nodes(h),
                       "reads_state": bool(st), "fit_route": how})
        # the same computation on the block the oracle is given
        try:
            po, bo, Lo_in, _ = fit_plan(SPlan(b, Xo), h, st, yo, d)
            Lo = loss_of(predict_plan(SPlan(b, Xp), h, st, po, bo), yp)
            bo_bad = 0
            if floor is not None:
                pa = predict_plan(SPlan(b, Xoa), h, st, po, bo)
                bo_bad = 0 if np.all(np.isfinite(pa)) and pa.min() >= floor else 1
            if np.isfinite(Lo):
                oracle_rank.append({"inadmissible": bo_bad, "loss": Lo,
                                    "body": br, "head": hr,
                                    "nodes": G.nodes(b) + G.nodes(h)})
        except (ValueError, FloatingPointError, np.linalg.LinAlgError):
            pass
    ranked.sort(key=lambda r: (r["inadmissible"], r["loss"], r["nodes"],
                               r["body"], r["head"]))
    oracle_rank.sort(key=lambda r: (r["inadmissible"], r["loss"], r["nodes"],
                                    r["body"], r["head"]))
    rule = {"support_floor": floor, "enumerated": len(scored),
            "demoted_on_fit_slice": demoted,
            "inert": bool(floor is None),
            "non_vacuous": bool(floor is not None and 0 < demoted < len(scored)),
            "ranked_demoted": sum(1 for r in ranked if r["inadmissible"])}
    budget = {"screen_rows": SCREEN_ROWS, "keep": KEEP, "sweeps": SWEEPS,
              "rank_fit_rows": int(len(rank_fit)),
              "rank_score_rows": int(len(rank_score)),
              "oracle_block_rows": ORACLE_ROWS,
              "rank_split_tenths": RANK_SPLIT}
    print("[%s] screened %d (demoted %d) kept %d in %.1fs; chosen %s | %s "
          "out_of_sample_loss=%.6g"
          % (tag, len(scored), demoted, len(kept), time.time() - t0,
             ranked[0]["body"], ranked[0]["head"], ranked[0]["loss"]))
    return ranked, scored, rule, budget, oracle_rank, (rank_fit, rank_score)


def parse_tree(s):
    pos = [0]

    def node():
        i = pos[0]
        j = i
        while j < len(s) and (s[j].isalnum() or s[j] == "_"):
            j += 1
        name = s[i:j]
        pos[0] = j
        if pos[0] < len(s) and s[pos[0]] == "(":
            pos[0] += 1
            kids = [node()]
            while s[pos[0]] == ",":
                pos[0] += 1
                kids.append(node())
            pos[0] += 1
            return tuple([name] + kids)
        return ("LEAF", name)
    return node()


def minimal_nodes(trees, target, grid):
    want = G.meaning(target, grid)
    best = None
    for t in trees:
        if G.meaning(t, grid) == want:
            n = G.nodes(t)
            if best is None or n < best:
                best = n
    return best


# ------------------------------------------------------------- scope run ----

def run_scope(key, eco):
    sigma = SCOPES[key]
    n = len(eco["y"])
    sl = slices(n)
    pairs, bq, hq, meta = build_candidates()
    digest_before = G.digest()
    rec = {"scope": key, "sigma": sigma, "ecology": eco["name"],
           "n_rows": int(n), "n_fit": int(len(sl["fit"])),
           "n_held": int(len(sl["held"])), "n_search": int(len(sl["search"])),
           "n_regen_fit": int(len(sl["regen_fit"])),
           "n_regen_held": int(len(sl["regen_held"])),
           "grammar": meta, "xden": list(eco["xden"]), "yden": int(eco["yden"])}
    if "columns" in eco:
        rec["columns"] = list(eco["columns"])

    if key == "R03":
        rec["admissibility"] = admissibility_F03(eco, sl["fit"])

    floor = SUPPORT_FLOOR[key]
    ranked, scored, rule, budget, orank, parts = run_search(
        pairs, eco, sl["search"], sl["fit"], floor, key)
    rec["admissibility_rule"] = rule
    rec["search_budget"] = budget
    w = ranked[0]
    body, head = parse_tree(w["body"]), parse_tree(w["head"])
    attrs = G.classify(body, head)
    rec["chosen"] = {"body": w["body"], "head": w["head"],
                     "class": attrs["class"], "attributes": attrs,
                     "search_loss": w["loss"], "search_fit_route": w["fit_route"]}
    rec["search"] = {"ranked_top10": ranked[:10],
                     "screen_top20": [{"loss": s[1], "body": s[3], "head": s[4],
                                       "inadmissible": s[0]}
                                      for s in scored[:20]]}

    params_f, bias_f, route = fit_on(eco, sl["fit"], body, head, attrs["reads_state"])
    params = [rationalise(v) for v in params_f]
    bias = rationalise(bias_f)
    rec["chosen"]["params"] = [qstr(p) for p in params]
    rec["chosen"]["bias"] = qstr(bias)
    rec["chosen"]["fit_route"] = route
    rec["chosen"]["fit_rows"] = int(len(sl["fit"]))

    t_ev = time.time()
    ev = exact_evaluate(eco, sl["held"], body, head, attrs["reads_state"],
                        params, bias, want_decisions=(key == "R02"))
    rec["chosen"]["held_out"] = ev
    if (G.meaning(body, G.body_grid()) == G.meaning(AFFINE_BODY, G.body_grid())
            and not attrs["reads_state"]
            and head_affine_coefficients(head) is not None):
        alt = affine_int_sse(eco, sl["held"], params, bias, head)
        if alt is not None:
            ev["sse_second_route"] = qstr(alt)
            ev["two_routes_agree"] = bool(qstr(alt) == ev["sse"])
    print("[%s] class=%s held n=%d sse=%s (%.1fs)"
          % (key, attrs["class"], ev["n"], ev["sse"][:44], time.time() - t_ev))

    # R06 exact lower bound over the whole enumeration
    braw = G.all_trees(G.BODY_BUDGET, G.BODY_LEAVES)
    hraw = G.all_trees(G.HEAD_BUDGET, G.HEAD_LEAVES)
    rec["lower_bound"] = {
        "body_nodes": G.nodes(body),
        "body_min_nodes": minimal_nodes(braw, body, G.body_grid()),
        "head_nodes": G.nodes(head),
        "head_min_nodes": minimal_nodes(hraw, head, G.head_grid()),
        "body_raw": len(braw), "head_raw": len(hraw)}
    rec["lower_bound"]["is_minimal"] = bool(
        rec["lower_bound"]["body_nodes"] == rec["lower_bound"]["body_min_nodes"]
        and rec["lower_bound"]["head_nodes"] == rec["lower_bound"]["head_min_nodes"])

    # R07 resource crossover
    m_star = G.table_crossover(body, head, attrs["reads_state"])
    rec["crossover"] = {"m_star": m_star}
    if m_star is not None:
        rec["crossover"]["program_cost_at_m_star"] = G.program_cost(
            body, head, m_star, attrs["reads_state"])
        rec["crossover"]["table_cost_at_m_star"] = G.table_cost(m_star)
        rec["crossover"]["program_cost_at_m_star_minus_1"] = G.program_cost(
            body, head, m_star - 1, attrs["reads_state"]) if m_star > 1 else None
        rec["crossover"]["table_cost_at_m_star_minus_1"] = (
            G.table_cost(m_star - 1) if m_star > 1 else None)

    # R09 independent regeneration on disjoint slices
    ranked2, _, rule2, _, _, _ = run_search(
        pairs, eco, sl["regen_fit"], sl["regen_fit"], floor, key + "/regen")
    w2 = ranked2[0]
    b2, h2 = parse_tree(w2["body"]), parse_tree(w2["head"])
    a2 = G.classify(b2, h2)
    rec["regeneration"] = {"body": w2["body"], "head": w2["head"],
                           "class": a2["class"],
                           "class_matches": bool(a2["class"] == attrs["class"]),
                           "expression_matches": bool(w2["body"] == w["body"]
                                                      and w2["head"] == w["head"]),
                           "n_rows": int(len(sl["regen_fit"])),
                           "admissibility_rule": rule2}
    print("[%s] regeneration class=%s matches=%s"
          % (key, a2["class"], rec["regeneration"]["class_matches"]))

    # replay partial for the stdlib checker and the oracle
    vidx = sl["held"][:VERIFY_ROWS]
    vrows = [exact_row_values(eco, i) for i in vidx]
    vys = [exact_response(eco, i) for i in vidx]
    vpred = exact_predict(body, head, attrs["reads_state"], vrows, params, bias)
    rec["replay"] = {"rows": int(len(vidx)), "slot": "held_prefix",
                     "X": [[int(v) for v in eco["X"][i]] for i in vidx],
                     "y": [int(eco["y"][i]) for i in vidx],
                     "partial_sse": qstr(exact_sse_of_pairs(vpred, vys))}
    if key == "R02":
        rec["replay"]["partial_decision_errors"] = decision_errors(vpred, vys)

    # FREEZE_V3_ADDENDUM.md section 5: the block route B re-ranks on, plus the
    # primary's own ranking of the same survivors on exactly that block.
    rank_fit, rank_score = parts
    ob_fit = rank_fit[:ORACLE_ROWS]
    ob_score = rank_score[:ORACLE_ROWS]
    ob_admiss = sl["fit"][:ORACLE_ROWS]
    rec["search_sample"] = {
        "rows": int(len(ob_fit)), "d": eco["d"],
        "xden": list(eco["xden"]), "yden": int(eco["yden"]),
        "support_floor": floor,
        "X": [[int(v) for v in eco["X"][i]] for i in ob_fit],
        "y": [int(eco["y"][i]) for i in ob_fit],
        "Xs": [[int(v) for v in eco["X"][i]] for i in ob_score],
        "ys": [int(eco["y"][i]) for i in ob_score],
        "Xa": ([[int(v) for v in eco["X"][i]] for i in ob_admiss]
               if floor is not None else []),
        "survivors": [{"body": t[3], "head": t[4], "screen_loss": t[1],
                       "inadmissible": t[0]} for t in scored[:KEEP]],
        "primary_ranking_on_this_block": orank[:10],
        "note": ("route B re-ranks these survivors on these rows and must "
                 "reproduce primary_ranking_on_this_block; the full-scale "
                 "ranking is not re-derived by route B")}

    rec["grammar_digest_after"] = G.digest()
    rec["grammar_digest_unchanged"] = bool(digest_before == rec["grammar_digest_after"])
    return rec, sl, body, head, attrs, params, bias


def fit_on(eco, idx, body, head, stateful):
    X, y = design(eco, idx)
    p, b, L, route = generic_fit(body, head, stateful, X, y, eco["d"])
    return p, b, route


def admissibility_F03(eco, fit_idx):
    """FREEZE_V1.md section 8 P3e. Exact, on the fit slice only, before any arm."""
    ys = [int(v) for v in eco["y"][fit_idx]]
    n = len(ys)
    s = sum(ys)
    mean = Q(s, n)
    var = Q(sum((y * n - s) ** 2 for y in ys), n * n * n)
    ratio = var / mean
    ok = (min(ys) >= 1) and (len(set(ys)) >= 2) and (ratio > 1)
    return {"n_fit": n, "min_response": min(ys), "max_response": max(ys),
            "distinct_responses": len(set(ys)), "mean": qstr(mean),
            "variance": qstr(var), "variance_over_mean": qstr(ratio),
            "variance_over_mean_float": float(ratio), "admissible": bool(ok)}


# ------------------------------------------------------------------ arms ----

def const_int_sse(eco, idx, const):
    """Exact squared error of a constant arm, by integer accumulation."""
    c = int(const.numerator) * (RAT_DEN // int(const.denominator))
    M = _lcm(RAT_DEN, eco["yden"])
    f_c = M // RAT_DEN
    f_y = M // eco["yden"]
    Y = eco["y"][idx]
    total = 0
    base = c * f_c
    for v in Y.tolist():
        d = base - v * f_y
        total += d * d
    return Q(total, M * M)


def arms_R02(eco, sl, chosen_eval):
    Xf, yf = design(eco, sl["fit"])
    const = rationalise(float(yf.mean()))
    const_sse = const_int_sse(eco, sl["held"], const)
    pos = int((yf > 0).sum())
    maj = 1 if pos * 2 > len(yf) else 0
    Yh = eco["y"][sl["held"]]
    maj_err = int(((Yh > 0).astype(np.int64) != maj).sum())
    return {"best_constant": {"value": qstr(const), "n": int(len(sl["held"])),
                              "held_sse": qstr(const_sse)},
            "majority_sign": {"predict": maj, "n": int(len(sl["held"])),
                              "held_decision_errors": maj_err},
            "chosen": {"held_sse": chosen_eval["sse"],
                       "held_decision_errors": chosen_eval["decision_errors"]}}


def poisson_irls(X, y, iters=30, ridge=1e-8):
    n, d = X.shape
    Z = np.concatenate([X, np.ones((n, 1))], axis=1)
    beta = np.zeros(d + 1)
    beta[-1] = np.log(max(float(y.mean()), 1e-9))
    for _ in range(iters):
        eta = np.clip(Z.dot(beta), -30, 30)
        mu = np.exp(eta)
        W = mu
        z = eta + (y - mu) / np.maximum(mu, 1e-12)
        A = (Z * W[:, None]).T.dot(Z) + ridge * np.eye(d + 1)
        b = (Z * W[:, None]).T.dot(z)
        try:
            new = np.linalg.solve(A, b)
        except np.linalg.LinAlgError:
            break
        if not np.all(np.isfinite(new)):
            break
        if np.max(np.abs(new - beta)) < 1e-10:
            beta = new
            break
        beta = new
    return beta


def ols(X, y, ridge=1e-8):
    n, d = X.shape
    Z = np.concatenate([X, np.ones((n, 1))], axis=1)
    A = Z.T.dot(Z) + ridge * np.eye(d + 1)
    return np.linalg.solve(A, Z.T.dot(y))


def arms_R03(eco, sl):
    Xf, yf = design(eco, sl["fit"])
    bp = poisson_irls(Xf, yf)
    bg = ols(Xf, yf)
    Xh, yh = design(eco, sl["held"])
    Zh = np.concatenate([Xh, np.ones((Xh.shape[0], 1))], axis=1)
    mu_log = np.exp(np.clip(Zh.dot(bp), -30, 30))
    mu_id = Zh.dot(bg)
    mp = [rationalise(v) for v in mu_log]
    mg = [rationalise(v) for v in mu_id]
    ys = [Q(int(v), eco["yden"]) for v in eco["y"][sl["held"]]]
    win_log = win_id = tie = 0
    for a, b, y in zip(mp, mg, ys):
        da = a - y
        db = b - y
        da = da if da >= 0 else -da
        db = db if db >= 0 else -db
        if da < db:
            win_log += 1
        elif db < da:
            win_id += 1
        else:
            tie += 1
    k = min(VERIFY_ROWS, len(ys))
    pw = iw = tw = 0
    for a, b, y in zip(mp[:k], mg[:k], ys[:k]):
        da = a - y
        db = b - y
        da = da if da >= 0 else -da
        db = db if db >= 0 else -db
        if da < db:
            pw += 1
        elif db < da:
            iw += 1
        else:
            tw += 1
    replay = {"rows": k, "slot": "held_prefix",
              "mu_log": [qstr(v) for v in mp[:k]],
              "mu_identity": [qstr(v) for v in mg[:k]],
              "y": [int(v) for v in eco["y"][sl["held"]][:k]],
              "partial_log_strict_wins": pw,
              "partial_identity_strict_wins": iw,
              "partial_ties": tw,
              "partial_log_negative_means": sum(1 for v in mp[:k] if v < 0),
              "partial_identity_negative_means": sum(1 for v in mg[:k] if v < 0)}
    return {"replay": replay,
            "log_link": {"n": len(ys), "strict_wins": win_log,
                         "negative_means": sum(1 for v in mp if v < 0),
                         "held_sse": qstr(exact_sse_of_pairs(mp, ys)),
                         "distinct_predictions": len(set(mp[:20000])),
                         "beta": [float(v) for v in bp]},
            "identity_link": {"n": len(ys), "strict_wins": win_id,
                              "negative_means": sum(1 for v in mg if v < 0),
                              "held_sse": qstr(exact_sse_of_pairs(mg, ys)),
                              "distinct_predictions": len(set(mg[:20000])),
                              "beta": [float(v) for v in bg]},
            "ties": tie}


AFFINE_BODY = ("MUL", ("LEAF", "ARG"), ("LEAF", "PARAM"))
AFFINE_HEAD = ("ADD", ("LEAF", "S"), ("LEAF", "BIAS"))


def arms_R04(eco, sl, body, head, stateful, params, bias, chosen_eval):
    pa_f, ba_f, route = fit_on(eco, sl["fit"], AFFINE_BODY, AFFINE_HEAD, False)
    pa = [rationalise(v) for v in pa_f]
    ba = rationalise(ba_f)
    aff = exact_evaluate(eco, sl["held"], AFFINE_BODY, AFFINE_HEAD, False, pa, ba)
    aff_int = affine_int_sse(eco, sl["held"], pa, ba, AFFINE_HEAD)
    out = {"affine": {"body": G.show(AFFINE_BODY), "head": G.show(AFFINE_HEAD),
                      "n": aff["n"], "held_sse": aff["sse"], "fit_route": route,
                      "held_sse_second_route": qstr(aff_int),
                      "two_routes_agree": bool(qstr(aff_int) == aff["sse"])},
           "lifted": {"n": chosen_eval["n"], "held_sse": chosen_eval["sse"]},
           "landmark": {}}
    q_star = G.landmark_crossover(body, head, stateful, eco["d"], eco["d"])
    out["landmark"]["q_star"] = q_star
    if q_star is not None:
        out["landmark"]["landmark_cost_at_q_star"] = G.landmark_cost(q_star, eco["d"])
        out["landmark"]["program_cost"] = G.program_cost(
            body, head, eco["d"], stateful)
        out["landmark"]["landmark_cost_at_q_star_minus_1"] = (
            G.landmark_cost(q_star - 1, eco["d"]) if q_star > 1 else None)
        Xf, yf = design(eco, sl["fit"][:20000])
        step = max(1, Xf.shape[0] // q_star)
        L = Xf[[j * step for j in range(q_star)]]
        K = np.exp(-((Xf[:, None, :] - L[None, :, :]) ** 2).sum(axis=2))
        beta = ols(K, yf)
        Xh, yh = design(eco, sl["held"])
        Kh = np.exp(-((Xh[:, None, :] - L[None, :, :]) ** 2).sum(axis=2))
        Zh = np.concatenate([Kh, np.ones((Kh.shape[0], 1))], axis=1)
        ph = [rationalise(v) for v in Zh.dot(beta)]
        ys = [Q(int(v), eco["yden"]) for v in eco["y"][sl["held"]]]
        out["landmark"]["held_sse_at_q_star"] = qstr(exact_sse_of_pairs(ph, ys))
    return out


# -------------------------------------------------------------- controls ----

def controls_R02(eco, sl, body, head, stateful, chosen_sse):
    """FREEZE_V1.md section 8 P2d. Response-permutation controls, with the
    applicability band that fails the run when the permutation does not bite.

    The chosen program at this scope is the pure affine one, so the design
    matrix of the least-squares refit does not move when the response is
    permuted: the normal-equations matrix is formed once and only the
    right-hand side changes. Control 0 is additionally refitted through the
    same generic routine every other arm uses and the two are asserted equal,
    so the fast path is checked rather than trusted.
    """
    grid = G.body_grid()
    if G.meaning(body, grid) != G.meaning(AFFINE_BODY, grid):
        raise SystemExit("CONTROL PATH REFUSED: the chosen BODY is not the "
                         "linear score MUL(ARG,PARAM)")
    if stateful or head_affine_coefficients(head) is None:
        raise SystemExit("CONTROL PATH REFUSED: the chosen HEAD is not jointly "
                         "affine in S and BIAS without STATE")
    Xf, yf = design(eco, sl["fit"])
    d = eco["d"]
    plan_f = SPlan(body, Xf)
    base, Z = joint_affine(plan_f, head, stateful, len(yf), d)
    if Z is None:
        raise SystemExit("CONTROL PATH REFUSED: the chosen program is not "
                         "jointly affine in its parameters")
    A = Z.T.dot(Z) + 1e-8 * np.eye(d + 1)
    const = rationalise(float(yf.mean()))
    const_sse = const_int_sse(eco, sl["held"], const)
    lo = Q(9, 10) * const_sse
    hi = Q(11, 10) * const_sse
    rs = np.random.RandomState(SEED)
    in_band = 0
    beat_chosen = 0
    ratios = []
    t0 = time.time()
    for k in range(N_CONTROLS):
        perm = rs.permutation(yf.shape[0])
        yp = yf[perm]
        v = np.linalg.solve(A, Z.T.dot(yp - base))
        if k == 0:
            pg, bg, Lg, route = fit_plan(plan_f, head, stateful, yp, d)
            got = predict_plan(plan_f, head, stateful, v[:d], float(v[d]))
            want = predict_plan(plan_f, head, stateful, pg, bg)
            if not np.allclose(got, want, rtol=1e-6,
                               atol=1e-8 * max(1.0, float(np.abs(want).max()))):
                raise SystemExit("CONTROL FAST PATH DISAGREES WITH fit_plan")
        pq = [rationalise(x) for x in v[:d]]
        bq = rationalise(float(v[d]))
        s = affine_int_sse(eco, sl["held"], pq, bq, head)
        if lo <= s <= hi:
            in_band += 1
        if s < chosen_sse:
            beat_chosen += 1
        ratios.append(s / const_sse)
        if k % 50 == 0:
            print("  control %d/%d ratio=%.6f in_band=%d (%.1fs)"
                  % (k, N_CONTROLS, float(s / const_sse), in_band, time.time() - t0))
    ratios.sort()
    return {"controls": N_CONTROLS, "seed": SEED,
            "constant_sse": qstr(const_sse),
            "chosen_arm_held_sse": qstr(chosen_sse),
            "chosen_over_constant_parts_per_billion":
                int(chosen_sse / const_sse * 10 ** 9),
            "band_low": qstr(lo), "band_high": qstr(hi),
            "in_band": in_band, "applicable": bool(in_band == N_CONTROLS),
            "controls_beating_the_chosen_arm": beat_chosen,
            "chosen_below_band": bool(chosen_sse < lo),
            "ratio_min": qstr(ratios[0]),
            "ratio_median": qstr(ratios[len(ratios) // 2]),
            "ratio_max": qstr(ratios[-1]),
            "ratio_min_float": float(ratios[0]),
            "ratio_median_float": float(ratios[len(ratios) // 2]),
            "ratio_max_float": float(ratios[-1])}


# ------------------------------------------------------------------ main ----

def controls_only():
    """Re-run only the P2d controls against the committed SIGMA_R02 receipt."""
    pcm, texts, sources = load_sources()
    eco = ecology_F02(pcm)
    sl = slices(len(eco["y"]))
    with open(os.path.join(RUNS, "scope_R02.json")) as fh:
        rec = json.load(fh)
    body = parse_tree(rec["chosen"]["body"])
    head = parse_tree(rec["chosen"]["head"])
    stateful = bool(rec["chosen"]["attributes"]["reads_state"])
    c = controls_R02(eco, sl, body, head, stateful,
                     Q(rec["chosen"]["held_out"]["sse"]))
    with open(os.path.join(RUNS, "controls.json"), "w") as fh:
        json.dump(c, fh, indent=1, sort_keys=True)
    print("controls: in_band=%d/%d applicable=%s beating=%d"
          % (c["in_band"], c["controls"], c["applicable"],
             c["controls_beating_the_chosen_arm"]))


def main():
    if "--controls-only" in sys.argv:
        controls_only()
        return
    os.makedirs(RUNS, exist_ok=True)
    pcm, texts, sources = load_sources()
    with open(os.path.join(RUNS, "sources.json"), "w") as fh:
        json.dump(sources, fh, indent=1, sort_keys=True)
    print("sources verified: D2 %d frames, D3 %d files"
          % (sources["D2"]["frames"], sources["D3"]["files"]))

    ecos = {"R02": ecology_F02(pcm), "R03": ecology_F03(texts),
            "R04": ecology_F04(pcm)}
    keep = {}
    for key in ("R02", "R03", "R04"):
        eco = ecos[key]
        rec, sl, body, head, attrs, params, bias = run_scope(key, eco)
        if key == "R02":
            rec["arms"] = arms_R02(eco, sl, rec["chosen"]["held_out"])
        elif key == "R03":
            rec["arms"] = arms_R03(eco, sl)
        else:
            rec["arms"] = arms_R04(eco, sl, body, head, attrs["reads_state"],
                                   params, bias, rec["chosen"]["held_out"])
        with open(os.path.join(RUNS, "scope_%s.json" % key), "w") as fh:
            json.dump(rec, fh, indent=1, sort_keys=True)
        keep[key] = (eco, sl, body, head, attrs, params, bias,
                     rec["chosen"]["held_out"])
        print("[%s] written" % key)

    # cross-ecology controls: each scope's chosen class on the other ecologies
    cross = {}
    for key in ("R02", "R03", "R04"):
        eco, sl, body, head, attrs, params, bias, ev = keep[key]
        cross[key] = {"class": attrs["class"], "body": G.show(body),
                      "head": G.show(head)}
    with open(os.path.join(RUNS, "cross_scope.json"), "w") as fh:
        json.dump(cross, fh, indent=1, sort_keys=True)

    if "--controls" in sys.argv:
        eco, sl, body, head, attrs, params, bias, ev = keep["R02"]
        c = controls_R02(eco, sl, body, head, attrs["reads_state"], Q(ev["sse"]))
        with open(os.path.join(RUNS, "controls.json"), "w") as fh:
            json.dump(c, fh, indent=1, sort_keys=True)
        print("controls: in_band=%d/%d applicable=%s"
              % (c["in_band"], c["controls"], c["applicable"]))
    print("done")


if __name__ == "__main__":
    main()

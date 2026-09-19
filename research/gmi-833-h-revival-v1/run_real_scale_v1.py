"""Real-scale run driver for gmi-833-h-revival-v1 (scopes SIGMA_V02 and
SIGMA_V03 and their matched negative controls T02, T03).

Runs on the host of record (FREEZE_V1.md section 5). Reads the sha256-bound
real sources, builds the registered ecologies, runs the family-blind
enumerative search over G_S under each scope's registered loss, fits the arms
at real scale and writes the receipts under REAL_RUNS/ that the stdlib checker
replays exactly.

Numpy is used only inside fitting and screening. Every claimed quantity is
recomputed exactly with fractions.Fraction, or as a certified interval
(certify_v1), before it is written.

Usage:  python3 -B run_real_scale_v1.py [--controls] [--quick] [--only V02,V03,T02,T03]
"""
from fractions import Fraction as Q
import glob
import hashlib
import json
import multiprocessing as mp
import os
import sys
import time
import wave

import numpy as np

import grammar_s_v1 as G
import certify_v1 as CERT

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "REAL_RUNS")

RAT_DEN = 10 ** 9              # FREEZE_V1.md section 9
SEED = 20260919                # controls and multistart, sections 11, 12
SCREEN_ROWS = 400
ORACLE_ROWS = 1500
RANK_SPLIT = 7                 # tenths of the search slice used to fit the ranking
KEEP = 40
N_CONTROLS = 200
VERIFY_ROWS = 1500
N_STARTS = 6
ITERS = {"screen": 40, "rank": 200, "final": 600}

D2_DIGEST = "a9f677295dcb2d102bb43b86cbad70babe208c1a5fd38a2ae4d8a05f7fdb7a7a"
D3_DIGEST = "41607de5c1577303abc83cccfd29e5d12e6c180689d9fc3d98eac3f97dec9ec9"

SCOPES = {"V02": "SIGMA_V02", "V03": "SIGMA_V03"}
CONTROLS = {"T02": "control_for_SIGMA_V02", "T03": "control_for_SIGMA_V03"}
LOSS = {"V02": "squared", "V03": "deviance", "T02": "squared", "T03": "deviance"}
PEP8_LIMIT = 79


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
               "frames": int(len(pcm)), "digest_of_digests": d2, "per_file": d2parts},
        "D3": {"files": len(pys), "bytes": sum(len(t) for _, t in texts),
               "digest_of_digests": d3},
    }
    return pcm, texts, sources


# ------------------------------------------------------------- ecologies ----

V02_COLS = ("lead", "alpha", "space", "usc", "eq", "paren", "brack", "comma",
            "dot", "quote", "hash", "digit")
V02_DEN = (16, 64, 64, 8, 4, 8, 8, 8, 8, 8, 4, 8)


def d3_lines(texts):
    """FREEZE_V1.md section 5.1: latin-1, split on newline, len >= 1."""
    lines = []
    for _, raw in texts:
        t = raw.decode("latin-1")
        for ln in t.split("\n"):
            if len(ln) >= 1:
                lines.append(ln)
    return lines


def _line_census(lines):
    rows = np.zeros((len(lines), 12), dtype=np.int64)
    lens = np.zeros(len(lines), dtype=np.int64)
    for i, ln in enumerate(lines):
        c = [0] * 12
        j = 0
        while j < len(ln) and ln[j] == " ":
            j += 1
        c[0] = j
        for ch in ln:
            if "0" <= ch <= "9":
                c[11] += 1
            elif ch.isalpha():
                c[1] += 1
            elif ch == " ":
                c[2] += 1
            elif ch == "_":
                c[3] += 1
            elif ch == "=":
                c[4] += 1
            elif ch in "()":
                c[5] += 1
            elif ch in "[]":
                c[6] += 1
            elif ch == ",":
                c[7] += 1
            elif ch == ".":
                c[8] += 1
            elif ch in "\"'":
                c[9] += 1
            elif ch == "#":
                c[10] += 1
        rows[i] = c
        lens[i] = len(ln)
    return rows, lens


def ecology_V02(lines):
    X, lens = _line_census(lines)
    return {"name": "V02", "X": X, "y": lens - PEP8_LIMIT, "d": 12,
            "xden": V02_DEN, "yden": 64, "loss": "squared", "columns": V02_COLS,
            "response": "(len - 79) / 64", "label": "[y > 0]"}


def ecology_T03(lines):
    X, lens = _line_census(lines)
    return {"name": "T03", "X": X, "y": lens, "d": 12, "xden": V02_DEN,
            "yden": 1, "loss": "deviance", "columns": V02_COLS,
            "response": "len"}


TOKEN_START = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_")
TOKEN_REST = TOKEN_START | set("0123456789")
VOWELS = set("aeiouAEIOU")


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


V03_COLS = ("tok_len", "lead_us", "trail_us", "upper", "lower", "digits",
            "underscores", "vowels", "first_is_us", "file_bytes",
            "file_lines", "file_tokens")


def ecology_V03(texts):
    """FREEZE_V1.md section 5.2: the F03 construction, verbatim."""
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
    return {"name": "V03", "X": X, "y": y, "d": X.shape[1], "xden": tuple(den),
            "yden": 1, "loss": "deviance", "columns": V03_COLS}


def ecology_T02(pcm):
    """FREEZE_V1.md section 5.3: the F04b construction, verbatim."""
    d = 32
    n = len(pcm) - 33
    idx = np.arange(n)[:, None] + np.arange(1, d + 1)[None, :]
    X = pcm[idx]
    positive = (pcm > 0).astype(np.int64)
    cs = np.concatenate([[0], np.cumsum(positive)])
    y = cs[32:32 + n] - cs[0:n]
    return {"name": "T02", "X": X, "y": y, "d": d, "xden": (32768,) * d,
            "yden": 32, "loss": "squared"}


# ---------------------------------------------------------------- slices ----

def slices(n):
    """FREEZE_V1.md section 5.4. Modulus 8."""
    i = np.arange(n)
    m = i % 8
    return {"search": i[m == 5], "held": i[m == 6], "regen": i[m == 7],
            "fit": i[m <= 4]}


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
        src = "def _f(arg, param, _shape):\n    return " + _np_source(body) + "\n"
        env = {"np": np, "_np_reciprocal": _np_reciprocal}
        exec(src, env)
        _BODY_CACHE[key] = env["_f"]
    return _BODY_CACHE[key]


def head_fn(head):
    key = G.show(head)
    if key not in _HEAD_CACHE:
        src = "def _g(s, bias, state, _shape):\n    return " + _np_source(head) + "\n"
        env = {"np": np, "_np_reciprocal": _np_reciprocal}
        exec(src, env)
        _HEAD_CACHE[key] = env["_g"]
    return _HEAD_CACHE[key]


def head_scalar_fn(head):
    key = G.show(head)
    if key not in _HEAD_SCALAR_CACHE:
        src = "def _h(s, bias, state):\n    return " + G.to_python(head) + "\n"
        env = {"_reciprocal": _reciprocal}
        exec(src, env)
        _HEAD_SCALAR_CACHE[key] = env["_h"]
    return _HEAD_SCALAR_CACHE[key]


class SPlan(object):
    """Shared fold-value plan for one BODY on one design block (the fold value
    depends on BODY alone). When BODY is affine in PARAM — decided on the
    frozen probe grid — S is an offset plus a matrix-vector product."""

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


def predict_plan(plan, head, stateful, params, bias):
    return apply_head(head, plan.fold(params), bias, stateful)


def loss_squared(pred, y):
    r = pred - y
    return float(np.dot(r, r))


def loss_deviance(pred, y):
    """FREEZE_V1.md section 5.2: Poisson deviance, +inf if any mean <= 0."""
    if not np.all(np.isfinite(pred)) or np.any(pred <= 0.0):
        return float("inf")
    pos = y > 0
    term = np.zeros_like(y)
    term[pos] = y[pos] * np.log(y[pos] / pred[pos])
    return float(2.0 * np.sum(term - (y - pred)))


def loss_of(kind, pred, y):
    if kind == "squared":
        return loss_squared(pred, y)
    return loss_deviance(pred, y)


def joint_affine(plan, head, stateful, d):
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


def _num_grad(f, theta, f0):
    g = np.zeros_like(theta)
    for j in range(len(theta)):
        h = 1e-6 * max(1.0, abs(theta[j]))
        tp = theta.copy()
        tp[j] += h
        tm = theta.copy()
        tm[j] -= h
        fp = f(tp)
        fm = f(tm)
        if np.isfinite(fp) and np.isfinite(fm):
            g[j] = (fp - fm) / (2 * h)
        elif np.isfinite(fp):
            g[j] = (fp - f0) / h
        elif np.isfinite(fm):
            g[j] = (f0 - fm) / h
        else:
            g[j] = 0.0
    return g


def descend(f, theta0, iters, memory=10):
    """Generic first-order descent: L-BFGS direction from numerical gradients
    with backtracking (Armijo) line search. One routine for every candidate."""
    theta = np.array(theta0, dtype=np.float64)
    f0 = f(theta)
    if not np.isfinite(f0):
        return theta, f0
    s_hist = []
    y_hist = []
    g = _num_grad(f, theta, f0)
    for it in range(iters):
        if not np.all(np.isfinite(g)) or np.linalg.norm(g) < 1e-12:
            break
        q = g.copy()
        alphas = []
        for s, yv in reversed(list(zip(s_hist, y_hist))):
            rho = 1.0 / max(float(np.dot(yv, s)), 1e-300)
            a = rho * float(np.dot(s, q))
            alphas.append((a, rho, yv))
            q = q - a * yv
        if s_hist:
            s, yv = s_hist[-1], y_hist[-1]
            gamma = float(np.dot(s, yv)) / max(float(np.dot(yv, yv)), 1e-300)
            q = gamma * q
        else:
            q = q / max(np.linalg.norm(q), 1e-300) * min(1.0, 1.0 / max(1.0, abs(f0)))
        for (a, rho, yv), s in zip(reversed(alphas), s_hist):
            b = rho * float(np.dot(yv, q))
            q = q + s * (a - b)
        d = -q
        if float(np.dot(d, g)) >= 0:
            d = -g
            s_hist = []
            y_hist = []
        step = 1.0
        accepted = False
        gd = float(np.dot(g, d))
        for _ in range(40):
            cand = theta + step * d
            fc = f(cand)
            if np.isfinite(fc) and fc <= f0 + 1e-4 * step * gd:
                accepted = True
                break
            step *= 0.5
        if not accepted:
            break
        g_new = _num_grad(f, cand, fc)
        s_vec = cand - theta
        y_vec = g_new - g
        if float(np.dot(s_vec, y_vec)) > 1e-12:
            s_hist.append(s_vec)
            y_hist.append(y_vec)
            if len(s_hist) > memory:
                s_hist.pop(0)
                y_hist.pop(0)
        theta = cand
        if f0 - fc < 1e-12 * max(1.0, abs(f0)):
            f0 = fc
            g = g_new
            break
        f0 = fc
        g = g_new
    return theta, f0


def fit_plan(plan, head, stateful, y, d, kind, iters):
    """FREEZE_V1.md section 11: one generic routine for every candidate."""
    base, Z = joint_affine(plan, head, stateful, d)
    if Z is not None and kind == "squared":
        p, b = lsq_from(base, Z, y, d)
        L = loss_of(kind, predict_plan(plan, head, stateful, p, b), y)
        if not np.isfinite(L):
            raise ValueError("non-finite")
        return p, b, L, "LEAST_SQUARES"

    def f(theta):
        try:
            with np.errstate(all="ignore"):
                pred = predict_plan(plan, head, stateful, theta[:d], theta[d])
                return loss_of(kind, pred, y)
        except (ValueError, FloatingPointError, np.linalg.LinAlgError):
            return float("inf")
    starts = [np.zeros(d + 1)]
    if Z is not None:
        p, b = lsq_from(base, Z, y, d)
        starts.append(np.concatenate([p, [b]]))
    rs = np.random.RandomState(SEED)
    for _ in range(N_STARTS):
        starts.append(rs.normal(size=d + 1))
    best = None
    for s in starts:
        v = f(s)
        if np.isfinite(v) and (best is None or v < best[1]):
            best = (s, v)
    if best is None:
        return np.zeros(d), 0.0, float("inf"), "NO_FINITE_START"
    theta, L = descend(f, best[0], iters)
    return theta[:d], float(theta[d]), float(L), "DESCENT"


# ------------------------------------------------------- exact arithmetic ----

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
    def __init__(self):
        self.M = 1
        self.acc = 0

    def add(self, diff):
        d = diff.denominator
        if self.M % d != 0:
            new_M = _lcm(self.M, d)
            if new_M > LCM_GUARD:
                raise ValueError("EXACT ACCUMULATION GUARD: common denominator "
                                 "exceeds 10**40")
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


def exact_evaluate_squared(eco, idx, body, head, stateful, params, bias, chunk=4000):
    sse = ExactSSE()
    errors = 0
    preds_seen = set()
    resp_seen = set()
    pos_pred = 0
    prev = Q(0)
    for start in range(0, len(idx), chunk):
        part = idx[start:start + chunk]
        for i in part:
            r = exact_row_values(eco, i)
            y = exact_response(eco, i)
            S = Q(0)
            for j, v in enumerate(r):
                S += G.value(body, {"ARG": v, "PARAM": params[j]})
            o = G.value(head, {"S": S, "BIAS": bias, "STATE": prev})
            if stateful:
                prev = o
            sse.add(o - y)
            if (1 if o > 0 else 0) != (1 if y > 0 else 0):
                errors += 1
            if o > 0:
                pos_pred += 1
            if len(preds_seen) < 20000:
                preds_seen.add(o)
                resp_seen.add(y)
    return {"n": int(len(idx)), "sse": qstr(sse.value()), "decision_errors": errors,
            "positive_decisions": pos_pred,
            "nondegeneracy": {"distinct_predictions": len(preds_seen),
                              "distinct_responses": len(resp_seen),
                              "response_is_constant": len(resp_seen) <= 1,
                              "prediction_is_constant": len(preds_seen) <= 1,
                              "emits_both_labels": 0 < pos_pred < len(idx)}}


def exact_means(eco, idx, body, head, stateful, params, bias):
    """Exact predicted means of a program on the rows (deviance scopes)."""
    out = []
    prev = Q(0)
    for i in idx:
        r = exact_row_values(eco, i)
        S = Q(0)
        for j, v in enumerate(r):
            S += G.value(body, {"ARG": v, "PARAM": params[j]})
        o = G.value(head, {"S": S, "BIAS": bias, "STATE": prev})
        if stateful:
            prev = o
        out.append(o)
    return out


def exact_sse_of_pairs(pred, ys):
    acc = ExactSSE()
    for a, b in zip(pred, ys):
        acc.add(a - b)
    return acc.value()


def head_affine_coefficients(head):
    z = G.value(head, {"S": Q(0), "BIAS": Q(0), "STATE": Q(0)})
    hs = G.value(head, {"S": Q(1), "BIAS": Q(0), "STATE": Q(0)}) - z
    hb = G.value(head, {"S": Q(0), "BIAS": Q(1), "STATE": Q(0)}) - z
    for a in (Q(-2), Q(3, 2), Q(2)):
        for b in (Q(-1), Q(1, 2), Q(2)):
            if G.value(head, {"S": a, "BIAS": b, "STATE": Q(0)}) != hs * a + hb * b + z:
                return None
    return hs, hb, z


def affine_int_sse(eco, idx, params, bias, head=None):
    """Second route to the exact squared error of a linear-score program by
    integer accumulation, when every xden is equal (V02 has mixed xden, so it
    returns None there and the streaming route stands alone at that scope)."""
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
    if (k_lin.denominator != 1 or k_const.denominator != 1 or k_y.denominator != 1):
        return None
    kl, kc, ky = int(k_lin), int(k_const), int(k_y)
    total = 0
    for v, yv in zip(lin.tolist(), Y.tolist()):
        dd = v * kl + kc - yv * ky
        total += dd * dd
    return Q(total, M * M)


def mixed_int_sse(eco, idx, params, bias):
    """Second route for V02 (mixed xden): pred_i = sum_j X_ij a_j / (xden_j 10^9)
    + b, with one common denominator M = lcm over columns."""
    dens = eco["xden"]
    b = Q(bias)
    M = eco["yden"]
    for dj in dens:
        M = _lcm(M, dj * RAT_DEN)
    M = _lcm(M, b.denominator)
    a = [int(Q(p) * M / dj) if (Q(p) * M / dj).denominator == 1 else None
         for p, dj in zip(params, dens)]
    if any(v is None for v in a):
        return None
    a = np.array(a, dtype=object)
    X = eco["X"][idx]
    Y = eco["y"][idx]
    kb = b * M
    ky = Q(M, eco["yden"])
    if kb.denominator != 1 or ky.denominator != 1:
        return None
    kb = int(kb)
    ky = int(ky)
    total = 0
    Xl = X.tolist()
    Yl = Y.tolist()
    al = [int(v) for v in a]
    for row, yv in zip(Xl, Yl):
        s = kb
        for xij, aj in zip(row, al):
            s += xij * aj
        dd = s - yv * ky
        total += dd * dd
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


WORKERS = int(os.environ.get("REVIVAL_WORKERS", "8"))
_CTX = {}


def _screen_one_body(br):
    body, heads = _CTX["by_body"][br]
    X, y, d, kind = _CTX["X"], _CTX["y"], _CTX["d"], _CTX["kind"]
    plan = SPlan(body, X)
    res = []
    for h in heads:
        stateful = G.depends_on(h, "STATE", ["S", "BIAS"])
        try:
            p, bi, L, how = fit_plan(plan, h, stateful, y, d, kind, ITERS["screen"])
        except (ValueError, FloatingPointError, np.linalg.LinAlgError):
            continue
        res.append((0 if np.isfinite(L) else 1, L if np.isfinite(L) else float("inf"),
                    G.nodes(body) + G.nodes(h), br, G.show(h), body, h, bool(stateful)))
    return res


def screen(pairs, X, y, d, kind):
    by_body = {}
    for (b, h) in pairs:
        by_body.setdefault(G.show(b), (b, []))[1].append(h)
    _CTX.clear()
    _CTX.update({"by_body": by_body, "X": X, "y": y, "d": d, "kind": kind})
    names = sorted(by_body)
    t0 = time.time()
    chunks = []
    if WORKERS > 1:
        pool = mp.Pool(WORKERS)
        try:
            for k, chunk in enumerate(pool.imap_unordered(_screen_one_body, names)):
                chunks.append(chunk)
                if k % 20 == 0:
                    print("    screened body %d/%d (%.0fs)" % (k + 1, len(names), time.time() - t0), flush=True)
        finally:
            pool.close()
            pool.join()
    else:
        for k, name in enumerate(names):
            chunks.append(_screen_one_body(name))
    scored = [t for chunk in chunks for t in chunk]
    scored.sort(key=lambda t: (t[0], int(round(t[1] * RAT_DEN)) if t[1] != float("inf") else 0,
                               t[2], t[3], t[4]))
    return scored


def run_search(pairs, eco, idx, tag):
    """FREEZE_V1.md section 11. Screen on 400 ranking-fit rows, rank the 40
    survivors out of sample on the ranking-score part; infinite loss (an
    inadmissible candidate under the deviance) ranks last."""
    d = eco["d"]
    kind = eco["loss"]
    t0 = time.time()
    cut = len(idx) * RANK_SPLIT // 10
    rank_fit = idx[:cut]
    rank_score = idx[cut:]
    Xs, ys = design(eco, rank_fit[:SCREEN_ROWS])
    scored = screen(pairs, Xs, ys, d, kind)
    kept = scored[:KEEP]
    Xf, yf = design(eco, rank_fit)
    Xv, yv = design(eco, rank_score)
    Xo, yo = design(eco, rank_fit[:ORACLE_ROWS])
    Xp, yp = design(eco, rank_score[:ORACLE_ROWS])
    ranked = []
    oracle_rank = []
    for (_, _, _, br, hr, b, h, st) in kept:
        plan_f = SPlan(b, Xf)
        plan_v = SPlan(b, Xv)
        try:
            p, bi, L_in, how = fit_plan(plan_f, h, st, yf, d, kind, ITERS["rank"])
            L = loss_of(kind, predict_plan(plan_v, h, st, p, bi), yv)
        except (ValueError, FloatingPointError, np.linalg.LinAlgError):
            continue
        ranked.append({"inadmissible": 0 if np.isfinite(L) else 1,
                       "loss": L if np.isfinite(L) else None,
                       "in_sample_loss": L_in if np.isfinite(L_in) else None,
                       "body": br, "head": hr, "nodes": G.nodes(b) + G.nodes(h),
                       "reads_state": bool(st), "fit_route": how})
        try:
            po, bo, Lo_in, _ = fit_plan(SPlan(b, Xo), h, st, yo, d, kind, ITERS["rank"])
            Lo = loss_of(kind, predict_plan(SPlan(b, Xp), h, st, po, bo), yp)
            oracle_rank.append({"inadmissible": 0 if np.isfinite(Lo) else 1,
                                "loss": Lo if np.isfinite(Lo) else None,
                                "body": br, "head": hr,
                                "nodes": G.nodes(b) + G.nodes(h)})
        except (ValueError, FloatingPointError, np.linalg.LinAlgError):
            pass

    def key(r):
        # FREEZE_V1.md section 9: a fitting routine's output is rationalised at
        # the registered precision before it is used, and the loss is one. Two
        # candidates whose losses agree at 10**-9 are a tie and the node count
        # decides, so a one-ulp float wobble cannot pick a longer spelling.
        L = r["loss"] if r["loss"] is not None else float("inf")
        Lq = int(round(L * RAT_DEN)) if L != float("inf") else None
        return (r["inadmissible"], Lq if Lq is not None else 0 if r["inadmissible"] else 0,
                r["nodes"], r["body"], r["head"])
    ranked.sort(key=key)
    oracle_rank.sort(key=key)
    budget = {"screen_rows": SCREEN_ROWS, "keep": KEEP, "iters": ITERS,
              "rank_fit_rows": int(len(rank_fit)), "rank_score_rows": int(len(rank_score)),
              "oracle_block_rows": ORACLE_ROWS, "rank_split_tenths": RANK_SPLIT,
              "starts": N_STARTS + 1, "seed": SEED}
    print("[%s] screened %d kept %d in %.1fs; chosen %s | %s loss=%s"
          % (tag, len(scored), len(kept), time.time() - t0, ranked[0]["body"],
             ranked[0]["head"], ranked[0]["loss"]), flush=True)
    return ranked, scored, budget, oracle_rank, (rank_fit, rank_score)


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


AFFINE_BODY = ("MUL", ("LEAF", "ARG"), ("LEAF", "PARAM"))
AFFINE_HEAD = ("ADD", ("LEAF", "S"), ("LEAF", "BIAS"))


def fit_on(eco, idx, body, head, stateful, iters):
    X, y = design(eco, idx)
    p, b, L, route = fit_plan(SPlan(body, X), head, stateful, y, eco["d"], eco["loss"], iters)
    return p, b, L, route


# ------------------------------------------------------------- scope run ----

def run_scope(key, eco, sigma):
    n = len(eco["y"])
    sl = slices(n)
    pairs, bq, hq, meta = build_candidates()
    digest_before = G.digest()
    rec = {"scope": key, "sigma": sigma, "ecology": eco["name"], "loss": eco["loss"],
           "n_rows": int(n), "n_fit": int(len(sl["fit"])), "n_held": int(len(sl["held"])),
           "n_search": int(len(sl["search"])), "n_regen": int(len(sl["regen"])),
           "grammar": meta, "xden": list(eco["xden"]), "yden": int(eco["yden"])}
    if "columns" in eco:
        rec["columns"] = list(eco["columns"])
    if "response" in eco:
        rec["response"] = eco["response"]
    if eco["loss"] == "deviance":
        rec["admissibility"] = admissibility(eco, sl["fit"])

    ranked, scored, budget, orank, parts = run_search(pairs, eco, sl["search"], key)
    rec["search_budget"] = budget
    w = ranked[0]
    body, head = parse_tree(w["body"]), parse_tree(w["head"])
    attrs = G.classify(body, head)
    rec["chosen"] = {"body": w["body"], "head": w["head"], "class": attrs["class"],
                     "attributes": attrs, "search_loss": w["loss"],
                     "search_fit_route": w["fit_route"]}
    rec["search"] = {"ranked_top10": ranked[:10],
                     "screen_top20": [{"loss": (s[1] if np.isfinite(s[1]) else None),
                                       "body": s[3], "head": s[4], "inadmissible": s[0]}
                                      for s in scored[:20]],
                     "screen_inadmissible": sum(1 for s in scored if s[0]),
                     "screen_enumerated": len(scored)}

    params_f, bias_f, Lfit, route = fit_on(eco, sl["fit"], body, head, attrs["reads_state"], ITERS["final"])
    params = [rationalise(v) for v in params_f]
    bias = rationalise(bias_f)
    rec["chosen"]["params"] = [qstr(p) for p in params]
    rec["chosen"]["bias"] = qstr(bias)
    rec["chosen"]["fit_route"] = route
    rec["chosen"]["fit_rows"] = int(len(sl["fit"]))
    rec["chosen"]["fit_loss_float_diagnostic"] = Lfit if np.isfinite(Lfit) else None

    t_ev = time.time()
    if eco["loss"] == "squared":
        ev = exact_evaluate_squared(eco, sl["held"], body, head, attrs["reads_state"], params, bias)
        rec["chosen"]["held_out"] = ev
        if (G.meaning(body, G.body_grid()) == G.meaning(AFFINE_BODY, G.body_grid())
                and not attrs["reads_state"] and head_affine_coefficients(head) is not None):
            hs, hb, h0 = head_affine_coefficients(head)
            if hs == 1 and h0 == 0:
                alt = mixed_int_sse(eco, sl["held"], params, hb * bias)
                if alt is not None:
                    ev["sse_second_route"] = qstr(alt)
                    ev["two_routes_agree"] = bool(qstr(alt) == ev["sse"])
        print("[%s] class=%s held n=%d sse=%s errors=%d (%.1fs)"
              % (key, attrs["class"], ev["n"], ev["sse"][:40], ev["decision_errors"],
                 time.time() - t_ev), flush=True)
    else:
        mu = exact_means(eco, sl["held"], body, head, attrs["reads_state"], params, bias)
        ys = [exact_response(eco, i) for i in sl["held"]]
        rec["chosen"]["held_out"] = {
            "n": int(len(sl["held"])),
            "nonpositive_means": CERT.nonpositive_count(mu),
            "deviance_interval": CERT.deviance_interval(ys, mu),
            "nondegeneracy": {"distinct_predictions": len(set(mu[:20000])),
                              "distinct_responses": len(set(ys[:20000]))}}
        rec["_mu_chosen"] = mu
        rec["_ys"] = ys
        print("[%s] class=%s held n=%d nonpositive=%d dev=%s (%.1fs)"
              % (key, attrs["class"], len(mu), rec["chosen"]["held_out"]["nonpositive_means"],
                 rec["chosen"]["held_out"]["deviance_interval"].get("lo", "INADMISSIBLE")[:20],
                 time.time() - t_ev), flush=True)

    braw = G.all_trees(G.BODY_BUDGET, G.BODY_LEAVES)
    hraw = G.all_trees(G.HEAD_BUDGET, G.HEAD_LEAVES)
    rec["lower_bound"] = {
        "body_nodes": G.nodes(body), "body_min_nodes": minimal_nodes(braw, body, G.body_grid()),
        "head_nodes": G.nodes(head), "head_min_nodes": minimal_nodes(hraw, head, G.head_grid()),
        "body_raw": len(braw), "head_raw": len(hraw)}
    rec["lower_bound"]["is_minimal"] = bool(
        rec["lower_bound"]["body_nodes"] == rec["lower_bound"]["body_min_nodes"]
        and rec["lower_bound"]["head_nodes"] == rec["lower_bound"]["head_min_nodes"])

    m_star = G.table_crossover(body, head, attrs["reads_state"])
    rec["crossover"] = {"m_star": m_star}
    if m_star is not None:
        rec["crossover"]["program_cost_at_m_star"] = G.program_cost(body, head, m_star, attrs["reads_state"])
        rec["crossover"]["table_cost_at_m_star"] = G.table_cost(m_star)
        rec["crossover"]["program_cost_at_m_star_minus_1"] = (
            G.program_cost(body, head, m_star - 1, attrs["reads_state"]) if m_star > 1 else None)
        rec["crossover"]["table_cost_at_m_star_minus_1"] = G.table_cost(m_star - 1) if m_star > 1 else None

    ranked2, _, _, _, _ = run_search(pairs, eco, sl["regen"], key + "/regen")
    w2 = ranked2[0]
    b2, h2 = parse_tree(w2["body"]), parse_tree(w2["head"])
    a2 = G.classify(b2, h2)
    rec["regeneration"] = {"body": w2["body"], "head": w2["head"], "class": a2["class"],
                           "class_matches": bool(a2["class"] == attrs["class"]),
                           "expression_matches": bool(w2["body"] == w["body"] and w2["head"] == w["head"]),
                           "n_rows": int(len(sl["regen"]))}
    print("[%s] regeneration class=%s matches=%s expr=%s"
          % (key, a2["class"], rec["regeneration"]["class_matches"],
             rec["regeneration"]["expression_matches"]), flush=True)

    vidx = sl["held"][:VERIFY_ROWS]
    vrows = [exact_row_values(eco, i) for i in vidx]
    vys = [exact_response(eco, i) for i in vidx]
    vpred = exact_predict(body, head, attrs["reads_state"], vrows, params, bias)
    rec["replay"] = {"rows": int(len(vidx)), "slot": "held_prefix",
                     "X": [[int(v) for v in eco["X"][i]] for i in vidx],
                     "y": [int(eco["y"][i]) for i in vidx]}
    if eco["loss"] == "squared":
        rec["replay"]["partial_sse"] = qstr(exact_sse_of_pairs(vpred, vys))
        rec["replay"]["partial_decision_errors"] = sum(
            1 for a, b in zip(vpred, vys) if (1 if a > 0 else 0) != (1 if b > 0 else 0))
    else:
        rec["replay"]["partial_nonpositive_means"] = CERT.nonpositive_count(vpred)
        rec["replay"]["mu_chosen"] = [qstr(v) for v in vpred]

    rank_fit, rank_score = parts
    ob_fit = rank_fit[:ORACLE_ROWS]
    ob_score = rank_score[:ORACLE_ROWS]
    rec["search_sample"] = {
        "rows": int(len(ob_fit)), "d": eco["d"], "xden": list(eco["xden"]),
        "yden": int(eco["yden"]), "loss": eco["loss"],
        "X": [[int(v) for v in eco["X"][i]] for i in ob_fit],
        "y": [int(eco["y"][i]) for i in ob_fit],
        "Xs": [[int(v) for v in eco["X"][i]] for i in ob_score],
        "ys": [int(eco["y"][i]) for i in ob_score],
        "survivors": [{"body": t[3], "head": t[4],
                       "screen_loss": (t[1] if np.isfinite(t[1]) else None),
                       "inadmissible": t[0]} for t in scored[:KEEP]],
        "primary_ranking_on_this_block": orank[:10],
        "note": ("route B re-ranks these survivors on these rows with its own "
                 "fitting routine and must reproduce primary_ranking_on_this_block; "
                 "the full-scale ranking is not re-derived by route B")}
    rec["grammar_digest_after"] = G.digest()
    rec["grammar_digest_unchanged"] = bool(digest_before == rec["grammar_digest_after"])
    return rec, sl, body, head, attrs, params, bias


def admissibility(eco, fit_idx):
    """FREEZE_V1.md section 12 V3e. Exact, on the fit slice only, before any arm."""
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
            "variance_over_mean_float_diagnostic": float(ratio), "admissible": bool(ok)}


# ------------------------------------------------------------------ arms ----

def const_int_sse(eco, idx, const):
    c = Q(const)
    M = _lcm(c.denominator, eco["yden"])
    f_c = M // c.denominator
    f_y = M // eco["yden"]
    Y = eco["y"][idx]
    total = 0
    base = c.numerator * f_c
    for v in Y.tolist():
        dd = base - v * f_y
        total += dd * dd
    return Q(total, M * M)


def arms_V02(eco, sl, chosen_eval):
    Yf = eco["y"][sl["fit"]]
    const = Q(int(Yf.sum()), int(len(Yf)) * eco["yden"])
    const_sse = const_int_sse(eco, sl["held"], const)
    pos = int((Yf > 0).sum())
    maj = 1 if pos * 2 > len(Yf) else 0
    Yh = eco["y"][sl["held"]]
    maj_err = int(((Yh > 0).astype(np.int64) != maj).sum())
    pa_f, ba_f, _, route = fit_on(eco, sl["fit"], AFFINE_BODY, AFFINE_HEAD, False, ITERS["final"])
    pa = [rationalise(v) for v in pa_f]
    ba = rationalise(ba_f)
    return {"best_constant": {"value": qstr(const), "n": int(len(sl["held"])),
                              "held_sse": qstr(const_sse), "exact_fit_mean": True},
            "majority_label": {"predict": maj, "n": int(len(sl["held"])),
                               "held_decision_errors": maj_err,
                               "fit_positive_fraction_num": pos, "fit_rows": int(len(Yf))},
            "affine_arm": {"body": G.show(AFFINE_BODY), "head": G.show(AFFINE_HEAD),
                           "params": [qstr(p) for p in pa], "bias": qstr(ba),
                           "intercept_nonzero": bool(ba != 0), "fit_route": route},
            "chosen": {"held_sse": chosen_eval["sse"],
                       "held_decision_errors": chosen_eval["decision_errors"]}}


def poisson_irls(X, y, iters=50, ridge=1e-8):
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


def arms_V03(eco, sl, rec):
    mu_chosen = rec.pop("_mu_chosen")
    ys = rec.pop("_ys")
    Xf, yf = design(eco, sl["fit"])
    bp = poisson_irls(Xf, yf)
    bg = ols(Xf, yf)
    Xh, yh = design(eco, sl["held"])
    Zh = np.concatenate([Xh, np.ones((Xh.shape[0], 1))], axis=1)
    mu_log = [rationalise(v) for v in np.exp(np.clip(Zh.dot(bp), -30, 30))]
    mu_id = [rationalise(v) for v in Zh.dot(bg)]
    Yf = eco["y"][sl["fit"]]
    const = Q(int(Yf.sum()), int(len(Yf)) * eco["yden"])
    mu_const = [const] * len(ys)
    k = min(VERIFY_ROWS, len(ys))
    t0 = time.time()
    out = {
        "intercept_only": {"mu": qstr(const), "n": len(ys), "exact_fit_mean": True,
                           "deviance_interval": CERT.deviance_interval(ys, mu_const)},
        "log_link": {"n": len(ys), "nonpositive_means": CERT.nonpositive_count(mu_log),
                     "beta_float_diagnostic": [float(v) for v in bp],
                     "deviance_interval": CERT.deviance_interval(ys, mu_log)},
        "identity_link": {"n": len(ys), "nonpositive_means": CERT.nonpositive_count(mu_id),
                          "beta_float_diagnostic": [float(v) for v in bg],
                          "deviance_interval": CERT.deviance_interval(ys, mu_id)},
        "chosen": {"n": len(ys), "nonpositive_means": CERT.nonpositive_count(mu_chosen)},
        "comparisons": {
            "chosen_minus_intercept_only": CERT.deviance_difference(ys, mu_chosen, mu_const),
            "log_link_minus_intercept_only": CERT.deviance_difference(ys, mu_log, mu_const),
            "chosen_minus_log_link": CERT.deviance_difference(ys, mu_chosen, mu_log),
            "identity_minus_intercept_only": CERT.deviance_difference(ys, mu_id, mu_const)},
        "replay": {"rows": k, "slot": "held_prefix",
                   "mu_log": [qstr(v) for v in mu_log[:k]],
                   "mu_identity": [qstr(v) for v in mu_id[:k]],
                   "mu_intercept_only": qstr(const),
                   "y": [int(v) for v in eco["y"][sl["held"]][:k]],
                   "partial_chosen_minus_intercept_only":
                       CERT.deviance_difference(ys[:k], mu_chosen[:k], mu_const[:k]),
                   "partial_chosen_minus_log_link":
                       CERT.deviance_difference(ys[:k], mu_chosen[:k], mu_log[:k]),
                   "partial_identity_nonpositive_means": CERT.nonpositive_count(mu_id[:k]),
                   "partial_chosen_nonpositive_means": CERT.nonpositive_count(mu_chosen[:k])},
    }
    print("[V03] arms certified in %.1fs: chosen-vs-const %s log-vs-const %s chosen-vs-log %s identity nonpos %d"
          % (time.time() - t0, out["comparisons"]["chosen_minus_intercept_only"]["status"] + str(out["comparisons"]["chosen_minus_intercept_only"].get("sign")),
             out["comparisons"]["log_link_minus_intercept_only"]["status"] + str(out["comparisons"]["log_link_minus_intercept_only"].get("sign")),
             out["comparisons"]["chosen_minus_log_link"]["status"] + str(out["comparisons"]["chosen_minus_log_link"].get("sign")),
             out["identity_link"]["nonpositive_means"]), flush=True)
    return out


# -------------------------------------------------------------- controls ----

def controls_V02(eco, sl, body, head, stateful, chosen_sse):
    """FREEZE_V1.md section 12 V2d: response-permutation controls with the
    applicability band. When the chosen program is jointly affine in its
    parameters the normal-equations matrix is formed once; control 0 is also
    refitted through the generic routine and asserted equal."""
    Xf, yf = design(eco, sl["fit"])
    d = eco["d"]
    plan_f = SPlan(body, Xf)
    base, Z = joint_affine(plan_f, head, stateful, d)
    fast = Z is not None
    if fast:
        A = Z.T.dot(Z) + 1e-8 * np.eye(d + 1)
    Yf = eco["y"][sl["fit"]]
    const = Q(int(Yf.sum()), int(len(Yf)) * eco["yden"])
    const_sse = const_int_sse(eco, sl["held"], const)
    lo = Q(9, 10) * const_sse
    hi = Q(11, 10) * const_sse
    rs = np.random.RandomState(SEED)
    in_band = 0
    beat_chosen = 0
    ratios = []
    t0 = time.time()
    coeffs = head_affine_coefficients(head) if not stateful else None
    for k in range(N_CONTROLS):
        perm = rs.permutation(yf.shape[0])
        yp = yf[perm]
        if fast:
            v = np.linalg.solve(A, Z.T.dot(yp - base))
            pv, bv = v[:d], float(v[d])
            if k == 0:
                pg, bg, Lg, route = fit_plan(plan_f, head, stateful, yp, d, "squared", ITERS["final"])
                got = predict_plan(plan_f, head, stateful, pv, bv)
                want = predict_plan(plan_f, head, stateful, pg, bg)
                if not np.allclose(got, want, rtol=1e-6, atol=1e-8 * max(1.0, float(np.abs(want).max()))):
                    raise SystemExit("CONTROL FAST PATH DISAGREES WITH fit_plan")
        else:
            pv, bv, _, _ = fit_plan(plan_f, head, stateful, yp, d, "squared", ITERS["rank"])
        pq = [rationalise(x) for x in pv]
        bq = rationalise(bv)
        s = None
        if (coeffs is not None and coeffs[0] == 1 and coeffs[2] == 0
                and G.meaning(body, G.body_grid()) == G.meaning(AFFINE_BODY, G.body_grid())):
            s = mixed_int_sse(eco, sl["held"], pq, coeffs[1] * bq)
        if s is None:
            s = Q(exact_evaluate_squared(eco, sl["held"], body, head, stateful, pq, bq)["sse"])
        if lo <= s <= hi:
            in_band += 1
        if s < chosen_sse:
            beat_chosen += 1
        ratios.append(s / const_sse)
        if k % 50 == 0:
            print("  control %d/%d ratio=%.6f in_band=%d (%.1fs)"
                  % (k, N_CONTROLS, float(s / const_sse), in_band, time.time() - t0), flush=True)
    ratios.sort()
    return {"controls": N_CONTROLS, "seed": SEED, "constant_sse": qstr(const_sse),
            "chosen_arm_held_sse": qstr(chosen_sse),
            "chosen_over_constant_parts_per_billion": int(chosen_sse / const_sse * 10 ** 9),
            "band_low": qstr(lo), "band_high": qstr(hi), "in_band": in_band,
            "applicable": bool(in_band == N_CONTROLS),
            "controls_beating_the_chosen_arm": beat_chosen,
            "chosen_below_band": bool(chosen_sse < lo),
            "ratio_min": qstr(ratios[0]), "ratio_median": qstr(ratios[len(ratios) // 2]),
            "ratio_max": qstr(ratios[-1]),
            "ratio_min_float_diagnostic": float(ratios[0]),
            "ratio_max_float_diagnostic": float(ratios[-1]),
            "fast_path": fast}


def run_control(key, eco):
    """A matched negative control: the full search, the class it recovers."""
    n = len(eco["y"])
    sl = slices(n)
    pairs, bq, hq, meta = build_candidates()
    ranked, scored, budget, orank, parts = run_search(pairs, eco, sl["search"], key)
    w = ranked[0]
    body, head = parse_tree(w["body"]), parse_tree(w["head"])
    attrs = G.classify(body, head)
    rec = {"control": key, "role": CONTROLS[key], "ecology": eco["name"], "loss": eco["loss"],
           "n_rows": int(n), "n_search": int(len(sl["search"])),
           "grammar": meta, "xden": list(eco["xden"]), "yden": int(eco["yden"]),
           "chosen": {"body": w["body"], "head": w["head"], "class": attrs["class"],
                      "attributes": attrs, "search_loss": w["loss"]},
           "search": {"ranked_top10": ranked[:10], "screen_enumerated": len(scored),
                      "screen_inadmissible": sum(1 for s in scored if s[0])},
           "search_budget": budget}
    if "response" in eco:
        rec["response"] = eco["response"]
    print("[%s] control class=%s (%s | %s)" % (key, attrs["class"], w["body"], w["head"]), flush=True)
    return rec


# ------------------------------------------------------------------ main ----

def main():
    quick = "--quick" in sys.argv
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1].split(",")
    os.makedirs(RUNS, exist_ok=True)
    pcm, texts, sources = load_sources()
    if quick:
        texts = texts[:60]
        pcm = pcm[:120000]
    with open(os.path.join(RUNS, "sources.json"), "w") as fh:
        json.dump(sources, fh, indent=1, sort_keys=True)
    print("sources verified: D2 %d frames, D3 %d files" % (sources["D2"]["frames"], sources["D3"]["files"]), flush=True)
    lines = d3_lines(texts)
    ecos = {"V02": lambda: ecology_V02(lines), "V03": lambda: ecology_V03(texts),
            "T02": lambda: ecology_T02(pcm), "T03": lambda: ecology_T03(lines)}
    todo = only or ["V02", "V03", "T02", "T03"]
    for key in todo:
        eco = ecos[key]()
        if key in SCOPES:
            rec, sl, body, head, attrs, params, bias = run_scope(key, eco, SCOPES[key])
            if key == "V02":
                rec["arms"] = arms_V02(eco, sl, rec["chosen"]["held_out"])
                if "--controls" in sys.argv:
                    c = controls_V02(eco, sl, body, head, attrs["reads_state"],
                                     Q(rec["chosen"]["held_out"]["sse"]))
                    with open(os.path.join(RUNS, "controls_V02.json"), "w") as fh:
                        json.dump(c, fh, indent=1, sort_keys=True)
                    print("controls: in_band=%d/%d applicable=%s beating=%d"
                          % (c["in_band"], c["controls"], c["applicable"],
                             c["controls_beating_the_chosen_arm"]), flush=True)
            else:
                rec["arms"] = arms_V03(eco, sl, rec)
            with open(os.path.join(RUNS, "scope_%s.json" % key), "w") as fh:
                json.dump(rec, fh, indent=1, sort_keys=True)
        else:
            rec = run_control(key, eco)
            with open(os.path.join(RUNS, "control_%s.json" % key), "w") as fh:
                json.dump(rec, fh, indent=1, sort_keys=True)
        print("[%s] written" % key, flush=True)
    print("done", flush=True)


if __name__ == "__main__":
    main()

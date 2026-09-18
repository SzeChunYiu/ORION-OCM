"""Stage 1: real-data search, fitting and exact evaluation. laptop-billy only.

Reads D1-D3 (sha256-verified), builds E_H01..E_H04 exactly as
FREEZE_V1_ECOLOGY_ADDENDUM.md sections A1-A4 specify, runs the family-blind
search of A8, fits every registered arm at real scale, and writes REAL_RUNS/.

numpy is used ONLY inside fitting and search. Every emitted number is an exact
integer or an exact rational written as "num/den". Stage 2
(real_scale_classical_v1.py) is stdlib-only and recomputes the exact arithmetic
from the committed verification slices.
"""
from __future__ import print_function
from fractions import Fraction as F
import glob
import hashlib
import json
import os
import struct
import sys
import time
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grammar_v1 as G  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "REAL_RUNS")

D1_PATH = "/usr/share/dict/words"
D1_SHA = "f6c94d35691b9c356f7e5072f94d23f127b168cf9b04f0f5b26e0cb1f6ef4414"
D2_GLOB = "/usr/share/sounds/alsa/*.wav"
D2_DOD = "a9f677295dcb2d102bb43b86cbad70babe208c1a5fd38a2ae4d8a05f7fdb7a7a"
D3_GLOB = "/usr/lib/python3.8/**/*.py"
D3_DOD = "41607de5c1577303abc83cccfd29e5d12e6c180689d9fc3d98eac3f97dec9ec9"

RAT_DEN = 10 ** 9          # FREEZE_V1.md section 6
KERNEL_DEN = 2 ** 30       # registered dyadic rounding of the landmark kernel
N_SCREEN = 600
N_SEARCH = 20000
KEEP = 40
SWEEPS = 6


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def dod(paths):
    h = hashlib.sha256()
    per = []
    for p in paths:
        d = sha(p)
        per.append({"path": p, "sha256": d, "bytes": os.path.getsize(p)})
        h.update(d.encode())
    return h.hexdigest(), per


# ------------------------------------------------------------- sources -------

def load_sources(negative_control=False):
    src = {}
    p1 = D1_PATH + ("X" if negative_control else "")
    d1 = sha(p1)
    if d1 != D1_SHA:
        raise SystemExit("D1 digest mismatch: %s" % d1)
    src["D1"] = {"path": D1_PATH, "sha256": d1, "bytes": os.path.getsize(p1)}
    with open(p1, "rb") as f:
        d1bytes = f.read()

    wavs = sorted(glob.glob(D2_GLOB))
    d2, per2 = dod(wavs)
    if d2 != D2_DOD:
        raise SystemExit("D2 digest-of-digests mismatch: %s" % d2)
    src["D2"] = {"digest_of_digests": d2, "files": per2}
    pcm = []
    for p in wavs:
        w = wave.open(p, "rb")
        assert w.getnchannels() == 1 and w.getsampwidth() == 2
        raw = w.readframes(w.getnframes())
        pcm.extend(struct.unpack("<%dh" % (len(raw) // 2), raw))
        w.close()
    pcm = np.asarray(pcm, dtype=np.int64)

    pys = sorted(glob.glob(D3_GLOB, recursive=True))
    d3, per3 = dod(pys)
    if d3 != D3_DOD:
        raise SystemExit("D3 digest-of-digests mismatch: %s" % d3)
    src["D3"] = {"digest_of_digests": d3, "n_files": len(pys),
                 "bytes": sum(x["bytes"] for x in per3)}
    lines = []
    for p in pys:
        with open(p, "rb") as f:
            t = f.read().decode("latin-1")
        for ln in t.split("\n"):
            if len(ln) >= 1:
                lines.append(ln)
    return src, d1bytes, pcm, lines, per3


# ----------------------------------------------------------- ecologies -------

SEP = 26


def ecology_H01(d1bytes):
    sym = np.full(len(d1bytes), SEP, dtype=np.int64)
    b = np.frombuffer(d1bytes, dtype=np.uint8).astype(np.int64)
    lo = (b >= 97) & (b <= 122)
    up = (b >= 65) & (b <= 90)
    sym[lo] = b[lo] - 97
    sym[up] = b[up] - 65
    x = sym[:-1]
    y = (sym[1:] == SEP).astype(np.int64)
    return {"kind": "onehot", "sym": x, "y": y, "d": 27, "xden": 1, "yden": 1,
            "loss": "decision"}


def ecology_H02(pcm):
    d = 32
    n = len(pcm) - d
    idx = np.arange(n)[:, None] + np.arange(d)[None, :]
    return {"kind": "dense", "Xi": pcm[idx], "yi": pcm[d:], "d": d,
            "xden": 32768, "yden": 32768, "loss": "squared"}


def ecology_H04(pcm):
    d = 32
    W = 32
    n = len(pcm) - d - W + 1
    idx = np.arange(n)[:, None] + np.arange(d)[None, :]
    X = pcm[idx]
    e = pcm.astype(np.int64) ** 2
    cs = np.concatenate([[0], np.cumsum(e)])
    ysum = cs[d + W:d + W + n] - cs[d:d + n]
    return {"kind": "dense", "Xi": X, "yi": ysum, "d": d,
            "xden": 32768, "yden": W * 32768 * 32768, "loss": "squared"}


H03_COLS = ("len", "lead", "alpha", "space", "usc", "eq", "paren",
            "brack", "comma", "dot", "quote", "hash")
H03_DEN = (64, 16, 64, 64, 8, 4, 8, 8, 8, 8, 8, 4)


def ecology_H03(lines):
    rows = np.zeros((len(lines), 12), dtype=np.int64)
    ys = np.zeros(len(lines), dtype=np.int64)
    for i, ln in enumerate(lines):
        c = [0] * 12
        c[0] = len(ln)
        j = 0
        while j < len(ln) and ln[j] == " ":
            j += 1
        c[1] = j
        nd = 0
        for ch in ln:
            if "0" <= ch <= "9":
                nd += 1
            elif ch.isalpha():
                c[2] += 1
            elif ch == " ":
                c[3] += 1
            elif ch == "_":
                c[4] += 1
            elif ch == "=":
                c[5] += 1
            elif ch in "()":
                c[6] += 1
            elif ch in "[]":
                c[7] += 1
            elif ch == ",":
                c[8] += 1
            elif ch == ".":
                c[9] += 1
            elif ch in "\"'":
                c[10] += 1
            elif ch == "#":
                c[11] += 1
        rows[i] = c
        ys[i] = nd
    return {"kind": "scaled", "Xi": rows, "yi": ys, "d": 12,
            "xden": H03_DEN, "yden": 1, "loss": "squared", "raw_lines": None}


def slices(n):
    """FREEZE_V1.md section 4 slice rule + addendum A7 contiguous tail."""
    i = np.arange(n)
    m = i % 5
    search = i[m == 3]
    held = i[m == 4]
    fit = i[(m != 3) & (m != 4)]
    remint_fit = i[m == 0]
    half = n // 2
    remint_held = i[(m == 2) & (i >= half)]
    t0 = int(n * 0.8) + 64
    tail = i[i >= t0]
    fit = fit[fit < int(n * 0.8)]
    return {"fit": fit, "search": search, "held": held, "tail": tail,
            "remint_fit": remint_fit[remint_fit < int(n * 0.8)],
            "remint_held": remint_held}


def design(eco, idx):
    """Float design matrix and response for a row index set."""
    if eco["kind"] == "onehot":
        s = eco["sym"][idx]
        X = np.zeros((len(idx), 27), dtype=np.float64)
        X[np.arange(len(idx)), s] = 1.0
        return X, eco["y"][idx].astype(np.float64)
    if eco["kind"] == "dense":
        return (eco["Xi"][idx].astype(np.float64) / eco["xden"],
                eco["yi"][idx].astype(np.float64) / eco["yden"])
    X = eco["Xi"][idx].astype(np.float64) / np.asarray(eco["xden"], dtype=np.float64)
    return X, eco["yi"][idx].astype(np.float64)


# ------------------------------------------------- numpy codegen + eval ------

np.seterr(all="ignore")


def _np_rec(x):
    x = np.asarray(x, dtype=np.float64)
    return np.where(x != 0.0, 1.0 / np.where(x == 0.0, 1.0, x), 0.0)


def _np_step(x):
    return (np.asarray(x, dtype=np.float64) > 0.0).astype(np.float64)


def codegen_np(e):
    h = e[0]
    if h == "L":
        n = e[1]
        return {"C0": "_z", "C1": "_o"}.get(n, n.lower())
    if h == "NEG":
        return "(-(%s))" % codegen_np(e[1])
    if h == "ABS":
        return "(np.abs(%s))" % codegen_np(e[1])
    if h == "STEP":
        return "(_np_step(%s))" % codegen_np(e[1])
    if h == "RECIP":
        return "(_np_rec(%s))" % codegen_np(e[1])
    if h == "ADD":
        return "((%s)+(%s))" % (codegen_np(e[1]), codegen_np(e[2]))
    return "((%s)*(%s))" % (codegen_np(e[1]), codegen_np(e[2]))


_ENV = {"np": np, "_np_rec": _np_rec, "_np_step": _np_step}


def body_fn(body):
    src = "lambda arg, param, _z, _o: " + codegen_np(body)
    return eval(src, dict(_ENV))


def head_fn_np(head):
    src = "lambda s, bias, state, _z, _o: " + codegen_np(head)
    return eval(src, dict(_ENV))


def _rec(x):
    return 0.0 if x == 0.0 else 1.0 / x


def head_fn_scalar(head):
    src = "lambda s, bias, state: " + G.codegen(head)
    return eval(src, {"_rec": _rec, "abs": abs})


def predict(bf, hf_np, hf_s, reads_state, X, params, bias):
    z = np.zeros(X.shape[0])
    o = np.ones(X.shape[0])
    vals = bf(X, params[None, :], np.zeros_like(X), np.ones_like(X))
    vals = np.broadcast_to(np.asarray(vals, dtype=np.float64), X.shape)
    S = np.sum(vals, axis=1)
    if not reads_state:
        r = hf_np(S, bias, 0.0, z, o)
        return np.broadcast_to(np.asarray(r, dtype=np.float64), S.shape)
    out = np.empty(X.shape[0])
    st = 0.0
    f = hf_s
    for i in range(X.shape[0]):
        v = f(S[i], bias, st)
        out[i] = v
        st = v
    return out


def loss_of(kind, out, y):
    out = np.broadcast_to(np.asarray(out, dtype=np.float64), y.shape)
    if not np.all(np.isfinite(out)):
        return float("inf")
    if kind == "decision":
        return float(np.mean((out > 0.0).astype(np.float64) != y))
    r = out - y
    return float(np.mean(r * r))


# --------------------------------------------------------- generic fitting ---

def affine_in_params(bf, hf_np, hf_s, reads_state, X, d):
    """Probe whether the prediction is affine in (params, bias)."""
    z = np.zeros(min(64, X.shape[0]))
    Xs = X[:len(z)]
    base = predict(bf, hf_np, hf_s, reads_state, Xs, np.zeros(d), 0.0)
    cols = []
    for j in range(d):
        p = np.zeros(d)
        p[j] = 1.0
        cols.append(predict(bf, hf_np, hf_s, reads_state, Xs, p, 0.0) - base)
    cols.append(predict(bf, hf_np, hf_s, reads_state, Xs, np.zeros(d), 1.0) - base)
    Z = np.stack(cols, axis=1)
    rs = np.random.RandomState(20260918)
    for _ in range(3):
        v = rs.randint(-3, 4, size=d + 1).astype(np.float64)
        got = predict(bf, hf_np, hf_s, reads_state, Xs, v[:d], v[d])
        want = base + Z.dot(v)
        if not np.allclose(got, want, rtol=1e-9, atol=1e-9):
            return None
    return True


def lsq_fit(bf, hf_np, hf_s, reads_state, X, y, d, ridge=1e-8):
    base = predict(bf, hf_np, hf_s, reads_state, X, np.zeros(d), 0.0)
    cols = []
    for j in range(d):
        p = np.zeros(d)
        p[j] = 1.0
        cols.append(predict(bf, hf_np, hf_s, reads_state, X, p, 0.0) - base)
    cols.append(predict(bf, hf_np, hf_s, reads_state, X, np.zeros(d), 1.0) - base)
    Z = np.stack(cols, axis=1)
    A = Z.T.dot(Z) + ridge * np.eye(d + 1)
    b = Z.T.dot(y - base)
    try:
        v = np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        v = np.linalg.lstsq(Z, y - base, rcond=None)[0]
    return v[:d], float(v[d])


def cd_fit(bf, hf_np, hf_s, reads_state, X, y, d, kind, p0=None, b0=0.0,
           sweeps=SWEEPS):
    """Generic coordinate descent, step halved each sweep. No family info."""
    p = np.zeros(d) if p0 is None else np.array(p0, dtype=np.float64)
    bias = float(b0)
    best = loss_of(kind, predict(bf, hf_np, hf_s, reads_state, X, p, bias), y)
    step = 1.0
    for _ in range(sweeps):
        for j in range(d + 1):
            cur = p[j] if j < d else bias
            for k in (-4, -3, -2, -1, 1, 2, 3, 4):
                v = cur + k * step
                if j < d:
                    p[j] = v
                else:
                    bias = v
                L = loss_of(kind, predict(bf, hf_np, hf_s, reads_state, X, p, bias), y)
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


def generic_fit(body, head, reads_state, X, y, d, kind):
    bf = body_fn(body)
    hn = head_fn_np(head)
    hs = head_fn_scalar(head)
    if affine_in_params(bf, hn, hs, reads_state, X, d):
        p, b = lsq_fit(bf, hn, hs, reads_state, X, y, d)
        if kind == "decision":
            p, b, L = cd_fit(bf, hn, hs, reads_state, X, y, d, kind, p, b, 4)
        else:
            L = loss_of(kind, predict(bf, hn, hs, reads_state, X, p, b), y)
        return p, b, L, "LEAST_SQUARES"
    p, b, L = cd_fit(bf, hn, hs, reads_state, X, y, d, kind)
    return p, b, L, "COORDINATE_DESCENT"


# ------------------------------------------------------- exact arithmetic ----

def rat(x, den=RAT_DEN):
    """Rationalise a float at the registered precision. Output is data."""
    return F(int(round(float(x) * den)), den)


def exact_rows(eco, idx):
    """Exact Fraction rows for an index set."""
    if eco["kind"] == "onehot":
        return None, [F(int(v)) for v in eco["y"][idx]]
    if eco["kind"] == "dense":
        q = eco["xden"]
        Xs = eco["Xi"][idx]
        rows = [[F(int(v), q) for v in r] for r in Xs]
        ys = [F(int(v), eco["yden"]) for v in eco["yi"][idx]]
        return rows, ys
    dens = eco["xden"]
    Xs = eco["Xi"][idx]
    rows = [[F(int(v), dens[j]) for j, v in enumerate(r)] for r in Xs]
    ys = [F(int(v)) for v in eco["yi"][idx]]
    return rows, ys


def exact_predict(body, head, reads_state, rows, params, bias, syms=None, d=None):
    """Exact prediction sequence. Fractions only."""
    out = []
    st = F(0)
    if syms is not None:
        for t in range(len(syms)):
            s = G.ev(body, {"ARG": F(1), "PARAM": params[int(syms[t])]})
            zero = G.ev(body, {"ARG": F(0), "PARAM": F(0)})
            tot = s
            for j in range(d):
                if j != int(syms[t]):
                    tot += G.ev(body, {"ARG": F(0), "PARAM": params[j]})
            v = G.ev(head, {"S": tot, "BIAS": bias, "STATE": st})
            out.append(v)
            st = v
        return out
    for r in rows:
        tot = F(0)
        for j, xv in enumerate(r):
            tot += G.ev(body, {"ARG": xv, "PARAM": params[j]})
        v = G.ev(head, {"S": tot, "BIAS": bias, "STATE": st})
        out.append(v)
        if reads_state:
            st = v
    return out


def fs(x):
    return "%d/%d" % (x.numerator, x.denominator)


# -------------------------------------------------------------- search -------

def build_candidates():
    braw = G.enumerate_exprs(G.BODY_MAX_NODES, G.BODY_LEAVES)
    hraw = G.enumerate_exprs(G.HEAD_MAX_NODES, G.HEAD_LEAVES)
    bq, _, nbr, nbc = G.quotient(braw, G.body_probe_points())
    hq, _, nhr, nhc = G.quotient(hraw, G.head_probe_points())
    pairs = [(b, h) for b in bq for h in hq]
    meta = {"body_raw": nbr, "body_classes": nbc, "head_raw": nhr,
            "head_classes": nhc, "pairs": len(pairs),
            "grammar_digest": G.grammar_digest()}
    return pairs, meta


def screen(pairs, X, y, kind, d):
    """Generic-fit screen (FREEZE_V1_SEARCH_AMENDMENT.md): every enumerated pair
    is fitted by the same generic routine as step 4, at reduced rows/sweeps."""
    scored = []
    for (b, h) in pairs:
        rs = G._depends_on(h, "STATE", None, ["S", "BIAS"])
        bf, hn, hs = body_fn(b), head_fn_np(h), head_fn_scalar(h)
        try:
            if affine_in_params(bf, hn, hs, rs, X, d):
                p, bi = lsq_fit(bf, hn, hs, rs, X, y, d)
                if kind == "decision":
                    p, bi, L = cd_fit(bf, hn, hs, rs, X, y, d, kind, p, bi, 2)
                else:
                    L = loss_of(kind, predict(bf, hn, hs, rs, X, p, bi), y)
            else:
                p, bi, L = cd_fit(bf, hn, hs, rs, X, y, d, kind, None, 0.0, 2)
        except (FloatingPointError, ValueError, np.linalg.LinAlgError):
            continue
        if not np.isfinite(L):
            continue
        scored.append((L, G.size(b), G.render(b), G.render(h), b, h, rs))
    scored.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
    return scored


def run_search(pairs, eco, sl, tag):
    d = eco["d"]
    kind = eco["loss"]
    si = sl["search"]
    Xs, ys = design(eco, si[:N_SCREEN])
    t0 = time.time()
    scored = screen(pairs, Xs, ys, kind, d)
    kept = scored[:KEEP]
    Xf, yf = design(eco, si[:N_SEARCH])
    ranked = []
    for (_, _, br, hr, b, h, rs) in kept:
        p, bi, L, how = generic_fit(b, h, rs, Xf, yf, d, kind)
        ranked.append({"loss": L, "body": br, "head": hr, "nodes": G.size(b) + G.size(h),
                       "reads_state": bool(rs), "fit": how})
    ranked.sort(key=lambda r: (r["loss"], r["nodes"], r["body"], r["head"]))
    print("[%s] screen %d -> %d, search done in %.1fs; winner %s | %s loss=%.6g"
          % (tag, len(scored), len(kept), time.time() - t0,
             ranked[0]["body"], ranked[0]["head"], ranked[0]["loss"]))
    return ranked, scored


def parse_expr(s):
    """Parse a rendered expression back to a tree (independent of enumeration)."""
    pos = [0]

    def p():
        i = pos[0]
        j = i
        while j < len(s) and s[j] not in "(),":
            j += 1
        name = s[i:j]
        pos[0] = j
        if pos[0] < len(s) and s[pos[0]] == "(":
            pos[0] += 1
            args = [p()]
            while s[pos[0]] == ",":
                pos[0] += 1
                args.append(p())
            pos[0] += 1
            return tuple([name] + args)
        return ("L", name)
    return p()


# ---------------------------------------------------------------- arms -------

AFFINE_BODY = ("MUL", ("L", "ARG"), ("L", "PARAM"))
AFFINE_HEAD = ("ADD", ("L", "S"), ("L", "BIAS"))


def fit_arm(body, head, reads_state, eco, idx, kind):
    X, y = design(eco, idx)
    p, b, L, how = generic_fit(body, head, reads_state, X, y, eco["d"], kind)
    return [rat(v) for v in p], rat(b), how


def exact_eval(body, head, reads_state, eco, idx, params, bias):
    rows, ys = exact_rows(eco, idx)
    syms = eco["sym"][idx] if eco["kind"] == "onehot" else None
    out = exact_predict(body, head, reads_state, rows, params, bias,
                        syms=syms, d=eco["d"])
    return out, ys


def sse(out, ys):
    t = F(0)
    for o, y in zip(out, ys):
        r = o - y
        t += r * r
    return t


def dec_err(out, ys):
    n = 0
    for o, y in zip(out, ys):
        if (F(1) if o > 0 else F(0)) != y:
            n += 1
    return n


def poisson_irls(X, y, iters=25, ridge=1e-8):
    n, d = X.shape
    Z = np.concatenate([X, np.ones((n, 1))], axis=1)
    beta = np.zeros(d + 1)
    beta[d] = np.log(max(y.mean(), 1e-3))
    for _ in range(iters):
        eta = np.clip(Z.dot(beta), -20.0, 20.0)
        mu = np.exp(eta)
        w = np.maximum(mu, 1e-8)
        z = eta + (y - mu) / w
        A = (Z * w[:, None]).T.dot(Z) + ridge * np.eye(d + 1)
        bnew = np.linalg.solve(A, (Z * w[:, None]).T.dot(z))
        if not np.all(np.isfinite(bnew)):
            break
        if np.max(np.abs(bnew - beta)) < 1e-10:
            beta = bnew
            break
        beta = bnew
    return beta


def ols(X, y, ridge=1e-8):
    n, d = X.shape
    Z = np.concatenate([X, np.ones((n, 1))], axis=1)
    A = Z.T.dot(Z) + ridge * np.eye(d + 1)
    return np.linalg.solve(A, Z.T.dot(y))


def apply_lin(X, beta, link):
    Z = np.concatenate([X, np.ones((X.shape[0], 1))], axis=1)
    eta = Z.dot(beta)
    if link == "log":
        return np.exp(np.clip(eta, -20.0, 20.0))
    return eta


def kernel_design(X, L):
    """k(x,z) = RECIP(C1 + sum_i (x_i - z_i)^2), rationalised at KERNEL_DEN."""
    d2 = ((X[:, None, :] - L[None, :, :]) ** 2).sum(axis=2)
    K = 1.0 / (1.0 + d2)
    return np.round(K * KERNEL_DEN) / KERNEL_DEN


def basis2(X):
    n, d = X.shape
    cols = [X]
    for i in range(d):
        cols.append(X[:, i:i + 1] * X[:, i:])
    return np.concatenate(cols, axis=1)


def exact_sse_from_pred(pred_rat, ys):
    t = F(0)
    for p, y in zip(pred_rat, ys):
        r = p - y
        t += r * r
    return t


# ------------------------------------------------------- route B search ------

def search_route_b(kept, eco, sl):
    """Second, independently parameterised optimiser over the same survivors.

    Random multistart instead of coordinate descent. Same loss, same rows.
    Agreement of the argmin is the decisive-step independence check.
    """
    d = eco["d"]
    kind = eco["loss"]
    X, y = design(eco, sl["search"][:N_SEARCH])
    rs = np.random.RandomState(833833)
    out = []
    for (_, _, br, hr, b, h, st) in kept:
        bf, hn, hsc = body_fn(b), head_fn_np(h), head_fn_scalar(h)
        best = None
        for _ in range(60):
            p = rs.randint(-4, 5, size=d).astype(np.float64) * 0.5
            bi = float(rs.randint(-4, 5)) * 0.5
            try:
                L = loss_of(kind, predict(bf, hn, hsc, st, X, p, bi), y)
            except (FloatingPointError, ValueError):
                continue
            if np.isfinite(L) and (best is None or L < best):
                best = L
                bp, bb = p.copy(), bi
        if best is None:
            continue
        p, bi, L = cd_fit(bf, hn, hsc, st, X, y, d, kind, bp, bb, 4)
        out.append({"loss": L, "body": br, "head": hr,
                    "nodes": G.size(b) + G.size(h)})
    out.sort(key=lambda r: (r["loss"], r["nodes"], r["body"], r["head"]))
    return out


# ------------------------------------------------------------- driver --------

def nondegenerate(out, ys, kind):
    vals = set()
    for o in out[:20000]:
        vals.add(o)
    info = {"distinct_predictions": len(vals),
            "distinct_responses": len(set(ys[:20000]))}
    if kind == "decision":
        pos = sum(1 for o in out if o > 0)
        info["predicted_positive"] = pos
        info["predicted_negative"] = len(out) - pos
        info["both_classes_predicted"] = bool(0 < pos < len(out))
    info["non_degenerate"] = bool(info["distinct_predictions"] > 1
                                  and info["distinct_responses"] > 1)
    return info


def run_scope(name, eco, verify_rows):
    n = len(eco["yi"]) if eco["kind"] != "onehot" else len(eco["y"])
    sl = slices(n)
    pairs, meta = build_candidates()
    rec = {"scope": name, "n_rows": int(n), "grammar": meta,
           "n_fit": int(len(sl["fit"])), "n_held": int(len(sl["held"])),
           "n_tail": int(len(sl["tail"])), "n_search": int(len(sl["search"]))}
    ranked, scored = run_search(pairs, eco, sl, name)
    kept = scored[:KEEP]
    rb = search_route_b(kept, eco, sl)
    w = ranked[0]
    b, h = parse_expr(w["body"]), parse_expr(w["head"])
    cls = G.classify(b, h)
    rec["winner"] = {"body": w["body"], "head": w["head"], "class": cls["class"],
                     "attributes": cls, "search_loss": w["loss"],
                     "fit_route": w["fit"]}
    rec["search"] = {"ranked_top10": ranked[:10],
                     "route_b_top10": rb[:10],
                     "route_b_agrees": bool(rb and rb[0]["body"] == w["body"]
                                            and rb[0]["head"] == w["head"]),
                     "screen_top20": [{"loss": s[0], "body": s[2], "head": s[3]}
                                      for s in scored[:20]]}
    print("[%s] class=%s routeB_agrees=%s" % (name, cls["class"],
                                              rec["search"]["route_b_agrees"]))

    params, bias, how = fit_arm(b, h, cls["reads_state"], eco, sl["fit"], eco["loss"])
    rec["winner"]["fit_rows"] = int(len(sl["fit"]))
    rec["winner"]["params"] = [fs(p) for p in params]
    rec["winner"]["bias"] = fs(bias)
    rec["winner"]["full_fit_route"] = how

    ev = {}
    for slot in ("held", "tail"):
        idx = sl[slot]
        out, ys = exact_eval(b, h, cls["reads_state"], eco, idx, params, bias)
        e = {"n": len(idx)}
        if eco["loss"] == "decision":
            e["errors"] = dec_err(out, ys)
        else:
            e["sse"] = fs(sse(out, ys))
        e["nondegeneracy"] = nondegenerate(out, ys, eco["loss"])
        ev[slot] = e
        print("[%s] %s %s" % (name, slot, {k: v for k, v in e.items()
                                           if k != "nondegeneracy"}))
    rec["winner"]["evaluation"] = ev

    # remint: independent re-derivation on the disjoint remint slices
    sl2 = {"search": sl["remint_fit"], "fit": sl["remint_fit"],
           "held": sl["remint_held"], "tail": sl["tail"]}
    ranked2, _ = run_search(pairs, eco, sl2, name + "/remint")
    w2 = ranked2[0]
    b2, h2 = parse_expr(w2["body"]), parse_expr(w2["head"])
    cls2 = G.classify(b2, h2)
    rec["remint"] = {"body": w2["body"], "head": w2["head"],
                     "class": cls2["class"],
                     "class_matches": bool(cls2["class"] == cls["class"]),
                     "expression_matches": bool(w2["body"] == w["body"]
                                                and w2["head"] == w["head"]),
                     "n_rows": int(len(sl["remint_fit"]))}
    print("[%s] remint class=%s matches=%s" % (name, cls2["class"],
                                               rec["remint"]["class_matches"]))

    # verification slice for stage 2 / oracle
    vidx = sl["held"][:verify_rows]
    vout, vys = exact_eval(b, h, cls["reads_state"], eco, vidx, params, bias)
    v = {"rows": verify_rows, "slot": "held_prefix"}
    if eco["kind"] == "onehot":
        v["syms"] = [int(x) for x in eco["sym"][vidx]]
        v["y"] = [int(x) for x in eco["y"][vidx]]
    else:
        v["Xi"] = [[int(x) for x in r] for r in eco["Xi"][vidx]]
        v["yi"] = [int(x) for x in eco["yi"][vidx]]
        v["xden"] = (list(eco["xden"]) if isinstance(eco["xden"], tuple)
                     else int(eco["xden"]))
        v["yden"] = int(eco["yden"])
    if eco["loss"] == "decision":
        v["partial_errors"] = dec_err(vout, vys)
    else:
        v["partial_sse"] = fs(sse(vout, vys))
    rec["verification"] = v
    return rec, sl, b, h, cls, params, bias, ev


def arms_H01(eco, sl, ranked, rec):
    stateless = None
    for r in ranked:
        if not r["reads_state"]:
            stateless = r
            break
    b2, h2 = parse_expr(stateless["body"]), parse_expr(stateless["head"])
    p2, bi2, how2 = fit_arm(b2, h2, False, eco, sl["fit"], "decision")
    arms = {"stateless_best": {"body": stateless["body"], "head": stateless["head"],
                               "params": [fs(x) for x in p2], "bias": fs(bi2),
                               "fit_route": how2}}
    for slot in ("held", "tail"):
        out, ys = exact_eval(b2, h2, False, eco, sl[slot], p2, bi2)
        arms["stateless_best"][slot] = {"n": len(sl[slot]), "errors": dec_err(out, ys),
                                        "nondegeneracy": nondegenerate(out, ys, "decision")}
    yfit = eco["y"][sl["fit"]]
    maj = 1 if yfit.mean() > 0.5 else 0
    arms["majority_class"] = {"predict": int(maj)}
    for slot in ("held", "tail"):
        ys = eco["y"][sl[slot]]
        arms["majority_class"][slot] = {"n": int(len(ys)),
                                        "errors": int((ys != maj).sum())}
    return arms


def arms_H02(eco, sl):
    _, yf = design(eco, sl["fit"])
    c = rat(float(yf.mean()))
    arms = {"best_constant": {"value": fs(c)}}
    for slot in ("held", "tail"):
        _, ys = exact_rows(eco, sl[slot])
        arms["best_constant"][slot] = {"n": len(ys),
                                       "sse": fs(exact_sse_from_pred([c] * len(ys), ys))}
    pos = int((yf > 0).sum())
    maj = 1 if pos * 2 > len(yf) else 0
    arms["majority_sign"] = {"predict": maj}
    for slot in ("held", "tail"):
        _, ys = exact_rows(eco, sl[slot])
        err = sum(1 for y in ys if (1 if y > 0 else 0) != maj)
        arms["majority_sign"][slot] = {"n": len(ys), "errors": err}
    return arms


def arms_H03(eco, sl):
    Xf, yf = design(eco, sl["fit"])
    bp = poisson_irls(Xf, yf)
    bg = ols(Xf, yf)
    arms = {"poisson_log": {"beta": [float(v) for v in bp]},
            "gaussian_identity": {"beta": [float(v) for v in bg]}}
    for slot in ("held", "tail"):
        X, y = design(eco, sl[slot])
        mp = [rat(v) for v in apply_lin(X, bp, "log")]
        mg = [rat(v) for v in apply_lin(X, bg, "identity")]
        ys = [F(int(v)) for v in eco["yi"][sl[slot]]]
        pw = gw = tie = 0
        for a, bb, yy in zip(mp, mg, ys):
            da = a - yy
            db = bb - yy
            da = da if da >= 0 else -da
            db = db if db >= 0 else -db
            if da < db:
                pw += 1
            elif db < da:
                gw += 1
            else:
                tie += 1
        arms["poisson_log"][slot] = {
            "n": len(ys), "strict_wins": pw, "negative_means": sum(1 for v in mp if v < 0),
            "sse": fs(exact_sse_from_pred(mp, ys)),
            "distinct_predictions": len(set(mp[:20000]))}
        arms["gaussian_identity"][slot] = {
            "n": len(ys), "strict_wins": gw, "negative_means": sum(1 for v in mg if v < 0),
            "sse": fs(exact_sse_from_pred(mg, ys)),
            "distinct_predictions": len(set(mg[:20000]))}
        arms.setdefault("ties", {})[slot] = tie
    return arms


def arms_H04(eco, sl):
    arms = {}
    p, bi, how = fit_arm(AFFINE_BODY, AFFINE_HEAD, False, eco, sl["fit"], "squared")
    arms["affine"] = {"body": G.render(AFFINE_BODY), "head": G.render(AFFINE_HEAD),
                      "params": [fs(x) for x in p], "bias": fs(bi), "fit_route": how,
                      "cost": G.program_cost(AFFINE_BODY, AFFINE_HEAD, eco["d"], False)}
    for slot in ("held", "tail"):
        out, ys = exact_eval(AFFINE_BODY, AFFINE_HEAD, False, eco, sl[slot], p, bi)
        arms["affine"][slot] = {"n": len(ys), "sse": fs(sse(out, ys)),
                                "nondegeneracy": nondegenerate(out, ys, "squared")}
    Xf, yf = design(eco, sl["fit"])
    d = eco["d"]
    Xh, yh = design(eco, sl["held"])
    yh_ex = [F(int(v), eco["yden"]) for v in eco["yi"][sl["held"]]]
    arms["landmark"] = {}
    for q in (1, 2, 4, 8, 16, 32, 64):
        step = max(1, len(sl["fit"]) // q)
        L = Xf[[j * step for j in range(q)]]
        K = kernel_design(Xf, L)
        beta = ols(K, yf)
        Kh = kernel_design(Xh, L)
        pred = [rat(v) for v in apply_lin(Kh, beta, "identity")]
        arms["landmark"][str(q)] = {
            "sse_held": fs(exact_sse_from_pred(pred, yh_ex)),
            "ops": q * (3 * d + 4) + 2 * q, "storage": q * (d + 1) + 1,
            "total": q * (3 * d + 4) + 2 * q + q * (d + 1) + 1}
    Bf = basis2(Xf)
    Bh = basis2(Xh)
    bb = ols(Bf, yf)
    predb = [rat(v) for v in apply_lin(Bh, bb, "identity")]
    nb = Bf.shape[1]
    arms["basis2"] = {"n_features": int(nb),
                      "sse_held": fs(exact_sse_from_pred(predb, yh_ex)),
                      "ops": 2 * nb + nb, "storage": nb + 1,
                      "total": 3 * nb + nb + 1}
    return arms


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    src, d1b, pcm, lines, _ = load_sources()
    with open(os.path.join(OUT, "sources.json"), "w") as f:
        json.dump(src, f, indent=1, sort_keys=True)
    jobs = {"H01": (ecology_H01, (d1b,), 4000),
            "H02": (ecology_H02, (pcm,), 1200),
            "H03": (ecology_H03, (lines,), 4000),
            "H04": (ecology_H04, (pcm,), 1200)}
    for name in ["H01", "H02", "H03", "H04"]:
        if which not in ("all", name):
            continue
        fn, args, vr = jobs[name]
        eco = fn(*args)
        t0 = time.time()
        rec, sl, b, h, cls, params, bias, ev = run_scope("SIGMA_" + name, eco, vr)
        if name == "H01":
            rec["arms"] = arms_H01(eco, sl, rec["search"]["ranked_top10"], rec)
        elif name == "H02":
            rec["arms"] = arms_H02(eco, sl)
        elif name == "H03":
            rec["arms"] = arms_H03(eco, sl)
        else:
            rec["arms"] = arms_H04(eco, sl)
        rec["winner"]["cost"] = G.program_cost(b, h, eco["d"], cls["reads_state"])
        rec["winner"]["table_crossover_m"] = G.table_crossover(b, h, cls["reads_state"])
        rec["seconds"] = round(time.time() - t0, 1)
        with open(os.path.join(OUT, "scope_%s.json" % name), "w") as f:
            json.dump(rec, f, indent=1, sort_keys=True)
        print("[%s] WROTE scope_%s.json in %.1fs" % (name, name, rec["seconds"]))


if __name__ == "__main__":
    main()

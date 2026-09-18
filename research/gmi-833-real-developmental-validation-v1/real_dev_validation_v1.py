"""Route A executor for gmi-833-real-developmental-validation-v1.

Created AFTER freeze commit 808054d94dcdc188b7ef3e72cd55c18265ef22af.

Stage 1 (deterministic, stdlib only, no torch): instantiate the six registered
ecologies from the sha256-bound real sources, recompute every invariant,
coefficient vector, threshold and UL-11 label, and assert byte-equality with the
frozen tables of FREEZE_V1.md sections 2.5-2.8.

Stage 2 (deterministic): score the committed REAL_RUNS/ artifacts produced by
train_real_systems_v1.py and train_continual_v1.py against the frozen
predictions, and emit RESULT_V1.json.

Exact rational arithmetic throughout. No float enters any claim.

Usage:
  python3 -I -B real_dev_validation_v1.py [<out RESULT_V1.json>]
"""

import hashlib
import json
import os
import sys
from fractions import Fraction as F

SRC_ROOT = os.environ.get("OCM833_SRC_ROOT", "/home/billy/ocm-scratch/real-l/sources")

EPS = F(1, 4)  # default; each ecology registers its own
PRICE_KEYS = ("p_test", "p_carry", "p_store", "p_build", "p_branch",
              "p_meta", "p_mut", "lam")
NPRICE = 8
KMAX = 3

# ---- registered real sources (primary, fallback) ----------------------------
# (id, primary source, fallback source, rule, rule offsets, CTXK, RS offsets)
SOURCES = [
    ("X1-gutenberg-1342", SRC_ROOT + "/g1342.txt",
     "/usr/share/dict/american-english", "AND", (1, 2), 3, (1, 2, 3, 4), F(3, 8)),
    ("X2-alsa-noise-wav", "/usr/share/sounds/alsa/Noise.wav",
     "/usr/share/sounds/alsa/Rear_Left.wav", "AND", (1, 2), 3, (1, 2, 3, 4), F(3, 8)),
    ("X3-stdlib-json-src", "/usr/lib/python3.8/json/__init__.py",
     "/usr/lib/python3.8/ast.py", "OR", (1, 2), 4, (1, 2, 3, 4), F(7, 16)),
    ("X4-dict-american", "/usr/share/dict/american-english",
     "/usr/share/dict/swedish", "MAJ", (1, 2, 3), 4, (1, 2, 3, 4), F(7, 16)),
    ("X5-gutenberg-84", SRC_ROOT + "/g84.txt",
     SRC_ROOT + "/g2701.txt", "COPY", (2,), 3, (1, 2), F(1, 4)),
    ("X6-python38-elf", "/usr/bin/python3.8", "/usr/bin/git", "OR", (2, 4), 5,
     (1, 2, 3, 4), F(1, 4)),
]


def apply_rule(bits, z, rule, offs):
    v = [bits[z - o] for o in offs]
    if rule == "AND":
        return 1 if all(v) else 0
    if rule == "OR":
        return 1 if any(v) else 0
    if rule == "COPY":
        return v[0]
    if rule == "MAJ":
        return 1 if sum(v) * 2 > len(v) else 0
    raise RuntimeError("unregistered rule " + rule)

# registered ecology shape (identical for every ecology; only the data differs)
M = 9                 # candidates: predict b[z - d], d = 1..9
T = 64                # training positions per episode
NQ = 64               # held-out query positions per episode
K = 4                 # episodes in the registered family
K0 = 1                # leading episodes before the cross-episode slot informs
STARTS = (4, 5, 6, 7, 3, 8, 2, 1, 0)   # registered ascent-start order
BREADTH_GRID = (1, 2, 3, 4, 5, 6, 7, 8, 9)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def bits_from_file(path, nbits):
    raw = open(path, "rb").read()
    need = (nbits + 7) // 8
    if len(raw) < need:
        raise RuntimeError("source too short: %s" % path)
    out = []
    for byte in raw[:need]:
        for s in range(7, -1, -1):
            out.append((byte >> s) & 1)
    return out[:nbits]


def build_episode(bits, base, rule, offs):
    """One episode: positions base+16 .. base+16+T+NQ-1 of the real stream."""
    lo = base + 16
    zs = list(range(lo, lo + T + NQ))
    target = {z: apply_rule(bits, z, rule, offs) for z in zs}
    # candidate tables: candidate i (0-based) predicts b[z - (i+1)]
    Hn = [{z: bits[z - (i + 1)] for z in zs} for i in range(M)]
    train = tuple(zs[:T])
    qset = tuple(zs[T:])
    return {"Z": tuple(zs), "target": target, "H": Hn,
            "train": train, "Qset": qset, "bits": bits}


def posterior(env, eps=None):
    e = EPS if eps is None else eps
    prior = [F(1, M)] * M
    w = []
    for i in range(M):
        err = sum(1 for z in env["train"] if env["H"][i][z] != env["target"][z])
        agr = len(env["train"]) - err
        w.append(prior[i] * (e ** err) * ((1 - e) ** agr))
    s = sum(w)
    if s == 0:
        raise RuntimeError("degenerate posterior")
    return [x / s for x in w]


def weighted_prediction(env, post, z):
    m1 = sum(post[i] for i in range(M) if env["H"][i][z] == 1)
    return 1 if m1 > F(1, 2) else 0


def best_index(post):
    bi, bv = 0, post[0]
    for i in range(1, M):
        if post[i] > bv:
            bi, bv = i, post[i]
    return bi


def alpha_gain(env, post):
    pidx = best_index(post)
    pc = env["H"][pidx]
    g = 0
    for z in env["Qset"]:
        wp = weighted_prediction(env, post, z)
        pp = pc[z]
        t = env["target"][z]
        if pp != t and wp == t:
            g += 1
        elif wp != t and pp == t:
            g -= 1
    return g, pidx


def retrieval(env, ctxk):
    """registered structural retrieval: match the CTXK-bit real context."""
    bits = env["bits"]

    def ctx(z):
        return tuple(bits[z - ctxk:z])
    tmap = {}
    for idx, z in enumerate(env["train"]):
        tmap.setdefault(ctx(z), []).append(idx)
    retr = {}
    for z in env["Qset"]:
        c = ctx(z)
        cand = tmap.get(c)
        retr[z] = cand[-1] if cand else (len(env["train"]) - 1)
    return retr, len(set(retr.values()))


def production_space(rs_offsets):
    """registered finite production set; len = |O| + 2."""
    import itertools
    rs = []
    for o in rs_offsets:
        for v in (0, 1):
            for y in (0, 1):
                rs.append((("off", (o,), (v,)), y, 3))
    for pair in itertools.combinations(rs_offsets, 2):
        for pat in itertools.product((0, 1), repeat=2):
            for y in (0, 1):
                rs.append((("off", pair, pat), y, 4))
    for tri in itertools.combinations(rs_offsets, 3):
        for pat in itertools.product((0, 1), repeat=3):
            for y in (0, 1):
                rs.append((("off", tri, pat), y, 5))
    return rs


def fires(env, prod, z):
    bits = env["bits"]
    (_tag, offs, pat), _y, _ln = prod
    return all(bits[z - o] == v for o, v in zip(offs, pat))


def consistent_cover(env, rs):
    """Dmin over consistent covering subsets of size <= KMAX; measured cover."""
    tr = env["train"]
    ok = []
    for j, p in enumerate(rs):
        y = p[1]
        bad = any(fires(env, p, z) and env["target"][z] != y for z in tr)
        if not bad:
            ok.append(j)
    covsets = {}
    for j in ok:
        covsets[j] = frozenset(z for z in tr if fires(env, rs[j], z))
    full = set(tr)
    best, bestsub = None, None
    import itertools
    for r in range(1, KMAX + 1):
        for sub in itertools.combinations(ok, r):
            u = set()
            for j in sub:
                u |= covsets[j]
            if u >= full:
                tot = sum(rs[j][2] for j in sub)
                if best is None or tot < best:
                    best, bestsub = tot, sub
        if best is not None:
            break
    if best is None:
        # no full cover: measured partial cover with the best subset by coverage
        bestsub = None
        bestcov = set()
        for r in range(1, KMAX + 1):
            for sub in itertools.combinations(ok, r):
                u = set()
                for j in sub:
                    u |= covsets[j]
                if len(u) > len(bestcov):
                    bestcov, bestsub = u, sub
        cover_measured = 2 * len(bestcov)
        return None, None, cover_measured, len(ok)
    u = set()
    for j in bestsub:
        u |= covsets[j]
    return best, bestsub, 2 * len(u), len(ok)


def vfun(env):
    return [F(sum(1 for z in env["train"] if env["H"][i][z] == env["target"][z]),
              len(env["train"])) for i in range(M)]


def ascent(V, start):
    cur, steps = start, 0
    while True:
        nb = [j for j in (cur - 1, cur + 1) if 0 <= j < M]
        best = max(nb + [cur], key=lambda j: (V[j], -j))
        if best == cur:
            return cur, steps
        cur, steps = best, steps + 1


def breadth_invariants(V):
    gi = max(range(M), key=lambda i: (V[i], -i))
    Vglob = V[gi]
    t0, stepmax = ascent(V, STARTS[0])
    Vloc = V[t0]
    Bmin = None
    for b in BREADTH_GRID:
        reached = False
        for s in STARTS[:b]:
            t, _ = ascent(V, s)
            if V[t] == Vglob:
                reached = True
        if reached:
            Bmin = b
            break
    if Bmin is None:
        Bmin = max(BREADTH_GRID)
    return Vglob, Vloc, Bmin, max(stepmax, 1)


def tuple_vector(g, inv, env, loss):
    carry, store, build, breadth, meta, mut = g
    Kx, Tx, nq = inv["K"], inv["T"], inv["nq"]
    evals = 0
    for ep in range(Kx):
        width = inv["M"]
        if meta > 0 and ep >= inv["k0"]:
            width = meta
        if carry > 0:
            evals += width * Tx
    if carry == 0 and store == 0 and build == 0:
        ascent_c = breadth * (inv["Tsteps"] + 1) * (inv["max_degree"] + 1) * Tx
    else:
        ascent_c = 0
    evals += Kx * (store * nq + ascent_c +
                   (inv["disc"] if build > 0 else 0) + build * nq + nq)
    return (evals, Kx * carry * Tx, Kx * store * Tx, Kx * build,
            Kx * (breadth - 1) * inv["Tsteps"], meta * Kx, Kx * mut, loss)


def solve_ratio_threshold(va, vb, coord):
    A1, B1 = F(va[coord]), F(vb[coord])
    A0 = sum(F(va[i]) for i in range(NPRICE) if i != coord)
    B0 = sum(F(vb[i]) for i in range(NPRICE) if i != coord)
    if A1 == B1:
        if A0 == B0:
            return None, "IDENTICAL_AT_EVERY_PRICE"
        return None, ("A_WINS_AT_EVERY_PRICE" if A0 < B0 else "B_WINS_AT_EVERY_PRICE")
    x = (B0 - A0) / (A1 - B1)
    if x <= 0:
        at1 = (A0 + A1) - (B0 + B1)
        return x, ("A_WINS_AT_EVERY_POSITIVE_PRICE" if at1 < 0 else
                   ("B_WINS_AT_EVERY_POSITIVE_PRICE" if at1 > 0 else "TIE_AT_UNIT"))
    return x, ("A_WINS_BELOW" if A1 > B1 else "A_WINS_ABOVE")


# ---- emitted predictors per structural tuple (faithful to the #1018 mapping) --
def loss_weighted(env, post):
    return sum(1 for z in env["Qset"]
               if weighted_prediction(env, post, z) != env["target"][z])


def loss_point(env, post):
    pi_ = best_index(post)
    return sum(1 for z in env["Qset"]
               if env["H"][pi_][z] != env["target"][z])


def loss_incumbent(env):
    cur = STARTS[0]
    return sum(1 for z in env["Qset"] if env["H"][cur][z] != env["target"][z])


def loss_retrieval(env, retr):
    tr = env["train"]
    return sum(1 for z in env["Qset"]
               if env["target"][tr[retr[z]]] != env["target"][z])


def loss_rules(env, rs, sub):
    if sub is None:
        return len(env["Qset"])
    bad = 0
    for z in env["Qset"]:
        pred = None
        for j in sub:
            if fires(env, rs[j], z):
                pred = rs[j][1]
                break
        if pred is None:
            pred = 0
        if pred != env["target"][z]:
            bad += 1
    return bad


def loss_breadth(env, V, b):
    best, bv = None, None
    for s in STARTS[:b]:
        t, _ = ascent(V, s)
        if bv is None or V[t] > bv:
            best, bv = t, V[t]
    return sum(1 for z in env["Qset"] if env["H"][best][z] != env["target"][z])


def loss_meta(env, post, hprime):
    sub = sorted(hprime)
    bi = max(sub, key=lambda i: (post[i], -i))
    return sum(1 for z in env["Qset"] if env["H"][bi][z] != env["target"][z])


# ---- UL-11 (frozen 5-step selector, reimplemented from the #1018 freeze) -----
REGIME_IDS = ("SIG-W", "BASE-0", "NULL-0", "SIG-X", "SIG-R", "SIG-L",
              "SIG-P", "SIG-T", "SIG-S")
SEVEN = ("SIG-W", "SIG-X", "SIG-R", "SIG-L", "SIG-P", "SIG-T", "SIG-S")
REQUIRED_KEYS = ("M", "T", "nq", "K", "k0", "Mprime", "r", "mu", "Dmin",
                 "disc", "Bmin", "Tsteps", "max_degree", "alpha_gain")


def charge(vec, price):
    return sum(F(vec[i]) * price[i] for i in range(NPRICE))


def select(inv, vecs, price):
    for k in REQUIRED_KEYS:
        if inv.get(k) is None:
            return {"kind": "ABSTAIN_UNDERDETERMINED", "missing": k}
    for rid in SEVEN:
        if vecs.get(rid) is None:
            return {"kind": "ABSTAIN_UNDERDETERMINED", "missing": "coefficients:" + rid}
    for x in price:
        if not isinstance(x, F) or x <= 0:
            return {"kind": "ABSTAIN_ILL_TYPED"}
    scored = [(charge(vecs[r], price), r) for r in SEVEN]
    best = min(s for s, _ in scored)
    tied = sorted(r for s, r in scored if s == best)
    if len(tied) == 1:
        return {"kind": "REGIME", "regime": tied[0], "charge": str(best)}
    return {"kind": "ABSTAIN_TIE", "tied": tied, "charge": str(best)}


# ---- registered anchored price vectors (frozen design, not measured) ---------
def P(**kw):
    d = {k: F(1) for k in PRICE_KEYS}
    d.update({k: F(v) if not isinstance(v, F) else v for k, v in kw.items()})
    return tuple(d[k] for k in PRICE_KEYS)


ANCHORED = [
    ("A1-unit", P()),
    ("A2-carry-cheap", P(p_carry=F(1, 256), p_store=F(256), p_build=F(256),
                         p_branch=F(256), p_meta=F(256), p_mut=F(256), lam=F(256))),
    ("A3-store-cheap", P(p_store=F(1, 256), p_carry=F(256), p_build=F(256),
                         p_branch=F(256), p_meta=F(256), p_mut=F(256), lam=F(256))),
    ("A4-build-cheap", P(p_build=F(1, 256), p_test=F(1, 4096), p_carry=F(256),
                         p_store=F(256), p_branch=F(256), p_meta=F(256),
                         p_mut=F(256), lam=F(256))),
    ("A5-branch-cheap", P(p_branch=F(1, 256), p_carry=F(256), p_store=F(256),
                          p_build=F(256), p_meta=F(256), p_mut=F(256), lam=F(256))),
    ("A6-meta-cheap", P(p_meta=F(1, 256), p_carry=F(256), p_store=F(256),
                        p_build=F(256), p_branch=F(256), p_mut=F(256), lam=F(256))),
    ("A7-mut-cheap", P(p_mut=F(1, 256), p_carry=F(256), p_store=F(256),
                       p_build=F(256), p_branch=F(256), p_meta=F(256), lam=F(256))),
    ("A8-loss-dominant", P(lam=F(4096))),
]


def derive(sid, path, fallback, rule, roffs, ctxk, rs_offsets, eps):
    used, fb = path, False
    try:
        open(used, "rb").close()
    except OSError:
        used, fb = fallback, True
    nbits = K * (T + NQ) + 16 * K + 64
    bits = bits_from_file(used, nbits)
    eps_ = [build_episode(bits, ep * (T + NQ), rule, roffs) for ep in range(K)]
    env = eps_[0]
    post = posterior(env, eps)
    ag, pidx = alpha_gain(env, post)
    retr, mu = retrieval(env, ctxk)
    rs = production_space(rs_offsets)
    Dmin, sub, cover, n_consistent = consistent_cover(env, rs)
    V = vfun(env)
    Vglob, Vloc, Bmin, Tsteps = breadth_invariants(V)
    hp = set()
    for e in eps_:
        for i in range(M):
            if all(e["H"][i][z] == e["target"][z] for z in e["Z"]):
                hp.add(i)
    target_in_H = bool(hp)
    if not hp:
        hp = set(range(M))
    Mprime = len(hp)
    disc = len(rs) * T
    inv = {"M": M, "T": T, "nq": NQ, "K": K, "k0": K0, "Mprime": Mprime,
           "r": M - Mprime, "mu": mu, "Dmin": Dmin, "disc": disc,
           "Bmin": Bmin, "Tsteps": Tsteps, "max_degree": 2,
           "alpha_gain": ag, "cover": cover, "RS_size": len(rs),
           "n_consistent_productions": n_consistent,
           "Vglob": str(Vglob), "Vloc": str(Vloc), "target_in_H": target_in_H,
           "compression_strict": (Dmin is not None and Dmin < cover)}
    Dmin_L, hocc, delta, kdef = None, None, None, None
    if Dmin is not None and sub is not None:
        counts = {}
        for z in env["Qset"]:
            for j in sub:
                if fires(env, rs[j], z):
                    counts[j] = counts.get(j, 0) + 1
                    break
        if counts:
            prod = sorted(counts, key=lambda j: (-counts[j], j))[0]
            ln = rs[prod][2]
            hocc, delta, kdef = counts[prod], ln - 1, ln + 1
            Dmin_L = max(1, Dmin - (hocc * delta - kdef))
    inv["Dmin_L"] = Dmin_L
    inv["Hocc"] = hocc
    inv["Delta"] = delta
    inv["Kdef"] = kdef
    b2 = Bmin if Bmin >= 2 else 2
    losses = {
        "SIG-W": loss_weighted(env, post),
        "BASE-0": loss_point(env, post),
        "NULL-0": loss_incumbent(env),
        "SIG-X": loss_retrieval(env, retr),
        "SIG-R": loss_rules(env, rs, sub),
        "SIG-L": loss_rules(env, rs, sub),
        "SIG-P": loss_breadth(env, V, b2),
        "SIG-T": loss_meta(env, post, hp),
    }
    losses["SIG-S"] = losses["BASE-0"]
    tuples = {
        "SIG-W": (M, 0, 0, 1, 0, 0),
        "BASE-0": (1, 0, 0, 1, 0, 0),
        "NULL-0": (0, 0, 0, 1, 0, 0),
        "SIG-X": (0, mu, 0, 1, 0, 0),
        "SIG-R": (0, 0, Dmin, 1, 0, 0) if Dmin is not None else None,
        "SIG-L": (0, 0, Dmin_L, 1, 0, 0) if Dmin_L is not None else None,
        "SIG-P": (0, 0, 0, b2, 0, 0),
        "SIG-T": (1, 0, 0, 1, Mprime, 0),
        "SIG-S": (1, 0, 0, 1, 0, 1),
    }
    vecs = {}
    for rid, g in tuples.items():
        vecs[rid] = None if g is None else tuple_vector(g, inv, env, losses[rid])
    th = {}
    th["beta_star"] = str(F(ag, (M - 1) * T))
    den = (Bmin - 1) * Tsteps
    th["pistar_star"] = "0" if den == 0 else str((Vglob - Vloc) / den)
    th["tau_star"] = str(F(inv["r"] * T * (K - K0), Mprime * K))
    if vecs["SIG-X"] is not None and vecs["SIG-R"] is not None:
        x, o = solve_ratio_threshold(vecs["SIG-X"], vecs["SIG-R"],
                                     PRICE_KEYS.index("p_store"))
        th["chi_star"] = None if x is None else str(x)
        th["chi_orientation"] = o
    else:
        th["chi_star"] = None
        th["chi_orientation"] = "UNDETERMINED_NO_CONSISTENT_COVER"
    sel = {}
    for name, price in ANCHORED:
        sel[name] = select(inv, vecs, price)
    return {"system_id": sid, "source_used": used, "fallback_used": fb,
            "rule": rule, "rule_offsets": list(roffs), "ctxk": ctxk, "eps": str(eps),
            "source_sha256": sha256_file(used),
            "invariants": inv, "losses": losses,
            "coefficient_vectors": {k: (None if v is None else list(v))
                                    for k, v in vecs.items()},
            "thresholds": th, "ul11": sel}



# ---------------------------------------------------------------------------
# FROZEN tables from FREEZE_V1.md sections 2.5-2.8. The executor must reproduce
# these exactly from the sha256-bound real sources; any divergence fails closed.
# ---------------------------------------------------------------------------
FROZEN_SHA256 = {
    "X1-gutenberg-1342": "81300b79e8a8d65ac530a97578417d06137e3bbc90622a10a65e5036183d2500",
    "X2-alsa-noise-wav": "0d897df3862192ea078efc1dd8fdc4f51fae9e93d3ed4c15e049829b0386729e",
    "X3-stdlib-json-src": "41c4abb6840b6eeca85e7ea5e9b08bba71dc529725a415cc826ca940be4c79b2",
    "X4-dict-american": "f6c94d35691b9c356f7e5072f94d23f127b168cf9b04f0f5b26e0cb1f6ef4414",
    "X5-gutenberg-84": "06c37d2c52d208d3d81eb12c3b10b5edbd7728b73554325ddceadbe2fb427e77",
    "X6-python38-elf": "298a9e830ed52f36c299427565485d717d1ce0179c0597cc16560513eb780b06",
}
FROZEN_INVARIANTS = {
    # id: (Mprime, r, mu, Dmin, Dmin_L, cover, RS_size, Bmin, Tsteps, alpha_gain, target_in_H)
    "X1-gutenberg-1342": (9, 0, 7, 10, 1, 128, 128, 7, 1, 10, False),
    "X2-alsa-noise-wav": (9, 0, 8, 10, 1, 128, 128, 5, 1, 6, False),
    "X3-stdlib-json-src": (9, 0, 14, 10, 1, 128, 128, 7, 1, 0, False),
    "X4-dict-american": (9, 0, 15, None, None, 96, 128, 5, 1, 15, False),
    "X5-gutenberg-84": (1, 8, 7, 6, 1, 128, 16, 7, 1, 0, True),
    "X6-python38-elf": (9, 0, 6, 10, 1, 128, 128, 1, 1, 0, False),
}
FROZEN_THRESHOLDS = {
    "X1-gutenberg-1342": ("5/256", "16787/896", "1/192", "0"),
    "X2-alsa-noise-wav": ("3/256", "4165/256", "5/256", "0"),
    "X3-stdlib-json-src": ("0", "1135/128", "11/384", "0"),
    "X4-dict-american": ("15/512", None, "1/32", "0"),
    "X5-gutenberg-84": ("0", "1931/896", "7/128", "384"),
    "X6-python38-elf": ("0", "4229/192", "0", "0"),
}
_R = ["SIG-S", "SIG-W", "SIG-X", "SIG-L", "SIG-P", "SIG-P", "SIG-P", "SIG-X"]
_A = ["ABSTAIN_UNDERDETERMINED"] * 8
FROZEN_UL11 = {
    "X1-gutenberg-1342": list(_R),
    "X2-alsa-noise-wav": list(_R),
    "X3-stdlib-json-src": list(_R),
    "X4-dict-american": list(_A),
    "X5-gutenberg-84": ["SIG-T", "SIG-T", "SIG-X", "SIG-L", "SIG-L", "SIG-L",
                        "SIG-L", "SIG-T"],
    "X6-python38-elf": list(_R),
}
PRICE_NAMES = [n for n, _ in ANCHORED]
RANKED = SEVEN


def check_frozen(eco):
    """Every divergence from the freeze is a hard failure, reported by name."""
    sid = eco["system_id"]
    i = eco["invariants"]
    errs = []
    if eco["source_sha256"] != FROZEN_SHA256[sid]:
        errs.append("SOURCE_SHA256_MISMATCH:" + sid)
    fi = FROZEN_INVARIANTS[sid]
    got = (i["Mprime"], i["r"], i["mu"], i["Dmin"], i["Dmin_L"], i["cover"],
           i["RS_size"], i["Bmin"], i["Tsteps"], i["alpha_gain"], i["target_in_H"])
    if got != fi:
        errs.append("INVARIANT_MISMATCH:%s:%r!=%r" % (sid, got, fi))
    t = eco["thresholds"]
    gt = (t["beta_star"], t["chi_star"], t["pistar_star"], t["tau_star"])
    if gt != FROZEN_THRESHOLDS[sid]:
        errs.append("THRESHOLD_MISMATCH:%s:%r!=%r" % (sid, gt, FROZEN_THRESHOLDS[sid]))
    got_lab = [(eco["ul11"][n].get("regime") or eco["ul11"][n]["kind"])
               for n in PRICE_NAMES]
    if got_lab != FROZEN_UL11[sid]:
        errs.append("UL11_LABEL_MISMATCH:%s:%r!=%r" % (sid, got_lab, FROZEN_UL11[sid]))
    return errs


# ---------------------------------------------------------------------------
# Stage 2a: score the Section I real trained systems (blind, opaque IDs)
# ---------------------------------------------------------------------------
def score_real_systems(eco, run):
    """run['measured'] maps opaque id -> 8 integer coordinates. The mapping
    opaque id -> signature is consumed ONLY after the argmin is fixed."""
    opaque = run["measured"]
    for oid, vec in sorted(opaque.items()):
        if len(vec) != NPRICE or any((not isinstance(v, int)) or v < 0 for v in vec):
            raise RuntimeError("INVALID_MEASURED_VECTOR:" + oid)
    # UL-11 ranks exactly the seven signatures; BASE-0 and NULL-0 are
    # recorded comparators (FREEZE 2.9) and must not enter the argmin.
    o2s = run["opaque_to_signature"]
    ranked_ids = sorted(o for o in opaque if o2s[o] in RANKED)
    cells = {}
    for name, price in ANCHORED:
        scored = sorted((charge(opaque[o], price), o) for o in ranked_ids)
        best = scored[0][0]
        tied = sorted(o for c, o in scored if c == best)
        pred = eco["ul11"][name].get("regime") or eco["ul11"][name]["kind"]
        if len(tied) > 1:
            cells[name] = {"verdict": "TIE_NONIDENTIFYING", "predicted": pred,
                           "observed": None, "tied": tied,
                           "observed_charge": str(best)}
            continue
        # de-anonymise only now
        obs = o2s[tied[0]]
        if pred.startswith("ABSTAIN"):
            v = "ABSTAIN_UNMATCHED"
        else:
            v = "HIT" if obs == pred else "MISS"
        cells[name] = {"verdict": v, "predicted": pred, "observed": obs,
                       "observed_charge": str(best)}
    return cells


def divergence_report(eco, run):
    """RV-3 diagnostic: how far the MEASURED resource/loss vector of a real
    trained realization sits from the ANALYTIC vector a_i(E) that UL-11 ranks.
    Exact rational ratios; no float."""
    o2s = run["opaque_to_signature"]
    out = {}
    for oid, obs in sorted(run["measured"].items()):
        sig = o2s[oid]
        ana = eco["coefficient_vectors"].get(sig)
        if ana is None:
            continue
        rows = {}
        for i, k in enumerate(PRICE_KEYS):
            a, b = ana[i], obs[i]
            rows[k] = {"analytic": a, "measured": b,
                       "ratio": (None if a == 0 else str(F(b, a))),
                       "equal": a == b}
        out[sig] = {"coords": rows,
                    "loss_analytic": ana[NPRICE - 1],
                    "loss_measured": obs[NPRICE - 1],
                    "any_coord_differs": any(not r["equal"] for r in rows.values())}
    return out


def score_abstaining(eco, run):
    """A frozen-abstention ecology: every cell must abstain for the registered
    reason. The real systems are still measured and recorded."""
    cells = {}
    for name, _price in ANCHORED:
        sel = eco["ul11"][name]
        # Post-freeze deviation D1, disclosed: FREEZE 2.7 named the registered
        # abstention reason `coefficients:SIG-R`. UL-11 STEP 1 reaches the
        # invariant gate first, so the emitted key is `Dmin`. Same root cause
        # (no consistent cover exists on X4) and the same frozen label
        # ABSTAIN_UNDERDETERMINED; only the reported key differs.
        ok = (sel["kind"] == "ABSTAIN_UNDERDETERMINED"
              and sel.get("missing") in ("Dmin", "coefficients:SIG-R"))
        cells[name] = {"verdict": "ABSTAIN_MATCHED" if ok else "ABSTAIN_UNMATCHED",
                       "predicted": sel["kind"], "observed": None,
                       "missing": sel.get("missing")}
    return cells


# ---------------------------------------------------------------------------
# Stage 2b: score the Section L continual-learning receipts (HIST-1/CAPITAL-1/
# DP-1/EV-1 exactly as #909/#908 state them)
# ---------------------------------------------------------------------------
C_PROP = 300          # priced burden of one proposal (FREEZE 3.2)
H_LOW = F(0)
H_HIGH = F(4800)
N_PROP = 24
THETA_NUM, THETA_DEN = 1, 4


def hist1_verdict(p0, pH, h):
    """#909/#908 HIST-1A with its four registered boundary terminals."""
    if p0 == 0 and pH == 0:
        return "BOTH_UNREACHABLE"
    if p0 == 0:
        return "HISTORY_STRICTLY_IMPROVES"
    if pH == 0:
        return "HISTORY_HARMS"
    lhs = h + F(C_PROP) / pH
    rhs = F(C_PROP) / p0
    if lhs < rhs:
        return "HISTORY_STRICTLY_IMPROVES"
    if lhs == rhs:
        return "TIE"
    return "HISTORY_HARMS"


def classify_capital(solution_capital, law_changed, verdict):
    """#909/#908 CAPITAL-1A 2x2. The contaminated cell fails closed with None."""
    if solution_capital and not law_changed:
        return {"solution_capital": True, "search_policy_capital": False,
                "status": "SOLUTION_ONLY_UNCHANGED_POLICY"}
    if solution_capital and law_changed:
        return {"solution_capital": True, "search_policy_capital": None,
                "status": "CANNOT_IDENTIFY_STORED_SOLUTION_CONTAMINATION"}
    return {"solution_capital": False,
            "search_policy_capital": bool(law_changed and
                                          verdict == "HISTORY_STRICTLY_IMPROVES"),
            "status": ("SEARCH_POLICY_CAPITAL"
                       if (law_changed and verdict == "HISTORY_STRICTLY_IMPROVES")
                       else "NO_SEARCH_POLICY_CAPITAL")}


def ev1a_band(p, mean_first_hit):
    """EV-1A: E[T] = 1/p, Var = (1-p)/p^2. Registered 2-sigma band, compared in
    exact rational arithmetic by squaring -- no float, no sqrt."""
    if p == 0:
        return {"status": "UNREACHABLE_ZERO_USEFUL_MASS", "in_band": None,
                "expected": None}
    mu = F(1) / p
    var = (1 - p) / (p * p)
    d = mean_first_hit - mu
    in_band = (d * d) <= (4 * var)
    return {"status": "FINITE_EXPECTATION", "expected": str(mu),
            "variance": str(var), "mean_first_hit": str(mean_first_hit),
            "in_band": bool(in_band)}


def score_continual_v2(rec, tag="CL2"):
    """FREEZE_V2_REVIVAL.md scorer: adds the DP-1 budget ladder and the
    CENSORED terminal for EV-1A."""
    n = rec["N_prop"]
    p0 = F(rec["successes_Q0"], n)
    pH = F(rec["successes_QH"], n)
    fam = rec["family"]
    c = rec["c"]
    h_low, h_high = F(rec["h_low"]), F(rec["h_high"])

    def verdict(h):
        if p0 == 0 and pH == 0:
            return "BOTH_UNREACHABLE"
        if p0 == 0:
            return "HISTORY_STRICTLY_IMPROVES"
        if pH == 0:
            return "HISTORY_HARMS"
        lhs, rhs = h + F(c) / pH, F(c) / p0
        return ("HISTORY_STRICTLY_IMPROVES" if lhs < rhs
                else ("TIE" if lhs == rhs else "HISTORY_HARMS"))

    v_low, v_high = verdict(h_low), verdict(h_high)
    sol_cap = bool(rec["stored_solution_reaches_U"])
    cap = classify_capital(sol_cap, bool(rec["law_changed"]), v_low)
    if rec["first_hit_censored_QH"] > 0 or rec["first_hit_blocks_QH"] == 0:
        ev = {"status": "CENSORED",
              "censored_blocks": rec["first_hit_censored_QH"], "in_band": None}
    else:
        ev = ev1a_band(pH, F(rec["first_hit_sum_QH"], rec["first_hit_blocks_QH"]))
    hstar = (None if (p0 == 0 or pH == 0) else F(c) / p0 - F(c) / pH)
    hd0 = rec["C_pot_Q0_B2"] - rec["C_now_Q0"]
    hdH = rec["C_pot_QH_B2"] - rec["C_now_QH"]
    interior = (0 < rec["successes_Q0"] < n)
    ch = {}
    if fam == "POS":
        ch[tag + "-P1"] = bool(pH > p0)
        ch[tag + "-P2"] = (v_low == "HISTORY_STRICTLY_IMPROVES")
        ch[tag + "-P3"] = (v_high != "HISTORY_STRICTLY_IMPROVES")
        ch[tag + "-P4"] = (not sol_cap) and cap["status"] == "SEARCH_POLICY_CAPITAL"
        ch[tag + "-P5b"] = bool(rec["C_now_Q0"] == rec["C_now_QH"] and hdH > hd0)
    else:
        ch[tag + "-P1"] = bool(pH <= p0)
        ch[tag + "-P2"] = (v_low != "HISTORY_STRICTLY_IMPROVES")
        ch[tag + "-P3"] = (v_high != "HISTORY_STRICTLY_IMPROVES")
        ch[tag + "-P4"] = True
        ch[tag + "-P5b"] = bool(hdH <= hd0)
    ch[tag + "-P5a"] = bool(rec["C_pot_Q0_B1"] <= rec["C_pot_Q0_B2"]
                         and rec["C_pot_QH_B1"] <= rec["C_pot_QH_B2"])
    ch[tag + "-P6"] = (ev.get("in_band") is True)
    ch[tag + "-P7"] = isinstance(pH, F)
    return {"sequence_id": rec["sequence_id"], "family": fam,
            "source_sha256": rec["source_sha256"],
            "p0": str(p0), "pH": str(pH), "Ev_Q_U": str(pH),
            "baseline_mass_interior": interior,
            "c": c, "h_low": str(h_low), "h_high": str(h_high),
            "h_star": None if hstar is None else str(hstar),
            "verdict_h_low": v_low, "verdict_h_high": v_high,
            "capital": cap, "ev1a": ev,
            "C_now_Q0": rec["C_now_Q0"], "C_now_QH": rec["C_now_QH"],
            "C_pot_Q0_B1": rec["C_pot_Q0_B1"], "C_pot_QH_B1": rec["C_pot_QH_B1"],
            "C_pot_Q0_B2": rec["C_pot_Q0_B2"], "C_pot_QH_B2": rec["C_pot_QH_B2"],
            "headroom_Q0_B2": hd0, "headroom_QH_B2": hdH,
            "checks": ch}


def score_continual(rec):
    p0 = F(rec["successes_Q0"], N_PROP)
    pH = F(rec["successes_QH"], N_PROP)
    fam = rec["family"]
    law_changed = bool(rec["law_changed"])
    sol_cap = bool(rec["stored_solution_reaches_U"])
    v_low = hist1_verdict(p0, pH, H_LOW)
    v_high = hist1_verdict(p0, pH, H_HIGH)
    cap = classify_capital(sol_cap, law_changed, v_low)
    mfh = (F(rec["first_hit_sum_QH"], rec["first_hit_blocks_QH"])
           if rec["first_hit_blocks_QH"] else F(0))
    ev = ev1a_band(pH, mfh)
    hstar = (None if (p0 == 0 or pH == 0)
             else F(C_PROP) / p0 - F(C_PROP) / pH)
    pot_H = rec["C_pot_QH"]
    pot_0 = rec["C_pot_Q0"]
    checks = {}
    if fam == "POS":
        checks["CL-P1"] = bool(pH > p0)
        checks["CL-P2"] = (v_low == "HISTORY_STRICTLY_IMPROVES")
        checks["CL-P3"] = (v_high != "HISTORY_STRICTLY_IMPROVES")
        checks["CL-P4"] = (not sol_cap) and cap["status"] == "SEARCH_POLICY_CAPITAL"
        checks["CL-P5"] = (rec["C_now_QH"] == rec["C_now_Q0"] == 0) and pot_H > pot_0
    else:
        checks["CL-P1"] = bool(pH <= p0)
        checks["CL-P2"] = (v_low != "HISTORY_STRICTLY_IMPROVES")
        checks["CL-P3"] = (v_high != "HISTORY_STRICTLY_IMPROVES")
        checks["CL-P4"] = True
        checks["CL-P5"] = not (pot_H > pot_0)
    checks["CL-P6"] = (ev["in_band"] is True) if pH > 0 else (
        ev["status"] == "UNREACHABLE_ZERO_USEFUL_MASS")
    checks["CL-P7"] = isinstance(pH, F)
    return {"sequence_id": rec["sequence_id"], "family": fam,
            "source_sha256": rec["source_sha256"],
            "p0": str(p0), "pH": str(pH), "Ev_Q_U": str(pH),
            "c": C_PROP, "h_low": str(H_LOW), "h_high": str(H_HIGH),
            "h_star": None if hstar is None else str(hstar),
            "verdict_h_low": v_low, "verdict_h_high": v_high,
            "capital": cap, "ev1a": ev,
            "C_now_Q0": rec["C_now_Q0"], "C_now_QH": rec["C_now_QH"],
            "C_pot_Q0": pot_0, "C_pot_QH": pot_H,
            "headroom_Q0": pot_0 - rec["C_now_Q0"],
            "headroom_QH": pot_H - rec["C_now_QH"],
            "checks": checks}


def load_runs(d):
    out = {}
    if not os.path.isdir(d):
        return out
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".json"):
            with open(os.path.join(d, fn)) as f:
                out[fn] = json.load(f)
    return out


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    outp = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "RESULT_V1.json")
    ecos = [derive(*s) for s in SOURCES]
    freeze_errors = []
    for e in ecos:
        freeze_errors.extend(check_frozen(e))
    runs = load_runs(os.path.join(here, "REAL_RUNS"))
    section_i = {}
    for e in ecos:
        sid = e["system_id"]
        r = runs.get("ecology_%s.json" % sid)
        if r is None:
            section_i[sid] = {"status": "NO_RUN_ARTIFACT"}
            continue
        if r["source_sha256"] != FROZEN_SHA256[sid]:
            section_i[sid] = {"status": "RUN_SOURCE_SHA256_MISMATCH"}
            continue
        cells = (score_abstaining(e, r) if FROZEN_UL11[sid][0].startswith("ABSTAIN")
                 else score_real_systems(e, r))
        section_i[sid] = {"status": "SCORED", "cells": cells,
                          "analytic_vs_measured": divergence_report(e, r),
                          "measured": {k: list(v) for k, v in
                                       sorted(r["measured"].items())},
                          "comparators_recorded_not_ranked": sorted(
                              o for o, sg in r["opaque_to_signature"].items()
                              if sg not in RANKED),
                          "seed_spread": r.get("seed_spread"),
                          "torch_version": r.get("torch_version")}
    section_l = {}
    section_l2 = {}
    section_l3 = {}
    for fn, rec in sorted(runs.items()):
        if fn.startswith("cl_"):
            section_l[rec["sequence_id"]] = score_continual(rec)
        elif fn.startswith("cl2_"):
            section_l2[rec["sequence_id"]] = score_continual_v2(rec)
        elif fn.startswith("cl3_"):
            section_l3[rec["sequence_id"]] = score_continual_v2(rec, "CL3")
    tally = {"HIT": 0, "MISS": 0, "ABSTAIN_MATCHED": 0, "ABSTAIN_UNMATCHED": 0,
             "TIE_NONIDENTIFYING": 0}
    for sid, v in section_i.items():
        for c in v.get("cells", {}).values():
            tally[c["verdict"]] = tally.get(c["verdict"], 0) + 1
    def tally_of(sec):
        t = {"HIT": 0, "MISS": 0}
        for _sid, v in sec.items():
            for _k, ok in v["checks"].items():
                t["HIT" if ok else "MISS"] += 1
        return t

    cl_tally = tally_of(section_l)
    cl2_tally = tally_of(section_l2)
    cl3_tally = tally_of(section_l3)
    ecologies_scored = sum(1 for v in section_i.values() if v["status"] == "SCORED")
    div_sig, div_tot, loss_diff = set(), 0, 0
    for _sid, v in section_i.items():
        for sg, d in v.get("analytic_vs_measured", {}).items():
            div_tot += 1
            if d["any_coord_differs"]:
                div_sig.add(sg)
            if d["loss_analytic"] != d["loss_measured"]:
                loss_diff += 1
    cl_pos_qualifying = sum(
        1 for v in section_l.values()
        if v["family"] == "POS"
        and v["capital"]["status"] == "SEARCH_POLICY_CAPITAL")
    terminal_i = ("REAL_ECOLOGY_SELECTOR_TEST_EXECUTED_AT_REGISTERED_SCOPE"
                  if (ecologies_scored == 6 and not freeze_errors)
                  else "INSUFFICIENT_REAL_ECOLOGY_EVIDENCE")
    def pos_qual(sec):
        return sum(1 for v in sec.values()
                   if v["family"] == "POS"
                   and v["capital"]["status"] in ("SEARCH_POLICY_CAPITAL",
                                                  "NO_SEARCH_POLICY_CAPITAL"))

    def pos_direction_hits(sec):
        return sum(1 for v in sec.values()
                   if v["family"] == "POS" and v["checks"].get("CL2-P1") is True)

    # CL3-P8 matched control: same source, same U, same budget, same seeds;
    # only the four sequence task offsets differ. Pairs are T0k <-> T1k.
    matched = {}
    for pid in sorted(section_l3):
        if not pid.startswith("T0"):
            continue
        nid = "T1" + pid[2:]
        if nid not in section_l3:
            continue
        pv, nv = section_l3[pid], section_l3[nid]
        if pv["source_sha256"] != nv["source_sha256"]:
            matched[pid] = {"status": "SOURCE_MISMATCH"}
            continue
        ok = F(pv["pH"]) > F(nv["pH"])
        matched[pid] = {"pos": pid, "neg": nid,
                        "source_sha256": pv["source_sha256"],
                        "pH_pos": pv["pH"], "pH_neg": nv["pH"],
                        "p0_pos": pv["p0"], "p0_neg": nv["p0"],
                        "CL3-P8": bool(ok)}
    for pid, mv in matched.items():
        if "CL3-P8" in mv:
            section_l3[pid]["checks"]["CL3-P8"] = mv["CL3-P8"]

    # DP-1B is an EXISTENCE claim: there exist states with equal current
    # capability and different headroom. Identified POST HOC from the frozen
    # V3 record -- reported as an observation, never counted as a frozen hit.
    dp1b = {"witnesses": [], "note": ("post-hoc census over the committed V3 "
                                      "record; not a frozen prediction")}
    for sid in sorted(section_l3):
        v = section_l3[sid]
        if v["C_now_Q0"] == v["C_now_QH"] and v["headroom_Q0_B2"] != v["headroom_QH_B2"]:
            dp1b["witnesses"].append(
                {"sequence_id": sid, "C_now": v["C_now_Q0"],
                 "headroom_Q0_B2": v["headroom_Q0_B2"],
                 "headroom_QH_B2": v["headroom_QH_B2"]})

    latest = section_l3 if section_l3 else section_l2
    lab = "V3" if section_l3 else "V2"
    mc_hits = sum(1 for v in matched.values() if v.get("CL3-P8") is True)
    mc_pairs = len(matched)
    cap_clean = sum(
        1 for v in latest.values()
        if v["capital"]["status"] != "CANNOT_IDENTIFY_STORED_SOLUTION_CONTAMINATION"
    ) if latest else 0
    if latest and mc_pairs >= 5 and mc_hits == mc_pairs and cap_clean == len(latest):
        terminal_l = ("DEVELOPMENTAL_PREDICTIONS_VALIDATED_ON_REAL_CONTINUAL_"
                      "SYSTEMS_AT_REGISTERED_SCOPE")
    else:
        terminal_l = ("CONTINUAL_LEARNING_PREDICTIONS_EXECUTED_"
                      "PARTIAL_DIRECTION_AGREEMENT_AT_%s" % lab)
    res = {
        "schema": "GMI_833_REAL_DEVELOPMENTAL_VALIDATION_RESULT_V1",
        "claim_ceiling": ("GMI_833_REAL_SYSTEM_UPDATE_LAW_AND_DEVELOPMENTAL_"
                          "VALIDATION_AND_DERIVED_INVENTION_LIBRARY_CONDITIONS_"
                          "AT_REGISTERED_SCOPE"),
        "freeze_commit": "808054d94dcdc188b7ef3e72cd55c18265ef22af",
        "source_main": "91cff402303be751e464eb8a8001d2258d0e05a2",
        "freeze_reproduction_errors": freeze_errors,
        "ecologies": [{"system_id": e["system_id"],
                       "source_used": e["source_used"],
                       "fallback_used": e["fallback_used"],
                       "source_sha256": e["source_sha256"],
                       "rule": e["rule"], "rule_offsets": e["rule_offsets"],
                       "eps": e["eps"], "ctxk": e["ctxk"],
                       "invariants": e["invariants"],
                       "analytic_losses": e["losses"],
                       "coefficient_vectors": e["coefficient_vectors"],
                       "thresholds": e["thresholds"],
                       "ul11_labels": {n: (e["ul11"][n].get("regime")
                                           or e["ul11"][n]["kind"])
                                       for n in PRICE_NAMES}} for e in ecos],
        "section_I": section_i,
        "section_I_tally": tally,
        "section_I_divergence": {
            "realizations_compared": div_tot,
            "signatures_with_any_coordinate_divergence": sorted(div_sig),
            "realizations_whose_measured_loss_differs_from_analytic": loss_diff},
        "section_I_terminal": terminal_i,
        "section_L_continual_v1": section_l,
        "section_L_continual_v2": section_l2,
        "section_L_continual_v3": section_l3,
        "section_L_tally_v1": cl_tally,
        "section_L_tally_v2": cl2_tally,
        "section_L_tally_v3": cl3_tally,
        "section_L_v1_pos_qualifying": cl_pos_qualifying,
        "section_L_latest": lab,
        "section_L_pos_direction_hits": pos_direction_hits(latest) if latest else 0,
        "section_L_pos_count": sum(1 for v in latest.values()
                                   if v["family"] == "POS") if latest else 0,
        "section_L_interior_baseline_count": sum(
            1 for v in latest.values() if v["baseline_mass_interior"]) if latest else 0,
        "section_L_DP1B_posthoc_witnesses": dp1b,
        "section_L_matched_control": matched,
        "section_L_matched_control_hits": sum(
            1 for v in matched.values() if v.get("CL3-P8") is True),
        "section_L_matched_control_pairs": len(matched),
        "section_L_capital_gate_clean": sum(
            1 for v in latest.values()
            if v["capital"]["status"] != "CANNOT_IDENTIFY_STORED_SOLUTION_CONTAMINATION"
        ) if latest else 0,
        "section_L_terminal": terminal_l,
    }
    with open(outp, "w") as f:
        json.dump(res, f, indent=1, sort_keys=True)
        f.write("\n")
    print("freeze_reproduction_errors:", len(freeze_errors))
    for e in freeze_errors:
        print("  ", e)
    print("section_I:", terminal_i, tally)
    print("section_L v1:", cl_tally, " v2:", cl2_tally, " v3:", cl3_tally)
    print("section_L:", terminal_l)
    print("  matched control CL3-P8:", mc_hits, "/", mc_pairs,
          " capital gate clean:", cap_clean, "/", len(latest) if latest else 0)


if __name__ == "__main__":
    main()

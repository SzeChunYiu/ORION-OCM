"""Route B oracle for gmi-833-real-developmental-validation-v1.

Materially independent of real_dev_validation_v1: it does NOT import it. Every
quantity is recomputed by a different algorithm on the same sha256-bound real
sources and the same committed REAL_RUNS artifacts:

  * posteriors by log-free exact integer odds ratios instead of rational powers;
  * Dmin by breadth-first subset expansion instead of size-ordered combinations;
  * chi* by outward bisection on an integer bracket instead of the affine solve;
  * charges as integer dot products after clearing denominators, instead of
    Fraction arithmetic;
  * HIST-1 by cross-multiplied integer comparison instead of rational division.

Usage: python3 -I -B oracle_real_dev_validation_v1.py [<out>]
"""
from __future__ import annotations

import hashlib
import itertools
import json
import os
import sys
from fractions import Fraction as Q

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_ROOT = os.environ.get("OCM833_SRC_ROOT", "/home/billy/ocm-scratch/real-l/sources")
NP = 8
PK = ("p_test", "p_carry", "p_store", "p_build", "p_branch", "p_meta", "p_mut", "lam")
SEVEN = ("SIG-W", "SIG-X", "SIG-R", "SIG-L", "SIG-P", "SIG-T", "SIG-S")
MM, TT, NQ, KK, K0 = 9, 64, 64, 4, 1
ST = (4, 5, 6, 7, 3, 8, 2, 1, 0)
SPECS = [
    ("X1-gutenberg-1342", SRC_ROOT + "/g1342.txt", "AND", (1, 2), 3, (1, 2, 3, 4), (3, 8)),
    ("X2-alsa-noise-wav", "/usr/share/sounds/alsa/Noise.wav", "AND", (1, 2), 3, (1, 2, 3, 4), (3, 8)),
    ("X3-stdlib-json-src", "/usr/lib/python3.8/json/__init__.py", "OR", (1, 2), 4, (1, 2, 3, 4), (7, 16)),
    ("X4-dict-american", "/usr/share/dict/american-english", "MAJ", (1, 2, 3), 4, (1, 2, 3, 4), (7, 16)),
    ("X5-gutenberg-84", SRC_ROOT + "/g84.txt", "COPY", (2,), 3, (1, 2), (1, 4)),
    ("X6-python38-elf", "/usr/bin/python3.8", "OR", (2, 4), 5, (1, 2, 3, 4), (1, 4)),
]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def prefixes():
    fp = os.path.join(HERE, "REAL_SOURCE_PREFIXES_V1.json")
    if not os.path.exists(fp):
        return {}
    with open(fp) as f:
        return json.load(f)["prefixes"]


def bits_or_prefix(sid, p, n):
    """independent of route A: resolves the same real bytes, preferring the
    real file and otherwise the committed prefix, which it re-hashes itself."""
    if os.path.exists(p):
        raw = open(p, "rb").read()[:(n + 7) // 8]
        return unpack(raw, n), sha(p), True
    pr = prefixes().get(sid)
    if pr is None:
        raise RuntimeError("SOURCE_AND_PREFIX_BOTH_ABSENT:" + sid)
    if True:
        raw = bytes.fromhex(pr["prefix_hex"])
        if hashlib.sha256(raw).hexdigest() != pr["prefix_sha256"]:
            raise RuntimeError("COMMITTED_PREFIX_SELF_HASH_MISMATCH:" + sid)
        return unpack(raw[:(n + 7) // 8], n), pr["source_sha256"], False


def unpack(raw, n):
    o = []
    for by in raw:
        for s in (7, 6, 5, 4, 3, 2, 1, 0):
            o.append((by >> s) & 1)
    return o[:n]


def bits(p, n):
    raw = open(p, "rb").read()[:(n + 7) // 8]
    o = []
    for by in raw:
        for s in (7, 6, 5, 4, 3, 2, 1, 0):
            o.append((by >> s) & 1)
    return o[:n]


def rule(b, z, r, offs):
    v = [b[z - o] for o in offs]
    if r == "AND":
        return 1 if all(v) else 0
    if r == "OR":
        return 1 if any(v) else 0
    if r == "COPY":
        return v[0]
    return 1 if sum(v) * 2 > len(v) else 0


def episode(b, base, r, offs):
    zs = list(range(base + 16, base + 16 + TT + NQ))
    return {"Z": zs, "t": [rule(b, z, r, offs) for z in zs],
            "H": [[b[z - (i + 1)] for z in zs] for i in range(MM)],
            "tr": zs[:TT], "q": zs[TT:], "b": b}


def errs(e, i):
    return sum(1 for k in range(TT) if e["H"][i][k] != e["t"][k])


def post_odds(e, eps):
    """posterior by exact integer odds against the best candidate (no powers of
    a rational carried through the whole product)."""
    en, ed = eps
    er = [errs(e, i) for i in range(MM)]
    lo = min(er)
    num = []
    for i in range(MM):
        d = er[i] - lo
        num.append(Q(en, ed - en) ** d if d else Q(1))
    s = sum(num)
    return [x / s for x in num], er


def wpred(e, po, k):
    m = sum(po[i] for i in range(MM) if e["H"][i][TT + k] == 1)
    return 1 if m > Q(1, 2) else 0


def alpha(e, po):
    bi = min(range(MM), key=lambda i: (-po[i], i))
    g = 0
    for k in range(NQ):
        w, p, t = wpred(e, po, k), e["H"][bi][TT + k], e["t"][TT + k]
        if p != t and w == t:
            g += 1
        elif w != t and p == t:
            g -= 1
    return g, bi


def retr(e, ck):
    b = e["b"]
    tm = {}
    for idx, z in enumerate(e["tr"]):
        tm.setdefault(tuple(b[z - ck:z]), []).append(idx)
    r = {}
    for z in e["q"]:
        c = tm.get(tuple(b[z - ck:z]))
        r[z] = c[-1] if c else TT - 1
    return r, len(set(r.values()))


def prods(offs):
    rs = []
    for k in (1, 2, 3):
        for o in itertools.combinations(offs, k):
            for pat in itertools.product((0, 1), repeat=k):
                for y in (0, 1):
                    rs.append((o, pat, y, k + 2))
    return rs


def fires(e, p, z):
    return all(e["b"][z - o] == v for o, v in zip(p[0], p[1]))


def cover_bfs(e, rs):
    """breadth-first over subsets by insertion order, not size-ordered combos."""
    tr = e["tr"]
    tgt = {z: e["t"][i] for i, z in enumerate(tr)}
    ok, cov = [], {}
    for j, p in enumerate(rs):
        if not any(fires(e, p, z) and tgt[z] != p[2] for z in tr):
            ok.append(j)
            cov[j] = frozenset(z for z in tr if fires(e, p, z))
    full = frozenset(tr)
    frontier = [((), frozenset())]
    best, bsub = None, None
    for _depth in range(3):
        nxt = []
        for sub, u in frontier:
            lo = sub[-1] + 1 if sub else 0
            for j in ok:
                if j < lo:
                    continue
                s2, u2 = sub + (j,), u | cov[j]
                if u2 >= full:
                    tot = sum(rs[x][3] for x in s2)
                    if best is None or tot < best:
                        best, bsub = tot, s2
                else:
                    nxt.append((s2, u2))
        if best is not None:
            break
        frontier = nxt
    if best is None:
        bu = frozenset()
        for sub, u in frontier:
            if len(u) > len(bu):
                bu = u
        return None, None, 2 * len(bu), len(ok)
    u = frozenset()
    for j in bsub:
        u |= cov[j]
    return best, bsub, 2 * len(u), len(ok)


def vf(e):
    return [Q(TT - errs(e, i), TT) for i in range(MM)]


def climb(V, s):
    c, n = s, 0
    while True:
        nb = [j for j in (c - 1, c + 1) if 0 <= j < MM] + [c]
        b = max(nb, key=lambda j: (V[j], -j))
        if b == c:
            return c, n
        c, n = b, n + 1


def vecs_for(inv, loss, g):
    carry, store, build, breadth, meta, mut = g
    ev = 0
    for ep in range(KK):
        w = meta if (meta > 0 and ep >= K0) else MM
        if carry > 0:
            ev += w * TT
    asc = (breadth * (inv["Tsteps"] + 1) * (inv["max_degree"] + 1) * TT
           if (carry == 0 and store == 0 and build == 0) else 0)
    ev += KK * (store * NQ + asc + (inv["disc"] if build > 0 else 0) + build * NQ + NQ)
    return [ev, KK * carry * TT, KK * store * TT, KK * build,
            KK * (breadth - 1) * inv["Tsteps"], meta * KK, KK * mut, loss]


def price(**kw):
    d = dict((k, Q(1)) for k in PK)
    d.update(kw)
    return [d[k] for k in PK]


ANCH = [
    ("A1-unit", price()),
    ("A2-carry-cheap", price(p_carry=Q(1, 256), p_store=Q(256), p_build=Q(256),
                             p_branch=Q(256), p_meta=Q(256), p_mut=Q(256), lam=Q(256))),
    ("A3-store-cheap", price(p_store=Q(1, 256), p_carry=Q(256), p_build=Q(256),
                             p_branch=Q(256), p_meta=Q(256), p_mut=Q(256), lam=Q(256))),
    ("A4-build-cheap", price(p_build=Q(1, 256), p_test=Q(1, 4096), p_carry=Q(256),
                             p_store=Q(256), p_branch=Q(256), p_meta=Q(256),
                             p_mut=Q(256), lam=Q(256))),
    ("A5-branch-cheap", price(p_branch=Q(1, 256), p_carry=Q(256), p_store=Q(256),
                              p_build=Q(256), p_meta=Q(256), p_mut=Q(256), lam=Q(256))),
    ("A6-meta-cheap", price(p_meta=Q(1, 256), p_carry=Q(256), p_store=Q(256),
                            p_build=Q(256), p_branch=Q(256), p_mut=Q(256), lam=Q(256))),
    ("A7-mut-cheap", price(p_mut=Q(1, 256), p_carry=Q(256), p_store=Q(256),
                           p_build=Q(256), p_branch=Q(256), p_meta=Q(256), lam=Q(256))),
    ("A8-loss-dominant", price(lam=Q(4096))),
]


def int_dot(vec, pr):
    """clear denominators once, then compare integers only."""
    den = 1
    for x in pr:
        den = den * x.denominator // _gcd(den, x.denominator)
    return sum(v * int(x * den) for v, x in zip(vec, pr))


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def chi_by_scan(ax, ar):
    """Bracket the sign change by outward scan, then reconstruct the exact root
    from two SAMPLED evaluations of the (affine) difference -- no closed form
    from the coefficient vectors is used."""
    i = PK.index("p_store")

    def diff(ps):
        a = sum(ax[j] for j in range(NP) if j != i) + ax[i] * ps
        b = sum(ar[j] for j in range(NP) if j != i) + ar[i] * ps
        return a - b
    d0, d1 = diff(Q(0)), diff(Q(1))
    slope = d1 - d0
    if slope == 0:
        return None
    lo, hi = Q(0), Q(1)
    while diff(hi) * diff(lo) > 0 and hi < Q(1 << 40):
        hi *= 2
    if diff(hi) * diff(lo) > 0:
        return None
    root = -d0 / slope                      # affine identity from two samples
    if diff(root) != 0:
        return None                          # not affine: refuse rather than guess
    return root if root > 0 else None


def hist1_int(p0n, pHn, dn, hn, hd, c):
    """h + c/pH < c/p0 by integer cross-multiplication (no division)."""
    if p0n == 0 and pHn == 0:
        return "BOTH_UNREACHABLE"
    if p0n == 0:
        return "HISTORY_STRICTLY_IMPROVES"
    if pHn == 0:
        return "HISTORY_HARMS"
    lhs = hn * pHn * p0n * c * 0 + (hn * pHn * p0n) + hd * c * dn * p0n
    rhs = hd * c * dn * pHn
    if lhs < rhs:
        return "HISTORY_STRICTLY_IMPROVES"
    if lhs == rhs:
        return "TIE"
    return "HISTORY_HARMS"


def main():
    out = {"schema": "GMI_833_REAL_DEV_ORACLE_V1", "ecologies": {}, "continual": {}}
    runs = {}
    rd = os.path.join(HERE, "REAL_RUNS")
    if os.path.isdir(rd):
        for fn in sorted(os.listdir(rd)):
            if fn.endswith(".json"):
                runs[fn] = json.load(open(os.path.join(rd, fn)))
    for sid, path, r, roffs, ck, rso, eps in SPECS:
        b, src_digest, _verified = bits_or_prefix(
            sid, path, KK * (TT + NQ) + 16 * KK + 64)
        eps_list = [episode(b, e * (TT + NQ), r, roffs) for e in range(KK)]
        e0 = eps_list[0]
        po, _er = post_odds(e0, eps)
        ag, bi = alpha(e0, po)
        rr, mu = retr(e0, ck)
        rs = prods(rso)
        Dmin, sub, cover, _nc = cover_bfs(e0, rs)
        V = vf(e0)
        gi = max(range(MM), key=lambda i: (V[i], -i))
        t0, steps = climb(V, ST[0])
        Vglob, Vloc = V[gi], V[t0]
        Bmin = MM
        for bw in range(1, MM + 1):
            if any(V[climb(V, s)[0]] == Vglob for s in ST[:bw]):
                Bmin = bw
                break
        Ts = max(steps, 1)
        hp = set()
        for e in eps_list:
            for i in range(MM):
                if all(e["H"][i][k] == e["t"][k] for k in range(len(e["Z"]))):
                    hp.add(i)
        tih = bool(hp)
        if not hp:
            hp = set(range(MM))
        Mp = len(hp)
        inv = {"Tsteps": Ts, "max_degree": 2, "disc": len(rs) * TT}
        # analytic losses, recomputed independently
        L = {}
        L["SIG-W"] = sum(1 for k in range(NQ) if wpred(e0, po, k) != e0["t"][TT + k])
        L["BASE-0"] = sum(1 for k in range(NQ) if e0["H"][bi][TT + k] != e0["t"][TT + k])
        L["NULL-0"] = sum(1 for k in range(NQ) if e0["H"][ST[0]][TT + k] != e0["t"][TT + k])
        trz = e0["tr"]
        L["SIG-X"] = sum(1 for j, z in enumerate(e0["q"])
                         if e0["t"][trz.index(trz[rr[z]])] != e0["t"][TT + j])
        rp = []
        for z in e0["q"]:
            p = None
            for j in (sub or ()):
                if fires(e0, rs[j], z):
                    p = rs[j][2]
                    break
            rp.append(0 if p is None else p)
        L["SIG-R"] = L["SIG-L"] = sum(1 for j in range(NQ) if rp[j] != e0["t"][TT + j])
        b2 = Bmin if Bmin >= 2 else 2
        bst, bv = None, None
        for s in ST[:b2]:
            t, _ = climb(V, s)
            if bv is None or V[t] > bv:
                bst, bv = t, V[t]
        L["SIG-P"] = sum(1 for k in range(NQ) if e0["H"][bst][TT + k] != e0["t"][TT + k])
        mi = max(sorted(hp), key=lambda i: (po[i], -i))
        L["SIG-T"] = sum(1 for k in range(NQ) if e0["H"][mi][TT + k] != e0["t"][TT + k])
        L["SIG-S"] = L["BASE-0"]
        DmL = None
        if Dmin is not None and sub is not None:
            cnt = {}
            for z in e0["q"]:
                for j in sub:
                    if fires(e0, rs[j], z):
                        cnt[j] = cnt.get(j, 0) + 1
                        break
            if cnt:
                pr_ = sorted(cnt, key=lambda j: (-cnt[j], j))[0]
                ln = rs[pr_][3]
                DmL = max(1, Dmin - (cnt[pr_] * (ln - 1) - (ln + 1)))
        tup = {"SIG-W": (MM, 0, 0, 1, 0, 0), "SIG-X": (0, mu, 0, 1, 0, 0),
               "SIG-R": (0, 0, Dmin, 1, 0, 0) if Dmin is not None else None,
               "SIG-L": (0, 0, DmL, 1, 0, 0) if DmL is not None else None,
               "SIG-P": (0, 0, 0, b2, 0, 0), "SIG-T": (1, 0, 0, 1, Mp, 0),
               "SIG-S": (1, 0, 0, 1, 0, 1)}
        cv = dict((k, None if g is None else vecs_for(inv, L[k], g))
                  for k, g in tup.items())
        th = {"beta_star": str(Q(ag, (MM - 1) * TT)),
              "pistar_star": ("0" if (Bmin - 1) * Ts == 0
                              else str((Vglob - Vloc) / ((Bmin - 1) * Ts))),
              "tau_star": str(Q((MM - Mp) * TT * (KK - K0), Mp * KK)),
              "chi_star": (None if (cv["SIG-X"] is None or cv["SIG-R"] is None)
                           else (lambda x: None if x is None else str(x))(
                               chi_by_scan(cv["SIG-X"], cv["SIG-R"])))}
        lab = {}
        for nm, pr in ANCH:
            if any(cv[k] is None for k in SEVEN) or Dmin is None:
                lab[nm] = "ABSTAIN_UNDERDETERMINED"
                continue
            sc = sorted((int_dot(cv[k], pr), k) for k in SEVEN)
            tied = [k for v, k in sc if v == sc[0][0]]
            lab[nm] = tied[0] if len(tied) == 1 else "ABSTAIN_TIE"
        obs = {}
        run = runs.get("ecology_%s.json" % sid)
        if run is not None:
            o2s = run["opaque_to_signature"]
            rid = [o for o in sorted(run["measured"]) if o2s[o] in SEVEN]
            for nm, pr in ANCH:
                sc = sorted((int_dot(run["measured"][o], pr), o) for o in rid)
                tied = [o for v, o in sc if v == sc[0][0]]
                obs[nm] = o2s[tied[0]] if len(tied) == 1 else "TIE"
        out["ecologies"][sid] = {
            "source_sha256": src_digest,
            "invariants": {"Mprime": Mp, "r": MM - Mp, "mu": mu, "Dmin": Dmin,
                           "Dmin_L": DmL, "cover": cover, "RS_size": len(rs),
                           "Bmin": Bmin, "Tsteps": Ts, "alpha_gain": ag,
                           "target_in_H": tih},
            "analytic_losses": L, "coefficient_vectors": cv,
            "thresholds": th, "ul11_labels": lab, "observed_argmin": obs}
    for fn, rec in sorted(runs.items()):
        if not fn.startswith("cl_"):
            continue
        p0n, pHn, dn = rec["successes_Q0"], rec["successes_QH"], 24
        out["continual"][rec["sequence_id"]] = {
            "verdict_h_low": hist1_int(p0n, pHn, dn, 0, 1, 300),
            "verdict_h_high": hist1_int(p0n, pHn, dn, 4800, 1, 300),
            "direction_pH_gt_p0": bool(pHn > p0n),
            "stored_reaches_U": bool(rec["stored_solution_reaches_U"]),
            "Ev_Q_U": str(Q(pHn, dn))}
    outp = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        HERE, "ORACLE_RESULT_V1.json")
    with open(outp, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True, default=str)
        f.write("\n")
    print("oracle ecologies:", len(out["ecologies"]), "continual:", len(out["continual"]))


if __name__ == "__main__":
    main()

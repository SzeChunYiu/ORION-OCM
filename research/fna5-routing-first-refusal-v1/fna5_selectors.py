"""FNA-5/D7 selector arms A2..A6 (conventional parents first, neural last, diagnostic only).

Every arm sees the SAME legal 12-feature surface and the SAME applicable-instance set from
the real index. Fitting uses DEV records only; protected EVAL never feeds back. Each arm
reports its own build work, per-query inference work, and persistent model bytes -- no free
preprocessing anywhere. Python 3.8 stdlib only, deterministic under seed.
"""
from __future__ import annotations

import json
import math
import random
from typing import Dict, List, Optional, Sequence, Tuple

from fna5_world import EXACT_FAMILIES, FAMILIES, VERIFY_WORK, cheapest, derive_seed

RIDGE_LAMBDA = 1e-6
KNN_K = 15
BANDIT_ALPHA = 0.5


def standardize(feats):
    n, d = len(feats), len(feats[0])
    means = [sum(f[j] for f in feats) / n for j in range(d)]
    stds = [max(math.sqrt(sum((f[j] - means[j]) ** 2 for f in feats) / n), 1e-9) for j in range(d)]
    out = [[(f[j] - means[j]) / stds[j] for j in range(d)] for f in feats]
    return out, means, stds


def solve_spd(a, b):
    """Gaussian elimination with partial pivoting for small SPD systems (d <= 13)."""
    n = len(b)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(m[r][col]))
        m[col], m[piv] = m[piv], m[col]
        inv = 1.0 / m[col][col]
        for r in range(col + 1, n):
            f = m[r][col] * inv
            if f:
                for c in range(col, n + 1):
                    m[r][c] -= f * m[col][c]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        s = m[i][n] - sum(m[i][j] * x[j] for j in range(i + 1, n))
        x[i] = s / m[i][i]
    return x


def fallback_expected(q: Query, insts: Sequence[Instance], state) -> float:
    scan = cheapest(insts, q, state, "scan")
    return scan.declared_cost_estimate(q, state) + VERIFY_WORK if scan else 0.0


def decode_family(family, q, insts, state):
    """Family -> cheapest applicable instance of that family, else cheapest exact."""
    cand = cheapest(insts, q, state, family)
    if cand is not None:
        return cand
    return cheapest(insts, q, state, None)


class CostModelArm:
    """A2 -- the Rice-1976 algorithm-selection / portfolio-pivoting parent: per-instance
    ridge cost regression plus binned success-rate estimates on dev; pick argmin predicted
    total cost including the fallback expectation."""

    name = "A2_COST_MODEL"
    eligible = True
    n_bins = 5

    def __init__(self):
        self.beta: Dict[str, List[float]] = {}
        self.bins: Dict[str, Dict] = {}
        self.means: List[float] = []
        self.stds: List[float] = []
        self.build_work = 0

    def fit(self, records):
        work = 0
        d = len(records[0]["query"].features)
        raw = [r["query"].features for r in records]
        z, self.means, self.stds = standardize(raw)
        work += 2 * len(raw) * d
        for op_id in sorted({oid for r in records for oid in r["exec_by_id"]}):
            rows = [(zi, r["exec_by_id"][op_id][0]) for zi, r in zip(z, records)
                    if op_id in r["exec_by_id"]]
            if len(rows) < d + 2:
                continue
            xtx = [[0.0] * (d + 1) for _ in range(d + 1)]
            xty = [0.0] * (d + 1)
            for xi, y in rows:
                xv = [1.0] + xi
                for i in range(d + 1):
                    xty[i] += xv[i] * y
                    for j in range(d + 1):
                        xtx[i][j] += xv[i] * xv[j]
            work += len(rows) * (d + 1) * (d + 1)
            for i in range(d + 1):
                xtx[i][i] += RIDGE_LAMBDA
            self.beta[op_id] = solve_spd(xtx, xty)
            work += (d + 1) ** 3 // 3
        # per-family success bins on (disp, alias) quantile edges from dev
        disps = sorted(r["query"].features[1] for r in records)
        aliass = sorted(r["query"].features[2] for r in records)
        nb = self.n_bins
        self.edges = ([disps[int(len(disps) * (i + 1) / nb) - 1] for i in range(nb - 1)],
                      [aliass[int(len(aliass) * (i + 1) / nb) - 1] for i in range(nb - 1)])
        for fam in FAMILIES:
            hit = {}
            tot = {}
            for r in records:
                key = self._bin(r["query"])
                ks = key
                hit[ks] = hit.get(ks, 0)
                tot[ks] = tot.get(ks, 0)
                for oid, (w, ok) in r["exec_by_id"].items():
                    fam_oid = oid.split(":")[0]
                    if fam_oid == fam:
                        tot[ks] += 1
                        hit[ks] += 1 if ok else 0
            self.bins[fam] = {"hit": hit, "tot": tot}
            work += len(records) * 2
        self.build_work = work
        return work

    def _bin(self, q):
        e1, e2 = self.edges
        i1 = sum(1 for e in e1 if q.features[1] > e)
        i2 = sum(1 for e in e2 if q.features[2] > e)
        return (i1, i2)

    def p_pass(self, fam, q):
        b = self.bins.get(fam)
        if not b:
            return 0.0
        key = self._bin(q)
        tot = b["tot"].get(key, 0)
        hit = b["hit"].get(key, 0)
        if tot >= 10:
            return hit / tot
        allt = sum(b["tot"].values())
        return (sum(b["hit"].values()) / allt) if allt else 0.0

    def choose(self, q, insts, state):
        work = 4
        z = [(q.features[j] - self.means[j]) / self.stds[j] for j in range(len(self.means))]
        work += 2 * len(z)
        fb = fallback_expected(q, insts, state)
        best, best_cost = None, None
        for it in insts:
            beta = self.beta.get(it.op_id)
            xv = [1.0] + z
            pred = sum(b * v for b, v in zip(beta, xv)) if beta else it.declared_cost_estimate(q, state)
            work += 2 * len(xv) + 3
            total = pred + (1.0 - self.p_pass(it.family, q)) * fb
            work += 5
            if best_cost is None or total < best_cost - 1e-9:
                best, best_cost = it, total
        return best, work

    def model_bytes(self):
        return len(json.dumps({"beta": self.beta, "edges": self.edges}, sort_keys=True))


class KnnArm:
    """A3a -- k-NN vote on the standardized legal surface (lazy: build is cheap, inference
    is honestly charged at k-neighbour scan cost per query)."""

    name = "A3A_KNN"
    eligible = True

    def __init__(self, k=KNN_K):
        self.k = k
        self.z: List[List[float]] = []
        self.labels: List[str] = []
        self.build_work = 0

    def fit(self, records):
        raw = [r["query"].features for r in records]
        z, self.means, self.stds = standardize(raw)
        self.z, self.labels = z, [r["oracle_family"] for r in records]
        self.build_work = 2 * len(raw) * len(raw[0])
        return self.build_work

    def choose(self, q, insts, state):
        d = len(self.means)
        zq = [(q.features[j] - self.means[j]) / self.stds[j] for j in range(d)]
        dists = []
        work = d
        for i, z in enumerate(self.z):
            dd = 0.0
            for j in range(d):
                t = z[j] - zq[j]
                dd += t * t
            dists.append((dd, i))
            work += d
        top = sorted(dists, key=lambda t: (t[0], t[1]))[:self.k]
        votes: Dict[str, int] = {}
        for _, i in top:
            votes[self.labels[i]] = votes.get(self.labels[i], 0) + 1
        work += self.k
        fam = max(sorted(votes), key=lambda f: votes[f])
        exact_votes = votes.get("scan", 0) + votes.get("probe", 0)
        if votes[fam] <= exact_votes:  # no plurality over exact -> fall back to exact
            fam = "probe" if any(it.family == "probe" for it in insts) else "scan"
            work += 4
        return decode_family(fam, q, insts, state), work

    def model_bytes(self):
        return len(json.dumps({"n": len(self.z), "k": self.k}, sort_keys=True))


class LogisticArm:
    """A3b -- multinomial logistic regression on the legal surface (family classes)."""

    name = "A3B_LOGISTIC"
    eligible = True
    epochs = 60
    lr = 0.1

    def fit(self, records):
        raw = [r["query"].features for r in records]
        z, self.means, self.stds = standardize(raw)
        y = [FAMILIES.index(r["oracle_family"]) for r in records]
        n, d = len(z), len(z[0])
        c = len(FAMILIES)
        self.w = [[0.0] * d for _ in range(c)]
        self.b = [0.0] * c
        rng = random.Random(derive_seed("logistic"))
        order = list(range(n))
        work = 2 * n * d
        for ep in range(self.epochs):
            rng.shuffle(order)
            lr = self.lr * (0.7 ** (ep // 20))
            for i in order:
                xi, yi = z[i], y[i]
                s = [self.b[k] + sum(self.w[k][j] * xi[j] for j in range(d)) for k in range(c)]
                mx = max(s)
                ex = [math.exp(v - mx) for v in s]
                tot = sum(ex)
                p = [e / tot for e in ex]
                for k in range(c):
                    g = (1.0 if k == yi else 0.0) - p[k]
                    gb = g * lr
                    self.b[k] += gb
                    wk = self.w[k]
                    for j in range(d):
                        wk[j] += gb * xi[j]
                work += c * d * 4
        self.build_work = work
        return work

    def choose(self, q, insts, state):
        d = len(self.means)
        zq = [(q.features[j] - self.means[j]) / self.stds[j] for j in range(d)]
        s = [self.b[k] + sum(self.w[k][j] * zq[j] for j in range(d)) for k in range(len(FAMILIES))]
        work = d * len(FAMILIES) * 2
        mx = max(s)
        ex = [math.exp(v - mx) for v in s]
        tot = sum(ex)
        p = [e / tot for e in ex]
        avail = {it.family for it in insts}
        best_fam, best_p = None, -1.0
        for k, fam in enumerate(FAMILIES):
            if fam in avail and p[k] > best_p + 1e-12:
                best_fam, best_p = fam, p[k]
        work += len(FAMILIES) * 3
        if best_p < 0.5:  # no confident class -> exact family
            best_fam = "probe" if "probe" in avail else "scan"
            work += 2
        return decode_family(best_fam, q, insts, state), work

    def model_bytes(self):
        return len(json.dumps({"w": self.w, "b": self.b}, sort_keys=True))


class TreeArm:
    """A4 -- CART classification tree over family choice; depth <= 3 frozen, min-leaf by
    5-fold CV ON DEV ONLY. Candidate thresholds are dev quantiles (16 per feature)."""

    name = "A4_TREE"
    eligible = True
    max_depth = 3

    def __init__(self):
        self.min_leaf = 16
        self.build_work = 0

    def _fit_node(self, rows, depth):
        """rows: list of (feature_index, z-row, y). Returns nested node dict."""
        work = 0
        labels = [r[2] for r in rows]
        counts: Dict[int, int] = {}
        for y in labels:
            counts[y] = counts.get(y, 0) + 1
        if depth >= self.max_depth or len(rows) < 2 * self.min_leaf or len(counts) == 1:
            leaf = max(sorted(counts), key=lambda k: counts[k])
            return {"leaf": leaf}, work + len(labels)
        d = len(rows[0][1])
        best = None  # (gain, j, thr)
        ent0 = self._entropy(counts, len(labels))
        work += len(labels)
        for j in range(d):
            vals = sorted(set(r[1][j] for r in rows))
            if len(vals) < 2:
                continue
            cand = [vals[int(len(vals) * (q + 1) / 17.0)] for q in range(16) if
                    int(len(vals) * (q + 1) / 17.0) < len(vals)]
            work += len(vals) * 3
            for thr in cand:
                lc: Dict[int, int] = {}
                rc: Dict[int, int] = {}
                for _, z, y in rows:
                    (lc if z[j] <= thr else rc)[y] = (lc if z[j] <= thr else rc).get(y, 0) + 1
                work += len(rows)
                nl, nr = sum(lc.values()), sum(rc.values())
                if nl < self.min_leaf or nr < self.min_leaf:
                    continue
                gain = ent0 - (nl * self._entropy(lc, nl) + nr * self._entropy(rc, nr)) / len(rows)
                if best is None or gain > best[0] + 1e-12:
                    best = (gain, j, thr)
        if best is None:
            leaf = max(sorted(counts), key=lambda k: counts[k])
            return {"leaf": leaf}, work
        _, j, thr = best
        left = [r for r in rows if r[1][j] <= thr]
        right = [r for r in rows if r[1][j] > thr]
        ln, w1 = self._fit_node(left, depth + 1)
        rn, w2 = self._fit_node(right, depth + 1)
        return {"j": j, "thr": thr, "l": ln, "r": rn}, work + w1 + w2

    @staticmethod
    def _entropy(counts, total):
        e = 0.0
        for c in counts.values():
            p = c / total
            e -= p * math.log2(p)
        return e

    def _predict_node(self, node, z):
        while "leaf" not in node:
            node = node["l"] if z[node["j"]] <= node["thr"] else node["r"]
        return node["leaf"]

    def fit(self, records):
        raw = [r["query"].features for r in records]
        z, self.means, self.stds = standardize(raw)
        y = [FAMILIES.index(r["oracle_family"]) for r in records]
        rows = list(zip(range(len(z)), z, y))
        # 5-fold CV on dev over (min_leaf) configs; depth frozen at 3
        rng = random.Random(derive_seed("tree-cv"))
        folds = [[] for _ in range(5)]
        for i, r in enumerate(sorted(rows, key=lambda t: (t[2], t[0]))):
            folds[i % 5].append(r)
        work = 2 * len(z) * len(z[0])
        best_ml, best_acc = None, -1.0
        for ml in (16, 48):
            accs = []
            for f in range(5):
                tr = [r for g in range(5) if g != f for r in folds[g]]
                te = folds[f]
                self.min_leaf = ml
                node, w = self._fit_node(tr, 0)
                work += w
                hit = sum(1 for _, zz, yy in te if self._predict_node(node, zz) == yy)
                accs.append(hit / max(len(te), 1))
                work += len(te) * 4
            acc = sum(accs) / len(accs)
            work += 10
            if acc > best_acc + 1e-12:
                best_ml, best_acc = ml, acc
        self.min_leaf = best_ml
        self.node, w = self._fit_node(rows, 0)
        work += w
        self.build_work = work
        return work

    def choose(self, q, insts, state):
        d = len(self.means)
        zq = [(q.features[j] - self.means[j]) / self.stds[j] for j in range(d)]
        fam = FAMILIES[self._predict_node(self.node, zq)]
        work = d + self.max_depth
        avail = {it.family for it in insts}
        if fam not in avail:
            fam = "probe" if "probe" in avail else "scan"
            work += 2
        return decode_family(fam, q, insts, state), work

    def model_bytes(self):
        return len(json.dumps({"node": self.node, "min_leaf": self.min_leaf}, sort_keys=True))


class LinUcbArm:
    """A5 -- disjoint LinUCB over families, trained on the DEV stream (reward = realized
    savings vs the scan baseline, normalized), then FROZEN. Protected EVAL never feeds back.

    Training executes real choices (charged to build); inference solves nothing: A_inv is
    maintained by rank-1 Sherman-Morrison updates."""

    name = "A5_LINUCB"
    eligible = True

    def __init__(self, alpha=BANDIT_ALPHA):
        self.alpha = alpha
        self.build_work = 0
        self.exec_spent_build = 0

    def _init(self, d):
        self.d = d
        self.A = {f: [[1.0 if i == j else 0.0 for j in range(d)] for i in range(d)]
                  for f in FAMILIES}
        self.Ainv = {f: [row[:] for row in self.A[f]] for f in FAMILIES}
        self.b = {f: [0.0] * d for f in FAMILIES}

    @staticmethod
    def _dot(a, b):
        return sum(x * y for x, y in zip(a, b))

    def _ucb(self, fam, z):
        theta = [self._dot(self.Ainv[fam][i], self.b[fam]) for i in range(self.d)]
        Az = [self._dot(self.Ainv[fam][i], z) for i in range(self.d)]
        bonus = self.alpha * math.sqrt(max(self._dot(z, Az), 0.0))
        return self._dot(theta, z) + bonus

    def _update(self, fam, z, reward):
        Ainv = self.Ainv[fam]
        Az = [self._dot(Ainv[i], z) for i in range(self.d)]
        denom = 1.0 + self._dot(z, Az)
        for i in range(self.d):
            for j in range(self.d):
                self.A[fam][i][j] += z[i] * z[j]
            self.b[fam][i] += reward * z[i]
        for i in range(self.d):
            g = Az[i] / denom
            for j in range(self.d):
                Ainv[i][j] -= g * Az[j]

    def train(self, records, world, execute):
        """Sequential dev stream: pick argmax-UCB among applicable families, observe the
        realized reward. execute(chosen_instance, query) -> (exec_work, passed) is the
        charged execution callback owned by the driver."""
        raw = [r["query"].features for r in records]
        z, self.means, self.stds = standardize(raw)
        self._init(1 + len(z[0]))          # context = [intercept] + z
        work = 2 * len(z) * self.d
        for zi, r in zip(z, records):
            q, insts = r["query"], r["insts"]
            zq = [1.0] + zi
            fams = sorted({it.family for it in insts})
            best_fam, best_u = None, None
            for f in fams:
                u = self._ucb(f, zq)
                work += self.d * self.d * 2
                if best_u is None or u > best_u + 1e-12:
                    best_fam, best_u = f, u
            choice = decode_family(best_fam, q, insts, world["state"])
            exec_work, passed = execute(choice, q)
            self.exec_spent_build += exec_work
            scan = cheapest(insts, q, world["state"], "scan")
            scan_cost = scan.declared_cost_estimate(q, world["state"]) + VERIFY_WORK
            base = scan_cost
            reward = (base - exec_work) / base
            if not passed:                 # a failed attempt then pays the scan fallback
                reward -= scan_cost / base
            self._update(best_fam, zq, max(min(reward, 1.0), -1.0))
            work += self.d * self.d * 2 + 6
        self.build_work = work
        return work

    def fit(self, records):
        raise NotImplementedError("LinUCB trains online via train()")

    def choose(self, q, insts, state):
        """Frozen-model inference: exploitation only (theta'z). The alpha bonus exists to
        drive exploration during the online dev stream; a frozen selector has no trials
        left to run, so argmax-bonus at eval would reward under-exploration itself."""
        zq = [1.0] + [(q.features[j] - self.means[j]) / self.stds[j]
                      for j in range(self.d - 1)]
        fams = sorted({it.family for it in insts})
        best_fam, best_v = None, None
        work = self.d
        for f in fams:
            theta = [self._dot(self.Ainv[f][i], self.b[f]) for i in range(self.d)]
            v = self._dot(theta, zq)
            work += self.d * self.d
            if best_v is None or v > best_v + 1e-12:
                best_fam, best_v = f, v
        return decode_family(best_fam, q, insts, state), work

    def model_bytes(self):
        return len(json.dumps({"A": self.A, "b": self.b}, sort_keys=True))


class MlpArm:
    """A6 -- NEURAL REFERENCE, diagnostic only, never eligible for adoption. One hidden
    layer (12->16->5) trained by plain SGD+momentum on dev. It exists to measure any
    surviving representation gap, not to win anything."""

    name = "A6_NEURAL_REF"
    eligible = False
    epochs = 60
    hidden = 16

    def __init__(self):
        self.build_work = 0

    def fit(self, records):
        raw = [r["query"].features for r in records]
        z, self.means, self.stds = standardize(raw)
        y = [FAMILIES.index(r["oracle_family"]) for r in records]
        n, d = len(z), len(z[0])
        c, h = len(FAMILIES), self.hidden
        rng = random.Random(derive_seed("mlp"))
        self.w1 = [[rng.gauss(0, 0.1) for _ in range(d)] for _ in range(h)]
        self.b1 = [0.0] * h
        self.w2 = [[rng.gauss(0, 0.1) for _ in range(h)] for _ in range(c)]
        self.b2 = [0.0] * c
        vw1 = [[0.0] * d for _ in range(h)]
        vb1 = [0.0] * h
        vw2 = [[0.0] * h for _ in range(c)]
        vb2 = [0.0] * c
        order = list(range(n))
        work = 2 * n * d + (h * d + c * h) * 2
        mom = 0.9
        for ep in range(self.epochs):
            rng.shuffle(order)
            lr = 0.15 * (0.7 ** (ep // 20))
            for i in order:
                xi, yi = z[i], y[i]
                a1 = [self.b1[k] + sum(self.w1[k][j] * xi[j] for j in range(d)) for k in range(h)]
                hh = [math.tanh(v) for v in a1]
                s = [self.b2[k] + sum(self.w2[k][j] * hh[j] for j in range(h)) for k in range(c)]
                mx = max(s)
                ex = [math.exp(v - mx) for v in s]
                tot = sum(ex)
                p = [e / tot for e in ex]
                d2 = [p[k] - (1.0 if k == yi else 0.0) for k in range(c)]
                d1 = [sum(d2[k] * self.w2[k][j] for k in range(c)) * (1.0 - hh[j] ** 2)
                      for j in range(h)]
                for k in range(c):
                    for j in range(h):
                        vw2[k][j] = mom * vw2[k][j] - lr * d2[k] * hh[j]
                        self.w2[k][j] += vw2[k][j]
                    vb2[k] = mom * vb2[k] - lr * d2[k]
                    self.b2[k] += vb2[k]
                for j in range(h):
                    for jj in range(d):
                        vw1[j][jj] = mom * vw1[j][jj] - lr * d1[j] * xi[jj]
                        self.w1[j][jj] += vw1[j][jj]
                    vb1[j] = mom * vb1[j] - lr * d1[j]
                    self.b1[j] += vb1[j]
                work += (h * d + c * h) * 6
        self.build_work = work
        return work

    def choose(self, q, insts, state):
        d = len(self.means)
        zq = [(q.features[j] - self.means[j]) / self.stds[j] for j in range(d)]
        hh = [math.tanh(self.b1[k] + sum(self.w1[k][j] * zq[j] for j in range(d)))
              for k in range(self.hidden)]
        s = [self.b2[k] + sum(self.w2[k][j] * hh[j] for j in range(self.hidden))
             for k in range(len(FAMILIES))]
        work = d * self.hidden * 2 + self.hidden * len(FAMILIES) * 2
        avail = {it.family for it in insts}
        best_fam = max((f for f in FAMILIES if f in avail), key=lambda f: s[FAMILIES.index(f)])
        work += len(FAMILIES)
        return decode_family(best_fam, q, insts, state), work

    def model_bytes(self):
        return len(json.dumps({"w1": self.w1, "w2": self.w2}, sort_keys=True))


def make_null_records(records):
    """Shuffle-equal-n null: destroy the feature->outcome mapping, keep marginals and the
    feasible decision structure. Labels (oracle family) are permuted WITHIN strata sharing
    the same applicable-family set; per-op execution outcomes are permuted within each
    operator's own pool. Nothing outside the conditional structure moves."""
    rng = random.Random(derive_seed("null-perm"))
    out = [dict(r, exec_by_id=dict(r["exec_by_id"])) for r in records]
    strata = {}
    for i, r in enumerate(records):
        key = tuple(sorted({it.family for it in r["insts"]}))
        strata.setdefault(key, []).append(i)
    for key in sorted(strata):
        pool = strata[key]
        labels = [records[i]["oracle_family"] for i in pool]
        rng.shuffle(labels)
        for i, lab in zip(pool, labels):
            out[i]["oracle_family"] = lab
    by_op = {}
    for i, r in enumerate(records):
        for oid, val in r["exec_by_id"].items():
            by_op.setdefault(oid, []).append((i, val))
    for oid in sorted(by_op):
        vals = [v for _, v in by_op[oid]]
        rng.shuffle(vals)
        for (i, _), v in zip(by_op[oid], vals):
            out[i]["exec_by_id"][oid] = v
    return out

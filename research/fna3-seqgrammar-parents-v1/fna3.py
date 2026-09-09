#!/usr/bin/env python3
"""FNA-3 / FNA-D5 (#214): non-neural sequence / grammar parent suite.

Frozen by research/fna3-seqgrammar-parents-v1/FREEZE_FNA3_V1.json BEFORE the first
scored run. Issue #214 section 4 FNA-3 asks whether bounded non-neural sequence
parents (n-gram / PPM / CTW / weighted automata / PCFG / BPE / case memory) own
the next-symbol prediction function at registered scope, and WHERE their
expressivity / data efficiency breaks. These are bounded parents, NOT claimed as
frontier-language replacements.

Task worlds: main's frozen UD EWT r2.14 corpus under
docs/provenance/UD_EWT_CUSTODY_MANIFEST_V1.json (real language, protected test),
plus three seeded synthetic worlds where a generative oracle exists and
expressivity boundaries can be measured. Every world, ladder, salt, metric and
terminal is registered in the freeze.

Stdlib only, Python 3.8, deterministic under the registered seeds. Research-only;
no production source is imported or modified.

Declarations (all in the freeze):
- P4 spectral/Hankel learner: CANNOT_CHECK_NO_STDLIB_SVD; EM-HMM substitute.
- P5 uses a hand-authored rule TEMPLATE; the template is charged prior
  information and counted in the results.
- P2 PPM has no exclusion; P6 charges merge induction; P7 charges index build
  and every window comparison and scores on a declared stride-8 subsample.
- P8 logistic is DIAGNOSTIC ONLY and holds no adoption authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CUSTODY = ROOT / "docs" / "provenance" / "UD_EWT_CUSTODY_MANIFEST_V1.json"
UD_DIR = Path(os.environ.get("FNA3_UD_DIR", str(Path.home() / "ocm-data" / "ud-ewt-r2.14")))

SCHEMA = "ocm.fna.fna3-seqgrammar.v1"
P5_FIT_BLOCKS = 1500  # declared EM fit block cap (pre-run amendment A3)
EPS_FLOOR_P = 2.0 ** -20
LN2 = math.log(2.0)

# ---------------------------------------------------------------- work ledger


class Work(object):
    """Deterministic elementary-operation counter. Charged uniformly: one
    count = one list/dict access, one arithmetic step, or one comparison."""

    __slots__ = ("n",)

    def __init__(self):
        self.n = 0

    def add(self, k=1):
        self.n += k


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def state_digest(obj) -> str:
    return hashlib.sha256(canon(obj).encode("utf-8")).hexdigest()


# ------------------------------------------------------------------- worlds


def _psa_table(seed):
    """Variable-order Markov source over [a,b,c], sparse contexts to depth 3."""
    rng = random.Random(seed)
    alpha = ["a", "b", "c"]
    table = {}

    def rand_dist():
        xs = [rng.random() + 0.05 for _ in alpha]
        s = sum(xs)
        return [x / s for x in xs]

    # depth-3 contexts: only contexts starting with 'a' branch fully (sparse PSA)
    for c1 in alpha:
        table[(c1,)] = rand_dist()
        if c1 == "a":
            for c2 in alpha:
                table[("a", c2)] = rand_dist()
                if c2 == "b":
                    for c3 in alpha:
                        table[("a", "b", c3)] = rand_dist()
    return table


def _psa_next(sym_hist, table, rng):
    for d in (3, 2, 1):
        if d > len(sym_hist):
            continue
        ctx = tuple(sym_hist[-d:])
        if ctx in table:
            p = table[ctx]
            break
    else:
        ctx = ()
        p = table.get((), [1.0 / 3.0] * 3)
    r = rng.random()
    acc = 0.0
    for i, w in enumerate(p):
        acc += w
        if r < acc:
            return i, p
    return len(p) - 1, p


def gen_psa(n_total, seed=2140301):
    """Returns (stream, oracle_fn). Oracle: exact table distribution."""
    table = _psa_table(seed)
    rng = random.Random(seed * 7 + 1)
    alpha = ["a", "b", "c"]
    hist = ["c", "b"]  # fixed burn so the first predictions have a context
    out = []
    for _ in range(n_total):
        idx, _p = _psa_next(hist, table, rng)
        out.append(alpha[idx])
        hist.append(alpha[idx])
    stream = "".join(out)

    def oracle(pos, syms):
        for d in (3, 2, 1):
            if d <= pos:
                ctx = tuple(syms[pos - d:pos])
                if ctx in table:
                    return table[ctx]
        return table.get((), [1.0 / 3.0] * 3)

    return stream, {"alpha": alpha, "oracle": oracle}


def gen_nested(n_total, seed=2140302, d_max=48, p_open=0.72):
    """Stochastic nesting S -> a S b (p_open) | c; depth truncated at d_max.
    Returns (stream, oracle_dict). The oracle tracks exact stack depth."""
    rng = random.Random(seed * 7 + 2)
    out = []
    depth = 0
    last = ""
    for _ in range(n_total):
        # Depth-first law of S -> a S b (p_open) | c: after 'a' the innermost S
        # decides (a/c); after 'c' or 'b' the recursion unwinds (b) until the
        # stack empties; at depth 0 a fresh S decides (a/c). Every depth-0
        # block is therefore exactly a^k c b^k (0 <= k <= d_max) -- the
        # declared grammar's language, no nieces/empty interiors.
        if depth == 0:
            if rng.random() < p_open:
                out.append("a")
                depth = 1
            else:
                out.append("c")
        elif last == "a":
            # innermost S deciding: open again (depth cap) or terminate
            if depth < d_max and rng.random() < p_open:
                out.append("a")
                depth += 1
            else:
                out.append("c")
        else:
            out.append("b")
            depth -= 1
        last = out[-1]
    stream = "".join(out)

    def oracle(pos, syms):
        # exact generator state = pending stack depth + phase (is the
        # innermost S deciding, or is the recursion unwinding?)
        # Exact pending depth: blocks are balanced, so the depth at pos is
        # the MAXIMUM suffix sum of delta(a)=+1, delta(b)=-1, delta(c)=0
        # ending at pos (block starts maximise it; earlier blocks net 0).
        run = 0
        d = 0
        for j in range(pos - 1, -1, -1):
            ch = syms[j]
            if ch == "a":
                run += 1
                if run > d:
                    d = run
            elif ch == "b":
                run -= 1
        if d == 0:
            q = p_open
            return [q, 0.0, 1.0 - q]
        if pos > 0 and syms[pos - 1] == "a":
            # innermost S deciding: open again or terminate with c; at the
            # depth cap termination is forced
            if d < d_max:
                q = p_open
                return [q, 0.0, 1.0 - q]
            return [0.0, 0.0, 1.0]
        # unwinding (last was c or b): deterministic b
        return [0.0, 1.0, 0.0]

    return stream, {"alpha": ["a", "b", "c"], "oracle": oracle}


def gen_lexicon(n_total, seed=2140303):
    """24 multi-char words (2-5 chars, shared internal structure), Zipf word
    frequencies, order-1 Markov over word ids, deterministic word internals."""
    rng = random.Random(seed * 7 + 3)
    chars = ["p", "q", "r", "s", "t", "u", "v"]
    n_words = 24
    words = []
    for i in range(n_words):
        ln = 2 + (i % 4)
        w = []
        for j in range(ln):
            # shared structure: word i uses chars from a rotating neighborhood
            w.append(chars[(i + j) % 4 if j % 2 == 0 else 4 + ((i + j) % 3)])
        words.append("".join(w))
    # Zipf weights over word ids (rank 1 most frequent)
    ranks = list(range(1, n_words + 1))
    zipf = [1.0 / r for r in ranks]
    zs = sum(zipf)
    freq = [z / zs for z in zipf]
    # order-1 Markov over word ids: mixture of independence and a rotation map
    rot = {i: (i + 5) % n_words for i in range(n_words)}
    mix = 0.35
    trans = []
    for i in range(n_words):
        row = [(1.0 - mix) * freq[j] + mix * (1.0 if j == rot[i] else 0.0) for j in range(n_words)]
        trans.append(row)
    out = []
    prev = 0
    while len(out) < n_total:
        r = rng.random()
        acc = 0.0
        nxt = n_words - 1
        for j, w in enumerate(trans[prev]):
            acc += w
            if r < acc:
                nxt = j
                break
        out.append(words[nxt])
        prev = nxt
    stream = "".join(out)[:n_total]

    # oracle: map word-level next distribution onto characters.
    # word_pos[i] = (word TYPE id, offset); types index the 24-word table.
    wid_of = {w: i for i, w in enumerate(words)}
    buf = []
    for w in out:
        for j in range(len(w)):
            buf.append((wid_of[w], j))
        if len(buf) >= n_total:
            break
    word_pos = buf[:n_total]

    alpha = sorted(set(stream))

    def oracle(pos, syms):
        if pos <= 0:
            return [1.0 / len(alpha)] * len(alpha)
        w_id, off = word_pos[pos - 1]
        w = words[w_id]
        if off < len(w) - 1:
            nxt_char = w[off + 1]
        else:
            row = trans[w_id]
            nxt_char = None
        if off < len(w) - 1:
            p = [0.0] * len(alpha)
            p[alpha.index(nxt_char)] = 1.0
            return p
        # next word's first char: mixture distribution over first chars
        row = trans[w_id]
        p = [0.0] * len(alpha)
        for j, wt in enumerate(row):
            if wt > 0:
                p[alpha.index(words[j][0])] += wt
        return p

    return stream, {"alpha": alpha, "oracle": oracle}


# -------------------------------------------------------------- UD custody


class CustodyError(ValueError):
    pass


def ud_verify_file(path: Path, split: str):
    if not CUSTODY.exists():
        raise CustodyError("custody manifest missing: %s" % CUSTODY)
    man = json.loads(CUSTODY.read_text(encoding="utf-8"))
    spec = man["files"].get("en_ewt-ud-%s.conllu" % split)
    if spec is None:
        raise CustodyError("split %s not in manifest" % split)
    data = path.read_bytes()
    if len(data) != spec["bytes"] or hashlib.sha256(data).hexdigest() != spec["sha256"]:
        raise CustodyError("custody sha256 mismatch for %s" % path.name)
    return spec["sha256"]


def ud_conllu_texts(path: Path):
    """Yield sentence texts (misc-joined token surfaces) from a conllu file."""
    texts = []
    toks = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.startswith("#") or not raw.strip():
            if toks:
                texts.append(" ".join(toks))
                toks = []
            continue
        parts = raw.split("\t")
        if parts[0].isdigit():
            toks.append(parts[1])
    if toks:
        texts.append(" ".join(toks))
    return texts


def ud_conllu_tags(path: Path):
    """Yield per-sentence UPOS tag tuples."""
    sents = []
    toks = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.startswith("#") or not raw.strip():
            if toks:
                sents.append(tuple(toks))
                toks = []
            continue
        parts = raw.split("\t")
        if parts[0].isdigit():
            toks.append(parts[3])
    if toks:
        sents.append(tuple(toks))
    return sents


def load_ud_char_world():
    train = UD_DIR / "en_ewt-ud-train.conllu"
    dev = UD_DIR / "en_ewt-ud-dev.conllu"
    test = UD_DIR / "en_ewt-ud-test.conllu"
    digests = {
        "train": ud_verify_file(train, "train"),
        "dev": ud_verify_file(dev, "dev"),
        "test": ud_verify_file(test, "test"),  # PROTECTED: only the frozen
        # evaluator (this function's caller, below) consumes it.
    }
    tr_txt = "\n".join(ud_conllu_texts(train))
    dv_txt = "\n".join(ud_conllu_texts(dev))
    te_txt = "\n".join(ud_conllu_texts(test))
    stream = tr_txt[:1000000]
    scored = te_txt[:100000]
    alpha = sorted(set(stream))
    return stream, scored, alpha, digests, len(dv_txt)


def load_ud_pos_world():
    train = UD_DIR / "en_ewt-ud-train.conllu"
    test = UD_DIR / "en_ewt-ud-test.conllu"
    ud_verify_file(train, "train")
    ud_verify_file(test, "test")
    tr = ud_conllu_tags(train)
    te = ud_conllu_tags(test)
    stream = "_".join("_".join(s) for s in tr)
    stream = stream[:254000]
    scored = "_".join("_".join(s) for s in te)
    alpha = sorted(set(stream)) or ["_"]
    return stream, scored, alpha, len(tr), len(te)


# --------------------------------------------------------------------- arms
#
# Uniform arm interface.
#   fit(stream_alpha_ids, n)   — consume burn-in [0,n); online arms
#                                predict-then-update without scoring; batch
#                                arms fit here (all preparation charged).
#   prob(sym_id, hist_ids)     — predictive probability of the next symbol id
#                                given the id history (hist is a list; the arm
#                                keeps its own state and may assume hist has
#                                advanced by one since the previous call).
#   observe(sym_id, hist_ids)  — online arms only: post-prediction update.
#
# Accuracy is measured over the DECLARED candidate closure (symbols seen in the
# recent context plus the actual symbol) for every arm including the oracle, so
# no arm is favoured; log-loss uses the exact probability of the actual symbol.


class NgramWB(object):
    """P1: interpolated n-gram, Witten-Bell lambda, max order 8."""

    name = "P1_NGRAM_WB_D8"
    kind = "online"

    def __init__(self, alpha, order=8):
        self.m = len(alpha)
        self.order = order
        self.tables = [dict() for _ in range(order + 1)]  # d -> ctx tuple -> [c0..c_{m-1}, N, D]
        self.work = Work()

    def _node(self, d, ctx):
        t = self.tables[d]
        node = t.get(ctx)
        if node is None:
            node = [0.0] * self.m + [0.0, 0.0]
            t[ctx] = node
        return node

    def _p_rec(self, d, ctx, x):
        # returns P(x | ctx of length d) by Witten-Bell interpolation
        if d == 0:
            node = self._node(0, ())
            w = self.work
            w.add(3)
            return (node[x] + 0.5) / (node[self.m] + 0.5 * (self.m + 1))
        node = self._node(d, ctx)
        N = node[self.m]
        D = node[self.m + 1]
        w = self.work
        w.add(6)
        if N == 0:
            return self._p_rec(d - 1, ctx[1:], x)
        lam = N / (N + D) if D > 0 else 1.0
        ml = node[x] / N
        return lam * ml + (1.0 - lam) * self._p_rec(d - 1, ctx[1:], x)

    def prob(self, x, hist):
        d = min(self.order, len(hist))
        return self._p_rec(d, tuple(hist[len(hist) - d:]), x)

    def observe(self, x, hist):
        d = min(self.order, len(hist))
        w = self.work
        w.add(2 * (d + 1))
        for k in range(d + 1):
            ctx = tuple(hist[len(hist) - k:]) if k else ()
            node = self._node(k, ctx)
            if node[x] == 0.0:
                node[self.m + 1] += 1.0
            node[x] += 1.0
            node[self.m] += 1.0

    def unobserve(self, x, hist):
        """Exact inverse of observe (integer counters). Deletes emptied nodes."""
        d = min(self.order, len(hist))
        for k in range(d + 1):
            ctx = tuple(hist[len(hist) - k:]) if k else ()
            t = self.tables[k]
            node = t[ctx]
            node[x] -= 1.0
            if node[x] == 0.0:
                node[self.m + 1] -= 1.0
            node[self.m] -= 1.0
            if node[self.m] == 0.0:
                del t[ctx]

    def fit(self, ids, n):
        for i in range(n):
            self.observe(ids[i], ids[:i])

    def candidates(self, hist):
        out = set()
        for d in (1, 2, 3):
            if d <= len(hist):
                node = self.tables[d].get(tuple(hist[len(hist) - d:]))
                if node:
                    for i in range(self.m):
                        if node[i] > 0:
                            out.add(i)
        return out

    def model_state(self):
        return [sorted([[list(k), v] for k, v in t.items()]) for t in self.tables]


class PPMC(object):
    """P2: PPM escape method C, max order 8, no exclusion (declared)."""

    name = "P2_PPM_C_O8"
    kind = "online"

    def __init__(self, alpha, order=8):
        self.m = len(alpha)
        self.order = order
        self.tables = [dict() for _ in range(order + 1)]
        self.work = Work()

    def _ctx_node(self, d, hist):
        ctx = tuple(hist[len(hist) - d:]) if d else ()
        t = self.tables[d]
        node = t.get(ctx)
        if node is None:
            node = {}
            t[ctx] = node
        return node

    def _escape_seen(self, node, x):
        """Return (prob, is_escape) at this order."""
        N = 0
        esc = 0
        seen = False
        cx = 0
        for k, v in node.items():
            N += v
            esc += 1
            if k == x:
                seen = True
                cx = v
        self.work.add(2 * esc + 4)
        if seen:
            return cx / (N + esc), False
        if N == 0:
            return 1.0, True  # empty context: escape with full weight
        return esc / (N + esc), True

    def prob(self, x, hist):
        d = min(self.order, len(hist))
        w = 1.0
        for o in range(d, 0, -1):
            node = self._ctx_node(o, hist)
            p, esc = self._escape_seen(node, x)
            if not esc:
                return w * p
            w *= p
        node = self._ctx_node(0, hist)
        p, esc = self._escape_seen(node, x)
        if not esc:
            return w * p
        # order-0 escape falls through to uniform over the full alphabet
        return w / self.m

    def observe(self, x, hist):
        d = min(self.order, len(hist))
        self.work.add(d + 2)
        for k in range(d + 1):
            node = self._ctx_node(k, hist)
            node[x] = node.get(x, 0) + 1

    def unobserve(self, x, hist):
        """Exact inverse of observe. Deletes emptied symbols and contexts."""
        d = min(self.order, len(hist))
        for k in range(d + 1):
            ctx = tuple(hist[len(hist) - k:]) if k else ()
            t = self.tables[k]
            node = t[ctx]
            c = node.get(x, 0) - 1
            if c <= 0:
                node.pop(x, None)
            else:
                node[x] = c
            if not node:
                del t[ctx]

    def fit(self, ids, n):
        for i in range(n):
            self.observe(ids[i], ids[:i])

    def candidates(self, hist):
        out = set()
        for d in (1, 2, 3):
            if d <= len(hist):
                node = self.tables[d].get(tuple(hist[len(hist) - d:]))
                if node:
                    out.update(node.keys())
        return out

    def model_state(self):
        return [sorted((list(k), sorted(v.items())) for k, v in t.items()) for t in self.tables]


def _lae(a, b):
    """log(exp(a)+exp(b)) in floats, deterministic."""
    if a < b:
        a, b = b, a
    d = b - a
    if d < -700.0:
        return a
    return a + math.log1p(math.exp(d))


class CTW(object):
    """P3: exact Context Tree Weighting, KT / Dirichlet(1/2) per node, mixture
    1/2 estimate : 1/2 children-product, depth 12, log domain, lazy children.

    Willems, Shtarkov & Tjalkens, `The Context-Tree Weighting Method: Basic
    Properties' (IEEE Trans. Information Theory, 1995); KT estimator from
    Krichevsky & Trofimov 1981. General alphabet: Dirichlet(1/2,...,1/2).
    Node value: [counts_dict, n, pe_log, pc_log, pw_log];
    pw = 0.5*exp(pe) + 0.5*exp(pc); pc = sum of children pw (unseen child = 0).
    """

    name = "P3_CTW_KT_D12"
    kind = "online"

    def __init__(self, alpha, depth=12):
        self.m = len(alpha)
        self.depth = depth
        self.nodes = {(): [{}, 0.0, 0.0, 0.0, 0.0]}
        self.work = Work()

    def _path(self, hist):
        D = min(self.depth, len(hist))
        path = [()]
        for k in range(1, D + 1):
            path.append(tuple(hist[len(hist) - k:]))
        return path  # shallowest (root) first

    def _node(self, ctx):
        node = self.nodes.get(ctx)
        if node is None:
            node = [{}, 0.0, 0.0, 0.0, 0.0]
            self.nodes[ctx] = node
        return node

    def _mix(self, ctx, pe, pc):
        """CTW node mixture: full-depth contexts are LEAVES (pure KT); internal
        nodes mix 1/2 the KT estimate with 1/2 the children product."""
        if len(ctx) >= self.depth:
            return pe
        return _lae(pe, pc) - LN2

    def simulate(self, x, hist):
        """Predictive probability of x without committing the update."""
        path = self._path(hist)
        w = self.work
        w.add(6 * len(path))
        # deepest first: prospective delta of each child propagates into parent pc
        deltas = [0.0] * len(path)
        for i in range(len(path) - 1, -1, -1):
            ctx = path[i]
            node = self._node(ctx)
            cd, n, pe, pc, pw = node
            cx = cd.get(x, 0)
            new_pe = pe + math.log((cx + 0.5) / (n + 0.5 * self.m))
            child_delta = deltas[i + 1] if i + 1 < len(path) else 0.0
            new_pc = pc + child_delta
            new_pw = self._mix(ctx, new_pe, new_pc)
            deltas[i] = new_pw - pw
        return math.exp(deltas[0]) if deltas[0] > -700.0 else 0.0

    def observe(self, x, hist):
        self.commit(x, hist)

    def commit(self, x, hist):
        path = self._path(hist)
        w = self.work
        w.add(8 * len(path))
        child_delta = 0.0
        for i in range(len(path) - 1, -1, -1):
            ctx = path[i]
            node = self._node(ctx)
            cd, n, pe, pc, pw = node
            cx = cd.get(x, 0)
            cd[x] = cx + 1
            n += 1.0
            pe = pe + math.log((cx + 0.5) / (n - 1.0 + 0.5 * self.m))
            pc = pc + child_delta
            new_pw = self._mix(ctx, pe, pc)
            child_delta = new_pw - pw
            self.nodes[ctx] = [cd, n, pe, pc, new_pw]

    def prob(self, x, hist):
        return self.simulate(x, hist)

    def fit(self, ids, n):
        for i in range(n):
            self.commit(ids[i], ids[:i])

    def unobserve(self, x, hist):
        """Exact inverse on the sufficient statistic (integer counts); emptied
        nodes are deleted. Float caches pe/pc/pw are then RECOMPUTED from the
        counts with the lgamma-exact KT closed form (mathematically identical
        to the incremental product), so state digests (counts-only, see
        model_state) restore exactly and prediction continues correctly."""
        path = self._path(hist)
        for ctx in path:
            node = self.nodes.get(ctx)
            cd, n, pe, pc, pw = node
            cx = cd.get(x, 0)
            if cx <= 0:
                raise ValueError("unobserve underflow at %r" % (ctx,))
            if cx == 1:
                del cd[x]
            else:
                cd[x] = cx - 1
            if n - 1.0 <= 0.0 and not cd and ctx != ():
                del self.nodes[ctx]
            else:
                self.nodes[ctx] = [cd, n - 1.0, pe, pc, pw]
        self._recompute_caches()

    def _recompute_caches(self):
        m = self.m
        half = 0.5 * m
        lg_half = math.lgamma(half)
        by_depth = {}
        for ctx in self.nodes:
            by_depth.setdefault(len(ctx), []).append(ctx)
        for depth in sorted(by_depth, reverse=True):
            for ctx in by_depth[depth]:
                cd, n, _pe, _pc, _pw = self.nodes[ctx]
                pe = math.lgamma(n + half) - lg_half
                for cx in cd.values():
                    pe -= math.lgamma(cx + 0.5) - math.lgamma(0.5)
                pc = 0.0
                for sym in range(m):
                    child = self.nodes.get(ctx + (sym,))
                    if child is not None:
                        pc += child[4]
                self.nodes[ctx] = [cd, n, pe, pc, self._mix(ctx, pe, pc)]
                self.work.add(6 * (1 + len(cd)))

    def candidates(self, hist):
        out = set()
        for k in (1, 2, 3):
            if k <= len(hist):
                node = self.nodes.get(tuple(hist[len(hist) - k:]))
                if node:
                    out.update(node[0].keys())
        return out

    def model_state(self):
        flat = {}
        for ctx, (cd, n, pe, pc, pw) in self.nodes.items():
            flat["|".join(str(c) for c in ctx)] = [sorted(cd.items()), n]
        return flat


class HMMEM(object):
    """P4: weighted automaton parent — k-state HMM by Baum-Welch EM (batch).

    The spectral/Hankel learner is CANNOT_CHECK_NO_STDLIB_SVD (no stdlib SVD);
    this EM-HMM is the declared bounded substitute. Init seeded, 10 iterations
    CAP with deterministic early stop at relative LL gain < 1e-6. Frozen at
    eval; filtering continues on the scored region without parameter updates.
    """

    name = "P4_WFA_EM"
    kind = "batch"

    def __init__(self, alpha, k=8, iters=10, seed=2140354):
        self.m = len(alpha)
        self.k = k
        self.iters = iters
        self.rng = random.Random(seed)
        self.work = Work()
        self.A = None
        self.B = None
        self.pi = None

    def _rand_stochastic(self, rows, cols):
        M = []
        for _ in range(rows):
            xs = [self.rng.random() + 0.01 for _ in range(cols)]
            s = sum(xs)
            M.append([v / s for v in xs])
        return M

    def _forward(self, ids):
        k, m = self.k, self.m
        A, B, pi = self.A, self.B, self.pi
        work = self.work
        T = len(ids)
        alphas = []
        scales = []
        a = [pi[i] * B[i][ids[0]] for i in range(k)]
        s = sum(a)
        a = [v / s for v in a]
        alphas.append(a)
        scales.append(s)
        work.add(4 * k + 2)
        for t in range(1, T):
            prev = alphas[-1]
            a = []
            for j in range(k):
                acc = 0.0
                Aj = [A[i][j] for i in range(k)]
                for i in range(k):
                    acc += prev[i] * Aj[i]
                a.append(acc * B[j][ids[t]])
            s = sum(a)
            a = [v / s for v in a]
            alphas.append(a)
            scales.append(s)
            work.add(4 * k * k)
        return alphas, scales

    def _backward(self, ids, scales):
        k = self.k
        A, B = self.A, self.B
        T = len(ids)
        betas = [None] * T
        betas[T - 1] = [1.0] * k
        for t in range(T - 2, -1, -1):
            b = []
            for i in range(k):
                acc = 0.0
                for j in range(k):
                    acc += A[i][j] * B[j][ids[t + 1]] * betas[t + 1][j]
                b.append(acc / scales[t + 1])
            betas[t] = b
            self.work.add(4 * k * k)
        return betas

    def fit(self, ids, n):
        ids = ids[:n]
        k, m = self.k, self.m
        self.A = self._rand_stochastic(k, k)
        self.B = self._rand_stochastic(k, m)
        self.pi = self._rand_stochastic(1, k)[0]
        prev_ll = None
        iters_used = 0
        for it in range(self.iters):
            alphas, scales = self._forward(ids)
            ll = sum(math.log(max(s, 1e-300)) for s in scales)
            betas = self._backward(ids, scales)
            T = len(ids)
            g = []
            for t in range(T):
                a, b = alphas[t], betas[t]
                s = sum(a[i] * b[i] for i in range(k))
                g.append([a[i] * b[i] / s for i in range(k)])
            A_num = [[0.0] * k for _ in range(k)]
            A_den = [0.0] * k
            B_num = [[0.0] * m for _ in range(k)]
            B_den = [0.0] * k
            for t in range(T - 1):
                gt = g[t]
                gt1 = g[t + 1]
                x1 = ids[t + 1]
                for i in range(k):
                    A_den[i] += gt[i]
                    Ai = A_num[i]
                    for j in range(k):
                        Ai[j] += gt[i] * self.A[i][j] * self.B[j][x1] * betas[t + 1][j] / scales[t + 1]
            for t in range(T):
                gt = g[t]
                xt = ids[t]
                for i in range(k):
                    B_den[i] += gt[i]
                    B_num[i][xt] += gt[i]
            self.pi = [g[0][i] for i in range(k)]
            sp = sum(self.pi) or 1.0
            self.pi = [v / sp for v in self.pi]
            for i in range(k):
                dA = A_den[i]
                self.A[i] = [(v + 1e-9) / (dA + k * 1e-9) for v in A_num[i]]
                dB = B_den[i]
                self.B[i] = [(v + 1e-9) / (dB + m * 1e-9) for v in B_num[i]]
            self.work.add(T * 8 * k * k)
            iters_used = it + 1
            if prev_ll is not None and abs(ll - prev_ll) < 1e-6 * max(1.0, abs(prev_ll)):
                break
            prev_ll = ll
        self.iters_used = iters_used
        self.filter_state = [v for v in self.pi]
        self._filter_consume(ids)

    def _filter_consume(self, ids):
        """Continue filtering (no parameter update) over given ids."""
        k = self.k
        for x in ids:
            a = self.filter_state
            new = []
            for j in range(k):
                acc = 0.0
                for i in range(k):
                    acc += a[i] * self.A[i][j]
                new.append(acc * self.B[j][x])
            s = sum(new) or 1e-300
            self.filter_state = [v / s for v in new]
            self.work.add(4 * k * k)

    def prob(self, x, hist):
        """P(x_t) from the current filter state (parameters frozen)."""
        k = self.k
        a = self.filter_state
        acc = 0.0
        for i in range(k):
            acc += a[i] * self.B[i][x]
        self.work.add(2 * k)
        return acc

    def observe(self, x, hist):
        self._filter_consume([x])

    def candidates(self, hist):
        return None  # full-distribution arm (small declared alphabets only)

    def model_state(self):
        return {"A": self.A, "B": self.B, "pi": self.pi}


class PCFGEM(object):
    """P5: bounded PCFG induction — frozen hand-authored rule template,
    probabilities by inside-outside EM, prefix probabilities by relaxed
    probabilistic Earley (Stolcke 1995). Batch arm: parameters frozen at eval.

    Scope: W2_NESTED only. Receives the DECLARED depth-0 constituent-block
    gift (fit and score); every other arm sees the raw stream.
    Template (8 rules, 3 nonterminals S,T,W; terminals a,b,c):
        r0 S->a T, r1 T->S b, r2 S->c  (can derive the true nesting language)
        r3 S->S S, r4 S->b W, r5 W->S a, r6 S->a S, r7 S->b S  (distractors)
    """

    name = "P5_PCFG_EM"
    kind = "batch"

    def _rules(self):
        S, T, W = 0, 1, 2
        a, b, c = self._tid["a"], self._tid["b"], self._tid["c"]
        return [
            (S, "tN", a, T),
            (T, "Nt", S, b),
            (S, "t", c, None),
            (S, "NN", S, S),
            (S, "tN", b, W),
            (W, "Nt", S, a),
            (S, "tN", a, S),
            (S, "tN", b, S),
        ]

    def __init__(self, alpha, iters=60, seed=2140356):
        self.m = len(alpha)
        self._tid = {s: i for i, s in enumerate(alpha)}
        self.rules = self._rules()
        self.rng = random.Random(seed)
        self.work = Work()
        self.iters = iters
        acc = {}
        for lhs, _sh, _a1, _a2 in self.rules:
            acc.setdefault(lhs, []).append(self.rng.random() + 0.05)
        self.w = []
        pos = {}
        for lhs, _sh, _a1, _a2 in self.rules:
            p = pos.get(lhs, 0)
            s = sum(acc[lhs])
            self.w.append(acc[lhs][p] / s)
            pos[lhs] = p + 1
        self.prior_rule_count = len(self.rules)  # charged hand-authored prior

    # ---- inside/outside for EM fitting on complete S-rooted strings.
    # beta[j][nt][i] = inside of span sent[i:j] labeled nt.
    def _inside(self, sent):
        n = len(sent)
        R = len(self.rules)
        w = self.w
        beta = [[[0.0] * n for _ in range(3)] for _ in range(n + 1)]
        work = self.work
        for i in range(n):
            for r in range(R):
                lhs, sh, a1, _a2 = self.rules[r]
                if sh == "t" and sent[i] == a1:
                    beta[i + 1][lhs][i] += w[r]
                    work.add(2)
        for length in range(2, n + 1):
            for i in range(0, n - length + 1):
                j = i + length
                cell = beta[j]
                for r in range(R):
                    lhs, sh, a1, a2 = self.rules[r]
                    if sh == "tN" and sent[i] == a1:
                        cell[lhs][i] += w[r] * cell[a2][i + 1]
                        work.add(3)
                    elif sh == "Nt" and sent[j - 1] == a2:
                        cell[lhs][i] += w[r] * beta[j - 1][a1][i]
                        work.add(3)
                    elif sh == "NN":
                        acc = 0.0
                        for k in range(i + 1, j):
                            acc += beta[k][a1][i] * cell[a2][k]
                        cell[lhs][i] += w[r] * acc
                        work.add(2 * (j - i))
        return beta

    # out[j][nt][i] = outside of span sent[i:j] labeled nt; base out[n][0][0]=1
    # Pull formulation: reads only strictly longer spans' outside values,
    # which are final because lengths are processed descending.
    def _outside(self, sent, beta):
        n = len(sent)
        w = self.w
        rules = self.rules
        out = [[[0.0] * n for _ in range(3)] for _ in range(n + 1)]
        work = self.work
        for length in range(n, 0, -1):
            for i in range(0, n - length + 1):
                j = i + length
                for nt in range(3):
                    if i == 0 and j == n and nt == 0:
                        out[j][nt][i] = 1.0
                        work.add(1)
                        continue
                    acc = 0.0
                    for r in range(len(rules)):
                        lhs, sh, a1, a2 = rules[r]
                        if sh == "tN" and a2 == nt and i > 0 and sent[i - 1] == a1:
                            acc += out[j][lhs][i - 1] * w[r]
                            work.add(3)
                        elif sh == "Nt" and a1 == nt and j < n and sent[j] == a2:
                            acc += out[j + 1][lhs][i] * w[r]
                            work.add(3)
                        elif sh == "NN":
                            if a1 == nt:
                                for j2 in range(j + 1, n + 1):
                                    o2 = out[j2][lhs][i]
                                    if o2:
                                        acc += o2 * w[r] * beta[j2][a2][j]
                            if a2 == nt:
                                for i0 in range(0, i):
                                    o2 = out[j][lhs][i0]
                                    if o2:
                                        acc += o2 * w[r] * beta[i][a1][i0]
                            work.add(2)
                    out[j][nt][i] = acc
        return out

    def _expected_counts(self, sent, beta, out):
        R = len(self.rules)
        w = self.w
        n = len(sent)
        counts = [0.0] * R
        work = self.work
        for r in range(R):
            lhs, sh, a1, a2 = self.rules[r]
            acc = 0.0
            if sh == "t":
                for i in range(n):
                    if sent[i] == a1:
                        acc += out[i + 1][lhs][i] * w[r]
                        work.add(2)
            elif sh == "tN":
                for i in range(n):
                    if sent[i] == a1 and i + 1 < n + 1:
                        for j in range(i + 2, n + 1):
                            acc += out[j][lhs][i] * w[r] * beta[j][a2][i + 1]
                            work.add(3)
            elif sh == "Nt":
                for j in range(2, n + 1):
                    if sent[j - 1] == a2:
                        for i in range(0, j - 1):
                            acc += out[j][lhs][i] * w[r] * beta[j - 1][a1][i]
                            work.add(3)
            else:  # NN
                for i in range(n):
                    for k in range(i + 1, n):
                        for j in range(k + 1, n + 1):
                            acc += out[j][lhs][i] * w[r] * beta[k][a1][i] * beta[j][a2][k]
                            work.add(4)
            counts[r] = acc
        return counts

    def fit(self, ids, n):  # ids unused; blocks are the declared input
        tid = self._tid
        blocks = [[tid[c] for c in b if c in tid]
                  for b in self.blocks[-P5_FIT_BLOCKS:]]  # pre-run amendment A3
        rules = self.rules
        prev_ll = None
        iters_used = 0
        for it in range(self.iters):
            ll = 0.0
            num = [0.0] * len(rules)
            for sent in blocks:
                if not sent or len(sent) > 128:
                    continue
                beta = self._inside(sent)
                P = beta[len(sent)][0][0]
                if P <= 1e-300:
                    continue
                ll += math.log(P)
                out = self._outside(sent, beta)
                cnt = self._expected_counts(sent, beta, out)
                for r in range(len(rules)):
                    num[r] += cnt[r]
            # M-step, normalised per lhs with smoothing
            den = {}
            for r in range(len(rules)):
                den.setdefault(rules[r][0], 0.0)
                den[rules[r][0]] += num[r]
            for r in range(len(rules)):
                self.w[r] = (num[r] + 1e-9) / (den[rules[r][0]] + 1e-9 * 3)
            iters_used = it + 1
            if prev_ll is not None and abs(ll - prev_ll) < 1e-6 * max(1.0, abs(prev_ll)):
                break
            prev_ll = ll
        self.iters_used = iters_used

    # ---- Earley prefix probabilities (Stolcke 1995).
    # Per-position charts: charts[k] maps (rule, dot, start) -> alpha after
    # consuming k symbols of the block. Every state in charts[k] accounts for
    # a partial derivation that has generated exactly the first k symbols, so
    # the prefix probability is rho_k = sum of charts[k] and the chain-rule
    # predictive probability is P(x_k | x_<k) = rho_k / rho_{k-1}.
    # Each position is stabilised to a fixpoint by full-recompute Jacobi
    # sweeps (contributions are recomputed from the current chart each sweep,
    # never re-accumulated), which handles the left-recursive S->SS rule.
    def _rhs(self, r):
        lhs, sh, a1, a2 = self.rules[r]
        if sh == "tN":
            return (("t", a1), ("N", a2))
        if sh == "Nt":
            return (("N", a1), ("t", a2))
        if sh == "t":
            return (("t", a1),)
        return (("N", a1), ("N", a2))

    def _rhs_table(self):
        return [self._rhs(r) for r in range(len(self.rules))]

    def _stabilize(self, k, seeds):
        """Jacobi fixpoint at position k over (alpha, beta) pairs per state.
        alpha = P(path to the partial derivation, outer context included);
        beta  = P(inner yield of the rule so far, context-free). Predictor
        grows alpha by alpha*w(rule); completer advances waiters by
        alpha(waiter)*beta(complete) and beta(waiter)*beta(complete) -- the
        completed span's alpha carries waiter-side context and must NOT be
        reused (Stolcke 1995)."""
        rules = self.rules
        w = self.w
        rt = self.rhs_tab
        chart = {s: list(v) for s, v in seeds.items()}
        for _sweep in range(200):
            # Jacobi: new = f(previous iterate), where f anchors every state at
            # its SEED value plus freshly recomputed predictor/completer mass.
            # Anchoring at the previous iterate instead would accumulate every
            # sweep and blow up (caught by the prefix-probability test).
            new = {s: list(v) for s, v in seeds.items()}
            # predictor: state waiting for nonterminal X at position k
            for (r, dot, st), v in chart.items():
                a = v[0]
                if a <= 0.0:
                    continue
                rhs = rt[r]
                if dot < len(rhs) and rhs[dot][0] == "N":
                    X = rhs[dot][1]
                    for r3 in self.by_lhs[X]:
                        tgt = (r3, 0, k)
                        tv = new.get(tgt)
                        if tv is None:
                            tv = [0.0, 1.0]  # fresh dot-0 state: beta = 1
                            new[tgt] = tv
                        tv[0] += a * w[r3]
                        self.work.add(2)
            # completer: complete state (X spanning st..k) advances waiters of X.
            # Waiters live at the completed span's START position; source charts
            # from earlier positions are already converged (read-only there).
            for (r, dot, st), v in chart.items():
                a, b = v[0], v[1]
                if a <= 0.0 or dot < len(rt[r]):
                    continue
                X = rules[r][0]
                src_c = chart if st == k else self.charts[st]
                for (r2, d2, s2), v2 in src_c.items():
                    rhs2 = rt[r2]
                    if d2 < len(rhs2) and rhs2[d2][0] == "N" and rhs2[d2][1] == X and v2[0] > 0.0:
                        tgt = (r2, d2 + 1, s2)
                        tv = new.get(tgt)
                        if tv is None:
                            tv = [0.0, 0.0]
                            new[tgt] = tv
                        tv[0] += v2[0] * b
                        # the waiting rule's own weight enters beta at ITS
                        # completion (d2+1 == len(rhs2)); b already carries the
                        # completed child's own weight
                        tv[1] += v2[1] * b * (w[r2] if d2 + 1 == len(rhs2) else 1.0)
                        self.work.add(3)
            delta = 0.0
            for s in new:
                tv, cv = new[s], chart.get(s)
                if cv is None:
                    d = abs(tv[0]) + abs(tv[1])
                else:
                    d = abs(tv[0] - cv[0]) + abs(tv[1] - cv[1])
                if d > delta:
                    delta = d
            chart = new
            if delta < 1e-14:
                break
        self.charts[k] = chart
        return chart

    def _pending_mass(self, chart):
        """Prefix probability mass: alpha summed over states whose next rhs
        item is a TERMINAL, plus complete ROOT states (a derivation that
        finished with exactly this yield has no pending item). With no epsilon
        rules each partial derivation of the prefix contributes via exactly
        one such frontier state (Stolcke 1995), so the ratios give exact
        chain-rule conditionals P(x_k | x_<k)."""
        rt = self.rhs_tab
        tot = 0.0
        for (r, dot, st), v in chart.items():
            rhs = rt[r]
            if dot < len(rhs):
                if rhs[dot][0] == "t":
                    tot += v[0]
            elif st == 0 and self.rules[r][0] == 0:
                tot += v[0]  # complete root: derivation finished with this yield
        return tot

    def reset_block(self):
        self.rhs_tab = self._rhs_table()
        self.by_lhs = {}
        for r, rule in enumerate(self.rules):
            self.by_lhs.setdefault(rule[0], []).append(r)
        seeds = {}
        s_tot = sum(self.w[r] for r in self.by_lhs.get(0, ()))
        for r in self.by_lhs.get(0, ()):  # S rules seeded by an implicit root;
            # the block IS one S constituent, so the root renormalises S to 1
            seeds[(r, 0, 0)] = [self.w[r] / max(s_tot, 1e-300), 1.0]
        self.charts = [None]  # position 0 stabilised below
        self.charts[0] = {}
        self._stabilize(0, seeds)
        self.rho = self._pending_mass(self.charts[0])

    def _scan_symbol(self, y):
        """Scan terminal y: charts[k] -> charts[k+1]; returns the new rho."""
        k = len(self.charts) - 1
        rt = self.rhs_tab
        w = self.w
        seeds = {}
        for (r, dot, st), v in self.charts[k].items():
            rhs = rt[r]
            if dot < len(rhs) and rhs[dot] == ("t", y):
                tgt = (r, dot + 1, st)
                tv = seeds.get(tgt)
                if tv is None:
                    tv = [0.0, 0.0]
                    seeds[tgt] = tv
                tv[0] += v[0]
                # scanning the FINAL rhs item completes the rule: its own
                # weight enters beta there (and only there)
                tv[1] += v[1] * (w[r] if dot + 1 == len(rhs) else 1.0)
            self.work.add(2)
        self.charts.append(None)
        chart = self._stabilize(k + 1, seeds)
        return self._pending_mass(chart)

    def prob(self, x, hist=None):
        rho2 = self._scan_symbol(x)
        p = rho2 / max(self.rho, 1e-300)
        self.rho = rho2
        return p

    def peek(self, y):
        """Non-destructive branch: prefix probability ratio if y came next."""
        saved = (list(self.charts), self.rho)  # list copy: scan appends in place
        p = self.prob(y)
        self.charts, self.rho = saved
        return p

    def observe(self, x, hist=None):
        return None

    def candidates(self, hist):
        return None  # full-dist via peek over the small alphabet

    def model_state(self):
        return {"w": self.w}


class BPEPPM(object):
    """P6: BPE segmentation (frozen 200-merge budget) + PPM order 4 over the
    unit stream. Merge induction fully charged. Buffered per word (W4,
    whitespace-delimited -- real surface structure) or per 8-char chunk (W3,
    declared implementation device). Loss is normalised per CHARACTER so it is
    commensurable with the character-level arms; the buffering lag is inherent
    to the parent and declared."""

    name = "P6_BPE_PPM"
    kind = "online-buffered"

    def __init__(self, alpha, merges=200, chunk=8, ppm_order=4):
        self.alpha = list(alpha)
        self.merges_budget = merges
        self.chunk = chunk
        self.ppm_order = ppm_order
        self.ppm = None
        self.work = Work()
        self.merges_used = 0
        self._word_mode = False

    def fit(self, ids, n):
        w = self.work
        s = "".join(self.alpha[i] for i in ids[:n])
        w.add(2 * len(s))
        self._word_mode = any(c.isspace() for c in s)
        if self._word_mode:
            # word mode: whitespace chars are single-unit tokens
            toks = []
            cur = []
            for ch in s:
                if ch.isspace():
                    if cur:
                        toks.append("".join(cur))
                        cur = []
                    toks.append(ch)
                else:
                    cur.append(ch)
            if cur:
                toks.append("".join(cur))
        else:
            toks = [s[i:i + self.chunk] for i in range(0, len(s), self.chunk)]
        freq = {}
        for t in toks:
            freq[t] = freq.get(t, 0) + 1
        w.add(3 * len(toks))
        order = []
        for _ in range(self.merges_budget):
            pairs = {}
            for t, f in freq.items():
                syms = list(t)
                for i in range(len(syms) - 1):
                    key = (syms[i], syms[i + 1])
                    pairs[key] = pairs.get(key, 0) + f
            w.add(2 * sum(len(t) for t in freq))
            if not pairs:
                break
            bc = max(pairs.values())
            cands = sorted(k for k, v in pairs.items() if v == bc)
            pair = cands[0]
            if bc < 2:
                break
            order.append(pair)
            newfreq = {}
            a, b = pair
            ab = a + b
            for t, f in freq.items():
                syms = list(t)
                outl = []
                i = 0
                while i < len(syms):
                    if i < len(syms) - 1 and syms[i] == a and syms[i + 1] == b:
                        outl.append(ab)
                        i += 2
                    else:
                        outl.append(syms[i])
                        i += 1
                nt = "".join(outl)
                newfreq[nt] = newfreq.get(nt, 0) + f
                w.add(4 * len(syms))
            freq = newfreq
        self.merges_used = len(order)
        self.merge_order = order
        vocab = set()
        for t in freq:
            vocab.update(self._apply_merges(t))
        vocab.update(s)
        vocab.add("\x00UNK")
        self.vocab = vocab
        self.uid = {u: i for i, u in enumerate(sorted(vocab))}
        self.uhist = []
        self.buf = []
        # unit PPM built over the ACTUAL unit alphabet (no free probability mass)
        self.ppm = PPMC(sorted(vocab), order=self.ppm_order)
        for t in toks:
            for u in self._apply_merges(t):
                uid = self.uid.get(u, self.uid["\x00UNK"])
                self.ppm.observe(uid, self.uhist)
                self.uhist.append(uid)

    def _apply_merges(self, tok):
        syms = list(tok)
        for a, b in self.merge_order:
            i = 0
            ab = a + b
            while i < len(syms) - 1:
                if syms[i] == a and syms[i + 1] == b:
                    syms[i:i + 2] = [ab]
                else:
                    i += 1
        return tuple(syms)

    def push_char(self, ch):
        """Buffer one scored character; returns the tuple of completed units."""
        self.buf.append(ch)
        if ch.isspace():
            units = ()
            if len(self.buf) > 1:
                units = self._apply_merges("".join(self.buf[:-1]))
            self.buf = []
            return units + (ch,)
        if self._word_mode:
            return ()
        if len(self.buf) >= self.chunk:
            units = self._apply_merges("".join(self.buf))
            self.buf = []
            return units
        return ()

    def flush(self):
        if self.buf:
            units = self._apply_merges("".join(self.buf))
            self.buf = []
            return units
        return ()

    def prob_unit(self, uid):
        return self.ppm.prob(uid, self.uhist)

    def observe_unit(self, uid):
        self.ppm.observe(uid, self.uhist)
        self.uhist.append(uid)

    def model_state(self):
        return {"merges": [list(p) for p in self.merge_order], "vocab": sorted(self.vocab)}


class KNNSeq(object):
    """P7: case-based sequence memory. Bucket index on the window prefix,
    scan at most the 8000 most recent same-bucket windows, k=8 nearest by
    Hamming distance, distance-weighted vote. Index build and every window
    comparison charged."""

    name = "P7_KNN_SEQ"
    kind = "online"

    def __init__(self, alpha, h=6, k=8, cap=8000):
        self.m = len(alpha)
        self.h = h
        self.k = k
        self.cap = cap
        self.b = 3 if self.m <= 20 else 2
        self.index = {}
        self.work = Work()

    def fit(self, ids, n):
        hist = []
        for i in range(n):
            if i >= self.h:
                win = tuple(ids[i - self.h:i])
                key = win[: self.b]
                self.index.setdefault(key, []).append((win, ids[i]))
                self.work.add(self.h + 2)
            hist.append(ids[i])

    def prob(self, x, hist):
        if len(hist) < self.h:
            return 1.0 / self.m
        win = tuple(hist[len(hist) - self.h:])
        key = win[: self.b]
        lst = self.index.get(key, ())
        w = self.work
        w.add(4)
        best = []  # (dist, -recency, next_id)
        start = max(0, len(lst) - self.cap)
        for j in range(len(lst) - 1, start - 1, -1):
            sw, nx = lst[j]
            d = 0
            for t in range(self.h):
                if win[t] != sw[t]:
                    d += 1
            w.add(self.h + 3)
            cand = (d, -j, nx)
            if len(best) < self.k:
                best.append(cand)
                best.sort()
            elif cand < best[-1]:
                best[-1] = cand
                best.sort()
        votes = {}
        tot = 0.0
        for d, _nj, nx in best:
            v = 1.0 / (1.0 + d)
            votes[nx] = votes.get(nx, 0.0) + v
            tot += v
            w.add(4)
        if tot <= 0:
            return 1.0 / self.m
        return votes.get(x, 0.0) / tot

    def observe(self, x, hist):
        if len(hist) >= self.h:
            win = tuple(hist[len(hist) - self.h:])
            key = win[: self.b]
            self.index.setdefault(key, []).append((win, x))
            self.work.add(self.h + 2)

    def candidates(self, hist):
        return None

    def model_state(self):
        return {"buckets": len(self.index), "entries": sum(len(v) for v in self.index.values())}


class LogisticDiag(object):
    """P8: DIAGNOSTIC ONLY, NO ADOPTION AUTHORITY. Single-layer softmax over
    one-hot last-4 symbols, SGD, frozen epochs/lr, seeded init."""

    name = "P8_LOGISTIC_DIAG"
    kind = "batch"

    def __init__(self, alpha, ctx=4, epochs=5, lr=0.05, seed=2140358):
        self.m = len(alpha)
        self.ctx = ctx
        self.epochs = epochs
        self.lr = lr
        rng = random.Random(seed)
        self.W = [[[ (rng.random() - 0.5) * 0.02 for _ in range(self.m)]
                   for _ in range(self.m)] for _ in range(ctx)]
        self.b = [0.0] * self.m
        self.work = Work()

    def dist(self, hist):
        c = hist[len(hist) - self.ctx:]
        off = self.ctx - len(c)  # positions before the stream start contribute
        m = self.m               # only the bias (never trained on pads)
        scores = list(self.b)
        W = self.W
        for p in range(len(c)):
            wp = W[p + off][c[p]]
            for o in range(m):
                scores[o] += wp[o]
        mx = max(scores)
        exps = [math.exp(v - mx) for v in scores]
        s = sum(exps)
        self.work.add(3 * self.ctx * m)
        return [v / s for v in exps]

    def fit(self, ids, n):
        ids = ids[:n]
        m = self.m
        for _ep in range(self.epochs):
            for i in range(self.ctx, n):
                c = ids[i - self.ctx:i]
                y = ids[i]
                p = self.dist(c)
                for pslot in range(self.ctx):
                    cp = c[pslot]
                    Wrow = self.W[pslot][cp]
                    for o in range(m):
                        e = (1.0 if o == y else 0.0) - p[o]
                        Wrow[o] += self.lr * e
                for o in range(m):
                    self.b[o] += self.lr * ((1.0 if o == y else 0.0) - p[o])
                self.work.add(2 * self.ctx * m)
        self.iters_used = self.epochs

    def prob(self, x, hist):
        return self.dist(hist)[x]

    def observe(self, x, hist):
        return None

    def candidates(self, hist):
        return None

    def model_state(self):
        return {"b": self.b}


# ----------------------------------------------------------------- evaluator


def closure_for(hist, actual, k=24):
    """Declared uniform candidate closure: distinct symbols in the last k
    history positions plus the actual next symbol. Arm-independent; the same
    closure is used for the oracle."""
    out = set(hist[len(hist) - k:])
    out.add(actual)
    return out


def _bits(p):
    return -math.log(max(p, EPS_FLOOR_P), 2.0)


def score_online(arm, ids, n, T, stride=1):
    """Prequential scoring of the protected tail for standard online arms.
    Every position is observed (learning continues); loss/accuracy are scored
    on the declared stride subsample."""
    bits = 0.0
    scored = 0
    correct = 0
    unseen = 0
    acc_n = 0
    w0 = arm.work.n
    for t in range(n, n + T):
        x = ids[t]
        hist = ids[max(0, t - 16):t]
        if (t - n) % stride == 0:
            p = arm.prob(x, hist)
            bits += _bits(p)
            scored += 1
            if (t - n) % ACC_STRIDE == 0:
                cl = closure_for(ids[max(0, t - 24):t], x)
                best = max(cl, key=lambda c: (arm.prob(c, hist), -c))
                if best == x:
                    correct += 1
                acc_n += 1
            if p < EPS_FLOOR_P:
                unseen += 1
    return {
        "bits_per_symbol": bits / max(scored, 1),
        "accuracy": correct / max(acc_n, 1),
        "positions_scored": scored,
        "accuracy_positions": acc_n,
        "floor_hits": unseen,
        "scored_work": arm.work.n - w0,
    }


def score_batch(arm, ids, n, T):
    """Batch arms: fit on [0,n), frozen parameters, then score the tail.
    P4 keeps filtering (no parameter update); P5 advances its own chart;
    P8 is stateless given hist."""
    bits = 0.0
    scored = 0
    correct = 0
    unseen = 0
    acc_n = 0
    w0 = arm.work.n
    for t in range(n, n + T):
        x = ids[t]
        hist = ids[max(0, t - 16):t]
        p = arm.prob(x, hist)
        bits += _bits(p)
        scored += 1
        if (t - n) % ACC_STRIDE == 0:
            cl = closure_for(ids[max(0, t - 24):t], x)
            best = max(cl, key=lambda c: (arm.prob(c, hist), -c))
            if best == x:
                correct += 1
            acc_n += 1
        if p < EPS_FLOOR_P:
            unseen += 1
        arm.observe(x, hist)
    return {
        "bits_per_symbol": bits / max(scored, 1),
        "accuracy": correct / max(acc_n, 1),
        "positions_scored": scored,
        "accuracy_positions": acc_n,
        "floor_hits": unseen,
        "scored_work": arm.work.n - w0,
    }


def score_oracle(stream, alpha, oracle, n, T):
    """Oracle over the same declared closure (synthetic worlds only)."""
    ti = {s: i for i, s in enumerate(alpha)}
    bits = 0.0
    scored = 0
    correct = 0
    for t in range(n, n + T):
        x = stream[t]
        dist = oracle(t, stream[:t])
        bits += _bits(dist[ti[x]] if x in ti else EPS_FLOOR_P)
        scored += 1
        cl = closure_for(stream[max(0, t - 24):t], x)
        best = max(cl, key=lambda s: (dist[ti[s]] if s in ti else 0.0, s))
        if best == x:
            correct += 1
    return {"bits_per_symbol": bits / max(scored, 1), "accuracy": correct / max(scored, 1),
            "positions_scored": scored, "floor_hits": 0}


def score_p6(arm, stream, alpha, n, T):
    """Buffered unit protocol (declared): characters are pushed one by one;
    when a unit completes with per-unit probability p and length L, each of
    its L characters is credited (-log2 max(p, floor))/L, so the loss is
    commensurable with the character-level arms. Candidate-closure accuracy
    is at unit granularity over the last 24 completed units plus the true
    unit (same closure rule, unit surface)."""
    ti = {s: i for i, s in enumerate(alpha)}
    bits = 0.0
    chars = 0
    correct_units = 0
    units = 0
    floor_hits = 0
    w0 = arm.work.n
    for t in range(n, n + T):
        ch = stream[t]
        done = arm.push_char(ch)
        for u in done:
            uid = arm.uid.get(u, arm.uid["\x00UNK"])
            p = arm.prob_unit(uid)
            bits += _bits(p) * len(u)
            floor_hits += 1 if p < EPS_FLOOR_P else 0
            units += 1
            chars += len(u)
            cl_units = set(arm.uhist[len(arm.uhist) - 24:])
            cl_units.add(uid)
            best = max(cl_units, key=lambda c: (arm.prob_unit(c), -c))
            if best == uid:
                correct_units += 1
            arm.observe_unit(uid)
    for u in arm.flush():
        uid = arm.uid.get(u, arm.uid["\x00UNK"])
        p = arm.prob_unit(uid)
        bits += _bits(p) * len(u)
        units += 1
        chars += len(u)
        arm.observe_unit(uid)
    return {
        "bits_per_symbol": bits / max(chars, 1),
        "accuracy": correct_units / max(units, 1),
        "positions_scored": units,
        "chars_credited": chars,
        "floor_hits": floor_hits,
        "scored_work": arm.work.n - w0,
    }


def score_p5(arm, blocks, alpha):
    """Block protocol (declared gift): each depth-0 constituent block is a
    sentence; per-symbol chain-rule prediction via Earley prefix probability;
    peek for candidate ranking; every symbol advances the chart."""
    bits = 0.0
    scored = 0
    correct = 0
    acc_n = 0
    w0 = arm.work.n
    tid = {s: i for i, s in enumerate(alpha)}
    for blk in blocks:
        ids = [tid[c] for c in blk if c in tid]
        arm.reset_block()
        for t in range(len(ids)):
            x = ids[t]
            p = arm.prob(x)
            bits += _bits(p)
            scored += 1
            if t % ACC_STRIDE == 0:
                cl = closure_for(ids[max(0, t - 24):t], x)
                best = max(cl, key=lambda c: (arm.peek(c), c))
                if best == x:
                    correct += 1
                acc_n += 1
    return {
        "bits_per_symbol": bits / max(scored, 1),
        "accuracy": correct / max(acc_n, 1),
        "accuracy_positions": acc_n,
        "positions_scored": scored,
        "floor_hits": 0,
        "scored_work": arm.work.n - w0,
    }


# ----------------------------------------------------------- P5 block gift


def nested_blocks(stream, start, end):
    """Depth-0 constituent blocks of stream[start:end] (the declared P5 gift):
    split where the nesting stack returns to 0 after a close, else at any
    depth-0 terminal run position."""
    blocks = []
    cur = []
    depth = 0
    i = start
    while i < end:
        ch = stream[i]
        cur.append(ch)
        if ch == "a":
            depth += 1
        elif ch == "b":
            depth -= 1
            if depth <= 0:
                depth = 0
                blocks.append("".join(cur))
                cur = []
        else:  # 'c' at depth 0: singleton constituent
            if depth == 0:
                blocks.append("".join(cur))
                cur = []
        i += 1
    if cur:
        blocks.append("".join(cur))
    return blocks


# --------------------------------------------------------------- arm specs

ARM_SPECS = {
    "P1": ("NgramWB", {}),
    "P2": ("PPMC", {}),
    "P3": ("CTW", {}),
    "P4": ("HMMEM", {}),
    "P5": ("PCFGEM", {}),
    "P6": ("BPEPPM", {}),
    "P7": ("KNNSeq", {}),
    "P8": ("LogisticDiag", {}),
}


def make_arm(key, alpha):
    cls_name = ARM_SPECS[key][0]
    cls = globals()[cls_name]
    return cls(alpha)


P7_STRIDE = 8  # declared subsample stride for the case-memory arm
ACC_STRIDE = 8  # declared uniform accuracy subsample (pre-run amendment A1)


# ------------------------------------------------------------- controls


def shuffled_ids(ids, n, seed=2140360):
    """Burn-in [0,n) permuted by the registered null; scored tail untouched."""
    rng = random.Random(seed)
    head = ids[:n]
    rng.shuffle(head)
    return head + ids[n:]


def run_shuffle_null(key, alpha, stream, n, T, score_stream=None):
    """Burn-in [0,n) permuted by the registered null; scored tail untouched.
    score_stream (post-run correction A8): the tail to score when the fit
    stream is truncated to exactly n symbols (real-corpus worlds), where the
    historical `stream[n:n+T]` slice is EMPTY -- the scored null window must
    be the protected scored stream itself, never an empty slice."""
    ids = [alpha.index(c) for c in stream]
    sid = shuffled_ids(ids, n)
    shuffled_stream = "".join(alpha[i] for i in sid)
    tail = score_stream if score_stream is not None else stream[n:n + T]
    r = eval_arm_split(key, alpha, shuffled_stream, n, tail)
    r.pop("arm", None)
    return r


def run_revocation(key, stream, ids, alpha, n=16000, k=256):
    """Retract the last k burn-in symbols. Online count arms must restore the
    exact state (digest over the integer sufficient statistic); batch arms pay
    a full refit on n-k. Returns timings and the digest verdict."""
    out = {"arm": key, "n": n, "retracted": k}
    if key in ("P1", "P2", "P3"):
        arm = make_arm(key, alpha)
        arm.fit(ids, n - k)
        d0 = state_digest(arm.model_state())
        for i in range(n - k, n):
            arm.observe(ids[i], ids[max(0, i - 16):i])
        d1 = state_digest(arm.model_state())
        t0 = time.time()
        for i in range(n - 1, n - k - 1, -1):
            arm.unobserve(ids[i], ids[max(0, i - 16):i])
        out["unobserve_wall_s"] = round(time.time() - t0, 4)
        d2 = state_digest(arm.model_state())
        out["digest_before"] = d0
        out["digest_after_retract_applied"] = d1
        out["digest_restored"] = d2
        out["exact_restore"] = (d0 == d2)
        # timing of the naive alternative: observe k more from a refit-free path
        arm2 = make_arm(key, alpha)
        t0 = time.time()
        arm2.fit(ids, n - k)
        out["refit_from_scratch_wall_s"] = round(time.time() - t0, 4)
    else:
        t0 = time.time()
        arm = make_arm(key, alpha)
        if key == "P5":
            arm.blocks = nested_blocks(stream, 0, n - k)
        arm.fit(ids, n - k)
        out["refit_from_scratch_wall_s"] = round(time.time() - t0, 4)
        out["exact_restore"] = None  # batch: full refit is the only semantics
    return out


# ----------------------------------------------------------- world runners


def eval_arm_split(key, alpha, fit_stream, fit_n, score_stream):
    """Fresh arm; fit on fit_stream[:fit_n]; score the WHOLE score_stream
    prequentially with the fitted state carried over (declared protocol for
    the real-corpus worlds: the scored region is a different document)."""
    fit_ids = [alpha.index(c) for c in fit_stream[:fit_n]]
    score_ids = [alpha.index(c) for c in score_stream]
    arm = make_arm(key, alpha)
    t0 = time.time()
    if key == "P5":
        arm.blocks = nested_blocks(fit_stream, 0, fit_n)
        arm.fit(fit_ids, fit_n)
    else:
        arm.fit(fit_ids, fit_n)
    fit_wall = time.time() - t0
    T = len(score_ids)
    if key == "P5":
        res = score_p5(arm, nested_blocks(score_stream, 0, len(score_stream)), alpha)
    elif key == "P6":
        res = score_p6(arm, score_stream, alpha, 0, T)
    elif key == "P7":
        res = score_online(arm, score_ids, 0, T, stride=P7_STRIDE)
    elif arm.kind == "online":
        res = score_online(arm, score_ids, 0, T)
    else:
        res = score_batch(arm, score_ids, 0, T)
    res["fit_wall_s"] = round(fit_wall, 4)
    res["total_work"] = arm.work.n
    try:
        res["persistent_bytes"] = len(canon(arm.model_state()).encode("utf-8"))
    except (TypeError, ValueError):
        res["persistent_bytes"] = None
    res["arm"] = arm
    return res


def run_synthetic_world(name, stream, meta, ladder, T, arms):
    alpha = meta["alpha"]
    ids = [alpha.index(c) for c in stream]
    res = {"world": name, "alpha_size": len(alpha), "ladder": ladder, "T": T, "arms": {}}
    oracle_bits = None
    if "P0" in arms:
        ores = score_oracle(stream, alpha, meta["oracle"], ladder[-1], T)
        oracle_bits = ores["bits_per_symbol"]
        res["P0_ORACLE"] = ores
    for key in arms:
        if key == "P0":
            continue
        entry = {}
        for n in ladder:
            r = eval_arm_split(key, alpha, stream, n, stream[ladder[-1]:ladder[-1] + T])
            r.pop("arm")
            r["gap_to_oracle_bits"] = (
                round(r["bits_per_symbol"] - oracle_bits, 6) if oracle_bits is not None else None)
            entry[str(n)] = r
        eff = None
        if oracle_bits is not None:
            for n in ladder:
                if entry[str(n)]["bits_per_symbol"] <= oracle_bits + 0.05:
                    eff = n
                    break
        entry["samples_to_oracle_threshold"] = eff
        res["arms"][key] = entry
    res["oracle_bits_per_symbol"] = oracle_bits
    return res


W4_LADDER = (50000, 200000, 1000000)
W5_LADDER = (20000, 80000, 254000)


def run_real_world(name, loader, ladder, arms, scope_map):
    """Real-corpus world: train slice of the TRAIN file, scored = PROTECTED
    test-stream prefix (W4) or whole test stream (W5), evaluated only here."""
    stream, scored, alpha = loader()
    # A6 (declared OOV device, pre-run): the protected score stream may contain
    # characters absent from the train-window alphabet; they are substituted by
    # one sentinel symbol appended to the alphabet (a first-class symbol for
    # every arm; the fit window never contains it). Count recorded below.
    aset = set(alpha)
    n_oov = sum(1 for c in scored if c not in aset)
    if n_oov:
        scored = "".join(c if c in aset else "\x00" for c in scored)
        alpha = list(alpha) + ["\x00"]
    res = {"world": name, "alpha_size": len(alpha), "ladder": list(ladder),
           "T": len(scored), "oov_substitutions": n_oov, "arms": {},
           "oracle": "CANNOT_CHECK_ORACLE_ABSENT_REAL_CORPUS"}
    for key in arms:
        entry = {}
        for n in ladder:
            note = scope_map.get((key, n))
            if note:
                entry[str(n)] = "CANNOT_CHECK_" + note
                continue
            r = eval_arm_split(key, alpha, stream, n, scored)
            r.pop("arm")
            entry[str(n)] = r
        res["arms"][key] = entry
    best = None
    for key in arms:
        r = res["arms"][key].get(str(ladder[-1]))
        if isinstance(r, dict):
            if best is None or r["bits_per_symbol"] < best[1]:
                best = (key, round(r["bits_per_symbol"], 6))
    res["strongest_parent_at_max_n"] = best
    return res


def w4_loader():
    stream, scored, alpha, digests, dev_len = load_ud_char_world()
    W4_CUSTODY.update(digests)
    W4_CUSTODY["dev_sanity_chars"] = dev_len
    return stream, scored, alpha


W4_CUSTODY = {}


def w5_loader():
    stream, scored, alpha, n_tr, n_te = load_ud_pos_world()
    W5_CUSTODY.update({"train_sentences": n_tr, "test_sentences": n_te})
    return stream, scored, alpha


W5_CUSTODY = {}


def run_expressivity_dial(arms_dial):
    """W2 regenerated with D_MAX in {8,16,32,48}; n=64000, T=20000."""
    out = {"world": "W2_NESTED_DIAL", "d_max_grid": [8, 16, 32, 48], "n": 64000, "T": 20000,
           "arms": {}}
    for d in (8, 16, 32, 48):
        stream, meta = gen_nested(84000, 2140302, d_max=d)
        alpha = meta["alpha"]
        res_d = run_synthetic_world("W2_D%d" % d, stream, meta, [64000], 20000, arms_dial)
        out["arms"]["D%d" % d] = res_d["arms"]
        out["oracle_bits_D%d" % d] = res_d.get("oracle_bits_per_symbol")
    return out


# ------------------------------------------------------------ unigram floor


def unigram_floor(fit_stream, fit_n, score_stream, alpha):
    """Order-0 add-0.5 frequency model: the declared floor an arm must beat
    for the shuffle null to be interpretable (R5)."""
    m = len(alpha)
    counts = [0.0] * m
    for c in fit_stream[:fit_n]:
        counts[alpha.index(c)] += 1.0
    tot = sum(counts)
    bits = 0.0
    ti = {s: i for i, s in enumerate(alpha)}
    for c in score_stream:
        i = ti.get(c)
        p = (counts[i] + 0.5) / (tot + 0.5 * m) if i is not None else EPS_FLOOR_P
        bits += _bits(p)
    return bits / max(len(score_stream), 1)


# --------------------------------------------------------------- verdicts


def _bits_at(world_res, key, n):
    r = world_res["arms"].get(key, {}).get(str(n))
    return r["bits_per_symbol"] if isinstance(r, dict) else None


def world_verdict(world_res):
    """Mechanical verdict from the frozen rules (no discretion)."""
    name = world_res["world"]
    ladder = world_res["ladder"]
    n = ladder[-1]
    if world_res.get("oracle_bits_per_symbol") is not None:
        ob = world_res["oracle_bits_per_symbol"]
        gaps = {}
        for key, entry in world_res["arms"].items():
            if not isinstance(entry, dict):
                continue
            r = entry.get(str(n))
            b = r.get("bits_per_symbol") if isinstance(r, dict) else None
            if b is not None:
                gaps[key] = round(b - ob, 6)
        best = min(gaps, key=gaps.get) if gaps else None
        if best is not None and gaps[best] <= 0.05:
            return {"verdict": "PARENT_SUFFICIENT_FOR_NEXT_SYMBOL_PREDICTION",
                    "best_parent": best, "gap_bits": gaps[best], "gaps": gaps,
                    "scope": "%s@n=%d" % (name, n)}
        return {"verdict": "REPRESENTATION_INSUFFICIENT",
                "best_parent": best, "gap_bits": gaps.get(best), "gaps": gaps,
                "scope": "%s@n=%d" % (name, n)}
    best = world_res.get("strongest_parent_at_max_n")
    return {"verdict": "CANNOT_CHECK_ORACLE_ABSENT_REAL_CORPUS",
            "strongest_parent": best, "scope": "%s@n=%d" % (name, n)}


def evaluate_predictions(R, w1, w2, w3, w5, dial, nulls, floors):
    out = {}

    def gap(world, key, n):
        g = _bits_at(world, key, n)
        if g is None:
            return None
        o = world.get("oracle_bits_per_symbol")
        return None if o is None else g - o

    r1a = gap(w1, "P3", 16000)
    r1b = gap(w1, "P1", 16000)
    r1c = gap(w1, "P1", 64000)
    out["R1"] = {
        "prediction": R["R1"],
        "ctw_gap_16000": r1a, "ngram_gap_16000": r1b, "ngram_gap_64000": r1c,
        "confirmed": (r1a is not None and r1a <= 0.02 and r1b is not None and r1b > 0.02
                      and r1c is not None and r1c <= 0.02)}

    d48 = dial["arms"].get("D48", {})
    fgaps = {}
    for k in ("P1", "P2", "P3"):
        e = d48.get(k, {}).get("64000")
        ob = dial.get("oracle_bits_D48")
        if isinstance(e, dict) and ob is not None:
            fgaps[k] = round(e["bits_per_symbol"] - ob, 6)
    p5e = d48.get("P5", {}).get("64000")
    p5gap = round(p5e["bits_per_symbol"] - dial.get("oracle_bits_D48"), 6) if isinstance(p5e, dict) and dial.get("oracle_bits_D48") is not None else None
    out["R2"] = {
        "prediction": R["R2"],
        "finite_context_gaps_D48": fgaps,
        "pcfg_gap_D48": p5gap,
        "confirmed": (all(g >= 0.10 for g in fgaps.values()) and len(fgaps) == 3
                      and p5gap is not None and p5gap <= 0.05)}

    p6w3 = _bits_at(w3, "P6", 64000)
    p2w3 = _bits_at(w3, "P2", 64000)
    out["R3"] = {"prediction": R["R3"], "p6_bits": p6w3, "p2_bits": p2w3,
                 "confirmed": p6w3 is not None and p2w3 is not None and p6w3 < p2w3}

    cands = {k: _bits_at(w5, k, 254000) for k in ("P1", "P2", "P3", "P7")}
    p8w5 = _bits_at(w5, "P8", 254000)
    online_best = min((v for v in cands.values() if v is not None), default=None)
    out["R4"] = {"prediction": R["R4"], "online_parents": cands, "p8_bits": p8w5,
                 "confirmed": online_best is not None and p8w5 is not None and online_best <= p8w5}

    r5 = {}
    for wname, entry in nulls.items():
        floor = floors.get(wname)
        for key, d in entry.items():
            normal = d.get("normal_bits")
            shuffled = d.get("shuffled_bits")
            if normal is None or shuffled is None or floor is None:
                continue
            beat = normal < floor
            r5["%s/%s" % (wname, key)] = {
                "beat_unigram_floor": beat,
                "degradation_bits": round(shuffled - normal, 6),
                "passes": (not beat) or (shuffled - normal) >= 0.05}
    out["R5"] = {"prediction": R["R5"], "cases": r5,
                 "confirmed": all(c["passes"] for c in r5.values()) if r5 else None}
    return out


# ------------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser(description="FNA-3/D5 sequence/grammar parent suite")
    ap.add_argument("--out", default=str(HERE / "FNA3_RESULTS_V1.json"))
    ap.add_argument("--skip-ud", action="store_true",
                    help="skip the UD worlds (custody files unavailable); recorded as CANNOT_CHECK")
    args = ap.parse_args()
    t_start = time.time()
    import platform

    def log(msg):
        print("[%7.1fs] %s" % (time.time() - t_start, msg), flush=True)

    freeze = json.loads((HERE / "FREEZE_FNA3_V1.json").read_text(encoding="utf-8"))
    R = freeze["registered_predictions_before_execution"]
    results = {
        "schema": SCHEMA,
        "freeze": "FREEZE_FNA3_V1.json",
        "host": platform.node(),
        "python": platform.python_version(),
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "amendments_pre_run": ["A1_uniform_stride8_accuracy_subsample",
                               "A2_P4_scope_n16000_synthetic_n20000_W5_iters10",
                               "A3_P5_EM_fit_block_cap_1500",
                               "A4_budget_cap_7200s",
                               "A5_W2_generator_corrected_to_declared_depth_first_law",
                               "A6_real_world_OOV_sentinel_substitution",
                               "A7_world_verdict_CANNOT_CHECK_entry_guard"],
    }

    LAD = [1000, 4000, 16000, 64000]
    T = 20000
    log("generating synthetic worlds")
    w1s, w1m = gen_psa(84000)
    w2s, w2m = gen_nested(84000)
    w3s, w3m = gen_lexicon(84000)

    log("W1_PSA ladder")
    w1 = run_synthetic_world("W1_PSA", w1s, w1m, LAD, T,
                             ["P0", "P1", "P2", "P3", "P4", "P7", "P8"])
    log("W2_NESTED ladder")
    w2 = run_synthetic_world("W2_NESTED", w2s, w2m, LAD, T,
                             ["P0", "P1", "P2", "P3", "P4", "P5", "P7", "P8"])
    log("W3_LEXICON ladder")
    w3 = run_synthetic_world("W3_LEXICON", w3s, w3m, LAD, T,
                             ["P0", "P1", "P2", "P3", "P4", "P6", "P7", "P8"])
    # P4 compute re-scope (amendment A2): synthetic worlds at n=16000 only
    for w in (w1, w2, w3):
        ent = w["arms"].get("P4", {})
        for n in LAD:
            if n != 16000 and isinstance(ent.get(str(n)), dict):
                ent[str(n)] = "CANNOT_CHECK_COMPUTE_BUDGET"

    log("expressivity dial (W2, D_MAX 8/16/32/48)")
    dial = run_expressivity_dial(["P0", "P1", "P2", "P3", "P5", "P8"])

    w4 = w5 = None
    if not args.skip_ud:
        log("W4_UD_CHAR (custody-gated)")
        w4 = run_real_world("W4_UD_CHAR", w4_loader, W4_LADDER, ["P1", "P2", "P3", "P6", "P7"],
                            {("P4", n): "COMPUTE_BUDGET" for n in W4_LADDER})
        w4["custody"] = W4_CUSTODY
        log("W5_UD_POS (custody-gated)")
        w5 = run_real_world("W5_UD_POS", w5_loader, W5_LADDER, ["P1", "P2", "P3", "P4", "P7", "P8"],
                            {("P4", n): ("COMPUTE_BUDGET" if n != 20000 else None) for n in W5_LADDER})
        w5["custody"] = W5_CUSTODY

    log("unigram floors")
    floors = {
        "W1_PSA": unigram_floor(w1s, 64000, w1s[64000:84000], w1m["alpha"]),
        "W2_NESTED": unigram_floor(w2s, 64000, w2s[64000:84000], w2m["alpha"]),
        "W3_LEXICON": unigram_floor(w3s, 64000, w3s[64000:84000], w3m["alpha"]),
    }

    log("shuffle nulls (synthetic, n=64000)")
    nulls = {}
    for wname, s, m in (("W1_PSA", w1s, w1m), ("W2_NESTED", w2s, w2m), ("W3_LEXICON", w3s, w3m)):
        entry = {}
        main_res = {"W1_PSA": w1, "W2_NESTED": w2, "W3_LEXICON": w3}[wname]
        for key in ("P1", "P2", "P3", "P7", "P8"):
            nr = run_shuffle_null(key, m["alpha"], s, 64000, T)
            entry[key] = {"normal_bits": _bits_at(main_res, key, 64000),
                          "shuffled_bits": nr.get("bits_per_symbol"),
                          "shuffled_fit_wall_s": nr.get("fit_wall_s")}
        nulls[wname] = entry

    if not args.skip_ud:
        log("shuffle nulls (UD, max n)")
        nulls["W4_UD_CHAR"] = {}
        stream4, scored4, alpha4 = w4_loader()
        # A6/A8: the scored stream may contain OOV chars; apply the same
        # sentinel substitution + extended alphabet as run_real_world so the
        # null scores the identical prediction problem the main run scored.
        aset4 = set(alpha4)
        if any(c not in aset4 for c in scored4):
            scored4 = "".join(c if c in aset4 else "\x00" for c in scored4)
            alpha4 = list(alpha4) + ["\x00"]
        for key in ("P1", "P2", "P3", "P7"):
            nr = run_shuffle_null(key, alpha4, stream4, 1000000, len(scored4),
                                  score_stream=scored4)
            nulls["W4_UD_CHAR"][key] = {
                "normal_bits": _bits_at(w4, key, 1000000),
                "shuffled_bits": nr.get("bits_per_symbol"),
                "shuffled_fit_wall_s": nr.get("fit_wall_s")}
        floors["W4_UD_CHAR"] = unigram_floor(stream4, 1000000, scored4, alpha4)
        nulls["W5_UD_POS"] = {}
        stream5, scored5, alpha5 = w5_loader()
        for key in ("P1", "P2", "P3", "P7"):
            nr = run_shuffle_null(key, alpha5, stream5, 254000, len(scored5),
                                  score_stream=scored5)
            nulls["W5_UD_POS"][key] = {
                "normal_bits": _bits_at(w5, key, 254000),
                "shuffled_bits": nr.get("bits_per_symbol"),
                "shuffled_fit_wall_s": nr.get("fit_wall_s")}
        floors["W5_UD_POS"] = unigram_floor(stream5, 254000, scored5, alpha5)

    log("revocation (n=16000, retract 256)")
    rev = {"W1_PSA": {}, "W2_NESTED": {}}
    ids1 = [w1m["alpha"].index(c) for c in w1s]
    for key in ("P1", "P2", "P3", "P8"):
        rev["W1_PSA"][key] = run_revocation(key, w1s, ids1, w1m["alpha"], 16000, 256)
    ids2 = [w2m["alpha"].index(c) for c in w2s]
    rev["W2_NESTED"]["P5"] = run_revocation("P5", w2s, ids2, w2m["alpha"], 16000, 256)
    rev["W1_PSA"]["P4"] = run_revocation("P4", w1s, ids1, w1m["alpha"], 16000, 256)

    log("verdicts + predictions")
    verdicts = {w["world"]: world_verdict(w) for w in (w1, w2, w3)}
    if w4 is not None:
        verdicts["W4_UD_CHAR"] = world_verdict(w4)
    if w5 is not None:
        verdicts["W5_UD_POS"] = world_verdict(w5)
    if w5 is None:
        w5 = {"arms": {}, "ladder": [20000, 80000, 254000]}
    preds = evaluate_predictions(R, w1, w2, w3, w5, dial, nulls, floors)

    results.update({
        "worlds": {"W1_PSA": w1, "W2_NESTED": w2, "W3_LEXICON": w3},
        "expressivity_dial": dial,
        "W4_UD_CHAR": w4,
        "W5_UD_POS": w5,
        "unigram_floors_bits_per_symbol": floors,
        "shuffle_nulls": nulls,
        "revocation": rev,
        "verdicts": verdicts,
        "predictions": preds,
        "wall_seconds": round(time.time() - t_start, 1),
        "budget_cap_seconds": 7200,
        "budget_respected": (time.time() - t_start) <= 7200,
    })
    out_path = Path(args.out)
    out_path.write_text(json.dumps(results, indent=1, sort_keys=True, default=str), encoding="utf-8")
    log("written %s (%d bytes)" % (out_path, out_path.stat().st_size))
    return 0


if __name__ == "__main__":
    sys.exit(main())

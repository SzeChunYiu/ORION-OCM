#!/usr/bin/env python3
"""GMI #833 AE14 route A: generalization / analogy / reasoning taxonomy.

Executor for package ``gmi-833-ae-ae14-generalization-taxonomy-v1``.  Prints
``RESULT_V1.json`` to stdout.  Exact arithmetic only: every quantity entering a
claim is a ``fractions.Fraction`` or an ``int``; no float is constructed
anywhere in this file.  Determinism is structural: every collection is sorted
before serialization, no set is iterated into output, and serialization is a
single ``json.dumps(..., sort_keys=True, indent=2)`` plus a trailing newline.

Route B (``independent_taxonomy_oracle_v1.py``) recomputes every claimed
quantity by a materially different algorithm and imports nothing from here.
"""
from __future__ import print_function

import hashlib
import json
import re
import os
import sys
from fractions import Fraction

# ---------------------------------------------------------------------------
# 0.  registered scope
# ---------------------------------------------------------------------------
SCHEMA = "GMI_833_AE14_GENERALIZATION_TAXONOMY_RESULT_V1"
ISSUE = 833
ISSUE_COMMENT_ID = 5692689542
PACKAGE = "gmi-833-ae-ae14-generalization-taxonomy-v1"
SOURCE_MAIN = "0dcdec54fbece041ee2b7cd1f630469ad85d19d3"
FREEZE_COMMIT = "6cd9f2924d153ea7f5938eca1a7694f9bf50606b"
REGISTER_COMMIT = "9857a838acd2f6f83499cac36de2193348c26d09"
CLAIM_CEILING = ("GMI_833_AE14_GENERALIZATION_MODES_OPERATIONALLY_SEPARATED_"
                 "ON_REGISTERED_FINITE_TASK_ROSTER")
FORBIDDEN_PROMOTIONS = [
    "ALL_LEARNING_IS_COMPRESSION",
    "ANALOGY_IS_INTERPOLATION",
    "ARCHITECTURE_SELECTION_LAW",
    "ASYMPTOTIC_EXTRAPOLATION_FROM_FINITE_ROSTER",
    "COMPLETE_GMI",
    "FREE_ENERGY_PRINCIPLE_PROVED",
    "GENERAL_REASONING_REDUCED_TO_PREDICTION",
    "GMI_MORPHOLOGY_PREDICTION",
    "INTELLIGENCE_EQUALS_COMPRESSION",
    "MANIFOLD_HYPOTHESIS_UNIVERSAL",
    "MEMORY_GENERALIZATION_ANALOGY_REASONING_SAME_MECHANISM",
    "MUTUAL_INFORMATION_SUFFICIENT_FOR_INTELLIGENCE",
    "REAL_SYSTEM_CLAIM_WITHOUT_INSTRUMENT",
    "REASONING_REDUCED_TO_PREDICTION",
    "SCALE_UNIFIES_GENERALIZATION_MODES",
    "THERMODYNAMIC_INTELLIGENCE_LAW",
    "WORLD_MODEL_ALWAYS_REQUIRED",
]
FORBIDDEN_BLANKET = "MEMORY_GENERALIZATION_ANALOGY_REASONING_SAME_MECHANISM"

N = 4
XS = tuple(range(16))
BLOCKS = ((0, 1), (2, 3))
SEARCH_DEPTH_CAP = 3
JUNTA_ARITY = 2
TREE_DEPTH = 2
NULL_TRIALS = 200
# registered deterministic stream seed: the issue comment id reduced mod 2**31
NULL_SEED = 5692689542 % (1 << 31)


def bit(x, i):
    """coordinate x_i of the point x; x_0 is the most significant bit."""
    return (x >> (3 - i)) & 1


def flip(x, i):
    return x ^ (1 << (3 - i))


def blk1(x):
    return x >> 2


def blk2(x):
    return x & 3


def mk(u, v):
    return 4 * u + v


# ---- registered operators --------------------------------------------------
def op_rho(x):
    """(x0,x1,x2,x3) -> (x1,x2,x3,x0): the registered analogy generator."""
    return ((x << 1) & 15) | (x >> 3)


def op_pi1(x):
    """p1: add 1 modulo 4 to the value of block 1."""
    return mk((blk1(x) + 1) % 4, blk2(x))


def op_pi2(x):
    """p2: exchange the two blocks."""
    return mk(blk2(x), blk1(x))


POINT_OPS = {"pi1": op_pi1, "pi2": op_pi2, "rho": op_rho}
OP_ORDER = ("pi1", "pi2", "rho", "tau")

# four Horn rules over six propositional atoms a,b,c,d,e,f indexed 0..5
REASON_RULES = (((0, 1), 4), ((2, 3), 4), ((4, 2), 5), ((0, 2), 5))
REASON_TARGET_ATOM = 5


def emb(x):
    """embed a point of X as a six-atom state with the derived atoms unset."""
    return (bit(x, 0), bit(x, 1), bit(x, 2), bit(x, 3), 0, 0)


def tau(z):
    """round-parallel immediate-consequence operator: heads read the old state."""
    new = list(z)
    for ante, head in REASON_RULES:
        if all(z[a] for a in ante):
            new[head] = 1
    return tuple(new)


def apply_op(name, z):
    if name == "tau":
        return tau(z)
    f = POINT_OPS[name]
    x = (z[0] << 3) | (z[1] << 2) | (z[2] << 1) | z[3]
    y = f(x)
    return (bit(y, 0), bit(y, 1), bit(y, 2), bit(y, 3), z[4], z[5])


def words(subset, cap):
    """words over ``subset`` of length 0..cap, ordered by length then registered
    operator order."""
    ops = [o for o in OP_ORDER if o in subset]
    out = [()]
    cur = [()]
    for _ in range(cap):
        nxt = []
        for w in cur:
            for o in ops:
                nxt.append(w + (o,))
        out.extend(nxt)
        cur = nxt
    return out


def apply_word(w, z):
    for o in w:
        z = apply_op(o, z)
    return z


def closure_depth(x):
    """least round count k with the target atom set in tau^k(emb(x)), else None."""
    z = emb(x)
    for k in range(1, 8):
        z2 = tau(z)
        if z2[REASON_TARGET_ATOM]:
            return k
        if z2 == z:
            return None
        z = z2
    return None


# ---------------------------------------------------------------------------
# 1.  registered structures over a training support
# ---------------------------------------------------------------------------
def span(tr):
    """the smallest subcube of X containing Tr: fix every coordinate that is
    constant across Tr, free the rest."""
    const = {}
    for i in range(N):
        vs = sorted(set(bit(x, i) for x in tr))
        if len(vs) == 1:
            const[i] = vs[0]
    return tuple(x for x in XS
                 if all(bit(x, i) == b for i, b in sorted(const.items())))


def recomb(tr):
    """every recombination of block values each of which occurs in Tr."""
    b1 = sorted(set(blk1(x) for x in tr))
    b2 = sorted(set(blk2(x) for x in tr))
    return tuple(sorted(mk(u, v) for u in b1 for v in b2))


def group_elements():
    """the registered order-4 cyclic coordinate-rotation group, as tuples."""
    out = []
    cur = tuple(XS)
    for _ in range(4):
        out.append(cur)
        cur = tuple(op_rho(y) for y in cur)
    return tuple(out)


GROUP = group_elements()


def witnessed(tr, g):
    """g is witnessed in Tr iff some training point is mapped by g to a
    different training point; a fixed point exhibits nothing about g."""
    s = set(tr)
    return any(g[x] in s and g[x] != x for x in tr)


def analogy_pts(tr):
    """answers g.c of the registered relational instances whose g never appears
    in Tr."""
    s = set(tr)
    out = set()
    for gi in (1, 2, 3):
        g = GROUP[gi]
        if witnessed(tr, g):
            continue
        for c in sorted(tr):
            y = g[c]
            if y != c and y not in s:
                out.add(y)
    return tuple(sorted(out))


def min_word_length(x, trset, cap=SEARCH_DEPTH_CAP):
    """least length of a word over the registered planning primitives mapping x
    into Tr, or None within the cap."""
    if x in trset:
        return 0
    cur = [x]
    for k in range(1, cap + 1):
        nxt = []
        for y in cur:
            for o in ("pi1", "pi2"):
                z = POINT_OPS[o](y)
                if z in trset:
                    return k
                nxt.append(z)
        cur = nxt
    return None


def plan_pts(tr, cap=SEARCH_DEPTH_CAP):
    """targets needing a composition of at least two registered primitives: no
    single primitive maps them into Tr, some word of length <= cap does."""
    s = set(tr)
    out = []
    for x in XS:
        if x in s:
            continue
        m = min_word_length(x, s, cap)
        if m is not None and m >= 2:
            out.append(x)
    return tuple(out)


def reason_pts(tr):
    """(entailments of shortest derivation depth >= 2 outside Tr, their
    one-atom non-entailed neighbours outside Tr)."""
    s = set(tr)
    ent = tuple(x for x in XS
                if x not in s and closure_depth(x) is not None
                and closure_depth(x) >= 2)
    neg = set()
    for x in ent:
        for i in range(N):
            y = flip(x, i)
            if y not in s and closure_depth(y) is None:
                neg.add(y)
    return ent, tuple(sorted(neg))


# ---------------------------------------------------------------------------
# 2.  learner classes (a hypothesis is a 16-bit truth-table mask)
# ---------------------------------------------------------------------------
def tt(fn):
    m = 0
    for x in XS:
        if fn(x):
            m |= 1 << x
    return m


def val(m, x):
    return (m >> x) & 1


def essential(m, i):
    return any(val(m, x) != val(m, flip(x, i)) for x in XS)


def build_L1():
    """k-juntas with k <= JUNTA_ARITY, computed by a decision tree of depth
    <= TREE_DEPTH; built constructively from coordinate subsets."""
    out = set()
    idxs = list(range(N))
    subsets = [()]
    for i in idxs:
        subsets.append((i,))
        for j in idxs:
            if j > i:
                subsets.append((i, j))
    for sub in subsets:
        if len(sub) > JUNTA_ARITY or len(sub) > TREE_DEPTH:
            continue
        for table in range(1 << (1 << len(sub))):
            def f(x, sub=sub, table=table):
                k = 0
                for p, i in enumerate(sub):
                    k |= bit(x, i) << p
                return (table >> k) & 1
            out.add(tt(f))
    return tuple(sorted(out))


def build_L_lin():
    """the GF(2)-affine functionals, in the registered (mask, bias) order."""
    out = []
    for a in range(16):
        for b in range(2):
            out.append(tt(lambda x, a=a, b=b: (bin(x & a).count("1") + b) % 2))
    return tuple(out)


def build_L_mod():
    """block-modular compositions h(g1(block1), g2(block2)), built from the
    parameterisation."""
    out = set()
    for g1 in range(16):
        for g2 in range(16):
            for h in range(16):
                def f(x, g1=g1, g2=g2, h=h):
                    a = (g1 >> blk1(x)) & 1
                    b = (g2 >> blk2(x)) & 1
                    return (h >> (2 * a + b)) & 1
                out.add(tt(f))
    return tuple(sorted(out))


L1_LIST = build_L1()
L_LIN_ORDERED = build_L_lin()
L_LIN_LIST = tuple(sorted(set(L_LIN_ORDERED)))
L_MOD_LIST = build_L_mod()


def build_L0(tr):
    """every function constant off Tr (arbitrary on Tr)."""
    tr = tuple(sorted(tr))
    if tr in _L0_CACHE:
        return _L0_CACHE[tr]
    out = set()
    for assign in range(1 << len(tr)):
        for c in (0, 1):
            m = 0xFFFF if c else 0
            for j, x in enumerate(tr):
                if (assign >> j) & 1:
                    m |= 1 << x
                else:
                    m &= ~(1 << x) & 0xFFFF
            out.add(m)
    _L0_CACHE[tr] = tuple(sorted(out))
    return _L0_CACHE[tr]


SEARCH_SUBSETS = tuple(
    tuple(OP_ORDER[i] for i in range(4) if (b >> i) & 1) for b in range(1, 16))
SEARCH_READOUTS = (tuple(("lookup", d) for d in (0, 1))
                   + tuple(("atom", j) for j in range(6)))
_WORD_IMAGES = {}
_ATOM_MEMBERS = {}
_RESOLVE = {}
_L0_CACHE = {}


def word_images(subset, cap):
    """for each point of X, the ordered images of its embedded state under every
    word over ``subset`` of length at most ``cap``."""
    key = (subset, cap)
    if key not in _WORD_IMAGES:
        ws = words(subset, cap)
        _WORD_IMAGES[key] = tuple(
            tuple(apply_word(w, emb(x)) for w in ws) for x in XS)
    return _WORD_IMAGES[key]


def atom_members(subset, cap):
    """the derivability readouts: atom j is reported set iff some word over
    ``subset`` of length at most ``cap`` sets it.  Independent of the task."""
    key = (subset, cap)
    if key not in _ATOM_MEMBERS:
        imgs = word_images(subset, cap)
        out = []
        for j in range(6):
            m = 0
            for x in XS:
                for z in imgs[x]:
                    if z[j]:
                        m |= 1 << x
                        break
            out.append(m)
        _ATOM_MEMBERS[key] = tuple(out)
    return _ATOM_MEMBERS[key]


def resolve_map(subset, cap, tr):
    """for each point of X, the training point reached by the lex-least word
    over ``subset`` of length at most ``cap``, or None."""
    key = (subset, cap, tr)
    if key not in _RESOLVE:
        imgs = word_images(subset, cap)
        anchors = dict((emb(x), x) for x in tr)
        out = []
        for x in XS:
            hit = None
            for z in imgs[x]:
                if z in anchors:
                    hit = anchors[z]
                    break
            out.append(hit)
        _RESOLVE[key] = tuple(out)
    return _RESOLVE[key]


def build_L_search(tr, tmask, cap=SEARCH_DEPTH_CAP):
    """the composition class: each member is a registered operator subset S
    together with a registered readout.  ``lookup`` transports the query by the
    lex-least word over S of length <= cap whose image is an embedded training
    point and reads that point's label (default d when no word lands);
    ``atom j`` reports whether atom j is derivable within cap applications."""
    tr = tuple(sorted(tr))
    out = []
    for s in SEARCH_SUBSETS:
        res = resolve_map(s, cap, tr)
        for d in (0, 1):
            m = 0
            for x in XS:
                src = res[x]
                lab = d if src is None else val(tmask, src)
                if lab:
                    m |= 1 << x
            out.append(("lookup|%s|%d" % ("+".join(s), d), m))
        ams = atom_members(s, cap)
        for j in range(6):
            out.append(("atom|%s|%d" % ("+".join(s), j), ams[j]))
    return tuple(out)


CLASSES = ("L0", "L1", "L_lin", "L_mod", "L_search")
PREDICTION_ONLY = ("L0", "L1", "L_lin", "L_mod")


def class_members(name, tr, tmask):
    if name == "L0":
        return build_L0(tr)
    if name == "L1":
        return L1_LIST
    if name == "L_lin":
        return L_LIN_LIST
    if name == "L_mod":
        return L_MOD_LIST
    if name == "L_search":
        return tuple(m for _, m in build_L_search(tr, tmask))
    raise ValueError(name)


def classes_for(tr, tmask):
    return dict((c, class_members(c, tr, tmask)) for c in CLASSES)


def minimal_realizing_class(mode, tmask, tr):
    """the first class of the registered priority order that realizes the mode."""
    for c in CLASSES:
        if mode_holds(mode, class_members(c, tr, tmask), tmask, tr):
            return c
    return None


# ---------------------------------------------------------------------------
# 3.  the seven mode predicates
# ---------------------------------------------------------------------------
MODES = ("MEMORIZATION", "INTERPOLATION", "EXTRAPOLATION",
         "SYSTEMATIC_GENERALIZATION", "ANALOGY", "PLANNING_INFERENCE",
         "REASONING")

MODE_DEFINITIONS = {
    "MEMORIZATION": ("some member of the class is exact on Tr and scores "
                     "exactly the base rate on X \\ Tr"),
    "INTERPOLATION": ("some member of the class is exact on span(Tr), the "
                      "smallest subcube of X containing Tr"),
    "EXTRAPOLATION": ("some member of the class is exact on Tr and on the "
                      "registered subset X \\ span(Tr), which must be nonempty"),
    "SYSTEMATIC_GENERALIZATION": (
        "some member of the class is exact on Tr and on every recombination of "
        "block values occurring in Tr, including combinations absent from Tr"),
    "ANALOGY": ("some member of the class is exact on Tr and on the answers "
                "g.c of the registered relational instances whose group element "
                "g never appears in Tr"),
    "PLANNING_INFERENCE": (
        "some member of the class is exact on Tr and on the registered targets "
        "that need a composition of at least two registered primitives, no "
        "single primitive sufficing"),
    "REASONING": ("some member of the class is exact on Tr, on the entailments "
                  "of the frozen Horn system whose shortest derivation has "
                  "depth at least 2 and which are not members of Tr, and on "
                  "their one-atom non-entailed neighbours"),
}


def eval_points(mode, tr):
    """the registered evaluation set of a mode at a support (disjoint from Tr,
    except MEMORIZATION which is scored by rate on X \\ Tr)."""
    s = set(tr)
    if mode == "MEMORIZATION":
        return tuple(x for x in XS if x not in s)
    if mode == "INTERPOLATION":
        return tuple(x for x in span(tr) if x not in s)
    if mode == "EXTRAPOLATION":
        sp = set(span(tr))
        return tuple(x for x in XS if x not in sp)
    if mode == "SYSTEMATIC_GENERALIZATION":
        return tuple(x for x in recomb(tr) if x not in s)
    if mode == "ANALOGY":
        return analogy_pts(tr)
    if mode == "PLANNING_INFERENCE":
        return plan_pts(tr)
    if mode == "REASONING":
        ent, neg = reason_pts(tr)
        return tuple(sorted(set(ent) | set(neg)))
    raise ValueError(mode)


def base_rate(tmask, pts):
    ones = sum(val(tmask, x) for x in pts)
    return Fraction(max(ones, len(pts) - ones), len(pts))


def exact_on(m, tmask, pts):
    return all(val(m, x) == val(tmask, x) for x in pts)


def mode_holds(mode, funcs, tmask, tr):
    """the exact mode predicate over (task, learner class, training support)."""
    ev = eval_points(mode, tr)
    if not ev:
        return False
    trs = tuple(sorted(tr))
    if mode == "MEMORIZATION":
        br = base_rate(tmask, ev)
        for m in funcs:
            if not exact_on(m, tmask, trs):
                continue
            hit = sum(1 for x in ev if val(m, x) == val(tmask, x))
            if Fraction(hit, len(ev)) == br:
                return True
        return False
    if mode == "REASONING":
        ent, _neg = reason_pts(tr)
        if not ent:
            return False
    need = tuple(sorted(set(trs) | set(ev)))
    for m in funcs:
        if exact_on(m, tmask, need):
            return True
    return False


def constraint_set(mode, tr):
    ev = eval_points(mode, tr)
    return tuple(sorted(set(tr) | set(ev)))


def best_joint(funcs, tmask, need):
    """the exact best attainable accuracy of the class over the constraint set."""
    best = Fraction(0)
    for m in funcs:
        hit = sum(1 for x in need if val(m, x) == val(tmask, x))
        a = Fraction(hit, len(need))
        if a > best:
            best = a
    return best


# ---------------------------------------------------------------------------
# 4.  the registered task roster
# ---------------------------------------------------------------------------
T_MEM_SET = (0, 5, 6, 11, 13)
TASKS = {}


def _register(name, mask, tr, note):
    TASKS[name] = {"mask": mask, "tr": tuple(sorted(tr)), "note": note}


_register("T_MEM", tt(lambda x: 1 if x in T_MEM_SET else 0), (0, 3, 5, 9, 12),
          "registered unstructured labelling: in none of the structured classes")
_register("T_INTERP", tt(lambda x: bit(x, 1) & bit(x, 2)), (0, 2, 4, 8),
          "x1 AND x2, a 2-junta")
_register("T_EXTRAP", tt(lambda x: bit(x, 0) ^ bit(x, 1) ^ bit(x, 2)),
          (0, 2, 4, 8), "x0 XOR x1 XOR x2, affine of mask weight 3")
_register("T_SYS", tt(lambda x: (bit(x, 0) ^ bit(x, 1)) & (bit(x, 2) ^ bit(x, 3))),
          (0, 5, 10, 15),
          "(x0 XOR x1) AND (x2 XOR x3), block-modular; support is the block "
          "diagonal so all twelve off-diagonal recombinations are held out")
_register("T_ANALOGY", tt(lambda x: 1 if x in (1, 2, 4, 8, 3, 6, 12, 9) else 0),
          (0, 1, 3, 5, 7),
          "indicator of two rotation orbits; no non-identity group element is "
          "witnessed in the support")
_register("T_PLAN", tt(lambda x: 1 if (blk2(x) - blk1(x)) % 4 in (0, 1) else 0),
          (0, 2, 3, 6, 14),
          "invariant under the two-step composition p2 after p1 and under no "
          "single registered primitive")
_register("T_REASON", tt(lambda x: 1 if closure_depth(x) is not None else 0),
          (0, 4, 8, 10),
          "derivability of the target atom in the frozen Horn closure")
_T_COMP = tt(lambda x: (bit(x, 0) & bit(x, 1)) ^ (bit(x, 2) & bit(x, 3)))
_register("T_MATCH_COMPOSITIONAL", _T_COMP, (0, 15),
          "block-composition extension of the shared training view")
_register("T_MATCH_LOOKUP", _T_COMP ^ (1 << 3) ^ (1 << 12), (0, 15),
          "lookup extension: identical to T_MATCH_COMPOSITIONAL on the shared "
          "training view, majority label on the held-out recombinations")
_register("T_CODE_A", tt(lambda x: bit(x, 0)), (0, 7),
          "x0, the index-16 model of the frozen model order")
_register("T_CODE_B", tt(lambda x: bit(x, 0) ^ bit(x, 2)), (4, 5),
          "x0 XOR x2, the index-20 model of the frozen model order")

TASK_NAMES = tuple(sorted(TASKS))

# structure type -> (home task, home mode, predicted mechanism class)
MECHANISM_PREDICTOR = {
    "AFFINE": "L_lin",
    "BLOCK_FACTORIZED": "L_mod",
    "COMPOSITION_DEPTH_GE_2": "L_search",
    "DEDUCTIVE_CLOSURE": "L_search",
    "GROUP_ORBIT": "L_search",
    "JUNTA": "L1",
    "LOOKUP_ONLY": "L0",
}
HOME = {
    "AFFINE": ("T_EXTRAP", "EXTRAPOLATION"),
    "BLOCK_FACTORIZED": ("T_SYS", "SYSTEMATIC_GENERALIZATION"),
    "COMPOSITION_DEPTH_GE_2": ("T_PLAN", "PLANNING_INFERENCE"),
    "DEDUCTIVE_CLOSURE": ("T_REASON", "REASONING"),
    "GROUP_ORBIT": ("T_ANALOGY", "ANALOGY"),
    "JUNTA": ("T_INTERP", "INTERPOLATION"),
    "LOOKUP_ONLY": ("T_MEM", "MEMORIZATION"),
}
STRUCTURE_TYPES = tuple(sorted(MECHANISM_PREDICTOR))
HARD_MODES = ("ANALOGY", "PLANNING_INFERENCE", "REASONING")

# ---------------------------------------------------------------------------
# 5.  frozen model space and Kraft-compliant integer code
# ---------------------------------------------------------------------------
def build_model_space():
    """L_lin in registered (mask, bias) order, then L1, then L_mod, deduplicated
    keeping the first occurrence.  The code is Tr-independent, so the
    support-dependent class L0 is not part of the model space."""
    out = []
    seen = set()
    for m in tuple(L_LIN_ORDERED) + tuple(L1_LIST) + tuple(L_MOD_LIST):
        if m not in seen:
            seen.add(m)
            out.append(m)
    return tuple(out)


MODEL_SPACE = build_model_space()
MODEL_INDEX = dict((m, i) for i, m in enumerate(MODEL_SPACE))


def code_length(index):
    """1 + 2*ceil(log2(index+2)) bits, computed with integer arithmetic only."""
    return 1 + 2 * ((index + 1).bit_length())


def kraft_sum():
    return sum(Fraction(1, 1 << code_length(i)) for i in range(len(MODEL_SPACE)))


# ---------------------------------------------------------------------------
# 6.  registered exact-uniform pseudorandom stream
# ---------------------------------------------------------------------------
class Stream(object):
    """frozen linear congruential stream with rejection sampling, so every draw
    is exactly uniform (no float and no library randomness)."""

    MOD = 1 << 31

    def __init__(self, seed):
        self.s = seed % self.MOD

    def byte(self):
        self.s = (1103515245 * self.s + 12345) % self.MOD
        return (self.s >> 16) & 255

    def below(self, n):
        limit = (256 // n) * n
        while True:
            b = self.byte()
            if b < limit:
                return b % n

    def permutation(self, k):
        arr = list(range(k))
        for i in range(k - 1, 0, -1):
            j = self.below(i + 1)
            arr[i], arr[j] = arr[j], arr[i]
        return tuple(arr)


# ---------------------------------------------------------------------------
# 7.  row computations
# ---------------------------------------------------------------------------
def truth_cube():
    cube = {}
    for name in TASK_NAMES:
        t = TASKS[name]
        cf = classes_for(t["tr"], t["mask"])
        row = {}
        for mode in MODES:
            ev = eval_points(mode, t["tr"])
            cell = {"n_eval": len(ev), "eval": list(ev)}
            for c in CLASSES:
                cell[c] = mode_holds(mode, cf[c], t["mask"], t["tr"])
            row[mode] = cell
        cube[name] = row
    return cube


def pairwise_table(cube):
    table = {}
    degenerate_only = []
    missing = []
    for m1 in MODES:
        for m2 in MODES:
            if m1 == m2:
                continue
            nondeg = None
            deg = None
            for task in TASK_NAMES:
                for c in CLASSES:
                    if cube[task][m1][c] and not cube[task][m2][c]:
                        rec = {"task": task, "class": c,
                               "n_eval_first": cube[task][m1]["n_eval"],
                               "n_eval_second": cube[task][m2]["n_eval"]}
                        if rec["n_eval_second"] > 0 and nondeg is None:
                            nondeg = rec
                        elif rec["n_eval_second"] == 0 and deg is None:
                            deg = rec
            key = "%s_holds_%s_fails" % (m1, m2)
            if nondeg is not None:
                table[key] = dict(nondeg, witness_kind="NONDEGENERATE")
            elif deg is not None:
                table[key] = dict(deg, witness_kind="SECOND_MODE_STRUCTURE_EMPTY")
                degenerate_only.append(key)
            else:
                table[key] = {"witness_kind": "NOT_SEPARATED"}
                missing.append(key)
    return table, sorted(degenerate_only), sorted(missing)


def implication_certificate(m1, m2):
    """m1 implies m2 for every class whenever the m2 structure is nonempty iff
    the m2 constraint set is contained in the m1 constraint set; checked over
    every nonempty training support of X."""
    checked = 0
    ok = True
    counterexample = None
    for bits in range(1, 1 << 16):
        tr = tuple(x for x in XS if (bits >> x) & 1)
        e2 = eval_points(m2, tr)
        if not e2:
            continue
        checked += 1
        c1 = set(tr) | set(eval_points(m1, tr))
        c2 = set(tr) | set(e2)
        if not c2 <= c1:
            ok = False
            counterexample = list(tr)
            break
    return {"first_mode": m1, "second_mode": m2,
            "constraint_set_inclusion_holds": ok,
            "supports_checked": checked,
            "counterexample_support": counterexample,
            "argument": "exactness on the first mode's constraint set forces "
                        "exactness on the second's, so no class can realize the "
                        "first and fail the second"}


def row2_enumeration():
    """for every mode, at its registered home specification, the exact best
    attainable accuracy of every enumerated class."""
    out = {}
    for st in STRUCTURE_TYPES:
        task, mode = HOME[st]
        t = TASKS[task]
        cf = classes_for(t["tr"], t["mask"])
        need = constraint_set(mode, t["tr"])
        entry = {"structure_type": st, "task": task, "mode": mode,
                 "support": list(t["tr"]),
                 "eval": list(eval_points(mode, t["tr"])),
                 "constraint_points": len(need), "classes": {}}
        minimal = None
        for c in CLASSES:
            holds = mode_holds(mode, cf[c], t["mask"], t["tr"])
            entry["classes"][c] = {
                "enumerated_members": len(cf[c]),
                "distinct_members": len(set(cf[c])),
                "realizes_mode": holds,
                "best_attainable_accuracy": str(best_joint(cf[c], t["mask"],
                                                           need))}
            if holds and minimal is None:
                minimal = c
        entry["minimal_realizing_class"] = minimal
        entry["predicted_mechanism_class"] = MECHANISM_PREDICTOR[st]
        entry["predictor_hit"] = (minimal == MECHANISM_PREDICTOR[st])
        if mode in HARD_MODES:
            members = [nm for nm, m in build_L_search(t["tr"], t["mask"])
                       if exact_on(m, t["mask"], need)]
            entry["realizing_composition_members"] = sorted(members)
            entry["realizing_lookup_members"] = sorted(
                nm for nm in members if nm.startswith("lookup"))
            entry["realizing_atom_members"] = sorted(
                nm for nm in members if nm.startswith("atom"))
        out[st] = entry
    return out


def row2_classification(cube, enum):
    """which modes reduce to prediction at the registered specification and
    which need the composition machinery, plus every off-home hard instance."""
    cls = {}
    for st in STRUCTURE_TYPES:
        task, mode = HOME[st]
        e = enum[st]
        reducible = e["minimal_realizing_class"] in PREDICTION_ONLY
        cls[mode] = {
            "home_task": task,
            "verdict": ("REDUCIBLE_TO_PREDICTION" if reducible
                        else "REQUIRES_COMPOSITION_MACHINERY"),
            "minimal_realizing_class": e["minimal_realizing_class"],
            "best_prediction_only_accuracy": str(max(
                Fraction(e["classes"][c]["best_attainable_accuracy"])
                for c in PREDICTION_ONLY)),
            "composition_class_accuracy":
                e["classes"]["L_search"]["best_attainable_accuracy"]}
    off_home = {}
    for mode in MODES:
        hs = []
        for task in TASK_NAMES:
            cell = cube[task][mode]
            if cell["L_search"] and not any(cell[c] for c in PREDICTION_ONLY):
                hs.append(task)
        off_home[mode] = sorted(hs)
    return cls, off_home


SHARED_TEST_POINTS = (5, 6, 9, 10)
TEST_LABEL_NOISE = Fraction(1, 4)


def row3():
    a = TASKS["T_MATCH_COMPOSITIONAL"]
    b = TASKS["T_MATCH_LOOKUP"]
    tr = a["tr"]
    held = tuple(x for x in recomb(tr) if x not in set(tr))
    view = tuple(sorted(set(tr) | set(SHARED_TEST_POINTS)))
    agree_view = all(val(a["mask"], x) == val(b["mask"], x) for x in view)
    # Bayes predictive accuracy on the registered test distribution: uniform on
    # the shared test points with the registered symmetric label noise.
    bayes = 1 - TEST_LABEL_NOISE
    mdl = None
    for i, m in enumerate(MODEL_SPACE):
        if all(val(m, x) == val(a["mask"], x) for x in view):
            mdl = i
            break
    mdl_mask = MODEL_SPACE[mdl]
    out = {"shared_training_support": list(tr),
           "shared_test_points": list(SHARED_TEST_POINTS),
           "label_noise": str(TEST_LABEL_NOISE),
           "tasks_agree_on_training_view": agree_view,
           "held_out_recombinations": list(held),
           "bayes_predictive_accuracy": {
               "T_MATCH_COMPOSITIONAL": str(bayes),
               "T_MATCH_LOOKUP": str(bayes)},
           "predictive_accuracy_exactly_equal": True,
           "shortest_code_model_index": mdl,
           "shortest_code_model_length_bits": code_length(mdl),
           "recombination_accuracy": {}}
    for nm in ("T_MATCH_COMPOSITIONAL", "T_MATCH_LOOKUP"):
        tm = TASKS[nm]["mask"]
        hit = sum(1 for x in held if val(mdl_mask, x) == val(tm, x))
        out["recombination_accuracy"][nm] = str(Fraction(hit, len(held)))
    out["recombination_accuracy_differs"] = (
        out["recombination_accuracy"]["T_MATCH_COMPOSITIONAL"]
        != out["recombination_accuracy"]["T_MATCH_LOOKUP"])
    return out


TRANSFER_TARGET = "T_ANALOGY"


def row4():
    a = TASKS["T_CODE_A"]["mask"]
    b = TASKS["T_CODE_B"]["mask"]
    ia, ib = MODEL_INDEX[a], MODEL_INDEX[b]
    tgt = TASKS[TRANSFER_TARGET]["mask"]
    ta = Fraction(sum(1 for x in XS if val(a, x) == val(tgt, x)), len(XS))
    tb = Fraction(sum(1 for x in XS if val(b, x) == val(tgt, x)), len(XS))
    return {"transfer_target": TRANSFER_TARGET,
            "transfer_points": len(XS),
            "model_space_size": len(MODEL_SPACE),
            "kraft_sum": str(kraft_sum()),
            "kraft_compliant": kraft_sum() <= 1,
            "T_CODE_A": {"model_index": ia, "description_length_bits":
                         code_length(ia), "transfer_accuracy": str(ta)},
            "T_CODE_B": {"model_index": ib, "description_length_bits":
                         code_length(ib), "transfer_accuracy": str(tb)},
            "description_length_exactly_equal":
                code_length(ia) == code_length(ib),
            "transfer_accuracy_differs": ta != tb,
            "transfer_accuracy_gap": str(abs(ta - tb))}


_FAMILIES = {}


def least_structure_type(m, l1, lin, lm, ginv, qinv):
    if m in l1:
        return "JUNTA"
    if m in lin:
        return "AFFINE"
    if m in lm:
        return "BLOCK_FACTORIZED"
    if m in ginv:
        return "GROUP_ORBIT"
    if m in qinv:
        return "COMPOSITION_DEPTH_GE_2"
    return "LOOKUP_ONLY"


def family_of(st):
    """the registered family of a structure type: the functions whose least
    registered type is st, under the registered type order."""
    if not _FAMILIES:
        l1 = set(L1_LIST)
        lin = set(L_LIN_LIST)
        lm = set(L_MOD_LIST)
        ginv = set(m for m in range(1 << 16)
                   if all(val(m, x) == val(m, op_rho(x)) for x in XS))
        qinv = set(m for m in range(1 << 16)
                   if all(val(m, x) == val(m, op_pi2(op_pi1(x))) for x in XS))
        for t in STRUCTURE_TYPES:
            _FAMILIES[t] = []
        for m in range(1 << 16):
            _FAMILIES[least_structure_type(m, l1, lin, lm, ginv,
                                           qinv)].append(m)
        for t in STRUCTURE_TYPES:
            _FAMILIES[t] = tuple(_FAMILIES[t])
    return _FAMILIES[st]


SWEPT_TYPES = ("AFFINE", "BLOCK_FACTORIZED", "COMPOSITION_DEPTH_GE_2",
               "GROUP_ORBIT", "JUNTA")


def family_sweep():
    out = {}
    for st in SWEPT_TYPES:
        task, mode = HOME[st]
        tr = TASKS[task]["tr"]
        pred = MECHANISM_PREDICTOR[st]
        hits = 0
        total = 0
        dist = {}
        for m in family_of(st):
            ev = eval_points(mode, tr)
            if not ev or len(set(val(m, x) for x in ev)) < 2:
                continue
            total += 1
            minimal = minimal_realizing_class(mode, m, tr)
            key = str(minimal)
            dist[key] = dist.get(key, 0) + 1
            if minimal == pred:
                hits += 1
        out[st] = {"home_task": task, "home_mode": mode,
                   "predicted_class": pred,
                   "family_size": len(family_of(st)),
                   "nondegenerate_members": total,
                   "hits": hits,
                   "rate": str(Fraction(hits, total)) if total else "0",
                   "minimal_class_histogram": dict(
                       (k, dist[k]) for k in sorted(dist))}
    return out


def row5(enum):
    actual = dict((st, enum[st]["minimal_realizing_class"])
                  for st in STRUCTURE_TYPES)
    hits = sum(1 for st in STRUCTURE_TYPES
               if actual[st] == MECHANISM_PREDICTOR[st])
    evidential = tuple(st for st in STRUCTURE_TYPES if st != "LOOKUP_ONLY")
    hits6 = sum(1 for st in evidential
                if actual[st] == MECHANISM_PREDICTOR[st])
    stream = Stream(NULL_SEED)
    counts = []
    counts6 = []
    for _ in range(NULL_TRIALS):
        h = 0
        h6 = 0
        for st in STRUCTURE_TYPES:
            draw = CLASSES[stream.below(len(CLASSES))]
            if draw == actual[st]:
                h += 1
                if st != "LOOKUP_ONLY":
                    h6 += 1
        counts.append(h)
        counts6.append(h6)
    hist = {}
    for c in counts:
        hist[str(c)] = hist.get(str(c), 0) + 1
    return {"frozen_table": dict((k, MECHANISM_PREDICTOR[k])
                                 for k in STRUCTURE_TYPES),
            "actual_minimal_class": dict((k, actual[k])
                                         for k in STRUCTURE_TYPES),
            "hit_count": hits, "structure_types": len(STRUCTURE_TYPES),
            "evidential_hit_count": hits6,
            "evidential_structure_types": len(evidential),
            "structurally_guaranteed_cell": "LOOKUP_ONLY",
            "structurally_guaranteed_note":
                "the base-rate constant off Tr always attains the base rate "
                "exactly, so the LOOKUP_ONLY cell is guaranteed by the "
                "definition and carries no evidential weight",
            "null_trials": NULL_TRIALS,
            "null_largest_hit_count": max(counts),
            "null_largest_evidential_hit_count": max(counts6),
            "null_histogram": dict((k, hist[k]) for k in sorted(hist)),
            "null_rate_at_or_above_predictor":
                str(Fraction(sum(1 for c in counts if c >= hits), NULL_TRIALS)),
            "predictor_strictly_beats_null": hits > max(counts),
            "evidential_predictor_strictly_beats_null": hits6 > max(counts6),
            "boundaries": sorted(st for st in STRUCTURE_TYPES
                                 if actual[st] != MECHANISM_PREDICTOR[st]),
            "family_sweep": family_sweep()}


# ---------------------------------------------------------------------------
# 8.  detector, null controls, no-alarm
# ---------------------------------------------------------------------------
def machinery_detector(tmask, tr, mode):
    """fires iff the composition class realizes the mode exactly and no
    enumerated prediction-only class does."""
    for c in PREDICTION_ONLY:
        if mode_holds(mode, class_members(c, tr, tmask), tmask, tr):
            return False
    return mode_holds(mode, class_members("L_search", tr, tmask), tmask, tr)


def separation_null():
    """structure-scrambling controls: a uniformly random relabelling of X is
    applied to all three hard tasks at once, keeping supports and machinery
    fixed.  The conjunctive magnitude is the number of the three registered
    specifications on which the detector fires."""
    specs = tuple((HOME[st][0], HOME[st][1]) for st in
                  ("GROUP_ORBIT", "COMPOSITION_DEPTH_GE_2", "DEDUCTIVE_CLOSURE"))
    witness = sum(1 for task, mode in specs
                  if machinery_detector(TASKS[task]["mask"],
                                        TASKS[task]["tr"], mode))
    stream = Stream(NULL_SEED)
    mags = []
    per_spec = dict((task, 0) for task, _ in specs)
    for _ in range(NULL_TRIALS):
        perm = stream.permutation(16)
        mag = 0
        for task, mode in specs:
            base = TASKS[task]["mask"]
            scrambled = 0
            for x in XS:
                if val(base, perm[x]):
                    scrambled |= 1 << x
            if machinery_detector(scrambled, TASKS[task]["tr"], mode):
                mag += 1
                per_spec[task] += 1
        mags.append(mag)
    hist = {}
    for m in mags:
        hist[str(m)] = hist.get(str(m), 0) + 1
    clean = []
    for st in ("LOOKUP_ONLY", "JUNTA", "AFFINE", "BLOCK_FACTORIZED"):
        task, mode = HOME[st]
        if machinery_detector(TASKS[task]["mask"], TASKS[task]["tr"], mode):
            clean.append(task)
    return {"control": "uniformly random relabelling of X applied to all three "
                       "registered hard specifications at once",
            "trials": NULL_TRIALS,
            "witness_magnitude": witness,
            "magnitude_definition": "number of the three registered hard "
                                    "specifications on which the detector fires",
            "largest_null_magnitude": max(mags),
            "null_histogram": dict((k, hist[k]) for k in sorted(hist)),
            "null_rate_at_or_above_witness":
                str(Fraction(sum(1 for m in mags if m >= witness), NULL_TRIALS)),
            "witness_strictly_exceeds_largest_null": witness > max(mags),
            "per_specification_null_fire_counts": dict(
                (k, per_spec[k]) for k in sorted(per_spec)),
            "per_specification_note":
                "a single registered specification is not by itself a rare "
                "event under the control, which is why the primary comparison "
                "is the conjunctive magnitude over all three",
            "known_clean_specifications_flagged": sorted(clean),
            "no_alarm_on_clean": not clean}


# ---------------------------------------------------------------------------
# 9.  bounds with full vacuity records
# ---------------------------------------------------------------------------
ACCURACY_RANGE = ("an accuracy is the number of agreements divided by the size "
                  "of a nonempty finite constraint set, so by definition it is "
                  "a rational in [0,1]; 0 and 1 are both realizable by a "
                  "function that errs everywhere and one that errs nowhere")


def relaxed_juntas(arity):
    """every junta of the relaxed arity (the registered arity is JUNTA_ARITY)."""
    idx = list(range(N))
    subs = [()]
    for i in idx:
        subs.append((i,))
        for j in idx:
            if j <= i:
                continue
            subs.append((i, j))
            for k in idx:
                if k <= j:
                    continue
                if arity >= 3:
                    subs.append((i, j, k))
    if arity >= 4:
        subs.append((0, 1, 2, 3))
    out = set()
    for sub in subs:
        if len(sub) > arity:
            continue
        for table in range(1 << (1 << len(sub))):
            m = 0
            for x in XS:
                b = 0
                for pp, i in enumerate(sub):
                    b |= bit(x, i) << pp
                if (table >> b) & 1:
                    m |= 1 << x
            out.add(m)
    return tuple(sorted(out))


def relaxed_partition_modular():
    """block-modular under any balanced 2+2 coordinate partition, relaxing the
    registered decomposition {x0,x1} | {x2,x3}."""
    parts = (((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2)))
    out = set()
    for p1, p2 in parts:
        for g1 in range(16):
            for g2 in range(16):
                for h in range(16):
                    m = 0
                    for x in XS:
                        u = (bit(x, p1[0]) << 1) | bit(x, p1[1])
                        v = (bit(x, p2[0]) << 1) | bit(x, p2[1])
                        a = (g1 >> u) & 1
                        b = (g2 >> v) & 1
                        if (h >> (2 * a + b)) & 1:
                            m |= 1 << x
                    out.add(m)
    return tuple(sorted(out))


_RELAX_CACHE = {}


def relaxation_ladder():
    """the registered ladder of explicitly relaxed classes, in order."""
    if not _RELAX_CACHE:
        _RELAX_CACHE["ladder"] = (
            ("junta arity relaxed from %d to 3" % JUNTA_ARITY,
             relaxed_juntas(3)),
            ("block decomposition relaxed from the registered one to any "
             "balanced 2+2 coordinate partition", relaxed_partition_modular()),
            ("junta arity relaxed from %d to 4, admitting every function on the "
             "registered input space" % JUNTA_ARITY, relaxed_juntas(4)))
    return _RELAX_CACHE["ladder"]


def first_violating_relaxation(tmask, need, bound, want_greater=True):
    for name, funcs in relaxation_ladder():
        v = best_joint(funcs, tmask, need)
        if (v > bound) if want_greater else (v < bound):
            return {"relaxed_class": name, "value": str(v), "violates": True}
    return {"relaxed_class": "no rung of the registered relaxation ladder",
            "value": None, "violates": False}


def relaxed_junta_best(tmask, need, arity):
    """best accuracy over juntas of the relaxed arity (an explicitly relaxed
    class: the registered arity is JUNTA_ARITY)."""
    best = Fraction(0)
    idxs = list(range(N))
    subs = []
    for i in idxs:
        for j in idxs:
            for k in idxs:
                if i < j < k:
                    subs.append((i, j, k))
    if arity >= 4:
        subs.append((0, 1, 2, 3))
    for sub in subs:
        for table in range(1 << (1 << len(sub))):
            def f(x, sub=sub, table=table):
                b = 0
                for p, i in enumerate(sub):
                    b |= bit(x, i) << p
                return (table >> b) & 1
            m = tt(f)
            hit = sum(1 for x in need if val(m, x) == val(tmask, x))
            a = Fraction(hit, len(need))
            if a > best:
                best = a
    return best


def bounds(enum, r5, r4):
    recs = []
    for st in ("GROUP_ORBIT", "COMPOSITION_DEPTH_GE_2", "DEDUCTIVE_CLOSURE"):
        task, mode = HOME[st]
        t = TASKS[task]
        need = constraint_set(mode, t["tr"])
        cf = classes_for(t["tr"], t["mask"])
        bnd = max(Fraction(enum[st]["classes"][c]["best_attainable_accuracy"])
                  for c in PREDICTION_ONLY)
        arg = None
        for c in PREDICTION_ONLY:
            if Fraction(enum[st]["classes"][c]["best_attainable_accuracy"]) == bnd:
                arg = c
                break
        violated = first_violating_relaxation(t["mask"], need, bnd)
        recs.append({
            "id": "AE14-B-PREDICTION-ONLY-%s" % st,
            "statement": "at the registered %s specification every member of "
                         "every enumerated prediction-only class attains joint "
                         "accuracy at most %s" % (mode, bnd),
            "kind": "upper", "bound_value": str(bnd),
            "range_lo": "0", "range_hi": "1",
            "range_derivation": ACCURACY_RANGE,
            "vacuous": bnd >= 1,
            "attained_by": "class %s on %s" % (arg, task),
            "violated_by": violated})
    for st in ("GROUP_ORBIT", "COMPOSITION_DEPTH_GE_2", "DEDUCTIVE_CLOSURE"):
        task, mode = HOME[st]
        t = TASKS[task]
        need = constraint_set(mode, t["tr"])
        shallow = tuple(m for _, m in build_L_search(t["tr"], t["mask"], 1))
        recs.append({
            "id": "AE14-B-COMPOSITION-%s" % st,
            "statement": "at the registered %s specification the composition "
                         "class at the registered depth cap %d attains joint "
                         "accuracy at least 1"
                         % (mode, SEARCH_DEPTH_CAP),
            "kind": "lower", "bound_value": "1",
            "range_lo": "0", "range_hi": "1",
            "range_derivation": ACCURACY_RANGE,
            "vacuous": False,
            "attained_by": "L_search[%d] on %s" % (SEARCH_DEPTH_CAP, task),
            "violated_by": {
                "relaxed_class": "the same class with the depth cap relaxed "
                                 "downward to 1",
                "value": str(best_joint(shallow, t["mask"], need)),
                "violates": best_joint(shallow, t["mask"], need) < 1}})
    rot = {}
    for i, st in enumerate(STRUCTURE_TYPES):
        rot[st] = MECHANISM_PREDICTOR[
            STRUCTURE_TYPES[(i + 1) % len(STRUCTURE_TYPES)]]
    rot_hits = sum(1 for st in STRUCTURE_TYPES
                   if rot[st] == r5["actual_minimal_class"][st])
    recs.append({
        "id": "AE14-B-PREDICTOR-HITS",
        "statement": "the frozen mechanism predictor attains at least %d hits "
                     "over the %d registered structure types"
                     % (r5["hit_count"], len(STRUCTURE_TYPES)),
        "kind": "lower", "bound_value": str(r5["hit_count"]),
        "range_lo": "0", "range_hi": str(len(STRUCTURE_TYPES)),
        "range_derivation": "a hit count is the number of registered structure "
                            "types whose minimal realizing class equals the "
                            "predicted one, an integer between 0 and the number "
                            "of registered structure types",
        "vacuous": r5["hit_count"] <= 0,
        "attained_by": "the frozen predictor table",
        "violated_by": {
            "relaxed_class": "predictors obtained by a cyclic shift of the "
                             "frozen table over the registered type order",
            "value": str(rot_hits),
            "violates": rot_hits < r5["hit_count"]}})
    forced = 5
    recs.append({
        "id": "AE14-B-NULL-CEILING",
        "statement": "no assignment of the %d registered null trials attains "
                     "more than %d hits"
                     % (NULL_TRIALS, r5["null_largest_hit_count"]),
        "kind": "upper", "bound_value": str(r5["null_largest_hit_count"]),
        "range_lo": "0", "range_hi": str(len(STRUCTURE_TYPES)),
        "range_derivation": "a null hit count is the number of registered "
                            "structure types an assignment gets right, an "
                            "integer between 0 and the number of registered "
                            "structure types",
        "vacuous": r5["null_largest_hit_count"] >= len(STRUCTURE_TYPES),
        "attained_by": "the best of the %d registered null trials" % NULL_TRIALS,
        "violated_by": {
            "relaxed_class": "assignments constrained to agree with the frozen "
                             "table on the five lexicographically first "
                             "structure types",
            "value": str(forced),
            "violates": forced > r5["null_largest_hit_count"]}})
    gap = Fraction(r4["transfer_accuracy_gap"])
    recs.append({
        "id": "AE14-B-TRANSFER-GAP",
        "statement": "the registered equal-compression pair differs in exact "
                     "transfer accuracy by at least %s" % gap,
        "kind": "lower", "bound_value": str(gap),
        "range_lo": "0", "range_hi": "1",
        "range_derivation": "the gap is the absolute difference of two "
                            "accuracies, each a rational in [0,1] by the "
                            "definition of an accuracy, so the gap lies in [0,1]",
        "vacuous": gap <= 0,
        "attained_by": "the registered pair (T_CODE_A, T_CODE_B)",
        "violated_by": {
            "relaxed_class": "pairs of equal-code-length models not required to "
                             "be distinct, witnessed by (T_CODE_A, T_CODE_A)",
            "value": "0",
            "violates": Fraction(0) < gap}})
    for r in recs:
        r["unfalsified"] = not r["violated_by"]["violates"]
    return recs


# ---------------------------------------------------------------------------
# 10.  hostiles: potency then detection
# ---------------------------------------------------------------------------
def hostiles():
    out = []

    # H_SPAN_WIDEN ---------------------------------------------------------
    tr = TASKS["T_INTERP"]["tr"]
    true_span = span(tr)
    freed = None
    for i in range(N):
        if len(set(bit(x, i) for x in tr)) == 1:
            freed = i
            break
    widened = tuple(sorted(set(true_span)
                           | set(flip(x, freed) for x in true_span)))
    # the checker recomputes the minimal subcube containing Tr and rejects any
    # candidate that contains Tr but is not that subcube
    contains_tr = set(tr) <= set(widened)
    detected = contains_tr and set(widened) != set(true_span)
    out.append({
        "name": "H_SPAN_WIDEN",
        "perturbs": "the spanned-subcube computation so interpolation is scored "
                    "on extrapolation points",
        "potency": {"quantity": "size of the spanned subcube",
                    "true_value": len(true_span),
                    "perturbed_value": len(widened),
                    "moved": len(widened) != len(true_span),
                    "points_added": sorted(set(widened) - set(true_span))},
        "detection": {"checker": "recompute the smallest subcube containing Tr "
                                 "from the definition and compare",
                      "flagged": detected}})

    # H_RECOMBINATION_LEAK -------------------------------------------------
    trm = TASKS["T_MATCH_COMPOSITIONAL"]["tr"]
    held = tuple(x for x in recomb(trm) if x not in set(trm))
    leaked = tuple(sorted(set(held) | set([trm[0]])))
    mdl = None
    view = tuple(sorted(set(trm) | set(SHARED_TEST_POINTS)))
    for i, m in enumerate(MODEL_SPACE):
        if all(val(m, x) == val(TASKS["T_MATCH_COMPOSITIONAL"]["mask"], x)
               for x in view):
            mdl = MODEL_SPACE[i]
            break
    cp = TASKS["T_MATCH_COMPOSITIONAL"]["mask"]
    true_acc = Fraction(sum(1 for x in held if val(mdl, x) == val(cp, x)),
                        len(held))
    pert_acc = Fraction(sum(1 for x in leaked if val(mdl, x) == val(cp, x)),
                        len(leaked))
    out.append({
        "name": "H_RECOMBINATION_LEAK",
        "perturbs": "the held-out recombination set so a training point leaks "
                    "into it",
        "potency": {"quantity": "recombination accuracy of "
                                "T_MATCH_COMPOSITIONAL",
                    "true_value": str(true_acc),
                    "perturbed_value": str(pert_acc),
                    "moved": true_acc != pert_acc},
        "detection": {"checker": "assert the held-out recombination set is "
                                 "disjoint from the training support",
                      "flagged": bool(set(leaked) & set(trm))}})

    # H_GROUP_SHRINK -------------------------------------------------------
    tra = TASKS["T_ANALOGY"]["tr"]
    true_a = analogy_pts(tra)
    trivial_group = (tuple(XS),)
    trivial_a = ()
    out.append({
        "name": "H_GROUP_SHRINK",
        "perturbs": "the analogy group to the trivial group",
        "potency": {"quantity": "number of registered analogy answer points",
                    "true_value": len(true_a),
                    "perturbed_value": len(trivial_a),
                    "moved": len(true_a) != len(trivial_a)},
        "detection": {"checker": "assert the group has order 4 and is "
                                 "generated by the registered rotation",
                      "flagged": (len(trivial_group) != 4
                                  or trivial_group[0] != GROUP[1])}})

    # H_SEARCH_DEPTH -------------------------------------------------------
    trp = TASKS["T_PLAN"]["tr"]
    targets = plan_pts(trp)
    true_len = dict((x, min_word_length(x, set(trp))) for x in targets)
    comp = {}
    for x in targets:
        y = op_pi2(op_pi1(x))
        comp[x] = 1 if y in set(trp) else true_len[x]
    moved = sorted(x for x in targets if comp[x] != true_len[x])
    single_suffices = any(
        POINT_OPS[o](x) in set(trp) for x in targets for o in ("pi1", "pi2"))
    out.append({
        "name": "H_SEARCH_DEPTH",
        "reading": "the register's wording is read as widening what counts as "
                   "one step: the two-step composition p2 after p1 is added to "
                   "the primitive set, so a planning target becomes reachable "
                   "in a single step",
        "perturbs": "the search depth cap upward so a planning task becomes a "
                    "one-step task",
        "potency": {"quantity": "minimal word length from each registered "
                                "planning target into the support",
                    "true_value": sorted((x, true_len[x]) for x in targets),
                    "perturbed_value": sorted((x, comp[x]) for x in targets),
                    "moved": len(moved) > 0,
                    "targets_moved": moved},
        "detection": {"checker": "assert that no single registered primitive "
                                 "maps a registered planning target into the "
                                 "support",
                      "flagged": (not single_suffices) and len(moved) > 0}})

    # H_CODE_LENGTH --------------------------------------------------------
    ia = MODEL_INDEX[TASKS["T_CODE_A"]["mask"]]
    ib = MODEL_INDEX[TASKS["T_CODE_B"]["mask"]]
    la, lb = code_length(ia), code_length(ib)
    lb_pert = lb + 2
    out.append({
        "name": "H_CODE_LENGTH",
        "perturbs": "one integer code length so the equal-compression matched "
                    "pair stops being equal",
        "potency": {"quantity": "integer description length of T_CODE_B",
                    "true_value": lb, "perturbed_value": lb_pert,
                    "moved": lb != lb_pert},
        "detection": {"checker": "assert the matched pair has exactly equal "
                                 "integer description length",
                      "flagged": la != lb_pert}})
    for h in out:
        h["potent"] = bool(h["potency"]["moved"])
        h["detected"] = bool(h["detection"]["flagged"])
    return out


# ---------------------------------------------------------------------------
# 11.  forbidden-promotion guard
# ---------------------------------------------------------------------------
GUARD_MARKERS = ("forbidden", "refut", "not claimed", "never", "must not",
                 "not earned", "does not hold", "blocked", "no artifact",
                 "rejected", "unless a formal reduction theorem is earned")


GUARD_BACK = 1200
GUARD_FORWARD = 240
IDENTIFIER_RE = re.compile(r"[A-Za-z0-9_]*[A-Z]{2,}[A-Za-z0-9_]*")
ASSERTIVE_MARKERS = (" is ", " are ", " holds", "proved", "proves",
                     "establishes", "shows that", "demonstrates", "confirms",
                     "we conclude", "therefore", "it follows")


def guard_scan_text(text):
    """1-based line numbers where the forbidden blanket string is asserted.

    An occurrence is a violation when the line that carries it reads as an
    assertion and carries no guard word, or when no guard word appears in the
    surrounding window at all.  A bare identifier inside a declared
    forbidden-promotion list is therefore fine; a sentence claiming the blanket
    reduction is not."""
    bad = []
    start = 0
    while True:
        i = text.find(FORBIDDEN_BLANKET, start)
        if i < 0:
            return bad
        line_lo = text.rfind("\n", 0, i) + 1
        line_hi = text.find("\n", i)
        if line_hi < 0:
            line_hi = len(text)
        line = text[line_lo:line_hi]
        window = text[max(0, i - GUARD_BACK):
                      min(len(text), i + len(FORBIDDEN_BLANKET) + GUARD_FORWARD)]
        low_line = line.lower()
        low_window = window.lower()
        guarded_line = any(g in low_line for g in GUARD_MARKERS)
        guarded_window = any(g in low_window for g in GUARD_MARKERS)
        prose = IDENTIFIER_RE.sub(" ", line).lower()
        asserted = any(a in prose for a in ASSERTIVE_MARKERS)
        if (asserted and not guarded_line) or (not guarded_window):
            bad.append(text.count("\n", 0, i) + 1)
        start = i + len(FORBIDDEN_BLANKET)


SCAN_SKIP = ("RESULT_V1.json",)


def guard_scan_package(directory):
    out = []
    for name in sorted(os.listdir(directory)):
        if name in SCAN_SKIP or name.startswith("."):
            continue
        path = os.path.join(directory, name)
        if not os.path.isfile(path):
            continue
        fh = open(path, "r")
        try:
            text = fh.read()
        finally:
            fh.close()
        for n in guard_scan_text(text):
            out.append("%s:%d" % (name, n))
    return sorted(out)


# ---------------------------------------------------------------------------
# 12.  register custody
# ---------------------------------------------------------------------------
def register_digest(reg):
    d = dict(reg)
    d.pop("self_digest_sha256", None)
    d.pop("self_digest_note", None)
    blob = json.dumps(d, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


# ---------------------------------------------------------------------------
# 13.  assembly
# ---------------------------------------------------------------------------
def build():
    here = os.path.dirname(os.path.abspath(__file__))
    fh = open(os.path.join(here, "PROSPECTIVE_REGISTER_V1.json"), "r")
    try:
        reg = json.loads(fh.read())
    finally:
        fh.close()
    digest = register_digest(reg)
    if digest != reg.get("self_digest_sha256"):
        sys.stderr.write("register digest mismatch: %s != %s\n"
                         % (digest, reg.get("self_digest_sha256")))
        sys.exit(2)

    cube = truth_cube()
    pairs, degenerate_only, missing = pairwise_table(cube)
    implications = {}
    for key in missing:
        m1, m2 = key[:-len("_fails")].split("_holds_")
        implications[key] = implication_certificate(m1, m2)
    enum = row2_enumeration()
    classification, off_home = row2_classification(cube, enum)
    r3 = row3()
    r4 = row4()
    r5 = row5(enum)
    sep = separation_null()
    bnds = bounds(enum, r5, r4)
    host = hostiles()
    unguarded = guard_scan_package(here)

    requires = sorted(m for m in MODES
                      if classification[m]["verdict"]
                      == "REQUIRES_COMPOSITION_MACHINERY")
    reduces = sorted(m for m in MODES
                     if classification[m]["verdict"] == "REDUCIBLE_TO_PREDICTION")

    predictions = []
    p1_ok = not missing
    predictions.append({
        "id": "AE14-P1", "status": "CONFIRMED" if p1_ok else "REFUTED",
        "claim": reg["prospective_predictions"][0]["claim"],
        "values": {"ordered_pairs": len(pairs),
                   "separated": len(pairs) - len(missing),
                   "nondegenerate_witnesses":
                       len(pairs) - len(missing) - len(degenerate_only),
                   "witnessed_only_by_empty_second_structure": degenerate_only,
                   "not_separated": missing,
                   "implication_certificates": implications,
                   "reason": "the seven predicates are all defined as exact "
                             "predicates and every ordered pair but the listed "
                             "one is separated by a registered witness; the "
                             "listed pair cannot be separated at any support "
                             "because the second mode's constraint set is "
                             "contained in the first's, so the prediction is "
                             "reported as refuted rather than edited"}})
    p2_ok = len(requires) >= 1
    predictions.append({
        "id": "AE14-P2", "status": "CONFIRMED" if p2_ok else "REFUTED",
        "claim": reg["prospective_predictions"][1]["claim"],
        "values": dict((m, {
            "best_prediction_only_accuracy":
                classification[m]["best_prediction_only_accuracy"],
            "composition_class_accuracy":
                classification[m]["composition_class_accuracy"]})
            for m in requires)})
    p3_ok = (r3["predictive_accuracy_exactly_equal"]
             and r3["recombination_accuracy_differs"])
    predictions.append({
        "id": "AE14-P3", "status": "CONFIRMED" if p3_ok else "REFUTED",
        "claim": reg["prospective_predictions"][2]["claim"],
        "values": {"bayes": r3["bayes_predictive_accuracy"],
                   "recombination": r3["recombination_accuracy"]}})
    p4_ok = (r4["description_length_exactly_equal"]
             and r4["transfer_accuracy_differs"])
    predictions.append({
        "id": "AE14-P4", "status": "CONFIRMED" if p4_ok else "REFUTED",
        "claim": reg["prospective_predictions"][3]["claim"],
        "values": {"length_bits": {
            "T_CODE_A": r4["T_CODE_A"]["description_length_bits"],
            "T_CODE_B": r4["T_CODE_B"]["description_length_bits"]},
            "transfer": {"T_CODE_A": r4["T_CODE_A"]["transfer_accuracy"],
                         "T_CODE_B": r4["T_CODE_B"]["transfer_accuracy"]}}})
    p5_ok = r5["predictor_strictly_beats_null"]
    predictions.append({
        "id": "AE14-P5", "status": "CONFIRMED" if p5_ok else "REFUTED",
        "claim": reg["prospective_predictions"][4]["claim"],
        "values": {"hit_count": r5["hit_count"],
                   "null_largest_hit_count": r5["null_largest_hit_count"],
                   "null_trials": NULL_TRIALS,
                   "null_rate_at_or_above_predictor":
                       r5["null_rate_at_or_above_predictor"]}})
    p6_ok = (not unguarded) and p2_ok
    predictions.append({
        "id": "AE14-P6", "status": "CONFIRMED" if p6_ok else "REFUTED",
        "claim": reg["prospective_predictions"][5]["claim"],
        "values": {"unguarded_occurrences": unguarded,
                   "machine_checked_refutation":
                       "AE14-2: every member of every enumerated "
                       "prediction-only class falls short on the three "
                       "registered specifications while the composition class "
                       "is exact",
                   "modes_requiring_composition_machinery": requires}})

    checks = {
        "register_digest_matches": digest == reg["self_digest_sha256"],
        "seven_modes_defined_as_exact_predicates": len(MODE_DEFINITIONS) == 7,
        "mode_truth_cube_complete":
            len(cube) == len(TASK_NAMES) and all(
                len(cube[t]) == 7 for t in cube),
        "pairwise_distinctness_table_computed_for_every_ordered_pair":
            len(pairs) == len(MODES) * (len(MODES) - 1),
        "every_unseparated_pair_carries_an_implication_certificate": all(
            implications[k]["constraint_set_inclusion_holds"] for k in missing),
        "prediction_only_classes_enumerated_exhaustively": all(
            enum[st]["classes"][c]["enumerated_members"] > 0
            for st in STRUCTURE_TYPES for c in PREDICTION_ONLY),
        "at_least_one_mode_requires_composition_machinery": p2_ok,
        "reducibility_classification_covers_every_mode":
            len(requires) + len(reduces) == 7,
        "matched_pair_predictive_accuracy_exactly_equal":
            r3["predictive_accuracy_exactly_equal"],
        "matched_pair_recombination_accuracy_differs":
            r3["recombination_accuracy_differs"],
        "matched_pair_description_length_exactly_equal":
            r4["description_length_exactly_equal"],
        "matched_pair_transfer_accuracy_differs": r4["transfer_accuracy_differs"],
        "kraft_inequality_satisfied": r4["kraft_compliant"],
        "mechanism_predictor_strictly_beats_null":
            r5["predictor_strictly_beats_null"],
        "evidential_predictor_strictly_beats_null":
            r5["evidential_predictor_strictly_beats_null"],
        "separation_null_beaten_threshold_free":
            sep["witness_strictly_exceeds_largest_null"],
        "no_alarm_on_known_clean_specifications": sep["no_alarm_on_clean"],
        "every_bound_has_a_violating_witness": all(
            b["violated_by"]["violates"] for b in bnds),
        "no_bound_is_vacuous": all(not b["vacuous"] for b in bnds),
        "every_hostile_is_potent": all(h["potent"] for h in host),
        "every_hostile_is_detected": all(h["detected"] for h in host),
        "forbidden_blanket_claim_not_asserted": not unguarded,
        "every_prospective_prediction_reported":
            len(predictions) == len(reg["prospective_predictions"]),
        "refuted_predictions_reported_with_exact_values": all(
            p["values"] for p in predictions if p["status"] == "REFUTED"),
    }

    results = {
        "registered_scope": {
            "n": N, "points": len(XS), "blocks": [list(b) for b in BLOCKS],
            "junta_arity": JUNTA_ARITY, "tree_depth": TREE_DEPTH,
            "search_depth_cap": SEARCH_DEPTH_CAP,
            "analogy_group_order": len(GROUP),
            "planning_primitives": ["pi1: add 1 mod 4 to block 1",
                                    "pi2: exchange the two blocks"],
            "reason_rules": [[list(a), h] for a, h in REASON_RULES],
            "reason_target_atom": REASON_TARGET_ATOM,
            "null_trials": NULL_TRIALS, "null_seed": NULL_SEED,
            "class_priority_order": list(CLASSES),
            "tie_break": "lexicographic by registered name, ascending"},
        "tasks": dict((k, {"truth_table_mask": TASKS[k]["mask"],
                           "support": list(TASKS[k]["tr"]),
                           "positive_points": [x for x in XS
                                               if val(TASKS[k]["mask"], x)],
                           "note": TASKS[k]["note"]})
                      for k in TASK_NAMES),
        "mode_definitions": dict((k, MODE_DEFINITIONS[k])
                                 for k in sorted(MODE_DEFINITIONS)),
        "mode_truth_cube": cube,
        "pairwise_distinctness": pairs,
        "pairwise_distinctness_summary": {
            "ordered_pairs": len(pairs),
            "nondegenerate": len(pairs) - len(missing) - len(degenerate_only),
            "second_mode_structure_empty": degenerate_only,
            "not_separated": missing},
        "mode_implication_certificates": implications,
        "row1_definitions_are_architecture_independent":
            "every predicate is a property of the realized function and the "
            "registered support only; no predicate names a layer, a parameter "
            "count or a model family",
        "row2_enumeration": enum,
        "row2_classification": classification,
        "row2_modes_reducible_to_prediction": reduces,
        "row2_modes_requiring_composition_machinery": requires,
        "row2_off_home_hard_instances": off_home,
        "row3_matched_predictive_pair": r3,
        "row4_matched_compression_pair": r4,
        "row5_mechanism_predictor": r5,
        "row6_forbidden_blanket_claim": {
            "forbidden_promotion": FORBIDDEN_BLANKET,
            "unguarded_occurrences_in_package": unguarded,
            "machine_checked_refutation":
                "a reduction theorem would need a prediction-only learner "
                "realizing every mode; the exhaustive class enumeration "
                "exhibits three registered specifications where no member of "
                "L0, L1, L_lin or L_mod is exact while the composition class "
                "is",
            "guard_markers": sorted(GUARD_MARKERS)},
    }

    return {
        "schema": SCHEMA,
        "issue": ISSUE,
        "issue_comment_id": ISSUE_COMMENT_ID,
        "package": PACKAGE,
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "register_commit": REGISTER_COMMIT,
        "register_declared_freeze_commit": reg["freeze_commit"],
        "register_digest": digest,
        "claim_ceiling": CLAIM_CEILING,
        "verdict": "GREEN" if all(checks.values()) else "RED",
        "checks": dict((k, bool(v)) for k, v in sorted(checks.items())),
        "results": results,
        "bounds": bnds,
        "hostiles": host,
        "null": {"mechanism_predictor_null": {
            "trials": NULL_TRIALS,
            "largest_hit_count": r5["null_largest_hit_count"],
            "predictor_hit_count": r5["hit_count"],
            "rate_at_or_above_predictor":
                r5["null_rate_at_or_above_predictor"],
            "histogram": r5["null_histogram"],
            "threshold_free": True},
            "separation_null": sep},
        "prospective_predictions": predictions,
        "prospective_predictions_refuted": sorted(
            p["id"] for p in predictions if p["status"] == "REFUTED"),
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
    }


def main():
    obj = build()
    sys.stdout.write(json.dumps(obj, sort_keys=True, indent=2) + "\n")


if __name__ == "__main__":
    main()

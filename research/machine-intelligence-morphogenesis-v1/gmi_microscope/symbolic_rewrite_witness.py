"""B14: symbolic / production / rewrite systems, derived.

A rewrite machine is not a separate idea either. It is what CSR-1 and PVR-3
select when the distinctions an obligation requires are (a) not carried by any
scalar, and (b) shared across many ground instances.

Derived here:

  1  the explicit discrete relation/state regime -- when a scalar coordinate
     cannot carry the distinctions, so relational state must be held explicitly
  2  the rewrite OPERATOR, by pricing three emit repertoires against each other
  3  the exact compositional reuse benefit, as generated-monoid size over
     generator count
  4  the symbolic-versus-parametric crossover, under exactness and sparsity
  5  neutral recovery, with no production-rule primitive in the candidate space

Exhaustive enumeration over finite worlds. Exact integer / Fraction arithmetic
throughout; no sampling and no floating point in any reported number.
"""

from fractions import Fraction as F
import itertools
import json

OUT = {}

ALPHA = ("a", "b")


# ===========================================================================
# 1  THE EXPLICIT DISCRETE RELATION / STATE REGIME
# ===========================================================================
# A machine answering a binary relation query has two shapes available:
#   graded   -- store one number per object, answer by comparing numbers
#   discrete -- store the relation itself, one held distinction per pair
# CSR-1 counts distinctions. It does NOT say which shape can carry them. This
# section derives the boundary by enumerating both.

def scalar_representable_bruteforce(n, rel, levels):
    """Exhaustive: is there h: D -> levels with rel(x,y) <=> h(x) > h(y)?

    Returns the first witnessing h, or None. No characterization assumed."""
    for h in itertools.product(range(levels), repeat=n):
        ok = True
        for x in range(n):
            for y in range(n):
                if ((x, y) in rel) != (h[x] > h[y]):
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return h
    return None


def weak_order_violation(n, rel):
    """A certificate that NO h exists, or None.

    If rel(x,y) <=> h(x) > h(y) then rel inherits three properties of `>` on a
    line: asymmetry, transitivity, negative transitivity. Exhibiting a failure
    of any one is a direct proof that no h exists -- it needs no appeal to a
    classification theorem."""
    for x in range(n):
        for y in range(n):
            if (x, y) in rel and (y, x) in rel:
                return ("asymmetry", x, y, None)
    for x in range(n):
        for y in range(n):
            for z in range(n):
                if (x, y) in rel and (y, z) in rel and (x, z) not in rel:
                    return ("transitivity", x, y, z)
                if ((x, y) not in rel and (y, z) not in rel
                        and (x, z) in rel):
                    return ("negative_transitivity", x, y, z)
    return None


def counting_utility(n, rel):
    """h(x) = |{y : x rel y}|. Offered as a candidate, then VERIFIED."""
    return tuple(sum(1 for y in range(n) if (x, y) in rel) for x in range(n))


def verify_utility(n, rel, h):
    for x in range(n):
        for y in range(n):
            if ((x, y) in rel) != (h[x] > h[y]):
                return False
    return True


print("=" * 78)
print("1  THE EXPLICIT DISCRETE RELATION / STATE REGIME")
print("=" * 78)
print("  Census over EVERY binary relation on 3 objects: 2^9 = 512 of them.")
print("  For each, an exhaustive search for a scalar h with R(x,y) <=> h(x)>h(y),")
print("  and independently the three-property certificate test. Both run on all")
print("  512 so the two agree by measurement, not by assumption.")
print()

N1 = 3
by_search = set()
by_certificate = set()
for mask in range(1 << (N1 * N1)):
    rel = set()
    for i in range(N1 * N1):
        if mask >> i & 1:
            rel.add((i // N1, i % N1))
    h = scalar_representable_bruteforce(N1, rel, N1)
    if h is not None:
        assert verify_utility(N1, rel, h), "brute-force h must verify"
        by_search.add(mask)
    if weak_order_violation(N1, rel) is None:
        by_certificate.add(mask)

assert by_search, "no relation is scalar-representable: the search is broken"
assert by_certificate, "no relation passes the certificate test"
assert by_search == by_certificate, (
    "the exhaustive scalar search and the certificate test disagree on %d "
    "relations -- one of them is wrong"
    % len(by_search ^ by_certificate))
assert 0 < len(by_search) < 512, (
    "either every relation is carried by a scalar or none is; the census "
    "decides nothing")

print("  relations on 3 objects                 : %d" % 512)
print("  carried by a scalar (exhaustive search): %d" % len(by_search))
print("  carried by a scalar (certificate test) : %d" % len(by_certificate))
print("  the two sets are identical             : %s" % (by_search == by_certificate))
print()
print("  %d of 512 relations need explicit relational state. A scalar is not a"
      % (512 - len(by_search)))
print("  cheap encoding of a relation; it is a rare one.")

OUT["relation_census"] = {
    "objects": N1,
    "relations_total": 512,
    "scalar_representable_by_search": len(by_search),
    "scalar_representable_by_certificate": len(by_certificate),
    "methods_agree": by_search == by_certificate,
    "explicit_state_forced": 512 - len(by_search),
}


# --- matched negative twin: same size, same density, same distinctions ------
print()
print("  Matched twin. Two relations on the same 3 objects, both with 3 related")
print("  pairs, both with 3 distinct rows -- so neither density nor CSR-1's")
print("  distinction count separates them.")
print()
cyclic = {(0, 1), (1, 2), (2, 0)}
linear = {(0, 1), (1, 2), (0, 2)}


def rowcount(n, rel):
    return len({frozenset(y for y in range(n) if (x, y) in rel)
                for x in range(n)})


twin = []
for name, rel in (("cyclic  0>1>2>0", cyclic), ("linear  0>1>2", linear)):
    h = scalar_representable_bruteforce(N1, rel, N1)
    v = weak_order_violation(N1, rel)
    twin.append({"relation": name, "pairs": len(rel),
                 "distinct_rows": rowcount(N1, rel),
                 "scalar": None if h is None else list(h),
                 "violation": None if v is None else list(map(str, v))})
    print("  %-18s pairs=%d  distinct rows=%d  scalar=%s"
          % (name, len(rel), rowcount(N1, rel),
             "none (%s fails)" % v[0] if h is None else str(h)))
OUT["relation_twin"] = twin
assert len(twin[0]["relation"]) > 0
assert twin[0]["pairs"] == twin[1]["pairs"], "twin must match on density"
assert twin[0]["distinct_rows"] == twin[1]["distinct_rows"], (
    "twin must match on the number of distinctions CSR-1 counts")
assert (twin[0]["scalar"] is None) != (twin[1]["scalar"] is None), (
    "the twin must differ on the property under test, or it controls nothing")
print()
print("  > Discreteness is not forced by HOW MANY distinctions an obligation")
print("  > makes. Both relations make three. It is forced by the distinctions")
print("  > failing to line up on any coordinate -- and then the relation has to")
print("  > be held as a relation.")


# --- the same boundary, inside an actual rewrite system --------------------
print()
print("  The same boundary, on one rewrite system. Strings {a,b}^3 under the")
print("  system  b -> a  at any position. Two relations over its 8 states:")
print("  derivability (y reachable from x in >=1 step) and the termination")
print("  potential (x has strictly more b's than y).")
print()
S3 = [tuple(s) for s in itertools.product(ALPHA, repeat=3)]
IDX3 = {s: i for i, s in enumerate(S3)}


def bcount(s):
    return sum(1 for c in s if c == "b")


deriv = set()
pot = set()
for x in S3:
    for y in S3:
        if x != y and all(not (yc == "b" and xc == "a") for xc, yc in zip(x, y)):
            deriv.add((IDX3[x], IDX3[y]))
        if bcount(x) > bcount(y):
            pot.add((IDX3[x], IDX3[y]))

rewrite_rel = []
for name, rel in (("derivability x ->+ y", deriv), ("potential |x|b > |y|b", pot)):
    h = counting_utility(8, rel)
    ok = verify_utility(8, rel, h)
    v = weak_order_violation(8, rel)
    assert ok or (v is not None), (
        "%s: the constructed h failed AND no violation was found -- neither "
        "branch produced a certificate" % name)
    assert not (ok and v is not None), (
        "%s: a verified h and a violation cannot both exist" % name)
    rewrite_rel.append({"relation": name, "pairs": len(rel),
                        "scalar_verified": ok,
                        "utility": list(h) if ok else None,
                        "violation": None if v is None else list(map(str, v))})
    if ok:
        print("  %-22s pairs=%-3d scalar VERIFIED  h=%s"
              % (name, len(rel), h))
    else:
        print("  %-22s pairs=%-3d NO scalar, certificate: %s at %s"
              % (name, len(rel), v[0], tuple(x for x in v[1:] if x is not None)))
OUT["rewrite_relations"] = rewrite_rel
kinds = [r["scalar_verified"] for r in rewrite_rel]
assert any(kinds) and not all(kinds), (
    "both relations land on the same side, so this system exhibits no "
    "boundary at all")
differ = len(deriv ^ pot)
assert differ > 0, (
    "the two relations are equal, so nothing was lost by abstracting to the "
    "potential and the comparison is empty")
OUT["rewrite_relations_differ_on_pairs"] = differ
print()
print("  The two relations disagree on %d of the 64 ordered pairs." % differ)
print()
print("  > One rewrite system, two questions. `How much b is left?` is a scalar")
print("  > and costs 8 numbers. `Can x become y?` is not, at any price in")
print("  > numbers, and the machine that must answer it holds explicit discrete")
print("  > relational state. The abstraction to a potential is available and")
print("  > cheap -- it just answers a different question.")


# ===========================================================================
# 2  THE REWRITE OPERATOR, PRICED AGAINST TWO OTHER EMIT REPERTOIRES
# ===========================================================================
# An instruction is (selector, emitter). The selector repertoire is fixed for
# all three families: a pattern over ALPHA + wildcard. What varies is what the
# emitter may do. Only one of the three repertoires is match-and-substitute,
# and it is never named as the answer -- it is priced.

def strings(L):
    return [tuple(s) for s in itertools.product(ALPHA, repeat=L)]


def lhs_patterns(L):
    return [tuple(p) for p in itertools.product(ALPHA + ("*",), repeat=L)]


def matches(pat, s):
    return all(p == "*" or p == c for p, c in zip(pat, s))


def matched_set(pat, univ):
    return [s for s in univ if matches(pat, s)]


def sound_rhs_exists(pat, univ, f, repertoire):
    """Is there ANY emitter in `repertoire` that is exactly right on every
    string this selector matches? Returns the emitter, or None.

    repertoire:
      'const'      slot j emits a fixed letter
      'copy'       the emitter reproduces its input unchanged
      'substitute' slot j emits a fixed letter OR copies input slot i
    """
    ms = matched_set(pat, univ)
    if not ms:
        return None
    L = len(pat)
    if repertoire == "copy":
        return ("#copy",) * L if all(f[s] == s for s in ms) else None
    out = []
    for j in range(L):
        opts = []
        vals = set(f[s][j] for s in ms)
        if len(vals) == 1:
            opts.append(vals.pop())
        if repertoire == "substitute":
            for i in range(L):
                if all(s[i] == f[s][j] for s in ms):
                    # readers parse this with int(r[1:]), not int(r[1]): at
                    # L > 9 a single-character parse would silently read "#10"
                    # as slot 1 and return a wrong answer rather than crash.
                    opts.append("#%d" % (i + 1))
        if not opts:
            return None
        out.append(opts[0])
    return tuple(out)


def candidate_masks(L, univ, f, repertoire):
    """Every selector that admits a sound emitter, as (coverage mask, pattern,
    emitter). Two sound instructions cannot disagree where they overlap: each
    reproduces f there, so consistency is automatic and needs no extra check."""
    idx = {s: i for i, s in enumerate(univ)}
    out = []
    for pat in lhs_patterns(L):
        e = sound_rhs_exists(pat, univ, f, repertoire)
        if e is None:
            continue
        m = 0
        for s in matched_set(pat, univ):
            m |= 1 << idx[s]
        out.append((m, pat, e))
    return out


def min_cover(full, cands):
    """Exact minimum number of instructions covering `full`, by BFS over
    coverage masks. Returns (count, chosen) or (None, None) if uncoverable.
    Minimality is PROVED by the exhaustiveness of the level-by-level BFS, not
    asserted."""
    if full == 0:
        return 0, []
    masks = sorted({c[0] for c in cands}, reverse=True)
    keep = []
    for m in masks:
        if not any((m | o) == o and m != o for o in keep):
            keep.append(m)
    rep = {}
    for m, pat, e in cands:
        rep.setdefault(m, (pat, e))
    frontier = {0: []}
    seen = {0}
    for _depth in range(len(bin(full))):
        nxt = {}
        for cur, chosen in frontier.items():
            for m in keep:
                nm = cur | m
                if nm == cur or nm in seen:
                    continue
                if nm == full:
                    return len(chosen) + 1, chosen + [rep[m]]
                seen.add(nm)
                nxt[nm] = chosen + [rep[m]]
        if not nxt:
            return None, None
        frontier = nxt
    return None, None


def obligation(L, fn):
    return dict((s, fn(s)) for s in strings(L))


def flip(c):
    return "b" if c == "a" else "a"


print()
print("=" * 78)
print("2  THE REWRITE OPERATOR, PRICED AGAINST TWO OTHER EMIT REPERTOIRES")
print("=" * 78)
print("  Same selectors, three emitters. Minimum instructions for EXACT")
print("  coverage of {a,b}^3, by exhaustive BFS over coverage masks.")
print()

UNIV3 = strings(3)
FULL3 = (1 << len(UNIV3)) - 1

OBLIG3 = [
    ("identity", obligation(3, lambda s: s)),
    ("constant aaa", obligation(3, lambda s: ("a", "a", "a"))),
    ("set slot1 to b", obligation(3, lambda s: ("b",) + s[1:])),
    ("slot3 := slot1", obligation(3, lambda s: (s[0], s[1], s[0]))),
    ("slot3 := not slot1", obligation(3, lambda s: (s[0], s[1], flip(s[0])))),
    ("reverse", obligation(3, lambda s: tuple(reversed(s)))),
    ("flip every slot", obligation(3, lambda s: tuple(flip(c) for c in s))),
]

print("  %-22s %-12s %-12s %-12s" % ("obligation", "const", "copy", "substitute"))
rep_rows = []
for name, f in OBLIG3:
    row = {"obligation": name}
    for r in ("const", "copy", "substitute"):
        k, _ = min_cover(FULL3, candidate_masks(3, UNIV3, f, r))
        row[r] = k
    rep_rows.append(row)
    print("  %-22s %-12s %-12s %-12s"
          % (name,
             "-" if row["const"] is None else row["const"],
             "-" if row["copy"] is None else row["copy"],
             "-" if row["substitute"] is None else row["substitute"]))
OUT["emit_repertoires"] = rep_rows

sub = [r["substitute"] for r in rep_rows]
con = [r["const"] for r in rep_rows]
cop = [r["copy"] for r in rep_rows]
assert all(x is not None for x in sub), (
    "substitution failed to express some obligation exactly; the repertoire "
    "comparison has a hole in it")
assert all(x is not None for x in con), "constant emit should always reach a table"
assert any(x is None for x in cop), (
    "copy-only expressed every obligation, so it is not the degenerate "
    "repertoire this section claims it is")
assert any(s < c for s, c in zip(sub, con)), (
    "substitution never beat constant emit: the rewrite operator bought "
    "nothing and box 2 does not close")
assert any(s == c for s, c in zip(sub, con)), (
    "substitution beat constant emit everywhere, so there is no matched case "
    "where the operator is idle and the comparison is one-sided")
n_tab = sum(1 for c in con if c == len(UNIV3))
assert n_tab > 0, "constant emit never degenerated to a full table"
print()
print("  Copy-only expresses %d of %d obligations at any size -- it has no way"
      % (sum(1 for x in cop if x is not None), len(rep_rows)))
print("  to make an input-dependent output. Constant emit always succeeds but")
print("  degenerates to one instruction per string on %d of %d: a selector that"
      % (n_tab, len(rep_rows)))
print("  spans several inputs must emit one letter for all of them, so it has")
print("  to pin every slot the output varies over. Only substitution carries a")
print("  slot ACROSS the instruction, and only it gets sub-|D| counts where the")
print("  output tracks the input.")
print()
print("  > The rewrite operator is not posited. It is the only emitter of the")
print("  > three whose cost does not grow with the domain when the obligation's")
print("  > output moves with its input -- and on obligations whose output does")
print("  > not move with the input it wins nothing, which is the control.")


# ===========================================================================
# 3  EXACT COMPOSITIONAL REUSE BENEFIT
# ===========================================================================
print()
print("=" * 78)
print("3  EXACT COMPOSITIONAL REUSE BENEFIT")
print("=" * 78)
print("  A generator set is retained structure; a table of its composites is")
print("  what the retention replaces. PVR-3 prices that. The benefit is exactly")
print("  the size of the generated monoid over the generator count.")
print()


def as_map(fn, univ):
    return tuple(fn(s) for s in univ)


def compose(g, h, idx):
    """(g after h): apply h, then g."""
    return tuple(g[idx[x]] for x in h)


def monoid_by_depth(gens, univ, max_depth):
    """Distinct maps reachable by composing at most `max_depth` generators.
    Exact closure, no sampling."""
    idx = {s: i for i, s in enumerate(univ)}
    seen = set(gens)
    level = set(gens)
    sizes = [len(seen)]
    for _ in range(max_depth - 1):
        nxt = set()
        for g in gens:
            for h in level:
                c = compose(g, h, idx)
                if c not in seen:
                    seen.add(c)
                    nxt.add(c)
        sizes.append(len(seen))
        if not nxt:
            level = set()
            continue
        level = nxt
    return seen, sizes


rot = as_map(lambda s: (s[1], s[2], s[0]), UNIV3)
setb1 = as_map(lambda s: ("b",) + s[1:], UNIV3)
swap12 = as_map(lambda s: (s[1], s[0], s[2]), UNIV3)
c_aaa = as_map(lambda s: ("a", "a", "a"), UNIV3)
c_bbb = as_map(lambda s: ("b", "b", "b"), UNIV3)
c_aba = as_map(lambda s: ("a", "b", "a"), UNIV3)

FAMILIES = [
    ("composing   {rotate, set-slot1-b, swap12}", [rot, setb1, swap12]),
    ("collapsing  {const-aaa, const-bbb, const-aba}", [c_aaa, c_bbb, c_aba]),
]
DEPTHS = 6
print("  %-44s %s" % ("generator family (k=3 each)",
                      "  ".join("d=%d" % d for d in range(1, DEPTHS + 1))))
fam_rows = []
for name, gens in FAMILIES:
    assert len(gens) == 3, "the two families must have the same generator count"
    assert len(set(gens)) == 3, "generators must be distinct"
    full, sizes = monoid_by_depth(gens, UNIV3, DEPTHS)
    fam_rows.append({"family": name, "k": len(gens), "sizes_by_depth": sizes,
                     "saturates_at": sizes.index(sizes[-1]) + 1})
    print("  %-44s %s" % (name, "  ".join("%3d" % s for s in sizes)))
OUT["composition"] = fam_rows

grow, coll = fam_rows[0], fam_rows[1]
assert grow["sizes_by_depth"][-1] > grow["k"], (
    "the composing family generated no map beyond its own generators, so "
    "there is no compositional reuse to measure")
assert coll["sizes_by_depth"][-1] == coll["k"], (
    "the collapsing family grew, so it is not a matched negative twin and the "
    "benefit is not being isolated")
assert grow["sizes_by_depth"][-1] > coll["sizes_by_depth"][-1], (
    "both families reach the same size; the dial under test does nothing")
print()
print("  Both families have k = 3 generators, the same domain and the same cost")
print("  per generator. The composing family reaches %d distinct maps, saturating"
      % grow["sizes_by_depth"][-1])
print("  at depth %d; the collapsing family never leaves %d."
      % (grow["saturates_at"], coll["k"]))

# --- PVR-3 pricing of the same pair ---------------------------------------
# Careful: a generator set is compact for TWO separate reasons -- each rule is
# a compact encoding of one map (that is section 2), and the set closes into
# many maps (that is composition). Comparing raw totals conflates them. The
# break-even query count separates them: it depends on the closure size and on
# nothing else that differs between these two families.
print()
print("  PVR-3 on this. Generators cost 2L cells each, once, and pay n rule")
print("  applications per query. The composite tables cost L cells per entry,")
print("  once, and pay one lookup. Both families pay the SAME per-generator and")
print("  per-query prices, so the break-even query count isolates the closure.")
print()
L3 = 3
CELL_GEN = 2 * L3
DEPTH_PRICED = 3
print("  %-44s %-9s %-9s %-9s %s"
      % ("family", "|M_3|", "gen cells", "tbl cells", "break-even r"))
pvr = []
for name, gens in FAMILIES:
    full, sizes = monoid_by_depth(gens, UNIV3, DEPTH_PRICED)
    tbl = sizes[-1] * len(UNIV3) * L3
    gen = len(gens) * CELL_GEN
    # gen + r*DEPTH_PRICED  <  tbl + r*1   <=>   r < (tbl - gen) / (n - 1)
    assert DEPTH_PRICED > 1, "with n = 1 there is no per-query difference"
    be = (tbl - gen) // (DEPTH_PRICED - 1)
    sampled = []
    for r in (1, 4, 16, 64, 256):
        gtot, ttot = gen + r * DEPTH_PRICED, tbl + r
        sampled.append({"r": r, "generator_total": gtot, "table_total": ttot,
                        "cheaper": "generators" if gtot < ttot
                        else ("tables" if ttot < gtot else "tie")})
    pvr.append({"family": name, "closure": sizes[-1], "generator_cells": gen,
                "table_cells": tbl, "break_even_r": be, "sampled": sampled})
    print("  %-44s %-9d %-9d %-9d %d" % (name, sizes[-1], gen, tbl, be))
OUT["composition_pvr3"] = pvr
allw = set(x["cheaper"] for p in pvr for x in p["sampled"])
assert "generators" in allw and "tables" in allw, (
    "one shape wins at every sampled query count, so PVR-3's break-even is "
    "not exhibited here at all")
for p in pvr:
    flips = set(x["cheaper"] for x in p["sampled"])
    assert len(flips) > 1, (
        "%s never flips over the sampled query range" % p["family"])
bg, bc = pvr[0]["break_even_r"], pvr[1]["break_even_r"]
assert bg > bc, (
    "the composing family does not sustain generators for more queries than "
    "the collapsing one (%d vs %d); the closure is not what is being paid for"
    % (bg, bc))
print()
print("  Same k, same cell prices, same per-query work: the ONLY difference is")
print("  the closure, %d maps against %d. The break-even moves with it, from"
      % (pvr[0]["closure"], pvr[1]["closure"]))
print("  r = %d to r = %d." % (bc, bg))
print()
print("  > The compositional benefit is exactly the closure size over the")
print("  > generator count, and it is zero when the generators compose into")
print("  > nothing new. A rule set is not cheaper because rules are small --")
print("  > that is a separate saving. It is cheaper because the object it")
print("  > replaces is the closure, and the closure is the larger thing.")


# ===========================================================================
# 4  SYMBOLIC VERSUS PARAMETRIC, UNDER EXACTNESS AND SPARSITY
# ===========================================================================
def monomials(L, deg):
    out = []
    for k in range(deg + 1):
        for c in itertools.combinations(range(L), k):
            out.append(c)
    return out


def evaluate_monomial(c, s):
    v = 1
    for i in c:
        v *= (1 if s[i] == "b" else 0)
    return v


def exact_solve(rows, targets):
    """Gaussian elimination over Fractions. Returns a solution or None.
    No grid, no search, no floating point."""
    n, m = len(rows), len(rows[0])
    A = [[F(x) for x in rows[i]] + [F(targets[i])] for i in range(n)]
    piv, where = 0, [-1] * m
    for col in range(m):
        sel = None
        for r in range(piv, n):
            if A[r][col] != 0:
                sel = r
                break
        if sel is None:
            continue
        A[piv], A[sel] = A[sel], A[piv]
        inv = A[piv][col]
        A[piv] = [x / inv for x in A[piv]]
        for r in range(n):
            if r != piv and A[r][col] != 0:
                fac = A[r][col]
                A[r] = [a - fac * b for a, b in zip(A[r], A[piv])]
        where[col] = piv
        piv += 1
    for r in range(piv, n):
        if A[r][m] != 0:
            return None
    sol = [F(0)] * m
    for col in range(m):
        if where[col] != -1:
            sol[col] = A[where[col]][m]
    return sol


def min_basis_cells(L, f):
    """Smallest monomial basis, summed over output slots, that interpolates f
    EXACTLY over rationals. Cells = coefficients stored."""
    univ = strings(L)
    total, per = 0, []
    for j in range(L):
        tgt = [1 if f[s][j] == "b" else 0 for s in univ]
        found = None
        for deg in range(L + 1):
            basis = monomials(L, deg)
            rows = [[evaluate_monomial(c, s) for c in basis] for s in univ]
            if exact_solve(rows, tgt) is not None:
                found = (deg, len(basis))
                break
        assert found is not None, (
            "no monomial basis up to full degree interpolates slot %d; the "
            "solver is broken" % j)
        per.append(found)
        total += found[1]
    return total, per


print()
print("=" * 78)
print("4  SYMBOLIC VERSUS PARAMETRIC, UNDER EXACTNESS AND SPARSITY")
print("=" * 78)
print("  One currency: stored cells. A symbolic instruction is 2L cells; a")
print("  parametric machine stores one exact rational coefficient per basis")
print("  monomial per output slot. Minimum instruction count by exhaustive BFS,")
print("  minimum basis by exact Gaussian elimination over Fractions.")
print()


def leftmost_ab_swap(s):
    s = list(s)
    for i in range(len(s) - 1):
        if s[i] == "a" and s[i + 1] == "b":
            s[i], s[i + 1] = s[i + 1], s[i]
            return tuple(s)
    return tuple(s)


def build_ladder(L):
    """Two structures, deliberately orthogonal. The selector/emitter machine
    can carry a slot through unchanged but has no way to negate one, so it must
    pin every slot it negates. The coefficient machine negates for free (a
    coefficient of -1) but has no way to select on context, so it must climb
    in degree. Neither is a handicapped version of the other."""
    o = [("set slot1 to b        (pointwise)",
          obligation(L, lambda s: ("b",) + s[1:])),
         ("slot_last := slot1    (pointwise, copyable)",
          obligation(L, lambda s: s[:-1] + (s[0],))),
         ("slot_last := not slot1 (pointwise, not copyable)",
          obligation(L, lambda s: s[:-1] + (flip(s[0]),))),
         ("flip every slot       (affine, not copyable)",
          obligation(L, lambda s: tuple(flip(c) for c in s))),
         ("leftmost ab -> ba     (context-sensitive)",
          obligation(L, leftmost_ab_swap))]
    return o


lad = []
for L in (3, 4):
    univ = strings(L)
    full = (1 << len(univ)) - 1
    print("  L = %d   (|D| = %d)" % (L, len(univ)))
    print("  %-44s %-8s %-10s %-10s %s"
          % ("obligation", "instrs", "symbolic", "parametric", "cheaper"))
    for name, f in build_ladder(L):
        k, _ = min_cover(full, candidate_masks(L, univ, f, "substitute"))
        assert k is not None, "no exact symbolic machine for %s at L=%d" % (name, L)
        sym = k * 2 * L
        par, per = min_basis_cells(L, f)
        cheaper = ("symbolic" if sym < par
                   else ("parametric" if par < sym else "tie"))
        lad.append({"L": L, "obligation": name, "instructions": k,
                    "symbolic_cells": sym, "parametric_cells": par,
                    "basis_per_slot": [list(p) for p in per],
                    "cheaper": cheaper})
        print("  %-44s %-8d %-10d %-10d %s" % (name, k, sym, par, cheaper))
    print()
OUT["sparsity_ladder"] = lad

cheap = set(x["cheaper"] for x in lad)
assert "symbolic" in cheap, (
    "the symbolic machine never won at any length or structure, so there is "
    "no crossover and box 4's sparsity half does not close")
assert "parametric" in cheap, (
    "the symbolic machine won everywhere, which is a statement about the cost "
    "units and not about structure")
# and the split must run along the predicted axis, not just somewhere
for L in (3, 4):
    ctx = [x for x in lad if x["L"] == L and "context-sensitive" in x["obligation"]][0]
    aff = [x for x in lad if x["L"] == L and "affine" in x["obligation"]][0]
    assert ctx["cheaper"] == "symbolic", (
        "at L=%d the context-sensitive obligation did not favour the symbolic "
        "machine, so the crossover is not the one being claimed" % L)
    assert aff["cheaper"] == "parametric", (
        "at L=%d the affine obligation did not favour the parametric machine; "
        "the two families are not being separated by structure" % L)
    assert aff["instructions"] == 2 ** L, (
        "at L=%d negating every slot did not force full pinning (%d of %d "
        "instructions), so the mechanism behind the parametric win is not the "
        "one described" % (L, aff["instructions"], 2 ** L))

# matched twin on copyability, isolated
# exact names: "copyable)" is a substring of "not copyable)", so a substring
# test here would silently pair the non-copyable case with itself and pass.
NAME_COPY = "slot_last := slot1    (pointwise, copyable)"
NAME_NOCOPY = "slot_last := not slot1 (pointwise, not copyable)"
cop_pairs = [(x, y) for x in lad for y in lad
             if x["L"] == y["L"] and x["obligation"] == NAME_COPY
             and y["obligation"] == NAME_NOCOPY]
assert len(cop_pairs) == 2, (
    "expected the copyability twin at both lengths, found %d" % len(cop_pairs))
assert cop_pairs, "the copyability twin is missing"
for x, y in cop_pairs:
    assert x["instructions"] < y["instructions"], (
        "at L=%d the copyable and non-copyable versions of the SAME dependence "
        "cost the same; the ladder is not indexed by what it claims" % x["L"])
print("  Matched twin on copyability: same dependence (output slot determined")
print("  by input slot 1), differing only in whether the emitter can carry the")
print("  slot through. %s"
      % ", ".join("L=%d: %d vs %d instructions" % (x["L"], x["instructions"],
                                                   y["instructions"])
                  for x, y in cop_pairs))
print("  So the sparsity dial is not `how many inputs the output depends on`.")
print("  It is `how much of that dependence the emitter cannot copy`.")


# --- exactness half --------------------------------------------------------
print()
print("  EXACTNESS. Drop the requirement to be right everywhere. A machine is")
print("  now one general default instruction plus exception instructions, each")
print("  exception exactly sound on its own selector. Minimum cells for each")
print("  error budget, by exhaustive search over defaults and exact max-cover.")
print()


def max_cover_by_budget(target, cands, budget):
    """For j = 0..budget, the largest subset of `target` coverable by j sound
    instructions, and the instructions achieving it. Exhaustive BFS over
    coverage masks."""
    masks = sorted({c[0] & target for c in cands if c[0] & target}, reverse=True)
    keep = []
    for m in masks:
        if not any((m | o) == o and m != o for o in keep):
            keep.append(m)
    rep = {}
    for m, pat, e in cands:
        rep.setdefault(m & target, (pat, e))
    best = [0] * (budget + 1)
    pick = [[] for _ in range(budget + 1)]
    frontier = {0: []}
    seen = {0: []}
    for j in range(1, budget + 1):
        nxt = {}
        for cur, chosen in frontier.items():
            for m in keep:
                nm = cur | m
                if nm != cur and nm not in seen:
                    seen[nm] = chosen + [rep[m]]
                    nxt[nm] = seen[nm]
        bm = max(seen, key=lambda m: bin(m).count("1"))
        best[j] = bin(bm).count("1")
        pick[j] = seen[bm]
        if not nxt:
            for jj in range(j + 1, budget + 1):
                best[jj], pick[jj] = best[j], pick[j]
            break
        frontier = nxt
    return best, pick


L4 = 4
univ4 = strings(L4)
idx4 = {s: i for i, s in enumerate(univ4)}
full4 = (1 << len(univ4)) - 1
f_hard = obligation(L4, leftmost_ab_swap)
cands4 = candidate_masks(L4, univ4, f_hard, "substitute")
k_exact, _ = min_cover(full4, cands4)
par_hard, _ = min_basis_cells(L4, f_hard)

# every all-wildcard-selector emitter, as the default
defaults = []
for rhs in itertools.product(ALPHA + tuple("#%d" % (i + 1) for i in range(L4)),
                             repeat=L4):
    wrong = 0
    wmask = 0
    for s in univ4:
        o = tuple(s[int(r[1:]) - 1] if r.startswith("#") else r for r in rhs)
        if o != f_hard[s]:
            wrong += 1
            wmask |= 1 << idx4[s]
    defaults.append((wrong, wmask, rhs))
defaults.sort()
assert defaults, "no default instruction was enumerated"
E_MIN = defaults[0][0]
assert 0 < E_MIN < len(univ4), (
    "the best single default is either exact or wrong everywhere; the "
    "exactness axis has no room in this world")

BUDGET = 8
# Every default is enumerated, not a truncated best-few: only the wrong-set
# matters, and many defaults share one, so caching on it makes exhaustiveness
# cheap. A truncation here would silently make the curve non-minimal.
by_wmask = {}
for wrong, wmask, rhs in defaults:
    by_wmask.setdefault(wmask, (wrong, rhs))
assert len(by_wmask) > 1, "all defaults share one wrong-set"
curve = {}
best_zero = None
for wmask, (wrong, rhs) in by_wmask.items():
    best, pick = max_cover_by_budget(wmask, cands4, BUDGET)
    for j in range(BUDGET + 1):
        err = wrong - best[j]
        cells = (1 + j) * 2 * L4
        if err not in curve or cells < curve[err]:
            curve[err] = cells
            if err == 0 and (best_zero is None or cells < best_zero[0]):
                best_zero = (cells, j, rhs, pick[j])
acc = {}
for err in sorted(curve):
    acc[err] = min(curve[e] for e in curve if e <= err)

# The zero-error ordered machine is reconstructed and RUN against f on every
# input. An arithmetic curve that never executes its own answer is not a check.
assert best_zero is not None, "no zero-error machine was found at all"
_cells, _j, _rhs, _exc = best_zero


def apply_instr(rhs, s):
    return tuple(s[int(r[1:]) - 1] if r.startswith("#") else r for r in rhs)


for s in univ4:
    fired = None
    for pat, e in _exc:
        if matches(pat, s):
            fired = e
            break
    got = apply_instr(fired if fired is not None else _rhs, s)
    assert got == f_hard[s], (
        "the reconstructed zero-error ordered machine is wrong on %s: got %s, "
        "wanted %s" % (s, got, f_hard[s]))
ordered_exact = (1 + _j) * 2 * L4
assert ordered_exact == acc[0], "reconstruction disagrees with the curve"

print("  obligation: leftmost ab -> ba at L=4.")
print("  unordered sound cover : %d instructions = %d cells  (verified minimal)"
      % (k_exact, k_exact * 2 * L4))
print("  ordered default+exceptions: %d instructions = %d cells  (verified on"
      % (1 + _j, ordered_exact))
print("                              all %d inputs)" % len(univ4))
print("  exact parametric      : %d cells" % par_hard)
print()
assert ordered_exact <= k_exact * 2 * L4, (
    "an ordered machine cost MORE than an unordered sound cover, which cannot "
    "happen: every sound cover is also a legal ordered machine")
OUT["ordering_saving_cells"] = k_exact * 2 * L4 - ordered_exact
if ordered_exact < k_exact * 2 * L4:
    print("  Ordering is worth exactly %d cells here: a default may be WRONG on"
          % (k_exact * 2 * L4 - ordered_exact))
    print("  inputs an earlier instruction catches, so it need not be sound on")
    print("  its own selector. That is the difference between a rule set and a")
    print("  production system, and it is measured rather than assumed.")
    print()

print("  %-10s %-14s %-16s %s" % ("errors", "error fraction", "symbolic cells",
                                  "vs exact"))
ex_rows = []
for err in sorted(acc):
    if err > len(univ4) // 2:
        continue
    frac = F(err, len(univ4))
    ex_rows.append({"errors": err, "error_fraction": str(frac),
                    "cells": acc[err]})
    print("  %-10d %-14s %-16d %s"
          % (err, "%s/%s" % (frac.numerator, frac.denominator), acc[err],
             "%+d" % (acc[err] - ordered_exact)))
OUT["exactness_curve"] = {"L": L4, "exact_instructions_unordered": k_exact,
                          "exact_cells_unordered": k_exact * 2 * L4,
                          "exact_cells_ordered": ordered_exact,
                          "exact_parametric_cells": par_hard,
                          "best_single_default_errors": E_MIN,
                          "defaults_enumerated": len(defaults),
                          "distinct_wrong_sets": len(by_wmask),
                          "rows": ex_rows}
assert len(ex_rows) >= 2, (
    "the tolerance curve has fewer than two points below half the domain; "
    "there is nothing to read")
QUARTER = len(univ4) // 4
cheap_tol = min(acc[e] for e in acc if 0 < e <= QUARTER)
assert cheap_tol < acc[0], (
    "tolerating up to a quarter of the domain never bought a cheaper machine, "
    "so exactness is not what is being priced")
small_tol = min(acc[e] for e in acc if 0 < e <= 1)
assert small_tol < acc[0], (
    "the saving only appears at large error fractions, where a `crossover` "
    "would be an artefact of the domain being too small to have a tolerance "
    "regime at all")
OUT["exactness_curve"]["saving_at_one_error"] = acc[0] - small_tol
OUT["exactness_curve"]["saving_at_quarter"] = acc[0] - cheap_tol
print()
print("  Exactness is not free and not ruinous here: giving up ONE input of %d"
      % len(univ4))
print("  (%s of the domain) saves %d of %d cells. The saving is real at a small"
      % (str(F(1, len(univ4))), acc[0] - small_tol, acc[0]))
print("  error fraction, so it is a tolerance regime and not an artefact of")
print("  letting the machine be wrong about half the time.")
print()
print("  > A symbolic machine pays for exactness in exceptions, one instruction")
print("  > at a time, and the price is visible because exceptions are countable.")
print("  > The parametric machine pays for the same exactness in basis degree,")
print("  > where it is not separable from the rest of what it stores.")


# ===========================================================================
# 5  NEUTRAL RECOVERY: NO PRODUCTION-RULE PRIMITIVE
# ===========================================================================
print()
print("=" * 78)
print("5  NEUTRAL RECOVERY: NO PRODUCTION-RULE PRIMITIVE")
print("=" * 78)
print("  Candidates are described only as (selector, emitter) slots, where the")
print("  selector repertoire is every pattern over {a,b,*} and the emitter")
print("  repertoire is every slot-wise choice of a letter or an input slot. The")
print("  space contains constant machines, identity machines, lookup tables and")
print("  everything between. No family is named. The search is the BFS above,")
print("  whose level-by-level exhaustiveness PROVES the returned count minimal.")
print()

NEUTRAL = [
    ("identity", obligation(3, lambda s: s)),
    ("constant aaa", obligation(3, lambda s: ("a", "a", "a"))),
    ("set slot1 to b", obligation(3, lambda s: ("b",) + s[1:])),
    ("reverse", obligation(3, lambda s: tuple(reversed(s)))),
    ("flip every slot", obligation(3, lambda s: tuple(flip(c) for c in s))),
    ("leftmost ab -> ba", obligation(3, leftmost_ab_swap)),
    ("arithmetic scramble", obligation(
        3, lambda s: UNIV3[(5 * sum((1 if c == "b" else 0) << i
                                    for i, c in enumerate(s)) + 3) % 8])),
]

print("  %-22s %-7s %-6s %-6s %-6s %s"
      % ("obligation", "instrs", "wild", "copy", "moved", "reads as"))
rec = []
for name, f in NEUTRAL:
    k, chosen = min_cover(FULL3, candidate_masks(3, UNIV3, f, "substitute"))
    assert k is not None, "no machine found for %s" % name
    # execute the returned machine on every input rather than trusting the mask
    for pat, e in chosen:
        for st in matched_set(pat, UNIV3):
            got = tuple(st[int(r[1:]) - 1] if r.startswith("#") else r
                        for r in e)
            assert got == f[st], (
                "the returned machine is wrong on %s for %s" % (st, name))
    covered = set()
    for pat, _e in chosen:
        covered |= set(matched_set(pat, UNIV3))
    assert covered == set(UNIV3), (
        "the returned machine for %s leaves %d inputs unanswered"
        % (name, len(UNIV3) - len(covered)))
    wild = sum(1 for pat, _e in chosen for pp in pat if pp == "*")
    cps = sum(1 for _p, e in chosen for r in e if r.startswith("#"))
    moved = sum(1 for _p, e in chosen for j, r in enumerate(e)
                if r.startswith("#") and int(r[1:]) - 1 != j)
    if k == len(UNIV3):
        reads = "a lookup table"
    elif k == 1 and cps == 0:
        reads = "a constant"
    elif k == 1 and cps == 3 and moved == 0:
        reads = "a bare copy"
    elif k == 1 and cps == 3 and moved > 0:
        reads = "a slot permutation"
    elif wild > 0 and cps > 0:
        reads = "a production system"
    else:
        reads = "a partial table"
    rec.append({"obligation": name, "instructions": k, "wildcards": wild,
                "copies": cps, "moved_copies": moved,
                "fingerprint": [k, wild, cps, moved], "reads_as": reads})
    print("  %-22s %-7d %-6d %-6d %-6d %s" % (name, k, wild, cps, moved, reads))
OUT["neutral_recovery"] = rec

fps = [tuple(r["fingerprint"]) for r in rec]
assert len(rec) > 0 and len(set(fps)) >= 4, (
    "the winning machines share fewer than four distinct (instructions, "
    "wildcards, copies, moved-copies) fingerprints, so the candidate space is "
    "not discriminating and nothing was recovered")
assert any(r["instructions"] == len(UNIV3) for r in rec), (
    "no obligation drove the search to a full table; the space never reaches "
    "its degenerate end, so the result is not a selection between shapes")
assert any(r["instructions"] == 1 for r in rec), (
    "no obligation was answered by a single instruction")
assert any(1 < r["instructions"] < len(UNIV3) and r["wildcards"] > 0
           and r["copies"] > 0 for r in rec), (
    "no obligation recovered an intermediate shape -- the space produced only "
    "its two extremes, which decides nothing")
# the scramble is defined arithmetically: it was never written as a selector or
# an emitter, so there is no handed answer for the search to echo. Its count is
# whatever the BFS proves, and is reported rather than asserted.
scr = [r for r in rec if r["obligation"] == "arithmetic scramble"][0]
OUT["scramble_instructions"] = scr["instructions"]
ident = [r for r in rec if r["obligation"] == "identity"][0]
rev = [r for r in rec if r["obligation"] == "reverse"][0]
assert ident["fingerprint"] != rev["fingerprint"], (
    "identity and reverse received the same fingerprint, so the measurement "
    "cannot tell a copy from a permutation and the labels are doing the work")
print()
print("  %d distinct (instructions, wildcards, copies, moved-copies) fingerprints"
      % len(set(fps)))
print("  across %d obligations. Those four numbers are measured off the machine"
      % len(rec))
print("  the BFS returned; the `reads as` column is a reading of them and")
print("  carries no assertion. The arithmetic scramble was never written as a")
print("  selector or an emitter -- it is defined by modular arithmetic on the")
print("  string index -- so there is no handed answer for the search to echo,")
print("  and the %d instructions it needs are what the BFS proved minimal."
      % scr["instructions"])
print()
print("  > A production system is what the accounting selects when an")
print("  > obligation's output moves with its input in a way a selector can")
print("  > span. The same space returns a constant, a bare copy, a slot")
print("  > permutation and a full lookup table on obligations where it cannot")
print("  > -- and the family was never in the candidate space to be found.")

print()
print("=" * 78)
print("all assertions held")
print("=" * 78)

with open("microscopes/results/STAGE_SYMBOLIC_REWRITE_V1.json", "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)

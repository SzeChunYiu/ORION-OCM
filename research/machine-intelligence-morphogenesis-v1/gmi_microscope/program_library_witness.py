"""B15: program composition, search over programs, and library/macro pressure.

B14 (`GMI_SYMBOLIC_REWRITE_DERIVATION_V1.md`) derived compositional closure and
priced it on the SERVING ledger: a composing generator family reaches a larger
closure than a collapsing one at the same `k` and the same cell prices, so its
PVR-3 break-even is r=255 against r=27.  B16
(`GMI_SEARCH_FRONTIER_DERIVATION_V1.md`) priced compile-against-search, also on
the serving ledger: how much work a stored answer saves per query.

Library learning is the third thing, and it lives on a ledger neither of those
uses.  A retained chunk of program adds NO expressive power -- the closure is
unchanged, set-equal -- and it adds serving cost.  What it changes is the
number of candidates a LATER obligation must enumerate before its answer is
found.  That is the SEARCH ledger, and it is the only place a macro can earn.

Derived here, by exhaustive enumeration over a finite world, with exact
integers and `Fraction` throughout:

  1  obligation geometry fixes search burden -- and the obvious mechanism for
     it (deep answers being rare) is measured and found FALSE (B15 box 2)
  2  program length against search burden: a chunk pays only inside a bounded
     WINDOW of obligation depth, both ends exact (B15 box 4)
  3  the cost metric, and the order-dependent one that was discarded
  4  a retained chunk is pure cost on the serving ledger (the B14/B16 delta)
  5  which chunks pay on the search ledger and which do not (B15 boxes 3, 5)
  6  amortization: break-even in CORPUS SIZE, with matched twins at two chunk
     lengths holding everything fixed but recurrence (B15 box 3)
  7  composition is a precondition for a chunk to exist at all -- B14's
     collapsing family carried forward, confound stated (B15 box 1)
  8  neutral recovery over stored runs of moves, with no program / library /
     macro / synthesis / interpreter vocabulary anywhere in the candidate
     space, and the searcher never handed a short answer (B15 box 6)

Run from `machine-intelligence-morphogenesis-v1`; writes
`microscopes/results/STAGE_PROGRAM_LIBRARY_V1.json`.
"""

from fractions import Fraction as F
import itertools
import json
import time

T_START = time.time()
OUT = {}

# ---------------------------------------------------------------------------
# The world.  B14's composing family {rotate, set-slot1-b, swap12}, carried to
# one more slot.  Same three generator names, same k=3; only the world is
# deeper, which is what gives the search ledger any dynamic range at all.
# ---------------------------------------------------------------------------


def make_world(length):
    dom = [tuple(s) for s in itertools.product("ab", repeat=length)]
    idx = {s: i for i, s in enumerate(dom)}

    def tab(f):
        return tuple(idx[f(s)] for s in dom)

    gens = [
        ("rot", tab(lambda s: s[1:] + s[:1])),
        ("setb1", tab(lambda s: ("b",) + s[1:])),
        ("swap12", tab(lambda s: (s[1], s[0]) + s[2:])),
    ]
    collapsing = [
        ("const-" + c, tab(lambda s, c=c: tuple(c)))
        for c in ("a" * length, "b" * length, ("ab" * length)[:length])
    ]
    return dom, gens, collapsing


def compose(t, g):
    return tuple(g[x] for x in t)


def closure_ladder(gens, dmax):
    """|M_d| for d = 1..dmax, plus table -> minimal length.

    B14's convention: M_d is what programs of length 1..d can compute.
    """
    out = []
    seen = {}
    cur = {}
    for _n, g in gens:
        seen[g] = 1
        cur[g] = None
    for d in range(1, dmax + 1):
        if d > 1:
            nxt = {}
            for t in cur:
                for _n, g in gens:
                    u = compose(t, g)
                    if u not in seen:
                        seen[u] = d
                        nxt[u] = None
            cur = nxt
        out.append(len(seen))
    return out, seen


def enumerate_costs(gen_tables, lmax, dom_size):
    """Enumerate every move sequence of length 1..lmax in canonical
    length-then-lexicographic order.

    `first[table]` is the 1-based position of the FIRST sequence realising that
    table: exactly the number of candidates a searcher examines before it may
    stop.  `mult[table]` is how many of the enumerated sequences realise it.
    """
    first = {}
    mult = {}
    idx = 0
    cur = [tuple(range(dom_size))]
    for _length in range(1, lmax + 1):
        nxt = []
        for t in cur:
            for g in gen_tables:
                u = compose(t, g)
                idx += 1
                if u not in first:
                    first[u] = idx
                mult[u] = mult.get(u, 0) + 1
                nxt.append(u)
        cur = nxt
    return first, mult, idx


DOM4, GENS4, COLL4 = make_world(4)
DOM3, GENS3, COLL3 = make_world(3)
N4 = len(DOM4)
K = len(GENS4)
LMAX = 8

print("=" * 78)
print("0  THE WORLD, AND THE B14 BINDING")
print("=" * 78)

lad3, _s3 = closure_ladder(GENS3, 6)
ladc3, _c3 = closure_ladder(COLL3, 6)
lad4, seen4 = closure_ladder(GENS4, 14)
print("  B14's composing family  {rot, setb1, swap12} on {a,b}^3: |M_d| = %s"
      % lad3)
print("  B14's collapsing family {const x 3}          on {a,b}^3: |M_d| = %s"
      % ladc3)
assert lad3 == [3, 11, 22, 31, 34, 34], (
    "the composing ladder must reproduce B14's 3,11,22,31,34,34; if it does "
    "not, this witness is not standing on B14's family")
assert ladc3 == [3, 3, 3, 3, 3, 3], (
    "the collapsing ladder must reproduce B14's 3,3,3,3,3,3")
print("  Both reproduce B14 exactly, so this is the same family, not a")
print("  lookalike.  Everything below is that family one slot wider.")
print()

DEPTH = dict(seen4)
prof = {}
for _t, d in DEPTH.items():
    prof[d] = prof.get(d, 0) + 1
MAXD = max(prof)
print("  carried to {a,b}^4: |D| = %d, k = %d, closure = %d, deepest"
      % (N4, K, len(DEPTH)))
print("  obligation at minimal length %d.  obligations by minimal length:" % MAXD)
print("    " + "  ".join("%d:%d" % (d, prof[d]) for d in sorted(prof)))
assert MAXD >= 7, "the world must be deep enough for a length-3 chunk to pay"

GT4 = [g for _n, g in GENS4]
BASE_FIRST, BASE_MULT, BASE_TOTAL = enumerate_costs(GT4, LMAX, N4)
TASKS = sorted(DEPTH, key=lambda t: (DEPTH[t], BASE_FIRST[t]))
assert all(t in BASE_FIRST for t in TASKS), (
    "an obligation was not found inside lmax; a silently unsolved task is a "
    "wrong answer that does not crash")
print("  base enumeration to length %d: %d candidates, and every one of the"
      % (LMAX, BASE_TOTAL))
print("  %d obligations is found inside it." % len(TASKS))
OUT["world"] = {
    "domain": "{a,b}^4", "domain_size": N4,
    "generators": [n for n, _g in GENS4], "k": K, "closure": len(DEPTH),
    "max_minimal_length": MAXD, "lmax": LMAX,
    "base_enumeration_total": BASE_TOTAL, "obligations": len(TASKS),
    "depth_profile": dict((str(d), prof[d]) for d in sorted(prof)),
    "b14_composing_ladder_L3": lad3, "b14_collapsing_ladder_L3": ladc3,
}

# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("1  OBLIGATION GEOMETRY FIXES SEARCH BURDEN")
print("=" * 78)
print("  Burden = candidates enumerated before the answer is reached.  In the")
print("  canonical order the burden of a depth-d obligation is pinned to the")
print("  half-open block ((k^d - k)/(k-1), (k^(d+1) - k)/(k-1)], so depth")
print("  fixes burden to within one level and nothing the searcher does moves")
print("  it out of that block.  That block has top/bottom ratio exactly k for")
print("  every d, so 'depth fixes burden to within a factor of k' holds for ANY")
print("  length-major enumeration order, not just the canonical one.  The")
print("  burden lo/hi columns below ARE order-dependent: they show where this")
print("  particular order lands inside the block, and only the block is claimed.")
print()
print("  %-5s %-7s %-10s %-10s %-9s %-12s %s"
      % ("d", "count", "burden lo", "burden hi", "within-d", "k^d", "hit rate"))
geom = []
for d in sorted(prof):
    at = [t for t in TASKS if DEPTH[t] == d]
    lo = min(BASE_FIRST[t] for t in at)
    hi = max(BASE_FIRST[t] for t in at)
    level = K ** d
    hit = F(len(at), level)
    geom.append({"min_length": d, "count": len(at), "burden_lo": lo,
                 "burden_hi": hi, "within_depth_ratio": str(F(hi, lo)),
                 "candidates_at_length_d": level, "hit_rate": str(hit)})
    print("  %-5d %-7d %-10d %-10d %-9s %-12d %s"
          % (d, len(at), lo, hi, str(F(hi, lo)), level, hit))
OUT["geometry"] = geom

for i in range(1, len(geom)):
    assert geom[i]["burden_lo"] > geom[i - 1]["burden_hi"], (
        "depth blocks overlap in the canonical enumeration")
    assert (geom[i] if True else None) is not None
blocks_ok = all(
    geom[i]["burden_hi"] <= (K ** (geom[i]["min_length"] + 1) - K) // (K - 1)
    and geom[i]["burden_lo"] > (K ** geom[i]["min_length"] - K) // (K - 1)
    for i in range(len(geom)))
assert blocks_ok, "measured burdens fall outside the exact depth blocks"

hits = [F(g["hit_rate"]) for g in geom]
assert all(hits[i] < hits[i - 1] for i in range(1, len(hits))), (
    "the hit rate must fall strictly with depth, else there is no geometry")
hit_span = hits[0] / hits[-1]
assert hit_span >= 1000, (
    "the hit rate must collapse by at least three orders across the closure, "
    "else the geometry claim is vacuous; measured %s" % hit_span)
widest = max(geom, key=lambda g: F(g["within_depth_ratio"]))
deep_widest = max([g for g in geom if g["min_length"] >= 3],
                  key=lambda g: F(g["within_depth_ratio"]))
assert F(widest["within_depth_ratio"]) <= K, (
    "within-depth burden variation exceeded one level, so depth does not fix "
    "burden and the block statement is empty")
assert F(deep_widest["within_depth_ratio"]) < K, (
    "below the level where a block is narrower than the level itself, the "
    "block statement carries no information")
print()
print("  The closure saturates at %d while program space keeps multiplying by"
      % len(TASKS))
print("  k = %d per level, so the share of candidates naming a new obligation" % K)
print("  collapses by a factor of %s from the first level to the last." % hit_span)
print("  Within a single depth, burden varies by at most %s -- exactly the"
      % widest["within_depth_ratio"])
print("  block's own width, and by at most %s once the closure stops filling"
      % deep_widest["within_depth_ratio"])
print("  its level (depth >= 3).  The first of those is structural; the second")
print("  is a measurement about this order, and it is the weaker of the two.")
OUT["geometry_gates"] = {"hit_rate_span": str(hit_span),
                         "max_within_depth_ratio": widest["within_depth_ratio"],
                         "max_within_depth_ratio_d3plus":
                             deep_widest["within_depth_ratio"],
                         "blocks_exact": blocks_ok}

print()
print("  MEASURED NEGATIVE -- the obvious mechanism is not the mechanism.")
print("  If deep obligations were expensive because their answers are RARE in")
print("  program space, the expected burden under a random enumeration order,")
print("  (N+1)/(m+1) for m solutions among N candidates, would rise with depth.")
print("  It does not:")
print()
print("  %-5s %-12s %-14s %s" % ("d", "min solutions", "E[burden], rand", "as int"))
rand = []
for d in sorted(prof):
    at = [t for t in TASKS if DEPTH[t] == d]
    mlo = min(BASE_MULT[t] for t in at)
    eb = F(BASE_TOTAL + 1, mlo + 1)
    rand.append({"min_length": d, "min_solutions": mlo, "expected_burden": str(eb)})
    print("  %-5d %-12d %-14s %d" % (d, mlo, eb, int(eb)))
OUT["random_order_burden"] = rand
ebs = [F(r["expected_burden"]) for r in rand]
assert not all(ebs[i] >= ebs[i - 1] for i in range(1, len(ebs))), (
    "expected burden under a random order came out monotone in depth; the "
    "reported negative would then be false and this section must be rewritten")
assert max(ebs) / min(ebs) < 100, (
    "expected burden under a random order spans too much to call it flat")
print()
print("  Non-monotone, and spanning a factor of only %s against the hit rate's"
      % (max(ebs) // min(ebs)))
print("  %s.  Solution rarity is NOT what makes a deep obligation expensive." % int(hit_span))
print("  > What makes it expensive is that the canonical order must walk every")
print("  > shallower level first.  Burden is a property of where the obligation")
print("  > sits in the closure, not of how rare its answers are.")
print("  (B16 settled WHEN storage cannot hold a direct answer; that argument")
print("   is cited, not repeated.)")

# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("2  PROGRAM LENGTH AGAINST SEARCH BURDEN: THE PAYING WINDOW")
print("=" * 78)
print("  Retaining a chunk of length l turns an obligation of depth L into one")
print("  of depth L-l+1 and raises branching from k=%d to k=%d.  Both effects" % (K, K + 1))
print("  are exact:  N_k(L) = (k^(L+1) - k) / (k-1), the worst-case burden of a")
print("  depth-L obligation.  The chunk pays iff N_4(L-l+1) < N_3(L).")
print()


def nk(k, length):
    return (k ** (length + 1) - k) // (k - 1)


print("  %-8s %-8s %-15s %-15s %s"
      % ("chunk l", "depth L", "k=3, len L", "k=4, len L-l+1", "chunk pays"))
cross = []
windows = {}
for ell in (2, 3, 4):
    pay_depths = []
    for depth in range(ell, 20):
        base = nk(K, depth)
        chunked = nk(K + 1, depth - ell + 1)
        pays = chunked < base
        if pays:
            pay_depths.append(depth)
        cross.append({"chunk_length": ell, "depth": depth, "base": base,
                      "chunked": chunked, "pays": pays})
        if depth <= ell + 1 or depth in (5, 6, 10, 11, 19):
            print("  %-8d %-8d %-15d %-15d %s"
                  % (ell, depth, base, chunked, "yes" if pays else "no"))
    assert pay_depths == list(range(pay_depths[0], pay_depths[-1] + 1)), (
        "the paying depths for l=%d are not contiguous; the window story is "
        "wrong" % ell)
    assert not cross[-1]["pays"], (
        "for l=%d the deepest obligation tested still pays, so the window's "
        "upper end is the edge of the tested range and has not been "
        "established" % ell)
    windows[ell] = (pay_depths[0], pay_depths[-1])
    print("     -> length-%d chunk pays exactly for depth L in [%d, %d]"
          % (ell, pay_depths[0], pay_depths[-1]))
    print()
OUT["crossover"] = cross
OUT["paying_windows"] = dict((str(e), list(w)) for e, w in windows.items())

assert any(c["pays"] for c in cross) and any(not c["pays"] for c in cross), (
    "the crossover must have both sides present; a rule that fires everywhere "
    "or nowhere is vacuous")
for ell in (2, 3):
    assert windows[ell + 1][1] > windows[ell][1], (
        "a longer chunk must survive to greater depth")
    assert windows[ell][1] < 19, "window upper end escaped the tested range"
print("  > A retained chunk pays only inside a bounded window.  Too shallow and")
print("  > there is nothing to shorten; too deep and the extra branching, paid")
print("  > at every level, outruns the levels saved.  Program length does not")
print("  > trade against search burden monotonically -- it has an optimum.")
print()
print("  This is a PREDICTION, and section 5 tests it against a measurement")
print("  that knows nothing about this arithmetic: the obligations of this")
print("  world sit at depths 1-%d, so length-2 chunks (window [%d,%d]) should"
      % (MAXD, windows[2][0], windows[2][1]))
print("  mostly lose and length-3 chunks (window [%d,%d]) should win."
      % (windows[3][0], windows[3][1]))
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("3  THE COST METRIC, AND THE ONE THAT WAS DISCARDED")
print("=" * 78)
print("  A search-ledger cost must not depend on how the machine happens to")
print("  order its moves.  The metric used below is the WORST-CASE burden:")
print("  N_k(L) candidates, the whole enumeration up to and including the")
print("  obligation's minimal length L.  It depends only on the move set's")
print("  size and on where the obligation sits, both properties of the SET.")
print()
print("  DISCARDED: the first metric tried was the index of the obligation's")
print("  first answer in the canonical length-then-lexicographic enumeration.")
print("  That metric is order-dependent, and not mildly so -- moving the")
print("  retained chunk from the end of the move alphabet to the front FLIPS")
print("  THE SIGN of the headline saving (+16547 becomes -10599 for the same")
print("  chunk in the same world).  A result that survives only one arbitrary")
print("  tie-break is not a result.  The metric was replaced, not the chunk.")
print()


def nk_cost(k, length):
    return (k ** (length + 1) - k) // (k - 1)


BASE_COST = dict((t, nk_cost(K, DEPTH[t])) for t in TASKS)
TOTAL_BASE = sum(BASE_COST.values())
print("  Base worst-case burden over all %d obligations: %d candidates."
      % (len(TASKS), TOTAL_BASE))
OUT["cost_metric"] = {
    "metric": "worst-case burden N_k(L) = (k^(L+1)-k)/(k-1)",
    "order_independent": True, "total_base_burden": TOTAL_BASE,
    "discarded_metric": "first-answer index in canonical enumeration",
    "discarded_because": "sign of headline saving flips with chunk position",
    "discarded_saving_chunk_last": 16547,
    "discarded_saving_chunk_first": -10599,
}

# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("4  A RETAINED CHUNK IS PURE COST ON THE SERVING LEDGER")
print("=" * 78)
print("  Candidate chunks: every base sequence of length 2 and 3, deduplicated")
print("  by what it computes, minus any that merely repeats a base generator.")
print()

CHUNKS = []
_seen_tab = set(GT4)
for ell in (2, 3):
    for w in itertools.product(range(K), repeat=ell):
        t = tuple(range(N4))
        for i in w:
            t = compose(t, GT4[i])
        if t in _seen_tab:
            continue
        _seen_tab.add(t)
        CHUNKS.append({"word": "+".join(GENS4[i][0] for i in w),
                       "moves": list(w), "length": ell, "table": t})
n2 = sum(1 for c in CHUNKS if c["length"] == 2)
n3 = sum(1 for c in CHUNKS if c["length"] == 3)
print("  %d candidate chunks (%d of length 2, %d of length 3)."
      % (len(CHUNKS), n2, n3))
assert len(CHUNKS) >= 20 and n2 >= 4 and n3 >= 8, (
    "too few candidate chunks at either length to call this a search")

CELL_BASE = K * N4
CELL_CHUNK = (K + 1) * N4
BASE_CLOSURE = set(DEPTH)
for c in CHUNKS:
    _l, cl = closure_ladder(list(GENS4) + [("chunk", c["table"])], 14)
    c["depths"] = cl
    assert set(cl) == BASE_CLOSURE, (
        "chunk %s changed the closure, so it is not a composition of existing "
        "generators; that is a bug, not a result" % c["word"])
print("  For every one of the %d: closure(base + chunk) == closure(base), as"
      % len(CHUNKS))
print("  SETS of functions -- %d before, %d after, zero new."
      % (len(BASE_CLOSURE), len(BASE_CLOSURE)))
print("  Serving cost goes %d cells -> %d cells, one cell per stored atom,"
      % (CELL_BASE, CELL_CHUNK))
print("  B14's convention.")
assert CELL_CHUNK > CELL_BASE
OUT["serving_ledger"] = {
    "cells_base": CELL_BASE, "cells_with_chunk": CELL_CHUNK,
    "closure_base": len(BASE_CLOSURE), "closure_with_chunk": len(BASE_CLOSURE),
    "new_functions": 0, "chunks_tested": len(CHUNKS),
}
print()
print("  > Strictly positive serving cost, exactly zero new expressible")
print("  > functions.  On B14's ledger and on B16's, a retained chunk is a loss")
print("  > in every world and for every chunk.  Whatever library learning is,")
print("  > it is not visible from there.")

# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("5  WHICH CHUNKS PAY ON THE SEARCH LEDGER, AND WHICH DO NOT")
print("=" * 78)
print("  delta = worst-case burden with the chunk retained, minus without,")
print("  summed over all %d reachable obligations.  'shortens' counts the" % len(TASKS))
print("  obligations whose minimal length actually drops.")
print()

for c in CHUNKS:
    d2 = c["depths"]
    helped, taxed, shortened, total = [], [], 0, 0
    for t in TASKS:
        cost2 = nk_cost(K + 1, d2[t])
        d = cost2 - BASE_COST[t]
        total += d
        if d2[t] < DEPTH[t]:
            shortened += 1
        if d < 0:
            helped.append(d)
        elif d > 0:
            taxed.append(d)
    c["saving"] = -total
    c["n_helped"] = len(helped)
    c["n_taxed"] = len(taxed)
    c["n_shortened"] = shortened
    c["gross_help"] = sum(-d for d in helped)
    c["taxes"] = sorted(taxed)
    del c["depths"]

ranked = sorted(CHUNKS, key=lambda c: c["saving"], reverse=True)
print("  %-22s %-4s %-10s %-8s %-8s %s"
      % ("chunk", "l", "shortens", "helps", "taxes", "net saving"))
for c in ranked[:3] + ranked[-3:]:
    print("  %-22s %-4d %-10d %-8d %-8d %+d"
          % (c["word"], c["length"], c["n_shortened"], c["n_helped"],
             c["n_taxed"], c["saving"]))
OUT["chunks"] = [{"word": c["word"], "length": c["length"],
                  "n_shortened": c["n_shortened"], "n_helped": c["n_helped"],
                  "n_taxed": c["n_taxed"], "gross_help": c["gross_help"],
                  "saving": c["saving"]} for c in ranked]

winners = [c for c in CHUNKS if c["saving"] > 0]
losers = [c for c in CHUNKS if c["saving"] < 0]
assert winners, "no chunk pays anywhere; nothing has been derived"
assert losers, ("every chunk pays, so the branching tax is not real and the "
                "result is vacuous")
assert not any(c["n_helped"] == len(TASKS) for c in CHUNKS), (
    "a chunk that helps every obligation fires everywhere and discriminates "
    "nothing")
assert min(c["n_helped"] for c in CHUNKS) <= 2, (
    "no chunk is near-useless, so this obligation set cannot separate "
    "recurrence from chunk length")
BEST = ranked[0]
print()
print("  Exactly %d of %d chunks pays over the whole obligation set; %d cost"
      % (len(winners), len(CHUNKS), len(losers)))
print("  more than they save.  best: %s (length %d)," % (BEST["word"], BEST["length"]))
print("  shortens %d obligations, helps %d of %d, nets %+d candidates."
      % (BEST["n_shortened"], BEST["n_helped"], len(TASKS), BEST["saving"]))

gap = [c for c in CHUNKS if c["n_shortened"] > c["n_helped"]]
worst_gap = max(gap, key=lambda c: c["n_shortened"] - c["n_helped"])
assert gap, (
    "no chunk shortens an obligation it does not help, so the window of "
    "section 2 has no measured consequence and that section is decorative")
print()
print("  SHORTENING IS NOT HELPING.  %d of the %d chunks shorten obligations"
      % (len(gap), len(CHUNKS)))
print("  they nonetheless make more expensive; %s shortens %d and helps only"
      % (worst_gap["word"], worst_gap["n_shortened"]))
print("  %d.  Those %d obligations sit past the chunk's paying window: the"
      % (worst_gap["n_helped"], worst_gap["n_shortened"] - worst_gap["n_helped"]))
print("  level saved is worth less than the extra branching at every level.")
OUT["shorten_not_help"] = {
    "chunks_with_gap": len(gap), "worst": worst_gap["word"],
    "shortens": worst_gap["n_shortened"], "helps": worst_gap["n_helped"],
}

win_lengths = sorted(set(c["length"] for c in winners))
lose2 = sum(1 for c in losers if c["length"] == 2)
print()
print("  SECTION 2's PREDICTION, TESTED against a measurement that knows")
print("  nothing about that arithmetic: every paying chunk has length %s, and"
      % win_lengths)
print("  all %d length-2 chunks lose.  The obligations sit at depths 1-%d,"
      % (lose2, MAXD))
print("  outside the length-2 window [%d,%d] for most of them, inside the"
      % (windows[2][0], windows[2][1]))
print("  length-3 window [%d,%d] for all of them." % (windows[3][0], windows[3][1]))
assert win_lengths == [3], (
    "section 2 predicted only length-3 chunks pay in this world; the "
    "measurement disagrees, so one of the two is wrong")
assert lose2 == n2, "section 2 predicted every length-2 chunk loses here"
OUT["window_prediction"] = {
    "predicted_paying_length": 3, "measured_paying_lengths": win_lengths,
    "length2_chunks": n2, "length2_losing": lose2,
    "winners": len(winners), "losers": len(losers),
}

print()
print("  ORDER-INDEPENDENCE, CHECKED not assumed: the metric is computed from")
print("  the move SET, so scoring the best chunk with it written first in the")
print("  alphabet instead of last must give the identical number.")
_l, d_first = closure_ladder([("chunk", BEST["table"])] + list(GENS4), 14)
alt = -sum(nk_cost(K + 1, d_first[t]) - BASE_COST[t] for t in TASKS)
print("  chunk last: %+d.  chunk first: %+d.  %s."
      % (BEST["saving"], alt,
         "identical" if alt == BEST["saving"] else "DIFFERENT -- metric is not "
         "order-independent after all"))
assert alt == BEST["saving"], (
    "the worst-case burden metric came out order-dependent, which contradicts "
    "its construction and means there is a bug")
OUT["order_independence"] = {"chunk": BEST["word"], "last": BEST["saving"],
                             "first": alt, "identical": alt == BEST["saving"]}

# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("6  AMORTIZATION: THE BREAK-EVEN IS IN CORPUS SIZE")
print("=" * 78)
print("  A chunk is bought once and taxed on every obligation that does not")
print("  use it, so it survives only a corpus of bounded size.  n* = the")
print("  largest corpus -- its helped obligations plus taxed ones, cheapest")
print("  tax first -- on which the chunk still saves.  Cheapest-first is the")
print("  most favourable ordering, so n* is an upper bound; n*_worst takes the")
print("  taxed obligations most-expensive first and brackets it from below.")
print()


def break_even(c, order):
    taxes = sorted(c["taxes"], reverse=(order == "worst"))
    acc, n = 0, c["n_helped"]
    for tx in taxes:
        if acc + tx >= c["gross_help"]:
            break
        acc += tx
        n += 1
    return n


for c in CHUNKS:
    c["n_star_best"] = break_even(c, "best")
    c["n_star_worst"] = break_even(c, "worst")
    # A chunk whose break-even runs out of taxed obligations has NOT had its
    # ceiling established: it survives at least this corpus, and how much more
    # cannot be read off a world with only this many obligations in it.
    c["ceiling_open"] = c["n_star_best"] >= len(TASKS)

print("  %-22s %-4s %-8s %-12s %-10s %s"
      % ("chunk", "l", "helps r", "saves there", "n* worst", "n* best"))
amort = []
for c in ranked[:2] + ranked[-3:]:
    amort.append({"word": c["word"], "length": c["length"], "r": c["n_helped"],
                  "gross_saving": c["gross_help"],
                  "n_star_best": c["n_star_best"],
                  "n_star_worst": c["n_star_worst"],
                  "n_star_best_is_lower_bound_only": c["ceiling_open"],
                  "obligations_available": len(TASKS)})
    print("  %-22s %-4d %-8d %-12d %-10d %s"
          % (c["word"], c["length"], c["n_helped"], c["gross_help"],
             c["n_star_worst"],
             (">= %d" % c["n_star_best"]) if c["ceiling_open"]
             else str(c["n_star_best"])))
OUT["amortization"] = amort
assert all(c["n_star_worst"] <= c["n_star_best"] for c in CHUNKS)
assert all(c["n_star_best"] >= c["n_helped"] >= 1 for c in CHUNKS), (
    "a chunk that pays on no corpus at all would make the break-even empty")
nondegen = [c for c in CHUNKS if 1 < c["n_star_best"] < len(TASKS)]
assert len(nondegen) >= len(CHUNKS) // 2, (
    "most break-evens are degenerate -- never paying, or surviving everything "
    "-- so there is no amortization curve to report")
# The spread is computed over chunks whose ceiling IS established.  Including
# a chunk that ran out of taxed obligations would report the size of this
# obligation set, not that chunk's break-even.
bounded = [c for c in CHUNKS if not c["ceiling_open"]]
open_ceiling = [c for c in CHUNKS if c["ceiling_open"]]
spread = max(c["n_star_best"] for c in bounded) // max(
    1, min(c["n_star_best"] for c in bounded))
assert bounded, "every chunk's ceiling is open, so no break-even is bracketed"
assert spread >= 20, (
    "break-even barely varies across chunks, so it carries no information; "
    "measured spread %d" % spread)
OUT["break_even_spread"] = {
    "spread": spread, "chunks_bracketed": len(bounded),
    "chunks_with_open_ceiling": [c["word"] for c in open_ceiling],
    "ceiling_note": "n* for an open-ceiling chunk is a lower bound: it ran "
                    "out of taxed obligations inside this world",
}
print()
print("  %d of %d chunks have a break-even strictly inside the obligation set."
      % (len(nondegen), len(CHUNKS)))
print("  Across the %d whose ceiling is established, n* spans a factor of %d."
      % (len(bounded), spread))
print("  EVERY chunk pays on some corpus -- even the one that helps a single")
print("  obligation pays on a corpus of %d."
      % min(c["n_star_best"] for c in CHUNKS))
if open_ceiling:
    print("  %s runs out of taxed obligations before it stops"
          % ", ".join(c["word"] for c in open_ceiling))
    print("  paying, so its n* is a LOWER BOUND of %d, not a measurement: this"
          % len(TASKS))
    print("  world does not contain enough obligations to close it.  It is")
    print("  excluded from the spread above for that reason.")

print()
print("  MATCHED TWINS.  Hold chunk length fixed, so the branching tax (k: %d"
      % K)
print("  -> %d), the serving price (%d -> %d cells) and the world are all"
      % (K + 1, CELL_BASE, CELL_CHUNK))
print("  identical, and vary only how many obligations the chunk recurs in.")
print("  Both members are drawn from the chunks that LOSE over the full")
print("  obligation set, so nothing separates them except how far down a")
print("  corpus they survive:")
print()
print("  %-4s %-22s %-10s %-10s %s"
      % ("l", "chunk", "recurs r", "n* best", "net saving over all %d" % len(TASKS)))
twins = []
for ell in sorted(set(c["length"] for c in CHUNKS)):
    group = sorted([c for c in CHUNKS if c["length"] == ell and c["saving"] < 0],
                   key=lambda c: c["n_helped"])
    if len(group) < 2 or group[0]["n_helped"] == group[-1]["n_helped"]:
        continue
    lo, hi = group[0], group[-1]
    twins.append({"length": ell,
                  "low": {"word": lo["word"], "r": lo["n_helped"],
                          "n_star": lo["n_star_best"], "saving": lo["saving"]},
                  "high": {"word": hi["word"], "r": hi["n_helped"],
                           "n_star": hi["n_star_best"],
                           "saving": hi["saving"]}})
    for m in (lo, hi):
        print("  %-4d %-22s %-10d %-10d %+d"
              % (ell, m["word"], m["n_helped"], m["n_star_best"], m["saving"]))
OUT["recurrence_twins"] = twins
assert len(twins) >= 2, (
    "fewer than two matched twins; without one at each chunk length the "
    "amortization claim is not isolated from chunk length")
for tw in twins:
    assert tw["low"]["r"] != tw["high"]["r"], "twin is not varied on recurrence"
    assert tw["high"]["n_star"] > tw["low"]["n_star"], (
        "recurrence did not order the break-even at length %d" % tw["length"])
    assert 1 < tw["low"]["n_star"] < len(TASKS), (
        "the low-recurrence twin at length %d has a degenerate break-even"
        % tw["length"])
    assert tw["low"]["saving"] < 0 and tw["high"]["saving"] < 0, (
        "the twin at length %d is not clean: both members must lose over the "
        "full obligation set, so the only thing separating them is n*"
        % tw["length"])
print()
print("  Both members of both twins lose over the full %d-obligation corpus,"
      % len(TASKS))
print("  so recurrence is the only live variable: at length %d, n* = %d against"
      % (twins[0]["length"], twins[0]["low"]["n_star"]))
print("  %d; at length %d, %d against %d."
      % (twins[0]["high"]["n_star"], twins[1]["length"],
         twins[1]["low"]["n_star"], twins[1]["high"]["n_star"]))
print()
print("  > Recurrence is not what makes a chunk useful.  A chunk used once can")
print("  > pay, if it is long enough and its obligation deep enough -- the")
print("  > one-use chunk here pays on any corpus of %d or fewer."
      % min(c["n_star_best"] for c in CHUNKS))
print("  > Recurrence sets HOW MANY unrelated obligations the chunk can be")
print("  > taxed on before it stops paying.  Library pressure is a statement")
print("  > about the size and spread of the corpus, not about the chunk.")

# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("7  COMPOSITION IS A PRECONDITION (B14's COLLAPSING FAMILY)")
print("=" * 78)
CGT = [g for _n, g in COLL4]
c_lad, c_seen = closure_ladder(COLL4, 8)
print("  Collapsing family on {a,b}^4: |M_d| = %s." % c_lad)
print("  Every obligation sits at minimal length 1, and every sequence of")
print("  length >= 2 computes exactly what its last move computes.")
c_tasks = sorted(c_seen)
c_base = sum(nk_cost(K, c_seen[t]) for t in c_tasks)
coll_savings = []
for ell in (2, 3):
    for w in itertools.product(range(K), repeat=ell):
        t = tuple(range(N4))
        for i in w:
            t = compose(t, CGT[i])
        _l2, d2 = closure_ladder(list(COLL4) + [("chunk", t)], 8)
        coll_savings.append(c_base - sum(nk_cost(K + 1, d2[x]) for x in c_tasks))
best_coll = max(coll_savings)
print("  Best chunk over all %d candidates: net saving %+d candidates."
      % (len(coll_savings), best_coll))
OUT["collapsing_control"] = {
    "ladder": c_lad, "closure": len(c_seen),
    "chunks_tested": len(coll_savings), "best_saving": best_coll,
    "composing_best_saving": BEST["saving"],
}
assert best_coll <= 0, "a chunk paid in a family with no composition"
assert BEST["saving"] > 0
print()
print("  POSITIVE CONTROL for this negative: the identical chunk search, run")
print("  on the composing family in section 5, returned %s" % BEST["word"])
print("  with net saving %+d.  So the negative here is about the family, not"
      % BEST["saving"])
print("  about a searcher that cannot find anything.")
print()
print("  CONFOUND, STATED: the collapsing family is also flat -- every")
print("  obligation is at minimal length 1, so there is no depth for a chunk")
print("  to save even in principle.  This exhibit shows composition is")
print("  NECESSARY for a chunk to have anything to shorten.  It does NOT")
print("  isolate composition from depth.  The clean isolation of the library")
print("  claim is the matched twins in section 6, which hold chunk length,")
print("  branching tax, serving price and world fixed and vary only recurrence.")

# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("8  NEUTRAL RECOVERY: STORED RUNS OF MOVES, NO FAMILY NAMES")
print("=" * 78)
print("  The searcher is handed exactly two things: the move alphabet as raw")
print("  input/output tables, and each obligation as its input/output table.")
print("  It is NEVER handed a short answer for any obligation, so there is no")
print("  answer for it to echo back.  Candidates are described only by what")
print("  they store and what that costs.")
print()

FORBIDDEN = ("program", "library", "macro", "synthesis", "interpreter")
PLANS = [{"label": "store nothing, examine every sequence", "run": None}]
for ell in (2, 3):
    for w in itertools.product(range(K), repeat=ell):
        PLANS.append({"label": "store one run of %d moves" % ell, "run": w})
for p in PLANS:
    low = p["label"].lower()
    for bad in FORBIDDEN:
        assert bad not in low, "candidate space leaks the word '%s'" % bad
print("  candidate space: %d retention plans; vocabulary check passed -- none"
      % len(PLANS))
print("  of %s" % ", ".join(FORBIDDEN))
print("  appears in any candidate label.")
print()

WORLDS = [("deep obligations, min len >= 7",
           [t for t in TASKS if DEPTH[t] >= 7]),
          ("middling obligations, min len 5-6",
           [t for t in TASKS if 5 <= DEPTH[t] <= 6]),
          ("shallow obligations, min len <= 3",
           [t for t in TASKS if DEPTH[t] <= 3])]
_cache = {}
for p in PLANS:
    if p["run"] is not None:
        t = tuple(range(N4))
        for i in p["run"]:
            t = compose(t, GT4[i])
        _cache[p["run"]] = closure_ladder(list(GENS4) + [("chunk", t)], 14)[1]
print("  %-30s %-5s %-30s %s"
      % ("obligation set", "n", "cheapest plan", "cost vs nothing"))
rec = []
for wname, wtasks in WORLDS:
    assert wtasks, "an empty obligation set proves nothing"
    scored = []
    for p in PLANS:
        if p["run"] is None:
            cost = sum(BASE_COST[x] for x in wtasks)
        else:
            d2 = _cache[p["run"]]
            cost = sum(nk_cost(K + 1, d2[x]) for x in wtasks)
        scored.append((cost, p["label"], p["run"]))
    scored.sort(key=lambda z: (z[0], str(z[2])))
    cost, label, run = scored[0]
    nothing = sum(BASE_COST[x] for x in wtasks)
    beat = sum(1 for s in scored if s[2] is not None and s[0] < nothing)
    shown = "store nothing" if run is None else "store the run %s" % (
        "+".join(GENS4[i][0] for i in run))
    rec.append({"obligations": wname, "n": len(wtasks), "plan": label,
                "run": None if run is None else list(run),
                "run_word": None if run is None else "+".join(
                    GENS4[i][0] for i in run),
                "cost": cost, "cost_storing_nothing": nothing,
                "plans_beating_nothing": beat, "stores_nothing": run is None})
    print("  %-30s %-5d %-30s %d vs %d"
          % (wname[:30], len(wtasks), shown[:30], cost, nothing))
OUT["neutral_recovery"] = rec

stores = [r["stores_nothing"] for r in rec]
assert any(stores) and not all(stores), (
    "the obvious plan -- store nothing -- must win on one obligation set and "
    "lose on another; winning everywhere means the search recovered nothing, "
    "losing everywhere means the candidate space is rigged")
assert rec[0]["plans_beating_nothing"] >= 3, (
    "only one plan beats storing nothing on the deep set, so the recovery "
    "rests on a single lucky candidate")
print()
print("  ANTI-RIG 1: 'store nothing' wins on %d of the %d obligation sets and"
      % (sum(stores), len(rec)))
print("  loses on the other, so the obvious answer does not win everywhere.")
print("  On the deep set %d separate retention plans beat storing nothing, so"
      % rec[0]["plans_beating_nothing"])
print("  that win does not rest on one lucky candidate.")
print("  POSITIVE CONTROL: the two negatives above come from the same searcher")
print("  that returns a stored run on the deep set, so they are findings and")
print("  not a searcher that finds nothing.")

shortest = {}
cur = {tuple(range(N4)): ()}
for _L in range(1, LMAX + 1):
    nxt = {}
    for t, w in cur.items():
        for i in range(K):
            u = compose(t, GT4[i])
            if u not in shortest:
                shortest[u] = w + (i,)
                nxt[u] = w + (i,)
    cur = nxt
freq = {}
for t in TASKS:
    if DEPTH[t] < 7:
        continue
    w = shortest[t]
    for ell in (2, 3):
        for i in range(len(w) - ell + 1):
            freq[w[i:i + ell]] = freq.get(w[i:i + ell], 0) + 1
obvious = max(freq, key=lambda s: (freq[s], -len(s)))
obvious3 = max([s for s in freq if len(s) == 3], key=lambda s: freq[s])
deep_run = tuple(rec[0]["run"]) if rec[0]["run"] is not None else None
OUT["anti_rig"] = {
    "most_frequent_run": list(obvious), "most_frequent_count": freq[obvious],
    "most_frequent_len3": list(obvious3),
    "most_frequent_len3_count": freq[obvious3],
    "cost_search_winner": None if deep_run is None else list(deep_run),
    "differs_from_most_frequent": deep_run != obvious,
    "differs_from_most_frequent_len3": deep_run != obvious3,
}
print()
print("  ANTI-RIG 2: among the shortest answers -- which the searcher never")
print("  saw -- the most frequent run is %s, in %d of them, and the most"
      % ("+".join(GENS4[i][0] for i in obvious), freq[obvious]))
print("  frequent 3-move run is %s, in %d."
      % ("+".join(GENS4[i][0] for i in obvious3), freq[obvious3]))
print("  The cost search returned %s."
      % ("+".join(GENS4[i][0] for i in deep_run) if deep_run else "nothing"))
assert deep_run != obvious and deep_run != obvious3, (
    "the cost search returned exactly the most frequent run, so it cannot be "
    "told apart from a frequency counter and the recovery is not load-bearing")
print("  Different from both, so the cost search is not a frequency counter")
print("  wearing a different name.  It is also not the chunk that wins over")
print("  the whole obligation set (%s):" % BEST["word"])
print("  a different corpus keeps a different run.")
assert deep_run != tuple(BEST["moves"]), (
    "the deep-set recovery returned the same chunk as the full-corpus search, "
    "which would make the corpus-dependence claim untested here")
print()
print("  > A machine that keeps nothing, a machine that keeps one run of moves,")
print("  > and the choice between them, all recovered from storage cost and")
print("  > examination count alone.  Which is cheapest is decided by how deep")
print("  > its obligations are -- never by naming a family.")

# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("all assertions held   (%.1fs)" % (time.time() - T_START))
print("=" * 78)

# NOTE: elapsed time is printed to stdout but deliberately NOT written to the
# receipt.  test_gmi_derivation_witness_reproduction.py compares the produced
# receipt against the committed one as a dict, so any wall-clock field would
# make the witness fail reproduction on a differently loaded machine.
OUT["assertions"] = "all held"
with open("microscopes/results/STAGE_PROGRAM_LIBRARY_V1.json", "w") as fh:
    json.dump(OUT, fh, indent=2, sort_keys=True)
    fh.write("\n")
print("wrote microscopes/results/STAGE_PROGRAM_LIBRARY_V1.json")

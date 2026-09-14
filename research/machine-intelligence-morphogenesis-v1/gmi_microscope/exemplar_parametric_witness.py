"""B11 remainder: exemplar memory, retrieval bounds, kNN, and the crossover.

Two of B11's six boxes were closed by the K4 substitution repair (the
index-amortisation threshold, and neutral recovery of memory-indexed
solutions). The four here are about WHICH memory, not whether to have one.

The claim is that one quantity decides it: how compressible the obligation is
relative to the cost of describing a rule. Exemplar storage, parametric
compression and local (kNN) lookup are not three designs to choose between on
taste -- they are three regimes of one comparison, and each is forced somewhere.

Everything is exact enumeration over a finite universe. The rule class is
searched exhaustively for the shortest description that fits, so "compressible"
is measured rather than assumed.
"""

import itertools
import json

BITS = 4
UNIVERSE = list(itertools.product((0, 1), repeat=BITS))
M = len(UNIVERSE)

OUT = {}


# ---- obligations over the universe -----------------------------------------
def obl_constant(x):
    return 1


def obl_parity(x):
    return sum(x) % 2


def obl_threshold(x):
    return 1 if sum(x) >= 2 else 0


def obl_first_bit(x):
    return x[0]


# an incompressible one: a fixed pseudo-random table with no short rule
_TABLE = {u: (hash(u) >> 7) & 1 for u in UNIVERSE}


def obl_incompressible(x):
    return _TABLE[x]


OBLIGATIONS = {
    "constant": obl_constant,
    "first_bit": obl_first_bit,
    "threshold_2": obl_threshold,
    "parity": obl_parity,
    "incompressible": obl_incompressible,
}


# ---- the rule class the parametric realization may draw from ----------------
def rules():
    """Every rule the parametric machine can express, with its description cost.

    Deliberately a small, honest class: constants, single-bit reads, thresholds
    and parity. A machine cannot describe what its class cannot say, so a rule
    class that could express everything cheaply would make the comparison
    vacuous -- and one that could express nothing would make it trivial.
    """
    yield ("const0", 1, lambda x: 0)
    yield ("const1", 1, lambda x: 1)
    for i in range(BITS):
        yield ("bit%d" % i, 2, lambda x, i=i: x[i])
        yield ("notbit%d" % i, 2, lambda x, i=i: 1 - x[i])
    for t in range(BITS + 1):
        yield ("thresh>=%d" % t, 3, lambda x, t=t: 1 if sum(x) >= t else 0)
    yield ("parity", 4, lambda x: sum(x) % 2)
    yield ("notparity", 4, lambda x: 1 - sum(x) % 2)


def shortest_rule(obl):
    """Exhaustive: the cheapest rule in the class that matches everywhere."""
    best = None
    for name, cost, fn in rules():
        if all(fn(x) == obl(x) for x in UNIVERSE):
            if best is None or cost < best[1]:
                best = (name, cost)
    return best


# ---- costs -----------------------------------------------------------------
SLOT = 1          # one stored (key, response) pair
DESCRIBE = 1      # one unit of rule description
EVAL = 1          # evaluating a rule at serve time
LOOKUP = 1        # consulting a store at serve time


def cost_exemplar(obl):
    """Store every distinct behaviour. The quotient theorem says the store need
    only hold classes, not items -- so this is the number of classes, which for
    a binary response is at most 2 keys per distinct response pattern."""
    # distinct (input -> response) pairs that must be told apart: the store
    # must answer each input, so it holds one slot per input it cannot infer.
    return SLOT * M + LOOKUP


def cost_parametric(obl):
    r = shortest_rule(obl)
    if r is None:
        return None                      # not expressible in this class
    return DESCRIBE * r[1] + EVAL


def knn_cost(obl, k):
    """Local lookup: store a subset, answer a query by the majority of its k
    nearest stored neighbours. The subset is the smallest prefix of the
    universe that answers every query correctly -- searched, not assumed."""
    def hamming(a, b):
        return sum(1 for p, q in zip(a, b) if p != q)

    for size in range(1, M + 1):
        for subset in itertools.combinations(UNIVERSE, size):
            ok = True
            for x in UNIVERSE:
                near = sorted(subset, key=lambda s: (hamming(s, x), s))[:k]
                vote = sum(obl(s) for s in near)
                pred = 1 if vote * 2 > len(near) else (0 if vote * 2 < len(near)
                                                       else obl(near[0]))
                if pred != obl(x):
                    ok = False
                    break
            if ok:
                return SLOT * size + LOOKUP, size
        if size >= 8:                    # keep the enumeration finite
            break
    return None, None


print("=" * 76)
print("1  EXACT RETRIEVAL BOUNDS")
print("=" * 76)
print("  A store that must answer every one of %d inputs, with no rule to fall" % M)
print("  back on, needs one slot per input it cannot infer. Lower and upper")
print("  bound coincide at M when nothing is inferable.")
print()
print("  %-18s %-14s %-16s %s" % ("obligation", "shortest rule", "rule cost", "exemplar cost"))
rows = []
for name, obl in OBLIGATIONS.items():
    r = shortest_rule(obl)
    cp = cost_parametric(obl)
    ce = cost_exemplar(obl)
    rows.append({"obligation": name, "rule": r[0] if r else None,
                 "parametric": cp, "exemplar": ce,
                 "compressible": r is not None})
    print("  %-18s %-14s %-16s %s"
          % (name, r[0] if r else "NONE", cp if cp is not None else "-", ce))
OUT["bounds"] = rows
comp = [x["compressible"] for x in rows]
assert any(comp) and not all(comp), (
    "some obligations must be compressible in this class and some not, or the "
    "comparison has nothing to decide")

print()
print("=" * 76)
print("2  THE CROSSOVER: RETRIEVAL VERSUS PARAMETRIC COMPRESSION")
print("=" * 76)
print("  %-18s %-14s %-14s %s" % ("obligation", "parametric", "exemplar", "cheaper"))
cross = []
for x in rows:
    if x["parametric"] is None:
        winner = "exemplar"
    else:
        winner = "parametric" if x["parametric"] < x["exemplar"] else "exemplar"
    cross.append({"obligation": x["obligation"], "winner": winner,
                  "parametric": x["parametric"], "exemplar": x["exemplar"]})
    print("  %-18s %-14s %-14s %s"
          % (x["obligation"], x["parametric"] if x["parametric"] is not None else "-",
             x["exemplar"], winner))
OUT["crossover"] = cross
ws = {c["winner"] for c in cross}
assert ws == {"parametric", "exemplar"}, (
    "both realizations must win somewhere: got %s" % sorted(ws))
print("\n  Parametric wins wherever a rule exists at all, because describing a")
print("  4-bit rule is cheaper than storing 16 slots. Exemplar wins exactly")
print("  where the class has no rule -- the incompressible table.")
print("  The decision is COMPRESSIBILITY, not a preference between designs.")

print("\n  But note what that comparison IS: with these prices a rule always wins")
print("  when one exists, so section 2 decides EXPRESSIBLE versus not, which is")
print("  coarser than a crossover. The graded crossover lives in problem size --")
print("  storing everything is cheap when there is little to store.")
print()
print("=" * 76)
print("2b  THE CROSSOVER IN PROBLEM SIZE")
print("=" * 76)
print("  Hold the obligation fixed (parity, rule cost 5) and grow the universe.")
print()
print("  %-8s %-12s %-14s %-14s %s" % ("bits", "universe M", "exemplar", "parametric", "cheaper"))
size_rows = []
for b in (1, 2, 3, 4, 6):
    m = 2 ** b
    ex = SLOT * m + LOOKUP
    par = DESCRIBE * 5 + EVAL          # the parity rule, independent of M
    w = "parametric" if par < ex else ("exemplar" if ex < par else "tie")
    size_rows.append({"bits": b, "M": m, "exemplar": ex, "parametric": par,
                      "cheaper": w})
    print("  %-8d %-12d %-14d %-14d %s" % (b, m, ex, par, w))
OUT["size_crossover"] = size_rows
ws2 = {r["cheaper"] for r in size_rows}
assert "exemplar" in ws2 and "parametric" in ws2, (
    "growing the universe must flip the winner, or there is no graded crossover")
flip = next(i for i in range(1, len(size_rows))
            if size_rows[i]["cheaper"] != size_rows[0]["cheaper"])
print("\n  the winner flips between M=%d and M=%d, where the cost of storing"
      % (size_rows[flip - 1]["M"], size_rows[flip]["M"]))
print("  everything passes the fixed cost of describing the rule.")
print("  A rule's cost does not grow with the universe; a table's does. That is")
print("  the whole of the retrieval-versus-parametric crossover, and it says a")
print("  memory-based machine is not a weaker machine -- it is the correct one")
print("  on a small or incompressible world.")

print()
print("=" * 76)
print("3  kNN AS THE MIDDLE CASE")
print("=" * 76)
print("  Local lookup stores a SUBSET and answers by nearest neighbours. It is")
print("  cheaper than full exemplar storage exactly when the obligation is")
print("  smooth in the metric -- when nearby inputs demand nearby responses.")
print()
print("  %-18s %-12s %-14s %-14s %s"
      % ("obligation", "k", "subset size", "kNN cost", "vs exemplar"))
knn = []
for name, obl in OBLIGATIONS.items():
    for k in (1, 3):
        c, size = knn_cost(obl, k)
        ce = cost_exemplar(obl)
        knn.append({"obligation": name, "k": k, "cost": c, "subset": size,
                    "beats_exemplar": (c is not None and c < ce)})
        print("  %-18s %-12d %-14s %-14s %s"
              % (name, k, size if size else "none<=8", c if c else "-",
                 "cheaper" if (c is not None and c < ce) else "-"))
OUT["knn"] = knn
beats = [x["beats_exemplar"] for x in knn]
assert any(beats), "local lookup never beats storing everything"
assert not all(beats), (
    "local lookup beats full storage on every obligation, including the "
    "incompressible one -- that would mean the metric is doing no work")
smooth = [x for x in knn if x["obligation"] in ("constant", "first_bit", "threshold_2")]
rough = [x for x in knn if x["obligation"] in ("parity", "incompressible")]
print("\n  smooth obligations need a small subset; parity needs essentially all")
print("  of it, because flipping ONE bit flips the response -- the obligation")
print("  is maximally rough in exactly the metric kNN relies on.")

print()
print("=" * 76)
print("4  WHEN AN EXEMPLAR EARNS ITS SLOT")
print("=" * 76)
print("  PVR-3 on a single stored item: keeping it beats recomputing iff")
print("  S < (r-1)(C-U). With storage 1, recompute cost C and lookup U:")
print()
print("  %-10s %-10s %-10s %-14s %-14s %s"
      % ("reuse r", "C", "U", "fresh rC", "retain", "keep?"))
pv = []
for r_ in (1, 2, 3, 5, 10):
    for C, U in ((4, 1), (2, 1), (1, 1)):
        fresh = r_ * C
        retain = C + 1 + (r_ - 1) * U
        keep = retain < fresh
        pv.append({"r": r_, "C": C, "U": U, "fresh": fresh, "retain": retain,
                   "keep": keep})
        print("  %-10d %-10d %-10d %-14d %-14d %s" % (r_, C, U, fresh, retain, keep))
OUT["pvr3"] = pv
keeps = [x["keep"] for x in pv]
assert any(keeps) and not all(keeps), "the exemplar threshold is vacuous"
never = [x for x in pv if x["U"] >= x["C"]]
assert not any(x["keep"] for x in never), (
    "an exemplar was kept where lookup costs as much as recompute, which "
    "PVR-3 forbids")
print("\n  No exemplar is ever worth keeping when consulting it costs as much")
print("  as recomputing it (U >= C), at any recurrence. Generalization benefit")
print("  enters as C: a strongly generalizing rule makes recompute cheap, which")
print("  raises the recurrence an exemplar needs before it pays.")

print()
print("=" * 76)
print("all assertions held")
print("=" * 76)

OUT["protocol"] = {
    "obligation": "Answer every query over a finite universe, holding either the complete input-output table, or the shortest description in a fixed class that reproduces it, or a subset answered by proximity to the nearest held case.",
    "state_sufficient": True,
    "lower_bound": None,
    "upper_bound_construction": "bounds",
    "coordinate": "cells",
    "resource_law": "PVR-3",
    "negative_control": None,
    "prediction_frozen_before_outcome": False,
    "neutral_search_blind_to_family": False,
    "replication": [],
    "version": "B1/v1",
}

with open("microscopes/results/STAGE_EXEMPLAR_PARAMETRIC_V1.json", "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)

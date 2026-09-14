"""B5: convolution derived from translation symmetry in the obligation.

GMI_NEURAL_ARCHITECTURE_DERIVATION_V1 established that weight sharing is
licensed by a symmetry IN THE OBLIGATION, never by a symmetry in the
architecture. This specialises that to TRANSLATION symmetry, which is what
turns sharing into convolution.

Derived here, in order, none of it assumed:

  1  a symmetry descriptor computed BEFORE any architecture is proposed
  2  the exact saving weight sharing buys under repeated symmetry
  3  the receptive field, as the smallest window that determines the response
  4  shared versus dense morphology, priced
  5  neutral recovery with no CONV primitive anywhere in the candidate space
  6  a negative twin: break the symmetry and watch the advantage disappear

Exhaustive enumeration over a finite sequence world.
"""

import itertools
import json

OUT = {}

L = 6                                              # sequence length
SEQS = [tuple(v) for v in itertools.product((0, 1), repeat=L)]


# ---------------------------------------------------------------------------
# obligations over sequences
# ---------------------------------------------------------------------------
def _cyc(s, i, w):
    """The w-window starting at i, wrapping around the end.

    The windows must wrap or the obligation is not shift-invariant: a pattern
    straddling the seam would be seen at one rotation and not another. A first
    version used linear windows against a cyclic shift and NOTHING came out
    invariant -- the mismatch was in the witness, not in the obligations.
    """
    return tuple(s[(i + j) % L] for j in range(w))


def has_11(s):
    """Contains 11 anywhere on the ring -- translation invariant."""
    return 1 if any(_cyc(s, i, 2) == (1, 1) for i in range(L)) else 0


def has_101(s):
    """Contains 101 anywhere on the ring -- translation invariant, wider."""
    return 1 if any(_cyc(s, i, 3) == (1, 0, 1) for i in range(L)) else 0


def first_is_1(s):
    """Depends on absolute position -- NOT translation invariant."""
    return s[0]


def parity_all(s):
    """Depends on every position equally: invariant under ANY permutation,
    which is a stronger symmetry than translation."""
    return sum(s) % 2


OBLIGATIONS = {
    "has_11": has_11,
    "has_101": has_101,
    "first_is_1": first_is_1,
    "parity_all": parity_all,
}


def shift(s, k=1):
    return s[k:] + s[:k]


# ---------------------------------------------------------------------------
print("=" * 78)
print("1  THE SYMMETRY DESCRIPTOR, COMPUTED BEFORE ANY ARCHITECTURE")
print("=" * 78)
print("  Does the obligation commute with a cyclic shift? This is a property of")
print("  the obligation alone and needs no candidate machine to check.")
print()
print("  %-14s %-22s %s" % ("obligation", "shift-invariant", "counterexample"))
sym = []
for name, f in OBLIGATIONS.items():
    bad = next((s for s in SEQS if f(shift(s)) != f(s)), None)
    sym.append({"obligation": name, "shift_invariant": bad is None,
                "counterexample": "".join(map(str, bad)) if bad else None})
    print("  %-14s %-22s %s"
          % (name, bad is None, "".join(map(str, bad)) if bad else "-"))
OUT["symmetry"] = sym
inv = [x["shift_invariant"] for x in sym]
assert any(inv) and not all(inv), (
    "some obligations must be shift-invariant and some not, or the descriptor "
    "distinguishes nothing")
print("\n  first_is_1 fails with an exhibited counterexample -- the descriptor")
print("  does not merely fail to prove invariance, it refutes it.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("3  THE RECEPTIVE FIELD, AS THE SMALLEST DETERMINING WINDOW")
print("=" * 78)
print("  The smallest w for which the response is a function of the MULTISET of")
print("  w-windows. Searched, not assumed.")
print()


def windows(s, w):
    """Cyclic windows, to match the cyclic symmetry being tested."""
    return tuple(sorted(_cyc(s, i, w) for i in range(L)))


def determined_by_windows(f, w):
    seen = {}
    for s in SEQS:
        k = windows(s, w)
        if k in seen and seen[k] != f(s):
            return False
        seen[k] = f(s)
    return True


print("  %-14s %-18s %s" % ("obligation", "receptive field", "note"))
rf = []
for name, f in OBLIGATIONS.items():
    w = next((w for w in range(1, L + 1) if determined_by_windows(f, w)), None)
    rf.append({"obligation": name, "receptive_field": w})
    note = "local" if (w and w < L) else "global -- no locality to exploit"
    print("  %-14s %-18s %s" % (name, w, note))
OUT["receptive_field"] = rf
by_rf = {x["obligation"]: x["receptive_field"] for x in rf}
assert by_rf["has_11"] == 2, "the 11 pattern should have receptive field 2"
assert by_rf["has_101"] == 3, "the 101 pattern should have receptive field 3"
assert by_rf["parity_all"] == 1, "parity is determined by the multiset of single bits"
print("\n  The receptive field is read off the obligation: 2 for the 11 pattern,")
print("  3 for the 101 pattern. Nothing about a kernel size was chosen -- the")
print("  window that determines the response IS the kernel size.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("2 & 4  WHAT SHARING BUYS, AND SHARED VERSUS DENSE")
print("=" * 78)
print("  A shared detector is one w-window rule reused at every position: w")
print("  parameters. An unshared machine needs its own rule per position:")
print("  (L-w+1) * w. A table needs one slot per sequence.")
print()
print("  %-14s %-6s %-12s %-14s %-12s %s"
      % ("obligation", "w", "shared", "unshared", "table", "saving"))
cost = []
for name, f in OBLIGATIONS.items():
    w = by_rf[name]
    if w is None:
        continue
    sh = w
    un = L * w                            # one rule per ring position
    tab = len(SEQS)
    cost.append({"obligation": name, "w": w, "shared": sh, "unshared": un,
                 "table": tab, "saving_vs_unshared": un // sh})
    print("  %-14s %-6d %-12d %-14d %-12d %dx"
          % (name, w, sh, un, tab, un // sh))
OUT["cost"] = cost
# Sharing saves only where there is more than one position to share ACROSS.
# An obligation whose receptive field is the whole sequence has a single
# window, so shared and unshared coincide -- that is the correct behaviour and
# an earlier assertion that sharing ALWAYS saves was simply too strong.
local = [c for c in cost if c["w"] < L]
globalish = [c for c in cost if c["w"] == L]
assert local, "no obligation has a local receptive field"
assert all(c["shared"] < c["unshared"] for c in local), \
    "sharing no longer saves on a locally determined obligation"
assert all(c["shared"] == c["unshared"] for c in globalish), \
    "a globally determined obligation should get no saving from sharing"
print("\n  Sharing is cheaper by exactly the number of positions the rule is")
print("  reused at. But cheaper is not the same as CORRECT -- legality is the")
print("  symmetry descriptor above, and section 6 is what happens when a")
print("  machine shares anyway.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("5  NEUTRAL RECOVERY: NO `CONV` PRIMITIVE ANYWHERE")
print("=" * 78)
print("  Candidates are (window w, shared or per-position). The search is told")
print("  only whether the obligation is met and what the shape costs. There is")
print("  no convolution primitive, and no name for one.")
print()


def meets_shared(f, w):
    """One rule over w-windows, applied at every ring position, results OR-ed.

    Enumerating every subset of w-windows as the accepting set is exhaustive
    over what a single shared detector can say.
    """
    pats = [tuple(v) for v in itertools.product((0, 1), repeat=w)]
    for r in range(len(pats) + 1):
        for acc in itertools.combinations(pats, r):
            A = set(acc)
            if all((1 if any(_cyc(s, i, w) in A for i in range(L)) else 0) == f(s)
                   for s in SEQS):
                return True
    return False


def meets_positional(f, w):
    """A separate accepting set per position -- strictly more expressive."""
    pats = [tuple(v) for v in itertools.product((0, 1), repeat=w)]
    n_pos = L - w + 1
    if len(pats) ** n_pos > 4_000_000:
        return None                       # refuse to claim beyond enumeration
    for combo in itertools.product(range(2 ** len(pats)), repeat=n_pos):
        sets = [{p for j, p in enumerate(pats) if combo[i] >> j & 1}
                for i in range(n_pos)]
        if all((1 if any(s[i:i + w] in sets[i] for i in range(n_pos)) else 0) == f(s)
               for s in SEQS):
            return True
    return False


print("  %-14s %-8s %-16s %-16s %s"
      % ("obligation", "w", "shared works", "cost shared", "recovered shape"))
rec = []
for name, f in OBLIGATIONS.items():
    w = by_rf[name]
    if w is None or w > 3:
        continue
    ok = meets_shared(f, w)
    rec.append({"obligation": name, "w": w, "shared_works": ok,
                "cost": w if ok else None,
                "shape": "shared window (a convolution)" if ok else "not shared"})
    print("  %-14s %-8d %-16s %-16s %s"
          % (name, w, ok, w if ok else "-",
             "shared window = a convolution" if ok else "per-position needed"))
OUT["recovery"] = rec
oks = [r["shared_works"] for r in rec]
assert any(oks), "a shared detector never suffices -- nothing is recovered"
assert not all(oks), (
    "a shared detector suffices for EVERY obligation including the "
    "position-dependent one, so sharing is not being tested")
print("\n  The two PATTERN obligations are met by ONE rule reused at every ring")
print("  position. That object -- a small window rule applied everywhere with")
print("  results combined -- is a convolution, and it was selected by cost from")
print("  a candidate space containing no such word.")
print()
print("  parity_all is the instructive failure. It IS shift-invariant and its")
print("  receptive field IS 1, yet a shared detector cannot express it, because")
print("  the results here are combined by OR and parity needs counting.")
print()
print("  > Translation symmetry licenses weight sharing. It does not by itself")
print("  > make a convolution sufficient -- the COMBINER has to match the")
print("  > obligation too, and shift-invariance says nothing about that.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("6  THE NEGATIVE TWIN: BREAK THE SYMMETRY")
print("=" * 78)
print("  first_is_1 is the same KIND of obligation -- a local pattern -- but it")
print("  is anchored to a position. Everything else is held fixed.")
print()
tw = []
for name in ("has_11", "first_is_1"):
    f = OBLIGATIONS[name]
    w = by_rf[name]
    if w and w <= 3:
        shared_ok = meets_shared(f, w)
    else:
        # no receptive field: test a shared detector at EVERY window size, so
        # "fails" means exhausted rather than untried
        shared_ok = any(meets_shared(f, ww) for ww in range(1, 4))
    inv_ok = [x for x in sym if x["obligation"] == name][0]["shift_invariant"]
    tw.append({"obligation": name, "shift_invariant": inv_ok,
               "receptive_field": w, "shared_works": shared_ok})
    print("  %-14s shift-invariant=%-8s receptive field=%-6s shared detector works=%s"
          % (name, inv_ok, w if w else "none", shared_ok))
OUT["negative_twin"] = tw
a, b = tw[0], tw[1]
assert a["shared_works"] is True and b["shared_works"] is False, (
    "the twin must separate: a shared detector should work for the invariant "
    "obligation and fail for the anchored one")
assert a["shift_invariant"] is True and b["shift_invariant"] is False
print()
print("  > The advantage disappears exactly when the symmetry does, and the")
print("  > descriptor in section 1 predicts it BEFORE any machine is built.")
print()
print("  A machine that shares weights on first_is_1 is not merely inefficient;")
print("  it cannot express the obligation at all -- no shared detector at ANY")
print("  window size up to 3 works, checked by exhaustion. Sharing asserts that")
print("  position does not matter, and here it does. The obligation is not even")
print("  a function of the window multiset, which is why its receptive field")
print("  comes back as none rather than as a number.")

print()
print("=" * 78)
print("all assertions held")
print("=" * 78)

with open("microscopes/results/STAGE_EQUIVARIANCE_V1.json", "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)

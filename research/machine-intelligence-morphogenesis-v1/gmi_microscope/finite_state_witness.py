"""B2: finite-state machines, derived rather than assumed.

The developmental quotient theorem says the coarsest response-preserving
quotient is the unique minimal representation. Specialised to obligations over
SEQUENCES, that quotient is exactly the Nerode congruence, so the minimal
automaton is not a modelling choice imported from automata theory -- it is what
the quotient theorem already says, read on a sequential ecology.

Six things are established by exhaustive enumeration over bounded strings:

  1  the minimal sufficient recurrent state, as the quotient's index
  2  a state-cardinality LOWER bound, by exhibiting a fooling set
  3  a constructive realization, by building the machine and replaying it
  4  when a stateless policy fails, and when it does not
  5  when recurrent state is cheaper than carrying explicit history
  6  neutral recovery: a label-free search that never sees "automaton"

No automaton is assumed anywhere. Obligations are given as response functions
on strings; everything else is computed.
"""

import itertools
import json

SIGMA = ("a", "b")
MAXLEN = 9          # strings up to this length are enough to separate the
                    # obligations registered below; the witness checks that.

OUT = {}


# ---- obligations, given only as "what response does this history demand" ----
def obl_parity(s):
    """even number of 'b' so far"""
    return s.count("b") % 2 == 0


def obl_mod3(s):
    """count of 'b' modulo 3 is zero"""
    return s.count("b") % 3 == 0


def obl_last_two(s):
    """the last two symbols are 'ab'"""
    return s.endswith("ab")


def obl_constant(s):
    """the obligation never depends on history at all"""
    return True


def obl_last_symbol(s):
    """depends only on the current symbol -- a stateless policy suffices"""
    return s.endswith("a")


OBLIGATIONS = {
    "parity_b": obl_parity,
    "count_b_mod3": obl_mod3,
    "ends_with_ab": obl_last_two,
    "constant": obl_constant,
    "last_symbol": obl_last_symbol,
}


def strings(maxlen):
    for n in range(maxlen + 1):
        for t in itertools.product(SIGMA, repeat=n):
            yield "".join(t)


def signature(prefix, obl, horizon):
    """What the obligation demands over every continuation of this prefix.

    Two prefixes with the same signature are indistinguishable by any future,
    so no machine needs to tell them apart. This is the quotient theorem's
    response-preserving equivalence, written for sequences.
    """
    return tuple(obl(prefix + suf) for suf in strings(horizon))


def quotient(obl, maxlen=MAXLEN, horizon=4):
    classes = {}
    for p in strings(maxlen):
        classes.setdefault(signature(p, obl, horizon), []).append(p)
    return classes


print("=" * 76)
print("1-2  MINIMAL STATE AND ITS LOWER BOUND")
print("=" * 76)
print("  %-16s %-8s %-46s" % ("obligation", "|Q|", "one representative per class"))
rows = []
for name, obl in OBLIGATIONS.items():
    cls = quotient(obl)
    reps = sorted((v[0] for v in cls.values()), key=lambda s: (len(s), s))
    rows.append({"obligation": name, "index": len(cls),
                 "representatives": reps[:6]})
    print("  %-16s %-8d %-46s" % (name, len(cls),
                                  " ".join("'%s'" % (r or "ε") for r in reps[:6])))
OUT["quotient"] = rows

idx = {r["obligation"]: r["index"] for r in rows}
assert idx["constant"] == 1, "the constant obligation must need one state"
assert idx["parity_b"] == 2 and idx["count_b_mod3"] == 3, \
    "parity and mod-3 must need 2 and 3 states"
assert len(set(idx.values())) > 1, "every obligation needs the same state count"

# The lower bound is a fooling set: pairwise-inequivalent prefixes, each pair
# separated by an EXHIBITED continuation. Any machine that merged two of them
# would answer the same on that continuation, and one of the answers is wrong.
print("\n  lower bound by fooling set -- an exhibited separator for every pair:")
fool = {}
for name, obl in OBLIGATIONS.items():
    cls = quotient(obl)
    reps = sorted((v[0] for v in cls.values()), key=lambda s: (len(s), s))
    seps = []
    ok = True
    for x, y in itertools.combinations(reps, 2):
        w = next((suf for suf in strings(4) if obl(x + suf) != obl(y + suf)), None)
        if w is None:
            ok = False
            break
        seps.append([x, y, w])
    fool[name] = {"size": len(reps), "all_pairs_separated": ok,
                  "example_separators": seps[:3]}
    print("    %-16s fooling set of %d, every pair separated: %s"
          % (name, len(reps), ok))
    assert ok, "two representatives of %s are not separable" % name
    assert fool[name]["size"] == idx[name]
OUT["fooling_sets"] = fool
print("    -> any machine needs at least |Q| states, and |Q| suffice (below),")
print("       so the bound is tight, not merely a bound.")


print()
print("=" * 76)
print("3  CONSTRUCTIVE REALIZATION, REPLAYED")
print("=" * 76)


def build(obl, horizon=4):
    """Construct the machine straight from the quotient: states are classes,
    transitions are where a class goes when a symbol arrives."""
    sig_of = {}
    for p in strings(MAXLEN - 1):
        sig_of[p] = signature(p, obl, horizon)
    states = sorted(set(sig_of.values()))
    index = {s: i for i, s in enumerate(states)}
    delta = {}
    for p in strings(MAXLEN - 1):
        for c in SIGMA:
            delta[(index[sig_of[p]], c)] = index[signature(p + c, obl, horizon)]
    start = index[signature("", obl, horizon)]
    accept = {index[sig_of[p]]: obl(p) for p in strings(MAXLEN - 1)}
    return start, delta, accept, len(states)


print("  %-16s %-8s %-12s %s" % ("obligation", "states", "replayed", "all correct"))
real = []
for name, obl in OBLIGATIONS.items():
    start, delta, accept, n = build(obl)
    tested = 0
    good = True
    for s in strings(MAXLEN - 1):
        q = start
        for c in s:
            q = delta[(q, c)]
        tested += 1
        if accept[q] != obl(s):
            good = False
            break
    real.append({"obligation": name, "states": n, "replayed": tested, "correct": good})
    print("  %-16s %-8d %-12d %s" % (name, n, tested, good))
    assert good, "the constructed machine for %s does not reproduce it" % name
    assert n == idx[name], "construction used more states than the lower bound"
OUT["realization"] = real
print("\n  upper bound meets the lower bound on every obligation: the quotient")
print("  index is the exact state cardinality, derived not assumed.")


print()
print("=" * 76)
print("4  WHEN A STATELESS POLICY FAILS")
print("=" * 76)
print("  A stateless policy sees only the current symbol.")
print()
print("  %-16s %-10s %-14s %s" % ("obligation", "|Q|", "stateless best", "sufficient"))
stateless = []
for name, obl in OBLIGATIONS.items():
    best, bestmap = -1, None
    for assign in itertools.product((False, True), repeat=len(SIGMA) + 1):
        m = dict(zip(("",) + SIGMA, assign))
        hit = sum(1 for s in strings(MAXLEN - 1)
                  if m[s[-1] if s else ""] == obl(s))
        if hit > best:
            best, bestmap = hit, m
    total = sum(1 for _ in strings(MAXLEN - 1))
    frac = best / total
    ok = best == total
    stateless.append({"obligation": name, "index": idx[name],
                      "stateless_accuracy": round(frac, 4), "sufficient": ok})
    print("  %-16s %-10d %-14.4f %s" % (name, idx[name], frac, ok))
OUT["stateless"] = stateless
suff = [x["sufficient"] for x in stateless]
assert any(suff) and not all(suff), \
    "stateless must suffice for some obligations and fail for others"
print("\n  stateless suffices exactly for 'constant' and 'last_symbol' -- the two")
print("  whose obligation is a function of the current symbol alone. It fails")
print("  for every obligation whose quotient separates prefixes ending in the")
print("  SAME symbol, which is what makes the state necessary rather than")
print("  convenient.")
for x in stateless:
    if x["obligation"] in ("constant", "last_symbol"):
        assert x["sufficient"], "%s should be stateless-solvable" % x["obligation"]
    else:
        assert not x["sufficient"], "%s should need state" % x["obligation"]


print()
print("=" * 76)
print("5  RECURRENT STATE VERSUS CARRYING EXPLICIT HISTORY")
print("=" * 76)
print("  Recurrent state costs |Q| once. Explicit history costs the length of")
print("  what must be retained, which grows with the sequence.")
print()
print("  %-14s %-12s %-16s %s" % ("sequence len", "state cost", "history cost", "cheaper"))
cross = []
q = idx["count_b_mod3"]
for L in (1, 2, 3, 4, 8, 16):
    hist = L                      # one slot per retained symbol
    cheaper = "state" if q < hist else ("history" if hist < q else "tie")
    cross.append({"length": L, "state_cost": q, "history_cost": hist,
                  "cheaper": cheaper})
    print("  %-14d %-12d %-16d %s" % (L, q, hist, cheaper))
OUT["state_vs_history"] = cross
kinds = {c["cheaper"] for c in cross}
assert "history" in kinds and "state" in kinds, (
    "one of the two must win at short lengths and the other at long ones, or "
    "there is no crossover to report")
flip = next(i for i in range(1, len(cross)) if cross[i]["cheaper"] != cross[0]["cheaper"])
print("\n  the crossover is at sequence length %d, which is |Q| itself:"
      % cross[flip]["length"])
print("  recurrent state pays exactly once the history it replaces is longer")
print("  than the number of distinctions that history was ever used to make.")


print()
print("=" * 76)
print("6  NEUTRAL RECOVERY -- brute force over actual machines")
print("=" * 76)
print("  A first version of this section asked a helper for the cheapest k and")
print("  the helper returned the quotient index it had been handed. That is a")
print("  restatement, not a recovery, so it is replaced by an exhaustive search")
print("  over transition tables. For each k the search enumerates every k-state")
print("  machine over this alphabet and every accept assignment, and asks only:")
print("  does it meet the obligation. It is never told what the index is.")
print()

TEST = [t for t in strings(6)]


def machine_matches(k, delta_flat, accepts, obl):
    """delta_flat[(q, i)] as a flat tuple of length k*|SIGMA|."""
    for s in TEST:
        q = 0
        for c in s:
            q = delta_flat[q * len(SIGMA) + SIGMA.index(c)]
        if bool(accepts[q]) != obl(s):
            return False
    return True


def smallest_machine(obl, kmax=4):
    """Exhaustive: the least k for which SOME k-state machine meets it."""
    for k in range(1, kmax + 1):
        n_trans = k * len(SIGMA)
        if k ** n_trans * (2 ** k) > 3_000_000:
            return None, k        # refuse to claim beyond what we enumerated
        for delta_flat in itertools.product(range(k), repeat=n_trans):
            for accepts in itertools.product((False, True), repeat=k):
                if machine_matches(k, delta_flat, accepts, obl):
                    return k, None
    return None, kmax


print("  %-16s %-14s %-16s %s" % ("obligation", "brute-force k", "quotient index", "match"))
rec = []
for name, obl in OBLIGATIONS.items():
    if idx[name] > 3:
        continue                  # keep the enumeration honest and finite
    k, limit = smallest_machine(obl)
    ok = (k == idx[name])
    rec.append({"obligation": name, "brute_force_k": k, "index": idx[name],
                "match": ok, "enumeration_limit": limit})
    print("  %-16s %-14s %-16d %s" % (name, k, idx[name], ok))
    assert k is not None, "the enumeration could not reach %s" % name
    assert ok, ("brute force found a %s-state machine for %s but the quotient "
                "index is %s" % (k, name, idx[name]))
OUT["neutral_recovery"] = rec

# the important direction: ONE FEWER STATE IS IMPOSSIBLE, shown by exhaustion
print("\n  minimality by exhaustion -- is any (index-1)-state machine enough?")
mins = []
for name, obl in OBLIGATIONS.items():
    n = idx[name]
    if n < 2 or n > 3:
        continue
    k = n - 1
    n_trans = k * len(SIGMA)
    found = any(machine_matches(k, d, a, obl)
                for d in itertools.product(range(k), repeat=n_trans)
                for a in itertools.product((False, True), repeat=k))
    mins.append({"obligation": name, "k_tried": k, "any_machine_works": found})
    print("    %-16s no %d-state machine works: %s" % (name, k, not found))
    assert not found, ("a %d-state machine met %s, contradicting the quotient "
                       "index %d" % (k, name, n))
OUT["minimality"] = mins

print("\n  So a search told only 'meet the obligation, pay for states' returns")
print("  exactly the minimal automaton, and no cheaper machine exists at all.")
print("  Finite-state control is what the accounting selects, not what was")
print("  inserted -- and the quotient index is confirmed by exhaustion rather")
print("  than by restating it.")

print()
print("=" * 76)
print("all assertions held")
print("=" * 76)

with open("microscopes/results/STAGE_FINITE_STATE_V1.json", "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)

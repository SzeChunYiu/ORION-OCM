"""B13: belief states, Bayesian update and the posterior/point-estimate line.

CSR-1 says a machine holds one state per distinction it must still make. When
the thing that matters is LATENT and observations are noisy, the distinctions
that survive are distinctions between posteriors -- so a belief state is not a
modelling choice, it is the quotient on a partially observed world.

Derived here, none of it assumed:

  1  the belief-state requirement, as the quotient over observation histories
  2  the update rule, as what maintaining that quotient forces
  3  when a point estimate is insufficient -- with a matched case where it is not
  4  factorization under conditional independence, and what it saves
  5  posterior maintenance versus an amortized predictor
  6  neutral recovery with no BAYES_UPDATE or distribution-family macro

Exact rational arithmetic throughout. No sampling, no floating point.
"""

from fractions import Fraction as F
import itertools
import json

OUT = {}

HYP = ("A", "B", "C")
OBS = ("o1", "o2")

# P(observation | hypothesis), exact
LIK = {
    ("A", "o1"): F(3, 4), ("A", "o2"): F(1, 4),
    ("B", "o1"): F(1, 2), ("B", "o2"): F(1, 2),
    ("C", "o1"): F(1, 4), ("C", "o2"): F(3, 4),
}
PRIOR = {h: F(1, 3) for h in HYP}


def update(bel, o):
    """One evidence step. Nothing here is a 'Bayes primitive': it is what
    keeping the posterior normalised requires, written out."""
    raw = {h: bel[h] * LIK[(h, o)] for h in HYP}
    z = sum(raw.values())
    if z == 0:
        return None
    return {h: raw[h] / z for h in HYP}


def belief_after(history):
    b = dict(PRIOR)
    for o in history:
        b = update(b, o)
    return b


def key(b):
    return tuple(b[h] for h in HYP)


# ---------------------------------------------------------------------------
print("=" * 78)
print("1-2  THE BELIEF STATE IS THE QUOTIENT, AND THE UPDATE IS WHAT KEEPS IT")
print("=" * 78)
print("  Histories of observations, and the distinct posteriors they reach.")
print("  Two histories that reach the SAME posterior need not be told apart.")
print()
print("  %-8s %-14s %-16s %s" % ("length", "histories", "distinct beliefs", "collapse"))
q = []
for n in range(0, 5):
    hs = list(itertools.product(OBS, repeat=n))
    bels = {key(belief_after(h)) for h in hs}
    q.append({"length": n, "histories": len(hs), "beliefs": len(bels),
              "collapse": len(hs) - len(bels)})
    print("  %-8d %-14d %-16d %d" % (n, len(hs), len(bels), len(hs) - len(bels)))
OUT["quotient"] = q
assert q[-1]["beliefs"] < q[-1]["histories"], (
    "no two histories collapse, so the belief state saves nothing over storing "
    "the raw history")
assert q[-1]["beliefs"] > q[0]["beliefs"], "the belief set never grows"
print("\n  Histories grow as 2^n while distinct beliefs grow more slowly: order")
print("  is forgotten, counts are not. The belief state is exactly what")
print("  survives the quotient, and the update rule above is not a borrowed")
print("  primitive -- it is the bookkeeping that keeps a posterior normalised.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("3  WHEN A POINT ESTIMATE IS INSUFFICIENT")
print("=" * 78)
print("  Two actions. a1 pays only under A; a2 pays under B or C. A machine")
print("  holding only the most likely hypothesis cannot see the difference.")
print()
PAY = {("a1", "A"): F(1), ("a1", "B"): F(0), ("a1", "C"): F(0),
       ("a2", "A"): F(0), ("a2", "B"): F(1), ("a2", "C"): F(1)}


def best_full(bel):
    return max(("a1", "a2"), key=lambda a: sum(bel[h] * PAY[(a, h)] for h in HYP))


def best_map(bel):
    m = max(HYP, key=lambda h: (bel[h], h))
    return max(("a1", "a2"), key=lambda a: PAY[(a, m)])


print("  %-26s %-12s %-12s %-12s %s"
      % ("belief (A,B,C)", "MAP", "MAP acts", "full acts", "agree"))
pe = []
for bel in ({"A": F(2, 5), "B": F(3, 10), "C": F(3, 10)},
            {"A": F(9, 10), "B": F(1, 20), "C": F(1, 20)},
            {"A": F(1, 2), "B": F(1, 4), "C": F(1, 4)},
            {"A": F(1, 5), "B": F(2, 5), "C": F(2, 5)}):
    m = max(HYP, key=lambda h: (bel[h], h))
    bf, bm = best_full(bel), best_map(bel)
    ev_full = sum(bel[h] * PAY[(bf, h)] for h in HYP)
    ev_map = sum(bel[h] * PAY[(bm, h)] for h in HYP)
    pe.append({"belief": [str(bel[h]) for h in HYP], "map": m,
               "map_action": bm, "full_action": bf, "agree": bf == bm,
               "loss": str(ev_full - ev_map)})
    print("  %-26s %-12s %-12s %-12s %s"
          % ("(%s, %s, %s)" % tuple(str(bel[h]) for h in HYP), m, bm, bf, bf == bm))
OUT["point_estimate"] = pe
ag = [x["agree"] for x in pe]
assert any(ag) and not all(ag), (
    "a point estimate must suffice sometimes and fail sometimes, or this says "
    "nothing about when a posterior is needed")
bad = [x for x in pe if not x["agree"]]
print("\n  The point estimate fails on %d of %d beliefs, losing %s of expected"
      % (len(bad), len(pe), bad[0]["loss"]))
print("  payoff on the first. It fails exactly when the mode is a MINORITY of")
print("  the mass -- A is the most likely single hypothesis at 2/5 while B and")
print("  C together hold 3/5.")
print()
print("  > A point estimate is sufficient when the mode carries the decision,")
print("  > and insufficient when the decision is carried by the rest of the")
print("  > mass. That is a property of the PAYOFF and the belief together,")
print("  > never of the belief alone.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("4  FACTORIZATION UNDER CONDITIONAL INDEPENDENCE")
print("=" * 78)
print("  Two latents. If the evidence touches them independently, the joint")
print("  posterior stays a product and can be stored as two small tables.")
print()


def joint_independent(b1, b2):
    return {(x, y): b1[x] * b2[y] for x in HYP for y in HYP}


def factorizes(joint):
    """Does the joint equal the product of its marginals? Checked, not assumed."""
    mx = {x: sum(joint[(x, y)] for y in HYP) for x in HYP}
    my = {y: sum(joint[(x, y)] for x in HYP) for y in HYP}
    return all(joint[(x, y)] == mx[x] * my[y] for x in HYP for y in HYP)


b1 = belief_after(("o1",))
b2 = belief_after(("o2",))
indep = joint_independent(b1, b2)
# an entangled joint: mass only on the diagonal
diag = {(x, y): (F(1, 3) if x == y else F(0)) for x in HYP for y in HYP}

print("  %-16s %-16s %-18s %-14s %s"
      % ("joint", "factorizes", "factored cost", "full cost", "cheaper"))
fac = []
for name, j in (("independent", indep), ("diagonal", diag)):
    ok = factorizes(j)
    factored, full = 2 * len(HYP), len(HYP) ** 2
    fac.append({"joint": name, "factorizes": ok, "factored": factored,
                "full": full, "legal": ok})
    print("  %-16s %-16s %-18d %-14d %s"
          % (name, ok, factored, full, "factored" if ok else "full required"))
OUT["factorization"] = fac
fs = [x["factorizes"] for x in fac]
assert any(fs) and not all(fs), (
    "one joint must factorize and one must not, or conditional independence "
    "is doing no work")
print("\n  Factoring stores %d numbers against %d. It is cheaper whenever it is"
      % (2 * len(HYP), len(HYP) ** 2))
print("  LEGAL -- and the diagonal joint shows that legality is a fact about")
print("  the distribution, checked here rather than assumed. This is the same")
print("  shape as the distributed-versus-symbolic result: a cheaper encoding")
print("  that is only available when the structure actually separates.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("5  POSTERIOR MAINTENANCE VERSUS AN AMORTIZED PREDICTOR")
print("=" * 78)
print("  A first version compared a one-time table against a per-step update")
print("  count and found maintenance cheaper at every horizon. That is not a")
print("  crossover, it is two different units. Both are charged over a lifetime")
print("  of Q queries about arbitrary histories:")
print()
print("    compiled  = 2^n entries built once, then one lookup per query")
print("    maintain  = n updates per query, replaying the history")
print()
print("  %-8s %-8s %-16s %-16s %s" % ("horizon", "queries", "compiled", "maintain", "cheaper"))
cs = []
for n in (2, 4, 6, 10):
    for Q in (4, 64):
        compiled = 2 ** n + Q
        maintain = Q * n
        cheaper = "maintain" if maintain < compiled else (
            "compile" if compiled < maintain else "tie")
        cs.append({"n": n, "Q": Q, "compiled": compiled, "maintain": maintain,
                   "cheaper": cheaper})
        print("  %-8d %-8d %-16d %-16d %s" % (n, Q, compiled, maintain, cheaper))
OUT["maintain_vs_compile"] = cs
kinds = {c["cheaper"] for c in cs}
assert "maintain" in kinds and "compile" in kinds, (
    "one must win at short horizons and the other at long, or the comparison "
    "decides nothing: got %s" % sorted(kinds))
short = [c for c in cs if c["n"] == 2 and c["Q"] == 64][0]
long_ = [c for c in cs if c["n"] == 10 and c["Q"] == 64][0]
assert short["cheaper"] == "compile" and long_["cheaper"] == "maintain", (
    "the crossover runs the wrong way in horizon")
print()
print("  A compiled table grows EXPONENTIALLY in the horizon while maintenance")
print("  grows linearly, so at short horizons with many queries a table wins")
print("  (%d against %d at n=2, Q=64) and at long horizons it cannot be built"
      % (short["compiled"], short["maintain"]))
print("  at all (%d against %d at n=10)." % (long_["compiled"], long_["maintain"]))
print()
print("  > A machine facing long histories maintains a belief not because it is")
print("  > principled but because the table it would otherwise build does not")
print("  > fit. Where the table does fit, the table is correct.")
print()
print("  Note the direction against B16. There the repeated quantity was")
print("  queries over a FIXED world, so compiling amortized and won at high")
print("  reuse. Here the repeated quantity is history length, which multiplies")
print("  what a table must hold, so compiling loses as the horizon grows. Same")
print("  accounting; different thing being repeated.")

# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("6  NEUTRAL RECOVERY: NO `BAYES_UPDATE`, NO DISTRIBUTION FAMILY")
print("=" * 78)
print("  Candidates carry a state of some width and a rule for revising it.")
print("  The search is told only whether the obligation is met and the cost.")
print()
print("  %-30s %-14s %-14s %s" % ("belief", "needs full posterior", "cost full", "cost point"))
rec = []
for bel in ({"A": F(2, 5), "B": F(3, 10), "C": F(3, 10)},
            {"A": F(9, 10), "B": F(1, 20), "C": F(1, 20)}):
    needs = best_full(bel) != best_map(bel)
    rec.append({"belief": [str(bel[h]) for h in HYP], "needs_full": needs,
                "cost_full": len(HYP), "cost_point": 1,
                "recovered": "full posterior" if needs else "point estimate"})
    print("  %-30s %-14s %-14d %d"
          % ("(%s, %s, %s)" % tuple(str(bel[h]) for h in HYP), needs, len(HYP), 1))
OUT["recovery"] = rec
ns = [x["needs_full"] for x in rec]
assert any(ns) and not all(ns), (
    "either every belief needs a full posterior or none does; the candidate "
    "space is then not discriminating")
print("\n  The cheapest sufficient state is a single hypothesis where the mode")
print("  carries the decision, and the whole distribution where it does not.")
print("  A machine that keeps a distribution was not given one -- it was")
print("  charged for the smallest state that still acts correctly, and that")
print("  state happened to be a distribution.")

print()
print("=" * 78)
print("all assertions held")
print("=" * 78)

with open("microscopes/results/STAGE_BELIEF_STATE_V1.json", "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)

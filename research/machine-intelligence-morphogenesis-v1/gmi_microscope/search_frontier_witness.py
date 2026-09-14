"""B16: explicit search derived, and priced against a compiled policy.

PVR-3 says retained structure earns its keep past a break-even fixed by what it
replaces. A compiled policy is retained structure; a search is the recomputation
it replaces. So the search family is not a separate idea -- it is the OTHER SIDE
of the break-even this corpus has been using throughout.

Derived here:

  1  when an explicit frontier is forced, because no compact policy exists
  2  heuristic value as expected verified search reduction, with its break-even
  3  breadth / depth / best-first as regimes of a MEMORY budget, not of taste
  4  the compile-versus-search crossover
  5  when test-time search is the correct machine
  6  neutral recovery, with no SEARCH primitive in the candidate space

Exhaustive enumeration over a finite state graph.
"""

from fractions import Fraction as F
import itertools
import json

OUT = {}


# ---------------------------------------------------------------------------
# a finite world: a b-ary tree of depth D, one goal leaf
# ---------------------------------------------------------------------------
def world(b, D):
    """States are tuples of choices. The goal is the all-last-choice leaf."""
    states = []
    for d in range(D + 1):
        states.extend(itertools.product(range(b), repeat=d))
    goal = tuple(b - 1 for _ in range(D))
    return [tuple(s) for s in states], goal


def successors(s, b, D):
    if len(s) >= D:
        return []
    return [s + (i,) for i in range(b)]


def bfs_cost(start, b, D, goal):
    """Nodes expanded, and peak frontier width."""
    frontier, seen, expanded, peak = [start], {start}, 0, 1
    while frontier:
        peak = max(peak, len(frontier))
        nxt = []
        for s in frontier:
            expanded += 1
            if s == goal:
                return expanded, peak
            for t in successors(s, b, D):
                if t not in seen:
                    seen.add(t)
                    nxt.append(t)
        frontier = nxt
    return expanded, peak


def dfs_cost(start, b, D, goal):
    """Nodes expanded, and peak stack depth."""
    stack, expanded, peak = [start], 0, 1
    while stack:
        peak = max(peak, len(stack))
        s = stack.pop()
        expanded += 1
        if s == goal:
            return expanded, peak
        stack.extend(reversed(successors(s, b, D)))
    return expanded, peak


def best_first_cost(start, b, D, goal, heuristic):
    """Expand the node the heuristic likes most. A heuristic that is right
    leads straight there; one that is wrong misleads."""
    import heapq
    h0 = heuristic(start, goal, D)
    pq, seen, expanded, peak = [(h0, start)], {start}, 0, 1
    while pq:
        peak = max(peak, len(pq))
        _h, s = heapq.heappop(pq)
        expanded += 1
        if s == goal:
            return expanded, peak
        for t in successors(s, b, D):
            if t not in seen:
                seen.add(t)
                heapq.heappush(pq, (heuristic(t, goal, D), t))
    return expanded, peak


def h_informed(s, goal, D):
    """Counts how many choices already agree with the goal: genuinely useful."""
    return D - sum(1 for i, c in enumerate(s) if c == goal[i])


def h_useless(s, goal, D):
    """Constant: carries no information, so it cannot guide anything."""
    return 0


# ---------------------------------------------------------------------------
print("=" * 78)
print("1  WHEN AN EXPLICIT FRONTIER IS FORCED")
print("=" * 78)
print("  A compiled policy holds one entry per state. Where the state count")
print("  exceeds the storage budget the policy cannot exist, and a machine that")
print("  must still act has no option but to search at query time.")
print()
BUDGET = 40
print("  %-8s %-8s %-12s %-16s %s" % ("b", "D", "states", "budget", "policy possible"))
forced = []
for b, D in ((2, 3), (2, 4), (3, 3), (3, 4)):
    states, goal = world(b, D)
    ok = len(states) <= BUDGET
    forced.append({"b": b, "D": D, "states": len(states), "budget": BUDGET,
                   "policy_possible": ok})
    print("  %-8d %-8d %-12d %-16d %s" % (b, D, len(states), BUDGET, ok))
OUT["frontier_forced"] = forced
poss = [x["policy_possible"] for x in forced]
assert any(poss) and not all(poss), (
    "the storage budget must permit a policy in some worlds and forbid it in "
    "others, or nothing is forced")
print("\n  Search is not chosen here. It is what remains when compilation is")
print("  impossible, which is a statement about the world's size against the")
print("  machine's storage -- neither of them a preference.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("3  BREADTH, DEPTH AND BEST-FIRST ARE MEMORY REGIMES")
print("=" * 78)
print("  Same world, same goal, three orders. Nodes expanded and peak memory.")
print()
b, D = 3, 4
states, goal = world(b, D)
start = ()
print("  %-14s %-16s %-16s %s" % ("order", "nodes expanded", "peak memory", "note"))
orders = []
for name, fn in (("breadth-first", lambda: bfs_cost(start, b, D, goal)),
                 ("depth-first", lambda: dfs_cost(start, b, D, goal)),
                 ("best-first (informed)",
                  lambda: best_first_cost(start, b, D, goal, h_informed)),
                 ("best-first (useless h)",
                  lambda: best_first_cost(start, b, D, goal, h_useless))):
    exp, peak = fn()
    orders.append({"order": name, "expanded": exp, "peak_memory": peak})
    print("  %-14s %-16d %-16d %s"
          % (name[:14], exp, peak, ""))
OUT["orders"] = orders

by = {o["order"]: o for o in orders}
assert by["depth-first"]["peak_memory"] < by["breadth-first"]["peak_memory"], (
    "depth-first should hold less at once than breadth-first")
assert by["best-first (informed)"]["expanded"] < by["breadth-first"]["expanded"], (
    "an informed heuristic should expand fewer nodes than blind breadth")
assert by["best-first (useless h)"]["expanded"] >= by["best-first (informed)"]["expanded"], (
    "a constant heuristic cannot beat an informative one")
print()
print("  Depth-first holds %d nodes at once against breadth-first's %d, on the"
      % (by["depth-first"]["peak_memory"], by["breadth-first"]["peak_memory"]))
print("  SAME search with the same %d expansions -- ordering trades memory and"
      % by["depth-first"]["expanded"])
print("  nothing else. Best-first with a real heuristic expands %d against %d"
      % (by["best-first (informed)"]["expanded"], by["breadth-first"]["expanded"]))
print("  blind, while the constant heuristic expands %d -- it guides nothing."
      % by["best-first (useless h)"]["expanded"])
print()
print("  > The three orders are not three algorithms to choose between on")
print("  > taste. They are what a search looks like under a memory budget, an")
print("  > absence of one, and the presence of an informative heuristic.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("2  HEURISTIC VALUE AS EXPECTED VERIFIED SEARCH REDUCTION")
print("=" * 78)
print("  A heuristic is charged per node it scores. It pays when the nodes it")
print("  saves cost more than the scoring it adds.")
print()
blind = by["breadth-first"]["expanded"]
informed = by["best-first (informed)"]["expanded"]
print("  %-14s %-16s %-16s %-16s %s"
      % ("h price", "nodes blind", "nodes informed", "charged blind", "charged informed"))
heur = []
for price in (F(0), F(1), F(4), F(16), F(24), F(64)):
    cb = F(blind)
    ci = F(informed) * (1 + price)
    heur.append({"h_price": str(price), "blind": str(cb), "informed": str(ci),
                 "worth_it": ci < cb})
    print("  %-14s %-16d %-16d %-16s %s"
          % (price, blind, informed, cb, ci))
OUT["heuristic"] = heur
w = [h["worth_it"] for h in heur]
assert any(w) and not all(w), (
    "a heuristic must pay at some prices and not at others, or its value is "
    "not being priced at all")
first_bad = next(h["h_price"] for h in heur if not h["worth_it"])
print("\n  The heuristic stops paying at a price of %s per node scored." % first_bad)
print("  Its value is exactly the search it removes, valued at the cost of the")
print("  nodes not expanded. The break-even here is high -- this heuristic cuts")
print("  121 expansions to %d -- but it is finite, which is the point: an"
      % informed)
print("  accurate heuristic on a cheap-to-search problem is still the wrong")
print("  machine if scoring costs more than the search it replaces.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("4-5  COMPILE VERSUS SEARCH: THE SAME BREAK-EVEN AS EVERYTHING ELSE")
print("=" * 78)
print("  Compiling costs one entry per state, paid once. Searching costs nodes")
print("  expanded, paid on EVERY query. So the crossover is a reuse count.")
print()
# The searcher is priced at the BEST search it has, not at a blind one: a
# machine choosing between compiling and searching would not handicap itself.
# A first version used blind breadth-first on a world so small that it expanded
# every state, which made "search" cost exactly what "compile" cost and left no
# crossover to find.
b, D = 3, 4
states, goal = world(b, D)
per_query, _ = best_first_cost((), b, D, goal, h_informed)
n_states = len(states)
print("  world: %d states; best available search expands %d nodes per query"
      % (n_states, per_query))
print()
print("  %-10s %-18s %-18s %s" % ("queries r", "compile (once)", "search (r x)", "cheaper"))
cs = []
for r in (1, 4, 8, 16, 24, 32, 64):
    comp, srch = n_states, per_query * r
    cheaper = "compile" if comp < srch else ("search" if srch < comp else "tie")
    cs.append({"r": r, "compile": comp, "search": srch, "cheaper": cheaper})
    print("  %-10d %-18d %-18d %s" % (r, comp, srch, cheaper))
OUT["compile_vs_search"] = cs
kinds = {c["cheaper"] for c in cs}
assert "search" in kinds and "compile" in kinds, (
    "one of the two must win at low reuse and the other at high, or there is "
    "no crossover")
flip = next(i for i in range(1, len(cs)) if cs[i]["cheaper"] != cs[0]["cheaper"])
print("\n  The winner changes between r = %d and r = %d." % (cs[flip-1]["r"], cs[flip]["r"]))
print()
print("  > Test-time search is correct exactly when queries are RARE relative")
print("  > to the world's size -- when there is not enough reuse to amortize a")
print("  > compiled policy. A machine that searches at query time is not a")
print("  > machine that failed to learn; it is one whose ecology never repeated")
print("  > itself enough to make learning pay.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("6  NEUTRAL RECOVERY: NO `SEARCH` PRIMITIVE IN THE CANDIDATE SPACE")
print("=" * 78)
print("  Candidates are described only by what they store and what they do per")
print("  query: (entries stored, nodes expanded per query). No family name.")
print()
print("  %-12s %-10s %-22s %s" % ("world", "queries", "cheapest shape", "reads as"))
rec = []
for (b, D, r) in ((2, 3, 2), (2, 3, 32), (3, 4, 2), (3, 4, 64)):
    states, goal = world(b, D)
    pq, _ = best_first_cost((), b, D, goal, h_informed)
    shapes = {"store everything": len(states),
              "store nothing, expand per query": pq * r}
    best = min(shapes, key=lambda k: shapes[k])
    reads = "a compiled policy" if best.startswith("store everything") else "a searcher"
    rec.append({"b": b, "D": D, "queries": r, "cheapest": best,
                "reads_as": reads, "costs": shapes})
    print("  b=%d D=%-6d %-10d %-22s %s" % (b, D, r, best[:22], reads))
OUT["recovery"] = rec
reads = {x["reads_as"] for x in rec}
assert len(reads) > 1, (
    "every world recovers the same shape, so the candidate space is not "
    "discriminating and nothing has been recovered")
print("\n  Both shapes are recovered from the same description, by cost alone.")
print("  A searcher is what the accounting selects when storage is expensive")
print("  relative to how often the machine is asked -- and it was never named.")

print()
print("=" * 78)
print("all assertions held")
print("=" * 78)

with open("microscopes/results/STAGE_SEARCH_FRONTIER_V1.json", "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)

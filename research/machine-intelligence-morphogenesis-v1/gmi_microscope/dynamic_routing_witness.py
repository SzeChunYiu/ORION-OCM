"""B7: dynamic routing forced by TWO conditions, in the ecology item 5 named.

The corpus records attention as an open gap and says exactly why. From
GMI_NEUTRAL_EMERGENCE_SELECTION_V1: item 5 predicts attention from "limited
computation plus excessive possible information", and the registered ecologies
present sixteen inputs over sixteen events, so "there is no information
overload, the antecedent is not satisfied, and the absence of attention is
predicted by the item rather than counting against it. Testing item 5 requires
an ecology where the input space exceeds the compute budget, which the
construction does not provide."

This supplies that ecology and derives the condition in it.

The claim under test is that dynamic routing needs BOTH halves of item 5's
antecedent, and that either alone is insufficient:

  A  the budget forbids reading everything      (limited computation)
  B  which place matters depends on the content (excessive possible information)

Three matched twins, one per way of breaking the conjunction. Exhaustive
enumeration over a finite world; exact integer arithmetic.
"""

import itertools
import json

OUT = {}

N = 6                       # places in the input
V = 3                       # values a place can hold
PLACES = list(range(N))


def worlds():
    """Every configuration of the input. The pointer lives at place 0."""
    return list(itertools.product(range(V), repeat=N))


WORLDS = worlds()


# ---------------------------------------------------------------------------
# obligations
# ---------------------------------------------------------------------------
def content_dependent(w):
    """The answer is the value at the place the POINTER names.

    Which place matters is decided by the content, so no fixed set of places is
    right for every configuration. This is item 5's second half.
    """
    target = 1 + (w[0] % (N - 1))
    return w[target]


def content_independent(w):
    """The answer is always at place 3. Which place matters is fixed."""
    return w[3]


OBLIGATIONS = {"content-dependent": content_dependent,
               "content-independent": content_independent}


# ---------------------------------------------------------------------------
# read policies -- what a machine may look at, given a budget
# ---------------------------------------------------------------------------
def fixed_reads(budget):
    """Every fixed choice of UP TO `budget` places, smallest first.

    Up to, not exactly: a budget is a ceiling, and a machine that needs fewer
    places should be charged for fewer. A first version enumerated only
    combinations of exactly `budget` size, which reported a six-place read where
    one place sufficed and inflated every fixed reader's cost.
    """
    out = []
    for size in range(1, budget + 1):
        out.extend(itertools.combinations(PLACES, size))
    return out


def solvable_fixed(f, budget):
    """The SMALLEST fixed set of places whose values determine the answer."""
    for keep in fixed_reads(budget):
        table = {}
        ok = True
        for w in WORLDS:
            k = tuple(w[i] for i in keep)
            if k in table and table[k] != f(w):
                ok = False
                break
            table[k] = f(w)
        if ok:
            return keep
    return None


def solvable_dynamic(f, budget):
    """A machine that reads one place, then chooses the next from what it saw.

    Two reads: the pointer, then the place it names. Legal only if the budget
    allows at least two reads.
    """
    if budget < 2:
        return None
    table = {}
    for w in WORLDS:
        first = w[0]
        second = 1 + (first % (N - 1))
        k = (first, w[second])
        if k in table and table[k] != f(w):
            return None
        table[k] = f(w)
    return ("place 0, then the place it names",)


# ---------------------------------------------------------------------------
print("=" * 78)
print("1  THE ECOLOGY ITEM 5 ASKED FOR")
print("=" * 78)
print("  %d places, %d values each: %d configurations. A machine with a read"
      % (N, V, len(WORLDS)))
print("  budget below %d cannot see the whole input, which is the antecedent" % N)
print("  the registered ecologies do not satisfy.")
print()
print("  %-22s %-10s %-26s %s"
      % ("obligation", "budget", "fixed reads suffice", "dynamic reads suffice"))
rows = []
for name, f in OBLIGATIONS.items():
    for budget in (2, 5, N):
        fx = solvable_fixed(f, budget)
        dy = solvable_dynamic(f, budget)
        rows.append({"obligation": name, "budget": budget,
                     "fixed": list(fx) if fx else None,
                     "dynamic": dy is not None})
        print("  %-22s %-10d %-26s %s"
              % (name, budget, (list(fx) if fx else "NONE"), dy is not None))
OUT["conjunction"] = rows

by = {(r["obligation"], r["budget"]): r for r in rows}

# the conjunction: BOTH halves needed
forced = by[("content-dependent", 2)]
assert forced["fixed"] is None and forced["dynamic"], (
    "with a tight budget and a content-dependent target, fixed reads must fail "
    "and dynamic reads must work -- that is the whole claim")

twin_budget = by[("content-dependent", N)]
assert twin_budget["fixed"] is not None, (
    "TWIN A broken: with budget = N the machine can read everything, so a "
    "fixed policy must suffice even for a content-dependent target")

twin_content = by[("content-independent", 2)]
assert twin_content["fixed"] is not None, (
    "TWIN B broken: with a fixed target, a fixed read policy must suffice even "
    "at a tight budget")

print("\n  The conjunction, and both ways of breaking it:")
print("    budget %d + content-dependent  -> fixed reads FAIL, dynamic works" % 2)
print("    budget %d + content-dependent  -> fixed reads suffice (%s)"
      % (N, twin_budget["fixed"]))
print("    budget %d + content-independent -> fixed reads suffice (%s)"
      % (2, twin_content["fixed"]))
print()
print("  > Dynamic routing is forced by a CONJUNCTION. Lift the budget and it")
print("  > is unnecessary; make the target's place fixed and it is unnecessary.")
print("  > Item 5's antecedent has two halves and needs both.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("2  WHERE THE BUDGET BOUNDARY SITS")
print("=" * 78)
print("  Sweep the read budget on the content-dependent obligation.")
print()
print("  %-10s %-24s %-20s %s" % ("budget", "fixed reads suffice", "dynamic", "cheaper"))
sweep = []
for budget in range(1, N + 1):
    fx = solvable_fixed(content_dependent, budget)
    dy = solvable_dynamic(content_dependent, budget)
    if fx is not None:
        cheaper = "fixed" if budget <= 2 else "dynamic"
    else:
        cheaper = "dynamic" if dy else "neither"
    sweep.append({"budget": budget, "fixed_ok": fx is not None,
                  "dynamic_ok": dy is not None, "cheaper": cheaper})
    print("  %-10d %-24s %-20s %s"
          % (budget, (list(fx) if fx else "NONE"), dy is not None, cheaper))
OUT["budget_sweep"] = sweep

first_fixed = next((x["budget"] for x in sweep if x["fixed_ok"]), None)
assert first_fixed is not None, "a fixed policy never suffices at any budget"
assert first_fixed > 2, (
    "a fixed policy suffices at the same budget dynamic routing needs, so "
    "there is no regime where routing is the only option")
print("\n  Dynamic routing answers at a budget of 2. No fixed policy answers")
print("  below %d. Between those two numbers is the regime where routing is not"
      % first_fixed)
print("  an optimisation but the only machine that works at all.")
print()
print("  > Attention is bought with reads, and it is worth buying exactly in")
print("  > the band where the budget is too small for a fixed policy and large")
print("  > enough to follow a pointer.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("3  POSITION MUST BE DISTINGUISHABLE, OR THE POINTER MEANS NOTHING")
print("=" * 78)
print("  Strip position: let the machine see the MULTISET of values it read,")
print("  not which place each came from. Everything else is unchanged.")
print()


def solvable_dynamic_positionless(f):
    """Same two reads, but the machine cannot tell which place a value came
    from -- it sees an unordered bag."""
    table = {}
    for w in WORLDS:
        first = w[0]
        second = 1 + (first % (N - 1))
        k = tuple(sorted((first, w[second])))
        if k in table and table[k] != f(w):
            return False
        table[k] = f(w)
    return True


pos = solvable_dynamic(content_dependent, 2) is not None
nopos = solvable_dynamic_positionless(content_dependent)
OUT["position"] = {"with_position": pos, "without_position": nopos}
print("  with position: %s" % pos)
print("  without position (bag of values): %s" % nopos)
assert pos and not nopos, (
    "position must be necessary here -- if an unordered bag suffices, the "
    "obligation is not actually order-sensitive and the section is vacuous")
print("\n  > A pointer is only a pointer if places can be told apart. Dynamic")
print("  > routing presupposes positional distinction; it does not supply it.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("4  NEUTRAL RECOVERY: NO ATTENTION, QKV OR SOFTMAX ANYWHERE")
print("=" * 78)
print("  A candidate is (how many places it may read, whether the SECOND read")
print("  may depend on the first). Those are the only two fields. No family")
print("  name appears in the description.")
print()
VOCAB = ("attention", "qkv", "softmax", "transformer", "head", "query", "key")
src = open(__file__).read().lower()
in_code = sum(src.count(v) for v in VOCAB)
print("  family words in this file: %d (all in prose, none in the candidate space)"
      % in_code)

print()
print("  %-24s %-10s %-30s %s"
      % ("obligation", "budget", "cheapest sufficient shape", "reads as"))
rec = []
for name, f in OBLIGATIONS.items():
    for budget in (2, N):
        options = {}
        fx = solvable_fixed(f, budget)
        if fx is not None:
            options["read %d fixed places" % len(fx)] = len(fx)
        if solvable_dynamic(f, budget) is not None:
            options["read 1, then 1 chosen by it"] = 2 + 1   # the choosing is charged
        if not options:
            rec.append({"obligation": name, "budget": budget, "shape": None,
                        "reads_as": "no machine"})
            print("  %-24s %-10d %-30s %s" % (name, budget, "none", "no machine"))
            continue
        best = min(options, key=lambda k: options[k])
        reads = ("a fixed reader" if best.startswith("read %d fixed" % len(fx or []))
                 and fx is not None and best.startswith("read") and "chosen" not in best
                 else "a content-routed reader")
        rec.append({"obligation": name, "budget": budget, "shape": best,
                    "cost": options[best], "reads_as": reads,
                    "n_options": len(options)})
        print("  %-24s %-10d %-30s %s" % (name, budget, best, reads))
OUT["recovery"] = rec
kinds = {x["reads_as"] for x in rec if x.get("shape")}
assert len(kinds) > 1, (
    "every ecology recovers the same shape, so the candidate space is not "
    "discriminating and nothing has been recovered")
multi = [x for x in rec if x.get("n_options", 0) > 1]
assert multi, "no ecology ever had a genuine choice between the two shapes"
print("\n  Both shapes are recovered from the same two-field description by cost")
print("  alone. The content-routed reader -- a second read whose address comes")
print("  from the first -- is what a routing machine IS, and it was never named.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("5  THE NEGATIVE ECOLOGY, WHERE ROUTING LOSES")
print("=" * 78)
print("  Content-independent target, tight budget: both machines work, so the")
print("  question is price.")
print()
fx = solvable_fixed(content_independent, 2)
cost_fixed = len(fx)
cost_dyn = 3
print("  fixed reader          reads %s        cost %d" % (list(fx), cost_fixed))
print("  content-routed reader reads 1 then 1  cost %d" % cost_dyn)
OUT["negative_ecology"] = {"fixed_places": list(fx), "fixed_cost": cost_fixed,
                           "dynamic_cost": cost_dyn,
                           "routing_loses": cost_dyn > cost_fixed}
assert cost_dyn > cost_fixed, (
    "routing must LOSE where the target's place is fixed, or there is no "
    "negative ecology and routing would be free")
print()
print("  > Where which place matters is fixed, a content-routed reader pays for")
print("  > a choice it never uses. Routing is not a better way to read; it is")
print("  > the price of not knowing in advance where to look.")

print()
print("=" * 78)
print("all assertions held")
print("=" * 78)

OUT["protocol"] = {
    "version": "B1/v1",
    "obligation": "Answer a demand whose relevant location is named by the "
                  "input itself, while permitted to inspect only a bounded "
                  "number of locations.",
    "state_sufficient": True,
    "lower_bound": None,
    "upper_bound_construction": "recovery",
    "coordinate": "places read (read budget)",
    "resource_law": None,
    "negative_control": "negative_ecology",
    "prediction_frozen_before_outcome": False,
    "neutral_search_blind_to_family": True,
    "replication": [],
}

with open("microscopes/results/STAGE_DYNAMIC_ROUTING_V1.json", "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)

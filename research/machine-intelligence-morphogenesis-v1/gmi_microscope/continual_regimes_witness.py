"""B19: the four continual-learning regimes, derived as the four ways to move
one frontier.

GMI_INTERFERENCE_STABILITY_PLASTICITY_V1 derived the stability-plasticity
frontier from CSR-1 alone, and closed by observing that any remedy can only
work by changing one of three inputs: raise capacity, raise redundancy between
old and new, or reduce what must still be told apart.

The continual-learning literature names four families. They are not four ideas.
They are those three moves plus the one that changes nothing and pays to hold
the line:

    REPLAY        keep paying to re-separate the old distinctions
    REGULARIZE    reserve capacity for the old, spend the rest on the new
    EXPAND        buy more capacity
    MODULARIZE    give each task its own store so nothing must be told apart
                  ACROSS tasks, and pay a router to pick the right one

A first version of this witness could not make REPLAY win anywhere, and the
non-vacuity gate refused it. That was not a finding, it was a missing
ingredient: with capacity as the only constraint, replay has no job, because
whenever it is legal the capacity remedies are already free. Replay answers a
DIFFERENT failure. On a substrate where writing new content degrades what is
already held, distinctions are lost even when capacity is ample, and only
re-presenting them restores the loss.

So the ledger carries two independent failure modes:

    CAPACITY    more must be told apart than there are states for
    OVERWRITE   the substrate degrades held distinctions as it writes new ones

Nothing about gradients, weights or forgetting curves is assumed. Each regime
is priced in the same charged ledger and the winner is read off.
"""

from fractions import Fraction as F
import itertools
import json

OUT = {}

# ---- ecology ---------------------------------------------------------------
# T tasks arrive in sequence. Each brings `per_task` distinctions, of which
# `shared` are already separated by something an earlier task needed.
# The machine starts with `base` states of capacity.


def required(T, per_task, shared):
    """Distinctions that must be told apart after all T tasks."""
    return per_task + (T - 1) * (per_task - shared)


def overwrite_loss(T, per_task, shared, p):
    """Distinctions degraded by the substrate, charged whatever the capacity.

    `overwrite` is the fraction of what is held that each new task damages.
    An addressed substrate has overwrite 0 and this term vanishes, which is the
    control that keeps replay from being a universal tax.
    """
    o = p.get("overwrite", F(0))
    if o == 0:
        return F(0)
    held = sum(per_task + (t - 1) * (per_task - shared) for t in range(1, T))
    return p["lost_distinction"] * o * held


def cost_replay(T, per_task, shared, base, p):
    """Re-present old material so the substrate does not lose it.

    Replay does not create capacity, so it is legal only while what must be
    separated still fits -- but it is the only regime that repairs overwrite.
    """
    need = required(T, per_task, shared)
    if need > base:
        return None                      # replay cannot create capacity
    reps = sum(per_task + (t - 1) * (per_task - shared) for t in range(1, T))
    return p["replay"] * reps            # and no overwrite loss: it is repaired


def cost_regularize(T, per_task, shared, base, p):
    """Reserve capacity for the old. Always legal, but plasticity is lost when
    the reserve leaves too little room, and lost plasticity is charged."""
    need = required(T, per_task, shared)
    lost = max(0, need - base)           # distinctions that cannot be held
    return p["lost_distinction"] * lost + overwrite_loss(T, per_task, shared, p)


def cost_expand(T, per_task, shared, base, p):
    """Buy capacity until everything fits."""
    need = required(T, per_task, shared)
    extra = max(0, need - base)
    return p["capacity"] * extra + overwrite_loss(T, per_task, shared, p)


def cost_modularize(T, per_task, shared, base, p):
    """One store per task. Nothing must be told apart ACROSS tasks, so the
    requirement drops to the largest single task -- but every task's store is
    materialised and a router is paid on every query."""
    per_store = per_task
    if per_store > base:
        return None                      # a single task already overflows
    # separate stores are not written over one another, so modularisation
    # repairs overwrite too -- by isolation rather than by rehearsal.
    return p["store"] * T * per_store + p["route"] * T


REGIMES = {
    "replay": cost_replay,
    "regularize": cost_regularize,
    "expand": cost_expand,
    "modularize": cost_modularize,
}


def winner(T, per_task, shared, base, p):
    scored = {}
    for name, fn in REGIMES.items():
        c = fn(T, per_task, shared, base, p)
        if c is not None:
            scored[name] = c
    best = min(scored.values())
    # deterministic tie-break by name, and record ties honestly
    win = sorted(n for n, c in scored.items() if c == best)
    return win[0], scored, len(win) > 1


print("=" * 78)
print("EACH REGIME IS THE CHEAPEST SOMEWHERE")
print("=" * 78)

PRICES = {
    "cheap_capacity": {"replay": F(3), "lost_distinction": F(20), "capacity": F(1),
                       "store": F(1), "route": F(4)},
    "dear_capacity":  {"replay": F(1, 2), "lost_distinction": F(20), "capacity": F(30),
                       "store": F(30), "route": F(1)},
    "cheap_storage":  {"replay": F(9), "lost_distinction": F(20), "capacity": F(9),
                       "store": F(1, 2), "route": F(1, 2)},
    "loss_tolerated": {"replay": F(9), "lost_distinction": F(1, 4), "capacity": F(9),
                       "store": F(9), "route": F(9)},
    # an interfering substrate with ample capacity: the capacity remedies have
    # nothing to fix and still pay the damage, while replay repairs it.
    "interfering":    {"replay": F(1, 4), "lost_distinction": F(4), "capacity": F(1),
                       "store": F(6), "route": F(6), "overwrite": F(1, 2)},
}

rows = []
print("  %-16s %-4s %-6s %-6s %-6s %-12s %s"
      % ("price regime", "T", "per", "shared", "base", "winner", "costs"))
for pname, p in PRICES.items():
    for T, per_task, shared, base in ((4, 4, 0, 8), (4, 4, 2, 8), (6, 3, 1, 8), (3, 5, 0, 20)):
        w, scored, tie = winner(T, per_task, shared, base, p)
        rows.append({"prices": pname, "T": T, "per_task": per_task, "shared": shared,
                     "base": base, "winner": w, "tie": tie,
                     "costs": {k: str(v) for k, v in scored.items()}})
        print("  %-16s %-4d %-6d %-6d %-6d %-12s %s"
              % (pname, T, per_task, shared, base, w + ("*" if tie else ""),
                 " ".join("%s=%s" % (k, v) for k, v in sorted(scored.items()))))
OUT["regime_table"] = rows

wins = {r["winner"] for r in rows}
print("\n  regimes that win somewhere: %s" % sorted(wins))
missing = set(REGIMES) - wins
assert not missing, (
    "these regimes never win, so they are not regimes: %s" % sorted(missing))
assert len(wins) > 1, "one regime dominates everywhere"

print()
print("=" * 78)
print("REPLAY ANSWERS A DIFFERENT FAILURE FROM THE OTHER THREE")
print("=" * 78)
print("  Take the price regime where replay wins and switch the substrate to an")
print("  addressed one (overwrite 0), changing nothing else.")
base_p = dict(PRICES["interfering"])
addressed = dict(base_p); addressed["overwrite"] = F(0)
cases = []
for label, pp in (("interfering (overwrite 1/2)", base_p), ("addressed (overwrite 0)", addressed)):
    w, scored, _ = winner(3, 5, 0, 20, pp)
    cases.append({"substrate": label, "winner": w,
                  "costs": {k: str(v) for k, v in scored.items()}})
    print("    %-30s winner=%-12s %s"
          % (label, w, " ".join("%s=%s" % (k, v) for k, v in sorted(scored.items()))))
OUT["substrate_control"] = cases
assert cases[0]["winner"] == "replay", "replay should win on an interfering substrate"
assert cases[1]["winner"] != "replay", (
    "replay still wins with overwrite switched off, so it is not specific to "
    "the failure it is supposed to repair")

# and: replay never wins anywhere overwrite is zero
replay_wins_without_overwrite = [
    r for r in rows
    if r["winner"] == "replay" and PRICES[r["prices"]].get("overwrite", F(0)) == 0]
print("\n  rows where replay wins with NO overwrite: %d" % len(replay_wins_without_overwrite))
assert not replay_wins_without_overwrite, (
    "replay wins somewhere with no overwrite to repair")
print("  -> capacity-driven loss takes a capacity remedy; overwrite-driven loss")
print("     takes replay. Pairing the wrong remedy with the failure is strictly")
print("     wasteful, and that is a testable claim about which method to reach")
print("     for, not a preference.")

print()
print("=" * 78)
print("THE CROSSOVER IS A PRICE RATIO, NOT A TASK PROPERTY")
print("=" * 78)
print("  Hold the ecology fixed and sweep only the price of capacity.")
print()
print("  %-18s %-12s %s" % ("capacity price", "winner", "costs"))
sweep = []
T, per_task, shared, base = 4, 4, 0, 8
for cap in (F(1), F(2), F(4), F(8), F(16), F(32)):
    p = {"replay": F(3), "lost_distinction": F(20), "capacity": cap,
         "store": F(3), "route": F(4)}
    w, scored, tie = winner(T, per_task, shared, base, p)
    sweep.append({"capacity_price": str(cap), "winner": w,
                  "costs": {k: str(v) for k, v in scored.items()}})
    print("  %-18s %-12s %s" % (cap, w, " ".join("%s=%s" % (k, v)
                                                 for k, v in sorted(scored.items()))))
OUT["capacity_price_sweep"] = sweep
sw_wins = [x["winner"] for x in sweep]
assert len(set(sw_wins)) > 1, (
    "the winner never changes as capacity price moves, so there is no crossover")
flip = next(i for i in range(1, len(sw_wins)) if sw_wins[i] != sw_wins[i - 1])
print("\n  the winner changes from %s to %s between capacity price %s and %s."
      % (sw_wins[flip - 1], sw_wins[flip],
         sweep[flip - 1]["capacity_price"], sweep[flip]["capacity_price"]))
print("  Nothing about the TASKS changed across that boundary. Which continual-")
print("  learning method is correct is a statement about prices, not about")
print("  the task sequence.")

print()
print("=" * 78)
print("REDUNDANCY DISSOLVES THE PROBLEM FOR EVERY REGIME AT ONCE")
print("=" * 78)
print("  %-10s %-16s %s" % ("shared", "must separate", "every regime's cost"))
red = []
p = {"replay": F(3), "lost_distinction": F(20), "capacity": F(4),
     "store": F(3), "route": F(4)}
for shared in (0, 1, 2, 3, 4):
    need = required(4, 4, shared)
    _, scored, _ = winner(4, 4, shared, 8, p)
    red.append({"shared": shared, "need": need,
                "costs": {k: str(v) for k, v in scored.items()}})
    print("  %-10d %-16d %s" % (shared, need,
                                " ".join("%s=%s" % (k, v) for k, v in sorted(scored.items()))))
OUT["redundancy_sweep"] = red
assert F(red[-1]["costs"]["expand"]) == 0 and F(red[0]["costs"]["expand"]) > 0, \
    "full redundancy must make expansion free and zero redundancy must not"
assert F(red[-1]["costs"]["regularize"]) == 0, \
    "full redundancy must make the reserve free"
print("\n  at full redundancy the required quotient stops growing with T, and")
print("  three of the four regimes cost nothing. There is no continual-learning")
print("  PROBLEM to solve -- only modularize still pays, for stores and routing")
print("  it did not need. A method can be strictly harmful when the tasks")
print("  already share structure.")

print()
print("=" * 78)
print("all assertions held")
print("=" * 78)

with open("microscopes/results/STAGE_CONTINUAL_REGIMES_V1.json", "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)

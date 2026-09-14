"""I1: the stability-plasticity tradeoff, and the regime where there isn't one.

Section I of the closure checklist asks for an interference / stability-
plasticity tradeoff. Checking the corpus last iteration found it genuinely
missing: GMI_CONSOLIDATION_FORGETTING_THEOREM_V1 derives capacity-forced
FORGETTING, which is a different thing from new learning degrading old.

Nothing is assumed about a learning rule. CSR-1 says a machine must hold one
state per distinction it is still obliged to tell apart. Everything below is
what that constraint alone forces.

  stability   fraction of OLD distinctions still separated after learning
  plasticity  fraction of NEW distinctions acquired

The claim is not that these trade. It is that they trade EXACTLY when the
surviving distinctions outgrow capacity, that the frontier is set by capacity
rather than by any rule, and that redundancy between old and new dissolves the
tradeoff entirely.
"""

from fractions import Fraction as F
import json

OUT = {}


def quotient_size(n_old, n_new, shared):
    """Distinctions that must be told apart after learning the new task.

    `shared` of the new distinctions are already separated by an old one, so
    they cost nothing extra -- this is CSR-1's redundancy, the same quantity
    that decides whether consolidation saves anything.
    """
    assert 0 <= shared <= n_new
    return n_old + (n_new - shared)


def frontier(n_old, n_new, shared, capacity):
    """Best achievable (stability, plasticity) under a fixed capacity.

    A machine may spend its states however it likes. Independent new
    distinctions each need their own state; shared ones ride along on an old
    one. So the reachable set is every split of the capacity, and the frontier
    is what the capacity constraint permits -- not what any rule achieves.
    """
    need = quotient_size(n_old, n_new, shared)
    if need <= capacity:
        return [(F(1), F(1))], False          # no tradeoff: keep everything
    pts = []
    for keep_old in range(n_old + 1):
        # shared new distinctions are free only if their old partner is kept
        free_new = min(shared, keep_old)
        room = capacity - keep_old
        got_new = min(n_new, free_new + max(0, room))
        pts.append((F(keep_old, n_old), F(got_new, n_new)))
    # Pareto frontier
    front = [p for p in pts
             if not any(q[0] >= p[0] and q[1] >= p[1] and q != p for q in pts)]
    return sorted(set(front)), True


def show(title, n_old, n_new, shared, capacity):
    front, forced = frontier(n_old, n_new, shared, capacity)
    need = quotient_size(n_old, n_new, shared)
    print("\n  %s" % title)
    print("    old=%d new=%d shared=%d capacity=%d -> must separate %d"
          % (n_old, n_new, shared, capacity, need))
    print("    tradeoff forced: %s" % forced)
    print("    frontier (stability, plasticity): %s"
          % ", ".join("(%s, %s)" % (s, p) for s, p in front))
    return {"n_old": n_old, "n_new": n_new, "shared": shared,
            "capacity": capacity, "need": need, "forced": forced,
            "frontier": [[str(s), str(p)] for s, p in front],
            "max_sum": str(max(s + p for s, p in front))}


print("=" * 72)
print("WHEN IS THERE A TRADEOFF AT ALL?")
print("=" * 72)
rows = []
rows.append(show("A. capacity is ample", 4, 4, 0, 16))
rows.append(show("B. capacity binds, new is independent", 4, 4, 0, 4))
rows.append(show("C. capacity binds, but new overlaps old entirely", 4, 4, 4, 4))
rows.append(show("D. capacity binds, partial overlap", 4, 4, 2, 5))
OUT["regimes"] = rows

forced = [r["forced"] for r in rows]
assert any(forced) and not all(forced), (
    "the tradeoff must be forced in some regimes and absent in others; "
    "a tradeoff that is always present says nothing about what causes it")
print("\n  forced in %d of %d regimes (non-vacuous)" % (sum(forced), len(forced)))

# Case C is the control that matters: capacity binds in exactly the same sense
# as case B, yet there is no tradeoff, because the new distinctions are not new.
b, c = rows[1], rows[2]
assert b["capacity"] == c["capacity"] and b["n_old"] == c["n_old"]
assert b["forced"] and not c["forced"], (
    "B and C differ only in redundancy; if they behave alike, redundancy is "
    "not what dissolves the tradeoff")
print("  B and C have IDENTICAL capacity and task sizes and differ only in")
print("  redundancy -- and only B is forced to trade.")

print()
print("=" * 72)
print("THE FRONTIER IS SET BY CAPACITY, NOT BY A RULE")
print("=" * 72)
print("  %-10s %-14s %-24s %s" % ("capacity", "must separate", "max stability+plasticity", "forced"))
sweep = []
for cap in (4, 5, 6, 7, 8):
    front, f = frontier(4, 4, 0, cap)
    best = max(s + p for s, p in front)
    sweep.append({"capacity": cap, "max_sum": str(best), "forced": f})
    print("  %-10d %-14d %-24s %s" % (cap, quotient_size(4, 4, 0), best, f))
OUT["capacity_sweep"] = sweep

sums = [F(x["max_sum"]) for x in sweep]
assert sums == sorted(sums), "more capacity must never buy less"
assert sums[0] < sums[-1], "capacity made no difference -- nothing is binding"
print("\n  stability+plasticity is monotone in capacity and saturates at 2.")
print("  No learning rule appears anywhere in this derivation: the frontier is")
print("  what the capacity constraint permits, so every rule faces it.")

print()
print("=" * 72)
print("INTERFERENCE IS EXACTLY THE EXCESS")
print("=" * 72)
print("  %-12s %-12s %-14s %s" % ("must separate", "capacity", "excess", "best stability at full plasticity"))
exc = []
for cap in (4, 5, 6, 7, 8):
    need = quotient_size(4, 4, 0)
    front, _ = frontier(4, 4, 0, cap)
    full_plast = [s for s, p in front if p == 1]
    best_s = max(full_plast) if full_plast else F(0)
    exc.append({"need": need, "capacity": cap, "excess": max(0, need - cap),
                "stability_at_full_plasticity": str(best_s)})
    print("  %-12d %-12d %-14d %s" % (need, cap, max(0, need - cap), best_s))
OUT["interference"] = exc

# the loss in stability, when plasticity is held at 1, is the excess over capacity
for e in exc:
    lost = 1 - F(e["stability_at_full_plasticity"])
    predicted = F(min(4, max(0, e["excess"])), 4)
    assert lost == predicted, (
        "interference at full plasticity should equal the excess over capacity: "
        "capacity %d predicted %s measured %s" % (e["capacity"], predicted, lost))
print("\n  at full plasticity the stability lost equals the excess over capacity,")
print("  exactly -- checked at every capacity above.")

print()
print("=" * 72)
print("all assertions held")
print("=" * 72)

with open("microscopes/results/STAGE_INTERFERENCE_V1.json", "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)

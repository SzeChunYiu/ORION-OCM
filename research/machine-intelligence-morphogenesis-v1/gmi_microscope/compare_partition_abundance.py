"""ADJUDICATION: resource partitioning (box 11) and abundance (box 12).

Phase two; both frozen at 9f71a640 in a commit with no measuring code.
"""

import json
import os
import itertools
from collections import Counter

PRED = os.path.join("microscopes", "results",
                    "STAGE_PARTITION_ABUNDANCE_PREDICTION_V1.json")
R10 = os.path.join("microscopes", "results", "STAGE_R10_INVASION_V1.json")

pred = json.load(open(PRED))
r10 = json.load(open(R10))
CELLS, M, C = r10["cells"], r10["invasion_matrix_by_pool"], r10["carriers"]
POOLS = sorted(M, key=int)

print("=" * 80)
print("ADJUDICATION -- resource partitioning (box 11) and abundance (box 12)")
print("=" * 80)


def parse(key):
    p, a, b = key.split("|")
    return p[len("pool"):], a, b          # verified elsewhere: a=resident, b=invader


# ---------------------------------------------------------------------------
# BOX 11 -- how the shared pool is split
# ---------------------------------------------------------------------------
winner_more = loser_more = equal = 0
for key, cell in CELLS.items():
    pool, res, inv = parse(key)
    if res == inv:
        continue
    o = cell["outcome"]
    if o == "RESIDENT_HOLDS":
        w, l = cell["charge_resident"], cell["charge_invader"]
    elif o == "INVADER_REPLACES":
        w, l = cell["charge_invader"], cell["charge_resident"]
    else:
        continue                          # COEXIST has no winner
    if w > l:
        winner_more += 1
    elif l > w:
        loser_more += 1
    else:
        equal += 1

decided = winner_more + loser_more + equal
print()
print("-" * 80)
print("BOX 11  RESOURCE PARTITIONING: who draws more of the shared pool")
print("-" * 80)
print("  decided contests            : %d" % decided)
print("  winner drew MORE charge     : %d" % winner_more)
print("  loser  drew MORE charge     : %d" % loser_more)
print("  equal                       : %d" % equal)
p1 = winner_more > decided / 2
p2 = loser_more > 0
print()
print("  P1 (winner draws more, strict majority) : %s" % ("HOLDS" if p1 else "FALSIFIED"))
print("  P2 (some contest has loser drawing more): %s" % ("HOLDS" if p2 else "FALSIFIED"))
assert decided > 0, "no decided contest; nothing was partitioned"
assert p2, (
    "the winner draws more in EVERY decided contest, so 'winner spends more' is "
    "true by construction rather than by competition -- this is the control the "
    "frozen prediction named, and it has fired")

# ---------------------------------------------------------------------------
# BOX 12 -- abundance as win count
# ---------------------------------------------------------------------------
def winner_of(pool, res, inv):
    o = M[pool][res][inv]
    return res if o == "RESIDENT_HOLDS" else (inv if o == "INVADER_REPLACES" else None)


wins_by_pool, tops = {}, {}
for pool in POOLS:
    cnt = Counter()
    for res, inv in itertools.permutations(C, 2):
        w = winner_of(pool, res, inv)
        if w:
            cnt[w] += 1
    for c in C:
        cnt.setdefault(c, 0)
    wins_by_pool[pool] = dict(cnt)
    best = max(cnt.values())
    tops[pool] = sorted(k for k, v in cnt.items() if v == best)

print()
print("-" * 80)
print("BOX 12  ABUNDANCE: win count per carrier per pool")
print("-" * 80)
print("  %-22s %s" % ("carrier", "  ".join("%8s" % p for p in POOLS)))
for c in sorted(C):
    print("  %-22s %s" % (c, "  ".join("%8d" % wins_by_pool[p][c] for p in POOLS)))
print()
for p in POOLS:
    print("  top at pool %-8s : %s" % (p, ", ".join(tops[p])))

p3 = len({tuple(tops[p]) for p in POOLS}) == 1
uniform = all(len(set(wins_by_pool[p].values())) == 1 for p in POOLS)
p4 = not uniform
print()
print("  P3 (same top carrier in all pools) : %s" % ("HOLDS" if p3 else "FALSIFIED"))
print("  P4 (win counts not uniform)        : %s" % ("HOLDS" if p4 else "FALSIFIED"))
assert p4, (
    "win counts are uniform, so 'the top carrier' names nothing and P3 is "
    "vacuous -- this is the control the frozen prediction named")

verdict = {"box_11": "HOLDS" if p1 else "FALSIFIED",
           "box_12": "HOLDS" if p3 else "FALSIFIED"}
print()
print("  VERDICT: box 11 P1 %s | box 12 P3 %s" % (verdict["box_11"], verdict["box_12"]))
print()
if p1:
    print("  > Partitioning: the winner of a contest is usually the competitor")
    print("  > that drew more of the shared pool -- %d of %d decided contests --" % (winner_more, decided))
    print("  > but not always: in %d the loser drew more and still lost, so" % loser_more)
    print("  > charge is a strong but not sufficient predictor of occupancy.")
else:
    print("  > Partitioning: drawing more charge does NOT predict winning.")
if p3:
    print("  > Abundance: the same carrier tops every pool, so abundance is stable")
    print("  > under repricing even though 2 pairs oscillate.")
else:
    print("  > Abundance: the top carrier MOVES between pools, so abundance is not")
    print("  > stable under repricing.  The frozen prediction is FALSIFIED.")

OUT = {
    "registration_scored": pred["registration"],
    "decided_contests": decided,
    "winner_drew_more": winner_more,
    "loser_drew_more": loser_more,
    "equal_charge": equal,
    "box_11_P1_holds": p1, "box_11_P2_holds": p2,
    "wins_by_pool": wins_by_pool,
    "top_by_pool": tops,
    "box_12_P3_holds": p3, "box_12_P4_holds": p4,
    "verdict": verdict,
    "caveat": pred["caveat_carried"],
}
os.makedirs(os.path.join("microscopes", "results"), exist_ok=True)
with open(os.path.join("microscopes", "results",
                       "STAGE_PARTITION_ABUNDANCE_VERDICT_V1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
print()
print("  receipt: microscopes/results/STAGE_PARTITION_ABUNDANCE_VERDICT_V1.json")
print("=" * 80)

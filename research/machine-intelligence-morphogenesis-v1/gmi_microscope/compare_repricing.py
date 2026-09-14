"""ADJUDICATION: morphology transitions under repricing.  Phase two; frozen at f0c7cd29."""

import json
import os
import itertools

PRED = os.path.join("microscopes", "results", "STAGE_REPRICING_PREDICTION_V1.json")
R10 = os.path.join("microscopes", "results", "STAGE_R10_INVASION_V1.json")

pred = json.load(open(PRED))
r10 = json.load(open(R10))
M = r10["invasion_matrix_by_pool"]
C = r10["carriers"]
POOLS = sorted(M, key=int)

print("=" * 80)
print("ADJUDICATION -- morphology transitions under repricing (box 13)")
print("=" * 80)
print("  pools (ascending): %s" % POOLS)


def winner(pool, resident, invader):
    o = M[pool][resident][invader]
    if o == "RESIDENT_HOLDS":
        return resident
    if o == "INVADER_REPLACES":
        return invader
    return None                      # COEXIST -> neither


oscillating, changing, constant = [], [], 0
seqs = {}
for res, inv in itertools.permutations(C, 2):
    seq = tuple(winner(p, res, inv) for p in POOLS)
    seqs[(res, inv)] = seq
    if len(set(seq)) == 1:
        constant += 1
        continue
    changing.append((res, inv, seq))
    # oscillation: X, Y, X with X != Y and both actual carriers
    if seq[0] == seq[2] and seq[0] is not None and seq[1] is not None and seq[0] != seq[1]:
        oscillating.append((res, inv, seq))

total = len(seqs)
print()
print("-" * 80)
print("1  WINNER SEQUENCES ACROSS THE THREE POOLS")
print("-" * 80)
print("  ordered pairs            : %d" % total)
print("  constant across pools    : %d" % constant)
print("  changed at least once    : %d" % len(changing))
print("  OSCILLATING (X, Y, X)    : %d" % len(oscillating))

p1 = len(oscillating) == 0
p2 = len(changing) > 0
print()
print("  P1 (no oscillation)      : %s" % ("HOLDS" if p1 else "FALSIFIED"))
print("  P2 (some pair changes)   : %s" % ("HOLDS" if p2 else "FALSIFIED"))

assert total > 0, "no pairs examined"
assert p2, (
    "no pair changes winner across the pools, so the repricing moves nothing "
    "and P1's zero carries no information -- this is the control the frozen "
    "prediction named in advance, and it has fired")

if oscillating:
    print()
    print("  oscillating examples:")
    for res, inv, seq in oscillating[:5]:
        print("    %-18s vs %-18s  %s" % (res, inv, " -> ".join(str(x) for x in seq)))

# Direction: among changing pairs, does the resident's advantage move one way?
to_resident = sum(1 for r, i, s in changing if s[0] != r and s[-1] == r)
to_invader = sum(1 for r, i, s in changing if s[0] == r and s[-1] != r)
print()
print("-" * 80)
print("2  DIRECTION OF THE TRANSITIONS")
print("-" * 80)
print("  changed pairs where the RESIDENT gains by the largest pool : %d" % to_resident)
print("  changed pairs where the RESIDENT loses by the largest pool : %d" % to_invader)

verdict = "BOTH_HOLD" if (p1 and p2) else ("P1_FALSIFIED" if not p1 else "P2_FALSIFIED")
print()
print("  VERDICT: %s" % verdict)
print()
if p1:
    print("  > Repricing has a DIRECTION.  No pair reverses and reverses back, so")
    print("  > a transition, once made, is not undone by more budget.  Knowing the")
    print("  > outcome at two pools constrains the third, which is what makes box")
    print("  > 13 predictable in principle rather than merely observed.")
else:
    print("  > Repricing is NON-MONOTONE: %d pairs reverse and reverse back." % len(oscillating))
    print("  > Morphology transitions cannot be extrapolated from endpoints, and")
    print("  > the frozen prediction is recorded as FALSIFIED.")

OUT = {
    "registration_scored": pred["registration"],
    "P1": pred["P1"], "P2": pred["P2"],
    "pools_ascending": POOLS,
    "ordered_pairs": total,
    "constant_pairs": constant,
    "changing_pairs": len(changing),
    "oscillating_pairs": len(oscillating),
    "oscillating_examples": [[r, i, list(s)] for r, i, s in oscillating[:5]],
    "resident_gains_by_largest_pool": to_resident,
    "resident_loses_by_largest_pool": to_invader,
    "P1_holds": p1, "P2_holds": p2,
    "verdict": verdict,
    "caveat": pred["caveat_carried"],
}

os.makedirs(os.path.join("microscopes", "results"), exist_ok=True)
with open(os.path.join("microscopes", "results",
                       "STAGE_REPRICING_VERDICT_V1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
print()
print("  receipt: microscopes/results/STAGE_REPRICING_VERDICT_V1.json")
print("=" * 80)

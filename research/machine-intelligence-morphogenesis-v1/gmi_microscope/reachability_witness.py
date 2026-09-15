"""E: developmental reachability, separated from representability and proved.

Section E's premise is that optimality is not enough -- the theory must say
whether development can FIND the predicted form.  Its first boxes ask for formal
definitions, and a definition is a claim about structure, so each is proved by
exhaustion here rather than stated.

THE SETTING
    Morphologies are the 8-bit organizational descriptors of
    GMI_SPECIES_ALGEBRA_V1 (256 of them).  A DEVELOPMENTAL LAW is a set of
    operators, each flipping a fixed subset of coordinates.  Development starts
    somewhere and applies operators.

    REPRESENTABLE   the descriptor exists in the space          -- always 256
    REACHABLE       connected to the start under the law's operators

THE LAW THIS DERIVES
    Applying an operator adds its flip-vector mod 2, so the reachable set is the
    coset  start + span_GF(2){flip vectors}.  Therefore

        |reachable| = 2^rank   and   target reachable  iff  target XOR start
                                                            lies in the span.

    That gives an exact sufficient-and-necessary condition for reaching a
    morphology, an exact morphology-search burden (8 - rank: the number of
    dimensions the law cannot move), and it is verified by BFS rather than
    assumed -- the algebra predicts, the search confirms.
"""

import json
import os
import itertools

N = 8
SPACE = list(itertools.product((0, 1), repeat=N))
OUT = {}


def flip(d, mask):
    return tuple(b ^ ((mask >> i) & 1) for i, b in enumerate(d))


def reachable(start, masks):
    seen = {start}
    frontier = [start]
    while frontier:
        nxt = []
        for d in frontier:
            for m in masks:
                e = flip(d, m)
                if e not in seen:
                    seen.add(e)
                    nxt.append(e)
        frontier = nxt
    return seen


def rank_gf2(masks):
    basis = []
    for m in masks:
        v = m
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
            basis.sort(reverse=True)
    return len(basis)


def in_span(v, masks):
    basis = []
    for m in masks:
        x = m
        for b in basis:
            x = min(x, x ^ b)
        if x:
            basis.append(x)
            basis.sort(reverse=True)
    x = v
    for b in basis:
        x = min(x, x ^ b)
    return x == 0


# Developmental laws: each a set of flip masks.
LAWS = {
    "single-coordinate":  [1 << i for i in range(N)],
    "paired-coordinates": [(1 << i) | (1 << (i + 1)) for i in range(N - 1)],
    "first-half-only":    [1 << i for i in range(4)],
    "all-or-nothing":     [(1 << N) - 1],
    "paired + one single": [(1 << i) | (1 << (i + 1)) for i in range(N - 1)] + [1],
}

START = tuple([0] * N)

print("=" * 90)
print("E: DEVELOPMENTAL REACHABILITY")
print("=" * 90)
print("  morphologies representable: %d" % len(SPACE))
print()
print("  %-22s %6s %10s %10s %s" % ("law", "rank", "predicted", "reached", "burden"))
rows = {}
for name, masks in LAWS.items():
    r = rank_gf2(masks)
    pred = 2 ** r
    got = len(reachable(START, masks))
    rows[name] = {"rank": r, "predicted": pred, "reached": got,
                  "burden": N - r, "operators": len(masks)}
    print("  %-22s %6d %10d %10d %6d" % (name, r, pred, got, N - r))
    assert pred == got, (
        "the span law predicts %d reachable but BFS found %d for %s -- the "
        "algebra and the search disagree" % (pred, got, name))

OUT["laws"] = rows
print()
print("  > |reachable| = 2^rank on every law, BFS-confirmed.  The algebra is")
print("  > not assumed: it predicts and the exhaustive search checks it.")

# ---------------------------------------------------------------------- 1
print()
print("-" * 90)
print("1  REPRESENTABILITY IS NOT REACHABILITY")
print("-" * 90)
strict = {n: v for n, v in rows.items() if v["reached"] < len(SPACE)}
full = {n: v for n, v in rows.items() if v["reached"] == len(SPACE)}
for n, v in rows.items():
    print("  %-22s reaches %3d of %d%s"
          % (n, v["reached"], len(SPACE), "" if v["reached"] == len(SPACE) else "   <-- strict"))
OUT["strict_laws"] = sorted(strict)
assert strict and full, (
    "every law reaches everything, or none does; either way representability "
    "and reachability are not being separated")
print()
print("  > %d of %d laws reach strictly less than the representable space."
      % (len(strict), len(rows)))
print("  > A morphology can be representable, optimal, and still unreachable.")

# ---------------------------------------------------------------------- 2
print()
print("-" * 90)
print("2  LOCAL BARRIER vs GLOBAL IMPOSSIBILITY")
print("-" * 90)
target = tuple([1] + [0] * (N - 1))          # flip one coordinate
local, glob = [], []
for name, masks in LAWS.items():
    ok = in_span(1, masks)
    (local if ok else glob).append(name)
print("  target: flip coordinate 0 only")
print("    reachable under : %s" % ", ".join(local))
print("    unreachable under: %s" % ", ".join(glob))
OUT["barrier_example"] = {"target": "single coordinate flip",
                          "reachable_under": local, "unreachable_under": glob}
assert local and glob, (
    "the target is reachable under all laws or none; the local/global "
    "distinction needs a target that some laws reach and others cannot")
print()
print("  > Unreachable under one law and reachable under another is a LOCAL")
print("  > barrier -- a property of the developmental law, not of the target.")
print("  > Global impossibility would require unreachability under every law,")
print("  > and no target here has that, which is itself the point: what looks")
print("  > like impossibility is usually the search.")

# ---------------------------------------------------------------------- 3
print()
print("-" * 90)
print("3  ADDING AN OPERATOR RESTORES REACHABILITY")
print("-" * 90)
before = rows["paired-coordinates"]
after = rows["paired + one single"]
print("  paired-coordinates      : rank %d, reaches %d" % (before["rank"], before["reached"]))
print("  + one single-coordinate : rank %d, reaches %d" % (after["rank"], after["reached"]))
OUT["operator_restoration"] = {"before": before, "after": after}
assert after["reached"] > before["reached"], "adding the operator changed nothing"
assert after["reached"] == len(SPACE), "the restored law still does not reach everything"
print()
print("  > One added operator raises the rank by one and takes reachability")
print("  > from half the space to all of it.  Search burden is a property of")
print("  > the OPERATOR SET, and it is repairable by enlarging that set.")

os.makedirs(os.path.join("microscopes", "results"), exist_ok=True)
OUT["law"] = "|reachable| = 2^rank; target reachable iff (target XOR start) in span"
OUT["space"] = len(SPACE)
with open(os.path.join("microscopes", "results",
                       "STAGE_REACHABILITY_V1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
print()
print("=" * 90)
print("all assertions held")
print("=" * 90)
print("  receipt: microscopes/results/STAGE_REACHABILITY_V1.json")

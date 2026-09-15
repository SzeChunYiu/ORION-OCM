"""C box 14: adjudicate the held-out prediction in the L = 3 ecology.

Phase 2.  `predict_heldout_ecology.py` was committed first, with no measuring
code and with nothing at L = 3 computed.  This file enumerates the new ecology
and scores the six registered predictions.

SELF-VALIDATION FIRST.  Before any L = 3 number is reported, the same code is
run at L = 2 and required to reproduce the published box 12 receipt exactly.  A
checker is only trusted on data whose answer is already known; if the L = 2
replay disagrees, every L = 3 number here is worthless and the run aborts.

The task space at L = 3 is 4^8 = 65536, so scores are computed by splitting each
8-tuple into two halves and combining precomputed per-half match counts, which
keeps the inner loop at C speed without numpy.  All arithmetic is integer.
"""

import itertools
import json
import os
from operator import add

S, E = 4, 2
START = 0
ALL = list(itertools.product(range(S), repeat=S * E))


def apply(u, s, e):
    return u[s * E + e]


def is_additive(u):
    return any(all(apply(u, s, e) == (s + g[e]) % S
                   for s in range(S) for e in range(E))
               for g in itertools.product(range(S), repeat=E))


def is_overwrite(u):
    return all(apply(u, 0, e) == apply(u, s, e)
               for s in range(S) for e in range(E))


def is_insertion(u):
    return all((s & ~apply(u, s, e)) == 0 for s in range(S) for e in range(E))


def is_idempotent(u):
    return all(apply(u, apply(u, s, e), e) == apply(u, s, e)
               for s in range(S) for e in range(E))


def is_keep_or_replace(u):
    return any(all(apply(u, s, e) in (s, h[e]) for s in range(S) for e in range(E))
               for h in itertools.product(range(S), repeat=E))


def is_state_only(u):
    return all(apply(u, s, 0) == apply(u, s, e)
               for s in range(S) for e in range(E))


PRED = {
    "additive": is_additive,
    "overwrite": is_overwrite,
    "insertion-monotone": is_insertion,
    "idempotent-on-repeat": is_idempotent,
    "keep-or-replace": is_keep_or_replace,
    "state-only": is_state_only,
}
LAWS = list(PRED)
MEMBERS = {n: [u for u in ALL if f(u)] for n, f in PRED.items()}


def ecology(L):
    """Enumerate the ecology with evidence sequences of length L.

    Returns behaviour sets, uniquely-best counts, and the never-uniquely-best
    set.  Every number is an exact integer count over a complete enumeration.
    """
    seqs = list(itertools.product(range(E), repeat=L))
    n = len(seqs)

    def behaviour(u):
        out = []
        for seq in seqs:
            s = START
            for e in seq:
                s = apply(u, s, e)
            out.append(s)
        return tuple(out)

    beh = {m: sorted({behaviour(u) for u in MEMBERS[m]}) for m in LAWS}

    half = n // 2
    lo_space = list(itertools.product(range(S), repeat=half))
    hi_space = list(itertools.product(range(S), repeat=n - half))
    lo_index = {t: i for i, t in enumerate(lo_space)}
    hi_index = {t: i for i, t in enumerate(hi_space)}

    # score[m][task] for every task, task ordered as (lo, hi)
    scores = {}
    for m in LAWS:
        bl = [b[:half] for b in beh[m]]
        bh = [b[half:] for b in beh[m]]
        # per-half match counts, one row per candidate half-task
        lo_tab = [[sum(1 for x, y in zip(b, t) if x == y) for b in bl]
                  for t in lo_space]
        hi_tab = [[sum(1 for x, y in zip(b, t) if x == y) for b in bh]
                  for t in hi_space]
        col = []
        for a in lo_tab:
            for b2 in hi_tab:
                col.append(max(map(add, a, b2)))
        scores[m] = col

    total = len(lo_space) * len(hi_space)
    assert total == S ** n, "task enumeration lost tasks"

    uniq = {m: 0 for m in LAWS}
    unique_tasks = 0
    for i in range(total):
        best, who, cnt = -1, None, 0
        for m in LAWS:
            v = scores[m][i]
            if v > best:
                best, who, cnt = v, m, 1
            elif v == best:
                cnt += 1
        if cnt == 1:
            uniq[who] += 1
            unique_tasks += 1

    contained = {}
    for a, b in itertools.permutations(LAWS, 2):
        if set(beh[a]) <= set(beh[b]):
            contained.setdefault(a, []).append(b)

    return {
        "L": L,
        "sequences": n,
        "tasks": total,
        "behaviour_counts": {m: len(beh[m]) for m in LAWS},
        "behaviour_contained_in": contained,
        "uniquely_best_on": uniq,
        "never_uniquely_best": sorted(m for m in LAWS if uniq[m] == 0),
        "tasks_with_unique_best": unique_tasks,
        "distinct_behaviours_total": len({b for m in LAWS for b in beh[m]}),
    }


print("=" * 88)
print("C BOX 14: HELD-OUT PREDICTION IN A NEW ECOLOGY (L = 3)")
print("=" * 88)

# ---------------------------------------------------------------- self-check
print("\nSELF-VALIDATION: replay L = 2 and require the published receipt")
l2 = ecology(2)
BOX12 = os.path.join("microscopes", "results", "STAGE_NEGATIVE_ECOLOGY_V1.json")
with open(BOX12) as fh:
    published = json.load(fh)
print("  published uniquely_best_on : %s" % published["uniquely_best_on"])
print("  replayed  uniquely_best_on : %s" % l2["uniquely_best_on"])
assert l2["uniquely_best_on"] == published["uniquely_best_on"], (
    "the L=2 replay does not reproduce box 12's published counts, so this code "
    "is not measuring what box 12 measured and no L=3 number from it can be "
    "trusted")
assert l2["never_uniquely_best"] == sorted(published["never_uniquely_best"]), (
    "the L=2 replay disagrees with box 12 on which laws are never uniquely best")
print("  L = 2 replay MATCHES the published receipt -- proceeding to L = 3")

# ------------------------------------------------------------------- held out
print("\nL = 3 (never enumerated before this commit)")
l3 = ecology(3)
print("  sequences %d   tasks %d" % (l3["sequences"], l3["tasks"]))
for m in LAWS:
    print("    %-22s behaviours %4d   uniquely best on %6d tasks"
          % (m, l3["behaviour_counts"][m], l3["uniquely_best_on"][m]))
print("  never uniquely best : %s" % l3["never_uniquely_best"])
print("  behaviour containment: %s" % l3["behaviour_contained_in"])

f2 = (l2["tasks_with_unique_best"], l2["tasks"])
f3 = (l3["tasks_with_unique_best"], l3["tasks"])
print("  unique-best fraction  L=2 %d/%d   L=3 %d/%d" % (f2 + f3))

order3 = [m for m in sorted(LAWS, key=lambda m: -l3["uniquely_best_on"][m])
          if l3["uniquely_best_on"][m] > 0]

verdict = {
    "H1_state_only_behaviour_contained_in_overwrite":
        "overwrite" in l3["behaviour_contained_in"].get("state-only", []),
    "H2_state_only_uniquely_best_on_zero_tasks":
        l3["uniquely_best_on"]["state-only"] == 0,
    "H3_behaviour_counts":
        l3["behaviour_counts"]["state-only"] == 4
        and l3["behaviour_counts"]["overwrite"] == 16,
    "H4_never_uniquely_best_set":
        l3["never_uniquely_best"] == ["keep-or-replace", "overwrite", "state-only"],
    "H5_order_preserved":
        order3 == ["idempotent-on-repeat", "insertion-monotone", "additive"],
    "H6_unique_fraction_strictly_smaller_than_l2":
        f3[0] * f2[1] < f2[0] * f3[1],
}

controls = {
    "C1_ecology_is_actually_new":
        l3["behaviour_counts"] != l2["behaviour_counts"],
    "C2_unique_and_nonunique_tasks_both_occur":
        0 < l3["tasks_with_unique_best"] < l3["tasks"],
    "C3_ecology_is_not_saturated":
        l3["distinct_behaviours_total"] < l3["tasks"],
}

print("\n" + "=" * 88)
print("ADJUDICATION against the held-out predictions")
print("=" * 88)
for k, v in verdict.items():
    print("  %-52s %-5s  %s" % (k, v, "HOLDS" if v else "FALSIFIED"))
print("\nnon-vacuity controls")
for k, v in controls.items():
    print("  %-52s %s" % (k, v))
    assert v, "control %s failed: the comparison would be vacuous" % k

OUT = {
    "schema": "GMI_HELDOUT_ECOLOGY_V1",
    "prediction_file": "gmi_microscope/predict_heldout_ecology.py",
    "self_validation_l2_matches_box12": True,
    "l2_replay": l2,
    "l3": l3,
    "l3_order_of_winners": order3,
    "verdict": verdict,
    "controls": controls,
}
os.makedirs(os.path.join("microscopes", "results"), exist_ok=True)
with open(os.path.join("microscopes", "results",
                       "STAGE_HELDOUT_ECOLOGY_V1.json"), "w") as fh:
    json.dump(OUT, fh, indent=2, sort_keys=True)
print("\n  receipt: microscopes/results/STAGE_HELDOUT_ECOLOGY_V1.json")

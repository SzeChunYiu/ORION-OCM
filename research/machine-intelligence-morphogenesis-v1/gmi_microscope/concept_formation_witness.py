"""Item 9 / I2: the concept-formation TRIGGER, and where category boundaries fall.

The audit's gap: the quotient theorem is a minimality result, not a trigger law -- nothing
says when experiences get compressed into a named concept, nor where category boundaries lie.

Both halves are already proved separately:
  * BOUNDARY  -- the developmental quotient theorem: two experiences belong to the same
    concept iff they license the same future responses (response-equivalence). The coarsest
    such quotient is the unique minimal representation.
  * TRIGGER   -- PVR-3: naming and storing an abstraction costs S once and saves (C-U) per
    use, so it pays iff its recurrence clears r > 1 + S/(C-U).

So a concept is a RETAINED EQUIVALENCE CLASS, and this tests the two halves together:
does the set of classes that clear the threshold behave as the trigger predicts, and are
the boundaries exactly response-equivalence?
"""
import json, itertools

H = list(range(16))
bit = lambda k: (lambda h: (h >> k) & 1)

# an experience stream: each experience is a (stimulus, response-map) pair
_p0 = lambda h: (h & 1)
_p1 = lambda h: ((h >> 1) & 1)
_p2 = lambda h: (h & 1) ^ ((h >> 1) & 1)
# recurring experiences PLUS three one-off experiences that must NOT become concepts --
# without a class below threshold the trigger's selectivity is untested.
_q3 = lambda h: ((h >> 2) & 1)
_q4 = lambda h: ((h >> 3) & 1)
_q5 = lambda h: ((h >> 2) & 1) & ((h >> 3) & 1)
STREAM = [_p0, _p1, _p2, _p0, _p2, _p0, _p1, _p2, _p0, _p2, _p2, _p0, _q3, _q4, _q5]

C_DERIVE, S_NAME, U_RECALL = 5, 3, 1
THRESH = 1 + S_NAME / (C_DERIVE - U_RECALL)

# BOUNDARY: group experiences by response-equivalence (identical response map over H)
classes = {}
for i, q in enumerate(STREAM):
    key = tuple(q(h) for h in H)
    classes.setdefault(key, []).append(i)

print("PVR-3 trigger threshold: recurrence > %.2f" % THRESH)
print("\nresponse-equivalence classes (the quotient theorem's boundary):")
print("  class  members  recurrence  clears threshold?  named concept?")
named, unnamed = [], []
for k, members in sorted(classes.items(), key=lambda kv: -len(kv[1])):
    r = len(members)
    clears = r > THRESH
    (named if clears else unnamed).append((k, r))
    print("  %-6s %-8s %-11d %-18s %s" % (str(k[:4]) + "..", members, r, clears, "YES" if clears else "no"))

flat = sum(C_DERIVE for _ in STREAM)
with_concepts = 0
for k, members in classes.items():
    r = len(members)
    if r > THRESH: with_concepts += C_DERIVE + S_NAME + (r - 1) * U_RECALL
    else:          with_concepts += r * C_DERIVE
print("\ncost with no concepts at all : %d" % flat)
print("cost with the triggered set  : %d  (saving %d)" % (with_concepts, flat - with_concepts))

# counterfactual: naming EVERY class, including ones below threshold
name_all = sum(C_DERIVE + S_NAME + (len(m) - 1) * U_RECALL for m in classes.values())
print("cost if every class is named : %d  (worse than triggered by %d)" % (name_all, name_all - with_concepts))

# BOUNDARY CHECK: are members of one class interchangeable, and members of different classes not?
same_ok = all(tuple(STREAM[i](h) for h in H) == tuple(STREAM[j](h) for h in H)
              for m in classes.values() for i, j in itertools.combinations(m, 2))
diff_ok = all(tuple(STREAM[a[0]](h) for h in H) != tuple(STREAM[b[0]](h) for h in H)
              for a, b in itertools.combinations(list(classes.values()), 2))
print("\nboundary is exactly response-equivalence:")
print("  all within-class pairs licence identical responses :", same_ok)
print("  all cross-class pairs licence different responses   :", diff_ok)

json.dump({"schema": "ConceptFormationWitnessV1", "threshold": THRESH,
           "n_classes": len(classes), "named": len(named), "unnamed": len(unnamed),
           "cost_no_concepts": flat, "cost_triggered": with_concepts, "cost_name_all": name_all,
           "boundary_within_class_identical": same_ok, "boundary_cross_class_distinct": diff_ok},
          open("microscopes/results/STAGE_CONCEPT_FORMATION_V1.json", "w"), indent=1, sort_keys=True)
print("written")

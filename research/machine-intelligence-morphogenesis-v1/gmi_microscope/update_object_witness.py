"""C: one update object, and learning paradigms as structural restrictions of it.

Section C's first box asks for a formal common update object across learning
paradigms; the nine that follow ask for each paradigm as a specialization.  The
first is the keystone -- without it, "specialization" has nothing to specialize.

THE OBJECT
    An update is a total map  U : (state, evidence) -> state.  Nothing else.
    Over a finite state set S and evidence set E there are |S|^(|S|*|E|) of
    them, and with |S| = 4, |E| = 2 that is 65536 -- small enough to enumerate
    every single one, which is what makes the claims below checkable rather
    than argued.

PARADIGMS AS PREDICATES
    Each paradigm is a structural restriction on U, stated without reference to
    any implementation:

    additive (gradient-like)   U(s,e) = s + g(e)          -- evidence contributes
                                                             an increment that
                                                             does not depend on s
    overwrite (point estimate) U(s,e) = h(e)              -- the state is
                                                             replaced, not revised
    insertion-monotone         U(s,e) >= s as subsets     -- state only grows
      (exemplar/library)
    idempotent-on-repeat       U(U(s,e),e) = U(s,e)       -- consolidation: the
      (rule induction)                                      same evidence twice
                                                             changes nothing more
    keep-or-replace            U(s,e) in {s, h(e)}        -- selection between
      (evolutionary)                                         incumbent and challenger
    state-only (drift)         U(s,e) = k(s)              -- ignores evidence

WHAT IS PROVED
    Every predicate is non-vacuous and strictly smaller than the whole space;
    the predicates are pairwise distinct; and the containment pattern between
    them is computed rather than asserted.  A paradigm that turned out to be
    the whole space, or identical to another, would not be a specialization.

WHAT IS NOT CLAIMED
    That these predicates ARE gradient descent, Bayes, or DreamCoder.  They are
    the structural signatures those families share, exhibited on a space small
    enough to enumerate.  Deriving each named algorithm is section C's later
    boxes and is not done here.
"""

import json
import os
import itertools

S = 4                      # states 0..3, read also as subsets of a 2-element set
E = 2                      # evidence values
CELLS = [(s, e) for s in range(S) for e in range(E)]

OUT = {}
print("=" * 88)
print("C: ONE UPDATE OBJECT, PARADIGMS AS RESTRICTIONS")
print("=" * 88)
print("  states %d, evidence %d -> %d total update maps" % (S, E, S ** (S * E)))


def apply(u, s, e):
    return u[s * E + e]


def is_additive(u):
    for g0 in range(S):
        for g1 in range(S):
            g = (g0, g1)
            if all(apply(u, s, e) == (s + g[e]) % S for s, e in CELLS):
                return True
    return False


def is_overwrite(u):
    return all(apply(u, 0, e) == apply(u, s, e) for s in range(S) for e in range(E))


def is_insertion_monotone(u):
    # state as a 2-bit subset; growth means no bit is ever cleared
    return all((s & ~apply(u, s, e)) == 0 for s, e in CELLS)


def is_idempotent_repeat(u):
    return all(apply(u, apply(u, s, e), e) == apply(u, s, e) for s, e in CELLS)


def is_keep_or_replace(u):
    for h0 in range(S):
        for h1 in range(S):
            h = (h0, h1)
            if all(apply(u, s, e) in (s, h[e]) for s, e in CELLS):
                return True
    return False


def is_state_only(u):
    return all(apply(u, s, 0) == apply(u, s, e) for s in range(S) for e in range(E))


PRED = {
    "additive (gradient-like)": is_additive,
    "overwrite (point estimate)": is_overwrite,
    "insertion-monotone (exemplar/library)": is_insertion_monotone,
    "idempotent-on-repeat (rule induction)": is_idempotent_repeat,
    "keep-or-replace (evolutionary)": is_keep_or_replace,
    "state-only (drift, evidence ignored)": is_state_only,
}

ALL = list(itertools.product(range(S), repeat=S * E))
sets = {name: {i for i, u in enumerate(ALL) if f(u)} for name, f in PRED.items()}

print()
print("-" * 88)
print("1  EACH PARADIGM IS A NON-VACUOUS, STRICT RESTRICTION")
print("-" * 88)
counts = {}
for name, ids in sets.items():
    counts[name] = len(ids)
    print("  %-40s %6d of %d  (%.2f%%)"
          % (name, len(ids), len(ALL), 100.0 * len(ids) / len(ALL)))
    assert ids, "%s is empty -- not a specialization, just an impossible rule" % name
    assert len(ids) < len(ALL), "%s is the whole space -- it restricts nothing" % name
OUT["total_updates"] = len(ALL)
OUT["counts"] = counts

print()
print("-" * 88)
print("2  THE PARADIGMS ARE PAIRWISE DISTINCT")
print("-" * 88)
names = list(sets)
identical = [(a, b) for a, b in itertools.combinations(names, 2) if sets[a] == sets[b]]
assert not identical, "two paradigms are the same set of updates: %s" % identical
print("  no two predicates pick the same set of updates (%d pairs checked)"
      % (len(names) * (len(names) - 1) // 2))

print()
print("-" * 88)
print("3  CONTAINMENT AND OVERLAP, COMPUTED NOT ASSERTED")
print("-" * 88)
contain, disjoint, overlap = [], [], []
for a, b in itertools.permutations(names, 2):
    if sets[a] < sets[b]:
        contain.append((a, b))
for a, b in itertools.combinations(names, 2):
    inter = sets[a] & sets[b]
    if not inter:
        disjoint.append((a, b))
    elif not (sets[a] <= sets[b] or sets[b] <= sets[a]):
        overlap.append((a, b, len(inter)))
for a, b in contain:
    print("  %-40s  STRICTLY INSIDE  %s" % (a, b))
for a, b in disjoint:
    print("  %-40s  DISJOINT FROM    %s" % (a, b))
print("  partially overlapping pairs: %d" % len(overlap))
OUT["strict_containments"] = [[a, b] for a, b in contain]
OUT["disjoint_pairs"] = [[a, b] for a, b in disjoint]
OUT["overlapping_pairs"] = len(overlap)

assert overlap, (
    "no two paradigms share an update, so the space is a set of unrelated "
    "islands and 'one common object' explains nothing about their relation")
assert disjoint or contain, (
    "every pair merely overlaps, with no containment or disjointness anywhere; "
    "the structure would then carry no information about which paradigm is a "
    "special case of which")

union = set().union(*sets.values())
print()
print("  updates matching at least one paradigm : %d of %d (%.1f%%)"
      % (len(union), len(ALL), 100.0 * len(union) / len(ALL)))
OUT["covered_by_some_paradigm"] = len(union)
assert len(union) < len(ALL), (
    "every update belongs to some named paradigm, which would mean the six "
    "names exhaust learning -- not credible on a space this size")
print("  > %d updates belong to NO named paradigm.  The object is strictly"
      % (len(ALL) - len(union)))
print("  > larger than the union of the paradigms, which is what makes room")
print("  > for a learning law the corpus has not named.")

os.makedirs(os.path.join("microscopes", "results"), exist_ok=True)
with open(os.path.join("microscopes", "results",
                       "STAGE_UPDATE_OBJECT_V1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
print()
print("=" * 88)
print("all assertions held")
print("=" * 88)
print("  receipt: microscopes/results/STAGE_UPDATE_OBJECT_V1.json")

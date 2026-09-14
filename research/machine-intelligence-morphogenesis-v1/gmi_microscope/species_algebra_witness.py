"""G: machine-species theory -- the definitions, proved rather than asserted.

Section G opens with six "define X" boxes.  A prose definition closes none of
them: the question is whether the definition has the properties the word
implies.  "Equivalence relation" is a claim (reflexive, symmetric, transitive).
"Distance" is a claim (identity of indiscernibles, symmetry, triangle
inequality).  Both are checkable by exhaustion on a finite descriptor space, and
both are checked here.

The species descriptor is the one section G proposes, split into the part that
is organizational and the part that is not:

    ORGANIZATIONAL   state carrier, native operators, control law, update law,
                     memory organization, communication, verification,
                     development law
    NON-ORGANIZATIONAL   resource profile

That split IS the theory.  It is what makes species identity survive a compiler
or substrate change, because a substrate change moves the resource profile and
nothing else.  If the split were wrong, substrate invariance would fail, and the
witness checks it rather than assuming it.

Everything below is exact and exhaustive over the stated space.  No sampling.
"""

import json
import itertools
import os

NORG = 8                      # organizational components
VALS = (0, 1)                 # values per organizational component
RESOURCES = (0, 1, 2)         # resource profiles = substrate variation

ORG = list(itertools.product(VALS, repeat=NORG))
FULL = [(o, r) for o in ORG for r in RESOURCES]

OUT = {}
print("=" * 78)
print("G: SPECIES ALGEBRA, PROVED BY EXHAUSTION")
print("=" * 78)
print("  organizational descriptors : %d" % len(ORG))
print("  resource profiles          : %d" % len(RESOURCES))
print("  full descriptors           : %d" % len(FULL))


# --------------------------------------------------------------------------
# 1  SPECIES EQUIVALENCE -- and the proof that it is one
# --------------------------------------------------------------------------
def species(d):
    """The species of a descriptor: its organizational part."""
    return d[0]


def conspecific(a, b):
    return species(a) == species(b)


print()
print("-" * 78)
print("1  SPECIES EQUIVALENCE: reflexive, symmetric, transitive -- checked")
print("-" * 78)
refl = all(conspecific(x, x) for x in FULL)
sym = all(conspecific(x, y) == conspecific(y, x) for x in FULL for y in FULL)
trans = True
for x in FULL:
    for y in FULL:
        if not conspecific(x, y):
            continue
        for z in FULL:
            if conspecific(y, z) and not conspecific(x, z):
                trans = False
                break
print("  reflexive  : %s   (%d descriptors)" % (refl, len(FULL)))
print("  symmetric  : %s   (%d ordered pairs)" % (sym, len(FULL) ** 2))
print("  transitive : %s" % trans)
assert refl and sym and trans, "the proposed relation is not an equivalence relation"
classes = {}
for d in FULL:
    classes.setdefault(species(d), []).append(d)
OUT["equivalence"] = {"descriptors": len(FULL), "species": len(classes),
                      "reflexive": refl, "symmetric": sym, "transitive": trans}
print("  > %d descriptors partition into %d species." % (len(FULL), len(classes)))
assert 1 < len(classes) < len(FULL), (
    "the partition is trivial -- either one species or all singletons, and "
    "either way the relation carries no information")


# --------------------------------------------------------------------------
# 2  WITHIN-SPECIES VARIATION
# --------------------------------------------------------------------------
print()
print("-" * 78)
print("2  WITHIN-SPECIES VARIATION: what varies without changing the species")
print("-" * 78)
sizes = {len(v) for v in classes.values()}
varies = set()
for members in classes.values():
    for a in members:
        for b in members:
            if a != b:
                varies.add("resource" if a[1] != b[1] else "organizational")
OUT["within_species"] = {"class_size": sorted(sizes),
                         "dimensions_that_vary": sorted(varies)}
print("  every species has exactly %s members" % sorted(sizes))
print("  the only dimension that varies within a species: %s" % sorted(varies))
assert sizes == {len(RESOURCES)}, "species classes are not uniform in size"
assert varies == {"resource"}, (
    "an organizational component varies within a species, which contradicts the "
    "definition of the equivalence")


# --------------------------------------------------------------------------
# 3  MORPHOLOGICAL DISTANCE -- and the proof that it is a metric
# --------------------------------------------------------------------------
def dist(a, b):
    """Between-species morphological distance: disagreeing organizational parts."""
    return sum(1 for x, y in zip(species(a), species(b)) if x != y)


print()
print("-" * 78)
print("3  MORPHOLOGICAL DISTANCE: a metric on species, checked exhaustively")
print("-" * 78)
reps = [(o, RESOURCES[0]) for o in ORG]
d_sym = all(dist(a, b) == dist(b, a) for a in reps for b in reps)
d_zero = all((dist(a, b) == 0) == conspecific(a, b) for a in reps for b in reps)
tri = True
worst = None
for a in reps:
    for b in reps:
        ab = dist(a, b)
        for c in reps:
            if ab > dist(a, c) + dist(c, b):
                tri = False
                worst = (a, b, c)
                break
print("  symmetry                        : %s" % d_sym)
print("  d(x,y)=0 exactly when conspecific: %s" % d_zero)
print("  triangle inequality             : %s   (%d triples)" % (tri, len(reps) ** 3))
assert d_sym and d_zero and tri, "the proposed distance is not a metric: %s" % (worst,)
spread = sorted({dist(a, b) for a in reps for b in reps})
OUT["distance"] = {"symmetric": d_sym, "zero_iff_conspecific": d_zero,
                   "triangle": tri, "triples_checked": len(reps) ** 3,
                   "values": spread}
print("  > distance takes the values %s" % spread)
assert len(spread) > 2, (
    "distance takes fewer than three values, so it is a near-constant and "
    "cannot order morphologies")


# --------------------------------------------------------------------------
# 4  IDENTITY UNDER COMPILER / SUBSTRATE CHANGE
# --------------------------------------------------------------------------
print()
print("-" * 78)
print("4  IDENTITY UNDER SUBSTRATE CHANGE")
print("-" * 78)
moved = 0
for d in FULL:
    for r in RESOURCES:
        if not conspecific(d, (d[0], r)):
            moved += 1
OUT["substrate_invariance"] = {"substrate_changes_tried": len(FULL) * len(RESOURCES),
                               "species_changes": moved}
print("  substrate changes tried : %d" % (len(FULL) * len(RESOURCES)))
print("  that changed the species: %d" % moved)
assert moved == 0, "a substrate change moved a machine to another species"
print("  > Species identity is invariant under substrate change, BY CONSTRUCTION")
print("  > and verified.  This is the content of the organizational split: if the")
print("  > resource profile were organizational, recompiling would speciate.")


# --------------------------------------------------------------------------
# 5  SPECIATION THRESHOLD
# --------------------------------------------------------------------------
print()
print("-" * 78)
print("5  SPECIATION THRESHOLD under developmental divergence")
print("-" * 78)
below = sorted({dist(a, b) for a in reps for b in reps if conspecific(a, b)})
above = sorted({dist(a, b) for a in reps for b in reps if not conspecific(a, b)})
OUT["speciation_threshold"] = {"distances_within": below, "distances_between": above,
                               "threshold": min(above) if above else None}
print("  distances within a species  : %s" % below)
print("  distances between species   : %s" % above)
print("  > The threshold is exactly 1 and it is SHARP: there is no distance")
print("  > attained both within and between species, so 'how far must development")
print("  > diverge before it is a new species' has an exact answer rather than a")
print("  > tuned cutoff.")
assert set(below).isdisjoint(above), (
    "some distance occurs both within and between species, so no sharp threshold "
    "exists and the criterion would need a tuned cutoff")
assert min(above) == 1


# --------------------------------------------------------------------------
# 6  HYBRIDIZATION vs A GENUINELY NEW SPECIES
# --------------------------------------------------------------------------
print()
print("-" * 78)
print("6  HYBRIDIZATION: when is a composition a NEW species?")
print("-" * 78)
new = variant = 0
reachable = set()
for a in ORG:
    for b in ORG:
        if a == b:
            continue
        for mask in range(1 << NORG):
            child = tuple(a[i] if (mask >> i) & 1 else b[i] for i in range(NORG))
            reachable.add(child)
            if child == a or child == b:
                variant += 1
            else:
                new += 1
OUT["hybridization"] = {"crossovers": new + variant, "new_species": new,
                        "parental_variants": variant,
                        "distinct_children": len(reachable),
                        "organizational_space": len(ORG)}
print("  crossovers enumerated : %d" % (new + variant))
print("  produced a NEW species: %d" % new)
print("  reproduced a parent   : %d" % variant)
print("  distinct children     : %d of %d organizational descriptors"
      % (len(reachable), len(ORG)))
assert new > 0 and variant > 0, (
    "hybridization either always or never produces a new species, so the "
    "criterion does not discriminate and closes nothing")
# What a FIXED pair of parents can reach.  Pooling over all pairs reaches
# everything and says nothing; the constraint is per-pair.
per_pair = {}
for a in ORG:
    for b in ORG:
        if a == b:
            continue
        k = sum(1 for x, y in zip(a, b) if x != y)
        kids = {tuple(a[i] if (mask >> i) & 1 else b[i] for i in range(NORG))
                for mask in range(1 << NORG)}
        per_pair.setdefault(k, set()).add(len(kids))
OUT["hybridization"]["children_per_pair_by_distance"] = {
    str(k): sorted(v) for k, v in sorted(per_pair.items())}
subcube_law = all(v == {2 ** k} for k, v in per_pair.items())
OUT["hybridization"]["subcube_law_holds"] = subcube_law
assert subcube_law, (
    "parents at distance k do not reach exactly 2^k children, so hybrids are "
    "not confined to the subcube spanned by the parents' disagreements")
print("  > A composition is a NEW species exactly when its organizational")
print("  > descriptor equals neither parent's.  Both outcomes occur, so the")
print("  > criterion separates cases rather than labelling all of them alike.")
print()
print("  CONFINEMENT LAW, which is the real limit on hybridization:")
print("  parents at morphological distance k reach EXACTLY 2^k children --")
print("  checked for every k: %s"
      % {k: sorted(v) for k, v in sorted(per_pair.items())})
print("  > So a hybrid never leaves the subcube spanned by where its parents")
print("  > disagree.  Composition RECOMBINES; it cannot introduce a component")
print("  > value that neither parent had.  Pooling over all parent pairs reaches")
print("  > all %d descriptors, which is why the constraint has to be stated" % len(reachable))
print("  > per pair -- the pooled number says nothing.")

os.makedirs(os.path.join("microscopes", "results"), exist_ok=True)
with open(os.path.join("microscopes", "results",
                       "STAGE_SPECIES_ALGEBRA_V1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
print()
print("=" * 78)
print("all assertions held")
print("=" * 78)
print("  receipt: microscopes/results/STAGE_SPECIES_ALGEBRA_V1.json")

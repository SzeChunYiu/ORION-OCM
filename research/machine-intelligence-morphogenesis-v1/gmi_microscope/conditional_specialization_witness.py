"""B10: conditional specialization, derived, and priced against one shared rule.

PVR-3 says retained structure earns its keep past a break-even fixed by what it
replaces. CSR-1 says a machine holds one state per distinction it must still
make. A map from context to a small label set is retained structure, and it is
licensed only by distinctions that survive. So conditional specialization is not
a separate idea either -- it is the SAME break-even, read over a context set.

Derived here:

  1  specialization pressure from heterogeneous sub-ecologies
  2  the cost of the label map, net of what one shared rule pays anyway
  3  the reuse / amortization law: what conditioning actually saves
  4  load and communication: PVR-3 per rule, with load as the recurrence count
  5  the crossover between one shared rule and several conditioned ones
  6  neutral recovery, with no family name in the candidate space

Everything is exhaustive enumeration over a finite world, in exact integers and
exact rationals. No sampling. No floating point in any reported number.
"""

from fractions import Fraction as F
from functools import lru_cache
import json

OUT = {}

B = 2                       # context-tag bits
K = 1 << B                  # contexts
N = 3                       # payload bits


# ---------------------------------------------------------------------------
# The only cost primitive: minimal branching structure.
#
# A machine is charged for what it HOLDS -- every node of the smallest branching
# tree computing it -- and for what it TRAVERSES on one query, the longest
# root-to-leaf path. A constant holds one node and traverses none. Nothing else
# is charged. Both numbers are exact, found by dynamic programming over every
# subcube: no tree shape is assumed and every split is tried.
# ---------------------------------------------------------------------------
@lru_cache(maxsize=None)
def _best(vals, d, assign):
    idxs = [i for i in range(1 << d)
            if all(a is None or ((i >> k) & 1) == a
                   for k, a in enumerate(assign))]
    if len(set(vals[i] for i in idxs)) == 1:
        return (1, 0, -1)
    best = None
    for k in range(d):
        if assign[k] is not None:
            continue
        a0 = assign[:k] + (0,) + assign[k + 1:]
        a1 = assign[:k] + (1,) + assign[k + 1:]
        s0, d0, _ = _best(vals, d, a0)
        s1, d1, _ = _best(vals, d, a1)
        cand = (1 + s0 + s1, 1 + max(d0, d1), k)
        if best is None or cand[:2] < best[:2]:
            best = cand
    return best


def held(vals, d):
    return _best(tuple(vals), d, (None,) * d)[0]


def traversed(vals, d):
    return _best(tuple(vals), d, (None,) * d)[1]


def first_test(vals, d):
    return _best(tuple(vals), d, (None,) * d)[2]


def _path_sum(vals, d, assign):
    """Total tests paid, summed over every input in this subcube, by the very
    tree the search above selected. Exact integer."""
    _s, _dep, k = _best(vals, d, assign)
    if k < 0:
        return 0
    a0 = assign[:k] + (0,) + assign[k + 1:]
    a1 = assign[:k] + (1,) + assign[k + 1:]
    n_free = sum(1 for a in assign if a is None)
    return (1 << n_free) + _path_sum(vals, d, a0) + _path_sum(vals, d, a1)


def expected_traversed(vals, d):
    """Mean tests per query, uniform over inputs. Exact rational."""
    vals = tuple(vals)
    return F(_path_sum(vals, d, (None,) * d), 1 << d)


def internal_only(total_nodes):
    """The same tree charged for its tests alone. A binary tree with I tests has
    I+1 leaves, so total = 2I+1 and I = (total-1)/2. Minimising one minimises the
    other, so this is the SAME tree re-priced -- not a second search."""
    return (total_nodes - 1) // 2


# ---------------------------------------------------------------------------
# the finite world
# ---------------------------------------------------------------------------
def tab(fn):
    return tuple(fn(tuple((i >> k) & 1 for k in range(N))) for i in range(1 << N))


# Obligations over a 3-bit payload, named for what they do, so that the
# candidate space below contains no family name to be recovered by reading.
MASTER = [
    ("alternating",       tab(lambda x: (x[0] + x[1] + x[2]) % 2)),
    ("weight-threshold",  tab(lambda x: 1 if x[0] + x[1] + x[2] >= 2 else 0)),
    ("all-on",            tab(lambda x: 1 if x[0] and x[1] and x[2] else 0)),
    ("one-coordinate",    tab(lambda x: x[0])),
    ("two-on",            tab(lambda x: 1 if x[0] and x[1] else 0)),
    ("other-coordinate",  tab(lambda x: x[1])),
    ("two-on-other",      tab(lambda x: 1 if x[1] and x[2] else 0)),
    ("one-coordinate-up", tab(lambda x: 1 - x[0])),
    ("other-coord-up",    tab(lambda x: 1 - x[1])),
]

# A first version of this witness used ONE catalogue and varied only the
# ARRANGEMENT of obligations across the context tags. It found a clean
# biconditional, which turned out to be a property of that catalogue: its
# obligations were expensive enough that duplicating one always outweighed
# holding a label map. The catalogue is therefore swept as well. What survives
# the sweep is stated as the law; what does not is printed as the counterexample
# that killed it.
CATALOGUES = [
    ("dear",     (0, 1, 2, 3)),
    ("cheap",    (3, 4, 5, 6)),
    ("cheapest", (3, 7, 5, 8)),
    ("mixed",    (3, 0, 4, 1)),
]


def dense_decomposition(lab, tabs):
    """Take the undivided rule's OWN minimal tree apart and measure it, rather
    than narrating what it must contain.

    Walking down from the root, a node is REACH while more than one obligation
    is still possible below it. The moment only one is, the whole subtree below
    is that obligation's BODY, implemented in that particular place. A constant
    subtree met while several obligations are still live is a leaf they SHARE --
    one leaf answering several obligations at once, which no split machine can
    have, because each of its blocks implements its rule alone.
    """
    jt = joint_table(lab, tabs)
    D = B + N
    bodies = []
    reach = [0]

    def walk(assign):
        ctx = [c for c in range(K)
               if all(assign[k] is None or ((c >> k) & 1) == assign[k]
                      for k in range(B))]
        cls = set(lab[c] for c in ctx)
        s, _dep, k = _best(jt, D, assign)
        if len(cls) == 1:
            bodies.append((cls.pop(), s))
            return
        if k < 0:
            bodies.append((None, s))
            return
        reach[0] += 1
        walk(assign[:k] + (0,) + assign[k + 1:])
        walk(assign[:k] + (1,) + assign[k + 1:])

    walk((None,) * D)
    placed = {}
    for j, _s in bodies:
        placed[j] = placed.get(j, 0) + 1
    return {"reach": reach[0],
            "body_nodes": sum(s for _j, s in bodies),
            "n_bodies": len(bodies),
            "places_per_obligation": dict((a, b) for a, b in placed.items()
                                          if a is not None),
            "shared_leaves": placed.get(None, 0),
            "total": reach[0] + sum(s for _j, s in bodies)}


def set_partitions(items):
    items = list(items)
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for p in set_partitions(rest):
        for i in range(len(p)):
            yield p[:i] + [[first] + p[i]] + p[i + 1:]
        yield [[first]] + p


def canon(part):
    return [sorted(b) for b in sorted(part, key=min)]


PARTS = [canon(p) for p in set_partitions(range(K))]
PARTS.sort(key=lambda p: (len(p), p))
BELL = len(PARTS)


def labels_of(part):
    lab = [0] * K
    for j, blk in enumerate(part):
        for c in blk:
            lab[c] = j
    return tuple(lab)


def joint_table(lab, tabs):
    """One rule over the whole input: tag bits 0..B-1, payload bits B..B+N-1."""
    D = B + N
    out = []
    for i in range(1 << D):
        c = i & ((1 << B) - 1)
        x = i >> B
        out.append(tabs[lab[c]][x])
    return tuple(out)


# ---------------------------------------------------------------------------
# THE CANDIDATE SPACE
#
# A candidate is described only by two things: how it splits the context set
# into blocks, and which rule it holds for each block. A candidate with one
# block holds a single rule for everything. No candidate is named, none is
# privileged, and the one-block candidate is a member like any other. The
# alternative shape -- hold ONE rule over the tag and payload together -- is
# priced by the same primitive, at the best tree that exists for it, so that it
# is never handicapped.
# ---------------------------------------------------------------------------
def price_split(part, world_lab, world_tabs):
    """None if this split cannot answer the obligation."""
    lab = labels_of(part)
    tabs = []
    for blk in part:
        t = set(world_tabs[world_lab[c]] for c in blk)
        if len(t) != 1:
            return None
        tabs.append(t.pop())
    lab_held = held(lab, B)
    s = lab_held + sum(held(t, N) for t in tabs)
    u = traversed(lab, B) + max(traversed(t, N) for t in tabs)
    return {"blocks": len(part), "held": s, "traversed": u,
            "label_held": lab_held,
            "rule_mass": sum(held(t, N) for t in tabs)}


def price_single(world_lab, world_tabs):
    jt = joint_table(world_lab, world_tabs)
    D = B + N
    root = first_test(jt, D)
    return {"held": held(jt, D), "traversed": traversed(jt, D),
            "root_test": ("tag bit %d" % root) if root < B
            else ("payload bit %d" % (root - B))}


# ---------------------------------------------------------------------------
# the census: every arrangement of every catalogue over this context set
# ---------------------------------------------------------------------------
WORLDS = []
for cname, cidx in CATALOGUES:
    names = [MASTER[i][0] for i in cidx]
    tabs_all = [MASTER[i][1] for i in cidx]
    for part in PARTS:
        lab = labels_of(part)
        m = len(part)
        tabs = tabs_all[:m]
        single = price_single(lab, tabs)
        own = price_split(part, lab, tabs)
        dec = dense_decomposition(lab, tabs)
        map_held = own["label_held"]
        split_body = own["rule_mass"]
        net = single["held"] - own["held"]
        term_a = map_held - dec["reach"]
        term_b = dec["body_nodes"] - split_body
        assert dec["total"] == single["held"], (
            "the decomposition of the shared rule's tree does not add back up "
            "to the tree: %d + %d != %d"
            % (dec["reach"], dec["body_nodes"], single["held"]))
        assert net == term_b - term_a, (
            "the measured decomposition does not reproduce the cost difference")
        net_int = internal_only(single["held"]) - (
            internal_only(map_held) + sum(internal_only(held(t, N)) for t in tabs))
        WORLDS.append({
            "catalogue": cname, "rule_costs": [held(t, N) for t in tabs],
            "partition": part, "labels": list(lab), "m": m, "rules": names[:m],
            "label_held": map_held, "tag_collapsible": (map_held == 2 * m - 1),
            "single_held": single["held"], "single_traversed": single["traversed"],
            "single_root": single["root_test"],
            "split_held": own["held"], "split_traversed": own["traversed"],
            "reach": dec["reach"], "dense_body": dec["body_nodes"],
            "split_body": split_body, "n_bodies": dec["n_bodies"],
            "shared_leaves": dec["shared_leaves"],
            "max_places": max(dec["places_per_obligation"].values())
            if dec["places_per_obligation"] else 0,
            "term_a_map_over_reach": term_a,
            "term_b_body_over_bodies": term_b,
            "net_leaves": net, "net_internal_only": net_int,
            "pays": net > 0,
        })

assert len(CATALOGUES) > 1, (
    "only one catalogue is swept, so arrangement and obligation price are "
    "confounded and any law found is a property of that catalogue -- this is "
    "the exact mistake the first version of this witness made")
assert len(set(tuple(held(MASTER[i][1], N) for i in ix)
               for _c, ix in CATALOGUES)) > 1, (
    "the catalogues all price the same, so sweeping them varies nothing")
DEAR = [w for w in WORLDS if w["catalogue"] == "dear"]
CHEAP = [w for w in WORLDS if w["catalogue"] == "cheap"]
assert DEAR and CHEAP, "the two catalogues printed in full must both exist"


# ---------------------------------------------------------------------------
print("=" * 78)
print("1  SPECIALIZATION PRESSURE IS A COUNT OF SURVIVING DISTINCTIONS")
print("=" * 78)
print("  A block may hold one rule only if every context in it imposes the same")
print("  obligation. That is not a modelling choice -- it is what 'answers the")
print("  obligation' means. So the admissible splits are exactly the refinements")
print("  of the split by obligation, and the coarsest of them holds one block per")
print("  SURVIVING distinction. CSR-1, read over a context set.")
print()
print("  Every split of %d contexts (%d of them) is enumerated and tested in"
      % (K, BELL))
print("  every one of the %d worlds: %d arrangements x %d catalogues."
      % (len(WORLDS), BELL, len(CATALOGUES)))
print()
print("  %-26s %-4s %-14s %-16s %s"
      % ("split by obligation", "m", "admissible", "cheapest split", "is coarsest"))
box1 = []
for w in WORLDS:
    lab = tuple(w["labels"])
    tabs = [MASTER[i][1] for i in dict(CATALOGUES)[w["catalogue"]]][:w["m"]]
    adm = []
    for cand in PARTS:
        pr = price_split(cand, lab, tabs)
        if pr is not None:
            adm.append((pr["held"], cand))
    best_cost = min(a[0] for a in adm)
    winners = [a[1] for a in adm if a[0] == best_cost]
    box1.append({"catalogue": w["catalogue"], "partition": w["partition"],
                 "m": w["m"], "n_admissible": len(adm),
                 "cheapest_held": best_cost,
                 "coarsest_is_cheapest": w["partition"] in winners})
for r in box1[:BELL]:
    print("  %-26s %-4d %-14s %-16d %s"
          % (str(r["partition"]), r["m"], "%d / %d" % (r["n_admissible"], BELL),
             r["cheapest_held"], r["coarsest_is_cheapest"]))
print("  (table shown for the first catalogue; all %d worlds are checked)"
      % len(WORLDS))
OUT["admissible_splits"] = box1

for r in box1:
    assert r["coarsest_is_cheapest"], (
        "the split by obligation was not cheapest in %s / %s -- a refinement "
        "beat it, which would break the CSR-1 reading"
        % (r["catalogue"], r["partition"]))
counts = sorted(set(r["n_admissible"] for r in box1))
assert len(counts) >= 3, (
    "admissibility prunes to the same number of candidates in every world, so "
    "the enumeration is not discriminating")
assert any(1 < r["n_admissible"] < BELL for r in box1), (
    "no world leaves the search a real choice: admissibility either keeps "
    "everything or keeps one, and nothing was rejected")
assert any(r["n_admissible"] == 1 for r in box1), (
    "no world forces a unique split, so the pressure is never maximal")
assert any(r["n_admissible"] == BELL for r in box1), (
    "no world leaves every split admissible, so the pressure is never absent")
print()
print("  Admissible counts across the census: %s (of %d)."
      % (", ".join(str(c) for c in counts), BELL))
print("  In every one of the %d worlds the cheapest admissible split is the"
      % len(WORLDS))
print("  split by obligation. Refining past it duplicates rules, and that is")
print("  never bought back by a cheaper label map -- checked, not assumed.")
print()
print("  > Specialization pressure is not a preference for modularity. It is the")
print("  > number of distinctions among contexts that the obligation refuses to")
print("  > let collapse, and it is read off the obligation alone.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("2  THE SHARED RULE'S OWN TREE, TAKEN APART AND MEASURED")
print("=" * 78)
print("  A machine holding one rule over tag and payload together must ALSO")
print("  separate the contexts, inside its own tree. So the label map is not")
print("  charged against zero. Rather than argue about what that tree contains,")
print("  it is walked and measured:")
print()
print("    REACH  nodes spent while more than one obligation is still possible")
print("    BODY   nodes below the point where only one is -- an obligation")
print("           implemented in some particular place")
print("    SHARED leaves reached while several obligations are still live and")
print("           already agree: one leaf serving several obligations at once,")
print("           which no split machine can have")
print()
print("  reach + body = the whole tree, asserted in every world.")
print()
print("  A label map is TAG-COLLAPSIBLE when its smallest tree has one leaf per")
print("  label, i.e. holds 2m-1 nodes.")
print()
for lbl, grp in (("dear", DEAR), ("cheap", CHEAP)):
    print("  -- catalogue %s, rule costs %s --" % (lbl, grp[1]["rule_costs"]))
    print("     %-18s %-3s %-6s %-6s %-7s %-7s %-7s %-8s %s"
          % ("labels", "m", "map", "coll.", "reach", "body", "bodies", "shared",
             "most places"))
    for w in grp:
        print("     %-18s %-3d %-6d %-6s %-7d %-7d %-7d %-8d %d"
              % (str(w["labels"]), w["m"], w["label_held"],
                 w["tag_collapsible"], w["reach"], w["dense_body"],
                 w["n_bodies"], w["shared_leaves"], w["max_places"]))
    print()
OUT["census"] = WORLDS

coll = [w["tag_collapsible"] for w in WORLDS]
assert any(coll) and not all(coll), (
    "the label maps in this census are all collapsible or none are, so the "
    "distinction is never exercised")
dup = [w for w in WORLDS if w["max_places"] > 1]
assert dup, (
    "no world's shared rule implements any obligation in more than one place, "
    "so the duplication the whole argument rests on was never observed")
assert len(dup) < len(WORLDS), (
    "every world duplicates, so duplication distinguishes nothing")
# Collapsibility is a property of the LABEL MAP; duplication is a property of
# the tree that was actually built. They are measured separately and their
# relationship is reported, not assumed.
agree = sum(1 for w in WORLDS
            if (w["max_places"] > 1) == (not w["tag_collapsible"]))
OUT["collapsible_vs_duplication"] = {
    "agree": agree, "worlds": len(WORLDS),
    "collapsible_but_duplicates": [
        {"catalogue": w["catalogue"], "labels": w["labels"],
         "max_places": w["max_places"], "root": w["single_root"]}
        for w in WORLDS if w["tag_collapsible"] and w["max_places"] > 1],
    "noncollapsible_no_duplication": [
        {"catalogue": w["catalogue"], "labels": w["labels"]}
        for w in WORLDS if (not w["tag_collapsible"]) and w["max_places"] <= 1]}
sh = [w for w in WORLDS if w["shared_leaves"] > 0]
assert sh, (
    "no shared leaf anywhere: the one advantage the undivided rule has that a "
    "split cannot copy is absent from the census")
print("  Duplication is OBSERVED, not inferred: %d of %d worlds implement some"
      % (len(dup), len(WORLDS)))
print("  obligation in more than one place. It does NOT coincide with what the")
print("  label map looks like:")
print()
print("    %-24s %-14s %s" % ("", "duplicates", "does not"))
for cflag in (True, False):
    row = [sum(1 for w in WORLDS
               if w["tag_collapsible"] == cflag and (w["max_places"] > 1) == d)
           for d in (True, False)]
    print("    %-24s %-14d %d"
          % ("map collapsible" if cflag else "map not collapsible",
             row[0], row[1]))
print()
nc_nodup = [w for w in WORLDS
            if (not w["tag_collapsible"]) and w["max_places"] <= 1]
assert not nc_nodup, (
    "%d non-collapsible world(s) do not duplicate, so the implication below is "
    "false" % len(nc_nodup))
print("  The implication runs ONE way, with no exceptions: every")
print("  non-collapsible world duplicates (%d of %d), while collapsible worlds"
      % (sum(1 for w in WORLDS if not w["tag_collapsible"]),
         sum(1 for w in WORLDS if not w["tag_collapsible"])))
print("  may duplicate too. Interleaved labels FORCE the tree to reach an")
print("  obligation twice; a compact label map merely permits it to avoid that,")
print("  and it often does not bother.")
print()
mismatch = [w for w in WORLDS
            if w["tag_collapsible"] and w["max_places"] > 1]
assert mismatch, (
    "collapsibility and duplication agree in every world, so the two were "
    "never independently measured and one is standing in for the other")
print("  %d worlds have a collapsible label map and STILL duplicate. The reason"
      % len(mismatch))
print("  is visible in the root tests below: the undivided rule often tests a")
print("  PAYLOAD bit first and separates the contexts late, so it arrives at the")
print("  same obligation down many branches even when a compact label map")
print("  exists. What the map could look like does not determine what the tree")
print("  actually does -- which is why the tree is walked rather than argued")
print("  about.")
print()
print("  %d worlds contain at least one SHARED leaf -- a place where the"
      % len(sh))
print("  obligations already agree and the undivided rule answers them all at")
print("  once. A split machine cannot do this: each block implements its rule")
print("  alone, so it re-tests payload structure the obligations had in common.")
print()
roots = {}
for w in WORLDS:
    roots[w["single_root"]] = roots.get(w["single_root"], 0) + 1
print("  Root test of the shared rule across the census:")
for k in sorted(roots):
    print("    %-16s %d world(s)" % (k, roots[k]))
print("  (It was priced at the best tree that exists, over tag and payload")
print("  jointly, and was free to test payload first.)")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("3  THE LAW: A LABEL MAP MUST OUT-EARN WHAT IT REPLACES")
print("=" * 78)
print("  The two machines differ in exactly two terms, both measured above:")
print()
print("    A = map held - reach      what the split pays to hold the")
print("                              separation explicitly, net of what the")
print("                              undivided rule spends separating anyway")
print("    B = body - split bodies   what the undivided rule pays implementing")
print("                              obligations in several places, net of what")
print("                              it saves by sharing leaves between them")
print()
print("    net = B - A,  asserted in every world.")
print()
print("  So conditioning pays iff B > A. That is PVR-3 with the label map on the")
print("  retention side: retained structure earns its keep past a break-even")
print("  fixed by what it replaces.")
print()
for lbl, grp in (("dear", DEAR), ("cheap", CHEAP)):
    print("  -- catalogue %s, rule costs %s --" % (lbl, grp[1]["rule_costs"]))
    print("     %-18s %-3s %-7s %-9s %-6s %-6s %-6s %s"
          % ("labels", "m", "coll.", "one rule", "split", "A", "B", "pays"))
    for w in grp:
        print("     %-18s %-3d %-7s %-9d %-6d %-6d %-6d %s"
              % (str(w["labels"]), w["m"], w["tag_collapsible"],
                 w["single_held"], w["split_held"],
                 w["term_a_map_over_reach"], w["term_b_body_over_bodies"],
                 w["pays"]))
    print()

pays = [w["pays"] for w in WORLDS]
assert any(pays), (
    "conditioning never pays anywhere in the census: the positive claim has no "
    "support and this box cannot be closed")
assert not all(pays), (
    "conditioning pays in every world, so the mechanism fires everywhere and "
    "distinguishes nothing")
A = [w["term_a_map_over_reach"] for w in WORLDS]
Bv = [w["term_b_body_over_bodies"] for w in WORLDS]
assert any(x > 0 for x in A), "the label map is never a net extra cost"
assert any(x > 0 for x in Bv), (
    "the undivided rule never pays extra to implement obligations in several "
    "places, so there is nothing for a label map to buy back")
assert any(x < 0 for x in Bv), (
    "the undivided rule never comes out AHEAD on obligation bodies, so leaf "
    "sharing -- the split machine's structural disadvantage -- is invisible")

# necessity and insufficiency of non-collapsibility
for w in WORLDS:
    assert not (w["pays"] and w["tag_collapsible"]), (
        "%s / %s pays although its label map is tag-collapsible: the "
        "undivided rule reaches every obligation once and there is nothing to "
        "amortize" % (w["catalogue"], w["labels"]))
counterex = [w for w in WORLDS if (not w["tag_collapsible"]) and not w["pays"]]
assert counterex, (
    "every non-collapsible world pays, so this census cannot tell the "
    "biconditional from the one-way implication and must not claim either")
print("  NECESSARY, AND NOT SUFFICIENT.")
print()
print("  Necessary: no world pays while its label map is tag-collapsible. If the")
print("  undivided rule reaches each obligation exactly once, B <= 0 and there")
print("  is nothing for the map to buy back. %d of %d worlds are collapsible and"
      % (sum(1 for w in WORLDS if w["tag_collapsible"]), len(WORLDS)))
print("  none of them pay.")
print()
print("  Not sufficient: %d worlds are NOT collapsible and STILL do not pay."
      % len(counterex))
print("  %-10s %-18s %-3s %-9s %-6s %-6s %-6s %s"
      % ("catalogue", "labels", "m", "one rule", "split", "A", "B", "net"))
for w in counterex:
    print("  %-10s %-18s %-3d %-9d %-6d %-6d %-6d %d"
          % (w["catalogue"], str(w["labels"]), w["m"], w["single_held"],
             w["split_held"], w["term_a_map_over_reach"],
             w["term_b_body_over_bodies"], w["net_leaves"]))
OUT["counterexamples_to_biconditional"] = counterex
print()
print("  These are the counterexamples that killed a cleaner-looking law. An")
print("  earlier version of this witness swept only the ARRANGEMENT, over one")
print("  catalogue, and found 'pays iff not collapsible' holding in all %d"
      % BELL)
print("  worlds. Sweeping the catalogue breaks it: when the obligations are")
print("  cheap, duplicating one costs less than holding a map, so B <= A even")
print("  though the tree genuinely does duplicate.")
print()
print()
print("  WHICH TERM DOES THE WORK. Among the worlds that pay:")
paying = [w for w in WORLDS if w["pays"]]
by_a = [w for w in paying if w["term_a_map_over_reach"] < 0]
by_b = [w for w in paying if w["term_b_body_over_bodies"] > 0]
both = [w for w in paying if w in by_a and w in by_b]
OUT["which_term"] = {"paying": len(paying), "map_cheaper_than_reach": len(by_a),
                     "bodies_cost_more_undivided": len(by_b),
                     "both": len(both)}
print("    %d pay with A < 0 -- holding the separation explicitly costs LESS"
      % len(by_a))
print("       than what the undivided rule spends separating inside its tree")
print("    %d pay with B > 0 -- the undivided rule spends more on obligation"
      % len(by_b))
print("       bodies than the split does")
print("    %d have both" % len(both))
assert by_a and by_b, (
    "one of the two terms never carries a world on its own, so the "
    "decomposition is not two mechanisms but one wearing two names")
print()
print("  So 'the tree must duplicate the rule' is only part of it, and in this")
print("  census not the larger part. The undivided rule's real handicap is that")
print("  it must INTERLEAVE separating the contexts with computing the")
print("  obligation; the split holds that separation once, compactly, and the")
print("  saving often shows up as A < 0 rather than as duplicated bodies.")
print()
print("  > Conditioning pays when what the undivided rule spends implementing")
print("  > the same obligation in several places exceeds what the split spends")
print("  > holding the separation explicitly. Interleaving is what makes that")
print("  > surplus POSSIBLE; the price of the obligations is what makes it")
print("  > REAL. Both ends still die: with m = 1 there is no distinction to")
print("  > hold, with m = K no obligation is reached twice.")
for w in WORLDS:
    if w["m"] == 1 or w["m"] == K:
        assert not w["pays"], (
            "%s / %s pays at m = %d, where one end of the law should be dead"
            % (w["catalogue"], w["labels"], w["m"]))


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("3b  TWO MATCHED NEGATIVE TWINS")
print("=" * 78)
print("  A positive claim is worth what its nearest negative is. Two are built,")
print("  each differing from its positive in exactly ONE thing.")
print()
print("  (i) ARRANGEMENT twin -- same catalogue, same obligations, same m; only")
print("      where in the context set they sit differs.")
print()
arr = [w for w in DEAR if w["m"] == 2]
ap = [w for w in arr if w["pays"]]
an = [w for w in arr if not w["pays"]]
assert ap and an, (
    "every arrangement of the same two obligations falls the same way, so "
    "there is no arrangement twin")
print("      %-18s %-7s %-9s %-6s %-6s %-6s %s"
      % ("labels", "coll.", "one rule", "split", "A", "B", "verdict"))
for w in arr:
    print("      %-18s %-7s %-9d %-6d %-6d %-6d %s"
          % (str(w["labels"]), w["tag_collapsible"], w["single_held"],
             w["split_held"], w["term_a_map_over_reach"],
             w["term_b_body_over_bodies"],
             "pays" if w["pays"] else "pure overhead"))
print()
print("      %d pay, %d are overhead. The obligations did not change."
      % (len(ap), len(an)))
print()
print("  (ii) CATALOGUE twin -- same arrangement, same m, same context set; only")
print("       how expensive the obligations are differs.")
print()
cat_twin = []
for lab in set(tuple(w["labels"]) for w in WORLDS):
    grp = [w for w in WORLDS if tuple(w["labels"]) == lab]
    if len(set(w["pays"] for w in grp)) > 1:
        cat_twin.append((lab, grp))
assert cat_twin, (
    "no arrangement changes verdict when the catalogue changes, so the "
    "catalogue sweep found nothing and the earlier biconditional would stand")
lab, grp = sorted(cat_twin)[0]
print("       %-18s %-10s %-12s %-9s %-6s %-6s %-6s %s"
      % ("labels", "catalogue", "rule costs", "one rule", "split", "A", "B",
         "verdict"))
for w in grp:
    print("       %-18s %-10s %-12s %-9d %-6d %-6d %-6d %s"
          % (str(w["labels"]), w["catalogue"], str(w["rule_costs"]),
             w["single_held"], w["split_held"], w["term_a_map_over_reach"],
             w["term_b_body_over_bodies"],
             "pays" if w["pays"] else "pure overhead"))
OUT["twins"] = {"arrangement": arr, "catalogue_flip_arrangements":
                [list(l) for l, _g in cat_twin]}
print()
print("       %d of the %d arrangements change verdict when only the price of"
      % (len(cat_twin), BELL))
print("       the obligations changes. Interleaving alone does not decide.")
print()
hom = [w for w in DEAR if w["m"] == 1][0]
forced = []
for cand in PARTS:
    if len(cand) == 1:
        continue
    pr = price_split(cand, tuple(hom["labels"]),
                     [MASTER[i][1] for i in (0, 1, 2, 3)][:1])
    if pr is not None:
        forced.append(pr["held"])
assert forced, "the homogeneous world admits no split with more than one block"
assert min(forced) > hom["single_held"], (
    "a forced split beat the shared rule in the homogeneous world, which would "
    "mean conditioning can pay with no distinction to condition on")
print("  (iii) The HOMOGENEOUS twin. With one obligation the only admissible")
print("        split is the single block, and it still holds a label-map node")
print("        (%d against the shared rule's %d). Every FORCED split of that"
      % (hom["split_held"], hom["single_held"]))
print("        world costs at least %d against %d -- strictly worse, always."
      % (min(forced), hom["single_held"]))
OUT["homogeneous_forced_splits"] = {"single_held": hom["single_held"],
                                    "cheapest_forced_split": min(forced),
                                    "n_forced": len(forced)}


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("3c  THE SAME CENSUS, CHARGED FOR TESTS ONLY")
print("=" * 78)
print("  Charging leaves is what puts the break-even off zero. Under a")
print("  tests-only charge every tree re-prices as (nodes-1)/2 -- the SAME tree,")
print("  so no second search. The verdicts are recomputed so the claim can be")
print("  seen not to be an artifact of the convention.")
print()
flips = [w for w in WORLDS
         if (w["net_leaves"] > 0) != (w["net_internal_only"] > 0)]
OUT["convention_check"] = {
    "n_flips": len(flips),
    "flipped": [{"catalogue": w["catalogue"], "labels": w["labels"],
                 "net_leaves": w["net_leaves"],
                 "net_tests_only": w["net_internal_only"]} for w in flips]}
print("  worlds: %d    verdict flips under the other convention: %d"
      % (len(WORLDS), len(flips)))
for w in flips:
    print("    %-10s %-18s net(leaves)=%-4d net(tests only)=%d"
          % (w["catalogue"], str(w["labels"]), w["net_leaves"],
             w["net_internal_only"]))
assert len(flips) < len(WORLDS), "the convention decides every world"
margin = max(abs(w["net_leaves"]) for w in flips) if flips else 0
OUT["convention_check"]["max_flipped_margin"] = margin
assert all(abs(w["net_leaves"]) <= 1 for w in flips), (
    "a world with a clear verdict (margin %d nodes) flips under the other "
    "charge, so the result IS a convention artifact and must be reported as "
    "one rather than as a law" % margin)
assert flips, (
    "no world flips at all, so this check never exercised the convention and "
    "proves nothing about it")
print()
print("  %d of %d worlds flip, and every one of them was within %d node(s) of a"
      % (len(flips), len(WORLDS), margin))
print("  tie under the leaf charge. No world with a clear verdict changes hands.")
print("  The convention decides the margin and nothing else -- which is stated")
print("  here rather than hidden by picking the convention that reads better.")
print("  All flips move the SAME way (a tie becomes a narrow win for the split),")
print("  because dropping the leaf charge removes m-1 leaves more from the")
print("  split's bill than from the undivided rule's.")
assert all(w["net_internal_only"] > w["net_leaves"] for w in flips), (
    "the flips do not all move the same way, so the explanation above is wrong")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("4  LOAD AND COMMUNICATION: PVR-3 PER BLOCK, WITH LOAD AS THE COUNT")
print("=" * 78)
print("  A held rule is retained structure. PVR-3 prices it: holding beats")
print("  re-deriving iff  S < (r-1)(C-U),  where r is how often it is REACHED.")
print("  Splitting a fixed query budget across blocks gives each block its own")
print("  r. Load balance is therefore not a separate concern -- it is PVR-3")
print("  evaluated per block with the ecology's own frequencies.")
print()
print("  Communication. A label map must emit one state per surviving")
print("  distinction (CSR-1), so it emits ceil(log2 m) bits per query.")
comm = []
for m in range(1, K + 1):
    bits = 0
    while (1 << bits) < m:
        bits += 1
    comm.append({"m": m, "bits_per_query": bits})
    print("    m = %d  ->  %d bit(s) per query" % (m, bits))
OUT["communication"] = comm
assert comm[0]["bits_per_query"] == 0, (
    "a single-block machine is charged for naming a block, which is a state "
    "held against no distinction")
assert comm[-1]["bits_per_query"] > 0, "naming is free at every m"
print("  At m = 1 the charge is zero: there is nothing to say.")
print()
print("  Load is exhibited on the m = K world of the dear catalogue. That world")
print("  is the one this witness's own accounting says should NOT be built")
print("  (net %d). It is used here because four distinct obligations at four"
      % [w for w in DEAR if w["m"] == K][0]["net_leaves"])
print("  different prices give the most load differentiation; the PVR-3")
print("  arithmetic below is per block and does not depend on that verdict.")
print()
LTABS = [MASTER[i][1] for i in (0, 1, 2, 3)]
LNAMES = [MASTER[i][0] for i in (0, 1, 2, 3)]
lab4 = tuple(range(K))
R_TOTAL = 16
regimes = [("uniform", tuple(F(1, K) for _ in range(K))),
           ("skewed", (F(13, 16), F(1, 16), F(1, 16), F(1, 16)))]

# The same two regimes, run against EVERY catalogue, so that the result is not
# a property of one set of prices. C-U is 12 down to 2 across these.
sweep = []
for cname, cidx in CATALOGUES:
    tb_ = [MASTER[i][1] for i in cidx]
    for rname, q in regimes:
        npass = 0
        for c in range(K):
            S = held(tb_[c], N)
            U = traversed(tb_[c], N)
            rq = int(q[c] * R_TOTAL)
            if S < (rq - 1) * (S - U):
                npass += 1
        sweep.append({"catalogue": cname, "regime": rname, "n_pass": npass,
                      "blocks": K,
                      "c_minus_u": [held(t, N) - traversed(t, N) for t in tb_]})
OUT["load_sweep"] = sweep
print("  %-10s %-10s %-12s %s" % ("catalogue", "regime", "clear PVR-3", "C-U per block"))
for r in sweep:
    print("  %-10s %-10s %-12s %s"
          % (r["catalogue"], r["regime"], "%d / %d" % (r["n_pass"], r["blocks"]),
             str(r["c_minus_u"])))
for r in sweep:
    if r["regime"] == "uniform":
        assert r["n_pass"] == K, (
            "catalogue %s: a block fails PVR-3 under a UNIFORM load, so the "
            "skewed result there would not be attributable to skew" % r["catalogue"])
    else:
        assert 0 < r["n_pass"] < K, (
            "catalogue %s: the skewed load leaves %d of %d blocks worth "
            "holding, which is not imbalance"
            % (r["catalogue"], r["n_pass"], K))
print()
print("  The split is %d/%d under a uniform load and %d/%d under the skewed one"
      % (K, K, sweep[1]["n_pass"], K))
print("  in EVERY catalogue, with C-U ranging from %d to %d. The load result is"
      % (min(min(r["c_minus_u"]) for r in sweep),
         max(max(r["c_minus_u"]) for r in sweep)))
print("  not a property of one set of prices.")
print()
print("  In full, for the dear catalogue:")
print()
load_rows = []
for rname, q in regimes:
    assert sum(q) == 1, "frequencies must be exact and sum to one"
    for c in range(K):
        assert (q[c] * R_TOTAL).denominator == 1, (
            "the query budget must be a multiple of the frequency denominators "
            "so that every load is an exact integer")
    print("  -- %s frequencies, %d queries --" % (rname, R_TOTAL))
    print("     %-20s %-8s %-6s %-6s %-6s %-14s %s"
          % ("obligation", "load r", "S", "C", "U", "(r-1)(C-U)", "worth holding"))
    for c in range(K):
        t = LTABS[lab4[c]]
        S = held(t, N)
        C = S
        U = traversed(t, N)
        rq = int(q[c] * R_TOTAL)
        thr = (rq - 1) * (C - U)
        load_rows.append({"regime": rname, "rule": LNAMES[lab4[c]],
                          "freq": str(q[c]), "load": rq, "S": S, "C": C,
                          "U": U, "threshold": thr, "worth_holding": S < thr})
        print("     %-20s %-8d %-6d %-6d %-6d %-14d %s"
              % (LNAMES[lab4[c]], rq, S, C, U, thr, S < thr))
    ex = sum(q[c] * F(traversed(LTABS[lab4[c]], N)) for c in range(K))
    print("     expected traversal per query: %s + %s = %s"
          % (traversed(lab4, B), ex, F(traversed(lab4, B)) + ex))
    print()
OUT["load"] = load_rows
uni = [r for r in load_rows if r["regime"] == "uniform"]
skw = [r for r in load_rows if r["regime"] == "skewed"]
for r in load_rows:
    assert r["C"] - r["U"] > 0, (
        "obligation %s has C <= U, so PVR-3's threshold is not defined for it"
        % r["rule"])
assert all(r["worth_holding"] for r in uni), (
    "some block fails PVR-3 even under a uniform load, so the skewed result "
    "would not be attributable to skew")
assert any(not r["worth_holding"] for r in skw), (
    "every block still clears PVR-3 under the skewed load, so skew costs "
    "nothing here and load balance has not been exhibited")
assert not all(not r["worth_holding"] for r in skw), (
    "no block survives the skewed load, so the skew is degenerate")
n_fail = sum(1 for r in skw if not r["worth_holding"])
print("  Under a uniform load all %d blocks clear PVR-3. Under the skewed load"
      % K)
print("  %d of %d fall below it: their storage is held for queries that never"
      % (n_fail, K))
print("  arrive. Nothing about those obligations changed -- only how often the")
print("  ecology reaches them.")
print()
print("  > A block is worth holding separately exactly when its OWN load clears")
print("  > PVR-3. Imbalance does not make a machine slow; it makes part of the")
print("  > machine unpaid-for. The ecology's frequencies, not the designer, fix")
print("  > how many blocks can exist.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("5  THE CROSSOVER IS IN ARRANGEMENT AND PRICE, NOT IN THE BLOCK COUNT")
print("=" * 78)
print("  %-10s %-5s %-14s %-18s %s"
      % ("catalogue", "m", "arrangements", "conditioning pays", "net range"))
cross = []
for cname, _ci in CATALOGUES:
    for m in range(1, K + 1):
        grp = [w for w in WORLDS if w["catalogue"] == cname and w["m"] == m]
        p = [w for w in grp if w["pays"]]
        nets = sorted(w["net_leaves"] for w in grp)
        cross.append({"catalogue": cname, "m": m, "arrangements": len(grp),
                      "n_pays": len(p), "net_min": nets[0], "net_max": nets[-1]})
        print("  %-10s %-5d %-14d %-18s %s"
              % (cname, m, len(grp), "%d / %d" % (len(p), len(grp)),
                 "%d .. %d" % (nets[0], nets[-1])))
OUT["crossover"] = cross
for c in cross:
    if c["m"] in (1, K):
        assert c["n_pays"] == 0, (
            "conditioning pays at m = %d in catalogue %s" % (c["m"], c["catalogue"]))
mid = [c for c in cross if 1 < c["m"] < K]
assert any(c["n_pays"] > 0 for c in mid), (
    "conditioning never pays at any intermediate m, so there is no crossover")
assert any(c["n_pays"] < c["arrangements"] for c in mid), (
    "at every intermediate m every arrangement pays, so arrangement decides "
    "nothing and the result is only a statement about m")
assert len(set(c["n_pays"] for c in cross if c["m"] == 2)) > 1, (
    "the catalogue makes no difference at fixed m, so the sweep was wasted")
print()
print("  The prediction is NOT 'few blocks good, many blocks bad'. At a fixed m")
print("  both verdicts occur, and the same arrangement flips when only the")
print("  price of the obligations changes.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("5b  TRAVERSAL, AND WHY THE SPLIT'S ADVANTAGE EXPIRES")
print("=" * 78)
print("  Worst case is the longest path; expected is the mean over every input,")
print("  uniform over contexts and payloads. Both exact rationals.")
print()
u_rows = []
for w in WORLDS:
    lab = tuple(w["labels"])
    tabs = [MASTER[i][1] for i in dict(CATALOGUES)[w["catalogue"]]][:w["m"]]
    e_single = expected_traversed(joint_table(lab, tabs), B + N)
    e_split = expected_traversed(lab, B) + sum(
        F(1, K) * expected_traversed(tabs[lab[c]], N) for c in range(K))
    u_rows.append({
        "catalogue": w["catalogue"], "labels": w["labels"],
        "single_U": w["single_traversed"], "split_U": w["split_traversed"],
        "worst_cheaper": ("split" if w["split_traversed"] < w["single_traversed"]
                          else ("one rule" if w["single_traversed"] < w["split_traversed"]
                                else "tie")),
        "single_expected_U": str(e_single), "split_expected_U": str(e_split),
        "expected_cheaper": ("split" if e_split < e_single
                             else ("one rule" if e_single < e_split else "tie"))})
OUT["traversal"] = u_rows
levels = sorted(set(r["single_U"] for r in u_rows))
assert len(levels) > 1, (
    "traversal takes one value across the whole census, so the quantity is "
    "dead and no statement about it means anything")
assert not any(r["expected_cheaper"] == "split" for r in u_rows), (
    "expected traversal favours the split in some world, so conditioning does "
    "buy computation here and the negative below is wrong")
n_worse = sum(1 for r in u_rows if r["expected_cheaper"] == "one rule")
assert 0 < n_worse < len(u_rows), (
    "expected traversal either ties everywhere or separates everywhere; either "
    "way the comparison below is not what is printed")
n_wtie = sum(1 for r in u_rows if r["worst_cheaper"] == "tie")
OUT["traversal_summary"] = {"worst_case_ties": n_wtie, "worlds": len(u_rows),
                            "expected_split_ever_cheaper": False,
                            "expected_split_strictly_worse_in": n_worse}
w_exc = [r for r in u_rows if r["worst_cheaper"] != "tie"]
assert all(r["worst_cheaper"] == "one rule" for r in w_exc), (
    "a world's worst-case traversal favours the SPLIT, so the claim that "
    "conditioning never buys computation is false on that axis too")
print("  worst-case traversal takes the values %s; the two shapes tie on it in"
      % ", ".join(str(v) for v in levels))
print("  %d of %d worlds, and in the %d that do not tie it is the UNDIVIDED"
      % (n_wtie, len(u_rows), len(w_exc)))
print("  rule that traverses less -- never the split:")
for r in w_exc:
    print("    %-9s %-16s one rule U=%d  split U=%d"
          % (r["catalogue"], str(r["labels"]), r["single_U"], r["split_U"]))
print("  On EXPECTED traversal the split is likewise NEVER cheaper, and is")
print("  strictly more expensive in %d of %d." % (n_worse, len(u_rows)))
print()
print("  > Conditioning buys no computation here. It costs some.")
print()
print("  The reason is structural. A branching machine already visits one path")
print("  per query, so the undivided rule is ALREADY conditional at run time.")
print("  Worse, it may interleave tag and payload tests and stop early where the")
print("  obligations agree -- those are the SHARED leaves counted in box 2. The")
print("  split machine must resolve the label FIRST, in full, before it may look")
print("  at the payload at all. Committing to a block up front is what costs the")
print("  extra tests. A compute saving would need a machine that reads all of")
print("  itself on every query -- a flat weighted sum, not a tree -- and that")
print("  shape is not priced here.")
print()
print("  So the split wins on what it HOLDS and loses on what it SPENDS, and")
print("  where both are strict the verdict must turn over, at exactly")
print()
print("      r* = (net held) / (E[tests] split - E[tests] one rule)")
print()
print("  %-10s %-18s %-8s %-10s %-10s %s"
      % ("catalogue", "labels", "net held", "gap/query", "r*", "r = 8 / 64 / 512"))
xover = []
for w, u in zip(WORLDS, u_rows):
    if not w["pays"]:
        continue
    gap = F(u["split_expected_U"]) - F(u["single_expected_U"])
    net = F(w["net_leaves"])
    rstar = str(net / gap) if gap > 0 else "never"
    verdicts = []
    for r in (8, 64, 512):
        ts = F(w["split_held"]) + r * F(u["split_expected_U"])
        to = F(w["single_held"]) + r * F(u["single_expected_U"])
        verdicts.append("split" if ts < to else ("one rule" if to < ts else "tie"))
    xover.append({"catalogue": w["catalogue"], "labels": w["labels"],
                  "net_held": str(net), "per_query_gap": str(gap),
                  "r_star": rstar, "verdict_r8": verdicts[0],
                  "verdict_r64": verdicts[1], "verdict_r512": verdicts[2]})
    print("  %-10s %-18s %-8s %-10s %-10s %s"
          % (w["catalogue"], str(w["labels"]), str(net), str(gap), rstar,
             " / ".join(verdicts)))
OUT["query_crossover"] = xover
finite = [x for x in xover if x["r_star"] != "never"]
never = [x for x in xover if x["r_star"] == "never"]
assert finite, (
    "no world where the split wins on storage loses it back at any query "
    "count, so there is no crossover in r and this box is empty")
assert never, (
    "every split-favouring world expires, so the case where conditioning is "
    "unconditionally right is absent and the law reads stronger than it is")
flipped = [x for x in xover if x["verdict_r8"] != x["verdict_r512"]]
assert flipped, (
    "no world changes hands between r = 8 and r = 512, so the crossover is "
    "outside the printed range and the table misleads")
print()
print("  %d of %d split-favouring worlds expire at a finite r; %d never do;"
      % (len(finite), len(xover), len(never)))
print("  %d change hands inside the printed range." % len(flipped))
print()
print("  > Conditional specialization is a STORAGE bargain paid for in per-query")
print("  > work, and the bargain has a finite life. It is the correct machine")
print("  > exactly while the ecology asks few enough questions that the storage")
print("  > it saves outweighs the extra tests it spends. Past r* the undivided")
print("  > rule is cheaper -- the same break-even as everything else in this")
print("  > corpus, read with the split on the retention side for once.")
print("  The exception is printed and real: where the two spend the same per")
print("  query, the split's storage win never expires.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("6  NEUTRAL RECOVERY: NO FAMILY NAME IN THE CANDIDATE SPACE")
print("=" * 78)
print("  A candidate is described by two things only: how it splits the context")
print("  set into blocks, and which rule it holds per block. The one-block")
print("  candidate -- hold a single rule for everything -- is a member like any")
print("  other, as is holding one rule over tag and payload together. Every")
print("  candidate is enumerated and priced in every world. Nothing is named.")
print()
rec = []
for w in WORLDS:
    lab = tuple(w["labels"])
    tabs = [MASTER[i][1] for i in dict(CATALOGUES)[w["catalogue"]]][:w["m"]]
    cands = []
    for cand in PARTS:
        pr = price_split(cand, lab, tabs)
        if pr is not None:
            cands.append((pr["held"], len(cand),
                          "split into %d block(s)" % len(cand), cand))
    sg = price_single(lab, tabs)
    cands.append((sg["held"], 1, "one rule over tag and payload", None))
    cands.sort(key=lambda z: (z[0], z[1]))
    best = cands[0]
    reads = ("conditioned on context"
             if (best[3] is not None and len(best[3]) > 1)
             else "one undivided rule")
    floor = min(z[0] for z in cands)
    rec.append({"catalogue": w["catalogue"], "labels": w["labels"], "m": w["m"],
                "cheapest": best[2], "held": best[0], "reads_as": reads,
                "n_candidates_priced": len(cands), "cost_floor": floor,
                "n_strictly_worse_rejected": sum(1 for z in cands if z[0] > floor),
                "winner_is_the_worlds_own_split":
                    best[3] is not None and
                    [sorted(b) for b in best[3]] == w["partition"]})
OUT["recovery"] = rec
for lbl, cn in (("dear", "dear"), ("cheap", "cheap")):
    print("  -- catalogue %s --" % lbl)
    print("     %-18s %-3s %-30s %-7s %s"
          % ("labels", "m", "cheapest candidate", "held", "reads as"))
    for r in [r for r in rec if r["catalogue"] == cn]:
        print("     %-18s %-3d %-30s %-7d %s"
              % (str(r["labels"]), r["m"], r["cheapest"], r["held"],
                 r["reads_as"]))
    print()

shapes = set(r["reads_as"] for r in rec)
assert len(shapes) > 1, (
    "every world recovers the same shape, so the candidate space is not "
    "discriminating and nothing has been recovered")
assert any(r["n_candidates_priced"] > 2 for r in rec), (
    "no world priced more than the trivial two candidates, so the enumeration "
    "is a restatement rather than a search")
# Checks against a chooser that returns the answer it was handed rather than
# searching. Each fires on a rigged selection the shape counts above accept.
for r in rec:
    assert r["held"] == r["cost_floor"], (
        "%s / %s reports a winner costing %d while a priced candidate costs "
        "%d: the selection is not a minimum and is therefore not a search"
        % (r["catalogue"], r["labels"], r["held"], r["cost_floor"]))
assert all(r["n_strictly_worse_rejected"] > 0 for r in rec), (
    "some world has no strictly worse candidate to reject, so nothing was "
    "chosen against")
assert any(not r["winner_is_the_worlds_own_split"] for r in rec), (
    "the winner is the world's own split by obligation in EVERY world, which "
    "is what a chooser handed the answer would produce")
assert any(r["winner_is_the_worlds_own_split"] for r in rec), (
    "the world's own split never wins, so the recovery means something else")
for r, w in zip(rec, WORLDS):
    assert (r["reads_as"] == "conditioned on context") == w["pays"], (
        "%s / %s: the search recovers %r while the independent net-held "
        "accounting says pays=%s -- two routes to one verdict disagree"
        % (r["catalogue"], r["labels"], r["reads_as"], w["pays"]))
n_own = sum(1 for r in rec if r["winner_is_the_worlds_own_split"])
n_cond = sum(1 for r in rec if r["reads_as"] == "conditioned on context")
print("  Each world priced %d to %d candidates and rejected %d to %d of them as"
      % (min(r["n_candidates_priced"] for r in rec),
         max(r["n_candidates_priced"] for r in rec),
         min(r["n_strictly_worse_rejected"] for r in rec),
         max(r["n_strictly_worse_rejected"] for r in rec)))
print("  strictly more expensive. The world's own split by obligation won in %d"
      % n_own)
print("  of %d worlds and LOST in %d; a chooser handed the answer would have won"
      % (len(rec), len(rec) - n_own))
print("  in all %d. Every recovered verdict was cross-checked against the"
      % len(rec))
print("  independent accounting of box 3 and agrees with it.")
print()
print()
print("  By catalogue:")
for cname, _ix in CATALOGUES:
    g = [r for r in rec if r["catalogue"] == cname]
    n = sum(1 for r in g if r["reads_as"] == "conditioned on context")
    print("    %-10s split recovered in %2d / %d" % (cname, n, len(g)))
assert len(set(sum(1 for r in rec if r["catalogue"] == c
                   and r["reads_as"] == "conditioned on context")
               for c, _i in CATALOGUES)) > 1, (
    "every catalogue recovers the split equally often, so price changes nothing")
print("  Three of the four catalogues were chosen CHEAP, to press the mechanism")
print("  rather than flatter it. The split is recovered where obligations are")
print("  expensive and almost nowhere where they are not, which is the law.")
print()
print("  %d of %d worlds recover a machine that splits the context set; %d"
      % (n_cond, len(rec), len(rec) - n_cond))
print("  recover one undivided rule. Both shapes fall out of the same neutral")
print("  description, by cost alone, and neither was ever named.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("SCOPE -- WHAT THIS WORLD CANNOT SHOW")
print("=" * 78)
print("  * The context is GIVEN, as tag bits in the input. Inferring which")
print("    obligation is active from the payload alone is NOT modelled. That")
print("    latent case is the open gap's antecedent -- limited computation")
print("    against excessive possible information -- and this cost model charges")
print("    structure held, not information available, so it cannot test it.")
print("    Nothing here recovers routing in general.")
print("  * The corpus measured GATE at 0.37x under neutral selection. That is")
print("    consistent with, not contradicted by, this result: the registered")
print("    ecologies sit at m = 1, at tag-collapsible arrangements, or at cheap")
print("    obligations, and this accounting says conditioning is overhead in")
print("    all three. What is derived here is a CONDITION, not a recovery.")
print("  * The compute story is REFUTED here, not merely absent. A branching")
print("    machine is already conditional per query, and committing to a block")
print("    before reading the payload strictly RAISES expected tests. The")
print("    familiar 'active parameters' argument needs a machine that reads all")
print("    of itself per query; that shape is not priced here, and until it is,")
print("    nothing in this witness supports a compute claim.")
print("  * Trees only. A machine that could rejoin paths would get the reuse")
print("    saving with no label map at all, and the whole result would vanish.")
print("    The tree restriction is doing real work; it is named, not hidden.")
print("  * The verdict AT THE MARGIN is convention-dependent, and box 3c says")
print("    so: charging tests instead of tests-and-leaves flips 9 of 60 worlds,")
print("    every one of them within one node of a tie. Clear verdicts are")
print("    stable; near-ties are not, and should not be read as results.")
print("  * PVR-3 is applied in box 4 with C = S: re-deriving an obligation is")
print("    charged what holding it costs. That is an assumption, not a result,")
print("    and the thresholds printed there depend on it.")
print("  * %d contexts over %d tag bits, %d payload bits, %d catalogues of up to"
      % (K, B, N, len(CATALOGUES)))
print("    %d obligations, assigned to blocks in a fixed order. %d worlds in"
      % (K, len(WORLDS)))
print("    all. Orderings are the result; the constants are not. A wider")
print("    catalogue sweep could move the counterexample count, not the shape")
print("    of the law.")
print("  * Cost is nodes held and path traversed. Bytes, fan-out and any cost")
print("    of moving between blocks are not modelled.")
print()
print("  Falsifier. Exhibit a tag-collapsible arrangement where conditioning is")
print("  strictly cheaper than one undivided rule; or a world where a refinement")
print("  of the split by obligation beats the split by obligation; or a world")
print("  where the split's expected traversal is strictly lower.")

print()
print("=" * 78)
print("all assertions held")
print("=" * 78)

OUT["parameters"] = {"tag_bits": B, "contexts": K, "payload_bits": N,
                     "catalogues": [{"name": c, "rules": [MASTER[i][0] for i in ix]}
                                    for c, ix in CATALOGUES],
                     "n_splits_enumerated": BELL, "n_worlds": len(WORLDS),
                     "query_budget": R_TOTAL}

with open("microscopes/results/STAGE_CONDITIONAL_SPECIALIZATION_V1.json", "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)

"""B8: message passing derived from permutation symmetry in the obligation.

GMI_EQUIVARIANCE_DERIVATION_V1 derived convolution from TRANSLATION symmetry,
and found that shift-invariance LICENSES weight sharing without making a shared
detector sufficient -- the COMBINER has to match the obligation too. This is
the same argument on a general relation: PERMUTATION symmetry rather than
translation, with the incident set replacing the window and ROUNDS replacing
the receptive field.

Derived here, in order, none of it assumed:

  1  a permutation descriptor computed BEFORE any architecture is proposed
  2  ROUNDS, as the smallest propagation depth that determines the response --
     read off the obligation, exactly as the window was
  3  CSR-1: the carrier width is one state per distinction that must STILL be
     made, which is NOT one state per answer that gets reported
  4  the burden, rounds x traffic x width, and the round past which more
     propagation buys nothing and still costs
  5  neutral recovery over a candidate menu with no word for a message
  6  the ceiling: an obligation NO round count can meet, with the blocking
     pair of graphs exhibited and proven non-isomorphic

Exhaustive enumeration over three finite worlds. Exact integers throughout;
no sampling and no floating point in any reported number.
"""

import itertools
import json

OUT = {}

N4 = 4                                   # descriptor world: full S_4 is cheap
N5 = 5                                   # rounds / carrier / recovery world
N6 = 6                                   # ceiling world, unmarked

INF = 99                                 # "no marked node reachable"

OUT["scope"] = {
    "descriptor_world": "all 2^6 labelled graphs on 4 nodes x all 2^4 mark "
                        "assignments, against the FULL symmetric group S_4",
    "rounds_carrier_recovery_world": "all 2^10 labelled graphs on 5 nodes x "
                                     "all 2^5 mark assignments = 32768 "
                                     "configurations, 163840 (config, node) items",
    "machine_search_subcorpus": "the configurations of the 5-node world whose "
                                "maximum degree is at most 2. A machine on the "
                                "full world restricts to one of the searched "
                                "machines on this subcorpus, so finding none "
                                "here proves there is none anywhere",
    "ceiling_world": "all 2^15 labelled graphs on 6 nodes, unmarked, plus the "
                     "same construction at 3, 4 and 5 nodes for minimality",
    "arithmetic": "exact integers; widths are (k-1).bit_length() = ceil(log2 k)",
}


# ---------------------------------------------------------------------------
# the worlds
# ---------------------------------------------------------------------------
def graphs(n):
    """Every labelled simple undirected graph on n nodes, as incidence lists."""
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    out = []
    for bits in itertools.product((0, 1), repeat=len(pairs)):
        nbr = [[] for _ in range(n)]
        for b, (i, j) in zip(bits, pairs):
            if b:
                nbr[i].append(j)
                nbr[j].append(i)
        out.append(tuple(tuple(x) for x in nbr))
    return out


def marked_world(n):
    return [(g, m) for g in graphs(n)
            for m in itertools.product((0, 1), repeat=n)]


def edge_list(nbr):
    return sorted([i, j] for i in range(len(nbr)) for j in nbr[i] if i < j)


def describe(nbr, marks=None):
    d = {"edges": edge_list(nbr)}
    if marks is not None:
        d["marks"] = "".join(map(str, marks))
    return d


def mark_distance(nbr, marks):
    """Hops to the nearest marked node, INF if none is reachable."""
    n = len(nbr)
    d = [INF] * n
    cur = [v for v in range(n) if marks[v]]
    for v in cur:
        d[v] = 0
    step = 0
    while cur:
        step += 1
        nxt = []
        for v in cur:
            for u in nbr[v]:
                if d[u] == INF:
                    d[u] = step
                    nxt.append(u)
        cur = nxt
    return d


# ---------------------------------------------------------------------------
# the obligations
#
# Node-level obligations return one response per node; the single graph-level
# one returns a scalar. Nothing here mentions a machine.
# ---------------------------------------------------------------------------
LEVEL = {"any_marked": "graph"}


def responses(nbr, marks):
    n = len(nbr)
    d = mark_distance(nbr, marks)
    total = sum(marks)
    return {
        # reported at every node
        "own_mark": tuple(marks),
        "reach_1": tuple(1 if d[v] <= 1 else 0 for v in range(n)),
        "reach_2": tuple(1 if d[v] <= 2 else 0 for v in range(n)),
        "reach_3": tuple(1 if d[v] <= 3 else 0 for v in range(n)),
        # same rounds and same two-valued answer as reach_3, but it must still
        # tell "not reached yet" from "reached at an even distance"
        "odd_dist_3": tuple(1 if d[v] in (1, 3) else 0 for v in range(n)),
        # same rounds as reach_3, wider answer
        "cap_dist_4": tuple(min(d[v], 4) for v in range(n)),
        # global, but nothing to do with the relation
        "marked_and_company": tuple(
            1 if (marks[v] and total >= 2) else 0 for v in range(n)),
        # anchored in the labelling: which partner, not how many
        "lowest_partner_marked": tuple(
            marks[min(nbr[v])] if nbr[v] else 0 for v in range(n)),
        # anchored in the labelling: which node am I
        "is_node_0": tuple(1 if v == 0 else 0 for v in range(n)),
        # reported once for the whole configuration
        "any_marked": 1 if total else 0,
    }


NAMES = sorted(responses(((), (), (), (), ()), (0, 0, 0, 0, 0)))


# ===========================================================================
print("=" * 78)
print("1  THE PERMUTATION DESCRIPTOR, COMPUTED BEFORE ANY ARCHITECTURE")
print("=" * 78)
print("  Does the obligation commute with a relabelling of the nodes? For a")
print("  node-level obligation that means f(pi.G)[pi(v)] = f(G)[v]. This is a")
print("  property of the obligation alone and needs no candidate machine.")
print("  Checked against the FULL symmetric group, by exhaustion.")
print()

W4 = marked_world(N4)
RESP4 = {}
for nbr, marks in W4:
    RESP4[(nbr, marks)] = responses(nbr, marks)
PERMS4 = [tuple(p) for p in itertools.permutations(range(N4))]


def relabel(nbr, marks, p):
    n = len(nbr)
    nb = [[] for _ in range(n)]
    for v in range(n):
        for u in nbr[v]:
            nb[p[v]].append(p[u])
    inv = [0] * n
    for v in range(n):
        inv[p[v]] = v
    return (tuple(tuple(sorted(x)) for x in nb),
            tuple(marks[inv[w]] for w in range(n)))


print("  %-22s %-14s %s" % ("obligation", "equivariant", "counterexample"))
equi = []
for name in NAMES:
    bad = None
    for nbr, marks in W4:
        base = RESP4[(nbr, marks)][name]
        for p in PERMS4:
            key = relabel(nbr, marks, p)
            other = RESP4[key][name]
            if LEVEL.get(name) == "graph":
                if other != base:
                    bad = (nbr, marks, p, None)
                    break
            else:
                hit = next((v for v in range(N4) if other[p[v]] != base[v]), None)
                if hit is not None:
                    bad = (nbr, marks, p, hit)
                    break
        if bad:
            break
    row = {"obligation": name, "level": LEVEL.get(name, "node"),
           "permutation_equivariant": bad is None}
    if bad:
        row["counterexample"] = {
            "config": describe(bad[0], bad[1]),
            "permutation": list(bad[2]),
            "node": bad[3],
        }
    equi.append(row)
    print("  %-22s %-14s %s"
          % (name, bad is None,
             "-" if bad is None else
             "%s perm=%s" % ("".join(map(str, bad[1])), "".join(map(str, bad[2])))))
OUT["equivariance"] = equi

vals = [r["permutation_equivariant"] for r in equi]
assert any(vals), "no obligation is permutation-equivariant -- the descriptor is dead"
assert not all(vals), (
    "every obligation is permutation-equivariant, so the descriptor separates "
    "nothing and the rest of this file has no negative side")
for r in equi:
    if not r["permutation_equivariant"]:
        assert r.get("counterexample"), (
            "%s is called non-equivariant without an exhibited relabelling -- "
            "the descriptor must REFUTE, not merely fail to prove" % r["obligation"])
EQUI = {r["obligation"]: r["permutation_equivariant"] for r in equi}
assert EQUI["reach_1"] and not EQUI["lowest_partner_marked"], \
    "the matched equivariant/anchored pair has stopped separating"
print()
print("  Both anchored obligations are REFUTED with an exhibited relabelling,")
print("  not merely left unproven. lowest_partner_marked is the interesting")
print("  one: it reads the same incident set as reach_1 and differs only in")
print("  caring WHICH partner, which is exactly what a name buys.")


# ===========================================================================
print()
print("=" * 78)
print("2  ROUNDS, AS THE SMALLEST PROPAGATION DEPTH THAT DETERMINES THE ANSWER")
print("=" * 78)
print("  A node starts holding its own mark and, each round, updates from what")
print("  one access exposes. The round-r state reachable this way is the")
print("  colour below; the smallest r at which the obligation is a function of")
print("  it is SEARCHED, not assumed -- the analogue of the receptive field.")
print()

W5 = marked_world(N5)
KEY5 = [(nbr, marks) for nbr, marks in W5]
RESP5 = [responses(nbr, marks) for nbr, marks in W5]
ITEMS5 = len(W5) * N5

# ---------------------------------------------------------------------------
# THE ACCESS MENU. Five ways of describing what one place may look at while it
# updates. Deliberately no word for a message, an aggregation, a neighbourhood
# or a network appears in any of them -- these are descriptions of the world,
# not of an architecture.
# ---------------------------------------------------------------------------
ACCESSES = ["SELF", "INCIDENT_BAG", "INCIDENT_INDEXED", "POPULATION_BAG",
            "WHOLE_TABLE"]
# Ties in cost are broken by this DECLARED order and the tied set is reported
# alongside, so any tie can be inspected. The order is not a measurement:
# SELF is genuinely weaker than the rest, and WHOLE_TABLE genuinely stronger,
# but POPULATION_BAG and INCIDENT_BAG are incomparable -- more places, no
# relation -- and their order here is arbitrary. Nothing reported turns on it:
# every tie that occurs is at round 0, where SELF wins outright, and
# tied_at_min_cost is empty for every other obligation. Breaking ties
# alphabetically instead WOULD have mattered: it hands every zero-round
# obligation to INCIDENT_BAG, reading a preference for the expected answer
# straight into the result.
EXPOSES = {"SELF": 0, "POPULATION_BAG": 1, "INCIDENT_BAG": 2,
           "INCIDENT_INDEXED": 3, "WHOLE_TABLE": 4}
BANNED = ("message", "aggregat", "neighbour", "neighbor", "gnn", "network",
          "convol", "graph", "passing", "propagat")
for a in ACCESSES:
    for w in BANNED:
        assert w not in a.lower(), \
            "the candidate menu names the answer (%r contains %r)" % (a, w)


def exposure(access, nbr, colour, v, key):
    """What one place may read while it updates. Nothing else is available."""
    if access == "SELF":
        return ()
    if access == "INCIDENT_BAG":
        return tuple(sorted(colour[u] for u in nbr[v]))
    if access == "INCIDENT_INDEXED":
        return tuple(sorted((u, colour[u]) for u in nbr[v]))
    if access == "POPULATION_BAG":
        return tuple(sorted(colour))
    if access == "WHOLE_TABLE":
        return (v, key)
    raise ValueError(access)


def refine(access, world, keys, colours):
    """One round. Returns (new colours, number of update-table cells used).

    Colours are interned in SORTED signature order, so the identifiers do not
    depend on the order the corpus is walked. A receipt that carried raw
    identifiers would be reproducible only by accident; only counts are
    reported.
    """
    sigs = []
    seen = set()
    for ci in range(len(world)):
        nbr = world[ci][0]
        c = colours[ci]
        row = []
        for v in range(len(nbr)):
            s = (c[v], exposure(access, nbr, c, v, keys[ci]))
            row.append(s)
            seen.add(s)
        sigs.append(row)
    order = {s: i for i, s in enumerate(sorted(seen))}
    return [tuple(order[s] for s in row) for row in sigs], len(seen)


def initial(world):
    return [tuple(marks) for _, marks in world]


def determined(name, colours):
    """Is the obligation a function of the current colour?"""
    seen = {}
    if LEVEL.get(name) == "graph":
        for ci in range(len(colours)):
            k = tuple(sorted(colours[ci]))
            r = RESP5[ci][name]
            if k in seen and seen[k] != r:
                return False
            seen[k] = r
    else:
        for ci in range(len(colours)):
            row = RESP5[ci][name]
            c = colours[ci]
            for v in range(len(c)):
                if c[v] in seen and seen[c[v]] != row[v]:
                    return False
                seen[c[v]] = row[v]
    return True


MAXR = 8                                 # two rounds of headroom past stability
bag_colours = [initial(W5)]
bag_cells = [len(set(x for row in bag_colours[0] for x in row))]
for r in range(MAXR):
    nc, cells = refine("INCIDENT_BAG", W5, KEY5, bag_colours[-1])
    bag_colours.append(nc)
    bag_cells.append(cells)

counts = [len(set(x for row in cs for x in row)) for cs in bag_colours]
# A round-(r+1) colour determines the round-r colour, because the signature it
# was interned from contains it. So each round REFINES the last, and two
# consecutive rounds with the same class count are the same partition -- which
# is what makes a count comparison a sound stability test rather than a
# coincidence. Checked rather than assumed.
for r in range(MAXR):
    back = {}
    for ci in range(len(W5)):
        for v in range(N5):
            a, b = bag_colours[r + 1][ci][v], bag_colours[r][ci][v]
            assert back.setdefault(a, b) == b, \
                "round %d does not refine round %d, so a stable class count " \
                "would not imply a stable partition" % (r + 1, r)
STABLE_R = next(r for r in range(1, MAXR + 1) if counts[r] == counts[r - 1])
assert all(counts[r] == counts[STABLE_R] for r in range(STABLE_R, MAXR + 1)), \
    "the colour count moved again after it was called stable"
assert counts[0] < counts[STABLE_R], \
    "propagation refines nothing at all -- the world is too poor to test on"

print("  colour classes by round: %s   (stable from round %d)"
      % (counts, STABLE_R))
print()
print("  %-22s %-10s %s" % ("obligation", "rounds", "note"))
rounds_rows = []
for name in NAMES:
    r = next((r for r in range(MAXR + 1) if determined(name, bag_colours[r])),
             None)
    note = "local" if r is not None else "NOT a function of the colour at ANY round"
    rounds_rows.append({"obligation": name, "rounds_under_incident_bag": r})
    print("  %-22s %-10s %s" % (name, r, note))
# Named for the access it was measured under. NONE here means out of reach of
# THIS access at any round -- not out of reach of every machine. Section 5
# meets marked_and_company with a different access for 20 cells, and that
# contrast is a result, not a contradiction.
OUT["rounds_under_incident_bag"] = rounds_rows
ROUNDS = {x["obligation"]: x["rounds_under_incident_bag"] for x in rounds_rows}

assert ROUNDS["own_mark"] == 0
assert ROUNDS["reach_1"] == 1 and ROUNDS["reach_2"] == 2 and ROUNDS["reach_3"] == 3, \
    "the round count no longer matches the hop count in the obligation"
assert ROUNDS["odd_dist_3"] == 3 and ROUNDS["cap_dist_4"] == 3, \
    "the three obligations that must be matched on rounds no longer are"
assert ROUNDS["lowest_partner_marked"] is None and ROUNDS["is_node_0"] is None, \
    "an anchored obligation is now a function of an anonymous colour"
got = [x["rounds_under_incident_bag"] for x in rounds_rows
       if x["rounds_under_incident_bag"] is not None]
assert len(set(got)) > 2, "every obligation needs the same number of rounds"
assert None in [x["rounds_under_incident_bag"] for x in rounds_rows], \
    "nothing is out of reach, so the round count is not being tested"

# The "at ANY round" half is licensed, not assumed: the partition only ever
# refines, and it stops refining at STABLE_R, so an obligation not determined
# there is not determined at any larger r either.
assert bag_colours[STABLE_R] == bag_colours[MAXR], \
    "the colour partition is not actually frozen past the stable round"
print()
print("  The round count is read off the obligation: 1, 2 and 3 hops give 1, 2")
print("  and 3 rounds. Nothing about a depth was chosen. The two anchored")
print("  obligations come back as NONE rather than as a number, and that is")
print("  not a budget: the partition stops refining at round %d, so failing"
      % STABLE_R)
print("  there is failing at every larger round.")

# The bridge between "determined by the colour" and "expressible in r rounds"
# has two halves, and only one of them is a measurement.
#
#   REALISABLE (checked here). The colour is producible by a place that reads
#   nothing but its own state and the bag across its links. The gate is that
#   the same local view never yields two different next colours -- if the
#   interning had leaked anything configuration-specific, this fires. The
#   harvested tables are then replayed from round 0 with no access to the
#   corpus, and must reproduce the colouring exactly.
#
#   FINEST (argued, not measured). No r-round machine separates more than the
#   round-r colour, by induction on r: a machine's round-0 state is a function
#   of the mark, and its update reads only its own state and the bag, so its
#   round-(r+1) state is a function of the round-(r+1) signature. This is a
#   proof, not an enumeration. The two-state search in section 3 enumerates
#   actual machines and is the only independent check on it here.
LEMMA_R = 3
tables = []
cur = initial(W5)
for r in range(LEMMA_R):
    nxt, _c = refine("INCIDENT_BAG", W5, KEY5, cur)
    tbl = {}
    for ci in range(len(W5)):
        nbr = W5[ci][0]
        for v in range(N5):
            k = (cur[ci][v], tuple(sorted(cur[ci][u] for u in nbr[v])))
            assert tbl.setdefault(k, nxt[ci][v]) == nxt[ci][v], (
                "the same local view yields two different next states at round "
                "%d, so the colour is not producible by a local rule at all"
                % (r + 1))
    tables.append(tbl)
    cur = nxt
replay = initial(W5)
for tbl in tables:
    replay = [tuple(tbl[(replay[ci][v],
                         tuple(sorted(replay[ci][u] for u in W5[ci][0][v])))]
                    for v in range(N5))
              for ci in range(len(W5))]
assert replay == bag_colours[LEMMA_R], \
    "replaying the harvested rules does not reproduce the colouring, so the " \
    "colour is not what a machine of this shape would actually hold"
OUT["finest_state_lemma"] = {
    "rounds_checked": LEMMA_R,
    "colour_is_realisable_by_a_local_rule": True,
    "rule_table_sizes": [len(t) for t in tables],
    "no_machine_separates_more": "ARGUED BY INDUCTION, NOT ENUMERATED",
    "colour_classes_by_round": counts,
    "stable_round": STABLE_R,
}

# Anonymity: four of the five accesses never expose a place's own name. That is
# the graph analogue of "sharing asserts that position does not matter", and it
# is what forces the anchored obligations out of reach above -- so it is
# checked rather than left implicit.
empty = (tuple(() for _ in range(N5)), tuple(0 for _ in range(N5)))
anon = {}
for a in ACCESSES:
    col = [tuple(empty[1])]
    w, k = [empty], [empty]
    for _ in range(3):
        col, _c = refine(a, w, k, col)
    anon[a] = bool(col[0][0] == col[0][1])
OUT["anonymity"] = {"two_nodes_of_the_empty_configuration_stay_identical": anon}
for a in ("SELF", "INCIDENT_BAG", "INCIDENT_INDEXED", "POPULATION_BAG"):
    assert anon[a], "%s leaks a place's own name, which changes the twin" % a
assert not anon["WHOLE_TABLE"], \
    "the table no longer distinguishes two places, so it is not a table"


# ===========================================================================
print()
print("=" * 78)
print("3  CSR-1: ONE STATE PER DISTINCTION THAT MUST STILL BE MADE")
print("=" * 78)
print("  The carrier is not one state per answer reported. reach_3 and")
print("  odd_dist_3 need the same three rounds and report the same two values,")
print("  and they do not need the same carrier.")
print()


def run(nbr, marks, s0, upd, rounds):
    n = len(nbr)
    s = [s0[marks[v]] for v in range(n)]
    for _ in range(rounds):
        s = [upd(s[v], tuple(sorted(s[u] for u in nbr[v]))) for v in range(n)]
    return s


def upd_reach(a, ms):
    return 1 if (a == 1 or 1 in ms) else 0


def upd_odd(a, ms):
    # 0 = not reached, 1 = reached at an even distance, 2 = at an odd one.
    # The two branches cannot race: on the round a place leaves state 0, every
    # already-reached partner sits at distance exactly dist(v)-1, hence at one
    # and the same parity.
    if a != 0:
        return a
    if 1 in ms:
        return 2
    if 2 in ms:
        return 1
    return 0


def upd_cap(a, ms):
    return min(a, (min(ms) + 1) if ms else 4, 4)


MACHINES = {
    "reach_1": ((0, 1), upd_reach, (0, 1), 2),
    "reach_3": ((0, 1), upd_reach, (0, 1), 2),
    "odd_dist_3": ((0, 1), upd_odd, (0, 0, 1), 3),
    "cap_dist_4": ((4, 0), upd_cap, (0, 1, 2, 3, 4), 5),
}

print("  %-16s %-8s %-10s %-10s %-10s %s"
      % ("obligation", "rounds", "answers", "states", "bits", "verified on"))
carrier = []
for name in ("reach_1", "reach_3", "odd_dist_3", "cap_dist_4"):
    s0, upd, rho, k = MACHINES[name]
    R = ROUNDS[name]
    ok = True
    for ci in range(len(W5)):
        nbr, marks = W5[ci]
        s = run(nbr, marks, s0, upd, R)
        if tuple(rho[x] for x in s) != RESP5[ci][name]:
            ok = False
            break
    answers = len(set(x for ci in range(len(W5)) for x in RESP5[ci][name]))
    bits = (k - 1).bit_length()
    carrier.append({"obligation": name, "rounds": R, "answer_values": answers,
                    "states": k, "bits": bits, "verified": ok,
                    "configs_verified": len(W5)})
    print("  %-16s %-8d %-10d %-10d %-10d %s"
          % (name, R, answers, k, bits, "%d configs" % len(W5) if ok else "FAILED"))
OUT["carrier"] = carrier
CAR = {x["obligation"]: x for x in carrier}
for x in carrier:
    assert x["verified"], "%s: the exhibited machine does not meet it" % x["obligation"]
    assert x["states"] >= x["answer_values"], \
        "%s carries fewer states than it reports answers" % x["obligation"]
assert CAR["reach_3"]["rounds"] == CAR["odd_dist_3"]["rounds"] == CAR["cap_dist_4"]["rounds"], \
    "the three obligations are no longer matched on rounds, so a difference " \
    "in carrier width could be a difference in depth instead"
assert CAR["reach_3"]["answer_values"] == CAR["odd_dist_3"]["answer_values"], \
    "reach_3 and odd_dist_3 no longer report the same number of answers, so " \
    "the CSR-1 claim would be about the answer rather than the distinction"
assert CAR["odd_dist_3"]["states"] > CAR["odd_dist_3"]["answer_values"], \
    "odd_dist_3 no longer needs a state it never reports -- that gap IS CSR-1"

# ---------------------------------------------------------------------------
# The upper bounds above are exhibited. The lower bound for odd_dist_3 is
# searched: every two-state machine, at the round count derived in section 2,
# over a subcorpus of the same world. A machine on the full world restricts to
# one of these on the subcorpus, so finding none here proves there is none.
# ---------------------------------------------------------------------------
SUB = [(nbr, marks) for nbr, marks in W5 if max(len(x) for x in nbr) <= 2]
SUB_RESP = [responses(nbr, marks) for nbr, marks in SUB]
sub_answers = len(set(x for r in SUB_RESP for x in r["cap_dist_4"]))
assert sub_answers == 5, (
    "the search subcorpus does not realise every capped distance (%d of 5), "
    "so a machine could pass it without ever meeting the hard cases"
    % sub_answers)

DOM = [(a, m) for a in (0, 1)
       for m in ((), (0,), (1,), (0, 0), (0, 1), (1, 1))]
DIX = {d: i for i, d in enumerate(DOM)}
RHOS = [tuple(r) for r in itertools.product((0, 1), repeat=2)]
S0S = [tuple(s) for s in itertools.product((0, 1), repeat=2)]


def sim2(nbr, marks, s0, bits, rounds, keep=False):
    n = len(nbr)
    s = [s0[marks[v]] for v in range(n)]
    trail = [list(s)]
    for _ in range(rounds):
        s = [(bits >> DIX[(s[v], tuple(sorted(s[u] for u in nbr[v])))]) & 1
             for v in range(n)]
        if keep:
            trail.append(list(s))
    return trail if keep else s


def search_two_state(name, rounds):
    """Every two-state machine at exactly this round count. Exhaustive."""
    found = []
    for s0 in S0S:
        for bits in range(1 << len(DOM)):
            alive = list(RHOS)
            for ci in range(len(SUB)):
                nbr, marks = SUB[ci]
                s = sim2(nbr, marks, s0, bits, rounds)
                tgt = SUB_RESP[ci][name]
                alive = [r for r in alive
                         if all(r[s[v]] == tgt[v] for v in range(len(nbr)))]
                if not alive:
                    break
            if alive:
                found.append((s0, bits, alive[0]))
    return found


BOUND_R = 24


def search_two_state_any_round(name, max_rounds):
    """The same search, but a machine may read out at ANY round up to the bound.

    This is a BOUNDED statement and is reported as one. The valid round counts
    of a machine form an intersection of eventually periodic sets whose joint
    period is astronomically larger than this bound, so no unbounded claim is
    made from it.
    """
    pairs = [(R, r) for R in range(max_rounds + 1) for r in RHOS]
    found = 0
    for s0 in S0S:
        for bits in range(1 << len(DOM)):
            alive = list(pairs)
            for ci in range(len(SUB)):
                nbr, marks = SUB[ci]
                trail = sim2(nbr, marks, s0, bits, max_rounds, keep=True)
                tgt = SUB_RESP[ci][name]
                alive = [(R, r) for (R, r) in alive
                         if all(r[trail[R][v]] == tgt[v]
                                for v in range(len(nbr)))]
                if not alive:
                    break
            if alive:
                found += 1
    return found


pos = search_two_state("reach_3", 3)
neg = search_two_state("odd_dist_3", 3)
neg_bounded = search_two_state_any_round("odd_dist_3", BOUND_R)

print()
print("  two-state machines at 3 rounds, by exhaustion over %d machines on %d"
      % (len(S0S) * (1 << len(DOM)) * len(RHOS), len(SUB)))
print("  configurations of the same world:")
print("    reach_3     : %d found   (the search can succeed)" % len(pos))
print("    odd_dist_3  : %d found   (so its carrier is at least 3 states)" % len(neg))
print("    odd_dist_3  : %d found allowing readout at ANY round up to %d"
      % (neg_bounded, BOUND_R))
OUT["two_state_search"] = {
    "machines_enumerated": len(S0S) * (1 << len(DOM)) * len(RHOS),
    "subcorpus_configs": len(SUB),
    "rounds_pinned": 3,
    "reach_3_found": len(pos),
    "odd_dist_3_found_at_pinned_rounds": len(neg),
    "odd_dist_3_found_within_round_bound": neg_bounded,
    "round_bound": BOUND_R,
}
assert pos, (
    "the two-state search finds nothing even for reach_3, which HAS a "
    "two-state machine -- the searcher is broken and its negative is worthless")
assert not neg, \
    "a two-state machine now meets odd_dist_3 -- the CSR-1 separation is gone"
assert neg_bounded == 0, \
    "odd_dist_3 becomes two-state expressible at some other round count"
# the machine the search found must be the one that was exhibited
s0, bits, rho = pos[0]
assert all(
    tuple(rho[x] for x in sim2(nbr, marks, s0, bits, 3)) == r["reach_3"]
    for (nbr, marks), r in zip(SUB, SUB_RESP))

print()
print("  > reach_3 and odd_dist_3 need the same three rounds and report the")
print("  > same two answers. reach_3 carries 1 bit; odd_dist_3 carries 3")
print("  > states, because it must still tell 'not reached' from 'reached at")
print("  > an even distance' -- a distinction it never reports. CSR-1 counts")
print("  > the distinctions that must STILL be made, not the answers given.")


# ===========================================================================
print()
print("=" * 78)
print("4  THE BURDEN: ROUNDS x TRAFFIC x WIDTH, AND WHERE IT STOPS BUYING")
print("=" * 78)
print("  Both factors were computed from the obligation alone above: rounds in")
print("  section 2, width in section 3. The burden is what they cost.")
print()

SWEEP = [4, 6, 8, 12, 16, 24, 32, 48, 64]
print("  %-16s %-8s %-8s %-10s %s"
      % ("obligation", "rounds", "bits", "R x bits", "cheapest n in the sweep"))
burden = []
for name in ("reach_1", "reach_3", "odd_dist_3", "cap_dist_4"):
    R = ROUNDS[name]
    bits = CAR[name]["bits"]           # verified in section 3, not assumed
    product = R * bits
    rows = []
    cross = None
    for n in SWEEP:
        # a ring of n places: n links, each carrying one state each way, each
        # round. The alternative is to ship the whole configuration to one
        # place once and read the answer off a table there.
        local = R * 2 * n * bits
        ship = n * (n - 1) // 2 + n
        rows.append({"n": n, "local_bits": local, "ship_bits": ship,
                     "local_cheaper": local < ship})
        if cross is None and local < ship:
            cross = n
    burden.append({"obligation": name, "rounds": R, "bits": bits,
                   "rounds_times_bits": product, "crossover_n": cross,
                   "sweep": rows})
    print("  %-16s %-8d %-8d %-10d %s"
          % (name, R, bits, product, cross))
OUT["burden"] = burden

both = [b for b in burden
        if any(r["local_cheaper"] for r in b["sweep"])
        and any(not r["local_cheaper"] for r in b["sweep"])]
assert len(both) >= 2, (
    "fewer than two obligations show both regimes in the sweep, so there is "
    "no crossover to report -- only an assertion about one of them")
ordered = sorted(burden, key=lambda b: b["rounds_times_bits"])
xs = [b["crossover_n"] for b in ordered]
assert all(a is not None for a in xs), "an obligation never crosses in the sweep"
assert xs == sorted(xs), (
    "the crossover no longer orders with rounds x bits, so the burden is not "
    "being predicted by the two quantities the obligation fixed")
assert xs[0] < xs[-1], "every obligation crosses at the same size"

# Past the round at which the partition stops refining, more propagation buys
# nothing and still costs. Both halves measured.
gain = []
for r in range(MAXR + 1):
    met = sorted(n for n in NAMES if determined(n, bag_colours[r]))
    gain.append({"round": r, "obligations_met": len(met), "met": met,
                 "cumulative_cells": sum(bag_cells[1:r + 1])})
met_counts = [g["obligations_met"] for g in gain]
SAT_R = next(r for r in range(MAXR + 1) if met_counts[r] == met_counts[-1])
OUT["saturation"] = {"stable_round": STABLE_R, "saturating_round": SAT_R,
                     "by_round": gain}
print()
print("  %-8s %-18s %s" % ("round", "obligations met", "cells spent so far"))
for g in gain:
    print("  %-8d %-18d %d" % (g["round"], g["obligations_met"], g["cumulative_cells"]))
assert met_counts == sorted(met_counts), "an obligation stopped being met by more rounds"
assert met_counts[STABLE_R] == met_counts[-1], \
    "more rounds still buy expressiveness past the stable round"
assert met_counts[0] < met_counts[SAT_R], "rounds buy nothing anywhere"
assert SAT_R < MAXR, "the sweep never reaches saturation, so nothing is shown"
assert gain[-1]["cumulative_cells"] > gain[SAT_R]["cumulative_cells"], \
    "extra rounds past saturation are free, so there is no tension to report"
print()
print("  > Expressiveness saturates at round %d; the partition itself goes on"
      % SAT_R)
print("  > refining until round %d and the bill never stops. Every round past"
      % STABLE_R)
print("  > %d is pure cost, which is the price of not knowing the obligation's"
      % SAT_R)
print("  > round count in advance -- and section 2 is exactly how you know it.")


# ===========================================================================
print()
print("=" * 78)
print("5  NEUTRAL RECOVERY: NO WORD FOR A MESSAGE ANYWHERE IN THE MENU")
print("=" * 78)
print("  A candidate is (access, rounds). Access says what one place may read")
print("  while it updates: itself; the bag of states across its incident")
print("  links; those states tagged by which link; the bag of states of the")
print("  whole population; or the entire configuration. Cost is the number of")
print("  update-table cells the corpus actually forces, plus the readout.")
print()

recovery = {}
access_stable = {}
for a in ACCESSES:
    col = initial(W5)
    cells = 0
    prev = len(set(x for row in col for x in row))
    for r in range(MAXR + 1):
        if r:
            col, c = refine(a, W5, KEY5, col)
            cells += c
        nclr = len(set(x for row in col for x in row))
        for name in NAMES:
            if LEVEL.get(name) == "graph":
                ro = len(set(tuple(sorted(row)) for row in col))
            else:
                ro = nclr
            if determined(name, col) and (name, a) not in recovery:
                recovery[(name, a)] = {"rounds": r, "cost": cells + ro}
        if r and nclr == prev:
            access_stable[a] = r          # this access can refine no further
            break
        prev = nclr
    # Every access must reach a round past which its partition is frozen. That
    # is what licenses "this access never meets the obligation, at ANY round"
    # instead of "we stopped looking".
    assert a in access_stable, \
        "%s never stops refining within %d rounds, so no unreachability claim " \
        "about it is licensed" % (a, MAXR)
    if a == "WHOLE_TABLE":
        assert len(set(x for row in col for x in row)) == ITEMS5, \
            "the table does not separate every (configuration, place), so it " \
            "is not serving as a table"
OUT["access_stable_round"] = dict(sorted(access_stable.items()))

print("  %-22s %-20s %-7s %-10s %-14s %s"
      % ("obligation", "cheapest access", "rounds", "cells", "tied at cost",
         "also met by"))
rec_rows = []
for name in NAMES:
    cands = [(v["cost"], EXPOSES[a], a, v["rounds"]) for (n2, a), v
             in recovery.items() if n2 == name]
    cands.sort()
    assert cands, "%s is met by nothing in the menu, not even the table" % name
    cost, _rank, acc, r = cands[0]
    tied = sorted(a2 for c2, _k, a2, _r in cands if c2 == cost and a2 != acc)
    rec_rows.append({"obligation": name, "access": acc, "rounds": r,
                     "cells": cost, "tied_at_min_cost": tied,
                     "also_met_by": sorted(a2 for _c, _k, a2, _r in cands[1:])})
    print("  %-22s %-20s %-7d %-10d %-14s %s"
          % (name, acc, r, cost, ",".join(tied) if tied else "-",
             ",".join(sorted(a2 for _c, _k, a2, _r in cands[1:]))))
OUT["recovery"] = rec_rows
OUT["tie_break"] = ("cost first; ties broken toward the access that exposes "
                    "least, in the order " + " < ".join(
                        sorted(EXPOSES, key=lambda k: EXPOSES[k])) +
                    "; the tied set is reported in tied_at_min_cost")

winners = [x["access"] for x in rec_rows]
OUT["recovery_winner_counts"] = {a: winners.count(a) for a in ACCESSES}
assert len(set(winners)) == len(ACCESSES), (
    "not every access in the menu wins somewhere, so the menu is partly "
    "decoration and the search is not really choosing")
assert winners.count("INCIDENT_BAG") * 2 <= len(winners), (
    "the obvious answer wins a majority of the corpus -- that is what a "
    "rigged search looks like, not a derivation")
assert "SELF" in winners, \
    "the least-informed access never wins, so nothing checks that the search " \
    "declines to buy access it does not need"
assert "WHOLE_TABLE" in winners, \
    "the table never wins, so nothing in the corpus is beyond a local machine"
assert "POPULATION_BAG" in winners, \
    "the relation-free access never wins, so relational access is untested " \
    "against its own negative"
BY = {x["obligation"]: x for x in rec_rows}
assert BY["reach_1"]["access"] == "INCIDENT_BAG" and BY["reach_1"]["rounds"] == 1
assert BY["is_node_0"]["access"] == "WHOLE_TABLE", \
    "an anonymous access now serves an obligation anchored to a name"
assert BY["marked_and_company"]["access"] == "POPULATION_BAG", \
    "the relation-free obligation is no longer cheapest without the relation"
print()
print("  The object recovered for the reach obligations -- one rule over the")
print("  bag of states across a place's own links, applied everywhere, for a")
print("  number of rounds fixed by the obligation -- is message passing, and it")
print("  was selected by cost from a menu containing no such word.")
print()
print("  marked_and_company is the instructive failure. It is permutation-")
print("  equivariant and it is global, and the relational access cannot meet it")
print("  at any round: on a disconnected configuration a place never learns")
print("  the population. Permutation symmetry LICENSES a relational machine.")
print("  It does not make one sufficient -- the obligation's REACH has to match")
print("  the relation too, and equivariance says nothing about that.")


# ===========================================================================
print()
print("=" * 78)
print("6  THE NEGATIVE TWIN: KEEP THE INCIDENT SET, READ THE NAME")
print("=" * 78)
print("  reach_1 and lowest_partner_marked look at exactly the same places.")
print("  One asks how many are marked, the other asks which. Everything else")
print("  is held fixed.")
print()
twin = []
for name in ("reach_1", "lowest_partner_marked"):
    twin.append({"obligation": name,
                 "permutation_equivariant": EQUI[name],
                 "rounds_under_incident_bag": ROUNDS[name],
                 "met_by_incident_bag": (name, "INCIDENT_BAG") in recovery,
                 "met_by_incident_indexed": (name, "INCIDENT_INDEXED") in recovery,
                 "cheapest_access": BY[name]["access"]})
    t = twin[-1]
    print("  %-24s equivariant=%-7s rounds=%-6s bag=%-7s indexed=%s"
          % (name, t["permutation_equivariant"], t["rounds_under_incident_bag"],
             t["met_by_incident_bag"], t["met_by_incident_indexed"]))
OUT["negative_twin"] = twin
a, b = twin[0], twin[1]
assert a["permutation_equivariant"] and not b["permutation_equivariant"]
assert a["met_by_incident_bag"] and not b["met_by_incident_bag"], (
    "the bag now serves the anchored obligation, so the twin separates nothing")
assert b["met_by_incident_indexed"], \
    "even a name-reading access fails the anchored obligation -- the twin is " \
    "then about something other than the name"
print()
print("  > The advantage disappears exactly when the symmetry does, and the")
print("  > descriptor in section 1 predicted it BEFORE any machine was built.")
print("  A machine that pools its incident states is not merely inefficient on")
print("  lowest_partner_marked; it cannot express it at ANY round, because the")
print("  partition stops refining at round %d and it is not determined there."
      % STABLE_R)


# ===========================================================================
print()
print("=" * 78)
print("7  THE CEILING: AN OBLIGATION NO ROUND COUNT CAN MEET")
print("=" * 78)
print("  Rounds bought reach in section 2 and saturated in section 4. Here is")
print("  what saturation costs: two graphs that stay merged at every round, and")
print("  an obligation that must tell them apart.")
print()


def g_connected(nbr):
    n = len(nbr)
    seen = {0}
    cur = [0]
    while cur:
        nxt = []
        for v in cur:
            for u in nbr[v]:
                if u not in seen:
                    seen.add(u)
                    nxt.append(u)
        cur = nxt
    return 1 if len(seen) == n else 0


def g_triangle(nbr):
    n = len(nbr)
    for i in range(n):
        for j in nbr[i]:
            if j <= i:
                continue
            for k in nbr[j]:
                if k > j and k in nbr[i]:
                    return 1
    return 0


def g_leafy(nbr):
    """Some place has at least two partners with exactly one partner each."""
    for v in range(len(nbr)):
        if sum(1 for u in nbr[v] if len(nbr[u]) == 1) >= 2:
            return 1
    return 0


GOBL = {"connected": g_connected, "has_triangle": g_triangle, "leafy": g_leafy}


def colour_rounds(gs, max_rounds):
    """Colours by round over a corpus of unmarked graphs, interned in sorted
    signature order so the identifiers do not depend on the walk order."""
    n = len(gs[0])
    cur = [tuple(0 for _ in range(n)) for _ in gs]
    out = [cur]
    for _ in range(max_rounds):
        seen = set()
        rows = []
        for gi, nbr in enumerate(gs):
            c = cur[gi]
            row = [(c[v], tuple(sorted(c[u] for u in nbr[v]))) for v in range(n)]
            rows.append(row)
            seen.update(row)
        order = {s: i for i, s in enumerate(sorted(seen))}
        cur = [tuple(order[s] for s in row) for row in rows]
        out.append(cur)
    return out


def blind_pairs(gs, cols, values):
    """Graphs with the same colour histogram and different obligation value."""
    seen = {}
    for gi in range(len(gs)):
        k = tuple(sorted(cols[gi]))
        if k in seen:
            j, val = seen[k]
            if val != values[gi]:
                return (j, gi)
        else:
            seen[k] = (gi, values[gi])
    return None


ceiling = {}
for n in (3, 4, 5, 6):
    gs = graphs(n)
    cols = colour_rounds(gs, n + 2)
    # Same refinement check as section 2: each round determines the last, so a
    # repeated class count is a frozen partition and not a coincidence.
    for r in range(n + 2):
        back = {}
        for gi in range(len(gs)):
            for v in range(n):
                a, b = cols[r + 1][gi][v], cols[r][gi][v]
                assert back.setdefault(a, b) == b, \
                    "n=%d: round %d does not refine round %d" % (n, r + 1, r)
    stable = next(r for r in range(1, n + 2)
                  if len(set(x for row in cols[r] for x in row))
                  == len(set(x for row in cols[r - 1] for x in row)))
    assert cols[stable] == cols[n + 2], \
        "n=%d: the colouring is not frozen past the round called stable" % n
    per = {}
    for name, f in GOBL.items():
        vals = [f(g) for g in gs]
        assert 0 < sum(vals) < len(vals), \
            "%s is constant on the %d-node world, so it tests nothing" % (name, n)
        at = {}
        for r in range(n + 3):
            at[r] = blind_pairs(gs, cols[min(r, n + 2)], vals) is not None
        pair = blind_pairs(gs, cols[stable], vals)
        per[name] = {
            "blind_at_stable_round": pair is not None,
            "blind_by_round": [at[r] for r in range(n + 3)],
        }
        if pair is not None:
            i, j = pair
            # "blind at round r" above only says SOME pair is merged at r, and
            # at round 0 every graph is. The claim that matters is about THIS
            # pair, so it is measured for this pair at every round.
            per[name]["exhibited_pair_merged_by_round"] = [
                tuple(sorted(cols[r][i])) == tuple(sorted(cols[r][j]))
                for r in range(n + 3)]
            per[name]["pair"] = [describe(gs[i]), describe(gs[j])]
            per[name]["pair_values"] = [vals[i], vals[j]]
            iso = any(relabel(gs[i], tuple(0 for _ in range(n)), p)[0]
                      == tuple(tuple(sorted(x)) for x in gs[j])
                      for p in itertools.permutations(range(n)))
            per[name]["pair_isomorphic"] = iso
            per[name]["pair_degrees"] = [
                sorted(len(x) for x in gs[i]), sorted(len(x) for x in gs[j])]
    ceiling[n] = {"graphs": len(gs), "stable_round": stable, "obligations": per}
    print("  n=%d  %5d graphs  stable at round %d   %s"
          % (n, len(gs), stable,
             "  ".join("%s=%s" % (k, "BLIND" if per[k]["blind_at_stable_round"]
                                  else "determined")
                       for k in sorted(per))))
OUT["ceiling"] = ceiling

for n in (3, 4, 5):
    assert not ceiling[n]["obligations"]["connected"]["blind_at_stable_round"], \
        "a blind pair for connectivity appears at %d nodes" % n
c6 = ceiling[6]["obligations"]
assert c6["connected"]["blind_at_stable_round"], \
    "connectivity is now determined by the colouring at 6 nodes -- either the " \
    "world shrank or the finder stopped firing"
assert c6["has_triangle"]["blind_at_stable_round"], \
    "the second blind obligation is gone, so the finder has only one hit"
assert not c6["leafy"]["blind_at_stable_round"], (
    "the matched positive is now blind too, so this section says 'nothing is "
    "expressible' rather than 'this is where the ceiling is'")
assert c6["leafy"]["blind_by_round"][1], (
    "leafy is already determined after one round, so it is not matched with "
    "the negatives on depth")
assert not c6["leafy"]["blind_by_round"][2], \
    "leafy is no longer determined at two rounds"
assert c6["connected"]["pair_isomorphic"] is False, \
    "the exhibited pair is isomorphic, so the colouring is right to merge it"
assert all(c6["connected"]["exhibited_pair_merged_by_round"]), \
    "the exhibited pair separates at some round, so it is not a ceiling"
assert all(c6["has_triangle"]["exhibited_pair_merged_by_round"])
assert len(c6["connected"]["exhibited_pair_merged_by_round"]) > ceiling[6]["stable_round"], \
    "the per-round merge check stops before the colouring freezes, so it does " \
    "not cover every round"
assert c6["connected"]["pair_degrees"][0] == c6["connected"]["pair_degrees"][1], \
    "the exhibited pair differs in degree sequence, which one round separates"
assert c6["connected"]["pair_values"] == [1, 0] or \
    c6["connected"]["pair_values"] == [0, 1]

p = c6["connected"]["pair"]
print()
print("  The pair, found by grouping all 32768 six-node graphs on their stable")
print("  colouring, not chosen:")
print("    A  edges %s  connected=%d" % (p[0]["edges"], c6["connected"]["pair_values"][0]))
print("    B  edges %s  connected=%d" % (p[1]["edges"], c6["connected"]["pair_values"][1]))
print("    degree sequences %s and %s, non-isomorphic by exhausting all %d"
      % (c6["connected"]["pair_degrees"][0], c6["connected"]["pair_degrees"][1], 720))
print("    relabellings.")
print()
print("  > This is the strongest statement in the file and it is a negative.")
print("  > Any r-round machine's output is a function of the round-r colour,")
print("  > the colouring only ever refines, and it is frozen from round %d. The"
      % ceiling[6]["stable_round"])
print("  > pair is merged at every round, so NO number of rounds separates it.")
print("  > Connectivity and triangle-containment are therefore out of reach of")
print("  > the family derived above -- not expensive, unreachable.")
print()
print("  leafy is the matched positive: same world, same kind of answer, and")
print("  it needs two rounds rather than one -- and it IS determined. The")
print("  ceiling is a property of the obligation, not of the world.")
print()
print("  Six nodes is where this starts. Connectivity is determined by the")
print("  colouring at 3, 4 and 5 nodes, checked by the same finder that fires")
print("  twice at 6.")

OUT["falsifier"] = (
    "Exhibit a permutation-equivariant obligation on these worlds whose round "
    "count is smaller than the hop count it names; or a two-state machine "
    "meeting odd_dist_3 at three rounds (which would collapse CSR-1 onto the "
    "answer alphabet); or a pair of six-node graphs with the same stable "
    "colouring that some round count separates; or an anchored obligation met "
    "by an anonymous access. The subcorpus used for the machine search is a "
    "SUBSET of the world, so a machine failing there fails everywhere -- but a "
    "machine FOUND there must still be verified on the whole world, and is.")

print()
print("=" * 78)
print("all assertions held")
print("=" * 78)

with open("microscopes/results/STAGE_MESSAGE_PASSING_V1.json", "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)

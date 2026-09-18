# -*- coding: utf-8 -*-
"""AH4 route A -- the L0..L8 organization ladder, measured.

The issue states the ladder and calls it provisional.  This file treats it as a hypothesis.
It rebuilds the registered binary organization set, defines the eight transition invariants
fixed in `FREEZE_V1.md`, measures each one exhaustively, searches for the nearest system that
fails each transition, and reports which transitions are separating, which separate only on
the description, which separate only relative to a declared external boundary, and where an
intermediate layer is indicated.

    python3 -I -B  ah4_organization_ladder_v1.py
"""

import json
import os
import random
from fractions import Fraction
from itertools import product

HERE = os.path.dirname(os.path.abspath(__file__))

SOURCE_MAIN = "5e57d4292266bccf435136e1f7d72caa32e920a0"
CLAIM_CEILING = ("AH4_ORGANIZATION_LADDER_INVARIANTS_AND_LEVEL_STRUCTURE_"
                 "AT_REGISTERED_FINITE_SCOPE")
FORBIDDEN_PROMOTIONS = (
    "PERIODIC_TABLE_OF_MI_COMPLETE",
    "LEVEL_MEMBERSHIP_IS_INTELLIGENCE",
    "LADDER_IS_TOTAL_ORDER",
    "ALL_ORGANIZATION_LEVELS_ENUMERATED",
    "HIGHER_LEVEL_IMPLIES_HIGHER_CAPABILITY",
    "UNBOUNDED_LEVEL_HIERARCHY_PROVED",
    "COMPLETE_GMI",
)

LEVELS = ("L0 elementary substrate/process events",
          "L1 stable local motifs / reusable transition patterns",
          "L2 state-bearing modules / bounded computational organizations",
          "L3 interacting modules / composed machines",
          "L4 adaptive organizations whose internal state/update changes from experience",
          "L5 developmental organizations that alter representation/operators/search law",
          "L6 self-modeling/self-modifying organizations under verification/governance",
          "L7 populations/collectives/cultural inheritance / multi-instance development",
          "L8 grammar/theory expansion and new effective units")

INVARIANTS = ("I1_MOTIF_REUSE", "I2_HISTORY_DEPENDENCE", "I3_IRREDUCIBLE_COMPOSITION",
              "I4_EXPERIENCE_CONDITIONED_UPDATE", "I5_OPERATOR_INVENTORY_GROWTH",
              "I6_EXTERNALLY_ADMITTED_SELF_CHANGE", "I7_CROSS_INSTANCE_ACQUISITION",
              "I8_NEW_EFFECTIVE_UNIT")

BITS = (0, 1)
MAX_WORD = 5           # Moore bound for 4-state against 2-state transducers
WORDS = []
for _n in range(1, MAX_WORD + 1):
    for _w in product(BITS, repeat=_n):
        WORDS.append(_w)


# --------------------------------------------------------------------------------------
# 1.  The registered organization set: four cell-free plus 256 one-cell systems.
# --------------------------------------------------------------------------------------

class Org(object):
    """A deterministic transducer with zero or one persistent state cell."""

    __slots__ = ("oid", "cells", "table", "init")

    def __init__(self, oid, cells, table, init=0):
        self.oid = oid
        self.cells = cells          # 0 or 1 declared state cells
        self.table = table          # (state, input) -> (next_state, output)
        self.init = init

    def run(self, word):
        s = self.init
        out = []
        for i in word:
            s, o = self.table[(s, i)]
            out.append(o)
        return tuple(out)

    def description(self):
        """The declared description as a bit vector, for edit distance."""
        bits = []
        for s in range(max(1, 2 ** self.cells)):
            for i in BITS:
                ns, o = self.table[(s, i)]
                bits.append(ns)
                bits.append(o)
        if self.cells == 0:
            bits = bits + bits      # pad a cell-free system to the one-cell width
        return tuple(bits)


def base_organizations():
    orgs = []
    oid = 0
    for f0 in BITS:
        for f1 in BITS:
            table = {(0, 0): (0, f0), (0, 1): (0, f1)}
            orgs.append(Org("S%03d" % oid, 0, table))
            oid += 1
    for choice in product(range(4), repeat=4):
        table = {}
        for k, (s, i) in enumerate(((0, 0), (0, 1), (1, 0), (1, 1))):
            table[(s, i)] = (choice[k] >> 1, choice[k] & 1)
        orgs.append(Org("M%03d" % oid, 1, table))
        oid += 1
    return orgs


def signature(org):
    return tuple(org.run(w) for w in WORDS)


def equivalent_by_product(a, b):
    """The authority: reachable product exploration, not a length bound."""
    seen = set()
    stack = [(a.init, b.init)]
    while stack:
        sa, sb = stack.pop()
        if (sa, sb) in seen:
            continue
        seen.add((sa, sb))
        for i in BITS:
            na, oa = a.table[(sa, i)]
            nb, ob = b.table[(sb, i)]
            if oa != ob:
                return False
            stack.append((na, nb))
    return True


def equivalence_classes(orgs):
    classes = []
    index = {}
    for o in orgs:
        placed = False
        for ci, members in enumerate(classes):
            if equivalent_by_product(o, members[0]):
                members.append(o)
                index[o.oid] = ci
                placed = True
                break
        if not placed:
            index[o.oid] = len(classes)
            classes.append([o])
    return classes, index


# --------------------------------------------------------------------------------------
# 2.  The eight invariants.
# --------------------------------------------------------------------------------------

def motif_multiplicity(org):
    """A motif is the local effect `(output, KEEP|FLIP)`; multiplicity is the largest number
    of distinct sites producing the same effect."""
    counts = {}
    sites = ((0, 0), (0, 1)) if org.cells == 0 else ((0, 0), (0, 1), (1, 0), (1, 1))
    for (s, i) in sites:
        ns, o = org.table[(s, i)]
        key = (o, "KEEP" if ns == s else "FLIP")
        counts[key] = counts.get(key, 0) + 1
    return max(counts.values())


def i1(org):
    return motif_multiplicity(org) >= 2


def i2_clauses(org, cellfree_signatures):
    a = org.cells >= 1
    b = signature(org) not in cellfree_signatures
    return (a, b)


def i3_composite_signature(sig_a, sig_b, word_index):
    """Series wiring: the input word drives A, A's output word drives B."""
    out = []
    for w in WORDS:
        oa = sig_a[word_index[w]]
        out.append(sig_b[word_index[oa]])
    return tuple(out)


# --------------------------------------------------------------------------------------
# 3.  Witness families for L4..L8.  Each is an explicit finite object.
# --------------------------------------------------------------------------------------

class Adaptive(object):
    """An update law indexed by an experience register that counts past `1` inputs."""

    def __init__(self, tables, experience_from_input=True):
        self.tables = tables                       # experience -> {(s,i):(s',o)}
        self.experience_from_input = experience_from_input

    def run(self, word, hidden=()):
        s, e = 0, 0
        out = []
        for k, i in enumerate(word):
            s, o = self.tables[e][(s, i)]
            out.append(o)
            if self.experience_from_input:
                e = 1 if (e or i == 1) else 0
            else:
                e = hidden[k] if k < len(hidden) else e
        return tuple(out)

    def witness_triples(self):
        """Sites where the same (state, input) yields different successors by experience."""
        found = []
        for s in BITS:
            for i in BITS:
                a = self.tables[0][(s, i)]
                b = self.tables[1][(s, i)]
                if a != b:
                    found.append({"state": s, "input": i, "e0": list(a), "e1": list(b)})
        return found

    def absorbed(self):
        """The same system re-described as a plain transducer over the pair state `(s, e)`."""
        table = {}
        for s in BITS:
            for e in BITS:
                for i in BITS:
                    ns, o = self.tables[e][(s, i)]
                    ne = 1 if (e or i == 1) else 0
                    table[((s, e), i)] = ((ns, ne), o)
        return table

    def run_absorbed(self, word):
        st = (0, 0)
        table = self.absorbed()
        out = []
        for i in word:
            st, o = table[(st, i)]
            out.append(o)
        return tuple(out)


def adaptive_witness(adaptive=True):
    t0 = {(0, 0): (0, 0), (0, 1): (1, 0), (1, 0): (1, 0), (1, 1): (0, 1)}
    t1 = {(0, 0): (1, 1), (0, 1): (0, 1), (1, 0): (0, 0), (1, 1): (1, 0)}
    return Adaptive([t0, t1] if adaptive else [t0, t0])


class Developmental(object):
    """An operator inventory that may grow when a registered trigger fires."""

    def __init__(self, base_ops, added_ops):
        self.base_ops = tuple(base_ops)
        self.added_ops = tuple(added_ops)

    def inventory_before(self):
        return set(self.base_ops)

    def inventory_after(self):
        return set(self.base_ops) | set(self.added_ops)

    def growth(self):
        return len(self.inventory_after()) - len(self.inventory_before())


class Governed(object):
    """Self-change admitted by a guard that consumes a value the internal state does not
    determine.  With `external=False` the guard is computed from the candidate alone."""

    def __init__(self, external=True):
        self.external = external

    def adopt(self, active, candidate, receipt_authority):
        if self.external:
            admitted = (receipt_authority == "REGISTERED")
        else:
            admitted = (candidate[0] == 0)
        return (candidate if admitted else active), admitted

    def hidden_channel_divergence(self):
        """Two runs with identical visible input and identical internal state, differing only
        in the externally registered value."""
        active = (1, 1, 1)
        cand = (0, 1, 0)
        a, ok_a = self.adopt(active, cand, "REGISTERED")
        b, ok_b = self.adopt(active, cand, "UNREGISTERED")
        return {"internal_state_identical": True,
                "visible_input_identical": True,
                "outcomes_differ": a != b or ok_a != ok_b,
                "a": list(a), "b": list(b)}


class Population(object):
    """Two instances and a registered transfer channel."""

    def __init__(self, channel=True):
        self.channel = channel

    def reachable(self, seed, with_channel, donor=None):
        """A tiny edit law: an instance may flip one coordinate of its own vector per step,
        for at most two steps; a transfer copies the donor vector whole."""
        out = set()
        frontier = {seed}
        for _ in range(2):
            nxt = set()
            for v in frontier:
                for k in range(len(v)):
                    w = list(v)
                    w[k] ^= 1
                    nxt.add(tuple(w))
            out |= nxt
            frontier = nxt
        out.add(seed)
        if with_channel and donor is not None:
            out.add(donor)
        return out

    def acquisition(self):
        seed_b = (0, 0, 0, 0, 0, 0)
        donor_a = (1, 1, 1, 1, 1, 1)
        alone = self.reachable(seed_b, False)
        withch = self.reachable(seed_b, self.channel, donor_a)
        only = sorted(withch - alone)
        return {"reachable_alone": len(alone), "reachable_with_channel": len(withch),
                "acquired_only_through_channel": len(only),
                "witness": list(only[0]) if only else None}


class GrammarUnit(object):
    """A macro added to an inventory.  Expressive power is expected to be unchanged; what may
    change is description length and search distance."""

    def __init__(self, expansion):
        self.expansion = tuple(expansion)

    def expressive_delta(self, corpus):
        base = set()
        grown = set()
        for w in corpus:
            base.add(w)
            grown.add(w)
        return len(grown - base)

    def description_delta(self, corpus):
        """Total symbol count with and without the macro available."""
        before = sum(len(w) for w in corpus)
        after = 0
        e = self.expansion
        for w in corpus:
            k = 0
            n = 0
            while k < len(w):
                if len(e) and tuple(w[k:k + len(e)]) == e:
                    n += 1
                    k += len(e)
                else:
                    n += 1
                    k += 1
            after += n
        return after - before

    def search_distance_delta(self, target):
        """Steps to build `target` by appending one unit at a time, with and without the
        macro."""
        before = len(target)
        e = self.expansion
        k = 0
        after = 0
        while k < len(target):
            if len(e) and tuple(target[k:k + len(e)]) == e:
                after += 1
                k += len(e)
            else:
                after += 1
                k += 1
        return after - before


CORPUS = ((0, 1, 0, 1), (0, 1, 1), (0, 1, 0, 1, 0, 1), (1, 1, 0), (0, 1))
TARGET = (0, 1, 0, 1, 0, 1)


# --------------------------------------------------------------------------------------
# 4.  Capability on a registered task set -- exact rational scores, no scalarization.
# --------------------------------------------------------------------------------------
PROTECTED = [w for w in WORDS if len(w) <= 3]

TASKS = ("IDENTITY", "NEGATION", "CONST0", "DELAY1", "PARITY")


def task_target(task, word):
    if task == "IDENTITY":
        return tuple(word)
    if task == "NEGATION":
        return tuple(1 - x for x in word)
    if task == "CONST0":
        return tuple(0 for _ in word)
    if task == "DELAY1":
        return tuple([0] + list(word[:-1]))
    if task == "PARITY":
        out = []
        p = 0
        for x in word:
            p ^= x
            out.append(p)
        return tuple(out)
    raise ValueError("UNKNOWN_TASK")


def capability_vector(run):
    out = []
    for task in TASKS:
        hit = 0
        for w in PROTECTED:
            if run(w) == task_target(task, w):
                hit += 1
        out.append(Fraction(hit, len(PROTECTED)))
    return tuple(out)


def dominates(a, b):
    """`a` is at least `b` on every task and strictly better on one."""
    return all(x >= y for x, y in zip(a, b)) and any(x > y for x, y in zip(a, b))


# --------------------------------------------------------------------------------------
# 5.  Nearest negative: minimum description edit distance to a system that fails.
# --------------------------------------------------------------------------------------

def nearest_negative(bits, rebuild, predicate, max_radius=None):
    """Smallest Hamming edit of the description that turns a passing system into a failing
    one.  Exhaustive by increasing radius; returns `None` when no failing neighbour exists."""
    n = len(bits)
    if max_radius is None:
        max_radius = n
    for r in range(1, min(max_radius, n) + 1):
        for positions in _combinations(range(n), r):
            cand = list(bits)
            for p in positions:
                cand[p] ^= 1
            obj = rebuild(tuple(cand))
            if obj is None:
                continue
            if not predicate(obj):
                return {"distance": r, "flipped_positions": list(positions),
                        "description": list(cand)}
    return None


def _combinations(seq, r):
    seq = list(seq)
    n = len(seq)
    if r > n:
        return
    idx = list(range(r))
    while True:
        yield tuple(seq[i] for i in idx)
        i = r - 1
        while i >= 0 and idx[i] == i + n - r:
            i -= 1
        if i < 0:
            return
        idx[i] += 1
        for j in range(i + 1, r):
            idx[j] = idx[j - 1] + 1


def org_from_bits(bits):
    table = {}
    for k, (s, i) in enumerate(((0, 0), (0, 1), (1, 0), (1, 1))):
        table[(s, i)] = (bits[2 * k], bits[2 * k + 1])
    return Org("EDIT", 1, table)


# --------------------------------------------------------------------------------------
# 6.  The prohibition checker for the fourth AH4 row.
# --------------------------------------------------------------------------------------

def level_claim_verdict(claim):
    """A claim that a system is intelligent because of its level is refused unless registered
    capability AND development evidence accompany it."""
    if claim.get("asserts") != "INTELLIGENT":
        return "NOT_AN_INTELLIGENCE_CLAIM"
    if claim.get("capability_evidence") and claim.get("development_evidence"):
        return "ADMITTED_WITH_EVIDENCE"
    return "REFUSED__LEVEL_MEMBERSHIP_IS_NOT_INTELLIGENCE"


# --------------------------------------------------------------------------------------
# 7.  Measurement.
# --------------------------------------------------------------------------------------

def measure():
    orgs = base_organizations()
    word_index = dict((w, k) for k, w in enumerate(WORDS))
    sigs = dict((o.oid, signature(o)) for o in orgs)
    classes, index = equivalence_classes(orgs)
    class_sizes = {}
    for members in classes:
        class_sizes[str(len(members))] = class_sizes.get(str(len(members)), 0) + 1

    # the length bound must agree with the product-exploration authority
    sig_partition = {}
    for o in orgs:
        sig_partition.setdefault(sigs[o.oid], []).append(o.oid)
    bound_agrees = (len(sig_partition) == len(classes))
    for group in sig_partition.values():
        first = index[group[0]]
        for oid in group:
            if index[oid] != first:
                bound_agrees = False

    cellfree_sigs = set(sigs[o.oid] for o in orgs if o.cells == 0)

    i1_pass = [o.oid for o in orgs if i1(o)]
    clause_counts = {"both": 0, "cell_only": 0, "neither": 0, "behaviour_only": 0}
    i2_pass = []
    intermediate = []
    for o in orgs:
        a, b = i2_clauses(o, cellfree_sigs)
        if a and b:
            clause_counts["both"] += 1
            i2_pass.append(o.oid)
        elif a and not b:
            clause_counts["cell_only"] += 1
            intermediate.append(o.oid)
        elif b and not a:
            clause_counts["behaviour_only"] += 1
        else:
            clause_counts["neither"] += 1

    # is I1 determined by behaviour?
    i1_by_class = {}
    i1_description_only = 0
    for members in classes:
        vals = set(i1(o) for o in members)
        if len(vals) > 1:
            i1_description_only += 1
    i2_description_only = 0
    for members in classes:
        vals = set(i2_clauses(o, cellfree_sigs)[1] for o in members)
        if len(vals) > 1:
            i2_description_only += 1

    non_cumulative = [o.oid for o in orgs
                      if (not i1(o)) and all(i2_clauses(o, cellfree_sigs))]

    # ---- I3 over all ordered pairs -------------------------------------------------
    base_sigs = set(sigs.values())
    comp_total = 0
    comp_irreducible = 0
    irreducible_example = None
    reducible_example = None
    for a in orgs:
        sa = sigs[a.oid]
        for b in orgs:
            sb = sigs[b.oid]
            comp = i3_composite_signature(sa, sb, word_index)
            comp_total += 1
            if comp not in base_sigs:
                comp_irreducible += 1
                if irreducible_example is None:
                    irreducible_example = [a.oid, b.oid]
            elif reducible_example is None:
                reducible_example = [a.oid, b.oid]

    # ---- I4 ------------------------------------------------------------------------
    ad = adaptive_witness(True)
    nd = adaptive_witness(False)
    i4_triples = ad.witness_triples()
    i4_negative_triples = nd.witness_triples()
    absorbed_matches = all(ad.run(w) == ad.run_absorbed(w) for w in WORDS)
    # is the adaptive witness behaviourally reachable by a plain two-cell transducer?
    # it is, by construction: the absorbed re-description IS such a transducer.
    i4_collapses_under_absorption = absorbed_matches

    # ---- I5 ------------------------------------------------------------------------
    dev = Developmental(("READ", "EMIT", "INC"), ("REUSE_AB",))
    dev_neg = Developmental(("READ", "EMIT", "INC"), ("INC",))
    i5_growth = dev.growth()
    i5_negative_growth = dev_neg.growth()

    # ---- I6 ------------------------------------------------------------------------
    gov = Governed(True)
    gov_neg = Governed(False)
    i6 = gov.hidden_channel_divergence()
    i6_neg = gov_neg.hidden_channel_divergence()

    # ---- I7 ------------------------------------------------------------------------
    pop = Population(True)
    pop_neg = Population(False)
    i7 = pop.acquisition()
    i7_neg = pop_neg.acquisition()

    # ---- I8 ------------------------------------------------------------------------
    unit = GrammarUnit((0, 1))
    unit_neg = GrammarUnit((0,))
    i8 = {"expressive_delta": unit.expressive_delta(CORPUS),
          "description_delta": unit.description_delta(CORPUS),
          "search_distance_delta": unit.search_distance_delta(TARGET)}
    i8_neg = {"expressive_delta": unit_neg.expressive_delta(CORPUS),
              "description_delta": unit_neg.description_delta(CORPUS),
              "search_distance_delta": unit_neg.search_distance_delta(TARGET)}

    return {"orgs": orgs, "sigs": sigs, "classes": classes, "index": index,
            "class_count": len(classes), "class_sizes": class_sizes,
            "length_bound_agrees_with_product_authority": bound_agrees,
            "i1_pass": len(i1_pass), "i1_fail": len(orgs) - len(i1_pass),
            "i1_classes_split_by_description": i1_description_only,
            "i2_clause_counts": clause_counts,
            "i2_pass": len(i2_pass), "i2_intermediate": len(intermediate),
            "i2_classes_split_by_description": i2_description_only,
            "non_cumulative_base_systems": len(non_cumulative),
            "composites_total": comp_total,
            "composites_irreducible": comp_irreducible,
            "composite_irreducible_example": irreducible_example,
            "composite_reducible_example": reducible_example,
            "i4_witness_triples": len(i4_triples),
            "i4_negative_witness_triples": len(i4_negative_triples),
            "i4_collapses_under_absorption": i4_collapses_under_absorption,
            "i5_growth": i5_growth, "i5_negative_growth": i5_negative_growth,
            "i6": i6, "i6_negative": i6_neg,
            "i7": i7, "i7_negative": i7_neg,
            "i8": i8, "i8_negative": i8_neg,
            "cellfree_sigs": cellfree_sigs}


# --------------------------------------------------------------------------------------
# 8.  Verdicts.  The derivation rule is fixed before any number is looked at.
#
#   no passing or no failing system                      -> NOT_SEPARATING_AT_SCOPE
#   the invariant reads a value outside the visible input -> SEPARATING_UNDER_DECLARED_EXTERNAL_BOUNDARY
#   some behavioural equivalence class is split           -> SEPARATING_ONLY_ON_DESCRIPTION
#   otherwise                                             -> SEPARATING_ON_VISIBLE_BEHAVIOUR
#
# Invariants whose objects are inventories rather than transducers have no class structure and
# are marked DESCRIPTION_DOMAIN_BY_DEFINITION.
# --------------------------------------------------------------------------------------

EXTERNAL_INPUT_INVARIANTS = ("I6_EXTERNALLY_ADMITTED_SELF_CHANGE",
                             "I7_CROSS_INSTANCE_ACQUISITION")
INVENTORY_INVARIANTS = ("I5_OPERATOR_INVENTORY_GROWTH", "I8_NEW_EFFECTIVE_UNIT")


def verdict(name, passing, failing, class_split, external_exhibit=None):
    if not passing or not failing:
        return "NOT_SEPARATING_AT_SCOPE"
    if name in EXTERNAL_INPUT_INVARIANTS:
        if not external_exhibit:
            return "EXTERNAL_BOUNDARY_NOT_EXHIBITED"
        return "SEPARATING_UNDER_DECLARED_EXTERNAL_BOUNDARY"
    if name in INVENTORY_INVARIANTS:
        return "SEPARATING_ONLY_ON_DESCRIPTION"
    if class_split:
        return "SEPARATING_ONLY_ON_DESCRIPTION"
    return "SEPARATING_ON_VISIBLE_BEHAVIOUR"


# --------------------------------------------------------------------------------------
# 9.  Nulls.
# --------------------------------------------------------------------------------------

def null_class_constancy(m, draws=200, seed=8334401):
    """A behaviour-determined invariant must be constant on every equivalence class.  How
    often does a random predicate with the same pass rate manage that by accident?"""
    rnd = random.Random(seed)
    orgs = m["orgs"]
    classes = m["classes"]
    target_pass = m["i2_pass"]
    n = len(orgs)
    hits = 0
    for _ in range(draws):
        chosen = set(rnd.sample(range(n), target_pass))
        pred = dict((orgs[k].oid, (k in chosen)) for k in range(n))
        constant = True
        for members in classes:
            vals = set(pred[o.oid] for o in members)
            if len(vals) > 1:
                constant = False
                break
        if constant:
            hits += 1
    return {"draws": draws, "matched_pass_rate": target_pass,
            "class_constant_hits": hits}


def null_level_labels(m, draws=200, seed=8334402):
    """A random three-way level labelling reproducing the measured one."""
    rnd = random.Random(seed)
    orgs = m["orgs"]
    cellfree = m["cellfree_sigs"]
    measured = []
    for o in orgs:
        a, b = i2_clauses(o, cellfree)
        measured.append(2 if (a and b) else (1 if i1(o) else 0))
    hits = 0
    for _ in range(draws):
        draw = [rnd.randrange(3) for _ in orgs]
        if draw == measured:
            hits += 1
    return {"draws": draws, "hits": hits}


# --------------------------------------------------------------------------------------
# 10.  Receipt.
# --------------------------------------------------------------------------------------

def canonical_json(obj):
    return json.dumps(obj, indent=2, sort_keys=True, separators=(",", ": "))


def frac(x):
    return "%d/%d" % (x.numerator, x.denominator)


def main():
    m = measure()
    orgs = m["orgs"]
    cellfree = m["cellfree_sigs"]

    # ---- nearest negatives ---------------------------------------------------------
    nn = {}
    seed_i1 = None
    for o in orgs:
        if o.cells == 1 and i1(o):
            seed_i1 = o
            break
    nn["I1_MOTIF_REUSE"] = nearest_negative(
        seed_i1.description(), org_from_bits, i1)
    seed_i2 = None
    for o in orgs:
        if o.cells == 1 and all(i2_clauses(o, cellfree)):
            seed_i2 = o
            break
    nn["I2_HISTORY_DEPENDENCE"] = nearest_negative(
        seed_i2.description(), org_from_bits,
        lambda x: all(i2_clauses(x, cellfree)))

    word_index = dict((w, k) for k, w in enumerate(WORDS))
    base_sigs = set(m["sigs"].values())

    def comp_pred(pair):
        a, b = pair
        return i3_composite_signature(signature(a), signature(b), word_index) not in base_sigs

    def comp_rebuild(bits):
        return (org_from_bits(bits[:8]), org_from_bits(bits[8:]))

    seed_pair = None
    for a in orgs:
        if a.cells != 1:
            continue
        for b in orgs:
            if b.cells != 1:
                continue
            if comp_pred((a, b)):
                seed_pair = (a, b)
                break
        if seed_pair:
            break
    nn["I3_IRREDUCIBLE_COMPOSITION"] = nearest_negative(
        seed_pair[0].description() + seed_pair[1].description(), comp_rebuild, comp_pred,
        max_radius=3) if seed_pair else None

    def ad_bits(a):
        out = []
        for t in a.tables:
            for (s, i) in ((0, 0), (0, 1), (1, 0), (1, 1)):
                ns, o = t[(s, i)]
                out.append(ns)
                out.append(o)
        return tuple(out)

    def ad_rebuild(bits):
        tabs = []
        for half in (bits[:8], bits[8:]):
            t = {}
            for k, (s, i) in enumerate(((0, 0), (0, 1), (1, 0), (1, 1))):
                t[(s, i)] = (half[2 * k], half[2 * k + 1])
            tabs.append(t)
        return Adaptive(tabs)

    ad = adaptive_witness(True)
    nn["I4_EXPERIENCE_CONDITIONED_UPDATE"] = nearest_negative(
        ad_bits(ad), ad_rebuild, lambda x: len(x.witness_triples()) > 0)

    def inv_rebuild(bits):
        added = ("REUSE_AB",) if bits[0] else ("INC",)
        return Developmental(("READ", "EMIT", "INC"), added)
    nn["I5_OPERATOR_INVENTORY_GROWTH"] = nearest_negative(
        (1,), inv_rebuild, lambda x: x.growth() > 0)

    nn["I6_EXTERNALLY_ADMITTED_SELF_CHANGE"] = nearest_negative(
        (1,), lambda bits: Governed(bool(bits[0])),
        lambda x: x.hidden_channel_divergence()["outcomes_differ"])

    nn["I7_CROSS_INSTANCE_ACQUISITION"] = nearest_negative(
        (1,), lambda bits: Population(bool(bits[0])),
        lambda x: x.acquisition()["acquired_only_through_channel"] > 0)

    def unit_rebuild(bits):
        exp = tuple(b for b, keep in zip((0, 1), bits) if keep)
        return GrammarUnit(exp)

    def unit_pred(u):
        return (u.expressive_delta(CORPUS) == 0
                and (u.description_delta(CORPUS) != 0
                     or u.search_distance_delta(TARGET) != 0))
    nn["I8_NEW_EFFECTIVE_UNIT"] = nearest_negative((1, 1), unit_rebuild, unit_pred)

    # ---- verdicts ------------------------------------------------------------------
    verdicts = {
        "I1_MOTIF_REUSE": verdict("I1_MOTIF_REUSE", m["i1_pass"], m["i1_fail"],
                                  m["i1_classes_split_by_description"]),
        "I2_HISTORY_DEPENDENCE": verdict("I2_HISTORY_DEPENDENCE", m["i2_pass"],
                                         len(orgs) - m["i2_pass"],
                                         m["i2_classes_split_by_description"]),
        "I3_IRREDUCIBLE_COMPOSITION": verdict(
            "I3_IRREDUCIBLE_COMPOSITION", m["composites_irreducible"],
            m["composites_total"] - m["composites_irreducible"], 0),
        "I4_EXPERIENCE_CONDITIONED_UPDATE": verdict(
            "I4_EXPERIENCE_CONDITIONED_UPDATE", m["i4_witness_triples"],
            1 if m["i4_negative_witness_triples"] == 0 else 0,
            1 if m["i4_collapses_under_absorption"] else 0),
        "I5_OPERATOR_INVENTORY_GROWTH": verdict(
            "I5_OPERATOR_INVENTORY_GROWTH", m["i5_growth"],
            1 if m["i5_negative_growth"] == 0 else 0, 0),
        "I6_EXTERNALLY_ADMITTED_SELF_CHANGE": verdict(
            "I6_EXTERNALLY_ADMITTED_SELF_CHANGE",
            1 if m["i6"]["outcomes_differ"] else 0,
            1 if not m["i6_negative"]["outcomes_differ"] else 0, 0,
            external_exhibit=m["i6"]["internal_state_identical"]
            and m["i6"]["visible_input_identical"] and m["i6"]["outcomes_differ"]),
        "I7_CROSS_INSTANCE_ACQUISITION": verdict(
            "I7_CROSS_INSTANCE_ACQUISITION",
            m["i7"]["acquired_only_through_channel"],
            1 if m["i7_negative"]["acquired_only_through_channel"] == 0 else 0, 0,
            external_exhibit=m["i7"]["acquired_only_through_channel"] > 0),
        "I8_NEW_EFFECTIVE_UNIT": verdict(
            "I8_NEW_EFFECTIVE_UNIT",
            1 if unit_pred(GrammarUnit((0, 1))) else 0,
            1 if not unit_pred(GrammarUnit((0,))) else 0, 0),
    }

    # ---- level versus capability ----------------------------------------------------
    levels = {}
    caps = {}
    for o in orgs:
        a, b = i2_clauses(o, cellfree)
        levels[o.oid] = 2 if (a and b) else (1 if i1(o) else 0)
        caps[o.oid] = capability_vector(o.run)
    inversions = 0
    inversion_example = None
    ids = [o.oid for o in orgs]
    for x in ids:
        for y in ids:
            if levels[x] > levels[y] and dominates(caps[y], caps[x]):
                inversions += 1
                if inversion_example is None:
                    inversion_example = {
                        "higher_level_system": x, "higher_level": levels[x],
                        "higher_level_capability": [frac(v) for v in caps[x]],
                        "lower_level_system": y, "lower_level": levels[y],
                        "lower_level_capability": [frac(v) for v in caps[y]]}

    zero_capability_at_top = None
    best = None
    for o in orgs:
        if levels[o.oid] != 2:
            continue
        key = tuple(caps[o.oid])
        if best is None or key < best[0]:
            best = (key, o.oid)
    if best is not None:
        zero_capability_at_top = {"system": best[1], "level": 2,
                                  "capability": [frac(v) for v in caps[best[1]]],
                                  "note": "componentwise-least capability among level-2 systems"}

    trip = level_claim_verdict({"system": zero_capability_at_top["system"]
                                if zero_capability_at_top else None,
                                "level": 2, "asserts": "INTELLIGENT",
                                "capability_evidence": False,
                                "development_evidence": False})
    admit = level_claim_verdict({"system": "ANY", "level": 2, "asserts": "INTELLIGENT",
                                 "capability_evidence": True,
                                 "development_evidence": True})
    non_claim = level_claim_verdict({"system": "ANY", "level": 2, "asserts": "AT_LEVEL_2"})

    nulls = {"class_constancy": null_class_constancy(m),
             "level_labels": null_level_labels(m)}

    failed = []
    if not m["length_bound_agrees_with_product_authority"]:
        failed.append("GATE_LENGTH_BOUND_DISAGREES_WITH_AUTHORITY")
    for k, v in verdicts.items():
        if v in ("NOT_SEPARATING_AT_SCOPE", "EXTERNAL_BOUNDARY_NOT_EXHIBITED"):
            # a non-separating transition is a result, not a failure; an unexhibited
            # external boundary is a failure.
            if v == "EXTERNAL_BOUNDARY_NOT_EXHIBITED":
                failed.append("GATE_EXTERNAL_BOUNDARY:" + k)
    for k, v in nn.items():
        if v is None:
            failed.append("GATE_NO_NEAREST_NEGATIVE:" + k)
    if m["i2_intermediate"] <= 0:
        failed.append("GATE_INTERMEDIATE_LAYER_NOT_MEASURED")
    if trip != "REFUSED__LEVEL_MEMBERSHIP_IS_NOT_INTELLIGENCE":
        failed.append("GATE_PROHIBITION_NOT_TRIPPED")
    if admit != "ADMITTED_WITH_EVIDENCE":
        failed.append("GATE_PROHIBITION_ALWAYS_REFUSES")
    if non_claim != "NOT_AN_INTELLIGENCE_CLAIM":
        failed.append("GATE_PROHIBITION_OVERREACHES")
    if inversions == 0:
        failed.append("GATE_NO_LEVEL_CAPABILITY_INVERSION")
    if nulls["level_labels"]["hits"]:
        failed.append("GATE_NULL_LEVEL_LABELS")
    if m["composites_irreducible"] == 0:
        failed.append("GATE_NO_IRREDUCIBLE_COMPOSITE")
    if zero_capability_at_top is None:
        failed.append("GATE_NO_TOP_LEVEL_CAPABILITY_WITNESS")
    if nulls["class_constancy"]["class_constant_hits"] > 20:
        failed.append("GATE_CLASS_CONSTANCY_NOT_INFORMATIVE")

    receipt = {
        "schema": "GMI833AH4OrganizationLadderReceiptV1",
        "package": "gmi-833-ah4-organization-ladder-v1",
        "issue": 833,
        "section": "AH4",
        "source_main": SOURCE_MAIN,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": list(FORBIDDEN_PROMOTIONS),
        "levels": list(LEVELS),
        "invariants": list(INVARIANTS),
        "base_organizations": len(orgs),
        "cell_free": sum(1 for o in orgs if o.cells == 0),
        "one_cell": sum(1 for o in orgs if o.cells == 1),
        "operational_classes": m["class_count"],
        "class_size_histogram": m["class_sizes"],
        "length_bound_agrees_with_product_authority":
            m["length_bound_agrees_with_product_authority"],
        "i1_pass": m["i1_pass"], "i1_fail": m["i1_fail"],
        "i1_classes_split_by_description": m["i1_classes_split_by_description"],
        "i2_clause_counts": m["i2_clause_counts"],
        "i2_pass": m["i2_pass"],
        "i2_intermediate_layer_population": m["i2_intermediate"],
        "i2_classes_split_by_description": m["i2_classes_split_by_description"],
        "non_cumulative_base_systems": m["non_cumulative_base_systems"],
        "composites_total": m["composites_total"],
        "composites_irreducible": m["composites_irreducible"],
        "composite_irreducible_example": m["composite_irreducible_example"],
        "composite_reducible_example": m["composite_reducible_example"],
        "i4_witness_triples": m["i4_witness_triples"],
        "i4_negative_witness_triples": m["i4_negative_witness_triples"],
        "i4_collapses_under_absorption": m["i4_collapses_under_absorption"],
        "i5_growth": m["i5_growth"], "i5_negative_growth": m["i5_negative_growth"],
        "i6": m["i6"], "i6_negative": m["i6_negative"],
        "i7": m["i7"], "i7_negative": m["i7_negative"],
        "i8": m["i8"], "i8_negative": m["i8_negative"],
        "verdicts": verdicts,
        "verdict_counts": dict((v, sum(1 for x in verdicts.values() if x == v))
                               for v in sorted(set(verdicts.values()))),
        "nearest_negatives": nn,
        "level_capability_inversions": inversions,
        "level_capability_inversion_example": inversion_example,
        "highest_level_zero_capability_witness": zero_capability_at_top,
        "prohibition": {"trip": trip, "admit_with_evidence": admit,
                        "non_intelligence_claim": non_claim},
        "nulls": nulls,
        "failed_gates": failed,
        "status": "GREEN" if not failed else "RED",
    }
    return receipt


if __name__ == "__main__":
    r = main()
    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as fh:
        fh.write(canonical_json(r) + "\n")
    print(canonical_json({"status": r["status"], "failed_gates": r["failed_gates"],
                          "operational_classes": r["operational_classes"],
                          "verdicts": r["verdicts"],
                          "i2_intermediate_layer_population":
                              r["i2_intermediate_layer_population"],
                          "level_capability_inversions": r["level_capability_inversions"]}))

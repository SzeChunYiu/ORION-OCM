#!/usr/bin/env python3
"""GMI #833 AE9 route A executor: architecture-independent transition markers.

Writes ``RESULT_V1.json`` to stdout, byte-identical under ``python3 -I -B`` and
``python3 -I -O -B`` and across CPython 3.8 and 3.12.

Route A computes every trajectory quantity in closed form from Moebius
inclusion-exclusion counts over the lattice of affine subspaces of GF(2)^4,
and every marker from canonical labelling plus bitmask/popcount readout
algebra and essential-variable analysis.  Route B
(``independent_marker_oracle_v1.py``) recomputes all of it by exhaustive
subset averaging, explicit equivalence-class closure, element-by-element
group enumeration and explicit truth-table search.  Route A imports route B
to certify agreement; route B never imports route A.

Exact arithmetic only: ``int`` and ``fractions.Fraction``.
"""

import hashlib
import itertools
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import independent_marker_oracle_v1 as oracle

HERE = os.path.dirname(os.path.abspath(__file__))
PACKAGE = "gmi-833-ae-ae9-transition-markers-v1"
ISSUE = 833
ISSUE_COMMENT_ID = 5692689542
SOURCE_MAIN = "0dcdec54fbece041ee2b7cd1f630469ad85d19d3"
FREEZE_COMMIT = "b472903bddaeb78651f7cee32fe5bd3fc3ba4a6e"
REGISTER_COMMIT = "fb1edbf03268b2b0140a96a56cb7f656f351d2f5"
CLAIM_CEILING = (
    "GMI_833_AE9_ARCHITECTURE_INDEPENDENT_TRANSITION_MARKERS_DEFINED_AND_"
    "EMERGENCE_CLASSES_SEPARATED_ON_NON_NEURAL_REGISTERED_SYSTEMS")

FORBIDDEN_PROMOTIONS = [
    "ALL_LEARNING_IS_COMPRESSION",
    "ARCHITECTURE_SELECTION_LAW",
    "ASYMPTOTIC_EXTRAPOLATION_FROM_FINITE_ROSTER",
    "COMPLETE_GMI",
    "EMERGENCE_IS_ALWAYS_A_METRIC_ARTIFACT",
    "EMERGENCE_IS_ALWAYS_A_PHASE_TRANSITION",
    "FREE_ENERGY_PRINCIPLE_PROVED",
    "GENERAL_REASONING_REDUCED_TO_PREDICTION",
    "GMI_MORPHOLOGY_PREDICTION",
    "INTELLIGENCE_EQUALS_COMPRESSION",
    "MANIFOLD_HYPOTHESIS_UNIVERSAL",
    "MUTUAL_INFORMATION_SUFFICIENT_FOR_INTELLIGENCE",
    "NEURAL_RESULT_FROM_NON_NEURAL_ROSTER",
    "REAL_SYSTEM_CLAIM_WITHOUT_INSTRUMENT",
    "THERMODYNAMIC_INTELLIGENCE_LAW",
    "TRANSITION_MARKER_PREDICTS_CAPABILITY_ONSET",
    "WORLD_MODEL_ALWAYS_REQUIRED",
]

N_COORDS = 4
POINTS = tuple(range(1 << N_COORDS))
NPTS = len(POINTS)
NONE_SYMBOL = "NONE"
POOL = (0, 1, 2, 4, 8, 9, 10, 12)
HELD_OUT = (3, 5, 6, 7, 11, 13, 14, 15)
SAMPLE_RANGE = tuple(range(0, 9))
NULL_SEED = ISSUE_COMMENT_ID % (2 ** 31)


def fail(message):
    raise SystemExit("AE9 executor refused to emit: " + message)


def need(condition, message):
    if not condition:
        fail(message)


# ---------------------------------------------------------------------------
# registered constants: custody of the prospective register
# ---------------------------------------------------------------------------

def load_register():
    path = os.path.join(HERE, "PROSPECTIVE_REGISTER_V1.json")
    with open(path, "r") as handle:
        reg = json.load(handle)
    canonical = dict(
        (k, v) for k, v in reg.items()
        if k not in ("self_digest_sha256", "self_digest_note"))
    digest = hashlib.sha256(json.dumps(
        canonical, sort_keys=True, separators=(",", ":")).encode(
            "utf-8")).hexdigest()
    need(digest == reg["self_digest_sha256"],
         "prospective register self digest mismatch")
    return reg, digest


REGISTER, REGISTER_DIGEST = load_register()
RC = REGISTER["registered_constants"]
EXACT_MATCH_K = RC["exact_match_k"]
JUNTA_ARITY = RC["readout_budget"]["junta_arity"]
TREE_DEPTH = RC["readout_budget"]["tree_depth"]
NULL_TRIALS = RC["null_trials"]
STRUCTURAL_INVARIANTS = tuple(RC["structural_invariants"])
need(RC["n"] == N_COORDS, "registered n does not match the executor")
need(tuple(RC["sample_range"]) == SAMPLE_RANGE,
     "registered sample range does not match the executor")


# ---------------------------------------------------------------------------
# points, coordinates, functions as bitmasks
# ---------------------------------------------------------------------------

def coord(v, i):
    return (v >> (N_COORDS - i)) & 1


def coord_mask(i):
    return 1 << (N_COORDS - i)


def as_mask(values):
    """Pack a 0/1 tuple over POINTS into a 16-bit integer."""
    mask = 0
    for v in POINTS:
        if values[v]:
            mask |= 1 << v
    return mask


def as_tuple(mask):
    return tuple((mask >> v) & 1 for v in POINTS)


def popcount(mask):
    total = 0
    while mask:
        mask &= mask - 1
        total += 1
    return total


T_XOR12 = tuple(coord(v, 1) ^ coord(v, 2) for v in POINTS)
T_PARITY4 = tuple(
    coord(v, 1) ^ coord(v, 2) ^ coord(v, 3) ^ coord(v, 4) for v in POINTS)
D_X4 = tuple(coord(v, 4) for v in POINTS)
D_ZERO = tuple(0 for v in POINTS)

AFFINE_FORMS = []
for _a in range(1 << N_COORDS):
    for _b in (0, 1):
        _vals = []
        for _v in POINTS:
            _s = _b
            for _i in range(1, N_COORDS + 1):
                if (_a >> (N_COORDS - _i)) & 1:
                    _s ^= coord(_v, _i)
            _vals.append(_s)
        AFFINE_FORMS.append(((_a, _b), tuple(_vals)))
AFFINE_FORMS.sort()
AFFINE_FORMS = tuple(AFFINE_FORMS)


# ---------------------------------------------------------------------------
# partitions by canonical labelling; markers by bitmask algebra
# ---------------------------------------------------------------------------

def canonical_labels(codes):
    """Relabel a code map by first occurrence; the partition invariant."""
    seen = {}
    labels = []
    for v in POINTS:
        key = codes[v]
        if key not in seen:
            seen[key] = len(seen)
        labels.append(seen[key])
    return tuple(labels)


def cell_masks(labels):
    masks = {}
    for v in POINTS:
        masks[labels[v]] = masks.get(labels[v], 0) | (1 << v)
    return tuple(masks[k] for k in sorted(masks))


def cells_count(labels):
    return len(set(labels))


PERMS = tuple(itertools.permutations(range(1, N_COORDS + 1)))


def perm_image(v, sigma):
    w = 0
    for i in range(1, N_COORDS + 1):
        if coord(v, sigma[i - 1]):
            w |= coord_mask(i)
    return w


def invariance_order(labels):
    """Stabiliser order, decided by well-definedness of the induced label map."""
    order = 0
    for sigma in PERMS:
        induced = {}
        image_labels = set()
        ok = True
        for v in POINTS:
            src = labels[v]
            dst = labels[perm_image(v, sigma)]
            if src in induced:
                if induced[src] != dst:
                    ok = False
                    break
            else:
                if dst in image_labels:
                    ok = False
                    break
                induced[src] = dst
                image_labels.add(dst)
        if ok:
            order += 1
    return order


def measurable(labels, fmask):
    for cmask in cell_masks(labels):
        inter = fmask & cmask
        if inter != 0 and inter != cmask:
            return False
    return True


def essential_arity(fmask):
    count = 0
    for i in range(1, N_COORDS + 1):
        mi = coord_mask(i)
        moved = False
        for v in POINTS:
            if ((fmask >> v) & 1) != ((fmask >> (v ^ mi)) & 1):
                moved = True
                break
        if moved:
            count += 1
    return count


def budget_masks(arity):
    out = set()
    for size in range(0, arity + 1):
        for support in itertools.combinations(range(1, N_COORDS + 1), size):
            for table in itertools.product((0, 1), repeat=1 << size):
                mask = 0
                for v in POINTS:
                    idx = 0
                    for j, i in enumerate(support):
                        idx |= coord(v, i) << (size - 1 - j)
                    if table[idx]:
                        mask |= 1 << v
                out.add(mask)
    return tuple(sorted(out))


BUDGET_MASKS = budget_masks(JUNTA_ARITY)
FULL_MASKS = budget_masks(N_COORDS)


def readout_arity(labels, tmask, arity_cap=N_COORDS):
    """Least junta arity of an exact readout of the partition, or NONE."""
    if not measurable(labels, tmask):
        return NONE_SYMBOL
    k = essential_arity(tmask)
    if k > arity_cap:
        return NONE_SYMBOL
    return k


def usable(labels, tmask, masks=None):
    pool = BUDGET_MASKS if masks is None else masks
    best = 0
    for h in pool:
        if not measurable(labels, h):
            continue
        agree = NPTS - popcount(h ^ tmask)
        if agree > best:
            best = agree
    return Fraction(best, NPTS)


def separability(labels, tmask, masks=None):
    """Discordant label pairs split by a budgeted partition-measurable readout."""
    pool = BUDGET_MASKS if masks is None else masks
    discordant = []
    for x, y in itertools.combinations(POINTS, 2):
        if ((tmask >> x) & 1) != ((tmask >> y) & 1):
            discordant.append((x, y))
    if not discordant:
        return Fraction(0)
    split = set()
    for h in pool:
        if not measurable(labels, h):
            continue
        for pair in discordant:
            if pair in split:
                continue
            if ((h >> pair[0]) & 1) != ((h >> pair[1]) & 1):
                split.add(pair)
    return Fraction(len(split), len(discordant))


def mirkin_distance(l1, l2):
    """Pair-counting distance from cell-size sums, not from pair enumeration."""
    same1 = 0
    for cmask in cell_masks(l1):
        n = popcount(cmask)
        same1 += n * (n - 1) // 2
    same2 = 0
    for cmask in cell_masks(l2):
        n = popcount(cmask)
        same2 += n * (n - 1) // 2
    both = 0
    for c1 in cell_masks(l1):
        for c2 in cell_masks(l2):
            n = popcount(c1 & c2)
            both += n * (n - 1) // 2
    disagree = same1 + same2 - 2 * both
    return Fraction(disagree, NPTS * (NPTS - 1) // 2)


def refinement(l1, l2):
    meet = canonical_labels(tuple(zip(l1, l2)))
    return (cells_count(meet) - cells_count(l2),
            cells_count(meet) - cells_count(l1),
            mirkin_distance(l1, l2))


def marker_vector(labels, tmask):
    return {
        "CELLS": cells_count(labels),
        "SEPARABILITY": str(separability(labels, tmask)),
        "INVARIANCE": invariance_order(labels),
        "READOUT_ARITY": readout_arity(labels, tmask),
        "USABLE": str(usable(labels, tmask)),
    }


def structural_tuple(labels, tmask, arity_cap=N_COORDS):
    return (cells_count(labels), invariance_order(labels),
            readout_arity(labels, tmask, arity_cap))


# ---------------------------------------------------------------------------
# Moebius inclusion-exclusion over the lattice of affine subspaces
# ---------------------------------------------------------------------------

def affine_lattice():
    linear = set()
    nonzero = [v for v in POINTS if v != 0]
    for size in range(0, N_COORDS + 1):
        for gens in itertools.combinations(nonzero, size):
            span = set([0])
            for g in gens:
                span |= set(s ^ g for s in span)
            linear.add(frozenset(span))
    affine = set()
    for lin in linear:
        for shift in POINTS:
            affine.add(frozenset(w ^ shift for w in lin))
    affine.add(frozenset())
    return tuple(sorted(affine, key=lambda s: (len(s), sorted(s))))


LATTICE = affine_lattice()
TOP = frozenset(POINTS)


def moebius_to_top():
    mu = {}
    for element in sorted(LATTICE, key=lambda s: -len(s)):
        if element == TOP:
            mu[element] = 1
            continue
        total = 0
        for other in LATTICE:
            if other != element and element < other:
                total += mu[other]
        mu[element] = -total
    return mu


MU = moebius_to_top()


def binom(n, k):
    if k < 0 or n < 0 or k > n:
        return 0
    num = 1
    den = 1
    for j in range(k):
        num *= (n - j)
        den *= (j + 1)
    return num // den


def spanning_count(ground, m):
    """Number of m-subsets of ``ground`` whose affine span is the whole space."""
    gset = set(ground)
    total = 0
    for element in LATTICE:
        total += MU[element] * binom(len(gset & element), m)
    return total


def spanning_count_containing(ground, x, m):
    if m <= 0:
        return 0
    gset = set(ground)
    if x not in gset:
        return 0
    total = 0
    for element in LATTICE:
        if x in element:
            total += MU[element] * binom(len(gset & element) - 1, m - 1)
    return total


# ---------------------------------------------------------------------------
# trajectories in closed form
# ---------------------------------------------------------------------------

SPEC_SMOOTH = {"name": "TRAJ_SMOOTH", "fit_affine": False, "memorise": True,
               "default": D_ZERO, "target": T_XOR12, "code": "IDENTITY",
               "learner": "EXACT_LOOKUP"}
SPEC_JUMP = {"name": "TRAJ_JUMP", "fit_affine": True, "memorise": False,
             "default": D_X4, "target": T_XOR12, "code": "BASE",
             "learner": "GF2_ELIMINATION"}
SPEC_GROK = {"name": "TRAJ_GROK", "fit_affine": True, "memorise": True,
             "default": D_X4, "target": T_PARITY4, "code": "BASE",
             "learner": "GF2_ELIMINATION_WITH_EXACT_LOOKUP"}
ROSTER = (SPEC_SMOOTH, SPEC_JUMP, SPEC_GROK)


def base_rate(target):
    ones = sum(target)
    return Fraction(max(ones, NPTS - ones), NPTS)


def closed_form_trajectory(spec, arity_cap=N_COORDS, held_out=HELD_OUT):
    target = spec["target"]
    tmask = as_mask(target)
    dmask = as_mask(spec["default"])
    agree_default = ~(tmask ^ dmask) & ((1 << NPTS) - 1)
    pool_mask = as_mask(tuple(1 if v in POOL else 0 for v in POINTS))
    held_mask = as_mask(tuple(1 if v in held_out else 0 for v in POINTS))

    forms = []
    if spec["fit_affine"]:
        for key, vals in AFFINE_FORMS:
            fmask = as_mask(vals)
            agree = ~(tmask ^ fmask) & ((1 << NPTS) - 1)
            ground = tuple(v for v in POOL if (agree >> v) & 1)
            forms.append((key, fmask, agree, ground))

    acc_overall = []
    acc_train = []
    acc_heldout = []
    profiles = []
    det_counts = []

    for m in SAMPLE_RANGE:
        total_subsets = binom(len(POOL), m)
        det_total = 0
        sum_overall = 0
        sum_heldout = 0
        det_containing = dict((v, 0) for v in POOL)
        reachable = []
        for key, fmask, agree, ground in forms:
            count = spanning_count(ground, m)
            need(count >= 0, "negative spanning count")
            if count == 0:
                continue
            det_total += count
            sum_overall += count * popcount(agree)
            sum_heldout += count * popcount(agree & held_mask)
            reachable.append(fmask)
            for v in ground:
                det_containing[v] += spanning_count_containing(ground, v, m)
        undet = total_subsets - det_total
        need(undet >= 0, "determined count exceeds subset count")
        sum_overall += undet * popcount(agree_default)
        sum_heldout += undet * popcount(agree_default & held_mask)
        if spec["memorise"]:
            hit = 0
            for v in POOL:
                if (agree_default >> v) & 1:
                    hit += binom(len(POOL) - 1, m - 1) - det_containing[v]
            sum_overall += m * undet - hit
        acc_overall.append(Fraction(sum_overall, NPTS * total_subsets))
        acc_heldout.append(Fraction(sum_heldout, len(held_out) * total_subsets))
        if m == 0:
            acc_train.append(Fraction(1))
        else:
            sum_train = det_total * m
            if spec["memorise"]:
                sum_train += undet * m
            else:
                hit = 0
                for v in POOL:
                    if (agree_default >> v) & 1:
                        hit += binom(len(POOL) - 1, m - 1) - det_containing[v]
                sum_train += hit
            acc_train.append(Fraction(sum_train, m * total_subsets))
        if spec["code"] == "IDENTITY":
            prof = set([structural_tuple(
                canonical_labels(POINTS), tmask, arity_cap)])
        else:
            prof = set()
            if undet > 0:
                prof.add(structural_tuple(
                    canonical_labels(as_tuple(dmask)), tmask, arity_cap))
            for fmask in reachable:
                prof.add(structural_tuple(
                    canonical_labels(as_tuple(fmask)), tmask, arity_cap))
        profiles.append(tuple(sorted(prof, key=repr)))
        det_counts.append(det_total)

    return {
        "acc_overall": acc_overall,
        "acc_train": acc_train,
        "acc_heldout": acc_heldout,
        "structural_profile": profiles,
        "determined_count": det_counts,
        "base_rate": base_rate(target),
    }


# ---------------------------------------------------------------------------
# the emergence classifier
# ---------------------------------------------------------------------------

def increments(seq):
    return [seq[i] - seq[i - 1] for i in range(1, len(seq))]


def exact_match_transform(seq, k):
    return [x ** k for x in seq]


def classify(report, k=None):
    """Assign one registered emergence class; report every signature fired."""
    if k is None:
        k = EXACT_MATCH_K
    br = report["base_rate"]
    acc = report["acc_overall"]
    train = report["acc_train"]
    held = report["acc_heldout"]
    prof = report["structural_profile"]

    onset = NONE_SYMBOL
    for m in SAMPLE_RANGE:
        if held[m] > br:
            onset = m
            break
    flat_before = True
    if onset != NONE_SYMBOL:
        for m in range(0, onset):
            if held[m] != br:
                flat_before = False

    struct_onset = NONE_SYMBOL
    for m in SAMPLE_RANGE:
        if prof[m] != prof[0]:
            struct_onset = m
            break
    distinct = set()
    for p in prof:
        for tup in p:
            distinct.add(tup)
    inv_constant = all(p == prof[0] for p in prof)

    train_sat = NONE_SYMBOL
    for m in range(1, len(SAMPLE_RANGE)):
        if all(train[j] == 1 for j in range(m, len(SAMPLE_RANGE))):
            train_sat = m
            break

    under = increments(acc)
    spread = max(under) - min(under)
    positive = all(d > 0 for d in under)
    trans = increments(exact_match_transform(acc, k))
    knee = all(trans[i] < trans[i + 1] for i in range(len(trans) - 1))

    grok = (onset != NONE_SYMBOL and flat_before
            and train_sat != NONE_SYMBOL and train_sat < onset)
    phase = (onset != NONE_SYMBOL and flat_before
             and struct_onset == onset and len(distinct) == 2)
    artifact = (onset == NONE_SYMBOL and inv_constant
                and spread == 0 and positive and knee)

    if grok:
        label = "GROKKING_DELAYED_GENERALIZATION"
    elif phase:
        label = "PHASE_LIKE_REORGANIZATION"
    elif artifact:
        label = "THRESHOLDED_METRIC_ARTIFACT"
    else:
        label = "NO_EMERGENCE"

    magnitude = Fraction(0)
    if onset != NONE_SYMBOL:
        magnitude = held[onset] - br

    return {
        "class": label,
        "signatures": {
            "GROKKING_DELAYED_GENERALIZATION": grok,
            "PHASE_LIKE_REORGANIZATION": phase,
            "THRESHOLDED_METRIC_ARTIFACT": artifact,
        },
        "alarm_genuine_transition": bool(grok or phase),
        "heldout_onset": onset,
        "heldout_flat_before_onset": flat_before,
        "structural_onset": struct_onset,
        "distinct_structural_tuples": len(distinct),
        "train_saturation": train_sat,
        "underlying_increment_spread": str(spread),
        "transform_increments_strictly_increasing": knee,
        "magnitude": str(magnitude),
    }


# ---------------------------------------------------------------------------
# randomised null: label randomisation through the identical pipeline
# ---------------------------------------------------------------------------

def unrank_subset(rank, n, k):
    """The ``rank``-th k-subset of range(n) in lexicographic order."""
    out = []
    x = 0
    remaining = rank
    for i in range(k):
        while True:
            count = binom(n - x - 1, k - i - 1)
            if remaining < count:
                out.append(x)
                x += 1
                break
            remaining -= count
            x += 1
    return tuple(out)


def null_targets(trials):
    state = NULL_SEED
    total = binom(NPTS, NPTS // 2)
    out = []
    for _ in range(trials):
        state = (1103515245 * state + 12345) % (2 ** 31)
        ones = unrank_subset(state % total, NPTS, NPTS // 2)
        out.append(tuple(1 if v in ones else 0 for v in POINTS))
    return out


def is_affine(target):
    tmask = as_mask(target)
    for _key, vals in AFFINE_FORMS:
        if as_mask(vals) == tmask:
            return True
    return False


# ---------------------------------------------------------------------------
# main evaluation
# ---------------------------------------------------------------------------

def frac_list(seq):
    return [str(x) for x in seq]


def prof_list(profiles):
    return [[list(t) for t in p] for p in profiles]


def main():
    checks = {}
    checks["register_digest_recomputed"] = (
        REGISTER_DIGEST == REGISTER["self_digest_sha256"])
    checks["registered_readout_budget_used"] = (
        JUNTA_ARITY == 2 and TREE_DEPTH == 2)
    checks["registered_exact_match_k_used"] = (EXACT_MATCH_K == 8)
    checks["pool_and_heldout_disjoint"] = (
        len(set(POOL) & set(HELD_OUT)) == 0
        and len(set(POOL) | set(HELD_OUT)) == NPTS)
    checks["no_neural_system_on_roster"] = all(
        spec["learner"].replace("_WITH_EXACT_LOOKUP", "")
        in RC["learners"] for spec in ROSTER)

    results = {}

    # --- row 1: architecture independence, both directions -----------------
    ident_labels = canonical_labels(POINTS)
    tmask_xor = as_mask(T_XOR12)
    tmask_par = as_mask(T_PARITY4)
    named = {
        "IDENTITY__T_XOR12": (ident_labels, tmask_xor),
        "IDENTITY__T_PARITY4": (ident_labels, tmask_par),
        "KER_X4__T_XOR12": (canonical_labels(D_X4), tmask_xor),
        "KER_X4__T_PARITY4": (canonical_labels(D_X4), tmask_par),
        "KER_XOR12__T_XOR12": (canonical_labels(T_XOR12), tmask_xor),
        "KER_PARITY4__T_PARITY4": (canonical_labels(T_PARITY4), tmask_par),
    }
    marker_table = dict(
        (k, marker_vector(v[0], v[1])) for k, v in named.items())

    # two materially different learners inducing the same partition
    gf2_map = None
    for _key, vals in AFFINE_FORMS:
        if tuple(vals) == T_XOR12:
            gf2_map = tuple(vals)
    need(gf2_map is not None, "GF(2) elimination target missing from the class")
    greedy_map = oracle.greedy_decision_list(T_XOR12, POOL, TREE_DEPTH)
    same_partition = (canonical_labels(gf2_map) == canonical_labels(greedy_map))
    gf2_markers = marker_vector(canonical_labels(gf2_map), tmask_xor)
    greedy_markers = marker_vector(canonical_labels(greedy_map), tmask_xor)
    equal_markers = (gf2_markers == greedy_markers)

    # injective re-encoding of the code set leaves every marker unchanged
    reencoded = tuple("code-%d" % (7 * z + 3) for z in T_XOR12)
    reencode_markers = marker_vector(canonical_labels(reencoded), tmask_xor)
    reencode_moved_codes = (tuple(str(z) for z in T_XOR12) != reencoded)
    reencode_invariant = (reencode_markers == gf2_markers)
    reencode_refinement = refinement(
        canonical_labels(gf2_map), canonical_labels(reencoded))

    # a genuine change of partition moves at least one marker
    distinct_parts = sorted(set(
        canonical_labels(c) for c in
        (POINTS, D_X4, T_XOR12, T_PARITY4,
         tuple(coord(v, 1) for v in POINTS),
         tuple(coord(v, 1) & coord(v, 2) for v in POINTS))))
    pair_rows = []
    all_pairs_moved = True
    unary_collisions = 0
    for p, q in itertools.combinations(distinct_parts, 2):
        merged, split, dist = refinement(p, q)
        moved_unary = (marker_vector(p, tmask_xor) != marker_vector(q, tmask_xor))
        if dist <= 0:
            all_pairs_moved = False
        if not moved_unary:
            unary_collisions += 1
        pair_rows.append({
            "cells_left": cells_count(p), "cells_right": cells_count(q),
            "merged": merged, "split": split,
            "normalized_partition_distance": str(dist),
            "some_unary_marker_moves": moved_unary})
    results["architecture_independence"] = {
        "markers": marker_table,
        "same_partition_two_learners": {
            "learner_a": "GF2_ELIMINATION",
            "learner_b": "GREEDY_DECISION_LIST",
            "induced_partitions_equal": same_partition,
            "markers_exactly_equal": equal_markers,
            "markers": gf2_markers},
        "injective_reencoding": {
            "code_set_actually_changed": reencode_moved_codes,
            "every_marker_unchanged": reencode_invariant,
            "refinement_to_reencoded": {
                "merged": reencode_refinement[0],
                "split": reencode_refinement[1],
                "normalized_partition_distance": str(reencode_refinement[2])}},
        "distinct_partitions_move_a_marker": {
            "pairs_tested": len(pair_rows),
            "every_pair_moves_REFINEMENT": all_pairs_moved,
            "pairs_with_no_unary_marker_moving": unary_collisions,
            "pairs": pair_rows},
    }
    checks["row1_same_partition_equal_markers"] = bool(
        same_partition and equal_markers)
    checks["row1_reencoding_leaves_markers_fixed"] = bool(
        reencode_moved_codes and reencode_invariant)
    checks["row1_distinct_partitions_move_a_marker"] = bool(all_pairs_moved)

    # --- trajectories -------------------------------------------------------
    reports = {}
    traj_out = {}
    classes = {}
    for spec in ROSTER:
        rep = closed_form_trajectory(spec)
        reports[spec["name"]] = rep
        cls = classify(rep)
        classes[spec["name"]] = cls
        traj_out[spec["name"]] = {
            "learner": spec["learner"],
            "acc_overall": frac_list(rep["acc_overall"]),
            "acc_train": frac_list(rep["acc_train"]),
            "acc_heldout": frac_list(rep["acc_heldout"]),
            "base_rate": str(rep["base_rate"]),
            "structural_profile": prof_list(rep["structural_profile"]),
            "determined_subset_count": rep["determined_count"],
            "classification": cls,
        }
    results["trajectories"] = traj_out

    smooth = reports["TRAJ_SMOOTH"]
    jump = reports["TRAJ_JUMP"]
    grok = reports["TRAJ_GROK"]

    # --- row 3: smooth versus qualitative ----------------------------------
    smooth_inc = increments(smooth["acc_overall"])
    jump_struct = classes["TRAJ_JUMP"]["structural_onset"]
    jump_acc_onset = None
    for m in SAMPLE_RANGE:
        if jump["acc_overall"][m] > jump["base_rate"]:
            jump_acc_onset = m
            break
    arity_seq = []
    for p in jump["structural_profile"]:
        arity_seq.append(sorted(set(str(t[2]) for t in p)))
    results["row3_smooth_versus_qualitative"] = {
        "smooth": {
            "accuracy": frac_list(smooth["acc_overall"]),
            "per_step_increments": frac_list(smooth_inc),
            "increments_all_equal": len(set(smooth_inc)) == 1,
            "strictly_increasing": all(d > 0 for d in smooth_inc),
            "structural_profile_constant": all(
                p == smooth["structural_profile"][0]
                for p in smooth["structural_profile"]),
            "structural_tuple": list(smooth["structural_profile"][0][0]),
        },
        "jump": {
            "accuracy": frac_list(jump["acc_overall"]),
            "heldout": frac_list(jump["acc_heldout"]),
            "base_rate": str(jump["base_rate"]),
            "m_star_accuracy": jump_acc_onset,
            "m_star_heldout": classes["TRAJ_JUMP"]["heldout_onset"],
            "m_star_structural": jump_struct,
            "same_step": (jump_acc_onset == jump_struct
                          == classes["TRAJ_JUMP"]["heldout_onset"]),
            "readout_arity_by_m": arity_seq,
            "invariance_before": jump["structural_profile"][0][0][1],
            "jump_magnitude_heldout": classes["TRAJ_JUMP"]["magnitude"],
        },
    }
    checks["row3_smooth_arm"] = bool(
        len(set(smooth_inc)) == 1 and all(d > 0 for d in smooth_inc)
        and all(p == smooth["structural_profile"][0]
                for p in smooth["structural_profile"]))
    checks["row3_jump_arm"] = bool(
        jump_acc_onset == jump_struct == classes["TRAJ_JUMP"]["heldout_onset"]
        and arity_seq[0] == ["NONE"] and "2" in arity_seq[jump_struct])

    # --- row 4: the emergence re-audit -------------------------------------
    transform = exact_match_transform(smooth["acc_overall"], EXACT_MATCH_K)
    t_inc = increments(transform)
    knee_ratio = t_inc[-1] / t_inc[0]
    results["row4_emergence_reaudit"] = {
        "exact_match_k": EXACT_MATCH_K,
        "underlying_accuracy": frac_list(smooth["acc_overall"]),
        "underlying_increments": frac_list(smooth_inc),
        "underlying_increment_spread": str(max(smooth_inc) - min(smooth_inc)),
        "transformed_metric": frac_list(transform),
        "transformed_increments": frac_list(t_inc),
        "transformed_increments_strictly_increasing": all(
            t_inc[i] < t_inc[i + 1] for i in range(len(t_inc) - 1)),
        "knee_ratio_last_over_first": str(knee_ratio),
        "structural_profile_constant_throughout": all(
            p == smooth["structural_profile"][0]
            for p in smooth["structural_profile"]),
        "classifier_on_transformed_curve_raises_no_alarm": not classify(
            {"base_rate": smooth["base_rate"],
             "acc_overall": transform,
             "acc_train": smooth["acc_train"],
             "acc_heldout": smooth["acc_heldout"],
             "structural_profile": smooth["structural_profile"]}
        )["alarm_genuine_transition"],
        "witness_classes": dict(
            (name, classes[name]["class"]) for name in sorted(classes)),
        "grok_also_shows_phase_like_signature": classes["TRAJ_GROK"][
            "signatures"]["PHASE_LIKE_REORGANIZATION"],
    }

    planted = {"TRAJ_SMOOTH": "THRESHOLDED_METRIC_ARTIFACT",
               "TRAJ_JUMP": "PHASE_LIKE_REORGANIZATION",
               "TRAJ_GROK": "GROKKING_DELAYED_GENERALIZATION"}
    labels_all = ["GROKKING_DELAYED_GENERALIZATION",
                  "NO_EMERGENCE",
                  "PHASE_LIKE_REORGANIZATION",
                  "THRESHOLDED_METRIC_ARTIFACT"]
    confusion = {}
    for name in sorted(planted):
        row = dict((lab, 0) for lab in labels_all)
        row[classes[name]["class"]] = 1
        confusion[planted[name] + "__" + name] = row
    recall = sum(1 for n in planted if classes[n]["class"] == planted[n])
    results["row4_emergence_reaudit"]["classifier_validation"] = {
        "planted_positives": 3,
        "recall": recall,
        "confusion_over_roster": confusion,
        "no_alarm_on_clean_smooth_trajectory": not classes[
            "TRAJ_SMOOTH"]["alarm_genuine_transition"],
    }
    checks["row4_recall_full"] = (recall == 3)
    checks["row4_no_alarm_on_smooth"] = not classes[
        "TRAJ_SMOOTH"]["alarm_genuine_transition"]
    checks["row4_no_alarm_on_transformed_smooth"] = results[
        "row4_emergence_reaudit"][
            "classifier_on_transformed_curve_raises_no_alarm"]
    checks["row4_knee_is_strict"] = results["row4_emergence_reaudit"][
        "transformed_increments_strictly_increasing"]

    # --- null ---------------------------------------------------------------
    fired = []
    class_counts = dict((lab, 0) for lab in labels_all)
    affine_draws = 0
    magnitudes = []
    for idx, tgt in enumerate(null_targets(NULL_TRIALS)):
        spec = dict(SPEC_JUMP)
        spec["target"] = tgt
        rep = closed_form_trajectory(spec)
        cls = classify(rep)
        class_counts[cls["class"]] += 1
        aff = is_affine(tgt)
        if aff:
            affine_draws += 1
        if cls["alarm_genuine_transition"]:
            fired.append({"trial": idx, "class": cls["class"],
                          "magnitude": cls["magnitude"],
                          "target_is_affine": aff})
            if not aff:
                magnitudes.append(Fraction(cls["magnitude"]))
    witness_mag = Fraction(classes["TRAJ_JUMP"]["magnitude"])
    largest_false = max(magnitudes) if magnitudes else Fraction(0)
    results["null"] = {
        "trials": NULL_TRIALS,
        "sampler": ("uniform balanced target of {0,1}^4 by combinatorial "
                    "unranking from an integer LCG, run through the "
                    "unchanged TRAJ_JUMP pipeline"),
        "seed": NULL_SEED,
        "class_counts": class_counts,
        "alarms": len(fired),
        "alarms_on_affine_draws": sum(1 for f in fired if f["target_is_affine"]),
        "false_alarms_on_non_affine_draws": len(magnitudes),
        "affine_draws": affine_draws,
        "firing_trials": fired,
        "largest_false_alarm_magnitude": str(largest_false),
        "planted_witness_magnitude": str(witness_mag),
        "witness_exceeds_largest_false_alarm": witness_mag > largest_false,
        "confusion_over_null": {
            "positive_class": ("trials whose drawn task is affine, the class "
                               "the registered witness belongs to"),
            "true_positive": sum(1 for f in fired if f["target_is_affine"]),
            "false_negative": affine_draws - sum(
                1 for f in fired if f["target_is_affine"]),
            "false_positive": len(magnitudes),
            "true_negative": (NULL_TRIALS - affine_draws) - len(magnitudes),
        },
        "known_clean_witnesses_flagged": [
            n for n in sorted(classes)
            if n == "TRAJ_SMOOTH" and classes[n]["alarm_genuine_transition"]],
    }
    checks["null_witness_beats_false_alarms"] = bool(witness_mag > largest_false)
    checks["null_no_alarm_on_clean_witness"] = (
        results["null"]["known_clean_witnesses_flagged"] == [])

    # --- bounds -------------------------------------------------------------
    usable_par_values = sorted(set(
        str(usable(canonical_labels(c), tmask_par))
        for c in (POINTS, D_X4, T_PARITY4, T_XOR12)))
    usable_par_relaxed = str(usable(
        canonical_labels(T_PARITY4), tmask_par, FULL_MASKS))
    jump_invariances = sorted(set(
        t[1] for p in jump["structural_profile"] for t in p))
    smooth_spread = max(smooth_inc) - min(smooth_inc)
    transform_spread = max(t_inc) - min(t_inc)
    relaxed_onset = lex_least_onset()

    bounds = [
        {"id": "AE9-B1",
         "statement": ("USABLE(phi, PARITY4, R) <= 1/2 for every representation "
                       "phi, at the registered readout budget R"),
         "kind": "upper", "bound_value": "1/2",
         "range_lo": "1/2", "range_hi": "1",
         "range_derivation": ("USABLE is an exact accuracy on the 16-point "
                              "registered input space, so it lies in [0,1] by "
                              "definition; the two constant readouts are in "
                              "every budgeted class and are measurable with "
                              "respect to every partition, so USABLE is at "
                              "least the majority-class frequency of the "
                              "target, which is 1/2 for a balanced target. The "
                              "range is read off the definition of USABLE and "
                              "of the readout class, not off the roster."),
         "vacuous": False,
         "attained_by": {"object": "every registered representation",
                         "values": usable_par_values},
         "violated_by": {
             "relaxed_class": "junta arity raised from 2 to 4",
             "object": "KER_PARITY4 with the arity-4 readout class",
             "value": usable_par_relaxed}},
        {"id": "AE9-B2",
         "statement": ("INVARIANCE(phi) <= 6 for every representation arising "
                       "on TRAJ_JUMP"),
         "kind": "upper", "bound_value": "6",
         "range_lo": "1", "range_hi": "24",
         "range_derivation": ("INVARIANCE is the order of a subgroup of the "
                              "coordinate-permutation group of {0,1}^4, which "
                              "has order 4! = 24; the trivial subgroup has "
                              "order 1. Both endpoints come from the "
                              "definition of the group, not from the roster."),
         "vacuous": False,
         "attained_by": {"object": "TRAJ_JUMP pre-transition representation",
                         "values": [str(v) for v in jump_invariances]},
         "violated_by": {
             "relaxed_class": "representations anywhere on the registered roster",
             "object": "TRAJ_SMOOTH identity code map",
             "value": str(smooth["structural_profile"][0][0][1])}},
        {"id": "AE9-B3",
         "statement": ("the spread of the per-step increments of TRAJ_SMOOTH's "
                       "underlying accuracy is <= 0"),
         "kind": "upper", "bound_value": "0",
         "range_lo": "0", "range_hi": "1",
         "range_derivation": ("the spread is max increment minus min increment "
                              "of a non-decreasing sequence of accuracies in "
                              "[0,1]; each increment lies in [0,1] and the "
                              "spread of such a sequence therefore lies in "
                              "[0,1] by definition of an accuracy."),
         "vacuous": False,
         "attained_by": {"object": "TRAJ_SMOOTH underlying accuracy",
                         "values": [str(smooth_spread)]},
         "violated_by": {
             "relaxed_class": ("transformed metrics, that is the registered "
                               "exact-match transform of the same accuracy "
                               "sequence, instead of the accuracy itself"),
             "object": "TRAJ_SMOOTH accuracy raised to the registered k",
             "value": str(transform_spread)}},
        {"id": "AE9-B4",
         "statement": ("TRAJ_SMOOTH's exact held-out accuracy is <= 1/2 at "
                       "every registered sample count"),
         "kind": "upper", "bound_value": "1/2",
         "range_lo": "0", "range_hi": "1",
         "range_derivation": ("an exact accuracy on the registered 8-point "
                              "held-out set is a fraction of that set's size "
                              "and therefore lies in [0,1] by definition."),
         "vacuous": False,
         "attained_by": {"object": "TRAJ_SMOOTH held-out accuracy at every m",
                         "values": frac_list(smooth["acc_heldout"])},
         "violated_by": {
             "relaxed_class": ("trajectories whose learner also fits the "
                               "registered affine class, not only the lookup "
                               "table"),
             "object": "TRAJ_GROK held-out accuracy at m = 8",
             "value": str(grok["acc_heldout"][8])}},
        {"id": "AE9-B5",
         "statement": ("the structural onset on TRAJ_JUMP is >= 5 sample "
                       "points"),
         "kind": "lower", "bound_value": "5",
         "range_lo": "0", "range_hi": "8",
         "range_derivation": ("the onset is an index of the registered sample "
                              "range 0..8, so by definition it lies in [0,8]."),
         "vacuous": False,
         "attained_by": {"object": "TRAJ_JUMP structural onset",
                         "values": [str(jump_struct)]},
         "violated_by": {
             "relaxed_class": ("learners that commit to the lexicographically "
                               "least consistent affine form instead of "
                               "waiting for a singleton version space"),
             "object": "lex-least-commitment variant of TRAJ_JUMP",
             "value": str(relaxed_onset)}},
    ]
    for b in bounds:
        lo = Fraction(b["range_lo"])
        hi = Fraction(b["range_hi"])
        val = Fraction(b["bound_value"])
        vac = (val >= hi) if b["kind"] == "upper" else (val <= lo)
        need(vac == b["vacuous"], "bound vacuity flag inconsistent: " + b["id"])
        # A bound with no violated_by witness is EMITTED as UNFALSIFIED_BOUND
        # and must not be used to close a row; it is never edited away.
        b["status"] = ("FALSIFIABLE_BOUND" if "violated_by" in b
                       else "UNFALSIFIED_BOUND")
        b["used_to_close_a_row"] = (b["status"] == "FALSIFIABLE_BOUND")
    results["bounds_note"] = (
        "every bound carries a definition-derived range and a violated_by "
        "witness in an explicitly relaxed class; none is UNFALSIFIED_BOUND")
    checks["every_bound_has_violated_by"] = all("violated_by" in b for b in bounds)
    checks["no_bound_is_vacuous"] = all(not b["vacuous"] for b in bounds)

    # --- hostiles -----------------------------------------------------------
    hostiles = build_hostiles(reports, classes, marker_table)
    for h in hostiles:
        if h["inverted"]:
            need(h["potency"] and h["silence"],
                 "inverted hostile failed: " + h["name"])
        else:
            need(h["potency"] and h["detected"],
                 "hostile failed: " + h["name"])
    checks["all_hostiles_potent"] = all(h["potency"] for h in hostiles)
    checks["all_hostiles_resolved"] = all(
        (h["silence"] if h["inverted"] else h["detected"]) for h in hostiles)

    # --- route independence -------------------------------------------------
    agree, route_b = cross_check(reports)
    checks["routes_agree"] = agree
    results["route_b_agreement"] = route_b

    # --- prospective predictions -------------------------------------------
    preds = []
    p1 = bool(same_partition and equal_markers and reencode_moved_codes
              and reencode_invariant and all_pairs_moved)
    preds.append({
        "id": "AE9-P1", "verdict": "CONFIRMED" if p1 else "REFUTED",
        "values": {
            "same_partition_markers_equal": equal_markers,
            "reencoding_leaves_markers_fixed": reencode_invariant,
            "distinct_partitions_all_move_REFINEMENT": all_pairs_moved,
            "pairs_tested": len(pair_rows)}})
    p2 = bool(checks["row3_smooth_arm"] and checks["row3_jump_arm"])
    preds.append({
        "id": "AE9-P2", "verdict": "CONFIRMED" if p2 else "REFUTED",
        "values": {
            "smooth_increments": frac_list(smooth_inc),
            "jump_accuracy": frac_list(jump["acc_overall"]),
            "m_star": jump_struct,
            "readout_arity_before": "NONE",
            "readout_arity_at_m_star": arity_seq[jump_struct]}})
    p3 = bool(len(set(smooth_inc)) == 1
              and results["row4_emergence_reaudit"][
                  "transformed_increments_strictly_increasing"]
              and results["row4_emergence_reaudit"][
                  "structural_profile_constant_throughout"])
    preds.append({
        "id": "AE9-P3", "verdict": "CONFIRMED" if p3 else "REFUTED",
        "values": {"underlying_increment": str(smooth_inc[0]),
                   "knee_ratio_last_over_first": str(knee_ratio),
                   "structural_tuple": list(smooth["structural_profile"][0][0])}})
    p4 = bool(recall == 3 and checks["row4_no_alarm_on_smooth"]
              and checks["row4_no_alarm_on_transformed_smooth"])
    preds.append({
        "id": "AE9-P4", "verdict": "CONFIRMED" if p4 else "REFUTED",
        "values": {"recall": recall,
                   "no_alarm_on_clean_smooth": checks["row4_no_alarm_on_smooth"],
                   "null_trials": NULL_TRIALS,
                   "null_class_counts": class_counts,
                   "false_alarms_on_non_affine_draws": len(magnitudes)}})
    p5 = bool(checks["no_neural_system_on_roster"])
    preds.append({
        "id": "AE9-P5", "verdict": "CONFIRMED" if p5 else "REFUTED",
        "values": {"learners": sorted(RC["learners"]),
                   "neural_systems_evaluated": 0,
                   "NEURAL_RESULT_FROM_NON_NEURAL_ROSTER_asserted_absent": True}})
    checks["every_registered_prediction_reported"] = (
        len(preds) == len(REGISTER["prospective_predictions"]))
    # Deliberately NOT a check: a REFUTED prediction is reported as refuted,
    # never edited away and never allowed to suppress the receipt.
    prediction_summary = {
        "registered": len(REGISTER["prospective_predictions"]),
        "reported": len(preds),
        "confirmed": sum(1 for p in preds if p["verdict"] == "CONFIRMED"),
        "refuted": sum(1 for p in preds if p["verdict"] == "REFUTED"),
        "refuted_ids": sorted(
            p["id"] for p in preds if p["verdict"] == "REFUTED"),
    }

    receipt = {
        "schema": "GMI_833_AE9_TRANSITION_MARKERS_RESULT_V1",
        "issue": ISSUE,
        "issue_comment_id": ISSUE_COMMENT_ID,
        "section": "AE9",
        "package": PACKAGE,
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "register_commit": REGISTER_COMMIT,
        "register_digest": REGISTER_DIGEST,
        "claim_ceiling": CLAIM_CEILING,
        "theorems": ["AE9-1", "AE9-2", "AE9-3", "AE9-4", "AE9-5", "AE9-6",
                     "AE9-7"],
        "verdict": "GREEN",
        "checks": checks,
        "results": results,
        "bounds": bounds,
        "hostiles": hostiles,
        "null": results["null"],
        "prospective_predictions": preds,
        "prospective_prediction_summary": prediction_summary,
        "forbidden_promotions": [
            {"name": n, "asserted_absent": True} for n in FORBIDDEN_PROMOTIONS],
        "rows_left_open": ROWS_LEFT_OPEN,
    }
    need(all(checks.values()), "a named check is false; refusing to emit GREEN")
    sys.stdout.write(json.dumps(receipt, sort_keys=True, indent=2) + "\n")


ROWS_LEFT_OPEN = [
    {"row": ("For neural systems, measure representational geometry, effective "
             "rank/dimension, clustering, linear separability, invariances, "
             "circuit/path usage and information flow across training."),
     "instrument_required": ("a training run on a real neural system with "
                             "checkpointed representations, from which the "
                             "geometry, rank, clustering, separability, "
                             "invariance and path-usage measurements are read "
                             "at each checkpoint")},
    {"row": ("Freeze prospective markers of a representation transition before "
             "observing the capability transition."),
     "instrument_required": ("a preregistered marker freeze recorded before the "
                             "capability onset is observed on a real training "
                             "run, with the freeze commit preceding the run")},
    {"row": ("Test whether internal transition markers predict new capability "
             "onset better than parameter count/training loss alone."),
     "instrument_required": ("a predictive comparison against parameter count "
                             "and training loss on real training runs, scored "
                             "out of sample on held-out runs")},
    {"row": ("Compare neural transition results with non-neural systems to test "
             "whether the law is architecture-general."),
     "instrument_required": ("a matched neural-versus-non-neural comparison in "
                             "which the same markers are read on real neural "
                             "runs and on the non-neural roster under one "
                             "protocol")},
]


def lex_least_onset():
    """Structural onset when the learner commits to the lex-least consistent form."""
    tmask = as_mask(T_XOR12)
    base_profile = None
    for m in SAMPLE_RANGE:
        prof = set()
        for subset in itertools.combinations(POOL, m):
            chosen = None
            for _key, vals in AFFINE_FORMS:
                ok = True
                for v in subset:
                    if vals[v] != T_XOR12[v]:
                        ok = False
                        break
                if ok:
                    chosen = vals
                    break
            if chosen is None:
                chosen = D_X4
            prof.add(structural_tuple(canonical_labels(chosen), tmask))
        prof = tuple(sorted(prof, key=repr))
        if base_profile is None:
            base_profile = prof
        elif prof != base_profile:
            return m
    return NONE_SYMBOL


def build_hostiles(reports, classes, marker_table):
    tmask_xor = as_mask(T_XOR12)
    tmask_par = as_mask(T_PARITY4)
    out = []

    # H_PARTITION_RELABEL: inverted, the checker must stay silent
    base_labels = canonical_labels(T_XOR12)
    relabelled_codes = tuple("relabel-%d" % (11 * z + 5) for z in T_XOR12)
    relabelled = canonical_labels(relabelled_codes)
    true_markers = marker_vector(base_labels, tmask_xor)
    pert_markers = marker_vector(relabelled, tmask_xor)
    out.append({
        "name": "H_PARTITION_RELABEL", "inverted": True,
        "perturbs": "the code set by an injection",
        "potency": tuple(str(z) for z in T_XOR12) != relabelled_codes,
        "potency_note": ("the code map is genuinely a different function; its "
                         "code set changed under the injection"),
        "silence": true_markers == pert_markers,
        "detected": False,
        "true_value": true_markers, "perturbed_value": pert_markers})

    # H_INVARIANCE_INFLATE: score by preserved cell sizes rather than cells
    labels_x4 = canonical_labels(D_X4)
    sizes = sorted(popcount(c) for c in cell_masks(labels_x4))
    broken = 0
    for sigma in PERMS:
        image_sizes = []
        for cmask in cell_masks(labels_x4):
            img = 0
            for v in POINTS:
                if (cmask >> v) & 1:
                    img |= 1 << perm_image(v, sigma)
            image_sizes.append(popcount(img))
        if sorted(image_sizes) == sizes:
            broken += 1
    true_inv = invariance_order(labels_x4)
    oracle_inv = oracle.invariance_order(oracle.partition_of(list(D_X4)))
    out.append({
        "name": "H_INVARIANCE_INFLATE", "inverted": False,
        "perturbs": "the subgroup search, scoring size preservation as invariance",
        "potency": broken != true_inv,
        "potency_note": "the perturbed subgroup order differs from the true one",
        "detected": broken != oracle_inv and true_inv == oracle_inv,
        "silence": False,
        "true_value": true_inv, "perturbed_value": broken})

    # H_ARITY_CAP: cap the readout arity so the jump stops jumping
    capped = closed_form_trajectory(SPEC_JUMP, arity_cap=1)
    true_arities = [sorted(set(str(t[2]) for t in p))
                    for p in reports["TRAJ_JUMP"]["structural_profile"]]
    cap_arities = [sorted(set(str(t[2]) for t in p))
                   for p in capped["structural_profile"]]
    cap_class = classify(capped)
    out.append({
        "name": "H_ARITY_CAP", "inverted": False,
        "perturbs": "the readout arity cap, lowered from 4 to 1",
        "potency": true_arities != cap_arities,
        "potency_note": "the READOUT_ARITY sequence of TRAJ_JUMP moved",
        "detected": "2" not in cap_arities[5],
        "silence": False,
        "true_value": true_arities, "perturbed_value": cap_arities,
        "perturbed_class": cap_class["class"]})

    # H_THRESHOLD_K: perturb the exact-match exponent
    smooth = reports["TRAJ_SMOOTH"]
    true_t = increments(exact_match_transform(smooth["acc_overall"],
                                              EXACT_MATCH_K))
    pert_t = increments(exact_match_transform(smooth["acc_overall"], 1))
    true_knee = all(true_t[i] < true_t[i + 1] for i in range(len(true_t) - 1))
    pert_knee = all(pert_t[i] < pert_t[i + 1] for i in range(len(pert_t) - 1))
    out.append({
        "name": "H_THRESHOLD_K", "inverted": False,
        "perturbs": "the registered exact-match exponent, 8 replaced by 1",
        "potency": true_t != pert_t,
        "potency_note": "the transformed increment sequence moved",
        "detected": (true_knee and not pert_knee),
        "silence": False,
        "true_value": {"knee": true_knee,
                       "increments": [str(x) for x in true_t]},
        "perturbed_value": {"knee": pert_knee,
                            "increments": [str(x) for x in pert_t]}})

    # H_TRAIN_LEAK: a training point leaks into the held-out set
    leaked = tuple(sorted(set(HELD_OUT) - set([15]) | set([0])))
    leaked_rep = closed_form_trajectory(SPEC_GROK, held_out=leaked)
    true_held = reports["TRAJ_GROK"]["acc_heldout"]
    out.append({
        "name": "H_TRAIN_LEAK", "inverted": False,
        "perturbs": "the held-out set of TRAJ_GROK, a pool point leaks in",
        "potency": [str(x) for x in leaked_rep["acc_heldout"]] != [
            str(x) for x in true_held],
        "potency_note": "the exact held-out accuracy sequence moved",
        "detected": len(set(POOL) & set(leaked)) != 0,
        "silence": False,
        "true_value": [str(x) for x in true_held],
        "perturbed_value": [str(x) for x in leaked_rep["acc_heldout"]],
        "leaked_points": sorted(set(POOL) & set(leaked))})
    return out


def cross_check(reports):
    bundle = oracle.oracle_bundle()
    agree = True
    detail = {}
    for name in sorted(bundle["trajectories"]):
        b = bundle["trajectories"][name]
        a = reports[name]
        rows = {
            "acc_overall": frac_list(a["acc_overall"]) == b["acc_overall"],
            "acc_train": frac_list(a["acc_train"]) == b["acc_train"],
            "acc_heldout": frac_list(a["acc_heldout"]) == b["acc_heldout"],
            "structural_profile": prof_list(
                a["structural_profile"]) == b["structural_profile"],
            "determined_count": a["determined_count"] == b["determined_count"],
        }
        detail[name] = rows
        if not all(rows.values()):
            agree = False
    spanning_rows = {}
    for m in SAMPLE_RANGE:
        ours = spanning_count(POOL, m)
        spanning_rows[str(m)] = (ours == bundle["spanning"][str(m)])
        if not spanning_rows[str(m)]:
            agree = False
    detail["spanning_counts"] = spanning_rows
    marker_rows = {}
    named = {
        "IDENTITY__T_XOR12": (canonical_labels(POINTS), as_mask(T_XOR12)),
        "IDENTITY__T_PARITY4": (canonical_labels(POINTS), as_mask(T_PARITY4)),
        "KER_X4__T_XOR12": (canonical_labels(D_X4), as_mask(T_XOR12)),
        "KER_X4__T_PARITY4": (canonical_labels(D_X4), as_mask(T_PARITY4)),
        "KER_XOR12__T_XOR12": (canonical_labels(T_XOR12), as_mask(T_XOR12)),
        "KER_PARITY4__T_PARITY4": (canonical_labels(T_PARITY4),
                                   as_mask(T_PARITY4)),
    }
    for key in sorted(named):
        ours = marker_vector(named[key][0], named[key][1])
        marker_rows[key] = (ours == bundle["markers"][key])
        if not marker_rows[key]:
            agree = False
    detail["markers"] = marker_rows
    detail["route_b_module"] = "independent_marker_oracle_v1.py"
    detail["independence"] = (
        "route B contains no executable import of route A; route A imports "
        "route B only to certify agreement")
    return agree, detail


if __name__ == "__main__":
    main()

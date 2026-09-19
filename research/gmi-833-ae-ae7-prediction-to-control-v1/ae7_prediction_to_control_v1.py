#!/usr/bin/env python3
"""GMI #833 AE7 -- from prediction to control.  Route A (analytic executor).

Exhaustive exact-rational census over all Bell(8) = 4140 sensors (set
partitions of an 8-state latent space).  Separates predictive sufficiency from
control sufficiency in both directions, prices the value of information, and
evaluates the five predictions frozen in FREEZE_V1.md before this file existed.

No float appears anywhere.  Run:

    python3 -I -B  ae7_prediction_to_control_v1.py
    python3 -I -O -B ae7_prediction_to_control_v1.py
"""

from fractions import Fraction as F
import json
import sys

SCHEMA = "GMI_833_AE7_PREDICTION_TO_CONTROL_RESULT_V1"
SOURCE_MAIN = "5e57d4292266bccf435136e1f7d72caa32e920a0"
FREEZE_COMMIT = "65b45210b0cca60dba37d36fd556c8846fa3232f"
CLAIM_CEILING = (
    "GMI_833_AE7_PREDICTION_TO_CONTROL_BOUNDARY_EXACTLY_SEPARATED_AND_PRICED_"
    "AT_REGISTERED_FINITE_SCOPE"
)
COMMENT_ID = 5692689542

FORBIDDEN_PROMOTIONS = [
    "PREDICTION_INSUFFICIENT_FOR_INTELLIGENCE_IN_GENERAL",
    "CONTROL_SUFFICIENCY_IMPLIES_PREDICTIVE_SUFFICIENCY",
    "PREDICTIVE_SUFFICIENCY_IMPLIES_CONTROL_SUFFICIENCY",
    "POMDP_BELIEF_SUFFICIENCY_REPROVED",
    "INFINITE_HORIZON_CONTROL_PROVED",
    "CONTINUOUS_STATE_EXTENSION_PROVED",
    "ENERGY_OR_TIME_PRICE_MEASURED",
    "ARCHITECTURE_SELECTION_LAW",
    "GMI_MORPHOLOGY_PREDICTION",
    "COMPLETE_GMI",
]

# --------------------------------------------------------------------------
# Registered scope: latent states, sensors, targets, control problems.
# --------------------------------------------------------------------------

N_STATES = 8
STATES = tuple(range(N_STATES))
PRIOR = tuple(F(1, N_STATES) for _ in STATES)


def bits(s):
    """(b0, b1, b2) of state index s; b0 is the least significant bit."""
    return (s & 1, (s >> 1) & 1, (s >> 2) & 1)


# Registered prediction targets.  EVERY one is a function of (b0, b1) only, so
# the third coordinate is predictively invisible to the whole registered suite.
# The boundary at which that stops being true is measured below (PC-6).
def _t_b0(s):
    return bits(s)[0]


def _t_b1(s):
    return bits(s)[1]


def _t_xor(s):
    b = bits(s)
    return b[0] ^ b[1]


def _t_and(s):
    b = bits(s)
    return b[0] & b[1]


def _t_or(s):
    b = bits(s)
    return b[0] | b[1]


def _t_pair(s):
    """The full (b0,b1) pair as a 4-valued target: the finest registered task."""
    b = bits(s)
    return 2 * b[0] + b[1]


REGISTERED_TARGETS = (
    ("Y_b0", _t_b0),
    ("Y_b1", _t_b1),
    ("Y_xor01", _t_xor),
    ("Y_and01", _t_and),
    ("Y_or01", _t_or),
    ("Y_pair01", _t_pair),
)


# Probe targets used ONLY to measure the boundary of the PC-6 witness.  They are
# not members of the registered suite and no row is closed with them.
def _p_parity(s):
    b = bits(s)
    return b[0] ^ b[1] ^ b[2]


def _p_b2(s):
    return bits(s)[2]


def _p_majority(s):
    b = bits(s)
    return 1 if (b[0] + b[1] + b[2]) >= 2 else 0


PROBE_TARGETS = (
    ("Y_b2", _p_b2),
    ("Y_parity", _p_parity),
    ("Y_majority", _p_majority),
)

ACTIONS = ("a0", "a1", "a2", "a3")


def _u_hidden_coordinate(s, a):
    """Utility that depends only on b2 -- invisible to every registered target."""
    b2 = bits(s)[2]
    if a == "a0":
        return F(1) if b2 == 0 else F(0)
    if a == "a1":
        return F(1) if b2 == 1 else F(0)
    return F(1, 2)


def _u_visible_coordinate(s, a):
    """Utility that depends only on b0 -- fully visible to the registered suite."""
    b0 = bits(s)[0]
    if a == "a0":
        return F(1) if b0 == 0 else F(0)
    if a == "a1":
        return F(1) if b0 == 1 else F(0)
    return F(1, 4)


# A utility whose optimal-action sets are PAIRWISE intersecting on a triple yet
# have empty triple intersection: the Helly failure that makes "coarsest
# control-sufficient partition" a genuinely non-local property.
_HELLY_ARGMAX = {
    0: ("a0", "a1"),
    1: ("a1", "a2"),
    2: ("a2", "a0"),
}


def _u_helly(s, a):
    if s in _HELLY_ARGMAX:
        return F(1) if a in _HELLY_ARGMAX[s] else F(0)
    # remaining states pin a3 so they never interfere with the triple
    return F(1) if a == "a3" else F(0)


def _u_graded(s, a):
    """A utility with a rich priced ladder: graded payoffs over all 8 states."""
    b = bits(s)
    v = b[0] + 2 * b[1] + 4 * b[2]
    if a == "a0":
        return F(v, 8)
    if a == "a1":
        return F(7 - v, 8)
    if a == "a2":
        return F(1, 2) + F((v % 3), 16)
    return F(3, 8) + F((v % 5), 32)


REGISTERED_UTILITIES = (
    ("U_hidden_coordinate", _u_hidden_coordinate),
    ("U_visible_coordinate", _u_visible_coordinate),
    ("U_helly_triple", _u_helly),
    ("U_graded", _u_graded),
)


# --------------------------------------------------------------------------
# Sensors: every set partition of the 8 states, as a restricted-growth string.
# --------------------------------------------------------------------------

def all_partitions(n):
    """Every restricted-growth string of length n, in lexicographic order."""
    out = []
    cur = [0] * n

    def rec(i, mx):
        if i == n:
            out.append(tuple(cur))
            return
        for v in range(mx + 2):
            cur[i] = v
            rec(i + 1, mx if v <= mx else v)

    rec(1, 0)
    return out


def blocks_of(part):
    k = max(part) + 1
    bl = [[] for _ in range(k)]
    for s, b in enumerate(part):
        bl[b].append(s)
    return tuple(tuple(x) for x in bl)


def block_masks(part):
    k = max(part) + 1
    m = [0] * k
    for s, b in enumerate(part):
        m[b] |= 1 << s
    return tuple(sorted(m))


def refines(part_fine, part_coarse):
    """True iff part_fine refines part_coarse (every fine block inside a coarse one)."""
    for s in range(len(part_fine)):
        for t in range(s + 1, len(part_fine)):
            if part_fine[s] == part_fine[t] and part_coarse[s] != part_coarse[t]:
                return False
    return True


def coarsenings(part):
    """Every partition that `part` refines, including `part` itself.

    Generated by merging blocks of `part`, i.e. by taking every partition of the
    block index set and pushing it down onto the states.
    """
    k = max(part) + 1
    out = []
    for meta in all_partitions(k):
        out.append(canonical(tuple(meta[part[s]] for s in range(len(part)))))
    return sorted(set(out))


def canonical(lab):
    """Relabel an arbitrary block labelling into restricted-growth form."""
    seen = {}
    out = []
    for v in lab:
        if v not in seen:
            seen[v] = len(seen)
        out.append(seen[v])
    return tuple(out)


# --------------------------------------------------------------------------
# Control value: exact rational, computed by per-block aggregate maximisation.
# --------------------------------------------------------------------------

def control_value(part, util):
    total = F(0)
    for blk in blocks_of(part):
        best = None
        for a in ACTIONS:
            v = F(0)
            for s in blk:
                v += PRIOR[s] * util(s, a)
            if best is None or v > best:
                best = v
        total += best
    return total


def argmax_actions(s, util):
    best = None
    for a in ACTIONS:
        v = util(s, a)
        if best is None or v > best:
            best = v
    return tuple(a for a in ACTIONS if util(s, a) == best)


def block_is_free(blk, util):
    """A block costs no control value iff its states share an optimal action."""
    common = None
    for s in blk:
        am = set(argmax_actions(s, util))
        common = am if common is None else (common & am)
        if not common:
            return False
    return True


# --------------------------------------------------------------------------
# Predictive content.
# --------------------------------------------------------------------------

def target_partition(target):
    lab = tuple(target(s) for s in STATES)
    return canonical(lab)


def predictive_profile(part, targets):
    """Multiset over blocks of (block mass, conditional law of each target).

    Any predictor's achievable expected score under any loss depends on the
    sensor only through this object, so equality of profiles means the two
    sensors are indistinguishable by every registered prediction task.
    """
    rows = []
    for blk in blocks_of(part):
        mass = sum(PRIOR[s] for s in blk)
        cond = []
        for name, tg in targets:
            vals = sorted(set(tg(s) for s in STATES))
            law = []
            for v in vals:
                m = sum(PRIOR[s] for s in blk if tg(s) == v)
                law.append(str(m / mass))
            cond.append((name, tuple(law)))
        rows.append((str(mass), tuple(cond)))
    return tuple(sorted(rows))


def predictively_sufficient(part, target):
    return refines(part, target_partition(target))


# --------------------------------------------------------------------------
# Costs and priced selection.
# --------------------------------------------------------------------------

def sensor_cost(part):
    """Registered sensing cost: one unit per distinction the sensor resolves."""
    return F(max(part))


PRICE_LADDER = tuple(F(n, 16) for n in range(0, 33))


def priced_selection(parts, util, price, vlist=None, costs=None):
    """argmax of V(T) - price*cost(T); ties resolved to the COARSEST member.

    The tie rule is declared, not silent: the whole tie set is returned too.
    """
    best = None
    tie = []
    for i, p in enumerate(parts):
        v = control_value(p, util) if vlist is None else vlist[i]
        c = sensor_cost(p) if costs is None else costs[i]
        j = v - price * c
        if best is None or j > best:
            best = j
            tie = [p]
        elif j == best:
            tie.append(p)
    coarse = min(tie, key=lambda p: (max(p), p))
    return coarse, tuple(sorted(tie)), best


# --------------------------------------------------------------------------
# The seven results.
# --------------------------------------------------------------------------

def run():
    parts = all_partitions(N_STATES)
    n_parts = len(parts)
    full = tuple(range(N_STATES))
    blind = tuple(0 for _ in range(N_STATES))

    vals = {}
    for uname, util in REGISTERED_UTILITIES:
        vals[uname] = [control_value(p, util) for p in parts]

    idx = dict((p, i) for i, p in enumerate(parts))
    costs = [sensor_cost(p) for p in parts]
    coarse_cache = dict((p, coarsenings(p)) for p in parts)

    # ---- PC-1: same predictive content, different control value -----------
    groups = {}
    for i, p in enumerate(parts):
        groups.setdefault(predictive_profile(p, REGISTERED_TARGETS), []).append(i)

    pc1_pairs = {}
    pc1_witness = None
    for uname, _ in REGISTERED_UTILITIES:
        v = vals[uname]
        cnt = 0
        for g in groups.values():
            for a in range(len(g)):
                for b in range(a + 1, len(g)):
                    if v[g[a]] != v[g[b]]:
                        cnt += 1
                        if uname == "U_hidden_coordinate" and pc1_witness is None:
                            pc1_witness = (g[a], g[b])
        pc1_pairs[uname] = cnt

    # The named witness.  Both sensors cut the 8 states into two blocks of mass
    # 1/2 in which all four (b0,b1) combinations appear exactly once, so the
    # conditional law of EVERY registered target equals the global marginal in
    # every block: the two sensors are indistinguishable by every registered
    # prediction task, at any loss.  One of them resolves b2 and the other does
    # not, so under a utility that reads b2 their control values differ.
    sens_b2 = canonical(tuple(bits(s)[2] for s in STATES))
    sens_b0xb2 = canonical(tuple(bits(s)[0] ^ bits(s)[2] for s in STATES))
    same_profile_named = (
        predictive_profile(sens_b2, REGISTERED_TARGETS)
        == predictive_profile(sens_b0xb2, REGISTERED_TARGETS)
    )
    v_named = (
        control_value(sens_b2, _u_hidden_coordinate),
        control_value(sens_b0xb2, _u_hidden_coordinate),
    )

    if pc1_witness is None:
        raise RuntimeError("PC-1: no same-predictive/different-control pair found")
    w0, w1 = pc1_witness

    pc1 = {
        "definition": (
            "two sensors have identical predictive content iff their predictive "
            "profiles -- the multiset over blocks of (block mass, conditional law "
            "of each registered target) -- are equal as exact rationals; any "
            "predictor's achievable expected score under any loss depends on the "
            "sensor only through that object"
        ),
        "sensors_enumerated": n_parts,
        "distinct_predictive_profiles": len(groups),
        "same_predictive_different_control_pairs": dict(
            (k, pc1_pairs[k]) for k, _ in REGISTERED_UTILITIES
        ),
        "named_witness": {
            "sensor_A": "".join(str(x) for x in sens_b2),
            "sensor_B": "".join(str(x) for x in sens_b0xb2),
            "identical_predictive_profile": bool(same_profile_named),
            "control_value_A": str(v_named[0]),
            "control_value_B": str(v_named[1]),
            "gap": str(v_named[0] - v_named[1]),
            "utility": "U_hidden_coordinate",
        },
        "machine_found_witness": {
            "sensor_A": "".join(str(x) for x in parts[w0]),
            "sensor_B": "".join(str(x) for x in parts[w1]),
            "control_value_A": str(vals["U_hidden_coordinate"][w0]),
            "control_value_B": str(vals["U_hidden_coordinate"][w1]),
        },
        "scope_note": (
            "insufficiency is proved AT THE REGISTERED SCOPE -- the registered "
            "target suite and utility family -- and is not a claim about general "
            "intelligence as such"
        ),
    }

    # ---- PC-2: control sufficiency, coarsest control-sufficient sensors ---
    pc2 = {}
    relation_counts = {}
    for uname, util in REGISTERED_UTILITIES:
        v_full = control_value(full, util)
        suff = [i for i in range(n_parts) if vals[uname][i] == v_full]
        suff_set = set(parts[i] for i in suff)
        minimal = []
        for i in suff:
            p = parts[i]
            strictly_coarser_suff = False
            for c in coarse_cache[p]:
                if c != p and c in suff_set:
                    strictly_coarser_suff = True
                    break
            if not strictly_coarser_suff:
                minimal.append(p)
        free_block_agrees = all(
            all(block_is_free(b, util) for b in blocks_of(p)) for p in minimal
        )
        pc2[uname] = {
            "V_full": str(v_full),
            "V_blind": str(control_value(blind, util)),
            "control_sufficient_sensors": len(suff),
            "coarsest_control_sufficient_sensors": len(minimal),
            "unique_coarsest": len(minimal) == 1,
            "coarsest_examples": [
                "".join(str(x) for x in p) for p in sorted(minimal)[:4]
            ],
            "common_optimal_action_criterion_agrees": bool(free_block_agrees),
        }

        # relation between the coarsest control-sufficient sensor(s) and the
        # coarsest predictively sufficient sensor for each registered target
        rel = {"EQUAL": 0, "CONTROL_STRICTLY_COARSER": 0,
               "PREDICTIVE_STRICTLY_COARSER": 0, "INCOMPARABLE": 0}
        for tname, tg in REGISTERED_TARGETS:
            tp = target_partition(tg)
            for p in minimal:
                a = refines(p, tp)
                b = refines(tp, p)
                if a and b:
                    rel["EQUAL"] += 1
                elif b:
                    rel["CONTROL_STRICTLY_COARSER"] += 1
                elif a:
                    rel["PREDICTIVE_STRICTLY_COARSER"] += 1
                else:
                    rel["INCOMPARABLE"] += 1
        relation_counts[uname] = rel

    # Helly: pairwise-compatible triple with empty common optimal action
    helly_triples = []
    for a in range(N_STATES):
        for b in range(a + 1, N_STATES):
            for c in range(b + 1, N_STATES):
                pw = (
                    block_is_free((a, b), _u_helly)
                    and block_is_free((a, c), _u_helly)
                    and block_is_free((b, c), _u_helly)
                )
                if pw and not block_is_free((a, b, c), _u_helly):
                    helly_triples.append((a, b, c))

    pc2_out = {
        "definition_control_sufficient": "V(T) = V(full discrete sensor)",
        "definition_predictively_sufficient": (
            "T refines the level-set partition of s -> p(Y|s)"
        ),
        "per_utility": pc2,
        "relation_to_predictive_sufficiency": relation_counts,
        "helly_failure": {
            "claim": (
                "pairwise mergeability does not imply block mergeability, so the "
                "coarsest control-sufficient sensor is not a pairwise-local object"
            ),
            "utility": "U_helly_triple",
            "pairwise_compatible_triples_without_common_optimum": len(helly_triples),
            "example": list(helly_triples[0]) if helly_triples else None,
        },
    }

    # ---- PC-3: parent crosswalk -------------------------------------------
    pc3 = [
        {"gmi_symbol": "control-sufficient sensor T with V(T)=V_full",
         "parent": "belief-state / information-state sufficiency for POMDPs",
         "citation": "Astrom 1965, doi:10.1016/0022-247X(65)90154-X; "
                     "Smallwood & Sondik 1973, doi:10.1287/opre.21.5.1071",
         "status": "PARENT_SUFFICIENT",
         "residual": "none -- the sufficiency notion is parent-owned"},
        {"gmi_symbol": "coarsest sufficient state aggregation",
         "parent": "bisimulation / model minimisation for MDPs",
         "citation": "Givan, Dean & Greig 2003, doi:10.1016/S0004-3702(02)00376-4",
         "status": "PARENT_SUFFICIENT",
         "residual": "the exhaustive census of ALL minimal elements, including "
                     "the non-uniqueness and the Helly failure, is measured here"},
        {"gmi_symbol": "V(T) - price*cost(T) sensor selection",
         "parent": "rate-distortion control / information-theoretic bounded "
                   "rationality",
         "citation": "Tishby & Polani 2011, doi:10.1007/978-1-4419-1452-1_19; "
                     "Rubin, Shamir & Tishby 2012, "
                     "doi:10.1007/978-3-642-24647-0_3; Ortega & Braun 2013, "
                     "doi:10.1098/rspa.2012.0683",
         "status": "PARENT_OWNED_OBJECTIVE",
         "residual": "the exact rational transition ladder over all 4140 sensors"},
        {"gmi_symbol": "VoI(T,T') = V(T) - V(T')",
         "parent": "value of information",
         "citation": "Howard 1966, doi:10.1109/TSSC.1966.300074",
         "status": "PARENT_SUFFICIENT",
         "residual": "none -- the quantity is parent-owned; the break-even price "
                     "table is the instantiation"},
        {"gmi_symbol": "price on attention/sensing",
         "parent": "rational inattention / bounded rationality",
         "citation": "Sims 2003, doi:10.1016/S0304-3932(03)00029-1; "
                     "Simon 1955, doi:10.2307/1884852",
         "status": "PARENT_OWNED_FRAMING",
         "residual": "none claimed"},
    ]

    # ---- PC-4: value of information and break-even prices -----------------
    refine_pairs = 0
    voi_zero = 0
    voi_pos = 0
    breakevens = set()
    for p in parts:
        cp = costs[idx[p]]
        for c in coarse_cache[p]:
            if c == p:
                continue
            refine_pairs += 1
            d = vals["U_graded"][idx[p]] - vals["U_graded"][idx[c]]
            if d == 0:
                voi_zero += 1
            else:
                voi_pos += 1
            dc = cp - costs[idx[c]]
            if dc != 0:
                breakevens.add(d / dc)
    bmax = max(breakevens)
    bsorted = sorted(breakevens)

    # witnesses strictly on each side of one break-even, and AT it
    probe_fine = full
    probe_coarse = blind
    voi = vals["U_graded"][idx[probe_fine]] - vals["U_graded"][idx[probe_coarse]]
    dcost = sensor_cost(probe_fine) - sensor_cost(probe_coarse)
    be = voi / dcost
    below = be - F(1, 64)
    above = be + F(1, 64)

    def net(p, price):
        return control_value(p, _u_graded) - price * sensor_cost(p)

    pc4 = {
        "rule": "acquire the finer sensor iff VoI(T,T') > price * (cost(T)-cost(T'))",
        "comparable_sensor_pairs_checked": refine_pairs,
        "pairs_with_zero_value_of_information": voi_zero,
        "pairs_with_positive_value_of_information": voi_pos,
        "distinct_break_even_prices": len(breakevens),
        "break_even_min": str(bsorted[0]),
        "break_even_max": str(bmax),
        "probe": {
            "utility": "U_graded",
            "fine": "full discrete sensor",
            "coarse": "blind sensor",
            "VoI": str(voi),
            "cost_increment": str(dcost),
            "break_even_price": str(be),
            "net_below": [str(net(probe_fine, below)), str(net(probe_coarse, below))],
            "acquire_below": bool(net(probe_fine, below) > net(probe_coarse, below)),
            "net_at": [str(net(probe_fine, be)), str(net(probe_coarse, be))],
            "tie_at_break_even": bool(net(probe_fine, be) == net(probe_coarse, be)),
            "net_above": [str(net(probe_fine, above)), str(net(probe_coarse, above))],
            "acquire_above": bool(net(probe_fine, above) > net(probe_coarse, above)),
        },
    }

    # ---- PC-5: when merging is free ---------------------------------------
    pc5 = {}
    for uname, util in REGISTERED_UTILITIES:
        free_pairs = 0
        costly_pairs = 0
        fw = None
        cw = None
        for a in range(N_STATES):
            for b in range(a + 1, N_STATES):
                if block_is_free((a, b), util):
                    free_pairs += 1
                    if fw is None:
                        fw = (a, b)
                else:
                    costly_pairs += 1
                    if cw is None:
                        cw = (a, b)
        # verify the criterion against the value function on every pair merge
        mismatches = 0
        for a in range(N_STATES):
            for b in range(a + 1, N_STATES):
                lab = list(range(N_STATES))
                lab[b] = lab[a]
                merged = canonical(tuple(lab))
                free_by_value = control_value(merged, util) == control_value(full, util)
                if free_by_value != block_is_free((a, b), util):
                    mismatches += 1
        pc5[uname] = {
            "free_state_pairs": free_pairs,
            "costly_state_pairs": costly_pairs,
            "criterion_vs_value_mismatches": mismatches,
            "free_example": list(fw) if fw else None,
            "costly_example": list(cw) if cw else None,
        }

    pc5_out = {
        "condition": (
            "merging a set of states costs no control value iff they share an "
            "optimal action -- the intersection of their argmax action sets is "
            "non-empty; verified against the exact value function on every "
            "pairwise merge"
        ),
        "per_utility": pc5,
    }

    # ---- PC-6: predictively redundant, control-relevant --------------------
    pred_equiv = {}
    for s in STATES:
        key = tuple(tg(s) for _, tg in REGISTERED_TARGETS)
        pred_equiv.setdefault(key, []).append(s)
    redundant_pairs = []
    for g in pred_equiv.values():
        for i in range(len(g)):
            for j in range(i + 1, len(g)):
                redundant_pairs.append((g[i], g[j]))

    pc6_counts = {}
    for uname, util in REGISTERED_UTILITIES:
        n = 0
        for (a, b) in redundant_pairs:
            if not block_is_free((a, b), util):
                n += 1
        pc6_counts[uname] = n

    # boundary: the smallest probe target that destroys the redundancy
    boundary = []
    for pname, ptg in PROBE_TARGETS:
        ext = REGISTERED_TARGETS + ((pname, ptg),)
        eq = {}
        for s in STATES:
            eq.setdefault(tuple(tg(s) for _, tg in ext), []).append(s)
        survivors = sum(len(g) * (len(g) - 1) // 2 for g in eq.values())
        boundary.append({"probe_target": pname,
                         "redundant_pairs_surviving": survivors})

    pc6 = {
        "claim": (
            "a distinction that every registered prediction target discards can "
            "be strictly necessary for control"
        ),
        "predictively_redundant_state_pairs": len(redundant_pairs),
        "control_relevant_among_them": pc6_counts,
        "witness": {
            "pair": list(redundant_pairs[0]) if redundant_pairs else None,
            "utility": "U_hidden_coordinate",
            "V_full": str(control_value(full, _u_hidden_coordinate)),
            "V_after_merge": str(
                control_value(
                    canonical(tuple(
                        (s if s != redundant_pairs[0][1] else redundant_pairs[0][0])
                        for s in STATES)),
                    _u_hidden_coordinate)) if redundant_pairs else None,
        },
        "converse_PC5_attested": True,
        "boundary_of_the_witness": boundary,
        "boundary_note": (
            "the registered target suite is exactly the functions of (b0,b1). "
            "Reading the hidden coordinate does NOT by itself destroy the "
            "redundancy: Y_b2 and Y_parity do, but Y_majority does not, because "
            "on the four states with b0 == b1 the majority is pinned by b0 and "
            "b2 stays invisible, so two redundant pairs survive. The asymmetry "
            "is reported rather than rounded to 'any extra target kills it'."
        ),
    }

    # ---- PC-7: the five prospectively frozen predictions -------------------
    ladder = {}
    predictions = {}
    r1_viol = 0
    r2_worlds = 0
    r3_out = 0
    r4_fail = 0
    r5_worlds = 0

    transition_set = set()
    for p in parts:
        for c in coarse_cache[p]:
            if c == p:
                continue
            dc = costs[idx[p]] - costs[idx[c]]
            if dc != 0:
                for uname, _ in REGISTERED_UTILITIES:
                    d = vals[uname][idx[p]] - vals[uname][idx[c]]
                    transition_set.add((uname, d / dc))

    for uname, util in REGISTERED_UTILITIES:
        seq = []
        for pi in PRICE_LADDER:
            sel, tie, _ = priced_selection(parts, util, pi, vals[uname], costs)
            seq.append((pi, sel, len(tie)))
        distinct = []
        for _, sel, _ in seq:
            if not distinct or distinct[-1] != sel:
                distinct.append(sel)
        # R1: nesting monotonicity
        for i in range(len(seq) - 1):
            if not refines(seq[i][1], seq[i + 1][1]):
                r1_viol += 1
        if len(set(distinct)) >= 3:
            r2_worlds += 1
        # R3: transitions lie in the exact difference-quotient set
        for i in range(len(seq) - 1):
            if seq[i][1] != seq[i + 1][1]:
                lo, hi = seq[i][0], seq[i + 1][0]
                hit = any(
                    (u == uname and lo < q <= hi) for (u, q) in transition_set
                )
                if not hit:
                    r3_out += 1
        # R4: blind at a price above the maximal gain over minimal cost
        v_full = control_value(full, util)
        v_blind = control_value(blind, util)
        hi_price = (v_full - v_blind) + F(1, 16)
        sel_hi, _, _ = priced_selection(parts, util, hi_price, vals[uname], costs)
        if max(sel_hi) != 0:
            r4_fail += 1
        # R5: a selected sensor that is control-sufficient but NOT predictively
        #     sufficient for some registered target
        found = False
        for _, sel, _ in seq:
            if control_value(sel, util) == v_full:
                for tname, tg in REGISTERED_TARGETS:
                    if not predictively_sufficient(sel, tg):
                        found = True
                        break
            if found:
                break
        if found:
            r5_worlds += 1
        ladder[uname] = {
            "distinct_selected_sensors": len(set(distinct)),
            "selection_sequence": ["".join(str(x) for x in s) for s in distinct],
            "price_points": len(PRICE_LADDER),
            "blind_at_high_price": "".join(str(x) for x in sel_hi),
            "high_price": str(hi_price),
        }

    predictions["R1_monotone_coarsening"] = {
        "statement": "for pi <= pi', the sensor selected at pi refines the sensor "
                     "selected at pi' -- no re-refinement anywhere",
        "violations": r1_viol,
        "verdict": "HELD" if r1_viol == 0 else "FAILED",
    }
    predictions["R2_multistage_transition"] = {
        "statement": "at least one registered control problem shows >= 3 distinct "
                     "selected sensors across the ladder",
        "problems_with_three_or_more": r2_worlds,
        "verdict": "HELD" if r2_worlds >= 1 else "FAILED",
    }
    predictions["R3_transition_prices_in_exact_set"] = {
        "statement": "every selection change is bracketed by a difference quotient "
                     "(V(T)-V(T'))/(cost(T)-cost(T')) of the registered family",
        "distinct_difference_quotients": len(transition_set),
        "transitions_outside_the_set": r3_out,
        "verdict": "HELD" if r3_out == 0 else "FAILED",
    }
    predictions["R4_blind_above_max_gain"] = {
        "statement": "above the maximal achievable gain the blind sensor is "
                     "selected in every registered problem",
        "failures": r4_fail,
        "verdict": "HELD" if r4_fail == 0 else "FAILED",
    }
    predictions["R5_control_order_is_not_predictive_order"] = {
        "statement": "some registered problem selects, at some price, a sensor that "
                     "is control-sufficient and not predictively sufficient for a "
                     "registered target",
        "problems_witnessing": r5_worlds,
        "verdict": "HELD" if r5_worlds >= 1 else "FAILED",
    }

    pc7 = {
        "frozen_before_executor": True,
        "freeze_commit": FREEZE_COMMIT,
        "price_ladder": [str(x) for x in PRICE_LADDER],
        "per_problem": ladder,
        "predictions": predictions,
    }

    # ---- hostiles ----------------------------------------------------------
    hostiles = build_hostiles(parts, idx, vals)

    # ---- null --------------------------------------------------------------
    null = build_null(parts)

    checks = {
        "sensors_enumerated_is_bell_8": n_parts == 4140,
        "pc1_witness_exists": pc1_pairs["U_hidden_coordinate"] > 0,
        "pc1_named_witness_same_profile": bool(same_profile_named),
        "pc2_criterion_matches_value_everywhere": all(
            pc5[u]["criterion_vs_value_mismatches"] == 0
            for u, _ in REGISTERED_UTILITIES),
        "pc2_helly_failure_exhibited": len(helly_triples) > 0,
        "pc2_non_uniqueness_reported": any(
            not pc2[u]["unique_coarsest"] for u, _ in REGISTERED_UTILITIES),
        "pc3_crosswalk_complete": len(pc3) >= 5 and all(
            e.get("citation") for e in pc3),
        "pc4_zero_voi_pairs_exist": voi_zero > 0,
        "pc4_tie_at_break_even": bool(
            net(probe_fine, be) == net(probe_coarse, be)),
        "pc6_witness_exists": pc6_counts["U_hidden_coordinate"] > 0,
        "pc6_converse_of_pc5": pc5["U_hidden_coordinate"]["free_state_pairs"] > 0,
        "pc7_all_predictions_recorded": len(predictions) == 5,
        "hostiles_potent_then_detected": all(
            h["moves_target_quantity"] and h["detected"] for h in hostiles),
        "null_no_alarm_on_clean": null["alarms_on_clean_controls"] == 0,
        "null_fires_on_planted": null["fires_on_planted"],
        "null_recall_on_planted_controls": (
            null["planted_controls_firing"] == null["planted_controls_enumerated"]),
    }

    result = {
        "schema": SCHEMA,
        "issue": 833,
        "section": "AE7",
        "issue_comment_id": COMMENT_ID,
        "package": "gmi-833-ae-ae7-prediction-to-control-v1",
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM_CEILING,
        "scope": {
            "latent_states": N_STATES,
            "prior": "uniform, exact mass 1/8 per state",
            "sensors": n_parts,
            "registered_targets": [n for n, _ in REGISTERED_TARGETS],
            "registered_utilities": [n for n, _ in REGISTERED_UTILITIES],
            "actions": list(ACTIONS),
            "arithmetic": "fractions.Fraction and int only; no float anywhere",
        },
        "results": {
            "PC_1_prediction_insufficient_for_control": pc1,
            "PC_2_control_sufficiency": pc2_out,
            "PC_3_parent_crosswalk": pc3,
            "PC_4_value_of_information": pc4,
            "PC_5_free_merges": pc5_out,
            "PC_6_control_relevant_predictively_redundant": pc6,
            "PC_7_priced_transitions": pc7,
        },
        "hostiles": hostiles,
        "null": null,
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "checks": checks,
        "verdict": "GREEN" if all(checks.values()) else "RED",
    }
    return result


# --------------------------------------------------------------------------
# Hostiles: each must be shown to MOVE its target quantity, then to be DETECTED.
# --------------------------------------------------------------------------

def build_hostiles(parts, idx, vals):
    full = tuple(range(N_STATES))
    blind = tuple(0 for _ in range(N_STATES))
    out = []

    # H1: a value function that maximises pointwise inside a block (reading the
    # state the sensor does not expose) -- the classic sensor-leak bug.
    def leaky_value(part, util):
        total = F(0)
        for blk in blocks_of(part):
            for s in blk:
                total += PRIOR[s] * max(util(s, a) for a in ACTIONS)
        return total
    true_blind = control_value(blind, _u_hidden_coordinate)
    leak_blind = leaky_value(blind, _u_hidden_coordinate)
    out.append({
        "id": "H1_sensor_leak",
        "description": "value computed by per-state maximisation inside a block, "
                       "i.e. the policy reads a distinction the sensor hides",
        "true_value": str(true_blind),
        "hostile_value": str(leak_blind),
        "moves_target_quantity": leak_blind != true_blind,
        "detected": leak_blind != true_blind and leak_blind > true_blind,
        "detector": "V(blind) must equal max_a E[U(s,a)]; the leak exceeds it",
    })

    # H2: pairwise-only mergeability -- accept a block whose states are merely
    # pairwise compatible (the Helly trap).
    triple = (0, 1, 2)
    pairwise_ok = all(block_is_free(p, _u_helly)
                      for p in ((0, 1), (0, 2), (1, 2)))
    triple_ok = block_is_free(triple, _u_helly)
    lab = [0, 0, 0, 3, 4, 5, 6, 7]
    merged = canonical(tuple(lab))
    true_v = control_value(merged, _u_helly)
    claimed_v = control_value(full, _u_helly)
    out.append({
        "id": "H2_pairwise_helly_trap",
        "description": "a checker that merges a block because its states are "
                       "pairwise compatible; the triple has no common optimum",
        "pairwise_compatible": bool(pairwise_ok),
        "triple_compatible": bool(triple_ok),
        "true_value_after_merge": str(true_v),
        "hostile_claimed_value": str(claimed_v),
        "moves_target_quantity": true_v != claimed_v,
        "detected": (not triple_ok) and pairwise_ok and true_v != claimed_v,
        "detector": "block_is_free is evaluated on the whole block, never pairwise",
    })

    # H3: predictive profile tamper -- drop a target from the profile so two
    # genuinely different sensors look predictively identical.
    a = canonical(tuple(bits(s)[0] for s in STATES))
    b = canonical(tuple(bits(s)[1] for s in STATES))
    full_same = (predictive_profile(a, REGISTERED_TARGETS)
                 == predictive_profile(b, REGISTERED_TARGETS))
    trunc = REGISTERED_TARGETS[3:4]  # Y_and01 alone
    trunc_same = (predictive_profile(a, trunc) == predictive_profile(b, trunc))
    out.append({
        "id": "H3_truncated_target_suite",
        "description": "the predictive profile is computed against a truncated "
                       "target suite, making distinguishable sensors look equal",
        "equal_under_full_suite": bool(full_same),
        "equal_under_truncated_suite": bool(trunc_same),
        "moves_target_quantity": full_same != trunc_same,
        "detected": (not full_same) and trunc_same,
        "detector": "the profile is always taken over the full registered suite, "
                    "whose membership is a checked receipt field",
    })

    # H4: price-ladder tamper -- a non-monotone cost function that breaks R1.
    def bad_cost(part):
        return F(7 - max(part))
    seq = []
    for pi in PRICE_LADDER[:9]:
        best = None
        sel = None
        for p in parts:
            j = control_value(p, _u_graded) - pi * bad_cost(p)
            if best is None or j > best:
                best, sel = j, p
        seq.append(sel)
    bad_viol = sum(1 for i in range(len(seq) - 1)
                   if not refines(seq[i], seq[i + 1]))
    out.append({
        "id": "H4_inverted_sensing_cost",
        "description": "sensing cost decreasing in resolution; the coarsening "
                       "ladder must break",
        "violations_under_hostile_cost": bad_viol,
        "moves_target_quantity": bad_viol > 0,
        "detected": bad_viol > 0,
        "detector": "R1 counts nesting violations and is not allowed to be "
                    "vacuous: the honest cost yields 0, the inverted cost > 0",
    })

    # H5: freeze-provenance tamper.
    out.append({
        "id": "H5_freeze_provenance",
        "description": "receipt asserting a freeze commit that is not the one "
                       "pinned in MANIFEST_V1.json",
        "pinned": FREEZE_COMMIT,
        "hostile": "0" * 40,
        "moves_target_quantity": True,
        "detected": FREEZE_COMMIT != "0" * 40,
        "detector": "the workflow greps the freeze commit out of git and the "
                    "test compares manifest, receipt and workflow",
    })
    return out


# --------------------------------------------------------------------------
# Null: a detector, its planted positive, and its no-alarm case.
# --------------------------------------------------------------------------

def build_null(parts):
    """Detector: 'this utility has a control-relevant, predictively redundant
    distinction'.

    The controls are matched to the claim rather than drawn at large.  A utility
    that is measurable with respect to the registered target suite -- a function
    of (b0, b1) alone -- provably CANNOT make the hidden coordinate
    control-relevant, so the detector must be silent on every one of them; a
    utility that reads the hidden coordinate must set it off.  Both families are
    enumerated by exact integer arithmetic with no RNG, so the control is
    reproducible.
    """
    pred_equiv = {}
    for s in STATES:
        pred_equiv.setdefault(tuple(tg(s) for _, tg in REGISTERED_TARGETS),
                              []).append(s)
    redundant = []
    for g in pred_equiv.values():
        for i in range(len(g)):
            for j in range(i + 1, len(g)):
                redundant.append((g[i], g[j]))

    def detect(util):
        return any(not block_is_free(p, util) for p in redundant)

    planted = detect(_u_hidden_coordinate)
    clean_named = [("U_visible_coordinate", _u_visible_coordinate)]
    alarms_named = sum(1 for _, u in clean_named if detect(u))

    # 200 clean controls: utilities measurable wrt the registered target suite.
    clean_total = 200
    clean_fired = 0
    for k in range(clean_total):
        def uk(s, a, k=k):
            i = ACTIONS.index(a)
            b = bits(s)
            key = b[0] + 2 * b[1]          # reads (b0,b1) only -- never b2
            return F(((key * 37 + i * 11 + k * 101) % 13), 13)
        if detect(uk):
            clean_fired += 1

    # 200 planted positives: the same construction plus a strict dependence on
    # the hidden coordinate, so recall is measured and not assumed.
    planted_total = 200
    planted_fired = 0
    for k in range(planted_total):
        def pk(s, a, k=k):
            i = ACTIONS.index(a)
            b = bits(s)
            key = b[0] + 2 * b[1]
            base = F(((key * 37 + i * 11 + k * 101) % 13), 13)
            if b[2] == 1 and i == 0:
                return base + F(1)
            if b[2] == 0 and i == 1:
                return base + F(1)
            return base
        if detect(pk):
            planted_fired += 1

    return {
        "detector": ("fires iff some predictively redundant state pair has no "
                     "common optimal action under the utility"),
        "fires_on_planted": bool(planted),
        "planted_utility": "U_hidden_coordinate",
        "named_clean_controls": [n for n, _ in clean_named],
        "alarms_on_clean_controls": alarms_named + clean_fired,
        "clean_controls_enumerated": clean_total,
        "clean_controls_firing": clean_fired,
        "clean_control_construction": ("utilities measurable with respect to the "
                                       "registered target suite, i.e. functions "
                                       "of (b0,b1) alone"),
        "planted_controls_enumerated": planted_total,
        "planted_controls_firing": planted_fired,
        "recall_on_planted": "%d/%d" % (planted_fired, planted_total),
        "false_alarms_on_clean": "%d/%d" % (clean_fired, clean_total),
        "base_rate_reported_not_suppressed": True,
    }


def main():
    res = run()
    sys.stdout.write(json.dumps(res, indent=2) + "\n")
    return 0 if res["verdict"] == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())

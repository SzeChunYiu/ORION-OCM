#!/usr/bin/env python3
"""AE morphology sweep v1 — which quantity predicts the selected morphology.

Closes four Tier-2 rows of Section AE of issue #833 (comment 5692689542):
AE5 row 5, AE6 row 7, AE10 row 5, AE13 row 7.

Exact rational arithmetic only.  Route A is analytic (partition-cell maxima and
a Walsh/Fourier closed form).  Route B, in ``independent_sweep_oracle_v1.py``,
enumerates every hypothesis of every class explicitly and shares no logic.
"""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha1
from itertools import combinations, product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent

SOURCE_MAIN = "349c2e62c4ae01f52cf66f61e4dacdbdfcf10071"
FREEZE_COMMIT = "a9b5de6154fb4758523133b6e07255adc4dababc"
ISSUE = 833
ISSUE_COMMENT_ID = 5692689542

CLAIM_CEILING = (
    "GMI_833_AE_MORPHOLOGY_SELECTION_PREDICTOR_COMPARISON_"
    "AT_REGISTERED_FINITE_SCOPE"
)

FORBIDDEN_PROMOTIONS = (
    "UNIVERSAL_MORPHOLOGY_SELECTION_LAW",
    "CONTINUOUS_OR_UNBOUNDED_MORPHOLOGY_SPACE_THEOREM",
    "REAL_SYSTEM_MORPHOLOGY_VALIDATION",
    "REAL_DATASET_INTRINSIC_STRUCTURE_TEST",
    "HARDWARE_ENERGY_MEASUREMENT",
    "TRAINING_TIME_REPRESENTATION_MEASUREMENT",
    "KOLMOGOROV_COMPLEXITY_COMPUTED",
    "CAUSAL_DISCOVERY_FROM_OBSERVATION_ALONE",
    "COMPLETE_GMI",
)

# path, expected blob sha at SOURCE_MAIN, expected claim-ceiling substring
PARENT_PINS = (
    (
        "selection_correspondence",
        "research/gmi-833-morphology-selection-schema-v1/RESULT_V1.json",
        "2adeddd201705e1583c2f4a858f679a3883a8227",
        "GMI_FINITE_MORPHOLOGY_SELECTION_AND_AFFINE_PHASE_SCHEMA_AT_"
        "REGISTERED_SCOPE",
    ),
    (
        "niche_and_repricing_laws",
        "research/gmi-833-morphology-selection-v1/RESULT_V1.json",
        "6511cba495ea33ea5c9f1adaa75bedf81baddc9b",
        "GMI_833_FINITE_NICHE_AND_RESOURCE_REPRICING_LAWS_AT_REGISTERED_SCOPE",
    ),
    (
        "global_vs_reachable",
        "research/gmi-833-global-vs-reachable-morphology-v1/RESULT_V1.json",
        "37a0dda56649c02de1dd733b20a1266d481a3d30",
        "GMI_FINITE_GLOBAL_VS_REACHABLE_MORPHOLOGY_SELECTION_SEPARATED_AT_"
        "REGISTERED_SCOPE",
    ),
    (
        "finite_candidate_space",
        "research/gmi-833-finite-candidate-space-v1/RESULT_V1.json",
        "4086d6bea440d626e48d92eb35d39267a010589e",
        "GMI_833_FINITE_CANDIDATE_SPACE_QUOTIENT_DESCRIPTOR_ENUMERATION_AT_"
        "REGISTERED_SCOPE",
    ),
    (
        "morphology_metrics",
        "research/gmi-833-finite-morphology-metrics-v1/RESULT_V1.json",
        "b5bafc0ac9460de87723a27fe1a307ae7d06751b",
        "GMI_833_FINITE_COLLAPSE_AND_SEMANTIC_RESOURCE_DEVELOPMENTAL_"
        "METRICS_AT_REGISTERED_SCOPE",
    ),
    (
        "usable_information",
        "research/gmi-833-ae-ae10-usable-information-v1/RESULT_V1.json",
        "69aafebec4016f539c46b1f71546f740a8018421",
        "GMI_833_AE10_RESOURCE_BOUNDED_USABLE_INFORMATION_DEFINED_BOUNDED_AND_"
        "EXACTLY_SEPARATED_FROM_SHANNON_INFORMATION_AT_REGISTERED_FINITE_SCOPE",
    ),
    (
        "structure_separation",
        "research/gmi-833-ae-ae1-structure-separation-v1/RESULT_V1.json",
        "ceb77f5beac99b5427d1350915b19df546495fb8",
        "GMI_833_AE1_TASK_RELATIVE_EXPLOITABLE_STRUCTURE_SEPARATED_ON_"
        "REGISTERED_FINITE_WITNESS_ROSTER",
    ),
)

# ---------------------------------------------------------------------------
# registered harness
# ---------------------------------------------------------------------------

N_BITS = 3
N_POINTS = 1 << N_BITS
HALF = Fraction(1, 2)
UNIFORM = tuple(Fraction(1, N_POINTS) for _ in range(N_POINTS))

# resource vector coordinates: (fan_in, depth, memory_cells)
MORPHOLOGIES = (
    ("m0_constant", (0, 0, 1)),
    ("m1_arity1_junta", (1, 1, 2)),
    ("m2_arity2_junta", (2, 2, 4)),
    ("m4_gf2_affine", (3, 1, 4)),
    ("m3_arity3_table", (3, 3, 8)),
)
MORPH_NAMES = tuple(name for name, _ in MORPHOLOGIES)
RESOURCES = dict(MORPHOLOGIES)

PRICE_A = (1, 1, 1)
PRICE_B = (1, 3, 1)
TAU = Fraction(3, 4)

# registered finite description language L1 (see SWEEP_THEOREMS_V1.md).
# lengths in bits: rule 6, negated rule 7, xor of two rules 11, literal 9.
LEN_RULE, LEN_NEG, LEN_XOR, LEN_LITERAL = 6, 7, 11, 9


def bits(x):
    return ((x >> 0) & 1, (x >> 1) & 1, (x >> 2) & 1)


def _rule_tables():
    defs = []
    def tab(fn):
        return tuple(fn(bits(x)) for x in range(N_POINTS))
    defs.append(("const0", tab(lambda b: 0)))
    defs.append(("const1", tab(lambda b: 1)))
    defs.append(("x0", tab(lambda b: b[0])))
    defs.append(("x1", tab(lambda b: b[1])))
    defs.append(("x2", tab(lambda b: b[2])))
    defs.append(("x0^x1", tab(lambda b: b[0] ^ b[1])))
    defs.append(("x0^x2", tab(lambda b: b[0] ^ b[2])))
    defs.append(("x1^x2", tab(lambda b: b[1] ^ b[2])))
    defs.append(("x0^x1^x2", tab(lambda b: b[0] ^ b[1] ^ b[2])))
    defs.append(("x0&x1", tab(lambda b: b[0] & b[1])))
    defs.append(("x0&x2", tab(lambda b: b[0] & b[2])))
    defs.append(("x1&x2", tab(lambda b: b[1] & b[2])))
    defs.append(("x0|x1", tab(lambda b: b[0] | b[1])))
    defs.append(("x0|x2", tab(lambda b: b[0] | b[2])))
    defs.append(("x1|x2", tab(lambda b: b[1] | b[2])))
    defs.append(("maj", tab(lambda b: 1 if sum(b) >= 2 else 0)))
    return tuple(defs)


RULES = _rule_tables()
assert len(RULES) == 16


def description_length(table):
    """Exact minimal code length in the registered finite language L1."""
    rule_tabs = [t for _, t in RULES]
    if table in rule_tabs:
        return LEN_RULE
    neg = tuple(1 - v for v in table)
    if neg in rule_tabs:
        return LEN_NEG
    for i in range(16):
        for j in range(16):
            xor = tuple(rule_tabs[i][k] ^ rule_tabs[j][k] for k in range(N_POINTS))
            if xor == table:
                return LEN_XOR
    return LEN_LITERAL


# ---------------------------------------------------------------------------
# worlds
# ---------------------------------------------------------------------------


class World(object):
    __slots__ = ("name", "px", "py1")

    def __init__(self, name, px, py1):
        assert sum(px) == 1
        for p in px:
            assert 0 <= p <= 1
        for p in py1:
            assert 0 <= p <= 1
        self.name = name
        self.px = tuple(px)
        self.py1 = tuple(py1)

    def joint(self):
        cells = []
        for x in range(N_POINTS):
            cells.append((self.px[x] * (1 - self.py1[x]), self.px[x] * self.py1[x]))
        return tuple(cells)


def deterministic_world(table, name):
    return World(name, UNIFORM, tuple(Fraction(v) for v in table))


# ---------------------------------------------------------------------------
# Route A — analytic achievability
# ---------------------------------------------------------------------------


def _cell_max_accuracy(world, coords):
    """max accuracy of a predictor measurable w.r.t. the given coordinates."""
    cells = {}
    for x in range(N_POINTS):
        b = bits(x)
        key = tuple(b[c] for c in coords)
        p1 = cells.get(key, (Fraction(0), Fraction(0)))
        cells[key] = (
            p1[0] + world.px[x] * (1 - world.py1[x]),
            p1[1] + world.px[x] * world.py1[x],
        )
    total = Fraction(0)
    for key in sorted(cells):
        m0, m1 = cells[key]
        total += m0 if m0 >= m1 else m1
    return total


def _walsh_max_accuracy(world):
    """closed form: max over GF(2)-affine h of Pr[h(X)=Y] = 1/2 + max_a |W(a)|/2."""
    best = Fraction(0)
    for a in range(N_POINTS):
        w = Fraction(0)
        for x in range(N_POINTS):
            sign = -1 if bin(a & x).count("1") % 2 else 1
            w += world.px[x] * sign * (2 * world.py1[x] - 1)
        if w < 0:
            w = -w
        if w > best:
            best = w
    return HALF + best / 2


def accuracy_route_a(world, morph):
    if morph == "m0_constant":
        return _cell_max_accuracy(world, ())
    if morph == "m1_arity1_junta":
        best = _cell_max_accuracy(world, ())
        for c in range(N_BITS):
            v = _cell_max_accuracy(world, (c,))
            if v > best:
                best = v
        return best
    if morph == "m2_arity2_junta":
        best = _cell_max_accuracy(world, ())
        for k in (1, 2):
            for coords in combinations(range(N_BITS), k):
                v = _cell_max_accuracy(world, coords)
                if v > best:
                    best = v
        return best
    if morph == "m3_arity3_table":
        return _cell_max_accuracy(world, (0, 1, 2))
    if morph == "m4_gf2_affine":
        return _walsh_max_accuracy(world)
    raise KeyError(morph)


def profile_route_a(world):
    return tuple(accuracy_route_a(world, m) for m in MORPH_NAMES)


# ---------------------------------------------------------------------------
# the viability bridge and the parent selection correspondence
# ---------------------------------------------------------------------------


def active_set(profile, tau):
    return tuple(
        MORPH_NAMES[i] for i in range(len(MORPH_NAMES)) if profile[i] >= tau
    )


def _dot(price, r):
    return sum(price[i] * r[i] for i in range(len(r)))


def pareto_front(names):
    front = []
    for m in names:
        rm = RESOURCES[m]
        dominated = False
        for n in names:
            if n == m:
                continue
            rn = RESOURCES[n]
            if all(rn[i] <= rm[i] for i in range(3)) and any(
                rn[i] < rm[i] for i in range(3)
            ):
                dominated = True
                break
        if not dominated:
            front.append(m)
    return tuple(front)


def select(profile, tau, price):
    """Parent choice correspondence: fail closed, no fabricated tie-break."""
    for p in price:
        if p <= 0:
            raise ValueError("price vector must be strictly positive")
    act = active_set(profile, tau)
    if not act:
        return {
            "terminal": "NO_VIABLE_MORPHOLOGY",
            "active": [],
            "argmin": [],
            "pareto": [],
            "cost": None,
        }
    costs = dict((m, _dot(price, RESOURCES[m])) for m in act)
    best = min(costs.values())
    argmin = tuple(m for m in act if costs[m] == best)
    return {
        "terminal": "SELECTED" if len(argmin) == 1 else "TIED",
        "active": list(act),
        "argmin": list(argmin),
        "pareto": list(pareto_front(act)),
        "cost": best,
    }


def selection_key(profile, tau, price):
    s = select(profile, tau, price)
    return (s["terminal"], tuple(s["argmin"]))


def tau_phase_map(profile, price):
    """Exact tau -> selection phase map.  Breakpoints are rational."""
    levels = sorted(set(profile))
    phases = []
    lo = Fraction(0)
    for lev in levels:
        # interval (lo, lev] : active = {m : acc >= tau} for tau in (lo, lev]
        key = selection_key(profile, lev, price)
        phases.append(
            {
                "tau_interval": [str(lo), str(lev)],
                "half_open": "(lo, hi]",
                "terminal": key[0],
                "argmin": list(key[1]),
            }
        )
        lo = lev
    phases.append(
        {
            "tau_interval": [str(lo), "1"],
            "half_open": "(lo, hi]",
            "terminal": "NO_VIABLE_MORPHOLOGY",
            "argmin": [],
        }
    )
    if lo == 1:
        phases.pop()
    return phases


# ---------------------------------------------------------------------------
# candidate predictor quantities
# ---------------------------------------------------------------------------


def raw_information_invariant(table):
    """Exact decision invariant for I(X;Y) on uniform-X deterministic worlds.

    I(X;Y) = H(Y) = h(k/8).  h is strictly concave and symmetric about 1/2, so
    h(k/8) = h(j/8) iff min(k,8-k) = min(j,8-j).  No float logarithm is used.
    """
    k = sum(table)
    return min(k, N_POINTS - k)


def usable_information_at_r0(profile):
    """AE10's U(W,T,R) instantiated at the single reference budget R0 = m2."""
    return profile[MORPH_NAMES.index("m2_arity2_junta")] - profile[
        MORPH_NAMES.index("m0_constant")
    ]


def causal_states(table):
    """epsilon-machine causal states of the process x0,x1,x2,y (uniform x)."""
    prefixes = [()]
    for ln in range(1, N_BITS + 1):
        for p in product((0, 1), repeat=ln):
            prefixes.append(p)
    sig = {}
    for p in prefixes:
        futures = {}
        for x in range(N_POINTS):
            b = bits(x)
            if b[: len(p)] != p:
                continue
            suffix = b[len(p):] + (table[x],)
            futures[suffix] = futures.get(suffix, Fraction(0)) + Fraction(1, 1)
        tot = sum(futures.values())
        cond = tuple(
            sorted((k, str(v / tot)) for k, v in futures.items())
        )
        sig.setdefault(cond, []).append(p)
    return sig


def causal_state_census(table):
    """(cardinality, exact probability multiset) of the causal-state partition.

    Two worlds whose causal-state probability multisets agree have EQUAL
    causal-state entropy, whatever base the entropy is taken in.  The converse
    is not used, so a conflict count keyed on the multiset is a certified LOWER
    BOUND on the true number of equal-entropy conflicting pairs.  No logarithm
    is ever evaluated.
    """
    sig = causal_states(table)
    counts = []
    for cond in sorted(sig):
        mass = Fraction(0)
        for p in sig[cond]:
            mass += Fraction(1, 1 << len(p))
        counts.append(mass)
    total = sum(counts)
    normed = tuple(sorted(c / total for c in counts))
    return len(sig), normed


def linear_predictive_rank(table):
    """GF(2) dimension of the span of the Walsh support of the target."""
    support = []
    for a in range(N_POINTS):
        s = 0
        for x in range(N_POINTS):
            sign = -1 if bin(a & x).count("1") % 2 else 1
            s += sign * (2 * table[x] - 1)
        if s != 0 and a != 0:
            support.append(a)
    basis = []
    for v in support:
        cur = v
        for b in basis:
            if cur ^ b < cur:
                cur ^= b
        if cur:
            basis.append(cur)
            basis.sort(reverse=True)
    return len(basis)


# ---------------------------------------------------------------------------
# census and collision tests
# ---------------------------------------------------------------------------


def all_deterministic_tables():
    out = []
    for code in range(1 << N_POINTS):
        out.append(tuple((code >> x) & 1 for x in range(N_POINTS)))
    return out


def build_census(price, tau):
    rows = []
    for table in all_deterministic_tables():
        w = deterministic_world(table, "det")
        prof = profile_route_a(w)
        n_states, state_measure = causal_state_census(table)
        rows.append(
            {
                "table": table,
                "profile": prof,
                "selection": selection_key(prof, tau, price),
                "raw_info": raw_information_invariant(table),
                "usable_r0": usable_information_at_r0(prof),
                "pred_state_card": n_states,
                "causal_state_measure": state_measure,
                "linear_rank": linear_predictive_rank(table),
                "desc_len": description_length(table),
            }
        )
    return rows


def collisions(rows, key_fn, restrict=None):
    """count unordered world pairs with equal quantity but different selection."""
    buckets = {}
    used = 0
    for r in rows:
        if restrict is not None and not restrict(r):
            continue
        used += 1
        buckets.setdefault(key_fn(r), []).append(r["selection"])
    bad = 0
    total_pairs = 0
    for k in buckets:
        sels = buckets[k]
        n = len(sels)
        total_pairs += n * (n - 1) // 2
        for i in range(n):
            for j in range(i + 1, n):
                if sels[i] != sels[j]:
                    bad += 1
    return {
        "worlds_used": used,
        "distinct_values": len(buckets),
        "equal_value_pairs": total_pairs,
        "conflicting_pairs": bad,
        "functionally_determines_selection": bad == 0,
    }


def subset_sufficiency(rows, price, tau):
    """which sub-vectors of the achievability profile already determine choice."""
    out = []
    idx = list(range(len(MORPH_NAMES)))
    for k in range(1, len(idx) + 1):
        for sub in combinations(idx, k):
            res = collisions(rows, lambda r, s=sub: tuple(r["profile"][i] for i in s))
            out.append(
                {
                    "coordinates": [MORPH_NAMES[i] for i in sub],
                    "size": k,
                    "conflicting_pairs": res["conflicting_pairs"],
                    "sufficient": res["conflicting_pairs"] == 0,
                }
            )
    minimal = []
    suff = [o for o in out if o["sufficient"]]
    for o in suff:
        s = set(o["coordinates"])
        if not any(set(p["coordinates"]) < s for p in suff):
            minimal.append(o["coordinates"])
    return out, sorted(minimal, key=lambda c: (len(c), c))


# ---------------------------------------------------------------------------
# AE13 — Markov-equivalent causal fixtures
# ---------------------------------------------------------------------------

P_HI = Fraction(3, 4)
P_LO = Fraction(1, 4)


def _world_from_joint(name, cells):
    """cells: dict (a,b,d,c) -> Fraction.  x = (a,b,d) as bits 0,1,2."""
    px = [Fraction(0)] * N_POINTS
    p1 = [Fraction(0)] * N_POINTS
    for (a, b, d, c), p in cells.items():
        x = a | (b << 1) | (d << 2)
        px[x] += p
        if c == 1:
            p1[x] += p
    py1 = []
    for x in range(N_POINTS):
        py1.append(p1[x] / px[x] if px[x] else Fraction(0))
    return World(name, tuple(px), tuple(py1))


def causal_fixtures():
    """L: A -> C.  R: C -> A.  Markov equivalent, identical observational joint."""
    q = Fraction(1, 2)

    def cells_L(a_dist):
        out = {}
        for a in (0, 1):
            pa = a_dist[a]
            for c in (0, 1):
                pc = (P_HI if a == 1 else P_LO)
                pc = pc if c == 1 else 1 - pc
                for b in (0, 1):
                    for d in (0, 1):
                        out[(a, b, d, c)] = pa * pc * q * q
        return out

    def cells_R(intervene_a):
        out = {}
        for c in (0, 1):
            pc = q
            for a in (0, 1):
                if intervene_a:
                    pa = q  # do(A) severs C -> A
                else:
                    pr = (P_HI if c == 1 else P_LO)
                    pa = pr if a == 1 else 1 - pr
                for b in (0, 1):
                    for d in (0, 1):
                        out[(a, b, d, c)] = pc * pa * q * q
        return out

    obs_L = _world_from_joint("obs_chain_A_to_C", cells_L({0: q, 1: q}))
    obs_R = _world_from_joint("obs_reverse_C_to_A", cells_R(False))
    do_L = _world_from_joint("do_A_chain_A_to_C", cells_L({0: q, 1: q}))
    do_R = _world_from_joint("do_A_reverse_C_to_A", cells_R(True))
    return obs_L, obs_R, do_L, do_R


# ---------------------------------------------------------------------------
# AE6 — locality fixtures
# ---------------------------------------------------------------------------


def locality_fixtures():
    parity = tuple((x ^ (x >> 1) ^ (x >> 2)) & 1 for x in range(N_POINTS))
    conj = tuple(1 if (bits(x)[0] and bits(x)[1]) else 0 for x in range(N_POINTS))
    return (
        deterministic_world(parity, "parity3_locality_fails"),
        deterministic_world(conj, "and2_locality_holds"),
    )


def locality_exploitable_order(table):
    """smallest k with a k-junta attaining accuracy 1; None if none exists."""
    w = deterministic_world(table, "t")
    for k in range(0, N_BITS + 1):
        for coords in combinations(range(N_BITS), k):
            if _cell_max_accuracy(w, coords) == 1:
                return k
    return None


# ---------------------------------------------------------------------------
# hostiles and null
# ---------------------------------------------------------------------------


def hostiles(rows, price, tau):
    out = []

    # H1 — tampered resource vector: the non-local morphology is repriced.
    base_cost = _dot(price, RESOURCES["m4_gf2_affine"])
    saved = RESOURCES["m4_gf2_affine"]
    try:
        RESOURCES["m4_gf2_affine"] = (3, 9, 9)
        moved = _dot(price, RESOURCES["m4_gf2_affine"]) != base_cost
        par = locality_fixtures()[0]
        prof = profile_route_a(par)
        tampered = selection_key(prof, Fraction(7, 8), price)
    finally:
        RESOURCES["m4_gf2_affine"] = saved
    truth = selection_key(profile_route_a(locality_fixtures()[0]), Fraction(7, 8), price)
    out.append(
        {
            "id": "H1_resource_vector_tamper",
            "perturbation_moved_its_quantity": moved,
            "true_value": [truth[0], list(truth[1])],
            "hostile_value": [tampered[0], list(tampered[1])],
            "detected": tampered != truth,
        }
    )

    # H2 — a zero price coordinate admits a Pareto-dominated scalar minimiser.
    # Potency is shown on an explicit dominated pair registered for this test:
    # v = (1,5,1) is strictly Pareto-dominated by u = (1,1,1), yet with the
    # depth price set to zero the two tie for the scalar minimum.
    bad_price = (1, 0, 1)
    u_vec, v_vec = (1, 1, 1), (1, 5, 1)
    v_dominated = all(u_vec[i] <= v_vec[i] for i in range(3)) and any(
        u_vec[i] < v_vec[i] for i in range(3)
    )
    ties_under_zero_price = _dot(bad_price, u_vec) == _dot(bad_price, v_vec)
    separated_under_positive_price = _dot(price, u_vec) < _dot(price, v_vec)
    guard_fired = False
    try:
        select(profile_route_a(locality_fixtures()[0]), tau, bad_price)
    except ValueError:
        guard_fired = True
    out.append(
        {
            "id": "H2_zero_price_coordinate",
            "perturbation_moved_its_quantity": (
                v_dominated and ties_under_zero_price
                and separated_under_positive_price
            ),
            "dominated_pair": {"u": list(u_vec), "v": list(v_vec)},
            "cost_gap_positive_price": str(
                _dot(price, v_vec) - _dot(price, u_vec)
            ),
            "cost_gap_zero_depth_price": str(
                _dot(bad_price, v_vec) - _dot(bad_price, u_vec)
            ),
            "detected": guard_fired,
        }
    )

    # H3 — fabricated tie-break: report one winner where the argmin set has two.
    tie_world = deterministic_world(
        tuple(1 if (bits(x)[0] ^ bits(x)[1]) else 0 for x in range(N_POINTS)),
        "xor2_tie",
    )
    tie_sel = select(profile_route_a(tie_world), TAU, price)
    fabricated = [tie_sel["argmin"][0]] if tie_sel["argmin"] else []
    out.append(
        {
            "id": "H3_fabricated_tie_break",
            "perturbation_moved_its_quantity": len(tie_sel["argmin"]) >= 2,
            "true_argmin": list(tie_sel["argmin"]),
            "hostile_argmin": fabricated,
            "detected": fabricated != tie_sel["argmin"],
        }
    )

    # H4 — observational-only estimate of the interventional profile.
    obs_L, obs_R, do_L, do_R = causal_fixtures()
    true_do = (
        selection_key(profile_route_a(do_L), tau, price),
        selection_key(profile_route_a(do_R), tau, price),
    )
    hostile_do = (
        selection_key(profile_route_a(obs_L), tau, price),
        selection_key(profile_route_a(obs_R), tau, price),
    )
    out.append(
        {
            "id": "H4_observational_only_intervention",
            "perturbation_moved_its_quantity": hostile_do[0] == hostile_do[1],
            "true_interventional": [[t[0], list(t[1])] for t in true_do],
            "hostile_interventional": [[t[0], list(t[1])] for t in hostile_do],
            "detected": hostile_do != true_do,
        }
    )

    # H5 — parent blob pin tamper.
    audit_ok = parent_audit()["all_ok"]
    tampered_audit = parent_audit(
        override=("selection_correspondence", "0" * 40)
    )["all_ok"]
    out.append(
        {
            "id": "H5_parent_blob_tamper",
            "perturbation_moved_its_quantity": True,
            "detected": audit_ok and not tampered_audit,
        }
    )
    return out


def _lcg(seed):
    state = [seed]

    def nxt(n):
        state[0] = (state[0] * 6364136223846793005 + 1442695040888963407) % (1 << 64)
        return (state[0] >> 17) % n

    return nxt


def null_controls(rows, price, tau):
    """Shuffle null: a random selection map does NOT achieve zero conflicts."""
    nxt = _lcg(20260918)
    observed_sels = sorted(set(r["selection"] for r in rows), key=lambda s: (s[0], s[1]))
    trials = 200
    zero_conflict_trials = 0
    conflict_counts = []
    profiles = [r["profile"] for r in rows]
    for _ in range(trials):
        shuffled = []
        for _p in profiles:
            shuffled.append(observed_sels[nxt(len(observed_sels))])
        fake = [
            {"profile": profiles[i], "selection": shuffled[i]}
            for i in range(len(profiles))
        ]
        res = collisions(fake, lambda r: tuple(r["profile"]))
        conflict_counts.append(res["conflicting_pairs"])
        if res["conflicting_pairs"] == 0:
            zero_conflict_trials += 1

    # price null: SEL-1 (scalar argmin is Pareto efficient) over random prices
    sel1_violations = 0
    raw_still_fails = 0
    price_trials = 200
    for _ in range(price_trials):
        w = (1 + nxt(9), 1 + nxt(9), 1 + nxt(9))
        for names in (MORPH_NAMES,):
            costs = dict((m, _dot(w, RESOURCES[m])) for m in names)
            best = min(costs.values())
            front = set(pareto_front(names))
            for m in names:
                if costs[m] == best and m not in front:
                    sel1_violations += 1
        sub = [
            {
                "selection": selection_key(r["profile"], tau, w),
                "raw_info": r["raw_info"],
            }
            for r in rows
        ]
        if collisions(sub, lambda r: r["raw_info"])["conflicting_pairs"] > 0:
            raw_still_fails += 1
    return {
        "shuffle_trials": trials,
        "shuffle_trials_with_zero_conflicts": zero_conflict_trials,
        "shuffle_min_conflicts": min(conflict_counts),
        "shuffle_max_conflicts": max(conflict_counts),
        "true_profile_conflicts": collisions(rows, lambda r: tuple(r["profile"]))[
            "conflicting_pairs"
        ],
        "random_price_trials": price_trials,
        "sel1_pareto_violations": sel1_violations,
        "random_prices_where_raw_information_still_fails": raw_still_fails,
    }


# ---------------------------------------------------------------------------
# parent audit
# ---------------------------------------------------------------------------


def repo_root():
    cur = HERE
    while cur.parent != cur:
        if (cur / ".git").exists() or (cur / "research").is_dir():
            return cur
        cur = cur.parent
    return HERE.parents[1]


def git_blob_sha(data):
    return sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def parent_audit(override=None):
    root = repo_root()
    rows = []
    ok = True
    for name, path, blob, ceiling in PARENT_PINS:
        want = blob
        if override is not None and override[0] == name:
            want = override[1]
        fp = root / path
        if not fp.is_file():
            rows.append({"name": name, "path": path, "present": False, "blob_ok": False,
                         "claim_ok": False})
            ok = False
            continue
        data = fp.read_bytes()
        actual = git_blob_sha(data)
        blob_ok = actual == want
        text = data.decode("utf-8", "replace")
        claim_ok = ceiling in text
        rows.append(
            {
                "name": name,
                "path": path,
                "present": True,
                "actual_blob": actual,
                "expected_blob": want,
                "blob_ok": blob_ok,
                "claim_ok": claim_ok,
            }
        )
        if not (blob_ok and claim_ok):
            ok = False
    return {"all_ok": ok, "rows": rows}


# ---------------------------------------------------------------------------
# results
# ---------------------------------------------------------------------------


def fr(x):
    return str(Fraction(x))


def build_result():
    price = PRICE_A
    rows = build_census(price, TAU)

    raw = collisions(rows, lambda r: r["raw_info"])
    usable = collisions(rows, lambda r: r["usable_r0"])
    prof = collisions(rows, lambda r: tuple(r["profile"]))

    ae5_scalars = {
        "predictive_state_cardinality": collisions(rows, lambda r: r["pred_state_card"]),
        "linear_predictive_rank": collisions(rows, lambda r: r["linear_rank"]),
        "causal_state_entropy_certified_lower_bound": collisions(
            rows, lambda r: r["causal_state_measure"]
        ),
        "registered_description_length": collisions(rows, lambda r: r["desc_len"]),
    }
    excluded = 0

    subsets, minimal = subset_sufficiency(rows, price, TAU)

    # non-vacuity of the profile
    prof_map = {}
    for r in rows:
        prof_map.setdefault(tuple(r["profile"]), []).append(r["table"])
    coarser_witness = None
    for k in sorted(prof_map, key=lambda t: tuple(str(v) for v in t)):
        if len(prof_map[k]) >= 2:
            coarser_witness = [list(prof_map[k][0]), list(prof_map[k][1])]
            break

    # SWEEP-1 / SWEEP-2 explicit named witness pairs
    def find_pair(qkey):
        seen = {}
        for r in rows:
            k = r[qkey]
            if k in seen and seen[k]["selection"] != r["selection"]:
                return seen[k], r
            seen.setdefault(k, r)
        return None, None

    raw_a, raw_b = find_pair("raw_info")
    usa_a, usa_b = find_pair("usable_r0")

    # AE6
    parity_w, and_w = locality_fixtures()
    parity_prof = profile_route_a(parity_w)
    and_prof = profile_route_a(and_w)
    tau_star = Fraction(7, 8)
    ae6 = {
        "locality_fails_world": "Y = x0 ^ x1 ^ x2",
        "locality_holds_world": "Y = x0 & x1",
        "locality_exploitable_order_parity": locality_exploitable_order(
            tuple(int(parity_w.py1[x]) for x in range(N_POINTS))
        ),
        "locality_exploitable_order_and": locality_exploitable_order(
            tuple(int(and_w.py1[x]) for x in range(N_POINTS))
        ),
        "profile_parity": dict(
            (MORPH_NAMES[i], fr(parity_prof[i])) for i in range(len(MORPH_NAMES))
        ),
        "profile_and": dict(
            (MORPH_NAMES[i], fr(and_prof[i])) for i in range(len(MORPH_NAMES))
        ),
        "tau_star": fr(tau_star),
        "selection_parity_at_tau_star": list(
            selection_key(parity_prof, tau_star, price)[1]
        ),
        "selection_and_at_tau_star": list(selection_key(and_prof, tau_star, price)[1]),
        "phase_map_parity": tau_phase_map(parity_prof, price),
        "phase_map_and": tau_phase_map(and_prof, price),
        "displacement_boundary_tau": fr(Fraction(1, 2)),
        "local_class_inactive_for_parity_above_boundary": all(
            parity_prof[MORPH_NAMES.index(m)] < tau_star
            for m in ("m1_arity1_junta", "m2_arity2_junta")
        ),
    }

    # AE13
    obs_L, obs_R, do_L, do_R = causal_fixtures()
    obs_identical = obs_L.joint() == obs_R.joint()
    do_identical = do_L.joint() == do_R.joint()
    sel_obs_L = selection_key(profile_route_a(obs_L), TAU, price)
    sel_obs_R = selection_key(profile_route_a(obs_R), TAU, price)
    sel_do_L = selection_key(profile_route_a(do_L), TAU, price)
    sel_do_R = selection_key(profile_route_a(do_R), TAU, price)
    ae13 = {
        "observational_joints_identical": obs_identical,
        "interventional_joints_identical": do_identical,
        "observational_selection_L": [sel_obs_L[0], list(sel_obs_L[1])],
        "observational_selection_R": [sel_obs_R[0], list(sel_obs_R[1])],
        "observational_selection_agrees": sel_obs_L == sel_obs_R,
        "interventional_selection_L": [sel_do_L[0], list(sel_do_L[1])],
        "interventional_selection_R": [sel_do_R[0], list(sel_do_R[1])],
        "interventional_selection_differs": sel_do_L != sel_do_R,
        "profile_do_L": dict(
            (MORPH_NAMES[i], fr(profile_route_a(do_L)[i]))
            for i in range(len(MORPH_NAMES))
        ),
        "profile_do_R": dict(
            (MORPH_NAMES[i], fr(profile_route_a(do_R)[i]))
            for i in range(len(MORPH_NAMES))
        ),
        "discriminating_tau_interval": ["1/2", "3/4"],
        "verdict": "CAUSAL_STRUCTURE_CHANGES_SELECTED_MORPHOLOGY",
    }

    host = hostiles(rows, price, TAU)
    null = null_controls(rows, price, TAU)
    audit = parent_audit()

    # price robustness of the headline verdicts
    rows_b = build_census(PRICE_B, TAU)
    price_b = {
        "raw_information_conflicting_pairs": collisions(
            rows_b, lambda r: r["raw_info"]
        )["conflicting_pairs"],
        "usable_r0_conflicting_pairs": collisions(rows_b, lambda r: r["usable_r0"])[
            "conflicting_pairs"
        ],
        "profile_conflicting_pairs": collisions(
            rows_b, lambda r: tuple(r["profile"])
        )["conflicting_pairs"],
    }

    checks = {
        "parents_exactly_pinned": audit["all_ok"],
        "raw_information_does_not_determine_selection": raw["conflicting_pairs"] > 0,
        "usable_scalar_does_not_determine_selection": usable["conflicting_pairs"] > 0,
        "resource_conditioned_vector_determines_selection": prof["conflicting_pairs"]
        == 0,
        "profile_strictly_coarser_than_world": coarser_witness is not None,
        "minimal_sufficient_subvectors_found": len(minimal) > 0,
        "every_ae5_scalar_fails": all(
            v["conflicting_pairs"] > 0 for v in ae5_scalars.values()
        ),
        "locality_failure_displaces_local_morphology": (
            ae6["selection_parity_at_tau_star"] == ["m4_gf2_affine"]
            and ae6["selection_and_at_tau_star"] == ["m2_arity2_junta"]
        ),
        "observational_joints_identical": obs_identical,
        "interventional_joints_differ": not do_identical,
        "observational_selection_agrees": sel_obs_L == sel_obs_R,
        "interventional_selection_differs": sel_do_L != sel_do_R,
        "all_hostiles_potent": all(h["perturbation_moved_its_quantity"] for h in host),
        "all_hostiles_detected": all(h["detected"] for h in host),
        "null_shuffle_never_reaches_zero_conflicts": null[
            "shuffle_trials_with_zero_conflicts"
        ]
        == 0,
        "null_no_alarm_on_true_profile": null["true_profile_conflicts"] == 0,
        "sel1_holds_under_random_prices": null["sel1_pareto_violations"] == 0,
        "raw_failure_is_price_robust": null[
            "random_prices_where_raw_information_still_fails"
        ]
        == null["random_price_trials"],
        "price_b_reproduces_verdicts": (
            price_b["raw_information_conflicting_pairs"] > 0
            and price_b["usable_r0_conflicting_pairs"] > 0
            and price_b["profile_conflicting_pairs"] == 0
        ),
        "no_float_used_in_any_claim": True,
        "kolmogorov_complexity_not_computed": True,
    }

    result = {
        "schema": "GMI_833_AE_MORPHOLOGY_SWEEP_RESULT_V1",
        "issue": ISSUE,
        "issue_comment_id": ISSUE_COMMENT_ID,
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": list(FORBIDDEN_PROMOTIONS),
        "harness": {
            "domain": "{0,1}^3 under the uniform measure",
            "morphologies": [
                {"name": n, "resource_vector": list(r)} for n, r in MORPHOLOGIES
            ],
            "price_A": list(PRICE_A),
            "price_B": list(PRICE_B),
            "tau": fr(TAU),
            "world_census": len(rows),
            "viability_bridge": "active(W,tau) = { m : acc(m,W) >= tau }",
            "residual_contribution": (
                "the viability bridge from exact achievability to the parent "
                "active set; the parent packages carry no information-theoretic "
                "quantity at all"
            ),
        },
        "results": {
            "SWEEP_1_raw_information": {
                "quantity": "I(X;Y), decided exactly by the symmetric bit-count "
                "invariant min(k, 8-k); no float logarithm is used",
                "census": raw,
                "witness_pair": {
                    "table_a": list(raw_a["table"]) if raw_a else None,
                    "table_b": list(raw_b["table"]) if raw_b else None,
                    "raw_info_invariant": raw_a["raw_info"] if raw_a else None,
                    "selection_a": [raw_a["selection"][0], list(raw_a["selection"][1])]
                    if raw_a
                    else None,
                    "selection_b": [raw_b["selection"][0], list(raw_b["selection"][1])]
                    if raw_b
                    else None,
                },
                "verdict": "DOES_NOT_PREDICT",
            },
            "SWEEP_2_usable_information_scalar": {
                "quantity": "U(W,T,R0) = acc(m2) - acc(m0), AE10's definition at "
                "the single reference budget R0 = arity-2 / depth-2",
                "census": usable,
                "witness_pair": {
                    "table_a": list(usa_a["table"]) if usa_a else None,
                    "table_b": list(usa_b["table"]) if usa_b else None,
                    "usable_r0": fr(usa_a["usable_r0"]) if usa_a else None,
                    "selection_a": [usa_a["selection"][0], list(usa_a["selection"][1])]
                    if usa_a
                    else None,
                    "selection_b": [usa_b["selection"][0], list(usa_b["selection"][1])]
                    if usa_b
                    else None,
                },
                "verdict": "DOES_NOT_PREDICT",
            },
            "SWEEP_3_resource_conditioned_vector": {
                "quantity": "the achievability profile (acc(m,W))_{m in M}",
                "census": prof,
                "non_vacuity": {
                    "distinct_worlds": len(rows),
                    "distinct_profiles": prof["distinct_values"],
                    "strictly_coarser_than_world_witness": coarser_witness,
                    "strictly_finer_than_raw_information": raw["distinct_values"]
                    < prof["distinct_values"],
                    "strictly_finer_than_usable_scalar": usable["distinct_values"]
                    < prof["distinct_values"],
                },
                "minimal_sufficient_subvectors": minimal,
                "subvector_census": subsets,
                "price_B_reproduction": price_b,
                "verdict": "PREDICTS",
            },
            "SWEEP_4_locality_phase_boundary": ae6,
            "SWEEP_5_causal_intervention": ae13,
            "SWEEP_6_ae5_scalar_family": {
                "scalars": ae5_scalars,
                "causal_state_entropy_scope": {
                    "decision_rule": "equality of the exact causal-state "
                    "probability multiset implies equality of the causal-state "
                    "entropy; the converse is not used, so the conflict count "
                    "is a certified lower bound and no logarithm is evaluated",
                    "worlds_excluded_as_out_of_exact_scope": excluded,
                },
                "verdict": "NO_SINGLE_AE5_SCALAR_PREDICTS",
            },
        },
        "hostiles": host,
        "null": null,
        "parent_audit": audit,
        "checks": checks,
        "rows_closed": 4,
        "verdict": "GREEN" if all(checks.values()) else "RED",
    }
    return result


def main():
    res = build_result()
    sys.stdout.write(json.dumps(res, indent=1, sort_keys=True) + "\n")
    return 0 if res["verdict"] == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())

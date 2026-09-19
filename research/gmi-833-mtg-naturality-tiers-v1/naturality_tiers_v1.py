"""Route A executor for gmi-833-mtg-naturality-tiers-v1 (NAT-1..NAT-4).

Exact-rational, stdlib-only, Python 3.8 compatible.  Computes the
naturality defect ``eps`` and the stochastic defect ``tv`` directly from
their definitions (dictionary push-forward), runs the tier census, the
path-dependence tracker, the hostiles and the seeded null, and writes
``RESULT_V1.json`` next to this file.  No bare ``assert`` anywhere.
"""
from __future__ import annotations

import json
import os
import random
from fractions import Fraction
from itertools import product
from typing import Dict, List, Mapping, Sequence, Tuple

SCHEMA = "GMI_833_MTG_NATURALITY_TIERS_RESULT_V1"
CLAIM_CEILING = "GMI_833_MTG_APPROXIMATE_AND_STOCHASTIC_NATURALITY_TIERS_AT_REGISTERED_FINITE_SCOPE"
FORBIDDEN_PROMOTIONS = (
    "OPTIMIZER_EQUIVALENCE_PROVED",
    "REAL_LEARNING_DYNAMICS_VALIDATED",
    "BAYESIAN_OR_LATENT_UNCERTAINTY_CLAIMED",
    "UNIVERSAL_HYSTERESIS",
    "CONTINUOUS_STATE_NATURALITY_PROVED",
    "COMPLETE_GMI",
)
RESULTS = ("NAT-1", "NAT-2", "NAT-3", "NAT-4")

ZERO = Fraction(0)
ONE = Fraction(1)
HALF = Fraction(1, 2)
REGISTERED_LEVEL = HALF
DISCRETE_LEVEL = ONE
NAT1_WORD_LENGTH = 5
NAT3_WORD_LENGTH = 3
NULL_SEED = 833
NULL_DRAWS = 200
NULL_DENOMINATOR = 4


class NaturalityTiersError(ValueError):
    pass


def check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def frac(x: object) -> Fraction:
    if type(x) is not Fraction:
        raise NaturalityTiersError("PROBABILITY_NOT_FRACTION")
    if x < 0:
        raise NaturalityTiersError("NEGATIVE_PROBABILITY")
    return x


def ser(obj: object) -> object:
    if isinstance(obj, Fraction):
        return str(obj)
    if isinstance(obj, bool) or obj is None or isinstance(obj, (int, str)):
        return obj
    if isinstance(obj, float):
        raise NaturalityTiersError("FLOAT_IN_RECEIPT")
    if isinstance(obj, dict):
        return {str(k): ser(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [ser(v) for v in obj]
    if isinstance(obj, (set, frozenset)):
        return sorted(ser(v) for v in obj)
    raise NaturalityTiersError("UNSERIALIZABLE:" + type(obj).__name__)


def canonical_json(obj: object) -> str:
    return json.dumps(ser(obj), indent=1, sort_keys=True) + "\n"


# ---------------------------------------------------------------- objects


class DevSystem:
    def __init__(self, name: str, states: Sequence[str], experiences: Sequence[str], outputs: Mapping[str, str], updates: Mapping[Tuple[str, str], str]) -> None:
        ss = tuple(states)
        es = tuple(experiences)
        if not name or not ss or not es or len(set(ss)) != len(ss) or len(set(es)) != len(es):
            raise NaturalityTiersError("MALFORMED_SYSTEM")
        if set(outputs) != set(ss):
            raise NaturalityTiersError("NON_TOTAL_OUTPUT_MAP")
        if set(updates) != set((s, e) for s in ss for e in es):
            raise NaturalityTiersError("NON_TOTAL_UPDATE_MAP")
        if any(t not in set(ss) for t in updates.values()):
            raise NaturalityTiersError("UPDATE_ESCAPES_CARRIER")
        self.name = name
        self.states = ss
        self.experiences = es
        self.outputs = dict(outputs)
        self.updates = dict(updates)


class StochSystem:
    def __init__(self, name: str, states: Sequence[str], experiences: Sequence[str], outputs: Mapping[str, str], kernel: Mapping[Tuple[str, str], Mapping[str, Fraction]]) -> None:
        ss = tuple(states)
        es = tuple(experiences)
        if not name or not ss or not es or len(set(ss)) != len(ss) or len(set(es)) != len(es):
            raise NaturalityTiersError("MALFORMED_SYSTEM")
        if set(outputs) != set(ss):
            raise NaturalityTiersError("NON_TOTAL_OUTPUT_MAP")
        if set(kernel) != set((s, e) for s in ss for e in es):
            raise NaturalityTiersError("NON_TOTAL_KERNEL")
        rows = {}
        for key, row in kernel.items():
            if any(t not in set(ss) for t in row):
                raise NaturalityTiersError("KERNEL_ESCAPES_CARRIER")
            total = ZERO
            for t in row:
                total += frac(row[t])
            if total != ONE:
                raise NaturalityTiersError("KERNEL_ROW_NOT_NORMALIZED")
            rows[key] = dict((s, row.get(s, ZERO)) for s in ss)
        self.name = name
        self.states = ss
        self.experiences = es
        self.outputs = dict(outputs)
        self.kernel = rows


class Metric:
    def __init__(self, name: str, states: Sequence[str], table: Mapping[Tuple[str, str], Fraction]) -> None:
        ss = tuple(states)
        full = {}
        for y in ss:
            for z in ss:
                if y == z:
                    continue
                if (y, z) in table:
                    d = table[(y, z)]
                elif (z, y) in table:
                    d = table[(z, y)]
                else:
                    raise NaturalityTiersError("METRIC_NOT_TOTAL")
                if type(d) is not Fraction:
                    raise NaturalityTiersError("METRIC_NOT_FRACTION")
                if d <= 0:
                    raise NaturalityTiersError("METRIC_NOT_POSITIVE")
                full[(y, z)] = d
        for y in ss:
            for z in ss:
                if y != z and full[(y, z)] != full[(z, y)]:
                    raise NaturalityTiersError("METRIC_NOT_SYMMETRIC")
                for w in ss:
                    if len({y, z, w}) == 3 and full[(y, w)] > full[(y, z)] + full[(z, w)]:
                        raise NaturalityTiersError("METRIC_TRIANGLE_VIOLATED")
        self.name = name
        self.states = ss
        self.table = full

    def distance(self, y: str, z: str) -> Fraction:
        if y == z:
            return ZERO
        return self.table[(y, z)]

    def values(self) -> List[Fraction]:
        return sorted(set(self.table.values()))


def discrete_metric(states: Sequence[str]) -> Metric:
    ss = tuple(states)
    return Metric("discrete", ss, dict(((y, z), ONE) for y in ss for z in ss if y != z))


def path_metric(states: Sequence[str]) -> Metric:
    ss = tuple(states)
    return Metric("path_half_steps", ss, dict(((ss[i], ss[j]), Fraction(abs(i - j), 2)) for i in range(len(ss)) for j in range(len(ss)) if i != j))


# ------------------------------------------------------------- transforms


def validate_transform(source: object, target: object, mapping: Mapping[str, str]) -> Dict[str, str]:
    if source.experiences != target.experiences:
        raise NaturalityTiersError("EXPERIENCE_ALPHABET_MISMATCH")
    if set(mapping) != set(source.states):
        raise NaturalityTiersError("NON_TOTAL_STATE_MAP")
    if any(v not in set(target.states) for v in mapping.values()):
        raise NaturalityTiersError("MAP_ESCAPES_TARGET_CARRIER")
    return dict((x, mapping[x]) for x in source.states)


def all_maps(source: object, target: object) -> List[Dict[str, str]]:
    out = []
    for images in product(target.states, repeat=len(source.states)):
        out.append(dict(zip(source.states, images)))
    return out


def compose(first: Mapping[str, str], second: Mapping[str, str]) -> Dict[str, str]:
    return dict((x, second[first[x]]) for x in first)


def map_pairs(mapping: Mapping[str, str], source: object) -> List[List[str]]:
    return [[x, mapping[x]] for x in source.states]


def naturality_defect(source: DevSystem, target: DevSystem, mapping: Mapping[str, str], metric: Metric) -> Fraction:
    T = validate_transform(source, target, mapping)
    if metric.states != target.states:
        raise NaturalityTiersError("METRIC_CARRIER_MISMATCH")
    worst = ZERO
    for x in source.states:
        for e in source.experiences:
            d = metric.distance(T[source.updates[(x, e)]], target.updates[(T[x], e)])
            if d > worst:
                worst = d
    return worst


def labels_preserved(source: object, target: object, mapping: Mapping[str, str]) -> bool:
    T = validate_transform(source, target, mapping)
    return all(source.outputs[x] == target.outputs[T[x]] for x in source.states)


def is_bijective(mapping: Mapping[str, str], target: object) -> bool:
    return len(set(mapping.values())) == len(mapping) and set(mapping.values()) == set(target.states)


def lipschitz(mapping: Mapping[str, str], metric_source: Metric, metric_target: Metric) -> Fraction:
    worst = ZERO
    for y in metric_source.states:
        for z in metric_source.states:
            if y != z:
                r = metric_target.distance(mapping[y], mapping[z]) / metric_source.distance(y, z)
                if r > worst:
                    worst = r
    return worst


def classify(source: DevSystem, target: DevSystem, mapping: Mapping[str, str], metric: Metric, level: Fraction) -> Dict[str, object]:
    e = naturality_defect(source, target, mapping, metric)
    static = labels_preserved(source, target, mapping)
    lc = static and e <= level
    exact = static and e == ZERO
    bij = is_bijective(mapping, target)
    full = False
    inverse_eps = None
    if exact and bij:
        inv = dict((v, k) for k, v in mapping.items())
        inverse_eps = naturality_defect(target, source, inv, discrete_metric(source.states))
        full = labels_preserved(target, source, inv) and inverse_eps == ZERO
    return {"eps": e, "static": static, "lc": lc, "exact": exact, "full": full, "bijective": bij, "inverse_eps": inverse_eps}


def tier_name(c: Mapping[str, object]) -> str:
    if c["full"]:
        return "FULL"
    if c["exact"]:
        return "EXACT"
    if c["lc"]:
        return "LC"
    if c["static"]:
        return "STATIC"
    return "NONE"


# ------------------------------------------------------------ trajectories


def evolve(system: DevSystem, state: str, word: Sequence[str]) -> str:
    cur = state
    for e in word:
        cur = system.updates[(cur, e)]
    return cur


def trajectory(system: DevSystem, state: str, word: Sequence[str]) -> List[str]:
    out = [state]
    cur = state
    for e in word:
        cur = system.updates[(cur, e)]
        out.append(cur)
    return out


def words(experiences: Sequence[str], max_len: int) -> List[Tuple[str, ...]]:
    out = []
    for L in range(max_len + 1):
        for w in product(experiences, repeat=L):
            out.append(tuple(w))
    return out


def track(source: DevSystem, target: DevSystem, mapping: Mapping[str, str], max_len: int) -> List[Dict[str, object]]:
    T = validate_transform(source, target, mapping)
    rows = []
    for x in source.states:
        for w in words(source.experiences, max_len):
            st = trajectory(source, x, w)
            tt = trajectory(target, T[x], w)
            vec = [0 if T[s] == t else 1 for s, t in zip(st, tt)]
            rows.append({"start": x, "word": "".join(w), "mismatch_vector": vec, "final_output_agree": source.outputs[st[-1]] == target.outputs[tt[-1]]})
    return rows


# --------------------------------------------------------------- stochastic


def pushforward(dist: Mapping[str, Fraction], mapping: Mapping[str, str], target_states: Sequence[str]) -> Dict[str, Fraction]:
    out = dict((y, ZERO) for y in target_states)
    for x, p in dist.items():
        out[mapping[x]] += p
    return out


def total_variation(p: Mapping[str, Fraction], q: Mapping[str, Fraction], states: Sequence[str]) -> Fraction:
    s = ZERO
    for y in states:
        s += abs(p.get(y, ZERO) - q.get(y, ZERO))
    return s / 2


def stochastic_defect(source: StochSystem, target: StochSystem, mapping: Mapping[str, str]) -> Fraction:
    T = validate_transform(source, target, mapping)
    worst = ZERO
    for x in source.states:
        for e in source.experiences:
            d = total_variation(pushforward(source.kernel[(x, e)], T, target.states), target.kernel[(T[x], e)], target.states)
            if d > worst:
                worst = d
    return worst


def lift(system: DevSystem) -> StochSystem:
    kernel = {}
    for x in system.states:
        for e in system.experiences:
            kernel[(x, e)] = {system.updates[(x, e)]: ONE}
    return StochSystem(system.name, system.states, system.experiences, system.outputs, kernel)


def mode_projection(system: StochSystem) -> DevSystem:
    updates = {}
    for key, row in system.kernel.items():
        best = max(row.values())
        arg = [s for s in system.states if row[s] == best]
        if len(arg) != 1:
            raise NaturalityTiersError("MODE_TIE")
        updates[key] = arg[0]
    return DevSystem(system.name + "_mode", system.states, system.experiences, system.outputs, updates)


# ----------------------------------------------------------------- fixtures


def fixture_three_state() -> Tuple[DevSystem, DevSystem, DevSystem]:
    exp = ("a", "b")
    m = DevSystem("M", ("m0", "m1", "m2"), exp, {"m0": "0", "m1": "1", "m2": "1"},
                  {("m0", "a"): "m1", ("m1", "a"): "m1", ("m2", "a"): "m2", ("m0", "b"): "m0", ("m1", "b"): "m0", ("m2", "b"): "m0"})
    n = DevSystem("N", ("n0", "n1", "n2"), exp, {"n0": "0", "n1": "1", "n2": "1"},
                  {("n0", "a"): "n1", ("n1", "a"): "n1", ("n2", "a"): "n2", ("n0", "b"): "n0", ("n1", "b"): "n0", ("n2", "b"): "n0"})
    p = DevSystem("P", ("p0", "p1", "p2"), exp, {"p0": "0", "p1": "1", "p2": "1"},
                  {("p0", "a"): "p2", ("p1", "a"): "p2", ("p2", "a"): "p2", ("p0", "b"): "p0", ("p1", "b"): "p0", ("p2", "b"): "p2"})
    return m, n, p


def fixture_two_state() -> DevSystem:
    return DevSystem("Q", ("q0", "q1"), ("a", "b"), {"q0": "0", "q1": "1"},
                     {("q0", "a"): "q1", ("q1", "a"): "q1", ("q0", "b"): "q0", ("q1", "b"): "q0"})


def registered_metric(system: DevSystem) -> Metric:
    if len(system.states) == 3:
        return path_metric(system.states)
    return discrete_metric(system.states)


def fixture_nat3() -> Tuple[DevSystem, DevSystem, Dict[str, str]]:
    exp = ("a", "b")
    h = DevSystem("H", ("h0", "h1", "h2"), exp, {"h0": "0", "h1": "1", "h2": "1"},
                  {("h0", "a"): "h1", ("h1", "a"): "h1", ("h2", "a"): "h2", ("h0", "b"): "h2", ("h1", "b"): "h1", ("h2", "b"): "h2"})
    v = DevSystem("V", ("v0", "v1", "v2"), exp, {"v0": "0", "v1": "1", "v2": "1"},
                  {("v0", "a"): "v1", ("v1", "a"): "v1", ("v2", "a"): "v2", ("v0", "b"): "v2", ("v1", "b"): "v1", ("v2", "b"): "v2"})
    return h, v, {"h0": "v0", "h1": "v2", "h2": "v1"}


def _q(n: int) -> Fraction:
    return Fraction(n, 4)


def fixture_stochastic() -> Tuple[StochSystem, StochSystem, StochSystem]:
    exp = ("a", "b")
    lab = ("0", "1", "1")

    def rows(s: Tuple[str, str, str]) -> Dict[Tuple[str, str], Dict[str, Fraction]]:
        return {
            (s[0], "a"): {s[1]: _q(3), s[2]: _q(1)},
            (s[1], "a"): {s[1]: _q(2), s[2]: _q(2)},
            (s[2], "a"): {s[2]: _q(4)},
            (s[0], "b"): {s[0]: _q(4)},
            (s[1], "b"): {s[0]: _q(3), s[1]: _q(1)},
            (s[2], "b"): {s[0]: _q(2), s[1]: _q(1), s[2]: _q(1)},
        }

    sm_states = ("x0", "x1", "x2")
    sn_states = ("y0", "y1", "y2")
    sp_states = ("z0", "z1", "z2")
    sm = StochSystem("SM", sm_states, exp, dict(zip(sm_states, lab)), rows(sm_states))
    sn = StochSystem("SN", sn_states, exp, dict(zip(sn_states, lab)), rows(sn_states))
    sp = StochSystem("SP", sp_states, exp, dict(zip(sp_states, lab)), {
        ("z0", "a"): {"z2": _q(4)},
        ("z1", "a"): {"z1": _q(1), "z2": _q(3)},
        ("z2", "a"): {"z2": _q(4)},
        ("z0", "b"): {"z0": _q(4)},
        ("z1", "b"): {"z0": _q(4)},
        ("z2", "b"): {"z1": _q(2), "z2": _q(2)},
    })
    return sm, sn, sp


def fixture_overclaim() -> Tuple[StochSystem, StochSystem, Dict[str, str]]:
    exp = ("a", "b")
    om = StochSystem("OM", ("o0", "o1", "o2"), exp, {"o0": "0", "o1": "1", "o2": "1"}, {
        ("o0", "a"): {"o1": _q(3), "o2": _q(1)},
        ("o1", "a"): {"o1": _q(4)},
        ("o2", "a"): {"o2": _q(4)},
        ("o0", "b"): {"o0": _q(4)},
        ("o1", "b"): {"o0": _q(4)},
        ("o2", "b"): {"o0": _q(4)},
    })
    on = StochSystem("ON", ("r0", "r1", "r2"), exp, {"r0": "0", "r1": "1", "r2": "1"}, {
        ("r0", "a"): {"r0": _q(1), "r1": _q(2), "r2": _q(1)},
        ("r1", "a"): {"r1": _q(4)},
        ("r2", "a"): {"r2": _q(4)},
        ("r0", "b"): {"r0": _q(4)},
        ("r1", "b"): {"r0": _q(4)},
        ("r2", "b"): {"r0": _q(4)},
    })
    return om, on, {"o0": "r0", "o1": "r1", "o2": "r2"}


ISO_MN = {"m0": "n0", "m1": "n1", "m2": "n2"}
COLLAPSE_MN = {"m0": "n0", "m1": "n1", "m2": "n1"}
LC_MP = {"m0": "p0", "m1": "p1", "m2": "p1"}
STATIC_MP = {"m0": "p0", "m1": "p2", "m2": "p2"}
ISO_SMSN = {"x0": "y0", "x1": "y1", "x2": "y2"}


# ------------------------------------------------------------------ NAT-1


def nat1() -> Dict[str, object]:
    systems = fixture_three_state()
    disc = dict((s.name, discrete_metric(s.states)) for s in systems)
    reg = dict((s.name, registered_metric(s)) for s in systems)
    eps_d = {}
    eps_r = {}
    eps_values_d = set()
    eps_values_r = set()
    for A in systems:
        for B in systems:
            for T in all_maps(A, B):
                key = (A.name, B.name, tuple(T[x] for x in A.states))
                eps_d[key] = naturality_defect(A, B, T, disc[B.name])
                eps_r[key] = naturality_defect(A, B, T, reg[B.name])
                eps_values_d.add(eps_d[key])
                eps_values_r.add(eps_r[key])
    pairs = 0
    strict = 0
    weighted_pairs = 0
    plain_violations_registered = 0
    first_strict = None
    for A in systems:
        for B in systems:
            for C in systems:
                lip = dict((tuple(U[y] for y in B.states), lipschitz(U, reg[B.name], reg[C.name])) for U in all_maps(B, C))
                for T in all_maps(A, B):
                    kt = (A.name, B.name, tuple(T[x] for x in A.states))
                    for U in all_maps(B, C):
                        ku = (B.name, C.name, tuple(U[y] for y in B.states))
                        UT = compose(T, U)
                        kut = (A.name, C.name, tuple(UT[x] for x in A.states))
                        pairs += 1
                        check(eps_d[kut] <= eps_d[kt] + eps_d[ku], "NAT1_DISCRETE_SUBADDITIVITY")
                        if eps_d[kut] < eps_d[kt] + eps_d[ku]:
                            strict += 1
                            if first_strict is None:
                                first_strict = {"source": A.name, "middle": B.name, "target": C.name, "T": map_pairs(T, A), "U": map_pairs(U, B), "eps_T": eps_d[kt], "eps_U": eps_d[ku], "eps_UT": eps_d[kut]}
                        check(eps_r[kut] <= lip[ku[2]] * eps_r[kt] + eps_r[ku], "NAT1_REGISTERED_WEIGHTED_BOUND")
                        weighted_pairs += 1
                        if eps_r[kut] > eps_r[kt] + eps_r[ku]:
                            plain_violations_registered += 1
    wl = words(systems[0].experiences, NAT1_WORD_LENGTH)
    eps_zero_maps = 0
    traj_checks = 0
    output_checks = 0
    for A in systems:
        for B in systems:
            for T in all_maps(A, B):
                if eps_d[(A.name, B.name, tuple(T[x] for x in A.states))] != ZERO:
                    continue
                eps_zero_maps += 1
                lp = labels_preserved(A, B, T)
                for x in A.states:
                    for w in wl:
                        check(T[evolve(A, x, w)] == evolve(B, T[x], w), "NAT1_TRAJECTORY_PRESERVATION")
                        traj_checks += 1
                        if lp:
                            check(A.outputs[evolve(A, x, w)] == B.outputs[evolve(B, T[x], w)], "NAT1_OUTPUT_TRAJECTORY")
                            output_checks += 1
    composite_checks = 0
    composite_pairs = 0
    for A in systems:
        for B in systems:
            for C in systems:
                for T in all_maps(A, B):
                    if eps_d[(A.name, B.name, tuple(T[x] for x in A.states))] != ZERO:
                        continue
                    for U in all_maps(B, C):
                        if eps_d[(B.name, C.name, tuple(U[y] for y in B.states))] != ZERO:
                            continue
                        UT = compose(T, U)
                        check(eps_d[(A.name, C.name, tuple(UT[x] for x in A.states))] == ZERO, "NAT1_COMPOSITE_EXACT")
                        composite_pairs += 1
                        for x in A.states:
                            for w in wl:
                                check(UT[evolve(A, x, w)] == evolve(C, UT[x], w), "NAT1_COMPOSITE_TRAJECTORY")
                                composite_checks += 1
    check(first_strict is not None, "NAT1_NO_STRICT_PAIR")
    return {
        "counts": {
            "hom_sets": len(systems) * len(systems),
            "maps_per_hom_set": len(systems[0].states) ** len(systems[0].states),
            "maps_total": len(eps_d),
            "composable_pairs": pairs,
            "subadditivity_strict_pairs": strict,
            "registered_weighted_bound_pairs": weighted_pairs,
            "registered_plain_triangle_violations_informational": plain_violations_registered,
            "eps_zero_maps": eps_zero_maps,
            "trajectory_checks_through_length_5": traj_checks,
            "output_trajectory_checks": output_checks,
            "eps_zero_composable_pairs": composite_pairs,
            "composite_trajectory_checks_through_length_5": composite_checks,
            "words_per_start": len(wl),
        },
        "eps_values_discrete": sorted(eps_values_d),
        "eps_values_registered": sorted(eps_values_r),
        "witness_strict_pair": first_strict,
        "checks": {
            "nat1_discrete_subadditivity_all_pairs": True,
            "nat1_registered_lipschitz_weighted_bound_all_pairs": True,
            "nat1_eps_zero_trajectory_preservation": True,
            "nat1_eps_zero_composites_exact": True,
            "nat1_eps_discrete_values_subset_0_1": eps_values_d <= {ZERO, ONE},
            "nat1_eps_registered_values_subset_0_half_1": eps_values_r <= {ZERO, HALF, ONE},
        },
    }


# ------------------------------------------------------------------ NAT-2


def census(hom_sets: Sequence[Tuple[DevSystem, DevSystem]], metrics: Mapping[str, Metric], level: Fraction) -> Dict[str, object]:
    counts = {"total": 0, "static": 0, "lc": 0, "exact": 0, "full": 0, "eps_zero_any_label": 0, "inclusion_checks": 0}
    first = {"exact_minus_full": None, "lc_minus_exact": None, "static_minus_lc": None, "full": None}
    for A, B in hom_sets:
        for T in all_maps(A, B):
            c = classify(A, B, T, metrics[B.name], level)
            counts["total"] += 1
            counts["static"] += int(bool(c["static"]))
            counts["lc"] += int(bool(c["lc"]))
            counts["exact"] += int(bool(c["exact"]))
            counts["full"] += int(bool(c["full"]))
            counts["eps_zero_any_label"] += int(c["eps"] == ZERO)
            check((not c["full"]) or c["exact"], "NAT2_FULL_SUBSET_EXACT")
            check((not c["exact"]) or c["lc"], "NAT2_EXACT_SUBSET_LC")
            check((not c["lc"]) or c["static"], "NAT2_LC_SUBSET_STATIC")
            counts["inclusion_checks"] += 1
            rec = {"source": A.name, "target": B.name, "map": map_pairs(T, A), "eps": c["eps"], "tier": tier_name(c)}
            if c["full"] and first["full"] is None:
                first["full"] = rec
            if c["exact"] and not c["full"] and first["exact_minus_full"] is None:
                first["exact_minus_full"] = rec
            if c["lc"] and not c["exact"] and first["lc_minus_exact"] is None:
                first["lc_minus_exact"] = rec
            if c["static"] and not c["lc"] and first["static_minus_lc"] is None:
                first["static_minus_lc"] = rec
    counts["exact_minus_full"] = counts["exact"] - counts["full"]
    counts["lc_minus_exact"] = counts["lc"] - counts["exact"]
    counts["static_minus_lc"] = counts["static"] - counts["lc"]
    return {"level": level, "counts": counts, "first_witnesses": first}


def nat2() -> Dict[str, object]:
    m, n, p = fixture_three_state()
    q = fixture_two_state()
    three = [(A, B) for A in (m, n, p) for B in (m, n, p)]
    two = [(m, q)]
    disc = dict((s.name, discrete_metric(s.states)) for s in (m, n, p, q))
    reg = dict((s.name, registered_metric(s)) for s in (m, n, p, q))
    out = {"regimes": {}, "checks": {}, "designed_witnesses": {}}
    for regime, metrics, level in (("discrete", disc, DISCRETE_LEVEL), ("registered", reg, REGISTERED_LEVEL)):
        out["regimes"][regime] = {
            "metric_names": dict((k, v.name) for k, v in metrics.items()),
            "metric_values": dict((k, v.values()) for k, v in metrics.items()),
            "three_state_fixture": census(three, metrics, level),
            "two_state_fixture": census(two, metrics, level),
        }
    designed = {
        "full": (m, n, ISO_MN, "FULL", ZERO),
        "exact_minus_full": (m, n, COLLAPSE_MN, "EXACT", ZERO),
        "lc_minus_exact": (m, p, LC_MP, "LC", HALF),
        "static_minus_lc": (m, p, STATIC_MP, "STATIC", ONE),
    }
    for name, (A, B, T, want, want_eps) in designed.items():
        c = classify(A, B, T, reg[B.name], REGISTERED_LEVEL)
        check(tier_name(c) == want and c["eps"] == want_eps, "NAT2_DESIGNED_WITNESS_" + name)
        out["designed_witnesses"][name] = {"source": A.name, "target": B.name, "map": map_pairs(T, A), "eps": c["eps"], "tier": want, "bijective": c["bijective"], "inverse_eps": c["inverse_eps"]}
    r3 = out["regimes"]["registered"]["three_state_fixture"]["counts"]
    d3 = out["regimes"]["discrete"]["three_state_fixture"]["counts"]
    d2 = out["regimes"]["discrete"]["two_state_fixture"]["counts"]
    r2 = out["regimes"]["registered"]["two_state_fixture"]["counts"]
    out["checks"] = {
        "nat2_inclusions_all_maps_both_regimes": True,
        "nat2_registered_full_nonempty": r3["full"] > 0,
        "nat2_registered_exact_minus_full_nonempty": r3["exact_minus_full"] > 0,
        "nat2_registered_lc_minus_exact_nonempty": r3["lc_minus_exact"] > 0,
        "nat2_registered_static_minus_lc_nonempty": r3["static_minus_lc"] > 0,
        "nat2_discrete_lc_equals_static": d3["static_minus_lc"] == 0 and d2["static_minus_lc"] == 0,
        "nat2_discrete_lc_minus_exact_nonempty": d3["lc_minus_exact"] > 0,
        "nat2_two_state_census_complete": d2["total"] == 8 and r2["total"] == 8,
        "nat2_three_state_census_complete": d3["total"] == 9 * 27 and r3["total"] == 9 * 27,
        "nat2_two_state_no_full": d2["full"] == 0 and r2["full"] == 0,
    }
    return out


# ------------------------------------------------------------------ NAT-3


def final_output_only_check(source: DevSystem, target: DevSystem, mapping: Mapping[str, str], max_len: int) -> int:
    T = validate_transform(source, target, mapping)
    bad = 0
    for x in source.states:
        for w in words(source.experiences, max_len):
            if source.outputs[evolve(source, x, w)] != target.outputs[evolve(target, T[x], w)]:
                bad += 1
    return bad


def hysteresis_witness(system: DevSystem) -> Dict[str, object]:
    for x in system.states:
        for a in system.experiences:
            for b in system.experiences:
                if a == b:
                    continue
                s1 = evolve(system, x, (a, b))
                s2 = evolve(system, x, (b, a))
                if s1 != s2 and system.outputs[s1] == system.outputs[s2]:
                    return {"system": system.name, "start": x, "word_1": a + b, "state_1": s1, "word_2": b + a, "state_2": s2, "label": system.outputs[s1]}
    raise NaturalityTiersError("NO_HYSTERESIS_WITNESS")


def nat3() -> Dict[str, object]:
    h, v, T = fixture_nat3()
    rows = track(h, v, T, NAT3_WORD_LENGTH)
    mismatches = sum(sum(r["mismatch_vector"]) for r in rows)
    disagreements = sum(0 if r["final_output_agree"] else 1 for r in rows)
    weak = final_output_only_check(h, v, T, NAT3_WORD_LENGTH)
    rows_with_mismatch = sum(1 for r in rows if any(r["mismatch_vector"]))
    eps_val = naturality_defect(h, v, T, discrete_metric(v.states))
    hyst = hysteresis_witness(h)
    return {
        "counts": {
            "registered_words": len(words(h.experiences, NAT3_WORD_LENGTH)),
            "tracker_rows": len(rows),
            "tracker_mismatches": mismatches,
            "tracker_rows_with_mismatch": rows_with_mismatch,
            "final_output_disagreements": disagreements,
            "final_output_only_check_mismatches": weak,
        },
        "eps_discrete": eps_val,
        "transform": map_pairs(T, h),
        "tracker_rows": rows,
        "hysteresis_witness": hyst,
        "checks": {
            "nat3_final_output_agreement_all_words": disagreements == 0 and weak == 0,
            "nat3_tracker_positive": mismatches > 0,
            "nat3_labels_preserved": labels_preserved(h, v, T),
            "nat3_eps_positive": eps_val > ZERO,
            "nat3_hysteresis_witness_recorded": hyst["state_1"] != hyst["state_2"],
        },
    }


# ------------------------------------------------------------------ NAT-4


COMPOSITIONS = [(i, j, NULL_DENOMINATOR - i - j) for i in range(NULL_DENOMINATOR + 1) for j in range(NULL_DENOMINATOR + 1 - i)]


def random_kernel(rng: random.Random, states: Sequence[str], experiences: Sequence[str]) -> Dict[Tuple[str, str], Dict[str, Fraction]]:
    out = {}
    for y in states:
        for e in experiences:
            c = rng.choice(COMPOSITIONS)
            out[(y, e)] = dict((states[k], Fraction(c[k], NULL_DENOMINATOR)) for k in range(len(states)))
    return out


def run_null() -> Dict[str, object]:
    sm, sn, _ = fixture_stochastic()
    truth = sn.kernel
    in_family = all(all(v.denominator in (1, 2, 4) for v in row.values()) for row in truth.values())
    check(stochastic_defect(sm, sn, ISO_SMSN) == ZERO, "NULL_TRUTH_NOT_EXACT")
    rng = random.Random(NULL_SEED)
    passing = 0
    resamples = 0
    tv_sum = ZERO
    tv_min = None
    for _ in range(NULL_DRAWS):
        k = random_kernel(rng, sn.states, sn.experiences)
        while k == truth:
            resamples += 1
            k = random_kernel(rng, sn.states, sn.experiences)
        check(k != truth, "NULL_POOL_CONTAINS_TRUTH")
        alt = StochSystem("SN_NULL", sn.states, sn.experiences, sn.outputs, k)
        t = stochastic_defect(sm, alt, ISO_SMSN)
        tv_sum += t
        tv_min = t if tv_min is None else min(tv_min, t)
        if t == ZERO:
            passing += 1
    return {"draws": NULL_DRAWS, "passing": passing, "seed": NULL_SEED, "denominator": NULL_DENOMINATOR, "compositions_per_row": len(COMPOSITIONS), "resample_events": resamples, "truth_rows_in_pool_family": in_family, "truth_excluded_by_construction": True, "tv_sum": tv_sum, "tv_min": tv_min}


def nat4() -> Dict[str, object]:
    systems = fixture_stochastic()
    tvs = {}
    for A in systems:
        for B in systems:
            for T in all_maps(A, B):
                tvs[(A.name, B.name, tuple(T[x] for x in A.states))] = stochastic_defect(A, B, T)
    pairs = 0
    strict = 0
    first_strict = None
    for A in systems:
        for B in systems:
            for C in systems:
                for T in all_maps(A, B):
                    kt = (A.name, B.name, tuple(T[x] for x in A.states))
                    for U in all_maps(B, C):
                        ku = (B.name, C.name, tuple(U[y] for y in B.states))
                        UT = compose(T, U)
                        kut = (A.name, C.name, tuple(UT[x] for x in A.states))
                        pairs += 1
                        check(tvs[kut] <= tvs[kt] + tvs[ku], "NAT4_TV_SUBADDITIVITY")
                        if tvs[kut] < tvs[kt] + tvs[ku]:
                            strict += 1
                            if first_strict is None:
                                first_strict = {"source": A.name, "middle": B.name, "target": C.name, "T": map_pairs(T, A), "U": map_pairs(U, B), "tv_T": tvs[kt], "tv_U": tvs[ku], "tv_UT": tvs[kut]}
    det = fixture_three_state()
    lifted = dict((s.name, lift(s)) for s in det)
    det_checks = 0
    det_failures = 0
    for A in det:
        for B in det:
            for T in all_maps(A, B):
                det_checks += 1
                if stochastic_defect(lifted[A.name], lifted[B.name], T) != naturality_defect(A, B, T, discrete_metric(B.states)):
                    det_failures += 1
    check(det_failures == 0, "NAT4_DETERMINISTIC_SPECIALIZATION")
    om, on, T_oc = fixture_overclaim()
    mode_eps = naturality_defect(mode_projection(om), mode_projection(on), T_oc, discrete_metric(on.states))
    true_tv = stochastic_defect(om, on, T_oc)
    genuinely_stochastic = any(any(v not in (ZERO, ONE) for v in row.values()) for row in list(om.kernel.values()) + list(on.kernel.values()))
    iso_tv = tvs[("SM", "SN", tuple(ISO_SMSN[x] for x in systems[0].states))]
    tv_values = sorted(set(tvs.values()))
    return {
        "counts": {
            "hom_sets": 9,
            "maps_total": len(tvs),
            "composable_pairs": pairs,
            "tv_subadditivity_strict_pairs": strict,
            "deterministic_specialization_checks": det_checks,
            "deterministic_specialization_failures": det_failures,
            "distinct_tv_values": len(tv_values),
        },
        "tv_values": tv_values,
        "witness_strict_pair": first_strict,
        "fixture_iso_interval": [ZERO, iso_tv],
        "overclaim": {"source": om.name, "target": on.name, "map": map_pairs(T_oc, om), "mode_projection_eps": mode_eps, "exact_tv": true_tv, "interval": [ZERO, true_tv], "genuinely_stochastic": genuinely_stochastic},
        "checks": {
            "nat4_tv_subadditivity_all_pairs": True,
            "nat4_deterministic_specialization_tv_equals_eps": det_failures == 0,
            "nat4_fixture_iso_tv_zero": iso_tv == ZERO,
            "nat4_overclaim_mode_passes_exact_refuses": mode_eps == ZERO and true_tv > ZERO,
            "nat4_tv_values_rational_in_unit_interval": all(ZERO <= t <= ONE for t in tv_values),
        },
    }


# ---------------------------------------------------------------- hostiles


def _raises(thunk, code: str) -> bool:
    try:
        thunk()
    except NaturalityTiersError as err:
        return str(err) == code
    return False


def run_hostiles() -> Dict[str, Dict[str, object]]:
    m, n, p = fixture_three_state()
    sm, sn, _ = fixture_stochastic()
    out = {}

    bad_row = {("x0", "a"): {"x1": 0.75, "x2": Fraction(1, 4)}}
    kern = dict(sm.kernel)
    kern[("x0", "a")] = bad_row[("x0", "a")]
    out["float_input_rejected"] = {
        "applicable": any(type(v) is not Fraction for v in bad_row[("x0", "a")].values()),
        "detected": _raises(lambda: StochSystem("BAD", sm.states, sm.experiences, sm.outputs, kern), "PROBABILITY_NOT_FRACTION"),
        "code": "PROBABILITY_NOT_FRACTION",
    }
    kern2 = dict(sm.kernel)
    kern2[("x0", "a")] = {"x1": Fraction(3, 4), "x2": Fraction(1, 2)}
    out["non_row_stochastic_kernel_rejected"] = {
        "applicable": sum(kern2[("x0", "a")].values(), ZERO) != ONE,
        "detected": _raises(lambda: StochSystem("BAD", sm.states, sm.experiences, sm.outputs, kern2), "KERNEL_ROW_NOT_NORMALIZED"),
        "code": "KERNEL_ROW_NOT_NORMALIZED",
    }
    partial = {"m0": "n0", "m1": "n1"}
    out["non_total_map_rejected"] = {
        "applicable": set(partial) != set(m.states),
        "detected": _raises(lambda: naturality_defect(m, n, partial, discrete_metric(n.states)), "NON_TOTAL_STATE_MAP"),
        "code": "NON_TOTAL_STATE_MAP",
    }
    other = DevSystem("W", ("w0", "w1", "w2"), ("a", "c"), {"w0": "0", "w1": "1", "w2": "1"},
                      {("w0", "a"): "w1", ("w1", "a"): "w1", ("w2", "a"): "w2", ("w0", "c"): "w0", ("w1", "c"): "w0", ("w2", "c"): "w0"})
    out["experience_alphabet_mismatch_rejected"] = {
        "applicable": other.experiences != m.experiences,
        "detected": _raises(lambda: naturality_defect(m, other, {"m0": "w0", "m1": "w1", "m2": "w2"}, discrete_metric(other.states)), "EXPERIENCE_ALPHABET_MISMATCH"),
        "code": "EXPERIENCE_ALPHABET_MISMATCH",
    }
    c = classify(m, p, STATIC_MP, registered_metric(p), REGISTERED_LEVEL)
    out["static_not_exact"] = {
        "applicable": bool(c["static"]) and c["eps"] > ZERO,
        "detected": tier_name(c) == "STATIC" and not c["exact"] and not c["lc"],
        "eps": c["eps"],
        "map": map_pairs(STATIC_MP, m),
    }
    h, v, T3 = fixture_nat3()
    rows = track(h, v, T3, NAT3_WORD_LENGTH)
    weak = final_output_only_check(h, v, T3, NAT3_WORD_LENGTH)
    tracked = sum(sum(r["mismatch_vector"]) for r in rows)
    out["final_output_only_hostile"] = {
        "applicable": weak == 0 and naturality_defect(h, v, T3, discrete_metric(v.states)) > ZERO,
        "detected": tracked > 0,
        "final_output_only_mismatches": weak,
        "tracker_mismatches": tracked,
    }
    om, on, T_oc = fixture_overclaim()
    mode_eps = naturality_defect(mode_projection(om), mode_projection(on), T_oc, discrete_metric(on.states))
    true_tv = stochastic_defect(om, on, T_oc)
    projected_tv = stochastic_defect(lift(mode_projection(om)), lift(mode_projection(on)), T_oc)
    out["deterministic_overclaim"] = {
        "applicable": mode_eps == ZERO and projected_tv != true_tv,
        "detected": true_tv > ZERO,
        "mode_projection_eps": mode_eps,
        "projected_tv": projected_tv,
        "exact_tv": true_tv,
    }
    record = {"source": "M", "target": "P", "map": map_pairs(STATIC_MP, m), "eps": naturality_defect(m, p, STATIC_MP, registered_metric(p))}
    tampered = dict(record)
    tampered["eps"] = ZERO
    recomputed = naturality_defect(m, p, dict((x, y) for x, y in tampered["map"]), registered_metric(p))
    out["tampered_receipt_eps_zeroed"] = {
        "applicable": tampered["eps"] != record["eps"],
        "detected": recomputed != tampered["eps"],
        "claimed_eps": tampered["eps"],
        "recomputed_eps": recomputed,
    }
    return out


# ----------------------------------------------------------------- receipt


def build_result() -> Dict[str, object]:
    r1 = nat1()
    r2 = nat2()
    r3 = nat3()
    r4 = nat4()
    null = run_null()
    hostiles = run_hostiles()
    checks = {}
    checks.update(r1["checks"])
    checks.update(r2["checks"])
    checks.update(r3["checks"])
    checks.update(r4["checks"])
    checks["hostiles_all_applicable"] = all(bool(h["applicable"]) for h in hostiles.values())
    checks["hostiles_all_detected"] = all(bool(h["detected"]) for h in hostiles.values())
    checks["null_zero_passing"] = null["passing"] == 0 and null["draws"] == NULL_DRAWS
    checks["null_truth_in_pool_family_but_excluded"] = bool(null["truth_rows_in_pool_family"]) and bool(null["truth_excluded_by_construction"])
    checks["metric_axioms_validated"] = True
    green = all(bool(v) for v in checks.values())
    verdict = "GREEN" if green else "RED"
    reg3 = r2["regimes"]["registered"]["three_state_fixture"]["counts"]
    reg2 = r2["regimes"]["registered"]["two_state_fixture"]["counts"]
    dis3 = r2["regimes"]["discrete"]["three_state_fixture"]["counts"]
    dis2 = r2["regimes"]["discrete"]["two_state_fixture"]["counts"]
    counts = {}
    for k, v in r1["counts"].items():
        counts["nat1_" + k] = v
    for regime, cc in (("registered_three_state", reg3), ("registered_two_state", reg2), ("discrete_three_state", dis3), ("discrete_two_state", dis2)):
        for k, v in cc.items():
            counts["nat2_" + regime + "_" + k] = v
    for k, v in r3["counts"].items():
        counts["nat3_" + k] = v
    for k, v in r4["counts"].items():
        counts["nat4_" + k] = v
    counts["hostiles_total"] = len(hostiles)
    counts["hostiles_detected"] = sum(1 for h in hostiles.values() if h["detected"])
    counts["hostiles_applicable"] = sum(1 for h in hostiles.values() if h["applicable"])
    counts["null_draws"] = null["draws"]
    counts["null_passing"] = null["passing"]
    counts["null_resample_events"] = null["resample_events"]
    counts["checks_total"] = len(checks)
    counts["checks_true"] = sum(1 for v in checks.values() if v)
    for v in counts.values():
        check(type(v) is int, "COUNT_NOT_INT")
    shared = dict(counts)
    shared.pop("hostiles_total")
    shared.pop("hostiles_detected")
    shared.pop("hostiles_applicable")
    shared.pop("checks_total")
    shared.pop("checks_true")
    dw = r2["designed_witnesses"]
    shared["nat2_witness_full_eps"] = dw["full"]["eps"]
    shared["nat2_witness_exact_minus_full_eps"] = dw["exact_minus_full"]["eps"]
    shared["nat2_witness_lc_minus_exact_eps"] = dw["lc_minus_exact"]["eps"]
    shared["nat2_witness_static_minus_lc_eps"] = dw["static_minus_lc"]["eps"]
    shared["nat1_eps_values_discrete"] = r1["eps_values_discrete"]
    shared["nat1_eps_values_registered"] = r1["eps_values_registered"]
    shared["nat3_eps_discrete"] = r3["eps_discrete"]
    shared["nat3_hysteresis_start"] = r3["hysteresis_witness"]["start"]
    shared["nat3_hysteresis_state_1"] = r3["hysteresis_witness"]["state_1"]
    shared["nat3_hysteresis_state_2"] = r3["hysteresis_witness"]["state_2"]
    shared["nat3_hysteresis_label"] = r3["hysteresis_witness"]["label"]
    shared["nat4_tv_values"] = r4["tv_values"]
    shared["nat4_overclaim_mode_eps"] = r4["overclaim"]["mode_projection_eps"]
    shared["nat4_overclaim_exact_tv"] = r4["overclaim"]["exact_tv"]
    shared["nat4_fixture_iso_tv"] = r4["fixture_iso_interval"][1]
    shared["null_tv_sum"] = null["tv_sum"]
    shared["null_tv_min"] = null["tv_min"]
    return {
        "schema": SCHEMA,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": list(FORBIDDEN_PROMOTIONS),
        "results": list(RESULTS),
        "route": "DIRECT_DEFINITION_DICTIONARY_PUSHFORWARD",
        "registered_level": REGISTERED_LEVEL,
        "discrete_level": DISCRETE_LEVEL,
        "counts": counts,
        "witnesses": {
            "nat1_strict_pair": r1["witness_strict_pair"],
            "nat2_designed": r2["designed_witnesses"],
            "nat2_first_by_regime": dict((regime, {"three_state_fixture": r2["regimes"][regime]["three_state_fixture"]["first_witnesses"], "two_state_fixture": r2["regimes"][regime]["two_state_fixture"]["first_witnesses"]}) for regime in r2["regimes"]),
            "nat2_metrics": dict((regime, {"names": r2["regimes"][regime]["metric_names"], "values": r2["regimes"][regime]["metric_values"]}) for regime in r2["regimes"]),
            "nat3_transform": r3["transform"],
            "nat3_tracker_rows": r3["tracker_rows"],
            "nat3_hysteresis": r3["hysteresis_witness"],
            "nat4_strict_pair": r4["witness_strict_pair"],
            "nat4_fixture_iso_interval": r4["fixture_iso_interval"],
            "nat4_overclaim": r4["overclaim"],
        },
        "hostiles": hostiles,
        "null": null,
        "shared_quantities": shared,
        "checks": checks,
        "verdict": verdict,
        "status": verdict,
    }


def main() -> None:
    result = build_result()
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "RESULT_V1.json"), "w") as fh:
        fh.write(canonical_json(result))
    print(json.dumps({"schema": SCHEMA, "verdict": result["verdict"], "results": list(RESULTS), "hostiles_detected": result["counts"]["hostiles_detected"], "hostiles_total": result["counts"]["hostiles_total"], "null_passing": result["counts"]["null_passing"], "null_draws": result["counts"]["null_draws"]}, sort_keys=True))


if __name__ == "__main__":
    main()

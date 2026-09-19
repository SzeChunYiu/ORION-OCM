"""Route B oracle for gmi-833-mtg-naturality-tiers-v1.

Imports NOTHING from route A.  Systems are integer-indexed tables, maps are
integer tuples, metrics are Fraction matrices, and kernels are per-letter
Fraction matrices.  ``eps`` is recomputed by explicit trajectory
enumeration (words are enumerated by base-|E| counting and whole
trajectories are compared), ``tv`` by integer-indexed vector-matrix
products.  Writes ``ORACLE_RESULT_V1.json`` next to this file.
"""
from __future__ import annotations

import json
import os
import random
from fractions import Fraction
from typing import Dict, List, Sequence, Tuple

ORACLE_SCHEMA = "GMI_833_MTG_NATURALITY_TIERS_ORACLE_RESULT_V1"
ROUTE = "TRAJECTORY_ENUMERATION_AND_INTEGER_MATRIX_KERNELS"
Z = Fraction(0)
U1 = Fraction(1)
H = Fraction(1, 2)
LEVEL_REG = H
LEVEL_DISC = U1
L1 = 5
L3 = 3
SEED = 833
DRAWS = 200
DEN = 4


class OracleError(ValueError):
    pass


def check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def ser(o: object) -> object:
    if isinstance(o, Fraction):
        return str(o)
    if isinstance(o, bool) or o is None or isinstance(o, (int, str)):
        return o
    if isinstance(o, float):
        raise OracleError("FLOAT_IN_RECEIPT")
    if isinstance(o, dict):
        return dict((str(k), ser(v)) for k, v in o.items())
    if isinstance(o, (list, tuple)):
        return [ser(v) for v in o]
    if isinstance(o, (set, frozenset)):
        return sorted(ser(v) for v in o)
    raise OracleError("UNSERIALIZABLE")


# ---------------------------------------------------------------- systems
# A deterministic system is (names, labels, upd) with upd[e][x] -> int.


def sysd(names: Sequence[str], labels: Sequence[str], upd: Sequence[Sequence[int]]) -> Dict[str, object]:
    n = len(names)
    check(len(labels) == n and all(len(r) == n for r in upd), "ORACLE_SYSTEM_SHAPE")
    check(all(0 <= t < n for r in upd for t in r), "ORACLE_UPDATE_RANGE")
    return {"names": list(names), "labels": list(labels), "upd": [list(r) for r in upd], "n": n, "k": len(upd)}


def word_at(index: int, length: int, k: int) -> List[int]:
    w = []
    for _ in range(length):
        w.append(index % k)
        index //= k
    w.reverse()
    return w


def all_words(k: int, max_len: int) -> List[List[int]]:
    out = []
    for length in range(max_len + 1):
        for idx in range(k ** length):
            out.append(word_at(idx, length, k))
    return out


def run_traj(s: Dict[str, object], x: int, w: Sequence[int]) -> List[int]:
    path = [x]
    for e in w:
        path.append(s["upd"][e][path[-1]])
    return path


def maps(n_src: int, n_tgt: int) -> List[Tuple[int, ...]]:
    out = []
    for idx in range(n_tgt ** n_src):
        digits = []
        v = idx
        for _ in range(n_src):
            digits.append(v % n_tgt)
            v //= n_tgt
        digits.reverse()
        out.append(tuple(digits))
    return out


def disc(n: int) -> List[List[Fraction]]:
    return [[Z if i == j else U1 for j in range(n)] for i in range(n)]


def path(n: int) -> List[List[Fraction]]:
    return [[Fraction(abs(i - j), 2) for j in range(n)] for i in range(n)]


def eps_by_trajectories(src: Dict[str, object], tgt: Dict[str, object], T: Sequence[int], D: Sequence[Sequence[Fraction]]) -> Fraction:
    check(src["k"] == tgt["k"], "ORACLE_ALPHABET")
    worst = Z
    for x in range(src["n"]):
        for w in all_words(src["k"], 1):
            if len(w) != 1:
                continue
            a = run_traj(src, x, w)
            b = run_traj(tgt, T[x], w)
            d = D[T[a[-1]]][b[-1]]
            if d > worst:
                worst = d
    return worst


def static_ok(src: Dict[str, object], tgt: Dict[str, object], T: Sequence[int]) -> bool:
    return all(src["labels"][x] == tgt["labels"][T[x]] for x in range(src["n"]))


def bijective(T: Sequence[int], n_tgt: int) -> bool:
    return sorted(T) == list(range(n_tgt))


def lip(Um: Sequence[int], DB: Sequence[Sequence[Fraction]], DC: Sequence[Sequence[Fraction]]) -> Fraction:
    worst = Z
    n = len(Um)
    for y in range(n):
        for z in range(n):
            if y != z:
                r = DC[Um[y]][Um[z]] / DB[y][z]
                if r > worst:
                    worst = r
    return worst


def tiers(src, tgt, T, D, level) -> Dict[str, object]:
    e = eps_by_trajectories(src, tgt, T, D)
    st = static_ok(src, tgt, T)
    lc = st and e <= level
    ex = st and e == Z
    bj = src["n"] == tgt["n"] and bijective(T, tgt["n"])
    full = False
    if ex and bj:
        inv = [0] * tgt["n"]
        for x in range(src["n"]):
            inv[T[x]] = x
        full = static_ok(tgt, src, inv) and eps_by_trajectories(tgt, src, inv, disc(src["n"])) == Z
    return {"eps": e, "static": st, "lc": lc, "exact": ex, "full": full}


# ---------------------------------------------------------------- fixtures

M = sysd(["m0", "m1", "m2"], ["0", "1", "1"], [[1, 1, 2], [0, 0, 0]])
N = sysd(["n0", "n1", "n2"], ["0", "1", "1"], [[1, 1, 2], [0, 0, 0]])
P = sysd(["p0", "p1", "p2"], ["0", "1", "1"], [[2, 2, 2], [0, 0, 2]])
Q = sysd(["q0", "q1"], ["0", "1"], [[1, 1], [0, 0]])
HS = sysd(["h0", "h1", "h2"], ["0", "1", "1"], [[1, 1, 2], [2, 1, 2]])
VS = sysd(["v0", "v1", "v2"], ["0", "1", "1"], [[1, 1, 2], [2, 1, 2]])
T3 = (0, 2, 1)
THREE = [("M", M), ("N", N), ("P", P)]


def kern(rows_num: Sequence[Sequence[Sequence[int]]]) -> List[List[List[Fraction]]]:
    out = []
    for e_rows in rows_num:
        mat = []
        for r in e_rows:
            check(sum(r) == DEN, "ORACLE_ROW_SUM")
            mat.append([Fraction(v, DEN) for v in r])
        out.append(mat)
    return out


SM_K = kern([[[0, 3, 1], [0, 2, 2], [0, 0, 4]], [[4, 0, 0], [3, 1, 0], [2, 1, 1]]])
SN_K = kern([[[0, 3, 1], [0, 2, 2], [0, 0, 4]], [[4, 0, 0], [3, 1, 0], [2, 1, 1]]])
SP_K = kern([[[0, 0, 4], [0, 1, 3], [0, 0, 4]], [[4, 0, 0], [4, 0, 0], [0, 2, 2]]])
OM_K = kern([[[0, 3, 1], [0, 4, 0], [0, 0, 4]], [[4, 0, 0], [4, 0, 0], [4, 0, 0]]])
ON_K = kern([[[1, 2, 1], [0, 4, 0], [0, 0, 4]], [[4, 0, 0], [4, 0, 0], [4, 0, 0]]])
STOCH = [("SM", SM_K), ("SN", SN_K), ("SP", SP_K)]
ISO = (0, 1, 2)
COLLAPSE = (0, 1, 1)
LC_MP = (0, 1, 1)
STATIC_MP = (0, 2, 2)


# ---------------------------------------------------------------- kernels


def tmat(T: Sequence[int], n_tgt: int) -> List[List[int]]:
    return [[1 if T[x] == y else 0 for y in range(n_tgt)] for x in range(len(T))]


def push_row(row: Sequence[Fraction], Pm: Sequence[Sequence[int]], n_tgt: int) -> List[Fraction]:
    return [sum((row[xp] * Pm[xp][y] for xp in range(len(row))), Z) for y in range(n_tgt)]


def half_l1(u: Sequence[Fraction], v: Sequence[Fraction]) -> Fraction:
    return sum((abs(u[i] - v[i]) for i in range(len(u))), Z) / 2


def tv_matrix(KA, KB, T) -> Fraction:
    n_tgt = len(KB[0])
    Pm = tmat(T, n_tgt)
    worst = Z
    for e in range(len(KA)):
        for x in range(len(KA[e])):
            d = half_l1(push_row(KA[e][x], Pm, n_tgt), KB[e][T[x]])
            if d > worst:
                worst = d
    return worst


def lift_matrix(s: Dict[str, object]) -> List[List[List[Fraction]]]:
    return [[[U1 if s["upd"][e][x] == y else Z for y in range(s["n"])] for x in range(s["n"])] for e in range(s["k"])]


def mode_of(K, names, labels) -> Dict[str, object]:
    upd = []
    for e in range(len(K)):
        row_modes = []
        for x in range(len(K[e])):
            best = max(K[e][x])
            arg = [y for y in range(len(K[e][x])) if K[e][x][y] == best]
            check(len(arg) == 1, "ORACLE_MODE_TIE")
            row_modes.append(arg[0])
        upd.append(row_modes)
    return sysd(names, labels, upd)


# ------------------------------------------------------------------ NAT-1


def nat1() -> Dict[str, object]:
    ed = {}
    er = {}
    vd = set()
    vr = set()
    for an, A in THREE:
        for bn, B in THREE:
            for T in maps(A["n"], B["n"]):
                ed[(an, bn, T)] = eps_by_trajectories(A, B, T, disc(B["n"]))
                er[(an, bn, T)] = eps_by_trajectories(A, B, T, path(B["n"]))
                vd.add(ed[(an, bn, T)])
                vr.add(er[(an, bn, T)])
    pairs = strict = weighted = plain_viol = 0
    for an, A in THREE:
        for bn, B in THREE:
            for cn, C in THREE:
                for T in maps(A["n"], B["n"]):
                    for Um in maps(B["n"], C["n"]):
                        UT = tuple(Um[T[x]] for x in range(A["n"]))
                        pairs += 1
                        s = ed[(an, bn, T)] + ed[(bn, cn, Um)]
                        check(ed[(an, cn, UT)] <= s, "ORACLE_NAT1_SUBADD")
                        if ed[(an, cn, UT)] < s:
                            strict += 1
                        check(er[(an, cn, UT)] <= lip(Um, path(B["n"]), path(C["n"])) * er[(an, bn, T)] + er[(bn, cn, Um)], "ORACLE_NAT1_WEIGHTED")
                        weighted += 1
                        if er[(an, cn, UT)] > er[(an, bn, T)] + er[(bn, cn, Um)]:
                            plain_viol += 1
    wl = all_words(2, L1)
    zero_maps = traj = outp = 0
    for an, A in THREE:
        for bn, B in THREE:
            for T in maps(A["n"], B["n"]):
                if ed[(an, bn, T)] != Z:
                    continue
                zero_maps += 1
                st = static_ok(A, B, T)
                for x in range(A["n"]):
                    for w in wl:
                        a = run_traj(A, x, w)
                        b = run_traj(B, T[x], w)
                        check([T[s] for s in a] == b, "ORACLE_NAT1_TRAJ")
                        traj += 1
                        if st:
                            check(A["labels"][a[-1]] == B["labels"][b[-1]], "ORACLE_NAT1_OUT")
                            outp += 1
    cpairs = ctraj = 0
    for an, A in THREE:
        for bn, B in THREE:
            for cn, C in THREE:
                for T in maps(A["n"], B["n"]):
                    if ed[(an, bn, T)] != Z:
                        continue
                    for Um in maps(B["n"], C["n"]):
                        if ed[(bn, cn, Um)] != Z:
                            continue
                        UT = tuple(Um[T[x]] for x in range(A["n"]))
                        check(ed[(an, cn, UT)] == Z, "ORACLE_NAT1_COMP")
                        cpairs += 1
                        for x in range(A["n"]):
                            for w in wl:
                                a = run_traj(A, x, w)
                                c = run_traj(C, UT[x], w)
                                check([UT[s] for s in a] == c, "ORACLE_NAT1_COMP_TRAJ")
                                ctraj += 1
    return {
        "nat1_hom_sets": 9, "nat1_maps_per_hom_set": 27, "nat1_maps_total": len(ed), "nat1_composable_pairs": pairs,
        "nat1_subadditivity_strict_pairs": strict, "nat1_registered_weighted_bound_pairs": weighted,
        "nat1_registered_plain_triangle_violations_informational": plain_viol, "nat1_eps_zero_maps": zero_maps,
        "nat1_trajectory_checks_through_length_5": traj, "nat1_output_trajectory_checks": outp,
        "nat1_eps_zero_composable_pairs": cpairs, "nat1_composite_trajectory_checks_through_length_5": ctraj,
        "nat1_words_per_start": len(wl), "nat1_eps_values_discrete": sorted(vd), "nat1_eps_values_registered": sorted(vr),
    }


# ------------------------------------------------------------------ NAT-2


def census(hom: Sequence[Tuple[Dict[str, object], Dict[str, object]]], regime: str, level: Fraction) -> Dict[str, int]:
    c = {"total": 0, "static": 0, "lc": 0, "exact": 0, "full": 0, "eps_zero_any_label": 0, "inclusion_checks": 0}
    for A, B in hom:
        D = disc(B["n"]) if regime == "discrete" or B["n"] != 3 else path(B["n"])
        for T in maps(A["n"], B["n"]):
            t = tiers(A, B, T, D, level)
            c["total"] += 1
            c["static"] += int(t["static"])
            c["lc"] += int(t["lc"])
            c["exact"] += int(t["exact"])
            c["full"] += int(t["full"])
            c["eps_zero_any_label"] += int(t["eps"] == Z)
            check((not t["full"]) or t["exact"], "ORACLE_INC1")
            check((not t["exact"]) or t["lc"], "ORACLE_INC2")
            check((not t["lc"]) or t["static"], "ORACLE_INC3")
            c["inclusion_checks"] += 1
    c["exact_minus_full"] = c["exact"] - c["full"]
    c["lc_minus_exact"] = c["lc"] - c["exact"]
    c["static_minus_lc"] = c["static"] - c["lc"]
    return c


def nat2() -> Dict[str, object]:
    out = {}
    three = [(A, B) for _, A in THREE for _, B in THREE]
    two = [(M, Q)]
    for regime, level in (("discrete", LEVEL_DISC), ("registered", LEVEL_REG)):
        for fname, hom in (("three_state", three), ("two_state", two)):
            for k, v in census(hom, regime, level).items():
                out["nat2_" + regime + "_" + fname + "_" + k] = v
    out["nat2_witness_full_eps"] = tiers(M, N, ISO, path(3), LEVEL_REG)["eps"]
    check(tiers(M, N, ISO, path(3), LEVEL_REG)["full"], "ORACLE_W_FULL")
    tc = tiers(M, N, COLLAPSE, path(3), LEVEL_REG)
    check(tc["exact"] and not tc["full"], "ORACLE_W_EXACT")
    out["nat2_witness_exact_minus_full_eps"] = tc["eps"]
    tl = tiers(M, P, LC_MP, path(3), LEVEL_REG)
    check(tl["lc"] and not tl["exact"], "ORACLE_W_LC")
    out["nat2_witness_lc_minus_exact_eps"] = tl["eps"]
    ts = tiers(M, P, STATIC_MP, path(3), LEVEL_REG)
    check(ts["static"] and not ts["lc"], "ORACLE_W_STATIC")
    out["nat2_witness_static_minus_lc_eps"] = ts["eps"]
    return out


# ------------------------------------------------------------------ NAT-3


def nat3() -> Dict[str, object]:
    wl = all_words(HS["k"], L3)
    rows = mism = rows_with = disagree = weak = 0
    for x in range(HS["n"]):
        for w in wl:
            a = run_traj(HS, x, w)
            b = run_traj(VS, T3[x], w)
            vec = [0 if T3[a[i]] == b[i] else 1 for i in range(len(a))]
            rows += 1
            mism += sum(vec)
            rows_with += int(any(vec))
            if HS["labels"][a[-1]] != VS["labels"][b[-1]]:
                disagree += 1
                weak += 1
    hyst = None
    for x in range(HS["n"]):
        for a in range(HS["k"]):
            for b in range(HS["k"]):
                if a == b or hyst is not None:
                    continue
                s1 = run_traj(HS, x, [a, b])[-1]
                s2 = run_traj(HS, x, [b, a])[-1]
                if s1 != s2 and HS["labels"][s1] == HS["labels"][s2]:
                    hyst = (x, s1, s2)
    check(hyst is not None, "ORACLE_NO_HYST")
    return {
        "nat3_registered_words": len(wl), "nat3_tracker_rows": rows, "nat3_tracker_mismatches": mism,
        "nat3_tracker_rows_with_mismatch": rows_with, "nat3_final_output_disagreements": disagree,
        "nat3_final_output_only_check_mismatches": weak, "nat3_eps_discrete": eps_by_trajectories(HS, VS, T3, disc(3)),
        "nat3_hysteresis_start": HS["names"][hyst[0]], "nat3_hysteresis_state_1": HS["names"][hyst[1]],
        "nat3_hysteresis_state_2": HS["names"][hyst[2]], "nat3_hysteresis_label": HS["labels"][hyst[1]],
    }


# ------------------------------------------------------------------ NAT-4

COMPS = [(i, j, DEN - i - j) for i in range(DEN + 1) for j in range(DEN + 1 - i)]


def draw_kernel(rng: random.Random) -> List[List[List[Fraction]]]:
    out = [[None] * 3 for _ in range(2)]
    for y in range(3):
        for e in range(2):
            c = rng.choice(COMPS)
            out[e][y] = [Fraction(c[k], DEN) for k in range(3)]
    return out


def nat4() -> Dict[str, object]:
    tvs = {}
    for an, KA in STOCH:
        for bn, KB in STOCH:
            for T in maps(3, 3):
                tvs[(an, bn, T)] = tv_matrix(KA, KB, T)
    pairs = strict = 0
    for an, _ in STOCH:
        for bn, _ in STOCH:
            for cn, _ in STOCH:
                for T in maps(3, 3):
                    for Um in maps(3, 3):
                        UT = tuple(Um[T[x]] for x in range(3))
                        pairs += 1
                        s = tvs[(an, bn, T)] + tvs[(bn, cn, Um)]
                        check(tvs[(an, cn, UT)] <= s, "ORACLE_NAT4_SUBADD")
                        if tvs[(an, cn, UT)] < s:
                            strict += 1
    dchecks = dfail = 0
    for an, A in THREE:
        for bn, B in THREE:
            for T in maps(3, 3):
                dchecks += 1
                if tv_matrix(lift_matrix(A), lift_matrix(B), T) != eps_by_trajectories(A, B, T, disc(3)):
                    dfail += 1
    om = mode_of(OM_K, ["o0", "o1", "o2"], ["0", "1", "1"])
    on = mode_of(ON_K, ["r0", "r1", "r2"], ["0", "1", "1"])
    mode_eps = eps_by_trajectories(om, on, ISO, disc(3))
    exact_tv = tv_matrix(OM_K, ON_K, ISO)
    check(mode_eps == Z and exact_tv > Z, "ORACLE_OVERCLAIM")
    rng = random.Random(SEED)
    passing = resamples = 0
    tv_sum = Z
    tv_min = None
    for _ in range(DRAWS):
        K = draw_kernel(rng)
        while K == SN_K:
            resamples += 1
            K = draw_kernel(rng)
        t = tv_matrix(SM_K, K, ISO)
        tv_sum += t
        tv_min = t if tv_min is None else min(tv_min, t)
        passing += int(t == Z)
    return {
        "nat4_hom_sets": 9, "nat4_maps_total": len(tvs), "nat4_composable_pairs": pairs, "nat4_tv_subadditivity_strict_pairs": strict,
        "nat4_deterministic_specialization_checks": dchecks, "nat4_deterministic_specialization_failures": dfail,
        "nat4_distinct_tv_values": len(set(tvs.values())), "nat4_tv_values": sorted(set(tvs.values())),
        "nat4_overclaim_mode_eps": mode_eps, "nat4_overclaim_exact_tv": exact_tv, "nat4_fixture_iso_tv": tvs[("SM", "SN", ISO)],
        "null_draws": DRAWS, "null_passing": passing, "null_resample_events": resamples, "null_tv_sum": tv_sum, "null_tv_min": tv_min,
    }


def build() -> Dict[str, object]:
    shared = {}
    shared.update(nat1())
    shared.update(nat2())
    shared.update(nat3())
    shared.update(nat4())
    ok = shared["null_passing"] == 0 and shared["nat4_deterministic_specialization_failures"] == 0
    return {"schema": ORACLE_SCHEMA, "route": ROUTE, "shared_quantities": shared, "shared_quantity_count": len(shared), "verdict": "GREEN" if ok else "RED", "status": "GREEN" if ok else "RED"}


def main() -> None:
    r = build()
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "ORACLE_RESULT_V1.json"), "w") as fh:
        fh.write(json.dumps(ser(r), indent=1, sort_keys=True) + "\n")
    print(json.dumps({"schema": ORACLE_SCHEMA, "route": ROUTE, "status": r["status"], "shared_quantity_count": r["shared_quantity_count"]}, sort_keys=True))


if __name__ == "__main__":
    main()

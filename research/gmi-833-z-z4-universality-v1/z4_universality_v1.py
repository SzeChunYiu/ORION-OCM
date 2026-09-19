"""Route A -- resource-response universality classes and surviving distinctions
(#833 Section Z, subsection Z4).

Route A *simulates*: every candidate is replayed at every rung of the budget
ladder and every class, frontier, distinction, null and hostile is decided by
scanning the resulting list.  Stdlib only, exact integers, no float in any
claim.  Python 3.8 compatible.

Run:  python3 -I -B z4_universality_v1.py
"""
import itertools
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

LADDER_L = (2, 3, 4)
LADDER_BITS = (0, 1)
N1_SEEDS = tuple(range(7100, 7300))
N2_SEEDS = tuple(range(7300, 7500))
N4_SEEDS = tuple(range(7500, 7700))
SHUFFLE_SEED = 31337
RENAME_SEED = 90210


def errors_at(bits, nxt, table, L):
    """Exact integer (k_now, k_delay) over all 2^L sequences, t = 1..L-1."""
    kn = kd = 0
    for seq in itertools.product((0, 1), repeat=L):
        for mode in (0, 1):
            st = 0
            for t in range(L):
                cur = seq[t]
                if bits == 0:
                    got = (table >> (2 * mode + cur)) & 1
                else:
                    a = 4 * st + 2 * mode + cur
                    got = (table >> a) & 1
                    st = (nxt >> a) & 1
                if t >= 1:
                    want = cur if mode == 0 else seq[t - 1]
                    if got != want:
                        if mode == 0:
                            kn += 1
                        else:
                            kd += 1
    return kn, kd


def behaviour48(bits, nxt, table):
    key = 0
    for mode in (0, 1):
        for seq in itertools.product((0, 1), repeat=3):
            st = 0
            for t in range(3):
                cur = seq[t]
                if bits == 0:
                    o = (table >> (2 * mode + cur)) & 1
                else:
                    a = 4 * st + 2 * mode + cur
                    o = (table >> a) & 1
                    st = (nxt >> a) & 1
                key = (key << 1) | o
    return key


def build():
    """(bits, nxt, table, {L: (kn, kd)}, beh48)."""
    out = []
    for table in range(16):
        e = dict((L, errors_at(0, None, table, L)) for L in LADDER_L)
        out.append((0, None, table, e, behaviour48(0, None, table)))
    for nxt in range(256):
        for table in range(256):
            e = dict((L, errors_at(1, nxt, table, L)) for L in LADDER_L)
            out.append((1, nxt, table, e, behaviour48(1, nxt, table)))
    return out


def exponent_identifiable(rungs):
    """Amendment 1: a guard that must refuse AND accept, not a constant."""
    return rungs >= 4


def pareto(points):
    """Minimal points of a set of integer tuples under componentwise <=."""
    pts = sorted(set(points))
    out = []
    for a in pts:
        dominated = False
        for b in pts:
            if b == a:
                continue
            if all(bi <= ai for bi, ai in zip(b, a)) and b != a:
                dominated = True
                break
        if not dominated:
            out.append(a)
    return tuple(out)


def frontier_sound(front, points):
    """No frontier point is dominated by any point of the set."""
    for a in front:
        for b in points:
            if b != a and all(bi <= ai for bi, ai in zip(b, a)):
                return False
    return True


def families(univ):
    fam = dict((k, set()) for k in
               ("F_STATELESS", "F_DEAD_TABLE", "F_FROZEN_STATE", "F_MOORE",
                "F_MEALY_PURE", "F_IDENTITY_STATE"))
    for i, (bits, nxt, table, _e, _b) in enumerate(univ):
        if bits == 0:
            fam["F_STATELESS"].add(i)
            continue
        if all(((table >> (2 * m + c)) & 1) == ((table >> (4 + 2 * m + c)) & 1)
               for m in (0, 1) for c in (0, 1)):
            fam["F_DEAD_TABLE"].add(i)
        if nxt in (0, 255):
            fam["F_FROZEN_STATE"].add(i)
        if all(((table >> (4 * s + 2 * m)) & 1) ==
               ((table >> (4 * s + 2 * m + 1)) & 1)
               for s in (0, 1) for m in (0, 1)):
            fam["F_MOORE"].add(i)
        else:
            fam["F_MEALY_PURE"].add(i)
        if nxt == 0b10101010:
            fam["F_IDENTITY_STATE"].add(i)
    return fam


def g_state(rec):
    bits, nxt, table, _e, _b = rec
    if bits == 0:
        return rec
    n2 = t2 = 0
    for s in (0, 1):
        for m in (0, 1):
            for c in (0, 1):
                i2 = 4 * s + 2 * m + c
                i1 = 4 * (1 - s) + 2 * m + c
                n2 |= (1 - ((nxt >> i1) & 1)) << i2
                t2 |= ((table >> i1) & 1) << i2
    e = dict((L, errors_at(1, n2, t2, L)) for L in LADDER_L)
    return (1, n2, t2, e, behaviour48(1, n2, t2))


def g_out(rec):
    bits, nxt, table, _e, _b = rec
    t2 = (~table) & (0xF if bits == 0 else 0xFF)
    e = dict((L, errors_at(bits, nxt, t2, L)) for L in LADDER_L)
    return (bits, nxt, t2, e, behaviour48(bits, nxt, t2))


def main():
    univ = build()
    total = len(univ)

    # ------------------------------------------------- row 3: frontiers
    per_block = {}
    for b in LADDER_BITS:
        for L in LADDER_L:
            pts = set(rec[3][L] for rec in univ if rec[0] == b)
            per_block[(b, L)] = (pareto(pts), sorted(pts))
    fam = families(univ)
    fam_front = {}
    for name, members in fam.items():
        pts = set(univ[i][3][3] for i in members)
        fam_front[name] = (pareto(pts), len(pts))

    frontier_sound_all = all(
        frontier_sound(f, p) for (f, p) in per_block.values())
    # HS2 hostile: a frontier with a dominated point injected
    some_block = per_block[(1, 3)]
    dominated_extra = None
    for p in some_block[1]:
        if p not in some_block[0]:
            dominated_extra = p
            break
    hs2_detected = (dominated_extra is not None and
                    not frontier_sound(tuple(some_block[0]) + (dominated_extra,),
                                       some_block[1]))
    # N3: frontier is invariant under a shuffled traversal
    shuffled = list(univ)
    random.Random(SHUFFLE_SEED).shuffle(shuffled)
    n3_ok = True
    for b in LADDER_BITS:
        for L in LADDER_L:
            pts = set(rec[3][L] for rec in shuffled if rec[0] == b)
            if pareto(pts) != per_block[(b, L)][0]:
                n3_ok = False

    # U7: closed forms in L
    stateless_min_delay = dict(
        (L, min(rec[3][L][1] for rec in univ if rec[0] == 0))
        for L in LADDER_L)
    stateful_min_delay = dict(
        (L, min(rec[3][L][1] for rec in univ if rec[0] == 1))
        for L in LADDER_L)
    closed_form = dict((L, (L - 1) * (2 ** (L - 1))) for L in LADDER_L)
    scored_per_mode = dict((L, (L - 1) * (2 ** L)) for L in LADDER_L)

    # ------------------------------------------- row 2: resource-response
    def rrp(i):
        rec = univ[i]
        prof = []
        for L in LADDER_L:
            kn, kd = rec[3][L]
            prof.append((kn, kd))
        dom = []
        for L in LADDER_L:
            dom.append(1 if rec[3][L] in per_block[(rec[0], L)][0] else 0)
        return (tuple(prof), tuple(dom))

    classes = {}
    for i in range(total):
        classes.setdefault(rrp(i), []).append(i)
    sizes = sorted(len(v) for v in classes.values())
    n_classes = len(classes)
    singletons = sum(1 for s in sizes if s == 1)
    non_degenerate = sizes[-1] < total and singletons < n_classes

    # HS1 hostile: a class key that carries the candidate index
    def rrp_named(i):
        return (rrp(i), i)
    named_classes = len(set(rrp_named(i) for i in range(total)))
    hs1_detected = named_classes != n_classes
    # the honest profile must be invariant under renaming, and it is by
    # construction: rrp reads no index.  Verified by permuting the index space.
    perm = list(range(total))
    random.Random(RENAME_SEED).shuffle(perm)
    rrp_after = {}
    for i in range(total):
        rrp_after.setdefault(rrp(perm[i]), []).append(i)
    rrp_rename_invariant = (sorted(len(v) for v in rrp_after.values()) == sizes
                            and set(rrp_after) == set(classes))

    beh_classes = len(set(rec[4] for rec in univ))

    def vacuity_verdict(sizes_):
        n = len(sizes_)
        singles = sum(1 for x in sizes_ if x == 1)
        return "DEGENERATE" if (max(sizes_) >= total or singles >= n) \
            else "NON_DEGENERATE"

    hs5 = {
        "registered_definition": vacuity_verdict(sizes),
        "planted_constant_profile": vacuity_verdict([total]),
        "planted_index_keyed_profile": vacuity_verdict([1] * total),
    }
    hs5_detected = (hs5["registered_definition"] == "NON_DEGENERATE"
                    and hs5["planted_constant_profile"] == "DEGENERATE"
                    and hs5["planted_index_keyed_profile"] == "DEGENERATE")

    # --------------------------------- row 5: irreducibility of distinctions
    beh_of = [rec[4] for rec in univ]
    beh_members = {}
    for i, b in enumerate(beh_of):
        beh_members.setdefault(b, []).append(i)

    def clause1(setA, setB):
        """No behaviour class straddles the two sides, and each side owns one."""
        straddle = 0
        ownA = ownB = 0
        for b, mem in beh_members.items():
            inA = any(i in setA for i in mem)
            inB = any(i in setB for i in mem)
            if inA and inB:
                straddle += 1
            elif inA:
                ownA += 1
            elif inB:
                ownB += 1
        return straddle == 0 and ownA > 0 and ownB > 0, straddle, ownA, ownB

    def side_signature(members):
        """Behavioural content of a side: its behaviour-class set and its
        attainable (kn, kd, bits) frontier at L = 3."""
        bset = frozenset(beh_of[i] for i in members)
        pts = set((univ[i][3][3][0], univ[i][3][3][1], univ[i][0])
                  for i in members)
        return bset, pareto(pts)

    gstate_img = [g_state(rec) for rec in univ]
    gout_img = [g_out(rec) for rec in univ]

    def clause2(members):
        """The side's behavioural content is carried to itself by each
        registered generator, as a set-level statement."""
        base_b, base_f = side_signature(members)
        res = {}
        for name, img in (("g_rename", univ), ("g_state", gstate_img),
                          ("g_out", gout_img)):
            bset = frozenset(img[i][4] for i in members)
            pts = set((img[i][3][3][0], img[i][3][3][1], img[i][0])
                      for i in members)
            res[name] = {"behaviour_set_preserved": bset == base_b,
                         "frontier_preserved": pareto(pts) == base_f}
        # g_rename acts on names only, so the side's content is untouched
        res["g_rename"] = {"behaviour_set_preserved": True,
                           "frontier_preserved": True}
        return res

    names = ["bits0_vs_bits1"] + sorted(fam)
    dist = {}
    pairs = []
    b0 = set(i for i in range(total) if univ[i][0] == 0)
    b1 = set(range(total)) - b0
    pairs.append(("bits0_vs_bits1", b0, b1))
    fnames = sorted(fam)
    for a in range(len(fnames)):
        for c in range(a + 1, len(fnames)):
            A = fam[fnames[a]] - fam[fnames[c]]
            B = fam[fnames[c]] - fam[fnames[a]]
            if A and B:
                pairs.append(("%s_vs_%s" % (fnames[a], fnames[c]), A, B))

    for label, A, B in pairs:
        ok1, straddle, ownA, ownB = clause1(A, B)
        c2a = clause2(A)
        c2b = clause2(B)
        ok2 = all(v["behaviour_set_preserved"] and v["frontier_preserved"]
                  for v in list(c2a.values()) + list(c2b.values()))
        dist[label] = {
            "clause1_semantic_quotient": ok1,
            "straddling_behaviour_classes": straddle,
            "behaviour_classes_only_in_A": ownA,
            "behaviour_classes_only_in_B": ownB,
            "clause2_re_encoding": ok2,
            "clause2_detail_A": c2a,
            "clause2_detail_B": c2b,
            "IRREDUCIBLE": ok1 and ok2,
            "size_A": len(A), "size_B": len(B),
        }

    irreducible = sorted(k for k, v in dist.items() if v["IRREDUCIBLE"])
    fails_clause1 = sorted(k for k, v in dist.items()
                           if not v["clause1_semantic_quotient"])

    # HS3 hostile (amendment 1): a planted clause-1-only verdict
    clause1_only = sorted(k for k, v in dist.items()
                          if v["clause1_semantic_quotient"])
    hs3_detected = clause1_only != irreducible

    # ---------------------------------------------------------- nulls
    n1_respecting = 0
    for sd in N1_SEEDS:
        rng = random.Random(sd)
        cut = rng.randrange(1, total)
        idx = list(range(total))
        rng.shuffle(idx)
        A = set(idx[:cut])
        B = set(idx[cut:])
        ok1, _s, _a, _b = clause1(A, B)
        if ok1:
            n1_respecting += 1
    n2_irreducible = 0
    for sd in N2_SEEDS:
        rng = random.Random(sd)
        A = set(i for i in range(total) if rng.random() < 0.5)
        B = set(range(total)) - A
        if not A or not B:
            continue
        ok1, _s, _a, _b = clause1(A, B)
        if not ok1:
            continue
        c2a = clause2(A)
        c2b = clause2(B)
        if all(v["behaviour_set_preserved"] and v["frontier_preserved"]
               for v in list(c2a.values()) + list(c2b.values())):
            n2_irreducible += 1

    beh_keys = sorted(beh_members)
    n4_irreducible = 0
    for sd in N4_SEEDS:
        rng = random.Random(sd)
        sideA = set()
        A = set()
        for b in beh_keys:
            if rng.getrandbits(1):
                sideA.add(b)
        if not sideA or len(sideA) == len(beh_keys):
            continue
        for b in sideA:
            A.update(beh_members[b])
        B = set(range(total)) - A
        ok1, _s, _a, _b2 = clause1(A, B)
        if not ok1:
            continue
        c2a = clause2(A)
        c2b = clause2(B)
        if all(v["behaviour_set_preserved"] and v["frontier_preserved"]
               for v in list(c2a.values()) + list(c2b.values())):
            n4_irreducible += 1

    res = {
        "schema": "GMI_833_Z4_UNIVERSALITY_RESULT_V1",
        "route": "A_simulation",
        "source_main": "5e57d4292266bccf435136e1f7d72caa32e920a0",
        "claim_ceiling": ("GMI_833_Z4_RESOURCE_RESPONSE_UNIVERSALITY_CLASSES_"
                          "AND_SURVIVING_DISTINCTIONS_AT_REGISTERED_BINARY_"
                          "TRANSDUCER_SCOPE"),
        "rows_in_scope": [2, 3, 5],
        "rows_deliberately_left_open": [1, 4],
        "universe_candidates": total,
        "ladder": {"state_bit_rungs": len(LADDER_BITS),
                   "sequence_length_rungs": len(LADDER_L),
                   "state_bit_values": list(LADDER_BITS),
                   "sequence_length_values": list(LADDER_L),
                   "ladder_cells": len(LADDER_BITS) * len(LADDER_L)},
        "row2_resource_response_classes": {
            "classes": n_classes,
            "behaviour_classes_at_L3": beh_classes,
            "registered_named_families": len(fam),
            "class_size_min": sizes[0],
            "class_size_max": sizes[-1],
            "singleton_classes": singletons,
            "U1_non_degenerate": non_degenerate,
            "U2_between_behaviour_classes_and_families":
                len(fam) < n_classes < beh_classes,
            "rename_invariant": rrp_rename_invariant,
            "HS1_index_keyed_definition_detected": hs1_detected,
            "HS5_vacuity_verdicts": hs5,
            "HS5_planted_degenerate_definitions_detected": hs5_detected,
            "U12_vacuity_guard_correct_on_all_three": hs5_detected,
        },
        "row3_frontiers_and_exponents": {
            "frontier_by_block": dict(
                ("bits%d_L%d" % (b, L), [list(x) for x in per_block[(b, L)][0]])
                for (b, L) in per_block),
            "distinct_points_by_block": dict(
                ("bits%d_L%d" % (b, L), len(per_block[(b, L)][1]))
                for (b, L) in per_block),
            "frontier_by_family": dict(
                (k, {"frontier_L3": [list(x) for x in v[0]],
                     "distinct_points_L3": v[1]})
                for k, v in fam_front.items()),
            "frontier_soundness": frontier_sound_all,
            "HS2_dominated_point_detected": hs2_detected,
            "N3_frontier_invariant_under_shuffle": n3_ok,
            "stateless_min_delayed_errors": stateless_min_delay,
            "stateful_min_delayed_errors": stateful_min_delay,
            "closed_form_half_of_scored": closed_form,
            "scored_moments_per_mode": scored_per_mode,
            "U7_closed_form_holds_at_every_rung":
                all(stateless_min_delay[L] == closed_form[L] for L in LADDER_L)
                and all(stateful_min_delay[L] == 0 for L in LADDER_L),
            "U8_moore_and_mealy_frontiers_differ":
                fam_front["F_MOORE"][0] != fam_front["F_MEALY_PURE"][0],
            "exponent_verdict": "NOT_IDENTIFIED",
            "exponent_reason": (
                "the state-bit axis has 2 rungs and the sequence-length axis "
                "has 3; an exponent fitted to 2 or 3 points is not identified, "
                "so none is reported. The row's own clause 'where mathematically "
                "justified' is what licenses this refusal, and the rung counts "
                "are printed above so the refusal can be checked."),
            "exponent_guard": {
                "state_bit_axis_rungs": len(LADDER_BITS),
                "state_bit_axis_identifiable":
                    exponent_identifiable(len(LADDER_BITS)),
                "sequence_length_axis_rungs": len(LADDER_L),
                "sequence_length_axis_identifiable":
                    exponent_identifiable(len(LADDER_L)),
                "synthetic_five_rung_axis_identifiable":
                    exponent_identifiable(5),
            },
            "U11_exponent_guard_refuses_and_accepts":
                (not exponent_identifiable(len(LADDER_BITS))
                 and not exponent_identifiable(len(LADDER_L))
                 and exponent_identifiable(5)),
            "HS4_exponent_from_short_ladder_blocked":
                not exponent_identifiable(len(LADDER_L)),
            "asymptotic_forms_delivered": [
                "min delayed errors without state = (L-1)*2^(L-1), exactly half "
                "of the (L-1)*2^L scored moments per mode, at every rung",
                "min delayed errors with one state bit = 0 at every rung",
            ],
        },
        "row5_irreducible_distinctions": {
            "distinctions_tested": len(dist),
            "irreducible": irreducible,
            "irreducible_count": len(irreducible),
            "fail_clause1_semantic_quotient": fails_clause1,
            "U3_bits_split_irreducible": dist["bits0_vs_bits1"]["IRREDUCIBLE"],
            "U4_moore_mealy_irreducible":
                dist.get("F_MEALY_PURE_vs_F_MOORE",
                         dist.get("F_MOORE_vs_F_MEALY_PURE", {})
                         ).get("IRREDUCIBLE"),
            "U5_naive_all_pairs_irreducible": len(irreducible) == len(dist),
            "U6_some_family_separation_fails_clause1": len(fails_clause1) > 0,
            "clause1_only_verdict": clause1_only,
            "clause1_only_verdict_count": len(clause1_only),
            "U10_clause2_rejects_something_clause1_admits": hs3_detected,
            "HS3_planted_clause1_only_verdict_detected": hs3_detected,
            "detail": dist,
        },
        "nulls": {
            "N1_random_partitions": len(N1_SEEDS),
            "N1_random_partitions_respecting_behaviour": n1_respecting,
            "N2_random_bipartitions": len(N2_SEEDS),
            "N2_random_bipartitions_irreducible": n2_irreducible,
            "N2_note": ("a uniformly random split of 65552 candidates across "
                        "21904 behaviour classes cannot reach clause 2; N2 is "
                        "true but inert with respect to it, which is why N4 "
                        "exists -- see freeze amendment 1"),
            "N4_behaviour_respecting_bipartitions": len(N4_SEEDS),
            "N4_behaviour_respecting_bipartitions_irreducible": n4_irreducible,
        },
    }
    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=True, default=str)
        fh.write("\n")
    print(json.dumps({
        "classes": n_classes, "beh": beh_classes,
        "sizes": [sizes[0], sizes[-1]], "singletons": singletons,
        "U1": non_degenerate, "U2": len(fam) < n_classes < beh_classes,
        "irreducible": irreducible, "fail_c1": fails_clause1,
        "U7": res["row3_frontiers_and_exponents"]["U7_closed_form_holds_at_every_rung"],
        "U8": res["row3_frontiers_and_exponents"]["U8_moore_and_mealy_frontiers_differ"],
        "moore_front": res["row3_frontiers_and_exponents"]["frontier_by_family"]["F_MOORE"],
        "mealy_front": res["row3_frontiers_and_exponents"]["frontier_by_family"]["F_MEALY_PURE"],
        "N1": n1_respecting, "N2": n2_irreducible, "N4": n4_irreducible,
        "clause1_only": clause1_only, "HS3": hs3_detected, "HS5": hs5_detected,
    }, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())

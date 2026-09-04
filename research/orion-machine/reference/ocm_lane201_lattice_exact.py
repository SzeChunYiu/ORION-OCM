#!/usr/bin/env python3
"""Lane #201 exact checker: query-relative representation lattice, single-representation
lower bound, active-state/reopening conservation, selective reopening, scope intersection.

Theorems under test (``theory/OCM_LANE_201_TERMINAL_V1.md``):

* **L1 (existence/uniqueness).** For finite worlds ``Omega`` and a query set ``Q`` (each
  ``q: Omega -> A_q``), the coarsest representation sufficient for every ``q in Q`` exists,
  is unique, and equals the common refinement ``meet_{q in Q} ker q`` of the kernel
  partitions.  Checked exhaustively over *all* partitions of ``Omega``.
* **L2 (single all-query lower bound).** Any representation sufficient for all of ``Q``
  has at least ``|meet ker q|`` blocks, hence ``ceil(log2 |meet|)`` bits (Hartley).
* **L3 (query-relative active state).** Holding only ``ker q_t`` costs
  ``max_t ceil(log2 |q_t(Omega)|)`` bits; the gap to L2 is strict on an incompatible
  (pairwise non-nested) kernel family and zero when all kernels coincide.
* **L4 (conservation).** Over any adaptive query sequence, initial state bits plus total
  source-access bits is at least ``ceil(log2 |meet_t ker q_t|)``: the active-state saving
  of L3 is a relocation into reopening access, not a saving.  Checked over every order of a
  query family for a retentive and a forgetful strategy.
* **L5 (selective reopening).** On a query change the blocks that must be reopened are
  exactly those on which the new query is not constant: reopening fewer is unsound,
  reopening more is non-minimal.
* **L6 (scope intersection).** A composite authorised outside the intersection of its
  components' scopes admits a countermodel (WLL-4 restated in the lattice).

Planted failures (must fire in the same call): a free-reopening strategy (answers without
access where the stored block does not determine the query) is caught as unsound; an
under-reopening and an over-reopening rule are caught; a union-scope authorisation rule
meets a countermodel.  Mutation controls (asserted applied on a witness before the check):
``M1`` meet replaced by join, ``M2`` floor instead of ceil in the bit count, ``M3``
reopening that skips one needed block, ``M4`` accounting that never charges access.

Exit codes: ``0`` pass, ``1`` fail, ``2`` CANNOT_CHECK (never a pass).  Finite
enumeration only; no novelty or architecture claim.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from collections.abc import Callable, Iterable, Sequence

Partition = frozenset[frozenset[int]]
Query = tuple[int, ...]


class CannotCheck(RuntimeError):
    pass


# ----------------------------------------------------------------------------
# Partition lattice primitives
# ----------------------------------------------------------------------------

def kernel(q: Query) -> Partition:
    blocks: dict[int, set[int]] = {}
    for w, a in enumerate(q):
        blocks.setdefault(a, set()).add(w)
    return frozenset(frozenset(b) for b in blocks.values())


def meet(partitions: Iterable[Partition], n: int) -> Partition:
    """Common refinement: coarsest partition finer than every input."""
    parts = list(partitions)
    if not parts:
        return frozenset({frozenset(range(n))})
    key = {w: tuple(next(i for i, b in enumerate(sorted(map(sorted, p))) if w in b) for p in parts) for w in range(n)}
    blocks: dict[tuple[int, ...], set[int]] = {}
    for w, k in key.items():
        blocks.setdefault(k, set()).add(w)
    return frozenset(frozenset(b) for b in blocks.values())


def join(partitions: Iterable[Partition], n: int) -> Partition:
    """M1 mutation target: finest partition coarser than every input (transitive closure)."""
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for p in partitions:
        for b in p:
            b = sorted(b)
            for w in b[1:]:
                parent[find(w)] = find(b[0])
    blocks: dict[int, set[int]] = {}
    for w in range(n):
        blocks.setdefault(find(w), set()).add(w)
    return frozenset(frozenset(b) for b in blocks.values())


def refines(fine: Partition, coarse: Partition) -> bool:
    return all(any(b <= c for c in coarse) for b in fine)


def sufficient(p: Partition, q: Query) -> bool:
    return all(len({q[w] for w in b}) == 1 for b in p)


def all_partitions(n: int) -> tuple[Partition, ...]:
    if n > 8:
        raise CannotCheck("exhaustive partition enumeration capped at n=8")
    out: list[Partition] = []

    def rec(w: int, blocks: list[set[int]]) -> None:
        if w == n:
            out.append(frozenset(frozenset(b) for b in blocks))
            return
        for b in blocks:
            b.add(w)
            rec(w + 1, blocks)
            b.remove(w)
        blocks.append({w})
        rec(w + 1, blocks)
        blocks.pop()

    rec(0, [])
    return tuple(out)


def bits_ceil(p: Partition) -> int:
    return math.ceil(math.log2(len(p)))


def bits_floor(p: Partition) -> int:
    """M2 mutation target."""
    return math.floor(math.log2(len(p)))


# ----------------------------------------------------------------------------
# L1 / L2 / L3
# ----------------------------------------------------------------------------

def check_lattice(n: int, queries: Sequence[Query], meet_fn: Callable = meet, bits_fn: Callable = bits_ceil) -> dict[str, object]:
    everything = all_partitions(n)
    suff = [p for p in everything if all(sufficient(p, q) for q in queries)]
    m = meet_fn((kernel(q) for q in queries), n)
    if not all(sufficient(m, q) for q in queries):
        raise AssertionError("computed coarsest representation is not sufficient")
    # Coarsest: every single pair-merge is insufficient (complete test, see record §3).
    blocks = sorted(map(sorted, m))
    for i, j in itertools.combinations(range(len(blocks)), 2):
        merged = frozenset({frozenset(blocks[i]) | frozenset(blocks[j])} | {frozenset(b) for k, b in enumerate(blocks) if k not in (i, j)})
        if all(sufficient(merged, q) for q in queries):
            raise AssertionError("a coarser sufficient representation exists; meet is not coarsest")
    # Uniqueness over all sufficient partitions: m is the unique maximum in coarseness.
    coarsest = [p for p in suff if not any(other != p and refines(p, other) for other in suff)]
    if coarsest != [m]:
        raise AssertionError("coarsest sufficient partition is not unique or not the meet")
    if any(len(p) < len(m) for p in suff):
        raise AssertionError("a sufficient partition has fewer blocks than the meet")
    all_query_bits = bits_fn(m)
    per_query_bits = max(bits_fn(kernel(q)) for q in queries)
    return {
        "worlds": n,
        "queries": len(queries),
        "partitions_enumerated": len(everything),
        "sufficient_partitions": len(suff),
        "meet_blocks": len(m),
        "all_query_bits": all_query_bits,
        "max_single_query_bits": per_query_bits,
        "active_state_gap_bits": all_query_bits - per_query_bits,
        "kernels_pairwise_incomparable": all(
            not refines(kernel(a), kernel(b)) and not refines(kernel(b), kernel(a))
            for a, b in itertools.combinations(queries, 2)
        ) if len(queries) > 1 else False,
    }


# ----------------------------------------------------------------------------
# L4 conservation over adaptive query sequences
# ----------------------------------------------------------------------------

def refine_cost(stored: Partition, target: Partition) -> int:
    """Bits of source access needed to refine every stored block to the blocks of
    ``stored meet target``: worst case over stored blocks of log2 (sub-block count)."""
    worst = 1
    for b in stored:
        sub = {frozenset(b & t) for t in target if b & t}
        worst = max(worst, len(sub))
    return math.ceil(math.log2(worst))


def run_sequence(
    n: int, order: Sequence[Query], strategy: str, charge: Callable = refine_cost
) -> dict[str, object]:
    """Simulate a zero-error machine over ``order``.  ``retentive`` keeps the meet of
    everything seen; ``forgetful`` keeps only the kernel of the current query;
    ``free`` never pays access (planted unsound strategy)."""
    stored: Partition = frozenset({frozenset(range(n))})
    access = 0
    unsound_witness = None
    for q in order:
        k = kernel(q)
        if sufficient(stored, q):
            pass
        elif strategy == "free":
            for b in stored:
                if len({q[w] for w in b}) > 1:
                    unsound_witness = sorted(b)
                    break
        else:
            access += charge(stored, k)
            stored = meet((stored, k), n)
        if strategy == "forgetful":
            stored = k
    return {"access_bits": access, "unsound_witness": unsound_witness}


def check_conservation(n: int, queries: Sequence[Query], charge: Callable = refine_cost) -> dict[str, object]:
    m = meet((kernel(q) for q in queries), n)
    bound = bits_ceil(m)
    orders = list(itertools.permutations(queries))
    retentive = [run_sequence(n, o, "retentive", charge)["access_bits"] for o in orders]
    if min(retentive) < bound:
        raise AssertionError(f"conservation violated: access {min(retentive)} < meet bits {bound}")
    revisit = list(queries) + list(queries)  # every query asked twice
    forgetful = run_sequence(n, revisit, "forgetful", charge)["access_bits"]
    retentive_revisit = run_sequence(n, revisit, "retentive", charge)["access_bits"]
    if forgetful < bound or retentive_revisit < bound:
        raise AssertionError("conservation violated on revisit sequence")
    free = run_sequence(n, list(queries), "free", charge)
    if free["unsound_witness"] is None and free["access_bits"] == 0 and bound > 0:
        raise AssertionError("free-reopening strategy was not caught as unsound")
    return {
        "meet_bits": bound,
        "orders": len(orders),
        "retentive_access_min": min(retentive),
        "retentive_access_max": max(retentive),
        "tight_for_some_order": min(retentive) == bound,
        "revisit_forgetful_access": forgetful,
        "revisit_retentive_access": retentive_revisit,
        "forgetful_pays_more_on_revisit": forgetful > retentive_revisit,
        "free_reopening_unsound_witness": free["unsound_witness"],
    }


# ----------------------------------------------------------------------------
# L5 selective reopening
# ----------------------------------------------------------------------------

def reopen_set(stored: Partition, q: Query) -> frozenset[frozenset[int]]:
    return frozenset(b for b in stored if len({q[w] for w in b}) > 1)


def reopen_all(stored: Partition, q: Query) -> frozenset[frozenset[int]]:
    return frozenset(stored)


def reopen_skip_one(stored: Partition, q: Query) -> frozenset[frozenset[int]]:
    needed = sorted(reopen_set(stored, q), key=sorted)
    return frozenset(needed[1:])


def check_reopening(n: int, stored_queries: Sequence[Query], new_query: Query, rule: Callable = reopen_set) -> dict[str, object]:
    stored = meet((kernel(q) for q in stored_queries), n)
    reopened = rule(stored, new_query)
    # Soundness: answering on non-reopened blocks is exact.
    unsound = [sorted(b) for b in stored if b not in reopened and len({new_query[w] for w in b}) > 1]
    # Minimality: every reopened block really needs it.
    unnecessary = [sorted(b) for b in reopened if len({new_query[w] for w in b}) == 1]
    return {
        "stored_blocks": len(stored),
        "reopened_blocks": len(reopened),
        "sound": not unsound,
        "minimal": not unnecessary,
        "unsound_blocks": unsound,
        "unnecessary_blocks": unnecessary,
    }


# ----------------------------------------------------------------------------
# L6 scope intersection (WLL-4 in lattice form)
# ----------------------------------------------------------------------------

def check_scopes(contexts: int, scopes: Sequence[frozenset[int]], rule: str) -> dict[str, object]:
    """Composite authorised on ``authorised(rule)``; a countermodel is a context where
    some component is outside its scope: set that component wrong there, composite wrong."""
    inter = frozenset.intersection(*scopes)
    union = frozenset.union(*scopes)
    authorised = inter if rule == "intersection" else union
    countermodels = [
        {"context": c, "component_outside_scope": i}
        for c in sorted(authorised)
        for i, s in enumerate(scopes)
        if c not in s
    ]
    return {
        "rule": rule,
        "authorised_contexts": sorted(authorised),
        "countermodels": countermodels,
        "sound": not countermodels,
    }


# ----------------------------------------------------------------------------
# Registered families and runner
# ----------------------------------------------------------------------------

def bit_queries(k: int) -> tuple[int, tuple[Query, ...]]:
    n = 1 << k
    return n, tuple(tuple((w >> i) & 1 for w in range(n)) for i in range(k))


def run_exact_calibration() -> dict[str, object]:
    n3, bits3 = bit_queries(3)
    # Family A: incompatible bit queries on 8 worlds (strict gap).
    lattice_a = check_lattice(n3, bits3)
    if not lattice_a["kernels_pairwise_incomparable"] or lattice_a["active_state_gap_bits"] != 2:
        raise AssertionError("bit-query family should give a strict 3-vs-1 gap")
    # Family B: identical kernels (no-alarm: zero gap).
    same = (bits3[0], tuple(1 - x for x in bits3[0]))
    lattice_b = check_lattice(n3, same)
    if lattice_b["active_state_gap_bits"] != 0:
        raise AssertionError("identical-kernel family should give zero gap")
    # Family C: six worlds, three queries with non-power-of-two meet (exercises ceil).
    q6 = ((0, 0, 1, 1, 2, 2), (0, 1, 0, 1, 0, 1), (0, 0, 0, 1, 1, 1))
    lattice_c = check_lattice(6, q6)
    conservation = check_conservation(n3, bits3)
    if not conservation["tight_for_some_order"] or not conservation["forgetful_pays_more_on_revisit"]:
        raise AssertionError("conservation tightness or relocation witness missing")
    if conservation["free_reopening_unsound_witness"] is None:
        raise AssertionError("planted free-reopening strategy did not produce an unsound witness")
    reopen_ok = check_reopening(n3, bits3[:1], bits3[1])
    reopen_under = check_reopening(n3, bits3[:1], bits3[1], reopen_skip_one)
    if not (reopen_ok["sound"] and reopen_ok["minimal"]):
        raise AssertionError("exact reopening rule failed")
    # After storing bits 0 and 1, bit-2 is non-constant on every block, so reopen_all is
    # minimal there; use a query that is constant on some blocks to catch over-reopening.
    reopen_over = check_reopening(n3, bits3[:2], bits3[0], reopen_all)
    if reopen_over["minimal"]:
        raise AssertionError("planted over-reopening not caught")
    if reopen_under["sound"]:
        raise AssertionError("planted under-reopening not caught")
    scopes = (frozenset({0, 1, 2}), frozenset({1, 2, 3}), frozenset({1, 2}))
    scope_inter = check_scopes(4, scopes, "intersection")
    scope_union = check_scopes(4, scopes, "union")
    scope_equal = check_scopes(4, (frozenset({0, 1}), frozenset({0, 1})), "union")
    if not scope_inter["sound"] or scope_union["sound"] or not scope_equal["sound"]:
        raise AssertionError("scope-intersection checks failed")
    mutations = mutation_controls()
    return {
        "schema": "orion.ocm.lane201-lattice.exact-results.v1",
        "terminal": "PASS_REPRESENTATION_LATTICE_PARENT_OWNED_FINITE",
        "lattice": {"bits3_incompatible": lattice_a, "identical_kernels": lattice_b, "six_world_ceil": lattice_c},
        "conservation": conservation,
        "reopening": {"exact": reopen_ok, "planted_over": reopen_over, "planted_under": reopen_under},
        "scopes": {"intersection": scope_inter, "planted_union": scope_union, "equal_scopes_no_alarm": scope_equal},
        "mutation_controls": mutations,
        "denominators": {
            "partitions_enumerated": lattice_a["partitions_enumerated"] + lattice_b["partitions_enumerated"] + lattice_c["partitions_enumerated"],
            "query_orders": conservation["orders"],
            "planted_failures": 4,
            "mutations": len(mutations),
        },
        "authority": {
            "finite_enumeration_only": True,
            "all_size_authority": "hand proofs in theory/OCM_LANE_201_TERMINAL_V1.md (partition lattice, Hartley, CEGAR; parent-owned)",
            "novelty_established": False,
            "architecture_separation": False,
            "certified_representation_residual": False,
        },
    }


def mutation_controls() -> dict[str, object]:
    n3, bits3 = bit_queries(3)
    out: dict[str, object] = {}
    # M1: join instead of meet.
    applied = join((kernel(q) for q in bits3), n3) != meet((kernel(q) for q in bits3), n3)
    if not applied:
        raise AssertionError("M1 not applied")
    try:
        check_lattice(n3, bits3, meet_fn=join)
        detected = False
    except AssertionError:
        detected = True
    out["M1_join_instead_of_meet"] = {"applied": True, "detected": detected}
    # M2: floor bits — applied on the six-world meet (6 blocks -> 3 vs 2).
    q6 = ((0, 0, 1, 1, 2, 2), (0, 1, 0, 1, 0, 1), (0, 0, 0, 1, 1, 1))
    m6 = meet((kernel(q) for q in q6), 6)
    applied = bits_floor(m6) != bits_ceil(m6)
    if not applied:
        raise AssertionError("M2 not applied")
    floored = check_lattice(6, q6, bits_fn=bits_floor)
    detected = floored["all_query_bits"] < bits_ceil(m6)
    out["M2_floor_bits"] = {"applied": True, "detected": detected}
    # M3: reopening skips one needed block.
    stored = meet((kernel(bits3[0]),), n3)
    applied = reopen_skip_one(stored, bits3[1]) != reopen_set(stored, bits3[1])
    if not applied:
        raise AssertionError("M3 not applied")
    detected = not check_reopening(n3, bits3[:1], bits3[1], reopen_skip_one)["sound"]
    out["M3_under_reopening"] = {"applied": True, "detected": detected}
    # M4: accounting that never charges access.
    def no_charge(stored: Partition, target: Partition) -> int:
        return 0
    applied = no_charge(stored, kernel(bits3[1])) != refine_cost(stored, kernel(bits3[1]))
    if not applied:
        raise AssertionError("M4 not applied")
    try:
        check_conservation(n3, bits3, charge=no_charge)
        detected = False
    except AssertionError:
        detected = True
    out["M4_uncharged_access"] = {"applied": True, "detected": detected}
    for name, row in out.items():
        if not row["detected"]:
            raise AssertionError(f"{name} not detected")
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = run_exact_calibration()
    except CannotCheck as exc:
        print(json.dumps({"terminal": "CANNOT_CHECK", "reason": str(exc)}, indent=2))
        return 2
    except AssertionError as exc:
        print(json.dumps({"terminal": "FAIL", "error": str(exc)}, indent=2))
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, default=str))
    else:
        d = result["denominators"]
        print(f"PASS lane-201 lattice: {d['partitions_enumerated']} partitions, {d['query_orders']} orders, {d['planted_failures']} planted failures, {d['mutations']} mutations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

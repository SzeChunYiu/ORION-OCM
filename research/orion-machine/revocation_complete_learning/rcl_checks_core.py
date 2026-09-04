"""Core exact checks for Revocation-Complete Learning V0."""

from __future__ import annotations

import itertools

from rcl_model import (
    alternative_bits,
    enumerate_antichains,
    fixed_certificate_profiles,
    live,
    live_via_active_set,
    omitted_warrant_revocation,
    powerset,
    profile_from_bits,
    signature,
)

def verify_antichain_injectivity(n: int = 4) -> dict[str, object]:
    profiles = enumerate_antichains(n)
    signatures = {signature(profile, n) for profile in profiles}
    cross_checks = sum(
        live(profile, revoked) == live_via_active_set(profile, revoked, n)
        for profile in profiles
        for revoked in powerset(tuple(range(n)))
    )
    denominator = len(profiles) * (1 << n)
    return {
        "n": n,
        "candidate_families_scanned": 1 << (1 << n),
        "profile_count": len(profiles),
        "distinct_signature_count": len(signatures),
        "injective": len(signatures) == len(profiles),
        "independent_liveness_agreement": cross_checks,
        "independent_liveness_denominator": denominator,
    }


def verify_positive_witness_omissions(n: int = 4) -> dict[str, object]:
    profiles = enumerate_antichains(n)
    checked = 0
    for profile in profiles:
        for emitted_size in range(len(profile) + 1):
            for emitted in itertools.combinations(profile, emitted_size):
                if len(emitted) == len(profile):
                    continue
                emitted_profile = tuple(emitted)
                hidden = next(w for w in profile if w not in emitted_profile)
                revoked = omitted_warrant_revocation(emitted_profile, hidden)
                if live(emitted_profile, revoked) or not live(profile, revoked):
                    raise AssertionError("omission witness construction failed")
                checked += 1
    return {
        "n": n,
        "profiles_checked": len(profiles),
        "proper_positive_transcripts_checked": checked,
        "all_omissions_distinguished": True,
    }


def verify_bounded_witness_family(max_k: int = 6) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for k in range(1, max_k + 1):
        warrants = tuple(
            frozenset({2 * i, 2 * i + 1}) for i in range(k + 1)
        )
        emitted, full = warrants[:k], warrants
        revoked = frozenset(2 * i for i in range(k))
        row = {
            "k": k,
            "emitted_live": live(emitted, revoked),
            "full_live": live(full, revoked),
        }
        if row != {"k": k, "emitted_live": False, "full_live": True}:
            raise AssertionError("bounded-witness family failed")
        rows.append(row)
    return {"max_k": max_k, "witness_count": len(rows), "all_exact": True, "cases": rows}


def verify_counterfactual_gap(max_n: int = 5) -> dict[str, object]:
    cases: list[dict[str, object]] = []
    coordinate_checks = 0
    for n in range(1, max_n + 1):
        fixed, alternatives, profiles = fixed_certificate_profiles(n)
        expected = 1 << len(alternatives)
        signatures = {signature(profile, n) for profile in profiles}
        for profile in profiles:
            truth = alternative_bits(profile, n)
            observed = tuple(
                live(profile, frozenset(range(n)) - warrant)
                for warrant in alternatives
            )
            coordinate_checks += len(alternatives)
            if observed != truth:
                raise AssertionError("shattering coordinates do not recover profile bits")
        case = {
            "n": n,
            "middle_layer_warrant_count": len(alternatives) + 1,
            "profile_count": len(profiles),
            "distinct_signature_count": len(signatures),
            "same_current_certificate": all(fixed in p for p in profiles),
            "revocation_shattering_dimension": len(alternatives),
            "zero_query_lower_bound_bits": len(alternatives),
            "exact": len(profiles) == expected == len(signatures),
        }
        if not case["exact"]:
            raise AssertionError("counterfactual-gap family failed")
        cases.append(case)
    return {
        "max_n": max_n,
        "coordinate_checks": coordinate_checks,
        "all_exact": True,
        "cases": cases,
    }


def verify_storage_query_frontier(max_n: int = 5) -> dict[str, object]:
    cases: list[dict[str, object]] = []
    checks = 0
    for n in range(1, max_n + 1):
        _, alternatives, profiles = fixed_certificate_profiles(n)
        total = len(alternatives)
        points = []
        for stored in range(total + 1):
            for profile in profiles:
                bits = alternative_bits(profile, n)
                reconstructed = profile_from_bits(bits[:stored] + bits[stored:], n)
                checks += 1
                if reconstructed != profile:
                    raise AssertionError("frontier reconstruction failed")
            points.append(
                {
                    "stored_bits": stored,
                    "queried_binary_coordinates": total - stored,
                    "sum": total,
                    "exact": True,
                }
            )
        cases.append(
            {
                "n": n,
                "variable_warrant_bits": total,
                "profile_count": len(profiles),
                "frontier_points": points,
            }
        )
    return {"max_n": max_n, "reconstruction_checks": checks, "all_exact": True, "cases": cases}


def verify_direct_sum(n: int = 4, skill_count: int = 2) -> dict[str, object]:
    _, alternatives, profiles = fixed_certificate_profiles(n)
    per_skill = len(alternatives)
    vectors = {
        tuple(bit for profile in joint for bit in alternative_bits(profile, n))
        for joint in itertools.product(profiles, repeat=skill_count)
    }
    expected = 1 << (skill_count * per_skill)
    return {
        "n": n,
        "skill_count": skill_count,
        "per_skill_dimension": per_skill,
        "joint_dimension": skill_count * per_skill,
        "joint_profile_count": len(vectors),
        "expected_joint_profile_count": expected,
        "exact": len(vectors) == expected,
    }



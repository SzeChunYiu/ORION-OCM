#!/usr/bin/env python3
"""Finite warrant-profile model for Revocation-Complete Learning V0."""

from __future__ import annotations

import itertools
import math
from functools import lru_cache
from collections.abc import Iterable, Iterator, Sequence
from typing import Final

Atom = int
Warrant = frozenset[Atom]
Profile = tuple[Warrant, ...]
MAX_EXHAUSTIVE_N: Final[int] = 4


def powerset(items: Sequence[Atom]) -> Iterator[Warrant]:
    for size in range(len(items) + 1):
        for choice in itertools.combinations(items, size):
            yield frozenset(choice)


def _key(warrant: Warrant) -> tuple[int, tuple[int, ...]]:
    return len(warrant), tuple(sorted(warrant))


def canonical_profile(warrants: Iterable[Iterable[Atom]]) -> Profile:
    unique = {frozenset(warrant) for warrant in warrants}
    minimal = {
        warrant
        for warrant in unique
        if not any(other < warrant for other in unique)
    }
    return tuple(sorted(minimal, key=_key))


def is_antichain(profile: Profile) -> bool:
    return len(profile) == len(set(profile)) and all(
        not (left < right or right < left)
        for i, left in enumerate(profile)
        for right in profile[i + 1 :]
    )


def live(profile: Profile, revoked: Iterable[Atom]) -> bool:
    revoked_set = frozenset(revoked)
    return any(warrant.isdisjoint(revoked_set) for warrant in profile)


def live_via_active_set(profile: Profile, revoked: Iterable[Atom], n: int) -> bool:
    """Independent formulation used to cross-check ``live``."""
    active = frozenset(range(n)) - frozenset(revoked)
    return any(warrant <= active for warrant in profile)


def signature(profile: Profile, n: int) -> tuple[bool, ...]:
    atoms = tuple(range(n))
    return tuple(live(profile, revoked) for revoked in powerset(atoms))


@lru_cache(maxsize=None)
def enumerate_antichains(n: int) -> tuple[Profile, ...]:
    if n < 0:
        raise ValueError("n must be non-negative")
    if n > MAX_EXHAUSTIVE_N:
        raise ValueError("exhaustive enumeration is capped at n=4")
    subsets = list(powerset(tuple(range(n))))
    profiles: list[Profile] = []
    for mask in range(1 << len(subsets)):
        family = tuple(
            subsets[i] for i in range(len(subsets)) if mask & (1 << i)
        )
        if is_antichain(family):
            profiles.append(tuple(sorted(family, key=_key)))
    return tuple(profiles)


def first_difference(a: Profile, b: Profile, n: int) -> Warrant | None:
    for revoked in powerset(tuple(range(n))):
        if live(a, revoked) != live(b, revoked):
            return revoked
    return None


def omitted_warrant_revocation(emitted: Profile, hidden: Warrant) -> Warrant:
    revoked: set[Atom] = set()
    for witness in emitted:
        outside = witness - hidden
        if not outside:
            raise ValueError("warrants must be distinct members of an antichain")
        revoked.add(min(outside))
    return frozenset(revoked)


@lru_cache(maxsize=None)
def middle_layer(n: int) -> Profile:
    if n < 1:
        raise ValueError("n must be positive")
    d = n // 2
    return tuple(frozenset(x) for x in itertools.combinations(range(n), d))


@lru_cache(maxsize=None)
def fixed_certificate_profiles(n: int) -> tuple[Warrant, Profile, tuple[Profile, ...]]:
    layer = middle_layer(n)
    fixed, alternatives = layer[0], layer[1:]
    profiles = [
        canonical_profile(
            [fixed]
            + [
                alternatives[i]
                for i in range(len(alternatives))
                if mask & (1 << i)
            ]
        )
        for mask in range(1 << len(alternatives))
    ]
    return fixed, alternatives, tuple(profiles)


def alternative_bits(profile: Profile, n: int) -> tuple[bool, ...]:
    fixed, alternatives, _ = fixed_certificate_profiles(n)
    if fixed not in profile:
        raise ValueError("profile lacks the fixed current certificate")
    present = set(profile)
    return tuple(warrant in present for warrant in alternatives)


def profile_from_bits(bits: Sequence[bool], n: int) -> Profile:
    fixed, alternatives, _ = fixed_certificate_profiles(n)
    if len(bits) != len(alternatives):
        raise ValueError("wrong bit-vector length")
    return canonical_profile(
        [fixed]
        + [w for w, present in zip(alternatives, bits, strict=True) if present]
    )


def combinatorial_rank(support: Warrant, n: int, d: int) -> int:
    if len(support) != d:
        raise ValueError("support has wrong size")
    ordered = tuple(sorted(support))
    for rank, candidate in enumerate(itertools.combinations(range(n), d)):
        if candidate == ordered:
            return rank
    raise ValueError("support contains an out-of-range atom")


def combinatorial_unrank(rank: int, n: int, d: int) -> Warrant:
    choices = list(itertools.combinations(range(n), d))
    if rank < 0 or rank >= len(choices):
        raise ValueError("rank out of range")
    return frozenset(choices[rank])



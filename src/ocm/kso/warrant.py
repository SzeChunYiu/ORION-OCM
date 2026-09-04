"""Warrant algebra — antichain profiles, the idempotent semiring, and three-valued liveness.

Consolidates ``research/orion-machine/reference/kso_math_v1.py`` (profile algebra, KS-T01) and
``theory/OCM_OPERATIONAL_SEMANTICS_V1.md`` (the ``complete`` flag that makes absence of a surviving
warrant ``UNKNOWN`` rather than false) into one canonical implementation.

Parents (see ``docs/parent-subtraction/KSO_CORE_PARENTS_V1.md``): ATMS labels (de Kleer 1986),
provenance semirings (Green, Karvounarakis & Tannen 2007), Kleene strong three-valued logic (1938).
Nothing here is claimed as novel; the semiring proof (KS-T01) is a monotone-Boolean-function argument.

Exit-code discipline for every checker in this package: 0 holds, 1 fails, 2 ``CANNOT_CHECK``.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass
from enum import Enum
from typing import Any, Hashable, Iterable, Sequence

Warrant = frozenset  # frozenset[EvidenceId]
Profile = tuple      # tuple[Warrant, ...], canonical antichain


class CannotCheck(RuntimeError):
    """Distinct from failure: the check could not be performed."""


def _ekey(x: Hashable) -> tuple[str, str]:
    return (type(x).__name__, repr(x))


def _wkey(w: Warrant) -> tuple[int, tuple[tuple[str, str], ...]]:
    return (len(w), tuple(sorted(_ekey(e) for e in w)))


def canon(items: Iterable[Iterable[Hashable]]) -> Profile:
    """Canonical antichain: drop duplicates and non-minimal sets; deterministic order."""
    unique = {frozenset(item) for item in items}
    minimal = [w for w in unique if not any(v < w for v in unique)]
    return tuple(sorted(minimal, key=_wkey))


ZERO: Profile = ()               # no sufficient warrant at all (additive zero)
ONE: Profile = (frozenset(),)    # unconditionally warranted (multiplicative unit)


def join(left: Profile, right: Profile) -> Profile:
    """P ⊕ Q — alternative support: either profile suffices."""
    return canon((*left, *right))


def meet(left: Profile, right: Profile) -> Profile:
    """P ⊗ Q — conjunctive support: one warrant from each must survive."""
    if not left or not right:
        return ZERO
    return canon(a | b for a in left for b in right)


def meet_all(profiles: Iterable[Profile]) -> Profile:
    out = ONE
    for p in profiles:
        out = meet(out, p)
    return out


def is_antichain(profile: Sequence[Iterable[Hashable]]) -> bool:
    ws = [frozenset(w) for w in profile]
    return len(set(ws)) == len(ws) and not any(a < b for a in ws for b in ws)


def live(profile: Profile, revoked: Iterable[Hashable]) -> bool:
    """Two-valued ℓ_R(P): some exhibited warrant survives revocation R."""
    rv = frozenset(revoked)
    return any(not (w & rv) for w in profile)


class Liveness(str, Enum):
    LIVE = "LIVE"
    DEAD = "DEAD"
    UNKNOWN = "UNKNOWN"


def kleene_and(a: Liveness, b: Liveness) -> Liveness:
    if a is Liveness.DEAD or b is Liveness.DEAD:
        return Liveness.DEAD
    if a is Liveness.UNKNOWN or b is Liveness.UNKNOWN:
        return Liveness.UNKNOWN
    return Liveness.LIVE


def kleene_or(a: Liveness, b: Liveness) -> Liveness:
    if a is Liveness.LIVE or b is Liveness.LIVE:
        return Liveness.LIVE
    if a is Liveness.UNKNOWN or b is Liveness.UNKNOWN:
        return Liveness.UNKNOWN
    return Liveness.DEAD


def leq(lower: Profile, upper: Profile) -> bool:
    """Semiring order P ≤ Q  ⇔  f_P ≤ f_Q  ⇔  every warrant of P contains a warrant of Q."""
    return all(any(w2 <= w1 for w2 in upper) for w1 in lower)


@dataclass(frozen=True, slots=True)
class WarrantProfile:
    """An interval of antichain profiles: ``lower`` = exhibited sufficient warrants, ``upper`` =
    every warrant that could possibly suffice.  ``lower ≤ upper`` in the semiring order.

    * certified (complete) profile: ``lower == upper``;
    * partial profile: ``upper == ONE`` (anything might still warrant it);
    * certified-unwarranted: ``lower == upper == ZERO`` — FEEDBACK atoms by construction (KS-T18).

    Liveness under revocation R is three-valued: LIVE iff some exhibited warrant survives; DEAD iff
    no possible warrant survives; UNKNOWN otherwise.  Theorem KS-T21: this map is an exact
    homomorphism from (⊕, ⊗) on intervals to Kleene strong three-valued (∨, ∧).
    Parents: rough-set lower/upper approximation (Pawlak 1982); Kleene 1938; Belnap 1977.
    """

    lower: Profile
    upper: Profile

    def __post_init__(self) -> None:
        lo, up = canon(self.lower), canon(self.upper)
        if not leq(lo, up):
            raise ValueError("warrant interval violates lower ≤ upper")
        object.__setattr__(self, "lower", lo)
        object.__setattr__(self, "upper", up)

    # constructors -------------------------------------------------------------------------
    @staticmethod
    def certified(profile: Iterable[Iterable[Hashable]]) -> "WarrantProfile":
        p = canon(profile)
        return WarrantProfile(p, p)

    @staticmethod
    def partial(profile: Iterable[Iterable[Hashable]]) -> "WarrantProfile":
        return WarrantProfile(canon(profile), ONE)

    @staticmethod
    def zero() -> "WarrantProfile":
        return WarrantProfile(ZERO, ZERO)

    @staticmethod
    def one() -> "WarrantProfile":
        return WarrantProfile(ONE, ONE)

    @staticmethod
    def of(*warrants: Iterable[Hashable], complete: bool = True) -> "WarrantProfile":
        p = tuple(frozenset(w) for w in warrants)
        return WarrantProfile.certified(p) if complete else WarrantProfile.partial(p)

    # views ---------------------------------------------------------------------------------
    @property
    def profile(self) -> Profile:
        return self.lower

    @property
    def complete(self) -> bool:
        return self.lower == self.upper

    @property
    def is_zero(self) -> bool:
        return self.lower == ZERO

    @property
    def evidence(self) -> frozenset:
        return frozenset(e for w in self.lower for e in w)

    def liveness(self, revoked: Iterable[Hashable]) -> Liveness:
        rv = frozenset(revoked)
        if live(self.lower, rv):
            return Liveness.LIVE
        if not live(self.upper, rv):
            return Liveness.DEAD
        return Liveness.UNKNOWN

    def is_live(self, revoked: Iterable[Hashable]) -> bool:
        return self.liveness(revoked) is Liveness.LIVE

    def join(self, other: "WarrantProfile") -> "WarrantProfile":
        return WarrantProfile(join(self.lower, other.lower), join(self.upper, other.upper))

    def meet(self, other: "WarrantProfile") -> "WarrantProfile":
        return WarrantProfile(meet(self.lower, other.lower), meet(self.upper, other.upper))

    def as_dict(self) -> dict[str, Any]:
        return {
            "lower": [sorted(map(repr, w)) for w in self.lower],
            "upper": [sorted(map(repr, w)) for w in self.upper],
            "complete": self.complete,
        }


def meet_all_profiles(profiles: Iterable[WarrantProfile]) -> WarrantProfile:
    out = WarrantProfile.one()
    for p in profiles:
        out = out.meet(p)
    return out


# ------------------------------------------------------------------------------------------------
# exhaustive finite calibration
# ------------------------------------------------------------------------------------------------


def powerset(items: Sequence[Hashable]) -> list[frozenset]:
    out: list[frozenset] = []
    for r in range(len(items) + 1):
        out.extend(frozenset(c) for c in itertools.combinations(items, r))
    return out


def all_profiles(n: int) -> list[Profile]:
    """Every antichain over n evidence atoms (Dedekind numbers: 2, 3, 6, 20, 168, ...)."""
    subsets = powerset(tuple(range(n)))
    profiles: set[Profile] = set()
    for mask in range(1 << len(subsets)):
        selected = [subsets[i] for i in range(len(subsets)) if mask & (1 << i)]
        profiles.add(canon(selected))
    return sorted(profiles, key=lambda p: (len(p), tuple(_wkey(w) for w in p)))


def check_semiring(n: int = 3) -> dict[str, int]:
    """KS-T01: (antichains, ⊕, ⊗, 0, 1) is a commutative idempotent semiring — exhaustive at n."""
    ps = all_profiles(n)
    pair_checks = triple_checks = 0
    for a in ps:
        assert join(a, ZERO) == a and meet(a, ONE) == a and meet(a, ZERO) == ZERO
        assert join(a, a) == a
        for b in ps:
            pair_checks += 1
            assert join(a, b) == join(b, a)
            assert meet(a, b) == meet(b, a)
            assert is_antichain(join(a, b)) and is_antichain(meet(a, b))
            for c in ps:
                triple_checks += 1
                assert join(join(a, b), c) == join(a, join(b, c))
                assert meet(meet(a, b), c) == meet(a, meet(b, c))
                assert meet(a, join(b, c)) == join(meet(a, b), meet(a, c))
    return {"evidence_atoms": n, "profiles": len(ps), "pair_checks": pair_checks, "triple_checks": triple_checks}


def check_three_valued_reduction(n: int = 3) -> dict[str, int]:
    """KS-T21 (three-valued liveness on warrant intervals).

    (a) Reduction: for a certified profile (lower == upper) liveness is LIVE iff the two-valued
        ℓ_R holds and is never UNKNOWN.
    (b) Homomorphism: for all intervals P, Q and every revocation R,
        liveness(P ⊗ Q, R) = kleene_and(liveness(P,R), liveness(Q,R)) and
        liveness(P ⊕ Q, R) = kleene_or(liveness(P,R), liveness(Q,R)).
    (c) Refinement monotonicity: narrowing an interval (certifying) can only move UNKNOWN to LIVE
        or DEAD, never flip LIVE and DEAD.
    Exhaustive over every valid interval (lower ≤ upper) of antichains at n and all 2^n revocations.
    """
    ps = all_profiles(n)
    revocations = powerset(tuple(range(n)))
    intervals = [WarrantProfile(lo, up) for lo in ps for up in ps if leq(lo, up)]
    reduction = homomorphism = monotone = 0
    for a in ps:
        wa = WarrantProfile(a, a)
        for r in revocations:
            assert wa.liveness(r) is not Liveness.UNKNOWN
            assert (wa.liveness(r) is Liveness.LIVE) == live(a, r)
            reduction += 1
    for p in intervals:
        for q in intervals:
            if leq(p.lower, q.lower) and leq(q.upper, p.upper):  # q refines p
                for r in revocations:
                    lp, lq = p.liveness(r), q.liveness(r)
                    assert lp is lq or lp is Liveness.UNKNOWN, (p, q, r)
                    monotone += 1
    for p in intervals:
        for q in intervals:
            for r in revocations:
                lp, lq = p.liveness(r), q.liveness(r)
                assert p.meet(q).liveness(r) is kleene_and(lp, lq), (p, q, r)
                assert p.join(q).liveness(r) is kleene_or(lp, lq), (p, q, r)
                homomorphism += 1
    return {
        "intervals": len(intervals),
        "reduction_checks": reduction,
        "homomorphism_checks": homomorphism,
        "refinement_monotone_checks": monotone,
    }


# planted mutants (each must be caught by tests/m1/test_mutants.py)


def mutant_meet_as_union(left: Profile, right: Profile) -> Profile:
    """Wrong: alternative support where conjunction is required."""
    return join(left, right)


def mutant_unknown_as_live(profile: WarrantProfile, revoked: Iterable[Hashable]) -> Liveness:
    """Wrong: treats an uncertified absence of warrant as LIVE."""
    if live(profile.lower, revoked):
        return Liveness.LIVE
    return Liveness.DEAD if profile.complete else Liveness.LIVE


def mutant_unknown_as_dead(profile: WarrantProfile, revoked: Iterable[Hashable]) -> Liveness:
    """Wrong: collapses UNKNOWN into DEAD (absence of exhibited warrant read as falsity)."""
    return Liveness.LIVE if live(profile.lower, revoked) else Liveness.DEAD

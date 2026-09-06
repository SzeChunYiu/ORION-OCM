"""Nogoods — registered inconsistent assumption sets inside the warrant interval algebra (MEG-16).

An ATMS nogood is a set of assumptions that cannot hold together (de Kleer 1986).  In the KSO a
CONSTRAINT hyperedge between two claims, or an EXACT_CHECKER refutation, registers a nogood
``N ⊆ E``.  A warrant that contains a nogood is not a warrant at all.

Definitions.  For a nogood family 𝒩 ⊆ 2^E and a profile P:

    filter_𝒩(P) = Min{ W ∈ P : ∀N ∈ 𝒩, N ⊄ W }

applied to both bounds of an interval.  Liveness under (R, 𝒩) is liveness of the filtered
interval under R.

Theorems (checked exhaustively at n = 3 with every single nogood and every pair):
  MEG-16(i)   filter commutes with ⊕:   filter(P ⊕ Q) = filter(P) ⊕ filter(Q).
  MEG-16(ii)  filter is *not* a ⊗-homomorphism: filter(P ⊗ Q) ≤ filter(P) ⊗ filter(Q) in the
              semiring order (strict on a two-assumption witness) — so the filter must be applied
              AFTER composition; applying it before (the planted mutant) can leave a composite
              LIVE on a nogood.
  MEG-16(iii) liveness under (R, 𝒩) is an exact Kleene homomorphism for ⊕ and a
              *sub*-homomorphism for ⊗: λ(filter(P⊗Q)) ≤ λ(P) ∧₃ λ(Q) in the order
              DEAD < UNKNOWN < LIVE (a composite of two individually LIVE parts may be DEAD when
              their joint warrant is a nogood — that is the point).  Filtering never revives:
              it never moves DEAD → LIVE.
  MEG-16(iv)  two claims joined by a violated CONSTRAINT cannot both be tails of an ENABLED edge:
              the constraint registers the nogood of their joint warrants, so any composite over
              both is filtered out (KS-T02 with the nogood acting as a revoked pseudo-evidence).

No "Both" truth value is introduced (Belnap only if inconsistency must be *stored*); the
contradiction is stored as the nogood record itself, which is append-only history.
Parent: ATMS nogoods (de Kleer 1986, verified in KSO_CORE_PARENTS_V1).  Nothing new.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Any, Hashable, Iterable

from .warrant import ONE, ZERO, Liveness, Profile, WarrantProfile, all_profiles, canon, join, kleene_and, kleene_or, leq, live, meet, powerset


@dataclass(frozen=True)
class NogoodSet:
    """A registered family of inconsistent assumption sets (append-only history of contradictions)."""

    nogoods: tuple[frozenset, ...] = ()

    @staticmethod
    def of(*sets: Iterable[Hashable]) -> "NogoodSet":
        return NogoodSet(canon(sets))  # minimal nogoods suffice: a superset of a nogood is a nogood

    def violated_by(self, warrant: frozenset) -> bool:
        return any(n <= warrant for n in self.nogoods)

    def filter(self, profile: Profile) -> Profile:
        return canon(w for w in profile if not self.violated_by(w))

    def filter_interval(self, wp: WarrantProfile) -> WarrantProfile:
        return WarrantProfile(self.filter(wp.lower), self.filter(wp.upper))

    def liveness(self, wp: WarrantProfile, revoked: Iterable[Hashable]) -> Liveness:
        return self.filter_interval(wp).liveness(revoked)

    def add(self, nogood: Iterable[Hashable]) -> "NogoodSet":
        return NogoodSet(canon((*self.nogoods, frozenset(nogood))))

    def as_dict(self) -> dict[str, Any]:
        return {"nogoods": [sorted(map(repr, n)) for n in self.nogoods]}


EMPTY = NogoodSet()


def register_constraint_nogood(left: WarrantProfile, right: WarrantProfile) -> NogoodSet:
    """A violated CONSTRAINT between two claims: every joint warrant (one from each lower profile)
    is a nogood — the two cannot be warranted together."""
    return NogoodSet.of(*(a | b for a in left.lower for b in right.lower)) if left.lower and right.lower else EMPTY


def mutant_filter_before_compose(nogoods: NogoodSet, p: Profile, q: Profile) -> Profile:
    """Planted: filter the factors, then compose — lets a composite survive on a nogood."""
    return meet(nogoods.filter(p), nogoods.filter(q))


def check_nogoods(n: int = 3) -> dict[str, Any]:
    ps = all_profiles(n)
    universe = tuple(range(n))
    families = [NogoodSet.of(N) for N in powerset(universe) if len(N) >= 1] + [NogoodSet.of(a, b) for a, b in itertools.combinations([s for s in powerset(universe) if 1 <= len(s) <= 2], 2)]
    revs = powerset(universe)
    comm_join = ineq_meet = strict = hom = refine = 0
    for ng in families:
        for p in ps:
            for q in ps:
                assert ng.filter(join(p, q)) == join(ng.filter(p), ng.filter(q))
                comm_join += 1
                after = ng.filter(meet(p, q))
                before = mutant_filter_before_compose(ng, p, q)
                # filtered composite is at least as hard to satisfy as the mutant's composite
                assert leq(after, before), (ng, p, q)
                ineq_meet += 1
                if after != before:
                    strict += 1
                wp, wq = WarrantProfile(p, p), WarrantProfile(q, q)
                for r in revs:
                    lp, lq = ng.liveness(wp, r), ng.liveness(wq, r)
                    order = {Liveness.DEAD: 0, Liveness.UNKNOWN: 1, Liveness.LIVE: 2}
                    assert order[ng.liveness(wp.meet(wq), r)] <= order[kleene_and(lp, lq)]
                    assert ng.liveness(wp.join(wq), r) is kleene_or(lp, lq)
                    hom += 1
        for p in ps:
            wp = WarrantProfile(p, p)
            f = ng.filter_interval(wp)
            assert leq(f.lower, wp.lower)  # filtering only removes warrants: harder to satisfy
            for r in revs:
                a, b = wp.liveness(r), f.liveness(r)
                assert not (a is Liveness.DEAD and b is Liveness.LIVE)  # filtering never revives
                refine += 1
    # strictness witness for (ii): P = {{0}}, Q = {{1}}, nogood {0,1}
    ng = NogoodSet.of({0, 1})
    p, q = (frozenset({0}),), (frozenset({1}),)
    assert ng.filter(meet(p, q)) == ZERO and mutant_filter_before_compose(ng, p, q) == (frozenset({0, 1}),)
    assert live(mutant_filter_before_compose(ng, p, q), ()) and not live(ng.filter(meet(p, q)), ())
    # (iv): a violated constraint's nogood kills the composite over both claims
    left, right = WarrantProfile.of({0}), WarrantProfile.of({1})
    cn = register_constraint_nogood(left, right)
    assert cn.liveness(left.meet(right), ()) is Liveness.DEAD and cn.liveness(left, ()) is Liveness.LIVE and cn.liveness(right, ()) is Liveness.LIVE
    # no-alarm: empty nogood set changes nothing
    for p in ps:
        assert EMPTY.filter(p) == p
    return {"evidence_atoms": n, "families": len(families), "join_commutation_checks": comm_join, "meet_inequality_checks": ineq_meet, "meet_strict_cases": strict, "kleene_checks": hom, "refinement_checks": refine, "strict_witness": 1, "constraint_nogood_kills_composite": 1, "empty_family_no_alarm": len(ps)}

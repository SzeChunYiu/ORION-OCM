"""Regression controls for the registered quotient contract, not new science.

The same partition must reach the navigation and warrant checks, including
one-shot outer/inner iterables. These tests use the production KSO algebra.
"""
from fractions import Fraction
from itertools import product

import pytest

from ocm.kso.abstraction import QuotientVerdict, is_lumpable, lump, quotient_admissible
from ocm.kso.space import Atom, KnowledgeSpace
from ocm.kso.warrant import WarrantProfile, all_profiles, leq, powerset


def _partition(shape, blocks):
    rows = tuple(iter(block) if shape in ("inner", "both") else block for block in blocks)
    return iter(rows) if shape in ("outer", "both") else rows


def _matrix(lumpable):
    rows = ((1, 0, 0), (0, 1, 0), (0, 0, 1)) if lumpable else (
        (1, 0, 0), (0, 0, 1), (0, 0, 1)
    )
    return tuple(tuple(Fraction(x) for x in row) for row in rows)


@pytest.mark.parametrize("shape", ("tuple", "outer", "inner", "both"))
@pytest.mark.parametrize("revocation_iterator", (False, True))
@pytest.mark.parametrize("lumpable,measurable,expected", (
    (True, True, QuotientVerdict.ADMISSIBLE),
    (True, False, QuotientVerdict.NOT_WARRANT_MEASURABLE),
    (False, True, QuotientVerdict.NOT_LUMPABLE),
    (False, False, QuotientVerdict.NEITHER),
))
def test_partition_shape_preserves_both_checks(shape, revocation_iterator, lumpable, measurable, expected):
    left = WarrantProfile.of({"a"})
    right = left if measurable else WarrantProfile.of({"b"})
    ks = KnowledgeSpace((Atom("a", "claim", left), Atom("b", "claim", right), Atom("c", "claim")), ())
    revocations = (frozenset(), frozenset({"a"}))
    if revocation_iterator:
        revocations = iter(revocations)
    result = quotient_admissible(ks, _matrix(lumpable), _partition(shape, (("a", "b"), ("c",))), revocations)
    assert result is expected


@pytest.mark.parametrize("shape", ("outer", "inner", "both"))
@pytest.mark.parametrize("other", (WarrantProfile.zero(), WarrantProfile.one()))
def test_unknown_remains_distinct_when_revocation_family_is_empty(shape, other):
    ks = KnowledgeSpace((Atom("a", "claim", WarrantProfile.partial(())), Atom("b", "claim", other)), ())
    identity = ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(1)))
    assert quotient_admissible(ks, identity, _partition(shape, (("a", "b"),)), iter(())) is QuotientVerdict.NOT_WARRANT_MEASURABLE


@pytest.mark.parametrize("shape", ("tuple", "outer", "inner", "both"))
@pytest.mark.parametrize("blocks", ((("a",),), (("a", "a"), ("b",)), (("a",), ("missing",))))
def test_incomplete_duplicate_or_unknown_partition_stays_invalid(shape, blocks):
    ks = KnowledgeSpace((Atom("a", "claim"), Atom("b", "claim")), ())
    identity = ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(1)))
    with pytest.raises(ValueError):
        quotient_admissible(ks, identity, _partition(shape, blocks), ())


@pytest.mark.parametrize("check", (is_lumpable, lump))
def test_empty_partition_blocks_are_rejected_at_the_boundary(check):
    identity = ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(1)))
    with pytest.raises(ValueError, match="partition"):
        check(identity, ((), (0, 1)))


def test_empty_state_has_an_empty_partition():
    assert quotient_admissible(KnowledgeSpace((), ()), (), iter(()), ()) is QuotientVerdict.ADMISSIBLE
    assert lump((), ()) == []


def test_id_translation_does_not_repeatedly_scan_all_ids():
    class NoLinearIndex(tuple):
        def index(self, *args, **kwargs):
            raise AssertionError("partition translation must index IDs once, not scan for each atom")

    ks = KnowledgeSpace((Atom("a", "claim"), Atom("b", "claim")), ())
    # Operation-count sentinel only; no mocked navigation or warrant decisions.
    ks.__dict__["ids"] = NoLinearIndex(ks.ids)
    identity = ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(1)))
    assert quotient_admissible(ks, identity, (("a",), ("b",)), ()) is QuotientVerdict.ADMISSIBLE


def test_exhaustive_two_evidence_intervals_preserve_liveness_distinctions():
    profiles = all_profiles(2)
    intervals = tuple(WarrantProfile(lo, hi) for lo, hi in product(profiles, repeat=2) if leq(lo, hi))
    identity = ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(1)))
    checks = 0
    for left, right in product(intervals, repeat=2):
        ks = KnowledgeSpace((Atom("a", "claim", left), Atom("b", "claim", right)), ())
        for revoked in powerset((0, 1)):
            # Independent expected verdict from the defining liveness condition.
            expected = (QuotientVerdict.ADMISSIBLE if left.liveness(revoked) is right.liveness(revoked)
                        else QuotientVerdict.NOT_WARRANT_MEASURABLE)
            for shape in ("tuple", "outer", "inner", "both"):
                assert quotient_admissible(ks, identity, _partition(shape, (("a", "b"),)), iter((revoked,))) is expected
                checks += 1
    assert checks == len(intervals) ** 2 * 4 * 4

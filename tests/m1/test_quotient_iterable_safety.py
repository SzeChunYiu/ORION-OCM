"""Regression controls for the same-partition requirement in quotient admission.

These are ordinary developer tests, not protected evidence or quantum advantage.
The fixture is lumpable but loses a required evidence distinction after revocation.
"""
from fractions import Fraction

import pytest

from ocm.kso.abstraction import QuotientVerdict, quotient_admissible, warrant_measurable
from ocm.kso.space import Atom, KnowledgeSpace
from ocm.kso.warrant import WarrantProfile


def field(*, same_support=False, partial=False):
    wa = WarrantProfile.of({"left"}, complete=not partial)
    wb = wa if same_support else WarrantProfile.of({"right"})
    return KnowledgeSpace((Atom("a", "claim", wa), Atom("b", "claim", wb), Atom("c", "claim")), ())


def matrix():
    h = Fraction(1, 2)
    z, one = Fraction(0), Fraction(1)
    return ((h, h, z), (h, h, z), (z, z, one))


@pytest.mark.parametrize("form", ["tuple", "outer", "inner", "both"])
@pytest.mark.parametrize("partial", [False, True])
def test_partition_iterators_cannot_skip_warrant_check(form, partial):
    blocks = (("a", "b"), ("c",))
    if form in {"inner", "both"}:
        blocks = tuple(iter(block) for block in blocks)
    if form in {"outer", "both"}:
        blocks = iter(blocks)
    assert quotient_admissible(field(partial=partial), matrix(), blocks, iter((frozenset({"left"}),))) is QuotientVerdict.NOT_WARRANT_MEASURABLE


@pytest.mark.parametrize("form", ["tuple", "outer", "inner", "both"])
def test_valid_quotient_remains_admissible(form):
    blocks = (("a", "b"), ("c",))
    if form in {"inner", "both"}:
        blocks = tuple(iter(block) for block in blocks)
    if form in {"outer", "both"}:
        blocks = iter(blocks)
    assert quotient_admissible(field(same_support=True), matrix(), blocks, (frozenset({"left"}),)) is QuotientVerdict.ADMISSIBLE


def test_one_shot_partition_is_consumed_once():
    class Once:
        def __init__(self, values):
            self.values = values
            self.used = False
        def __iter__(self):
            if self.used:
                raise AssertionError("partition iterated twice")
            self.used = True
            return iter(self.values)
    blocks = Once((Once(("a", "b")), Once(("c",))))
    assert quotient_admissible(field(), matrix(), blocks, (frozenset({"left"}),)) is QuotientVerdict.NOT_WARRANT_MEASURABLE


def test_nested_revocation_iterator_is_snapshotted():
    # Supported input is Iterable[frozenset]; freezing each scenario also safely
    # handles a one-shot iterable without consuming different evidence per atom.
    assert warrant_measurable(field(same_support=True), (("a", "b"),), (iter(("left",)),))


def test_empty_revocation_collection_still_checks_present_liveness():
    ks = KnowledgeSpace((Atom("a", "claim", WarrantProfile.zero()), Atom("b", "claim")), ())
    p = ((Fraction(1, 2), Fraction(1, 2)),) * 2
    assert quotient_admissible(ks, p, iter((("a", "b"),)), iter(())) is QuotientVerdict.NOT_WARRANT_MEASURABLE


def test_unknown_atom_still_rejected_as_value_error():
    with pytest.raises(ValueError):
        quotient_admissible(field(), matrix(), iter((("a", "missing"), ("c",))), ())


@pytest.mark.parametrize("blocks", [(("a", "a"), ("b", "c")), (("a",), ("c",))])
def test_invalid_partition_is_not_admitted(blocks):
    with pytest.raises(ValueError):
        quotient_admissible(field(), matrix(), iter(blocks), ())


def test_nonlumpability_and_warrant_failure_both_survive_generators():
    z, one = Fraction(0), Fraction(1)
    p = ((one, z, z), (z, z, one), (z, z, one))
    assert quotient_admissible(field(), p, iter((("a", "b"), ("c",))), (frozenset({"left"}),)) is QuotientVerdict.NEITHER


def test_small_measurability_check_does_not_copy_whole_atom_map(monkeypatch):
    ks = field(same_support=True)
    def no_copy(_self):
        raise AssertionError("whole-field atom_map copy")
    monkeypatch.setattr(KnowledgeSpace, "atom_map", no_copy)
    assert warrant_measurable(ks, (("a", "b"),), (frozenset({"left"}),))

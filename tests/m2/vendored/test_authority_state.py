"""Ported from ORION tests/unit/kernel/test_authority_state.py (commit adb97ec).

Vocabulary adapted to ``ocm.store.registry`` (``AuthorityObjectKind`` →
``RegistryObjectKind``, ``AuthorityRegistration`` → ``Registration``, no
``public_key_hex``) and ``ocm.store.dependency_history`` (support sets and the
DNF ``evaluate_support`` are gone; the single-conjunction verdict is
``status_verdict`` / ``DependencyHistoryState.verdict``). The source test for
the evaluator/key public-key rule is replaced by the rule's absence: a
registration of any kind carries no key. Assertions are otherwise the source's.
"""

from dataclasses import replace

import pytest

from ocm.store.dependency_history import (
    DependencyHistoryState,
    DependencyStatus,
    DependencyStatusEvent,
    SupportVerdict,
    append_dependency_status,
    status_verdict,
    statuses_at,
)
from ocm.store.registry import (
    Registration,
    RegistryObjectKind,
    RegistryObjectStatus,
    RegistryState,
    RegistryStatusEvent,
    append_registry_status,
)


def _registration(kind=RegistryObjectKind.CHECKER, registration_id="checker:v1"):
    return Registration(
        registration_id=registration_id,
        kind=kind,
        artifact_hash="a" * 64,
        epoch_id="epoch:1",
        metadata_hash="b" * 64,
    )


def _event(registration_id="checker:v1", status=RegistryObjectStatus.LIVE, observed_at=1, event_id="event:1"):
    return RegistryStatusEvent(event_id, registration_id, status, observed_at, "status observation")


def test_registration_commitment_binds_kind_artifact_epoch_and_metadata():
    base = _registration()
    assert base.commitment != replace(base, artifact_hash="d" * 64).commitment
    assert base.commitment != replace(base, epoch_id="epoch:2").commitment
    assert base.commitment != replace(base, kind=RegistryObjectKind.OPERATOR).commitment
    assert base.commitment != replace(base, metadata_hash="e" * 64).commitment


def test_every_registry_kind_is_admissible_and_none_carries_a_key():
    for kind in RegistryObjectKind:
        registration = Registration("r", kind, "a" * 64, "epoch", "b" * 64)
        assert not hasattr(registration, "public_key_hex")
    with pytest.raises(ValueError):
        Registration("r", RegistryObjectKind.EVIDENCE, "not-a-digest", "epoch", "b" * 64)
    with pytest.raises(ValueError):
        Registration(" ", RegistryObjectKind.EVIDENCE, "a" * 64, "epoch", "b" * 64)


def test_registry_revision_changes_append_only_with_status_history_and_logical_time():
    registration = _registration()
    state = RegistryState((registration,), (_event(),), 1)
    later_history = append_registry_status(
        state.status_history,
        _event(status=RegistryObjectStatus.REVOKED, observed_at=2, event_id="event:2"),
    )
    later = RegistryState((registration,), later_history, 2)
    assert state.revision != later.revision
    assert state.current_status(registration.registration_id) is RegistryObjectStatus.LIVE
    assert later.current_status(registration.registration_id) is RegistryObjectStatus.REVOKED
    assert later.live_registration(registration.registration_id) is None


def test_status_at_explicit_logical_time_does_not_read_future_event():
    registration = _registration()
    state = RegistryState(
        (registration,),
        (
            _event(),
            _event(status=RegistryObjectStatus.REVOKED, observed_at=10, event_id="event:10"),
        ),
        5,
    )
    assert state.current_status(registration.registration_id) is RegistryObjectStatus.LIVE


def test_unknown_registration_status_is_unknown_and_never_live():
    registration = _registration()
    state = RegistryState((registration,), (), 0)
    assert state.current_status(registration.registration_id) is RegistryObjectStatus.UNKNOWN
    assert state.live_registration(registration.registration_id) is None
    assert state.registration("missing") is None


def test_live_registration_of_the_wrong_kind_is_none():
    registration = _registration()
    state = RegistryState((registration,), (_event(),), 1)
    assert state.live_registration(registration.registration_id) is registration
    assert state.live_registration(registration.registration_id, kind=RegistryObjectKind.CHECKER) is registration
    assert state.live_registration(registration.registration_id, kind=RegistryObjectKind.LEARNER) is None


def test_status_history_cannot_reference_unknown_registration_or_rewind():
    registration = _registration()
    with pytest.raises(ValueError):
        RegistryState((registration,), (_event(registration_id="missing"),), 1)
    history = (_event(observed_at=5),)
    with pytest.raises(ValueError):
        append_registry_status(history, _event(observed_at=4, event_id="older"))
    with pytest.raises(ValueError):
        append_registry_status(history, _event(observed_at=6, event_id="event:1"))


def test_dependency_history_revision_and_verdict_are_separate_from_registry_revision():
    history = (
        DependencyStatusEvent("a", "dep:a", DependencyStatus.REVOKED, 1, "revoked"),
        DependencyStatusEvent("b", "dep:b", DependencyStatus.LIVE, 1, "live"),
        DependencyStatusEvent("c", "dep:c", DependencyStatus.LIVE, 1, "live"),
    )
    state = DependencyHistoryState(history, 1)
    assert state.verdict(("dep:a", "dep:b")) is SupportVerdict.FAIL
    assert state.verdict(("dep:c",)) is SupportVerdict.PASS
    changed = DependencyHistoryState(
        append_dependency_status(
            history, DependencyStatusEvent("c2", "dep:c", DependencyStatus.REVOKED, 2, "revoked")
        ),
        2,
    )
    assert state.revision != changed.revision
    assert changed.verdict(("dep:c",)) is SupportVerdict.FAIL
    # The registry revision is a different domain: same logical time, no collision.
    assert state.revision != RegistryState((), (), 1).revision


def test_unknown_or_stale_dependency_yields_cannot_check_not_fail():
    state = DependencyHistoryState((), 0)
    assert state.verdict(("missing",)) is SupportVerdict.CANNOT_CHECK
    assert state.status_of("missing") is DependencyStatus.UNKNOWN
    assert status_verdict([DependencyStatus.LIVE, DependencyStatus.STALE]) is SupportVerdict.CANNOT_CHECK
    assert status_verdict([DependencyStatus.STALE, DependencyStatus.REVOKED]) is SupportVerdict.FAIL
    assert status_verdict([]) is SupportVerdict.CANNOT_CHECK
    assert state.verdict(()) is SupportVerdict.CANNOT_CHECK


def test_dependency_statuses_resolve_at_logical_time_and_never_read_the_future():
    history = (
        DependencyStatusEvent("1", "dep:a", DependencyStatus.LIVE, 1, "live"),
        DependencyStatusEvent("2", "dep:a", DependencyStatus.REVOKED, 10, "revoked"),
    )
    assert statuses_at(history, 5) == {"dep:a": DependencyStatus.LIVE}
    assert statuses_at(history, 10) == {"dep:a": DependencyStatus.REVOKED}
    assert statuses_at(history, 0) == {}
    with pytest.raises(ValueError):
        append_dependency_status(history, DependencyStatusEvent("3", "dep:a", DependencyStatus.LIVE, 9, "older"))
    with pytest.raises(ValueError):
        append_dependency_status(history, DependencyStatusEvent("1", "dep:b", DependencyStatus.LIVE, 9, "dup"))


def test_registry_state_requires_unique_registration_and_event_ids():
    registration = _registration()
    with pytest.raises(ValueError):
        RegistryState((registration, registration), (), 0)
    with pytest.raises(ValueError):
        RegistryState((registration,), (_event(), _event()), 1)

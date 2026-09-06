"""Byte-guard optimization and public validation boundaries."""
from contextlib import contextmanager
from pathlib import Path

import pytest

import ocm.store.ledger as L


def decodes(monkeypatch):
    seen = []
    original = L._decode

    def record(line, number):
        seen.append(number)
        return original(line, number)

    monkeypatch.setattr(L, "_decode", record)
    return seen


def test_unchanged_verified_bytes_do_not_decode_old_rows(tmp_path, monkeypatch):
    store = L.LedgerStore(tmp_path)
    first = store.append("EVENT", {"value": 1})
    seen = decodes(monkeypatch)
    second = store.append("EVENT", {"value": 2}, expected_head=first.entry_hash)
    assert seen == []
    assert second.sequence == 1
    assert store.entries() == (first, second)
    assert seen == [1, 2]


def test_public_and_identified_reads_still_validate_every_row(tmp_path, monkeypatch):
    store = L.LedgerStore(tmp_path)
    store.append("EVENT", {"value": 1})
    seen = decodes(monkeypatch)
    store.entries()
    assert seen == [1]
    seen.clear()
    old = store.append_identified("EVENT", {"value": 2}, transaction_id="tx")
    assert seen == [1]
    seen.clear()
    assert store.append_identified("EVENT", {"value": 2}, transaction_id="tx") == old
    assert seen == [1, 2]


def test_one_captured_read_under_lock_for_hit_and_miss(tmp_path, monkeypatch):
    store = L.LedgerStore(tmp_path)
    original_read = Path.read_bytes
    original_lock = store._exclusive_lock
    locked = False
    reads = []

    @contextmanager
    def tracked_lock():
        nonlocal locked
        with original_lock():
            locked = True
            try:
                yield
            finally:
                locked = False

    def read(path):
        if path == store.path:
            assert locked
            reads.append(path)
        return original_read(path)

    def no_second_path_read():
        raise AssertionError("append must validate its captured bytes")

    monkeypatch.setattr(store, "_raw_lines", no_second_path_read)
    monkeypatch.setattr(store, "_exclusive_lock", tracked_lock)
    monkeypatch.setattr(Path, "read_bytes", read)
    store.append("EVENT", {"value": 1})
    assert len(reads) == 1
    store.append("EVENT", {"value": 2})
    assert len(reads) == 2


def test_payload_aliases_cannot_change_validated_head(tmp_path):
    store = L.LedgerStore(tmp_path)
    payload = {"nested": {"value": [1]}}
    first = store.append("EVENT", payload)
    payload["nested"]["value"].append(2)
    first.payload["nested"]["value"].append(3)
    read_back = store.entries()[0]
    read_back.payload["nested"]["value"].append(4)
    store.append("EVENT", {"value": 5}, expected_head=first.entry_hash)
    assert store.entries()[0].payload == {"nested": {"value": [1]}}
    assert store.verify() == ()


@pytest.mark.parametrize("failure", ["file", "replace", "directory"])
def test_failed_persistence_does_not_publish_new_cache(tmp_path, monkeypatch, failure):
    store = L.LedgerStore(tmp_path)
    store.append("EVENT", {"value": 1})
    old_cache = store._validated_snapshot
    old_bytes = store.path.read_bytes()
    seen = decodes(monkeypatch)

    def fail(*args):
        raise OSError("injected persistence failure")

    with monkeypatch.context() as patch:
        if failure == "file":
            patch.setattr(L.os, "fsync", fail)
        elif failure == "replace":
            patch.setattr(L.os, "replace", fail)
        else:
            patch.setattr(store, "_fsync_directory", fail)
        with pytest.raises(OSError, match="injected persistence failure"):
            store.append("EVENT", {"value": 2})
    assert store._validated_snapshot is old_cache
    after = store.path.read_bytes()
    assert (after == old_bytes) is (failure != "directory")
    seen.clear()
    final = store.append("EVENT", {"value": 3})
    assert final.sequence == (1 if failure != "directory" else 2)
    assert len(seen) == (0 if failure != "directory" else 2)
    assert store.verify() == ()
    assert not tuple(tmp_path.glob(".ledger.jsonl.*.tmp"))

def test_optional_snapshot_allocation_failure_preserves_success(tmp_path, monkeypatch):
    store = L.LedgerStore(tmp_path)
    first = store.append("EVENT", {"value": 1})
    original_read = Path.read_bytes

    class AllocationFails(bytes):
        def __add__(self, other):
            raise MemoryError("injected optional snapshot allocation")

    def read(path):
        data = original_read(path)
        return AllocationFails(data) if path == store.path else data

    with monkeypatch.context() as patch:
        patch.setattr(Path, "read_bytes", read)
        second = store.append("EVENT", {"value": 2}, expected_head=first.entry_hash)
    assert store._validated_snapshot is None
    assert store.entries() == (first, second)
    seen = decodes(monkeypatch)
    third = store.append("EVENT", {"value": 3}, expected_head=second.entry_hash)
    assert seen == [1, 2]
    assert third.sequence == 2
    assert store.verify() == ()

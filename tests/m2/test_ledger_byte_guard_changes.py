"""Changed-file and parser compatibility for exact-byte guarded append."""
import os
from pathlib import Path

import pytest

import ocm.store.ledger as L


def test_same_size_historical_change_is_rejected_with_warm_cache(tmp_path):
    store = L.LedgerStore(tmp_path)
    store.append("EVENT", {"value": 1})
    store.append("EVENT", {"value": 2})
    original = store.path.read_bytes()
    changed = original.replace(b'"value":1', b'"value":9', 1)
    assert changed != original and len(changed) == len(original)
    stamp = store.path.stat()
    store.path.write_bytes(changed)
    os.utime(store.path, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
    with pytest.raises(L.LedgerIntegrityError, match="content does not match"):
        store.append("EVENT", {"value": 3})
    assert store.path.read_bytes() == changed


def test_two_warm_instances_revalidate_and_enforce_cas(tmp_path):
    a, b = L.LedgerStore(tmp_path), L.LedgerStore(tmp_path)
    one = a.append("EVENT", {"value": 1}, expected_head=None)
    two = b.append("EVENT", {"value": 2}, expected_head=one.entry_hash)
    with pytest.raises(L.StaleLedgerHead) as refused:
        a.append("EVENT", {"value": 3}, expected_head=one.entry_hash)
    assert refused.value.actual_head == two.entry_hash
    three = a.append("EVENT", {"value": 3}, expected_head=two.entry_hash)
    four = b.append("EVENT", {"value": 4}, expected_head=three.entry_hash)
    with pytest.raises(L.StaleLedgerHead):
        b.append("EVENT", {}, expected_head=None)
    assert a.entries() == (one, two, three, four)


@pytest.mark.parametrize("edit", ["truncate", "replace-empty", "replace-valid", "missing"])
def test_disk_changes_follow_reference_head_semantics(tmp_path, edit):
    store = L.LedgerStore(tmp_path / "state")
    first = store.append("EVENT", {"value": 1})
    store.append("EVENT", {"value": 2})
    if edit == "missing":
        store.path.unlink()
        with pytest.raises(FileNotFoundError):
            store.append("EVENT", {})
        return
    if edit == "truncate":
        store.path.write_bytes(store.path.read_bytes().splitlines(keepends=True)[0])
        expected = first.entry_hash
    elif edit == "replace-empty":
        replacement = tmp_path / "empty"
        replacement.write_bytes(b"")
        replacement.replace(store.path)
        expected = None
    else:
        other = L.LedgerStore(tmp_path / "other")
        expected = other.append("OTHER", {"value": 9}).entry_hash
        other.path.replace(store.path)
    reference = L.LedgerStore(store.root).entries()
    appended = store.append("EVENT", {}, expected_head=expected)
    assert appended.sequence == len(reference)
    assert store.entries() == (*reference, appended)


@pytest.mark.parametrize("ending", [b"\n", b"\r\n", b"\r", b""])
def test_universal_newlines_blank_lines_and_missing_final_newline(tmp_path, ending):
    store = L.LedgerStore(tmp_path)
    first = store.append("EVENT", {"value": 1})
    # Warm cache must not bypass validation of this alternate physical encoding.
    content = b" \t\r\n\r" + store.path.read_bytes().rstrip(b"\n") + ending
    store.path.write_bytes(content)
    assert store.entries() == (first,)
    second = store.append("EVENT", {"value": 2}, expected_head=first.entry_hash)
    expected_prefix = content + (b"\n" if not content.endswith(b"\n") else b"")
    assert store.path.read_bytes().startswith(expected_prefix)
    assert store.entries() == (first, second)


@pytest.mark.parametrize("suffix", [
    b"\v{}", b"\x85{}", b"\xff", b"\n{}", b"\n[]",
    b'\n{"sequence":"bad","kind":"EVENT","payload":{},"prev_hash":"","entry_hash":""}',
])
def test_decoder_errors_match_full_public_validation(tmp_path, suffix):
    store = L.LedgerStore(tmp_path)
    store.append("EVENT", {"value": 1})
    content = store.path.read_bytes().rstrip(b"\n") + suffix
    store.path.write_bytes(content)
    with pytest.raises(Exception) as reference:
        store.entries()
    with pytest.raises(type(reference.value)) as observed:
        store.append("EVENT", {})
    assert str(observed.value) == str(reference.value)
    assert store.path.read_bytes() == content


def test_empty_is_valid_but_cache_starts_uninitialized(tmp_path):
    store = L.LedgerStore(tmp_path)
    assert store._validated_snapshot is None
    first = store.append("EVENT", {}, expected_head=None)
    content, head, count = store._validated_snapshot
    assert content == store.path.read_bytes()
    assert (head, count) == (first.entry_hash, 1)
    assert type(content) is bytes and type(head) is str and type(count) is int

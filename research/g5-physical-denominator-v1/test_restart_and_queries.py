"""Restart suffix replay, head-query shape, and absence of full-state copies."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ocm.store.ledger import LedgerIntegrityError, LedgerStore
from wal_ledger import CheckpointedWALLedger


def test_normal_restart_replays_only_suffix(tmp_path: Path) -> None:
    root = tmp_path / "wal"
    first = CheckpointedWALLedger(root, checkpoint_interval=8)
    for index in range(20):
        first.append("EVENT", {"i": index})
    assert first.snapshot_count() == 2
    last = first.head()
    identity = first.authenticated_identity()

    restarted = CheckpointedWALLedger(root, checkpoint_interval=8)
    assert restarted.snapshot_sequence_on_open == 15
    assert restarted.suffix_rows_verified_on_open == 4
    assert restarted.head() == last
    assert restarted.authenticated_identity() == identity
    assert [entry.sequence for entry in restarted.entries()] == list(range(20))
    assert restarted.verify() == ()


def test_explicit_checkpoint_then_restart_verifies_zero_suffix_when_caught_up(
    tmp_path: Path,
) -> None:
    root = tmp_path / "wal"
    store = CheckpointedWALLedger(root, checkpoint_interval=1000)
    for index in range(11):
        store.append("EVENT", {"i": index})
    receipt = store.checkpoint()
    assert receipt["count"] == 11
    restarted = CheckpointedWALLedger(root, checkpoint_interval=1000)
    assert restarted.snapshot_sequence_on_open == 10
    assert restarted.suffix_rows_verified_on_open == 0
    assert restarted.head() == store.head()


def test_suffix_replay_detects_tail_tampering(tmp_path: Path) -> None:
    root = tmp_path / "wal"
    store = CheckpointedWALLedger(root, checkpoint_interval=4)
    for index in range(6):
        store.append("EVENT", {"i": index})
    connection = sqlite3.connect(store.path)
    try:
        connection.execute(
            "UPDATE ledger_entries SET payload_json = ? WHERE sequence = 5",
            ('{"i":999}',),
        )
        connection.commit()
    finally:
        connection.close()
    with pytest.raises(LedgerIntegrityError, match="does not match its digest"):
        CheckpointedWALLedger(root, checkpoint_interval=4)


def test_head_query_is_meta_plus_primary_key_not_history_scan(tmp_path: Path) -> None:
    store = CheckpointedWALLedger(tmp_path / "wal", checkpoint_interval=32)
    for index in range(40):
        store.append("EVENT", {"i": index})
    statements: list[str] = []

    def tracer(statement: str) -> None:
        statements.append(statement)

    with store._connect() as connection:
        connection.set_trace_callback(tracer)
        head_hash, sequence, _identity, count = store._meta(connection)
        assert count == 40
        row = connection.execute(
            "SELECT e.sequence, k.kind, e.payload_json, e.prev_hash, e.entry_hash, e.identity "
            "FROM ledger_entries AS e "
            "JOIN kind_dict AS k ON k.handle = e.kind_handle "
            "WHERE e.sequence = ?",
            (sequence,),
        ).fetchone()
        assert row is not None
        assert head_hash == row[4]
    history_scans = [
        statement
        for statement in statements
        if "FROM ledger_entries" in statement and "WHERE e.sequence =" not in statement
    ]
    assert history_scans == []
    assert store.head() is not None
    assert store.head().sequence == 39


def test_jsonl_incumbent_head_still_replays_full_history(tmp_path: Path) -> None:
    store = LedgerStore(tmp_path / "jsonl")
    store.append("EVENT", {"i": 0})
    store.append("EVENT", {"i": 1})
    assert store._validated_snapshot is not None
    snapshot_bytes, head_hash, count = store._validated_snapshot
    assert count == 2
    assert len(snapshot_bytes) == store.path.stat().st_size
    assert store.head().entry_hash == head_hash


def test_wal_store_keeps_no_detached_full_state_copy(tmp_path: Path) -> None:
    store = CheckpointedWALLedger(tmp_path / "wal")
    for index in range(50):
        store.append("EVENT", {"i": index, "pad": "x" * 64})
    assert not any(
        isinstance(value, (bytes, bytearray, memoryview)) and len(value) > 64
        for value in vars(store).values()
    )
    assert store.head() is not None
    assert store.kind_handle_count() == 1


def test_kind_filter_does_not_require_python_scan_of_other_kinds(tmp_path: Path) -> None:
    store = CheckpointedWALLedger(tmp_path / "wal")
    store.append("A", {"n": 1})
    store.append("B", {"n": 2})
    store.append("A", {"n": 3})
    assert [entry.payload["n"] for entry in store.entries("A")] == [1, 3]
    assert [entry.kind for entry in store.entries("B")] == ["B"]

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from ocm.store.ledger import LedgerStore, StaleLedgerHead, TransactionIdConflict
from ocm.store.sqlite_ledger import SQLiteLedgerStore


def _stores(tmp_path: Path):
    return LedgerStore(tmp_path / "jsonl"), SQLiteLedgerStore(tmp_path / "sqlite")


def test_sqlite_parent_matches_incumbent_hash_chain_and_export_bytes(tmp_path: Path):
    incumbent, donor = _stores(tmp_path)
    records = [
        ("EVIDENCE", {"z": 3, "a": [2, 1]}),
        ("OBJECT", {"id": "claim:x", "warrant": ["e1"]}),
        ("REVISION", {"evidence": "e1", "revoked": True}),
    ]
    incumbent_head = donor_head = None
    for kind, payload in records:
        left = incumbent.append(kind, payload, expected_head=incumbent_head)
        right = donor.append(kind, payload, expected_head=donor_head)
        assert right == left
        incumbent_head = left.entry_hash
        donor_head = right.entry_hash

    assert donor.entries() == incumbent.entries()
    assert donor.export_jsonl_bytes() == incumbent.path.read_bytes()
    assert donor.verify() == ()
    assert donor.journal_mode() == "wal"


def test_sqlite_parent_preserves_compare_and_swap_across_instances(tmp_path: Path):
    root = tmp_path / "shared"
    first = SQLiteLedgerStore(root)
    second = SQLiteLedgerStore(root)
    a = first.append("A", {"n": 1}, expected_head=None)
    b = first.append("B", {"n": 2}, expected_head=a.entry_hash)
    with pytest.raises(StaleLedgerHead) as exc:
        second.append("STALE", {"n": 3}, expected_head=a.entry_hash)
    assert exc.value.expected_head == a.entry_hash
    assert exc.value.actual_head == b.entry_hash
    assert [entry.kind for entry in second.entries()] == ["A", "B"]


def test_sqlite_parent_matches_identified_transaction_semantics(tmp_path: Path):
    incumbent, donor = _stores(tmp_path)
    left = incumbent.append_identified("TX", {"value": 7}, transaction_id="t-1")
    right = donor.append_identified("TX", {"value": 7}, transaction_id="t-1")
    assert right == left

    assert incumbent.append_identified("TX", {"value": 7}, transaction_id="t-1") == left
    assert donor.append_identified("TX", {"value": 7}, transaction_id="t-1") == right
    assert len(incumbent.entries()) == len(donor.entries()) == 1

    with pytest.raises(TransactionIdConflict):
        incumbent.append_identified("TX", {"value": 8}, transaction_id="t-1")
    with pytest.raises(TransactionIdConflict):
        donor.append_identified("TX", {"value": 8}, transaction_id="t-1")


def test_sqlite_parent_rolls_back_failed_cas_without_partial_row(tmp_path: Path):
    store = SQLiteLedgerStore(tmp_path / "db")
    first = store.append("A", {"n": 1}, expected_head=None)
    with pytest.raises(StaleLedgerHead):
        store.append("B", {"n": 2}, expected_head="not-the-head")
    assert store.entries() == (first,)


def test_sqlite_parent_full_verify_detects_historical_tampering(tmp_path: Path):
    store = SQLiteLedgerStore(tmp_path / "db")
    store.append("A", {"n": 1})
    store.append("B", {"n": 2})

    connection = sqlite3.connect(store.path)
    try:
        connection.execute(
            "UPDATE ledger_entries SET payload_json = ? WHERE sequence = 0",
            ('{"n":999}',),
        )
        connection.commit()
    finally:
        connection.close()

    violations = store.verify()
    assert violations
    assert "does not match its digest" in violations[0]

"""Semantic parity of the checkpointed WAL parent against the JSONL ledger."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ocm.store.ledger import LedgerStore, StaleLedgerHead, TransactionIdConflict
from wal_ledger import CheckpointedWALLedger, fold_authenticated_identity


def _stores(tmp_path: Path):
    return (
        LedgerStore(tmp_path / "jsonl"),
        CheckpointedWALLedger(tmp_path / "wal", checkpoint_interval=4),
    )


def test_hash_chain_sequence_and_export_bytes_match_jsonl(tmp_path: Path) -> None:
    incumbent, donor = _stores(tmp_path)
    records = [
        ("EVIDENCE", {"z": 3, "a": [2, 1]}),
        ("OBJECT", {"id": "claim:x", "warrant": ["e1"]}),
        ("REVISION", {"evidence": "e1", "revoked": True}),
        ("EVIDENCE", {"note": "again"}),
    ]
    incumbent_head = donor_head = None
    for kind, payload in records:
        left = incumbent.append(kind, payload, expected_head=incumbent_head)
        right = donor.append(kind, payload, expected_head=donor_head)
        assert right == left
        incumbent_head = left.entry_hash
        donor_head = right.entry_hash

    assert donor.entries() == incumbent.entries()
    assert donor.head() == incumbent.head()
    assert donor.export_jsonl_bytes() == incumbent.path.read_bytes()
    assert donor.verify() == ()
    assert donor.journal_mode() == "wal"
    assert donor.kind_handle_count() == 3


def test_compare_and_swap_none_means_genesis(tmp_path: Path) -> None:
    incumbent, donor = _stores(tmp_path)
    left = incumbent.append("ROUND", {"round_index": 0}, expected_head=None)
    right = donor.append("ROUND", {"round_index": 0}, expected_head=None)
    assert right == left
    with pytest.raises(StaleLedgerHead) as left_exc:
        incumbent.append("ROUND", {"round_index": 1}, expected_head=None)
    with pytest.raises(StaleLedgerHead) as right_exc:
        donor.append("ROUND", {"round_index": 1}, expected_head=None)
    assert left_exc.value.expected_head is None
    assert right_exc.value.expected_head is None
    assert left_exc.value.actual_head == right_exc.value.actual_head == left.entry_hash


def test_stale_head_rolls_back_without_partial_row(tmp_path: Path) -> None:
    donor = CheckpointedWALLedger(tmp_path / "wal")
    first = donor.append("A", {"n": 1}, expected_head=None)
    with pytest.raises(StaleLedgerHead):
        donor.append("B", {"n": 2}, expected_head="not-the-head")
    assert donor.entries() == (first,)
    assert donor.head() == first


def test_identified_transaction_idempotency_and_conflict(tmp_path: Path) -> None:
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
    with pytest.raises(TransactionIdConflict):
        donor.append_identified("OTHER", {"value": 7}, transaction_id="t-1")


def test_identified_idempotency_runs_before_head_cas(tmp_path: Path) -> None:
    incumbent, donor = _stores(tmp_path)
    first_left = incumbent.append_identified("EVENT", {"x": 1}, transaction_id="tx:1")
    first_right = donor.append_identified("EVENT", {"x": 1}, transaction_id="tx:1")
    incumbent.append("ROUND", {"round_index": 0})
    donor.append("ROUND", {"round_index": 0})
    replayed_left = incumbent.append_identified(
        "EVENT", {"x": 1}, transaction_id="tx:1", expected_head=first_left.prev_hash
    )
    replayed_right = donor.append_identified(
        "EVENT", {"x": 1}, transaction_id="tx:1", expected_head=first_right.prev_hash
    )
    assert replayed_left == first_left
    assert replayed_right == first_right
    assert len(incumbent.entries()) == len(donor.entries()) == 2


def test_incremental_identity_matches_genesis_fold(tmp_path: Path) -> None:
    donor = CheckpointedWALLedger(tmp_path / "wal", checkpoint_interval=3)
    identity = donor.genesis_identity
    for index in range(10):
        entry = donor.append("EVENT", {"i": index})
        identity = fold_authenticated_identity(identity, entry.sequence, entry.entry_hash)
        assert donor.authenticated_identity() == identity
    assert donor.verify() == ()
    assert donor.snapshot_count() == 3


def test_full_genesis_audit_detects_prefix_tampering(tmp_path: Path) -> None:
    donor = CheckpointedWALLedger(tmp_path / "wal", checkpoint_interval=2)
    donor.append("A", {"n": 1})
    donor.append("B", {"n": 2})
    donor.append("C", {"n": 3})
    connection = sqlite3.connect(donor.path)
    try:
        connection.execute(
            "UPDATE ledger_entries SET payload_json = ? WHERE sequence = 0",
            ('{"n":999}',),
        )
        connection.commit()
    finally:
        connection.close()
    violations = donor.verify()
    assert violations
    assert "does not match its digest" in violations[0]

"""SQLite/WAL donor backend for the OCM hash-chained ledger contract.

This module is an **experimental parent**, not the default runtime store. It keeps
OCM's canonical row hashes, sequence/previous-hash chain, compare-and-swap head
semantics and identified-transaction behaviour while delegating transactional
persistence and incremental append to SQLite WAL.

The incumbent :mod:`ocm.store.ledger` intentionally rewrites the complete JSONL
file and re-verifies the complete chain on every append. That is an excellent
small-state reference/durability oracle, but its lifetime write work grows with
all previous history. This donor instead verifies the chain on ``entries`` /
``verify`` / explicit export and uses a database transaction plus indexed tail
lookup for normal append. Therefore corruption-detection *timing* is not yet
identical to the incumbent and runtime adoption requires a separately registered
contract decision. No scientific result follows from this engineering parent.
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .canonical import canonical_bytes
from .ledger import (
    LedgerEntry,
    LedgerIntegrityError,
    StaleLedgerHead,
    TransactionIdConflict,
    _EXPECTED_HEAD_UNSET,
    _GENESIS_HASH,
    _TRANSACTION_ID_FIELD,
    _ExpectedHeadUnset,
    _require_kind,
    compute_entry_hash,
)

_DB_FILENAME = "ledger.sqlite3"


class SQLiteLedgerStore:
    """Transactional hash-chain store backed by SQLite WAL."""

    def __init__(self, root: Path, *, timeout: float = 30.0) -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)
        self._path = self._root / _DB_FILENAME
        self._timeout = float(timeout)
        if self._timeout <= 0:
            raise ValueError("timeout must be positive")
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS ledger_entries (
                    sequence INTEGER PRIMARY KEY,
                    kind TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    prev_hash TEXT NOT NULL,
                    entry_hash TEXT NOT NULL UNIQUE,
                    transaction_id TEXT
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS ledger_txid_idx ON ledger_entries(transaction_id)"
            )

    @property
    def root(self) -> Path:
        return self._root

    @property
    def path(self) -> Path:
        return self._path

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._path, timeout=self._timeout, isolation_level=None)
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=FULL")
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    @staticmethod
    def _payload_text(payload: Mapping[str, Any]) -> tuple[Mapping[str, Any], str]:
        normalized = json.loads(canonical_bytes(payload))
        text = canonical_bytes(normalized).decode("utf-8")
        return normalized, text

    @staticmethod
    def _row_entry(row: tuple[Any, ...]) -> LedgerEntry:
        sequence, kind, payload_json, prev_hash, entry_hash = row[:5]
        try:
            payload = json.loads(payload_json)
        except json.JSONDecodeError as error:
            raise LedgerIntegrityError(
                f"sequence {sequence} payload is not valid canonical JSON: {error}"
            ) from error
        if not isinstance(payload, Mapping):
            raise LedgerIntegrityError(f"sequence {sequence} payload is not an object")
        return LedgerEntry(int(sequence), str(kind), payload, str(prev_hash), str(entry_hash))

    @staticmethod
    def _check_expected_head(
        actual_head: str | None,
        expected_head: str | None | _ExpectedHeadUnset,
    ) -> None:
        if not isinstance(expected_head, _ExpectedHeadUnset) and expected_head != actual_head:
            raise StaleLedgerHead(expected_head, actual_head)

    @staticmethod
    def _tail(connection: sqlite3.Connection) -> LedgerEntry | None:
        row = connection.execute(
            "SELECT sequence, kind, payload_json, prev_hash, entry_hash "
            "FROM ledger_entries ORDER BY sequence DESC LIMIT 1"
        ).fetchone()
        return None if row is None else SQLiteLedgerStore._row_entry(row)

    @staticmethod
    def _insert(
        connection: sqlite3.Connection,
        *,
        kind: str,
        normalized_payload: Mapping[str, Any],
        payload_text: str,
        tail: LedgerEntry | None,
    ) -> LedgerEntry:
        sequence = 0 if tail is None else tail.sequence + 1
        prev_hash = _GENESIS_HASH if tail is None else tail.entry_hash
        entry_hash = compute_entry_hash(sequence, kind, normalized_payload, prev_hash)
        transaction_id = str(normalized_payload.get(_TRANSACTION_ID_FIELD, "")) or None
        connection.execute(
            "INSERT INTO ledger_entries "
            "(sequence, kind, payload_json, prev_hash, entry_hash, transaction_id) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (sequence, kind, payload_text, prev_hash, entry_hash, transaction_id),
        )
        return LedgerEntry(sequence, kind, normalized_payload, prev_hash, entry_hash)

    def entries(self, kind: str | None = None) -> tuple[LedgerEntry, ...]:
        """Read and fully verify the canonical hash chain."""
        query = (
            "SELECT sequence, kind, payload_json, prev_hash, entry_hash "
            "FROM ledger_entries ORDER BY sequence"
        )
        with self._connect() as connection:
            rows = connection.execute(query).fetchall()
        replayed: list[LedgerEntry] = []
        previous = _GENESIS_HASH
        for expected_sequence, row in enumerate(rows):
            entry = self._row_entry(row)
            if entry.sequence != expected_sequence:
                raise LedgerIntegrityError(
                    f"sequence {entry.sequence}, expected {expected_sequence}"
                )
            if entry.prev_hash != previous:
                raise LedgerIntegrityError(
                    f"sequence {entry.sequence} does not chain to its predecessor"
                )
            recomputed = compute_entry_hash(
                entry.sequence, entry.kind, entry.payload, entry.prev_hash
            )
            if recomputed != entry.entry_hash:
                raise LedgerIntegrityError(
                    f"sequence {entry.sequence} content does not match its digest"
                )
            replayed.append(entry)
            previous = entry.entry_hash
        if kind is None:
            return tuple(replayed)
        return tuple(entry for entry in replayed if entry.kind == kind)

    def head(self) -> LedgerEntry | None:
        with self._connect() as connection:
            return self._tail(connection)

    def append(
        self,
        kind: str,
        payload: Mapping[str, Any],
        *,
        expected_head: str | None | _ExpectedHeadUnset = _EXPECTED_HEAD_UNSET,
    ) -> LedgerEntry:
        kind = _require_kind(kind)
        if not isinstance(payload, Mapping):
            raise ValueError("ledger payload must be a mapping")
        normalized, text = self._payload_text(payload)
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            tail = self._tail(connection)
            self._check_expected_head(None if tail is None else tail.entry_hash, expected_head)
            entry = self._insert(
                connection,
                kind=kind,
                normalized_payload=normalized,
                payload_text=text,
                tail=tail,
            )
            connection.execute("COMMIT")
            return entry
        except Exception:
            if connection.in_transaction:
                connection.execute("ROLLBACK")
            raise
        finally:
            connection.close()

    def append_identified(
        self,
        kind: str,
        payload: Mapping[str, Any],
        *,
        transaction_id: str,
        expected_head: str | None | _ExpectedHeadUnset = _EXPECTED_HEAD_UNSET,
    ) -> LedgerEntry:
        kind = _require_kind(kind)
        if not isinstance(payload, Mapping):
            raise ValueError("ledger payload must be a mapping")
        if type(transaction_id) is not str or not transaction_id.strip():
            raise ValueError("transaction_id must be a nonblank string")
        declared = payload.get(_TRANSACTION_ID_FIELD, transaction_id)
        if declared != transaction_id:
            raise ValueError("payload transaction_id disagrees with the declared transaction_id")
        identified = {**dict(payload), _TRANSACTION_ID_FIELD: transaction_id}
        normalized, text = self._payload_text(identified)
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            existing_rows = connection.execute(
                "SELECT sequence, kind, payload_json, prev_hash, entry_hash "
                "FROM ledger_entries WHERE transaction_id = ? ORDER BY sequence",
                (transaction_id,),
            ).fetchall()
            for row in existing_rows:
                existing = self._row_entry(row)
                if existing.kind == kind and existing.payload == normalized:
                    connection.execute("COMMIT")
                    return existing
                raise TransactionIdConflict(
                    f"transaction id {transaction_id} already exists with different content"
                )
            tail = self._tail(connection)
            self._check_expected_head(None if tail is None else tail.entry_hash, expected_head)
            entry = self._insert(
                connection,
                kind=kind,
                normalized_payload=normalized,
                payload_text=text,
                tail=tail,
            )
            connection.execute("COMMIT")
            return entry
        except Exception:
            if connection.in_transaction:
                connection.execute("ROLLBACK")
            raise
        finally:
            connection.close()

    def verify(self) -> tuple[str, ...]:
        try:
            self.entries()
        except (LedgerIntegrityError, sqlite3.DatabaseError) as error:
            return (str(error),)
        return ()

    def export_jsonl_bytes(self) -> bytes:
        chunks = []
        for entry in self.entries():
            chunks.append(
                canonical_bytes(
                    {
                        "sequence": entry.sequence,
                        "kind": entry.kind,
                        "payload": entry.payload,
                        "prev_hash": entry.prev_hash,
                        "entry_hash": entry.entry_hash,
                    }
                )
                + b"\n"
            )
        return b"".join(chunks)

    def journal_mode(self) -> str:
        with self._connect() as connection:
            row = connection.execute("PRAGMA journal_mode").fetchone()
        return str(row[0]).lower()

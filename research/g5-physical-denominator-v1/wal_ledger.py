"""Checkpointed SQLite/WAL ledger parent for G5.1 physical-denominator work.

Parallel to ``ocm.store.ledger.LedgerStore``. Production JSONL rewrite and the
existing experimental ``ocm.store.sqlite_ledger`` module are left unchanged.

Normal restart verifies only the suffix after the last application snapshot.
``verify()`` remains a full-genesis audit. Head and append consult a singleton
meta row plus primary-key lookups; they do not scan or copy the full history.
Kinds are dictionary-encoded as integer handles. Authenticated state identity
is a rolling fold of ``(prev_identity, sequence, entry_hash)``.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from ocm.store.canonical import canonical_bytes
from ocm.store.ledger import (
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
_IDENTITY_DOMAIN = "ocm.authenticated-state.v1"
_GENESIS_IDENTITY = hashlib.sha256(b"ocm.authenticated-state.v1\x00genesis").hexdigest()
_ENTRY_SELECT = (
    "SELECT e.sequence, k.kind, e.payload_json, e.prev_hash, e.entry_hash, e.identity "
    "FROM ledger_entries AS e "
    "JOIN kind_dict AS k ON k.handle = e.kind_handle"
)


def fold_authenticated_identity(prev_identity: str, sequence: int, entry_hash: str) -> str:
    """Incrementally bind state identity to the previous fold and this row hash."""

    return hashlib.sha256(
        canonical_bytes(
            {
                "domain": _IDENTITY_DOMAIN,
                "entry_hash": entry_hash,
                "prev_identity": prev_identity,
                "sequence": sequence,
            }
        )
    ).hexdigest()


def _payload_text(payload: Mapping[str, Any]) -> tuple[Mapping[str, Any], str]:
    normalized = json.loads(canonical_bytes(payload))
    return normalized, canonical_bytes(normalized).decode("utf-8")


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


class CheckpointedWALLedger:
    """Append-only hash chain with SQLite WAL, snapshots, and suffix restart replay."""

    def __init__(
        self,
        root: Path,
        *,
        checkpoint_interval: int = 64,
        wal_checkpoint: bool = True,
        timeout: float = 30.0,
    ) -> None:
        if checkpoint_interval <= 0:
            raise ValueError("checkpoint_interval must be positive")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)
        self._path = self._root / _DB_FILENAME
        self._checkpoint_interval = int(checkpoint_interval)
        self._wal_checkpoint = bool(wal_checkpoint)
        self._timeout = float(timeout)
        self.suffix_rows_verified_on_open = 0
        self.snapshot_sequence_on_open: int | None = None
        self.checkpoint_count = 0
        self.checkpoint_wall_s = 0.0
        self.wal_checkpoint_wall_s = 0.0
        self.append_count = 0
        with self._connect() as connection:
            self._ensure_schema(connection)
            self._replay_suffix(connection)

    @property
    def root(self) -> Path:
        return self._root

    @property
    def path(self) -> Path:
        return self._path

    @property
    def genesis_identity(self) -> str:
        return _GENESIS_IDENTITY

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self._path, timeout=self._timeout, isolation_level=None)
        try:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA synchronous=FULL")
            connection.execute("PRAGMA foreign_keys=ON")
            yield connection
        finally:
            connection.close()

    @staticmethod
    def _ensure_schema(connection: sqlite3.Connection) -> None:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS kind_dict (
                handle INTEGER PRIMARY KEY,
                kind TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS ledger_entries (
                sequence INTEGER PRIMARY KEY,
                kind_handle INTEGER NOT NULL REFERENCES kind_dict(handle),
                payload_json TEXT NOT NULL,
                prev_hash TEXT NOT NULL,
                entry_hash TEXT NOT NULL UNIQUE,
                transaction_id TEXT,
                identity TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS ledger_txid_idx
                ON ledger_entries(transaction_id);
            CREATE TABLE IF NOT EXISTS ledger_meta (
                singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                head_hash TEXT,
                sequence INTEGER NOT NULL,
                identity TEXT NOT NULL,
                count INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS snapshots (
                sequence INTEGER PRIMARY KEY,
                head_hash TEXT,
                identity TEXT NOT NULL,
                count INTEGER NOT NULL
            );
            """
        )
        existing = connection.execute(
            "SELECT 1 FROM ledger_meta WHERE singleton = 1"
        ).fetchone()
        if existing is None:
            connection.execute(
                "INSERT INTO ledger_meta(singleton, head_hash, sequence, identity, count) "
                "VALUES (1, NULL, -1, ?, 0)",
                (_GENESIS_IDENTITY,),
            )

    def _replay_suffix(self, connection: sqlite3.Connection) -> None:
        snapshot = connection.execute(
            "SELECT sequence, head_hash, identity, count FROM snapshots "
            "ORDER BY sequence DESC LIMIT 1"
        ).fetchone()
        if snapshot is None:
            start_sequence = -1
            previous_hash = _GENESIS_HASH
            previous_identity = _GENESIS_IDENTITY
            self.snapshot_sequence_on_open = None
        else:
            start_sequence = int(snapshot[0])
            previous_hash = str(snapshot[1]) if snapshot[1] is not None else _GENESIS_HASH
            previous_identity = str(snapshot[2])
            self.snapshot_sequence_on_open = start_sequence
        rows = connection.execute(
            f"{_ENTRY_SELECT} WHERE e.sequence > ? ORDER BY e.sequence",
            (start_sequence,),
        ).fetchall()
        last_entry: LedgerEntry | None = None
        last_identity = previous_identity
        for offset, row in enumerate(rows):
            entry = _row_entry(row)
            expected_sequence = start_sequence + 1 + offset
            stored_identity = str(row[5])
            if entry.sequence != expected_sequence:
                raise LedgerIntegrityError(
                    f"sequence {entry.sequence}, expected {expected_sequence}"
                )
            if entry.prev_hash != previous_hash:
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
            folded = fold_authenticated_identity(
                previous_identity, entry.sequence, entry.entry_hash
            )
            if folded != stored_identity:
                raise LedgerIntegrityError(
                    f"sequence {entry.sequence} identity does not match the incremental fold"
                )
            previous_hash = entry.entry_hash
            previous_identity = folded
            last_entry = entry
            last_identity = folded
        self.suffix_rows_verified_on_open = len(rows)
        if last_entry is None and snapshot is None:
            return
        if last_entry is None:
            head_hash, sequence, identity, count = (
                snapshot[1],
                int(snapshot[0]),
                str(snapshot[2]),
                int(snapshot[3]),
            )
        else:
            head_hash, sequence, identity, count = (
                last_entry.entry_hash,
                last_entry.sequence,
                last_identity,
                last_entry.sequence + 1,
            )
        connection.execute(
            "UPDATE ledger_meta SET head_hash = ?, sequence = ?, identity = ?, count = ? "
            "WHERE singleton = 1",
            (head_hash, sequence, identity, count),
        )

    @staticmethod
    def _meta(connection: sqlite3.Connection) -> tuple[str | None, int, str, int]:
        row = connection.execute(
            "SELECT head_hash, sequence, identity, count FROM ledger_meta WHERE singleton = 1"
        ).fetchone()
        if row is None:
            raise LedgerIntegrityError("ledger meta row is missing")
        return row[0], int(row[1]), str(row[2]), int(row[3])

    @staticmethod
    def _intern_kind(connection: sqlite3.Connection, kind: str) -> int:
        row = connection.execute(
            "SELECT handle FROM kind_dict WHERE kind = ?", (kind,)
        ).fetchone()
        if row is not None:
            return int(row[0])
        connection.execute("INSERT INTO kind_dict(kind) VALUES (?)", (kind,))
        return int(connection.execute("SELECT last_insert_rowid()").fetchone()[0])

    @staticmethod
    def _check_expected_head(
        actual_head: str | None,
        expected_head: str | None | _ExpectedHeadUnset,
    ) -> None:
        if not isinstance(expected_head, _ExpectedHeadUnset) and expected_head != actual_head:
            raise StaleLedgerHead(expected_head, actual_head)

    def _insert(
        self,
        connection: sqlite3.Connection,
        *,
        kind: str,
        normalized_payload: Mapping[str, Any],
        payload_text: str,
        head_hash: str | None,
        last_sequence: int,
        prev_identity: str,
        count: int,
    ) -> LedgerEntry:
        sequence = 0 if count == 0 else last_sequence + 1
        prev_hash = _GENESIS_HASH if head_hash is None else head_hash
        entry_hash = compute_entry_hash(sequence, kind, normalized_payload, prev_hash)
        identity = fold_authenticated_identity(prev_identity, sequence, entry_hash)
        transaction_id = str(normalized_payload.get(_TRANSACTION_ID_FIELD, "")) or None
        kind_handle = self._intern_kind(connection, kind)
        connection.execute(
            "INSERT INTO ledger_entries "
            "(sequence, kind_handle, payload_json, prev_hash, entry_hash, transaction_id, identity) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                sequence,
                kind_handle,
                payload_text,
                prev_hash,
                entry_hash,
                transaction_id,
                identity,
            ),
        )
        connection.execute(
            "UPDATE ledger_meta SET head_hash = ?, sequence = ?, identity = ?, count = ? "
            "WHERE singleton = 1",
            (entry_hash, sequence, identity, count + 1),
        )
        entry = LedgerEntry(sequence, kind, normalized_payload, prev_hash, entry_hash)
        if (count + 1) % self._checkpoint_interval == 0:
            self._write_snapshot(
                connection,
                sequence=sequence,
                head_hash=entry_hash,
                identity=identity,
                count=count + 1,
            )
        return entry

    def _write_snapshot(
        self,
        connection: sqlite3.Connection,
        *,
        sequence: int,
        head_hash: str | None,
        identity: str,
        count: int,
    ) -> None:
        started = time.perf_counter()
        connection.execute(
            "INSERT OR REPLACE INTO snapshots(sequence, head_hash, identity, count) "
            "VALUES (?, ?, ?, ?)",
            (sequence, head_hash, identity, count),
        )
        self.checkpoint_wall_s += time.perf_counter() - started
        self.checkpoint_count += 1

    def checkpoint(self) -> dict[str, Any]:
        """Write an application snapshot of the current head and checkpoint WAL."""

        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                head_hash, sequence, identity, count = self._meta(connection)
                if count == 0:
                    connection.execute("COMMIT")
                    return {
                        "sequence": None,
                        "count": 0,
                        "identity": identity,
                        "wal_checkpoint": None,
                    }
                self._write_snapshot(
                    connection,
                    sequence=sequence,
                    head_hash=head_hash,
                    identity=identity,
                    count=count,
                )
                connection.execute("COMMIT")
            except Exception:
                if connection.in_transaction:
                    connection.execute("ROLLBACK")
                raise
        wal_info = None
        wal_wall = 0.0
        if self._wal_checkpoint:
            started = time.perf_counter()
            with self._connect() as connection:
                wal_info = connection.execute("PRAGMA wal_checkpoint(FULL)").fetchone()
            wal_wall = time.perf_counter() - started
            self.wal_checkpoint_wall_s += wal_wall
        return {
            "sequence": sequence,
            "count": count,
            "identity": identity,
            "wal_checkpoint": None if wal_info is None else list(wal_info),
            "wal_checkpoint_wall_s": wal_wall,
        }

    def head(self) -> LedgerEntry | None:
        with self._connect() as connection:
            head_hash, sequence, _identity, count = self._meta(connection)
            if count == 0 or head_hash is None:
                return None
            row = connection.execute(
                f"{_ENTRY_SELECT} WHERE e.sequence = ?",
                (sequence,),
            ).fetchone()
            if row is None:
                raise LedgerIntegrityError(f"meta sequence {sequence} is missing from entries")
            return _row_entry(row)

    def authenticated_identity(self) -> str:
        with self._connect() as connection:
            return self._meta(connection)[2]

    def entries(self, kind: str | None = None) -> tuple[LedgerEntry, ...]:
        """Return rows. Prefix hashes are not re-audited; use ``verify()`` for genesis replay."""

        query = f"{_ENTRY_SELECT} ORDER BY e.sequence"
        params: tuple[Any, ...] = ()
        if kind is not None:
            query = f"{_ENTRY_SELECT} WHERE k.kind = ? ORDER BY e.sequence"
            params = (kind,)
        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return tuple(_row_entry(row) for row in rows)

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
        normalized, text = _payload_text(payload)
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                head_hash, last_sequence, prev_identity, count = self._meta(connection)
                self._check_expected_head(head_hash, expected_head)
                entry = self._insert(
                    connection,
                    kind=kind,
                    normalized_payload=normalized,
                    payload_text=text,
                    head_hash=head_hash,
                    last_sequence=last_sequence,
                    prev_identity=prev_identity,
                    count=count,
                )
                connection.execute("COMMIT")
                self.append_count += 1
                return entry
            except Exception:
                if connection.in_transaction:
                    connection.execute("ROLLBACK")
                raise

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
        normalized, text = _payload_text(identified)
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                existing_rows = connection.execute(
                    f"{_ENTRY_SELECT} WHERE e.transaction_id = ? ORDER BY e.sequence",
                    (transaction_id,),
                ).fetchall()
                for row in existing_rows:
                    existing = _row_entry(row)
                    if existing.kind == kind and existing.payload == normalized:
                        connection.execute("COMMIT")
                        return existing
                    raise TransactionIdConflict(
                        f"transaction id {transaction_id} already exists with different content"
                    )
                head_hash, last_sequence, prev_identity, count = self._meta(connection)
                self._check_expected_head(head_hash, expected_head)
                entry = self._insert(
                    connection,
                    kind=kind,
                    normalized_payload=normalized,
                    payload_text=text,
                    head_hash=head_hash,
                    last_sequence=last_sequence,
                    prev_identity=prev_identity,
                    count=count,
                )
                connection.execute("COMMIT")
                self.append_count += 1
                return entry
            except Exception:
                if connection.in_transaction:
                    connection.execute("ROLLBACK")
                raise

    def verify(self) -> tuple[str, ...]:
        """Full-genesis audit. Empty means the local chain and identities are intact."""

        try:
            self.verify_from_genesis()
        except (LedgerIntegrityError, sqlite3.DatabaseError) as error:
            return (str(error),)
        return ()

    def verify_from_genesis(self) -> tuple[LedgerEntry, ...]:
        with self._connect() as connection:
            rows = connection.execute(f"{_ENTRY_SELECT} ORDER BY e.sequence").fetchall()
        replayed: list[LedgerEntry] = []
        previous = _GENESIS_HASH
        previous_identity = _GENESIS_IDENTITY
        for expected_sequence, row in enumerate(rows):
            entry = _row_entry(row)
            stored_identity = str(row[5])
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
            folded = fold_authenticated_identity(
                previous_identity, entry.sequence, entry.entry_hash
            )
            if folded != stored_identity:
                raise LedgerIntegrityError(
                    f"sequence {entry.sequence} identity does not match the incremental fold"
                )
            replayed.append(entry)
            previous = entry.entry_hash
            previous_identity = folded
        return tuple(replayed)

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

    def snapshot_count(self) -> int:
        with self._connect() as connection:
            row = connection.execute("SELECT COUNT(*) FROM snapshots").fetchone()
        return int(row[0])

    def kind_handle_count(self) -> int:
        with self._connect() as connection:
            row = connection.execute("SELECT COUNT(*) FROM kind_dict").fetchone()
        return int(row[0])

    def physical_bytes(self) -> int:
        return sum(path.stat().st_size for path in self._root.iterdir() if path.is_file())

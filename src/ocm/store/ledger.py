"""Crash-atomic, hash-chained, compare-and-swap append-only ledger.

ADAPTED from ORION ``src/orion/kernel/store.py`` (SzeChunYiu/ORION commit
adb97ecce7d8e1fe6effab456b98e653f401dae0). Kept, with the mechanics verbatim:

* ``canonical_bytes`` / ``compute_entry_hash`` (byte-identical digest semantics;
  ``canonical_bytes`` now lives in ``ocm.store.canonical``);
* the durability path: ``fcntl.flock(LOCK_EX)`` around every append, stale
  same-directory temp cleanup, write-whole-file to a ``NamedTemporaryFile`` in
  the ledger directory, ``fsync`` the handle, ``os.replace``, then ``fsync``
  the *directory*;
* compare-and-swap on ``expected_head`` (``StaleLedgerHead``), where
  ``expected_head=None`` means "genesis", not "no precondition";
* ``verify()`` and the chain replay in ``entries()`` (sequence, prev_hash and
  recomputed digest checked on every row);
* the transaction-id semantics of ORION's ``append_transaction`` as
  ``append_identified``: the same id with the same canonical content is
  idempotent (the existing row is returned), the same id with different
  content is a typed ``TransactionIdConflict``; the idempotency check runs
  before the head CAS, exactly as in ORION.

What changed: the ORION research-lane ``EntryKind`` enum (ROUND / ANSWER / ...
/ TRANSITION) is replaced by a generic non-blank ``str`` kind; the
``TransitionTransaction``-bound ``append_transaction``, ``LedgerExpectation``,
``protected_expectation``, ``StaleTransitionExpectation``,
``LegacyLedgerRequiresMigration`` and ``completed_round_count`` are dropped —
the OCM event layer (``ocm.store.event``) supplies the expectation tuple and
the event families.

Provenance: docs/provenance/VENDORED_SOURCE_MANIFEST_V1.json.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import fcntl

from .canonical import canonical_bytes

_GENESIS_HASH = "0" * 64
_LEDGER_FILENAME = "ledger.jsonl"
_LOCK_FILENAME = ".ledger.jsonl.lock"
_TEMP_PREFIX = ".ledger.jsonl."
_TEMP_SUFFIX = ".tmp"
_TRANSACTION_ID_FIELD = "transaction_id"


class _ExpectedHeadUnset:
    pass


_EXPECTED_HEAD_UNSET = _ExpectedHeadUnset()


@dataclass(frozen=True)
class LedgerEntry:
    """One append-only, hash-chained ledger row."""

    sequence: int
    kind: str
    payload: Mapping[str, Any]
    prev_hash: str
    entry_hash: str


class LedgerIntegrityError(RuntimeError):
    """Raised when a ledger on disk cannot be replayed as a valid chain."""


class StaleLedgerHead(RuntimeError):
    """Raised when an append's compare-and-swap precondition is stale."""

    def __init__(self, expected_head: str | None, actual_head: str | None) -> None:
        self.expected_head = expected_head
        self.actual_head = actual_head
        super().__init__(
            f"expected ledger head {expected_head!r}, found {actual_head!r}"
        )


class TransactionIdConflict(RuntimeError):
    """A transaction id was reused for different canonical content."""


def _require_kind(kind: str) -> str:
    if type(kind) is not str or not kind.strip():
        raise ValueError("ledger entry kind must be a nonblank string")
    return kind


def compute_entry_hash(
    sequence: int, kind: str, payload: Mapping[str, Any], prev_hash: str
) -> str:
    """Bind an entry to its position, content and predecessor."""

    return hashlib.sha256(
        canonical_bytes(
            {
                "sequence": sequence,
                "kind": kind,
                "payload": payload,
                "prev_hash": prev_hash,
            }
        )
    ).hexdigest()


def _decode(line: str, line_number: int) -> LedgerEntry:
    try:
        raw = json.loads(line)
    except json.JSONDecodeError as error:
        raise LedgerIntegrityError(
            f"line {line_number} is not valid JSON: {error}"
        ) from error
    if not isinstance(raw, Mapping):
        raise LedgerIntegrityError(f"line {line_number} is not a JSON object")
    missing = {"sequence", "kind", "payload", "prev_hash", "entry_hash"} - set(raw)
    if missing:
        raise LedgerIntegrityError(
            f"line {line_number} is missing fields: {', '.join(sorted(missing))}"
        )
    kind = raw["kind"]
    if type(kind) is not str or not kind.strip():
        raise LedgerIntegrityError(f"line {line_number} has an invalid kind")
    if not isinstance(raw["payload"], Mapping):
        raise LedgerIntegrityError(f"line {line_number} payload is not a JSON object")
    return LedgerEntry(
        sequence=int(raw["sequence"]),
        kind=kind,
        payload=raw["payload"],
        prev_hash=str(raw["prev_hash"]),
        entry_hash=str(raw["entry_hash"]),
    )


class LedgerStore:
    """Durable append-only, hash-chained state for one OCM runtime.

    Every row is bound to its position, content and predecessor; every append
    is serialised under an exclusive file lock and persisted crash-atomically.
    """

    def __init__(self, root: Path) -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)
        self._path = self._root / _LEDGER_FILENAME
        self._lock_path = self._root / _LOCK_FILENAME
        self._path.touch(exist_ok=True)

    @property
    def root(self) -> Path:
        return self._root

    @property
    def path(self) -> Path:
        return self._path

    def _raw_lines(self) -> Iterator[tuple[int, str]]:
        with self._path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if line.strip():
                    yield line_number, line

    def entries(self, kind: str | None = None) -> tuple[LedgerEntry, ...]:
        """Replay the ledger, verifying the chain, optionally filtered by kind."""

        replayed: list[LedgerEntry] = []
        prev_hash = _GENESIS_HASH
        for line_number, line in self._raw_lines():
            entry = _decode(line, line_number)
            expected_sequence = len(replayed)
            if entry.sequence != expected_sequence:
                raise LedgerIntegrityError(
                    f"line {line_number} has sequence {entry.sequence}, expected {expected_sequence}"
                )
            if entry.prev_hash != prev_hash:
                raise LedgerIntegrityError(
                    f"line {line_number} does not chain to its predecessor"
                )
            recomputed = compute_entry_hash(
                entry.sequence, entry.kind, entry.payload, entry.prev_hash
            )
            if recomputed != entry.entry_hash:
                raise LedgerIntegrityError(
                    f"line {line_number} content does not match its recorded digest"
                )
            replayed.append(entry)
            prev_hash = entry.entry_hash
        if kind is None:
            return tuple(replayed)
        return tuple(item for item in replayed if item.kind == kind)

    def head(self) -> LedgerEntry | None:
        entries = self.entries()
        return entries[-1] if entries else None

    @contextmanager
    def _exclusive_lock(self) -> Iterator[None]:
        descriptor = os.open(self._lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX)
            yield
        finally:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
            os.close(descriptor)

    def _cleanup_stale_temporaries(self) -> None:
        for candidate in self._root.glob(f"{_TEMP_PREFIX}*{_TEMP_SUFFIX}"):
            try:
                candidate.unlink()
            except FileNotFoundError:
                pass

    def _fsync_directory(self) -> None:
        flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        descriptor = os.open(self._root, flags)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

    def _persist_entry(
        self,
        *,
        entries: tuple[LedgerEntry, ...],
        kind: str,
        payload: Mapping[str, Any],
    ) -> LedgerEntry:
        actual_head = entries[-1].entry_hash if entries else None
        sequence = len(entries)
        prev_hash = actual_head if actual_head is not None else _GENESIS_HASH
        normalized = json.loads(canonical_bytes(payload))
        entry = LedgerEntry(
            sequence=sequence,
            kind=kind,
            payload=normalized,
            prev_hash=prev_hash,
            entry_hash=compute_entry_hash(sequence, kind, normalized, prev_hash),
        )
        encoded_entry = canonical_bytes(
            {
                "sequence": entry.sequence,
                "kind": entry.kind,
                "payload": entry.payload,
                "prev_hash": entry.prev_hash,
                "entry_hash": entry.entry_hash,
            }
        ) + b"\n"
        old_content = self._path.read_bytes()
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=self._root,
                prefix=_TEMP_PREFIX,
                suffix=_TEMP_SUFFIX,
                delete=False,
            ) as handle:
                temporary_path = Path(handle.name)
                handle.write(old_content)
                if old_content and not old_content.endswith(b"\n"):
                    handle.write(b"\n")
                handle.write(encoded_entry)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, self._path)
            temporary_path = None
            self._fsync_directory()
        finally:
            if temporary_path is not None:
                try:
                    temporary_path.unlink()
                except FileNotFoundError:
                    pass
        return entry

    @staticmethod
    def _check_head(
        entries: tuple[LedgerEntry, ...],
        expected_head: str | None | _ExpectedHeadUnset,
    ) -> None:
        actual_head = entries[-1].entry_hash if entries else None
        if (
            not isinstance(expected_head, _ExpectedHeadUnset)
            and expected_head != actual_head
        ):
            raise StaleLedgerHead(expected_head, actual_head)

    def append(
        self,
        kind: str,
        payload: Mapping[str, Any],
        *,
        expected_head: str | None | _ExpectedHeadUnset = _EXPECTED_HEAD_UNSET,
    ) -> LedgerEntry:
        """Atomically append one row.

        With ``expected_head`` given, the append is compare-and-swap: it
        succeeds only if the current head matches (``None`` matches an empty
        ledger and nothing else). Omitted, the append is unconditional.
        """

        kind = _require_kind(kind)
        if not isinstance(payload, Mapping):
            raise ValueError("ledger payload must be a mapping")
        with self._exclusive_lock():
            self._cleanup_stale_temporaries()
            entries = self.entries()
            self._check_head(entries, expected_head)
            return self._persist_entry(entries=entries, kind=kind, payload=payload)

    @staticmethod
    def _transaction_id(entry: LedgerEntry) -> str:
        return str(entry.payload.get(_TRANSACTION_ID_FIELD, ""))

    def append_identified(
        self,
        kind: str,
        payload: Mapping[str, Any],
        *,
        transaction_id: str,
        expected_head: str | None | _ExpectedHeadUnset = _EXPECTED_HEAD_UNSET,
    ) -> LedgerEntry:
        """Atomically append one row identified by a caller-chosen transaction id.

        Under one writer lock: if a row with the same ``transaction_id`` and the
        same kind and canonical content already exists it is returned unchanged
        (idempotent replay); the same id with different content raises
        ``TransactionIdConflict``; only then is ``expected_head`` checked and
        the row persisted. The id is stored in the payload under
        ``"transaction_id"`` and must not disagree with a value already there.
        """

        kind = _require_kind(kind)
        if not isinstance(payload, Mapping):
            raise ValueError("ledger payload must be a mapping")
        if type(transaction_id) is not str or not transaction_id.strip():
            raise ValueError("transaction_id must be a nonblank string")
        declared = payload.get(_TRANSACTION_ID_FIELD, transaction_id)
        if declared != transaction_id:
            raise ValueError("payload transaction_id disagrees with the declared transaction_id")
        identified = {**dict(payload), _TRANSACTION_ID_FIELD: transaction_id}
        normalized_payload = json.loads(canonical_bytes(identified))
        with self._exclusive_lock():
            self._cleanup_stale_temporaries()
            entries = self.entries()

            for entry in entries:
                if self._transaction_id(entry) != transaction_id:
                    continue
                if entry.kind == kind and entry.payload == normalized_payload:
                    return entry
                raise TransactionIdConflict(
                    f"transaction id {transaction_id} already exists with different content"
                )

            self._check_head(entries, expected_head)
            return self._persist_entry(
                entries=entries, kind=kind, payload=normalized_payload
            )

    def verify(self) -> tuple[str, ...]:
        """Return integrity violations; empty means the local chain is intact."""

        try:
            self.entries()
        except LedgerIntegrityError as error:
            return (str(error),)
        return ()


__all__ = [
    "LedgerEntry",
    "LedgerIntegrityError",
    "LedgerStore",
    "StaleLedgerHead",
    "TransactionIdConflict",
    "canonical_bytes",
    "compute_entry_hash",
]

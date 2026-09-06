"""Classical, finite query-relative views; a donor calibration, NOT an OCM authority.

Uses ordinary dictionary encoding and packed integer IDs. A view preserves exactly
its supplied observation columns on one finite source snapshot. Columns may name
queries under registered revisions; omitting those columns loses that guarantee.
This does NOT prove lumpability, empirical truth or arbitrary future-revision safety.
The host must validate a view against trusted source data before registering it.
"""
from __future__ import annotations

from array import array
from dataclasses import dataclass, field
from hashlib import sha256
import json
import struct
from typing import Iterable, Sequence


class ViewRefusal(ValueError):
    pass


def _names(values: Iterable[str]) -> tuple[str, ...]:
    out = tuple(values)
    if not out or any(type(v) is not str or not v for v in out) or len(set(out)) != len(out):
        raise ValueError("observation names must be nonempty, unique strings")
    return out


def _row(values: Sequence[str], width: int) -> tuple[str, ...]:
    out = tuple(values)
    if len(out) != width or any(type(v) is not str for v in out):
        raise ValueError("each source row must contain one string per observation")
    return out


def _bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _feed(digest, value: object) -> None:
    data = _bytes(value)
    digest.update(struct.pack("<Q", len(data)))
    digest.update(data)


def _source_hasher(names: tuple[str, ...]):
    h = sha256(b"OCM_FINITE_OBSERVATIONS_V1\0")
    _feed(h, names)
    return h


@dataclass(frozen=True, slots=True)
class PackedView:
    source_digest: str
    observations: tuple[str, ...]
    signatures: tuple[tuple[str, ...], ...]
    code_width: int
    codes: bytes
    _header: bytes = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        names = _names(self.observations)
        sigs = tuple(_row(row, len(names)) for row in self.signatures)
        if not sigs or len(set(sigs)) != len(sigs):
            raise ValueError("nonempty unique signatures required")
        if type(self.code_width) is not int or self.code_width not in (1, 2, 4, 8):
            raise ValueError("unsupported code width")
        if type(self.codes) is not bytes or not self.codes or len(self.codes) % self.code_width:
            raise ValueError("codes must be nonempty whole-width immutable bytes")
        if type(self.source_digest) is not str or len(self.source_digest) != 64 or any(c not in "0123456789abcdef" for c in self.source_digest):
            raise ValueError("expected a lowercase SHA256 source binding")
        if any(code[0] >= len(sigs) for code in struct.iter_unpack(self.code_format, self.codes)):
            raise ValueError("code outside signature dictionary")
        object.__setattr__(self, "observations", names)
        object.__setattr__(self, "signatures", sigs)
        object.__setattr__(self, "_header", _bytes((self.source_digest, names, sigs, self.code_width)))

    @property
    def code_format(self) -> str:
        return {1: "<B", 2: "<H", 4: "<I", 8: "<Q"}[self.code_width]

    @property
    def row_count(self) -> int:
        return len(self.codes) // self.code_width

    def signature_at(self, row_id: int) -> tuple[str, ...]:
        if type(row_id) is not int or not 0 <= row_id < self.row_count:
            raise ViewRefusal("ROW_OUTSIDE_REGISTERED_SNAPSHOT")
        code = struct.unpack_from(self.code_format, self.codes, row_id * self.code_width)[0]
        return self.signatures[code]

    def answer(self, row_id: int, observation: str, *, current_source_digest: str) -> str:
        if current_source_digest != self.source_digest:
            raise ViewRefusal("STALE_SOURCE_REVALIDATION_REQUIRED")
        try:
            column = self.observations.index(observation)
        except ValueError:
            raise ViewRefusal("REFINE_REQUIRED") from None
        return self.signature_at(row_id)[column]

    @property
    def encoded_payload_bytes(self) -> int:
        # Exact size of this declared encoding, NOT Python heap/RSS or archive size.
        return 8 + len(self._header) + len(self.codes)

    def to_bytes(self) -> bytes:
        """Concrete payload encoding; source archive is deliberately not included."""
        return struct.pack("<Q", len(self._header)) + self._header + self.codes


def compile_view(rows: Iterable[Sequence[str]], observations: Iterable[str], retain: Iterable[str]) -> PackedView:
    """One-pass source intake; O(ND) source binding and O(Nm) projection.

    Ordinary dict encoding is the adopted parent. Temporary 64-bit codes cost
    8N bytes before final packing; the source and indexes are NOT free storage.
    No whole-source Python object graph is retained by the returned view.
    """
    names, selected = _names(observations), _names(retain)
    positions = {name: i for i, name in enumerate(names)}
    if any(name not in positions for name in selected):
        raise ValueError("unknown retained observation")
    columns = tuple(positions[name] for name in selected)
    digest = _source_hasher(names)
    dictionary: dict[tuple[str, ...], int] = {}
    signatures: list[tuple[str, ...]] = []
    codes = array("Q")
    for values in rows:
        row = _row(values, len(names))
        _feed(digest, row)
        sig = tuple(row[i] for i in columns)
        code = dictionary.get(sig)
        if code is None:
            code = len(signatures)
            dictionary[sig] = code
            signatures.append(sig)
        codes.append(code)
    if not codes:
        raise ValueError("empty source has no registered states")
    width = next(w for w in (1, 2, 4, 8) if len(signatures) <= 1 << (8 * w))
    packed = bytearray(len(codes) * width)
    fmt = {1: "<B", 2: "<H", 4: "<I", 8: "<Q"}[width]
    for i, code in enumerate(codes):
        struct.pack_into(fmt, packed, i * width, code)
    return PackedView(digest.hexdigest(), selected, tuple(signatures), width, bytes(packed))


def verify_view(rows: Iterable[Sequence[str]], observations: Iterable[str], view: PackedView) -> bool:
    """Independent source-vs-decoder check, not compiler replay or a proof oracle.

    Visits the COMPLETE supplied snapshot. A digest alone never proves a summary
    sufficient. Successful finite checking grants no authority outside this table.
    """
    names = _names(observations)
    if any(name not in names for name in view.observations):
        return False
    columns = tuple(names.index(name) for name in view.observations)
    digest = _source_hasher(names)
    count = 0
    for values in rows:
        row = _row(values, len(names))
        _feed(digest, row)
        if count >= view.row_count or view.signature_at(count) != tuple(row[i] for i in columns):
            return False
        count += 1
    return count == view.row_count and digest.hexdigest() == view.source_digest


def select_view(views: Iterable[PackedView], required: Iterable[str], *, current_source_digest: str) -> PackedView:
    """Least encoded-payload choice among current, host-validated scoped views.

    This is one explicit storage objective, NOT a latency/resource Pareto theorem.
    The host is responsible for prior verify_view() and trustworthy source identity.
    Candidates may be incomparable partitions; no universal hierarchy is assumed.
    """
    wanted = frozenset(_names(required))
    candidates = [v for v in views if v.source_digest == current_source_digest and wanted <= set(v.observations)]
    if not candidates:
        raise ViewRefusal("NO_AUTHORIZED_VIEW_REFINE_OR_REVALIDATE")
    return min(candidates, key=lambda v: (v.encoded_payload_bytes, v.observations))

"""Research packed physical field parent for G5.2 (issue #165).

Production ``ocm.kso.space.KnowledgeSpace`` remains the default Python-object
field. This module is a parallel parent: interned identifiers, columnar packed
atoms/edges, CSR incidence, version-bound indexes, copy-on-write / local
deltas, and immutable payload handles. Semantic APIs round-trip to the
reference KSO. Production adoption is a separate economics decision.
"""
from __future__ import annotations

import hashlib
import sys
from array import array
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Hashable, Iterable, Mapping, Sequence

from ocm.kso.ids import canonical_json
from ocm.kso.nogoods import NogoodSet, register_constraint_nogood
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace, TypedRejection
from ocm.kso.types import DEFAULT_REGISTRY, Authority, Scope, TypeRegistry
from ocm.kso.warrant import Liveness, WarrantProfile

_UINT32 = "I"
_UINT8 = "B"
_INT64 = "q"
_NONE_PAYLOAD = 0


def _array_nbytes(arr: array) -> int:
    return len(arr) * arr.itemsize


def _copy_array(arr: array) -> array:
    return array(arr.typecode, arr)


def _empty_uint32() -> array:
    return array(_UINT32)


def _empty_uint8() -> array:
    return array(_UINT8)


def _empty_int64() -> array:
    return array(_INT64)


def _u32(value: int) -> bytes:
    return int(value).to_bytes(4, "little", signed=False)


# --------------------------------------------------------------------------------------
# intern tables and immutable payload archive
# --------------------------------------------------------------------------------------


class InternTable:
    """Append-only dictionary: hashable key → stable uint32 handle."""

    __slots__ = ("_to_id", "_from_id")

    def __init__(self) -> None:
        self._to_id: dict[Hashable, int] = {}
        self._from_id: list[Hashable] = []

    def intern(self, key: Hashable) -> int:
        hid = self._to_id.get(key)
        if hid is None:
            hid = len(self._from_id)
            self._to_id[key] = hid
            self._from_id.append(key)
        return hid

    def lookup(self, hid: int) -> Hashable:
        return self._from_id[hid]

    def __len__(self) -> int:
        return len(self._from_id)

    def contains(self, key: Hashable) -> bool:
        return key in self._to_id

    def host_bytes(self) -> int:
        seen: set[int] = set()
        return deep_sizeof(self._to_id, seen) + deep_sizeof(self._from_id, seen)


class PayloadArchive:
    """Content-addressed immutable blobs. Handle 0 is None/empty."""

    __slots__ = ("_digest_to_handle", "_blobs")

    def __init__(self) -> None:
        self._digest_to_handle: dict[str, int] = {"": _NONE_PAYLOAD}
        self._blobs: list[bytes] = [b""]

    def put(self, data: bytes | str | None) -> int:
        if data is None:
            return _NONE_PAYLOAD
        raw = data.encode("utf-8") if isinstance(data, str) else bytes(data)
        if not raw:
            return _NONE_PAYLOAD
        digest = hashlib.sha256(raw).hexdigest()
        hid = self._digest_to_handle.get(digest)
        if hid is None:
            hid = len(self._blobs)
            self._blobs.append(raw)
            self._digest_to_handle[digest] = hid
        return hid

    def get(self, hid: int) -> bytes | None:
        if hid == _NONE_PAYLOAD:
            return None
        return self._blobs[hid]

    def get_text(self, hid: int) -> str | None:
        raw = self.get(hid)
        if raw is None:
            return None
        return raw.decode("utf-8")

    def __len__(self) -> int:
        return len(self._blobs)

    def blob_bytes(self) -> int:
        return sum(len(blob) for blob in self._blobs)

    def host_bytes(self) -> int:
        seen: set[int] = set()
        return deep_sizeof(self._digest_to_handle, seen) + deep_sizeof(self._blobs, seen)


class InternBundle:
    """Shared intern pool for a COW lineage. Append-only; never cloned on edit."""

    __slots__ = (
        "atom_ids",
        "edge_ids",
        "types",
        "relations",
        "scope_tags",
        "authority_coords",
        "scopes",
        "authorities",
        "evidence",
        "warrants",
        "warrant_objs",
        "fractions",
        "payloads",
    )

    def __init__(self) -> None:
        self.atom_ids = InternTable()
        self.edge_ids = InternTable()
        self.types = InternTable()
        self.relations = InternTable()
        self.scope_tags = InternTable()
        self.authority_coords = InternTable()
        self.scopes = InternTable()
        self.authorities = InternTable()
        self.evidence = InternTable()
        self.warrants = InternTable()
        self.warrant_objs: list[WarrantProfile] = []
        self.fractions = InternTable()
        self.payloads = PayloadArchive()

    def intern_type(self, name: str) -> int:
        return self.types.intern(name)

    def intern_relation(self, name: str) -> int:
        return self.relations.intern(name)

    def intern_scope(self, scope: Scope) -> int:
        if scope.contexts is None:
            ctx_key: tuple[int, ...] | None = None
        else:
            ctx_key = tuple(sorted(self.scope_tags.intern(tag) for tag in scope.contexts))
        epoch = scope.epoch
        return self.scopes.intern((ctx_key, epoch))

    def lookup_scope(self, hid: int) -> Scope:
        ctx_key, epoch = self.scopes.lookup(hid)  # type: ignore[misc]
        if ctx_key is None:
            return Scope(None, epoch)
        tags = frozenset(str(self.scope_tags.lookup(i)) for i in ctx_key)
        return Scope(tags, epoch)

    def intern_authority(self, authority: Authority) -> int:
        ranks = tuple((self.authority_coords.intern(k), int(v)) for k, v in authority.ranks)
        return self.authorities.intern(ranks)

    def lookup_authority(self, hid: int) -> Authority:
        ranks = self.authorities.lookup(hid)  # type: ignore[misc]
        return Authority(tuple((str(self.authority_coords.lookup(k)), v) for k, v in ranks))

    def intern_warrant(self, wp: WarrantProfile) -> int:
        def intern_profile(profile: tuple[frozenset, ...]) -> tuple[tuple[int, ...], ...]:
            warrants = []
            for warrant in profile:
                ev = tuple(sorted(self.evidence.intern(item) for item in warrant))
                warrants.append(ev)
            return tuple(sorted(warrants))

        key = (intern_profile(wp.lower), intern_profile(wp.upper))
        hid = self.warrants._to_id.get(key)
        if hid is None:
            hid = self.warrants.intern(key)
            assert hid == len(self.warrant_objs)
            self.warrant_objs.append(wp)
        return hid

    def lookup_warrant(self, hid: int) -> WarrantProfile:
        return self.warrant_objs[hid]

    def intern_fraction(self, value: Fraction) -> int:
        return self.fractions.intern(Fraction(value))

    def lookup_fraction(self, hid: int) -> Fraction:
        return Fraction(self.fractions.lookup(hid))  # type: ignore[arg-type]

    def intern_meta(self, meta: Sequence[tuple[str, Any]]) -> int:
        if not meta:
            return _NONE_PAYLOAD
        payload = canonical_json([[k, v] for k, v in meta])
        return self.payloads.put(payload)

    def lookup_meta(self, hid: int) -> tuple[tuple[str, Any], ...]:
        text = self.payloads.get_text(hid)
        if text is None:
            return ()
        pairs = __import__("json").loads(text)
        return tuple((str(k), v) for k, v in pairs)

    def intern_content_ref(self, ref: str | None) -> int:
        return self.payloads.put(ref)

    def lookup_content_ref(self, hid: int) -> str | None:
        return self.payloads.get_text(hid)

    def host_bytes(self) -> int:
        total = 0
        for name in (
            "atom_ids",
            "edge_ids",
            "types",
            "relations",
            "scope_tags",
            "authority_coords",
            "scopes",
            "authorities",
            "evidence",
            "warrants",
            "fractions",
        ):
            total += getattr(self, name).host_bytes()
        total += self.payloads.host_bytes()
        seen: set[int] = set()
        total += deep_sizeof(self.warrant_objs, seen)
        return total

    def payload_blob_bytes(self) -> int:
        return self.payloads.blob_bytes()


# --------------------------------------------------------------------------------------
# packed columns, deltas, version-bound indexes
# --------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AtomPatch:
    slot: int
    id_handle: int
    type_id: int
    epoch: int
    quarantined: int
    content_ref: int
    warrant_handle: int
    authority_handle: int
    scope_handle: int
    meta_handle: int
    row_digest: bytes


@dataclass(frozen=True)
class BoundIndexes:
    """Incidence CSR, id maps and type bitmaps bound to a space version."""

    version: int
    n_atoms: int
    n_edges: int
    atom_id_to_slot: dict[int, int]
    edge_id_to_slot: dict[int, int]
    type_bitmaps: dict[int, bytearray]
    incident_ptr: array
    incident_idx: array
    outgoing_ptr: array
    outgoing_idx: array
    build_touches: int = 0
    patched: bool = False

    def usable_for(self, version: int, n_atoms: int, n_edges: int) -> bool:
        return self.version == version and self.n_atoms == n_atoms and self.n_edges == n_edges

    def bytes(self) -> int:
        seen: set[int] = set()
        total = sys.getsizeof(self.atom_id_to_slot) + sys.getsizeof(self.edge_id_to_slot)
        total += sys.getsizeof(self.type_bitmaps)
        total += _array_nbytes(self.incident_ptr) + _array_nbytes(self.incident_idx)
        total += _array_nbytes(self.outgoing_ptr) + _array_nbytes(self.outgoing_idx)
        for bitmap in self.type_bitmaps.values():
            total += len(bitmap)
        total += deep_sizeof(self.atom_id_to_slot, seen) - sys.getsizeof(self.atom_id_to_slot)
        return total


@dataclass(frozen=True, slots=True)
class ScanCost:
    method: str
    units_touched: int
    hits: int
    wall_s: float
    atom_ids: tuple[str, ...]


def _bitmap_nbytes(n: int) -> int:
    return (n + 7) // 8 if n else 0


def _bitmap_set(bits: bytearray, i: int) -> None:
    bits[i >> 3] |= 1 << (i & 7)


def _bitmap_clear(bits: bytearray, i: int) -> None:
    bits[i >> 3] &= ~(1 << (i & 7))


def _bitmap_scan(bits: bytearray, n: int) -> tuple[list[int], int]:
    out: list[int] = []
    bytes_read = 0
    for byte_i, byte in enumerate(bits):
        bytes_read += 1
        if not byte:
            continue
        base = byte_i * 8
        for bit in range(8):
            if byte & (1 << bit):
                idx = base + bit
                if idx < n:
                    out.append(idx)
    return out, bytes_read


def _prefix(degrees: list[int]) -> array:
    ptr = array(_UINT32, [0]) * (len(degrees) + 1)
    running = 0
    for i, deg in enumerate(degrees):
        ptr[i] = running
        running += deg
    ptr[len(degrees)] = running
    return ptr


# --------------------------------------------------------------------------------------
# packed space
# --------------------------------------------------------------------------------------


class PackedKnowledgeSpace:
    """Columnar COW knowledge space with interned identifiers and versioned indexes."""

    __slots__ = (
        "intern",
        "registry",
        "version",
        "n_atoms",
        "n_edges",
        "atom_id_handles",
        "atom_type_ids",
        "atom_epochs",
        "atom_quarantined",
        "atom_content_refs",
        "atom_warrant_handles",
        "atom_authority_handles",
        "atom_scope_handles",
        "atom_meta_handles",
        "atom_row_digests",
        "edge_id_handles",
        "edge_relation_ids",
        "edge_weight_handles",
        "edge_warrant_handles",
        "edge_authority_handles",
        "edge_scope_handles",
        "edge_exec_refs",
        "edge_meta_handles",
        "edge_row_digests",
        "tail_ptr",
        "tail_idx",
        "head_ptr",
        "head_idx",
        "head_weight_ptr",
        "head_weight_idx",
        "atom_deltas",
        "_indexes",
        "_incremental_identity",
    )

    def __init__(
        self,
        intern: InternBundle,
        *,
        registry: TypeRegistry,
        version: int,
        n_atoms: int,
        n_edges: int,
        atom_id_handles: array,
        atom_type_ids: array,
        atom_epochs: array,
        atom_quarantined: array,
        atom_content_refs: array,
        atom_warrant_handles: array,
        atom_authority_handles: array,
        atom_scope_handles: array,
        atom_meta_handles: array,
        atom_row_digests: list[bytes],
        edge_id_handles: array,
        edge_relation_ids: array,
        edge_weight_handles: array,
        edge_warrant_handles: array,
        edge_authority_handles: array,
        edge_scope_handles: array,
        edge_exec_refs: array,
        edge_meta_handles: array,
        edge_row_digests: list[bytes],
        tail_ptr: array,
        tail_idx: array,
        head_ptr: array,
        head_idx: array,
        head_weight_ptr: array,
        head_weight_idx: array,
        atom_deltas: Mapping[int, AtomPatch] | None = None,
        indexes: BoundIndexes | None = None,
    ) -> None:
        self.intern = intern
        self.registry = registry
        self.version = version
        self.n_atoms = n_atoms
        self.n_edges = n_edges
        self.atom_id_handles = atom_id_handles
        self.atom_type_ids = atom_type_ids
        self.atom_epochs = atom_epochs
        self.atom_quarantined = atom_quarantined
        self.atom_content_refs = atom_content_refs
        self.atom_warrant_handles = atom_warrant_handles
        self.atom_authority_handles = atom_authority_handles
        self.atom_scope_handles = atom_scope_handles
        self.atom_meta_handles = atom_meta_handles
        self.atom_row_digests = atom_row_digests
        self.edge_id_handles = edge_id_handles
        self.edge_relation_ids = edge_relation_ids
        self.edge_weight_handles = edge_weight_handles
        self.edge_warrant_handles = edge_warrant_handles
        self.edge_authority_handles = edge_authority_handles
        self.edge_scope_handles = edge_scope_handles
        self.edge_exec_refs = edge_exec_refs
        self.edge_meta_handles = edge_meta_handles
        self.edge_row_digests = edge_row_digests
        self.tail_ptr = tail_ptr
        self.tail_idx = tail_idx
        self.head_ptr = head_ptr
        self.head_idx = head_idx
        self.head_weight_ptr = head_weight_ptr
        self.head_weight_idx = head_weight_idx
        self.atom_deltas = dict(atom_deltas) if atom_deltas else {}
        self._indexes = indexes
        self._incremental_identity: str | None = None
        self.validate()

    # --- construction -----------------------------------------------------------------
    @classmethod
    def empty(cls, registry: TypeRegistry = DEFAULT_REGISTRY) -> "PackedKnowledgeSpace":
        intern = InternBundle()
        return cls(
            intern,
            registry=registry,
            version=1,
            n_atoms=0,
            n_edges=0,
            atom_id_handles=_empty_uint32(),
            atom_type_ids=_empty_uint32(),
            atom_epochs=_empty_int64(),
            atom_quarantined=_empty_uint8(),
            atom_content_refs=_empty_uint32(),
            atom_warrant_handles=_empty_uint32(),
            atom_authority_handles=_empty_uint32(),
            atom_scope_handles=_empty_uint32(),
            atom_meta_handles=_empty_uint32(),
            atom_row_digests=[],
            edge_id_handles=_empty_uint32(),
            edge_relation_ids=_empty_uint32(),
            edge_weight_handles=_empty_uint32(),
            edge_warrant_handles=_empty_uint32(),
            edge_authority_handles=_empty_uint32(),
            edge_scope_handles=_empty_uint32(),
            edge_exec_refs=_empty_uint32(),
            edge_meta_handles=_empty_uint32(),
            edge_row_digests=[],
            tail_ptr=array(_UINT32, [0]),
            tail_idx=_empty_uint32(),
            head_ptr=array(_UINT32, [0]),
            head_idx=_empty_uint32(),
            head_weight_ptr=array(_UINT32, [0]),
            head_weight_idx=_empty_uint32(),
        )

    @classmethod
    def from_reference(cls, ks: KnowledgeSpace) -> "PackedKnowledgeSpace":
        intern = InternBundle()
        n_atoms = len(ks.atoms)
        n_edges = len(ks.hyperedges)
        atom_id_handles = array(_UINT32, [0]) * n_atoms
        atom_type_ids = array(_UINT32, [0]) * n_atoms
        atom_epochs = array(_INT64, [0]) * n_atoms
        atom_quarantined = array(_UINT8, [0]) * n_atoms
        atom_content_refs = array(_UINT32, [0]) * n_atoms
        atom_warrant_handles = array(_UINT32, [0]) * n_atoms
        atom_authority_handles = array(_UINT32, [0]) * n_atoms
        atom_scope_handles = array(_UINT32, [0]) * n_atoms
        atom_meta_handles = array(_UINT32, [0]) * n_atoms
        atom_row_digests: list[bytes] = [b""] * n_atoms
        id_to_slot: dict[str, int] = {}
        for slot, atom in enumerate(ks.atoms):
            id_handle = intern.atom_ids.intern(atom.atom_id)
            type_id = intern.intern_type(atom.atom_type)
            content_ref = intern.intern_content_ref(atom.content_ref)
            warrant_handle = intern.intern_warrant(atom.warrant)
            authority_handle = intern.intern_authority(atom.authority)
            scope_handle = intern.intern_scope(atom.scope)
            meta_handle = intern.intern_meta(atom.meta)
            atom_id_handles[slot] = id_handle
            atom_type_ids[slot] = type_id
            atom_epochs[slot] = int(atom.epoch)
            atom_quarantined[slot] = 1 if atom.quarantined else 0
            atom_content_refs[slot] = content_ref
            atom_warrant_handles[slot] = warrant_handle
            atom_authority_handles[slot] = authority_handle
            atom_scope_handles[slot] = scope_handle
            atom_meta_handles[slot] = meta_handle
            atom_row_digests[slot] = _semantic_atom_digest(atom)
            id_to_slot[atom.atom_id] = slot

        edge_id_handles = array(_UINT32, [0]) * n_edges
        edge_relation_ids = array(_UINT32, [0]) * n_edges
        edge_weight_handles = array(_UINT32, [0]) * n_edges
        edge_warrant_handles = array(_UINT32, [0]) * n_edges
        edge_authority_handles = array(_UINT32, [0]) * n_edges
        edge_scope_handles = array(_UINT32, [0]) * n_edges
        edge_exec_refs = array(_UINT32, [0]) * n_edges
        edge_meta_handles = array(_UINT32, [0]) * n_edges
        edge_row_digests: list[bytes] = [b""] * n_edges
        tail_idx = _empty_uint32()
        head_idx = _empty_uint32()
        head_weight_idx = _empty_uint32()
        tail_ptr = array(_UINT32, [0]) * (n_edges + 1)
        head_ptr = array(_UINT32, [0]) * (n_edges + 1)
        head_weight_ptr = array(_UINT32, [0]) * (n_edges + 1)
        for slot, edge in enumerate(ks.hyperedges):
            tail_ptr[slot] = len(tail_idx)
            for atom_id in edge.tails:
                tail_idx.append(id_to_slot[atom_id])
            head_ptr[slot] = len(head_idx)
            for atom_id in edge.heads:
                head_idx.append(id_to_slot[atom_id])
            head_weight_ptr[slot] = len(head_weight_idx)
            for weight in edge.head_weights:
                head_weight_idx.append(intern.intern_fraction(weight))
            id_handle = intern.edge_ids.intern(edge.edge_id)
            relation_id = intern.intern_relation(edge.relation_type)
            weight_handle = intern.intern_fraction(edge.weight)
            warrant_handle = intern.intern_warrant(edge.warrant)
            authority_handle = intern.intern_authority(edge.authority)
            scope_handle = intern.intern_scope(edge.scope)
            exec_ref = intern.intern_content_ref(edge.executable_ref)
            meta_handle = intern.intern_meta(edge.meta)
            edge_id_handles[slot] = id_handle
            edge_relation_ids[slot] = relation_id
            edge_weight_handles[slot] = weight_handle
            edge_warrant_handles[slot] = warrant_handle
            edge_authority_handles[slot] = authority_handle
            edge_scope_handles[slot] = scope_handle
            edge_exec_refs[slot] = exec_ref
            edge_meta_handles[slot] = meta_handle
            edge_row_digests[slot] = _semantic_edge_digest(edge)
        tail_ptr[n_edges] = len(tail_idx)
        head_ptr[n_edges] = len(head_idx)
        head_weight_ptr[n_edges] = len(head_weight_idx)
        packed = cls(
            intern,
            registry=ks.registry,
            version=1,
            n_atoms=n_atoms,
            n_edges=n_edges,
            atom_id_handles=atom_id_handles,
            atom_type_ids=atom_type_ids,
            atom_epochs=atom_epochs,
            atom_quarantined=atom_quarantined,
            atom_content_refs=atom_content_refs,
            atom_warrant_handles=atom_warrant_handles,
            atom_authority_handles=atom_authority_handles,
            atom_scope_handles=atom_scope_handles,
            atom_meta_handles=atom_meta_handles,
            atom_row_digests=atom_row_digests,
            edge_id_handles=edge_id_handles,
            edge_relation_ids=edge_relation_ids,
            edge_weight_handles=edge_weight_handles,
            edge_warrant_handles=edge_warrant_handles,
            edge_authority_handles=edge_authority_handles,
            edge_scope_handles=edge_scope_handles,
            edge_exec_refs=edge_exec_refs,
            edge_meta_handles=edge_meta_handles,
            edge_row_digests=edge_row_digests,
            tail_ptr=tail_ptr,
            tail_idx=tail_idx,
            head_ptr=head_ptr,
            head_idx=head_idx,
            head_weight_ptr=head_weight_ptr,
            head_weight_idx=head_weight_idx,
        )
        packed._indexes = packed._rebuild_indexes(patched=False)
        return packed

    def to_reference(self) -> KnowledgeSpace:
        atoms = tuple(self.materialize_atom_at(slot) for slot in range(self.n_atoms))
        edges = tuple(self.materialize_edge_at(slot) for slot in range(self.n_edges))
        return KnowledgeSpace(atoms, edges, self.registry)

    # --- column readers (delta overlay) ------------------------------------------------
    def _atom_id_handle(self, slot: int) -> int:
        patch = self.atom_deltas.get(slot)
        return patch.id_handle if patch else self.atom_id_handles[slot]

    def _atom_type_id(self, slot: int) -> int:
        patch = self.atom_deltas.get(slot)
        return patch.type_id if patch else self.atom_type_ids[slot]

    def _atom_epoch(self, slot: int) -> int:
        patch = self.atom_deltas.get(slot)
        return patch.epoch if patch else int(self.atom_epochs[slot])

    def _atom_quarantined(self, slot: int) -> int:
        patch = self.atom_deltas.get(slot)
        return patch.quarantined if patch else int(self.atom_quarantined[slot])

    def _atom_content_ref(self, slot: int) -> int:
        patch = self.atom_deltas.get(slot)
        return patch.content_ref if patch else self.atom_content_refs[slot]

    def _atom_warrant_handle(self, slot: int) -> int:
        patch = self.atom_deltas.get(slot)
        return patch.warrant_handle if patch else self.atom_warrant_handles[slot]

    def _atom_authority_handle(self, slot: int) -> int:
        patch = self.atom_deltas.get(slot)
        return patch.authority_handle if patch else self.atom_authority_handles[slot]

    def _atom_scope_handle(self, slot: int) -> int:
        patch = self.atom_deltas.get(slot)
        return patch.scope_handle if patch else self.atom_scope_handles[slot]

    def _atom_meta_handle(self, slot: int) -> int:
        patch = self.atom_deltas.get(slot)
        return patch.meta_handle if patch else self.atom_meta_handles[slot]

    def _atom_digest_at(self, slot: int) -> bytes:
        patch = self.atom_deltas.get(slot)
        return patch.row_digest if patch else self.atom_row_digests[slot]

    def handle_of(self, atom_id: str) -> int:
        if not self.intern.atom_ids.contains(atom_id):
            raise TypedRejection("UNKNOWN_ATOM", atom_id)
        return int(self.intern.atom_ids._to_id[atom_id])

    def slot_of(self, atom_id: str) -> int:
        indexes = self.indexes()
        hid = self.handle_of(atom_id)
        try:
            return indexes.atom_id_to_slot[hid]
        except KeyError:
            raise TypedRejection("UNKNOWN_ATOM", atom_id) from None

    def materialize_atom_at(self, slot: int) -> Atom:
        intern = self.intern
        return Atom(
            str(intern.atom_ids.lookup(self._atom_id_handle(slot))),
            str(intern.types.lookup(self._atom_type_id(slot))),
            intern.lookup_warrant(self._atom_warrant_handle(slot)),
            intern.lookup_authority(self._atom_authority_handle(slot)),
            intern.lookup_scope(self._atom_scope_handle(slot)),
            self._atom_epoch(slot),
            bool(self._atom_quarantined(slot)),
            intern.lookup_content_ref(self._atom_content_ref(slot)),
            intern.lookup_meta(self._atom_meta_handle(slot)),
        )

    def materialize_edge_at(self, slot: int) -> Hyperedge:
        intern = self.intern
        tails = tuple(
            str(intern.atom_ids.lookup(self._atom_id_handle(atom_slot)))
            for atom_slot in self.tail_idx[self.tail_ptr[slot] : self.tail_ptr[slot + 1]]
        )
        heads = tuple(
            str(intern.atom_ids.lookup(self._atom_id_handle(atom_slot)))
            for atom_slot in self.head_idx[self.head_ptr[slot] : self.head_ptr[slot + 1]]
        )
        weights = tuple(
            intern.lookup_fraction(hid)
            for hid in self.head_weight_idx[self.head_weight_ptr[slot] : self.head_weight_ptr[slot + 1]]
        )
        return Hyperedge(
            str(intern.edge_ids.lookup(self.edge_id_handles[slot])),
            tails,
            heads,
            str(intern.relations.lookup(self.edge_relation_ids[slot])),
            intern.lookup_fraction(self.edge_weight_handles[slot]),
            weights,
            intern.lookup_warrant(self.edge_warrant_handles[slot]),
            intern.lookup_authority(self.edge_authority_handles[slot]),
            intern.lookup_scope(self.edge_scope_handles[slot]),
            intern.lookup_content_ref(self.edge_exec_refs[slot]),
            intern.lookup_meta(self.edge_meta_handles[slot]),
        )

    def atom(self, atom_id: str) -> Atom:
        return self.materialize_atom_at(self.slot_of(atom_id))

    # --- validation / identity ---------------------------------------------------------
    def validate(self) -> None:
        id_handles = [self._atom_id_handle(slot) for slot in range(self.n_atoms)]
        if len(set(id_handles)) != len(id_handles):
            raise ValueError("duplicate atom id")
        edge_ids = list(self.edge_id_handles)
        if len(set(edge_ids)) != len(edge_ids):
            raise ValueError("duplicate edge id")
        known = set(range(self.n_atoms))
        for slot in range(self.n_atoms):
            self.registry.require_atom_type(str(self.intern.types.lookup(self._atom_type_id(slot))))
        for slot in range(self.n_edges):
            for atom_slot in (*self.tail_idx[self.tail_ptr[slot] : self.tail_ptr[slot + 1]], *self.head_idx[self.head_ptr[slot] : self.head_ptr[slot + 1]]):
                if int(atom_slot) not in known:
                    raise ValueError(f"hyperedge {self.intern.edge_ids.lookup(self.edge_id_handles[slot])} references an unknown atom")
            self.registry.require_relation_type(str(self.intern.relations.lookup(self.edge_relation_ids[slot])))

    def digest(self) -> str:
        return self.to_reference().digest()

    def incremental_identity(self) -> str:
        if self._incremental_identity is None:
            h = hashlib.sha256()
            h.update(_u32(self.n_atoms))
            h.update(_u32(self.n_edges))
            for slot in range(self.n_atoms):
                h.update(self._atom_digest_at(slot))
            for digest in self.edge_row_digests:
                h.update(digest)
            self._incremental_identity = h.hexdigest()
        return self._incremental_identity

    # --- indexes ----------------------------------------------------------------------
    def indexes(self) -> BoundIndexes:
        current = self._indexes
        if current is not None and current.usable_for(self.version, self.n_atoms, self.n_edges):
            return current
        rebuilt = self._rebuild_indexes(patched=False)
        self._indexes = rebuilt
        return rebuilt

    def _rebuild_indexes(self, *, patched: bool) -> BoundIndexes:
        touches = 0
        atom_id_to_slot: dict[int, int] = {}
        type_bitmaps: dict[int, bytearray] = {}
        nbytes = _bitmap_nbytes(self.n_atoms)
        for slot in range(self.n_atoms):
            touches += 1
            hid = self._atom_id_handle(slot)
            atom_id_to_slot[hid] = slot
            type_id = self._atom_type_id(slot)
            bits = type_bitmaps.get(type_id)
            if bits is None:
                bits = bytearray(nbytes)
                type_bitmaps[type_id] = bits
            if nbytes:
                _bitmap_set(bits, slot)
        edge_id_to_slot = {int(self.edge_id_handles[slot]): slot for slot in range(self.n_edges)}
        touches += self.n_edges
        incident_deg = [0] * self.n_atoms
        outgoing_deg = [0] * self.n_atoms
        for slot in range(self.n_edges):
            for tail in self.tail_idx[self.tail_ptr[slot] : self.tail_ptr[slot + 1]]:
                outgoing_deg[int(tail)] += 1
                incident_deg[int(tail)] += 1
                touches += 1
            for head in self.head_idx[self.head_ptr[slot] : self.head_ptr[slot + 1]]:
                incident_deg[int(head)] += 1
                touches += 1
        incident_ptr = _prefix(incident_deg)
        outgoing_ptr = _prefix(outgoing_deg)
        incident_idx = array(_UINT32, [0]) * int(incident_ptr[-1]) if self.n_atoms else _empty_uint32()
        outgoing_idx = array(_UINT32, [0]) * int(outgoing_ptr[-1]) if self.n_atoms else _empty_uint32()
        incident_fill = list(incident_ptr)
        outgoing_fill = list(outgoing_ptr)
        for slot in range(self.n_edges):
            for tail in self.tail_idx[self.tail_ptr[slot] : self.tail_ptr[slot + 1]]:
                t = int(tail)
                outgoing_idx[outgoing_fill[t]] = slot
                outgoing_fill[t] += 1
                incident_idx[incident_fill[t]] = slot
                incident_fill[t] += 1
            for head in self.head_idx[self.head_ptr[slot] : self.head_ptr[slot + 1]]:
                h = int(head)
                incident_idx[incident_fill[h]] = slot
                incident_fill[h] += 1
        return BoundIndexes(
            version=self.version,
            n_atoms=self.n_atoms,
            n_edges=self.n_edges,
            atom_id_to_slot=atom_id_to_slot,
            edge_id_to_slot=edge_id_to_slot,
            type_bitmaps=type_bitmaps,
            incident_ptr=incident_ptr,
            incident_idx=incident_idx,
            outgoing_ptr=outgoing_ptr,
            outgoing_idx=outgoing_idx,
            build_touches=touches,
            patched=patched,
        )

    def _patch_indexes_atom_replace(self, base: BoundIndexes, patch: AtomPatch, old_type: int) -> BoundIndexes:
        atom_id_to_slot = dict(base.atom_id_to_slot)
        type_bitmaps = {tid: bytearray(bits) for tid, bits in base.type_bitmaps.items()}
        if old_type != patch.type_id:
            old_bits = type_bitmaps.get(old_type)
            if old_bits is not None:
                _bitmap_clear(old_bits, patch.slot)
            new_bits = type_bitmaps.get(patch.type_id)
            if new_bits is None:
                new_bits = bytearray(_bitmap_nbytes(self.n_atoms))
                type_bitmaps[patch.type_id] = new_bits
            if new_bits:
                _bitmap_set(new_bits, patch.slot)
        atom_id_to_slot[patch.id_handle] = patch.slot
        return BoundIndexes(
            version=self.version,
            n_atoms=self.n_atoms,
            n_edges=self.n_edges,
            atom_id_to_slot=atom_id_to_slot,
            edge_id_to_slot=base.edge_id_to_slot,
            type_bitmaps=type_bitmaps,
            incident_ptr=base.incident_ptr,
            incident_idx=base.incident_idx,
            outgoing_ptr=base.outgoing_ptr,
            outgoing_idx=base.outgoing_idx,
            build_touches=1,
            patched=True,
        )

    def incident_edges(self, atom_id: str) -> tuple[Hyperedge, ...]:
        indexes = self.indexes()
        slot = self.slot_of(atom_id)
        start, end = int(indexes.incident_ptr[slot]), int(indexes.incident_ptr[slot + 1])
        return tuple(self.materialize_edge_at(int(indexes.incident_idx[i])) for i in range(start, end))

    def outgoing_edges(self, atom_id: str) -> tuple[Hyperedge, ...]:
        indexes = self.indexes()
        slot = self.slot_of(atom_id)
        start, end = int(indexes.outgoing_ptr[slot]), int(indexes.outgoing_ptr[slot + 1])
        return tuple(self.materialize_edge_at(int(indexes.outgoing_idx[i])) for i in range(start, end))

    def atoms_of_type(self, atom_type: str, *, method: str = "bitmap") -> ScanCost:
        import time

        type_id = self.intern.types._to_id.get(atom_type)
        t0 = time.perf_counter()
        if method == "linear":
            slots: list[int] = []
            for slot in range(self.n_atoms):
                if self._atom_type_id(slot) == type_id:
                    slots.append(slot)
            units = self.n_atoms
        elif method == "bitmap":
            if type_id is None:
                slots, units = [], 0
            else:
                indexes = self.indexes()
                bits = indexes.type_bitmaps.get(type_id)
                if bits is None:
                    slots, units = [], 0
                else:
                    slots, units = _bitmap_scan(bits, self.n_atoms)
        else:
            raise ValueError(method)
        wall = time.perf_counter() - t0
        atom_ids = tuple(str(self.intern.atom_ids.lookup(self._atom_id_handle(slot))) for slot in slots)
        return ScanCost(method, units, len(slots), wall, atom_ids)

    # --- liveness / nogoods ------------------------------------------------------------
    def live_atoms(self, revoked: Iterable[Hashable] = ()) -> frozenset[str]:
        rv = frozenset(revoked)
        intern = self.intern
        return frozenset(
            str(intern.atom_ids.lookup(self._atom_id_handle(slot)))
            for slot in range(self.n_atoms)
            if intern.lookup_warrant(self._atom_warrant_handle(slot)).is_live(rv)
        )

    def dead_atoms(self, revoked: Iterable[Hashable] = ()) -> frozenset[str]:
        rv = frozenset(revoked)
        intern = self.intern
        return frozenset(
            str(intern.atom_ids.lookup(self._atom_id_handle(slot)))
            for slot in range(self.n_atoms)
            if intern.lookup_warrant(self._atom_warrant_handle(slot)).liveness(rv) is Liveness.DEAD
        )

    def unknown_atoms(self, revoked: Iterable[Hashable] = ()) -> frozenset[str]:
        rv = frozenset(revoked)
        intern = self.intern
        return frozenset(
            str(intern.atom_ids.lookup(self._atom_id_handle(slot)))
            for slot in range(self.n_atoms)
            if intern.lookup_warrant(self._atom_warrant_handle(slot)).liveness(rv) is Liveness.UNKNOWN
        )

    def edge_enabled_liveness(self, edge: Hyperedge | str | int, revoked: Iterable[Hashable] = ()) -> Liveness:
        from ocm.kso.warrant import kleene_and as _and

        rv = frozenset(revoked)
        if isinstance(edge, Hyperedge):
            materialized = edge
        elif isinstance(edge, str):
            hid = self.intern.edge_ids._to_id.get(edge)
            if hid is None:
                raise TypedRejection("UNKNOWN_EDGE", edge)
            slot = self.indexes().edge_id_to_slot[hid]
            materialized = self.materialize_edge_at(slot)
        else:
            materialized = self.materialize_edge_at(int(edge))
        out = materialized.liveness(rv)
        for atom_id in (*materialized.tails, *materialized.heads):
            out = _and(out, self.atom(atom_id).liveness(rv))
        return out

    def evidence_universe(self) -> frozenset:
        ev: set = set()
        intern = self.intern
        for slot in range(self.n_atoms):
            ev |= intern.lookup_warrant(self._atom_warrant_handle(slot)).evidence
        for slot in range(self.n_edges):
            ev |= intern.lookup_warrant(self.edge_warrant_handles[slot]).evidence
        return frozenset(ev)

    def constraint_nogoods(self) -> NogoodSet:
        """Register nogoods from CONSTRAINT edges (MEG-16(iv) parent, if easy)."""
        nogoods = NogoodSet()
        constraint_id = self.intern.relations._to_id.get("CONSTRAINT")
        if constraint_id is None:
            return nogoods
        for slot in range(self.n_edges):
            if int(self.edge_relation_ids[slot]) != constraint_id:
                continue
            incident = [
                *self.tail_idx[self.tail_ptr[slot] : self.tail_ptr[slot + 1]],
                *self.head_idx[self.head_ptr[slot] : self.head_ptr[slot + 1]],
            ]
            if len(incident) < 2:
                continue
            left = self.intern.lookup_warrant(self._atom_warrant_handle(int(incident[0])))
            right = self.intern.lookup_warrant(self._atom_warrant_handle(int(incident[1])))
            extra = register_constraint_nogood(left, right)
            for nogood in extra.nogoods:
                nogoods = nogoods.add(nogood)
        return nogoods

    def filtered_liveness(self, atom_id: str, revoked: Iterable[Hashable], nogoods: NogoodSet) -> Liveness:
        return nogoods.liveness(self.atom(atom_id).warrant, revoked)

    # --- persistent edits (COW) --------------------------------------------------------
    def _clone(
        self,
        *,
        version: int | None = None,
        n_atoms: int | None = None,
        n_edges: int | None = None,
        copy_atom_columns: bool = False,
        copy_edge_columns: bool = False,
        atom_deltas: Mapping[int, AtomPatch] | None = None,
        indexes: BoundIndexes | None = None,
        **overrides: Any,
    ) -> "PackedKnowledgeSpace":
        def atom_col(name: str) -> Any:
            if name in overrides:
                return overrides[name]
            value = getattr(self, name)
            if copy_atom_columns and name.startswith("atom_"):
                return list(value) if name == "atom_row_digests" else _copy_array(value)
            return value

        def edge_col(name: str) -> Any:
            if name in overrides:
                return overrides[name]
            value = getattr(self, name)
            if copy_edge_columns and (name.startswith("edge_") or name in {"tail_ptr", "tail_idx", "head_ptr", "head_idx", "head_weight_ptr", "head_weight_idx"}):
                return list(value) if name == "edge_row_digests" else _copy_array(value)
            return value

        return PackedKnowledgeSpace(
            self.intern,
            registry=self.registry,
            version=self.version + 1 if version is None else version,
            n_atoms=self.n_atoms if n_atoms is None else n_atoms,
            n_edges=self.n_edges if n_edges is None else n_edges,
            atom_id_handles=atom_col("atom_id_handles"),
            atom_type_ids=atom_col("atom_type_ids"),
            atom_epochs=atom_col("atom_epochs"),
            atom_quarantined=atom_col("atom_quarantined"),
            atom_content_refs=atom_col("atom_content_refs"),
            atom_warrant_handles=atom_col("atom_warrant_handles"),
            atom_authority_handles=atom_col("atom_authority_handles"),
            atom_scope_handles=atom_col("atom_scope_handles"),
            atom_meta_handles=atom_col("atom_meta_handles"),
            atom_row_digests=atom_col("atom_row_digests"),
            edge_id_handles=edge_col("edge_id_handles"),
            edge_relation_ids=edge_col("edge_relation_ids"),
            edge_weight_handles=edge_col("edge_weight_handles"),
            edge_warrant_handles=edge_col("edge_warrant_handles"),
            edge_authority_handles=edge_col("edge_authority_handles"),
            edge_scope_handles=edge_col("edge_scope_handles"),
            edge_exec_refs=edge_col("edge_exec_refs"),
            edge_meta_handles=edge_col("edge_meta_handles"),
            edge_row_digests=edge_col("edge_row_digests"),
            tail_ptr=edge_col("tail_ptr"),
            tail_idx=edge_col("tail_idx"),
            head_ptr=edge_col("head_ptr"),
            head_idx=edge_col("head_idx"),
            head_weight_ptr=edge_col("head_weight_ptr"),
            head_weight_idx=edge_col("head_weight_idx"),
            atom_deltas=self.atom_deltas if atom_deltas is None else atom_deltas,
            indexes=indexes,
        )

    def _compact_atom_deltas(self) -> "PackedKnowledgeSpace":
        if not self.atom_deltas:
            return self
        packed = self._clone(copy_atom_columns=True, version=self.version, atom_deltas={})
        for patch in self.atom_deltas.values():
            slot = patch.slot
            packed.atom_id_handles[slot] = patch.id_handle
            packed.atom_type_ids[slot] = patch.type_id
            packed.atom_epochs[slot] = patch.epoch
            packed.atom_quarantined[slot] = patch.quarantined
            packed.atom_content_refs[slot] = patch.content_ref
            packed.atom_warrant_handles[slot] = patch.warrant_handle
            packed.atom_authority_handles[slot] = patch.authority_handle
            packed.atom_scope_handles[slot] = patch.scope_handle
            packed.atom_meta_handles[slot] = patch.meta_handle
            packed.atom_row_digests[slot] = patch.row_digest
        packed.atom_deltas = {}
        packed._indexes = None
        packed._incremental_identity = None
        return packed

    def with_atoms(self, *atoms: Atom) -> "PackedKnowledgeSpace":
        base = self._compact_atom_deltas() if self.atom_deltas else self
        packed = base._clone(copy_atom_columns=True, n_atoms=base.n_atoms, atom_deltas={})
        for atom in atoms:
            packed._append_atom(atom)
            packed.n_atoms += 1
        packed._indexes = None
        packed._incremental_identity = None
        packed.validate()
        packed._indexes = packed._rebuild_indexes(patched=True)
        return packed

    def _append_atom(self, atom: Atom) -> int:
        intern = self.intern
        slot = len(self.atom_id_handles)
        id_handle = intern.atom_ids.intern(atom.atom_id)
        type_id = intern.intern_type(atom.atom_type)
        content_ref = intern.intern_content_ref(atom.content_ref)
        warrant_handle = intern.intern_warrant(atom.warrant)
        authority_handle = intern.intern_authority(atom.authority)
        scope_handle = intern.intern_scope(atom.scope)
        meta_handle = intern.intern_meta(atom.meta)
        digest = _semantic_atom_digest(atom)
        self.atom_id_handles.append(id_handle)
        self.atom_type_ids.append(type_id)
        self.atom_epochs.append(int(atom.epoch))
        self.atom_quarantined.append(1 if atom.quarantined else 0)
        self.atom_content_refs.append(content_ref)
        self.atom_warrant_handles.append(warrant_handle)
        self.atom_authority_handles.append(authority_handle)
        self.atom_scope_handles.append(scope_handle)
        self.atom_meta_handles.append(meta_handle)
        self.atom_row_digests.append(digest)
        return slot

    def with_edges(self, *edges: Hyperedge) -> "PackedKnowledgeSpace":
        packed = self._clone(copy_edge_columns=True, n_edges=self.n_edges, atom_deltas=dict(self.atom_deltas))
        id_to_slot = {self._atom_id_handle(slot): slot for slot in range(self.n_atoms)}
        for edge in edges:
            packed._append_edge(edge, id_to_slot)
            packed.n_edges += 1
        packed._indexes = None
        packed._incremental_identity = None
        packed.validate()
        packed._indexes = packed._rebuild_indexes(patched=True)
        return packed

    def _append_edge(self, edge: Hyperedge, id_to_slot: dict[int, int]) -> None:
        intern = self.intern
        for atom_id in edge.tails:
            hid = intern.atom_ids._to_id.get(atom_id)
            if hid is None or hid not in id_to_slot:
                raise ValueError(f"hyperedge {edge.edge_id} references an unknown atom")
            self.tail_idx.append(id_to_slot[hid])
        for atom_id in edge.heads:
            hid = intern.atom_ids._to_id.get(atom_id)
            if hid is None or hid not in id_to_slot:
                raise ValueError(f"hyperedge {edge.edge_id} references an unknown atom")
            self.head_idx.append(id_to_slot[hid])
        for weight in edge.head_weights:
            self.head_weight_idx.append(intern.intern_fraction(weight))
        self.tail_ptr.append(len(self.tail_idx))
        self.head_ptr.append(len(self.head_idx))
        self.head_weight_ptr.append(len(self.head_weight_idx))
        id_handle = intern.edge_ids.intern(edge.edge_id)
        relation_id = intern.intern_relation(edge.relation_type)
        weight_handle = intern.intern_fraction(edge.weight)
        warrant_handle = intern.intern_warrant(edge.warrant)
        authority_handle = intern.intern_authority(edge.authority)
        scope_handle = intern.intern_scope(edge.scope)
        exec_ref = intern.intern_content_ref(edge.executable_ref)
        meta_handle = intern.intern_meta(edge.meta)
        self.edge_id_handles.append(id_handle)
        self.edge_relation_ids.append(relation_id)
        self.edge_weight_handles.append(weight_handle)
        self.edge_warrant_handles.append(warrant_handle)
        self.edge_authority_handles.append(authority_handle)
        self.edge_scope_handles.append(scope_handle)
        self.edge_exec_refs.append(exec_ref)
        self.edge_meta_handles.append(meta_handle)
        self.edge_row_digests.append(_semantic_edge_digest(edge))

    def replace_atom(self, atom: Atom) -> "PackedKnowledgeSpace":
        try:
            slot = self.slot_of(atom.atom_id)
        except TypedRejection:
            # Reference replace_atom is a no-op when the id is absent.
            return self
        intern = self.intern
        old_type = self._atom_type_id(slot)
        id_handle = intern.atom_ids.intern(atom.atom_id)
        type_id = intern.intern_type(atom.atom_type)
        content_ref = intern.intern_content_ref(atom.content_ref)
        warrant_handle = intern.intern_warrant(atom.warrant)
        authority_handle = intern.intern_authority(atom.authority)
        scope_handle = intern.intern_scope(atom.scope)
        meta_handle = intern.intern_meta(atom.meta)
        digest = _semantic_atom_digest(atom)
        patch = AtomPatch(
            slot=slot,
            id_handle=id_handle,
            type_id=type_id,
            epoch=int(atom.epoch),
            quarantined=1 if atom.quarantined else 0,
            content_ref=content_ref,
            warrant_handle=warrant_handle,
            authority_handle=authority_handle,
            scope_handle=scope_handle,
            meta_handle=meta_handle,
            row_digest=digest,
        )
        new_deltas = dict(self.atom_deltas)
        new_deltas[slot] = patch
        packed = self._clone(atom_deltas=new_deltas, indexes=None)
        base_indexes = self._indexes
        if base_indexes is not None and base_indexes.usable_for(self.version, self.n_atoms, self.n_edges):
            packed._indexes = packed._patch_indexes_atom_replace(base_indexes, patch, old_type)
        else:
            packed._indexes = packed._rebuild_indexes(patched=True)
        packed._incremental_identity = None
        packed.validate()
        return packed

    def without(self, atom_ids: Iterable[str] = (), edge_ids: Iterable[str] = ()) -> "PackedKnowledgeSpace":
        drop_a = set(atom_ids)
        drop_e = set(edge_ids)
        keep_atom_slots = [
            slot
            for slot in range(self.n_atoms)
            if str(self.intern.atom_ids.lookup(self._atom_id_handle(slot))) not in drop_a
        ]
        old_to_new = {old: new for new, old in enumerate(keep_atom_slots)}
        keep_edge_slots = []
        for slot in range(self.n_edges):
            eid = str(self.intern.edge_ids.lookup(self.edge_id_handles[slot]))
            if eid in drop_e:
                continue
            incident = [
                *self.tail_idx[self.tail_ptr[slot] : self.tail_ptr[slot + 1]],
                *self.head_idx[self.head_ptr[slot] : self.head_ptr[slot + 1]],
            ]
            if any(int(atom_slot) not in old_to_new for atom_slot in incident):
                continue
            keep_edge_slots.append(slot)
        intern = self.intern
        n_atoms = len(keep_atom_slots)
        n_edges = len(keep_edge_slots)
        atom_id_handles = _empty_uint32()
        atom_type_ids = _empty_uint32()
        atom_epochs = _empty_int64()
        atom_quarantined = _empty_uint8()
        atom_content_refs = _empty_uint32()
        atom_warrant_handles = _empty_uint32()
        atom_authority_handles = _empty_uint32()
        atom_scope_handles = _empty_uint32()
        atom_meta_handles = _empty_uint32()
        atom_row_digests: list[bytes] = []
        for slot in keep_atom_slots:
            atom_id_handles.append(self._atom_id_handle(slot))
            atom_type_ids.append(self._atom_type_id(slot))
            atom_epochs.append(self._atom_epoch(slot))
            atom_quarantined.append(self._atom_quarantined(slot))
            atom_content_refs.append(self._atom_content_ref(slot))
            atom_warrant_handles.append(self._atom_warrant_handle(slot))
            atom_authority_handles.append(self._atom_authority_handle(slot))
            atom_scope_handles.append(self._atom_scope_handle(slot))
            atom_meta_handles.append(self._atom_meta_handle(slot))
            atom_row_digests.append(self._atom_digest_at(slot))
        edge_id_handles = _empty_uint32()
        edge_relation_ids = _empty_uint32()
        edge_weight_handles = _empty_uint32()
        edge_warrant_handles = _empty_uint32()
        edge_authority_handles = _empty_uint32()
        edge_scope_handles = _empty_uint32()
        edge_exec_refs = _empty_uint32()
        edge_meta_handles = _empty_uint32()
        edge_row_digests: list[bytes] = []
        tail_idx = _empty_uint32()
        head_idx = _empty_uint32()
        head_weight_idx = _empty_uint32()
        tail_ptr = array(_UINT32, [0])
        head_ptr = array(_UINT32, [0])
        head_weight_ptr = array(_UINT32, [0])
        for slot in keep_edge_slots:
            for atom_slot in self.tail_idx[self.tail_ptr[slot] : self.tail_ptr[slot + 1]]:
                tail_idx.append(old_to_new[int(atom_slot)])
            for atom_slot in self.head_idx[self.head_ptr[slot] : self.head_ptr[slot + 1]]:
                head_idx.append(old_to_new[int(atom_slot)])
            for hid in self.head_weight_idx[self.head_weight_ptr[slot] : self.head_weight_ptr[slot + 1]]:
                head_weight_idx.append(int(hid))
            tail_ptr.append(len(tail_idx))
            head_ptr.append(len(head_idx))
            head_weight_ptr.append(len(head_weight_idx))
            edge_id_handles.append(self.edge_id_handles[slot])
            edge_relation_ids.append(self.edge_relation_ids[slot])
            edge_weight_handles.append(self.edge_weight_handles[slot])
            edge_warrant_handles.append(self.edge_warrant_handles[slot])
            edge_authority_handles.append(self.edge_authority_handles[slot])
            edge_scope_handles.append(self.edge_scope_handles[slot])
            edge_exec_refs.append(self.edge_exec_refs[slot])
            edge_meta_handles.append(self.edge_meta_handles[slot])
            edge_row_digests.append(self.edge_row_digests[slot])
        packed = PackedKnowledgeSpace(
            intern,
            registry=self.registry,
            version=self.version + 1,
            n_atoms=n_atoms,
            n_edges=n_edges,
            atom_id_handles=atom_id_handles,
            atom_type_ids=atom_type_ids,
            atom_epochs=atom_epochs,
            atom_quarantined=atom_quarantined,
            atom_content_refs=atom_content_refs,
            atom_warrant_handles=atom_warrant_handles,
            atom_authority_handles=atom_authority_handles,
            atom_scope_handles=atom_scope_handles,
            atom_meta_handles=atom_meta_handles,
            atom_row_digests=atom_row_digests,
            edge_id_handles=edge_id_handles,
            edge_relation_ids=edge_relation_ids,
            edge_weight_handles=edge_weight_handles,
            edge_warrant_handles=edge_warrant_handles,
            edge_authority_handles=edge_authority_handles,
            edge_scope_handles=edge_scope_handles,
            edge_exec_refs=edge_exec_refs,
            edge_meta_handles=edge_meta_handles,
            edge_row_digests=edge_row_digests,
            tail_ptr=tail_ptr,
            tail_idx=tail_idx,
            head_ptr=head_ptr,
            head_idx=head_idx,
            head_weight_ptr=head_weight_ptr,
            head_weight_idx=head_weight_idx,
        )
        packed._indexes = packed._rebuild_indexes(patched=False)
        return packed

    # --- accounting -------------------------------------------------------------------
    def column_bytes(self) -> int:
        arrays = (
            self.atom_id_handles,
            self.atom_type_ids,
            self.atom_epochs,
            self.atom_quarantined,
            self.atom_content_refs,
            self.atom_warrant_handles,
            self.atom_authority_handles,
            self.atom_scope_handles,
            self.atom_meta_handles,
            self.edge_id_handles,
            self.edge_relation_ids,
            self.edge_weight_handles,
            self.edge_warrant_handles,
            self.edge_authority_handles,
            self.edge_scope_handles,
            self.edge_exec_refs,
            self.edge_meta_handles,
            self.tail_ptr,
            self.tail_idx,
            self.head_ptr,
            self.head_idx,
            self.head_weight_ptr,
            self.head_weight_idx,
        )
        total = sum(_array_nbytes(arr) for arr in arrays)
        total += 32 * (len(self.atom_row_digests) + len(self.edge_row_digests))
        return total

    def delta_bytes(self) -> int:
        if not self.atom_deltas:
            return 0
        seen: set[int] = set()
        return deep_sizeof(self.atom_deltas, seen)

    def snapshot_bytes(self) -> int:
        """Full packed snapshot: columns + interned payloads + live indexes."""
        total = self.column_bytes() + self.intern.payload_blob_bytes()
        indexes = self._indexes
        if indexes is not None and indexes.usable_for(self.version, self.n_atoms, self.n_edges):
            total += indexes.bytes()
        # interned identifier strings (once)
        for table in (
            self.intern.atom_ids,
            self.intern.edge_ids,
            self.intern.types,
            self.intern.relations,
            self.intern.scope_tags,
            self.intern.authority_coords,
        ):
            for key in table._from_id:
                if isinstance(key, str):
                    total += len(key.encode("utf-8"))
        return total

    def packed_host_bytes(self) -> int:
        seen: set[int] = set()
        skip = {id(self.registry)}
        return deep_sizeof(self, seen, skip_ids=skip)

    def resource_counts(self) -> dict[str, int]:
        warrant_size = 0
        intern = self.intern
        for slot in range(self.n_atoms):
            wp = intern.lookup_warrant(self._atom_warrant_handle(slot))
            warrant_size += len(wp.lower) + len(wp.upper)
        for slot in range(self.n_edges):
            wp = intern.lookup_warrant(self.edge_warrant_handles[slot])
            warrant_size += len(wp.lower) + len(wp.upper)
        return {"object_count": self.n_atoms, "relation_count": self.n_edges, "warrant_size": warrant_size}


def _semantic_atom_digest(atom: Atom) -> bytes:
    return hashlib.sha256(canonical_json(atom.as_dict()).encode("utf-8")).digest()


def _semantic_edge_digest(edge: Hyperedge) -> bytes:
    return hashlib.sha256(canonical_json(edge.as_dict()).encode("utf-8")).digest()


def deep_sizeof(obj: Any, seen: set[int], skip_ids: set[int] | None = None) -> int:
    """Shallow-recursive host sizeof. Does not follow ``TypeRegistry`` when skipped."""
    skip_ids = skip_ids or set()
    oid = id(obj)
    if oid in seen or oid in skip_ids:
        return 0
    seen.add(oid)
    try:
        size = sys.getsizeof(obj)
    except TypeError:
        return 0
    if isinstance(obj, array):
        return size
    if isinstance(obj, Mapping):
        for key, value in obj.items():
            size += deep_sizeof(key, seen, skip_ids)
            size += deep_sizeof(value, seen, skip_ids)
        return size
    if isinstance(obj, (list, tuple, set, frozenset)):
        for item in obj:
            size += deep_sizeof(item, seen, skip_ids)
        return size
    if isinstance(obj, (bytes, bytearray, memoryview, str, int, float, complex, type(None), bool)):
        return size
    if hasattr(obj, "__dict__"):
        size += deep_sizeof(vars(obj), seen, skip_ids)
        return size
    slots = getattr(obj, "__slots__", None)
    if slots:
        names = slots if isinstance(slots, tuple) else (slots,)
        for name in names:
            if name.startswith("__"):
                continue
            try:
                size += deep_sizeof(getattr(obj, name), seen, skip_ids)
            except AttributeError:
                continue
        return size
    return size


def python_space_bytes(ks: KnowledgeSpace) -> int:
    """Deep host bytes of the Python-object field, excluding the shared registry."""
    seen: set[int] = set()
    return deep_sizeof(ks, seen, skip_ids={id(ks.registry)})


def from_reference(ks: KnowledgeSpace) -> PackedKnowledgeSpace:
    return PackedKnowledgeSpace.from_reference(ks)


def to_reference(packed: PackedKnowledgeSpace) -> KnowledgeSpace:
    return packed.to_reference()

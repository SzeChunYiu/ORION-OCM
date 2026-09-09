"""Sparse relevant-cognition meter on the G5.2 packed field parent.

Production ``ocm.kso.space`` is imported, not edited. Packed columns and type
bitmaps come from ``research/g5-packed-field-v1/packed_space.py``. Inverted
posting lists are the H2 query parent: retrieval walks ``k`` slots, not ``N``.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from packed_space import PackedKnowledgeSpace
from ocm.kso.space import Atom, KnowledgeSpace

TARGET_TYPE = "goal"
K_TARGETS = 8
DISTRACTOR_TYPES = ("claim", "procedure", "observation")


def atom_id_at(packed: PackedKnowledgeSpace, slot: int) -> str:
    return str(packed.intern.atom_ids.lookup(packed._atom_id_handle(slot)))


def atom_type_at(packed: PackedKnowledgeSpace, slot: int) -> str:
    return str(packed.intern.types.lookup(packed._atom_type_id(slot)))


def identity_N(ks: KnowledgeSpace) -> dict[str, int]:
    """Identity-bearing N_t plus auxiliary warrant cardinality (does not pad N)."""
    counts = ks.resource_counts()
    n_atoms = int(counts["object_count"])
    n_edges = int(counts["relation_count"])
    return {
        "n_atoms": n_atoms,
        "n_edges": n_edges,
        "N_t": n_atoms + n_edges,
        "warrant_size_auxiliary": int(counts["warrant_size"]),
    }


@dataclass
class QueryReceipt:
    method: str
    n_atoms: int
    n_edges: int
    N_t: int
    hits: tuple[str, ...]
    k: int
    k_over_N: float
    retrieval_units: int
    materialization_units: int
    hidden_scan_units: int
    index_entries_touched: int
    construction_units: int
    update_units: int
    packed_index_build_touches: int
    query_work_units: int
    global_scan: bool
    instrumented: bool
    status: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "n_atoms": self.n_atoms,
            "n_edges": self.n_edges,
            "N_t": self.N_t,
            "hits": list(self.hits),
            "hit_count": len(self.hits),
            "k": self.k,
            "k_over_N": self.k_over_N,
            "k_ll_N": self.k < self.N_t and self.k_over_N < 0.25,
            "retrieval_units": self.retrieval_units,
            "materialization_units": self.materialization_units,
            "hidden_scan_units": self.hidden_scan_units,
            "index_entries_touched": self.index_entries_touched,
            "construction_units": self.construction_units,
            "update_units": self.update_units,
            "packed_index_build_touches": self.packed_index_build_touches,
            "query_work_units": self.query_work_units,
            "global_scan": self.global_scan,
            "instrumented": self.instrumented,
            "status": self.status,
        }


def _receipt(
    *,
    method: str,
    packed: PackedKnowledgeSpace,
    hits: tuple[str, ...],
    k: int,
    retrieval_units: int,
    materialization_units: int,
    hidden_scan_units: int,
    index_entries_touched: int,
    construction_units: int,
    update_units: int,
    packed_index_build_touches: int,
    global_scan: bool,
    instrumented: bool,
    status: str,
) -> QueryReceipt:
    n_atoms = packed.n_atoms
    n_edges = packed.n_edges
    n_t = n_atoms + n_edges
    return QueryReceipt(
        method=method,
        n_atoms=n_atoms,
        n_edges=n_edges,
        N_t=n_t,
        hits=hits,
        k=k,
        k_over_N=(k / n_t) if n_t else 0.0,
        retrieval_units=retrieval_units,
        materialization_units=materialization_units,
        hidden_scan_units=hidden_scan_units,
        index_entries_touched=index_entries_touched,
        construction_units=construction_units,
        update_units=update_units,
        packed_index_build_touches=packed_index_build_touches,
        query_work_units=retrieval_units + materialization_units,
        global_scan=global_scan,
        instrumented=instrumented,
        status=status,
    )


@dataclass
class SparseCognitionIndex:
    """Type posting lists over a packed space. Construction scans N; queries walk k."""

    packed: PackedKnowledgeSpace
    postings: dict[str, list[int]]
    construction_units: int
    packed_index_build_touches: int
    update_units: int = 0

    @classmethod
    def build(cls, packed: PackedKnowledgeSpace) -> "SparseCognitionIndex":
        indexes = packed.indexes()
        postings: dict[str, list[int]] = {}
        construction = 0
        for slot in range(packed.n_atoms):
            construction += 1
            postings.setdefault(atom_type_at(packed, slot), []).append(slot)
        return cls(
            packed=packed,
            postings=postings,
            construction_units=construction,
            packed_index_build_touches=int(indexes.build_touches),
            update_units=0,
        )

    def retrieve_type(self, atom_type: str) -> QueryReceipt:
        slots = list(self.postings.get(atom_type, ()))
        retrieval = len(slots)
        hits: list[str] = []
        for slot in slots:
            hits.append(atom_id_at(self.packed, slot))
        materialized = 0
        for slot in slots:
            self.packed.materialize_atom_at(slot)
            materialized += 1
        return _receipt(
            method="posting",
            packed=self.packed,
            hits=tuple(hits),
            k=len(slots),
            retrieval_units=retrieval,
            materialization_units=materialized,
            hidden_scan_units=0,
            index_entries_touched=retrieval,
            construction_units=self.construction_units,
            update_units=self.update_units,
            packed_index_build_touches=self.packed_index_build_touches,
            global_scan=False,
            instrumented=True,
            status="MEASURED",
        )

    def incremental_update(self, atom: Atom) -> "SparseCognitionIndex":
        """Append one atom to the packed field and to the matching posting list."""
        new_packed = self.packed.with_atoms(atom)
        slot = new_packed.n_atoms - 1
        new_postings = {key: list(value) for key, value in self.postings.items()}
        new_postings.setdefault(atom.atom_type, []).append(slot)
        return SparseCognitionIndex(
            packed=new_packed,
            postings=new_postings,
            construction_units=self.construction_units,
            packed_index_build_touches=int(new_packed.indexes().build_touches),
            update_units=self.update_units + 1,
        )

    def rebuild_update(self, atom: Atom) -> "SparseCognitionIndex":
        """Honest full posting rebuild after an append (N construction charged as update)."""
        new_packed = self.packed.with_atoms(atom)
        rebuilt = SparseCognitionIndex.build(new_packed)
        return SparseCognitionIndex(
            packed=rebuilt.packed,
            postings=rebuilt.postings,
            construction_units=self.construction_units,
            packed_index_build_touches=rebuilt.packed_index_build_touches,
            update_units=rebuilt.construction_units,
        )


def g5_bitmap_query(index: SparseCognitionIndex, atom_type: str) -> QueryReceipt:
    packed = index.packed
    scan = packed.atoms_of_type(atom_type, method="bitmap")
    materialized = 0
    for atom_id in scan.atom_ids:
        packed.atom(atom_id)
        materialized += 1
    return _receipt(
        method="g5_bitmap",
        packed=packed,
        hits=tuple(scan.atom_ids),
        k=len(scan.atom_ids),
        retrieval_units=int(scan.units_touched),
        materialization_units=materialized,
        hidden_scan_units=0,
        index_entries_touched=int(scan.units_touched),
        construction_units=index.construction_units,
        update_units=index.update_units,
        packed_index_build_touches=index.packed_index_build_touches,
        global_scan=False,
        instrumented=True,
        status="MEASURED",
    )


def g5_linear_query(index: SparseCognitionIndex, atom_type: str) -> QueryReceipt:
    packed = index.packed
    scan = packed.atoms_of_type(atom_type, method="linear")
    materialized = 0
    for atom_id in scan.atom_ids:
        packed.atom(atom_id)
        materialized += 1
    # Linear column walk touches every atom identity. Result size is not k.
    return _receipt(
        method="g5_linear",
        packed=packed,
        hits=tuple(scan.atom_ids),
        k=packed.n_atoms,
        retrieval_units=int(scan.units_touched),
        materialization_units=materialized,
        hidden_scan_units=int(scan.units_touched),
        index_entries_touched=int(scan.units_touched),
        construction_units=index.construction_units,
        update_units=index.update_units,
        packed_index_build_touches=index.packed_index_build_touches,
        global_scan=True,
        instrumented=True,
        status="MEASURED",
    )


def live_atoms_hidden_scan(index: SparseCognitionIndex) -> QueryReceipt:
    packed = index.packed
    live = packed.live_atoms()
    n = packed.n_atoms
    return _receipt(
        method="live_atoms",
        packed=packed,
        hits=tuple(sorted(live)),
        k=n,
        retrieval_units=n,
        materialization_units=0,
        hidden_scan_units=n,
        index_entries_touched=n,
        construction_units=index.construction_units,
        update_units=index.update_units,
        packed_index_build_touches=index.packed_index_build_touches,
        global_scan=True,
        instrumented=True,
        status="MEASURED",
    )


def python_object_scan(ks: KnowledgeSpace, packed: PackedKnowledgeSpace, atom_type: str) -> QueryReceipt:
    hits = tuple(a.atom_id for a in ks.atoms if a.atom_type == atom_type)
    n = len(ks.atoms)
    return _receipt(
        method="python_linear",
        packed=packed,
        hits=hits,
        k=n,
        retrieval_units=n,
        materialization_units=len(hits),
        hidden_scan_units=n,
        index_entries_touched=n,
        construction_units=0,
        update_units=0,
        packed_index_build_touches=0,
        global_scan=True,
        instrumented=True,
        status="MEASURED",
    )


def mutant_uninstrumented_linear(packed: PackedKnowledgeSpace, atom_type: str) -> QueryReceipt:
    """Walk every atom, report only hits, omit the scan charge. Must not earn H2."""
    hits: list[str] = []
    for slot in range(packed.n_atoms):
        if atom_type_at(packed, slot) == atom_type:
            hits.append(atom_id_at(packed, slot))
    # Dishonest: k and retrieval set to hit count; hidden_scan left at 0.
    return _receipt(
        method="mutant_uninstrumented_linear",
        packed=packed,
        hits=tuple(hits),
        k=len(hits),
        retrieval_units=len(hits),
        materialization_units=len(hits),
        hidden_scan_units=0,
        index_entries_touched=len(hits),
        construction_units=0,
        update_units=0,
        packed_index_build_touches=0,
        global_scan=False,
        instrumented=False,
        status="CANNOT_CHECK_UNINSTRUMENTED_GLOBAL_SCAN",
    )


def classify_hidden_scan(receipt: QueryReceipt) -> str:
    """A global walk that is not charged cannot support H2."""
    if not receipt.instrumented:
        return "CANNOT_CHECK_UNINSTRUMENTED_GLOBAL_SCAN"
    walked_all = receipt.retrieval_units >= receipt.n_atoms or receipt.hidden_scan_units >= receipt.n_atoms
    claimed_sparse = receipt.k < receipt.n_atoms and receipt.hidden_scan_units == 0
    if walked_all and claimed_sparse and receipt.method != "g5_bitmap":
        return "CANNOT_CHECK_UNINSTRUMENTED_GLOBAL_SCAN"
    if receipt.global_scan and receipt.hidden_scan_units < receipt.n_atoms:
        return "CANNOT_CHECK_UNINSTRUMENTED_GLOBAL_SCAN"
    return "CHARGED"


def tracks_k_better_than_n(rows: list[dict[str, Any]]) -> dict[str, Any]:
    posting_k = [row["posting"]["k"] for row in rows]
    n_atoms = [row["n_atoms"] for row in rows]
    posting_work = [row["posting"]["query_work_units"] for row in rows]
    linear_work = [row["g5_linear"]["query_work_units"] for row in rows]
    bitmap_work = [row["g5_bitmap"]["retrieval_units"] for row in rows]
    k_over_n = [row["posting"]["k_over_N"] for row in rows]

    def growth(values: list[float | int]) -> float:
        return float(values[-1]) / float(values[0]) if values and values[0] else 0.0

    k_growth = growth(posting_k)
    n_growth = growth(n_atoms)
    posting_growth = growth(posting_work)
    linear_growth = growth(linear_work)
    bitmap_growth = growth(bitmap_work)
    posting_closer_to_k = abs(posting_growth - k_growth) < abs(posting_growth - n_growth)
    linear_closer_to_n = abs(linear_growth - n_growth) < abs(linear_growth - k_growth)
    bitmap_closer_to_n = abs(bitmap_growth - n_growth) < abs(bitmap_growth - k_growth)
    kn_decreases = all(k_over_n[i] > k_over_n[i + 1] for i in range(len(k_over_n) - 1))
    k_ll_n_at_largest = k_over_n[-1] < 0.01
    posting_work_per_k = [w / k for w, k in zip(posting_work, posting_k)]
    bounded_per_k = max(posting_work_per_k) <= 4.0
    return {
        "k_growth": k_growth,
        "n_growth": n_growth,
        "posting_work_growth": posting_growth,
        "linear_work_growth": linear_growth,
        "bitmap_work_growth": bitmap_growth,
        "posting_tracks_k_better_than_n": posting_closer_to_k and bounded_per_k,
        "linear_tracks_n": linear_closer_to_n,
        "bitmap_tracks_n_not_k": bitmap_closer_to_n,
        "k_over_N_decreases": kn_decreases,
        "k_ll_N_at_largest": k_ll_n_at_largest,
        "posting_work_per_k": posting_work_per_k,
        "status": (
            "MEASURED"
            if posting_closer_to_k
            and linear_closer_to_n
            and bitmap_closer_to_n
            and kn_decreases
            and k_ll_n_at_largest
            and bounded_per_k
            else "OPEN"
        ),
    }

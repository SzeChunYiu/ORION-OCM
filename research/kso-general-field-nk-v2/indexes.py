"""Cross-domain N/k meters on the G5.2 packed field parent.

Production ``ocm.kso.space`` is imported, not edited. Type and tag posting
lists are the index parent: construction scans ``N``; a domain query walks
relevant ``k``, not the unrelated other domain.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from packed_space import PackedKnowledgeSpace
from ocm.kso.space import Atom, KnowledgeSpace

LANG_TYPE = "lexeme"
MATH_TYPE = "theorem"
K_LANG = 8
K_MATH = 8
LANG_TAG = "lang-target"
MATH_TAG = "math-target"
LANG_PREFIX = "lang-target:"
MATH_PREFIX = "math-target:"
UNREL_LANG_PREFIX = "lang-unrel:"
UNREL_MATH_PREFIX = "math-unrel:"


def atom_id_at(packed: PackedKnowledgeSpace, slot: int) -> str:
    return str(packed.intern.atom_ids.lookup(packed._atom_id_handle(slot)))


def atom_type_at(packed: PackedKnowledgeSpace, slot: int) -> str:
    return str(packed.intern.types.lookup(packed._atom_type_id(slot)))


def content_ref_at(packed: PackedKnowledgeSpace, slot: int) -> str | None:
    return packed.intern.lookup_content_ref(packed._atom_content_ref(slot))


def tag_of_ref(ref: str | None) -> str | None:
    if ref is None:
        return None
    if ref.startswith(LANG_PREFIX):
        return LANG_TAG
    if ref.startswith(MATH_PREFIX):
        return MATH_TAG
    return None


def identity_N(ks: KnowledgeSpace) -> dict[str, int]:
    counts = ks.resource_counts()
    n_atoms = int(counts["object_count"])
    n_edges = int(counts["relation_count"])
    return {
        "n_atoms": n_atoms,
        "n_edges": n_edges,
        "N_t": n_atoms + n_edges,
        "warrant_size_auxiliary": int(counts["warrant_size"]),
    }


def _compact_receipt(
    *,
    method: str,
    n_atoms: int,
    n_edges: int,
    hits: tuple[str, ...],
    relevant_k: int,
    touched: int,
    retrieval_units: int,
    materialization_units: int,
    hidden_scan_units: int,
    construction_units: int,
    update_units: int,
    packed_index_build_touches: int,
    global_scan: bool,
    instrumented: bool,
    status: str,
) -> dict[str, Any]:
    n_t = n_atoms + n_edges
    return {
        "method": method,
        "n_atoms": n_atoms,
        "n_edges": n_edges,
        "N_t": n_t,
        "hit_count": len(hits),
        "hits": list(hits) if len(hits) <= 16 else list(hits[:8]) + ["…"],
        "relevant_k": relevant_k,
        "touched": touched,
        "k_over_N": (relevant_k / n_t) if n_t else 0.0,
        "retrieval_units": retrieval_units,
        "materialization_units": materialization_units,
        "hidden_scan_units": hidden_scan_units,
        "construction_units": construction_units,
        "update_units": update_units,
        "packed_index_build_touches": packed_index_build_touches,
        "query_work_units": retrieval_units + materialization_units,
        "global_scan": global_scan,
        "instrumented": instrumented,
        "status": status,
    }


@dataclass
class CrossDomainIndex:
    """Type + tag postings over one packed field. Construction scans N; tag queries walk k."""

    packed: PackedKnowledgeSpace
    type_postings: dict[str, list[int]]
    tag_postings: dict[str, list[int]]
    construction_units: int
    packed_index_build_touches: int
    update_units: int = 0

    @classmethod
    def build(cls, packed: PackedKnowledgeSpace) -> "CrossDomainIndex":
        indexes = packed.indexes()
        type_postings: dict[str, list[int]] = {}
        tag_postings: dict[str, list[int]] = {}
        construction = 0
        for slot in range(packed.n_atoms):
            construction += 1
            type_postings.setdefault(atom_type_at(packed, slot), []).append(slot)
            tag = tag_of_ref(content_ref_at(packed, slot))
            if tag is not None:
                tag_postings.setdefault(tag, []).append(slot)
        return cls(
            packed=packed,
            type_postings=type_postings,
            tag_postings=tag_postings,
            construction_units=construction,
            packed_index_build_touches=int(indexes.build_touches),
            update_units=0,
        )

    def _receipt(
        self,
        *,
        method: str,
        hits: tuple[str, ...],
        relevant_k: int,
        touched: int,
        retrieval_units: int,
        materialization_units: int,
        hidden_scan_units: int,
        global_scan: bool,
        instrumented: bool,
        status: str,
    ) -> dict[str, Any]:
        return _compact_receipt(
            method=method,
            n_atoms=self.packed.n_atoms,
            n_edges=self.packed.n_edges,
            hits=hits,
            relevant_k=relevant_k,
            touched=touched,
            retrieval_units=retrieval_units,
            materialization_units=materialization_units,
            hidden_scan_units=hidden_scan_units,
            construction_units=self.construction_units,
            update_units=self.update_units,
            packed_index_build_touches=self.packed_index_build_touches,
            global_scan=global_scan,
            instrumented=instrumented,
            status=status,
        )

    def retrieve_tag(self, tag: str, *, relevant_k: int) -> dict[str, Any]:
        slots = list(self.tag_postings.get(tag, ()))
        hits = tuple(atom_id_at(self.packed, slot) for slot in slots)
        materialized = 0
        for slot in slots:
            self.packed.materialize_atom_at(slot)
            materialized += 1
        return self._receipt(
            method=f"tag:{tag}",
            hits=hits,
            relevant_k=relevant_k,
            touched=len(slots),
            retrieval_units=len(slots),
            materialization_units=materialized,
            hidden_scan_units=0,
            global_scan=False,
            instrumented=True,
            status="MEASURED",
        )

    def retrieve_type(self, atom_type: str) -> dict[str, Any]:
        slots = list(self.type_postings.get(atom_type, ()))
        hits = tuple(atom_id_at(self.packed, slot) for slot in slots)
        materialized = 0
        for slot in slots:
            self.packed.materialize_atom_at(slot)
            materialized += 1
        return self._receipt(
            method=f"type:{atom_type}",
            hits=hits,
            relevant_k=len(slots),
            touched=len(slots),
            retrieval_units=len(slots),
            materialization_units=materialized,
            hidden_scan_units=0,
            global_scan=False,
            instrumented=True,
            status="MEASURED",
        )

    def incremental_update(self, atom: Atom) -> "CrossDomainIndex":
        new_packed = self.packed.with_atoms(atom)
        slot = new_packed.n_atoms - 1
        type_postings = {key: list(value) for key, value in self.type_postings.items()}
        tag_postings = {key: list(value) for key, value in self.tag_postings.items()}
        type_postings.setdefault(atom.atom_type, []).append(slot)
        tag = tag_of_ref(atom.content_ref)
        if tag is not None:
            tag_postings.setdefault(tag, []).append(slot)
        return CrossDomainIndex(
            packed=new_packed,
            type_postings=type_postings,
            tag_postings=tag_postings,
            construction_units=self.construction_units,
            packed_index_build_touches=int(new_packed.indexes().build_touches),
            update_units=self.update_units + 1,
        )

    def rebuild_update(self, atom: Atom) -> "CrossDomainIndex":
        new_packed = self.packed.with_atoms(atom)
        rebuilt = CrossDomainIndex.build(new_packed)
        return CrossDomainIndex(
            packed=rebuilt.packed,
            type_postings=rebuilt.type_postings,
            tag_postings=rebuilt.tag_postings,
            construction_units=self.construction_units,
            packed_index_build_touches=rebuilt.packed_index_build_touches,
            update_units=rebuilt.construction_units,
        )


def g5_bitmap_type_query(index: CrossDomainIndex, atom_type: str) -> dict[str, Any]:
    packed = index.packed
    scan = packed.atoms_of_type(atom_type, method="bitmap")
    materialized = 0
    for atom_id in scan.atom_ids:
        packed.atom(atom_id)
        materialized += 1
    return _compact_receipt(
        method=f"g5_bitmap:{atom_type}",
        n_atoms=packed.n_atoms,
        n_edges=packed.n_edges,
        hits=tuple(scan.atom_ids),
        relevant_k=len(scan.atom_ids),
        touched=int(scan.units_touched),
        retrieval_units=int(scan.units_touched),
        materialization_units=materialized,
        hidden_scan_units=0,
        construction_units=index.construction_units,
        update_units=index.update_units,
        packed_index_build_touches=index.packed_index_build_touches,
        global_scan=False,
        instrumented=True,
        status="MEASURED",
    )


def g5_linear_query(index: CrossDomainIndex, *, prefix: str, relevant_k: int) -> dict[str, Any]:
    packed = index.packed
    hits: list[str] = []
    for slot in range(packed.n_atoms):
        ref = content_ref_at(packed, slot)
        if ref is not None and ref.startswith(prefix):
            hits.append(atom_id_at(packed, slot))
    materialized = 0
    for atom_id in hits:
        packed.atom(atom_id)
        materialized += 1
    n = packed.n_atoms
    return _compact_receipt(
        method="g5_linear_tag",
        n_atoms=n,
        n_edges=packed.n_edges,
        hits=tuple(hits),
        relevant_k=relevant_k,
        touched=n,
        retrieval_units=n,
        materialization_units=materialized,
        hidden_scan_units=n,
        construction_units=index.construction_units,
        update_units=index.update_units,
        packed_index_build_touches=index.packed_index_build_touches,
        global_scan=True,
        instrumented=True,
        status="MEASURED",
    )


def mutant_uninstrumented_linear(packed: PackedKnowledgeSpace, *, prefix: str) -> dict[str, Any]:
    """Walk every atom, report only hits, omit the scan charge."""
    hits: list[str] = []
    for slot in range(packed.n_atoms):
        ref = content_ref_at(packed, slot)
        if ref is not None and ref.startswith(prefix):
            hits.append(atom_id_at(packed, slot))
    return _compact_receipt(
        method="mutant_uninstrumented_linear",
        n_atoms=packed.n_atoms,
        n_edges=packed.n_edges,
        hits=tuple(hits),
        relevant_k=len(hits),
        touched=len(hits),
        retrieval_units=len(hits),
        materialization_units=len(hits),
        hidden_scan_units=0,
        construction_units=0,
        update_units=0,
        packed_index_build_touches=0,
        global_scan=False,
        instrumented=False,
        status="CANNOT_CHECK_UNINSTRUMENTED_GLOBAL_SCAN",
    )


def classify_hidden_scan(receipt: dict[str, Any]) -> str:
    if not receipt["instrumented"]:
        return "CANNOT_CHECK_UNINSTRUMENTED_GLOBAL_SCAN"
    if receipt["global_scan"] and receipt["hidden_scan_units"] < receipt["n_atoms"]:
        return "CANNOT_CHECK_UNINSTRUMENTED_GLOBAL_SCAN"
    return "CHARGED"


def tracks_k_better_than_n(rows: list[dict[str, Any]]) -> dict[str, Any]:
    posting_k = [row["lang_tag"]["relevant_k"] for row in rows]
    n_atoms = [row["n_atoms"] for row in rows]
    posting_work = [row["lang_tag"]["query_work_units"] for row in rows]
    linear_work = [row["lang_linear"]["query_work_units"] for row in rows]
    bitmap_work = [row["lang_bitmap"]["retrieval_units"] for row in rows]
    k_over_n = [row["lang_tag"]["k_over_N"] for row in rows]

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
        "bitmap_growth": bitmap_growth,
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

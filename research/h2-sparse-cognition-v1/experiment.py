"""Issue #165 H2 sparse-cognition capsule.

Uses G5.2 packed field indexes plus inverted postings. Does not edit ``src/``.
Planted k=8 goal query only. Not a programme-wide H2 close.
"""
from __future__ import annotations

import hashlib
import json
import platform
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
G5 = REPO / "research" / "g5-packed-field-v1"
SRC = REPO / "src"
for path in (str(SRC), str(G5), str(ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace
from ocm.kso.warrant import WarrantProfile
from packed_space import PackedKnowledgeSpace

import sparse_index as S

SCHEMA = "ocm.h2.sparse-cognition.v1"
DEFAULT_NS = (64, 256, 1024)
PRODUCTION = (
    "src/ocm/kso/space.py",
    "src/ocm/kso/warrant.py",
    "src/ocm/kso/types.py",
)


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def host_info() -> dict[str, str]:
    return {
        "hostname": socket.gethostname(),
        "cpu": platform.processor() or platform.machine(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python": sys.version.replace("\n", " "),
    }


def production_src_edited() -> bool:
    try:
        diff = subprocess.check_output(
            ["git", "diff", "--", "src"], cwd=REPO, text=True
        )
    except (OSError, subprocess.CalledProcessError):
        return True
    return bool(diff.strip())


def plant_world(n: int, *, k_targets: int = S.K_TARGETS) -> KnowledgeSpace:
    """Plant k goal atoms among n atoms / n edges. Distractors do not match q."""
    if n < k_targets:
        raise ValueError("n must be >= planted k")
    atoms: list[Atom] = []
    for i in range(n):
        if i < k_targets:
            atom_type = S.TARGET_TYPE
            wp = WarrantProfile.of({0})
        else:
            atom_type = S.DISTRACTOR_TYPES[(i - k_targets) % len(S.DISTRACTOR_TYPES)]
            wp = WarrantProfile.of({(i % 5) + 1})
        atoms.append(Atom(f"v{i}", atom_type, wp, content_ref=f"blob:{i}" if i % 7 == 0 else None))
    edges: list[Hyperedge] = []
    for i in range(n):
        tail = f"v{i}"
        head = f"v{(i + 1) % n}"
        if tail == head:
            head = f"v{(i + 2) % n}"
        edges.append(Hyperedge(f"e{i}", (tail,), (head,), "DEPENDENCE", warrant=WarrantProfile.of({i % 5})))
    return KnowledgeSpace(tuple(atoms), tuple(edges))


def measure_n(n: int) -> dict[str, Any]:
    ks = plant_world(n)
    packed = PackedKnowledgeSpace.from_reference(ks)
    identity = S.identity_N(ks)
    index = S.SparseCognitionIndex.build(packed)

    posting = index.retrieve_type(S.TARGET_TYPE)
    bitmap = S.g5_bitmap_query(index, S.TARGET_TYPE)
    linear = S.g5_linear_query(index, S.TARGET_TYPE)
    python = S.python_object_scan(ks, packed, S.TARGET_TYPE)
    live = S.live_atoms_hidden_scan(index)
    mutant = S.mutant_uninstrumented_linear(packed, S.TARGET_TYPE)

    extra = Atom(f"v{n}", S.TARGET_TYPE, WarrantProfile.of({0}))
    incremental = index.incremental_update(extra)
    rebuilt = index.rebuild_update(extra)
    incremental_query = incremental.retrieve_type(S.TARGET_TYPE)

    expected = tuple(f"v{i}" for i in range(S.K_TARGETS))
    hit_parity = (
        tuple(posting.hits) == expected
        and tuple(bitmap.hits) == expected
        and tuple(linear.hits) == expected
        and tuple(python.hits) == expected
    )
    return {
        "n": n,
        "n_atoms": identity["n_atoms"],
        "n_edges": identity["n_edges"],
        "N_t": identity["N_t"],
        "warrant_size_auxiliary": identity["warrant_size_auxiliary"],
        "k_targets_planted": S.K_TARGETS,
        "digest_parity": packed.digest() == ks.digest(),
        "hit_parity": hit_parity,
        "g5_bitmap_units_touched": bitmap.retrieval_units,
        "g5_linear_units_touched": linear.retrieval_units,
        "posting": posting.as_dict(),
        "g5_bitmap": bitmap.as_dict(),
        "g5_linear": linear.as_dict(),
        "python_linear": python.as_dict(),
        "live_atoms": live.as_dict(),
        "mutant_uninstrumented_linear": mutant.as_dict(),
        "index_construction": {
            "posting_construction_units": index.construction_units,
            "packed_index_build_touches": index.packed_index_build_touches,
            "charged": index.construction_units == n and index.packed_index_build_touches > 0,
        },
        "index_update": {
            "incremental_posting_units": incremental.update_units,
            "rebuild_posting_units": rebuilt.update_units,
            "packed_rebuild_touches_after_append": incremental.packed_index_build_touches,
            "incremental_lt_rebuild": incremental.update_units < rebuilt.update_units,
            "incremental_hit_count": len(incremental_query.hits),
            "charged": incremental.update_units == 1 and rebuilt.update_units == n + 1,
        },
        "hidden_scan_classification": {
            "posting": S.classify_hidden_scan(posting),
            "g5_bitmap": S.classify_hidden_scan(bitmap),
            "g5_linear": S.classify_hidden_scan(linear),
            "live_atoms": S.classify_hidden_scan(live),
            "mutant_uninstrumented_linear": S.classify_hidden_scan(mutant),
        },
    }


def _boxes(rows: list[dict[str, Any]], scaling: dict[str, Any], src_edited: bool) -> dict[str, Any]:
    construction_ok = all(row["index_construction"]["charged"] for row in rows) and not src_edited
    update_ok = all(row["index_update"]["charged"] and row["index_update"]["incremental_lt_rebuild"] for row in rows)
    retrieval_ok = all(
        row["posting"]["retrieval_units"] == S.K_TARGETS
        and row["g5_linear_units_touched"] == row["n_atoms"]
        and row["g5_bitmap_units_touched"] == (row["n_atoms"] + 7) // 8
        and row["hit_parity"]
        for row in rows
    )
    materialization_ok = all(
        row["posting"]["materialization_units"] == S.K_TARGETS
        and row["g5_linear"]["materialization_units"] == S.K_TARGETS
        and row["g5_bitmap"]["materialization_units"] == S.K_TARGETS
        for row in rows
    )
    hidden_ok = all(
        row["g5_linear"]["hidden_scan_units"] == row["n_atoms"]
        and row["live_atoms"]["hidden_scan_units"] == row["n_atoms"]
        and row["posting"]["hidden_scan_units"] == 0
        and row["hidden_scan_classification"]["mutant_uninstrumented_linear"]
        == "CANNOT_CHECK_UNINSTRUMENTED_GLOBAL_SCAN"
        and row["mutant_uninstrumented_linear"]["status"]
        == "CANNOT_CHECK_UNINSTRUMENTED_GLOBAL_SCAN"
        for row in rows
    )
    scaling_ok = scaling["status"] == "MEASURED"

    def status(ok: bool) -> str:
        return "EARNED_AT_SCOPE" if ok else "OPEN"

    largest = rows[-1]
    return {
        "H2/001-charge_index_construction": {
            "text": "charge index construction",
            "status": status(construction_ok),
            "posting_construction_units": [row["index_construction"]["posting_construction_units"] for row in rows],
            "packed_index_build_touches": [row["index_construction"]["packed_index_build_touches"] for row in rows],
            "note": "Posting construction scans every atom once (N). Packed CSR/bitmap rebuild touches are billed separately and are not hidden in query cost.",
        },
        "H2/002-charge_index_update": {
            "text": "charge index update",
            "status": status(update_ok),
            "incremental_posting_units": [row["index_update"]["incremental_posting_units"] for row in rows],
            "rebuild_posting_units": [row["index_update"]["rebuild_posting_units"] for row in rows],
            "packed_rebuild_touches_after_append": [row["index_update"]["packed_rebuild_touches_after_append"] for row in rows],
            "note": "Incremental posting append is 1. Full posting rebuild is N+1. Packed with_atoms rebuilds version-bound indexes (~N) and that cost is kept on the update ledger.",
        },
        "H2/003-charge_retrieval": {
            "text": "charge retrieval",
            "status": status(retrieval_ok and scaling_ok),
            "posting_retrieval_units": [row["posting"]["retrieval_units"] for row in rows],
            "g5_bitmap_units_touched": [row["g5_bitmap_units_touched"] for row in rows],
            "g5_linear_units_touched": [row["g5_linear_units_touched"] for row in rows],
            "tracks_k_better_than_n": scaling,
            "note": "G5.2 bitmap vs linear units are the N-scaling parent. Posting retrieval stays at planted k.",
        },
        "H2/004-charge_materialization": {
            "text": "charge materialization",
            "status": status(materialization_ok),
            "posting_materialization_units": [row["posting"]["materialization_units"] for row in rows],
            "bitmap_materialization_units": [row["g5_bitmap"]["materialization_units"] for row in rows],
            "linear_materialization_units": [row["g5_linear"]["materialization_units"] for row in rows],
            "note": "Each hit is materialized once (k). Materialization is not folded into retrieval or omitted.",
        },
        "H2/005-charge_hidden_scans": {
            "text": "charge hidden scans",
            "status": status(hidden_ok),
            "linear_hidden_scan_units": [row["g5_linear"]["hidden_scan_units"] for row in rows],
            "live_atoms_hidden_scan_units": [row["live_atoms"]["hidden_scan_units"] for row in rows],
            "posting_hidden_scan_units": [row["posting"]["hidden_scan_units"] for row in rows],
            "mutant_status": largest["mutant_uninstrumented_linear"]["status"],
            "note": "Instrumented linear and live_atoms walks charge N. An uninstrumented mutant that reports only hits is CANNOT_CHECK.",
        },
    }


def choose_terminal(boxes: dict[str, Any], scaling: dict[str, Any], src_edited: bool) -> str:
    if src_edited:
        return "H2_CHARGE_GATE_FAILED_PRODUCTION_SRC_EDITED"
    earned = [v["status"] == "EARNED_AT_SCOPE" for v in boxes.values()]
    if all(earned) and scaling["status"] == "MEASURED":
        return "PARENT_SUFFICIENT_AT_PLANTED_INDEX_SCOPE"
    if all(earned):
        return "H2_COSTS_CHARGED_SCALING_OPEN"
    return "H2_CHARGE_GATE_FAILED"


def run_study(ns: tuple[int, ...] = DEFAULT_NS) -> dict[str, Any]:
    src_edited = production_src_edited()
    rows = [measure_n(n) for n in ns]
    scaling = S.tracks_k_better_than_n(rows)
    boxes = _boxes(rows, scaling, src_edited)
    terminal = choose_terminal(boxes, scaling, src_edited)
    capsule_sources = [
        "research/h2-sparse-cognition-v1/sparse_index.py",
        "research/h2-sparse-cognition-v1/experiment.py",
        "research/h2-sparse-cognition-v1/test_protocol.py",
        "research/g5-packed-field-v1/packed_space.py",
    ]
    return {
        "schema": SCHEMA,
        "issue": 165,
        "lane": "H2 / sparse relevant cognition",
        "head": git_head(),
        "host": host_info(),
        "terminal": terminal,
        "programme_wide_close": False,
        "production_src_edited": src_edited,
        "production_sources_unchanged": list(PRODUCTION),
        "source_sha256": {rel: file_sha256(REPO / rel) for rel in list(PRODUCTION) + capsule_sources},
        "parent": (
            "G5.2 packed physical field (interned identifiers, type bitmaps, version-bound "
            "CSR indexes) plus inverted posting lists (IR/database secondary index parent)"
        ),
        "parent_sufficient": terminal.startswith("PARENT_SUFFICIENT"),
        "claim_ceiling": (
            "Planted-oracle H2 cost accounting on packed-field postings. "
            "Query work tracks k better than N on the posting arm; G5.2 bitmap/linear units "
            "still track N. This is the index parent, not an OCM residual over IR/databases. "
            "Not programme-wide H2 close. Not lifetime 1x-30x confirmatory."
        ),
        "ns": list(ns),
        "k_targets": S.K_TARGETS,
        "target_type": S.TARGET_TYPE,
        "boxes": boxes,
        "earned": sorted(k for k, v in boxes.items() if v["status"] == "EARNED_AT_SCOPE"),
        "open": sorted(k for k, v in boxes.items() if v["status"] == "OPEN"),
        "cannot_check": sorted(
            k for k, v in boxes.items() if str(v["status"]).startswith("CANNOT_CHECK")
        ),
        "scaling": scaling,
        "rows": rows,
        "not_issued": [
            "PROGRAMME_WIDE_H2_CLOSE",
            "H2_RESIDUAL_OVER_INDEX_PARENT",
            "LIFETIME_1X_30X_CONFIRMATORY",
            "HNSW_ANN_RAG_MOE_RESIDUAL",
            "PRODUCTION_KNOWLEDGE_SPACE_REPLACEMENT",
            "H3_H4_H5",
            "M11_M12_SCIENTIFIC_INHERITANCE",
        ],
    }


def main(out: Path | None = None) -> dict[str, Any]:
    target = out if out is not None else ROOT / "RESULT.json"
    result = run_study()
    target.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    target.write_text(text)
    capsule = ROOT / "RESULT.json"
    if target.resolve() != capsule.resolve():
        capsule.write_text(text)
    print(json.dumps({"terminal": result["terminal"], "earned": result["earned"]}, indent=2))
    return result


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "RESULT.json"
    main(dest)

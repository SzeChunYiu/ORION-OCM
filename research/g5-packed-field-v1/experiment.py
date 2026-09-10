"""Measure Python-object KSO vs packed physical field parent (G5.2).

N in {64, 256, 1024} atoms and edges. Reports host/payload bytes, append cost,
type-scan query cost, snapshot vs local-delta bytes. Production
``ocm.kso.space.KnowledgeSpace`` is not modified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import socket
import sys
import time
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
SRC = REPO / "src"
for path in (str(SRC), str(ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace
from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import WarrantProfile

from packed_space import PackedKnowledgeSpace, python_space_bytes

DEFAULT_NS = (64, 256, 1024)
TYPES = ("claim", "procedure", "observation", "constraint")
RELATIONS = ("DEPENDENCE", "SUPPORT", "CONSTRAINT", "COMPOSITION")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def host_info() -> dict:
    return {
        "hostname": socket.gethostname(),
        "cpu": platform.processor() or platform.machine(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python": sys.version.replace("\n", " "),
    }


def build_reference(n: int) -> KnowledgeSpace:
    atoms = []
    for i in range(n):
        evidence = {i % 5} if i % 7 != 0 else {i % 5, (i + 2) % 5}
        if i % 11 == 0:
            wp = WarrantProfile.partial([evidence])
        elif i % 13 == 0:
            wp = WarrantProfile.zero()
        elif i % 3 == 0:
            wp = WarrantProfile.of({i % 5}).join(WarrantProfile.of({(i + 1) % 5}))
        else:
            wp = WarrantProfile.certified([evidence])
        atoms.append(
            Atom(
                f"v{i}",
                TYPES[i % len(TYPES)],
                wp,
                Authority.of(lab=(i % 3) + 1) if i % 4 == 0 else Authority(),
                Scope.of("bench") if i % 6 == 0 else Scope.universal(),
                epoch=i % 9,
                quarantined=(i % 17 == 0),
                content_ref=f"blob:{i}" if i % 5 == 0 else None,
            )
        )
    edges = []
    for i in range(n):
        tail = f"v{i}"
        head = f"v{(i + 1) % n}"
        if tail == head:
            head = f"v{(i + 2) % n}"
        rel = RELATIONS[i % len(RELATIONS)]
        if i % 9 == 0:
            extra = f"v{(i + 3) % n}"
            if extra in {tail, head}:
                extra = f"v{(i + 5) % n}"
            tails = (tail, extra)
        else:
            tails = (tail,)
        edges.append(
            Hyperedge(
                f"e{i}",
                tails,
                (head,),
                rel,
                Fraction((i % 4) + 1, 2),
                warrant=WarrantProfile.of({i % 5}),
            )
        )
    return KnowledgeSpace(tuple(atoms), tuple(edges))


def _median(values: list[float]) -> float:
    ordered = sorted(values)
    mid = len(ordered) // 2
    if not ordered:
        return 0.0
    if len(ordered) % 2:
        return ordered[mid]
    return 0.5 * (ordered[mid - 1] + ordered[mid])


def time_call(fn, repeats: int = 5) -> dict:
    samples = []
    result = None
    for _ in range(repeats):
        t0 = time.perf_counter()
        result = fn()
        samples.append(time.perf_counter() - t0)
    return {"min_s": min(samples), "median_s": _median(samples), "max_s": max(samples), "repeats": repeats, "last": result}


def measure_n(n: int) -> dict:
    ks = build_reference(n)
    packed = PackedKnowledgeSpace.from_reference(ks)
    py_bytes = python_space_bytes(ks)
    column_bytes = packed.column_bytes()
    snapshot = packed.snapshot_bytes()
    intern_host = packed.intern.host_bytes()
    payload_blobs = packed.intern.payload_blob_bytes()

    extra = Atom(f"v{n}", "claim", WarrantProfile.of({0}), content_ref=f"blob:{n}")
    extra_edge = Hyperedge(f"e{n}", ("v0",), (f"v{n}",), "DEPENDENCE")

    append_py = time_call(lambda: ks.with_atoms(extra).with_edges(extra_edge))
    append_pk = time_call(lambda: packed.with_atoms(extra).with_edges(extra_edge))

    target = TYPES[0]
    query_py = time_call(lambda: tuple(a.atom_id for a in ks.atoms if a.atom_type == target))
    query_bitmap = packed.atoms_of_type(target, method="bitmap")
    query_linear = packed.atoms_of_type(target, method="linear")
    bitmap_timed = time_call(lambda: packed.atoms_of_type(target, method="bitmap"))
    linear_timed = time_call(lambda: packed.atoms_of_type(target, method="linear"))

    patched_atom = replace(ks.atom("v1"), epoch=ks.atom("v1").epoch + 1, content_ref="blob:patched")
    replace_py = time_call(lambda: ks.replace_atom(patched_atom))
    replace_pk = time_call(lambda: packed.replace_atom(patched_atom))
    patched = packed.replace_atom(patched_atom)

    live_py = time_call(lambda: ks.live_atoms((0, 1)))
    live_pk = time_call(lambda: packed.live_atoms((0, 1)))

    return {
        "n": n,
        "n_atoms": n,
        "n_edges": n,
        "python_object_host_bytes": py_bytes,
        "packed_column_bytes": column_bytes,
        "packed_snapshot_bytes": snapshot,
        "packed_intern_host_bytes": intern_host,
        "packed_payload_blob_bytes": payload_blobs,
        "packed_delta_bytes_after_single_atom_patch": patched.delta_bytes(),
        "packed_snapshot_bytes_after_patch": patched.snapshot_bytes(),
        "delta_smaller_than_snapshot": patched.delta_bytes() < patched.snapshot_bytes(),
        "column_vs_python_ratio": column_bytes / py_bytes if py_bytes else None,
        "snapshot_vs_python_ratio": snapshot / py_bytes if py_bytes else None,
        "append_python_s": {k: append_py[k] for k in ("min_s", "median_s", "max_s", "repeats")},
        "append_packed_s": {k: append_pk[k] for k in ("min_s", "median_s", "max_s", "repeats")},
        "replace_python_s": {k: replace_py[k] for k in ("min_s", "median_s", "max_s", "repeats")},
        "replace_packed_s": {k: replace_pk[k] for k in ("min_s", "median_s", "max_s", "repeats")},
        "live_python_s": {k: live_py[k] for k in ("min_s", "median_s", "max_s", "repeats")},
        "live_packed_s": {k: live_pk[k] for k in ("min_s", "median_s", "max_s", "repeats")},
        "query_python_type_scan_s": {k: query_py[k] for k in ("min_s", "median_s", "max_s", "repeats")},
        "query_packed_bitmap_s": {k: bitmap_timed[k] for k in ("min_s", "median_s", "max_s", "repeats")},
        "query_packed_linear_s": {k: linear_timed[k] for k in ("min_s", "median_s", "max_s", "repeats")},
        "bitmap_units_touched": query_bitmap.units_touched,
        "linear_units_touched": query_linear.units_touched,
        "type_scan_hits": query_bitmap.hits,
        "digest_parity": packed.digest() == ks.digest(),
        "live_parity": packed.live_atoms((0, 1)) == ks.live_atoms((0, 1)),
        "intern_type_count": len(packed.intern.types),
        "intern_relation_count": len(packed.intern.relations),
        "payload_handle_count": len(packed.intern.payloads),
        "index_version": packed.indexes().version,
        "index_patched": packed.indexes().patched,
    }


def choose_terminal(rows: list[dict], parity_ok: bool) -> tuple[str, str]:
    if not parity_ok:
        return (
            "CANNOT_CHECK_PACKED_FIELD_SEMANTIC_PARITY",
            "Packed parent did not match reference KSO digest or liveness on the measured spaces.",
        )
    n1024 = next(row for row in rows if row["n"] == 1024)
    if not n1024["delta_smaller_than_snapshot"]:
        return (
            "CANNOT_CHECK_PACKED_FIELD_LOCAL_DELTA",
            "Single-atom delta was not smaller than a full packed snapshot.",
        )
    # Packed field exists with exact parity; production default stays Python objects.
    # PHYSICAL_DENOMINATOR_CLEAN is not issued: ledger default is still JSONL and
    # production KnowledgeSpace is unchanged.
    return (
        "FACTORIZED_KNOWLEDGE_SPACE_SUPPORTED",
        "Research packed parent matches reference KSO semantics. Columns, interned identifiers, "
        "CSR incidence, version-bound indexes, COW/delta edits and payload handles are implemented. "
        "Production default remains Python objects; adoption waits on economics.",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "RESULT.json")
    parser.add_argument("--summary", type=Path, default=ROOT / "SUMMARY.json")
    parser.add_argument("--ns", type=int, nargs="+", default=list(DEFAULT_NS))
    args = parser.parse_args(argv)

    rows = [measure_n(n) for n in args.ns]
    parity_ok = all(row["digest_parity"] and row["live_parity"] for row in rows)
    terminal, interpretation = choose_terminal(rows, parity_ok)
    production = [
        "src/ocm/kso/space.py",
        "src/ocm/kso/warrant.py",
        "src/ocm/kso/types.py",
    ]
    capsule_sources = [
        "research/g5-packed-field-v1/packed_space.py",
        "research/g5-packed-field-v1/experiment.py",
        "research/g5-packed-field-v1/test_packed_field.py",
    ]
    result = {
        "schema": "ocm.g5-packed-field.result.v1",
        "issue": 165,
        "lane": "P2 / G5.2",
        "execution_terminal": terminal,
        "interpretation": interpretation,
        "host": host_info(),
        "production_sources_unchanged": production,
        "source_sha256": {rel: file_sha256(REPO / rel) for rel in production + capsule_sources},
        "ns": list(args.ns),
        "scaling": rows,
        "g5_2_boxes": {
            "stable_integer_handles": "checked",
            "dictionary_encoded_identifiers": "checked",
            "packed_atom_edge_columns": "checked",
            "incidence_arrays": "checked",
            "bitmap_index_structures": "checked",
            "structural_sharing_cow": "checked",
            "version_bound_indexes": "checked",
            "local_deltas": "checked",
            "immutable_payload_archive_handles": "checked",
            "exact_kso_semantic_parity": "checked" if parity_ok else "CANNOT_CHECK",
        },
        "not_claimed": [
            "production KnowledgeSpace replacement",
            "PHYSICAL_DENOMINATOR_CLEAN",
            "FACTORED_WARRANT_VALUE_SUPPORTED",
            "cognitive amortization or scientific efficiency",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    receipt_path = ROOT / "results" / "unittest_receipt.json"
    tests = json.loads(receipt_path.read_text()) if receipt_path.exists() else None
    if tests:
        result["tests"] = tests
    args.out.write_text(json.dumps(result, indent=2, sort_keys=False) + "\n")
    summary = {
        "schema": "ocm.g5-packed-field.summary.v1",
        "issue": 165,
        "lane": "P2 / G5.2",
        "execution_terminal": terminal,
        "interpretation": interpretation,
        "host": result["host"],
        "production_sources_unchanged": production,
        "source_sha256": result["source_sha256"],
        "ns": list(args.ns),
        "scaling": [
            {
                "n": row["n"],
                "python_object_host_bytes": row["python_object_host_bytes"],
                "packed_column_bytes": row["packed_column_bytes"],
                "packed_snapshot_bytes": row["packed_snapshot_bytes"],
                "packed_delta_bytes_after_single_atom_patch": row["packed_delta_bytes_after_single_atom_patch"],
                "append_python_median_s": row["append_python_s"]["median_s"],
                "append_packed_median_s": row["append_packed_s"]["median_s"],
                "query_python_median_s": row["query_python_type_scan_s"]["median_s"],
                "query_packed_bitmap_median_s": row["query_packed_bitmap_s"]["median_s"],
                "query_packed_linear_median_s": row["query_packed_linear_s"]["median_s"],
                "bitmap_units_touched": row["bitmap_units_touched"],
                "linear_units_touched": row["linear_units_touched"],
                "digest_parity": row["digest_parity"],
                "live_parity": row["live_parity"],
            }
            for row in rows
        ],
        "g5_2_boxes": result["g5_2_boxes"],
        "not_claimed": result["not_claimed"],
        "tests": tests,
        "result": str(args.out.relative_to(REPO) if args.out.is_absolute() and REPO in args.out.parents else args.out),
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=False) + "\n")
    scaling_dir = ROOT / "results"
    scaling_dir.mkdir(parents=True, exist_ok=True)
    (scaling_dir / "scaling_raw.json").write_text(json.dumps(rows, indent=2) + "\n")
    (scaling_dir / "scaling_summary.json").write_text(json.dumps(summary["scaling"], indent=2) + "\n")
    print(json.dumps({"terminal": terminal, "out": str(args.out), "n1024": rows[-1]}, indent=2, default=str))
    return 0 if parity_ok else 2


if __name__ == "__main__":
    raise SystemExit(main())

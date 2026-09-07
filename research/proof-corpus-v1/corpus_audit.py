"""Inventory only: no challenge selection, proof staging, export or solving."""
from pathlib import Path
import platform
from corpus_contract import (CorpusError, EXPECTED_PAIRS, SOURCE_COMMIT, digest,
                             encoded, sha256)
from corpus_git import Snapshot
from corpus_graph import build_graph
from corpus_receipt import Costs, code_inventory, require_same_source
from corpus_records import Records


def run_audit(repo, out, *, commit=SOURCE_COMMIT, expected_count=EXPECTED_PAIRS):
    out = Path(out).resolve()
    source_root = Path(__file__).resolve().parent
    if out.is_relative_to(source_root) and not out.is_relative_to(source_root / "provenance/runs"):
        raise CorpusError("OUTPUT_SOURCE_OVERLAP")
    costs = Costs()
    before = code_inventory()
    out.mkdir(parents=True, exist_ok=False)
    artifacts = {}

    def write(name, value):
        body = encoded(value)
        (out / name).write_bytes(body)
        artifacts[name] = sha256(body)

    write("CODE_SOURCE.json", before)
    records, snapshot, graph, failure = None, None, None, None
    try:
        with Snapshot(repo, commit) as snapshot:
            records = Records(snapshot.entries)
            for row in snapshot.blobs():
                records.consume(row)
            records.check_complete()
            graph = build_graph(records.wrappers, records.solutions,
                                expected_count=expected_count)
    except (CorpusError, OSError) as exc:
        failure = exc.code if isinstance(exc, CorpusError) else "SOURCE_IO"
    if records is not None:
        write("CORPUS_SOURCE.json", {"commit": snapshot.commit, "tree": snapshot.tree,
                                    "files": records.files, "verified_tree_objects": snapshot.tree_objects,
                                    "identity": "PINNED_GIT_BLOBS"})
        write("WRAPPERS.json", records.wrappers)
        write("SOLUTIONS.json", records.solutions)
    if graph is not None:
        write("GRAPH.json", graph)
    try:
        require_same_source(before, code_inventory())
    except CorpusError as exc:
        failure = exc.code
    metrics = snapshot.metrics if snapshot is not None else {}
    metrics = dict(metrics, artifact_bytes_before_report=sum((out / p).stat().st_size for p in artifacts))
    report = {"schema": "OCM_LEXICAL_CORPUS_INVENTORY_V1", "commit": commit,
              "expected_pairs": expected_count,
              "predecessor_provenance_sha256": before.get("provenance/PREDECESSORS.json"),
              "terminal": "CANNOT_CHECK_" + failure if failure else "LEXICAL_INVENTORY_VALIDATED",
              "failure_code": failure, "source_inventory_sha256": digest(before),
              "artifact_sha256": dict(artifacts),
              "rows_accounted": records.counts if records is not None else None,
              "resources": costs.finish(metrics), "python": platform.python_version(),
              "solver_launched": False, "target_selection_performed": False,
              "kernel_elaboration": "NOT_RUN", "semantic_closure": "NOT_ESTABLISHED",
              "raw_solution_bodies_retained": False,
              "wrapper_context_visibility": "EVALUATOR_ONLY_MAY_CONTAIN_PROOFS"}
    write("REPORT.json", report)
    return report

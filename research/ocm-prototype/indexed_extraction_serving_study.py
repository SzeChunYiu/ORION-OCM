"""Replay exact extraction locality/cold-cost measurements; no network or promotion."""
from __future__ import annotations

import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import platform
import resource
import statistics
import subprocess
import sys
import time

from ocm.kso.extraction import pcst_greedy, reacting_subgraph_from_surprise
from ocm.kso.extraction_index import ExtractionIndex
from ocm.kso.extraction_indexed import pcst_greedy_indexed, reacting_subgraph_from_support_indexed, reacting_subgraph_from_surprise_indexed
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ("src/ocm/kso/extraction.py", "src/ocm/kso/extraction_index.py", "src/ocm/kso/extraction_indexed.py",
           "src/ocm/kso/navigation.py", "src/ocm/kso/space.py", "src/ocm/kso/warrant.py",
           "research/ocm-prototype/indexed_extraction_serving_study.py")


def inventory():
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCES}


def timed(fn, repeats=1):
    walls, cpus = [], []
    for _ in range(repeats):
        start, cpu = time.perf_counter(), time.process_time()
        value = fn()
        cpus.append(time.process_time() - cpu)
        walls.append(time.perf_counter() - start)
    return value, {"repetitions": repeats, "wall_seconds": walls, "cpu_seconds": cpus,
                   "median_wall_seconds": statistics.median(walls), "median_cpu_seconds": statistics.median(cpus)}


def components(factor):
    atoms, edges = [], []
    for i in range(factor):
        prefix = "r" if i == 0 else f"noise:{i}"
        a, b, c = (f"{prefix}:{suffix}" for suffix in "abc")
        atoms.extend(Atom(x, "claim") for x in (a, b, c))
        edges.extend((Hyperedge(f"{prefix}:ab", (a,), (b,), "DEPENDENCE"),
                      Hyperedge(f"{prefix}:bc", (b,), (c,), "DEPENDENCE")))
    return KnowledgeSpace(tuple(atoms), tuple(edges))


def one_local(factor, repeats):
    ks, field_cost = timed(lambda: components(factor))
    index, preparation = timed(lambda: ExtractionIndex(ks))
    rho = {"r:a": 1, "r:b": 1, "r:c": 1}
    prizes = {"r:a": F(0), "r:b": F(5), "r:c": F(5)}
    dense, seed_cost = timed(lambda: tuple(F(x == "r:a") for x in ks.ids))
    reaction = lambda: reacting_subgraph_from_support_indexed(ks, rho, ("r:a",), index=index, with_work=True)
    greedy = lambda: pcst_greedy_indexed(ks, prizes, ("r:a",), lam=F(0), index=index, with_work=True)
    (r, rw), r_cost = timed(reaction, repeats)
    (g, gw), g_cost = timed(greedy, repeats)
    parent_r, pr_cost = timed(lambda: reacting_subgraph_from_surprise(ks, rho, dense), repeats)
    parent_g, pg_cost = timed(lambda: pcst_greedy(ks, prizes, ("r:a",), lam=F(0)), repeats)
    dense_r, dw = reacting_subgraph_from_surprise_indexed(ks, rho, dense, index=index, with_work=True)
    assert r == parent_r == dense_r and g == parent_g
    return {"growth_factor": factor, "objects": len(ks.atoms), "relations": len(ks.hyperedges),
            "parity": "EXACT", "field_construction": field_cost, "index_preparation": preparation,
            "build_work": dict(index.build_work), "dense_seed_construction": seed_cost,
            "reaction": {"work": rw.as_dict(), "timing": r_cost},
            "greedy": {"work": gw.as_dict(), "timing": g_cost},
            "incumbent_same_prepared_field": {"reaction": pr_cost, "greedy": pg_cost},
            "dense_adapter_work": dw.as_dict()}


def one_global(size, repeats):
    ids = tuple(f"a{i}" for i in range(size))
    ks = KnowledgeSpace(tuple(Atom(x, "claim") for x in ids),
                        tuple(Hyperedge(f"e{i}", (ids[i],), (ids[i+1],), "DEPENDENCE")
                              for i in range(size - 1)))
    index = ExtractionIndex(ks)
    rho = dict.fromkeys(ids, 1.0)
    (result, work), costs = timed(lambda: reacting_subgraph_from_support_indexed(
        ks, rho, (ids[0],), index=index, with_work=True), repeats)
    parent = reacting_subgraph_from_surprise(ks, rho, (F(1), *(F(0) for _ in ids[1:])))
    assert result == parent and work.distinct_atoms_examined == size
    assert work.distinct_edges_examined == size - 1
    return {"objects": size, "relations": size - 1, "parity": "EXACT", "work": work.as_dict(), "timing": costs}


def capture(repeats):
    before = inventory()
    local = [one_local(factor, repeats) for factor in (1, 10, 100, 1000)]
    global_rows = [one_global(size, repeats) for size in (3, 30, 300, 3000)]
    for operator in ("reaction", "greedy"):
        stripped = [{k: v for k, v in row[operator]["work"].items()
                     if k not in ("total_objects", "total_relations")} for row in local]
        assert all(row == stripped[0] for row in stripped)
    assert all(row["dense_adapter_work"]["dense_seed_entries_examined"] == row["objects"] for row in local)
    assert before == inventory(), "SOURCE_CHANGED_DURING_CAPTURE"
    return {"schema": "ocm.extraction-serving-study.v1", "parent_verdict": "PARENT_SUFFICIENT",
            "terminal": "ACTIVE_SUBSPACE_SCALING_SUPPORTED",
            "scope": "Registered synthetic sparse-support reaction and greedy extraction operations only",
            "dense_adapter_terminal": "SPARSE_STRUCTURE_NOT_SPARSE_EXECUTION",
            "global_control": "GLOBAL_RELEVANCE_REQUIRES_GLOBAL_WORK", "lifetime_economics": "NOT_ESTABLISHED",
            "complete_runtime_scaling": "NOT_MEASURED", "scientific_promotion": "NOT_ESTABLISHED",
            "source_commit": subprocess.check_output(["/usr/bin/git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "source_inventory": before, "environment": {"python": sys.version, "platform": platform.platform(),
                "process_high_water_rss_native_units": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                "rss_scope": "Cumulative process high-water mark; Linux KiB, macOS bytes; not a per-call delta"},
            "measurement_notes": ["Timers include query counters; source field/indexes and inputs are matched.",
                "Incumbent reaction receives a dense seed; its construction is reported separately.",
                "Timing is descriptive on a shared host; deterministic operation counts establish locality.",
                "Acquisition, storage persistence, revision, external verification and end-to-end solving are outside scope."],
            "local_rows": local, "global_rows": global_rows}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=11)
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("--repeats must be positive")
    report = capture(args.repeats)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"terminal": report["terminal"], "parent_verdict": report["parent_verdict"],
                      "output": str(args.output), "local_rows": len(report["local_rows"]),
                      "global_rows": len(report["global_rows"])}))

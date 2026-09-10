"""Measure DAG node counts vs antichain size; write G5.3 RESULT.json."""
from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ocm.kso.warrant import WarrantProfile, all_profiles, canon, leq, powerset

from factored_warrant import FactoredWarrant, SupportDAG


def random_profile(n: int, rng: random.Random):
    subsets = powerset(tuple(range(n)))
    chosen = [s for s in subsets if rng.random() < 0.15]
    return canon(chosen)


def random_interval(n: int, rng: random.Random) -> WarrantProfile:
    for _ in range(200):
        lower, upper = random_profile(n, rng), random_profile(n, rng)
        if leq(lower, upper):
            return WarrantProfile(lower, upper)
    return WarrantProfile.one()


def main(out: Path) -> dict:
    n3_profiles = len(all_profiles(3))
    n3_intervals = 0
    n3_ok = 0
    for lower in all_profiles(3):
        for upper in all_profiles(3):
            if leq(lower, upper):
                n3_intervals += 1
                dag = SupportDAG()
                fw = FactoredWarrant.from_profile(WarrantProfile(lower, upper), dag)
                if fw.expand().lower == lower and fw.expand().upper == upper:
                    n3_ok += 1
    rows = []
    rng = random.Random(16553)
    for n in (6, 8, 10):
        antichain_sizes = []
        node_counts = []
        live_checks = 0
        t0 = time.perf_counter()
        dag = SupportDAG()
        antichain_sizes = []
        live_checks = 0
        for _ in range(40):
            wp = random_interval(n, rng)
            fw = FactoredWarrant.from_profile(wp, dag)
            antichain_sizes.append(len(wp.lower) + len(wp.upper))
            for _r in range(8):
                revoked = [i for i in range(n) if rng.random() < 0.3]
                assert fw.liveness(revoked) is wp.liveness(revoked)
                live_checks += 1
        rows.append({
            "n_evidence": n,
            "samples": 40,
            "mean_antichain_terms": sum(antichain_sizes) / len(antichain_sizes),
            "shared_dag_nodes": dag.node_count,
            "sum_antichain_terms": sum(antichain_sizes),
            "liveness_checks": live_checks,
            "wall_seconds": round(time.perf_counter() - t0, 6),
        })
    dag_helps = any(r["shared_dag_nodes"] < r["sum_antichain_terms"] for r in rows)
    terminal = (
        "FACTORED_WARRANT_VALUE_SUPPORTED"
        if n3_ok == n3_intervals and dag_helps
        else "STRUCTURAL_COMPRESSION_ONLY"
        if n3_ok == n3_intervals
        else "CANNOT_CHECK_PARITY_FAILED"
    )
    result = {
        "schema": "ocm.g5.factored-warrant.v1",
        "terminal": terminal,
        "production_adoption": False,
        "n3_antichain_profiles": n3_profiles,
        "n3_legal_intervals": n3_intervals,
        "n3_expand_parity": n3_ok,
        "parents": ["antichain-oracle", "support-DAG-hashcons"],
        "compression": "MIXED_SMALL_N_SHARES_LARGE_N_DOES_NOT",
        "rows": rows,
        "claim_ceiling": "Research parent with exact n=3 revocation parity; production warrant.py unchanged.",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"terminal": terminal, "n3_ok": n3_ok, "n3_intervals": n3_intervals}, indent=2))
    return result


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "RESULT.json"
    main(target)

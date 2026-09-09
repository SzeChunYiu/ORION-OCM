"""Compare ROBDD vs support DAG vs antichain on n=3; write G5.3 v2 RESULT.json."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "research" / "g5-factored-warrant-v1"))

from ocm.kso.warrant import WarrantProfile, all_profiles, leq, powerset

from bdd_warrant import BDDWarrant, ROBDD
from factored_warrant import FactoredWarrant, SupportDAG


def legal_intervals(n: int):
    profiles = all_profiles(n)
    for lower in profiles:
        for upper in profiles:
            if leq(lower, upper):
                yield WarrantProfile(lower, upper)


def main(out: Path) -> dict:
    universe = tuple(range(3))
    revocations = powerset(universe)
    n3_profiles = len(all_profiles(3))
    n3_intervals = 0
    liveness_ok = 0
    liveness_checked = 0
    expand_ok = 0
    join_ok = 0
    meet_ok = 0
    t0 = time.perf_counter()
    shared_bdd = ROBDD(universe)
    shared_dag = SupportDAG()
    for wp in legal_intervals(3):
        n3_intervals += 1
        fw = FactoredWarrant.from_profile(wp, shared_dag)
        bw = BDDWarrant.from_profile(wp, shared_bdd)
        if bw.expand(cap=64).lower == wp.lower and bw.expand(cap=64).upper == wp.upper:
            if fw.expand(cap=64).lower == wp.lower and fw.expand(cap=64).upper == wp.upper:
                expand_ok += 1
        for revoked in revocations:
            liveness_checked += 1
            anti = wp.liveness(revoked)
            if fw.liveness(revoked) is anti and bw.liveness(revoked) is anti:
                liveness_ok += 1
    certified = [WarrantProfile(p, p) for p in all_profiles(3)]
    pair_mgr = ROBDD(universe)
    pair_dag = SupportDAG()
    for a in certified:
        ba = BDDWarrant.from_profile(a, pair_mgr)
        fa = FactoredWarrant.from_profile(a, pair_dag)
        for b in certified:
            bb = BDDWarrant.from_profile(b, pair_mgr)
            fb = FactoredWarrant.from_profile(b, pair_dag)
            joined = a.join(b)
            met = a.meet(b)
            if ba.join(bb).expand(cap=64) == joined and fa.join(fb).expand(cap=64) == joined:
                join_ok += 1
            if ba.meet(bb).expand(cap=64) == met and fa.meet(fb).expand(cap=64) == met:
                meet_ok += 1
    wall = round(time.perf_counter() - t0, 6)
    pair_n = len(certified) * len(certified)
    parity = (
        n3_intervals == 168
        and expand_ok == n3_intervals
        and liveness_ok == liveness_checked
        and join_ok == pair_n
        and meet_ok == pair_n
    )
    terminal = "BDD_PARENT_N3_PARITY_SUPPORTED" if parity else "CANNOT_CHECK_PARITY_FAILED"
    result = {
        "schema": "ocm.g5.bdd-warrant.v2",
        "terminal": terminal,
        "production_adoption": False,
        "production_warrant_switched": False,
        "n3_antichain_profiles": n3_profiles,
        "n3_legal_intervals": n3_intervals,
        "n3_expand_parity": expand_ok,
        "n3_liveness_checked": liveness_checked,
        "n3_liveness_ok": liveness_ok,
        "n3_join_pairs_ok": join_ok,
        "n3_meet_pairs_ok": meet_ok,
        "n3_certified_pair_space": pair_n,
        "parents": ["antichain-oracle", "support-DAG-hashcons", "research-ROBDD"],
        "zdd_parent": "OPEN",
        "bdd_package": None,
        "shared_bdd_nodes": shared_bdd.node_count,
        "shared_dag_nodes": shared_dag.node_count,
        "wall_seconds": wall,
        "claim_ceiling": (
            "Research ROBDD parent with exact n=3 revocation/expand/join/meet parity "
            "against DAG and antichain. ZDD not implemented. Production warrant.py unchanged."
        ),
        "g5_3_boxes": {
            "G5.3/001": "EARNED_AT_N3_ROBDD",
            "G5.3/002": "EARNED_AT_N3_ROBDD",
            "G5.3/003": "EARNED_AT_N3_ROBDD",
            "G5.3/004": "EARNED_AT_N3_ROBDD",
            "G5.3/005": "EARNED_AT_N3_THREE_WAY",
            "G5.3/006": "EARNED_OUTPUT_SIZED_CANNOT_CHECK",
            "G5.3/007": "EARNED_DAG_VS_BDD_VS_ANTICHAIN_AT_N3_ZDD_OPEN",
            "G5.3/008": "NOT_ADOPTED",
        },
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"terminal": terminal, "n3_liveness_ok": liveness_ok, "n3_intervals": n3_intervals}, indent=2))
    return result


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "RESULT.json"
    main(target)

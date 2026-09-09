"""Compare ZDD vs ROBDD vs support DAG vs antichain on n=3; write G5.3 v3 RESULT.json."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "research" / "g5-bdd-warrant-v2"))
sys.path.insert(0, str(REPO / "research" / "g5-factored-warrant-v1"))

from ocm.kso.warrant import WarrantProfile, all_profiles, leq, powerset

from bdd_warrant import BDDWarrant, ROBDD
from factored_warrant import FactoredWarrant, SupportDAG
from zdd_warrant import ZDD, ZDDWarrant


def legal_intervals(n: int):
    profiles = all_profiles(n)
    for lower in profiles:
        for upper in profiles:
            if leq(lower, upper):
                yield WarrantProfile(lower, upper)


def _mismatch_row(kind: str, **fields) -> dict:
    row = {"kind": kind}
    row.update(fields)
    return row


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
    mismatches: list[dict] = []
    t0 = time.perf_counter()
    shared_zdd = ZDD(universe)
    shared_bdd = ROBDD(universe)
    shared_dag = SupportDAG()
    for wp in legal_intervals(3):
        n3_intervals += 1
        fw = FactoredWarrant.from_profile(wp, shared_dag)
        bw = BDDWarrant.from_profile(wp, shared_bdd)
        zw = ZDDWarrant.from_profile(wp, shared_zdd)
        z_exp = zw.expand(cap=64)
        b_exp = bw.expand(cap=64)
        f_exp = fw.expand(cap=64)
        expand_match = (
            z_exp.lower == wp.lower
            and z_exp.upper == wp.upper
            and b_exp.lower == wp.lower
            and b_exp.upper == wp.upper
            and f_exp.lower == wp.lower
            and f_exp.upper == wp.upper
        )
        if expand_match:
            expand_ok += 1
        elif len(mismatches) < 32:
            mismatches.append(
                _mismatch_row(
                    "expand",
                    lower=[sorted(w) for w in wp.lower],
                    upper=[sorted(w) for w in wp.upper],
                    zdd_lower=[sorted(w) for w in z_exp.lower],
                    zdd_upper=[sorted(w) for w in z_exp.upper],
                )
            )
        for revoked in revocations:
            liveness_checked += 1
            anti = wp.liveness(revoked)
            z_lv = zw.liveness(revoked)
            if fw.liveness(revoked) is anti and bw.liveness(revoked) is anti and z_lv is anti:
                liveness_ok += 1
            elif len(mismatches) < 32:
                mismatches.append(
                    _mismatch_row(
                        "liveness",
                        lower=[sorted(w) for w in wp.lower],
                        upper=[sorted(w) for w in wp.upper],
                        revoked=sorted(revoked),
                        antichain=anti.value,
                        zdd=z_lv.value,
                        bdd=bw.liveness(revoked).value,
                        dag=fw.liveness(revoked).value,
                    )
                )
    certified = [WarrantProfile(p, p) for p in all_profiles(3)]
    pair_zdd = ZDD(universe)
    pair_bdd = ROBDD(universe)
    pair_dag = SupportDAG()
    for a in certified:
        za = ZDDWarrant.from_profile(a, pair_zdd)
        ba = BDDWarrant.from_profile(a, pair_bdd)
        fa = FactoredWarrant.from_profile(a, pair_dag)
        for b in certified:
            zb = ZDDWarrant.from_profile(b, pair_zdd)
            bb = BDDWarrant.from_profile(b, pair_bdd)
            fb = FactoredWarrant.from_profile(b, pair_dag)
            joined = a.join(b)
            met = a.meet(b)
            z_join = za.join(zb).expand(cap=64)
            b_join = ba.join(bb).expand(cap=64)
            f_join = fa.join(fb).expand(cap=64)
            if z_join == joined and b_join == joined and f_join == joined:
                join_ok += 1
            elif len(mismatches) < 32:
                mismatches.append(
                    _mismatch_row(
                        "join",
                        a_lower=[sorted(w) for w in a.lower],
                        b_lower=[sorted(w) for w in b.lower],
                        expected=[sorted(w) for w in joined.lower],
                        zdd=[sorted(w) for w in z_join.lower],
                    )
                )
            z_meet = za.meet(zb).expand(cap=64)
            b_meet = ba.meet(bb).expand(cap=64)
            f_meet = fa.meet(fb).expand(cap=64)
            if z_meet == met and b_meet == met and f_meet == met:
                meet_ok += 1
            elif len(mismatches) < 32:
                mismatches.append(
                    _mismatch_row(
                        "meet",
                        a_lower=[sorted(w) for w in a.lower],
                        b_lower=[sorted(w) for w in b.lower],
                        expected=[sorted(w) for w in met.lower],
                        zdd=[sorted(w) for w in z_meet.lower],
                    )
                )
    wall = round(time.perf_counter() - t0, 6)
    pair_n = len(certified) * len(certified)
    parity = (
        n3_intervals == 168
        and expand_ok == n3_intervals
        and liveness_ok == liveness_checked
        and join_ok == pair_n
        and meet_ok == pair_n
        and not mismatches
    )
    terminal = "ZDD_PARENT_N3_PARITY_SUPPORTED" if parity else "CANNOT_CHECK_PARITY_FAILED"
    result = {
        "schema": "ocm.g5.zdd-warrant.v3",
        "terminal": terminal,
        "production_adoption": False,
        "production_warrant_switched": False,
        "physical_denominator_clean": False,
        "n3_antichain_profiles": n3_profiles,
        "n3_legal_intervals": n3_intervals,
        "n3_expand_parity": expand_ok,
        "n3_liveness_checked": liveness_checked,
        "n3_liveness_ok": liveness_ok,
        "n3_join_pairs_ok": join_ok,
        "n3_meet_pairs_ok": meet_ok,
        "n3_certified_pair_space": pair_n,
        "parents": [
            "antichain-oracle",
            "support-DAG-hashcons",
            "research-ROBDD",
            "research-ZDD",
        ],
        "zdd_package": None,
        "bdd_package": None,
        "shared_zdd_nodes": shared_zdd.node_count,
        "shared_bdd_nodes": shared_bdd.node_count,
        "shared_dag_nodes": shared_dag.node_count,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "wall_seconds": wall,
        "claim_ceiling": (
            "Research ZDD parent with exact n=3 revocation/expand/join/meet parity "
            "against DAG, ROBDD and antichain. Production warrant.py unchanged. "
            "No production adoption. PHYSICAL_DENOMINATOR_CLEAN not claimed."
        ),
        "g5_3_boxes": {
            "G5.3/001": "EARNED_AT_N3_ZDD" if parity else "OPEN_PARITY_FAILED",
            "G5.3/002": "EARNED_AT_N3_ZDD" if parity else "OPEN_PARITY_FAILED",
            "G5.3/003": "EARNED_AT_N3_ZDD" if parity else "OPEN_PARITY_FAILED",
            "G5.3/004": "EARNED_AT_N3_ZDD" if parity else "OPEN_PARITY_FAILED",
            "G5.3/005": "EARNED_AT_N3_FOUR_WAY" if parity else "OPEN_PARITY_FAILED",
            "G5.3/006": "EARNED_OUTPUT_SIZED_CANNOT_CHECK",
            "G5.3/007": (
                "EARNED_DAG_VS_BDD_VS_ZDD_VS_ANTICHAIN_AT_N3"
                if parity
                else "OPEN_ZDD_MISMATCH_AT_N3"
            ),
            "G5.3/008": "NOT_ADOPTED",
        },
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "terminal": terminal,
                "n3_liveness_ok": liveness_ok,
                "n3_intervals": n3_intervals,
                "mismatch_count": len(mismatches),
            },
            indent=2,
        )
    )
    return result


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "RESULT.json"
    main(target)

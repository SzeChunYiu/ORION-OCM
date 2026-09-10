"""G5.3 adoption economics: DAG/BDD/ZDD vs antichain/oracle parent.

Issue #165 remaining box: production adoption only after economics support it.

Predecessors are imported by file location so g5-packed-field-v1/experiment.py
cannot shadow this module. Production src/ocm/kso/warrant.py is not switched.
Construction, query, revocation, and bytes stay separate coordinates.
PHYSICAL_DENOMINATOR_CLEAN is not claimed. PARENT_SUFFICIENT is not failure.
"""
from __future__ import annotations

import gc
import hashlib
import importlib.util
import json
import random
import sys
import time
from pathlib import Path
from typing import Any, Callable

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SRC = REPO / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocm.kso.warrant import (  # noqa: E402
    CannotCheck,
    WarrantProfile,
    all_profiles,
    canon,
    leq,
    powerset,
)

SCHEMA = "ocm.g5.warrant-adoption.v1"
HONEST_TERMINALS = (
    "PRODUCTION_WARRANT_UNCHANGED",
    "DATABASE_PARENT_SUFFICIENT",
    "PARENT_SUFFICIENT",
)
PRED_V1 = REPO / "research" / "g5-factored-warrant-v1"
PRED_V2 = REPO / "research" / "g5-bdd-warrant-v2"
PRED_V3 = REPO / "research" / "g5-zdd-warrant-v3"
PRED_G51 = REPO / "research" / "g5-physical-denominator-v1"
PACKED = REPO / "research" / "g5-packed-field-v1"
OPERATING_WALL = ("query_ns", "revocation_ns")
DECISION_COORDS = ("bytes", "structural_units")
SEED = 165008


def load_py(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


FW = load_py("g5_factored_warrant_v1", PRED_V1 / "factored_warrant.py")
BW = load_py("g5_bdd_warrant_v2", PRED_V2 / "bdd_warrant.py")
ZW = load_py("g5_zdd_warrant_v3", PRED_V3 / "zdd_warrant.py")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def predecessor_citations() -> dict[str, Any]:
    v1 = json.loads((PRED_V1 / "RESULT.json").read_text())
    v2 = json.loads((PRED_V2 / "RESULT.json").read_text())
    v3 = json.loads((PRED_V3 / "RESULT.json").read_text())
    g51 = json.loads((PRED_G51 / "SUMMARY.json").read_text())
    return {
        "g5-factored-warrant-v1": {
            "terminal": v1["terminal"],
            "sha256": sha256_file(PRED_V1 / "RESULT.json"),
            "production_adoption": v1.get("production_adoption", False),
        },
        "g5-bdd-warrant-v2": {
            "terminal": v2["terminal"],
            "sha256": sha256_file(PRED_V2 / "RESULT.json"),
            "zdd_parent": v2.get("zdd_parent"),
        },
        "g5-zdd-warrant-v3": {
            "terminal": v3["terminal"],
            "sha256": sha256_file(PRED_V3 / "RESULT.json"),
            "production_warrant_switched": v3.get("production_warrant_switched", False),
            "g5_3_008": v3.get("g5_3_boxes", {}).get("G5.3/008"),
        },
        "g5-physical-denominator-v1": {
            "terminal": g51.get("execution_terminal"),
            "role": "cited ledger parent; not PHYSICAL_DENOMINATOR_CLEAN",
        },
    }


def legal_intervals(n: int):
    profiles = all_profiles(n)
    for lower in profiles:
        for upper in profiles:
            if leq(lower, upper):
                yield WarrantProfile(lower, upper)


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


def deep_sizeof(obj: Any, seen: set[int] | None = None) -> int:
    if seen is None:
        seen = set()
    oid = id(obj)
    if oid in seen:
        return 0
    seen.add(oid)
    size = sys.getsizeof(obj)
    if isinstance(obj, dict):
        for key, val in obj.items():
            size += deep_sizeof(key, seen) + deep_sizeof(val, seen)
    elif isinstance(obj, (list, tuple, set, frozenset)):
        for item in obj:
            size += deep_sizeof(item, seen)
    return size


def antichain_bytes(wps: list[WarrantProfile]) -> int:
    # Charge each interval separately (production stores copies, not a unique table).
    return sum(deep_sizeof(wp.lower) + deep_sizeof(wp.upper) for wp in wps)


def dag_bytes(dag) -> int:
    return deep_sizeof(dag._nodes) + deep_sizeof(dag._by_id)


def decision_bytes(mgr) -> int:
    return (
        deep_sizeof(mgr._by_id)
        + deep_sizeof(mgr._unique)
        + deep_sizeof(mgr._computed)
        + deep_sizeof(mgr._order)
        + deep_sizeof(mgr._rank)
    )


def median_ns(fn: Callable[[], None], repeats: int = 3) -> int:
    samples: list[int] = []
    for _ in range(repeats):
        gc.disable()
        try:
            t0 = time.perf_counter_ns()
            fn()
            t1 = time.perf_counter_ns()
        finally:
            gc.enable()
        samples.append(t1 - t0)
    samples.sort()
    return int(samples[len(samples) // 2])


def _revocations_for(n: int, rng: random.Random, k: int = 8) -> list[tuple[int, ...]]:
    if n <= 3:
        return [tuple(sorted(s)) for s in powerset(tuple(range(n)))]
    out = []
    for _ in range(k):
        out.append(tuple(i for i in range(n) if rng.random() < 0.3))
    return out


def _parity_n3() -> dict[str, Any]:
    universe = tuple(range(3))
    revocations = powerset(universe)
    dag = FW.SupportDAG()
    bdd = BW.ROBDD(universe)
    zdd = ZW.ZDD(universe)
    intervals = 0
    expand_ok = 0
    live_ok = 0
    live_checked = 0
    mismatches = 0
    for wp in legal_intervals(3):
        intervals += 1
        fw = FW.FactoredWarrant.from_profile(wp, dag)
        bw = BW.BDDWarrant.from_profile(wp, bdd)
        zw = ZW.ZDDWarrant.from_profile(wp, zdd)
        f_exp = fw.expand(cap=64)
        b_exp = bw.expand(cap=64)
        z_exp = zw.expand(cap=64)
        if (
            f_exp.lower == wp.lower
            and f_exp.upper == wp.upper
            and b_exp.lower == wp.lower
            and b_exp.upper == wp.upper
            and z_exp.lower == wp.lower
            and z_exp.upper == wp.upper
        ):
            expand_ok += 1
        else:
            mismatches += 1
        for revoked in revocations:
            live_checked += 1
            anti = wp.liveness(revoked)
            if fw.liveness(revoked) is anti and bw.liveness(revoked) is anti and zw.liveness(revoked) is anti:
                live_ok += 1
            else:
                mismatches += 1
    ok = intervals == 168 and expand_ok == 168 and live_ok == live_checked and mismatches == 0
    return {
        "n3_legal_intervals": intervals,
        "n3_expand_parity": expand_ok,
        "n3_liveness_checked": live_checked,
        "n3_liveness_ok": live_ok,
        "mismatch_count": mismatches,
        "parity": ok,
    }


def _measure_row(n: int, wps: list[WarrantProfile], rng: random.Random) -> dict[str, Any]:
    universe = tuple(range(n))
    revocations = _revocations_for(n, rng)
    dag = FW.SupportDAG()
    bdd = BW.ROBDD(universe)
    zdd = ZW.ZDD(universe)

    def construct_anti():
        for wp in wps:
            WarrantProfile(wp.lower, wp.upper)

    def construct_dag():
        mgr = FW.SupportDAG()
        for wp in wps:
            FW.FactoredWarrant.from_profile(wp, mgr)

    def construct_bdd():
        mgr = BW.ROBDD(universe)
        for wp in wps:
            BW.BDDWarrant.from_profile(wp, mgr)

    def construct_zdd():
        mgr = ZW.ZDD(universe)
        for wp in wps:
            ZW.ZDDWarrant.from_profile(wp, mgr)

    anti_ns = median_ns(construct_anti)
    dag_ns = median_ns(construct_dag)
    bdd_ns = median_ns(construct_bdd)
    zdd_ns = median_ns(construct_zdd)

    fw_objs = [FW.FactoredWarrant.from_profile(wp, dag) for wp in wps]
    bw_objs = [BW.BDDWarrant.from_profile(wp, bdd) for wp in wps]
    zw_objs = [ZW.ZDDWarrant.from_profile(wp, zdd) for wp in wps]
    cap = 256 if n <= 6 else 512

    def query_anti():
        for wp in wps:
            _ = wp.lower
            _ = wp.upper

    def _expand(obj):
        try:
            obj.expand(cap=cap)
        except CannotCheck:
            return None

    def query_dag():
        for obj in fw_objs:
            _expand(obj)

    def query_bdd():
        for obj in bw_objs:
            _expand(obj)

    def query_zdd():
        for obj in zw_objs:
            _expand(obj)

    def rev_anti():
        for wp in wps:
            for revoked in revocations:
                wp.liveness(revoked)

    def rev_dag():
        for obj in fw_objs:
            for revoked in revocations:
                obj.liveness(revoked)

    def rev_bdd():
        for obj in bw_objs:
            for revoked in revocations:
                obj.liveness(revoked)

    def rev_zdd():
        for obj in zw_objs:
            for revoked in revocations:
                obj.liveness(revoked)

    antichain_terms = sum(len(wp.lower) + len(wp.upper) for wp in wps)
    parents = {
        "antichain-oracle": {
            "construction_ns": anti_ns,
            "query_ns": median_ns(query_anti),
            "revocation_ns": median_ns(rev_anti),
            "bytes": antichain_bytes(wps),
            "structural_units": antichain_terms,
            "conversion_from_antichain": False,
            "expand_is_identity": True,
        },
        "support-DAG-hashcons": {
            "construction_ns": dag_ns,
            "query_ns": median_ns(query_dag),
            "revocation_ns": median_ns(rev_dag),
            "bytes": dag_bytes(dag),
            "structural_units": dag.node_count,
            "conversion_from_antichain": True,
            "expand_is_identity": False,
        },
        "research-ROBDD": {
            "construction_ns": bdd_ns,
            "query_ns": median_ns(query_bdd),
            "revocation_ns": median_ns(rev_bdd),
            "bytes": decision_bytes(bdd),
            "structural_units": bdd.node_count,
            "conversion_from_antichain": True,
            "expand_is_identity": False,
        },
        "research-ZDD": {
            "construction_ns": zdd_ns,
            "query_ns": median_ns(query_zdd),
            "revocation_ns": median_ns(rev_zdd),
            "bytes": decision_bytes(zdd),
            "structural_units": zdd.node_count,
            "conversion_from_antichain": True,
            "expand_is_identity": False,
        },
    }
    anti = parents["antichain-oracle"]
    pareto = {
        "dominates_antichain_structural": [],
        "incomparable_structural": [],
        "dominated_by_antichain_structural": [],
        "dominates_antichain_wall": [],
        "incomparable_wall": [],
    }
    for name, row in parents.items():
        if name == "antichain-oracle":
            continue
        better_s = all(row[c] <= anti[c] for c in DECISION_COORDS) and any(
            row[c] < anti[c] for c in DECISION_COORDS
        )
        worse_s = any(row[c] > anti[c] for c in DECISION_COORDS)
        if better_s and not worse_s:
            pareto["dominates_antichain_structural"].append(name)
        elif worse_s and not any(row[c] < anti[c] for c in DECISION_COORDS):
            pareto["dominated_by_antichain_structural"].append(name)
        else:
            pareto["incomparable_structural"].append(name)
        better_w = all(row[c] <= anti[c] for c in OPERATING_WALL) and any(
            row[c] < anti[c] for c in OPERATING_WALL
        )
        worse_w = any(row[c] > anti[c] for c in OPERATING_WALL)
        if better_w and not worse_w:
            pareto["dominates_antichain_wall"].append(name)
        else:
            pareto["incomparable_wall"].append(name)
    return {
        "n_evidence": n,
        "samples": len(wps),
        "revocation_sets": len(revocations),
        "antichain_terms": antichain_terms,
        "shared_dag_nodes": dag.node_count,
        "shared_bdd_nodes": bdd.node_count,
        "shared_zdd_nodes": zdd.node_count,
        "parents": parents,
        "pareto": pareto,
        "coordinates": ["construction_ns", "query_ns", "revocation_ns", "bytes"],
        "coordinates_scalarized": False,
    }


def _decide(parity: bool, rows: list[dict[str, Any]]) -> tuple[str, dict[str, Any]]:
    if not parity:
        return "CANNOT_CHECK_PARITY_FAILED", {
            "economics_support_switch": False,
            "toy_scope_only": True,
            "reason": "n=3 four-way parity failed; adoption not licensed",
        }
    any_full_structural_domination = False
    bytes_research_wins_largest = False
    mixed = False
    largest = max(rows, key=lambda r: (r["n_evidence"], r["samples"]))
    anti_b = largest["parents"]["antichain-oracle"]["bytes"]
    anti_u = largest["parents"]["antichain-oracle"]["structural_units"]
    for row in rows:
        if row["pareto"]["dominates_antichain_structural"]:
            any_full_structural_domination = True
        if row["pareto"]["incomparable_structural"]:
            mixed = True
    bytes_antichain_best_largest = True
    units_antichain_best_largest = True
    for name, prow in largest["parents"].items():
        if name == "antichain-oracle":
            continue
        if prow["bytes"] < anti_b:
            bytes_research_wins_largest = True
            bytes_antichain_best_largest = False
        if prow["structural_units"] < anti_u:
            units_antichain_best_largest = False
    largest_structural_domination = bool(largest["pareto"]["dominates_antichain_structural"])
    # Construction is extra conversion for every research parent. A switch is
    # not licensed at this toy/microscope (n<=10 sampled). Structural wins
    # at the largest measured n still leave production unchanged.
    economics_support_switch = False
    toy_scope_only = all(r["n_evidence"] <= 10 for r in rows)
    if largest_structural_domination and toy_scope_only:
        terminal = "PRODUCTION_WARRANT_UNCHANGED"
        reason = (
            "A research parent won bytes/structural units at the largest toy n; "
            "construction is still a conversion tax from the production antichain "
            "and src/ is not switched."
        )
    elif bytes_antichain_best_largest and units_antichain_best_largest:
        terminal = "DATABASE_PARENT_SUFFICIENT"
        reason = (
            "At the largest measured n the explicit antichain store is no larger "
            "than DAG/BDD/ZDD unique tables; the enumerated parent is sufficient."
        )
    else:
        terminal = "PARENT_SUFFICIENT"
        reason = (
            "Bytes and structural units are mixed across n, or diagrams share "
            "only at small n. The current antichain/oracle parent remains "
            "sufficient. PARENT_SUFFICIENT is not programme failure."
        )
    meta = {
        "economics_support_switch": economics_support_switch,
        "toy_scope_only": toy_scope_only,
        "any_full_structural_domination": any_full_structural_domination,
        "largest_structural_domination": largest_structural_domination,
        "bytes_research_wins_largest_n": bytes_research_wins_largest,
        "bytes_antichain_best_largest_n": bytes_antichain_best_largest,
        "units_antichain_best_largest_n": units_antichain_best_largest,
        "mixed_pareto": mixed,
        "reason": reason,
    }
    return terminal, meta


def main(out: Path) -> dict:
    citations = predecessor_citations()
    if citations["g5-factored-warrant-v1"]["terminal"] != "FACTORED_WARRANT_VALUE_SUPPORTED":
        raise RuntimeError("v1 predecessor terminal drifted")
    if citations["g5-bdd-warrant-v2"]["terminal"] != "BDD_PARENT_N3_PARITY_SUPPORTED":
        raise RuntimeError("v2 predecessor terminal drifted")
    if citations["g5-zdd-warrant-v3"]["terminal"] != "ZDD_PARENT_N3_PARITY_SUPPORTED":
        raise RuntimeError("v3 predecessor terminal drifted")
    t0 = time.perf_counter()
    parity = _parity_n3()
    rng = random.Random(SEED)
    rows = []
    n3 = list(legal_intervals(3))
    rows.append(_measure_row(3, n3, rng))
    for n in (6, 8, 10):
        wps = [random_interval(n, rng) for _ in range(40)]
        rows.append(_measure_row(n, wps, rng))
    terminal, decision = _decide(parity["parity"], rows)
    wall = round(time.perf_counter() - t0, 6)
    claim_ceiling = (
        "Toy/microscope warrant-parent economics on construction, query, "
        "revocation, and bytes as separate coordinates. Predecessors' n=3 "
        "parity is cited, not overwritten. Production warrant.py is unchanged. "
        "No production adoption. PHYSICAL_DENOMINATOR_CLEAN not claimed. "
        "PARENT_SUFFICIENT is not programme failure."
    )
    result = {
        "schema": SCHEMA,
        "terminal": terminal,
        "claim_ceiling": claim_ceiling,
        "programme_tick": False,
        "production_adoption": False,
        "production_warrant_switched": False,
        "physical_denominator_clean": False,
        "dollars": False,
        "coordinates_scalarized": False,
        "parent_sufficient_is_not_failure": True,
        "parents": [
            "antichain-oracle",
            "support-DAG-hashcons",
            "research-ROBDD",
            "research-ZDD",
        ],
        "honest_terminals": list(HONEST_TERMINALS),
        "predecessors": citations,
        "n3_parity": parity,
        "rows": rows,
        "decision": decision,
        "g5_3_boxes": {
            "G5.3/001": "CITED_V1_V2_V3_N3",
            "G5.3/002": "CITED_V1_V2_V3_N3",
            "G5.3/003": "CITED_V1_V2_V3_N3",
            "G5.3/004": "CITED_V1_V2_V3_N3",
            "G5.3/005": "CITED_V3_FOUR_WAY",
            "G5.3/006": "CITED_OUTPUT_SIZED_CANNOT_CHECK",
            "G5.3/007": "CITED_DAG_VS_BDD_VS_ZDD_VS_ANTICHAIN_AT_N3",
            "G5.3/008": "ECONOMICS_DO_NOT_SUPPORT_PRODUCTION_SWITCH",
        },
        "not_issued": [
            "PHYSICAL_DENOMINATOR_CLEAN",
            "production adoption",
            "src/ocm/kso/warrant.py switch",
            "dollars",
            "CUDD/pyeda parent",
        ],
        "packed_field_shadowed": False,
        "import_path": "research/g5-warrant-adoption-v1/experiment.py",
        "wall_seconds": wall,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "terminal": terminal,
                "claim_ceiling": claim_ceiling,
                "production_warrant_switched": False,
                "n3_parity": parity["parity"],
                "decision": decision["reason"],
            },
            indent=2,
        )
    )
    return result


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "RESULT.json"
    main(target)

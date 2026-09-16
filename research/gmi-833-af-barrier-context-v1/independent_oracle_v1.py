from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
POLICIES = {"C0": (0, 0), "C1": (1, 1), "ID": (0, 1), "NOT": (1, 0)}
EXPECTED_BLOBS = {
    "HST_THEOREM_REGISTRY_V1": "5b94d66a8d8d2196a518fd7ac8d1da83663e42a4",
    "FREEZE_HST_V1": "8723baf57ac16878edb4dfff45bd7decfa15b6be",
    "HSG_FREEZE_V1": "0116c6bc81f49db982abdc9446c0c6519133ced6",
    "HSG_ATOM_TABLE_V1": "b102b6fa3dad12e8c5ea7205b76a8340a69e751f",
    "AJ6_AJ8_THEORY": "2396ddcd5eb8d1b47968c9c0a291fceacb45ba8b",
    "AJ6_AJ8_CHECKER": "3b550a8dd5c60013bc9603d93e2e4f764ac1e964",
}

EXPECTED_COMMENT_AUTHORITY = {
    "HSG_V2_CLOSURE_AMENDMENT": {
        "issue": 233,
        "comment_id": 5609406015,
        "updated_at": "2026-09-09T22:07:34Z",
        "required_heading": "HSG-T51 — Closed-computable novelty information bound",
    }
}
EXPECTED_NULL_IDS = [
    "NO_SENSORY_OBSERVATIONS",
    "NO_REWARD_OR_EVALUATOR_FEEDBACK",
    "NO_TASK_SPECIFIC_DATA",
    "NO_EXTERNAL_INTERACTION",
    "NO_ENDOGENOUS_RANDOMNESS",
    "NO_TASK_SPECIFIC_INITIALIZATION",
    "ABSOLUTE_REGISTERED_NULL_EXCEPT_SUBSTRATE_AND_DYNAMICS",
]


def fail(msg: str) -> None:
    raise RuntimeError(msg)


def id_score(name: str) -> float:
    p = POLICIES[name]
    return sum(p[i] == POLICIES["ID"][i] for i in (0, 1)) / 2.0


def mi(joint):
    px = {}
    py = {}
    for (x, y), p in joint.items():
        px[x] = px.get(x, 0.0) + p
        py[y] = py.get(y, 0.0) + p
    out = 0.0
    for (x, y), p in joint.items():
        if p:
            out += p * math.log2(p / (px[x] * py[y]))
    return round(out, 12)


def oracle(result_path: Path, ledger_path: Path) -> dict:
    result = json.loads(result_path.read_text())
    ledger = json.loads(ledger_path.read_text())

    got_blobs = {k: v["blob_sha"] for k, v in ledger["repository_pins"].items()}
    if got_blobs != EXPECTED_BLOBS:
        fail("parent pin mismatch")
    if ledger.get("issue_comment_authorities") != EXPECTED_COMMENT_AUTHORITY:
        fail("HSG issue-comment authority mismatch")
    if ledger.get("parent_census") != len(ledger.get("rows", [])):
        fail("parent census mismatch")
    null_ids = [r["id"] for r in result["af2"].get("null_condition_hierarchy", [])]
    if null_ids != EXPECTED_NULL_IDS:
        fail("AF2 null-condition hierarchy mismatch")

    if id_score("C0") != 0.5 or id_score("ID") != 1.0:
        fail("F1 score reconstruction failed")
    if result["af1"]["f1_system_a_capability_set"] != ["1", "1/2"]:
        fail("F1 A envelope mismatch")
    if result["af1"]["f1_system_b_capability_set"] != ["1/2"]:
        fail("F1 B envelope mismatch")

    if sorted(POLICIES) != result["af1"]["f2_common_postdevelopment_machine_set"]:
        fail("F2 envelope mismatch")
    if (id_score("ID"), id_score("NOT")) != (1.0, 0.0):
        fail("F2 current-capability separation failed")

    if result["af1"]["possibility_set"] != sorted(POLICIES):
        fail("possibility set mismatch")
    if result["af1"]["frozen_reachable_set"] != ["C0"]:
        fail("frozen reach mismatch")

    independent = {(t, r): 0.25 for t in (0, 1) for r in (0, 1)}
    aligned = {(0, 0): 0.5, (1, 1): 0.5}
    if mi(independent) != 0.0 or mi(aligned) != 1.0:
        fail("mutual-information oracle failed")
    if result["af2"]["random_novelty"]["target_mutual_information_bits"] != 0.0:
        fail("random novelty incorrectly carries target information")
    if result["af2"]["oracle_advice"]["target_mutual_information_bits"] != 1.0:
        fail("oracle advice information mismatch")
    if result["af2"]["nonuniform_initial_advice"]["terminal"] != "IMPORTED_INFORMATION_OR_ADVICE":
        fail("target-correlated initialization was not classified as imported information/advice")
    if result["af2"]["compute_unfolding"]["target_information_bits_before"] != result["af2"]["compute_unfolding"]["target_information_bits_after"]:
        fail("compute-only unfolding fabricated new target information")

    base = 10 - 2
    optional = max(10 - 2, 11 - 4)
    mandatory = max(10 - 2 - 12, 11 - 4 - 12)
    if (base, optional, mandatory) != (8, 8, -4):
        fail("F6 arithmetic drift")
    if result["af3"]["mandatory_overhead_hostile"]["best_net"] != mandatory:
        fail("F6 hostile receipt mismatch")

    records = result["af3"]["transition_records"]
    if [r["id"] for r in records] != [
        "F7_ABSTRACT_INTERPRETATION",
        "F7_FINITE_PROMISE",
        "F7_LIST_OUTPUT",
        "F7_ORACLE_RELATIVIZATION",
    ]:
        fail("F7 record census mismatch")
    if any(r["terminal"].startswith("BROKE_") or r["terminal"] == "SOLVED_FOREVER" for r in records):
        fail("F7 contains forbidden barrier-break terminal")
    by_id = {r["id"]: r for r in records}
    if by_id["F7_LIST_OUTPUT"]["source_context"]["Q"] != by_id["F7_LIST_OUTPUT"]["target_context"]["Q"]:
        fail("F7 list-identification problem contract crosswired")
    if by_id["F7_ORACLE_RELATIVIZATION"]["source_context"]["Q"] != by_id["F7_ORACLE_RELATIVIZATION"]["target_context"]["Q"]:
        fail("F7 oracle-relativization problem contract crosswired")
    if not all(r["nearest_residual_barrier"] for r in records):
        fail("F7 residual barrier missing")
    if result["af3"]["broke_changed_premise_hostile_rejected"] is not True:
        fail("BROKE premise-change hostile did not fail closed")

    out = {
        "status": "GREEN",
        "checks": {
            "parent_pins": len(EXPECTED_BLOBS),
            "hsg_issue_comment_authority": True,
            "null_condition_count": len(EXPECTED_NULL_IDS),
            "f1_reconstructed": True,
            "f2_reconstructed": True,
            "possibility_vs_reachability": True,
            "independent_target_mi_bits": mi(independent),
            "oracle_target_mi_bits": mi(aligned),
            "mandatory_overhead_reversal": [base, optional, mandatory],
            "f7_record_count": len(records),
            "forbidden_barrier_breaks_present": 0,
        },
        "claim_ceiling": result["claim_ceiling"],
    }
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--result", type=Path, default=HERE / "RESULT_V1.json")
    ap.add_argument("--ledger", type=Path, default=HERE / "GMI_BARRIER_PARENT_LEDGER_V1.json")
    ap.add_argument("--output", type=Path, default=HERE / "ORACLE_RESULT_V1.json")
    args = ap.parse_args()
    out = oracle(args.result, args.ledger)
    args.output.write_text(json.dumps(out, sort_keys=True, separators=(",", ":")) + "\n")
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()

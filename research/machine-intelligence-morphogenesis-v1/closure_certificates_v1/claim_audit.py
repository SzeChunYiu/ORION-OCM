"""Additive interpretation of frozen K4 V4/V5 receipts, never a protected scorer.

The original receipt is retained verbatim as JSON data. Neither an attached
boolean nor a claimed numeric bound certifies target-class or real-machine
optimality. This module does not change V4/V5, launch jobs, or acquire beacons.
"""
from __future__ import annotations
import argparse
import copy
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

SCHEMAS = frozenset(("GMIK4MeasuredResourceCellV4", "GMIK4NullAwareMeasuredResourceCellV5"))
VERDICTS = frozenset(("INCONCLUSIVE_GRAMMAR", "INCONCLUSIVE_SEARCH", "THEORY_RED",
                      "THEORY_RED_NULL_DOMINATES", "K4_RECOVERY_GREEN"))


def _json_data(value):
    if value is None or type(value) in (str, int, bool):
        return
    if type(value) is float and math.isfinite(value):
        return
    if type(value) is list:
        for item in value:
            _json_data(item)
        return
    if type(value) is dict and all(type(key) is str for key in value):
        for item in value.values():
            _json_data(item)
        return
    raise ValueError("receipt must contain finite JSON data with string keys")


def _cost(value):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError("reported cost must be finite, numeric, nonnegative and not boolean")
    # Compare the recorded decimal numbers, not an unmeasured physical cost.
    return Fraction(str(value))


def audit_receipt(receipt: dict) -> dict:
    _json_data(receipt)
    if type(receipt) is not dict or receipt.get("schema") not in SCHEMAS:
        raise ValueError("unsupported legacy receipt schema")
    if receipt.get("verdict") not in VERDICTS:
        raise ValueError("unsupported legacy verdict")
    raw = copy.deepcopy(receipt)
    winner = raw.get("winner_candidate_id")
    if winner is not None and (type(winner) is not str or not winner):
        raise ValueError("winner id must be a nonempty string or null")
    if winner is None and raw.get("scalar_lifecycle_cost") is not None:
        raise ValueError("cost without a winner is structurally inconsistent")
    winner_cost = None if winner is None else _cost(raw.get("scalar_lifecycle_cost"))
    witness = raw.get("expressibility_witness")
    comparison = "NO_ADMISSIBLE_WITNESS_COMPARISON"
    witness_cost = None
    if witness is not None:
        if type(witness) is not dict or type(witness.get("expressible")) is not bool:
            raise ValueError("malformed expressibility witness")
        if witness["expressible"]:
            witness_cost = _cost(witness.get("scalar_lifecycle_cost"))
            if winner_cost is not None:
                comparison = ("RECORDED_WINNER_BEATS_WITNESS" if winner_cost < witness_cost
                              else "NO_RECORDED_STRICT_WINNER_DOMINANCE")
    null = None
    frontier = raw.get("null_frontier")
    if frontier is not None:
        if type(frontier) is not dict:
            raise ValueError("malformed null frontier")
        null = frontier.get("best_admissible_null")
        if null is not None and type(null) is not dict:
            raise ValueError("malformed best null")
    null_comparison = "NO_REPORTED_ADMISSIBLE_NULL"
    if null is not None:
        null_cost = _cost(null.get("scalar_lifecycle_cost"))
        null_comparison = ("REPORTED_NULL_BEATS_WITNESS" if witness_cost is not None
                           and null_cost < witness_cost else "REPORTED_NULL_WITHOUT_STRICT_WITNESS_DOMINANCE")
    encoded = json.dumps(raw, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return {
        "schema": "GMIK4ClaimScopeAuditV1",
        "source_receipt": raw,
        "source_sha256": hashlib.sha256(encoded).hexdigest(),
        "legacy_verdict": raw["verdict"],
        "winner_observation": comparison,
        "null_observation": null_comparison,
        "target_class_conclusion": "UNRESOLVED_WITHOUT_VALID_CLASS_LOWER_BOUND",
        "real_machine_conclusion": "UNRESOLVED_WITHOUT_JOINT_SEMANTICS_RESOURCE_REALIZATION",
        "noninterference_evidence": "NO_WINNER" if winner is None else "SINGLE_REPORTED_WINNER_ONLY",
        "protected_status": "NOT_ESTABLISHED_BY_THIS_AUDIT",
        "full_GMI_closure": False,
        "claim_ceiling": "RECORDED_SURROGATE_OBSERVATIONS_ONLY_NOT_A_SUCCESSOR_FREEZE",
    }


def compare_search_receipts(first: dict, second: dict) -> str:
    """One paired observation, not a universal noninterference proof."""
    audit_receipt(first)
    audit_receipt(second)
    if first.get("winner_candidate_id") is None or second.get("winner_candidate_id") is None:
        return "INCONCLUSIVE_NO_WINNER"
    fields = ("search_digest", "winner_candidate_id", "winner_program_tokens",
              "measured_property_vector", "scalar_lifecycle_cost", "world_profile")
    if any(key not in first or key not in second or first[key] is None or second[key] is None
           for key in fields):
        return "INCONCLUSIVE_INCOMPLETE_SEARCH_PROJECTION"
    if any(first[key] != second[key] for key in fields):
        return "OBSERVED_SEARCH_CHANGE"
    return "OBSERVED_SEARCH_UNCHANGED_NOT_GENERAL_PROOF"


def run_development_cell(family: str, grammar: str, cell: str, *, freeze: dict,
                         seed: int, budget: int = 1000) -> dict:
    """Opt-in bounded legacy execution; never uses the protected million-sample cap."""
    if type(budget) is not int or not 0 <= budget <= 20_000:
        raise ValueError("development budget must be an integer in [0, 20000]")
    import gmi_k4_search_v5 as legacy
    return audit_receipt(legacy.run_cell(family, grammar, cell, freeze=copy.deepcopy(freeze),
                                        seed=seed, budget=budget))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit_receipt(json.loads(args.receipt.read_text())), indent=2))


if __name__ == "__main__":
    main()

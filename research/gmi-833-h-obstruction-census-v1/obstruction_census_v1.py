#!/usr/bin/env python3
"""Exact finite obstruction census for Issue #833 Section H.

The implementation deliberately works only with external Boolean truth tables.
Family names are metadata in the frozen registry and never grammar primitives.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
REGISTRY_PATH = HERE / "FROZEN_FAMILY_REGISTRY_V1.json"
RESULT_PATH = HERE / "RESULT_V1.json"
REGISTRY_SHA256 = "296dac889f8711f8c2703df70c349e121a1a9a693f897f241c7b1d8ba8f543ce"

N_COORDS = 8
N_ROWS = 1 << N_COORDS
FULL_MASK = (1 << N_ROWS) - 1
BUDGET = 3
LOWER_BOUND_LIMIT = 5
VISIBLE_COORDS = (0, 1, 2, 3)
UNAVAILABLE_COORDS = (4, 5, 6, 7)
OBSERVATION_ROWS = tuple(range(8))  # x0..x2 vary; x3..x7 are zero.

DISPOSITIONS = (
    "RECOVERED_CONTROL",
    "IDENTIFIABILITY_OBSTRUCTION",
    "RESOURCE_OBSTRUCTION",
    "EXPRESSIVITY_OBSTRUCTION",
)

EXPECTED_ROWS = (
    "Finite-state/automata intelligence.",
    "Linear regression / linear classifiers.",
    "GLMs.",
    "Basis/kernel methods.",
    "Nearest-neighbor / exemplar memory.",
    "Associative memory.",
    "Retrieval-augmented systems.",
    "Decision trees/rule systems.",
    "Symbolic logic systems.",
    "Program synthesis/program induction.",
    "Library-learning/program-reuse systems.",
    "Search/frontier algorithms.",
    "Planning systems.",
    "Dynamic programming/control.",
    "Model-free RL-like learning.",
    "Model-based RL-like learning.",
    "Bayesian inference/belief-state systems.",
    "Probabilistic graphical models.",
    "Particle/population inference.",
    "Feed-forward neural networks.",
    "Backprop/reverse-mode credit assignment.",
    "CNN/equivariant local-weight-sharing systems.",
    "RNNs.",
    "LSTM/GRU-like gating.",
    "Attention mechanisms.",
    "Transformer-like dynamic routing/composition.",
    "Graph neural/message-passing systems.",
    "State-space models.",
    "Mixture-of-experts/routing systems.",
    "Autoregressive generative systems.",
    "Latent-variable generative systems.",
    "Flow-like transport systems.",
    "Diffusion/iterative-refinement systems.",
    "Energy-based systems.",
    "Evolutionary/population search.",
    "Cellular/local-field computation.",
    "Distributed/collective intelligence.",
    "Tool-using/solver-routing intelligence.",
    "Neuro-symbolic/statistical-symbolic hybrids.",
    "Continual-learning systems.",
    "Meta-learning systems.",
    "Self-modifying/morphogenetic systems.",
    "Multi-agent emergent communication systems.",
)


class CensusError(RuntimeError):
    """Fail-closed validation error."""


@dataclass(frozen=True)
class Representative:
    cost: int
    expression: str


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def variable_table(coordinate: int) -> int:
    if type(coordinate) is not int or not 0 <= coordinate < N_COORDS:
        raise CensusError("coordinate must be a non-Boolean integer in [0,7]")
    table = 0
    for row in range(N_ROWS):
        table |= ((row >> coordinate) & 1) << row
    return table


VARIABLES = tuple(variable_table(i) for i in range(N_COORDS))


def table_digest(table: int) -> str:
    if type(table) is not int or not 0 <= table <= FULL_MASK:
        raise CensusError("truth table outside the registered interface")
    return sha256_bytes(table.to_bytes(N_ROWS // 8, "little"))


def projection(table: int, rows: Sequence[int] = OBSERVATION_ROWS) -> Tuple[int, ...]:
    return tuple((table >> row) & 1 for row in rows)


def flip_invariant(table: int, coordinate: int) -> bool:
    stride = 1 << coordinate
    for row in range(N_ROWS):
        if row & stride:
            continue
        if ((table >> row) & 1) != ((table >> (row | stride)) & 1):
            return False
    return True


def target_tables() -> Dict[str, int]:
    x = VARIABLES
    return {
        "COPY_SIGNAL": x[0],
        "INVERT_SIGNAL": FULL_MASK ^ x[0],
        "PAIR_PARITY": x[0] ^ x[1],
        "PAIR_CONJUNCTION": x[0] & x[1],
        "TRIPLE_PARITY": x[0] ^ x[1] ^ x[2],
        "TRIPLE_CONJUNCTION": x[0] & x[1] & x[2],
        "UNEXCITED_CONTEXT": x[3],
        "HISTORY_STATE_CHANNEL": x[4],
        "STOCHASTIC_SOURCE_CHANNEL": x[5],
        "UPDATE_FEEDBACK_CHANNEL": x[6],
        "EXTERNAL_PEER_TOOL_CHANNEL": x[7],
    }


def _record_candidate(
    candidates: Dict[int, str], table: int, expression: str
) -> None:
    previous = candidates.get(table)
    if previous is None or expression < previous:
        candidates[table] = expression


def enumerate_minimum_semantics(max_cost: int) -> Tuple[Dict[int, Representative], Dict[int, Dict[int, str]]]:
    """Enumerate the exact semantic quotient by minimum node cost.

    Keeping only minimum-cost subexpressions is complete: replacing a
    non-minimal subexpression by a cheaper extensionally equal one preserves
    the enclosing denotation and lowers its total cost.
    """
    if type(max_cost) is not int or not 1 <= max_cost <= 9:
        raise CensusError("max_cost must be a non-Boolean integer in [1,9]")
    leaves = {0: "0", FULL_MASK: "1"}
    for coordinate in VISIBLE_COORDS:
        leaves[VARIABLES[coordinate]] = "x%d" % coordinate
    exact: Dict[int, Dict[int, str]] = {1: dict(sorted(leaves.items()))}
    best: Dict[int, Representative] = {
        table: Representative(1, expression) for table, expression in exact[1].items()
    }
    for cost in range(2, max_cost + 1):
        proposed: Dict[int, str] = {}
        for child, child_expression in exact.get(cost - 1, {}).items():
            _record_candidate(proposed, FULL_MASK ^ child, "NOT(%s)" % child_expression)
        for left_cost in range(1, cost - 1):
            right_cost = cost - 1 - left_cost
            if right_cost < 1:
                continue
            for left, left_expression in exact.get(left_cost, {}).items():
                for right, right_expression in exact.get(right_cost, {}).items():
                    ordered = tuple(sorted((left_expression, right_expression)))
                    _record_candidate(proposed, left ^ right, "XOR(%s,%s)" % ordered)
                    _record_candidate(proposed, left & right, "AND(%s,%s)" % ordered)
        layer: Dict[int, str] = {}
        for table, expression in sorted(proposed.items()):
            previous = best.get(table)
            if previous is None:
                layer[table] = expression
                best[table] = Representative(cost, expression)
            elif previous.cost == cost and expression < previous.expression:
                layer[table] = expression
                best[table] = Representative(cost, expression)
        exact[cost] = layer
    return best, exact


def candidate_records(best: Mapping[int, Representative], budget: int = BUDGET) -> List[dict]:
    rows = []
    for index, (table, rep) in enumerate(
        sorted((item for item in best.items() if item[1].cost <= budget), key=lambda item: (item[1].cost, item[1].expression, item[0]))
    ):
        rows.append(
            {
                "candidate_id": "C%04d" % index,
                "cost": rep.cost,
                "expression": rep.expression,
                "table": table,
            }
        )
    return rows


def classify_from_records(
    records: Sequence[Mapping[str, object]],
    target: int,
    observation_rows: Sequence[int] = OBSERVATION_ROWS,
) -> dict:
    observed = projection(target, observation_rows)
    fits = [
        row
        for row in records
        if projection(int(row["table"]), observation_rows) == observed
    ]
    if not fits:
        return {
            "minimum_fit_cost": None,
            "minimum_fit_tables": [],
            "minimum_fit_digests": [],
            "identified": False,
        }
    minimum = min(int(row["cost"]) for row in fits)
    minimum_rows = [row for row in fits if int(row["cost"]) == minimum]
    tables = sorted({int(row["table"]) for row in minimum_rows})
    return {
        "minimum_fit_cost": minimum,
        "minimum_fit_tables": tables,
        "minimum_fit_digests": [table_digest(table) for table in tables],
        "identified": len(tables) == 1 and tables[0] == target,
    }


def load_registry(path: Path = REGISTRY_PATH) -> dict:
    if path.resolve() == REGISTRY_PATH.resolve() and file_sha256(path) != REGISTRY_SHA256:
        raise CensusError("frozen family registry hash mismatch")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "GMI833HObstructionFamilyRegistryV1":
        raise CensusError("unknown registry schema")
    families = data.get("families")
    if not isinstance(families, list) or len(families) != 43:
        raise CensusError("registry must contain exactly 43 family rows")
    ids = [row.get("id") for row in families]
    rows = [row.get("row") for row in families]
    if len(set(ids)) != 43 or tuple(rows) != EXPECTED_ROWS:
        raise CensusError("family registry is incomplete, duplicated, or out of order")
    targets = target_tables()
    for row in families:
        if row.get("contract") not in targets or not row.get("hallmark"):
            raise CensusError("family row has an unknown or empty contract")
    return data


def disposition_for_target(
    target_name: str,
    best: Mapping[int, Representative],
    records: Sequence[Mapping[str, object]],
) -> Tuple[str, dict]:
    targets = target_tables()
    target = targets[target_name]
    if target_name in {
        "HISTORY_STATE_CHANNEL",
        "STOCHASTIC_SOURCE_CHANNEL",
        "UPDATE_FEEDBACK_CHANNEL",
        "EXTERNAL_PEER_TOOL_CHANNEL",
    }:
        varied_coordinate = {
            "HISTORY_STATE_CHANNEL": 4,
            "STOCHASTIC_SOURCE_CHANNEL": 5,
            "UPDATE_FEEDBACK_CHANNEL": 6,
            "EXTERNAL_PEER_TOOL_CHANNEL": 7,
        }[target_name]
        return "EXPRESSIVITY_OBSTRUCTION", {
            "varied_coordinate": varied_coordinate,
            "target_changes_on_coordinate": not flip_invariant(target, varied_coordinate),
            "grammar_invariant_by_induction": True,
            "minimum_cost": None,
        }
    representative = best.get(target)
    if representative is None:
        raise CensusError("registered available-coordinate target absent through lower-bound limit")
    if representative.cost > BUDGET:
        return "RESOURCE_OBSTRUCTION", {
            "budget": BUDGET,
            "minimum_cost": representative.cost,
            "witness": representative.expression,
            "complete_absence_through_budget": True,
        }
    selection = classify_from_records(records, target)
    if not selection["identified"]:
        return "IDENTIFIABILITY_OBSTRUCTION", {
            "target_minimum_cost": representative.cost,
            "observation_rows": list(OBSERVATION_ROWS),
            "selection": selection,
        }
    return "RECOVERED_CONTROL", {
        "minimum_cost": representative.cost,
        "witness": representative.expression,
        "selection": selection,
    }


def remint_records(records: Sequence[Mapping[str, object]], mode: str) -> List[dict]:
    if mode == "reverse":
        order = list(reversed(records))
    elif mode == "digest":
        order = sorted(records, key=lambda row: sha256_bytes(str(row["candidate_id"]).encode("utf-8")))
    else:
        raise CensusError("unknown remint mode")
    reminted = []
    for index, row in enumerate(order):
        copy = dict(row)
        copy["candidate_id"] = "%s_R%04d" % (mode.upper(), index)
        reminted.append(copy)
    return reminted


def build_result(registry_path: Path = REGISTRY_PATH) -> dict:
    registry = load_registry(registry_path)
    best, exact = enumerate_minimum_semantics(LOWER_BOUND_LIMIT)
    records = candidate_records(best)
    targets = target_tables()
    target_results = {}
    for name in sorted(targets):
        disposition, evidence = disposition_for_target(name, best, records)
        target_results[name] = {
            "disposition": disposition,
            "target_digest": table_digest(targets[name]),
            "evidence": evidence,
        }

    all_invariant = all(
        flip_invariant(table, coordinate)
        for table in best
        for coordinate in UNAVAILABLE_COORDS
    )
    if not all_invariant:
        raise CensusError("enumerated grammar violates the analytic invariant")

    baseline = {
        name: classify_from_records(records, table) for name, table in targets.items()
    }
    remint_checks = {}
    for mode in ("reverse", "digest"):
        reminted = remint_records(records, mode)
        remint_checks[mode] = all(
            classify_from_records(reminted, table) == baseline[name]
            for name, table in targets.items()
        )
    if not all(remint_checks.values()):
        raise CensusError("candidate remint changed a scientific result")

    budget_five_records = candidate_records(best, budget=5)
    budget_hostile = classify_from_records(
        budget_five_records, targets["TRIPLE_PARITY"]
    )
    expanded_context_rows = tuple(range(16))
    ecology_hostile = classify_from_records(
        records, targets["UNEXCITED_CONTEXT"], expanded_context_rows
    )
    expanded_x4_rows = tuple(range(32))
    expanded_leaf_tables = [0, FULL_MASK] + [VARIABLES[i] for i in range(5)]
    expanded_x4_fits = [
        table
        for table in expanded_leaf_tables
        if projection(table, expanded_x4_rows)
        == projection(targets["HISTORY_STATE_CHANNEL"], expanded_x4_rows)
    ]
    grammar_ecology_hostile = {
        "expanded_leaf_set": ["0", "1", "x0", "x1", "x2", "x3", "x4"],
        "expanded_observation_rows": len(expanded_x4_rows),
        "minimum_cost": 1,
        "identified": expanded_x4_fits == [targets["HISTORY_STATE_CHANNEL"]],
        "minimum_fit_digests": [table_digest(table) for table in expanded_x4_fits],
    }
    if not budget_hostile["identified"] or not ecology_hostile["identified"] or not grammar_ecology_hostile["identified"]:
        raise CensusError("scope-sensitivity hostile failed to remove an obstruction")

    census = []
    counts = {key: 0 for key in DISPOSITIONS}
    for family in registry["families"]:
        target_result = target_results[family["contract"]]
        predicted = registry["target_contracts"][family["contract"]]["predicted_disposition"]
        if target_result["disposition"] != predicted:
            raise CensusError("post-freeze disposition differs from prediction")
        disposition = target_result["disposition"]
        counts[disposition] += 1
        census.append(
            {
                "id": family["id"],
                "row": family["row"],
                "registered_hallmark": family["hallmark"],
                "mapping_status": "AUTHORED_POSTHOC_EVALUATION_PRIOR",
                "historical_family_definition": "INCOMPLETE_BY_DESIGN",
                "contract": family["contract"],
                "disposition": disposition,
                "target_digest": target_result["target_digest"],
                "named_family_checkbox": "MUST_REMAIN_OPEN",
            }
        )
    if counts != registry["predicted_counts"]:
        raise CensusError("census count mismatch")

    return {
        "schema": "GMI833HObstructionCensusResultV1",
        "source_base": registry["source"]["source_base"],
        "source_issue_body_sha256": registry["source"]["issue_body_sha256"],
        "freeze_commit": "d2cbd897890e67a2866552b4df50b7583a2f3ceb",
        "scope": {
            "interface": "{0,1}^8",
            "visible_coordinates": list(VISIBLE_COORDS),
            "unavailable_coordinates": list(UNAVAILABLE_COORDS),
            "leaves": ["0", "1", "x0", "x1", "x2", "x3"],
            "operators": ["NOT", "XOR", "AND"],
            "node_budget": BUDGET,
            "lower_bound_enumeration_limit": LOWER_BOUND_LIMIT,
            "protected_rows": N_ROWS,
            "observation_rows": list(OBSERVATION_ROWS),
            "search": "complete semantic quotient then exact node-cost minimization without extra tie-breaker",
        },
        "registry_prior": {
            "status": "AUTHORED_POSTHOC_EVALUATION_PRIOR",
            "rationales": "one external-semantics rationale per family_census row, frozen before checker implementation",
            "boundary": "a hallmark is neither a complete definition nor proof of full recovery/non-recovery of its historical family",
        },
        "semantic_quotient": {
            "new_semantics_by_minimum_cost": {
                str(cost): len(exact[cost]) for cost in range(1, LOWER_BOUND_LIMIT + 1)
            },
            "through_budget": sum(len(exact[cost]) for cost in range(1, BUDGET + 1)),
            "through_lower_bound_limit": len(best),
        },
        "theorems": {
            "EXPRESSIVITY": {
                "enumerated_invariant_check": all_invariant,
                "analytic_rule": "structural induction: every leaf is invariant in x4..x7 and every operator preserves invariance",
            },
            "RESOURCE": {
                "TRIPLE_PARITY_minimum_cost": best[targets["TRIPLE_PARITY"]].cost,
                "TRIPLE_CONJUNCTION_minimum_cost": best[targets["TRIPLE_CONJUNCTION"]].cost,
                "budget": BUDGET,
            },
            "IDENTIFIABILITY": target_results["UNEXCITED_CONTEXT"],
            "POSITIVE_CONTROLS": {
                name: target_results[name]
                for name in ("COPY_SIGNAL", "INVERT_SIGNAL", "PAIR_PARITY", "PAIR_CONJUNCTION")
            },
            "REMINT": {"modes": remint_checks, "target_checks": len(targets) * len(remint_checks)},
            "SCOPE_SENSITIVITY_HOSTILES": {
                "budget_expansion": {
                    "target": "TRIPLE_PARITY",
                    "baseline": "RESOURCE_OBSTRUCTION_AT_B3",
                    "expanded_budget": 5,
                    "expanded_result": budget_hostile,
                },
                "ecology_expansion": {
                    "target": "UNEXCITED_CONTEXT",
                    "baseline": "IDENTIFIABILITY_OBSTRUCTION_WITH_X3_FIXED_ZERO",
                    "expanded_ecology": "all 16 assignments of x0..x3 with x4..x7 fixed zero",
                    "expanded_result": ecology_hostile,
                },
                "grammar_and_ecology_expansion": {
                    "target": "HISTORY_STATE_CHANNEL",
                    "baseline": "EXPRESSIVITY_OBSTRUCTION_WITH_X4_ABSENT",
                    "expanded_result": grammar_ecology_hostile,
                },
                "conclusion": "obstruction classes are scope-relative and may disappear when grammar, ecology, or budget expands",
            },
        },
        "target_results": target_results,
        "family_census": census,
        "counts": counts,
        "family_gate_audit": {
            "eligible_named_family_rows": 0,
            "all_named_family_rows": "MUST_REMAIN_OPEN",
            "reason": "this package supplies neither a complete ten-gate ledger nor real-scale evidence",
        },
        "forbidden_promotions": registry["forbidden_claims"],
        "verdict": "REGISTERED_43_FAMILY_HALLMARK_CENSUS_COMPLETE__UNIVERSAL_NONRECOVERABILITY_FORBIDDEN",
    }


def write_or_check(path: Path, check: bool) -> None:
    payload = canonical_bytes(build_result())
    if check:
        if not path.exists() or path.read_bytes() != payload:
            raise CensusError("RESULT_V1.json is absent or stale")
        print("RESULT_V1_OK sha256=%s" % sha256_bytes(payload))
    else:
        path.write_bytes(payload)
        print("wrote %s sha256=%s" % (path, sha256_bytes(payload)))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    write_or_check(RESULT_PATH, args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

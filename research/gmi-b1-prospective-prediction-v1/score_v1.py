from __future__ import annotations

import copy
import hashlib
import itertools
import json
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

HERE = Path(__file__).resolve().parent
PREDICTIONS_PATH = HERE / "PREDICTIONS_V1.json"
PREDICTION_AUTHORITY_COMMIT = "0be66ccebf50bd7e0fac31421b052d2d858adbce"
FREEZE_COMMIT = "526ff2d4ddee43abc2cf69e8ef820e9b55278154"

FORBIDDEN_CASE_KEYS = {
    "family",
    "family_name",
    "architecture",
    "architecture_name",
    "phenotype",
    "donor_path",
    "donor_file",
    "measured",
    "outcome",
    "result",
}
ALLOWED_CASE_KEYS = {
    "case_id",
    "object_kind",
    "period",
    "accepted_residue",
    "dimension",
    "coefficients",
    "coefficient_grid",
    "expected",
}


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_predictions(payload: Mapping[str, object]) -> None:
    if payload.get("schema") != "B1ProspectivePredictionsV1":
        raise ValueError("wrong prediction schema")
    if payload.get("freeze_commit") != FREEZE_COMMIT:
        raise ValueError("wrong freeze authority")
    if payload.get("outcomes_seen") is not False:
        raise ValueError("prediction receipt is outcome-contaminated")
    if payload.get("scorer_exists") is not False:
        raise ValueError("prediction receipt claims scorer existed")
    if payload.get("surface_remints_materialized") is not False:
        raise ValueError("prediction receipt claims remints existed")
    cases = payload.get("cases")
    if not isinstance(cases, list) or len(cases) != 8:
        raise ValueError("expected eight protected prediction cases")
    seen = set()
    for row in cases:
        if not isinstance(row, Mapping):
            raise ValueError("prediction case must be object")
        if FORBIDDEN_CASE_KEYS.intersection(row):
            raise ValueError("family/architecture/outcome field leaked into case")
        if set(row) - ALLOWED_CASE_KEYS:
            raise ValueError("unexpected predictor-visible field")
        cid = row.get("case_id")
        if not isinstance(cid, str) or cid in seen:
            raise ValueError("invalid/duplicate case id")
        seen.add(cid)
        if row.get("object_kind") not in {
            "periodic_sequence_response",
            "finite_coefficient_identification",
        }:
            raise ValueError("unknown generic object kind")


def load_predictions() -> Mapping[str, object]:
    payload = json.loads(PREDICTIONS_PATH.read_text())
    validate_predictions(payload)
    return payload


def _surface_tokens(case_id: str, remint: int) -> Tuple[str, str]:
    if remint not in (1, 2):
        raise ValueError("unknown remint")
    domain = "T602-B1P-B2-SURFACE" if remint == 1 else "T602-B1P-B2-SURFACE-ALT"
    return tuple(
        "S_" + _digest(f"{domain}|{PREDICTION_AUTHORITY_COMMIT}|{case_id}|{j}")[:12]
        for j in (0, 1)
    )  # type: ignore[return-value]


def _response(history: Sequence[str], token1: str, period: int, residue: int) -> bool:
    return sum(1 for item in history if item == token1) % period == residue


def _residue_signatures(token1: str, period: int, residue: int) -> Tuple[Tuple[bool, ...], ...]:
    signatures = []
    for start_residue in range(period):
        sig = []
        for added in range(period):
            history = [token1] * (start_residue + added)
            sig.append(_response(history, token1, period, residue))
        signatures.append(tuple(sig))
    return tuple(signatures)


def _all_residue_pairs_separated(token1: str, period: int, residue: int) -> bool:
    sigs = _residue_signatures(token1, period, residue)
    return all(sigs[a] != sigs[b] for a, b in itertools.combinations(range(period), 2))


def _replay_period_machine(tokens: Tuple[str, str], period: int, residue: int) -> bool:
    token0, token1 = tokens
    horizon = period + 2
    for length in range(horizon + 1):
        for history in itertools.product(tokens, repeat=length):
            state = 0
            for item in history:
                if item == token1:
                    state = (state + 1) % period
                elif item != token0:
                    raise AssertionError("surface token outside remint")
            machine = state == residue
            oracle = _response(history, token1, period, residue)
            if machine != oracle:
                return False
    return True


def _stateless_sufficient(tokens: Tuple[str, str], period: int, residue: int) -> bool:
    buckets: Dict[str, set] = {"<empty>": set(), tokens[0]: set(), tokens[1]: set()}
    horizon = period + 2
    for length in range(horizon + 1):
        for history in itertools.product(tokens, repeat=length):
            key = "<empty>" if not history else history[-1]
            buckets[key].add(_response(history, tokens[1], period, residue))
    return all(len(values) <= 1 for values in buckets.values())


def _score_periodic_case(row: Mapping[str, object], remint: int) -> Mapping[str, object]:
    case_id = str(row["case_id"])
    period = int(row["period"])
    residue = int(row["accepted_residue"])
    tokens = _surface_tokens(case_id, remint)
    sigs = _residue_signatures(tokens[1], period, residue)
    q = len(set(sigs))
    pairwise = _all_residue_pairs_separated(tokens[1], period, residue)
    replay = _replay_period_machine(tokens, period, residue)
    stateless = _stateless_sufficient(tokens, period, residue)
    return {
        "quotient_classes": q,
        "minimal_recurrent_states": q if pairwise and replay else None,
        "all_residue_pairs_future_distinguishable": pairwise,
        "stateless_sufficient": stateless,
        "history_cheaper_below_length": q,
        "tie_at_length": q,
        "state_first_cheaper_length": q + 1,
        "exact_period_state_realization_exists": replay,
    }


def _feature_order(case_id: str, d: int, remint: int) -> Tuple[int, ...]:
    if remint not in (1, 2):
        raise ValueError("unknown remint")
    domain = "T602-B1P-B3-FEATURE" if remint == 1 else "T602-B1P-B3-FEATURE-ALT"
    keyed = []
    for index in range(d):
        keyed.append((_digest(f"{domain}|{PREDICTION_AUTHORITY_COMMIT}|{case_id}|{index}"), index))
    return tuple(index for _, index in sorted(keyed))


def _basis_vector(d: int, index: int) -> Tuple[int, ...]:
    return tuple(1 if j == index else 0 for j in range(d))


def _dot(weights: Sequence[int], x: Sequence[int]) -> int:
    return sum(int(w) * int(v) for w, v in zip(weights, x))


def _candidate_count(
    d: int,
    grid: Sequence[int],
    observations: Iterable[Tuple[Tuple[int, ...], int]],
) -> int:
    obs = tuple(observations)
    count = 0
    for candidate in itertools.product(grid, repeat=d):
        if all(_dot(candidate, x) == y for x, y in obs):
            count += 1
    return count


def _monomial_basis_size(d: int) -> int:
    subsets = []
    for degree in range(d + 1):
        subsets.extend(itertools.combinations(range(d), degree))
    return len(subsets)


def _boolean_table_size(d: int) -> int:
    return sum(1 for _ in itertools.product((0, 1), repeat=d))


def _score_coefficient_case(row: Mapping[str, object], remint: int) -> Mapping[str, object]:
    case_id = str(row["case_id"])
    d = int(row["dimension"])
    weights = tuple(int(v) for v in row["coefficients"])
    grid = tuple(int(v) for v in row["coefficient_grid"])
    order = _feature_order(case_id, d, remint)
    independent = tuple(_basis_vector(d, index) for index in order)

    def obs(xs: Sequence[Tuple[int, ...]]):
        return tuple((x, _dot(weights, x)) for x in xs)

    count_dm1 = _candidate_count(d, grid, obs(independent[: d - 1]))
    count_d = _candidate_count(d, grid, obs(independent))
    dependent_xs = independent[: d - 1] + (independent[0],)
    count_dep = _candidate_count(d, grid, obs(dependent_xs))

    identified_at = None
    for n in range(d + 1):
        if _candidate_count(d, grid, obs(independent[:n])) == 1:
            identified_at = n
            break

    return {
        "consistent_after_d_minus_1_independent": count_dm1,
        "consistent_after_d_independent": count_d,
        "consistent_after_d_dependent": count_dep,
        "identified_at_independent_n": identified_at,
        "dependent_d_identifies": count_dep == 1,
        "full_boolean_monomial_basis_size": _monomial_basis_size(d),
        "boolean_input_table_size": _boolean_table_size(d),
    }


def _score_row(row: Mapping[str, object], remint: int) -> Mapping[str, object]:
    if row["object_kind"] == "periodic_sequence_response":
        return _score_periodic_case(row, remint)
    if row["object_kind"] == "finite_coefficient_identification":
        return _score_coefficient_case(row, remint)
    raise ValueError("unknown object kind")


def _current_symbol_only_control() -> Mapping[str, object]:
    tokens = _surface_tokens("NEG_CURRENT_SYMBOL", 1)
    values: Dict[str, set] = {"<empty>": set(), tokens[0]: set(), tokens[1]: set()}
    for length in range(8):
        for history in itertools.product(tokens, repeat=length):
            key = "<empty>" if not history else history[-1]
            response = bool(history and history[-1] == tokens[1])
            values[key].add(response)
    sufficient = all(len(bucket) <= 1 for bucket in values.values())
    if not sufficient:
        raise AssertionError("current-symbol-only control should be stateless-sufficient")
    return {"stateless_sufficient": sufficient, "control_fired": True}


def _label_injection_control(payload: Mapping[str, object]) -> Mapping[str, object]:
    mutant = copy.deepcopy(payload)
    mutant["cases"][0]["family_name"] = "forbidden"
    rejected = False
    try:
        validate_predictions(mutant)
    except ValueError:
        rejected = True
    if not rejected:
        raise AssertionError("label-injection hostile did not fire")
    return {"rejected": True}


def _prediction_tamper_control(payload: Mapping[str, object]) -> Mapping[str, object]:
    mutant = copy.deepcopy(payload)
    mutant["cases"][0]["expected"]["quotient_classes"] += 1
    measured = _score_row(mutant["cases"][0], 1)
    mismatch = measured != mutant["cases"][0]["expected"]
    if not mismatch:
        raise AssertionError("prediction tamper was not detected")
    return {"mismatch_detected": True}


def build_result() -> Mapping[str, object]:
    predictions = load_predictions()
    rows = []
    all_match = True
    all_remint_invariant = True
    for row in predictions["cases"]:
        expected = row["expected"]
        measured_1 = _score_row(row, 1)
        measured_2 = _score_row(row, 2)
        match_1 = measured_1 == expected
        match_2 = measured_2 == expected
        invariant = measured_1 == measured_2
        all_match = all_match and match_1 and match_2
        all_remint_invariant = all_remint_invariant and invariant
        rows.append(
            {
                "case_id": row["case_id"],
                "object_kind": row["object_kind"],
                "expected": expected,
                "measured_remint_1": measured_1,
                "measured_remint_2": measured_2,
                "match_remint_1": match_1,
                "match_remint_2": match_2,
                "surface_remint_invariant": invariant,
            }
        )

    hostiles = {
        "prediction_tamper": _prediction_tamper_control(predictions),
        "label_injection": _label_injection_control(predictions),
        "current_symbol_only_negative": _current_symbol_only_control(),
        "dependent_observation_negative": {
            "all_registered_cases_remain_ambiguous": all(
                r["measured_remint_1"].get("dependent_d_identifies") is False
                for r in rows
                if r["object_kind"] == "finite_coefficient_identification"
            )
        },
    }
    if not hostiles["dependent_observation_negative"]["all_registered_cases_remain_ambiguous"]:
        raise AssertionError("dependent-observation hostile failed")

    green = all_match and all_remint_invariant and all(
        (
            hostiles["prediction_tamper"]["mismatch_detected"],
            hostiles["label_injection"]["rejected"],
            hostiles["current_symbol_only_negative"]["control_fired"],
            hostiles["dependent_observation_negative"]["all_registered_cases_remain_ambiguous"],
        )
    )
    return {
        "schema": "B1ProspectivePredictionResultV1",
        "issue": 776,
        "freeze_commit": FREEZE_COMMIT,
        "prediction_authority_commit": PREDICTION_AUTHORITY_COMMIT,
        "scorer_imports_prediction_implementation": False,
        "protected_case_count": len(rows),
        "cases": rows,
        "all_predictions_match": all_match,
        "all_surface_remints_invariant": all_remint_invariant,
        "hostiles": hostiles,
        "status": "PASS" if green else "FAIL",
        "terminal": (
            "B1_PREOUTCOME_PREDICTION_CUSTODY_SUPPORTED_ON_TWO_FRESH_EXACT_FAMILY_REMINTS"
            if green
            else "B1_PREOUTCOME_PREDICTION_CUSTODY_NOT_SUPPORTED"
        ),
        "claim_ceiling": "two exact family remints; not B1/global known-family closure",
        "nonclaims": [
            "B1_COMMON_PROTOCOL_CLOSED",
            "KNOWN_FORM_ZERO_PRIOR_DERIVATION_GREEN_AT_REGISTERED_SCOPE",
            "ALL_KNOWN_FAMILIES_PROSPECTIVELY_VALIDATED",
            "REAL_REGIME_REPLICATION_COMPLETE",
            "COMPLETE_GMI",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(build_result(), indent=2, sort_keys=True))

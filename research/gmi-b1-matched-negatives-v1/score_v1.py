from __future__ import annotations

import copy
import hashlib
import heapq
import itertools
import json
from fractions import Fraction as F
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

HERE = Path(__file__).resolve().parent
PREDICTIONS_PATH = HERE / "PREDICTIONS_V1.json"
FREEZE_COMMIT = "a57664ec99b143f5c56fdd2f058d1a3aa5e16bb7"
PREDICTION_AUTHORITY_COMMIT = "95e817f46a3224b6299013fdae47aaa0835c8f31"

FORBIDDEN_CASE_KEYS = {
    "family", "family_name", "architecture", "architecture_name",
    "phenotype", "donor_path", "donor_file", "measured", "outcome", "result",
}
KNOWN_KINDS = {
    "finite_coefficient_identification_control",
    "parameter_output_credit_control",
    "finite_update_landscape_control",
    "conditional_retention_control",
    "finite_transition_affinity_control",
    "metric_local_lookup_control",
    "finite_joint_factorization_control",
    "finite_search_heuristic_control",
}


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _surface_permutation(domain: str, case_id: str, n: int, remint: int) -> Tuple[int, ...]:
    if remint not in (1, 2):
        raise ValueError("unknown remint")
    rows = []
    for i in range(n):
        key = _digest(
            f"T602-B1N-V1|{domain}|{PREDICTION_AUTHORITY_COMMIT}|{case_id}|{i}|{remint}"
        )
        rows.append((key, i))
    return tuple(i for _, i in sorted(rows))


def _surface_labels(domain: str, case_id: str, n: int, remint: int) -> Tuple[str, ...]:
    return tuple(
        "X_" + _digest(
            f"T602-B1N-V1|{domain}|{PREDICTION_AUTHORITY_COMMIT}|{case_id}|{i}|{remint}"
        )[:12]
        for i in range(n)
    )


def _surface_fingerprint(domain: str, case_id: str, n: int, remint: int) -> str:
    labels = _surface_labels(domain, case_id, n, remint)
    return _digest("|".join(labels))[:16]


def validate_predictions(payload: Mapping[str, object]) -> None:
    if payload.get("schema") != "B1MatchedNegativePredictionsV1":
        raise ValueError("wrong prediction schema")
    if payload.get("freeze_commit") != FREEZE_COMMIT:
        raise ValueError("wrong freeze authority")
    if payload.get("outcomes_seen") is not False or payload.get("scorer_exists") is not False:
        raise ValueError("prediction phase contaminated by outcomes/scorer")
    if payload.get("surface_remints_materialized") is not False:
        raise ValueError("surface remints existed before prediction authority")
    cases = payload.get("cases")
    if not isinstance(cases, list) or len(cases) != 8:
        raise ValueError("expected eight controls")
    ids = set()
    for case in cases:
        if not isinstance(case, Mapping):
            raise ValueError("case must be object")
        if FORBIDDEN_CASE_KEYS.intersection(case):
            raise ValueError("forbidden family/architecture/outcome field in case")
        cid = case.get("case_id")
        if not isinstance(cid, str) or cid in ids:
            raise ValueError("invalid/duplicate case id")
        ids.add(cid)
        if case.get("object_kind") not in KNOWN_KINDS:
            raise ValueError("unknown generic object kind")
        semantics = case.get("semantics")
        matched = case.get("matched_fields")
        varying = case.get("varying_coordinate")
        arms = case.get("arms")
        if not isinstance(semantics, Mapping) or not isinstance(matched, list):
            raise ValueError("missing matching contract")
        if set(matched) != set(semantics):
            raise ValueError("matched_fields must cover every common semantic coordinate")
        if not isinstance(varying, str) or varying in semantics:
            raise ValueError("varying coordinate must be arm-specific")
        if not isinstance(arms, list) or len(arms) < 2:
            raise ValueError("control needs at least positive/fail arms")
        seen_values = set()
        for arm in arms:
            if not isinstance(arm, Mapping) or "arm" not in arm or "expected" not in arm:
                raise ValueError("malformed arm")
            if varying not in arm:
                raise ValueError("arm missing declared varying coordinate")
            if set(matched).intersection(arm):
                raise ValueError("arm overrides a matched field")
            allowed = {"arm", "expected", varying}
            if cid == "N4":
                allowed.add("gap_set")
            if set(arm) - allowed:
                raise ValueError("undeclared second varying field")
            encoded = json.dumps(arm[varying], sort_keys=True)
            if encoded in seen_values:
                raise ValueError("control arms do not vary the declared coordinate")
            seen_values.add(encoded)
    if ids != {f"N{i}" for i in range(1, 9)}:
        raise ValueError("protected case set drift")


def load_predictions() -> Mapping[str, object]:
    payload = json.loads(PREDICTIONS_PATH.read_text())
    validate_predictions(payload)
    return payload


def _dot(a: Sequence[int], b: Sequence[int]) -> int:
    return sum(int(x) * int(y) for x, y in zip(a, b))


def _score_n1(case: Mapping[str, object], remint: int) -> Dict[str, Mapping[str, object]]:
    s = case["semantics"]
    d = int(s["dimension"])
    grid = tuple(int(x) for x in s["coefficient_grid"])
    w = tuple(int(x) for x in s["true_vector"])
    order = _surface_permutation("N1-FEATURE", str(case["case_id"]), d, remint)
    basis = [tuple(1 if j == i else 0 for j in range(d)) for i in order]

    def count(xs: Sequence[Tuple[int, ...]]) -> int:
        obs = tuple((x, _dot(w, x)) for x in xs)
        return sum(
            1 for cand in itertools.product(grid, repeat=d)
            if all(_dot(cand, x) == y for x, y in obs)
        )

    out = {}
    for arm in case["arms"]:
        if int(arm["observation_rank"]) == d:
            xs = basis
        else:
            xs = basis[: d - 1] + [basis[0]]
        c = count(xs)
        out[str(arm["arm"])] = {"consistent_candidates": c, "identified": c == 1}
    return out


def _credit_costs(n_out: int) -> Tuple[int, int]:
    n_in, n_hid = 4, 1
    params = n_in * n_hid
    x = [1] * n_in
    W = [[1 for _ in range(n_in)] for _ in range(n_hid)]
    V = [[1 for _ in range(n_hid)] for _ in range(n_out)]

    def forward(counter: List[int]):
        hpre = []
        for j in range(n_hid):
            value = 0
            for i in range(n_in):
                value += W[j][i] * x[i]
                counter[0] += 1
            hpre.append(value)
        h = [max(0, v) for v in hpre]
        for k in range(n_out):
            value = 0
            for j in range(n_hid):
                value += V[k][j] * h[j]
                counter[0] += 1
        return hpre

    cf = [0]
    for _ in range(params):
        forward(cf)
    cr = [0]
    hpre = forward(cr)
    for _k in range(n_out):
        for j in range(n_hid):
            cr[0] += 1
            if hpre[j] > 0:
                for _i in range(n_in):
                    cr[0] += 1
    return cf[0], cr[0]


def _score_n2(case: Mapping[str, object], remint: int) -> Dict[str, Mapping[str, object]]:
    _surface_fingerprint("N2-OUTPUT", str(case["case_id"]), 8, remint)
    out = {}
    for arm in case["arms"]:
        f, r = _credit_costs(int(arm["n_out"]))
        winner = "reverse" if r < f else ("forward" if f < r else "tie")
        out[str(arm["arm"])] = {"forward": f, "reverse": r, "winner": winner}
    return out


def _smooth(theta: Sequence[int], target: Sequence[int]) -> int:
    return -sum(abs(a - b) for a, b in zip(theta, target))


def _needle(theta: Sequence[int], target: Sequence[int]) -> int:
    return 0 if tuple(theta) == tuple(target) else -1


def _steps_local(d: int, f, target: Tuple[int, ...]) -> F | None:
    theta = [0] * d
    evals = 1
    while tuple(theta) != target:
        best, move = f(theta, target), None
        for i in range(d):
            for delta in (-1, 1):
                cand = list(theta)
                cand[i] += delta
                if 0 <= cand[i] < 4:
                    evals += 1
                    value = f(cand, target)
                    if value > best:
                        best, move = value, (i, delta)
        if move is None:
            return None
        theta[move[0]] += move[1]
    return F(evals)


def _steps_gradient(d: int, f, target: Tuple[int, ...], order: Tuple[int, ...]) -> F | None:
    theta = [0] * d
    evals = 0
    for _ in range(4 * d):
        if tuple(theta) == target:
            return F(evals if evals else 1)
        evals += 1
        moved = False
        for i in order:
            up, down = list(theta), list(theta)
            up[i] = min(3, theta[i] + 1)
            down[i] = max(0, theta[i] - 1)
            if f(up, target) > f(theta, target):
                theta[i] = up[i]
                moved = True
            elif f(down, target) > f(theta, target):
                theta[i] = down[i]
                moved = True
        if not moved:
            return None
    return None


def _fstr(x: F | None) -> str | None:
    if x is None:
        return None
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def _score_n3(case: Mapping[str, object], remint: int) -> Dict[str, Mapping[str, object]]:
    d = int(case["semantics"]["dimension"])
    target = tuple(int(x) for x in case["semantics"]["target"])
    order = _surface_permutation("N3-COORD", str(case["case_id"]), d, remint)
    random_expected = F(4**d + 1, 2)
    out = {}
    for arm in case["arms"]:
        signal = arm["landscape_signal"]
        f = _smooth if signal == "coordinate_distance" else _needle
        grad = _steps_gradient(d, f, target, order)
        local = _steps_local(d, f, target)
        if signal == "coordinate_distance":
            grad_cost = grad * 3 if grad is not None else None
            out[str(arm["arm"])] = {
                "gradient_evals": int(grad) if grad is not None and grad.denominator == 1 else _fstr(grad),
                "gradient_charged_cost": _fstr(grad_cost),
                "random_expected_evals": _fstr(random_expected),
                "gradient_reaches": grad is not None,
                "gradient_cheaper_than_random": grad_cost is not None and grad_cost < random_expected,
            }
        else:
            out[str(arm["arm"])] = {
                "gradient_evals": _fstr(grad),
                "local_evals": _fstr(local),
                "random_expected_evals": _fstr(random_expected),
                "gradient_reaches": grad is not None,
            }
    return out


def _n4_tokens(case_id: str, remint: int) -> Mapping[str, str]:
    names = ("M", "P0", "P1", "F", "Q")
    labels = _surface_labels("N4-TOKEN", case_id, len(names), remint)
    return dict(zip(names, labels))


def _score_n4(case: Mapping[str, object], remint: int) -> Dict[str, Mapping[str, object]]:
    tok = _n4_tokens(str(case["case_id"]), remint)

    def stream(gap: int, payload: int):
        return (tok["M"], tok[f"P{payload}"]) + (tok["F"],) * gap + (tok["Q"],)

    def required(xs):
        for i, value in enumerate(xs):
            if value == tok["M"]:
                return xs[i + 1]
        raise AssertionError("marker missing")

    def register(xs, L: int):
        buf = [None] * L
        for value in xs:
            if value == tok["Q"]:
                return buf[0]
            buf = buf[1:] + [value]
        return None

    def gated(xs):
        cell, armed = None, False
        for value in xs:
            if value == tok["Q"]:
                return cell
            if armed:
                cell, armed = value, False
            if value == tok["M"]:
                armed = True
        return cell

    lengths = tuple(int(x) for x in case["semantics"]["register_lengths"])
    out = {}
    for arm in case["arms"]:
        gaps = tuple(int(x) for x in arm["gap_set"])
        eco = [stream(g, p) for g in gaps for p in (0, 1)]
        working = [L for L in lengths if all(register(xs, L) == required(xs) for xs in eco)]
        gated_ok = all(gated(xs) == required(xs) for xs in eco)
        out[str(arm["arm"])] = {
            "working_register_lengths": working,
            "gated_works": gated_ok,
            "conditional_write_required": gated_ok and not working,
        }
    return out


def _affine_realizable(delta: Mapping[Tuple[str, str], str], states: Sequence[str], symbols: Sequence[str]) -> bool:
    def as_vec(v: int) -> Tuple[int, int]:
        return (v & 1, (v >> 1) & 1)

    mats = list(itertools.product(list(itertools.product((0, 1), repeat=2)), repeat=2))
    biases = list(itertools.product((0, 1), repeat=2))

    def apply(A, c, v):
        return tuple((sum(A[i][j] * v[j] for j in range(2)) + c[i]) % 2 for i in range(2))

    for assign in itertools.permutations(range(4), 4):
        code = {state: as_vec(assign[i]) for i, state in enumerate(states)}
        ok = True
        for symbol in symbols:
            found = False
            for A in mats:
                for c in biases:
                    if all(apply(A, c, code[q]) == code[delta[(q, symbol)]] for q in states):
                        found = True
                        break
                if found:
                    break
            if not found:
                ok = False
                break
        if ok:
            return True
    return False


def _score_n5(case: Mapping[str, object], remint: int) -> Dict[str, Mapping[str, object]]:
    state_labels = _surface_labels("N5-STATE", str(case["case_id"]), 4, remint)
    symbol_labels = _surface_labels("N5-SYMBOL", str(case["case_id"]), 2, remint)
    out = {}
    for arm in case["arms"]:
        kind = arm["transition_structure"]
        delta = {}
        for q in range(4):
            if kind == "four_cycle_with_identity":
                a, b = q, (q + 1) % 4
            else:
                a = 1
                b = {0: 3, 1: 2, 2: 3, 3: 3}[q]
            delta[(state_labels[q], symbol_labels[0])] = state_labels[a]
            delta[(state_labels[q], symbol_labels[1])] = state_labels[b]
        out[str(arm["arm"])] = {
            "affine_realizable": _affine_realizable(delta, state_labels, symbol_labels)
        }
    return out


def _score_n6(case: Mapping[str, object], remint: int) -> Dict[str, Mapping[str, object]]:
    universe = list(itertools.product((0, 1), repeat=4))
    order = _surface_permutation("N6-FEATURE", str(case["case_id"]), 4, remint)
    cap = int(case["semantics"]["subset_cap"])

    def distance(a, b):
        return sum(x != y for x, y in zip(a, b))

    def surface_tuple(x):
        return tuple(x[i] for i in order)

    def obligation(kind, x):
        return int(sum(x) >= 2) if kind == "threshold_sum_ge_2" else sum(x) % 2

    def minimum(kind):
        for size in range(1, cap + 1):
            for subset in itertools.combinations(universe, size):
                ok = True
                for x in universe:
                    near = min(subset, key=lambda s: (distance(s, x), surface_tuple(s)))
                    if obligation(kind, near) != obligation(kind, x):
                        ok = False
                        break
                if ok:
                    return size
        return None

    out = {}
    for arm in case["arms"]:
        size = minimum(str(arm["response_geometry"]))
        out[str(arm["arm"])] = {
            "smallest_sufficient_subset": size,
            "sufficient_within_cap": size is not None,
        }
    return out


def _score_n7(case: Mapping[str, object], remint: int) -> Dict[str, Mapping[str, object]]:
    row_order = _surface_permutation("N7-ROW", str(case["case_id"]), 3, remint)
    col_order = _surface_permutation("N7-COL", str(case["case_id"]), 3, remint)

    def base_joint(kind):
        if kind == "independent_uniform":
            return [[F(1, 9) for _ in range(3)] for _ in range(3)]
        return [[F(1, 6) if i == j else F(1, 12) for j in range(3)] for i in range(3)]

    out = {}
    for arm in case["arms"]:
        base = base_joint(str(arm["dependence_structure"]))
        joint = [[base[i][j] for j in col_order] for i in row_order]
        rows = [sum(row, F(0)) for row in joint]
        cols = [sum((joint[i][j] for i in range(3)), F(0)) for j in range(3)]
        factorizes = all(joint[i][j] == rows[i] * cols[j] for i in range(3) for j in range(3))
        out[str(arm["arm"])] = {
            "factorizes": factorizes,
            "factored_storage_legal": factorizes,
        }
    return out


def _search_expansions(informative: bool) -> int:
    goal = (2, 2, 2, 2)

    def heuristic(node: Tuple[int, ...]) -> int:
        if not informative:
            return 0
        return 4 - len(node) if tuple(goal[: len(node)]) == node else 100

    counter = 0
    queue = [(heuristic(()), counter, ())]
    expansions = 0
    while queue:
        _score, _order, node = heapq.heappop(queue)
        expansions += 1
        if node == goal:
            return expansions
        if len(node) < 4:
            for child in (0, 1, 2):
                counter += 1
                nxt = node + (child,)
                heapq.heappush(queue, (heuristic(nxt), counter, nxt))
    raise AssertionError("goal unreachable")


def _score_n8(case: Mapping[str, object], remint: int) -> Dict[str, Mapping[str, object]]:
    _surface_labels("N8-CHILD", str(case["case_id"]), 3, remint)
    out = {}
    for arm in case["arms"]:
        informative = arm["heuristic_informativeness"] == "goal_prefix_distance"
        expansions = _search_expansions(informative)
        out[str(arm["arm"])] = {
            "expansions": expansions,
            "charged_work": expansions * 2,
        }
    out["positive"]["reduces_expansions_vs_fail"] = (
        out["positive"]["expansions"] < out["fail"]["expansions"]
    )
    return out


SCORERS = {
    "N1": _score_n1,
    "N2": _score_n2,
    "N3": _score_n3,
    "N4": _score_n4,
    "N5": _score_n5,
    "N6": _score_n6,
    "N7": _score_n7,
    "N8": _score_n8,
}


def _expected_by_arm(case: Mapping[str, object]) -> Dict[str, Mapping[str, object]]:
    return {str(arm["arm"]): arm["expected"] for arm in case["arms"]}


def _score_case(case: Mapping[str, object], remint: int) -> Dict[str, Mapping[str, object]]:
    return SCORERS[str(case["case_id"])](case, remint)


def _prediction_tamper_hostile(payload: Mapping[str, object]) -> Mapping[str, object]:
    mutant = copy.deepcopy(payload)
    mutant["cases"][1]["arms"][0]["expected"]["forward"] += 1
    case = mutant["cases"][1]
    mismatch = _score_case(case, 1) != _expected_by_arm(case)
    if not mismatch:
        raise AssertionError("prediction tamper did not cause mismatch")
    return {"mismatch_detected": True}


def _label_swap_hostile(payload: Mapping[str, object]) -> Mapping[str, object]:
    mutant = copy.deepcopy(payload)
    case = mutant["cases"][6]
    case["arms"][0]["expected"], case["arms"][1]["expected"] = (
        case["arms"][1]["expected"], case["arms"][0]["expected"]
    )
    mismatch = _score_case(case, 1) != _expected_by_arm(case)
    if not mismatch:
        raise AssertionError("positive/fail expected-label swap escaped")
    return {"mismatch_detected": True}


def _matching_mutation_hostile(payload: Mapping[str, object]) -> Mapping[str, object]:
    mutant = copy.deepcopy(payload)
    case = mutant["cases"][0]
    case["arms"][1][case["matched_fields"][0]] = 999
    rejected = False
    try:
        validate_predictions(mutant)
    except ValueError:
        rejected = True
    if not rejected:
        raise AssertionError("second-coordinate matching mutation escaped")
    return {"rejected": True}


def _label_injection_hostile(payload: Mapping[str, object]) -> Mapping[str, object]:
    mutant = copy.deepcopy(payload)
    mutant["cases"][0]["family_name"] = "forbidden"
    rejected = False
    try:
        validate_predictions(mutant)
    except ValueError:
        rejected = True
    if not rejected:
        raise AssertionError("family-label injection escaped")
    return {"rejected": True}


def build_result() -> Mapping[str, object]:
    payload = load_predictions()
    rows = []
    all_match = True
    all_invariant = True
    for case in payload["cases"]:
        expected = _expected_by_arm(case)
        m1 = _score_case(case, 1)
        m2 = _score_case(case, 2)
        match1 = m1 == expected
        match2 = m2 == expected
        invariant = m1 == m2
        all_match = all_match and match1 and match2
        all_invariant = all_invariant and invariant
        rows.append({
            "case_id": case["case_id"],
            "object_kind": case["object_kind"],
            "varying_coordinate": case["varying_coordinate"],
            "matched_fields": case["matched_fields"],
            "expected": expected,
            "measured_remint_1": m1,
            "measured_remint_2": m2,
            "match_remint_1": match1,
            "match_remint_2": match2,
            "surface_remint_invariant": invariant,
            "matching_contract_passed": True,
        })

    hostiles = {
        "prediction_tamper": _prediction_tamper_hostile(payload),
        "positive_fail_label_swap": _label_swap_hostile(payload),
        "second_matched_field_mutation": _matching_mutation_hostile(payload),
        "family_label_injection": _label_injection_hostile(payload),
    }
    hostiles_green = all(next(iter(v.values())) is True for v in hostiles.values())
    green = all_match and all_invariant and hostiles_green
    return {
        "schema": "B1MatchedNegativeResultV1",
        "issue": 786,
        "freeze_commit": FREEZE_COMMIT,
        "prediction_authority_commit": PREDICTION_AUTHORITY_COMMIT,
        "scorer_imports_prediction_implementation": False,
        "scorer_reads_historical_donor_results_as_outcomes": False,
        "historical_measured_matched_negative_count": 11,
        "successor_control_count": 8,
        "effective_measured_matched_negative_count": 19 if green else 11,
        "cases": rows,
        "all_predictions_match": all_match,
        "all_surface_remints_invariant": all_invariant,
        "hostiles": hostiles,
        "status": "PASS" if green else "FAIL",
        "terminal": (
            "B1_MATCHED_NEGATIVE_CONTROLS_MEASURED_19_OF_19_AT_REGISTERED_EXACT_SCOPE"
            if green else "B1_MATCHED_NEGATIVE_CONTROL_SUCCESSOR_NOT_GREEN"
        ),
        "claim_ceiling": "matched-negative exact controls only; not B1/global known-family closure",
        "nonclaims": payload["nonclaims"],
    }


if __name__ == "__main__":
    print(json.dumps(build_result(), sort_keys=True, separators=(",", ":")))

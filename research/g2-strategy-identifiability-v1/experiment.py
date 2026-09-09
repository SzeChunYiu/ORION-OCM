"""G4.4 identifiability boxes on a tiny polynomial two-decision MDP. No ML.

Two exclusive search arms (primitive enumeration vs compiled 2-op MACRO) both
verify four frozen polynomial identities. Exact Q is the slot count. The
closed-form parent is MACRO iff degree >= 2.
"""
from __future__ import annotations

import argparse
from itertools import product
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "src"
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))

from ocm.learning import methods as M  # noqa: E402

METHOD_BLOB = "50323a33418b8ef8bb6500ddeba4b9d1f795e9e3"
SCHEMA = "ocm.g2.strategy-identifiability.result.v1"
BUDGET = M.SearchBudget(slots=1000, max_length=4)
FRAGMENT: M.Program = ("inc", "square")
ACTIONS = ("PRIMITIVE", "MACRO")
# Closed-form analogue of g4-horizon-exact-v1 analytic_should_buy:
# remaining*(rent-hit) > build  →  here MACRO iff degree >= 2.
ANALYTIC_DEGREE_THRESHOLD = 2

TASK_SPECS: tuple[tuple[str, tuple[str, ...], str], ...] = (
    ("match-0", ("inc", "square"), "MATCH"),
    ("match-1", ("inc", "square", "inc"), "MATCH"),
    ("mismatch-0", ("double", "inc"), "MISMATCH"),
    ("mismatch-1", ("dec", "double"), "MISMATCH"),
)


def git_blob_sha1(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def pin_methods() -> str:
    blob = git_blob_sha1(SRC / "ocm" / "learning" / "methods.py")
    if blob != METHOD_BLOB:
        raise RuntimeError(f"methods.py blob {blob} != pinned {METHOD_BLOB}")
    return blob


def task_from_program(name: str, program: tuple[str, ...]) -> M.PolynomialTask:
    return M.PolynomialTask(name, M.normal_form(program))


def frozen_tasks() -> tuple[dict[str, Any], ...]:
    rows = []
    fingerprints = []
    for name, program, family in TASK_SPECS:
        task = task_from_program(name, program)
        fingerprints.append(task.fingerprint)
        rows.append({
            "state_id": name,
            "family": family,
            "program": list(program),
            "coefficients": [str(c) for c in task.coefficients],
            "degree": len(task.coefficients) - 1,
            "constant_term_nonzero": task.coefficients[0] != 0,
            "fingerprint": task.fingerprint,
            "task": task,
        })
    if len(fingerprints) != len(set(fingerprints)):
        raise RuntimeError("frozen task fingerprint collision")
    return tuple(rows)


def legal_actions(_state: dict[str, Any]) -> tuple[str, ...]:
    """Snapshot acceptable actions before any Q comparison (decision-core iterator)."""
    return ACTIONS


def run_arm(task: M.PolynomialTask, action: str) -> M.SearchResult:
    if action == "PRIMITIVE":
        programs = M._primitive_programs(BUDGET.max_length)
    elif action == "MACRO":
        method = M.GeneratorMethod((FRAGMENT,), ("frozen-match-family",))
        programs = M._guided_programs(method, BUDGET.max_length)
    else:
        raise ValueError(action)
    seen: set[M.Program] = set()
    checked = 0
    counterexamples = [0]
    result = None
    for slots in range(1, BUDGET.slots + 1):
        try:
            program = next(programs)
        except StopIteration:
            result = M.SearchResult(
                task.fingerprint, action, "EXHAUSTED_DECLARED_GRAMMAR",
                None, slots - 1, checked, tuple(counterexamples), BUDGET.max_length,
            )
            break
        if len(program) > BUDGET.max_length or program in seen:
            continue
        seen.add(program)
        checked += 1
        if any(M.execute(program, x) != M.evaluate_polynomial(task.coefficients, x) for x in counterexamples):
            continue
        coefficients = M.normal_form(program)
        if coefficients == task.coefficients:
            result = M.SearchResult(
                task.fingerprint, action, "VERIFIED_POLYNOMIAL_IDENTITY",
                program, slots, checked, tuple(counterexamples), BUDGET.max_length,
            )
            break
        for x in range(max(len(coefficients), len(task.coefficients))):
            if M.evaluate_polynomial(coefficients, x) != M.evaluate_polynomial(task.coefficients, x):
                counterexamples.append(x)
                break
    else:
        result = M.SearchResult(
            task.fingerprint, action, "BUDGET_EXHAUSTED", None,
            BUDGET.slots, checked, tuple(counterexamples), BUDGET.max_length,
        )
    return result


def q_table(states: tuple[dict[str, Any], ...]) -> dict[str, dict[str, dict[str, Any]]]:
    table: dict[str, dict[str, dict[str, Any]]] = {}
    for state in states:
        table[state["state_id"]] = {}
        for action in legal_actions(state):
            result = run_arm(state["task"], action)
            verified = M.verify_solution(state["task"], result)
            table[state["state_id"]][action] = {
                "status": result.status,
                "slots": result.slots,
                "program": list(result.program) if result.program is not None else [],
                "verified": verified,
                "candidates_checked": result.candidates_checked,
            }
    return table


def exact_backup(table: dict[str, dict[str, dict[str, Any]]]) -> dict[str, dict[str, Any]]:
    """V(s)=min_a Q(s,a); unused-arm Q is the exact counterfactual, not a sample."""
    backups = {}
    for state_id, arms in table.items():
        admissible = [a for a, row in arms.items() if row["verified"]]
        if not admissible:
            raise RuntimeError(f"no admissible arm at {state_id}")
        best = min(admissible, key=lambda a: (arms[a]["slots"], a))
        value = arms[best]["slots"]
        unused = [a for a in admissible if a != best]
        unused_rows = {
            a: {
                "slots": arms[a]["slots"],
                "advantage_of_best": arms[a]["slots"] - value,
                "mechanism": "exact_arm_rollout_slots",
            }
            for a in unused
        }
        backups[state_id] = {
            "admissible": admissible,
            "optimal": best,
            "value_slots": value,
            "q_slots": {a: arms[a]["slots"] for a in arms},
            "unused_counterfactuals": unused_rows,
            "counterfactual_identifiable": bool(unused_rows) and all(
                row["mechanism"] == "exact_arm_rollout_slots" for row in unused_rows.values()
            ),
        }
    return backups


def analytic_action(degree: int) -> str:
    return "MACRO" if degree >= ANALYTIC_DEGREE_THRESHOLD else "PRIMITIVE"


def policy_cost(states: tuple[dict[str, Any], ...], table: dict[str, dict[str, dict[str, Any]]],
                choose) -> dict[str, Any]:
    choices = []
    total = 0
    verified = True
    for state in states:
        action = choose(state)
        row = table[state["state_id"]][action]
        choices.append({"state_id": state["state_id"], "action": action, "slots": row["slots"],
                        "verified": row["verified"]})
        total += row["slots"]
        verified = verified and row["verified"]
    return {"choices": choices, "total_slots": total, "all_verified": verified}


def regret_floor(buckets: dict[str, list[str]], backups: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """C_phi - C_oracle on a frozen observation partition (ACTION_SUFFICIENT_STATE_V1)."""
    oracle = sum(backups[s]["value_slots"] for s in backups)
    phi = 0
    collisions = []
    unanimous = True
    for key, members in buckets.items():
        required = {backups[s]["optimal"] for s in members}
        if len(required) != 1:
            unanimous = False
            collisions.append({"bucket": key, "members": members, "required_actions": sorted(required)})
        best_common = min(
            ACTIONS,
            key=lambda a: (sum(backups[s]["q_slots"][a] for s in members), a),
        )
        phi += sum(backups[s]["q_slots"][best_common] for s in members)
    return {
        "oracle_slots": oracle,
        "phi_slots": phi,
        "regret_floor_slots": phi - oracle,
        "unanimous_buckets": unanimous,
        "collisions": collisions,
    }


def hypothesis_class_check(states: tuple[dict[str, Any], ...], backups: dict[str, dict[str, Any]]) -> dict[str, Any]:
    dp = {s["state_id"]: backups[s["state_id"]]["optimal"] for s in states}
    constant = {}
    for action in ACTIONS:
        constant[action] = all(dp[s["state_id"]] == action for s in states)
    thresholds = {}
    recovered = []
    for t in range(0, 4):
        pred = {s["state_id"]: ("MACRO" if s["degree"] >= t else "PRIMITIVE") for s in states}
        ok = pred == dp
        thresholds[str(t)] = {"policy": pred, "recovers_dp": ok}
        if ok:
            recovered.append(t)
    return {
        "constant_class_adequate": any(constant.values()),
        "constant_matches": constant,
        "threshold_on_degree_adequate": bool(recovered),
        "thresholds_that_recover_dp": recovered,
        "registered_class": "MACRO iff degree >= t, t in {0,1,2,3}",
        "dp_policy": dp,
    }


def decide_terminal(payload: dict[str, Any]) -> tuple[str, dict[str, bool]]:
    n_safe = payload["safe_strategies"]["n_distinct_all_succeed"]
    n_optima = len({row["optimal"] for row in payload["exact_backup"].values()})
    cf = all(row["counterfactual_identifiable"] for row in payload["exact_backup"].values())
    unused_positive = any(
        cf_row["advantage_of_best"] > 0
        for row in payload["exact_backup"].values()
        for cf_row in row["unused_counterfactuals"].values()
    )
    analytic_residual = payload["residual_table"]["analytic_degree_threshold"]["residual_slots"]
    legal = payload["legal_features"]["registered_degree"]
    h = payload["hypothesis_class"]
    criteria = {
        "methods_blob_pinned": payload["methods_blob"] == METHOD_BLOB,
        "multiple_safe_strategies": n_safe >= 2,
        "all_arms_verify_all_states": payload["all_arms_verify_all_states"],
        "optimal_strategy_changes": n_optima >= 2,
        "counterfactual_identifiable_exact_backup": cf and unused_positive,
        "analytic_recovers_dp": analytic_residual == 0,
        "legal_degree_unanimous": legal["unanimous_buckets"],
        "legal_degree_regret_floor_zero": legal["regret_floor_slots"] == 0,
        "threshold_class_adequate": h["threshold_on_degree_adequate"],
        "constant_class_inadequate": not h["constant_class_adequate"],
        "no_sampling": payload["no_sampling"],
        "ml_not_trained": payload["ml_trained"] is False,
    }
    if not criteria["multiple_safe_strategies"] or not criteria["all_arms_verify_all_states"]:
        return "SINGLE_SAFE_STRATEGY_ONLY", criteria
    if not criteria["optimal_strategy_changes"]:
        return "OPTIMAL_STRATEGY_CONSTANT", criteria
    if not criteria["counterfactual_identifiable_exact_backup"]:
        return "COUNTERFACTUAL_NOT_IDENTIFIABLE", criteria
    if not criteria["legal_degree_unanimous"]:
        return "OBSERVATION_CHANNEL_INSUFFICIENT", criteria
    if not criteria["threshold_class_adequate"]:
        return "HYPOTHESIS_CLASS_INADEQUATE", criteria
    if analytic_residual > 0:
        return "STRATEGY_SELECTION_RESIDUAL_CONFIRMED", criteria
    if all(criteria.values()):
        return "PARENT_SUFFICIENT_AT_SCOPE", criteria
    return "CANNOT_CHECK_LEGAL_FEATURES", criteria


def box_mapping(terminal: str, criteria: dict[str, bool], payload: dict[str, Any]) -> list[dict[str, Any]]:
    analytic_residual = payload["residual_table"]["analytic_degree_threshold"]["residual_slots"]
    greedy_residual = payload["residual_table"]["always_macro"]["residual_slots"]
    return [
        {
            "id": "G4.4.1",
            "checkbox": "multiple safe strategies remain after exact admissibility",
            "at_this_microscope": "CHECK" if criteria["multiple_safe_strategies"] else "FAIL",
            "programme_tick": False,
            "witness": f"{payload['safe_strategies']['n_distinct_all_succeed']} complete strategies verify every task",
        },
        {
            "id": "G4.4.2",
            "checkbox": "optimal strategy changes across legal pre-outcome states",
            "at_this_microscope": "CHECK" if criteria["optimal_strategy_changes"] else "FAIL",
            "programme_tick": False,
            "witness": "MACRO on MATCH (degree 2); PRIMITIVE on MISMATCH (degree 1)",
        },
        {
            "id": "G4.4.3",
            "checkbox": "counterfactual value is identifiable",
            "at_this_microscope": "CHECK" if criteria["counterfactual_identifiable_exact_backup"] else "FAIL",
            "programme_tick": False,
            "witness": "unused-arm Q is the exact exclusive rollout slot count",
        },
        {
            "id": "G4.4.4",
            "checkbox": "simple exact/analytic parents leave a material residual",
            "at_this_microscope": (
                "FAIL_PARENT_CAPTURES"
                if analytic_residual == 0
                else "CHECK"
            ),
            "programme_tick": False,
            "witness": (
                f"greedy always-MACRO residual {greedy_residual} slots; "
                f"analytic degree-threshold residual {analytic_residual} slots. "
                "The residual of ignoring degree is a missing legal feature read, not a learner case."
            ),
        },
        {
            "id": "G4.4.5",
            "checkbox": "legal features contain enough information for the required decision",
            "at_this_microscope": "CHECK" if criteria["legal_degree_regret_floor_zero"] else "CANNOT_CHECK",
            "programme_tick": False,
            "witness": "registered feature = degree; deficient control constant_term_nonzero aliases",
        },
        {
            "id": "G4.4.6",
            "checkbox": "hypothesis class is adequate",
            "at_this_microscope": "CHECK" if criteria["threshold_class_adequate"] else "FAIL",
            "programme_tick": False,
            "witness": "threshold-on-degree recovers DP; constant policies do not",
        },
        {
            "id": "G2.4-complete",
            "checkbox": "G2.4 fresh-task causal use closed",
            "at_this_microscope": "NOT_CLAIMED",
            "programme_tick": False,
            "witness": "this capsule is identifiability at the polynomial microscope, not G2.4",
        },
        {
            "id": "G4.4-ml-unlock",
            "checkbox": "#71 learned router authorized",
            "at_this_microscope": "NOT_UNLOCKED",
            "programme_tick": False,
            "witness": terminal,
        },
    ]


def run() -> dict[str, Any]:
    blob = pin_methods()
    states = frozen_tasks()
    table = q_table(states)
    backups = exact_backup(table)
    all_verify = all(row["verified"] for arms in table.values() for row in arms.values())

    always_p = policy_cost(states, table, lambda _s: "PRIMITIVE")
    always_m = policy_cost(states, table, lambda _s: "MACRO")
    analytic = policy_cost(states, table, lambda s: analytic_action(s["degree"]))
    dp = policy_cost(states, table, lambda s: backups[s["state_id"]]["optimal"])
    dp_total = dp["total_slots"]

    safe = []
    for name, policy in (("always_primitive", always_p), ("always_macro", always_m),
                         ("analytic_degree_threshold", analytic), ("exact_dp", dp)):
        if policy["all_verified"]:
            safe.append(name)

    degree_buckets: dict[str, list[str]] = {}
    alias_buckets: dict[str, list[str]] = {"constant_term_nonzero=true": []}
    for state in states:
        degree_buckets.setdefault(str(state["degree"]), []).append(state["state_id"])
        alias_buckets["constant_term_nonzero=true"].append(state["state_id"])

    sequential = [
        {"t": 1, "state_id": "match-0", "optimal": backups["match-0"]["optimal"]},
        {"t": 2, "state_id": "mismatch-0", "optimal": backups["mismatch-0"]["optimal"]},
    ]

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "methods_blob": blob,
        "claim_ceiling": (
            "G4.4 identifiability preconditions at this four-task polynomial microscope. "
            "Not G2.4-complete. Not a G4.4 ML unlock. PARENT_SUFFICIENT is not programme failure."
        ),
        "parents_cited_not_rewritten": [
            "research/g4-horizon-exact-v1/",
            "research/paid-decision-region-correction-v1/",
            "research/decision-core-successor-repair-v1/",
            "research/g2-two-decision-search-v1/",
        ],
        "world": {
            "kind": "finite_noiseless_two_action_mdp_over_polynomial_identities",
            "fragment": list(FRAGMENT),
            "budget": {"slots": BUDGET.slots, "max_length": BUDGET.max_length},
            "actions": list(ACTIONS),
            "analytic_rule": "MACRO iff degree >= 2",
            "n_states": len(states),
            "states": [
                {k: v for k, v in s.items() if k != "task"}
                for s in states
            ],
        },
        "q_table": table,
        "exact_backup": backups,
        "two_decision_episode": {
            "trajectory": sequential,
            "optimal_changes": sequential[0]["optimal"] != sequential[1]["optimal"],
            "note": "one MATCH then one MISMATCH; exclusive arms, not mixed methods.solve alternation",
        },
        "safe_strategies": {
            "names": safe,
            "n_distinct_all_succeed": len({n for n in safe if n in ("always_primitive", "always_macro")}),
            "policies": {
                "always_primitive": always_p,
                "always_macro": always_m,
                "analytic_degree_threshold": analytic,
                "exact_dp": dp,
            },
        },
        "residual_table": {
            "oracle_slots": dp_total,
            "always_primitive": {
                "total_slots": always_p["total_slots"],
                "residual_slots": always_p["total_slots"] - dp_total,
                "mechanism": "state-independent PRIMITIVE pays MATCH-family prefix search the fragment already names",
            },
            "always_macro": {
                "total_slots": always_m["total_slots"],
                "residual_slots": always_m["total_slots"] - dp_total,
                "mechanism": "state-independent MACRO enumerates (inc,square)-expansions that cannot be degree-1 identities",
            },
            "analytic_degree_threshold": {
                "total_slots": analytic["total_slots"],
                "residual_slots": analytic["total_slots"] - dp_total,
                "mechanism": "closed-form threshold on legal degree; residual 0 iff it recovers DP",
            },
            "exact_dp": {
                "total_slots": dp_total,
                "residual_slots": 0,
                "mechanism": "finite exact backup over the four frozen states",
            },
        },
        "legal_features": {
            "registered_degree": regret_floor(degree_buckets, backups),
            "deficient_constant_term_nonzero": regret_floor(alias_buckets, backups),
        },
        "hypothesis_class": hypothesis_class_check(states, backups),
        "all_arms_verify_all_states": all_verify,
        "no_sampling": True,
        "ml_trained": False,
        "g24_complete": False,
        "g44_ml_authorized": False,
    }
    succeeding_maps = []
    for assignment in product(ACTIONS, repeat=len(states)):
        choose = dict(zip([s["state_id"] for s in states], assignment))
        ok = all(table[s][choose[s]]["verified"] for s in choose)
        if ok:
            succeeding_maps.append(choose)
    payload["safe_strategies"]["enumerated_verified_assignments"] = len(succeeding_maps)
    payload["safe_strategies"]["n_distinct_all_succeed"] = max(
        payload["safe_strategies"]["n_distinct_all_succeed"],
        2 if always_p["all_verified"] and always_m["all_verified"] else 0,
    )

    terminal, criteria = decide_terminal(payload)
    payload["terminal"] = terminal
    payload["criteria"] = criteria
    payload["box_mapping"] = box_mapping(terminal, criteria, payload)
    return payload


def jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "RESULT.json")
    args = parser.parse_args()
    result = jsonable(run())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "terminal": result["terminal"],
        "g24_complete": result["g24_complete"],
        "g44_ml_authorized": result["g44_ml_authorized"],
        "oracle_slots": result["residual_table"]["oracle_slots"],
        "analytic_residual": result["residual_table"]["analytic_degree_threshold"]["residual_slots"],
        "macro_residual": result["residual_table"]["always_macro"]["residual_slots"],
        "primitive_residual": result["residual_table"]["always_primitive"]["residual_slots"],
        "optimal_by_state": {k: v["optimal"] for k, v in result["exact_backup"].items()},
    }, sort_keys=True))


if __name__ == "__main__":
    main()

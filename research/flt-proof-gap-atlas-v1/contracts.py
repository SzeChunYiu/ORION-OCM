"""Hermetic FLT Proof Gap Atlas contracts.

Development/evaluation infrastructure only.  These helpers validate frozen
benchmark declarations and source-bound route evidence; they do not execute Lean,
establish mathematical novelty, or authorize protected OCM claims.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction


class CannotCheck(ValueError):
    """The declared evidence is insufficient or internally inconsistent."""


GAP_CLASSES = frozenset(f"G{i}" for i in range(1, 9))
DISCOVERY_TERMINALS = frozenset({
    "SOLVED",
    "TIMEOUT",
    "NOT_FOUND_WITHIN_REGISTERED_BUDGET",
})
EXHAUSTIVE_TERMINAL = "ALL_NORMALIZED_ROUTES_WITHIN_BOUND_FOUND"
FORBIDDEN_TERMINALS = frozenset({"ALL_FLT_PROOFS_FOUND"})


def identity(value) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
    ).hexdigest()


def token(value, field: str = "identity") -> str:
    if type(value) is not str or not value:
        raise CannotCheck(f"nonempty {field} required")
    return value


def sha256(value, field: str = "SHA-256 identity") -> str:
    if (
        type(value) is not str
        or len(value) != 64
        or any(c not in "0123456789abcdef" for c in value)
    ):
        raise CannotCheck(f"{field} required")
    return value


def git_sha(value, field: str = "git commit") -> str:
    if (
        type(value) is not str
        or len(value) != 40
        or any(c not in "0123456789abcdef" for c in value)
    ):
        raise CannotCheck(f"40-hex {field} required")
    return value


def finite_tokens(value, field: str) -> tuple[str, ...]:
    if type(value) is not list or not value:
        raise CannotCheck(f"nonempty finite {field} required")
    out = tuple(token(v, field) for v in value)
    if len(out) != len(set(out)):
        raise CannotCheck(f"duplicate {field}")
    return out


def resource_budget(value) -> dict[str, int]:
    if type(value) is not dict or not value:
        raise CannotCheck("nonempty named finite resource budget required")
    result: dict[str, int] = {}
    for name, amount in value.items():
        name = token(name, "budget resource")
        if type(amount) is not int or amount < 0:
            raise CannotCheck("resource ceilings must be nonnegative integers")
        result[name] = amount
    return result


def validate_universe(universe: dict) -> dict:
    """Validate the prospectively frozen finite search contract U=(E,L,O,B,≈)."""
    if type(universe) is not dict:
        raise CannotCheck("universe object required")
    try:
        env = universe["environment"]
        if type(env) is not dict:
            raise CannotCheck("environment object required")
        source = env["source"]
        if type(source) is not dict:
            raise CannotCheck("source object required")
        token(source["repository"], "source repository")
        git_sha(source["commit"], "source commit")
        token(env["lean_toolchain"], "Lean toolchain")
        token(env["mathlib_ref"], "Mathlib ref")
        git_sha(env["mathlib_commit"], "Mathlib commit")
        checkers = finite_tokens(env["checkers"], "checker inventory")

        library = universe["library"]
        if type(library) is not dict:
            raise CannotCheck("library contract required")
        sha256(library["declaration_inventory_sha256"], "declaration inventory SHA-256")
        if type(library["declaration_count"]) is not int or library["declaration_count"] <= 0:
            raise CannotCheck("positive declaration count required")

        operators = finite_tokens(universe["operators"], "proof operator")
        budget = resource_budget(universe["budget"])
        normalization = universe["normalization"]
        if type(normalization) is not dict:
            raise CannotCheck("normalization contract required")
        token(normalization["version"], "normalization version")
        finite_tokens(normalization["features"], "normalization feature")
    except KeyError as exc:
        raise CannotCheck(f"missing universe field: {exc.args[0]}") from exc

    return {
        "status": "FROZEN_UNIVERSE_VALID",
        "universe_sha256": identity(universe),
        "checker_count": len(checkers),
        "operator_count": len(operators),
        "budget": budget,
    }


def _target(challenge: dict) -> dict:
    try:
        target = challenge["target"]
        if type(target) is not dict:
            raise CannotCheck("target object required")
        token(target["id"], "target theorem id")
        sha256(target["statement_sha256"], "target statement SHA-256")
        token(target["theorem_module"], "target theorem module")
        token(target["solution_module"], "target solution module")
        return target
    except KeyError as exc:
        raise CannotCheck(f"missing target field: {exc.args[0]}") from exc


def validate_challenge(challenge: dict, universe: dict) -> dict:
    """Reject answer leakage and bind a challenge to one exact frozen universe."""
    frozen = validate_universe(universe)
    if type(challenge) is not dict:
        raise CannotCheck("challenge object required")
    target = _target(challenge)
    try:
        if sha256(challenge["universe_sha256"], "challenge universe SHA-256") != frozen["universe_sha256"]:
            raise CannotCheck("challenge bound to a different frozen universe")
        gap_class = token(challenge["gap_class"], "gap class")
        if gap_class not in GAP_CLASSES:
            raise CannotCheck("gap class must be one of G1..G8")
        hidden_nodes = finite_tokens(challenge["hidden_nodes"], "hidden node")
        if target["id"] not in hidden_nodes:
            raise CannotCheck("target must be hidden")
        view = challenge["solver_view"]
        if type(view) is not dict:
            raise CannotCheck("solver_view object required")
        if sha256(view["statement_sha256"], "solver statement SHA-256") != target["statement_sha256"]:
            raise CannotCheck("solver statement differs from target")
        sha256(view["visible_declarations_sha256"], "visible declarations SHA-256")
        if view["network_access"] is not False:
            raise CannotCheck("hermetic challenge requires network_access=false")
        if view["solution_bytes_present"] is not False:
            raise CannotCheck("original solution bytes must be absent")
        if view["theorem_wrapper_present"] is not False:
            raise CannotCheck("original theorem wrapper must be absent")
        forbidden = set(finite_tokens(view["forbidden_modules"], "forbidden module"))
        if target["solution_module"] not in forbidden:
            raise CannotCheck("target solution module must be forbidden")
        if target["theorem_module"] not in forbidden:
            raise CannotCheck("target theorem wrapper must be forbidden")
        if resource_budget(challenge["budget"]) != frozen["budget"]:
            raise CannotCheck("challenge resource budget differs from frozen universe")
        if sha256(challenge["operators_sha256"], "operator inventory SHA-256") != identity(universe["operators"]):
            raise CannotCheck("challenge operator inventory differs from frozen universe")
        if token(challenge["normalization_version"], "normalization version") != universe["normalization"]["version"]:
            raise CannotCheck("challenge normalization differs from frozen universe")
    except KeyError as exc:
        raise CannotCheck(f"missing challenge field: {exc.args[0]}") from exc

    return {
        "status": "HERMETIC_CHALLENGE_VALID",
        "challenge_sha256": identity(challenge),
        "universe_sha256": frozen["universe_sha256"],
        "gap_class": gap_class,
    }


def _cannot_check_terminal(status: str) -> bool:
    return status == "CANNOT_CHECK" or status.startswith("CANNOT_CHECK_")


def validate_outcome(outcome: dict, challenge: dict, universe: dict) -> dict:
    """Validate source-bound outcome evidence without turning unknown into success."""
    challenge_receipt = validate_challenge(challenge, universe)
    if type(outcome) is not dict:
        raise CannotCheck("outcome object required")
    try:
        if sha256(outcome["challenge_sha256"], "outcome challenge SHA-256") != challenge_receipt["challenge_sha256"]:
            raise CannotCheck("outcome bound to a different challenge")
        status = token(outcome["status"], "terminal status")
        if status in FORBIDDEN_TERMINALS:
            raise CannotCheck("unbounded all-proofs terminal is forbidden")

        budget_used = resource_budget(outcome["resource_usage"])
        ceilings = resource_budget(challenge["budget"])
        if set(budget_used) != set(ceilings):
            raise CannotCheck("resource usage must name exactly the registered resources")
        if any(budget_used[k] > ceilings[k] for k in ceilings):
            raise CannotCheck("reported resource usage exceeds registered ceiling")

        if status == "SOLVED":
            evidence = outcome["checker_evidence"]
            if type(evidence) is not dict:
                raise CannotCheck("checker evidence object required")
            checker_id = token(evidence["checker_id"], "checker id")
            if checker_id not in universe["environment"]["checkers"]:
                raise CannotCheck("unregistered checker")
            if sha256(evidence["statement_sha256"], "checked statement SHA-256") != challenge["target"]["statement_sha256"]:
                raise CannotCheck("checker evidence belongs to a different statement")
            sha256(evidence["proof_sha256"], "proof SHA-256")
            sha256(evidence["dependencies_sha256"], "dependency-set SHA-256")
            sha256(evidence["environment_sha256"], "checker environment SHA-256")
            if evidence["accepted"] is not True:
                raise CannotCheck("SOLVED requires accepted=true")
        elif status == EXHAUSTIVE_TERMINAL:
            if outcome.get("search_exhaustive") is not True:
                raise CannotCheck("exhaustive terminal requires search_exhaustive=true")
            sha256(
                outcome.get("completeness_certificate_sha256"),
                "completeness certificate SHA-256",
            )
            if outcome.get("checker_evidence") not in (None, {}):
                raise CannotCheck("enumeration terminal must not masquerade as one proof")
        elif status in DISCOVERY_TERMINALS:
            if status != "SOLVED" and outcome.get("checker_evidence") not in (None, {}):
                raise CannotCheck("negative/timeout terminal cannot carry accepted proof evidence")
        elif _cannot_check_terminal(status):
            token(outcome.get("reason"), "cannot-check reason")
            if outcome.get("checker_evidence") not in (None, {}):
                raise CannotCheck("CANNOT_CHECK cannot carry accepted proof evidence")
        else:
            raise CannotCheck("unregistered terminal status")
    except KeyError as exc:
        raise CannotCheck(f"missing outcome field: {exc.args[0]}") from exc

    return {
        "status": "OUTCOME_CONTRACT_VALID",
        "terminal": status,
        "solved": status == "SOLVED",
        "scientific_claim_authorized": False,
    }


def validate_route(route: dict, challenge: dict, universe: dict) -> dict:
    """Validate one independently checker-backed support hyperedge."""
    if type(route) is not dict:
        raise CannotCheck("route object required")
    challenge_receipt = validate_challenge(challenge, universe)
    try:
        token(route["route_id"], "route id")
        if sha256(route["challenge_sha256"], "route challenge SHA-256") != challenge_receipt["challenge_sha256"]:
            raise CannotCheck("route bound to a different challenge")
        deps = finite_tokens(route["dependencies"], "dependency")
        proof_sha = sha256(route["proof_sha256"], "proof SHA-256")
        evidence = route["checker_evidence"]
        if type(evidence) is not dict or evidence.get("accepted") is not True:
            raise CannotCheck("independent accepted checker evidence required")
        checker_id = token(evidence["checker_id"], "checker id")
        if checker_id not in universe["environment"]["checkers"]:
            raise CannotCheck("unregistered checker")
        if sha256(evidence["proof_sha256"], "checked proof SHA-256") != proof_sha:
            raise CannotCheck("checker evidence belongs to a different proof")
        if sha256(evidence["statement_sha256"], "checked statement SHA-256") != challenge["target"]["statement_sha256"]:
            raise CannotCheck("checker evidence belongs to a different target")
        if sha256(evidence["dependencies_sha256"], "checked dependencies SHA-256") != identity(sorted(deps)):
            raise CannotCheck("checker evidence does not bind exact dependency set")
        metrics = route["metrics"]
        if type(metrics) is not dict or not metrics:
            raise CannotCheck("nonempty route metric vector required")
        for name, value in metrics.items():
            token(name, "metric name")
            if type(value) is not int or value < 0:
                raise CannotCheck("route metrics must be nonnegative integers")
        token(route["novelty_class"], "route novelty class")
        token(route["normalization_family"], "normalization family")
    except KeyError as exc:
        raise CannotCheck(f"missing route field: {exc.args[0]}") from exc

    return {
        "status": "CHECKED_ROUTE_VALID",
        "route_sha256": identity(route),
        "dependency_count": len(deps),
    }


def theorem_liveness(routes: list[dict], revoked: list[str]) -> dict:
    """AND/OR support semantics: a theorem is live if any complete route survives."""
    if type(routes) is not list or not routes:
        raise CannotCheck("nonempty checked route inventory required")
    dead = set(finite_tokens(revoked, "revoked identity")) if revoked else set()
    surviving: list[str] = []
    for route in routes:
        if type(route) is not dict:
            raise CannotCheck("route object required")
        route_id = token(route.get("route_id"), "route id")
        proof = sha256(route.get("proof_sha256"), "proof SHA-256")
        deps = set(finite_tokens(route.get("dependencies"), "dependency"))
        if proof not in dead and not deps & dead:
            surviving.append(route_id)
    return {
        "status": "LIVE" if surviving else "DEAD",
        "surviving_route_ids": tuple(sorted(surviving)),
    }


def dependency_distance(left: dict, right: dict) -> dict:
    """Exact Jaccard dependency distance, without claiming semantic novelty."""
    a = set(finite_tokens(left.get("dependencies"), "dependency"))
    b = set(finite_tokens(right.get("dependencies"), "dependency"))
    union = a | b
    distance = Fraction(len(a ^ b), len(union)) if union else Fraction(0, 1)
    overlap = Fraction(len(a & b), len(union)) if union else Fraction(1, 1)
    return {
        "dependency_distance": str(distance),
        "dependency_overlap": str(overlap),
        "semantic_novelty": "NOT_ESTABLISHED",
    }


def pareto_frontier(routes: list[dict], metric_names: list[str]) -> tuple[str, ...]:
    """Return route IDs not dominated on registered minimization metrics."""
    metrics = finite_tokens(metric_names, "Pareto metric")
    if type(routes) is not list or not routes:
        raise CannotCheck("nonempty route inventory required")
    rows: list[tuple[str, tuple[int, ...]]] = []
    for route in routes:
        if type(route) is not dict:
            raise CannotCheck("route object required")
        route_id = token(route.get("route_id"), "route id")
        vector: list[int] = []
        try:
            record = route["metrics"]
            for name in metrics:
                value = record[name]
                if type(value) is not int or value < 0:
                    raise CannotCheck("Pareto metrics must be nonnegative integers")
                vector.append(value)
        except (KeyError, TypeError) as exc:
            raise CannotCheck("missing registered Pareto metric") from exc
        rows.append((route_id, tuple(vector)))

    frontier: list[str] = []
    for route_id, vector in rows:
        dominated = any(
            other_id != route_id
            and all(a <= b for a, b in zip(other, vector))
            and any(a < b for a, b in zip(other, vector))
            for other_id, other in rows
        )
        if not dominated:
            frontier.append(route_id)
    return tuple(sorted(frontier))

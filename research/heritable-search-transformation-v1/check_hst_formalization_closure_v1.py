#!/usr/bin/env python3
"""Audit the additive HST formalization closure overlay.

This checker deliberately does not prove P1/P5 mathematics by execution.  It checks that
all frozen theorem rows are covered by exactly one primary proof class and that the
appropriate proof/certificate/bound/bridge/limit obligations are named.  The underlying
P1/P5 proofs remain the mathematical artifacts in proofs/; P2/P3 executable evidence
remains in exact/ and bounds/.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
REGISTRY = ROOT / "HST_THEOREM_REGISTRY_V1.json"
OVERLAY = ROOT / "HST_FORMALIZATION_CLOSURE_V1.json"
BRIDGE = ROOT / "HST_EMPIRICAL_BRIDGE_V1.json"
DEFINITIONS = ROOT / "HST_DEFINITIONS_V1.md"

ALLOWED_PRIMARY = {"P1", "P2", "P3", "P4", "P5"}
ALLOWED_TERMINALS = {
    "PROVED",
    "FINITE_CERTIFIED",
    "PARENT_SUFFICIENT",
    "BOUND_DERIVED",
    "BOUND_DERIVED_VACUOUS_AT_SCOPE",
}
EXPECTED = {f"HST-T{i:02d}" for i in range(1, 19)}

# The dependency overlay intentionally uses the frozen mathematical surface notation
# x/e/Adm/Useful.  Resolve those names explicitly rather than silently dropping them.
# Any unrecognized identifier is a closure failure.
DEFINITION_ALIASES = {
    "x": "proposal_x",
    "e": "evidence_e",
    "Adm": "frozen predicates Adm/Useful",
    "Useful": "frozen predicates Adm/Useful",
}
DEFINITION_PRIMITIVES = {
    "L_t",
    "Q_t",
    "H_t",
    "E_t",
    "R_t",
    "V_t",
    "U",
    "tau",
    "first-admissible stopping event",
}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def flatten_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for value in obj.values():
            yield from flatten_strings(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from flatten_strings(value)


def path_part(locator: str) -> str | None:
    """Return a repo-relative path when a locator starts with one."""
    candidate = locator.split("#", 1)[0].split("::", 1)[0].strip()
    if not candidate or " " in candidate:
        return None
    if candidate.endswith((".md", ".json", ".py", ".txt")):
        return candidate
    return None


def normalize_definition_graph(
    deps: dict[str, list[str]],
) -> tuple[dict[str, list[str]], list[str]]:
    """Resolve frozen surface aliases and reject every dangling dependency name."""
    external_parameters = set(deps.get("external_parameters", []))
    defined = set(deps) - {"external_parameters"}
    allowed_leaves = external_parameters | DEFINITION_PRIMITIVES
    graph: dict[str, list[str]] = {}
    unknown: list[str] = []

    for node in sorted(defined):
        values = deps.get(node, [])
        if not isinstance(values, list):
            unknown.append(f"{node}: dependency list is not a list")
            graph[node] = []
            continue
        resolved_edges: list[str] = []
        for raw_dep in values:
            dep = DEFINITION_ALIASES.get(raw_dep, raw_dep)
            if dep in defined:
                resolved_edges.append(dep)
            elif dep in allowed_leaves:
                continue
            else:
                unknown.append(f"{node} -> {raw_dep}")
        graph[node] = resolved_edges
    return graph, unknown


def definition_graph_is_acyclic(graph: dict[str, list[str]]) -> tuple[bool, list[str]]:
    visiting: set[str] = set()
    visited: set[str] = set()
    cycle: list[str] = []

    def visit(node: str, stack: list[str]) -> bool:
        if node in visiting:
            start = stack.index(node)
            cycle.extend(stack[start:] + [node])
            return False
        if node in visited:
            return True
        visiting.add(node)
        stack.append(node)
        for nxt in graph[node]:
            if not visit(nxt, stack):
                return False
        stack.pop()
        visiting.remove(node)
        visited.add(node)
        return True

    ok = all(visit(node, []) for node in sorted(graph) if node not in visited)
    return ok, cycle


def main() -> int:
    failures: list[str] = []
    for path in (REGISTRY, OVERLAY, BRIDGE, DEFINITIONS):
        require(path.is_file(), f"missing required file: {path.relative_to(ROOT)}", failures)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    registry = load_json(REGISTRY)
    overlay = load_json(OVERLAY)
    bridge = load_json(BRIDGE)

    require(
        overlay.get("allowed_primary_classes") == ["P1", "P2", "P3", "P4", "P5"],
        "overlay primary-class vocabulary drifted",
        failures,
    )

    reg_rows = registry.get("rows", [])
    ov_rows = overlay.get("rows", [])
    reg_by_id = {row.get("theorem_id"): row for row in reg_rows}
    ov_by_id = {row.get("theorem_id"): row for row in ov_rows}

    require(len(reg_rows) == len(reg_by_id), "duplicate theorem_id in frozen registry", failures)
    require(len(ov_rows) == len(ov_by_id), "duplicate theorem_id in closure overlay", failures)
    require(
        set(reg_by_id) == EXPECTED,
        f"registry theorem census mismatch: {sorted(set(reg_by_id) ^ EXPECTED)}",
        failures,
    )
    require(
        set(ov_by_id) == EXPECTED,
        f"overlay theorem census mismatch: {sorted(set(ov_by_id) ^ EXPECTED)}",
        failures,
    )

    bridge_rows = bridge.get("rows", {})
    bridge_expected = {f"T{i:02d}" for i in range(1, 19)}
    require(
        set(bridge_rows) == bridge_expected,
        f"empirical bridge census mismatch: {sorted(set(bridge_rows) ^ bridge_expected)}",
        failures,
    )

    deps = overlay.get("definition_dependencies", {})
    graph, unknown_dependencies = normalize_definition_graph(deps)
    require(
        not unknown_dependencies,
        "definition dependency identifiers do not resolve: " + ", ".join(unknown_dependencies),
        failures,
    )
    acyclic, cycle = definition_graph_is_acyclic(graph)
    require(acyclic, f"definition dependency cycle: {' -> '.join(cycle)}", failures)

    # Regression guard for the aliases that previously disappeared from the graph.
    require(
        graph.get("evidence_e") == ["proposal_x"],
        f"definition alias regression: evidence_e edges={graph.get('evidence_e')!r}",
        failures,
    )
    require(
        graph.get("Sigma_t_plus_1") == ["Sigma_t", "proposal_x", "evidence_e"],
        f"definition alias regression: Sigma_t_plus_1 edges={graph.get('Sigma_t_plus_1')!r}",
        failures,
    )
    require(
        graph.get("Ev_t") == ["proposal_x"],
        f"definition alias regression: Ev_t edges={graph.get('Ev_t')!r}",
        failures,
    )

    definitions_text = DEFINITIONS.read_text(encoding="utf-8")
    for needle in ("Σ_t", "B_t", "Ev_t", "One primary class per row"):
        require(needle in definitions_text, f"frozen definition anchor missing: {needle}", failures)

    class_counts = {name: 0 for name in sorted(ALLOWED_PRIMARY)}
    for theorem_id in sorted(EXPECTED):
        frozen = reg_by_id[theorem_id]
        row = ov_by_id[theorem_id]
        primary = row.get("primary_proof_class")
        require(primary in ALLOWED_PRIMARY, f"{theorem_id}: invalid primary class {primary!r}", failures)
        if primary in class_counts:
            class_counts[primary] += 1

        for field in ("domain", "quantifiers", "proof_artifact", "counterexample_or_escape", "claim_ceiling"):
            require(bool(str(row.get(field, "")).strip()), f"{theorem_id}: missing {field}", failures)

        require(bool(frozen.get("assumptions")), f"{theorem_id}: frozen assumptions missing", failures)
        require(bool(frozen.get("parent_theorem")), f"{theorem_id}: strongest/owning parent missing", failures)
        require(bool(frozen.get("ocm_residual")), f"{theorem_id}: OCM residual missing", failures)
        require(
            frozen.get("status") in ALLOWED_TERMINALS,
            f"{theorem_id}: non-terminal or unknown status {frozen.get('status')!r}",
            failures,
        )

        proof_path = path_part(row.get("proof_artifact", ""))
        if proof_path:
            require((ROOT / proof_path).is_file(), f"{theorem_id}: proof artifact path missing: {proof_path}", failures)

        exact_path = path_part(row.get("exact_certificate", "")) if row.get("exact_certificate") else None
        if exact_path:
            require((ROOT / exact_path).is_file(), f"{theorem_id}: exact certificate path missing: {exact_path}", failures)

        frozen_strings = "\n".join(flatten_strings(frozen))
        has_exact_evidence = bool(row.get("exact_certificate")) or "exact/" in frozen_strings
        if primary == "P2":
            require(has_exact_evidence, f"{theorem_id}: P2 primary lacks exact certificate/checker", failures)
        if primary == "P3":
            require(
                bool(row.get("distributional_assumptions")),
                f"{theorem_id}: P3 primary lacks explicit distributional assumptions",
                failures,
            )
            require(
                "bounds/" in str(row.get("proof_artifact", "")),
                f"{theorem_id}: P3 primary lacks bound artifact",
                failures,
            )
        if primary == "P4":
            require(bool(row.get("empirical_bridge")), f"{theorem_id}: P4 primary lacks preregistered bridge", failures)
        if primary == "P5":
            ceiling = row.get("claim_ceiling", "").lower()
            require(
                any(token in ceiling for token in ("limit", "bar", "unavailable", "requires", "never")),
                f"{theorem_id}: P5 row lacks explicit consequence/ceiling language",
                failures,
            )

        bridge_key = theorem_id.replace("HST-", "")
        bridge_row = bridge_rows.get(bridge_key, {})
        require(bool(bridge_row.get("hook")), f"{theorem_id}: empirical residual lacks concrete bridge hook", failures)
        require(bool(bridge_row.get("issue")), f"{theorem_id}: empirical residual lacks target issue", failures)

    require(
        class_counts["P4"] == 0,
        "HST theorem registry unexpectedly has a primary P4 theorem; P4 is intentionally carried as empirical residual bridges",
        failures,
    )
    require(bool(overlay.get("master_statement", "").strip()), "master surviving conditional statement missing", failures)

    result = {
        "schema": "HST_FORMALIZATION_CLOSURE_RECEIPT_V1",
        "verdict": "PASS" if not failures else "FAIL",
        "theorems_checked": len(EXPECTED),
        "primary_class_counts": class_counts,
        "bridge_rows_checked": len(bridge_rows),
        "definition_dependency_graph_acyclic": acyclic,
        "definition_dependency_unknown_identifiers": unknown_dependencies,
        "definition_dependency_resolved_edges": graph,
        "input_sha256": {
            REGISTRY.name: sha256(REGISTRY),
            OVERLAY.name: sha256(OVERLAY),
            BRIDGE.name: sha256(BRIDGE),
            DEFINITIONS.name: sha256(DEFINITIONS),
        },
        "failures": failures,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

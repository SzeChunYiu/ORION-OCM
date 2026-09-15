#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Set, Tuple

ROOT = Path(__file__).resolve().parent


class ValidationError(ValueError):
    pass


def load_json(name: str):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def validate_prior_ledger(data: Mapping) -> None:
    categories = set(data.get("allowed_categories", []))
    tiers = set(data.get("allowed_tiers", []))
    required_categories = {
        "ARCHITECTURE", "REPRESENTATION", "OPERATOR",
        "SEARCH", "ECOLOGICAL", "EVALUATION",
    }
    if categories != required_categories:
        raise ValidationError(f"prior categories mismatch: {sorted(categories)}")
    if tiers != {"P0", "P1", "P2", "P3", "P4"}:
        raise ValidationError(f"prior tiers mismatch: {sorted(tiers)}")
    entries = data.get("entries", [])
    if not entries:
        raise ValidationError("prior ledger has no entries")
    ids = set()
    seen_categories = set()
    for entry in entries:
        required = {"id", "category", "tier", "restriction", "used_by", "justification", "falsifier"}
        missing = required - set(entry)
        if missing:
            raise ValidationError(f"{entry.get('id', '<unknown>')} missing {sorted(missing)}")
        if entry["id"] in ids:
            raise ValidationError(f"duplicate prior id {entry['id']}")
        ids.add(entry["id"])
        if entry["category"] not in categories:
            raise ValidationError(f"unknown prior category {entry['category']}")
        if entry["tier"] not in tiers:
            raise ValidationError(f"unknown prior tier {entry['tier']}")
        if not entry["falsifier"].strip():
            raise ValidationError(f"{entry['id']} lacks falsifier")
        seen_categories.add(entry["category"])
    if seen_categories != required_categories:
        raise ValidationError(f"prior ledger does not disclose every category: {sorted(required_categories-seen_categories)}")
    claim = data.get("architecture_prior_free_claim", {})
    if claim.get("forbidden_interpretation") != "prior-free or assumption-free derivation":
        raise ValidationError("architecture-prior-free claim does not forbid literal prior-free interpretation")


def _descendants(node_id: str, children: Mapping[str, Sequence[str]]) -> Iterable[str]:
    stack = list(children.get(node_id, ()))
    seen = set()
    while stack:
        item = stack.pop()
        if item in seen:
            continue
        seen.add(item)
        yield item
        stack.extend(children.get(item, ()))


def validate_gap_graph(data: Mapping) -> None:
    allowed_status = set(data.get("closure_states", []))
    expected = {"OPEN", "LOCALLY_CLOSED", "HOSTILE_CLOSED", "REPLICATED_CLOSED", "REAL_SCALE_CLOSED"}
    if allowed_status != expected:
        raise ValidationError(f"closure states mismatch: {sorted(allowed_status)}")
    nodes = data.get("nodes", [])
    by_id = {}
    required = {
        "id", "kind", "title", "claim", "premises", "inference",
        "unresolved_assumption", "possible_counterexample", "severity", "owner",
        "parent", "dependencies", "evidence_required", "falsifier", "status",
    }
    for node in nodes:
        missing = required - set(node)
        if missing:
            raise ValidationError(f"{node.get('id', '<unknown>')} missing {sorted(missing)}")
        if node["id"] in by_id:
            raise ValidationError(f"duplicate gap id {node['id']}")
        if node["status"] not in allowed_status:
            raise ValidationError(f"{node['id']} has unknown status {node['status']}")
        if node["severity"] not in {"CRITICAL", "HIGH", "MEDIUM", "LOW"}:
            raise ValidationError(f"{node['id']} has unknown severity {node['severity']}")
        for key in ("claim", "inference", "unresolved_assumption", "possible_counterexample", "falsifier"):
            if not str(node[key]).strip():
                raise ValidationError(f"{node['id']} has empty {key}")
        if not node["evidence_required"]:
            raise ValidationError(f"{node['id']} lacks evidence_required")
        by_id[node["id"]] = node

    if "ISSUE-833" not in by_id:
        raise ValidationError("#833 root is missing")

    children: Dict[str, List[str]] = {node_id: [] for node_id in by_id}
    for node in nodes:
        parent = node["parent"]
        if parent is not None:
            if parent not in by_id:
                raise ValidationError(f"{node['id']} has dangling parent {parent}")
            children[parent].append(node["id"])
        for dep in node["dependencies"]:
            if dep not in by_id:
                raise ValidationError(f"{node['id']} has dangling dependency {dep}")

    # Parent-edge cycle detection.
    for start in by_id:
        seen = set()
        cur = start
        while cur is not None:
            if cur in seen:
                raise ValidationError(f"parent cycle reachable from {start}")
            seen.add(cur)
            cur = by_id[cur]["parent"]

    # Dependency graph cycle detection.
    temporary, permanent = set(), set()
    def visit(node_id: str) -> None:
        if node_id in permanent:
            return
        if node_id in temporary:
            raise ValidationError(f"dependency cycle at {node_id}")
        temporary.add(node_id)
        for dep in by_id[node_id]["dependencies"]:
            visit(dep)
        temporary.remove(node_id)
        permanent.add(node_id)
    for node_id in by_id:
        visit(node_id)

    # Fail-closed recursive rule requested by #833.
    for node in nodes:
        if node["status"] == "OPEN":
            continue
        for desc_id in _descendants(node["id"], children):
            desc = by_id[desc_id]
            if desc["severity"] == "CRITICAL" and desc["status"] == "OPEN":
                raise ValidationError(
                    f"{node['id']} cannot be {node['status']}: critical descendant {desc_id} is OPEN"
                )

    if by_id["ISSUE-833"]["status"] != "OPEN":
        raise ValidationError("#833 root must remain OPEN in this tranche")


def validate_results(data: Mapping) -> None:
    if data.get("evidence_level") != "E3-local":
        raise ValidationError("this package must stay at E3-local")
    if data.get("maturity") != "M3-local":
        raise ValidationError("this package must stay at M3-local")
    forbidden = {"universal intelligence", "literal prior-free induction", "#833 closure"}
    if not forbidden.issubset(set(data.get("nonclaims", []))):
        raise ValidationError("results claim ceiling lost required nonclaims")
    for claim in data.get("claims", []):
        if claim.get("universal_proof_from_finite_check") is not False:
            raise ValidationError(f"{claim.get('id')} launders a finite check into universal proof")
    for parent in data.get("strongest_parents", []):
        if parent.get("reclaimed") is not False:
            raise ValidationError(f"parent {parent.get('issue')} is incorrectly reclaimed")


# ---------- finite mathematical reconstruction ----------

def symmetry_sanity(max_n: int = 6) -> Dict[str, int]:
    checked = 0
    for n in range(2, max_n + 1):
        H = tuple(range(n))
        perms = list(itertools.permutations(H))
        # Evidence is fully invariant, so an equivariant selected h would have
        # to be fixed by every permutation. Verify that no candidate is.
        for h in H:
            if all(p[h] == h for p in perms):
                raise ValidationError(f"unexpected global fixed point for Sym({n}): {h}")
            checked += 1
    return {"hypothesis_sizes": max_n - 1, "candidate_fixed_point_checks": checked}


Machine = Mapping[int, Mapping[str, Tuple[int, int]]]


def behavioral_partition(machine: Machine) -> List[Set[int]]:
    states = sorted(machine)
    actions = sorted(next(iter(machine.values())))
    blocks = [set(states)]
    while True:
        cls = {s: i for i, block in enumerate(blocks) for s in block}
        groups: Dict[Tuple, Set[int]] = {}
        for s in states:
            sig = tuple((machine[s][a][0], cls[machine[s][a][1]]) for a in actions)
            groups.setdefault(sig, set()).add(s)
        new = sorted(groups.values(), key=lambda b: min(b))
        if {frozenset(b) for b in new} == {frozenset(b) for b in blocks}:
            return new
        blocks = new


def exact_map(machine: Machine, labels: Sequence[int]) -> bool:
    states = sorted(machine)
    actions = sorted(next(iter(machine.values())))
    for s in states:
        for t in states:
            if labels[s] != labels[t]:
                continue
            for a in actions:
                out_s, nxt_s = machine[s][a]
                out_t, nxt_t = machine[t][a]
                if out_s != out_t or labels[nxt_s] != labels[nxt_t]:
                    return False
    return True


def behavior_quotient_sanity() -> Dict[str, object]:
    # 0 and 1 are equivalent. State 2 is only distinguished from 0/1 after a
    # two-step experiment; 3 is immediately distinguished by action a.
    machine: Dict[int, Dict[str, Tuple[int, int]]] = {
        0: {"a": (0, 0), "b": (0, 2)},
        1: {"a": (0, 1), "b": (0, 2)},
        2: {"a": (0, 3), "b": (0, 2)},
        3: {"a": (1, 3), "b": (0, 3)},
    }
    blocks = behavioral_partition(machine)
    canonical = {frozenset(b) for b in blocks}
    expected = {frozenset({0, 1}), frozenset({2}), frozenset({3})}
    if canonical != expected:
        raise ValidationError(f"unexpected behavioral quotient {blocks}")

    # Hostile minimality reconstruction: no exact abstraction into <=2 labels.
    smaller_exact = []
    for k in (1, 2):
        for labels in itertools.product(range(k), repeat=len(machine)):
            if exact_map(machine, labels):
                smaller_exact.append((k, labels))
    if smaller_exact:
        raise ValidationError(f"found too-small exact abstraction: {smaller_exact[0]}")

    quotient_labels = (0, 0, 1, 2)
    if not exact_map(machine, quotient_labels):
        raise ValidationError("behavioral quotient map is not exact")
    return {"classes": [sorted(b) for b in blocks], "minimum_used_states": 3}


LTS = Mapping[str, Sequence[Tuple[str, str]]]


def finite_traces(graph: LTS, start: str) -> Set[Tuple[str, ...]]:
    memo: Dict[str, Set[Tuple[str, ...]]] = {}
    visiting = set()
    def rec(node: str) -> Set[Tuple[str, ...]]:
        if node in memo:
            return memo[node]
        if node in visiting:
            raise ValidationError("trace enumerator requires acyclic hostile fixture")
        visiting.add(node)
        traces: Set[Tuple[str, ...]] = {()}
        for label, dest in graph.get(node, ()):
            for suffix in rec(dest):
                traces.add((label,) + suffix)
        visiting.remove(node)
        memo[node] = traces
        return traces
    return rec(start)


def bisimilar(graph: LTS, left: str, right: str) -> bool:
    nodes = sorted(set(graph) | {dest for edges in graph.values() for _, dest in edges})
    relation = {(x, y) for x in nodes for y in nodes}
    changed = True
    while changed:
        changed = False
        for x, y in list(relation):
            xedges = graph.get(x, ())
            yedges = graph.get(y, ())
            forward = all(any(lx == ly and (dx, dy) in relation for ly, dy in yedges)
                          for lx, dx in xedges)
            backward = all(any(ly == lx and (dx, dy) in relation for lx, dx in xedges)
                           for ly, dy in yedges)
            if not (forward and backward):
                relation.remove((x, y))
                changed = True
    return (left, right) in relation


def nondeterminism_boundary_sanity() -> Dict[str, object]:
    graph: Dict[str, List[Tuple[str, str]]] = {
        "p0": [("a", "p1")],
        "p1": [("b", "z"), ("c", "z")],
        "q0": [("a", "qb"), ("a", "qc")],
        "qb": [("b", "z")],
        "qc": [("c", "z")],
        "z": [],
    }
    p = finite_traces(graph, "p0")
    q = finite_traces(graph, "q0")
    if p != q:
        raise ValidationError(f"N1 trace sets unexpectedly differ: {p} vs {q}")
    if bisimilar(graph, "p0", "q0"):
        raise ValidationError("N1 hostile pair unexpectedly bisimilar")
    return {"traces": ["".join(t) if t else "epsilon" for t in sorted(p)], "bisimilar": False}


def run_all() -> Dict[str, object]:
    prior = load_json("PRIOR_LEDGER.json")
    graph = load_json("GMI_GAP_GRAPH.json")
    results = load_json("RESULTS.json")
    validate_prior_ledger(prior)
    validate_gap_graph(graph)
    validate_results(results)
    return {
        "prior_ledger": "valid",
        "gap_graph": "valid",
        "results": "valid",
        "S1_finite_reconstruction": symmetry_sanity(),
        "B1_B3_finite_reconstruction": behavior_quotient_sanity(),
        "N1_finite_reconstruction": nondeterminism_boundary_sanity(),
        "claim_ceiling": "E3-local/M3-local; finite checks are not universal proofs",
    }


if __name__ == "__main__":
    print(json.dumps(run_all(), indent=2, sort_keys=True))

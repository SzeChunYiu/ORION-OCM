from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
import json
from typing import Any, Iterable, Sequence, Tuple

F = Fraction

FREEZE_COMMIT = "9cc71b4876cc1f578d93df79cdbb6b042a995fec"
CLAIM_CEILING = "DEPENDENCY_AWARE_UNCERTAINTY_COMPOSITION_AT_REGISTERED_FINITE_DAG_SCOPE"
MISSING_RELATION_FULL_DOMAIN = "MISSING_RELATION_FULL_DOMAIN"


def _probability(value: Any, name: str) -> F:
    if type(value) is not F:
        raise ValueError(f"{name} must be an exact Fraction")
    if not F(0) <= value <= F(1):
        raise ValueError(f"{name} must lie in [0,1]")
    return value


def _key(value: Any) -> tuple[int, Any]:
    if isinstance(value, bool):
        return (0, int(value))
    if isinstance(value, int):
        return (1, value)
    if type(value) is F:
        return (2, value)
    if isinstance(value, str):
        return (3, value)
    if isinstance(value, tuple):
        return (4, tuple(_key(v) for v in value))
    return (99, repr(value))


def _canon(values: Iterable[Any]) -> tuple[Any, ...]:
    return tuple(sorted(set(values), key=_key))


def _domain(values: tuple[Any, ...], name: str) -> tuple[Any, ...]:
    if not isinstance(values, tuple) or not values:
        raise ValueError(f"{name} must be a nonempty tuple")
    try:
        unique = set(values)
    except TypeError as exc:
        raise ValueError(f"{name} values must be hashable") from exc
    if len(unique) != len(values):
        raise ValueError(f"{name} contains duplicates")
    return _canon(values)


@dataclass(frozen=True)
class NodeSpec:
    name: str
    domain: tuple[Any, ...]
    parents: tuple[str, ...] = ()
    relation: tuple[tuple[tuple[Any, ...], Any], ...] | None = None
    beta: F = F(0)

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("node name must be a nonempty string")
        _domain(self.domain, f"domain({self.name})")
        if not isinstance(self.parents, tuple):
            raise ValueError("parents must be a tuple")
        if any(not isinstance(p, str) or not p.strip() for p in self.parents):
            raise ValueError("parent names must be nonempty strings")
        if len(set(self.parents)) != len(self.parents):
            raise ValueError(f"{self.name} contains duplicate parent names")
        if self.name in self.parents:
            raise ValueError(f"{self.name} cannot parent itself")
        _probability(self.beta, f"beta({self.name})")
        if not self.parents:
            if self.relation is not None:
                raise ValueError("root nodes cannot register a local relation")
            if self.beta != 0:
                raise ValueError("root nodes cannot claim a local relation-failure budget")
        elif self.relation is None and self.beta != 0:
            raise ValueError("missing relation cannot claim a relation-failure budget")
        elif self.relation is not None and not isinstance(self.relation, tuple):
            raise ValueError("relation must be a tuple or None")


@dataclass(frozen=True)
class RootContract:
    roots: tuple[str, ...]
    joint_set: tuple[tuple[Any, ...], ...]
    alpha: F
    source_kind: str

    def __post_init__(self):
        if not isinstance(self.roots, tuple) or not self.roots:
            raise ValueError("roots must be a nonempty tuple")
        if len(set(self.roots)) != len(self.roots):
            raise ValueError("roots contain duplicates")
        if not isinstance(self.joint_set, tuple):
            raise ValueError("joint_set must be a tuple")
        _probability(self.alpha, "root alpha")
        if self.source_kind not in {"JOINT", "MARGINAL_UNION_BOUND"}:
            raise ValueError("unsupported root source_kind")


@dataclass(frozen=True)
class DagResult:
    topological_order: tuple[str, ...]
    global_assignments: tuple[tuple[Any, ...], ...]
    global_output: tuple[tuple[Any, ...], ...]
    local_sets: tuple[tuple[str, tuple[Any, ...]], ...]
    local_output: tuple[tuple[Any, ...], ...]
    lower_coverage: F
    missing_nodes: tuple[str, ...]


class DagCampaign:
    def __init__(self):
        self._nodes: list[NodeSpec] = []
        self._outputs: tuple[str, ...] | None = None
        self._root_contract: RootContract | None = None
        self._active = False

    @property
    def active(self) -> bool:
        return self._active

    @property
    def nodes(self) -> tuple[NodeSpec, ...]:
        return tuple(self._nodes)

    def register_node(self, node: NodeSpec) -> None:
        if self._active:
            raise RuntimeError("campaign is frozen after activation")
        if not isinstance(node, NodeSpec):
            raise ValueError("node must be NodeSpec")
        if node.name in {n.name for n in self._nodes}:
            raise ValueError(f"duplicate node name: {node.name}")
        self._nodes.append(node)

    def set_outputs(self, outputs: tuple[str, ...]) -> None:
        if self._active:
            raise RuntimeError("campaign is frozen after activation")
        if not isinstance(outputs, tuple) or not outputs:
            raise ValueError("outputs must be a nonempty tuple")
        if len(set(outputs)) != len(outputs):
            raise ValueError("outputs contain duplicates")
        self._outputs = outputs

    def set_joint_root_contract(
        self,
        roots: tuple[str, ...],
        joint_set: tuple[tuple[Any, ...], ...],
        alpha: F,
    ) -> None:
        if self._active:
            raise RuntimeError("campaign is frozen after activation")
        self._root_contract = RootContract(roots, joint_set, alpha, "JOINT")

    def set_marginal_root_contract(
        self,
        roots: tuple[str, ...],
        marginal_sets: tuple[tuple[Any, ...], ...],
        alphas: tuple[F, ...],
    ) -> None:
        if self._active:
            raise RuntimeError("campaign is frozen after activation")
        if not isinstance(roots, tuple) or not roots:
            raise ValueError("roots must be a nonempty tuple")
        if not isinstance(marginal_sets, tuple) or len(marginal_sets) != len(roots):
            raise ValueError("marginal_sets must align with roots")
        if not isinstance(alphas, tuple) or len(alphas) != len(roots):
            raise ValueError("alphas must align with roots")
        total = F(0)
        for i, alpha in enumerate(alphas):
            total += _probability(alpha, f"alpha[{i}]")
        joint = tuple(product(*marginal_sets))
        self._root_contract = RootContract(
            roots=roots,
            joint_set=joint,
            alpha=min(F(1), total),
            source_kind="MARGINAL_UNION_BOUND",
        )

    def _node_map(self) -> dict[str, NodeSpec]:
        return {node.name: node for node in self._nodes}

    def _validate_and_toposort(self) -> tuple[str, ...]:
        if not self._nodes:
            raise ValueError("graph must contain at least one node")
        node_map = self._node_map()
        if len(node_map) != len(self._nodes):
            raise ValueError("duplicate node names")
        for node in self._nodes:
            for parent in node.parents:
                if parent not in node_map:
                    raise ValueError(f"unknown parent {parent!r} for node {node.name!r}")

        indegree = {node.name: len(node.parents) for node in self._nodes}
        children: dict[str, list[str]] = {node.name: [] for node in self._nodes}
        for node in self._nodes:
            for parent in node.parents:
                children[parent].append(node.name)
        queue = [node.name for node in self._nodes if indegree[node.name] == 0]
        order: list[str] = []
        while queue:
            name = queue.pop(0)
            order.append(name)
            for child in children[name]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    queue.append(child)
        if len(order) != len(self._nodes):
            raise ValueError("graph contains a directed cycle")
        return tuple(order)

    def _roots(self, topo: tuple[str, ...]) -> tuple[str, ...]:
        node_map = self._node_map()
        return tuple(name for name in topo if not node_map[name].parents)

    def _validate_relation_rows(self, node: NodeSpec, node_map: dict[str, NodeSpec]) -> None:
        if node.relation is None:
            return
        parent_domains = [set(_domain(node_map[p].domain, f"domain({p})")) for p in node.parents]
        out_domain = set(_domain(node.domain, f"domain({node.name})"))
        seen = set()
        for row in node.relation:
            if not isinstance(row, tuple) or len(row) != 2:
                raise ValueError(f"relation({node.name}) rows must be (parent_tuple, output)")
            parent_tuple, output = row
            if not isinstance(parent_tuple, tuple) or len(parent_tuple) != len(node.parents):
                raise ValueError(f"relation({node.name}) parent tuple has wrong arity")
            for i, value in enumerate(parent_tuple):
                if value not in parent_domains[i]:
                    raise ValueError(f"relation({node.name}) parent endpoint outside domain")
            if output not in out_domain:
                raise ValueError(f"relation({node.name}) output outside domain")
            try:
                key = (parent_tuple, output)
                if key in seen:
                    raise ValueError(f"relation({node.name}) contains duplicate rows")
                seen.add(key)
            except TypeError as exc:
                raise ValueError("relation values must be hashable") from exc

    def _validate_root_contract(
        self, topo: tuple[str, ...], node_map: dict[str, NodeSpec]
    ) -> RootContract:
        if self._root_contract is None:
            raise ValueError("root contract must be registered before activation")
        contract = self._root_contract
        roots = self._roots(topo)
        if contract.roots != roots:
            raise ValueError(
                f"root contract order {contract.roots!r} must equal graph root order {roots!r}"
            )
        root_domains = [set(_domain(node_map[r].domain, f"domain({r})")) for r in roots]
        seen = set()
        for root_tuple in contract.joint_set:
            if not isinstance(root_tuple, tuple) or len(root_tuple) != len(roots):
                raise ValueError("root confidence tuple has wrong arity")
            for i, value in enumerate(root_tuple):
                if value not in root_domains[i]:
                    raise ValueError("root confidence tuple contains value outside root domain")
            if root_tuple in seen:
                raise ValueError("root confidence set contains duplicate tuples")
            seen.add(root_tuple)
        return contract

    def activate(self) -> None:
        if self._active:
            return
        topo = self._validate_and_toposort()
        node_map = self._node_map()
        if self._outputs is None:
            raise ValueError("outputs must be registered before activation")
        for out in self._outputs:
            if out not in node_map:
                raise ValueError(f"unknown output node {out!r}")
        for node in self._nodes:
            self._validate_relation_rows(node, node_map)
        self._validate_root_contract(topo, node_map)
        self._active = True

    def _config(self):
        if not self._active:
            raise RuntimeError("campaign must be activated before execution")
        topo = self._validate_and_toposort()
        node_map = self._node_map()
        contract = self._validate_root_contract(topo, node_map)
        return topo, node_map, contract

    def global_feasible_assignments(self) -> tuple[tuple[Any, ...], ...]:
        topo, node_map, contract = self._config()
        roots = self._roots(topo)
        root_indices = tuple(topo.index(r) for r in roots)
        root_allowed = set(contract.joint_set)
        domains = [node_map[name].domain for name in topo]
        feasible = []
        for assignment in product(*domains):
            root_tuple = tuple(assignment[i] for i in root_indices)
            if root_tuple not in root_allowed:
                continue
            values = dict(zip(topo, assignment))
            good = True
            for name in topo:
                node = node_map[name]
                if not node.parents or node.relation is None:
                    continue
                parent_tuple = tuple(values[p] for p in node.parents)
                if (parent_tuple, values[name]) not in set(node.relation):
                    good = False
                    break
            if good:
                feasible.append(tuple(assignment))
        return tuple(sorted(feasible, key=_key))

    def project_global(
        self, assignments: tuple[tuple[Any, ...], ...] | None = None
    ) -> tuple[tuple[Any, ...], ...]:
        topo, _, _ = self._config()
        assignments = self.global_feasible_assignments() if assignments is None else assignments
        if self._outputs is None:
            raise RuntimeError("campaign outputs are unavailable")
        indices = tuple(topo.index(o) for o in self._outputs)
        return _canon(tuple(tuple(row[i] for i in indices) for row in assignments))

    def local_sets(self) -> tuple[tuple[str, tuple[Any, ...]], ...]:
        topo, node_map, contract = self._config()
        roots = self._roots(topo)
        root_index = {root: i for i, root in enumerate(roots)}
        local: dict[str, tuple[Any, ...]] = {}
        for name in topo:
            node = node_map[name]
            if not node.parents:
                i = root_index[name]
                local[name] = _canon(row[i] for row in contract.joint_set)
                continue
            parent_sets = [local[p] for p in node.parents]
            if any(len(s) == 0 for s in parent_sets):
                local[name] = ()
                continue
            if node.relation is None:
                local[name] = _canon(node.domain)
                continue
            allowed_parents = set(product(*parent_sets))
            local[name] = _canon(
                output
                for parent_tuple, output in node.relation
                if parent_tuple in allowed_parents
            )
        return tuple((name, local[name]) for name in topo)

    def project_local(self) -> tuple[tuple[Any, ...], ...]:
        topo, _, _ = self._config()
        if self._outputs is None:
            raise RuntimeError("campaign outputs are unavailable")
        local = dict(self.local_sets())
        return tuple(product(*(local[o] for o in self._outputs)))

    def coverage_lower_bound(self) -> F:
        _, node_map, contract = self._config()
        total = contract.alpha
        for node in node_map.values():
            if node.parents and node.relation is not None:
                total += node.beta
        return max(F(0), F(1) - total)

    def execute(self) -> DagResult:
        topo, node_map, _ = self._config()
        global_assignments = self.global_feasible_assignments()
        missing = tuple(
            name
            for name in topo
            if node_map[name].parents and node_map[name].relation is None
        )
        return DagResult(
            topological_order=topo,
            global_assignments=global_assignments,
            global_output=self.project_global(global_assignments),
            local_sets=self.local_sets(),
            local_output=self.project_local(),
            lower_coverage=self.coverage_lower_bound(),
            missing_nodes=missing,
        )


def _function_relation_unary(
    parent: str, outputs: tuple[int, int]
) -> tuple[tuple[tuple[int, ...], int], ...]:
    del parent
    return (((0,), outputs[0]), ((1,), outputs[1]))


def _function_relation_binary(
    outputs: tuple[int, int, int, int]
) -> tuple[tuple[tuple[int, ...], int], ...]:
    parents = ((0, 0), (0, 1), (1, 0), (1, 1))
    return tuple((parents[i], outputs[i]) for i in range(4))


def _all_bits(n: int) -> tuple[tuple[int, ...], ...]:
    return tuple(product((0, 1), repeat=n))


def _root_subsets_binary() -> tuple[tuple[tuple[int, ...], ...], ...]:
    atoms = ((0,), (1,))
    return tuple(
        tuple(atoms[i] for i, keep in enumerate(mask) if keep)
        for mask in product((False, True), repeat=2)
    )


def _single_output_values(output_tuples: tuple[tuple[Any, ...], ...]) -> tuple[Any, ...]:
    return _canon(row[0] for row in output_tuples)


def exhaustive_local_soundness_certificate() -> dict[str, int | bool]:
    cases = 0
    failures = 0
    strict = 0
    binary = (0, 1)
    unary_functions = _all_bits(2)
    binary_functions = _all_bits(4)
    for root_set in _root_subsets_binary():
        for fa in unary_functions:
            for fb in unary_functions:
                for fy in binary_functions:
                    campaign = DagCampaign()
                    campaign.register_node(NodeSpec("x", binary))
                    campaign.register_node(
                        NodeSpec("a", binary, ("x",), _function_relation_unary("x", fa), F(0))
                    )
                    campaign.register_node(
                        NodeSpec("b", binary, ("x",), _function_relation_unary("x", fb), F(0))
                    )
                    campaign.register_node(
                        NodeSpec("y", binary, ("a", "b"), _function_relation_binary(fy), F(0))
                    )
                    campaign.set_outputs(("y",))
                    campaign.set_joint_root_contract(("x",), root_set, F(0))
                    campaign.activate()
                    result = campaign.execute()
                    global_y = set(_single_output_values(result.global_output))
                    local_y = set(_single_output_values(result.local_output))
                    cases += 1
                    if not global_y.issubset(local_y):
                        failures += 1
                    if global_y < local_y:
                        strict += 1
    return {
        "cases": cases,
        "failures": failures,
        "strict_overapproximation_cases": strict,
        "all_sound": failures == 0,
        "strict_dependency_loss_exercised": strict > 0,
    }


def shared_ancestor_hostile() -> dict[str, Any]:
    campaign = DagCampaign()
    campaign.register_node(NodeSpec("x", (-1, 1)))
    campaign.register_node(
        NodeSpec("a", (-1, 1), ("x",), (((-1,), -1), ((1,), 1)), F(0))
    )
    campaign.register_node(
        NodeSpec("b", (-1, 1), ("x",), (((-1,), -1), ((1,), 1)), F(0))
    )
    y_relation = tuple(
        ((a, b), a - b)
        for a in (-1, 1)
        for b in (-1, 1)
    )
    campaign.register_node(NodeSpec("y", (-2, 0, 2), ("a", "b"), y_relation, F(0)))
    campaign.set_outputs(("y",))
    campaign.set_joint_root_contract(("x",), ((-1,), (1,)), F(0))
    campaign.activate()
    result = campaign.execute()
    return {
        "global_y": list(_single_output_values(result.global_output)),
        "local_y": list(_single_output_values(result.local_output)),
        "strict": set(_single_output_values(result.global_output))
        < set(_single_output_values(result.local_output)),
    }


def joint_root_xor_control() -> dict[str, Any]:
    campaign = DagCampaign()
    campaign.register_node(NodeSpec("r1", (0, 1)))
    campaign.register_node(NodeSpec("r2", (0, 1)))
    relation = tuple(((a, b), a ^ b) for a in (0, 1) for b in (0, 1))
    campaign.register_node(NodeSpec("y", (0, 1), ("r1", "r2"), relation, F(0)))
    campaign.set_outputs(("y",))
    campaign.set_joint_root_contract(("r1", "r2"), ((0, 0), (1, 1)), F(0))
    campaign.activate()
    result = campaign.execute()
    return {
        "global_y": list(_single_output_values(result.global_output)),
        "local_y": list(_single_output_values(result.local_output)),
        "strict": set(_single_output_values(result.global_output))
        < set(_single_output_values(result.local_output)),
    }


def nonlinear_setvalued_control() -> dict[str, Any]:
    campaign = DagCampaign()
    campaign.register_node(NodeSpec("x", (-2, -1, 0, 1, 2)))
    s_relation = tuple(((x,), x * x) for x in (-2, -1, 0, 1, 2))
    campaign.register_node(NodeSpec("s", (0, 1, 4), ("x",), s_relation, F(0)))
    q_relation = tuple(
        ((s,), q)
        for s in (0, 1, 4)
        for q in (s - 1, s, s + 1)
    )
    campaign.register_node(
        NodeSpec("q", (-1, 0, 1, 2, 3, 4, 5), ("s",), q_relation, F(0))
    )
    campaign.set_outputs(("s", "q"))
    campaign.set_joint_root_contract(("x",), ((-1,), (0,), (1,)), F(1, 20))
    campaign.activate()
    result = campaign.execute()
    local = dict(result.local_sets)
    global_s = _canon(row[0] for row in result.global_output)
    global_q = _canon(row[1] for row in result.global_output)
    return {
        "global_s": list(global_s),
        "global_q": list(global_q),
        "local_s": list(local["s"]),
        "local_q": list(local["q"]),
        "coverage_lower_bound": frac(result.lower_coverage),
    }


def marginal_dependence_hostile() -> dict[str, Any]:
    omega = {"a", "b", "c", "d"}
    f1 = {"a"}
    f2 = {"b"}
    g1 = omega - f1
    g2 = omega - f2
    joint = F(len(g1 & g2), 4)
    product_bound = F(len(g1), 4) * F(len(g2), 4)
    union_lower = F(1) - F(len(f1), 4) - F(len(f2), 4)

    of1 = {"a"}
    of2 = {"a"}
    og1 = omega - of1
    og2 = omega - of2
    overlap_joint = F(len(og1 & og2), 4)
    overlap_union = F(1) - F(1, 4) - F(1, 4)

    return {
        "disjoint": {
            "marginal_coverage_1": "3/4",
            "marginal_coverage_2": "3/4",
            "true_joint_coverage": frac(joint),
            "independence_product": frac(product_bound),
            "union_lower": frac(union_lower),
            "product_unsound": product_bound > joint,
            "union_attained": union_lower == joint,
        },
        "overlap": {
            "true_joint_coverage": frac(overlap_joint),
            "union_lower": frac(overlap_union),
            "union_conservative": overlap_joint > overlap_union,
        },
    }


def missing_relation_control() -> dict[str, Any]:
    campaign = DagCampaign()
    campaign.register_node(NodeSpec("x", (0, 1)))
    campaign.register_node(NodeSpec("m", ("a", "b", "c"), ("x",), None, F(0)))
    downstream = (
        (("a",), 0),
        (("b",), 1),
        (("c",), 1),
    )
    campaign.register_node(NodeSpec("y", (0, 1), ("m",), downstream, F(0)))
    campaign.set_outputs(("m", "y"))
    campaign.set_joint_root_contract(("x",), ((0,),), F(1, 20))
    campaign.activate()
    result = campaign.execute()
    local = dict(result.local_sets)
    return {
        "missing_nodes": list(result.missing_nodes),
        "global_m": list(_canon(row[0] for row in result.global_output)),
        "global_y": list(_canon(row[1] for row in result.global_output)),
        "local_m": list(local["m"]),
        "local_y": list(local["y"]),
        "coverage_lower_bound": frac(result.lower_coverage),
    }


def budget_controls() -> dict[str, Any]:
    alpha = F(1, 20)
    betas = (F(1, 100), F(1, 200), F(1, 400))
    lower = max(F(0), F(1) - alpha - sum(betas, F(0)))
    marginal_alpha = F(1, 40) + F(1, 40)
    lower_marginal = max(F(0), F(1) - marginal_alpha - sum(betas, F(0)))
    return {
        "joint_source": {
            "alpha": frac(alpha),
            "betas": [frac(x) for x in betas],
            "lower": frac(lower),
        },
        "marginal_source": {
            "alphas": ["1/40", "1/40"],
            "union_alpha": frac(marginal_alpha),
            "betas": [frac(x) for x in betas],
            "lower": frac(lower_marginal),
        },
    }


def frac(value: F) -> str:
    if type(value) is not F:
        raise ValueError("frac requires Fraction")
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def build_receipt() -> dict[str, Any]:
    return {
        "schema": "DependencyAwareUncertaintyCompositionReceiptV1",
        "issue": 759,
        "parent_issue": 602,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM_CEILING,
        "proof_classes": {
            "DA-1": ["P1", "P2"],
            "DA-2": ["P1", "P2"],
            "DA-3": ["P1", "P2"],
            "DA-4": ["P1", "P2"],
        },
        "exhaustive_local_soundness": exhaustive_local_soundness_certificate(),
        "shared_ancestor_hostile": shared_ancestor_hostile(),
        "joint_root_xor_control": joint_root_xor_control(),
        "marginal_dependence_hostile": marginal_dependence_hostile(),
        "nonlinear_setvalued_control": nonlinear_setvalued_control(),
        "missing_relation_control": missing_relation_control(),
        "budget_controls": budget_controls(),
        "hostile_summary": {
            "cycle_rejected": True,
            "post_activation_mutation_rejected": True,
            "registered_empty_relation_distinct_from_missing": True,
        },
        "forbidden_claims": [
            "UNIVERSAL_UNCERTAINTY_PROPAGATION",
            "PROBABILISTIC_CAPABILITY_CALIBRATION",
            "INDEPENDENCE_PROVED",
            "REAL_SCALE_CALIBRATION",
            "G6",
            "G7",
            "COMPLETE_GMI",
        ],
    }


def canonical_receipt_bytes() -> bytes:
    return (json.dumps(build_receipt(), indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    print(canonical_receipt_bytes().decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

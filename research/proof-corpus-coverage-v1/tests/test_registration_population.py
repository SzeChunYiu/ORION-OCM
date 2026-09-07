"""Full-population contracts exercised only on authored metadata."""
from copy import deepcopy
from hashlib import sha256
import pytest
from registration_fixture import inputs, metadata, population, refresh


def test_complete_toy_population_and_lexical_dependency():
    source, graph, solutions, _ = metadata()
    graph["nodes"]["beta"]["dependencies"] = ["alpha"]
    graph["edge_count"] = 1
    solutions["beta"]["imports"].append("Theorems.Thm_alpha")
    refresh(graph)
    rows = population.validate_population(source, graph, solutions, 2)
    assert {r["key"] for r in rows} == {"alpha", "beta"}
    assert rows[0]["wrapper"] == source["files"]["Theorems/Thm_alpha.lean"]


@pytest.mark.parametrize("mutate,reason", [
    (lambda s,g,z: s.update(identity="TRUST_ME"), "source authority"),
    (lambda s,g,z: s["files"]["Theorems/Thm_alpha.lean"].update(state="REFUSED"), "file identity"),
    (lambda s,g,z: s["files"]["Theorems/Thm_alpha.lean"].update(mode="120000"), "file identity"),
    (lambda s,g,z: s["files"]["Theorems/Thm_alpha.lean"].update(bytes=True), "file size"),
    (lambda s,g,z: z.pop("beta"), "solution keyset"),
    (lambda s,g,z: s["files"].pop("P2M/Sol/S_beta.lean"), "source pair keyset"),
    (lambda s,g,z: g.update(node_count=True), "node count"),
    (lambda s,g,z: g.update(semantic_dependencies_verified=True), "graph scope"),
    (lambda s,g,z: g.update(topological_order=["alpha", "alpha"]), "topological keyset"),
    (lambda s,g,z: g["nodes"]["alpha"].update(dependencies=["unknown"]), "dependency keyset"),
    (lambda s,g,z: g["nodes"]["beta"].update(dependencies=["alpha", "alpha"]), "dependency keyset"),
    (lambda s,g,z: g["nodes"]["alpha"].update(dependencies=["beta"]), "dependency order"),
    (lambda s,g,z: z["beta"]["imports"].append("Theorems.Thm_alpha"), "import dependency mismatch"),
    (lambda s,g,z: z["beta"].update(solution_id="beta"), "solution duplicate identity"),
    (lambda s,g,z: z["beta"].update(solution_bytes=True), "solution duplicate identity"),
    (lambda s,g,z: z["beta"].update(solution_sha256="f" * 64), "solution duplicate identity"),
    (lambda s,g,z: z["beta"].update(oid="f" * 40), "solution source identity"),
    (lambda s,g,z: g["nodes"]["alpha"].update(wrapper_sha256="f" * 64), "wrapper hash"),
    (lambda s,g,z: g.update(edge_count=True), "edge count"),
    (lambda s,g,z: g.update(graph_sha256="f" * 64), "internal graph digest"),
])
def test_invalid_metadata_refuses_at_intended_boundary(mutate, reason):
    source, graph, solutions, _ = metadata()
    mutate(source, graph, solutions)
    with pytest.raises(ValueError, match=reason):
        population.validate_population(source, graph, solutions, 2)


@pytest.mark.parametrize("path,reason", [("Theorems/Other.lean", "wrapper path"), ("P2M/Sol/Other.lean", "solution path")])
def test_noncanonical_pair_path_is_not_context(path, reason):
    source, graph, solutions, _ = metadata()
    source["files"][path] = dict(source["files"]["Theorems/Thm_alpha.lean"], path=path)
    with pytest.raises(ValueError, match=reason):
        population.validate_population(source, graph, solutions, 2)


def test_assignment_independent_of_input_order_and_payload():
    source, graph, solutions, _ = metadata(("alpha", "beta", "gamma", "delta", "epsilon"))
    rows = population.validate_population(source, graph, solutions, 5)
    before = deepcopy(rows)
    assigned = population.ordered_population(rows, source["commit"])
    expected = {r["key"]: sha256(b"ocm.f1.semantic-coverage.v1\0" + b"a" * 40 + b"\0" + r["key"].encode()).hexdigest() for r in rows}
    assert {r["key"]: r["assignment_digest"] for r in assigned} == expected
    assert [r["key"] for r in assigned] == sorted(expected, key=lambda k: (bytes.fromhex(expected[k]), k.encode()))
    changed = deepcopy(rows[::-1])
    for r in changed: r["wrapper"]["bytes"] += 1000
    second = population.ordered_population(changed, source["commit"])
    assert [(r["key"], r["assignment_digest"]) for r in second] == [(r["key"], r["assignment_digest"]) for r in assigned]
    assert rows == before
    with pytest.raises(ValueError, match="duplicate population key"):
        population.ordered_population(rows + rows[:1], source["commit"])


def test_authorized_json_rejects_duplicate_keys_and_hash_drift(tmp_path):
    path = tmp_path / "metadata.json"
    path.write_bytes(b'{"key":1,"key":2}\n')
    with pytest.raises(ValueError, match="duplicate JSON key"):
        inputs.bound_json(path, sha256(path.read_bytes()).hexdigest())
    path.write_bytes(b'{"key":1}\n')
    with pytest.raises(ValueError, match="independently registered digest"):
        inputs.bound_json(path, "f" * 64)

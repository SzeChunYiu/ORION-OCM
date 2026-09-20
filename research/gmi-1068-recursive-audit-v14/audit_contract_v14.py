"""Reviewed exact stochastic-process adjudication and source custody."""
import hashlib
import importlib.util
import json

PACKAGE = "research/gmi-1068-stochastic-process-v14"
ATOM_SPECS = {
    "GMI2-R1-008": ("formalize stochastic/nondeterministic optional structure", "Finite stochastic kernels and total relations supply lawful optional process instances with faithful deterministic embeddings; support preserves composition but loses probabilities. Generic scalar-law and actual finite rational proofs are distinguished from paper-level rational/real specialization."),
}
REPAIR_SCOPES = {
    "R1": "Finite stochastic kernels and total relations are lawful optional process instances with faithful deterministic embeddings. Support preserves identities and composition but loses probability information; uniformization is not functorial. Only the original optional-structure atom closes; other process obligations remain open.",
    "R14": "Lean 4.19.0 checks registered arbitrary finite kernel laws under explicit nonnegative-weight scalar assumptions, general total-relation laws, deterministic embeddings, support laws and an actual finite rational model. General rational/real scalar instantiation remains paper-level.",
    "R15": "Independent exact path sums and relational reachability check all registered kernels, relations, maps and composable pairs/triples, including empty objects and products outside the input grid. Malformed inputs, assumption countermodels and exact evidence guards limit closure to the registered optional-structure requirement.",
}
BOUNDARIES = [
    "one original scientific requirement only; R1 remains open",
    "generic nonnegative-weight semiring laws are explicit assumptions",
    "general rational/real scalar instantiation remains paper-level",
    "the actual finite rational model uses kernel-checked arithmetic",
    "support loses probabilities; uniformization does not preserve composition",
    "206 original requirements retain their unresolved statuses",
    "no canonical probability assignment, architecture recovery or empirical novelty",
]
SOURCE_BINDINGS = {
    "research/gmi-1068-grand-unified-v2-r0/ATOMIC_CHECKLIST_V1.json": "4cc262d491fbcdccf2b4c8656e80dcdb06e1795344500e46ac980ca09a679574",
    "research/gmi-1068-r1-minimal-process-core-v1/FREEZE_V1.md": "5f755106e6e5e2fcda6257d71e6eda6f2d895adf817834b2f2464685a491558a",
    "research/gmi-1068-recursive-audit-v13/SCOPE_SNAPSHOT_V13.json": "db349656850afb8d7cd6248d73ab0338792ee8a30d91bc6dc26f5decc534dea0",
}
SOURCE_NAMES = ("WeightSumsV14.lean", "MatricesV14.lean", "RelationsV14.lean", "SupportV14.lean", "RationalModelV14.lean")
PROOF_CONTRACT_SHA = "b96fde74e0923dfce9bcf492b1339f63766f3d9e739f0a8d1026bf4a6c03b345"
PROOF_AUDIT_SHA = "4b4ac4e2ea2d75dad29e6bca161686f2b03ddd5b13c185d3711d2dc95dedc95b"
PROOF_COUNT = 37


def need(condition, message):
    if not condition:
        raise ValueError(message)


def exact(actual, expected, message):
    need(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True), message)


def load(path):
    spec = importlib.util.spec_from_file_location("v14_contract_" + path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_artifacts(root):
    return [{"path": str(path.relative_to(root)), "sha256": digest(path)}
            for path in sorted((root / PACKAGE).iterdir())
            if path.is_file() and path.suffix in {".py", ".md", ".lean", ".json"}]


def witness(root, name, kind, locator):
    path = PACKAGE + "/" + name
    return {"path": path, "sha256": digest(root / path), "kind": kind, "locator": locator}


def atom_evidence(root, atom):
    need(atom in ATOM_SPECS, "unregistered atom")
    declarations = (("MatricesV14.lean", "assoc"), ("RelationsV14.lean", "assoc"),
                    ("SupportV14.lean", "support_comp"), ("RationalModelV14.lean", "support_probability_loss"))
    return [witness(root, "RESULT_V14.json", "json_pointer", "/atoms/" + atom)] + [
        witness(root, name, "lean_declaration", declaration) for name, declaration in declarations]


def repair(root, name):
    evidence = [witness(root, "check_stochastic_v14.py", "python_symbol", "evaluate"),
                witness(root, "RESULT_V14.json", "json_pointer", "/kernel" if name == "R14" else "/coverage")]
    extras = {"R1": ("SupportV14.lean", "lean_declaration", "support_comp"),
              "R14": ("proof_contract_v14.py", "python_symbol", "audit_source"),
              "R15": ("independent_oracle_v14.py", "python_symbol", "path_sum")}
    evidence.insert(0, witness(root, *extras[name]))
    return {"id": name + "-stochastic-v14", "scope": REPAIR_SCOPES[name],
            "status": "LOCAL_VERIFIED", "evidence": evidence}


def validate_receipt(root, receipt):
    need(type(receipt) is dict and set(receipt) == {
        "schema", "tests_run", "kernel", "coverage", "source_bindings", "atoms", "inputs",
        "overall_closure", "scientific_truth_certified", "claim_boundaries"}, "receipt fields")
    fixed = {"schema": "GMI_1068_STOCHASTIC_PROCESS_V14", "tests_run": 9,
             "overall_closure": "OPEN", "scientific_truth_certified": False, "claim_boundaries": BOUNDARIES}
    for key, value in fixed.items():
        exact(receipt[key], value, "receipt field drift:" + key)
    atoms = {key: {"title": title, "scope": scope, "status": "VERIFIED_AT_REGISTERED_SCOPE"}
             for key, (title, scope) in ATOM_SPECS.items()}
    exact(receipt["atoms"], atoms, "registered atom adjudication drift")
    artifacts = package_artifacts(root)
    inputs = {entry["path"].rsplit("/", 1)[-1]: entry["sha256"] for entry in artifacts
              if not entry["path"].endswith("/RESULT_V14.json")}
    exact(receipt["inputs"], inputs, "package input custody drift")
    exact(receipt["source_bindings"], SOURCE_BINDINGS, "historical source receipt drift")
    for path, expected in SOURCE_BINDINGS.items():
        need(digest(root / path) == expected, "historical source drift:" + path)
    package = root / PACKAGE
    exact(receipt["coverage"], load(package / "coverage_v14.py").REQUIRED, "coverage receipt drift")
    need(digest(package / "proof_contract_v14.py") == PROOF_CONTRACT_SHA, "reviewed proof-type drift")
    proof = load(package / "proof_contract_v14.py")
    need(proof.SOURCE_NAMES == SOURCE_NAMES and len(proof.ENTRIES) == PROOF_COUNT, "registered proof inventory drift")
    need(hashlib.sha256(proof.audit_source().encode()).hexdigest() == PROOF_AUDIT_SHA, "proof audit drift")
    expected_kernel = {"status": "PASS", "lean_version": "4.19.0", "proof_entry_count": PROOF_COUNT,
        "audit_sha256": PROOF_AUDIT_SHA,
        "sources": {PACKAGE + "/" + name: digest(package / name) for name in SOURCE_NAMES},
        "source_assumptions": "nonnegative-weight semiring laws, general relations and actual finite rational model; general rational/real instantiation paper-only"}
    exact(receipt["kernel"], expected_kernel, "kernel receipt drift")
    return artifacts

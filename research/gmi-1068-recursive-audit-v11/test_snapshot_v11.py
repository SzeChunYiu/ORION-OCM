"""Real-snapshot no-alarm and rehashed hostile adjudication mutations."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("checked_snapshot_v11", HERE / "check_snapshot_v11.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
COVERAGE = {}


def replace(value, path, replacement):
    for component in path[:-1]:
        value = value[component]
    value[path[-1]] = replacement


class SnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = json.loads((HERE / "SCOPE_SNAPSHOT_V11.json").read_text())
        cls.receipt = json.loads((checker.ROOT / checker.CONTRACT.PACKAGE / "RESULT_V11.json").read_text())
        cls.gate = checker.load("test_gate", checker.ROOT / "research/gmi-1068-recursive-audit-v3/gate.py")

    def rebind(self, snapshot):
        for name in self.gate.NODES:
            row = snapshot["rounds"][name]
            row["parent_bindings"] = {parent: snapshot["rounds"][parent]["evidence_digest"]
                                      for parent in self.gate.DAG[name]}
            row["evidence_digest"] = self.gate.evidence_digest(row)
        return snapshot

    def test_actual_snapshot_no_alarm(self):
        result = checker.evaluate()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["scientific_atoms_closed"], sorted(checker.CLOSING))
        self.assertEqual(result["remaining_atoms"], 211)
        self.assertEqual(result["earned_rounds"], ["R0"])
        COVERAGE["valid_snapshots"] = 1

    def test_snapshot_mutations(self):
        repair = lambda owner, field: ("rounds", owner, "local_repairs", -1, field)
        atom = lambda owner, index, field: ("rounds", owner, "obligations", index, field)
        wrong = checker.CONTRACT.witness(checker.ROOT, "TypedPathsV11.lean", "lean_declaration", "nil_append")
        mutations = [
            (repair("R14", "scope"), "Every AI architecture is derived without assumptions."),
            (repair("R15", "status"), "PENDING_REVIEW"),
            (repair("R1", "id"), "R1-unregistered"),
            (repair("R2", "evidence"), [wrong]),
            (atom("R2", 1, "evidence"), [wrong]),
            (atom("R1", 1, "title"), "a different original requirement"),
            (atom("R1", 2, "status"), "OPEN"),
            (atom("R2", 1, "disposition"), "all restricted classes lack a decoder"),
            (atom("R1", 1, "historical_status"), "CLOSED"),
            (atom("R1", 1, "id"), "GMI2-R1-099"),
            (atom("R3", 0, "status"), "CLOSED"),
            (atom("R3", 0, "disposition"), "changed unrelated requirement"),
            (("rounds", "R1", "scope"), "unregistered scope"),
            (("rounds", "R2", "status"), "STALE"),
            (("rounds", "R1", "local_repairs", 0, "scope"), "rewritten history"),
            (atom("R1", 2, "evidence"), []),
            (atom("R2", 1, "evidence"), [checker.CONTRACT.witness(
                checker.ROOT, "RESULT_V11.json", "json_pointer", "/coverage")]),
        ]
        count = 0
        for path, value in mutations:
            bad = deepcopy(self.snapshot)
            replace(bad, path, value)
            with self.subTest(path=path), self.assertRaises(ValueError):
                checker.evaluate(self.rebind(bad), self.receipt)
            count += 1
        extra = deepcopy(self.snapshot)
        extra["rounds"]["R1"]["local_repairs"].append({"id": "extra", "scope": "extra",
                                                       "status": "LOCAL_VERIFIED", "evidence": [wrong]})
        missing = deepcopy(self.snapshot)
        missing["rounds"]["R1"]["artifacts"] = [a for a in missing["rounds"]["R1"]["artifacts"]
                                                  if not a["path"].endswith("/ADJUDICATION_V11.md")]
        added = deepcopy(self.snapshot)
        path = HERE / "audit_contract_v11.py"
        added["rounds"]["R1"]["artifacts"].append({"path": str(path.relative_to(checker.ROOT)),
                                                    "sha256": checker.CONTRACT.digest(path)})
        for bad in (extra, missing, added):
            with self.assertRaises(ValueError):
                checker.evaluate(self.rebind(bad), self.receipt)
            count += 1
        self.assertEqual(count, 20)
        COVERAGE["snapshot_mutation_rejections"] = count

    def test_receipt_mutations(self):
        atom = "GMI2-R2-002"
        source = next(iter(self.receipt["kernel"]["sources"]))
        input_name = next(iter(self.receipt["inputs"]))
        context_source = next(iter(self.receipt["context"]["bindings"]))
        mutations = [
            (("atoms", atom, "title"), "different title"),
            (("atoms", atom, "status"), "PENDING_REVIEW"),
            (("atoms", atom, "scope"), "every restricted class lacks a decoder"),
            (("kernel", "status"), "FAIL"), (("kernel", "lean_version"), "4.18.0"),
            (("kernel", "proof_entry_count"), True), (("kernel", "proof_entry_count"), 14.0),
            (("kernel", "audit_sha256"), "0" * 64),
            (("kernel", "sources", source), "0" * 64),
            (("kernel", "source_assumptions"), "no assumptions"),
            (("inputs", input_name), "0" * 64),
            (("coverage", "test_paths_v11", "dag_graphs"), True),
            (("coverage", "test_paths_v11", "dag_graphs"), 729.0),
            (("context", "bindings", context_source), "0" * 64),
            (("context", "coverage", "full_process_comparisons"), True),
            (("context", "ranking_witness"), [[1, 0], [1, 0]]),
            (("context", "ranking_witness"), [[1.0, 0], [0, 1]]),
            (("context", "scope"), "universal independence"),
            (("context", "atom_id"), "GMI2-R2-003"),
            (("tests_run",), True), (("tests_run",), 12.0), (("tests_run",), 11),
            (("overall_closure",), "CLOSED"), (("scientific_truth_certified",), 0),
            (("claim_boundaries",), []), (("kernel",), []),
        ]
        invalid = []
        for path, value in mutations:
            bad = deepcopy(self.receipt)
            replace(bad, path, value)
            invalid.append(bad)
        for key in self.receipt:
            bad = deepcopy(self.receipt)
            del bad[key]
            invalid.append(bad)
        for path in ((), ("kernel",), ("context",), ("coverage", "test_paths_v11"), ("inputs",)):
            bad = deepcopy(self.receipt)
            cursor = bad
            for key in path:
                cursor = cursor[key]
            cursor["unexpected"] = "unexpected"
            invalid.append(bad)
        invalid.append({"atoms": deepcopy(self.receipt["atoms"]), "kernel": {"status": "PASS"}})
        count = 0
        for bad in invalid:
            with self.assertRaises((ValueError, TypeError)):
                checker.evaluate(self.snapshot, bad)
            count += 1
        self.assertEqual(count, 42)
        COVERAGE["receipt_mutation_rejections"] = count

    def test_coupled_scope_drift(self):
        snapshot, receipt = deepcopy(self.snapshot), deepcopy(self.receipt)
        claim = "Context is independent on every restricted model class."
        snapshot["rounds"]["R2"]["obligations"][1]["disposition"] = claim
        receipt["atoms"]["GMI2-R2-002"]["scope"] = claim
        with self.assertRaisesRegex(ValueError, "registered atom adjudication drift"):
            checker.evaluate(self.rebind(snapshot), receipt)
        COVERAGE["coupled_scope_rejections"] = 1


if __name__ == "__main__":
    program = unittest.main(exit=False, verbosity=2)
    print(json.dumps(COVERAGE, sort_keys=True))
    raise SystemExit(not program.result.wasSuccessful())

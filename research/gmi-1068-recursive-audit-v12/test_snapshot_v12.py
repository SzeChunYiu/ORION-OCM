"""Real-snapshot baseline and rehashed hostile sole-atom adjudications."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("checked_snapshot_v12", HERE / "check_snapshot_v12.py")
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
        cls.snapshot = json.loads((HERE / "SCOPE_SNAPSHOT_V12.json").read_text())
        cls.receipt = json.loads((checker.ROOT / checker.CONTRACT.PACKAGE / "RESULT_V12.json").read_text())
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
        self.assertEqual(result["new_scientific_atoms_closed"], ["GMI2-R2-006"])
        self.assertEqual(result["scientific_atoms_closed"],
                         ["GMI2-R1-002", "GMI2-R1-003", "GMI2-R2-002", "GMI2-R2-006"])
        self.assertEqual(result["remaining_atoms"], 210)
        self.assertEqual(result["earned_rounds"], ["R0"])
        COVERAGE["valid_snapshots"] = 1

    def test_snapshot_mutations(self):
        repair = lambda owner, field: ("rounds", owner, "local_repairs", -1, field)
        atom = lambda owner, index, field: ("rounds", owner, "obligations", index, field)
        wrong = checker.CONTRACT.witness(checker.ROOT, "FiniteSumsV12.lean", "lean_declaration", "sum_zero")
        mutations = [
            (repair("R14", "scope"), "Every AI architecture is derived without assumptions."),
            (repair("R15", "status"), "PENDING_REVIEW"),
            (repair("R2", "id"), "R2-unregistered"), (repair("R2", "evidence"), [wrong]),
            (atom("R2", 5, "evidence"), [wrong]),
            (atom("R2", 5, "title"), "a different original requirement"),
            (atom("R2", 5, "status"), "OPEN"),
            (atom("R2", 5, "disposition"), "all positive weights recover every Pareto point"),
            (atom("R2", 5, "historical_status"), "CLOSED"),
            (atom("R2", 5, "id"), "GMI2-R2-099"),
            (atom("R3", 0, "status"), "CLOSED"),
            (atom("R3", 0, "disposition"), "changed unrelated requirement"),
            (("rounds", "R2", "scope"), "unregistered scope"),
            (("rounds", "R2", "status"), "STALE"),
            (("rounds", "R2", "local_repairs", 0, "scope"), "rewritten history"),
            (atom("R2", 5, "evidence"), []),
            (atom("R2", 5, "evidence"), [checker.CONTRACT.witness(
                checker.ROOT, "RESULT_V12.json", "json_pointer", "/coverage")]),
            (atom("R1", 1, "status"), "OPEN"),
        ]
        count = 0
        for path, value in mutations:
            bad = deepcopy(self.snapshot)
            replace(bad, path, value)
            with self.subTest(path=path), self.assertRaises(ValueError):
                checker.evaluate(self.rebind(bad), self.receipt)
            count += 1
        extra = deepcopy(self.snapshot)
        extra["rounds"]["R2"]["local_repairs"].append({"id": "extra", "scope": "extra",
                                                       "status": "LOCAL_VERIFIED", "evidence": [wrong]})
        missing = deepcopy(self.snapshot)
        missing["rounds"]["R2"]["artifacts"] = [a for a in missing["rounds"]["R2"]["artifacts"]
                                                  if a["path"] != checker.CONTRACT.PACKAGE + "/FREEZE_V12.md"]
        added = deepcopy(self.snapshot)
        path = HERE / "audit_contract_v12.py"
        added["rounds"]["R2"]["artifacts"].append({"path": str(path.relative_to(checker.ROOT)),
                                                    "sha256": checker.CONTRACT.digest(path)})
        swapped = deepcopy(self.snapshot)
        source, target = swapped["rounds"]["R2"]["obligations"][5], swapped["rounds"]["R2"]["obligations"][2]
        source["status"] = "OPEN"
        target.update(status="CLOSED", disposition=source["disposition"], evidence=source["evidence"])
        extended = deepcopy(self.snapshot)
        extended["rounds"]["R2"]["obligations"][5]["unsupported_authority"] = "universal"
        for bad in (extra, missing, added, swapped, extended):
            with self.assertRaises(ValueError):
                checker.evaluate(self.rebind(bad), self.receipt)
            count += 1
        self.assertEqual(count, 23)
        COVERAGE["snapshot_mutation_rejections"] = count

    def test_receipt_mutations(self):
        atom = "GMI2-R2-006"
        source = next(iter(self.receipt["kernel"]["sources"]))
        input_name = next(iter(self.receipt["inputs"]))
        historical = next(iter(self.receipt["source_bindings"]))
        mutations = [
            (("atoms", atom, "title"), "different title"),
            (("atoms", atom, "status"), "PENDING_REVIEW"),
            (("atoms", atom, "scope"), "every scalar recovers the whole order"),
            (("kernel", "status"), "FAIL"), (("kernel", "lean_version"), "4.18.0"),
            (("kernel", "proof_entry_count"), True), (("kernel", "proof_entry_count"), 17.0),
            (("kernel", "audit_sha256"), "0" * 64), (("kernel", "sources", source), "0" * 64),
            (("kernel", "source_assumptions"), "real instance kernel checked"),
            (("inputs", input_name), "0" * 64),
            (("coverage", "test_scalarization_v12", "dimensions"), True),
            (("coverage", "test_scalarization_v12", "dimensions"), 5.0),
            (("source_bindings", historical), "0" * 64), (("source_bindings",), {}),
            (("tests_run",), True), (("tests_run",), 8.0), (("tests_run",), 7),
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
        for path in ((), ("kernel",), ("source_bindings",), ("coverage", "test_scalarization_v12"), ("inputs",)):
            bad = deepcopy(self.receipt)
            cursor = bad
            for key in path:
                cursor = cursor[key]
            cursor["unexpected"] = "unexpected"
            invalid.append(bad)
        for index in range(len(self.receipt["claim_boundaries"])):
            bad = deepcopy(self.receipt)
            bad["claim_boundaries"][index] = "unregistered universal promotion"
            invalid.append(bad)
        invalid.append({"atoms": deepcopy(self.receipt["atoms"]), "kernel": {"status": "PASS"}})
        count = 0
        for bad in invalid:
            with self.assertRaises((ValueError, TypeError)):
                checker.evaluate(self.snapshot, bad)
            count += 1
        self.assertEqual(count, 44)
        COVERAGE["receipt_mutation_rejections"] = count

    def test_coupled_scope_drift(self):
        snapshot, receipt = deepcopy(self.snapshot), deepcopy(self.receipt)
        claim = "A unique scalar derives all objectives and selects every Pareto point."
        snapshot["rounds"]["R2"]["obligations"][5]["disposition"] = claim
        receipt["atoms"]["GMI2-R2-006"]["scope"] = claim
        with self.assertRaisesRegex(ValueError, "registered atom adjudication drift"):
            checker.evaluate(self.rebind(snapshot), receipt)
        COVERAGE["coupled_scope_rejections"] = 1


if __name__ == "__main__":
    program = unittest.main(exit=False, verbosity=2)
    print(json.dumps(COVERAGE, sort_keys=True))
    raise SystemExit(not program.result.wasSuccessful())

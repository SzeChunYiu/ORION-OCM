"""Real-snapshot baseline and rehashed hostile sole-atom adjudications."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("checked_snapshot_v18", HERE / "check_snapshot_v18.py")
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
        cls.snapshot = json.loads((HERE / "SCOPE_SNAPSHOT_V18.json").read_text())
        cls.receipt = json.loads((checker.ROOT / checker.CONTRACT.PACKAGE / "RESULT_V18.json").read_text())
        cls.gate = checker.load("test_gate", checker.ROOT / "research/gmi-1068-recursive-audit-v3/gate.py")
    def rebind(self, snapshot):
        for name in self.gate.NODES:
            row = snapshot["rounds"][name]
            row["parent_bindings"] = {parent: snapshot["rounds"][parent]["evidence_digest"]
                                      for parent in self.gate.DAG[name]}
            row["evidence_digest"] = self.gate.evidence_digest(row)
        return snapshot
    def check(self, snapshot, receipt):
        accounting = checker.CONTRACT.current_accounting(snapshot, self.receipt["amendment_carry"])
        return checker.evaluate(snapshot, receipt, accounting)
    def test_actual_snapshot_no_alarm(self):
        result = checker.evaluate()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["new_scientific_atoms_closed"], ["GMI2-R2-008"])
        self.assertEqual(len(result["scientific_atoms_closed"]), 12)
        self.assertEqual((result["remaining_atoms"], result["original_fulfilled"],
                          result["qualified_replacements"], result["active_unresolved"]), (202,20,2,200))
        self.assertEqual(result["earned_rounds"], ["R0"])
        COVERAGE["valid_snapshots"] = 1
    def test_snapshot_mutations(self):
        repair = lambda owner, field: ("rounds", owner, "local_repairs", -1, field)
        atom = lambda owner, index, field: ("rounds", owner, "obligations", index, field)
        wrong = checker.CONTRACT.witness(checker.ROOT, "PrefixWrapperV18.lean", "lean_declaration", "wrapper_target")
        mutations = [
            (repair("R14", "scope"), "Every AI architecture is derived without assumptions."),
            (repair("R15", "status"), "PENDING_REVIEW"),
            (repair("R2", "id"), "R2-unregistered"), (repair("R2", "evidence"), [wrong]),
            (atom("R2", 7, "evidence"), [wrong]),
            (atom("R2", 7, "title"), "a different original requirement"),
            (atom("R2", 7, "status"), "OPEN"),
            (atom("R2", 7, "disposition"), "undefined histories carry a total context preorder"),
            (atom("R2", 7, "historical_status"), "CLOSED"),
            (atom("R2", 7, "id"), "GMI2-R2-099"),
            (atom("R3", 0, "status"), "CLOSED"),
            (atom("R3", 0, "disposition"), "changed unrelated requirement"),
            (("rounds", "R2", "scope"), "unregistered scope"),
            (("rounds", "R2", "status"), "STALE"),
            (("rounds", "R2", "local_repairs", 0, "scope"), "rewritten history"),
            (atom("R2", 7, "evidence"), []),
            (atom("R2", 7, "evidence"), [checker.CONTRACT.witness(
                checker.ROOT, "RESULT_V18.json", "json_pointer", "/coverage")]),
            (atom("R1", 1, "status"), "OPEN"),
            (atom("R1", 4, "status"), "OPEN"),
            (atom("R1", 9, "status"), "OPEN"),
        ]
        count = 0
        for path, value in mutations:
            bad = deepcopy(self.snapshot)
            replace(bad, path, value)
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.check(self.rebind(bad), self.receipt)
            count += 1
        extra = deepcopy(self.snapshot)
        extra["rounds"]["R2"]["local_repairs"].append({"id": "extra", "scope": "extra",
                                                       "status": "LOCAL_VERIFIED", "evidence": [wrong]})
        missing = deepcopy(self.snapshot)
        missing["rounds"]["R2"]["artifacts"] = [a for a in missing["rounds"]["R2"]["artifacts"]
                                                  if a["path"] != checker.CONTRACT.PACKAGE + "/FREEZE_V18.md"]
        added = deepcopy(self.snapshot)
        path = HERE / "audit_contract_v18.py"
        added["rounds"]["R2"]["artifacts"].append({"path": str(path.relative_to(checker.ROOT)),
                                                    "sha256": checker.CONTRACT.digest(path)})
        swapped = deepcopy(self.snapshot)
        source, target = swapped["rounds"]["R2"]["obligations"][7], swapped["rounds"]["R2"]["obligations"][2]
        source["status"] = "OPEN"
        target.update(status="CLOSED", disposition=source["disposition"], evidence=source["evidence"])
        extended = deepcopy(self.snapshot)
        extended["rounds"]["R2"]["obligations"][7]["unsupported_authority"] = "universal"
        for bad in (extra, missing, added, swapped, extended):
            with self.assertRaises(ValueError):
                self.check(self.rebind(bad), self.receipt)
            count += 1
        self.assertEqual(count, 25)
        COVERAGE["snapshot_mutation_rejections"] = count
    def test_receipt_mutations(self):
        atom = "GMI2-R2-008"
        source = next(iter(self.receipt["kernel"]["sources"]))
        input_name = next(iter(self.receipt["inputs"]))
        historical = next(iter(self.receipt["source_bindings"]))
        mutations = [
            (("atoms", atom, "title"), "different title"),
            (("atoms", atom, "status"), "PENDING_REVIEW"),
            (("atoms", atom, "scope"), "all permitted evaluator classes give opposite rankings"),
            (("kernel", "status"), "FAIL"), (("kernel", "lean_version"), "4.18.0"),
            (("kernel", "proof_entry_count"), True), (("kernel", "proof_entry_count"), float(checker.CONTRACT.PROOF_COUNT)),
            (("kernel", "audit_sha256"), "0" * 64), (("kernel", "sources", source), "0" * 64),
            (("kernel", "source_assumptions"), "no permitted-evaluator premises required"),
            (("inputs", input_name), "0" * 64),
            (("coverage", "test_prefix_v18", "finite_books"), True),
            (("coverage", "test_prefix_v18", "finite_books"), 15131.0),
            (("source_bindings", historical), "0" * 64),
            (("amendment_carry", "qualified_revision_ids"), []), (("source_bindings",), {}),
            (("inherited_receipts",), {}),
            (("amendment_carry", "ledger_sha256"), "0" * 64),
            (("amendment_carry", "scope"), "original requirements fulfilled"),
            (("amendment_carry", "governance_receipt_sha256"), "0" * 64),
            (("tests_run",), True), (("tests_run",), 16.0), (("tests_run",), 15),
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
        for path in ((), ("kernel",), ("source_bindings",), ("coverage", "test_prefix_v18"), ("inputs",)):
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
                self.check(self.snapshot, bad)
            count += 1
        self.assertEqual(count, 57)
        COVERAGE["receipt_mutation_rejections"] = count
    def test_coupled_scope_drift(self):
        rejected = 0
        for index in (7,):
            snapshot, receipt = deepcopy(self.snapshot), deepcopy(self.receipt)
            atom = snapshot["rounds"]["R2"]["obligations"][index]
            claim = "All contexts, admissibility recovery and universal values are now kernel proved."
            atom["disposition"] = claim
            receipt["atoms"][atom["id"]]["scope"] = claim
            with self.assertRaisesRegex(ValueError, "registered atom adjudication drift"):
                self.check(self.rebind(snapshot), receipt)
            rejected += 1
        self.assertEqual(rejected, 1)
        COVERAGE["coupled_scope_rejections"] = rejected
    def test_current_accounting_mutations(self):
        baseline = checker.CONTRACT.current_accounting(self.snapshot, self.receipt["amendment_carry"])
        mutations = []
        for key in baseline:
            bad = deepcopy(baseline)
            del bad[key]
            mutations.append(bad)
        for path, value in [(("original_fulfilled",), 19), (("original_unresolved",), 203),
                (("active_unresolved",), 201), (("qualified_replacements",), 0),
                (("original_total",), 222.0), (("original_fulfilled",), True),
                (("qualified_original_ids",), []), (("snapshot_content_sha256",), "0" * 64),
                (("amendment_carry", "ledger_sha256"), "0" * 64),
                (("scientific_truth_certified",), 0), (("overall_closure",), "CLOSED")]:
            bad = deepcopy(baseline)
            replace(bad, path, value)
            mutations.append(bad)
        bad = deepcopy(baseline)
        bad["unsupported"] = True
        mutations.append(bad)
        for bad in mutations:
            with self.assertRaises(ValueError):
                checker.evaluate(self.snapshot, self.receipt, bad)
        self.assertEqual(len(mutations), 23)
        COVERAGE["accounting_mutation_rejections"] = len(mutations)

if __name__ == "__main__":
    program = unittest.main(exit=False, verbosity=2)
    print(json.dumps(COVERAGE, sort_keys=True))
    raise SystemExit(not program.result.wasSuccessful())

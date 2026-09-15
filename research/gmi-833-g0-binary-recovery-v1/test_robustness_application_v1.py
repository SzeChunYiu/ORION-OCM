import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from g0_binary_recovery_v1 import delay1_target, identity_target
from robustness_application_v1 import (
    build_record,
    finite_certificate,
    load_robustness_module,
    resource_branch_and_bound,
    semantic_encoding,
)


class BinaryRecoveryRobustnessTests(unittest.TestCase):
    def test_semantic_encodings_are_bijective_and_cross_match(self):
        nand, nrev = semantic_encoding("NAND")
        nor, rrev = semantic_encoding("NOR")
        self.assertEqual(len(nand), 260)
        self.assertEqual(len(nor), 260)
        self.assertEqual(set(nand.values()), set(nor.values()))
        self.assertEqual(len(nrev), 260)
        self.assertEqual(len(rrev), 260)

    def test_resource_branch_and_bound_agrees_and_prunes(self):
        delay, evaluated, pruned = resource_branch_and_bound("NAND", delay1_target)
        self.assertEqual(len(delay), 1)
        self.assertEqual((evaluated, pruned), (8, 252))
        identity, evaluated, pruned = resource_branch_and_bound("NAND", identity_target)
        self.assertEqual(len(identity), 1)
        self.assertEqual((evaluated, pruned), (1, 259))

    def test_parent_control_audit_delay(self):
        rob = load_robustness_module()
        audit, counts = build_record(rob, "NAND", "DELAY1", delay1_target)
        self.assertEqual(audit["control_requirements_terminal"], "CONTROL_REQUIREMENTS_SATISFIED")
        self.assertEqual(audit["terminal"], "ROBUST_AT_REGISTERED_CONTROLS")
        self.assertEqual(audit["subaudits"]["grammar"]["terminal"], "GRAMMAR_TWIN_MATCHED")
        self.assertEqual(audit["subaudits"]["encoding"]["terminal"], "ENCODING_INVARIANT_AT_REGISTERED_REMINTS")
        self.assertEqual(audit["subaudits"]["search"]["terminal"], "SEARCH_INVARIANT_AT_REGISTERED_ALGORITHMS")
        self.assertEqual(audit["subaudits"]["scalarization"]["terminal"], "SCALARIZATION_INVARIANT_AT_REGISTERED_WEIGHTS")
        self.assertEqual(counts["branch_and_bound_evaluated"], 8)

    def test_parent_control_audit_identity(self):
        rob = load_robustness_module()
        audit, counts = build_record(rob, "NOR", "IDENTITY", identity_target)
        self.assertEqual(audit["terminal"], "ROBUST_AT_REGISTERED_CONTROLS")
        self.assertEqual(counts["exact_solution_count"], 29)
        self.assertEqual(counts["branch_and_bound_evaluated"], 1)
        self.assertEqual(counts["branch_and_bound_pruned"], 259)

    def test_receipt_green(self):
        rob = load_robustness_module()
        r = finite_certificate()
        self.assertEqual(r["parent_control_claim"], rob.CLAIM_CEILING)
        self.assertEqual(r["verdict"], "GREEN")
        self.assertTrue(all(r["checks"].values()))
        self.assertEqual(set(r["audits"]), {"DELAY1_NAND", "DELAY1_NOR", "IDENTITY_NAND", "IDENTITY_NOR"})
        json.dumps(rob.canon(r), sort_keys=True, separators=(",", ":"))


if __name__ == "__main__":
    unittest.main()

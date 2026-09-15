from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from axiom_core_v1 import AXIOM_IDS, evaluate_axioms, response_partition, validate_all, validate_model


HERE = Path(__file__).resolve().parent


class AxiomCoreTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((HERE / "AXIOMS_V1.json").read_text(encoding="utf-8"))
        self.model = self.data["finite_model"]

    def test_exact_receipt(self):
        result = validate_all()
        self.assertEqual(result["axioms_satisfied"], 10)
        self.assertEqual(result["derived_constructs"], 10)
        self.assertEqual(result["imported_green_packages"], 4)
        self.assertEqual(result["verdict"], "GREEN")

    def test_every_named_axiom_has_a_true_witness_predicate(self):
        checks = evaluate_axioms(self.model)
        self.assertEqual(set(checks), AXIOM_IDS)
        self.assertTrue(all(checks.values()))

    def test_response_quotient_is_nontrivial(self):
        self.assertEqual(response_partition(self.model), (("s0",), ("s1",)))

    def test_missing_transition_fails_closed(self):
        mutant = copy.deepcopy(self.model)
        mutant["transition"] = mutant["transition"][:-1]
        with self.assertRaisesRegex(ValueError, "AX3_TOTAL_REGISTERED_PROCESS"):
            validate_model(mutant)

    def test_negative_resource_fails_closed(self):
        mutant = copy.deepcopy(self.model)
        mutant["resources"][0] = -1
        with self.assertRaises(ValueError):
            validate_model(mutant)

    def test_kind_conflation_and_scope_omission_fail_closed(self):
        kind_mutant = copy.deepcopy(self.model)
        kind_mutant["uncertainty_kind"] = "OVERLOADED_SCALAR"
        self.assertFalse(evaluate_axioms(kind_mutant)["AX8_UNCERTAINTY"])
        scope_mutant = copy.deepcopy(self.model)
        scope_mutant["theorem_scopes"]["FINITE_MODEL_CHECK"] = ""
        self.assertFalse(evaluate_axioms(scope_mutant)["AX10_SCOPE_TAGS"])


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3

from __future__ import annotations

import inspect
import json
from pathlib import Path
import unittest

from neutral_three_law_v1 import (
    CLAIM_CEILING,
    COST_CAP,
    FROZEN_PROTOCOL,
    POINTS,
    Protocol,
    ProtocolError,
    VARIABLES,
    activate_protocol,
    build_receipt,
    dependency_signature,
    enumerate_semantic_quotient,
    equivalent_syntax_control,
    frozen_target_tables,
    no_half_ablation,
    perturbed_target_control,
    recover_opaque_targets,
    required_variable_ablations,
)

ROOT = Path(__file__).resolve().parent
RESULT_PATH = ROOT / "RESULT_V1.json"


class NeutralThreeLawTests(unittest.TestCase):
    def test_frozen_protocol_accepts_itself_and_rejects_mutation(self) -> None:
        fingerprint = activate_protocol()
        self.assertEqual(len(fingerprint), 64)
        mutated = Protocol(
            variables=FROZEN_PROTOCOL.variables,
            constants=FROZEN_PROTOCOL.constants,
            operators=FROZEN_PROTOCOL.operators,
            cost_cap=7,
            tie_rule=FROZEN_PROTOCOL.tie_rule,
        )
        with self.assertRaisesRegex(ProtocolError, "FROZEN_PROTOCOL_MUTATION"):
            activate_protocol(mutated)

    def test_universe_and_exact_quotient_census(self) -> None:
        self.assertEqual(len(POINTS), 81)
        quotient, layers = enumerate_semantic_quotient(FROZEN_PROTOCOL)
        self.assertEqual([len(layers[c]) for c in range(1, COST_CAP + 1)], [7, 6, 60, 128, 650, 1834])
        self.assertEqual(len(quotient), 2685)

    def test_neutral_minimum_cost_recovery(self) -> None:
        targets = frozen_target_tables()
        recovered = recover_opaque_targets(targets)
        self.assertEqual({key: recovered[key].cost for key in sorted(recovered)}, {
            "OPAQUE_A": 4,
            "OPAQUE_B": 6,
            "OPAQUE_C": 6,
        })
        for key in targets:
            self.assertEqual(recovered[key].table, targets[key])

    def test_searcher_does_not_branch_on_frozen_target_ids(self) -> None:
        source = inspect.getsource(recover_opaque_targets)
        self.assertNotIn("OPAQUE_A", source)
        self.assertNotIn("OPAQUE_B", source)
        self.assertNotIn("OPAQUE_C", source)
        targets = frozen_target_tables()
        reminted = {
            "T-93": targets["OPAQUE_C"],
            "T-17": targets["OPAQUE_A"],
            "T-51": targets["OPAQUE_B"],
        }
        recovered = recover_opaque_targets(reminted)
        self.assertEqual(recovered["T-17"].cost, 4)
        self.assertEqual(recovered["T-51"].cost, 6)
        self.assertEqual(recovered["T-93"].cost, 6)

    def test_dependency_signatures_are_exact_and_distinct(self) -> None:
        targets = frozen_target_tables()
        expected = {
            "OPAQUE_A": ("w", "y"),
            "OPAQUE_B": ("w", "x", "y"),
            "OPAQUE_C": ("w", "x", "r"),
        }
        actual = {}
        for key, table in targets.items():
            signature, detail = dependency_signature(table)
            actual[key] = signature
            self.assertEqual(signature, expected[key])
            for variable in VARIABLES:
                if variable in signature:
                    self.assertTrue(detail[variable]["required"])
                    witness = detail[variable]["witness"]
                    self.assertIsNotNone(witness)
                    left = witness["left"]
                    right = witness["right"]
                    differing = [i for i, (a, b) in enumerate(zip(left, right)) if a != b]
                    self.assertEqual(differing, [VARIABLES.index(variable)])
                    self.assertNotEqual(witness["left_output"], witness["right_output"])
                else:
                    self.assertFalse(detail[variable]["required"])
                    self.assertTrue(detail[variable]["all_matched_pairs_invariant"])
        self.assertEqual(len(set(actual.values())), 3)

    def test_required_variable_ablations_all_fail(self) -> None:
        ablations = required_variable_ablations()
        expected_signatures = {
            "OPAQUE_A": {"w", "y"},
            "OPAQUE_B": {"w", "x", "y"},
            "OPAQUE_C": {"w", "x", "r"},
        }
        for target, variables in expected_signatures.items():
            self.assertEqual(set(ablations[target]), variables)
            for variable in variables:
                self.assertFalse(ablations[target][variable]["recovered"])
                self.assertEqual(ablations[target][variable]["quotient_size"], 1390)

    def test_no_half_ablation_is_structurally_impossible(self) -> None:
        control = no_half_ablation()
        self.assertTrue(control["all_quotient_values_integral"])
        self.assertEqual(control["quotient_size"], 505)
        self.assertEqual(control["layer_sizes"], [7, 0, 54, 0, 444, 0])
        self.assertTrue(all(control["each_target_has_half_integer"].values()))
        self.assertFalse(any(control["target_recovered"].values()))

    def test_equivalent_syntax_collapses_extensionally(self) -> None:
        control = equivalent_syntax_control()
        self.assertTrue(control["add_w_y_equals_add_y_w"])
        self.assertTrue(control["semantic_table_present_once"])
        self.assertEqual(control["canonical_representative"], "add(w,y)")

    def test_perturbed_target_does_not_retrofit_previous_winner(self) -> None:
        recovered = recover_opaque_targets(frozen_target_tables())
        control = perturbed_target_control(recovered)
        self.assertEqual(control["row_index"], 0)
        self.assertFalse(control["previous_representative_still_exact"])
        self.assertNotEqual(control["original_output"], control["perturbed_output"])

    def test_receipt_headlines(self) -> None:
        receipt = build_receipt()
        self.assertEqual(receipt["terminal"], CLAIM_CEILING)
        self.assertEqual(receipt["quotient_size"], 2685)
        self.assertEqual(receipt["layer_sizes"], [7, 6, 60, 128, 650, 1834])
        self.assertTrue(receipt["signatures_pairwise_distinct"])
        self.assertTrue(receipt["required_variable_ablations_all_fail"])
        self.assertFalse(receipt["perturbed_target_control"]["previous_representative_still_exact"])

    def test_committed_receipt_is_exactly_reproducible(self) -> None:
        committed = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(build_receipt(), committed)

    def test_receipt_contains_no_float_values(self) -> None:
        def walk(value):
            if isinstance(value, dict):
                for child in value.values():
                    yield from walk(child)
            elif isinstance(value, list):
                for child in value:
                    yield from walk(child)
            else:
                yield value

        for value in walk(build_receipt()):
            self.assertNotIsInstance(value, float)


if __name__ == "__main__":
    unittest.main()

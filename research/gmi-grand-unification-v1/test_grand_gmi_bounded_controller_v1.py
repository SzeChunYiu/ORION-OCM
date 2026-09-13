import math
import unittest
from dataclasses import replace
from grand_gmi_bounded_controller_model_v1 import (
    Model, controllers, decode_controller, decode_model, encode_controller,
    encode_model, evaluate, search, validate,
)
from grand_gmi_bounded_controller_checks_v1 import (
    blind_chain, canonical_chain_controller, census, graph_winning, run,
)


class BoundedControllerTests(unittest.TestCase):
    def test_complete_small_universe_against_independent_graph_oracle(self):
        result = census()
        self.assertEqual(result["models"], 108)
        self.assertEqual(result["model_controller_pairs"], 1188)
        self.assertGreater(result["successful_pairs"], 0)
        self.assertGreater(result["failed_pairs"], 0)

    def test_blind_chain_negative_then_memory_revival(self):
        model = blind_chain()
        self.assertEqual(search(model, 2)["candidates"], 11)
        self.assertFalse(search(model, 2)["winners"])
        result = search(model, 3)
        self.assertEqual(result["candidates"], 75)
        self.assertTrue(result["winners"])
        self.assertEqual({p for _, p in result["winners"]}, {(2, 9, 12, 2, 5)})
        for controller, _ in result["winners"]:
            self.assertTrue(graph_winning(model, controller))

    def test_blind_chain_length_family(self):
        for length in (1, 2, 3):
            model = blind_chain(length)
            self.assertFalse(search(model, length)["winners"])
            witness = canonical_chain_controller(length)
            self.assertTrue(evaluate(model, witness)["success"])
            self.assertTrue(graph_winning(model, witness))

    def test_actual_serialized_witness_bytes(self):
        model, controller = blind_chain(), canonical_chain_controller()
        self.assertEqual(encode_model(model), "101100001001")
        self.assertEqual(encode_controller(model, controller), "101110000")
        self.assertEqual(decode_model("101100001001", 3, 1, 1, 1), model)
        self.assertEqual(decode_controller("101110000", model, 3), controller)
        self.assertEqual(evaluate(model, controller)["product_pair_inspections"], 3)
        self.assertEqual(evaluate(model, controller)["physical_transition_lookups"], 2)

    def test_each_coordinate_is_enforced_on_whole_controller(self):
        profile = (2, 9, 12, 2, 5)
        self.assertTrue(search(blind_chain(), 3, profile)["winners"])
        for coordinate in range(5):
            ceilings = list(profile)
            ceilings[coordinate] -= 1
            self.assertFalse(search(blind_chain(), 3, tuple(ceilings))["winners"])

    def test_feedback_revives_repeated_controller_node(self):
        model = blind_chain(feedback=True)
        controller = ((1, (0, 1)), (0, ()))
        result = evaluate(model, controller)
        self.assertTrue(result["success"])
        self.assertEqual(result["runs"], (("SUCCESS", 2),))
        self.assertEqual(result["profile"], (1, 6, 15, 2, 5))
        self.assertTrue(graph_winning(model, controller))
        self.assertFalse(search(model, 1)["winners"])
        self.assertTrue(search(model, 2)["winners"])

    def test_shared_row_cannot_access_hidden_initial_state(self):
        model = Model((((1, 0),), (None,)), (0, 1), (0, 1))
        self.assertFalse(search(model, 3)["winners"])
        for state in model.initial:
            self.assertTrue(search(replace(model, initial=(state,)), 2)["winners"])

    def test_distinct_actual_failure_modes(self):
        self.assertEqual(evaluate(blind_chain(), ((0, ()),))["runs"], (("WRONG_TERMINAL", 0),))
        self.assertEqual(evaluate(replace(blind_chain(), initial=(2,)), ((1, (0,)),))["runs"],
                         (("ILLEGAL", 0),))
        loop = Model((((0, 0),),), (0,), (0,))
        self.assertEqual(evaluate(loop, ((1, (0,)),))["runs"], (("LOOP", 1),))
        self.assertFalse(graph_winning(loop, ((1, (0,)),)))

    def test_zero_control_goal_and_empty_success_relation(self):
        model = Model(((),), (1,), (0,))
        self.assertEqual(search(model, 1)["winners"], [(((0, ()),), (0, 0, 2, 0, 1))])
        self.assertEqual(decode_controller("", model, 1), ((0, ()),))
        self.assertFalse(search(replace(blind_chain(), goals=(0, 0, 0)), 3)["winners"])

    def test_invalid_models_and_bounds_are_not_false_green(self):
        for initial in ((), (0, 0), (3,), (True,)):
            with self.assertRaises(ValueError):
                validate(replace(blind_chain(), initial=initial))
        for bound in (0, -1, True, math.inf, math.nan):
            with self.assertRaises(ValueError):
                search(blind_chain(), bound)
        for bad in (math.inf, math.nan, -1, True, 1.5):
            with self.assertRaises(ValueError):
                search(blind_chain(), 3, (bad, 9, 12, 2, 5))

    def test_malformed_code_and_model_representations(self):
        for payload in ("111110000", "101110001", "10111000", "10111000x"):
            with self.assertRaises(ValueError):
                decode_controller(payload, blind_chain(), 3)
        with self.assertRaises(ValueError):
            decode_model("111110000001001", 3, 1, 1, 2)
        with self.assertRaises(ValueError):
            evaluate(blind_chain(), ((2, (0,)),))

    def test_receipt_executes_full_declared_register(self):
        result = run()
        self.assertTrue(result["all_checks_green"])
        self.assertEqual(result["final_retained_action_bits"], 0)
        self.assertEqual(result["blind_bound_3"]["candidates"], 75)
        self.assertEqual(result["census"]["model_controller_pairs"], 1188)


if __name__ == "__main__":
    unittest.main()

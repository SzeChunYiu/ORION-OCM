import json
from pathlib import Path
import tempfile
import unittest

from joint_relation_checks_v1 import run
from joint_relation_model_v1 import (Relation, cover_protocol, fixed_bits, from_preimages,
                                     incidence_bound, joint_relation, minimum_cover, verify_protocol)
from joint_relation_oracle_v1 import (joint_selector_optimum, selector_optimum,
                                      verify_pair_protocol)
from joint_relation_witnesses_v1 import c5, c5_relation, triangle
from replay_v1 import verify_manifest

HERE = Path(__file__).resolve().parent


class JointRelationTests(unittest.TestCase):
    def test_complete_receipt_and_independent_selector_census(self):
        actual = run()
        expected = json.loads((HERE/"JOINT_RELATIONAL_COMPOSITION_RECEIPT_V1.json").read_text())
        self.assertEqual(actual, expected)
        self.assertEqual(actual["local"]["relations"], 343)
        self.assertEqual(actual["local"]["adequate_selectors"], 1728)
        self.assertEqual(actual["joint"]["relation_pairs"], 1521)
        self.assertEqual(actual["joint"]["adequate_joint_selectors"], 1045984)
        self.assertEqual(actual["joint"]["executed_pairs"], 10404)
        self.assertEqual(actual["exact_functions"]["function_pairs"], 729)

    def test_triangle_refutes_pairgraph_and_unrestricted_multiplicativity(self):
        result = triangle()
        self.assertEqual(result["shared_width"], 3)
        self.assertLess(result["shared_width"], result["product_width"])
        self.assertGreater(result["local_width"], result["pairgraph_incorrect_width"])
        self.assertEqual(result["independent_selectors"], 262144)
        self.assertEqual(result["shared_bits"], result["product_bits"])

    def test_c5_constructs_all_25_inputs_and_beats_packed_parent(self):
        result = c5()
        self.assertEqual(len(result["executions"]), 25)
        self.assertEqual(result["shared_width"], 8)
        self.assertEqual(result["product_parent"]["width"], 9)
        self.assertEqual(result["product_parent"]["local_selector_pairs"], 1024)
        self.assertEqual((result["shared_bits"], result["product_bits"]), (3, 4))
        self.assertEqual(sum(result["actual_row_incidences"]), 16)

    def test_area_bound_does_not_prove_seven_feasible(self):
        relation = c5_relation()
        local = selector_optimum(relation.rows)["width"]
        bounds = incidence_bound(relation, relation, local, local)
        self.assertEqual(bounds["area"], 7)
        self.assertEqual((bounds["row"], bounds["column"]), (8, 8))
        self.assertGreater(5*local, 7*bounds["max_first_preimage"])

    def test_shared_constant_action_needs_no_fixed_bit(self):
        r = Relation(((0, 1), (0, 2), (0,)), 3)
        result, _ = minimum_cover(joint_relation(r, r))
        self.assertEqual(result["used_symbols"], 1)
        self.assertEqual(fixed_bits(1), 0)

    def test_unused_action_and_duplicate_preimage_are_harmless(self):
        r = Relation(((0, 2), (1,)), 4)
        actual, _ = minimum_cover(r)
        self.assertEqual(actual["used_symbols"], 2)
        self.assertEqual(actual["used_symbols"], selector_optimum(r.rows)["width"])

    def test_exact_functions_still_multiply(self):
        left, right = Relation(((0,), (1,), (0,)), 2), Relation(((0,), (1,), (2,)), 3)
        result, _ = minimum_cover(joint_relation(left, right))
        self.assertEqual(result["used_symbols"], 6)

    def test_unbalanced_joint_inputs_keep_both_constraints(self):
        left, right = Relation(((0, 1),), 2), c5_relation()
        actual, _ = minimum_cover(joint_relation(left, right))
        self.assertEqual(actual["used_symbols"], joint_selector_optimum(left.rows, right.rows)["width"])
        self.assertEqual(actual["used_symbols"], 3)

    def test_fixed_bits_pack_joint_alphabet_without_parent_padding(self):
        self.assertEqual(fixed_bits(15), 4)
        self.assertEqual(fixed_bits(3)+fixed_bits(5), 5)
        self.assertEqual(fixed_bits(8), 3)
        self.assertEqual(fixed_bits(9), 4)

    def test_missing_input_rejected(self):
        r = Relation(((0,), (1,)), 2)
        with self.assertRaises(ValueError):
            verify_protocol(r, (0,), (0, 1))
        with self.assertRaises(ValueError):
            verify_pair_protocol(r.rows, r.rows, (0, 0, 0), ((0, 0),))

    def test_altered_decoder_rejected(self):
        r = Relation(((0,), (1,)), 2)
        good = cover_protocol(r, (0, 1))
        self.assertEqual(good["outputs"], (0, 1))
        with self.assertRaises(ValueError):
            verify_protocol(r, good["encoder"], (0, 0))

    def test_uncovered_product_rectangle_rejected(self):
        r = c5_relation()
        joint = joint_relation(r, r)
        with self.assertRaises(ValueError):
            cover_protocol(joint, (0, 1, 5, 6, 12, 13, 17))

    def test_bad_message_and_action_labels_rejected(self):
        r = Relation(((0,),), 1)
        for encoder, decoder in (((True,), (0,)), ((1,), (0,)), ((0,), (True,)), ((0,), (1,))):
            with self.assertRaises(ValueError):
                verify_protocol(r, encoder, decoder)

    def test_empty_or_malformed_relation_rejected(self):
        for rows, actions in (((), 1), (((),), 1), (((0,),), 0), (((True,),), 2), (((2,),), 2)):
            with self.assertRaises(ValueError):
                Relation(rows, actions)
        with self.assertRaises(ValueError):
            from_preimages(((0,),), 2)

    def test_source_manifest_no_alarm_and_meaningful_mismatch(self):
        manifest = json.loads((HERE/"MANIFEST.json").read_text())
        self.assertEqual(verify_manifest(), len(manifest["files"]))
        with tempfile.TemporaryDirectory() as location:
            target = Path(location)
            name = "joint_relation_model_v1.py"
            binding = dict(schema=manifest["schema"], files={name: manifest["files"][name]})
            (target/"MANIFEST.json").write_text(json.dumps(binding))
            (target/name).write_bytes((HERE/name).read_bytes())
            self.assertEqual(verify_manifest(target), 1)
            (target/name).write_bytes((HERE/name).read_bytes()+b"# mutation\n")
            with self.assertRaises(ValueError):
                verify_manifest(target)


if __name__ == "__main__":
    unittest.main()

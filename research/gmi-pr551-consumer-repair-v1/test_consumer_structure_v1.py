import copy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from consumer_structure_v1 import inspect
from source_contract_v1 import current_contract
from contract_v1 import AuditError


def graph():
    return {"nodes": {"d": ["DENSE", {"width": 1}], "x": ["INPUT", {"width": 1}],
            "y": ["TARGET", {}], "p": ["LINEAR", {}], "g": ["GRAD", {"lr": 1}],
            "o": ["OUTPUT", {}]},
            "edges": [["d", "p", 0], ["x", "p", 1], ["d", "g", 0],
                      ["p", "g", 1], ["y", "g", 2], ["p", "o", 0]], "meta": {}}


class StructureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kinds, cls.roles = current_contract()

    def inspect(self, g):
        return inspect("control", json.dumps(g), self.kinds, self.roles)

    def test_zero_outgoing_grad_keeps_parameter_update_route(self):
        row = self.inspect(graph())
        self.assertEqual(len(row["numeric_parameter_routes"]), 1)
        self.assertEqual(len(row["feedback_parameter_routes"]), 1)
        update = row["feedback_updates"][0]
        self.assertEqual(update["outgoing_edges"], [])
        self.assertEqual(update["identity_parameter_sources"], ["d"])
        self.assertFalse(update["outgoing_edge_required_for_cell_write"])
        self.assertEqual(row["nonzero_parameter_write"], "UNVERIFIED")

    def test_swapped_parameter_data_ports_do_not_count_read(self):
        g = graph()
        g["edges"][:2] = [["d", "p", 1], ["x", "p", 0]]
        row = self.inspect(g)
        self.assertEqual(row["numeric_parameter_routes"], [])
        self.assertTrue(any(r["role"] == "data" for r in row["native_role_adjacency"]))

    def test_affine_parameter_and_data_are_distinct(self):
        g = graph(); g["nodes"]["a"] = ["AFFINE", {"width": 1}]
        g["edges"] += [["d", "a", 0], ["x", "a", 1]]
        self.assertEqual(len(self.inspect(g)["numeric_parameter_routes"]), 2)
        g["edges"][-2:] = [["d", "a", 1], ["x", "a", 0]]
        self.assertEqual(len(self.inspect(g)["numeric_parameter_routes"]), 1)

    def test_identity_chain_retains_names(self):
        g = graph(); g["nodes"]["e"] = ["EDGE", {}]
        g["edges"][0] = ["e", "p", 0]; g["edges"].append(["d", "e", 0])
        self.assertEqual(self.inspect(g)["numeric_parameter_routes"][0]["path"], ["d", "e", "p"])

    def test_nonidentity_routes_are_uninspected_not_absent(self):
        g = graph(); g["nodes"]["n"] = ["NONLIN", {"fn": 2}]
        g["edges"][0] = ["n", "p", 0]; g["edges"].append(["d", "n", 0])
        row = self.inspect(g)
        self.assertEqual(row["numeric_parameter_routes"], [])
        self.assertEqual(row["other_route_semantics"], "UNINSPECTED")
        self.assertEqual(row["nonidentity_routes"][0]["kind"], "NONLIN")

    def test_grad_output_edge_does_not_certify_an_update(self):
        g = graph(); g["nodes"]["e"] = ["EDGE", {}]; g["edges"].append(["g", "e", 0])
        update = self.inspect(g)["feedback_updates"][0]
        self.assertEqual(update["runtime_result"], "NONE")
        self.assertEqual(len(update["outgoing_edges"]), 1)
        self.assertTrue(update["write_effect"].startswith("UNVERIFIED"))

    def test_missing_target_stays_eligible_but_not_verified(self):
        g = graph(); g["edges"].remove(["y", "g", 2])
        update = self.inspect(g)["feedback_updates"][0]
        self.assertEqual(update["missing_input_ports"], [2])
        self.assertEqual(update["query_schedule"], "SKIPPED")

    def test_zero_width_and_zero_rate_never_promote(self):
        g = graph(); g["nodes"]["d"][1]["width"] = 0; g["nodes"]["g"][1]["lr"] = 0
        self.assertEqual(self.inspect(g)["nonzero_parameter_write"], "UNVERIFIED")

    def test_no_dense_is_inspected_not_missing(self):
        g = graph(); del g["nodes"]["d"]
        g["edges"] = [e for e in g["edges"] if e[0] != "d"]
        row = self.inspect(g)
        self.assertEqual(row["status"], "STRUCTURE_INSPECTED")
        self.assertEqual(row["dense_nodes"], [])

    def test_unknown_kind_refused(self):
        g = graph(); g["nodes"]["p"][0] = "DOT"
        with self.assertRaises(AuditError): self.inspect(g)

    def test_negative_boolean_duplicate_and_wrong_type_ports_refused(self):
        for edge in (["d", "p", -1], ["d", "p", False], ["d", "o", 0], ["d", "p", 0]):
            with self.subTest(edge=edge):
                g = graph(); g["edges"].append(edge)
                with self.assertRaises(AuditError): self.inspect(g)

    def test_cyclic_routing_refused(self):
        g = graph(); g["nodes"]["e"] = ["EDGE", {}]; g["edges"].append(["e", "e", 0])
        with self.assertRaises(AuditError): self.inspect(g)


if __name__ == "__main__":
    unittest.main()

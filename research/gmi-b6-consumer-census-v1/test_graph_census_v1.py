"""Real-data no-alarm plus primitive/port/ancestry falsifying controls."""
import ast
import copy
import json
import unittest
from census_v1 import run
from contract_v1 import AuditError, strict_json
from inputs_v1 import load_inputs
from native_roles_v1 import native_contract
from graph_census_v1 import describe
from oracle_v1 import compare


class GraphCensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.binding, cls.files = load_inputs()
        cls.kinds, cls.roles = native_contract(cls.files)
        cls.result = run()

    def graph(self, consumer="LINEAR", port=0, edge=False, served=True):
        nodes = {"x": ["INPUT", {"width": 1}], "d": ["DENSE", {"width": 4}],
                 "o": ["OUTPUT", {}], "k": ["CONST", {"value": 0}],
                 "n": [consumer, {"width": 1} if consumer == "AFFINE" else {}]}
        edges = [["d", "n", port], ["x", "n", 1 - port], ["n" if served else "k", "o", 0]]
        if consumer == "AFFINE": edges[-1] = ["k", "o", 0]
        if edge:
            nodes["e"] = ["EDGE", {}]; edges[0] = ["e", "n", port]; edges.append(["d", "e", 0])
        return {"nodes": nodes, "edges": edges, "meta": {}}

    def inspect(self, graph):
        text = json.dumps(graph)
        result = describe("synthetic", text, self.kinds, self.roles)
        compare({"text": text}, result, self.roles)
        return result

    def test_real_packet_no_alarm_and_exact_cohorts(self):
        r = self.result
        self.assertEqual((r["all_arm_summary"]["rows"], r["all_arm_summary"]["distinct_serialized_graphs"]), (70, 63))
        self.assertEqual((r["legacy_scan_summary"]["rows"], r["legacy_scan_summary"]["distinct_serialized_graphs"]), (17, 15))
        self.assertEqual(r["independent_oracle_row_comparisons"], 437)
        self.assertEqual(r["recorded_arm_archive_cells_including_duplicate_arm"], 800)

    def test_actual_affine_omission_breaks_original_scanner(self):
        tree = ast.parse(self.files["native/b6_dense_consumer_scan.py"])
        allowed = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "probe"
                   or isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)
                   and n.targets[0].id in ("NUMERIC", "GRADS")]
        env = {}; exec(compile(ast.Module(body=allowed, type_ignores=[]), "<pinned-pure-probe>", "exec"), env)
        raw = strict_json(self.files["pr551/STAGE_B6_DEV_CROSS_TWIN_S0_billy.json"])
        graph = strict_json(raw["final_best_genotypes"]["DENSE"]["genotype"])
        self.assertFalse(env["probe"](graph)["numeric_consumer"])
        self.assertTrue(any(e["kind"] == "AFFINE" and e["role"] == "parameter"
                            for e in self.inspect(graph)["native_role_adjacency"]))
        self.assertEqual(self.result["legacy_incomplete_whitelist_count"], 2)
        self.assertEqual(self.result["legacy_scan_summary"]["numeric_parameter_adjacency_rows"], 6)

    def test_data_port_is_not_a_coefficient_port(self):
        r = self.inspect(self.graph(port=1))
        self.assertEqual([e["role"] for e in r["native_role_adjacency"]], ["data"])

    def test_edge_routing_does_not_hide_parameter_adjacency(self):
        r = self.inspect(self.graph(edge=True))
        self.assertEqual(r["native_role_adjacency"][0]["path"], ["d", "e", "n"])

    def test_off_output_ancestry_is_retained_without_causal_upgrade(self):
        r = self.inspect(self.graph(served=False))
        self.assertFalse(r["native_role_adjacency"][0]["target_on_output_ancestry"])
        self.assertFalse(r["causal_coefficient_use_certified"])

    def test_zero_input_dense_can_have_parameter_update_consumer(self):
        g = self.graph(); g["nodes"]["u"] = ["GRAD", {"lr": 1}]
        g["edges"] += [["d", "u", 0], ["n", "u", 1], ["k", "u", 2]]
        r = self.inspect(g)
        self.assertFalse(any(b == "d" for a, b, p in g["edges"]))
        self.assertTrue(any(e["kind"] == "GRAD" and e["role"] == "parameter"
                            for e in r["native_role_adjacency"]))
        self.assertFalse(r["causal_coefficient_use_certified"])

    def test_unknown_dot_primitive_fails_closed(self):
        with self.assertRaises(AuditError): self.inspect(self.graph(consumer="DOT"))

    def test_negative_and_boolean_ports_rejected(self):
        for port in (-1, True):
            g = self.graph(); g["edges"][0][2] = port
            with self.assertRaises(AuditError): self.inspect(g)

    def test_duplicate_port_and_cycle_rejected(self):
        g = self.graph(); g["edges"].append(["x", "n", 0])
        with self.assertRaises(AuditError): self.inspect(g)
        g = self.graph(edge=True); g["edges"][-1] = ["e", "e", 0]
        with self.assertRaises(AuditError): self.inspect(g)

    def test_native_parameter_role_drift_rejected(self):
        files = dict(self.files)
        files["native/vm.py"] = files["native/vm.py"].replace(
            b"self._dot(self._in(i, 0, vals), self._in(i, 1, vals), tape)",
            b"self._dot(self._in(i, 1, vals), self._in(i, 0, vals), tape)")
        with self.assertRaises(AuditError): native_contract(files)

    def test_source_gradients_and_seed_matches_are_retained(self):
        sources = self.result["source_archive_summaries"]
        self.assertEqual(sum(s["summary"]["rows"] for s in sources), 350)
        self.assertEqual(sum(len(s["GRAD_graphs"]) for s in sources), 8)
        self.assertEqual(self.result["all_arm_summary"]["grad_rows"], 0)
        evidence = self.result["source_population_evidence"]
        self.assertEqual(len(evidence["selected_source_checks"]), 7)
        self.assertEqual(len(evidence["recorded_seed_fingerprint_matches_to_GRAD_graphs"]), 10)
        self.assertEqual(evidence["unavailable_selected_sources"][0]["arm"], "SAME/TWIN/S1")

    def test_same_witness_does_not_become_independent_material(self):
        self.assertTrue(self.result["prior_raw_pruned_strings_and_six_caps_identical"])
        self.assertFalse(self.result["scope"]["causal_coefficient_use_or_admissible_learning_established"])


if __name__ == "__main__": unittest.main()

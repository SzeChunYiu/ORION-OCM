"""Read retained source-bound evidence; no literal archive count is an experiment."""
from fractions import Fraction as F
from pathlib import Path
from copy import deepcopy
import types
import unittest

HERE = Path(__file__).resolve().parent
e = types.ModuleType("aem_evidence")
e.__file__ = str(HERE/"architecture_evidence_v1.py")
exec(compile((HERE/"architecture_evidence_v1.py").read_bytes(),
             str(HERE/"architecture_evidence_v1.py"), "exec"), e.__dict__)
e.__file__ = str(HERE/"architecture_evidence_v1.py")


class EvidenceAndTransportControls(unittest.TestCase):
    def test_actual_retained_no_return_edge_controls_update(self):
        evidence = e.retained_evidence()
        for facts in evidence["native_no_return_edge_controls"].values():
            self.assertEqual(facts["outgoing_edges_from_graph"], [])
            self.assertEqual((facts["weight_before"], facts["weight_after"]), (8, 7))
            self.assertTrue(facts["write_recorded"])
            self.assertEqual((facts["output_before"], facts["output_after"]), (8, 7))
        self.assertEqual(evidence["new_native_or_ecology_calls"], 0)

    def test_outgoing_fact_is_derived_from_graph_not_reported_flag(self):
        nar = e.read_parent("research/gmi-native-adjoint-repair-v1/RECEIPT_V1.json")
        row = deepcopy(nar["native_vm_controls"]["B0/corrected/nonzero_input"])
        self.assertEqual(row["grad_outgoing_edges"], [])
        row["genotype"]["edges"].append(["grad", "output", 0])
        self.assertNotEqual(e.gradient_facts(row)["outgoing_edges_from_graph"], [])

    def test_exact_census_records_preserve_distinct_scopes(self):
        result = e.retained_evidence()
        self.assertEqual((result["retained_source_archives"], result["retained_source_cells"],
                          result["retained_source_grad_rows"]), (5, 350, 8))
        self.assertEqual((result["exported_rows"], result["exported_distinct_graphs"]), (70, 63))
        self.assertFalse(result["reported_34_cell_capabilities_recomputed"])

    def test_lower_bound_at_six_permits_three_orderings(self):
        xor, lower = 3*6+2, 2*6+1
        totals = [6+n for n in (13, 14, 15)]
        self.assertTrue(all(n >= lower for n in (13, 14, 15)))
        self.assertLess(totals[0], xor)
        self.assertEqual(totals[1], xor)
        self.assertGreater(totals[2], xor)

    def test_size_five_lower_endpoint_does_not_establish_tie(self):
        xor = 3*5+2
        self.assertEqual(6+11, xor)
        self.assertGreater(6+12, xor)

    def test_exact_hypothesis_revives_crossover_and_other_cost_changes_it(self):
        for n in range(1, 13):
            xor = 3*n+2
            exact = 6+2*n+1
            self.assertEqual(xor-exact, n-5)
            self.assertLess(xor, 6+4*n)
            self.assertEqual(n+(n-1)+1, 2*n)

    def test_corrected_zero_input_preserves_source_version_difference(self):
        nar = e.read_parent("research/gmi-native-adjoint-repair-v1/RECEIPT_V1.json")
        old = e.gradient_facts(nar["native_vm_controls"]["B0/old/zero_input"])
        new = e.gradient_facts(nar["native_vm_controls"]["B0/corrected/zero_input"])
        self.assertEqual((old["weight_before"], old["weight_after"]), (8, 9))
        self.assertEqual((new["weight_before"], new["weight_after"]), (8, 8))
        self.assertEqual((new["output_before"], new["output_after"]), (0, 0))


if __name__ == "__main__":
    unittest.main()

import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "grand_gmi_quantum_cut_scope_checks_v1",
    HERE / "grand_gmi_quantum_cut_scope_checks_v1.py",
)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class QuantumCutScopeTests(unittest.TestCase):
    def test_exact_separation_and_preserved_global_code(self):
        result = MOD.check_quantum_separation()
        self.assertEqual(result["classical_minimum_alphabet"], 5)
        self.assertEqual(result["quantum_minimum_dimension"], 4)
        self.assertEqual(result["classical_fixed_length_bits"], 3)
        self.assertEqual(result["quantum_qubits"], 2)
        self.assertEqual(result["promised_input_context_checks"], 74)
        self.assertEqual(result["global_four_message_identity_checks"], 16)
        self.assertEqual(result["classical_lower_certificate"]["candidate_orientations_exhausted"], 8)

    def test_collapsed_conflicting_encoding_is_rejected(self):
        _, edges, states, measurements = MOD.witness_data()
        states = list(states)
        i, j = edges[0]
        states[j] = states[i]
        with self.assertRaisesRegex(ValueError, "nonzero error"):
            MOD.verify_edge_protocol(states, measurements, edges)

    def test_swapped_decoder_outputs_are_rejected(self):
        _, edges, states, measurements = MOD.witness_data()
        edge = edges[0]
        measurements[edge] = tuple(reversed(measurements[edge]))
        with self.assertRaisesRegex(ValueError, "nonzero error"):
            MOD.verify_edge_protocol(states, measurements, edges)

    def test_missing_promised_context_is_rejected(self):
        _, edges, states, measurements = MOD.witness_data()
        del measurements[edges[0]]
        with self.assertRaisesRegex(ValueError, "contexts do not match"):
            MOD.verify_edge_protocol(states, measurements, edges)

    def test_incomplete_povm_is_rejected(self):
        _, edges, states, measurements = MOD.witness_data()
        i, j = edges[0]
        # Two orthogonal rank-one effects omit two dimensions of this carrier.
        measurements[i, j] = (states[i], states[j])
        with self.assertRaisesRegex(ValueError, "sum to identity"):
            MOD.verify_edge_protocol(states, measurements, edges)

    def test_receipt_replays_exactly(self):
        receipt = json.loads((HERE / "GRAND_GMI_QUANTUM_CUT_SCOPE_RECEIPT_V1.json").read_text())
        self.assertEqual(MOD.run(), receipt)


if __name__ == "__main__":
    unittest.main()

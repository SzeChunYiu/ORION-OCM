"""V4 changes execution identity and descriptive scope, never timing design."""
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent


class ExecutionRecoveryV4Tests(unittest.TestCase):
    def test_complete_instrument_identity_except_version_labels(self):
        old = (HERE / 'nn_nonnn_point_parity3_experiment_v3.py').read_text()
        expected = old.replace('frozen V3.', 'frozen V4.').replace('PREREG_V3', 'PREREG_V4').replace('RESULT_V3', 'RESULT_V4').replace('PARITY3_V3_INSTRUMENT', 'PARITY3_V4_INSTRUMENT').replace('V3 must disclose', 'V4 must disclose')
        self.assertEqual((HERE / 'nn_nonnn_point_parity3_experiment_v4.py').read_text(), expected)

    def test_registered_design_unchanged_and_no_timing_in_preflight(self):
        old = json.loads((HERE / 'NN_NONNN_POINT_PARITY3_PREREG_V3.json').read_text())
        new = json.loads((HERE / 'NN_NONNN_POINT_PARITY3_PREREG_V4.json').read_text())
        for key in ('candidates', 'problem', 'measurement_schedule', 'selection_rule',
                    'registered_resource_coordinates', 'development_accounting', 'substrate',
                    'claim_ceiling', 'execution_policy', 'candidate_expansion_attack'):
            self.assertEqual(old[key], new[key], key)
        self.assertIn('four response-equivalent', new['scientific_scope'])
        source = HERE / 'nn_nonnn_point_parity3_experiment_v4.py'
        spec = importlib.util.spec_from_file_location('parity4', source)
        module = importlib.util.module_from_spec(spec)
        exec(compile(source.read_bytes(), str(source), 'exec'), module.__dict__)
        with patch.object(module, 'timed_block', side_effect=AssertionError('timing forbidden')):
            result = module.deterministic_self_test()
        self.assertEqual(result['terminal'], 'PARITY3_V4_INSTRUMENT_SELF_TEST_GREEN')
        self.assertIs(result['protected_timing_measurement_executed'], False)


if __name__ == '__main__':
    unittest.main()

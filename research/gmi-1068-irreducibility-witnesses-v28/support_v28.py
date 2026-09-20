"""Load cached production modules and verify exposed recovery certificates."""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import oracle_v28 as oracle
import core_v28 as core
import forward_v28 as forward
import reverse_v28 as reverse
import recovery_v28 as recovery
import scalar_v28 as scalar


def check_recovery(test, observations, targets):
    expected = oracle.attained_decoders(observations, targets)
    result = recovery.recovery(observations, targets)
    test.assertEqual(result is not None, bool(expected))
    if result is None:
        return False
    test.assertTrue(recovery.verify_recovery(observations, targets, result))
    obs = tuple(result.observation_codes[i] for i in result.observation_labels)
    tgt = tuple(result.target_codes[i] for i in result.target_labels)
    oracle.certify(obs, observations)
    oracle.certify(tgt, targets)
    test.assertEqual(set(result.decoder), set(result.observation_labels))
    mapping = {oracle.exact(result.observation_codes[k]):
               oracle.exact(result.target_codes[v]) for k, v in result.decoder.items()}
    test.assertIn(mapping, expected)
    return True

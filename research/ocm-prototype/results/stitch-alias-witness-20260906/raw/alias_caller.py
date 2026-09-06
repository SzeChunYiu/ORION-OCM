"""Five frozen witness/control checks; no search, synthesis, rewrite or compression."""
import argparse
import json
from pathlib import Path
import resource
import sys
import time
import traceback
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'source'))
from observed_caller import observed, write
import generation_clia as G

IDS = ['saved_subtraction', 'saved_integer_predicate',
       'wrong_subtraction_orientation', 'shifted_integer_threshold',
       'unsupported_real_reinterpretation']

def forbidden(*args, **kwargs):
    raise ValueError('NO_DONOR_CALL_IN_WITNESS_QUALIFICATION')

def main(input_path, output):
    if sys.flags.optimize:
        raise ValueError('nonoptimized Python required')
    directory = Path(output); directory.mkdir()
    start = time.perf_counter(); cpu = time.process_time()
    state = {'status': 'CANNOT_CHECK_EXECUTION', 'counts': None, 'rows': []}
    try:
        data = json.loads(Path(input_path).read_text())
        if [p['id'] for p in data['probes']] != IDS:
            raise ValueError('FIXED_ASSIGNMENT_DRIFT')
        counts = observed(SimpleNamespace(donor=forbidden), directory)
        state['counts'] = counts
        for probe in data['probes']:
            index = len(state['rows'])
            row = {'id': probe['id'], 'expected': probe['expected'],
                   'left': probe['left'], 'right': probe['right']}
            write(directory/('probe-%02d-input.json' % index), probe)
            before = counts['verify_boundary_calls']
            params = [[G.S(name), G.S(sort)] for name, sort in probe['accepted_parameters']]
            if any(str(sort) != 'Int' for _, sort in params):
                raise ValueError('ACCEPTED_SIGNATURE_DRIFT')
            sigs = {'probe': {'parameters': params}}
            try:
                result = G.equivalent(probe['left'], probe['right'], sigs, timeout_ms=5000)
                row['verifier'] = result
                if result.get('native_invoked') is not True:
                    row['observed'] = 'CANNOT_CHECK'
                elif result.get('status') == 'PASS' and result.get('solver_result') == 'unsat':
                    row['observed'] = 'WITNESS_EQUIVALENT'
                elif (result.get('status') == 'FAIL' and result.get('solver_result') == 'sat'
                      and isinstance(result.get('counterexample'), str) and result['counterexample'].strip()):
                    row['observed'] = 'COUNTEREXAMPLE'
                else:
                    row['observed'] = 'CANNOT_CHECK'
            except ValueError as exc:
                row['exception'] = {'type': type(exc).__name__, 'message': str(exc)}
                no_call = counts['verify_boundary_calls'] == before
                row['observed'] = ('UNSUPPORTED_HOST_TYPE' if
                    probe['id'] == IDS[-1] and no_call and
                    str(exc) == 'parameter names/arity/sorts or output sort mismatch'
                    else 'CANNOT_CHECK_INTERFACE')
            except Exception as exc:
                row['observed'] = 'CANNOT_CHECK_EXECUTION'
                row['exception'] = {'type': type(exc).__name__, 'message': str(exc),
                                    'traceback': traceback.format_exc()}
            row['verify_boundary_calls'] = counts['verify_boundary_calls'] - before
            row['expected_outcome_matched'] = row['observed'] == probe['expected']
            write(directory/('probe-%02d-result.json' % index), row)
            state['rows'].append(row)
        state['assigned'] = len(IDS)
        state['completed'] = len(state['rows'])
        expected_counts = [1, 1, 1, 1, 0]
        matched = (len(state['rows']) == 5 and
                   all(r['expected_outcome_matched'] for r in state['rows']) and
                   [r['verify_boundary_calls'] for r in state['rows']] == expected_counts and
                   counts == {'verify_boundary_calls': 4, 'native_verify_invocations': 4,
                              'compress_calls': 0})
        state['status'] = 'WITNESS_QUALIFICATION_PASS' if matched else 'WITNESS_QUALIFICATION_NOT_PASSED'
    except Exception as exc:
        state['exception'] = {'type': type(exc).__name__, 'message': str(exc),
                              'traceback': traceback.format_exc()}
        traceback.print_exc()
    state.update(caller_wall_s=time.perf_counter()-start,
                 caller_self_cpu_s=time.process_time()-cpu,
                 caller_self_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                 total_process_tree_cpu='UNKNOWN', total_process_tree_peak_rss='UNKNOWN',
                 scope='Two exact witness identities and three controls; not exhaustive alias search.',
                 discovery='NOT_RUN', normalization='NOT_RUN', later_use='NOT_RUN',
                 novelty='NOT_ESTABLISHED', historical_receipts='UNCHANGED')
    write(directory/'caller-receipt.json', state)
    print(json.dumps(state), flush=True)
    return 0 if state['status'] == 'WITNESS_QUALIFICATION_PASS' else 2

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--input', required=True); p.add_argument('--output', required=True)
    a = p.parse_args()
    raise SystemExit(main(a.input, a.output))

"""One observed call to the frozen donor adapter; no policy or checker substitution."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import sys
import time
import traceback
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'source'))
sys.dont_write_bytecode = True

def write(path, value):
    with Path(path).open('x') as out:
        json.dump(value, out, indent=2, sort_keys=True)
        out.write('\n')

def observed(module, directory):
    """Observe unchanged native arguments/results; prohibit synthesis and a second compress."""
    import clia_process
    native = clia_process.invoke
    donor = module.donor
    counts = {'verify_boundary_calls': 0, 'native_verify_invocations': 0, 'compress_calls': 0}
    def verify(action, payload, **kwargs):
        if action != 'verify':
            raise ValueError('induction contract excludes synthesis')
        i = counts['verify_boundary_calls']; counts['verify_boundary_calls'] += 1
        prefix = directory / ('verify-%02d' % i)
        write(str(prefix)+'-request.json', {'action': action, 'payload': payload, 'kwargs': kwargs})
        try:
            result = native(action, payload, **kwargs)
        except BaseException as exc:
            write(str(prefix)+'-exception.json', {'type':type(exc).__name__, 'message':str(exc)})
            raise
        write(str(prefix)+'-result.json', result)
        counts['native_verify_invocations'] += int(result.get('native_invoked') is True)
        return result
    def get_donor():
        actual = donor()
        def compress(*args, **kwargs):
            if counts['compress_calls']:
                raise ValueError('second compress forbidden')
            counts['compress_calls'] += 1
            write(directory/'compress-request.json', {'args':args, 'kwargs':kwargs})
            try:
                result = actual.compress(*args, **kwargs)
                # Preserve the donor JSON before typed admission or equivalence can refuse it.
                write(directory/'compress-return.json', result.json)
                return result
            except BaseException as exc:
                write(directory/'compress-exception.json', {'type':type(exc).__name__, 'message':str(exc)})
                raise
        return SimpleNamespace(compress=compress)
    clia_process.invoke = verify
    module.donor = get_donor
    return counts

def main(input_path, output):
    if sys.flags.optimize:
        raise ValueError('optimized Python is outside contract')
    directory = Path(output); directory.mkdir()
    start = time.perf_counter(); cpu = time.process_time()
    state = {'status':'CALLER_EXCEPTION', 'counts':None}
    try:
        data = json.loads(Path(input_path).read_text())
        ids = [x['task']['task_id'] for x in data['experiences']]
        if ids != ['jmbl_fg_max3', 'jmbl_fg_mpg_guard2']:
            raise ValueError('fixed TRAIN assignment mismatch')
        import generation_stitch as G
        if G.SETTINGS != {'iterations':1, 'max_arity':2, 'threads':1, 'silent':True}:
            raise ValueError('fixed donor settings mismatch')
        counts = observed(G, directory); state['counts'] = counts
        returned = G.induce([(x['task'], x['candidate']) for x in data['experiences']])
        write(directory/'adapter-return.json', returned)
        state.update(status='ADAPTER_RETURNED', adapter_status=returned.get('status'))
    except BaseException as exc:
        state.update(exception={'type':type(exc).__name__, 'message':str(exc),
                                'traceback':traceback.format_exc()})
        traceback.print_exc()
    state.update(caller_wall_s=time.perf_counter()-start,
                 caller_self_cpu_s=time.process_time()-cpu,
                 caller_self_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                 total_process_tree_cpu='UNKNOWN', total_process_tree_peak_rss='UNKNOWN',
                 later_synthesis='NOT_RUN', primitive_alias_assessment='NOT_RUN',
                 useful_operator='NOT_ESTABLISHED', whole_lifetime_cost='NOT_ESTABLISHED',
                 historical_acquisition='IMPORTED_PRIOR_NOT_EXECUTED_OR_CHARGED_HERE')
    write(directory/'caller-receipt.json', state)
    print(json.dumps(state), flush=True)
    return 0 if state['status']=='ADAPTER_RETURNED' else 2

if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('--input', required=True); p.add_argument('--output', required=True)
    a=p.parse_args(); raise SystemExit(main(a.input,a.output))

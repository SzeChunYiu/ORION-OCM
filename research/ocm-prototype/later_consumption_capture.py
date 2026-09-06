"""Create-only raw capture. Uses the existing process-group cleanup supervisor."""
import argparse
import importlib.util
import json
from pathlib import Path
import time

from later_consumption_contract import ROOT, ROUTES, sha

SUPERVISOR = ROOT/'results/stitch-primitive-rewrite-20260906/raw/normalized-induction/supervision.py'
_spec = importlib.util.spec_from_file_location('later_consumption_prior_supervision', SUPERVISOR)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
capture_one = _module.capture_one
write = _module.write


def binding(path):
    p = Path(path)
    return {'bytes':p.stat().st_size, 'sha256':sha(p), 'resolved':str(p.resolve())}


def seal(directory):
    directory = Path(directory)
    inventory = {str(p.relative_to(directory)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(directory.rglob('*')) if p.is_file()}
    write(directory/'seal.json', inventory)
    return inventory


def verify_seal(directory):
    directory = Path(directory)
    inventory = json.loads((directory/'seal.json').read_text())
    actual = {str(p.relative_to(directory)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(directory.rglob('*'))
              if p.is_file() and p != directory/'seal.json'}
    if actual != inventory:
        raise ValueError('raw seal inventory/binding drift')
    return inventory


def verify(manifest):
    from later_consumption_contract import requests, CHECKS
    from later_consumption_prepare import command
    for group in ('source_bindings','environment_bindings','request_bindings'):
        for path, expected in manifest[group].items():
            if binding(path) != expected:
                raise ValueError('binding drift: '+path)
    if (manifest['candidate_commands'] != {r:command(20) for r in ROUTES}
            or manifest['checker_commands'] != {s:command(10) for s in CHECKS}
            or manifest['candidate_watchdog_s'] != 24 or manifest['checker_watchdog_s'] != 14
            or manifest['maximum_checker_obligations'] != 4):
        raise ValueError('frozen command/envelope drift')
    if manifest['route_order'] != list(ROUTES) or manifest['native_timeout_ms'] != 5000:
        raise ValueError('assignment drift')
    for route, source in requests().items():
        request = json.loads(Path(manifest['requests'][route]).read_text())
        if request != {'action':'synthesize','payload':{'sygus':source},'timeout_ms':5000}:
            raise ValueError('frozen request drift: '+route)


def decode_result(directory, capture):
    """Timeout/failed/malformed output is retained, never an absence proof."""
    result = {'status':'CANNOT_CHECK','candidate':'','reason':'native return unavailable',
              'native_invoked':'UNKNOWN' if capture.get('pid') else False,
              'metrics':{'envelope_wall_s':capture.get('elapsed_ns',0)/1e9,
                         'worker_cpu_s':None,'peak_rss_kib':None}}
    if capture.get('exit_code') != 0:
        result['reason'] = 'NATIVE_PROCESS_FAILED_OR_TIMEOUT'
        return result
    try:
        value = json.loads((Path(directory)/'stdout').read_text())
        if not isinstance(value, dict) or value.get('status') not in ('SOLUTION','PASS','FAIL','CANNOT_CHECK'):
            raise ValueError('malformed native result')
        if not isinstance(value.get('metrics'), dict) or type(value['metrics'].get('worker_pid')) is not int:
            raise ValueError('missing native worker completion identity')
        if value['status'] == 'SOLUTION' and not isinstance(value.get('candidate'), str):
            raise ValueError('malformed candidate')
        result.update(value)
        result['native_invoked'] = True  # Completed worker boundary, not proof of solver search work.
        result['metrics']['envelope_wall_s'] = capture.get('elapsed_ns',0)/1e9
    except (OSError, ValueError, TypeError, UnicodeError) as exc:
        result['reason'] = 'UNREADABLE_NATIVE_RESULT: '+type(exc).__name__
    return result


def run(manifest_path):
    start = time.perf_counter()
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text())
    verify(manifest)
    output = Path(manifest['output']); output.mkdir()
    candidates = output/'candidates'; candidates.mkdir()
    (candidates/'manifest.json').write_bytes(manifest_path.read_bytes())
    rows = []
    for route in ROUTES:
        try:
            verify(manifest)
            raw = capture_one(manifest['candidate_commands'][route], Path(manifest['requests'][route]).read_bytes(),
                              candidates/route, ROOT, manifest['candidate_watchdog_s'])
            rows.append({'route':route, 'capture':raw})
            verify(manifest)
        except (OSError, ValueError, KeyError) as exc:
            rows.append({'route':route, 'status':'CANNOT_CHECK_EXECUTION', 'reason':str(exc)})
            # Frozen source drift must not trigger further calls on changed bytes.
            break
    done = {x['route'] for x in rows}
    rows += [{'route':r, 'status':'NOT_RUN_FROZEN_BOUNDARY_FAILURE'} for r in ROUTES if r not in done]
    receipt = {'status':'CANDIDATE_RAW_SEALED', 'semantic_assessment':'NOT_RUN', 'rows':rows,
               'manifest_sha256':sha(manifest_path), 'capture_wall_s':time.perf_counter()-start,
               'process_tree_cpu':'UNKNOWN','process_tree_peak_rss':'UNKNOWN'}
    write(candidates/'receipt.json', receipt)
    seal(candidates)  # All assigned rows are sealed before any return is interpreted.
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.manifest)))

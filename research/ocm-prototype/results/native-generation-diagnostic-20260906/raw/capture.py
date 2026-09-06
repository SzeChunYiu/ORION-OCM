"""Four frozen interface cases, once each; raw capture only, no semantic grading."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    with Path(path).open('x') as out:
        json.dump(value, out, indent=2, sort_keys=True)
        out.write('\n')


def capture_one(argv, stdin_bytes, directory, cwd, watchdog_s):
    directory = Path(directory); directory.mkdir()
    (directory/'stdin.json').write_bytes(stdin_bytes)
    write(directory/'launch.json', {'argv': argv, 'cwd': str(cwd),
          'stdin_sha256': sha(directory/'stdin.json'), 'watchdog_s': watchdog_s})
    start = time.monotonic_ns(); process = None
    result = {'exit_code': None, 'pid': None, 'supervisor_timeout': False,
              'gnu_timeout_exit': False, 'error': None, 'cleanup_signal_sent': False}
    try:
        with (directory/'stdin.json').open('rb') as src, (directory/'stdout').open('wb') as out, (directory/'stderr').open('wb') as err:
            process = subprocess.Popen(argv, stdin=src, stdout=out, stderr=err,
                                       cwd=cwd, start_new_session=True)
            result['pid'] = process.pid
            write(directory/'pid.json', {'pid': process.pid})
            try:
                process.wait(timeout=watchdog_s)
            except subprocess.TimeoutExpired:
                result['supervisor_timeout'] = True
                os.killpg(process.pid, signal.SIGKILL)
                result['cleanup_signal_sent'] = True
                process.wait()
            result['exit_code'] = process.returncode
            result['gnu_timeout_exit'] = process.returncode in (124, 137)
    except (OSError, ValueError) as exc:
        result['error'] = type(exc).__name__+': '+str(exc)
    finally:
        if process is not None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
                result['cleanup_signal_sent'] = True
            except ProcessLookupError:
                pass
            process.wait()
        result['elapsed_ns'] = time.monotonic_ns()-start
        result['cost_scope'] = 'Per-case Popen through wait and cleanup; no CPU/RSS/tree or efficiency claim.'
        for stream in ('stdout', 'stderr'):
            path = directory/stream
            if not path.exists():
                path.write_bytes(b'')
            result[stream+'_sha256'] = sha(path)
            result[stream+'_bytes'] = path.stat().st_size
        write(directory/'result.json', result)
    return result


def verify(manifest):
    for path, binding in manifest['bindings'].items():
        if Path(path).stat().st_size != binding['bytes'] or sha(path) != binding['sha256']:
            raise ValueError('BINDING_DRIFT: '+path)
    head = subprocess.check_output(['/usr/bin/git','rev-parse','HEAD'], cwd=manifest['cwd'], text=True).strip()
    if head != manifest['execution_head']:
        raise ValueError('EXECUTION_HEAD_DRIFT')


def run(manifest_path, output):
    manifest_path, output = Path(manifest_path), Path(output)
    manifest = json.loads(manifest_path.read_text())
    output.mkdir()  # create-only; no overwrite or automatic retry
    (output/'manifest.json').write_bytes(manifest_path.read_bytes())
    receipt = {'scope': manifest['scope'], 'manifest_sha256': sha(manifest_path),
               'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'assigned_cases': manifest['execution_order'], 'cases': [], 'error': None}
    try:
        verify(manifest)
        proposal = json.loads(Path(manifest['proposal']).read_text())
        if proposal['execution_order'] != manifest['execution_order']:
            raise ValueError('ASSIGNMENT_DRIFT')
        (output/'proposal.json').write_bytes(Path(manifest['proposal']).read_bytes())
        for row in proposal['proposed_cases']:
            verify(manifest)
            case = row['case']; path = Path(manifest['proposal']).parent/row['input']
            if sha(path) != row['input_sha256']:
                raise ValueError('INPUT_DRIFT: '+case)
            result = capture_one(row['argv'], path.read_bytes(), output/case,
                                 manifest['cwd'], manifest['watchdog_seconds'])
            receipt['cases'].append({'case': case, **result})
            verify(manifest)
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        receipt['error'] = type(exc).__name__+': '+str(exc)
    done = {x['case'] for x in receipt['cases']}
    receipt['not_run'] = [x for x in manifest['execution_order'] if x not in done]
    receipt['completed_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    receipt['status'] = 'RAW_CAPTURE_COMPLETE' if not receipt['error'] and not receipt['not_run'] else 'RAW_CAPTURE_INCOMPLETE'
    receipt['semantic_status'] = 'NOT_GRADED'
    write(output/'receipt.json', receipt)
    inventory = {str(p.relative_to(output)): {'sha256':sha(p),'bytes':p.stat().st_size}
                 for p in sorted(output.rglob('*')) if p.is_file()}
    write(output/'seal.json', inventory)
    print(json.dumps({'status':receipt['status'],'case_exits':[x['exit_code'] for x in receipt['cases']],
                      'seal_sha256':sha(output/'seal.json')}))
    return 0 if receipt['status'] == 'RAW_CAPTURE_COMPLETE' else 2


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.manifest, args.output))

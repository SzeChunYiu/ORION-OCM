"""One root-bound native prefix verification/export, adapted from release observer."""
from pathlib import Path
import hashlib
import json
import os
import signal
import subprocess
import time

ROOT = Path('/home/billy/orion-director-work/20260908/ordinary-training-trace-export-v1')
REQUEST = ROOT / 'REQUEST-EXECUTION-01.json'
GATE = ROOT / 'ROOT-EXPORT-GATE-01.json'
OUTPUT = ROOT / 'native-export-01'
OBSERVATION = ROOT / 'native-export-observer-01'
EXPECTED_PYTHON = {'bytes': 21334200, 'sha256': 'edca1fc80dbd58182c849c13707fb6bfb522b0d7049adc408225f7c69b124d3b'}
EXPECTED_OUTPUTS = {'REQUEST.json', 'CUSTODIAN-PROGRESS.jsonl', 'CUSTODIAN-UNUSABLE-TRACES.json',
    'NATIVE-AUTHORITY.json', 'P1-INVENTORY.json', 'TEACHING-PACKET-CANDIDATE.json',
    'P0-CONTRACTS.json', 'RESULT.json'}


def byte_identity(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def identity(path):
    return byte_identity(path.read_bytes())


def write(path, data):
    with path.open('x') as stream:
        json.dump(data, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


def run():
    measured_start = time.perf_counter()
    request_raw = REQUEST.read_bytes()
    request = json.loads(request_raw)
    gate_raw = GATE.read_bytes()
    gate = json.loads(gate_raw)
    assert gate['authorization'] == 'ROOT_TRAINING_NATIVE_EXPORT_GATE'
    assert gate['request'] == byte_identity(request_raw) and gate['max_runs'] == 1
    assert type(gate['outer_wall_s']) is int and gate['outer_wall_s'] == 180
    assert gate['observer'] == identity(Path(__file__).resolve())
    assert gate['observer_contract'] == request['observer_contract']
    assert request['gate_path'] == str(GATE)
    assert gate['output'] == str(OUTPUT) and gate['observation'] == str(OBSERVATION)
    argv = [request['python']['path'], '-I', '-S', '-B', str(ROOT / 'trace_export.py'), str(REQUEST), str(OUTPUT)]
    assert gate['argv'] == argv
    pins = {str(ROOT / name): pin for name, pin in request['sources'].items()}
    pins[str(REQUEST)] = byte_identity(request_raw)
    for key in ('python', 'verifier', 'release', 'registry_scope', 'authority_contract',
                'observer_contract', 'P0_contracts', 'prefix'):
        row = request[key]
        pins[row['path']] = {k: row[k] for k in ('bytes', 'sha256')}
    assert pins[request['python']['path']] == EXPECTED_PYTHON
    pins[str(Path(__file__).resolve())] = gate['observer']
    for path, pin in gate['review_bindings'].items():
        assert path not in pins or pins[path] == pin, 'conflicting review pin: ' + path
        pins[path] = pin
    for path, pin in pins.items():
        assert identity(Path(path)) == pin, path
    assert not OUTPUT.exists() and OUTPUT.name not in {p.name for p in ROOT.iterdir()}
    assert not OBSERVATION.exists() and OBSERVATION.name not in {p.name for p in ROOT.iterdir()}
    OBSERVATION.mkdir()
    write(OBSERVATION / 'START.json', {'observer_pid': os.getpid(), 'gate': byte_identity(gate_raw),
        'request': byte_identity(request_raw), 'pins': pins, 'argv': argv})
    process_start = time.perf_counter()
    timed_out = False
    child, pid, status, usage, process_error = None, None, None, None, None
    try:
        with (OBSERVATION / 'stdout.log').open('xb') as out, (OBSERVATION / 'stderr.log').open('xb') as err:
            child = subprocess.Popen(argv, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                env={'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'}, start_new_session=True)
            while True:
                pid, status, usage = os.wait4(child.pid, os.WNOHANG)
                if pid:
                    break
                if time.perf_counter() - process_start > gate['outer_wall_s']:
                    timed_out = True
                    break
                time.sleep(0.02)
    except BaseException as error:
        process_error = repr(error)
    finally:
        if child is not None and pid != child.pid:
            try:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass  # The child may have exited between wait and kill.
                pid, status, usage = os.wait4(child.pid, 0)
            except BaseException as error:
                process_error = str(process_error) + '; cleanup: ' + repr(error)
        if child is not None and pid == child.pid:
            child.returncode = os.waitstatus_to_exitcode(status)
    process_wall = time.perf_counter() - process_start
    unchanged, read_errors, output_files, output_entries = {}, {}, {}, []
    if process_error is not None:
        read_errors['process'] = process_error
    for path, pin in pins.items():
        try:
            unchanged[path] = identity(Path(path)) == pin
        except OSError as error:
            unchanged[path] = False
            read_errors[path] = repr(error)
    try:
        unchanged[str(GATE)] = GATE.read_bytes() == gate_raw
        if OUTPUT.exists():
            entries = list(OUTPUT.iterdir())
            output_entries = [p.name for p in entries]
            output_files = {p.name: identity(p) for p in entries if p.is_file() and not p.is_symlink()}
    except OSError as error:
        read_errors['gate_or_outputs'] = repr(error)
    population_ok = set(output_files) == set(output_entries) == EXPECTED_OUTPUTS
    reaped = child is not None and pid == child.pid
    exit_code = child.returncode if reaped else None
    successful = (reaped and exit_code == 0 and all(unchanged.values()) and not timed_out
        and not read_errors and population_ok)
    receipt = {'schema': 'ordinary.native-export.outer-process.v1', 'observer_pid': os.getpid(),
        'pid': child.pid if child is not None else None, 'reaped': reaped, 'exit_code': exit_code,
        'timeout': timed_out, 'argv': argv, 'cwd': str(ROOT), 'process_wall_s': process_wall,
        'user_cpu_s': usage.ru_utime if usage else None, 'system_cpu_s': usage.ru_stime if usage else None,
        'rss_kib': usage.ru_maxrss if usage else None,
        'inputs_unchanged': unchanged, 'read_errors': read_errors, 'outputs': output_files,
        'output_entries': output_entries, 'output_population_ok': population_ok,
        'stdout': identity(OBSERVATION / 'stdout.log') if (OBSERVATION / 'stdout.log').is_file() else None,
        'stderr': identity(OBSERVATION / 'stderr.log') if (OBSERVATION / 'stderr.log').is_file() else None,
        'measured_outer_wall_s': time.perf_counter() - measured_start,
        'measurement_scope': 'Observer run entry through post-run input/output hashes; excludes interpreter/import startup, source preparation, root review and final receipt serialization. Not lifetime cost.',
        'terminal': 'NATIVE_EXPORT_PROCESS_COMPLETED' if successful else 'NATIVE_EXPORT_PROCESS_FAILED',
        'scope': 'One fixed native prefix verification and trace observation. Candidate artifacts require separate root qualification; no cut learner or evaluation executed by observer.'}
    write(OBSERVATION / 'PROCESS.json', receipt)
    print(json.dumps({'terminal': receipt['terminal'], 'pid': receipt['pid'], 'exit_code': exit_code,
        'receipt': str(OBSERVATION / 'PROCESS.json')}))
    return 0 if successful else 1


if __name__ == '__main__':
    raise SystemExit(run())

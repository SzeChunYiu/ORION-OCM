"""Source-frozen commissioning of one exposed finite application-closure apparatus."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import time

from episode import _runtime_check as verify_runtime, canonical_task, run_task
from f0_fixture import f0_fixture
from kernel_check import check_staged
from proof_check import stage_candidate

HERE = Path(__file__).resolve().parent
ASSIGNMENTS = (
    ('original', 'KERNEL_PASS'), ('restart', 'KERNEL_PASS'), ('eq_only', 'KERNEL_PASS'),
    ('missing_member', 'EXHAUSTED_REGISTERED_BOUND'), ('reversed_subset', 'EXHAUSTED_REGISTERED_BOUND'),
    ('wrong_witness', 'EXHAUSTED_REGISTERED_BOUND'), ('max_terms', 'CANNOT_CHECK'),
    ('injected_target', 'CANNOT_CHECK'), ('ill_typed', 'REJECTED'),
    ('missing_checker', 'CANNOT_CHECK'), ('corrupted_target', 'CANNOT_CHECK'),
    ('raw_ast', 'VALUE_ERROR'), ('admit_ast', 'VALUE_ERROR'), ('unknown_constant', 'VALUE_ERROR'))


def source_inventory():
    return {p.name: sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.iterdir())
            if p.is_file() and (p.suffix == '.py' or p.name == 'Target.lean')}


def write_json(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False); stream.write('\n')


def _case(name, original, original_digest, runtime, out):
    destination = out / name
    if name in dict(ASSIGNMENTS[:8]):
        task = f0_fixture(change=name) if name in {'missing_member', 'reversed_subset', 'wrong_witness'} else f0_fixture()
        if name == 'eq_only': task['constants'] = {0: task['constants'][0]}
        if name in {'missing_member', 'reversed_subset', 'wrong_witness'}:
            task['limits'] = {'max_application_depth': 3}
        if name == 'max_terms': task['limits'] = {'max_terms': 1}
        if name == 'injected_target': task['constants'][99] = original['goal']
        registered = original_digest if name == 'injected_target' else sha256(canonical_task(task)).hexdigest()
        declared = out / 'declared-inputs'; declared.mkdir(exist_ok=True)
        actual = canonical_task(task)
        with (declared / (name + '.json')).open('xb') as stream: stream.write(actual)
        write_json(declared / (name + '.binding.json'),
                   {'registered_sha256': registered, 'actual_sha256': sha256(actual).hexdigest()})
        return run_task(task, registered, runtime, destination)
    destination.mkdir()
    malformed = {'raw_ast': ['raw', 'by sorry'], 'admit_ast': ['admit'], 'unknown_constant': ['const', 99]}
    if name in malformed:
        candidate = malformed[name]
        write_json(destination / 'input-candidate.json', candidate)
        try:
            stage_candidate(candidate, destination / 'stage')
        except ValueError as exc:
            return {'terminal': 'VALUE_ERROR', 'reason': str(exc),
                    'staging_created': (destination / 'stage').exists()}
        return {'terminal': 'UNEXPECTED_STAGED', 'reason': 'malformed AST was accepted'}
    stage = stage_candidate(['const', 0], destination / 'stage')
    write_json(destination / 'stage.json', stage)
    if name == 'corrupted_target':
        (Path(stage['directory']) / 'Target.lean').write_text('def statement : Prop := True\n')
    lean = destination / 'missing-lean-runtime' if name == 'missing_checker' else runtime['lean_root']
    checked = check_staged(stage, lean, runtime['shared_libraries']['mounts'])
    if name == 'missing_checker': checked['commission_missing_runtime'] = str(lean)
    return checked


def _extra_control(name, result):
    reason = result.get('reason', '')
    if name == 'max_terms':
        worker = result.get('worker') or {}; process = result.get('worker_process') or {}
        audit = worker.get('worker_audit') or {}
        return (reason == worker.get('reason') == 'Operational bound: max_terms reached' and
                worker.get('status') == 'CANNOT_CHECK' and worker.get('candidate') is None and
                worker.get('counters', {}).get('generated_terms') == 1 and result.get('checker') is None and
                audit.get('guard_sealed') is True and audit.get('prohibited_events') == [] and
                process.get('terminal') == 'COMPLETED' and process.get('returncode') == 0 and
                type(process.get('pid')) is int and process['pid'] > 0 and not process.get('stderr'))
    if name == 'injected_target':
        return (reason == 'ValueError: task differs from separately registered input' and
                result.get('worker') is None and 'worker_process' not in result)
    if name == 'missing_checker':
        phases = result.get('phases', [])
        if len(phases) != 1 or phases[0].get('phase') != 'version': return False
        process = phases[0].get('process', {}); missing = result.get('commission_missing_runtime')
        return (reason == 'version: incomplete process envelope' and type(missing) is str and
                not Path(missing).exists() and process.get('pid') is None and
                process.get('terminal') == 'CANNOT_CHECK' and
                'FileNotFoundError' in process.get('reason', '') and missing in process['reason'])
    if name == 'corrupted_target':
        return reason == 'ValueError: checker source identity changed' and result.get('phases') == []
    if name in {'raw_ast', 'admit_ast', 'unknown_constant'}:
        expected = ('unregistered sort, free variable or constant' if name == 'unknown_constant'
                    else 'unregistered AST constructor or arity')
        return reason == expected and result.get('staging_created') is False
    if name == 'eq_only': return result.get('worker', {}).get('used_constants') == [0]
    return True


def commission(runtime_manifest, runtime_sha256, out):
    started = time.monotonic(); out = Path(out); out.mkdir(exist_ok=False)
    rows = [{'id': name, 'expected': expected, 'observed': 'NOT_RUN', 'passed': False, 'result': None}
            for name, expected in ASSIGNMENTS]
    record = {'schema': 'mechanical-f0-commission-v1', 'terminal': 'CANNOT_CHECK', 'reason': '',
              'runtime_manifest_source': str(runtime_manifest), 'runtime_sha256': runtime_sha256,
              'source_files': source_inventory(), 'cases': rows, 'restart_equal': False,
              'claim_scope': 'Exposed finite application-closure apparatus; PARENT_SUFFICIENT. No generic-witness, liveness, global no-neural, learned-method, transfer, FLT or novelty qualification.'}
    try:
        snapshot = out / 'source-snapshot'; snapshot.mkdir()
        for name, digest in record['source_files'].items():
            shutil.copyfile(HERE / name, snapshot / name)
            if sha256((snapshot / name).read_bytes()).hexdigest() != digest:
                raise ValueError('source snapshot drift')
        raw = Path(runtime_manifest).read_bytes()
        if (type(runtime_sha256) is not str or len(runtime_sha256) != 64 or
                any(c not in '0123456789abcdef' for c in runtime_sha256) or sha256(raw).hexdigest() != runtime_sha256):
            raise ValueError('runtime manifest differs from required registered SHA256')
        with (out / 'runtime-manifest.json').open('xb') as stream: stream.write(raw)
        runtime = json.loads(raw)
        verify_runtime(runtime)
        record['runtime_cost'] = {key: runtime.get(key) for key in
            ('preparation_wall_s', 'preparation_including_failed_attempts_wall_s', 'prior_development_preparations', 'acquisition')}
        def binding_check():
            if source_inventory() != record['source_files']:
                raise ValueError('top-level source changed after freeze')
            if {p.name for p in snapshot.iterdir()} != set(record['source_files']):
                raise ValueError('source snapshot file set changed')
            for name, digest in record['source_files'].items():
                if sha256((snapshot / name).read_bytes()).hexdigest() != digest:
                    raise ValueError('source snapshot changed after freeze')
            if Path(runtime_manifest).read_bytes() != raw or (out / 'runtime-manifest.json').read_bytes() != raw:
                raise ValueError('registered runtime manifest changed after freeze')
        original = f0_fixture(); original_digest = sha256(canonical_task(original)).hexdigest()
        record['original_task_sha256'] = original_digest
        for row in rows:
            binding_check()
            case_started = time.monotonic()
            try:
                result = _case(row['id'], original, original_digest, runtime, out)
                passed = result['terminal'] == row['expected'] and _extra_control(row['id'], result)
            except Exception as exc:
                result = {'terminal': 'CANNOT_CHECK', 'reason': type(exc).__name__ + ': ' + str(exc)}
                passed = False
            row.update(observed=result['terminal'], passed=passed, result=result,
                       wall_s=time.monotonic() - case_started)
            case_dir = out / row['id']; case_dir.mkdir(exist_ok=True)
            write_json(case_dir / 'case-record.json', row)
            binding_check()
        verify_runtime(runtime)
        first, restart = rows[0]['result'].get('worker'), rows[1]['result'].get('worker')
        record['restart_equal'] = (type(first) is dict and type(restart) is dict and
                                  first.get('candidate') is not None and
                                  first.get('candidate') == restart.get('candidate') and
                                  first.get('counters') == restart.get('counters'))
        if all(row['passed'] for row in rows) and record['restart_equal']:
            record['terminal'] = 'MECHANICAL_PROPOSER_COMMISSIONING_PASS'
        else:
            record['reason'] = 'One or more assigned controls or fresh-process equality did not pass'
        binding_check()
    except Exception as exc:
        record.update(terminal='CANNOT_CHECK', reason=type(exc).__name__ + ': ' + str(exc))
    record['wall_s'] = time.monotonic() - started
    record['cost_scope'] = ('This commissioning includes all assigned cases, failures, input/source validation and copying. '
                            'Pinned manifest retains runtime preparation and any declared failed-attempt history; absent history is unknown. '
                            'Episode costs overlap this envelope and must not be added twice. Acquisition/download '
                            'gaps, CPU/RSS and energy remain unmeasured; no speedup or whole-lifetime benefit claim.')
    write_json(out / 'commission.json', record)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime-manifest', required=True, type=Path)
    parser.add_argument('--runtime-sha256', required=True)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    record = commission(args.runtime_manifest, args.runtime_sha256, args.out)
    print(json.dumps({'terminal': record['terminal'], 'reason': record['reason'],
                      'record': str(args.out / 'commission.json')}, sort_keys=True))


if __name__ == '__main__':
    main()

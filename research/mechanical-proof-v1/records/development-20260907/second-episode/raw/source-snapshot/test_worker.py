"""Worker boundary controls execute hooks only in fresh isolated Python children."""
import json
from pathlib import Path
import subprocess
import sys

import pytest
from f0_fixture import f0_fixture

HERE = Path(__file__).resolve().parent


def child(body, payload=None):
    script = f"import sys; sys.path.insert(0, {str(HERE)!r}); import worker\n" + body
    run = subprocess.run([sys.executable, '-I', '-S', '-B', '-c', script],
                         input=json.dumps(payload) if payload is not None else '',
                         text=True, capture_output=True, timeout=10)
    assert run.returncode == 0, run.stderr
    return json.loads(run.stdout)


def test_worker_proposal_and_actual_module_and_term_dependencies():
    result = child('print(worker.json.dumps(worker.execute(sys.stdin.buffer.read())))', f0_fixture())
    assert result['status'] == 'FOUND'
    assert result['worker_audit']['guard_sealed'] is True
    names = {m['name'] for m in result['worker_audit']['imported_modules']}
    assert {'f0_terms', 'f0_search', 'dataclasses'} <= names
    assert 'f0_fixture' not in names
    assert result['worker_audit']['prohibited_events'] == []
    assert result['used_constants'] == [0]
    assert result['worker_audit']['constant_occurrences']['proof_term'] == {}
    assert result['worker_audit']['constant_occurrences']['type_annotations']['0'] > 0


@pytest.mark.parametrize('field', ['callback', 'restore', 'module', 'code', 'guard'])
def test_task_cannot_supply_execution_or_guard_fields(field):
    task = f0_fixture(); task[field] = 'anything'
    result = child('print(worker.json.dumps(worker.execute(sys.stdin.buffer.read())))', task)
    assert result['status'] == 'CANNOT_CHECK' and result['candidate'] is None


def test_duplicate_keys_nonfinite_and_transport_bounds_refuse():
    body = '''
answers = []
for raw in (b'{"goal":[],"goal":[],"constants":{}}', b'{"goal":NaN,"constants":{}}',
            b' ' * (worker.MAX_INPUT_BYTES + 1), b'[' * 10000):
    try: worker.parse_task(raw)
    except ValueError: answers.append('refused')
print(worker.json.dumps(answers))
'''
    assert child(body) == ['refused'] * 4


@pytest.mark.parametrize('probe', [
    "__import__('socket')", "__import__('ctypes')", "__import__('subprocess')",
    "worker.os.system('exit 99')", "worker.os.fork()", "eval('1+1')",
    "sys.audit('ctypes.dlopen', None)", "sys.audit('socket.connect', None, ('127.0.0.1', 1))",
])
def test_forbidden_dispatch_is_denied_and_recorded(probe):
    body = f'''
guard = worker.install_guard()
guard.seal()
try:
    {probe}
except worker.PolicyError:
    print(worker.json.dumps(guard.report()))
'''
    report = child(body)
    assert report['guard_sealed']
    assert len(report['prohibited_events']) == 1


def test_extra_source_and_stdlib_name_shadowing_are_refused(tmp_path):
    (tmp_path / 'extra.py').write_text('raise RuntimeError("executed forbidden module")')
    (tmp_path / 'colorsys.py').write_text('raise RuntimeError("executed shadow stdlib")')
    body = f'''
guard = worker.install_guard()
sys.path.insert(0, {str(tmp_path)!r})
answers = []
for name in ('extra', 'colorsys'):
    try: __import__(name)
    except worker.PolicyError: answers.append(name)
print(worker.json.dumps({{'answers':answers, 'audit':guard.report()}}))
'''
    result = child(body)
    assert result['answers'] == ['extra', 'colorsys']
    assert len(result['audit']['prohibited_events']) == 2


def test_main_refuses_nonfixed_input_argument():
    run = subprocess.run([sys.executable, '-I', '-S', '-B', str(HERE/'worker.py'), '/tmp/task.json'],
                         capture_output=True, text=True, timeout=10)
    assert run.returncode == 0, run.stderr
    result = json.loads(run.stdout)
    assert result['status'] == 'CANNOT_CHECK' and result['candidate'] is None


def test_loaded_code_exec_and_late_stdlib_import_are_sealed():
    report = child('''
compiled = compile('pass', '<control>', 'exec')
guard = worker.install_guard()
guard.seal()
for call in (lambda: exec(compiled), lambda: __import__('colorsys')):
    try: call()
    except worker.PolicyError: pass
print(worker.json.dumps(guard.report()))
''')
    assert [event['event'] for event in report['prohibited_events']] == ['exec', 'import']


def test_all_refusals_keep_the_worker_audit_schema():
    run = subprocess.run([sys.executable, '-I', '-S', '-B', str(HERE/'worker.py'), '/tmp/task.json'],
                         capture_output=True, text=True, timeout=10)
    assert run.returncode == 0
    result = json.loads(run.stdout)
    assert result['worker_audit']['schema'] == 'mechanical-worker-audit-v1'
    assert result['worker_audit']['guard_sealed'] is False


def test_floating_overflow_and_limits_code_fields_are_refused():
    assert child('''
try: worker.parse_task(b'{"goal":1e999,"constants":{}}')
except ValueError: print(worker.json.dumps('refused'))
''') == 'refused'
    task = f0_fixture(); task['limits'] = {'callback':'run'}
    result = child('print(worker.json.dumps(worker.execute(sys.stdin.buffer.read())))', task)
    assert result['status'] == 'CANNOT_CHECK' and result['candidate'] is None

"""Authored acquisition-phase controls; all material/resource dispatch is mocked."""
from hashlib import sha256
from pathlib import Path
import importlib.util
import io
import json
import copy
import runpy
import types
import pytest

HERE = Path(__file__).resolve().parent


@pytest.fixture
def contract():
    spec = importlib.util.spec_from_file_location('phase_contract_test', HERE / 'acquisition_contract.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def registration_fixture(tmp_path, monkeypatch, c):
    root = tmp_path / 'registration'; root.mkdir()
    assignments = {'denominator': 4, 'continuation_cursor': 4,
                   'rows': [{'key': str(i), 'assignment_rank': i} for i in range(4)]}
    policy = {'limits': {'memory_bytes': 1024}}
    files = {}
    for name, value in [('ASSIGNMENTS.json', assignments), ('POLICY.json', policy)]:
        raw = c.canonical(value); (root / name).write_bytes(raw)
        files[name] = {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}
    raw = c.canonical({'files': files}); (root / 'SEAL.json').write_bytes(raw)
    monkeypatch.setattr(c, 'SEAL', sha256(raw).hexdigest())
    return root, assignments, policy


def test_exact_toy_registration_consumes_fixed_bytes(tmp_path, monkeypatch, contract):
    root, assignments, policy = registration_fixture(tmp_path, monkeypatch, contract)
    binding, actual, actual_policy = contract.registration(root)
    assert binding['sha256'] == contract.SEAL
    assert actual == assignments and actual_policy == policy
    (root / 'POLICY.json').write_bytes(b'{}')
    with pytest.raises(ValueError): contract.registration(root)


def test_changed_reopened_policy_is_never_consumed(tmp_path, monkeypatch, contract):
    root, _, policy = registration_fixture(tmp_path, monkeypatch, contract)
    original = Path.open; reads = []
    def opened(path, mode='r', *args, **kwargs):
        if path == root / 'POLICY.json' and mode == 'rb':
            reads.append(True)
            if len(reads) > 1:
                return io.BytesIO(contract.canonical({'limits': {'memory_bytes': 999999}}))
        return original(path, mode, *args, **kwargs)
    monkeypatch.setattr(Path, 'open', opened)
    try: _, _, observed = contract.registration(root)
    except ValueError: pass
    else: assert observed == policy, 'unverified reopened policy was consumed'
    assert reads, 'control must reach the policy read'


def test_remaining_clock_cannot_restart_or_cross_boot(contract):
    start = {'boot_id': 'boot-a', 'monotonic_seconds': 20, 'whole_deadline_monotonic': 43220}
    assert contract.remaining_episode(start, 30, 'boot-a') == 43190
    assert contract.remaining_episode(start, 43221, 'boot-a') == 0
    for now, boot in [(19, 'boot-a'), (30, 'boot-b')]:
        with pytest.raises(ValueError): contract.remaining_episode(start, now, boot)


def receipt():
    return {'terminal': 'COMPLETED', 'returncode': 0, 'evidence_complete': True,
            'dispatch': {'state': 'STARTED', 'attempted': True, 'pid': 42}, 'pid': 42,
            'controller_readback': {}, 'reason': '',
            'cleanup': {'reaped': True, 'members_empty': True, 'controllers_removed': True}}


@pytest.mark.parametrize('fault', ['clean', 'exit', 'bool_exit', 'evidence', 'reaped',
    'members_empty', 'controllers_removed', 'no_dispatch', 'bool_pid', 'output', 'test_transport', 'validation'])
def test_worker_completion_requires_actual_clean_result(tmp_path, contract, fault):
    r = receipt(); root = tmp_path / 'materials'
    result = {'output': str(root), 'transport': 'PRODUCTION_SUBPROCESS'}
    checked = {'terminal': 'MATERIAL_BYTES_REVALIDATED', 'packages': 9}
    if fault in ('exit', 'bool_exit'): r['returncode'] = 1 if fault == 'exit' else False
    elif fault == 'evidence': r['evidence_complete'] = False
    elif fault in ('reaped', 'members_empty', 'controllers_removed'): r['cleanup'][fault] = False
    elif fault == 'no_dispatch': r['dispatch'] = {'state': 'NOT_ATTEMPTED', 'attempted': False}
    elif fault == 'bool_pid': r['dispatch']['pid'] = True
    elif fault == 'output': result['output'] = str(tmp_path / 'elsewhere')
    elif fault == 'test_transport': result['transport'] = 'INJECTED_TEST_TRANSPORT'
    elif fault == 'validation': checked['packages'] = 8
    worker = types.SimpleNamespace(revalidate=lambda *args: checked)
    if fault == 'clean': assert contract.validate_worker(result, root, worker, r) == checked
    else:
        with pytest.raises(ValueError): contract.validate_worker(result, root, worker, r)


@pytest.fixture
def phase(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location('phase_entry_test', HERE / 'acquisition_run.py')
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    c = m.contract; reg, _, _ = registration_fixture(tmp_path, monkeypatch, c)
    policy = runpy.run_path(str(HERE / 'coverage_policy.py'))['POLICY']
    oldreg = c.registration
    monkeypatch.setattr(c, 'registration', lambda p: (*oldreg(p)[:2], policy))
    monkeypatch.setattr(m, 'sys', types.SimpleNamespace(executable=str(Path(m.sys.executable).resolve())))
    monkeypatch.setattr(c, 'PYTHON', c.record(m.sys.executable)['sha256'])
    lock = tmp_path / 'lock.json'; lock.write_bytes(b'{}\n'); monkeypatch.setattr(c, 'LOCK', sha256(lock.read_bytes()).hexdigest())
    state = {'receipt': receipt(), 'calls': [], 'mutation': lambda out: None, 'clock': 100.0}
    clock = types.SimpleNamespace(monotonic=lambda: state['clock'], time=lambda: 1000.0)
    monkeypatch.setattr(m, 'time', clock)
    def dispatch(argv, env, limits, output, owned):
        state['calls'].append((argv, env, limits, output, owned))
        material = Path(argv[-1]); material.mkdir()
        c.write(material / 'RESULT.json', {'terminal': 'ACQUIRED', 'output': str(material),
                'transport': 'PRODUCTION_SUBPROCESS', 'packages': [{} for _ in range(9)]})
        state['mutation'](material.parent)
        return copy.deepcopy(state['receipt'])
    def checked(result, root):
        if len(result['packages']) != 9: raise ValueError('incomplete nine packages')
        return {'terminal': 'MATERIAL_BYTES_REVALIDATED', 'packages': 9}
    modules = {'resource_runner': types.SimpleNamespace(run=dispatch), 'build_profile': types.SimpleNamespace()}
    boot = types.SimpleNamespace(load=lambda: modules, loaded_sources=lambda _: {})
    monkeypatch.setattr(c, 'load_source', lambda p, name: boot if name == 'resource_boot' else types.SimpleNamespace(revalidate=checked))
    return m, reg, lock, tmp_path / 'episode', state


def test_phase_clean_retains_four_rows_and_no_semantic_dispatch(phase):
    m, reg, lock, out, state = phase; result = m.run(reg, lock, out)
    assert result['terminal'] == 'MATERIAL_READY' and result['semantic_checks_reached'] == 0
    assert result['whole_episode_open'] is True and len(state['calls']) == 1
    assert state['calls'][0][1] == {} and state['calls'][0][2]['wall_s'] == 3600
    declared = json.loads((out / 'ROWS-DECLARED.json').read_bytes())
    assert len(declared['rows']) == 4
    rows = json.loads((out / 'ROWS-AFTER-ACQUISITION.json').read_bytes())
    assert rows['denominator'] == rows['continuation_cursor'] == len(rows['rows']) == 4
    for row in rows['rows']:
        assert [s['state'] for s in row['stages']] == ['COMPLETED'] * 2 + ['NOT_RUN'] * 5
    with pytest.raises(FileExistsError): m.run(reg, lock, out)


@pytest.mark.parametrize('fault', ['STARTED.json', 'LIMITS.json', 'sources/acquisition_worker.py',
                                  'partial_nine', 'deadline', 'interrupted', 'resource_stop'])
def test_phase_failure_cannot_become_material_ready(phase, fault):
    m, reg, lock, out, state = phase
    def mutation(root):
        if fault == 'deadline': state['clock'] += 3601
        elif fault == 'interrupted': raise KeyboardInterrupt('authored interruption')
        elif fault == 'partial_nine':
            p = root / 'materials/RESULT.json'; value = json.loads(p.read_bytes()); value['packages'].pop(); p.write_bytes(m.contract.canonical(value))
        elif fault != 'resource_stop': (root / fault).write_bytes((root / fault).read_bytes() + b' ')
    state['mutation'] = mutation
    if fault == 'resource_stop': state['receipt']['terminal'] = 'RESOURCE_STOP'
    result = m.run(reg, lock, out)
    assert result['terminal'] == 'CANNOT_CHECK' and result['whole_episode_open'] is False
    reasons = {'STARTED.json': 'phase authority artifact drift', 'LIMITS.json': 'phase authority artifact drift',
               'sources/acquisition_worker.py': 'source drift', 'partial_nine': 'incomplete nine packages',
               'deadline': 'ACQUISITION_DEADLINE_INCLUDING_CUSTODY', 'interrupted': 'authored interruption'}
    if fault in reasons: assert reasons[fault] in result['error']['message']
    else: assert result['resource']['terminal'] == 'RESOURCE_STOP' and result['error'] is None
    assert result['semantic_checks_reached'] == 0 and (out / 'materials/RESULT.json').is_file()
    rows = json.loads((out / 'ROWS-AFTER-ACQUISITION.json').read_bytes())['rows']
    assert len(rows) == 4 and all(s['cause'] for row in rows for s in row['stages'])
    assert all(s['state'] == 'NOT_RUN' for row in rows for s in row['stages'][2:])


@pytest.mark.parametrize('which', ['registration', 'lock_parent', 'symlink'])
def test_output_overlap_refuses_before_creation(tmp_path, contract, which):
    source = tmp_path / 'input'; source.mkdir(); (source / 'lock').write_bytes(b'{}')
    out = source / 'episode'
    inputs = [source] if which != 'lock_parent' else [source / 'lock']
    if which == 'lock_parent': out = source
    if which == 'symlink':
        alias = tmp_path / 'alias'; alias.symlink_to(source, target_is_directory=True); out = alias / 'episode'
    with pytest.raises(ValueError): contract.new_output(out, inputs)
    assert not (source / 'episode').exists()


@pytest.mark.parametrize('fault', ['clock', 'contract_stamp', 'lock'])
def test_phase_refuses_before_dispatch_on_input_or_clock_failure(phase, monkeypatch, fault):
    m, reg, lock, out, state = phase
    if fault == 'clock':
        original = m.contract.registration
        def expired(path):
            result = original(path); state['clock'] += 3601; return result
        monkeypatch.setattr(m.contract, 'registration', expired)
    elif fault == 'contract_stamp': monkeypatch.setattr(m, 'CONTRACT_BYTES', m.CONTRACT_BYTES + b' ')
    else: monkeypatch.setattr(m.contract, 'LOCK', '0' * 64)
    result = m.run(reg, lock, out)
    assert result['terminal'] == 'CANNOT_CHECK' and state['calls'] == []
    expected = {'clock': 'ACQUISITION_DEADLINE', 'contract_stamp': 'executed contract differs', 'lock': 'exact corpus lock unavailable'}
    assert expected[fault] in result['error']['message']
    assert result['reached_phase'] == 'INPUT_VALIDATION' and not (out / 'resource').exists()

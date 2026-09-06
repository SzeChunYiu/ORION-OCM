"""Manual donor records exercise capture/check sequencing; no native solvers run."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from test_later_consumption_contract import PRIMITIVE, USED


def modules():
    for name in ('later_consumption_capture', 'later_consumption_assess', 'later_consumption_prepare'):
        assert importlib.util.find_spec(name) is not None, name + ' preparation is missing'
    import later_consumption_capture as C
    import later_consumption_assess as A
    import later_consumption_prepare as P
    return C, A, P


def fake_capture(candidate, events, *, exit_code=0, response=None):
    def capture(argv, stdin_bytes, directory, cwd, watchdog_s):
        events.append(json.loads(stdin_bytes))
        directory = Path(directory)
        directory.mkdir()
        (directory/'stdin.json').write_bytes(stdin_bytes)
        payload = response if response is not None else {'status':'SOLUTION', 'candidate':candidate,
            'solver':'cvc5 1.3.4', 'metrics':{'worker_pid':123, 'worker_cpu_s':0.1}}
        (directory/'stdout').write_text(json.dumps(payload))
        (directory/'stderr').write_text('deliberately retained stderr')
        result = {'exit_code':exit_code, 'pid':123, 'elapsed_ns':100, 'supervisor_timeout':exit_code == 137}
        (directory/'result.json').write_text(json.dumps(result))
        return result
    return capture


def prepared(tmp_path, monkeypatch):
    C, A, P = modules()
    sentinel = tmp_path/'mock-environment'
    sentinel.write_text('MOCK_UNIT_TEST_ENVIRONMENT_NOT_NATIVE_QUALIFICATION\n')
    environment = {str(sentinel): C.binding(sentinel)}
    monkeypatch.setattr(P, 'environment', lambda: environment)
    manifest = P.prepare(tmp_path/'packet')
    return C, A, manifest


def test_raw_three_routes_sealed_before_any_check_and_no_retry(tmp_path, monkeypatch):
    C, A, manifest = prepared(tmp_path, monkeypatch)
    events = []
    monkeypatch.setattr(C, 'capture_one', fake_capture(PRIMITIVE, events))
    raw = C.run(manifest)
    assert len(events) == 3
    assert all(x['action'] == 'synthesize' and x['timeout_ms'] == 5000 for x in events)
    assert raw['status'] == 'CANDIDATE_RAW_SEALED'
    output = Path(json.loads(manifest.read_text())['output'])
    seal = C.verify_seal(output/'candidates')
    assert len([k for k in seal if k.endswith('/stdout')]) == 3
    assert not (output/'assessment').exists()
    with pytest.raises(FileExistsError):
        C.run(manifest)
    assert len(events) == 3


def test_timeout_and_malformed_rows_retained_as_assigned_denominator(tmp_path, monkeypatch):
    C, A, manifest = prepared(tmp_path, monkeypatch)
    events = []
    monkeypatch.setattr(C, 'capture_one', fake_capture('', events, exit_code=137, response={'bad':True}))
    C.run(manifest)
    output = Path(json.loads(manifest.read_text())['output'])
    assert [r['route'] for r in json.loads((output/'candidates/receipt.json').read_text())['rows']] == ['C','E0','B']
    monkeypatch.setattr(A, 'native_verify', lambda *a: pytest.fail('invalid row must not launch native checker'))
    got = A.run(manifest)
    assert len(got['rows']) == 3
    assert got['consumption'] == 'CANNOT_CHECK_CONSUMPTION'
    assert got['reached_obligations'] == []
    assert all(x['status'] == 'CANNOT_CHECK' for x in got['rows'])


@pytest.mark.parametrize('candidate, expected', [(PRIMITIVE,'NO_OBSERVED_USE'), (USED,'LEARNED_DEFINITION_CONSUMPTION_QUALIFIED')])
def test_four_check_ceiling_and_observed_use_is_separate(tmp_path, monkeypatch, candidate, expected):
    C, A, manifest = prepared(tmp_path, monkeypatch)
    events = []
    def donor(argv, stdin, directory, cwd, watchdog):
        body = candidate if Path(directory).name == 'B' else PRIMITIVE
        return fake_capture(body, events)(argv, stdin, directory, cwd, watchdog)
    monkeypatch.setattr(C, 'capture_one', donor)
    C.run(manifest)
    checks = []
    def verifier(manifest, output, slot, payload):
        assert (Path(manifest['output'])/'candidates/seal.json').is_file()
        checks.append((slot,payload))
        return {'status':'PASS','native_invoked':True,'metrics':{},'solver_result':'unsat'}
    monkeypatch.setattr(A, 'native_verify', verifier)
    got = A.run(manifest)
    assert [k for k,p in checks] == ['C-spec','E0-spec','B-expansion','B-spec']
    assert got['consumption'] == expected
    assert len(got['rows']) == 3
    assert got['reached_obligations'] == [k for k,p in checks]
    assert got['whole_lifetime_economics'] == 'NOT_ESTABLISHED'
    with pytest.raises(FileExistsError):
        A.run(manifest)
    assert len(checks) == 4


def test_wrong_expansion_cannot_qualify_even_when_spec_passes(tmp_path, monkeypatch):
    C, A, manifest = prepared(tmp_path, monkeypatch)
    events = []
    def donor(argv, stdin, directory, cwd, watchdog):
        return fake_capture(USED if Path(directory).name == 'B' else PRIMITIVE, events)(argv,stdin,directory,cwd,watchdog)
    monkeypatch.setattr(C, 'capture_one', donor)
    C.run(manifest)
    monkeypatch.setattr(A, 'native_verify', lambda m,o,s,p: {'status':'FAIL' if s == 'B-expansion' else 'PASS', 'native_invoked':True,'metrics':{}})
    got = A.run(manifest)
    assert got['consumption'] == 'CANNOT_CHECK_CONSUMPTION'
    assert got['rows'][-1]['check']['status'] == 'PASS'
    assert got['rows'][-1]['expansion']['status'] == 'FAIL'


def test_raw_drift_prevents_assessment_native_calls(tmp_path, monkeypatch):
    C, A, manifest = prepared(tmp_path, monkeypatch)
    monkeypatch.setattr(C, 'capture_one', fake_capture(PRIMITIVE, []))
    C.run(manifest)
    output = Path(json.loads(manifest.read_text())['output'])
    (output/'candidates/B/stdout').write_text('{}')
    monkeypatch.setattr(A, 'native_verify', lambda *a: pytest.fail('raw drift reached native checker'))
    with pytest.raises(ValueError, match='seal'):
        A.run(manifest)


def test_prepared_commands_preserve_worker_and_envelope(tmp_path, monkeypatch):
    C, A, manifest = prepared(tmp_path, monkeypatch)
    m = json.loads(manifest.read_text())
    assert m['status'] == 'PREPARED_NOT_FROZEN_NOT_EXECUTED'
    assert m['route_order'] == ['C','E0','B']
    assert set(m['candidate_commands']) == {'C','E0','B'}
    assert set(m['checker_commands']) == {'C-spec','E0-spec','B-expansion','B-spec'}
    for argv in m['candidate_commands'].values():
        assert '20s' in argv and '--as=4294967296' in argv
        assert argv[argv.index('-c')+1] == '0'
        assert argv[-1].endswith('/clia_worker.py')
    for argv in m['checker_commands'].values():
        assert '10s' in argv and argv[-1].endswith('/clia_worker.py')
    assert m['native_timeout_ms'] == 5000
    assert m['source_bindings']
    sentinel = tmp_path/'mock-environment'
    assert m['environment_bindings'] == {str(sentinel): C.binding(sentinel)}


def test_command_drift_cannot_launch_native(tmp_path, monkeypatch):
    C, A, manifest = prepared(tmp_path, monkeypatch)
    m = json.loads(manifest.read_text())
    m['candidate_commands']['B'].append('--new-solver-option')
    manifest.write_text(json.dumps(m))
    monkeypatch.setattr(C, 'capture_one', lambda *a: pytest.fail('command drift launched native'))
    with pytest.raises(ValueError, match='command'):
        C.run(manifest)


def test_raw_seal_remains_verifiable_after_evidence_copy(tmp_path, monkeypatch):
    import shutil
    C, A, manifest = prepared(tmp_path, monkeypatch)
    monkeypatch.setattr(C, 'capture_one', fake_capture(PRIMITIVE, []))
    C.run(manifest)
    output = Path(json.loads(manifest.read_text())['output'])
    copied = tmp_path/'copied-evidence'
    shutil.copytree(output/'candidates',copied)
    assert C.verify_seal(copied) == C.verify_seal(output/'candidates')


def test_production_environment_rejects_unpinned_interpreter(tmp_path, monkeypatch):
    _, _, P = modules()
    monkeypatch.setattr(P.sys, 'executable', str(tmp_path/'unpinned-python'))
    monkeypatch.setattr(P.metadata, 'distribution', lambda *a: pytest.fail('interpreter refusal must precede dependency inspection'))
    # Exercise the real production body; no prior cached qualification may answer.
    with pytest.raises(ValueError, match='pinned generation environment'):
        P.environment.__wrapped__()

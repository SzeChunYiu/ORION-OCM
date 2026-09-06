"""Actual five-process unit audit qualification, not a synthetic full-study pass."""
import copy
import json
from pathlib import Path
import pytest
import grade_clia_reuse as G
import grade_clia_reuse_audit as A
from grade_clia_reuse_capture import Sealed


@pytest.fixture(scope='module')
def emitted_workers(tmp_path_factory):
    from test_clia_reuse_worker_fixture import emit_unit_workers
    result = {}
    for arm in ('native', 'ocm'):
        base = tmp_path_factory.mktemp('actual-audit-' + arm)
        emitted = emit_unit_workers(base, arm)
        stages = []
        for phase in A.PHASES[1:]:
            worker = json.loads((base / (phase + '.stdout')).read_text())
            rows = [json.loads(x) for x in (base / (phase + '.rows.jsonl')).read_text().splitlines()]
            stages.append((worker, rows))
        result[arm] = {'stages': stages, 'bindings': stages[0][0]['bindings'], 'directory': str(base)}
    return result


def test_actual_audits_events_values_and_withdrawal_no_alarm(emitted_workers):
    f1 = {'arms': {a: data['bindings'] for a, data in emitted_workers.items()}}
    A.validate_f1(f1)
    for arm, data in emitted_workers.items():
        prior = None
        for worker, rows in data['stages']:
            phase = worker['phase']; A.check_events(worker, rows, phase)
            prior = A.stage_audits(worker, data['bindings'], phase, prior)
            math, syntax = A.grade_rows(worker, rows, data['bindings'])
            assert syntax == []  # Unit model is a named placeholder, never inference.
            assert len(math) == 2
            assert [r['status'] for r in math] == (['EXPECTED_POLICY_REFUSAL', 'CORRECT_VALUE']
                if phase == 'withdraw' else ['CORRECT_VALUE', 'CORRECT_VALUE'])
        assert len({w['pid'] for w, _ in data['stages']}) == 5


@pytest.mark.parametrize('mutation', ['liveness', 'support', 'payload', 'history', 'missing_proof'])
def test_altered_real_audit_is_rejected(emitted_workers, mutation):
    for data in emitted_workers.values():
        worker, _ = data['stages'][0]; audit = copy.deepcopy(worker['final_audit']); b = data['bindings']
        key = b['programs']['max3']['proof_id']
        if mutation == 'liveness': audit['records'][key]['liveness'] = 'DEAD'
        elif mutation == 'support': audit['records'][key]['support'] = {'lower': [[]], 'upper': [[]]}
        elif mutation == 'payload': audit['records'][key]['payload']['ALTERED'] = True
        elif mutation == 'history': audit['history_records'][b['programs']['max3']['history_ids'][0]]['sha256'] = '0' * 64
        else: del audit['records'][key]
        with pytest.raises((ValueError, KeyError)): A.check_audit(audit, b, set())


def test_old_payload_cannot_be_replaced_or_dropped_after_revision(emitted_workers):
    for data in emitted_workers.values():
        worker, _ = data['stages'][2]; before = worker['exit_query_audit']['records']
        after = copy.deepcopy(worker['final_audit']); key = next(iter(before))
        after['records'][key]['payload']['ALTERED'] = True
        after['records'][key]['payload_sha256'] = A.digest(after['records'][key]['payload'])
        with pytest.raises(ValueError, match='IMMUTABLE_PRIOR_CHANGED'):
            A.check_audit(after, data['bindings'], A.revoked_for(data['bindings'], 'history', after=True), before)
        del after['records'][key]
        with pytest.raises((ValueError, KeyError)):
            A.check_audit(after, data['bindings'], A.revoked_for(data['bindings'], 'history', after=True), before)


@pytest.mark.parametrize('mutation', ['tuple', 'unfinished', 'counter', 'extra_event'])
def test_actual_event_log_mutations_do_not_establish_reuse(emitted_workers, mutation):
    for data in emitted_workers.values():
        worker, rows = copy.deepcopy(data['stages'][0])
        if mutation == 'tuple': worker['invocations'][0]['payload_sha256'] = '0' * 64
        elif mutation == 'unfinished': worker['invocations'][0].pop('finished_monotonic')
        elif mutation == 'counter': rows[0]['invocation_delta']['application'] = True
        else: worker['invocations'].append(copy.deepcopy(worker['invocations'][-1]))
        with pytest.raises(ValueError): A.check_events(worker, rows, 'warm')


def test_real_policy_cannot_be_relabelled_error_or_missing_invocation(emitted_workers):
    for data in emitted_workers.values():
        worker, rows = copy.deepcopy(data['stages'][3])
        rows[0]['result']['status'] = 'CANNOT_CHECK_APPLICATION'
        math, _ = A.grade_rows(worker, rows, data['bindings'])
        assert math[0]['status'] == 'REFUSAL_NOT_ESTABLISHED'
        worker, rows = copy.deepcopy(data['stages'][0]); rows[0]['invocation_delta']['application'] = 0
        with pytest.raises(ValueError, match='APPLICATION_NOT_OBSERVED'):
            A.grade_rows(worker, rows, data['bindings'])


def test_real_raw_bytes_seal_no_alarm_and_changed_or_unsealed_rejected(emitted_workers, tmp_path):
    raw = Path(emitted_workers['native']['directory']) / 'warm.stdout'
    destination = tmp_path / 'actual-native.stdout'; destination.write_bytes(raw.read_bytes())
    from clia_reuse_study_common import sha
    (tmp_path / 'capture-manifest.json').write_text(json.dumps({'files': {destination.name: sha(destination)}}))
    sealed = Sealed(tmp_path)
    assert sealed.read(destination.name) == json.loads(raw.read_text())
    with pytest.raises(ValueError, match='UNSEALED'): sealed.path('missing.rows')
    destination.write_bytes(raw.read_bytes() + b' ')
    with pytest.raises(ValueError): Sealed(tmp_path)


def test_missing_capture_keeps_assigned_denominators_and_unknown_cost(tmp_path):
    result = G.grade_capture(tmp_path)
    assert result['function'] == 'CANNOT_CHECK_STUDY'
    assert result['cost']['status'] == 'CANNOT_CHECK_COST' and result['cost']['total_process_tree_cpu_s'] is None
    for arm in result['arms'].values():
        assert arm['assigned']['authorized_values'] == 34 and arm['assigned']['policy_refusals'] == 2
        assert arm['math_unchecked'] == 36 and arm['syntax_unchecked'] == 5


def test_actual_unit_model_placeholder_custody_not_prediction(emitted_workers, tmp_path):
    from grade_clia_reuse_capture import model_archives
    from clia_reuse_study_common import sha
    f1 = {'arms': {a: d['bindings'] for a, d in emitted_workers.items()}}
    paths = []
    for arm, data in emitted_workers.items():
        name = data['bindings']['model_file']
        source = Path(data['directory']) / 'state' / name
        target = tmp_path / (arm + '-state') / name
        target.parent.mkdir(); target.write_bytes(source.read_bytes()); paths.append(target)
    def seal():
        (tmp_path / 'capture-manifest.json').write_text(json.dumps({'files': {str(p.relative_to(tmp_path)): sha(p) for p in paths}}))
        return Sealed(tmp_path)
    expected = {'sha256': sha(paths[0]), 'bytes': paths[0].stat().st_size}
    model_archives(seal(), f1, expected)
    paths[0].write_bytes(b'ALTERED_UNIT_PLACEHOLDER')
    with pytest.raises(ValueError, match='FINAL_MODEL_ARCHIVE_CHANGED'):
        model_archives(seal(), f1, expected)


def test_native_repeated_syntax_binds_without_timing_uniqueness(tmp_path, monkeypatch):
    from clia_reuse_study_state import Actor
    import udpipe_donor
    actor = Actor(tmp_path / 'native', 'native')
    model = tmp_path / 'UNIT_PLACEHOLDER_NOT_A_MODEL'; model.write_bytes(b'UNIT_FIXED_PREDICTOR')
    actor.setup(model, {'UNIT_FIXTURE': 'no model inference'})
    words = [{'id': 1, 'form': 'widget', 'head': 0, 'deprel': 'root', 'upos': 'NOUN'}]
    calls = []
    def fixed(tokens, path, model_sha):
        calls.append(tokens)
        return {'status': 'PREDICTED', 'words': copy.deepcopy(words), 'model_sha256': model_sha}
    monkeypatch.setattr(udpipe_donor, 'predict', fixed)
    request = {'kind': 'syntax', 'tokens': ['widget']}
    first, second = actor.query(request), actor.query(request)
    assert first == second and len(calls) == 2
    audit = actor.audit()
    records = {k: r for k, r in audit['records'].items() if k.startswith('syntax/')}
    assert len(records) == 1
    key, record = next(iter(records.items()))
    assert key == 'syntax/' + A.digest(record['payload']) + '.json'
    for result in (first, second):
        row = {'arm': 'native', 'request': request, 'result': result}
        assert A.selected_record(row, audit) == record
    assert all('wall' not in key for key in first['answer'])

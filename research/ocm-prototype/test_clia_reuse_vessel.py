"""Host-binding/revocation unit controls, not the prospective new-input reuse panel."""
from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys
import pytest
from ocm.kso.warrant import WarrantProfile
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel
import clia_solver
import clia_checker
from clia_tasks import load_task
from g1_field import ROOT, MODEL, CLIA, SCOPE, put
from g1_vessel import CONFIG
import clia_reuse_vessel as V
from test_clia_reuse_program import UNIT_PROGRAMS, request


def fixture_state(tmp_path):
    runtime = OCMRuntime(tmp_path, config=CONFIG)
    _, shared = runtime.admit_evidence({'unit': 'fixed grammar/checker prior'}, Channel.INSTRUCTION, 'unit', scope=SCOPE)
    support = WarrantProfile.of({shared})
    put(runtime, ROOT, {'unit': 'root'}, support, ())
    put(runtime, MODEL, {'unit': 'model placeholder; no donor model loaded', 'sha256': '0' * 64}, support)
    put(runtime, CLIA, {'unit': 'checker prior'}, support)
    result = {}
    for task_id, code in UNIT_PROGRAMS.items():
        task = load_task(task_id)
        proposal = dict(status='SOLUTION', candidate=code, task_sha256=task['task_sha256'], grammar_id=task['grammar']['id'])
        assert clia_checker.check(task, proposal)['status'] == 'PASS'
        _, query = runtime.admit_evidence({'unit_task': task_id}, Channel.INSTRUCTION, 'unit-public-spec', scope=SCOPE)
        truth = support.meet(WarrantProfile.of({query}))
        record = dict(claim='SPECIFICATION_VERIFIED_PROGRAM', query={'kind': 'clia', 'task': task}, output=proposal)
        _, proof = runtime.admit_evidence(record, Channel.PROOF, 'unit-fixed-checker', scope=SCOPE, derived_from=truth)
        aid = 'unit-proof:' + task_id
        put(runtime, aid, record, truth.meet(WarrantProfile.of({proof})), (CLIA,), 'EXACT_CHECKER', 'proof')
        result[task_id] = (aid, query, proof)
    _, history = runtime.admit_evidence({'unit': 'separate search-history observation'}, Channel.OBSERVATION, 'unit-history', scope=SCOPE)
    runtime.persist()
    return runtime, result, history, shared


def test_registry_rebind_full_catalogue_and_no_synthesis(tmp_path, monkeypatch):
    runtime, records, history, shared = fixture_state(tmp_path)
    desc = V.adopt(runtime, records['jmbl_fg_max3'][0], history=[history])
    assert set(desc['support']['lower'][0]) == {records['jmbl_fg_max3'][1], shared}
    V.bind(runtime, desc['id'])
    def forbidden(*args, **kwargs): raise AssertionError('application invoked synthesis')
    monkeypatch.setattr(clia_solver, 'propose', forbidden)
    out = V.apply(runtime, request(desc, [41, -7, 12]))
    assert out['status'] == 'ADMITTED' and out['answer']['value'] == 41
    assert out['catalogue'][:2] == ['syntax:udpipe1', 'procedure:cvc5']
    assert out['counters']['catalogue_visits'] == out['catalogue']
    assert out['counters']['synthesis_dispatches'] == 0 and out['counters']['application_calls'] == 1
    fresh = OCMRuntime(tmp_path, config=CONFIG)
    assert not fresh.state.operators.operators
    unbound = V.apply(fresh, request(desc, [41, -7, 12]))
    assert unbound['status'] != 'ADMITTED' and unbound['counters']['application_calls'] == 0
    V.bind(fresh, desc['id'])
    assert V.apply(fresh, request(desc, [41, -7, 12]))['status'] == 'ADMITTED'


def test_history_withdrawal_true_query_withdrawal_unaffected_and_restore(tmp_path):
    runtime, records, history, shared = fixture_state(tmp_path)
    descriptors = {name: V.adopt(runtime, record[0], history=[history]) for name, record in records.items()}
    for desc in descriptors.values(): V.bind(runtime, desc['id'])
    maximum = descriptors['jmbl_fg_max3']; guard = descriptors['jmbl_fg_mpg_guard2']
    first = V.apply(runtime, request(maximum, [41, -7, 12]))
    untouched = V.apply(runtime, request(guard, [17, -9, 0]))
    runtime.revoke([history]); runtime.persist()
    assert V.apply(runtime, request(maximum, [41, -7, 12]))['status'] == 'ADMITTED'
    runtime.revoke([records['jmbl_fg_max3'][1]]); runtime.persist()
    fresh = OCMRuntime(tmp_path, config=CONFIG)
    assert not fresh.state.ks.atom_map()[first['admitted_id']].is_live(fresh.state.revoked)
    assert fresh.state.ks.atom_map()[untouched['admitted_id']].is_live(fresh.state.revoked)
    assert fresh.state.ks.atom_map()[MODEL].is_live(fresh.state.revoked)
    assert V.apply(fresh, request(maximum, [41, -7, 12]))['status'] != 'ADMITTED'
    V.bind(fresh, guard['id'])
    assert V.apply(fresh, request(guard, [17, -9, 0]))['answer']['value'] == 8
    fresh.reinstate([records['jmbl_fg_max3'][1]]); V.bind(fresh, maximum['id'])
    assert V.apply(fresh, request(maximum, [41, -7, 12]))['status'] == 'ADMITTED'
    with pytest.raises(ValueError): fresh.revoke([records['jmbl_fg_max3'][2]])


def test_wrong_host_value_never_admitted(tmp_path):
    runtime, records, _, _ = fixture_state(tmp_path)
    desc = V.adopt(runtime, records['jmbl_fg_max3'][0]); key = V.bind(runtime, desc['id'])['registry_key']
    op = runtime.state.operators.operators[key]
    runtime.state.operators.operators[key] = replace(op, backend=lambda ks, q: {**op.backend(ks, q), 'value': -999})
    out = V.apply(runtime, request(desc, [41, -7, 12]))
    assert out['admitted_id'] is None and out['answer'] is None
    assert any(c.get('reason') == 'WRONG_APPLICATION_VALUE' for c in out['checks'])


def test_actual_fresh_process_host_rebind(tmp_path):
    runtime, records, _, _ = fixture_state(tmp_path)
    desc = V.adopt(runtime, records['jmbl_fg_max3'][0]); V.bind(runtime, desc['id'])
    script = '''import json,sys
from pathlib import Path
from ocm.runtime.ocm_runtime import OCMRuntime
from g1_vessel import CONFIG
import clia_reuse_vessel as V
r=OCMRuntime(Path(sys.argv[1]),config=CONFIG); key=sys.argv[2]
assert not r.state.operators.operators
V.bind(r,key)
print(json.dumps(V.apply(r,{'kind':'clia_apply','program_id':key,'arguments':[41,-7,12]})))'''
    cp = subprocess.run([sys.executable, '-c', script, str(tmp_path), desc['id']], cwd=Path(__file__).parent,
                        text=True, capture_output=True, check=True)
    assert json.loads(cp.stdout)['answer']['value'] == 41


def test_audit_is_read_only_and_names_real_support(tmp_path):
    runtime, records, history, shared = fixture_state(tmp_path)
    desc = V.adopt(runtime, records['jmbl_fg_max3'][0], history=[history]); V.bind(runtime, desc['id'])
    result = V.apply(runtime, request(desc, [41, -7, 12]))
    runtime.revoke([records['jmbl_fg_max3'][1]]); runtime.persist()
    count = len(runtime.events); snapshot = runtime.state.ks.digest()
    audit = V.audit(runtime)
    assert audit['programs'][desc['id']]['liveness'] == 'DEAD'
    assert audit['programs'][desc['id']]['support'] == desc['support']
    assert audit['programs'][desc['id']]['history_only'] == [history]
    assert audit['answers'][result['admitted_id']]['liveness'] == 'DEAD'
    assert len(runtime.events) == count and runtime.state.ks.digest() == snapshot


def test_default_and_expanded_g1_catalogue_use_same_admission(tmp_path, monkeypatch):
    import g1_vessel as G
    a, records, _, _ = fixture_state(tmp_path / 'default')
    b, other, _, _ = fixture_state(tmp_path / 'expanded')
    for record in other.values():
        desc = V.adopt(b, record[0]); V.bind(b, desc['id'])
    calls = []
    def unit_propose(task):
        calls.append(task['task_id'])
        return dict(status='SOLUTION', candidate=UNIT_PROGRAMS[task['task_id']],
                    task_sha256=task['task_sha256'], grammar_id=task['grammar']['id'])
    monkeypatch.setattr(clia_solver, 'propose', unit_propose)
    q = {'kind': 'clia', 'task': load_task('jmbl_fg_max3')}
    plain = G.query(a, q); expanded = V.query(b, q)
    assert plain['status'] == expanded['status'] == 'ADMITTED'
    assert plain['answer'] == expanded['answer'] and plain['claim'] == expanded['claim']
    assert plain['catalogue'] == ['syntax:udpipe1', 'procedure:cvc5']
    assert len(expanded['catalogue']) == 4
    assert calls == ['jmbl_fg_max3', 'jmbl_fg_max3']
    assert expanded['reuse_counters']['application_calls'] == 0
    assert expanded['reuse_counters']['synthesis_dispatches'] == 1
    # SV filters the two apply slots whose descriptor inputs are outside this query graph.
    assert expanded['reuse_counters']['catalogue_visits'] == expanded['catalogue'][:2]
    assert sum(c.get('reason') == 'NOT_APPLICABLE' for c in expanded['checks']) == 1


def test_expanded_syntax_routes_to_existing_observation_gate(tmp_path, monkeypatch):
    import g1_vessel as G
    runtime, records, _, _ = fixture_state(tmp_path)
    for record in records.values():
        desc = V.adopt(runtime, record[0]); V.bind(runtime, desc['id'])
    words = [{'id': 1, 'form': 'widget', 'head': 0, 'deprel': 'root', 'upos': 'NOUN'}]
    monkeypatch.setattr(G, 'predict', lambda tokens, path, digest: {'status': 'PREDICTED', 'words': words, 'model_sha256': digest})
    out = V.query(runtime, {'kind': 'syntax', 'tokens': ['widget']})
    assert out['status'] == 'ADMITTED' and out['claim'] == 'MODEL_SUPPORTED_SYNTAX_OBSERVATION'
    assert out['answer']['words'] == words and len(out['catalogue']) == 4
    assert out['reuse_counters']['catalogue_visits'] == out['catalogue'][:2]
    assert out['reuse_counters']['application_calls'] == out['reuse_counters']['synthesis_dispatches'] == 0

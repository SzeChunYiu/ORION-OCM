"""Commission orchestration controls are mocked: no native proof/search dispatch."""
import hashlib
import json
from pathlib import Path
from unittest.mock import Mock

import pytest
import commission as C


@pytest.fixture
def registered(tmp_path):
    manifest = tmp_path / 'runtime.json'
    manifest.write_text(json.dumps({'lean_root':'/registered/lean', 'shared_libraries':{'mounts':[]},
      'preparation_wall_s':8.0, 'preparation_including_failed_attempts_wall_s':35.0,
      'prior_development_preparations':[{'elapsed_wall_s':9.0}]*3, 'acquisition':{'download_wall_s':None}}))
    return manifest, hashlib.sha256(manifest.read_bytes()).hexdigest(), tmp_path/'commission'


@pytest.fixture
def doubles(monkeypatch):
    calls=[]
    def task(task, registered_sha256, runtime, destination):
        destination=Path(destination); destination.mkdir()
        name=destination.name; calls.append(name)
        if name=='injected_target':
            assert registered_sha256 != hashlib.sha256(C.canonical_task(task)).hexdigest()
            return {'terminal':'CANNOT_CHECK','reason':'ValueError: task differs from separately registered input','worker':None,'checker':None}
        status='EXHAUSTED_REGISTERED_BOUND' if name in ('missing_member','reversed_subset','wrong_witness') else 'CANNOT_CHECK' if name=='max_terms' else 'KERNEL_PASS'
        result = {'terminal':status,'reason':'','worker':{'candidate':['var',0] if status=='KERNEL_PASS' else None,
                'counters':{'applications':24},'used_constants':[0] if status=='KERNEL_PASS' else []},'wall_s':1.0}
        if name=='max_terms':
            result.update(reason='Operational bound: max_terms reached',checker=None,
                          worker_process={'terminal':'COMPLETED','returncode':0,'pid':123,'stderr':''})
            result['worker'].update(status='CANNOT_CHECK',reason=result['reason'],counters={'generated_terms':1},
                                   worker_audit={'guard_sealed':True,'prohibited_events':[]})
        return result
    def stage(candidate,destination):
        if candidate[0] in ('raw','admit'):raise ValueError('unregistered AST constructor or arity')
        if candidate==['const',99]:raise ValueError('unregistered sort, free variable or constant')
        destination=Path(destination); destination.mkdir(parents=True)
        (destination/'Target.lean').write_text('registered target')
        return {'directory':str(destination)}
    def check(stage,runtime,shared_mounts):
        name=Path(stage['directory']).parent.name
        status='REJECTED' if name=='ill_typed' else 'CANNOT_CHECK'
        if name=='missing_checker':
            return {'terminal':status,'reason':'version: incomplete process envelope','phases':[
                {'phase':'version','process':{'pid':None,'terminal':'CANNOT_CHECK',
                 'reason':'FileNotFoundError: '+str(runtime)}}]}
        return {'terminal':status,'reason':'ValueError: checker source identity changed' if name=='corrupted_target' else 'candidate: nonzero tool exit',
                'phases':[] if status=='CANNOT_CHECK' else [{'phase':'candidate'}]}
    monkeypatch.setattr(C,'verify_runtime',lambda runtime: None)
    monkeypatch.setattr(C,'run_task',task); monkeypatch.setattr(C,'stage_candidate',stage)
    monkeypatch.setattr(C,'check_staged',check)
    return calls


def test_exact_matrix_restart_and_complete_source_runtime_bindings(registered,doubles):
    manifest,digest,out=registered
    result=C.commission(manifest,digest,out)
    assert result['terminal']=='MECHANICAL_PROPOSER_COMMISSIONING_PASS',result
    assert len(result['cases'])==14 and len({row['id'] for row in result['cases']})==14
    assert all(row['passed'] for row in result['cases'])
    assert result['restart_equal'] is True
    assert doubles==['original','restart','eq_only','missing_member','reversed_subset','wrong_witness','max_terms','injected_target']
    assert (out/'runtime-manifest.json').read_bytes()==manifest.read_bytes()
    assert result['runtime_sha256']==digest and result['source_files']
    for name,source_digest in result['source_files'].items():
        assert hashlib.sha256((out/'source-snapshot'/name).read_bytes()).hexdigest()==source_digest
    assert result['runtime_cost']['preparation_including_failed_attempts_wall_s']==35.0
    assert len(result['runtime_cost']['prior_development_preparations'])==3
    assert json.loads((out/'commission.json').read_text())['terminal']==result['terminal']


@pytest.mark.parametrize('mode',['missing','wrong_hash','invalid_json'])
def test_bad_runtime_keeps_fixed_denominator_without_dispatch(registered,monkeypatch,mode):
    manifest,digest,out=registered
    if mode=='missing':manifest.unlink()
    elif mode=='wrong_hash':digest='0'*64
    else:
        manifest.write_text('invalid'); digest=hashlib.sha256(manifest.read_bytes()).hexdigest()
    run=Mock(); monkeypatch.setattr(C,'run_task',run)
    result=C.commission(manifest,digest,out)
    assert result['terminal']=='CANNOT_CHECK'
    assert len(result['cases'])==14 and all(row['observed']=='NOT_RUN' for row in result['cases'])
    assert (out/'commission.json').is_file();run.assert_not_called()


def test_existing_output_never_overwritten(registered,doubles):
    manifest,digest,out=registered;out.mkdir();sentinel=out/'keep';sentinel.write_bytes(b'original')
    with pytest.raises(FileExistsError):C.commission(manifest,digest,out)
    assert list(out.iterdir())==[sentinel] and sentinel.read_bytes()==b'original' and doubles==[]


def test_failed_case_is_retained_without_skipping_later_assignments(registered,doubles,monkeypatch):
    original=C.run_task
    def fail_first(*args):
        if Path(args[3]).name=='original':raise RuntimeError('controlled dispatch error')
        return original(*args)
    monkeypatch.setattr(C,'run_task',fail_first)
    result=C.commission(*registered)
    assert result['terminal']=='CANNOT_CHECK'
    assert result['cases'][0]['observed']=='CANNOT_CHECK' and not result['cases'][0]['passed']
    assert 'RuntimeError' in result['cases'][0]['result']['reason']
    assert result['cases'][-1]['observed']=='VALUE_ERROR'


def test_post_dispatch_manifest_drift_stops_remaining_cases(registered,doubles,monkeypatch):
    manifest,digest,out=registered;original=C.run_task
    def drift(*args):
        result=original(*args);manifest.write_bytes(manifest.read_bytes()+b' ');return result
    monkeypatch.setattr(C,'run_task',drift)
    result=C.commission(manifest,digest,out)
    assert result['terminal']=='CANNOT_CHECK'
    assert result['cases'][0]['observed']=='KERNEL_PASS'
    assert all(row['observed']=='NOT_RUN' for row in result['cases'][1:])
    assert doubles==['original']


def test_post_dispatch_snapshot_drift_stops_remaining_cases(registered,doubles,monkeypatch):
    manifest,digest,out=registered;original=C.run_task
    def drift(*args):
        result=original(*args)
        path=next((out/'source-snapshot').glob('*.py'));path.write_bytes(path.read_bytes()+b' ')
        return result
    monkeypatch.setattr(C,'run_task',drift)
    result=C.commission(manifest,digest,out)
    assert result['terminal']=='CANNOT_CHECK' and doubles==['original']
    assert all(row['observed']=='NOT_RUN' for row in result['cases'][1:])


def test_runtime_custody_failure_precedes_dispatch(registered,doubles,monkeypatch):
    def refuse(runtime):raise ValueError('copied runtime drift')
    monkeypatch.setattr(C,'verify_runtime',refuse)
    result=C.commission(*registered)
    assert result['terminal']=='CANNOT_CHECK' and doubles==[]
    assert all(row['observed']=='NOT_RUN' for row in result['cases'])


def test_injected_task_and_original_registration_are_preserved(registered,doubles):
    manifest,digest,out=registered;C.commission(manifest,digest,out)
    original=(out/'declared-inputs/original.json').read_bytes()
    injected=(out/'declared-inputs/injected_target.json').read_bytes()
    binding=json.loads((out/'declared-inputs/injected_target.binding.json').read_text())
    assert original!=injected and binding['registered_sha256']==hashlib.sha256(original).hexdigest()
    assert binding['actual_sha256']==hashlib.sha256(injected).hexdigest()


def test_actual_recipe_schema_does_not_invent_absent_preparation_history(registered,doubles):
    manifest,_,out=registered;runtime=json.loads(manifest.read_text())
    del runtime['preparation_including_failed_attempts_wall_s'];del runtime['prior_development_preparations']
    manifest.write_text(json.dumps(runtime));digest=hashlib.sha256(manifest.read_bytes()).hexdigest()
    result=C.commission(manifest,digest,out)
    assert result['terminal']=='MECHANICAL_PROPOSER_COMMISSIONING_PASS'
    assert result['runtime_cost']['preparation_including_failed_attempts_wall_s'] is None
    assert result['runtime_cost']['prior_development_preparations'] is None


@pytest.mark.parametrize('name',['max_terms','injected_target','missing_checker','corrupted_target','raw_ast'])
def test_unrelated_refusal_never_passes_a_control(registered,doubles,monkeypatch,name):
    original=C._case
    def wrong(which,*args):
        result=original(which,*args)
        if which==name:result['reason']='unrelated source-copy failure'
        return result
    monkeypatch.setattr(C,'_case',wrong)
    result=C.commission(*registered)
    assert result['terminal']=='CANNOT_CHECK'
    assert not next(row for row in result['cases'] if row['id']==name)['passed']
    assert result['cases'][-1]['observed']!='NOT_RUN'

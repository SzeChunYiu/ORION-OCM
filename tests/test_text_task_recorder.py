"""Additive qualification custody controls; synthetic pytest artifacts, no donors."""
import importlib.util
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))


def api():
    assert importlib.util.find_spec('record_text_task_slice'), 'text-task recorder is missing'
    import record_text_task_slice as R
    import text_task_qualification as Q
    return R,Q


@pytest.fixture
def root(tmp_path,monkeypatch):
    R,Q=api()
    for name in ('src','tests/integration','tools','research/ocm-prototype/clia_fixtures'):
        (tmp_path/name).mkdir(parents=True)
    (tmp_path/'pyproject.toml').write_text('[project]\nname="fixture"\n')
    p=tmp_path/'research/ocm-prototype'
    (p/'text_task_slice.py').write_text('import text_task_programs\n')
    (p/'text_task_programs.py').write_text('import clia_tasks\n')
    (p/'clia_tasks.py').write_text('VALUE=1\n')
    (p/'clia_worker.py').write_text('VALUE=1\n')
    (p/'requirements-g1.txt').write_text('pytest==8.3.5\n')
    fixtures={}
    for name in ('jmbl_fg_max3','jmbl_fg_mpg_guard2'):
        f=p/'clia_fixtures'/(name+'.sl');f.write_text('(check-synth)\n')
        fixtures[name]={'file':f.name,'sha256':Q.sha(f)}
    (p/'clia_fixtures/manifest.json').write_text(json.dumps({'fixtures':fixtures}))
    for name in Q.TESTS:(tmp_path/name).write_text('def test_example(): pass\n')
    monkeypatch.setattr(Q,'git_identity',lambda _: {'head':'fixture-head','tree':'fixture-tree'})
    monkeypatch.setattr(Q,'environment',lambda: {'fixture_only':True,'python':sys.version})
    return tmp_path


def successful_gate(argv,root,env,stdout,stderr):
    R,Q=api()
    nodes=[Q.TESTS[0 if i<21 else 1]+'::test_case_'+str(i) for i in range(29)]
    trace={'collected':nodes,'reports':[{'nodeid':n,'when':phase,'outcome':'passed'}
        for n in nodes for phase in ('setup','call','teardown')],'exit_status':0}
    Path(env['OCM_TEXT_TASK_TRACE']).write_text(json.dumps(trace))
    xml=ET.Element('testsuites');suite=ET.SubElement(xml,'testsuite',tests='29',failures='0',errors='0',skipped='0')
    for node in nodes:
        path,name=node.split('::');ET.SubElement(suite,'testcase',classname=path[:-3].replace('/','.'),name=name)
    ET.ElementTree(xml).write(next(x.split('=',1)[1] for x in argv if x.startswith('--junitxml=')))
    stdout.write(b'synthetic custody control only\n')
    return 0


def test_transitive_research_fixture_and_root_identity_are_bound(root):
    R,Q=api();before=Q.snapshot(root)
    assert 'research/ocm-prototype/clia_tasks.py' in before['donor_inventory']
    assert 'research/ocm-prototype/clia_worker.py' in before['donor_inventory']
    assert 'research/ocm-prototype/clia_fixtures/jmbl_fg_max3.sl' in before['donor_inventory']
    p=root/'research/ocm-prototype/clia_tasks.py';p.write_text('VALUE=2\n')
    after=Q.snapshot(root)
    assert Q.identity(before)!=Q.identity(after)
    assert before['root_source_id']==after['root_source_id']  # Historic root scope remains separate.


def test_create_only_full_archive_and_unchanged_scope(root,monkeypatch):
    R,Q=api();monkeypatch.setattr(R,'execute',successful_gate)
    before=Q.snapshot(root);out=root/'qualification'
    assert R.record(root,out,Q.identity(before))==0
    receipt=json.loads((out/'RECEIPT.json').read_text())
    assert receipt['status']=='TEXT_TASK_DONOR_QUALIFIED'
    assert receipt['junit']['tests']==29 and receipt['junit']['skipped']==0
    assert (out/'source.zip').is_file() and (out/'pytest-trace.json').is_file()
    assert Q.verify_archive(out/'source.zip',before)
    assert not (root/'docs/provenance/engineering_revisions/CURRENT_ENGINEERING.json').exists()
    with pytest.raises(FileExistsError):R.record(root,out,Q.identity(before))


@pytest.mark.parametrize('mutation',['skip','missing_call','wrong_file','duplicate','failure'])
def test_incomplete_or_wrong_test_execution_never_qualifies(root,monkeypatch,mutation):
    R,Q=api()
    def bad(*args):
        successful_gate(*args);path=Path(args[2]['OCM_TEXT_TASK_TRACE']);trace=json.loads(path.read_text())
        if mutation=='missing_call':trace['reports']=[r for r in trace['reports'] if r['when']!='call']
        elif mutation=='wrong_file':trace['collected'][0]='tests/test_other.py::test_case_0'
        elif mutation=='duplicate':trace['collected'][1]=trace['collected'][0]
        else:trace['reports'][1]['outcome']='skipped' if mutation=='skip' else 'failed'
        path.write_text(json.dumps(trace));return 0
    monkeypatch.setattr(R,'execute',bad)
    assert R.record(root,root/'bad',Q.identity(Q.snapshot(root)))==1
    assert (root/'bad/FAILED.json').is_file() and not (root/'bad/RECEIPT.json').exists()


def test_source_change_during_execution_keeps_failure_and_raw_artifacts(root,monkeypatch):
    R,Q=api()
    def drift(*args):
        code=successful_gate(*args)
        (root/'research/ocm-prototype/clia_tasks.py').write_text('VALUE=99\n')
        return code
    monkeypatch.setattr(R,'execute',drift)
    assert R.record(root,root/'drift',Q.identity(Q.snapshot(root)))==1
    failed=json.loads((root/'drift/FAILED.json').read_text())
    assert 'changed' in failed['reason']
    assert (root/'drift/junit.xml').is_file() and (root/'drift/stdout.log').is_file()


def test_wrong_frozen_identity_refuses_before_execution(root,monkeypatch):
    R,Q=api();monkeypatch.setattr(R,'execute',lambda *a:pytest.fail('drift launched donor tests'))
    with pytest.raises(ValueError,match='identity'):R.record(root,root/'wrong','0'*64)
    assert not (root/'wrong').exists()


def test_recorder_module_exists():
    api()


def test_malformed_junit_retains_failed_execution(root,monkeypatch):
    R,Q=api()
    def bad_xml(*args):
        successful_gate(*args)
        Path(next(a.split('=',1)[1] for a in args[0] if a.startswith('--junitxml='))).write_text('<broken')
        return 0
    monkeypatch.setattr(R,'execute',bad_xml)
    assert R.record(root,root/'broken',Q.identity(Q.snapshot(root)))==1
    assert (root/'broken/FAILED.json').is_file()


def test_one_file_cannot_supply_all_required_test_count(root,monkeypatch):
    R,Q=api()
    def omitted(*args):
        successful_gate(*args)
        p=Path(args[2]['OCM_TEXT_TASK_TRACE']);trace=json.loads(p.read_text())
        trace['collected']=[n.replace(Q.TESTS[1],Q.TESTS[0]) for n in trace['collected']]
        for report in trace['reports']:report['nodeid']=report['nodeid'].replace(Q.TESTS[1],Q.TESTS[0])
        p.write_text(json.dumps(trace))
        p=Path(next(a.split('=',1)[1] for a in args[0] if a.startswith('--junitxml=')))
        p.write_text(p.read_text().replace('test_text_task_binding','test_text_task_slice'))
        return 0
    monkeypatch.setattr(R,'execute',omitted)
    assert R.record(root,root/'omitted',Q.identity(Q.snapshot(root)))==1


def test_real_pytest_trace_plugin_on_two_nondonor_fixture_tests(root):
    import os
    R,Q=api();out=root/'plugin-control';out.mkdir()
    env=dict(os.environ,PYTHONPATH=str(Path(R.__file__).parent),PYTEST_DISABLE_PLUGIN_AUTOLOAD='1',
             OCM_TEXT_TASK_TRACE=str(out/'pytest-trace.json'))
    argv=[sys.executable,'-m','pytest','-p','record_text_task_slice',*Q.TESTS,'-q',
          '--junitxml='+str(out/'junit.xml')]
    with (out/'stdout').open('xb') as stdout,(out/'stderr').open('xb') as stderr:
        assert R.execute(argv,root,env,stdout,stderr)==0
    trace=json.loads((out/'pytest-trace.json').read_text())
    assert len(trace['collected'])==2
    assert sum(r['when']=='call' and r['outcome']=='passed' for r in trace['reports'])==2
    with pytest.raises(ValueError,match='collection'):Q.validate_execution(out)


def test_archived_source_tampering_never_qualifies(root,monkeypatch):
    import zipfile
    R,Q=api()
    def changed_archive(*args):
        successful_gate(*args)
        archive=Path(args[2]['OCM_TEXT_TASK_TRACE']).with_name('source.zip')
        with zipfile.ZipFile(archive,'a') as out:out.writestr('unregistered.py','pass')
        return 0
    monkeypatch.setattr(R,'execute',changed_archive)
    assert R.record(root,root/'tampered',Q.identity(Q.snapshot(root)))==1
    assert 'archive' in json.loads((root/'tampered/FAILED.json').read_text())['reason']


def test_required_dependency_versions_are_not_advisory(monkeypatch):
    from types import SimpleNamespace
    R,Q=api()
    monkeypatch.setattr(Q.metadata,'distribution',lambda _:SimpleNamespace(version='wrong'))
    with pytest.raises(ValueError,match='dependency version'):Q.environment()

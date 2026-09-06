"""Read-only source/input verification and create-only prospective launch metadata."""
import hashlib
import json
from pathlib import Path
import shlex
import subprocess

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parent/'successor-v2'
REPO = Path('/home/billy/orion-director-work/20260906/ocm-generation-feasibility')
HEAD = 'b03b74905a331bf40af16f1531bb5f2b58821ba2'
ORDER = ['implicit_primitive','explicit_primitive','explicit_macro']


def binding(path):
    path = Path(path)
    return {'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'bytes':path.stat().st_size,'resolved':str(path.resolve())}


def write(path, value):
    with Path(path).open('x') as stream:
        json.dump(value,stream,sort_keys=True,indent=2); stream.write('\n')


def prepare():
    old = json.loads((OLD/'manifest.json').read_text())
    assert subprocess.check_output(['/usr/bin/git','rev-parse','HEAD'],cwd=REPO,text=True).strip() == HEAD
    assert subprocess.check_output(['/usr/bin/git','status','--porcelain'],cwd=REPO) == b''
    assert not (ROOT/'capture-v4').exists()
    selected = {}
    for name, row in old['bindings'].items():
        if ('/generation-env/' in name or '/libpython' in name or name.startswith('/usr/bin/')
                or name.endswith('/clia_worker.py') or name.endswith('/public-task.json')
                or name.endswith('/manual-macro.json')):
            assert binding(name) == row
            selected[name] = row
    previous = json.loads((OLD/'PROPOSAL.json').read_text())
    cases = []
    for row in previous['proposed_cases'][:3]:
        row = dict(row); case = row['case']
        for extension in ('.json','.sl'):
            destination = ROOT/(case+extension)
            with destination.open('xb') as out:
                out.write((OLD/(case+extension)).read_bytes())
            selected[str(destination)] = binding(destination)
        assert binding(ROOT/row['input'])['sha256'] == row['input_sha256']
        assert binding(ROOT/(case+'.sl'))['sha256'] == row['sygus_sha256']
        row['argv'] = row['argv'][:-1]+[str(ROOT/'diagnostic_worker.py'),'--events',
                                      str(ROOT/'capture-v4'/case/'boundaries.jsonl')]
        row.pop('shell_proposal')
        row['role'] = 'PUBLIC_BOUNDARY_LOCALIZATION_NOT_COMPARATIVE_TIMING'
        cases.append(row)
    proposal = {k:previous[k] for k in ('task_id','task_sha256','original_source_sha256','resource_envelope')}
    proposal.update({'schema':'ocm.generation.timeout-localization-proposal.v1',
        'status':'PROPOSED_NOT_EXECUTED','execution_order':ORDER,'proposed_cases':cases,
        'predecessor_proposal_sha256':binding(OLD/'PROPOSAL.json')['sha256'],
        'task_source_preparation_commit':previous['core_commit'],
        'execution_head':HEAD,'cwd':str(REPO),
        'intervention':'Byte-identical quoted-v2 inputs, unchanged native/outer deadlines; replace worker with boundary/statistics observer and enable only three native diagnostic output tags. No algorithm option changes.',
        'scope':'Three nonforced public requests only. Manual macro, no learned claim. Diagnostic output NOT_GRADED; no timing or cognition comparison.',
        'output_tags':{'added':['options-auto','sygus-grammar','sygus-enumerator'],
                       'preserved_in_input':['sygus-sol-gterm'],
                       'routing':'stderr set before observer tags, and unchanged quoted input sets it again.',
                       'effective_getter':'Unavailable in pinned API; successful requested setters recorded, never substituted for observed native emission.'}})
    write(ROOT/'PROPOSAL.json',proposal)
    for p in [ROOT/'diagnostic_worker.py',ROOT/'control.py',ROOT/'native_setup_control.py',
              ROOT/'prepare.py',ROOT/'PROPOSAL.json',ROOT.parent/'capture.py',
              OLD/'PROPOSAL.json',OLD/'manifest.json',
              ROOT/'controls-v2/CONTROL.json',ROOT/'native-setup-v3/SETUP.json']:
        selected[str(p)] = binding(p)
    manifest = {'schema':'ocm.generation-timeout-localization-launch.v1',
        'status':'READY_FOR_ROOT_REGISTRATION_NOT_EXECUTED','execution_head':HEAD,'cwd':str(REPO),
        'scope':proposal['scope'],'proposal':str(ROOT/'PROPOSAL.json'),'execution_order':ORDER,
        'resource_envelope':proposal['resource_envelope'],'watchdog_seconds':24,
        'watchdog_scope':old['watchdog_scope'],'bindings':selected,'versions':old['versions'],
        'runtime_scope':old['runtime_scope'],'intervention':proposal['intervention'],
        'raw_policy':'Separate flushed boundaries.jsonl, command return JSON stdout and native stderr; unchanged existing supervisor seals all. Create-only capture-v4, all three assigned cases once, no retries or fallback.',
        'interpretation':'An unmatched begin localizes an observed public call only; marker absence does not prove a solver phase never ran. Pre-call statistics are not timeout statistics. Hard-killed calls have no final snapshot. Logging/serialization can change execution time; no comparative efficiency inference.',
        'qualification':{'stub_controls':7,'native_setup_completed_commands':3,
             'native_setup_stats_entries':[61,61,61],'retained_native_control_failures':2,
             'actual_public_task_invocations':0,'synth_fun_dispatches':0,'check_synth_dispatches':0,
             'discovery_calls':0,'z3_checks':0,'source_and_control_details':'QUALIFICATION.json'},
        'source_basis':'https://github.com/SzeChunYiu/ORION-OCM/issues/62#issuecomment-5559798070',
        'future_status':'Root registration and explicit launch required.'}
    write(ROOT/'manifest.json',manifest)
    argv = ['/home/billy/orion-director-work/20260906/generation-env/bin/python',
            str(ROOT.parent/'capture.py'),'--manifest',str(ROOT/'manifest.json'),
            '--output',str(ROOT/'capture-v4')]
    write(ROOT/'LAUNCH.json',{'status':'NOT_EXECUTED','manifest_sha256':binding(ROOT/'manifest.json')['sha256'],
                            'argv':argv,'cwd':str(REPO),'command':shlex.join(argv)})
    print(json.dumps({'manifest':binding(ROOT/'manifest.json'),'bindings':len(selected),
                      'proposal':binding(ROOT/'PROPOSAL.json'),'command':shlex.join(argv)}))


if __name__ == '__main__':
    prepare()

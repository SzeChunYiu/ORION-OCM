"""Read-only custody comparisons; no target imports."""
from read_data import *
def check():
    q=load(ROOT/'REQUEST-EXECUTION-01.json'); g=load(ROOT/'ROOT-EXPORT-GATE-01.json')
    s=load(OBS/'START.json'); p=load(OBS/'PROCESS.json'); result=load(OUT/'RESULT.json')
    equal('exact-root-gate',identity(read(ROOT/'ROOT-EXPORT-GATE-01.json'))['sha256'],
          'e03cc44b678c1f3842dac8141e30e7c08e484537e506a351ff0510caff00598f')
    equal('gate-once',g['max_runs'],1); equal('gate-timeout',g['outer_wall_s'],180)
    equal('gate-authorized',g['authorization'],'ROOT_TRAINING_NATIVE_EXPORT_GATE')
    bound(ROOT/'REQUEST-EXECUTION-01.json',g['request'])
    equal('gate-start-identity',s['gate'],identity(read(ROOT/'ROOT-EXPORT-GATE-01.json')))
    equal('requests-at-start-result',s['request'],result['request'])
    equal('requests-at-gate',s['request'],g['request'])
    equal('request-output-copy',load(OUT/'REQUEST.json'),q)
    expected=[q['python']['path'],'-I','-S','-B',str(ROOT/'trace_export.py'),
              str(ROOT/'REQUEST-EXECUTION-01.json'),str(OUT)]
    for name,v in [('gate',g['argv']),('start',s['argv']),('process',p['argv'])]: equal('argv-'+name,v,expected)
    equal('inner-argv',result['argv'],expected[4:])
    equal('outer-child-pid',p['pid'],2048380); equal('inner-child-pid',result['pid'],p['pid'])
    equal('observer-parent',result['ppid'],p['observer_pid']); equal('start-parent',s['observer_pid'],p['observer_pid'])
    equal('process-cwd',p['cwd'],str(ROOT)); equal('result-cwd',result['cwd'],str(ROOT))
    equal('inner-entry',result['entry_file'],str(ROOT/'trace_export.py'))
    equal('inner-python',result['python_executable'],q['python']['path'])
    for key,want in [('exit_code',0),('reaped',True),('timeout',False),('read_errors',{}),
                     ('output_population_ok',True),('terminal','NATIVE_EXPORT_PROCESS_COMPLETED')]: equal('outer-'+key,p[key],want)
    equal('inner-terminal',result['terminal'],'FRESH_NATIVE_EXPORT_CANDIDATE_REQUIRES_ROOT_QUALIFICATION')
    for key,want in [('native_error',None),('trace_error',None),('native_calls',8446),('verified_count',4223),
                     ('trace_unusable',{}),('opportunity_calls',0),('learner_calls',0),('gate_read',True),
                     ('prefix_read',True),('native_module_loaded',True)]: equal('inner-'+key,result[key],want)
    equal('pin-population',len(s['pins']),25)
    equal('unchanged-population',set(p['inputs_unchanged']),set(s['pins'])|{q['gate_path']})
    require('every-outer-input-unchanged',all(v is True for v in p['inputs_unchanged'].values()))
    for path,d in s['pins'].items(): bound(path,d)
    for path,d in g['review_bindings'].items(): bound(path,d)
    equal('source-before',result['sources_before'],q['sources']); equal('source-after',result['sources_after'],q['sources'])
    equal('nine-sources',len(q['sources']),9)
    for path,d in q['sources'].items(): bound(ROOT/path,d)
    for key in ['python','verifier','prefix','release','registry_scope','authority_contract','observer_contract','P0_contracts']:
        bound(q[key]['path'],q[key]); equal('request-in-start-'+key,small(q[key]),s['pins'][q[key]['path']])
    observer=ROOT.parent/'observe_ordinary_export_v1.py'
    bound(observer,g['observer']); equal('reviewed-actual-observer',read(observer),read(ROOT/'REVIEWED-OBSERVER-SOURCE-02.py'))
    equal('observer-contract-gate',g['observer_contract'],q['observer_contract'])
    h=load(ROOT/'HASHES-02.json')
    for name,d in h['files'].items(): bound(ROOT/name,d)
    expected_outputs={'NATIVE-AUTHORITY.json','RESULT.json','CUSTODIAN-UNUSABLE-TRACES.json','REQUEST.json',
       'CUSTODIAN-PROGRESS.jsonl','P0-CONTRACTS.json','TEACHING-PACKET-CANDIDATE.json','P1-INVENTORY.json'}
    equal('output-population',set(p['outputs']),expected_outputs)
    equal('output-directory',set(x.name for x in OUT.iterdir()),expected_outputs)
    equal('output-entries',set(p['output_entries']),expected_outputs)
    for name,d in p['outputs'].items(): require('output-no-symlink-'+name,not (OUT/name).is_symlink()); bound(OUT/name,d)
    for name,d in result['artifacts'].items(): bound(d['path'],d)
    for name in ['stdout','stderr']: bound(OBS/(name+'.log'),p[name])
    equal('copied-P0',read(OUT/'P0-CONTRACTS.json'),read(q['P0_contracts']['path']))
    return q,g,s,p,result

"""Consumer-revival source/retained-data reader; no reviewed code execution."""
from pathlib import Path
import ast,datetime,hashlib,json,sys
R=Path('/home/billy/orion-director-work/20260908/native-typed-wff-consumer-revival-v1')
A=Path('/home/billy/orion-director-work/20260908/native-typed-wff-lifecycle-v1')
O=Path('/home/billy/orion-director-work/20260908/native-ocm-adoption-source-review-v1/typed-wff/lifecycle/consumer-revival')
reads={};checks=[]
def raw(p):
 p=Path(p);b=p.read_bytes();reads[str(p)]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()};return b
def pin(p):raw(p);return reads[str(p)]
def data(p):return json.loads(raw(p))
def ck(n,b):checks.append({'check':n,'pass':bool(b)})
q=data(R/'SOURCE-REVIEW-REQUEST-01.json');f=data(R/'SOURCE-FREEZE.json');rr=data(R/'RUN-REQUEST.json');old=data(A/'SOURCE-REVIEW-REQUEST-02.json')
ck('requested_generation',pin(R/'SOURCE-REVIEW-REQUEST-01.json')=={'bytes':5359,'sha256':'59ad1c031f7bfe3ac3cdbccd6aabe1df36b6f59fe6da054d5185540b3cf97337'})
for rel,key in [('SOURCE-FREEZE.json','source_freeze'),('RUN-REQUEST.json','run_request'),('READ-SCOPE.diff','diff'),('ORIGIN.json','origin'),('PROTOCOL.md','protocol')]:ck('request_pin:'+rel,pin(R/rel)==q[key])
ck('maps_equal',q['sources']==f['sources'] and q['inputs']==f['inputs'])
for rel,expected in q['sources'].items():
 ck('snapshot_and_current_source:'+rel,pin(R/rel)==pin(R/'source-candidate-01'/rel)==expected)
 if rel!='run_b.py':ck('unchanged_from_original:'+rel,expected==old['source_files'][rel] and pin(A/rel)==expected)
ck('pre_repair_B_preserved',pin(R/'source-pre-repair/run_b.py')==old['source_files']['run_b.py']==pin(A/'run_b.py'))
oldb=raw(A/'run_b.py').decode();newb=raw(R/'run_b.py').decode()
ck('B_execution_body_unchanged',oldb.split('    sys.addaudithook(audit);C.AUDIT_READS=opened',1)[1]==newb.split('    sys.addaudithook(audit);C.AUDIT_READS=opened',1)[1])
def fn(text,name):return ast.dump(next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name==name),include_attributes=False)
ck('unchanged_refusal_helpers',all(fn(oldb,n)==fn(newb,n) for n in ['refused','require_native_negative']))
for rel,expected in q['inputs'].items():ck('current_input:'+rel,pin(R/rel)==expected)
for rel in ['PROJECTION.json','B-REQUEST.json','inputs/CLASS-PAYLOAD.json','inputs/PARENT.json','inputs/PREFIX.mm','SOURCE-INPUTS-01.json','LIVE-SOURCE-BASE.json']:ck('historical_bytes:'+rel,pin(R/rel)==pin(A/rel))
ck('same_executable',pin(Path(rr['python']))==rr['python_identity'])
ck('exact_freeze_and_envelopes',rr['source_freeze']==pin(R/'SOURCE-FREEZE.json') and rr['prepared_input_envelope']==pin(R/'B-INPUT.json') and rr['prepared_gate_envelope']==pin(R/'B-GATE.json'))
bi=data(R/'B-INPUT.json');bg=data(R/'B-GATE.json');origin=data(R/'ORIGIN.json');proj=data(R/'PROJECTION.json');claims=data(R/'B-REQUEST.json');ap=data(A/'lifecycle-01/A-PROCESS.json');ares=data(A/'producer-01/RESULT.json');state=data(A/'producer-01/STATE.json')
ck('historical_freeze_not_relabelled',rr['historical_producer_source_freeze']==proj['origin']['source_freeze']==origin['original_source_freeze']==pin(A/'SOURCE-FREEZE.json') and bi['source_freeze']==pin(R/'SOURCE-FREEZE.json') and bi['source_freeze']!=proj['origin']['source_freeze'])
ck('prepared_B_bindings',bi['projection']==rr['projection']==pin(R/'PROJECTION.json') and bi['request']==rr['issued_request']==pin(R/'B-REQUEST.json') and bg['input']==pin(R/'B-INPUT.json') and bg['exited_producer']==pin(A/'lifecycle-01/A-PROCESS.json'))
for key,rel in [('failed_consumer','consumer-01/FAILURE.json'),('original_gate','EXECUTION-GATE.json'),('original_outer_process','outer-01/PROCESS.json'),('original_source_freeze','SOURCE-FREEZE.json'),('producer_process','lifecycle-01/A-PROCESS.json'),('producer_result','producer-01/RESULT.json'),('producer_state','producer-01/STATE.json'),('projection','PROJECTION.json'),('requests','B-REQUEST.json')]:ck('origin_chain:'+key,origin[key]==pin(A/rel))
ck('origin_copies',origin==f['origin'])
ck('clean_A_chain',ap['exit_code']==0 and ap['reaped'] and ap['sources_unchanged'] and ap['request_unchanged'] and ap['result']==pin(A/'producer-01/RESULT.json') and ares['pid']==ap['pid'] and ares['terminal']=='ADMITTED_AND_PERSISTED' and ares['state']==pin(A/'producer-01/STATE.json'))
ck('projection_from_state',proj['witnesses']==state['witnesses'] and proj['origin']['state']==pin(A/'producer-01/STATE.json') and proj['origin']['producer_result']==pin(A/'producer-01/RESULT.json') and proj['origin']['process']==pin(A/'lifecycle-01/A-PROCESS.json'))
ck('unchanged_empty_eligibility',rr['policy']['eligible_method_ids']==proj['eligible_method_ids']==state['eligible_method_ids']==ares['eligible_method_ids']==[])
ck('same_seven_claims',len(claims['claims'])==7 and sum(x['cohort']=='typed' for x in claims['claims'])==6 and sum(x['cohort']=='class_regression' for x in claims['claims'])==1)
for rel,key in [('preflight/check_read_scope.py','source'),('preflight/PROCESS-01.json','process'),('preflight/run-01/RESULT.json','result')]:ck('preflight_pin:'+rel,pin(R/rel)==q['preflight'][key]==rr['preflight'][key])
t=data(R/'preflight/run-01/RESULT.json');p=data(R/'preflight/PROCESS-01.json')
ck('retained_eleven_pass',t['terminal']=='READ_SCOPE_CONTROLS_PASS' and len(t['checks'])==11 and all(x['pass'] for x in t['checks']))
ck('preflight_source_stable',t['sources_before']==t['sources_after']==f['sources'])
ck('preflight_process',p['pid']==t['pid']==1796587 and p['parent_pid']==t['parent_pid']==1796586 and p['exit_code']==0 and p['reaped'])
ck('no_reported_native_bridge_learner_calls',t['native_calls']==t['bridge_calls']==t['learner_calls']==0 and t['forbidden_calls']==[])
opened=t['open_attempts']
for name in ['life_payload','life_requests','life_native']:
 cache='__pycache__/'+name+'.cpython-311.pyc';ix=next(i for i,x in enumerate(opened) if x['path']==cache)
 ck('actual_helper_probe_then_source:'+name,opened[ix]['mode']=='r' and any(x['path']==name+'.py' for x in opened[ix+1:]))
ck('retained_original_failed_probe',t['actual_failed_probe']==data(A/'consumer-01/OPEN-AUDIT-FAILURE.json')['open_attempts'][-1]['path'])
ck('real_engine_probe_recorded',any(x['path'].startswith('engine/') and x['path'].endswith('.pyc') for x in opened))
cachepaths=[R/Path(rel).parent/'__pycache__'/(Path(rel).stem+'.'+sys.implementation.cache_tag+'.pyc') for rel in f['sources']]
ck('pinned_source_caches_absent_at_readback',all(not p.exists() for p in cachepaths))
ck('expected_guard_control_names',set(x['check'] for x in t['checks'])=={'actual_failed_root_probe_and_all_B_helper_imports','actual_engine_cache_probes','declared_absent_read_probe','existing_declared_cache','write_probe','absent_unissued_cache','existing_unissued_cache','unregistered_tag','teaching_path','declared_source_read','existing_cache_symlink'})
ck('same_B_runtime_input_scope',f['b_inputs']==data(A/'SOURCE-FREEZE.json')['b_inputs'])
ck('consumer_only_entry',rr['argv']==[rr['python'],'-I','-S','-B',str(R/'run_b.py'),str(R/'consumer-01')] and data(R/'OUTER-PATHS.json')['argv']==rr['argv'])
entries=sorted(str(p.relative_to(R)) for p in R.rglob('*') if p.is_file())
ck('no_producer_or_discovery_or_supervisor_copied',not any(Path(v).name in ['run_a.py','life_discovery.py','lifecycle.py','TRAINING.json','TRAINING-SUFFIX.mm','FIXTURES.json'] for v in entries))
result={'schema':'independent.typed-consumer-revival-binding-review.v1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'terminal':'SOURCE_AND_RETAINED_CONTROL_BINDINGS_PASS' if all(x['pass'] for x in checks) else 'READER_FINDINGS','checks':checks,'read_scope':reads,'inventory':entries,'scope':'Data/AST/source-byte review only; no project module imported or executed; no native, bridge, learner, matcher or reconstruction call. Fixed PREFIX/PARENT hash-only.','outer_gate_requirements':['Check both prepared B envelope identities against RUN-REQUEST before and after execution.','Check the original exited A process/result/state and retained projection chain.','Preserve original failure and separate nested intervals; no A rerun or reprojection.']}
with (O/'BINDINGS.json').open('x') as out:json.dump(result,out,indent=2,sort_keys=True);out.write('\n')
print(json.dumps({'terminal':result['terminal'],'checks':len(checks),'findings':[x for x in checks if not x['pass']],'identity':pin(O/'BINDINGS.json')}))

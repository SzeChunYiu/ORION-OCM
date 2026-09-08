"""Retained consumer revival outcomes only; no reviewed module imports or execution."""
from pathlib import Path
import copy,datetime,hashlib,json,sys
R=Path('/home/billy/orion-director-work/20260908/native-typed-wff-consumer-revival-v1'); A=Path('/home/billy/orion-director-work/20260908/native-typed-wff-lifecycle-v1')
O=Path('/home/billy/orion-director-work/20260908/native-ocm-adoption-source-review-v1/typed-wff/lifecycle/consumer-revival')
reads={};checks=[]
def raw(p):
 p=Path(p);b=p.read_bytes();reads[str(p)]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()};return b
def pin(p):raw(p);return reads[str(p)]
def data(p):return json.loads(raw(p))
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode()).hexdigest()
def ck(n,b):checks.append({'check':n,'pass':bool(b)})
f=data(R/'SOURCE-FREEZE.json');q=data(R/'RUN-REQUEST.json');g=data(R/'EXECUTION-GATE.json');p=data(R/'outer-01/PROCESS.json');launch=data(R/'outer-01/LAUNCH-INTENT.json');result=data(R/'consumer-01/RESULT.json');review=data(O/'REVIEW.json')
ck('exact_result',pin(R/'consumer-01/RESULT.json')=={'bytes':2909,'sha256':'3a7b861beb9ca4d9fed09a954bc2e53ec7c3fb9b4c2d982a0e64750605eb1bb4'})
ck('exact_process',pin(R/'outer-01/PROCESS.json')=={'bytes':12263,'sha256':'30e1eadfe87f9052b0da0741eccc26e3ceb2c64cf21e0948b0235da5c4ce1e16'})
ck('reviewed_generation',pin(R/'SOURCE-FREEZE.json')==review['source_freeze'] and pin(R/'RUN-REQUEST.json')==review['run_request'])
expected={str(R/rel):v for rel,v in {**f['sources'],**f['inputs']}.items()}
ck('28_current_source_input_files',len(expected)==28)
ck('9_historical_bindings',len(g['historical_bindings'])==9)
expected.update(g['historical_bindings'])
expected.update({str(R/'EXECUTION-GATE.json'):pin(R/'EXECUTION-GATE.json'),str(R/'RUN-REQUEST.json'):pin(R/'RUN-REQUEST.json'),str(R/'SOURCE-FREEZE.json'):pin(R/'SOURCE-FREEZE.json'),q['python']:q['python_identity'],g['review']['path']:{k:g['review'][k] for k in ('bytes','sha256')},str(R/'B-INPUT.json'):q['prepared_input_envelope'],str(R/'B-GATE.json'):q['prepared_gate_envelope']})
proj=data(R/'PROJECTION.json');packet=data(R/'B-REQUEST.json')
for key,name in [('admission','ADMISSION.json'),('discovery','DISCOVERY.json')]:expected[str(A/'producer-01'/name)]=proj['origin'][key]
ck('exact_before_after_custody_population',launch['before']['files']==p['post_custody']['files']==expected)
for path,identity in expected.items():ck('actual_retained_binding:'+path,pin(Path(path))==identity)
ck('prepared_B_envelopes',g['prepared_input_envelope']==q['prepared_input_envelope']==pin(R/'B-INPUT.json') and g['prepared_gate_envelope']==q['prepared_gate_envelope']==pin(R/'B-GATE.json'))
ck('observer_source_launch_binding',launch['observer_source']==pin(R/'OUTER-OBSERVER.py'))
ck('exact_gate_and_entry',g['authorization']=='ROOT_GATE_OPEN' and g['request']==p['request']==pin(R/'RUN-REQUEST.json') and g['source_freeze']==pin(R/'SOURCE-FREEZE.json') and launch['gate']==p['gate']==pin(R/'EXECUTION-GATE.json') and q['argv']==g['argv']==p['argv']==launch['argv'])
ck('fresh_clean_process_result',p['pid']==result['pid']==1829521 and p['parent_pid']==result['parent_pid']==launch['parent_pid']==1829517 and p['exit_code']==0 and p['reaped'] and p['failure'] is None and p['result']==pin(R/'consumer-01/RESULT.json'))
ck('observer_custody_passes',p['bindings_unchanged'] and p['post_custody']['prepared_envelopes_checked'] and p['post_custody']['original_A_exited_and_projection_chain'] and launch['before']['prepared_envelopes_checked'] and launch['before']['original_A_exited_and_projection_chain'])
for key in ['stdout','stderr']:ck('outer_log:'+key,p[key]==pin(R/'outer-01'/(key+'.log')))
ap=data(A/'lifecycle-01/A-PROCESS.json');ar=data(A/'producer-01/RESULT.json');st=data(A/'producer-01/STATE.json');oldlife=data(A/'lifecycle-01/RESULT.json');origin=data(R/'ORIGIN.json')
ck('old_A_clean_before_new_B',ap['exit_code']==0 and ap['reaped'] and ap['result']==pin(A/'producer-01/RESULT.json') and ar['pid']==ap['pid'] and ar['state']==pin(A/'producer-01/STATE.json') and ap['exit_utc']<p['start_utc'] and ap['pid']!=p['pid'])
ck('unchanged_original_projection_request',pin(R/'PROJECTION.json')==pin(A/'PROJECTION.json') and pin(R/'B-REQUEST.json')==pin(A/'B-REQUEST.json') and proj['witnesses']==st['witnesses'])
ck('historical_source_remains_distinct',proj['origin']['source_freeze']==origin['original_source_freeze']==q['historical_producer_source_freeze']==pin(A/'SOURCE-FREEZE.json') and proj['origin']['source_freeze']!=pin(R/'SOURCE-FREEZE.json'))
ck('origin_state_chain',proj['origin']['process']==pin(A/'lifecycle-01/A-PROCESS.json') and proj['origin']['producer_result']==pin(A/'producer-01/RESULT.json') and proj['origin']['state']==pin(A/'producer-01/STATE.json'))
ck('original_failure_preserved',oldlife['terminal']=='LIFECYCLE_FAILED' and pin(A/'lifecycle-01/RESULT.json')==data(O.parent/'ATTEMPT01-REVIEW.json')['lifecycle_result'])
ck('alias_only_terminal_and_inputs',result['terminal']=='TYPED_INTERFACE_QUALIFIED_ALIAS_ONLY' and result['eligible_method_ids']==proj['eligible_method_ids']==ar['eligible_method_ids']==[] and result['alias_witness_ids']==proj['alias_witness_ids'] and result['request']==pin(R/'B-REQUEST.json') and result['projection']==pin(R/'PROJECTION.json'))
recon=data(R/'consumer-01/RECONSTRUCTIONS.json');claims=[x['claim'] for x in packet['claims']]
ck('all_seven_reconstructions',len(recon)==len(claims)==7 and result['typed_reconstructions']==6 and result['class_reconstructions']==1)
for row,item in zip(recon,packet['claims']):
 c=item['claim'];holes=[{'label':h,'statement':v} for h,v in zip(c['holes'],c['premises'])]
 ck('issued_constructor_recipe:'+c['label'],row['label']==c['label'] and row['cohort']==item['cohort'] and row['witness_id']==item['witness_id'] and all(row[k]['proof']==c['proof'] and row[k]['target']==c['query'] and row[k]['hypotheses']==holes for k in ['constructor','recipe']))
 ck('reported_proof_counts:'+c['label'],row['normal_labels']==len(c['proof'])==11 and row['proof_sha256']==digest(c['proof']) and len(row['constructor']['semantic_labels'])==row['recipe']['semantic_applications_expanded']==2)
posit=data(R/'consumer-01/NATIVE-RECONSTRUCTION.json');prefix=posit['verified_labels'][:4095]
ck('current_prefix_matches_A',prefix==data(A/'producer-01/ADMISSION.json')['verified_labels'][:4095])
negative=[]
for mode,leaf in [('reconstruction','NATIVE-RECONSTRUCTION.json'),('wrong_hole','WRONG_HOLE.json'),('wrong_target','WRONG_TARGET.json')]:
 base=R/'consumer-01'/('native-'+mode);x=data(R/'consumer-01'/leaf);req=data(base/'request.json')
 ck(mode+':native_receipt_copy',pin(base/'result.json')==pin(R/'consumer-01'/leaf))
 ck(mode+':exact_request_digest',x['native_calls']==1 and x['claims_sha256']==digest(req['claims']) and x['selected']==[c['label'] for c in req['claims']])
 ck(mode+':exact_native_artifacts',x['log']==pin(base/'native.log') and x['suffix']==pin(base/'suffix.mm') and {k:x['database'][k] for k in ('bytes','sha256')}==pin(base/'database.mm'))
 ck(mode+':prefix_trust_authority',req['authority']['prefix']=={k:x['closed_prefix'][k] for k in ('bytes','sha256')}==f['inputs']['inputs/PREFIX.mm'] and len(x['trusted_assertions'])==96 and digest(x['trusted_assertions'])==req['authority']['trusted_assertions_sha256']=='299ebb0851b93b21a351fba98ad474eefb1298114ad11cf76ac43d8c0fa09a58')
 for k,sp in x['sources'].items():ck(mode+':source:'+k,sp==req['sources'][k] and {z:sp[z] for z in ('bytes','sha256')}==pin(Path(sp['path'])))
 verifylog=[line[8:] for line in raw(base/'native.log').decode().splitlines() if line.startswith('Verify: ')]
 if mode=='reconstruction':
  ck('native_positive_population',req['claims']==claims and x['terminal']=='NATIVE_VERIFIED' and x['error'] is None and x['verified_labels']==prefix+[c['label'] for c in claims] and verifylog==x['verified_labels'] and len(x['traces'])==7)
  for c in claims:
   tr=x['traces'][c['label']];s=tr['source']
   ck('native_exact_typed_trace:'+c['label'],tr['terminal']=='NATIVE_VERIFIED' and s['proof']==c['proof'] and s['statement']==c['query'] and s['essential']==[{'label':h,'statement':v} for h,v in zip(c['holes'],c['premises'])] and s['floating']==[{'label':z['floating_label'],'statement':[z['type'],z['variable']]} for z in c['parameters']] and s['dv']==s['active_dv']==[])
 else:
  expected_claim=copy.deepcopy(claims[0]);key='query' if mode=='wrong_target' else 'premises'
  if key=='query':expected_claim[key]=['|-','-.']+expected_claim[key][1:]
  else:expected_claim[key][0]=['|-','-.']+expected_claim[key][0][1:]
  ck(mode+':only_registered_claim_change',req['claims']==[expected_claim])
  ck(mode+':exact_native_failure_stage',x['terminal']=='NATIVE_REJECTED' and x['error']['stage']=='native_check' and x['error']['pending']==claims[0]['label'] and x['verified_labels']==prefix and verifylog==prefix+[claims[0]['label']] and x['traces']=={})
  negative.append(x)
ck('three_actual_native_calls',result['work']['native_calls']==result['work']['native_wrapper_invocations']==3 and len(negative)==2)
ck('positive_result_identity',result['native_reconstruction']==pin(R/'consumer-01/NATIVE-RECONSTRUCTION.json'))
for row,x in zip(result['native_negative_controls'],negative):ck('reported_exact_negative:'+row['control'],row['error']==x['error'] and row['issued_label']==x['error']['pending'] and row['claims_sha256']==x['claims_sha256'] and row['native_calls']==1 and row['verified_prefix_sha256']==digest(prefix))
ck('nine_structural_refusals',result['structural_controls']==data(R/'consumer-01/STRUCTURAL-CONTROLS.json') and len(result['structural_controls'])==9 and all(x['terminal']=='STRUCTURAL_REFUSAL' for x in result['structural_controls']))
audit=data(R/'consumer-01/OPEN-AUDIT.json');allowed=set(f['sources'])|set(f['b_inputs'])|{'SOURCE-FREEZE.json','RUN-REQUEST.json','EXECUTION-GATE.json','B-INPUT.json','B-GATE.json','B-REQUEST.json','PROJECTION.json'}
caches={str(Path(v).parent/'__pycache__'/(Path(v).stem+'.'+sys.implementation.cache_tag+'.pyc')) for v in f['sources']}
ck('complete_scoped_open_population',audit['status']=='COMPLETED_MAIN_AND_SOURCE_CUSTODY' and len(audit['open_attempts'])==128 and all(x['path'] in allowed|caches for x in audit['open_attempts']))
ck('no_owned_teaching_reads_in_audit',not any('TRAINING' in x['path'] or 'producer-' in x['path'] or 'discovery' in x['path'] for x in audit['open_attempts']))
ck('observed_read_only_cache_probes',all(x['mode']=='r' and x['flags']==524288 for x in audit['open_attempts'] if x['path'] in caches))
ck('absent_cache_at_readback',all(not (R/v).exists() for v in caches))
oldouter=data(A/'outer-01/PROCESS.json');total=oldouter['outer_wall_s']+p['total_observer_wall_s']
result2={'schema':'independent.typed-consumer-revival-outcome-data.v1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'terminal':'RETAINED_CONSUMER_REVIVAL_QUALIFIED_ALIAS_ONLY' if all(x['pass'] for x in checks) else 'READER_FINDINGS','checks':checks,'read_scope':reads,'facts':{'positive_native_proofs':4102,'positive_selected_claims':7,'negative_verified_prefix_proofs_each':4095,'native_calls':3,'eligible_methods':0,'original_lifecycle':'LIFECYCLE_FAILED','original_native_calls':2,'all_actual_native_calls':5},'timing':{'revival_measured_outer_s':p['total_observer_wall_s'],'revival_child_s':p['wall_s'],'original_measured_outer_s':oldouter['outer_wall_s'],'disjoint_outer_window_sum_s':total,'scope':'Revival timer starts after initial observer imports, directory checks, metadata parsing and pin-map setup; includes opening check, launch, child, post-custody and identity reads; final PROCESS serialization excluded. Nested child and wrapper intervals not additive.'},'scope':'Retained results/source/data only; no native, bridge, learner, matcher, reconstruction or target execution by reviewer. Logs corroborate but do not replace source-bound native receipts.'}
with (O/'OUTCOME-DATA.json').open('x') as out:json.dump(result2,out,indent=2,sort_keys=True);out.write('\n')
print(json.dumps({'terminal':result2['terminal'],'checks':len(checks),'findings':[x for x in checks if not x['pass']],'identity':pin(O/'OUTCOME-DATA.json')}))

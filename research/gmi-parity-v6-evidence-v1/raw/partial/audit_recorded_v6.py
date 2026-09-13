from pathlib import Path
import copy, hashlib, importlib.util, json, platform, sys
base=Path('/home/billy/ocm-verify/gmi-scientific-completion-20260913/research/gmi-grand-unification-v1')
helpers=Path('/home/billy/ocm-verify/gmi-parity-custody-20260913/research/gmi-parity-custody-repair-v1')
sys.path.insert(0,str(helpers))
from frozen_contract_v1 import same, require, strict_json, EXPECTED, IDS, FAMILIES, AuditError
from resource_evidence_v6 import validate_resources
harness=base/'nn_nonnn_point_parity3_experiment_v6.py'
prereg_path=base/'NN_NONNN_POINT_PARITY3_PREREG_V6.json'
spec=importlib.util.spec_from_file_location('v6_static',harness)
m=importlib.util.module_from_spec(spec);exec(compile(harness.read_bytes(),str(harness),'exec'),m.__dict__)
prereg=strict_json(prereg_path.read_bytes());m.validate_preregistration(prereg)
f=base/('NN_NONNN_POINT_PARITY3_RESULT_V6_claude-code-remote-container_CPython'+platform.python_version()+'.json')
p=strict_json(f.read_bytes());env=p['environment']
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
same(env['python_version'],platform.python_version(),'version')
same(env['harness_sha256'],sha(harness),'harness binding')
same(env['preregistration_sha256'],sha(prereg_path),'prereg binding')
same(env['candidate_ast_sha256_local'],m.candidate_ast_hashes(),'native AST')
same(env['candidate_source_sha256'],m.candidate_source_hashes(harness),'source segments')
same(p['candidate_identity'],m.candidate_identity_record(),'parent source identity')
same(p['capability'],{cid:{'candidate_id':cid,'family':FAMILIES[cid],'outputs':EXPECTED,'expected':EXPECTED,'correct':8,'total':8,'exact_gate_pass':True} for cid in IDS},'capability')
same(p['null_baseline'],{'outputs':[0]*8,'correct':4,'total':8},'null')
same(p['candidate_universe'],[{'candidate_id':cid,'family':FAMILIES[cid]} for cid in IDS],'universe')
for key in ('measurement_schedule','claim_ceiling','replication_lineage','registered_replication_expectation'):
 same(p[key],prereg[key],'registered '+key)
for key in ('environment_gate_pass','instrumentation_gate_pass','protected_resource_measurement_executed','protected_timing_measurement_executed'):
 same(p[key],True,'gate '+key)
same(p['environment_gate_failures'],[],'environment failures')
# The extra V6 fields are audited independently; unchanged resource core uses
# the independently implemented V5 static checker. This calls no candidates.
q=copy.deepcopy(p);ins=q['instrumentation']
priming=ins.pop('priming_witness_diagnostics');required=ins.pop('priming_was_required_on_this_interpreter')
result=validate_resources(q,m)
same(sorted(priming),sorted(IDS),'priming register')
for cid in IDS:
 expected=copy.deepcopy(ins['witness_diagnostics'][cid])
 if platform.python_version()=='3.13.12':
  n=expected['expected_events_per_call'];expected.update(events_per_call=[0]+[n]*7,total_events=7*n,complete_frames=7,empty_frames=1)
 same(priming[cid],expected,'reported forward priming diagnostics')
same(required,platform.python_version()=='3.13.12','priming diagnostic flag')
controls=[]
for name in ('wrong_trace_output','missing_return','negative_block','wrong_frontier'):
 bad=copy.deepcopy(q)
 if name=='wrong_trace_output':bad['instrumentation']['forward_witnesses'][IDS[0]]['calls'][0]['output']=1
 elif name=='missing_return':bad['instrumentation']['reverse_witnesses'][IDS[1]]['calls'][0]['returned']=False
 elif name=='negative_block':bad['measurements'][IDS[0]][0]['wall_block_ns']=-1
 else:bad['frontier_candidate_ids']=[IDS[0]]
 try:validate_resources(bad,m)
 except AuditError:controls.append(name)
 else:raise RuntimeError('missed malformed control '+name)
print(json.dumps({'status':'V6_RECORDED_EVIDENCE_STATIC_PASS','packet':f.name,'packet_sha256':sha(f),'harness_sha256':sha(harness),'preregistration_sha256':sha(prereg_path),'python':platform.python_version(),'frontier_candidate_ids':result['frontier_candidate_ids'],'terminal':result['terminal'],'opcode_counts':result['opcode_counts'],'capability_cases':32,'complete_recorded_frames':64,'timed_blocks':128,'malformed_controls_rejected':controls,'candidate_calls_executed':0,'timing_rerun':False,'custody_authenticated':False,'priming_raw_traces_available':False},indent=2,sort_keys=True))

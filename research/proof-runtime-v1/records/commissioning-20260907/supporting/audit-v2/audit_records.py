"""Read-only retained-record audit; standard library only, no application imports."""
from pathlib import Path
import ast, base64, collections, datetime, hashlib, json, os
BASE=Path('/home/billy/orion-director-work/20260907'); R=BASE/'proof-runtime-commissioning-20260907'; OUT=Path(__file__).parent
raw=lambda v:json.dumps(v,sort_keys=True,separators=(',',':')).encode()
digest=lambda b:hashlib.sha256(b).hexdigest()
sha=lambda p:digest(Path(p).read_bytes())
load=lambda p:json.loads(Path(p).read_bytes())
def save(name,v):
 with (OUT/name).open('x') as f:f.write(json.dumps(v,sort_keys=True,indent=2)+'\n')
issues=[]
def check(ok,label):
 if not ok:issues.append(label)
result=load(R/'result.json'); frozen=load(R/'freeze.json'); parent=load(R/'parent.json'); reg=load(R/'issuer/registration.json')
check(result['terminal']=='PROOF_RUNTIME_LIFECYCLE_COMMISSIONING_PASS','top terminal')
check(result['freeze_sha256']==sha(R/'freeze.json'),'freeze binding')
check(frozen['runtime_sha256']==result['runtime_sha256']==sha(R/'runtime-manifest.json')==sha(frozen['runtime_manifest'])=='93aa17a738a8511bbb8996eff91e81da0ec5868db50d0f81ab26809e38661894','runtime bindings')
check(frozen['task_sha256']==sha(R/'registered-task.json'),'task hash')
for group in ('sources','python','inputs_and_snapshot'):
 for p,h in frozen[group].items():check(Path(p).is_file() and sha(p)==h,group+': '+p)
check({str(p) for p in (R/'source-snapshot').rglob('*') if p.is_file()}=={p for p in frozen['inputs_and_snapshot'] if p.startswith(str(R/'source-snapshot')+'/')},'exact snapshot membership')
module=ast.parse((R/'source-snapshot/research/proof-runtime-v1/lifecycle.py').read_text())
expected=next(ast.literal_eval(n.value) for n in module.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PHASES' for t in n.targets))
check(len(expected)==24 and tuple(x['name'] for x in result['phases'])==expected,'24 exact phase identities')
phases={x['name']:load(R/x['record']) for x in result['phases']}; allowed=frozen['sources']|frozen['python']
def imports(mapping,label):
 for n,p in mapping.items():check(p in allowed and sha(p)==allowed[p],label+' origin '+n)
check(parent['flags']=={'dont_write_bytecode':1,'isolated':1,'no_site':1} and parent['executable']==frozen['python_executable'],'parent executable/flags');imports(parent['imports'],'parent')
for name,p in phases.items():
 check(p['name']==name and p['passed'] is True and p['wall_s']>=0,'phase '+name);imports(p['parent_imports'],name)
routes=result['routes'];a=reg['discovery_id'];s=reg['environment_evidence_id'];processes=[];route_summary=[]
check(len(routes)==2 and len({x['run_id'] for x in routes})==len({x['run_evidence_id'] for x in routes})==2,'distinct routes')
for label,route in zip(('B','C'),routes):
 session=R/('session-'+label);solved=phases['solve_'+label]['result'];answer=solved['solve']['answer'];h=route['handle'];k=h['checker'];stage=Path(k['stage']['directory'])
 check(solved['terminal']=='ADMITTED' and solved['solve']['decision']=='ANSWER','actual solve '+label)
 check(raw(route['candidate'])==raw(answer['candidate']) and route['run_id']==solved['run_id'] and h['proposal_id']==answer['proposal_id'],'exact solve binding '+label)
 check(route['task_sha256']==h['task_sha256']==answer['task_sha256']==frozen['task_sha256'],'task '+label)
 check(route['environment_id']==h['environment_id']==answer['environment_id']==reg['environment_id'],'environment '+label)
 check(sha(h['record_path'])==h['record_sha256'] and sha(answer['record_path'])==answer['record_sha256'],'receipt hashes '+label)
 check(raw({key:v for key,v in h.items() if key != 'record_sha256'})==raw(load(h['record_path'])),'raw handle '+label)
 check(k['terminal']==h['terminal']=='KERNEL_PASS' and k['fresh_kernel_replay'] is True and k['axioms']==[],'fresh empty-axiom pass '+label)
 check(k['formal_target']=='F0Target.statement' and k['target_sha256']=='0694094c1851d5fb72827f4af8a5de0e7d5fd14b646ad9926319f573206273ce','fixed target '+label)
 check(sha(stage/'Candidate.olean')==k['compiled_proof_sha256'],'compiled proof '+label)
 for name,hash_ in k['stage']['files'].items():check(sha(stage/name)==hash_,'stage '+label+'/'+name)
 check(sha(stage/'candidate.json')==h['candidate_sha256']==digest(raw(route['candidate'])+b'\n'),'candidate bytes '+label)
 for item in route['items']:
  w=item['atom']['warrant'];support=sorted([repr(route['run_evidence_id']),repr(s)])
  check(w['lower']==w['upper']==[support] and repr(a) not in support,'B/C correctness excludes A '+label)
 for x in route['artifacts']:check(Path(x['path']).stat().st_size==x['bytes'] and sha(x['path'])==x['sha256'],'artifact '+x['path'])
 for tree in route['artifact_trees']:
  root=Path(tree['root']);check({str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file()}==tree['files'],'artifact tree '+str(root))
 worker=load(next(session.glob('proposal-*/worker-process.json')));processes.append(('worker_'+label,worker));native=json.loads(base64.b64decode(worker['stdout_base64']))
 check(raw(native['candidate'])==raw(route['candidate']),'native worker candidate '+label)
 audit=native['worker_audit'];check(audit['guard_sealed'] is True and audit['prohibited_events']==[],'worker guard '+label)
 check(audit['constant_occurrences']['proof_term']=={} and native['used_constants']==[0],'no proof-lemma use '+label)
 for imp in audit['imported_modules']:
  origin=imp['origin'];check(origin in ('built-in','frozen','trusted-entrypoint') or origin.startswith('/python/lib/python3.11/') or origin in ('/app/f0_search.py','/app/f0_terms.py','/app/worker_guard.py'),'worker origin '+origin)
 check([x['phase'] for x in k['phases']]==['version','foundation','target','candidate'],'fresh checker sequence '+label)
 processes.extend((label+'_'+x['phase'],x['process']) for x in k['phases'])
 check(k['phases'][-1]['process']['stdout']=="'OCMMechanicalProof.constructed' does not depend on any axioms\n",'candidate axiom output '+label)
 check(len(list(session.glob('proposal-*')))==len(list(session.glob('check-*')))==len(list(session.glob('authenticate-*')))==1,'exact session dispatch count '+label)
 route_summary.append({'label':label,'run_id':route['run_id'],'run_evidence_id':route['run_evidence_id'],'proposal_id':h['proposal_id'],'candidate_sha256':h['candidate_sha256'],'candidate_lean_sha256':sha(stage/'Candidate.lean'),'compiled_sha256':k['compiled_proof_sha256'],'axioms':k['axioms'],'counters':native['counters']})
for name,status in (('cold_live','LIVE'),('cold_B_open','OPEN'),('cold_final','LIVE')):
 p=phases[name]['result'];child=p['result'];processes.append((name,p));imports(child['imports'],name)
 check(child['pid']==p['pid'] and child['read_only'] is True and child['session_bound'] is False and child['host_operators']==[] and child['executable_operators']==[] and child['imports_bound'] is True,'cold data-only '+name)
 check(child['status']['terminal']==status and p['argv'][1:4]==['-I','-S','-B'] and p['argv'][-1]==result['freeze_sha256'],'cold launch/status '+name)
process_summary=[]
for name,p in processes:
 check(p['terminal']=='COMPLETED' and type(p['returncode']) is int and p['returncode']==0 and p['stderr']=='','clean process '+name)
 check(p['cleanup']['reaped'] is True and p['cleanup']['group_absent'] is True,'cleanup '+name)
 for stream in ('stdout','stderr'):
  data=base64.b64decode(p[stream+'_base64']);check(data.decode('utf-8')==p[stream],'raw bytes '+name+' '+stream)
  if stream+'_sha256' in p:check(digest(data)==p[stream+'_sha256'] and len(data)==p[stream+'_bytes'],'raw digest '+name+' '+stream)
 try:os.killpg(p['pid'],0);absent=False
 except ProcessLookupError:absent=True
 check(absent,'group present '+name);process_summary.append({'name':name,'pid':p['pid'],'wall_s':p['wall_s'],'cleanup':p['cleanup'],'group_absent_at_audit':absent})
check(len({p['pid'] for p in process_summary})==13,'13 distinct process IDs')
status_expected={'B_live':'LIVE','restore_B':'LIVE','B_withdrawn':'OPEN','B_reinstated':'LIVE','discovery_withdrawn':'LIVE','discovery_reinstated':'LIVE','two_routes':'LIVE','B_withdrawn_C_live':'LIVE','both_withdrawn':'OPEN','both_reinstated':'LIVE','environment_withdrawn':'OPEN','environment_reinstated':'LIVE'}
for name,terminal in status_expected.items():
 value=phases[name]['result'];status=value.get('status',value);check(status['terminal']==terminal and status['applicable'] is (name!='discovery_withdrawn'),'A/B/C/S outcome '+name)
 if 'evidence' in value:check(value['no_new_evidence_or_dispatch'] is True,'revision no dispatch '+name)
ledgers={}
for folder in ('ocm','issuer'):
 rows=[json.loads(line) for line in (R/folder/'ledger.jsonl').read_text().splitlines()];previous='0'*64
 for i,row in enumerate(rows):
  check(row['sequence']==i and row['prev_hash']==previous and row['entry_hash']==digest(raw({k:v for k,v in row.items() if k!='entry_hash'})),'ledger chain '+folder+str(i));previous=row['entry_hash']
 ledgers[folder]=rows
ocm_events=[x['payload'] for x in ledgers['ocm'] if x['kind']=='OCM_EVENT'];previous='0'*64
for i,e in enumerate(ocm_events,1):
 check(e['sequence']==i and e['prev_hash']==previous and e['event_hash']==digest(raw({k:v for k,v in e.items() if k not in ('event_hash','event_id')})),'event chain '+str(i));previous=e['event_hash']
check([x['kind'] for x in ledgers['issuer']]==['REGISTERED','PREPARED','COMMITTED','PREPARED','COMMITTED'],'two issuer commits')
actual_revisions=[(e['event_type'],e['payload']['evidence']) for e in ocm_events if e['event_type'] in ('EVIDENCE_REVOKED','EVIDENCE_REINSTATED')]
expected_revisions=[('EVIDENCE_REINSTATED' if n in ('B_reinstated','discovery_reinstated','both_reinstated','environment_reinstated') else 'EVIDENCE_REVOKED',phases[n]['result']['evidence']) for n in expected if isinstance(phases[n]['result'],dict) and 'evidence' in phases[n]['result']]
check(actual_revisions==expected_revisions,'exact revision event schedule')
files=[p for p in sorted(R.rglob('*')) if p.is_file()]
inventory=[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p),'retention':'metadata_only' if p.suffix=='.olean' or '__pycache__' in p.parts else 'raw'} for p in files];save('RAW_INVENTORY.json',inventory)
summary={'schema':'ocm.proof-runtime-native-record-audit.v1','audited_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'raw_root':str(R),'terminal':'RECORD_AUDIT_PASS' if not issues else 'RECORD_AUDIT_FAILED','issues':issues,'result_sha256':sha(R/'result.json'),'freeze_sha256':sha(R/'freeze.json'),'runtime_sha256':frozen['runtime_sha256'],'parent_sha256':sha(R/'parent.json'),'source_bindings':len(frozen['sources']),'python_bindings':len(frozen['python']),'input_snapshot_bindings':len(frozen['inputs_and_snapshot']),'phase_count':len(phases),'routes':route_summary,'processes':process_summary,'ledger_rows':{k:len(v) for k,v in ledgers.items()},'ocm_event_counts':dict(collections.Counter(e['event_type'] for e in ocm_events)),'discovery_A':a,'environment_S':s,'outer_wall_s':result['outer_wall_s'],'process_cost_sha256':sha(BASE/'proof-runtime-native-process-cost.txt'),'external_log_sha256':sha(BASE/'proof-runtime-native.log'),'inventory_sha256':sha(OUT/'RAW_INVENTORY.json'),'retention':{kind:{'files':sum(x['retention']==kind for x in inventory),'bytes':sum(x['bytes'] for x in inventory if x['retention']==kind)} for kind in ('raw','metadata_only')},'inventory_total_files':len(inventory),'inventory_total_bytes':sum(x['bytes'] for x in inventory),'audit_script_sha256':sha(__file__),'scope':'Standard-library read-only byte/hash/record audit, no OCM restore, solver, Lean, test or proof execution. Auditor implemented lifecycle; a separate agent independently reviewed implementation. Metadata-only .olean archive is an evidence bundle, not directly operable original custody state.'}
save('AUDIT.json',summary)
print(json.dumps({k:v for k,v in summary.items() if k not in ('processes','routes','scope')},indent=2))

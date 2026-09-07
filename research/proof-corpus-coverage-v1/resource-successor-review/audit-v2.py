"""Independent retained-data audit only; no imported product code or dispatch."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET,datetime
B=Path('/home/billy/orion-director-work/20260907')
R=B/'proof-corpus-resource-successor-qualification-20260907-v1'
D=B/'resource-dispatch-successor-development-v1'
P=B/'ocm-proof-corpus-coverage/research/proof-corpus-coverage-v1'
O=Path(__file__).parent
def read(p):return json.loads(Path(p).read_bytes())
def record(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
checked={}
def verify(v,p=None):
 p=Path(p or v['path']);r=record(p)
 assert (r['bytes'],r['sha256'])==(v['bytes'],v['sha256']),str(p)
 checked[str(p)]=r
 return p
def refs(v):
 if isinstance(v,dict):
  if {'path','bytes','sha256'}<=v.keys():verify(v)
  for x in v.values():refs(x)
 elif isinstance(v,list):
  for x in v:refs(x)
def tree(p):
 return {str(f.relative_to(p)):record(f) for f in sorted(p.rglob('*')) if f.is_file() and not f.is_symlink()}
before=tree(R)
f=read(R/'SOURCE_FREEZE.json');assert f['count']==len(f['files'])==22
assert record(R/'SOURCE_FREEZE.json')['sha256']=='a4d30369035cd8d483293b8295418d1158d50772f6358875956e5fe1b1dcd758'
for n,v in f['files'].items():
 verify(v,v['origin']);verify(v,v['snapshot'])
 assert Path(v['snapshot'])==R/'source'/n
reg=read(R/'REGISTRATION.json');res=read(R/'RESULT.json');refs(reg)
names=['envelope','policy','plugin-allowed','plugin-denied','cpu','memory','pids','tree','spool','wall','file-size','host-interruption']
assert [v['id'] for v in reg['cases']]==[v['case'] for v in res['rows']]==names
assert reg['fixed_denominator']==res['assigned']==res['passed']==12
assert res['terminal']=='AUTHORED_RESOURCE_PROFILE_CONTROLS_PASSED'
lineage=read(R/'LINEAGE.json');verify(lineage['recipe'],lineage['recipe']['origin'])
assert (R/'qualify.py').read_bytes()==Path(lineage['recipe']['origin']).read_bytes()
stats=[];loaded=0;raw=0
for plan,row in zip(reg['cases'],res['rows']):
 name=row['case'];c=R/'cases'/name
 assert row['status']=='PASS' and row==read(c/'assessment.json')
 verify(row['receipt']);r=read(row['receipt']['path']);d=r['dispatch'];refs(r)
 assert d==read(c/'run/dispatch/resource-receipt.json')
 assert r==read(c/'host.stdout') and (c/'host.stderr').read_bytes()==b''
 assert r['schema']=='ocm.f1.build-profile-receipt.v2' and d['schema']=='ocm.f1.resource-receipt.v2'
 assert r['dispatch_state']==d['dispatch']['state']=='STARTED' and d['dispatch']['attempted'] is True
 assert d['dispatch']['pid']==d['pid'] and not Path('/proc',str(d['pid'])).exists()
 assert d['evidence_complete'] is True and d['evidence_errors']==[]
 assert all(d['cleanup'][k] is True for k in ['reaped','members_empty','controllers_removed'])
 assert r['policy_cleanup']['removed'] is True and r['post_input_custody']=='UNCHANGED'
 assert d['final_resources']['members']==[] and all(not Path(x).exists() for x in d['controller_paths'].values())
 assert set(d['raw'])=={'stdout.bin','stderr.bin','samples.jsonl'}
 raw+=len(d['raw'])
 for n,v in r['driver_sources'].items():
  expected=f['files'][n+'.py']
  assert v['path']==expected['snapshot'] and v['sha256']==expected['sha256'] and v['bytes']==expected['bytes']
  loaded+=1
 for n,v in d['helper_loaded_sources'].items():assert v['sha256']==f['files'][n]['sha256']
 limits=read(c/'limits.json');assert limits==plan['limits']
 assert all(d['limits'][k]==v for k,v in limits.items() if k!='wall_s')
 assert 0<d['limits']['wall_s']<=limits['wall_s']
 for key,limit in [('memory.limit_in_bytes','memory_bytes'),('memory.memsw.limit_in_bytes','memsw_bytes'),('cpu.cfs_quota_us','cpu_quota_us'),('cpu.cfs_period_us','cpu_period_us'),('pids.max','pids')]:
  assert d['controller_readback'][key]==d['final_resources'][key]==limits[limit]
 proc=read(c/'host-process.json')
 assert proc['environment']=={} and proc['argv'][:4]==[reg['python']['path'],'-I','-S',str(R/'source/resource_boot.py')]
 assert proc['returncode']==(0 if r['terminal']=='COMPLETED' else 2)
 assert proc['wall_s']>=r['wall_through_cleanup_s']>=d['wall_through_cleanup_s']>=0
 out=(c/'run/dispatch/stdout.bin').read_bytes()
 if name=='envelope':assert b'(enforce)' in out and d['initial']['available_memory_bytes']>=limits['min_available_bytes'] and d['initial']['free_bytes']>=limits['min_free_bytes']
 if name=='policy':assert all(s in out for s in [b'source_write=-1 errno=30',b'network=-1 errno=13',b'plugin_map=DENIED errno=13',b'unexpected_exec=DENIED errno=13'])
 if name=='plugin-allowed':assert b'dlopen=ALLOWED value=17' in out
 if name=='plugin-denied':assert b'dlopen=DENIED' in out
 if name=='cpu':assert d['final_resources']['cpu.stat']['nr_throttled']>0
 if name=='tree':assert b'detached-child=' in out
 expected={'memory':'MEMORY_LIMIT','pids':'PID_LIMIT','spool':'OWNED_BYTES','wall':'WALL_DEADLINE'}
 if name in expected:assert r['terminal']=='RESOURCE_STOP' and d['reason']==expected[name] and d['first_stop'] is not None
 elif name=='file-size':assert r['terminal']==d['primary_outcome']['terminal']=='COMMAND_FAILED' and d['returncode']==153 and len(out)==65536
 elif name=='host-interruption':assert r['terminal']=='INTERRUPTED' and d['error']['class']=='InterruptedError' and b'before-sleep' in out
 else:assert r['terminal']=='COMPLETED' and d['returncode']==0
 stats.append({'case':name,'terminal':r['terminal'],'primary':d['primary_outcome']['terminal'],'reason':d['reason'],'returncode':d['returncode'],'pid':d['pid'],'current_pid_and_controller_paths_absent':True,'overshoot_bytes':d['overshoot_bytes'],'resource_wall_s':d['wall_through_cleanup_s'],'profile_wall_s':r['wall_through_cleanup_s']})
xml=ET.parse(R/'focused-tests.xml').getroot()
suites=list(xml.iter('testsuite'));assert len(suites)==1
a=suites[0].attrib
assert (a['tests'],a['failures'],a['errors'],a['skipped'])==('62','0','0','0')
for n in ['focused-process.json','qualification-process.json']:assert read(R/n)['returncode']==0
assert (R/'focused.stderr').read_bytes()==(R/'qualification.stderr').read_bytes()==b''
nonzero=[]
for p in sorted((R/'focused-cases').glob('test_nonzero_primary_survives_*/out/resource-receipt.json')):
 if p.parent.parent.is_symlink():continue
 j=read(p);assert j['returncode']==7 and j['primary_outcome']['terminal']=='COMMAND_FAILED' and j['dispatch']['state']=='STARTED'
 nonzero.append({'receipt':record(p),'terminal':j['terminal'],'primary':j['primary_outcome'],'cleanup':j['cleanup']})
assert [x['terminal'] for x in nonzero]==['COMMAND_FAILED','EVIDENCE_FAILED','CLEANUP_INCOMPLETE']
u=read(R/'focused-cases/test_launch_exception_does_not0/out/resource-receipt.json')
assert u['dispatch']['state']=='ATTEMPTED_UNKNOWN' and u['cleanup']['reaped'] is False and u['primary_outcome']['terminal']=='DISPATCH_UNCERTAIN'
hist=[]
for x in sorted(D.rglob('tests.xml')):
 for e in ET.parse(x).getroot().iter('testsuite'):hist.append({'xml':record(x),**e.attrib})
assert any(int(v['failures'])>0 for v in hist)
hosts=read(R/'HOST-INPUTS.json');assert len(hosts['files'])==11;refs(hosts)
old=P/'resource-records';seal=read(old/'SEAL.json')
assert record(old/'SEAL.json')['sha256']=='2457516e82e1b07062360655dc0dfbce772f3b72aa16379bcfadb23eb6ae00e0'
for n,v in seal['files'].items():verify(v,old/n)
assert record(P/'resource_evidence.py')['sha256']=='b6d0909df6c6d3ee8818a548b09a8b53f20ded184617340a44aaa3723a762703'
assert record(P/'test_resource_evidence.py')['sha256']=='0cc4d8859148dfb15749df112d13985eb4cac1cc141afcc03895aff07afb98de'
assert before==tree(R),'qualification changed during read-only audit'
out={'schema':'ocm.f1.resource-successor-independent-audit.v1','terminal':'RETAINED_RECORD_AUDIT_PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'result':record(R/'RESULT.json'),'source_freeze':record(R/'SOURCE_FREEZE.json'),'scope':'Read-only actual records and file bindings; no tests, resource/native/corpus dispatch, archive extraction or guard execution. Not a full host/runtime closure or universal security assurance.','source_count':22,'loaded_source_occurrences':loaded,'matrix':stats,'focused_tests':dict(a),'nonzero_controls':nonzero,'launch_uncertainty_control':'Confirmed; no reaped/no-dispatch claim','host_inputs_rehashed':11,'raw_stream_bindings':raw,'historical_seal':record(old/'SEAL.json'),'historical_package_files':len(seal['files']),'historical_guard_unchanged':True,'development_xml_history':hist,'verified_unique_file_bindings':len(checked),'qualification_inventory_count':len(before),'qualification_inventory_bytes':sum(v['bytes'] for v in before.values()),'qualification_unchanged_during_audit':True,'cost_scope':'Nested profile/resource durations are not summed. Disk stop is sampled and spool overshoot is retained. Full stdlib/kernel installation and preparation costs are outside these process timings.','package_guard_audit':'Not performed by this audit'}
with (O/'AUDIT.json').open('x') as f:json.dump(out,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps({'audit':record(O/'AUDIT.json'),'matrix':len(stats),'tests':a,'sources':22,'bindings':len(checked),'qualification_files':len(before)}))

from pathlib import Path
import os,json,hashlib,time,datetime,subprocess,traceback
r=Path('/home/billy/orion-director-work/20260908/native-typed-wff-consumer-revival-v1'); out=r/'outer-01'
def ident(p):
 b=Path(p).read_bytes(); return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p): return json.loads(Path(p).read_text())
def write(p,v):
 with Path(p).open('x') as f:
  json.dump(v,f,sort_keys=True,indent=2,allow_nan=False); f.write('\n'); f.flush(); os.fsync(f.fileno())
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
assert not list(out.iterdir()),'OUTER_ALREADY_USED'
assert not (r/'consumer-01').exists(),'CONSUMER_ALREADY_EXISTS'
gate_pin={'bytes':3754,'sha256':'f7661d4ed943c6f7dfb628723acefb9d46a0832d70eedf08e6c73777a3279eed'}
assert ident(r/'EXECUTION-GATE.json')==gate_pin
g=read(r/'EXECUTION-GATE.json'); q=read(r/'RUN-REQUEST.json'); f=read(r/'SOURCE-FREEZE.json'); origin=read(r/'ORIGIN.json')
assert g['authorization']=='ROOT_GATE_OPEN'
assert q['argv']==g['argv']==read(r/'OUTER-PATHS.json')['argv']
assert g['request']=={'bytes':2655,'sha256':'ef6d300c02eb29944d224dbac5e220afadc73295cb457685a1a665295ba552f9'}
pins={str(r/'EXECUTION-GATE.json'):gate_pin,str(r/'RUN-REQUEST.json'):g['request'],str(r/'SOURCE-FREEZE.json'):g['source_freeze'],q['python']:q['python_identity'],g['review']['path']:{k:g['review'][k] for k in ('bytes','sha256')}}
for table in ('sources','inputs'):
 for name,identity in f[table].items():pins[str(r/name)]=identity
assert len(f['sources'])+len(f['inputs'])==g['frozen_bindings_checked']==28
assert len(g['historical_bindings'])==9
pins.update(g['historical_bindings'])
for name,key in [('B-INPUT.json','prepared_input_envelope'),('B-GATE.json','prepared_gate_envelope')]:
 assert g[key]==q[key];pins[str(r/name)]=q[key]
old=Path(origin['original_root'])
for key,p in [('admission',old/'producer-01/ADMISSION.json'),('discovery',old/'producer-01/DISCOVERY.json')]:
 pins[str(p)]=read(r/'PROJECTION.json')['origin'][key]
def check():
 actual={p:ident(p) for p in pins}
 assert actual==pins,'CUSTODY_MISMATCH'
 assert (r/'PROJECTION.json').read_bytes()==(old/'PROJECTION.json').read_bytes()
 assert (r/'B-REQUEST.json').read_bytes()==(old/'B-REQUEST.json').read_bytes()
 ap=read(old/'lifecycle-01/A-PROCESS.json'); ar=read(old/'producer-01/RESULT.json'); po=read(r/'PROJECTION.json')['origin']
 assert ap['exit_code']==0 and ap['reaped'] and ap['sources_unchanged'] and ap['request_unchanged'] and ap['failure'] is None
 assert ar['pid']==ap['pid'] and ar['terminal']=='ADMITTED_AND_PERSISTED'
 assert ap['result']==po['producer_result']==origin['producer_result']
 assert ar['state']==po['state']==origin['producer_state']
 assert po['process']==origin['producer_process']
 assert po['source_freeze']==origin['original_source_freeze']==q['historical_producer_source_freeze']
 assert q['projection']==origin['projection'] and q['issued_request']==origin['requests']
 assert ar['eligible_method_ids']==[]
 return {'files':actual,'original_A_exited_and_projection_chain':True,'prepared_envelopes_checked':True}
begin=time.perf_counter(); cbegin=time.process_time(); start=utc()
before=check(); prewall=time.perf_counter()-begin
write(out/'LAUNCH-INTENT.json',{'argv':q['argv'],'utc':utc(),'parent_pid':os.getpid(),'gate':gate_pin,'before':before,'preflight_wall_s':prewall,'observer_source':ident(r/'OUTER-OBSERVER.py')})
rec={'schema':'native.typed-consumer-outer-process.v1','argv':q['argv'],'parent_pid':os.getpid(),'start_utc':utc(),'gate':gate_pin,'request':g['request'],'preflight_wall_s':prewall,'cost_scope':'child wall and wait4 resources separate from complete observer through post-custody; record serialization excluded','original_A_replayed':False}
child=None;t=time.perf_counter()
try:
 with (out/'stdout.log').open('xb') as stdout,(out/'stderr.log').open('xb') as stderr:
  child=subprocess.Popen(q['argv'],stdout=stdout,stderr=stderr,cwd=r)
  pid,status,usage=os.wait4(child.pid,0);child.returncode=os.waitstatus_to_exitcode(status)
  rec.update(pid=pid,exit_code=child.returncode,reaped=True,wall_s=time.perf_counter()-t,user_cpu_s=usage.ru_utime,system_cpu_s=usage.ru_stime,highwater_rss_kib=usage.ru_maxrss,exit_utc=utc())
except BaseException as exc:
 rec.update(observer_error={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()},wall_s=time.perf_counter()-t)
try:
 after=check(); rec.update(bindings_unchanged=after==before,post_custody=after)
except BaseException as exc:
 rec.update(bindings_unchanged=False,custody_error={'type':type(exc).__name__,'message':str(exc)})
for key,p in [('result',r/'consumer-01/RESULT.json'),('failure',r/'consumer-01/FAILURE.json'),('stdout',out/'stdout.log'),('stderr',out/'stderr.log')]:
 rec[key]=ident(p) if p.exists() else None
rec.update(total_observer_wall_s=time.perf_counter()-begin,observer_cpu_s=time.process_time()-cbegin,observer_start_utc=start,observer_end_utc=utc())
write(out/'PROCESS.json',rec)
print(json.dumps({k:v for k,v in rec.items() if k!='post_custody'},sort_keys=True))

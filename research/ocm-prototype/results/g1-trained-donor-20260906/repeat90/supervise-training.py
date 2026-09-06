from pathlib import Path
import subprocess,resource,json,time,os,signal,datetime,hashlib
ROOT=Path(__file__).resolve().parent
plan=json.loads((ROOT/'training-plan.json').read_text())
def bounded():resource.setrlimit(resource.RLIMIT_AS,(plan['address_space_bytes'],plan['address_space_bytes']))
start=time.monotonic();started=datetime.datetime.now(datetime.timezone.utc)
with (ROOT/'training.stdout').open('w') as out,(ROOT/'training.stderr').open('w') as err:
 child=subprocess.Popen([plan['python'],str(ROOT/'train-components.py')],cwd=ROOT,stdout=out,stderr=err,preexec_fn=bounded,start_new_session=True)
 receipt={'status':'RUNNING','supervisor_pid':os.getpid(),'child_pid':child.pid,'pgid':os.getpgid(child.pid),'start_utc':started.isoformat(),'deadline_utc':(started+datetime.timedelta(seconds=plan['outer_seconds'])).isoformat(),'command':[plan['python'],str(ROOT/'train-components.py')],'outer_seconds':plan['outer_seconds'],'address_space_bytes':plan['address_space_bytes'],'plan_sha256':hashlib.sha256((ROOT/'training-plan.json').read_bytes()).hexdigest(),'prior_attempt_receipt':plan['prior_attempt_receipt'],'prior_attempt_costs':plan['prior_attempt_costs']}
 (ROOT/'training-process.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
 try:child.wait(timeout=plan['outer_seconds']);terminal='COMPLETED' if child.returncode==0 else 'TRAINING_FAILED'
 except subprocess.TimeoutExpired:
  os.killpg(child.pid,signal.SIGTERM)
  try:child.wait(timeout=10)
  except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
  terminal='EXTERNAL_TIME_BOUND'
 usage=resource.getrusage(resource.RUSAGE_CHILDREN)
 receipt.update(status=terminal,returncode=child.returncode,external_wall_seconds=time.monotonic()-start,child_user_seconds=usage.ru_utime,child_system_seconds=usage.ru_stime,child_maxrss_kib=usage.ru_maxrss,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 (ROOT/'training-process.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)

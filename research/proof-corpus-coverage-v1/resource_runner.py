"""Aggregate subprocess supervision; offline code policy is added by build_profile."""
from pathlib import Path
import os,resource,signal,subprocess,time,uuid,threading
from resource_pidfd import preflight
from resource_contract import validate_limits,available_memory,write_json,canonical,record
from resource_cgroup import Controller
from resource_monitor import disk_snapshot,signal_members,reason
def run(argv,env,limits,output,owned_paths,*,token=None):
 handlers={}
 def interrupted(signum,frame):raise InterruptedError("host signal "+str(signum))
 if threading.current_thread() is threading.main_thread():
  for sig in (signal.SIGTERM,signal.SIGHUP):handlers[sig]=signal.signal(sig,interrupted)
 try:return _run(argv,env,limits,output,owned_paths,token=token,guarded=bool(handlers))
 finally:
  for sig,old in handlers.items():signal.signal(sig,old)
def _run(argv,env,limits,output,owned_paths,*,token,guarded):
 limits=validate_limits(limits);start=time.monotonic();root=Path(output).resolve()
 root.mkdir();work=root/"work";work.mkdir()
 roots=[root,*[Path(p).resolve(strict=True) for p in owned_paths]]
 token=token or "run-"+uuid.uuid4().hex
 receipt={"schema":"ocm.f1.resource-receipt.v2","terminal":"SETUP_REFUSED","reason":"",
  "argv":argv,"environment":env,"limits":limits,"token":token,"returncode":None,
  "cleanup":{"reaped":False,"members_empty":False},"disk_enforcement":"SAMPLED_STOP_NOT_HARD_QUOTA",
  "cpu_scope":"v1 cpuacct aggregate descendant usage; not RSS","peak_rss_bytes":None,
  "dispatch":{"state":"NOT_ATTEMPTED","attempted":False,"pid":None},"evidence_errors":[]}
 c=p=None;signals=[];first=None;last=None;stop="";error=None;phase="SETUP"
 try:
  receipt["pidfd"]=preflight()
  initial=disk_snapshot(roots);initial["available_memory_bytes"]=available_memory()
  receipt["initial"]=initial
  if initial["available_memory_bytes"]<limits["min_available_bytes"]:raise ValueError("INITIAL_MEMORY_HEADROOM")
  if initial["free_bytes"]<limits["min_free_bytes"]:raise ValueError("INITIAL_DISK_HEADROOM")
  if initial["owned_bytes"]>limits["max_owned_bytes"]:raise ValueError("INITIAL_OWNED_BYTES")
  c=Controller.create(token,limits);receipt["controller_paths"]={k:str(v) for k,v in c.paths.items()}
  receipt["controller_readback"]=c.snapshot();receipt["helper_loaded_sources"]=c.helper_sources
  write_json(root/"plan.json",receipt)
  def before_exec():
   c.attach()
   resource.setrlimit(resource.RLIMIT_FSIZE,(limits["max_file_bytes"],limits["max_file_bytes"]))
  with (root/"stdout.bin").open("xb") as out,(root/"stderr.bin").open("xb") as err,(root/"samples.jsonl").open("xb") as samples:
   kwargs=dict(env=env,cwd=work,stdout=out,stderr=err,stdin=subprocess.DEVNULL,
    start_new_session=True,preexec_fn=before_exec,close_fds=True)
   phase="LAUNCH";receipt["dispatch"].update(state="ATTEMPTED_UNKNOWN",attempted=True)
   p=subprocess.Popen(argv,**kwargs)
   receipt["pid"]=p.pid;receipt["dispatch"].update(state="STARTED",pid=p.pid)
   phase="MONITOR"
   while True:
    last={**disk_snapshot(roots),"elapsed_s":time.monotonic()-start,"resources":c.snapshot()}
    samples.write(canonical(last));samples.flush()
    stop=reason(last,limits,last["elapsed_s"])
    if stop:first=last;break
    observed=p.poll()
    if observed is not None:receipt["returncode"]=observed;break
    time.sleep(limits["poll_s"])
  receipt["terminal"]="RESOURCE_STOP" if stop else "COMPLETED" if p.returncode==0 else "COMMAND_FAILED"
  receipt["reason"]=stop
 except BaseException as exc:
  error={"class":type(exc).__name__,"message":str(exc)}
  state=receipt["dispatch"]["state"]
  receipt["terminal"]=("INTERRUPTED" if isinstance(exc,(KeyboardInterrupt,SystemExit,InterruptedError))
   else "MONITOR_FAILED" if state=="STARTED" else "DISPATCH_UNCERTAIN" if state=="ATTEMPTED_UNKNOWN" else "SETUP_REFUSED")
  receipt["reason"]=type(exc).__name__+": "+str(exc)
  receipt["failure_phase"]=phase
 finally:
  receipt["primary_outcome"]={"terminal":receipt["terminal"],"reason":receipt["reason"],"phase":phase,"error":error}
  if guarded:
   for sig in (signal.SIGTERM,signal.SIGHUP):signal.signal(sig,signal.SIG_IGN)
  if c is not None:
   try:
    deadline=time.monotonic()+limits["term_grace_s"]+limits["reap_s"]
    if c.snapshot()["members"]:
     signals.append(signal_members(c,signal.SIGTERM));until=time.monotonic()+limits["term_grace_s"]
     while c.snapshot()["members"] and time.monotonic()<until:
      if p is not None:p.poll()
      time.sleep(min(.05,limits["poll_s"]))
    until=deadline
    while c.snapshot()["members"] and time.monotonic()<until:
     signals.append(signal_members(c,signal.SIGKILL))
     if p is not None:p.poll()
     time.sleep(min(.05,limits["poll_s"]))
    if p is not None:
     p.wait(timeout=max(.001,deadline-time.monotonic()));receipt["returncode"]=p.returncode;receipt["cleanup"]["reaped"]=True
    else:receipt["cleanup"]["reaped"]=not receipt["dispatch"]["attempted"]
    receipt["final_resources"]=c.snapshot()
    receipt["cleanup"]["members_empty"]=not receipt["final_resources"]["members"]
    if receipt["cleanup"]["members_empty"] and receipt["cleanup"]["reaped"]:c.remove();receipt["cleanup"]["controllers_removed"]=True
   except BaseException as exc:
    receipt["cleanup"]["error"]=type(exc).__name__+": "+str(exc)
    receipt["terminal"]="CLEANUP_INCOMPLETE"
  else:receipt["cleanup"]={"reaped":True,"members_empty":True,"no_dispatch":True}
  if p is not None and p.returncode is not None:receipt["returncode"]=p.returncode
  if not all(receipt["cleanup"].get(k) for k in ("reaped","members_empty")):receipt["terminal"]="CLEANUP_INCOMPLETE"
  if receipt["terminal"]=="COMPLETED" and receipt["returncode"]!=0:receipt["terminal"]="COMMAND_FAILED"
  try:
   final_disk={**disk_snapshot(roots),"available":True}
   if receipt["terminal"] in ("COMPLETED","COMMAND_FAILED") and "final_resources" in receipt:
    late=reason({**final_disk,"resources":receipt["final_resources"]},limits,0)
    if late:receipt["terminal"]="RESOURCE_STOP";receipt["reason"]=late
  except BaseException as exc:
   final_disk={"available":False,"error":{"class":type(exc).__name__,"message":str(exc)}}
   receipt["evidence_errors"].append({"phase":"FINAL_DISK_ACCOUNTING",**final_disk["error"]})
   if receipt["terminal"] in ("COMPLETED","COMMAND_FAILED"):
    receipt["terminal"]="EVIDENCE_FAILED";receipt["reason"]="DISK_ACCOUNTING_UNAVAILABLE"
  receipt.update(error=error,signals=signals,first_stop=first,final_disk=final_disk,
   overshoot_bytes=max(0,final_disk["owned_bytes"]-limits["max_owned_bytes"]) if final_disk["available"] else None,
   free_space_undershoot_bytes=max(0,limits["stop_free_bytes"]-final_disk["free_bytes"]) if final_disk["available"] else None,
   wall_through_cleanup_s=time.monotonic()-start,stop_to_cleanup_s=None if first is None else time.monotonic()-start-first["elapsed_s"])
  receipt["raw"]={}
  for name in ("stdout.bin","stderr.bin","samples.jsonl"):
   try:
    if receipt["dispatch"]["attempted"] or (root/name).exists():receipt["raw"][name]=record(root/name)
   except BaseException as exc:
    receipt["evidence_errors"].append({"phase":"RAW_CUSTODY","file":name,"class":type(exc).__name__,"message":str(exc)})
    if receipt["dispatch"]["attempted"] and receipt["terminal"]!="CLEANUP_INCOMPLETE":
     receipt["terminal"]="EVIDENCE_FAILED";receipt["reason"]="RAW_CUSTODY_UNAVAILABLE"
  receipt["evidence_complete"]=not receipt["evidence_errors"]
  write_json(root/"resource-receipt.json",receipt)
 return receipt

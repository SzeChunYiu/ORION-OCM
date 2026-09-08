"""Explicit offline evaluator profile. Audit records are external authority, not inferred."""
from pathlib import Path
from hashlib import sha256
import json,os,re,time,uuid
from resource_contract import record,verify,canonical,write_json,validate_limits
from resource_cgroup import helper
from build_profile_policy import guest_path,verify_inventory,apparmor_policy
import resource_runner
from resource_boot import loaded_sources
from resource_deadline import Started,DeadlineFailure,GUEST
KEYS={"schema","bwrap","aa_exec","files","materials","writable","argv","environment","code_audit"}
ENV={"PATH","HOME","TMPDIR","LEAN_SYSROOT","LEAN_PATH","LEAN_NUM_THREADS","LANG","LC_ALL","TZ"}
def payload(p):return {k:v for k,v in p.items() if k!="code_audit"}
def validate(p):
 if type(p) is not dict or set(p)!=KEYS or p["schema"]!="ocm.f1.build-profile.v1":raise ValueError("exact profile required")
 verify(p["bwrap"]);verify(p["aa_exec"])
 guests={"/proc","/dev","/tmp","/policy-aa-exec"};entries=[]
 if type(p["files"]) is not list or not p["files"]:raise ValueError("explicit file mounts required")
 for f in p["files"]:
  if set(f)!={"source","guest","access"} or f["access"] not in ("executable","library","read"):raise ValueError("file mount contract")
  verify(f["source"]);g=guest_path(f["guest"])
  if g in guests:raise ValueError("duplicate or reserved guest")
  guests.add(g);entries.append((g,"file",f["source"]["path"]))
 for d in p["materials"]:
  if set(d)!={"path","guest","inventory"}:raise ValueError("material contract")
  path=Path(d["path"])
  if str(path) in ("/","/usr","/home","/home/billy","/etc","/var","/run","/tmp"):raise ValueError("whole host directory forbidden")
  if str(path.resolve(strict=True))!=str(path) or not path.is_dir():raise ValueError("canonical material directory required")
  inv=verify(d["inventory"]);verify_inventory(path,json.loads(inv.read_bytes()))
  g=guest_path(d["guest"])
  if g in guests:raise ValueError("duplicate or reserved guest")
  guests.add(g);entries.append((g,"material",str(path)))
 for w in p["writable"]:
  if set(w)!={"path","guest"}:raise ValueError("writable contract")
  path=Path(w["path"])
  if not path.is_absolute() or str(path.resolve())!=str(path):raise ValueError("canonical writable path required")
  g=guest_path(w["guest"])
  if g in guests:raise ValueError("duplicate or reserved guest")
  guests.add(g);entries.append((g,"writable",str(path)))
 for i,(g,kind,host) in enumerate(entries):
  for reserved in ("/proc","/dev","/tmp","/policy-aa-exec"):
   if g.startswith(reserved+"/"):raise ValueError("reserved namespace overlap")
  for h,k,other in entries[i+1:]:
   if (h.startswith(g+"/") and kind=="file") or (g.startswith(h+"/") and k=="file"):raise ValueError("file mount overlap")
   if kind=="writable" and (h.startswith(g+"/") or g==h):raise ValueError("writable covers code/material")
   if k=="writable" and (g.startswith(h+"/") or g==h):raise ValueError("writable covers code/material")
   if kind=="writable" and (Path(host)==Path(other) or Path(other).is_relative_to(host) or Path(host).is_relative_to(other)):raise ValueError("writable host overlaps input")
   if k=="writable" and (Path(host)==Path(other) or Path(host).is_relative_to(other) or Path(other).is_relative_to(host)):raise ValueError("writable host overlaps input")
 if not p["writable"]:raise ValueError("owned writable work mount required")
 argv=p["argv"]
 if type(argv) is not list or not argv or any(type(x) is not str or "\0" in x for x in argv):raise ValueError("argv required")
 if argv[0] not in {f["guest"] for f in p["files"] if f["access"]=="executable"}:raise ValueError("unregistered executable")
 if type(p["environment"]) is not dict or set(p["environment"])-ENV:raise ValueError("unregistered environment")
 if any(type(v) is not str or "\0" in v for v in p["environment"].values()):raise ValueError("invalid environment")
 audit=json.loads(verify(p["code_audit"]).read_bytes())
 if set(audit)!={"schema","profile_payload_sha256","non_neural_code_reviewed","dynamic_code_scope","evidence","limitations"}:raise ValueError("audit contract")
 if audit["schema"]!="ocm.f1.build-code-audit.v1" or audit["profile_payload_sha256"]!=sha256(canonical(payload(p))).hexdigest():raise ValueError("audit binding drift")
 if audit["non_neural_code_reviewed"] is not True or audit["dynamic_code_scope"]!="REGISTERED_EXEC_AND_FILE_MAPPING_ONLY":raise ValueError("code audit not qualified")
 if type(audit["evidence"]) is not list or not audit["evidence"] or type(audit["limitations"]) is not str or not audit["limitations"].strip():raise ValueError("audit evidence and scope required")
 for item in audit["evidence"]:verify(item)
 return audit
def command(p,token):
 args=[p["bwrap"]["path"],"--unshare-all","--die-with-parent","--new-session","--cap-drop","ALL",
  "--proc","/proc","--dev","/dev","--tmpfs","/tmp"]
 for key,value in sorted(p["environment"].items()):args+=["--setenv",key,value]
 for d in sorted(p["materials"],key=lambda x:x["guest"].count("/")):args+=["--ro-bind",d["path"],d["guest"]]
 for f in p["files"]:args+=["--ro-bind",f["source"]["path"],f["guest"]]
 args+=["--ro-bind",p["aa_exec"]["path"],"/policy-aa-exec"]
 for w in p["writable"]:args+=["--bind",w["path"],w["guest"]]
 args+=["--chdir",p["writable"][0]["guest"],"--","/policy-aa-exec","-p","ocm-f1-"+token,"--",*p["argv"]]
 return args
def run(profile,limits,output,*,external_started=None):
 profile=json.loads(canonical(profile));limits=validate_limits(limits)
 root=Path(output).resolve()
 host_paths=[w["path"] for w in profile["writable"]]+[d["path"] for d in profile["materials"]]
 host_paths += [f["source"]["path"] for f in profile["files"]]+[profile[k]["path"] for k in ("bwrap","aa_exec","code_audit")]
 for value in host_paths:
  path=Path(value).resolve()
  if path==root or path.is_relative_to(root) or root.is_relative_to(path):raise ValueError("output overlaps workload/input path")
 sources=loaded_sources(globals())
 root.mkdir();start=time.monotonic();token="build-"+uuid.uuid4().hex
 result={"schema":"ocm.f1.build-profile-receipt.v2","terminal":"PROFILE_REFUSED","token":token,
  "authority":"External source/code audit plus observed controls; not whole-host neural absence."}
 loaded=False;phase="PROFILE_PREPARATION";result["dispatch_state"]="NOT_ATTEMPTED"
 result["driver_sources"]=sources
 clock=None if external_started is None else Started(external_started,[root,*[w["path"] for w in profile["writable"]]])
 if clock is not None:result["external_started"]=clock.receipt
 try:
  if clock is not None:
   clock.check("PROFILE_PREPARATION")
   if not any(f=={"source":clock.receipt["binding"]["record"],"guest":GUEST,"access":"read"} for f in profile["files"]):
    raise ValueError("EXTERNAL_STARTED_READONLY_MOUNT")
  audit=validate(profile);result["audit"]=audit;write_json(root/"profile.json",profile)
  for w in profile["writable"]:
   p=Path(w["path"]);p.mkdir(parents=False,exist_ok=True)
   if not p.is_dir() or p.is_symlink() or p.stat().st_uid!=os.getuid():raise ValueError("unowned writable output")
  files=[*profile["files"],{"guest":"/policy-aa-exec","access":"executable"}]
  policy=apparmor_policy(token,files,[d["guest"] for d in profile["materials"]],[w["guest"] for w in profile["writable"]])
  pp=root/"apparmor.profile";pp.write_text(policy);result["policy"]=record(pp)
  result["policy_setup"]=helper("policy-add",token,str(pp));loaded=True
  remaining=limits["wall_s"]-(time.monotonic()-start)
  if remaining<=0:raise ValueError("PROFILE_PREPARATION_DEADLINE")
  dispatch_limits={**limits,"wall_s":remaining}
  argv=command(profile,token);owned=[str(root),*[w["path"] for w in profile["writable"]]]
  options={} if external_started is None else {"external_started":external_started}
  if clock is not None:clock.check("PROFILE_PREDISPATCH")
  phase="DISPATCH";result["dispatch_state"]="ATTEMPTED_UNKNOWN"
  result["dispatch"]=resource_runner.run(argv,{},dispatch_limits,root/"dispatch",owned,token=token,**options)
  result["dispatch_state"]=result["dispatch"].get("dispatch",{}).get("state","ATTEMPTED_UNKNOWN")
  result["terminal"]=result["dispatch"]["terminal"]
  phase="POST_DISPATCH_CUSTODY"
  validate(profile)
  for binding in sources.values():verify(binding)
  if loaded_sources(globals())!=sources:raise ValueError("loaded source custody drift")
  result["post_input_custody"]="UNCHANGED"
  if clock is not None:clock.check("PROFILE_POST_CUSTODY")
 except BaseException as exc:
  result["error"]={"class":type(exc).__name__,"message":str(exc)}
  result["terminal"]=("POST_DISPATCH_CUSTODY_FAILED" if "dispatch" in result
   else "DISPATCH_UNCERTAIN" if result["dispatch_state"]=="ATTEMPTED_UNKNOWN" else "PROFILE_REFUSED")
  result["failure_phase"]=phase
 finally:
  result["primary_outcome"]={"terminal":result["terminal"],"phase":phase,"error":result.get("error")}
  cleanup=result.get("dispatch",{}).get("cleanup",{})
  safe=result["dispatch_state"]=="NOT_ATTEMPTED" or all(cleanup.get(k) is True for k in ("members_empty","reaped"))
  if loaded and not safe:
   result["policy_retained_until_empty"]=True
  elif loaded:
   try:result["policy_cleanup"]=helper("policy-remove",token,str(root/"apparmor.profile"))
   except BaseException as exc:result["terminal"]="CLEANUP_INCOMPLETE";result["policy_cleanup_error"]=str(exc)
  if clock is not None:
   try:clock.check("PROFILE_FINAL_CUSTODY")
   except DeadlineFailure as exc:
    if result["terminal"] in ("COMPLETED","COMMAND_FAILED"):
     result["terminal"]="POST_DISPATCH_CUSTODY_FAILED";result["deadline_error"]=str(exc)
  result["wall_through_cleanup_s"]=time.monotonic()-start
  write_json(root/"build-profile-receipt.json",result)
 return result

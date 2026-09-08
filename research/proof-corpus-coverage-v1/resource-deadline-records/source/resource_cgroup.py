"""Read-back enforced v1 limits; only owned, root-created groups are used."""
from pathlib import Path
import os,re,subprocess,json
from resource_contract import validate_limits,record
HELPER=Path("/usr/local/libexec/ocm-f1-coverage-v1/resource_setup.py")
HERE=Path(__file__).resolve().parent
CONTROL={"memory.limit_in_bytes":"memory","memory.memsw.limit_in_bytes":"memory",
 "cpu.cfs_period_us":"cpu","cpu.cfs_quota_us":"cpu","pids.max":"pids"}
STATS={"memory.usage_in_bytes":"memory","memory.memsw.usage_in_bytes":"memory",
 "memory.max_usage_in_bytes":"memory","memory.memsw.max_usage_in_bytes":"memory",
 "memory.failcnt":"memory","memory.memsw.failcnt":"memory","cpuacct.usage":"cpu","pids.current":"pids"}
def valid_token(name):
 if not re.fullmatch("[a-z][a-z0-9-]{5,63}",name):raise ValueError("invalid owned controller token")
def helper(mode,name,*args):
 valid_token(name)
 for n in ("resource_setup.py","resource_contract.py"):
  p=HELPER.parent/n
  if p.stat().st_uid!=0 or p.stat().st_mode&0o022:raise ValueError("unprotected privileged helper")
  if record(p)["sha256"]!=record(HERE/n)["sha256"]:raise ValueError("installed helper source drift")
 r=subprocess.run(["/usr/bin/sudo","-n","/usr/bin/python3","-I",str(HELPER),mode,name,*args],
  stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=35)
 if r.returncode:raise ValueError("SCOPED_SETUP: "+r.stderr.decode(errors="replace"))
 value=json.loads(r.stdout)
 if value["source_stamps"]!={n:record(HELPER.parent/n) for n in ("resource_setup.py","resource_contract.py")}:raise ValueError("executed helper binding drift")
 result=value["result"];result["_helper_sources"]=value["source_stamps"];return result
class Controller:
 def __init__(self,name,paths):self.name=name;self.paths={k:Path(v) for k,v in paths.items()}
 @classmethod
 def create(cls,name,limits):
  valid_token(name);limits=validate_limits(limits)
  value=helper("create",name,json.dumps(limits),str(os.getuid()));stamps=value.pop("_helper_sources")
  c=cls(name,value);c.helper_sources=stamps
  s=c.snapshot()
  expected={"memory.limit_in_bytes":limits["memory_bytes"],"memory.memsw.limit_in_bytes":limits["memsw_bytes"],
   "cpu.cfs_period_us":limits["cpu_period_us"],"cpu.cfs_quota_us":limits["cpu_quota_us"],"pids.max":limits["pids"]}
  if any(s[k]!=v for k,v in expected.items()):c.remove();raise ValueError("resource limit readback differs")
  return c
 def attach(self):
  for p in self.paths.values():(p/"cgroup.procs").write_text(str(os.getpid()))
 def snapshot(self):
  result={k:int((self.paths[g]/k).read_text()) for k,g in {**CONTROL,**STATS}.items()}
  result["members_by_controller"]={g:sorted(set(map(int,(p/"cgroup.procs").read_text().split()))) for g,p in self.paths.items()}
  result["members"]=sorted(set(pid for v in result["members_by_controller"].values() for pid in v))
  for g,n in [("cpu","cpu.stat"),("memory","memory.oom_control"),("pids","pids.events")]:
   p=self.paths[g]/n
   result[n]={a:int(b) for a,b in (l.split() for l in p.read_text().splitlines())} if p.exists() else None
  return result
 def root_owned_limits(self):
  return all((self.paths[g]/f).stat().st_uid==0 and not (self.paths[g]/f).stat().st_mode&0o022 for f,g in CONTROL.items())
 def remove(self):return helper("remove",self.name)

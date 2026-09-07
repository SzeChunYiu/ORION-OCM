"""Root-only scoped v1 controller/AppArmor setup; never changes existing job groups."""
from pathlib import Path
import os,re,json,sys,subprocess
from hashlib import sha256
HERE=Path(__file__).resolve().parent
CONTRACT=(HERE/"resource_contract.py").read_bytes()
contract_namespace={"__name__":"ocm_resource_contract","__file__":str(HERE/"resource_contract.py")}
exec(compile(CONTRACT,str(HERE/"resource_contract.py"),"exec"),contract_namespace)
validate_limits=contract_namespace["validate_limits"]
BASES={"memory":Path("/sys/fs/cgroup/memory/ocm-f1-coverage-v1"),
 "cpu":Path("/sys/fs/cgroup/cpu,cpuacct/ocm-f1-coverage-v1"),
 "pids":Path("/sys/fs/cgroup/pids/ocm-f1-coverage-v1")}
def token(value):
 if not re.fullmatch("[a-z][a-z0-9-]{5,63}",value):raise ValueError("invalid owned token")
 return value
def paths(name):return {k:p/token(name) for k,p in BASES.items()}
def write(path,value):path.write_text(str(value))
def create(name,limits,owner):
 limits=validate_limits(limits)
 if owner<=0 or owner!=int(os.environ["SUDO_UID"]):raise ValueError("caller ownership mismatch")
 made=[]
 try:
  for base in BASES.values():
   base.mkdir(exist_ok=True)
   if base.stat().st_uid!=0:raise ValueError("controller base is not root-owned")
  ps=paths(name)
  for p in ps.values():p.mkdir();made.append(p)
  for key,file in [("memory_bytes","memory.limit_in_bytes"),("memsw_bytes","memory.memsw.limit_in_bytes")]:
   write(ps["memory"]/file,limits[key])
  if (ps["memory"]/"memory.use_hierarchy").read_text().strip()!="1":raise ValueError("hierarchical accounting missing")
  write(ps["cpu"]/"cpu.cfs_period_us",limits["cpu_period_us"])
  write(ps["cpu"]/"cpu.cfs_quota_us",limits["cpu_quota_us"])
  write(ps["pids"]/"pids.max",limits["pids"])
  for p in ps.values():os.chown(p/"cgroup.procs",owner,-1)
  return {k:str(v) for k,v in ps.items()}
 except BaseException:
  for p in reversed(made):
   if not (p/"cgroup.procs").read_text().strip():p.rmdir()
  raise
def remove(name):
 ps=paths(name)
 for p in ps.values():
  if (p/"cgroup.procs").read_text().strip():raise ValueError("controller still populated")
 for p in reversed(list(ps.values())):p.rmdir()
 return {"removed":True}
def apparmor(name,policy,remove=False):
 if remove:
  for p in paths(name).values():
   f=p/"cgroup.procs"
   if f.exists() and f.read_text().strip():raise ValueError("policy still protects populated controller")
 text=Path(policy).read_text()
 expected="profile ocm-f1-"+token(name)+" flags=(attach_disconnected,mediate_deleted) {"
 lines=text.splitlines()
 if not lines or lines[0]!=expected or lines[-1]!="}":raise ValueError("profile ownership mismatch")
 for line in lines[1:-1]:
  s=line.strip()
  if s in ("deny network,","signal (send, receive),"):continue
  if not re.fullmatch(r"/[A-Za-z0-9_./+*,-]+ [rmwklix]+,",s):raise ValueError("unregistered profile directive")
 result=subprocess.run(["/sbin/apparmor_parser","-R" if remove else "-a","-K","-j","1"],
  input=text.encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30)
 if result.returncode:raise ValueError(result.stderr.decode(errors="replace"))
 return {"profile":"ocm-f1-"+name,"removed":remove,"stderr":result.stderr.decode()}
if __name__=="__main__":
 if os.geteuid()!=0:raise SystemExit("root required")
 mode,name,*args=sys.argv[1:];token(name)
 if mode=="create":value=create(name,json.loads(args[0]),int(args[1]))
 elif mode=="remove":value=remove(name)
 elif mode in ("policy-add","policy-remove"):value=apparmor(name,args[0],mode=="policy-remove")
 else:raise ValueError("unknown scoped operation")
 stamps={n:{"path":str(HERE/n),"sha256":sha256(b).hexdigest(),"bytes":len(b)} for n,b in
  [("resource_setup.py",Path(__file__).read_bytes()),("resource_contract.py",CONTRACT)]}
 print(json.dumps({"result":value,"source_stamps":stamps},sort_keys=True))

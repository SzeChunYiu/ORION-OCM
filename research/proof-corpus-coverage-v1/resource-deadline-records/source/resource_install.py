"""Install only this package's protected helper; preserve predecessor bytes and commands."""
from pathlib import Path
import os,subprocess,time
from resource_contract import record,write_json
TARGET=Path("/usr/local/libexec/ocm-f1-coverage-v1")
SOURCES=("resource_setup.py","resource_contract.py")
def install(output):
 root=Path(output).resolve();root.mkdir();before=root/"previous";before.mkdir()
 start=time.monotonic();result={"schema":"ocm.f1.resource-install.v1","terminal":"SETUP_REFUSED","commands":[]}
 try:
  for base in ("/sys/fs/cgroup/memory","/sys/fs/cgroup/cpu,cpuacct","/sys/fs/cgroup/pids"):
   owned=Path(base)/"ocm-f1-coverage-v1"
   if owned.exists():
    for p in owned.iterdir():
     if p.is_dir() and (p/"cgroup.procs").read_text().strip():raise ValueError("owned controller active; preserve installed helper")
  sources=[record(Path(__file__).resolve().parent/n) for n in SOURCES]
  for n in SOURCES:
   p=TARGET/n
   if p.exists():
    if p.is_symlink() or p.stat().st_uid!=0:raise ValueError("unexpected existing helper")
    (before/n).write_bytes(p.read_bytes())
  commands=[["/usr/bin/sudo","-n","/usr/bin/install","-d","-m","0755",str(TARGET)]]
  commands += [["/usr/bin/sudo","-n","/usr/bin/install","-o","root","-g","root","-m","0644",b["path"],str(TARGET/Path(b["path"]).name)] for b in sources]
  for i,argv in enumerate(commands):
   with (root/(str(i)+".stdout")).open("xb") as out,(root/(str(i)+".stderr")).open("xb") as err:
    ran=subprocess.run(argv,stdout=out,stderr=err,timeout=30)
   result["commands"].append({"argv":argv,"returncode":ran.returncode})
   if ran.returncode:raise ValueError("scoped installation failed")
  installed=[record(TARGET/n) for n in SOURCES]
  for a,b in zip(sources,installed):
   p=Path(b["path"])
   if a["sha256"]!=b["sha256"] or p.stat().st_uid!=0 or p.stat().st_mode&0o022:raise ValueError("installed binding/ownership drift")
   if record(a["path"])!=a:raise ValueError("installation input drift")
  result.update(terminal="SCOPED_HELPER_INSTALLED",sources=sources,installed=installed)
 except BaseException as exc:result["error"]={"class":type(exc).__name__,"message":str(exc)}
 result["wall_s"]=time.monotonic()-start;write_json(root/"INSTALL.json",result);return result
if __name__=="__main__":
 import argparse,json
 p=argparse.ArgumentParser();p.add_argument("--output",required=True);a=p.parse_args()
 result=install(a.output);print(json.dumps(result));raise SystemExit(0 if result["terminal"]=="SCOPED_HELPER_INSTALLED" else 2)

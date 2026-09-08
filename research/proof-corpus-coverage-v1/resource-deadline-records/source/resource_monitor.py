"""Sampled disk accounting and PID-safe signalling for the owned cgroup only."""
from pathlib import Path
import os,signal,time
from resource_pidfd import open_pid,send
def scan_error(exc):raise exc
def disk_snapshot(roots):
 started=time.monotonic();seen=set();logical=allocated=0
 unique=sorted(set(Path(p).resolve() for p in roots),key=lambda p:len(p.parts))
 roots=[p for p in unique if not any(p!=q and p.is_relative_to(q) for q in unique)]
 for root in roots:
  for base,dirs,files in os.walk(root,followlinks=False,onerror=scan_error):
   for name in files:
    p=Path(base)/name
    try:s=p.lstat()
    except FileNotFoundError:continue
    key=(s.st_dev,s.st_ino)
    if key in seen:continue
    seen.add(key);logical+=s.st_size;allocated+=s.st_blocks*512
 frees=[os.statvfs(p).f_bavail*os.statvfs(p).f_frsize for p in roots]
 return {"owned_bytes":logical,"allocated_bytes":allocated,"free_bytes":min(frees),
  "sample_wall_s":time.monotonic()-started}
def signal_members(controller,sig):
 sent=[];errors=[]
 expected="/ocm-f1-coverage-v1/"+controller.name
 for pid in controller.snapshot()["members"]:
  try:
   fd=open_pid(pid)
   try:
    memberships=Path("/proc/"+str(pid)+"/cgroup").read_text().splitlines()
    if not any(l.split(":",2)[-1]==expected for l in memberships):raise ValueError("membership changed before signal")
    send(fd,sig);sent.append(pid)
   finally:os.close(fd)
  except ProcessLookupError:continue
  except FileNotFoundError:continue
  except Exception as exc:errors.append({"pid":pid,"error":str(exc)})
 return {"signal":int(sig),"sent":sent,"errors":errors}
def reason(sample,limits,elapsed):
 if elapsed>=limits["wall_s"]:return "WALL_DEADLINE"
 if sample["free_bytes"]<limits["stop_free_bytes"]:return "FREE_SPACE"
 if sample["owned_bytes"]>limits["max_owned_bytes"]:return "OWNED_BYTES"
 if sample["resources"]["memory.failcnt"] or sample["resources"]["memory.memsw.failcnt"]:return "MEMORY_LIMIT"
 if sample["resources"]["pids.events"] and sample["resources"]["pids.events"].get("max",0):return "PID_LIMIT"
 return ""

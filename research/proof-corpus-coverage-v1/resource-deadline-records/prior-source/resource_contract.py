"""Registered aggregate v1 bounds; smaller authored qualification settings are valid."""
import math,re
from pathlib import Path
from hashlib import sha256
import json

INTEGER_MAX = {
 "memory_bytes":20*1024**3,"memsw_bytes":20*1024**3,"cpu_quota_us":200000,
 "cpu_period_us":100000,"pids":128,"max_file_bytes":8*1024**3,
 "min_available_bytes":64*1024**3,"min_free_bytes":1024**4,
 "stop_free_bytes":1024**4,"max_owned_bytes":128*1024**3}
TIME_MAX={"wall_s":43200,"term_grace_s":5,"reap_s":10,"poll_s":1}
ZERO={"min_available_bytes","min_free_bytes","stop_free_bytes"}
def validate_limits(value):
 if type(value) is not dict or set(value)!=set(INTEGER_MAX)|set(TIME_MAX):raise ValueError("exact limits required")
 for k,maximum in INTEGER_MAX.items():
  v=value[k]
  if type(v) is not int or not (0 if k in ZERO else 1)<=v<=maximum:raise ValueError("invalid "+k)
 for k,maximum in TIME_MAX.items():
  v=value[k]
  if type(v) not in (int,float) or not math.isfinite(v) or not 0<v<=maximum:raise ValueError("invalid "+k)
 if value["cpu_period_us"]!=100000:raise ValueError("unregistered CPU period")
 if value["memory_bytes"]>value["memsw_bytes"]:raise ValueError("combined bound below memory")
 if value["memory_bytes"]%4096 or value["memsw_bytes"]%4096:raise ValueError("page aligned limits required")
 if value["min_free_bytes"]<value["stop_free_bytes"]:raise ValueError("initial free space below stop")
 return dict(value)
def canonical(value):return (json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n").encode()
def record(path):
 p=Path(path).resolve(strict=True);h=sha256();size=0
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1024**2),b""):h.update(b);size+=len(b)
 return {"path":str(p),"sha256":h.hexdigest(),"bytes":size}
def verify(binding):
 if type(binding) is not dict or set(binding)!={"path","sha256","bytes"}:raise ValueError("exact file binding required")
 if type(binding["bytes"]) is not int or binding["bytes"]<0 or type(binding["path"]) is not str:
  raise ValueError("typed file binding required")
 if type(binding["sha256"]) is not str or not re.fullmatch("[0-9a-f]{64}",binding["sha256"]):raise ValueError("sha256 required")
 p=Path(binding["path"])
 if p.resolve(strict=True)!=p or not p.is_file() or record(p)!=binding:raise ValueError("file binding drift")
 return p
def write_json(path,value):
 with Path(path).open("xb") as f:f.write(canonical(value))
def available_memory():
 for line in Path("/proc/meminfo").read_text().splitlines():
  if line.startswith("MemAvailable:"):return int(line.split()[1])*1024
 raise ValueError("MemAvailable unavailable")

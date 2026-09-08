"""Optional external clock authority; no privileged operations or clock creation."""
from pathlib import Path
from hashlib import sha256
import json,re,stat,time
from resource_contract import canonical

MAX_BYTES=4096
GUEST="/assay/STARTED.json"
BINDING=("schema","record","run_id","launch_seal_sha256","duration_ns")
FIELDS=("schema","run_id","boot_id","started_monotonic_ns","deadline_monotonic_ns","launch_seal_sha256")
def boot_id():return Path("/proc/sys/kernel/random/boot_id").read_text().strip()
def fields(value,keys):
 if type(value) is not dict or any(type(k) is not str for k in value) or set(value)!=set(keys):
  raise ValueError("EXTERNAL_STARTED_STRUCTURE")
def text(value,pattern):
 if type(value) is not str or re.fullmatch(pattern,value) is None:raise ValueError("EXTERNAL_STARTED_TYPE")
def integer(value,low,high):
 if type(value) is not int or not low<=value<=high:raise ValueError("EXTERNAL_STARTED_TIME_TYPE")
def binding(value):
 fields(value,BINDING);fields(value["record"],("path","bytes","sha256"))
 if type(value["schema"]) is not str or value["schema"]!="ocm.unary-external-deadline.v1":
  raise ValueError("EXTERNAL_STARTED_SCHEMA")
 text(value["run_id"],r"[a-z0-9][a-z0-9._-]{0,127}")
 text(value["launch_seal_sha256"],r"[0-9a-f]{64}")
 integer(value["duration_ns"],1,1200000000000)
 r=value["record"];text(r["path"],r"/[^\x00]+");text(r["sha256"],r"[0-9a-f]{64}")
 integer(r["bytes"],1,MAX_BYTES)
 return json.loads(canonical(value))

class DeadlineFailure(ValueError):pass

class Started:
 def __init__(self,value,forbidden=()):
  self.value=value;self.forbidden=tuple(Path(p).resolve() for p in forbidden)
  self.initial_record=None;self.identity=None
  self.receipt={"binding":None,"checks":0,"bytes_read":0,"read_wall_s":0.0,"read_cpu_s":0.0,
                "initial":None,"latest":None,"first_failure":None}
 def _read(self):
  bound=binding(self.value)
  if self.receipt["binding"] is None:self.receipt["binding"]=bound
  elif self.receipt["binding"]!=bound:raise ValueError("EXTERNAL_STARTED_BINDING_DRIFT")
  r=bound["record"];p=Path(r["path"])
  if any(p==root or p.is_relative_to(root) for root in self.forbidden):
   raise ValueError("EXTERNAL_STARTED_WRITABLE_OVERLAP")
  st=p.lstat()
  if not stat.S_ISREG(st.st_mode) or st.st_nlink!=1 or p.resolve(strict=True)!=p:
   raise ValueError("EXTERNAL_STARTED_ENTRY")
  if st.st_size!=r["bytes"] or st.st_size>MAX_BYTES:raise ValueError("EXTERNAL_STARTED_BYTES")
  identity=[st.st_dev,st.st_ino,st.st_mode,st.st_mtime_ns,st.st_ctime_ns]
  with p.open("rb") as stream:raw=stream.read(MAX_BYTES+1)
  self.receipt["bytes_read"]+=len(raw)
  after=p.lstat()
  if identity!=[after.st_dev,after.st_ino,after.st_mode,after.st_mtime_ns,after.st_ctime_ns]:
   raise ValueError("EXTERNAL_STARTED_IDENTITY_DRIFT")
  if len(raw)!=r["bytes"] or sha256(raw).hexdigest()!=r["sha256"]:raise ValueError("EXTERNAL_STARTED_HASH")
  value=json.loads(raw);fields(value,FIELDS)
  if canonical(value)!=raw:raise ValueError("EXTERNAL_STARTED_NONCANONICAL")
  if type(value["schema"]) is not str or value["schema"]!="ocm.unary-started.v1":
   raise ValueError("EXTERNAL_STARTED_SCHEMA")
  for key in ("run_id","launch_seal_sha256"):
   if type(value[key]) is not str or value[key]!=bound[key]:raise ValueError("EXTERNAL_STARTED_AUTHORITY")
  text(value["boot_id"],r"[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}")
  for key in ("started_monotonic_ns","deadline_monotonic_ns"):integer(value[key],0,2**63-1)
  if value["deadline_monotonic_ns"]-value["started_monotonic_ns"]!=bound["duration_ns"]:
   raise ValueError("EXTERNAL_STARTED_DURATION")
  if self.initial_record is not None and (value!=self.initial_record or identity!=self.identity):
   raise ValueError("EXTERNAL_STARTED_IDENTITY_DRIFT")
  self.initial_record=value;self.identity=identity
  if value["boot_id"]!=boot_id():raise ValueError("EXTERNAL_STARTED_BOOT")
  return value
 def check(self,phase):
  start=time.monotonic();cpu=time.process_time();self.receipt["checks"]+=1;reason=None;error=None
  value=self.initial_record
  try:
   value=self._read();now=time.monotonic_ns()
   if value["started_monotonic_ns"]>now:raise ValueError("EXTERNAL_STARTED_FUTURE")
   if now>=value["deadline_monotonic_ns"]:raise ValueError("EXTERNAL_DEADLINE_EXPIRED")
  except FileNotFoundError as exc:
   reason="EXTERNAL_STARTED_MISSING";error={"class":type(exc).__name__,"message":str(exc)}
  except (OSError,ValueError,TypeError,RecursionError) as exc:
   error={"class":type(exc).__name__,"message":str(exc)}
   reason=str(exc) if str(exc).startswith("EXTERNAL_") else "EXTERNAL_STARTED_INVALID:"+type(exc).__name__
  except BaseException as exc:
   reason="EXTERNAL_STARTED_EXCEPTION:"+type(exc).__name__
   error={"class":type(exc).__name__,"message":str(exc)}
   raise
  finally:
   now=time.monotonic_ns();value=value if value is not None else self.initial_record
   if reason is None and value is not None:
    if value["started_monotonic_ns"]>now:reason="EXTERNAL_STARTED_FUTURE"
    elif now>=value["deadline_monotonic_ns"]:reason="EXTERNAL_DEADLINE_EXPIRED"
   obs={"phase":phase,"observed_monotonic_ns":now,"reason":reason,"terminal":"VALID" if reason is None else "REFUSED"}
   if error is not None:obs["validation_error"]=error
   if value is not None:
    obs.update(started_monotonic_ns=value["started_monotonic_ns"],deadline_monotonic_ns=value["deadline_monotonic_ns"],
     remaining_ns=value["deadline_monotonic_ns"]-now,lateness_ns=max(0,now-value["deadline_monotonic_ns"]))
   self.receipt["read_wall_s"]+=time.monotonic()-start;self.receipt["read_cpu_s"]+=time.process_time()-cpu
   self.receipt["latest"]=obs
   if self.receipt["initial"] is None:self.receipt["initial"]=obs
   if reason is not None and self.receipt["first_failure"] is None:self.receipt["first_failure"]=obs
  if reason is not None:raise DeadlineFailure(reason)
  return obs

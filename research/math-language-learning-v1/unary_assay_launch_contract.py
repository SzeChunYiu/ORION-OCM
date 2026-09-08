"""Fixed assay launch data; reviewed source selection is external authority."""
import hashlib,os,re,stat,time
from pathlib import Path
import unary_method_plain as D
import unary_method_profile as B

PROJECT="/assay/project";WORK="/assay/work";STARTED="/assay/STARTED.json"
SEAL="/assay/SEAL.json";PLAN="/assay/PLAN.json";BINDING="/assay/BINDING.json";INPUT="/assay/INPUT.json"
BOOT=PROJECT+"/research/math-language-learning-v1/unary_assay_bootstrap.py"
DURATION=1200000000000
SNAPSHOT_SEAL="2f74e10608687e527357168f990a5eaa6ec5b9b3aaeed465f45df45162fc4a71"
MAPPING_SEAL="f9e1f027a396034b699626436e081ddae5a235ade35d11376cde57bb569dd994"
MODES=("REGISTERED","AUTHORED_LIFECYCLE","AUTHORED_PROBE")
CASES=("normal","network","source_write","native_exec","native_map","deadline","memory")
LIMITS={"memory_bytes":1073741824,"memsw_bytes":1073741824,"cpu_quota_us":100000,
 "cpu_period_us":100000,"pids":32,"wall_s":1260,"term_grace_s":2,"reap_s":5,"poll_s":.2,
 "max_file_bytes":536870912,"max_owned_bytes":17179869184,"min_available_bytes":2147483648,
 "min_free_bytes":25769803776,"stop_free_bytes":8589934592}

def stamp(path):
    path=Path(path);st=path.lstat()
    if not stat.S_ISREG(st.st_mode) or path.resolve(strict=True)!=path or st.st_nlink!=1:
        raise ValueError("LAUNCH_REGULAR_FILE")
    h=hashlib.sha256();size=0
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b);size+=len(b)
    after=path.lstat()
    if (st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns,st.st_ctime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns):
        raise ValueError("LAUNCH_FILE_DRIFT")
    return {"path":str(path),"sha256":h.hexdigest(),"bytes":size}

def read(path,expected):
    p=Path(path);st=p.lstat()
    if not stat.S_ISREG(st.st_mode) or p.resolve(strict=True)!=p or st.st_nlink!=1:raise ValueError("LAUNCH_REGULAR_FILE")
    if st.st_size>D.MAX_BYTES:raise ValueError("LAUNCH_DATA_BOUND")
    before=(st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns,st.st_ctime_ns)
    with p.open("rb") as f:raw=f.read(D.MAX_BYTES+1)
    after=p.lstat()
    if before!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns):raise ValueError("LAUNCH_FILE_DRIFT")
    if len(raw)!=st.st_size or hashlib.sha256(raw).hexdigest()!=expected:raise ValueError("LAUNCH_CONSUMED_BYTES")
    return D.parse(raw)

def write(path,value):
    p=Path(path);raw=D.raw(value)
    with p.open("xb") as f:f.write(raw);f.flush();os.fsync(f.fileno())
    sync_dir(p.parent)
    return stamp(p)

def sync_dir(path):
    fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)

def plan(value):
    value=D.parse(D.raw(value))
    keys={"schema","run_id","mode","cpu","duration_ns","sources","input","runtime_seal","mapping_seal","python"}
    if type(value) is not dict or set(value)!=keys:raise ValueError("LAUNCH_PLAN_FIELDS")
    if value["schema"]!="ocm.unary-launch-plan.v1" or value["mode"] not in MODES:raise ValueError("LAUNCH_PLAN_SCHEMA")
    if type(value["run_id"]) is not str or re.fullmatch("[a-z0-9][a-z0-9._-]{0,127}",value["run_id"]) is None:raise ValueError("LAUNCH_RUN_ID")
    if type(value["cpu"]) is not int or value["cpu"]<0:raise ValueError("LAUNCH_CPU")
    if type(value["duration_ns"]) is not int or not 0<value["duration_ns"]<=DURATION:raise ValueError("LAUNCH_DURATION")
    if value["mode"]=="REGISTERED" and (value["duration_ns"]!=DURATION or value["input"] is not None):raise ValueError("REGISTERED_FIXED_INPUT")
    if value["mode"]!="REGISTERED" and value["input"] is None:raise ValueError("AUTHORED_INPUT")
    if value["runtime_seal"]!=SNAPSHOT_SEAL or value["mapping_seal"]!=MAPPING_SEAL:raise ValueError("LAUNCH_RUNTIME_SEAL")
    if value["python"]!=B.DEFAULT:raise ValueError("LAUNCH_FIXED_PYTHON")
    if type(value["sources"]) is not dict or not value["sources"]:raise ValueError("LAUNCH_SOURCES")
    for name,digest in value["sources"].items():
        p=Path(name)
        if not p.parts or p.is_absolute() or p.as_posix()!=name or any(x in (".","..") for x in p.parts):raise ValueError("LAUNCH_SOURCE_PATH")
        if type(digest) is not str or re.fullmatch("[0-9a-f]{64}",digest) is None:raise ValueError("LAUNCH_SOURCE_HASH")
    if value["input"] is not None:
        r=value["input"]
        if type(r) is not dict or set(r)!={"sha256","bytes"} or type(r["bytes"]) is not int or not 0<r["bytes"]<=D.MAX_BYTES:
            raise ValueError("LAUNCH_INPUT")
        if type(r["sha256"]) is not str or re.fullmatch("[0-9a-f]{64}",r["sha256"]) is None:raise ValueError("LAUNCH_INPUT_HASH")
    return value

def guest_binding(binding):
    result=D.parse(D.raw(binding));result["record"]["path"]=STARTED
    return result

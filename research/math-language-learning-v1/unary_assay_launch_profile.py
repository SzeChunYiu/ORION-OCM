"""Fixed readonly snapshot/profile recipe; no implicit code-review authority."""
import hashlib,json,os,time,types,sys
from pathlib import Path
import unary_assay_launch_contract as L
import unary_method_outer as D

RUNTIME_MANIFEST="f229852f1500bcf9680e52321ac2325bbb27819db0afaafbad45827790a53a92"
RESOURCE=("resource_contract","resource_deadline","resource_pidfd","resource_cgroup","resource_monitor",
          "resource_runner","build_profile_policy","build_profile","resource_install","resource_boot")

def resources():
    root=Path(__file__).resolve().parents[2];p=root/"research/proof-corpus-coverage-v1/resource_boot.py"
    raw=p.read_bytes();m=types.ModuleType("resource_boot");m.__file__=str(p);sys.modules["resource_boot"]=m
    exec(compile(raw,str(p),"exec"),m.__dict__);loaded=m.load()
    return loaded,m.loaded_sources(loaded["build_profile"].__dict__)

def runtime(root):
    root=Path(root).resolve(strict=True);p=root/"COPIED-FILES.json"
    if L.stamp(root/"SEAL.json")["sha256"]!=L.SNAPSHOT_SEAL or L.stamp(p)["sha256"]!=RUNTIME_MANIFEST:raise ValueError("RUNTIME_SNAPSHOT_BINDING")
    raw=p.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=RUNTIME_MANIFEST:raise ValueError("RUNTIME_CONSUMED_MANIFEST")
    value=json.loads(raw);files=[];stdlib=[];special={}
    for item in value["files"]:
        p=root/item["snapshot"];r=L.stamp(p)
        if {k:r[k] for k in ("sha256","bytes")}!={k:item["copy"][k] for k in ("sha256","bytes")}:raise ValueError("RUNTIME_COPY_DRIFT")
        role=item["role"]
        if role=="stdlib_source":stdlib.append({"source":r,"guest":item["guest"],"access":"read"})
        elif role in ("aa_exec","supervisor_bwrap"):special[role]=r
        else:files.append({"source":r,"guest":item["guest"],"access":"executable" if role=="python" else "library"})
    if len(value["files"])!=744 or len(stdlib)!=734 or len(files)!=8:raise ValueError("RUNTIME_SET")
    std=root/"payload"/Path(L.B.DEFAULT["executable"]).relative_to("/").parents[1]/"lib/python3.11"
    return files,special,std,stdlib

def prepare(root,runtime_root,*,run_id,mode,duration_ns,cpu,input_value,review):
    start=time.monotonic();cpu_start=time.process_time();root=Path(root).resolve();root.mkdir();L.sync_dir(root.parent)
    source_root=Path(__file__).resolve().parents[2];source_before=D.sources();loaded,drivers=resources()
    inv=loaded["build_profile_policy"].inventory
    files,special,std,stdlib=runtime(runtime_root);L.read(review["path"],review["sha256"])
    (root/"work").mkdir();(root/"work/home").mkdir()
    project=root/"project";project.mkdir()
    for rel,digest in source_before.items():
        src=source_root/rel;raw=src.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError("PREPARATION_SOURCE_DRIFT")
        dest=project/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        with dest.open("xb") as f:
            f.write(raw);f.flush();os.fchmod(f.fileno(),0o444);os.fsync(f.fileno())
    for folder,_,_ in os.walk(project,topdown=False):L.sync_dir(folder)
    copied={str(p.relative_to(project)):L.stamp(p)["sha256"] for p in project.rglob("*") if p.is_file()}
    if copied!=source_before or D.sources()!=source_before:raise ValueError("PREPARATION_COPY_DRIFT")
    inp=None
    if input_value is not None:
        r=L.write(root/"INPUT.json",input_value);inp={k:r[k] for k in ("sha256","bytes")}
    value=L.plan({"schema":"ocm.unary-launch-plan.v1","run_id":run_id,"mode":mode,"duration_ns":duration_ns,"cpu":cpu,
        "sources":source_before,"input":inp,"python":L.B.DEFAULT,"runtime_seal":L.SNAPSHOT_SEAL,"mapping_seal":L.MAPPING_SEAL})
    if cpu!=min(os.sched_getaffinity(0)):raise ValueError("PREPARATION_LOWEST_CPU")
    plan=L.write(root/"PLAN.json",value)
    project_inventory=L.write(root/"PROJECT-INVENTORY.json",inv(project))
    # Python requires both the source directory tree and its empty native landmark.
    stdcopy=root/"stdlib";stdcopy.mkdir();copy_start=time.monotonic();copy_cpu=time.process_time();copied_std={}
    guest_std=Path(L.B.DEFAULT["executable"]).parents[1]/"lib/python3.11"
    for item in stdlib:
        rel=str(Path(item["guest"]).relative_to(guest_std));dest=stdcopy/rel
        raw=Path(item["source"]["path"]).read_bytes()
        if len(raw)!=item["source"]["bytes"] or hashlib.sha256(raw).hexdigest()!=item["source"]["sha256"]:raise ValueError("STDLIB_CONSUMED_SOURCE")
        dest.parent.mkdir(parents=True,exist_ok=True)
        with dest.open("xb") as f:
            f.write(raw);f.flush();os.fchmod(f.fileno(),0o444);os.fsync(f.fileno())
        copied_std[rel]=item["source"]["sha256"]
    (stdcopy/"lib-dynload").mkdir()
    for folder,_,_ in os.walk(stdcopy,topdown=False):L.sync_dir(folder)
    L.sync_dir(root)
    after={str(p.relative_to(stdcopy)):L.stamp(p)["sha256"] for p in stdcopy.rglob("*") if p.is_file()}
    if after!=copied_std:raise ValueError("STDLIB_COPY_DRIFT")
    std_inventory=L.write(root/"STDLIB-INVENTORY.json",inv(stdcopy))
    lineage=L.write(root/"STDLIB-COPY.json",{"sources":stdlib,"copied_sha256":after,"added_empty_directories":["lib-dynload"],
        "wall_s":time.monotonic()-copy_start,"own_cpu_s":time.process_time()-copy_cpu})
    template={"schema":"ocm.f1.build-profile.v1","bwrap":special["supervisor_bwrap"],"aa_exec":special["aa_exec"],
      "files":files+[{"source":plan,"guest":L.PLAN,"access":"read"}],
      "materials":[{"path":str(project),"guest":L.PROJECT,"inventory":project_inventory},
                   {"path":str(stdcopy),"guest":str(guest_std),"inventory":std_inventory}],
      "writable":[{"path":str(root/"work"),"guest":L.WORK}],
      "environment":{"HOME":L.WORK+"/home","TMPDIR":"/tmp","LANG":"C.UTF-8","LC_ALL":"C.UTF-8","TZ":"UTC","PATH":"/no-ambient-tools"},
      "argv":[L.B.DEFAULT["executable"],"-I","-S","-B",L.BOOT,plan["sha256"],"DYNAMIC_BINDING_SHA256"]}
    if inp is not None:template["files"].append({"source":L.stamp(root/"INPUT.json"),"guest":L.INPUT,"access":"read"})
    result={"schema":"ocm.unary-launch-prepared.v1","plan":plan,"template":template,"driver_sources":drivers,"review":review,"limits":L.LIMITS,"stdlib_copy":lineage,
            "preparation_wall_s":time.monotonic()-start,"preparation_own_cpu_s":time.process_time()-cpu_start}
    L.write(root/"PREPARED.json",result);return result

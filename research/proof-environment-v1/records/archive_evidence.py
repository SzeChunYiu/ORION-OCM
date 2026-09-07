"""Deterministic evidence archival only; no native commands or archive extraction."""
from pathlib import Path
import gzip,hashlib,io,json,tarfile,time
BASE=Path("/home/billy/orion-director-work/20260907")
OUT=BASE/"ocm-proof-environment/research/proof-environment-v1/records"
GROUPS={
 "final-commissioning":[("proof-environment-commissioning-20260907-v1","")],
 "registration-and-envelope":[(n,n) for n in ("proof-environment-commissioning-envelope-20260907-v1","proof-environment-freeze-20260907-v1","proof-environment-registration-20260907-v1")],
 "final-profile":[("proof-environment-final-profile-20260907-v1","")],
 "runtime-authority":[("proof-environment-final-package-authority-20260907-v1","")],
 "native-build-custody":[("proof-environment-final-runtime-1cf7eca5-20260907T033758","")],
 "runtime-package-metadata":[("proof-environment-qualified-runtime-20260907-v1","")],
 "development-history":[("proof-environment-development","")],
}
def record(path):
 h=hashlib.sha256();size=0
 with path.open("rb") as f:
  for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk);size+=len(chunk)
 return {"sha256":h.hexdigest(),"bytes":size}
def put(name,data):
 p=OUT/name
 with p.open("xb") as f:f.write((json.dumps(data,sort_keys=True,indent=2)+"\n").encode())
 return record(p)
class HashSink:
 def __init__(self):self.h=hashlib.sha256();self.n=0
 def write(self,data):self.h.update(data);self.n+=len(data);return len(data)
 def flush(self):pass
 def result(self):return {"sha256":self.h.hexdigest(),"bytes":self.n}
def emit(sink,files):
 with gzip.GzipFile(filename="",mode="wb",fileobj=sink,mtime=0,compresslevel=9) as gz:
  with tarfile.open(fileobj=gz,mode="w|",format=tarfile.PAX_FORMAT) as tar:
   for name,(path,binding) in sorted(files.items()):
    info=tarfile.TarInfo(name);info.size=binding["bytes"];info.mode=0o644
    info.uid=info.gid=info.mtime=0;info.uname=info.gname=""
    with path.open("rb") as stream:tar.addfile(info,stream)
def verify_archive(path,members):
 seen={}
 with tarfile.open(path,mode="r|gz") as tar:
  for m in tar:
   assert m.isfile() and m.name not in seen,m.name
   assert m.mode==0o644 and m.uid==m.gid==m.mtime==0,m.name
   stream=tar.extractfile(m);h=hashlib.sha256();size=0
   for chunk in iter(lambda:stream.read(1024*1024),b""):h.update(chunk);size+=len(chunk)
   seen[m.name]={"sha256":h.hexdigest(),"bytes":size}
 assert seen==members,"archive member custody differs"
 return len(seen)
def main():
 started=time.monotonic();omitted={};groups={}
 for label,roots in GROUPS.items():
  begin=time.monotonic();files={};all_records={}
  for dirname,prefix in roots:
   root=BASE/dirname
   for p in sorted(root.rglob("*")):
    assert not p.is_symlink(),str(p)
    if not p.is_file():continue
    rel=str(p.relative_to(root));name=str(Path(prefix)/rel)
    assert not any(x in (".git",".lake","__pycache__") for x in Path(rel).parts),str(p)
    assert name not in all_records,name
    binding=record(p);all_records[name]=(p,binding)
    with p.open("rb") as f:is_elf=f.read(4)==b"\x7fELF"
    if is_elf:
     assert label not in ("final-commissioning","registration-and-envelope","final-profile","runtime-authority")
     omitted[label+"/"+name]={"source_path":str(p),**binding,"reason":"ELF payload retained externally; original authoritative source path and exact content identity preserved"}
    else:files[name]=(p,binding)
  members={name:binding for name,(_,binding) in files.items()}
  if label=="final-commissioning":
   assert len(members)==681 and sum(r["bytes"] for r in members.values())==66843845
   assert members["seal.json"]["sha256"]=="67476a9394ad8ebe945ca3f1105ad893574ba0712df8a0e7ceb238ae42867fc9"
   seal=json.loads(files["seal.json"][0].read_text())
   assert seal["evidence_complete"] is True and seal["terminal"]=="CONTROLS_PASSED"
   assert seal["files"]=={k:v for k,v in members.items() if k!="seal.json"}
  mp=label+".members.json";member_binding=put(mp,members)
  archive=OUT/(label+".tar.gz")
  with archive.open("xb") as f:emit(f,files)
  archive_binding=record(archive)
  count=verify_archive(archive,members)
  sink=HashSink();emit(sink,files)
  assert sink.result()==archive_binding,"second deterministic stream differs"
  for name,(p,binding) in all_records.items():assert record(p)==binding,"original drift: "+str(p)
  groups[label]={"archive":{"path":archive.name,**archive_binding},"members":{"path":mp,**member_binding},"original_roots":[{"path":str(BASE/n),"archive_prefix":prefix} for n,prefix in roots],"member_count":count,"member_bytes":sum(x["bytes"] for x in members.values()),"original_file_count":len(all_records),"original_bytes":sum(x[1]["bytes"] for x in all_records.values()),"omitted_elf_count":len(all_records)-count,"all_originals_rehashed_after_archiving":True,"deterministic_second_stream_identical":True,"wall_s":time.monotonic()-begin}
  print(json.dumps({"completed":label,**groups[label]["archive"],"members":count,"omitted":len(all_records)-count}),flush=True)
 omission_binding=put("OMITTED_ELF_FILES.json",omitted)
 runtime=json.loads((BASE/"proof-environment-qualified-runtime-20260907-v1/runtime.json").read_text())
 build=json.loads((BASE/"proof-environment-final-runtime-1cf7eca5-20260907T033758/BUILD-CUSTODY.json").read_text())
 external={"schema":"ocm.proof-environment.external-prerequisites.v1","scope":"Previously bound prerequisites outside these archived input roots; records copied from retained audit, not re-executed or newly downloaded","host_python":runtime["host_python"],"prior_toolchain_inventory":build["prior_toolchain"],"release_archive":build["release_archive"],"selected_toolchain_files_verified_by_prior_audit":build["selected_toolchain_files_verified"]}
 external_binding=put("EXTERNAL_PREREQUISITES.json",external)
 manifest={"schema":"ocm.proof-environment.evidence-archives.v1","terminal":"ARCHIVED_AND_BYTE_VERIFIED","groups":groups,"omitted_elf_files":{"path":"OMITTED_ELF_FILES.json",**omission_binding},"external_prerequisites":{"path":"EXTERNAL_PREREQUISITES.json",**external_binding},"archiver":{"path":"archive_evidence.py",**record(OUT/"archive_evidence.py")},"format":"Sorted regular files only, root-relative or declared prefix; PAX tar with uid/gid/mtime0 mode0644 empty owner names, gzip mtime0 filename empty level9","verification":"Streamed full member digest equality, identical second compressed stream, and post-archive hashes of every original including omitted ELF payloads","wall_s":time.monotonic()-started,"native_calls":0,"originals_modified":False,"whole_worktree_or_lake_cache_archived":False}
 put("MANIFEST.json",manifest)
 print(json.dumps({"manifest":record(OUT/"MANIFEST.json"),"groups":len(groups),"omitted_files":len(omitted),"omitted_bytes":sum(x["bytes"] for x in omitted.values()),"archive_bytes":sum(x["archive"]["bytes"] for x in groups.values()),"wall_s":manifest["wall_s"]}),flush=True)
if __name__=="__main__":main()

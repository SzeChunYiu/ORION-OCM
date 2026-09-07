"""Create-only deterministic evidence archive. Metadata/file copying only."""
from pathlib import Path
import gzip,hashlib,json,os,stat,tarfile,time
import xml.etree.ElementTree as ET

BASE=Path("/home/billy/orion-director-work/20260907")
WORK=BASE/"ocm-corpus-material/research/proof-corpus-coverage-v1"
OUT=WORK/"acquisition-qualification-records"
ROOTS={"worker":BASE/"acquisition-git-controls-v1","phase":BASE/"acquisition-qualification-v1",
 "phase-initial":BASE/"acquisition-phase-controls-v1","helper-smoke":BASE/"acquisition-helper-smoke-v1",
 "lake":BASE/"lake-build-qualification-v1","lake-review":BASE/"lake-build-independent-review-v1",
 "lock-input":BASE/"acquisition-lock-input-v1"}
started=time.monotonic()
def bind(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
 return {"sha256":h.hexdigest(),"bytes":p.stat().st_size}
def save(name,value):
 with (OUT/name).open("x") as f:json.dump(value,f,sort_keys=True,indent=2);f.write("\n")
def fail(e):raise e
sources={};omitted_special=[]
for prefix,root in ROOTS.items():
 for parent,dirs,files in os.walk(root,followlinks=False,onerror=fail):
  for name in dirs+files:
   p=Path(parent)/name;member=prefix+"/"+str(p.relative_to(root));mode=p.lstat().st_mode
   if stat.S_ISREG(mode):sources[member]=p
   elif not stat.S_ISDIR(mode):
    omitted_special.append({"member":member,"origin":str(p),"mode":mode,
      "kind":"symlink" if stat.S_ISLNK(mode) else "fifo" if stat.S_ISFIFO(mode) else "unsupported",
      "target":os.readlink(p) if stat.S_ISLNK(mode) else None,
      "reason":"No regular-file bytes; do not follow pytest aliases or read the authored FIFO refusal fixture."})
runtime=Path("/home/billy/orion-director-work/20260906/f0-development-runtime-v4/runtime-manifest.json")
assert bind(runtime)["sha256"]=="93aa17a738a8511bbb8996eff91e81da0ec5868db50d0f81ab26809e38661894"
sources["external-bindings/runtime-manifest.json"]=runtime
groups={}
for label,process in (("phase04-historical","phase.04.process.json"),("phase05-current","phase.05.process.json")):
 record=json.loads((ROOTS["phase"]/process).read_bytes())
 assert record["sources_before"]==record["sources_after"] and record["returncode"]==0
 groups[label]={}
 for name,expected in record["sources_before"].items():
  choices=[WORK/name,ROOTS["helper-smoke"]/"sources"/name,
           BASE/"coverage-material-episode-v1/sources"/name]
  origin=next((p for p in choices if p.is_file() and bind(p)==expected),None)
  assert origin is not None,(label,name,expected)
  member="source-generations/"+label+"/"+name;sources[member]=origin
  groups[label][name]={**expected,"member":member,"origin":str(origin)}
manifest={name:bind(path) for name,path in sorted(sources.items())}
assert all(not Path(n).is_absolute() and ".." not in Path(n).parts for n in manifest)
origins={name:str(path) for name,path in sorted(sources.items())}
external={}
def visit(value):
 if isinstance(value,dict):
  p=value.get("path");h=value.get("sha256");size=value.get("bytes")
  if isinstance(p,str) and p.startswith("/") and isinstance(h,str) and len(h)==64 and type(size) is int:
   external[(p,h,size)]={"path":p,"sha256":h,"bytes":size}
  for key,item in value.items():
   if isinstance(key,str) and key.startswith("/") and isinstance(item,dict) and "sha256" in item and "bytes" in item:
    visit({"path":key,**item})
   visit(item)
 elif isinstance(value,list):
  for item in value:visit(item)
for name,p in sources.items():
 if p.suffix==".json":
  try:visit(json.loads(p.read_bytes()))
  except (ValueError,UnicodeError):pass
retained_by_hash={}
for name,value in manifest.items():retained_by_hash.setdefault((value["sha256"],value["bytes"]),name)
external_rows=[]
for key,value in sorted(external.items()):
 if (value["sha256"],value["bytes"]) not in retained_by_hash:
  external_rows.append({**value,"disposition":"EXTERNAL_BYTES_NOT_COPIED_OR_REVALIDATED_BY_PACKAGING"})
runtime_data=json.loads(runtime.read_bytes())
runtime_summary={"root":runtime_data["lean_root"],"entries":len(runtime_data["lean_files"]),
 "regular_files":sum(v.get("kind")=="file" for v in runtime_data["lean_files"].values()),
 "regular_bytes":sum(v.get("bytes",0) for v in runtime_data["lean_files"].values() if v.get("kind")=="file"),
 "archive_bytes":runtime_data["archive_bytes"],"archive_sha256":runtime_data["archive_sha256"],
 "retained_inventory":"external-bindings/runtime-manifest.json",
 "scope":"Prior exact inventories are retained; the installed distribution/archive and shared-library bodies are not copied or requalified here."}
save("qualification.members.json",manifest);save("ORIGINS.json",origins)
save("SOURCE-GENERATIONS.json",groups)
save("OMISSIONS.json",{"nonregular_authored_entries":omitted_special,"external_bound_files":external_rows,
 "installed_runtime":runtime_summary,
 "real_corpus_episodes":"Outside this authored qualification package; root packages actual v1/v2 acquisition episodes separately.",
 "historical_limit":"Early development logs are retained as historical records; only named current/historical source-generation maps establish the corresponding frozen byte sets."})
archive=OUT/"qualification.tar.gz"
with archive.open("xb") as raw,gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0,compresslevel=9) as compressed:
 with tarfile.open(fileobj=compressed,mode="w",format=tarfile.PAX_FORMAT) as tar:
  for name,path in sorted(sources.items()):
   info=tarfile.TarInfo(name);info.size=manifest[name]["bytes"];info.mode=0o644
   info.uid=info.gid=info.mtime=0;info.uname=info.gname=""
   with path.open("rb") as data:tar.addfile(info,data)
observed={}
with tarfile.open(archive,"r:gz",ignore_zeros=True) as tar:
 for member in tar:
  assert member.isfile() and member.name in manifest and member.name not in observed,member.name
  h=hashlib.sha256();n=0
  with tar.extractfile(member) as data:
   for block in iter(lambda:data.read(1024*1024),b""):h.update(block);n+=len(block)
  observed[member.name]={"sha256":h.hexdigest(),"bytes":n}
assert observed==manifest
assert all(bind(path)==manifest[name] for name,path in sources.items()),"ORIGINAL_DRIFT"
for prefix,root in ROOTS.items():
 current={prefix+"/"+str((Path(parent)/n).relative_to(root)) for parent,dirs,files in os.walk(root,followlinks=False,onerror=fail)
          for n in files if stat.S_ISREG((Path(parent)/n).lstat().st_mode)}
 assert current=={n for n in manifest if n.startswith(prefix+"/")},"ORIGINAL_FILE_SET_DRIFT"
def counts(p):
 suites=ET.parse(p).getroot().iter("testsuite")
 total={"tests":0,"failures":0,"errors":0,"skipped":0}
 for suite in suites:
  for key in total:total[key]+=int(suite.attrib.get(key,0))
 return total
checks={"worker_current":counts(ROOTS["worker"]/"final.xml"),
 "phase04_historical":counts(ROOTS["phase"]/"phase.04.xml"),
 "phase05_current":counts(ROOTS["phase"]/"phase.05.xml"),
 "lake_current":counts(ROOTS["lake"]/"07-final-tests/tests.xml")}
for name,wanted in (("worker_current",25),("phase04_historical",29),("phase05_current",31),("lake_current",14)):
 assert checks[name]=={"tests":wanted,"failures":0,"errors":0,"skipped":0}
save("QUALIFICATION-COUNTS.json",checks)
save("VERIFY.json",{"terminal":"ARCHIVE_BYTE_CUSTODY_PASS","members":len(manifest),
 "raw_bytes":sum(v["bytes"] for v in manifest.values()),"archive":bind(archive),
 "all_archived_member_bytes_match_originals":True,"all_original_sources_unchanged":True,
 "readback":"tarfile regular-member stream; no extraction or execution; trailing zero blocks do not hide appended members.",
 "elapsed_packaging_and_readback_wall_s":time.monotonic()-started})
save("INDEX.json",{"schema":"ocm.authored-acquisition-qualification-package.v1",
 "terminal":"QUALIFICATION_EVIDENCE_PACKAGED","members":len(manifest),
 "raw_bytes":sum(v["bytes"] for v in manifest.values()),"archive":bind(archive),
 "manifest":bind(OUT/"qualification.members.json"),"groups":{k:str(v) for k,v in ROOTS.items()},
 "source_generations":{"phase04-historical":6,"phase05-current":10},
 "scope":"Authored Git/phase/helper/Lake qualification only. Not actual corpus acquisition, coverage, proof reconstruction or learning."})
print(json.dumps({"members":len(manifest),"raw_bytes":sum(v["bytes"] for v in manifest.values()),
 "archive":bind(archive),"manifest":bind(OUT/"qualification.members.json"),
 "external_bound_omissions":len(external_rows),"nonregular_omissions":len(omitted_special),
 "runtime":runtime_summary,"qualification":checks},sort_keys=True))

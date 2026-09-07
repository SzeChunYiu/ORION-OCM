"""Lossless regular-byte packaging only; no extracted source is executed."""
from pathlib import Path
import gzip,hashlib,json,os,stat,tarfile,time
import xml.etree.ElementTree as ET
BASE=Path("/home/billy/orion-director-work/20260907")
WORK=BASE/"ocm-corpus-material/research/proof-corpus-coverage-v1"
RAW=BASE/"corpus-layout-qualification-v1"
OUT=WORK/"corpus-layout-records"
ROOTS={"qualification":RAW,"read-record":BASE/"corpus-layout-read-record-qualification-v1",
       "preflight":BASE/"corpus-layout-preflight-qualification-v1"}
started=time.monotonic()
def bind(p):
 h=hashlib.sha256();size=0
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1024**2),b""):h.update(b);size+=len(b)
 return {"sha256":h.hexdigest(),"bytes":size}
def save(name,value):
 with (OUT/name).open("x") as f:json.dump(value,f,sort_keys=True,indent=2);f.write("\n")
def gzjson(name,value):
 b=(json.dumps(value,sort_keys=True,separators=(",",":"))+"\n").encode()
 with (OUT/name).open("xb") as f,gzip.GzipFile(filename="",mode="wb",fileobj=f,mtime=0,compresslevel=9) as g:g.write(b)
def fail(e):raise e
def scan():
 sources={};metadata={};inodes={}
 for prefix,root in ROOTS.items():
  assert root.is_dir() and not root.is_symlink(),root
  for base,dirs,files in os.walk(root,followlinks=False,onerror=fail):
   for name in dirs+files:
    p=Path(base)/name;s=p.lstat();key=prefix+"/"+p.relative_to(root).as_posix()
    assert not Path(key).is_absolute() and ".." not in Path(key).parts
    row={"mode":stat.S_IMODE(s.st_mode),"mtime_ns":s.st_mtime_ns}
    if stat.S_ISREG(s.st_mode):
     sources[key]=p;row["kind"]="regular"
     if s.st_nlink>1:inodes.setdefault((s.st_dev,s.st_ino),[]).append(key)
    elif stat.S_ISDIR(s.st_mode):row["kind"]="directory"
    elif stat.S_ISLNK(s.st_mode):row.update(kind="symlink",target=os.readlink(p))
    else:row["kind"]="special"
    metadata[key]=row
 return sources,metadata,[v for v in inodes.values() if len(v)>1]
sources,metadata,hardlinks=scan()
# These temporary roots contain only this authored module's fixture names.
for prefix in ROOTS:
 if prefix.startswith("early"):
  tops={Path(k).parts[1] for k in metadata if k.startswith(prefix+"/")}
  assert tops and all(n.startswith("test_") or n==".lock" for n in tops),tops
manifest={k:bind(p) for k,p in sorted(sources.items())}
before=json.loads((RAW/"05-final/SOURCE.json").read_bytes())
assert before==json.loads((RAW/"05-final/SOURCE-AFTER.json").read_bytes())
for n,s in before.items():assert bind(RAW/"05-final/source"/n)==s
targeted=json.loads((ROOTS["preflight"]/"03-green/SOURCE.json").read_bytes())
assert targeted==json.loads((ROOTS["preflight"]/"03-green/SOURCE-AFTER.json").read_bytes())
for n,value in targeted.items():
 assert bind(WORK/n)==value and bind(ROOTS["preflight"]/"03-green/source"/n)==value
current={n:{**value,"member":"preflight/03-green/source/"+n} for n,value in targeted.items()}
OUT.mkdir()
gzjson("MEMBERS.json.gz",manifest);gzjson("ENTRY-METADATA.json.gz",{"entries":metadata,"hardlink_groups":hardlinks})
save("ROOTS.json",{k:str(v) for k,v in ROOTS.items()})
save("SOURCE-BINDINGS.json",{"current_targeted_closure":current,"current_layout_owned":["corpus_layout.py","test_corpus_layout.py"],
 "historical_21_control_closure":before,
 "scope":"The current nine-file snapshot binds seven focused boundary controls. The historical nine-file snapshot binds the earlier 21 controls. These are distinct generations; no additive test or full-current-suite claim."})
external={}
def visit(x):
 if isinstance(x,dict):
  path=x.get("path");h=x.get("sha256");size=x.get("bytes")
  if isinstance(path,str) and path.startswith("/") and isinstance(h,str) and len(h)==64 and type(size)is int:
   if not any(Path(path).is_relative_to(root) for root in ROOTS.values()):
    external[(path,h,size)]={"path":path,"sha256":h,"bytes":size}
  for v in x.values():visit(v)
 elif isinstance(x,list):
  for v in x:visit(v)
for p in sources.values():
 if p.suffix==".json":
  try:visit(json.loads(p.read_bytes()))
  except (ValueError,UnicodeError):pass
save("OMISSIONS.json",{"symlinks_not_followed_or_archived":sum(v["kind"]=="symlink" for v in metadata.values()),
 "special_entries_not_read":sum(v["kind"]=="special" for v in metadata.values()),
 "entry_inventory":"ENTRY-METADATA.json.gz",
 "directories":"Names, modes and timestamps retained as metadata; tar stores regular payloads only.",
 "hardlinks":"Every regular path is archived as independent bytes; original grouped paths are recorded.",
 "external_bound_files":[{**v,"disposition":"EXTERNAL_BYTES_NOT_COPIED_OR_REVALIDATED"} for _,v in sorted(external.items())],
 "external_scope":"Structured path/hash/byte references in archived JSON only; not a complete Python, pytest, stdlib or Git dynamic-runtime inventory.",
 "initial_red_temporary_root":"/tmp/pytest-of-billy/pytest-357 is absent; initial tests failed before fixture creation. Logs/JUnit and initial test bytes remain.",
 "early_fixture_bodies":"Earlier default pytest temporary trees were not protected snapshots and were not archived. A collection preflight observed pytest-358 already removed and refused before package creation. Earlier logs/JUnit and source generations, plus all final authored fixture bytes, remain retained.",
 "real_corpus":"No actual corpus materials or upstream proof bodies are included or processed by this archive."})
archive=OUT/"qualification.tar.gz"
with archive.open("xb") as f,gzip.GzipFile(filename="",mode="wb",fileobj=f,mtime=0,compresslevel=9) as g:
 with tarfile.open(fileobj=g,mode="w",format=tarfile.PAX_FORMAT) as tar:
  for name,path in sorted(sources.items()):
   item=tarfile.TarInfo(name);item.size=manifest[name]["bytes"];item.mode=0o644
   item.uid=item.gid=item.mtime=0;item.uname=item.gname=""
   with path.open("rb") as body:tar.addfile(item,body)
observed={}
with tarfile.open(archive,"r:gz",ignore_zeros=True) as tar:
 for item in tar:
  assert item.isfile() and item.name in manifest and item.name not in observed
  with tar.extractfile(item) as f:
   data=f.read()
  observed[item.name]={"sha256":hashlib.sha256(data).hexdigest(),"bytes":len(data)}
assert observed==manifest
assert all(bind(p)==manifest[k] for k,p in sources.items())
now,after,groups=scan();assert set(now)==set(sources) and after==metadata and groups==hardlinks
counts={}
for prefix,relative in [("qualification",n) for n in ("01-red.xml","02-green.xml","03-red.xml","04-green.xml","05-final/tests.xml")]+[("read-record",n) for n in ("01-red.xml","02-green/tests.xml")]+[("preflight",n) for n in ("01-red.xml","02-red.xml","03-green/tests.xml")]:
 suites=list(ET.parse(ROOTS[prefix]/relative).getroot().iter("testsuite"))
 counts[prefix+"/"+relative]={k:sum(int(s.get(k,"0")) for s in suites) for k in ("tests","failures","errors","skipped")}
assert counts["qualification/05-final/tests.xml"]=={"tests":21,"failures":0,"errors":0,"skipped":0}
assert counts["preflight/03-green/tests.xml"]=={"tests":7,"failures":0,"errors":0,"skipped":0}
save("GENERATIONS.json",{"counts":counts,
 "01-red":"Absent module; initial test bytes retained in qualification/03-predecessor/test_corpus_layout.py.",
 "02-green":"Predecessor module and tests retained in qualification/03-predecessor; 16-pass log/JUnit.",
 "03-red":"Predecessor module plus final 21-control tests; three demonstrated late-layout failures.",
 "04-green":"Repaired module/final tests as retained in the final snapshot; 21-pass log/JUnit.",
 "05-final":"Contemporaneous nine-source before/after freeze, process envelope and retained authored fixture trees.",
 "historical_scope":"Earlier source associations are retrospective development lineage, not a newly issued native/source qualification.",
 "read_record_successor":"Two hostile controls failed, clean control passed; consumed byte/hash/deadline repair then passed all three targeted controls.",
 "preflight_successor":"Initial hostile decoy was an ancestor and correctly hit old overlap refusal; corrected disjoint decoy reproduced the write-before-refusal defect. Bound preflight reader then passed seven focused controls.",
 "fixture_successor":"Historical21 uses test_materialize_git.py cfb8e01c; current targeted7 uses portable fixture successor1f3f71be. Neither receipt is rebound to the other generation."})
save("VERIFY.json",{"terminal":"LAYOUT_ARCHIVE_BYTE_CUSTODY_PASS","members":len(manifest),
 "raw_bytes":sum(v["bytes"] for v in manifest.values()),"archive":bind(archive),
 "all_members_rehashed_against_originals":True,"original_entry_sets_and_metadata_unchanged":True,
 "scope":"Readback of regular tar streams without extraction/execution; no rerun, actual layout or profile qualification.",
 "packaging_and_readback_wall_s":time.monotonic()-started})
save("INDEX.json",{"schema":"ocm.corpus-layout-archive.v1","terminal":"AUTHORED_LAYOUT_EVIDENCE_PACKAGED",
 "archive":bind(archive),"members_map":bind(OUT/"MEMBERS.json.gz"),"members":len(manifest),
 "raw_bytes":sum(v["bytes"] for v in manifest.values()),"roots":list(ROOTS),
 "current_layout_sources":2,"current_targeted_snapshot_sources":len(targeted),
 "historical_snapshot_sources":len(before),"historical_authored_passed":21,"current_targeted_passed":7,
 "scope":"Authored layout-copy controls only. Actual corpus materialization, layout, build and semantic execution remain undispatched."})
print(json.dumps({"members":len(manifest),"raw_bytes":sum(v["bytes"] for v in manifest.values()),
 "archive":bind(archive),"map":bind(OUT/"MEMBERS.json.gz"),
 "symlinks":sum(v["kind"]=="symlink" for v in metadata.values()),"external_bound_files":len(external)}))

"""One fresh-process observer; hashes are custody work, not syntax experiments."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
OUT=ROOT/"qualification-01"
def pin(p):
 b=p.read_bytes();return {"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}
def write(p,value):
 with p.open("x") as handle:
  json.dump(value,handle,indent=2,sort_keys=True,allow_nan=False);handle.write("\n")
assert not OUT.exists(),"create-only qualification"
OUT.mkdir()
lark=json.loads((BASE/"donor/LARK-FILES.json").read_bytes())["files"]
paths=[ROOT/"check_coverage.py",Path(__file__).resolve(),Path(sys.executable).resolve()]
paths+=list((ROOT/"source").glob("*.py"))
paths+=[BASE/"donor/lark-runtime"/name for name in lark]
# Pre-pin the isolated interpreter's standard library sources/extensions so every
# file-backed imported module can later be reconciled, including lazy imports.
stdlib=Path(sys.executable).resolve().parent.parent/"lib/python3.11"
paths += [p for p in stdlib.rglob("*") if p.is_file() and
          "site-packages" not in p.parts and p.suffix in {".py",".so"}]
paths=sorted(set(p.resolve() for p in paths))
before={str(p):pin(p) for p in paths}
for name,expected in lark.items():
 assert before[str((BASE/"donor/lark-runtime"/name).resolve())]==expected
historical=[BASE/"source/syntax_engine.py",BASE/"SOURCE-FREEZE.json",
 BASE/"SOURCE-REVIEW-REQUEST.json",BASE/"QUALIFICATION.json",
 BASE/"qualification-01/PROCESS.json"]
old_before={str(p):pin(p) for p in historical}
write(OUT/"PINS-BEFORE.json",before);write(OUT/"HISTORY-BEFORE.json",old_before)
argv=[sys.executable,"-I","-S","-B",str(ROOT/"check_coverage.py"),str(OUT)]
started=time.perf_counter()
with (OUT/"stdout.txt").open("xb") as stdout,(OUT/"stderr.txt").open("xb") as stderr:
 child=subprocess.Popen(argv,cwd=ROOT,stdout=stdout,stderr=stderr)
 pid,status,usage=os.wait4(child.pid,0)
 child.returncode=os.waitstatus_to_exitcode(status)
wall=time.perf_counter()-started
after={str(p):pin(p) for p in paths}
old_after={str(p):pin(p) for p in historical}
write(OUT/"PINS-AFTER.json",after);write(OUT/"HISTORY-AFTER.json",old_after)
control=json.loads((OUT/"CONTROLS.json").read_bytes()) if (OUT/"CONTROLS.json").exists() else None
imports=control["imported_modules"] if control else {}
uncovered={name:row for name,row in imports.items()
 if before.get(row["path"])!={"bytes":row["bytes"],"sha256":row["sha256"]}}
receipt={"schema":"ordinary.syntax-coverage-process.v1","observer_pid":os.getpid(),
 "pid":pid,"argv":argv,"cwd":str(ROOT),"exit_code":child.returncode,
 "child_window_wall_s":wall,"child_user_s":usage.ru_utime,"child_system_s":usage.ru_stime,
 "child_peak_rss_kib":usage.ru_maxrss,"before_after_equal":before==after,
 "history_unchanged":old_before==old_after,"pinned_file_count":len(paths),
 "imported_file_module_count":len(imports),"uncovered_imported_modules":uncovered,
 "child_identity_matches":bool(control and control["pid"]==pid and control["parent_pid"]==os.getpid()
 and control["cwd"]==str(ROOT) and control["python"]==sys.executable),
 "controls":pin(OUT/"CONTROLS.json") if control else None,
 "timing_scope":"Popen through log closure/wait4; source/import custody and observer setup/serialization excluded."}
write(OUT/"PROCESS.json",receipt)
print(json.dumps(receipt,sort_keys=True))
assert child.returncode==0 and control and control["success"]
assert before==after and old_before==old_after and not uncovered and receipt["child_identity_matches"]

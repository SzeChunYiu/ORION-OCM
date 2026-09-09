"""Run authored output controls and the exact missing-gate startup refusal only."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time
HERE=Path(__file__).resolve().parent
RUN=HERE
PYTHON=Path("/home/billy/.local/share/uv/python/cpython-3.11.14-linux-x86_64-gnu/bin/python3.11")
def identity(p):
 raw=p.read_bytes();return {"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
def write(path,value):
 with path.open("x") as f:f.write(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+"\n")
def observed(name,argv,root):
 before={n:identity(HERE/n) for n in ("observe_screening.py","output_contract.py","check_outputs.py","OBSERVER-CONTRACT.json","EXECUTION-REQUEST-DRAFT.json","qualify.py")}
 start=time.perf_counter()
 with (root/(name+".stdout.txt")).open("xb") as out,(root/(name+".stderr.txt")).open("xb") as err:
  child=subprocess.Popen(argv,cwd="/tmp",stdin=subprocess.DEVNULL,stdout=out,stderr=err,
       env={"PATH":"/usr/bin:/bin","LANG":"C.UTF-8"},start_new_session=True)
  pid,status,usage=os.wait4(child.pid,0)
  child.returncode=os.waitstatus_to_exitcode(status)
 after={n:identity(HERE/n) for n in before}
 receipt={"argv":argv,"cwd":"/tmp","pid":child.pid,"parent_pid":os.getpid(),"reaped":pid==child.pid,
  "exit_code":child.returncode,"wall_s":time.perf_counter()-start,"user_s":usage.ru_utime,
  "system_s":usage.ru_stime,"rss_kib":usage.ru_maxrss,"sources_before":before,"sources_after":after,
  "stdout":identity(root/(name+".stdout.txt")),"stderr":identity(root/(name+".stderr.txt"))}
 write(root/(name+".PROCESS.json"),receipt)
 return receipt
assert Path(sys.executable)==PYTHON and sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode
root=HERE/"qualification-01";root.mkdir()
pin_paths={p.resolve() for p in HERE.parent.rglob("*.py") if "history" not in p.parts}
stdlib=PYTHON.parent.parent/"lib/python3.11"
pin_paths.update(p.resolve() for p in stdlib.rglob("*") if p.is_file() and p.suffix in {".py",".so"})
pin_paths.add(PYTHON)
full_before={str(p):identity(p) for p in sorted(pin_paths)}
write(root/"FULL-PINS-BEFORE.json",full_before)
write(root/"SOURCE-PINS.json",{p.name:identity(p) for p in HERE.iterdir() if p.is_file()})
checks=observed("output-controls",[str(PYTHON),"-I","-S","-B",str(HERE/"check_outputs.py")],root)
text=(root/"output-controls.stderr.txt").read_text()
controls_pass=checks["exit_code"]==0 and "Ran 5 tests" in text and text.rstrip().endswith("OK")
actual_paths=[RUN/n for n in ("ROOT-SCREENING-GATE.json","screening-01","observation-01")]
absent_before={str(p):not p.exists() and p.name not in {x.name for x in RUN.iterdir()} for p in actual_paths}
assert all(absent_before.values())
startup=observed("missing-gate-startup",[str(PYTHON),"-I","-S","-B",str(HERE/"observe_screening.py")],root)
err=(root/"missing-gate-startup.stderr.txt").read_text()
absent_after={str(p):not p.exists() and p.name not in {x.name for x in RUN.iterdir()} for p in actual_paths}
startup_pass=(startup["exit_code"]==1 and "FileNotFoundError" in err and "ROOT-SCREENING-GATE.json" in err
              and "ModuleNotFoundError" not in err and all(absent_after.values()))
donor_path=Path("/home/billy/orion-director-work/20260908/ordinary-training-trace-export-v1/OBSERVER-PROCESS-CONTROLS-01.json")
donor=json.loads(donor_path.read_bytes())
donor_pass=(donor["passed"] and len(donor["cases"])==3 and all(c["passed"] for c in donor["cases"])
 and donor["observer_source"]["sha256"]=="17cd28c890cabfd3f80e32fcd60d4991e7b5142cbb53c19bfb4e5970a9281fee")
wrong_request=root/"WRONG-METHOD.json"
write(wrong_request,{"schema":"ordinary.retained-screening-request.v1","syntax_method":"uncached","gate_path":"/unissued"})
driver=observed("wrong-method-startup",[str(PYTHON),"-I","-S","-B",str(HERE.parent/"run_screening.py"),str(wrong_request),str(root/"UNISSUED-OUTPUT")],root)
driver_error=(root/"wrong-method-startup.stderr.txt").read_text()
driver_pass=(driver["exit_code"]==1 and "ValueError: screening syntax method" in driver_error and "ModuleNotFoundError" not in driver_error and not (root/"UNISSUED-OUTPUT").exists())
full_after={p:identity(Path(p)) for p in full_before}
write(root/"FULL-PINS-AFTER.json",full_after)
source_stable=full_before==full_after and all(x["sources_before"]==x["sources_after"] for x in (checks,startup,driver))
passed=controls_pass and startup_pass and driver_pass and donor_pass and source_stable
control=json.loads((root/"CONTROL-RESULT.json").read_bytes())
assert control["tests_run"]==5 and control["passed"] and control["pid"]==checks["pid"]
assert control["cwd"]=="/tmp" and control["parent_pid"]==os.getpid()
assert control["imported_modules"]["output_contract"]==str(HERE/"output_contract.py")
assert all(p in full_before for p in control["imported_modules"].values())
assert not any(n in control["imported_modules"] for n in ("syntax_memo","syntax_engine","screen","matcher"))
receipt={"schema":"ordinary.screening-observer-authored-qualification.v1","pid":os.getpid(),
 "python":{"path":str(PYTHON),**identity(PYTHON)},"passed":passed,"authored_output_controls":5,
 "output_controls_pass":controls_pass,"isolated_missing_gate_startup_pass":startup_pass,
 "sources_unchanged":source_stable,"full_pin_count":len(full_before),"wrong_method_startup_pass":driver_pass,"actual_gate_and_outputs_absent_before":absent_before,
 "actual_gate_and_outputs_absent_after":absent_after,"retained_cleanup_donor_pass":donor_pass,
 "cleanup_evidence":{"path":str(donor_path),**identity(donor_path)},
 "cleanup_scope":"Retained three donor cleanup process cases plus exact current block identity; no new cleanup process experiment.",
 "actual_control_cwd":control["cwd"],"actual_control_modules":control["imported_modules"],"processes":{"output_controls":identity(root/"output-controls.PROCESS.json"),"startup":identity(root/"missing-gate-startup.PROCESS.json"),"driver":identity(root/"wrong-method-startup.PROCESS.json")},
 "actual_native_or_export_or_screen_calls":0,"actual_retained_proposal_decodes":0,"inherited_suites_replayed":False,"source_or_template_edits":False,
 "scope":"Five affected authored output/history/import controls and exact isolated observer missing-gate and driver wrong-method refusals. Startup reads the fixed request metadata and refuses at absent gate before any real input or research import. No screening child executes."}
write(root/"QUALIFICATION.json",receipt)
print(json.dumps({"passed":passed,"output_controls":controls_pass,"startup_refusal":startup_pass,"cleanup_reuse":donor_pass}))
raise SystemExit(0 if passed else 1)

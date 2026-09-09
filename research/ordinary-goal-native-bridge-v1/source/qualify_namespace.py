"""Observe one authored qualification process; never imports target modules itself."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time
ROOT=Path(__file__).resolve().parent
PYTHON=Path("/home/billy/.local/share/uv/python/cpython-3.11.14-linux-x86_64-gnu/bin/python3.11")
def identity(p):
    b=p.read_bytes();return {"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}
def write(p,v):
    with p.open("x") as f:f.write(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+"\n")
def main():
    started=time.perf_counter()
    assert Path(sys.executable)==PYTHON and sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode
    assert not sys.flags.optimize
    output=ROOT/sys.argv[1];output.mkdir()
    paths={p.resolve() for p in ROOT.glob("*.py")}|{p.resolve() for p in (ROOT/"vendor").glob("*.py")}|{PYTHON}
    stdlib=PYTHON.parent.parent/"lib/python3.11"
    paths.update(p.resolve() for p in (ROOT/"inputs").iterdir() if p.is_file())
    paths.update(p.resolve() for p in stdlib.rglob("*") if p.is_file() and p.suffix in {".py",".so"})
    runtime=json.loads((ROOT/"inputs/RUNTIME.json").read_bytes())
    paths.update((Path(runtime["path"])/name).resolve() for name in runtime["files"])
    before={str(p):identity(p) for p in sorted(paths)}
    write(output/"PINS-BEFORE.json",before)
    snap=output/"source";snap.mkdir()
    for p in ROOT.glob("*.py"):(snap/p.name).write_bytes(p.read_bytes())
    argv=[str(PYTHON),"-I","-S","-B",str(ROOT/"check_namespace.py"),str(output/"CONTROLS.json")]
    launch=time.perf_counter()
    with (output/"stdout.txt").open("xb") as out,(output/"stderr.txt").open("xb") as err:
        child=subprocess.Popen(argv,cwd="/tmp",stdin=subprocess.DEVNULL,stdout=out,stderr=err,
                               env={"PATH":"/usr/bin:/bin","LANG":"C.UTF-8"},start_new_session=True)
        pid,status,usage=os.wait4(child.pid,0);child.returncode=os.waitstatus_to_exitcode(status)
    wall=time.perf_counter()-launch
    after={p:identity(Path(p)) for p in before};write(output/"PINS-AFTER.json",after)
    controls=json.loads((output/"CONTROLS.json").read_bytes()) if (output/"CONTROLS.json").exists() else None
    matched=(bool(controls) and controls["pid"]==child.pid and controls["parent_pid"]==os.getpid()
        and controls["cwd"]=="/tmp" and controls["python"]==str(PYTHON)
        and all(p in before for p in controls["imported_modules"].values()))
    allowed={str(p.resolve()) for p in ROOT.glob("*.py")}|{str(p.resolve()) for p in (ROOT/"vendor").glob("*.py")}
    allowed|={str((Path(runtime["path"])/n).resolve()) for n in runtime["files"]}
    imports_ok=bool(controls) and all(p in allowed or Path(p).is_relative_to(stdlib) for p in controls["imported_modules"].values())
    forbidden=bool(controls) and any(n=="torch" or n.startswith("torch.") or n in {"mmverify","trace_adapter","theorem_refactor"} for n in controls["imported_modules"])
    passed=(pid==child.pid and child.returncode==0 and matched and imports_ok and not forbidden
        and before==after and controls["passed"] and controls["tests_run"]==1 and controls["native_calls"]==0)
    receipt={"passed":passed,"pid":child.pid,"parent_pid":os.getpid(),"reaped":pid==child.pid,"exit_code":child.returncode,
      "argv":argv,"cwd":"/tmp","python":{"path":str(PYTHON),**identity(PYTHON)},
      "process_wall_s":wall,"user_cpu_s":usage.ru_utime,"system_cpu_s":usage.ru_stime,"peak_rss_kib":usage.ru_maxrss,
      "qualifier_measured_window_s":time.perf_counter()-started,"pins_unchanged":before==after,"pin_count":len(before),
      "import_identities_match":matched,"imports_within_declared_source_and_stdlib":imports_ok,"forbidden_import":forbidden,
      "control_count":controls["tests_run"] if controls else None,"actual_control_ids":controls["tests"] if controls else None,
      "stdout":identity(output/"stdout.txt"),"stderr":identity(output/"stderr.txt"),
      "control_receipt":identity(output/"CONTROLS.json") if controls else None,
      "measurement_scope":"Fresh authored child wall/CPU/RSS; qualifier window includes source pins and readback but excludes interpreter imports and final receipt serialization. Windows nested, not additive.",
      "native_or_retained_data_runs":0,"previous_suites_replayed":False}
    write(output/"PROCESS.json",receipt)
    print(json.dumps({"passed":passed,"pid":child.pid,"exit_code":child.returncode,"output":str(output)}))
    return 0 if passed else 1
if __name__=="__main__":raise SystemExit(main())

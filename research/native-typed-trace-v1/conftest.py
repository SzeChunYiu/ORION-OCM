"""Portable pure controls: native verification imports are explicitly forbidden."""
import hashlib,importlib.abc,json,os,sys,time
from pathlib import Path
START=time.monotonic();CALLS=0
HERE=Path(__file__).resolve().parent
def sources():
    return {str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(HERE.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}
BEFORE=sources()
class NativeForbidden(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        if fullname.split(".")[-1] in {"mmverify","native_checker","native_check","trace_adapter"}:
            global CALLS
            CALLS+=1
            raise AssertionError("NATIVE_EXECUTION_FORBIDDEN_IN_PURE_CONTROLS")
GUARD=NativeForbidden();sys.meta_path.insert(0,GUARD)
def pytest_sessionfinish(session,exitstatus):
    after=sources();dest=os.environ.get("TYPED_ENGINEERING_RECEIPT")
    record={"schema":"native.typed-pure-controls.v1","pid":os.getpid(),"parent_pid":os.getppid(),
            "exit":int(exitstatus),"collected":session.testscollected,"failed":session.testsfailed,
            "selected_nodeids":[item.nodeid for item in session.items],"native_guard_calls":CALLS,
            "native_execution":False,"sources_before":BEFORE,"sources_after":after,
            "sources_unchanged":BEFORE==after,"wall_s":time.monotonic()-START}
    if dest:
        with Path(dest).open("x") as f:json.dump(record,f,sort_keys=True,indent=2);f.write("\n")
    sys.meta_path.remove(GUARD)

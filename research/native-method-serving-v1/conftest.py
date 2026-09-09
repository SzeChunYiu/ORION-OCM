"""Engineering controls prohibit native verification, including portable CI."""
import hashlib,json,os,sys,time
from pathlib import Path
import pytest
from native_checker import NativeChecker
START=time.monotonic();GUARD_CALLS=0;DESELECTED=[]
HERE=Path(__file__).resolve().parent
def source_files():
    return {str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(HERE.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}
BEFORE=source_files()
def pytest_addoption(parser):
    parser.addoption("--native-bundle",help="Explicit external bundle for separately selected actual-input controls.")
def pytest_configure(config):
    config.addinivalue_line("markers","native_actual_input: requires the separately supplied fixed input bundle; excluded from portable CI")
def pytest_deselected(items):
    DESELECTED.extend(item.nodeid for item in items)
@pytest.fixture
def native_bundle(request):
    supplied=request.config.getoption("--native-bundle")
    if not supplied:
        pytest.fail("Actual-input control requires --native-bundle; portable controls use -m 'not native_actual_input'.")
    return Path(supplied).resolve()
@pytest.fixture(autouse=True)
def prohibit_native_dispatch(monkeypatch):
    def forbidden(*args,**kwargs):
        global GUARD_CALLS
        GUARD_CALLS+=1;raise AssertionError("NATIVE_DISPATCH_FORBIDDEN_IN_ENGINEERING_CONTROLS")
    monkeypatch.setattr(NativeChecker,"verify",forbidden)
def pytest_sessionfinish(session,exitstatus):
    destination=os.environ.get("NATIVE_ENGINEERING_RECEIPT")
    if destination:
        after=source_files();python=Path(sys.executable).resolve()
        result={"schema":"native.engineering-controls.v1","pid":os.getpid(),"parent_pid":os.getppid(),
                "exit":int(exitstatus),"collected":session.testscollected,"failed":session.testsfailed,
                "deselected":DESELECTED,"deselected_count":len(DESELECTED),
                "selected_nodeids":[item.nodeid for item in session.items],
                "native_guard_calls":GUARD_CALLS,"native_qualification_executed":False,
                "scope":"Actual OCM route with explicit engine/check doubles; pure compiler, payload and scheduler controls. Actual-input controls run only when selected with an explicit bundle; selected/deselected node IDs are recorded. No native outcome or measured comparison.",
                "sources_before":BEFORE,"sources_after":after,"sources_unchanged":BEFORE==after,
                "python":{"path":str(python),"sha256":hashlib.sha256(python.read_bytes()).hexdigest()},
                "wall_s":time.monotonic()-START}
        with Path(destination).open("x") as f:json.dump(result,f,sort_keys=True,indent=2);f.write("\n")

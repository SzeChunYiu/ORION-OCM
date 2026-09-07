"""Real source-only CLI refusal controls; production policy never selects toy rows."""
from pathlib import Path
import importlib._bootstrap_external as bytecode
import json,subprocess,sys
from registration_fixture import PACKAGE, boot

PYTHON=str(Path(sys.executable).resolve())


def invoke(script,inventory,bare,out,*flags):
    return subprocess.run([PYTHON,*flags,str(script),str(inventory),str(bare),str(out)],
                          stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=20)


def test_cli_requires_isolated_no_site_before_output(tmp_path):
    out=tmp_path / "out"
    p=invoke(PACKAGE / "register.py",tmp_path,tmp_path,out,"-S","-B")
    assert p.returncode!=0 and b"usage: pinned-python" in p.stderr
    assert not out.exists()


def test_cli_failure_is_retained_with_no_assignments_and_no_reuse(tmp_path):
    inv=tmp_path / "input";inv.mkdir()
    (inv / "CORPUS_SOURCE.json").write_text("authored wrong inventory")
    out=tmp_path / "out"
    p=invoke(PACKAGE / "register.py",inv,tmp_path,out,"-I","-S","-B")
    assert p.returncode!=0 and b"file binding differs" in p.stderr
    failure=json.loads((out / "FAILURE.json").read_bytes())
    assert failure["state"]=="CANNOT_REGISTER" and failure["dispatches"]==0
    assert not (out / "SEAL.json").exists() and not (out / "POPULATION.json").exists()
    prior={x.relative_to(out):x.read_bytes() for x in out.rglob("*") if x.is_file()}
    again=invoke(PACKAGE / "register.py",inv,tmp_path,out,"-I","-S","-B")
    assert again.returncode!=0 and b"FileExistsError" in again.stderr
    assert prior=={x.relative_to(out):x.read_bytes() for x in out.rglob("*") if x.is_file()}


def test_cli_ignores_harmless_matching_header_policy_cache(tmp_path):
    package=tmp_path / "research/proof-corpus-coverage-v1";package.mkdir(parents=True)
    for name in ("register.py","coverage_boot.py","coverage_population.py","coverage_git.py","coverage_policy.py","coverage_register.py","F1-CORPUS-COVERAGE-DESIGN.md","F1-CORPUS-COVERAGE-EXECUTION.md"):
        (package / name).write_bytes((PACKAGE / name).read_bytes())
    for relative,_ in boot.PARENTS.values():
        destination=package.parent / relative;destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_bytes((PACKAGE.parent / relative).read_bytes())
    source=package / "coverage_policy.py";cache=Path(bytecode.cache_from_source(str(source)));cache.parent.mkdir()
    cache.write_bytes(bytecode._code_to_timestamp_pyc(compile("raise RuntimeError('HARMLESS_POLICY_CACHE')",str(source),"exec"),int(source.stat().st_mtime),source.stat().st_size))
    check=subprocess.run([PYTHON,"-I","-S","-B","-c","import sys;sys.path.insert(0,sys.argv[1]);import coverage_policy",str(package)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    assert check.returncode!=0 and b"HARMLESS_POLICY_CACHE" in check.stderr
    inv=tmp_path / "input";inv.mkdir();(inv / "CORPUS_SOURCE.json").write_text("wrong input")
    out=tmp_path / "out";p=invoke(package / "register.py",inv,tmp_path,out,"-I","-S","-B")
    assert p.returncode!=0 and b"file binding differs" in p.stderr and b"HARMLESS_POLICY_CACHE" not in p.stderr
    assert json.loads((out / "FAILURE.json").read_bytes())["dispatches"]==0


def test_partial_unverified_seal_keeps_explicit_failure_record(tmp_path):
    script = r"""
from pathlib import Path
from types import ModuleType,SimpleNamespace
import sys
entry_path=Path(sys.argv[1]);out=Path(sys.argv[2])
entry=ModuleType('authored_registration_entry');entry.__file__=str(entry_path)
exec(compile(entry_path.read_bytes(),str(entry_path),'exec'),entry.__dict__)
real_compile=compile
class FailingRegistrar:
    def register(self, directory,bare,out,*args):
        (out/'SEAL.json').write_text('{"state":"REGISTERED_NO_DISPATCH","files":{}}\n')
        raise OSError('AUTHORED_UNVERIFIED_SEAL_WRITE')
def substituted_compile(raw,filename,*args,**kwargs):
    if filename.endswith('/coverage_boot.py'):
        return real_compile('def boot(package): return FAILING_REGISTRAR, {}',filename,'exec')
    return real_compile(raw,filename,*args,**kwargs)
class Module(ModuleType):
    def __init__(self,name):super().__init__(name);self.FAILING_REGISTRAR=FailingRegistrar()
entry.compile=substituted_compile;entry.ModuleType=Module
sys.argv=[str(entry_path),str(out.parent),str(out.parent),str(out)]
entry.main()
"""
    out=tmp_path / 'partial'
    result=subprocess.run([PYTHON,'-I','-S','-B','-c',script,str(PACKAGE/'register.py'),str(out)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=20)
    assert result.returncode!=0 and b'AUTHORED_UNVERIFIED_SEAL_WRITE' in result.stderr
    assert (out/'SEAL.json').is_file()
    failure=json.loads((out/'FAILURE.json').read_bytes())
    assert failure['state']=='CANNOT_REGISTER' and failure['dispatches']==0

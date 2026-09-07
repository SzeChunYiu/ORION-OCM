"""Fixed conventional closure and unchanged generic ledger source loading."""
import hashlib,sys,types
from pathlib import Path
import unary_method_plain as D
from unary_contract import InputRefused

ROOT=Path(__file__).resolve().parents[2]
PACKAGE="_unary_conventional_ledger"
LOADED={}
def _load_ledger():
    folder=ROOT/"src/ocm/store"
    package=types.ModuleType(PACKAGE);package.__path__=[];sys.modules[PACKAGE]=package
    for name in ("canonical","ledger"):
        path=folder/(name+".py");raw=path.read_bytes()
        mod=types.ModuleType(PACKAGE+"."+name)
        mod.__file__=str(path);mod.__package__=PACKAGE
        mod.__source_sha256__=hashlib.sha256(raw).hexdigest()
        sys.modules[mod.__name__]=mod
        try:exec(compile(raw,str(path),"exec"),mod.__dict__)
        except BaseException:
            sys.modules.pop(mod.__name__,None);raise
        LOADED[str(path.relative_to(ROOT))]=mod.__source_sha256__
    return sys.modules[PACKAGE+".ledger"].LedgerStore

LedgerStore=_load_ledger()

def sources(work=None):
    root,paths=D.shared_paths();here=Path(__file__).resolve().parent
    paths+=list(here.glob("unary_parent_*.py"))
    paths+=[here/(n+".py") for n in ("unary_method_arm","unary_method_episode",
            "unary_method_process","unary_method_profile","unary_method_outer")]
    paths+=[root/"src/ocm/store"/n for n in ("canonical.py","ledger.py")]
    result=D.inventory(paths,root,work)
    if any(result.get(k)!=v for k,v in LOADED.items()):raise InputRefused("PARENT_LOADED_LEDGER_SOURCE")
    return result

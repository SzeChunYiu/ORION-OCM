"""Bounded-file IO; no native invocation or corpus path discovery."""
import hashlib,json,sys,types
from pathlib import Path

def identity(raw):return {"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
def canonical(value):return (json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n").encode()

def loads(raw):
    def unique(pairs):
        obj={}
        for key,value in pairs:
            if key in obj:raise ValueError("duplicate JSON key: "+key)
            obj[key]=value
        return obj
    return json.loads(raw,object_pairs_hook=unique,parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))

def read_bound(binding):
    raw=Path(binding["path"]).read_bytes()
    if identity(raw)!={k:binding[k] for k in ("bytes","sha256")}:raise ValueError("input drift: "+binding["path"])
    return raw

def write(path,value):
    raw=canonical(value)
    with path.open("xb") as stream:stream.write(raw)
    return {"path":str(path.resolve()),**identity(raw)}

def load(path,pin,name):
    raw=path.read_bytes()
    if identity(raw)!=pin:raise ValueError("source drift: "+str(path))
    module=types.ModuleType(name);module.__file__=str(path.resolve())
    sys.modules[name]=module
    exec(compile(raw,str(path),"exec"),module.__dict__)
    return module

def snapshot(root,names):return {name:identity((root/name).read_bytes()) for name in names}

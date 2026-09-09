"""Local-only vendor loader and predecessor-compatible canonical identities."""
import hashlib, importlib.util, json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def canonical(obj):return (json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n").encode()
def raw_id(raw):return {"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
def load(name):
    path=HERE/(name+".py")
    if path.parent!=HERE or not path.is_file():raise ValueError("LOCAL_VENDOR_MODULE")
    spec=importlib.util.spec_from_file_location("_native_"+name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

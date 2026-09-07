"""A strict launcher-only interpreter identity; not a host qualification."""
import hashlib,re,sys
from pathlib import Path
from unary_contract import InputRefused,fields
import unary_method_data as D

VERSION="3.11.14"
DEFAULT={"schema":"ocm.unary-method.python.v1","version":VERSION,
 "executable":"/home/billy/.local/share/uv/python/cpython-3.11.14-linux-x86_64-gnu/bin/python3.11",
 "sha256":"edca1fc80dbd58182c849c13707fb6bfb522b0d7049adc408225f7c69b124d3b"}

def validate(value):
    value=D.parse(D.raw(value));fields(value,("schema","version","executable","sha256"))
    if value["schema"]!="ocm.unary-method.python.v1" or value["version"]!=VERSION:
        raise InputRefused("PYTHON_PROFILE_VERSION")
    if type(value["executable"]) is not str or not Path(value["executable"]).is_absolute():
        raise InputRefused("PYTHON_PROFILE_PATH")
    if type(value["sha256"]) is not str or re.fullmatch("[0-9a-f]{64}",value["sha256"]) is None:
        raise InputRefused("PYTHON_PROFILE_HASH")
    try:resolved=Path(value["executable"]).resolve(strict=True)
    except OSError as exc:raise InputRefused("PYTHON_PROFILE_UNAVAILABLE") from exc
    if str(resolved)!=value["executable"]:raise InputRefused("PYTHON_PROFILE_RESOLVED_PATH")
    return value

def verify(value,*,actual=False):
    value=validate(value);path=Path(value["executable"])
    try:data=path.read_bytes()
    except OSError as exc:raise InputRefused("PYTHON_PROFILE_UNAVAILABLE") from exc
    digest=hashlib.sha256(data).hexdigest()
    if digest!=value["sha256"]:raise InputRefused("PYTHON_HASH")
    if actual:
        if str(Path(sys.executable).resolve())!=value["executable"]:raise InputRefused("PYTHON_ACTUAL_PATH")
        if tuple(sys.version_info[:3])!=(3,11,14):raise InputRefused("PYTHON_ACTUAL_VERSION")
        if not (sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode):
            raise InputRefused("PYTHON_ACTUAL_FLAGS")
    return {"path":str(path),"sha256":digest,"bytes":len(data)}

def observe():
    if tuple(sys.version_info[:3])!=(3,11,14):raise InputRefused("PYTHON_OBSERVATION_VERSION")
    path=Path(sys.executable).resolve()
    return {"schema":"ocm.unary-method.python.v1","version":VERSION,
            "executable":str(path),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()}

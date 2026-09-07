"""Strict plain data and the shared mechanical computation source closure."""
import hashlib,json,math
from pathlib import Path
from unary_contract import InputRefused

MAX_BYTES=1<<20

def bump(work,key,n=1):work[key]=work.get(key,0)+n

def raw(value):
    nodes=0
    def check(x,depth=0):
        nonlocal nodes
        nodes+=1
        if nodes>100000 or depth>40:raise InputRefused("METHOD_DATA_BOUND")
        if type(x) is dict:
            if any(type(k) is not str for k in x):raise InputRefused("METHOD_DATA_KEY")
            for v in x.values():check(v,depth+1)
        elif type(x) is list:
            for v in x:check(v,depth+1)
        elif type(x) is float:
            if not math.isfinite(x):raise InputRefused("METHOD_DATA_FLOAT")
        elif type(x) not in (str,int,bool,type(None)):raise InputRefused("METHOD_NOT_DATA")
    check(value)
    result=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()
    if len(result)>MAX_BYTES:raise InputRefused("METHOD_DATA_BOUND")
    return result

def hashed(value):return hashlib.sha256(raw(value)).hexdigest()

def parse(data):
    if type(data) is not bytes or len(data)>MAX_BYTES:raise InputRefused("METHOD_DATA_BYTES")
    def pairs(items):
        result={}
        for key,value in items:
            if key in result:raise InputRefused("METHOD_DUPLICATE_KEY")
            result[key]=value
        return result
    try:value=json.loads(data,object_pairs_hook=pairs)
    except (UnicodeError,ValueError,RecursionError) as exc:raise InputRefused("METHOD_JSON") from exc
    if raw(value)!=data:raise InputRefused("METHOD_NONCANONICAL")
    return value

def shared_paths():
    here=Path(__file__).resolve().parent;root=here.parents[1]
    names=("unary_method_plain","unary_method_execution","unary_method_postings","unary_method_verify_use",
           "unary_method_selection","unary_method_selection_check","unary_method_selection_support")
    paths=[here/(n+".py") for n in names]
    paths+=list(here.glob("unary_rule_*.py"))
    paths+=[root/"research/math-language-v1"/n for n in
            ("unary_contract.py","unary_language.py","unary_solver.py","unary_verify.py")]
    policy=root/"docs/plans/unary-adaptive-parent-v2-1"
    paths+=[policy/(n+".md") for n in ("CORE","GENERATOR","SELECTION","EXECUTION","PARENT-POLICY","FAILURES")]
    return root,paths

def inventory(paths,root,work=None):
    work={} if work is None else work;out={}
    for p in sorted(set(paths)):
        b=p.read_bytes();bump(work,"source_files_hashed");bump(work,"source_bytes_hashed",len(b))
        out[str(p.relative_to(root))]=hashlib.sha256(b).hexdigest()
    return out

def sources(work=None):
    root,paths=shared_paths()
    return inventory(paths,root,work)

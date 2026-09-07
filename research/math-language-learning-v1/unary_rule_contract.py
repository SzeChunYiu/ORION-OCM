"""Plain universal-schema data, content identity, and explicit key traversal."""
import hashlib
import json
from unary_contract import InputRefused, SCHEMA, fields, validate_task

RULE_SCHEMA="ocm.unary-rule.v1"
RECIPE="universal-cover.v1"
BODY=("schema","parameters","premises","conclusion","recipe")

def count(work,name,n=1):
    work[name]=work.get(name,0)+n

def encoded(value,work):
    """Inputs already validated as plain data. Count serialization-key traversal."""
    def walk(x):
        count(work,"key_nodes")
        if type(x) is dict:
            for k,v in x.items():walk(k);walk(v)
        elif type(x) is list:
            for v in x:walk(v)
    walk(value)
    raw=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()
    count(work,"key_bytes",len(raw))
    return raw

def digest(value,work):
    raw=encoded(value,work);count(work,"bytes_hashed",len(raw))
    return hashlib.sha256(raw).hexdigest()

def _body(value):
    fields(value,BODY)
    for k,want in (("schema",RULE_SCHEMA),("recipe",RECIPE)):
        if type(value[k]) is not str or value[k]!=want:raise InputRefused("RULE_VERSION")
    task=validate_task({"schema":SCHEMA,"predicates":value["parameters"],
                        "premises":value["premises"],"query":value["conclusion"]})
    names=task["predicates"]
    if len(names)>3 or names!=["P"+str(i) for i in range(len(names))]:
        raise InputRefused("RULE_PARAMETERS")
    if not 2<=len(task["premises"])<=3:raise InputRefused("RULE_PREMISE_BOUND")
    if any(s["kind"] not in ("every","no") for s in [*task["premises"],task["query"]]):
        raise InputRefused("RULE_UNIVERSAL_ONLY")
    return {"schema":RULE_SCHEMA,"parameters":names,"premises":task["premises"],
            "conclusion":task["query"],"recipe":RECIPE}

def seal_rule(parameters,premises,conclusion,work=None):
    """Seal supplied structure; neither discovery nor a logical acceptance decision."""
    work={} if work is None else work
    body=_body({"schema":RULE_SCHEMA,"parameters":parameters,"premises":premises,
                "conclusion":conclusion,"recipe":RECIPE})
    return dict(body,rule_id=digest(body,work))

def validate_rule(value,work=None):
    work={} if work is None else work
    fields(value,(*BODY,"rule_id"))
    if type(value["rule_id"]) is not str:raise InputRefused("RULE_ID_TYPE")
    body=_body({k:value[k] for k in BODY})
    expected=digest(body,work)
    if value["rule_id"]!=expected:raise InputRefused("RULE_CONTENT_ID")
    return dict(body,rule_id=expected)

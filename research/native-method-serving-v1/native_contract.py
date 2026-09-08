"""Finite authored serving boundary; unsupported contexts refuse explicitly."""
from vendor import common as C
T=C.load("typed_terms")
CONTEXT={"classes":["A","B","C"],"type":"|-","ambient_dv":[],"hypothesis_type":"|-"}
class InputRefused(ValueError):pass
def fields(value,names):
    if type(value) is not dict or set(value)!=set(names):raise InputRefused("SCHEMA_FIELDS")
def require(ok,reason):
    if not ok:raise InputRefused(reason)
def task(value):
    fields(value,("premises","query"))
    require(type(value["premises"]) is list and len(value["premises"])<=8,"PREMISE_BOUND")
    for statement in value["premises"]+[value["query"]]:
        require(type(statement) is list and 2<=len(statement)<=128 and all(type(t) is str for t in statement),"STATEMENT_DATA")
        require(statement[0]=="|-","UNSUPPORTED_TYPE")
        try:T.syntax("wff",statement[1:])
        except ValueError as exc:raise InputRefused("UNSUPPORTED_STATEMENT") from exc
    return value

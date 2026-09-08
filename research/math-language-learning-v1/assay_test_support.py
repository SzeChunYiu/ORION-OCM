"""Manually authored inputs; no registered stream invocation."""
import importlib,importlib.util,json,os
from unary_test_support import task,statement as s,pred

def api(name):
    assert importlib.util.find_spec(name),"missing pure generator helper "+name
    return importlib.import_module(name)

def chain():
    return task([s("every","P0","P1"),s("every","P1","P2")],s("every","P0","P2"))

def other():
    return task([s("some","P0","P1"),s("every","P1","P2")],s("no","P0","P2"))

def grouped():
    return task([s("every",["and",pred("P0"),pred("P1")],"P2"),
                 s("some","P0","P0"),s("no","P1","P1"),s("every","P2","P2")],
                s("some","P2","P2"))

def draw(value,split,d,slot):
    return {"split":split,"attempt":d,"slot":slot,"fields":[{"authored_fixture":True}],
            "task":value,"task_bytes":json.dumps(value,sort_keys=True,separators=(",",":"))}

class Sink:
    def __init__(self,path):self.path=path;self.rows=[]
    def __call__(self,row):
        raw=json.dumps(row,sort_keys=True,separators=(",",":"))+"\n"
        with self.path.open("ab") as f:f.write(raw.encode());f.flush();os.fsync(f.fileno())
        self.rows.append(json.loads(raw))


import pytest
from unary_contract import InputRefused

@pytest.fixture(autouse=True)
def authored_only(monkeypatch):
    """Fail before hashing if an engineering test reaches the registered stream."""
    stream=api("unary_assay_stream");original=stream.choice
    def prohibited(*a,**k):raise InputRefused("REGISTERED_STREAM_FORBIDDEN_IN_ENGINEERING")
    def choice(master,*a,**k):
        if master==stream.MASTER:prohibited()
        return original(master,*a,**k)
    monkeypatch.setattr(stream,"draw",prohibited)
    monkeypatch.setattr(stream,"choice",choice)

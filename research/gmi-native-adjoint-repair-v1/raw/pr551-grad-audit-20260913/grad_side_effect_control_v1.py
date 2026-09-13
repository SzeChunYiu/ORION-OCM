"""One fixed source-bound VM input/feedback control; no ecology or search."""
from pathlib import Path
import json, sys, hashlib
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "raw"))
from gmi_microscope import core, bases, morph, vm
g = morph.make({"input": ("INPUT", {"width": 1}), "dense": ("DENSE", {"width": 1}),
    "linear": ("LINEAR", {}), "output": ("OUTPUT", {}), "target": ("TARGET", {}),
    "grad": ("GRAD", {"lr": 1})},
    [("dense","linear",0),("input","linear",1),("linear","output",0),
     ("dense","grad",0),("linear","grad",1),("target","grad",2)])
M = core.Machine(bases.B0, seed=0)
machine = vm.VM(g, M, seed=0)
stages = []
def snapshot(label):
    stages.append({"stage":label,"cells":dict(M.cells),"stores":dict(M.stores),
        "ledger":dict(M.L.c),"native_ops":M.L.native_ops,"emulated_ops":M.L.emulated_ops,
        "ops_by_kind":dict(M.L.ops_by_kind),"writes_in_event":sorted(M.L.writes_in_event),
        "event_write_fracs":list(M.L.event_write_fracs)})
machine.init(); snapshot("initialization")
M.phase("exec"); before = machine.query(1); snapshot("query_before")
M.phase("upd"); machine.feedback(1, 0); snapshot("feedback_before_end_event")
M.end_event(); snapshot("feedback_after_end_event")
M.phase("exec"); after = machine.query(1); snapshot("query_after")
observed = {"before":before,"after":after}
result = {"schema":"PR551_GRAD_SIDE_EFFECT_NATIVE_CONTROL_V1",
    "source_commit":"7328d5b3b0a5111fd43c3e277679faf0edeee1bb",
    "protocol_sha256":hashlib.sha256((HERE/"CONTROL_PROTOCOL_V1.md").read_bytes()).hexdigest(),
    "source_bindings_sha256":hashlib.sha256((HERE/"SOURCE_BINDINGS_V1.json").read_bytes()).hexdigest(),
    "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "python":sys.version,"python_executable":str(Path(sys.executable).resolve()),
    "binary_sha256":hashlib.sha256(Path(sys.executable).resolve().read_bytes()).hexdigest(),
    "input":1,"feedback_target_fx":0,"learning_rate_fx":1,"seed":0,
    "basis":M.basis.spec(),"genotype":g,"evaluation_order":machine.order,
    "grad_outgoing_edges":[e for e in g["edges"] if e[0]=="grad"],
    "observed":observed,"stages":stages,
    "scope":"one fixed-point state/response control; no capability, search, ecology or physical cost inference"}
print(json.dumps(result,indent=2,sort_keys=True))
if observed != {"before":8,"after":7}: raise SystemExit("declared arithmetic control did not match")

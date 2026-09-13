"""One zero-input native adjoint control, with a passive tape observer."""
from pathlib import Path
import hashlib, json, sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/"raw"))
from gmi_microscope import core,bases,morph,vm
previous=json.loads((HERE/"GRAD_SIDE_EFFECT_CONTROL_V1.json").read_text())
g=previous["genotype"]
M=core.Machine(bases.B0,seed=0); machine=vm.VM(g,M,seed=0)
stages=[]; observations=[]
def state(label):
    stages.append({"stage":label,"cells":dict(M.cells),"stores":dict(M.stores),
        "ledger":dict(M.L.c),"native_ops":M.L.native_ops,"emulated_ops":M.L.emulated_ops,
        "ops_by_kind":dict(M.L.ops_by_kind),"writes_in_event":sorted(M.L.writes_in_event),
        "event_write_fracs":list(M.L.event_write_fracs)})
def tape(root):
    nodes=[];seen={}
    def visit(v):
        if id(v) in seen: return seen[id(v)]
        index=len(nodes);seen[id(v)]=index;nodes.append(None)
        parents=[]
        for par in v.parents:
            if par[0]=="param": parents.append({"parameter":par[1]})
            else: parents.append({"node":visit(par[0]),"local_derivative_fx":par[1]})
        nodes[index]={"node":index,"value_fx":v.v,"adjoint_fx":v.grad,"parents":parents}
        return index
    return {"root":visit(root),"nodes":nodes}
original=machine._backprop
def observe(out,err):
    record={"error_fx":err,"before":tape(out),"machine_tape":list(M.tape or [])}
    result=original(out,err)
    record.update({"after":tape(out),"parameter_adjoints_fx":dict(result)})
    observations.append(record)
    return result
machine._backprop=observe
machine.init();state("initialization")
M.phase("exec");before=machine.query(0);state("query_before")
M.phase("upd");machine.feedback(0,16);state("feedback_before_end_event")
M.end_event();state("feedback_after_end_event")
M.phase("exec");after=machine.query(0);state("query_after")
result={"schema":"PR551_ZERO_INPUT_ADJOINT_CONTROL_V1",
    "source_commit":previous["source_commit"],"genotype":g,"basis":M.basis.spec(),
    "input":0,"target_fx":16,"learning_rate_fx":1,"seed":0,
    "exact_zero_multiplier_sensitivity":0,"expected_parameter_adjoint_fx":0,
    "observed_outputs":{"before":before,"after":after},"tape_observations":observations,
    "stages":stages,"python":sys.version,"binary":str(Path(sys.executable).resolve()),
    "binary_sha256":hashlib.sha256(Path(sys.executable).resolve().read_bytes()).hexdigest(),
    "source_bindings_sha256":hashlib.sha256((HERE/"SOURCE_BINDINGS_V1.json").read_bytes()).hexdigest(),
    "protocol_sha256":hashlib.sha256((HERE/"ZERO_INPUT_ADJOINT_PROTOCOL_V1.md").read_bytes()).hexdigest(),
    "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "positive_control_sha256":hashlib.sha256((HERE/"GRAD_SIDE_EFFECT_CONTROL_V1.json").read_bytes()).hexdigest(),
    "scope":"one authored VM adjoint counterexample; no ecology, search, capability or physical-cost claim"}
print(json.dumps(result,indent=2,sort_keys=True))

"""Pure serving controls. No native replay, protected target search or timing study."""
from types import SimpleNamespace
import copy,pytest
from native_engine import NativeEngine,F,K
from native_packet import validate_packet
from native_inputs import Inputs
from native_macros import compile_macros
from native_contract import InputRefused,require
from vendor import common as C
import native_data as D

@pytest.mark.native_actual_input
def test_sealed_projection_and_in_memory_tamper(native_bundle):
    inp=Inputs(native_bundle,{})
    assert set(inp.methods)==set().union(*(set(v) for v in inp.binding["eligible"].values()))
    mid=next(iter(inp.methods));inp.methods[mid]["saved_accepted"]=True
    with pytest.raises(InputRefused,match="MUTATED_INPUT_OBJECT"):inp.check()

@pytest.mark.native_actual_input
def test_projection_disk_tamper_is_refused(tmp_path,native_bundle):
    import shutil
    shutil.copytree(native_bundle,tmp_path/"bundle")
    f=tmp_path/"bundle/METHODS.json";f.write_bytes(f.read_bytes()+b" ")
    with pytest.raises(InputRefused,match="INPUT_BYTES_CHANGED"):Inputs(tmp_path/"bundle",{})

@pytest.mark.native_actual_input
def test_constructor_recipe_all_six_bindings_and_wrong_hole_refusal(native_bundle):
    inp=Inputs(native_bundle,{});mid=inp.binding["eligible"]["learn"][0];work={}
    actions=compile_macros(inp.methods,[mid],[],inp.bank,K,work)
    assert len(actions)==6 and {a["method_id"] for a in actions}=={mid}
    item=inp.methods[mid];body=item["body"];holes=[{"label":"local-"+str(i),"statement":s} for i,s in enumerate(body["premises"])]
    holes[0]["statement"]=body["query"]
    with pytest.raises(ValueError,match="external statement"):
        K.construct(item["trace"],item["contracts"],{"A":"A","B":"B","C":"C"},holes,4096)

class TinyEngine(NativeEngine):
    def __init__(self):
        self.work={};self.source_map=D.sources(self.work);self.source_sha=D.hashed(self.source_map);self.qualification={}
        parent=[{"label":"ssid","kind":"$p","statement":["|-","A","C_","A"],"dv":[],
                 "floating":[{"label":"cA","statement":["class","A"]}],"essential":[]}]
        bank={"class":[{"tokens":[a],"proof":["c"+a]} for a in ("A","B","C")],
              "wff":[{"tokens":[a,"C_",a],"proof":["c"+a,"c"+a,"wss"]} for a in ("A","B","C")]}
        self.inputs=SimpleNamespace(parent=parent,bank=bank,methods={},identity={"TEST_ONLY":"tiny ordinary bank"})
    def check_environment(self):require(D.sources(self.work)==self.source_map,"SOURCE_CHANGED")

@pytest.mark.parametrize("scheduler",["layered","indexed"])
def test_shared_engine_tiny_ordinary_compiler_emit_and_packet_check(scheduler):
    engine=TinyEngine();request=engine.request({"premises":[],"query":["|-","A","C_","A"]},scheduler=scheduler)
    packet=engine.propose(request);validate_packet(engine,request,packet,{})
    assert packet["normal_proof"]==["cA","ssid"] and packet["decision_count"]==1
    assert packet["execution"]["ordinary_instances"]==3 and packet["selected_proof_method_ids"]==[]
    bad=copy.deepcopy(packet);bad["derivation"]["output"]=["|-","B","C_","B"]
    with pytest.raises(InputRefused):validate_packet(engine,request,bad,{})

@pytest.mark.parametrize("field,value",[("ambient_dv",[["A","B"]]),("type","wff"),("classes",["A","B","C","D"])])
def test_unsupported_native_context_refuses(field,value):
    engine=TinyEngine();request=engine.request({"premises":[],"query":["|-","A","C_","A"]})
    request["context"][field]=value
    with pytest.raises(InputRefused,match="REQUEST_BINDING"):engine.validate_request(request)

def test_wrong_target_and_hole_are_not_saved_accepted_flags():
    engine=TinyEngine();request=engine.request({"premises":[["|-","A","C_","A"]],"query":["|-","A","C_","A"]})
    packet=engine.propose(request);validate_packet(engine,request,packet,{})
    for change in ("target","hole","proof"):
        bad=copy.deepcopy(packet)
        if change=="target":bad["derivation"]["output"]=["|-","B","C_","B"]
        elif change=="hole":bad["derivation"]["slot"]=1
        else:bad["normal_proof"]=["search-hyp-1"]
        with pytest.raises(InputRefused):validate_packet(engine,request,bad,{})

"""Shared conventional computation; OCM does not substitute its warrant checker."""
import time,uuid
from vendor import common as C
from native_contract import fields,require,task as validate_task,CONTEXT
from native_inputs import Inputs
from native_macros import compile_macros
from native_checker import NativeChecker
import native_data as D
F=C.load("finite_search");A=C.load("indexed_agenda");K=C.load("native_constructor")
class NativeEngine:
    def __init__(self,bundle,archive):
        start=time.monotonic();self.work={};self.source_map=D.sources(self.work);self.source_sha=D.hashed(self.source_map)
        self.inputs=Inputs(bundle,self.work);self.checker=NativeChecker(bundle,archive,self.work)
        self.qualification={};self.check_environment()
        # Acceptance is freshly computed here, never restored from old flags.
        for mid,item in sorted(self.inputs.methods.items()):
            body=item["body"];holes=["search-hyp-"+str(i) for i in range(len(body["premises"]))]
            native=K.construct(item["trace"],item["contracts"],dict(zip(("A","B","C"),("A","B","C"))),
                               [{"label":h,"statement":s} for h,s in zip(holes,body["premises"])],4096)
            recipe=C.load("native_recipe").emit(body,item["contracts"],holes,self.work)
            require(native["proof"]==recipe["proof"] and native["target"]==body["query"],"QUALIFICATION_CONSTRUCTOR")
            claims=[{"task":{"premises":body["premises"],"query":body["query"]},"proof":native["proof"],"holes":holes}]
            checked=self.checker.verify(claims);require(checked["terminal"]=="NATIVE_VERIFIED","METHOD_REPLAY_REFUSED")
            self.qualification[mid]={"method_payload_sha256":D.hashed(item),"claims_sha256":D.hashed(claims),
                                     "database":checked["database"],"trace_sha256":checked["trace_sha256"],
                                     "sources_sha256":self.source_sha,"library":self.inputs.identity}
        self.check_environment();D.bump(self.work,"cold_init_wall_s",time.monotonic()-start)
    def check_environment(self):
        require(D.sources(self.work)==self.source_map,"SOURCE_CHANGED")
        self.inputs.check()
    def request(self,task,eligible_ids=(),*,scheduler="layered",invoke=True,request_id=None):
        self.check_environment();task=validate_task(D.parse(D.raw(task)))
        require(scheduler in ("layered","indexed") and type(invoke) is bool,"EXECUTION_POLICY")
        ids=list(eligible_ids);require(ids==sorted(set(ids)) and set(ids)<=set(self.qualification),"ELIGIBLE_IDS")
        request_id=str(uuid.uuid4()) if request_id is None else request_id
        require(type(request_id) is str and 0<len(request_id)<=128,"REQUEST_ID")
        return D.parse(D.raw({"schema":"native.request.v1","request_id":request_id,"task":task,"context":CONTEXT,
                "library":self.inputs.identity,"sources_sha256":self.source_sha,"scheduler":scheduler,
                "invoke":invoke,"eligible_ids":ids,"max_decisions":8,"instance_bound":200000}))
    def validate_request(self,request):
        fields(request,("schema","request_id","task","context","library","sources_sha256","scheduler","invoke","eligible_ids","max_decisions","instance_bound"))
        expected=self.request(request["task"],request["eligible_ids"],scheduler=request["scheduler"],invoke=request["invoke"],request_id=request["request_id"])
        require(D.raw(request)==D.raw(expected),"REQUEST_BINDING")
    def propose(self,request):
        start=time.monotonic();self.validate_request(request);work={};timings={};inp=self.inputs
        t=time.monotonic();ordinary=F.compile_parent(inp.parent,inp.bank,work,limit=200000)
        timings["cold_parent_compile_s"]=time.monotonic()-t
        ids=request["eligible_ids"] if request["invoke"] else []
        t=time.monotonic();macros=compile_macros(inp.methods,ids,[],inp.bank,K,work)
        timings["macro_compile_s"]=time.monotonic()-t
        t=time.monotonic();search=(F.search if request["scheduler"]=="layered" else A.search)(ordinary+macros,inp.bank,request["task"],work,8)
        timings["search_s"]=time.monotonic()-t;proof=[];used=[];derivation=None
        if search["terminal"]=="PROVED":
            derivation=search["derivation"];used=selected_methods(derivation)
            t=time.monotonic();proof=F.emit(derivation,inp.parent,inp.bank,work);timings["emission_s"]=time.monotonic()-t
        normal=" ".join(proof)+("\n" if proof else "")
        packet={"schema":"native.packet.v1","request_sha256":D.hashed(request),"context":request["context"],
                "library":request["library"],"terminal":search["terminal"],"decision_count":search.get("decision_count"),
                "eligible_ids":request["eligible_ids"],"selected_proof_method_ids":used,"normal_proof":proof,
                "normal_proof_bytes":normal,"normal_proof_sha256":C.raw_id(normal.encode("ascii"))["sha256"],
                "derivation":derivation,"execution":{"work":work,"timings":timings,
                "ordinary_instances":len(ordinary),"ordinary_sha256":C.raw_id(C.canonical(ordinary))["sha256"],
                "macro_instances":len(macros),"search_terminal":search["terminal"],"wall_s":time.monotonic()-start}}
        self.check_environment();return D.parse(D.raw(packet))
    def check(self,request,packet):
        from native_packet import validate_packet
        start=time.monotonic();self.validate_request(request);work={}
        validate_packet(self,request,packet,work)
        claims=[{"task":request["task"],"proof":packet["normal_proof"],
                 "holes":["search-hyp-"+str(i) for i in range(len(request["task"]["premises"]))]}]
        checked=self.checker.verify(claims)
        require(checked["terminal"]=="NATIVE_VERIFIED","OUTPUT_NATIVE_REJECTED")
        self.check_environment();D.bump(work,"check_wall_s",time.monotonic()-start)
        return {"status":"PASS","packet_sha256":D.hashed(packet),"request_sha256":D.hashed(request),"native":checked,"work":work}
    def direct(self,request):
        start=time.monotonic();packet=self.propose(request)
        if packet["terminal"]!="PROVED":return {"terminal":"CANNOT_CHECK","packet":None,"proposal":packet,"check":None,"wall_s":time.monotonic()-start}
        checked=self.check(request,packet)
        return {"terminal":"CHECKED","packet":packet,"check":checked,"wall_s":time.monotonic()-start}
def selected_methods(node):
    used=set()
    def visit(n):
        if n["kind"]=="action":
            if n["action"]["kind"]=="macro":used.add(n["action"]["method_id"])
            for child in n["parents"]:visit(child)
    visit(node);return sorted(used)

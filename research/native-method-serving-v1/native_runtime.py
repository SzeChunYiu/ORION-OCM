"""Registered PROGRAMMATIC backend, genuine OCM solve, exact native check and use."""
import time
from ocm.operators.registry import OperatorSpec,BackendKind
from ocm.runtime import solve as SV
from native_contract import InputRefused,require
from native_request import request,read_request,check_packet
from native_journal import begin_use,record_use
import native_data as D
class NativeRuntime:
    def __init__(self,store):
        self.store=store;self.rt=store.rt;self.active=None;self.dispatches=0;self.checks=0
        self.op=OperatorSpec("native:generic-dispatcher",store.source_sha,BackendKind.PROGRAMMATIC,self._backend,(),
                            output_type="proof",warrant=store.warrant(),scope=D.SCOPE,checker=self._check)
        self.registry_key=self.rt.register_operator(self.op)
    def current_operator(self):
        require(self.rt.state.operators.operators.get(self.registry_key) is self.op,"REGISTERED_DISPATCHER_CHANGED")
    def _backend(self,ks,inputs):
        self.dispatches+=1;a=self.active
        try:
            require(a is not None and inputs=={"qid":a["qid"]},"DISPATCH_INPUT");self.current_operator()
            data=read_request(self.store,a["qid"],a["request"])
            packet=self.store.engine.propose(data["engine_request"]);self.current_operator()
            a["execution"]=packet["execution"];a["issued"]=D.raw(packet)
            return D.parse(a["issued"])
        except Exception as exc:
            if a is not None:a["backend_failure"]=str(exc)
            return {"terminal":"CANNOT_CHECK","reason":str(exc)}
    def _check(self,packet):
        self.checks+=1;a=self.active
        try:
            self.current_operator();require(a is not None and a["issued"] is not None and D.raw(packet)==a["issued"],"UNISSUED_PACKET")
            checked=check_packet(self.store,a["qid"],a["request"],packet);self.current_operator()
            # Re-evaluate combined current warrants after the external checker.
            read_request(self.store,a["qid"],a["request"])
            self.store.require_selected_live(packet["selected_proof_method_ids"],a["request"]["evidence"])
            a["check"]=checked;return SV.Status.PASS
        except Exception as exc:
            if a is not None:a["check"]={"status":"CANNOT_CHECK","reason":str(exc)}
            return SV.Status.CANNOT_CHECK
    def solve(self,task,requested_ids=(),*,scheduler="layered",invoke=True,request_id=None):
        start=time.monotonic();self.current_operator();self.store.check_environment()
        require(not self.store.pending,"INCOMPLETE_USE");require(self.active is None,"ACTIVE_REQUEST")
        if D.live(self.rt,self.store.warrant())!="LIVE":return {"terminal":"CANNOT_CHECK","reason":"ENVIRONMENT_UNAVAILABLE","dispatches":0}
        qid,data=request(self.store,task,list(requested_ids),scheduler=scheduler,invoke=invoke,request_id=request_id)
        intent=begin_use(self.store,qid,data)
        self.active={"qid":qid,"request":data,"issued":None,"check":None,"backend_failure":None,"execution":None}
        db=self.dispatches;cb=self.checks
        try:
            wrapper=SV.OperatorSpec(self.op.operator_id,self.op.version,
            lambda ks,name,ctx:self.op.backend(ks,{"qid":qid}),(qid,),output_type="proof",
            warrant=self.store.warrant([data["evidence"]]),scope=D.SCOPE,checker=lambda packet:self.op.checker(packet))
            out=self.rt.solve(SV.Task(qid,(SV.QueryPart(qid,"query_seed",(qid,)),),context=D.CONTEXT),(wrapper,))
            receipt={"terminal":"CHECKED" if SV.committed(out) else "CANNOT_CHECK","qid":qid,"trace":out.trace.as_dict(),
                     "check":self.active["check"],"packet":out.answer,"backend_failure":self.active["backend_failure"],
                     "execution_observation":self.active["execution"],"dispatches":self.dispatches-db,"checks":self.checks-cb,
                     "solve_wall_s":time.monotonic()-start}
            t=time.monotonic();record_use(self.store,qid,data,receipt,intent)
            receipt["return_observation"]={"journal_wall_s":time.monotonic()-t,"total_wall_s":time.monotonic()-start}
            return receipt
        finally:self.active=None

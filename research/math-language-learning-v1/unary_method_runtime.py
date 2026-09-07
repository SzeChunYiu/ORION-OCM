"""One registered dispatcher; request-specific SV wrapping and independent checking."""
import time
from ocm.operators.registry import OperatorSpec,BackendKind
from ocm.runtime import solve as SV
from unary_contract import InputRefused,negate
from unary_solver import RegionSolver
from unary_rule_apply import apply_rule
from unary_method_index import MethodIndex
from unary_method_check import request,read_request,answer_warrant,check_packet
import unary_method_data as D

class MethodRuntime:
    def __init__(self,store):
        self.store=store;self.rt=store.rt;self.dispatches=0;self.checks=0;self.active=None
        self.op=OperatorSpec("unary:generic-dispatcher",store.source_sha,BackendKind.PROGRAMMATIC,
            self._backend,(),output_type="proof",warrant=answer_warrant(store),scope=D.SCOPE,
            checker=lambda _: "CANNOT_CHECK")
        self.registry_key=self.rt.register_operator(self.op)

    def _observe(self):
        a=self.active;execution=a["execution"]
        execution["index"]=dict(a["index"].work)
        if a.get("engine") is not None:
            execution.update(parent_semantic_total=dict(a["engine"].counters),
                             prepared_binding_total=dict(a["engine"].binding_work))

    def _backend(self,ks,inputs):
        self.dispatches+=1
        self.active["execution"]={"preparations":0,"parent_completions":0,"candidate_attempts":[],
            "matching":[],"index_refusals":self.active["index"].refusals,"stage":"REQUEST_BINDING"}
        try:return self._propose(ks,inputs)
        except Exception as exc:
            reason=str(exc) if type(exc) is InputRefused else type(exc).__name__
            self.active["backend_failure"]=reason
            for attempt in self.active["execution"]["matching"]:
                if attempt["terminal"]=="ATTEMPTED":attempt["terminal"]="PARTIAL_WORK_UNAVAILABLE"
            return {"terminal":"CANNOT_CHECK","reason":reason}
        finally:self._observe()

    def _propose(self,ks,inputs):
        a=self.active
        if a is None or inputs!={"qid":a["qid"],"invoke":a["invoke"]}:raise InputRefused("DISPATCH_INPUT")
        data=read_request(self.store,a["qid"],a["request"])
        execution=a["execution"];execution["stage"]="PREPARATION"
        engine=RegionSolver(data["task"]["predicates"]);a["engine"]=engine
        execution["preparation_attempts"]=1;p=engine.prepare(data["task"]);execution["preparations"]=1
        use={"method_id":None,"rule_id":None,"binding":{},"cover":[],"recipes_applied":0,"replaced_branch":None}
        result=None
        if a["invoke"]:
            query=data["task"]["query"];universal=query["kind"] in ("every","no")
            kind=(query if universal else negate(query))["kind"]
            for mid in a["index"].select(kind):
                item=self.store.read(mid)
                if not item["eligible"]:raise InputRefused("METHOD_NOT_ELIGIBLE")
                execution["candidate_attempts"].append(mid)
                execution["stage"]="MATCH_AND_RECIPE"
                attempt={"method_id":mid,"terminal":"ATTEMPTED","counters":None}
                execution["matching"].append(attempt)
                proposed=apply_rule(item["envelope"]["rule"],data["task"],engine,p)
                attempt.update(terminal=proposed["terminal"],counters=proposed["counters"])
                if proposed["terminal"]=="PROPOSED":
                    result=proposed["result"]
                    use={"method_id":mid,"rule_id":proposed["method_id"],"binding":proposed["binding"],
                         "cover":proposed["cover"],"recipes_applied":1,"replaced_branch":"no" if universal else "yes"}
                    break
        if result is None:
            execution["stage"]="PARENT_COMPLETION"
            execution["parent_completions"]+=1;result=engine.complete(p)
        execution["stage"]="PROPOSAL_COMPLETE";self._observe()
        packet={"schema":"ocm.unary-method.packet.v1","task_sha256":data["task_sha256"],
                "result":result,"use":use,"execution":execution}
        a["issued"]=D.raw(packet)
        return D.parse(a["issued"])

    def _check(self,packet):
        self.checks+=1;a=self.active;work={}
        try:
            if a["issued"] is None or D.raw(packet)!=a["issued"]:raise InputRefused("UNISSUED_PACKET")
            check_packet(self.store,a["qid"],a["request"],packet,work=work)
            a["check"]={"status":"PASS","reason":"INDEPENDENT_CERTIFICATE_AND_BINDING","work":work}
            return SV.Status.PASS
        except (InputRefused,KeyError,TypeError,ValueError) as exc:
            a["check"]={"status":"CANNOT_CHECK","reason":str(exc),"work":work}
            return SV.Status.CANNOT_CHECK

    def solve(self,task,*,invoke=True):
        start=time.monotonic()
        if type(invoke) is not bool:raise InputRefused("INVOKE_TYPE")
        self.store._check_environment()
        if self.rt.state.operators.operators.get(self.registry_key) is not self.op:
            raise InputRefused("REGISTERED_DISPATCHER_CHANGED")
        if D.live(self.rt,answer_warrant(self.store))!="LIVE":
            return {"terminal":"CANNOT_CHECK","reason":"ANSWER_CHECKER_UNAVAILABLE","dispatches":0}
        if self.active is not None:raise InputRefused("ACTIVE_REQUEST")
        qid,data=request(self.store,task)
        from unary_method_journal import begin_use,record_use
        intent=begin_use(self.store,qid,data)
        index=MethodIndex(self.store)
        self.active={"qid":qid,"request":data,"invoke":invoke,"index":index,"issued":None,"check":None,"backend_failure":None,"execution":None,"engine":None}
        dispatch_before=self.dispatches;checks_before=self.checks
        wrapper=SV.OperatorSpec(self.op.operator_id,self.op.version,
            lambda ks,name,ctx:self.op.backend(ks,{"qid":qid,"invoke":invoke}),
            (qid,),output_type="proof",warrant=answer_warrant(self.store),scope=D.SCOPE,checker=self._check)
        try:
            outcome=self.rt.solve(SV.Task(qid,(SV.QueryPart(qid,"query_seed",(qid,)),),context=D.CONTEXT),(wrapper,))
            trace=outcome.trace.as_dict()
            receipt={"terminal":"CHECKED" if SV.committed(outcome) else "CANNOT_CHECK","qid":qid,
                     "trace":trace,"check":self.active["check"],"packet":outcome.answer,
                     "backend_failure":self.active["backend_failure"],
                     "execution_observation":self.active["execution"],
                     "dispatches":self.dispatches-dispatch_before,"checks":self.checks-checks_before,
                     "solve_wall_s":time.monotonic()-start}
            journal_start=time.monotonic()
            record_use(self.store,qid,data,receipt,intent)
            journal_wall=time.monotonic()-journal_start
            receipt["return_observation"]={"journal_wall_s":journal_wall,"total_wall_s":time.monotonic()-start}
            return receipt
        finally:self.active=None

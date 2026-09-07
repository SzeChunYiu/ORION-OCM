"""Direct conventional dispatcher over the same checked proposal computation."""
import time
from unary_contract import InputRefused,validate_task
from unary_method_verify_use import verify_use,verify_answer
import unary_method_plain as D
import unary_method_execution as E
from unary_method_postings import contents,select
from unary_parent_journal import validate_intent,validate_use

class ParentIndex:
    def __init__(self,store):
        self.store=store;self.work={"index_probes":0,"postings_examined":0}
        self.state=(store.head,store.revision);token=(store.selection,store.revision,store.source_sha)
        self.postings,self.refusals=contents(store,token,self.work)
    def validate(self):
        if (self.store.head,self.store.revision)!=self.state:raise InputRefused("STALE_INDEX")
    def select(self,kind):return select(self,kind)

class ParentRuntime:
    def __init__(self,store):
        self.store=store;self.engines=E.EnginePool();self.active=False
        self.dispatches=0;self.checks=0;self.last_observation=None

    def solve(self,value,*,invoke=True):
        start=time.monotonic();self.last_observation={"stage":"PUBLIC_ENTRY"};store=self.store;store._enter()
        if type(invoke) is not bool:raise InputRefused("INVOKE_TYPE")
        if self.active:raise InputRefused("ACTIVE_REQUEST")
        task=validate_task(D.parse(D.raw(value)))
        qid="parent:query:"+D.hashed({"task":task,"head":store.head})
        intent={"schema":"ocm.unary-parent.use-intent.v1","qid":qid,"task":task,
                "task_sha256":D.hashed(task),"selection":store.selection,"sources_sha256":store.source_sha,
                "revision":store.revision,"roles":D.parse(D.raw(store.roles)),"invoke":invoke}
        validate_intent(store,intent);store._append("USE_PREPARE",intent)
        self.active=True;engine=None;index=None;execution={"stage":"INDEX","matching":[]}
        self.last_observation={"execution_observation":execution}
        receipt={"terminal":"CANNOT_CHECK","qid":qid,"packet":None,"check":None,
                 "backend_failure":None,"dispatches":0,"checks":0}
        try:
            if not store.answers_live():raise InputRefused("ANSWER_CHECKER_UNAVAILABLE")
            index=ParentIndex(store);execution=E.begin(index)
            self.last_observation={"execution_observation":execution}
            engine=self.engines.get(task,execution);self.dispatches+=1;receipt["dispatches"]=1
            packet=E.propose(task,lookup=store.read,index=index,engine=engine,invoke=invoke,observation=execution)
            issued=D.raw(packet);receipt["checks"]=1;self.checks+=1;work={}
            if D.raw(packet)!=issued:raise InputRefused("UNISSUED_PACKET")
            if packet["task_sha256"]!=intent["task_sha256"] or not verify_answer(task,packet["result"],work=work,counter="independent_answer_checks"):
                raise InputRefused("ANSWER_CERTIFICATE")
            verify_use(task,packet["use"],store.read,work=work)
            receipt.update(terminal="CHECKED",packet=D.parse(issued),check={"status":"PASS","work":work})
        except Exception as exc:
            receipt["backend_failure"]=type(exc).__name__+":"+str(exc);E.partial(execution)
        finally:
            E.observe(execution,engine,index);self.active=False
        receipt.update(execution_observation=execution,solve_wall_s=time.monotonic()-start)
        self.last_observation=receipt
        body={"schema":"ocm.unary-parent.use.v1","intent_sha256":D.hashed(intent),"receipt":receipt}
        validate_use(store,body,intent)
        journal_start=time.monotonic();store._append("USE" if receipt["terminal"]=="CHECKED" else "USE_REFUSED",body)
        store.attempts.append(D.parse(D.raw(body)))
        if receipt["terminal"]=="CHECKED":store.uses.append(D.parse(D.raw(body)))
        receipt["return_observation"]={"journal_wall_s":time.monotonic()-journal_start,"total_wall_s":time.monotonic()-start}
        return receipt

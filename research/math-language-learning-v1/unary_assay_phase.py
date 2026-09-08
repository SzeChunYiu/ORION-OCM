"""Fixed coordinator process/copy boundary; external containment is still required."""
import resource,time
from pathlib import Path
from unary_contract import InputRefused
from unary_assay_service import remaining
from unary_assay_ledger import Ledger,write,read,copy_store,inventory
from unary_method_process import launch
from unary_method_profile import validate
import unary_method_outer as D
import unary_assay_auth as A

ARMS=("EXACT_PARENT","ADAPTIVE_PARENT","OCM_ENABLED","OCM_KNOCKOUT")
BACKEND={"EXACT_PARENT":"exact","ADAPTIVE_PARENT":"conventional","OCM_ENABLED":"ocm","OCM_KNOCKOUT":"ocm"}
ROLES=("schema_environment","discovery","utility")

def order(episode):return ARMS[episode:]+ARMS[:episode]

class Session:
    def __init__(self,root,*,deadline,profile):
        self.started=time.monotonic();self.cpu=time.process_time();self.work={}
        self.usage=resource.getrusage(resource.RUSAGE_CHILDREN)
        remaining(deadline);self.root=Path(root);self.root.mkdir(parents=True,exist_ok=False)
        self.deadline=deadline;self.profile=validate(profile);self.sources=D.sources(self.work)
        for name in ("calls","stores","reports"): (self.root/name).mkdir()
        self.ledger=Ledger(self.root/"ledger",deadline=deadline);self.abort=None;self.calls=[];self.copies=[]
        self.slots={};self.current_episode=None
        self.ledger.append("SESSION",{"scope":"INTERNAL_COORDINATOR_UNQUALIFIED_CONTAINMENT",
            "deadline_monotonic":deadline,"profile":self.profile,"sources":self.sources})

    def fail(self,kind,reason,*,slot=None):
        episode=self.slots.get(slot,{}).get("detail",{}).get("episode",self.current_episode)
        cause={"kind":kind,"reason":reason,"episode":episode,"slot":slot}
        if self.abort is None:self.abort={**cause,"causes":[cause]}
        else:
            if cause not in self.abort["causes"]:self.abort["causes"].append(cause)
            if kind=="SEMANTIC_CONTROL_FAILED" and self.abort["kind"]!="SEMANTIC_CONTROL_FAILED":
                self.abort.update(cause)

    def expect(self,slot,detail):
        if slot in self.slots:raise InputRefused("DUPLICATE_PHASE_SLOT")
        self.slots[slot]={"state":"REQUESTED","detail":detail}
        self.ledger.append("EXPECTED",{"slot":slot,**detail})

    def mark(self,slot,state,reason,**extra):
        if slot not in self.slots:raise InputRefused("UNREGISTERED_PHASE_SLOT")
        self.slots[slot].update(state=state,reason=reason,**extra)
        self.ledger.append("SLOT",{"slot":slot,**self.slots[slot]})

    def snapshot(self,source,name):
        remaining(self.deadline);work={}
        try:
            result=copy_store(source,self.root/"stores"/name,deadline=self.deadline,work=work)
            ref=write(self.root/"reports",name+"-copy.json",result);self.copies.append(ref)
            self.ledger.append("COPY",ref);remaining(self.deadline)
            return self.root/"stores"/name
        except Exception as exc:
            self.ledger.append("COPY_FAILED",{"name":name,"reason":type(exc).__name__+":"+str(exc),"work":work})
            self.fail("CANNOT_CHECK","COPY_CUSTODY:"+str(exc),slot=name)
            raise

    def call(self,slot,arm,mode,request):
        if self.abort is not None:
            self.mark(slot,"UNAVAILABLE","GLOBAL_ABORT");return None
        try:remaining(self.deadline)
        except InputRefused as exc:
            self.fail("CANNOT_CHECK",str(exc),slot=slot);self.mark(slot,"UNAVAILABLE",str(exc));return None
        self.mark(slot,"ATTEMPTED",None);work={};start=time.monotonic();cpu=time.process_time()
        path=self.root/"calls"/slot;facts=None;p=None;error=None;source_before=None
        record={"slot":slot,"arm":arm,"mode":mode,"request":request,"path":str(path),
                "call_started_monotonic":start,"source_before":source_before}
        try:
            source_before=D.sources(self.work);record["source_before"]=source_before
            if source_before!=self.sources:raise A.CustodyFailure("COORDINATOR_SOURCE")
            store=request.get("store")
            record["store_before_dispatch"]=None
            if store is not None:
                if mode=="acquire_selected":
                    if Path(store).exists() or Path(store).is_symlink():raise A.CustodyFailure("ACQUISITION_STORE_EXISTS")
                else:record["store_before_dispatch"]=A.artifact(inventory,store,deadline=self.deadline,work=work)
            if mode=="presented_batch":request={**request,"deadline_monotonic":self.deadline};record["request"]=request
            p=launch(path,mode,request,arm=BACKEND[arm],profile=self.profile,
                     timeout=remaining(self.deadline),deadline=self.deadline)
            record["process_observed"]=p
            record["launch_return_wall_s"]=time.monotonic()-start
            record["launch_return_own_cpu_s"]=time.process_time()-cpu
            remaining(self.deadline)
            if p["returncode"] is not None and p["returncode"]<0:raise A.CustodyFailure("CHILD_SIGNAL")
            store=request.get("store") if p["terminal"]=="COMPLETED" else None
            if store is not None:record["store_before_audit"]=A.artifact(inventory,store,deadline=self.deadline,work=work)
            facts=A.inspect(path,arm=BACKEND[arm],mode=mode,request=request,sources=self.sources,
                            profile=self.profile,deadline=self.deadline,work=work)
            if store is not None:
                record["store_after_audit"]=A.artifact(inventory,store,deadline=self.deadline,work=work)
                if record["store_before_audit"]!=record["store_after_audit"]:raise A.CustodyFailure("AUDIT_CHANGED_STORE")
            remaining(self.deadline)
        except A.ControlFailure as exc:
            error=str(exc);self.fail("SEMANTIC_CONTROL_FAILED",error,slot=slot)
        except A.CustodyFailure as exc:
            error=str(exc);self.fail("CANNOT_CHECK",error,slot=slot)
        except Exception as exc:
            error=type(exc).__name__+":"+str(exc)
            if "DEADLINE" in error or p is None:self.fail("CANNOT_CHECK",error,slot=slot)
        after=None
        try:after=D.sources(self.work)
        except Exception as exc:
            error=error or type(exc).__name__+":"+str(exc)
            self.fail("CANNOT_CHECK","SOURCE_AFTER_UNAVAILABLE",slot=slot)
        record.update(facts=facts,error=error,work=work,source_after=after,
                      call_return_wall_s=time.monotonic()-start,call_return_own_cpu_s=time.process_time()-cpu)
        if after is not None and after!=self.sources:
            error=error or "COORDINATOR_SOURCE";record["error"]=error;self.fail("CANNOT_CHECK",error,slot=slot)
        ref=write(self.root/"reports",slot+".json",record);self.calls.append(ref)
        complete=error is None and facts is not None and facts["terminal"]=="CHECKED"
        self.mark(slot,"COMPLETED" if complete else "UNAVAILABLE",error or (None if complete else "OPERATION_INCOMPLETE"),record=ref)
        return record

    def finalize(self,episodes):
        for slot,value in list(self.slots.items()):
            if value["state"] in ("REQUESTED","ATTEMPTED"):self.mark(slot,"UNAVAILABLE","UNREACHED")
        usage=resource.getrusage(resource.RUSAGE_CHILDREN)
        body={"schema":"ocm.unary-coordinator.v1","scope":"INTERNAL_UNQUALIFIED_CONTAINMENT",
              "root":str(self.root),"deadline_monotonic":self.deadline,"sources":self.sources,"profile":self.profile,
              "coordinator_work":dict(self.work),"episodes":episodes,"slots":self.slots,"calls":self.calls,"copies":self.copies,"abort":self.abort,
              "physical":{"wall_s":time.monotonic()-self.started,"own_cpu_s":time.process_time()-self.cpu,
                  "waited_child_user_s":usage.ru_utime-self.usage.ru_utime,
                  "waited_child_system_s":usage.ru_stime-self.usage.ru_stime}}
        ref=write(self.root,"COORDINATOR.json",body);self.ledger.append("FINAL",ref)
        return body

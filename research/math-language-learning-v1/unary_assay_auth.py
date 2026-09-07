"""Retained process and issuer authentication; never reconstruct missing answers."""
import time
from pathlib import Path
from unary_contract import InputRefused,task_digest
from unary_method_verify_use import verify_answer,verify_use
from unary_assay_rows import audit,read_row
from unary_method_process import stamp
import unary_method_plain as D

class ControlFailure(InputRefused):pass
class CustodyFailure(InputRefused):pass

def artifact(fn,*args,**kwargs):
    try:return fn(*args,**kwargs)
    except (CustodyFailure,ControlFailure):raise
    except (OSError,ValueError,KeyError,TypeError) as exc:
        raise CustodyFailure("PROMISED_ARTIFACT:"+type(exc).__name__+":"+str(exc)) from exc

def load(path,work):
    try:
        p=Path(path);st=p.lstat()
        import stat
        if not stat.S_ISREG(st.st_mode) or st.st_nlink!=1 or st.st_size>D.MAX_BYTES:raise CustodyFailure("ARTIFACT_ENTRY")
        with p.open("rb") as f:raw=f.read(D.MAX_BYTES+1)
        D.bump(work,"artifact_bytes_read",len(raw));D.bump(work,"artifact_reads")
        value=D.parse(raw)
        if type(value) is not dict:raise CustodyFailure("ARTIFACT_SHAPE")
        return value
    except CustodyFailure:raise
    except (OSError,ValueError,TypeError) as exc:raise CustodyFailure("ARTIFACT_UNAVAILABLE:"+str(exc)) from exc

def positive(row,arm):
    result=row.get("result")
    if row["terminal"]!="CHECKED" and result is None:result=row.get("partial_observation")
    if type(result) is not dict or result.get("terminal")!="CHECKED":
        if row["terminal"]=="CHECKED":raise CustodyFailure("CHECKED_RESULT_UNAVAILABLE")
        return None
    packet=result.get("packet")
    if (type(packet) is not dict or type(packet.get("task_sha256")) is not str
        or type(packet.get("result")) is not dict):
        raise CustodyFailure("CHECKED_PACKET_STRUCTURE")
    if arm!="exact" and (type(result.get("qid")) is not str or type(packet.get("use")) is not dict):
        raise CustodyFailure("CHECKED_USE_STRUCTURE")
    return result

def restore(path,arm):
    if arm=="conventional":
        from unary_parent_store import ParentStore
        return ParentStore(path)
    from ocm.runtime.ocm_runtime import OCMRuntime
    from unary_method_store import MethodStore
    return MethodStore(OCMRuntime(path))

def _process(root,*,arm,mode,request,sources,profile,deadline,work):
    root=Path(root);p=load(root/"PROCESS.json",work)
    if p["source_before"]!=sources or p["source_after"]!=sources:raise CustodyFailure("PROCESS_SOURCE")
    if p["profile"]!=profile or p["arm"]!=arm or p["deadline_monotonic"]!=deadline:
        raise CustodyFailure("PROCESS_BINDING")
    if p["pid"] is not None and (not p["reaped"] or not p["group_absent"]):raise CustodyFailure("PROCESS_CLEANUP")
    for name in ("request","stdout","stderr"):
        if p[name]!=stamp(root/{"request":"request.json","stdout":"stdout.bin","stderr":"stderr.bin"}[name]):
            raise CustodyFailure("PROCESS_RAW_CHANGED")
    if D.raw(load(root/"request.json",work))!=D.raw(request):raise CustodyFailure("PROCESS_REQUEST")
    if p["terminal"]!="COMPLETED":return p,None
    if p["returncode"]!=0 or not p["reaped"] or not p["group_absent"]:raise CustodyFailure("FALSE_PROCESS_COMPLETE")
    data=load(root/"result.json",work)
    if (data["mode"]!=mode or data["arm"]!=arm or data["pid"]!=p["pid"] or data["terminal"]!="COMPLETED"
        or data["profile"]!=profile or data["source_before"]!=sources or data["source_after"]!=sources
        or data["input_sha256"]!=D.hashed(request) or p["result"]!=stamp(root/"result.json")
        or p["result"]["sha256"]!=p["stdout"]["sha256"] or p["stderr"]["bytes"]!=0):
        raise CustodyFailure("CHILD_BINDING")
    return p,data

def process(root,**kwargs):return artifact(_process,root,**kwargs)

def inspect(root,*,arm,mode,request,sources,profile,deadline,work):
    start=time.monotonic();cpu=time.process_time();store=None;restore_attempted=False
    try:
        p,data=process(root,arm=arm,mode=mode,request=request,sources=sources,profile=profile,deadline=deadline,work=work)
        if data is None:return {"terminal":"CANNOT_CHECK","rows":[],"process":p,"reason":"PROCESS_REFUSED"}
        store=None;items={};facts={"terminal":"CHECKED","rows":[],"process":p}
        if arm!="exact":
            restore_attempted=True;store=restore(request["store"],arm)
            if data["issuer_head"]!=store.head:raise CustodyFailure("ISSUER_HEAD")
            if arm=="ocm" and data["core_head"]!=store.rt.events[-1].event_hash:raise CustodyFailure("CORE_HEAD")
            items={mid:store.read(mid) for mid in store.method_ids}
            facts["methods"]={mid:{k:item[k] for k in ("rule_id","correctness","selection","eligible")} for mid,item in items.items()}
        if mode=="acquire_selected":
            retained=(store.selection["receipt"] if arm=="ocm" else D.parse(store._raw[store.selection]))
            if D.raw(retained)!=D.raw(data["outcome"]):raise CustodyFailure("A_SELECTION_BINDING")
            facts["selection"]={k:retained[k] for k in ("terminal","pool_sha256","ranking_sha256","library_sha256")}
            facts["selected_rule_ids"]=[x["rule_id"] for x in retained["selected"]]
        elif mode=="revise":
            r=data["outcome"];role=request["role"];mid=request["method_id"]
            rid=(store.environment[role] if role in store.environment else items[mid]["envelope"][role]) if arm=="ocm" else (
                "role:"+role if role in ("semantics","schema_environment","answer_environment") else items[mid]["envelope"][role])
            if arm=="ocm":
                import unary_method_data as K
                state="REVOKED" if rid in store.rt.state.revoked|store.rt.state.evidence.revoked else "LIVE"
            else:state=store.roles[rid]["state"]
            if r["record"]!=rid or r["role"]!=role or r["state"]!=request["state"] or state!=request["state"]:
                raise ControlFailure("REVISION_NOT_APPLIED")
            facts["revision"]={"record":rid,"role":role,"state":state}
        elif mode=="presented_batch":
            artifact(audit,root,data,request,pid=p["pid"],work=work)
            refs=data["outcome"]["rows"];checked=[]
            for i,ref in enumerate(refs):
                row=artifact(read_row,root,ref,request["rows"][i],pid=p["pid"],work=work)
                if row["terminal"]!="CHECKED":facts["terminal"]="CANNOT_CHECK"
                result=positive(row,arm)
                if result is None:
                    facts.setdefault("unverified_reached_rows",[]).append(i);continue
                # The paired formal AST is provided by the coordinator, not guessed from answers.
                expected=request["rows"][i]
                from unary_language import parse
                task=parse(expected["payload"]) if expected["presentation"]=="text" else expected["payload"]
                packet=result["packet"]
                if packet["task_sha256"]!=task_digest(task) or not verify_answer(
                        task,packet["result"],work=work,counter="retained_answer_checks"):
                    raise ControlFailure("INVALID_ACCEPTED_ANSWER")
                use=packet.get("use");mid=None
                if arm!="exact":
                    qid=result["qid"];matches=[b for b in store.uses if b["receipt"]["qid"]==qid]
                    retained={k:v for k,v in result.items() if k!="return_observation"}
                    if len(matches)!=1 or D.raw(matches[0]["receipt"])!=D.raw(retained):raise ControlFailure("UNAUTHENTICATED_ACCEPTED_USE")
                    try:verify_use(task,use,items.__getitem__,work=work)
                    except (ValueError,KeyError,TypeError) as exc:
                        raise ControlFailure("INVALID_ACCEPTED_USE:"+str(exc)) from exc
                    if not request["invoke"] and use["recipes_applied"]:raise ControlFailure("KNOCKOUT_INVOKED")
                    checked.append(qid);mid=use["method_id"]
                elif use is not None:raise ControlFailure("EXACT_METHOD_USE")
                facts["rows"].append({"index":i,"terminal":row["terminal"],"observation_id":row["observation_id"],"row_id":row["row_id"],
                    "presentation":row["presentation"],"task_sha256":task_digest(task),"status":packet["result"]["status"],
                    "use":use,"wall_s":row["wall_s"],"cpu_s":row["cpu_s"],
                    "sink_wall_s":ref["write_wall_s"],"sink_cpu_s":ref["write_cpu_s"]})
            if store is not None:
                actual=[b["receipt"]["qid"] for b in store.uses]
                if data["prior_uses"]!=len(actual)-len(checked) or (checked and actual[-len(checked):]!=checked):
                    raise ControlFailure("RESTART_USE_SEQUENCE")
            if data["outcome"]["terminal"]!="CHECKED":facts["terminal"]="CANNOT_CHECK"
        if store is not None:
            facts.update(replay_work=dict(store.work),prior_uses=data["prior_uses"],use_count=len(store.uses))
        return facts
    finally:
        if store is not None:work["replay_work"]=dict(store.work)
        elif restore_attempted:work["replay_work_unavailable"]="RESTORE_DID_NOT_RETURN"
        work["retained_audit_wall_s"]=time.monotonic()-start;work["retained_audit_cpu_s"]=time.process_time()-cpu

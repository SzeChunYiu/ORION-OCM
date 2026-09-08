"""Presented-input service; supplied order is authoritative, not a study schedule."""
import hashlib,math,os,re,time
from unary_contract import InputRefused,fields,task_digest,validate_task
from unary_language import parse
import unary_method_plain as D
import unary_assay_observe as O

def remaining(deadline):
    if type(deadline) not in (int,float) or not math.isfinite(deadline):
        raise InputRefused("ABSOLUTE_DEADLINE")
    left=deadline-time.monotonic()
    if left<=0:raise InputRefused("DEADLINE_EXPIRED")
    return left

def validate_rows(value):
    value=D.parse(D.raw(value))
    if type(value) is not list or not 1<=len(value)<=128:raise InputRefused("PRESENTED_ROWS_BOUND")
    seen=set()
    for row in value:
        fields(row,("observation_id","row_id","presentation","payload","task_sha256"))
        for name in ("observation_id","row_id"):
            if type(row[name]) is not str or not 1<=len(row[name])<=256:
                raise InputRefused("PRESENTED_ID")
        if row["observation_id"] in seen:raise InputRefused("DUPLICATE_OBSERVATION")
        seen.add(row["observation_id"])
        if type(row["presentation"]) is not str or row["presentation"] not in ("ast","text"):
            raise InputRefused("PRESENTATION")
        if type(row["task_sha256"]) is not str or re.fullmatch("[0-9a-f]{64}",row["task_sha256"]) is None:
            raise InputRefused("PRESENTED_DIGEST")
    return value

def run(runtime,value,*,deadline,invoke=True,observation=None,sink=None):
    o={} if observation is None else observation
    o.update(stage="PRESENTED_METADATA",rows=[],totals={},unreached_rows=[])
    start=time.monotonic();rows=validate_rows(value)
    if type(invoke) is not bool:raise InputRefused("INVOKE_TYPE")
    if type(deadline) not in (int,float) or not math.isfinite(deadline):raise InputRefused("ABSOLUTE_DEADLINE")
    o["order_sha256"]=D.hashed(rows);o["deadline_monotonic"]=deadline
    for i,row in enumerate(rows):
        try:remaining(deadline)
        except InputRefused as exc:
            o.update(stage="DEADLINE_BEFORE_ROW",reason=str(exc),unreached_rows=list(range(i,len(rows))))
            break
        stamp=time.monotonic();cpu=time.process_time();entered=False;result=None;partial=None
        item={"index":i,"observation_id":row["observation_id"],"row_id":row["row_id"],
              "presentation":row["presentation"],"input_sha256":D.hashed(row),"pid":os.getpid(),
              "terminal":"ATTEMPTED","result":None,"parse":{"parse_calls":0,"ast_validation_calls":0,
              "task_digest_calls":0,"serialized_input_bytes":len(D.raw(row["payload"]))}}
        o["rows"].append(item);before=O.store_work(runtime);o["stage"]="INPUT"
        parse_start=time.monotonic()
        try:
            if row["presentation"]=="text":
                item["parse"]["parse_calls"]=1;task=parse(row["payload"])
            else:
                item["parse"]["ast_validation_calls"]=1;task=validate_task(row["payload"])
            item["parse"]["task_digest_calls"]=1;digest=task_digest(task)
            item["parse"]["task_sha256"]=digest
            if digest!=row["task_sha256"]:raise InputRefused("PRESENTED_TASK_DIGEST")
            item["parse"]["wall_s"]=time.monotonic()-parse_start
            remaining(deadline);o["stage"]="SOLVING";entered=True
            result=runtime.solve(task,invoke=invoke);item["result"]=result
            item["terminal"]=result["terminal"]
            if item["terminal"]!="CHECKED":item["reason"]=result.get("reason",result.get("backend_failure"))
            remaining(deadline)
        except Exception as exc:
            item.update(terminal="CANNOT_CHECK",reason=type(exc).__name__+": "+str(exc))
            if entered:partial=D.parse(D.raw(getattr(runtime,"last_observation",None)))
        finally:
            item["parse"].setdefault("wall_s",time.monotonic()-parse_start)
            if partial is not None:item["partial_observation"]=partial
            try:
                item["call_totals"]=O.capture(result,partial)
                item["store_work_before"]=before;item["store_work_after"]=O.store_work(runtime)
                item["store_work_delta"]=O.store_delta(before,item["store_work_after"])
                O.aggregate(o["totals"],item)
            except Exception as exc:
                item.update(terminal="CANNOT_CHECK",observation_error=type(exc).__name__+": "+str(exc))
                o["totals_complete"]=False
            item["wall_s"]=time.monotonic()-stamp;item["cpu_s"]=time.process_time()-cpu
        if sink is not None:
            try:
                o["stage"]="ROW_WRITE"
                ref=sink(item);o["rows"][-1]=ref
                o.setdefault("sink",{"rows":0,"bytes":0,"write_wall_s":0.0,"write_cpu_s":0.0})
                o["sink"]["rows"]+=1;o["sink"]["bytes"]+=ref["bytes"]
                o["sink"]["write_wall_s"]+=ref["write_wall_s"];o["sink"]["write_cpu_s"]+=ref["write_cpu_s"]
                remaining(deadline)
            except Exception as exc:
                o.update(terminal="CANNOT_CHECK",reason=type(exc).__name__+": "+str(exc),
                         unreached_rows=list(range(i+1,len(rows))),service_wall_s=time.monotonic()-start)
                return o
        if item["terminal"]!="CHECKED":
            o["unreached_rows"]=list(range(i+1,len(rows)));break
    complete=len(o["rows"])==len(rows) and all(x["terminal"]=="CHECKED" for x in o["rows"])
    o.update(terminal="CHECKED" if complete else "CANNOT_CHECK",service_wall_s=time.monotonic()-start)
    if complete:o["stage"]="PRESENTED_COMPLETE"
    return o

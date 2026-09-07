"""Single-log admission/use recovery with explicit pending-state refusal."""
from unary_contract import InputRefused,fields,validate_task
from unary_method_verify_use import verify_use,verify_answer
import unary_method_plain as D
import unary_parent_payloads as P

def validate_intent(store,body):
    fields(body,("schema","qid","task","task_sha256","selection","sources_sha256","revision","roles","invoke"))
    validate_task(body["task"])
    if (body["schema"]!="ocm.unary-parent.use-intent.v1" or body["sources_sha256"]!=store.source_sha
        or body["selection"]!=store.selection or body["task_sha256"]!=D.hashed(body["task"])
        or type(body["qid"]) is not str or type(body["invoke"]) is not bool
        or type(body["revision"]) is not int or body["revision"]!=store.revision
        or D.raw(body["roles"])!=D.raw(store.roles)):raise InputRefused("PARENT_USE_INTENT")

def validate_use(store,body,intent):
    fields(body,("schema","intent_sha256","receipt"))
    if body["schema"]!="ocm.unary-parent.use.v1" or body["intent_sha256"]!=D.hashed(intent):
        raise InputRefused("PARENT_USE_BINDING")
    r=body["receipt"]
    fields(r,("terminal","qid","packet","check","execution_observation","backend_failure","dispatches","checks","solve_wall_s"))
    if r["qid"]!=intent["qid"] or r["terminal"] not in ("CHECKED","CANNOT_CHECK"):raise InputRefused("PARENT_USE_TERMINAL")
    if r["terminal"]=="CHECKED":
        p=r["packet"];fields(p,("schema","task_sha256","result","use","execution"))
        if (p["schema"]!="ocm.unary-method.packet.v1" or p["task_sha256"]!=intent["task_sha256"]
            or type(r["dispatches"]) is not int or r["dispatches"]!=1 or type(r["checks"]) is not int
            or r["checks"]!=1 or r["check"]["status"]!="PASS" or r["backend_failure"] is not None
            or D.raw(p["execution"])!=D.raw(r["execution_observation"])):raise InputRefused("PARENT_USE_EXECUTION")
        if any(intent["roles"]["role:"+x]["state"]!="LIVE" for x in ("semantics","answer_environment")):
            raise InputRefused("PARENT_HISTORICAL_CHECKER")
        if not verify_answer(intent["task"],p["result"],work=store.work,counter="use_answer_revalidations"):raise InputRefused("PARENT_ANSWER")
        def lookup(mid):
            item=store.read(mid);env=item["envelope"];roles=intent["roles"]
            item["eligible"]=all(roles[env[x]]["state"]=="LIVE" for x in ("semantics","schema_environment","utility"))
            return item
        verify_use(intent["task"],p["use"],lookup,work=store.work)
        if not intent["invoke"] and p["use"]["recipes_applied"]:raise InputRefused("PARENT_KNOCKOUT_USE")
    elif r["packet"] is not None:raise InputRefused("PARENT_REFUSED_ANSWER")
    return r

def restore(store):
    rows=store.journal.entries();D.bump(store.work,"journal_rows_read",len(rows))
    if not rows or rows[0].kind!="INIT":raise InputRefused("PARENT_INIT")
    init=D.parse(D.raw(rows[0].payload));fields(init,("schema","sources"))
    if init["schema"]!="ocm.unary-parent.v1" or init["sources"]!=store.source_map:raise InputRefused("PARENT_SOURCE")
    store.refs={};store.records={};store.selection=None;store.revision=0
    store.roles={"role:"+r:{"role":r,"state":"LIVE"} for r in ("semantics","schema_environment","answer_environment")}
    store.uses=[];store.attempts=[];pending=None;intents={};finished=[];seen=set()
    for row in rows[1:]:
        b=D.parse(D.raw(row.payload));D.bump(store.work,"journal_records_decoded")
        if row.kind=="ADMIT_PREPARE":
            fields(b,("schema","selection","records","refs","sources_sha256"))
            if pending is not None or store.selection is not None or b["schema"]!="ocm.unary-parent.admission.v1" or b["sources_sha256"]!=store.source_sha:
                raise InputRefused("PARENT_ADMISSION")
            pending=b
        elif row.kind=="ADMIT":
            fields(b,("intent_sha256",))
            if pending is None or b["intent_sha256"]!=D.hashed(pending):raise InputRefused("PARENT_ADMISSION_BINDING")
            store.selection=pending["selection"];store.refs=pending["refs"];store.records=pending["records"]
            if set(store.refs)!={store.selection,*store.records.values()}:raise InputRefused("PARENT_REFERENCES")
            store._raw=P.validate(store.payloads,store.refs,store.work)
            for mid,digest in store.records.items():
                env=D.parse(store._raw[digest])
                for role in ("discovery","utility"):
                    rid=env[role]
                    expected="discovery:"+store.selection if role=="discovery" else "utility:"+env["rule"]["rule_id"]
                    if rid!=expected:raise InputRefused("PARENT_ROLE_ID")
                    store.roles[rid]={"role":role,"state":"LIVE"}
            store._validate_library();pending=None
        elif row.kind=="REVISE":
            fields(b,("record","role","state","revision"))
            if (b["record"] not in store.roles or store.roles[b["record"]]["role"]!=b["role"]
                or b["state"] not in ("LIVE","REVOKED","UNKNOWN") or type(b["revision"]) is not int
                or b["revision"]!=store.revision+1):raise InputRefused("PARENT_REVISION")
            store.roles[b["record"]]={"role":b["role"],"state":b["state"]};store.revision=b["revision"]
        elif row.kind=="USE_PREPARE":
            validate_intent(store,b)
            if pending is not None or intents or b["qid"] in seen:raise InputRefused("PARENT_USE_SEQUENCE")
            seen.add(b["qid"]);intents[b["qid"]]=b
        elif row.kind in ("USE","USE_REFUSED"):
            qid=b.get("receipt",{}).get("qid")
            if qid not in intents:raise InputRefused("PARENT_UNMATCHED_USE")
            intent=intents.pop(qid);receipt=validate_use(store,b,intent)
            if (row.kind=="USE")!=(receipt["terminal"]=="CHECKED"):raise InputRefused("PARENT_USE_KIND")
            store.attempts.append(b)
            if row.kind=="USE":store.uses.append(b)
        else:raise InputRefused("PARENT_ROW_KIND")
    if pending is not None:raise InputRefused("INCOMPLETE_ADMISSION")
    if intents:raise InputRefused("INCOMPLETE_USE")
    store.head=rows[-1].entry_hash

"""Intent/final use records; historical checking never implies current liveness."""
from unary_contract import InputRefused,fields
from unary_method_check import check_packet,read_request
import unary_method_data as D

def validate_intent(store,body):
    fields(body,("schema","sources_sha256","qid","request","core_sequence","core_hash"))
    if body["schema"]!="ocm.unary-method.use-intent.v1" or body["sources_sha256"]!=store.source_sha:
        raise InputRefused("USE_INTENT_SOURCE")
    i=body["core_sequence"]
    if type(i) is not int or not 1<=i<=len(store.rt.events):raise InputRefused("USE_INTENT_SEQUENCE")
    if store.rt.events[i-1].event_hash!=body["core_hash"]:raise InputRefused("USE_INTENT_HEAD")
    read_request(store,body["qid"],body["request"])
    return body

def begin_use(store,qid,request):
    body={"schema":"ocm.unary-method.use-intent.v1","sources_sha256":store.source_sha,
          "qid":qid,"request":request,"core_sequence":len(store.rt.events),
          "core_hash":store.rt.events[-1].event_hash}
    validate_intent(store,body);store._append("USE_PREPARE",body)
    store.intents[qid]=D.parse(D.raw(body))
    return D.parse(D.raw(body))

def validate_receipt(store,body,intent,*,successful=True):
    fields(body,("schema","sources_sha256","qid","request","receipt","core_events","intent_sha256"))
    validate_intent(store,intent)
    if (body["schema"]!="ocm.unary-method.use.v1" or body["sources_sha256"]!=store.source_sha
        or body["intent_sha256"]!=D.hashed(intent) or body["qid"]!=intent["qid"]
        or D.raw(body["request"])!=D.raw(intent["request"])):raise InputRefused("USE_SOURCE")
    receipt=body["receipt"]
    fields(receipt,("terminal","qid","trace","check","packet","dispatches","checks","solve_wall_s",
                    "backend_failure","execution_observation"))
    if receipt["qid"]!=body["qid"]:raise InputRefused("USE_QUERY")
    if receipt["terminal"]!=("CHECKED" if successful else "CANNOT_CHECK"):raise InputRefused("USE_TERMINAL")
    stages=receipt["trace"]["stages"]
    if receipt["trace"]["task_id"]!=body["qid"] or not stages:raise InputRefused("USE_TRACE")
    committed=stages[-1]["stage"]=="COMMITMENT" and stages[-1]["status"]=="PASS"
    if committed!=successful:raise InputRefused("USE_COMMITMENT")
    actual=[s for s in stages if s["stage"] in ("NAVIGATION","EXTRACTION","COMPOSITION","CHECK")]
    events=store.rt.events;refs=body["core_events"]
    if type(refs) is not list or len(refs)!=1+len(actual):raise InputRefused("USE_CORE_EVENTS")
    selected=[]
    for offset,ref in enumerate(refs,1):
        fields(ref,("sequence","hash"));i=ref["sequence"]
        if type(i) is not int or i!=intent["core_sequence"]+offset or i>len(events):
            raise InputRefused("USE_CORE_SEQUENCE")
        ev=events[i-1]
        if ev.sequence!=i or ev.event_hash!=ref["hash"]:raise InputRefused("USE_CORE_HASH")
        selected.append(ev)
    first=selected[0]
    if (first.event_type.value!="QUERY_OPENED" or first.payload["task_id"]!=body["qid"]
        or first.prev_hash!=intent["core_hash"]):raise InputRefused("USE_CORE_QUERY")
    kinds={"NAVIGATION":"NAVIGATION","EXTRACTION":"EXTRACTION","COMPOSITION":"CANDIDATE_COMPOSED","CHECK":"CHECKER_RESULT"}
    for ev,stage in zip(selected[1:],actual):
        if ev.event_type.value!=kinds[stage["stage"]] or D.raw(dict(ev.payload))!=D.raw({**stage,"admitted":False}):
            raise InputRefused("USE_TRACE_BINDING")
    if successful:
        if (receipt["backend_failure"] is not None or type(receipt["dispatches"]) is not int
            or receipt["dispatches"]!=1 or type(receipt["checks"]) is not int or receipt["checks"]!=1
            or receipt["check"]["status"]!="PASS"):raise InputRefused("USE_EXECUTION")
        if D.raw(receipt["execution_observation"])!=D.raw(receipt["packet"]["execution"]):
            raise InputRefused("USE_EXECUTION_BINDING")
        check_packet(store,body["qid"],body["request"],receipt["packet"],current=False,work=store.work)
    elif receipt["packet"] is not None:raise InputRefused("REFUSED_USE_HAS_ANSWER")
    return body

def record_use(store,qid,request,receipt,intent):
    events=store.rt.events[intent["core_sequence"]:]
    body={"schema":"ocm.unary-method.use.v1","sources_sha256":store.source_sha,"qid":qid,
          "request":request,"receipt":receipt,"intent_sha256":D.hashed(intent),
          "core_events":[{"sequence":e.sequence,"hash":e.event_hash} for e in events]}
    body=D.parse(D.raw(body));success=receipt["terminal"]=="CHECKED"
    validate_receipt(store,body,intent,successful=success)
    if any(old["qid"]==qid for old in store.attempts):raise InputRefused("DUPLICATE_USE")
    store._append("USE" if success else "USE_REFUSED",body)
    store.attempts.append(body)
    if success:store.uses.append(body)

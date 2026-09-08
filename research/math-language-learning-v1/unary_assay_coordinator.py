"""Internal fixed coordinator; no CLI, STARTED issuer, or containment authority."""
import time
from unary_contract import InputRefused,validate_task
from unary_assay_service import remaining
from unary_assay_phase import Session
from unary_assay_schedule import expected,episode
from unary_assay_generate import generate_episode
from unary_assay_identity import semantic_key,syntax_key
import unary_method_plain as D

SIZES={"training":32,"development":16,"final":32}

def authored_partitions(values,e,work):
    if type(values) is not dict or set(values)!=set(SIZES):raise InputRefused("AUTHORED_PARTITIONS")
    parts={}
    for split,limit in SIZES.items():
        rows=values[split]
        if type(rows) is not list or not 1<=len(rows)<=limit:raise InputRefused("AUTHORED_PARTITION_COUNT")
        split="train" if split=="training" else split
        parts[split]=[]
        for i,value in enumerate(rows):
            task=validate_task(value)
            parts[split].append({"row_id":f"e{e}/{split}/{i}","task":task,
                "semantic_key":semantic_key(task,work),"syntax_key":syntax_key(task,work=work)})
    return {"terminal":"GENERATED","partitions":parts,"scope":"AUTHORED_INPUTS","work":work}

def _run(root,*,deadline,profile,authored=None):
    session=Session(root,deadline=deadline,profile=profile);out=[]
    count=4 if authored is None else len(authored)
    for e in range(count):expected(session,e,32 if authored is None else len(authored[e]["final"]))
    for e in range(count):
        session.current_episode=e
        start=time.monotonic();cpu=time.process_time();work={};observation={};generated=None;stage="GENERATION"
        if session.abort is not None:
            out.append({"episode":e,"generation_terminal":"UNAVAILABLE","reason":"GLOBAL_ABORT"});continue
        try:
            remaining(deadline)
            if authored is None:
                generated=generate_episode(e,sink=lambda row:session.ledger.append("GENERATOR",row),
                    deadline=deadline,work=work,observation=observation)
            else:generated=authored_partitions(authored[e],e,work)
            session.ledger.append("GENERATION",{"episode":e,"result":generated})
            remaining(deadline)
            stage="EPISODE";result=episode(session,e,generated,authored=authored is not None)
        except Exception as exc:
            result={"episode":e,"generation_terminal":"CANNOT_CHECK" if generated is None else generated["terminal"],
                    "failed_stage":stage,"reason":type(exc).__name__+":"+str(exc)}
            session.ledger.append("EPISODE_EXCEPTION",{"episode":e,"reason":result["reason"],
                                                       "work":work,"known_observation":observation})
            if "DEADLINE" in str(exc):session.fail("CANNOT_CHECK",result["reason"])
        result["coordinator_episode_wall_s"]=time.monotonic()-start
        result["coordinator_episode_own_cpu_s"]=time.process_time()-cpu
        out.append(result);session.ledger.append("EPISODE",result)
    return session.finalize(out)

def run(root,*,deadline,profile):
    """Future qualified entry must supply its original externally supervised deadline."""
    return _run(root,deadline=deadline,profile=profile)

def run_authored(root,inputs,*,deadline,profile):
    """Engineering-only explicit partitions; never invokes or changes the registered master."""
    values=D.parse(D.raw(inputs))
    if type(values) is not list or not 1<=len(values)<=4:raise InputRefused("AUTHORED_EPISODE_COUNT")
    return _run(root,deadline=deadline,profile=profile,authored=values)

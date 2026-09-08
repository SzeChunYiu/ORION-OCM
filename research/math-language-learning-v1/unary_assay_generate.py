"""Pure episode allocation with mandatory durable-sink and absolute-deadline seams."""
import json,math,time
from unary_contract import InputRefused
from unary_rule_contract import count,encoded
import unary_assay_identity as I
import unary_assay_stream as S

def _episode(episode,source,targets,limit,*,sink,deadline,clock,work,observation):
    """Injected authored source/limits are a test seam; production fixes both."""
    S._index(episode,S.EPISODES,"EPISODE")
    if type(work) is not dict or type(observation) is not dict:raise TypeError("work/observation must be dict")
    if type(deadline) not in (int,float) or not math.isfinite(deadline):raise InputRefused("DEADLINE")
    if type(limit) is not int or not 1<=limit<=S.MAX_ATTEMPTS:raise InputRefused("DRAW_LIMIT")
    if not targets or tuple(s for s,n in targets)!=S.SPLITS[:len(targets)]:raise InputRefused("SPLIT_ORDER")
    for split,n in targets:
        if type(n) is not int or not 1<=n<=S.SIZES[S.SPLITS.index(split)]:raise InputRefused("SLOT_COUNT")
    o=observation;start=time.monotonic();syntax=set();semantic=set()
    o.update(stage="START",partitions={s:[] for s,n in targets},missing=[])
    def expired():
        count(work,"deadline_reads");return clock()>=deadline
    def emit(row):
        row["work_before_append"]=dict(work)
        detached=json.loads(encoded(row,work));o["active_record"]=detached
        count(work,"sink_attempts");begin=time.monotonic()
        try:sink(detached)
        except BaseException:
            o["stage"]="RECORDING_CANNOT_CHECK";raise
        else:count(work,"sink_successes")
        finally:count(work,"sink_wall_s",time.monotonic()-begin)
    failure=None
    for split,n in targets:
        accepted=o["partitions"][split];attempt=0
        if failure is not None:
            for slot in range(n):o["missing"].append({"row_id":f"e{episode}/{split}/{slot}","reason":"DEPENDENCY_UNAVAILABLE"})
            continue
        while len(accepted)<n and attempt<limit:
            slot=len(accepted)
            if expired():failure="DEADLINE";break
            row={"kind":"DRAW","episode":episode,"split":split,"attempt":attempt,"slot":slot,
                 "row_id":f"e{episode}/{split}/{slot}","candidate":None,"syntax_key":None,"semantic_key":None,
                 "reason":None,"authority":"PROVISIONAL_UNTIL_EPISODE_RESULT"}
            try:
                o["stage"]="DRAW";count(work,"candidate_attempts")
                candidate=source(split,attempt,slot);row["candidate"]=candidate
                if (candidate["split"]!=split or candidate["attempt"]!=attempt or candidate["slot"]!=slot
                    or candidate["task_bytes"]!=encoded(candidate["task"],work).decode()):
                    raise InputRefused("DRAW_RECORD_BINDING")
                o["stage"]="GATE"
                reason="DEADLINE" if expired() else I.gate(candidate["task"],split,work=work)
                if reason is None:
                    o["stage"]="SYNTAX_IDENTITY"
                    if expired():reason="DEADLINE"
                    else:
                        row["syntax_key"]=I.syntax_key(candidate["task"],work=work)
                        if row["syntax_key"] in syntax:reason="SYNTAX_DUPLICATE"
                if reason is None:
                    o["stage"]="SEMANTIC_IDENTITY"
                    if expired():reason="DEADLINE"
                    else:
                        row["semantic_key"]=I.semantic_key(candidate["task"],work)
                        if row["semantic_key"] in semantic:reason="SEMANTIC_DUPLICATE"
                if expired():reason="DEADLINE"
                row["reason"]=reason or "ACCEPTED"
            except Exception as exc:
                row["reason"]="DRAW_EXCEPTION" if o["stage"]=="DRAW" else "IDENTITY_EXCEPTION"
                row["error"]=type(exc).__name__+":"+str(exc);o["error"]=row["error"]
            emit(row);attempt+=1
            if row["reason"] in ("DEADLINE","DRAW_EXCEPTION","IDENTITY_EXCEPTION"):
                failure=row["reason"];break
            if expired():failure="DEADLINE_AFTER_APPEND";break
            count(work,"decision_"+row["reason"])
            if row["reason"]=="ACCEPTED":
                syntax.add(row["syntax_key"]);semantic.add(row["semantic_key"])
                accepted.append(json.loads(encoded({"row_id":row["row_id"],"attempt":attempt-1,
                    "task":row["candidate"]["task"],"syntax_key":row["syntax_key"],"semantic_key":row["semantic_key"]},work)))
        if len(accepted)<n:
            failure=failure or "DRAW_LIMIT"
            for slot in range(len(accepted),n):
                o["missing"].append({"row_id":f"e{episode}/{split}/{slot}","reason":failure})
    o["stage"]="EPISODE_RESULT"
    result={"kind":"EPISODE_RESULT","episode":episode,"terminal":"GENERATION_CANNOT_CHECK" if o["missing"] else "GENERATED",
            "partitions":o["partitions"],"missing":o["missing"],
            "accepted_syntax":sorted(syntax),"accepted_semantic":sorted(semantic)}
    emit(result)
    if expired() and result["terminal"]=="GENERATED":
        result["terminal"]="GENERATION_CANNOT_CHECK";result["reason"]="DEADLINE_AFTER_RESULT_APPEND"
        emit({"kind":"EPISODE_OVERRUN","episode":episode,"reason":result["reason"]})
    o["stage"]="COMPLETE";result=json.loads(encoded(result,work))
    count(work,"generation_wall_s",time.monotonic()-start);result["work"]=dict(work)
    return result

def generate_episode(episode,*,sink,deadline,work,observation):
    """Registered entry, deliberately without a CLI or automatic scientific dispatch."""
    return _episode(episode,lambda split,d,slot:S.draw(episode,split,d,slot,work=work),
        tuple(zip(S.SPLITS,S.SIZES)),S.MAX_ATTEMPTS,sink=sink,deadline=deadline,
        clock=time.monotonic,work=work,observation=observation)

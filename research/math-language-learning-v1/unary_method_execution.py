"""Shared mechanical proposal work; neither dispatch nor persistence authority."""
from unary_contract import InputRefused,negate
from unary_solver import RegionSolver
from unary_rule_apply import apply_rule
import unary_method_plain as D

class EnginePool:
    def __init__(self):self.engines={}
    def get(self,task,observation):
        key=tuple(task["predicates"])
        observation["registry_key_names"]=len(key)
        observation["engine_cache_reused"]=key in self.engines
        if key not in self.engines:self.engines[key]=RegionSolver(list(key))
        return self.engines[key]

def begin(index):
    return {"preparations":0,"parent_completions":0,"candidate_attempts":[],
            "matching":[],"index_refusals":index.refusals,"stage":"REQUEST_BINDING"}

def observe(execution,engine,index=None):
    if index is not None:execution["index"]=dict(index.work)
    if engine is not None:
        execution.update(parent_semantic_total=dict(engine.counters),
                         prepared_binding_total=dict(engine.binding_work))

def partial(execution):
    for attempt in execution["matching"]:
        if attempt["terminal"]=="ATTEMPTED":attempt["terminal"]="PARTIAL_WORK_UNAVAILABLE"

def propose(task,*,lookup,index,engine,invoke,observation,apply=apply_rule):
    e=observation;e["stage"]="PREPARATION";e["preparation_attempts"]=1
    try:
        p=engine.prepare(task);e["preparations"]=1
        use={"method_id":None,"rule_id":None,"binding":{},"cover":[],"recipes_applied":0,"replaced_branch":None}
        result=None
        if invoke:
            query=task["query"];universal=query["kind"] in ("every","no")
            kind=(query if universal else negate(query))["kind"]
            for mid in index.select(kind):
                item=lookup(mid)
                if not item["eligible"]:raise InputRefused("METHOD_NOT_ELIGIBLE")
                e["candidate_attempts"].append(mid);e["stage"]="MATCH_AND_RECIPE"
                attempt={"method_id":mid,"terminal":"ATTEMPTED","counters":None}
                e["matching"].append(attempt)
                proposed=apply(item["envelope"]["rule"],task,engine,p)
                attempt.update(terminal=proposed["terminal"],counters=proposed["counters"])
                if proposed["terminal"]=="PROPOSED":
                    result=proposed["result"]
                    use={"method_id":mid,"rule_id":proposed["method_id"],"binding":proposed["binding"],
                         "cover":proposed["cover"],"recipes_applied":1,"replaced_branch":"no" if universal else "yes"}
                    if "dependency" in proposed:use["dependency"]=proposed["dependency"]
                    break
        if result is None:
            e["stage"]="PARENT_COMPLETION";e["parent_completions"]+=1;result=engine.complete(p)
        e["stage"]="PROPOSAL_COMPLETE"
        observe(e,engine,index)
        return {"schema":"ocm.unary-method.packet.v1","task_sha256":D.hashed(task),
                "result":result,"use":use,"execution":D.parse(D.raw(e))}
    finally:observe(e,engine,index)

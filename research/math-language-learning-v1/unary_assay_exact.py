"""Direct exact service: existing warm engine, no adaptive admission or journal."""
import time
from unary_contract import InputRefused,validate_task
from unary_method_execution import EnginePool,observe
from unary_method_verify_use import verify_answer
import unary_method_plain as D

class ExactRuntime:
    def __init__(self):
        self.engines=EnginePool();self.last_observation=None

    def solve(self,value,*,invoke=True):
        start=time.monotonic();e={"stage":"TASK_VALIDATION","matching":[]}
        out={"terminal":"CANNOT_CHECK","packet":None,"check":None,"dispatches":0,"checks":0,
             "execution_observation":e}
        self.last_observation=out;engine=None;work={}
        try:
            if type(invoke) is not bool or not invoke:raise InputRefused("EXACT_HAS_NO_KNOCKOUT")
            task=validate_task(value);engine=self.engines.get(task,e)
            e.update(stage="PREPARATION",preparation_attempts=1)
            p=engine.prepare(task);e["preparations"]=1
            e.update(stage="EXACT_COMPLETION",parent_completions=1);out["dispatches"]=1
            result=engine.complete(p)
            e["stage"]="ANSWER_CHECK";out["checks"]=1
            out["check"]={"status":"CANNOT_CHECK","work":work}
            if not verify_answer(task,result,work=work,counter="independent_answer_checks"):
                raise InputRefused("ANSWER_CERTIFICATE")
            out.update(terminal="CHECKED",packet={"task_sha256":D.hashed(task),"result":result})
            out["check"]["status"]="PASS";e["stage"]="CHECKED"
        except Exception as exc:out["reason"]=type(exc).__name__+": "+str(exc)
        finally:
            if e.get("preparation_attempts"):observe(e,engine)
            out["return_observation"]={"total_wall_s":time.monotonic()-start}
        return out

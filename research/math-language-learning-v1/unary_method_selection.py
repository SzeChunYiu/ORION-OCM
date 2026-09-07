"""Real warm training, mechanical mining, and fresh-trial development selection."""
import hashlib,time
from pathlib import Path
from unary_contract import InputRefused,fields,validate_task
from unary_solver import RegionSolver
from unary_method_verify_use import verify_answer
from unary_rule_acquire import acquire
from unary_rule_apply import apply_rule
from unary_method_execution import EnginePool,observe
import unary_method_plain as D

SCHEMA="ocm.unary-selection.v1"
def policy_hash():
    root=Path(__file__).resolve().parents[2]/"docs/plans/unary-adaptive-parent-v2-1"
    names=("CORE","GENERATOR","SELECTION","EXECUTION","PARENT-POLICY","FAILURES")
    return D.hashed({n:hashlib.sha256((root/(n+".md")).read_bytes()).hexdigest() for n in names})

def contract(training_rows=32,development_rows=16,*,authored=False):
    return {"schema":SCHEMA,"scope":"AUTHORED" if authored else "ASSAY",
            "training_rows":training_rows,"development_rows":development_rows,"policy_sha256":policy_hash()}

def validate_contract(value):
    value=D.parse(D.raw(value));fields(value,("schema","scope","training_rows","development_rows","policy_sha256"))
    if value["schema"]!=SCHEMA or value["scope"] not in ("AUTHORED","ASSAY") or value["policy_sha256"]!=policy_hash():
        raise InputRefused("SELECTION_POLICY")
    a,b=value["training_rows"],value["development_rows"]
    if type(a) is not int or type(b) is not int or not 1<=a<=32 or not 1<=b<=16:
        raise InputRefused("SELECTION_COUNTS")
    if value["scope"]=="ASSAY" and (a,b)!=(32,16):raise InputRefused("SELECTION_COUNTS")
    return value

def trial(task,engine,row,*,rule=None):
    o=row["observation"];start=time.monotonic()
    try:
        p=engine.prepare(task);o["preparation"]=dict(engine.counters);row["stage"]="QUERY"
        proposed=None
        if rule is not None:
            row["stage"]="MATCH";proposed=apply_rule(rule,task,engine,p)
            row["application"]=proposed
        result=proposed["result"] if proposed is not None and proposed["terminal"]=="PROPOSED" else engine.complete(p)
        row["result"]=result;row["stage"]="VERIFY"
        if not verify_answer(task,result,work=o,counter="independent_answer_checks"):raise InputRefused("SELECTION_ANSWER_CERTIFICATE")
        row["terminal"]="COMPLETE";row["stage"]="COMPLETE"
    except BaseException as exc:
        row.update(terminal="CANNOT_CHECK",reason=type(exc).__name__+":"+str(exc));raise
    finally:
        observe(o,engine)
        prep=o.get("preparation")
        o["query_constraints"]=None if prep is None else engine.counters["constraints_checked"]-prep["constraints_checked"]
        o["wall_s"]=time.monotonic()-start

def acquire_selected(training,development,selection_contract,*,work=None,observation=None,sources_sha256=None):
    work={} if work is None else work;r={} if observation is None else observation
    start=time.monotonic();r.update(stage="INPUT",training=[],baseline=[],trials=[])
    try:
        policy=validate_contract(selection_contract)
        if (type(training) is not list or type(development) is not list or
            len(training)!=policy["training_rows"] or len(development)!=policy["development_rows"]):
            raise InputRefused("SELECTION_COUNTS")
        training=D.parse(D.raw(training));development=D.parse(D.raw(development))
        r.update(schema=SCHEMA,contract=policy,sources_sha256=D.hashed(D.sources(work)) if sources_sha256 is None else sources_sha256)
        pool=EnginePool();episodes=[]
        for value in training:
            r["stage"]="TRAINING";task=validate_task(value);o={}
            row={"task":task,"observation":o,"terminal":"ATTEMPTED"};r["training"].append(row)
            trial(task,pool.get(task,o),row);episodes.append({"task":task,"result":row["result"]})
        r["stage"]="MINING";D.bump(work,"acquisition_calls");r["acquisition"]=acquire(episodes)
        if policy["scope"]=="ASSAY" and any(len(x["rule"]["premises"])!=2 for x in r["acquisition"]["rules"]):
            raise InputRefused("ASSAY_FRAGMENT_BOUND")
        for value in development:
            r["stage"]="DEVELOPMENT_BASELINE";task=validate_task(value)
            row={"task":task,"observation":{"engine_cache_reused":False},"terminal":"ATTEMPTED"}
            r["baseline"].append(row);trial(task,RegionSolver(task["predicates"]),row)
        for item in r["acquisition"]["rules"]:
            for index,base in enumerate(r["baseline"]):
                r["stage"]="DEVELOPMENT_CANDIDATE";task=base["task"]
                row={"task":task,"rule_id":item["rule"]["rule_id"],"row":index,
                     "observation":{"engine_cache_reused":False},"terminal":"ATTEMPTED"}
                r["trials"].append(row);trial(task,RegionSolver(task["predicates"]),row,rule=item["rule"])
        from unary_method_selection_check import decisions
        r.update(decisions(r));r["stage"]="COMPLETE"
        r["work"]=dict(work);r["work"]["acquisition_wall_s"]=time.monotonic()-start
        r["receipt_sha256"]=D.hashed(r)
        return D.parse(D.raw(r))
    finally:work["outer_selection_wall_s"]=time.monotonic()-start

def validate_receipt(value,*,sources_sha256=None,work=None):
    from unary_method_selection_check import validate_receipt as check
    return check(value,sources_sha256=sources_sha256,work={} if work is None else work)

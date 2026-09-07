"""Fixed arm/mode adapter; no data-defined callbacks or task generator."""
import time
from pathlib import Path
from unary_contract import InputRefused,fields
import unary_method_outer as D

MODES=("acquire","solve","acquire_selected","batch","revise","status")
def run(arm,mode,value,*,observation=None):
    o={} if observation is None else observation
    if type(arm) is not str or arm not in ("ocm","conventional"):raise InputRefused("PROCESS_ARM")
    if mode not in MODES:raise InputRefused("PROCESS_MODE")
    keys={"acquire":("store","training"),"solve":("store","task","invoke"),
          "acquire_selected":("store","training","development","contract"),
          "batch":("store","tasks","invoke"),"revise":("store","role","state","method_id"),"status":("store",)}
    fields(value,keys[mode])
    if type(value["store"]) is not str:raise InputRefused("STORE_PATH")
    path=Path(value["store"]);create=mode in ("acquire","acquire_selected")
    if not path.is_absolute() or path.is_symlink():raise InputRefused("STORE_PATH")
    if create and path.exists():raise InputRefused("CREATE_ONLY_STORE")
    if arm=="conventional":
        if mode=="acquire":raise InputRefused("PARENT_REQUIRES_SELECTION")
        from unary_parent_store import ParentStore
        from unary_parent_runtime import ParentRuntime
        store=ParentStore(path,create=create);runtime=lambda:ParentRuntime(store)
        persist=store.persist;callbacks=0;rt=None
    else:
        from ocm.runtime.ocm_runtime import OCMRuntime
        from unary_method_store import MethodStore
        from unary_method_runtime import MethodRuntime
        if not create and not (path/"unary-method-journal/ledger.jsonl").is_file():
            raise InputRefused("MISSING_ISSUER_JOURNAL")
        rt=OCMRuntime(path);store=MethodStore(rt,create=create);runtime=lambda:MethodRuntime(store)
        persist=rt.persist;callbacks=len(rt._host_operators)
    prior=len(store.uses);o.update(stage="RESTORED",prior_uses=prior,callbacks_on_restore=callbacks)
    if mode=="acquire":
        o["stage"]="ACQUISITION";outcome=store.acquire(value["training"])
    elif mode=="acquire_selected":
        o["stage"]="ACQUISITION";o["selection_attempt"]={}
        outcome=store.acquire_selected(value["training"],value["development"],value["contract"],observation=o["selection_attempt"])
    elif mode in ("solve","batch"):
        tasks=[value["task"]] if mode=="solve" else value["tasks"]
        if type(tasks) is not list or not 1<=len(tasks)<=128:raise InputRefused("BATCH_BOUND")
        b=runtime();o["stage"]="SOLVING";o["rows"]=[];outcome=None
        for i,task in enumerate(tasks):
            item={"row":i,"terminal":"ATTEMPTED"};o["rows"].append(item)
            try:
                result=b.solve(task,invoke=value["invoke"]);item.update(terminal=result["terminal"],result=result)
            except BaseException as exc:
                item.update(terminal="CANNOT_CHECK",reason=type(exc).__name__+":"+str(exc))
                o["unreached_rows"]=list(range(i+1,len(tasks)))
                try:
                    item["pre_journal_observation"]=D.parse(D.raw(b.last_observation))
                    item["store_work"]=dict(store.work)
                except Exception as secondary:item["observation_unavailable"]=type(secondary).__name__+":"+str(secondary)
                raise
            if result["terminal"]!="CHECKED":
                o["unreached_rows"]=list(range(i+1,len(tasks)));break
        outcome=o["rows"][0]["result"] if mode=="solve" else {"terminal":"CHECKED" if len(o["rows"])==len(tasks) and all(r["terminal"]=="CHECKED" for r in o["rows"]) else "CANNOT_CHECK","rows":o["rows"],"unreached_rows":o.get("unreached_rows",[])}
    elif mode=="revise":
        role,state,mid=value["role"],value["state"],value["method_id"]
        if arm=="conventional":outcome=store.revise(role,state,mid=mid)
        else:
            store._check_environment()
            if role not in ("semantics","schema_environment","answer_environment","discovery","utility") or state not in ("LIVE","REVOKED"):
                raise InputRefused("OCM_REVISION")
            eid=store.environment[role] if role in store.environment else store.read(mid)["envelope"][role]
            (rt.reinstate if state=="LIVE" else rt.revoke)([eid])
            outcome={"record":eid,"role":role,"state":state}
    else:
        outcome={"method_ids":store.method_ids,"prior_uses":prior,"items":[store.read(mid) for mid in store.method_ids]}
    begin=time.monotonic();persist();elapsed=time.monotonic()-begin;o["stage"]="PERSISTED"
    return {"outcome":outcome,"callbacks_on_restore":callbacks,"prior_uses":prior,
            "work":dict(store.work),"persist_wall_s":elapsed,
            "core_head":None if rt is None else rt.events[-1].event_hash,"issuer_head":store.head}

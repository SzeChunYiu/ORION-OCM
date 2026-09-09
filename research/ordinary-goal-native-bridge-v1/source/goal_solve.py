"""Finite ordinary derivation -> full normal proof; native validity remains pending."""
import json,time,math
import finite_search as FS
from bank_policy import bank_from
from syntax_adapter import SyntaxPool
from syntax_engine import SyntaxUnknown
from screen_work import Work
import typed_context as TC
from goal_library import encoded,identity,require
def validate_task(task):
    require(type(task) is dict and set(task)=={"schema","query","premises","context","limits"},"goal-only task fields")
    require(task["schema"]=="ordinary.goal-task.v1","task schema")
    ps=TC.validate(task["context"]);lim=task["limits"]
    require(set(lim)=={"max_decisions","max_instances","max_token_states","soft_wall_s"},"limit fields")
    require(all(type(lim[k]) is int and lim[k]>0 for k in ("max_decisions","max_instances","max_token_states"))
            and type(lim["soft_wall_s"]) in (int,float) and math.isfinite(lim["soft_wall_s"]) and lim["soft_wall_s"]>0,"positive finite limits")
    require(type(task["premises"]) is list,"premise vector")
    for s in [task["query"]]+task["premises"]:
        require(type(s) is list and 1<len(s)<=513 and s[0]=="|-" and
                all(type(t) is str and t and not any(c.isspace() for c in t) for t in s),"logical token vector")
    return ps
def action_scope(contracts):
    supported=[];unsupported=[]
    for r in contracts:
        if r["statement"][0]!="|-":continue
        reason=None
        if r["dv"]:reason="DV outside qualified action interface"
        elif any(h["statement"][0] not in {"class","wff"} for h in r["floating"]):reason="floating type outside emitter interface"
        elif any(h["statement"][0]!="|-" for h in r["essential"]):reason="nonlogical essential"
        if reason:unsupported.append({"label":r["label"],"reason":reason})
        else:supported.append(r)
    return supported,unsupported
def solve(task,library,mode):
    started=time.perf_counter();result={"terminal":"UNKNOWN","native_acceptance":False,"generated_proof":None}
    work=None;pool=None;library_before=library.costs
    try:
        task=json.loads(encoded(task));ps=validate_task(task)
        require(mode in {"enabled","resident-disabled","restored"},"arm mode")
        result.update(task=identity(task),library=library.pin,mode=mode)
        lim=task["limits"];work=Work(lim["max_token_states"],lim["soft_wall_s"],started)
        contracts=library.contracts;cohort=library.cohort_labels
        physical={p["variable"]:p["id"] for p in ps};inverse={v:k for k,v in physical.items()}
        require(not set(TC.IDS)&set(physical),"physical/canonical variable collision")
        resident=[];hint_bindings=[];indexed=library.rows
        for r in contracts:
            if r["label"] not in cohort:continue
            formal=TC.from_source(indexed[r["label"]])["parameters"]
            require([p["type"] for p in formal]==[p["type"] for p in ps],"resident cohort typed frame")
            renaming={p["variable"]:q["variable"] for p,q in zip(formal,ps)}
            normalized=TC.rename(r["statement"],renaming)
            resident.append({**r,"statement":normalized})
            hint_bindings.append({"label":r["label"],"original_contract":identity(r),
                                  "hint_only_renaming":renaming,"normalized_statement":normalized})
        result["resident_hint_bindings"]=hint_bindings
        bank=bank_from(task["query"],resident,[s[1:] for s in task["premises"]])
        for r in bank["wff"]:r["tokens"]=TC.rename(r["tokens"],physical)
        search_task={"query":TC.rename(task["query"],physical),
                     "premises":[TC.rename(s,physical) for s in task["premises"]]}
        result.update(bank=bank,bank_identity=identity(bank),resident_cohort=cohort)
        pool=SyntaxPool(contracts,work);ctx=pool.context([{"id":p["id"],"type":p["type"]} for p in ps])
        for row in bank["wff"]:ctx.proof("wff",row["tokens"])
        parent,unsupported=action_scope(contracts)
        result.update(parent_contract_count=len(contracts),unsupported_actions=unsupported,
                      parent_scope_complete=not unsupported)
        tick=time.perf_counter()
        actions=FS.compile_parent(parent,bank,work,lim["max_instances"],ctx.checker)
        work.add("grounding_wall_s",time.perf_counter()-tick);work.checkpoint()
        # Resident action grounding and syntax materialization are identical in every arm.
        result.update(grounded_actions_identity=identity(actions),grounded_actions=len(actions))
        syntax={"class":[],"wff":[]};seen=set();tick=time.perf_counter();bylabel={r["label"]:r for r in contracts}
        for a in actions:
            for h in bylabel[a["label"]]["floating"]:
                kind,var=h["statement"];tokens=a["substitution"][var];key=(kind,tuple(tokens))
                if key not in seen:
                    proof=ctx.proof(kind,tokens);syntax[kind].append({"tokens":tokens,"proof":proof});seen.add(key)
        work.add("syntax_materialization_wall_s",time.perf_counter()-tick)
        result["emission_syntax_identity"]=identity(syntax)
        eligible=[a for a in actions if mode!="resident-disabled" or a["label"] not in cohort]
        result["eligible_actions_identity"]=identity(eligible);result["eligible_actions"]=len(eligible)
        result["eligible_cohort_labels"]=cohort if mode!="resident-disabled" else []
        tick=time.perf_counter();found=FS.search(eligible,bank,search_task,work,lim["max_decisions"])
        work.add("search_wall_s",time.perf_counter()-tick);work.checkpoint();result["search"]=found
        if found["terminal"]!="PROVED":
            result["terminal"]="NO_PROOF_IN_REGISTERED_FINITE_BANK" if not unsupported else "UNKNOWN_PARENT_SCOPE"
            return result
        tick=time.perf_counter()
        proof=FS.emit(found["derivation"],contracts,syntax,work,("cut-f0","cut-f1","cut-f2"))
        mapping={"cut-f"+str(i):p["floating_label"] for i,p in enumerate(ps)}
        proof=[mapping.get(label,label) for label in proof]
        require(set(proof)<=set(library.rows)|{"search-hyp-"+str(i) for i in range(len(task["premises"]))},
                "foreign generated proof label")
        selected=[x for x in proof if x in cohort]
        require(mode!="resident-disabled" or not selected,"disabled cohort consumed")
        result.update(terminal="GENERATED_PROOF_PENDING_NATIVE",generated_proof=proof,
                      selected_cohort_labels=selected,decision_count=found["decision_count"],
                      generated_target=TC.rename(found["derivation"]["output"],inverse),
                      generated_premises=task["premises"])
        require(result["generated_target"]==task["query"],"generated target mismatch")
        work.add("proof_emission_wall_s",time.perf_counter()-tick);work.checkpoint()
    except (ValueError,KeyError,TypeError,IndexError,RecursionError,SyntaxUnknown) as exc:
        result.update(terminal="UNKNOWN",error={"type":type(exc).__name__,"reason":str(exc)},generated_proof=None)
    finally:
        result["library_costs"]={"before":library_before,"after":library.costs,
                                 "delta":{k:v-library_before[k] for k,v in library.costs.items()}}
        result.update(work=work.snapshot() if work else None,syntax=pool.report() if pool else [],
                      measured_solver_wall_s=time.perf_counter()-started)
    return result

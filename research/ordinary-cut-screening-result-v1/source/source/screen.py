"""Complete P1 traversal with conservative UNKNOWN and separate proof-ready aliases."""
import matcher as A
from syntax_engine import SyntaxUnknown
CAUGHT=(SyntaxUnknown,ValueError,KeyError,TypeError,IndexError,RecursionError,MemoryError)
def screen(body,pool,work):
    answers=[];unknown=[];visited=0;grammar_complete=False
    def failure(stage,exc,label=None):
        unknown.append({"stage":stage,"label":label,"reason":type(exc).__name__+": "+str(exc)})
    try:
        work.checkpoint()
        context=pool.context(body["parameters"])
        grammar_complete=not context.engine.compiled["unsupported"]
    except CAUGHT as exc:
        failure("construction",exc);context=None
    if context is not None:
        try:
            if type(body["premises"]) is not list:raise ValueError("premise vector")
            A.ground_guard(body["query"],body["premises"],context.checker)
        except CAUGHT as exc:
            failure("ground_guard",exc);context=None
    if context is not None:
        if not grammar_complete:
            unknown.append({"stage":"grammar","reason":"Unsupported syntax contracts",
                            "contracts":context.engine.compiled["unsupported"]})
        for i,p in enumerate(body["premises"]):
            if p==body["query"]:
                answers.append({"kind":"hypothesis_return","premise_indices":[i],"proof":["cut-h"+str(i)]})
        for row in pool.contracts:
            try:
                work.checkpoint()
                A.count(work,"P1_assertions_visited");visited+=1
                if any(h["statement"][0] not in ("wff","class","setvar") for h in row["floating"]):
                    raise ValueError("unsupported floating type")
                witnesses=A.applications(row,body["query"],body["premises"],work,context.checker)
            except CAUGHT as exc:
                failure("rule_match",exc,row.get("label"))
                if work.exhausted:break
                continue
            for witness in witnesses:
                try:
                    proof=[]
                    for h in row["floating"]:
                        A.count(work,"syntax_proof_requests")
                        proof+=context.proof(h["statement"][0],witness["substitution"][h["statement"][1]])
                    proof+=["cut-h"+str(i) for i in witness["premise_indices"]]+[row["label"]]
                    answers.append({"kind":"one_logical_assertion",**witness,"proof":proof})
                    work.add("alias_proof_labels",len(proof))
                except CAUGHT as exc:
                    failure("syntax_proof",exc,row.get("label"))
                    if work.exhausted:break
            if work.exhausted:break
    complete=grammar_complete and not unknown and visited==len(pool.contracts)
    return {"status":"ALIAS_FOUND_PROOF_READY" if answers else
                    "SCREENED_NEGATIVE_IN_DOMAIN" if complete else "UNKNOWN",
            "coverage_complete":complete,"grammar_coverage_complete":grammar_complete,
            "P1_total":len(pool.contracts),"P1_visited":visited,"reasons":unknown,"aliases":answers,
            "native_acceptance":False,"new_native_admissions":0,
            "scope":"Exact retained P1; same one-logical-assertion matcher and premise reuse/omission/order. Syntax witnesses replayed structurally; no native theorem admission."}

"""Finite ordinary-parent instance construction and deterministic bounded search."""
import collections
import hashlib
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location("_common",Path(__file__).with_name("common.py"))
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
M=C.load("native_match");T=C.load("typed_terms")
def count(work,key,n=1):work[key]=work.get(key,0)+n
def replace(tokens,mapping):return [v for t in tokens for v in mapping.get(t,[t])]
def compile_parent(parent,bank,work,limit=200000):
    formulas=[["|-"]+r["tokens"] for r in bank["wff"]]
    lookup={tuple(t):i for i,t in enumerate(formulas)}
    maxima={}
    for f in formulas:
        for t,n in collections.Counter(f).items():maxima[t]=max(n,maxima.get(t,0))
    actions=[]
    for row in parent:
        count(work,"parent_contracts_scanned")
        if row["statement"][0]!="|-":continue
        variables={h["statement"][1] for h in row["floating"]}
        patterns=[row["statement"]]+[h["statement"] for h in row["essential"]]
        if any(any(n>maxima.get(t,0) for t,n in collections.Counter(x for x in p if x not in variables).items()) for p in patterns):
            count(work,"bank_literal_exclusions");continue
        for qi,query in enumerate(formulas):
            for mapping in M.match(row["statement"],query,row["floating"],{},work):
                states=[(mapping,[])]
                for h in row["essential"]:
                    successors=[]
                    for prior,slots in states:
                        if {t for t in h["statement"] if t in variables}<=set(prior):
                            pi=lookup.get(tuple(replace(h["statement"],prior)))
                            count(work,"ground_hypothesis_lookups")
                            if pi is not None:successors.append((prior,slots+[pi]))
                        else:
                            for pi,premise in enumerate(formulas):
                                count(work,"ground_hypothesis_matches")
                                for nxt in M.match(h["statement"],premise,row["floating"],prior,work):
                                    successors.append((nxt,slots+[pi]))
                        if len(successors)>limit:raise ValueError("INSTANCE_BOUND: partial instantiations")
                    states=successors
                for mapping,slots in states:
                    if set(mapping)!=variables:raise ValueError("unbound mandatory variable")
                    count(work,"dv_checks")
                    if not M.dv_valid(row,mapping):continue
                    action={"kind":"primitive","label":row["label"],"substitution":mapping,
                            "query":qi,"premises":slots}
                    action["id"]=hashlib.sha256(C.canonical(action)).hexdigest()
                    actions.append(action);count(work,"primitive_instances")
                    if len(actions)>limit:raise ValueError("INSTANCE_BOUND: complete instantiations")
    return actions

def order(action,formulas):
    name=("native:"+action["label"]) if action["kind"]=="primitive" else ("macro:"+action["method_id"])
    return (tuple(formulas[action["query"]]),name,C.canonical(action["substitution"]))
def search(actions,bank,task,work,max_decisions=8):
    formulas=[["|-"]+r["tokens"] for r in bank["wff"]];lookup={tuple(t):i for i,t in enumerate(formulas)}
    if tuple(task["query"]) not in lookup or any(tuple(p) not in lookup for p in task["premises"]):
        raise ValueError("BANK_INCOMPLETE: task")
    target=lookup[tuple(task["query"])];facts={}
    for i,p in enumerate(task["premises"]):
        facts.setdefault(lookup[tuple(p)],{"kind":"premise","slot":i,"decision_count":0,"output":p})
    if target in facts:return {"terminal":"PROVED","decision_count":0,"derivation":facts[target]}
    ordered=sorted(actions,key=lambda a:order(a,formulas))
    for layer in range(1,max_decisions+1):
        count(work,"search_layers")
        for action in ordered:
            count(work,"action_attempts");count(work,action["kind"]+"_action_attempts")
            qi=action["query"]
            if qi in facts or any(p not in facts for p in action["premises"]):continue
            parents=[facts[p] for p in action["premises"]]
            cost=1+sum(p["decision_count"] for p in parents)
            if cost!=layer:continue
            derivation={"kind":"action","action":action,"parents":parents,
                        "decision_count":cost,"output":formulas[qi]}
            facts[qi]=derivation;count(work,"successful_relaxations")
            if qi==target:return {"terminal":"PROVED","decision_count":cost,"derivation":derivation}
    return {"terminal":"NO_PROOF_WITHIN_BOUND","max_decisions":max_decisions,"reached_facts":len(facts)}

def emit(derivation,parent,bank,work):
    contracts={r["label"]:r for r in parent}
    syntax={(k,tuple(r["tokens"])):r["proof"] for k in ("class","wff") for r in bank[k]}
    def visit(node):
        if node["kind"]=="premise":return ["search-hyp-"+str(node["slot"])]
        action=node["action"];parents=[visit(p) for p in node["parents"]]
        if action["kind"]=="primitive":
            row=contracts[action["label"]];proof=[]
            for h in row["floating"]:
                key=(h["statement"][0],tuple(action["substitution"][h["statement"][1]]))
                if key not in syntax:raise ValueError("BANK_INCOMPLETE: syntax")
                proof+=syntax[key];count(work,"construction_syntax_label_visits",len(syntax[key]))
            for p in parents:proof+=p
            proof.append(row["label"]);count(work,"construction_primitive_semantic_visits")
            return proof
        holes=action["holes"]
        if len(parents)!=len(holes):raise ValueError("macro hole population")
        proof=[]
        for label in action["template"]:
            if label in holes:proof+=parents[holes.index(label)]
            else:proof.append(label)
        count(work,"construction_macro_template_visits",len(action["template"]))
        return proof
    proof=visit(derivation)
    if len(proof)>4096:raise ValueError("PROOF_BOUND")
    # Count the final expanded stream, including repeated macro-hole splices.
    # Construction visits above intentionally count physical constructor work only.
    for label in proof:
        if label.startswith("search-hyp-"):
            count(work,"final_hypothesis_labels")
        elif label in ("cA","cB","cC"):
            count(work,"final_floating_labels")
        elif label in contracts:
            key="final_semantic_labels" if contracts[label]["statement"][0]=="|-" else "final_syntax_labels"
            count(work,key)
        else:raise ValueError("unclassified final proof label")
    count(work,"normal_proof_labels",len(proof))
    return proof

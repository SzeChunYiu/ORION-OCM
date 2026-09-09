"""Finite complete one-assertion matching to typed ground strings."""
import importlib.util
from pathlib import Path

spec=importlib.util.spec_from_file_location("_chunk_types",Path(__file__).with_name("typed_terms.py"))
T=importlib.util.module_from_spec(spec); spec.loader.exec_module(T)
def count(work,key,n=1):
    work[key]=work.get(key,0)+n
def match(pattern, ground, floating, initial, work, syntax_checker=None):
    variables={h["statement"][1]:h["statement"][0] for h in floating}
    results=[]; cache={}
    def walk(i,j,mapping):
        count(work,"token_states")
        if i==len(pattern):
            if j==len(ground): results.append(mapping)
            return
        token=pattern[i]
        if token not in variables:
            if j<len(ground) and token==ground[j]: walk(i+1,j+1,mapping)
        elif token in mapping:
            value=mapping[token]
            if ground[j:j+len(value)]==value: walk(i+1,j+len(value),mapping)
        else:
            for end in range(j+1,len(ground)+1):
                value=ground[j:end]; key=(variables[token],tuple(value))
                if key not in cache:
                    count(work,"type_checks")
                    try: (syntax_checker or T.syntax)(variables[token],value); cache[key]=True
                    except ValueError: cache[key]=False
                if cache[key]: walk(i+1,end,{**mapping,token:value})
    walk(0,0,dict(initial))
    return results
def dv_valid(row,mapping):
    # Authored scope has class variables A/B/C and no declared distinct pairs.
    for a,b in row["dv"]:
        av=set(mapping[a]) & set(T.ATOMS); bv=set(mapping[b]) & set(T.ATOMS)
        if av and bv: return False
    return True
def applications(row,query,premises,work):
    answers=[]
    for m in match(row["statement"],query,row["floating"],{},work):
        states=[(m,[])]
        for h in row["essential"]:
            successors=[]
            for prior,slots in states:
                for i,p in enumerate(premises):
                    count(work,"essential_matches")
                    for nxt in match(h["statement"],p,row["floating"],prior,work):
                        successors.append((nxt,slots+[i]))
            states=successors
        for mapping,slots in states:
            if set(mapping)!={h["statement"][1] for h in row["floating"]}:
                raise ValueError("mandatory variable missing from conclusion and hypotheses")
            count(work,"dv_checks")
            if dv_valid(row,mapping):
                answers.append({"label":row["label"],"substitution":mapping,"premise_indices":slots})
    return answers
def ground_guard(query,premises):
    for statement in [query]+premises:
        if type(statement) is not list or not statement or statement[0]!="|-" or any(type(t) is not str for t in statement):
            raise ValueError("UNSUPPORTED_GROUND_SYNTAX: token vector")
        try:T.syntax("wff",statement[1:])
        except ValueError as exc:raise ValueError("UNSUPPORTED_GROUND_SYNTAX: "+str(exc)) from exc
def one_step(contracts,query,premises,work):
    if type(premises) is not list:raise ValueError("UNSUPPORTED_GROUND_SYNTAX: premise vector")
    ground_guard(query,premises)
    if any(h["statement"][0] not in ("class","wff","setvar") for r in contracts for h in r["floating"]):
        raise ValueError("UNSUPPORTED_NATIVE_INVENTORY: floating type")
    result=[]
    for row in contracts:
        count(work,"assertions_visited")
        result+=applications(row,query,premises,work)
    return result

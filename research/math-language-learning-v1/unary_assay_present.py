"""Pure final presentations and candidate support variants; no use authentication."""
import hashlib,json
from unary_contract import InputRefused,validate_task
from unary_language import realize
from unary_rule_contract import count,encoded
from unary_assay_identity import used_names
from unary_assay_stream import NAMES,EPISODES,_index

def digest(task,work):
    task=validate_task(task);raw=encoded(task,work);count(work,"bytes_hashed",len(raw))
    count(work,"present_task_hashes");return hashlib.sha256(raw).hexdigest()

def final_pair(value,episode,slot,*,work):
    task=validate_task(value);_index(episode,EPISODES,"EPISODE");_index(slot,32,"SLOT")
    if task["predicates"]!=list(NAMES):raise InputRefused("FINAL_SLOT_NAMES")
    mapping={name:f"e{episode}f{slot}p{i}" for i,name in enumerate(NAMES)}
    def walk(e):
        count(work,"rename_expression_nodes")
        return ["pred",mapping[e[1]]] if e[0]=="pred" else [e[0],*[walk(x) for x in e[1:]]]
    def statement(s):return {"kind":s["kind"],"left":walk(s["left"]),"right":walk(s["right"])}
    formal=validate_task({"schema":task["schema"],"predicates":sorted(mapping.values()),
                         "premises":[statement(s) for s in task["premises"]],"query":statement(task["query"])})
    count(work,"realizations");text=realize(formal);count(work,"realized_text_bytes",len(text.encode()))
    return {"row_id":f"e{episode}/final/{slot}","episode":episode,"slot":slot,
            "original_task_sha256":digest(task,work),"rename":mapping,
            "formal":formal,"text":text,"task_sha256":digest(formal,work)}

def presentation_rows(pairs,episode,*,work):
    _index(episode,EPISODES,"EPISODE")
    if type(pairs) is not list or not 1<=len(pairs)<=32:raise InputRefused("PRESENTATION_BOUND")
    rows=[]
    for slot,pair in enumerate(pairs):
        if (pair["episode"]!=episode or pair["slot"]!=slot or pair["row_id"]!=f"e{episode}/final/{slot}"
            or digest(pair["formal"],work)!=pair["task_sha256"]):raise InputRefused("PRESENTATION_BINDING")
        for presentation in (("ast","text") if (episode+slot)%2==0 else ("text","ast")):
            count(work,"presentation_rows")
            rows.append({"row_id":pair["row_id"],"presentation":presentation,
                         "observation_id":pair["row_id"]+"/"+presentation,"task_sha256":pair["task_sha256"],
                         "payload":pair["formal"] if presentation=="ast" else pair["text"]})
    return json.loads(encoded(rows,work))

def remove(value,index,*,work):
    task=validate_task(value);_index(index,len(task["premises"]),"REMOVAL_INDEX")
    positions=[None if i==index else i-(i>index) for i in range(len(task["premises"]))]
    changed={**task,"premises":[s for i,s in enumerate(task["premises"]) if i!=index]}
    names,_=used_names(changed,work=work);changed["predicates"]=sorted(names);changed=validate_task(changed)
    count(work,"support_removals");count(work,"premise_positions_mapped",len(positions))
    return {"terminal":"READY","task":changed,"task_sha256":digest(changed,work),
            "removed_original_index":index,"original_to_derived":positions}

def support_variants(value,*,used_cover,work):
    """None is caller-established checked no-use; missing authority is not an input here."""
    task=validate_task(value);n=len(task["premises"])
    if used_cover is not None and (type(used_cover) is not list or not used_cover or
            any(type(i) is not int or not 0<=i<n for i in used_cover) or used_cover!=sorted(set(used_cover))):
        raise InputRefused("SUPPORT_COVER")
    ordinary=next((i for i,s in enumerate(task["premises"]) if s["kind"] in ("every","no")),None)
    out=[]
    for kind,index in (("ordinary",ordinary),("used",None if used_cover is None else min(used_cover))):
        variant={"terminal":"NOT_APPLICABLE","task":None,"task_sha256":None,
                 "removed_original_index":None,"original_to_derived":None} if index is None else remove(task,index,work=work)
        out.append({"kind":kind+"_remove",**variant})
        out.append({"kind":kind+"_restore","terminal":"READY","task":task,"task_sha256":digest(task,work),
                    "removed_original_index":None,"original_to_derived":list(range(n))})
        count(work,"support_variant_slots",2)
    return json.loads(encoded(out,work))

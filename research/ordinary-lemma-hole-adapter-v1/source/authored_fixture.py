"""Authored transport fixtures; the legacy marker is not actual native acceptance."""
from copy import deepcopy
from structural_fixture import trace_from_proof
from hole_match import identity
import typed_context as TC

def substitute(ts,m):return [x for t in ts for x in m.get(t,[t])]
def fixture(repeated=False,inconsistent=False,missing=False,root_kind="$p"):
    kind="wff";names=("ph","ps","ch");labels=("wph","wps","wch")
    floats=[{"label":f,"statement":[kind,v]} for f,v in zip(labels,names)]
    context={"schema":"native.typed-context.v1","dv":[],"parameters":[
        {"id":key,"type":kind,"variable":v,"floating_label":f} for key,v,f in zip(TC.IDS,names,labels)]}
    active_floats=[{"label":f,"statement":[kind,v]} for f,v in zip(("fa","fb","fc"),("a","b","c"))]
    args=[["fa","fb","syn"],["fa","fb","syn"] if repeated else ["fc"],["fc"] if repeated else ["fa"]]
    images=[["(","a","op","b",")"],["(","a","op","b",")"] if repeated else ["c"],["c"] if repeated else ["a"]]
    form=lambda head,vs:["|-",head]+[x for v in vs for x in v]
    nf=2 if missing else 3
    rh=["|-","R"]+list(names[:nf]);sh=["|-","S","ph","ps"];th=["|-","T"]+list(names[:nf])
    ordinary={}
    def add(label,fs,es,out,k="$a"):
        ordinary[label]={"label":label,"kind":k,"floating":deepcopy(fs),"essential":[{"label":label+"-h"+str(i),"statement":list(h)} for i,h in enumerate(es)],
                         "statement":list(out),"dv":[],"span":[1,2]}
    add("syn",floats[:2],[],["wff","(","ph","op","ps",")"])
    add("syntax-id",floats[:1],[],["wff","ph"],"$p")
    add("step1",floats[:nf],[rh],sh)
    add("step2",floats[:nf],[sh] if missing else [sh,rh],th,root_kind)
    add("argument",floats[:nf],[rh],rh,"$p")
    add("outer",floats[:nf],[th],th,"$p")
    add("join",floats[:nf],[th,th],th,"$p")
    pattern_rows={h["label"]:{"label":h["label"],"kind":"$f","statement":h["statement"],"span":[0,1]} for h in floats}
    pattern_rows.update({n:deepcopy(ordinary[n]) for n in ("step1","step2")})
    f_nodes=[{"kind":"float","output":["wff",v]} for v in TC.IDS[:nf]]
    canonical=lambda ts:substitute(ts,{v:[k] for v,k in zip(names,TC.IDS)})
    premises=[canonical(rh)]+([["|-","Q","V2"]] if missing else [])
    h=nf;a1=nf+1;a2=nf+2
    body={"schema":"native.typed-proper-chunk.v1","parameters":TC.parameters("wff"),"premises":premises,
      "query":canonical(th),"nodes":f_nodes+[{"kind":"hole","slot":0,"output":canonical(rh)},
      {"kind":"apply","label":"step1","inputs":list(range(nf))+[h],"output":canonical(sh),"substitution":{v:[k] for v,k in zip(names[:nf],TC.IDS)}},
      {"kind":"apply","label":"step2","inputs":list(range(nf))+[a1]+([] if missing else [h]),"output":canonical(th),"substitution":{v:[k] for v,k in zip(names[:nf],TC.IDS)}}],"root":a2}
    lemma={"label":"learned-cut","kind":"$p","floating":deepcopy(floats),
      "essential":[{"label":"lemma-h"+str(i),"statement":substitute(p,dict(zip(TC.IDS,[[v] for v in names])))} for i,p in enumerate(premises)],
      "statement":th,"dv":[]}
    target_rows={h["label"]:{"label":h["label"],"kind":"$f","statement":h["statement"],"span":[0,1]} for h in active_floats}
    m=dict(zip(names,images));first_m=deepcopy(m)
    first_args=deepcopy(args)
    if inconsistent:first_m["ch"]=["b"];first_args[2]=["fb"]
    essentials=[{"label":"ht","statement":substitute(rh,m)}]
    if inconsistent:essentials.append({"label":"ht-other","statement":substitute(rh,first_m)})
    if missing:essentials.append({"label":"unused","statement":["|-","Q","a"]})
    target_rows.update({h["label"]:{"label":h["label"],"kind":"$e","statement":h["statement"],"span":[0,1]} for h in essentials})
    target_rows.update(deepcopy(ordinary))
    cat=lambda xs:[x for proof in xs for x in proof]
    # Explicit proof skeleton: step2(floats, step1(floats, argument), argument).
    hproof=cat(args[:nf])+["ht","argument"]
    hproof_first=cat(first_args[:nf])+["ht-other" if inconsistent else "ht","argument"]
    candidate=cat(args[:nf])+cat(first_args[:nf])+hproof_first+["step1"]+([] if missing else hproof)+["step2"]
    proof=cat(args[:nf])+candidate+["outer"]
    source={"label":"authored-target","kind":"$p","floating":active_floats,"essential":essentials,
            "statement":substitute(th,m),"dv":[],"active_dv":[],"span":[100,101]}
    target_rows={k:v for k,v in target_rows.items() if k in proof}
    trace=trace_from_proof(source,target_rows,proof)
    target=len(trace["nodes"])-2
    return {"body":body,"pattern":pattern_rows,"lemma":lemma,"trace":trace,"target_contracts":target_rows,
            "parameter_context":context,"target":target,"args":args,"candidate_proof":candidate,"ordinary":ordinary,
            "all_target_floats":active_floats,"source":source,"proof":proof}

def context(f):
    values={"body":f["body"],"pattern_contracts":f["pattern"],"lemma":f["lemma"],
            "target_trace":f["trace"],"target_contracts":f["target_contracts"],"parameter_context":f["parameter_context"]}
    return {"schema":"ordinary.hole-context.v1","pins":{k:identity(v) for k,v in values.items()},
            "parameter_context":deepcopy(f["parameter_context"]),
            "library_identity":identity({"authored":"library"}),"native_authority_identity":identity({"authored":"no native authority"})}

def shared_fixture():
    f=fixture();prefix=sum(f["args"],[]);candidate=f["candidate_proof"]
    rows=deepcopy(f["target_contracts"]);rows["join"]=deepcopy(f["ordinary"]["join"]);rows.pop("outer")
    full=prefix+candidate+candidate+["join"]
    tr=trace_from_proof(f["source"],rows,full)
    start=len(prefix)+len(candidate);end=start+len(candidate);producer=start-1
    mapping={i:(i if i<start else start if i<end else i-(end-start)+1) for i in range(len(tr["nodes"]))}
    kept=[]
    for i,n in enumerate(tr["nodes"]):
        if start<=i<end:continue
        q=deepcopy(n);q["id"]=mapping[i];q["inputs"]=[mapping[j] for j in n["inputs"]]
        for o in q.get("obligations",[]):o["from"]=mapping[o["from"]]
        kept.append(q)
    ref={"id":start,"kind":"saved_reference","inputs":[],"slot":0,"saved_node":producer,"output":deepcopy(tr["nodes"][producer]["output"])}
    kept.insert(start,ref);events=[]
    for n in kept:
        events.append({"kind":"step","node":n["id"]})
        if n["id"]==producer:events.append({"kind":"save","slot":0,"node":producer})
    tr.update(nodes=kept,events=events,root=len(kept)-1)
    f.update(trace=tr,target_contracts=rows,target=producer)
    return f

def double_shared(f):
    """Authored repeated DAG, preserving stack events; no compressed-proof parser."""
    tr=f["trace"];offset=5;head=deepcopy(tr["nodes"][:offset]);old=deepcopy(tr["nodes"])
    for n in old:
        n["id"]+=offset;n["inputs"]=[i+offset for i in n["inputs"]]
        if n["kind"]=="saved_reference":n["saved_node"]+=offset
        for o in n.get("obligations",[]):o["from"]+=offset
    events=[{"kind":"step","node":n["id"]} for n in head]
    for e in tr["events"]:
        q=deepcopy(e);q["node"]+=offset;events.append(q)
    slot=1+max((e["slot"] for e in tr["events"] if e["kind"]=="save"),default=-1)
    producer=offset+tr["root"];ref_id=offset+len(old)
    ref={"id":ref_id,"kind":"saved_reference","inputs":[],"slot":slot,"saved_node":producer,"output":deepcopy(tr["source"]["statement"])}
    join=deepcopy(tr["nodes"][-1]);assert join["label"]=="join"
    join.update(id=ref_id+1,inputs=[2,3,4,producer,ref_id])
    for o,j in zip(join["obligations"],join["inputs"]):o["from"]=j
    events.extend([{"kind":"save","slot":slot,"node":producer},{"kind":"step","node":ref_id},{"kind":"step","node":ref_id+1}])
    tr.update(nodes=head+old+[ref,join],events=events,root=ref_id+1)
    f["target"]+=offset
    return f

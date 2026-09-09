"""Exact current wrapper/trace/request bindings; no native verifier invocation."""
import json
import hashlib
import trace_source as S
import life_native as N
from hole_match import identity, require

def raw_identity(raw):
    return {"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}

def verify_result(result,claim,prefix_raw,database_raw,authority,sources,prefix_path,archive):
    require(result["terminal"]=="NATIVE_VERIFIED" and result["native_calls"]==1
            and result["error"] is None,"current native success required")
    require(result["claims_sha256"]==identity([claim])["sha256"],"issued claims digest")
    require(result["sources"]==sources,"current native sources")
    require(result["closed_prefix"]=={"path":str(prefix_path),**raw_identity(prefix_raw)}
            and raw_identity(prefix_raw)==authority["prefix"],"current full prefix")
    suffix=N.serialize([claim])
    require(result["suffix"]==raw_identity(suffix),"exact issued suffix")
    require(database_raw==prefix_raw+b"\n"+suffix,"exact native database")
    require(result["database"]=={"path":str(archive/"database.mm"),**raw_identity(database_raw)},"database binding")
    prefix,_=S.index(prefix_raw);rows,_=S.index(database_raw)
    prefix_proofs=[k for k,v in prefix.items() if v["kind"]=="$p"]
    trusted=[k for k,v in rows.items() if v["kind"]=="$a"]
    require(len(prefix_proofs)==authority["prefix_proof_count"],"full prefix proof count")
    require(len(trusted)==authority["trusted_assertion_count"]
            and identity(trusted)["sha256"]==authority["trusted_assertions_sha256"],"exact trust inventory")
    require(result["trusted_assertions"]==trusted and result["verified_labels"]==prefix_proofs+[claim["label"]],
            "full native verified population/order")
    require(result["selected"]==[claim["label"]] and set(result["traces"])=={claim["label"]},"selected trace")
    require(set(rows)-set(prefix)=={claim["label"],*claim["holes"]},"issued label population")
    trace=result["traces"][claim["label"]];source=rows[claim["label"]]
    wanted={"label":claim["label"],"kind":"$p","statement":claim["query"],"dv":[],
      "floating":[{"label":p["floating_label"],"statement":[p["type"],p["variable"]]} for p in claim["parameters"]],
      "essential":[{"label":h,"statement":s} for h,s in zip(claim["holes"],claim["premises"])]}
    require(S.contract(source)==wanted and source["proof"]==claim["proof"]
            and source["active_dv"]==[],"exact issued source/context")
    require(trace["label"]==claim["label"] and trace["terminal"]=="NATIVE_VERIFIED"
            and trace["source"]==source,"current indexed trace source")
    require(trace["external_logical_hypotheses"]==wanted["essential"],"trace ordered essentials")
    nodes=trace["nodes"]
    require(type(nodes) is list and 1<=len(nodes)<=256,"trace node scope")
    used={n["label"] for n in nodes if "label" in n}
    expected={k:{**S.contract(rows[k]),"span":rows[k]["span"]} for k in used}
    require(result["contracts"]==expected,"complete current used contracts")
    for k,row in expected.items():
        require(row["span"][1]<=source["span"][0],"used source-index span")
        if row["kind"] in {"$f","$e"}:
            frame=source["floating"] if row["kind"]=="$f" else source["essential"]
            require({"label":k,"statement":row["statement"]} in frame,"scoped mandatory hypothesis")
        else:
            require(k in prefix and row["kind"] in {"$a","$p"} and row["dv"]==[],"ordinary prefix/DV scope")
    return trace,expected,prefix

def adapter_context(definition,result,trace,used,prefix,authority):
    lemma=definition["lemma"];label=lemma["label"]
    require(label in prefix and S.contract(prefix[label])==lemma,"current native lemma contract")
    pattern=definition["pattern_contracts"]
    for k,row in pattern.items():
        require(k in prefix and row=={**S.contract(prefix[k]),"span":prefix[k]["span"]},"current recipe contract")
    # Never trim the complete native used map to satisfy the adapter's collision rule.
    require(label not in used and label not in pattern,"lemma already used")
    values={"body":definition["body"],"pattern_contracts":pattern,"lemma":lemma,
            "target_trace":trace,"target_contracts":used,"parameter_context":definition["parameter_context"]}
    return {"schema":"ordinary.hole-context.v1","pins":{k:identity(v) for k,v in values.items()},
            "parameter_context":definition["parameter_context"],"library_identity":authority["prefix"],
            "native_authority_identity":identity(result)}

def check_proposal(definition,proposal):
    require(proposal["status"]=="REPLACEMENT_PROPOSAL" and proposal["native_acceptance"] is False,"proposal only")
    source=definition["source_claim"];issued=definition["replacement_claim"]
    require(not {source["label"],issued["label"]}.intersection(proposal["proof"]),"target shortcut")
    require(proposal["target"]==issued["query"],"issued replacement target")
    expected=[{"label":h,"statement":s} for h,s in zip(issued["holes"],issued["premises"])]
    require(proposal["hypotheses"]==expected,"issued replacement ordered holes")
    require(proposal["proof"]==issued["proof"] and len(proposal["proof"])<=4096,"exact issued normal proof")
    require(proposal["proof"].count(definition["lemma"]["label"])==1
            and proposal["replacement_applications"]==1,"one ordinary lemma occurrence")
    require(proposal["occurrence_path"]==definition["occurrence_path"],"issued occurrence")

def negative_at_issued(result,claim,prefix_labels):
    """A negative counts only at the exact issued claim after its full prefix."""
    return (result.get("terminal")=="NATIVE_REJECTED" and result.get("native_calls")==1
       and result.get("error",{}).get("stage")=="native_check"
       and result.get("error",{}).get("pending")==claim["label"]
       and result.get("verified_labels")==prefix_labels)

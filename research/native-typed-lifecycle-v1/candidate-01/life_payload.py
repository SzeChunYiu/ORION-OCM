"""Post-exit projection and strict serving data; no teaching proof reads in B."""
import copy
import life_common as C

KEYS={"id","body","context","trace","contracts","alias","discovery_id","admission"}
OLD_CLASS_ID="5c8ff07719c450616a56ebe26ab8983473c4ad1d95f208df330d4de3c2270a06"


def validate(payload,engine):
    C.require(type(payload) is dict and set(payload)==
              {"schema","witnesses","eligible_method_ids","alias_witness_ids","origin","class_regression"},
              "PROJECTION_SCHEMA")
    C.require(payload["schema"]=="native.typed-serving.v1","PROJECTION_VERSION")
    C.require(type(payload["origin"]) is dict and set(payload["origin"])==
              {"state","process","producer_result","discovery","admission","source_freeze"},"ORIGIN_SCHEMA")
    eligible=[];aliases=[]
    for key,row in sorted(payload["witnesses"].items()):
        C.require(set(row)==KEYS and row["id"]==key==C.digest(row["body"]),"WITNESS_ID")
        C.require(set(row["trace"])=={"terminal","source","label","nodes","root","events",
                  "external_logical_hypotheses"},"TRACE_SCHEMA")
        C.require(set(row["trace"]["source"])=={"active_dv","active_variables","dv","essential","floating",
                  "kind","label","proof","proof_raw","raw","span","statement","statement_raw"},"SOURCE_SCHEMA")
        context=row["context"];params=engine["typed_context"].validate(context)
        C.require(engine["typed_context"].from_source(row["trace"]["source"],
                  [r["variable"] for r in params])==context,"WITNESS_CONTEXT")
        C.require(row["alias"]["status"] in ("ALIAS","NO_ALIAS_IN_REGISTERED_DOMAIN"),"UNKNOWN_WITNESS")
        C.require(set(row["alias"])=={"status","eligible","aliases"} and
                  bool(row["alias"]["aliases"])==(row["alias"]["status"]=="ALIAS"),"ALIAS_SCHEMA")
        expected=row["alias"]["status"]=="NO_ALIAS_IN_REGISTERED_DOMAIN"
        C.require(row["alias"]["eligible"] is expected,"ALIAS_ELIGIBILITY")
        (eligible if expected else aliases).append(key)
        C.require(type(row["discovery_id"]) is str and len(row["discovery_id"])==64,"DISCOVERY_ID")
        C.require(row["admission"]==payload["origin"]["admission"],"ADMISSION_ID")
        used={n["label"] for n in row["trace"]["nodes"] if "label" in n}
        C.require(set(row["contracts"])==used,"EXACT_USED_CONTRACTS")
    C.require(payload["eligible_method_ids"]==eligible and payload["alias_witness_ids"]==aliases,
              "ELIGIBILITY_SET")
    C.require(payload["class_regression"]==C.freeze()["inputs"]["inputs/CLASS-PAYLOAD.json"],
              "CLASS_REGRESSION_ID")
    return payload


def project(state_path,process_path,result_path,output,engine):
    process=C.read(process_path)
    C.require(process["exit_code"]==0 and process["reaped"] is True and
              process["sources_unchanged"] and process["request_unchanged"],"PRODUCER_NOT_CLEANLY_EXITED")
    result=C.checked(result_path,process["result"])
    C.require(result["terminal"]=="ADMITTED_AND_PERSISTED" and result["pid"]==process["pid"],
              "PRODUCER_NOT_PERSISTED")
    state=C.checked(state_path,result["state"])
    C.require(set(state)=={"schema","witnesses","eligible_method_ids","alias_witness_ids",
              "discovery","admission","source_freeze"} and
              state["schema"]=="native.typed-persisted.v1","STATE_SCHEMA")
    C.require(state["source_freeze"]==C.identity(C.HERE/"SOURCE-FREEZE.json"),"STATE_SOURCE")
    C.require(state["eligible_method_ids"]==result["eligible_method_ids"] and
              state["alias_witness_ids"]==result["alias_witness_ids"],"STATE_RESULT_ELIGIBILITY")
    projected={"schema":"native.typed-serving.v1","witnesses":copy.deepcopy(state["witnesses"]),
        "eligible_method_ids":state["eligible_method_ids"],"alias_witness_ids":state["alias_witness_ids"],
        "origin":{"state":C.identity(state_path),"process":C.identity(process_path),
                  "producer_result":C.identity(result_path),"discovery":state["discovery"],
                  "admission":state["admission"],"source_freeze":state["source_freeze"]},
        "class_regression":C.freeze()["inputs"]["inputs/CLASS-PAYLOAD.json"]}
    validate(projected,engine)
    return C.write(output,projected)


def class_witness(engine):
    old=C.checked(C.HERE/"inputs/CLASS-PAYLOAD.json",C.freeze()["inputs"]["inputs/CLASS-PAYLOAD.json"])
    C.require(set(old)=={"id","body","trace","contracts","admission"} and old["id"]==OLD_CLASS_ID,
              "CLASS_PAYLOAD_SCHEMA")
    context=engine["typed_context"].from_source(old["trace"]["source"],["A","B","C"])
    mapping=dict(zip(("A","B","C"),("V0","V1","V2")))
    body=copy.deepcopy(old["body"])
    C.require(body["schema"]=="native.proper-chunk.v1" and body["parameters"]==["A","B","C"],
              "CLASS_BODY_ORIGIN")
    body["schema"]="native.typed-proper-chunk.v1";body["parameters"]=engine["typed_context"].parameters("class")
    rename=engine["typed_context"].rename
    body["premises"]=[rename(p,mapping) for p in body["premises"]];body["query"]=rename(body["query"],mapping)
    for node in body["nodes"]:
        node["output"]=rename(node["output"],mapping)
        if "substitution" in node:
            node["substitution"]={k:rename(v,mapping) for k,v in node["substitution"].items()}
    return {"id":OLD_CLASS_ID,"body":body,"context":context,"trace":old["trace"],"contracts":old["contracts"]}

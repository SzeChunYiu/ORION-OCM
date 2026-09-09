"""All-candidate grouping; every completed stage survives a later hard refusal."""
import time
import life_common as C


def discover(training,engine,work,archive):
    archive.mkdir(exist_ok=False)
    groups={};occurrences=[];contexts=[];sequence=0;current=None;stage="imports"
    def checkpoint(status,error=None):
        nonlocal sequence
        C.write(archive/(str(sequence).zfill(3)+".json"),{"stage":stage,"status":status,
            "current":current,"contexts":contexts,"groups":[groups[k] for k in sorted(groups)],
            "occurrences":occurrences,"work":dict(work),"error":error,
            "partial_extraction":"Only returned candidates are available; a failed extractor call does not expose its partial local list."})
        sequence+=1
    started=time.perf_counter()
    try:
        contract=C.load("unary_contract","authority/unary_contract.py")
        verifier=C.load("unary_verify","authority/unary_verify.py")
        syntax=C.load("registered_bridge_syntax","authority/bridge_syntax.py")
        meaning=C.load("registered_bridge_meaning","authority/bridge_meaning.py")
        signatures=C.load("registered_signatures","authority/signatures.py")
        for label in training["selected"]:
            trace=training["traces"][label];source=trace["source"]
            current={"label":label};contexts.append(current)
            stage="translation";C.bump(work,"bridge_attempts");checkpoint("STARTED")
            bridge=syntax.translate(source["statement"],source["essential"],source["floating"],contract)
            current["bridge"]=bridge;checkpoint("RETURNED")
            stage="meaning";C.bump(work,"meaning_calls");checkpoint("STARTED")
            checked=meaning.check(source,bridge,contract,verifier);current["meaning"]=checked
            C.bump(work,"bridge_completed_worlds",checked["worlds"]);checkpoint("RETURNED")
            stage="meaning_gates"
            C.require(checked["terminal"]=="INTERPRETATION_EQUIVALENT","BRIDGE_REFUSED")
            gates=checked["gates"]
            C.require(gates["premises_satisfiable"] is not None and gates["query_not_tautological"] is not None
                      and gates["entailment_counterexample"] is None
                      and all(x is not None for x in gates["essentiality_counterexamples"]),"SOURCE_MEANING_GATES")
            C.bump(work,"bridge_accepted_worlds",checked["worlds"]);checkpoint("PASSED")
            stage="signature";C.bump(work,"signature_calls");checkpoint("STARTED")
            sign=signatures.canonical(checked["table"],bridge["task"]["predicates"])
            current["signatures"]=sign;joint=sign["joint_premise_query"]["sha256"]
            C.bump(work,"signature_world_permutations",6*255);checkpoint("RETURNED")
            used={n["label"] for n in trace["nodes"] if "label" in n}
            contracts={key:training["contracts"][key] for key in sorted(used)}
            stage="extraction";C.bump(work,"extractor_calls");checkpoint("STARTED")
            found=engine["typed_extract"].extract(trace,contracts,work)
            C.bump(work,"returned_candidates",len(found))
            for item in found:
                body=item["body"];key=C.digest(body)
                support={"source_label":label,"joint_sha256":joint,"source_root":item["source_root"],
                         "source_nodes":item["source_nodes"],"source_proof_sha256":C.digest(source["proof"])}
                groups.setdefault(key,{"id":key,"body":body,"context":item["context"],"supports":[]})["supports"].append(support)
                occurrences.append({"id":key,"support":support});checkpoint("CANDIDATE_RETAINED")
            checkpoint("RETURNED")
        records=[];supported=[];stage="support_grouping"
        for key in sorted(groups):
            row=groups[key];count=len({s["joint_sha256"] for s in row["supports"]})
            row["support_disposition"]="SUPPORTED" if count>=2 else "INSUFFICIENT_DISTINCT_JOINT_SUPPORT"
            records.append(row)
            if count>=2:supported.append(row)
        checkpoint("COMPLETE")
        return {"contexts":contexts,"occurrences":occurrences,"groups":records,"supported":supported}
    except Exception as exc:
        checkpoint("FAILED",{"type":type(exc).__name__,"message":str(exc)})
        raise
    finally:C.bump(work,"discovery_wall_s",time.perf_counter()-started)

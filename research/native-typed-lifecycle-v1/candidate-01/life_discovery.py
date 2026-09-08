"""All-candidate support grouping through the unchanged registered bridge."""
import life_common as C


def discover(training,engine,work):
    contract=C.load("unary_contract","authority/unary_contract.py")
    verifier=C.load("unary_verify","authority/unary_verify.py")
    syntax=C.load("registered_bridge_syntax","authority/bridge_syntax.py")
    meaning=C.load("registered_bridge_meaning","authority/bridge_meaning.py")
    signatures=C.load("registered_signatures","authority/signatures.py")
    groups={};occurrences=[];contexts=[]
    for label in training["selected"]:
        trace=training["traces"][label];source=trace["source"]
        bridge=syntax.translate(source["statement"],source["essential"],source["floating"],contract)
        checked=meaning.check(source,bridge,contract,verifier)
        C.require(checked["terminal"]=="INTERPRETATION_EQUIVALENT","BRIDGE_REFUSED")
        gates=checked["gates"]
        C.require(gates["premises_satisfiable"] is not None and gates["query_not_tautological"] is not None
                  and gates["entailment_counterexample"] is None
                  and all(x is not None for x in gates["essentiality_counterexamples"]),"SOURCE_MEANING_GATES")
        sign=signatures.canonical(checked["table"],bridge["task"]["predicates"])
        joint=sign["joint_premise_query"]["sha256"]
        contexts.append({"label":label,"bridge":bridge,"meaning":checked,"signatures":sign})
        C.bump(work,"bridge_worlds",checked["worlds"]);C.bump(work,"signature_world_permutations",6*255)
        used={n["label"] for n in trace["nodes"] if "label" in n}
        contracts={key:training["contracts"][key] for key in sorted(used)}
        for item in engine["typed_extract"].extract(trace,contracts,work):
            body=item["body"];key=C.digest(body)
            support={"source_label":label,"joint_sha256":joint,"source_root":item["source_root"],
                     "source_nodes":item["source_nodes"],"source_proof_sha256":C.digest(source["proof"])}
            groups.setdefault(key,{"id":key,"body":body,"context":item["context"],"supports":[]})["supports"].append(support)
            occurrences.append({"id":key,"support":support})
    records=[];supported=[]
    for key in sorted(groups):
        row=groups[key];count=len({s["joint_sha256"] for s in row["supports"]})
        row["support_disposition"]="SUPPORTED" if count>=2 else "INSUFFICIENT_DISTINCT_JOINT_SUPPORT"
        records.append(row)
        if count>=2:supported.append(row)
    return {"contexts":contexts,"occurrences":occurrences,"groups":records,"supported":supported}

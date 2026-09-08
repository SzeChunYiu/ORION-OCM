"""Independent direct label transport of the admitted own normal proof."""
import itertools
import life_common as C


def issue(row,number,permutation,cohort):
    source=row["trace"]["source"];context=row["context"]
    original=[r["variable"] for r in context["parameters"]]
    C.require(len(permutation)==3 and set(permutation)==set(original),"REQUEST_ATOMIC_BIJECTION")
    mapping=dict(zip(original,permutation))
    by_variable={p["variable"]:p for p in context["parameters"]}
    renamed_context={"schema":context["schema"],"dv":[],"parameters":[
        {"id":r["id"],**{k:by_variable[mapping[r["variable"]]][k]
                        for k in ("type","variable","floating_label")}}
        for r in context["parameters"]]}
    label="typed-reconstruct-"+str(number)
    rename=lambda tokens:[mapping.get(t,t) for t in tokens]
    holes=[{"label":label+".h"+str(i),"statement":rename(h["statement"])}
           for i,h in enumerate(source["essential"])]
    labels={p["floating_label"]:by_variable[mapping[p["variable"]]]["floating_label"]
            for p in context["parameters"]}
    labels.update({old["label"]:new["label"] for old,new in zip(source["essential"],holes)})
    # Only source proof labels are transported; no body/emitter/constructor decides the oracle.
    proof=[labels.get(t,t) for t in source["proof"]]
    claim=C.claim(label,rename(source["statement"]),holes,proof,C.parameters(source))
    return {"cohort":cohort,"witness_id":row["id"],"renaming":mapping,
            "context":renamed_context,"claim":claim}


def requests(payload,class_row):
    result=[]
    for _,row in sorted(payload["witnesses"].items()):
        variables=sorted(r["variable"] for r in row["context"]["parameters"])
        for permutation in itertools.permutations(variables):
            result.append(issue(row,len(result),permutation,"typed"))
    variables=[p["variable"] for p in class_row["context"]["parameters"]]
    result.append(issue(class_row,len(result),variables,"class_regression"))
    return {"schema":"native.typed-b-requests.v1","projection":C.digest(payload),
            "claims":result,"typed_permutations_per_witness":6,"class_identity_requests":1}


def check(packet,payload,class_row):
    C.require(packet==requests(payload,class_row),"EXACT_ISSUED_REQUEST")
    return packet

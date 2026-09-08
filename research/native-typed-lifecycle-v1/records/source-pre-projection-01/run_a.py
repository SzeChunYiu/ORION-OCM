"""Fresh typed producer: native training, all proposals, admission, persist, exit."""
from pathlib import Path
import importlib.util,sys,time
spec=importlib.util.spec_from_file_location("life_common",Path(__file__).with_name("life_common.py"))
C=importlib.util.module_from_spec(spec);sys.modules["life_common"]=C;spec.loader.exec_module(C)


def main(out):
    work={};engine=C.engine();packet=C.read(C.HERE/"inputs/fixtures/FIXTURES.json")
    claims=[{**{k:row[k] for k in ("label","premises","query","holes","proof")},
             "parameters":packet["parameters"]} for row in packet["fixtures"]]
    training=C.native(claims,out/"native-training",work,
                      (C.HERE/"inputs/fixtures/TRAINING-SUFFIX.mm").read_bytes())
    C.write(out/"TRAINING.json",training)
    C.require(training["terminal"]=="NATIVE_VERIFIED","NATIVE_TRAINING_REFUSED")
    discovery=C.load("life_discovery","life_discovery.py").discover(training,engine,work)
    parent=C.read(C.HERE/"inputs/PARENT.json");by_label={r["label"]:r for r in parent}
    C.require(len(parent)==4191 and len(by_label)==4191,"ORDINARY_CATALOGUE_POPULATION")
    for row in discovery["supported"]:
        for node in row["body"]["nodes"]:
            if node["kind"]=="apply":
                actual=training["contracts"][node["label"]]
                C.require({k:v for k,v in actual.items() if k!="span"}==by_label[node["label"]],
                          "ORDINARY_CONTRACT_MISMATCH")
        row["alias"]=engine["typed_alias"].classify(parent,row["body"],work)
    discovery_pin=C.write(out/"DISCOVERY.json",discovery)
    if not discovery["supported"]:
        return {"terminal":"NO_SUPPORTED_CANDIDATE","discovery":discovery_pin,"work":work}
    if any(row["alias"]["status"]=="UNKNOWN" for row in discovery["supported"]):
        return {"terminal":"ALIAS_CHECK_UNKNOWN","discovery":discovery_pin,"work":work}
    emitted=[];requests=[]
    for number,row in enumerate(discovery["supported"]):
        label="typed-admitted-"+str(number);context=row["context"]
        rename={r["id"]:r["variable"] for r in context["parameters"]}
        holes=[{"label":label+".h"+str(i),"statement":engine["typed_context"].rename(p,rename)}
               for i,p in enumerate(row["body"]["premises"])]
        proof=engine["typed_emit"].emit(row["body"],training["contracts"],context,holes,work)
        fixed=packet["parameters"]
        requests.append(C.claim(label,proof["target"],holes,proof["proof"],fixed))
        emitted.append({"id":row["id"],"label":label,"emission":proof})
    C.write(out/"ADMISSION-REQUESTS.json",requests)
    admission=C.native(requests,out/"native-admission",work)
    admission_pin=C.write(out/"ADMISSION.json",admission)
    C.require(admission["terminal"]=="NATIVE_VERIFIED","NATIVE_ADMISSION_REFUSED")
    witnesses={};eligible=[];aliases=[]
    for row,proposal in zip(discovery["supported"],emitted):
        key=row["id"];trace=admission["traces"][proposal["label"]]
        used={n["label"] for n in trace["nodes"] if "label" in n}
        contracts={name:admission["contracts"][name] for name in sorted(used)}
        variables=[r["variable"] for r in row["context"]["parameters"]]
        C.require(engine["typed_context"].from_source(trace["source"],variables)==row["context"],
                  "ADMITTED_CONTEXT_CHANGED")
        holes=[{"label":"producer-compare-"+str(i),"statement":p} for i,p in
               enumerate([h["statement"] for h in trace["source"]["essential"]])]
        constructed=engine["typed_constructor"].construct(trace,contracts,
                    {v:v for v in variables},holes,4096)
        recipe=engine["typed_emit"].emit(row["body"],contracts,row["context"],holes,work)
        C.require(all(constructed[k]==recipe[k] for k in ("proof","target","hypotheses")),
                  "ADMITTED_RECIPE_CONSTRUCTOR_MISMATCH")
        disposition=row["alias"]["status"]
        C.require(disposition in ("ALIAS","NO_ALIAS_IN_REGISTERED_DOMAIN"),"ALIAS_DISPOSITION")
        (aliases if disposition=="ALIAS" else eligible).append(key)
        witnesses[key]={"id":key,"body":row["body"],"context":row["context"],"trace":trace,
                        "contracts":contracts,"alias":row["alias"],"discovery_id":C.digest(row["supports"]),
                        "admission":admission_pin}
    state={"schema":"native.typed-persisted.v1","witnesses":witnesses,"eligible_method_ids":eligible,
           "alias_witness_ids":aliases,"discovery":discovery_pin,"admission":admission_pin,
           "source_freeze":C.identity(C.HERE/"SOURCE-FREEZE.json")}
    state_pin=C.write(out/"STATE.json",state)
    return {"terminal":"ADMITTED_AND_PERSISTED","state":state_pin,"admission":admission_pin,
            "eligible_method_ids":eligible,"alias_witness_ids":aliases,"work":work}


if __name__=="__main__":C.invocation(main)

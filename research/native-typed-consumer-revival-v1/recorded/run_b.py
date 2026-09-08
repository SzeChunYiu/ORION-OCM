"""Fresh consumer: admitted-own data only; independent exact-request native checking."""
from pathlib import Path
import copy,importlib.util,os,sys
spec=importlib.util.spec_from_file_location("life_common",Path(__file__).with_name("life_common.py"))
C=importlib.util.module_from_spec(spec);sys.modules["life_common"]=C;spec.loader.exec_module(C)


def refused(name,call,contains,records):
    try:call()
    except (ValueError,TypeError,KeyError) as exc:
        C.require(contains in str(exc),"WRONG_REFUSAL:"+name+":"+str(exc))
        records.append({"control":name,"terminal":"STRUCTURAL_REFUSAL","error":str(exc)})
    else:raise ValueError("FALSE_ACCEPT:"+name)


def require_native_negative(result,claim,verified_prefix,mode):
    C.require(result["terminal"]=="NATIVE_REJECTED" and result["native_calls"]==1 and
              result["error"]["stage"]=="native_check" and result["error"]["pending"]==claim["label"] and
              result["verified_labels"]==verified_prefix,
              "NATIVE_NEGATIVE_DID_NOT_REFUSE_EXACT_ISSUED_CLAIM:"+mode)


def audit_open(original,mode,flags,root,output,allowed,caches,opened):
    original=original.absolute();path=original.resolve()
    try:lexical=str(original.relative_to(root))
    except ValueError:lexical=None
    try:relative=str(path.relative_to(root))
    except ValueError:relative=None
    if lexical is None and relative is None:return
    if output==path or output in path.parents:return
    opened.append({"path":lexical or relative,"mode":str(mode),"flags":flags})
    if original in caches:
        write_flags=os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND
        C.require(type(flags) is int and flags&write_flags==0 and mode in ("r","rb",None),
                  "B_CACHE_PROBE_NOT_READ_ONLY:"+str(lexical))
        C.require(not original.exists(),"B_BYTECODE_PRESENT:"+str(lexical))
        return
    C.require(relative is not None,"B_PATH_ESCAPE:"+str(lexical))
    C.require(relative in allowed,"B_FORBIDDEN_READ:"+relative)


def main(out):
    opened=[]
    frozen=C.freeze()
    allowed=set(frozen["sources"])|set(frozen["b_inputs"])|{
        "SOURCE-FREEZE.json","RUN-REQUEST.json","EXECUTION-GATE.json","B-INPUT.json",
        "B-GATE.json","B-REQUEST.json","PROJECTION.json"}
    caches={Path(importlib.util.cache_from_source(str(C.HERE/name))).absolute()
            for name in frozen["sources"] if name.endswith(".py")}
    def audit(event,args):
        if event!="open" or not isinstance(args[0],(str,bytes)):return
        audit_open(Path(os.fsdecode(args[0])),args[1],args[2],C.HERE,out,allowed,caches,opened)
    sys.addaudithook(audit);C.AUDIT_READS=opened
    work={};C.ACTIVE_WORK=work;engine=C.engine();P=C.load("life_payload","life_payload.py")
    R=C.load("life_requests","life_requests.py")
    entry=C.checked(C.HERE/"B-INPUT.json",C.read(C.HERE/"B-GATE.json")["input"])
    C.require(set(entry)=={"projection","request","source_freeze"},"B_INPUT_SCHEMA")
    C.require(entry["source_freeze"]==C.identity(C.HERE/"SOURCE-FREEZE.json"),"B_SOURCE")
    payload=P.validate(C.checked(C.HERE/"PROJECTION.json",entry["projection"]),engine)
    class_row=P.class_witness(engine)
    request=R.check(C.checked(C.HERE/"B-REQUEST.json",entry["request"]),payload,class_row)
    parent={r["label"]:r for r in C.checked(C.HERE/"inputs/PARENT.json",
                                           C.freeze()["inputs"]["inputs/PARENT.json"])}
    for row in list(payload["witnesses"].values())+[class_row]:
        for label,contract in row["contracts"].items():
            if contract["kind"] in ("$a","$p"):
                C.require({k:v for k,v in contract.items() if k!="span"}==parent[label],
                          "CURRENT_ORDINARY_CONTRACT")
    records=[];proposals=[]
    for item in request["claims"]:
        row=class_row if item["cohort"]=="class_regression" else payload["witnesses"][item["witness_id"]]
        claim=item["claim"];holes=[{"label":h,"statement":p}
                                for h,p in zip(claim["holes"],claim["premises"])]
        constructed=engine["typed_constructor"].construct(row["trace"],row["contracts"],
                                                          item["renaming"],holes,4096)
        recipe=engine["typed_emit"].emit(row["body"],row["contracts"],item["context"],holes,work)
        expected={"proof":claim["proof"],"target":claim["query"],"hypotheses":holes}
        for path,value in (("constructor",constructed),("recipe",recipe)):
            C.require(all(value[k]==v for k,v in expected.items()),"ISSUED_OUTPUT_MISMATCH:"+path)
        proposals.append(claim)
        records.append({"label":claim["label"],"cohort":item["cohort"],"witness_id":item["witness_id"],
                        "proof_sha256":C.digest(claim["proof"]),"normal_labels":len(claim["proof"]),
                        "constructor":constructed,"recipe":recipe})
    C.write(out/"RECONSTRUCTIONS.json",records)
    controls=[];first=request["claims"][0];row=payload["witnesses"][first["witness_id"]]
    holes=[{"label":h,"statement":p} for h,p in zip(first["claim"]["holes"],first["claim"]["premises"])]
    wrong_holes=copy.deepcopy(holes);wrong_holes[0]["statement"]=["|-","-."]+wrong_holes[0]["statement"][1:]
    refused("wrong_exact_hole_constructor",lambda:engine["typed_constructor"].construct(
        row["trace"],row["contracts"],first["renaming"],wrong_holes,4096),"external statement",controls)
    refused("wrong_exact_hole_recipe",lambda:engine["typed_emit"].emit(
        row["body"],row["contracts"],first["context"],wrong_holes,work),"wrong exact hole",controls)
    changed=copy.deepcopy(request);changed["claims"][0]["claim"]["query"]=["|-","-."]+first["claim"]["query"][1:]
    refused("wrong_issued_target",lambda:R.check(changed,payload,class_row),"EXACT_ISSUED_REQUEST",controls)
    tc=engine["typed_context"];variables=list(first["renaming"])
    repeated={v:variables[0] for v in variables}
    composite={v:v for v in variables};composite[variables[0]]=["-.",variables[0]]
    refused("noninjective",lambda:tc.bijection(row["context"],repeated),"atomic bijection",controls)
    refused("composite",lambda:tc.bijection(row["context"],composite),"atomic bijection",controls)
    mixed=copy.deepcopy(row["context"]);mixed["parameters"][0]["type"]="setvar"
    refused("unsupported_type",lambda:tc.validate(mixed),"parameter identity/type",controls)
    dv=copy.deepcopy(row["context"]);dv["dv"]=[[variables[0],variables[1]]]
    refused("unsupported_DV",lambda:tc.validate(dv),"context schema/DV",controls)
    changed=copy.deepcopy(payload)
    if changed["alias_witness_ids"]:changed["eligible_method_ids"].append(changed["alias_witness_ids"][0])
    else:changed["eligible_method_ids"]=[]
    refused("changed_eligibility",lambda:P.validate(changed,engine),"ELIGIBILITY_SET",controls)
    changed=copy.deepcopy(payload);changed["witnesses"][first["witness_id"]]["teaching_history"]=[]
    refused("history_payload",lambda:P.validate(changed,engine),"WITNESS_ID",controls)
    # Save structural controls before opening current native authority.
    C.write(out/"STRUCTURAL-CONTROLS.json",controls)
    checked=C.native(proposals,out/"native-reconstruction",work)
    C.write(out/"NATIVE-RECONSTRUCTION.json",checked)
    C.require(checked["terminal"]=="NATIVE_VERIFIED","FRESH_RECONSTRUCTION_REFUSED")
    negative=[]
    _,authority=C.native_configuration()
    verified_prefix=checked["verified_labels"][:authority["prefix_proof_count"]]
    for mode in ("wrong_hole","wrong_target"):
        claim=copy.deepcopy(proposals[0])
        if mode=="wrong_hole":claim["premises"][0]=["|-","-."]+claim["premises"][0][1:]
        else:claim["query"]=["|-","-."]+claim["query"][1:]
        result=C.native([claim],out/("native-"+mode),work)
        C.write(out/(mode.upper()+".json"),result)
        require_native_negative(result,claim,verified_prefix,mode)
        negative.append({"control":mode,"claims_sha256":result["claims_sha256"],"error":result["error"],
                         "native_calls":result["native_calls"],"issued_label":claim["label"],
                         "verified_prefix_sha256":C.digest(verified_prefix)})
    C.require(C.identity(C.HERE/"PROJECTION.json")==entry["projection"] and
              C.identity(C.HERE/"B-REQUEST.json")==entry["request"],"CONSUMED_B_INPUT_CHANGED")
    return {"terminal":"TYPED_INTERFACE_QUALIFIED_ALIAS_ONLY" if not payload["eligible_method_ids"]
            else "TYPED_INTERFACE_QUALIFIED_WITH_NONALIAS_ELIGIBILITY",
            "eligible_method_ids":payload["eligible_method_ids"],"alias_witness_ids":payload["alias_witness_ids"],
            "request":entry["request"],"projection":entry["projection"],
            "typed_witnesses":len(payload["witnesses"]),"typed_reconstructions":6*len(payload["witnesses"]),
            "class_reconstructions":1,"structural_controls":controls,"native_negative_controls":negative,
            "work":work,"native_reconstruction":C.identity(out/"NATIVE-RECONSTRUCTION.json")}


if __name__=="__main__":C.invocation(main,"B")

"""Pure interface tests. Synthetic NATIVE_VERIFIED text grants no authority."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import pytest
import structural_fixture as F
import typed_context as C
import typed_constructor as K
import typed_extract as X
import typed_emit as E


def extracted(kind="wff",names=("ph","ps","ch"),labels=("wph","wps","wch")):
    trace,rows,proof=F.fixture(kind,names,labels)
    found=X.extract(trace,rows,{})
    assert len(found)==1
    return trace,rows,proof,found[0]


def supplied(item):
    m={r["id"]:r["variable"] for r in item["context"]["parameters"]}
    return [{"label":"external."+str(i),"statement":C.rename(p,m)}
            for i,p in enumerate(item["body"]["premises"])]


def test_wff_exact_expected_proof_and_repeated_hole():
    _,rows,_,item=extracted()
    actual=E.emit(item["body"],rows,item["context"],supplied(item),{})
    assert actual["proof"]==["wph","wps","wch","external.0","wph","wps","wch",
                             "external.0","external.1","compose","pair"]
    assert actual["target"]==["|-","(","ph","->","(","ps","/\\","ch",")",")"]
    assert actual["semantic_applications_expanded"]==2


def test_actual_renamed_graph_has_same_canonical_body():
    trace,rows,_,first=extracted()
    renaming={"ph":"ps","ps":"ch","ch":"ph"}
    labels={"wph":"wps","wps":"wch","wch":"wph"}
    renamed=deepcopy(trace);newrows=deepcopy(rows)
    renamed["source"]["statement"]=C.rename(trace["source"]["statement"],renaming)
    for h in renamed["source"]["essential"]:
        h["statement"]=C.rename(h["statement"],renaming)
        newrows[h["label"]]["statement"]=h["statement"]
    renamed["external_logical_hypotheses"]=deepcopy(renamed["source"]["essential"])
    for node in renamed["nodes"]:
        node["output"]=C.rename(node["output"],renaming)
        if node["kind"]=="floating_hypothesis":node["label"]=labels[node["label"]]
        if "substitution" in node:
            node["substitution"]={k:C.rename(v,renaming) for k,v in node["substitution"].items()}
            for obligation in node["obligations"]:
                obligation["expected"]=C.rename(obligation["expected"],renaming)
    second=X.extract(renamed,newrows,{})
    assert len(second)==1 and first["body"]==second[0]["body"]


def test_renamed_emission_uses_declared_floating_labels():
    _,rows,_,item=extracted();ctx=deepcopy(item["context"])
    for row,var,label in zip(ctx["parameters"],("ps","ch","ph"),("wps","wch","wph")):
        row.update(variable=var,floating_label=label)
    alt={**item,"context":ctx};actual=E.emit(item["body"],rows,ctx,supplied(alt),{})
    assert actual["proof"]==["wps","wch","wph","external.0","wps","wch","wph",
                             "external.0","external.1","compose","pair"]


def test_class_constructor_matches_existing_reference():
    trace,rows,_,_=extracted("class",("A","B","C"),("cA","cB","cC"))
    path=Path(__file__).resolve().parents[1]/"native-method-serving-v1/vendor/native_constructor.py"
    spec=importlib.util.spec_from_file_location("old_class_constructor",path)
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    holes=[{"label":"external."+str(i),"statement":h["statement"]}
           for i,h in enumerate(trace["source"]["essential"])]
    mapping={"A":"B","B":"C","C":"A"}
    for h in holes:h["statement"]=C.rename(h["statement"],mapping)
    assert K.construct(trace,rows,mapping,holes)==old.construct(trace,rows,mapping,holes)


@pytest.mark.parametrize("change",["type","dv","extra","repeat","composite"])
def test_context_boundaries(change):
    trace,_,_=F.fixture();source=deepcopy(trace["source"])
    if change=="type":source["floating"][1]["statement"][0]="class"
    elif change=="dv":source["active_dv"]=[["ph","ps"]]
    elif change=="extra":source["floating"].append({"label":"extra","statement":["wff","other"]})
    else:
        context=C.from_source(source)
        mapping={"ph":"ps","ps":"ps","ch":"ch"} if change=="repeat" else {"ph":["ph"],"ps":"ps","ch":"ch"}
        with pytest.raises(ValueError):C.bijection(context,mapping)
        return
    with pytest.raises(ValueError):C.from_source(source)


@pytest.mark.parametrize("change",["wrong_hole","swap_holes","wrong_type","changed_contract","unreachable","forward","extra_field"])
def test_recipe_refusals(change):
    _,rows,_,item=extracted();body=deepcopy(item["body"]);holes=supplied(item)
    if change=="wrong_hole":holes[0]["statement"]=["|-","ph"]
    elif change=="swap_holes":holes.reverse()
    elif change=="wrong_type":body["nodes"][0]["output"][0]="class"
    elif change=="changed_contract":rows["pair"]["statement"]=["|-","ph"]
    elif change=="unreachable":body["nodes"].insert(0,deepcopy(body["nodes"][0]));body["root"]+=1
    elif change=="forward":body["nodes"][-1]["inputs"][0]=body["root"]
    else:body["extra"]="history"
    with pytest.raises(ValueError):E.emit(body,rows,item["context"],holes,{})


@pytest.mark.parametrize("change",["output","contract","extra_float","node_limit","proof_limit"])
def test_full_trace_refusals(change):
    trace,rows,_=F.fixture();holes=[{"label":"ext."+str(i),"statement":h["statement"]}
                                  for i,h in enumerate(trace["source"]["essential"])]
    maximum=4096
    if change=="output":trace["nodes"][0]["output"]=["wff","ps"]
    elif change=="contract":rows["compose"]["dv"]=[["ph","ps"]]
    elif change=="extra_float":trace["source"]["floating"][0]["label"]="another"
    elif change=="node_limit":trace["nodes"]*=20
    else:maximum=5
    with pytest.raises(ValueError):K.construct(trace,rows,{"ph":"ph","ps":"ps","ch":"ch"},holes,maximum)


@pytest.mark.parametrize("change",["floating_label","floating_statement"])
def test_floating_context_must_match_exact_native_contract(change):
    _,rows,_,item=extracted()
    if change=="floating_label":
        item["context"]["parameters"][0]["floating_label"]="invented"
    else:
        rows["wph"]["statement"]=["wff","ps"]
    with pytest.raises(ValueError,match="exact floating"):
        E.emit(item["body"],rows,item["context"],supplied(item),{})


def test_extraction_enumerates_all_proper_roots_with_fixed_semantic_bound():
    trace,rows,inner=F.fixture()
    many=F.trace_from_proof(trace["source"],rows,["wph","wps","wch"]*10+inner+["wrap"]*10)
    candidates=X.extract(many,rows,{})
    assert [c["semantic_nodes"] for c in candidates]==list(range(2,9))
    assert len({c["source_root"] for c in candidates})==7


@pytest.mark.parametrize("size",[1,8,9])
def test_recipe_semantic_dag_boundary(size):
    _,rows,_,item=extracted();body=deepcopy(item["body"])
    if size==1:
        body["nodes"]=body["nodes"][:-1]
        body["root"]=len(body["nodes"])-1;body["query"]=body["nodes"][-1]["output"]
    else:
        floats=[next(i for i,n in enumerate(body["nodes"]) if n["kind"]=="float" and n["output"][1]==v)
                for v in C.IDS]
        while sum(n["kind"]=="apply" for n in body["nodes"])<size:
            body["nodes"].append({"kind":"apply","label":"wrap","inputs":floats+[body["root"]],
                                  "output":body["query"],
                                  "substitution":dict(zip(("ph","ps","ch"),[[v] for v in C.IDS]))})
            body["root"]=len(body["nodes"])-1
    if size==8:
        result=E.emit(body,rows,item["context"],supplied(item),{})
        assert result["semantic_applications_expanded"]==8
    else:
        with pytest.raises(ValueError,match="proper semantic DAG bound"):
            E.emit(body,rows,item["context"],supplied(item),{})


def test_recipe_root_rejects_boolean_identity():
    _,rows,_,item=extracted();item["body"]["root"]=True
    with pytest.raises(ValueError,match="body root/population"):
        E.emit(item["body"],rows,item["context"],supplied(item),{})

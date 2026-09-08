"""Independent ordinary alias witnesses; no learned-method selection."""
from copy import deepcopy
import pytest
import typed_alias as A
import typed_context as C


def rule(label="ordinary",premises=None,dv=None):
    return {"label":label,"kind":"$a",
            "floating":[{"label":"fx","statement":["wff","x"]},
                        {"label":"fy","statement":["wff","y"]}],
            "essential":[{"label":"h"+str(i),"statement":p} for i,p in enumerate(premises or [])],
            "statement":["|-","(","x","->","y",")"],"dv":dv or []}


def body(query,premises=None,kind="wff"):
    return {"parameters":C.parameters(kind),"query":query,"premises":premises or []}


def test_composite_and_repeated_images_are_ordinary_aliases():
    q=["|-","(","(","V0","->","V1",")","->","(","V0","->","V1",")",")"]
    result=A.classify([rule()],body(q),{})
    assert result["status"]=="ALIAS" and not result["eligible"]
    assert result["aliases"]==[{"label":"ordinary",
        "substitution":{"x":["(","V0","->","V1",")"],"y":["(","V0","->","V1",")"]},
        "premise_indices":[]}]


def test_repeated_essential_ports_may_use_same_premise():
    h=["|-","(","x","->","y",")"];q=["|-","(","V0","->","V1",")"]
    result=A.classify([rule(premises=[h,h])],body(q,[q]),{})
    assert result["status"]=="ALIAS"
    assert result["aliases"][0]["premise_indices"]==[0,0]


def test_all_parallel_alias_labels_retained():
    q=["|-","(","V0","->","V1",")"]
    result=A.classify([rule("first"),rule("second")],body(q),{})
    assert [r["label"] for r in result["aliases"]]==["first","second"]


def test_no_ambient_dv_forbids_nonempty_image_supports():
    q=["|-","(","V0","->","V1",")"]
    result=A.classify([rule(dv=[["x","y"]])],body(q),{})
    assert result=={"status":"NO_ALIAS_IN_REGISTERED_DOMAIN","eligible":True,"aliases":[]}


@pytest.mark.parametrize("q",[["|-","unknown"],["|-","(","V0","nonsense","V1",")"],["|-","V3"]])
def test_unsupported_ground_never_grants_eligibility(q):
    result=A.classify([rule()],body(q),{})
    assert result["status"]=="UNKNOWN" and result["eligible"] is False


def test_unsupported_inventory_never_grants_eligibility():
    r=rule();r["floating"][0]["statement"][0]="alien"
    assert A.classify([r],body(["|-","(","V0","->","V1",")"]),{})["status"]=="UNKNOWN"


def test_class_composite_image_alias_regression():
    r=rule();r["floating"][0]["statement"][0]="class";r["floating"][1]["statement"][0]="class"
    r["statement"]=["|-","x","C_","y"]
    q=["|-","(","V0","i^i","V1",")","C_","V2"]
    result=A.classify([r],body(q,kind="class"),{})
    assert result["status"]=="ALIAS"
    assert result["aliases"][0]["substitution"]=={"x":["(","V0","i^i","V1",")"],"y":["V2"]}


@pytest.mark.parametrize("dv",[[],[["x","y"]]])
def test_raw_legacy_atoms_are_unknown_even_with_dv(dv):
    r=rule(dv=dv)
    for h in r["floating"]:h["statement"][0]="class"
    r["statement"]=["|-","x","C_","y"]
    result=A.classify([r],body(["|-","A","C_","V0"],kind="class"),{})
    assert result["status"]=="UNKNOWN" and not result["eligible"]


@pytest.mark.parametrize("depth",[16,17])
def test_exact_donor_expression_depth_boundary(depth):
    import typed_grammar as G
    from vendor import bridge_syntax as donor
    q=["|-","(","V0","->"]+["-."]*(depth-1)+["V1",")"]
    check=G.checker(C.parameters("wff"));types=dict.fromkeys(C.IDS,"wff")
    if depth==16:
        assert donor.parse(q,types)["body"]["op"]=="implies"
        assert check("wff",q[1:])
    else:
        with pytest.raises(ValueError):donor.parse(q,types)
        with pytest.raises(ValueError):check("wff",q[1:])


@pytest.mark.parametrize("total_tokens",[512,513])
def test_exact_donor_expression_token_boundary(total_tokens):
    import typed_grammar as G
    from vendor import bridge_syntax as donor
    def tree(depth):
        return ["V0"] if depth==0 else ["("]+tree(depth-1)+["->"]+tree(depth-1)+[")"]
    q=["|-","("]+["-."]*(total_tokens-510)+tree(6)+["->"]+tree(6)+[")"]
    assert len(q)==total_tokens
    check=G.checker(C.parameters("wff"));types=dict.fromkeys(C.IDS,"wff")
    if total_tokens==512:
        assert donor.parse(q,types)["body"]["op"]=="implies"
        assert check("wff",q[1:])
    else:
        with pytest.raises(ValueError):donor.parse(q,types)
        with pytest.raises(ValueError):check("wff",q[1:])

"""Syntactic versus actual finite-world identity, never output filtering."""
from assay_test_support import authored_only
import copy
from unary_test_support import task,statement as s,pred
from unary_rule_identity import semantic_key
from assay_test_support import api,chain,other,grouped

def test_alpha_and_premise_order_identity_preserves_multiplicity():
    m=api("unary_assay_identity");a=chain()
    b=task([s("every","B","C"),s("every","A","B")],s("every","A","C"))
    assert m.syntax_key(a,work={})==m.syntax_key(b,work={})
    b=copy.deepcopy(a);b["premises"].append(copy.deepcopy(b["premises"][0]))
    assert m.syntax_key(a,work={})!=m.syntax_key(b,work={})
    work={}
    assert m.semantic_key(a,work)==m.semantic_key(b,{})
    assert work["semantic_worlds"]==6*255

def test_ast_order_not_boolean_commutative_normalization():
    m=api("unary_assay_identity");a=grouped();b=copy.deepcopy(a)
    b["premises"][0]["left"][1:]=reversed(b["premises"][0]["left"][1:])
    assert m.syntax_key(a,work={})!=m.syntax_key(b,work={})
    assert m.semantic_key(a,{})==m.semantic_key(b,{})

def test_syntax_gate_precedence_and_actual_semantic_distinction():
    m=api("unary_assay_identity")
    a=chain();a["premises"]=[s("every","P0","P0")];a["query"]=s("every","P0","P0")
    assert m.gate(a,"development",work={})=="MISSING_PREDICATE"
    assert m.gate(chain(),"development",work={})=="MISSING_BOOLEAN_GROUP"
    assert m.gate(grouped(),"development",work={}) is None
    assert m.semantic_key(chain(),{})!=m.semantic_key(other(),{})

def test_inconsistent_tasks_are_kept_and_collide_semantically():
    m=api("unary_assay_identity")
    a=task([s("some","P0","P1"),s("no","P0","P1")],s("every","P2","P2"))
    b=task([s("some","P2","P2"),s("no","P2","P2")],s("no","P0","P1"))
    assert m.gate(a,"train",work={}) is None
    assert m.semantic_key(a,{})==m.semantic_key(b,{})

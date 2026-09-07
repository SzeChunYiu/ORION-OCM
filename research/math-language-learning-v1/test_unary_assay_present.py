"""Authored presentation/variant checks; use provenance is a later caller duty."""
from assay_test_support import authored_only
import copy
import pytest
from unary_contract import task_digest,InputRefused
from unary_language import parse
from unary_test_support import task,statement as s
from assay_test_support import api,chain,grouped

def test_fresh_labels_exact_text_digest_and_counterbalanced_order():
    m=api("unary_assay_present");work={}
    pairs=[m.final_pair(grouped(),1,i,work=work) for i in range(2)]
    assert pairs[0]["formal"]["predicates"]==["e1f0p0","e1f0p1","e1f0p2"]
    assert task_digest(parse(pairs[0]["text"]))==pairs[0]["task_sha256"]
    rows=m.presentation_rows(pairs,1,work=work)
    assert [r["presentation"] for r in rows]==["text","ast","ast","text"]
    assert [r["row_id"] for r in rows]==["e1/final/0","e1/final/0","e1/final/1","e1/final/1"]
    assert work["realizations"]==2 and work["presentation_rows"]==4

def test_removal_recomputes_used_registry_and_original_index_map():
    m=api("unary_assay_present")
    t=task([s("every","P0","P1"),s("some","P2","P2")],s("every","P0","P1"))
    r=m.remove(t,1,work={})
    assert r["task"]["predicates"]==["P0","P1"]
    assert r["original_to_derived"]==[0,None] and r["removed_original_index"]==1
    assert task_digest(r["task"])==r["task_sha256"]

def test_no_use_and_duplicate_removals_keep_all_restorations():
    m=api("unary_assay_present");t=chain()
    a=m.support_variants(t,used_cover=[0,1],work={})
    assert [x["kind"] for x in a]==["ordinary_remove","ordinary_restore","used_remove","used_restore"]
    assert a[0]["task_sha256"]==a[2]["task_sha256"]
    assert a[1]["task_sha256"]==a[3]["task_sha256"]==task_digest(t)
    b=m.support_variants(t,used_cover=None,work={})
    assert b[2]["terminal"]=="NOT_APPLICABLE" and b[3]["task_sha256"]==task_digest(t)

@pytest.mark.parametrize("cover",[[],[True],[1,0],[0,0],[99]])
def test_invalid_cover_not_interpreted_as_checked_no_use(cover):
    with pytest.raises(InputRefused,match="SUPPORT_COVER"):
        api("unary_assay_present").support_variants(chain(),used_cover=cover,work={})

def test_unused_registry_remains_refused():
    t=chain();t["predicates"].append("P3")
    with pytest.raises(InputRefused,match="UNUSED_PREDICATE"):
        api("unary_assay_present").final_pair(t,0,0,work={})

def test_no_universal_support_still_keeps_both_original_restorations():
    m=api("unary_assay_present")
    t=task([s("some","P0","P1"),s("some","P2","P2")],s("some","P0","P2"))
    r=m.support_variants(t,used_cover=None,work={})
    assert [x["terminal"] for x in r]==["NOT_APPLICABLE","READY","NOT_APPLICABLE","READY"]
    assert r[1]["task"]==r[3]["task"]==t

def test_changed_pair_identity_refuses_before_presentation_output():
    m=api("unary_assay_present");pair=m.final_pair(grouped(),0,0,work={})
    pair["task_sha256"]="0"*64
    with pytest.raises(InputRefused,match="PRESENTATION_BINDING"):
        m.presentation_rows([pair],0,work={})

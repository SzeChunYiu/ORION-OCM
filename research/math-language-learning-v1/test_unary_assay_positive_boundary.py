"""Actual exact child plus resealed malformed claimed-positive artifact controls."""
import pytest
from assay_test_support import authored_only
from test_unary_assay_coordinator_boundaries import alter_row

@pytest.mark.parametrize("fault",["none","missing_packet","null_packet","missing_answer","invalid_answer"])
def test_claimed_checked_row_requires_whole_positive_result(tmp_path,fault):
    import unary_assay_auth as a
    from test_unary_assay_service_process import child
    from test_unary_assay_service import rows
    import unary_method_plain as D
    root=tmp_path/"exact"
    p,v=child(root,"exact","presented_batch",{"rows":rows()[:1]})
    request=D.parse((root/"request.json").read_bytes())
    kw=dict(arm="exact",mode="presented_batch",request=request,sources=p["source_before"],
            profile=p["profile"],deadline=p["deadline_monotonic"])
    assert len(a.inspect(root,work={},**kw)["rows"])==1
    def change(row):
        if fault=="none":row["result"]=None
        elif fault=="missing_packet":del row["result"]["packet"]
        elif fault=="null_packet":row["result"]["packet"]=None
        elif fault=="missing_answer":del row["result"]["packet"]["result"]
        else:row["result"]["packet"]["result"]["status"]="UNKNOWN"
    alter_row(root,change)
    error=a.ControlFailure if fault=="invalid_answer" else a.CustodyFailure
    with pytest.raises(error):a.inspect(root,work={},**kw)

def test_operational_row_without_result_remains_unavailable(tmp_path):
    import unary_assay_auth as a
    from test_unary_assay_service_process import child
    from test_unary_assay_service import rows
    import unary_method_plain as D
    root=tmp_path/"exact"
    p,v=child(root,"exact","presented_batch",{"rows":rows()[:1]})
    request=D.parse((root/"request.json").read_bytes())
    alter_row(root,lambda row:row.update(result=None,terminal="CANNOT_CHECK"),partial=True)
    result=a.inspect(root,work={},arm="exact",mode="presented_batch",request=request,
        sources=p["source_before"],profile=p["profile"],deadline=p["deadline_monotonic"])
    assert result["terminal"]=="CANNOT_CHECK" and result["rows"]==[]

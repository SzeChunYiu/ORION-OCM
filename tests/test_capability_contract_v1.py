from __future__ import annotations
import copy, importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LANE=ROOT/"research"/"capability-contract-v1"
SPEC=importlib.util.spec_from_file_location("capability_contract_validate",LANE/"validate.py")
v=importlib.util.module_from_spec(SPEC); assert SPEC.loader is not None; SPEC.loader.exec_module(v)
def load(): return v.load_registry(LANE)

def test_registry_valid_and_exact():
    m,c,q=load(); assert v.validate_registry(m,c,q)==[]; assert (len(c),len(q))==(27,17)
def test_missing_field_rejected():
    m,c,q=load(); c=copy.deepcopy(c); del c[0]["falsifier"]; assert any("missing fields" in x for x in v.validate_registry(m,c,q))
def test_missing_capability_rejected():
    m,c,q=load(); c=copy.deepcopy(c); c.pop(); assert any("capability ID set mismatch" in x for x in v.validate_registry(m,c,q))
def test_unknown_resource_rejected():
    m,c,q=load(); c=copy.deepcopy(c); c[0]["resource_metric"].append("free_magic"); assert any("unknown resource" in x for x in v.validate_registry(m,c,q))
def test_unknown_coordinate_link_rejected():
    m,c,q=load(); c=copy.deepcopy(c); c[0]["coordinate_links"]=["nope"]; assert any("unknown coordinate" in x for x in v.validate_registry(m,c,q))
def test_claim_escalation_rejected():
    m,c,q=load(); c=copy.deepcopy(c); c[0]["claim_ceiling"]="G6"; assert any("claim ceiling exceeds" in x for x in v.validate_registry(m,c,q))
def test_twin_reference_required():
    m,c,q=load(); c=copy.deepcopy(c); c[0]["minimal_negative_twin"]="bad"; assert any("N0" in x for x in v.validate_registry(m,c,q))
def test_parent_first_refusal_required():
    m,c,q=load(); c=copy.deepcopy(c); c[0]["strongest_parent"]="bad"; assert any("P0" in x for x in v.validate_registry(m,c,q))
def test_coordinate_set_exact():
    m,c,q=load(); q=copy.deepcopy(q); r=copy.deepcopy(q[0]); r["id"]="fake_iq"; q.append(r); assert any("coordinate ID set mismatch" in x for x in v.validate_registry(m,c,q))
def test_coordinate_global_gate_metadata_required():
    m,c,q=load(); q=copy.deepcopy(q); del q[0]["falsifier"]; assert any("missing fields" in x for x in v.validate_registry(m,c,q))

def test_hoeffding_radius_three_tail_allocation():
    import math
    assert abs(v.hoeffding_radius(200,0.05)-math.sqrt(2*math.log(60)/200))<1e-12

def test_s0_assay_accepts_separation_and_twin_collapse():
    assert v.assay_pass([0.8]*200,[0.0]*200,tau_parent=0.5,tau_twin=0.25,alpha=0.05)
    assert not v.assay_pass([0.8]*200,[0.4]*200,tau_parent=0.5,tau_twin=0.25,alpha=0.05)

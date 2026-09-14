#!/usr/bin/env python3
"""Structural verifier for issue #602 A4/F1 capability-contract V1."""
from __future__ import annotations
import json, math, re, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
EXPECTED_CAPABILITIES=(
"perception","selective_attention","working_memory","episodic_memory","semantic_memory",
"procedural_memory","retrieval","consolidation","forgetting","prediction","abstraction_concept_formation",
"compositional_reasoning","hierarchical_skill_formation","planning","exploration_information_seeking",
"causal_inference","counterfactual_reasoning","metacognition","social_cognition_theory_of_mind",
"communication","imitation","teaching","cultural_accumulation","self_modeling","self_improvement",
"tool_use","coordination_collective_cognition")
EXPECTED_COORDINATES=(
"memory_capacity_retention","retrieval_efficiency","abstraction_compression_ability",
"transfer_generalization","compositional_depth","planning_horizon",
"exploration_information_gain_efficiency","causal_identifiability_intervention","robustness_invariance",
"continual_learning_plasticity","catastrophic_forgetting_susceptibility","tool_use_solver_routing",
"social_model_depth","communication_capacity","verification_reliability","self_model_accuracy",
"meta_learning_evolvability")
CAP_REQUIRED={"id","label","inputs","allowed_information","required_behavior","success_metric",
"resource_metric","minimal_negative_twin","strongest_parent","falsifier","scope","assumptions",
"evidence_class","claim_ceiling","coordinate_links"}
COORD_REQUIRED={"id","label","definition","reporting_contract","scope","evidence_class","claim_ceiling"}
META_REQUIRED={"schema_version","issue","scope","assumptions","evidence_class","strongest_parent",
"falsifier","claim_ceiling","definitions","statistics","resource_dimensions","capability_files",
"coordinate_file"}

def rank(x):
    m=re.fullmatch(r"G(\d+)",x if isinstance(x,str) else "")
    if not m: raise ValueError(f"invalid claim ceiling {x!r}")
    return int(m.group(1))

def hoeffding_radius(n, alpha):
    """One-sided radius for each of the three simultaneous paired-difference tails."""
    if not isinstance(n, int) or n <= 0:
        raise ValueError("n must be a positive integer")
    if not isinstance(alpha, (int, float)) or not 0 < alpha < 1:
        raise ValueError("alpha must lie in (0,1)")
    return math.sqrt(2.0 * math.log(3.0 / alpha) / n)

def assay_pass(positive_diffs, twin_diffs, tau_parent, tau_twin, alpha=0.05):
    """Evaluate common S0 gates for paired differences already bounded in [-1,1]."""
    if not positive_diffs or not twin_diffs:
        raise ValueError("both paired-difference samples must be nonempty")
    for x in [*positive_diffs, *twin_diffs]:
        if not isinstance(x, (int, float)) or not -1 <= x <= 1:
            raise ValueError("paired differences must lie in [-1,1]")
    mp=sum(positive_diffs)/len(positive_diffs)
    mt=sum(twin_diffs)/len(twin_diffs)
    ep=hoeffding_radius(len(positive_diffs),alpha)
    et=hoeffding_radius(len(twin_diffs),alpha)
    return (mp-ep>tau_parent) and (abs(mt)+et<=tau_twin)

def load_registry(base=HERE):
    meta=json.loads((base/"CAPABILITY_CONTRACT_V1.json").read_text(encoding="utf-8"))
    caps=[]
    for name in meta["capability_files"]:
        caps.extend(json.loads((base/name).read_text(encoding="utf-8")))
    coords=json.loads((base/meta["coordinate_file"]).read_text(encoding="utf-8"))
    return meta,caps,coords

def validate_registry(meta,caps,coords):
    e=[]
    missing=META_REQUIRED-set(meta)
    if missing: return [f"meta missing fields: {sorted(missing)}"]
    if meta["issue"]!=602: e.append("issue must be 602")
    defs=meta.get("definitions",{})
    for code in ("A0","S0","N0","P0"):
        if not isinstance(defs.get(code),str) or not defs[code]: e.append(f"missing common definition {code}")
    if "alpha/3" not in meta.get("statistics",{}).get("rule",""): e.append("statistics must state three-tail Bonferroni correction")
    a=meta.get("statistics",{}).get("alpha_default")
    if not isinstance(a,(int,float)) or not 0<a<1: e.append("alpha_default must lie in (0,1)")
    cids=[r.get("id") for r in caps if isinstance(r,dict)]
    qids=[r.get("id") for r in coords if isinstance(r,dict)]
    if len(cids)!=len(set(cids)): e.append("capability IDs must be unique")
    if len(qids)!=len(set(qids)): e.append("coordinate IDs must be unique")
    if set(cids)!=set(EXPECTED_CAPABILITIES):
        e.append(f"capability ID set mismatch: missing={sorted(set(EXPECTED_CAPABILITIES)-set(cids))}, extra={sorted(set(cids)-set(EXPECTED_CAPABILITIES))}")
    if set(qids)!=set(EXPECTED_COORDINATES):
        e.append(f"coordinate ID set mismatch: missing={sorted(set(EXPECTED_COORDINATES)-set(qids))}, extra={sorted(set(qids)-set(EXPECTED_COORDINATES))}")
    try: ceiling=rank(meta["claim_ceiling"])
    except ValueError as x: e.append(str(x)); ceiling=-1
    resources=set(meta.get("resource_dimensions",{})); qset=set(qids)
    for r in caps:
        if not isinstance(r,dict): e.append("capability row must be object"); continue
        cid=r.get("id","<missing>"); miss=CAP_REQUIRED-set(r)
        if miss: e.append(f"{cid}: missing fields {sorted(miss)}"); continue
        for k in ("label","inputs","allowed_information","required_behavior","success_metric",
                  "minimal_negative_twin","strongest_parent","falsifier","scope","evidence_class"):
            if not isinstance(r[k],str) or not r[k].strip(): e.append(f"{cid}: {k} must be nonempty text")
        if r["allowed_information"]!="A0": e.append(f"{cid}: allowed_information must reference A0")
        if r["success_metric"]!="S0": e.append(f"{cid}: success_metric must reference S0")
        if "+ N0" not in r["minimal_negative_twin"]: e.append(f"{cid}: negative twin must reference one-dependency N0")
        if "+ P0" not in r["strongest_parent"]: e.append(f"{cid}: strongest parent must reference first-refusal P0")
        if not isinstance(r["resource_metric"],list) or not r["resource_metric"]:
            e.append(f"{cid}: resource_metric must be nonempty")
        else:
            u=set(r["resource_metric"])-resources
            if u: e.append(f"{cid}: unknown resource dimensions {sorted(u)}")
        if not isinstance(r["coordinate_links"],list) or not r["coordinate_links"]:
            e.append(f"{cid}: coordinate_links must be nonempty")
        else:
            u=set(r["coordinate_links"])-qset
            if u: e.append(f"{cid}: unknown coordinate links {sorted(u)}")
        try:
            if rank(r["claim_ceiling"])>ceiling: e.append(f"{cid}: claim ceiling exceeds meta")
        except ValueError as x: e.append(f"{cid}: {x}")
    for r in coords:
        if not isinstance(r,dict): e.append("coordinate row must be object"); continue
        qid=r.get("id","<missing>"); miss=COORD_REQUIRED-set(r)
        if miss: e.append(f"{qid}: missing fields {sorted(miss)}"); continue
        for k in ("label","definition","reporting_contract","scope","evidence_class"):
            if not isinstance(r[k],str) or not r[k].strip(): e.append(f"{qid}: {k} must be nonempty text")
        try:
            if rank(r["claim_ceiling"])>ceiling: e.append(f"{qid}: claim ceiling exceeds meta")
        except ValueError as x: e.append(f"{qid}: {x}")
    return e

def main():
    try: meta,caps,coords=load_registry()
    except Exception as x:
        print(f"ERROR: unable to load registry: {x}",file=sys.stderr); return 1
    errors=validate_registry(meta,caps,coords)
    if errors:
        for x in errors: print("ERROR:",x,file=sys.stderr)
        return 1
    print(f"CAPABILITY_CONTRACT_V1: VALID ({len(caps)} capabilities, {len(coords)} coordinates)")
    return 0
if __name__=="__main__": raise SystemExit(main())

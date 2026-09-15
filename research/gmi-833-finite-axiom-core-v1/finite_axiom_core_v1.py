from __future__ import annotations

from copy import deepcopy
from fractions import Fraction as F
from itertools import product
import json
from typing import Any, Dict, Iterable, Mapping, Sequence, Tuple

CLAIM_CEILING = "GMI_REGISTERED_FINITE_AXIOM_CORE_SATISFIABLE_AND_COMPACT_AT_SCOPE"
FORBIDDEN_PROMOTIONS = (
    "GMI_ABSOLUTELY_CONSISTENT",
    "ZFC_CONSISTENCY_PROVED",
    "ALL_FUTURE_GMI_EXTENSIONS_CONSISTENT",
    "ONTOLOGICAL_COMPLETENESS",
    "ALL_GMI_DERIVED_FROM_FIVE_AXIOMS_UNIVERSALLY",
    "ALL_EMPIRICAL_GMI_RESULTS_DERIVED",
    "COMPLETE_GMI",
)
AXIOMS = ("AX-1", "AX-2", "AX-3", "AX-4", "AX-5")
ALLOWED_UNCERTAINTY_TAGS = (
    "FeasibleSet",
    "ConfidenceSet",
    "PredictiveLaw",
    "LatentPredictiveModel",
    "SelectivePrediction",
)
SUPPORTS = {
    ("FINITE_MODEL_WITNESS", "FINITE_EXISTENTIAL"),
    ("FINITE_EXHAUSTIVE", "BOUNDED_FINITE"),
    ("ANALYTIC_FINITE", "REGISTERED_FINITE"),
    ("UNIVERSAL_PROOF", "UNIVERSAL"),
}


def _unique_nonempty(values: Sequence[Any]) -> bool:
    return isinstance(values, tuple) and bool(values) and len(values) == len(set(values))


def _prob_law(law: Mapping[Any, F], domain: Sequence[Any]) -> bool:
    if set(law) != set(domain):
        return False
    if any(type(v) is not F or v < 0 or v > 1 for v in law.values()):
        return False
    return sum(law.values(), F(0)) == 1


def check_ax1(model: Mapping[str, Any]) -> Tuple[bool, Tuple[str, ...]]:
    errors = []
    states = model.get("states", ())
    actions = model.get("actions", ())
    outputs = model.get("outputs", ())
    interventions = model.get("interventions", ())
    intervention_outputs = model.get("intervention_outputs", ())
    for name, values in (
        ("states", states), ("actions", actions), ("outputs", outputs),
        ("interventions", interventions), ("intervention_outputs", intervention_outputs),
    ):
        if not _unique_nonempty(values):
            errors.append(f"{name}:FINITE_NONEMPTY_UNIQUE")
    sset, aset, oset = set(states), set(actions), set(outputs)
    jset, ioset = set(interventions), set(intervention_outputs)
    for key, target in model.get("transition", {}).items():
        if not isinstance(key, tuple) or len(key) != 2 or key[0] not in sset or key[1] not in aset or target not in sset:
            errors.append("transition:TYPED")
            break
    for s, out in model.get("output", {}).items():
        if s not in sset or out not in oset:
            errors.append("output:TYPED")
            break
    for key, out in model.get("intervention_response", {}).items():
        if not isinstance(key, tuple) or len(key) != 2 or key[0] not in sset or key[1] not in jset or out not in ioset:
            errors.append("intervention:TYPED")
            break
    for edge in model.get("development_edges", ()):
        if not isinstance(edge, tuple) or len(edge) != 2 or edge[0] not in sset or edge[1] not in sset:
            errors.append("development:TYPED")
            break
    return not errors, tuple(errors)


def check_ax2(model: Mapping[str, Any]) -> Tuple[bool, Tuple[str, ...]]:
    errors = []
    states, actions = model.get("states", ()), model.get("actions", ())
    interventions = model.get("interventions", ())
    if model.get("initial") not in set(states):
        errors.append("initial:REGISTERED")
    expected_t = {(s, a) for s in states for a in actions}
    if set(model.get("transition", {})) != expected_t:
        errors.append("transition:TOTAL")
    if set(model.get("output", {})) != set(states):
        errors.append("output:TOTAL")
    expected_i = {(s, j) for s in states for j in interventions}
    if set(model.get("intervention_response", {})) != expected_i:
        errors.append("intervention:TOTAL")
    return not errors, tuple(errors)


def check_ax3(model: Mapping[str, Any]) -> Tuple[bool, Tuple[str, ...]]:
    errors = []
    resources = model.get("resources")
    if not isinstance(resources, tuple) or not resources:
        errors.append("resources:NONEMPTY_VECTOR")
        return False, tuple(errors)
    if any(type(x) is not F or x < 0 for x in resources):
        errors.append("resources:NONNEGATIVE_EXACT")
    for contract in model.get("capability_contracts", ()):
        budget = contract.get("budget")
        if not isinstance(budget, tuple) or len(budget) != len(resources):
            errors.append(f"budget:{contract.get('id')}:DIMENSION")
        elif any(type(x) is not F or x < 0 for x in budget):
            errors.append(f"budget:{contract.get('id')}:NONNEGATIVE_EXACT")
    return not errors, tuple(errors)


def _check_uncertainty_object(obj: Mapping[str, Any]) -> Tuple[str, ...]:
    errors = []
    tag = obj.get("tag")
    if tag not in ALLOWED_UNCERTAINTY_TAGS:
        return ("uncertainty:UNKNOWN_TAG",)
    if tag in ("FeasibleSet", "ConfidenceSet"):
        domain = obj.get("domain", ())
        values = obj.get("values", ())
        if not _unique_nonempty(domain):
            errors.append(f"{tag}:DOMAIN")
        if not isinstance(values, tuple) or not set(values).issubset(set(domain)):
            errors.append(f"{tag}:SUBSET")
        if tag == "ConfidenceSet":
            alpha = obj.get("alpha")
            if type(alpha) is not F or not (0 <= alpha <= 1):
                errors.append("ConfidenceSet:ALPHA")
            truth_law = obj.get("truth_law", {})
            if not _prob_law(truth_law, domain):
                errors.append("ConfidenceSet:TRUTH_LAW")
            elif type(alpha) is F and isinstance(values, tuple) and set(values).issubset(set(domain)):
                coverage = sum((truth_law[x] for x in values), F(0))
                if coverage < 1 - alpha:
                    errors.append("ConfidenceSet:COVERAGE_PREMISE_FALSE")
    elif tag == "PredictiveLaw":
        domain = obj.get("domain", ())
        if not _unique_nonempty(domain) or not _prob_law(obj.get("law", {}), domain):
            errors.append("PredictiveLaw:NORMALIZED")
    elif tag == "LatentPredictiveModel":
        theta = obj.get("theta", ())
        outcomes = obj.get("outcomes", ())
        if not _unique_nonempty(theta) or not _unique_nonempty(outcomes):
            errors.append("LatentPredictiveModel:DOMAINS")
        if not _prob_law(obj.get("pi", {}), theta):
            errors.append("LatentPredictiveModel:PI")
        kernels = obj.get("kernels", {})
        if set(kernels) != set(theta):
            errors.append("LatentPredictiveModel:KERNEL_KEYS")
        else:
            for t in theta:
                if not _prob_law(kernels[t], outcomes):
                    errors.append("LatentPredictiveModel:KERNEL_NORMALIZATION")
                    break
    elif tag == "SelectivePrediction":
        values = obj.get("value_set", ())
        coverage = obj.get("coverage")
        risk = obj.get("risk")
        if not isinstance(values, tuple) or not values:
            errors.append("SelectivePrediction:VALUE_SET")
        if type(coverage) is not F or not (0 <= coverage <= 1):
            errors.append("SelectivePrediction:COVERAGE")
        if type(risk) is not F or not (0 <= risk <= 1):
            errors.append("SelectivePrediction:RISK")
    return tuple(errors)


def check_ax4(model: Mapping[str, Any]) -> Tuple[bool, Tuple[str, ...]]:
    errors = []
    objs = model.get("uncertainty_objects", ())
    if not isinstance(objs, tuple) or not objs:
        return False, ("uncertainty:OBJECTS_REQUIRED",)
    tags = [obj.get("tag") for obj in objs]
    for tag in ALLOWED_UNCERTAINTY_TAGS:
        if tag not in tags:
            errors.append(f"uncertainty:MISSING_{tag}")
    for obj in objs:
        errors.extend(_check_uncertainty_object(obj))
    return not errors, tuple(errors)


def check_ax5(model: Mapping[str, Any]) -> Tuple[bool, Tuple[str, ...]]:
    errors = []
    for claim in model.get("scope_claims", ()):
        pair = (claim.get("evidence_scope"), claim.get("claim_scope"))
        if pair not in SUPPORTS:
            errors.append(f"scope:UNSUPPORTED:{pair[0]}->{pair[1]}")
        if claim.get("claim") in FORBIDDEN_PROMOTIONS:
            errors.append(f"scope:FORBIDDEN_PROMOTION:{claim.get('claim')}")
    return not errors, tuple(errors)


def check_axioms(model: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    checks = {
        "AX-1": check_ax1(model),
        "AX-2": check_ax2(model),
        "AX-3": check_ax3(model),
        "AX-4": check_ax4(model),
        "AX-5": check_ax5(model),
    }
    return {key: {"ok": ok, "errors": list(errors)} for key, (ok, errors) in checks.items()}


def axioms_green(model: Mapping[str, Any]) -> bool:
    return all(row["ok"] for row in check_axioms(model).values())


def behavioral_partition(model: Mapping[str, Any]) -> Tuple[Tuple[Any, ...], ...]:
    if not check_ax1(model)[0] or not check_ax2(model)[0]:
        raise ValueError("behavioral partition requires AX-1/AX-2")
    states = tuple(model["states"])
    actions = tuple(model["actions"])
    blocks = [set(states)]
    while True:
        cls = {s: i for i, block in enumerate(blocks) for s in block}
        groups: Dict[Tuple[Any, ...], set] = {}
        for s in states:
            sig = (model["output"][s],) + tuple(cls[model["transition"][(s, a)]] for a in actions)
            groups.setdefault(sig, set()).add(s)
        new = sorted(groups.values(), key=lambda b: repr(sorted(b, key=repr)))
        if {frozenset(b) for b in new} == {frozenset(b) for b in blocks}:
            return tuple(tuple(sorted(b, key=repr)) for b in new)
        blocks = new


def behavior_relation(model: Mapping[str, Any]) -> set[Tuple[Any, Any]]:
    rel = set()
    for block in behavioral_partition(model):
        for x in block:
            for y in block:
                rel.add((x, y))
    return rel


def check_behavior_certificate(model: Mapping[str, Any]) -> Tuple[bool, str]:
    claimed = set(model.get("claimed_behavior_equiv", ()))
    actual = behavior_relation(model)
    if claimed != actual:
        return False, "DEF-BEQ:CERTIFICATE_MISMATCH"
    states = set(model["states"])
    if not all((s, s) in claimed for s in states):
        return False, "DEF-BEQ:NONREFLEXIVE"
    if any((b, a) not in claimed for a, b in claimed):
        return False, "DEF-BEQ:NONSYMMETRIC"
    if any((a, c) not in claimed for a, b in claimed for bb, c in claimed if b == bb):
        return False, "DEF-BEQ:NONTRANSITIVE"
    return True, "GREEN"


def development_reachable(model: Mapping[str, Any]) -> Tuple[Any, ...]:
    states = set(model["states"])
    if any(a not in states or b not in states for a, b in model["development_edges"]):
        raise ValueError("typed development required")
    budget = model.get("development_step_budget", 0)
    reached = {model["initial"]}
    frontier = {model["initial"]}
    for _ in range(budget):
        nxt = {b for a, b in model["development_edges"] if a in frontier}
        reached |= nxt
        frontier = nxt
    return tuple(sorted(reached, key=repr))


def run_word(model: Mapping[str, Any], word: Sequence[Any]) -> Any:
    s = model["initial"]
    for a in word:
        s = model["transition"][(s, a)]
    return model["output"][s]


def capability_value(model: Mapping[str, Any], contract: Mapping[str, Any]) -> F | None:
    if len(contract["budget"]) != len(model["resources"]):
        return None
    if any(r > b for r, b in zip(model["resources"], contract["budget"])):
        return None
    denom = sum((task["weight"] for task in contract["tasks"]), F(0))
    if denom <= 0:
        raise ValueError("capability tasks require positive total weight")
    num = F(0)
    for task in contract["tasks"]:
        if run_word(model, task["word"]) == task["target"]:
            num += task["weight"]
    return num / denom


def check_capability_certificates(model: Mapping[str, Any]) -> Tuple[bool, Tuple[str, ...], Dict[str, Any]]:
    errors = []
    details = {}
    for contract in model["capability_contracts"]:
        value = capability_value(model, contract)
        ceiling = value
        declared = model["capability_certificates"].get(contract["id"])
        if declared != ceiling:
            errors.append(f"DEF-CAP:CERTIFICATE:{contract['id']}")
        impossible = ceiling is None or contract["threshold"] > ceiling
        details[contract["id"]] = {"value": value,"ceiling": ceiling,"threshold": contract["threshold"],"impossible": impossible}
    return not errors, tuple(errors), details


def query_terminal(model: Mapping[str, Any]) -> Dict[str, Any]:
    q = model["query_fixture"]
    values = q["values"]
    if not values:
        return {"terminal": "INCONSISTENT_REGISTERED_ASSUMPTIONS", "values": ()}
    image = tuple(sorted({model["output"][s] for s in values}, key=repr))
    if len(image) == 1:
        return {"terminal": "IDENTIFIED", "values": image}
    return {"terminal": "CANNOT_IDENTIFY", "values": image}


def check_scope_claims(model: Mapping[str, Any]) -> Tuple[bool, Tuple[str, ...]]:
    return check_ax5(model)


def check_model(model: Mapping[str, Any]) -> Dict[str, Any]:
    axioms = check_axioms(model)
    derived_errors = []
    derived = {}
    if all(axioms[x]["ok"] for x in ("AX-1", "AX-2")):
        b_ok, b_msg = check_behavior_certificate(model)
        if not b_ok:
            derived_errors.append(b_msg)
        derived["behavioral_partition"] = behavioral_partition(model)
        derived["behavior_certificate"] = b_msg
        derived["development_reachable"] = development_reachable(model)
        c_ok, c_errors, c_details = check_capability_certificates(model)
        if not c_ok:
            derived_errors.extend(c_errors)
        derived["capability"] = c_details
        derived["query"] = query_terminal(model)
    return {"axioms": axioms,"axioms_green": all(row["ok"] for row in axioms.values()),"derived_green": not derived_errors,"derived_errors": derived_errors,"derived": derived}


def renamed_model(model: Mapping[str, Any]) -> Dict[str, Any]:
    out = deepcopy(model)
    mapping = {"s0": "x", "s1": "y", "s2": "z"}
    out["states"] = tuple(mapping[s] for s in model["states"])
    out["initial"] = mapping[model["initial"]]
    out["transition"] = {(mapping[s], a): mapping[t] for (s, a), t in model["transition"].items()}
    out["output"] = {mapping[s]: y for s, y in model["output"].items()}
    out["intervention_response"] = {(mapping[s], j): y for (s, j), y in model["intervention_response"].items()}
    out["development_edges"] = tuple((mapping[a], mapping[b]) for a, b in model["development_edges"])
    return out


def mechanism_isomorphic(left: Mapping[str, Any], right: Mapping[str, Any], mapping: Mapping[Any, Any]) -> bool:
    if set(mapping) != set(left["states"]) or set(mapping.values()) != set(right["states"]): return False
    if mapping[left["initial"]] != right["initial"]: return False
    if tuple(left["actions"]) != tuple(right["actions"]): return False
    if tuple(left["outputs"]) != tuple(right["outputs"]): return False
    if tuple(left["interventions"]) != tuple(right["interventions"]): return False
    if tuple(left["resources"]) != tuple(right["resources"]): return False
    for s in left["states"]:
        if left["output"][s] != right["output"][mapping[s]]: return False
        for a in left["actions"]:
            if mapping[left["transition"][(s, a)]] != right["transition"][(mapping[s], a)]: return False
        for j in left["interventions"]:
            if left["intervention_response"][(s, j)] != right["intervention_response"][(mapping[s], j)]: return False
    return {(mapping[a], mapping[b]) for a,b in left["development_edges"]} == set(right["development_edges"])


def build_model() -> Dict[str, Any]:
    states = ("s0", "s1", "s2")
    model: Dict[str, Any] = {
        "states": states,"actions": ("stay", "flip"),"outputs": (0, 1),"interventions": ("probe",),"intervention_outputs": (0, 1),"initial": "s0",
        "transition": {("s0", "stay"): "s0", ("s0", "flip"): "s2",("s1", "stay"): "s1", ("s1", "flip"): "s2",("s2", "stay"): "s2", ("s2", "flip"): "s2"},
        "output": {"s0": 0, "s1": 0, "s2": 1},
        "intervention_response": {("s0", "probe"): 0, ("s1", "probe"): 0, ("s2", "probe"): 1},
        "development_edges": (("s0", "s1"), ("s1", "s2")),"development_step_budget": 2,"resources": (F(2), F(1)),
        "capability_contracts": (
            {"id":"achievable","tasks":({"word":(),"target":0,"weight":F(1)},{"word":("flip",),"target":1,"weight":F(1)}),"budget":(F(2),F(1)),"threshold":F(1)},
            {"id":"impossible","tasks":({"word":(),"target":1,"weight":F(1)},),"budget":(F(2),F(1)),"threshold":F(1)},
        ),
        "capability_certificates": {"achievable": F(1), "impossible": F(0)},
        "uncertainty_objects": (
            {"tag":"FeasibleSet","domain":states,"values":("s0","s1")},
            {"tag":"ConfidenceSet","domain":states,"values":("s0","s1"),"alpha":F(1,10),"truth_law":{"s0":F(1,2),"s1":F(1,2),"s2":F(0)}},
            {"tag":"PredictiveLaw","domain":(0,1),"law":{0:F(1,2),1:F(1,2)}},
            {"tag":"LatentPredictiveModel","theta":("t0","t1"),"outcomes":(0,1),"pi":{"t0":F(1,2),"t1":F(1,2)},"kernels":{"t0":{0:F(1),1:F(0)},"t1":{0:F(0),1:F(1)}}},
            {"tag":"SelectivePrediction","value_set":(0,1),"coverage":F(1,2),"risk":F(0)},
        ),
        "query_fixture": {"domain":states,"values":("s0","s2"),"query":"protected_output"},
        "scope_claims": (
            {"id":"model-sat","evidence_scope":"FINITE_MODEL_WITNESS","claim_scope":"FINITE_EXISTENTIAL","claim":CLAIM_CEILING},
            {"id":"bounded-census","evidence_scope":"FINITE_EXHAUSTIVE","claim_scope":"BOUNDED_FINITE","claim":"BOUNDED_SMALL_MODEL_CENSUS"},
            {"id":"finite-theorem","evidence_scope":"ANALYTIC_FINITE","claim_scope":"REGISTERED_FINITE","claim":"FINITE_CORE_THEOREMS"},
        ),
    }
    model["claimed_behavior_equiv"] = tuple(sorted(behavior_relation(model), key=repr))
    return model


def axiom_independence_witnesses() -> Dict[str, Any]:
    base = build_model(); mutations = {}
    m=deepcopy(base); m["development_edges"] += (("OUT","s0"),); mutations["AX-1"]=m
    m=deepcopy(base); del m["transition"][("s0","stay")]; mutations["AX-2"]=m
    m=deepcopy(base); m["resources"]=(F(-1),F(1)); mutations["AX-3"]=m
    m=deepcopy(base); objs=list(m["uncertainty_objects"]); c=dict(objs[1]); c["values"]=("s0","OUT"); objs[1]=c; m["uncertainty_objects"]=tuple(objs); mutations["AX-4"]=m
    m=deepcopy(base); claims=list(m["scope_claims"]); claims[1]=dict(claims[1],claim_scope="UNIVERSAL"); m["scope_claims"]=tuple(claims); mutations["AX-5"]=m
    out={}
    for axiom,candidate in mutations.items():
        checks=check_axioms(candidate); false_axioms=tuple(k for k,v in checks.items() if not v["ok"]); out[axiom]={"false_axioms":false_axioms,"only_target_false":false_axioms==(axiom,)}
    return out


def targeted_hostiles() -> Dict[str, Any]:
    base=build_model(); results={}
    m=deepcopy(base); objs=list(m["uncertainty_objects"]); c=dict(objs[1]); c["values"]=(); objs[1]=c; m["uncertainty_objects"]=tuple(objs); results["empty_positive_confidence"]=check_axioms(m)["AX-4"]
    m=deepcopy(base); m["capability_certificates"]=dict(m["capability_certificates"],achievable=F(1,2)); ok,errs,_=check_capability_certificates(m); results["capability_ceiling_below_attained"]={"ok":ok,"errors":list(errs)}
    m=deepcopy(base); claimed=list(m["claimed_behavior_equiv"]); claimed.remove(("s0","s0")); m["claimed_behavior_equiv"]=tuple(claimed); ok,err=check_behavior_certificate(m); results["malformed_behavior_equivalence"]={"ok":ok,"errors":[err] if not ok else []}
    return results


def bounded_structural_census() -> Dict[str, int]:
    states=(0,1); action="a"; total=satisfying=0; by_failure={ax:0 for ax in ("AX-1","AX-2","AX-3")}; transition_options=(0,1,None); output_options=(0,1,None); resource_options=(F(-1),F(0),F(1)); valid_edges=((0,0),(0,1),(1,0),(1,1)); hostile_edge=("OUT",0); base=build_model()
    for trans_vals in product(transition_options,repeat=2):
        for output_vals in product(output_options,repeat=2):
            for resources in product(resource_options,repeat=2):
                for mask in range(32):
                    total+=1; m=deepcopy(base); m["states"]=states; m["actions"]=(action,); m["outputs"]=(0,1); m["interventions"]=("probe",); m["intervention_outputs"]=(0,1); m["initial"]=0
                    m["transition"]={(0,action):trans_vals[0],(1,action):trans_vals[1]}; m["transition"]={k:v for k,v in m["transition"].items() if v is not None}
                    m["output"]={0:output_vals[0],1:output_vals[1]}; m["output"]={k:v for k,v in m["output"].items() if v is not None}; m["intervention_response"]={(0,"probe"):0,(1,"probe"):1}
                    edges=[valid_edges[i] for i in range(4) if mask&(1<<i)];
                    if mask&16: edges.append(hostile_edge)
                    m["development_edges"]=tuple(edges); m["development_step_budget"]=1; m["resources"]=tuple(resources); checks=check_axioms(m); structural={ax:checks[ax] for ax in ("AX-1","AX-2","AX-3")}
                    for ax,row in structural.items():
                        if not row["ok"]: by_failure[ax]+=1
                    if all(row["ok"] for row in structural.values()): satisfying+=1
    return {"candidates":total,"structurally_satisfying":satisfying,"ax1_failures":by_failure["AX-1"],"ax2_failures":by_failure["AX-2"],"ax3_failures":by_failure["AX-3"]}


def jsonable(x: Any) -> Any:
    if isinstance(x,F): return str(x.numerator) if x.denominator==1 else f"{x.numerator}/{x.denominator}"
    if isinstance(x,dict): return {str(k):jsonable(v) for k,v in x.items()}
    if isinstance(x,(tuple,list,set)): return [jsonable(v) for v in x]
    return x


def build_receipt() -> Dict[str, Any]:
    model=build_model(); checked=check_model(model); renamed=renamed_model(model); iso=mechanism_isomorphic(model,renamed,{"s0":"x","s1":"y","s2":"z"}); independence=axiom_independence_witnesses(); hostiles=targeted_hostiles(); census=bounded_structural_census(); cap=checked["derived"]["capability"]
    return jsonable({"schema":"GMI833FiniteAxiomCoreReceiptV1","issue":854,"parent_issue":833,"claim_ceiling":CLAIM_CEILING,"forbidden_promotions":FORBIDDEN_PROMOTIONS,"axiom_count":len(AXIOMS),"axioms":checked["axioms"],"axioms_green":checked["axioms_green"],"derived_green":checked["derived_green"],"behavioral_partition":checked["derived"]["behavioral_partition"],"behavioral_class_count":len(checked["derived"]["behavioral_partition"]),"development_reachable":checked["derived"]["development_reachable"],"capability":cap,"query":checked["derived"]["query"],"morphology_renaming_isomorphic":iso,"uncertainty_tags":[o["tag"] for o in model["uncertainty_objects"]],"axiom_independence":independence,"targeted_hostiles":hostiles,"bounded_structural_census":census,"terminal":"GMI_833_FINITE_AXIOM_CORE_V1_ALL_GREEN" if (checked["axioms_green"] and checked["derived_green"] and iso and all(row["only_target_false"] for row in independence.values()) and census["candidates"]==23328 and census["structurally_satisfying"]==1024) else "RED"})


def main() -> None:
    print(json.dumps(build_receipt(),indent=2,sort_keys=True))


if __name__ == "__main__":
    main()

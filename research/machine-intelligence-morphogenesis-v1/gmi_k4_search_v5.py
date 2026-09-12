from __future__ import annotations

"""K4 V5: DG-10-corrected search plus explicit constant/fixed-function null frontier.

V4 fixed the supplied resource-axis leak. V5 adds the DG-9 / rules-40/42 null requirement before
any protected beacon exists. Search generation/ranking remains exactly V4. Nulls are deterministic
strong parents evaluated after the stochastic search stream, without reading the target property
vector. The target is read only after both search and null audit are frozen.
"""

import copy
import hashlib
import json

import gmi_k4_search as base
import gmi_k4_search_v2 as phase
import gmi_k4_search_v4 as v4
import gmi_k4_resource_native_v4 as rn
import gmi_k4_null_frontier_v5 as nf

THRESHOLD = v4.THRESHOLD
REGISTERED_STOCHASTIC_BUDGET = v4.REGISTERED_STOCHASTIC_BUDGET


def _semantic(cand, task, scale, twin, profile):
    return phase._semantic_adjust(base.semantic_score(cand.as_form(), task, scale, twin), cand.as_form(), task, twin, profile)


def _target_independent_null_digest(audit):
    body=[]
    for r in audit["rows"]:
        body.append([r["null_id"],r["candidate_id"],r["semantic_score"],r["admissible"],r["scalar_lifecycle_cost"],r["measured_property_vector"]])
    return hashlib.sha256(json.dumps(body,sort_keys=True).encode()).hexdigest()


def run_cell(family: str, grammar: str, cell: str, *, freeze: dict, seed: int, budget: int = REGISTERED_STOCHASTIC_BUDGET):
    fr=copy.deepcopy(freeze); fr.pop("name_key",None)
    # V4 performs target-free stochastic search internally; it may read target only after ranking for its own adjudication.
    out=v4.run_cell(family,grammar,cell,freeze=fr,seed=seed,budget=budget)
    out=dict(out); out["schema"]="GMIK4NullAwareMeasuredResourceCellV5"
    if family not in fr.get("families",{}) or grammar not in rn.PREFIX or cell not in ("w1","w2","w4","w8"):
        out["null_frontier"]=None; out["null_search_digest"]=None; return out
    spec=fr["families"][family]; task=base.OBLIGATION_KIND.get(spec["obligation_class"])
    if task is None or out.get("world_profile") is None:
        out["null_frontier"]=None; out["null_search_digest"]=None; return out
    scale=int(cell[1:]); profile=out["world_profile"]
    audit=nf.audit(grammar,task,scale,profile,_semantic,THRESHOLD)
    out["null_frontier"]=audit; out["null_search_digest"]=_target_independent_null_digest(audit)
    out.setdefault("independence",{})["DG-9_NULLS"]="EXPLICIT_CONSTANT_AND_FIXED_FUNCTION_FRONTIER_V5"

    # Target witness exists only after stochastic search and null audit; V4 already constructed it post-ranking.
    witness=out.get("expressibility_witness")
    bestnull=audit.get("best_admissible_null")
    if bestnull is not None and isinstance(witness,dict) and witness.get("expressible"):
        wc=float(witness["scalar_lifecycle_cost"]); nc=float(bestnull["scalar_lifecycle_cost"])
        out["null_vs_target_witness_margin"] = wc - nc  # positive means null cheaper
        if nc < wc - 1e-12:
            out["verdict"]="THEORY_RED_NULL_DOMINATES"
            out["reason"]="an inert hard-coded null is admissible and strictly cheaper than the frozen target witness; registered obligation does not require development"
            out["null_dominating_id"]=bestnull["null_id"]
            out["null_same_vector_as_target"]=bestnull["measured_property_vector"]==spec["property_vector"]
            return out
    else:
        out["null_vs_target_witness_margin"]=None

    # Preserve V4 adjudication otherwise. No V5 GREEN exists below its search cap.
    return out

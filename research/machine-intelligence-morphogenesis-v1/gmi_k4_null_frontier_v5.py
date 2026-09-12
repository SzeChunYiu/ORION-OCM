from __future__ import annotations

"""Explicit null frontier required by PR #445 / DG-9 rules 40/42.

A K4 morphology claim is non-discriminating if an inert realization that never develops can satisfy
the registered obligation more cheaply.  These nulls are not sampled and are not historical family
macros.  They are generic hard-coded parents evaluated under the same semantic constitution:
constant emitter, fixed numeric program, fixed lookup table, fixed verified program, fixed stochastic
sequence generator, and fixed model/planner.

Nulls pay description/state/serve/verification/communication cost.  Their development and
update/retraining cost are set to zero by definition because the target is hard-coded into the
realization.  This makes them strong controls; if such a null wins, the finite registered obligation
did not require development.
"""

import gmi_k4_resource_native_v4 as rn


def _cand(grammar, state, serve, caps=(), routing="none", sharing="shared", retrieval="none",
          iterations="one", stochastic=False, verifier=False, authority=False, locality="none", knob=1):
    return rn.Candidate(grammar, state, serve, tuple(sorted(caps)), routing, sharing, retrieval,
                        iterations, stochastic, verifier, authority, locality, knob)


def null_candidates(grammar: str):
    return {
        "NULL_CONSTANT": _cand(grammar, rn.C(1), rn.C(1)),
        "NULL_FIXED_NUMERIC": _cand(grammar, rn.STATE_REFERENCE["n_features"], rn.SERVE_REFERENCE["n_features"],
                                    ("affine","direct_numeric")),
        "NULL_FIXED_TABLE": _cand(grammar, rn.STATE_REFERENCE["n_records"], rn.SERVE_REFERENCE["log_n_records"],
                                  ("volatile_records",), retrieval="exact_key"),
        "NULL_FIXED_VERIFIED_PROGRAM": _cand(grammar, rn.STATE_REFERENCE["program_size"], rn.SERVE_REFERENCE["search_tree"],
                                             ("program_search","exact_search","constraints"), iterations="one", verifier=True),
        "NULL_FIXED_SEQUENCE_SAMPLER": _cand(grammar, rn.STATE_REFERENCE["vocab_times_context"], rn.SERVE_REFERENCE["sequence_length"],
                                             ("ordered_factorization","sequence_model"), iterations="many", stochastic=True),
        "NULL_FIXED_WORLD_MODEL": _cand(grammar, rn.STATE_REFERENCE["dynamics_model_size"], rn.SERVE_REFERENCE["rollout_depth_times_branch"],
                                        ("world_model","planning"), iterations="many"),
    }


def null_cost(cand, scale: int, profile: dict):
    c = rn.lifecycle(cand, scale, profile)
    c["development_compute"] = 0.0
    c["update_retraining"] = 0.0
    return c


def audit(grammar: str, task: str, scale: int, profile: dict, semantic_fn, threshold: float):
    rows=[]
    for nid,cand in null_candidates(grammar).items():
        score=float(semantic_fn(cand,task,scale,False,profile)); cost=null_cost(cand,scale,profile); total=sum(float(v) for v in cost.values())
        rows.append({"null_id":nid,"candidate_id":cand.cid,"semantic_score":score,"admissible":score>=threshold,
                     "measured_property_vector":cand.vector(),"lifecycle_cost":cost,"scalar_lifecycle_cost":total,
                     "development_compute_forced_zero":True,"update_retraining_forced_zero":True})
    admiss=[r for r in rows if r["admissible"]]
    best=min(admiss,key=lambda r:(r["scalar_lifecycle_cost"],r["null_id"])) if admiss else None
    return {"rows":rows,"best_admissible_null":best,"n_admissible_nulls":len(admiss),
            "interpretation":"If an admissible null is cheaper than the frozen target witness, the registered finite obligation does not discriminate development and the K4 cell is THEORY_RED_NULL_DOMINATES."}

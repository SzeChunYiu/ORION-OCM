"""Research-only donor adapter around unchanged SV.solve. No runtime default or stored KS changes."""
from collections import Counter
from fractions import Fraction
from unittest.mock import patch
from ocm.kso import navigation as N
from ocm.kso import surprise as SP
from ocm.runtime import solve as SV
from representation_donor_fixture import fixture
from representation_donor_policy import prepare, state_binding
from representation_donor_grade import wire, digest


def evaluate(policy, *, arm, revoked=(), task=None, ks=None, config=None):
    if arm not in ("full", "informed_parent", "ocm"):
        raise ValueError("UNREGISTERED_ARM")
    f = policy.fixture
    ks = f["ks"] if ks is None else ks
    task = f["task"] if task is None else task
    cfg = f["config"] if config is None else config
    rv = frozenset(revoked)
    stable = state_binding(ks) == policy.binding and task == f["task"] and cfg == f["config"] and rv in f["revocations"]
    original, surprise_original = N.fixed_point, SP.surprise
    calls, vectors, surprises = [], [], []
    run_counts = Counter()
    n, m = len(ks.ids), len(policy.blocks)

    def call(name, *args):
        run_counts[name] += 1
        group, method = name.split(".")
        return getattr(policy.donors[group], method)(*args)

    def nav(field, seed, alpha, *, revoked=(), relevance=None, mode=N.NavigationMode.WARRANTED, matrix=None):
        R = frozenset(revoked)
        uniform = N.uniform_seed(field)
        kind = "global_uniform" if list(seed) == uniform else "registered_query" if list(seed) == policy.seed else "other"
        bound = stable and state_binding(field) == policy.binding and R == rv and alpha == cfg.alpha and relevance is None and matrix is None and kind != "other"
        eligible = bound and policy.eligibility["warranted"] == "CERTIFIED" and policy.eligibility["exploratory"] == "DYNAMIC_LUMPABILITY_ONLY" and policy.eligibility["reconstruction"] == "EXACT_ZERO_INCIDENT_DECODER"
        query = "EXACT_FINE_NAVIGATION_VALUES"
        routes = [{"name": "full", "supports": [query], "burden": n},
                  {"name": "compact", "supports": [query] if eligible else [], "burden": m}]
        selected = call("router.choose", {"query": query, "routes": routes}, "B0" if arm == "full" else "B2")
        if selected == "compact":
            P = policy.matrices[(R, mode)].as_lists()
            Q = call("f2.quotient", P, policy.blocks)
            gated = N.gated_seed(field, seed, R, mode)
            pushed = call("f2.push", gated, policy.blocks)
            coarse = call("f2.fixed_point", Q, pushed, alpha)
            values = {}
            for b, block in enumerate(policy.blocks):
                for i in block:
                    values[field.ids[i]] = coarse[b] if len(block) == 1 else alpha * gated[i]
        else:
            run_counts["ocm.original_fixed_point"] += 1
            values = original(field, seed, alpha, revoked=R, relevance=relevance, mode=mode, matrix=matrix)
        vectors.append(wire({"mode": mode.value, "seed": list(seed), "alpha": alpha, "revoked": R, "values": values}))
        calls.append({"selected": selected, "mode": mode.value, "seed_kind": kind,
                      "binding": "MATCHED" if bound else "REFINE_REQUIRED_CHANGED_BINDING",
                      "fine_dimension": len(field.ids), "solve_dimension": m if selected == "compact" else len(field.ids)})
        return values

    def observed_surprise(*args, **kwargs):
        result = surprise_original(*args, **kwargs)
        surprises.append(wire(result))
        return result

    # One isolated single-threaded research call only; restored in finally by the context managers.
    with patch.object(N, "fixed_point", nav), patch.object(SP, "surprise", observed_surprise):
        outcome = SV.solve(ks, task, f["operators"], revoked=rv, config=cfg, commit_authority=f["authority"])
    consumer = {"decision": outcome.decision, "answer": outcome.answer, "committed": SV.committed(outcome),
                "trace": outcome.trace.as_dict(), "witness": outcome.witness, "gap_hook": outcome.gap_hook}
    return {"arm": arm, "request": wire({"state": state_binding(ks), "task": task, "config": cfg, "revoked": rv}),
            "consumer": wire(consumer), "vectors": vectors, "surprise": surprises,
            "eligibility": policy.eligibility, "calls": calls,
            "resources": {"donor_calls": dict(run_counts), "preparation_donor_calls": dict(policy.counts),
                          "materialized_matrix_cells": policy.matrix_cells,
                          "fine_output_entries": sum(len(v["values"]) for v in vectors),
                          "exact_rational_outputs": True, "runtime_reported_vector": outcome.trace.resources.as_dict(),
                          "performance_claim": "NOT_TESTED; runtime work proxy unchanged; no process-tree CPU claim"}}

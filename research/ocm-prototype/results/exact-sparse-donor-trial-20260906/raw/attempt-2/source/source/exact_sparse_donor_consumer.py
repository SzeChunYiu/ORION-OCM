"""One isolated research call around unchanged SV.solve; no default injection.

Reference invokes current original behavior without added residual work.
Candidate pays its mandatory original-kernel residual. External parity compares
all complete records. No candidate import, cross-call cache or timers in reference.
Temporary module patching is single-threaded research scope, not runtime API.
"""
from collections import Counter
from unittest.mock import patch
from ocm.kso import navigation as N
from ocm.kso import surprise as SP
from ocm.runtime import solve as SV
from representation_donor_grade import wire


def evaluate(ks, task, operators, *, arm, revoked=(), config=None, commit_authority=None):
    if arm not in ("reference", "sympy"):
        raise ValueError("UNREGISTERED_EXACT_DONOR_ARM")
    original, surprise_original = N.fixed_point, SP.surprise
    vectors, surprises, checks = [], [], []
    if arm == "sympy":
        from exact_sparse_donor import solve_checked

    def nav(field, seed, alpha, *, revoked=(), relevance=None,
            mode=N.NavigationMode.WARRANTED, matrix=None):
        kwargs = dict(revoked=revoked, relevance=relevance, mode=mode, matrix=matrix)
        if arm == "sympy":
            values, check = solve_checked(field, seed, alpha, **kwargs)
        else:
            values = original(field, seed, alpha, **kwargs)
            check = {"route": "CURRENT_FRACTION_REFERENCE", "donor_solve_calls": 0,
                     "independent_residual": "ORIGINAL_BEHAVIOR_NO_ADDED_CHECK"}
        vectors.append(wire({"mode": mode.value, "seed": list(seed), "alpha": alpha,
                             "revoked": frozenset(revoked), "values": values}))
        checks.append(check)
        return values

    def observed_surprise(*args, **kwargs):
        result = surprise_original(*args, **kwargs)
        surprises.append(wire(result))
        return result

    kwargs = dict(revoked=revoked, commit_authority=commit_authority)
    if config is not None:
        kwargs["config"] = config
    with patch.object(N, "fixed_point", nav), patch.object(SP, "surprise", observed_surprise):
        outcome = SV.solve(ks, task, operators, **kwargs)
    consumer = {"status": "COMPLETED", "decision": outcome.decision, "answer": outcome.answer,
                "committed": SV.committed(outcome), "trace": outcome.trace.as_dict(),
                "witness": outcome.witness, "gap_hook": outcome.gap_hook}
    return {"arm": arm, "consumer": wire(consumer), "vectors": vectors,
            "surprise": surprises, "checks": checks,
            "stage_counts": dict(Counter(s.stage.value for s in outcome.trace.stages)),
            "logical_fixed_point_calls": len(vectors),
            "performance_authority": "NOT_TESTED",
            "runtime_work_proxy": "UNCHANGED_REFERENCE_PROXY"}


def main():
    import argparse
    import json
    from representation_donor_fixture import fixture
    parser = argparse.ArgumentParser(description="Untimed named development fixture control")
    parser.add_argument("--arm", required=True, choices=("reference", "sympy"))
    parser.add_argument("--fixture", default="base", choices=("base", "incoming", "mixed_warrant", "alternative"))
    args = parser.parse_args()
    f = fixture(args.fixture)
    result = evaluate(f["ks"], f["task"], f["operators"], arm=args.arm,
                      config=f["config"], commit_authority=f["authority"])
    print(json.dumps(result, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()

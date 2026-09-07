"""Executable engineering demonstration: methods -> generator -> maths -> experiment plan."""
import argparse
import json
from pathlib import Path
import tempfile

from ocm.learning import methods as M
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.science.finite_identification import ModelClass, Observation, ExperimentLearner


def evaluate(root):
    # These are explicit mathematical specifications, not examples relabelled as proof.
    training_tasks = (M.PolynomialTask("shift-square-increment", (2, 2, 1)),
                      M.PolynomialTask("shift-square-double", (2, 4, 2)))
    held_out = (M.PolynomialTask("shift-square-decrement", (0, 2, 1)),
                M.PolynomialTask("fourth-power-of-shift", (1, 4, 6, 4, 1)))
    training = tuple((task, M.solve(task)) for task in training_tasks)
    rt = OCMRuntime(root)
    receipt = M.admit_generator(rt, training, held_out)
    restarted = OCMRuntime(root)
    method = M.load_generator(restarted, receipt["generator_id"])
    queries = ("do(x=0)", "do(x=1)", "do(x=2)")
    programs = (("square",), ("inc", "square"), ("square", "inc"))
    models = ModelClass(queries, tuple((str(i), tuple(str(M.execute(p, x)) for x in (0, 1, 2))) for i, p in enumerate(programs)))
    science = []
    for name, outcomes in models.predictions:
        learner = ExperimentLearner(models)
        steps = []
        for i in range(len(models.predictions) - 1):
            decision = learner.assess()
            if decision["next_query"] is None:
                break
            q = decision["next_query"]
            outcome = outcomes[queries.index(q)]
            learner.observe(Observation(f"sim:{name}:{i}", q, outcome, "SIMULATED_MODEL_DEMONSTRATION", models.fingerprint))
            steps.append({"query": q, "outcome": outcome})
        science.append({"simulated_truth": name, "experiments": steps, "assessment": learner.assess()})
    rt = restarted
    rt.revoke([receipt["training"][0]["evidence_id"]])
    try:
        M.load_generator(OCMRuntime(root), receipt["generator_id"])
    except ValueError:
        revocation = "REUSE_REFUSED_AFTER_RESTART"
    else:
        raise RuntimeError("revoked generator was reused")
    return {"schema": "ocm.method-learning-engineering.v1", "status": "ENGINEERING_DEMONSTRATION",
            "training": [r.as_dict() for _, r in training], "learned_fragments": method.fragments,
            "validation": receipt["validation"], "persistent_generator": receipt["generator_id"],
            "revocation": revocation, "science": science,
            "convergence": "Finite total grammar with fair fallback; deterministic separating experiments within the declared class",
            "external_science": "NOT_RUN", "general_intelligence": "NOT_ESTABLISHED"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    if args.out and (args.out.exists() or args.out.is_symlink()):
        parser.error("choose a new engineering output path")
    with tempfile.TemporaryDirectory() as root:
        result = evaluate(Path(root))
    if args.out:
        from ocm.evaluation.output import write_result
        write_result(args.out, result)
    else:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Shared G1 vessel: unchanged production executive, two donors, fixed host checks."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path[:0] = [str(REPO / "src"), str(HERE)]

import hashlib
import json
import time
from ocm.kso.ids import content_hash
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.runtime import solve as SV
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel
import clia_checker
import clia_solver
from clia_tasks import validate_task
from g1_field import CLIA, MODEL, SCOPE, archive_path, encode, payload, put, setup, warrant
from syntax_contract import validate as syntax_validate, validate_tokens
from udpipe_donor import predict

CONFIG = SV.SolveConfig(exact_extraction_max_atoms=0)
CATALOGUE = ("syntax:udpipe1", "procedure:cvc5")


def identities():
    files = sorted({*HERE.glob("g1_*.py"), *HERE.glob("clia_*.py"),
                    HERE / "syntax_contract.py", HERE / "udpipe_donor.py",
                    HERE / "vendor/conll18_ud_eval.py",
                    *REPO.glob("src/ocm/**/*.py")})
    return {str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def validate_request(request):
    if not isinstance(request, dict):
        raise ValueError("query must be data")
    if request.get("kind") == "syntax" and set(request) == {"kind", "tokens"}:
        validate_tokens(request["tokens"])
    elif request.get("kind") == "clia" and set(request) == {"kind", "task"}:
        validate_task(request["task"])
    else:
        raise ValueError("unknown request contract or unexpected fields")


def check(runtime, request, output, name):
    if name == CATALOGUE[0] and request["kind"] == "syntax":
        if output.get("status") == "CANNOT_CHECK":
            return {"status": "CANNOT_CHECK", "reason": output.get("reason")}
        model = payload(runtime.state.ks, MODEL)
        if output.get("status") != "PREDICTED" or output.get("model_sha256") != model["sha256"]:
            return {"status": "FAIL", "reason": "MODEL_OR_OUTPUT_BINDING"}
        reason = syntax_validate(output.get("words"), request["tokens"])
        return {"status": "FAIL" if reason else "PASS", "reason": reason,
                "scope": "STRUCTURE_ONLY_NO_GOLD_CORRECTNESS"}
    if name == CATALOGUE[1] and request["kind"] == "clia":
        return clia_checker.check(request["task"], output)
    return {"status": "FAIL", "reason": "NOT_APPLICABLE"}


def catalogue(runtime, query_id, request, checks, fault=None):
    result = []
    for name, root in zip(CATALOGUE, (MODEL, CLIA)):
        def backend(ks, operator_id, context, name=name):
            if name == CATALOGUE[0] and request["kind"] == "syntax":
                model = payload(ks, MODEL)
                return predict(request["tokens"], archive_path(runtime, model["sha256"]), model["sha256"])
            if name == CATALOGUE[1] and request["kind"] == "clia":
                return clia_solver.propose(request["task"])
            return {"status": "NOT_APPLICABLE"}
        def checker(output, name=name):
            receipt = check(runtime, request, output, name)
            checks.append({"operator": name, "phase": "solve", **receipt})
            return SV.Status(receipt["status"])
        result.append(SV.OperatorSpec(name, "g1-v1", backend, (query_id, root), scope=SCOPE,
                                      checker=None if fault == "missing_checker" else checker))
    return tuple(result)


def query(runtime, request, fault=None):
    start = time.perf_counter()
    fixture = identities()
    try:
        validate_request(request)
    except (ValueError, TypeError, KeyError) as exc:
        return {"status": "INPUT_REFUSED", "reason": str(exc), "admitted_id": None}
    qid = "g1:query:" + content_hash(request)
    if qid not in runtime.state.ks.ids:
        _, evidence = runtime.admit_evidence(request, Channel.INSTRUCTION, "public-task", scope=SCOPE)
        put(runtime, qid, request, WarrantProfile.of({evidence}), kind="query_seed")
    checks = []
    operators = catalogue(runtime, qid, request, checks, fault)
    task = SV.Task(qid, (SV.QueryPart(encode(request), "query_seed", (qid, MODEL, CLIA)),), context="g1-pilot")
    before = runtime.state.ks.digest()
    outcome = runtime.solve(task, operators)
    pure = before == runtime.state.ks.digest()
    admitted, selected, claim = None, None, None
    if SV.committed(outcome) and pure and identities() == fixture:
        operator, output, _ = outcome.candidate
        selected = operator.operator_id
        receipt = check(runtime, request, output, selected)
        checks.append({"operator": selected, "phase": "admission", **receipt})
        support = (qid, MODEL if selected == CATALOGUE[0] else CLIA)
        truth = warrant(runtime, support)
        if receipt["status"] == "PASS" and truth.liveness(runtime.state.revoked) is Liveness.LIVE:
            syntax = selected == CATALOGUE[0]
            claim = "MODEL_SUPPORTED_SYNTAX_OBSERVATION" if syntax else "SPECIFICATION_VERIFIED_PROGRAM"
            record = {"claim": claim, "query": request, "output": output, "host_check": receipt,
                      "source_identity": content_hash(fixture), "search_lineage": list(operator.input_atoms)}
            # Syntax means that this model emitted this structurally valid tree,
            # never that the tree is gold-correct. No generic runtime.compose call.
            _, evidence = runtime.admit_evidence(record, Channel.OBSERVATION if syntax else Channel.PROOF,
                "fixed-host-observation" if syntax else "fixed-host-z3", scope=SCOPE, derived_from=truth)
            admitted = "g1:answer:" + content_hash(record)
            put(runtime, admitted, record, truth.meet(WarrantProfile.of({evidence})), support,
                "OBSERVATION" if syntax else "EXACT_CHECKER", "observation" if syntax else "proof")
    runtime.persist()
    final_status = "ADMITTED" if admitted else "NOT_ADMITTED"
    if not admitted and (outcome.decision is SV.Decision.CANNOT_CHECK or
                         (checks and checks[-1]["status"] == "CANNOT_CHECK")):
        final_status = "CANNOT_CHECK"
    return {"status": final_status, "solve_status": outcome.decision.value,
            "admitted_id": admitted, "claim": claim,
            "selected": selected, "answer": outcome.answer if admitted else None,
            "proposal_diagnostic": outcome.answer if not admitted else None, "catalogue": list(CATALOGUE),
            "checks": checks, "trace": outcome.trace.as_dict(), "pure_proposals": pure,
            "source_identity": content_hash(fixture), "query_wall_seconds": time.perf_counter() - start}


def worker(root, command):
    runtime = OCMRuntime(root, config=CONFIG)
    if command["action"] == "setup":
        return setup(runtime, Path(command["model"]), command["training_manifest"])
    if command["action"] == "query":
        return query(runtime, command["request"], command.get("fault"))
    if command["action"] in {"revoke", "reinstate"}:
        if not isinstance(command["evidence"], list) or not all(isinstance(e, str) for e in command["evidence"]):
            raise ValueError("evidence must be a list of complete evidence identifiers")
        getattr(runtime, command["action"])(command["evidence"])
        runtime.persist()
        return {"liveness": {a.atom_id: a.liveness(runtime.state.revoked).value for a in runtime.state.ks.atoms}}
    raise ValueError("unknown fixed host action")


if __name__ == "__main__":
    print(json.dumps(worker(Path(sys.argv[1]), json.loads(sys.argv[2])), sort_keys=True))

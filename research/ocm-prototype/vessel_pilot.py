"""One unchanged SV loop, persistent field and explicit host checked admission."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "research/ocm-n1"), str(HERE)]

import hashlib
from importlib.metadata import version
import json
import os
import resource
import time
from ocm.kso.ids import content_hash
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.runtime import solve as SV
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel
from vessel_state import GEN, LANG, PRIM, SCOPE, encode, payload, put, setup, truth_warrant
from vessel_ops import CATALOGUE, CHECKERS, TRUTH_SUPPORT, make_catalogue

CONFIG = SV.SolveConfig(exact_extraction_max_atoms=0)
C_FILES = ("src/ocm/kso/admission.py", "src/ocm/kso/warrant.py", "src/ocm/kso/types.py",
           "src/ocm/runtime/ocm_runtime.py", "src/ocm/store/ledger.py", "research/ocm-prototype/vessel_ops.py",
           "research/ocm-prototype/vessel_pilot.py")
REUSED_FILES = ("research/ocm-n1/minimal_language_learning.py", "research/ocm-n1/packed_chart.py",
    "src/ocm/learning/methods.py", "src/ocm/language/interpret.py", "src/ocm/language/meaning.py",
    "src/ocm/language/constructions.py", "src/ocm/language/lexicon.py", "src/ocm/language/acquisition.py")


def identities():
    digest = lambda path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
    return {"Pi": digest("src/ocm/runtime/solve.py"), "C_trusted_host_fixture": {p: digest(p) for p in (*C_FILES, *REUSED_FILES)},
        "config": {"exact_extraction_max_atoms": CONFIG.exact_extraction_max_atoms},
        "adapter_source_bytes": sum((HERE / p).stat().st_size for p in ("vessel_state.py", "vessel_ops.py")),
        "reused_implementation_sources": {p: {"sha256": digest(p), "bytes": (ROOT / p).stat().st_size} for p in REUSED_FILES},
        "dependency_versions": {"sympy": version("sympy"), "binding": "declared version; package artifact not hashed"},
        "prior_note": "Listed source bytes account for adapters and reused role template/DSL code separately; not total prior information or process isolation"}


def validate_request(request):
    if not isinstance(request, dict):
        raise ValueError("request must be data")
    if request.get("kind") == "language":
        if set(request) != {"kind", "utterance"} or not isinstance(request["utterance"], str):
            raise ValueError("language query has unexpected fields")
    elif request.get("kind") == "polynomial":
        if set(request) - {"kind", "coefficients", "slots", "max_length"} or "coefficients" not in request:
            raise ValueError("polynomial query has unexpected fields")
        from ocm.learning.methods import PolynomialTask, SearchBudget
        from fractions import Fraction
        PolynomialTask("validation", tuple(Fraction(c) for c in request["coefficients"]))
        SearchBudget(request.get("slots", 1000), request.get("max_length", 4))
    else:
        raise ValueError("unknown typed query")


def query(runtime, request, fault=None):
    start, cpu = time.perf_counter(), time.process_time()
    fixture = identities()
    try:
        validate_request(request)
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        return {"status": "INPUT_REFUSED", "reason": str(exc), "admitted_id": None,
                "catalogue": list(CATALOGUE), "fixture": fixture, "pid": os.getpid(), "trace": None}
    qid = "query:" + content_hash(request)
    if qid not in runtime.state.ks.ids:
        _, evidence = runtime.admit_evidence(request, Channel.INSTRUCTION, "task-input", scope=SCOPE)
        put(runtime, qid, request, WarrantProfile.of({evidence}))
    catalogue = make_catalogue(runtime.state.ks, qid, runtime.state.revoked, fault)
    # All descriptors and all capability roots are offered on every task. No answer
    # or evaluator-selected operator is supplied to the controller or adapters.
    task = SV.Task(qid, (SV.QueryPart(encode(request), "procedure", (qid, LANG, GEN, PRIM)),),
                   context="vessel-pilot")
    before = runtime.state.ks.digest()
    outcome = runtime.solve(task, catalogue)
    pure = before == runtime.state.ks.digest()
    admitted, selected = None, None
    if SV.committed(outcome) and pure and identities() == fixture:
        op, output, _ = outcome.candidate
        selected = op.operator_id
        # Recheck at admission using trusted binding; payload cannot name a checker.
        if CHECKERS[selected](runtime.state.ks, request, output, runtime.state.revoked) is SV.Status.PASS:
            support = (qid, *TRUTH_SUPPORT[selected])
            warrant = truth_warrant(runtime, support)
            if warrant.liveness(runtime.state.revoked) is Liveness.LIVE and all(
                    runtime.state.ks.atom_map()[x].scope.covers("vessel-pilot") for x in support):
                proof = {"query": request, "output": output, "checker": selected,
                         "C_identity": content_hash(fixture["C_trusted_host_fixture"])}
                _, eid = runtime.admit_evidence(proof, Channel.PROOF, "host-fixed-checker",
                    scope=SCOPE, derived_from=warrant)
                admitted = "answer:" + content_hash(proof)
                put(runtime, admitted, {**proof, "search_lineage": list(op.input_atoms)},
                    warrant.meet(WarrantProfile.of({eid})), support, "EXACT_CHECKER")
    runtime.persist()
    return {"status": outcome.decision.value, "selected": selected, "answer": outcome.answer,
        "admitted_id": admitted, "catalogue": [o.operator_id for o in catalogue],
        "trace": outcome.trace.as_dict(), "proxy_resources": outcome.trace.resources.as_dict(),
        "pure_proposals": pure, "fixture": fixture, "pid": os.getpid(), "fault": fault,
        "observed": {"wall_seconds": time.perf_counter() - start, "cpu_seconds": time.process_time() - cpu,
                     "peak_rss_native_units": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}}


def run_study(root):
    from vessel_study import run
    return run(root)


def worker(root, command):
    runtime = OCMRuntime(root, config=CONFIG)
    action = command["action"]
    if action == "setup":
        return {"fixture": setup(runtime), "identity": identities(), "pid": os.getpid()}
    if action == "query":
        return query(runtime, command["request"], command.get("fault"))
    if action in {"revoke", "reinstate"}:
        getattr(runtime, action)(command["evidence"])
        runtime.persist()
        return {"pid": os.getpid(), "liveness": {a.atom_id: a.liveness(runtime.state.revoked).value
                for a in runtime.state.ks.atoms}}
    raise ValueError("unknown host action")


if __name__ == "__main__":
    print(json.dumps(worker(Path(sys.argv[1]), json.loads(sys.argv[2])), sort_keys=True))

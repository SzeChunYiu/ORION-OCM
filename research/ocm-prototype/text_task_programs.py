"""Existing cvc5/checked CLIA descriptors served through the actual OCM solve loop."""
from __future__ import annotations

from copy import deepcopy

from ocm.kso.ids import content_hash
from ocm.kso.warrant import WarrantProfile
from ocm.operators.registry import BackendKind, OperatorSpec
from ocm.runtime import solve as SV

import clia_checker
import clia_reuse_descriptor as D
from clia_reuse_apply import CompiledProgram, check_value
from clia_reuse_support import decode, encode as encode_support
import clia_solver
from clia_tasks import load_task
from g1_field import SCOPE, payload, put
from text_task_contracts import check_ground, signature, validate_semantic

METHOD_PREFIX = "text:method:"
PROGRAM_PREFIX = "text:program:"


def register(runtime, name, version, backend, inputs, support, kind=BackendKind.PROGRAMMATIC):
    op = OperatorSpec(name, version, kind, backend, tuple(inputs),
                      output_type="proof", warrant=support, scope=SCOPE,
                      checker=lambda output: "CANNOT_CHECK")
    key = runtime.register_operator(op)
    return runtime.state.operators.operators[key]


def solve(runtime, qid, registered, check, traces, request=None):
    refs = tuple(dict.fromkeys((qid, *registered.input_atoms)))
    def pure_backend(ks, name, context):
        def state_key():
            state = runtime.state
            return (state.ks.digest(), state.evidence_epoch, state.registry_revision, len(runtime.events))
        before = state_key()
        try:
            return registered.backend(ks, request)
        finally:
            if state_key() != before:
                raise ValueError("proposal backend changed field, evidence, registry or event state")
    operator = SV.OperatorSpec(registered.operator_id, registered.version,
                              pure_backend,
                              refs, scope=SCOPE, warrant=registered.warrant,
                              checker=lambda output: SV.Status(check(output)["status"]))
    task = SV.Task(qid, (SV.QueryPart(qid, "query_seed", refs),), context="g1-pilot")
    before = runtime.state.ks.digest()
    outcome = runtime.solve(task, (operator,))
    traces.append(outcome.trace.as_dict())
    if not SV.committed(outcome) or runtime.state.ks.digest() != before:
        raise ValueError("OCM solve did not commit a pure checked candidate: " + outcome.decision.value)
    return outcome.candidate[1]


def acquire(runtime, semantic, qid, evidence, counters, traces):
    task = load_task(semantic["task_id"])
    support = WarrantProfile.of({evidence["specification"], evidence["reuse_authority"]})
    if not support.is_live(runtime.state.revoked):
        raise ValueError("specification/reuse authority is not live")
    def propose(ks, unused):
        counters["synthesis_calls"] += 1
        return clia_solver.propose(task)
    def verify(output):
        counters["universal_checker_calls"] += 1
        return clia_checker.check(task, output)
    registered = register(runtime, "text:acquire:" + task["task_sha256"],
                          D.digest(D.checker_prior()), propose, ("text:specification:" + semantic["task_id"],
                          "text:reuse_authority:" + semantic["task_id"]), support, kind=BackendKind.SEARCH)
    proposal = solve(runtime, qid, registered, verify, traces)
    # Descriptor creation invokes the independent universal checker again for admission.
    counters["universal_checker_calls"] += 1
    desc = D.create(task, proposal, encode_support(support))
    aid = PROGRAM_PREFIX + desc["id"]
    put(runtime, aid, {"descriptor": desc, "discovery_query": qid}, support,
        ("text:specification:" + semantic["task_id"], "text:reuse_authority:" + semantic["task_id"]),
        "EXACT_CHECKER", "procedure")
    binding = {"task_sha256": task["task_sha256"], "signature": signature(task),
               "program_id": desc["id"], "program_atom": aid}
    put(runtime, METHOD_PREFIX + task["task_sha256"], binding, support, (aid,), "EXACT_CHECKER", "procedure")
    return desc


def obtain(runtime, semantic, qid, evidence, counters, traces):
    """Exact specification AND signature dispatch; absence in this registered table only."""
    validate_semantic(semantic)
    support = WarrantProfile.of({evidence["specification"], evidence["reuse_authority"]})
    if not support.is_live(runtime.state.revoked):
        raise ValueError("specification/reuse authority is not live; explicit reinstatement required")
    mid = METHOD_PREFIX + semantic["task_sha256"]
    if mid not in runtime.state.ks.atom_view:
        return acquire(runtime, semantic, qid, evidence, counters, traces), False
    binding = payload(runtime.state.ks, mid)
    atom = runtime.state.ks.atom_view[mid]
    if not atom.is_live(runtime.state.revoked):
        raise ValueError("registered method is not live; no silent replacement")
    if binding["task_sha256"] != semantic["task_sha256"] or binding["signature"] != semantic["signature"]:
        raise ValueError("method index semantic identity/signature mismatch")
    desc = D.validate(payload(runtime.state.ks, binding["program_atom"])["descriptor"])
    if (desc["id"] != binding["program_id"] or desc["task"]["task_sha256"] != semantic["task_sha256"]
            or signature(desc["task"]) != semantic["signature"]
            or encode_support(runtime.state.ks.atom_view[binding["program_atom"]].warrant) != desc["support"]):
        raise ValueError("program descriptor/semantic/support binding mismatch")
    return desc, True


def apply(runtime, semantic, qid, desc, compiled_cache, counters, traces):
    accepted = payload(runtime.state.ks, qid)["semantic"]
    validate_semantic(accepted)
    if D.digest(semantic) != D.digest(accepted):
        raise ValueError("application meaning differs from the admitted request")
    semantic = accepted
    aid = PROGRAM_PREFIX + desc["id"]
    support = decode(desc["support"]).meet(runtime.state.ks.atom_view[qid].warrant)
    if not support.is_live(runtime.state.revoked):
        raise ValueError("application support is not live")
    request = {"kind": "clia_apply", "program_id": desc["id"], "arguments": list(semantic["arguments"])}
    if desc["id"] not in compiled_cache:
        compiled_cache[desc["id"]] = CompiledProgram(desc)
        counters["compile_calls"] += 1
    compiled = compiled_cache[desc["id"]]
    def execute(ks, requested):
        counters["application_calls"] += 1
        return compiled.apply(deepcopy(requested))
    checks = []
    def verify(output):
        counters["pointwise_checker_calls"] += 1
        program = check_value(desc, request, output)
        specification = {"status": "NOT_RUN"}
        if program["status"] == "PASS":
            counters["ground_spec_checker_calls"] += 1
            specification = check_ground(load_task(semantic["task_id"]), semantic["arguments"], output["value"])
        receipt = {"status": specification["status"] if program["status"] == "PASS" else program["status"],
                   "program_application": program, "source_specification": specification}
        checks.append(receipt)
        return receipt
    # Query-bound host callable is registered explicitly after restart, never deserialized.
    registered = register(runtime, "text:apply:" + desc["id"],
                          D.digest(desc["checker_prior"]), execute, (aid,), decode(desc["support"]))
    try:
        output = solve(runtime, qid, registered, verify, traces, request)
    except ValueError as exc:
        if any(c["source_specification"]["status"] not in {"PASS", "NOT_RUN"} for c in checks):
            raise ValueError("returned value does not pass the independent source specification") from exc
        raise
    checked = verify(output)
    if checked["status"] != "PASS":
        raise ValueError("independent application admission check failed")
    record = {"claim": "SPECIFICATION_VERIFIED_APPLICATION", "request": request,
              "output": output, "check": checked, "program_sha256": desc["program_sha256"]}
    answer_id = "text:checked-value:" + content_hash(record)
    put(runtime, answer_id, record, support, (qid, aid), "EXACT_CHECKER", "proof")
    return output["value"], answer_id, checks

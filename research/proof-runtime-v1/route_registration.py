"""One exact task in KSO; discovery/applicability and formal correctness are distinct."""
from ocm.kso.space import Atom, Hyperedge
from ocm.kso.types import Scope
from ocm.kso.warrant import WarrantProfile
from route_data import evidence_spec, put_evidence, durable_json, hashed, host_sources
from session_bindings import canonical


def register(rt, session, root):
    if session.readiness["terminal"] != "READY": raise ValueError("closed session unavailable")
    env = session.environment_id; scope = Scope.of(env)
    descriptor = session.task
    base = {"schema": "ocm.mechanical-proof-registration.v1", "runtime_root": str(rt.root.resolve()),
            "task": descriptor, "task_sha256": session.task_sha256, "environment_id": env,
            "session_bindings": session.bindings, "host_sources": host_sources()}
    eid = "proof-task:" + hashed(base)
    discovery = evidence_spec(rt, {"registration": base, "role": "discovery_and_applicability"},
                              "instruction", eid, scope)
    environment = evidence_spec(rt, {"bindings": session.bindings, "role": "checker_environment_assumption"},
                                "imported", "checker-environment:" + env, scope)
    put_evidence(rt, discovery); put_evidence(rt, environment)
    w = rt.state.evidence.citation_warrant([discovery["id"]])
    request = Atom(eid + ":request", "claim", w, scope=scope, quarantined=True,
                   content_ref=session.task_sha256)
    proc = Atom(eid + ":procedure", "procedure", w, scope=scope, content_ref=session.task_sha256,
                meta=(("descriptor_json", canonical(descriptor).decode()), ("environment_id", env)))
    edge = Hyperedge(eid + ":registered", (request.atom_id,), (proc.atom_id,), "COMPOSITION",
                     warrant=WarrantProfile.one(), scope=scope)
    items = [{"atom": request.as_dict(), "edges": [], "certificate": "INSTRUCTION"},
             {"atom": proc.as_dict(), "edges": [edge.as_dict()], "certificate": "INSTRUCTION"}]
    rt.admit_batch(((request, (), "INSTRUCTION"), (proc, (edge,), "INSTRUCTION")))
    goal = eid + ":goal"
    rt.compose((proc.atom_id,), goal, head_type="goal", bridge_warrant=WarrantProfile.partial(()))
    result = {**base, "discovery_id": discovery["id"], "environment_evidence_id": environment["id"],
              "discovery": discovery, "environment": environment, "registration_items": items,
              "procedure_id": proc.atom_id, "goal_id": goal}
    durable_json(root / "registration.json", result)
    return result

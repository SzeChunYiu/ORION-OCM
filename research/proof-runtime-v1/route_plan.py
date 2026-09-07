"""Fixed atomic claim plan authorized only by a freshly issued matching check."""
from ocm.kso.space import Atom, Hyperedge
from ocm.kso.types import Scope
from ocm.kso.warrant import WarrantProfile, Liveness
from pathlib import Path
import json
from route_data import evidence_spec, artifact_seal, hashed, clone, encoded


def make_plan(view, proposal, handle):
    reg = view.registration; session = view.session; rt = view.rt
    if session is None or not session.authentic_for(handle, reg["task_sha256"],
                        hashed(proposal["candidate"]), reg["environment_id"]):
        raise ValueError("fresh matching session-issued kernel check required")
    if handle["proposal_id"] != proposal.get("proposal_id") or handle["terminal"] != "KERNEL_PASS":
        raise ValueError("proposal/check identity mismatch")
    checked_proposal = json.loads((Path(handle["record_path"]).parent / "requested-proposal.json").read_bytes())
    if encoded(checked_proposal) != encoded(proposal): raise ValueError("checked proposal body changed")
    env_id = reg["environment_evidence_id"]
    env = rt.state.evidence.records[env_id]
    if not env.is_assumption: raise ValueError("registered checker environment must be an assumption")
    scope = Scope.of(reg["environment_id"]); run = handle["run_id"]
    artifacts, trees = artifact_seal(session, proposal, handle)
    body = {"run_id": run, "handle": handle, "task": reg["task"], "candidate": proposal["candidate"],
            "correctness_environment": env_id, "discovery_provenance": [reg["discovery_id"]]}
    run_spec = evidence_spec(rt, body, "proof", "checked-run:" + run, scope)
    if run_spec["id"] in rt.state.evidence.records: raise ValueError("run evidence already exists")
    support = WarrantProfile.of({run_spec["id"], env_id})
    effective = rt.state.nogoods.filter_interval(support)
    effective = rt.state.evidence.nogoods.filter_interval(effective)
    if effective.liveness(rt.state.revoked | rt.state.evidence.revoked) is not Liveness.LIVE:
        raise ValueError("correctness support not live")
    derived = evidence_spec(rt, {"candidate": proposal["candidate"], "task": reg["task"], "run_id": run},
                            "proof", "checked-derivation:" + run, scope, support)
    prefix = "checked:" + run
    anchor = Atom(prefix + ":anchor", "claim", support, scope=scope, quarantined=True,
                  content_ref=run_spec["id"])
    proof = Atom(prefix + ":proof", "proof", support, scope=scope, content_ref=derived["id"])
    claim = Atom(prefix + ":claim", "claim", support, scope=scope, content_ref=reg["task_sha256"],
                 meta=(("goal_id", reg["goal_id"]), ("run_id", run)))
    items = [{"atom": anchor.as_dict(), "edges": [], "certificate": "EXACT_CHECKER"}]
    for tail, head in ((anchor, proof), (proof, claim)):
        edge = Hyperedge(head.atom_id + ":support", (tail.atom_id,), (head.atom_id,), "COMPOSITION",
                         warrant=WarrantProfile.one(), scope=scope)
        items.append({"atom": head.as_dict(), "edges": [edge.as_dict()], "certificate": "EXACT_CHECKER"})
    return clone({"schema": "ocm.checked-route-plan.v1", "run_id": run,
        "registration_sha256": hashed(reg), "predecessor": rt.events[-1].event_hash if rt.events else None,
        "runtime_ledger_head": rt._ledger_head, "candidate": proposal["candidate"], "handle": handle,
        "task_sha256": reg["task_sha256"], "environment_id": reg["environment_id"],
        "run_evidence_id": run_spec["id"], "claim_id": claim.atom_id, "proof_id": proof.atom_id,
        "evidence": [run_spec, derived], "items": items, "artifacts": artifacts, "artifact_trees": trees})

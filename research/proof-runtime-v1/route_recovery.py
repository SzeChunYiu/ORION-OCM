"""Explicit exact-prefix recovery: status never repairs or re-verifies a proof."""
from route_data import encoded, put_evidence, check_evidence, check_items, batch_items, check_artifacts
from route_journal import append, routes, writer


def expected_events(plan):
    return [("EVIDENCE_ADMITTED", e["event_payload"]) for e in plan["evidence"]] + [
        ("OBJECT_BATCH_ADMITTED_V1", {"schema": "ocm.object-admission-batch.v1", "items": plan["items"]})]


def events_after(rt, plan):
    if plan["predecessor"] is None: return rt.events
    positions = [i for i, e in enumerate(rt.events) if e.event_hash == plan["predecessor"]]
    if len(positions) != 1: raise ValueError("authorized OCM predecessor unavailable")
    return rt.events[positions[0] + 1:]


def check_sequence(actual, expected):
    if len(actual) > len(expected): raise ValueError("intervening OCM events")
    for event, (kind, payload) in zip(actual, expected):
        if event.event_type.value != kind or event.status.value != "PASS" or encoded(event.payload) != encoded(payload):
            raise ValueError("intervening/changed OCM event")


def check_committed(view, route):
    plan = route["plan"]; commit = route["commit"]
    if commit is None: raise ValueError("prepared route requires explicit recovery")
    check_artifacts(plan)
    hashes = commit["events"]
    if len(hashes) != 3 or len(set(hashes)) != 3: raise ValueError("incomplete event commitment")
    actual = events_after(view.rt, plan)[:3]
    if [e.event_hash for e in actual] != hashes: raise ValueError("committed event identity changed")
    check_sequence(actual, expected_events(plan))
    for spec in plan["evidence"]: check_evidence(view.rt, spec)
    check_items(view.rt, plan["items"])


def recover(view, run_id):
    with writer(view.root):
        entries = routes(view)
        matching = [r for r in entries if r["plan"]["run_id"] == run_id]
        if len(matching) != 1: raise ValueError("unknown issued run")
        route = matching[0]; plan = route["plan"]
        if route["commit"] is not None:
            check_committed(view, route); return route
        check_artifacts(plan)
        actual = events_after(view.rt, plan); expected = expected_events(plan)
        check_sequence(actual, expected)
        for i, spec in enumerate(plan["evidence"]):
            if i < len(actual): check_evidence(view.rt, spec)
            else:
                if spec["id"] in view.rt.state.evidence.records:
                    raise ValueError("unbound pre-existing run evidence")
                put_evidence(view.rt, spec)
                view.fault(("run_evidence", "derived_evidence")[i])
        if len(actual) < 3:
            view.rt.admit_batch(batch_items(plan["items"])); view.fault("batch")
        check_items(view.rt, plan["items"]); check_artifacts(plan)
        actual = events_after(view.rt, plan); check_sequence(actual, expected)
        payload = {"run_id": run_id, "prepare_hash": route["prepare_hash"],
                   "events": [e.event_hash for e in actual]}
        append(view, "COMMITTED", payload, "commit:" + run_id)
        view.fault("committed")
        return {**route, "commit": payload}

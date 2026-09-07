"""Complete serialized bindings; inherited OCM epoch Infinity encoding is preserved."""
import json
import os
from pathlib import Path
from hashlib import sha256
from ocm.store.canonical import canonical_bytes
from ocm.store.evidence import Channel, EvidenceRecord
from ocm.kso.ids import content_hash, evidence_id
from ocm.kso.types import Authority
from ocm.runtime.ocm_runtime import _wp, _scope, _atom_from, _edge_from
from session_bindings import inventory


def encoded(value): return canonical_bytes(value) + b"\n"
def clone(value): return json.loads(encoded(value))
def hashed(value): return sha256(encoded(value)).hexdigest()


def durable_json(path, value):
    with Path(path).open("xb") as stream:
        stream.write(encoded(value)); stream.flush(); os.fsync(stream.fileno())
    fd = os.open(Path(path).parent, os.O_DIRECTORY)
    try: os.fsync(fd)
    finally: os.close(fd)


def host_sources():
    here = Path(__file__).resolve().parent; repo = here.parent.parent
    paths = list((repo / "src/ocm").rglob("*.py"))
    paths += [here / n for n in ("adapter.py", "route_data.py", "route_registration.py",
                               "route_plan.py", "route_journal.py", "route_recovery.py")]
    return {str(p.relative_to(repo)): sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def evidence_spec(rt, body, channel, source, scope, warrant=None):
    ch = Channel(channel)
    policy = {"scope": scope.as_dict(), "authority": Authority().as_dict(),
              "derived_from": None if warrant is None else warrant.as_dict()}
    payload = {"schema": "ocm.proof-evidence.v1", "body": body, "policy": policy}
    eid = evidence_id(rt.state.evidence.namespace, {"payload": payload, "channel": ch.value, "source": source})
    record = EvidenceRecord(eid, ch, source, content_hash(payload), scope, Authority(), warrant)
    event = {"payload": payload, "channel": ch.value, "source": source, **policy,
             "contradicts": [], "supersedes": None}
    return {"id": eid, "record": record.as_dict(), "event_payload": event}


def check_evidence(rt, spec):
    record = rt.state.evidence.records.get(spec["id"])
    if record is None or encoded(record.as_dict()) != encoded(spec["record"]):
        raise ValueError("evidence identity/policy does not match registered body")
    if not any(e.event_type.value == "EVIDENCE_ADMITTED" and e.status.value == "PASS" and
               encoded(e.payload) == encoded(spec["event_payload"]) for e in rt.events):
        raise ValueError("original evidence payload is unavailable")


def put_evidence(rt, spec):
    if spec["id"] in rt.state.evidence.records:
        check_evidence(rt, spec); return
    p = spec["event_payload"]
    _, eid = rt.admit_evidence(p["payload"], p["channel"], p["source"], scope=_scope(p["scope"]),
                               authority=Authority(), derived_from=_wp(p["derived_from"]))
    if eid != spec["id"]: raise ValueError("evidence identity changed")
    check_evidence(rt, spec)


def check_items(rt, items):
    for item in items:
        aid = item["atom"]["atom_id"]
        if aid not in rt.state.ks.atom_view or encoded(rt.state.ks.atom(aid).as_dict()) != encoded(item["atom"]):
            raise ValueError("registered object body missing or changed")
        if rt.state.certificates.get(aid) != item["certificate"]:
            raise ValueError("certificate label changed")
        for edge in item["edges"]:
            actual = rt.state.ks.edge_view.get(edge["edge_id"])
            if actual is None or encoded(actual.as_dict()) != encoded(edge):
                raise ValueError("registered edge body missing or changed")


def batch_items(items):
    return tuple((_atom_from(i["atom"]), tuple(_edge_from(e) for e in i["edges"]), i["certificate"]) for i in items)


def artifact_seal(session, proposal, handle):
    roots = [session.root / "source-snapshot", Path(proposal["record_path"]).parent,
             Path(handle["record_path"]).parent]
    trees = [{"root": str(p), "files": inventory(p)} for p in roots]
    files = [session.root / n for n in ("session.json", "registered-task.json",
                                       "requested-descriptor.json", "runtime-manifest.json")]
    files += [Path(t["root"]) / n for t in trees for n in t["files"]]
    result = []
    for p in sorted(set(files)):
        if p.is_symlink(): raise ValueError("artifact link")
        data = p.read_bytes()
        with p.open("rb") as stream: os.fsync(stream.fileno())
        result.append({"path": str(p), "bytes": len(data), "sha256": sha256(data).hexdigest()})
    for p in sorted({f.parent for f in files}, key=str):
        fd = os.open(p, os.O_DIRECTORY)
        try: os.fsync(fd)
        finally: os.close(fd)
    return result, trees


def check_artifacts(plan):
    for item in plan["artifacts"]:
        p = Path(item["path"])
        if p.is_symlink() or not p.is_file(): raise ValueError("artifact missing/linked")
        data = p.read_bytes()
        if len(data) != item["bytes"] or sha256(data).hexdigest() != item["sha256"]:
            raise ValueError("artifact bytes changed")
    for tree in plan["artifact_trees"]:
        if inventory(Path(tree["root"])) != tree["files"]: raise ValueError("artifact tree changed")

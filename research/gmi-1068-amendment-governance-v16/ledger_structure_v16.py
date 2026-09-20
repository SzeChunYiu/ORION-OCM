"""Strict append-only structure; validation alone does not establish proof truth."""
import hashlib
import json

FREEZE = "ef27aa6373403d3e9add7571bb97635320d63c50"
CONTRACT_SHA = "faa8f83c0af7a2f0a042e84deb7be191b09a281c08f287c5e986397124177902"
SNAPSHOT = "research/gmi-1068-recursive-audit-v15/SCOPE_SNAPSHOT_V15.json"


def canonical(value):
    def check(item):
        if type(item) is dict:
            if any(type(key) is not str for key in item):
                raise ValueError("JSON object keys must be strings")
            for child in item.values():
                check(child)
        elif type(item) is list:
            for child in item:
                check(child)
        elif item is not None and type(item) not in (str, int, bool):
            raise ValueError("strict JSON types required; no floating aliases")
    check(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def same(left, right):
    return canonical(left) == canonical(right)


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def keys(value, expected):
    if type(value) is not dict or set(value) != set(expected.split()):
        raise ValueError("noncanonical object keys")


def string(value):
    if type(value) is not str or not value.strip():
        raise ValueError("nonempty string required")


def sha(value):
    if type(value) is not str or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise ValueError("SHA256 required")


def sequence(value):
    if type(value) is not list:
        raise ValueError("canonical list required")


def revision_specs(contract):
    return {r["revision_id"]: dict(r, dependency_revision_ids=r.get("dependency_revision_ids", []))
            for r in contract["permitted_revisions"]}


def validate_structure(ledger, trusted_predecessor, target_contract):
    canonical(ledger)
    keys(ledger, "schema control_plane protocol_freeze_commit contract_sha256 original_snapshot previous_ledger targets events")
    if (ledger["schema"] != "GMI_1068_AMENDMENT_LEDGER_V16"
            or type(ledger["control_plane"]) is not int or ledger["control_plane"] != 1068
            or ledger["protocol_freeze_commit"] != FREEZE or ledger["contract_sha256"] != CONTRACT_SHA):
        raise ValueError("ledger authority mismatch")
    expected = {"path": SNAPSHOT, "sha256": target_contract["source_bindings"][SNAPSHOT]}
    if not same(ledger["original_snapshot"], expected) or not same(ledger["targets"], target_contract["original_targets"]):
        raise ValueError("original target or baseline changed")
    sequence(ledger["events"])
    if trusted_predecessor is None:
        if ledger["previous_ledger"] is not None:
            raise ValueError("untrusted predecessor")
    else:
        expected = {"sha256": digest(trusted_predecessor), "event_count": len(trusted_predecessor["events"])}
        if not same(ledger["previous_ledger"], expected):
            raise ValueError("predecessor binding mismatch")
        count = expected["event_count"]
        if not same(ledger["events"][:count], trusted_predecessor["events"]):
            raise ValueError("append-only prefix changed")
        for field in ("schema", "control_plane", "protocol_freeze_commit", "contract_sha256",
                      "original_snapshot", "targets"):
            if not same(ledger[field], trusted_predecessor[field]):
                raise ValueError("predecessor custody changed")
    specs = revision_specs(target_contract)
    targets = {x["original_atom_id"] for x in ledger["targets"]}
    seen, revisions, leaves, attestations, retracted = set(), {}, {}, {}, set()
    previous = None
    for number, event in enumerate(ledger["events"]):
        keys(event, "seq previous_sha256 type id payload")
        if type(event["seq"]) is not int or event["seq"] != number:
            raise ValueError("event sequence mismatch")
        if event["previous_sha256"] != previous:
            raise ValueError("event predecessor digest mismatch")
        string(event["id"])
        if event["id"] in seen:
            raise ValueError("duplicate event identity")
        seen.add(event["id"])
        payload = event["payload"]
        if event["type"] == "REVISION":
            keys(payload, "revision_id original_atom_id supersedes required_statements explicit_changes parent_ownership dependency_revision_ids")
            rid, atom = payload["revision_id"], payload["original_atom_id"]
            if rid not in specs or not same(payload, specs[rid]) or rid in revisions or atom not in targets:
                raise ValueError("revision scope mismatch")
            if payload["supersedes"] != leaves.get(atom, atom):
                raise ValueError("fork, cycle or wrong predecessor")
            sequence(payload["dependency_revision_ids"])
            deps = payload["dependency_revision_ids"]
            if len(deps) != len(set(deps)) or any(dep not in revisions for dep in deps):
                raise ValueError("unknown, forward or cyclic dependency")
            revisions[rid], leaves[atom] = payload, rid
        elif event["type"] == "ATTEST":
            keys(payload, "revision_id kind statement_ids verdict science_sha256 review_sha256")
            rid = payload["revision_id"]
            if rid not in revisions or payload["kind"] != "REFUTATION_AND_REPLACEMENT":
                raise ValueError("attestation target mismatch")
            if not same(payload["statement_ids"], revisions[rid]["required_statements"]):
                raise ValueError("attestation statement scope mismatch")
            if payload["verdict"] not in ("VERIFIED", "FAILED", "CANNOT_CHECK"):
                raise ValueError("invalid evidence verdict")
            sha(payload["science_sha256"])
            sha(payload["review_sha256"])
            if any(a["revision_id"] == rid and key not in retracted
                   for key, a in attestations.items()):
                raise ValueError("ambiguous active attestations")
            attestations[event["id"]] = payload
        elif event["type"] == "RETRACT":
            keys(payload, "attestation_id reason evidence_sha256")
            aid = payload["attestation_id"]
            if aid not in attestations or aid in retracted:
                raise ValueError("unknown or duplicate retraction")
            string(payload["reason"])
            sha(payload["evidence_sha256"])
            retracted.add(aid)
        else:
            raise ValueError("unknown event type")
        previous = digest(event)
    return {"revisions": revisions, "leaves": leaves, "attestations": attestations,
            "retracted": retracted}


def append_event(ledger, event_type, event_id, payload):
    events = ledger["events"]
    events.append({"seq": len(events), "previous_sha256": digest(events[-1]) if events else None,
                   "type": event_type, "id": event_id, "payload": payload})

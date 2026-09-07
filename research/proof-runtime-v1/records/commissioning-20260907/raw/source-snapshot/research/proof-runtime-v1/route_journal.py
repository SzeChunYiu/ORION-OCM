"""Trusted-host issuer custody; consistency checking is not a cryptographic signature."""
from contextlib import contextmanager
import fcntl
import json
from pathlib import Path
from ocm.store.ledger import LedgerStore
from route_data import encoded, hashed, host_sources, check_evidence, check_items


@contextmanager
def writer(root):
    with (root / "writer.lock").open("a") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        try: yield
        finally: fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def append(view, kind, payload, key):
    row = view.journal.append_identified(kind, payload, transaction_id=key, expected_head=view._issuer_head)
    view._issuer_head = row.entry_hash
    return row


def verify(view):
    if not view.journal.path.is_file(): raise ValueError("issuer journal missing")
    rows = view.journal.entries()
    if not rows or rows[0].kind != "REGISTERED": raise ValueError("issuer registration unavailable")
    reg = json.loads((view.root / "registration.json").read_bytes())
    if encoded(reg) != encoded(view.registration) or rows[0].payload["sha256"] != hashed(reg):
        raise ValueError("registration custody changed")
    if reg["runtime_root"] != str(view.rt.root.resolve()): raise ValueError("different OCM ledger identity")
    if reg["host_sources"] != host_sources(): raise ValueError("host source binding changed")
    if view.rt.ledger.verify(): raise ValueError("OCM ledger integrity failure")
    head = view.rt.ledger.head()
    if (head.entry_hash if head else None) != view.rt._ledger_head:
        raise ValueError("OCM instance requires replay")
    check_evidence(view.rt, reg["discovery"]); check_evidence(view.rt, reg["environment"])
    check_items(view.rt, reg["registration_items"])
    return rows


def routes(view):
    rows = verify(view); result = {}
    for row in rows[1:]:
        p = row.payload; run = p["run_id"]
        if row.kind == "PREPARED":
            if run in result or p["plan"]["run_id"] != run or p["sha256"] != hashed(p["plan"]):
                raise ValueError("duplicate/changed route preparation")
            if p["plan"]["registration_sha256"] != hashed(view.registration):
                raise ValueError("route registration differs")
            result[run] = {"plan": p["plan"], "prepare_hash": row.entry_hash, "commit": None}
        elif row.kind == "COMMITTED":
            if run not in result or result[run]["commit"] is not None:
                raise ValueError("unprepared/duplicate route commitment")
            if p["prepare_hash"] != result[run]["prepare_hash"]: raise ValueError("wrong preparation")
            result[run]["commit"] = p
        else: raise ValueError("unregistered issuer record")
    return list(result.values())


def open_existing(root):
    root = Path(root).resolve()
    if not (root / "ledger.jsonl").is_file(): raise ValueError("issuer journal unavailable")
    return root, LedgerStore(root)

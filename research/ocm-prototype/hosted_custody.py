"""Public comparator result/memory custody; no OCM authority or gold access."""
import hashlib
import json
import os
from pathlib import Path
import re

MAX_MEMORY_BYTES = 1024 * 1024
MAX_RECORD_BYTES = 4 * 1024 * 1024


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


class Custody:
    def __init__(self, root):
        self.root = Path(root)
        for name in ("proposals", "finals"):
            (self.root / name).mkdir(exist_ok=True)

    def put(self, kind, request, result):
        record = {"kind": kind, "request": request, "result": result}
        raw = encoded(record)
        if len(raw) > MAX_RECORD_BYTES: raise ValueError("proposal record too large")
        ref = hashlib.sha256(raw).hexdigest()
        path = self.root / "proposals" / (ref + ".json")
        try:
            with path.open("xb") as f: f.write(raw)
        except FileExistsError:
            if path.read_bytes() != raw: raise ValueError("proposal custody collision")
        return ref

    def read(self, ref):
        if not isinstance(ref, str) or re.fullmatch("[0-9a-f]{64}", ref) is None:
            raise ValueError("opaque proposal reference required")
        path = self.root / "proposals" / (ref + ".json")
        if path.is_symlink(): raise ValueError("proposal symlink denied")
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != ref: raise ValueError("proposal custody mismatch")
        return json.loads(raw)

    def memory_read(self):
        p = self.root / "memory.txt"
        if p.is_symlink(): raise ValueError("memory symlink denied")
        raw = p.read_bytes() if p.exists() else b""
        if len(raw) > MAX_MEMORY_BYTES: raise ValueError("memory too large")
        return {"text": raw.decode(), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}

    def memory_write(self, text):
        if not isinstance(text, str): raise ValueError("memory must be text")
        raw = text.encode()
        if len(raw) > MAX_MEMORY_BYTES: raise ValueError("memory too large")
        fd = os.open(self.root / "memory.txt", os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "wb") as f: f.write(raw)
        return self.memory_read()

    def final(self, item, answer, proposal_ref=None):
        from clia_checker import check
        from syntax_contract import validate
        request = item["request"]
        if proposal_ref is not None:
            record = self.read(proposal_ref)
            if record["request"] != request: raise ValueError("proposal belongs to another public item")
            answer = record["result"]
        if not isinstance(answer, dict): raise ValueError("answer object required")
        if request["kind"] == "syntax":
            reason = validate(answer.get("words"), request["tokens"])
            checked = {"status": "PASS" if reason is None else "FAIL", "reason": reason,
                       "claim": "STRUCTURAL_PREDICTION_ONLY"}
        else:
            checked = check(request["task"], answer)
        result = {"item_id": item["id"], "request": request, "answer": answer,
                  "proposal_ref": proposal_ref, "check": checked, "status": "COMMITTED",
                  "claim": "BENCHMARK_OUTPUT_CUSTODY_ONLY"}
        raw = encoded(result)
        if len(raw) > MAX_RECORD_BYTES: raise ValueError("final record too large")
        path = self.root / "finals" / (hashlib.sha256(item["id"].encode()).hexdigest() + ".json")
        try:
            with path.open("xb") as f:
                f.write(raw); f.flush(); os.fsync(f.fileno())
        except FileExistsError:
            raise ValueError("item already committed; final submissions are append-only")
        return {"status": "COMMITTED", "item_id": item["id"], "check": checked,
                "final_sha256": hashlib.sha256(raw).hexdigest(), "proposal_ref": proposal_ref}

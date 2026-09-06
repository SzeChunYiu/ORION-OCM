"""A fixed public-task/native-donor interface; all calls are logged with costs."""
import json
from pathlib import Path
import time
from hosted_custody import Custody, encoded
from clia_tasks import validate_task
from clia_solver import propose
from clia_checker import check
from syntax_contract import validate, validate_tokens
from udpipe_donor import predict

TOOL_NAMES = ("public_task", "syntax_predict", "syntax_check", "clia_synthesize", "clia_check",
              "proposal_read", "memory_read", "memory_write", "final_submit")


class PublicTools:
    def __init__(self, public="/public", memory="/memory"):
        self.public = Path(public)
        items = json.loads((self.public / "items.json").read_text())
        self.items = {x["id"]: x for x in items}
        self.model = json.loads((self.public / "model.json").read_text())["sha256"]
        self.custody = Custody(memory)
        self.journal = Path(memory) / "tool-calls.jsonl"

    def invoke(self, name, **arguments):
        if name not in TOOL_NAMES: raise ValueError("tool not in fixed public interface")
        start = time.perf_counter(); cpu = time.process_time()
        try:
            result = getattr(self, "_" + name)(**arguments)
        except (ValueError, OSError, KeyError, TypeError) as exc:
            result = {"status": "REFUSED", "reason": str(exc)}
        receipt = {"tool": name, "arguments": arguments, "result": result,
                   "wall_seconds": time.perf_counter() - start,
                   "host_cpu_seconds": time.process_time() - cpu,
                   "unmeasured": ["energy", "provider inference costs (captured by actor launcher)"]}
        with self.journal.open("ab") as f: f.write(encoded(receipt) + b"\n")
        return result

    def _public_task(self, item_id):
        if item_id not in self.items: raise ValueError("item not released in this public chunk")
        return self.items[item_id]

    def _syntax_predict(self, tokens):
        validate_tokens(tokens)
        result = predict(tokens, self.public / "model.udpipe", self.model)
        ref = self.custody.put("syntax", {"kind": "syntax", "tokens": tokens}, result)
        return {k: v for k, v in result.items() if k != "words"} | {"proposal_ref": ref}

    def _syntax_check(self, tokens, words=None, proposal_ref=None):
        validate_tokens(tokens)
        if (words is None) == (proposal_ref is None): raise ValueError("choose words or proposal_ref")
        if proposal_ref is not None:
            record = self.custody.read(proposal_ref)
            if record["request"] != {"kind": "syntax", "tokens": tokens}: raise ValueError("proposal token mismatch")
            words = record["result"].get("words")
        reason = validate(words, tokens)
        return {"status": "PASS" if reason is None else "FAIL", "reason": reason,
                "claim": "STRUCTURAL_PREDICTION_ONLY"}

    def _clia_synthesize(self, task, timeout_ms=5000, deadline_s=15):
        validate_task(task)
        result = propose(task, timeout_ms=timeout_ms, deadline_s=deadline_s)
        ref = self.custody.put("clia", {"kind": "clia", "task": task}, result)
        return {k: v for k, v in result.items() if k != "candidate"} | {"proposal_ref": ref}

    def _clia_check(self, task, proposal=None, proposal_ref=None, timeout_ms=5000, deadline_s=10):
        validate_task(task)
        if (proposal is None) == (proposal_ref is None): raise ValueError("choose proposal or proposal_ref")
        if proposal_ref is not None:
            record = self.custody.read(proposal_ref)
            if record["request"] != {"kind": "clia", "task": task}: raise ValueError("proposal task mismatch")
            proposal = record["result"]
        return check(task, proposal, timeout_ms=timeout_ms, deadline_s=deadline_s)

    def _proposal_read(self, proposal_ref):
        return self.custody.read(proposal_ref)

    def _memory_read(self):
        return self.custody.memory_read()

    def _memory_write(self, text):
        return self.custody.memory_write(text)

    def _final_submit(self, item_id, proposal_ref=None, custom_answer=None):
        if (proposal_ref is None) == (custom_answer is None):
            raise ValueError("choose proposal_ref or custom_answer")
        return self.custody.final(self._public_task(item_id), custom_answer, proposal_ref)

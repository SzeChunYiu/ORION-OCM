"""FNA-8/D9 consolidation: assemble the scored receipts into FNA8_RESULTS_V1.json.

Verifies (tamper-evidence) that the frozen code/protocol digests still match, that
the model receipts are CODEX-stamped (never MOCK), that R6 comes from the full
no-model run, then re-evaluates the frozen terminal tree over the combined
evidence. Deterministic; writes one JSON artifact and prints headline numbers.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "src"))

import fna8_world as W                       # noqa: E402
from fna8 import evaluate_terminals, pending_rungs  # noqa: E402


def main() -> int:
    freeze = json.loads((HERE / "FREEZE_FNA8_V1.json").read_text())
    for rel, want in freeze["sha256"].items():
        got = hashlib.sha256((HERE / rel).read_bytes()).hexdigest()
        if got != want:
            raise SystemExit("freeze digest mismatch: %s" % rel)
    r6 = json.loads((HERE / "FNA8_R6_FULL.json").read_text())
    r1_path = HERE / "FNA8_R1_CODEX.json"
    r2_path = HERE / "FNA8_R2_CODEX.json"
    if not r1_path.exists():
        r1_path = HERE / "FNA8_R1_CODEX_INTERFACE_REFUSED.json"
    if not r2_path.exists():
        r2_path = HERE / "FNA8_R2_CODEX_INTERFACE_REFUSED.json"
    r1 = json.loads(r1_path.read_text())
    r2 = json.loads(r2_path.read_text())
    if r6["model_mode"] != "MOCK" or r6["rung6"]["ledgers"]["A1_INCUMBENT"]["capability"]["n"] == 0:
        raise SystemExit("rung6 receipt is not the full no-model run")
    for name, r in (("r1", r1), ("r2", r2)):
        if r["model_mode"] != "CODEX":
            raise SystemExit("%s receipt is not CODEX-stamped" % name)
        if not r.get("codex_version"):
            raise SystemExit("%s receipt missing codex version" % name)

    results = {
        "schema": "ocm.fna.fna8-privilege-ladder.results.v1",
        "salt": W.SALT,
        "freeze": "FREEZE_FNA8_V1.json",
        "rung6_full": r6["rung6"],
        "rung6_splits": r6["splits"],
        "rung1_shadow": r1["rung1"],
        "rung1_model_config": r1["model_config"],
        "rung1_codex_version": r1.get("codex_version"),
        "rung2_shadow": r2["rung2"],
        "rung2_codex_version": r2.get("codex_version"),
        "pending_rungs": pending_rungs(),
        "terminals": evaluate_terminals(r6["rung6"], r1["rung1"], r2["rung2"], "CODEX"),
    }
    from fna8 import _interface_refused
    results["interface_status"] = {
        "rung1": "INTERFACE_REFUSED" if _interface_refused(r1["rung1"]["ledger"]) else "live",
        "rung2": "INTERFACE_REFUSED" if _interface_refused(r2["rung2"]["ledger"]) else "live",
        "probe_evidence": "2026-09-09T19:24Z live probe completed (21,562 tokens, reply FNA8_PROBE_OK); scored window 19:54Z onwards all calls refused",
    }
    blob = json.dumps(results)
    for tok in ("TRANSFORMER_REPLACED", "LLM_EQUIVALENT", "GENERAL_SUPERIORITY", "AGI"):
        if tok in blob:
            raise SystemExit("forbidden token in results: %s" % tok)
    (HERE / "FNA8_RESULTS_V1.json").write_text(json.dumps(results, indent=1, default=str))

    led6 = r6["rung6"]["ledgers"]
    l1, l2 = r1["rung1"]["ledger"], r2["rung2"]["ledger"]
    head = {
        "R6_incumbent": led6["A1_INCUMBENT"]["delivered_correct_rate"],
        "R6_guarded": led6["A2_GUARDED"]["delivered_correct_rate"],
        "R6_guarded_lifetime_work": led6["A2_GUARDED"]["lifetime_logical_work"],
        "R6_incumbent_lifetime_work": led6["A1_INCUMBENT"]["lifetime_logical_work"],
        "R1_model_rate": l1["delivered_correct_rate"],
        "R1_first_pass": l1["capability"]["first_pass"],
        "R1_fallbacks": l1["capability"]["fallbacks"],
        "R1_tokens": l1["model_usage"]["tokens"],
        "R1_calls": l1["model_usage"]["calls"],
        "R1_parse_failures": l1["model_usage"]["parse_failures"],
        "R1_ctrl_failures": sum(1 for row in l1["per_query"] if row.get("ctrl_failure")),
        "R2_rate": l2["delivered_correct_rate"],
        "R2_tokens": l2["model_usage"]["tokens"],
        "terminals": results["terminals"]["rungs"],
    }
    print(json.dumps(head, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())

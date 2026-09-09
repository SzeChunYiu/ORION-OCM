"""FNA-8/D9 model adapter: the ONE place a frontier model is reached.

Two modes, chosen by the driver and recorded in every receipt:
- ``codex``  real frontier-model calls via the pinned local codex CLI
             (``codex exec``, version recorded per run). Parsing of the CLI's
             text tail is conservative; any parse failure is recorded as
             ``parse_failure`` and the query is scored as a control failure —
             nothing is ever repaired, retried into existence, or fabricated.
- ``mock``   a deterministic declared stub used ONLY by the test battery and
             the --tiny smoke path; receipts produced in mock mode are stamped
             ``model_mode: "MOCK"`` and the driver refuses to emit rung
             terminals from them.

Frozen model configuration (FREEZE_FNA8_V1.json): model gpt-5.5,
model_reasoning_effort low, sandbox read-only, workdir an empty directory,
one call per query, timeout 300 s, zero retries.
"""
from __future__ import annotations

import os
import subprocess
import time
from typing import Dict, List, Optional

MODEL_CONFIG = {
    "cli": "codex",
    "subcommand": "exec",
    "model": "gpt-5.5",
    "model_reasoning_effort": "low",
    "sandbox_mode": "read-only",
    "timeout_s": 300,
    "retries": 0,
}


def codex_version() -> str:
    try:
        out = subprocess.run(["codex", "--version"], capture_output=True, text=True,
                             timeout=30)
        return out.stdout.strip() or out.stderr.strip() or "unknown"
    except Exception as exc:  # pragma: no cover - environment-dependent
        return "unavailable: %s" % exc


def _parse_codex_tail(stdout: str) -> Dict:
    """Parse codex exec's text tail: last 'tokens used' block.

    Layout observed on codex-cli 0.129.0-alpha.15 (probe 2026-09-09):
    ``...\\ncodex\\n<message>\\ntokens used\\n<tokens with commas>\\n<message>``.
    Message = last non-empty line strictly before the 'tokens used' line,
    skipping a literal ``codex`` marker line. Failures return parse_failure.
    """
    lines = [ln.rstrip() for ln in stdout.splitlines()]
    idx = None
    for i in range(len(lines) - 1):
        if lines[i].strip().lower() == "tokens used":
            idx = i
    if idx is None:
        return {"parse_failure": "no tokens-used marker"}
    tokens = None
    if idx + 1 < len(lines):
        t = lines[idx + 1].strip().replace(",", "")
        if t.isdigit():
            tokens = int(t)
    message = None
    for j in range(idx - 1, -1, -1):
        s = lines[j].strip()
        if s and s.lower() != "codex":
            message = s
            break
    if tokens is None or message is None:
        return {"parse_failure": "unparseable tokens/message block"}
    return {"tokens": tokens, "message": message}


def call_codex(prompt: str, workdir: str) -> Dict:
    """One real frontier-model call. Returns a receipt; never raises for model
    behaviour (failures are data), only for environment misuse."""
    cmd = ["codex", "exec", "--skip-git-repo-check", "-C", workdir,
           "-c", "model=%s" % MODEL_CONFIG["model"],
           "-c", "model_reasoning_effort=%s" % MODEL_CONFIG["model_reasoning_effort"],
           "-c", "sandbox_mode=%s" % MODEL_CONFIG["sandbox_mode"],
           prompt]
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=MODEL_CONFIG["timeout_s"])
        wall = round(time.time() - t0, 3)
        parsed = _parse_codex_tail(proc.stdout)
        return {
            "ok": proc.returncode == 0 and "parse_failure" not in parsed,
            "returncode": proc.returncode,
            "wall_s": wall,
            "tokens": parsed.get("tokens"),
            "message": parsed.get("message"),
            "parse_failure": parsed.get("parse_failure"),
            "stderr_tail": proc.stderr[-400:] if proc.stderr else "",
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "returncode": None, "wall_s": round(time.time() - t0, 3),
                "tokens": None, "message": None,
                "parse_failure": "timeout", "stderr_tail": ""}
    except FileNotFoundError:
        return {"ok": False, "returncode": None, "wall_s": 0.0, "tokens": None,
                "message": None, "parse_failure": "codex binary not found",
                "stderr_tail": ""}


class MockModel:
    """Deterministic declared stub: cheapest declared EXACT operator + the exact
    answer computed by the world (i.e. it behaves like a perfect controller).
    MOCK ONLY — receipts from mock mode are stamped and never scored."""

    mode = "mock"

    def call(self, prompt: str) -> Dict:
        return {"ok": True, "returncode": 0, "wall_s": 0.0, "tokens": 0,
                "message": None, "parse_failure": None, "stderr_tail": "",
                "mock": True}


class CodexModel:
    mode = "codex"

    def __init__(self, workdir: str) -> None:
        os.makedirs(workdir, exist_ok=True)
        self.workdir = workdir
        self.version = codex_version()

    def call(self, prompt: str) -> Dict:
        return call_codex(prompt, self.workdir)


def make_model(mode: str, workdir: str):
    if mode == "codex":
        return CodexModel(workdir)
    if mode == "mock":
        return MockModel()
    raise ValueError("unknown model mode: %r" % mode)


def mock_controller_reply(q, world) -> str:
    """The mock's declared reply for query q: cheapest declared EXACT op, exact mass."""
    from fna8_world import EXACT_FAMILIES  # local import: capsule module
    best = None
    for inst in world["catalogue"]:
        if inst.family not in EXACT_FAMILIES:
            continue
        if inst.family == "probe" and inst.anchor not in q.slice_ids:
            continue
        est = inst.declared_cost_estimate(q, world["state"])
        if best is None or est < best[0]:
            best = (est, inst)
    op = best[1] if best else [i for i in world["catalogue"] if i.family == "scan"][0]
    m = q.true_mass(world["atoms"])
    if q.task_flag:
        return "CTRL|%s|%s" % (op.op_id, m)
    return "CTRL|%s|%s|%s" % (op.op_id, m, "HIGH" if m >= q.theta_q else "LOW")


def mock_proposal_reply(q, world) -> str:
    """The mock's declared proposal: exact ops first, cheapest declared first."""
    from fna8_world import EXACT_FAMILIES
    exact, approx = [], []
    for inst in sorted(world["catalogue"], key=lambda i: i.declared_cost_estimate(q, world["state"])):
        if inst.family in EXACT_FAMILIES:
            if inst.family == "probe" and inst.anchor not in q.slice_ids:
                continue
            exact.append(inst.op_id)
        else:
            if inst.family in ("window", "sample") and inst.param > q.n:
                continue
            approx.append(inst.op_id)
    ranked = (exact + approx)[:3]
    return "PROP|%s" % "|".join(ranked)

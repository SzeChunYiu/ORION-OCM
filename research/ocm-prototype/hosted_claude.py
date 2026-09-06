"""Claude's exact local tool catalogue, without provider inference or real credentials."""
from __future__ import annotations
import gzip
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import signal
import subprocess
import threading
import time

CLAUDE = Path.home() / ".local/bin/claude"
PIN = "2.1.228 (Claude Code)"
TERMINAL_TOOLS = {"EndConversation"}  # Explicit, non-filesystem protocol exception.
DUMMY_KEY = "LOCAL_CATALOGUE_ONLY_NOT_A_CREDENTIAL"


def command(actor, mcp_config=None, *, model="claude-fable-5", client=CLAUDE, allowed_names=None):
    """Subscription-compatible flags; deliberately no --bare or credential override."""
    args = [str(client), "--print", "--model", model, "--effort", "high",
            "--tools", "", "--strict-mcp-config", "--mcp-config",
            json.dumps(mcp_config or {"mcpServers": {}}),
            "--setting-sources", "", "--disable-slash-commands", "--no-chrome",
            "--no-session-persistence", "--permission-mode", "dontAsk",
            "--settings", json.dumps({"disableAllHooks": True, "autoMemoryEnabled": False}),
            "--system-prompt", "Use only the supplied public tasks and explicitly attached tools.",
            "--output-format", "stream-json", "--verbose"]
    if mcp_config:
        if allowed_names is None:
            from hosted_tools import TOOL_NAMES
            allowed_names = ["mcp__g1__" + n for n in TOOL_NAMES]
        args += ["--allowedTools", ",".join(allowed_names)]
    return args


def catalogue_verdict(tools, expected_names):
    names = [t.get("name", "") for t in tools]
    unexpected = sorted(set(names) - set(expected_names) - TERMINAL_TOOLS)
    missing = sorted(set(expected_names) - set(names))
    return {"passed": not unexpected and not missing and len(names) == len(set(names)),
            "unexpected_tools": unexpected, "missing_tools": missing,
            "terminal_tools": sorted(set(names) & TERMINAL_TOOLS)}


def audit_catalogue(output, *, mcp_config=None, expected_names=(),
                    client=CLAUDE, pin=PIN, model="claude-fable-5"):
    """Local HTTP 400 captures the real Messages tool payload; no inference is run."""
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    actor = output / "actor"; actor.mkdir(exist_ok=True)
    config = output / "synthetic-config"; config.mkdir(exist_ok=True)
    canary = "SYNTHETIC_AMBIENT_CONTEXT_CANARY_20260906"
    (config / "CLAUDE.md").write_text(canary)
    if subprocess.check_output([str(client), "--version"], text=True).strip() != pin:
        raise ValueError("Claude client version mismatch")
    captures = []; errors = []; auth_ok = []
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_): pass
        def do_POST(self):
            try:
                raw = self.rfile.read(int(self.headers.get("Content-Length", "0")))
                if self.headers.get("Content-Encoding") == "gzip": raw = gzip.decompress(raw)
                body = json.loads(raw)
                if "tools" in body:
                    auth_ok.append(self.headers.get("x-api-key") == DUMMY_KEY
                                   or self.headers.get("authorization") == "Bearer " + DUMMY_KEY)
                    captures.append({"tools": body["tools"], "model": body.get("model"),
                                     "context_canary_found": canary in raw.decode(),
                                     "request_sha256": hashlib.sha256(raw).hexdigest()})
            except Exception as exc:
                errors.append(type(exc).__name__)
            reply = b'{"type":"error","error":{"type":"invalid_request_error","message":"LOCAL_CATALOGUE_CAPTURE_ONLY"}}'
            self.send_response(400); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(reply))); self.end_headers(); self.wfile.write(reply)
    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    # Only this local audit replaces auth. The real subscription launch does not.
    env = dict(os.environ)
    for key in ("CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_AUTH_TOKEN",
                "CLAUDE_CODE_USE_BEDROCK", "CLAUDE_CODE_USE_VERTEX", "CLAUDE_CODE_USE_FOUNDRY"):
        env.pop(key, None)
    env.update(ANTHROPIC_API_KEY=DUMMY_KEY, ANTHROPIC_BASE_URL=f"http://127.0.0.1:{server.server_port}",
               CLAUDE_CONFIG_DIR=str(config), DISABLE_AUTOUPDATER="1",
               CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1")
    args = command(actor, mcp_config, client=client, model=model, allowed_names=expected_names); start = time.monotonic(); timeout = False
    try:
        with (output / "stdout.jsonl").open("wb") as out, (output / "stderr.private.log").open("wb") as err:
            os.chmod(err.name, 0o600)
            p = subprocess.Popen(args, cwd=actor, env=env, stdin=subprocess.PIPE,
                                 stdout=out, stderr=err, start_new_session=True)
            try: p.communicate(b"LOCAL TOOL CATALOGUE AUDIT ONLY.\n", timeout=45)
            except subprocess.TimeoutExpired:
                timeout = True; os.killpg(p.pid, signal.SIGKILL); p.wait()
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=2)
    tools = captures[0]["tools"] if captures else []
    verdict = catalogue_verdict(tools, expected_names)
    receipt = {"purpose": "LOCAL_NON_INFERENCE_CATALOGUE", "hosted_inference_requests": 0,
               "captured_requests": len(captures), "tools": tools, "parse_errors": errors,
               "captured_models": [x["model"] for x in captures], "exit_code": p.returncode,
               "outer_timeout": timeout, "wall_seconds": time.monotonic() - start,
               "dummy_auth_verified": bool(auth_ok) and all(auth_ok),
               "ambient_canary_absent": bool(captures) and not any(x["context_canary_found"] for x in captures),
               **verdict, "command": args, "bare_mode": False,
               "request_hashes": [x["request_sha256"] for x in captures],
               "client_version": pin, "requested_model": model}
    receipt["passed"] = (receipt["passed"] and bool(captures) and not errors and not timeout
                         and receipt["dummy_auth_verified"] and receipt["ambient_canary_absent"]
                         and all(catalogue_verdict(x["tools"], expected_names)["passed"] for x in captures))
    (output / "catalogue.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt

"""Pinned reference launch and a local non-inference tool-catalogue gate."""
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

PIN = "codex-cli 0.129.0-alpha.15"
DISABLED = ("apps", "multi_agent", "memories", "shell_tool", "unified_exec",
            "browser_use", "browser_use_external", "computer_use", "image_generation",
            "plugins", "hooks", "shell_snapshot", "tool_search", "tool_suggest",
            "request_permissions_tool", "request_rule", "skill_mcp_dependency_install")


def command(actor, *, mcp_command=None, provider=None):
    """The same tool switches must be used for qualification and real execution."""
    args = ["codex", "exec", "--ignore-user-config", "--ephemeral", "--sandbox", "read-only",
            "-c", 'approval_policy="never"', "-c", 'web_search="disabled"',
            "-c", "include_apply_patch_tool=false", "-c", "tools.view_image=false",
            "-c", "skills.include_instructions=false", "-c", "include_apps_instructions=false",
            "-c", "include_environment_context=false",
            "-m", "gpt-5.5", "-c", 'model_reasoning_effort="high"',
            "-C", str(actor), "--skip-git-repo-check", "--json"]
    for feature in DISABLED:
        args += ["--disable", feature]
    if mcp_command:
        args += ["-c", "mcp_servers.g1.command=" + json.dumps(mcp_command[0]),
                 "-c", "mcp_servers.g1.args=" + json.dumps(mcp_command[1:]),
                 "-c", "mcp_servers.g1.startup_timeout_sec=30",
                 "-c", "mcp_servers.g1.tool_timeout_sec=130"]
    if provider:
        args += ["-c", 'model_provider="local_catalogue_audit"',
                 "-c", 'model_providers.local_catalogue_audit.name="Local catalogue audit"',
                 "-c", "model_providers.local_catalogue_audit.base_url=" + json.dumps(provider),
                 "-c", 'model_providers.local_catalogue_audit.wire_api="responses"',
                 "-c", "model_providers.local_catalogue_audit.requires_openai_auth=false",
                 "-c", "model_providers.local_catalogue_audit.request_max_retries=0",
                 "-c", "model_providers.local_catalogue_audit.stream_max_retries=0"]
    return args + ["-"]


def validate_catalogue(tools, expected_names):
    """Fail closed on every unknown builtin, tool type, duplicate or missing donor."""
    return (isinstance(tools, list) and all(t.get("type") == "function" for t in tools)
            and sorted(t.get("name", "") for t in tools) == sorted(expected_names))


def audit_catalogue(output, *, mcp_command=None, expected_names=()):
    """Capture a request at loopback; return HTTP 400 without invoking any model."""
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    actor = output / "actor"; actor.mkdir(exist_ok=True)
    if subprocess.check_output(["codex", "--version"], text=True).strip() != PIN:
        raise ValueError("pinned CLI version mismatch")
    captures = []; errors = []
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_): pass
        def do_POST(self):
            try:
                raw = self.rfile.read(int(self.headers.get("Content-Length", "0")))
                if self.headers.get("Content-Encoding") == "gzip": raw = gzip.decompress(raw)
                body = json.loads(raw)
                captures.append({"tools": body.get("tools", []), "model": body.get("model"),
                                 "request_sha256": hashlib.sha256(raw).hexdigest()})
            except Exception as exc:
                errors.append(type(exc).__name__)
            response = b'{"error":{"type":"invalid_request_error","message":"LOCAL_CATALOGUE_CAPTURE_ONLY"}}'
            self.send_response(400); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response))); self.end_headers()
            self.wfile.write(response)
    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    args = command(actor, mcp_command=mcp_command,
                   provider=f"http://127.0.0.1:{server.server_port}/v1")
    start = time.monotonic(); timeout = False
    try:
        with (output / "stdout.jsonl").open("wb") as out, (output / "stderr.private.log").open("wb") as err:
            os.chmod(err.name, 0o600)
            p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=out, stderr=err, start_new_session=True)
            try: p.communicate(b"LOCAL TOOL CATALOGUE AUDIT ONLY.\n", timeout=45)
            except subprocess.TimeoutExpired:
                timeout = True; os.killpg(p.pid, signal.SIGKILL); p.wait()
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=2)
    tools = captures[0]["tools"] if captures else []
    receipt = {"purpose": "LOCAL_NON_INFERENCE_CATALOGUE", "provider_requests": 0,
               "captured_requests": len(captures), "tools": tools, "parse_errors": errors,
               "captured_models": [x["model"] for x in captures], "exit_code": p.returncode,
               "outer_timeout": timeout, "wall_seconds": time.monotonic() - start,
               "passed": bool(captures) and not errors and not timeout
               and all(validate_catalogue(x["tools"], expected_names) for x in captures),
               "command": args, "request_hashes": [x["request_sha256"] for x in captures]}
    (output / "catalogue.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt

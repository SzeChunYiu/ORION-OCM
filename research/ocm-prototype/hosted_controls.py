"""Real SDK/native and OS-boundary controls; no hosted model requests."""
import asyncio
from datetime import timedelta
import json
from pathlib import Path
import socket
import subprocess
import time
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from hosted_stage import namespace_command
from hosted_tools import TOOL_NAMES


def decoded(result):
    if result.isError: raise AssertionError(str(result.content))
    if result.structuredContent is not None: return result.structuredContent
    return json.loads(result.content[0].text)


async def exercise(manifest, output, *, transport=None):
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter(); cpu = time.process_time(); raw = []
    cmd = namespace_command(manifest)
    if transport is not None: cmd = transport(cmd)
    params = StdioServerParameters(command=cmd[0], args=cmd[1:])
    async def call(session, name, args):
        r = await session.call_tool(name, args)
        raw.append({"name": name, "arguments": args, "raw": r.model_dump(mode="json")})
        return decoded(r)
    receipt = {"hosted_inference_requests": 0, "source_stage": manifest, "processes": 2, "transport_command": cmd}
    with (output / "mcp-stderr.log").open("w") as err:
        async with stdio_client(params, errlog=err) as (read, write):
            async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=130)) as s:
                await s.initialize(); inventory = await s.list_tools()
                receipt["tool_catalogue"] = [t.model_dump(mode="json") for t in inventory.tools]
                receipt["catalogue_exact"] = sorted(t.name for t in inventory.tools) == sorted(TOOL_NAMES)
                items = json.loads((Path(manifest["root"]) / "public/items.json").read_text())
                syntax = next(x for x in items if x["request"]["kind"] == "syntax")
                clia = next(x for x in items if x["request"]["kind"] == "clia")
                receipt["public_task"] = await call(s, "public_task", {"item_id": syntax["id"]})
                receipt["syntax"] = await call(s, "syntax_predict", {"tokens": syntax["request"]["tokens"]})
                sref = receipt["syntax"]["proposal_ref"]
                receipt["syntax_check"] = await call(s, "syntax_check", {"tokens": syntax["request"]["tokens"],
                                                                         "proposal_ref": sref})
                full = await call(s, "proposal_read", {"proposal_ref": sref})
                custom = await call(s, "final_submit", {"item_id": syntax["id"], "custom_answer": full["result"]})
                receipt["custom_answer_allowed"] = custom["status"] == "COMMITTED" and custom["check"]["status"] == "PASS"
                receipt["clia"] = await call(s, "clia_synthesize", {"task": clia["request"]["task"]})
                pref = receipt["clia"]["proposal_ref"]
                receipt["clia_check"] = await call(s, "clia_check", {"task": clia["request"]["task"], "proposal_ref": pref})
                receipt["clia_final"] = await call(s, "final_submit", {"item_id": clia["id"], "proposal_ref": pref})
                duplicate = await call(s, "final_submit", {"item_id": clia["id"], "proposal_ref": pref})
                receipt["duplicate_submit_denied"] = duplicate["status"] == "REFUSED"
                receipt["unknown_item_denied"] = (await call(s, "public_task", {"item_id": "../outside"}))["status"] == "REFUSED"
                receipt["path_reference_denied"] = (await call(s, "proposal_read", {"proposal_ref": "../../outside"}))["status"] == "REFUSED"
                await call(s, "memory_write", {"text": "PUBLIC_MEMORY_CONTROL"})
        async with stdio_client(params, errlog=err) as (read, write):
            async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=130)) as s:
                await s.initialize()
                receipt["memory_reload"] = await call(s, "memory_read", {})
                restored = await call(s, "proposal_read", {"proposal_ref": pref})
                receipt["proposal_reload"] = restored["result"]["status"] == "SOLUTION"
    receipt["wall_seconds"] = time.perf_counter() - start
    receipt["host_cpu_seconds"] = time.process_time() - cpu
    receipt["state_bytes"] = sum(p.stat().st_size for p in Path(manifest["memory"]).rglob("*") if p.is_file())
    receipt["passed"] = all((receipt["catalogue_exact"], receipt["syntax"]["status"] == "PREDICTED",
        receipt["syntax_check"]["status"] == "PASS", receipt["clia"]["status"] == "SOLUTION",
        receipt["clia_check"]["status"] == "PASS", receipt["clia_final"]["status"] == "COMMITTED",
        receipt["memory_reload"]["text"] == "PUBLIC_MEMORY_CONTROL", receipt["custom_answer_allowed"],
        receipt["duplicate_submit_denied"], receipt["unknown_item_denied"],
        receipt["path_reference_denied"], receipt["proposal_reload"]))
    (output / "mcp-calls.json").write_text(json.dumps(raw, indent=2) + "\n")
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


def namespace_controls(manifest, output, *, transport=None):
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    sentinel = output / "synthetic-outside-canary.txt"; sentinel.write_text("SYNTHETIC_OUTSIDE_ONLY")
    link = Path(manifest["memory"]) / "outside-link"
    link.symlink_to(sentinel)
    server = socket.socket(); server.bind(("127.0.0.1", 0)); server.listen()
    host = socket.create_connection(server.getsockname(), timeout=2); host.close()
    port = server.getsockname()[1]
    script = """
import json, socket
from pathlib import Path
checks = {}
checks['public_input_readable'] = isinstance(json.loads(Path('/public/items.json').read_text()), list)
for name, path in [('outside_unmounted', SENTINEL), ('symlink_escape_denied', '/memory/outside-link')]:
    try: Path(path).read_bytes(); checks[name] = False
    except (OSError, PermissionError): checks[name] = True
try: Path('/public/items.json').write_text('UNAUTHORIZED_WRITE'); checks['public_write_denied'] = False
except OSError: checks['public_write_denied'] = True
Path('/memory/control.txt').write_text('PUBLIC_WRITE_CONTROL')
checks['memory_writable'] = Path('/memory/control.txt').read_text() == 'PUBLIC_WRITE_CONTROL'
s = socket.socket(); s.settimeout(1)
try: s.connect(('127.0.0.1', PORT)); checks['host_network_denied'] = False
except OSError: checks['host_network_denied'] = True
s.close()
checks['credential_paths_absent'] = not Path('/home/billy/.claude').exists() and not Path('/home/billy/.codex').exists()
checks['repo_path_absent'] = not Path(REPO).exists()
print(json.dumps(checks))
""".replace("SENTINEL", repr(str(sentinel))).replace("PORT", str(port)).replace("REPO", repr(str(Path(__file__).resolve().parents[2])))
    start = time.perf_counter()
    cmd = namespace_command(manifest, ["-c", script])
    if transport is not None: cmd = transport(cmd)
    try: r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    finally: server.close()
    checks = json.loads(r.stdout) if r.returncode == 0 else {}
    receipt = {"passed": bool(checks) and all(checks.values()) and r.returncode == 0, "checks": checks,
               "exit_code": r.returncode, "stderr": r.stderr, "wall_seconds": time.perf_counter() - start,
               "host_listener_positive": True, "synthetic_data_only": True, "transport_command": cmd}
    (output / "namespace-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt

"""Exact public-data export and a networkless native MCP mount namespace."""
from __future__ import annotations
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import shutil
import sys
import time

SOURCE = Path(__file__).resolve().parent
MODULES = ("clia_grammar.py", "clia_tasks.py", "clia_solver.py", "clia_checker.py",
           "clia_process.py", "clia_worker.py", "udpipe_donor.py", "syntax_contract.py",
           "vendor/conll18_ud_eval.py", "hosted_tools.py", "hosted_custody.py", "hosted_mcp.py")
PINS = {"mcp": "1.29.1", "cvc5": "1.3.4", "z3-solver": "5.1.0.0",
        "sexpdata": "1.0.2", "ufal.udpipe": "1.4.0.1"}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""): h.update(b)
    return h.hexdigest()


def validate_items(items):
    from clia_tasks import validate_task
    from syntax_contract import validate_tokens
    if not isinstance(items, list) or not items: raise ValueError("public item list required")
    ids = set()
    for row in items:
        if not isinstance(row, dict) or set(row) != {"id", "request"}:
            raise ValueError("only explicit public id/request fields allowed")
        if not isinstance(row["id"], str) or not row["id"] or row["id"] in ids:
            raise ValueError("unique public item IDs required")
        ids.add(row["id"]); r = row["request"]
        if not isinstance(r, dict): raise ValueError("request object required")
        if r.get("kind") == "syntax" and set(r) == {"kind", "tokens"}:
            validate_tokens(r["tokens"])
        elif r.get("kind") == "clia" and set(r) == {"kind", "task"}:
            validate_task(r["task"])
        else: raise ValueError("unknown fields or domain in public request")
    return items


def stage(items, model_path, model_sha256, output, *, memory_dir=None):
    start = time.perf_counter(); cpu = time.process_time()
    validate_items(items); model_path = Path(model_path).resolve()
    if sha(model_path) != model_sha256: raise ValueError("model custody mismatch")
    actual = {k: version(k) for k in PINS}
    if actual != PINS: raise ValueError("pinned native/MCP dependency mismatch")
    output = Path(output).resolve(); output.mkdir(parents=True, exist_ok=False)
    tools = output / "tools"; tools.mkdir()
    files = list(MODULES)
    fixture_manifest = json.loads((SOURCE / "clia_fixtures/manifest.json").read_text())
    files += ["clia_fixtures/manifest.json", "clia_fixtures/NOTICE.md"]
    files += ["clia_fixtures/" + x["file"] for x in fixture_manifest["fixtures"].values()]
    for rel in files:
        src = SOURCE / rel
        if src.is_symlink(): raise ValueError("source symlink not permitted")
        dst = tools / rel; dst.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(src, dst)
    public = output / "public"; public.mkdir()
    (public / "items.json").write_text(json.dumps(items, ensure_ascii=False, sort_keys=True) + "\n")
    shutil.copyfile(model_path, public / "model.udpipe")
    (public / "model.json").write_text(json.dumps({"sha256": model_sha256}) + "\n")
    memory = Path(memory_dir).resolve() if memory_dir is not None else output / "memory"
    memory.mkdir(parents=True, exist_ok=True)
    if memory.is_symlink(): raise ValueError("memory root symlink not permitted")
    manifest = {"kind": "HOSTED_NATIVE_PUBLIC_STAGE", "root": str(output), "memory": str(memory),
                "model_sha256": model_sha256, "model_bytes": model_path.stat().st_size,
                "public_item_ids": [r["id"] for r in items], "versions": actual,
                "source": {rel: {"sha256": sha(tools / rel), "bytes": (tools / rel).stat().st_size}
                           for rel in files},
                "public_items_sha256": sha(public / "items.json"),
                "python_base": str(Path(sys.base_prefix).resolve()),
                "environment": str(Path(sys.prefix).resolve()), "python_version": sys.version,
                "python_name": Path(sys.executable).resolve().name,
                "stage_wall_seconds": time.perf_counter() - start,
                "stage_cpu_seconds": time.process_time() - cpu,
                "unmeasured": ["environment installation/development", "energy", "OS cache costs"]}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    manifest["command"] = namespace_command(manifest)
    return manifest


def namespace_command(manifest, python_args=None):
    root = Path(manifest["root"])
    args = ["/usr/bin/env", "-i", "/usr/bin/bwrap", "--unshare-all", "--die-with-parent", "--new-session",
            "--cap-drop", "ALL", "--ro-bind", "/usr", "/usr",
            "--symlink", "usr/bin", "/bin", "--symlink", "usr/lib", "/lib",
            "--symlink", "usr/lib64", "/lib64", "--proc", "/proc", "--dev", "/dev",
            "--tmpfs", "/tmp", "--ro-bind", manifest["python_base"], "/runtime",
            "--ro-bind", manifest["environment"], "/env",
            "--ro-bind", str(root / "tools"), "/tools",
            "--ro-bind", str(root / "public"), "/public",
            "--bind", manifest["memory"], "/memory",
            "--setenv", "PATH", "/usr/bin:/bin",
            "--setenv", "PYTHONPATH", "/tools:/env/lib/python3.13/site-packages",
            "--setenv", "PYTHONDONTWRITEBYTECODE", "1", "--setenv", "PYTHONNOUSERSITE", "1",
            "--setenv", "LC_ALL", "C.UTF-8", "--chdir", "/tools",
            "/runtime/bin/" + manifest["python_name"]]
    return args + (list(python_args) if python_args is not None else ["/tools/hosted_mcp.py"])


def mcp_config(manifest):
    cmd = namespace_command(manifest)
    return {"mcpServers": {"g1": {"type": "stdio", "command": cmd[0], "args": cmd[1:]}}}

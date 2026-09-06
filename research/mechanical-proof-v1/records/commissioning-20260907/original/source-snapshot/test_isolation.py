"""Real, harmless process-containment controls; run only on the qualified Linux host."""
import importlib.util
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys

import pytest

HERE = Path(__file__).resolve().parent
BWRAP_SHA = "af662c55cd85178a58da083220a9348c4a7d3c24333fd0bc7badb18c93392987"


@pytest.fixture
def runner():
    path = HERE / "isolation.py"
    if not path.is_file(): return None
    spec = importlib.util.spec_from_file_location("f0_isolation_tested", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def registered(tmp_path):
    import hashlib
    executable = Path(sys.executable).resolve()
    runtime = executable.parents[1]
    libraries = {}
    output = subprocess.check_output(["/usr/bin/ldd", str(executable)], text=True)
    assert "not found" not in output
    for guest in re.findall(r"(?<!\S)(/[^\s()]+)", output):
        resolved = Path(guest).resolve()
        if not resolved.is_relative_to(runtime): libraries[guest] = resolved
    assert (runtime/"bin/python3").is_file() and libraries
    work = tmp_path / "work"; work.mkdir()
    return dict(read_only=[(runtime, "/python")]
                + [(p, guest) for guest, p in sorted(libraries.items())],
                executable_sha256=hashlib.sha256(executable.read_bytes()).hexdigest(),
                work_dir=work, env={"PATH": "/bin", "LANG": "C.UTF-8"},
                timeout_s=5, max_output_bytes=4096, bwrap_sha256=BWRAP_SHA)


def call(runner, registered, code):
    return runner.run_isolated(["/python/bin/python3", "-I", "-S", "-c", code], **registered)


def test_real_minimal_launch_has_clean_environment_and_no_host_file(runner, registered, tmp_path, monkeypatch):
    assert runner is not None, "isolated execution helper is not implemented"
    secret = tmp_path / "host-only"; secret.write_text("HOST_ONLY")
    monkeypatch.setenv("F0_INHERITED_SECRET", "MUST_NOT_APPEAR")
    code = "import os,json;print(json.dumps([os.path.exists(" + repr(str(secret)) + "),os.getenv('F0_INHERITED_SECRET'),os.getcwd()]))"
    result = call(runner, registered, code)
    assert result["terminal"] == "COMPLETED", result
    assert result["returncode"] == 0 and json.loads(result["stdout"]) == [False, None, "/work"]
    assert result["bwrap"]["sha256"] == BWRAP_SHA and result["cleanup"]["reaped"]
    assert result["cpu_s"] is None and result["peak_rss_bytes"] is None


def test_real_network_namespace_cannot_reach_host_listener(runner, registered):
    with socket.socket() as server:
        server.bind(("127.0.0.1", 0)); server.listen()
        port = server.getsockname()[1]
        code = ("import os,socket,json;s=socket.socket();s.settimeout(.2);"
                "r=s.connect_ex(('127.0.0.1'," + str(port) + "));"
                "print(json.dumps([os.readlink('/proc/self/ns/net'),r]))")
        result = call(runner, registered, code)
    assert result["terminal"] == "COMPLETED" and result["returncode"] == 0, result
    namespace, connection = json.loads(result["stdout"])
    assert namespace != os.readlink("/proc/self/ns/net") and connection != 0


def test_real_only_work_is_persistent_writable_mount(runner, registered, tmp_path):
    data = tmp_path / "input.txt"; data.write_text("READ_ONLY")
    registered["read_only"].append((data, "/input.txt"))
    code = """import json,os
open('/work/result.txt','w').write('OK')
try:
    open('/input.txt','w').write('BAD')
    status='WRITABLE'
except OSError:
    status='READ_ONLY'
print(json.dumps([status,os.path.exists('/home'),os.path.exists('/root')]))
"""
    result = call(runner, registered, code)
    assert result["terminal"] == "COMPLETED" and result["returncode"] == 0, result
    assert json.loads(result["stdout"]) == ["READ_ONLY", False, False]
    assert data.read_text() == "READ_ONLY"
    assert (registered["work_dir"] / "result.txt").read_text() == "OK"


@pytest.mark.parametrize("violation", ["host_root", "home", "guest_root", "duplicate", "overlap",
                                     "traversal", "dispatch", "wrong_exec_hash", "wrong_bwrap_hash"])
def test_disallowed_registration_refuses_before_process(runner, registered, violation):
    if violation == "host_root": registered["read_only"].append((Path("/"), "/host"))
    elif violation == "home": registered["read_only"].append((Path("/home/billy"), "/host"))
    elif violation == "guest_root": registered["read_only"].append((Path("/etc/hostname"), "/"))
    elif violation == "duplicate": registered["read_only"].append(registered["read_only"][0])
    elif violation == "overlap": registered["read_only"].append((Path("/etc/hostname"), "/python/bin/python3/inside"))
    elif violation == "traversal": registered["read_only"].append((Path("/etc/hostname"), "/data/../oops"))
    elif violation == "wrong_exec_hash": registered["executable_sha256"] = "0" * 64
    elif violation == "wrong_bwrap_hash": registered["bwrap_sha256"] = "0" * 64
    argv = ["/unregistered/python"] if violation == "dispatch" else ["/python/bin/python3", "--version"]
    result = runner.run_isolated(argv, **registered)
    assert result["terminal"] == "REFUSED" and result["pid"] is None, result


def test_external_symlink_refused_but_internal_executable_link_supported(runner, registered, tmp_path):
    result = runner.run_isolated(["/python/bin/python3", "-I", "-S", "-c", "print('OK')"], **registered)
    assert result["terminal"] == "COMPLETED" and result["stdout"].strip() == "OK", result
    directory = tmp_path / "tools"; directory.mkdir()
    (directory / "escape").symlink_to("/etc/hostname")
    registered["read_only"].append((directory, "/tools"))
    result = runner.run_isolated(["/python/bin/python3", "--version"], **registered)
    assert result["terminal"] == "REFUSED" and result["pid"] is None


def test_writable_overlap_or_symlink_is_refused(runner, registered, tmp_path):
    registered["read_only"].append((registered["work_dir"], "/alias"))
    result = call(runner, registered, "pass")
    assert result["terminal"] == "REFUSED" and result["pid"] is None
    registered["read_only"].pop()
    alias = tmp_path / "alias"; alias.symlink_to(registered["work_dir"], target_is_directory=True)
    registered["work_dir"] = alias
    assert call(runner, registered, "pass")["terminal"] == "REFUSED"


def test_real_timeout_reaps_process_and_group(runner, registered):
    registered["timeout_s"] = .15
    result = call(runner, registered, "import os,time;os.fork();time.sleep(30)")
    assert result["terminal"] == "TIMEOUT" and result["timed_out"], result
    assert result["wall_s"] < 3 and result["cleanup"]["reaped"]
    with pytest.raises(ProcessLookupError): os.killpg(result["pid"], 0)


def test_real_output_limit_is_bounded_and_reaps(runner, registered):
    registered["max_output_bytes"] = 128
    result = call(runner, registered, "import os;\nwhile True: os.write(1,b'x'*4096)")
    assert result["terminal"] == "OUTPUT_LIMIT" and result["output_truncated"], result
    assert len(result["stdout"].encode()) + len(result["stderr"].encode()) <= 128
    assert result["cleanup"]["reaped"]


def test_missing_isolation_tool_cannot_fallback_to_host(runner, registered, tmp_path):
    registered["bwrap_path"] = str(tmp_path / "missing-bwrap")
    result = call(runner, registered, "print('UNISOLATED')")
    assert result["terminal"] == "CANNOT_CHECK" and result["pid"] is None
    assert result["stdout"] == "" and result["stderr"] == ""


@pytest.mark.parametrize("kind", ["symlink", "fifo"])
def test_special_writable_outputs_cannot_be_consumed_as_regular_artifacts(runner, registered, kind):
    expression = "os.symlink('/etc/hostname','/work/out')" if kind == "symlink" else "os.mkfifo('/work/out')"
    result = call(runner, registered, "import os;" + expression)
    assert result["terminal"] == "CANNOT_CHECK" and "writable output" in result["reason"], result
    assert result["cleanup"]["reaped"]


def test_raw_non_utf8_output_remains_exactly_recoverable(runner, registered):
    import base64
    result = call(runner, registered, "import os;os.write(1,b'\\xff\\x00')")
    assert result["terminal"] == "COMPLETED" and result["returncode"] == 0, result
    assert base64.b64decode(result["stdout_base64"]) == b"\xff\x00"


@pytest.mark.parametrize("persistent", [True, False])
def test_real_root_is_read_only_with_only_intended_temporary_writes(runner, registered, persistent):
    if not persistent: registered["work_dir"] = None
    code = """import errno,json
states = []
for name in ['/unregistered', '/work/allowed', '/tmp/allowed']:
    try:
        with open(name, 'w') as stream: stream.write('OK')
        states.append('WRITTEN')
    except OSError as error:
        states.append(error.errno)
print(json.dumps(states))
"""
    result = call(runner, registered, code)
    assert result["terminal"] == "COMPLETED" and result["returncode"] == 0, result
    import errno
    assert json.loads(result["stdout"]) == [errno.EROFS, "WRITTEN", "WRITTEN"]

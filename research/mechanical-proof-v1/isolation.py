"""Closed-mount process isolation; caller owns full source/artifact custody and argv policy."""
from __future__ import annotations

import base64
import hashlib
import math
import os
from pathlib import Path
import selectors
import signal
import subprocess
import time

BWRAP_SHA256 = "af662c55cd85178a58da083220a9348c4a7d3c24333fd0bc7badb18c93392987"
RESERVED = ("/home", "/root", "/proc", "/dev", "/sys", "/tmp", "/work")
BROAD = {"/", "/home", "/root", "/usr", "/usr/lib", "/usr/local", "/lib", "/lib64", "/bin", "/sbin", "/etc"}


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""): digest.update(block)
    return digest.hexdigest()


def _path(value):
    text = os.fspath(value)
    path = Path(text)
    if not path.is_absolute() or text != path.as_posix() or any(x in {".", "..", ""} for x in text.split("/")[1:]):
        raise ValueError("noncanonical absolute path")
    return path


def _source(value):
    path = _path(value)
    if path.resolve(strict=True) != path: raise ValueError("symlink source component")
    if not (path.is_file() or path.is_dir()): raise ValueError("nonregular mount source")
    return path


def _overlap(a, b):
    return a == b or a.is_relative_to(b) or b.is_relative_to(a)


def _registered(read_only, work_dir, argv, executable_sha256):
    mounts = []
    for host, guest in read_only:
        source, destination = _source(host), _path(guest)
        if (str(source) in BROAD or source == Path.home() or (source / ".git").exists()
                or str(destination) in BROAD or any(destination.is_relative_to(p) for p in RESERVED)):
            raise ValueError("broad, repository-root or reserved mount")
        if any(_overlap(destination, prior[1]) for prior in mounts):
            raise ValueError("duplicate or overlapping guest destinations")
        if source.is_dir():
            for current, directories, files in os.walk(source, followlinks=False):
                for name in directories + files:
                    entry = Path(current) / name
                    if entry.is_symlink() and (entry.readlink().is_absolute() or not entry.resolve(strict=True).is_relative_to(source)):
                        raise ValueError("mount contains escaped or absolute symlink")
        mounts.append((source, destination))
    work = _source(work_dir) if work_dir is not None else None
    if work is not None:
        if not work.is_dir() or str(work) in BROAD or work == Path.home() or (work / ".git").exists():
            raise ValueError("invalid writable work directory")
        if any(_overlap(work, host) for host, _ in mounts): raise ValueError("writable/read-only source overlap")
        if any(p.is_symlink() or not (p.is_file() or p.is_dir()) for p in work.rglob("*")):
            raise ValueError("writable work contains nonregular object")
    executable = _path(argv[0]); resolved = None
    for host, guest in mounts:
        if executable == guest or (host.is_dir() and executable.is_relative_to(guest)):
            candidate = host / executable.relative_to(guest) if host.is_dir() else host
            resolved = candidate.resolve(strict=True)
            if host.is_dir() and not resolved.is_relative_to(host): raise ValueError("executable escapes registered root")
    if resolved is None or not resolved.is_file() or not os.access(resolved, os.X_OK):
        raise ValueError("unregistered executable")
    if sha256(resolved) != executable_sha256: raise ValueError("registered executable hash mismatch")
    return mounts, work, resolved


def run_isolated(argv, *, read_only, executable_sha256, work_dir=None, env=None,
                 timeout_s, max_output_bytes, bwrap_path="/usr/bin/bwrap", bwrap_sha256=BWRAP_SHA256):
    """Execute one registered command. No host fallback; CPU/RSS remain unmeasured."""
    started = time.monotonic()
    result = dict(terminal="CANNOT_CHECK", reason="", pid=None, returncode=None, timed_out=False,
                  output_truncated=False, stdout="", stderr="", cpu_s=None, peak_rss_bytes=None,
                  cleanup={"reaped": False, "group_absent": None, "kill_sent": False})
    process = None; work = None; streams = {"stdout": bytearray(), "stderr": bytearray()}
    try:
        if (not isinstance(argv, (list, tuple)) or not argv or
                any(not isinstance(a, str) or "\0" in a for a in argv)):
            raise ValueError("invalid argv")
        if (isinstance(timeout_s, bool) or not isinstance(timeout_s, (int, float)) or
                not math.isfinite(timeout_s) or timeout_s <= 0 or type(max_output_bytes) is not int or max_output_bytes < 1):
            raise ValueError("invalid time/output bound")
        environment = dict(env or {})
        if any(not isinstance(k, str) or not isinstance(v, str) or not k or "=" in k or "\0" in k + v
               or k.startswith(("LD_", "DYLD_")) or k in {"BASH_ENV", "ENV"} for k, v in environment.items()):
            raise ValueError("invalid or code-loading environment entry")
        mounts, work, executable = _registered(read_only, work_dir, argv, executable_sha256)
        bwrap = _source(bwrap_path)
        if not bwrap.is_file() or sha256(bwrap) != bwrap_sha256: raise ValueError("bubblewrap identity mismatch")
        command = [str(bwrap), "--unshare-all", "--unshare-user", "--unshare-pid", "--unshare-net",
                   "--die-with-parent", "--new-session", "--cap-drop", "ALL",
                   "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp"]
        for host, guest in mounts: command += ["--ro-bind", str(host), str(guest)]
        command += ["--bind", str(work), "/work"] if work else ["--tmpfs", "/work"]
        command += ["--remount-ro", "/", "--chdir", "/work", "--", *argv]
        result.update(invocation=command, environment=environment, execution_timeout_s=timeout_s,
                      max_output_bytes=max_output_bytes,
                      mounts=[{"source": str(h), "destination": str(g), "mode": "read-only"} for h, g in mounts],
                      work_dir=str(work) if work else None,
                      executable={"source": str(executable), "sha256": executable_sha256},
                      bwrap={"path": str(bwrap), "sha256": bwrap_sha256})
        process = subprocess.Popen(command, env=environment, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, start_new_session=True, close_fds=True, bufsize=0)
        result["pid"] = process.pid
        deadline = time.monotonic() + timeout_s; total = 0
        with selectors.DefaultSelector() as selector:
            for name in streams:
                pipe = getattr(process, name); os.set_blocking(pipe.fileno(), False)
                selector.register(pipe, selectors.EVENT_READ, name)
            while selector.get_map() or process.poll() is None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    result.update(terminal="TIMEOUT", timed_out=True); break
                for key, _ in selector.select(min(remaining, .05)):
                    data = os.read(key.fd, min(65536, max_output_bytes - total + 1))
                    if not data: selector.unregister(key.fileobj); continue
                    allowed = max_output_bytes - total
                    streams[key.data].extend(data[:allowed]); total += len(data[:allowed])
                    if len(data) > allowed:
                        result.update(terminal="OUTPUT_LIMIT", output_truncated=True); break
                if result["output_truncated"]: break
            else: result["terminal"] = "COMPLETED"
        if sha256(executable) != executable_sha256 or sha256(bwrap) != bwrap_sha256:
            result.update(terminal="CANNOT_CHECK", reason="executable identity changed during invocation")
    except (ValueError, TypeError, IndexError, RuntimeError) as exc:
        result.update(terminal="REFUSED", reason=type(exc).__name__ + ": " + str(exc))
    except (OSError, subprocess.SubprocessError) as exc:
        result.update(terminal="CANNOT_CHECK", reason=type(exc).__name__ + ": " + str(exc))
    finally:
        if process is not None:
            try: os.killpg(process.pid, signal.SIGKILL); result["cleanup"]["kill_sent"] = True
            except ProcessLookupError: pass
            process.wait(); result["cleanup"]["reaped"] = True; result["returncode"] = process.returncode
            for name in streams: getattr(process, name).close()
            try: os.killpg(process.pid, 0); result["cleanup"]["group_absent"] = False
            except ProcessLookupError: result["cleanup"]["group_absent"] = True
            if not result["cleanup"]["group_absent"]:
                result.update(terminal="CANNOT_CHECK", reason="process group cleanup incomplete")
            if work is not None:
                try:
                    if any(p.is_symlink() or not (p.is_file() or p.is_dir()) for p in work.rglob("*")):
                        result.update(terminal="CANNOT_CHECK", reason="nonregular writable output")
                except OSError as exc:
                    result.update(terminal="CANNOT_CHECK", reason="writable output inspection failed: " + str(exc))
        for name, data in streams.items():
            result[name] = data.decode("utf-8", errors="replace")
            result[name + "_base64"] = base64.b64encode(data).decode("ascii")
            result[name + "_bytes"] = len(data)
            result[name + "_sha256"] = hashlib.sha256(data).hexdigest()
        result["wall_s"] = time.monotonic() - started
        result["cost_scope"] = "Validation through cleanup; limit/hashes bind captured raw bytes; text decoding may expand bytes. CPU/RSS unmeasured."
        result["completion_scope"] = "Isolated process envelope; caller must validate executable response before attributing native work or proof status."
    return result

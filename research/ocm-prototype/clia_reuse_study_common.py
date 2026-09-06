"""Shared custody and observational meters; no expected answers or actor policy."""
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PROTOCOL_SHA = "619218d6c5a70bc4713c89f388e80e990c571f400c9ef48731fc76c9b7aad556"
PUBLIC_SHA = "ea1f2074eb404ba3687276183b0b3aedfa85a7190b0e1538a90a3991325faf48"


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f:
        json.dump(value, f, sort_keys=True, indent=2); f.write("\n")


def source_files():
    paths = {*HERE.glob("g1_*.py"), *HERE.glob("clia_*.py"), *REPO.glob("src/ocm/**/*.py"),
             *HERE.glob("clia_fixtures/*"), HERE / "vendor/conll18_ud_eval.py",
             HERE / "syntax_contract.py", HERE / "udpipe_donor.py",
             HERE / "capture_clia_reuse.py", HERE / "grade_clia_reuse.py",
             HERE / "grade_clia_reuse_audit.py", HERE / "grade_clia_reuse_capture.py",
             *HERE.glob("grade_clia_reuse*.py"),
             HERE / "matched_g1_worker.py", HERE / "requirements-g1.txt"}
    missing = sorted(str(p) for p in paths if not p.is_file())
    if missing: raise ValueError("REQUIRED_SOURCE_MISSING:" + ",".join(missing))
    return {str(p.relative_to(REPO)): sha(p) for p in sorted(paths)}


def tree_bytes(root):
    files = [p for p in Path(root).rglob("*") if p.is_file()]
    return {"logical_bytes": sum(p.stat().st_size for p in files),
            "allocated_file_bytes": sum(p.stat().st_blocks * 512 for p in files),
            "files": len(files), "scope": "sum over files; filesystem dedup/compression unknown"}


class InvocationMeter:
    """Observe the actual existing native worker boundary, preserving its result."""
    def __init__(self, events, sink=None):
        self.events = events; self.sink = sink; self.restores = []

    def __enter__(self):
        import clia_process
        self.original = clia_process.invoke
        def observed(action, payload, **kwargs):
            event = {"index": len(self.events), "action": action,
                     "payload_sha256": digest(payload), "bounds": kwargs,
                     "started_monotonic": time.monotonic()}
            self.events.append(event)
            if self.sink: self.sink("started", event)
            try:
                result = self.original(action, payload, **kwargs)
                event["result"] = json.loads(json.dumps(result))
                return result
            except BaseException as exc:
                event["error"] = type(exc).__name__
                raise
            finally:
                event["finished_monotonic"] = time.monotonic()
                if self.sink: self.sink("finished", event)
        clia_process.invoke = observed
        from clia_reuse_apply import CompiledProgram
        import udpipe_donor
        import sys
        def wrap(owner, name, action):
            original = getattr(owner, name); self.restores.append((owner, name, original))
            def call(*args, **kwargs):
                info = args[1] if action == "application" else {"tokens": args[0], "model_sha256": args[2]}
                event = {"index": len(self.events), "action": action, "payload_sha256": digest(info),
                         "started_monotonic": time.monotonic()}
                self.events.append(event)
                if self.sink: self.sink("started", event)
                try:
                    answer = original(*args, **kwargs); event["result"] = answer; return answer
                except BaseException as exc:
                    event["error"] = type(exc).__name__; raise
                finally:
                    event["finished_monotonic"] = time.monotonic()
                    if self.sink: self.sink("finished", event)
            setattr(owner, name, call)
        wrap(CompiledProgram, "apply", "application")
        wrap(udpipe_donor, "predict", "syntax")
        if "g1_vessel" in sys.modules: wrap(sys.modules["g1_vessel"], "predict", "syntax")
        return self

    def __exit__(self, *_):
        import clia_process
        clia_process.invoke = self.original
        for owner, name, original in reversed(self.restores): setattr(owner, name, original)


def run_process(argv, prefix, *, seconds, cwd=None, env=None, cpu=None, address_bytes=None):
    """Direct wait4, no wrapper; preserve distinct scopes instead of asserting completeness."""
    prefix = Path(prefix)
    for suffix in (".stdout", ".stderr"):
        if prefix.with_suffix(suffix).exists(): raise ValueError("refuse process-output overwrite")
    def limits():
        if cpu is not None: os.sched_setaffinity(0, {cpu})
        if address_bytes is not None:
            resource.setrlimit(resource.RLIMIT_AS, (address_bytes, address_bytes))
    start = time.monotonic(); timed_out = False; sent_kill = False; term_at = None
    with prefix.with_suffix(".stdout").open("x") as out, prefix.with_suffix(".stderr").open("x") as err:
        process = subprocess.Popen(argv, cwd=cwd, env=env, stdout=out, stderr=err,
                                   start_new_session=True, preexec_fn=limits)
        while True:
            pid, status, usage = os.wait4(process.pid, os.WNOHANG)
            if pid: break
            now = time.monotonic()
            if now - start >= seconds and not timed_out:
                timed_out = True; term_at = now
                try: os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError: pass
            if timed_out and now - term_at >= 2 and not sent_kill:
                try: os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError: pass
                sent_kill = True
            time.sleep(.01)
        process.returncode = os.waitstatus_to_exitcode(status)
        if timed_out:
            # Reaping the actor must not bypass termination of its surviving group.
            try: os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError: pass
    return {"pid": process.pid, "exit_code": process.returncode, "timed_out": timed_out,
            "wall_s": time.monotonic() - start, "wait4_cpu_s": usage.ru_utime + usage.ru_stime,
            "wait4_raw": {k: getattr(usage, k) for k in ("ru_utime", "ru_stime", "ru_maxrss",
                         "ru_inblock", "ru_oublock", "ru_nvcsw", "ru_nivcsw")},
            "complete_tree_cpu_verified": False,
            "cpu_scope": "direct actor wait4; actor self/reaped-child reports separate; no full-tree claim",
            "stdout_sha256": sha(prefix.with_suffix(".stdout")),
            "stderr_sha256": sha(prefix.with_suffix(".stderr"))}


def verify_capture_manifest(root):
    root = Path(root)
    manifest = json.loads((root / "capture-manifest.json").read_text())
    for rel, expected in manifest["files"].items():
        path = root / rel
        if not path.resolve().is_relative_to(root.resolve()) or sha(path) != expected:
            raise ValueError("CAPTURE_HASH_MISMATCH:" + rel)
    return manifest

"""Fourteen assigned fresh processes; preserve every terminal and charge cleanup."""
from pathlib import Path
import argparse
import os
import resource
import shutil
import signal
import subprocess
import time
from trial_common import ROOT, read, sha, verify_freeze, write

def run_process(argv, folder, *, seconds, cpu, address_bytes, env=None):
    """Direct wait4; no wrapper that could omit actor CPU."""
    folder = Path(folder); start = time.perf_counter_ns(); timed_out = False
    process = None; usage = None; error = None; cleanup_group = False
    def limits():
        if cpu is not None: os.sched_setaffinity(0, {cpu})
        if address_bytes is not None: resource.setrlimit(resource.RLIMIT_AS, (address_bytes, address_bytes))
    with (folder/"stdout").open("xb") as out, (folder/"stderr").open("xb") as err:
        try:
            process = subprocess.Popen(argv, stdout=out, stderr=err, cwd=folder,
                                       env=env, preexec_fn=limits, start_new_session=True)
            while True:
                pid, status, usage = os.wait4(process.pid, os.WNOHANG)
                if pid: break
                if (time.perf_counter_ns()-start)/1e9 >= seconds and not timed_out:
                    timed_out = True
                    try: os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError: pass
                time.sleep(.01)
            process.returncode = os.waitstatus_to_exitcode(status)
            # A reaped parent must not leave its child group running.
            try:
                os.killpg(process.pid, 0); cleanup_group = True
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError: pass
        except BaseException as exc:
            error = {"type": type(exc).__name__, "message": str(exc)}
            if process is not None:
                try: os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError: pass
                if process.returncode is None: process.wait()
    worker = None
    try: worker = read(folder/"stdout")
    except (ValueError, OSError) as exc:
        if error is None: error = {"type": "WORKER_RECORD_UNREADABLE", "message": str(exc)}
    private = folder/"private"
    copied = {}
    if private.exists():
        copied = {str(p.relative_to(private)): {"sha256": sha(p), "bytes": p.stat().st_size}
                  for p in sorted(private.rglob("*")) if p.is_file()}
        write(folder/"private-final-inventory.json", copied)
        shutil.rmtree(private)
    write(folder/"captured-worker.json", worker)
    result = {"pid": None if process is None else process.pid,
              "exit_code": None if process is None else process.returncode,
              "timed_out": timed_out, "supervisor_error": error,
              "pid_absent": process is not None and not Path("/proc",str(process.pid)).exists(),
              "post_reap_group_required_kill": cleanup_group,
              "private_state_removed": not private.exists(),
              "private_bytes": sum(v["bytes"] for v in copied.values()),
              "wait4_raw": None if usage is None else {k: getattr(usage,k) for k in
                  ("ru_utime","ru_stime","ru_maxrss","ru_inblock","ru_oublock","ru_nvcsw","ru_nivcsw")},
              "complete_tree_cpu_verified": False,
              "cpu_scope": "direct wait4 actor; worker self/reaped-child records separate; escaped/unknown descendant work not proved complete",
              "stdout_sha256": sha(folder/"stdout"), "stderr_sha256": sha(folder/"stderr"),
              "worker": worker, "total_two_call_process_ns": time.perf_counter_ns()-start,
              "total_scope": "before Popen/output-open through wait4, read/hash/write captured records and private-state inventory/removal; final timing-metadata write excluded"}
    write(folder/"process.json", result)
    return result

def capture(manifest_path, output):
    manifest_path, output = Path(manifest_path).resolve(), Path(output).resolve()
    m = verify_freeze(manifest_path); output.mkdir(parents=True, exist_ok=False)
    write(output/"manifest.json", m)
    if sha(output/"manifest.json") != sha(manifest_path): raise ValueError("NONCANONICAL_MANIFEST")
    launch = {"manifest_sha256": sha(manifest_path), "root": str(output),
              "assigned_processes": 14, "assigned_calls": 28,
              "registered_issue": m["registration"], "manifest_source": str(manifest_path), "started_ns": time.time_ns()}
    write(output/"launch.json", launch)
    reports = []
    env = dict(os.environ); env.pop("PYTHONPATH",None); env["PYTHONDONTWRITEBYTECODE"] = "1"
    for assignment in m["assignments"]:
        folder = output/f"case-{assignment['index']:02d}"; folder.mkdir()
        case = {"assignment": assignment, "manifest": str(manifest_path),
                "manifest_sha256": sha(manifest_path), "output": str(folder)}
        write(folder/"input.json", case)
        argv = [m["python"], str(ROOT/"trial_worker.py"), "--case", str(folder/"input.json")]
        result = run_process(argv, folder, seconds=m["seconds_per_process"],
                             cpu=m["cpu"], address_bytes=m["address_bytes"], env=env)
        reports.append({"assignment": assignment, "process": str(folder.relative_to(output)/"process.json"),
                        "exit_code": result["exit_code"], "timed_out": result["timed_out"]})
        print(assignment, result["exit_code"], flush=True)
    receipt = {"status": "SEALED", "reports": reports, "assigned_processes": 14, "assigned_calls": 28,
               "finished_ns": time.time_ns(), "manifest_sha256": sha(manifest_path)}
    write(output/"receipt.json", receipt)
    files = {str(p.relative_to(output)): sha(p) for p in sorted(output.rglob("*")) if p.is_file()}
    write(output/"SEAL.json", files)
    return output

def main():
    p=argparse.ArgumentParser(); p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True); a=p.parse_args()
    capture(a.manifest,a.output)
    return 0

if __name__ == "__main__": raise SystemExit(main())

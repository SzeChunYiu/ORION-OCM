"""Local process-supervision fixtures; all fixture children are cleaned even on failure."""
import json
import os
from pathlib import Path
import signal
import sys
import time

from clia_reuse_study_common import run_process


def test_timeout_reaps_actor_and_terminates_resistant_group_child(tmp_path):
    pidfile = tmp_path / "UNIT_CHILD_PID"
    child = ("import os,signal,time;from pathlib import Path;"
             "signal.signal(signal.SIGTERM,signal.SIG_IGN);"
             "Path(" + repr(str(pidfile)) + ").write_text(str(os.getpid()));time.sleep(30)")
    actor = tmp_path / "UNIT_ACTOR.py"
    actor.write_text("import subprocess,sys,time\nsubprocess.Popen([sys.executable,'-c',"
                     + repr(child) + "])\ntime.sleep(30)\n")
    receipt = run_process([sys.executable, str(actor)], tmp_path / "timeout", seconds=1)
    assert pidfile.exists(), "unit child did not reach its ready point"
    pid = int(pidfile.read_text())
    state = None
    try:
        for _ in range(50):
            path = Path("/proc") / str(pid) / "stat"
            state = path.read_text().rsplit(")", 1)[1].split()[0] if path.exists() else None
            if state in (None, "Z"): break
            time.sleep(.01)
        (tmp_path / "observed-child-state.json").write_text(json.dumps({
            "scope": "UNIT_PROCESS_FIXTURE_NOT_PANEL", "child_pid": pid, "state_after_supervision": state,
            "receipt": receipt}))
    finally:
        try: os.kill(pid, signal.SIGKILL)
        except ProcessLookupError: pass
    assert receipt["timed_out"] and receipt["exit_code"] != 0
    assert state in (None, "Z"), "fixture child remained running after timed-out actor was reaped"
    assert receipt["complete_tree_cpu_verified"] is False

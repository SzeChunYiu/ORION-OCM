"""Authored ten-tree integration fixture; resource controller is explicitly simulated."""
from pathlib import Path
import json
import os
import signal
import subprocess
import sys
import time
import pytest
from test_materialize_git import fixture
from test_materialize_phase import modules


def prepared(tmp_path, monkeypatch, after=None):
    loaded = modules(); run = loaded["materialize_run"]; phase = loaded["materialize_phase"]
    c = loaded["acquisition_contract"]; objects = loaded["materialize_objects"]
    try:
        qualified = (c.record(Path(sys.executable).resolve())["sha256"] == c.PYTHON
                     and c.record("/usr/bin/git")["sha256"] == phase.GIT)
    except (OSError, ValueError):
        qualified = False
    if not qualified:
        pytest.skip("real isolated worker requires exact qualified Python/Git; incompatible host is not a pass")
    reg = tmp_path / "reg"; reg.mkdir(); episode = tmp_path / "episode"; episode.mkdir()
    bare, commit, tree, _ = fixture(tmp_path)
    start = dict(boot_id=Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
                 monotonic_seconds=time.monotonic(), whole_deadline_monotonic=time.monotonic() + 90)
    p = dict(memory_bytes=134217728, memory_and_swap_bytes=134217728, cpu_equivalents=1, pids=16,
             file_size_bytes=8388608, initial_mem_available_bytes=0, initial_disk_free_bytes=0,
             stop_disk_free_bytes=0, stop_owned_new_bytes=134217728, term_grace_seconds=1,
             forced_reap_seconds=2, disk_poll_seconds=0.05)
    pin = tmp_path / "input.json"; pin.write_text("{}\n")
    authority = dict(start=start, assignments=dict(rows=[dict(key=str(i)) for i in range(4)]),
                     policy=dict(limits=p), inputs=[c.record(pin)], episode=str(episode),
                     registration=str(reg), acquisition_phase_sha256="AUTHORED_FIXTURE",
                     materials=[dict(name="corpus" if i == 0 else "dependency" + str(i),
                           bare_path=str(bare), commit=commit, tree=tree, files=objects.file_map(bare)) for i in range(10)])
    monkeypatch.setattr(phase, "authorize", lambda *args: authority)
    monkeypatch.setattr(run, "host", lambda: dict(python=c.record(Path(sys.executable).resolve()),
                                                 git=c.record("/usr/bin/git"), imports={}))
    calls = []
    def resource(source, command, bounds, root, owned):
        environment = {}
        root.mkdir(); calls.append(dict(argv=command, bounds=bounds, owned=owned))
        out = (root / "stdout.bin").open("xb"); err = (root / "stderr.bin").open("xb")
        child = subprocess.Popen(command, env=environment, stdout=out, stderr=err, start_new_session=True)
        try: code = child.wait(timeout=60)
        finally:
            if child.poll() is None: os.killpg(child.pid, signal.SIGKILL); child.wait(timeout=5)
            out.close(); err.close()
        (root / "samples.jsonl").write_bytes(b"")
        try: os.killpg(child.pid, 0)
        except ProcessLookupError: absent = True
        else: absent = False
        value = dict(terminal="COMPLETED" if code == 0 else "COMMAND_FAILED", returncode=code,
                     evidence_complete=True, argv=command, environment=environment, limits=bounds,
                     dispatch=dict(state="STARTED", attempted=True, pid=child.pid),
                     cleanup=dict(reaped=True, members_empty=absent, controllers_removed=True),
                     qualification_scope="MOCK_CONTROLLER_REAL_AUTHORED_WORKER")
        value["raw"] = {n: c.record(root / n) for n in ("stdout.bin", "stderr.bin", "samples.jsonl")}
        if after: after(root.parent, value, authority)
        c.write(root / "resource-receipt.json", value)
        return value
    monkeypatch.setattr(run, "dispatch", resource)
    return loaded, (reg, episode, bare, tmp_path / "out"), authority, calls

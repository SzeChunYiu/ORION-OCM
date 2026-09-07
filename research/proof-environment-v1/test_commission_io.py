"""Actual harmless process cleanup under an injected host-recorder interruption."""
from pathlib import Path
import sys
import time
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import commission_io as C
import env_inputs as I


def test_interrupted_host_dispatch_keeps_raw_logs_and_reaps_process(tmp_path, monkeypatch):
    original = C.subprocess.Popen
    log = tmp_path / "process"
    class InterruptedProcess:
        def __init__(self, child): self.child = child; self.first = True
        @property
        def pid(self): return self.child.pid
        @property
        def returncode(self): return self.child.returncode
        def wait(self):
            if self.first:
                self.first = False; deadline = time.monotonic() + 3
                while b"HARMLESS_RECORDER_CONTROL" not in (log / "stdout.bin").read_bytes():
                    if time.monotonic() >= deadline: raise AssertionError("control process never became ready")
                    time.sleep(.01)
                raise KeyboardInterrupt()
            return self.child.wait()
    def harmless_standin(argv, **kwargs):
        command = [sys.executable, "-I", "-S", "-c",
                   "import time; print('HARMLESS_RECORDER_CONTROL', flush=True); time.sleep(30)"]
        return InterruptedProcess(original(command, **kwargs))
    monkeypatch.setattr(C.subprocess, "Popen", harmless_standin)
    fake = {"path": "/authored/unit-fixture", "sha256": "a" * 64}
    matrix = {"runtime": fake, "timeout_s": 1, "max_output_bytes": 1024}
    with pytest.raises(KeyboardInterrupt): C.launch("prepare", fake, tmp_path / "unused", matrix, log)
    envelope = I.parse_json((log / "process.json").read_bytes())
    assert envelope["interrupted"] is True
    assert envelope["cleanup"] == {"reaped": True, "group_absent": True}
    assert envelope["returncode"] < 0
    assert b"HARMLESS_RECORDER_CONTROL" in (log / "stdout.bin").read_bytes()
    assert "receipt_error" in envelope  # This stand-in is deliberately not native proof evidence.

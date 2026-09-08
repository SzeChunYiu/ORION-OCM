import os,signal,subprocess,sys
import resource_pidfd as p
def test_fallback_owned_child_exit_and_signal_zero(monkeypatch):
 monkeypatch.delattr(os,"pidfd_open",raising=False)
 monkeypatch.delattr(signal,"pidfd_send_signal",raising=False)
 assert p.preflight()["signal_zero_verified"]
 child=subprocess.Popen([sys.executable,"-c","import time;time.sleep(10)"])
 fd=p.open_pid(child.pid)
 try:
  p.send(fd,signal.SIGTERM);assert child.wait(timeout=2)==-signal.SIGTERM
 finally:os.close(fd)

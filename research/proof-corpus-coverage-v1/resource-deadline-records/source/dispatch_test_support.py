"""Actual short child processes with an authored in-memory controller, not a cgroup test."""
from pathlib import Path
import signal,subprocess,time

def controlled(r, root, monkeypatch, fault=None):
    children=[]; calls=[]; original_popen=subprocess.Popen
    marker=root/"child-ran"
    class Controller:
        paths={};helper_sources={};removed=False
        @classmethod
        def create(cls,*args):return cls()
        def attach(self):pass
        def snapshot(self):
            if fault=="controller" and children and "fault" not in calls:
                calls.append("fault");raise OSError("authored controller sample")
            return {"members":[p.pid for p in children if p.poll() is None],
                    "memory.failcnt":0,"memory.memsw.failcnt":0,"pids.events":{}}
        def remove(self):
            if fault in ("cleanup","late_cleanup"):raise OSError("authored cleanup")
            self.removed=True;calls.append("removed")
    def popen(*a,**kw):
        if not a or str(marker) not in " ".join(a[0]):return original_popen(*a,**kw)
        if fault=="launch":raise OSError("authored launch uncertainty")
        p=original_popen(*a,**kw);children.append(p)
        deadline=time.monotonic()+3
        while not marker.exists():
            assert p.poll() is None
            assert time.monotonic()<deadline
            time.sleep(.005)
        return p
    original_disk=r.disk_snapshot
    def disk(roots):
        if fault in ("disk","cleanup") and children and "fault" not in calls:
            calls.append("fault");raise OSError("authored disk sample")
        return original_disk(roots)
    original_canonical=r.canonical
    def canonical(value):
        if fault=="missing_raw" and children and "fault" not in calls:
            calls.append("fault");(root/"out"/"stdout.bin").unlink()
        if fault=="sample" and children and "fault" not in calls:
            calls.append("fault");raise OSError("authored sample output")
        return original_canonical(value)
    def signal_members(c,sig):
        for p in children:
            if p.poll() is None:p.send_signal(sig)
        return {"signal":int(sig),"sent":[p.pid for p in children],"errors":[]}
    monkeypatch.setattr(r,"Controller",Controller)
    monkeypatch.setattr(r.subprocess,"Popen",popen)
    monkeypatch.setattr(r,"signal_members",signal_members)
    monkeypatch.setattr(r,"disk_snapshot",disk)
    monkeypatch.setattr(r,"canonical",canonical)
    if fault=="raw":
        original_record=r.record
        def record(path):
            if Path(path).name=="stdout.bin":raise OSError("authored raw custody")
            return original_record(path)
        monkeypatch.setattr(r,"record",record)
    return marker,children,calls

def command(marker):
    import sys
    return [sys.executable,"-I","-S","-c",
            "from pathlib import Path;import time;Path("+repr(str(marker))+").write_text('started');print('started',flush=True);time.sleep(.10)"]

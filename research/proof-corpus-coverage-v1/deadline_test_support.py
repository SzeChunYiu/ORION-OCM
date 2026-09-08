"""Authored external-clock records; never scientific run identifiers or master draws."""
from pathlib import Path
import time
from resource_contract import canonical,record

def started(root,*,seconds=5,changes=None):
    p=Path(root)/"AUTHORED-STARTED.json"
    start=time.monotonic_ns()-1000000;duration=int(seconds*1000000000)
    value={"schema":"ocm.unary-started.v1","run_id":"authored-deadline-control",
           "boot_id":Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
           "started_monotonic_ns":start,"deadline_monotonic_ns":start+duration,
           "launch_seal_sha256":"a"*64}
    value.update(changes or {})
    p.write_bytes(canonical(value))
    return {"schema":"ocm.unary-external-deadline.v1","record":record(p),
            "run_id":"authored-deadline-control","launch_seal_sha256":"a"*64,"duration_ns":duration}

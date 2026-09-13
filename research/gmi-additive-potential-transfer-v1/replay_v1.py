"""Replay complete static payload; never invokes an ecology or a campaign."""
import json
import subprocess
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from custody_v1 import verify,sha

def replay(root=None,worker=None):
    root=Path(root or Path(__file__).resolve().parent)
    initial,expected=verify(root)
    if worker is None:
        flags=["-I","-B"]+(["-O"] if sys.flags.optimize else [])
        run=subprocess.run([sys.executable,*flags,str(root/"check_additive_transfer_v1.py")],
                           cwd=root,capture_output=True,timeout=60,check=False)
        if run.returncode or run.stderr:
            raise ValueError("static worker failed")
        actual=run.stdout
    else:
        actual=worker(root)
    current,current_expected=verify(root)
    if current!=initial or current_expected!=expected:
        raise ValueError("source authority changed during worker")
    if actual!=expected or json.loads(actual)!=json.loads(expected):
        raise ValueError("complete recorded payload differs")
    return dict(status="FULL_STATIC_PAYLOAD_REPLAY_PASS",
                manifest_sha256=sha(initial),receipt_sha256=sha(expected))

if __name__=="__main__":
    print(json.dumps(replay(),sort_keys=True,indent=2))
